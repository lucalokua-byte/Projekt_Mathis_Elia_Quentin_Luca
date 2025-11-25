from abc import ABC, abstractmethod

class IntelligentDetectionSystem(ABC):
    """Interface for the complete detection system"""
    
    @abstractmethod
    def start_vehicle_detection(self) -> bool:
        pass
    
    @abstractmethod
    def start_plate_recognition(self) -> bool:
        pass
    
    @abstractmethod
    def run_complete_system(self) -> bool:
        pass
    
    @abstractmethod
    def stop_system(self):
        pass