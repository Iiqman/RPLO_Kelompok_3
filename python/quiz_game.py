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
    """Class untuk button/word card yang bisa diklik"""
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
        """Draw button on frame"""
        if color is None:
            if self.selected:
                color = (100, 200, 100)  # Green when selected
            elif self.hovered:
                color = (100, 150, 255)  # Light blue when hovered
            else:
                color = (80, 80, 80)  # Gray default
        
        # Draw button background
        cv2.rectangle(frame, (self.x, self.y), 
                      (self.x + self.width, self.y + self.height), 
                      color, -1)
        
        # Draw border
        border_color = (255, 255, 255) if self.hovered else (120, 120, 120)
        cv2.rectangle(frame, (self.x, self.y), 
                      (self.x + self.width, self.y + self.height), 
                      border_color, 2)
        
        # Draw text centered
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
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
    
    def setup_menu(self):
        """Setup main menu buttons"""
        self.state = "MENU"
        self.buttons = []
        
        # Reset score when going back to menu
        self.score = 0
        self.total_questions = 0
        
        categories = ["Present", "Past", "Future", "Past Future"]
        button_width = 200
        button_height = 80
        spacing = 20
        start_y = 180
        
        # Category buttons - centered
        for i, category in enumerate(categories):
            x = 640 - button_width // 2  # Center
            y = start_y + i * (button_height + spacing)
            self.buttons.append(Button(x, y, button_width, button_height, category, category))
        
        # Edit Quiz button - bottom center
        edit_btn_width = 250
        edit_x = 640 - edit_btn_width // 2
        self.buttons.append(Button(edit_x, 620, edit_btn_width, 60, "EDIT QUESTIONS", "edit_quiz"))
    
    def setup_difficulty(self):
        """Setup difficulty selection"""
        self.state = "DIFFICULTY"
        self.buttons = []
        
        difficulties = ["Easy", "Medium", "Hard"]
        
        button_width = 180
        button_height = 80
        spacing = 30
        start_x = 640 - (button_width * 3 + spacing * 2) // 2
        y = 300
        
        for i, diff in enumerate(difficulties):
            x = start_x + i * (button_width + spacing)
            btn = Button(x, y, button_width, button_height, diff, diff.lower())
            self.buttons.append(btn)
        
        # Back button - center bottom
        back_x = 640 - 60
        self.buttons.append(Button(back_x, 600, 120, 50, "Back", "back"))
    
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
        
        # SHUFFLE WORDS - INI YANG PENTING!
        self.available_words = question_data["words"].copy()
        random.shuffle(self.available_words)  # Acak posisi kata
        
        print(f"[*] Words shuffled: {self.available_words}")
        
        # Timer
        self.time_limit = question_data.get("timer", 30)
        self.start_time = time.time()
        
        # Create word buttons
        self.create_word_buttons()
        
        # Create answer area buttons
        self.create_answer_area()
    
    def create_word_buttons(self):
        """Create buttons for available words - CENTERED"""
        button_width = 120
        button_height = 60
        spacing_x = 15
        spacing_y = 15
        words_per_row = 6
        
        # Calculate rows needed
        num_words = len(self.available_words)
        num_rows = (num_words + words_per_row - 1) // words_per_row
        
        start_y = 500
        
        for i, word in enumerate(self.available_words):
            row = i // words_per_row
            col = i % words_per_row
            
            # Calculate words in this row
            words_in_row = min(words_per_row, num_words - row * words_per_row)
            
            # Calculate starting x for centering this row
            total_width = words_in_row * button_width + (words_in_row - 1) * spacing_x
            start_x = (1280 - total_width) // 2
            
            x = start_x + col * (button_width + spacing_x)
            y = start_y + row * (button_height + spacing_y)
            
            btn = Button(x, y, button_width, button_height, word, f"word_{i}")
            self.buttons.append(btn)
    
    def create_answer_area(self):
        """Create answer area for selected words"""
        # Answer area is dynamic, will be created as words are selected
        pass
    
    def update_answer_display(self):
        """Update answer buttons based on current sequence"""
        self.answer_buttons = []
        
        button_width = 120
        button_height = 60
        spacing = 10
        start_y = 250
        
        if not self.answer_sequence:
            return
        
        # Calculate total width and center
        total_width = len(self.answer_sequence) * button_width + (len(self.answer_sequence) - 1) * spacing
        start_x = (1280 - total_width) // 2
        
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
        """Draw main menu"""
        h, w = frame.shape[:2]
        
        # Title
        title = "ENGLISH SENTENCE QUIZ"
        cv2.putText(frame, title, (640 - 250, 100), 
                    cv2.FONT_HERSHEY_COMPLEX, 1.2, (0, 255, 100), 3, cv2.LINE_AA)
        
        # Subtitle
        subtitle = "Select Tense Category"
        cv2.putText(frame, subtitle, (640 - 150, 150), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2, cv2.LINE_AA)
        
        # Draw buttons
        for btn in self.buttons:
            if btn.id == "edit_quiz":
                # Special color for edit button
                btn.draw(frame, (150, 100, 255) if btn.hovered else (100, 70, 180))
            else:
                btn.draw(frame)
        
        # Instructions
        cv2.putText(frame, "Point and PINCH fingers to select", 
                    (50, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    
    def draw_difficulty(self, frame):
        """Draw difficulty selection"""
        h, w = frame.shape[:2]
        
        # Title
        title = f"Category: {self.current_category}"
        cv2.putText(frame, title, (640 - 200, 100), 
                    cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 255, 100), 2, cv2.LINE_AA)
        
        # Subtitle
        subtitle = "Select Difficulty"
        cv2.putText(frame, subtitle, (640 - 120, 200), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2, cv2.LINE_AA)
        
        # Draw buttons
        for btn in self.buttons:
            if btn.id == "easy":
                btn.draw(frame, (100, 200, 100) if btn.hovered else (80, 150, 80))
            elif btn.id == "medium":
                btn.draw(frame, (255, 180, 50) if btn.hovered else (200, 140, 40))
            elif btn.id == "hard":
                btn.draw(frame, (255, 120, 120) if btn.hovered else (200, 80, 80))
            else:
                btn.draw(frame)
        
        # Info text
        info_lines = [
            "Easy: 3-5 words, 25-30 seconds",
            "Medium: 6-8 words, 35-40 seconds",
            "Hard: 8+ words, 45-50 seconds"
        ]
        
        for i, line in enumerate(info_lines):
            cv2.putText(frame, line, (400, 450 + i * 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1, cv2.LINE_AA)
    
    def draw_quiz(self, frame):
        """Draw quiz interface"""
        h, w = frame.shape[:2]
        
        # Timer
        elapsed = time.time() - self.start_time
        remaining = max(0, self.time_limit - int(elapsed))
        
        timer_color = (0, 255, 0) if remaining > 10 else (0, 100, 255) if remaining > 5 else (0, 0, 255)
        cv2.putText(frame, f"Time: {remaining}s", (1100, 50), 
                    cv2.FONT_HERSHEY_COMPLEX, 1.0, timer_color, 2, cv2.LINE_AA)
        
        # Question
        question_text = self.current_question["question"]
        cv2.putText(frame, f"Question: {question_text}", (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Category and difficulty
        cv2.putText(frame, f"{self.current_category} - {self.current_difficulty.title()}", 
                    (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1, cv2.LINE_AA)
        
        # Score
        cv2.putText(frame, f"Score: {self.score}", (50, 130), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 100), 2, cv2.LINE_AA)
        
        # Answer area label
        cv2.putText(frame, "Your Answer:", (50, 200), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)
        
        # Draw answer buttons
        for btn in self.answer_buttons:
            btn.draw(frame)
        
        # Available words label
        cv2.putText(frame, "Available Words (click to add):", (50, 460), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)
        
        # Draw word buttons
        for btn in self.buttons:
            btn.draw(frame)
        
        # Submit and Clear buttons - CENTERED at bottom
        button_y = 660
        button_height = 50
        button_spacing = 30
        
        # Clear button (left)
        clear_width = 130
        submit_width = 150
        total_buttons_width = clear_width + button_spacing + submit_width
        start_x = (1280 - total_buttons_width) // 2
        
        clear_btn = Button(start_x, button_y, clear_width, button_height, "CLEAR", "clear")
        clear_btn.hovered = (self.finger_pos and 
                            clear_btn.contains_point(self.finger_pos[0], self.finger_pos[1]))
        clear_btn.draw(frame, (255, 100, 100) if clear_btn.hovered else (150, 80, 80))
        
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
            submit_btn.draw(frame, (100, 200, 100) if submit_btn.hovered else (80, 150, 80))
            
            # Check if submit clicked
            if submit_btn.hovered and self.is_pinching and not self.last_pinch:
                self.finish_quiz()
        
        # Time up check
        if remaining <= 0:
            self.finish_quiz()
        
        # Instructions
        cv2.putText(frame, "Pinch to select words | Build sentence | Click answer to remove | SUBMIT when done", 
                    (50, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    
    def draw_result(self, frame):
        """Draw result screen"""
        h, w = frame.shape[:2]
        
        # Result
        is_correct = self.check_answer()
        result_text = "CORRECT!" if is_correct else "WRONG!"
        result_color = (100, 255, 100) if is_correct else (100, 100, 255)
        
        cv2.putText(frame, result_text, (640 - 100, 150), 
                    cv2.FONT_HERSHEY_COMPLEX, 1.5, result_color, 3, cv2.LINE_AA)
        
        # Question
        cv2.putText(frame, f"Question: {self.current_question['question']}", 
                    (100, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Your answer
        your_answer = " ".join(self.answer_sequence)
        cv2.putText(frame, f"Your Answer:", (100, 320), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)
        cv2.putText(frame, your_answer if your_answer else "(empty)", 
                    (100, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 100), 2, cv2.LINE_AA)
        
        # Correct answer
        correct_answer = " ".join(self.current_question["correct_answer"])
        cv2.putText(frame, f"Correct Answer:", (100, 430), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)
        cv2.putText(frame, correct_answer, 
                    (100, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 255, 100), 2, cv2.LINE_AA)
        
        # Current Score
        cv2.putText(frame, f"Score: {self.score}/{self.total_questions}", 
                    (100, 540), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 255, 255), 2, cv2.LINE_AA)
        
        # Buttons - CENTERED
        button_y = 600
        button_width = 200
        button_height = 70
        button_spacing = 30
        
        total_width = button_width * 2 + button_spacing
        start_x = (1280 - total_width) // 2
        
        next_btn = Button(start_x, button_y, button_width, button_height, "NEXT", "next")
        menu_btn = Button(start_x + button_width + button_spacing, button_y, 
                         button_width, button_height, "MENU", "menu")
        
        for btn in [next_btn, menu_btn]:
            btn.hovered = (self.finger_pos and 
                          btn.contains_point(self.finger_pos[0], self.finger_pos[1]))
            btn.draw(frame)
            
            if btn.hovered and self.is_pinching and not self.last_pinch:
                if btn.id == "next":
                    self.start_quiz()  # Kata akan di-shuffle lagi!
                elif btn.id == "menu":
                    self.setup_menu()
    
    def finish_quiz(self):
        """Finish current quiz"""
        self.total_questions += 1
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
        
        # Draw finger pointer
        if self.finger_pos:
            x, y = self.finger_pos
            color = (0, 255, 255) if self.is_pinching else (255, 100, 100)
            cv2.circle(frame, (x, y), 12 if self.is_pinching else 8, color, -1, cv2.LINE_AA)
            cv2.circle(frame, (x, y), 16 if self.is_pinching else 12, color, 2, cv2.LINE_AA)
    
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
                self.start_quiz()  # Kata akan di-shuffle!
        
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
    print("[*] ENGLISH SENTENCE QUIZ - Starting Application")
    print("=" * 70)
    
    # Test camera
    print("[*] Testing camera access...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[X] ERROR: Cannot access camera!")
        return
    
    print("[OK] Camera accessed successfully!")
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Initialize game
    print("[*] Initializing quiz game...")
    game = QuizGame()
    game.setup_menu()
    print("[OK] Quiz game initialized!")
    print("\n[*] Starting main loop...")
    print("[*] Press 'r' to reload quiz data after editing")
    print("[*] Words will be SHUFFLED every time you start a new quiz!")
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
                    
                    # Draw hand landmarks (minimal)
                    mp_draw.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_draw.DrawingSpec(color=(0, 255, 100), thickness=1, circle_radius=1),
                        mp_draw.DrawingSpec(color=(0, 180, 255), thickness=1)
                    )
                
                # Update game
                game.update(frame)
                
                # Quit instruction
                cv2.putText(frame, "Press 'q' to Quit | 'r' to Reload", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)

                # Show frame
                cv2.imshow("English Sentence Quiz", frame)
                
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