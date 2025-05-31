import subprocess
import time

scripts = [
    ("🔗 Fetching links...", "scripts/fetch_latest.py"),
    ("📤 Submitting to Vizard...", "scripts/process_links_with_vizard.py"),
    ("🕵️ Checking Vizard projects...", "scripts/check_vizard_jobs.py"),
    ("📺 Uploading ready clips to YouTube...", "scripts/upload_ready_clips.py"),
]

def run_script(description, path):
    print(f"\n{description}")
    try:
        subprocess.run(["python", path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Script failed: {path}\n{e}")
        return False
    return True

def main():
    print("🚀 Starting full YouTube automation pipeline...\n")

    for description, script in scripts:
        success = run_script(description, script)
        if not success:
            print("⛔ Halting pipeline due to error.")
            break
        # Wait to space out API calls if needed
        time.sleep(2)

    print("\n✅ Pipeline finished. See logs for details.")

if __name__ == "__main__":
    main()
