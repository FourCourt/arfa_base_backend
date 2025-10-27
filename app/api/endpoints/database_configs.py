from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.models.database_config import (
    DatabaseConfigCreate, DatabaseConfigUpdate, DatabaseConfigResponse, 
    DatabaseConfigListResponse, DatabaseConfigTestRequest, DatabaseConfigTestResponse
)
from app.core.dependencies import get_current_user
from app.controllers.database_config_controller import DatabaseConfigController

router = APIRouter()
db_config_controller = DatabaseConfigController()

@router.post("/servers/{server_id}/configs/", 
            response_model=DatabaseConfigResponse, 
            summary="Create Database Config", 
            description="Create a new database configuration for a server")
async def create_database_config(
    server_id: int = Path(..., description="伺服器ID"),
    config: DatabaseConfigCreate = ...,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new database configuration for a server"""
    # 確保 server_id 與請求體中的 server_id 一致
    if config.server_id != server_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL中的server_id與請求體中的server_id不一致"
        )
    
    return db_config_controller.create_config(db, current_user, config)

@router.get("/", 
           response_model=DatabaseConfigListResponse, 
           summary="Get User Database Configs", 
           description="Get all database configurations for the current user")
async def get_user_database_configs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all database configurations for the current user"""
    return db_config_controller.get_user_configs(db, current_user, skip, limit)

@router.get("/servers/{server_id}/configs/", 
           response_model=DatabaseConfigListResponse, 
           summary="Get Server Database Configs", 
           description="Get database configurations for a specific server")
async def get_server_database_configs(
    server_id: int = Path(..., description="伺服器ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get database configurations for a specific server"""
    return db_config_controller.get_server_configs(db, server_id, current_user, skip, limit)

@router.get("/{config_id}", 
           response_model=DatabaseConfigResponse, 
           summary="Get Database Config by ID", 
           description="Get database configuration by ID")
async def get_database_config(
    config_id: int = Path(..., description="資料庫配置ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get database configuration by ID"""
    return db_config_controller.get_config_by_id(db, config_id, current_user)

@router.put("/{config_id}", 
           response_model=DatabaseConfigResponse, 
           summary="Update Database Config", 
           description="Update database configuration")
async def update_database_config(
    config_id: int = Path(..., description="資料庫配置ID"),
    config_update: DatabaseConfigUpdate = ...,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update database configuration"""
    return db_config_controller.update_config(db, config_id, current_user, config_update)

@router.delete("/{config_id}", 
              summary="Delete Database Config", 
              description="Delete database configuration")
async def delete_database_config(
    config_id: int = Path(..., description="資料庫配置ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete database configuration"""
    return db_config_controller.delete_config(db, config_id, current_user)

@router.get("/servers/{server_id}/default/", 
           response_model=DatabaseConfigResponse, 
           summary="Get Default Database Config", 
           description="Get default database configuration for a server")
async def get_default_database_config(
    server_id: int = Path(..., description="伺服器ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get default database configuration for a server"""
    return db_config_controller.get_default_config(db, server_id, current_user)

@router.post("/{config_id}/test/", 
            response_model=DatabaseConfigTestResponse, 
            summary="Test Database Connection", 
            description="Test database connection and save result")
async def test_database_connection(
    config_id: int = Path(..., description="資料庫配置ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test database connection and save result"""
    return db_config_controller.test_connection(db, config_id, current_user)

@router.post("/test/", 
            response_model=DatabaseConfigTestResponse, 
            summary="Test Database Connection (No Save)", 
            description="Test database connection without saving result")
async def test_database_connection_without_save(
    test_data: DatabaseConfigTestRequest = ...,
    current_user: User = Depends(get_current_user)
):
    """Test database connection without saving result"""
    return db_config_controller.test_connection_without_save(test_data)