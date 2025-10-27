from typing import List
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.models.server import ServerCreate, ServerResponse, ServerUpdate, ServerListResponse
from app.core.dependencies import get_current_user
from app.controllers.server_controller import ServerController

router = APIRouter()
server_controller = ServerController()

@router.post("/", response_model=ServerResponse, summary="Create Server", description="Create a new server for the current user")
async def create_server(
    server: ServerCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new server"""
    return server_controller.create_server(db, current_user, server)

@router.get("/", response_model=ServerListResponse, summary="Get User Servers", description="Get list of servers owned by the current user")
async def get_user_servers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's servers list"""
    return server_controller.get_user_servers(db, current_user, skip, limit)

@router.get("/{server_id}", response_model=ServerResponse, summary="Get Server by ID", description="Get server information by ID (owned by current user)")
async def get_server(
    server_id: int = Path(..., description="伺服器ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get server by ID"""
    return server_controller.get_server_by_id(db, server_id, current_user)

@router.put("/{server_id}", response_model=ServerResponse, summary="Update Server", description="Update server information (owned by current user)")
async def update_server(
    server_id: int = Path(..., description="伺服器ID"),
    server_update: ServerUpdate = ...,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update server information"""
    return server_controller.update_server(db, server_id, current_user, server_update)

@router.delete("/{server_id}", summary="Delete Server", description="Delete server (owned by current user)")
async def delete_server(
    server_id: int = Path(..., description="伺服器ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete server"""
    return server_controller.delete_server(db, server_id, current_user)
