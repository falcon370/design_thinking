import os
import socket
import subprocess
import re
import concurrent.futures
import time

def get_local_ip():
    try:
        # Connect to a public DNS to determine the most appropriate local interface
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return None

def ping_host(ip):
    # Ping with short timeout (-n 1 count, -w 100 timeout ms)
    # Output suppression for clean logs
    try:
        output = subprocess.check_output(f"ping -n 1 -w 200 {ip}", shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def check_ssh_port(ip):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((ip, 22))
        sock.close()
        if result == 0:
            return True
        return False
    except:
        return False

def get_arp_table():
    arp_output = subprocess.check_output("arp -a", shell=True).decode('utf-8', errors='ignore')
    devices = []
    # Parse output:  192.168.68.105        b8-27-eb-xx-xx-xx     dynamic
    lines = arp_output.split('\n')
    for line in lines:
        parts = line.split()
        if len(parts) >= 3:
            ip = parts[0]
            mac = parts[1].replace('-', ':').lower()
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
                devices.append((ip, mac))
    return devices

def is_rpi_mac(mac):
    rpi_ouis = [
        "b8:27:eb", 
        "dc:a6:32", 
        "e4:5f:01", 
        "28:cd:c1", 
        "d8:3a:dd"
    ]
    for oui in rpi_ouis:
        if mac.startswith(oui):
            return True
    return False

def main():
    print("🔍 Looking for Raspberry Pi on the network...")
    
    # 1. Check mDNS
    print("1️⃣  Trying hostname 'raspberrypi.local'...")
    try:
        ip = socket.gethostbyname("raspberrypi.local")
        print(f"   ✅ Found 'raspberrypi.local' at IP: {ip}")
        print(f"   👉 Use this IP in your configs.")
        return
    except:
        print("   ❌ 'raspberrypi.local' not found.")

    # 2. Network Scan
    local_ip = get_local_ip()
    if not local_ip:
        print("❌ Could not determine local IP. Are you connected to a network?")
        return

    print(f"\n2️⃣  Scanning network subnet (Your IP: {local_ip})...")
    network_prefix = ".".join(local_ip.split('.')[:-1])
    
    # Ping sweep to populate ARP table (fast)
    print("   Populating ARP table (Pinging 1-254)...")
    ips_to_scan = [f"{network_prefix}.{i}" for i in range(1, 255)]
    
    active_ips = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = {executor.submit(ping_host, ip): ip for ip in ips_to_scan}
        for future in concurrent.futures.as_completed(results):
            if future.result():
                # Just activity is enough to populate ARP
                pass

    # Read ARP table
    print("   Checking ARP table for Raspberry Pi MAC addresses...")
    devices = get_arp_table()
    found_rpi = False
    
    for ip, mac in devices:
        vendor = "Unknown"
        if is_rpi_mac(mac):
            vendor = "Raspberry Pi"
            found_rpi = True
            print(f"   🎉 FOUND RASPBERRY PI: IP={ip}, MAC={mac}")
            
            # Check SSH
            if check_ssh_port(ip):
                print(f"      ✅ SSH (Port 22) is OPEN.")
            else:
                print(f"      ⚠️ SSH (Port 22) seems CLOSED.")
        else:
            # Uncomment to see all devices
            # print(f"   Device: IP={ip}, MAC={mac}") 
            pass

    if not found_rpi:
        print("\n❌ No Raspberry Pi found via MAC address.")
        print("Possible reasons:")
        print("1. RPi is not connected to the same Wi-Fi/Ethernet.")
        print("2. RPi is just powered on (USB) but not connected to a router.")
        print("3. Check Ethernet lights on RPi.")

if __name__ == "__main__":
    main()
