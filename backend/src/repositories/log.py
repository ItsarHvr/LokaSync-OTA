from fastapi import Depends
from pymongo import DESCENDING
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import (
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection
)

from enums.log import LogStatus
from models.log import LogModel
from schemas.log import LogFilterOptions
from cores.dependencies import (
    get_db_connection,
    get_logs_collection
)
from utils.datetime import get_current_datetime
from utils.logger import logger


class LogRepository:
    def __init__(
        self,
        db: AsyncIOMotorDatabase = Depends(get_db_connection),
        logs_collection: AsyncIOMotorCollection = Depends(get_logs_collection)
    ):
        self.db = db
        self.logs_collection = logs_collection
    
    async def upsert_log(
        self,
        filter_query: Dict[str, Any],
        update_fields: Dict[str, Any],
        log_data: Dict[str, Any]
    ) -> Optional[LogModel]:
        """
        Upsert log entry in MongoDB.
        Returns LogModel with proper _id if successful, None otherwise.
        """
        try:
            existing = await self.logs_collection.find_one(filter_query)

            if existing:
                # Update existing log document
                await self.logs_collection.update_one(
                    filter_query,
                    {"$set": update_fields}
                )
                logger.db_info("Log updated in MongoDB")

                # Fetch updated log document
                updated_log = await self.logs_collection.find_one(filter_query)
                return LogModel(**updated_log) if updated_log else None
            else:
                # Create new log document with explicit field initialization
                insert_data = {**filter_query, **update_fields}
                
                # Explicitly set all optional QoS fields to None if not present
                optional_fields = [
                    "download_started_at",
                    "firmware_size_kb", 
                    "bytes_written",
                    "download_duration_sec",
                    "download_speed_kbps", 
                    "download_completed_at",
                    "flash_completed_at"
                ]
                
                for field in optional_fields:
                    if field not in insert_data:
                        insert_data[field] = None
                
                # Set flash_status to default if not present
                if "flash_status" not in insert_data:
                    insert_data["flash_status"] = str(LogStatus.IN_PROGRESS)
                
                # Set created_at if not present
                if "created_at" not in insert_data:
                    insert_data["created_at"] = get_current_datetime()
            
                # Insert without _id (MongoDB will generate it)
                result = await self.logs_collection.insert_one(insert_data)
                logger.db_info(f"Log inserted into MongoDB with ID: {result.inserted_id}")

                # Add the generated _id to the inserted log data
                insert_data["_id"] = result.inserted_id
                return LogModel(**insert_data)
        except Exception as e:
            logger.db_error("MongoDB upsert failed", e)
            return None

    async def get_all_logs(
        self,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 10,
    ) -> List[LogModel]:
        logger.db_info(f"Repository: Retrieving logs - Skip: {skip}, Limit: {limit}, Filters: {filters}")
        
        try:
            cursor = (
                self.logs_collection
                .find(filters or {})
                .sort("created_at", DESCENDING)
                .skip(skip)
                .limit(limit)
            )
            logs = await cursor.to_list(length=limit)
            logger.db_info(f"Repository: Retrieved {len(logs)} logs from database")
            return [LogModel(**log) for log in logs]
        except Exception as e:
            logger.db_error("Repository: Failed to retrieve logs", e)
            return []
    
    async def get_detail_log(self, node_codename: str, firmware_version: str) -> Optional[LogModel]:
        """
        Retrieve a detailed log entry by node codename and firmware version.
        Returns LogModel if found, None otherwise.
        """
        logger.db_info(f"Repository: Retrieving log for node '{node_codename}' - Version: '{firmware_version}'")

        try:
            log = await self.logs_collection.find_one({
                "node_codename": node_codename,
                "firmware_version": firmware_version
            })
            if log:
                logger.db_info(f"Repository: Log found for node '{node_codename}' - Version: '{firmware_version}'")
                return LogModel(**log)
            else:
                logger.db_info(f"Repository: No log found for node '{node_codename}' - Version: '{firmware_version}'")
                return None
        except Exception as e:
            logger.db_error(f"Repository: Failed to retrieve log for node '{node_codename}'", e)
            return None
    
    async def get_node_by_codename(self, node_codename: str) -> bool:
        """
        Check if a node in the logs collection exists by its codename.
        """
        logger.db_info(f"Repository: Checking if log exists for node '{node_codename}'")
        
        try:
            node_exists = await self.logs_collection.find_one({"node_codename": node_codename})
            result = True if node_exists else False
            logger.db_info(f"Repository: Log exists for node '{node_codename}': {result}")
            return result
        except Exception as e:
            logger.db_error(f"Repository: Failed to check log existence for node '{node_codename}'", e)
            return False

    async def delete_log(self, node_codename: str, firmware_version: Optional[str] = None) -> int:
        logger.db_info(f"Repository: Deleting logs for node '{node_codename}' - Version: '{firmware_version}'")

        try:
            if firmware_version:
                result = await self.logs_collection.delete_one({
                    "node_codename": node_codename,
                    "firmware_version": firmware_version
                })
                logger.db_info(f"Repository: Deleted {result.deleted_count} log(s) for node '{node_codename}' version '{firmware_version}'")
            else:
                result = await self.logs_collection.delete_many({"node_codename": node_codename})
                logger.db_info(f"Repository: Deleted {result.deleted_count} log(s) for node '{node_codename}' (all versions)")

            return result.deleted_count
        except Exception as e:
            logger.db_error(f"Repository: Failed to delete logs for node '{node_codename}'", e)
            return 0
    
    async def count_logs(self, filters: Dict[str, Any]) -> int:
        logger.db_info(f"Repository: Counting logs with filters: {filters}")
        
        try:
            count = await self.logs_collection.count_documents(filters)
            logger.db_info(f"Repository: Total logs count: {count}")
            return count
        except Exception as e:
            logger.db_error("Repository: Failed to count logs", e)
            return 0
    
    async def get_filter_options(self) -> LogFilterOptions:
        logger.db_info("Repository: Getting log filter options")
        
        try:
            pipeline = [
                {"$group": {
                    "_id": None,
                    "node_location": {"$addToSet": "$node_location"},
                    "node_type": {"$addToSet": "$node_type"}
                }},
                {"$project": {
                    "_id": 0,
                    "node_location": 1,
                    "node_type": 1
                }}
            ]

            result = await self.logs_collection.aggregate(pipeline).to_list(length=1)

            # Get all flash statuses from the LogStatus enum
            all_flash_statuses = [status.value for status in LogStatus]

            if result:
                filter_options = LogFilterOptions(
                    node_locations=result[0].get("node_location", []),
                    node_types=result[0].get("node_type", []),
                    flash_statuses=all_flash_statuses
                )
            else:
                filter_options = LogFilterOptions(
                    node_locations=[],
                    node_types=[],
                    flash_statuses=all_flash_statuses
                )
            
            logger.db_info("Repository: Log filter options retrieved successfully")
            return filter_options
        except Exception as e:
            logger.db_error("Repository: Failed to get log filter options", e)
            return LogFilterOptions(
                node_locations=[],
                node_types=[],
                flash_statuses=[status.value for status in LogStatus]
            )