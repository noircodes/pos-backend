from enum import Enum
from utils.models.model_data_type import BaseModel, ObjectId

class TokenData(BaseModel):
    userId: ObjectId = None
    username: str = None
    name: str = None
    role: str = None
    authToken: str = None
    exp: int = None
    course_ids: list[ObjectId] = None