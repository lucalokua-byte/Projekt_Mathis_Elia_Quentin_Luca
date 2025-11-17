import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import os
import urllib.request



class ObjectDetector:
    def __init__(self, model_path='efficientdet_lite0.tflite', score_threshold=0.2):
        self.model_path = model_path
        self.score_threshold = score_threshold
        self.detector = None
        self._download_model_if_needed()
        self._initialize_detector()
    
    def _download_model_if_needed(self):
        """Download the model if it doesn't exist"""
        if not os.path.exists(self.model_path):
            print("Downloading detection model...")
            url = "https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/int8/1/efficientdet_lite0.tflite"
            urllib.request.urlretrieve(url, self.model_path)
            print("Model downloaded!")
    
    def _initialize_detector(self):
        """Initialize the object detector"""
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.ObjectDetectorOptions(
            base_options=base_options,
            score_threshold=self.score_threshold,
            running_mode=vision.RunningMode.VIDEO
        )
        self.detector = vision.ObjectDetector.create_from_options(options)


class Camera:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self._initialize_camera()
    
    def _initialize_camera(self):
        """Initialize the camera"""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise Exception("Error: Cannot open camera")
    
    def read_frame(self):
        """Read a frame from the camera"""
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Error: Cannot read video stream")
        return frame
    
    def get_timestamp(self):
        """Get the current video timestamp"""
        return int(self.cap.get(cv2.CAP_PROP_POS_MSEC))
    
    def get_fps(self):
        """Get the current FPS"""
        return self.cap.get(cv2.CAP_PROP_FPS)
    
    def release(self):
        """Release camera resources"""
        if self.cap:
            self.cap.release()


class DetectionProcessor:
    def __init__(self):
        self.vehicle_keywords = ['car', 'truck', 'bus', 'vehicle']
    
    def is_vehicle(self, category_name):
        """Check if the detected category is a vehicle"""
        return any(vehicle in category_name.lower() for vehicle in self.vehicle_keywords)
    
    def process_detections(self, detection_result, frame):
        """
        Process detections and draw bounding boxes
        Returns a tuple (frame_processed, car_detected)
        """
        car_detected = False
        processed_frame = frame.copy()
        
        for detection in detection_result.detections:
            category = detection.categories[0]
            category_name = category.category_name
            confidence = category.score
            confidence_percent = confidence * 100
            
            # Check for vehicles with at least 30% confidence
            if self.is_vehicle(category_name) and confidence >= 0.3:
                if not car_detected:
                    print(f"CAR ALERT DETECTED! {confidence_percent:.1f}%")
                    car_detected = True
            
            # Draw bounding box
            self._draw_bounding_box(processed_frame, detection, category_name, confidence_percent)
        
        return processed_frame, car_detected
    
    def _draw_bounding_box(self, frame, detection, category_name, confidence_percent):
        """Draw bounding box and label on the image"""
        bbox = detection.bounding_box
        start_point = (bbox.origin_x, bbox.origin_y)
        end_point = (bbox.origin_x + bbox.width, bbox.origin_y + bbox.height)
        
        # Different color for vehicles
        color = (0, 0, 255) if self.is_vehicle(category_name) else (0, 255, 0)
        
        cv2.rectangle(frame, start_point, end_point, color, 2)
        cv2.putText(frame, f"{category_name} {confidence_percent:.1f}%", 
                   (bbox.origin_x, bbox.origin_y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)


class CarDetectionApp:
    def __init__(self):
        self.detector = ObjectDetector()
        self.camera = Camera()
        self.processor = DetectionProcessor()
        self.running = False
    
    def add_fps_to_frame(self, frame):
        """Add FPS counter to the frame"""
        fps = self.camera.get_fps()
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, frame.shape[0] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        return frame
    
    def convert_to_mediapipe_image(self, frame):
        """Convert OpenCV frame to MediaPipe format"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    def run(self):
        """Run the detection application"""
        print("Detection in progress...")
        print("CONSOLE ALERT for cars with +30% confidence")
        print("Press 'q' to quit")
        
        self.running = True
        
        while self.running:
            try:
                # Capture frame
                frame = self.camera.read_frame()
                
                # Convert for MediaPipe
                mp_image = self.convert_to_mediapipe_image(frame)
                
                # Detect objects
                timestamp = self.camera.get_timestamp()
                detection_result = self.detector.detector.detect_for_video(mp_image, timestamp)
                
                # Process detections
                processed_frame, car_detected = self.processor.process_detections(detection_result, frame)
                
                # Add FPS counter
                processed_frame = self.add_fps_to_frame(processed_frame)
                
                # Display the image
                cv2.imshow('Detection - Car Alert +30%', processed_frame)
                
                # Check for 'q' key to quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.stop()
                    
            except Exception as e:
                print(f"Error: {e}")
                self.stop()
    
    def stop(self):
        """Stop the application"""
        self.running = False
        self.camera.release()
        cv2.destroyAllWindows()
        print("Detection finished")