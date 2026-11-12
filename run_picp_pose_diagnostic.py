"""Explore sensitivity to initial misalignment, retaining paper's identity R0/t0.

The generated source pose changes; this is NOT a change to PICP's initial
transformation. No settings are automatically optimized or overwritten.
"""
from pathlib import Path
import sys,csv
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'code'))
import main as picp
OUT=ROOT/'results'/'diagnostics'
OUT.mkdir(parents=True,exist_ok=True)
POSE_ANGLES=(5.0,15.0,30.0)
N_TRIALS=10

def generate(model,angle,seed):
    rng=np.random.default_rng(seed)
    theta=np.deg2rad(angle)
    rot=np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
    clean=model@rot.T+np.array([12.0,-8.0])
    source=clean+rng.normal(0,0.4,clean.shape)
    x,y=clean[:,0],clean[:,1]
    mask=(x<np.percentile(x,25))&(y>np.percentile(y,20))&(y<np.percentile(y,80))
    source[mask]+=rng.normal(loc=(-12,-12),scale=2.0,size=(mask.sum(),2))
    return source,mask

def run():
    model=picp.load_shape_points('apple-1.gif',300)
    rows=[]
    for angle in POSE_ANGLES:
        for t in range(N_TRIALS):
            seed=20270201+t
            source,mask=generate(model,angle,seed)
            cases=[('ICP',*picp.run_icp(source,model,max_iterations=60)[:1],None)]
            for label,lam,scale in [('PICP baseline',1.4,0.2),('PICP slow-anneal candidate',1.1,0.05)]:
                a,_,_,p=picp.run_picp(source,model,max_iterations=60,lambda_anneal=lam,initial_variance_scale=scale)
                cases.append((label,a,p))
            for label,aligned,prob in cases:
                e=picp.evaluate_result(aligned,model,mask)
                rows.append({'Angle_deg':angle,'Trial':t+1,'Seed':seed,'Method':label,
                             'DirectInlierRMSE':e['Direct_RMSE_Inliers'],
                             'AllNNRMSE':e['NN_RMSE_All'],
                             'ESS':float(1/np.sum(prob**2)) if prob is not None else ''})
        print('Pose angle',angle,'completed',flush=True)
    path=OUT/'apple_pose_trials.csv'
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    lines=['# Apple initial-misalignment diagnostic','','All methods begin with identity rotation and zero translation. '+
           'The test source is generated at the listed true pose, with fixed translation (12,-8), '+
           'identical Gaussian-noise seeds across angles, and a region-based corruption mask. '+
           'N=300; ten trials per angle. This is an exploratory pose sensitivity analysis.','',
           '| True source angle | Method | Direct inlier RMSE (mean ± SD) | All NN RMSE (mean ± SD) | ESS |',
           '|---:|---|---:|---:|---:|']
    for angle in POSE_ANGLES:
        for label in ['ICP','PICP baseline','PICP slow-anneal candidate']:
            grp=[r for r in rows if r['Angle_deg']==angle and r['Method']==label]
            direct=np.array([r['DirectInlierRMSE'] for r in grp]); allnn=np.array([r['AllNNRMSE'] for r in grp])
            ess='n/a' if label=='ICP' else f"{np.mean([r['ESS'] for r in grp]):.1f}"
            lines.append(f'| {angle:.0f}° | {label} | {direct.mean():.3f} ± {direct.std(ddof=1):.3f} | {allnn.mean():.3f} ± {allnn.std(ddof=1):.3f} | {ess} |')
    (OUT/'apple_pose_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('\n'.join(lines[-9:]))
if __name__=='__main__':run()
