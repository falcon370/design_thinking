import cv2
try:
    import mediapipe.tasks
    print("mediapipe.tasks imported")
except ImportError:
    print("mediapipe.tasks failed")

print(f"OpenCV Version: {cv2.__version__}")
