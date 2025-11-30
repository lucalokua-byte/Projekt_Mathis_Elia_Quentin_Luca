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
from vehicle_detection.car_detection import CarDetectionApp
from NumberPlateReading.NumberPlateRecognition import NumberPlateRecognition 
from NumberPlateReading.NumberPlateRecognitionInterface import NumberPlateRecognizer 
from mail_system.email_system import EmailSender 


def main():
    """Unified main function for the intelligent detection system"""
    print("=== INTELLIGENT DETECTION SYSTEM ===")

    # Start vehicle detection
    print("  VEHICLE DETECTION SYSTEM")
    car_detection = CarDetectionApp()
    car_detection.run()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Intelligent Detection System')
    parser.add_argument('--camera', type=int, default=0, help='Camera ID (default: 0)')
    parser.add_argument('--no-display', action='store_true', help='Disable display window')
    parser.add_argument('--no-log', action='store_true', help='Disable logging')
    
    args = parser.parse_args()
    
    # Create recognizer using the interface
    recognizer: NumberPlateRecognizer = NumberPlateRecognition(
        confidence_threshold=0.9, 
        min_plate_length=4,
        max_plate_length=8,
    )
    
    # Use the interface methods
    print("Starting number plate recognition...")
    recognizer.begin_plate_detection()
    
    # After completion, retrieve the status
    final_plate = recognizer.get_confirmed_plate()
    if final_plate:
        plate_text = final_plate['text']
        print(f"\nFinal confirmed plate: {plate_text}")
        
        # Email security system integration
        print("\n=== STARTING EMAIL SECURITY SYSTEM ===")
        email_sender = EmailSender(db_manager=DBManager("data", "license_plates.json"))
        decision = email_sender.run_email_system(plate_text)
        print(f"Final decision: {decision}")
        
        # Process the decision
        if decision == 'accept_whitelist':
            print("Vehicle accepted and added to whitelist")
        elif decision == 'accept_only':
            print("Vehicle accepted temporarily")
        elif decision == 'reject_blacklist':
            print("Vehicle rejected and added to blacklist")
        elif decision == 'reject_only':
            print("Vehicle rejected temporarily")
        elif decision == 'timeout':
            print("No decision received within timeout period")
        
    
    # Clean up resources
    recognizer.close_camera_window()
    print("Main program completed successfully!")


if __name__ == "__main__":
    main()