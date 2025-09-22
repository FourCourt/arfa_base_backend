#!/bin/bash

# ARFA API AWS 狀態檢查腳本
# 用於檢查AWS部署的各種服務狀態

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

log_info "開始檢查AWS部署狀態..."

# 在EC2上執行狀態檢查
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

echo "=========================================="
echo "ARFA API AWS 部署狀態檢查"
echo "=========================================="
echo ""

# 檢查系統資訊
log_info "系統資訊:"
echo "作業系統: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "主機名稱: $(hostname)"
echo "IP地址: $(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo ""

# 檢查磁碟空間
log_info "磁碟空間:"
df -h /
echo ""

# 檢查記憶體使用
log_info "記憶體使用:"
free -h
echo ""

# 檢查Python版本
log_info "Python版本:"
python3 --version
echo ""

# 檢查PostgreSQL狀態
log_info "PostgreSQL狀態:"
if sudo systemctl is-active --quiet postgresql-15; then
    log_success "PostgreSQL 正在運行"
    sudo systemctl status postgresql-15 --no-pager -l
else
    log_error "PostgreSQL 未運行"
fi
echo ""

# 檢查資料庫連接
log_info "資料庫連接測試:"
if sudo -u postgres psql -c "SELECT version();" > /dev/null 2>&1; then
    log_success "資料庫連接正常"
else
    log_error "資料庫連接失敗"
fi
echo ""

# 檢查應用程式目錄
log_info "應用程式目錄:"
if [ -d "/opt/arfa" ]; then
    log_success "應用程式目錄存在"
    ls -la /opt/arfa/
else
    log_error "應用程式目錄不存在"
fi
echo ""

# 檢查虛擬環境
log_info "虛擬環境:"
if [ -d "/opt/arfa/venv" ]; then
    log_success "虛擬環境存在"
    /opt/arfa/venv/bin/python --version
else
    log_error "虛擬環境不存在"
fi
echo ""

# 檢查環境變數文件
log_info "環境變數文件:"
if [ -f "/opt/arfa/.env" ]; then
    log_success "環境變數文件存在"
    echo "文件大小: $(stat -c%s /opt/arfa/.env) bytes"
else
    log_warning "環境變數文件不存在"
fi
echo ""

# 檢查ARFA服務狀態
log_info "ARFA服務狀態:"
if sudo systemctl is-active --quiet arfa; then
    log_success "ARFA服務正在運行"
    sudo systemctl status arfa --no-pager -l
else
    log_error "ARFA服務未運行"
    echo "最近的日誌:"
    sudo journalctl -u arfa -n 10 --no-pager
fi
echo ""

# 檢查Nginx狀態
log_info "Nginx狀態:"
if sudo systemctl is-active --quiet nginx; then
    log_success "Nginx正在運行"
    sudo systemctl status nginx --no-pager -l
else
    log_error "Nginx未運行"
fi
echo ""

# 檢查端口監聽
log_info "端口監聽狀態:"
echo "端口8000 (應用程式):"
sudo netstat -tlnp | grep :8000 || echo "端口8000未監聽"
echo "端口80 (Nginx):"
sudo netstat -tlnp | grep :80 || echo "端口80未監聽"
echo ""

# 檢查防火牆狀態
log_info "防火牆狀態:"
sudo firewall-cmd --list-all
echo ""

# 檢查應用程式健康狀態
log_info "應用程式健康檢查:"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    log_success "應用程式健康檢查通過"
    curl -s http://localhost:8000/health
else
    log_error "應用程式健康檢查失敗"
fi
echo ""

# 檢查外部訪問
log_info "外部訪問測試:"
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
if curl -s http://$PUBLIC_IP/ > /dev/null 2>&1; then
    log_success "外部訪問正常"
else
    log_warning "外部訪問可能失敗"
fi
echo ""

# 檢查最近的日誌
log_info "最近的ARFA服務日誌:"
sudo journalctl -u arfa -n 20 --no-pager
echo ""

# 檢查Nginx日誌
log_info "最近的Nginx錯誤日誌:"
sudo tail -n 10 /var/log/nginx/error.log 2>/dev/null || echo "無錯誤日誌"
echo ""

log_info "狀態檢查完成!"
EOF

log_success "AWS狀態檢查完成!"

