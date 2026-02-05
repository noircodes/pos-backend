from pydantic import Field
from utils.models.model_data_type import BaseModel, Decimal128, ObjectId
from datetime import datetime


class ProductRequest(BaseModel):
    sku: str | None = Field(default=None, title="SKU - Auto-generated if not provided")
    name: str = Field(default=..., title="Name")
    price: Decimal128 = Field(default=...)
    cost: Decimal128 | None = None
    unit: str | None = None
    category_id: str = Field(default=..., title="Category ID - Required field")


class ProductInDb(ProductRequest):
    id: ObjectId = Field(default=..., alias="_id")
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
