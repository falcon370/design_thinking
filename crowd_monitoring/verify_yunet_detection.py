import cv2
import numpy as np
import os

MODEL_PATH = 'crowd_monitoring/face_detection_yunet_2023mar.onnx'

try:
    print("Loading model...")
    detector = cv2.FaceDetectorYN.create(
        model=MODEL_PATH,
        config="",
        input_size=(640, 480),
        score_threshold=0.5,
        nms_threshold=0.3,
        top_k=5000,
        backend_id=cv2.dnn.DNN_BACKEND_OPENCV,
        target_id=cv2.dnn.DNN_TARGET_CPU
    )
    print("Model loaded.")

    # Create dummy image
    print("Creating dummy frame...")
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Simulate setInputSize
    h, w, _ = frame.shape
    print(f"Setting input size to: {w}x{h}")
    detector.setInputSize((w, h))
    
    # Run detection
    print("Running detection...")
    _, faces = detector.detect(frame)
    print(f"Detection complete. Faces found: {faces}")

except Exception as e:
    print(f"CRASHED: {e}")
    import traceback
    traceback.print_exc()
