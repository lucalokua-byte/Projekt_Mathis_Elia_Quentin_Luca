from abc import ABC, abstractmethod
from typing import Dict, Any

class VehicleDetectionSystemInterface(ABC):
    """
    VEHICLE DETECTION SYSTEM INTERFACE
    Defines the contract that all vehicle detection systems must implement
    """
    
    @abstractmethod
    def configure_detection_vehicles(self, vehicles: str):
        """Configure the type of vehicles to detect"""
        pass
    
    @abstractmethod
    def set_stop_programme(self, duration_seconds: float):
        """When a vehicle is detected, how long does it take for the programme to stop automatically?"""
        pass
    
    @abstractmethod
    def detect_and_analyze(self, input_data: Any) -> Dict[str, Any]:
        """Detect and analyze vehicles in the input data"""
        pass
    
    @abstractmethod
    def execute_alert_actions(self):
        """Execute defined actions after prolonged detection"""
        pass