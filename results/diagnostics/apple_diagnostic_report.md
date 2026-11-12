# Apple sensitivity diagnosis (paired, n=10 seeds)

**Setup.** 300 contour points; identical source/model pairs and random seeds for each
configuration; 15-degree initial rotation, (12,-8) translation, Gaussian noise
standard deviation 0.4 pixels, and a structured corrupted patch. The PICP
algorithm starts with identity rotation and zero translation. Each run allows
up to 60 iterations. Source-index correspondence is known because the
source is generated from the model, so **direct inlier RMSE** is the more
informative measure of recovered registration than nearest-neighbour RMSE.

**Paper consistency.** Equation (8) specifies one nearest model point for each
source point; it does not enforce unique target matches across all sources.
The KD-tree nearest-neighbour implementation follows that equation. PICP uses
uniform initial point probabilities, probability-weighted SVD, and variance
annealing with lambda in (1,2]. The initial variance scale is an implementation
choice, not a numerical setting documented by the paper.

**Predeclared project baseline:** lambda=1.4, initial variance scale=0.20.
For that setting mean PICP direct inlier RMSE =
2.876 ± 0.863 pixels,
versus ICP = 6.619 ± 0.146
pixels. Mean PICP ESS is 3.0 / 300 points.

**Sensitivity overview:** Across 12 examined configurations, PICP direct inlier
RMSE means span 0.627 to
17.690 pixels. The numerically
best grid result is lambda=1.1, scale=0.05,
but this is **not** an unbiased held-out test or justification for replacing
the baseline. The complete grid is shown below.

| lambda | variance scale | PICP direct inlier | ICP direct inlier | PICP all NN | ESS | PICP better / 10 |
|---|---|---|---|---|---|---|
| 1.1 | 0.05 | 0.627 ± 0.090 | 6.619 ± 0.146 | 6.084 | 248.6 | 10 |
| 1.1 | 0.20 | 4.297 ± 0.229 | 6.619 ± 0.146 | 5.269 | 275.3 | 10 |
| 1.1 | 0.50 | 5.712 ± 0.241 | 6.619 ± 0.146 | 5.091 | 293.9 | 10 |
| 1.4 | 0.05 | 5.990 ± 0.322 | 6.619 ± 0.146 | 5.997 | 2.0 | 10 |
| 1.4 | 0.20 | 2.876 ± 0.863 | 6.619 ± 0.146 | 5.741 | 3.0 | 10 |
| 1.4 | 0.50 | 1.106 ± 0.349 | 6.619 ± 0.146 | 5.900 | 6.4 | 10 |
| 1.8 | 0.05 | 16.929 ± 0.616 | 6.619 ± 0.146 | 7.859 | 1.7 | 0 |
| 1.8 | 0.20 | 13.143 ± 0.926 | 6.619 ± 0.146 | 7.112 | 1.6 | 0 |
| 1.8 | 0.50 | 9.874 ± 0.681 | 6.619 ± 0.146 | 6.061 | 1.7 | 0 |
| 2.0 | 0.05 | 17.690 ± 0.676 | 6.619 ± 0.146 | 7.683 | 1.6 | 0 |
| 2.0 | 0.20 | 15.631 ± 0.894 | 6.619 ± 0.146 | 7.526 | 1.4 | 0 |
| 2.0 | 0.50 | 12.846 ± 0.782 | 6.619 ± 0.146 | 6.826 | 1.6 | 0 |

**Metric interpretation.** PICP probability-weighted RMS is an internal objective,
not directly comparable with ICP common nearest-neighbour RMSE. ESS very near
1 indicates strong probability concentration: a low weighted RMS can be caused
by the algorithm placing almost all weight on one or a few points, rather than
accurately aligning the entire contour.

**Limits.** This examines Apple only, one shape image, one corruption recipe,
and 10 seeds; do not generalize to the entire CE-Shape-1 benchmark or the
paper's original noise distribution. The baseline experiment remains unchanged.
