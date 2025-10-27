from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.base import Base

class UserRole(Base):
    __tablename__ = "user_roles"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    
    # 關聯
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")

class UserRoleResponse(BaseModel):
    user_id: int
    role_id: int
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True
