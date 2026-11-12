# Probability Iterative Closest Point (PICP) for Position Estimation

This project implements and evaluates Probability Iterative Closest Point (PICP), based on:

Liu, J., Du, S., Zhang, C., Zhu, J., Li, K. and Xue, J. (2014). “Probability Iterative Closest Point Algorithm for Position Estimation.” *2014 IEEE 17th International Conference on Intelligent Transportation Systems (ITSC)*, pp. 458–463. DOI: 10.1109/ITSC.2014.6957732.

## Project purpose

The project compares point-set registration methods on 2D shapes:

1. **ICP** – nearest-neighbour correspondences and an unweighted SVD rigid-transformation update.
2. **Soft-EM-ICP (simplified)** – a soft-correspondence Gaussian baseline. This is an EM-ICP-inspired baseline, not a verified full reproduction of the multi-scale Granger–Pennec EM-ICP method cited by the PICP paper.
3. **PICP** – probability-weighted rigid registration with EM variance estimation and global-to-local variance annealing.

The experiments use selected Apple, Cup and Children contours from the MPEG-7 CE-Shape-1 Part B dataset included in this repository.

## Repository layout

```text
PICP_Project/
├── code/
│   ├── main.py                     # Main ICP / Soft-EM-ICP / PICP implementations and experiment
│   └── utils.py                    # Path and utility functions
├── data/                           # Selected MPEG-7 shape GIFs
├── MPEG7_CE-Shape-1_Part_B/         # Dataset archive / additional shape examples
├── tests/
│   └── test_algorithms.py
├── results/
│   ├── figures/                    # Main experiment figures
│   ├── metrics.csv                 # Main per-trial metrics
│   ├── metrics_summary.csv         # Main experiment summary
│   └── robustness/                 # Created by the robustness runner
├── run.sh                          # Main experiment launcher
├── run_picp_robustness.py          # Separate outlier-rate experiment runner
├── generate_picp_tables.py         # Generates report-ready tables
├── requirements.txt
├── algorithm.txt                   # Pseudocode submitted separately
├── PICP.pdf                        # Original research paper
└── README.md
```

## Requirements and setup

- Python 3.10 or newer is recommended.
- A standard CPU is sufficient; no GPU is required.

Create and activate a virtual environment (recommended):

**Windows PowerShell**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Running the experiments

Run these commands from the project root directory.

### 1. Main registration experiment

```bash
bash run.sh
```

On Windows, because `run.sh` is a Bash script, use Git Bash or WSL. Alternatively, run the Python entry point directly:

```powershell
python code/main.py
```

This creates or updates the main experiment outputs in `results/`, including `metrics.csv`, `metrics_summary.csv`, and figures.

### 2. Robustness experiment (separate)

```bash
python run_picp_robustness.py
```

This runner tests 10%, 20%, 30% and 40% randomly selected outliers, with 10 deterministic trials for each shape and outlier rate. It runs ICP, simplified Soft-EM-ICP and PICP on the same generated trial data.

Outputs:

```text
results/robustness/
├── robustness_trials.csv     # Every individual trial
├── robustness_summary.csv    # Mean and sample standard deviation
└── robustness_table.md       # Readable PICP robustness table
```

The robustness noise model is a controlled synthetic experiment. Outliers are selected randomly to reach the requested percentage; this should not be described as the exact noise-generation procedure from the original paper.

### 3. Generate report tables

```bash
python generate_picp_tables.py
```

The table generator reads the main experiment summary and, when available, the robustness experiment output. It creates:

```text
results/report_tables/
├── main_results_table.csv
├── main_results_table.md
├── paper_table_II_comparison_template.csv
├── paper_table_II_comparison_template.md
├── robustness_table.csv       # Created only when robustness results are available
└── robustness_table.md        # Created only when robustness results are available
```

The Paper Table II comparison files are templates: manually enter the values reported in the original paper after checking the exact metric and experimental conditions. The generator must not invent or infer the paper's reported values.

## Recommended complete run order

```bash
# 1. Install dependencies (once)
python -m pip install -r requirements.txt

# 2. Main experiment
python code/main.py

# 3. Robustness experiment
python run_picp_robustness.py

# 4. Generate all report tables
python generate_picp_tables.py

# 5. Run unit tests
python -m unittest discover -s tests -v
```

On Windows PowerShell, use `python` or `py` consistently with the Python environment where dependencies were installed.

## Understanding the evaluation metrics

For a fair comparison, the main table reports the same unweighted nearest-neighbour RMSE for all methods. It also reports inlier-only RMSE, using the known synthetic corruption mask.

PICP additionally reports its probability-weighted RMS. This is PICP's own weighted objective and must be shown separately from the common unweighted RMSE; the two values are not directly comparable. Effective sample size is a diagnostic of how concentrated the PICP probability weights are.

- **All-point NN RMSE:** nearest-neighbour registration error over all source points.
- **Inlier NN RMSE:** the same metric restricted to synthetic inliers.
- **Outlier NN RMSE:** the same metric restricted to deliberately corrupted points.
- **PICP weighted RMS:** probability-weighted residual used by PICP.
- **Effective sample size:** inverse sum of squared normalized probabilities; a very small value indicates that only a few points carry most of the probability mass.

Lower RMSE is generally better. Interpret the inlier and all-point results together: a robust method may down-weight outliers rather than force every corrupted point to align.

## Reproduction scope and limitations

This is an implementation and experimental reproduction, not a claim of exact numerical replication of every result in the paper.

- The paper does not fully specify all synthetic perturbation-generation settings used in this project. The noise and outlier settings are therefore documented as this project's controlled experimental protocol.
- The project uses a KD-tree for nearest-neighbour lookup rather than the Delaunay triangulation described in the paper.
- The Soft-EM-ICP implementation is a simplified soft-correspondence baseline, not the full multi-scale Granger–Pennec algorithm.
- The robustness experiment uses randomly selected outliers at controlled percentages and is an additional experiment, not a direct reproduction of the paper's Table II.
- Only claim exact Table II reproduction if the dataset, noise model, parameters, metric definition and evaluation protocol have been verified to match the paper.

## Team members

Replace these placeholders before submission:

- Member 1: [Full name] – [University email]
- Member 2: [Full name] – [University email]
- Member 3: [Full name] – [University email]

## Course deliverables

The source code, pseudocode (`algorithm.txt`), generated quantitative/qualitative results and this README support the project submission. The written report is a separate deliverable and should describe data acquisition, preprocessing, algorithm implementation, experimental settings, quantitative and qualitative results, discussion, and limitations.

## Updated evaluation protocol

The main experiment uses 5 independent random trials per shape. The robustness
experiment uses 5 trials at each of 10%, 20%, 30%, and 40% synthetic outlier
rates. To keep the robustness sweep computationally manageable, it uses 300
sampled contour points and a maximum of 30 iterations per method; the main
experiment uses 600 points and the standard method-specific iteration limits.

All methods are evaluated with the same all-point nearest-neighbour RMSE.
Inlier-only and outlier-only nearest-neighbour RMSE are diagnostic subsets.
Because the synthetic generator preserves the original point ordering, the
project also reports direct inlier RMSE against the original corresponding
model points. This direct metric is useful for diagnosing correspondence
errors, but it is not generally available for real unordered point clouds.

PICP's probability-weighted RMS is its own optimisation objective. It must
not be compared numerically with the unweighted RMSE values of ICP or the
soft-EM baseline. The effective sample size (ESS = 1 / sum(p_i^2)) indicates
how many points effectively contribute to PICP's probability weighting; a
very small ESS signals highly concentrated weights and should be discussed.

## Reproduction scope and limitations

This project is an educational/experimental implementation based on the PICP
paper's algorithmic description. The PICP E-step uses one nearest model point
for each source point (Equation 8), and the M-step uses probability-weighted
SVD, variance annealing, and Gaussian probability updates. The Soft-EM-ICP
baseline is deliberately labelled simplified and is not the full multi-scale
EM-ICP implementation. The synthetic corruption model is a controlled test
scenario, not a claim to recreate the paper's exact noise-generation process
or every experimental setting. Any comparison with the paper's published
Table II must first match the dataset, point extraction, noise, units,
initialisation, and RMS definition.

## Recommended execution order

From the project root:

```bash
python code/main.py
python run_picp_robustness.py
python generate_picp_tables.py
python -m pytest -q
```

The scripts overwrite the corresponding CSVs, figures, and report tables in
`results/`. Keep the random seeds in the scripts fixed when producing the
final report so that the results are reproducible.


## Current experimental finding

The current generated results do not show PICP winning on the common all-point
nearest-neighbour RMSE for all three shapes. PICP does show lower inlier-only
nearest-neighbour errors, but direct inlier correspondence errors and effective
sample size reveal shape-dependent behaviour. Do not claim universal superiority
from this dataset. See `results/report_tables/experimental_interpretation.md`
for report-ready interpretation and limitations. The purpose is to test the
paper's proposed improvement, not to force the experiment to confirm it.

## Additional Apple diagnosis and parameter-sensitivity experiments (November 2026)

**New analyses included in this project** are separate from the original main
experiment so that its baseline is preserved. Run from the `PICP_Project` root:

```bash
python run_picp_apple_diagnostic.py
python run_picp_validation.py
python run_picp_pose_diagnostic.py
python -m pytest -q
```

The new scripts generate CSVs, a parameter-sensitivity figure, and Markdown
results under `results/diagnostics/`. These files are already included in the
provided archive. See especially:

- `results/diagnostics/apple_diagnostic_report.md` (12-configuration Apple grid,
  10 paired seeds; 300 points)
- `results/diagnostics/independent_seed_validation_report.md` (three shapes,
  10 new seeds each; 300 points)
- `results/diagnostics/full_resolution_validation_report.md` (three shapes,
  5 new seeds each; 600 points)
- `results/diagnostics/apple_pose_report.md` (Apple synthetic pose angles
  5°, 15°, 30°; 300 points)
- `results/diagnostics/apple_parameter_sensitivity.png` (sweep visualization)

The baseline remains `lambda_anneal=1.4` and
`initial_variance_scale=0.20`, with identity/zero initial pose and uniform
point probabilities. The Apple sweep *suggested* a slower-annealing candidate,
`lambda_anneal=1.1` and `initial_variance_scale=0.05`. These are NOT stated
paper-prescribed settings, and were examined after inspecting Apple results.
The scripts run the candidate using the existing `run_picp()` parameters; they
do not replace the baseline or automatically select parameters.

**Main findings.** PICP performs much better for Apple under slower annealing
on the *known synthetic direct inlier correspondence* metric, and ESS is much
larger, indicating less weight collapse. However, performance is shape- and
initial-misalignment-dependent: the original setting performs better for Cup
on 600-point direct inlier error, and both PICP settings fail to recover the
30-degree Apple pose reliably. PICP can also score worse than ICP on *all-point*
NN-RMSE because those measurements include intentionally displaced outliers.
Do not equate the paper's probability-weighted RMS with common RMSE.

**Correspondence clarification from paper Equation (8):** the paper calls the
method "one-to-one", but defines the match as each source point selecting its
nearest model point independently. It does **not** impose a global bijection
and model points may be reused. This project uses exactly that nearest-neighbor
rule. A Hungarian assignment would be an algorithm change, not a correction
required by Equation (8).

**Research validity warning:** the new independent-seed checks are exploratory
follow-ups, not a blind hold-out or a pre-registered hyperparameter search. Do
not claim universal PICP superiority or exact reproduction of the numerical
results in the original article. Validate the final selected setting against
predeclared settings, additional data, noise regimes, and seeds if time allows.
