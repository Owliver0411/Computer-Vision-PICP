DATASET AND PREPROCESSING NOTES

Dataset
-------
The project uses shape images from the CE-Shape-1 Part B collection, which is
also used in the PICP paper. The data/ folder contains selected GIF examples
from the Apple, Cup and Children shape categories. The experiment currently
uses apple-1.gif, cup-1.gif and children-1.gif.

The project archive also contains a larger copy of the MPEG7_CE-Shape-1_Part_B
folder. The main experiment does not scan that full folder; it reads the three
named files from data/ only.

Preprocessing implemented in code/main.py
------------------------------------------
1. Open each GIF and convert it to grayscale.
2. Threshold the image at intensity 128 to create a binary mask.
3. Detect boundary pixels from horizontal and vertical binary transitions.
4. Convert image coordinates (x, y) to Cartesian-style coordinates (x, -y).
5. Subtract the mean point coordinate to centre the shape at the origin.
6. If more than 600 boundary points are detected, sample 600 points at
   evenly spaced indices in the extracted pixel order.
7. Preserve the original pixel scale and aspect ratio; no resizing or
   scale-normalisation is performed.

Synthetic experiment data
-------------------------
The experiment creates a source point set by applying a 15-degree rotation
and translation [12, -8] to the centred model points. It then adds Gaussian
noise with standard deviation 0.4 pixels. A spatial patch on the left side
of the shape receives additional structured displacement noise with mean
[-12, -12] pixels and standard deviation 2 pixels. The Boolean outlier mask
is retained so inlier and outlier errors can be measured separately.

Reproducibility
---------------
The random seed base and number of trials are defined at the top of
code/main.py. The default configuration runs three noise trials per shape.
The trial seed is printed and written to results/metrics.csv.

Provenance
----------
Retain the dataset source, download record and any licence/usage statement
provided with the dataset distribution in the final submission. The PICP
paper cites the CE-Shape-1-related shape descriptor work in its references:
S. T. Latecki and R. Lakamper, "Shape descriptors for non-rigid shapes with a
single closed contour," Proceedings of the IEEE Conference on Computer Vision
and Pattern Recognition (CVPR), 2000, vol. 1, pp. 424-429.
