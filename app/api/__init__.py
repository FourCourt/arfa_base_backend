from fastapi import APIRouter
from app.api.endpoints import users, auth, database_configs, servers

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["User Management"])
api_router.include_router(servers.router, prefix="/servers", tags=["Server Management"])
api_router.include_router(database_configs.router, prefix="/database-configs", tags=["Database Configuration"])
