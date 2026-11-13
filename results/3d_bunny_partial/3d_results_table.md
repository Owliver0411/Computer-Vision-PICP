# 3D registration results

All errors are in normalised object units unless otherwise specified.
Lower is better for errors. ESS is effective sample size; higher is not automatically better.
All-point NN-RMSE includes known synthetic outliers; direct inlier RMSE excludes them.
Pose success = rotation error < 5 degrees AND translation error < 0.05 object units.

| Shape | Outliers | Overlap | Method | Direct inlier RMSE | NN-RMSE all | Rotation (deg) | Translation | Success |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| bun_zipper | 30% | 75% | ICP | 0.0729 ± 0.0320 | 0.1234 ± 0.0081 | 5.4991 ± 3.6649 | 0.0620 ± 0.0198 | 33% |
| bun_zipper | 30% | 75% | Soft-EM-ICP (simplified) | 0.0813 ± 0.0028 | 0.1240 ± 0.0078 | 4.9396 ± 1.3249 | 0.0766 ± 0.0010 | 0% |
| bun_zipper | 30% | 75% | PICP (original) | 0.0086 ± 0.0001 | 0.1276 ± 0.0085 | 0.1482 ± 0.0517 | 0.0011 ± 0.0004 | 100% |
| bun_zipper | 30% | 75% | PICP (slow annealing) | 0.0087 ± 0.0001 | 0.1275 ± 0.0085 | 0.2033 ± 0.0997 | 0.0016 ± 0.0008 | 100% |
