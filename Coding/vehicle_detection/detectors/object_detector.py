import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import os
import urllib.request

class ObjectDetector:
    """
    OBJECT DETECTOR
    Handles AI model loading and object detection using MediaPipe
    """
    
    def __init__(self, model_path='models\efficientdet_lite0.tflite', score_threshold=0.2):
        self.model_path = model_path
        self.score_threshold = score_threshold
        self.detector = None
        self._download_model_if_needed()
        self._initialize_detector() 
    
    def _download_model_if_needed(self):
        """Download the AI model"""
        if not os.path.exists(self.model_path):
            print(" Downloading detection model...")
            url = "https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/int8/1/efficientdet_lite0.tflite"
            urllib.request.urlretrieve(url, self.model_path)
    
    def _initialize_detector(self):
        """Initialize the MediaPipe object detector with configuration"""
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.ObjectDetectorOptions(
            base_options=base_options,
            score_threshold=self.score_threshold,
            running_mode=vision.RunningMode.VIDEO
        )
        self.detector = vision.ObjectDetector.create_from_options(options)