"""
Wrapper for GETTING_STARTED placed in scripts/ to keep root clean
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from GETTING_STARTED import *

if __name__ == '__main__':
    # call main function in original
    # The original GETTING_STARTED prints when executed directly
    import GETTING_STARTED as gs
    gs.print_header()
    gs.print_checklist()
    gs.print_quick_commands()
    gs.print_keyboard_controls()
    gs.print_file_guide()
    gs.print_troubleshooting()
    gs.print_next_steps()
    gs.print_final_message()
    response = input("Ready to start? (y/n): ").lower().strip()
    if response == 'y':
        print("\n✅ Run 'python main.py' to start the game!")
    else:
        print("\n📚 Read the documentation files to get started!")
