# Alpha Social 技术指南

## 目录

1. [架构概述](#架构概述)
2. [区块链层](#区块链层)
3. [API服务层](#api服务层)
4. [前端应用层](#前端应用层)
5. [开发环境搭建](#开发环境搭建)
6. [核心模块详解](#核心模块详解)
7. [API接口文档](#api接口文档)
8. [数据库设计](#数据库设计)
9. [安全机制](#安全机制)
10. [性能优化](#性能优化)

## 架构概述

Alpha Social 采用分层架构设计，从底层到顶层分为：

### 1. 基础设施层
- **P2P网络**: 基于libp2p的去中心化网络
- **共识机制**: AURA + GRANDPA混合共识
- **存储引擎**: RocksDB持久化存储
- **加密算法**: Ed25519数字签名

### 2. 区块链层
- **Runtime**: Substrate运行时环境
- **Pallets**: 自定义功能模块
- **交易池**: 交易排序和验证
- **状态机**: 区块链状态管理

### 3. API服务层
- **RESTful API**: 标准HTTP接口
- **WebSocket**: 实时通信
- **身份验证**: JWT + 区块链签名
- **数据缓存**: Redis缓存层

### 4. 应用层
- **Web应用**: React单页应用
- **移动端**: PWA渐进式应用
- **桌面端**: Electron跨平台应用

## 区块链层

### Substrate框架

Alpha区块链基于Substrate框架构建，提供了：

- **模块化设计**: 可插拔的功能模块
- **升级机制**: 无分叉升级
- **跨链互操作**: Polkadot生态兼容
- **开发工具**: 完整的开发工具链

### 核心Pallets

#### 1. AlphaCoin Pallet

```rust
// 代币基本信息
pub struct TokenInfo {
    pub name: Vec<u8>,
    pub symbol: Vec<u8>,
    pub decimals: u8,
    pub total_supply: Balance,
}

// 主要功能
impl<T: Config> Pallet<T> {
    // 转账
    pub fn transfer(origin, dest, amount) -> DispatchResult
    
    // 铸造
    pub fn mint(origin, to, amount) -> DispatchResult
    
    // 销毁
    pub fn burn(origin, amount) -> DispatchResult
    
    // 社交奖励
    pub fn reward_social_activity(user, activity_type) -> DispatchResult
}
```

#### 2. AlphaSocial Pallet

```rust
// 用户信息
pub struct UserProfile {
    pub username: Vec<u8>,
    pub bio: Vec<u8>,
    pub avatar_hash: H256,
    pub reputation: u32,
    pub created_at: BlockNumber,
}

// 内容信息
pub struct Content {
    pub id: ContentId,
    pub author: AccountId,
    pub content_hash: H256,
    pub content_type: ContentType,
    pub timestamp: BlockNumber,
    pub likes: u32,
    pub shares: u32,
}

// 主要功能
impl<T: Config> Pallet<T> {
    // 用户注册
    pub fn register_user(origin, username, bio) -> DispatchResult
    
    // 发布内容
    pub fn publish_content(origin, content_hash, content_type) -> DispatchResult
    
    // 社交互动
    pub fn like_content(origin, content_id) -> DispatchResult
    pub fn follow_user(origin, target_user) -> DispatchResult
    
    // 私聊消息
    pub fn send_private_message(origin, recipient, encrypted_message) -> DispatchResult
}
```

### 共识机制

Alpha区块链采用AURA + GRANDPA混合共识：

#### AURA (Authority Round)
- **出块机制**: 轮流出块
- **出块时间**: 6秒
- **验证者选择**: 基于质押权重

#### GRANDPA (GHOST-based Recursive Ancestor Deriving Prefix Agreement)
- **最终确定**: 拜占庭容错
- **确定时间**: 12秒
- **安全保证**: 1/3容错率

### 网络协议

```rust
// P2P网络配置
pub struct NetworkConfig {
    pub listen_addresses: Vec<Multiaddr>,
    pub boot_nodes: Vec<MultiaddrWithPeerId>,
    pub node_key: NodeKeyConfig,
    pub max_peers: u32,
    pub protocol_id: ProtocolId,
}

// 网络消息类型
pub enum NetworkMessage {
    BlockAnnounce(BlockAnnounce),
    BlockRequest(BlockRequest),
    BlockResponse(BlockResponse),
    TransactionAnnounce(TransactionAnnounce),
    Custom(Vec<u8>),
}
```

## API服务层

### Flask应用架构

```python
# 应用结构
alpha_social_api/
├── src/
│   ├── main.py              # 应用入口
│   ├── models/              # 数据模型
│   │   ├── blockchain.py    # 区块链交互
│   │   ├── user.py         # 用户模型
│   │   └── content.py      # 内容模型
│   ├── routes/             # API路由
│   │   ├── auth.py         # 身份验证
│   │   ├── users.py        # 用户管理
│   │   ├── content.py      # 内容管理
│   │   └── social.py       # 社交功能
│   └── utils/              # 工具函数
│       ├── crypto.py       # 加密工具
│       ├── validation.py   # 数据验证
│       └── cache.py        # 缓存管理
```

### 区块链交互

```python
class BlockchainClient:
    def __init__(self, rpc_url, ws_url):
        self.rpc_url = rpc_url
        self.ws_url = ws_url
        self.substrate = SubstrateInterface(url=rpc_url)
    
    def submit_extrinsic(self, call, keypair):
        """提交交易到区块链"""
        extrinsic = self.substrate.create_signed_extrinsic(
            call=call,
            keypair=keypair
        )
        return self.substrate.submit_extrinsic(extrinsic)
    
    def query_storage(self, module, storage_function, params=None):
        """查询区块链状态"""
        return self.substrate.query(
            module=module,
            storage_function=storage_function,
            params=params
        )
    
    def subscribe_events(self, callback):
        """订阅区块链事件"""
        def event_handler(obj, update_nr, subscription_id):
            callback(obj['params']['result'])
        
        self.substrate.subscribe_block_headers(event_handler)
```

### API接口设计

#### 用户管理API

```python
@users_bp.route('/register', methods=['POST'])
def register_user():
    """用户注册"""
    data = request.get_json()
    
    # 验证数据
    username = data.get('username')
    public_key = data.get('public_key')
    signature = data.get('signature')
    
    # 验证签名
    if not verify_signature(username, signature, public_key):
        return jsonify({'error': 'Invalid signature'}), 400
    
    # 提交到区块链
    call = substrate.compose_call(
        call_module='AlphaSocial',
        call_function='register_user',
        call_params={
            'username': username.encode(),
            'bio': data.get('bio', '').encode()
        }
    )
    
    result = blockchain_client.submit_extrinsic(call, keypair)
    return jsonify({'success': True, 'tx_hash': result.extrinsic_hash})

@users_bp.route('/profile/<username>', methods=['GET'])
def get_user_profile(username):
    """获取用户资料"""
    profile = blockchain_client.query_storage(
        module='AlphaSocial',
        storage_function='UserProfiles',
        params=[username.encode()]
    )
    
    if profile:
        return jsonify({
            'username': profile['username'].decode(),
            'bio': profile['bio'].decode(),
            'reputation': profile['reputation'],
            'created_at': profile['created_at']
        })
    else:
        return jsonify({'error': 'User not found'}), 404
```

#### 内容管理API

```python
@content_bp.route('/publish', methods=['POST'])
def publish_content():
    """发布内容"""
    data = request.get_json()
    
    # 上传内容到IPFS
    content_hash = ipfs_client.add_content(data['content'])
    
    # 提交到区块链
    call = substrate.compose_call(
        call_module='AlphaSocial',
        call_function='publish_content',
        call_params={
            'content_hash': content_hash,
            'content_type': data['content_type']
        }
    )
    
    result = blockchain_client.submit_extrinsic(call, user_keypair)
    return jsonify({'success': True, 'content_id': result.content_id})

@content_bp.route('/feed', methods=['GET'])
def get_content_feed():
    """获取内容流"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    # 从区块链查询内容
    contents = blockchain_client.query_storage(
        module='AlphaSocial',
        storage_function='Contents',
        params={'page': page, 'limit': limit}
    )
    
    # 从IPFS获取内容详情
    feed = []
    for content in contents:
        content_data = ipfs_client.get_content(content['content_hash'])
        feed.append({
            'id': content['id'],
            'author': content['author'],
            'content': content_data,
            'timestamp': content['timestamp'],
            'likes': content['likes'],
            'shares': content['shares']
        })
    
    return jsonify({'feed': feed})
```

### 实时通信

```python
from flask_socketio import SocketIO, emit, join_room, leave_room

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('join_chat')
def on_join_chat(data):
    """加入聊天室"""
    room = data['room']
    join_room(room)
    emit('status', {'msg': f'User joined room {room}'}, room=room)

@socketio.on('send_message')
def on_send_message(data):
    """发送消息"""
    room = data['room']
    message = data['message']
    
    # 加密消息
    encrypted_message = encrypt_message(message, room_key)
    
    # 广播到房间
    emit('new_message', {
        'message': encrypted_message,
        'sender': data['sender'],
        'timestamp': time.time()
    }, room=room)
    
    # 保存到区块链（可选）
    if data.get('save_to_blockchain'):
        save_message_to_blockchain(encrypted_message, room)
```

## 前端应用层

### React应用架构

```javascript
// 应用结构
src/
├── components/          # 可复用组件
│   ├── common/         # 通用组件
│   ├── auth/           # 认证组件
│   ├── content/        # 内容组件
│   └── social/         # 社交组件
├── pages/              # 页面组件
│   ├── Home.jsx        # 首页
│   ├── Profile.jsx     # 个人资料
│   ├── Chat.jsx        # 聊天页面
│   └── Settings.jsx    # 设置页面
├── hooks/              # 自定义Hooks
│   ├── useAuth.js      # 认证Hook
│   ├── useBlockchain.js # 区块链Hook
│   └── useSocket.js    # WebSocket Hook
├── services/           # 服务层
│   ├── api.js          # API服务
│   ├── blockchain.js   # 区块链服务
│   └── storage.js      # 存储服务
└── utils/              # 工具函数
    ├── crypto.js       # 加密工具
    ├── validation.js   # 验证工具
    └── constants.js    # 常量定义
```

### 区块链集成

```javascript
// 区块链服务
class BlockchainService {
    constructor() {
        this.api = null;
        this.keyring = new Keyring({ type: 'sr25519' });
    }
    
    async connect(wsUrl) {
        const wsProvider = new WsProvider(wsUrl);
        this.api = await ApiPromise.create({ provider: wsProvider });
        return this.api;
    }
    
    async createAccount(mnemonic) {
        const keyPair = this.keyring.addFromMnemonic(mnemonic);
        return {
            address: keyPair.address,
            publicKey: keyPair.publicKey,
            keyPair: keyPair
        };
    }
    
    async submitTransaction(extrinsic, keyPair) {
        return new Promise((resolve, reject) => {
            extrinsic.signAndSend(keyPair, ({ status, events }) => {
                if (status.isInBlock) {
                    resolve({
                        blockHash: status.asInBlock.toString(),
                        events: events
                    });
                } else if (status.isError) {
                    reject(new Error('Transaction failed'));
                }
            });
        });
    }
    
    async queryStorage(module, method, params = []) {
        return await this.api.query[module][method](...params);
    }
}

// React Hook
export function useBlockchain() {
    const [api, setApi] = useState(null);
    const [account, setAccount] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    
    const blockchainService = useMemo(() => new BlockchainService(), []);
    
    const connect = useCallback(async (wsUrl) => {
        try {
            const api = await blockchainService.connect(wsUrl);
            setApi(api);
            setIsConnected(true);
            return api;
        } catch (error) {
            console.error('Failed to connect to blockchain:', error);
            throw error;
        }
    }, [blockchainService]);
    
    const createAccount = useCallback(async (mnemonic) => {
        const account = await blockchainService.createAccount(mnemonic);
        setAccount(account);
        return account;
    }, [blockchainService]);
    
    const submitTransaction = useCallback(async (extrinsic) => {
        if (!account) throw new Error('No account available');
        return await blockchainService.submitTransaction(extrinsic, account.keyPair);
    }, [blockchainService, account]);
    
    return {
        api,
        account,
        isConnected,
        connect,
        createAccount,
        submitTransaction,
        queryStorage: blockchainService.queryStorage.bind(blockchainService)
    };
}
```

### 状态管理

```javascript
// 认证状态管理
export function useAuth() {
    const [user, setUser] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);
    
    const { account, submitTransaction } = useBlockchain();
    
    const login = useCallback(async (mnemonic) => {
        try {
            setLoading(true);
            
            // 创建账户
            const account = await createAccount(mnemonic);
            
            // 验证用户是否已注册
            const userProfile = await queryStorage('AlphaSocial', 'UserProfiles', [account.address]);
            
            if (userProfile) {
                setUser({
                    address: account.address,
                    username: userProfile.username.toString(),
                    bio: userProfile.bio.toString(),
                    reputation: userProfile.reputation.toNumber()
                });
                setIsAuthenticated(true);
            } else {
                throw new Error('User not registered');
            }
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        } finally {
            setLoading(false);
        }
    }, [createAccount, queryStorage]);
    
    const register = useCallback(async (mnemonic, username, bio) => {
        try {
            setLoading(true);
            
            // 创建账户
            const account = await createAccount(mnemonic);
            
            // 提交注册交易
            const extrinsic = api.tx.alphaSocial.registerUser(username, bio);
            await submitTransaction(extrinsic);
            
            // 设置用户状态
            setUser({
                address: account.address,
                username: username,
                bio: bio,
                reputation: 0
            });
            setIsAuthenticated(true);
        } catch (error) {
            console.error('Registration failed:', error);
            throw error;
        } finally {
            setLoading(false);
        }
    }, [api, createAccount, submitTransaction]);
    
    const logout = useCallback(() => {
        setUser(null);
        setIsAuthenticated(false);
        localStorage.removeItem('user_mnemonic');
    }, []);
    
    return {
        user,
        isAuthenticated,
        loading,
        login,
        register,
        logout
    };
}
```

### PWA功能

```javascript
// Service Worker注册
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// 离线检测
export function useOnlineStatus() {
    const [isOnline, setIsOnline] = useState(navigator.onLine);
    
    useEffect(() => {
        const handleOnline = () => setIsOnline(true);
        const handleOffline = () => setIsOnline(false);
        
        window.addEventListener('online', handleOnline);
        window.addEventListener('offline', handleOffline);
        
        return () => {
            window.removeEventListener('online', handleOnline);
            window.removeEventListener('offline', handleOffline);
        };
    }, []);
    
    return isOnline;
}

// 安装提示
export function useInstallPrompt() {
    const [deferredPrompt, setDeferredPrompt] = useState(null);
    const [isInstallable, setIsInstallable] = useState(false);
    
    useEffect(() => {
        const handleBeforeInstallPrompt = (e) => {
            e.preventDefault();
            setDeferredPrompt(e);
            setIsInstallable(true);
        };
        
        window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
        
        return () => {
            window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
        };
    }, []);
    
    const installApp = useCallback(async () => {
        if (deferredPrompt) {
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            setDeferredPrompt(null);
            setIsInstallable(false);
            return outcome === 'accepted';
        }
        return false;
    }, [deferredPrompt]);
    
    return { isInstallable, installApp };
}
```

## 开发环境搭建

### 1. 系统要求

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y git clang curl libssl-dev llvm libudev-dev make protobuf-compiler

# macOS
brew install protobuf

# Windows (使用WSL2推荐)
```

### 2. Rust环境

```bash
# 安装Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# 安装Substrate工具
cargo install --git https://github.com/paritytech/substrate subkey
cargo install --git https://github.com/paritytech/substrate substrate-node
```

### 3. Node.js环境

```bash
# 安装Node.js (推荐使用nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# 安装pnpm
npm install -g pnpm
```

### 4. Python环境

```bash
# 安装Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. 开发工具

```bash
# VS Code扩展
code --install-extension rust-lang.rust-analyzer
code --install-extension ms-python.python
code --install-extension bradlc.vscode-tailwindcss

# Git配置
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## 核心模块详解

### 1. 用户身份系统

用户身份基于区块链地址，支持多种认证方式：

```rust
// 用户注册流程
pub fn register_user(
    origin: OriginFor<T>,
    username: Vec<u8>,
    bio: Vec<u8>,
) -> DispatchResult {
    let who = ensure_signed(origin)?;
    
    // 检查用户名是否已存在
    ensure!(!UserProfiles::<T>::contains_key(&username), Error::<T>::UsernameExists);
    
    // 检查用户是否已注册
    ensure!(!UserProfiles::<T>::contains_key(&who), Error::<T>::UserExists);
    
    // 创建用户资料
    let profile = UserProfile {
        username: username.clone(),
        bio,
        avatar_hash: Default::default(),
        reputation: 0,
        created_at: <frame_system::Pallet<T>>::block_number(),
    };
    
    // 存储用户资料
    UserProfiles::<T>::insert(&who, &profile);
    UsernameToAccount::<T>::insert(&username, &who);
    
    // 发放注册奖励
    T::Currency::deposit_creating(&who, T::RegistrationReward::get());
    
    // 触发事件
    Self::deposit_event(Event::UserRegistered { account: who, username });
    
    Ok(())
}
```

### 2. 内容管理系统

内容存储采用链上索引 + IPFS存储的混合模式：

```rust
// 内容发布流程
pub fn publish_content(
    origin: OriginFor<T>,
    content_hash: H256,
    content_type: ContentType,
    tags: Vec<Vec<u8>>,
) -> DispatchResult {
    let who = ensure_signed(origin)?;
    
    // 检查用户是否已注册
    ensure!(UserProfiles::<T>::contains_key(&who), Error::<T>::UserNotRegistered);
    
    // 生成内容ID
    let content_id = Self::next_content_id();
    
    // 创建内容记录
    let content = Content {
        id: content_id,
        author: who.clone(),
        content_hash,
        content_type,
        timestamp: <frame_system::Pallet<T>>::block_number(),
        likes: 0,
        shares: 0,
        tags: tags.clone(),
    };
    
    // 存储内容
    Contents::<T>::insert(&content_id, &content);
    UserContents::<T>::append(&who, &content_id);
    
    // 更新内容计数
    NextContentId::<T>::put(content_id + 1);
    
    // 索引标签
    for tag in tags {
        TaggedContents::<T>::append(&tag, &content_id);
    }
    
    // 发放创作奖励
    let reward = T::ContentCreationReward::get();
    T::Currency::deposit_creating(&who, reward);
    
    // 触发事件
    Self::deposit_event(Event::ContentPublished { 
        content_id, 
        author: who, 
        content_hash 
    });
    
    Ok(())
}
```

### 3. 社交互动系统

```rust
// 点赞功能
pub fn like_content(
    origin: OriginFor<T>,
    content_id: ContentId,
) -> DispatchResult {
    let who = ensure_signed(origin)?;
    
    // 检查内容是否存在
    let mut content = Contents::<T>::get(&content_id)
        .ok_or(Error::<T>::ContentNotFound)?;
    
    // 检查是否已点赞
    let like_key = (content_id, who.clone());
    ensure!(!ContentLikes::<T>::contains_key(&like_key), Error::<T>::AlreadyLiked);
    
    // 记录点赞
    ContentLikes::<T>::insert(&like_key, true);
    content.likes += 1;
    Contents::<T>::insert(&content_id, &content);
    
    // 给作者奖励
    let reward = T::LikeReward::get();
    T::Currency::deposit_creating(&content.author, reward);
    
    // 触发事件
    Self::deposit_event(Event::ContentLiked { 
        content_id, 
        liker: who, 
        author: content.author 
    });
    
    Ok(())
}

// 关注功能
pub fn follow_user(
    origin: OriginFor<T>,
    target: T::AccountId,
) -> DispatchResult {
    let who = ensure_signed(origin)?;
    
    // 不能关注自己
    ensure!(who != target, Error::<T>::CannotFollowSelf);
    
    // 检查目标用户是否存在
    ensure!(UserProfiles::<T>::contains_key(&target), Error::<T>::UserNotFound);
    
    // 检查是否已关注
    let follow_key = (who.clone(), target.clone());
    ensure!(!UserFollows::<T>::contains_key(&follow_key), Error::<T>::AlreadyFollowing);
    
    // 记录关注关系
    UserFollows::<T>::insert(&follow_key, true);
    Followers::<T>::append(&target, &who);
    Following::<T>::append(&who, &target);
    
    // 触发事件
    Self::deposit_event(Event::UserFollowed { 
        follower: who, 
        followed: target 
    });
    
    Ok(())
}
```

### 4. 私聊系统

私聊采用端到端加密，消息哈希存储在链上：

```rust
// 发送私聊消息
pub fn send_private_message(
    origin: OriginFor<T>,
    recipient: T::AccountId,
    encrypted_message: Vec<u8>,
    message_hash: H256,
) -> DispatchResult {
    let who = ensure_signed(origin)?;
    
    // 检查接收者是否存在
    ensure!(UserProfiles::<T>::contains_key(&recipient), Error::<T>::UserNotFound);
    
    // 生成消息ID
    let message_id = Self::next_message_id();
    
    // 创建消息记录
    let message = PrivateMessage {
        id: message_id,
        sender: who.clone(),
        recipient: recipient.clone(),
        message_hash,
        timestamp: <frame_system::Pallet<T>>::block_number(),
        read: false,
    };
    
    // 存储消息
    PrivateMessages::<T>::insert(&message_id, &message);
    UserMessages::<T>::append(&recipient, &message_id);
    
    // 更新消息计数
    NextMessageId::<T>::put(message_id + 1);
    
    // 触发事件
    Self::deposit_event(Event::PrivateMessageSent { 
        message_id, 
        sender: who, 
        recipient 
    });
    
    Ok(())
}
```

## API接口文档

### 认证接口

#### POST /api/auth/login
用户登录

**请求参数:**
```json
{
    "mnemonic": "abandon abandon abandon...",
    "signature": "0x1234..."
}
```

**响应:**
```json
{
    "success": true,
    "token": "jwt_token_here",
    "user": {
        "address": "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",
        "username": "alice",
        "bio": "Hello world",
        "reputation": 100
    }
}
```

#### POST /api/auth/register
用户注册

**请求参数:**
```json
{
    "mnemonic": "abandon abandon abandon...",
    "username": "alice",
    "bio": "Hello world",
    "signature": "0x1234..."
}
```

### 用户接口

#### GET /api/users/profile/{username}
获取用户资料

**响应:**
```json
{
    "username": "alice",
    "bio": "Hello world",
    "avatar_url": "https://ipfs.io/ipfs/QmHash",
    "reputation": 100,
    "followers_count": 50,
    "following_count": 30,
    "posts_count": 25,
    "created_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /api/users/profile
更新用户资料

**请求参数:**
```json
{
    "bio": "Updated bio",
    "avatar_file": "base64_encoded_image"
}
```

### 内容接口

#### POST /api/content/publish
发布内容

**请求参数:**
```json
{
    "content": "Hello Alpha Social!",
    "content_type": "text",
    "tags": ["hello", "alpha"],
    "media_files": ["base64_encoded_file"]
}
```

**响应:**
```json
{
    "success": true,
    "content_id": 123,
    "content_hash": "QmHash",
    "tx_hash": "0x1234..."
}
```

#### GET /api/content/feed
获取内容流

**查询参数:**
- `page`: 页码 (默认: 1)
- `limit`: 每页数量 (默认: 20)
- `tag`: 标签过滤
- `author`: 作者过滤

**响应:**
```json
{
    "feed": [
        {
            "id": 123,
            "author": {
                "username": "alice",
                "avatar_url": "https://ipfs.io/ipfs/QmHash"
            },
            "content": "Hello Alpha Social!",
            "content_type": "text",
            "media_urls": ["https://ipfs.io/ipfs/QmHash"],
            "tags": ["hello", "alpha"],
            "timestamp": "2024-01-01T00:00:00Z",
            "likes": 10,
            "shares": 5,
            "comments": 3
        }
    ],
    "pagination": {
        "page": 1,
        "limit": 20,
        "total": 100,
        "has_next": true
    }
}
```

#### POST /api/content/{content_id}/like
点赞内容

**响应:**
```json
{
    "success": true,
    "likes": 11,
    "tx_hash": "0x1234..."
}
```

### 社交接口

#### POST /api/social/follow
关注用户

**请求参数:**
```json
{
    "username": "bob"
}
```

#### GET /api/social/followers/{username}
获取粉丝列表

#### GET /api/social/following/{username}
获取关注列表

### 私聊接口

#### POST /api/chat/send
发送私聊消息

**请求参数:**
```json
{
    "recipient": "bob",
    "message": "encrypted_message_content",
    "message_type": "text"
}
```

#### GET /api/chat/conversations
获取会话列表

#### GET /api/chat/messages/{conversation_id}
获取聊天记录

## 数据库设计

### 链上存储

```rust
// 用户资料
#[pallet::storage]
pub type UserProfiles<T: Config> = StorageMap<
    _,
    Blake2_128Concat,
    T::AccountId,
    UserProfile<T::BlockNumber>,
    OptionQuery,
>;

// 内容存储
#[pallet::storage]
pub type Contents<T: Config> = StorageMap<
    _,
    Blake2_128Concat,
    ContentId,
    Content<T::AccountId, T::BlockNumber>,
    OptionQuery,
>;

// 社交关系
#[pallet::storage]
pub type UserFollows<T: Config> = StorageMap<
    _,
    Blake2_128Concat,
    (T::AccountId, T::AccountId),
    bool,
    ValueQuery,
>;

// 私聊消息
#[pallet::storage]
pub type PrivateMessages<T: Config> = StorageMap<
    _,
    Blake2_128Concat,
    MessageId,
    PrivateMessage<T::AccountId, T::BlockNumber>,
    OptionQuery,
>;
```

### 链下缓存 (Redis)

```python
# 用户会话
user_session:{user_id} = {
    "address": "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",
    "username": "alice",
    "last_active": "2024-01-01T00:00:00Z"
}

# 内容缓存
content:{content_id} = {
    "author": "alice",
    "content": "Hello world",
    "likes": 10,
    "cached_at": "2024-01-01T00:00:00Z"
}

# 关注关系缓存
followers:{username} = ["bob", "charlie", "david"]
following:{username} = ["eve", "frank", "grace"]

# 实时通知
notifications:{user_id} = [
    {
        "type": "like",
        "from": "bob",
        "content_id": 123,
        "timestamp": "2024-01-01T00:00:00Z"
    }
]
```

## 安全机制

### 1. 身份验证

```python
def verify_signature(message, signature, public_key):
    """验证数字签名"""
    try:
        # 使用Ed25519验证签名
        verify_key = VerifyKey(public_key, encoder=HexEncoder)
        verify_key.verify(message.encode(), signature, encoder=HexEncoder)
        return True
    except Exception:
        return False

def generate_jwt_token(user_data):
    """生成JWT令牌"""
    payload = {
        'user_id': user_data['address'],
        'username': user_data['username'],
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')
```

### 2. 数据加密

```javascript
// 端到端加密
class E2EEncryption {
    constructor() {
        this.keyPair = null;
    }
    
    async generateKeyPair() {
        this.keyPair = await crypto.subtle.generateKey(
            {
                name: "ECDH",
                namedCurve: "P-256"
            },
            true,
            ["deriveKey"]
        );
        return this.keyPair;
    }
    
    async deriveSharedKey(publicKey) {
        const sharedKey = await crypto.subtle.deriveKey(
            {
                name: "ECDH",
                public: publicKey
            },
            this.keyPair.privateKey,
            {
                name: "AES-GCM",
                length: 256
            },
            false,
            ["encrypt", "decrypt"]
        );
        return sharedKey;
    }
    
    async encryptMessage(message, sharedKey) {
        const encoder = new TextEncoder();
        const data = encoder.encode(message);
        const iv = crypto.getRandomValues(new Uint8Array(12));
        
        const encrypted = await crypto.subtle.encrypt(
            {
                name: "AES-GCM",
                iv: iv
            },
            sharedKey,
            data
        );
        
        return {
            encrypted: new Uint8Array(encrypted),
            iv: iv
        };
    }
    
    async decryptMessage(encryptedData, iv, sharedKey) {
        const decrypted = await crypto.subtle.decrypt(
            {
                name: "AES-GCM",
                iv: iv
            },
            sharedKey,
            encryptedData
        );
        
        const decoder = new TextDecoder();
        return decoder.decode(decrypted);
    }
}
```

### 3. 权限控制

```rust
// 权限检查宏
macro_rules! ensure_owner {
    ($origin:expr, $owner:expr) => {
        let who = ensure_signed($origin)?;
        ensure!(who == $owner, Error::<T>::NotOwner);
    };
}

// 内容权限检查
pub fn delete_content(
    origin: OriginFor<T>,
    content_id: ContentId,
) -> DispatchResult {
    let content = Contents::<T>::get(&content_id)
        .ok_or(Error::<T>::ContentNotFound)?;
    
    // 只有作者或管理员可以删除
    ensure_owner!(origin, content.author);
    
    // 删除内容
    Contents::<T>::remove(&content_id);
    
    Ok(())
}
```

### 4. 速率限制

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

@app.route('/api/content/publish', methods=['POST'])
@limiter.limit("10 per minute")
def publish_content():
    # 发布内容逻辑
    pass

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # 登录逻辑
    pass
```

## 性能优化

### 1. 区块链优化

```rust
// 批量操作
pub fn batch_like_contents(
    origin: OriginFor<T>,
    content_ids: Vec<ContentId>,
) -> DispatchResult {
    let who = ensure_signed(origin)?;
    
    // 批量处理点赞
    for content_id in content_ids {
        if let Ok(mut content) = Contents::<T>::try_get(&content_id) {
            let like_key = (content_id, who.clone());
            if !ContentLikes::<T>::contains_key(&like_key) {
                ContentLikes::<T>::insert(&like_key, true);
                content.likes += 1;
                Contents::<T>::insert(&content_id, &content);
            }
        }
    }
    
    Ok(())
}

// 存储优化
#[pallet::storage]
#[pallet::getter(fn content_index)]
pub type ContentIndex<T: Config> = StorageMap<
    _,
    Blake2_128Concat,
    T::BlockNumber,
    BoundedVec<ContentId, T::MaxContentsPerBlock>,
    ValueQuery,
>;
```

### 2. API缓存

```python
from functools import wraps
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            
            return result
        return wrapper
    return decorator

@cache_result(expiration=60)
def get_user_profile(username):
    # 获取用户资料逻辑
    pass
```

### 3. 前端优化

```javascript
// 虚拟滚动
import { FixedSizeList as List } from 'react-window';

function ContentFeed({ contents }) {
    const Row = ({ index, style }) => (
        <div style={style}>
            <ContentItem content={contents[index]} />
        </div>
    );
    
    return (
        <List
            height={600}
            itemCount={contents.length}
            itemSize={200}
            width="100%"
        >
            {Row}
        </List>
    );
}

// 图片懒加载
function LazyImage({ src, alt, ...props }) {
    const [isLoaded, setIsLoaded] = useState(false);
    const [isInView, setIsInView] = useState(false);
    const imgRef = useRef();
    
    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    setIsInView(true);
                    observer.disconnect();
                }
            },
            { threshold: 0.1 }
        );
        
        if (imgRef.current) {
            observer.observe(imgRef.current);
        }
        
        return () => observer.disconnect();
    }, []);
    
    return (
        <div ref={imgRef} {...props}>
            {isInView && (
                <img
                    src={src}
                    alt={alt}
                    onLoad={() => setIsLoaded(true)}
                    style={{ opacity: isLoaded ? 1 : 0 }}
                />
            )}
        </div>
    );
}

// 状态管理优化
const ContentContext = createContext();

function ContentProvider({ children }) {
    const [contents, setContents] = useState([]);
    const [loading, setLoading] = useState(false);
    
    const loadContents = useCallback(async (page = 1) => {
        setLoading(true);
        try {
            const response = await api.get(`/content/feed?page=${page}`);
            if (page === 1) {
                setContents(response.data.feed);
            } else {
                setContents(prev => [...prev, ...response.data.feed]);
            }
        } catch (error) {
            console.error('Failed to load contents:', error);
        } finally {
            setLoading(false);
        }
    }, []);
    
    const value = useMemo(() => ({
        contents,
        loading,
        loadContents
    }), [contents, loading, loadContents]);
    
    return (
        <ContentContext.Provider value={value}>
            {children}
        </ContentContext.Provider>
    );
}
```

---

本技术指南涵盖了Alpha Social的核心技术架构和实现细节。如需更多信息，请参考其他文档或联系技术团队。




## 1.1 区块链底层架构设计

为了实现用户和社区共同维护区块链的目标，Alpha Social的底层区块链架构将采用**权益证明（Proof of Stake, PoS）**共识机制的变体，并结合**分层架构**，以支持不同类型的用户节点参与，同时优化数据存储和交互效率。我们将基于Substrate框架进行深度定制，以满足特定的需求。

### 1.1.1 共识机制选择：权益证明（PoS）及其变体

在去中心化网络中，共识机制是确保所有节点对交易顺序和状态达成一致的关键。考虑到用户和社区的广泛参与，以及对能源效率和交易吞吐量的需求，我们选择PoS作为Alpha Social的核心共识机制。与工作量证明（PoW）相比，PoS通过持有和质押代币来获得验证和出块的权利，避免了大量的计算资源消耗，更环保，也更容易实现去中心化治理。

**PoS的优势：**

*   **能源效率**：无需大量计算，降低了节点运行的门槛和成本，鼓励更多用户参与。
*   **去中心化**：只要持有并质押AlphaCoin，任何用户都有机会成为验证者，增加了网络的去中心化程度。
*   **安全性**：通过经济激励和惩罚机制（如罚没，Slashing），确保验证者的行为符合网络利益。
*   **高吞吐量**：通常比PoW具有更高的交易处理能力。

**PoS的挑战及应对：**

*   **富者愈富**：持有更多代币的用户可能获得更多奖励，导致中心化风险。我们将通过设计合理的奖励分配机制和引入委托机制来缓解。
*   **长程攻击**：理论上存在攻击者在链早期进行攻击的风险。Substrate框架提供了多种安全机制来应对此类攻击。

为了进一步增强用户参与度并优化性能，我们可能会考虑PoS的变体，例如**提名权益证明（Nominated Proof of Stake, NPoS）**或**委托权益证明（Delegated Proof of Stake, DPoS）**。

*   **NPoS (Substrate默认)**：允许代币持有者（提名人）提名一组验证者。提名人将其质押的代币委托给验证者，并分享验证者获得的奖励。这使得普通用户无需运行复杂节点也能参与网络安全和获得奖励，降低了参与门槛。
*   **DPoS**：用户通过投票选出少数代表（见证人或超级节点）来负责出块和验证。这种机制通常能提供更高的交易速度和更低的交易费用，但可能牺牲一定的去中心化程度，因为权力集中在少数代表手中。对于Alpha Social，我们更倾向于NPoS，因为它在去中心化和效率之间取得了更好的平衡，同时允许所有代币持有者参与。

### 1.1.2 节点类型及其职责

为了支持用户和社区的广泛参与，Alpha Social网络将支持多种类型的节点，每种节点承担不同的职责并享有相应的权利和奖励。

#### 1. 全节点 (Full Node)

*   **职责**：存储区块链的完整历史数据，包括所有区块和交易。独立验证所有交易和区块的有效性，并将新的区块和交易转发给网络中的其他节点。参与P2P网络，维护网络的完整性和安全性。
*   **参与门槛**：需要较高的存储空间（随着区块链增长而增加）和一定的带宽。对硬件要求相对较高，但普通PC或服务器即可运行。
*   **奖励**：全节点是网络的基石，通过提供数据同步和验证服务，可以获得基础的AlphaCoin奖励，并可能作为轻节点的查询端点获得额外奖励。
*   **重要性**：全节点是去中心化的核心，它们确保了网络的无需信任性，防止了审查和篡改。

#### 2. 轻节点 (Light Node)

*   **职责**：不存储完整的区块链历史，只下载区块头（包含关键信息，如区块哈希、时间戳、状态根等）。它们通过与全节点交互来验证交易，并依赖全节点提供完整的数据。轻节点可以发送交易、查询账户余额等，但不能独立验证所有历史交易。
*   **参与门槛**：对存储和带宽要求极低，可以在资源受限的设备上运行，如智能手机、平板电脑或低功耗设备。
*   **奖励**：轻节点主要通过参与网络连接和数据请求来间接贡献，可能获得少量AlphaCoin奖励，或通过提供特定服务（如数据缓存）获得奖励。
*   **重要性**：轻节点极大地降低了用户参与网络的门槛，使得普通用户也能直接连接到区块链，享受去中心化服务，而无需信任第三方。

#### 3. 验证者节点 (Validator Node)

*   **职责**：参与共识过程，负责创建新区块、验证交易、维护网络安全。验证者需要质押一定数量的AlphaCoin作为保证金，以证明其对网络的承诺。如果验证者行为不当（如双重签名、离线），其质押的代币可能会被罚没。
*   **参与门槛**：需要更高的硬件配置（高性能CPU、大内存、SSD），稳定的网络连接，以及质押大量的AlphaCoin。通常由专业的机构或对网络有较大贡献的社区成员运行。
*   **奖励**：验证者是网络的核心维护者，将获得主要的AlphaCoin奖励，包括区块奖励和交易费用。奖励与质押数量和验证贡献度相关。
*   **重要性**：验证者节点是PoS网络的安全保障，它们确保了交易的最终性和网络的活性。

#### 4. 归档节点 (Archive Node)

*   **职责**：存储区块链的全部历史状态，包括每一个区块的每一个状态转换。这比全节点存储的数据量更大，因为它保留了所有历史状态，而全节点通常只保留当前状态。
*   **参与门槛**：对存储空间要求极高，通常需要数TB甚至更多的数据存储，并且会持续增长。主要用于数据分析、历史查询和审计。
*   **奖励**：通常不直接参与共识，但可能通过提供历史数据查询服务获得奖励。
*   **重要性**：为开发者、分析师和区块浏览器提供完整的历史数据支持。

### 1.1.3 去中心化数据存储与交互

Alpha Social作为社交应用，将涉及大量的非结构化数据，如图片、视频、长文本等。将所有这些数据直接存储在区块链上是不切实际的，因为区块链主要用于存储交易记录和状态，而非海量文件。因此，我们将采用**链上链下结合**的去中心化存储方案。

*   **链上数据**：
    *   **元数据**：存储内容的哈希值（Content ID, CID）、作者信息、时间戳、内容类型、权限设置等关键元数据将存储在Alpha区块链上。这些元数据是不可篡改的，确保了内容的溯源和所有权。
    *   **交易记录**：所有用户行为，如发布内容、点赞、评论、关注、转账等，都将作为交易记录存储在区块链上，确保公开透明和可审计性。
    *   **用户身份**：用户的去中心化身份（DID）和相关密钥信息也将存储在链上。

*   **链下数据（去中心化存储）**：
    *   **文件内容**：实际的图片、视频、长文本等大文件将存储在去中心化存储网络中，例如**IPFS (InterPlanetary File System)**。
    *   **IPFS**：IPFS是一个点对点的分布式文件系统，它通过内容寻址（Content Addressing）来唯一标识文件。当用户上传文件到IPFS时，文件会被分割成小块，并计算出一个唯一的哈希值（CID）。这个CID就是文件的“指纹”，即使文件内容发生微小改变，CID也会完全不同。用户节点可以参与IPFS的存储和内容分发，从而获得奖励。

**数据交互流程：**

1.  **内容发布**：
    *   用户在Alpha Social应用中发布文字、图片或视频。
    *   应用将大文件（图片、视频）上传到IPFS网络，获取对应的CID。
    *   应用将内容的元数据（包括IPFS的CID）作为交易提交到Alpha区块链。
    *   区块链验证者验证交易并将其打包到区块中。
2.  **内容获取**：
    *   用户在Alpha Social应用中浏览内容。
    *   应用从Alpha区块链上查询内容的元数据，获取IPFS的CID。
    *   应用通过IPFS网络（可能通过本地运行的IPFS节点或公共网关）根据CID检索实际的文件内容。
    *   用户节点可以缓存常用内容，提高访问速度。

**用户节点的数据存储与交互职责：**

*   **全节点**：除了维护区块链数据，还可以选择运行IPFS节点，参与IPFS网络的数据存储和分发，为其他轻节点提供内容服务，从而获得额外奖励。
*   **轻节点**：主要从全节点或IPFS网关获取数据，但也可以选择缓存部分常用内容，减少对中心化服务的依赖。

这种链上链下结合的模式，既保证了核心数据的去中心化和不可篡改性，又解决了区块链存储大文件的效率和成本问题，同时鼓励用户通过运行IPFS节点来进一步贡献存储资源，实现真正的去中心化社交数据管理。

### 1.1.4 重新设计AlphaCoin的经济模型（初步）

基于用户和社区共同维护的理念，AlphaCoin (ALC) 的经济模型将进行重新设计，以激励节点参与和生态贡献。

*   **代币总量**：AlphaCoin的总量将固定为**100亿枚**。
*   **项目方持有**：**30% (30亿枚)**的AlphaCoin将由项目方持有。这部分代币将用于：
    *   **研发与运营**：支持Alpha Social的持续开发、维护和生态建设。
    *   **市场推广**：用于用户增长、社区建设和品牌推广。
    *   **团队激励**：激励核心开发团队和早期贡献者，通常会设置锁定期和线性释放机制，以确保长期利益与项目发展绑定。
    *   **生态基金**：用于支持第三方开发者、社区提案和生态系统内的创新项目。
*   **生态流通**：**70% (70亿枚)**的AlphaCoin将在生态中流通，主要通过以下方式分配：
    *   **节点奖励**：
        *   **验证者奖励**：运行验证者节点的参与者将获得区块奖励和交易费用，奖励数量与质押的AlphaCoin数量和验证贡献度成正比。
        *   **全节点/存储节点奖励**：运行全节点并参与IPFS数据存储和分发的用户，将根据其提供的存储空间、带宽和数据服务量获得AlphaCoin奖励。
        *   **轻节点奖励**：轻节点可能通过参与数据缓存、转发或提供特定服务获得少量奖励。
    *   **内容贡献奖励**：高质量的内容创作者、积极的社区互动者（如点赞、评论、分享）将获得AlphaCoin奖励，以激励生态内容的繁荣。
    *   **社区治理奖励**：参与社区治理（如投票、提案）的用户将获得奖励，鼓励用户积极参与项目决策。
    *   **早期社区空投/激励**：用于吸引早期用户和社区成员。
    *   **流动性挖矿/质押挖矿**：提供流动性或质押AlphaCoin的用户将获得额外奖励。

**奖励机制的考量：**

*   **公平性**：奖励机制将力求公平，避免过度中心化，确保小额持有者和普通用户也有机会获得奖励。
*   **可持续性**：奖励的发行速度将与网络发展和用户增长相匹配，避免过度通胀。
*   **透明性**：所有奖励规则和分配都将在区块链上公开透明，可供审计。

### 1.1.5 技术选型与实现考量

*   **区块链框架**：继续使用**Substrate**。Substrate是一个高度模块化和可定制的区块链框架，非常适合构建具有特定功能（如多种节点类型、自定义共识、链上治理）的区块链。它提供了强大的运行时模块（Pallets）系统，可以方便地实现AlphaCoin、用户身份、内容管理、社交关系等功能，并支持NPoS共识。
*   **去中心化存储**：集成**IPFS**。我们将开发Pallet或API接口，用于管理IPFS内容的CID，并激励用户运行IPFS节点。
*   **跨链互操作性**：未来可能考虑通过Substrate的XCMP（跨链消息传递协议）或Polkadot生态系统，实现与其他区块链的互操作性，扩展Alpha Social的应用场景。

通过上述设计，Alpha Social将能够构建一个真正由用户和社区驱动的去中心化社交网络，通过经济激励确保网络的稳定、安全和繁荣。

