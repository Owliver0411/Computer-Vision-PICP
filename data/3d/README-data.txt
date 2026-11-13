3D DATASET PROVENANCE AND REPRODUCTION
======================================

Bundled official Stanford Bunny data (REAL scanned geometry):
  bun_zipper.ply                High-resolution zipper-reconstructed Stanford Bunny
                                mesh with 35,947 vertices; imported as a point cloud
                                by reading the vertex x, y, z fields (triangles unused).
  bun000_raw.ply                A single raw range scan included as provenance and
                                for potential future scan-to-model work. NOT used in
                                our reported Bunny experiments.
  bun.conf                     Original configuration with transforms of the separate
                                raw Bunny scans. NOT used by the experiments.
  STANFORD_RECONSTRUCTION_README.txt and STANFORD_RANGE_README.txt
                                Unmodified explanatory files from the original archive.
  Source: Stanford Computer Graphics Laboratory, Stanford 3D Scanning Repository
  Official page: https://graphics.stanford.edu/data/3Dscanrep/
  Official archive: https://graphics.stanford.edu/pub/3Dscanrep/bunny.tar.gz
  Original upload: bunny.tar.gz supplied by user, extracted on 2026-11-12.

Terms: Stanford permits use for research and free redistribution with acknowledgement.
Credit Stanford Computer Graphics Laboratory in reports and figures. Commercial
use needs Stanford permission. Verify current terms at the official page.

Bundled procedural 3D benchmark shapes (SYNTHETIC, NOT scans):
  asymmetric_shell.ply         non-planar synthetic surface, 7,000 points
  curved_tube.ply              non-planar synthetic surface, 7,000 points
These shapes are regenerated using the deterministic seed 2026 from
code/three_d_data.py and prepare_3d_data.py.

Experiment on real Stanford Bunny GEOMETRY:
  python run_picp_3d.py --bunny-only --output results/3d_bunny
  python run_picp_3d.py --bunny-only --overlap 0.75 --outliers 0.30 --output results/3d_bunny_partial

What is real and what is simulated:
- The surface points come from an actual optically scanned and reconstructed Bunny.
- Our registration pairs are then synthetically generated from vertices of that
  SAME reconstruction by applying a known rigid transform, noise and outliers.
- The 75% overlap experiment deletes the highest-z 25% of the source samples.
- These are controlled experiments on real scanned GEOMETRY, not independent
  two-view sensor scans, and not validation of real scan-to-scan alignment.
- We normalise the longest bounding-box side to 1 unit, select 350 model
  vertices per run, apply Euler xyz (12,-9,15) deg, translation (0.18,-0.10,0.08),
  Gaussian noise std 0.005 units and outliers 10% or 30%. Base seed 20261112.
- All direct correspondence metrics rely on these synthetic known poses.
