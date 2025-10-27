"""
認證相關 API 端點
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User, UserLogin, PasswordReset, PasswordResetConfirm, UserRegister, EmailVerification, UserRegisterResponse
from app.core.dependencies import get_current_user
from app.controllers.auth_controller import AuthController

router = APIRouter()
auth_controller = AuthController()

@router.post("/login", summary="User Login", description="Authenticate user and return access token")
async def login(
    user_credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """User login authentication"""
    return auth_controller.login(request, db, user_credentials)

@router.post("/logout", summary="User Logout", description="Logout current user and invalidate session")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """User logout"""
    return auth_controller.logout(db, current_user)

@router.get("/me", summary="Get Current User", description="Get current authenticated user information")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return auth_controller.get_current_user_info(current_user)

@router.post("/password-reset", summary="Request Password Reset", description="Request password reset token")
async def request_password_reset(
    password_reset: PasswordReset,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    return auth_controller.request_password_reset(db, password_reset)

@router.post("/password-reset/confirm", summary="Confirm Password Reset", description="Confirm password reset with token")
async def confirm_password_reset(
    password_reset_confirm: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Confirm password reset"""
    return auth_controller.confirm_password_reset(db, password_reset_confirm)

@router.get("/login-logs", summary="Get Login Logs", description="Get user login history and logs")
async def get_login_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get login logs"""
    return auth_controller.get_login_logs(db, current_user, skip, limit)

@router.post("/register", response_model=UserRegisterResponse, summary="User Registration", description="Register a new user account")
async def register(
    user_register: UserRegister,
    db: Session = Depends(get_db)
):
    """User registration"""
    return auth_controller.register(db, user_register)

@router.post("/verify-email", summary="Verify Email", description="Verify user email with token")
async def verify_email(
    email_verification: EmailVerification,
    db: Session = Depends(get_db)
):
    """Verify email address"""
    return auth_controller.verify_email(db, email_verification)
