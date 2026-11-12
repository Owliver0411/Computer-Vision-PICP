import os

# Project root directory 
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(ROOT, 'data')
RESULTS_DIR = os.path.join(ROOT, 'results')
FIGURES_DIR = os.path.join(RESULTS_DIR, 'figures')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

def data_file(*parts):
    return os.path.join(DATA_DIR, *parts)

def result_file(*parts):
    return os.path.join(RESULTS_DIR, *parts)