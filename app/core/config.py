from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import validator
import os
from app.core.environments import get_config, get_environment

class Settings(BaseSettings):
    PROJECT_NAME: str = "LAZY API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # Database - 根據環境自動選擇
    DATABASE_URL: str = get_config().get("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/lazy_db")
    
    # Security
    SECRET_KEY: str = get_config().get("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: bool = get_config().get("DEBUG", True)
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = get_config().get("CORS_ORIGINS", ["http://localhost:3000", "http://localhost:8080"])
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
