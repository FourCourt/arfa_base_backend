#!/usr/bin/env python3
"""
檢查資料庫狀態
"""
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

# 創建數據庫引擎
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_database():
    """檢查資料庫狀態"""
    print("🗄️  檢查資料庫狀態...")
    print("=" * 60)
    
    try:
        db = SessionLocal()
        
        # 檢查所有表
        print("\n📋 資料庫表列表:")
        print("-" * 30)
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = result.fetchall()
        for (table_name,) in tables:
            print(f"✅ {table_name}")
        
        # 檢查用戶表數據
        print("\n👤 用戶數據:")
        print("-" * 30)
        result = db.execute(text("SELECT id, username, email, password_hash FROM users;"))
        users = result.fetchall()
        for user in users:
            print(f"ID: {user[0]}, 用戶名: {user[1]}, 郵箱: {user[2]}, 密碼哈希: {user[3][:20]}...")
        
        # 檢查角色表數據
        print("\n🎭 角色數據:")
        print("-" * 30)
        result = db.execute(text("SELECT id, code, name FROM roles;"))
        roles = result.fetchall()
        for role in roles:
            print(f"ID: {role[0]}, 代碼: {role[1]}, 名稱: {role[2]}")
        
        # 檢查權限表數據
        print("\n🔐 權限數據:")
        print("-" * 30)
        result = db.execute(text("SELECT id, code, name FROM permissions;"))
        permissions = result.fetchall()
        for perm in permissions:
            print(f"ID: {perm[0]}, 代碼: {perm[1]}, 名稱: {perm[2]}")
        
        # 檢查用戶角色關聯
        print("\n👤🎭 用戶角色關聯:")
        print("-" * 30)
        result = db.execute(text("SELECT ur.user_id, ur.role_id, u.username, r.name FROM user_roles ur JOIN users u ON ur.user_id = u.id JOIN roles r ON ur.role_id = r.id;"))
        user_roles = result.fetchall()
        for ur in user_roles:
            print(f"用戶: {ur[2]} -> 角色: {ur[3]}")
        
        # 檢查角色權限關聯
        print("\n🎭🔐 角色權限關聯:")
        print("-" * 30)
        result = db.execute(text("SELECT rp.role_id, rp.permission_id, r.name, p.name FROM role_permissions rp JOIN roles r ON rp.role_id = r.id JOIN permissions p ON rp.permission_id = p.id;"))
        role_permissions = result.fetchall()
        for rp in role_permissions:
            print(f"角色: {rp[2]} -> 權限: {rp[3]}")
        
        print("\n🎉 資料庫檢查完成!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 資料庫檢查失敗: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    check_database()
