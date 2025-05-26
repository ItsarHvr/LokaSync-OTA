# from firebase_admin import firestore
# from typing import List, Optional
# from google.cloud.firestore_v1.base_query import FieldFilter
# from datetime import datetime, timezone
# from fastapi.exceptions import HTTPException

# from models.model_log import Log
# from dtos.dto_log import InputLog, FilterOption

# class LogRepository:
#     def __init__(self):
#         self.db = firestore.client()
#         self.log_ref = self.db.collection("log")

#     async def get_list_log(
#         self,
#         node_location: Optional[str] = None,
#         node_status: Optional[bool] = None,
#         page: int = 1,
#         page_size: int = 5
#     ) -> List[Log]:
#         query = self.log_ref

#         # 1. Collect filter data if any.
#         if node_location is not None:
#             query = query.where(filter=FieldFilter("node_location", "==", node_location))
#         if node_status is not None:
#             query = query.where(filter=FieldFilter("node_status", "==", node_status))

#         # 2. Order filtered data by latest_updated field.
#         query = query.order_by("latest_updated", direction=firestore.Query.DESCENDING)

#         # 3. Set offset dan limit.
#         # Offset itu intinya pertambahan item di halaman berikutnya (skip kalau di mongo).
#         # Limit itu batasan item yang ditampilkan di halaman tersebut (per page)
#         offset = (page -1) * page_size
#         query = query.limit(page_size).offset(offset)

#         # 4. Get the results.
#         results = query.stream()
#         logs = [Log(**doc.to_dict()) for doc in results]

#         return logs
    
#     async def count_list_log(
#             self,
#             node_location: Optional[str] = None,
#             node_status: Optional[bool] = None,
#     ) -> int:
#         query = self.log_ref

#         # 1. Collect filter data if any.
#         if node_location is not None:
#             query = query.where(filter=FieldFilter("node_location", "==", node_location))
#         if node_status is not None:
#             query = query.where(filter=FieldFilter("node_status", "==", node_status))

#         # 2. Count the documents.
#         docs = query.stream()

#         # 3. Count the number of documents.
#         count = sum(1 for _ in docs)

#         return count
    
#     async def get_filter_options(self) -> FilterOption:
#         # 1. Stream the documents from the collection.
#         docs = self.log_ref.stream()

#         # 2. Initialize empty lists for node_id and node_location.
#         node_locations = set()
#         node_statuses = set()

#         # 3. Iterate through the documents and collect node_id and node_location.
#         for doc in docs:
#             data = doc.to_dict()
#             node_locations.add(data["node_location"])
#             node_statuses.add(data["node_status"])

#         # 4. Convert sets to lists and sort them.
#         node_locations = sorted(list(node_locations))
#         node_statuses = sorted(list(node_statuses))

#         # 5. Return the filter options as a dictionary.
#         return{
#             "node_location": node_locations,
#             "node_status": node_statuses
#         }
    
#     async def add_log(self, log: InputLog, node_name:str):
#         try:
#             log_data = log.model_dump()
#             log_data["latest_updated"] = datetime.now(timezone.tzname(env.TIMEZONE))

#             # Simpan log ke Firestore
#             await self.log_ref.document(node_name).set(log_data, merge=True)

#             return {"message": f"Log Added successfully to {node_name}."}
        
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=str(e))
