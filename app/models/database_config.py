from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import enum

class DatabaseType(str, enum.Enum):
    """資料庫類型枚舉"""
    MYSQL = "MYSQL"
    POSTGRESQL = "POSTGRESQL"
    SQLITE = "SQLITE"
    MONGODB = "MONGODB"

class TestStatus(str, enum.Enum):
    """測試狀態枚舉"""
    NEVER_TESTED = "NEVER_TESTED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class TestType(str, enum.Enum):
    """測試類型枚舉"""
    CONNECTION = "CONNECTION"
    QUERY = "QUERY"

class TestResult(str, enum.Enum):
    """測試結果枚舉"""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class DatabaseConfig(Base):
    """資料庫配置模型"""
    __tablename__ = "database_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    server_id = Column(Integer, ForeignKey("servers.id", ondelete="CASCADE"), nullable=False, index=True)
    config_name = Column(String(255), nullable=False, comment="配置名稱")
    host = Column(String(255), nullable=False, comment="資料庫主機")
    port = Column(Integer, nullable=False, comment="資料庫端口")
    database_name = Column(String(255), nullable=False, comment="資料庫名稱")
    username = Column(String(255), nullable=False, comment="使用者名稱")
    password_hash = Column(String(255), nullable=False, comment="加密後的密碼")
    db_type = Column(Enum(DatabaseType), nullable=False, comment="資料庫類型")
    connection_string = Column(Text, comment="完整連接字串")
    is_active = Column(Boolean, default=True, comment="是否啟用")
    is_default = Column(Boolean, default=False, comment="是否為預設資料庫")
    last_tested_at = Column(DateTime, nullable=True, comment="最後測試時間")
    test_status = Column(Enum(TestStatus), default=TestStatus.NEVER_TESTED, comment="測試狀態")
    test_error_message = Column(Text, comment="測試錯誤訊息")
    created_at = Column(DateTime, default=func.now(), comment="創建時間")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新時間")
    
    # 關聯關係
    user = relationship("User", back_populates="database_configs")
    server = relationship("Server", back_populates="database_configs")
    test_logs = relationship("ConnectionTestLog", back_populates="database_config", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DatabaseConfig(id={self.id}, name='{self.config_name}', host='{self.host}')>"

class ConnectionTestLog(Base):
    """連接測試日誌模型"""
    __tablename__ = "connection_test_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(Integer, ForeignKey("database_configs.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    test_type = Column(Enum(TestType), nullable=False, comment="測試類型")
    status = Column(Enum(TestResult), nullable=False, comment="測試結果")
    response_time_ms = Column(Integer, nullable=True, comment="響應時間(毫秒)")
    error_message = Column(Text, nullable=True, comment="錯誤訊息")
    error_code = Column(String(50), nullable=True, comment="錯誤代碼")
    tested_at = Column(DateTime, default=func.now(), comment="測試時間")
    
    # 關聯關係
    database_config = relationship("DatabaseConfig", back_populates="test_logs")
    user = relationship("User")
    
    def __repr__(self):
        return f"<ConnectionTestLog(id={self.id}, status='{self.status}', tested_at='{self.tested_at}')>"

# Pydantic 模型
class DatabaseConfigBase(BaseModel):
    server_id: int = Field(..., example=1)
    config_name: str = Field(..., example="主資料庫")
    host: str = Field(..., example="localhost")
    port: int = Field(..., example=3306)
    database_name: str = Field(..., example="test_db")
    username: str = Field(..., example="root")
    password: str = Field(..., example="password")
    db_type: DatabaseType = Field(..., example=DatabaseType.MYSQL)
    connection_string: Optional[str] = Field(None, example="mysql+pymysql://root:password@localhost:3306/test_db")
    is_active: bool = Field(True, example=True)
    is_default: bool = Field(False, example=False)
    
    class Config:
        json_schema_extra = {
            "example": {
                "server_id": 1,
                "config_name": "主資料庫",
                "host": "localhost",
                "port": 3306,
                "database_name": "test_db",
                "username": "root",
                "password": "password",
                "db_type": "MYSQL",
                "connection_string": "mysql+pymysql://root:password@localhost:3306/test_db",
                "is_active": True,
                "is_default": False
            }
        }

class DatabaseConfigCreate(DatabaseConfigBase):
    pass

class DatabaseConfigUpdate(BaseModel):
    config_name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    db_type: Optional[DatabaseType] = None
    connection_string: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None

class DatabaseConfigResponse(BaseModel):
    id: int
    user_id: int
    server_id: int
    config_name: str
    host: str
    port: int
    database_name: str
    username: str
    password: str = Field(default="", exclude=True)  # 不返回密碼
    db_type: DatabaseType
    connection_string: Optional[str]
    is_active: bool
    is_default: bool
    last_tested_at: Optional[datetime]
    test_status: TestStatus
    test_error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "server_id": 1,
                "config_name": "主資料庫",
                "host": "localhost",
                "port": 3306,
                "database_name": "test_db",
                "username": "root",
                "password": "",
                "db_type": "MYSQL",
                "connection_string": "mysql+pymysql://root:password@localhost:3306/test_db",
                "is_active": True,
                "is_default": False,
                "last_tested_at": None,
                "test_status": "NEVER_TESTED",
                "test_error_message": None,
                "created_at": "2023-01-01T12:00:00",
                "updated_at": "2023-01-01T12:00:00"
            }
        }

class DatabaseConfigListResponse(BaseModel):
    total: int
    configs: List[DatabaseConfigResponse]
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 1,
                "configs": [
                    {
                        "id": 1,
                        "user_id": 1,
                        "server_id": 1,
                        "config_name": "主資料庫",
                        "host": "localhost",
                        "port": 3306,
                        "database_name": "test_db",
                        "username": "root",
                        "password": "",
                        "db_type": "MYSQL",
                        "connection_string": "mysql+pymysql://root:password@localhost:3306/test_db",
                        "is_active": True,
                        "is_default": False,
                        "last_tested_at": None,
                        "test_status": "NEVER_TESTED",
                        "test_error_message": None,
                        "created_at": "2023-01-01T12:00:00",
                        "updated_at": "2023-01-01T12:00:00"
                    }
                ]
            }
        }

class DatabaseConfigTestRequest(BaseModel):
    config_name: str = Field(..., example="主資料庫")
    host: str = Field(..., example="localhost")
    port: int = Field(..., example=3306)
    database_name: str = Field(..., example="test_db")
    username: str = Field(..., example="root")
    password: str = Field(..., example="password")
    db_type: DatabaseType = Field(..., example=DatabaseType.MYSQL)
    connection_string: Optional[str] = Field(None, example="mysql+pymysql://root:password@localhost:3306/test_db")
    
    class Config:
        json_schema_extra = {
            "example": {
                "config_name": "主資料庫",
                "host": "localhost",
                "port": 3306,
                "database_name": "test_db",
                "username": "root",
                "password": "password",
                "db_type": "MYSQL",
                "connection_string": "mysql+pymysql://root:password@localhost:3306/test_db"
            }
        }

class DatabaseConfigTestResponse(BaseModel):
    success: bool
    message: str
    response_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "連接測試成功",
                "response_time_ms": 150,
                "error_message": None,
                "error_code": None
            }
        }
