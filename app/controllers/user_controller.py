"""
用戶控制器
"""
from typing import List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, UserCreate, UserResponse, UserStatusUpdate
from app.services.user_service import UserService
from app.core.dependencies import get_current_user

class UserController:
    """用戶控制器"""
    
    def __init__(self):
        self.user_service = UserService()
    
    def create_user(self, db: Session, user_data: UserCreate) -> UserResponse:
        """創建新用戶"""
        try:
            # 檢查密碼強度
            from app.core.security import is_password_strong
            is_strong, message = is_password_strong(user_data.password)
            if not is_strong:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=message
                )
            
            user = self.user_service.create_user(
                db=db,
                username=user_data.username,
                email=user_data.email,
                phone=user_data.phone,
                password=user_data.password
            )
            
            return UserResponse.from_orm(user)
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="創建用戶時發生錯誤"
            )
    
    def get_users(self, db: Session, current_user: User, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """獲取用戶列表"""
        try:
            users = self.user_service.get_all(db, skip, limit)
            return [UserResponse.from_orm(user) for user in users]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="獲取用戶列表時發生錯誤"
            )
    
    def get_user_by_id(self, db: Session, user_id: int) -> UserResponse:
        """根據 ID 獲取用戶"""
        try:
            user = self.user_service.get_by_id(db, user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用戶不存在"
                )
            return UserResponse.from_orm(user)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="獲取用戶信息時發生錯誤"
            )
    
    def update_user(self, db: Session, user_id: int, user_data: UserCreate, current_user: User) -> UserResponse:
        """更新用戶信息"""
        try:
            # 檢查權限（只有管理員或用戶本人可以更新）
            if current_user.id != user_id and not self._is_admin(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="無權限更新此用戶信息"
                )
            
            # 檢查用戶是否存在
            user = self.user_service.get_by_id(db, user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用戶不存在"
                )
            
            # 更新用戶信息
            update_data = {
                "username": user_data.username,
                "email": user_data.email,
                "phone": user_data.phone
            }
            
            updated_user = self.user_service.update(db, user_id, **update_data)
            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用戶不存在"
                )
            
            return UserResponse.from_orm(updated_user)
            
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新用戶信息時發生錯誤"
            )
    
    def delete_user(self, db: Session, user_id: int, current_user: User) -> Dict[str, str]:
        """刪除用戶"""
        try:
            # 檢查權限（只有管理員可以刪除用戶）
            if not self._is_admin(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="無權限刪除用戶"
                )
            
            # 不能刪除自己
            if current_user.id == user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不能刪除自己的帳號"
                )
            
            success = self.user_service.delete(db, user_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用戶不存在"
                )
            
            return {"message": "用戶刪除成功"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="刪除用戶時發生錯誤"
            )
    
    def update_user_status(self, db: Session, user_id: int, status_data: UserStatusUpdate, 
                          current_user: User) -> UserResponse:
        """更新用戶狀態"""
        try:
            # 檢查權限（只有管理員可以更新用戶狀態）
            if not self._is_admin(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="無權限更新用戶狀態"
                )
            
            # 不能修改自己的狀態
            if current_user.id == user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不能修改自己的狀態"
                )
            
            updated_user = self.user_service.update(db, user_id, status=status_data.status)
            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用戶不存在"
                )
            
            return UserResponse.from_orm(updated_user)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新用戶狀態時發生錯誤"
            )
    
    def get_active_users(self, db: Session, current_user: User, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """獲取活躍用戶列表"""
        try:
            # 檢查權限（只有管理員可以查看）
            if not self._is_admin(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="無權限查看用戶列表"
                )
            
            users = self.user_service.get_active_users(db, skip, limit)
            return [UserResponse.from_orm(user) for user in users]
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="獲取活躍用戶列表時發生錯誤"
            )
    
    def get_locked_users(self, db: Session, current_user: User, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """獲取被鎖定的用戶列表"""
        try:
            # 檢查權限（只有管理員可以查看）
            if not self._is_admin(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="無權限查看用戶列表"
                )
            
            users = self.user_service.get_locked_users(db, skip, limit)
            return [UserResponse.from_orm(user) for user in users]
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="獲取被鎖定用戶列表時發生錯誤"
            )
    
    def _is_admin(self, user: User) -> bool:
        """檢查用戶是否為管理員"""
        # 這裡可以根據角色系統來判斷
        # 暫時簡單判斷用戶名包含 admin
        return "admin" in user.username.lower()

