import cv2
import threading
import time
from queue import Queue

class CameraManager:
    def __init__(self, camera_id=0, frame_width=1280, frame_height=720):  # Higher resolution
        self.camera_id = camera_id
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.camera = None
        self.is_running = False
        self.frame_queue = Queue(maxsize=2)  # Small queue for latest frames only
        self.thread = None
        
    def initialize_camera(self):
        """Initialize camera for 60FPS"""
        try:
            self.camera = cv2.VideoCapture(self.camera_id)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.camera.set(cv2.CAP_PROP_FPS, 60)  # Request 60FPS
            self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 2)  # Small buffer for low latency
            
            if not self.camera.isOpened():
                raise Exception(f"Could not open camera with ID {self.camera_id}")
                
            actual_fps = self.camera.get(cv2.CAP_PROP_FPS)
            print(f"📷 Camera {self.camera_id} initialized - FPS: {actual_fps}")
            return True
            
        except Exception as e:
            print(f"❌ Camera error: {e}")
            return False
    
    def start_capture(self):
        """Start continuous frame capture"""
        if not self.initialize_camera():
            return False
            
        self.is_running = True
        self.thread = threading.Thread(target=self._capture_frames)
        self.thread.daemon = True
        self.thread.start()
        return True
    
    def _capture_frames(self):
        """Capture frames as fast as possible"""
        while self.is_running:
            ret, frame = self.camera.read()
            if ret:
                # Only keep the latest frame
                if self.frame_queue.full():
                    try:
                        self.frame_queue.get_nowait()
                    except:
                        pass
                self.frame_queue.put(frame)
            # No sleep - capture as fast as possible
    
    def get_frame(self):
        """Get the latest frame"""
        try:
            return self.frame_queue.get_nowait()
        except:
            return None
    
    def stop_capture(self):
        """Stop camera"""
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        
        if self.camera and self.camera.isOpened():
            self.camera.release()
    
    def __del__(self):
        self.stop_capture()