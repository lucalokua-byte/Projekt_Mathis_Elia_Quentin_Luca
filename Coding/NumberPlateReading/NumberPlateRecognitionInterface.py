from abc import ABC, abstractmethod
import cv2
import pytesseract
import os
import re
import time

class NumberPlateRecognizer(ABC):
    """Interface for Number Plate Recognition Systems"""
    
    @abstractmethod
    def initialize_camera(self) -> bool:
        """Initialize camera for capturing frames"""
        pass
    
    @abstractmethod
    def process_frame(self, frame):
        """Process a single frame to detect and read number plates"""
        pass
    
    @abstractmethod
    def extract_text_from_plate(self, plate_img):
        """Extract text from the detected plate"""
        pass
    
    @abstractmethod
    def begin_plate_detection(self):
        """Start the plate detection process"""
        pass
    
    @abstractmethod
    def get_detection_status(self) -> dict:
        """Get the current detection status"""
        pass
    
    @abstractmethod
    def set_confidence_threshold(self, threshold: float):
        """Set the confidence threshold for plate recognition"""
        pass
    
    @abstractmethod
    def get_confirmed_plate(self) -> dict:
        """Get the final confirmed plate information"""
        pass