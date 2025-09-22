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

@router.post("/", response_model=UserResponse, summary="Create User", description="Create a new user account")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create new user"""
    return user_controller.create_user(db, user)

@router.get("/", response_model=List[UserResponse], summary="Get Users", description="Get list of users (requires authentication)")
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get users list"""
    return user_controller.get_users(db, current_user, skip, limit)

@router.get("/{user_id}", response_model=UserResponse, summary="Get User by ID", description="Get user information by user ID")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    return user_controller.get_user_by_id(db, user_id)

@router.put("/{user_id}", response_model=UserResponse, summary="Update User", description="Update user information")
async def update_user(
    user_id: int, 
    user_update: UserCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user information"""
    return user_controller.update_user(db, user_id, user_update, current_user)

@router.delete("/{user_id}", summary="Delete User", description="Delete user account")
async def delete_user(
    user_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user"""
    return user_controller.delete_user(db, user_id, current_user)

@router.patch("/{user_id}/status", response_model=UserResponse, summary="Update User Status", description="Update user account status")
async def update_user_status(
    user_id: int,
    status_update: UserStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user status"""
    return user_controller.update_user_status(db, user_id, status_update, current_user)

@router.get("/active/list", response_model=List[UserResponse], summary="Get Active Users", description="Get list of active users (admin function)")
async def get_active_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active users list"""
    return user_controller.get_active_users(db, current_user, skip, limit)

@router.get("/locked/list", response_model=List[UserResponse], summary="Get Locked Users", description="Get list of locked users (admin function)")
async def get_locked_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get locked users list"""
    return user_controller.get_locked_users(db, current_user, skip, limit)