from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import WriteConcern
from typing import Optional


def get_client(uri: str = "mongodb://localhost:27017/") -> AsyncIOMotorClient:
    # Create a new client per call to avoid event-loop binding issues in test harnesses
    return AsyncIOMotorClient(uri)


def get_mgdb(db_name: str = "pos"):
    client = get_client()
    return client.get_database(
        db_name,
        write_concern=WriteConcern(w="majority", wtimeout=1000)
    )


async def mongo_start_default_session():
    client = get_client()
    return await client.start_session()