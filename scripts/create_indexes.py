import asyncio

from mongodb.mongo_client import get_mgdb
from core.config import settings


MGDB = get_mgdb(settings.MONGO_DB)


async def create_indexes():
    await MGDB.get_collection("users").create_index("username", unique=True)
    await MGDB.get_collection("users").create_index("email", unique=True)
    await MGDB.get_collection("products").create_index("sku", unique=True)
    await MGDB.get_collection("inventory").create_index([("store_id", 1), ("product_id", 1)], unique=True)
    await MGDB.get_collection("orders").create_index("idempotency_key", unique=False)
    await MGDB.get_collection("idempotency").create_index("key", unique=True)
    await MGDB.get_collection("idempotency").create_index("expires_at", expireAfterSeconds=0, background=True)


if __name__ == "__main__":
    asyncio.run(create_indexes())
