#!/bin/bash

# Alpha区块链节点 - macOS安装脚本

set -e

echo "🚀 Alpha Blockchain Node - macOS Installer"
echo "=========================================="

# 检查系统要求
echo "🔍 Checking system requirements..."

# 检查架构
ARCH=$(uname -m)
if [[ "$ARCH" != "x86_64" && "$ARCH" != "arm64" ]]; then
    echo "❌ Unsupported architecture: $ARCH"
    echo "   Alpha Node supports x86_64 and arm64 (Apple Silicon)."
    exit 1
fi

# 检查操作系统
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This installer is for macOS systems only."
    exit 1
fi

# 检查macOS版本
MACOS_VERSION=$(sw_vers -productVersion)
MACOS_MAJOR=$(echo $MACOS_VERSION | cut -d. -f1)
MACOS_MINOR=$(echo $MACOS_VERSION | cut -d. -f2)

echo "🍎 macOS Version: $MACOS_VERSION"

if [[ $MACOS_MAJOR -lt 10 || ($MACOS_MAJOR -eq 10 && $MACOS_MINOR -lt 15) ]]; then
    echo "⚠️  Warning: macOS 10.15 (Catalina) or later is recommended."
fi

# 检查内存
MEMORY_BYTES=$(sysctl -n hw.memsize)
MEMORY_GB=$((MEMORY_BYTES / 1024 / 1024 / 1024))
echo "💾 Total Memory: ${MEMORY_GB} GB"

if [[ $MEMORY_GB -lt 1 ]]; then
    echo "⚠️  Warning: Low memory detected. Minimum 1GB recommended for light node."
fi

# 检查磁盘空间
DISK_SPACE=$(df -g . | awk 'NR==2 {print $4}')
echo "💿 Available Disk Space: ${DISK_SPACE} GB"

if [[ $DISK_SPACE -lt 1 ]]; then
    echo "❌ Insufficient disk space. At least 1GB required."
    exit 1
fi

# 创建安装目录
INSTALL_DIR="/usr/local/bin"
DATA_DIR="$HOME/Library/Application Support/AlphaNode"

echo "📁 Creating directories..."
sudo mkdir -p "$INSTALL_DIR"
mkdir -p "$DATA_DIR"
mkdir -p "$DATA_DIR/logs"
mkdir -p "$DATA_DIR/db"
mkdir -p "$DATA_DIR/keystore"

# 下载节点程序
echo "⬇️  Downloading Alpha Node binary..."

# 根据架构选择下载链接
if [[ "$ARCH" == "arm64" ]]; then
    DOWNLOAD_URL="https://github.com/AlphaSNetwork/AlphaSNetwork/releases/latest/download/alpha-node-macos-arm64"
else
    DOWNLOAD_URL="https://github.com/AlphaSNetwork/AlphaSNetwork/releases/latest/download/alpha-node-macos-x86_64"
fi

if command -v curl &> /dev/null; then
    curl -L -o "/tmp/alpha-node" "$DOWNLOAD_URL" || {
        echo "⚠️  Download failed. Using local binary if available..."
        if [[ -f "./alpha-node" ]]; then
            cp "./alpha-node" "/tmp/alpha-node"
        else
            echo "❌ No binary found. Please build from source or download manually."
            exit 1
        fi
    }
elif command -v wget &> /dev/null; then
    wget -O "/tmp/alpha-node" "$DOWNLOAD_URL" || {
        echo "⚠️  Download failed. Using local binary if available..."
        if [[ -f "./alpha-node" ]]; then
            cp "./alpha-node" "/tmp/alpha-node"
        else
            echo "❌ No binary found. Please build from source or download manually."
            exit 1
        fi
    }
else
    echo "⚠️  Neither curl nor wget found. Using local binary if available..."
    if [[ -f "./alpha-node" ]]; then
        cp "./alpha-node" "/tmp/alpha-node"
    else
        echo "❌ No binary found. Please install curl or wget, then try again."
        exit 1
    fi
fi

# 安装二进制文件
echo "📦 Installing binary..."
sudo mv "/tmp/alpha-node" "$INSTALL_DIR/alpha-node"
sudo chmod +x "$INSTALL_DIR/alpha-node"

# 移除quarantine属性（macOS安全特性）
echo "🔓 Removing quarantine attribute..."
sudo xattr -d com.apple.quarantine "$INSTALL_DIR/alpha-node" 2>/dev/null || true

# 创建配置文件
echo "⚙️  Creating configuration file..."
cat > "$DATA_DIR/config.toml" << EOF
# Alpha Node Configuration

[node]
name = "MyAlphaNode"
chain = "local"
base_path = "$DATA_DIR"

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
EOF

# 创建启动脚本
echo "📝 Creating startup scripts..."
SCRIPTS_DIR="$HOME/.local/bin"
mkdir -p "$SCRIPTS_DIR"

# 轻节点启动脚本
cat > "$SCRIPTS_DIR/alpha-light-node" << EOF
#!/bin/bash
echo "🚀 Starting Alpha Light Node..."
alpha-node \\
    --chain local \\
    --light \\
    --base-path "$DATA_DIR" \\
    --name "AlphaLightNode-\$(hostname)" \\
    --rpc-port 9933 \\
    --ws-port 9944 \\
    --rpc-cors all \\
    --ws-external \\
    --rpc-external
EOF

# 全节点启动脚本
cat > "$SCRIPTS_DIR/alpha-full-node" << EOF
#!/bin/bash
echo "🚀 Starting Alpha Full Node..."
alpha-node \\
    --chain local \\
    --base-path "$DATA_DIR" \\
    --name "AlphaFullNode-\$(hostname)" \\
    --rpc-port 9933 \\
    --ws-port 9944 \\
    --rpc-cors all \\
    --ws-external \\
    --rpc-external
EOF

# 验证者节点启动脚本
cat > "$SCRIPTS_DIR/alpha-validator-node" << EOF
#!/bin/bash
echo "🚀 Starting Alpha Validator Node..."
echo "⚠️  Make sure you have generated and inserted your validator keys!"
alpha-node \\
    --chain local \\
    --validator \\
    --base-path "$DATA_DIR" \\
    --name "AlphaValidator-\$(hostname)" \\
    --rpc-port 9933 \\
    --ws-port 9944 \\
    --rpc-cors all
EOF

chmod +x "$SCRIPTS_DIR/alpha-light-node"
chmod +x "$SCRIPTS_DIR/alpha-full-node"
chmod +x "$SCRIPTS_DIR/alpha-validator-node"

# 添加到PATH
if [[ ":$PATH:" != *":$SCRIPTS_DIR:"* ]]; then
    echo "🔧 Adding to PATH..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bash_profile"
    echo "   Please run: source ~/.zshrc (or restart your terminal)"
fi

# 创建launchd服务文件（macOS服务管理）
echo "🔧 Creating launchd service..."
PLIST_DIR="$HOME/Library/LaunchAgents"
mkdir -p "$PLIST_DIR"

cat > "$PLIST_DIR/com.alphasocial.alphanode.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.alphasocial.alphanode</string>
    <key>ProgramArguments</key>
    <array>
        <string>$INSTALL_DIR/alpha-node</string>
        <string>--chain</string>
        <string>local</string>
        <string>--base-path</string>
        <string>$DATA_DIR</string>
        <string>--name</string>
        <string>AlphaNode-Service</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$DATA_DIR</string>
    <key>StandardOutPath</key>
    <string>$DATA_DIR/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>$DATA_DIR/logs/stderr.log</string>
    <key>KeepAlive</key>
    <true/>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF

# 创建应用程序包（可选）
echo "📱 Creating application bundle..."
APP_DIR="/Applications/Alpha Node.app"
sudo mkdir -p "$APP_DIR/Contents/MacOS"
sudo mkdir -p "$APP_DIR/Contents/Resources"

cat > "/tmp/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>alpha-node-gui</string>
    <key>CFBundleIdentifier</key>
    <string>com.alphasocial.alphanode</string>
    <key>CFBundleName</key>
    <string>Alpha Node</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>
EOF

sudo mv "/tmp/Info.plist" "$APP_DIR/Contents/Info.plist"

# 创建GUI启动器
cat > "/tmp/alpha-node-gui" << 'EOF'
#!/bin/bash
osascript << 'APPLESCRIPT'
tell application "Terminal"
    do script "alpha-full-node"
    activate
end tell
APPLESCRIPT
EOF

sudo mv "/tmp/alpha-node-gui" "$APP_DIR/Contents/MacOS/alpha-node-gui"
sudo chmod +x "$APP_DIR/Contents/MacOS/alpha-node-gui"

echo ""
echo "✅ Alpha Node installation completed!"
echo ""
echo "📁 Installation directory: $INSTALL_DIR"
echo "📁 Data directory: $DATA_DIR"
echo "📁 Configuration file: $DATA_DIR/config.toml"
echo ""
echo "🚀 Quick start commands:"
echo "   Light node:     alpha-light-node"
echo "   Full node:      alpha-full-node"
echo "   Validator node: alpha-validator-node"
echo "   Direct command: alpha-node --help"
echo ""
echo "🔑 To generate validator keys:"
echo "   alpha-node key generate"
echo ""
echo "🔧 To enable auto-start service:"
echo "   launchctl load ~/Library/LaunchAgents/com.alphasocial.alphanode.plist"
echo "   launchctl start com.alphasocial.alphanode"
echo ""
echo "🔧 To disable auto-start service:"
echo "   launchctl stop com.alphasocial.alphanode"
echo "   launchctl unload ~/Library/LaunchAgents/com.alphasocial.alphanode.plist"
echo ""
echo "📱 GUI Application: 'Alpha Node' in Applications folder"
echo ""
echo "📖 For more information, visit:"
echo "   https://github.com/AlphaSNetwork/AlphaSNetwork"

