# ARFA FastAPI 後端項目

這是一個使用 FastAPI 構建的現代化後端 API 項目。

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
- ✅ SQLite 數據庫
- ✅ Pydantic 數據驗證
- ✅ CORS 支持
- ✅ 用戶管理 API
- ✅ 項目管理 API
- ✅ 自動 API 文檔生成

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

### 用戶管理
- `POST /api/v1/users/` - 創建用戶
- `GET /api/v1/users/` - 獲取用戶列表
- `GET /api/v1/users/{user_id}` - 獲取特定用戶
- `PUT /api/v1/users/{user_id}` - 更新用戶
- `DELETE /api/v1/users/{user_id}` - 刪除用戶

### 項目管理
- `POST /api/v1/items/` - 創建項目
- `GET /api/v1/items/` - 獲取項目列表
- `GET /api/v1/items/{item_id}` - 獲取特定項目
- `PUT /api/v1/items/{item_id}` - 更新項目
- `DELETE /api/v1/items/{item_id}` - 刪除項目

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

## 下一步計劃

- [ ] 添加 JWT 認證
- [ ] 實現密碼加密
- [ ] 添加數據庫遷移
- [ ] 添加單元測試
- [ ] 添加日誌記錄
- [ ] 添加 Docker 支持

