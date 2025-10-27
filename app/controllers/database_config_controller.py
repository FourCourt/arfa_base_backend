from typing import List, Dict, Any
from fastapi import HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.user import User
from app.models.database_config import (
    DatabaseConfigCreate, DatabaseConfigUpdate, DatabaseConfigResponse, 
    DatabaseConfigListResponse, DatabaseConfigTestRequest, DatabaseConfigTestResponse,
    TestStatus
)
from app.services.database_config_service import DatabaseConfigService
from app.services.server_service import ServerService

class DatabaseConfigController:
    """資料庫配置控制器"""
    
    def __init__(self):
        self.db_config_service = DatabaseConfigService()
        self.server_service = ServerService()
    
    def create_config(self, db: Session, current_user: User, config_data: DatabaseConfigCreate) -> DatabaseConfigResponse:
        """創建資料庫配置"""
        try:
            # 檢查伺服器是否屬於該使用者
            server = self.server_service.get_server_by_id(db, config_data.server_id, current_user.id)
            if not server:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="伺服器不存在或無權限訪問"
                )
            
            config = self.db_config_service.create_config(db=db, user_id=current_user.id, config_data=config_data)
            return DatabaseConfigResponse.from_orm(config)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"創建資料庫配置時發生錯誤: {e}"
            )
    
    def get_user_configs(self, db: Session, current_user: User, skip: int = 0, limit: int = 100) -> DatabaseConfigListResponse:
        """獲取使用者所有資料庫配置"""
        try:
            configs = self.db_config_service.get_user_configs(db, current_user.id, skip, limit)
            return DatabaseConfigListResponse(total=len(configs), configs=[DatabaseConfigResponse.from_orm(c) for c in configs])
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"獲取資料庫配置列表時發生錯誤: {e}"
            )
    
    def get_server_configs(self, db: Session, server_id: int, current_user: User, skip: int = 0, limit: int = 100) -> DatabaseConfigListResponse:
        """獲取指定伺服器的資料庫配置"""
        try:
            # 檢查伺服器是否屬於該使用者
            server = self.server_service.get_server_by_id(db, server_id, current_user.id)
            if not server:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="伺服器不存在或無權限訪問"
                )
            
            configs = self.db_config_service.get_server_configs(db, server_id, current_user.id, skip, limit)
            return DatabaseConfigListResponse(total=len(configs), configs=[DatabaseConfigResponse.from_orm(c) for c in configs])
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"獲取伺服器資料庫配置時發生錯誤: {e}"
            )
    
    def get_config_by_id(self, db: Session, config_id: int, current_user: User) -> DatabaseConfigResponse:
        """根據ID獲取資料庫配置"""
        config = self.db_config_service.get_config_by_id(db, config_id, current_user.id)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="資料庫配置不存在或無權限訪問"
            )
        return DatabaseConfigResponse.from_orm(config)
    
    def update_config(self, db: Session, config_id: int, current_user: User, config_data: DatabaseConfigUpdate) -> DatabaseConfigResponse:
        """更新資料庫配置"""
        try:
            updated_config = self.db_config_service.update_config(db, config_id, current_user.id, config_data)
            if not updated_config:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="資料庫配置不存在或無權限訪問"
                )
            return DatabaseConfigResponse.from_orm(updated_config)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"更新資料庫配置時發生錯誤: {e}"
            )
    
    def delete_config(self, db: Session, config_id: int, current_user: User):
        """刪除資料庫配置"""
        try:
            success = self.db_config_service.delete_config(db, config_id, current_user.id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="資料庫配置不存在或無權限訪問"
                )
            return {"message": "資料庫配置刪除成功"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"刪除資料庫配置時發生錯誤: {e}"
            )
    
    def get_default_config(self, db: Session, server_id: int, current_user: User) -> DatabaseConfigResponse:
        """獲取指定伺服器的預設資料庫配置"""
        try:
            # 檢查伺服器是否屬於該使用者
            server = self.server_service.get_server_by_id(db, server_id, current_user.id)
            if not server:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="伺服器不存在或無權限訪問"
                )
            
            config = self.db_config_service.get_default_config(db, server_id, current_user.id)
            if not config:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="該伺服器沒有預設資料庫配置"
                )
            
            return DatabaseConfigResponse.from_orm(config)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"獲取預設資料庫配置時發生錯誤: {e}"
            )
    
    def test_connection(self, db: Session, config_id: int, current_user: User) -> DatabaseConfigTestResponse:
        """測試資料庫連接（保存結果）"""
        try:
            result = self.db_config_service.test_connection(db, config_id, current_user.id)
            return DatabaseConfigTestResponse(**result)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"測試資料庫連接時發生錯誤: {e}"
            )
    
    def test_connection_without_save(self, test_data: DatabaseConfigTestRequest) -> DatabaseConfigTestResponse:
        """測試資料庫連接（不保存結果）"""
        try:
            result = self.db_config_service.test_connection_without_save(test_data.dict())
            return DatabaseConfigTestResponse(**result)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"測試資料庫連接時發生錯誤: {e}"
            )
