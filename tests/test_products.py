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

    r = await client.post("/auth/login", data={"username": "bob", "password": "secret"})
    assert r.status_code == 200
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Create category first
    category_data = {
        "name": "beverage",
        "display_name": "Beverage",
        "sku_prefix": "BEV"
    }
    r = await client.post("/categories/", json=category_data, headers=headers)
    assert r.status_code == 200
    category_id = r.json()["id"]

    # Create product with custom SKU
    payload = {"sku": "SKU-001", "name": "Coffee", "price": "2.50", "unit": "cup", "category_id": category_id}
    r = await client.post("/products/", json=payload, headers=headers)
    assert r.status_code == 200
    p = r.json()
    assert p["sku"] == "SKU-001"
    assert p["category_id"] == category_id

    # Duplicate SKU should return 400
    r2 = await client.post("/products/", json=payload, headers=headers)
    assert r2.status_code == 400

    # List products
    r = await client.get("/products/")
    assert r.status_code == 200
    arr = r.json()
    assert any(x["sku"] == "SKU-001" for x in arr)


@pytest.mark.anyio
async def test_create_product_with_auto_sku(client):
    # Register and login
    r = await client.post("/auth/register", json={
        "name": "Alice",
        "email": "alice@example.com",
        "username": "alice",
        "password": "secret",
    })
    assert r.status_code == 200
    r = await client.post("/auth/login", data={"username": "alice", "password": "secret"})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Create category
    category_data = {
        "name": "food",
        "display_name": "Food",
        "sku_prefix": "FOD"
    }
    r = await client.post("/categories/", json=category_data, headers=headers)
    category_id = r.json()["id"]

    # Create product without SKU (auto-generated)
    payload = {"name": "Burger", "price": "15.00", "category_id": category_id}
    r = await client.post("/products/", json=payload, headers=headers)
    assert r.status_code == 200
    p = r.json()
    assert "sku" in p
    assert p["sku"].startswith("FOD-")  # Should start with category prefix
    assert p["category_id"] == category_id


@pytest.mark.anyio
async def test_create_product_invalid_category(client):
    # Register and login
    r = await client.post("/auth/register", json={
        "name": "Charlie",
        "email": "charlie@example.com",
        "username": "charlie",
        "password": "secret",
    })
    assert r.status_code == 200
    r = await client.post("/auth/login", data={"username": "charlie", "password": "secret"})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Try to create product with invalid category_id
    payload = {"name": "Invalid Product", "price": "10.00", "category_id": "507f1f77bcf86cd799439011"}
    r = await client.post("/products/", json=payload, headers=headers)
    assert r.status_code == 400
    assert "Invalid or inactive category" in r.json()["detail"]


@pytest.mark.anyio
async def test_regenerate_sku(client):
    # Register and login
    r = await client.post("/auth/register", json={
        "name": "David",
        "email": "david@example.com",
        "username": "david",
        "password": "secret",
    })
    assert r.status_code == 200
    r = await client.post("/auth/login", data={"username": "david", "password": "secret"})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Create category
    category_data = {
        "name": "electronics",
        "display_name": "Electronics",
        "sku_prefix": "ELEC"
    }
    r = await client.post("/categories/", json=category_data, headers=headers)
    category_id = r.json()["id"]

    # Create product
    payload = {"name": "Phone", "price": "500.00", "category_id": category_id}
    r = await client.post("/products/", json=payload, headers=headers)
    assert r.status_code == 200
    original_sku = r.json()["sku"]

    # Regenerate SKU
    r = await client.post(f"/products/{original_sku}/regenerate-sku", headers=headers)
    assert r.status_code == 200
    new_sku = r.json()["sku"]
    assert new_sku != original_sku
    assert new_sku.startswith("ELEC-")  # Should still have same prefix
