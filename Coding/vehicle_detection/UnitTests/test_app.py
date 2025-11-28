import unittest
import sys
import os
from unittest.mock import patch, MagicMock
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import CarDetectionApp

class TestCarDetectionApp(unittest.TestCase):
    
    def setUp(self):
        self.app = CarDetectionApp()
    
    def test_stop_method(self):
        # Mock du système
        self.app.system._stop_system = MagicMock()
        
        self.app.running = True
        self.app.stop()
        
        self.assertFalse(self.app.running)
        self.app.system._stop_system.assert_called_once()

if __name__ == '__main__':
    unittest.main()