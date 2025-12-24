"""
Breath Fog Game - Main Program
Use camera to detect mouth shape and hand gestures for interaction
"""
import cv2
import numpy as np
import sys
import os

from modules.face_detector import FaceDetector
from modules.hand_detector import HandDetector
from modules.fog_effect import FogEffect
from modules.game_logic import GameLogic
from utils.audio_player import AudioPlayer

class BreathFogGame:
    def __init__(self):
        """Initialize game"""
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Cannot open camera")
            sys.exit(1)
        
        # Set camera resolution to 1280x720 for larger display
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 680)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 340)
        
        # Get actual resolution
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Camera resolution: {self.width}x{self.height}")
        
        # Initialize modules
        self.face_detector = FaceDetector()
        self.hand_detector = HandDetector()
        self.fog_effect = FogEffect(self.width, self.height)
        self.game_logic = GameLogic()
        self.audio_player = AudioPlayer()
        
        # Load resources
        self.tree_image = self.load_tree_image()
        
        # Game state display
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
    def load_tree_image(self):
        """Load Christmas tree image"""
        tree_path = os.path.join("assets", "tree.png")
        if not os.path.exists(tree_path):
            print(f"Warning: Cannot find tree image {tree_path}")
            # Create a placeholder tree image
            tree_img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            cv2.putText(tree_img, "Christmas Tree", (self.width//2-100, self.height//2), 
                       self.font, 1, (0, 255, 0), 2)
            cv2.putText(tree_img, "Placeholder - Please add tree.png to assets folder", 
                       (self.width//2-200, self.height//2+40), self.font, 0.6, (255, 255, 255), 1)
            return tree_img
        
        # Use PIL to load image and convert to OpenCV format
        from PIL import Image
        pil_img = Image.open(tree_path)
        pil_img = pil_img.convert("RGB")
        
        # Resize image to fit screen
        pil_img = pil_img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        
        # Convert to OpenCV format
        tree_img = np.array(pil_img)
        tree_img = cv2.cvtColor(tree_img, cv2.COLOR_RGB2BGR)
        
        return tree_img
    
    def display_ui(self, frame, mouth_ratio=None, fog_level=None, state=None):
        """Display user interface on the frame"""
        # # Display game title
        # cv2.putText(frame, "Breath Fog Treasure Game", (10, 30), 
        #            self.font, 0.9, (255, 255, 255), 2)
        
        status_text = f"State: {state}"
        # Display operation hints
        if state == "WAITING":
            hint_text = "Make 'O' shape with your mouth"
            cv2.putText(frame, hint_text, (self.width//2-180, 40), 
                       self.font, 0.8, (0, 255, 0), 2)
        elif state == "FOG_COVERING":
            hint_text = "Fog is covering..."
            cv2.putText(frame, hint_text, (self.width//2-120, 40), 
                       self.font, 0.8, (255, 255, 0), 2)
        elif state == "FOG_CLEARING":
            hint_text = "Use your hand to clear fog"
            cv2.putText(frame, hint_text, (self.width//2-150, 40), 
                       self.font, 0.8, (0, 255, 255), 2)
        elif state == "TREE_REVEALED":
            hint_text = "Congratulations! Found Christmas Tree!"
            cv2.putText(frame, hint_text, (self.width//2-250, 40), 
                       self.font, 0.8, (0, 0, 255), 2)
        
        # Display exit hint
        cv2.putText(frame, "Press 'q' to quit", (10, self.height-20), 
                   self.font, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "Press 'r' to reset", (10, self.height-50), 
                   self.font, 0.7, (255, 255, 255), 2)
        
        return frame
    
    def show_christmas_tree(self, frame):
        """Display Christmas tree"""
        # Blend tree image with current frame
        alpha = 0.8  # Tree transparency
        beta = 1.0 - alpha
        
        # Ensure tree image size matches frame
        if self.tree_image.shape[:2] != frame.shape[:2]:
            self.tree_image = cv2.resize(self.tree_image, (frame.shape[1], frame.shape[0]))
        
        # Blend images
        blended = cv2.addWeighted(frame, beta, self.tree_image, alpha, 0)
        
        return blended
    
    def run(self):
        """Run main game loop"""
        print("Starting game...")
        print("Face the camera and make 'O' shape with your mouth to start")
        print("Press 'q' to quit, 'r' to reset")
        
        while True:
            # Read camera frame
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Cannot read camera frame")
                break
            
            # Flip frame horizontally (mirror effect)
            frame = cv2.flip(frame, 1)
            
            # Detect mouth shape
            mouth_ratio, mouth_is_o = self.face_detector.detect_mouth_shape(frame)
            
            # Detect hands
            hands_detected, hand_positions = self.hand_detector.detect_hands(frame)
            
            # Update game state
            state, fog_level = self.game_logic.update(mouth_is_o, hands_detected, hand_positions)
            
            # Apply game effects
            if state == "FOG_COVERING" or state == "FOG_CLEARING":
                # Apply fog effect
                frame = self.fog_effect.apply_fog(frame, fog_level)
                
                # Clear fog if hands detected
                if hands_detected and state == "FOG_CLEARING":
                    frame = self.fog_effect.clear_fog(frame, hand_positions)
            
            # Show Christmas tree and play music
            if state == "TREE_REVEALED":
                frame = self.show_christmas_tree(frame)
                
                # Play music (if not already playing)
                if not self.audio_player.is_playing():
                    music_path = os.path.join("assets", "music.mp3")
                    self.audio_player.play(music_path)
            
            # Display user interface
            frame = self.display_ui(frame, mouth_ratio, fog_level, state)
            
            # Show frame
            cv2.imshow('Breath Fog Treasure Game', frame)
            
            # Check keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):  # Reset game
                self.game_logic.reset()
                self.fog_effect.reset()
                self.audio_player.stop()
                print("Game reset")
        
        # Clean up resources
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("Exiting game...")
        self.cap.release()
        cv2.destroyAllWindows()
        self.audio_player.stop()
        print("Game exited")

if __name__ == "__main__":
    game = BreathFogGame()
    game.run()