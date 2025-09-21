"""
創建管理員用戶
"""
from app.database.seeders.base import BaseSeeder
from app.core.security import create_password_hash
from app.services.user_service import UserService
from app.services.role_service import RoleService
from sqlalchemy import text

class CreateAdminUserSeeder(BaseSeeder):
    """創建管理員用戶 seeder"""
    
    def __init__(self):
        super().__init__()
        self.name = "CreateAdminUserSeeder"
        self.description = "Create admin user"
        self.user_service = UserService()
        self.role_service = RoleService()
    
    def run(self, db):
        """創建管理員用戶"""
        
        # 檢查管理員用戶是否已存在
        if self.record_exists(db, "users", {"username": "admin"}):
            print("管理員用戶已存在，跳過創建")
            return
        
        # 創建管理員用戶
        admin_user = self.user_service.create_user(
            db=db,
            username="admin",
            email="admin@arfa.com",
            phone="+886912345678",
            password="Admin123!@#"
        )
        
        # 獲取管理員角色
        admin_role = self.role_service.get_by_code(db, "admin")
        if not admin_role:
            raise Exception("管理員角色不存在，請先執行角色 seeder")
        
        # 分配管理員角色給用戶
        self.role_service.assign_role_to_user(db, admin_user.id, admin_role.id)
        
        print("✅ 管理員用戶創建成功")
        print(f"   用戶名: admin")
        print(f"   郵箱: admin@arfa.com")
        print(f"   密碼: Admin123!@#")
        print(f"   角色: 系統管理員")
    
    def rollback(self, db):
        """回滾 seeder"""
        sql = "DELETE FROM users WHERE username = 'admin'"
        self.execute_sql(db, sql)
        print("✅ 管理員用戶已刪除")
