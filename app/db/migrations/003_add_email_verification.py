"""
添加郵箱驗證功能
"""
from datetime import datetime
from app.db.migrations.base import BaseMigration

class AddEmailVerification(BaseMigration):
    """添加郵箱驗證功能"""
    
    version = "003"
    description = "添加郵箱驗證功能"
    created_at = datetime(2024, 1, 1, 12, 0, 0)
    
    def up(self, db):
        """執行遷移"""
        # 添加郵箱驗證相關欄位
        sql = """
        ALTER TABLE users 
        ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT FALSE,
        ADD COLUMN email_verification_token VARCHAR(255),
        ADD COLUMN email_verification_expires TIMESTAMP NULL,
        ADD INDEX idx_email_verified (email_verified),
        ADD INDEX idx_email_verification_token (email_verification_token)
        """
        self.execute_sql(db, sql)
        
        # 更新現有用戶為已驗證狀態（管理員用戶）
        sql = """
        UPDATE users 
        SET email_verified = TRUE 
        WHERE username = 'admin'
        """
        self.execute_sql(db, sql)
    
    def down(self, db):
        """回滾遷移"""
        # 移除郵箱驗證相關欄位
        sql = """
        ALTER TABLE users 
        DROP COLUMN email_verified,
        DROP COLUMN email_verification_token,
        DROP COLUMN email_verification_expires
        """
        self.execute_sql(db, sql)
