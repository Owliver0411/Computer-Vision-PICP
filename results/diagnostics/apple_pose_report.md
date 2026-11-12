# Apple initial-misalignment diagnostic

All methods begin with identity rotation and zero translation. The test source is generated at the listed true pose, with fixed translation (12,-8), identical Gaussian-noise seeds across angles, and a region-based corruption mask. N=300; ten trials per angle. This is an exploratory pose sensitivity analysis.

| True source angle | Method | Direct inlier RMSE (mean ± SD) | All NN RMSE (mean ± SD) | ESS |
|---:|---|---:|---:|---:|
| 5° | ICP | 6.565 ± 0.195 | 5.222 ± 0.054 | n/a |
| 5° | PICP baseline | 0.592 ± 0.017 | 6.369 ± 0.077 | 4.6 |
| 5° | PICP slow-anneal candidate | 0.793 ± 0.137 | 6.210 ± 0.093 | 243.7 |
| 15° | ICP | 6.635 ± 0.190 | 5.082 ± 0.048 | n/a |
| 15° | PICP baseline | 2.873 ± 1.090 | 5.725 ± 0.293 | 5.6 |
| 15° | PICP slow-anneal candidate | 0.711 ± 0.163 | 6.073 ± 0.091 | 248.9 |
| 30° | ICP | 36.240 ± 1.995 | 7.433 ± 0.099 | n/a |
| 30° | PICP baseline | 42.151 ± 0.684 | 8.757 ± 0.084 | 2.0 |
| 30° | PICP slow-anneal candidate | 38.873 ± 1.280 | 8.466 ± 0.087 | 203.0 |
