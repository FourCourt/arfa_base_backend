"""
認證相關商務邏輯
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.login_log import UserLoginEvent
from app.models.user_session import UserSession
from app.services.user_service import UserService
from app.core.security import create_access_token, generate_password_reset_token, hash_token
from app.core.session import create_user_session, revoke_user_sessions, is_session_valid
from app.core.config import settings

class AuthService:
    """認證服務類"""
    
    def __init__(self):
        self.user_service = UserService()
    
    def login(self, db: Session, username: str, password: str, 
              ip_address: Optional[str], user_agent: Optional[str]) -> Dict[str, Any]:
        """用戶登入"""
        
        # 查找用戶
        user = self.user_service.get_by_username_or_email_or_phone(db, username, username, username)
        
        # 記錄登入嘗試
        login_event = self._create_login_event(db, user, False, "用戶不存在", ip_address, user_agent)
        
        if not user:
            raise ValueError("使用者名稱或密碼錯誤")
        
        # 檢查用戶是否被鎖定
        if user.is_locked:
            login_event.succeeded = False
            login_event.reason = 4  # 帳號鎖定
            login_event.user_id = user.id
            db.commit()
            raise ValueError("帳號已被鎖定，請稍後再試")
        
        # 驗證密碼
        if not self.user_service.authenticate_user(db, username, password):
            login_event.user_id = user.id
            login_event.reason = 2  # 密碼錯誤
            db.commit()
            raise ValueError("使用者名稱或密碼錯誤")
        
        # 檢查用戶是否活躍
        if not user.is_active:
            login_event.user_id = user.id
            login_event.reason = 4  # 帳號停用
            db.commit()
            raise ValueError("帳號已被停用")
        
        # 登入成功
        self.user_service.reset_failed_login_count(db, user, ip_address)
        
        # 創建訪問令牌
        access_token = self._create_access_token(user)
        
        # 創建會話
        session = create_user_session(user, access_token, ip_address, user_agent, db)
        
        # 記錄成功登入
        login_event.succeeded = True
        login_event.reason = 1  # 成功
        login_event.user_id = user.id
        db.commit()
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "status": user.status,
                "last_login_at": user.last_login_at,
                "mfa_enabled": user.mfa_enabled
            },
            "session_id": session.session_id
        }
    
    def logout(self, db: Session, user: User, session_id: Optional[str] = None):
        """用戶登出"""
        if session_id:
            # 撤銷特定會話
            from app.core.session import revoke_session
            revoke_session(session_id, db)
        else:
            # 撤銷用戶所有會話
            revoke_user_sessions(user.id, db)
        
        return {"message": "登出成功"}
    
    def request_password_reset(self, db: Session, username: str) -> Dict[str, str]:
        """請求密碼重設"""
        user = self.user_service.get_by_username_or_email_or_phone(db, username, username, username)
        
        if not user:
            # 為了安全，即使用戶不存在也返回成功消息
            return {"message": "如果該郵箱存在，重設密碼的郵件已發送"}
        
        # 生成重設令牌
        token = self.user_service.set_password_reset_token(db, user)
        
        # 在實際應用中，這裡應該發送郵件
        # 現在我們只是記錄令牌（僅用於開發測試）
        print(f"密碼重設令牌 (僅開發用): {token}")
        
        return {"message": "如果該郵箱存在，重設密碼的郵件已發送"}
    
    def confirm_password_reset(self, db: Session, token: str, new_password: str) -> Dict[str, str]:
        """確認密碼重設"""
        success = self.user_service.reset_password_with_token(db, token, new_password)
        
        if not success:
            raise ValueError("無效或已過期的重設令牌")
        
        return {"message": "密碼重設成功"}
    
    def verify_token(self, db: Session, token: str) -> Optional[User]:
        """驗證令牌並返回用戶"""
        from app.core.security import verify_token
        payload = verify_token(token)
        
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = self.user_service.get_by_id(db, int(user_id))
        if not user or not user.is_active:
            return None
        
        return user
    
    def get_user_login_logs(self, db: Session, user_id: int, skip: int = 0, limit: int = 100):
        """獲取用戶登入日誌"""
        return db.query(UserLoginEvent).filter(
            UserLoginEvent.user_id == user_id
        ).order_by(UserLoginEvent.occurred_at.desc()).offset(skip).limit(limit).all()
    
    def _create_access_token(self, user: User) -> str:
        """創建訪問令牌"""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )
    
    def _create_login_event(self, db: Session, user: Optional[User], succeeded: bool, 
                          reason: str, ip_address: Optional[str], user_agent: Optional[str]) -> UserLoginEvent:
        """創建登入事件記錄"""
        # 轉換 IP 地址為二進制
        ip_binary = None
        if ip_address:
            import socket
            try:
                if ':' in ip_address:  # IPv6
                    ip_binary = socket.inet_pton(socket.AF_INET6, ip_address)
                else:  # IPv4
                    ip_binary = socket.inet_pton(socket.AF_INET, ip_address)
            except socket.error:
                pass
        
        # 轉換原因為數字
        reason_code = 1 if succeeded else 2  # 1: 成功, 2: 失敗
        
        login_event = UserLoginEvent(
            user_id=user.id if user else None,
            succeeded=succeeded,
            reason=reason_code,
            ip=ip_binary,
            user_agent=user_agent[:255] if user_agent else None,
            occurred_at=datetime.utcnow()
        )
        
        db.add(login_event)
        return login_event




