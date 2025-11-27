import unittest
import sys
import os
from unittest.mock import patch, MagicMock
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from detectors.object_detector import ObjectDetector

class TestObjectDetector(unittest.TestCase):
    
    @patch('detectors.object_detector.urllib.request.urlretrieve')
    @patch('detectors.object_detector.os.path.exists')
    @patch('detectors.object_detector.vision.ObjectDetector.create_from_options')
    def test_initialisation_detector(self, mock_create, mock_exists, mock_urlretrieve):
        # Simule que le modèle existe déjà
        mock_exists.return_value = True
        mock_create.return_value = MagicMock()
        
        detector = ObjectDetector()
        
        self.assertEqual(detector.model_path, 'efficientdet_lite0.tflite')
        self.assertEqual(detector.score_threshold, 0.2)
        self.assertIsNotNone(detector.detector)
    
    @patch('detectors.object_detector.urllib.request.urlretrieve')
    @patch('detectors.object_detector.os.path.exists')
    def test_download_model_quand_inexistant(self, mock_exists, mock_urlretrieve):
        # Simule que le modèle n'existe pas
        mock_exists.return_value = False
        
        detector = ObjectDetector()
        mock_urlretrieve.assert_called_once()

if __name__ == '__main__':
    unittest.main()