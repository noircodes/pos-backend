from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

from repositories.repository_user import RepositoryUser
from models.auth import TokenPayload
from core.security import decode_access_token
from models.model_user import UserInDb
from utils.error_handler import handle_repo_errors


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
router = APIRouter(prefix="/users", tags=["users"])


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDb:
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await RepositoryUser.get_by_id(sub)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/me", response_model=UserInDb)
async def me(user: UserInDb = Depends(get_current_user)):
    return user


@router.get("/{user_id}", response_model=Optional[UserInDb])
@handle_repo_errors
async def get_user(user_id: str):
    u = await RepositoryUser.get_by_id(user_id)
    return u
