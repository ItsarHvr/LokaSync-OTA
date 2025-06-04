from typing import List
from googleapiclient.errors import HttpError

from externals.gdrive.client import gdrive_client
from utils.logger import logger

def delete_firmware_from_gdrive(file_id: str) -> bool:
    """
    Delete a firmware file from Google Drive.
    
    Args:
        file_id: Google Drive file ID
    
    Returns:
        True if deleted successfully, False otherwise
    """
    service = gdrive_client()
    if not service:
        logger.gdrive_error("Failed to initialize Google Drive client")
        return False
    
    try:
        # First, check if the file exists
        try:
            service.files().get(fileId=file_id).execute()
        except HttpError as e:
            if e.resp.status == 404:
                logger.gdrive_warning(f"File with ID: {file_id} not found (may have been already deleted)")
                return True  # Consider as success since the file is already gone
            else:
                logger.gdrive_error(f"Error checking file existence with ID: {file_id}", e)
                return False
        
        # Delete the file
        service.files().delete(fileId=file_id).execute()
        logger.gdrive_info(f"Successfully deleted file with ID: {file_id}")
        return True
    except HttpError as e:
        if e.resp.status == 404:
            logger.gdrive_warning(f"File with ID: {file_id} not found during deletion (may have been already deleted)")
            return True  # Consider as success since the file is already gone
        else:
            logger.gdrive_error(f"Failed to delete file with ID: {file_id}", e)
            return False
    except Exception as e:
        logger.gdrive_error(f"Unexpected error during file deletion", e)
        return False

def delete_multiple_firmware_from_gdrive(file_ids: List[str]) -> dict:
    """
    Delete multiple firmware files from Google Drive.
    
    Args:
        file_ids: List of Google Drive file IDs
    
    Returns:
        Dictionary with success/failure counts and details
    """
    if not file_ids:
        logger.gdrive_info("No file IDs provided for deletion")
        return {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'failed_ids': []
        }
    
    logger.gdrive_info(f"Starting batch deletion of {len(file_ids)} files from Google Drive")
    
    successful = 0
    failed = 0
    failed_ids = []
    
    for file_id in file_ids:
        if delete_firmware_from_gdrive(file_id):
            successful += 1
        else:
            failed += 1
            failed_ids.append(file_id)
    
    result = {
        'total': len(file_ids),
        'successful': successful,
        'failed': failed,
        'failed_ids': failed_ids
    }
    
    logger.gdrive_info(f"Batch deletion completed - Total: {result['total']}, Success: {result['successful']}, Failed: {result['failed']}")
    
    return result