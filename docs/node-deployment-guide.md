# Alpha区块链节点部署指南

## 概述

Alpha区块链支持用户和社区共同维护网络，通过运行节点来参与网络维护并获得代币奖励。本指南将帮助您在Linux、Windows或Mac系统上部署Alpha区块链节点。

## 节点类型

### 轻节点 (Light Node)
- **用途**: 基本的网络参与，验证交易
- **资源要求**: 最低
- **奖励**: 基础参与奖励
- **系统要求**:
  - CPU: 1核心
  - 内存: 1GB
  - 存储: 1GB
  - 网络: 稳定互联网连接

### 全节点 (Full Node)
- **用途**: 存储完整区块链数据，转发交易
- **资源要求**: 中等
- **奖励**: 中等参与奖励
- **系统要求**:
  - CPU: 2核心以上
  - 内存: 4GB以上
  - 存储: 50GB以上
  - 网络: 稳定互联网连接

### 验证者节点 (Validator Node)
- **用途**: 参与共识，生产区块
- **资源要求**: 最高
- **奖励**: 最高验证奖励
- **系统要求**:
  - CPU: 4核心以上
  - 内存: 8GB以上
  - 存储: 100GB以上
  - 网络: 高速稳定互联网连接

## 快速部署

### Linux系统

1. **下载安装脚本**:
   ```bash
   curl -sSL https://raw.githubusercontent.com/AlphaSNetwork/AlphaSNetwork/main/scripts/install-linux.sh | bash
   ```

2. **或手动安装**:
   ```bash
   wget https://github.com/AlphaSNetwork/AlphaSNetwork/releases/latest/download/alpha-node-linux-x86_64
   chmod +x alpha-node-linux-x86_64
   sudo mv alpha-node-linux-x86_64 /usr/local/bin/alpha-node
   ```

3. **启动节点**:
   ```bash
   # 轻节点
   alpha-node --chain local --light --name "MyLightNode"
   
   # 全节点
   alpha-node --chain local --name "MyFullNode"
   
   # 验证者节点（需要先生成密钥）
   alpha-node key generate
   alpha-node --chain local --validator --name "MyValidator"
   ```

### Windows系统

1. **下载安装脚本**:
   - 以管理员身份打开PowerShell
   - 运行: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
   - 运行: `iwr -useb https://raw.githubusercontent.com/AlphaSNetwork/AlphaSNetwork/main/scripts/install-windows.ps1 | iex`

2. **或手动安装**:
   - 下载 `alpha-node-windows-x86_64.exe`
   - 重命名为 `alpha-node.exe`
   - 放置到 `%LOCALAPPDATA%\AlphaNode\` 目录

3. **启动节点**:
   ```cmd
   # 轻节点
   alpha-node.exe --chain local --light --name "MyLightNode"
   
   # 全节点
   alpha-node.exe --chain local --name "MyFullNode"
   
   # 验证者节点
   alpha-node.exe key generate
   alpha-node.exe --chain local --validator --name "MyValidator"
   ```

### macOS系统

1. **下载安装脚本**:
   ```bash
   curl -sSL https://raw.githubusercontent.com/AlphaSNetwork/AlphaSNetwork/main/scripts/install-macos.sh | bash
   ```

2. **或手动安装**:
   ```bash
   # Intel Mac
   curl -L -o alpha-node https://github.com/AlphaSNetwork/AlphaSNetwork/releases/latest/download/alpha-node-macos-x86_64
   
   # Apple Silicon Mac
   curl -L -o alpha-node https://github.com/AlphaSNetwork/AlphaSNetwork/releases/latest/download/alpha-node-macos-arm64
   
   chmod +x alpha-node
   sudo mv alpha-node /usr/local/bin/
   ```

3. **启动节点**:
   ```bash
   # 轻节点
   alpha-node --chain local --light --name "MyLightNode"
   
   # 全节点
   alpha-node --chain local --name "MyFullNode"
   
   # 验证者节点
   alpha-node key generate
   alpha-node --chain local --validator --name "MyValidator"
   ```

## 图形化管理工具

我们提供了跨平台的图形化节点管理工具，让节点管理更加简单：

### 安装Python依赖
```bash
pip install tkinter  # 通常已预装
```

### 运行管理工具
```bash
python scripts/node-manager.py
```

管理工具功能：
- 🚀 一键启动/停止节点
- ⚙️ 图形化配置节点参数
- 📊 实时查看节点状态和日志
- 🔑 生成验证者密钥
- 📁 快速访问数据目录

## 高级配置

### 自定义配置文件

创建配置文件 `config.toml`：

```toml
[node]
name = "MyAlphaNode"
chain = "local"
base_path = "/path/to/data"

[network]
listen_addresses = ["/ip4/0.0.0.0/tcp/30333"]
public_addresses = []
bootnodes = [
    "/ip4/127.0.0.1/tcp/30333/p2p/12D3KooWEyoppNCUx8Yx66oV9fJnriXwCcXwDDUA2kj6vnc6iDEp"
]

[rpc]
port = 9933
cors = ["*"]

[ws]
port = 9944
cors = ["*"]

[telemetry]
enabled = true
url = "wss://telemetry.alpha-social.io/submit/"
```

使用配置文件启动：
```bash
alpha-node --config config.toml
```

### 环境变量配置

```bash
export ALPHA_NODE_NAME="MyNode"
export ALPHA_CHAIN="local"
export ALPHA_BASE_PATH="/custom/path"
export ALPHA_LOG_LEVEL="info"

alpha-node
```

### 服务化部署

#### Linux (systemd)
```bash
sudo tee /etc/systemd/system/alpha-node.service > /dev/null <<EOF
[Unit]
Description=Alpha Blockchain Node
After=network.target

[Service]
Type=simple
User=alpha
ExecStart=/usr/local/bin/alpha-node --chain local --name "AlphaNode-Service"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable alpha-node
sudo systemctl start alpha-node
```

#### Windows (服务)
```powershell
# 以管理员身份运行
New-Service -Name "AlphaNode" -BinaryPathName "C:\AlphaNode\alpha-node.exe --chain local" -DisplayName "Alpha Blockchain Node"
Start-Service AlphaNode
```

#### macOS (launchd)
```bash
# 创建 ~/Library/LaunchAgents/com.alphasocial.alphanode.plist
launchctl load ~/Library/LaunchAgents/com.alphasocial.alphanode.plist
launchctl start com.alphasocial.alphanode
```

## 网络连接

### 端口配置
- **P2P端口**: 30333 (TCP)
- **RPC端口**: 9933 (HTTP)
- **WebSocket端口**: 9944 (WS)

### 防火墙设置

#### Linux (ufw)
```bash
sudo ufw allow 30333/tcp
sudo ufw allow 9933/tcp
sudo ufw allow 9944/tcp
```

#### Windows防火墙
```powershell
New-NetFirewallRule -DisplayName "Alpha Node P2P" -Direction Inbound -Protocol TCP -LocalPort 30333
New-NetFirewallRule -DisplayName "Alpha Node RPC" -Direction Inbound -Protocol TCP -LocalPort 9933
New-NetFirewallRule -DisplayName "Alpha Node WS" -Direction Inbound -Protocol TCP -LocalPort 9944
```

#### macOS防火墙
```bash
# 通过系统偏好设置 > 安全性与隐私 > 防火墙 > 防火墙选项
# 或使用命令行（需要sudo）
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/bin/alpha-node
```

## 验证者节点设置

### 1. 生成密钥
```bash
alpha-node key generate --scheme sr25519 --password-interactive
```

### 2. 插入密钥
```bash
alpha-node key insert --base-path /path/to/data --chain local --scheme sr25519 --suri "your-secret-phrase" --key-type aura
```

### 3. 启动验证者
```bash
alpha-node --chain local --validator --name "MyValidator" --base-path /path/to/data
```

### 4. 注册验证者（通过前端界面）
1. 访问 Alpha Social Web界面
2. 连接钱包
3. 导航到"验证者"页面
4. 点击"注册验证者"
5. 输入验证者信息并提交

## 监控和维护

### 查看节点状态
```bash
# 检查节点是否运行
curl -H "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method": "system_health", "params":[]}' http://localhost:9933/

# 查看节点信息
curl -H "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method": "system_name", "params":[]}' http://localhost:9933/
```

### 日志管理
```bash
# 查看实时日志
tail -f ~/.local/share/alpha-node/logs/alpha-node.log

# 日志轮转（Linux）
sudo logrotate /etc/logrotate.d/alpha-node
```

### 数据备份
```bash
# 备份重要数据
tar -czf alpha-node-backup-$(date +%Y%m%d).tar.gz ~/.local/share/alpha-node/keystore/
```

### 更新节点
```bash
# 停止节点
sudo systemctl stop alpha-node

# 下载新版本
wget https://github.com/AlphaSNetwork/AlphaSNetwork/releases/latest/download/alpha-node-linux-x86_64
sudo mv alpha-node-linux-x86_64 /usr/local/bin/alpha-node
sudo chmod +x /usr/local/bin/alpha-node

# 重启节点
sudo systemctl start alpha-node
```

## 故障排除

### 常见问题

1. **节点无法启动**
   - 检查端口是否被占用
   - 检查数据目录权限
   - 查看错误日志

2. **无法连接到网络**
   - 检查防火墙设置
   - 验证网络连接
   - 检查引导节点配置

3. **同步缓慢**
   - 检查网络带宽
   - 增加连接的对等节点数量
   - 考虑使用快照同步

4. **验证者不活跃**
   - 检查密钥是否正确插入
   - 验证验证者是否已注册
   - 检查节点时间同步

### 获取帮助

- **文档**: https://docs.alpha-social.io
- **GitHub**: https://github.com/AlphaSNetwork/AlphaSNetwork
- **Discord**: https://discord.gg/alpha-social
- **Telegram**: https://t.me/alpha_social

## 奖励机制

### 参与奖励
- **轻节点**: 每日基础奖励
- **全节点**: 数据存储和转发奖励
- **验证者**: 区块生产和验证奖励

### 奖励计算
奖励基于以下因素：
- 节点在线时间
- 网络贡献度
- 验证者性能
- 社区投票

### 奖励领取
奖励将自动发放到节点关联的钱包地址，可通过Alpha Social界面查看和管理。

---

通过运行Alpha区块链节点，您不仅为去中心化社交网络的稳定性做出贡献，还能获得相应的代币奖励。欢迎加入Alpha社区，共同构建更好的去中心化未来！

