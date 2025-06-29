#!/bin/bash

# Alpha区块链节点 - Linux安装脚本

set -e

echo "🚀 Alpha Blockchain Node - Linux Installer"
echo "=========================================="

# 检查系统要求
echo "🔍 Checking system requirements..."

# 检查架构
ARCH=$(uname -m)
if [[ "$ARCH" != "x86_64" ]]; then
    echo "❌ Unsupported architecture: $ARCH"
    echo "   Alpha Node currently supports x86_64 only."
    exit 1
fi

# 检查操作系统
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ This installer is for Linux systems only."
    exit 1
fi

# 检查内存
MEMORY_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
MEMORY_MB=$((MEMORY_KB / 1024))
echo "💾 Available Memory: ${MEMORY_MB} MB"

if [[ $MEMORY_MB -lt 1024 ]]; then
    echo "⚠️  Warning: Low memory detected. Minimum 1GB recommended for light node."
fi

# 检查磁盘空间
DISK_SPACE=$(df -BM . | awk 'NR==2 {print $4}' | sed 's/M//')
echo "💿 Available Disk Space: ${DISK_SPACE} MB"

if [[ $DISK_SPACE -lt 1000 ]]; then
    echo "❌ Insufficient disk space. At least 1GB required."
    exit 1
fi

# 创建安装目录
INSTALL_DIR="$HOME/.local/bin"
DATA_DIR="$HOME/.local/share/alpha-node"

echo "📁 Creating directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$DATA_DIR"
mkdir -p "$DATA_DIR/logs"
mkdir -p "$DATA_DIR/db"
mkdir -p "$DATA_DIR/keystore"

# 下载节点程序（这里假设从GitHub releases下载）
echo "⬇️  Downloading Alpha Node binary..."
DOWNLOAD_URL="https://github.com/AlphaSNetwork/AlphaSNetwork/releases/latest/download/alpha-node-linux-x86_64"

if command -v wget &> /dev/null; then
    wget -O "$INSTALL_DIR/alpha-node" "$DOWNLOAD_URL" || {
        echo "⚠️  Download failed. Using local binary if available..."
        if [[ -f "./alpha-node" ]]; then
            cp "./alpha-node" "$INSTALL_DIR/alpha-node"
        else
            echo "❌ No binary found. Please build from source or download manually."
            exit 1
        fi
    }
elif command -v curl &> /dev/null; then
    curl -L -o "$INSTALL_DIR/alpha-node" "$DOWNLOAD_URL" || {
        echo "⚠️  Download failed. Using local binary if available..."
        if [[ -f "./alpha-node" ]]; then
            cp "./alpha-node" "$INSTALL_DIR/alpha-node"
        else
            echo "❌ No binary found. Please build from source or download manually."
            exit 1
        fi
    }
else
    echo "⚠️  Neither wget nor curl found. Using local binary if available..."
    if [[ -f "./alpha-node" ]]; then
        cp "./alpha-node" "$INSTALL_DIR/alpha-node"
    else
        echo "❌ No binary found. Please install wget or curl, then try again."
        exit 1
    fi
fi

# 设置执行权限
chmod +x "$INSTALL_DIR/alpha-node"

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

# 轻节点启动脚本
cat > "$INSTALL_DIR/alpha-light-node" << EOF
#!/bin/bash
echo "🚀 Starting Alpha Light Node..."
"$INSTALL_DIR/alpha-node" \\
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
cat > "$INSTALL_DIR/alpha-full-node" << EOF
#!/bin/bash
echo "🚀 Starting Alpha Full Node..."
"$INSTALL_DIR/alpha-node" \\
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
cat > "$INSTALL_DIR/alpha-validator-node" << EOF
#!/bin/bash
echo "🚀 Starting Alpha Validator Node..."
echo "⚠️  Make sure you have generated and inserted your validator keys!"
"$INSTALL_DIR/alpha-node" \\
    --chain local \\
    --validator \\
    --base-path "$DATA_DIR" \\
    --name "AlphaValidator-\$(hostname)" \\
    --rpc-port 9933 \\
    --ws-port 9944 \\
    --rpc-cors all
EOF

chmod +x "$INSTALL_DIR/alpha-light-node"
chmod +x "$INSTALL_DIR/alpha-full-node"
chmod +x "$INSTALL_DIR/alpha-validator-node"

# 添加到PATH（如果还没有）
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo "🔧 Adding to PATH..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    echo "   Please run: source ~/.bashrc"
    echo "   Or restart your terminal to use alpha-node commands."
fi

# 创建systemd服务文件（可选）
if command -v systemctl &> /dev/null; then
    echo "🔧 Creating systemd service..."
    mkdir -p "$HOME/.config/systemd/user"
    
    cat > "$HOME/.config/systemd/user/alpha-node.service" << EOF
[Unit]
Description=Alpha Blockchain Node
After=network.target

[Service]
Type=simple
ExecStart=$INSTALL_DIR/alpha-full-node
Restart=always
RestartSec=10
User=%i
WorkingDirectory=$DATA_DIR

[Install]
WantedBy=default.target
EOF

    echo "   To enable auto-start: systemctl --user enable alpha-node"
    echo "   To start now: systemctl --user start alpha-node"
    echo "   To check status: systemctl --user status alpha-node"
fi

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
echo "📖 For more information, visit:"
echo "   https://github.com/AlphaSNetwork/AlphaSNetwork"

