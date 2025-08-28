from datetime import datetime

from pydantic import Field

from utils.models.model_data_type import BaseModel, ObjectId


class AuditData(BaseModel):
    is_deleted: bool = Field(
        default=False,
        description="Is this data deleted?",
        alias="isDeleted"
    )
    created_at: datetime = Field(
        default=datetime.now(),
        description="When the data was created",
        alias="createdAt"
    )
    created_by: ObjectId = Field(
        default=ObjectId(),
        alias="createdBy"
    )
    updated_at: datetime | None = Field(
        default=None,
        description="When the data was updated",
    )
    updated_by: ObjectId | None = Field(
        default=None,
        alias="updatedBy"
    )
    deleted_at: datetime | None = Field(
        default=None,
        description="When the data was deleted",
        alias="deletedAt"
    )
    deleted_by: ObjectId | None = Field(
        default=None,
        alias="deletedBy"
    )
