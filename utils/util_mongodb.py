from typing import TYPE_CHECKING, Any

from pymongo import AsyncMongoClient
from pymongo.asynchronous.change_stream import AsyncChangeStream
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.cursor import AsyncCursor
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.command_cursor import AsyncCommandCursor
from pymongo.asynchronous.encryption import AsyncClientEncryption

if TYPE_CHECKING:
    TMongoClient = AsyncMongoClient[dict[str, Any]]
    TMongoClientSession = AsyncClientSession
    TMongoDatabase = AsyncDatabase[dict[str, Any]]
    TMongoCollection = AsyncCollection[dict[str, Any]]
    TMongoCursor = AsyncCursor[dict[str, Any]]
    TMongoCommandCursor = AsyncCommandCursor[dict[str, Any]]
    TMongoChangeStream = AsyncChangeStream[dict[str, Any]]
    TMongoClientEncryption = AsyncClientEncryption[dict[str, Any]]
else:
    TMongoClient = AsyncMongoClient
    TMongoClientSession = AsyncClientSession
    TMongoDatabase = AsyncDatabase
    TMongoCollection = AsyncCollection
    TMongoCursor = AsyncCursor
    TMongoCommandCursor = AsyncCommandCursor
    TMongoChangeStream = AsyncChangeStream
    TMongoClientEncryption = AsyncClientEncryption