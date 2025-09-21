"""
基礎 Service 類
"""
from typing import Type, TypeVar, Generic, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.db import get_db

T = TypeVar('T')

class BaseService(Generic[T]):
    """基礎 Service 類，提供通用的 CRUD 操作"""
    
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class
    
    def create(self, db: Session, **kwargs) -> T:
        """創建記錄"""
        obj = self.model_class(**kwargs)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    
    def get_by_id(self, db: Session, id: int) -> Optional[T]:
        """根據 ID 獲取記錄"""
        return db.query(self.model_class).filter(self.model_class.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[T]:
        """獲取所有記錄"""
        return db.query(self.model_class).offset(skip).limit(limit).all()
    
    def update(self, db: Session, id: int, **kwargs) -> Optional[T]:
        """更新記錄"""
        obj = db.query(self.model_class).filter(self.model_class.id == id).first()
        if obj:
            for key, value in kwargs.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            db.commit()
            db.refresh(obj)
        return obj
    
    def delete(self, db: Session, id: int) -> bool:
        """刪除記錄"""
        obj = db.query(self.model_class).filter(self.model_class.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False
    
    def count(self, db: Session) -> int:
        """統計記錄數量"""
        return db.query(self.model_class).count()
    
    def exists(self, db: Session, id: int) -> bool:
        """檢查記錄是否存在"""
        return db.query(self.model_class).filter(self.model_class.id == id).first() is not None
