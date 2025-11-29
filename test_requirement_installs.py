try:
    import cv2
    print(f"✅ OpenCV version: {cv2.__version__}")
except ImportError as e:
    print(f"❌ OpenCV error: {e}")

try:
    import pytesseract
    print("✅ pytesseract imported successfully")
except ImportError as e:
    print(f"❌ pytesseract error: {e}")

try:
    import numpy as np
    print(f"✅ NumPy version: {np.__version__}")
except ImportError as e:
    print(f"❌ NumPy error: {e}")

try:
    import imutils
    print("✅ imutils imported successfully")
except ImportError as e:
    print(f"❌ imutils error: {e}")

try:
    from PIL import Image
    print(f"✅ Pillow version: {Image.__version__}")
except ImportError as e:
    print(f"❌ Pillow error: {e}")

try:
    import requests
    print(f"✅ requests version: {requests.__version__}")
except ImportError as e:
    print(f"❌ requests error: {e}")

try:
    import mediapipe as mp
    print(f"✅ mediapipe imported successfully")
except ImportError as e:
    print(f"❌ mediapipe error: {e}")

print("\n🎉 All imports completed!")