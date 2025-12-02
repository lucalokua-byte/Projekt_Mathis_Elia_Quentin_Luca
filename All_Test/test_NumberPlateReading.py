import unittest
from unittest.mock import Mock, patch
import cv2
import numpy as np
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Coding.NumberPlateReading.NumberPlateRecognition import NumberPlateRecognition


class TestNumberPlateRecognition(unittest.TestCase):
    """Unit tests for NumberPlateRecognition class"""
    
    def setUp(self):
        """Setup test environment before each test"""
        # Create recognizer instance with test configuration
        self.recognizer = NumberPlateRecognition(confidence_threshold=0.8)

    def test_initialization(self):
        """Test that all attributes are correctly initialized"""
        # Verify confidence threshold is set correctly
        self.assertEqual(self.recognizer.confidence_threshold, 0.8)
        
        # Verify plate length constraints
        self.assertEqual(self.recognizer.min_plate_length, 4)
        self.assertEqual(self.recognizer.max_plate_length, 8)
        
        # Verify state flags
        self.assertFalse(self.recognizer.should_exit)
        self.assertIsNone(self.recognizer.final_confirmed_plate)
    
    def test_confidence_threshold_setting(self):
        """Test dynamic confidence threshold adjustment"""
        # Change threshold and verify update
        self.recognizer.set_confidence_threshold(0.75)
        self.assertEqual(self.recognizer.confidence_threshold, 0.75)
    
    def test_plate_confirmation_tracking(self):
        """Test plate confirmation requiring multiple detections"""
        test_plate = "TEST123"
        high_confidence = 0.9
        
        # First detection should not confirm
        confirmed, _ = self.recognizer.track_plate_confirmation(test_plate, high_confidence)
        self.assertFalse(confirmed)
        self.assertEqual(self.recognizer.confirmed_plates[test_plate]['count'], 1)
        
        # Second detection should not confirm
        confirmed, _ = self.recognizer.track_plate_confirmation(test_plate, high_confidence)
        self.assertFalse(confirmed)
        self.assertEqual(self.recognizer.confirmed_plates[test_plate]['count'], 2)
        
        # Third detection should confirm (3 consecutive detections)
        confirmed, _ = self.recognizer.track_plate_confirmation(test_plate, high_confidence)
        self.assertTrue(confirmed)
        self.assertEqual(self.recognizer.confirmed_plates[test_plate]['count'], 3)
    
    def test_plate_confirmation_low_confidence(self):
        """Test that low confidence plates are ignored"""
        test_plate = "LOW123"
        low_confidence = 0.5  # Below threshold of 0.8
        
        # Low confidence detection should be ignored
        confirmed, _ = self.recognizer.track_plate_confirmation(test_plate, low_confidence)
        self.assertFalse(confirmed)
        
        # Plate should not be tracked in confirmed_plates dictionary
        self.assertNotIn(test_plate, self.recognizer.confirmed_plates)
    
    def test_get_confirmed_plate(self):
        """Test retrieval of final confirmed plate"""
        # Test with no confirmed plate
        result = self.recognizer.get_confirmed_plate()
        self.assertIsNone(result)
        
        # Test with confirmed plate
        test_plate_data = {
            'text': 'CONFIRMED123',
            'confidence': 0.95,
            'coords': (100, 100, 200, 50),
            'timestamp': 1234567890
        }
        self.recognizer.final_confirmed_plate = test_plate_data
        
        result = self.recognizer.get_confirmed_plate()
        self.assertEqual(result['text'], 'CONFIRMED123')
        self.assertEqual(result['confidence'], 0.95)
        self.assertEqual(result['coords'], (100, 100, 200, 50))
    
    def test_delete_confirmed_plates(self):
        """Test cleanup of old/unconfirmed plates from tracking"""
        # Add test plates with different detection counts
        self.recognizer.confirmed_plates = {
            "PLATE1": {"count": 1},  # Should be removed (only 1 detection)
            "PLATE2": {"count": 3},  # Should remain (multiple detections)
            "PLATE3": {"count": 2},  # Should remain (multiple detections)
        }
        
        # Execute cleanup
        self.recognizer.cleanup_confirmed_plates()
        
        # Verify only plates with count > 1 remain
        self.assertNotIn("PLATE1", self.recognizer.confirmed_plates)
        self.assertIn("PLATE2", self.recognizer.confirmed_plates)
        self.assertIn("PLATE3", self.recognizer.confirmed_plates)
    
    def test_image_preprocessing(self):
        """Test plate image preprocessing for OCR"""
        # Create random color test image
        test_image = np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)
        
        # Process image
        processed_image = self.recognizer.preprocess_plate_image(test_image)
        
        # Verify output is grayscale (2D array)
        self.assertEqual(len(processed_image.shape), 2)
        self.assertEqual(processed_image.dtype, np.uint8)
    
    @patch('cv2.VideoCapture') # Mock OpenCV VideoCapture to not have to access real camera
    def test_camera_initialization_success(self, mock_video_capture):
        """Test successful camera initialization"""
        # Create mock camera that reports as opened
        mock_camera = Mock() # mock() creates a mock object as if to simulate a real one
        mock_camera.isOpened.return_value = True
        mock_video_capture.return_value = mock_camera
        
        # Initialize camera
        result = self.recognizer.initialize_camera()
        
        # Verify success
        self.assertTrue(result)
    
    @patch('cv2.VideoCapture')
    def test_camera_initialization_failure(self, mock_video_capture):
        """Test failed camera initialization"""
        # Create mock camera that reports as not opened
        mock_camera = Mock()
        mock_camera.isOpened.return_value = False
        mock_video_capture.return_value = mock_camera
        
        # Initialize camera
        result = self.recognizer.initialize_camera()
        
        # Verify failure
        self.assertFalse(result)
    
    @patch('cv2.resize')
    @patch('cv2.rectangle')
    @patch('cv2.putText')
    @patch('cv2.imshow')
    def test_process_frame_no_plates(self, mock_imshow, mock_puttext, mock_rectangle, mock_resize):
        """Test frame processing when no license plates are detected"""
        # Mock plate detector
        self.recognizer.plate_detector = Mock()
        
        # Create white test frame
        test_frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
        mock_resize.return_value = test_frame
        
        # Mock: No plates detected
        self.recognizer.plate_detector.detectMultiScale.return_value = []
        
        # Process frame
        result_frame, plate_text, confidence, confirmed = self.recognizer.process_frame(test_frame)
        
        # Verify empty results
        self.assertEqual(plate_text, "")
        self.assertEqual(confidence, 0.0)
        self.assertFalse(confirmed)
    
    @patch('pytesseract.image_to_data')
    @patch('cv2.resize')
    @patch('cv2.rectangle')
    @patch('cv2.putText')
    @patch('cv2.imshow')
    def test_process_frame_with_plate(self, mock_imshow, mock_puttext, mock_rectangle, mock_resize, mock_tesseract):
        """Test frame processing with detected license plate"""
        # Mock plate detector
        self.recognizer.plate_detector = Mock()
        
        # Create white test frame
        test_frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
        mock_resize.return_value = test_frame
        
        # Mock: One plate detected at position (100, 100, 200, 50)
        self.recognizer.plate_detector.detectMultiScale.return_value = [(100, 100, 200, 50)]
        
        # Mock Tesseract OCR response
        mock_tesseract.return_value = {
            'text': ['ABC', '123'],  # Detected text parts
            'conf': [90, 85]         # Confidence scores in percentage
        }
        
        # Mock internal text extraction method
        with patch.object(self.recognizer, 'extract_text_from_plate') as mock_extract:
            mock_extract.return_value = (
                "ABC123",            # Combined plate text
                0.9,                 # Confidence score
                np.ones((50, 200), dtype=np.uint8)  # Plate image
            )
            
            # Process frame
            result_frame, plate_text, confidence, confirmed = self.recognizer.process_frame(test_frame)
        
        # Verify plate detection results
        self.assertEqual(plate_text, "ABC123")
        self.assertEqual(confidence, 0.9)
        self.assertFalse(confirmed)  # Not confirmed after first detection
    
    def test_empty_string_plate(self):
        """Test handling of empty plate text"""
        # Empty text should not be confirmed regardless of confidence
        confirmed, _ = self.recognizer.track_plate_confirmation("", 0.9)
        self.assertFalse(confirmed)
    
    def test_very_short_plate(self):
        """Test handling of plates shorter than minimum length"""
        short_plate = "A12"  # Only 3 characters
        
        # Mock the plate detection to simulate short plate
        confirmed, _ = self.recognizer.track_plate_confirmation(short_plate, 0.9)
        # Should not confirm due to invalid length
        self.assertFalse(confirmed)
    
    def test_very_long_plate(self):
        """Test handling of plates longer than maximum length"""
        long_plate = "VERYLONG123456"  # 14 characters
        
        # Mock the plate detection to simulate long plate
        confirmed, _ = self.recognizer.track_plate_confirmation(long_plate, 0.9)
        
        # Should not confirm due to invalid length
        self.assertFalse(confirmed)


if __name__ == '__main__':
    """Run all tests with detailed output"""
    unittest.main(verbosity=2) # 0 = shows only total tests and failures, 1 = shows dots for each test, 2 = shows detailed info for each test