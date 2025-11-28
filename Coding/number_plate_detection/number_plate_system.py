from .system_interface import IntelligentDetectionSystem
import cv2
import time
from camera_manager import CameraManager
from utils import PlateLogger, draw_detection_results
from Db_maneger.AbstractDBManager import AbstractDBManager
from Db_maneger.Db_maneger import DBManager
from number_plate_detection.NumberPlateRecognition import PlateRecognizer

class NumberPlateRecognitionSystem:
    def __init__(self, camera_id=0, display=True, log_results=True):
        self.camera_manager = CameraManager(camera_id)
        self.plate_recognizer = PlateRecognizer()
        self.plate_logger = PlateLogger() if log_results else None
        self.display = display
        
        # Improved tracking
        self.detected_plates = set()
        self.confirmation_tracker = {}
        self.required_confirmations = 3  # Increased for reliability
        self.last_valid_detection = 0
        self.detection_cooldown = 5.0  # Cooldown after valid detection

        self.db_manager: AbstractDBManager = DBManager("data", "license_plates.json")
        
    def start(self):
        """Start the plate recognition system"""
        print("🚀 Starting Advanced Plate Recognition System...")
        
        if not self.plate_recognizer.setup():
            return False
        
        if not self.camera_manager.start_capture():
            return False
        
        print("✅ System ready - Point camera at license plates")
        print("📋 Controls: 'q'=quit, 's'=save frame, 'd'=debug info")
        
        try:
            last_process_time = 0
            process_interval = 0.2  # Process every 200ms
            
            while True:
                start_time = time.time()
                frame = self.camera_manager.get_frame()
                
                if frame is not None:
                    current_time = time.time()
                    
                    # Process frames at controlled rate
                    if current_time - last_process_time >= process_interval:
                        # Only process if not in cooldown
                        if current_time - self.last_valid_detection >= self.detection_cooldown:
                            results = self.plate_recognizer.recognize_from_frame(frame)
                            last_process_time = current_time
                            
                            if results:
                                for result in results:
                                    self.handle_detected_plate(result, current_time)
                    
                    # Display
                    if self.display:
                        display_frame = frame.copy()
                        self.add_display_info(display_frame, current_time)
                        cv2.imshow('License Plate Recognition', display_frame)
                
                # Handle input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s') and frame is not None:
                    self.save_frame(frame)
                elif key == ord('d'):
                    self.print_debug_info()
                
                # Maintain performance
                elapsed = time.time() - start_time
                if elapsed < 0.016:
                    time.sleep(0.016 - elapsed)
                    
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
        except Exception as e:
            print(f"❌ System error: {e}")
        finally:
            self.stop()
    
    def add_display_info(self, frame, current_time):
        """Add display information"""
        # Status
        if current_time - self.last_valid_detection < self.detection_cooldown:
            status = "COOLDOWN"
            color = (0, 165, 255)  # Orange
        else:
            status = "READY"
            color = (0, 255, 0)  # Green
            
        cv2.putText(frame, f"Status: {status}", (10, 30), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Confirmed plates count
        cv2.putText(frame, f"Confirmed: {len(self.detected_plates)}", (10, 60), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Show plates being tracked
        y_offset = 90
        for plate, data in list(self.confirmation_tracker.items())[:4]:
            count = data['count']
            confidence = data['max_confidence']
            text = f"{plate}: {count}/{self.required_confirmations} ({confidence:.2f})"
            color = (0, 255, 255) if count < self.required_confirmations else (0, 255, 0)
            cv2.putText(frame, text, (10, y_offset), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            y_offset += 20
    
    def handle_detected_plate(self, result, current_time):
        """Handle plate detection with improved validation"""
        plate_text = result['text']
        confidence = result['confidence']
        
        print(f"📝 Potential: {plate_text} (conf: {confidence:.2f})")
        
        # Initialize tracking
        if plate_text not in self.confirmation_tracker:
            self.confirmation_tracker[plate_text] = {
                'count': 1,
                'first_seen': current_time,
                'last_seen': current_time,
                'max_confidence': confidence
            }
        else:
            self.confirmation_tracker[plate_text]['count'] += 1
            self.confirmation_tracker[plate_text]['last_seen'] = current_time
            self.confirmation_tracker[plate_text]['max_confidence'] = max(
                self.confirmation_tracker[plate_text]['max_confidence'], confidence
            )
        
        current_count = self.confirmation_tracker[plate_text]['count']
        
        # Check for confirmation
        if (current_count >= self.required_confirmations and 
            plate_text not in self.detected_plates):
            
            self.confirm_plate_detection(plate_text, current_time)
    
    def confirm_plate_detection(self, plate_text, current_time):
        """Confirm a plate detection"""
        print(f"🎯 CONFIRMED PLATE: {plate_text}")
        
        self.detected_plates.add(plate_text)
        self.last_valid_detection = current_time
        
        # Add to database
        added = self.db_manager.add_license_plate(plate_text)
        if added:
            print(f"💾 Saved to database: {plate_text}")
        else:
            print(f"ℹ️ Already in database: {plate_text}")
        
        # Cleanup
        if plate_text in self.confirmation_tracker:
            del self.confirmation_tracker[plate_text]
        
        # Clean old entries
        self.cleanup_old_entries(current_time)
    
    def cleanup_old_entries(self, current_time):
        """Remove old confirmation attempts"""
        max_age = 10.0  # 10 seconds
        expired = []
        
        for plate, data in self.confirmation_tracker.items():
            if current_time - data['last_seen'] > max_age:
                expired.append(plate)
        
        for plate in expired:
            del self.confirmation_tracker[plate]
    
    def print_debug_info(self):
        """Print debug information"""
        print(f"\n🔍 Debug - Tracking {len(self.confirmation_tracker)} plates:")
        for plate, data in self.confirmation_tracker.items():
            print(f"  {plate}: {data['count']} confirms, max conf: {data['max_confidence']:.2f}")
    
    def save_frame(self, frame):
        """Save current frame"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"plate_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"💾 Saved: {filename}")
    
    def stop(self):
        """Stop system"""
        print("\n🛑 Stopping system...")
        self.camera_manager.stop_capture()
        cv2.destroyAllWindows()
        
        print(f"\n📊 Session Results:")
        print("=" * 40)
        if self.detected_plates:
            for plate in sorted(self.detected_plates):
                print(f"✅ {plate}")
        else:
            print("❌ No valid plates detected")
        print("=" * 40)

class CompleteDetectionSystem(IntelligentDetectionSystem):
    def __init__(self, camera_id=0, display=True, log_results=True):  
        self.camera_id = camera_id
        self.display = display
        self.log_results = log_results
        self.plate_system = None
    
    def start_plate_recognition(self) -> bool:
        self.plate_system = NumberPlateRecognitionSystem(
            camera_id=self.camera_id,
            display=self.display,
            log_results=self.log_results
        )
        return self.plate_system.start()
    
    def stop_system(self):
        if self.plate_system:
            self.plate_system.stop()