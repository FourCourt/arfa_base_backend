"""
創建 migrations 表
"""
from app.db.migrations.base import BaseMigration

class CreateMigrationsTable(BaseMigration):
    """創建 migrations 表"""
    
    def __init__(self):
        super().__init__()
        self.version = "001"
        self.description = "Create migrations table"
    
    def up(self, db):
        """創建 migrations 表"""
        # 檢查資料庫類型
        from app.core.config import settings
        
        if "sqlite" in settings.DATABASE_URL:
            # SQLite 語法
            sql = """
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version VARCHAR(10) NOT NULL UNIQUE,
                description TEXT,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        else:
            # MySQL 語法
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
        self.execute_sql(db, sql)
    
    def down(self, db):
        """刪除 migrations 表"""
        sql = "DROP TABLE IF EXISTS migrations"
        self.execute_sql(db, sql)