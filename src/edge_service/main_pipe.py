# main_pipe.py (Optimized with Threaded Reader)
import cv2
import sys
import numpy as np
import time
import requests
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
BACKEND_HOST = os.getenv("BACKEND_HOST", "192.168.68.107") # Default Laptop IP
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}/update-crowd-data"
CONFIDENCE_THRESHOLD = 0.4
SEND_INTERVAL = 1.0  # Send updates every 1 second
LOW_THRESHOLD = 2
MEDIUM_THRESHOLD = 3

# --- Globals ---
app = FastAPI()
output_frame = None
latest_frame_jpg = None # Raw JPEG bytes for reader thread
frame_lock = threading.Lock() # Lock for annotated frame (Web)
buffer_lock = threading.Lock() # Lock for raw input buffer
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

# --- Stdin Reader Thread ---
# Decouples reading from processing so we don't fall behind and create lag
def stdin_reader():
    global latest_frame_jpg, running
    stream = sys.stdin.buffer
    bytes_data = b''
    
    logger.info("Stdin reader thread started.")
    
    while running:
        try:
            chunk = stream.read(65536)
            if not chunk:
                time.sleep(0.001)
                continue
            
            bytes_data += chunk
            
            # If buffer gets too large (lagging), drop old data to catch up
            if len(bytes_data) > 10 * 1024 * 1024: # 10MB safety cap
                logger.warning("Buffer full! Dropping frames to catch up.")
                # find last start byte
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
                        # End found before Start? Discard garbage at front
                        bytes_data = bytes_data[a:]
                        continue
                    
                    # We have a candidate frame
                    jpg = bytes_data[a:b+2]
                    bytes_data = bytes_data[b+2:] 
                    
                    # Update the latest frame for the AI thread
                    with buffer_lock:
                        latest_frame_jpg = jpg
                else:
                    break # Wait for more chunks
                    
        except Exception as e:
            logger.error(f"Reader Error: {e}")
            time.sleep(0.1)

# --- AI Logic (Main Processing) ---
def run_ai_processing(location):
    global output_frame, running, latest_frame_jpg
    
    logger.info(f"Starting AI Inference Loop for '{location}'")
    try:
        model = YOLO('yolov8n.pt')
        logger.info("Model loaded.")
    except Exception as e:
        logger.critical(f"Failed to load model: {e}")
        return

    last_send_time = 0

    while running:
        current_jpg = None
        
        # Grab latest available frame
        with buffer_lock:
            if latest_frame_jpg is not None:
                current_jpg = latest_frame_jpg
                # Optional: clear it so we don't process same frame? 
                # No, we want to stream output continuously even if same frame.
        
        if current_jpg is None:
            time.sleep(0.01)
            continue

        try:
            # Decode JPEG
            frame = cv2.imdecode(np.frombuffer(current_jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            
            if frame is not None:
                # Inference
                results = model.predict(frame, classes=[0], conf=CONFIDENCE_THRESHOLD, verbose=False)
                person_count = len(results[0].boxes)
                
                # Annotation
                annotated_frame = results[0].plot()

                # Update Web Stream
                with frame_lock:
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
                        requests.post(BACKEND_URL, json=payload, timeout=0.5)
                        logger.info(f"Updated Backend: Count={person_count}")
                    except Exception as e:
                        logger.warning(f"Backend Sync Failed: {e}")
                    
                    last_send_time = current_time
            
        except Exception as e:
            logger.error(f"Inference Error: {e}")
            time.sleep(0.1)

    logger.info("AI Thread Stopped.")

# --- Web Stream Logic ---
def generate():
    global output_frame
    while True:
        with frame_lock:
            if output_frame is None:
                encodedImage = None
            else:
                (flag, encodedImage) = cv2.imencode(".jpg", output_frame)
                if not flag: encodedImage = None
        
        if encodedImage is not None:
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
        
        time.sleep(0.1) # 10 FPS Web Stream

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
    args = parser.parse_args()

    # Start Reader Thread
    t_reader = threading.Thread(target=stdin_reader)
    t_reader.daemon = True
    t_reader.start()

    # Start AI Thread
    t_ai = threading.Thread(target=run_ai_processing, args=(args.location,))
    t_ai.daemon = True
    t_ai.start()

    # Start Web Server
    logger.info("Starting Web Stream on port 5000...")
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="error")
