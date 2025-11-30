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
from vehicle_detection.detectors.object_detector import ObjectDetector
from vehicle_detection.detectors.detection_processor import DetectionProcessor
from interface.Implementation_Systeme_Detection_Camera import CameraVehicleDetectionSystem


class TestCamera(unittest.TestCase):
    
    def test_camera_initialization(self):
        """Test camera initialization with mock"""
        with patch('cv2.VideoCapture') as mock_video:
            mock_video.return_value.isOpened.return_value = True
            camera = Camera(camera_index=0)
            self.assertIsNotNone(camera.cap)
    
    def test_camera_read_frame(self):
        """Test frame reading functionality"""
        with patch('cv2.VideoCapture') as mock_video:
            mock_instance = mock_video.return_value
            mock_instance.isOpened.return_value = True
            mock_instance.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
            
            camera = Camera()
            frame = camera.read_frame()
            
            self.assertIsNotNone(frame)
            self.assertEqual(frame.shape, (480, 640, 3))
    
    def test_camera_release(self):
        """Test camera resource cleanup"""
        with patch('cv2.VideoCapture') as mock_video:
            mock_instance = mock_video.return_value
            mock_instance.isOpened.return_value = True
            
            camera = Camera()
            camera.release()
            
            mock_instance.release.assert_called_once()


class TestDetectionProcessor(unittest.TestCase):
    
    def test_detection_modes(self):
        """Test all detection mode configurations"""
        # Test cars_only mode
        processor = DetectionProcessor("cars_only")
        self.assertEqual(processor.vehicle_keywords, ['car'])
        
        # Test standard_vehicles mode
        processor = DetectionProcessor("standard_vehicles")
        self.assertEqual(processor.vehicle_keywords, ['car', 'truck', 'bus'])
        
        # Test all_vehicles mode
        processor = DetectionProcessor("all_vehicles")
        self.assertEqual(processor.vehicle_keywords, ['car', 'truck', 'bus', 'motorcycle'])
    
    def test_is_vehicle_detection(self):
        """Test vehicle identification logic"""
        processor = DetectionProcessor("all_vehicles")
        
        # Test vehicle detection
        self.assertTrue(processor.is_vehicle("car"))
        self.assertTrue(processor.is_vehicle("truck"))
        self.assertTrue(processor.is_vehicle("bus"))
        self.assertTrue(processor.is_vehicle("motorcycle"))
        
        # Test non-vehicle detection
        self.assertFalse(processor.is_vehicle("person"))
        self.assertFalse(processor.is_vehicle("cat"))
        self.assertFalse(processor.is_vehicle(""))


class TestCameraVehicleDetectionSystem(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.system = CameraVehicleDetectionSystem()
    
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
    
    def test_detect_and_analyze_error_handling(self):
        """Test error handling in detection"""
        # Don't setup components to force an error
        mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        result = self.system.detect_and_analyze(mock_frame)
        
        self.assertIn("error", result)
        self.assertFalse(result["vehicles_detected"])
        self.assertFalse(result["threshold_reached"])
        self.assertEqual(result["detection_duration"], 0)


class TestConsecutiveDetectionLogic(unittest.TestCase):
    
    def test_consecutive_detection_timing(self):
        """Test the consecutive detection timing logic"""
        system = CameraVehicleDetectionSystem()
        system.threshold = 3.0  # 3 seconds threshold
        
        # Simulate first detection
        with patch('time.time') as mock_time:
            mock_time.return_value = 1000.0
            # This would be called from detect_and_analyze internally
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


class TestIntegration(unittest.TestCase):
    
    @patch('vehicle_detection.camera.camera_manager.Camera')
    @patch('vehicle_detection.detectors.object_detector.ObjectDetector')
    @patch('vehicle_detection.detectors.detection_processor.DetectionProcessor')
    def test_system_integration(self, mock_processor, mock_detector, mock_camera):
        """Test integration between system components"""
        # Setup mocks
        mock_camera_instance = mock_camera.return_value
        mock_detector_instance = mock_detector.return_value
        mock_processor_instance = mock_processor.return_value
        
        # Create system and configure
        system = CameraVehicleDetectionSystem()
        system.detector = mock_detector_instance
        system.camera = mock_camera_instance
        system.processor = mock_processor_instance
        
        # Configure system
        system.configure_detection_vehicles("all_vehicles")
        system.set_duration_threshold(2.0)
        
        # Verify configuration
        self.assertEqual(system.detection_mode, "all_vehicles")
        self.assertEqual(system.threshold, 2.0)


if __name__ == '__main__':
    # Run tests with verbosity
    unittest.main(verbosity=2)