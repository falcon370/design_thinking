# Raspberry Pi Edge Service Deployment

This guide orchestrates the migration of the object detection logic from your laptop to the Raspberry Pi.
The Pi will act as a "Smart Camera" that:
1.  Captures video locally.
2.  Runs YOLOv8 AI to count people.
3.  Sends JSON data to your Laptop Backend.
4.  Streams the *Annotated* Video (with boxes) to a web browser for your demo.

## 1. Prerequisites (On Pi)

You need to install system dependencies for OpenCV and AI.
SSH into your Pi (`ssh napoleanpranav@192.168.68.106`) and run:

```bash
# Update and install system libraries
sudo apt update
sudo apt install -y python3-pip python3-venv libgl1 libglib2.0-0 libopenblas-dev
```

## 2. Setup Project Folder (On Pi)

Create the directory structure:

```bash
mkdir -p ~/crowd_monitoring/edge_service
mkdir -p ~/crowd_monitoring/logs
```

## 3. Copy Files (From Laptop)

Run this from your Laptop's terminal (PowerShell) to copy the necessary files to the Pi.
(Assuming you are in the project root outputting this file):

```powershell
# Copy the AI Model (Heavy, might take a moment)
scp yolov8n.pt napoleanpranav@192.168.68.106:~/crowd_monitoring/

# Copy the Code (Update main.py)
scp src/edge_service/main.py napoleanpranav@192.168.68.106:~/crowd_monitoring/edge_service/
scp src/edge_service/test_cam.py napoleanpranav@192.168.68.106:~/crowd_monitoring/edge_service/

# Copy Requirements
scp requirements_rpi.txt napoleanpranav@192.168.68.106:~/crowd_monitoring/
```

## 4. Install Python Dependencies (On Pi)

Back in your SSH session on the Pi:

```bash
cd ~/crowd_monitoring

# Create Virtual Environment (Optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install Libraries
pip install -r requirements_rpi.txt
```
*Note: Installing `ultralytics` on Pi might take 5-10 minutes as it builds some wheels.*

## 5. Stop the Old Stream

If you still have the `libcamera-vid` command running in a terminal, stop it (Ctrl+C). The Python script needs exclusive access to the camera.

## 6. Run the Edge Service (Robust Method)

Since `cv2.VideoCapture` can be flaky on Raspberry Pi, we will use the native `rpicam-vid` tool and pipe the video directly into our Python script.

Run this command inside your **Raspberry Pi SSH terminal**:

```bash
# Activate Virtual Env (if not already active)
source ~/crowd_monitoring/venv/bin/activate

# Use the 'rpicam-vid' to capture MJPEG and pipe (|) it to our script
# Note: 'rpicam-vid' might be 'libcamera-vid' on older OS versions
rpicam-vid -t 0 --inline --width 640 --height 480 --framerate 15 --codec mjpeg -o - | python3 edge_service/main_pipe.py canteen
```

## 7. Verify

- **Metrics:** Check your Laptop's Backend terminal. You should see "Received update for canteen" logs.
- **Video Demo:** Open your Laptop Browser and go to: `http://192.168.68.106:5000/video`
    - You should see the video with bounding boxes!
