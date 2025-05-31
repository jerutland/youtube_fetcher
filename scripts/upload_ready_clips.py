import os
import sys
import json

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from upload.youtube_uploader import upload_video

PENDING_FILE = "./output/pending_jobs.json"

def load_pending_jobs():
    if not os.path.exists(PENDING_FILE):
        return []
    with open(PENDING_FILE, "r") as f:
        return json.load(f)

def save_pending_jobs(jobs):
    with open(PENDING_FILE, "w") as f:
        json.dump(jobs, f, indent=2)

def main():
    jobs = load_pending_jobs()
    updated_jobs = []

    for job in jobs:
        if job.get("status") != "DONE" or not job.get("local_paths"):
            updated_jobs.append(job)
            continue

        print(f"\n🚀 Uploading clips for project: {job['project_id']}")
        uploaded = job.get("uploaded_paths", [])

        for clip in job["local_paths"]:
            # Handle legacy string entries for backward compatibility
            if isinstance(clip, str):
                clip = {
                    "path": clip,
                    "title": f"AI Clip from Project {job['project_id']}",
                    "description": f"Auto-edited with AI from {job.get('source_url', '')}",
                    "tags": ["ai", "shorts", "truecrime", "vizard", "automation"]
                }

            path = clip["path"]

            if path in uploaded:
                print(f"⏩ Already uploaded: {path}")
                continue

            try:
                print(f"🎬 Uploading: {path}")
                upload_video(
                    file_path=path,
                    title=clip.get("title", "AI Clip"),
                    description=clip.get("description", ""),
                    tags=clip.get("tags", [])
                )

                uploaded.append(path)
                print(f"✅ Uploaded: {path}")

            except Exception as e:
                error_message = str(e)
                print(f"❌ Upload failed for {path}: {error_message}")

                # Stop if we hit YouTube's daily upload quota
                if "uploadLimitExceeded" in error_message:
                    print("🛑 Reached YouTube daily upload limit. Halting uploads for now.")
                    break

        job["uploaded_paths"] = uploaded
        job["status"] = "UPLOADED" if len(uploaded) == len(job["local_paths"]) else "PARTIAL"
        updated_jobs.append(job)

    save_pending_jobs(updated_jobs)
    print("✅ Uploading complete.")

if __name__ == "__main__":
    main()
