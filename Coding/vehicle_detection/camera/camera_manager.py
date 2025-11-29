import cv2


class Camera:
    """
    CAMERA MANAGER
    Handles camera initialization, frame capture, and resource management
    """
    
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.frame_count = 0
        self._initialize_camera()
    
    def _initialize_camera(self):
        """Initialize camera connection and verify it's working"""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise Exception(" Error: Cannot open camera")
        print(" Camera initialized")
    
    def read_frame(self):
        """Capture a single frame from the camera"""
        ret, frame = self.cap.read()
        if not ret:
            raise Exception(" Error: Cannot read video stream")
        self.frame_count += 1
        return frame
    
    def get_timestamp(self):
        """Get current video timestamp in milliseconds"""
        return int(self.cap.get(cv2.CAP_PROP_POS_MSEC))
    
    def release(self):
        """Release camera resources and cleanup"""
        if self.cap:
            self.cap.release()
            print(" Camera released")