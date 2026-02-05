from datetime import datetime, timezone
from typing import Optional

from db.mongo import get_collection
from models.product import ProductRequest, ProductInDb
from utils.util_sku import SKUGenerator
from repositories.repository_category import RepositoryCategory
from utils.models.model_data_type import ObjectId


class RepositoryProduct:
    @staticmethod
    async def create_product(request: ProductRequest) -> ProductInDb:
        products = get_collection("products")
        
        # Validate category exists
        category = await RepositoryCategory.get_by_id(request.category_id)
        if not category or not category.active:
            raise ValueError("Invalid or inactive category")
        
        # Auto-generate SKU if not provided
        sku = request.sku
        if not sku:
            sku = await SKUGenerator.generate_unique(request.category_id)
        
        # uniqueness check
        if await products.count_documents({"sku": sku}) > 0:
            raise ValueError("SKU already exists")
        
        doc = request.model_dump()
        doc["sku"] = sku
        # Convert category_id to ObjectId for MongoDB
        doc["category_id"] = ObjectId(request.category_id)
        doc["created_at"] = datetime.now(timezone.utc)
        res = await products.insert_one(doc)
        created = await products.find_one({"_id": res.inserted_id})
        # Convert ObjectId back to string for validation
        created["category_id"] = str(created["category_id"])
        return ProductInDb.model_validate(created)
    
    @staticmethod
    async def regenerate_sku(sku: str) -> ProductInDb:
        """Regenerate SKU for a product while keeping other data"""
        products = get_collection("products")
        
        # Find existing product
        existing = await products.find_one({"sku": sku})
        if not existing:
            raise ValueError("Product not found")
        
        # Generate new SKU with same category
        category_id = existing.get("category_id")
        new_sku = await SKUGenerator.generate_unique(category_id)
        
        # Update product with new SKU and timestamp
        await products.update_one(
            {"sku": sku},
            {
                "$set": {
                    "sku": new_sku,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        # Return updated product
        updated = await products.find_one({"sku": new_sku})
        # Convert ObjectId back to string for validation
        updated["category_id"] = str(updated["category_id"])
        return ProductInDb.model_validate(updated)

    @staticmethod
    async def list_products(skip: int = 0, limit: int = 20):
        products = get_collection("products")
        cursor = products.find({}, projection=ProductInDb.Projection()).skip(skip).limit(limit)
        result = []
        async for x in cursor:
            # Convert ObjectId back to string for validation
            x["category_id"] = str(x["category_id"])
            result.append(ProductInDb.model_validate(x))
        return result

    @staticmethod
    async def get_by_sku(sku: str) -> Optional[ProductInDb]:
        products = get_collection("products")
        p = await products.find_one({"sku": sku})
        if not p:
            return None
        # Convert ObjectId back to string for validation
        p["category_id"] = str(p["category_id"])
        return ProductInDb.model_validate(p)
