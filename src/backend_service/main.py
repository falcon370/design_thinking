from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import json
import os
import logging

# Configure Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/backend_service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("backend_service")

app = FastAPI(title="Campus Crowd Awareness Backend")

# Ensure data directory exists
os.makedirs("data", exist_ok=True)
DATA_FILE = "data/crowd_data.json"

# Enable CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Model
class CrowdData(BaseModel):
    location_id: str
    timestamp: str
    count: int
    density_level: str
    trend: str

# Load initial data from file
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                logger.info(f"Loaded data from {DATA_FILE}")
                return data
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    else:
        logger.info(f"No existing data file found at {DATA_FILE}. Starting fresh.")
    return {}

def save_data(data_store):
    try:
        # Convert Pydantic models to dicts for JSON serialization
        serializable_store = {k: v.dict() if hasattr(v, 'dict') else v for k, v in data_store.items()}
        with open(DATA_FILE, "w") as f:
            json.dump(serializable_store, f, indent=4)
        logger.debug(f"Saved data to {DATA_FILE}")
    except Exception as e:
        logger.critical(f"Error saving data: {e}")

# In-memory storage (Dictionary)
crowd_data_store = load_data()

@app.get("/")
def read_root():
    logger.debug("Root endpoint accessed")
    return {"message": "Campus Crowd Awareness API is running"}

@app.post("/update-crowd-data")
def update_crowd_data(data: CrowdData):
    crowd_data_store[data.location_id] = data
    save_data(crowd_data_store) # Save to file on every update
    logger.info(f"Received update for {data.location_id}: Count={data.count}, Level={data.density_level}")
    logger.debug(f"Full payload: {data}")
    return {"status": "success", "received": data}

@app.get("/current-status/{location_id}")
def get_current_status(location_id: str):
    # If data was loaded from JSON, it might be a dict, not a CrowdData object
    # So we handle both cases
    data = crowd_data_store.get(location_id)
    
    if data:
        logger.debug(f"Serving status for {location_id}")
        return data
        
    logger.warning(f"Status requested for unknown location: {location_id}")
    return {
        "location_id": location_id,
        "timestamp": datetime.now().isoformat(),
        "count": 0,
        "density_level": "Unknown",
        "trend": "Stable"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
