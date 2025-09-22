#!/usr/bin/env python3
"""
檢查所有資料表結構
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

def check_all_tables():
    """檢查所有資料表結構"""
    print("🗄️  檢查所有資料表結構...")
    print("=" * 80)
    
    try:
        db = SessionLocal()
        
        # 獲取所有表名
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"))
        tables = [row[0] for row in result.fetchall()]
        
        print(f"📋 發現 {len(tables)} 個資料表:")
        print("-" * 50)
        
        for table_name in tables:
            print(f"\n🔍 檢查表: {table_name}")
            print("-" * 30)
            
            # 獲取表結構
            result = db.execute(text(f"PRAGMA table_info({table_name});"))
            columns = result.fetchall()
            
            print("欄位結構:")
            for col in columns:
                cid, name, type_name, notnull, default, pk = col
                pk_str = " (主鍵)" if pk else ""
                null_str = " NOT NULL" if notnull else ""
                default_str = f" DEFAULT {default}" if default else ""
                print(f"  - {name}: {type_name}{null_str}{default_str}{pk_str}")
            
            # 獲取記錄數
            result = db.execute(text(f"SELECT COUNT(*) FROM {table_name};"))
            count = result.fetchone()[0]
            print(f"記錄數: {count}")
            
            # 如果是用戶表，顯示用戶資訊
            if table_name == "users" and count > 0:
                result = db.execute(text("SELECT id, username, email, status FROM users;"))
                users = result.fetchall()
                print("用戶列表:")
                for user in users:
                    print(f"  - ID: {user[0]}, 用戶名: {user[1]}, 郵箱: {user[2]}, 狀態: {user[3]}")
            
            # 如果是角色表，顯示角色資訊
            elif table_name == "roles" and count > 0:
                result = db.execute(text("SELECT id, code, name FROM roles;"))
                roles = result.fetchall()
                print("角色列表:")
                for role in roles:
                    print(f"  - ID: {role[0]}, 代碼: {role[1]}, 名稱: {role[2]}")
            
            # 如果是權限表，顯示權限資訊
            elif table_name == "permissions" and count > 0:
                result = db.execute(text("SELECT id, code, name FROM permissions;"))
                permissions = result.fetchall()
                print("權限列表:")
                for perm in permissions:
                    print(f"  - ID: {perm[0]}, 代碼: {perm[1]}, 名稱: {perm[2]}")
            
            # 如果是關聯表，顯示關聯資訊
            elif table_name == "user_roles" and count > 0:
                result = db.execute(text("""
                    SELECT ur.user_id, ur.role_id, u.username, r.name 
                    FROM user_roles ur 
                    JOIN users u ON ur.user_id = u.id 
                    JOIN roles r ON ur.role_id = r.id
                """))
                user_roles = result.fetchall()
                print("用戶角色關聯:")
                for ur in user_roles:
                    print(f"  - 用戶: {ur[2]} -> 角色: {ur[3]}")
            
            elif table_name == "role_permissions" and count > 0:
                result = db.execute(text("""
                    SELECT rp.role_id, rp.permission_id, r.name, p.name 
                    FROM role_permissions rp 
                    JOIN roles r ON rp.role_id = r.id 
                    JOIN permissions p ON rp.permission_id = p.id
                """))
                role_permissions = result.fetchall()
                print("角色權限關聯:")
                for rp in role_permissions:
                    print(f"  - 角色: {rp[2]} -> 權限: {rp[3]}")
        
        print("\n" + "=" * 80)
        print("🎉 資料表檢查完成!")
        
        # 檢查是否有遺漏的表
        expected_tables = [
            "users", "roles", "permissions", "user_roles", "role_permissions",
            "user_sessions", "user_login_events", "password_resets"
        ]
        
        missing_tables = [table for table in expected_tables if table not in tables]
        if missing_tables:
            print(f"\n⚠️  遺漏的表: {missing_tables}")
        else:
            print("\n✅ 所有預期的表都存在!")
        
    except Exception as e:
        print(f"❌ 資料表檢查失敗: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    check_all_tables()
