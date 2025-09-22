#!/usr/bin/env python3
"""
檢查資料庫類型
"""
import sys
import os

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

def check_database_type():
    """檢查資料庫類型"""
    print("🗄️  檢查資料庫配置...")
    print("=" * 60)
    
    print(f"資料庫URL: {settings.DATABASE_URL}")
    
    if "postgresql" in settings.DATABASE_URL or "postgres" in settings.DATABASE_URL:
        print("資料庫類型: PostgreSQL")
    elif "sqlite" in settings.DATABASE_URL:
        print("資料庫類型: SQLite")
    elif "mysql" in settings.DATABASE_URL:
        print("資料庫類型: MySQL")
    else:
        print("資料庫類型: 未知")
    
    print("=" * 60)

if __name__ == "__main__":
    check_database_type()
