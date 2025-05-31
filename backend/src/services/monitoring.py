from fastapi import Depends

from repositories.monitoring import MonitoringRepository
from utils.logger import logger


class MonitoringService:
    def __init__(self, monitoring_repository: MonitoringRepository = Depends()):
        self.monitoring_repository = monitoring_repository

    async def get_list_nodes(self) -> dict:
        logger.api_info("Service: Getting list of available nodes")
        
        try:
            nodes = await self.monitoring_repository.get_list_nodes()
            
            total_locations = len(nodes.get("node_locations", []))
            total_types = len(nodes.get("node_types", []))
            total_ids = len(nodes.get("node_ids", []))
            
            logger.api_info(f"Service: Successfully retrieved node lists - Locations: {total_locations}, Types: {total_types}, IDs: {total_ids}")
            return nodes
            
        except Exception as e:
            logger.api_error("Service: Failed to get list of nodes", e)
            return {
                "node_locations": [],
                "node_types": [],
                "node_ids": []
            }