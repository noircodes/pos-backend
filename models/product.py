from pydantic import Field
from utils.models.model_data_type import BaseModel, Decimal128, ObjectId
from datetime import datetime


class ProductRequest(BaseModel):
    sku: str = Field(default=..., title="SKU")
    name: str = Field(default=..., title="Name")
    price: Decimal128 = Field(default=...)
    cost: Decimal128 | None = None
    unit: str | None = None


class ProductInDb(ProductRequest):
    id: ObjectId = Field(default=..., alias="_id")
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
