from datetime import datetime, timezone, timedelta
from typing import Optional

from db.mongo import get_collection


class RepositoryIdempotency:
    @staticmethod
    async def get(key: str):
        coll = get_collection("idempotency")
        return await coll.find_one({"key": key})

    @staticmethod
    async def create_processing(key: str, endpoint: str, user_id: str):
        coll = get_collection("idempotency")
        now = datetime.now(timezone.utc)
        doc = {"key": key, "endpoint": endpoint, "user_id": user_id, "state": "processing", "created_at": now}
        try:
            await coll.insert_one(doc)
            return doc
        except Exception:
            # duplicate key or other error
            return None

    @staticmethod
    async def set_response(key: str, response: dict, ttl_hours: int = 24):
        coll = get_collection("idempotency")
        expire_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)
        await coll.update_one({"key": key}, {"$set": {"state": "done", "response": response, "expires_at": expire_at}})
        return await coll.find_one({"key": key})
