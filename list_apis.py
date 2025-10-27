#!/usr/bin/env python3
"""
列出所有可用的 API 端點
"""
from app.main import app
from fastapi.routing import APIRoute

def list_all_apis():
    """列出所有 API 端點"""
    print("LAZY API 端點列表")
    print("=" * 60)
    
    routes = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name,
                "summary": getattr(route, 'summary', ''),
                "tags": getattr(route, 'tags', [])
            })
    
    # 按路徑排序
    routes.sort(key=lambda x: x['path'])
    
    current_tag = None
    for route in routes:
        # 顯示標籤分組
        if route['tags'] and route['tags'][0] != current_tag:
            current_tag = route['tags'][0]
            print(f"\n[{current_tag}]")
            print("-" * 40)
        
        # 顯示端點信息
        methods_str = ", ".join(route['methods'])
        summary = f" - {route['summary']}" if route['summary'] else ""
        
        print(f"{methods_str:15} {route['path']}{summary}")
    
    print("\n" + "=" * 60)
    print(f"總共 {len(routes)} 個 API 端點")
    
    # 顯示基礎信息
    print(f"\n服務信息:")
    print(f"  服務地址: http://localhost:8000")
    print(f"  API 文檔: http://localhost:8000/docs")
    print(f"  ReDoc: http://localhost:8000/redoc")
    print(f"  健康檢查: http://localhost:8000/health")

if __name__ == "__main__":
    list_all_apis()




