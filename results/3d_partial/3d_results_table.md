# 3D registration results

All errors are in normalised object units unless otherwise specified.
Lower is better for errors. ESS is effective sample size; higher is not automatically better.
All-point NN-RMSE includes known synthetic outliers; direct inlier RMSE excludes them.
Pose success = rotation error < 5 degrees AND translation error < 0.05 object units.

| Shape | Outliers | Overlap | Method | Direct inlier RMSE | NN-RMSE all | Rotation (deg) | Translation | Success |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| asymmetric_shell | 30% | 75% | ICP | 0.1299 ± 0.0274 | 0.1345 ± 0.0061 | 17.0790 ± 2.9125 | 0.1102 ± 0.0236 | 0% |
| asymmetric_shell | 30% | 75% | Soft-EM-ICP (simplified) | 0.2096 ± 0.0394 | 0.1357 ± 0.0063 | 38.8748 ± 7.8807 | 0.1540 ± 0.0363 | 0% |
| asymmetric_shell | 30% | 75% | PICP (original) | 0.0261 ± 0.0302 | 0.1479 ± 0.0096 | 3.2396 ± 5.3830 | 0.0043 ± 0.0050 | 67% |
| asymmetric_shell | 30% | 75% | PICP (slow annealing) | 0.0087 ± 0.0002 | 0.1477 ± 0.0096 | 0.1728 ± 0.1101 | 0.0016 ± 0.0004 | 100% |
| curved_tube | 30% | 75% | ICP | 0.1855 ± 0.0336 | 0.1346 ± 0.0050 | 28.2939 ± 5.4720 | 0.1373 ± 0.0388 | 0% |
| curved_tube | 30% | 75% | Soft-EM-ICP (simplified) | 0.1824 ± 0.0365 | 0.1354 ± 0.0048 | 27.4079 ± 4.6336 | 0.1422 ± 0.0381 | 0% |
| curved_tube | 30% | 75% | PICP (original) | 0.0976 ± 0.0047 | 0.1577 ± 0.0038 | 17.6776 ± 1.4763 | 0.0725 ± 0.0073 | 0% |
| curved_tube | 30% | 75% | PICP (slow annealing) | 0.0183 ± 0.0167 | 0.1569 ± 0.0096 | 2.3405 ± 3.7599 | 0.0063 ± 0.0076 | 67% |
