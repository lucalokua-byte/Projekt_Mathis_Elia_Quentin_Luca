import cv2
import time
import os
import sys

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
        print("\nStopping vehicle detection system...")
        self.running = False
        if hasattr(self.system, '_stop_system'):
            self.system._stop_system()
        cv2.destroyAllWindows()
    
    def run(self):
        #Main application loop
        print("Vehicle Detection System")
        print("=" * 40)
        
        # Configure detection for standard vehicles with 2-second alert threshold
        self.system.configure_detection_vehicles(self.detection_mode)
        self.system.set_stop_programme(self.threshold)
        
        # Initialize camera and detection components
        if not self.system.initialize_components():
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
                    self.system.execute_alert_actions(self.threshold)
                    break
                
                # Add detection timer and FPS overlay to frame
                frame_with_ui = self.system._add_overlays(
                    results["processed_image"], 
                    results["detection_duration"]
                )
                
                # Display the processed frame
                cv2.imshow('Vehicle Detection', frame_with_ui)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):  # Quit application
                    self.stop()
                elif key == ord('r'):  # Show temporary report
                    self.system.show_report()
                    
            except Exception as e:
                print(f"Error: {e}")
                self.stop()

        
    