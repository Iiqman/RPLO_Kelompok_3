import cv2
import mediapipe as mp
import numpy as np
import math
import os
from collections import deque
from pathlib import Path
import time
import sys
import json

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils


# Emoji database
EMOJI_PATTERNS = {
    "smile": {
        "name": "Smile", 
        "file": "smile.png", 
        "detection": "circle",
        "hint": "Draw: O"
    },
    "heart": {
        "name": "Heart", 
        "file": "heart.png", 
        "detection": "heart",
        "hint": "Draw: <3"
    },
    "star": {
        "name": "Star", 
        "file": "star.png", 
        "detection": "star",
        "hint": "Draw: *"
    },
    "check": {
        "name": "Check", 
        "file": "check.png", 
        "detection": "check",
        "hint": "Draw: v"
    },
    "thumbs_up": {
        "name": "Thumbs Up", 
        "file": "thumbs_up.png", 
        "detection": "vertical",
        "hint": "Draw: |"
    },
    "square": {
        "name": "Square", 
        "file": "square.png", 
        "detection": "square",
        "hint": "Draw: []"
    },
    "triangle": {
        "name": "Triangle", 
        "file": "triangle.png", 
        "detection": "triangle",
        "hint": "Draw: ^"
    }
}

class EmojiDrawer:
    def __init__(self):
        self.drawing = False
        self.points = deque(maxlen=2048)
        self.smoothed_points = deque(maxlen=5)
        self.canvas = None
        self.prev_point = None
        self.brush_size = 15
        self.color = (0, 255, 100)
        
        # Detection parameters
        self.detected_emoji = None
        self.emoji_position = None
        self.show_emoji_frames = 0
        self.emoji_alpha = 1.0
        
        # Load emoji images
        self.emoji_images = {}
        self.load_emoji_images()
        
        # UI State
        self.show_hints = True
        
        # Font untuk UI (lebih bagus)
        self.font = cv2.FONT_HERSHEY_DUPLEX
    
    def load_emoji_images(self):
        """Load emoji PNG images dari folder assets"""
        try:
            script_dir = Path(__file__).parent
            emoji_dir = script_dir / "assets" / "emojis"
            
            print("=" * 70)
            print("[*] EMOJI DRAWER - Loading Resources")
            print("=" * 70)
            print(f"[*] Emoji directory: {emoji_dir}")
            
            if not emoji_dir.exists():
                print(f"\n[!] WARNING: Emoji directory not found!")
                print(f"[*] Creating directory: {emoji_dir}")
                emoji_dir.mkdir(parents=True, exist_ok=True)
                print(f"\n[TIP] Add emoji PNG files to: {emoji_dir}")
                return
            
            # Load each emoji image
            loaded_count = 0
            for emoji_key, emoji_data in EMOJI_PATTERNS.items():
                file_path = emoji_dir / emoji_data["file"]
                
                if file_path.exists():
                    try:
                        img = cv2.imread(str(file_path), cv2.IMREAD_UNCHANGED)
                        if img is not None:
                            self.emoji_images[emoji_key] = img
                            print(f"[OK] Loaded: {emoji_data['file']:20s} -> {emoji_data['name']}")
                            loaded_count += 1
                        else:
                            print(f"[!] Failed to load: {emoji_data['file']} (file corrupted?)")
                    except Exception as e:
                        print(f"[X] Error loading {emoji_data['file']}: {e}")
                else:
                    print(f"[!] Not found: {emoji_data['file']}")
            
            print("=" * 70)
            if loaded_count == len(EMOJI_PATTERNS):
                print(f"[SUCCESS] All emojis loaded! ({loaded_count}/{len(EMOJI_PATTERNS)})")
            elif loaded_count > 0:
                print(f"[WARNING] Partially loaded: {loaded_count}/{len(EMOJI_PATTERNS)} emojis")
            else:
                print(f"[ERROR] No emojis loaded!")
            print("=" * 70)
            print()
            
        except Exception as e:
            print(f"[X] CRITICAL ERROR in load_emoji_images: {e}")
            import traceback
            traceback.print_exc()
    
    def overlay_png(self, background, overlay, x, y, size, alpha=1.0):
        """Overlay gambar PNG dengan transparency"""
        try:
            # Resize overlay
            overlay_resized = cv2.resize(overlay, (size, size))
            
            # Calculate position
            x1 = max(0, x - size // 2)
            y1 = max(0, y - size // 2)
            x2 = min(background.shape[1], x1 + size)
            y2 = min(background.shape[0], y1 + size)
            
            if x2 <= x1 or y2 <= y1:
                return
            
            # Calculate overlay region
            overlay_x1 = 0 if x >= size // 2 else (size // 2 - x)
            overlay_y1 = 0 if y >= size // 2 else (size // 2 - y)
            overlay_x2 = overlay_x1 + (x2 - x1)
            overlay_y2 = overlay_y1 + (y2 - y1)
            
            # Get ROI
            roi = background[y1:y2, x1:x2]
            overlay_region = overlay_resized[overlay_y1:overlay_y2, overlay_x1:overlay_x2]
            
            if roi.shape[:2] != overlay_region.shape[:2]:
                return
            
            # Blend with alpha
            if overlay_region.shape[2] == 4:
                overlay_rgb = overlay_region[:, :, :3]
                overlay_alpha = (overlay_region[:, :, 3] / 255.0) * alpha
                overlay_alpha = overlay_alpha[:, :, np.newaxis]
                
                blended = overlay_alpha * overlay_rgb + (1 - overlay_alpha) * roi
                background[y1:y2, x1:x2] = blended.astype(np.uint8)
            else:
                blended = alpha * overlay_region + (1 - alpha) * roi
                background[y1:y2, x1:x2] = blended.astype(np.uint8)
                
        except Exception as e:
            print(f"[!] Error in overlay_png: {e}")
    
    def smooth_point(self, point):
        """Apply moving average smoothing to point"""
        self.smoothed_points.append(point)
        if len(self.smoothed_points) < 2:
            return point
        
        # Calculate weighted average
        total_weight = 0
        weighted_x = 0
        weighted_y = 0
        
        for i, pt in enumerate(self.smoothed_points):
            weight = i + 1
            weighted_x += pt[0] * weight
            weighted_y += pt[1] * weight
            total_weight += weight
        
        smoothed_x = int(weighted_x / total_weight)
        smoothed_y = int(weighted_y / total_weight)
        
        return (smoothed_x, smoothed_y)
    
    def smooth_line(self, p1, p2):
        """Interpolasi untuk garis smooth"""
        if p1 is None or p2 is None:
            return []
        
        x1, y1 = p1
        x2, y2 = p2
        
        distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        if distance < 2:
            return [p2]
        
        num_points = max(int(distance / 2), 1)
        interpolated = []
        for i in range(num_points + 1):
            t = i / num_points
            x = int(x1 + (x2 - x1) * t)
            y = int(y1 + (y2 - y1) * t)
            interpolated.append((x, y))
        
        return interpolated
    
    def is_check_mark(self, contour, w, h):
        """Specifically detect V or check mark shape"""
        try:
            x, y, bw, bh = cv2.boundingRect(contour)
            mid_y = y + bh // 2
            
            top_points = []
            bottom_points = []
            
            for point in contour:
                px, py = point[0]
                if py < mid_y:
                    top_points.append(px)
                else:
                    bottom_points.append(px)
            
            if len(top_points) < 3 or len(bottom_points) < 3:
                return False
            
            top_width = max(top_points) - min(top_points) if top_points else 0
            bottom_width = max(bottom_points) - min(bottom_points) if bottom_points else 0
            
            width_ratio = top_width / bottom_width if bottom_width > 0 else 0
            aspect_ratio = float(bw) / bh if bh > 0 else 0
            
            if width_ratio > 1.2 and 1.0 < aspect_ratio < 2.5:
                print(f"   [CHECK] Width ratio: {width_ratio:.2f}, Aspect: {aspect_ratio:.2f}")
                return True
            
            return False
            
        except Exception as e:
            return False

    def is_heart_shape(self, contour):
        """Detect heart shape berdasarkan convexity defects"""
        try:
            hull = cv2.convexHull(contour, returnPoints=False)
            if hull is None or len(hull) < 3:
                return False
            
            defects = cv2.convexityDefects(contour, hull)
            if defects is None:
                return False
            
            count_defects = 0
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                if d > 1000:
                    count_defects += 1
            
            if count_defects == 2:
                print(f"   [HEART] Convexity defects count: {count_defects}")
                return True
            
            return False
        except:
            return False

    def is_star_shape(self, contour, corners, solidity, circularity):
        """IMPROVED star detection dengan multiple criteria"""
        try:
            # Kriteria 1: Many corners + low solidity (classic star)
            if 7 <= corners <= 20 and solidity < 0.75 and circularity < 0.65:
                print(f"   [STAR] Type A: corners={corners}, solidity={solidity:.2f}")
                return True
            
            # Kriteria 2: Moderate corners + very low solidity (rough star)
            if 5 <= corners <= 12 and solidity < 0.60:
                print(f"   [STAR] Type B: corners={corners}, solidity={solidity:.2f}")
                return True
            
            # Kriteria 3: Check convexity defects (star has many points)
            hull = cv2.convexHull(contour, returnPoints=False)
            if hull is not None and len(hull) >= 3:
                defects = cv2.convexityDefects(contour, hull)
                if defects is not None:
                    deep_defects = sum(1 for i in range(defects.shape[0]) if defects[i, 0, 3] > 800)
                    if deep_defects >= 4 and corners >= 6:
                        print(f"   [STAR] Type C: deep_defects={deep_defects}, corners={corners}")
                        return True
            
            # Kriteria 4: Alternative - banyak corners dengan circularity rendah
            if corners >= 8 and circularity < 0.70 and solidity < 0.80:
                print(f"   [STAR] Type D: corners={corners}, circularity={circularity:.2f}")
                return True
                
            return False
            
        except Exception as e:
            print(f"   [!] Error in is_star_shape: {e}")
            return False

    def detect_emoji_from_drawing(self, canvas):
        """Deteksi emoji dari gambar - IMPROVED dengan deteksi star yang lebih baik"""
        try:
            # Convert ke grayscale
            gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
            
            # Morphological operations
            kernel = np.ones((5,5), np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return None, None
            
            # Ambil contour terbesar
            main_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(main_contour)
            
            if area < 800:
                print(f"   [!] Area too small: {area:.0f} (minimum: 800)")
                return None, None
            
            # Get properties
            x, y, w, h = cv2.boundingRect(main_contour)
            center = (x + w//2, y + h//2)
            
            perimeter = cv2.arcLength(main_contour, True)
            circularity = 4 * math.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
            aspect_ratio = float(w) / h if h > 0 else 0
            
            # Polygon approximation - RELAXED untuk star
            epsilon = 0.03 * perimeter
            approx = cv2.approxPolyDP(main_contour, epsilon, True)
            corners = len(approx)
            
            # Convexity
            hull = cv2.convexHull(main_contour)
            hull_area = cv2.contourArea(hull)
            solidity = float(area) / hull_area if hull_area > 0 else 0
            
            # Debug info
            print(f"\n[DEBUG] Detection Analysis:")
            print(f"   Area: {area:.0f} | Circularity: {circularity:.2f}")
            print(f"   Aspect Ratio: {aspect_ratio:.2f} | Corners: {corners}")
            print(f"   Solidity: {solidity:.2f} | W: {w}, H: {h}")
            
            detected = None
            
            # DETECTION LOGIC - IMPROVED with BETTER STAR DETECTION
            
            # 1. CHECK MARK - PRIORITY
            if self.is_check_mark(main_contour, w, h):
                detected = "check"
                print(f"   [OK] Detected: CHECK MARK")
            
            # 2. STAR - IMPROVED DETECTION (check early to avoid confusion with other shapes)
            elif self.is_star_shape(main_contour, corners, solidity, circularity):
                detected = "star"
                print(f"   [OK] Detected: STAR")
            
            # 3. TRIANGLE - 3-4 corners, low circularity
            elif 3 <= corners <= 4 and circularity < 0.75 and 0.7 < aspect_ratio < 1.5:
                detected = "triangle"
                print(f"   [OK] Detected: TRIANGLE")
            
            # 4. SQUARE - 4-6 corners, square-like, medium-high solidity
            elif 4 <= corners <= 6 and 0.7 < aspect_ratio < 1.3 and solidity > 0.75:
                detected = "square"
                print(f"   [OK] Detected: SQUARE")
            
            # 5. CIRCLE (Smile) - High circularity
            elif circularity > 0.70 and 0.75 < aspect_ratio < 1.30:
                detected = "smile"
                print(f"   [OK] Detected: SMILE")
            
            # 6. HEART - Medium circularity, somewhat concave
            elif 0.40 < circularity < 0.75 and 0.70 < aspect_ratio < 1.40 and solidity < 0.88:
                if self.is_heart_shape(main_contour):
                    detected = "heart"
                    print(f"   [OK] Detected: HEART")
            
            # 7. THUMBS UP - Very vertical
            elif aspect_ratio < 0.60 and corners >= 6:
                detected = "thumbs_up"
                print(f"   [OK] Detected: THUMBS UP")
            
            if detected is None:
                print(f"   [X] No match found")
            
            return detected, center
            
        except Exception as e:
            print(f"[X] Error in detect_emoji_from_drawing: {e}")
            import traceback
            traceback.print_exc()
            return None, None
    
    def draw_emoji_popup(self, frame, emoji_key, position, fall_offset=0, alpha=1.0):
        """Gambar emoji popup dengan falling animation"""
        try:
            if emoji_key is None or position is None:
                return
            
            x, y_start = position
            y = y_start + fall_offset
            
            if y > frame.shape[0] + 200:
                return
            
            if emoji_key in self.emoji_images:
                emoji_img = self.emoji_images[emoji_key]
                emoji_size = 180  # Larger for 1920x1080
                self.overlay_png(frame, emoji_img, x, y, emoji_size, alpha=alpha)
            
        except Exception as e:
            print(f"[!] Error in draw_emoji_popup: {e}")
    
    def draw_text_with_shadow(self, frame, text, pos, font, scale, color, thickness):
        """Draw text with shadow for better readability"""
        x, y = pos
        # Shadow
        cv2.putText(frame, text, (x+3, y+3), font, scale, (0, 0, 0), thickness+2, cv2.LINE_AA)
        # Main text
        cv2.putText(frame, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)
    
    def draw_ui(self, frame):
        """Draw UI for 1920x1080 resolution"""
        try:
            h, w = frame.shape[:2]
            
            # Top-left: Simple status
            status = "DRAWING..." if self.drawing else f"Ready ({len(self.emoji_images)}/{len(EMOJI_PATTERNS)} emojis)"
            color = (0, 255, 255) if self.drawing else (0, 255, 100)
            self.draw_text_with_shadow(frame, status, (25, 50), 
                                       self.font, 1.0, color, 2)
            
            # Bottom-left: Instructions
            instructions = [
                "Pinch fingers = Draw",
                "Open hand = Detect",
                "H = Show/Hide hints",
                "C = Clear canvas",
                "Q = Quit"
            ]
            
            y_start = h - 180
            for i, inst in enumerate(instructions):
                self.draw_text_with_shadow(frame, inst, (25, y_start + i*35), 
                                          self.font, 0.7, (255, 255, 255), 1)
            
            # Top-right: Hints (if enabled)
            if self.show_hints:
                hint_x = w - 380
                hint_y = 40
                
                self.draw_text_with_shadow(frame, "DRAW THESE:", (hint_x, hint_y), 
                                          self.font, 0.8, (0, 255, 100), 2)
                
                y_offset = hint_y + 40
                for emoji_key, emoji_data in EMOJI_PATTERNS.items():
                    hint = f"{emoji_data['hint']} = {emoji_data['name']}"
                    color = (255, 255, 255) if emoji_key in self.emoji_images else (120, 120, 120)
                    self.draw_text_with_shadow(frame, hint, (hint_x, y_offset), 
                                              self.font, 0.65, color, 1)
                    y_offset += 35
                    
        except Exception as e:
            print(f"[!] Error in draw_ui: {e}")

def main():
    print("\n" + "=" * 70)
    print("[*] EMOJI DRAWER - Starting Application (1920x1080)")
    print("=" * 70)
    
    # Test camera access
    print("[*] Testing camera access...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[X] ERROR: Cannot access camera!")
        print("[!] Possible solutions:")
        print("    1. Check if camera is being used by another app")
        print("    2. Check camera permissions")
        print("    3. Try different camera index: cv2.VideoCapture(1)")
        return
    
    print("[OK] Camera accessed successfully!")
    
    # Set camera properties to 1920x1080
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Test read one frame
    ret, test_frame = cap.read()
    if not ret:
        print("[X] ERROR: Cannot read from camera!")
        cap.release()
        return
    
    print(f"[OK] Camera resolution: {test_frame.shape[1]}x{test_frame.shape[0]}")
    
    # Initialize drawer
    print("[*] Initializing emoji drawer...")
    try:
        drawer = EmojiDrawer()
    except Exception as e:
        print(f"[X] ERROR initializing drawer: {e}")
        import traceback
        traceback.print_exc()
        cap.release()
        return
    
    print("[OK] Emoji drawer initialized!")
    
    # Create window with specific size (windowed fullscreen)
    window_name = "Emoji Drawer - 1920x1080"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1920, 1080)
    
    print("\n[*] Starting main loop...")
    print("[*] Pinch fingers to draw, open hand to detect!")
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
                    print("[!] Failed to read frame")
                    break
                
                frame = cv2.flip(frame, 1)
                h, w, c = frame.shape
                
                # Initialize canvas
                if drawer.canvas is None:
                    drawer.canvas = np.zeros_like(frame)
                
                # Process hand
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)
                
                current_point = None
                
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    
                    # Draw hand skeleton
                    mp_draw.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        mp_hands.HAND_CONNECTIONS,
                        mp_draw.DrawingSpec(color=(0, 255, 100), thickness=3, circle_radius=3),
                        mp_draw.DrawingSpec(color=(0, 180, 255), thickness=2)
                    )
                    
                    # Get finger tips
                    index_tip = hand_landmarks.landmark[8]
                    thumb_tip = hand_landmarks.landmark[4]
                    
                    index_x = int(index_tip.x * w)
                    index_y = int(index_tip.y * h)
                    thumb_x = int(thumb_tip.x * w)
                    thumb_y = int(thumb_tip.y * h)
                    
                    # Distance between thumb and index
                    distance = math.sqrt((index_x - thumb_x)**2 + (index_y - thumb_y)**2)
                    
                    # Drawing mode (pinch)
                    if distance < 50:
                        drawer.drawing = True
                        
                        # Apply smoothing
                        raw_point = (index_x, index_y)
                        current_point = drawer.smooth_point(raw_point)
                        
                        if drawer.prev_point is not None:
                            smooth_points = drawer.smooth_line(drawer.prev_point, current_point)
                            for pt in smooth_points:
                                drawer.points.append(pt)
                                cv2.circle(drawer.canvas, pt, drawer.brush_size, 
                                         drawer.color, -1, lineType=cv2.LINE_AA)
                                cv2.circle(frame, pt, drawer.brush_size, 
                                         drawer.color, -1, lineType=cv2.LINE_AA)
                        
                        drawer.prev_point = current_point
                        
                        # Visual feedback
                        cv2.circle(frame, current_point, 20, (0, 255, 255), 3, cv2.LINE_AA)
                        cv2.circle(frame, current_point, 6, (0, 255, 255), -1, cv2.LINE_AA)
                    
                    else:
                        # Selesai drawing
                        if drawer.drawing and len(drawer.points) > 20:
                            print("\n[*] Analyzing drawing...")
                            emoji, position = drawer.detect_emoji_from_drawing(drawer.canvas)
                            if emoji:
                                drawer.detected_emoji = emoji
                                drawer.emoji_position = position
                                drawer.show_emoji_frames = 90
                                drawer.emoji_alpha = 1.0
                                print(f"[SUCCESS] Detected: {EMOJI_PATTERNS[emoji]['name']}")
                                
                                # CLEAR CANVAS IMMEDIATELY
                                drawer.canvas = np.zeros_like(frame)
                                drawer.points.clear()
                                print("[*] Canvas cleared!\n")
                            else:
                                print(f"[!] No emoji detected. Try drawing larger and clearer!\n")
                                # Auto clear
                                drawer.canvas = np.zeros_like(frame)
                                drawer.points.clear()
                        
                        drawer.drawing = False
                        drawer.prev_point = None
                        drawer.smoothed_points.clear()
                        
                        cv2.circle(frame, (index_x, index_y), 10, (255, 100, 100), 3, cv2.LINE_AA)
                        cv2.circle(frame, (index_x, index_y), 4, (255, 100, 100), -1, cv2.LINE_AA)
                
                else:
                    drawer.drawing = False
                    drawer.prev_point = None
                    drawer.smoothed_points.clear()
                
                # Merge canvas dengan frame
                frame = cv2.addWeighted(frame, 1, drawer.canvas, 0.7, 0)
                
                # Emoji popup animation
                if drawer.show_emoji_frames > 0:
                    total_frames = 90
                    progress = 1 - (drawer.show_emoji_frames / total_frames)
                    
                    fall_distance = int(progress * 350)
                    
                    if progress > 0.6:
                        fade_progress = (progress - 0.6) / 0.4
                        drawer.emoji_alpha = 1.0 - fade_progress
                    else:
                        drawer.emoji_alpha = 1.0
                    
                    drawer.draw_emoji_popup(frame, drawer.detected_emoji, 
                                          drawer.emoji_position, 
                                          fall_distance, drawer.emoji_alpha)
                    drawer.show_emoji_frames -= 1
                    
                    if drawer.show_emoji_frames == 0:
                        drawer.detected_emoji = None
                
                # Draw UI
                drawer.draw_ui(frame)
                
                # Show frame
                cv2.imshow(window_name, frame)
                
                # Keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n[*] Goodbye!\n")
                    break
                elif key == ord('h'):
                    drawer.show_hints = not drawer.show_hints
                elif key == ord('c'):
                    drawer.canvas = np.zeros_like(frame)
                    drawer.points.clear()
                    print("\n[*] Canvas cleared!\n")
    
    except KeyboardInterrupt:
        print("\n[*] Interrupted by user")
    except Exception as e:
        print(f"\n[X] ERROR in main loop: {e}")
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