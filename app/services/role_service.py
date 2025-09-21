"""
角色相關商務邏輯
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.role import Role
from app.services.base_service import BaseService

class RoleService(BaseService[Role]):
    """角色服務類"""
    
    def __init__(self):
        super().__init__(Role)
    
    def get_by_code(self, db: Session, code: str) -> Optional[Role]:
        """根據代碼獲取角色"""
        return db.query(Role).filter(Role.code == code).first()
    
    def assign_role_to_user(self, db: Session, user_id: int, role_id: int) -> bool:
        """為用戶分配角色"""
        from app.models.user_role import UserRole
        
        # 檢查是否已分配
        existing = db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        ).first()
        
        if existing:
            return True
        
        # 創建新的用戶角色關聯
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id
        )
        
        db.add(user_role)
        db.commit()
        db.refresh(user_role)
        
        return True
    
    def remove_role_from_user(self, db: Session, user_id: int, role_id: int) -> bool:
        """移除用戶角色"""
        from app.models.user_role import UserRole
        
        user_role = db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        ).first()
        
        if not user_role:
            return False
        
        db.delete(user_role)
        db.commit()
        
        return True
    
    def get_user_roles(self, db: Session, user_id: int) -> List[Role]:
        """獲取用戶的角色列表"""
        from app.models.user_role import UserRole
        
        return db.query(Role).join(UserRole).filter(
            UserRole.user_id == user_id
        ).all()
    
    def get_active_roles(self, db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
        """獲取活躍角色列表"""
        return db.query(Role).filter(Role.status == 1).offset(skip).limit(limit).all()

