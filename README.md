# Campus Crowd Density Awareness System (V1.0)

This project implements a real-time crowd density monitoring system using a single laptop. It consists of three components:
1.  **Edge Service:** Captures video from a webcam/IP camera, detects people using YOLOv8, and sends data to the backend.
2.  **Backend Service:** A FastAPI server that receives crowd data and serves it to the frontend.
3.  **Frontend Service:** A web dashboard that displays real-time crowd density, count, and trends.

---

## 🛠️ Prerequisites

*   **Python 3.9+** installed.
*   **Git** installed.
*   **Webcam** (for testing) or **Wi-Fi IP Camera** (for demo).

---

## 🚀 Installation

1.  **Clone the Repository**
    ```powershell
    git clone https://github.com/falcon370/design_thinking.git
    cd design_thinking
    ```

2.  **Create a Virtual Environment**
    ```powershell
    python -m venv venv
    ```

3.  **Activate the Virtual Environment**
    *   **Windows (PowerShell):**
        ```powershell
        .\venv\Scripts\activate
        ```
    *   **Mac/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install Dependencies**
    ```powershell
    pip install -r requirements.txt
    ```

---

## ▶️ How to Run

### Option 1: Automatic (Recommended for Windows)
We have provided a PowerShell script to start all services in separate windows.

1.  Open a PowerShell terminal in the project root.
2.  Run the script:
    *   **Localhost (Default):**
        ```powershell
        .\start_system.ps1
        ```
    *   **Specific IP (e.g., for mobile testing):**
        If you want to access the dashboard from your phone or another computer, use your laptop's Wi-Fi IP address (e.g., `192.168.68.104`).
        ```powershell
        .\start_system.ps1 -HostIP "192.168.68.104"
        ```
    *   *Optional: Run with debug logging enabled:*
        ```powershell
        .\start_system.ps1 -LogLevel DEBUG
        ```
3.  The dashboard will be available at:
    *   **Localhost:** [http://localhost:8081](http://localhost:8081)
    *   **IP Mode:** `http://<YOUR_IP>:8081` (e.g., `http://192.168.68.104:8081`)
4.  A window showing the camera feed with detections will appear.

### Option 2: Manual Startup
If you prefer to run services manually, open **three separate terminals** and follow these steps:

#### Terminal 1: Backend Service
```powershell
.\venv\Scripts\activate
$env:LOG_LEVEL='INFO'; uvicorn src.backend_service.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 2: Frontend Service
```powershell
python -m http.server 8081 --directory src/frontend
```
*Open [http://localhost:8081](http://localhost:8081) in your browser.*

#### Terminal 3: Edge Service
```powershell
.\venv\Scripts\activate
# Usage: python src/edge_service/main.py <location_id> <camera_source>
python src/edge_service/main.py canteen 0
```

---

## ⚙️ Configuration

### Multi-Camera Support
You can run multiple instances of the Edge Service for different locations.
```powershell
# Terminal A (Canteen - Webcam)
python src/edge_service/main.py canteen 0

# Terminal B (Library - IP Camera)
python src/edge_service/main.py library "rtsp://192.168.1.105:554/stream1"
```

### Logging & Debugging
The system supports three log levels, configurable via the `LOG_LEVEL` environment variable or the `-LogLevel` script parameter:
*   **INFO (Default):** Standard startup/shutdown and transmission logs.
*   **DEBUG:** Detailed logs including every detection count per frame.
*   **CRITICAL:** Only errors and critical failures.

### 🌍 Running on Local Network (Access from Mobile)
To access the dashboard from other devices (e.g., a phone) on the same Wi-Fi:

1.  **Find your Laptop's IP Address:**
    *   Open PowerShell and run `ipconfig`.
    *   Look for "IPv4 Address" (e.g., `192.168.1.10`).

2.  **Update Frontend Config:**
    *   Open `src/frontend/index.html`.
    *   Change line 55:
        ```javascript
        // const API_URL = "http://localhost:8000/current-status";
        const API_URL = "http://192.168.1.10:8000/current-status"; // Replace with YOUR IP
        ```

3.  **Restart Frontend:**
    *   If running manually, restart the frontend terminal.
    *   If using `start_system.ps1`, close and run it again.

4.  **Access from Mobile:**
    *   Open browser on phone: `http://192.168.1.10:8081`

---

## 📂 Project Structure

```
/src
  /backend_service    # FastAPI Server (main.py, test_backend.py)
  /edge_service       # Computer Vision Logic (main.py)
  /frontend           # Web Dashboard (index.html)
requirements.txt      # Python dependencies
start_system.ps1      # Startup script
README.md             # This file
```

## 🛑 Troubleshooting

*   **"Module not found"**: Ensure you activated the virtual environment (`.\venv\Scripts\activate`) before running python commands.
*   **Camera not opening**: Check if another app (Zoom, Teams) is using the camera. Verify `CAMERA_SOURCE` in `src/edge_service/main.py`.
*   **Backend connection error**: Ensure the Backend Service is running on port 8000 before starting the Edge Service.
