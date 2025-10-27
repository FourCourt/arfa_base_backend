"""
用戶相關商務邏輯
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.user import User
from app.services.base_service import BaseService
from app.core.security import create_password_hash, verify_password_with_salt, hash_token
from app.core.session import create_user_session, revoke_user_sessions

class UserService(BaseService[User]):
    """用戶服務類"""
    
    def __init__(self):
        super().__init__(User)
    
    def create_user(self, db: Session, username: str, email: Optional[str], 
                   phone: Optional[str], password: str) -> User:
        """創建新用戶"""
        # 檢查用戶名、郵箱、電話是否已存在
        existing_user = self.get_by_username_or_email_or_phone(db, username, email, phone)
        if existing_user:
            if existing_user.username == username:
                raise ValueError("用戶名已存在")
            elif existing_user.email == email:
                raise ValueError("郵箱已存在")
            elif existing_user.phone == phone:
                raise ValueError("電話已存在")
        
        # 創建密碼哈希
        password_hash, password_salt, password_iters = create_password_hash(password)
        
        # 創建用戶
        return self.create(
            db,
            username=username,
            email=email,
            phone=phone,
            password_hash=password_hash,
            password_salt=password_salt,
            password_iters=password_iters,
            status=1  # 活躍狀態
        )
    
    def get_by_username_or_email_or_phone(self, db: Session, username: str, 
                                        email: Optional[str], phone: Optional[str]) -> Optional[User]:
        """根據用戶名、郵箱或電話查找用戶"""
        conditions = [User.username == username]
        if email:
            conditions.append(User.email == email)
        if phone:
            conditions.append(User.phone == phone)
        
        return db.query(User).filter(or_(*conditions)).first()
    
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """用戶認證"""
        user = self.get_by_username_or_email_or_phone(db, username, username, username)
        
        if not user:
            return None
        
        # 檢查用戶狀態
        if not user.is_active:
            return None
        
        if user.is_locked:
            return None
        
        # 驗證密碼
        if not verify_password_with_salt(password, user.password_salt, user.password_hash, user.password_iters):
            # 增加失敗次數
            self.increment_failed_login_count(db, user)
            return None
        
        # 重置失敗次數
        self.reset_failed_login_count(db, user)
        return user
    
    def increment_failed_login_count(self, db: Session, user: User):
        """增加登入失敗次數"""
        user.failed_login_count += 1
        
        # 如果失敗次數達到3次，鎖定帳號
        if user.failed_login_count >= 3:
            user.status = -1  # 鎖定狀態
        
        db.commit()
    
    def reset_failed_login_count(self, db: Session, user: User, ip_address: Optional[str] = None):
        """重置登入失敗次數"""
        user.failed_login_count = 0
        user.status = 1  # 活躍狀態
        user.last_login_at = datetime.utcnow()
        
        # 記錄 IP 地址
        if ip_address:
            import socket
            try:
                if ':' in ip_address:  # IPv6
                    user.last_login_ip = socket.inet_pton(socket.AF_INET6, ip_address)
                else:  # IPv4
                    user.last_login_ip = socket.inet_pton(socket.AF_INET, ip_address)
            except socket.error:
                pass
        
        db.commit()
    
    def update_password(self, db: Session, user: User, new_password: str):
        """更新用戶密碼"""
        password_hash, password_salt, password_iters = create_password_hash(new_password)
        user.password_hash = password_hash
        user.password_salt = password_salt
        user.password_iters = password_iters
        user.updated_at = datetime.utcnow()
        db.commit()
    
    def set_password_reset_token(self, db: Session, user: User) -> str:
        """設置密碼重設令牌"""
        from app.core.security import generate_password_reset_token
        token = generate_password_reset_token()
        user.password_reset_token = hash_token(token)
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        return token
    
    def reset_password_with_token(self, db: Session, token: str, new_password: str) -> bool:
        """使用令牌重設密碼"""
        hashed_token = hash_token(token)
        user = db.query(User).filter(
            User.password_reset_token == hashed_token,
            User.password_reset_expires > datetime.utcnow()
        ).first()
        
        if not user:
            return False
        
        # 更新密碼
        self.update_password(db, user, new_password)
        
        # 清除重設令牌
        user.password_reset_token = None
        user.password_reset_expires = None
        user.failed_login_count = 0
        user.status = 1
        db.commit()
        
        return True
    
    def get_active_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """獲取活躍用戶列表"""
        return db.query(User).filter(User.status == 1).offset(skip).limit(limit).all()
    
    def get_locked_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """獲取被鎖定的用戶列表"""
        return db.query(User).filter(User.status == -1).offset(skip).limit(limit).all()
    
    def set_email_verification_token(self, db: Session, user: User) -> str:
        """設置郵箱驗證令牌"""
        from app.core.security import generate_password_reset_token
        token = generate_password_reset_token()
        user.email_verification_token = hash_token(token)
        user.email_verification_expires = datetime.utcnow() + timedelta(hours=24)  # 24小時過期
        db.commit()
        return token
    
    def verify_email_with_token(self, db: Session, token: str) -> bool:
        """使用令牌驗證郵箱"""
        hashed_token = hash_token(token)
        user = db.query(User).filter(
            User.email_verification_token == hashed_token,
            User.email_verification_expires > datetime.utcnow()
        ).first()
        
        if not user:
            return False
        
        # 驗證成功，激活帳號
        user.email_verified = True
        user.status = 1  # 活躍狀態
        user.email_verification_token = None
        user.email_verification_expires = None
        db.commit()
        
        return True




