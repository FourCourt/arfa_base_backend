"""
認證控制器
"""
from typing import Dict, Any
from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, UserLogin, PasswordReset, PasswordResetConfirm
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user

class AuthController:
    """認證控制器"""
    
    def __init__(self):
        self.auth_service = AuthService()
    
    def login(self, request: Request, db: Session, credentials: UserLogin) -> Dict[str, Any]:
        """用戶登入"""
        try:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
            
            result = self.auth_service.login(
                db=db,
                username=credentials.username,
                password=credentials.password,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return result
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="登入過程中發生錯誤"
            )
    
    def logout(self, db: Session, current_user: User, session_id: str = None) -> Dict[str, str]:
        """用戶登出"""
        try:
            result = self.auth_service.logout(db, current_user, session_id)
            return result
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="登出過程中發生錯誤"
            )
    
    def get_current_user_info(self, current_user: User) -> Dict[str, Any]:
        """獲取當前用戶信息"""
        return {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "phone": current_user.phone,
            "status": current_user.status,
            "last_login_at": current_user.last_login_at,
            "mfa_enabled": current_user.mfa_enabled,
            "created_at": current_user.created_at,
            "updated_at": current_user.updated_at
        }
    
    def request_password_reset(self, db: Session, password_reset: PasswordReset) -> Dict[str, str]:
        """請求密碼重設"""
        try:
            result = self.auth_service.request_password_reset(db, password_reset.username)
            return result
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="請求密碼重設時發生錯誤"
            )
    
    def confirm_password_reset(self, db: Session, password_reset_confirm: PasswordResetConfirm) -> Dict[str, str]:
        """確認密碼重設"""
        try:
            # 檢查密碼強度
            from app.core.security import is_password_strong
            is_strong, message = is_password_strong(password_reset_confirm.new_password)
            if not is_strong:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=message
                )
            
            result = self.auth_service.confirm_password_reset(
                db, 
                password_reset_confirm.token, 
                password_reset_confirm.new_password
            )
            return result
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="確認密碼重設時發生錯誤"
            )
    
    def get_login_logs(self, db: Session, current_user: User, skip: int = 0, limit: int = 100):
        """獲取登入日誌"""
        try:
            logs = self.auth_service.get_user_login_logs(db, current_user.id, skip, limit)
            return [
                {
                    "id": log.id,
                    "succeeded": log.succeeded,
                    "reason": log.reason,
                    "ip": log.ip.hex() if log.ip else None,
                    "user_agent": log.user_agent,
                    "occurred_at": log.occurred_at
                }
                for log in logs
            ]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="獲取登入日誌時發生錯誤"
            )
