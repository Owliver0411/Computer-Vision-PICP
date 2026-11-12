# 600-point additional independent-seed sensitivity check

Five previously unused seeds per shape; same corruption recipe as the main experiment. This exploratory check was conducted after viewing the Apple sweep and is not blind.

| Shape | Method | Direct inlier RMSE (mean ± SD) | All NN RMSE (mean ± SD) | ESS |
|---|---|---:|---:|---:|
| Apple | ICP | 6.978 ± 0.317 | 4.707 ± 0.015 | n/a |
| Apple | PICP baseline | 4.893 ± 0.278 | 5.833 ± 0.047 | 3.6 |
| Apple | PICP exploratory candidate | 1.821 ± 0.081 | 5.580 ± 0.028 | 499.4 |
| Cup | ICP | 4.727 ± 0.095 | 4.818 ± 0.076 | n/a |
| Cup | PICP baseline | 0.583 ± 0.011 | 5.722 ± 0.079 | 12.4 |
| Cup | PICP exploratory candidate | 1.613 ± 0.068 | 5.369 ± 0.083 | 527.2 |
| Children | ICP | 3.376 ± 0.070 | 4.780 ± 0.034 | n/a |
| Children | PICP baseline | 0.589 ± 0.015 | 5.460 ± 0.043 | 22.3 |
| Children | PICP exploratory candidate | 0.573 ± 0.006 | 5.431 ± 0.033 | 394.8 |
