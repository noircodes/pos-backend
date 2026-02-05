import pytest

from models.category import CategoryRequest, CategoryInDb, CategoryCombo


@pytest.mark.anyio
async def test_create_category(client):
    # Register and login first
    payload = {
        "name": "Alice",
        "email": "alice@example.com",
        "username": "alice",
        "password": "secret",
        "role": "admin",
    }
    r = await client.post("/auth/register", json=payload)
    assert r.status_code == 200

    # Login
    r = await client.post("/auth/login", data={"username": "alice", "password": "secret"})
    assert r.status_code == 200
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Create category
    category_data = {
        "name": "food",
        "display_name": "Food",
        "sku_prefix": "FOD",
        "description": "Food items"
    }
    r = await client.post("/categories/", json=category_data, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    assert data["name"] == "food"
    assert data["display_name"] == "Food"
    assert data["sku_prefix"] == "FOD"
    assert data["active"] is True
    assert data["description"] == "Food items"


@pytest.mark.anyio
async def test_create_duplicate_category(client):
    # Register and login
    payload = {
        "name": "Bob",
        "email": "bob@example.com",
        "username": "bob",
        "password": "secret",
    }
    await client.post("/auth/register", json=payload)
    r = await client.post("/auth/login", data={"username": "bob", "password": "secret"})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Create category
    category_data = {
        "name": "beverage",
        "display_name": "Beverage",
        "sku_prefix": "BEV"
    }
    r = await client.post("/categories/", json=category_data, headers=headers)
    assert r.status_code == 200

    # Try to create duplicate
    r = await client.post("/categories/", json=category_data, headers=headers)
    assert r.status_code == 400
    assert "already exists" in r.json()["detail"]


@pytest.mark.anyio
async def test_create_category_without_auth(client):
    # Try to create category without authentication
    category_data = {
        "name": "electronics",
        "display_name": "Electronics",
        "sku_prefix": "ELEC"
    }
    r = await client.post("/categories/", json=category_data)
    assert r.status_code == 401  # Unauthorized


@pytest.mark.anyio
async def test_get_categories_combo(client):
    # Register, login, and create categories
    payload = {
        "name": "Charlie",
        "email": "charlie@example.com",
        "username": "charlie",
        "password": "secret",
    }
    await client.post("/auth/register", json=payload)
    r = await client.post("/auth/login", data={"username": "charlie", "password": "secret"})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Create multiple categories
    categories = [
        {"name": "food", "display_name": "Food", "sku_prefix": "FOD"},
        {"name": "beverage", "display_name": "Beverage", "sku_prefix": "BEV"},
        {"name": "clothing", "display_name": "Clothing", "sku_prefix": "CLO"},
    ]
    for cat in categories:
        await client.post("/categories/", json=cat, headers=headers)

    # Get combo list
    r = await client.get("/categories/combo", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 3
    assert all("id" in item for item in data)
    assert all("name" in item for item in data)
    assert all("display_name" in item for item in data)
    # Should be sorted by display_name
    display_names = [item["display_name"] for item in data]
    assert display_names == sorted(display_names)


@pytest.mark.anyio
async def test_get_category_by_id(client):
    # Register and login
    payload = {
        "name": "David",
        "email": "david@example.com",
        "username": "david",
        "password": "secret",
    }
    await client.post("/auth/register", json=payload)
    r = await client.post("/auth/login", data={"username": "david", "password": "secret"})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Create category
    category_data = {
        "name": "accessories",
        "display_name": "Accessories",
        "sku_prefix": "ACC"
    }
    r = await client.post("/categories/", json=category_data, headers=headers)
    category_id = r.json()["id"]

    # Get category by ID
    r = await client.get(f"/categories/{category_id}", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == category_id
    assert data["name"] == "accessories"
    assert data["display_name"] == "Accessories"
    assert data["sku_prefix"] == "ACC"


@pytest.mark.anyio
async def test_update_category(client):
    # Register and login
    payload = {
        "name": "Eve",
        "email": "eve@example.com",
        "username": "eve",
        "password": "secret",
    }
    await client.post("/auth/register", json=payload)
    r = await client.post("/auth/login", data={"username": "eve", "password": "secret"})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Create category
    category_data = {
        "name": "stationery",
        "display_name": "Stationery",
        "sku_prefix": "STN"
    }
    r = await client.post("/categories/", json=category_data, headers=headers)
    category_id = r.json()["id"]

    # Update category
    update_data = {
        "name": "stationery",
        "display_name": "Stationery Items",
        "sku_prefix": "STAT",
        "description": "Updated description"
    }
    r = await client.put(f"/categories/{category_id}", json=update_data, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["display_name"] == "Stationery Items"
    assert data["sku_prefix"] == "STAT"
    assert data["description"] == "Updated description"


@pytest.mark.anyio
async def test_delete_category(client):
    # Register and login
    payload = {
        "name": "Frank",
        "email": "frank@example.com",
        "username": "frank",
        "password": "secret",
    }
    await client.post("/auth/register", json=payload)
    r = await client.post("/auth/login", data={"username": "frank", "password": "secret"})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Create category
    category_data = {
        "name": "toys",
        "display_name": "Toys",
        "sku_prefix": "TOY"
    }
    r = await client.post("/categories/", json=category_data, headers=headers)
    category_id = r.json()["id"]

    # Delete category
    r = await client.delete(f"/categories/{category_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["message"] == "Category deleted successfully"

    # Verify it's soft deleted (active=False)
    r = await client.get(f"/categories/{category_id}", headers=headers)
    # Should still exist but be inactive
    assert r.status_code == 200
    assert r.json()["active"] is False

    # Should not appear in combo list (active_only=True is default)
    r = await client.get("/categories/combo", headers=headers)
    assert r.status_code == 200
    category_ids = [item["id"] for item in r.json()]
    assert category_id not in category_ids


@pytest.mark.anyio
async def test_delete_category_with_products(client):
    # Register and login
    payload = {
        "name": "Grace",
        "email": "grace@example.com",
        "username": "grace",
        "password": "secret",
    }
    await client.post("/auth/register", json=payload)
    r = await client.post("/auth/login", data={"username": "grace", "password": "secret"})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Create category
    category_data = {
        "name": "books",
        "display_name": "Books",
        "sku_prefix": "BOK"
    }
    r = await client.post("/categories/", json=category_data, headers=headers)
    category_id = r.json()["id"]

    # Create product in this category
    product_data = {
        "name": "Python Book",
        "price": "50.00",
        "category_id": category_id
    }
    r = await client.post("/products/", json=product_data, headers=headers)
    assert r.status_code == 200

    # Try to delete category - should fail
    r = await client.delete(f"/categories/{category_id}", headers=headers)
    assert r.status_code == 400
    assert "Cannot delete category" in r.json()["detail"]
    assert "product(s) reference this category" in r.json()["detail"]


@pytest.mark.anyio
async def test_invalid_prefix_length(client):
    # Register and login
    payload = {
        "name": "Henry",
        "email": "henry@example.com",
        "username": "henry",
        "password": "secret",
    }
    await client.post("/auth/register", json=payload)
    r = await client.post("/auth/login", data={"username": "henry", "password": "secret"})
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Try to create category with prefix > 10 characters
    category_data = {
        "name": "invalid",
        "display_name": "Invalid",
        "sku_prefix": "TOOLONGPREFIX"
    }
    r = await client.post("/categories/", json=category_data, headers=headers)
    assert r.status_code == 400
    assert "must not exceed 10 characters" in r.json()["detail"]