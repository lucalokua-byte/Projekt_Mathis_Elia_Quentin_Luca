import cv2
import pytesseract
import os
import re
import time
from .NumberPlateRecognitionInterface import NumberPlateRecognizer

class NumberPlateRecognition(NumberPlateRecognizer): # The NumberPlateRecognition takes from the NumberPlateRecognizer Interface, which means it will implement all its methods
    """Implementation of Number Plate Recognition System"""
    def __init__(self, confidence_threshold=0.9, min_plate_length=4, max_plate_length=8): # The class constructor with default values for confidence threshold and plate length
        # These two lines set up the Haar Cascade file path for plate detection, that file is a pre-trained model for reading specifically Russian plates but works decently for others too
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.harcascade = os.path.join(self.current_dir, "haarcascade_russian_plate_number.xml") 

        self.min_area = 500 # Minimal area in pixels for a detected plate to be considered valid
        self.cap = None # Video capture object that will be initialized later
        self.plate_detector = None # Haar Cascade Classifier object
        
        # Confidence settings
        self.confidence_threshold = confidence_threshold
        self.min_plate_length = min_plate_length
        self.max_plate_length = max_plate_length
        
        # Store confirmed plates
        self.confirmed_plates = {}
        self.confirmation_count_threshold = 3 # Number of times a plate must be seen to be confirmed
        
        # Exit control
        self.should_exit = False # Indicates when to exit the detection loop (As soon as it turns true, the program will end)
        self.final_confirmed_plate = None # Store the final confirmed plate information
        
        # Status tracking dictionary which allows real time status updates
        self.current_status = {
            'detected_plate': '',
            'confidence': 0.0,
            'is_confirmed': False,
            'status_message': 'Initializing...',
            'frame_count': 0
        }
        
        # Set Tesseract path (tesseract being a text recognition engine)
        pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
    
    def initialize_camera(self) -> bool: # -> bool indicates that this method returns a boolean value
        """Initialize camera for capturing frames"""
        self.cap = cv2.VideoCapture(0) # creates a video capture object using the default camera of the system
        if not self.cap.isOpened(): # if statement to check if camera opened successfully
            self.current_status['status_message'] = "Error: Could not open camera"
            return False
        # otherwise:
        self.current_status['status_message'] = "Camera initialized"
        return True
    
    def load_haar_cascade(self) -> bool:
        """Load Haar Cascade Classifier for plate detection"""
        if not os.path.exists(self.harcascade): # Check if the Haar Cascade file exists
            self.current_status['status_message'] = f"Error: Haar Cascade file not found: {self.harcascade}"
            return False
            
        self.plate_detector = cv2.CascadeClassifier(self.harcascade) # cv2 loads the trained model and the model gets assigned to plate_detector
        
        if self.plate_detector.empty(): # Check if the classifier loaded successfully
            self.current_status['status_message'] = "Error: Haar Cascade could not be loaded"
            return False
        # otherwise:
        self.current_status['status_message'] = "Haar Cascade loaded successfully"
        return True
    
    def calculate_text_confidence(self, plate_img_thresh):
        """Calculate confidence score for OCR-extracted text"""
        ocr_data = pytesseract.image_to_data(plate_img_thresh, output_type=pytesseract.Output.DICT, config='--psm 7') # code to extract text data from the preprocessed plate image using Tesseract OCR
        
        # initialize variables to calculate average confidence
        total_confidence = 0
        valid_chars = 0
        
        for i, text in enumerate(ocr_data['text']): # iterate through each detected text element, text can't be empty
            confidence = ocr_data['conf'][i] # get confidence score for the current text element, between -1 and 100 comes from tesseract (-1 means no text detected)
            text = text.strip()
            
            if text and confidence > 30 and text.isalnum(): # confidence has to be more than 30 percent, and the text has to be either letters or numbers
                total_confidence += confidence # accumulate confidence scores
                valid_chars += 1 # count the number of valid characters
        
        if valid_chars > 0: # to avoid division by zero
            avg_confidence = total_confidence / valid_chars # calculate average confidence
            normalized_confidence = min(avg_confidence / 100.0, 1.0) # goes from 0-100 scale to 0.0-1.0 scale
            return normalized_confidence, ocr_data # return the normalized confidence and the full OCR data, for later use
        else:
            return 0.0, ocr_data # no valid characters detected, return 0 confidence
    
    def is_valid_plate_format(self, text):
        """Validate plate format using regex patterns"""
        if not text:
            return False # empty text is not valid
            
        if len(text) < self.min_plate_length or len(text) > self.max_plate_length:
            return False # check length constraints, cannot be too short or too long
        
        # list of patterns for valid plate formats
        patterns = [
            r'^[A-Z0-9]{4,8}$',
            r'^[A-Z]{2,3}\d{1,4}$',
            r'^\d{1,4}[A-Z]{2,3}$',
            r'^[A-Z]\d{1,3}[A-Z]{1,3}$',
        ]
        
        for pattern in patterns:
            if re.match(pattern, text, re.IGNORECASE): # check if text matches any of the patterns, without any case sensitivity
                return True
                
        return False # no patterns matched, invalid format
    
    def track_plate_confirmation(self, plate_text, confidence):
        """Track and confirm plates based on repeated detections"""
        if confidence < self.confidence_threshold or not self.is_valid_plate_format(plate_text): # if confidence is below threshold or plate format is invalid it doesn't try to confirm it
            return False, confidence
        
        
        if plate_text in self.confirmed_plates: # if plate text is already being tracked
            self.confirmed_plates[plate_text]['count'] += 1 # increment detection count
            self.confirmed_plates[plate_text]['last_confidence'] = confidence # update confidence
            self.confirmed_plates[plate_text]['max_confidence'] = max(self.confirmed_plates[plate_text]['max_confidence'], confidence)# update max confidence if current is higher
        else:
            self.confirmed_plates[plate_text] = { # plate is detected for the first time, initialize its tracking data
                'count': 1,
                'last_confidence': confidence,
                'max_confidence': confidence
            }
        
        # Check if the plate has been confirmed
        if self.confirmed_plates[plate_text]['count'] >= self.confirmation_count_threshold: # plate needs to be recognized 3 times to be confirmed
            return True, self.confirmed_plates[plate_text]['max_confidence']
        
        return False, confidence # not yet confirmed
    
    def preprocess_plate_image(self, plate_img):
        """Preprocess plate image for better OCR results"""
        gray_plate_img = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY) # convert to grayscale
        gray_plate_img = cv2.GaussianBlur(gray_plate_img, (5, 5), 0) # apply Gaussian blur to reduce noise (from OpenCV library)
        _, plate_img_thresh = cv2.threshold(gray_plate_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)) # the kernel is a small matrix (3x3) that goes over the image
        plate_img_thresh = cv2.morphologyEx(plate_img_thresh, cv2.MORPH_OPEN, kernel)
        
        return plate_img_thresh # return the preprocessed image for better OCR readings in later steps
    
    def extract_text_from_plate(self, plate_img):
        """text extraction from plate image using OCR"""
        processed_plate = self.preprocess_plate_image(plate_img) # vorher definiertes Preprocessing aufrufen
        
        confidence, ocr_data = self.calculate_text_confidence(processed_plate) # calculate confidence and get OCR data
        
        plate_text = "".join([text for i, text in enumerate(ocr_data['text']) # concatenate valid text elements
                            if ocr_data['conf'][i] > 30 and text.strip().isalnum()]) # only consider texts with confidence > 30 and alphanumeric
        
        return plate_text, confidence, processed_plate # return the extracted text, confidence score, and processed plate image
    
    def process_frame(self, frame):
        """Process a single frame for plate detection and recognition"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # convert frame to grayscale
        plates = self.plate_detector.detectMultiScale(gray, 1.1, 4) # detect plates in the frame 
        
        # Initialize variables to track the best plate candidate
        best_plate = None
        best_confidence = 0
        best_text = ""
        best_coords = (0, 0, 0, 0)
        
        # Reset current status
        self.current_status['detected_plate'] = ''
        self.current_status['confidence'] = 0.0
        self.current_status['is_confirmed'] = False
        self.current_status['status_message'] = 'No plate detected'
        
        for (x, y, w, h) in plates: # iterate through detected plates
            area = w * h
            if area > self.min_area:
                # exstract text using OCR
                plate_img = frame[y:y + h, x:x + w]
                plate_text, confidence, processed_plate = self.extract_text_from_plate(plate_img)
                
                is_confirmed, final_confidence = self.track_plate_confirmation(plate_text, confidence)
                
                # If plate is confirmed, set exit flag and store final plate info
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
                
                if final_confidence > best_confidence: # track the best candidate based on confidence in the current frame
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
        
        if best_plate:
            x, y, w, h = best_coords
            
            # Update current status
            self.current_status['detected_plate'] = best_text
            self.current_status['confidence'] = best_confidence
            
            # Visual feedback on the frame based on confidence and confirmation status
            if best_plate['confirmed']:
                color = (0, 255, 0)  # green for confirmed
                status = "CONFIRMED - EXITING SOON"
                self.current_status['status_message'] = status
            elif best_confidence >= self.confidence_threshold:
                color = (255, 255, 0)  # yellow for high confidence
                status = "HIGH CONFIDENCE"
                self.current_status['status_message'] = status
            else:
                color = (0, 165, 255)  # orange for low confidence
                status = "LOW CONFIDENCE"
                self.current_status['status_message'] = status
            
            # Draw rectangle around detected plate, visual feedback
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
            ####################################################################
            
            return frame_resized, best_text, best_confidence, best_plate['confirmed'] # return the processed frame and plate info
        
        # No plate detected, return original frame with message
        frame_resized = cv2.resize(frame, (512, 512))
        cv2.putText(frame_resized, "No plate detected", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame_resized, "", 0.0, False
    
    def draw_confidence_bar(self, frame, confidence, position):
        """Draw confidence bar on the frame"""
        # entire method using cv2 and basic drawing functions to visualize confidence level on the frame in real time
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
        """Get current detection status"""
        return self.current_status.copy()
    '''
    current status contains (with different values):
    self.current_status = {
            'detected_plate': '',
            'confidence': 0.0,
            'is_confirmed': False,
            'status_message': 'Initializing...',
            'frame_count': 0
            }
    '''
        
    def set_confidence_threshold(self, threshold: float):
        """set confidence threshold for plate confirmation"""
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
        """Finales bestätigtes Nummernschild-Resultat anzeigen und in DB speichern"""
        if self.final_confirmed_plate:
            plate_text = self.final_confirmed_plate['text']
            confidence = self.final_confirmed_plate['confidence']
            timestamp = self.final_confirmed_plate.get('timestamp', time.time())
            
            print("\n" + "="*50)
            print("NUMBERSCHILD ERKANNT UND BESTÄTIGT!")
            print("="*50)
            print(f"Nummernschild: {plate_text}")
            print(f"Confidence: {confidence:.1%}")
            print(f"Zeitstempel: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*50)
            
            # In Datenbank speichern mit besserer Fehlerbehandlung
            try:
                # Korrekte Importe
                from Db_maneger.Db_maneger import DBManager
                from mail_system.email_system import EmailSender
                
                # Datenbank-Manager erstellen
                db_manager = DBManager("data", "license_plate.json")
                
                # Prüfe Whitelist
                if plate_text in db_manager.whitelisted_plates:
                    print(f"Nummernschild {plate_text} ist in der Whitelist.")
                    db_manager.add_license_plate(plate_text, confidence)
                    db_manager.save_data()
                    return
                
                # Prüfe ob Nummernschild bereits in Datenbank existiert
                existing_record = db_manager.find(plate_text, verbose=False)
                if existing_record and plate_text not in db_manager.blacklisted_plates and plate_text not in db_manager.whitelisted_plates:
                    print(f"Numberplate {plate_text} found in database, requesting email system for decision...")
                    email_sender = EmailSender(db_manager)
                    decision = email_sender.run_email_system(plate_text)
                    return

                # Prüfe Blacklist
                if plate_text in db_manager.blacklisted_plates:
                    print(f"Numberplate {plate_text} is in the blacklist, gate stays closed.")
                    db_manager.add_license_plate(plate_text, confidence)
                    db_manager.save_data()
                    return
                
                # Für neue Nummernschilder: Email-System starten
                email_sender = EmailSender(db_manager)
                decision = email_sender.run_email_system(plate_text)
                
                # Entscheidung verarbeiten
                if decision == 'accept_whitelist':
                    db_manager.whitelist_plate(plate_text)
                    db_manager.add_license_plate(plate_text, confidence=confidence)
                elif decision == 'accept_only':
                    db_manager.add_license_plate(plate_text, confidence=confidence)
                elif decision == 'reject_blacklist':
                    db_manager.blacklist_plate(plate_text)
                elif decision == 'reject_only':
                    # Nur ablehnen, nicht in Datenbank speichern
                    pass
                    
                db_manager.save_data()

            except ImportError as e:
                print(f"Import-Fehler: {e}")
                print("DBManager oder EmailSender nicht verfügbar - Datenbank-Speicherung übersprungen")
            except Exception as e:
                print(f"Fehler beim Speichern in Datenbank: {e}")
    
    def begin_plate_detection(self):
        """Hauptausführungsmethode"""
        if not self.initialize_camera():
            return
        
        if not self.load_haar_cascade():
            self.cap.release()
            return
        
        print(f"Number Plate Recognition gestartet (Confidence threshold: {self.confidence_threshold:.0%})")
        print("Das Programm beendet sich automatisch sobald ein Nummernschild bestätigt wurde!")
        print("Drücke 'q' für manuelles Beenden")
        
        frame_count = 0
        
        try:
            while True:
                # Prüfe ob ein Nummernschild confirmed wurde
                if self.should_exit:
                    print("\nNummernschild bestätigt! Beende Programm...")
                    break
                
                ret, frame = self.cap.read()
                
                if not ret:
                    self.current_status['status_message'] = "Error: Could not read frame from camera"
                    break
                
                processed_frame, plate_text, confidence, confirmed = self.process_frame(frame)
                
                cv2.imshow("NumberPlateRecognition", processed_frame)
                
                if confirmed:
                    print(f"CONFIRMED: {plate_text} (Confidence: {confidence:.1%})")
                    # Kurze Verzögerung damit man das Ergebnis noch sehen kann
                    cv2.waitKey(1000)
                elif plate_text and confidence >= self.confidence_threshold:
                    print(f"Candidate: {plate_text} (Confidence: {confidence:.1%})")
                
                frame_count += 1
                self.current_status['frame_count'] = frame_count
                
                if frame_count % 30 == 0:
                    self.cleanup_confirmed_plates()
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\nManuell beendet durch Benutzer")
                    self.should_exit = True
                    break
                elif key == ord('r'):
                    self.confirmed_plates.clear()
                    self.current_status['status_message'] = "Tracking reset"
                    print("Confirmed plates reset")
                    
        except KeyboardInterrupt:
            print("\nProgramm durch Benutzer unterbrochen")
        except Exception as e:
            print(f"❌ Ein Fehler ist aufgetreten: {e}")
        finally:
            # Zeige das endgültige Ergebnis an
            self.display_final_result()
            self.close_camera_window()
    
    def close_camera_window(self):
        """Ressourcen freigeben"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.current_status['status_message'] = 'Stopped'
        print(" Number Plate Recognition beendet.")
