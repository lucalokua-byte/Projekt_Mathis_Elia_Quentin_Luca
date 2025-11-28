# import cv2
# import pytesseract
# import os
# import re
# import time

# class NumberPlateRecognizer:
#     def __init__(self, confidence_threshold=0.7, min_plate_length=4, max_plate_length=10):
#         self.current_dir = os.path.dirname(os.path.abspath(__file__))
#         self.harcascade = os.path.join(self.current_dir, "haarcascade_russian_plate_number.xml")
#         self.min_area = 500
#         self.cap = None
#         self.plate_detector = None
        
#         # Confidence settings
#         self.confidence_threshold = confidence_threshold
#         self.min_plate_length = min_plate_length
#         self.max_plate_length = max_plate_length
        
#         # Store confirmed plates
#         self.confirmed_plates = {}
#         self.confirmation_count_threshold = 3
        
#         # Exit control
#         self.should_exit = False
#         self.final_confirmed_plate = None
        
#         # Set Tesseract path
#         pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
        
#     def initialize_camera(self):
#         """Initialize the camera"""
#         self.cap = cv2.VideoCapture(0)
#         if not self.cap.isOpened():
#             print("Error: Could not open camera")
#             return False
#         return True
    
#     def load_haar_cascade(self):
#         """Load the Haar cascade classifier"""
#         if not os.path.exists(self.harcascade):
#             print(f"Error: Haar Cascade file not found: {self.harcascade}")
#             return False
            
#         self.plate_detector = cv2.CascadeClassifier(self.harcascade)
        
#         if self.plate_detector.empty():
#             print("Error: Haar Cascade could not be loaded")
#             return False
            
#         return True
    
#     def calculate_text_confidence(self, plate_img_thresh):
#         """Calculate confidence level of OCR result"""
#         ocr_data = pytesseract.image_to_data(plate_img_thresh, output_type=pytesseract.Output.DICT, config='--psm 7')
        
#         total_confidence = 0
#         valid_chars = 0
        
#         for i, text in enumerate(ocr_data['text']):
#             confidence = ocr_data['conf'][i]
#             text = text.strip()
            
#             if text and confidence > 30 and text.isalnum():
#                 total_confidence += confidence
#                 valid_chars += 1
        
#         if valid_chars > 0:
#             avg_confidence = total_confidence / valid_chars
#             normalized_confidence = min(avg_confidence / 100.0, 1.0)
#             return normalized_confidence, ocr_data
#         else:
#             return 0.0, ocr_data
    
#     def is_valid_plate_format(self, text):
#         """Check if the detected text matches typical license plate patterns"""
#         if not text:
#             return False
            
#         if len(text) < self.min_plate_length or len(text) > self.max_plate_length:
#             return False
        
#         patterns = [
#             r'^[A-Z0-9]{4,8}$',
#             r'^[A-Z]{2,3}\d{1,4}$',
#             r'^\d{1,4}[A-Z]{2,3}$',
#             r'^[A-Z]\d{1,3}[A-Z]{1,3}$',
#         ]
        
#         for pattern in patterns:
#             if re.match(pattern, text, re.IGNORECASE):
#                 return True
                
#         return False
    
#     def track_plate_confirmation(self, plate_text, confidence):
#         """Track and confirm plates over multiple detections"""
#         if confidence < self.confidence_threshold or not self.is_valid_plate_format(plate_text):
#             return False, confidence
        
#         # Update confirmation tracking
#         if plate_text in self.confirmed_plates:
#             self.confirmed_plates[plate_text]['count'] += 1
#             self.confirmed_plates[plate_text]['last_confidence'] = confidence
#             self.confirmed_plates[plate_text]['max_confidence'] = max(
#                 self.confirmed_plates[plate_text]['max_confidence'], confidence
#             )
#         else:
#             self.confirmed_plates[plate_text] = {
#                 'count': 1,
#                 'last_confidence': confidence,
#                 'max_confidence': confidence
#             }
        
#         # Check if plate is confirmed
#         if self.confirmed_plates[plate_text]['count'] >= self.confirmation_count_threshold:
#             return True, self.confirmed_plates[plate_text]['max_confidence']
        
#         return False, confidence
    
#     def preprocess_plate_image(self, plate_img):
#         """Preprocess the plate image for better OCR results"""
#         gray_plate_img = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
#         gray_plate_img = cv2.GaussianBlur(gray_plate_img, (5, 5), 0)
#         _, plate_img_thresh = cv2.threshold(gray_plate_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
#         kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
#         plate_img_thresh = cv2.morphologyEx(plate_img_thresh, cv2.MORPH_OPEN, kernel)
        
#         return plate_img_thresh
    
#     def extract_text_from_plate(self, plate_img):
#         """Extract text from plate image with confidence scoring"""
#         processed_plate = self.preprocess_plate_image(plate_img)
        
#         confidence, ocr_data = self.calculate_text_confidence(processed_plate)
        
#         plate_text = "".join([text for i, text in enumerate(ocr_data['text']) 
#                             if ocr_data['conf'][i] > 30 and text.strip().isalnum()])
        
#         return plate_text, confidence, processed_plate
    
#     def process_frame(self, frame):
#         """Process a single frame to detect and recognize number plates"""
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         plates = self.plate_detector.detectMultiScale(gray, 1.1, 4)
        
#         best_plate = None
#         best_confidence = 0
#         best_text = ""
#         best_coords = (0, 0, 0, 0)
        
#         for (x, y, w, h) in plates:
#             area = w * h
#             if area > self.min_area:
#                 plate_img = frame[y:y + h, x:x + w]
                
#                 plate_text, confidence, processed_plate = self.extract_text_from_plate(plate_img)
                
#                 is_confirmed, final_confidence = self.track_plate_confirmation(plate_text, confidence)
                
#                 # NEU: Wenn confirmed, setze Exit-Flag und speichere das endgültige Nummernschild
#                 if is_confirmed:
#                     self.should_exit = True
#                     self.final_confirmed_plate = {
#                         'text': plate_text,
#                         'confidence': final_confidence,
#                         'coords': (x, y, w, h)
#                     }
                
#                 if final_confidence > best_confidence:
#                     best_confidence = final_confidence
#                     best_text = plate_text
#                     best_coords = (x, y, w, h)
#                     best_plate = {
#                         'text': plate_text,
#                         'confidence': final_confidence,
#                         'confirmed': is_confirmed,
#                         'coords': (x, y, w, h),
#                         'processed_image': processed_plate
#                     }
        
#         # Process the best candidate
#         if best_plate:
#             x, y, w, h = best_coords
            
#             if best_plate['confirmed']:
#                 color = (0, 255, 0)  # Green for confirmed
#                 status = "CONFIRMED - EXITING SOON"
#             elif best_confidence >= self.confidence_threshold:
#                 color = (255, 255, 0)  # Yellow for high confidence
#                 status = "HIGH CONFIDENCE"
#             else:
#                 color = (0, 165, 255)  # Orange for low confidence
#                 status = "LOW CONFIDENCE"
            
#             cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
#             plate_img = frame[y:y + h, x:x + w]
#             roi_resized = cv2.resize(plate_img, (400, 100))
#             cv2.imshow("ROI", roi_resized)
            
#             frame_resized = cv2.resize(frame, (512, 512))
            
#             confidence_text = f"{best_confidence:.1%}"
#             display_text = f"{best_text} ({confidence_text}) - {status}"
            
#             cv2.putText(frame_resized, display_text, (10, 30), 
#                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
#             self.draw_confidence_bar(frame_resized, best_confidence, (10, 50))
            
#             return frame_resized, best_text, best_confidence, best_plate['confirmed']
        
#         frame_resized = cv2.resize(frame, (512, 512))
#         cv2.putText(frame_resized, "No plate detected", (10, 30), 
#                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
#         return frame_resized, "", 0.0, False
    
#     def draw_confidence_bar(self, frame, confidence, position):
#         """Draw a confidence bar visualization"""
#         bar_width = 200
#         bar_height = 20
#         x, y = position
        
#         cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height), (50, 50, 50), -1)
        
#         fill_width = int(bar_width * confidence)
        
#         if confidence >= self.confidence_threshold:
#             color = (0, 255, 0)
#         elif confidence >= self.confidence_threshold * 0.7:
#             color = (255, 255, 0)
#         else:
#             color = (0, 165, 255)
        
#         cv2.rectangle(frame, (x, y), (x + fill_width, y + bar_height), color, -1)
#         cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height), (255, 255, 255), 1)
        
#         confidence_text = f"Confidence: {confidence:.1%}"
#         cv2.putText(frame, confidence_text, (x, y - 5), 
#                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
#     def cleanup_confirmed_plates(self):
#         """Remove old unconfirmed plates from tracking"""
#         plates_to_remove = []
#         for plate_text, data in self.confirmed_plates.items():
#             if data['count'] < 2:
#                 plates_to_remove.append(plate_text)
        
#         for plate_text in plates_to_remove:
#             del self.confirmed_plates[plate_text]
    
#     def display_final_result(self):
#         """Display the final confirmed plate result"""
#         if self.final_confirmed_plate:
#             plate_text = self.final_confirmed_plate['text']
#             confidence = self.final_confirmed_plate['confidence']
            
#             print("\n" + "="*50)
#             print("🚗 NUMBERSCHILD ERKANNT UND BESTÄTIGT!")
#             print("="*50)
#             print(f"Nummernschild: {plate_text}")
#             print(f"Confidence: {confidence:.1%}")
#             print(f"Zeitstempel: {time.strftime('%Y-%m-%d %H:%M:%S')}")
#             print("="*50)
            
#             # Hier könntest du das Ergebnis in eine Datei schreiben oder weiterverarbeiten
#             # z.B.: self.save_to_database(plate_text, confidence)
            
#     def run(self):
#         """Main function to run the number plate recognition"""
#         if not self.initialize_camera():
#             return
        
#         if not self.load_haar_cascade():
#             self.cap.release()
#             return
        
#         print(f"🚀 Number Plate Recognition gestartet (Confidence threshold: {self.confidence_threshold:.0%})")
#         print("📋 Das Programm beendet sich automatisch sobald ein Nummernschild bestätigt wurde!")
#         print("⏹️  Drücke 'q' für manuelles Beenden")
        
#         frame_count = 0
        
#         try:
#             while True:
#                 # NEU: Prüfe ob ein Nummernschild confirmed wurde
#                 if self.should_exit:
#                     print("\n✅ Nummernschild bestätigt! Beende Programm...")
#                     break
                
#                 ret, frame = self.cap.read()
                
#                 if not ret:
#                     print("Error: Could not read frame from camera")
#                     break
                
#                 processed_frame, plate_text, confidence, confirmed = self.process_frame(frame)
                
#                 cv2.imshow("NumberPlateRecognition", processed_frame)
                
#                 if confirmed:
#                     print(f"✅ CONFIRMED: {plate_text} (Confidence: {confidence:.1%})")
#                     # Kurze Verzögerung damit man das Ergebnis noch sehen kann
#                     cv2.waitKey(1000)
#                 elif plate_text and confidence >= self.confidence_threshold:
#                     print(f"⚠️  Candidate: {plate_text} (Confidence: {confidence:.1%})")
                
#                 frame_count += 1
#                 if frame_count % 30 == 0:
#                     self.cleanup_confirmed_plates()
                
#                 key = cv2.waitKey(1) & 0xFF
#                 if key == ord('q'):
#                     print("\n⏹️  Manuell beendet durch Benutzer")
#                     break
#                 elif key == ord('r'):
#                     self.confirmed_plates.clear()
#                     print("Confirmed plates reset")
                    
#         except KeyboardInterrupt:
#             print("\n⏹️  Programm durch Benutzer unterbrochen")
#         except Exception as e:
#             print(f"❌ Ein Fehler ist aufgetreten: {e}")
#         finally:
#             # Zeige das endgültige Ergebnis an
#             self.display_final_result()
#             self.cleanup()
    
#     def cleanup(self):
#         """Clean up resources"""
#         if self.cap:
#             self.cap.release()
#         cv2.destroyAllWindows()
#         print("🔚 Number Plate Recognition beendet.")

# # Create and run the recognizer
# if __name__ == "__main__":
#     recognizer = NumberPlateRecognizer(
#         confidence_threshold=0.9,
#         min_plate_length=4,
#         max_plate_length=8,
#     )
#     recognizer.run()
import cv2
import pytesseract
import os
import re
import time
from NumberPlateRecognitionInterface import NumberPlateRecognizer

<<<<<<< HEAD

class NumberPlateRecognizer:
    def __init__(self, confidence_threshold=0.7, min_plate_length=4, max_plate_length=10):
=======
class NumberPlateRecognition(NumberPlateRecognizer):
    def __init__(self, confidence_threshold=0.9, min_plate_length=4, max_plate_length=8):
>>>>>>> 3d44db4fdfba9a909e594b09679b524d2f161c05
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.harcascade = os.path.join(self.current_dir, "haarcascade_russian_plate_number.xml")
        self.min_area = 500
        self.cap = None
        self.plate_detector = None
        
        # Confidence settings
        self.confidence_threshold = confidence_threshold
        self.min_plate_length = min_plate_length
        self.max_plate_length = max_plate_length
        
        # Store confirmed plates
        self.confirmed_plates = {}
        self.confirmation_count_threshold = 3
        
        # Exit control
        self.should_exit = False
        self.final_confirmed_plate = None
        
        # Status tracking
        self.current_status = {
            'detected_plate': '',
            'confidence': 0.0,
            'is_confirmed': False,
            'status_message': 'Initializing...',
            'frame_count': 0
        }
        
        # Set Tesseract path
        pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
    
    def initialize_camera(self) -> bool:
        """Kamera initialisieren"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.current_status['status_message'] = "Error: Could not open camera"
            return False
        self.current_status['status_message'] = "Camera initialized"
        return True
    
    def load_haar_cascade(self) -> bool:
        """Haar Cascade Classifier laden"""
        if not os.path.exists(self.harcascade):
            self.current_status['status_message'] = f"Error: Haar Cascade file not found: {self.harcascade}"
            return False
            
        self.plate_detector = cv2.CascadeClassifier(self.harcascade)
        
        if self.plate_detector.empty():
            self.current_status['status_message'] = "Error: Haar Cascade could not be loaded"
            return False
            
        self.current_status['status_message'] = "Haar Cascade loaded successfully"
        return True
    
    def calculate_text_confidence(self, plate_img_thresh):
        """Confidence Level des OCR Results berechnen"""
        ocr_data = pytesseract.image_to_data(plate_img_thresh, output_type=pytesseract.Output.DICT, config='--psm 7')
        
        total_confidence = 0
        valid_chars = 0
        
        for i, text in enumerate(ocr_data['text']):
            confidence = ocr_data['conf'][i]
            text = text.strip()
            
            if text and confidence > 30 and text.isalnum():
                total_confidence += confidence
                valid_chars += 1
        
        if valid_chars > 0:
            avg_confidence = total_confidence / valid_chars
            normalized_confidence = min(avg_confidence / 100.0, 1.0)
            return normalized_confidence, ocr_data
        else:
            return 0.0, ocr_data
    
    def is_valid_plate_format(self, text):
        """Prüfen ob der erkannte Text typischen Nummernschild-Mustern entspricht"""
        if not text:
            return False
            
        if len(text) < self.min_plate_length or len(text) > self.max_plate_length:
            return False
        
        patterns = [
            r'^[A-Z0-9]{4,8}$',
            r'^[A-Z]{2,3}\d{1,4}$',
            r'^\d{1,4}[A-Z]{2,3}$',
            r'^[A-Z]\d{1,3}[A-Z]{1,3}$',
        ]
        
        for pattern in patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
                
        return False
    
    def track_plate_confirmation(self, plate_text, confidence):
        """Nummernschild-Bestätigung über mehrere Erkennungen hinweg verfolgen"""
        if confidence < self.confidence_threshold or not self.is_valid_plate_format(plate_text):
            return False, confidence
        
        # Bestätigungs-Tracking aktualisieren
        if plate_text in self.confirmed_plates:
            self.confirmed_plates[plate_text]['count'] += 1
            self.confirmed_plates[plate_text]['last_confidence'] = confidence
            self.confirmed_plates[plate_text]['max_confidence'] = max(
                self.confirmed_plates[plate_text]['max_confidence'], confidence
            )
        else:
            self.confirmed_plates[plate_text] = {
                'count': 1,
                'last_confidence': confidence,
                'max_confidence': confidence
            }
        
        # Prüfen ob Nummernschild bestätigt ist
        if self.confirmed_plates[plate_text]['count'] >= self.confirmation_count_threshold:
            return True, self.confirmed_plates[plate_text]['max_confidence']
        
        return False, confidence
    
    def preprocess_plate_image(self, plate_img):
        """Nummernschild-Bild für bessere OCR-Results vorverarbeiten"""
        gray_plate_img = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        gray_plate_img = cv2.GaussianBlur(gray_plate_img, (5, 5), 0)
        _, plate_img_thresh = cv2.threshold(gray_plate_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        plate_img_thresh = cv2.morphologyEx(plate_img_thresh, cv2.MORPH_OPEN, kernel)
        
        return plate_img_thresh
    
    def extract_text_from_plate(self, plate_img):
        """Text aus Nummernschild mit Confidence-Scoring extrahieren"""
        processed_plate = self.preprocess_plate_image(plate_img)
        
        confidence, ocr_data = self.calculate_text_confidence(processed_plate)
        
        plate_text = "".join([text for i, text in enumerate(ocr_data['text']) 
                            if ocr_data['conf'][i] > 30 and text.strip().isalnum()])
        
        return plate_text, confidence, processed_plate
    
    def process_frame(self, frame):
        """Einzelnen Frame verarbeiten um Nummernschilder zu erkennen"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        plates = self.plate_detector.detectMultiScale(gray, 1.1, 4)
        
        best_plate = None
        best_confidence = 0
        best_text = ""
        best_coords = (0, 0, 0, 0)
        
        # Status zurücksetzen
        self.current_status['detected_plate'] = ''
        self.current_status['confidence'] = 0.0
        self.current_status['is_confirmed'] = False
        self.current_status['status_message'] = 'No plate detected'
        
        for (x, y, w, h) in plates:
            area = w * h
            if area > self.min_area:
                plate_img = frame[y:y + h, x:x + w]
                
                plate_text, confidence, processed_plate = self.extract_text_from_plate(plate_img)
                
                is_confirmed, final_confidence = self.track_plate_confirmation(plate_text, confidence)
                
                # Wenn confirmed, Exit-Flag setzen und finales Nummernschild speichern
                if is_confirmed:
                    self.should_exit = True
                    self.final_confirmed_plate = {
                        'text': plate_text,
                        'confidence': final_confidence,
                        'coords': (x, y, w, h),
                        'timestamp': time.time()
                    }
                    self.current_status['is_confirmed'] = True
                    self.current_status['status_message'] = 'CONFIRMED - Exiting'
                
                if final_confidence > best_confidence:
                    best_confidence = final_confidence
                    best_text = plate_text
                    best_coords = (x, y, w, h)
                    best_plate = {
                        'text': plate_text,
                        'confidence': final_confidence,
                        'confirmed': is_confirmed,
                        'coords': (x, y, w, h),
                        'processed_image': processed_plate
                    }
        
        # Besten Kandidaten verarbeiten
        if best_plate:
            x, y, w, h = best_coords
            
            # Status aktualisieren
            self.current_status['detected_plate'] = best_text
            self.current_status['confidence'] = best_confidence
            
            if best_plate['confirmed']:
                color = (0, 255, 0)  # Grün für confirmed
                status = "CONFIRMED - EXITING SOON"
                self.current_status['status_message'] = status
            elif best_confidence >= self.confidence_threshold:
                color = (255, 255, 0)  # Gelb für high confidence
                status = "HIGH CONFIDENCE"
                self.current_status['status_message'] = status
            else:
                color = (0, 165, 255)  # Orange für low confidence
                status = "LOW CONFIDENCE"
                self.current_status['status_message'] = status
            
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            plate_img = frame[y:y + h, x:x + w]
            roi_resized = cv2.resize(plate_img, (400, 100))
            cv2.imshow("ROI", roi_resized)
            
            frame_resized = cv2.resize(frame, (512, 512))
            
            confidence_text = f"{best_confidence:.1%}"
            display_text = f"{best_text} ({confidence_text}) - {status}"
            
            cv2.putText(frame_resized, display_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            self.draw_confidence_bar(frame_resized, best_confidence, (10, 50))
            
            return frame_resized, best_text, best_confidence, best_plate['confirmed']
        
        frame_resized = cv2.resize(frame, (512, 512))
        cv2.putText(frame_resized, "No plate detected", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame_resized, "", 0.0, False
    
    def draw_confidence_bar(self, frame, confidence, position):
        """Confidence Bar Visualisierung zeichnen"""
        bar_width = 200
        bar_height = 20
        x, y = position
        
        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height), (50, 50, 50), -1)
        
        fill_width = int(bar_width * confidence)
        
        if confidence >= self.confidence_threshold:
            color = (0, 255, 0)
        elif confidence >= self.confidence_threshold * 0.7:
            color = (255, 255, 0)
        else:
            color = (0, 165, 255)
        
        cv2.rectangle(frame, (x, y), (x + fill_width, y + bar_height), color, -1)
        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height), (255, 255, 255), 1)
        
        confidence_text = f"Confidence: {confidence:.1%}"
        cv2.putText(frame, confidence_text, (x, y - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def get_detection_status(self) -> dict:
        """Aktuellen Erkennungsstatus abrufen"""
        return self.current_status.copy()
    
    def set_confidence_threshold(self, threshold: float):
        """Confidence Threshold setzen"""
        self.confidence_threshold = max(0.0, min(1.0, threshold))
    
    def get_confirmed_plate(self) -> dict:
        """Bestätigtes Nummernschild abrufen"""
        return self.final_confirmed_plate.copy() if self.final_confirmed_plate else None
    
    def cleanup_confirmed_plates(self):
        """Alte unbestätigte Nummernschilder aus Tracking entfernen"""
        plates_to_remove = []
        for plate_text, data in self.confirmed_plates.items():
            if data['count'] < 2:
                plates_to_remove.append(plate_text)
        
        for plate_text in plates_to_remove:
            del self.confirmed_plates[plate_text]
    
    def display_final_result(self):
        """Finales bestätigtes Nummernschild-Resultat anzeigen"""
        if self.final_confirmed_plate:
            plate_text = self.final_confirmed_plate['text']
            confidence = self.final_confirmed_plate['confidence']
            
            print("\n" + "="*50)
            print("🚗 NUMBERSCHILD ERKANNT UND BESTÄTIGT!")
            print("="*50)
            print(f"Nummernschild: {plate_text}")
            print(f"Confidence: {confidence:.1%}")
            print(f"Zeitstempel: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*50)
    
    def run(self):
        """Hauptausführungsmethode"""
        if not self.initialize_camera():
            return
        
        if not self.load_haar_cascade():
            self.cap.release()
            return
        
        print(f"🚀 Number Plate Recognition gestartet (Confidence threshold: {self.confidence_threshold:.0%})")
        print("📋 Das Programm beendet sich automatisch sobald ein Nummernschild bestätigt wurde!")
        print("⏹️  Drücke 'q' für manuelles Beenden")
        
        frame_count = 0
        
        try:
            while True:
                # Prüfe ob ein Nummernschild confirmed wurde
                if self.should_exit:
                    print("\n✅ Nummernschild bestätigt! Beende Programm...")
                    break
                
                ret, frame = self.cap.read()
                
                if not ret:
                    self.current_status['status_message'] = "Error: Could not read frame from camera"
                    break
                
                processed_frame, plate_text, confidence, confirmed = self.process_frame(frame)
                
                cv2.imshow("NumberPlateRecognition", processed_frame)
                
                if confirmed:
                    print(f"✅ CONFIRMED: {plate_text} (Confidence: {confidence:.1%})")
                    # Kurze Verzögerung damit man das Ergebnis noch sehen kann
                    cv2.waitKey(1000)
                elif plate_text and confidence >= self.confidence_threshold:
                    print(f"⚠️  Candidate: {plate_text} (Confidence: {confidence:.1%})")
                
                frame_count += 1
                self.current_status['frame_count'] = frame_count
                
                if frame_count % 30 == 0:
                    self.cleanup_confirmed_plates()
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n⏹️  Manuell beendet durch Benutzer")
                    break
                elif key == ord('r'):
                    self.confirmed_plates.clear()
                    self.current_status['status_message'] = "Tracking reset"
                    print("Confirmed plates reset")
                    
        except KeyboardInterrupt:
            print("\n⏹️  Programm durch Benutzer unterbrochen")
        except Exception as e:
            print(f"❌ Ein Fehler ist aufgetreten: {e}")
        finally:
            # Zeige das endgültige Ergebnis an
            self.display_final_result()
            self.cleanup()
    
    def cleanup(self):
        """Ressourcen freigeben"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.current_status['status_message'] = 'Stopped'
        print(" Number Plate Recognition beendet.")

# Hauptprogramm
if __name__ == "__main__":
    # Erstelle Recognizer über das Interface
    recognizer: NumberPlateRecognizer = NumberPlateRecognition(confidence_threshold=0.9, min_plate_length=4,max_plate_length=8,)
    
    # Verwende die Interface-Methoden
    print("Starting number plate recognition...")
    recognizer.run()
    
    # Nach Beendigung könntest du den Status abrufen
    final_plate = recognizer.get_confirmed_plate()
    if final_plate:
        print(f"\n Final confirmed plate: {final_plate['text']}")
    
    recognizer.cleanup()