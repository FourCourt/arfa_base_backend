from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.server import ServerCreate, ServerResponse, ServerUpdate, ServerListResponse
from app.services.server_service import ServerService

class ServerController:
    """伺服器控制器"""
    
    def __init__(self):
        self.server_service = ServerService()
    
    def create_server(self, db: Session, current_user: User, server_data: ServerCreate) -> ServerResponse:
        """創建新伺服器"""
        try:
            server = self.server_service.create_server(db=db, user_id=current_user.id, server_data=server_data)
            return ServerResponse.from_orm(server)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"創建伺服器時發生錯誤: {e}"
            )
    
    def get_user_servers(self, db: Session, current_user: User, skip: int = 0, limit: int = 100) -> ServerListResponse:
        """獲取使用者伺服器列表"""
        try:
            servers = self.server_service.get_user_servers(db, current_user.id, skip, limit)
            return ServerListResponse(total=len(servers), servers=[ServerResponse.from_orm(s) for s in servers])
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"獲取伺服器列表時發生錯誤: {e}"
            )
    
    def get_server_by_id(self, db: Session, server_id: int, current_user: User) -> ServerResponse:
        """根據ID獲取伺服器"""
        server = self.server_service.get_server_by_id(db, server_id, current_user.id)
        if not server:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="伺服器不存在或無權限訪問"
            )
        return ServerResponse.from_orm(server)
    
    def update_server(self, db: Session, server_id: int, current_user: User, server_data: ServerUpdate) -> ServerResponse:
        """更新伺服器信息"""
        try:
            updated_server = self.server_service.update_server(db, server_id, current_user.id, server_data)
            if not updated_server:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="伺服器不存在或無權限訪問"
                )
            return ServerResponse.from_orm(updated_server)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"更新伺服器時發生錯誤: {e}"
            )
    
    def delete_server(self, db: Session, server_id: int, current_user: User):
        """刪除伺服器"""
        try:
            success = self.server_service.delete_server(db, server_id, current_user.id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="伺服器不存在或無權限訪問"
                )
            return {"message": "伺服器刪除成功"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"刪除伺服器時發生錯誤: {e}"
            )
