import cv2
import mediapipe as mp
import numpy as np
import math
import json
import random
from pathlib import Path

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

class Button:
    """Class untuk button yang bisa diklik"""
    def __init__(self, x, y, width, height, text, id=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.id = id
        self.hovered = False
        
    def contains_point(self, x, y):
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
    
    def draw(self, frame, color=None):
        if color is None:
            color = (100, 150, 255) if self.hovered else (80, 80, 80)
        
        # Background
        cv2.rectangle(frame, (self.x, self.y), 
                     (self.x + self.width, self.y + self.height), 
                     color, -1)
        
        # Border
        border_color = (255, 255, 255) if self.hovered else (120, 120, 120)
        cv2.rectangle(frame, (self.x, self.y), 
                     (self.x + self.width, self.y + self.height), 
                     border_color, 2)
        
        # Text centered
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        text_size = cv2.getTextSize(self.text, font, font_scale, thickness)[0]
        text_x = self.x + (self.width - text_size[0]) // 2
        text_y = self.y + (self.height + text_size[1]) // 2
        
        # Shadow
        cv2.putText(frame, self.text, (text_x + 2, text_y + 2), 
                   font, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)
        # Main
        cv2.putText(frame, self.text, (text_x, text_y), 
                   font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

class GuessGame:
    def __init__(self):
        self.state = "MENU"  # MENU, QUIZ, RESULT
        self.game_data = []
        self.current_question = None
        self.selected_answer = None
        self.buttons = []
        self.score = 0
        self.total_questions = 0
        
        # Hand tracking
        self.finger_pos = None
        self.is_pinching = False
        self.last_pinch = False
        self.pinch_cooldown = 0
        
        # Load game data
        self.load_game_data()
        
    def load_game_data(self):
        """Load game data from JSON"""
        try:
            json_path = Path(__file__).parent / "guess_data.json"
            
            if not json_path.exists():
                print("[!] guess_data.json not found!")
                self.game_data = []
                return
            
            with open(json_path, 'r', encoding='utf-8') as f:
                self.game_data = json.load(f)
            
            print(f"[OK] Loaded {len(self.game_data)} questions")
            
        except Exception as e:
            print(f"[X] Error loading game data: {e}")
            self.game_data = []
    
    def setup_menu(self):
        """Setup main menu"""
        self.state = "MENU"
        self.buttons = []
        
        # Start button
        self.buttons.append(Button(490, 300, 300, 80, "START GAME", "start"))
        
        # Edit button
        self.buttons.append(Button(490, 410, 300, 80, "EDIT QUESTIONS", "edit"))
    
    def start_game(self):
        """Start the game"""
        if not self.game_data:
            print("[!] No questions available!")
            return
        
        self.state = "QUIZ"
        self.total_questions += 1
        self.current_question = random.choice(self.game_data)
        self.selected_answer = None
        self.buttons = []
        
        # Create option buttons (4 options in 2x2 grid)
        options = self.current_question["options"]
        button_width = 280
        button_height = 70
        spacing = 30
        
        # Calculate center position
        grid_width = button_width * 2 + spacing
        grid_height = button_height * 2 + spacing
        start_x = (1280 - grid_width) // 2
        start_y = 480
        
        for i, option in enumerate(options):
            row = i // 2
            col = i % 2
            x = start_x + col * (button_width + spacing)
            y = start_y + row * (button_height + spacing)
            
            btn = Button(x, y, button_width, button_height, option, f"option_{i}")
            self.buttons.append(btn)
        
        print(f"[*] Question loaded: {self.current_question['blurred_image']}")
    
    def draw_menu(self, frame):
        """Draw main menu"""
        h, w = frame.shape[:2]
        
        # Title
        cv2.putText(frame, "GUESS THE PICTURE", (380, 150), 
                   cv2.FONT_HERSHEY_BOLD, 1.5, (0, 255, 100), 3, cv2.LINE_AA)
        
        # Subtitle
        cv2.putText(frame, "Can you guess what's behind the blur?", (400, 220), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2, cv2.LINE_AA)
        
        # Draw buttons
        for btn in self.buttons:
            if btn.id == "edit":
                btn.draw(frame, (150, 100, 255) if btn.hovered else (100, 70, 180))
            else:
                btn.draw(frame)
        
        # Instructions
        cv2.putText(frame, "Point and PINCH to select | Press 'q' to quit", 
                   (50, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    
    def draw_quiz(self, frame):
        """Draw quiz interface"""
        h, w = frame.shape[:2]
        
        # Load and display blurred image
        try:
            img_path = Path(__file__).parent / "assets" / "guess_game" / "blurred" / self.current_question["blurred_image"]
            
            if img_path.exists():
                img = cv2.imread(str(img_path))
                if img is not None:
                    # Resize to fit
                    img_h, img_w = img.shape[:2]
                    max_width = 500
                    max_height = 350
                    
                    scale = min(max_width / img_w, max_height / img_h)
                    new_w = int(img_w * scale)
                    new_h = int(img_h * scale)
                    
                    img_resized = cv2.resize(img, (new_w, new_h))
                    
                    # Center position
                    x_offset = (1280 - new_w) // 2
                    y_offset = 80
                    
                    # Place image
                    frame[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = img_resized
                    
                    # Border around image
                    cv2.rectangle(frame, (x_offset-3, y_offset-3), 
                                (x_offset+new_w+3, y_offset+new_h+3), 
                                (0, 255, 100), 3)
            else:
                # Placeholder if image not found
                cv2.putText(frame, "IMAGE NOT FOUND", (450, 250), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, cv2.LINE_AA)
                cv2.putText(frame, f"Path: {img_path}", (350, 300), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1, cv2.LINE_AA)
        
        except Exception as e:
            print(f"[X] Error loading image: {e}")
            cv2.putText(frame, "ERROR LOADING IMAGE", (450, 250), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, cv2.LINE_AA)
        
        # Question text
        cv2.putText(frame, "What is this?", (540, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Score
        cv2.putText(frame, f"Score: {self.score}/{self.total_questions}", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 255, 100), 2, cv2.LINE_AA)
        
        # Draw option buttons
        for btn in self.buttons:
            # Highlight selected
            if self.selected_answer == btn.id:
                btn.draw(frame, (255, 200, 100) if btn.hovered else (200, 150, 50))
            else:
                btn.draw(frame)
        
        # Submit button (if answer selected)
        if self.selected_answer:
            submit_btn = Button(490, 650, 300, 60, "SUBMIT", "submit")
            submit_btn.hovered = (self.finger_pos and 
                                submit_btn.contains_point(self.finger_pos[0], self.finger_pos[1]))
            submit_btn.draw(frame, (100, 200, 100) if submit_btn.hovered else (80, 150, 80))
            
            if submit_btn.hovered and self.is_pinching and not self.last_pinch:
                self.check_answer()
        
        # Instructions
        cv2.putText(frame, "Select an answer and SUBMIT", 
                   (50, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    
    def draw_result(self, frame):
        """Draw result screen"""
        h, w = frame.shape[:2]
        
        # Check if answer is correct
        selected_idx = int(self.selected_answer.split("_")[1])
        correct_answer = self.current_question["correct_answer"]
        is_correct = self.current_question["options"][selected_idx] == correct_answer
        
        # Result text
        result_text = "CORRECT!" if is_correct else "WRONG!"
        result_color = (100, 255, 100) if is_correct else (100, 100, 255)
        
        cv2.putText(frame, result_text, (500, 80), 
                   cv2.FONT_HERSHEY_BOLD, 1.8, result_color, 4, cv2.LINE_AA)
        
        # Load and display ORIGINAL (unblurred) image - THE PLOT TWIST!
        try:
            img_path = Path(__file__).parent / "assets" / "guess_game" / "original" / self.current_question["original_image"]
            
            if img_path.exists():
                img = cv2.imread(str(img_path))
                if img is not None:
                    # Resize
                    img_h, img_w = img.shape[:2]
                    max_width = 600
                    max_height = 400
                    
                    scale = min(max_width / img_w, max_height / img_h)
                    new_w = int(img_w * scale)
                    new_h = int(img_h * scale)
                    
                    img_resized = cv2.resize(img, (new_w, new_h))
                    
                    # Center position
                    x_offset = (1280 - new_w) // 2
                    y_offset = 140
                    
                    # Place image
                    frame[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = img_resized
                    
                    # Border
                    border_color = (100, 255, 100) if is_correct else (100, 100, 255)
                    cv2.rectangle(frame, (x_offset-4, y_offset-4), 
                                (x_offset+new_w+4, y_offset+new_h+4), 
                                border_color, 4)
                    
                    # "PLOT TWIST!" label
                    cv2.putText(frame, "THE TRUTH REVEALED!", (420, 120), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 100), 2, cv2.LINE_AA)
        
        except Exception as e:
            print(f"[X] Error loading result image: {e}")
        
        # Answer info
        cv2.putText(frame, f"Correct Answer: {correct_answer}", (380, 590), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Buttons
        button_y = 630
        button_width = 200
        button_height = 60
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
                    self.start_game()
                elif btn.id == "menu":
                    self.setup_menu()
    
    def check_answer(self):
        """Check answer and move to result"""
        selected_idx = int(self.selected_answer.split("_")[1])
        correct_answer = self.current_question["correct_answer"]
        
        if self.current_question["options"][selected_idx] == correct_answer:
            self.score += 1
        
        self.state = "RESULT"
    
    def open_editor(self):
        """Open question editor"""
        import subprocess
        import sys
        
        try:
            editor_path = Path(__file__).parent / "quiz_editor.py"
            
            if editor_path.exists():
                # Run editor as separate process
                subprocess.Popen([sys.executable, str(editor_path), "guess"])
                print("[OK] Opening editor...")
            else:
                print("[!] Editor not found: quiz_editor.py")
        
        except Exception as e:
            print(f"[X] Error opening editor: {e}")
    
    def update(self, frame):
        """Main update loop"""
        if self.finger_pos:
            x, y = self.finger_pos
            
            for btn in self.buttons:
                btn.hovered = btn.contains_point(x, y)
                
                if btn.hovered and self.is_pinching and not self.last_pinch and self.pinch_cooldown <= 0:
                    self.handle_button_click(btn)
                    self.pinch_cooldown = 15
        
        if self.pinch_cooldown > 0:
            self.pinch_cooldown -= 1
        
        # Draw based on state
        if self.state == "MENU":
            self.draw_menu(frame)
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
        """Handle button clicks"""
        if self.state == "MENU":
            if btn.id == "start":
                self.start_game()
            elif btn.id == "edit":
                self.open_editor()
        
        elif self.state == "QUIZ":
            if btn.id.startswith("option_"):
                self.selected_answer = btn.id

def main():
    print("\n" + "=" * 70)
    print("[*] GUESS THE PICTURE - Starting Application")
    print("=" * 70)
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[X] ERROR: Cannot access camera!")
        return
    
    print("[OK] Camera accessed successfully!")
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    game = GuessGame()
    game.setup_menu()
    print("[OK] Game initialized!")
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
                
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)
                
                game.finger_pos = None
                game.last_pinch = game.is_pinching
                game.is_pinching = False
                
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    
                    index_tip = hand_landmarks.landmark[8]
                    thumb_tip = hand_landmarks.landmark[4]
                    
                    index_x = int(index_tip.x * w)
                    index_y = int(index_tip.y * h)
                    thumb_x = int(thumb_tip.x * w)
                    thumb_y = int(thumb_tip.y * h)
                    
                    game.finger_pos = (index_x, index_y)
                    
                    distance = math.sqrt((index_x - thumb_x)**2 + (index_y - thumb_y)**2)
                    game.is_pinching = distance < 40
                    
                    mp_draw.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_draw.DrawingSpec(color=(0, 255, 100), thickness=1, circle_radius=1),
                        mp_draw.DrawingSpec(color=(0, 180, 255), thickness=1)
                    )
                
                game.update(frame)
                
                cv2.putText(frame, "Press 'q' to Quit | 'r' to Reload", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv2.LINE_AA)
                
                cv2.imshow("Guess The Picture", frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n[*] Goodbye!\n")
                    break
                elif key == ord('r'):
                    print("\n[*] Reloading game data...")
                    game.load_game_data()
                    game.setup_menu()
                    print("[OK] Data reloaded!\n")
    
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