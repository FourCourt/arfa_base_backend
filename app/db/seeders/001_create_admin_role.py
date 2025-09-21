"""
創建管理員角色
"""
from app.database.seeders.base import BaseSeeder

class CreateAdminRoleSeeder(BaseSeeder):
    """創建管理員角色 seeder"""
    
    def __init__(self):
        super().__init__()
        self.name = "CreateAdminRoleSeeder"
        self.description = "Create admin role"
    
    def run(self, db):
        """創建管理員角色"""
        
        # 檢查角色是否已存在
        if self.record_exists(db, "roles", {"code": "admin"}):
            print("管理員角色已存在，跳過創建")
            return
        
        # 創建管理員角色
        sql = """
        INSERT INTO roles (code, name, description, status, created_at, updated_at)
        VALUES (:code, :name, :description, :status, :created_at, :updated_at)
        """
        
        params = {
            "code": "admin",
            "name": "系統管理員",
            "description": "擁有系統所有權限的管理員角色",
            "status": 1,
            "created_at": self.created_at,
            "updated_at": self.created_at
        }
        
        self.execute_sql(db, sql, params)
        print("✅ 管理員角色創建成功")
    
    def rollback(self, db):
        """回滾 seeder"""
        sql = "DELETE FROM roles WHERE code = 'admin'"
        self.execute_sql(db, sql)
        print("✅ 管理員角色已刪除")
