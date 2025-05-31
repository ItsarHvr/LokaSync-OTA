from fastapi import Depends, HTTPException
from typing import Dict, Any, Optional, List

from models.log import LogModel
from schemas.log import LogFilterOptions
from repositories.log import LogRepository


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
        filter_query = {
            "session_id": session_id,
            "node_mac": node_mac,
            "node_location": node_location,
            "node_type": node_type,
            "node_id": node_id,
            "node_codename": node_codename,
            "firmware_version": firmware_version
        }
        
        return await self.logs_repository.upsert_log(
            filter_query=filter_query,
            update_fields=update_fields,
            log_data=log_data
        )

    async def get_all_logs(
        self,
        filters: dict = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[LogModel]:
        return await self.logs_repository.get_all_logs(filters=filters, skip=skip, limit=limit)
    
    async def delete_log(self, node_codename: str, firmware_version: Optional[str]) -> None:
        node_exist = await self.logs_repository.get_node_by_codename(node_codename)
        if not node_exist:
            raise HTTPException(status_code=404, detail="Node not found.")

        deleted = await self.logs_repository.delete_log(node_codename, firmware_version)
        if not deleted:
            raise HTTPException(status_code=404, detail="Firmware version not found.")

    async def count_logs(self, filters: Dict[str, Any]) -> int:
        return await self.logs_repository.count_logs(filters)

    async def get_filter_options(self) -> LogFilterOptions:
        return await self.logs_repository.get_filter_options()