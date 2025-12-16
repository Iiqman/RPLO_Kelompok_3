#!/usr/bin/env python3
"""
GETTING STARTED CHECKLIST
Interactive checklist untuk memulai Magic Hands English Learning
Run this file: python GETTING_STARTED.py
"""

def print_header():
    print("""
╔════════════════════════════════════════════════════════════╗
║    🎮 MAGIC HANDS ENGLISH LEARNING - GETTING STARTED      ║
╚════════════════════════════════════════════════════════════╝
    """)

def print_checklist():
    """Print interactive checklist"""
    
    checklist = [
        {
            'step': 1,
            'title': 'Install Dependencies',
            'command': 'pip install opencv-python cvzone numpy',
            'time': '~2 min',
            'status': '⭐'
        },
        {
            'step': 2,
            'title': 'Verify Installation',
            'command': 'python view_lessons.py',
            'time': '~10 sec',
            'status': '⭐'
        },
        {
            'step': 3,
            'title': 'Start Game',
            'command': 'python main.py',
            'time': 'unlimited!',
            'status': '🎮'
        },
        {
            'step': 4,
            'title': 'Read Documentation',
            'command': 'Open: INDEX.md or START_HERE.md',
            'time': '~15 min',
            'status': '📖'
        },
        {
            'step': 5,
            'title': 'Add Custom Lesson',
            'command': 'Edit database.py (see DATABASE_DOCS.md)',
            'time': '~20 min',
            'status': '🔧'
        }
    ]
    
    print("\n" + "="*60)
    print("GETTING STARTED CHECKLIST")
    print("="*60 + "\n")
    
    for item in checklist:
        print(f"[Step {item['step']}] {item['title']}")
        print(f"   {item['status']} Command: {item['command']}")
        print(f"   ⏱️  Time: {item['time']}")
        print()

def print_quick_commands():
    print("\n" + "="*60)
    print("QUICK COMMANDS")
    print("="*60 + "\n")
    
    commands = {
        'Start Game': 'python main.py',
        'View Database': 'python view_lessons.py',
        'Auto Setup': 'python run.py',
        'Install Libraries': 'pip install opencv-python cvzone numpy'
    }
    
    for desc, cmd in commands.items():
        print(f"  {desc:20} → {cmd}")
    print()

def print_keyboard_controls():
    print("\n" + "="*60)
    print("KEYBOARD CONTROLS (while playing)")
    print("="*60 + "\n")
    
    controls = {
        'Q': 'Quit Game',
        'R': 'Reset Lesson',
        'N': 'Next Lesson',
        'P': 'Previous Lesson'
    }
    
    for key, desc in controls.items():
        print(f"  [{key}] → {desc}")
    print()

def print_file_guide():
    print("\n" + "="*60)
    print("WHICH FILE TO READ?")
    print("="*60 + "\n")
    
    guides = {
        'INDEX.md': 'Navigation hub for all documentation',
        'START_HERE.md': 'Visual guide with quick reference',
        'QUICKSTART.md': 'Fast setup guide (5 minutes)',
        'README.md': 'Full documentation',
        'DATABASE_DOCS.md': 'How to add new lessons',
        'LESSON_TEMPLATE.py': 'Copy-paste template for new lesson'
    }
    
    print("  📖 For Documentation:")
    for file, desc in guides.items():
        print(f"     • {file:25} - {desc}")
    print()

def print_troubleshooting():
    print("\n" + "="*60)
    print("QUICK TROUBLESHOOTING")
    print("="*60 + "\n")
    
    issues = {
        'ModuleNotFoundError (cvzone)': 'pip install cvzone',
        'ModuleNotFoundError (cv2)': 'pip install opencv-python',
        'Camera not detected': 'Check USB connection, test with Camera app',
        'Hand not detected': 'Ensure good lighting, make a fist to grab',
        'Block not moving': 'Update hand position, check lighting'
    }
    
    print("  ⚠️  Common Issues:")
    for issue, solution in issues.items():
        print(f"     • {issue}")
        print(f"       Fix: {solution}\n")

def print_next_steps():
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60 + "\n")
    
    print("""
  OPTION A: Just Want to Play?
  ├─ Run: python main.py
  └─ Press N/P to switch lessons
  
  OPTION B: Want to Learn More?
  ├─ Read: INDEX.md
  └─ Follow documentation links
  
  OPTION C: Want to Create Custom Lesson?
  ├─ Read: DATABASE_DOCS.md
  ├─ Check: LESSON_TEMPLATE.py
  └─ Edit: database.py
  
  OPTION D: Got Questions?
  ├─ Check: QUICKSTART.md (FAQ section)
  └─ Read: README.md (full guide)

""")

def print_final_message():
    print("\n" + "="*60)
    print("🎉 YOU'RE ALL SET!")
    print("="*60 + "\n")
    
    print("""
  Everything is ready to use!
  
  Quick Start:
  1. python main.py          (start playing)
  2. Press N/P               (switch lessons)
  3. Press Q                 (quit)
  
  Happy Learning! 🚀
  
  For more info: Open INDEX.md or START_HERE.md
  
""")

if __name__ == "__main__":
    print_header()
    print_checklist()
    print_quick_commands()
    print_keyboard_controls()
    print_file_guide()
    print_troubleshooting()
    print_next_steps()
    print_final_message()
    
    # Optional: Ask user if they want to proceed
    print("\n" + "="*60)
    response = input("Ready to start? (y/n): ").lower().strip()
    
    if response == 'y':
        print("\n✅ Run 'python main.py' to start the game!")
        print("📖 For help, read 'INDEX.md' or 'START_HERE.md'\n")
    else:
        print("\n📚 Read the documentation files to get started!")
        print("🎯 Start with: INDEX.md or QUICKSTART.md\n")
