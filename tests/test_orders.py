import pytest
from utils.models.model_data_type import ObjectId
from db.mongo import get_database


@pytest.mark.anyio
async def test_create_order_idempotency(client):
    # Register user and login
    await client.post("/auth/register", json={"name":"Ord","email":"ord@example.com","username":"ord","password":"secret","role":"admin"})
    r = await client.post("/auth/login", data={"username":"ord","password":"secret"})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    store_id = str(ObjectId())
    product_id = str(ObjectId())

    # Seed inventory
    await client.post(f"/stores/{store_id}/inventory/adjust", json={"product_id": product_id, "delta": "5"}, headers=headers)

    payload = {
        "store_id": store_id,
        "user_id": str(ObjectId()),
        "items": [{"product_id": product_id, "qty": "2", "price": "3.50"}]
    }

    id_key = "idem-123"

    r1 = await client.post("/orders/", json=payload, headers={**headers, "Idempotency-Key": id_key})
    assert r1.status_code == 200
    o1 = r1.json()["order"]

    r2 = await client.post("/orders/", json=payload, headers={**headers, "Idempotency-Key": id_key})
    assert r2.status_code == 200
    o2 = r2.json()["order"]

    assert o1["id"] == o2["id"]

    # Inventory should have decreased by 2
    db = get_database()
    doc = db.get_collection("inventory").find_one({"store_id": ObjectId(store_id), "product_id": ObjectId(product_id)})
    # qty stored as BSON Decimal128; convert to Decimal then to float for assertion
    qty = doc["qty"]
    try:
        qty_val = qty.to_decimal()
    except Exception:
        from decimal import Decimal
        qty_val = Decimal(str(qty))
    assert float(qty_val) == 3.0


@pytest.mark.anyio
async def test_get_order_by_id(client):
    # Register user and login
    await client.post("/auth/register", json={"name":"Test","email":"test@example.com","username":"testuser","password":"secret","role":"admin"})
    r = await client.post("/auth/login", data={"username":"testuser","password":"secret"})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    store_id = str(ObjectId())
    product_id = str(ObjectId())

    # Seed inventory
    await client.post(f"/stores/{store_id}/inventory/adjust", json={"product_id": product_id, "delta": "10"}, headers=headers)

    # Create order
    payload = {
        "store_id": store_id,
        "user_id": str(ObjectId()),
        "items": [{"product_id": product_id, "qty": "3", "price": "5.00"}]
    }
    r = await client.post("/orders/", json=payload, headers=headers)
    assert r.status_code == 200
    order = r.json()["order"]
    order_id = order["id"]

    # Get order by ID
    r = await client.get(f"/orders/{order_id}", headers=headers)
    assert r.status_code == 200
    retrieved_order = r.json()
    assert retrieved_order["id"] == order_id
    assert retrieved_order["status"] == "created"


@pytest.mark.anyio
async def test_list_orders(client):
    # Register user and login
    await client.post("/auth/register", json={"name":"List","email":"list@example.com","username":"listuser","password":"secret","role":"admin"})
    r = await client.post("/auth/login", data={"username":"listuser","password":"secret"})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    store_id = str(ObjectId())
    product_id = str(ObjectId())

    # Seed inventory
    await client.post(f"/stores/{store_id}/inventory/adjust", json={"product_id": product_id, "delta": "20"}, headers=headers)

    user_id = str(ObjectId())

    # Create multiple orders
    for i in range(3):
        payload = {
            "store_id": store_id,
            "user_id": user_id,
            "items": [{"product_id": product_id, "qty": str(i + 1), "price": "2.00"}]
        }
        await client.post("/orders/", json=payload, headers=headers)

    # List all orders
    r = await client.get("/orders/", headers=headers)
    assert r.status_code == 200
    orders = r.json()
    assert len(orders) == 3

    # List orders filtered by store_id
    r = await client.get(f"/orders/?store_id={store_id}", headers=headers)
    assert r.status_code == 200
    orders = r.json()
    assert len(orders) == 3

    # List orders filtered by user_id
    r = await client.get(f"/orders/?user_id={user_id}", headers=headers)
    assert r.status_code == 200
    orders = r.json()
    assert len(orders) == 3

    # Test pagination
    r = await client.get("/orders/?skip=0&limit=2", headers=headers)
    assert r.status_code == 200
    orders = r.json()
    assert len(orders) == 2


@pytest.mark.anyio
async def test_update_order_status(client):
    # Register user and login
    await client.post("/auth/register", json={"name":"Status","email":"status@example.com","username":"statususer","password":"secret","role":"admin"})
    r = await client.post("/auth/login", data={"username":"statususer","password":"secret"})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    store_id = str(ObjectId())
    product_id = str(ObjectId())

    # Seed inventory
    await client.post(f"/stores/{store_id}/inventory/adjust", json={"product_id": product_id, "delta": "10"}, headers=headers)

    # Create order
    payload = {
        "store_id": store_id,
        "user_id": str(ObjectId()),
        "items": [{"product_id": product_id, "qty": "2", "price": "3.00"}]
    }
    r = await client.post("/orders/", json=payload, headers=headers)
    assert r.status_code == 200
    order = r.json()["order"]
    order_id = order["id"]

    # Update status to confirmed
    r = await client.patch(f"/orders/{order_id}/status", json={"status": "confirmed"}, headers=headers)
    assert r.status_code == 200
    updated_order = r.json()["order"]
    assert updated_order["status"] == "confirmed"

    # Update status to completed
    r = await client.patch(f"/orders/{order_id}/status", json={"status": "completed"}, headers=headers)
    assert r.status_code == 200
    updated_order = r.json()["order"]
    assert updated_order["status"] == "completed"

    # Test invalid status
    r = await client.patch(f"/orders/{order_id}/status", json={"status": "invalid"}, headers=headers)
    assert r.status_code == 400


@pytest.mark.anyio
async def test_update_status_flow(client):
    # Test typical order status flow: created -> confirmed -> preparing -> ready -> completed
    await client.post("/auth/register", json={"name":"Flow","email":"flow@example.com","username":"flowuser","password":"secret","role":"admin"})
    r = await client.post("/auth/login", data={"username":"flowuser","password":"secret"})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    store_id = str(ObjectId())
    product_id = str(ObjectId())

    await client.post(f"/stores/{store_id}/inventory/adjust", json={"product_id": product_id, "delta": "10"}, headers=headers)

    payload = {
        "store_id": store_id,
        "user_id": str(ObjectId()),
        "items": [{"product_id": product_id, "qty": "1", "price": "10.00"}]
    }
    r = await client.post("/orders/", json=payload, headers=headers)
    order = r.json()["order"]
    order_id = order["id"]

    statuses = ["confirmed", "preparing", "ready", "completed"]
    for status in statuses:
        r = await client.patch(f"/orders/{order_id}/status", json={"status": status}, headers=headers)
        assert r.status_code == 200
        assert r.json()["order"]["status"] == status

    # Test cancellation
    store_id2 = str(ObjectId())
    await client.post(f"/stores/{store_id2}/inventory/adjust", json={"product_id": product_id, "delta": "10"}, headers=headers)
    payload2 = {
        "store_id": store_id2,
        "user_id": str(ObjectId()),
        "items": [{"product_id": product_id, "qty": "1", "price": "10.00"}]
    }
    r = await client.post("/orders/", json=payload2, headers=headers)
    order_id2 = r.json()["order"]["id"]
    
    r = await client.patch(f"/orders/{order_id2}/status", json={"status": "cancelled"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["order"]["status"] == "cancelled"
