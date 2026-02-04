from fastapi import APIRouter, Depends, HTTPException, Header, Query
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, List

from repositories.repository_order import RepositoryOrder
from repositories.repository_idempotency import RepositoryIdempotency
from routers.users import get_current_user
from models.order import OrderRequest, OrderInDb
from utils.models.model_data_type import BaseModel, ObjectId

router = APIRouter(prefix="/orders", tags=["orders"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/")
async def create_order(payload: OrderRequest, idempotency_key: Optional[str] = Header(None), user=Depends(get_current_user)):
    # If idempotency key provided, try to return existing order
    if idempotency_key:
        existing = await RepositoryOrder.get_by_idempotency(idempotency_key)
        if existing:
            return {"ok": True, "order": existing.model_dump(mode="json")}
        # try to create processing lock
        created = await RepositoryIdempotency.create_processing(idempotency_key, "/orders", str(user.id))
        if not created:
            # concurrent op, return existing if any
            existing = await RepositoryOrder.get_by_idempotency(idempotency_key)
            if existing:
                return {"ok": True, "order": existing.model_dump(mode="json")}
            raise HTTPException(status_code=409, detail="Idempotency key is being processed")
    try:
        order = await RepositoryOrder.create_order(payload, idempotency_key)
        if idempotency_key:
            await RepositoryIdempotency.set_response(idempotency_key, {"order_id": str(order.id)})
        return {"ok": True, "order": order.model_dump(mode="json")}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{order_id}", response_model=OrderInDb)
async def get_order(order_id: str, _=Depends(get_current_user)):
    try:
        order = await RepositoryOrder.get_by_id(ObjectId(order_id))
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid order ID: {str(e)}")


@router.get("/", response_model=List[OrderInDb])
async def list_orders(
    store_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    _=Depends(get_current_user)
):
    try:
        store_oid = ObjectId(store_id) if store_id else None
        user_oid = ObjectId(user_id) if user_id else None
        
        orders = await RepositoryOrder.list_orders(
            store_id=store_oid,
            user_id=user_oid,
            status=status,
            skip=skip,
            limit=limit
        )
        return orders
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")


class UpdateStatusRequest(BaseModel):
    status: str


@router.patch("/{order_id}/status")
async def update_order_status(order_id: str, payload: UpdateStatusRequest, _=Depends(get_current_user)):
    try:
        order = await RepositoryOrder.update_status(ObjectId(order_id), payload.status)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return {"ok": True, "order": order.model_dump(mode="json")}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
