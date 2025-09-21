"""
安全相關工具函數
"""
from datetime import datetime, timedelta
from typing import Optional, Union, Tuple
import secrets
import hashlib
import os
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.core.config import settings

# 密碼加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_salt() -> bytes:
    """生成密碼鹽值"""
    return os.urandom(32)

def hash_password_with_salt(password: str, salt: bytes, iterations: int = 100000) -> bytes:
    """使用鹽值和迭代次數生成密碼哈希"""
    password_bytes = password.encode('utf-8')
    hash_result = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, iterations)
    return hash_result

def verify_password_with_salt(password: str, salt: bytes, password_hash: bytes, iterations: int) -> bool:
    """驗證密碼（使用鹽值）"""
    computed_hash = hash_password_with_salt(password, salt, iterations)
    return computed_hash == password_hash

def create_password_hash(password: str) -> Tuple[bytes, bytes, int]:
    """創建密碼哈希，返回 (hash, salt, iterations)"""
    salt = generate_salt()
    iterations = 100000
    password_hash = hash_password_with_salt(password, salt, iterations)
    return password_hash, salt, iterations

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證密碼（bcrypt 兼容）"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密碼哈希（bcrypt 兼容）"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """創建訪問令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """驗證令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def generate_password_reset_token() -> str:
    """生成密碼重設令牌"""
    return secrets.token_urlsafe(32)

def generate_csrf_token() -> str:
    """生成 CSRF 令牌"""
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    """對令牌進行哈希處理"""
    return hashlib.sha256(token.encode()).hexdigest()

def is_password_strong(password: str) -> Tuple[bool, str]:
    """檢查密碼強度"""
    if len(password) < 8:
        return False, "密碼長度至少需要8個字符"
    
    if not any(c.isupper() for c in password):
        return False, "密碼需要包含至少一個大寫字母"
    
    if not any(c.islower() for c in password):
        return False, "密碼需要包含至少一個小寫字母"
    
    if not any(c.isdigit() for c in password):
        return False, "密碼需要包含至少一個數字"
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "密碼需要包含至少一個特殊字符"
    
    return True, "密碼強度符合要求"
