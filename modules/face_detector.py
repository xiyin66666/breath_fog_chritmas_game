"""
Face and mouth shape detection module
Using MediaPipe to detect facial landmarks and recognize 'O' mouth shape
"""
import cv2
import numpy as np

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("Warning: mediapipe not installed, mouth detection will be limited")

class FaceDetector:
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """Initialize face detector"""
        self.mp_face_mesh = None
        self.face_mesh = None
        
        # Mouth landmark indices (MediaPipe Face Mesh)
        self.LIPS = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]
        self.OUTER_LIPS = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291]
        self.INNER_LIPS = [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308]
        
        # Key points for calculating mouth aspect ratio
        self.MOUTH_HORIZONTAL = [61, 291]  # Left and right mouth corners
        self.MOUTH_VERTICAL = [13, 14]     # Upper and lower lips
        
        # Mouth shape detection parameters
        # LOWERED THRESHOLD: Reduced from 0.4 to 0.15 for easier detection
        self.mouth_ratio_threshold = 0.15   # Threshold for 'O' mouth shape
        self.mouth_ratio_history = []      # History for smoothing
        self.history_max_len = 5
        
        # Use backup method if mediapipe not available
        if not MEDIAPIPE_AVAILABLE:
            print("Using backup mouth detection method (based on color and contour)")
            self.use_backup_method = True
        else:
            self.use_backup_method = False
            self.initialize_mediapipe(min_detection_confidence, min_tracking_confidence)
    
    def initialize_mediapipe(self, min_detection_confidence, min_tracking_confidence):
        """Initialize MediaPipe face mesh"""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
    
    def detect_mouth_shape(self, frame):
        """
        Detect mouth shape and determine if it's 'O' shape
        
        Args:
            frame: Input image frame
            
        Returns:
            mouth_ratio: Mouth aspect ratio
            is_o_shape: Whether it's 'O' shape
        """
        if not self.use_backup_method:
            return self.detect_mouth_shape_mediapipe(frame)
        else:
            return self.detect_mouth_shape_backup(frame)
    
    def detect_mouth_shape_mediapipe(self, frame):
        """Detect mouth shape using MediaPipe"""
        if self.face_mesh is None:
            return 0.0, False
        
        # Convert color space
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process image
        results = self.face_mesh.process(rgb_frame)
        
        mouth_ratio = 0.0
        is_o_shape = False
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Get image dimensions
                h, w, _ = frame.shape
                
                # Extract mouth key point coordinates
                mouth_points = []
                for idx in self.MOUTH_HORIZONTAL + self.MOUTH_VERTICAL:
                    landmark = face_landmarks.landmark[idx]
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    mouth_points.append((x, y))
                
                # Calculate mouth width and height
                if len(mouth_points) >= 4:
                    # Width between left and right mouth corners
                    left_corner = mouth_points[0]
                    right_corner = mouth_points[1]
                    mouth_width = np.linalg.norm(np.array(left_corner) - np.array(right_corner))
                    
                    # Height between upper and lower lips
                    upper_lip = mouth_points[2]
                    lower_lip = mouth_points[3]
                    mouth_height = np.linalg.norm(np.array(upper_lip) - np.array(lower_lip))
                    
                    # Calculate mouth aspect ratio
                    if mouth_width > 0:
                        mouth_ratio = mouth_height / mouth_width
                    else:
                        mouth_ratio = 0.0
                    
                    # Smoothing
                    self.mouth_ratio_history.append(mouth_ratio)
                    if len(self.mouth_ratio_history) > self.history_max_len:
                        self.mouth_ratio_history.pop(0)
                    
                    smoothed_ratio = np.mean(self.mouth_ratio_history) if self.mouth_ratio_history else mouth_ratio
                    
                    # Determine if it's 'O' shape
                    is_o_shape = smoothed_ratio > self.mouth_ratio_threshold
                    
                    return smoothed_ratio, is_o_shape
        
        return 0.0, False
    
    def detect_mouth_shape_backup(self, frame):
        """Backup method: Detect mouth shape using color and contour"""
        # Convert to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define lip color range (red/pink)
        lower_lip = np.array([0, 30, 30])
        upper_lip = np.array([20, 255, 255])
        
        # Create lip color mask
        lip_mask = cv2.inRange(hsv, lower_lip, upper_lip)
        
        # Morphological operations to enhance mask
        kernel = np.ones((5, 5), np.uint8)
        lip_mask = cv2.morphologyEx(lip_mask, cv2.MORPH_CLOSE, kernel)
        lip_mask = cv2.morphologyEx(lip_mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(lip_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Find largest contour (likely mouth)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Calculate bounding rectangle of contour
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Calculate aspect ratio
            if w > 0:
                mouth_ratio = h / w
            else:
                mouth_ratio = 0.0
            
            # Determine if it's 'O' shape (higher aspect ratio)
            is_o_shape = mouth_ratio > 0.25 and w > 30 and h > 10
            
            return mouth_ratio, is_o_shape
        
        return 0.0, False