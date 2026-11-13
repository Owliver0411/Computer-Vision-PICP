"""3D extension of PICP paper reproduction.

Runs all 3 existing algorithms on the same synthetic rigid transforms of
non-planar point clouds. 3D study is an extension, NOT Table II replication.

No tuning on test seeds: default PICP and exploratory config are predeclared.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from time import perf_counter

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.transform import Rotation

from main import (run_icp, run_soft_em_icp, run_picp,
                  compute_svd_transformation, nearest_neighbour_distances)
from three_d_data import ensure_procedural_datasets, load_ply_xyz, normalize_cloud

PROJECT_ROOT=Path(__file__).resolve().parents[1]
DATA_DIR=PROJECT_ROOT/'data'/'3d'
OUT_DIR=PROJECT_ROOT/'results'/'3d'
DEFAULT_METHODS=('ICP','Soft-EM-ICP (simplified)','PICP (original)','PICP (slow annealing)')
METRICS=('direct_inlier_rmse','nn_all_rmse','nn_inlier_rmse',
         'rotation_error_deg','translation_error','runtime_s','effective_samples')


def build_case(model_points: np.ndarray, seed: int, outlier_rate: float=0.2,
               overlap: float=1.0, noise_std: float=0.005,
               rot_xyz_deg: tuple[float,float,float]=(12,-9,15)) -> dict:
    """Create known 3D rigid pose, independent noise and random displaced outliers.

    Target points have known ordering, and corresponding source inliers keep
    the same original target index. All metrics use these *exact* labels.
    """
    if not (0<=outlier_rate<1 and 0<overlap<=1):
        raise ValueError('outlier_rate must be [0,1); overlap must be (0,1]')
    rng=np.random.default_rng(seed)
    model=np.asarray(model_points,float)
    if model.ndim!=2 or model.shape[1]!=3 or len(model)<10:
        raise ValueError('Expected model with (N>=10, 3) coordinates')
    n_keep=max(8,int(round(len(model)*overlap)))
    # Spatially coherent missing surface: delete points with largest z.
    keep=np.argsort(model[:,2])[:n_keep] if overlap < 1 else np.arange(len(model))
    target_for_source=model[keep]
    src_R=Rotation.from_euler('xyz',rot_xyz_deg,degrees=True).as_matrix()
    src_t=np.array([0.18,-0.10,0.08])
    clean_source=target_for_source @ src_R.T+src_t
    source=clean_source+rng.normal(0,noise_std,clean_source.shape)
    n_out=int(round(outlier_rate*len(source)))
    outliers=np.zeros(len(source),bool)
    if n_out:
        chosen=rng.choice(len(source),size=n_out,replace=False)
        outliers[chosen]=True
        source[outliers] += rng.normal(loc=[0.22,-0.22,0.15],
                                       scale=0.18,size=(n_out,3))
    # Correct source -> target rigid mapping: inverse of the known generated pose.
    true_R=src_R.T
    true_t=-true_R@src_t
    return {'source':source,'target':model,'true_correspondence':target_for_source,
            'outlier_mask':outliers,'true_rotation':true_R,'true_translation':true_t,
            'seed':int(seed)}


def get_pose(source: np.ndarray, aligned: np.ndarray) -> tuple[np.ndarray,np.ndarray]:
    """Recover composed R,t from the returned aligned cloud, no algorithm changes."""
    return compute_svd_transformation(source,aligned)


def evaluate_3d(case: dict, aligned: np.ndarray, weights: np.ndarray|None=None) -> dict:
    """Unweighted shared metrics; direct only uses synthetic known inlier pairs."""
    source, target=case['source'],case['target']
    mask=~case['outlier_mask']
    if not np.any(mask): raise ValueError('No inliers')
    nn=nearest_neighbour_distances(aligned,target)
    direct=np.linalg.norm(aligned[mask]-case['true_correspondence'][mask],axis=1)
    R_hat,t_hat=get_pose(source,aligned)
    angle=Rotation.from_matrix(R_hat@case['true_rotation'].T).magnitude()
    ess=float('nan') if weights is None else float(1.0/np.sum(np.asarray(weights)**2))
    return {
        'nn_all_rmse':float(np.sqrt(np.mean(nn**2))),
        'nn_inlier_rmse':float(np.sqrt(np.mean(nn[mask]**2))),
        'direct_inlier_rmse':float(np.sqrt(np.mean(direct**2))),
        'rotation_error_deg':float(np.rad2deg(angle)),
        'translation_error':float(np.linalg.norm(t_hat-case['true_translation'])),
        'effective_samples':ess,
        'inlier_count':int(mask.sum()),
        'outlier_count':int((~mask).sum()),
    }


def run_trial(case:dict, iterations: int=40)->tuple[list[dict],dict,dict]:
    """Compute ICP, soft EM, PICP standard, PICP exploratory, all same input."""
    source,target=case['source'],case['target']
    rows=[]; aligned_clouds={}; histories={}
    algorithms=[
      (DEFAULT_METHODS[0],lambda: (*run_icp(source,target,max_iterations=iterations),None,None)),
      (DEFAULT_METHODS[1],lambda: (*run_soft_em_icp(source,target,max_iterations=iterations,
                                   initial_variance_scale=0.12,minimum_variance=1e-5),None,None)),
      (DEFAULT_METHODS[2],lambda: run_picp(source,target,max_iterations=iterations,
                                      lambda_anneal=1.4,initial_variance_scale=0.20)),
      (DEFAULT_METHODS[3],lambda: run_picp(source,target,max_iterations=iterations,
                                      lambda_anneal=1.1,initial_variance_scale=0.05)),
    ]
    for name,func in algorithms:
        t0=perf_counter()
        result=func()
        duration=perf_counter()-t0
        # ICP/Soft-EM -> (aligned, history, None, None);
        # PICP -> (aligned, history, weighted_rms_history, probabilities)
        aligned,history,weighted_history,weights=result
        vals=evaluate_3d(case,aligned,weights)
        vals.update(method=name,runtime_s=float(duration),iterations=len(history),
                    picp_weighted_rms=(float(weighted_history[-1]) if weighted_history else float('nan')))
        vals['pose_success'] = int(vals['rotation_error_deg'] < 5 and vals['translation_error'] < 0.05)
        rows.append(vals)
        aligned_clouds[name]=aligned
        histories[name]=history
    return rows,aligned_clouds,histories


def plot_3d_registration(case:dict, clouds:dict, filename:Path,title:str):
    """Side-by-side 3D views with consistent axes and two point clouds per panel."""
    panels=[('Before alignment',case['source'])]+list(clouds.items())
    fig=plt.figure(figsize=(16,7))
    target=case['target']
    for i,(label,source) in enumerate(panels,1):
        ax=fig.add_subplot(2,3,i,projection='3d')
        ax.scatter(target[:,0],target[:,1],target[:,2],s=2,alpha=0.35,color='#1d70b7',label='Target')
        ax.scatter(source[:,0],source[:,1],source[:,2],s=2,alpha=0.6,color='#d04942',label='Source')
        ax.set_title(label,fontsize=10)
        ax.view_init(elev=23,azim=44)
        allpts=np.concatenate((source,target))
        centre=(allpts.min(axis=0)+allpts.max(axis=0))/2
        radius=max(np.ptp(allpts,axis=0))*0.55
        ax.set_xlim(centre[0]-radius,centre[0]+radius)
        ax.set_ylim(centre[1]-radius,centre[1]+radius)
        ax.set_zlim(centre[2]-radius,centre[2]+radius)
        ax.set_xlabel('X');ax.set_ylabel('Y');ax.set_zlabel('Z')
    fig.suptitle(title)
    fig.tight_layout(rect=[0,0,1,0.95])
    filename.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(filename,dpi=160)
    plt.close(fig)


def plot_convergence(histories:dict, filename:Path,title:str):
    fig,ax=plt.subplots(figsize=(8,4.5))
    for method,hist in histories.items():
        ax.plot(np.arange(1,len(hist)+1),hist,label=method)
    ax.set(xlabel='Iteration',ylabel='Common all-point NN-RMSE (normalised units)',title=title)
    ax.grid(alpha=0.2);ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(filename,dpi=150);plt.close(fig)


def save_csv(path:Path, rows:list[dict]):
    if not rows: return
    path.parent.mkdir(exist_ok=True,parents=True)
    with path.open('w',newline='',encoding='utf8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
        writer.writeheader();writer.writerows(rows)


def summarize(rows:list[dict])->list[dict]:
    groups={}
    for row in rows:
        key=(row['shape'],row['outlier_rate'],row['overlap'],row['method'])
        groups.setdefault(key,[]).append(row)
    output=[]
    for (shape,outlier,overlap,method),values in groups.items():
        rec={'shape':shape,'outlier_rate':outlier,'overlap':overlap,'method':method,
             'trials':len(values)}
        for name in METRICS:
            v=np.asarray([x[name] for x in values],dtype=float)
            good=v[np.isfinite(v)]
            rec[name+'_mean']=float(np.mean(good)) if len(good) else float('nan')
            rec[name+'_std']=float(np.std(good,ddof=1)) if len(good)>1 else 0.0 if len(good) else float('nan')
        rec['success_rate']=float(np.mean([x['pose_success'] for x in values]))
        output.append(rec)
    return output


def create_markdown(summary:list[dict],outpath:Path):
    text=['# 3D registration results', '',
          'All errors are in normalised object units unless otherwise specified.',
          'Lower is better for errors. ESS is effective sample size; higher is not automatically better.',
          'All-point NN-RMSE includes known synthetic outliers; direct inlier RMSE excludes them.',
          'Pose success = rotation error < 5 degrees AND translation error < 0.05 object units.',
          '', '| Shape | Outliers | Overlap | Method | Direct inlier RMSE | NN-RMSE all | Rotation (deg) | Translation | Success |',
          '|---|---:|---:|---|---:|---:|---:|---:|---:|']
    for r in summary:
        fmt=lambda k:f"{r[k+'_mean']:.4f} ± {r[k+'_std']:.4f}"
        text.append(f"| {r['shape']} | {r['outlier_rate']:.0%} | {r['overlap']:.0%} | {r['method']} | {fmt('direct_inlier_rmse')} | {fmt('nn_all_rmse')} | {fmt('rotation_error_deg')} | {fmt('translation_error')} | {r['success_rate']:.0%} |")
    outpath.write_text('\n'.join(text)+'\n',encoding='utf8')


def parse_args(argv=None):
    p=argparse.ArgumentParser(description='3D point-cloud ICP / PICP experiment (offline)')
    p.add_argument('--points',type=int,default=350,help='Sample N points from each object')
    p.add_argument('--trials',type=int,default=3)
    p.add_argument('--iterations',type=int,default=35)
    p.add_argument('--outliers',default='0.10,0.30',help='Comma-separated outlier fractions')
    p.add_argument('--overlap',type=float,default=1.0,help='Fraction of source surface retained, e.g. 0.75')
    p.add_argument('--seed',type=int,default=20261112)
    p.add_argument('--noise',type=float,default=0.005)
    p.add_argument('--include-bunny',action='store_true',help='Add official Stanford Bunny reconstructed geometry to procedural shapes')
    p.add_argument('--bunny-only',action='store_true',help='Evaluate only the official Stanford Bunny reconstruction (already bundled)')
    p.add_argument('--output',default='results/3d',help='Relative output folder inside project')
    return p.parse_args(argv)


def main(argv=None):
    args=parse_args(argv)
    if not (30<=args.points<=5000 and 1<=args.trials<=1000 and 1<=args.iterations<=200):
        raise ValueError('Invalid experiment sizes')
    if not (0.5<=args.overlap<=1): raise ValueError('overlap must be between 0.5 and 1')
    rates=[float(x) for x in args.outliers.split(',')]
    if not rates or any(not 0<=x<0.8 for x in rates): raise ValueError('Invalid outlier rates')
    output=(PROJECT_ROOT/args.output).resolve()
    if PROJECT_ROOT not in output.parents: raise ValueError('output must be inside project root')
    output.mkdir(parents=True,exist_ok=True)
    cloud_files=[] if args.bunny_only else ensure_procedural_datasets(DATA_DIR)
    if args.include_bunny or args.bunny_only:
        bunny=DATA_DIR/'bun_zipper.ply'
        if not bunny.exists(): raise FileNotFoundError('Bunny PLY missing. Run: python prepare_3d_data.py --download-bunny')
        cloud_files.append(bunny)
    input_config={**vars(args),'datasets':[f.name for f in cloud_files],
                  'normalisation':'centred; longest bbox side = 1 unit',
                  'data_provenance':{'bun_zipper.ply':'real Stanford Bunny geometry from Cyberware optical scan; reconstructed zipper PLY; source registration and corruption are synthetically generated',
                                     'other':'procedurally generated non-planar surfaces'},
                  'scan_alignment_note':'This benchmark registers a synthetic rigid transformation of points sampled from a single real reconstructed mesh, not two independent real sensor scans.'}
    (output/'config.json').write_text(json.dumps(input_config,indent=2)+'\n')
    all_rows=[]
    for shape_idx,cloudpath in enumerate(cloud_files):
        cloud=normalize_cloud(load_ply_xyz(cloudpath))
        rng=np.random.default_rng(args.seed+10_000*shape_idx)
        points=cloud[rng.choice(len(cloud),size=args.points,replace=False)]
        shape=cloudpath.stem
        print(f'3D object: {shape}, sampled points: {len(points)}',flush=True)
        for r_idx,outlier in enumerate(rates):
            for trial in range(args.trials):
                seed=args.seed+shape_idx*10_000+r_idx*1000+trial
                case=build_case(points,seed,outlier_rate=outlier,
                                overlap=args.overlap,noise_std=args.noise)
                result, aligned, histories=run_trial(case,iterations=args.iterations)
                for row in result:
                    all_rows.append({'shape':shape,'seed':seed,'trial':trial,
                        'outlier_rate':outlier,'overlap':args.overlap,'sampled_target_points':len(points),
                        'source_points':len(case['source']),**row})
                print(f'  outliers={outlier:.0%} trial={trial+1}/{args.trials}: '+
                      ', '.join(f'{x["method"].split(" (")[0]} {x["direct_inlier_rmse"]:.3f}' for x in result),flush=True)
                if trial==0:
                    name=f'{shape}_{int(outlier*100)}pct'
                    plot_3d_registration(case,aligned,output/'figures'/f'{name}_registration.png',
                                         f'3D {shape} registration ({outlier:.0%} outliers)')
                    plot_convergence(histories,output/'figures'/f'{name}_convergence.png',
                                     f'{shape}: common metric convergence')
    summary=summarize(all_rows)
    save_csv(output/'trials.csv',all_rows)
    save_csv(output/'summary.csv',summary)
    create_markdown(summary,output/'3d_results_table.md')
    print('Saved:',output, 'with',len(all_rows),'method results',flush=True)
    return summary

if __name__=='__main__': main()
