from fastapi import Depends, HTTPException
from typing import Dict, Any, Optional, List

from models.log import LogModel
from schemas.log import LogFilterOptions
from repositories.log import LogRepository
from repositories.node import NodeRepository


class LogService:
    def __init__(
        self,
        logs_repository: LogRepository = Depends(),
        nodes_repository: NodeRepository = Depends()
    ):
        self.logs_repository = logs_repository
        self.nodes_repository = nodes_repository

    async def get_all_logs(
        self,
        filters: dict = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[LogModel]:
        return await self.logs_repository.get_all_logs(filters=filters, skip=skip, limit=limit)
    
    async def delete_log(self, node_codename: str, firmware_version: Optional[str]) -> None:
        node_exist = await self.nodes_repository.get_node_by_codename(node_codename)
        if not node_exist:
            raise HTTPException(status_code=404, detail="Node not found.")

        deleted = await self.logs_repository.delete_log(node_codename, firmware_version)
        if not deleted:
            raise HTTPException(status_code=404, detail="Firmware version not found.")

    async def count_logs(self, filters: Dict[str, Any]) -> int:
        return await self.logs_repository.count_logs(filters)

    async def get_filter_options(self) -> LogFilterOptions:
        return await self.logs_repository.get_filter_options()