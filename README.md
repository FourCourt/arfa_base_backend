# ARFA FastAPI 後端項目

這是一個使用 FastAPI 構建的現代化後端 API 項目，已部署到 AWS EC2 並使用 PostgreSQL 資料庫。

## 🚀 線上部署

**應用程式網址:** http://3.26.158.168:8000  
**API 文檔:** http://3.26.158.168:8000/docs  
**健康檢查:** http://3.26.158.168:8000/health

### 🔐 管理員帳號
- **用戶名:** `admin`
- **密碼:** `Admin123!@#`

## 項目結構

```
ARFA/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 應用主文件
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py          # 配置文件
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       ├── users.py       # 用戶相關 API
│   │       └── items.py       # 項目相關 API
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py           # 數據庫基礎模型
│   │   ├── user.py           # 用戶模型
│   │   └── item.py           # 項目模型
│   └── database.py           # 數據庫配置
├── requirements.txt          # Python 依賴
├── create_tables.py         # 創建數據庫表
└── README.md               # 項目說明文檔
```

## 功能特性

- ✅ FastAPI 框架
- ✅ SQLAlchemy ORM
- ✅ PostgreSQL 資料庫 (生產環境)
- ✅ SQLite 資料庫 (開發環境)
- ✅ Pydantic 數據驗證
- ✅ JWT 認證系統
- ✅ 密碼加密與安全
- ✅ 角色權限管理
- ✅ 用戶會話管理
- ✅ 登入日誌記錄
- ✅ CORS 支持
- ✅ 自動 API 文檔生成
- ✅ pgAdmin 資料庫管理介面

## 安裝和運行

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 創建數據庫表

```bash
python create_tables.py
```

### 3. 啟動服務器

```bash
# 開發模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或者直接運行
python app/main.py
```

### 4. 訪問 API 文檔

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端點

### 基礎端點
- `GET /` - 歡迎頁面
- `GET /health` - 健康檢查

### 認證 API (Authentication)
- `POST /api/v1/auth/login` - 用戶登入
- `POST /api/v1/auth/logout` - 用戶登出
- `GET /api/v1/auth/me` - 獲取當前用戶資訊
- `POST /api/v1/auth/password-reset` - 請求重設密碼
- `POST /api/v1/auth/password-reset/confirm` - 確認重設密碼
- `GET /api/v1/auth/login-logs` - 獲取登入日誌

### 用戶管理 API (User Management)
- `POST /api/v1/users/` - 創建用戶
- `GET /api/v1/users/` - 獲取用戶列表
- `GET /api/v1/users/{user_id}` - 獲取特定用戶
- `PUT /api/v1/users/{user_id}` - 更新用戶
- `DELETE /api/v1/users/{user_id}` - 刪除用戶
- `PATCH /api/v1/users/{user_id}/status` - 更新用戶狀態
- `GET /api/v1/users/active/list` - 獲取活躍用戶列表
- `GET /api/v1/users/locked/list` - 獲取被鎖定用戶列表

## 數據模型

### 用戶模型 (User)
- `id`: 用戶 ID
- `email`: 電子郵件
- `username`: 用戶名
- `full_name`: 全名
- `hashed_password`: 加密密碼
- `is_active`: 是否啟用
- `created_at`: 創建時間
- `updated_at`: 更新時間

### 項目模型 (Item)
- `id`: 項目 ID
- `title`: 標題
- `description`: 描述
- `price`: 價格
- `owner_id`: 擁有者 ID
- `created_at`: 創建時間
- `updated_at`: 更新時間

## 開發說明

### 添加新的 API 端點

1. 在 `app/api/endpoints/` 創建新的路由文件
2. 在 `app/api/__init__.py` 中註冊路由
3. 創建對應的數據模型和 Pydantic 模型

### 數據庫遷移

使用 Alembic 進行數據庫遷移：

```bash
# 初始化遷移
alembic init alembic

# 創建遷移文件
alembic revision --autogenerate -m "描述"

# 執行遷移
alembic upgrade head
```

## 配置

項目配置在 `app/core/config.py` 中，支持通過環境變量覆蓋：

- `DATABASE_URL`: 數據庫連接字符串
- `SECRET_KEY`: JWT 密鑰
- `BACKEND_CORS_ORIGINS`: CORS 允許的來源

## 🗄️ 資料庫配置

### PostgreSQL (生產環境)
- **主機:** localhost
- **端口:** 5432
- **資料庫:** arfa
- **用戶:** lazyadmin
- **密碼:** 2djixxjl

### pgAdmin 可視化介面
- **URL:** http://3.26.158.168
- **登入郵箱:** lazy@lazy.com
- **密碼:** 2djixxjl

### 資料庫表結構
- `users` - 用戶表
- `roles` - 角色表
- `permissions` - 權限表
- `user_roles` - 用戶角色關聯表
- `role_permissions` - 角色權限關聯表
- `user_sessions` - 用戶會話表
- `user_login_events` - 登入事件表
- `password_resets` - 密碼重置表

## 🚀 AWS 部署資訊

### 伺服器配置
- **實例類型:** EC2
- **IP 地址:** 3.26.158.168
- **作業系統:** Amazon Linux 2023
- **Python 版本:** 3.9

### Docker 容器
- **PostgreSQL:** postgres:17
- **pgAdmin:** dpage/pgadmin4:latest
- **Portainer:** portainer/portainer-ce:latest

### 部署腳本
- `deploy_to_aws.sh` - AWS 部署腳本
- `aws_setup_server.sh` - 伺服器初始化腳本
- `aws_check_status.sh` - 狀態檢查腳本
- `aws_quick_start.bat` - Windows 快速部署腳本

## 🔧 開發工具

### 本地開發
```bash
# 啟動開發伺服器
python main.py

# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 資料庫遷移
```bash
# 執行遷移
python migrate_and_seed.py

# 或使用 SQLite 設置
python setup_sqlite_db.py
```

### 測試 API
```bash
# 登入測試
curl -X POST "http://3.26.158.168:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"Admin123!@#"}'
```

## 📋 已完成功能

- ✅ JWT 認證系統
- ✅ 密碼加密與安全
- ✅ 角色權限管理
- ✅ 用戶會話管理
- ✅ 登入日誌記錄
- ✅ PostgreSQL 資料庫
- ✅ pgAdmin 管理介面
- ✅ AWS EC2 部署
- ✅ API 文檔 (英文)
- ✅ 資料庫遷移
- ✅ 健康檢查端點

## 🔄 版本歷史

- **v1.0.0** - 初始版本，基本 CRUD 功能
- **v1.1.0** - 添加認證系統和權限管理
- **v1.2.0** - 部署到 AWS EC2，使用 PostgreSQL
- **v1.3.0** - 添加 pgAdmin 和 API 文檔英文化

