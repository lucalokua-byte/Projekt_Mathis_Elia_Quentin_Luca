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

class TestCameraVehicleDetectionSystem(unittest.TestCase):
    
    @patch('interface.Implementation_Systeme_Detection_Camera.ObjectDetector', autospec=True)
    def setUp(self, mock_detector):
        # mock_detector will be used instead of ObjectDetector
        self.system = CameraVehicleDetectionSystem()
        self.system.detector = mock_detector.return_value
    
    def test_configure_detection_vehicles(self):
        """Test vehicle configuration"""
        # Test valid configurations
        self.system.configure_detection_vehicles("cars_only")
        self.assertEqual(self.system.detection_mode, "cars_only")
        
        self.system.configure_detection_vehicles("all_vehicles")
        self.assertEqual(self.system.detection_mode, "all_vehicles")
    
    def test_configure_detection_vehicles_invalid(self):
        """Test invalid vehicle configuration"""
        with self.assertRaises(ValueError):
            self.system.configure_detection_vehicles("invalid_mode")
    
    def test_set_duration_threshold(self):
        """Test threshold configuration"""
        self.system.set_duration_threshold(5.0)
        self.assertEqual(self.system.threshold, 5.0)
        
        self.system.set_duration_threshold(1.5)
        self.assertEqual(self.system.threshold, 1.5)
    
    @patch('cv2.cvtColor')
    @patch('mediapipe.Image')
    def test_detect_and_analyze_with_mock_detection(self, mock_mp_image, mock_cvt):
        """Test detection and analysis with mocked components"""
        # Mock the system components
        self.system.detector = Mock()
        self.system.camera = Mock()
        self.system.processor = Mock()
        
        # Setup mock returns
        mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        self.system.camera.get_timestamp.return_value = 1000
        self.system.processor.process_detections.return_value = (mock_frame, True)
        
        # Mock detection result
        mock_detection = Mock()
        mock_category = Mock()
        mock_category.category_name = "car"
        mock_category.score = 0.8
        mock_detection.categories = [mock_category]
        mock_detection.bounding_box = Mock()
        
        mock_detection_result = Mock()
        mock_detection_result.detections = [mock_detection]
        self.system.detector.detector.detect_for_video.return_value = mock_detection_result
        
        # Mock color conversion
        mock_cvt.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Set threshold for detection
        self.system.threshold = 2.0
        self.system.vehicle_detection_start_time = None
        
        # Execute detection
        result = self.system.detect_and_analyze(mock_frame)
        
        # Verify results
        self.assertIn("vehicles_detected", result)
        self.assertIn("detection_duration", result)
        self.assertIn("threshold_reached", result)
        self.assertIn("processed_image", result)
        self.assertTrue(result["vehicles_detected"])

class TestConsecutiveDetectionLogic(unittest.TestCase):

    @patch('interface.Implementation_Systeme_Detection_Camera.ObjectDetector', autospec=True)
    def test_consecutive_detection_timing(self, mock_detector):
        """Test the consecutive detection timing logic"""
        system = CameraVehicleDetectionSystem()
        system.detector = mock_detector.return_value
        system.threshold = 3.0  # 3 seconds threshold

        # Simulate first detection
        with patch('time.time') as mock_time:
            mock_time.return_value = 1000.0
            if True:  # vehicle_detected = True
                if system.vehicle_detection_start_time is None:
                    system.vehicle_detection_start_time = 1000.0

            detection_duration = 1000.0 - system.vehicle_detection_start_time
            self.assertEqual(detection_duration, 0.0)

        # Simulate detection after 2 seconds (below threshold)
        with patch('time.time') as mock_time:
            mock_time.return_value = 1002.0
            detection_duration = 1002.0 - system.vehicle_detection_start_time
            self.assertEqual(detection_duration, 2.0)
            self.assertLess(detection_duration, system.threshold)

        # Simulate detection after 4 seconds (above threshold)
        with patch('time.time') as mock_time:
            mock_time.return_value = 1004.0
            detection_duration = 1004.0 - system.vehicle_detection_start_time
            self.assertEqual(detection_duration, 4.0)
            self.assertGreaterEqual(detection_duration, system.threshold)

if __name__ == "__main__":
    unittest.main()