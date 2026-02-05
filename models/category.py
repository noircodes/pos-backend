from pydantic import Field, ConfigDict
from utils.models.model_data_type import BaseModel, ObjectId
from datetime import datetime


class CategoryRequest(BaseModel):
    name: str = Field(default=..., title="Category Name (unique identifier)")
    display_name: str = Field(default=..., title="Display Name (for UI)")
    sku_prefix: str = Field(default=..., title="SKU Prefix (max 10 characters)")
    description: str | None = Field(default=None, title="Description")


class CategoryInDb(CategoryRequest):
    id: ObjectId = Field(default=..., alias="_id", serialization_alias="id")
    active: bool = Field(default=True, title="Active Status")
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        use_attribute_docstrings=True,
        by_alias=False
    )


class CategoryCombo(BaseModel):
    """Lightweight model for dropdown/combo boxes"""
    id: str
    name: str
    display_name: str
