import sys
import os
import requests
import time
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.path.join(os.getcwd()))

try:
    from Supplier_Portal_Dashboard.config import settings
except ImportError:
    # If run from /tmp or elsewhere, try to find it
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from Supplier_Portal_Dashboard.config import settings

def test_freepik():
    print(f"Testing Freepik integration...")
    print(f"API Key: {settings.FREEPIK_API_KEY[:5]}...{settings.FREEPIK_API_KEY[-5:]}")
    
    url = "https://api.freepik.com/v1/ai/text-to-image/flux-dev"
    headers = {
        "x-freepik-api-key": settings.FREEPIK_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": "A professional product photography of a high-quality plastic water bottle, cinematic lighting, 8k",
        "num_images": 1,
    }

    print("Step 1: Creating task...")
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"Status Code: {resp.status_code}")
    if resp.status_code != 200:
        print(f"Error: {resp.text}")
        return

    task_id = resp.json().get("data", {}).get("task_id")
    print(f"Task ID: {task_id}")

    print("Step 2: Polling...")
    poll_url = f"{url}/{task_id}"
    for i in range(10):
        time.sleep(3)
        poll_resp = requests.get(poll_url, headers=headers, timeout=20)
        print(f"Poll {i+1} status: {poll_resp.status_code}")
        if poll_resp.status_code == 200:
            full_resp = poll_resp.json()
            data = full_resp.get("data")
            print(f"Full Response: {full_resp}")
            if isinstance(data, list) and len(data) > 0:
                print("Success! Image generated.")
                return
            elif isinstance(data, dict):
                print(f"Status: {data.get('status')}")
                if data.get("status") == "COMPLETED":
                    generated = data.get("generated", [])
                    if len(generated) > 0:
                        image_url = generated[0]
                        print(f"Success! Image URL: {image_url}")
                        # Simulate the download and base64 conversion
                        import base64
                        img_resp = requests.get(image_url, timeout=30)
                        if img_resp.status_code == 200:
                            b64 = base64.b64encode(img_resp.content).decode('utf-8')
                            print(f"Base64 conversion successful. Length: {len(b64)}")
                            return
                        else:
                            print(f"Failed to download image from {image_url}")
                            return
                    return

    print("Polling timed out or failed.")

if __name__ == "__main__":
    test_freepik()
