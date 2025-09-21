from sqlalchemy import Column, BigInteger, VARBINARY, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.base import Base

class PasswordReset(Base):
    __tablename__ = "password_resets"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    token_hash = Column(VARBINARY(32), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class PasswordResetResponse(BaseModel):
    id: int
    user_id: int
    expires_at: datetime
    used_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

