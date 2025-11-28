import unittest
import sys
import os
from unittest.mock import patch, MagicMock
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from camera.camera_manager import Camera

class TestCamera(unittest.TestCase):
    
    @patch('camera.camera_manager.cv2.VideoCapture')
    def test_initialisation_camera(self, mock_video_capture):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap
        
        camera = Camera()
        
        self.assertEqual(camera.camera_index, 0)
        self.assertEqual(camera.frame_count, 0)
        mock_video_capture.assert_called_with(0)
    
    @patch('camera.camera_manager.cv2.VideoCapture')
    def test_read_frame_success(self, mock_video_capture):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, "frame_data")
        mock_video_capture.return_value = mock_cap
        
        camera = Camera()
        frame = camera.read_frame()
        
        self.assertEqual(frame, "frame_data")
        self.assertEqual(camera.frame_count, 1)
    
    @patch('camera.camera_manager.cv2.VideoCapture')
    def test_read_frame_echec(self, mock_video_capture):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (False, None)
        mock_video_capture.return_value = mock_cap
        
        camera = Camera()
        
        with self.assertRaises(Exception) as context:
            camera.read_frame()
        
        self.assertTrue("Cannot read video stream" in str(context.exception))

if __name__ == '__main__':
    unittest.main()