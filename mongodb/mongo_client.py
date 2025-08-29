import asyncio

from pymongo import AsyncMongoClient, WriteConcern


def create_mongo_client(uri: str, loop: asyncio.AbstractEventLoop = None):
    if loop:
        return AsyncMongoClient(uri, io_loop=loop)
    else:
        return AsyncMongoClient(uri)

MGDB_CLIENT = create_mongo_client('mongodb://localhost:27017/', asyncio.get_event_loop())

MGDB = MGDB_CLIENT.get_database(
    'pos',
    write_concern=WriteConcern(w="majority", wtimeout=1000)
)

async def mongo_start_default_session():
    return await MGDB.start_default_session()