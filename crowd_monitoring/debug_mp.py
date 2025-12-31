import mediapipe as mp
try:
    from mediapipe.python.solutions import face_detection
    print("Export import 'from mediapipe.python.solutions import face_detection' worked")
    print(f"FaceDetection available: {face_detection.FaceDetection}")
except Exception as e:
    print(f"Explicit import failed: {e}")

try:
    import mediapipe.solutions
    print("import mediapipe.solutions worked")
except ImportError as e:
    print(f"import mediapipe.solutions failed: {e}")
