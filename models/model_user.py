from pydantic import Field, ConfigDict

from models.model_audit import AuditData
from utils.models.model_data_type import BaseModel, ObjectId


class UserRequest(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        validate_by_name=True
    )

    name: str = Field(
        default=...,
        title="Name",
        description="Nama user",
        examples=["Ilham, Noir"]
    )
    email: str = Field(
        default=...,
        title="Email",
        description="Email user",
        examples=["noir@gmail.com"]
    )
    password: str = Field(
        default=None,
        title="Password",
        description="Password user",
        examples=["$2a$12$J9WtJAh.TUrJ6YvVGI38W..gb7Bsmfi2wo1vI8Y2nvl7DPOpttGT."]
    )
    username: str = Field(
        default=...,
        title="Username",
        description="Username user",
        examples=["ilham, noir"]
    )
    role: str = Field(
        default=...,
        title="Role",
        description="Role user",
        examples=["admin", "user"]
    )

class UserInDb(UserRequest, AuditData):
    id: ObjectId = Field(
        default=...,
        title="ID",
        description="User ID",
        alias="_id"
    )