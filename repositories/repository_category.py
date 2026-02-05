from datetime import datetime, timezone
from typing import Optional, List

from db.mongo import get_collection
from models.category import CategoryRequest, CategoryInDb, CategoryCombo
from utils.models.model_data_type import ObjectId


class RepositoryCategory:
    @staticmethod
    async def create_category(request: CategoryRequest) -> CategoryInDb:
        categories = get_collection("categories")
        
        # Check for unique name
        existing = await categories.find_one({"name": request.name.lower()})
        if existing:
            raise ValueError(f"Category with name '{request.name}' already exists")
        
        # Validate prefix length
        if len(request.sku_prefix) > 10:
            raise ValueError("SKU prefix must not exceed 10 characters")
        
        # Uppercase the prefix
        request_dict = request.model_dump()
        request_dict["name"] = request.name.lower()
        request_dict["sku_prefix"] = request.sku_prefix.upper()
        request_dict["active"] = True
        request_dict["created_at"] = datetime.now(timezone.utc)
        request_dict["updated_at"] = datetime.now(timezone.utc)
        
        res = await categories.insert_one(request_dict)
        created = await categories.find_one({"_id": res.inserted_id})
        return CategoryInDb.model_validate(created)
    
    @staticmethod
    async def list_categories(skip: int = 0, limit: int = 100, active_only: bool = False) -> List[CategoryInDb]:
        categories = get_collection("categories")
        query = {"active": True} if active_only else {}
        cursor = categories.find(query, projection=CategoryInDb.Projection()).skip(skip).limit(limit)
        return [CategoryInDb.model_validate(x) async for x in cursor]
    
    @staticmethod
    async def get_combo_list(active_only: bool = True) -> List[CategoryCombo]:
        """
        Get lightweight category list for dropdowns
        Returns only id, name, and display_name
        """
        categories = get_collection("categories")
        query = {"active": True} if active_only else {}
        
        cursor = categories.find(
            query,
            projection={"_id": 1, "name": 1, "display_name": 1}
        ).sort("display_name", 1)
        
        result = []
        async for cat in cursor:
            result.append(CategoryCombo(
                id=str(cat["_id"]),
                name=cat["name"],
                display_name=cat["display_name"]
            ))
        return result
    
    @staticmethod
    async def get_by_id(category_id: str) -> Optional[CategoryInDb]:
        categories = get_collection("categories")
        try:
            oid = ObjectId(category_id)
        except:
            return None
        
        cat = await categories.find_one({"_id": oid})
        if not cat:
            return None
        return CategoryInDb.model_validate(cat)
    
    @staticmethod
    async def get_by_name(name: str) -> Optional[CategoryInDb]:
        categories = get_collection("categories")
        cat = await categories.find_one({"name": name.lower()})
        if not cat:
            return None
        return CategoryInDb.model_validate(cat)
    
    @staticmethod
    async def update_category(category_id: str, request: CategoryRequest) -> CategoryInDb:
        categories = get_collection("categories")
        
        try:
            oid = ObjectId(category_id)
        except:
            raise ValueError("Invalid category ID")
        
        # Check if exists
        existing = await categories.find_one({"_id": oid})
        if not existing:
            raise ValueError("Category not found")
        
        # Check for duplicate name (excluding current category)
        name_check = await categories.find_one({
            "name": request.name.lower(),
            "_id": {"$ne": oid}
        })
        if name_check:
            raise ValueError(f"Category with name '{request.name}' already exists")
        
        # Validate prefix length
        if len(request.sku_prefix) > 10:
            raise ValueError("SKU prefix must not exceed 10 characters")
        
        # Update
        update_dict = request.model_dump()
        update_dict["name"] = request.name.lower()
        update_dict["sku_prefix"] = request.sku_prefix.upper()
        update_dict["updated_at"] = datetime.now(timezone.utc)
        
        await categories.update_one({"_id": oid}, {"$set": update_dict})
        updated = await categories.find_one({"_id": oid})
        return CategoryInDb.model_validate(updated)
    
    @staticmethod
    async def delete_category(category_id: str) -> bool:
        """
        Soft delete a category by setting active to false
        Checks if category is used by any products first
        """
        categories = get_collection("categories")
        products = get_collection("products")
        
        try:
            oid = ObjectId(category_id)
        except:
            raise ValueError("Invalid category ID")
        
        # Check if exists
        existing = await categories.find_one({"_id": oid})
        if not existing:
            raise ValueError("Category not found")
        
        # Check if used by any products
        product_count = await products.count_documents({"category_id": oid})
        if product_count > 0:
            raise ValueError(f"Cannot delete category: {product_count} product(s) reference this category")
        
        # Soft delete
        result = await categories.update_one(
            {"_id": oid},
            {"$set": {"active": False, "updated_at": datetime.now(timezone.utc)}}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    async def get_sku_prefix(category_id: str) -> Optional[str]:
        """
        Get SKU prefix for a category by ID
        Returns None if category not found
        """
        category = await RepositoryCategory.get_by_id(category_id)
        if not category or not category.active:
            return None
        return category.sku_prefix