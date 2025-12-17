import cv2
import mediapipe as mp
import numpy as np
import math
import json
import random
from pathlib import Path
import sys

camera_index = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 0
print(f"[INFO] Kamera index: {camera_index}")

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
            color = (120, 180, 255) if self.hovered else (60, 60, 60)
        
        # Background with gradient effect
        overlay = frame.copy()
        cv2.rectangle(overlay, (self.x, self.y), 
                     (self.x + self.width, self.y + self.height), 
                     color, -1)
        cv2.addWeighted(overlay, 0.9, frame, 0.1, 0, frame)
        
        # Outer glow when hovered
        if self.hovered:
            cv2.rectangle(frame, (self.x-2, self.y-2), 
                         (self.x + self.width+2, self.y + self.height+2), 
                         (150, 200, 255), 3, cv2.LINE_AA)
        
        # Border
        border_color = (200, 220, 255) if self.hovered else (100, 100, 100)
        cv2.rectangle(frame, (self.x, self.y), 
                     (self.x + self.width, self.y + self.height), 
                     border_color, 2, cv2.LINE_AA)
        
        # Text centered dengan font yang lebih baik
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 0.85
        thickness = 2
        text_size = cv2.getTextSize(self.text, font, font_scale, thickness)[0]
        text_x = self.x + (self.width - text_size[0]) // 2
        text_y = self.y + (self.height + text_size[1]) // 2
        
        # Shadow
        cv2.putText(frame, self.text, (text_x + 2, text_y + 2), 
                   font, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)
        # Main text
        text_color = (255, 255, 255) if self.hovered else (220, 220, 220)
        cv2.putText(frame, self.text, (text_x, text_y), 
                   font, font_scale, text_color, thickness, cv2.LINE_AA)

class GuessGame:
    def __init__(self):
        self.state = "MENU"  # MENU, QUIZ, RESULT
        self.game_data = []
        self.current_question = None
        self.selected_answer = None
        self.buttons = []
        self.score = 0
        self.total_questions = 0
        
        # Shuffled options for current question
        self.shuffled_options = []
        
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
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2, ensure_ascii=False)
                print("[OK] Created empty guess_data.json")
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
        
        # Reset score when going back to menu
        self.score = 0
        self.total_questions = 0
        
        # Start button (centered, larger)
        self.buttons.append(Button(710, 450, 500, 100, "START GAME", "start"))
        
        # Edit button (centered, below start)
        self.buttons.append(Button(710, 580, 500, 100, "EDIT QUESTIONS", "edit"))
    
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
        
        # SHUFFLE OPTIONS
        self.shuffled_options = self.current_question["options"].copy()
        random.shuffle(self.shuffled_options)
        
        print(f"[*] Question loaded: {self.current_question['blurred_image']}")
        print(f"[*] Options shuffled: {self.shuffled_options}")
        
        # Create option buttons (4 options in 2x2 grid)
        button_width = 420
        button_height = 90
        spacing = 40
        
        # Calculate center position
        grid_width = button_width * 2 + spacing
        grid_height = button_height * 2 + spacing
        start_x = (1920 - grid_width) // 2
        start_y = 720
        
        for i, option in enumerate(self.shuffled_options):
            row = i // 2
            col = i % 2
            x = start_x + col * (button_width + spacing)
            y = start_y + row * (button_height + spacing)
            
            btn = Button(x, y, button_width, button_height, option, f"option_{i}")
            self.buttons.append(btn)
    
    def draw_menu(self, frame):
        """Draw main menu"""
        h, w = frame.shape[:2]
        
        # Modern gradient background (subtle)
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 400), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        # Title with better font
        title_font = cv2.FONT_HERSHEY_TRIPLEX
        cv2.putText(frame, "GUESS THE PICTURE", (520, 200), 
                   title_font, 2.5, (100, 255, 200), 5, cv2.LINE_AA)
        cv2.putText(frame, "GUESS THE PICTURE", (518, 198), 
                   title_font, 2.5, (50, 200, 150), 4, cv2.LINE_AA)
        
        # Subtitle
        subtitle_font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, "Can you guess what's behind the blur?", (560, 280), 
                   subtitle_font, 1.1, (200, 220, 240), 2, cv2.LINE_AA)
        
        # Draw buttons
        for btn in self.buttons:
            if btn.id == "edit":
                btn.draw(frame, (180, 120, 255) if btn.hovered else (120, 80, 200))
            else:
                btn.draw(frame, (100, 220, 150) if btn.hovered else (60, 150, 100))
        
        # Instructions at bottom
        info_font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, "Point and PINCH to select | Press 'Q' to quit", 
                   (580, h - 40), info_font, 0.8, (200, 200, 200), 2, cv2.LINE_AA)
    
    def draw_quiz(self, frame):
        """Draw quiz interface"""
        h, w = frame.shape[:2]
        
        # Top bar with gradient
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 100), (30, 30, 30), -1)
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
        
        # Load and display blurred image
        try:
            img_path = Path(__file__).parent / "assets" / "guess_game" / "blurred" / self.current_question["blurred_image"]
            
            if img_path.exists():
                img = cv2.imread(str(img_path))
                if img is not None:
                    # Resize to fit (larger for 1920x1080)
                    img_h, img_w = img.shape[:2]
                    max_width = 800
                    max_height = 550
                    
                    scale = min(max_width / img_w, max_height / img_h)
                    new_w = int(img_w * scale)
                    new_h = int(img_h * scale)
                    
                    img_resized = cv2.resize(img, (new_w, new_h))
                    
                    # Center position
                    x_offset = (1920 - new_w) // 2
                    y_offset = 120
                    
                    # Add shadow effect
                    shadow_offset = 8
                    cv2.rectangle(frame, 
                                (x_offset + shadow_offset, y_offset + shadow_offset), 
                                (x_offset + new_w + shadow_offset, y_offset + new_h + shadow_offset), 
                                (0, 0, 0), -1)
                    
                    # Place image
                    frame[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = img_resized
                    
                    # Modern border
                    cv2.rectangle(frame, (x_offset-4, y_offset-4), 
                                (x_offset+new_w+4, y_offset+new_h+4), 
                                (100, 255, 200), 4, cv2.LINE_AA)
            else:
                # Placeholder if image not found
                cv2.putText(frame, "IMAGE NOT FOUND", (720, 400), 
                           cv2.FONT_HERSHEY_DUPLEX, 1.5, (100, 100, 255), 3, cv2.LINE_AA)
        
        except Exception as e:
            print(f"[X] Error loading image: {e}")
            cv2.putText(frame, "ERROR LOADING IMAGE", (680, 400), 
                       cv2.FONT_HERSHEY_DUPLEX, 1.5, (100, 100, 255), 3, cv2.LINE_AA)
        
        # Question text
        question_font = cv2.FONT_HERSHEY_TRIPLEX
        cv2.putText(frame, "What is this?", (800, 60), 
                   question_font, 1.3, (255, 255, 255), 3, cv2.LINE_AA)
        
        # Score display (top left)
        score_font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, f"Score: {self.score}/{self.total_questions}", (40, 60), 
                   score_font, 1.1, (100, 255, 200), 3, cv2.LINE_AA)
        
        # Draw option buttons
        for btn in self.buttons:
            # Highlight selected
            if self.selected_answer == btn.id:
                btn.draw(frame, (255, 200, 100) if btn.hovered else (220, 160, 60))
            else:
                btn.draw(frame)
        
        # Submit button (if answer selected)
        if self.selected_answer:
            submit_btn = Button(710, 960, 500, 80, "SUBMIT ANSWER", "submit")
            submit_btn.hovered = (self.finger_pos and 
                                submit_btn.contains_point(self.finger_pos[0], self.finger_pos[1]))
            submit_btn.draw(frame, (100, 220, 100) if submit_btn.hovered else (60, 170, 60))
            
            if submit_btn.hovered and self.is_pinching and not self.last_pinch:
                self.check_answer()
        
        # Instructions
        cv2.putText(frame, "Select an answer and SUBMIT", 
                   (690, h - 30), cv2.FONT_HERSHEY_DUPLEX, 0.8, (200, 200, 200), 2, cv2.LINE_AA)
    
    def draw_result(self, frame):
        """Draw result screen"""
        h, w = frame.shape[:2]
        
        # Check if answer is correct
        selected_idx = int(self.selected_answer.split("_")[1])
        selected_option = self.shuffled_options[selected_idx]
        correct_answer = self.current_question["correct_answer"]
        is_correct = selected_option == correct_answer
        
        # Result text with better font
        result_text = "CORRECT!" if is_correct else "WRONG!"
        result_color = (100, 255, 150) if is_correct else (100, 120, 255)
        result_font = cv2.FONT_HERSHEY_TRIPLEX
        
        # Large result text
        cv2.putText(frame, result_text, (720, 110), 
                   result_font, 3.0, result_color, 6, cv2.LINE_AA)
        
        # Load and display ORIGINAL (unblurred) image
        try:
            img_path = Path(__file__).parent / "assets" / "guess_game" / "original" / self.current_question["original_image"]
            
            if img_path.exists():
                img = cv2.imread(str(img_path))
                if img is not None:
                    # Resize (larger)
                    img_h, img_w = img.shape[:2]
                    max_width = 900
                    max_height = 600
                    
                    scale = min(max_width / img_w, max_height / img_h)
                    new_w = int(img_w * scale)
                    new_h = int(img_h * scale)
                    
                    img_resized = cv2.resize(img, (new_w, new_h))
                    
                    # Center position
                    x_offset = (1920 - new_w) // 2
                    y_offset = 180
                    
                    # Shadow
                    shadow_offset = 10
                    cv2.rectangle(frame, 
                                (x_offset + shadow_offset, y_offset + shadow_offset), 
                                (x_offset + new_w + shadow_offset, y_offset + new_h + shadow_offset), 
                                (0, 0, 0), -1)
                    
                    # Place image
                    frame[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = img_resized
                    
                    # Border
                    border_color = (100, 255, 150) if is_correct else (100, 120, 255)
                    cv2.rectangle(frame, (x_offset-5, y_offset-5), 
                                (x_offset+new_w+5, y_offset+new_h+5), 
                                border_color, 5, cv2.LINE_AA)
                    
                    # Label
                    label_font = cv2.FONT_HERSHEY_TRIPLEX
                    cv2.putText(frame, "THE TRUTH REVEALED!", (640, 155), 
                               label_font, 1.2, (255, 255, 150), 3, cv2.LINE_AA)
        
        except Exception as e:
            print(f"[X] Error loading result image: {e}")
        
        # Answer info with better layout
        info_font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, f"Your Answer: {selected_option}", (460, 830), 
                   info_font, 1.0, (255, 255, 150), 2, cv2.LINE_AA)
        cv2.putText(frame, f"Correct Answer: {correct_answer}", (460, 870), 
                   info_font, 1.0, (150, 255, 150), 2, cv2.LINE_AA)
        
        # Score (top left)
        cv2.putText(frame, f"Score: {self.score}/{self.total_questions}", (40, 60), 
                   cv2.FONT_HERSHEY_DUPLEX, 1.1, (100, 255, 255), 3, cv2.LINE_AA)
        
        # Buttons
        button_y = 930
        button_width = 320
        button_height = 80
        button_spacing = 50
        
        total_width = button_width * 2 + button_spacing
        start_x = (1920 - total_width) // 2
        
        next_btn = Button(start_x, button_y, button_width, button_height, "NEXT QUESTION", "next")
        menu_btn = Button(start_x + button_width + button_spacing, button_y, 
                         button_width, button_height, "MAIN MENU", "menu")
        
        for btn in [next_btn, menu_btn]:
            btn.hovered = (self.finger_pos and 
                          btn.contains_point(self.finger_pos[0], self.finger_pos[1]))
            
            if btn.id == "next":
                btn.draw(frame, (100, 220, 150) if btn.hovered else (60, 170, 100))
            else:
                btn.draw(frame, (220, 150, 100) if btn.hovered else (170, 100, 60))
            
            if btn.hovered and self.is_pinching and not self.last_pinch:
                if btn.id == "next":
                    self.start_game()
                elif btn.id == "menu":
                    self.setup_menu()
    
    def check_answer(self):
        """Check answer and move to result"""
        selected_idx = int(self.selected_answer.split("_")[1])
        selected_option = self.shuffled_options[selected_idx]
        correct_answer = self.current_question["correct_answer"]
        
        if selected_option == correct_answer:
            self.score += 1
        
        self.state = "RESULT"
    
    def open_editor(self):
        """Open question editor"""
        import subprocess
        import sys
        
        try:
            editor_path = Path(__file__).parent / "guess_editor.py"
            
            if not editor_path.exists():
                print("[!] Editor not found: guess_editor.py")
                print("[!] Please make sure guess_editor.py exists in the same folder")
                return
            
            subprocess.Popen([sys.executable, str(editor_path)])
            print("[OK] Opening Guess Game Editor...")
            print("[*] Edit your questions in the editor window")
            print("[*] Press 'r' in this window to reload after editing")
        
        except Exception as e:
            print(f"[X] Error opening editor: {e}")
            import traceback
            traceback.print_exc()
    
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
        
        # Draw finger pointer (improved design)
        if self.finger_pos:
            x, y = self.finger_pos
            if self.is_pinching:
                # Pinching - yellow glow
                cv2.circle(frame, (x, y), 20, (0, 255, 255), 2, cv2.LINE_AA)
                cv2.circle(frame, (x, y), 14, (0, 255, 255), -1, cv2.LINE_AA)
                cv2.circle(frame, (x, y), 8, (255, 255, 255), -1, cv2.LINE_AA)
            else:
                # Normal - cyan/blue
                cv2.circle(frame, (x, y), 16, (255, 150, 100), 2, cv2.LINE_AA)
                cv2.circle(frame, (x, y), 10, (255, 150, 100), -1, cv2.LINE_AA)
    
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
    
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print("[X] ERROR: Cannot access camera!")
        return
    
    print("[OK] Camera accessed successfully!")
    
    # Set resolusi 1920x1080
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    game = GuessGame()
    game.setup_menu()
    print("[OK] Game initialized!")
    print("\n[*] Starting main loop...")
    print("[*] Press 'r' to reload game data after editing")
    print("[*] Resolution: 1920x1080 (Full Screen Window Mode)")
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
                    
                    # Draw hand landmarks with subtle style
                    mp_draw.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_draw.DrawingSpec(color=(100, 255, 200), thickness=2, circle_radius=2),
                        mp_draw.DrawingSpec(color=(100, 200, 255), thickness=2)
                    )
                
                game.update(frame)
                
                # Status bar at top right
                cv2.putText(frame, "Press 'Q' to Quit | 'R' to Reload", (1480, 35), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.7, (150, 150, 150), 2, cv2.LINE_AA)
                
                # Window mode biasa dengan ukuran 1920x1080
                cv2.namedWindow("Guess The Picture", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Guess The Picture", 1920, 1080)
                cv2.imshow("Guess The Picture", frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    print("\n[*] Goodbye!\n")
                    break
                elif key == ord('r') or key == ord('R'):
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