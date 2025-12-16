"""
Wrapper run script in scripts/ that defers to root run.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from run import *

if __name__ == '__main__':
    check_and_install_libraries()
    input('\nTekan Enter untuk memulai aplikasi...')
    run_application()
