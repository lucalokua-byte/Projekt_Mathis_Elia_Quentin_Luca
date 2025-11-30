import cv2
import mediapipe as mp
import time
from typing import Dict, Any
from interface.Interface_Systeme_Detection import VehicleDetectionSystemInterface
from vehicle_detection.detectors.object_detector import ObjectDetector
from vehicle_detection.camera.camera_manager import Camera
from vehicle_detection.detectors.detection_processor import DetectionProcessor

class CameraVehicleDetectionSystem(VehicleDetectionSystemInterface):
    """
    CAMERA-BASED VEHICLE DETECTION SYSTEM
    Implements vehicle detection using computer vision and camera input
    """
    
    def __init__(self):
        self.detector = None
        self.camera = None
        self.processor = None
        self.vehicle_detection_start_time = None
        self.threshold = None
        self.detection_mode = None     
        self.vehicles_detected = 0
        self.session_start_time = None
        self.detector = ObjectDetector()
        self.camera = Camera()
        self.processor = DetectionProcessor(detection_mode=self.detection_mode)
    
    def configure_detection_vehicles(self, vehicles: str):
        valid_vehicles = {
            "cars_only": ["car", "vehicle"],
            "standard_vehicles": ["car", "truck", "bus", "vehicle"],
            "all_vehicles": ["car", "truck", "bus", "motorcycle", "vehicle"]
        }
        
        if vehicles in valid_vehicles:
            self.detection_mode = vehicles
            print(f" Vehicles configured: {vehicles}")
        else:
            raise ValueError(f"Invalid vehicles: {vehicles}")
    
    def set_duration_threshold(self, duration_seconds: float):
        self.threshold = duration_seconds
        print(f" Threshold configured: {duration_seconds}s")      
    
    def detect_and_analyze(self, frame) -> Dict[str, Any]:
        try:
            current_time = time.time()
            should_stop = False
            detection_duration = 0.0        

            # Convert frame to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Perform object detection
            timestamp = self.camera.get_timestamp()
            detection_result = self.detector.detector.detect_for_video(mp_image, timestamp)
            
            # Process detections and draw bounding boxes
            processed_frame, vehicle_detected = self.processor.process_detections(detection_result, frame)
            
            # Check consecutive detection duration       
            if vehicle_detected:
                if self.vehicle_detection_start_time is None:
                    self.vehicle_detection_start_time = current_time
                    print(" Vehicle detection started...")
                
                detection_duration = current_time - self.vehicle_detection_start_time
                
                if detection_duration >= self.threshold:
                     should_stop, detection_duration = True, detection_duration
            else:
                self.vehicle_detection_start_time = None

            
            # Count detected vehicles
            if vehicle_detected:
                self.vehicles_detected += 1
            
            return {
                "vehicles_detected": vehicle_detected,
                "detection_duration": detection_duration,
                "threshold_reached": should_stop,
                "processed_image": processed_frame,
                "timestamp": current_time,
            }
            
        except Exception as e:
            print(f" Detection error: {e}")
            return {
                "vehicles_detected": False,
                "detection_duration": 0,
                "threshold_reached": False,
                "error": str(e)
            }
    
    def show_report(self):
        """Display a temporary detection report"""
        try:
            print("\n" + "=" * 50)
            print("TEMPORARY DETECTION REPORT")
            print("=" * 50)
            
            # Display information
            print(f" Session duration: {time.time() - self.session_start_time:.1f} seconds")
            print(f" Vehicles detected: {self.vehicles_detected}")
            print(f" Detection mode: {self.detection_mode}")
            print(f" Alert threshold: {self.threshold} seconds")
            print(f" Report generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("=" * 50)
            print("Press any key to continue detection...")
        
        except Exception as e:
            print(f"Error generating report: {e}")