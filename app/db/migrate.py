"""
Migration 管理器
"""
import os
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db import SessionLocal
from app.db.migrations.base import BaseMigration
from app.db.migrations.create_migrations_table import CreateMigrationsTable
from app.db.migrations.create_all_tables import CreateAllTables
from app.db.migrations.add_email_verification import AddEmailVerification

class MigrationManager:
    """Migration 管理器"""
    
    def __init__(self):
        self.migrations: List[BaseMigration] = [
            CreateMigrationsTable(),
            CreateAllTables(),
            AddEmailVerification(),
        ]
    
    def get_executed_migrations(self, db: Session) -> List[str]:
        """獲取已執行的 migration 版本"""
        try:
            result = db.execute(text("SELECT version FROM migrations ORDER BY version"))
            return [row[0] for row in result.fetchall()]
        except:
            # 如果 migrations 表不存在，返回空列表
            return []
    
    def execute_migrations(self, db: Session):
        """執行所有未執行的 migrations"""
        executed_versions = self.get_executed_migrations(db)
        
        print("🚀 開始執行 Migrations...")
        print("=" * 50)
        
        for migration in self.migrations:
            if migration.version in executed_versions:
                print(f"⏭️  跳過 {migration.version}: {migration.description}")
                continue
            
            try:
                print(f"🔄 執行 {migration.version}: {migration.description}")
                migration.up(db)
                
                # 記錄已執行的 migration
                sql = """
                INSERT INTO migrations (version, description, executed_at)
                VALUES (:version, :description, :executed_at)
                """
                db.execute(text(sql), {
                    "version": migration.version,
                    "description": migration.description,
                    "executed_at": migration.created_at
                })
                db.commit()
                
                print(f"✅ 完成 {migration.version}")
                
            except Exception as e:
                print(f"❌ 失敗 {migration.version}: {str(e)}")
                db.rollback()
                raise e
        
        print("=" * 50)
        print("🎉 所有 Migrations 執行完成！")
    
    def rollback_migration(self, db: Session, version: str):
        """回滾指定版本的 migration"""
        executed_versions = self.get_executed_migrations(db)
        
        if version not in executed_versions:
            print(f"❌ Migration {version} 未執行過")
            return
        
        # 找到對應的 migration 並執行回滾
        for migration in self.migrations:
            if migration.version == version:
                try:
                    print(f"🔄 回滾 {migration.version}: {migration.description}")
                    migration.down(db)
                    
                    # 從 migrations 表中移除記錄
                    sql = "DELETE FROM migrations WHERE version = :version"
                    db.execute(text(sql), {"version": version})
                    db.commit()
                    
                    print(f"✅ 回滾完成 {migration.version}")
                    
                except Exception as e:
                    print(f"❌ 回滾失敗 {migration.version}: {str(e)}")
                    db.rollback()
                    raise e
                break
    
    def show_status(self, db: Session):
        """顯示 migration 狀態"""
        executed_versions = self.get_executed_migrations(db)
        
        print("📊 Migration 狀態")
        print("=" * 50)
        
        for migration in self.migrations:
            status = "✅ 已執行" if migration.version in executed_versions else "⏳ 待執行"
            print(f"{status} {migration.version}: {migration.description}")
        
        print("=" * 50)

def run_migrations():
    """執行所有 migrations"""
    db = SessionLocal()
    try:
        manager = MigrationManager()
        manager.execute_migrations(db)
    finally:
        db.close()

def rollback_migration(version: str):
    """回滾指定版本的 migration"""
    db = SessionLocal()
    try:
        manager = MigrationManager()
        manager.rollback_migration(db, version)
    finally:
        db.close()

def show_migration_status():
    """顯示 migration 狀態"""
    db = SessionLocal()
    try:
        manager = MigrationManager()
        manager.show_status(db)
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "rollback" and len(sys.argv) > 2:
            rollback_migration(sys.argv[2])
        elif sys.argv[1] == "status":
            show_migration_status()
        else:
            print("用法: python migrate.py [rollback <version>|status]")
    else:
        run_migrations()
