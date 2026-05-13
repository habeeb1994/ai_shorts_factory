import os
import pickle
import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class ManagerAgent:
    def __init__(self, secrets_file='client_secrets.json'):
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        self.youtube = self._auth(secrets_file)

    def _auth(self, secrets):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as t:
                creds = pickle.load(t)
                
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    creds = None
            if not creds:
                flow = InstalledAppFlow.from_client_secrets_file(secrets, self.scopes)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as t:
                pickle.dump(creds, t)
                
        return build("youtube", "v3", credentials=creds)

    def deploy_short(self, file_path, meta, schedule_minutes=0):
        status = {"privacyStatus": "public"}
        
        if schedule_minutes > 0:
            status["privacyStatus"] = "private"
            publish_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=schedule_minutes)
            status["publishAt"] = publish_time.isoformat("T").split('.')[0] + ".000Z"

        full_description = meta['description']
        if meta.get('cta_link') and meta.get('cta_link') not in full_description:
            full_description += f"\n\n👇 Check this out:\n{meta['cta_link']}"

        request = self.youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {"title": meta['title'], "description": full_description, "categoryId": "27"},
                "status": status
            },
            media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
        )
        response = request.execute()
        return response['id']