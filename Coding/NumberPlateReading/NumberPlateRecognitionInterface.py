from abc import ABC, abstractmethod
import cv2
import pytesseract
import os
import re
import time

class NumberPlateRecognizer(ABC):
    """Abstrakte Interface-Klasse für Nummernschild-Erkennung"""
    
    @abstractmethod
    def initialize_camera(self) -> bool:
        """Kamera initialisieren"""
        pass
    
    @abstractmethod
    def process_frame(self, frame):
        """Einzelnen Frame verarbeiten"""
        pass
    
    @abstractmethod
    def extract_text_from_plate(self, plate_img):
        """Text aus Nummernschild extrahieren"""
        pass
    
    @abstractmethod
    def run(self):
        """Hauptausführungsmethode"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Ressourcen freigeben"""
        pass
    
    @abstractmethod
    def get_detection_status(self) -> dict:
        """Aktuellen Erkennungsstatus abrufen"""
        pass
    
    @abstractmethod
    def set_confidence_threshold(self, threshold: float):
        """Confidence Threshold setzen"""
        pass
    
    @abstractmethod
    def get_confirmed_plate(self) -> dict:
        """Bestätigtes Nummernschild abrufen"""
        pass