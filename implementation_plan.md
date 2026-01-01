# 🚀 Implementation & Testing Plan (V1.0)

## 1. Project Overview
**Goal:** Build a "Campus Crowd Density Awareness System" V1.0 running entirely on a single laptop.
**Deployment:**
- **Dev/Test:** Laptop Webcam (ID `0`).
- **Demo:** External Wi-Fi IP Camera (RTSP/HTTP Stream).
**Architecture:** Monolithic logical separation (Edge + Backend + Frontend) running locally.

---

## 2. Technology Stack
- **Language:** Python 3.9+
- **Computer Vision:** OpenCV (`cv2`), Ultralytics YOLOv8 (`yolov8n` for speed) or MediaPipe.
- **Backend API:** FastAPI (high performance, easy async) or Flask.
- **Frontend:** HTML5, Bootstrap 5, JavaScript (Fetch API for polling).
- **Data Store:** In-memory (Python dict) or SQLite for V1 simplicity.

---

## 3. Implementation Phases

### Phase 1: Environment Setup
1.  **Repository Structure:**
    ```
    /src
      /edge_service    # Video processing logic
      /backend_service # API & State management
      /frontend        # Web assets (html, css, js)
    requirements.txt
    main.py            # Launcher for all services
    ```
2.  **Dependencies:**
    - `opencv-python`
    - `ultralytics` (YOLO)
    - `fastapi` / `flask`
    - `uvicorn` (server)
    - `requests`

### Phase 2: Edge Analytics Service (The "Eye")
**Objective:** Capture video, detect people, calculate density.

1.  **Video Source Abstraction:**
    - Create a config variable `CAMERA_SOURCE`.
    - If `CAMERA_SOURCE == 0`: Use Laptop Webcam.
    - If `CAMERA_SOURCE == "rtsp://..."`: Use Wi-Fi Camera stream.
2.  **Detection Logic:**
    - Load YOLOv8 Nano model (`yolov8n.pt`).
    - Process every Nth frame (e.g., every 5th frame) to save CPU.
    - Count bounding boxes with class `person`.
3.  **Density Logic:**
    - Define thresholds (Configurable):
        - `0-5`: Low
        - `6-15`: Medium
        - `16+`: High
    - Determine "Trend" (Compare current count vs. moving average of last 1 minute).
4.  **Data Push:**
    - Send JSON payload to Backend API:
      ```json
      {
        "timestamp": "2023-10-27T10:00:00",
        "count": 12,
        "density_level": "Medium",
        "trend": "Stable"
      }
      ```

### Phase 3: Backend Service (The "Brain")
**Objective:** Store state and serve to frontend.

1.  **API Endpoints:**
    - `POST /update-crowd-data`: Endpoint for Edge Service to push data.
    - `GET /current-status`: Endpoint for Frontend to fetch latest status.
2.  **State Management:**
    - Use a global variable or a simple `sqlite3` table to store the *latest* record.

### Phase 4: Presentation Service (The "Face")
**Objective:** Display insights to the user.

1.  **Dashboard UI:**
    - **Header:** "Campus Library - Live Status"
    - **Big Card:** Current Density (Color coded: Green/Orange/Red).
    - **Stat:** Person Count (Optional/Hidden for privacy, but good for demo).
    - **Indicator:** Trend Arrow (Up/Down/Flat).
2.  **Auto-Refresh:**
    - JavaScript `setInterval` to call `GET /current-status` every 2-5 seconds.

---

## 4. Testing Plan

### A. Unit & Component Testing
| Component | Test Case | Method | Expected Outcome |
|-----------|-----------|--------|------------------|
| **Edge** | **Webcam Access** | Run script with `source=0` | Window opens showing webcam feed. |
| **Edge** | **IP Cam Access** | Run script with `source=rtsp://...` | Window opens showing IP cam feed. |
| **Edge** | **Person Detection** | Stand in front of camera | Bounding box appears around user. |
| **Backend** | **API Response** | Hit `GET /current-status` via Browser | Returns JSON with default/null data. |
| **Backend** | **Data Update** | Send Mock `POST` via Postman/Curl | `GET` request immediately reflects new data. |

### B. Integration Testing (The "All-in-One" Test)
1.  Start Backend Server (`uvicorn main:app`).
2.  Start Edge Script.
3.  Open Frontend in Browser (`localhost:8000`).
4.  **Action:** Walk into the camera frame.
5.  **Verification:**
    - Edge logs: "Detected 1 person".
    - Edge logs: "Posted to API: 200 OK".
    - Frontend: Status changes from "Low" (0) to "Low" (1) or "Medium" (if threshold met).

### C. Scenario Testing (Demo Rehearsal)

#### Scenario 1: "The Quiet Morning" (Low Density)
- **Setup:** Point camera at empty desk/wall.
- **Input:** No people in view.
- **Expected UI:** Green Badge, "Low Density", Count: 0.

#### Scenario 2: "The Rush Hour" (High Density)
- **Setup:** Have 3-4 team members stand in frame (or use a printed photo of a crowd/video on phone for testing).
- **Input:** Multiple detections.
- **Expected UI:** Red Badge, "High Density", Count: > Threshold.

#### Scenario 3: "Network Failure" (Resilience)
- **Setup:** Disconnect Wi-Fi camera (or turn off Wi-Fi).
- **Expected Behavior:** Edge script should catch exception, retry connection, and NOT crash. Backend should report "Last updated: X mins ago" (Stale data warning).

---

## 5. Hardware Setup for Demo
1.  **Laptop:**
    - Connect to Demo Wi-Fi / Hotspot.
    - Ensure Power Adapter is plugged in (CV is battery intensive).
2.  **Wi-Fi Camera:**
    - Connect to same Wi-Fi / Hotspot.
    - Verify IP Address (e.g., `192.168.1.105`).
    - Verify RTSP Stream URL (e.g., `rtsp://admin:pass@192.168.1.105:554/stream1`).
3.  **Physical Placement:**
    - Camera: Elevated (shelf or tripod), angled down (45 degrees).
    - Laptop: Facing the audience/judges.

## 6. Execution Checklist
- [ ] Python Environment Created (`venv`)
- [ ] Dependencies Installed
- [ ] Backend API Running
- [ ] Edge Service Connected to Camera
- [ ] Frontend Loading Data
- [ ] Thresholds Calibrated for Demo Room Size
