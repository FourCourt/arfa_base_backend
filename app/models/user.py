from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, BigInteger, SmallInteger, VARBINARY
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models.base import Base

class User(Base):
    __tablename__ = "users"
    
    # 主鍵
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 用戶基本信息
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(191), unique=True, index=True, nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    
    # 密碼相關 (使用鹽值和迭代次數)
    password_hash = Column(VARBINARY(64), nullable=False)
    password_salt = Column(VARBINARY(32), nullable=False)
    password_iters = Column(Integer, nullable=False, default=100000)
    
    # 狀態和安全
    status = Column(Integer, index=True, nullable=False, default=1)  # 1: 活躍, 0: 停用, -1: 鎖定
    failed_login_count = Column(SmallInteger, nullable=False, default=0)
    last_login_at = Column(DateTime, nullable=True)
    last_login_ip = Column(VARBINARY(16), nullable=True)  # IPv6 支持
    mfa_enabled = Column(Boolean, nullable=False, default=False)
    
    # 密碼重設
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    
    # 郵箱驗證
    email_verified = Column(Boolean, nullable=False, default=False)
    email_verification_token = Column(String(255), nullable=True)
    email_verification_expires = Column(DateTime, nullable=True)
    
    # 時間戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯到登入日誌
    login_logs = relationship("UserLoginEvent", back_populates="user")
    # 關聯到用戶角色
    user_roles = relationship("UserRole", back_populates="user")
    # 關聯到用戶會話
    user_sessions = relationship("UserSession", back_populates="user")
    # 關聯到伺服器
    servers = relationship("Server", back_populates="user")
    # 關聯到資料庫配置
    database_configs = relationship("DatabaseConfig", back_populates="user")
    
    @property
    def is_active(self) -> bool:
        """檢查用戶是否活躍"""
        return self.status == 1
    
    @property
    def is_locked(self) -> bool:
        """檢查用戶是否被鎖定"""
        return self.status == -1
    
    @property
    def is_disabled(self) -> bool:
        """檢查用戶是否被停用"""
        return self.status == 0
    
    @property
    def is_verified(self) -> bool:
        """檢查用戶是否已驗證郵箱"""
        return self.email_verified

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str  # 可以是用戶名、郵箱或電話
    password: str

class UserResponse(UserBase):
    id: int
    status: int
    failed_login_count: int
    last_login_at: Optional[datetime]
    mfa_enabled: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserProfile(UserResponse):
    """用戶個人資料，包含敏感信息"""
    last_login_ip: Optional[str]
    password_iters: int

class PasswordReset(BaseModel):
    username: str  # 可以是用戶名、郵箱或電話

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class UserStatusUpdate(BaseModel):
    status: int  # 1: 活躍, 0: 停用, -1: 鎖定

class UserRegister(BaseModel):
    """用戶註冊模型"""
    username: str
    email: str
    phone: Optional[str] = None
    password: str
    confirm_password: str

class EmailVerification(BaseModel):
    """郵箱驗證模型"""
    token: str

class UserRegisterResponse(BaseModel):
    """註冊響應模型"""
    message: str
    user_id: int
    email: str
    verification_required: bool = True