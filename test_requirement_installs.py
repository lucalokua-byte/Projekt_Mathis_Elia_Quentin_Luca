# test_requirements.py - Behalten falls du testen willst
import sys
print(f"Python Version: {sys.version}")

try:
    import cv2
    print("✅ OpenCV funktioniert")
except ImportError as e:
    print(f"❌ OpenCV Fehler: {e}")

try:
    import numpy as np
    print("✅ NumPy funktioniert")
except ImportError as e:
    print(f"❌ NumPy Fehler: {e}")

try:
    import pytesseract
    print("✅ pytesseract funktioniert")
except ImportError as e:
    print(f"❌ pytesseract Fehler: {e}")