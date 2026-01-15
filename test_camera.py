import cv2
import sys
import time

def test_rtsp_stream(rtsp_url):
    print(f"Attempting to connect to: {rtsp_url}")
    print("Please wait, this might take a few seconds...")

    # Open the video stream
    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print("❌ Error: Could not open video stream.")
        print("Possible causes:")
        print("1. Incorrect Username/Password/Safety Code.")
        print("2. Incorrect IP Address (confirm with 'ping' or router).")
        print("3. Device is not on the same network.")
        print("4. Camera RTSP stream is disabled in settings.")
        return False

    print("✅ Connection Successful! Opening video window...")
    print("Press 'q' to quit.")

    frame_count = 0
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("❌ Error: Lost connection to stream (Failed to read frame).")
            break

        # Resize for easier viewing if stream is 4K/2K
        frame = cv2.resize(frame, (1280, 720))

        # Display FPS on frame
        frame_count += 1
        elapsed_time = time.time() - start_time
        if elapsed_time > 1:
            fps = frame_count / elapsed_time
            cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            frame_count = 0
            start_time = time.time()

        cv2.imshow("CP PLUS RTSP Test", frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return True

if __name__ == "__main__":
    # If a generic URL argument is provided, just use that
    if len(sys.argv) > 1:
        test_rtsp_stream(sys.argv[1])
        sys.exit(0)

    # Otherwise, try the credential list on the specific IP
    target_ip = "192.168.68.107"
    
    credentials = [
        ("admin", "admin"), 
        ("admin", "888888"),
        ("admin", "pranav123")
    ]

    path_templates = [
        ("/cam/realmonitor?channel=1&subtype=0", "Main Stream"),
        ("/cam/realmonitor?channel=1&subtype=1", "Sub Stream"),
        ("/live", "Simple Path")
    ]
    
    print(f"🔍 Starting comprehensive check for Camera IP: {target_ip}\n")
    
    success = False
    for user, password in credentials:
        if success: break
        
        for path, description in path_templates:
            print(f"--------------------------------------------------")
            print(f"👉 Trying: User='{user}', Pass='{password}', Type='{description}'")
            
            url = f"rtsp://{user}:{password}@{target_ip}:554{path}"
            
            if test_rtsp_stream(url):
                print(f"\n🎉 SUCCESS!")
                print(f"   Credentials: {user}/{password}")
                print(f"   URL Format: {url}")
                success = True
                break
            else:
                print("⚠️ Connection failed.")
    
    if not success:
        print("\n❌ All combinations failed.")
        print(f"Please verify the camera IP {target_ip} is reachable (ping it!) and the port 554 is open.")
