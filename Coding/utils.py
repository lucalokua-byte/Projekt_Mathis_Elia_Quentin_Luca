import cv2
import time
from datetime import datetime

class PlateLogger:
    def __init__(self, log_file="detected_plates.log"):
        self.log_file = log_file
    
    def log_plate(self, plate_text, confidence=1.0):
        """Log detected plates with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - Plate: {plate_text} - Confidence: {confidence}\n"
        
        with open(self.log_file, "a") as f:
            f.write(log_entry)
        print(f"Logged: {log_entry.strip()}")

def draw_detection_results(frame, results):
    """Draw bounding boxes and text on the frame"""
    for result in results:
        x, y, w, h = result['bbox']
        text = result['text']
        
        # Draw bounding box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Draw text background
        cv2.rectangle(frame, (x, y - 30), (x + w, y), (0, 255, 0), -1)
        
        # Draw plate text
        cv2.putText(frame, text, (x, y - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    
    return frame

# Zusätzliche Hilfsfunktionen die nützlich sein könnten:

def save_frame_with_timestamp(frame, prefix="capture"):
    """Save frame with timestamp"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.jpg"
    cv2.imwrite(filename, frame)
    print(f"Frame saved as {filename}")
    return filename

def resize_frame(frame, width=None, height=None):
    """Resize frame while maintaining aspect ratio"""
    if width is None and height is None:
        return frame
    
    h, w = frame.shape[:2]
    
    if width is not None and height is not None:
        return cv2.resize(frame, (width, height))
    elif width is not None:
        ratio = width / float(w)
        height = int(h * ratio)
        return cv2.resize(frame, (width, height))
    else:  # height is not None
        ratio = height / float(h)
        width = int(w * ratio)
        return cv2.resize(frame, (width, height))

def check_camera_connection(camera_id=0):
    """Check if camera is accessible"""
    cap = cv2.VideoCapture(camera_id)
    if cap.isOpened():
        ret, frame = cap.read()
        cap.release()
        return ret and frame is not None
    return False