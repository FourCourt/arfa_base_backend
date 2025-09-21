from sqlalchemy import Column, BigInteger, String, VARBINARY, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.base import Base

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(64), nullable=False, unique=True)
    token_signature = Column(String(64), nullable=False)
    ip = Column(VARBINARY(16), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_seen_at = Column(DateTime, nullable=True, index=True)
    revoked_at = Column(DateTime, nullable=True)
    
    # 關聯
    user = relationship("User", back_populates="user_sessions")

class UserSessionResponse(BaseModel):
    id: int
    user_id: int
    session_id: str
    ip: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    last_seen_at: Optional[datetime]
    revoked_at: Optional[datetime]
    
    class Config:
        from_attributes = True
