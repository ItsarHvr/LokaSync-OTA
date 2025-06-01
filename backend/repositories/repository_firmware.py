from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from models.model_firmware import Firmware
from dtos.dto_firmware import FilterOptions
from datetime import datetime, timezone

class FirmwareRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    def _to_firmware_model(self, doc: dict) -> Firmware:
        return Firmware(
            _id=str(doc["_id"]),
            firmware_description=doc.get("firmware_description", ""),
            firmware_version=doc["firmware_version"],
            firmware_url=doc["firmware_url"],
            latest_updated=doc["latest_updated"],
            node_id=doc["node_id"],
            node_location=doc["node_location"],
            node_codename=doc["node_codename"],
            node_type=doc["node_type"],
            is_group=doc.get("is_group", False)
        )

    def _build_filter_query(
            self, 
            node_id=None, 
            node_location=None, 
            node_type=None
        ) -> dict:
        query = {}
        if node_id is not None:
            query["node_id"] = node_id
        if node_location is not None:
            query["node_location"] = node_location
        if node_type is not None:
            query["node_type"] = node_type
        return query
    
    async def get_list_firmware(
        self,
        node_id: Optional[int] = None,
        node_location: Optional[str] = None,
        node_type: Optional[str] = None,
        page: int = 1,
        per_page: int = 5
    ) -> List[Firmware]:
        # Base query for filtering by parameters
        match_query = self._build_filter_query(node_id, node_location, node_type)
        
        # MongoDB aggregation pipeline to get only the latest firmware version for each node
        pipeline = [
            # Stage 1: Match documents based on query filters
            {"$match": match_query},
            # Stage 2: Sort by node_id, node_location, node_name, and latest_updated
            {"$sort": {"node_id": 1, "node_location": 1, "node_codename": 1, "latest_updated": -1}},
            # Stage 3: Group by node identifier and keep only the first (latest) document
            {"$group": {
                "_id": "$node_codename",  # Group by node_name (could also use a combination like {node_id, sensor_type})
                "doc": {"$first": "$$ROOT"}  # Keep the first document in each group (latest by updated date)
            }},
            # Stage 4: Replace the root with the original document
            {"$replaceRoot": {"newRoot": "$doc"}},
            # Stage 5: Sort results again by latest_updated for global ordering
            {"$sort": {"latest_updated": -1}},
            # Stage 6: Skip for pagination
            {"$skip": (page - 1) * per_page},
            # Stage 7: Limit results per page
            {"$limit": per_page}
        ]
    
        # Execute the aggregation pipeline
        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=per_page)
        return [self._to_firmware_model(doc) for doc in docs]
    
    async def count_list_firmware(
        self,
        node_id: Optional[int] = None,
        node_location: Optional[str] = None,
        node_type: Optional[str] = None
    ) -> int:
        query = self._build_filter_query(node_id, node_location, node_type)

        # MongoDB aggregation pipeline to count unique nodes
        pipeline = [
            # Stage 1: Match documents based on query filters
            {"$match": query},
            # Stage 2: Group by node identifier to get unique nodes
            {"$group": {"_id": "$node_codename"}},
            # Stage 3: Count the number of unique nodes
            {"$count": "count"}
        ]

        result = await self.collection.aggregate(pipeline).to_list(length=1)
        return result[0]["count"] if result else 0
    
    async def get_filter_options(self) -> FilterOptions:
        return {
            "node_id": await self.collection.distinct("node_id"),
            "node_location": await self.collection.distinct("node_location"),
            "node_type": await self.collection.distinct("node_type")
        }
    
    async def get_by_node_name(
            self,
            node_codename: str,
            page: int = 1,
            per_page: int = 10
    ) -> List[Firmware]:
        pipeline = [
            # Stage 1: Match documents based on query filters
            {"$match": {"node_codename": node_codename}},
            # Stage 2: Sort by latest_updated
            {"$sort": {"latest_updated": -1}},
            # Stage 3: Skip for pagination
            {"$skip": (page - 1) * per_page},
            # Stage 4: Limit results per page
            {"$limit": per_page}
        ]

        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=per_page)
        return [self._to_firmware_model(doc) for doc in docs]
    
    async def count_by_node_codename(self, node_codename: str) -> int:
        return await self.collection.count_documents({"node_codename":node_codename})
    
    async def add_firmware(self, firmware_data: dict) -> None:
        firmware_data["latest_updated"] = datetime.now(timezone.utc)
        await self.collection.insert_one(firmware_data)
    
    async def update_firmware(
            self, 
            node_codename: str,
            firmware_data: dict
    ) -> Optional[Firmware]:
        existing = await self.collection.find_one({"node_codename": node_codename})
        if not existing:
            return None
        
        new_data = {
            "node_id": existing["node_id"],
            "node_location": existing["node_location"],
            "node_type": existing["node_type"],
            "node_codename": node_codename,
            "firmware_description": firmware_data.get("firmware_description", ""),
            "firmware_version": firmware_data["firmware_version"],
            "firmware_url": firmware_data["firmware_url"],
            "latest_updated": datetime.now(timezone.utc),
            "is_group": existing.get("is_group", False)
        }
        
        await self.collection.insert_one(new_data)
        return self._to_firmware_model(new_data)
    
    async def update_firmware_description(
            self,
            node_codename: str,
            firmware_version: str,
            update_data: dict
    ) -> bool:
        result = await self.collection.update_one(
            {"node_codename": node_codename, "firmware_version": firmware_version},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def delete_by_firmware_version(self, node_codename: str,firmware_version: str):
        await self.collection.delete_one({
            "node_codename": node_codename,
            "firmware_version": firmware_version
        })

    async def delete_all_by_node_name(self, node_codename: str):
        await self.collection.delete_many({
            "node_codename": node_codename
        })