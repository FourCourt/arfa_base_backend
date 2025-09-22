#!/usr/bin/env python3
"""
修正登入事件表
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

def fix_login_events_table():
    """修正登入事件表"""
    print("🔧 修正登入事件表...")
    print("=" * 60)
    
    try:
        db = SessionLocal()
        
        # 檢查是否存在 user_login_events 表
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='user_login_events';"))
        table_exists = result.fetchone()
        
        if not table_exists:
            print("❌ user_login_events 表不存在，正在創建...")
            
            # 創建 user_login_events 表
            sql = """
            CREATE TABLE user_login_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                succeeded BOOLEAN NOT NULL,
                reason INTEGER NOT NULL,
                ip BLOB,
                user_agent VARCHAR(255),
                occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
            db.execute(text(sql))
            db.commit()
            print("✅ user_login_events 表已創建!")
        else:
            print("✅ user_login_events 表已存在")
        
        # 檢查是否存在 login_logs 表
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='login_logs';"))
        login_logs_exists = result.fetchone()
        
        if login_logs_exists:
            print("⚠️  發現舊的 login_logs 表，正在遷移數據...")
            
            # 遷移數據從 login_logs 到 user_login_events
            sql = """
            INSERT INTO user_login_events (user_id, succeeded, reason, ip, user_agent, occurred_at)
            SELECT user_id, succeeded, reason, ip, user_agent, occurred_at
            FROM login_logs
            WHERE NOT EXISTS (
                SELECT 1 FROM user_login_events 
                WHERE user_login_events.user_id = login_logs.user_id 
                AND user_login_events.occurred_at = login_logs.occurred_at
            )
            """
            db.execute(text(sql))
            db.commit()
            print("✅ 數據遷移完成!")
            
            # 刪除舊的 login_logs 表
            db.execute(text("DROP TABLE login_logs"))
            db.commit()
            print("✅ 舊的 login_logs 表已刪除!")
        
        print("\n🎉 登入事件表修正完成!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 表修正失敗: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    fix_login_events_table()
