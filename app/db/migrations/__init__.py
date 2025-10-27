# Migration 系統
from .base import BaseMigration

# 動態導入遷移類
import importlib
import os

def get_migration_classes():
    """獲取所有遷移類"""
    migrations = []
    migration_dir = os.path.dirname(__file__)
    
    for filename in os.listdir(migration_dir):
        if filename.startswith(('001_', '002_', '003_')) and filename.endswith('.py'):
            module_name = filename[:-3]  # 移除 .py
            try:
                module = importlib.import_module(f'.{module_name}', package=__name__)
                # 查找遷移類
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseMigration) and 
                        attr != BaseMigration):
                        migrations.append(attr)
            except Exception as e:
                print(f"Warning: Could not import {module_name}: {e}")
    
    return migrations

__all__ = ["BaseMigration", "get_migration_classes"]
