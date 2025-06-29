# Alpha区块链节点 - Windows安装脚本

param(
    [string]$InstallPath = "$env:LOCALAPPDATA\AlphaNode",
    [switch]$CreateDesktopShortcut = $true
)

Write-Host "🚀 Alpha Blockchain Node - Windows Installer" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# 检查PowerShell版本
if ($PSVersionTable.PSVersion.Major -lt 5) {
    Write-Host "❌ PowerShell 5.0 or higher is required." -ForegroundColor Red
    exit 1
}

# 检查系统架构
$arch = $env:PROCESSOR_ARCHITECTURE
if ($arch -ne "AMD64") {
    Write-Host "❌ Unsupported architecture: $arch" -ForegroundColor Red
    Write-Host "   Alpha Node currently supports x64 only." -ForegroundColor Red
    exit 1
}

# 检查系统要求
Write-Host "🔍 Checking system requirements..." -ForegroundColor Yellow

# 检查内存
$memory = Get-CimInstance -ClassName Win32_ComputerSystem
$memoryGB = [math]::Round($memory.TotalPhysicalMemory / 1GB, 2)
Write-Host "💾 Total Memory: $memoryGB GB" -ForegroundColor Cyan

if ($memoryGB -lt 1) {
    Write-Host "⚠️  Warning: Low memory detected. Minimum 1GB recommended for light node." -ForegroundColor Yellow
}

# 检查磁盘空间
$disk = Get-CimInstance -ClassName Win32_LogicalDisk | Where-Object { $_.DeviceID -eq "C:" }
$freeSpaceGB = [math]::Round($disk.FreeSpace / 1GB, 2)
Write-Host "💿 Available Disk Space: $freeSpaceGB GB" -ForegroundColor Cyan

if ($freeSpaceGB -lt 1) {
    Write-Host "❌ Insufficient disk space. At least 1GB required." -ForegroundColor Red
    exit 1
}

# 创建安装目录
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
$dataDir = "$InstallPath\data"
$logsDir = "$InstallPath\logs"
$dbDir = "$InstallPath\db"
$keystoreDir = "$InstallPath\keystore"

New-Item -ItemType Directory -Force -Path $InstallPath | Out-Null
New-Item -ItemType Directory -Force -Path $dataDir | Out-Null
New-Item -ItemType Directory -Force -Path $logsDir | Out-Null
New-Item -ItemType Directory -Force -Path $dbDir | Out-Null
New-Item -ItemType Directory -Force -Path $keystoreDir | Out-Null

# 下载节点程序
Write-Host "⬇️  Downloading Alpha Node binary..." -ForegroundColor Yellow
$downloadUrl = "https://github.com/AlphaSNetwork/AlphaSNetwork/releases/latest/download/alpha-node-windows-x86_64.exe"
$binaryPath = "$InstallPath\alpha-node.exe"

try {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $binaryPath -ErrorAction Stop
} catch {
    Write-Host "⚠️  Download failed. Checking for local binary..." -ForegroundColor Yellow
    if (Test-Path ".\alpha-node.exe") {
        Copy-Item ".\alpha-node.exe" $binaryPath
        Write-Host "✅ Using local binary." -ForegroundColor Green
    } else {
        Write-Host "❌ No binary found. Please build from source or download manually." -ForegroundColor Red
        exit 1
    }
}

# 创建配置文件
Write-Host "⚙️  Creating configuration file..." -ForegroundColor Yellow
$configContent = @"
# Alpha Node Configuration

[node]
name = "MyAlphaNode"
chain = "local"
base_path = "$($dataDir -replace '\\', '\\')"

[network]
listen_addresses = ["/ip4/0.0.0.0/tcp/30333"]
public_addresses = []
bootnodes = []

[rpc]
port = 9933
cors = ["*"]

[ws]
port = 9944
cors = ["*"]

[telemetry]
enabled = false
"@

$configPath = "$InstallPath\config.toml"
$configContent | Out-File -FilePath $configPath -Encoding UTF8

# 创建启动脚本
Write-Host "📝 Creating startup scripts..." -ForegroundColor Yellow

# 轻节点启动脚本
$lightNodeScript = @"
@echo off
echo 🚀 Starting Alpha Light Node...
"$binaryPath" --chain local --light --base-path "$dataDir" --name "AlphaLightNode-%COMPUTERNAME%" --rpc-port 9933 --ws-port 9944 --rpc-cors all --ws-external --rpc-external
pause
"@
$lightNodeScript | Out-File -FilePath "$InstallPath\start-light-node.bat" -Encoding ASCII

# 全节点启动脚本
$fullNodeScript = @"
@echo off
echo 🚀 Starting Alpha Full Node...
"$binaryPath" --chain local --base-path "$dataDir" --name "AlphaFullNode-%COMPUTERNAME%" --rpc-port 9933 --ws-port 9944 --rpc-cors all --ws-external --rpc-external
pause
"@
$fullNodeScript | Out-File -FilePath "$InstallPath\start-full-node.bat" -Encoding ASCII

# 验证者节点启动脚本
$validatorScript = @"
@echo off
echo 🚀 Starting Alpha Validator Node...
echo ⚠️  Make sure you have generated and inserted your validator keys!
"$binaryPath" --chain local --validator --base-path "$dataDir" --name "AlphaValidator-%COMPUTERNAME%" --rpc-port 9933 --ws-port 9944 --rpc-cors all
pause
"@
$validatorScript | Out-File -FilePath "$InstallPath\start-validator-node.bat" -Encoding ASCII

# 创建桌面快捷方式
if ($CreateDesktopShortcut) {
    Write-Host "🔧 Creating desktop shortcuts..." -ForegroundColor Yellow
    
    $WshShell = New-Object -comObject WScript.Shell
    
    # 轻节点快捷方式
    $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Alpha Light Node.lnk")
    $Shortcut.TargetPath = "$InstallPath\start-light-node.bat"
    $Shortcut.WorkingDirectory = $InstallPath
    $Shortcut.Description = "Start Alpha Light Node"
    $Shortcut.Save()
    
    # 全节点快捷方式
    $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Alpha Full Node.lnk")
    $Shortcut.TargetPath = "$InstallPath\start-full-node.bat"
    $Shortcut.WorkingDirectory = $InstallPath
    $Shortcut.Description = "Start Alpha Full Node"
    $Shortcut.Save()
}

# 添加到PATH
Write-Host "🔧 Adding to PATH..." -ForegroundColor Yellow
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($currentPath -notlike "*$InstallPath*") {
    $newPath = "$currentPath;$InstallPath"
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    Write-Host "   PATH updated. Please restart your command prompt." -ForegroundColor Green
}

# 创建Windows服务（可选）
Write-Host "🔧 Creating Windows service..." -ForegroundColor Yellow
$serviceScript = @"
# 创建Alpha Node Windows服务
# 以管理员身份运行此脚本

`$serviceName = "AlphaNode"
`$binaryPath = "$binaryPath"
`$arguments = "--chain local --base-path `"$dataDir`" --name `"AlphaNode-Service`""

if (Get-Service `$serviceName -ErrorAction SilentlyContinue) {
    Write-Host "Service already exists. Stopping and removing..." -ForegroundColor Yellow
    Stop-Service `$serviceName -Force
    sc.exe delete `$serviceName
}

Write-Host "Creating service..." -ForegroundColor Green
New-Service -Name `$serviceName -BinaryPathName "`$binaryPath `$arguments" -DisplayName "Alpha Blockchain Node" -Description "Alpha Blockchain Node Service" -StartupType Manual

Write-Host "Service created successfully!" -ForegroundColor Green
Write-Host "To start: Start-Service AlphaNode" -ForegroundColor Cyan
Write-Host "To stop: Stop-Service AlphaNode" -ForegroundColor Cyan
"@
$serviceScript | Out-File -FilePath "$InstallPath\create-service.ps1" -Encoding UTF8

Write-Host ""
Write-Host "✅ Alpha Node installation completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Installation directory: $InstallPath" -ForegroundColor Cyan
Write-Host "📁 Data directory: $dataDir" -ForegroundColor Cyan
Write-Host "📁 Configuration file: $configPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Quick start:" -ForegroundColor Yellow
Write-Host "   Light node:     Double-click 'Alpha Light Node' on desktop" -ForegroundColor White
Write-Host "   Full node:      Double-click 'Alpha Full Node' on desktop" -ForegroundColor White
Write-Host "   Command line:   alpha-node.exe --help" -ForegroundColor White
Write-Host ""
Write-Host "🔑 To generate validator keys:" -ForegroundColor Yellow
Write-Host "   alpha-node.exe key generate" -ForegroundColor White
Write-Host ""
Write-Host "🔧 To create Windows service (run as Administrator):" -ForegroundColor Yellow
Write-Host "   PowerShell -ExecutionPolicy Bypass -File `"$InstallPath\create-service.ps1`"" -ForegroundColor White
Write-Host ""
Write-Host "📖 For more information, visit:" -ForegroundColor Yellow
Write-Host "   https://github.com/AlphaSNetwork/AlphaSNetwork" -ForegroundColor White

