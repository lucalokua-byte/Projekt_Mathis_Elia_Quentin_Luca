import cv2
import mediapipe as mp
import time
import argparse
import os
import json
from camera_manager import CameraManager
from utils import PlateLogger, draw_detection_results
from Db_maneger.AbstractDBManager import AbstractDBManager
from Db_maneger.Db_maneger import DBManager
from vehicle_detection.app import CarDetectionApp
from number_plate_detection.NumberPlateDetection_Interface import NumberPlateDetection
from number_plate_detection.NumberPlateRecognition import PlateRecognizer


class NumberPlateRecognitionSystem:
    def __init__(self, camera_id=0, display=True, log_results=True):
        self.camera_manager = CameraManager(camera_id)
        self.plate_recognizer = PlateRecognizer()
        self.plate_logger = PlateLogger() if log_results else None
        self.display = display
        self.detected_plates = set()

        self.db_manager:AbstractDBManager = DBManager("data", "license_plates.json")
        
    def start(self):
        """Start the number plate recognition system"""
        print("Starting Number Plate Recognition System...")
        
        if not self.camera_manager.start_capture():
            print("Failed to start camera")
            return
        
        print("System started. Press 'q' to quit, 's' to save current frame")
        
        try:
            while True:
                frame = self.camera_manager.get_frame()
                
                if frame is not None:
                    # Process frame for license plates
                    results = self.plate_recognizer.recognize_from_frame(frame)
                    
                    # Handle detected plates
                    for result in results:
                        self.handle_detected_plate(result, frame)
                    
                    # Display results
                    if self.display:
                        display_frame = draw_detection_results(frame.copy(), results)
                        cv2.imshow('Number Plate Recognition', display_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s') and frame is not None:
                    self.save_frame(frame)
                
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.stop()
    
    def handle_detected_plate(self, result, frame):
        """Handle newly detected plates"""
        plate_text = result['text']
        
        if plate_text not in self.detected_plates:
            print(f"New plate detected: {plate_text}")
            self.detected_plates.add(plate_text)

            # Add to database
            added = self.db_manager.add_license_plate(plate_text)
            if added:
                print(f"Plate {plate_text} added to database.")
            else:
                print(f"Plate {plate_text} already exists in database.")
            
            if self.plate_logger:
                self.plate_logger.log_plate(plate_text, result.get('confidence', 1.0))
    
    def save_frame(self, frame):
        """Save current frame as image"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Frame saved as {filename}")
    
    def stop(self):
        """Stop the system and cleanup"""
        self.camera_manager.stop_capture()
        cv2.destroyAllWindows()
        print("\n Final logged plates:")
        for plate in self.db_manager.list_all():
            self.db_manager.find(plate['license_plate'])
            print(f"Logged plate: {plate['license_plate']}")
        print("System stopped.")

def main():
    """Unified main function"""
    print("=== INTELLIGENT DETECTION SYSTEM ===")

    # Start vehicle detection
    print("  VEHICLE DETECTION SYSTEM")
    app = CarDetectionApp()
    app.run()

    # Parse command-line arguments for number plate recognition
    parser = argparse.ArgumentParser(description='Number Plate Recognition System')
    parser.add_argument('--camera', type=int, default=0, help='Camera ID (default: 0)')
    parser.add_argument('--no-display', action='store_true', help='Disable display window')
    parser.add_argument('--no-log', action='store_true', help='Disable logging')
    
    args = parser.parse_args()
    
    system = NumberPlateRecognitionSystem(
        camera_id=args.camera,
        display=not args.no_display,
        log_results=not args.no_log
    )
    
    system.start()

if __name__ == "__main__":
    main()