import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import urllib.request

class DetectionProcessor:
    """
    DETECTION PROCESSOR - Processes detection results and draws visual annotations
    """
    def __init__(self, detection_mode):
        # Define detection vehicles modes
        if detection_mode == "1":
            detection_mode = "cars_only"
        elif detection_mode == "2":
            detection_mode = "standard_vehicles"
        elif detection_mode == "3":
            detection_mode = "all_vehicles"
        modes = {
            "cars_only": ['car'],
            "standard_vehicles": ['car', 'truck', 'bus'],
            "all_vehicles": ['car', 'truck', 'bus', 'motorcycle']
        }
        self.vehicle_invalid = modes.get(detection_mode, modes)     # Default if detection_mode = invalid mode
    
    def process_detections(self, detection_result, frame):
        """
        Processes detection results and draws bounding boxes
        Returns processed frame and vehicle detection status
        """
        vehicle_detected = False 
        processed_frame = frame.copy()    # Copy required to work without altering the image 
        
        for detection in detection_result.detections:    # Traverse each detection found in the image
            category = detection.categories[0]           # Recover category from detection
            category_name = category.category_name       # Extract the name of the detected object (‘car’ or 'bus' etc)
            confidence = category.score                  # Retrieves the confidence score of the detection (between 0 and 1)
            confidence_percent = confidence * 100        # Converts the score into a percentage for greater readability
            
            # Check if it's a vehicle with at least 30% confidence
            is_vehicle = any(vehicle in category_name.lower() for vehicle in self.vehicle_invalid)
            
            if is_vehicle and confidence >= 0.3:
                if not vehicle_detected:
                    print(f" VEHICLE DETECTED! {confidence_percent:.1f}%")
                    vehicle_detected = True
            
            # Draw bounding box
            bbox = detection.bounding_box       # Bounding box coordinates for current detection
            start_point = (bbox.origin_x, bbox.origin_y)      # Top-left corner coordinates
            end_point = (bbox.origin_x + bbox.width, bbox.origin_y + bbox.height)      # Bottom-right corner = top-left + dimensions
            
            # Red for vehicles, green for other objects
            color = (0, 0, 255) if is_vehicle else (0, 255, 0)
            
            # Draw rectangle and label
            cv2.rectangle(processed_frame, start_point, end_point, color, 2)     # Draw bounding box rectangle around detected object
            cv2.putText(processed_frame, f"{category_name} {confidence_percent:.1f}%",      # Add label with category name and confidence percentage (if Bus detected, write 'Bus' in the box)
                       (bbox.origin_x, bbox.origin_y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)   # Font settings (=what writing)
        
        return processed_frame, vehicle_detected   # Return annotated frame and vehicle detection status
    
class ObjectDetector:
    """
    OBJECT DETECTOR
    Handles AI model loading and object detection using MediaPipe
    """

    def __init__(self, model_path='models\efficientdet_lite0.tflite', score_threshold=0.2):
        self.model_path = model_path
        self.score_threshold = score_threshold
        self.detector = None

        # Ensure model file exists and initialize detection engine
        self._download_model_if_needed()
        self._initialize_detector() 

    def _download_model_if_needed(self):
        """Download the AI model"""
        if not os.path.exists(self.model_path):                # Check if model file already exists to avoid redundant downloads
            print(" Downloading detection model...")

            # URL to the pre-trained EfficientDet Lite0 model from Google's MediaPipe
            url = "https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/int8/1/efficientdet_lite0.tflite"
            urllib.request.urlretrieve(url, self.model_path)     # Download and save the model file to specified path

    def _initialize_detector(self):
        """Initialize the MediaPipe object detector with configuration"""
        base_options = python.BaseOptions(model_asset_path=self.model_path)     # Configure base model options
        
        # Set detection parameters for video processing
        options = vision.ObjectDetectorOptions(
            base_options=base_options,
            score_threshold=self.score_threshold,      # Minimum confidence score for detections
            running_mode=vision.RunningMode.VIDEO      # Optimized for video stream processing
        )
        self.detector = vision.ObjectDetector.create_from_options(options)