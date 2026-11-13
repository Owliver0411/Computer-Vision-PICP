# 3D registration results

All errors are in normalised object units unless otherwise specified.
Lower is better for errors. ESS is effective sample size; higher is not automatically better.
All-point NN-RMSE includes known synthetic outliers; direct inlier RMSE excludes them.
Pose success = rotation error < 5 degrees AND translation error < 0.05 object units.

| Shape | Outliers | Overlap | Method | Direct inlier RMSE | NN-RMSE all | Rotation (deg) | Translation | Success |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| bun_zipper | 10% | 100% | ICP | 0.0169 ± 0.0049 | 0.0809 ± 0.0096 | 0.7897 ± 0.4548 | 0.0128 ± 0.0050 | 100% |
| bun_zipper | 10% | 100% | Soft-EM-ICP (simplified) | 0.0332 ± 0.0080 | 0.0823 ± 0.0095 | 1.7518 ± 1.0229 | 0.0300 ± 0.0072 | 100% |
| bun_zipper | 10% | 100% | PICP (original) | 0.0085 ± 0.0002 | 0.0819 ± 0.0102 | 0.1280 ± 0.0821 | 0.0013 ± 0.0005 | 100% |
| bun_zipper | 10% | 100% | PICP (slow annealing) | 0.0085 ± 0.0001 | 0.0819 ± 0.0102 | 0.1226 ± 0.0408 | 0.0009 ± 0.0003 | 100% |
| bun_zipper | 30% | 100% | ICP | 0.1359 ± 0.0068 | 0.1355 ± 0.0080 | 12.7856 ± 4.1396 | 0.1139 ± 0.0284 | 0% |
| bun_zipper | 30% | 100% | Soft-EM-ICP (simplified) | 0.1278 ± 0.0063 | 0.1360 ± 0.0082 | 8.1776 ± 2.9940 | 0.1185 ± 0.0117 | 0% |
| bun_zipper | 30% | 100% | PICP (original) | 0.0086 ± 0.0003 | 0.1491 ± 0.0085 | 0.2432 ± 0.0734 | 0.0010 ± 0.0006 | 100% |
| bun_zipper | 30% | 100% | PICP (slow annealing) | 0.0086 ± 0.0003 | 0.1488 ± 0.0085 | 0.2032 ± 0.0785 | 0.0013 ± 0.0002 | 100% |
