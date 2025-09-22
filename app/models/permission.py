from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.base import Base

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    code = Column(String(150), nullable=False, unique=True)
    name = Column(String(150), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    role_permissions = relationship("RolePermission", back_populates="permission")

class PermissionResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class PermissionCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None




