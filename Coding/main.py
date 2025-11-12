import cv2
import mediapipe as mp
import time
import argparse
from camera_manager import CameraManager
from Fahrzeugerkennung import ObjectDetector, Camera, DetectionProcessor
from plate_recognition import PlateRecognizer
from utils import PlateLogger, draw_detection_results

def fahrzeugerkennung(camera_index=0, score_threshold=0.2):
    """
    Vehicle detection function
    
    Args:
        camera_index: Camera index (default: 0)
        score_threshold: Confidence threshold (default: 0.2)
    """
    try:
        # Initialize application
        detector = ObjectDetector(score_threshold=score_threshold)
        camera = Camera(camera_index=camera_index)
        processor = DetectionProcessor()
        
        print("Vehicle detection in progress...")
        print("CONSOLE ALERT for cars with +30% confidence")
        print("Press 'q' to quit")
        
        running = True
        
        while running:
            # Capture frame
            frame = camera.read_frame()
            
            # Convert for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Detect objects
            timestamp = camera.get_timestamp()
            detection_result = detector.detector.detect_for_video(mp_image, timestamp)
            
            # Process detections
            processed_frame, car_detected = processor.process_detections(detection_result, frame)
            
            # Add FPS
            fps = camera.get_fps()
            cv2.putText(processed_frame, f"FPS: {fps:.1f}", (10, frame.shape[0] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Display image
            cv2.imshow('Vehicle Detection - Alert +30%', processed_frame)
            
            # Check for 'q' key to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                running = False
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("Detection completed")

    


class NumberPlateRecognitionSystem:
    def __init__(self, camera_id=0, display=True, log_results=True):
        self.camera_manager = CameraManager(camera_id)
        self.plate_recognizer = PlateRecognizer()
        self.plate_logger = PlateLogger() if log_results else None
        self.display = display
        self.detected_plates = set()
        
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
        print("System stopped.")

def main():
    """Unified main function"""
    print("=== INTELLIGENT DETECTION SYSTEM ===")
    
    # Start vehicle detection
    fahrzeugerkennung()

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