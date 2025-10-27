#!/bin/bash

# LAZY API AWS 部署腳本
# 使用方法: ./deploy_to_aws.sh your-key.pem ec2-user@your-ec2-ip

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

# 檢查參數
if [ $# -ne 2 ]; then
    log_error "使用方法: $0 <pem-file> <ec2-connection>"
    log_error "例如: $0 my-key.pem ec2-user@1.2.3.4"
    exit 1
fi

PEM_FILE=$1
EC2_CONNECTION=$2

# 檢查PEM文件是否存在
if [ ! -f "$PEM_FILE" ]; then
    log_error "PEM文件不存在: $PEM_FILE"
    exit 1
fi

# 設置PEM文件權限
log_info "設置PEM文件權限..."
chmod 400 "$PEM_FILE"

# 創建臨時目錄
TEMP_DIR=$(mktemp -d)
log_info "創建臨時目錄: $TEMP_DIR"

# 複製項目文件到臨時目錄
log_info "準備項目文件..."
cp -r . "$TEMP_DIR/lazy"
cd "$TEMP_DIR/lazy"

# 刪除不需要的文件
rm -rf __pycache__ .git .env app/__pycache__ app/*/__pycache__

# 創建部署包
log_info "創建部署包..."
tar -czf ../lazy-deploy.tar.gz .

# 上傳到EC2
log_info "上傳文件到EC2實例..."
scp -i "$PEM_FILE" ../lazy-deploy.tar.gz "$EC2_CONNECTION:/tmp/"

# 在EC2上執行部署
log_info "在EC2上執行部署..."
ssh -i "$PEM_FILE" "$EC2_CONNECTION" << 'EOF'
set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 創建應用目錄
log_info "創建應用目錄..."
sudo mkdir -p /opt/lazy
sudo chown ec2-user:ec2-user /opt/lazy

# 停止現有服務
log_info "停止現有服務..."
sudo systemctl stop lazy 2>/dev/null || true

# 備份現有配置
if [ -f "/opt/lazy/.env" ]; then
    log_info "備份現有配置..."
    cp /opt/lazy/.env /tmp/lazy.env.backup
fi

# 解壓新文件
log_info "解壓新文件..."
cd /opt/lazy
tar -xzf /tmp/lazy-deploy.tar.gz

# 恢復配置
if [ -f "/tmp/lazy.env.backup" ]; then
    log_info "恢復配置..."
    cp /tmp/lazy.env.backup .env
fi

# 創建虛擬環境
log_info "創建虛擬環境..."
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
log_info "安裝依賴..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# 設置文件權限
log_info "設置文件權限..."
chmod 600 .env 2>/dev/null || true

# 運行資料庫遷移
log_info "運行資料庫遷移..."
python migrate_and_seed.py

# 重新載入systemd
log_info "重新載入systemd..."
sudo systemctl daemon-reload

# 啟動服務
log_info "啟動服務..."
sudo systemctl enable lazy
sudo systemctl start lazy

# 檢查服務狀態
log_info "檢查服務狀態..."
sleep 5
if sudo systemctl is-active --quiet lazy; then
    log_success "服務啟動成功!"
    sudo systemctl status lazy --no-pager
else
    log_error "服務啟動失敗!"
    sudo journalctl -u lazy -n 20 --no-pager
    exit 1
fi

# 清理臨時文件
rm -f /tmp/lazy-deploy.tar.gz /tmp/lazy.env.backup

log_success "部署完成!"
EOF

# 清理本地臨時文件
log_info "清理臨時文件..."
rm -rf "$TEMP_DIR"

log_success "AWS部署完成!"
log_info "請檢查服務狀態: ssh -i $PEM_FILE $EC2_CONNECTION 'sudo systemctl status lazy'"

