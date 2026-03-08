#!/bin/bash

# --- configuration ---
# Update this if your laptop IP changes
export BACKEND_HOST=192.168.68.107
export BACKEND_PORT=8000

# --- setup ---
cd ~/crowd_monitoring
source venv/bin/activate

echo "=========================================="
echo "   Starting Campus Crowd Edge Service"
echo "=========================================="
echo "Target Backend: http://$BACKEND_HOST:$BACKEND_PORT"
echo "Camera Mode:    RPiCam -> Pipe -> Python"
echo "Stream URL:     http://<RPi_IP>:5000/video"
echo ""

# --- execution ---
# -t 0        : Run forever
# --inline    : Insert SPS/PPS headers (critical for stream)
# --nopreview : Do not show local preview window (headless)
# -o -        : Output to Standard Output (pipe)
# python3 -u  : Run python in unbuffered mode
rpicam-vid -t 0 --inline --nopreview --width 640 --height 480 --framerate 10 --codec mjpeg -o - | python3 -u edge_service/main_pipe.py canteen
