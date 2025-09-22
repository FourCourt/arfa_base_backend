#!/usr/bin/env python3
"""
修正用戶會話表
"""
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

# 創建數據庫引擎
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fix_user_sessions_table():
    """修正用戶會話表"""
    print("🔧 修正用戶會話表...")
    print("=" * 60)
    
    try:
        db = SessionLocal()
        
        # 刪除舊的 user_sessions 表
        print("🗑️  刪除舊的 user_sessions 表...")
        db.execute(text("DROP TABLE IF EXISTS user_sessions"))
        db.commit()
        
        # 創建新的 user_sessions 表
        print("🆕 創建新的 user_sessions 表...")
        sql = """
        CREATE TABLE user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_id VARCHAR(64) NOT NULL UNIQUE,
            token_signature VARCHAR(64) NOT NULL,
            ip BLOB,
            user_agent VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen_at TIMESTAMP,
            revoked_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
        db.execute(text(sql))
        db.commit()
        
        print("✅ user_sessions 表已修正!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 表修正失敗: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    fix_user_sessions_table()
