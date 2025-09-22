#!/usr/bin/env python3
"""
修正管理員密碼
"""
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.security import create_password_hash

# 創建數據庫引擎
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fix_admin_password():
    """修正管理員密碼"""
    print("🔧 修正管理員密碼...")
    print("=" * 60)
    
    try:
        db = SessionLocal()
        
        # 生成正確的密碼哈希
        admin_password = "Admin123!@#"
        password_hash, password_salt, password_iters = create_password_hash(admin_password)
        
        print(f"新密碼: {admin_password}")
        print(f"密碼哈希: {password_hash.hex()}")
        print(f"密碼鹽值: {password_salt.hex()}")
        print(f"迭代次數: {password_iters}")
        
        # 更新管理員密碼
        sql = f"""
        UPDATE users 
        SET password_hash = X'{password_hash.hex()}', password_salt = X'{password_salt.hex()}', password_iters = {password_iters}
        WHERE username = 'admin'
        """
        db.execute(text(sql))
        db.commit()
        
        print("\n✅ 管理員密碼已更新!")
        print("=" * 60)
        print("管理員帳號: admin")
        print("管理員密碼: Admin123!@#")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 密碼更新失敗: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin_password()
