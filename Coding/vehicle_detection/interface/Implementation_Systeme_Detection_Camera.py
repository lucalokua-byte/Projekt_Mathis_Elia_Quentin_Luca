import cv2
import mediapipe as mp
import time
from typing import Dict, Any
from interface.Interface_Systeme_Detection import VehicleDetectionSystemInterface
from vehicle_detection.detectors.detection_processor import ObjectDetector
from vehicle_detection.camera.camera_manager import Camera
from vehicle_detection.detectors.detection_processor import DetectionProcessor

class CameraVehicleDetectionSystem(VehicleDetectionSystemInterface):
    """
    CAMERA-BASED VEHICLE DETECTION SYSTEM
    Implements vehicle detection using computer vision and camera input
    """
    
    def __init__(self):
        self.vehicle_detection_start_time = None
        self.threshold = None
        self.detection_mode = None     
        self.vehicles_detected = 0
        self.session_start_time = None
        self.detector = ObjectDetector()
        self.camera = Camera()
        self.processor = DetectionProcessor(detection_mode=self.detection_mode)
    
    def configure_detection_vehicles(self, vehicles: int):
        if vehicles == "1":
            vehicles = "cars_only"
        elif vehicles == "2":
            vehicles = "standard_vehicles"
        elif vehicles == "3":
            vehicles = "all_vehicles"
        valid_vehicles = {
            "cars_only": ["car", "vehicle"],                                #cars_only
            "standard_vehicles": ["car", "truck", "bus", "vehicle"],                #standard_vehicles
            "all_vehicles": ["car", "truck", "bus", "motorcycle", "vehicle"]   #all_vehicles
        }
        
        if vehicles in valid_vehicles:                #Valid vehicle configuration
            self.detection_mode = vehicles                #Set detection mode
            print(f" Vehicles configured: {vehicles}")
        else:
            raise ValueError(f"Invalid vehicles: {vehicles}")      #Raise error for invalid configuration
    
    def set_duration_threshold(self, duration_seconds: float):     
        self.threshold = duration_seconds      
        print(f" Threshold configured: {self.threshold}s")      
    
    def detect_and_analyze(self, frame) -> Dict[str, Any]:
        try:
            current_time = time.time()    # Get current timestamp
            should_stop = False        # Flag to indicate if threshold is reached
            detection_duration = 0.0        # Duration of continuous detection

            # Convert frame to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)                #Convert OpenCV BGR to standard RGB for MediaPipe color format compatibility
            mp_image = mp.Image(image_format = mp.ImageFormat.SRGB, data = rgb_frame)        #creating a MediaPipe Image object from the OpenCV frame
            
            # Perform object detection
            timestamp = self.camera.get_timestamp()    # Get current timestamp from camera
            detection_result = self.detector.detector.detect_for_video(mp_image, timestamp)  # detect_for_video() = a native MediaPipe method that detects objects in a video frame
            
            processed_frame, vehicle_detected = self.processor.process_detections(detection_result, frame)    # Process detection results
            
            # Check consecutive detection duration       
            if vehicle_detected:
                if self.vehicle_detection_start_time is None:
                    self.vehicle_detection_start_time = current_time   # Start timing
                    print(" Vehicle detection started...")
                
                detection_duration = current_time - self.vehicle_detection_start_time   # Calculate detection duration
                
                if detection_duration >= self.threshold:             # Check if threshold is reached
                     should_stop, detection_duration = True, detection_duration    # Threshold reached
            else:
                self.vehicle_detection_start_time = None    # Reset timing if no vehicle detected

            # Count detected vehicles
            if vehicle_detected:
                self.vehicles_detected += 1    # Increment vehicle count
            
            return {
                "vehicles_detected": vehicle_detected,       # Vehicle detection status
                "detection_duration": detection_duration,    # Duration of continuous detection
                "threshold_reached": should_stop,            # Threshold status
                "processed_image": processed_frame,          # Processed frame with annotations
                "timestamp": current_time,                   # Current timestamp
            }
            
        except Exception as e:           # Handle detection errors
            print(f" Detection error: {e}")
            return {
                "vehicles_detected": False,
                "detection_duration": 0,
                "threshold_reached": False,
                "error": str(e)        # Return error details
            }
    
    def show_report(self):
        """Display a temporary detection report"""
        try:
            print("\n" + "=" * 50)
            print("TEMPORARY DETECTION REPORT")
            print("=" * 50)
            
            # Display information
            print(f" Session duration: {time.time() - self.session_start_time:.1f} seconds")   #Total session duration
            print(f" Vehicles detected: {self.vehicles_detected}")                        #Total number of vehicles detected during the session
            print(f" Detection mode: {self.detection_mode}")                              #Configured detection mode we have selected
            print(f" Threshold: {self.threshold} seconds")                                # Threshold we have selected
            print(f" Report generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}")          #Timestamp
            
            print("=" * 50)
            print("Press any key to continue detection...")
        
        except Exception as e:
            print(f"Error generating report: {e}")