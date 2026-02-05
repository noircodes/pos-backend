from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List

from repositories.repository_category import RepositoryCategory
from models.category import CategoryRequest, CategoryInDb, CategoryCombo
from routers.users import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])


# Combo endpoint for dropdowns - lightweight list
@router.get("/combo", response_model=List[CategoryCombo])
async def get_categories_combo(active_only: bool = Query(True, description="Show only active categories")):
    """
    Get lightweight category list for dropdown/combo boxes
    Returns only id, name, and display_name sorted by display_name
    """
    return await RepositoryCategory.get_combo_list(active_only=active_only)


# CRUD endpoints
@router.post("/", response_model=CategoryInDb)
async def create_category(payload: CategoryRequest, _=Depends(get_current_user)):
    """
    Create a new category
    The category name must be unique
    """
    try:
        cat = await RepositoryCategory.create_category(payload)
        return cat
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[CategoryInDb])
async def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = Query(False, description="Show only active categories")
):
    """List all categories with pagination"""
    return await RepositoryCategory.list_categories(skip=skip, limit=limit, active_only=active_only)


@router.get("/{category_id}", response_model=CategoryInDb)
async def get_category(category_id: str):
    """Get category details by ID"""
    cat = await RepositoryCategory.get_by_id(category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


@router.put("/{category_id}", response_model=CategoryInDb)
async def update_category(category_id: str, payload: CategoryRequest, _=Depends(get_current_user)):
    """Update category details"""
    try:
        cat = await RepositoryCategory.update_category(category_id, payload)
        return cat
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}")
async def delete_category(category_id: str, _=Depends(get_current_user)):
    """
    Soft delete a category (sets active to false)
    Cannot delete if category is used by any products
    """
    try:
        success = await RepositoryCategory.delete_category(category_id)
        if success:
            return {"message": "Category deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))