import unittest
from unittest.mock import patch, MagicMock, PropertyMock
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class TestObjectDetector(unittest.TestCase):

    @patch('detectors.object_detector.vision.ObjectDetector.create_from_options')
    @patch('detectors.object_detector.urllib.request.urlretrieve')
    @patch('detectors.object_detector.os.path.exists')
    @patch('detectors.object_detector.os.path.getsize')
    @patch('detectors.object_detector.os.makedirs')
    def test_download_when_missing(self, mock_makedirs, mock_getsize, mock_exists, mock_urlretrieve, mock_create_detector):
        """Test model download when file doesn't exist"""
        from detectors.object_detector import ObjectDetector
        
        # Setup mocks
        mock_exists.return_value = False  # File doesn't exist
        mock_getsize.return_value = 1000  # Fake file size
        mock_detector_instance = MagicMock()
        mock_create_detector.return_value = mock_detector_instance
        
        # Create detector
        detector = ObjectDetector(model_path='test_model.tflite')
        
        # Verify download was called
        mock_urlretrieve.assert_called_once()
        
        # Verify detector was initialized
        mock_create_detector.assert_called_once()
        
        # Verify properties
        self.assertEqual(detector.model_path, 'test_model.tflite')
        self.assertEqual(detector.score_threshold, 0.2)

    @patch('detectors.object_detector.vision.ObjectDetector.create_from_options')
    @patch('detectors.object_detector.os.path.exists')
    @patch('detectors.object_detector.os.path.getsize')
    def test_initialization_with_default_path(self, mock_getsize, mock_exists, mock_create_detector):
        """Test detector initialization with default path"""
        from detectors.object_detector import ObjectDetector
        
        # Setup mocks
        mock_exists.return_value = True  # File exists
        mock_getsize.return_value = 1000  # Fake file size
        mock_detector_instance = MagicMock()
        mock_create_detector.return_value = mock_detector_instance
        
        # Create detector
        detector = ObjectDetector()
        
        # Verify the path contains 'models'
        self.assertIn('models', detector.model_path)
        
        # Verify properties
        self.assertEqual(detector.score_threshold, 0.2)
        self.assertIsNotNone(detector.detector)

if __name__ == '__main__':
    unittest.main()