import random
import string
from datetime import datetime
from typing import Optional

from db.mongo import get_collection
from utils.models.model_data_type import ObjectId


class SKUGenerator:
    """SKU Generator with configurable category prefixes from database"""
    
    DEFAULT_PREFIX = "PRD"
    
    @staticmethod
    async def get_prefix(category_id: Optional[str] = None) -> str:
        """
        Get SKU prefix for a category from database
        Returns default prefix if category not found or invalid
        """
        if not category_id:
            return SKUGenerator.DEFAULT_PREFIX
        
        try:
            categories = get_collection("categories")
            category = await categories.find_one({"_id": ObjectId(category_id), "active": True})
            
            if category and "sku_prefix" in category:
                return category["sku_prefix"]
            
            return SKUGenerator.DEFAULT_PREFIX
        except:
            return SKUGenerator.DEFAULT_PREFIX
    
    @staticmethod
    def generate_random_code(length: int = 8) -> str:
        """Generate random alphanumeric code"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choices(characters, k=length))
    
    @staticmethod
    async def generate(category_id: Optional[str] = None) -> str:
        """
        Generate SKU with format: PREFIX-TIMESTAMP-CODE
        Example: FOD-20250205-A3B7
        """
        prefix = await SKUGenerator.get_prefix(category_id)
        timestamp = datetime.now().strftime("%Y%m%d")
        random_code = SKUGenerator.generate_random_code(4)
        return f"{prefix}-{timestamp}-{random_code}"
    
    @staticmethod
    async def generate_unique(category_id: Optional[str] = None) -> str:
        """
        Generate a unique SKU, checking for duplicates
        Will regenerate if SKU already exists
        """
        products = get_collection("products")
        max_attempts = 10
        attempts = 0
        
        while attempts < max_attempts:
            sku = await SKUGenerator.generate(category_id)
            existing = await products.find_one({"sku": sku})
            if not existing:
                return sku
            attempts += 1
        
        # Fallback: append timestamp with milliseconds
        timestamp_ms = datetime.now().strftime("%Y%m%d%H%M%S%f")[:17]
        prefix = await SKUGenerator.get_prefix(category_id)
        return f"{prefix}-{timestamp_ms}"
