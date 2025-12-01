import unittest
from unittest.mock import patch
import sys
import os
import numpy as np


# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import your modules
from vehicle_detection.camera.camera_manager import Camera

class TestCamera(unittest.TestCase):

    def test_camera_initialization(self):
        #Test camera initialization with mock
        with patch('cv2.VideoCapture') as mock_video:    #MOCKS OpenCV VideoCapture
            mock_video.return_value.isOpened.return_value = True   #Mock camera opened successfully
            camera = Camera(camera_index=0)     # Create a camera
            self.assertIsNotNone(camera.cap)   #Verify camera is initialized
    
    def test_camera_read_frame(self):
        #Test frame reading functionality
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

if __name__ == "__main__":
    unittest.main()