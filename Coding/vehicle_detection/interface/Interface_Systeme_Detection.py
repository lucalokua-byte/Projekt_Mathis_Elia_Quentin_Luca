from abc import ABC, abstractmethod
from typing import Dict, Any

class VehicleDetectionSystemInterface(ABC):
    """
    VEHICLE DETECTION SYSTEM INTERFACE
    Defines the contract that all vehicle detection systems must implement
    """
    
    @abstractmethod
    def configure_detection_mode(self, mode: str):
        """Configure the type of vehicles to detect"""
        pass
    
    @abstractmethod
    def set_alert_threshold(self, duration_seconds: float):
        """Set the detection duration before triggering alerts"""
        pass
    
    @abstractmethod
    def detect_and_analyze(self, input_data: Any) -> Dict[str, Any]:
        """Detect and analyze vehicles in the input data"""
        pass
    
    @abstractmethod
    def execute_alert_actions(self):
        """Execute defined actions after prolonged detection"""
        pass
    
    """
    @abstractmethod
    def generate_report(self) -> Dict[str, Any]:
        #Generate a complete detection session report
        pass
    
        
    @abstractmethod
    def get_performance_stats(self) -> Dict[str, Any]:
        #Return real-time performance statistics
        pass
    """