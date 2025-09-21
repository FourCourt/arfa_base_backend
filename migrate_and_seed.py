#!/usr/bin/env python3
"""
Migration 和 Seeder 執行腳本
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
    echo=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_migrations_table(db: Session):
    """創建 migrations 表"""
    sql = """
    CREATE TABLE IF NOT EXISTS migrations (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        version VARCHAR(10) NOT NULL UNIQUE,
        description TEXT,
        executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_version (version),
        INDEX idx_executed_at (executed_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    db.execute(text(sql))
    db.commit()

def create_all_tables(db: Session):
    """創建所有業務表"""
    
    # 創建用戶表
    sql = """
    CREATE TABLE IF NOT EXISTS users (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(255),
        phone VARCHAR(20),
        password_hash VARBINARY(255) NOT NULL,
        password_salt VARBINARY(32) NOT NULL,
        password_iters SMALLINT NOT NULL DEFAULT 100000,
        status TINYINT NOT NULL DEFAULT 1,
        failed_login_count TINYINT NOT NULL DEFAULT 0,
        last_login_at TIMESTAMP NULL,
        last_login_ip VARBINARY(16),
        mfa_enabled BOOLEAN NOT NULL DEFAULT FALSE,
        password_reset_token VARCHAR(255),
        password_reset_expires TIMESTAMP NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_username (username),
        INDEX idx_email (email),
        INDEX idx_phone (phone),
        INDEX idx_status (status),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    db.execute(text(sql))
    db.commit()
    
    # 創建角色表
    sql = """
    CREATE TABLE IF NOT EXISTS roles (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        code VARCHAR(50) NOT NULL UNIQUE,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        status TINYINT NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_code (code),
        INDEX idx_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    db.execute(text(sql))
    db.commit()
    
    # 創建權限表
    sql = """
    CREATE TABLE IF NOT EXISTS permissions (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        code VARCHAR(50) NOT NULL UNIQUE,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_code (code)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    db.execute(text(sql))
    db.commit()
    
    # 創建用戶角色關聯表
    sql = """
    CREATE TABLE IF NOT EXISTS user_roles (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        user_id BIGINT NOT NULL,
        role_id BIGINT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY unique_user_role (user_id, role_id),
        INDEX idx_user_id (user_id),
        INDEX idx_role_id (role_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    db.execute(text(sql))
    db.commit()
    
    # 創建角色權限關聯表
    sql = """
    CREATE TABLE IF NOT EXISTS role_permissions (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        role_id BIGINT NOT NULL,
        permission_id BIGINT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY unique_role_permission (role_id, permission_id),
        INDEX idx_role_id (role_id),
        INDEX idx_permission_id (permission_id),
        FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
        FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    db.execute(text(sql))
    db.commit()
    
    # 創建項目表
    sql = """
    CREATE TABLE IF NOT EXISTS items (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        price DECIMAL(10,2),
        owner_id BIGINT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_owner_id (owner_id),
        INDEX idx_title (title),
        INDEX idx_price (price),
        INDEX idx_created_at (created_at),
        FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    db.execute(text(sql))
    db.commit()
    
    # 創建用戶會話表
    sql = """
    CREATE TABLE IF NOT EXISTS user_sessions (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        user_id BIGINT NOT NULL,
        session_id VARCHAR(255) NOT NULL UNIQUE,
        token_signature VARCHAR(255) NOT NULL,
        ip VARBINARY(16),
        user_agent VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        revoked_at TIMESTAMP NULL,
        INDEX idx_user_id (user_id),
        INDEX idx_session_id (session_id),
        INDEX idx_created_at (created_at),
        INDEX idx_revoked_at (revoked_at),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    db.execute(text(sql))
    db.commit()
    
    # 創建登入日誌表
    sql = """
    CREATE TABLE IF NOT EXISTS user_login_events (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        user_id BIGINT,
        succeeded BOOLEAN NOT NULL,
        reason TINYINT NOT NULL,
        ip VARBINARY(16),
        user_agent VARCHAR(255),
        occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_user_id (user_id),
        INDEX idx_succeeded (succeeded),
        INDEX idx_occurred_at (occurred_at),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    db.execute(text(sql))
    db.commit()
    
    # 創建密碼重設表
    sql = """
    CREATE TABLE IF NOT EXISTS password_resets (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        user_id BIGINT NOT NULL,
        token_hash VARCHAR(255) NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        used_at TIMESTAMP NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_user_id (user_id),
        INDEX idx_token_hash (token_hash),
        INDEX idx_expires_at (expires_at),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    db.execute(text(sql))
    db.commit()

def create_admin_role(db: Session):
    """創建管理員角色"""
    # 檢查角色是否已存在
    result = db.execute(text("SELECT COUNT(*) FROM roles WHERE code = 'admin'"))
    if result.scalar() > 0:
        print("✅ 管理員角色已存在")
        return
    
    sql = """
    INSERT INTO roles (code, name, description, status, created_at, updated_at)
    VALUES ('admin', '系統管理員', '擁有系統所有權限的管理員角色', 1, NOW(), NOW())
    """
    db.execute(text(sql))
    db.commit()
    print("✅ 管理員角色創建成功")

def create_permissions(db: Session):
    """創建權限數據"""
    permissions = [
        ("user.create", "創建用戶", "可以創建新用戶"),
        ("user.read", "查看用戶", "可以查看用戶信息"),
        ("user.update", "更新用戶", "可以更新用戶信息"),
        ("user.delete", "刪除用戶", "可以刪除用戶"),
        ("user.manage", "管理用戶", "可以管理所有用戶"),
        ("item.create", "創建項目", "可以創建新項目"),
        ("item.read", "查看項目", "可以查看項目信息"),
        ("item.update", "更新項目", "可以更新項目信息"),
        ("item.delete", "刪除項目", "可以刪除項目"),
        ("item.manage", "管理項目", "可以管理所有項目"),
        ("role.create", "創建角色", "可以創建新角色"),
        ("role.read", "查看角色", "可以查看角色信息"),
        ("role.update", "更新角色", "可以更新角色信息"),
        ("role.delete", "刪除角色", "可以刪除角色"),
        ("role.manage", "管理角色", "可以管理所有角色"),
        ("permission.create", "創建權限", "可以創建新權限"),
        ("permission.read", "查看權限", "可以查看權限信息"),
        ("permission.update", "更新權限", "可以更新權限信息"),
        ("permission.delete", "刪除權限", "可以刪除權限"),
        ("permission.manage", "管理權限", "可以管理所有權限"),
        ("system.admin", "系統管理", "擁有系統管理權限"),
        ("system.logs", "查看日誌", "可以查看系統日誌"),
        ("system.settings", "系統設置", "可以修改系統設置"),
    ]
    
    created_count = 0
    for code, name, description in permissions:
        # 檢查權限是否已存在
        result = db.execute(text("SELECT COUNT(*) FROM permissions WHERE code = :code"), {"code": code})
        if result.scalar() > 0:
            continue
        
        sql = """
        INSERT INTO permissions (code, name, description, created_at, updated_at)
        VALUES (:code, :name, :description, NOW(), NOW())
        """
        db.execute(text(sql), {"code": code, "name": name, "description": description})
        created_count += 1
    
    db.commit()
    print(f"✅ 權限創建完成，新增 {created_count} 個權限")

def create_admin_user(db: Session):
    """創建管理員用戶"""
    # 檢查管理員用戶是否已存在
    result = db.execute(text("SELECT COUNT(*) FROM users WHERE username = 'admin'"))
    if result.scalar() > 0:
        print("✅ 管理員用戶已存在")
        return
    
    # 創建密碼哈希
    password_hash, password_salt, password_iters = create_password_hash("Admin123!@#")
    
    # 創建管理員用戶
    sql = """
    INSERT INTO users (username, email, phone, password_hash, password_salt, password_iters, status, created_at, updated_at)
    VALUES ('admin', 'admin@arfa.com', '+886912345678', :password_hash, :password_salt, :password_iters, 1, NOW(), NOW())
    """
    db.execute(text(sql), {
        "password_hash": password_hash,
        "password_salt": password_salt,
        "password_iters": password_iters
    })
    db.commit()
    print("✅ 管理員用戶創建成功")

def assign_admin_permissions(db: Session):
    """為管理員角色分配所有權限"""
    # 獲取管理員角色 ID
    result = db.execute(text("SELECT id FROM roles WHERE code = 'admin'"))
    admin_role_id = result.scalar()
    
    if not admin_role_id:
        print("❌ 管理員角色不存在")
        return
    
    # 獲取所有權限 ID
    result = db.execute(text("SELECT id FROM permissions"))
    permission_ids = [row[0] for row in result.fetchall()]
    
    if not permission_ids:
        print("❌ 沒有權限數據")
        return
    
    # 為管理員角色分配所有權限
    assigned_count = 0
    for permission_id in permission_ids:
        # 檢查是否已分配
        result = db.execute(text("SELECT COUNT(*) FROM role_permissions WHERE role_id = :role_id AND permission_id = :permission_id"), {
            "role_id": admin_role_id,
            "permission_id": permission_id
        })
        if result.scalar() > 0:
            continue
        
        sql = """
        INSERT INTO role_permissions (role_id, permission_id, created_at)
        VALUES (:role_id, :permission_id, NOW())
        """
        db.execute(text(sql), {"role_id": admin_role_id, "permission_id": permission_id})
        assigned_count += 1
    
    db.commit()
    print(f"✅ 管理員權限分配完成，分配了 {assigned_count} 個權限")

def assign_admin_role_to_user(db: Session):
    """為管理員用戶分配管理員角色"""
    # 獲取管理員用戶 ID
    result = db.execute(text("SELECT id FROM users WHERE username = 'admin'"))
    admin_user_id = result.scalar()
    
    if not admin_user_id:
        print("❌ 管理員用戶不存在")
        return
    
    # 獲取管理員角色 ID
    result = db.execute(text("SELECT id FROM roles WHERE code = 'admin'"))
    admin_role_id = result.scalar()
    
    if not admin_role_id:
        print("❌ 管理員角色不存在")
        return
    
    # 檢查是否已分配
    result = db.execute(text("SELECT COUNT(*) FROM user_roles WHERE user_id = :user_id AND role_id = :role_id"), {
        "user_id": admin_user_id,
        "role_id": admin_role_id
    })
    if result.scalar() > 0:
        print("✅ 管理員用戶角色已分配")
        return
    
    # 分配角色
    sql = """
    INSERT INTO user_roles (user_id, role_id, created_at)
    VALUES (:user_id, :role_id, NOW())
    """
    db.execute(text(sql), {"user_id": admin_user_id, "role_id": admin_role_id})
    db.commit()
    print("✅ 管理員用戶角色分配完成")

def setup_database():
    """設置數據庫"""
    print("🗄️  開始設置數據庫...")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # 1. 創建 migrations 表
        print("\n📋 步驟 1: 創建 migrations 表")
        print("-" * 30)
        create_migrations_table(db)
        
        # 2. 創建所有業務表
        print("\n📋 步驟 2: 創建所有業務表")
        print("-" * 30)
        create_all_tables(db)
        
        # 3. 創建管理員角色
        print("\n📋 步驟 3: 創建管理員角色")
        print("-" * 30)
        create_admin_role(db)
        
        # 4. 創建權限數據
        print("\n📋 步驟 4: 創建權限數據")
        print("-" * 30)
        create_permissions(db)
        
        # 5. 創建管理員用戶
        print("\n📋 步驟 5: 創建管理員用戶")
        print("-" * 30)
        create_admin_user(db)
        
        # 6. 為管理員角色分配權限
        print("\n📋 步驟 6: 為管理員角色分配權限")
        print("-" * 30)
        assign_admin_permissions(db)
        
        # 7. 為管理員用戶分配角色
        print("\n📋 步驟 7: 為管理員用戶分配角色")
        print("-" * 30)
        assign_admin_role_to_user(db)
        
        print("\n" + "=" * 60)
        print("🎉 數據庫設置完成！")
        print("\n📊 創建的內容:")
        print("• 所有數據庫表")
        print("• 管理員角色 (admin)")
        print("• 完整的權限系統")
        print("• 管理員用戶 (admin)")
        print("• 管理員權限分配")
        
        print("\n🔑 管理員登入信息:")
        print("• 用戶名: admin")
        print("• 密碼: Admin123!@#")
        print("• 郵箱: admin@arfa.com")
        
        print("\n🌐 可以訪問:")
        print("• API 文檔: http://localhost:8000/docs")
        print("• 健康檢查: http://localhost:8000/health")
        
    except Exception as e:
        print(f"\n❌ 數據庫設置失敗: {str(e)}")
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    setup_database()

