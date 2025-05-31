import requests
import os
import time
import json
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
VIZARD_API_KEY = os.getenv("VIZARD_API_KEY")

# API headers
headers = {
    "VIZARDAI_API_KEY": VIZARD_API_KEY,
    "Content-Type": "application/json"
}

# File paths
PENDING_FILE = "./output/pending_jobs.json"
today = datetime.utcnow().strftime('%Y-%m-%d')
LINKS_FILE = f"./output/links_{today}.txt"

# Throttle limits
MAX_PER_HOUR = 20
MAX_PER_MINUTE = 3
MINUTE_WAIT = 60

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

def save_pending_job(project_id, link):
    job = {
        "project_id": project_id,
        "source_url": link,
        "submitted_at": datetime.utcnow().isoformat() + "Z",
        "status": "PENDING"
    }

    jobs = []
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, "r") as f:
            jobs = json.load(f)

    jobs.append(job)

    with open(PENDING_FILE, "w") as f:
        json.dump(jobs, f, indent=2)

def main():
    if not os.path.exists(LINKS_FILE):
        print(f"⚠️ Link file not found: {LINKS_FILE}")
        return

    with open(LINKS_FILE, "r") as f:
        links = [line.strip() for line in f.readlines() if line.strip()]

    for i, link in enumerate(links):
        if i >= MAX_PER_HOUR:
            print("🛑 Reached hourly limit (20 requests). Stopping.")
            break

        print(f"\n📺 [{i + 1}/{len(links)}] Submitting: {link}")
        try:
            result = submit_video(link)
            project_id = result.get("data", {}).get("projectId")
            if project_id:
                print(f"✅ Submitted — Project ID: {project_id}")
                save_pending_job(project_id, link)
            else:
                print("⚠️ No projectId returned")
        except Exception as e:
            print(f"❌ Error submitting video: {e}")

        # Throttle after every 3 requests
        if (i + 1) % MAX_PER_MINUTE == 0 and i != 0:
            print(f"⏳ Waiting {MINUTE_WAIT}s to respect API rate limits...")
            time.sleep(MINUTE_WAIT)

if __name__ == "__main__":
    main()
