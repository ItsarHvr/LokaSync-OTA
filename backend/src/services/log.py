from fastapi import Depends, HTTPException
from typing import Dict, Any, Optional, List

from models.log import LogModel
from schemas.log import LogFilterOptions
from repositories.log import LogRepository
from utils.logger import logger


class LogService:
    def __init__(
        self,
        logs_repository: LogRepository = Depends(),
    ):
        self.logs_repository = logs_repository

    async def upsert_log_from_mqtt(
        self,
        session_id: str,
        node_mac: str,
        node_location: str,
        node_type: str,
        node_id: str,
        node_codename: str,
        firmware_version: str,
        update_fields: Dict[str, Any],
        log_data: Dict[str, Any]
    ) -> Optional[LogModel]:
        """
        Upsert log entry in MongoDB.
        Returns LogModel with proper _id if successful, None otherwise.
        """
        logger.api_info(f"Service: Upserting log from MQTT for node '{node_codename}' - Version: '{firmware_version}'")

        filter_query = {
            "session_id": session_id,
            "node_mac": node_mac,
            "node_location": node_location,
            "node_type": node_type,
            "node_id": node_id,
            "node_codename": node_codename,
            "firmware_version": firmware_version
        }
        
        result = await self.logs_repository.upsert_log(
            filter_query=filter_query,
            update_fields=update_fields,
            log_data=log_data
        )
        
        if result:
            logger.api_info(f"Service: Successfully upserted log for node '{node_codename}'")
        else:
            logger.api_error(f"Service: Failed to upsert log for node '{node_codename}'")
            
        return result

    async def get_all_logs(
        self,
        filters: dict = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[LogModel]:
        logger.api_info(f"Service: Retrieving logs - Skip: {skip}, Limit: {limit}, Filters: {filters}")
        
        logs = await self.logs_repository.get_all_logs(filters=filters, skip=skip, limit=limit)
        
        logger.api_info(f"Service: Retrieved {len(logs)} logs")
        return logs
    
    async def get_detail_log(
        self,
        node_codename: str,
        firmware_version: str
    ) -> Optional[LogModel]:
        logger.api_info(f"Service: Retrieving log for node '{node_codename}' - Version: '{firmware_version}'")

        log = await self.logs_repository.get_detail_log(node_codename=node_codename, firmware_version=firmware_version)
        
        if log:
            logger.api_info(f"Service: Log found for node '{node_codename}' - Version: '{firmware_version}'")
        else:
            logger.api_error(f"Service: No log found for node '{node_codename}' - Version: '{firmware_version}'")
            raise HTTPException(status_code=404, detail="Log or firmware version not found.")

        return log
    
    async def delete_log(self, node_codename: str, firmware_version: Optional[str]) -> None:
        logger.api_info(f"Service: Deleting log for node '{node_codename}' - Version: '{firmware_version}'")

        node_exist = await self.logs_repository.get_node_by_codename(node_codename)
        if not node_exist:
            logger.api_error(f"Service: No logs found for node '{node_codename}'")
            raise HTTPException(status_code=404, detail="Node not found.")

        deleted = await self.logs_repository.delete_log(node_codename, firmware_version)
        if not deleted:
            logger.api_error(f"Service: No logs deleted for node '{node_codename}' - Version: '{firmware_version}'")
            raise HTTPException(status_code=404, detail="Firmware version not found.")
        
        logger.api_info(f"Service: Successfully deleted {deleted} log(s) for node '{node_codename}'")

    async def count_logs(self, filters: Dict[str, Any]) -> int:
        logger.api_info(f"Service: Counting logs with filters: {filters}")
        
        count = await self.logs_repository.count_logs(filters)
        
        logger.api_info(f"Service: Total logs count: {count}")
        return count

    async def get_filter_options(self) -> LogFilterOptions:
        logger.api_info("Service: Getting log filter options")
        
        options = await self.logs_repository.get_filter_options()
        
        logger.api_info(f"Service: Retrieved filter options - Locations: {len(options.node_locations)}, Types: {len(options.node_types)}, Statuses: {len(options.flash_statuses)}")
        return options