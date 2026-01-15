import socket

target_ip = "192.168.68.107"
ports_to_check = [554, 80, 8080, 8000, 37777]  # RTSP, HTTP, HTTP-Alt, Onvif/Dahua-proprietary

print(f"Checking ports on {target_ip}...\n")

for port in ports_to_check:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2.0)
    result = sock.connect_ex((target_ip, port))
    status = "OPEN" if result == 0 else "CLOSED/FILTERED"
    print(f"Port {port}: {status}")
    sock.close()
