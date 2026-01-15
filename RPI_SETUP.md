# Raspberry Pi Camera setup for Streaming

Since we are moving to a distributed setup where the Raspberry Pi captures video and the Laptop processes it, we need to turn the Pi into an "IP Camera".

## Step 1: Prepare the Raspberry Pi (Once)
Open a terminal on your Raspberry Pi and install VLC (which acts as our streaming server).

```bash
sudo apt update
sudo apt install vlc -y
```

## Step 2: Start the Camera Stream (Every time)
Run this command on the Raspberry Pi to start streaming video.
*Note: This command uses the modern `libcamera` stack. If you have an older OS, use `raspivid`.*

**For Raspberry Pi OS (Bullseye/Bookworm):**
```bash
libcamera-vid -t 0 --inline --width 640 --height 480 --framerate 15 -o - | cvlc stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8554/stream}' :demux=h264
```

*   **Explanation:**
    *   `-t 0`: Run forever.
    *   `--width 640 --height 480`: Lower resolution is faster and perfectly fine for crowd detection.
    *   `-o -`: Output video to "stdout" (pipe).
    *   `| cvlc ...`: Pipe that video into VLC, which broadcasts it as RTSP.

**Check if it works:**
1.  Keep that terminal open on the Pi.
2.  On your laptop, open VLC Player.
3.  Go to `Media -> Open Network Stream`.
4.  Enter: `rtsp://<RASPBERRY_PI_IP>:8554/stream`
    *   (Replace `<RASPBERRY_PI_IP>` with the actual IP address of your Pi, e.g., `192.168.68.xxx`).
5.  If you see video, it works!

## Step 3: Connect the System
Once the stream is running, start your Campus Crowd System on the laptop with the new stream URL.

**Command:**
```powershell
.\start_system.ps1 -HostIP 192.168.68.106 -CameraURL "rtsp://<RASPBERRY_PI_IP>:8554/stream"
```
