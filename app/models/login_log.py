from sqlalchemy import Column, Integer, Boolean, VARBINARY, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.base import Base

class UserLoginEvent(Base):
    __tablename__ = "user_login_events"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    succeeded = Column(Boolean, nullable=False)
    reason = Column(Integer, nullable=False)  # 1: 成功, 2: 密碼錯誤, 3: 用戶不存在, 4: 帳號鎖定
    ip = Column(VARBINARY(16), nullable=True)
    user_agent = Column(String(255), nullable=True)
    occurred_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # 關聯到用戶
    user = relationship("User", back_populates="login_logs")

class UserLoginEventResponse(BaseModel):
    id: int
    user_id: int
    succeeded: bool
    reason: int
    ip: Optional[str]
    user_agent: Optional[str]
    occurred_at: datetime
    
    class Config:
        from_attributes = True
