import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
VIZARD_API_KEY = os.getenv("VIZARD_API_KEY")

HEADERS = {
    "VIZARDAI_API_KEY": VIZARD_API_KEY,
    "Content-Type": "application/json"
}

PENDING_FILE = "./output/pending_jobs.json"
DOWNLOAD_DIR = "./output/clips"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def get_project_status(project_id):
    url = f"https://elb-api.vizard.ai/hvizard-server-front/open-api/v1/project/query/{project_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get project status: {response.status_code} - {response.text}")


def generate_tags_from_text(text):
    if not text:
        return []
    words = [w.strip("#.,").lower() for w in text.split()]
    keywords = [w for w in words if w.isalpha() and len(w) > 3]
    return list(set(keywords))[:10]


def main():
    if not os.path.exists(PENDING_FILE):
        print("⚠️ No pending jobs to check.")
        return

    with open(PENDING_FILE, "r") as f:
        jobs = json.load(f)

    updated_jobs = []
    for job in jobs:
        if job.get("status") == "DONE":
            updated_jobs.append(job)
            continue

        print(f"🔄 Checking project: {job['project_id']}")
        try:
            data = get_project_status(job["project_id"])
        except Exception as e:
            print(f"❌ Error fetching status: {e}")
            updated_jobs.append(job)
            continue

        status_code = data.get("code")

        if status_code == 2000:
            videos = data.get("videos", [])
            local_paths = []

            if videos:
                for i, video in enumerate(videos):
                    download_url = video.get("videoUrl")
                    if download_url:
                        filename = f"{job['project_id']}_clip_{i+1}.mp4"
                        output_path = os.path.join(DOWNLOAD_DIR, filename)
                        print(f"📥 Downloading clip {i+1}: {output_path}")
                        response = requests.get(download_url)
                        with open(output_path, "wb") as f:
                            f.write(response.content)

                        clip_info = {
                            "path": output_path,
                            "title": video.get("title", f"AI Clip {i+1}"),
                            "description": video.get("viralReason", "Edited with AI."),
                            "tags": generate_tags_from_text(video.get("viralReason", ""))
                        }
                        local_paths.append(clip_info)
                    else:
                        print(f"⚠️ Clip {i+1} in project {job['project_id']} has no videoUrl.")
            else:
                print(f"⚠️ No videos found for project {job['project_id']}")

            job["status"] = "DONE"
            job["local_paths"] = local_paths
        else:
            print(f"⏳ Not ready: {job['project_id']} - Status code: {status_code}")

        updated_jobs.append(job)

    with open(PENDING_FILE, "w") as f:
        json.dump(updated_jobs, f, indent=2)

    print("✅ All checked and saved.")


if __name__ == "__main__":
    main()
