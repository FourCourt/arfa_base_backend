from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import Base
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class Server(Base):
    """伺服器模型"""
    __tablename__ = "servers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    server_name = Column(String(255), nullable=False, comment="伺服器名稱")
    server_ip = Column(String(255), nullable=False, comment="伺服器IP地址")
    server_port = Column(Integer, nullable=False, comment="伺服器端口")
    description = Column(String(500), nullable=True, comment="伺服器描述")
    is_active = Column(Boolean, default=True, comment="是否啟用")
    created_at = Column(DateTime, default=datetime.utcnow, comment="創建時間")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新時間")
    
    # 關聯關係
    user = relationship("User", back_populates="servers")
    database_configs = relationship("DatabaseConfig", back_populates="server", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Server(id={self.id}, name='{self.server_name}', ip='{self.server_ip}')>"

# Pydantic 模型
class ServerBase(BaseModel):
    server_name: str = Field(..., example="My Dev Server")
    server_ip: str = Field(..., example="192.168.1.100")
    server_port: int = Field(..., example=22)
    description: Optional[str] = Field(None, example="開發環境的測試伺服器")
    is_active: bool = Field(True, example=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "server_name": "My Dev Server",
                "server_ip": "192.168.1.100",
                "server_port": 22,
                "description": "開發環境的測試伺服器",
                "is_active": True
            }
        }

class ServerCreate(ServerBase):
    pass

class ServerUpdate(ServerBase):
    server_name: Optional[str] = None
    server_ip: Optional[str] = None
    server_port: Optional[int] = None
    is_active: Optional[bool] = None

class ServerResponse(ServerBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "server_name": "My Dev Server",
                "server_ip": "192.168.1.100",
                "server_port": 22,
                "description": "開發環境的測試伺服器",
                "is_active": True,
                "created_at": "2023-01-01T12:00:00",
                "updated_at": "2023-01-01T12:00:00"
            }
        }

class ServerListResponse(BaseModel):
    total: int
    servers: List[ServerResponse]
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 1,
                "servers": [
                    {
                        "id": 1,
                        "user_id": 1,
                        "server_name": "My Dev Server",
                        "server_ip": "192.168.1.100",
                        "server_port": 22,
                        "description": "開發環境的測試伺服器",
                        "is_active": True,
                        "created_at": "2023-01-01T12:00:00",
                        "updated_at": "2023-01-01T12:00:00"
                    }
                ]
            }
        }
