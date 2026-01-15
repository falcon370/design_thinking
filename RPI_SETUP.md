# Raspberry Pi Camera setup for Streaming

Since we are moving to a distributed setup where the Raspberry Pi captures video and the Laptop processes it, we need to turn the Pi into an "IP Camera".

## Device Configuration
- **Device:** Raspberry Pi 4 Model B
- **Hostname:** `napoleanpranav`
- **Username:** `napoleanpranav`
- **Password:** `pranav123`
- **Connection:** `ssh napoleanpranav@napoleanpranav.local` (or via IP)

## Step 1: Prepare the Raspberry Pi (Once)
Open a terminal on your Raspberry Pi and install VLC (which acts as our streaming server).

```bash
sudo apt update
sudo apt install vlc -y
```

## Step 2: Start the Camera Stream (Final Working Method: HTTP/MJPEG)
The most reliable method that bypasses most firewalls is standard HTTP streaming with MJPEG.

Run this on the Raspberry Pi:
```bash
libcamera-vid -t 0 --inline --width 640 --height 480 --framerate 15 --codec mjpeg -o - | cvlc stream:///dev/stdin --sout '#standard{access=http,mux=mpjpeg,dst=:8080}' :demux=mjpeg
```
*   **If errors occur**: Ensure `vlc` is installed (`sudo apt install vlc -y`).

## Step 3: Connect the System
On your laptop, run:
```powershell
.\start_system.ps1 -HostIP 192.168.68.107 -CameraURL "http://192.168.68.106:8080"
```
*(Replace IPs with your actual laptop and RPi IPs)*

