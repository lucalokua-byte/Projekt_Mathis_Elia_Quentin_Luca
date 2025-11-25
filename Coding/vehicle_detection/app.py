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
    Uses camera to detect vehicles and automatically stops after 2 seconds of continuous detection
    """
    
    def __init__(self):
        # Initialize the detection system
        self.system = CameraVehicleDetectionSystem()
        self.running = False
    
    def run(self):
        """Main application loop"""
        print("Vehicle Detection System")
        print("=" * 40)
        
        # Configure detection for standard vehicles with 2-second alert threshold
        self.system.configure_detection_mode("standard_vehicles")
        self.system.set_alert_threshold(2.0)
        
        # Initialize camera and detection components
        if not self.system.initialize_components():
            return
        
        print("\nDetection in progress...")
        print("• Alerts for vehicles with >30% confidence")
        print("• Automatic shutdown after 2s of continuous detection") 
        print("• Press 'q' to quit, 'r' for report\n")
        
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
                    self.system.execute_alert_actions()
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
                    self.show_report()
                    
            except Exception as e:
                print(f"Error: {e}")
                self.stop()
    

    # def show_report(self):
    #     """Display temporary performance statistics"""
    #     stats = self.system.get_performance_stats()
    #     print("\nTEMPORARY REPORT:")
    #     print(f"   Uptime: {stats['uptime']:.1f}s")
    #     print(f"   Vehicles detected: {stats['total_vehicles_detected']}")
    #     print(f"   Mode: {stats['current_mode']}")
    #     print(f"   Camera status: {stats['camera_status']}")
    
    # def stop(self):
    #     """Stop the application and generate final report"""
    #     self.running = False
        
    #     # Generate final session report
    #     final_report = self.system.generate_report()
        
    #     print("\nFINAL REPORT:")
    #     print(f"   Session duration: {final_report['session_duration']:.1f}s")
    #     print(f"   Vehicles detected: {final_report['vehicles_detected']}")
    #     print(f"   Success rate: {final_report['success_rate']:.1%}")
    #     print(f"   End time: {final_report['end_timestamp']}")
        
    #     # Cleanup resources
    #     if self.system.camera:
    #         self.system.camera.release()
    #     cv2.destroyAllWindows()
    #     print("Application terminated")