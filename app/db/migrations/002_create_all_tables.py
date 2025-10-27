"""
創建所有業務表
"""
from app.db.migrations.base import BaseMigration

class CreateAllTables(BaseMigration):
    """創建所有業務表"""
    
    def __init__(self):
        super().__init__()
        self.version = "002"
        self.description = "Create all business tables"
    
    def up(self, db):
        """創建所有表"""
        from app.core.config import settings
        
        if "sqlite" in settings.DATABASE_URL:
            # 使用 SQLAlchemy ORM 創建表
            from app.models import Base
            Base.metadata.create_all(bind=db.bind)
        else:
            # MySQL 語法
            self.create_mysql_tables(db)
    
    def create_mysql_tables(self, db):
        """創建 MySQL 表"""
        # 創建用戶表
        if not self.table_exists(db, "users"):
            self.create_users_table(db)
        
        # 創建角色表
        if not self.table_exists(db, "roles"):
            self.create_roles_table(db)
        
        # 創建權限表
        if not self.table_exists(db, "permissions"):
            self.create_permissions_table(db)
        
        # 創建用戶角色關聯表
        if not self.table_exists(db, "user_roles"):
            self.create_user_roles_table(db)
        
        # 創建角色權限關聯表
        if not self.table_exists(db, "role_permissions"):
            self.create_role_permissions_table(db)
        
        # 創建用戶會話表
        if not self.table_exists(db, "user_sessions"):
            self.create_user_sessions_table(db)
        
        # 創建登入日誌表
        if not self.table_exists(db, "user_login_events"):
            self.create_user_login_events_table(db)
        
        # 創建密碼重設表
        if not self.table_exists(db, "password_resets"):
            self.create_password_resets_table(db)
    
    def down(self, db):
        """刪除所有表"""
        tables = [
            "password_resets",
            "user_login_events", 
            "user_sessions",
            "role_permissions",
            "user_roles",
            "permissions",
            "roles",
            "users"
        ]
        
        for table in tables:
            sql = f"DROP TABLE IF EXISTS {table}"
            self.execute_sql(db, sql)
    
    def create_users_table(self, db):
        """創建用戶表"""
        sql = """
        CREATE TABLE users (
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
        self.execute_sql(db, sql)
    
    
    def create_roles_table(self, db):
        """創建角色表"""
        sql = """
        CREATE TABLE roles (
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
        self.execute_sql(db, sql)
    
    def create_permissions_table(self, db):
        """創建權限表"""
        sql = """
        CREATE TABLE permissions (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(50) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_code (code)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        self.execute_sql(db, sql)
    
    def create_user_roles_table(self, db):
        """創建用戶角色關聯表"""
        sql = """
        CREATE TABLE user_roles (
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
        self.execute_sql(db, sql)
    
    def create_role_permissions_table(self, db):
        """創建角色權限關聯表"""
        sql = """
        CREATE TABLE role_permissions (
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
        self.execute_sql(db, sql)
    
    def create_user_sessions_table(self, db):
        """創建用戶會話表"""
        sql = """
        CREATE TABLE user_sessions (
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
        self.execute_sql(db, sql)
    
    def create_user_login_events_table(self, db):
        """創建登入日誌表"""
        sql = """
        CREATE TABLE user_login_events (
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
        self.execute_sql(db, sql)
    
    def create_password_resets_table(self, db):
        """創建密碼重設表"""
        sql = """
        CREATE TABLE password_resets (
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
        self.execute_sql(db, sql)
