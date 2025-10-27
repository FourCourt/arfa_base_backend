"""
環境配置管理
支持開發環境 (XAMPP MySQL) 和生產環境 (PostgreSQL)
"""
import os
from typing import Dict

# 環境配置
ENVIRONMENT_CONFIGS = {
    "development": {
        "DATABASE_URL": "sqlite:///./lazy_dev.db",
        "DEBUG": True,
        "CORS_ORIGINS": ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"],
        "SECRET_KEY": "development-secret-key-change-in-production"
    },
    "production": {
        "DATABASE_URL": "postgresql://username:password@localhost:5432/lazy_db",
        "DEBUG": False,
        "CORS_ORIGINS": ["https://yourdomain.com", "https://www.yourdomain.com"],
        "SECRET_KEY": "your-production-secret-key-here"
    }
}

def get_environment() -> str:
    """獲取當前環境"""
    return os.getenv("ENVIRONMENT", "development")

def get_config() -> Dict[str, str]:
    """獲取當前環境的配置"""
    env = get_environment()
    return ENVIRONMENT_CONFIGS.get(env, ENVIRONMENT_CONFIGS["development"])

def is_development() -> bool:
    """檢查是否為開發環境"""
    return get_environment() == "development"

def is_production() -> bool:
    """檢查是否為生產環境"""
    return get_environment() == "production"




