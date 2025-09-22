#!/usr/bin/env python3
"""
將數據從 test 資料庫遷移到 arfa 資料庫
"""
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# PostgreSQL 連接配置
POSTGRES_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'lazyadmin',
    'password': '2djixxjl'
}

def migrate_to_arfa_db():
    """遷移數據到 arfa 資料庫"""
    print("🔄 開始遷移數據到 arfa 資料庫...")
    print("=" * 60)
    
    try:
        # 連接 test 資料庫
        print("📱 連接 test 資料庫...")
        test_url = f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/test"
        test_engine = create_engine(test_url)
        test_session = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)()
        
        # 連接 arfa 資料庫
        print("🐘 連接 arfa 資料庫...")
        arfa_url = f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/arfa"
        arfa_engine = create_engine(arfa_url)
        arfa_session = sessionmaker(autocommit=False, autoflush=False, bind=arfa_engine)()
        
        # 創建 arfa 資料庫表結構
        print("🏗️  創建 arfa 資料庫表結構...")
        create_arfa_tables(arfa_session)
        
        # 遷移數據
        print("📦 開始遷移數據...")
        
        # 1. 遷移用戶數據
        migrate_table_data(test_session, arfa_session, "users")
        
        # 2. 遷移角色數據
        migrate_table_data(test_session, arfa_session, "roles")
        
        # 3. 遷移權限數據
        migrate_table_data(test_session, arfa_session, "permissions")
        
        # 4. 遷移用戶角色關聯
        migrate_table_data(test_session, arfa_session, "user_roles")
        
        # 5. 遷移角色權限關聯
        migrate_table_data(test_session, arfa_session, "role_permissions")
        
        # 6. 遷移用戶會話
        migrate_table_data(test_session, arfa_session, "user_sessions")
        
        # 7. 遷移登入事件
        migrate_table_data(test_session, arfa_session, "user_login_events")
        
        # 8. 遷移密碼重置
        migrate_table_data(test_session, arfa_session, "password_resets")
        
        arfa_session.commit()
        print("\n✅ 數據遷移到 arfa 資料庫完成!")
        print("=" * 60)
        
        # 驗證遷移結果
        verify_arfa_migration(arfa_session)
        
    except Exception as e:
        print(f"❌ 遷移失敗: {e}")
        raise e
    finally:
        if 'test_session' in locals():
            test_session.close()
        if 'arfa_session' in locals():
            arfa_session.close()

def create_arfa_tables(db):
    """創建 arfa 資料庫表結構"""
    
    # 刪除現有表（如果存在）
    tables_to_drop = [
        'password_resets', 'user_login_events', 'user_sessions', 
        'role_permissions', 'user_roles', 'permissions', 'roles', 'users'
    ]
    
    for table in tables_to_drop:
        db.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
    
    # 創建用戶表
    db.execute(text("""
        CREATE TABLE users (
            id BIGSERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(255) UNIQUE,
            phone VARCHAR(20),
            password_hash BYTEA NOT NULL,
            password_salt BYTEA NOT NULL,
            password_iters INTEGER NOT NULL DEFAULT 100000,
            status INTEGER NOT NULL DEFAULT 1,
            failed_login_count INTEGER NOT NULL DEFAULT 0,
            last_login_at TIMESTAMP,
            last_login_ip INET,
            mfa_enabled BOOLEAN NOT NULL DEFAULT FALSE,
            password_reset_token VARCHAR(255),
            password_reset_expires TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # 創建角色表
    db.execute(text("""
        CREATE TABLE roles (
            id BIGSERIAL PRIMARY KEY,
            code VARCHAR(50) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            status INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # 創建權限表
    db.execute(text("""
        CREATE TABLE permissions (
            id BIGSERIAL PRIMARY KEY,
            code VARCHAR(50) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # 創建用戶角色關聯表
    db.execute(text("""
        CREATE TABLE user_roles (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role_id BIGINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, role_id)
        )
    """))
    
    # 創建角色權限關聯表
    db.execute(text("""
        CREATE TABLE role_permissions (
            id BIGSERIAL PRIMARY KEY,
            role_id BIGINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
            permission_id BIGINT NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(role_id, permission_id)
        )
    """))
    
    # 創建用戶會話表
    db.execute(text("""
        CREATE TABLE user_sessions (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            session_id VARCHAR(64) NOT NULL UNIQUE,
            token_signature VARCHAR(64) NOT NULL,
            ip INET,
            user_agent VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen_at TIMESTAMP,
            revoked_at TIMESTAMP
        )
    """))
    
    # 創建登入事件表
    db.execute(text("""
        CREATE TABLE user_login_events (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            succeeded BOOLEAN NOT NULL,
            reason INTEGER NOT NULL,
            ip INET,
            user_agent VARCHAR(255),
            occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # 創建密碼重置表
    db.execute(text("""
        CREATE TABLE password_resets (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            token VARCHAR(255) NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    db.commit()
    print("✅ arfa 資料庫表結構創建完成")

def migrate_table_data(source_db, target_db, table_name):
    """遷移表數據"""
    print(f"📦 遷移 {table_name} 表數據...")
    
    # 獲取源表數據
    result = source_db.execute(text(f"SELECT * FROM {table_name}"))
    rows = result.fetchall()
    
    if not rows:
        print(f"⚠️  {table_name} 表無數據")
        return
    
    # 獲取列名
    columns = result.keys()
    column_names = ', '.join(columns)
    placeholders = ', '.join([f':{col}' for col in columns])
    
    # 插入數據到目標表
    sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
    
    for row in rows:
        row_dict = dict(zip(columns, row))
        target_db.execute(text(sql), row_dict)
    
    print(f"✅ 遷移了 {len(rows)} 條 {table_name} 記錄")

def verify_arfa_migration(db):
    """驗證 arfa 資料庫遷移結果"""
    print("\n🔍 驗證 arfa 資料庫遷移結果...")
    print("-" * 50)
    
    tables = ['users', 'roles', 'permissions', 'user_roles', 'role_permissions', 
              'user_sessions', 'user_login_events', 'password_resets']
    
    for table in tables:
        result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
        count = result.fetchone()[0]
        print(f"📊 {table}: {count} 條記錄")
    
    print("\n✅ arfa 資料庫遷移驗證完成!")

if __name__ == "__main__":
    migrate_to_arfa_db()
