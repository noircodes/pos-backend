from typing import Optional

from pymongo import WriteConcern

from core.config import settings
from mongodb.mongo_client import get_mgdb



def _db():
    return get_mgdb(settings.MONGO_DB)


async def start_session():
    return await _db().client.start_session()


def get_collection(name: str):
    return _db().get_collection(name)


def get_database():
    """Return a synchronous pymongo database for use in tests or admin scripts.
    Production async code should use `get_collection`/motor APIs instead."""
    from pymongo import MongoClient
    from core.config import settings
    client = MongoClient(settings.MONGO_URI)
    return client.get_database(settings.MONGO_DB)
