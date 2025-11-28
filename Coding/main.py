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
from number_plate_detection.NumberPlateDetection_Interface import NumberPlateDetection
from number_plate_detection.NumberPlateRecognition import PlateRecognizer
from number_plate_detection.number_plate_system import CompleteDetectionSystem


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
 
    system = CompleteDetectionSystem(
        camera_id=args.camera,
        display=not args.no_display,
        log_results=not args.no_log
    )
    system.start_plate_recognition()

if __name__ == "__main__":
    main()