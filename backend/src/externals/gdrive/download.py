import io
from typing import Optional, Tuple
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from utils.logger import logger
from .client import gdrive_client

def download_firmware_from_gdrive(file_id: str) -> Optional[Tuple[io.BytesIO, str, str]]:
    """
    Download a firmware file from Google Drive.
    
    Args:
        file_id: Google Drive file ID
    
    Returns:
        Tuple of (file_content, filename, mimetype) or None if failed
    """
    service = gdrive_client()
    if not service:
        logger.gdrive_error("Failed to initialize Google Drive client")
        return None
    
    try:
        # Get file metadata
        file_metadata = service.files().get(fileId=file_id).execute()
        filename = file_metadata.get('name', 'firmware.bin')
        
        logger.gdrive_info(f"Starting download for file: {filename} (ID: {file_id})")
        
        # Download file content
        request = service.files().get_media(fileId=file_id)
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            if status:
                logger.gdrive_debug(f"Download progress: {int(status.progress() * 100)}%")
        
        file_content.seek(0)
        
        logger.gdrive_info(f"Successfully downloaded file: {filename}")
        
        return file_content, filename, 'application/octet-stream'
        
    except HttpError as e:
        if e.resp.status == 404:
            logger.gdrive_error(f"File not found with ID: {file_id}")
        else:
            logger.gdrive_error(f"Google Drive API error during download", e)
        return None
    except Exception as e:
        logger.gdrive_error(f"Unexpected error during firmware download", e)
        return None

def get_firmware_info(file_id: str) -> Optional[dict]:
    """
    Get firmware file information from Google Drive.
    
    Args:
        file_id: Google Drive file ID
    
    Returns:
        Dictionary with file information or None if failed
    """
    service = gdrive_client()
    if not service:
        logger.gdrive_error("Failed to initialize Google Drive client")
        return None
    
    try:
        file_metadata = service.files().get(
            fileId=file_id,
            fields='id,name,size,createdTime,modifiedTime,description'
        ).execute()
        
        return {
            'file_id': file_metadata.get('id'),
            'filename': file_metadata.get('name'),
            'size': int(file_metadata.get('size', 0)),
            'created_time': file_metadata.get('createdTime'),
            'modified_time': file_metadata.get('modifiedTime'),
            'description': file_metadata.get('description', '')
        }
        
    except HttpError as e:
        logger.gdrive_error(f"Failed to get file info for ID: {file_id}", e)
        return None
    except Exception as e:
        logger.gdrive_error(f"Unexpected error getting file info", e)
        return None