"""
認證相關 API 端點
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User, UserLogin, PasswordReset, PasswordResetConfirm
from app.core.dependencies import get_current_user
from app.controllers.auth_controller import AuthController

router = APIRouter()
auth_controller = AuthController()

@router.post("/login")
async def login(
    user_credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """用戶登入"""
    return auth_controller.login(request, db, user_credentials)

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """用戶登出"""
    return auth_controller.logout(db, current_user)

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """獲取當前用戶信息"""
    return auth_controller.get_current_user_info(current_user)

@router.post("/password-reset")
async def request_password_reset(
    password_reset: PasswordReset,
    db: Session = Depends(get_db)
):
    """請求重設密碼"""
    return auth_controller.request_password_reset(db, password_reset)

@router.post("/password-reset/confirm")
async def confirm_password_reset(
    password_reset_confirm: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """確認重設密碼"""
    return auth_controller.confirm_password_reset(db, password_reset_confirm)

@router.get("/login-logs")
async def get_login_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """獲取登入日誌"""
    return auth_controller.get_login_logs(db, current_user, skip, limit)
