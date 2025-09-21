"""
會話管理相關功能
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user_session import UserSession
from app.core.security import hash_token

def create_user_session(user, access_token: str, ip_address: Optional[str], 
                       user_agent: Optional[str], db: Session) -> UserSession:
    """創建用戶會話"""
    session_id = hash_token(access_token)[:32]  # 使用令牌哈希的前32位作為會話ID
    token_signature = hash_token(access_token)
    
    # 轉換 IP 地址為二進制
    ip_binary = None
    if ip_address:
        import socket
        try:
            if ':' in ip_address:  # IPv6
                ip_binary = socket.inet_pton(socket.AF_INET6, ip_address)
            else:  # IPv4
                ip_binary = socket.inet_pton(socket.AF_INET, ip_address)
        except socket.error:
            pass
    
    session = UserSession(
        user_id=user.id,
        session_id=session_id,
        token_signature=token_signature,
        ip=ip_binary,
        user_agent=user_agent[:255] if user_agent else None,
        created_at=datetime.utcnow(),
        last_seen_at=datetime.utcnow()
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session

def revoke_user_sessions(user_id: int, db: Session):
    """撤銷用戶的所有會話"""
    sessions = db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.revoked_at.is_(None)
    ).all()
    
    for session in sessions:
        session.revoked_at = datetime.utcnow()
    
    db.commit()

def revoke_session(session_id: str, db: Session):
    """撤銷特定會話"""
    session = db.query(UserSession).filter(
        UserSession.session_id == session_id,
        UserSession.revoked_at.is_(None)
    ).first()
    
    if session:
        session.revoked_at = datetime.utcnow()
        db.commit()

def is_session_valid(session_id: str, db: Session) -> bool:
    """檢查會話是否有效"""
    session = db.query(UserSession).filter(
        UserSession.session_id == session_id,
        UserSession.revoked_at.is_(None)
    ).first()
    
    if not session:
        return False
    
    # 檢查會話是否過期（例如30天）
    if session.last_seen_at < datetime.utcnow() - timedelta(days=30):
        session.revoked_at = datetime.utcnow()
        db.commit()
        return False
    
    # 更新最後訪問時間
    session.last_seen_at = datetime.utcnow()
    db.commit()
    
    return True

def update_session_activity(session_id: str, db: Session):
    """更新會話活動時間"""
    session = db.query(UserSession).filter(
        UserSession.session_id == session_id,
        UserSession.revoked_at.is_(None)
    ).first()
    
    if session:
        session.last_seen_at = datetime.utcnow()
        db.commit()