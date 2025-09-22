#!/usr/bin/env python3
"""
將 SQLite 數據遷移到 PostgreSQL
"""
import sys
import os
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.security import create_password_hash

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# PostgreSQL 連接配置
POSTGRES_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'test',
    'user': 'lazyadmin',
    'password': '2djixxjl'
}

# SQLite 配置
SQLITE_URL = "sqlite:///./app.db"

def migrate_to_postgresql():
    """遷移數據到 PostgreSQL"""
    print("🔄 開始遷移 SQLite 數據到 PostgreSQL...")
    print("=" * 80)
    
    try:
        # 連接 SQLite
        print("📱 連接 SQLite 數據庫...")
        sqlite_engine = create_engine(SQLITE_URL)
        sqlite_session = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)()
        
        # 連接 PostgreSQL
        print("🐘 連接 PostgreSQL 數據庫...")
        postgres_url = f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}"
        postgres_engine = create_engine(postgres_url)
        postgres_session = sessionmaker(autocommit=False, autoflush=False, bind=postgres_engine)()
        
        # 創建 PostgreSQL 表
        print("🏗️  創建 PostgreSQL 表結構...")
        create_postgresql_tables(postgres_session)
        
        # 遷移數據
        print("📦 開始遷移數據...")
        
        # 1. 遷移用戶數據
        migrate_users(sqlite_session, postgres_session)
        
        # 2. 遷移角色數據
        migrate_roles(sqlite_session, postgres_session)
        
        # 3. 遷移權限數據
        migrate_permissions(sqlite_session, postgres_session)
        
        # 4. 遷移用戶角色關聯
        migrate_user_roles(sqlite_session, postgres_session)
        
        # 5. 遷移角色權限關聯
        migrate_role_permissions(sqlite_session, postgres_session)
        
        # 6. 遷移用戶會話
        migrate_user_sessions(sqlite_session, postgres_session)
        
        # 7. 遷移登入事件
        migrate_login_events(sqlite_session, postgres_session)
        
        # 8. 遷移密碼重置
        migrate_password_resets(sqlite_session, postgres_session)
        
        postgres_session.commit()
        print("\n✅ 數據遷移完成!")
        print("=" * 80)
        
        # 驗證遷移結果
        verify_migration(postgres_session)
        
    except Exception as e:
        print(f"❌ 遷移失敗: {e}")
        raise e
    finally:
        if 'sqlite_session' in locals():
            sqlite_session.close()
        if 'postgres_session' in locals():
            postgres_session.close()

def create_postgresql_tables(db):
    """創建 PostgreSQL 表結構"""
    
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
    print("✅ PostgreSQL 表結構創建完成")

def migrate_users(sqlite_db, postgres_db):
    """遷移用戶數據"""
    print("👤 遷移用戶數據...")
    
    result = sqlite_db.execute(text("SELECT * FROM users"))
    users = result.fetchall()
    
    for user in users:
        # 處理密碼哈希（從十六進制字符串轉換為字節）
        password_hash_hex = user[4]  # password_hash 欄位
        password_salt_hex = user[5]  # password_salt 欄位
        
        # 如果是字符串，轉換為字節
        if isinstance(password_hash_hex, str):
            password_hash = bytes.fromhex(password_hash_hex)
        else:
            password_hash = password_hash_hex
            
        if isinstance(password_salt_hex, str):
            password_salt = bytes.fromhex(password_salt_hex)
        else:
            password_salt = password_salt_hex
        
        # 處理 IP 地址
        last_login_ip = user[10]  # last_login_ip 欄位
        if isinstance(last_login_ip, bytes):
            # 將字節轉換為 IP 地址字符串
            try:
                ip_str = '.'.join(map(str, last_login_ip))
            except:
                ip_str = None
        else:
            ip_str = last_login_ip
        
        sql = """
        INSERT INTO users (id, username, email, phone, password_hash, password_salt, 
                          password_iters, status, failed_login_count, last_login_at, 
                          last_login_ip, mfa_enabled, password_reset_token, 
                          password_reset_expires, created_at, updated_at)
        VALUES (:id, :username, :email, :phone, :password_hash, :password_salt,
                :password_iters, :status, :failed_login_count, :last_login_at,
                :last_login_ip, :mfa_enabled, :password_reset_token,
                :password_reset_expires, :created_at, :updated_at)
        """
        
        postgres_db.execute(text(sql), {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'phone': user[3],
            'password_hash': password_hash,
            'password_salt': password_salt,
            'password_iters': user[6],
            'status': user[7],
            'failed_login_count': user[8],
            'last_login_at': user[9],
            'last_login_ip': ip_str,
            'mfa_enabled': bool(user[11]),
            'password_reset_token': user[12],
            'password_reset_expires': user[13],
            'created_at': user[14],
            'updated_at': user[15]
        })
    
    print(f"✅ 遷移了 {len(users)} 個用戶")

def migrate_roles(sqlite_db, postgres_db):
    """遷移角色數據"""
    print("🎭 遷移角色數據...")
    
    result = sqlite_db.execute(text("SELECT * FROM roles"))
    roles = result.fetchall()
    
    for role in roles:
        sql = """
        INSERT INTO roles (id, code, name, description, status, created_at, updated_at)
        VALUES (:id, :code, :name, :description, :status, :created_at, :updated_at)
        """
        
        postgres_db.execute(text(sql), {
            'id': role[0],
            'code': role[1],
            'name': role[2],
            'description': role[3],
            'status': role[4],
            'created_at': role[5],
            'updated_at': role[6]
        })
    
    print(f"✅ 遷移了 {len(roles)} 個角色")

def migrate_permissions(sqlite_db, postgres_db):
    """遷移權限數據"""
    print("🔐 遷移權限數據...")
    
    result = sqlite_db.execute(text("SELECT * FROM permissions"))
    permissions = result.fetchall()
    
    for perm in permissions:
        sql = """
        INSERT INTO permissions (id, code, name, description, created_at, updated_at)
        VALUES (:id, :code, :name, :description, :created_at, :updated_at)
        """
        
        postgres_db.execute(text(sql), {
            'id': perm[0],
            'code': perm[1],
            'name': perm[2],
            'description': perm[3],
            'created_at': perm[4],
            'updated_at': perm[5]
        })
    
    print(f"✅ 遷移了 {len(permissions)} 個權限")

def migrate_user_roles(sqlite_db, postgres_db):
    """遷移用戶角色關聯"""
    print("👤🎭 遷移用戶角色關聯...")
    
    result = sqlite_db.execute(text("SELECT * FROM user_roles"))
    user_roles = result.fetchall()
    
    for ur in user_roles:
        sql = """
        INSERT INTO user_roles (id, user_id, role_id, created_at)
        VALUES (:id, :user_id, :role_id, :created_at)
        """
        
        postgres_db.execute(text(sql), {
            'id': ur[0],
            'user_id': ur[1],
            'role_id': ur[2],
            'created_at': ur[3]
        })
    
    print(f"✅ 遷移了 {len(user_roles)} 個用戶角色關聯")

def migrate_role_permissions(sqlite_db, postgres_db):
    """遷移角色權限關聯"""
    print("🎭🔐 遷移角色權限關聯...")
    
    result = sqlite_db.execute(text("SELECT * FROM role_permissions"))
    role_permissions = result.fetchall()
    
    for rp in role_permissions:
        sql = """
        INSERT INTO role_permissions (id, role_id, permission_id, created_at)
        VALUES (:id, :role_id, :permission_id, :created_at)
        """
        
        postgres_db.execute(text(sql), {
            'id': rp[0],
            'role_id': rp[1],
            'permission_id': rp[2],
            'created_at': rp[3]
        })
    
    print(f"✅ 遷移了 {len(role_permissions)} 個角色權限關聯")

def migrate_user_sessions(sqlite_db, postgres_db):
    """遷移用戶會話"""
    print("🔑 遷移用戶會話...")
    
    result = sqlite_db.execute(text("SELECT * FROM user_sessions"))
    sessions = result.fetchall()
    
    for session in sessions:
        # 處理 IP 地址
        ip_data = session[4]  # ip 欄位
        if isinstance(ip_data, bytes):
            # 將字節轉換為 IP 地址字符串
            try:
                ip_str = '.'.join(map(str, ip_data))
            except:
                ip_str = None
        else:
            ip_str = ip_data
        
        sql = """
        INSERT INTO user_sessions (id, user_id, session_id, token_signature, 
                                  ip, user_agent, created_at, last_seen_at, revoked_at)
        VALUES (:id, :user_id, :session_id, :token_signature,
                :ip, :user_agent, :created_at, :last_seen_at, :revoked_at)
        """
        
        postgres_db.execute(text(sql), {
            'id': session[0],
            'user_id': session[1],
            'session_id': session[2],
            'token_signature': session[3],
            'ip': ip_str,
            'user_agent': session[5],
            'created_at': session[6],
            'last_seen_at': session[7],
            'revoked_at': session[8]
        })
    
    print(f"✅ 遷移了 {len(sessions)} 個用戶會話")

def migrate_login_events(sqlite_db, postgres_db):
    """遷移登入事件"""
    print("📝 遷移登入事件...")
    
    result = sqlite_db.execute(text("SELECT * FROM user_login_events"))
    events = result.fetchall()
    
    for event in events:
        # 處理 IP 地址
        ip_data = event[4]  # ip 欄位
        if isinstance(ip_data, bytes):
            # 將字節轉換為 IP 地址字符串
            try:
                ip_str = '.'.join(map(str, ip_data))
            except:
                ip_str = None
        else:
            ip_str = ip_data
        
        sql = """
        INSERT INTO user_login_events (id, user_id, succeeded, reason, 
                                      ip, user_agent, occurred_at)
        VALUES (:id, :user_id, :succeeded, :reason,
                :ip, :user_agent, :occurred_at)
        """
        
        postgres_db.execute(text(sql), {
            'id': event[0],
            'user_id': event[1],
            'succeeded': bool(event[2]),
            'reason': event[3],
            'ip': ip_str,
            'user_agent': event[5],
            'occurred_at': event[6]
        })
    
    print(f"✅ 遷移了 {len(events)} 個登入事件")

def migrate_password_resets(sqlite_db, postgres_db):
    """遷移密碼重置"""
    print("🔒 遷移密碼重置...")
    
    result = sqlite_db.execute(text("SELECT * FROM password_resets"))
    resets = result.fetchall()
    
    for reset in resets:
        sql = """
        INSERT INTO password_resets (id, user_id, token, expires_at, used, created_at)
        VALUES (:id, :user_id, :token, :expires_at, :used, :created_at)
        """
        
        postgres_db.execute(text(sql), {
            'id': reset[0],
            'user_id': reset[1],
            'token': reset[2],
            'expires_at': reset[3],
            'used': bool(reset[4]),
            'created_at': reset[5]
        })
    
    print(f"✅ 遷移了 {len(resets)} 個密碼重置記錄")

def verify_migration(db):
    """驗證遷移結果"""
    print("\n🔍 驗證遷移結果...")
    print("-" * 50)
    
    tables = ['users', 'roles', 'permissions', 'user_roles', 'role_permissions', 
              'user_sessions', 'user_login_events', 'password_resets']
    
    for table in tables:
        result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
        count = result.fetchone()[0]
        print(f"📊 {table}: {count} 條記錄")
    
    print("\n✅ 遷移驗證完成!")

if __name__ == "__main__":
    migrate_to_postgresql()
