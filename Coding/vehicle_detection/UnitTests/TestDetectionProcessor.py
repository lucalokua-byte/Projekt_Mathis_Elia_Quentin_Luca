import unittest
import sys
import os
import cv2
import numpy as np
from unittest.mock import Mock, patch, MagicMock

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import your modules
from vehicle_detection.camera.camera_manager import Camera
from vehicle_detection.detectors.detection_processor import DetectionProcessor, ObjectDetector
from interface.Implementation_Systeme_Detection_Camera import CameraVehicleDetectionSystem


class TestDetectionProcessor(unittest.TestCase):
    
    def test_detection_modes(self):
        #Test numeric mode configurations (1, 2, 3)
        # Test mode 1 -> cars_only
        processor = DetectionProcessor("1")
        self.assertEqual(processor.vehicle_invalid, ['car'])
        
        # Test mode 2 -> standard_vehicles
        processor = DetectionProcessor("2")
        self.assertEqual(processor.vehicle_invalid, ['car', 'truck', 'bus'])
        
        # Test mode 3 -> all_vehicles
        processor = DetectionProcessor("3")
        self.assertEqual(processor.vehicle_invalid, ['car', 'truck', 'bus', 'motorcycle'])
    
    def test_car_detection(self):
        processor = DetectionProcessor("3")   # mode "all vehicles"

        # Crée un mock detection result avec un bounding_box complet
        mock_result = Mock()
        mock_category = Mock()
        mock_category.category_name = "car"
        mock_category.score = 0.8
        mock_detection = Mock()

        # Simule un bounding_box avec attributs numériques
        mock_bbox = Mock()
        mock_bbox.origin_x = 10
        mock_bbox.origin_y = 20
        mock_bbox.width = 100
        mock_bbox.height = 50
        mock_detection.bounding_box = mock_bbox

        mock_detection.categories = [mock_category]
        mock_result.detections = [mock_detection]

        _, detected = processor.process_detections(mock_result, np.zeros((480, 640, 3)))

        self.assertTrue(detected)


if __name__ == "__main__":
    unittest.main()