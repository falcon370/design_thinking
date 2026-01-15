import socket
import concurrent.futures

def check_rtsp_port(ip, port=554, timeout=1):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            result = s.connect_ex((ip, port))
            if result == 0:
                try:
                    # Try to grab a banner or just assume open is enough
                    return True, "Port 554 Open (likely Camera)"
                except:
                    return True, "Port 554 Open"
            return False, None
        except:
            return False, None

def scan_network(subnet="192.168.68.", start_ip=1, end_ip=254):
    print(f"Scanning {subnet}1 to {subnet}{end_ip} for RTSP devices (Port 554)...")
    
    found_cameras = []
    
    # Priority check for the IPs found in ARP table to speed things up
    priority_ips = [100, 101, 102, 105, 107]
    other_ips = [i for i in range(start_ip, end_ip + 1) if i not in priority_ips]
    
    all_ips_to_scan = priority_ips + other_ips

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_ip = {
            executor.submit(check_rtsp_port, f"{subnet}{i}"): f"{subnet}{i}" 
            for i in all_ips_to_scan
        }
        
        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                is_open, msg = future.result()
                if is_open:
                    print(f"✅ FOUND DEVICE: {ip} - {msg}")
                    found_cameras.append(ip)
            except Exception as exc:
                pass

    if not found_cameras:
        print("❌ No cameras found on standard RTSP port (554).")
        print("Try: Checking if the camera uses a non-standard port or is on a different subnet.")
    else:
        print("\nPossible Camera IPs:")
        for cam in found_cameras:
            print(f" -> {cam}")

if __name__ == "__main__":
    scan_network()
