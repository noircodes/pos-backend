import pytest

from db.mongo import get_database as MGDB


@pytest.mark.anyio
async def test_register_login_and_me(client):
    # Register
    payload = {
        "name": "Alice",
        "email": "alice@example.com",
        "username": "alice",
        "password": "secret",
        "role": "admin",
    }
    r = await client.post("/auth/register", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "id" in data

    # Login
    r = await client.post("/auth/login", json={"username": "alice", "password": "secret"})
    assert r.status_code == 200
    token = r.json().get("access_token")
    assert token

    # Get current user
    headers = {"Authorization": f"Bearer {token}"}
    r = await client.get("/users/me", headers=headers)
    assert r.status_code == 200
    me = r.json()
    assert me["username"] == "alice"

    # Password should be hashed in DB
    # Check DB directly using sync client to avoid motor loop issues
    from pymongo import MongoClient
    from core.config import settings
    client = MongoClient(settings.MONGO_URI)
    udoc = client[settings.MONGO_DB].get_collection("users").find_one({"username": "alice"})
    assert udoc
    assert udoc.get("password") != "secret"
    assert udoc.get("password").startswith("$2")
