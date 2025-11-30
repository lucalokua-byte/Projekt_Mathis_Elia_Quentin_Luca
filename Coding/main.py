import cv2
import mediapipe as mp
import time
import argparse
import os
import json
from Db_maneger.AbstractDBManager import AbstractDBManager
from Db_maneger.Db_maneger import DBManager
from vehicle_detection.car_detection import CarDetectionApp
from NumberPlateReading.NumberPlateRecognition import NumberPlateRecognition 
from NumberPlateReading.NumberPlateRecognitionInterface import NumberPlateRecognizer 
from mail_system.email_system import EmailSender 


def main():
    """Unified main function for the intelligent detection system"""
    print("=== INTELLIGENT DETECTION SYSTEM ===")
    
    # Endlosschleife für kontinuierlichen Betrieb
    while True:
        try:
            # Start vehicle detection
            print("\n" + "="*50)
            print("STARTING VEHICLE DETECTION SYSTEM")
            print("="*50)
            app = CarDetectionApp()
            
            # Modified run method to check for 'q' key
            should_exit = app.run()
            if should_exit:
                print("\nVehicle detection stopped by user")
                break

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
            print("\n" + "="*50)
            print("STARTING NUMBER PLATE RECOGNITION")
            print("="*50)
            
            # Modified to check for exit flag
            recognizer.begin_plate_detection()
            
            # Check if user pressed 'q' during plate recognition
            if recognizer.should_exit and not recognizer.final_confirmed_plate:
                print("\nNumber plate recognition stopped by user")
                break
            
            # After completion, retrieve the status
            final_plate = recognizer.get_confirmed_plate()
            if final_plate:
                plate_text = final_plate['text']
                print(f"\n✅ Final confirmed plate: {plate_text}")
                
                # Email security system integration
                print("\n" + "="*50)
                print("STARTING EMAIL SECURITY SYSTEM")
                print("="*50)
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
            
            print("\n" + "="*50)
            print("MAIN PROGRAM COMPLETED SUCCESSFULLY!")
            print("RESTARTING SYSTEM IN 3 SECONDS...")
            print("Press 'q' during vehicle detection to stop completely")
            print("="*50)
            
            # Kurze Pause bevor Neustart mit Möglichkeit zum Beenden
            for i in range(3, 0, -1):
                print(f"Restarting in {i} seconds...", end='\r')
                time.sleep(1)
            
            # Clear the line
            print(" " * 50, end='\r')
            
        except KeyboardInterrupt:
            print("\n\nProgram manually stopped by user")
            break
        except Exception as e:
            print(f"\n\nAn error occurred: {e}")
            print("🔄 Restarting system in 5 seconds...")
            for i in range(5, 0, -1):
                print(f"Restarting in {i} seconds...", end='\r')
                time.sleep(1)
            print(" " * 50, end='\r')


if __name__ == "__main__":
    main()