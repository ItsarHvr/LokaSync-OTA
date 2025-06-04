import os
import tempfile
import time
import gc
from typing import Optional, Dict, Any
from fastapi import UploadFile
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from cores.config import env
from utils.logger import logger
from externals.gdrive.client import gdrive_client, create_folder_if_not_exists

async def upload_firmware_to_gdrive(
    firmware_file: UploadFile,
    node_codename: str,
    firmware_version: str
) -> Optional[Dict[str, Any]]:
    """
    Upload firmware file to Google Drive in a structured folder.
    
    Args:
        firmware_file: The uploaded firmware file
        node_codename: Node codename for folder structure
        firmware_version: Firmware version
    
    Returns:
        Dictionary with file information or None if failed
    """
    service = gdrive_client()
    if not service:
        logger.gdrive_error("Failed to initialize Google Drive client")
        return None
    
    temp_file_path = None
    media = None
    
    try:
        # Validate file
        if not firmware_file.filename.endswith('.bin'):
            logger.gdrive_error("Invalid file type. Only .bin files are allowed")
            return None
        
        # Check file size
        max_size = env.GOOGLE_DRIVE_MAX_FILE_SIZE_MB * 1024 * 1024
        firmware_file.file.seek(0, 2) # Seek to end
        file_size = firmware_file.file.tell()
        firmware_file.file.seek(0) # Reset to beginning
        
        if file_size > max_size:
            logger.gdrive_error(f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)")
            return None
        
        logger.gdrive_info(f"Starting upload for firmware: {firmware_file.filename} ({file_size} bytes)")
        
        # Create folder structure: Root -> node_codename -> firmware files
        main_folder_id = env.GOOGLE_DRIVE_FOLDER_ID
        node_folder_id = create_folder_if_not_exists(service, node_codename, main_folder_id)
        
        if not node_folder_id:
            logger.gdrive_error(f"Failed to create/find folder for node: {node_codename}")
            return None
        
        # Create temporary file with explicit close
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.bin')
        try:
            # Write uploaded file content to temporary file
            content = await firmware_file.read()
            temp_file.write(content)
            temp_file.flush()  # Ensure data is written
            temp_file_path = temp_file.name
        finally:
            temp_file.close()  # Explicitly close the file handle
        
        # Prepare filename with version
        clean_filename = f"{node_codename}_v{firmware_version}.bin"
        
        # Create file metadata
        file_metadata = {
            'name': clean_filename,
            'parents': [node_folder_id],
            'description': f"Firmware version {firmware_version} for node {node_codename}"
        }
        
        # Upload file
        media = MediaFileUpload(
            temp_file_path,
            mimetype='application/octet-stream',
            resumable=True
        )
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,name,size,webViewLink,webContentLink'
        ).execute()
        
        # Make file publicly accessible for download
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        service.permissions().create(
            fileId=file.get('id'),
            body=permission
        ).execute()
        
        # Generate direct download link
        file_id = file.get('id')
        download_link = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        result = {
            'file_id': file_id,
            'filename': file.get('name'),
            'size': int(file.get('size', 0)),
            'download_url': download_link,
            'web_view_link': file.get('webViewLink'),
            'folder_id': node_folder_id
        }
        
        logger.gdrive_info(f"Successfully uploaded firmware: {clean_filename}", {
            'file_id': file_id,
            'size': result['size'],
            'node_codename': node_codename,
            'version': firmware_version
        })
        
        return result
        
    except HttpError as e:
        logger.gdrive_error(f"Google Drive API error during upload", e)
        return None
    except Exception as e:
        logger.gdrive_error(f"Unexpected error during firmware upload", e)
        return None
    finally:
        # Clean up MediaFileUpload object first
        if media:
            try:
                # Force cleanup of MediaFileUpload
                media = None
                gc.collect()  # Force garbage collection
            except:
                pass
        
        # Clean up temporary file with more aggressive retry mechanism
        if temp_file_path and os.path.exists(temp_file_path):
            _cleanup_temp_file(temp_file_path)

def _cleanup_temp_file(temp_file_path: str, max_retries: int = 5, initial_delay: float = 0.1) -> None:
    """
    Aggressively attempt to clean up temporary file with exponential backoff.
    
    Args:
        temp_file_path: Path to temporary file
        max_retries: Maximum number of cleanup attempts
        initial_delay: Initial delay between attempts (doubles each retry)
    """
    for attempt in range(max_retries):
        try:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                logger.gdrive_debug(f"Successfully cleaned up temporary file: {temp_file_path} (attempt {attempt + 1})")
                return
            else:
                logger.gdrive_debug(f"Temporary file already removed: {temp_file_path}")
                return
        except PermissionError as e:
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)  # Exponential backoff
                logger.gdrive_debug(f"Cleanup attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                time.sleep(delay)
                gc.collect()  # Force garbage collection before retry
            else:
                logger.gdrive_warning(f"Failed to clean up temporary file after {max_retries} attempts: {temp_file_path} - {e}")
                # Log the file path for manual cleanup if needed
                logger.gdrive_info(f"Temporary file left behind (manual cleanup may be needed): {temp_file_path}")
        except Exception as e:
            logger.gdrive_warning(f"Unexpected error during cleanup attempt {attempt + 1}: {temp_file_path} - {e}")
            if attempt >= max_retries - 1:
                break