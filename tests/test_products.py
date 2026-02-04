import pytest
from db.mongo import get_database as MGDB


@pytest.mark.anyio
async def test_create_and_list_products(client):
    # Register and login a user
    r = await client.post("/auth/register", json={
        "name": "Bob",
        "email": "bob@example.com",
        "username": "bob",
        "password": "secret",
        "role": "admin",
    })
    assert r.status_code == 200

    r = await client.post("/auth/login", json={"username": "bob", "password": "secret"})
    assert r.status_code == 200
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Create product
    payload = {"sku": "SKU-001", "name": "Coffee", "price": "2.50", "unit": "cup"}
    r = await client.post("/products/", json=payload, headers=headers)
    assert r.status_code == 200
    p = r.json()
    assert p["sku"] == "SKU-001"

    # Duplicate SKU should return 400
    r2 = await client.post("/products/", json=payload, headers=headers)
    assert r2.status_code == 400

    # List products
    r = await client.get("/products/")
    assert r.status_code == 200
    arr = r.json()
    assert any(x["sku"] == "SKU-001" for x in arr)
