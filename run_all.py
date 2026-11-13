
"""Windows-friendly single-command runner for 2D + 3D + tables."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

experiments = [
    ('code/main.py',),

    ('run_picp_3d.py',),

    ('run_picp_3d.py', '--bunny-only',
     '--output', 'results/3d_bunny'),

    ('run_picp_3d.py', '--overlap', '0.75',
     '--outliers', '0.30',
     '--output', 'results/3d_partial'),

    ('run_picp_3d.py', '--bunny-only',
     '--overlap', '0.75',
     '--outliers', '0.30',
     '--output', 'results/3d_bunny_partial'),

    ('generate_picp_tables.py',),
]

for args in experiments:
    print('Running:', ' '.join(args), flush=True)
    subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        check=True
    )

print('All main experiments complete.')
