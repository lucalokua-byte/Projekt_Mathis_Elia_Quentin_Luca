import cv2
import pytesseract
import numpy as np
import re
from PIL import Image

class PlateRecognizer:
    def __init__(self):
        self.setup_tesseract()
        
    def setup_tesseract(self):
        """Setup tesseract path if needed (Windows)"""
        try:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            pass
        except Exception as e:
            print(f"Tesseract setup warning: {e}")
    
    def preprocess_image(self, image):
        """Preprocess the image for better OCR results"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive threshold
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up the image
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel)
        
        return processed
    
    def detect_plate_region(self, image):
        """Detect potential license plate regions in the image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter to reduce noise while keeping edges sharp
        filtered = cv2.bilateralFilter(gray, 11, 17, 17)
        
        # Find edges
        edged = cv2.Canny(filtered, 30, 200)
        
        # Find contours
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
        
        plate_contours = []
        
        for contour in contours:
            # Approximate the contour
            epsilon = 0.018 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Look for rectangular contours
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / float(h)
                
                # Typical license plate aspect ratios (adjust based on your country)
                if 2.0 <= aspect_ratio <= 5.0 and w > 100 and h > 30:
                    plate_contours.append(approx)
        
        return plate_contours
    
    def extract_plate_text(self, plate_image):
        """Extract text from the plate region using OCR"""
        try:
            # Preprocess the plate image
            processed = self.preprocess_image(plate_image)
            
            # OCR configuration for license plates
            config = '--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            
            # Perform OCR
            text = pytesseract.image_to_string(processed, config=config)
            
            # Clean and validate the extracted text
            cleaned_text = self.clean_plate_text(text)
            
            return cleaned_text if cleaned_text else None
            
        except Exception as e:
            print(f"OCR Error: {e}")
            return None
    
    def clean_plate_text(self, text):
        """Clean and validate the extracted plate text"""
        if not text:
            return None
            
        # Remove unwanted characters and whitespace
        cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
        
        # Basic validation (adjust based on your country's plate format)
        if 4 <= len(cleaned) <= 10:  # Most plates have 4-10 characters
            return cleaned
        return None
    
    def recognize_from_frame(self, frame):
        """Main method to recognize license plates from a frame"""
        try:
            # Detect plate regions
            plate_contours = self.detect_plate_region(frame)
            
            results = []
            
            for contour in plate_contours:
                # Extract the plate region
                x, y, w, h = cv2.boundingRect(contour)
                plate_roi = frame[y:y+h, x:x+w]
                
                # Extract text from the plate
                plate_text = self.extract_plate_text(plate_roi)
                
                if plate_text:
                    results.append({
                        'text': plate_text,
                        'bbox': (x, y, w, h),
                        'confidence': 1.0  # You can add confidence scoring
                    })
            
            return results
            
        except Exception as e:
            print(f"Recognition error: {e}")
            return []