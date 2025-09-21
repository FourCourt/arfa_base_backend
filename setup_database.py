#!/usr/bin/env python3
"""
數據庫設置腳本
執行 migrations 和 seeders
"""
import sys
import os

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.migrate import run_migrations, show_migration_status
from app.database.seed import run_all_seeders, show_seeder_list

def setup_database():
    """設置數據庫：執行 migrations 和 seeders"""
    print("🗄️  開始設置數據庫...")
    print("=" * 60)
    
    try:
        # 1. 執行 migrations
        print("\n📋 步驟 1: 執行 Migrations")
        print("-" * 30)
        run_migrations()
        
        # 2. 執行 seeders
        print("\n📋 步驟 2: 執行 Seeders")
        print("-" * 30)
        run_all_seeders()
        
        print("\n" + "=" * 60)
        print("🎉 數據庫設置完成！")
        print("\n📊 創建的內容:")
        print("• 所有數據庫表")
        print("• 管理員角色 (admin)")
        print("• 完整的權限系統")
        print("• 管理員用戶 (admin)")
        print("• 管理員權限分配")
        
        print("\n🔑 管理員登入信息:")
        print("• 用戶名: admin")
        print("• 密碼: Admin123!@#")
        print("• 郵箱: admin@arfa.com")
        
        print("\n🌐 可以訪問:")
        print("• API 文檔: http://localhost:8000/docs")
        print("• 健康檢查: http://localhost:8000/health")
        
    except Exception as e:
        print(f"\n❌ 數據庫設置失敗: {str(e)}")
        sys.exit(1)

def show_status():
    """顯示數據庫狀態"""
    print("📊 數據庫狀態")
    print("=" * 60)
    
    print("\n🔄 Migration 狀態:")
    print("-" * 30)
    show_migration_status()
    
    print("\n🌱 可用的 Seeders:")
    print("-" * 30)
    show_seeder_list()

def reset_database():
    """重置數據庫（危險操作）"""
    print("⚠️  警告：這將刪除所有數據！")
    response = input("確定要重置數據庫嗎？(yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ 操作已取消")
        return
    
    try:
        from app.database import engine
        from sqlalchemy import text
        
        print("🗑️  正在重置數據庫...")
        
        # 刪除所有表
        with engine.connect() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
            # 獲取所有表名
            result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            
            for table in tables:
                conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                print(f"🗑️  刪除表: {table}")
            
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            conn.commit()
        
        print("✅ 數據庫重置完成")
        print("🔄 重新設置數據庫...")
        setup_database()
        
    except Exception as e:
        print(f"❌ 重置失敗: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            show_status()
        elif sys.argv[1] == "reset":
            reset_database()
        else:
            print("用法:")
            print("  python setup_database.py          # 設置數據庫")
            print("  python setup_database.py status   # 顯示狀態")
            print("  python setup_database.py reset    # 重置數據庫")
    else:
        setup_database()

