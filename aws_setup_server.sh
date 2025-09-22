#!/bin/bash

# ARFA API AWS 伺服器初始設定腳本
# 此腳本用於在EC2實例上進行初始環境設定

set -e  # 遇到錯誤立即退出

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日誌函數
log_info() {
    echo -e "${BLUE}[資訊]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[成功]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

log_error() {
    echo -e "${RED}[錯誤]${NC} $1"
}

log_info "開始AWS伺服器初始設定..."

# 更新系統
log_info "更新系統套件..."
sudo yum update -y

# 安裝Python 3.11
log_info "安裝Python 3.11..."
sudo yum install python3 python3-pip python3-devel -y

# 創建軟連結
sudo ln -sf /usr/bin/python3 /usr/bin/python
sudo ln -sf /usr/bin/pip3 /usr/bin/pip

# 安裝PostgreSQL
log_info "安裝PostgreSQL..."
sudo yum install postgresql15 postgresql15-server postgresql15-devel -y
sudo /usr/pgsql-15/bin/postgresql-15-setup initdb
sudo systemctl enable postgresql-15
sudo systemctl start postgresql-15

# 安裝其他必要工具
log_info "安裝其他必要工具..."
sudo yum install git firewalld -y

# 啟動防火牆
sudo systemctl enable firewalld
sudo systemctl start firewalld

# 配置PostgreSQL
log_info "配置PostgreSQL..."

# 編輯postgresql.conf
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /var/lib/pgsql/15/data/postgresql.conf

# 編輯pg_hba.conf
echo "host    all             all             0.0.0.0/0               md5" | sudo tee -a /var/lib/pgsql/15/data/pg_hba.conf

# 重啟PostgreSQL
sudo systemctl restart postgresql-15

# 創建資料庫和用戶
log_info "創建資料庫和用戶..."
sudo -u postgres psql << 'EOF'
CREATE DATABASE arfa_db;
CREATE USER arfa_user WITH PASSWORD 'arfa_secure_password_2024';
GRANT ALL PRIVILEGES ON DATABASE arfa_db TO arfa_user;
ALTER USER arfa_user CREATEDB;
\q
EOF

# 創建應用目錄
log_info "創建應用目錄..."
sudo mkdir -p /opt/arfa
sudo chown ec2-user:ec2-user /opt/arfa

# 配置防火牆
log_info "配置防火牆..."
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# 安裝Nginx
log_info "安裝Nginx..."
sudo yum install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx

# 創建Nginx配置
log_info "創建Nginx配置..."
sudo tee /etc/nginx/conf.d/arfa.conf > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# 測試Nginx配置
sudo nginx -t
sudo systemctl restart nginx

# 創建systemd服務文件
log_info "創建systemd服務文件..."
sudo tee /etc/systemd/system/arfa.service > /dev/null << 'EOF'
[Unit]
Description=ARFA API Service
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=exec
User=ec2-user
Group=ec2-user
WorkingDirectory=/opt/arfa
Environment=PATH=/opt/arfa/venv/bin
ExecStart=/opt/arfa/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 重新載入systemd
sudo systemctl daemon-reload

# 創建環境變數範本
log_info "創建環境變數範本..."
tee /opt/arfa/.env.example > /dev/null << 'EOF'
# 環境設定
ENVIRONMENT=production

# 資料庫配置
DATABASE_URL=postgresql://arfa_user:arfa_secure_password_2024@localhost:5432/arfa_db

# 安全配置
SECRET_KEY=your-super-secure-secret-key-here-change-this-in-production

# CORS設定
BACKEND_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# 伺服器配置
HOST=0.0.0.0
PORT=8000
EOF

# 創建備份腳本
log_info "創建備份腳本..."
tee /opt/arfa/backup_db.sh > /dev/null << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/arfa/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/arfa_db_$DATE.sql"

mkdir -p $BACKUP_DIR

pg_dump -h localhost -U arfa_user -d arfa_db > $BACKUP_FILE

# 壓縮備份文件
gzip $BACKUP_FILE

# 刪除7天前的備份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "資料庫備份完成: $BACKUP_FILE.gz"
EOF

chmod +x /opt/arfa/backup_db.sh

# 創建日誌輪轉配置
log_info "創建日誌輪轉配置..."
sudo tee /etc/logrotate.d/arfa > /dev/null << 'EOF'
/opt/arfa/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ec2-user ec2-user
    postrotate
        sudo systemctl reload arfa
    endscript
}
EOF

log_success "AWS伺服器初始設定完成!"
log_info "下一步請執行:"
log_info "1. 複製 .env.example 到 .env 並修改配置"
log_info "2. 上傳應用程式代碼"
log_info "3. 執行部署腳本"

echo ""
log_info "重要資訊:"
log_info "- 資料庫密碼: arfa_secure_password_2024"
log_info "- 應用目錄: /opt/arfa"
log_info "- 服務名稱: arfa"
log_info "- 端口: 8000 (內部), 80 (外部)"

