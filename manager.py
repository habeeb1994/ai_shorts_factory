import os
import pickle
import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class ManagerAgent:
    def __init__(self, secrets_file='client_secrets.json'):
        self.youtube = self._auth(secrets_file)

    def _auth(self, secrets):
        with open('token.pickle', 'rb') as t:
            creds = pickle.load(t)
        return build("youtube", "v3", credentials=creds)

    def deploy_short(self, file_path, meta, schedule_minutes=0):
        status = {"privacyStatus": "public"}
        
        if schedule_minutes > 0:
            status["privacyStatus"] = "private"
            publish_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=schedule_minutes)
            status["publishAt"] = publish_time.isoformat("T").split('.')[0] + ".000Z"

        request = self.youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {"title": meta['title'], "description": meta['description'], "categoryId": "27"},
                "status": status
            },
            media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
        )
        response = request.execute()
        return response['id']