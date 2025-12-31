# OpenCV Face Detector (YuNet)
# Model: face_detection_yunet_2023mar.onnx

"""
Improved Crowd Monitoring Detector
- Uses MediaPipe Tasks API (FaceDetector)
- Decouples Video Capture from Processing from Streaming
- Maintains high FPS for video feed even if detection lags
"""

import cv2
import time
import threading
import numpy as np
from flask import Flask, jsonify, Response
from flask_cors import CORS

import os

# Constants
WIDTH, HEIGHT = 640, 480
# Use absolute path to ensure model is found regardless of CWD
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'face_detection_yunet_2023mar.onnx')
# Score threshold for face detection
SCORE_THRESHOLD = 0.5
# NMS threshold for face detection
NMS_THRESHOLD = 0.3

app = Flask(__name__)
CORS(app)

# Global State
class SharedState:
    def __init__(self):
        self.frame = None
        self.processed_frame = None  # Frame with bounding boxes
        self.people_count = 0
        self.status = "green"
        self.lock = threading.Lock()
        self.running = True

state = SharedState()

def get_status(count):
    if count <= 2: return "green"
    elif count <= 5: return "orange"
    else: return "red"

def capture_thread():
    """Reads frames from camera as fast as possible"""
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    print("Camera started.")
    while state.running:
        ret, frame = cap.read()
        if ret:
            with state.lock:
                state.frame = frame
        else:
            time.sleep(0.1)
    
    cap.release()

def detection_thread():
    """Runs YuNet detection on the latest available frame"""
    
    # Initialize FaceDetectorYN
    detector = cv2.FaceDetectorYN.create(
        model=MODEL_PATH,
        config="",
        input_size=(WIDTH, HEIGHT),
        score_threshold=SCORE_THRESHOLD,
        nms_threshold=NMS_THRESHOLD,
        top_k=5000,
        backend_id=cv2.dnn.DNN_BACKEND_OPENCV,
        target_id=cv2.dnn.DNN_TARGET_CPU
    )
    
    print("Detection model loaded (YuNet).")
        
    try:
        while state.running:
            frame_to_process = None
            
            # Get latest frame
            with state.lock:
                if state.frame is not None:
                    frame_to_process = state.frame.copy()
            
            if frame_to_process is None:
                time.sleep(0.01)
                continue

            # Process
            # YuNet requires the input size to be set if frame size changes, 
            # but here we assume fixed size or resize if needed.
            # Ideally, we ensure input matches initialization or update using setInputSize.
            h, w, _ = frame_to_process.shape
            detector.setInputSize((w, h))
            
            # Inference
            # results is a tuple: (unused, faces)
            # faces is a numpy array of shape [n_faces, 15] or None
            _, faces = detector.detect(frame_to_process)
            
            count = 0
            if faces is not None:
                count = len(faces)
                
                # Draw boxes
                for face in faces:
                    # bounding box is first 4 elements: x, y, w, h
                    box = face[0:4].astype(int)
                    x, y, w, h = box[0], box[1], box[2], box[3]
                    
                    cv2.rectangle(frame_to_process, (x, y), (x + w, y + h), (0, 255, 0), 2)

            current_status = get_status(count)
            
            # Simple UI on frame
            cv2.putText(frame_to_process, f"Count: {count} ({current_status})", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Update shared state
            with state.lock:
                state.people_count = count
                state.status = current_status
                state.processed_frame = frame_to_process
            
            # Sleep slightly to prevent burning 100% CPU if detection is too fast
            time.sleep(0.03)

    except Exception as e:
        print(f"Error in detection_thread: {e}")
        import traceback
        traceback.print_exc()

@app.route('/data')
def data():
    with state.lock:
        return jsonify({
            "count": state.people_count,
            "status": state.status
        })

@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            frame_bytes = None
            with state.lock:
                if state.processed_frame is not None:
                    ret, buffer = cv2.imencode('.jpg', state.processed_frame)
                    if ret:
                        frame_bytes = buffer.tobytes()
            
            if frame_bytes:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(0.04) # Limit streaming FPS to ~25
            
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    # Start threads
    t_cap = threading.Thread(target=capture_thread, daemon=True)
    t_det = threading.Thread(target=detection_thread, daemon=True)
    
    t_cap.start()
    t_det.start()
    
    # Run server
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
