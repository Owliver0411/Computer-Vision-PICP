"""Benchmark one 2D case and/or one 3D case, once per algorithm.

Run from project root: python benchmark_single_case.py
Optional: python benchmark_single_case.py --mode 3d
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from time import perf_counter

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'code'))

from main import (load_shape_points, make_synthetic_case, run_icp,
                  run_soft_em_icp, run_picp, evaluate_result)
from experiment_3d import (build_case, run_trial, plot_3d_registration)
from three_d_data import load_ply_xyz, normalize_cloud

OUT = ROOT / 'results' / 'single_case_benchmark'


def save_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run_2d(gif_name='apple-1.gif', points=300, seed=42):
    target = load_shape_points(gif_name, num_points=points)
    source, outliers, _, _ = make_synthetic_case(target, seed=seed)
    cases = [
        ('ICP', lambda: (*run_icp(source, target, max_iterations=40), None, None)),
        ('Soft-EM-ICP (simplified)', lambda: (*run_soft_em_icp(
            source, target, max_iterations=40), None, None)),
        ('PICP (original)', lambda: run_picp(
            source, target, max_iterations=40, lambda_anneal=1.4,
            initial_variance_scale=0.20)),
        ('PICP (slow annealing)', lambda: run_picp(
            source, target, max_iterations=40, lambda_anneal=1.1,
            initial_variance_scale=0.05)),
    ]
    rows = []
    clouds = {}
    for name, fn in cases:
        start = perf_counter()
        aligned, history, weighted_history, weights = fn()
        runtime = perf_counter() - start
        m = evaluate_result(aligned, target, outliers)
        rows.append({
            'dimension': '2D', 'object': gif_name, 'method': name,
            'target_points': len(target), 'source_points': len(source),
            'inliers': int((~outliers).sum()), 'outliers': int(outliers.sum()),
            'runtime_s': runtime, 'iterations': len(history),
            'all_point_NN_RMSE': m['NN_RMSE_All'],
            'direct_inlier_RMSE': m['Direct_RMSE_Inliers'],
            'weighted_RMS_PICP_only': (weighted_history[-1] if weighted_history else float('nan')),
        })
        clouds[name] = aligned

    fig, axs = plt.subplots(2, 2, figsize=(11, 10))
    for ax, (name, aligned) in zip(axs.flat, clouds.items()):
        ax.scatter(target[:, 0], target[:, 1], s=4, label='Target', alpha=.5)
        ax.scatter(aligned[:, 0], aligned[:, 1], s=4, label='Aligned', alpha=.5)
        ax.set_title(name)
        ax.set_aspect('equal', adjustable='box')
    axs.flat[0].legend()
    fig.suptitle(f'Single-case 2D registration: {gif_name}')
    fig.tight_layout()
    fig.savefig(OUT / '2d_registration.png', dpi=140)
    plt.close(fig)
    return rows


def run_3d(object_name='bun_zipper.ply', points=350, seed=42):
    path = ROOT / 'data' / '3d' / object_name
    if not path.is_file():
        raise FileNotFoundError(f'Missing 3D dataset: {path}')
    cloud = normalize_cloud(load_ply_xyz(path))
    rng = np.random.default_rng(seed + 10000)
    target = cloud[rng.choice(len(cloud), size=points, replace=False)]
    case = build_case(target, seed=seed, outlier_rate=.30, overlap=1.0)
    # The established 3D runner times only the registration algorithms,
    # not data loading, figure saving, or evaluation.
    metrics, aligned, _ = run_trial(case, iterations=40)
    rows = []
    for m in metrics:
        rows.append({
            'dimension': '3D', 'object': object_name, 'method': m['method'],
            'target_points': len(target), 'source_points': len(case['source']),
            'inliers': m['inlier_count'], 'outliers': m['outlier_count'],
            'runtime_s': m['runtime_s'], 'iterations': m['iterations'],
            'all_point_NN_RMSE': m['nn_all_rmse'],
            'direct_inlier_RMSE': m['direct_inlier_rmse'],
            'weighted_RMS_PICP_only': m['picp_weighted_rms'],
        })
    plot_3d_registration(case, aligned, OUT / '3d_registration.png',
                         f'Single-case 3D registration: {object_name}')
    return rows


def main():
    parser = argparse.ArgumentParser(description='One input per algorithm, 2D and/or 3D')
    parser.add_argument('--mode', choices=['2d', '3d', 'both'], default='both')
    parser.add_argument('--shape', default='apple-1.gif', help='GIF in data/ (2D)')
    parser.add_argument('--object', default='bun_zipper.ply', help='PLY in data/3d/ (3D)')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    if args.mode in ('2d', 'both'):
        rows += run_2d(args.shape, seed=args.seed)
    if args.mode in ('3d', 'both'):
        rows += run_3d(args.object, seed=args.seed)
    save_csv(OUT / 'single_case_results.csv', rows)
    for row in rows:
        print(f"{row['dimension']:2} | {row['method']:<26} | "
              f"{row['runtime_s']:.4f} s | "
              f"direct inlier RMSE={row['direct_inlier_RMSE']:.4f} | "
              f"all-point NN-RMSE={row['all_point_NN_RMSE']:.4f}")
    print(f'\nSaved: {OUT / "single_case_results.csv"}')
    print('This is a single-run demonstration, not a stable speed ranking.')
    print('2D RMSE uses pixels; 3D RMSE uses normalized object units. Do not compare them directly.')


if __name__ == '__main__':
    main()
