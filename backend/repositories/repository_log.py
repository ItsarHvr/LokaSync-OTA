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
            {"$sort": {
                "node_codename": 1,
                "node_mac": 1,
                "firmware_version": -1,
                "timestamp": -1
            }},
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
                node_id=doc["node_id"],
                node_codename=doc["node_codename"],
                node_location=doc["node_location"],
                node_type=doc["node_type"],
                node_mac=doc.get("node_mac"),
                type=doc["type"],
                message=doc["message"],
                timestamp=doc["timestamp"],
                firmware_version=doc["firmware_version"],
                data=doc.get("data"),
                firmware_size=doc["firmware_size"],
                download_speed=doc["download_speed"],
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
            query["node_location"] = node_location
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
        node_locations = await self.collection.distinct("node_location")
        node_types = await self.collection.distinct("node_type")
        ota_statuses = await self.collection.distinct("ota_status")

        return FilterOption(
            node_location=node_locations,
            node_type=node_types,
            ota_status=ota_statuses
        )
    
    async def add_log(self, log: InputLog) -> dict:
        try:
            log_data = log.model_dump()
            log_data["timestamp"] = datetime.now(timezone.utc)

            is_group = "_group" in log_data["node_codename"]

            filter_query = {
                "node_codename": log_data["node_codename"],
                "firmware_version": log_data["firmware_version"]
            }

            if is_group:
                node_mac = log_data.get("node_mac")
                if not node_mac:
                    raise HTTPException(status_code=400, detail="node_mac wajib diisi jika log dari grup")
                filter_query["node_mac"] = node_mac

            # Ambil field yang wajib selalu diupdate/set dari log_data
            update_fields = {
                "node_id": log_data["node_id"],
                "node_location": log_data["node_location"],
                "node_type": log_data["node_type"],
                "type": log_data["type"],
                "timestamp": log_data["timestamp"],
                "message": log_data.get("message"),
                "data": log_data.get("data"),
            }

            # Simpan node_mac jika ada
            if node_mac := log_data.get("node_mac"):
                update_fields["node_mac"] = node_mac

            msg = log_data.get("message", "").lower()
            default_fields = {}

            # Update fields berdasarkan message
            if "firmware size ok" in msg:
                update_fields["firmware_size"] = log_data.get("data", {}).get("size_kb")
            if "download speed" in msg:
                update_fields["download_speed"] = log_data.get("data", {}).get("speed_kbps")
            if "download complete" in msg:
                update_fields["download_status"] = "success"
            if "ota update complete" in msg:
                update_fields["ota_status"] = "success"

            if "ota update started" in msg:
                update_fields["download_status"] = "pending"
                update_fields["ota_status"] = "pending"
                default_fields["download_speed"] = None

            if "firmware_size" not in update_fields:
                default_fields["firmware_size"] = None
            if "download_speed" not in update_fields:
                default_fields["download_speed"] = None
            if "download_status" not in update_fields:
                default_fields["download_status"] = "pending"
            if "ota_status" not in update_fields:
                default_fields["ota_status"] = "pending"

            update_data = {
                "$set": update_fields,
                "$setOnInsert": default_fields
            }

            result = await self.collection.update_one(filter_query, update_data, upsert=True)

            return {"message": f"Log Added successfully."}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Insert failed: {str(e)}")
