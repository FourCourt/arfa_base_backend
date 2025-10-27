"""
Seeder 管理器
"""
import os
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db import SessionLocal
from app.db.seeders.base import BaseSeeder
from app.db.seeders import get_seeder_classes

class SeederManager:
    """Seeder 管理器"""
    
    def __init__(self):
        # 動態獲取 seeder 類
        seeder_classes = get_seeder_classes()
        self.seeders: List[BaseSeeder] = [cls() for cls in seeder_classes]
    
    def run_all_seeders(self, db: Session):
        """執行所有 seeders"""
        print("[INFO] 開始執行 Seeders...")
        print("=" * 50)
        
        for seeder in self.seeders:
            try:
                print(f"[RUN] 執行 {seeder.name}: {seeder.description}")
                seeder.run(db)
                
            except Exception as e:
                print(f"[ERROR] 失敗 {seeder.name}: {str(e)}")
                db.rollback()
                raise e
        
        print("=" * 50)
        print("[SUCCESS] 所有 Seeders 執行完成！")
    
    def run_specific_seeder(self, db: Session, seeder_name: str):
        """執行特定的 seeder"""
        seeder = next((s for s in self.seeders if s.name == seeder_name), None)
        
        if not seeder:
            print(f"❌ 找不到 seeder: {seeder_name}")
            return
        
        try:
            print(f"🔄 執行 {seeder.name}: {seeder.description}")
            seeder.run(db)
            print(f"✅ 完成 {seeder.name}")
            
        except Exception as e:
            print(f"❌ 失敗 {seeder.name}: {str(e)}")
            db.rollback()
            raise e
    
    def rollback_seeder(self, db: Session, seeder_name: str):
        """回滾特定的 seeder"""
        seeder = next((s for s in self.seeders if s.name == seeder_name), None)
        
        if not seeder:
            print(f"❌ 找不到 seeder: {seeder_name}")
            return
        
        try:
            print(f"🔄 回滾 {seeder.name}: {seeder.description}")
            if hasattr(seeder, 'rollback'):
                seeder.rollback(db)
            print(f"✅ 回滾完成 {seeder.name}")
            
        except Exception as e:
            print(f"❌ 回滾失敗 {seeder.name}: {str(e)}")
            db.rollback()
            raise e
    
    def show_seeder_list(self):
        """顯示所有 seeder 列表"""
        print("📋 可用的 Seeders:")
        print("=" * 50)
        
        for seeder in self.seeders:
            print(f"• {seeder.name}: {seeder.description}")
        
        print("=" * 50)

def run_all_seeders():
    """執行所有 seeders"""
    db = SessionLocal()
    try:
        manager = SeederManager()
        manager.run_all_seeders(db)
    finally:
        db.close()

def run_specific_seeder(seeder_name: str):
    """執行特定的 seeder"""
    db = SessionLocal()
    try:
        manager = SeederManager()
        manager.run_specific_seeder(db, seeder_name)
    finally:
        db.close()

def rollback_seeder(seeder_name: str):
    """回滾特定的 seeder"""
    db = SessionLocal()
    try:
        manager = SeederManager()
        manager.rollback_seeder(db, seeder_name)
    finally:
        db.close()

def show_seeder_list():
    """顯示 seeder 列表"""
    manager = SeederManager()
    manager.show_seeder_list()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "run" and len(sys.argv) > 2:
            run_specific_seeder(sys.argv[2])
        elif sys.argv[1] == "rollback" and len(sys.argv) > 2:
            rollback_seeder(sys.argv[2])
        elif sys.argv[1] == "list":
            show_seeder_list()
        else:
            print("用法: python seed.py [run <seeder_name>|rollback <seeder_name>|list]")
    else:
        run_all_seeders()
