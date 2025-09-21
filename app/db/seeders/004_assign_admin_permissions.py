"""
為管理員角色分配所有權限
"""
from app.database.seeders.base import BaseSeeder
from sqlalchemy import text

class AssignAdminPermissionsSeeder(BaseSeeder):
    """為管理員角色分配權限 seeder"""
    
    def __init__(self):
        super().__init__()
        self.name = "AssignAdminPermissionsSeeder"
        self.description = "Assign all permissions to admin role"
    
    def run(self, db):
        """為管理員角色分配所有權限"""
        
        # 獲取管理員角色 ID
        admin_role_result = db.execute(text("SELECT id FROM roles WHERE code = 'admin'"))
        admin_role_id = admin_role_result.scalar()
        
        if not admin_role_id:
            print("管理員角色不存在，跳過權限分配")
            return
        
        # 獲取所有權限 ID
        permissions_result = db.execute(text("SELECT id FROM permissions"))
        permission_ids = [row[0] for row in permissions_result.fetchall()]
        
        if not permission_ids:
            print("沒有權限數據，跳過權限分配")
            return
        
        # 為管理員角色分配所有權限
        assigned_count = 0
        for permission_id in permission_ids:
            # 檢查是否已分配
            if self.record_exists(db, "role_permissions", {
                "role_id": admin_role_id,
                "permission_id": permission_id
            }):
                continue
            
            sql = """
            INSERT INTO role_permissions (role_id, permission_id, created_at)
            VALUES (:role_id, :permission_id, :created_at)
            """
            
            params = {
                "role_id": admin_role_id,
                "permission_id": permission_id,
                "created_at": self.created_at
            }
            
            self.execute_sql(db, sql, params)
            assigned_count += 1
        
        print(f"✅ 管理員權限分配完成，分配了 {assigned_count} 個權限")
    
    def rollback(self, db):
        """回滾 seeder"""
        # 獲取管理員角色 ID
        admin_role_result = db.execute(text("SELECT id FROM roles WHERE code = 'admin'"))
        admin_role_id = admin_role_result.scalar()
        
        if admin_role_id:
            sql = "DELETE FROM role_permissions WHERE role_id = :role_id"
            self.execute_sql(db, sql, {"role_id": admin_role_id})
            print("✅ 管理員權限已清空")
