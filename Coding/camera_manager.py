import cv2
import threading
import time
from queue import Queue

class CameraManager:
    def __init__(self, camera_id=0, frame_width=640, frame_height=480):
        self.camera_id = camera_id
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.camera = None
        self.is_running = False
        self.frame_queue = Queue(maxsize=1)
        self.thread = None
        
    def initialize_camera(self):
        """Initialize the camera with specified settings"""
        try:
            self.camera = cv2.VideoCapture(self.camera_id)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            if not self.camera.isOpened():
                raise Exception(f"Could not open camera with ID {self.camera_id}")
                
            print(f"Camera {self.camera_id} initialized successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def start_capture(self):
        """Start continuous frame capture in a separate thread"""
        if not self.initialize_camera():
            return False
            
        self.is_running = True
        self.thread = threading.Thread(target=self._capture_frames)
        self.thread.daemon = True
        self.thread.start()
        return True
    
    def _capture_frames(self):
        """Internal method to capture frames continuously"""
        while self.is_running:
            ret, frame = self.camera.read()
            if ret:
                # Only keep the latest frame
                if not self.frame_queue.empty():
                    try:
                        self.frame_queue.get_nowait()
                    except:
                        pass
                self.frame_queue.put(frame)
            time.sleep(0.033)  # ~30 FPS
    
    def get_frame(self):
        """Get the latest frame from the queue"""
        try:
            return self.frame_queue.get_nowait()
        except:
            return None
    
    def stop_capture(self):
        """Stop the camera capture and release resources"""
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        
        if self.camera and self.camera.isOpened():
            self.camera.release()
        cv2.destroyAllWindows()
    
    def __del__(self):
        self.stop_capture()