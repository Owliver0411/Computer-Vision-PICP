"""Run PICP robustness experiments at 10/20/30/40% outliers.

Place this file in PICP_Project/ next to run.sh. Run:
    python run_picp_robustness.py

Uses the project's code/main.py implementations. Writes trial-level and compact
report tables under results/robustness/.
"""
from pathlib import Path
import sys
import csv
import numpy as np

ROOT = Path(__file__).resolve().parent
CODE = ROOT / "code"
sys.path.insert(0, str(CODE))

import main as picp  # noqa: E402

OUT_DIR = ROOT / "results" / "robustness"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUTLIER_RATES = (0.10, 0.20, 0.30, 0.40)
TRIALS = 5
ROBUSTNESS_NUM_POINTS = 300
ROBUSTNESS_MAX_ITERATIONS = 30
SEED_BASE = 20261104


def make_case(model_points, rate, seed, gaussian_noise_std=0.4,
             outlier_shift=(-12.0, -12.0), outlier_noise_std=2.0):
    """Generate known rigid transform, Gaussian noise, and exact-rate outliers."""
    rng = np.random.default_rng(seed)
    angle = np.deg2rad(15.0)
    rotation = np.array([[np.cos(angle), -np.sin(angle)],
                        [np.sin(angle),  np.cos(angle)]])
    translation = np.array([12.0, -8.0])
    clean_source = model_points @ rotation.T + translation
    source = clean_source + rng.normal(0, gaussian_noise_std, clean_source.shape)

    n = len(source)
    n_out = int(round(n * rate))
    outlier_mask = np.zeros(n, dtype=bool)
    if n_out:
        chosen = rng.choice(n, size=n_out, replace=False)
        outlier_mask[chosen] = True
        source[chosen] += rng.normal(
            loc=np.asarray(outlier_shift, dtype=float),
            scale=outlier_noise_std,
            size=(n_out, 2),
        )
    return source, outlier_mask


def write_csv(path, rows):
    if not rows:
        raise RuntimeError(f"No rows to write: {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def mean_sd(values):
    values = np.asarray(values, dtype=float)
    mean = float(np.mean(values))
    sd = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
    return mean, sd


def main():
    trial_rows = []
    for shape_idx, (shape_name, filename) in enumerate(picp.TEST_SHAPES):
        model = picp.load_shape_points(filename, num_points=ROBUSTNESS_NUM_POINTS)
        print(f"\nShape: {shape_name} ({len(model)} points)")
        for rate_idx, rate in enumerate(OUTLIER_RATES):
            for trial in range(TRIALS):
                seed = SEED_BASE + shape_idx * 100000 + rate_idx * 1000 + trial
                source, outlier_mask = make_case(model, rate, seed)

                # Run the exact algorithm functions from this project.
                icp_aligned, _ = picp.run_icp(source, model, max_iterations=ROBUSTNESS_MAX_ITERATIONS)
                em_aligned, _ = picp.run_soft_em_icp(source, model, max_iterations=ROBUSTNESS_MAX_ITERATIONS)
                p_aligned, _, weighted_history, probabilities = picp.run_picp(
                    source, model, max_iterations=ROBUSTNESS_MAX_ITERATIONS
                )

                im = picp.evaluate_result(icp_aligned, model, outlier_mask)
                em = picp.evaluate_result(em_aligned, model, outlier_mask)
                pm = picp.evaluate_result(p_aligned, model, outlier_mask)
                trial_rows.append({
                    "Shape": shape_name, "OutlierRate": rate,
                    "Trial": trial + 1, "Seed": seed,
                    "ActualOutlierCount": int(outlier_mask.sum()),
                    "ICP_NN_RMSE_All": im["NN_RMSE_All"],
                    "EM_ICP_NN_RMSE_All": em["NN_RMSE_All"],
                    "PICP_NN_RMSE_All": pm["NN_RMSE_All"],
                    "ICP_NN_RMSE_Inliers": im["NN_RMSE_Inliers"],
                    "EM_ICP_NN_RMSE_Inliers": em["NN_RMSE_Inliers"],
                    "PICP_NN_RMSE_Inliers": pm["NN_RMSE_Inliers"],
                    "ICP_NN_RMSE_Outliers": im["NN_RMSE_Outliers"],
                    "EM_ICP_NN_RMSE_Outliers": em["NN_RMSE_Outliers"],
                    "PICP_NN_RMSE_Outliers": pm["NN_RMSE_Outliers"],
                    "ICP_Direct_RMSE_Inliers": im["Direct_RMSE_Inliers"],
                    "EM_ICP_Direct_RMSE_Inliers": em["Direct_RMSE_Inliers"],
                    "PICP_Direct_RMSE_Inliers": pm["Direct_RMSE_Inliers"],
                    "PICP_Weighted_RMS": float(weighted_history[-1]),
                    "PICP_EffectiveSampleSize": float(1 / np.sum(probabilities ** 2)),
                })
            print(f"  {int(rate*100)}% outliers: completed {TRIALS} trials")

    write_csv(OUT_DIR / "robustness_trials.csv", trial_rows)

    # Compact report table: mean ± sample SD, by shape and outlier rate.
    metrics = ["ICP_NN_RMSE_All", "EM_ICP_NN_RMSE_All", "PICP_NN_RMSE_All",
               "ICP_NN_RMSE_Inliers", "EM_ICP_NN_RMSE_Inliers", "PICP_NN_RMSE_Inliers",
               "ICP_NN_RMSE_Outliers", "EM_ICP_NN_RMSE_Outliers", "PICP_NN_RMSE_Outliers",
               "ICP_Direct_RMSE_Inliers", "EM_ICP_Direct_RMSE_Inliers", "PICP_Direct_RMSE_Inliers",
               "PICP_Weighted_RMS", "PICP_EffectiveSampleSize"]
    summary = []
    for shape, _ in picp.TEST_SHAPES:
        for rate in OUTLIER_RATES:
            subset = [r for r in trial_rows if r["Shape"] == shape and r["OutlierRate"] == rate]
            row = {"Shape": shape, "OutlierPercent": int(rate * 100), "Trials": len(subset)}
            for metric in metrics:
                m, sd = mean_sd([r[metric] for r in subset])
                row[metric + "_Mean"] = m
                row[metric + "_SD"] = sd
            summary.append(row)
    write_csv(OUT_DIR / "robustness_summary.csv", summary)

    # Human-readable method-comparison table. The common all-point NN-RMSE
    # is the primary cross-method comparison; subset and direct errors are
    # additional diagnostics and must not be conflated.
    md = ["# PICP robustness results", "",
          "Mean ± sample SD across trials (5 trials; 300 sampled contour points; maximum 30 iterations). Lower RMSE is better. All-point NN-RMSE is the common primary metric. ",
          "Direct inlier RMSE uses known synthetic point correspondences; PICP weighted RMS is its own objective.", "",
          "| Shape | Outliers | ICP all NN | Soft-EM all NN | PICP all NN | ICP direct inlier | Soft-EM direct inlier | PICP direct inlier | PICP ESS |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in summary:
        def fmt(key):
            return f"{r[key+'_Mean']:.3f} ± {r[key+'_SD']:.3f}"
        md.append(f"| {r['Shape']} | {r['OutlierPercent']}% | {fmt('ICP_NN_RMSE_All')} | "
                  f"{fmt('EM_ICP_NN_RMSE_All')} | {fmt('PICP_NN_RMSE_All')} | "
                  f"{fmt('ICP_Direct_RMSE_Inliers')} | {fmt('EM_ICP_Direct_RMSE_Inliers')} | "
                  f"{fmt('PICP_Direct_RMSE_Inliers')} | {fmt('PICP_EffectiveSampleSize')} |")
    (OUT_DIR / "robustness_table.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print("\nFinished. Files created:")
    print(OUT_DIR / "robustness_trials.csv")
    print(OUT_DIR / "robustness_summary.csv")
    print(OUT_DIR / "robustness_table.md")

if __name__ == "__main__":
    main()
