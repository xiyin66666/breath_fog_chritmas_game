"""
Fog effect module
Generate and apply fog effects with erase functionality
"""
import cv2
import numpy as np
import random

class FogEffect:
    def __init__(self, width=1280, height=720):
        """Initialize fog effect"""
        self.width = width
        self.height = height
        
        # Fog texture
        self.fog_texture = None
        
        # Fog transparency layer
        self.fog_alpha = None
        
        # Initialize fog
        self.reset()
        
        # Erase parameters
        self.erase_radius = 80  # Erase radius
        self.erase_strength = 0.08  # Erase strength per frame
    
    def reset(self):
        """Reset fog effect"""
        # Create initial fog texture
        self.fog_texture = self.generate_fog_texture()
        
        # Create transparency layer (0 = fully transparent, 255 = fully opaque)
        self.fog_alpha = np.zeros((self.height, self.width), dtype=np.uint8)
        
        # Current fog level
        self.current_fog_level = 0.0
    
    def generate_fog_texture(self):
        """Generate fog texture"""
        # Create base fog texture (white with transparency effect)
        fog = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255
        
        # Add some random noise to simulate uneven fog
        noise = np.random.randint(200, 255, (self.height, self.width, 1), dtype=np.uint8)
        noise = np.repeat(noise, 3, axis=2)
        
        # Blend noise
        fog = cv2.addWeighted(fog, 0.7, noise, 0.3, 0)
        
        # Apply Gaussian blur for more natural fog
        fog = cv2.GaussianBlur(fog, (21, 21), 0)
        
        return fog
    
    def apply_fog(self, frame, fog_level):
        """
        Apply fog to image
        
        Args:
            frame: Input image frame
            fog_level: Fog level (0.0 - 1.0)
            
        Returns:
            Image with fog applied
        """
        self.current_fog_level = max(0.0, min(1.0, fog_level))
        
        # If fog level is 0, return original image
        if self.current_fog_level <= 0.0:
            return frame.copy()
        
        # Update fog transparency layer
        alpha_value = int(200 * self.current_fog_level)  # Max alpha 200 (not 255, keep some visibility)
        self.fog_alpha.fill(alpha_value)
        
        # Create fog image
        fog_img = self.fog_texture.copy()
        
        # Apply transparency
        fog_bgra = cv2.cvtColor(fog_img, cv2.COLOR_BGR2BGRA)
        fog_bgra[:, :, 3] = self.fog_alpha
        
        # Overlay fog onto original image
        result = frame.copy()
        
        # Create fog mask
        fog_mask = self.fog_alpha / 255.0
        
        # Apply fog effect
        for c in range(3):
            result[:, :, c] = result[:, :, c] * (1 - fog_mask) + fog_img[:, :, c] * fog_mask
        
        return result.astype(np.uint8)
    
    def clear_fog(self, frame, hand_positions):
        """
        Clear fog based on hand positions
        
        Args:
            frame: Current image frame (with fog applied)
            hand_positions: List of hand positions, each element is (center_x, center_y, radius)
            
        Returns:
            Image with fog cleared
        """
        if self.current_fog_level <= 0.0:
            return frame
        
        # Create a copy of the current frame
        result = frame.copy()
        
        # Create erase regions for each hand position
        for hand_pos in hand_positions:
            if len(hand_pos) >= 2:
                center_x, center_y = int(hand_pos[0]), int(hand_pos[1])
                radius = self.erase_radius
                
                # Ensure coordinates are within image bounds
                center_x = max(radius, min(self.width - radius, center_x))
                center_y = max(radius, min(self.height - radius, center_y))
                
                # Create circular mask
                y, x = np.ogrid[-radius:radius+1, -radius:radius+1]
                mask = x**2 + y**2 <= radius**2
                
                # Calculate erase region
                y_start = center_y - radius
                y_end = center_y + radius + 1
                x_start = center_x - radius
                x_end = center_x + radius + 1
                
                # Ensure indices are within bounds
                y_start = max(0, y_start)
                y_end = min(self.height, y_end)
                x_start = max(0, x_start)
                x_end = min(self.width, x_end)
                
                # Adjust mask size to match actual region
                mask_height = y_end - y_start
                mask_width = x_end - x_start
                if mask_height > 0 and mask_width > 0:
                    mask = mask[:mask_height, :mask_width]
                    
                    # Reduce transparency in fog alpha layer
                    for i in range(mask_height):
                        for j in range(mask_width):
                            if mask[i, j]:
                                current_alpha = self.fog_alpha[y_start + i, x_start + j]
                                new_alpha = max(0, int(current_alpha * (1 - self.erase_strength)))
                                self.fog_alpha[y_start + i, x_start + j] = new_alpha
        
        # Update current fog level
        self.current_fog_level = np.mean(self.fog_alpha) / 200.0  # 200 is max alpha value
        
        # Re-apply fog effect with updated alpha
        fog_img = self.fog_texture.copy()
        fog_mask = self.fog_alpha / 255.0
        
        # Apply updated fog
        for c in range(3):
            result[:, :, c] = result[:, :, c] * (1 - fog_mask) + fog_img[:, :, c] * fog_mask
        
        return result.astype(np.uint8)
    
    def get_fog_level(self):
        """Get current fog level"""
        return self.current_fog_level
    
    def is_fully_cleared(self):
        """Check if fog is completely cleared"""
        return self.current_fog_level <= 0.01