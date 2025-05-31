import json
import os
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_recent_videos(channel_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        maxResults=5,
        order='date',
        publishedAfter=(datetime.utcnow() - timedelta(days=1)).isoformat("T") + "Z"
    )
    response = request.execute()
    return [f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            for item in response['items'] if 'videoId' in item['id']]

def main():
    try:
        with open('./config/channels.json') as f:
            channels = json.load(f)

        all_links = []
        for channel in channels:
            try:
                links = get_recent_videos(channel['channel_id'])
                all_links.extend(links)
                print(f"✅ {channel['name']} — {len(links)} new videos")

            except Exception as e:
                print(f"❌ Error fetching from {channel['name']}: {e}")

        if not all_links:
            print("⚠️ No new video links found.")
        else:
            os.makedirs('./output', exist_ok=True)
            today = datetime.utcnow().strftime('%Y-%m-%d')
            output_path = f'./output/links_{today}.txt'

            with open(output_path, 'w') as f:
                for link in all_links:
                    f.write(link + '\n')

            print(f"✅ Links saved to: {output_path}")

    except Exception as e:
        print("❌ Unexpected error:", e)


if __name__ == '__main__':
    main()
