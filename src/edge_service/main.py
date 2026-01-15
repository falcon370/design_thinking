import cv2
import time
import requests
import sys
import os
import logging
from datetime import datetime
from ultralytics import YOLO

# Parse Command Line Arguments First (to name the log file)
# Usage: python main.py <location_id> <camera_source>
LOCATION_ID = "canteen" # Default
CAMERA_SOURCE = 0       # Default

if len(sys.argv) > 1:
    LOCATION_ID = sys.argv[1]
if len(sys.argv) > 2:
    # Check if source is an integer (webcam index) or string (URL)
    src_arg = sys.argv[2]
    if src_arg.isdigit():
        CAMERA_SOURCE = int(src_arg)
    else:
        CAMERA_SOURCE = src_arg

# Configure Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
BACKEND_HOST = os.getenv("BACKEND_HOST", "192.168.68.107")
#BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"logs/edge_service_{LOCATION_ID}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(f"edge_service_{LOCATION_ID}")

BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}/update-crowd-data"
CONFIDENCE_THRESHOLD = 0.4
SEND_INTERVAL = 2.0  # Send data every 2 seconds

# Density Thresholds
LOW_THRESHOLD = 2
MEDIUM_THRESHOLD = 3

def get_density_level(count):
    if count <= LOW_THRESHOLD:
        return "Low"
    elif count <= MEDIUM_THRESHOLD:
        return "Medium"
    else:
        return "High"

def main():
    logger.info(f"Starting Edge Service for '{LOCATION_ID}' with source: {CAMERA_SOURCE}")
    
    # Load YOLO model
    logger.info("Loading YOLOv8 model...")
    model = YOLO('yolov8n.pt')
    logger.info("Model loaded.")

    # Open Video Source
    cap = cv2.VideoCapture(CAMERA_SOURCE)
    if not cap.isOpened():
        logger.critical("Error: Could not open video source.")
        return

    last_send_time = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.error("Error: Failed to read frame.")
                break

            # Run inference
            results = model.predict(frame, classes=[0], conf=CONFIDENCE_THRESHOLD, verbose=False)
            
            # Count people
            person_count = len(results[0].boxes)
            logger.debug(f"Detected {person_count} people")
            
            # Visualize (Optional - will open a window on the laptop)
            annotated_frame = results[0].plot()
            cv2.imshow("Campus Crowd Monitor", annotated_frame)

            # Send data to backend
            current_time = time.time()
            if current_time - last_send_time > SEND_INTERVAL:
                density_level = get_density_level(person_count)
                
                payload = {
                    "location_id": LOCATION_ID,
                    "timestamp": datetime.now().isoformat(),
                    "count": person_count,
                    "density_level": density_level,
                    "trend": "Stable" # Placeholder for trend logic
                }
                
                try:
                    response = requests.post(BACKEND_URL, json=payload)
                    if response.status_code == 200:
                        logger.info(f"Sent update: Count={person_count}, Level={density_level}")
                    else:
                        logger.error(f"Failed to send update: {response.status_code}")
                except requests.exceptions.ConnectionError:
                    logger.error("Error: Could not connect to backend.")
                
                last_send_time = current_time

            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        logger.info("Stopping Edge Service...")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        logger.info("Edge Service stopped.")

if __name__ == "__main__":
    main()
