"""Regression checks for transparent reproducible sensitivity diagnostics."""
import sys
import unittest
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import main as picp

class TestPICPDiagnostics(unittest.TestCase):
    def test_annealing_range_validation(self):
        rng=np.random.default_rng(2)
        x=rng.normal(size=(20,2))
        with self.assertRaises(ValueError):
            picp.run_picp(x,x,lambda_anneal=2.1)
        with self.assertRaises(ValueError):
            picp.run_picp(x,x,lambda_anneal=1.0)

    def test_probabilities_ess_and_direct_metric_finite(self):
        rng=np.random.default_rng(3)
        points=rng.normal(size=(50,2))
        source=points+np.array([0.5,0.2])
        for lam,scale in ((1.4,0.2),(1.1,0.05)):
            aligned,nh,wh,p=picp.run_picp(source,points,max_iterations=10,
                            lambda_anneal=lam,initial_variance_scale=scale)
            self.assertTrue(np.isfinite(aligned).all())
            self.assertTrue(np.isfinite(p).all())
            self.assertAlmostEqual(float(p.sum()),1.0,places=10)
            ess=float(1.0/np.sum(p*p))
            self.assertGreaterEqual(ess,1.0-1e-8)
            self.assertLessEqual(ess,len(source)+1e-8)
            self.assertEqual(len(nh),len(wh))
            mask=np.zeros(len(points),dtype=bool)
            self.assertTrue(np.isfinite(picp.evaluate_result(aligned,points,mask)['Direct_RMSE_Inliers']))

if __name__=='__main__':unittest.main()
