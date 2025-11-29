import unittest
from unittest.mock import Mock, patch
import cv2
import numpy as np
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from NumberPlateReading.NumberPlateRecognition import NumberPlateRecognition


class TestNumberPlateRecognitionSimple(unittest.TestCase):
    """Einfache Unit Tests für die wichtigsten Funktionen der Nummernschild-Erkennung"""

    def setUp(self):
        """Setup für jeden Test"""
        self.recognizer = NumberPlateRecognition(confidence_threshold=0.8)

    def test_initialization(self):
        """Testet die grundlegende Initialisierung"""
        self.assertEqual(self.recognizer.confidence_threshold, 0.8)
        self.assertEqual(self.recognizer.min_plate_length, 4)
        self.assertEqual(self.recognizer.max_plate_length, 8)
        self.assertFalse(self.recognizer.should_exit)
        self.assertIsNone(self.recognizer.final_confirmed_plate)

    def test_plate_confirmation_tracking(self):
        """Testet das Bestätigungs-Tracking"""
        plate_text = "TEST123"
        confidence = 0.9
        
        # Erste Erkennung - nicht bestätigt
        confirmed, _ = self.recognizer.track_plate_confirmation(plate_text, confidence)
        self.assertFalse(confirmed)
        self.assertEqual(self.recognizer.confirmed_plates[plate_text]['count'], 1)

        # Zweite Erkennung - nicht bestätigt
        confirmed, _ = self.recognizer.track_plate_confirmation(plate_text, confidence)
        self.assertFalse(confirmed)
        self.assertEqual(self.recognizer.confirmed_plates[plate_text]['count'], 2)

        # Dritte Erkennung - bestätigt
        confirmed, _ = self.recognizer.track_plate_confirmation(plate_text, confidence)
        self.assertTrue(confirmed)
        self.assertEqual(self.recognizer.confirmed_plates[plate_text]['count'], 3)

    def test_plate_confirmation_low_confidence(self):
        """Testet Bestätigung mit niedriger Confidence"""
        plate_text = "TEST123"
        low_confidence = 0.5  # Unter Threshold 0.8
        
        confirmed, _ = self.recognizer.track_plate_confirmation(plate_text, low_confidence)
        self.assertFalse(confirmed)
        self.assertNotIn(plate_text, self.recognizer.confirmed_plates)

    def test_confidence_threshold_setting(self):
        """Testet das Setzen des Confidence Thresholds"""
        self.recognizer.set_confidence_threshold(0.75)
        self.assertEqual(self.recognizer.confidence_threshold, 0.75)

    def test_image_preprocessing(self):
        """Testet die Bildvorverarbeitung"""
        # Erstelle ein Testbild
        test_image = np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)
        
        processed_image = self.recognizer.preprocess_plate_image(test_image)
        
        # Überprüfe dass das Ergebnis ein Graustufenbild ist
        self.assertEqual(len(processed_image.shape), 2)  # Sollte 2D sein (Graustufen)
        self.assertEqual(processed_image.dtype, np.uint8)

    def test_detection_status(self):
        """Testet den Erkennungsstatus"""
        status = self.recognizer.get_detection_status()
        
        self.assertIn('detected_plate', status)
        self.assertIn('confidence', status)
        self.assertIn('is_confirmed', status)
        self.assertIn('status_message', status)
        self.assertIn('frame_count', status)

    def test_get_confirmed_plate(self):
        """Testet das Abrufen des bestätigten Nummernschilds"""
        # Kein bestätigtes Nummernschild
        result = self.recognizer.get_confirmed_plate()
        self.assertIsNone(result)
        
        # Mit bestätigtem Nummernschild
        test_plate = {
            'text': 'TEST123',
            'confidence': 0.95,
            'coords': (100, 100, 200, 50),
            'timestamp': 1234567890
        }
        self.recognizer.final_confirmed_plate = test_plate
        
        result = self.recognizer.get_confirmed_plate()
        self.assertEqual(result['text'], 'TEST123')
        self.assertEqual(result['confidence'], 0.95)

    @patch('cv2.VideoCapture')
    def test_camera_initialization_success(self, mock_video_capture):
        """Testet erfolgreiche Kamera-Initialisierung"""
        mock_camera = Mock()
        mock_camera.isOpened.return_value = True
        mock_video_capture.return_value = mock_camera

        result = self.recognizer.initialize_camera()
        self.assertTrue(result)

    @patch('cv2.VideoCapture')
    def test_camera_initialization_failure(self, mock_video_capture):
        """Testet fehlgeschlagene Kamera-Initialisierung"""
        mock_camera = Mock()
        mock_camera.isOpened.return_value = False
        mock_video_capture.return_value = mock_camera

        result = self.recognizer.initialize_camera()
        self.assertFalse(result)

    def test_cleanup_confirmed_plates(self):
        """Testet das Bereinigen der bestätigten Nummernschilder"""
        # Füge Testdaten hinzu
        self.recognizer.confirmed_plates = {
            "PLATE1": {"count": 1},  # Sollte entfernt werden
            "PLATE2": {"count": 3},  # Sollte bleiben
            "PLATE3": {"count": 2},  # Sollte bleiben
        }
        
        self.recognizer.cleanup_confirmed_plates()
        
        self.assertNotIn("PLATE1", self.recognizer.confirmed_plates)
        self.assertIn("PLATE2", self.recognizer.confirmed_plates)
        self.assertIn("PLATE3", self.recognizer.confirmed_plates)


class TestNumberPlateRecognitionMocked(unittest.TestCase):
    """Tests mit gemockten Abhängigkeiten"""

    def setUp(self):
        self.recognizer = NumberPlateRecognition()
        self.recognizer.plate_detector = Mock()

    @patch('cv2.resize')
    @patch('cv2.rectangle')
    @patch('cv2.putText')
    @patch('cv2.imshow')
    def test_process_frame_no_plates(self, mock_imshow, mock_puttext, mock_rectangle, mock_resize):
        """Testet Frame-Verarbeitung ohne erkannte Nummernschilder"""
        # Mock Frame
        test_frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
        mock_resize.return_value = test_frame
        
        # Mock - keine Plates gefunden
        self.recognizer.plate_detector.detectMultiScale.return_value = []
        
        result_frame, plate_text, confidence, confirmed = self.recognizer.process_frame(test_frame)
        
        self.assertEqual(plate_text, "")
        self.assertEqual(confidence, 0.0)
        self.assertFalse(confirmed)

    @patch('pytesseract.image_to_data')
    @patch('cv2.resize')
    @patch('cv2.rectangle')
    @patch('cv2.putText')
    @patch('cv2.imshow')
    def test_process_frame_with_plate(self, mock_imshow, mock_puttext, mock_rectangle, mock_resize, mock_tesseract):
        """Testet Frame-Verarbeitung mit erkanntem Nummernschild"""
        # Mock Frame
        test_frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
        mock_resize.return_value = test_frame
        
        # Mock - ein Plate gefunden
        self.recognizer.plate_detector.detectMultiScale.return_value = [(100, 100, 200, 50)]
        
        # Mock Tesseract OCR
        mock_tesseract.return_value = {
            'text': ['ABC', '123'],
            'conf': [90, 85]
        }
        
        # Mock extract_text_from_plate um konsistente Daten zurückzugeben
        with patch.object(self.recognizer, 'extract_text_from_plate') as mock_extract:
            mock_extract.return_value = ("ABC123", 0.9, np.ones((50, 200), dtype=np.uint8))
            
            result_frame, plate_text, confidence, confirmed = self.recognizer.process_frame(test_frame)
        
        self.assertEqual(plate_text, "ABC123")
        self.assertEqual(confidence, 0.9)
        self.assertFalse(confirmed)  # Noch nicht bestätigt nach erstem Frame


if __name__ == '__main__':
    # Einfachen Test-Runner erstellen
    unittest.main(verbosity=2)