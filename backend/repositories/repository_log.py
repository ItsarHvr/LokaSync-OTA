from typing import List, Optional
from datetime import datetime, timezone
from fastapi.exceptions import HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection
from models.model_log import Log
from dtos.dto_log import InputLog, FilterOption

class LogRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def get_list_log(
        self,
        node_location: Optional[str] = None,
        node_type: Optional[str] = None,
        ota_status: Optional[str] = None,
        page: int = 1,
        per_page: int = 10
    ) -> List[Log]:
        # base query
        match_query = {}
        if node_location is not None:
            match_query["node_location"] = node_location
        if node_type is not None:
            match_query["node_type"] = node_type
        if ota_status is not None:
            match_query["ota_status"] = ota_status

        # MongoDB aggregation pipline
        pipeline = [
            # Stage 1: Match documents based on query filters
            {"$match": match_query},
            # Stage 2: Sort by latest_updated
            {"$sort": {"timestamp": -1}},
            # Stage 3: Skip for pagination
            {"$skip": (page - 1) * per_page},
            # Stage 4: Limit results per page
            {"$limit": per_page}
        ]

        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=per_page)

        return [
            Log(
                _id=str(doc["_id"]),
                type=doc["type"],
                message=doc["message"],
                node_location=doc["node_location"],
                node_type=doc["node_type"],
                node_name=doc["node_name"],
                timestamp=doc["timestamp"],
                firmware_version=doc["firmware_version"],
                data=doc.get("data"),
                download_status=doc["download_status"],
                ota_status=doc["ota_status"]
            )
            for doc in docs
        ]
    
    async def count_list_log(
            self,
            node_location: Optional[str] = None,
            node_type: Optional[str] = None,
            ota_status: Optional[str] = None
    ) -> int:
        query = {}
        if node_location is not None:
            query["node_name"] = node_location
        if node_type is not None:
            query["node_type"] = node_type
        if ota_status is not None:
            query["ota_status"] = ota_status

        # MongoDB aggregation pipline
        pipeline = [
            # Stage 1: Match documents based on query filters
            {"$match": query},
            # Stage 2: Group by node identifier to get unique nodes
            {"$group": {"_id": "$node_name"}},
            # Stage 3: Count the number of unique nodes
            {"$count": "count"}
        ]

        cursor = self.collection.aggregate(pipeline)
        result = await cursor.to_list(length=1)

        return result[0]["count"] if result else 0
    
    async def get_filter_options(self) -> FilterOption:
        node_names = await self.collection.distinct("node_name")
        firmware_versions = await self.collection.distinct("firmware_version")

        return{
            "node_name": node_names,
            "firmware_version": firmware_versions
        }
    
    async def add_log(self, log: InputLog) -> dict:
        try:
            log_data = log.model_dump()
            log_data["timestamp"] = datetime.now(timezone.utc)

            # Simpan log ke MongoDB
            await self.collection.insert_one(log_data)

            return {"message": f"Log Added successfully."}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Insert failed: {str(e)}")
