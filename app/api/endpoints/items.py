from typing import List
from fastapi import APIRouter, Depends, Query
from app.models.item import Item, ItemCreate, ItemResponse
from app.models.user import User
from app.db import get_db
from app.core.dependencies import get_current_user
from app.controllers.item_controller import ItemController
from sqlalchemy.orm import Session

router = APIRouter()
item_controller = ItemController()

@router.post("/", response_model=ItemResponse)
async def create_item(
    item: ItemCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """創建新項目 (需要認證)"""
    return item_controller.create_item(db, item, current_user)

@router.get("/", response_model=List[ItemResponse])
async def get_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """獲取項目列表 (需要認證)"""
    return item_controller.get_items(db, current_user, skip, limit)

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """根據 ID 獲取項目 (需要認證)"""
    return item_controller.get_item_by_id(db, item_id, current_user)

@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int, 
    item_update: ItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新項目 (需要認證)"""
    return item_controller.update_item(db, item_id, item_update, current_user)

@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """刪除項目 (需要認證)"""
    return item_controller.delete_item(db, item_id, current_user)

@router.get("/search/query", response_model=List[ItemResponse])
async def search_items(
    q: str = Query(..., min_length=1, description="搜索關鍵字"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """搜索項目"""
    return item_controller.search_items(db, q, current_user, skip, limit)

@router.get("/filter/price", response_model=List[ItemResponse])
async def get_items_by_price_range(
    min_price: float = Query(..., ge=0, description="最低價格"),
    max_price: float = Query(..., ge=0, description="最高價格"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """根據價格範圍獲取項目"""
    return item_controller.get_items_by_price_range(db, min_price, max_price, current_user, skip, limit)

@router.get("/admin/all", response_model=List[ItemResponse])
async def get_all_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """獲取所有項目 (管理員功能)"""
    return item_controller.get_all_items(db, current_user, skip, limit)