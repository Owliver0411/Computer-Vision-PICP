"""Reproducible experiments for Probability ICP (PICP).

The PICP update follows the algorithm described in:
Liu et al., "Probability Iterative Closest Point Algorithm for Position
Estimation", IEEE ITSC 2014, pp. 458-463.

The Soft-EM-ICP function below is an explicitly documented, simplified
soft-correspondence baseline. It is not a full reimplementation of the
multi-scale EM-ICP method by Granger and Pennec (2002).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy.spatial import KDTree

from utils import FIGURES_DIR, result_file, data_file

FIGURES_PATH = Path(FIGURES_DIR)


# ---------------------------------------------------------------------------
# Experiment configuration
# ---------------------------------------------------------------------------
RANDOM_SEED = 42
NUM_POINTS = 600
NUM_TRIALS = 5
MAX_ICP_ITERATIONS = 60
MAX_PICP_ITERATIONS = 60
CONVERGENCE_TOLERANCE = 1e-5
ANNEALING_LAMBDA = 1.4  # The paper specifies 1 < lambda <= 2.

TEST_SHAPES = [
    ("Apple", "apple-1.gif"),
    ("Cup", "cup-1.gif"),
    ("Children", "children-1.gif"),
]


# ---------------------------------------------------------------------------
# Data loading and synthetic corruption
# ---------------------------------------------------------------------------
def load_shape_points(gif_name: str, num_points: int = NUM_POINTS) -> np.ndarray:
    """Convert a binary GIF shape into a centred 2D boundary point set.

    The image is thresholded at 128. Boundary pixels are detected by looking
    for horizontal and vertical transitions. Coordinates are returned as
    (x, -y), matching the usual Cartesian orientation.

    When there are more than ``num_points`` boundary pixels, deterministic
    index-based subsampling is applied. The original aspect ratio and pixel
    scale are preserved; the shape is not resized or normalised.
    """
    if num_points < 3:
        raise ValueError("num_points must be at least 3")

    path = Path(data_file(gif_name))
    if not path.is_file():
        raise FileNotFoundError(
            f"Shape file not found: {path}. Put the GIF inside the data/ folder."
        )

    image = Image.open(path).convert("L")
    image_array = np.asarray(image)
    binary = image_array < 128

    edges = np.zeros_like(binary, dtype=bool)
    edges[:-1, :] |= binary[:-1, :] != binary[1:, :]
    edges[:, :-1] |= binary[:, :-1] != binary[:, 1:]

    y_indices, x_indices = np.where(edges)
    points = np.column_stack((x_indices, -y_indices)).astype(np.float64)

    if len(points) < 3:
        raise ValueError(f"Not enough boundary points were detected in {gif_name}")

    # Remove translation caused by the image canvas, but retain scale.
    points -= points.mean(axis=0, keepdims=True)

    if len(points) > num_points:
        indices = np.linspace(0, len(points) - 1, num_points, dtype=int)
        points = points[indices]

    return points


def make_synthetic_case(
    model_points: np.ndarray,
    seed: int,
    gaussian_noise_std: float = 0.4,
    outlier_shift: Tuple[float, float] = (-12.0, -12.0),
    outlier_noise_std: float = 2.0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """Create a known rigid transform plus Gaussian and local structured noise.

    A rectangular region on the left side of the transformed contour is
    designated as the corrupted region. The returned Boolean mask identifies
    these outlier points, allowing inlier and outlier errors to be evaluated
    separately. Different trials use different noise seeds.
    """
    rng = np.random.default_rng(seed)

    angle_degrees = 15.0
    angle = np.deg2rad(angle_degrees)
    rotation = np.array(
        [[np.cos(angle), -np.sin(angle)],
         [np.sin(angle),  np.cos(angle)]],
        dtype=np.float64,
    )
    translation = np.array([12.0, -8.0], dtype=np.float64)

    clean_source = model_points @ rotation.T + translation
    noise = rng.normal(0.0, gaussian_noise_std, size=clean_source.shape)

    x = clean_source[:, 0]
    y = clean_source[:, 1]
    outlier_mask = (
        (x < np.percentile(x, 25))
        & (y > np.percentile(y, 20))
        & (y < np.percentile(y, 80))
    )

    number_of_outliers = int(outlier_mask.sum())
    if number_of_outliers:
        shift = np.asarray(outlier_shift, dtype=np.float64)
        noise[outlier_mask] += rng.normal(
            loc=shift,
            scale=outlier_noise_std,
            size=(number_of_outliers, 2),
        )

    source_points = clean_source + noise
    return source_points, outlier_mask, clean_source, angle_degrees


# ---------------------------------------------------------------------------
# Weighted rigid transform (SVD / Kabsch solution)
# ---------------------------------------------------------------------------
def compute_svd_transformation(
    source: np.ndarray,
    target: np.ndarray,
    weights: np.ndarray | None = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Find R,t minimising sum_i w_i ||R source_i + t - target_i||^2."""
    source = np.asarray(source, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)

    if source.ndim != 2 or target.ndim != 2 or source.shape != target.shape:
        raise ValueError("source and target must have the same (N, D) shape")
    if source.shape[0] < 2:
        raise ValueError("At least two point correspondences are required")

    count, dimension = source.shape
    if weights is None:
        weights = np.ones(count, dtype=np.float64)
    else:
        weights = np.asarray(weights, dtype=np.float64)
        if weights.shape != (count,):
            raise ValueError("weights must contain one value per correspondence")
        if np.any(weights < 0) or not np.all(np.isfinite(weights)):
            raise ValueError("weights must be finite and non-negative")

    weight_sum = float(weights.sum())
    if weight_sum <= np.finfo(np.float64).eps:
        raise ValueError("The sum of correspondence weights must be positive")

    centroid_source = np.sum(source * weights[:, None], axis=0) / weight_sum
    centroid_target = np.sum(target * weights[:, None], axis=0) / weight_sum

    source_centered = source - centroid_source
    target_centered = target - centroid_target
    covariance = source_centered.T @ (target_centered * weights[:, None])

    if not np.all(np.isfinite(covariance)):
        raise FloatingPointError("Non-finite covariance matrix in SVD solver")

    u, _, vt = np.linalg.svd(covariance)
    rotation = vt.T @ u.T

    # Enforce a proper rotation (det(R) = +1), not a reflection.
    if np.linalg.det(rotation) < 0:
        vt[-1, :] *= -1
        rotation = vt.T @ u.T

    translation = centroid_target - rotation @ centroid_source
    return rotation, translation


# ---------------------------------------------------------------------------
# Shared metrics
# ---------------------------------------------------------------------------
def nearest_neighbour_distances(
    points: np.ndarray,
    target: np.ndarray,
    target_tree: KDTree | None = None,
) -> np.ndarray:
    """Return each point's distance to its nearest point in the target set."""
    tree = target_tree if target_tree is not None else KDTree(target)
    distances, _ = tree.query(points, k=1)
    return np.asarray(distances, dtype=np.float64)


def nearest_neighbour_rmse(
    points: np.ndarray,
    target: np.ndarray,
    target_tree: KDTree | None = None,
) -> float:
    """Unweighted nearest-neighbour RMSE, used consistently for all methods."""
    distances = nearest_neighbour_distances(points, target, target_tree)
    return float(np.sqrt(np.mean(distances ** 2)))


def subset_rmse(distances: np.ndarray, mask: np.ndarray) -> float:
    """RMSE for a subset selected by a Boolean mask; NaN for an empty subset."""
    if not np.any(mask):
        return float("nan")
    return float(np.sqrt(np.mean(distances[mask] ** 2)))


# ---------------------------------------------------------------------------
# (A) Standard point-to-point ICP
# ---------------------------------------------------------------------------
def run_icp(
    source: np.ndarray,
    target: np.ndarray,
    max_iterations: int = MAX_ICP_ITERATIONS,
    tolerance: float = CONVERGENCE_TOLERANCE,
) -> Tuple[np.ndarray, List[float]]:
    """Standard ICP with nearest-neighbour matching and unweighted SVD."""
    if max_iterations < 1:
        raise ValueError("max_iterations must be positive")

    aligned = source.copy()
    target_tree = KDTree(target)
    rmse_history: List[float] = []

    for _ in range(max_iterations):
        _, indices = target_tree.query(aligned, k=1)
        matched_target = target[indices]

        rotation, translation = compute_svd_transformation(aligned, matched_target)
        aligned = aligned @ rotation.T + translation

        rmse = nearest_neighbour_rmse(aligned, target, target_tree)
        rmse_history.append(rmse)

        if len(rmse_history) > 1 and abs(rmse_history[-2] - rmse) < tolerance:
            break

    return aligned, rmse_history


# ---------------------------------------------------------------------------
# (B) Simplified soft-correspondence EM-ICP baseline
# ---------------------------------------------------------------------------
def run_soft_em_icp(
    source: np.ndarray,
    target: np.ndarray,
    max_iterations: int = MAX_ICP_ITERATIONS,
    tolerance: float = CONVERGENCE_TOLERANCE,
    initial_variance_scale: float = 0.12,
    cooling_rate: float = 0.90,
    minimum_variance: float = 0.5,
) -> Tuple[np.ndarray, List[float]]:
    """A simple soft-assignment EM-ICP-inspired comparison baseline.

    Each source point distributes its responsibility over all target points
    using a Gaussian kernel. The expected target point is then used in an
    unweighted SVD update. The variance follows a fixed cooling schedule.

    Important: this is a simplified baseline, not a full implementation of
    the multi-scale EM-ICP algorithm cited by Liu et al. (Granger & Pennec,
    ECCV 2002). The report and README must identify it as such.
    """
    if max_iterations < 1:
        raise ValueError("max_iterations must be positive")
    if not (0.0 < cooling_rate < 1.0):
        raise ValueError("cooling_rate must be between 0 and 1")

    aligned = source.copy()
    bbox_diagonal_squared = float(np.sum(np.ptp(target, axis=0) ** 2))
    variance = max(bbox_diagonal_squared * initial_variance_scale, minimum_variance)
    target_tree = KDTree(target)
    rmse_history: List[float] = []

    for _ in range(max_iterations):
        # Pairwise squared distances between the current source and target.
        pairwise_squared_distances = np.sum(
            (aligned[:, None, :] - target[None, :, :]) ** 2,
            axis=2,
        )

        log_responsibilities = -pairwise_squared_distances / (2.0 * variance)
        log_responsibilities -= np.max(
            log_responsibilities, axis=1, keepdims=True
        )
        responsibilities = np.exp(log_responsibilities)
        row_sums = responsibilities.sum(axis=1, keepdims=True)
        responsibilities /= np.maximum(row_sums, np.finfo(np.float64).tiny)

        expected_target = responsibilities @ target
        rotation, translation = compute_svd_transformation(aligned, expected_target)
        aligned = aligned @ rotation.T + translation

        rmse = nearest_neighbour_rmse(aligned, target, target_tree)
        rmse_history.append(rmse)

        variance = max(variance * cooling_rate, minimum_variance)
        if len(rmse_history) > 1 and abs(rmse_history[-2] - rmse) < tolerance:
            break

    return aligned, rmse_history


# ---------------------------------------------------------------------------
# (C) Probability ICP (proposed method)
# ---------------------------------------------------------------------------
def run_picp(
    source: np.ndarray,
    target: np.ndarray,
    max_iterations: int = MAX_PICP_ITERATIONS,
    tolerance: float = CONVERGENCE_TOLERANCE,
    lambda_anneal: float = ANNEALING_LAMBDA,
    initial_variance_scale: float = 0.20,
) -> Tuple[np.ndarray, List[float], List[float], np.ndarray]:
    """PICP implementation following the paper's E/M, variance and probability steps.

    Each source point is assigned its nearest model point, as in Equation (8).

    Returns:
        aligned: final transformed source points
        common_rmse_history: unweighted NN-RMSE at each iteration
        weighted_rms_history: paper-defined probability-weighted RMS
        probabilities: final normalised point probabilities
    """
    if max_iterations < 1:
        raise ValueError("max_iterations must be positive")
    if not (1.0 < lambda_anneal <= 2.0):
        raise ValueError("The paper specifies 1 < lambda_anneal <= 2")
    if source.ndim != 2 or target.ndim != 2 or source.shape[1] != target.shape[1]:
        raise ValueError("source and target must be 2D arrays with matching dimensions")

    number_source_points, dimension = source.shape
    if number_source_points < 2 or len(target) < 2:
        raise ValueError("Both point sets must contain at least two points")

    aligned = source.copy()
    target_tree = KDTree(target)

    bbox_diagonal_squared = float(np.sum(np.ptp(target, axis=0) ** 2))
    variance = max(
        bbox_diagonal_squared * initial_variance_scale,
        np.finfo(np.float64).eps,
    )

    # Correct initialisation from Algorithm 1: p_i^0 = 1 / N_x.
    # Do not divide by N_y: source and target sets need not have equal sizes.
    probabilities = np.full(
        number_source_points,
        1.0 / number_source_points,
        dtype=np.float64,
    )

    common_rmse_history: List[float] = []
    weighted_rms_history: List[float] = []

    for _ in range(max_iterations):
        # E-step: for each source point, select its nearest model point.
        # This is the correspondence c_k(i) in Equation (8). Each source
        # point has one correspondence; different source points may select
        # the same model point, as in the nearest-neighbour search described
        # by the paper. The KD-tree avoids a dense all-pairs assignment.
        _, indices = target_tree.query(aligned, k=1)
        matched_target = target[indices]

        # M-step: weighted rigid transform estimated from the original source.
        rotation, translation = compute_svd_transformation(
            source,
            matched_target,
            weights=probabilities,
        )
        aligned = source @ rotation.T + translation

        squared_residuals = np.sum((aligned - matched_target) ** 2, axis=1)

        # Equation (13): EM variance; n is the coordinate dimension (2 here).
        sigma_em_squared = float(
            np.sum(probabilities * squared_residuals) / dimension
        )

        # Equation (14): anneal from global to local, then use EM variance.
        annealed_variance = variance / lambda_anneal
        if annealed_variance > sigma_em_squared:
            variance = annealed_variance
        else:
            variance = max(sigma_em_squared, 1e-4)

        # Equation (15): Gaussian posterior. The common Gaussian constant
        # cancels during normalisation, so the stable softmax form is equivalent.
        log_weights = -squared_residuals / (2.0 * variance)
        log_weights -= np.max(log_weights)
        probabilities = np.exp(log_weights)
        probability_sum = float(probabilities.sum())
        probabilities /= max(probability_sum, np.finfo(np.float64).tiny)

        # Paper-defined weighted RMS and a separate common evaluation metric.
        weighted_rms = float(np.sqrt(np.sum(probabilities * squared_residuals)))
        common_rmse = nearest_neighbour_rmse(aligned, target, target_tree)
        weighted_rms_history.append(weighted_rms)
        common_rmse_history.append(common_rmse)

        # The paper's stopping condition uses its probability-weighted RMS.
        if (
            len(weighted_rms_history) > 1
            and abs(weighted_rms_history[-2] - weighted_rms) < tolerance
        ):
            break

    return aligned, common_rmse_history, weighted_rms_history, probabilities


# ---------------------------------------------------------------------------
# Evaluation and figure generation
# ---------------------------------------------------------------------------
def evaluate_result(
    aligned: np.ndarray,
    target: np.ndarray,
    outlier_mask: np.ndarray,
) -> Dict[str, float]:
    """Evaluate all algorithms with the same NN metric and split by noise type."""
    distances = nearest_neighbour_distances(aligned, target, KDTree(target))
    inlier_mask = ~outlier_mask

    direct_inlier_rmse = float(
        np.sqrt(np.mean(np.sum((aligned[inlier_mask] - target[inlier_mask]) ** 2, axis=1)))
    ) if np.any(inlier_mask) else float("nan")

    return {
        "NN_RMSE_All": float(np.sqrt(np.mean(distances ** 2))),
        "NN_RMSE_Inliers": subset_rmse(distances, inlier_mask),
        "NN_RMSE_Outliers": subset_rmse(distances, outlier_mask),
        # Because the synthetic source is generated from target point i,
        # this index-wise metric is also available for the known inlier subset.
        "Direct_RMSE_Inliers": direct_inlier_rmse,
    }


def save_registration_figure(
    target: np.ndarray,
    results: Dict[str, np.ndarray],
    output_path: Path,
) -> None:
    """Save side-by-side registration results for the Apple example."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for axis, (method, aligned) in zip(axes, results.items()):
        axis.scatter(target[:, 0], target[:, 1], s=5, c="red", label="Model")
        axis.scatter(aligned[:, 0], aligned[:, 1], s=5, c="blue", label="Registered source")
        axis.set_title(method)
        axis.set_aspect("equal", adjustable="datalim")
        axis.axis("off")
    axes[0].legend(loc="lower left", fontsize=8)
    fig.suptitle("Registration comparison on the Apple shape")
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def save_input_figure(
    target: np.ndarray,
    source: np.ndarray,
    outlier_mask: np.ndarray,
    output_path: Path,
) -> None:
    """Visualise the clean model, noisy source and deliberately corrupted patch."""
    fig, axis = plt.subplots(figsize=(7, 6))
    axis.scatter(target[:, 0], target[:, 1], s=5, c="black", label="Clean model")
    axis.scatter(source[~outlier_mask, 0], source[~outlier_mask, 1],
                 s=5, c="royalblue", label="Noisy inliers")
    axis.scatter(source[outlier_mask, 0], source[outlier_mask, 1],
                 s=8, c="darkorange", label="Structured outliers")
    axis.set_aspect("equal", adjustable="datalim")
    axis.set_title("Synthetic input point sets")
    axis.legend()
    axis.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def save_convergence_figure(
    histories: Dict[str, List[float]],
    output_path: Path,
) -> None:
    """Plot the same unweighted NN-RMSE metric for all three algorithms."""
    fig, axis = plt.subplots(figsize=(8, 5))
    for method, history in histories.items():
        axis.plot(history, label=method, linewidth=2)
    axis.set_xlabel("Iteration")
    axis.set_ylabel("Unweighted nearest-neighbour RMSE (pixels)")
    axis.set_title("Convergence using a common evaluation metric")
    axis.grid(True, linestyle=":", alpha=0.6)
    axis.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def save_picp_objective_figure(history: List[float], output_path: Path) -> None:
    """Plot PICP's paper-defined weighted RMS separately from common RMSE."""
    fig, axis = plt.subplots(figsize=(7, 5))
    axis.plot(history, color="green", linewidth=2)
    axis.set_xlabel("Iteration")
    axis.set_ylabel("PICP probability-weighted RMS")
    axis.set_title("PICP objective during optimisation")
    axis.grid(True, linestyle=":", alpha=0.6)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def write_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write to {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def make_summary(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    """Group trial measurements by shape and calculate mean and standard deviation."""
    metric_names = [
        "ICP_NN_RMSE_All", "ICP_NN_RMSE_Inliers", "ICP_NN_RMSE_Outliers",
        "ICP_Direct_RMSE_Inliers", "Soft_EM_ICP_NN_RMSE_All",
        "Soft_EM_ICP_NN_RMSE_Inliers", "Soft_EM_ICP_NN_RMSE_Outliers",
        "Soft_EM_ICP_Direct_RMSE_Inliers", "PICP_NN_RMSE_All",
        "PICP_NN_RMSE_Inliers", "PICP_NN_RMSE_Outliers", "PICP_Direct_RMSE_Inliers",
        "PICP_Weighted_RMS", "PICP_Effective_Sample_Size", "PICP_Max_Probability",
    ]
    summary_rows: List[Dict[str, object]] = []

    for shape_name, _ in TEST_SHAPES:
        shape_rows = [row for row in rows if row["Shape"] == shape_name]
        summary: Dict[str, object] = {
            "Shape": shape_name,
            "Trials": len(shape_rows),
        }
        for metric in metric_names:
            values = np.asarray([float(row[metric]) for row in shape_rows])
            summary[f"{metric}_Mean"] = float(np.mean(values))
            summary[f"{metric}_Std"] = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
        summary_rows.append(summary)

    return summary_rows


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------
def main() -> None:
    print("PICP reproduction experiment")
    print(f"Trials per shape: {NUM_TRIALS}; random seed base: {RANDOM_SEED}")
    print("Methods: ICP, simplified Soft-EM-ICP, PICP")

    all_rows: List[Dict[str, object]] = []
    apple_figure_written = False

    for shape_index, (shape_name, filename) in enumerate(TEST_SHAPES):
        print(f"\nProcessing {shape_name} ({filename})")
        model_points = load_shape_points(filename, num_points=NUM_POINTS)
        print(f"  Number of model points: {len(model_points)}")

        for trial in range(NUM_TRIALS):
            seed = RANDOM_SEED + shape_index * 1000 + trial
            source_points, outlier_mask, _, _ = make_synthetic_case(
                model_points,
                seed=seed,
            )

            icp_aligned, icp_history = run_icp(source_points, model_points)
            em_aligned, em_history = run_soft_em_icp(source_points, model_points)
            picp_aligned, picp_nn_history, picp_weighted_history, picp_probabilities = run_picp(
                source_points,
                model_points,
            )

            icp_metrics = evaluate_result(icp_aligned, model_points, outlier_mask)
            em_metrics = evaluate_result(em_aligned, model_points, outlier_mask)
            picp_metrics = evaluate_result(picp_aligned, model_points, outlier_mask)

            row: Dict[str, object] = {
                "Shape": shape_name,
                "Trial": trial + 1,
                "Seed": seed,
                "NumPoints": len(model_points),
                "NumOutliers": int(outlier_mask.sum()),
                "ICP_NN_RMSE_All": icp_metrics["NN_RMSE_All"],
                "ICP_NN_RMSE_Inliers": icp_metrics["NN_RMSE_Inliers"],
                "ICP_NN_RMSE_Outliers": icp_metrics["NN_RMSE_Outliers"],
                "ICP_Direct_RMSE_Inliers": icp_metrics["Direct_RMSE_Inliers"],
                "Soft_EM_ICP_NN_RMSE_All": em_metrics["NN_RMSE_All"],
                "Soft_EM_ICP_NN_RMSE_Inliers": em_metrics["NN_RMSE_Inliers"],
                "Soft_EM_ICP_NN_RMSE_Outliers": em_metrics["NN_RMSE_Outliers"],
                "Soft_EM_ICP_Direct_RMSE_Inliers": em_metrics["Direct_RMSE_Inliers"],
                "PICP_NN_RMSE_All": picp_metrics["NN_RMSE_All"],
                "PICP_NN_RMSE_Inliers": picp_metrics["NN_RMSE_Inliers"],
                "PICP_NN_RMSE_Outliers": picp_metrics["NN_RMSE_Outliers"],
                "PICP_Direct_RMSE_Inliers": picp_metrics["Direct_RMSE_Inliers"],
                "PICP_Weighted_RMS": picp_weighted_history[-1],
                "PICP_Effective_Sample_Size": float(1.0 / np.sum(picp_probabilities ** 2)),
                "PICP_Max_Probability": float(np.max(picp_probabilities)),
                "ICP_Iterations": len(icp_history),
                "Soft_EM_ICP_Iterations": len(em_history),
                "PICP_Iterations": len(picp_weighted_history),
            }
            all_rows.append(row)

            print(
                f"  Trial {trial + 1}/{NUM_TRIALS}: "
                f"NN-RMSE all (ICP/Soft-EM/PICP) = "
                f"{icp_metrics['NN_RMSE_All']:.3f} / "
                f"{em_metrics['NN_RMSE_All']:.3f} / "
                f"{picp_metrics['NN_RMSE_All']:.3f}; "
                f"PICP inlier NN-RMSE = {picp_metrics['NN_RMSE_Inliers']:.3f}; "
                f"PICP direct inlier RMSE = {picp_metrics['Direct_RMSE_Inliers']:.3f}; "
                f"PICP weighted RMS = {picp_weighted_history[-1]:.4f}; "
                f"PICP effective samples = {1.0 / np.sum(picp_probabilities ** 2):.1f}"
            )

            # Figures and probability diagnostics are saved for the first
            # Apple trial so that the output remains deterministic and compact.
            if shape_name == "Apple" and trial == 0:
                save_input_figure(
                    model_points,
                    source_points,
                    outlier_mask,
                    FIGURES_PATH / "figure1_synthetic_input.png",
                )
                save_registration_figure(
                    model_points,
                    {
                        "(a) ICP": icp_aligned,
                        "(b) Soft-EM-ICP": em_aligned,
                        "(c) PICP": picp_aligned,
                    },
                    FIGURES_PATH / "figure2_apple_registration.png",
                )
                save_convergence_figure(
                    {
                        "ICP": icp_history,
                        "Soft-EM-ICP (simplified)": em_history,
                        "PICP (common NN-RMSE)": picp_nn_history,
                    },
                    FIGURES_PATH / "figure3_common_metric_convergence.png",
                )
                save_picp_objective_figure(
                    picp_weighted_history,
                    FIGURES_PATH / "figure4_picp_weighted_rms.png",
                )

                probability_path = Path(result_file("apple_trial1_picp_probabilities.csv"))
                probability_rows = [
                    {
                        "PointIndex": index,
                        "X": float(source_points[index, 0]),
                        "Y": float(source_points[index, 1]),
                        "IsSyntheticOutlier": int(outlier_mask[index]),
                        "PICP_Probability": float(picp_probabilities[index]),
                    }
                    for index in range(len(source_points))
                ]
                write_csv(probability_path, probability_rows)
                apple_figure_written = True

    metrics_path = Path(result_file("metrics.csv"))
    summary_path = Path(result_file("metrics_summary.csv"))
    write_csv(metrics_path, all_rows)
    write_csv(summary_path, make_summary(all_rows))

    print("\nSaved results:")
    print(f"  Trial-level metrics: {metrics_path}")
    print(f"  Mean/std summary:    {summary_path}")
    if apple_figure_written:
        print(f"  Figures:             {FIGURES_PATH}")
    print("\nImportant: compare algorithms using the common NN-RMSE columns.")
    print("PICP_Weighted_RMS is the paper-defined weighted objective and must be")
    print("reported separately, not directly compared with unweighted RMSE.")


if __name__ == "__main__":
    main()
