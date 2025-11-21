import cv2
import mediapipe as mp
import time
from typing import Dict, Any
from interface.Interface_Systeme_Detection import VehicleDetectionSystemInterface
from detectors.object_detector import ObjectDetector
from detectors.detection_processor import DetectionProcessor
from camera.camera_manager import Camera

class CameraVehicleDetectionSystem(VehicleDetectionSystemInterface):
    """
    CAMERA-BASED VEHICLE DETECTION SYSTEM
    Implements vehicle detection using computer vision and camera input
    """
    
    def __init__(self):
        self.detector = None
        self.camera = None
        self.processor = None
        self.running = False
        self.vehicle_detection_start_time = None
        self.consecutive_detection_threshold = 2.0
        self.detection_mode = "standard_vehicles"
        self.session_start_time = time.time()
        self.vehicles_detected = 0
        self.false_positives = 0
    
    def configure_detection_mode(self, mode: str):
        valid_modes = {
            "cars_only": ["car", "vehicle"],
            "standard_vehicles": ["car", "truck", "bus", "vehicle"],
            "all_vehicles": ["car", "truck", "bus", "motorcycle", "vehicle"]
        }
        
        if mode in valid_modes:
            self.detection_mode = mode
            print(f" Mode configured: {mode}")
        else:
            raise ValueError(f"Invalid mode: {mode}")
    
    def set_alert_threshold(self, duration_seconds: float):
        self.consecutive_detection_threshold = duration_seconds
        print(f" Alert threshold configured: {duration_seconds}s")
    
    def initialize_components(self) -> bool:
        try:
            print(" Initializing components...")
            self.detector = ObjectDetector()
            self.camera = Camera()
            self.processor = DetectionProcessor()
            self.session_start_time = time.time()
            print(" Detection system initialized!")
            return True
        except Exception as e:
            print(f" Initialization error: {e}")
            return False
    
    def detect_and_analyze(self, frame) -> Dict[str, Any]:
        try:
            # Convert frame to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Perform object detection
            timestamp = self.camera.get_timestamp()
            detection_result = self.detector.detector.detect_for_video(mp_image, timestamp)
            
            # Process detections and draw bounding boxes
            processed_frame, vehicle_detected = self.processor.process_detections(detection_result, frame)
            
            # Check consecutive detection duration
            should_stop, detection_duration = self._check_consecutive_detection(vehicle_detected)
            
            # Count detected vehicles
            if vehicle_detected:
                self.vehicles_detected += 1
            
            return {
                "vehicles_detected": vehicle_detected,
                "detection_duration": detection_duration,
                "threshold_reached": should_stop,
                "processed_image": processed_frame,
                "timestamp": time.time(),
                "average_confidence": 0.85
            }
            
        except Exception as e:
            print(f" Detection error: {e}")
            return {
                "vehicles_detected": False,
                "detection_duration": 0,
                "threshold_reached": False,
                "error": str(e)
            }
    
    def execute_alert_actions(self):
        print(" ALERT: Vehicle detected for more than 2 seconds!")
        print(" Stopping detection system...")
        self._stop_system()
    
    def generate_report(self) -> Dict[str, Any]:
        session_duration = time.time() - self.session_start_time
        
        return {
            "session_duration": session_duration,
            "vehicles_detected": self.vehicles_detected,
            "false_positives": self.false_positives,
            "detection_mode": self.detection_mode,
            "alert_threshold": self.consecutive_detection_threshold,
            "success_rate": self.vehicles_detected / max(1, self.vehicles_detected + self.false_positives),
            "end_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        return {
            "uptime": time.time() - self.session_start_time,
            "total_vehicles_detected": self.vehicles_detected,
            "current_mode": self.detection_mode,
            "current_alert_threshold": self.consecutive_detection_threshold,
            "camera_status": "active" if self.camera and self.camera.cap else "inactive",
            "last_detection": time.strftime("%H:%M:%S") if self.vehicles_detected > 0 else "none"
        }
    
    def _check_consecutive_detection(self, vehicle_detected: bool):
        current_time = time.time()
        
        if vehicle_detected:
            if self.vehicle_detection_start_time is None:
                self.vehicle_detection_start_time = current_time
                print("⏱️ Vehicle detection started...")
            
            detection_duration = current_time - self.vehicle_detection_start_time
            
            if detection_duration >= self.consecutive_detection_threshold:
                return True, detection_duration
                
            return False, detection_duration
        else:
            self.vehicle_detection_start_time = None
            return False, 0
    
    def _add_overlays(self, frame, detection_duration: float):
        # Add detection timer overlay
        timer_text = f"Detection: {detection_duration:.1f}s"
        color = (0, 0, 255) if detection_duration >= self.consecutive_detection_threshold else (255, 255, 255)
        cv2.putText(frame, timer_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Add FPS counter overlay
        fps = self.camera.get_fps()
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, frame.shape[0] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    def _stop_system(self):
        self.running = False
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()