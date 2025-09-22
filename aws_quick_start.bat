@echo off
chcp 65001 >nul
echo ========================================
echo ARFA API AWS 快速部署工具
echo ========================================
echo.

REM 檢查參數
if "%~2"=="" (
    echo 使用方法: %0 ^<pem-file^> ^<ec2-ip^>
    echo 例如: %0 my-key.pem 1.2.3.4
    pause
    exit /b 1
)

set PEM_FILE=%~1
set EC2_IP=%~2
set EC2_CONNECTION=ec2-user@%EC2_IP%

echo 正在使用以下配置:
echo PEM文件: %PEM_FILE%
echo EC2 IP: %EC2_IP%
echo 連接字串: %EC2_CONNECTION%
echo.

REM 檢查PEM文件是否存在
if not exist "%PEM_FILE%" (
    echo 錯誤: PEM文件不存在 - %PEM_FILE%
    pause
    exit /b 1
)

echo 步驟1: 設置PEM文件權限...
icacls "%PEM_FILE%" /inheritance:r >nul 2>&1
icacls "%PEM_FILE%" /grant:r "%USERNAME%:F" >nul 2>&1

echo 步驟2: 測試SSH連接...
ssh -i "%PEM_FILE%" -o ConnectTimeout=10 -o BatchMode=yes %EC2_CONNECTION% "echo 'SSH連接成功'" >nul 2>&1
if errorlevel 1 (
    echo 錯誤: 無法連接到EC2實例
    echo 請檢查:
    echo - PEM文件路徑是否正確
    echo - EC2 IP地址是否正確
    echo - 安全組是否開放SSH端口(22)
    pause
    exit /b 1
)
echo SSH連接測試成功!

echo.
echo 步驟3: 上傳伺服器設定腳本...
scp -i "%PEM_FILE%" aws_setup_server.sh %EC2_CONNECTION%:/tmp/
if errorlevel 1 (
    echo 錯誤: 無法上傳設定腳本
    pause
    exit /b 1
)

echo 步驟4: 執行伺服器初始設定...
ssh -i "%PEM_FILE%" %EC2_CONNECTION% "chmod +x /tmp/aws_setup_server.sh && sudo /tmp/aws_setup_server.sh"
if errorlevel 1 (
    echo 錯誤: 伺服器設定失敗
    pause
    exit /b 1
)

echo 步驟5: 部署應用程式...
if exist "deploy_to_aws.sh" (
    bash deploy_to_aws.sh "%PEM_FILE%" "%EC2_CONNECTION%"
    if errorlevel 1 (
        echo 錯誤: 應用程式部署失敗
        pause
        exit /b 1
    )
) else (
    echo 警告: deploy_to_aws.sh 不存在，跳過自動部署
    echo 請手動執行部署步驟
)

echo.
echo ========================================
echo 部署完成!
echo ========================================
echo.
echo 下一步:
echo 1. 檢查服務狀態: ssh -i "%PEM_FILE%" %EC2_CONNECTION% "sudo systemctl status arfa"
echo 2. 測試API: curl http://%EC2_IP%/
echo 3. 查看日誌: ssh -i "%PEM_FILE%" %EC2_CONNECTION% "sudo journalctl -u arfa -f"
echo.

echo 按任意鍵退出...
pause >nul

