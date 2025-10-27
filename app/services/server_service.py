from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.server import Server, ServerCreate, ServerUpdate
from app.services.base_service import BaseService

class ServerService(BaseService[Server]):
    """伺服器服務"""
    
    def __init__(self):
        super().__init__(Server)
    
    def create_server(self, db: Session, user_id: int, server_data: ServerCreate) -> Server:
        """創建新伺服器"""
        # 檢查伺服器名稱是否已存在於該使用者下
        existing_server = db.query(Server).filter(
            and_(Server.user_id == user_id, Server.server_name == server_data.server_name)
        ).first()
        if existing_server:
            raise ValueError("伺服器名稱已存在")
        
        server = self.create(db, user_id=user_id, **server_data.dict())
        return server
    
    def get_user_servers(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Server]:
        """獲取使用者所有伺服器"""
        return db.query(Server).filter(Server.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_server_by_id(self, db: Session, server_id: int, user_id: int) -> Optional[Server]:
        """根據ID獲取伺服器，並驗證使用者權限"""
        return db.query(Server).filter(and_(Server.id == server_id, Server.user_id == user_id)).first()
    
    def update_server(self, db: Session, server_id: int, user_id: int, update_data: ServerUpdate) -> Optional[Server]:
        """更新伺服器信息"""
        server = self.get_server_by_id(db, server_id, user_id)
        if not server:
            return None
        
        # 檢查更新後的伺服器名稱是否與其他伺服器衝突
        if update_data.server_name and update_data.server_name != server.server_name:
            existing_server = db.query(Server).filter(
                and_(Server.user_id == user_id, Server.server_name == update_data.server_name, Server.id != server_id)
            ).first()
            if existing_server:
                raise ValueError("伺服器名稱已存在")
        
        updated_server = self.update(db, server_id, **update_data.dict(exclude_unset=True))
        return updated_server
    
    def delete_server(self, db: Session, server_id: int, user_id: int) -> bool:
        """刪除伺服器"""
        server = self.get_server_by_id(db, server_id, user_id)
        if not server:
            return False
        return self.delete(db, server_id)
