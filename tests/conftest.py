import os

# Ensure test DB/env is set before importing app modules
os.environ.setdefault("MONGO_DB", "pos_test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")

import pytest
from httpx import AsyncClient, ASGITransport
from pymongo import MongoClient

import main as app_main
from core.config import settings


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    transport = ASGITransport(app=app_main.app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
async def clear_db():
    # Use sync MongoClient for test housekeeping to avoid motor event loop issues
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB]
    coll_names = db.list_collection_names()
    for c in coll_names:
        db.get_collection(c).delete_many({})
    yield
    # Cleanup after test
    coll_names = db.list_collection_names()
    for c in coll_names:
        db.get_collection(c).delete_many({})
