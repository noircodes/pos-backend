from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from repositories.repository_user import RepositoryUser
from core.security import verify_password, create_access_token
from models.auth import Token
from utils.models.model_data_type import BaseModel


router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    json_data: LoginRequest | None = None
):
    # Support both OAuth2 form data and JSON body
    if form_data.username and form_data.password:
        username = form_data.username
        password = form_data.password
    elif json_data:
        username = json_data.username
        password = json_data.password
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username and password are required"
        )
    
    user = await RepositoryUser.get_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not verify_password(password, user.password):
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
