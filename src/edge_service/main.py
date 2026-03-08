import cv2
import time
import requests
import sys
import os
import json
import logging
import threading
import uvicorn
import argparse
import numpy as np
from datetime import datetime
from ultralytics import YOLO
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# --- Configuration Loading ---
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            full_config = json.load(f)
            profile_name = full_config.get("active_profile", "laptop")
            profile = full_config["profiles"][profile_name]
            print(f"Loaded configuration profile: {profile_name}")
            return profile
    except Exception as e:
        print(f"Error loading config.json: {e}. Using defaults.")
        # Default Fallback
        return {
            "source": 0,
            "backend_host": "192.168.68.107",
            "backend_port": 8000,
            "use_stdin": False,
            "send_interval": 2.0
        }

CONFIG = load_config()

# --- Configuration Constants ---
LOCATION_ID = "canteen" 
CAMERA_SOURCE = CONFIG.get("source", 0)
BACKEND_HOST = os.getenv("BACKEND_HOST", CONFIG.get("backend_host"))
BACKEND_PORT = os.getenv("BACKEND_PORT", str(CONFIG.get("backend_port", 8000)))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
USE_STDIN = CONFIG.get("use_stdin", False)
SEND_INTERVAL = CONFIG.get("send_interval", 2.0)

BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}/update-crowd-data"
CONFIDENCE_THRESHOLD = 0.4
LOW_THRESHOLD = 2
MEDIUM_THRESHOLD = 3

# --- Globals ---
app = FastAPI()
output_frame = None
latest_frame_jpg = None # For stdin reader
lock = threading.Lock() # Lock for output_frame
buffer_lock = threading.Lock() # Lock for latest_frame_jpg
running = True

# --- Logging ---
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(f"logs/edge_service.log"), logging.StreamHandler()]
)
logger = logging.getLogger(f"edge_service")

# --- Helper Functions ---
def get_density_level(count):
    if count <= LOW_THRESHOLD: return "Low"
    elif count <= MEDIUM_THRESHOLD: return "Medium"
    else: return "High"

# --- Stdin Reader Thread (For RPi Pipe Mode) ---
def stdin_reader():
    global latest_frame_jpg, running
    
    # Only run if stdin is expected
    if not USE_STDIN:
        return
        
    stream = sys.stdin.buffer
    bytes_data = b''
    logger.info("Stdin reader thread started (Pipe Mode).")
    
    while running:
        try:
            chunk = stream.read(65536)
            if not chunk:
                # If EOF, we might be done or stream closed
                time.sleep(0.01)
                continue
            
            bytes_data += chunk
            
            # Safety cap to prevent memory overflow
            if len(bytes_data) > 10 * 1024 * 1024: 
                logger.warning("Buffer full! Dropping frames.")
                last_start = bytes_data.rfind(b'\xff\xd8')
                if last_start != -1:
                    bytes_data = bytes_data[last_start:]
                else: 
                    bytes_data = b''
            
            while True:
                a = bytes_data.find(b'\xff\xd8')
                b = bytes_data.find(b'\xff\xd9')
                
                if a != -1 and b != -1:
                    if b < a:
                        bytes_data = bytes_data[a:]
                        continue
                    
                    jpg = bytes_data[a:b+2]
                    bytes_data = bytes_data[b+2:] 
                    
                    with buffer_lock:
                        latest_frame_jpg = jpg
                else:
                    break 
                    
        except Exception as e:
            logger.error(f"Reader Error: {e}")
            time.sleep(0.1)

# --- AI Logic (Unified) ---
def run_ai_processing(location):
    global output_frame, running, latest_frame_jpg, CAMERA_SOURCE, USE_STDIN
    
    logger.info(f"Starting AI Processing for '{location}'")
    logger.info(f"Backend URL: {BACKEND_URL}")
    logger.info("Loading YOLOv8 model...")
    try:
        model = YOLO('yolov8n.pt')
        logger.info("Model loaded.")
    except Exception as e:
        logger.critical(f"Failed to load model: {e}")
        return

    cap = None
    if not USE_STDIN:
        # --- OpenCV Mode ---
        source = CAMERA_SOURCE
        if isinstance(source, str) and source.isdigit():
            source = int(source)
            
        logger.info(f"Using OpenCV VideoCapture source: {source}")
        if isinstance(source, int):
            cap = cv2.VideoCapture(source, cv2.CAP_V4L2) # Try V4L2 first
            if not cap.isOpened():
                cap = cv2.VideoCapture(source) # Fallback
            
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        else:
            cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            logger.critical("Error: Could not open video source.")
            return
    else:
        logger.info("Using Stdin Pipe Mode for video source.")

    last_send_time = 0

    while running:
        frame = None
        
        if USE_STDIN:
            # Get latest frame from buffer thread
            jpg_bytes = None
            with buffer_lock:
                if latest_frame_jpg:
                    jpg_bytes = latest_frame_jpg
            
            if jpg_bytes:
                # Decode JPEG to OpenCV image
                try:
                    frame = cv2.imdecode(np.frombuffer(jpg_bytes, np.uint8), cv2.IMREAD_COLOR)
                except Exception as e:
                    logger.error(f"Decode error: {e}")
            else:
                time.sleep(0.01)
                continue
        else:
            # OpenCV Read
            ret, frame = cap.read()
            if not ret:
                logger.error("Failed to read frame. Retrying...")
                time.sleep(1)
                continue

        if frame is None:
            continue

        # Resize for consistent processing speed if needed
        # frame = cv2.resize(frame, (640, 480))

        # Inference
        results = model.predict(frame, classes=[0], conf=CONFIDENCE_THRESHOLD, verbose=False)
        person_count = len(results[0].boxes)
        
        # Annotation
        annotated_frame = results[0].plot()

        # Update global frame for Web Stream
        with lock:
            output_frame = annotated_frame.copy()

        # Send Data to Backend
        current_time = time.time()
        if current_time - last_send_time > SEND_INTERVAL:
            density_level = get_density_level(person_count)
            payload = {
                "location_id": location,
                "timestamp": datetime.now().isoformat(),
                "count": person_count,
                "density_level": density_level,
                "trend": "Stable"
            }
            try:
                requests.post(BACKEND_URL, json=payload, timeout=1)
                logger.info(f"Updated Backend: Count={person_count}")
            except Exception as e:
                logger.warning(f"Backend Sync Failed: {e}")
            
            last_send_time = current_time

        if not USE_STDIN:
            time.sleep(0.01) 

    if cap:
        cap.release()
    logger.info("AI Thread Stopped.")

# --- Web Stream Logic ---
def generate():
    global output_frame
    while True:
        with lock:
            if output_frame is None:
                encodedImage = None
            else:
                (flag, encodedImage) = cv2.imencode(".jpg", output_frame)
                if not flag:
                    encodedImage = None
        
        if encodedImage is not None:
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
        
        time.sleep(0.1) 

@app.get("/")
def index():
    return {"status": "Edge Service Running", "config": CONFIG}

@app.get("/video")
def video_feed():
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace;boundary=frame")

# --- Main Entry ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("location", nargs="?", default="canteen", help="Location ID")
    args = parser.parse_args()

    # Start Stdin Reader Thread if needed
    if USE_STDIN:
        t_reader = threading.Thread(target=stdin_reader)
        t_reader.daemon = True
        t_reader.start()

    # Start AI Thread
    t_ai = threading.Thread(target=run_ai_processing, args=(args.location,))
    t_ai.daemon = True
    t_ai.start()

    # Start Web Server
    logger.info(f"Starting Web Stream on port 5000 (Mode: {'STDIN' if USE_STDIN else 'OPENCV'})...")
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="error")
