# 3D registration results

All errors are in normalised object units unless otherwise specified.
Lower is better for errors. ESS is effective sample size; higher is not automatically better.
All-point NN-RMSE includes known synthetic outliers; direct inlier RMSE excludes them.
Pose success = rotation error < 5 degrees AND translation error < 0.05 object units.

| Shape | Outliers | Overlap | Method | Direct inlier RMSE | NN-RMSE all | Rotation (deg) | Translation | Success |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| asymmetric_shell | 10% | 100% | ICP | 0.0293 ± 0.0141 | 0.0898 ± 0.0144 | 2.3741 ± 2.1616 | 0.0255 ± 0.0114 | 100% |
| asymmetric_shell | 10% | 100% | Soft-EM-ICP (simplified) | 0.0477 ± 0.0144 | 0.0908 ± 0.0143 | 5.2809 ± 2.6734 | 0.0422 ± 0.0111 | 33% |
| asymmetric_shell | 10% | 100% | PICP (original) | 0.0085 ± 0.0001 | 0.0915 ± 0.0150 | 0.1271 ± 0.0776 | 0.0011 ± 0.0003 | 100% |
| asymmetric_shell | 10% | 100% | PICP (slow annealing) | 0.0085 ± 0.0001 | 0.0916 ± 0.0150 | 0.1142 ± 0.0205 | 0.0007 ± 0.0004 | 100% |
| asymmetric_shell | 30% | 100% | ICP | 0.1575 ± 0.0180 | 0.1424 ± 0.0040 | 14.6324 ± 3.3005 | 0.1404 ± 0.0184 | 0% |
| asymmetric_shell | 30% | 100% | Soft-EM-ICP (simplified) | 0.1486 ± 0.0116 | 0.1428 ± 0.0039 | 14.2998 ± 2.8732 | 0.1300 ± 0.0112 | 0% |
| asymmetric_shell | 30% | 100% | PICP (original) | 0.0086 ± 0.0001 | 0.1623 ± 0.0068 | 0.1333 ± 0.0981 | 0.0010 ± 0.0007 | 100% |
| asymmetric_shell | 30% | 100% | PICP (slow annealing) | 0.0086 ± 0.0001 | 0.1619 ± 0.0065 | 0.1539 ± 0.0945 | 0.0013 ± 0.0007 | 100% |
| curved_tube | 10% | 100% | ICP | 0.0452 ± 0.0159 | 0.1005 ± 0.0026 | 5.1842 ± 1.9564 | 0.0360 ± 0.0180 | 67% |
| curved_tube | 10% | 100% | Soft-EM-ICP (simplified) | 0.0531 ± 0.0049 | 0.1013 ± 0.0024 | 6.2360 ± 1.4245 | 0.0412 ± 0.0090 | 33% |
| curved_tube | 10% | 100% | PICP (original) | 0.0086 ± 0.0001 | 0.1037 ± 0.0028 | 0.1257 ± 0.0615 | 0.0009 ± 0.0005 | 100% |
| curved_tube | 10% | 100% | PICP (slow annealing) | 0.0086 ± 0.0001 | 0.1036 ± 0.0028 | 0.1300 ± 0.0067 | 0.0007 ± 0.0003 | 100% |
| curved_tube | 30% | 100% | ICP | 0.1388 ± 0.0046 | 0.1433 ± 0.0025 | 7.9594 ± 1.5598 | 0.1298 ± 0.0073 | 0% |
| curved_tube | 30% | 100% | Soft-EM-ICP (simplified) | 0.1149 ± 0.0061 | 0.1445 ± 0.0029 | 9.3863 ± 2.2154 | 0.1021 ± 0.0019 | 0% |
| curved_tube | 30% | 100% | PICP (original) | 0.0089 ± 0.0003 | 0.1673 ± 0.0032 | 0.1915 ± 0.0705 | 0.0015 ± 0.0007 | 100% |
| curved_tube | 30% | 100% | PICP (slow annealing) | 0.0089 ± 0.0002 | 0.1668 ± 0.0033 | 0.1216 ± 0.0325 | 0.0012 ± 0.0005 | 100% |
