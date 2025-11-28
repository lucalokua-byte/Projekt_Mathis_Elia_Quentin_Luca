import cv2

class DetectionProcessor:
    """
    DETECTION PROCESSOR
    Processes object detection results and draws visual annotations
    """
    
    def __init__(self):
        self.vehicle_keywords = ['car', 'truck', 'bus', 'vehicle']
    
    def is_vehicle(self, category_name):
        """Check if the detected object is a vehicle"""
        return any(vehicle in category_name.lower() for vehicle in self.vehicle_keywords)
    
    def process_detections(self, detection_result, frame):
        """
        Process detection results and draw bounding boxes
        Returns processed frame and vehicle detection status
        """
        vehicle_detected = False
        processed_frame = frame.copy()
        
        for detection in detection_result.detections:
            category = detection.categories[0]
            category_name = category.category_name
            confidence = category.score
            confidence_percent = confidence * 100
            
            # Check for vehicles with at least 30% confidence
            if self.is_vehicle(category_name) and confidence >= 0.3:
                if not vehicle_detected:
                    print(f" VEHICLE ALERT DETECTED! {confidence_percent:.1f}%")
                    vehicle_detected = True
            
            # Draw bounding box and label
            self._draw_bounding_box(processed_frame, detection, category_name, confidence_percent)
        
        return processed_frame, vehicle_detected
    
    def _draw_bounding_box(self, frame, detection, category_name, confidence_percent):
        """Draw bounding box and label on the frame"""
        bbox = detection.bounding_box
        start_point = (bbox.origin_x, bbox.origin_y)
        end_point = (bbox.origin_x + bbox.width, bbox.origin_y + bbox.height)
        
        # Red for vehicles, green for other objects
        color = (0, 0, 255) if self.is_vehicle(category_name) else (0, 255, 0)
        
        # Draw bounding box rectangle
        cv2.rectangle(frame, start_point, end_point, color, 2)
        
        # Draw label above bounding box
        cv2.putText(frame, f"{category_name} {confidence_percent:.1f}%", 
                   (bbox.origin_x, bbox.origin_y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)