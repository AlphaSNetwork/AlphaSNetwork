"""
社交关系管理API路由
提供关注、私聊、群组等社交功能
"""

from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.blockchain import blockchain_client
from datetime import datetime
import json

social_bp = Blueprint('social', __name__)

# 关注关系模型（简化版，实际应该在models中定义）
class Follow(db.Model):
    """关注关系模型"""
    __tablename__ = 'follows'
    
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.String(64), nullable=False, index=True)
    followed_id = db.Column(db.String(64), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 复合唯一索引，防止重复关注
    __table_args__ = (db.UniqueConstraint('follower_id', 'followed_id'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'follower_id': self.follower_id,
            'followed_id': self.followed_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PrivateMessage(db.Model):
    """私聊消息模型"""
    __tablename__ = 'private_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.String(64), nullable=False, index=True)
    recipient_id = db.Column(db.String(64), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    content_hash = db.Column(db.String(64))  # 区块链上的内容哈希
    message_type = db.Column(db.String(20), default='text')  # text, image, file
    is_read = db.Column(db.Boolean, default=False)
    is_deleted_by_sender = db.Column(db.Boolean, default=False)
    is_deleted_by_recipient = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    read_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'content': self.content,
            'content_hash': self.content_hash,
            'message_type': self.message_type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }

@social_bp.route('/follow', methods=['POST'])
def follow_user():
    """关注用户"""
    try:
        data = request.get_json()
        follower_id = data.get('follower_id')
        followed_id = data.get('followed_id')
        
        if not follower_id or not followed_id:
            return jsonify({'error': 'Missing follower_id or followed_id'}), 400
        
        if follower_id == followed_id:
            return jsonify({'error': 'Cannot follow yourself'}), 400
        
        # 检查是否已经关注
        existing_follow = Follow.query.filter_by(
            follower_id=follower_id,
            followed_id=followed_id
        ).first()
        
        if existing_follow:
            return jsonify({'error': 'Already following this user'}), 400
        
        # 创建关注关系
        follow = Follow(follower_id=follower_id, followed_id=followed_id)
        db.session.add(follow)
        db.session.commit()
        
        # 发送到区块链
        blockchain_result = blockchain_client.follow_user(follower_id, followed_id)
        
        return jsonify({
            'success': True,
            'data': follow.to_dict(),
            'blockchain_tx': blockchain_result.tx_hash if blockchain_result.success else None
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@social_bp.route('/unfollow', methods=['POST'])
def unfollow_user():
    """取消关注用户"""
    try:
        data = request.get_json()
        follower_id = data.get('follower_id')
        followed_id = data.get('followed_id')
        
        if not follower_id or not followed_id:
            return jsonify({'error': 'Missing follower_id or followed_id'}), 400
        
        # 查找关注关系
        follow = Follow.query.filter_by(
            follower_id=follower_id,
            followed_id=followed_id
        ).first()
        
        if not follow:
            return jsonify({'error': 'Not following this user'}), 404
        
        # 删除关注关系
        db.session.delete(follow)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@social_bp.route('/followers/<user_id>', methods=['GET'])
def get_followers(user_id):
    """获取用户的关注者列表"""
    try:
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = int(request.args.get('offset', 0))
        
        followers = Follow.query.filter_by(followed_id=user_id).offset(offset).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [follow.to_dict() for follow in followers],
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': len(followers) == limit
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@social_bp.route('/following/<user_id>', methods=['GET'])
def get_following(user_id):
    """获取用户的关注列表"""
    try:
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = int(request.args.get('offset', 0))
        
        following = Follow.query.filter_by(follower_id=user_id).offset(offset).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [follow.to_dict() for follow in following],
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': len(following) == limit
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@social_bp.route('/follow-status', methods=['GET'])
def get_follow_status():
    """检查关注状态"""
    try:
        follower_id = request.args.get('follower_id')
        followed_id = request.args.get('followed_id')
        
        if not follower_id or not followed_id:
            return jsonify({'error': 'Missing follower_id or followed_id'}), 400
        
        is_following = Follow.query.filter_by(
            follower_id=follower_id,
            followed_id=followed_id
        ).first() is not None
        
        return jsonify({
            'success': True,
            'data': {'is_following': is_following}
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@social_bp.route('/messages', methods=['POST'])
def send_message():
    """发送私聊消息"""
    try:
        data = request.get_json()
        sender_id = data.get('sender_id')
        recipient_id = data.get('recipient_id')
        content = data.get('content')
        message_type = data.get('message_type', 'text')
        
        if not all([sender_id, recipient_id, content]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if sender_id == recipient_id:
            return jsonify({'error': 'Cannot send message to yourself'}), 400
        
        # 创建消息
        message = PrivateMessage(
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            message_type=message_type
        )
        
        db.session.add(message)
        db.session.commit()
        
        # 发送到区块链
        blockchain_result = blockchain_client.send_private_message(
            sender_id, recipient_id, message.content_hash or content[:64]
        )
        
        if blockchain_result.success:
            message.content_hash = blockchain_result.events[0]['data']['content_hash']
            db.session.commit()
        
        return jsonify({
            'success': True,
            'data': message.to_dict(),
            'blockchain_tx': blockchain_result.tx_hash if blockchain_result.success else None
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@social_bp.route('/messages/<int:message_id>/read', methods=['POST'])
def mark_message_read(message_id):
    """标记消息为已读"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        message = PrivateMessage.query.filter_by(
            id=message_id,
            recipient_id=user_id
        ).first()
        
        if not message:
            return jsonify({'error': 'Message not found'}), 404
        
        message.is_read = True
        message.read_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@social_bp.route('/conversations/<user_id>', methods=['GET'])
def get_conversations(user_id):
    """获取用户的对话列表"""
    try:
        # 获取用户参与的所有对话
        conversations = db.session.query(PrivateMessage).filter(
            db.or_(
                PrivateMessage.sender_id == user_id,
                PrivateMessage.recipient_id == user_id
            )
        ).filter(
            db.and_(
                PrivateMessage.is_deleted_by_sender == False,
                PrivateMessage.is_deleted_by_recipient == False
            )
        ).order_by(PrivateMessage.created_at.desc()).all()
        
        # 按对话伙伴分组，只保留最新的消息
        conversation_dict = {}
        for message in conversations:
            partner_id = message.recipient_id if message.sender_id == user_id else message.sender_id
            
            if partner_id not in conversation_dict:
                conversation_dict[partner_id] = {
                    'partner_id': partner_id,
                    'last_message': message.to_dict(),
                    'unread_count': 0
                }
            
            # 计算未读消息数
            if message.recipient_id == user_id and not message.is_read:
                conversation_dict[partner_id]['unread_count'] += 1
        
        conversations_list = list(conversation_dict.values())
        conversations_list.sort(key=lambda x: x['last_message']['created_at'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': conversations_list
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@social_bp.route('/conversations/<user_id>/<partner_id>/messages', methods=['GET'])
def get_conversation_messages(user_id, partner_id):
    """获取与特定用户的对话消息"""
    try:
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))
        
        messages = PrivateMessage.query.filter(
            db.or_(
                db.and_(
                    PrivateMessage.sender_id == user_id,
                    PrivateMessage.recipient_id == partner_id,
                    PrivateMessage.is_deleted_by_sender == False
                ),
                db.and_(
                    PrivateMessage.sender_id == partner_id,
                    PrivateMessage.recipient_id == user_id,
                    PrivateMessage.is_deleted_by_recipient == False
                )
            )
        ).order_by(PrivateMessage.created_at.desc()).offset(offset).limit(limit).all()
        
        # 反转顺序，使最新消息在最后
        messages.reverse()
        
        return jsonify({
            'success': True,
            'data': [message.to_dict() for message in messages],
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': len(messages) == limit
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@social_bp.route('/messages/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    """删除消息"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        message = PrivateMessage.query.get(message_id)
        if not message:
            return jsonify({'error': 'Message not found'}), 404
        
        # 根据用户身份标记删除
        if message.sender_id == user_id:
            message.is_deleted_by_sender = True
        elif message.recipient_id == user_id:
            message.is_deleted_by_recipient = True
        else:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@social_bp.route('/social-stats/<user_id>', methods=['GET'])
def get_social_stats(user_id):
    """获取用户社交统计"""
    try:
        followers_count = Follow.query.filter_by(followed_id=user_id).count()
        following_count = Follow.query.filter_by(follower_id=user_id).count()
        
        # 获取消息统计
        sent_messages = PrivateMessage.query.filter_by(sender_id=user_id).count()
        received_messages = PrivateMessage.query.filter_by(recipient_id=user_id).count()
        unread_messages = PrivateMessage.query.filter_by(
            recipient_id=user_id,
            is_read=False,
            is_deleted_by_recipient=False
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'followers_count': followers_count,
                'following_count': following_count,
                'sent_messages': sent_messages,
                'received_messages': received_messages,
                'unread_messages': unread_messages
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@social_bp.route('/mutual-follows', methods=['GET'])
def get_mutual_follows():
    """获取互相关注的用户"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'Missing user_id parameter'}), 400
        
        # 查找互相关注的用户
        mutual_follows = db.session.query(Follow.followed_id).filter(
            Follow.follower_id == user_id
        ).intersect(
            db.session.query(Follow.follower_id).filter(
                Follow.followed_id == user_id
            )
        ).all()
        
        mutual_follow_ids = [follow[0] for follow in mutual_follows]
        
        return jsonify({
            'success': True,
            'data': mutual_follow_ids
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@social_bp.route('/suggested-users/<user_id>', methods=['GET'])
def get_suggested_users(user_id):
    """获取推荐关注的用户"""
    try:
        limit = min(int(request.args.get('limit', 10)), 50)
        
        # 简单的推荐算法：推荐关注者的关注者
        suggested_users = db.session.query(Follow.followed_id).filter(
            Follow.follower_id.in_(
                db.session.query(Follow.followed_id).filter(
                    Follow.follower_id == user_id
                )
            )
        ).filter(
            Follow.followed_id != user_id
        ).filter(
            ~Follow.followed_id.in_(
                db.session.query(Follow.followed_id).filter(
                    Follow.follower_id == user_id
                )
            )
        ).group_by(Follow.followed_id).limit(limit).all()
        
        suggested_user_ids = [user[0] for user in suggested_users]
        
        return jsonify({
            'success': True,
            'data': suggested_user_ids,
            'algorithm': 'friends_of_friends'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

