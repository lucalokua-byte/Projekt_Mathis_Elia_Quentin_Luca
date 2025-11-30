import cv2
import time
import os
import sys
from vehicle_detection.detectors.object_detector import ObjectDetector
from vehicle_detection.detectors.detection_processor import DetectionProcessor
from vehicle_detection.camera.camera_manager import Camera

# Add current directory to Python path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the vehicle detection system implementation
from interface.Implementation_Systeme_Detection_Camera import CameraVehicleDetectionSystem

class CarDetectionApp:
    """
    MAIN VEHICLE DETECTION APPLICATION
    Uses camera to detect vehicles and automatically stops after n seconds of continuous detection
    """
    
    def __init__(self):
        # Initialize the detection system
        self.system = CameraVehicleDetectionSystem()
        self.running = False
        self.threshold = 1.0  # seconds
        self.detection_mode = "all_vehicles"  # options: cars_only, standard_vehicles, all_vehicles
    
    def stop(self):
        #Stop the application gracefully
        self.running = False
        if self.system.camera:
            self.system.camera.release()
        cv2.destroyAllWindows()
    
    def run(self):
        #Main application loop
        print("Vehicle Detection System")
        print("=" * 40)
        
        # Configure detection for standard vehicles with 2-second alert threshold
        self.system.configure_detection_vehicles(self.detection_mode)
        self.system.set_duration_threshold(self.threshold)
        
        try:
            print(" Initializing components...")
            self.system.detector = ObjectDetector()
            self.system.camera = Camera()
            self.system.processor = DetectionProcessor(detection_mode=self.detection_mode)
            self.system.session_start_time = time.time()
            print(" Detection system initialized!")
        except Exception as e:
            print(f" Initialization error: {e}")
            return
        
        print("\nDetection in progress...")
        print(f" Automatic shutdown after {self.threshold}s of continuous detection") 
        print(" Press 'q' to quit, 'r' for report\n")
        
        self.running = True
        
        # Main detection loop
        while self.running:
            try:
                # Capture frame from camera
                frame = self.system.camera.read_frame()
                
                # Detect and analyze vehicles in the frame
                results = self.system.detect_and_analyze(frame)
                
                # Stop if vehicle detected for 2+ seconds
                if results["threshold_reached"]:
                    print(" Stopping Vehicle detection ...")
                    self.stop()
                    break
                
                # Display the processed frame
                cv2.imshow('Vehicle Detection', results["processed_image"])
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    return True  # Signal to exit completely
                elif key == ord('r'):  # Show temporary report
                    self.system.show_report()
                
                return False  # Continue running
                    
            except Exception as e:
                print(f"Error: {e}")
                self.stop()

        
    