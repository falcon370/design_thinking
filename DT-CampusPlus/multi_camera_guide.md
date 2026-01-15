# 🎥 Multi-Camera Support Guide

This guide explains how the Campus Crowd Density Awareness System supports monitoring multiple locations simultaneously using different cameras.

---

## 1. Conceptual Overview

The system achieves multi-camera support by decoupling the "Eye" (Edge Service) from the "Brain" (Backend Service).

### A. The Edge Service (The "Reporters")
Think of the Edge Service not as "The System," but as a single "Sensor." To support multiple cameras, we don't change the code; we just **run the code multiple times**.

Each running instance of the Edge Service is independent. It captures video from its specific source (Webcam or IP Camera) and reports data for its specific `location_id` (e.g., "canteen", "library").

### B. The Backend Service (The "Aggregator")
The Backend acts like a mailbox. It receives updates from any running Edge Service.
*   It maintains a dictionary of the latest status for every location.
*   It persists this data to `crowd_data.json` so that if the backend restarts, the last known state is preserved.

### C. The Frontend (The "Dashboard")
The dashboard visualizes the data.
*   It fetches the full list of location statuses from the backend.
*   It maps the data to specific HTML cards based on the `location_id`.

---

## 2. How to Run Multiple Cameras

To monitor multiple locations, you simply open multiple terminals and run an instance of the Edge Service in each one.

### Prerequisites
Ensure the **Backend Service** is running first.
```powershell
# Terminal 1
.\venv\Scripts\activate
uvicorn src.backend_service.main:app --host 0.0.0.0 --port 8000
```

### Command Syntax
The Edge Service script accepts two arguments:
```powershell
python src/edge_service/main.py <LOCATION_ID> <CAMERA_SOURCE>
```
*   `LOCATION_ID`: A unique name for the location (e.g., `canteen`, `library`, `corridor`).
*   `CAMERA_SOURCE`:
    *   `0`, `1`: Integer for USB Webcams.
    *   `rtsp://...` or `http://...`: URL for IP Cameras.

### Example Scenario
You want to monitor the **Canteen** using your laptop webcam and the **Library** using a Wi-Fi IP camera.

#### Step 1: Start the Canteen Service
Open a new terminal (**Terminal 2**):
```powershell
.\venv\Scripts\activate
# Use 'canteen' as ID and '0' for default webcam
python src/edge_service/main.py canteen 0
```

#### Step 2: Start the Library Service
Open another terminal (**Terminal 3**):
```powershell
.\venv\Scripts\activate
# Use 'library' as ID and the RTSP URL for the IP camera
python src/edge_service/main.py library "rtsp://admin:password@192.168.1.105:554/stream1"
```

Now, both services are sending data to the same backend.

---

## 3. Frontend Configuration

The Frontend (`src/frontend/index.html`) is currently configured to display cards for the following locations:
*   `canteen`
*   `library`
*   `corridor`
*   `event_hall`

If you start an Edge Service with one of these IDs, the corresponding card on the dashboard will automatically update.

### Adding New Locations
To display a new location (e.g., "gym"):
1.  Run the Edge Service with the new ID: `python src/edge_service/main.py gym 0`
2.  Edit `src/frontend/index.html` and duplicate one of the card `<div>` blocks.
3.  Change the ID of the card body to `id="card-gym"`.
4.  The JavaScript will automatically map the data for "gym" to this new card.

---

## 4. Troubleshooting & Limitations

### ⚠️ Single Webcam Limitation
You **cannot** open the same webcam (Source `0`) in two different terminals simultaneously. If you try, the second one will crash with an error like:
`[ WARN:0] ... videoio(MSMF): OnReadSample() is called with error status: -1072875772`

**Workaround for Testing on One Laptop:**
If you don't have a second physical camera, you can use a **video file** to simulate the second location.

1.  Record a short video of people walking (e.g., `test_video.mp4`) and save it in the project folder.
2.  Run the second service pointing to that file:
    ```powershell
    python src/edge_service/main.py library "test_video.mp4"
    ```

---

## Summary of Workflow
1.  **Camera 1 (Canteen)** detects 5 people -> Sends `{ "location_id": "canteen", "count": 5 }` to Backend.
2.  **Camera 2 (Library)** detects 20 people -> Sends `{ "location_id": "library", "count": 20 }` to Backend.
3.  **Backend** stores both separately: `{"canteen": {...}, "library": {...}}`.
4.  **Frontend** Canteen Card requests `/current-status/canteen` -> Gets 5.
5.  **Frontend** Library Card requests `/current-status/library` -> Gets 20.
