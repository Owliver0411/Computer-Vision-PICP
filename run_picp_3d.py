"""Run the 3D extension from project root (see --help)."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'code'))
from experiment_3d import main
if __name__=='__main__': main()
