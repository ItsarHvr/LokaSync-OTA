from os.path import join, dirname
from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError

from cores.config import env
from utils.logger import logger

SERVICE_ACCOUNT_FILE = join(dirname(__file__), '../../../', env.GOOGLE_DRIVE_CREDS_NAME)
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def check_gdrive_credentials(service_account_file: str) -> bool:
    """
    Check if the Google Drive service account credentials file exists.
    """
    try:
        with open(service_account_file, 'r'):
            logger.gdrive_info("Google Drive service account credentials file found")
        return True
    except FileNotFoundError:
        logger.gdrive_error(f"Google Drive service account credentials file not found: {service_account_file}")
        return False

def gdrive_client() -> Resource | None:
    """
    Create a Google Drive service using the service account credentials.
    """
    try:
        is_gdrive_creds_valid = check_gdrive_credentials(SERVICE_ACCOUNT_FILE)
        if not is_gdrive_creds_valid:
            logger.gdrive_error("Invalid Google Drive service account credentials.")
            return None
          
        # If the credentials file is valid, proceed to create the service
        if not SERVICE_ACCOUNT_FILE:
            logger.gdrive_error("Google Drive service account credentials file path is not set.")
            return None

        # Create the Google Drive service
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=SCOPES
        )
        service = build('drive', 'v3', credentials=credentials)
        logger.gdrive_info("Google Drive service created successfully")
        return service
    except Exception as e:
        logger.gdrive_error(f"Failed to create Google Drive service: {str(e)}")
        return None

def create_folder_if_not_exists(
  service: Resource,
  folder_name: str,
  parent_folder_id: str = None
) -> str | None:
    """
    Create a folder in Google Drive if it doesn't exist.
    
    Args:
        service: Google Drive service instance
        folder_name: Name of the folder to create
        parent_folder_id: ID of the parent folder (optional)
    
    Returns:
        Folder ID if created or found, None if failed
    """
    try:
        # Search for existing folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_folder_id:
            query += f" and '{parent_folder_id}' in parents"
        
        results = service.files().list(q=query).execute()
        items = results.get('files', [])
        
        if items:
            # Folder already exists
            folder_id = items[0]['id']
            logger.gdrive_info(f"Folder '{folder_name}' already exists with ID: {folder_id}")
            return folder_id
        
        # Create new folder
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]
        
        folder = service.files().create(body=file_metadata, fields='id').execute()
        folder_id = folder.get('id')
        
        logger.gdrive_info(f"Created new folder '{folder_name}' with ID: {folder_id}")
        return folder_id
        
    except HttpError as e:
        logger.gdrive_error(f"Failed to create folder '{folder_name}'", e)
        return None