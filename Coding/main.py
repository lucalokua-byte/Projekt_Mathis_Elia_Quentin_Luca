import cv2
import mediapipe as mp
import time
import argparse
import os
import json
from camera_manager import CameraManager 
from utils import PlateLogger, draw_detection_results
from Db_maneger.AbstractDBManager import AbstractDBManager
from Db_maneger.Db_maneger import DBManager
from vehicle_detection.app import CarDetectionApp
from NumberPlateReading.testing_number_plate_reading import NumberPlateRecognition 
from NumberPlateReading.NumberPlateRecognitionInterface import NumberPlateRecognizer 


def main():
    """Unified main function"""
    print("=== INTELLIGENT DETECTION SYSTEM ===")

    # Start vehicle detection
    print("  VEHICLE DETECTION SYSTEM")
    app = CarDetectionApp()
    app.run()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Intelligent Detection System')
    parser.add_argument('--camera', type=int, default=0, help='Camera ID (default: 0)')
    parser.add_argument('--no-display', action='store_true', help='Disable display window')
    parser.add_argument('--no-log', action='store_true', help='Disable logging')
    
    args = parser.parse_args()
    
    # Erstelle Recognizer über das Interface
    recognizer: NumberPlateRecognizer = NumberPlateRecognition(confidence_threshold=0.9, min_plate_length=4,max_plate_length=8,)
    
    # Verwende die Interface-Methoden
    print("Starting number plate recognition...")
    recognizer.run()
    
    # Nach Beendigung könntest du den Status abrufen
    final_plate = recognizer.get_confirmed_plate()
    if final_plate:
        print(f"\n Final confirmed plate: {final_plate['text']}")
    
    recognizer.cleanup()
 

if __name__ == "__main__":
    main()