"""Create clean report tables from PICP_Project/results/metrics_summary.csv.
Run from project root: python generate_picp_tables.py
Paper-reported numbers must be entered manually from the paper's Table II.
Robustness requires a separate experiment CSV with Outlier_Percent and metrics.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
SOURCE = RESULTS / "metrics_summary.csv"
OUT = RESULTS / "report_tables"
OUT.mkdir(parents=True, exist_ok=True)


def mean_std(df, prefix):
    mean = df[f"{prefix}_Mean"]
    std_col = f"{prefix}_Std"
    if std_col in df:
        return mean.map(lambda x: f"{x:.3f}") + " ± " + df[std_col].map(lambda x: f"{x:.3f}")
    return mean.map(lambda x: f"{x:.3f}")


def main_table():
    df = pd.read_csv(SOURCE)
    table = pd.DataFrame({
        "Shape": df["Shape"],
        "ICP RMSE (all points)": mean_std(df, "ICP_NN_RMSE_All"),
        "EM-ICP RMSE (all points)": mean_std(df, "Soft_EM_ICP_NN_RMSE_All"),
        "PICP RMSE (all points)": mean_std(df, "PICP_NN_RMSE_All"),
        "ICP RMSE (inliers)": mean_std(df, "ICP_NN_RMSE_Inliers"),
        "EM-ICP RMSE (inliers)": mean_std(df, "Soft_EM_ICP_NN_RMSE_Inliers"),
        "PICP RMSE (inliers)": mean_std(df, "PICP_NN_RMSE_Inliers"),
        "ICP direct inlier RMSE": mean_std(df, "ICP_Direct_RMSE_Inliers"),
        "Soft-EM direct inlier RMSE": mean_std(df, "Soft_EM_ICP_Direct_RMSE_Inliers"),
        "PICP direct inlier RMSE": mean_std(df, "PICP_Direct_RMSE_Inliers"),
        "PICP weighted RMS (paper objective)": mean_std(df, "PICP_Weighted_RMS"),
        "PICP effective sample size": mean_std(df, "PICP_Effective_Sample_Size"),
    })
    table.to_csv(OUT / "main_results_table.csv", index=False)
    (OUT / "main_results_table.md").write_text(
        "## Main registration results\n\n"
        "Values are mean ± standard deviation across trials. Lower RMSE is better. "
        "All-point and inlier-only nearest-neighbour RMSE are reported separately. Direct inlier RMSE uses known synthetic correspondences. PICP weighted RMS is its own objective and must not be compared numerically with unweighted RMSE.\n\n"
        + table.to_markdown(index=False) + "\n", encoding="utf-8")
    return table


def paper_comparison_template():
    # Fill these columns manually from the original paper's Table II.
    rows = [
        {"Shape": s, "Paper ICP": "ENTER FROM PAPER", "Paper EM-ICP": "ENTER FROM PAPER",
         "Paper PICP": "ENTER FROM PAPER", "Our ICP": "see main_results_table.csv",
         "Our EM-ICP": "see main_results_table.csv", "Our PICP": "see main_results_table.csv"}
        for s in ["Apple", "Cup", "Children"]
    ]
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "paper_table_II_comparison_template.csv", index=False)
    (OUT / "paper_table_II_comparison_template.md").write_text(
        "## Paper Table II versus our reproduction\n\n"
        "Replace ENTER FROM PAPER with the exact values and metric definitions from the paper. "
        "Do not compare values until the paper's metric, units, noise settings, and dataset setup match.\n\n"
        + df.to_markdown(index=False) + "\n", encoding="utf-8")
    return df


def robustness_table():
    # Matches the output produced by run_picp_robustness.py.
    source = RESULTS / "robustness" / "robustness_trials.csv"
    if not source.exists():
        print("Robustness results not found; skipping robustness report table.")
        return None

    df = pd.read_csv(source)
    required = {
        "Shape", "OutlierRate", "Trial",
        "ICP_NN_RMSE_All", "EM_ICP_NN_RMSE_All", "PICP_NN_RMSE_All",
        "ICP_NN_RMSE_Inliers", "EM_ICP_NN_RMSE_Inliers", "PICP_NN_RMSE_Inliers",
        "ICP_NN_RMSE_Outliers", "EM_ICP_NN_RMSE_Outliers", "PICP_NN_RMSE_Outliers",
        "ICP_Direct_RMSE_Inliers", "EM_ICP_Direct_RMSE_Inliers", "PICP_Direct_RMSE_Inliers",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{source} is missing required columns: {sorted(missing)}")

    metric_columns = [
        "ICP_NN_RMSE_All", "EM_ICP_NN_RMSE_All", "PICP_NN_RMSE_All",
        "ICP_NN_RMSE_Inliers", "EM_ICP_NN_RMSE_Inliers", "PICP_NN_RMSE_Inliers",
        "ICP_NN_RMSE_Outliers", "EM_ICP_NN_RMSE_Outliers", "PICP_NN_RMSE_Outliers",
        "ICP_Direct_RMSE_Inliers", "EM_ICP_Direct_RMSE_Inliers", "PICP_Direct_RMSE_Inliers",
    ]
    grouped = df.groupby(["OutlierRate", "Shape"], sort=True)
    rows = []
    for (rate, shape), group in grouped:
        row = {
            "Outlier percentage": f"{rate * 100:.0f}%",
            "Shape": shape,
            "Trials": group["Trial"].nunique(),
        }
        for col in metric_columns:
            mean = group[col].mean()
            std = group[col].std(ddof=1)
            row[col.replace("_NN_RMSE_", " ").replace("_", " ")] = (
                f"{mean:.3f} ± {std:.3f}" if pd.notna(std) else f"{mean:.3f} ± NA"
            )
        rows.append(row)

    out = pd.DataFrame(rows)
    out.to_csv(OUT / "robustness_table.csv", index=False)
    (OUT / "robustness_table.md").write_text(
        "## Robustness versus outlier percentage\n\n"
        "Values are mean ± sample standard deviation across trials. "
        "All methods are evaluated using the same all-point nearest-neighbour RMSE; "
        "PICP inlier/outlier RMSE are additional diagnostics. Lower RMSE is better.\n\n"
        + out.to_markdown(index=False) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    main_table()
    paper_comparison_template()
    robustness_table()
    print(f"Tables saved to: {OUT}")
