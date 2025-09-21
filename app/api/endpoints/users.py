"""
用戶相關 API 端點
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User, UserCreate, UserResponse, UserStatusUpdate
from app.core.dependencies import get_current_user
from app.controllers.user_controller import UserController

router = APIRouter()
user_controller = UserController()

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """創建新用戶"""
    return user_controller.create_user(db, user)

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """獲取用戶列表 (需要認證)"""
    return user_controller.get_users(db, current_user, skip, limit)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """根據 ID 獲取用戶"""
    return user_controller.get_user_by_id(db, user_id)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, 
    user_update: UserCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用戶信息"""
    return user_controller.update_user(db, user_id, user_update, current_user)

@router.delete("/{user_id}")
async def delete_user(
    user_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """刪除用戶"""
    return user_controller.delete_user(db, user_id, current_user)

@router.patch("/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: int,
    status_update: UserStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用戶狀態"""
    return user_controller.update_user_status(db, user_id, status_update, current_user)

@router.get("/active/list", response_model=List[UserResponse])
async def get_active_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """獲取活躍用戶列表 (管理員功能)"""
    return user_controller.get_active_users(db, current_user, skip, limit)

@router.get("/locked/list", response_model=List[UserResponse])
async def get_locked_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """獲取被鎖定的用戶列表 (管理員功能)"""
    return user_controller.get_locked_users(db, current_user, skip, limit)