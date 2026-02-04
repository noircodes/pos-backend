from datetime import datetime, timezone
from typing import Optional

from utils.models.model_data_type import ObjectId
from db.mongo import get_collection
from models.model_user import UserRequest, UserInDb
from core.security import hash_password


class RepositoryUser:
    @staticmethod
    async def create_user(
            request: UserRequest,
            created_by: ObjectId | None = None,
    ) -> UserInDb:
        users = get_collection("users")
        # uniqueness checks
        if await users.count_documents({"username": request.username}) > 0:
            raise ValueError("Username already exists")
        if await users.count_documents({"email": request.email}) > 0:
            raise ValueError("Email already exists")

        doc = request.model_dump()
        if doc.get("password"):
            doc["password"] = hash_password(doc["password"])
        doc["created_at"] = datetime.now(timezone.utc)
        doc["created_by"] = created_by
        res = await users.insert_one(doc)
        created = await users.find_one({"_id": res.inserted_id})
        return UserInDb.model_validate(created)

    @staticmethod
    async def get_by_username(username: str) -> Optional[UserInDb]:
        users = get_collection("users")
        u = await users.find_one({"username": username})
        if not u:
            return None
        return UserInDb.model_validate(u)

    @staticmethod
    async def get_by_email(email: str) -> Optional[UserInDb]:
        users = get_collection("users")
        u = await users.find_one({"email": email})
        if not u:
            return None
        return UserInDb.model_validate(u)

    @staticmethod
    async def get_by_id(uid: ObjectId | str) -> Optional[UserInDb]:
        users = get_collection("users")
        # Accept ObjectId or string
        try:
            if isinstance(uid, str):
                uid = ObjectId(uid)
        except Exception:
            return None
        u = await users.find_one({"_id": uid})
        if not u:
            return None
        return UserInDb.model_validate(u)
        