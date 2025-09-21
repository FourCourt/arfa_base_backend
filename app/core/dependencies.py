"""
認證依賴項
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.core.security import verify_token

# HTTP Bearer 認證
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """獲取當前用戶"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無效的認證憑證",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        if payload is None:
            raise credentials_exception
        
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except Exception:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """獲取當前活躍用戶"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用戶帳號已被停用"
        )
    return current_user

async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """獲取當前已驗證用戶"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用戶帳號尚未驗證"
        )
    return current_user

def check_user_not_locked(user: User) -> bool:
    """檢查用戶是否被鎖定"""
    return not user.is_locked

def increment_login_attempts(user: User, db: Session):
    """增加登入嘗試次數"""
    user.failed_login_count += 1
    
    # 如果嘗試次數達到3次，鎖定帳號
    if user.failed_login_count >= 3:
        user.status = -1  # 鎖定狀態
    
    db.commit()

def reset_login_attempts(user: User, db: Session, ip_address: str = None):
    """重置登入嘗試次數"""
    user.failed_login_count = 0
    user.status = 1  # 活躍狀態
    user.last_login_at = datetime.utcnow()
    
    # 記錄 IP 地址
    if ip_address:
        # 將 IP 地址轉換為二進制格式
        import socket
        try:
            if ':' in ip_address:  # IPv6
                user.last_login_ip = socket.inet_pton(socket.AF_INET6, ip_address)
            else:  # IPv4
                user.last_login_ip = socket.inet_pton(socket.AF_INET, ip_address)
        except socket.error:
            pass  # 如果 IP 地址無效，忽略
    
    db.commit()
