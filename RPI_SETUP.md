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

## Step 2: Start the Camera Stream (Robust Method)
We will use `netcat` (nc) to handle the network stream, as it's more reliable than the built-in tool.

Run this on the Raspberry Pi:
```bash
rpicam-vid -t 0 --inline --width 640 --height 480 --framerate 15 -o - | nc -l -p 8888
```
*   **If `nc: command not found`**, install it: `sudo apt install netcat-traditional -y`
*   **Explanation:** Camera captures video -> Pipes (`|`) it to Netcat -> Netcat waits for a connection on Port 8888.

## Step 3: Connect the System
On your laptop, run:
```powershell
.\start_system.ps1 -HostIP 192.168.68.107 -CameraURL "tcp://192.168.68.106:8888"
```

