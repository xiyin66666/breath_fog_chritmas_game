"""
Image processing utility functions
"""
import cv2
import numpy as np

def resize_image(image, width=None, height=None):
    """
    Resize image
    
    Args:
        image: Input image
        width: Target width
        height: Target height
        
    Returns:
        Resized image
    """
    h, w = image.shape[:2]
    
    # If width and height not specified, return original
    if width is None and height is None:
        return image.copy()
    
    # If only width specified, calculate height to maintain aspect ratio
    if width is not None and height is None:
        ratio = width / w
        height = int(h * ratio)
    
    # If only height specified, calculate width to maintain aspect ratio
    elif height is not None and width is None:
        ratio = height / h
        width = int(w * ratio)
    
    # Resize
    resized = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    
    return resized

def overlay_image(background, foreground, x, y, alpha=1.0):
    """
    Overlay foreground image onto background image
    
    Args:
        background: Background image
        foreground: Foreground image
        x, y: Overlay position
        alpha: Foreground transparency (0.0 - 1.0)
        
    Returns:
        Overlaid image
    """
    bg = background.copy()
    fg = foreground.copy()
    
    # Get foreground image dimensions
    fg_h, fg_w = fg.shape[:2]
    bg_h, bg_w = bg.shape[:2]
    
    # Ensure overlay position is within background bounds
    x = max(0, min(bg_w - fg_w, x))
    y = max(0, min(bg_h - fg_h, y))
    
    # Extract region of interest
    roi = bg[y:y+fg_h, x:x+fg_w]
    
    # If foreground image has alpha channel
    if fg.shape[2] == 4:
        # Separate RGB and alpha channels
        fg_rgb = fg[:, :, :3]
        fg_alpha = fg[:, :, 3] / 255.0 * alpha
        
        # Apply alpha blending
        for c in range(3):
            roi[:, :, c] = roi[:, :, c] * (1 - fg_alpha) + fg_rgb[:, :, c] * fg_alpha
    else:
        # If no alpha channel, overlay directly
        if alpha < 1.0:
            roi = cv2.addWeighted(roi, 1 - alpha, fg, alpha, 0)
        else:
            roi = fg
    
    # Put processed region back into background
    bg[y:y+fg_h, x:x+fg_w] = roi
    
    return bg

def create_text_image(text, font_scale=1.0, font_color=(255, 255, 255), 
                     bg_color=(0, 0, 0, 0), thickness=2, font=cv2.FONT_HERSHEY_SIMPLEX):
    """
    Create text image
    
    Args:
        text: Text to display
        font_scale: Font size
        font_color: Font color (B, G, R)
        bg_color: Background color (B, G, R) or (B, G, R, A)
        thickness: Font thickness
        font: Font type
        
    Returns:
        Text image
    """
    # Get text size
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    
    # Create image
    if len(bg_color) == 4:
        # Has alpha channel
        img = np.zeros((text_size[1] + 20, text_size[0] + 20, 4), dtype=np.uint8)
        img[:, :, 0] = bg_color[0]
        img[:, :, 1] = bg_color[1]
        img[:, :, 2] = bg_color[2]
        img[:, :, 3] = bg_color[3]
    else:
        # No alpha channel
        img = np.zeros((text_size[1] + 20, text_size[0] + 20, 3), dtype=np.uint8)
        img[:, :] = bg_color
    
    # Draw text
    text_x = (img.shape[1] - text_size[0]) // 2
    text_y = (img.shape[0] + text_size[1]) // 2
    
    cv2.putText(img, text, (text_x, text_y), font, font_scale, font_color, thickness)
    
    return img

def adjust_brightness_contrast(image, brightness=0, contrast=0):
    """
    Adjust image brightness and contrast
    
    Args:
        image: Input image
        brightness: Brightness adjustment (-255 to 255)
        contrast: Contrast adjustment (-255 to 255)
        
    Returns:
        Adjusted image
    """
    # Adjust brightness
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        
        alpha_b = (highlight - shadow) / 255
        gamma_b = shadow
        
        image = cv2.addWeighted(image, alpha_b, image, 0, gamma_b)
    
    # Adjust contrast
    if contrast != 0:
        f = 131 * (contrast + 127) / (127 * (131 - contrast))
        alpha_c = f
        gamma_c = 127 * (1 - f)
        
        image = cv2.addWeighted(image, alpha_c, image, 0, gamma_c)
    
    return image