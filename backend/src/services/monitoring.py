from fastapi import Depends

from repositories.monitoring import MonitoringRepository


class MonitoringService:
    def __init__(self, monitoring_repository: MonitoringRepository = Depends()):
        self.monitoring_repository = monitoring_repository

    async def get_list_nodes(self) -> dict:
        return await self.monitoring_repository.get_list_nodes()