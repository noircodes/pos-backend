from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import Any

from repositories.repository_inventory import RepositoryInventory
from routers.users import get_current_user
from utils.models.model_data_type import BaseModel, ObjectId, Decimal128
from utils.error_handler import handle_repo_errors

router = APIRouter(prefix="/stores/{store_id}/inventory", tags=["inventory"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class AdjustRequest(BaseModel):
    product_id: str
    delta: Decimal128


@router.post("/adjust")
@handle_repo_errors
async def adjust_inventory(store_id: str, payload: AdjustRequest, _=Depends(get_current_user)):
    item = await RepositoryInventory.adjust_qty(ObjectId(store_id), ObjectId(payload.product_id), payload.delta)
    return {"ok": True, "item": item.model_dump(mode="json")}
