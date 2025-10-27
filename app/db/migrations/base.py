"""
Migration 基礎類
"""
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db import engine
from app.core.config import settings

class BaseMigration:
    """Migration 基礎類"""
    
    def __init__(self):
        self.version = "000"
        self.description = "Base Migration"
        self.created_at = datetime.utcnow()
    
    def up(self, db: Session):
        """執行 migration"""
        raise NotImplementedError("子類必須實現 up 方法")
    
    def down(self, db: Session):
        """回滾 migration"""
        raise NotImplementedError("子類必須實現 down 方法")
    
    def execute_sql(self, db: Session, sql: str, params: Dict[str, Any] = None):
        """執行 SQL 語句"""
        try:
            if params:
                db.execute(text(sql), params)
            else:
                db.execute(text(sql))
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
    
    def table_exists(self, db: Session, table_name: str) -> bool:
        """檢查表是否存在"""
        if settings.DATABASE_URL.startswith("mysql"):
            result = db.execute(text(f"""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = '{table_name}'
            """))
        elif settings.DATABASE_URL.startswith("postgresql"):
            result = db.execute(text(f"""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = '{table_name}'
            """))
        else:
            # SQLite
            result = db.execute(text(f"""
                SELECT COUNT(*) 
                FROM sqlite_master 
                WHERE type='table' 
                AND name='{table_name}'
            """))
        
        return result.scalar() > 0
    
    def column_exists(self, db: Session, table_name: str, column_name: str) -> bool:
        """檢查欄位是否存在"""
        if settings.DATABASE_URL.startswith("mysql"):
            result = db.execute(text(f"""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = DATABASE() 
                AND table_name = '{table_name}'
                AND column_name = '{column_name}'
            """))
        elif settings.DATABASE_URL.startswith("postgresql"):
            result = db.execute(text(f"""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = '{table_name}'
                AND column_name = '{column_name}'
            """))
        else:
            # SQLite
            result = db.execute(text(f"""
                PRAGMA table_info({table_name})
            """))
            columns = result.fetchall()
            for column in columns:
                if column[1] == column_name:  # column[1] 是欄位名
                    return True
            return False
        
        return result.scalar() > 0