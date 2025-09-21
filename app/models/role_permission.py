from sqlalchemy import Column, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.base import Base

class RolePermission(Base):
    __tablename__ = "role_permissions"
    
    role_id = Column(BigInteger, ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(BigInteger, ForeignKey("permissions.id"), primary_key=True)
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    
    # 關聯
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")

class RolePermissionResponse(BaseModel):
    role_id: int
    permission_id: int
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True
