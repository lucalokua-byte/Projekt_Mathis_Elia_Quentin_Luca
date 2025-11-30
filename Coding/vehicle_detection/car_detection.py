import cv2
import time
import os
import sys
from vehicle_detection.detectors.detection_processor import ObjectDetector
from vehicle_detection.detectors.detection_processor import DetectionProcessor
from vehicle_detection.camera.camera_manager import Camera

sys.path.append(os.path.dirname(os.path.abspath(__file__)))  #Add current directory to Python path to import local modules


from interface.Implementation_Systeme_Detection_Camera import CameraVehicleDetectionSystem  #Import the vehicle detection system implementation

class CarDetectionApp:
    """
    MAIN VEHICLE DETECTION APPLICATION
    Uses camera to detect vehicles and automatically stops after n seconds of continuous detection

    Select the desired detection vehicle mode and threshold duration
    """
    
    def __init__(self):
        # Initialize the detection system
        self.system = CameraVehicleDetectionSystem()
        self.running = False
        self.threshold = 1.0                  # Select the threshold duration in seconds before the car detection programme stops
        self.detection_mode = "2"  # Select the desired detection vehicles mode: 1 = cars_only, 2 = standard_vehicles, 3 = all_vehicles
    
    def stop(self):
        #Stop the application gracefully
        self.running = False             #Set running flag to False to exit main loop
        if self.system.camera:           #Release camera resources
            self.system.camera.release()
        cv2.destroyAllWindows()          #Close all OpenCV windows
    
    def run(self):
        #Main application loop
        print("Vehicle Detection System")
        print("=" * 40)
        
        self.system.configure_detection_vehicles(self.detection_mode)    # Configure detection X-second threshold duration
        self.system.set_duration_threshold(self.threshold)               # Configure detection for desired detection vehicles mode
        
        # Initialize components
        try:
            print(" Initializing components...")
            self.system.detector = ObjectDetector()         # Initialize object detector
            self.system.camera = Camera()            # Initialize camera manager
            self.system.processor = DetectionProcessor(detection_mode=self.detection_mode) # Initialize detection processor
            self.system.session_start_time = time.time()      # Record session start time
            print(" Detection system initialized!")
        except Exception as e:                 #Handle initialization errors
            print(f" Initialization error: {e}")
            return
        
        print("\nDetection in progress...")
        print(f" Automatic shutdown after {self.threshold}s of continuous detection") 
        print(" Press 'q' to quit, 'r' for report\n")
        
        self.running = True         # Set running flag to True to start main loop
        
        # Main detection loop
        while self.running:
            try:
                frame = self.system.camera.read_frame()         # Read frame from camera
                results = self.system.detect_and_analyze(frame)      # Call the detect_and_analyze method
                
                # Stop if vehicle detected for X- seconds
                if results["threshold_reached"]:
                    print(" Stopping Vehicle detection ...")
                    self.stop()
                    break
                
                cv2.imshow('Vehicle Detection', results["processed_image"])        # Show processed image in a window
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF  # Wait for key press
                if key == ord('q'):    # Quit application
                    self.stop()
                elif key == ord('r'):  # Show temporary report
                    self.system.show_report() # Display detection report
                    
            except Exception as e:
                print(f"Error: {e}")
                self.stop()

        
    