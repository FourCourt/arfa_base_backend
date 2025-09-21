"""
創建權限數據
"""
from app.database.seeders.base import BaseSeeder

class CreatePermissionsSeeder(BaseSeeder):
    """創建權限 seeder"""
    
    def __init__(self):
        super().__init__()
        self.name = "CreatePermissionsSeeder"
        self.description = "Create permissions"
    
    def run(self, db):
        """創建權限"""
        
        permissions = [
            {"code": "user.create", "name": "創建用戶", "description": "可以創建新用戶"},
            {"code": "user.read", "name": "查看用戶", "description": "可以查看用戶信息"},
            {"code": "user.update", "name": "更新用戶", "description": "可以更新用戶信息"},
            {"code": "user.delete", "name": "刪除用戶", "description": "可以刪除用戶"},
            {"code": "user.manage", "name": "管理用戶", "description": "可以管理所有用戶"},
            
            {"code": "item.create", "name": "創建項目", "description": "可以創建新項目"},
            {"code": "item.read", "name": "查看項目", "description": "可以查看項目信息"},
            {"code": "item.update", "name": "更新項目", "description": "可以更新項目信息"},
            {"code": "item.delete", "name": "刪除項目", "description": "可以刪除項目"},
            {"code": "item.manage", "name": "管理項目", "description": "可以管理所有項目"},
            
            {"code": "role.create", "name": "創建角色", "description": "可以創建新角色"},
            {"code": "role.read", "name": "查看角色", "description": "可以查看角色信息"},
            {"code": "role.update", "name": "更新角色", "description": "可以更新角色信息"},
            {"code": "role.delete", "name": "刪除角色", "description": "可以刪除角色"},
            {"code": "role.manage", "name": "管理角色", "description": "可以管理所有角色"},
            
            {"code": "permission.create", "name": "創建權限", "description": "可以創建新權限"},
            {"code": "permission.read", "name": "查看權限", "description": "可以查看權限信息"},
            {"code": "permission.update", "name": "更新權限", "description": "可以更新權限信息"},
            {"code": "permission.delete", "name": "刪除權限", "description": "可以刪除權限"},
            {"code": "permission.manage", "name": "管理權限", "description": "可以管理所有權限"},
            
            {"code": "system.admin", "name": "系統管理", "description": "擁有系統管理權限"},
            {"code": "system.logs", "name": "查看日誌", "description": "可以查看系統日誌"},
            {"code": "system.settings", "name": "系統設置", "description": "可以修改系統設置"},
        ]
        
        created_count = 0
        for perm in permissions:
            # 檢查權限是否已存在
            if self.record_exists(db, "permissions", {"code": perm["code"]}):
                continue
            
            sql = """
            INSERT INTO permissions (code, name, description, created_at, updated_at)
            VALUES (:code, :name, :description, :created_at, :updated_at)
            """
            
            params = {
                "code": perm["code"],
                "name": perm["name"],
                "description": perm["description"],
                "created_at": self.created_at,
                "updated_at": self.created_at
            }
            
            self.execute_sql(db, sql, params)
            created_count += 1
        
        print(f"✅ 權限創建完成，新增 {created_count} 個權限")
    
    def rollback(self, db):
        """回滾 seeder"""
        sql = "DELETE FROM permissions WHERE code LIKE '%'"
        self.execute_sql(db, sql)
        print("✅ 所有權限已刪除")
