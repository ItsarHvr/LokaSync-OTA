from fastapi import Depends

from repositories.monitoring import MonitoringRepository


class MonitoringService:
    def __init__(self, monitoring_repository: MonitoringRepository = Depends()):
        self.monitoring_repository = monitoring_repository

    async def get_list_nodes(self) -> dict:
        """
        Get a list of unique node locations, types, and IDs from the database.
        """
        return await self.monitoring_repository.get_list_nodes()