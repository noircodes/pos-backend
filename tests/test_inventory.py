import pytest
from utils.models.model_data_type import ObjectId
from db.mongo import get_database


@pytest.mark.anyio
async def test_adjust_inventory(client):
    # Register user and login
    await client.post("/auth/register", json={"name":"Inv","email":"inv@example.com","username":"inv","password":"secret","role":"admin"})
    r = await client.post("/auth/login", json={"username":"inv","password":"secret"})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    store_id = str(ObjectId())
    product_id = str(ObjectId())

    # Increase qty
    r = await client.post(f"/stores/{store_id}/inventory/adjust", json={"product_id": product_id, "delta": "10"}, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"]
    assert float(data["item"]["qty"]) == 10.0

    # Decrease qty
    r = await client.post(f"/stores/{store_id}/inventory/adjust", json={"product_id": product_id, "delta": "-3"}, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert float(data["item"]["qty"]) == 7.0

    # Over-decrement should fail
    r = await client.post(f"/stores/{store_id}/inventory/adjust", json={"product_id": product_id, "delta": "-20"}, headers=headers)
    assert r.status_code == 400


@pytest.mark.anyio
async def test_inventory_persistence(client):
    # Ensure index existence by creating an item
    # register and login a user to authenticate the request
    await client.post("/auth/register", json={"name":"Inv","email":"inv@example.com","username":"inv","password":"secret","role":"admin"})
    r = await client.post("/auth/login", json={"username":"inv","password":"secret"})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    store_id = str(ObjectId())
    product_id = str(ObjectId())
    await client.post(f"/stores/{store_id}/inventory/adjust", json={"product_id": product_id, "delta": "5"}, headers=headers)
    db = get_database()
    doc = db.get_collection("inventory").find_one({"store_id": ObjectId(store_id), "product_id": ObjectId(product_id)})
    assert doc is not None
