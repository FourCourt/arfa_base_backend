from fastapi import APIRouter
from app.api.endpoints import users, items, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["認證"])
api_router.include_router(users.router, prefix="/users", tags=["用戶管理"])
api_router.include_router(items.router, prefix="/items", tags=["項目管理"])
