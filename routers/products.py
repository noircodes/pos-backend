from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List

from repositories.repository_product import RepositoryProduct
from models.product import ProductRequest, ProductInDb
from routers.users import get_current_user

router = APIRouter(prefix="/products", tags=["products"])


# Product CRUD endpoints
@router.post("/", response_model=ProductInDb)
async def create_product(payload: ProductRequest, _=Depends(get_current_user)):
    # For now any authenticated user can create; will gate by role later
    try:
        p = await RepositoryProduct.create_product(payload)
        return p
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ProductInDb])
async def list_products(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100)):
    return await RepositoryProduct.list_products(skip=skip, limit=limit)


@router.post("/{sku}/regenerate-sku", response_model=ProductInDb)
async def regenerate_sku(sku: str, _=Depends(get_current_user)):
    """
    Regenerate SKU for a product
    This will generate a new SKU while keeping all other product data unchanged
    """
    try:
        p = await RepositoryProduct.regenerate_sku(sku)
        return p
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
