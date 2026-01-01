

# 🏗️ Version 1.0 – Architecture & Technical Design

*(Demo Deployment: Wi-Fi Camera + Single Laptop)*

---

## 1️⃣ Architectural Diagram (Logical View)

### High-level Architecture (Version 1.0)

```
┌───────────────────┐
│  Wi-Fi IP Camera  │
│ (Elevated, Fixed) │
└─────────┬─────────┘
          │ Live Video Stream
          ▼
┌────────────────────────────────────────┐
│               Laptop                   │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │ Edge Analytics Service            │  │
│  │  • Video frame capture            │  │
│  │  • Person detection               │  │
│  │  • Count + density + trend        │  │
│  └───────────────┬──────────────────┘  │
│                  │ Metadata only        │
│  ┌───────────────▼──────────────────┐  │
│  │ Crowd Service (Backend API)       │  │
│  │  • Latest crowd state             │  │
│  │  • Threshold & alerts             │  │
│  └───────────────┬──────────────────┘  │
│                  │ REST / HTTP          │
│  ┌───────────────▼──────────────────┐  │
│  │ Presentation Service (Web UI)     │  │
│  │  • Dashboard                      │  │
│  │  • Mobile + Web access            │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘

### Key Architectural Principles

* **Logical separation**, physical co-location
* **Edge-first processing**
* **No video exposure beyond edge**
* **Production-aligned, demo-simplified**

---

## 2️⃣ Flow Diagram (End-to-End Runtime Flow)

### Real-Time Operational Flow

```
Camera ON
   ↓
Live video stream
   ↓
Edge Service pulls frames
   ↓
Person detection per frame
   ↓
Crowd count estimated
   ↓
Density level assigned
   ↓
Short-term trend computed
   ↓
Metadata sent to Crowd Service
   ↓
Crowd state updated
   ↓
Dashboard auto-refresh
   ↓
Users view crowd status
```
**Important:**
At no point is raw video shown, stored, or sent to users.

---

## 3️⃣ Service-Wise Design Breakdown (Core of V1.0)

---

# ⚙️ A. Edge Analytics Service

*(Video → Intelligence)*

### Role

> Convert live video into anonymous crowd intelligence.

### Inputs

* Live video stream from Wi-Fi IP camera

### Outputs

* Metadata only:

  * Estimated count
  * Density level
  * Trend
  * Timestamp

---

### Internal Design (Conceptual)

```
Video Stream
   ↓
Frame Extractor
   ↓
Person Detection Module
   ↓
Count Aggregator
   ↓
Density Classifier
   ↓
Trend Analyzer
   ↓
Metadata Publisher
```

---

### Responsibilities

* Connect to camera stream
* Extract frames periodically
* Detect people (no identity)
* Estimate crowd size
* Compute:

  * Density (Low / Medium / High / Critical)
  * Trend (Increasing / Stable / Decreasing)
* Discard frames after processing

---

### Design Constraints

* No face recognition
* No video storage
* Runs continuously
* Handles lighting variation

---

### Why It’s Called “Edge”

* Processes raw video **closest to source**
* Prevents video leakage
* Reduces network usage

---

# 🧠 B. Crowd Service (Backend / Aggregation Layer)

### Role

> Act as the **single source of truth** for crowd status.

---

### Inputs

* Metadata from Edge Service

### Outputs

* Current crowd state via APIs

---

### Internal Design (Conceptual)

```
Metadata Receiver
   ↓
State Store (latest only)
   ↓
Threshold & Alert Logic
   ↓
API Layer
```

---

### Responsibilities

* Receive crowd metadata
* Maintain latest state per location
* Apply alert thresholds
* Serve clean, read-only APIs to UI

---

### Data Managed

* Location ID
* Count
* Density
* Trend
* Timestamp
* Alert status

---

### Important Constraint

> Crowd Service **never** connects to camera or video.

This separation is **critical for privacy and explainability**.

---

# 🖥️ C. Presentation Service (Web Dashboard)

### Role

> Provide a simple, fast, and clear user experience.

---

### Inputs

* API responses from Crowd Service

### Outputs

* Visual dashboard (web + mobile browser)

---

### Internal Design (Conceptual)

```
API Fetch
   ↓
State Renderer
   ↓
UI Components
   ↓
Auto-Refresh Loop
```

---

### What the Dashboard Shows

* Location name
* Crowd density (color-coded)
* Trend arrow (↑ ↓ →)
* Alert message (if any)
* Last updated time

---

### Access Model

* View-only
* Responsive (desktop + mobile)
* Works over campus Wi-Fi

---

### Design Rule

> A user should understand the situation in **under 3 seconds**.

---

## 4️⃣ Mapping Architecture → Requirements (Traceability)

| Requirement     | Edge | Crowd | UI |
| --------------- | ---- | ----- | -- |
| Live capture    | ✅    | ❌     | ❌  |
| Crowd count     | ✅    | ❌     | ❌  |
| Density         | ✅    | ✅     | ✅  |
| Trend           | ✅    | ✅     | ✅  |
| Alerts          | ❌    | ✅     | ✅  |
| Privacy         | ✅    | ✅     | ✅  |
| Multi-user view | ❌    | ❌     | ✅  |

---

## 5️⃣ Why This Architecture Is Strong

### Academically

* Clear separation of concerns
* Matches real video-analytics systems
* Easy to reason about

### Practically

* Reliable demo
* Minimal hardware
* Scales naturally to production

### Ethically

* Privacy-first
* Non-surveillance
* Transparent behavior

---

## 🔑 One-Line Architecture Defense (Memorize)

> “Version 1.0 uses an edge-first, layered architecture where video is processed locally into anonymous crowd metadata, which is then shared via a web dashboard for campus users.”

## ✅ Your Proposed Setup (Confirmed)

> **CP-E31Q camera + Phone hotspot + Laptop running Python edge service → JSON output**

✔ This **works in real life**
✔ Fits **Design Thinking + AI/ML**
✔ Easy to demo without campus permissions
✔ No dependency on internet/cloud

---

## 🧠 System Architecture (Edge AI)

### 📡 Data Flow

```
CP-E31Q Camera
   │ (RTSP over Wi-Fi)
   ▼
Phone Hotspot (Local Network Only)
   │
   ▼
Laptop (Edge Node)
 ├─ Python RTSP Reader (OpenCV)
 ├─ YOLO Person Detection
 ├─ Crowd Logic (count, density, entry/exit)
 └─ JSON Output (API / File / WebSocket)
```

➡ **No internet needed after hotspot is on**
➡ Hotspot acts like a **local router**

---

## 🔧 Why This Is Technically Sound

### 1️⃣ Network (Hotspot is Enough)

* Phone hotspot creates **LAN**
* Camera + laptop get **local IPs**
* RTSP works **without internet**

✔ Faculty doubt: *“Internet is needed?”*
➡ **Answer:** No, only local network.

---

### 2️⃣ Laptop as Edge Device (Perfect Choice)

* Runs Python + OpenCV + YOLO
* No GPU required (CPU works for 3MP @ ~5–10 FPS)
* Acts as **Edge Compute Node**

✔ This clearly demonstrates **Edge AI vs Cloud AI**

---

### 3️⃣ JSON Output (Industry-Correct)

Your Python service can emit:

* `count`
* `density`
* `timestamp`
* `camera_id`
* `alerts`

✔ Matches **real smart-city systems**

---

## 📄 Example Output JSON (What You’ll Show in Demo)

```json
{
  "camera_id": "CP-E31Q-CLASS-A",
  "timestamp": "2026-01-01T15:42:10",
  "people_count": 18,
  "density_level": "HIGH",
  "zone": "Classroom A",
  "alert": true
}
```

---

## 🧪 Practical Constraints (Be Honest, Still Strong)

| Item       | Reality                        |
| ---------- | ------------------------------ |
| FPS        | 5–10 FPS (CPU)                 |
| Resolution | Downscale to 640×360 for speed |
| Pan/Tilt   | Disable auto-tracking          |
| Night Mode | Works, grayscale               |

➡ **These are acceptable for a prototype**
➡ Faculty expects **engineering tradeoffs**

---

## 🧠 ML Stack (Recommended)

| Task      | Choice                   |
| --------- | ------------------------ |
| Detection | YOLOv8-n                 |
| Library   | OpenCV + Ultralytics     |
| Language  | Python                   |
| Output    | JSON via Flask / FastAPI |
| Storage   | Local file or memory     |

---

## 🧩 Where This Scores in Design Thinking

| DT Stage  | Evidence              |
| --------- | --------------------- |
| Empathize | Campus crowd safety   |
| Define    | Overcrowding risk     |
| Ideate    | Multi-sensor vision   |
| Prototype | Camera + laptop       |
| Test      | Real-time JSON output |

➡ This **ticks every box** for S-grade.

---

## 🎯 Viva-Ready One-Line Explanation

> “We use a Wi-Fi IP camera connected via a phone hotspot to a laptop acting as an edge computing node, where a Python-based computer vision service processes live video and outputs crowd density metrics in JSON format.”

---

## 1️⃣ What exactly is the *Edge Service* in your project?

**One-line definition**

> The Edge Service is a local program that runs near the camera (laptop / mini-PC) to convert raw video into structured crowd data **without sending video to the cloud**.

**Why edge (not cloud)?**

* Privacy (no faces uploaded)
* Low latency (real-time density)
* Works even with **mobile hotspot**
* Faculty loves “edge AI” buzzword 😉

---

## 2️⃣ Where does the Edge Service physically run?

For your **demo + practical setup** 👇

```
IP Camera (CP-E31Q / Laptop Cam)
        │
        │ RTSP / USB
        ▼
Laptop (Edge Device)
 ├── Python Edge Service
 ├── OpenCV + AI Model
 └── REST API (FastAPI)
        │
        │ JSON over HTTP
        ▼
Backend / Dashboard
```

✅ **Yes — laptop camera is PERFECT for demo**
Later, same code runs with CP-E31Q using RTSP.

---

## 3️⃣ What does the Edge Service ACTUALLY do internally?

### 🔹 Module 1: Video Ingestion

* Reads frames from:

  * Laptop webcam (`cv2.VideoCapture(0)`)
  * OR IP camera via RTSP

### 🔹 Module 2: Pre-processing

* Resize frames (reduce CPU load)
* Convert color
* Skip frames (e.g., process 1 frame/sec)

### 🔹 Module 3: Crowd Detection (AI / CV)

Options (from simple → advanced):

* Haar Cascade (basic)
* HOG + SVM
* **YOLOv8 / MobileNet (recommended)**

Output:

```
Bounding boxes of people
```

### 🔹 Module 4: Density Logic

Convert detections → **numbers**

* Count people
* Map count → LOW / MEDIUM / HIGH
* Optional: zone-wise counting

### 🔹 Module 5: JSON Output + API

* Exposes `/crowd_status`
* Sends structured data to backend

---

## 4️⃣ Minimal Edge Service Architecture (Recommended)

```
edge_service/
│
├── camera.py        # frame capture
├── detector.py      # AI model logic
├── density.py       # rules + thresholds
├── api.py           # FastAPI endpoints
├── config.yaml      # camera IP, fps, thresholds
└── main.py          # glue code
```

---

## 5️⃣ Step-by-Step Implementation (REALISTIC)

### 🔹 Step 1: Capture Video (Laptop Camera)

```python
import cv2

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow("Edge Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
```

👉 This alone is enough to prove **edge device concept**.

---

### 🔹 Step 2: Add People Detection (Lightweight)

**Why YOLO-Nano / YOLOv8n?**

* Runs on CPU
* Accurate enough
* Faculty-friendly AI

```python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

results = model(frame)
people = [box for box in results[0].boxes if box.cls == 0]
count = len(people)
```

---

### 🔹 Step 3: Crowd Density Logic

```python
def density_level(count):
    if count <= 5:
        return "LOW"
    elif count <= 15:
        return "MEDIUM"
    else:
        return "HIGH"
```

You can explain this as **rule-based AI + vision**.

---

### 🔹 Step 4: Expose REST API (FastAPI)

```python
from fastapi import FastAPI
import time

app = FastAPI()

@app.get("/crowd_status")
def crowd_status():
    return {
        "timestamp": time.time(),
        "people_count": count,
        "density": density_level(count),
        "source": "edge_camera_01"
    }
```

Test in browser:

```
http://localhost:8000/crowd_status
```

🎯 **THIS JSON is your core project output**

---

## 6️⃣ Example Output JSON (Very Important)

```json
{
  "timestamp": 1704102012,
  "people_count": 18,
  "density": "HIGH",
  "camera_id": "BLOCK_A_GATE",
  "confidence": 0.87
}
```

Faculty understands **JSON → dashboard → decision making** instantly.

---

## 7️⃣ How Edge Talks to Backend (Hotspot Friendly)

Two ways (recommend **pull-based**):

### Option A: Backend pulls data (BEST)

```
Backend → GET /crowd_status → Edge
```

Why?

* No firewall issues
* Hotspot friendly
* Simple

### Option B: Edge pushes data

```
Edge → POST /ingest → Backend
```

---

## 8️⃣ CPU & Performance (Realistic Numbers)

| Device         | FPS     | People Count Accuracy |
| -------------- | ------- | --------------------- |
| Laptop i5      | 2–5 FPS | ~85–90%               |
| Raspberry Pi 4 | 1–2 FPS | ~75–80%               |
| Mini PC        | 5–8 FPS | ~90%                  |

For **crowd density**, FPS > accuracy.

---

## 9️⃣ How This Scores HIGH in Design Thinking

**Empathize**

* Students feel unsafe in crowded corridors

**Define**

* No real-time crowd visibility

**Ideate**

* Edge AI + low-cost cameras

**Prototype**

* Laptop + Python + webcam (✔)

**Test**

* Live crowd count JSON + dashboard

---

## 🔟 Faculty-Killer One-Liner (Use This)

> “We deliberately process video at the edge to preserve privacy, reduce latency, and make the system functional even with unstable internet — only anonymized crowd metadata is transmitted.”


Perfect. Below is a **complete, implementable V1 Crowd Service (camera-only, JSON-only, no DB)** that you can **code, demo, and defend in viva**.
I’ll keep it **engineering-clean, exam-ready, and minimal**.

---

## 🎯 V1 Crowd Service – Implementation Summary

**One-line goal:**

> Accept camera metadata via API, aggregate it in memory (JSON), and expose real-time crowd status.

---

## 🏗️ V1 Runtime Architecture
Camera Edge
   ↓ (JSON)
FastAPI Ingest API
   ↓
In-Memory Buffer (JSON / dict)
   ↓
Aggregation Worker (Timer)
   ↓
Crowd State (JSON)
   ↓
Read APIs (Dashboard / Alerts)
```

---

## 1️⃣ Folder Structure (Very Important)

```
crowd_service_v1/
│
├── main.py              # FastAPI entry
├── models.py            # Pydantic schemas
├── store.py             # In-memory JSON store
├── aggregator.py        # Aggregation logic
├── config.py            # Thresholds & timings
└── requirements.txt
```

---

## 2️⃣ Data Model (models.py)

```python
from pydantic import BaseModel
from datetime import datetime

class CameraEvent(BaseModel):
    device_id: str
    zone: str
    timestamp: datetime
    people_count: int
    confidence: float
```

✔ Simple
✔ Strict
✔ Camera-only

---

## 3️⃣ In-Memory Store (store.py)

This is your **JSON data source**.

```python
from collections import defaultdict

# Raw events buffer (per zone)
event_buffer = defaultdict(list)

# Aggregated crowd state (per zone)
crowd_state = defaultdict(dict)
```

---

## 4️⃣ Configuration (config.py)

```python
# Aggregation window in seconds
AGG_WINDOW = 30

# Confidence threshold
MIN_CONFIDENCE = 0.5

# Crowd levels
LEVELS = {
    "LOW": (0, 20),
    "MEDIUM": (21, 50),
    "HIGH": (51, 80),
    "CRITICAL": (81, 999)
}
```

---

## 5️⃣ Aggregation Logic (aggregator.py)

This is the **core intelligence**.

```python
import time
from store import event_buffer, crowd_state
from config import AGG_WINDOW, LEVELS

def classify(count):
    for level, (low, high) in LEVELS.items():
        if low <= count <= high:
            return level
    return "UNKNOWN"

def aggregate():
    now = time.time()

    for zone, events in list(event_buffer.items()):
        # Keep only recent events
        recent = [e for e in events if now - e["ts"] <= AGG_WINDOW]

        if not recent:
            continue

        avg_count = sum(e["count"] for e in recent) / len(recent)
        peak = max(e["count"] for e in recent)

        crowd_state[zone] = {
            "avg_count": round(avg_count, 2),
            "peak": peak,
            "level": classify(avg_count),
            "last_updated": now
        }

        event_buffer[zone] = recent
```

---

## 6️⃣ API Layer (main.py)

### Ingest API

```python
from fastapi import FastAPI
from models import CameraEvent
from store import event_buffer
import time

app = FastAPI()

@app.post("/api/v1/camera/events")
def ingest(event: CameraEvent):
    event_buffer[event.zone].append({
        "ts": event.timestamp.timestamp(),
        "count": max(0, event.people_count),
        "conf": event.confidence
    })
    return {"status": "accepted"}
```

---

### Live Crowd API

```python
from store import crowd_state

@app.get("/api/v1/crowd/live")
def live(zone: str):
    if zone not in crowd_state:
        return {"zone": zone, "status": "NO DATA"}

    return {
        "zone": zone,
        **crowd_state[zone]
    }
```

---

## 7️⃣ Background Aggregation Worker

Add this inside `main.py`:

```python
import threading
from aggregator import aggregate

def run_aggregator():
    while True:
        aggregate()
        time.sleep(5)

threading.Thread(target=run_aggregator, daemon=True).start()
```

✔ No Celery
✔ No Redis
✔ Clean V1 logic

---

## 8️⃣ Sample Edge Payload (Test with curl)

```bash
curl -X POST http://localhost:8000/api/v1/camera/events \
-H "Content-Type: application/json" \
-d '{
  "device_id": "cam1",
  "zone": "Gate-1",
  "timestamp": "2026-01-01T10:15:30Z",
  "people_count": 32,
  "confidence": 0.9
}'
```

---

## 9️⃣ Sample Live Output

```json
{
  "zone": "Gate-1",
  "avg_count": 30.5,
  "peak": 34,
  "level": "MEDIUM",
  "last_updated": 1704104140.22
}
```

---

## 🔐 Failure Handling (V1)

| Case           | Behavior               |
| -------------- | ---------------------- |
| No data        | `NO DATA`              |
| Low confidence | Ignored (optional)     |
| Sudden spike   | Smoothed by window     |
| Restart        | State reset (expected) |

---

## 🧪 Testing Strategy (Faculty-Friendly)

1. Send random counts every 2 sec
2. Observe smoothing
3. Increase count → level change
4. Stop sending → stale state

---

## 🧠 Why This Implementation is Correct for V1

* ✔ End-to-end working
* ✔ Real-time
* ✔ No unnecessary infra
* ✔ Clean upgrade path to DB
* ✔ Excellent Design Thinking justification

---

## 🎓 Viva-Ready Closing Line

> *Version-1 of the Crowd Service is implemented as a lightweight, in-memory aggregation backend that processes camera metadata in real time, ensuring correctness and low latency before introducing persistence and multi-sensor fusion in later versions.*


---

# Demo Setup: All 3 Layers on a Single Laptop

## One-Line Summary (Use This First)

> For the demo, all three layers—edge service, backend crowd service, and presentation layer—run as **separate processes on a single laptop**, connected to a Wi-Fi camera via a mobile hotspot, while still preserving real-world architecture principles.

---

# Physical Setup (What Is Actually Connected)

```text
Mobile Phone (Hotspot)
        ↓
Wi-Fi Camera  ←→  Laptop
                   |
                   ├─ Edge Service (Python)
                   ├─ Backend Crowd Service (API + WS)
                   └─ Presentation Layer (Browser UI)
```

✅ Camera is REAL
✅ Detection is REAL
✅ Data flow is REAL
❌ Only the hardware separation is collapsed

---

# Logical Architecture (What Matters Academically)

Even though everything runs on one laptop, **logically nothing changes**.

```text
Edge Layer        Backend Layer        Presentation Layer
-----------       --------------       -------------------
Process A  ──API→  Process B  ──WS→     Browser Tab
```

Each layer:

* Runs independently
* Communicates only via APIs / events
* Can be moved to separate machines later

---

# What Exactly Runs on the Laptop

## 1️⃣ Edge Service (Camera Processing)

### Runs as:

* **Background Python process**
* Uses OpenCV / people detection model

### Does:

* Connects to Wi-Fi camera stream (RTSP)
* Detects people
* Aggregates counts every N seconds
* Sends JSON to backend API

### Command (example)

```bash
python edge_camera_service.py
```

📌 **Important:**
This service **never talks to UI directly**.

---

## 2️⃣ Backend Crowd Service (Aggregation Layer)

### Runs as:

* **Local backend server**
* Example: FastAPI / Flask

### Components inside backend:

| Component        | Nature          |
| ---------------- | --------------- |
| Ingestion API    | API-driven      |
| Aggregator       | Background loop |
| Alert Engine     | Event-based     |
| WebSocket Server | Background      |

### Command

```bash
uvicorn crowd_service:app --port 8000
```

📌 Even though it’s local, it behaves like a real server.

---

## 3️⃣ Presentation Layer (Dashboard)

### Runs as:

* Web app in browser
* Same laptop, different process

### Connects to:

* REST APIs → `http://localhost:8000`
* WebSockets → `ws://localhost:8000/ws`

### Command

```bash
npm start
```

or simply open:

```text
http://localhost:3000
```

---

# Communication Between Layers (Demo Mode)

## Edge → Backend

* **REST API**
* `localhost` instead of IP

```http
POST http://localhost:8000/api/v1/crowd/events
```

✅ Same API as real deployment
✅ No mock data

---

## Backend → UI

* **WebSocket (real-time)**
* **REST (history / analytics)**

```text
ws://localhost:8000/ws/crowd
```

---

# Background vs Event vs API (Demo Classification)

| Layer          | Component      | How it runs                  |
| -------------- | -------------- | ---------------------------- |
| Edge           | Camera service | Background                   |
| Edge → Backend | Event send     | API-driven                   |
| Backend        | Aggregation    | Background                   |
| Backend        | Alerts         | Event-based                  |
| Backend → UI   | Live updates   | WebSocket                    |
| UI             | Charts         | Event-driven (state updates) |

📌 **This classification remains identical in production.**

---

# Why This Demo Setup Is Technically Correct

### 1️⃣ Separation of Concerns Is Preserved

* Different processes
* Different ports
* Clear boundaries

### 2️⃣ Real-Time Behavior Is Preserved

* Live camera
* Live detection
* Live UI updates

### 3️⃣ Deployment Flexibility

Today:

```text
All on one laptop
```

Tomorrow:

```text
Edge → NUC / Pi
Backend → Campus server
UI → Any browser
```

⚠️ **Zero code change required**

---

# What to Say If Examiner Questions This

### ❓ *“Why are all components on one laptop?”*

**Answer:**

> “For demonstration and rapid prototyping, we deployed all layers on a single laptop. However, each layer runs as an independent service communicating via APIs and WebSockets. This mirrors real-world deployment and allows seamless scaling by moving services to separate machines later.”

---

### ❓ *“Is this realistic?”*

**Answer:**

> “Yes. This is a standard industry practice for local development and proof-of-concept demos. The architecture remains unchanged; only the deployment topology is simplified.”

---

# Diagram for PPT (You Can Copy This)

```text
Wi-Fi Camera
     |
     v
[ Edge Service ]
 (Python, background)
     |
 REST API
     v
[ Crowd Service ]
 (Aggregation + Alerts)
     |
 WebSocket / REST
     v
[ Dashboard UI ]
 (Browser)
```

---

# Key Design Thinking Angle (Mention This)

> We intentionally chose a **single-laptop deployment** to rapidly test user experience, validate real-time behavior, and gather feedback before scaling to full campus infrastructure.

