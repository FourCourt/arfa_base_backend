#!/usr/bin/env python3
"""
SQLite 資料庫設置腳本
"""
import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.security import create_password_hash

# 創建數據庫引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_all_tables(db: Session):
    """創建所有業務表 - SQLite版本"""
    
    # 創建用戶表
    sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(255),
        phone VARCHAR(20),
        password_hash VARCHAR(255) NOT NULL,
        password_salt VARCHAR(32) NOT NULL,
        password_iters INTEGER NOT NULL DEFAULT 100000,
        status INTEGER NOT NULL DEFAULT 1,
        failed_login_count INTEGER NOT NULL DEFAULT 0,
        last_login_at TIMESTAMP NULL,
        last_login_ip VARCHAR(16),
        mfa_enabled BOOLEAN NOT NULL DEFAULT FALSE,
        password_reset_token VARCHAR(255),
        password_reset_expires TIMESTAMP NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    db.execute(text(sql))
    db.commit()
    
    # 創建角色表
    sql = """
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code VARCHAR(50) NOT NULL UNIQUE,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        status INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    db.execute(text(sql))
    db.commit()
    
    # 創建權限表
    sql = """
    CREATE TABLE IF NOT EXISTS permissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code VARCHAR(50) NOT NULL UNIQUE,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    db.execute(text(sql))
    db.commit()
    
    # 創建用戶角色關聯表
    sql = """
    CREATE TABLE IF NOT EXISTS user_roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        role_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, role_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
    )
    """
    db.execute(text(sql))
    db.commit()
    
    # 創建角色權限關聯表
    sql = """
    CREATE TABLE IF NOT EXISTS role_permissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_id INTEGER NOT NULL,
        permission_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(role_id, permission_id),
        FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
        FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
    )
    """
    db.execute(text(sql))
    db.commit()
    
    # 創建用戶會話表
    sql = """
    CREATE TABLE IF NOT EXISTS user_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        session_token VARCHAR(255) NOT NULL UNIQUE,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """
    db.execute(text(sql))
    db.commit()
    
    # 創建登入日誌表
    sql = """
    CREATE TABLE IF NOT EXISTS login_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username VARCHAR(50),
        ip_address VARCHAR(16),
        user_agent TEXT,
        login_status VARCHAR(20) NOT NULL,
        failure_reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    )
    """
    db.execute(text(sql))
    db.commit()
    
    # 創建密碼重置表
    sql = """
    CREATE TABLE IF NOT EXISTS password_resets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token VARCHAR(255) NOT NULL UNIQUE,
        expires_at TIMESTAMP NOT NULL,
        used BOOLEAN NOT NULL DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """
    db.execute(text(sql))
    db.commit()

def seed_data(db: Session):
    """插入初始數據"""
    
    # 創建管理員角色
    sql = """
    INSERT OR IGNORE INTO roles (code, name, description, status) 
    VALUES ('admin', '管理員', '系統管理員角色', 1)
    """
    db.execute(text(sql))
    db.commit()
    
    # 創建基本權限
    permissions = [
        ('user.create', '創建用戶', '創建新用戶的權限'),
        ('user.read', '查看用戶', '查看用戶信息的權限'),
        ('user.update', '更新用戶', '更新用戶信息的權限'),
        ('user.delete', '刪除用戶', '刪除用戶的權限'),
        ('role.create', '創建角色', '創建新角色的權限'),
        ('role.read', '查看角色', '查看角色信息的權限'),
        ('role.update', '更新角色', '更新角色信息的權限'),
        ('role.delete', '刪除角色', '刪除角色的權限'),
        ('permission.manage', '管理權限', '管理系統權限的權限'),
        ('system.admin', '系統管理', '系統管理員權限')
    ]
    
    for code, name, description in permissions:
        sql = f"""
        INSERT OR IGNORE INTO permissions (code, name, description) 
        VALUES ('{code}', '{name}', '{description}')
        """
        db.execute(text(sql))
        db.commit()
    
    # 創建管理員用戶
    sql = """
    INSERT OR IGNORE INTO users (username, email, password_hash, password_salt, password_iters, status) 
    VALUES ('admin', 'admin@example.com', 'admin123', 'salt', 100000, 1)
    """
    db.execute(text(sql))
    db.commit()
    
    # 獲取管理員用戶ID和角色ID
    result = db.execute(text("SELECT id FROM users WHERE username = 'admin'")).fetchone()
    admin_user_id = result[0] if result else None
    
    result = db.execute(text("SELECT id FROM roles WHERE code = 'admin'")).fetchone()
    admin_role_id = result[0] if result else None
    
    if admin_user_id and admin_role_id:
        # 分配管理員角色
        sql = f"""
        INSERT OR IGNORE INTO user_roles (user_id, role_id) 
        VALUES ({admin_user_id}, {admin_role_id})
        """
        db.execute(text(sql))
        db.commit()
        
        # 分配所有權限給管理員角色
        result = db.execute(text("SELECT id FROM permissions")).fetchall()
        for (permission_id,) in result:
            sql = f"""
            INSERT OR IGNORE INTO role_permissions (role_id, permission_id) 
            VALUES ({admin_role_id}, {permission_id})
            """
            db.execute(text(sql))
            db.commit()

def setup_database():
    """設置資料庫"""
    print("🗄️  開始設置SQLite資料庫...")
    print("=" * 60)
    
    try:
        db = SessionLocal()
        
        print("\n📋 步驟 1: 創建所有資料表")
        print("-" * 30)
        create_all_tables(db)
        print("✅ 資料表創建完成")
        
        print("\n📋 步驟 2: 插入初始數據")
        print("-" * 30)
        seed_data(db)
        print("✅ 初始數據插入完成")
        
        print("\n🎉 資料庫設置完成!")
        print("=" * 60)
        print("管理員帳號: admin")
        print("管理員密碼: admin123")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 資料庫設置失敗: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    setup_database()
