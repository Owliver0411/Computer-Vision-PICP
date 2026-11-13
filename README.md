# Probability Iterative Closest Point (PICP): 2D reproduction and 3D extension

**Course:** Computer Vision, Vrije Universiteit Brussel  
**Paper:** Liu, J., Du, S., Zhang, C., Zhu, J., Li, K., and Xue, J. (2014). *Probability Iterative Closest Point Algorithm for Position Estimation*, ITSC, pp. 458–463. DOI: [10.1109/ITSC.2014.6957732](https://doi.org/10.1109/ITSC.2014.6957732). Original paper in `PICP.pdf`.

**Team:** Enter the names of all three students here before submission.  
**Hardware:** Enter your CPU, RAM, and measured runtime before submission.

## What we implemented

- **Standard ICP:** hard nearest-neighbour correspondence; unweighted SVD transformation.
- **Soft-EM-ICP (simplified):** Gaussian soft correspondences; this is *not* a complete reproduction of the Granger–Pennec EM-ICP algorithm.
- **PICP (original study configuration):** nearest-neighbour correspondence and probability-weighted SVD, with variance annealing. Our chosen baseline configuration is `lambda=1.4`, `variance_scale=0.20`; these are **our** choices, not uniquely prescribed by the paper.
- **PICP (slow-annealing exploratory variant):** `lambda=1.1`, `variance_scale=0.05`, compared without replacing the original baseline.

The original project uses MPEG-7 **2D** Apple, Cup, and Children contour images. The **3D extension** includes two **procedurally generated** 3D point clouds **and the real reconstructed Stanford Bunny geometry** (`bun_zipper.ply`, 35,947 vertices). The 3D extension is **not** a numerical replication of the paper's 2D Table II.

## Python requirements

Python **3.10+** and a CPU. No GPU is necessary.

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Open3D is **optional** (only for external interactive viewing); the included project uses Matplotlib for 3D figures and NumPy for PLY parsing. Git is optional and should not go in `requirements.txt`.

## One-command reproduction

From the project root:

```bash
bash run.sh
```

Or on Windows without Bash:

```powershell
python run_all.py
```

These commands run: 2D main experiment, procedural 3D full-overlap experiment, **Stanford Bunny** full-overlap experiment, both **75% source-coverage partial-overlap experiments** (procedural 3D and Bunny), then 2D table generation. They do **not** rerun the optional 2D robustness and Apple diagnostic sweeps, which have separate scripts. They require only the bundled data and installed Python requirements.

### 3D experiment alone

```bash
python run_picp_3d.py
```

Defaults: 2 offline synthetic shapes, 350 target points each, 10% and 30% injected outliers, 3 seeds each, max 35 iterations, full overlap; 12 datasets/cases × 4 methods = 48 algorithm results. Seed base: `20261112`, with deterministic offsets for each shape, outlier rate, and trial. Gaussian inlier noise is 0.005 normalised units. Output under `results/3d/` includes trials, mean/std summary, figures, and an experiment config JSON.

Optional partial overlap (source retains the lowest-z 75% of corresponding surface points, plus corruption):

```bash
python run_picp_3d.py --overlap 0.75 --outliers 0.30 --output results/3d_partial
```

Defaults as above except overlap/rate; partial experiment output is included in this ZIP. This is a **controlled synthetic missing-surface condition**, not a real partial sensor scan.

### Real Stanford Bunny (included)

The official Stanford Bunny reconstructed mesh is **bundled** in
`data/3d/bun_zipper.ply`. The original archive was supplied by a group member;
Stanford Computer Graphics Laboratory must be credited. A separate original raw
range scan (`bun000_raw.ply`) and the original Stanford dataset notes are also
bundled for provenance, but the experiments below use the **reconstructed mesh
vertices**, not the raw scan.

```powershell
python run_picp_3d.py --bunny-only --output results/3d_bunny
python run_picp_3d.py --bunny-only --overlap 0.75 --outliers 0.30 --output results/3d_bunny_partial
```

The standard `python run_all.py` runs **both** Bunny experiments, saving
full-overlap results under `results/3d_bunny/` and 75% source-coverage results under
`results/3d_bunny_partial/`. The separate commands above let you run only one condition.

**Important difference:** The original 3D object geometry is from a real
optical scan, but the two registration inputs are NOT two independently
captured sensor scans. We sample vertices from the **same reconstructed Bunny**,
apply a known 3D rotation, translation, Gaussian noise, and some synthetic
outlier displacements. This provides ground-truth registration error and
reproducible comparison, but should be described as **synthetic transformations
of real scanned geometry**. The partial-overlap experiment removes part of
one source surface, also in software.

No extra PIP package (including Open3D) is required to read the official
Bunny's PLY. A fresh download is **not** required. In case of a missing file,
`python prepare_3d_data.py --download-bunny` can recover it when internet is
available. See `data/3d/README-data.txt` for source credit and usage terms.


## Optional single-case runtime and accuracy demo

`benchmark_single_case.py` compares **one generated registration case** on one
2D object and/or one 3D object, using the **same input point sets** for ICP,
the simplified Soft-EM-ICP baseline, the original PICP configuration, and the
slower-annealing PICP variant. It is separate from the multi-trial experiments
and is **not run by `run_all.py`**.

From the project root (put `benchmark_single_case.py` next to `run_all.py`):

```powershell
python benchmark_single_case.py
python benchmark_single_case.py --mode 2d
python benchmark_single_case.py --mode 3d
python benchmark_single_case.py --mode 2d --shape cup-1.gif
```

The default 2D input is Apple (`apple-1.gif`, 300 points) and the default 3D
input is Stanford Bunny (`bun_zipper.ply`, 350 sampled points), both with
synthetically introduced misalignment and corruption. The script uses seed 42
by default. It saves:

- `results/single_case_benchmark/single_case_results.csv` (per-method runtime,
  iterations, all-point NN-RMSE, direct inlier RMSE, and PICP weighted RMS)
- `results/single_case_benchmark/2d_registration.png`
- `results/single_case_benchmark/3d_registration.png`

**How to interpret:** Execution time measures registration only, excluding
file loading, plotting, and metric computation. For 2D and 3D, timings use the
same process but different datasets; they are not directly comparable as
algorithmic complexity measures. 2D errors are in pixels and 3D errors in
normalised object units. One timed run can be affected by machine load and
Python start-up/warm-up effects, so it is a **demonstration, not a statistically
reliable speed ranking**. For report-quality runtime claims, repeat the same
case many times and report median and variability on the submission machine.

The `tests/` folder is different: its unit tests check correctness and are
worth keeping. Run them with `python -m pytest -q`.

## Dataset and methods (read before reporting results)

### 2D

`data/` includes MPEG-7 binary shape GIFs. `code/main.py` thresholds contours, samples at most 600 boundary points, rotates by 15°, translates by `(12,-8)` pixels, adds Gaussian noise (0.4 px) and region-specific displaced points. The 2D baseline uses five trials per shape, random seed base `42`. The 2D Apple diagnostic examined annealing sensitivity; see `results/diagnostics/`.

### 3D

`data/3d/asymmetric_shell.ply` and `data/3d/curved_tube.ply` were generated with fixed seed `2026` by `code/three_d_data.py`; in addition, **Stanford Bunny reconstructed scanned geometry** is bundled as `data/3d/bun_zipper.ply`. They have nonzero depth variation in all dimensions. Points are centred and scaled so the longest bounding-box dimension is 1 unit. For each trial, the script samples 350 model points with fixed seed, applies the known 3D Euler rotation `(12°, -9°, 15°)` about xyz axes and translation `(0.18,-0.10,0.08)`, adds Gaussian noise (std 0.005 units), and corrupts a fixed fraction of source points with displaced noise (mean `(0.22,-0.22,0.15)` and std 0.18). Labels identify true inliers and their exact source-to-model correspondence. The underlying 3D coordinates remain real 3D rather than lifted planar 2D curves.

`--overlap 0.75` removes the highest-z 25% of points from the source cloud before noise and outlier injection. The target retains the full sampled surface. The experiment reports that overlap is generated, not measured.

### Metrics

- **Common all-point NN-RMSE:** distance of *each* aligned source point to the closest target point, including injected outliers.
- **NN-RMSE inliers:** same metric restricted to clean-correspondence source points.
- **Direct inlier RMSE:** distance to each point's original known counterpart, only possible for these synthetic test cases. The most interpretable registration accuracy measure here.
- **3D rotation error (degrees):** geodesic angle between estimated and known inverse rigid rotation.
- **3D translation error (normalised units):** distance between estimated and known inverse translation.
- **Pose success:** rotation error < 5 degrees **and** translation error < 0.05 normalised units (predeclared evaluation criterion, not from the paper).
- **PICP weighted RMS:** PICP-internal objective, **not** directly comparable to unweighted ICP errors.
- **Effective sample size (ESS):** `1 / sum(p_i^2)` (normalised probabilities); small values indicate concentrated weights.

The 3D runner does not tune hyperparameters to win. It compares fixed original-project and exploratory configurations on identical generated point sets. The exploratory configuration came from earlier 2D Apple experiments: it is **not an independently pre-registered hypothesis**. A separate external scanner dataset or independent held-out geometry would be required for a stronger generalisation claim.

## Where to find output

| Output | Content |
|---|---|
| `results/metrics.csv`, `results/metrics_summary.csv` | Original 2D trial values and summary |
| `results/figures/` | Original 2D figures |
| `results/robustness/` | 2D outlier sweep |
| `results/diagnostics/` | 2D Apple hyperparameter and pose diagnostics |
| `results/3d/trials.csv` | One row per 3D method and trial |
| `results/3d/summary.csv` | Mean/std per object, noise, method |
| `results/3d/3d_results_table.md` | Readable 3D table |
| `results/3d/figures/` | Static 3D registration and common-metric convergence figures |
| `results/3d_partial/` | Extra synthetic partial-overlap experiment |
| `results/3d_bunny/` | Real Stanford Bunny geometry, synthetic misalignment/noise/outliers; saved CSVs and figures |
| `results/3d_bunny_partial/` | 75% source coverage on Stanford Bunny geometry; synthetic corruption |
| `results/report_tables/` | 2D report-oriented tables |
| `results/single_case_benchmark/` | Optional one-case runtime and alignment demonstration (created only if run) |
| `PICP_Report.tex`, `PICP_Report.pdf` | Editable and compiled course report |
| `algorithm.txt` | Instructor pseudocode submission |

The 3D results in this archive are produced with **3 repeats** per condition: they demonstrate feasibility but are too few for strong statistical conclusions.

### Expected verification values (archive's saved defaults)

At 30% injected 3D outliers, full overlap, mean direct inlier RMSE (normalised units) approximately:

| Dataset | ICP | PICP original | PICP slow |
|---|---:|---:|---:|
| Asymmetric shell | 0.1575 | 0.0086 | 0.0086 |
| Curved tube | 0.1388 | 0.0089 | 0.0089 |

### Stanford Bunny results (real scanned geometry, synthetic registration task)

The bundled high-resolution Bunny reconstruction has 35,947 vertices, from
which we sample 350 points for each experiment. All metrics are in normalised
object units. Mean direct inlier RMSE at 30% outliers and full overlap,
over three independent fixed seeds:

| ICP | Simplified Soft-EM-ICP | PICP original | PICP slow |
|---:|---:|---:|---:|
| 0.1359 | 0.1278 | **0.0086** | **0.0086** |

At 75% source coverage and 30% outliers, the means were 0.0729, 0.0813,
0.0086 and 0.0087 respectively. All-point NN-RMSE did **not** always favour
PICP, since outliers are included. See `results/3d_bunny/summary.csv` and
`results/3d_bunny_partial/summary.csv` for rotation, translation, runtime,
ESS and full tables. Three trials cannot support broad real-world claims.

The 2D main all-point NN-RMSE means are approximately: Apple ICP `4.747`, PICP `5.857`; Cup ICP `4.801`, PICP `5.704`; Children ICP `4.831`, PICP `5.497` (pixel units). Do not confuse 2D pixel values with 3D normalised units.

**Warnings:** PICP need not win the all-point NN-RMSE; it discounts outliers. The original PICP paper's Table II is for different conditions and RMS definitions; do not directly compare the table's tiny PICP RMS with our inlier RMSE. Soft-EM-ICP is simplified. Two 3D datasets are synthetic; the included Stanford Bunny is genuinely scanned reconstructed geometry, but all source-target pairs are synthetically transformed, not independently captured scans. Runtime in CSV is measured by script on the environment that created the archive; measure it again on your own computer for your report.

## Project files

```text
PICP_Project/
  README.md, requirements.txt, run.sh, run_all.py
  PICP.pdf, PICP_Report.tex, PICP_Report.pdf, algorithm.txt
  code/main.py, code/utils.py, code/three_d_data.py, code/experiment_3d.py
  data/                            # unchanged MPEG-7 shapes
    3d/asymmetric_shell.ply, 3d/curved_tube.ply, 3d/bun_zipper.ply,
    3d/bun000_raw.ply, 3d/README-data.txt, Stanford provenance files
  prepare_3d_data.py, run_picp_3d.py, benchmark_single_case.py
  run_picp_apple_diagnostic.py, run_picp_pose_diagnostic.py,
  run_picp_validation.py, run_picp_robustness.py, generate_picp_tables.py
  tests/                           # original + new 3D tests
  results/                         # full experiment outputs
  figures/                         # report figures (2D and 3D)
  MPEG7_CE-Shape-1_Part_B/          # original extra shape dataset
```

## Project limitations and attribution

This is an *educational reproduction and 3D extension*. It does not exactly reimplement all details of the original paper, its specific Delaunay neighbour search or full EM-ICP baseline. The 3D experiments use constructed poses with known correspondence and synthetic noise, including on Stanford Bunny scanned geometry; they are not independent multi-view sensor scans. Results use data sampled from the *same object surface*, so they do not prove generalisation to new object geometries. The Stanford Bunny is included with credit to Stanford University Computer Graphics Laboratory; the repository permits research use and free redistribution with acknowledgement but disallows commercial use without permission: <https://graphics.stanford.edu/data/3Dscanrep/>.

See `results/3d/3d_results_table.md` and `results/3d_partial/3d_results_table.md` for the full table. Report source in `PICP_Report.tex` must be updated with team names, hardware, and measured wall-clock runtime before submission.
