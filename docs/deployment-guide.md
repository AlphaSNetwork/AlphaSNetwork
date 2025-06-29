# Alpha Social 部署指南

## 概述

本指南将帮助您在生产环境中部署Alpha Social区块链网络和相关应用。我们提供了多种部署方案，从单节点测试到多节点生产网络。

## 部署架构

### 推荐架构

```
┌─────────────────────────────────────────────────────────────┐
│                    生产环境架构                              │
├─────────────────────────────────────────────────────────────┤
│  负载均衡层                                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Nginx     │ │  Cloudflare │ │     CDN     │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│  应用层                                                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │  Frontend   │ │  API Server │ │ Block Explorer│         │
│  │  (React)    │ │  (Flask)    │ │  (Substrate)│           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│  区块链层                                                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ Validator 1 │ │ Validator 2 │ │ Validator 3 │           │
│  │   Node      │ │   Node      │ │   Node      │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│  存储层                                                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ PostgreSQL  │ │    Redis    │ │    IPFS     │           │
│  │  (主数据库)  │ │   (缓存)    │ │ (文件存储)   │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## 环境要求

### 硬件要求

#### 验证者节点
- **CPU**: 8核心 3.0GHz+
- **内存**: 32GB RAM
- **存储**: 1TB NVMe SSD
- **网络**: 1Gbps 带宽，低延迟
- **操作系统**: Ubuntu 22.04 LTS

#### API服务器
- **CPU**: 4核心 2.5GHz+
- **内存**: 16GB RAM
- **存储**: 500GB SSD
- **网络**: 500Mbps 带宽
- **操作系统**: Ubuntu 22.04 LTS

#### 前端服务器
- **CPU**: 2核心 2.0GHz+
- **内存**: 8GB RAM
- **存储**: 100GB SSD
- **网络**: 200Mbps 带宽
- **操作系统**: Ubuntu 22.04 LTS

### 软件要求

```bash
# 基础软件
- Docker 20.10+
- Docker Compose 2.0+
- Git 2.30+
- Nginx 1.20+

# 开发工具（可选）
- Rust 1.70+
- Node.js 18+
- Python 3.11+
```

## 快速部署

### 使用Docker Compose（推荐）

1. **克隆项目**
```bash
git clone https://github.com/alpha-team/alpha-blockchain.git
cd alpha-blockchain
```

2. **配置环境变量**
```bash
cp .env.example .env
nano .env
```

3. **启动服务**
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

4. **验证部署**
```bash
# 检查区块链节点
curl -H "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method": "system_health", "params":[]}' http://localhost:9933

# 检查API服务
curl http://localhost:5000/api/health

# 检查前端应用
curl http://localhost:3000
```

### 环境变量配置

```bash
# .env 文件示例

# 网络配置
NETWORK_NAME=alpha-mainnet
CHAIN_SPEC=mainnet
NODE_KEY=your_node_key_here

# 数据库配置
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=alpha_social
POSTGRES_USER=alpha
POSTGRES_PASSWORD=your_secure_password

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# API配置
API_HOST=0.0.0.0
API_PORT=5000
JWT_SECRET=your_jwt_secret_key
BLOCKCHAIN_WS_URL=ws://blockchain:9944

# 前端配置
REACT_APP_API_URL=http://localhost:5000
REACT_APP_WS_URL=ws://localhost:9944

# IPFS配置
IPFS_API_URL=http://ipfs:5001
IPFS_GATEWAY_URL=http://localhost:8080

# 监控配置
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
```

## 详细部署步骤

### 1. 准备服务器

#### 更新系统
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git htop
```

#### 安装Docker
```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 添加用户到docker组
sudo usermod -aG docker $USER
newgrp docker
```

#### 配置防火墙
```bash
# 开放必要端口
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 30333/tcp   # P2P
sudo ufw allow 9933/tcp    # RPC
sudo ufw allow 9944/tcp    # WebSocket

# 启用防火墙
sudo ufw enable
```

### 2. 部署区块链节点

#### 生成节点密钥
```bash
# 生成节点密钥
docker run --rm -v $(pwd)/keys:/keys parity/substrate:latest key generate-node-key --file /keys/node-key

# 生成会话密钥
docker run --rm -v $(pwd)/keys:/keys parity/substrate:latest key generate --scheme sr25519 --output-type json > keys/session-key.json
```

#### 配置创世区块
```bash
# 编辑创世配置
nano genesis.json

# 验证配置
docker run --rm -v $(pwd):/workspace alpha-blockchain:latest build-spec --chain genesis.json --raw > chain-spec.json
```

#### 启动验证者节点
```bash
# 创建节点配置
mkdir -p data/node1

# 启动节点
docker run -d \
  --name alpha-validator-1 \
  --restart unless-stopped \
  -p 30333:30333 \
  -p 9933:9933 \
  -p 9944:9944 \
  -v $(pwd)/data/node1:/data \
  -v $(pwd)/keys:/keys \
  alpha-blockchain:latest \
  --base-path /data \
  --chain chain-spec.json \
  --validator \
  --node-key-file /keys/node-key \
  --name "Alpha-Validator-1" \
  --telemetry-url "wss://telemetry.polkadot.io/submit/ 0"
```

### 3. 部署API服务

#### 准备数据库
```bash
# 启动PostgreSQL
docker run -d \
  --name alpha-postgres \
  --restart unless-stopped \
  -e POSTGRES_DB=alpha_social \
  -e POSTGRES_USER=alpha \
  -e POSTGRES_PASSWORD=your_secure_password \
  -v postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15

# 启动Redis
docker run -d \
  --name alpha-redis \
  --restart unless-stopped \
  -v redis_data:/data \
  -p 6379:6379 \
  redis:7 redis-server --requirepass your_redis_password
```

#### 部署API服务
```bash
# 构建API镜像
cd alpha-social-api
docker build -t alpha-api:latest .

# 启动API服务
docker run -d \
  --name alpha-api \
  --restart unless-stopped \
  --link alpha-postgres:postgres \
  --link alpha-redis:redis \
  --link alpha-validator-1:blockchain \
  -e DATABASE_URL=postgresql://alpha:your_secure_password@postgres:5432/alpha_social \
  -e REDIS_URL=redis://:your_redis_password@redis:6379/0 \
  -e BLOCKCHAIN_WS_URL=ws://blockchain:9944 \
  -p 5000:5000 \
  alpha-api:latest
```

### 4. 部署前端应用

#### 构建前端
```bash
cd alpha-social-frontend

# 配置环境变量
echo "REACT_APP_API_URL=https://api.alpha-social.com" > .env.production
echo "REACT_APP_WS_URL=wss://ws.alpha-social.com" >> .env.production

# 构建应用
docker build -t alpha-frontend:latest .

# 启动前端服务
docker run -d \
  --name alpha-frontend \
  --restart unless-stopped \
  -p 3000:80 \
  alpha-frontend:latest
```

#### 配置Nginx
```bash
# 创建Nginx配置
sudo nano /etc/nginx/sites-available/alpha-social

# 配置内容
server {
    listen 80;
    server_name alpha-social.com www.alpha-social.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name alpha-social.com www.alpha-social.com;
    
    # SSL配置
    ssl_certificate /etc/letsencrypt/live/alpha-social.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/alpha-social.com/privkey.pem;
    
    # 前端应用
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API服务
    location /api/ {
        proxy_pass http://localhost:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:9944;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}

# 启用站点
sudo ln -s /etc/nginx/sites-available/alpha-social /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. 配置SSL证书

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d alpha-social.com -d www.alpha-social.com

# 设置自动续期
sudo crontab -e
# 添加以下行
0 12 * * * /usr/bin/certbot renew --quiet
```

## 监控和日志

### 部署监控系统

#### Prometheus配置
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'alpha-blockchain'
    static_configs:
      - targets: ['localhost:9615']
  
  - job_name: 'alpha-api'
    static_configs:
      - targets: ['localhost:5000']
  
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
```

#### Grafana仪表板
```bash
# 启动Grafana
docker run -d \
  --name grafana \
  --restart unless-stopped \
  -p 3001:3000 \
  -v grafana_data:/var/lib/grafana \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana:latest

# 导入预配置的仪表板
curl -X POST \
  http://admin:admin@localhost:3001/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @grafana-dashboard.json
```

### 日志管理

#### 配置日志轮转
```bash
# 创建logrotate配置
sudo nano /etc/logrotate.d/alpha-social

# 配置内容
/var/log/alpha-social/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 alpha alpha
    postrotate
        systemctl reload alpha-api
    endscript
}
```

#### 集中日志收集
```bash
# 使用ELK Stack
docker-compose -f elk-stack.yml up -d

# 配置Filebeat
sudo nano /etc/filebeat/filebeat.yml
```

## 备份和恢复

### 数据备份

#### 区块链数据备份
```bash
#!/bin/bash
# backup-blockchain.sh

BACKUP_DIR="/backup/blockchain"
DATA_DIR="/data/node1"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 停止节点
docker stop alpha-validator-1

# 备份数据
tar -czf $BACKUP_DIR/blockchain_backup_$DATE.tar.gz -C $DATA_DIR .

# 重启节点
docker start alpha-validator-1

# 清理旧备份（保留7天）
find $BACKUP_DIR -name "blockchain_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: blockchain_backup_$DATE.tar.gz"
```

#### 数据库备份
```bash
#!/bin/bash
# backup-database.sh

BACKUP_DIR="/backup/database"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份PostgreSQL
docker exec alpha-postgres pg_dump -U alpha alpha_social | gzip > $BACKUP_DIR/postgres_backup_$DATE.sql.gz

# 备份Redis
docker exec alpha-redis redis-cli --rdb /data/dump.rdb
docker cp alpha-redis:/data/dump.rdb $BACKUP_DIR/redis_backup_$DATE.rdb

# 清理旧备份
find $BACKUP_DIR -name "*_backup_*.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*_backup_*.rdb" -mtime +7 -delete

echo "Database backup completed"
```

### 自动备份
```bash
# 添加到crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * /opt/alpha-social/scripts/backup-blockchain.sh
30 2 * * * /opt/alpha-social/scripts/backup-database.sh

# 每周日备份到远程存储
0 3 * * 0 rsync -av /backup/ user@backup-server:/backups/alpha-social/
```

### 灾难恢复

#### 恢复区块链数据
```bash
#!/bin/bash
# restore-blockchain.sh

BACKUP_FILE=$1
DATA_DIR="/data/node1"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# 停止节点
docker stop alpha-validator-1

# 清空数据目录
rm -rf $DATA_DIR/*

# 恢复数据
tar -xzf $BACKUP_FILE -C $DATA_DIR

# 重启节点
docker start alpha-validator-1

echo "Blockchain data restored from $BACKUP_FILE"
```

#### 恢复数据库
```bash
#!/bin/bash
# restore-database.sh

POSTGRES_BACKUP=$1
REDIS_BACKUP=$2

# 恢复PostgreSQL
docker exec -i alpha-postgres psql -U alpha -d alpha_social < <(gunzip -c $POSTGRES_BACKUP)

# 恢复Redis
docker cp $REDIS_BACKUP alpha-redis:/data/dump.rdb
docker restart alpha-redis

echo "Database restored"
```

## 性能优化

### 区块链节点优化

#### 数据库优化
```toml
# 在节点配置中添加
[database]
cache_size = 1024  # MB
state_cache_size = 1024  # MB
```

#### 网络优化
```bash
# 系统网络参数优化
echo 'net.core.rmem_default = 262144' >> /etc/sysctl.conf
echo 'net.core.rmem_max = 16777216' >> /etc/sysctl.conf
echo 'net.core.wmem_default = 262144' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 16777216' >> /etc/sysctl.conf
sysctl -p
```

### API服务优化

#### 连接池配置
```python
# 在API配置中
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 30
REDIS_CONNECTION_POOL_SIZE = 50
```

#### 缓存策略
```python
# Redis缓存配置
CACHE_CONFIG = {
    'user_profile': 3600,      # 1小时
    'content_feed': 300,       # 5分钟
    'trending_topics': 1800,   # 30分钟
}
```

### 前端优化

#### CDN配置
```bash
# 使用Cloudflare CDN
# 在DNS中配置CNAME记录指向Cloudflare
```

#### 静态资源优化
```javascript
// webpack配置
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
      },
    },
  },
};
```

## 安全配置

### 网络安全

#### 防火墙配置
```bash
# 配置iptables规则
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 30333 -j ACCEPT
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
sudo iptables -P INPUT DROP

# 保存规则
sudo iptables-save > /etc/iptables/rules.v4
```

#### DDoS防护
```nginx
# Nginx配置
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

server {
    # API限流
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://localhost:5000;
    }
    
    # 登录限流
    location /api/auth/login {
        limit_req zone=login burst=5 nodelay;
        proxy_pass http://localhost:5000;
    }
}
```

### 应用安全

#### 环境变量加密
```bash
# 使用sops加密敏感配置
sops -e .env > .env.encrypted

# 部署时解密
sops -d .env.encrypted > .env
```

#### 定期安全更新
```bash
#!/bin/bash
# security-update.sh

# 更新系统包
sudo apt update && sudo apt upgrade -y

# 更新Docker镜像
docker-compose pull
docker-compose up -d

# 检查漏洞
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image alpha-blockchain:latest

echo "Security update completed"
```

## 故障排除

### 常见问题

#### 节点同步问题
```bash
# 检查节点状态
curl -H "Content-Type: application/json" \
  -d '{"id":1, "jsonrpc":"2.0", "method": "system_health", "params":[]}' \
  http://localhost:9933

# 检查同步状态
curl -H "Content-Type: application/json" \
  -d '{"id":1, "jsonrpc":"2.0", "method": "system_syncState", "params":[]}' \
  http://localhost:9933

# 重启节点
docker restart alpha-validator-1
```

#### 数据库连接问题
```bash
# 检查数据库连接
docker exec alpha-postgres psql -U alpha -d alpha_social -c "SELECT 1;"

# 检查连接数
docker exec alpha-postgres psql -U alpha -d alpha_social -c "SELECT count(*) FROM pg_stat_activity;"

# 重启数据库
docker restart alpha-postgres
```

#### API服务问题
```bash
# 检查API健康状态
curl http://localhost:5000/api/health

# 查看API日志
docker logs alpha-api -f

# 重启API服务
docker restart alpha-api
```

### 日志分析

#### 区块链日志
```bash
# 查看节点日志
docker logs alpha-validator-1 --tail 100

# 搜索错误信息
docker logs alpha-validator-1 2>&1 | grep -i error

# 实时监控
docker logs alpha-validator-1 -f | grep -E "(ERROR|WARN)"
```

#### 性能监控
```bash
# 系统资源使用
htop
iotop
nethogs

# Docker容器资源使用
docker stats

# 磁盘使用情况
df -h
du -sh /data/*
```

## 升级和维护

### 版本升级

#### 区块链升级
```bash
# 1. 备份数据
./backup-blockchain.sh

# 2. 停止节点
docker stop alpha-validator-1

# 3. 拉取新镜像
docker pull alpha-blockchain:v2.0.0

# 4. 更新配置
# 根据升级说明更新配置文件

# 5. 启动新版本
docker run -d \
  --name alpha-validator-1-v2 \
  # ... 其他参数保持不变
  alpha-blockchain:v2.0.0

# 6. 验证升级
curl -H "Content-Type: application/json" \
  -d '{"id":1, "jsonrpc":"2.0", "method": "system_version", "params":[]}' \
  http://localhost:9933
```

#### 应用升级
```bash
# 使用蓝绿部署
docker-compose -f docker-compose.blue.yml up -d
# 测试新版本
# 切换流量
# 停止旧版本
```

### 定期维护

#### 数据清理
```bash
#!/bin/bash
# cleanup.sh

# 清理Docker镜像
docker image prune -f

# 清理日志文件
find /var/log -name "*.log" -mtime +30 -delete

# 清理临时文件
find /tmp -mtime +7 -delete

# 压缩旧的区块链数据
find /data -name "*.db" -mtime +90 -exec gzip {} \;

echo "Cleanup completed"
```

#### 健康检查
```bash
#!/bin/bash
# health-check.sh

# 检查服务状态
services=("alpha-validator-1" "alpha-postgres" "alpha-redis" "alpha-api" "alpha-frontend")

for service in "${services[@]}"; do
    if docker ps | grep -q $service; then
        echo "✓ $service is running"
    else
        echo "✗ $service is not running"
        # 发送告警
        curl -X POST https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK \
          -H 'Content-type: application/json' \
          --data "{\"text\":\"Alert: $service is down\"}"
    fi
done

# 检查磁盘空间
disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $disk_usage -gt 80 ]; then
    echo "Warning: Disk usage is ${disk_usage}%"
fi

# 检查内存使用
memory_usage=$(free | awk 'NR==2{printf "%.2f", $3*100/$2}')
if (( $(echo "$memory_usage > 80" | bc -l) )); then
    echo "Warning: Memory usage is ${memory_usage}%"
fi
```

---

本部署指南涵盖了Alpha Social的完整部署流程。如需更多帮助，请参考技术文档或联系技术支持团队。

