"""Small correctness tests for the core registration routines."""

import sys
import unittest
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "code"))

from main import compute_svd_transformation, run_picp  # noqa: E402


class TestPICPAlgorithms(unittest.TestCase):
    def test_weighted_svd_recovers_known_rigid_transform(self):
        rng = np.random.default_rng(7)
        source = rng.normal(size=(100, 2))
        angle = np.deg2rad(23.0)
        expected_rotation = np.array(
            [[np.cos(angle), -np.sin(angle)],
             [np.sin(angle),  np.cos(angle)]]
        )
        expected_translation = np.array([3.5, -2.0])
        target = source @ expected_rotation.T + expected_translation

        rotation, translation = compute_svd_transformation(source, target)
        recovered = source @ rotation.T + translation

        self.assertTrue(np.allclose(rotation, expected_rotation, atol=1e-10))
        self.assertTrue(np.allclose(translation, expected_translation, atol=1e-10))
        self.assertTrue(np.allclose(recovered, target, atol=1e-10))

    def test_picp_supports_different_source_and_target_sizes(self):
        rng = np.random.default_rng(11)
        target = rng.normal(size=(75, 2))
        source = target[:60] + np.array([1.0, -0.5])

        aligned, common_history, weighted_history, probabilities = run_picp(
            source,
            target,
            max_iterations=5,
        )

        self.assertEqual(aligned.shape, source.shape)
        self.assertEqual(probabilities.shape, (len(source),))
        self.assertTrue(np.all(np.isfinite(probabilities)))
        self.assertAlmostEqual(float(probabilities.sum()), 1.0, places=10)
        self.assertGreaterEqual(len(common_history), 1)
        self.assertEqual(len(common_history), len(weighted_history))


if __name__ == "__main__":
    unittest.main()
