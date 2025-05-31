import requests
import os
import time
from dotenv import load_dotenv
from datetime import datetime

# Load API key from .env
load_dotenv()
VIZARD_API_KEY = os.getenv("VIZARD_API_KEY")

# Headers for Vizard API
headers = {
    "VIZARDAI_API_KEY": VIZARD_API_KEY,
    "Content-Type": "application/json"
}

# Vizard submission function
def submit_video(video_url, prompt="Extract the best 60s highlight", duration=60):
    data = {
        "videoUrl": video_url,
        "videoType": 2,
        "preferLength": [2],
        "prompt": prompt,
        "clip_duration": duration,
        "lang": "en",
        "platforms": ["youtube"]
    }

    response = requests.post(
        "https://elb-api.vizard.ai/hvizard-server-front/open-api/v1/project/create",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Vizard API error: {response.status_code} - {response.text}")


# Load today's video link file
today = datetime.utcnow().strftime('%Y-%m-%d')
file_path = f'./output/links_{today}.txt'

if not os.path.exists(file_path):
    raise FileNotFoundError(f"No link file found for {today}")

with open(file_path, 'r') as f:
    links = [line.strip() for line in f.readlines() if line.strip()]

# Throttling configuration
MAX_PER_HOUR = 20
MAX_PER_MINUTE = 3
MINUTE_WAIT = 60

# Submit links with throttling
for i, link in enumerate(links):
    if i >= MAX_PER_HOUR:
        print("🛑 Reached hourly limit (20 requests). Stopping batch.")
        break

    print(f"\n📺 [{i + 1}/{len(links)}] Submitting: {link}")
    try:
        result = submit_video(link)
        print("✅ Success:")
        print(result)
    except Exception as e:
        print("❌ Failed:", e)

    # Throttle every 3 requests
    if (i + 1) % MAX_PER_MINUTE == 0 and i != 0:
        print(f"⏳ Pausing for {MINUTE_WAIT} seconds to respect rate limit...")
        time.sleep(MINUTE_WAIT)
