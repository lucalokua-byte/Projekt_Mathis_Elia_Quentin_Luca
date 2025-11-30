import cv2

class DetectionProcessor:
    """
    DETECTION PROCESSOR - Processes detection results and draws visual annotations
    """
    
    def __init__(self, detection_mode="standard_vehicles"):
        # Define detection modes
        modes = {
            "cars_only": ['car'],
            "standard_vehicles": ['car', 'truck', 'bus'],
            "all_vehicles": ['car', 'truck', 'bus', 'motorcycle']
        }
        self.vehicle_keywords = modes.get(detection_mode, modes["standard_vehicles"])
    
    def process_detections(self, detection_result, frame):
        """
        Processes detection results and draws bounding boxes
        Returns processed frame and vehicle detection status
        """
        vehicle_detected = False
        processed_frame = frame.copy()
        
        for detection in detection_result.detections:
            category = detection.categories[0]
            category_name = category.category_name
            confidence = category.score
            confidence_percent = confidence * 100
            
            # Check if it's a vehicle with at least 30% confidence
            is_vehicle = any(vehicle in category_name.lower() for vehicle in self.vehicle_keywords)
            
            if is_vehicle and confidence >= 0.3:
                if not vehicle_detected:
                    print(f" VEHICLE ALERT DETECTED! {confidence_percent:.1f}%")
                    vehicle_detected = True
            
            # Draw bounding box
            bbox = detection.bounding_box
            start_point = (bbox.origin_x, bbox.origin_y)
            end_point = (bbox.origin_x + bbox.width, bbox.origin_y + bbox.height)
            
            # Red for vehicles, green for other objects
            color = (0, 0, 255) if is_vehicle else (0, 255, 0)
            
            # Draw rectangle and label
            cv2.rectangle(processed_frame, start_point, end_point, color, 2)
            cv2.putText(processed_frame, f"{category_name} {confidence_percent:.1f}%", 
                       (bbox.origin_x, bbox.origin_y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        return processed_frame, vehicle_detected