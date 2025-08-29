from enum import Enum
from typing import Any, Mapping
import pymongo


class MongoIndexKey:
    def __init__(self, field: str, sort: int | str | Mapping[str, Any]) -> None:
        self.field = field
        self.sort = sort

class MongoIndex:
    def __init__(self, index_name: str, keys: list[MongoIndexKey], **kwargs: Any) -> None:
        self.index_name = index_name
        self.keys = keys
        self.kwargs = kwargs

class IndexUser(Enum):
    isDeleted_name = MongoIndex(
        "index_isDeleted_name",
        [
            MongoIndexKey("isDeleted", pymongo.ASCENDING),
            MongoIndexKey("name", pymongo.ASCENDING)
        ]
    )
    isDeleted_username = MongoIndex(
        "index_isDeleted_username",
        [
            MongoIndexKey("isDeleted", pymongo.ASCENDING),
            MongoIndexKey("username", pymongo.ASCENDING)
        ]
    )
    isDeleted_email = MongoIndex(
        "index_isDeleted_email",
        [
            MongoIndexKey("isDeleted", pymongo.ASCENDING),
            MongoIndexKey("email", pymongo.ASCENDING)
        ]
    )