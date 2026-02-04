from fastapi import APIRouter, HTTPException, status

from repositories.repository_user import RepositoryUser
from core.security import verify_password, create_access_token
from models.auth import Token
from utils.models.model_data_type import BaseModel


router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login", response_model=Token)
async def login(payload: LoginRequest):
    user = await RepositoryUser.get_by_username(payload.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": "bearer"}


class RegisterRequest(BaseModel):
    name: str
    email: str
    username: str
    password: str
    role: str = "user"


@router.post("/register", response_model=dict)
async def register(payload: RegisterRequest):
    r = await RepositoryUser.create_user(payload, None)
    return {"id": str(r.id), "username": r.username}
