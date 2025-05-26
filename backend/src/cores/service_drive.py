# import os
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload

# SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')
# SCOPES = ['https://www.googleapis.com/auth/drive.file']

# def upload_to_drive(filepath, filename, folder_id=None):
#     credentials = service_account.Credentials.from_service_account_file(
#         SERVICE_ACCOUNT_FILE, scopes=SCOPES
#     )
#     service = build('drive', 'v3', credentials=credentials)

#     file_metadata = {
#         'name': filename,
#         'parents': [folder_id] if folder_id else []
#     }
#     media = MediaFileUpload(filepath, resumable=True)
#     file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

#     file_id = file.get('id')
#     service.permissions().create(fileId=file_id, body={'role': 'reader', 'type': 'anyone'}).execute()

#     return f"https://drive.google.com/uc?id={file_id}&export=download"