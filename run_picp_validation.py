"""Independent-seed follow-up for Apple sweep, across Apple/Cup/Children.

This is exploratory confirmation, not a blinded test: the lambda/scale setting
was found in the Apple sweep. The original baseline remains in main.py.
"""
import csv
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'code'))
import main as picp
OUT=ROOT/'results'/'diagnostics'
OUT.mkdir(parents=True, exist_ok=True)
PARAMETERS=[('Baseline',1.4,0.20),('Apple-sweep candidate',1.1,0.05)]
N=300
TRIALS=10


def write(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def run():
    rows=[]
    for shape_idx,(shape,file) in enumerate(picp.TEST_SHAPES):
        model=picp.load_shape_points(file,N)
        for trial in range(TRIALS):
            seed=20270101+100*shape_idx+trial # disjoint from sweep
            source,mask,_,_=picp.make_synthetic_case(model,seed)
            icp,_=picp.run_icp(source,model,max_iterations=60)
            im=picp.evaluate_result(icp,model,mask)
            rows.append({'Shape':shape,'Trial':trial+1,'Seed':seed,
                         'Method':'ICP','Lambda':'','InitialVarianceScale':'',
                         'NN_All':im['NN_RMSE_All'],'Direct_Inlier':im['Direct_RMSE_Inliers'],
                         'ESS':'','Iterations':''})
            for label,lam,scale in PARAMETERS:
                aligned,_,wh,p=picp.run_picp(source,model,max_iterations=60,
                                lambda_anneal=lam,initial_variance_scale=scale)
                metrics=picp.evaluate_result(aligned,model,mask)
                rows.append({'Shape':shape,'Trial':trial+1,'Seed':seed,
                             'Method':'PICP '+label,'Lambda':lam,'InitialVarianceScale':scale,
                             'NN_All':metrics['NN_RMSE_All'],
                             'Direct_Inlier':metrics['Direct_RMSE_Inliers'],
                             'ESS':float(1/np.sum(p**2)), 'Iterations':len(wh)})
        print('Validation finished',shape,flush=True)
    write(OUT/'independent_seed_validation_trials.csv',rows)
    sums=[]
    for shape,_ in picp.TEST_SHAPES:
        for method in ('ICP','PICP Baseline','PICP Apple-sweep candidate'):
            group=[r for r in rows if r['Shape']==shape and r['Method']==method]
            s={'Shape':shape,'Method':method,'N':len(group)}
            for metric in ('NN_All','Direct_Inlier'):
                v=np.array([r[metric] for r in group],dtype=float)
                s[metric+'_mean']=float(v.mean());s[metric+'_SD']=float(v.std(ddof=1))
            if method!='ICP':
                s['ESS_mean']=float(np.mean([r['ESS'] for r in group]))
            else:s['ESS_mean']=''
            sums.append(s)
    write(OUT/'independent_seed_validation_summary.csv',sums)
    table=['| Shape | Method | Direct inlier RMSE | All NN-RMSE | ESS |',
           '|---|---|---:|---:|---:|']
    for s in sums:
        ess='n/a' if s['ESS_mean']=='' else f"{s['ESS_mean']:.1f}"
        table.append(f"| {s['Shape']} | {s['Method']} | {s['Direct_Inlier_mean']:.3f} ± {s['Direct_Inlier_SD']:.3f} | {s['NN_All_mean']:.3f} ± {s['NN_All_SD']:.3f} | {ess} |")
    (OUT/'independent_seed_validation_report.md').write_text(
        '# Independent-seed exploratory validation\n\n'+
        'Ten previously unused seeds for each of Apple, Cup and Children at 300 points; '+
        'the data generator and 15-degree/(12,-8) synthetic pose remain unchanged. '+
        'These are independent cases, **not** blind preregistered model selection. '+
        'PICP baseline is lambda 1.4, initial variance scale 0.20; the '+
        'candidate lambda 1.1/scale 0.05 was selected for examination following the Apple sweep. '+
        'ICP is evaluated on exactly the same cases. Lower RMSE is better.\n\n'+
        '\n'.join(table)+'\n\nThe candidate is a documented sensitivity variant, '+
        'not asserted to be the paper-author-recommended hyperparameters. '
        'The original project baseline remains unchanged.\n',encoding='utf-8')
    print('\n'.join(table))
    return sums

if __name__=='__main__':run()
