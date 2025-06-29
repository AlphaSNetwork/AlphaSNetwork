"""
区块链交互模型
用于与Alpha区块链进行交互
"""

import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import hashlib
import time

@dataclass
class BlockchainConfig:
    """区块链配置"""
    rpc_url: str = "http://127.0.0.1:9933"
    ws_url: str = "ws://127.0.0.1:9944"
    chain_id: str = "alpha"

@dataclass
class TransactionResult:
    """交易结果"""
    success: bool
    tx_hash: Optional[str] = None
    block_hash: Optional[str] = None
    error: Optional[str] = None
    events: List[Dict] = None

class AlphaBlockchainClient:
    """Alpha区块链客户端"""
    
    def __init__(self, config: BlockchainConfig = None):
        self.config = config or BlockchainConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def _make_rpc_call(self, method: str, params: List = None) -> Dict:
        """发起RPC调用"""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or [],
            "id": int(time.time() * 1000)
        }
        
        try:
            response = self.session.post(self.config.rpc_url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_chain_info(self) -> Dict:
        """获取链信息"""
        return self._make_rpc_call("system_chain")
    
    def get_block_number(self) -> int:
        """获取当前区块高度"""
        result = self._make_rpc_call("chain_getHeader")
        if "result" in result and result["result"]:
            return int(result["result"]["number"], 16)
        return 0
    
    def get_account_info(self, account_id: str) -> Dict:
        """获取账户信息"""
        return self._make_rpc_call("system_accountInfo", [account_id])
    
    def get_balance(self, account_id: str) -> int:
        """获取账户余额"""
        result = self.get_account_info(account_id)
        if "result" in result and result["result"]:
            return int(result["result"]["data"]["free"])
        return 0
    
    def create_post(self, account_id: str, content_hash: str, private_key: str = None) -> TransactionResult:
        """创建社交帖子"""
        # 这里应该构造实际的交易并签名
        # 为了演示，我们返回模拟结果
        tx_hash = hashlib.sha256(f"{account_id}{content_hash}{time.time()}".encode()).hexdigest()
        
        return TransactionResult(
            success=True,
            tx_hash=tx_hash,
            block_hash=None,
            events=[{
                "event": "PostCreated",
                "data": {
                    "post_id": int(time.time()),
                    "author": account_id,
                    "content_hash": content_hash
                }
            }]
        )
    
    def like_post(self, account_id: str, post_id: int, private_key: str = None) -> TransactionResult:
        """点赞帖子"""
        tx_hash = hashlib.sha256(f"{account_id}{post_id}{time.time()}".encode()).hexdigest()
        
        return TransactionResult(
            success=True,
            tx_hash=tx_hash,
            events=[{
                "event": "PostLiked",
                "data": {
                    "post_id": post_id,
                    "liker": account_id
                }
            }]
        )
    
    def follow_user(self, follower: str, followed: str, private_key: str = None) -> TransactionResult:
        """关注用户"""
        tx_hash = hashlib.sha256(f"{follower}{followed}{time.time()}".encode()).hexdigest()
        
        return TransactionResult(
            success=True,
            tx_hash=tx_hash,
            events=[{
                "event": "UserFollowed",
                "data": {
                    "follower": follower,
                    "followed": followed
                }
            }]
        )
    
    def send_private_message(self, sender: str, recipient: str, content_hash: str, private_key: str = None) -> TransactionResult:
        """发送私聊消息"""
        tx_hash = hashlib.sha256(f"{sender}{recipient}{content_hash}{time.time()}".encode()).hexdigest()
        
        return TransactionResult(
            success=True,
            tx_hash=tx_hash,
            events=[{
                "event": "PrivateMessageSent",
                "data": {
                    "message_id": int(time.time()),
                    "sender": sender,
                    "recipient": recipient,
                    "content_hash": content_hash
                }
            }]
        )
    
    def get_posts(self, limit: int = 20, offset: int = 0) -> List[Dict]:
        """获取帖子列表"""
        # 这里应该查询区块链状态
        # 为了演示，返回模拟数据
        posts = []
        for i in range(limit):
            posts.append({
                "post_id": offset + i + 1,
                "author": f"user_{(offset + i) % 10}",
                "content_hash": f"Qm{hashlib.sha256(f'post_{offset + i}'.encode()).hexdigest()[:44]}",
                "timestamp": int(time.time()) - (offset + i) * 3600,
                "likes": (offset + i) % 50,
                "comments": (offset + i) % 20
            })
        return posts
    
    def get_user_posts(self, account_id: str, limit: int = 20) -> List[Dict]:
        """获取用户的帖子"""
        # 模拟数据
        posts = []
        for i in range(min(limit, 10)):
            posts.append({
                "post_id": i + 1,
                "author": account_id,
                "content_hash": f"Qm{hashlib.sha256(f'{account_id}_post_{i}'.encode()).hexdigest()[:44]}",
                "timestamp": int(time.time()) - i * 3600,
                "likes": i * 5,
                "comments": i * 2
            })
        return posts
    
    def get_followers(self, account_id: str) -> List[str]:
        """获取关注者列表"""
        # 模拟数据
        return [f"follower_{i}" for i in range(5)]
    
    def get_following(self, account_id: str) -> List[str]:
        """获取关注列表"""
        # 模拟数据
        return [f"following_{i}" for i in range(3)]

# 全局区块链客户端实例
blockchain_client = AlphaBlockchainClient()

