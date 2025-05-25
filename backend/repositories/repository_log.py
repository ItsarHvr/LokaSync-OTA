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
        node_name: Optional[str] = None,
        firmware_version: Optional[str] = None,
        page: int = 1,
        per_page: int = 10
    ) -> List[Log]:
        # base query
        match_query = {}
        if node_name is not None:
            match_query["node_name"] = node_name
        if firmware_version is not None:
            match_query["firmware_version"] = firmware_version

        # MongoDB aggregation pipline
        pipeline = [
            # Stage 1: Match documents based on query filters
            {"$match": match_query},
            # Stage 2: Sort by latest_updated
            {"$sort": {"timestamp": -1}},
            # Stage 3: Skip for pagination
            {"skip": (page - 1) * per_page},
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
                node_name=doc["node_name"],
                firmware_url=doc["firmware_url"],
                latest_updated=doc["latest_updated"],
                firmware_version=doc["firmware_version"]
            )
            for doc in docs
        ]
    
    async def count_list_log(
            self,
            node_name: Optional[str] = None,
            firmware_version: Optional[str] = None,
    ) -> int:
        query = {}
        if node_name is not None:
            query["node_name"] = node_name
        if firmware_version is not None:
            query["firmware_version"] = firmware_version

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
