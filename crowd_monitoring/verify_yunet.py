import cv2
import os

MODEL_PATH = 'crowd_monitoring/face_detection_yunet_2023mar.onnx'

try:
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

    detector = cv2.FaceDetectorYN.create(
        model=MODEL_PATH,
        config="",
        input_size=(320, 320),
        score_threshold=0.5,
        nms_threshold=0.3,
        top_k=5000,
        backend_id=cv2.dnn.DNN_BACKEND_OPENCV,
        target_id=cv2.dnn.DNN_TARGET_CPU
    )
    print("SUCCESS: YuNet model loaded successfully.")
except Exception as e:
    print(f"FAILURE: {e}")
