from models.model_user import UserRequest, UserInDb
from utils.models.model_data_type import ObjectId
from datetime import datetime


class RepositoryUser:
    @staticmethod
    async def create_user(
            request: UserRequest,
            created_by: ObjectId,
    ):
        create_param = UserInDb.model_construct(request.model_fields_set, **request.model_dump())
        create_param.created_by = created_by
        create_param.created_at = datetime.now()
        