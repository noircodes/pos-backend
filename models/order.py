from pydantic import Field, ConfigDict
from utils.models.model_data_type import BaseModel, Decimal128, ObjectId
from datetime import datetime
from typing import List


class OrderLine(BaseModel):
    product_id: ObjectId
    qty: Decimal128
    price: Decimal128


class OrderRequest(BaseModel):
    store_id: ObjectId
    user_id: ObjectId
    items: List[OrderLine]
    idempotency_key: str | None = None


class OrderInDb(OrderRequest):
    model_config = ConfigDict(populate_by_name=True)
    
    id: ObjectId = Field(default=..., serialization_alias="id", alias="_id")
    subtotal: Decimal128 | None = None
    tax: Decimal128 | None = None
    total: Decimal128 | None = None
    status: str = Field(default="created")
    created_at: datetime | None = None
    updated_at: datetime | None = None
