"""3D rigid registration and dataset tests; no external downloads needed."""
from pathlib import Path
import sys
import numpy as np
from scipy.spatial.transform import Rotation

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from main import compute_svd_transformation, run_icp, run_picp
from three_d_data import generate_synthetic_surfaces, normalize_cloud, write_ply_ascii, load_ply_xyz
from experiment_3d import build_case, evaluate_3d, get_pose


def test_3d_weighted_svd_recovers_known_rigid_pose():
    rng=np.random.default_rng(1)
    x=rng.normal(size=(60,3))
    r=Rotation.from_euler('xyz',[13,-5,29],degrees=True).as_matrix()
    t=np.array([0.3,-0.4,0.2])
    y=x@r.T+t
    r_est,t_est=compute_svd_transformation(x,y,rng.uniform(.2,1.0,size=len(x)))
    assert np.allclose(r_est,r,atol=1e-12)
    assert np.allclose(t_est,t,atol=1e-12)
    assert np.isclose(np.linalg.det(r_est),1.0)


def test_3d_synthetic_datasets_have_true_depth(tmp_path):
    shapes=generate_synthetic_surfaces(seed=2,points=100)
    assert set(shapes)=={'asymmetric_shell','curved_tube'}
    for name,cloud in shapes.items():
        assert cloud.shape==(100,3)
        assert np.ptp(cloud[:,2])>0.1
        p=tmp_path/(name+'.ply')
        write_ply_ascii(p,cloud)
        loaded=load_ply_xyz(p)
        assert np.allclose(cloud,loaded,atol=1e-8)


def test_3d_true_inverse_and_metrics():
    model=generate_synthetic_surfaces(seed=1,points=200)['asymmetric_shell']
    case=build_case(model,seed=5,outlier_rate=.2,noise_std=0)
    assert case['source'].shape==(200,3)
    aligned=case['source']@case['true_rotation'].T+case['true_translation']
    result=evaluate_3d(case,aligned)
    assert result['rotation_error_deg']<1e-5
    assert result['translation_error']<1e-10
    assert result['direct_inlier_rmse']<1e-10
    assert result['inlier_count']==160


def test_3d_registration_methods_return_finite_and_valid_results():
    model=generate_synthetic_surfaces(seed=5,points=90)['curved_tube']
    case=build_case(model,seed=22,outlier_rate=.15)
    aligned,history=run_icp(case['source'],model,max_iterations=5)
    assert aligned.shape==model.shape and np.all(np.isfinite(aligned))
    assert history and np.all(np.isfinite(history))
    for lam in (1.1,1.4):
        aligned,history,weighted,probs=run_picp(case['source'],model,max_iterations=5,lambda_anneal=lam)
        assert aligned.shape==model.shape
        assert np.isclose(probs.sum(),1.0)
        assert np.all(probs>=0)
        assert np.all(np.isfinite(history)) and np.all(np.isfinite(weighted))


def test_official_stanford_bunny_is_bundled_and_3d():
    path=ROOT/'data'/'3d'/'bun_zipper.ply'
    assert path.is_file(), 'Original Stanford Bunny reconstruction must be bundled'
    points=load_ply_xyz(path)
    assert points.shape==(35947,3)
    assert np.all(np.isfinite(points))
    assert np.all(np.ptp(points,axis=0)>0.10)


def test_stanford_bunny_rigid_pose_ground_truth():
    full=normalize_cloud(load_ply_xyz(ROOT/'data'/'3d'/'bun_zipper.ply'))
    rng=np.random.default_rng(2026)
    model=full[rng.choice(len(full), 100, replace=False)]
    case=build_case(model,seed=48,noise_std=0.0,outlier_rate=0.0)
    aligned=case['source']@case['true_rotation'].T+case['true_translation']
    metrics=evaluate_3d(case,aligned)
    assert metrics['direct_inlier_rmse']<1e-10
    assert metrics['rotation_error_deg']<1e-5
