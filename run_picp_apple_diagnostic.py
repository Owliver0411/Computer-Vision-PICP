"""Paired Apple sensitivity study. Run from anywhere: python run_picp_apple_diagnostic.py.

No test-set hyperparameter optimization: the complete grid is reported.
This script does NOT change the declared baseline in code/main.py.
"""
from __future__ import annotations
import csv
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'code'))
import main as picp

OUT = ROOT / 'results' / 'diagnostics'
LAMBDAS = (1.1, 1.4, 1.8, 2.0)
SCALES = (0.05, 0.20, 0.50)
TRIALS = 10
POINTS = 300
ITERATIONS = 60
SEED_BASE = 20261105


def csv_write(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)


def mean_sd(vals):
    x = np.asarray(vals, dtype=float)
    return float(x.mean()), float(x.std(ddof=1))


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    model = picp.load_shape_points('apple-1.gif', POINTS)
    rows = []
    for trial in range(TRIALS):
        seed = SEED_BASE + trial
        source, outlier_mask, _, _ = picp.make_synthetic_case(model, seed)
        icp_aligned, _ = picp.run_icp(source, model, max_iterations=ITERATIONS)
        icp = picp.evaluate_result(icp_aligned, model, outlier_mask)
        for lam in LAMBDAS:
            for scale in SCALES:
                aligned, common_hist, weighted_hist, p = picp.run_picp(
                    source, model, max_iterations=ITERATIONS,
                    lambda_anneal=lam, initial_variance_scale=scale)
                m = picp.evaluate_result(aligned, model, outlier_mask)
                rows.append({
                    'Trial': trial+1, 'Seed': seed, 'N': len(model),
                    'Outliers': int(outlier_mask.sum()), 'Lambda': lam,
                    'InitialVarianceScale': scale,
                    'ICP_AllNN': icp['NN_RMSE_All'],
                    'ICP_DirectInlier': icp['Direct_RMSE_Inliers'],
                    'PICP_AllNN': m['NN_RMSE_All'],
                    'PICP_InlierNN': m['NN_RMSE_Inliers'],
                    'PICP_DirectInlier': m['Direct_RMSE_Inliers'],
                    'PICP_WeightedRMS': weighted_hist[-1],
                    'PICP_ESS': float(1/np.sum(p**2)),
                    'PICP_MaxProbability': float(p.max()),
                    'PICP_Iterations': len(weighted_hist),
                    'Delta_DirectInlier_PICP_minus_ICP': m['Direct_RMSE_Inliers']-icp['Direct_RMSE_Inliers'],
                })
        print(f'Apple paired trial {trial+1}/{TRIALS} complete', flush=True)
    csv_write(OUT/'apple_parameter_trials.csv', rows)
    summary=[]
    for lam in LAMBDAS:
        for scale in SCALES:
            group=[r for r in rows if r['Lambda']==lam and r['InitialVarianceScale']==scale]
            record={'Lambda':lam, 'InitialVarianceScale':scale, 'Trials':len(group)}
            for col in ('ICP_AllNN','ICP_DirectInlier','PICP_AllNN','PICP_InlierNN',
                        'PICP_DirectInlier','PICP_WeightedRMS','PICP_ESS',
                        'PICP_MaxProbability','PICP_Iterations','Delta_DirectInlier_PICP_minus_ICP'):
                record[col+'_Mean'],record[col+'_SD']=mean_sd([r[col] for r in group])
            record['PICP_better_DirectInlier_trials']=sum(r['Delta_DirectInlier_PICP_minus_ICP']<0 for r in group)
            summary.append(record)
    csv_write(OUT/'apple_parameter_summary.csv',summary)

    # Predeclared reference = baseline config, not selected by minimum score.
    ref=next(x for x in summary if x['Lambda']==1.4 and x['InitialVarianceScale']==0.2)
    ranked=sorted(summary,key=lambda x:x['PICP_DirectInlier_Mean'])
    headers=['lambda','variance scale','PICP direct inlier','ICP direct inlier','PICP all NN','ESS','PICP better / 10']
    table=['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']
    for x in summary:
        table.append(f"| {x['Lambda']:.1f} | {x['InitialVarianceScale']:.2f} | "
                     f"{x['PICP_DirectInlier_Mean']:.3f} ± {x['PICP_DirectInlier_SD']:.3f} | "
                     f"{x['ICP_DirectInlier_Mean']:.3f} ± {x['ICP_DirectInlier_SD']:.3f} | "
                     f"{x['PICP_AllNN_Mean']:.3f} | {x['PICP_ESS_Mean']:.1f} | "
                     f"{x['PICP_better_DirectInlier_trials']} |")
    discussion=f'''# Apple sensitivity diagnosis (paired, n={TRIALS} seeds)

**Setup.** {POINTS} contour points; identical source/model pairs and random seeds for each
configuration; 15-degree initial rotation, (12,-8) translation, Gaussian noise
standard deviation 0.4 pixels, and a structured corrupted patch. The PICP
algorithm starts with identity rotation and zero translation. Each run allows
up to {ITERATIONS} iterations. Source-index correspondence is known because the
source is generated from the model, so **direct inlier RMSE** is the more
informative measure of recovered registration than nearest-neighbour RMSE.

**Paper consistency.** Equation (8) specifies one nearest model point for each
source point; it does not enforce unique target matches across all sources.
The KD-tree nearest-neighbour implementation follows that equation. PICP uses
uniform initial point probabilities, probability-weighted SVD, and variance
annealing with lambda in (1,2]. The initial variance scale is an implementation
choice, not a numerical setting documented by the paper.

**Predeclared project baseline:** lambda=1.4, initial variance scale=0.20.
For that setting mean PICP direct inlier RMSE =
{ref['PICP_DirectInlier_Mean']:.3f} ± {ref['PICP_DirectInlier_SD']:.3f} pixels,
versus ICP = {ref['ICP_DirectInlier_Mean']:.3f} ± {ref['ICP_DirectInlier_SD']:.3f}
pixels. Mean PICP ESS is {ref['PICP_ESS_Mean']:.1f} / {POINTS} points.

**Sensitivity overview:** Across 12 examined configurations, PICP direct inlier
RMSE means span {min(s['PICP_DirectInlier_Mean'] for s in summary):.3f} to
{max(s['PICP_DirectInlier_Mean'] for s in summary):.3f} pixels. The numerically
best grid result is lambda={ranked[0]['Lambda']}, scale={ranked[0]['InitialVarianceScale']},
but this is **not** an unbiased held-out test or justification for replacing
the baseline. The complete grid is shown below.

'''+'\n'.join(table)+'''

**Metric interpretation.** PICP probability-weighted RMS is an internal objective,
not directly comparable with ICP common nearest-neighbour RMSE. ESS very near
1 indicates strong probability concentration: a low weighted RMS can be caused
by the algorithm placing almost all weight on one or a few points, rather than
accurately aligning the entire contour.

**Limits.** This examines Apple only, one shape image, one corruption recipe,
and 10 seeds; do not generalize to the entire CE-Shape-1 benchmark or the
paper's original noise distribution. The baseline experiment remains unchanged.
'''
    (OUT/'apple_diagnostic_report.md').write_text(discussion,encoding='utf-8')
    fig,ax=plt.subplots(figsize=(8,5))
    for scale in SCALES:
        sub=[r for r in summary if r['InitialVarianceScale']==scale]
        ax.errorbar([x['Lambda'] for x in sub],
                    [x['PICP_DirectInlier_Mean'] for x in sub],
                    yerr=[x['PICP_DirectInlier_SD'] for x in sub],
                    marker='o',capsize=3,label=f'Variance scale {scale}')
    ax.axhline(ref['ICP_DirectInlier_Mean'],linestyle='--',label='ICP (mean)')
    ax.set(xlabel='Annealing lambda',ylabel='Direct inlier RMSE (pixels)',
           title='Apple: PICP parameter sensitivity (mean ± SD)')
    ax.grid(alpha=0.25);ax.legend();fig.tight_layout()
    fig.savefig(OUT/'apple_parameter_sensitivity.png',dpi=170);plt.close(fig)
    print('Saved diagnostic trial CSV, summary CSV, report, and figure to',OUT)
    print('BASELINE PICP direct mean %.3f; ICP %.3f; ESS %.1f' %
          (ref['PICP_DirectInlier_Mean'],ref['ICP_DirectInlier_Mean'],ref['PICP_ESS_Mean']))
    return summary

if __name__=='__main__':
    run()
