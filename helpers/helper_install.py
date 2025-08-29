from datetime import datetime, timezone
from typing import Any, List
from fastapi.encoders import jsonable_encoder
from bson import SON
from loguru import logger
from mongodb.mongo_index import MongoIndex, IndexUser
from mongodb.mongo_client import MGDB
from mongodb.mongo_collection import tb_user
from mongodb.mongo_collection_name import CollectionNames

class MongoIndexInit:
    def __init__(self, coll, collName: str, indexes: list[MongoIndex]) -> None:
        self.coll = coll
        self.collName = collName
        self.indexes = indexes

ListMongoIndexInit: list[MongoIndexInit] = [
    MongoIndexInit(tb_user, CollectionNames.tb_user.value, indexes=[i.value for i in IndexUser])
]

class InstallHelper:

    @staticmethod
    async def start_install(
    ) -> dict[str, Any]:
        log: dict[str, Any] = {}
        list_collection = await MGDB.list_collection_names()
        start_time = datetime.now(timezone.utc)
        try:
            log = await InstallHelper.create_indexes(list_collection, log, start_time)

        except Exception as err:
            logger.exception(str(err), err)
            log["error"] = str(err)
        return jsonable_encoder(log)

    @staticmethod
    def collection_has_indexes(indexes: List[SON | Any], index_name: str) -> bool:
        for ind in indexes:
            if not isinstance(ind, SON):
                continue
            if not ind.has_key("name"):
                continue
            ind_name = ind.get("name")
            if ind_name == index_name:
                return True
        return False

    @staticmethod
    async def do_create_index(m: MongoIndexInit, list_collection: List[str], log: dict[str, Any], start_time: datetime) -> dict[str, Any]:
        sub_log: dict[str, Any] = {}
        if not m.collName in list_collection:
            await MGDB.create_collection(m.collName)
            sub_log[m.collName + "_collection"] = "created"
        else:
            sub_log[m.collName + "_collection"] = "already exists"

        indexes_cursor = m.coll.list_indexes()
        indexes: List[Any] = await indexes_cursor.to_list(None) # type: ignore
        for idx in m.indexes:
            index_name = idx.index_name
            if not InstallHelper.collection_has_indexes(indexes, index_name):
                await m.coll.create_index(
                    [(i.field, i.sort) for i in idx.keys],
                    name=index_name,
                    **idx.kwargs
                )
                sub_log[m.collName + "_" + index_name] = "created"
            else:
                sub_log[m.collName + "_" + index_name] = "already exists"

        return sub_log

    @staticmethod
    async def create_indexes(list_collection: List[str], log: dict[str, Any], start_time: datetime) -> dict[str, Any]:
        for index_init in ListMongoIndexInit:
            ret_index = await InstallHelper.do_create_index(index_init, list_collection, log, start_time)
            log["setup_" + index_init.collName] = ret_index
        return log