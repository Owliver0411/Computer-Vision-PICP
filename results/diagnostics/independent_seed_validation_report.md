# Independent-seed exploratory validation

Ten previously unused seeds for each of Apple, Cup and Children at 300 points; the data generator and 15-degree/(12,-8) synthetic pose remain unchanged. These are independent cases, **not** blind preregistered model selection. PICP baseline is lambda 1.4, initial variance scale 0.20; the candidate lambda 1.1/scale 0.05 was selected for examination following the Apple sweep. ICP is evaluated on exactly the same cases. Lower RMSE is better.

| Shape | Method | Direct inlier RMSE | All NN-RMSE | ESS |
|---|---|---:|---:|---:|
| Apple | ICP | 6.697 ± 0.151 | 5.136 ± 0.084 | n/a |
| Apple | PICP Baseline | 3.057 ± 0.794 | 5.807 ± 0.180 | 3.7 |
| Apple | PICP Apple-sweep candidate | 0.606 ± 0.081 | 6.181 ± 0.114 | 248.5 |
| Cup | ICP | 4.148 ± 0.132 | 5.043 ± 0.099 | n/a |
| Cup | PICP Baseline | 0.586 ± 0.024 | 5.818 ± 0.116 | 11.9 |
| Cup | PICP Apple-sweep candidate | 0.643 ± 0.034 | 5.720 ± 0.127 | 260.9 |
| Children | ICP | 3.306 ± 0.091 | 4.673 ± 0.120 | n/a |
| Children | PICP Baseline | 0.606 ± 0.034 | 5.352 ± 0.150 | 3.0 |
| Children | PICP Apple-sweep candidate | 0.574 ± 0.017 | 5.325 ± 0.131 | 253.7 |

The candidate is a documented sensitivity variant, not asserted to be the paper-author-recommended hyperparameters. The original project baseline remains unchanged.
