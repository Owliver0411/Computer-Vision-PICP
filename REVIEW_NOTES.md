# Review notes for the PICP project

## Corrections and improvements made

- Corrected PICP's initial probability from `1 / N_y` to the paper's
  `1 / N_x`. This matters when source and target point counts differ.
- Added validation for the PICP annealing parameter (`1 < lambda <= 2`),
  dimensions, weights and iteration limits.
- Reused the target KD-tree during iterations rather than rebuilding it.
- Kept PICP's paper-defined probability-weighted RMS, but reported it
  separately from the common unweighted nearest-neighbour RMSE.
- Added inlier/outlier evaluation. The synthetic outlier mask is known, so
  this separates clean-point alignment from deliberate outlier rejection.
- Added the effective sample size `1 / sum(p_i^2)` and maximum probability
  to help detect probability concentration.
- Increased the experiment from one noise realisation per shape to three
  deterministic trials per shape and added mean/std summary output.
- Renamed the EM baseline to `Soft-EM-ICP (simplified)` and documented that
  it is not a full implementation of the Granger-Pennec multi-scale EM-ICP
  method cited by the original PICP paper.
- Filled the previously empty `algorithm.txt` and `data/README-data.txt`.
- Added basic unit tests for the SVD transform and unequal source/target
  point counts in PICP.

## Verification performed

- `python -m unittest discover -s tests -v`: 2 tests passed.
- `bash run.sh` was executed from outside the project directory successfully.
- The experiment generated trial-level metrics, a mean/std summary, four
  figures and an Apple probability diagnostic CSV.

## Important limitations to disclose in the final report

1. The synthetic perturbation parameters are defined by this implementation;
   they are not confirmed as the exact noise generation parameters used in
   the paper.
2. The project uses a KD-tree instead of the Delaunay triangulation mentioned
   in the paper for nearest-neighbour search.
3. The Soft-EM-ICP baseline is a simplified soft-assignment comparison method,
   not a full reproduction of the Granger-Pennec multi-scale EM-ICP paper.
4. The PICP probability-weighted RMS and the unweighted ICP RMSE are not the
   same metric. Report a common metric for all methods and show PICP's weighted
   objective separately.
5. Effective sample size can be small in some trials. Discuss this as possible
   probability concentration; do not interpret a very low weighted RMS alone
   as proof that every point has aligned well.
6. The written project report is not included in this archive. It still needs
   to be authored and submitted separately.
