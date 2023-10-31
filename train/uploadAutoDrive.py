
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class UploadAuto:
    def Upload_auto_drive(file_path, file_name):
        print(">>>DANG UP NE>>>>", file_path, file_name)
        SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'client_secrets.json')
        SCOPES = ['https://www.googleapis.com/auth/drive.file']

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        drive_service = build('drive', 'v3', credentials=credentials)


        folder_id = '1aAIkfZS-anf5E6M8uj5nUka5B8Iy4yQn'

        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }

        media = MediaFileUpload(file_path, mimetype='application/octet-stream')

        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        if 'id' in file:
            file_id = file['id']
            file_url = "https://drive.google.com/file/d/" + file_id + "/view"
            return file_url
        else:
            return 0