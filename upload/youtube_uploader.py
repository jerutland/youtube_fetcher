import os
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "credentials.json", SCOPES)
    credentials = flow.run_local_server(port=8080)
    return build("youtube", "v3", credentials=credentials)

def upload_video(file_path, title, description, tags=None, privacy="public"):
    youtube = get_authenticated_service()

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or [],
                "categoryId": "22",  # People & Blogs
            },
            "status": {
                "privacyStatus": privacy
            }
        },
        media_body=MediaFileUpload(file_path)
    )
    response = request.execute()
    print(f"✅ Uploaded: https://youtu.be/{response['id']}")
