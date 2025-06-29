# Alpha Social - 精简源码版

## 版本说明

这是Alpha Social项目的精简源码版本，专为Windows用户优化：

✅ **移除了符号链接** - 解决Windows解压问题
✅ **移除了编译产物** - target目录、__pycache__等
✅ **移除了依赖包** - node_modules、Python虚拟环境
✅ **保留了所有源码** - 完整的项目源代码
✅ **保留了所有文档** - 技术文档、部署指南
✅ **更新了GitHub URL** - 所有链接指向 AlphaSNetwork/AlphaSNetwork

## 快速开始

### 1. 解压项目
```bash
unzip alpha-social-source-only.zip
cd alpha-blockchain-clean
```

### 2. 安装依赖并运行

#### 区块链节点 (Rust)
```bash
# 安装Rust (如果需要)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 构建节点
cargo build --release

# 运行开发节点
./target/release/alpha-node --dev
```

#### 前端应用 (React)
```bash
cd alpha-social-frontend
npm install
npm start
```

#### 桌面应用 (Electron)
```bash
cd alpha-social-desktop
npm install
npm run dev
```

#### 后端API (Python)
```bash
cd alpha-social-api
pip install flask flask-cors requests
python src/main.py
```

## 用户节点安装

用户可以直接使用安装脚本：

```bash
# Linux
curl -sSL https://raw.githubusercontent.com/AlphaSNetwork/AlphaSNetwork/main/scripts/install-linux.sh | bash

# Windows (PowerShell)
iwr -useb https://raw.githubusercontent.com/AlphaSNetwork/AlphaSNetwork/main/scripts/install-windows.ps1 | iex

# macOS
curl -sSL https://raw.githubusercontent.com/AlphaSNetwork/AlphaSNetwork/main/scripts/install-macos.sh | bash
```

## 项目结构

```
alpha-blockchain-clean/
├── contracts/           # 智能合约
├── pallets/            # Substrate Pallets
├── runtime/            # 区块链运行时
├── node/               # 节点实现
├── alpha-social-api/   # 后端API
├── alpha-social-frontend/ # Web前端
├── alpha-social-desktop/  # 桌面应用
├── scripts/            # 安装脚本
├── docs/              # 项目文档
├── Cargo.toml         # Rust配置
└── README.md          # 项目说明
```

## 完整功能

- 🔗 完整的区块链源代码
- 💻 Web、移动、桌面应用
- 🪙 AlphaCoin代币系统
- 📱 跨平台节点支持
- 📚 完整的技术文档
- 🔧 自动化部署脚本

这个版本适合开发者下载和二次开发，文件大小更小，在Windows上完全兼容！

