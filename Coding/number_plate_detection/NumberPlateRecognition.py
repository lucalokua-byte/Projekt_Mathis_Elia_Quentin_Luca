import cv2
import pytesseract
import numpy as np
import re
from typing import List, Dict, Any
from .NumberPlateDetection_Interface import NumberPlateDetection

class BasicPlateRecognizer(NumberPlateDetection):
    """
    Implementation of NumberPlateDetection interface
    """
    
    def __init__(self):
        self._initialized = False
        self.confidence_threshold = 0.5
        self.min_plate_length = 6
        self.max_plate_length = 8
        
    def setup(self) -> bool:
        """Initialize the detection system"""
        try:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            self._initialized = True
            print("✅ Plate recognizer initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Plate recognizer setup failed: {e}")
            return False
    
    def preprocess_image(self, image) -> Any:
        """Preprocess image for better detection - INTERFACE METHOD"""
        # This is the interface method, we'll use the enhanced version internally
        return self.preprocess_plate_image(image)
    
    def preprocess_plate_image(self, plate_image):
        """Enhanced preprocessing specifically for license plates"""
        try:
            # Resize image to make text more readable
            height, width = plate_image.shape[:2]
            if width < 200:
                scale = 300 / width
                new_width = 300
                new_height = int(height * scale)
                plate_image = cv2.resize(plate_image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # Convert to grayscale
            gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
            
            # Apply CLAHE for contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            contrast_enhanced = clahe.apply(gray)
            
            # Apply bilateral filter to reduce noise while keeping edges sharp
            filtered = cv2.bilateralFilter(contrast_enhanced, 11, 17, 17)
            
            # Use adaptive threshold for better character separation
            thresh = cv2.adaptiveThreshold(
                filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations to clean up the image
            kernel = np.ones((2,1), np.uint8)
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            kernel = np.ones((1,2), np.uint8)
            processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel)
            
            return processed
            
        except Exception as e:
            print(f"Preprocessing error: {e}")
            return plate_image
    
    def detect_plate_regions(self, image) -> List[Any]:
        """Detect potential plate regions in image - INTERFACE METHOD"""
        if not self._initialized:
            if not self.setup():
                return []
            
        try:
            # Method 1: Look for rectangular regions with specific aspect ratios
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply bilateral filter
            filtered = cv2.bilateralFilter(gray, 11, 17, 17)
            
            # Find edges
            edged = cv2.Canny(filtered, 50, 200)
            
            # Find contours
            contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:20]  # Check top 20
            
            plate_contours = []
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 1000 or area > 30000:  # Reasonable plate size range
                    continue
                    
                perimeter = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
                
                # Look for rectangular shapes (4 sides)
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / float(h)
                    
                    # Standard license plate aspect ratios (2:1 to 5:1)
                    if 2.0 <= aspect_ratio <= 5.0 and w > 100 and h > 30:
                        plate_contours.append(contour)
            
            # Method 2: Look for bright regions (license plates are often reflective)
            if not plate_contours:
                bright_regions = self.find_bright_regions(image)
                plate_contours.extend(bright_regions)
            
            return plate_contours
            
        except Exception as e:
            print(f"Plate detection error: {e}")
            return []
    
    def find_bright_regions(self, image):
        """Find bright regions that could be license plates"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Threshold to find bright regions
        _, bright_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Morphological operations to clean up
        kernel = np.ones((5,5), np.uint8)
        bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_CLOSE, kernel)
        bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        plate_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 500 < area < 20000:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / float(h)
                if 1.5 <= aspect_ratio <= 5.0:
                    plate_contours.append(contour)
        
        return plate_contours
    
    def extract_plate_text(self, plate_image) -> str:
        """Extract text from plate region - INTERFACE METHOD"""
        text, confidence = self.extract_plate_text_with_confidence(plate_image)
        return text
    
    def extract_plate_text_with_confidence(self, plate_image) -> tuple:
        """Enhanced OCR with multiple attempts and validation"""
        if not self._initialized:
            if not self.setup():
                return "", 0
            
        try:
            # Preprocess the plate image specifically for OCR
            processed = self.preprocess_plate_image(plate_image)
            
            # Try multiple OCR configurations for license plates
            configs = [
                '--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                '--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                '--oem 3 --psm 13 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
            ]
            
            best_text = ""
            best_confidence = 0
            
            for config in configs:
                try:
                    # Get detailed OCR data
                    ocr_data = pytesseract.image_to_data(processed, config=config, output_type=pytesseract.Output.DICT)
                    
                    # Extract text from high-confidence detections only
                    text_parts = []
                    confidences = []
                    
                    for i in range(len(ocr_data['text'])):
                        text = ocr_data['text'][i].strip()
                        conf = int(ocr_data['conf'][i])
                        
                        # Only consider high-confidence characters
                        if text and conf > 60:  # Increased threshold
                            text_parts.append(text)
                            confidences.append(conf)
                    
                    if text_parts:
                        current_text = ''.join(text_parts)
                        avg_confidence = sum(confidences) / len(confidences) / 100.0
                        
                        # Validate plate format
                        cleaned_text = self.validate_plate_format(current_text)
                        
                        if cleaned_text and avg_confidence > best_confidence:
                            best_confidence = avg_confidence
                            best_text = cleaned_text
                            
                except Exception as e:
                    continue
            
            if best_text:
                print(f"🔍 PLATE DETECTED: '{best_text}' (confidence: {best_confidence:.2f})")
                return best_text, best_confidence
            else:
                return "", 0
            
        except Exception as e:
            print(f"OCR Error: {e}")
            return "", 0
    
    def validate_plate_format(self, text):
        """Validate if text looks like a real license plate"""
        if not text:
            return None
            
        # Clean the text
        cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
        
        # Check length
        if len(cleaned) < self.min_plate_length or len(cleaned) > self.max_plate_length:
            return None
        
        # Check for reasonable mix of letters and numbers
        letter_count = sum(1 for c in cleaned if c.isalpha())
        digit_count = sum(1 for c in cleaned if c.isdigit())
        
        # Most plates have at least 2 letters and 2 numbers
        if letter_count < 2 or digit_count < 2:
            return None
        
        # Check for common plate patterns (adjust for your country)
        # Example: KY75OBH would be 2 letters, 2 numbers, 3 letters
        if len(cleaned) == 7:
            # Check if it matches common patterns like AB12CDE or ABC1234
            pattern1 = re.match(r'^[A-Z]{2}\d{2}[A-Z]{3}$', cleaned)  # KY75OBH
            pattern2 = re.match(r'^[A-Z]{3}\d{4}$', cleaned)          # ABC1234
            pattern3 = re.match(r'^\d{2}[A-Z]{3}\d{2}$', cleaned)     # 12ABC34
            
            if pattern1 or pattern2 or pattern3:
                return cleaned
        
        # For other lengths, use more lenient validation
        elif 6 <= len(cleaned) <= 8:
            # At least 2 letters and 2 numbers in any order
            return cleaned
        
        return None
    
    def clean_plate_text(self, text):
        """Clean and validate the extracted plate text"""
        if not text:
            return None
        cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
        
        # Basic validation
        if (self.min_plate_length <= len(cleaned) <= self.max_plate_length and 
            self.has_valid_format(cleaned)):
            return cleaned
        return None
    
    def has_valid_format(self, text):
        """Check if plate text has a valid format"""
        if len(text) < 6:
            return False
            
        # Count letters and numbers
        letter_count = sum(1 for c in text if c.isalpha())
        digit_count = sum(1 for c in text if c.isdigit())
        
        # Must have reasonable mix of letters and numbers
        return letter_count >= 2 and digit_count >= 2
    
    def recognize_from_frame(self, frame) -> List[Dict[str, Any]]:
        """Main method to recognize license plates from frame - INTERFACE METHOD"""
        if not self._initialized:
            if not self.setup():
                return []
        
        try:
            # Detect proper plate regions
            plate_contours = self.detect_plate_regions(frame)
            
            if not plate_contours:
                return []
            
            results = []
            
            for i, contour in enumerate(plate_contours[:3]):  # Process max 3 regions
                x, y, w, h = cv2.boundingRect(contour)
                
                # Additional validation of plate region
                if w < 80 or h < 25 or w/h < 1.8 or w/h > 5.5:
                    continue
                
                # Extract plate region with padding
                padding = 5
                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(frame.shape[1], x + w + padding)
                y2 = min(frame.shape[0], y + h + padding)
                
                plate_roi = frame[y1:y2, x1:x2]
                
                # Only process if region is reasonable
                if plate_roi.size == 0 or plate_roi.shape[0] < 20 or plate_roi.shape[1] < 50:
                    continue
                
                # Extract text with enhanced OCR
                plate_text, confidence = self.extract_plate_text_with_confidence(plate_roi)
                
                if plate_text and confidence >= self.confidence_threshold:
                    results.append({
                        'text': plate_text,
                        'bbox': (x, y, w, h),
                        'confidence': confidence
                    })
                    
                    # Draw visual feedback
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, plate_text, (x, y-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"{confidence:.2f}", (x, y+h+20), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            return results
            
        except Exception as e:
            print(f"Recognition error: {e}")
            return []
    
    def cleanup(self):
        """Cleanup resources - INTERFACE METHOD"""
        self._initialized = False
        print("Plate recognizer cleaned up")

# Backward compatibility - alias
PlateRecognizer = BasicPlateRecognizer