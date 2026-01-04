# 📘 Technical Reference & Data Flow

This document details the internal working of the three services, their data structures, inputs/outputs, and timing mechanisms.

---

## 1. Edge Analytics Service (The "Eye")
**File:** `src/edge_service/main.py`

### Function
Captures video frames, detects people using Computer Vision (YOLOv8), and pushes structured data to the backend.

### Input
*   **Arguments:** `<location_id>` (e.g., "canteen") and `<camera_source>` (ID `0` or RTSP URL).
*   **Source:** Laptop Webcam or Wi-Fi IP Camera.
*   **Frame Rate:** Dependent on hardware (typically 30 FPS), but inference runs on every frame in the loop.

### Processing
1.  **Capture:** Reads a frame from the video source.
2.  **Inference:** Runs YOLOv8 Nano model to detect objects of class `person` (Class ID `0`).
3.  **Logic:** Counts bounding boxes. Determines density level based on thresholds:
    *   `Low`: 0 - 5 people
    *   `Medium`: 6 - 15 people
    *   `High`: > 15 people

### Output (JSON Payload)
Sent via `POST` request to `http://localhost:8000/update-crowd-data`.

```json
{
  "location_id": "canteen",
  "timestamp": "2026-01-04T15:30:00.123456",
  "count": 12,
  "density_level": "Medium",
  "trend": "Stable"
}
```

### Timers & Background
*   **Send Interval:** `2.0 seconds` (Configurable via `SEND_INTERVAL`).
*   **Execution:** Runs as a continuous foreground process (Python script).

---

## 2. Backend Service (The "Brain")
**File:** `src/backend_service/main.py`

### Function
Acts as the central state manager. Receives updates from multiple Edge services and serves the latest state to the Frontend. Persists data to `crowd_data.json`.

### Endpoints

#### A. Receive Data (`POST /update-crowd-data`)
*   **Input:** JSON payload from Edge Service (see above).
*   **Action:** Updates the in-memory dictionary `crowd_data` and saves it to `crowd_data.json`.
*   **Response:** `200 OK` `{"status": "success", "received": ...}`

#### B. Serve Status (`GET /current-status`)
*   **Input:** None.
*   **Action:** Retrieves the current value of `crowd_data`.
*   **Output:** JSON Response (Dictionary of locations).

```json
{
  "canteen": {
    "location_id": "canteen",
    "timestamp": "...",
    "count": 12,
    "density_level": "Medium",
    "trend": "Stable"
  },
  "library": {
    "location_id": "library",
    "timestamp": "...",
    "count": 5,
    "density_level": "Low",
    "trend": "Stable"
  }
}
```
*   **Fallback:** If no data has been received yet, returns default "Unknown" states for configured locations.

### Timers & Background
*   **Server:** Uvicorn (ASGI Server).
*   **Persistence:** Writes to disk on every update (simple JSON dump).

---

## 3. Frontend Service (The "Face")
**File:** `src/frontend/index.html`

### Function
A static HTML/JS page that visualizes the crowd data for multiple locations.

### Input
*   Fetches data from `http://localhost:8000/current-status`.

### Processing
1.  **Polling:** JavaScript `setInterval` triggers `fetchData()` function.
2.  **DOM Update:** Iterates through the received JSON object and updates the corresponding HTML cards for each `location_id`.

### Output (Visuals)
*   **Density Badge:** Green (Low), Yellow (Medium), Red (High).
*   **Count:** Numeric value.
*   **Trend:** Text indicator.
*   **Last Updated:** Timestamp converted to local time.

### Timers & Background
*   **Refresh Rate:** Staggered updates (every 2-5 seconds) to avoid UI flickering.
*   **Hosting:** Served via Python's `http.server` on port `8081`.

---

## 🔄 End-to-End Data Flow

1.  **T=0s**: Camera captures frame.
2.  **T+0.1s**: Edge Service detects **5 people**.
3.  **T+0.1s**: Edge Service checks timer. If > 2s since last send, constructs JSON.
4.  **T+0.2s**: Edge Service sends `POST` to Backend.
5.  **T+0.25s**: Backend updates memory: `count=5`.
6.  **T+1.0s**: Frontend Timer fires (every 2s).
7.  **T+1.1s**: Frontend requests `GET /current-status`.
8.  **T+1.15s**: Frontend receives JSON and updates UI to **Green/Low**.

## ⚙️ Service Configuration Summary

| Service | Technology | Port | Key Config |
| :--- | :--- | :--- | :--- |
| **Edge** | Python / OpenCV / YOLO | N/A | `SEND_INTERVAL = 2.0` |
| **Backend** | FastAPI / Uvicorn | `8000` | In-Memory Storage |
| **Frontend** | HTML5 / JS | `8081` | `setInterval(..., 2000)` |
