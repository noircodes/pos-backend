from pydantic import Field
from utils.models.model_data_type import BaseModel, Decimal128, ObjectId
from datetime import datetime


class InventoryItem(BaseModel):
    store_id: ObjectId = Field(default=..., title="Store ID")
    product_id: ObjectId = Field(default=..., title="Product ID")
    qty: Decimal128 = Field(default=...)
    reserved_qty: Decimal128 = Field(default=0)
    version: int = Field(default=1)
    updated_at: datetime | None = None
    created_at: datetime | None = None
