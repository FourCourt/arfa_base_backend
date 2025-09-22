from sqlalchemy import Column, BigInteger, String, Integer, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.base import Base

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    code = Column(String(100), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    status = Column(Integer, nullable=False, default=1, index=True)
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    user_roles = relationship("UserRole", back_populates="role")
    role_permissions = relationship("RolePermission", back_populates="role")

class RoleResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str]
    status: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class RoleCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    status: int = 1


