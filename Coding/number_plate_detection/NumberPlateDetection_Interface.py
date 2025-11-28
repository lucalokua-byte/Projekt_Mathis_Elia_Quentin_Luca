from abc import ABC, abstractmethod
from typing import List, Dict, Any
import cv2

class NumberPlateDetection(ABC):
    #Abstract interface for number plate detection systems    
    @abstractmethod
    def setup(self) -> bool:
        """Initialize the detection system"""
        pass
    
    @abstractmethod
    def preprocess_image(self, image) -> Any:
        """Preprocess image for better detection"""
        pass
    
    @abstractmethod
    def detect_plate_regions(self, image) -> List[Any]:
        """Detect potential plate regions in image"""
        pass
    
    @abstractmethod
    def extract_plate_text(self, plate_image) -> str:
        """Extract text from plate region"""
        pass
    
    @abstractmethod
    def recognize_from_frame(self, frame) -> List[Dict[str, Any]]:
        """Main method to recognize plates from frame"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Cleanup resources"""
        pass