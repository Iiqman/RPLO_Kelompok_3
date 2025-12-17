import cv2
import mediapipe as mp
import numpy as np
import math
import json
import random
import time
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

@dataclass
class QuizQuestion:
    """Data class untuk soal quiz"""
    question: str
    words: List[str]
    correct_answer: List[str]
    category: str
    difficulty: str

class Button:
    """Class untuk button/word card yang bisa diklik - MODERN STYLE"""
    def __init__(self, x, y, width, height, text, id=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.id = id
        self.hovered = False
        self.selected = False
        
    def contains_point(self, x, y):
        """Check if point is inside button"""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
    
    def draw(self, frame, color=None):
        """Draw button with modern style"""
        if color is None:
            if self.selected:
                color = (80, 180, 80)  # Green when selected
            elif self.hovered:
                color = (100, 150, 255)  # Light blue when hovered
            else:
                color = (60, 60, 60)  # Dark gray default
        
        # Shadow effect
        shadow_offset = 4
        cv2.rectangle(frame, 
                     (self.x + shadow_offset, self.y + shadow_offset), 
                     (self.x + self.width + shadow_offset, self.y + self.height + shadow_offset), 
                     (20, 20, 20), -1)
        
        # Draw button background with rounded effect
        cv2.rectangle(frame, (self.x, self.y), 
                      (self.x + self.width, self.y + self.height), 
                      color, -1)
        
        # Draw border - modern accent
        if self.selected:
            border_color = (120, 255, 120)
            thickness = 3
        elif self.hovered:
            border_color = (150, 200, 255)
            thickness = 3
        else:
            border_color = (100, 100, 100)
            thickness = 2
            
        cv2.rectangle(frame, (self.x, self.y), 
                      (self.x + self.width, self.y + self.height), 
                      border_color, thickness)
        
        # Draw text centered - modern font
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 0.8
        thickness = 2
        text_size = cv2.getTextSize(self.text, font, font_scale, thickness)[0]
        text_x = self.x + (self.width - text_size[0]) // 2
        text_y = self.y + (self.height + text_size[1]) // 2
        
        # Text shadow
        cv2.putText(frame, self.text, (text_x + 2, text_y + 2), 
                    font, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)
        # Main text
        cv2.putText(frame, self.text, (text_x, text_y), 
                    font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

class QuizGame:
    def __init__(self):
        self.state = "MENU"  # MENU, DIFFICULTY, QUIZ, RESULT
        self.quiz_data = {}
        self.current_category = None
        self.current_difficulty = None
        self.current_question = None
        self.available_words = []
        self.answer_sequence = []
        self.buttons = []
        self.answer_buttons = []
        self.score = 0
        self.total_questions = 0
        self.start_time = 0
        self.time_limit = 0
        
        # Hand tracking
        self.finger_pos = None
        self.is_pinching = False
        self.last_pinch = False
        self.pinch_cooldown = 0
        
        # Modern font
        self.font = cv2.FONT_HERSHEY_DUPLEX
        
        # Load quiz data
        self.load_quiz_data()
        
    def load_quiz_data(self):
        """Load quiz data from JSON file"""
        try:
            json_path = Path(__file__).parent / "quiz_data.json"
            
            if not json_path.exists():
                print("[!] quiz_data.json not found!")
                print("[!] Please create quiz_data.json file")
                # Create empty structure
                self.quiz_data = {
                    "Present": {"easy": [], "medium": [], "hard": []},
                    "Past": {"easy": [], "medium": [], "hard": []},
                    "Future": {"easy": [], "medium": [], "hard": []},
                    "Past Future": {"easy": [], "medium": [], "hard": []}
                }
                # Save it
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(self.quiz_data, f, indent=2, ensure_ascii=False)
                print("[OK] Created empty quiz_data.json")
                return
            
            with open(json_path, 'r', encoding='utf-8') as f:
                self.quiz_data = json.load(f)
            
            print(f"[OK] Loaded quiz data: {len(self.quiz_data)} categories")
            
        except Exception as e:
            print(f"[X] Error loading quiz data: {e}")
            self.quiz_data = {}
    
    def open_quiz_editor(self):
        """Open quiz editor GUI"""
        import subprocess
        import sys
        
        try:
            editor_path = Path(__file__).parent / "quiz_editor.py"
            
            if not editor_path.exists():
                print("[!] Editor not found: quiz_editor.py")
                print("[!] Please make sure quiz_editor.py exists in the same folder")
                return
            
            # Run editor as separate process with "sentence" mode
            subprocess.Popen([sys.executable, str(editor_path), "sentence"])
            print("[OK] Opening Sentence Quiz Editor...")
            print("[*] Edit your questions in the editor window")
            print("[*] Press 'r' in this window to reload after editing")
        
        except Exception as e:
            print(f"[X] Error opening editor: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_text_shadow(self, frame, text, pos, font, scale, color, thickness):
        """Draw text with shadow for better visibility"""
        x, y = pos
        # Shadow
        cv2.putText(frame, text, (x+3, y+3), font, scale, (0, 0, 0), thickness+1, cv2.LINE_AA)
        # Main text
        cv2.putText(frame, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)
    
    def setup_menu(self):
        """Setup main menu buttons"""
        self.state = "MENU"
        self.buttons = []
        
        categories = ["Present", "Past", "Future", "Past Future"]
        button_width = 280
        button_height = 90
        spacing = 25
        start_y = 300
        
        # Category buttons - centered
        for i, category in enumerate(categories):
            x = 960 - button_width // 2  # Center for 1920
            y = start_y + i * (button_height + spacing)
            self.buttons.append(Button(x, y, button_width, button_height, category, category))
        
        # Edit Quiz button - bottom center
        edit_btn_width = 320
        edit_x = 960 - edit_btn_width // 2
        self.buttons.append(Button(edit_x, 880, edit_btn_width, 70, "EDIT QUESTIONS", "edit_quiz"))
    
    def setup_difficulty(self):
        """Setup difficulty selection"""
        self.state = "DIFFICULTY"
        self.buttons = []
        
        difficulties = ["Easy", "Medium", "Hard"]
        
        button_width = 250
        button_height = 100
        spacing = 40
        start_x = 960 - (button_width * 3 + spacing * 2) // 2
        y = 450
        
        for i, diff in enumerate(difficulties):
            x = start_x + i * (button_width + spacing)
            btn = Button(x, y, button_width, button_height, diff, diff.lower())
            self.buttons.append(btn)
        
        # Back button - center bottom
        back_x = 960 - 80
        self.buttons.append(Button(back_x, 880, 160, 60, "Back", "back"))
    
    def start_quiz(self):
        """Start quiz with selected category and difficulty"""
        self.state = "QUIZ"
        self.buttons = []
        self.answer_buttons = []
        self.answer_sequence = []
        
        # Get questions
        questions = self.quiz_data.get(self.current_category, {}).get(self.current_difficulty, [])
        
        if not questions:
            print(f"[!] No questions for {self.current_category} - {self.current_difficulty}")
            self.setup_difficulty()
            return
        
        # Select random question
        question_data = random.choice(questions)
        
        # Setup question
        self.current_question = question_data
        self.available_words = question_data["words"].copy()
        random.shuffle(self.available_words)
        
        # Timer
        self.time_limit = question_data.get("timer", 30)
        self.start_time = time.time()
        
        # Create word buttons
        self.create_word_buttons()
        
        # Create answer area buttons
        self.create_answer_area()
    
    def create_word_buttons(self):
        """Create buttons for available words - CENTERED, RAISED POSITION"""
        button_width = 140
        button_height = 70
        spacing_x = 18
        spacing_y = 18
        words_per_row = 8
        
        # Calculate rows needed
        num_words = len(self.available_words)
        num_rows = (num_words + words_per_row - 1) // words_per_row
        
        start_y = 620  # Raised from 720
        
        for i, word in enumerate(self.available_words):
            row = i // words_per_row
            col = i % words_per_row
            
            # Calculate words in this row
            words_in_row = min(words_per_row, num_words - row * words_per_row)
            
            # Calculate starting x for centering this row
            total_width = words_in_row * button_width + (words_in_row - 1) * spacing_x
            start_x = (1920 - total_width) // 2
            
            x = start_x + col * (button_width + spacing_x)
            y = start_y + row * (button_height + spacing_y)
            
            btn = Button(x, y, button_width, button_height, word, f"word_{i}")
            self.buttons.append(btn)
    
    def create_answer_area(self):
        """Create answer area for selected words"""
        pass
    
    def update_answer_display(self):
        """Update answer buttons based on current sequence"""
        self.answer_buttons = []
        
        button_width = 140
        button_height = 70
        spacing = 15
        start_y = 320  # Raised position
        
        if not self.answer_sequence:
            return
        
        # Calculate total width and center
        total_width = len(self.answer_sequence) * button_width + (len(self.answer_sequence) - 1) * spacing
        start_x = (1920 - total_width) // 2
        
        for i, word in enumerate(self.answer_sequence):
            x = start_x + i * (button_width + spacing)
            btn = Button(x, start_y, button_width, button_height, word, f"answer_{i}")
            self.answer_buttons.append(btn)
    
    def check_answer(self):
        """Check if answer is correct"""
        correct = self.current_question["correct_answer"]
        user_answer = self.answer_sequence
        
        if user_answer == correct:
            self.score += 1
            return True
        return False
    
    def draw_menu(self, frame):
        """Draw main menu - MODERN STYLE"""
        h, w = frame.shape[:2]
        
        # Title - modern
        title = "ENGLISH SENTENCE QUIZ"
        self.draw_text_shadow(frame, title, (960 - 380, 150), 
                             self.font, 1.8, (100, 200, 255), 3)
        
        # Subtitle
        subtitle = "Select Tense Category"
        self.draw_text_shadow(frame, subtitle, (960 - 200, 230), 
                             self.font, 1.0, (200, 200, 200), 2)
        
        # Draw buttons
        for btn in self.buttons:
            if btn.id == "edit_quiz":
                # Special color for edit button
                btn.draw(frame, (150, 100, 255) if btn.hovered else (100, 70, 180))
            else:
                btn.draw(frame)
        
        # Instructions
        self.draw_text_shadow(frame, "Point and PINCH fingers to select", 
                             (50, h - 40), self.font, 0.8, (255, 255, 255), 2)
    
    def draw_difficulty(self, frame):
        """Draw difficulty selection - MODERN STYLE"""
        h, w = frame.shape[:2]
        
        # Title
        title = f"Category: {self.current_category}"
        self.draw_text_shadow(frame, title, (960 - 280, 150), 
                             self.font, 1.5, (100, 255, 100), 3)
        
        # Subtitle
        subtitle = "Select Difficulty"
        self.draw_text_shadow(frame, subtitle, (960 - 180, 280), 
                             self.font, 1.1, (200, 200, 200), 2)
        
        # Draw buttons
        for btn in self.buttons:
            if btn.id == "easy":
                btn.draw(frame, (100, 200, 100) if btn.hovered else (70, 150, 70))
            elif btn.id == "medium":
                btn.draw(frame, (255, 200, 80) if btn.hovered else (200, 150, 60))
            elif btn.id == "hard":
                btn.draw(frame, (255, 120, 120) if btn.hovered else (200, 80, 80))
            else:
                btn.draw(frame)
        
        # Info text - modern layout
        info_lines = [
            "Easy: 3-5 words, 25-30 seconds",
            "Medium: 6-8 words, 35-40 seconds",
            "Hard: 8+ words, 45-50 seconds"
        ]
        
        for i, line in enumerate(info_lines):
            self.draw_text_shadow(frame, line, (960 - 200, 680 + i * 40), 
                                 self.font, 0.7, (180, 180, 180), 1)
    
    def draw_quiz(self, frame):
        """Draw quiz interface - MODERN & MINIMALIST"""
        h, w = frame.shape[:2]
        
        # Timer - top right, modern
        elapsed = time.time() - self.start_time
        remaining = max(0, self.time_limit - int(elapsed))
        
        timer_color = (100, 255, 100) if remaining > 10 else (255, 200, 100) if remaining > 5 else (255, 100, 100)
        
        # Timer background box
        timer_text = f"{remaining}s"
        timer_size = cv2.getTextSize(timer_text, self.font, 1.5, 3)[0]
        timer_box_x = 1750
        timer_box_y = 40
        timer_box_w = 140
        timer_box_h = 80
        
        # Draw timer box with shadow
        cv2.rectangle(frame, (timer_box_x + 4, timer_box_y + 4), 
                     (timer_box_x + timer_box_w + 4, timer_box_y + timer_box_h + 4), 
                     (20, 20, 20), -1)
        cv2.rectangle(frame, (timer_box_x, timer_box_y), 
                     (timer_box_x + timer_box_w, timer_box_y + timer_box_h), 
                     (50, 50, 50), -1)
        cv2.rectangle(frame, (timer_box_x, timer_box_y), 
                     (timer_box_x + timer_box_w, timer_box_y + timer_box_h), 
                     timer_color, 3)
        
        self.draw_text_shadow(frame, timer_text, 
                             (timer_box_x + (timer_box_w - timer_size[0]) // 2, 
                              timer_box_y + (timer_box_h + timer_size[1]) // 2), 
                             self.font, 1.5, timer_color, 3)
        
        # Question - top, modern
        question_text = self.current_question["question"]
        self.draw_text_shadow(frame, f"Q: {question_text}", (50, 80), 
                             self.font, 1.0, (255, 255, 255), 2)
        
        # Category and difficulty - subtle
        self.draw_text_shadow(frame, f"{self.current_category} - {self.current_difficulty.title()}", 
                             (50, 130), self.font, 0.7, (150, 150, 150), 1)
        
        # Answer area label
        self.draw_text_shadow(frame, "Your Answer:", (50, 250), 
                             self.font, 0.9, (100, 200, 255), 2)
        
        # Draw answer buttons
        for btn in self.answer_buttons:
            btn.draw(frame)
        
        # If no answer yet, show placeholder
        if not self.answer_sequence:
            placeholder = "Click words below to build sentence..."
            self.draw_text_shadow(frame, placeholder, (960 - 280, 360), 
                                 self.font, 0.7, (120, 120, 120), 1)
        
        # Available words label
        self.draw_text_shadow(frame, "Available Words (click to add):", (50, 560), 
                             self.font, 0.9, (200, 200, 200), 2)
        
        # Draw word buttons
        for btn in self.buttons:
            btn.draw(frame)
        
        # Submit and Clear buttons - RAISED POSITION, centered
        button_y = 880  # Raised from 980
        button_height = 60
        button_spacing = 35
        
        # Clear button (left)
        clear_width = 160
        submit_width = 180
        total_buttons_width = clear_width + button_spacing + submit_width
        start_x = (1920 - total_buttons_width) // 2
        
        clear_btn = Button(start_x, button_y, clear_width, button_height, "CLEAR", "clear")
        clear_btn.hovered = (self.finger_pos and 
                            clear_btn.contains_point(self.finger_pos[0], self.finger_pos[1]))
        clear_btn.draw(frame, (255, 120, 120) if clear_btn.hovered else (180, 80, 80))
        
        if clear_btn.hovered and self.is_pinching and not self.last_pinch:
            self.answer_sequence = []
            self.update_answer_display()
            # Restore all words
            for btn in self.buttons:
                btn.selected = False
        
        # Submit button (right) - only if answer has words
        if self.answer_sequence:
            submit_btn = Button(start_x + clear_width + button_spacing, button_y, 
                              submit_width, button_height, "SUBMIT", "submit")
            submit_btn.hovered = (self.finger_pos and 
                                 submit_btn.contains_point(self.finger_pos[0], self.finger_pos[1]))
            submit_btn.draw(frame, (120, 255, 120) if submit_btn.hovered else (80, 180, 80))
            
            # Check if submit clicked
            if submit_btn.hovered and self.is_pinching and not self.last_pinch:
                self.finish_quiz()
        
        # Time up check
        if remaining <= 0:
            self.finish_quiz()
        
        # Instructions - bottom
        self.draw_text_shadow(frame, "Pinch to select | Click answer to remove | SUBMIT when done", 
                             (50, h - 40), self.font, 0.7, (255, 255, 255), 1)
    
    def draw_result(self, frame):
        """Draw result screen - MODERN"""
        h, w = frame.shape[:2]
        
        # Result
        is_correct = self.check_answer()
        result_text = "CORRECT!" if is_correct else "WRONG!"
        result_color = (120, 255, 120) if is_correct else (255, 120, 120)
        
        self.draw_text_shadow(frame, result_text, (960 - 180, 200), 
                             self.font, 2.5, result_color, 4)
        
        # Question
        self.draw_text_shadow(frame, f"Q: {self.current_question['question']}", 
                             (150, 350), self.font, 0.9, (255, 255, 255), 2)
        
        # Your answer
        your_answer = " ".join(self.answer_sequence)
        self.draw_text_shadow(frame, f"Your Answer:", (150, 470), 
                             self.font, 0.8, (200, 200, 200), 1)
        self.draw_text_shadow(frame, your_answer if your_answer else "(empty)", 
                             (150, 530), self.font, 1.1, (255, 255, 150), 2)
        
        # Correct answer
        correct_answer = " ".join(self.current_question["correct_answer"])
        self.draw_text_shadow(frame, f"Correct Answer:", (150, 650), 
                             self.font, 0.8, (200, 200, 200), 1)
        self.draw_text_shadow(frame, correct_answer, 
                             (150, 710), self.font, 1.1, (120, 255, 120), 2)
        
        # Buttons - CENTERED
        button_y = 850
        button_width = 220
        button_height = 80
        button_spacing = 40
        
        total_width = button_width * 2 + button_spacing
        start_x = (1920 - total_width) // 2
        
        next_btn = Button(start_x, button_y, button_width, button_height, "NEXT", "next")
        menu_btn = Button(start_x + button_width + button_spacing, button_y, 
                         button_width, button_height, "MENU", "menu")
        
        for btn in [next_btn, menu_btn]:
            btn.hovered = (self.finger_pos and 
                          btn.contains_point(self.finger_pos[0], self.finger_pos[1]))
            btn.draw(frame)
            
            if btn.hovered and self.is_pinching and not self.last_pinch:
                if btn.id == "next":
                    self.start_quiz()
                elif btn.id == "menu":
                    self.setup_menu()
    
    def finish_quiz(self):
        """Finish current quiz"""
        self.state = "RESULT"
    
    def update(self, frame):
        """Main update loop"""
        # Update button hovers
        if self.finger_pos:
            x, y = self.finger_pos
            
            # Update main buttons
            for btn in self.buttons:
                btn.hovered = btn.contains_point(x, y)
                
                # Handle click
                if btn.hovered and self.is_pinching and not self.last_pinch and self.pinch_cooldown <= 0:
                    self.handle_button_click(btn)
                    self.pinch_cooldown = 15  # Cooldown frames
        
        # Update pinch cooldown
        if self.pinch_cooldown > 0:
            self.pinch_cooldown -= 1
        
        # Draw based on state
        if self.state == "MENU":
            self.draw_menu(frame)
        elif self.state == "DIFFICULTY":
            self.draw_difficulty(frame)
        elif self.state == "QUIZ":
            self.draw_quiz(frame)
        elif self.state == "RESULT":
            self.draw_result(frame)
        
        # Draw finger pointer - modern style
        if self.finger_pos:
            x, y = self.finger_pos
            if self.is_pinching:
                # Pinching - smaller, bright
                cv2.circle(frame, (x, y), 14, (100, 255, 255), -1, cv2.LINE_AA)
                cv2.circle(frame, (x, y), 18, (150, 255, 255), 3, cv2.LINE_AA)
            else:
                # Pointing - larger, subtle
                cv2.circle(frame, (x, y), 10, (255, 150, 150), -1, cv2.LINE_AA)
                cv2.circle(frame, (x, y), 15, (255, 200, 200), 2, cv2.LINE_AA)
    
    def handle_button_click(self, btn):
        """Handle button click"""
        if self.state == "MENU":
            if btn.id == "edit_quiz":
                self.open_quiz_editor()
            else:
                self.current_category = btn.id
                self.setup_difficulty()
        
        elif self.state == "DIFFICULTY":
            if btn.id == "back":
                self.setup_menu()
            else:
                self.current_difficulty = btn.id
                self.start_quiz()
        
        elif self.state == "QUIZ":
            if btn.id.startswith("word_"):
                # Select word
                if not btn.selected:
                    self.answer_sequence.append(btn.text)
                    btn.selected = True
                    self.update_answer_display()
            elif btn.id.startswith("answer_"):
                # Remove word from answer
                idx = int(btn.id.split("_")[1])
                removed_word = self.answer_sequence.pop(idx)
                # Unselect the word button
                for word_btn in self.buttons:
                    if word_btn.text == removed_word and word_btn.selected:
                        word_btn.selected = False
                        break
                self.update_answer_display()

def main():
    print("\n" + "=" * 70)
    print("[*] ENGLISH SENTENCE QUIZ - Starting Application (1920x1080)")
    print("=" * 70)
    
    # Test camera
    print("[*] Testing camera access...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[X] ERROR: Cannot access camera!")
        return
    
    print("[OK] Camera accessed successfully!")
    
    # Set camera properties to 1920x1080
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Initialize game
    print("[*] Initializing quiz game...")
    game = QuizGame()
    game.setup_menu()
    print("[OK] Quiz game initialized!")
    
    # Create window - windowed fullscreen
    window_name = "English Sentence Quiz - 1920x1080"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1920, 1080)
    
    print("\n[*] Starting main loop...")
    print("[*] Press 'r' to reload quiz data after editing")
    print("=" * 70 + "\n")
    
    try:
        with mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        ) as hands:
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame = cv2.flip(frame, 1)
                h, w, c = frame.shape
                
                # Process hand
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)
                
                game.finger_pos = None
                game.last_pinch = game.is_pinching
                game.is_pinching = False
                
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    
                    # Get index finger tip
                    index_tip = hand_landmarks.landmark[8]
                    thumb_tip = hand_landmarks.landmark[4]
                    
                    index_x = int(index_tip.x * w)
                    index_y = int(index_tip.y * h)
                    thumb_x = int(thumb_tip.x * w)
                    thumb_y = int(thumb_tip.y * h)
                    
                    game.finger_pos = (index_x, index_y)
                    
                    # Check pinch
                    distance = math.sqrt((index_x - thumb_x)**2 + (index_y - thumb_y)**2)
                    game.is_pinching = distance < 40
                    
                    # Draw hand landmarks (minimal, subtle)
                    mp_draw.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_draw.DrawingSpec(color=(100, 255, 150), thickness=2, circle_radius=2),
                        mp_draw.DrawingSpec(color=(80, 200, 255), thickness=1)
                    )
                
                # Update game
                game.update(frame)
                
                # Quit instruction - modern
                cv2.rectangle(frame, (8, 8), (350, 48), (30, 30, 30), -1)
                cv2.rectangle(frame, (8, 8), (350, 48), (100, 100, 100), 2)
                game.draw_text_shadow(frame, "Q: Quit | R: Reload", (20, 35), 
                                     game.font, 0.6, (255, 100, 100), 1)

                # Show frame
                cv2.imshow(window_name, frame)
                
                # Keyboard
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n[*] Goodbye!\n")
                    break
                elif key == ord('r'):
                    # Reload quiz data
                    print("\n[*] Reloading quiz data...")
                    game.load_quiz_data()
                    game.setup_menu()
                    print("[OK] Quiz data reloaded!\n")
    
    except KeyboardInterrupt:
        print("\n[*] Interrupted by user")
    except Exception as e:
        print(f"\n[X] ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("[*] Cleaning up...")
        cap.release()
        cv2.destroyAllWindows()
        print("[*] Application closed")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[X] FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")