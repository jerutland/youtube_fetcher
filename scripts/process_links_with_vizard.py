import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime
from opus_automation.vizard_client import submit_video

# 1. Get today's date filename
today = datetime.utcnow().strftime('%Y-%m-%d')
file_path = f'./output/links_{today}.txt'

# 2. Load video links
if not os.path.exists(file_path):
    raise FileNotFoundError(f"No link file found for {today}")

with open(file_path, 'r') as f:
    links = [line.strip() for line in f.readlines() if line.strip()]

# 3. Submit each link to Vizard
for i, link in enumerate(links):
    print(f"\n📺 [{i + 1}/{len(links)}] Submitting: {link}")
    try:
        result = submit_video(link)
        print("✅ Success:")
        print(result)
    except Exception as e:
        print("❌ Failed:", e)
