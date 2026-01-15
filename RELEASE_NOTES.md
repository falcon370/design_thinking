# Release Notes - v0.2.0 (Prototype)

**Date:** January 15, 2026
**Status:** Functional Localhost System, Pending External Camera Integration.

## 🚀 Features Implemented
1.  **Distributed Architecture:**
    - **Backend:** FastAPI service handling data aggregation and history.
    - **Edge:** Service running YOLOv8 for person detection.
    - **Frontend:** HTML/JS dashboard with dynamic polling and status cards.

2.  **Network Configurability:**
    - Removed hardcoded `localhost` references.
    - `start_system.ps1` now accepts `-HostIP` to bind services to a specific LAN IP.
    - Frontend automatically receives API endpoints via `config.js` injection.

3.  **Computer Vision Engine:**
    - Migrated from YuNet (Face Detection) to **YOLOv8n (Person/Object Detection)** for better crowd density accuracy.
    - Added standalone camera debug tools (`test_camera.py`, `find_camera.py`).

## 🐛 Known Issues
- **External Camera Connectivity:** 
    - Connection to CP Plus IP Camera (`...105` / `...107`) is failing.
    - RTSP Port 554 appears closed/filtered on the target IP.
    - Workaround: System defaults to local webcam (ID 0) if RTSP fails.

## 📦 File Manifest
- `test_camera.py`: Diagnostic tool for RTSP streams.
- `src/edge_service/main.py`: Core logic for video processing.
- `start_system.ps1`: Deployment automation script.
