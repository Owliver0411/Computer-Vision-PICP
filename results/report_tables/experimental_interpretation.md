# Experimental interpretation and limitations

## Main experiment

The main experiment contains five independent trials for each of Apple, Cup,
and Children. The common all-point nearest-neighbour RMSE is lower-is-better
and is used for the primary comparison across methods.

In the current synthetic setup, PICP does **not** achieve the lowest all-point
nearest-neighbour RMSE on any of the three shapes. Its mean all-point RMSE is
approximately 5.86 for Apple, 5.70 for Cup, and 5.50 for Children, compared
with approximately 4.75, 4.80, and 4.83 for standard ICP, respectively.
Therefore, these experiments do not support a general claim that this
implementation outperforms ICP under the current corruption and initialisation
settings.

PICP's inlier-only nearest-neighbour RMSE is lower than ICP for all three
shapes, but this metric allows a point to match a nearby point on the contour
rather than its original corresponding point. The direct inlier RMSE provides
a complementary check: PICP is substantially worse on Apple, while it is
similar to ICP on Cup and Children. The difference between these metrics is
important and should be discussed rather than hiding one of them.

PICP's probability-weighted RMS is its internal objective, not a common
cross-method evaluation metric. Its effective sample size is also small for
Apple and Children, showing that the probability mass is concentrated on a
small subset of points. This is a warning that many points contribute little
to the weighted transform and that the result may be sensitive to the selected
correspondences.

## Robustness experiment

The robustness sweep tests 10%, 20%, 30%, and 40% randomly selected synthetic
outliers, using five trials per shape and outlier rate. It uses 300 contour
points and a 30-iteration cap to keep the sweep tractable. The full per-method
all-point, inlier, outlier, and direct-inlier metrics are available in
`robustness_trials.csv` and the generated robustness report table.

Do not describe the robustness sweep as proving PICP superiority unless the
common all-point and direct-inlier metrics support that conclusion across
shapes and outlier levels. If performance varies by shape or outlier rate,
report the variation explicitly.

## What can be concluded

The code now reports complementary metrics and a larger repeat count than the
original three-trial run. However, the synthetic experiments are not an exact
reproduction of every detail of the paper's experimental protocol. The
soft-correspondence baseline is simplified. A definitive paper reproduction
would require matching the paper's exact data preparation, noise model,
initialisation, baseline implementation, parameter selection, and RMS
calculation. The results should be presented as a controlled implementation
and evaluation of the PICP method, with these limitations clearly stated.
