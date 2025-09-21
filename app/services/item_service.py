"""
項目相關商務邏輯
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.item import Item
from app.models.user import User
from app.services.base_service import BaseService

class ItemService(BaseService[Item]):
    """項目服務類"""
    
    def __init__(self):
        super().__init__(Item)
    
    def create_item(self, db: Session, title: str, description: Optional[str], 
                   price: Optional[float], owner: User) -> Item:
        """創建新項目"""
        return self.create(
            db,
            title=title,
            description=description,
            price=price,
            owner_id=owner.id
        )
    
    def get_user_items(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Item]:
        """獲取用戶的項目列表"""
        return db.query(Item).filter(
            Item.owner_id == user_id
        ).offset(skip).limit(limit).all()
    
    def update_user_item(self, db: Session, item_id: int, user_id: int, **kwargs) -> Optional[Item]:
        """更新用戶的項目"""
        item = db.query(Item).filter(
            Item.id == item_id,
            Item.owner_id == user_id
        ).first()
        
        if not item:
            return None
        
        return self.update(db, item_id, **kwargs)
    
    def delete_user_item(self, db: Session, item_id: int, user_id: int) -> bool:
        """刪除用戶的項目"""
        item = db.query(Item).filter(
            Item.id == item_id,
            Item.owner_id == user_id
        ).first()
        
        if not item:
            return False
        
        return self.delete(db, item_id)
    
    def search_items(self, db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Item]:
        """搜索項目"""
        return db.query(Item).filter(
            Item.title.contains(query) | Item.description.contains(query)
        ).offset(skip).limit(limit).all()
    
    def get_items_by_price_range(self, db: Session, min_price: float, max_price: float, 
                                skip: int = 0, limit: int = 100) -> List[Item]:
        """根據價格範圍獲取項目"""
        return db.query(Item).filter(
            Item.price >= min_price,
            Item.price <= max_price
        ).offset(skip).limit(limit).all()

