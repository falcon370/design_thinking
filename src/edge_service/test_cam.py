import cv2
import sys
import time

def test_camera(index=0):
    print(f"Testing Camera {index} with V4L2...")
    cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
    
    # Force MJPEG - essential for RPi
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        print("Failed to open camera!")
        return

    time.sleep(2) # Warmup
    
    print("Camera opened. Trying to read 10 frames...")
    
    success_count = 0
    for i in range(10):
        ret, frame = cap.read()
        if ret:
            print(f"Frame {i+1}: Success - Shape {frame.shape}")
            success_count += 1
        else:
            print(f"Frame {i+1}: Failed to read")
    
    cap.release()
    print(f"Test complete. Successes: {success_count}/10")

if __name__ == "__main__":
    idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    test_camera(idx)
