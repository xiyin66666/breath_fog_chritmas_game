"""
Hand detection module
Using MediaPipe to detect hand landmarks
"""
import cv2
import numpy as np

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("Warning: mediapipe not installed, hand detection will be limited")

class HandDetector:
    def __init__(self, mode=False, max_hands=2, detection_confidence=0.5, tracking_confidence=0.5):
        """Initialize hand detector"""
        self.mp_hands = None
        self.hands = None
        
        # Hand landmark indices
        self.WRIST = 0
        self.THUMB_CMC = 1
        self.THUMB_MCP = 2
        self.THUMB_IP = 3
        self.THUMB_TIP = 4
        self.INDEX_FINGER_MCP = 5
        self.INDEX_FINGER_PIP = 6
        self.INDEX_FINGER_DIP = 7
        self.INDEX_FINGER_TIP = 8
        self.MIDDLE_FINGER_MCP = 9
        self.MIDDLE_FINGER_PIP = 10
        self.MIDDLE_FINGER_DIP = 11
        self.MIDDLE_FINGER_TIP = 12
        self.RING_FINGER_MCP = 13
        self.RING_FINGER_PIP = 14
        self.RING_FINGER_DIP = 15
        self.RING_FINGER_TIP = 16
        self.PINKY_MCP = 17
        self.PINKY_PIP = 18
        self.PINKY_DIP = 19
        self.PINKY_TIP = 20
        
        # Use backup method if mediapipe not available
        if not MEDIAPIPE_AVAILABLE:
            print("Using backup hand detection method (based on color and contour)")
            self.use_backup_method = True
        else:
            self.use_backup_method = False
            self.initialize_mediapipe(mode, max_hands, detection_confidence, tracking_confidence)
    
    def initialize_mediapipe(self, mode, max_hands, detection_confidence, tracking_confidence):
        """Initialize MediaPipe hand detection"""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=mode,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
    
    def detect_hands(self, frame):
        """
        Detect hands in image
        
        Args:
            frame: Input image frame
            
        Returns:
            hands_detected: Whether hands are detected
            hand_positions: List of hand positions, each element is (center_x, center_y, radius)
        """
        if not self.use_backup_method:
            return self.detect_hands_mediapipe(frame)
        else:
            return self.detect_hands_backup(frame)
    
    def detect_hands_mediapipe(self, frame):
        """Detect hands using MediaPipe"""
        if self.hands is None:
            return False, []
        
        # Convert color space
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process image
        results = self.hands.process(rgb_frame)
        
        hands_detected = False
        hand_positions = []
        
        if results.multi_hand_landmarks:
            hands_detected = True
            
            for hand_landmarks in results.multi_hand_landmarks:
                # Get image dimensions
                h, w, _ = frame.shape
                
                # Calculate hand bounding box
                x_coords = [landmark.x * w for landmark in hand_landmarks.landmark]
                y_coords = [landmark.y * h for landmark in hand_landmarks.landmark]
                
                x_min, x_max = int(min(x_coords)), int(max(x_coords))
                y_min, y_max = int(min(y_coords)), int(max(y_coords))
                
                # Calculate hand center and radius
                center_x = (x_min + x_max) // 2
                center_y = (y_min + y_max) // 2
                radius = max((x_max - x_min) // 2, (y_max - y_min) // 2)
                
                hand_positions.append((center_x, center_y, radius))
        
        return hands_detected, hand_positions
    
    def detect_hands_backup(self, frame):
        """Backup method: Detect hands using color and contour"""
        # Convert to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define skin color range (may need adjustment based on lighting)
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Create skin color mask
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Morphological operations to enhance mask
        kernel = np.ones((5, 5), np.uint8)
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        hands_detected = False
        hand_positions = []
        
        if contours:
            # Filter out too small contours
            large_contours = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # Area threshold
                    large_contours.append(contour)
            
            if large_contours:
                hands_detected = True
                
                for contour in large_contours:
                    # Calculate bounding rectangle of contour
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Calculate center and radius
                    center_x = x + w // 2
                    center_y = y + h // 2
                    radius = max(w, h) // 2
                    
                    hand_positions.append((center_x, center_y, radius))
        
        return hands_detected, hand_positions