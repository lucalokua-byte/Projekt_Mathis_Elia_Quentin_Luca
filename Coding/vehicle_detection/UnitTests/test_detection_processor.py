import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from detectors.detection_processor import DetectionProcessor

class TestDetectionProcessor(unittest.TestCase):
    
    def setUp(self):
        self.processor = DetectionProcessor()
    
    def test_is_vehicle_voiture(self):
        self.assertTrue(self.processor.is_vehicle("car"))
    
    def test_is_vehicle_camion(self):
        self.assertTrue(self.processor.is_vehicle("truck"))
    
    def test_is_vehicle_bus(self):
        self.assertTrue(self.processor.is_vehicle("bus"))
    
    def test_is_vehicle_personne(self):
        self.assertFalse(self.processor.is_vehicle("person"))
    
    def test_is_vehicle_chien(self):
        self.assertFalse(self.processor.is_vehicle("dog"))
    
    def test_is_vehicle_case_insensitive(self):
        self.assertTrue(self.processor.is_vehicle("CAR"))
        self.assertTrue(self.processor.is_vehicle("TrUcK"))
    
    def test_vehicle_keywords_initialisation(self):
        expected_keywords = ['car', 'truck', 'bus', 'vehicle']
        self.assertEqual(self.processor.vehicle_keywords, expected_keywords)

if __name__ == '__main__':
    unittest.main()