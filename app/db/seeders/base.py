"""
Seeder 基礎類
"""
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db import engine
from app.core.config import settings

class BaseSeeder:
    """Seeder 基礎類"""
    
    def __init__(self):
        self.name = "BaseSeeder"
        self.description = "Base Seeder"
        self.created_at = datetime.utcnow()
    
    def run(self, db: Session):
        """執行 seeder"""
        raise NotImplementedError("子類必須實現 run 方法")
    
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
    
    def record_exists(self, db: Session, table: str, conditions: Dict[str, Any]) -> bool:
        """檢查記錄是否存在"""
        where_clause = " AND ".join([f"{k} = :{k}" for k in conditions.keys()])
        sql = f"SELECT COUNT(*) FROM {table} WHERE {where_clause}"
        result = db.execute(text(sql), conditions)
        return result.scalar() > 0
