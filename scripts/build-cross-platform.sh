#!/bin/bash

# Alpha区块链跨平台构建脚本
# 为Linux、Windows、Mac构建节点程序

set -e

echo "🚀 Alpha Blockchain Cross-Platform Build Script"
echo "================================================"

# 检查Rust环境
if ! command -v cargo &> /dev/null; then
    echo "❌ Cargo not found. Please install Rust first."
    exit 1
fi

# 检查是否安装了交叉编译目标
echo "📦 Installing cross-compilation targets..."
rustup target add x86_64-unknown-linux-gnu
rustup target add x86_64-pc-windows-gnu
rustup target add x86_64-apple-darwin

# 创建构建输出目录
mkdir -p dist/linux
mkdir -p dist/windows
mkdir -p dist/macos

echo "🔨 Building for Linux (x86_64)..."
cargo build --release --target x86_64-unknown-linux-gnu
cp target/x86_64-unknown-linux-gnu/release/alpha-node dist/linux/alpha-node

echo "🔨 Building for Windows (x86_64)..."
if command -v x86_64-w64-mingw32-gcc &> /dev/null; then
    cargo build --release --target x86_64-pc-windows-gnu
    cp target/x86_64-pc-windows-gnu/release/alpha-node.exe dist/windows/alpha-node.exe
else
    echo "⚠️  Windows cross-compilation toolchain not found. Skipping Windows build."
    echo "   To build for Windows, install mingw-w64: sudo apt install gcc-mingw-w64"
fi

echo "🔨 Building for macOS (x86_64)..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    cargo build --release --target x86_64-apple-darwin
    cp target/x86_64-apple-darwin/release/alpha-node dist/macos/alpha-node
else
    echo "⚠️  macOS builds can only be created on macOS systems. Skipping macOS build."
fi

# 创建启动脚本
echo "📝 Creating startup scripts..."

# Linux启动脚本
cat > dist/linux/start-alpha-node.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Alpha Node on Linux..."
./alpha-node --chain local --validator --alice
EOF
chmod +x dist/linux/start-alpha-node.sh

# Windows启动脚本
cat > dist/windows/start-alpha-node.bat << 'EOF'
@echo off
echo 🚀 Starting Alpha Node on Windows...
alpha-node.exe --chain local --validator --alice
pause
EOF

# macOS启动脚本
cat > dist/macos/start-alpha-node.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Alpha Node on macOS..."
./alpha-node --chain local --validator --alice
EOF
chmod +x dist/macos/start-alpha-node.sh

# 创建README文件
cat > dist/README.md << 'EOF'
# Alpha Blockchain Node

## 系统要求

### 验证者节点
- CPU: 4核心以上
- 内存: 8GB以上
- 存储: 100GB以上可用空间
- 网络: 稳定的互联网连接

### 全节点
- CPU: 2核心以上
- 内存: 4GB以上
- 存储: 50GB以上可用空间
- 网络: 稳定的互联网连接

### 轻节点
- CPU: 1核心以上
- 内存: 1GB以上
- 存储: 1GB以上可用空间
- 网络: 稳定的互联网连接

## 安装和运行

### Linux
1. 下载 `linux/alpha-node`
2. 给予执行权限: `chmod +x alpha-node`
3. 运行: `./alpha-node --help` 查看选项
4. 或使用启动脚本: `./start-alpha-node.sh`

### Windows
1. 下载 `windows/alpha-node.exe`
2. 双击运行或在命令行中执行
3. 或使用启动脚本: `start-alpha-node.bat`

### macOS
1. 下载 `macos/alpha-node`
2. 给予执行权限: `chmod +x alpha-node`
3. 运行: `./alpha-node --help` 查看选项
4. 或使用启动脚本: `./start-alpha-node.sh`

## 常用命令

### 启动验证者节点
```bash
./alpha-node --chain local --validator --name MyValidator
```

### 启动全节点
```bash
./alpha-node --chain local --name MyFullNode
```

### 启动轻节点
```bash
./alpha-node --chain local --light --name MyLightNode
```

### 生成账户
```bash
./alpha-node key generate
```

### 查看节点信息
```bash
./alpha-node --version
```

## 配置文件

节点配置文件位置：
- Linux: `~/.local/share/alpha-node/config.toml`
- Windows: `%APPDATA%\AlphaNode\config.toml`
- macOS: `~/Library/Application Support/AlphaNode/config.toml`

## 数据目录

区块链数据存储位置：
- Linux: `~/.local/share/alpha-node/`
- Windows: `%APPDATA%\AlphaNode\`
- macOS: `~/Library/Application Support/AlphaNode/`

## 获取帮助

运行 `./alpha-node --help` 查看所有可用选项和命令。

更多信息请访问: https://github.com/alpha-social/alpha-blockchain
EOF

echo "✅ Cross-platform build completed!"
echo "📁 Build artifacts are in the 'dist' directory:"
echo "   - dist/linux/alpha-node"
echo "   - dist/windows/alpha-node.exe"
echo "   - dist/macos/alpha-node"
echo ""
echo "🎯 Next steps:"
echo "   1. Test the binaries on target platforms"
echo "   2. Create installation packages"
echo "   3. Distribute to users"

