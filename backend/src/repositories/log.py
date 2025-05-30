from fastapi import Depends
from pymongo import DESCENDING
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import (
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection
)

from models.log import LogModel
from schemas.log import LogFilterOptions
from cores.dependencies import (
    get_db_connection,
    get_logs_collection
)


class LogRepository:
    def __init__(
        self,
        db: AsyncIOMotorDatabase = Depends(get_db_connection),
        logs_collection: AsyncIOMotorCollection = Depends(get_logs_collection)
    ):
        self.db = db
        self.logs_collection = logs_collection
    
    async def get_all_logs(
        self,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 10,
    ) -> List[LogModel]:
        cursor = (
            self.logs_collection
            .find(filters or {})
            .sort("created_at", DESCENDING)
            .skip(skip)
            .limit(limit)
        )
        logs = await cursor.to_list(length=limit)
        return [LogModel(**log) for log in logs]
    
    async def delete_log(self, node_codename: str, firmware_version: Optional[str] = None) -> int:
        if firmware_version:
            result = await self.logs_collection.delete_one({
                "node_codename": node_codename,
                "firmware_version": firmware_version
            })
        else:
            result = await self.logs_collection.delete_many({"node_codename": node_codename})

        return result.deleted_count
    
    async def count_logs(self, filters: Dict[str, Any]) -> int:
        return await self.logs_collection.count_documents(filters)
    
    async def get_filter_options(self) -> LogFilterOptions:
        pipeline = [
            {"$group": {
                "_id": None,
                "node_location": {"$addToSet": "$node_location"},
                "node_type": {"$addToSet": "$node_type"},
                "flash_status": {"$addToSet": "$flash_status"}
            }},
            {"$project": {
                "_id": 0,
                "node_location": 1,
                "node_type": 1,
                "flash_status": 1
            }}
        ]

        result = await self.logs_collection.aggregate(pipeline).to_list(length=1)
        if result:
            return LogFilterOptions(**result[0])
        
        # Return empty lists if not have result
        return LogFilterOptions(
            node_locations=[],
            node_types=[],
            flash_statuses=[]
        )