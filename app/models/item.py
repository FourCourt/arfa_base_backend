from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.base import Base

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=True)
    owner_id = Column(BigInteger, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯到用戶
    owner = relationship("User", back_populates="items")

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: Optional[float] = None

class ItemCreate(ItemBase):
    owner_id: Optional[int] = None

class ItemResponse(ItemBase):
    id: int
    owner_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
