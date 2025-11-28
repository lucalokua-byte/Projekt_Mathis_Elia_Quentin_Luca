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
    '''
    """Programme principal qui intègre les deux systèmes"""
    print("=== SYSTÈME COMPLET DE RECONNAISSANCE ===")
    
    # Étape 1: Détecter une plaque avec le premier programme
    print("\n1. 🔍 DÉTECTION DE PLAQUE...")
    detected_plate = detect_plate_and_return()
    
    if not detected_plate:
        print("❌ Aucune plaque détectée. Arrêt du système.")
        return
    
    print(f"\n✅ PLAQUE DÉTECTÉE: {detected_plate}")
    
    # Étape 2: Utiliser la plaque détectée dans Numberplate_validation.py
    print("\n2. 🚨 TRAITEMENT DE LA PLAQUE INCONNUE...")
    handler = UnknownPlateHandler()
    access_granted = handler.handle_unknown_plate(detected_plate)  # <-- ICI on utilise la plaque détectée
    
    # Étape 3: Résultat final
    print(f"\n3. 🎯 RÉSULTAT FINAL: Accès {'AUTORISÉ' if access_granted else 'REFUSÉ'}")
    
    if access_granted:
        print("🚪 La porte s'ouvre...")
        # Ajouter ici la logique pour ouvrir la porte
    else:
        print("🚪 La porte reste fermée...")
        # Ajouter ici la logique pour garder la porte fermée
    '''
if __name__ == "__main__":
    main()