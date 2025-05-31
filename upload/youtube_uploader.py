import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    creds = None

    # Load token from file if it exists
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # Refresh or authenticate if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_id = os.getenv("GOOGLE_CLIENT_ID")
            client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

            if not client_id or not client_secret:
                raise Exception("❌ Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET in environment variables")

            client_config = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uris": ["http://localhost:8080"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            }

            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=8080)

        # Save the credentials for next time
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

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
