import unittest
import sys
import os
from unittest.mock import patch, MagicMock
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from interface.Implementation_Systeme_Detection_Camera import CameraVehicleDetectionSystem

class TestCameraVehicleDetectionSystem(unittest.TestCase):
    
    def setUp(self):
        self.system = CameraVehicleDetectionSystem()
    
    def test_configure_detection_vehicles_valide(self):
        self.system.configure_detection_vehicles("cars_only")
        self.assertEqual(self.system.detection_mode, "cars_only")
        
        self.system.configure_detection_vehicles("standard_vehicles")
        self.assertEqual(self.system.detection_mode, "standard_vehicles")
        
        self.system.configure_detection_vehicles("all_vehicles")
        self.assertEqual(self.system.detection_mode, "all_vehicles")
    
    def test_configure_detection_vehicles_invalide(self):
        with self.assertRaises(ValueError) as context:
            self.system.configure_detection_vehicles("vehicules_invalides")
        
        self.assertTrue("Invalid vehicles" in str(context.exception))
    
    def test_set_stop_programme(self):
        self.system.set_duration_threshold(2.5)
        self.assertEqual(self.system.threshold, 2.5)
        
        self.system.set_duration_threshold(1.0)
        self.assertEqual(self.system.threshold, 1.0)
    
    def test_generate_report_structure(self):
        report = self.system.generate_report()
        
        self.assertIn("session_duration", report)
        self.assertIn("vehicles_detected", report)
        self.assertIn("false_positives", report)
        self.assertIn("detection_mode", report)
        self.assertIn("alert_threshold", report)
        self.assertIn("success_rate", report)
        self.assertIn("end_timestamp", report)

if __name__ == '__main__':
    unittest.main()