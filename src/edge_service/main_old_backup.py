import cv2
import time
import requests
import sys
import os
import logging
import threading
import uvicorn
import argparse
from datetime import datetime
from ultralytics import YOLO
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# --- Configuration ---
LOCATION_ID = "canteen" 
CAMERA_SOURCE = 0
BACKEND_HOST = os.getenv("BACKEND_HOST", "192.168.68.107") # Default to laptop IP
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}/update-crowd-data"
CONFIDENCE_THRESHOLD = 0.4
SEND_INTERVAL = 2.0
LOW_THRESHOLD = 2
MEDIUM_THRESHOLD = 3

# --- Globals for Threading ---
app = FastAPI()
output_frame = None
lock = threading.Lock()
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

# --- AI Logic (Runs in Background Thread) ---
def run_ai_processing(location, source):
    global output_frame, running
    
    logger.info(f"Starting AI Processing for '{location}' using source: {source}")
    logger.info("Loading YOLOv8 model...")
    try:
        model = YOLO('yolov8n.pt')
        logger.info("Model loaded.")
    except Exception as e:
        logger.critical(f"Failed to load model: {e}")
        return

    # Initialize Video Capture with RPi options
    if isinstance(source, str) and source.isdigit():
        source = int(source)
    
    if isinstance(source, int):
        logger.info(f"Opening Camera index {source} with CAP_V4L2...")
        cap = cv2.VideoCapture(source, cv2.CAP_V4L2)
        # Force common resolution and MJPEG for RPi compatibility
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    else:
        logger.info(f"Opening Video Source: {source}")
        cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        logger.critical("Error: Could not open video source.")
        return

    last_send_time = 0

    while running:
        ret, frame = cap.read()
        if not ret:
            logger.error("Failed to read frame. Retrying in 1s...")
            time.sleep(1)
            # Optional: Attempt reconnect logic here
            continue

        # Inference
        results = model.predict(frame, classes=[0], conf=CONFIDENCE_THRESHOLD, verbose=False)
        person_count = len(results[0].boxes)
        
        # Annotation for Video Stream
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
                # Use a short timeout so we don't block the AI loop
                requests.post(BACKEND_URL, json=payload, timeout=1)
                logger.info(f"Updated Backend: Count={person_count}")
            except Exception as e:
                logger.warning(f"Backend Sync Failed: {e}")
            
            last_send_time = current_time

        time.sleep(0.01) # Yield slightly

    cap.release()
    logger.info("AI Thread Stopped.")

# --- Web Stream Logic ---
def generate():
    global output_frame
    while True:
        with lock:
            if output_frame is None:
                continue
            (flag, encodedImage) = cv2.imencode(".jpg", output_frame)
            if not flag:
                continue
        
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
        time.sleep(0.1) # Max 10 FPS for stream to save bandwidth

@app.get("/")
def index():
    return {"status": "Edge Service Running", "message": "Go to /video for MJPEG stream"}

@app.get("/video")
def video_feed():
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace;boundary=frame")

# --- Main Entry ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("location", nargs="?", default="canteen", help="Location ID")
    parser.add_argument("source", nargs="?", default="0", help="Camera Source (0, RTSP URL, etc)")
    args = parser.parse_args()

    # Handle numeric source
    src = args.source
    if src.isdigit(): src = int(src)

    # Start AI Thread
    t = threading.Thread(target=run_ai_processing, args=(args.location, src))
    t.daemon = True
    t.start()

    # Start Web Server (Blocking)
    logger.info("Starting Web Stream on port 5000...")
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="error")
