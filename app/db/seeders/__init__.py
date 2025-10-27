# Seeder 系統
from .base import BaseSeeder

# 動態導入 seeder 類
import importlib
import os

def get_seeder_classes():
    """獲取所有 seeder 類"""
    seeders = []
    seeder_dir = os.path.dirname(__file__)
    
    for filename in os.listdir(seeder_dir):
        if filename.startswith(('001_', '002_', '003_', '004_')) and filename.endswith('.py'):
            module_name = filename[:-3]  # 移除 .py
            try:
                module = importlib.import_module(f'.{module_name}', package=__name__)
                # 查找 seeder 類
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseSeeder) and 
                        attr != BaseSeeder):
                        seeders.append(attr)
            except Exception as e:
                print(f"Warning: Could not import {module_name}: {e}")
    
    return seeders

__all__ = ["BaseSeeder", "get_seeder_classes"]
