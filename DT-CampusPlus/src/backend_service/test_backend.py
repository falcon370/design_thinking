import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_backend():
    print("Testing Backend Service...")

    # 1. Check Root
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Root Endpoint: {response.status_code} - {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Error: Backend is not running. Please start it with 'uvicorn src.backend_service.main:app --reload'")
        return

    # 2. Post Data
    payload = {
        "timestamp": datetime.now().isoformat(),
        "count": 15,
        "density_level": "Medium",
        "trend": "Increasing"
    }
    print(f"Sending Data: {payload}")
    response = requests.post(f"{BASE_URL}/update-crowd-data", json=payload)
    print(f"Post Response: {response.status_code} - {response.json()}")

    # 3. Get Data
    response = requests.get(f"{BASE_URL}/current-status")
    print(f"Get Response: {response.status_code} - {response.json()}")
    
    assert response.json()["count"] == 15
    print("Test Passed!")

if __name__ == "__main__":
    test_backend()
