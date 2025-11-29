from abc import ABC, abstractmethod
from typing import Dict, Any

class VehicleDetectionSystemInterface(ABC):
    """
    VEHICLE DETECTION SYSTEM INTERFACE
    Defines the contract that all vehicle detection systems must implement
    """
    
    @abstractmethod
    def configure_detection_vehicles(self, vehicles: str):
        """Configure the type of vehicles to detect
                "cars_only": ["car", "vehicle"],
                "standard_vehicles": ["car", "truck", "bus", "vehicle"],
                "all_vehicles": ["car", "truck", "bus", "motorcycle", "vehicle"]"""
        pass
    
    @abstractmethod
    def set_duration_threshold(self, duration_seconds: float):
        """Create a time check: if a car is detected for X seconds, then move to the next program."""
        pass
    
    @abstractmethod
    def detect_and_analyze(self, input_data: Any) -> Dict[str, Any]:
        """Detect and analyze vehicles in the input data"""
        pass
    
    @abstractmethod
    def execute_alert_actions(self):
        """Execute defined actions after prolonged detection"""
        pass