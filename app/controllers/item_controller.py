"""
項目控制器
"""
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status, Query
from sqlalchemy.orm import Session
from app.models.item import Item, ItemCreate, ItemResponse
from app.models.user import User
from app.services.item_service import ItemService
from app.core.dependencies import get_current_user

class ItemController:
    """項目控制器"""
    
    def __init__(self):
        self.item_service = ItemService()
    
    def create_item(self, db: Session, item_data: ItemCreate, current_user: User) -> ItemResponse:
        """創建新項目"""
        try:
            item = self.item_service.create_item(
                db=db,
                title=item_data.title,
                description=item_data.description,
                price=item_data.price,
                owner=current_user
            )
            
            return ItemResponse.from_orm(item)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="創建項目時發生錯誤"
            )
    
    def get_items(self, db: Session, current_user: User, skip: int = 0, limit: int = 100) -> List[ItemResponse]:
        """獲取項目列表"""
        try:
            items = self.item_service.get_user_items(db, current_user.id, skip, limit)
            return [ItemResponse.from_orm(item) for item in items]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="獲取項目列表時發生錯誤"
            )
    
    def get_item_by_id(self, db: Session, item_id: int, current_user: User) -> ItemResponse:
        """根據 ID 獲取項目"""
        try:
            item = self.item_service.get_by_id(db, item_id)
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="項目不存在"
                )
            
            # 檢查權限（只有項目擁有者或管理員可以查看）
            if item.owner_id != current_user.id and not self._is_admin(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="無權限查看此項目"
                )
            
            return ItemResponse.from_orm(item)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="獲取項目信息時發生錯誤"
            )
    
    def update_item(self, db: Session, item_id: int, item_data: ItemCreate, current_user: User) -> ItemResponse:
        """更新項目"""
        try:
            updated_item = self.item_service.update_user_item(
                db=db,
                item_id=item_id,
                user_id=current_user.id,
                title=item_data.title,
                description=item_data.description,
                price=item_data.price
            )
            
            if not updated_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="項目不存在或無權限修改"
                )
            
            return ItemResponse.from_orm(updated_item)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新項目時發生錯誤"
            )
    
    def delete_item(self, db: Session, item_id: int, current_user: User) -> Dict[str, str]:
        """刪除項目"""
        try:
            success = self.item_service.delete_user_item(db, item_id, current_user.id)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="項目不存在或無權限刪除"
                )
            
            return {"message": "項目刪除成功"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="刪除項目時發生錯誤"
            )
    
    def search_items(self, db: Session, query: str, current_user: User, 
                    skip: int = 0, limit: int = 100) -> List[ItemResponse]:
        """搜索項目"""
        try:
            items = self.item_service.search_items(db, query, skip, limit)
            
            # 過濾結果（只返回用戶自己的項目，除非是管理員）
            if not self._is_admin(current_user):
                items = [item for item in items if item.owner_id == current_user.id]
            
            return [ItemResponse.from_orm(item) for item in items]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="搜索項目時發生錯誤"
            )
    
    def get_items_by_price_range(self, db: Session, min_price: float, max_price: float, 
                                current_user: User, skip: int = 0, limit: int = 100) -> List[ItemResponse]:
        """根據價格範圍獲取項目"""
        try:
            items = self.item_service.get_items_by_price_range(db, min_price, max_price, skip, limit)
            
            # 過濾結果（只返回用戶自己的項目，除非是管理員）
            if not self._is_admin(current_user):
                items = [item for item in items if item.owner_id == current_user.id]
            
            return [ItemResponse.from_orm(item) for item in items]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="獲取價格範圍項目時發生錯誤"
            )
    
    def get_all_items(self, db: Session, current_user: User, skip: int = 0, limit: int = 100) -> List[ItemResponse]:
        """獲取所有項目（管理員功能）"""
        try:
            # 檢查權限（只有管理員可以查看所有項目）
            if not self._is_admin(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="無權限查看所有項目"
                )
            
            items = self.item_service.get_all(db, skip, limit)
            return [ItemResponse.from_orm(item) for item in items]
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="獲取所有項目時發生錯誤"
            )
    
    def _is_admin(self, user: User) -> bool:
        """檢查用戶是否為管理員"""
        # 這裡可以根據角色系統來判斷
        # 暫時簡單判斷用戶名包含 admin
        return "admin" in user.username.lower()

