#!/usr/bin/env python3
"""
測試註冊功能
"""
import requests
import json

def test_registration():
    """測試用戶註冊功能"""
    base_url = "http://localhost:8001"
    
    # 測試註冊
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "phone": "+886912345678",
        "password": "Test123!@#",
        "confirm_password": "Test123!@#"
    }
    
    print("測試用戶註冊...")
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"狀態碼: {response.status_code}")
        print(f"響應: {response.json()}")
        
        if response.status_code == 200:
            print("[SUCCESS] 註冊成功！")
            
            # 測試郵箱驗證（使用假令牌）
            print("\n測試郵箱驗證...")
            verify_data = {
                "token": "test-token-123"
            }
            
            verify_response = requests.post(
                f"{base_url}/api/v1/auth/verify-email",
                json=verify_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"驗證狀態碼: {verify_response.status_code}")
            print(f"驗證響應: {verify_response.json()}")
            
        else:
            print("[ERROR] 註冊失敗")
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] 無法連接到服務器，請確保服務器正在運行")
    except Exception as e:
        print(f"[ERROR] 測試失敗: {str(e)}")

def test_login_with_unverified_user():
    """測試未驗證用戶登入"""
    base_url = "http://localhost:8001"
    
    login_data = {
        "username": "testuser",
        "password": "Test123!@#"
    }
    
    print("\n測試未驗證用戶登入...")
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"狀態碼: {response.status_code}")
        print(f"響應: {response.json()}")
        
        if response.status_code == 401:
            print("[SUCCESS] 未驗證用戶無法登入（符合預期）")
        else:
            print("[ERROR] 未驗證用戶不應該能夠登入")
            
    except Exception as e:
        print(f"[ERROR] 測試失敗: {str(e)}")

if __name__ == "__main__":
    print("開始測試註冊功能...")
    test_registration()
    test_login_with_unverified_user()
    print("\n測試完成！")
