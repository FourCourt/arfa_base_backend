# ARFA 後端架構說明

## 🏗️ 整體架構

本項目採用 **MVC + Service 層** 架構，遵循企業級應用的最佳實踐：

```
app/
├── models/          # 數據模型層 (Model)
├── services/        # 商務邏輯層 (Service) 
├── controllers/     # 控制器層 (Controller)
├── api/            # API 路由層
├── core/           # 核心配置
└── database.py     # 數據庫配置
```

## 📋 各層職責

### 1. Models 層 (`app/models/`)
- **職責**: 數據模型定義，對應數據庫表結構
- **技術**: SQLAlchemy ORM
- **包含**:
  - 數據庫表模型
  - Pydantic 驗證模型
  - 模型關係定義

### 2. Services 層 (`app/services/`)
- **職責**: 商務邏輯處理，核心業務規則
- **特點**:
  - 純業務邏輯，不涉及 HTTP 請求/響應
  - 可重複使用
  - 易於單元測試
  - 處理複雜的業務流程

#### 服務類別：
- `BaseService`: 基礎 CRUD 操作
- `UserService`: 用戶相關業務邏輯
- `AuthService`: 認證相關業務邏輯  
- `ItemService`: 項目相關業務邏輯

### 3. Controllers 層 (`app/controllers/`)
- **職責**: 處理 HTTP 請求/響應，協調 Service 層
- **特點**:
  - 接收 HTTP 請求
  - 參數驗證和錯誤處理
  - 調用 Service 層處理業務邏輯
  - 返回 HTTP 響應

#### 控制器類別：
- `AuthController`: 認證控制器
- `UserController`: 用戶管理控制器
- `ItemController`: 項目管理控制器

### 4. API 層 (`app/api/`)
- **職責**: 定義 API 端點和路由
- **特點**:
  - 純路由定義
  - 依賴注入
  - 最小化邏輯

## 🔄 數據流向

```
HTTP Request → API Router → Controller → Service → Model → Database
                ↓
HTTP Response ← API Router ← Controller ← Service ← Model ← Database
```

## 📊 API 端點總覽

### 認證相關 (`/api/v1/auth/`)
- `POST /login` - 用戶登入
- `POST /logout` - 用戶登出  
- `GET /me` - 獲取當前用戶信息
- `POST /password-reset` - 請求密碼重設
- `POST /password-reset/confirm` - 確認密碼重設
- `GET /login-logs` - 獲取登入日誌

### 用戶管理 (`/api/v1/users/`)
- `POST /` - 創建用戶
- `GET /` - 獲取用戶列表
- `GET /{user_id}` - 獲取特定用戶
- `PUT /{user_id}` - 更新用戶信息
- `DELETE /{user_id}` - 刪除用戶
- `PATCH /{user_id}/status` - 更新用戶狀態
- `GET /active/list` - 獲取活躍用戶 (管理員)
- `GET /locked/list` - 獲取被鎖定用戶 (管理員)

### 項目管理 (`/api/v1/items/`)
- `POST /` - 創建項目
- `GET /` - 獲取用戶項目列表
- `GET /{item_id}` - 獲取特定項目
- `PUT /{item_id}` - 更新項目
- `DELETE /{item_id}` - 刪除項目
- `GET /search/query` - 搜索項目
- `GET /filter/price` - 按價格範圍篩選
- `GET /admin/all` - 獲取所有項目 (管理員)

## 🔧 核心功能

### 安全特性
- PBKDF2 密碼哈希 (鹽值 + 迭代)
- JWT 令牌認證
- 會話管理
- 登入失敗鎖定
- 密碼強度檢查
- CSRF 保護

### 數據庫支持
- **開發環境**: MySQL (XAMPP)
- **生產環境**: PostgreSQL
- 環境自動切換

### 錯誤處理
- 統一的異常處理
- 詳細的錯誤信息
- HTTP 狀態碼標準化

## 🚀 啟動方式

### 開發環境 (MySQL)
```bash
start_dev.bat
# 或
python run.py
```

### 生產環境 (PostgreSQL)
```bash
start_prod.bat
```

### API 文檔
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📝 開發規範

### 1. 新增功能流程
1. 在 `models/` 定義數據模型
2. 在 `services/` 實現業務邏輯
3. 在 `controllers/` 處理 HTTP 請求
4. 在 `api/endpoints/` 定義路由

### 2. 代碼風格
- 使用類型註解
- 遵循 PEP 8
- 詳細的文檔字符串
- 統一的錯誤處理

### 3. 測試建議
- Service 層單元測試
- Controller 層集成測試
- API 端點端到端測試

## 🔍 查看所有 API

運行以下命令查看完整的 API 列表：
```bash
python list_apis.py
```

---

這個架構確保了代碼的：
- **可維護性**: 清晰的層次結構
- **可擴展性**: 易於添加新功能
- **可測試性**: 各層職責明確
- **可重用性**: Service 層可被多個 Controller 使用


