from datetime import datetime, timezone
from typing import Optional

from db.mongo import get_collection
from models.product import ProductRequest, ProductInDb


class RepositoryProduct:
    @staticmethod
    async def create_product(request: ProductRequest) -> ProductInDb:
        products = get_collection("products")
        # uniqueness check
        if await products.count_documents({"sku": request.sku}) > 0:
            raise ValueError("SKU already exists")
        doc = request.model_dump()
        doc["created_at"] = datetime.now(timezone.utc)
        res = await products.insert_one(doc)
        created = await products.find_one({"_id": res.inserted_id})
        return ProductInDb.model_validate(created)

    @staticmethod
    async def list_products(skip: int = 0, limit: int = 20):
        products = get_collection("products")
        cursor = products.find({}, projection=ProductInDb.Projection()).skip(skip).limit(limit)
        return [ProductInDb.model_validate(x) async for x in cursor]

    @staticmethod
    async def get_by_sku(sku: str) -> Optional[ProductInDb]:
        products = get_collection("products")
        p = await products.find_one({"sku": sku})
        if not p:
            return None
        return ProductInDb.model_validate(p)
