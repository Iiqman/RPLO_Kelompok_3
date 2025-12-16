"""
Wrapper view_lessons placed in scripts/ and made robust to imports
"""
import sys
from pathlib import Path
# ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from view_lessons import *

if __name__ == '__main__':
    display_all_lessons()
