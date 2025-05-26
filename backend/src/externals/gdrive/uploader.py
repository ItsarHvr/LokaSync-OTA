from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from externals.gdrive.client import SERVICE_ACCOUNT_FILE, SCOPES
from cores.config import env

async def upload_file(
    filepath: str,
    filename: str,
    folder_id: str = env.GOOGLE_DRIVE_FOLDER_ID
) -> str:
    """ Uploads a file to Google Drive and returns the public download link. """

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {
        'name': filename,
        'parents': folder_id
    }
    media = MediaFileUpload(filepath, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    file_id = file.get('id')
    service.permissions().create(fileId=file_id, body={'role': 'reader', 'type': 'anyone'}).execute()

    return f"https://drive.google.com/uc?id={file_id}&export=download"