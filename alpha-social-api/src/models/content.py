"""
内容管理模型
处理社交内容的存储、检索和管理
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from typing import Dict, List, Optional
import hashlib
import json

db = SQLAlchemy()

class Content(db.Model):
    """内容模型"""
    __tablename__ = 'contents'
    
    id = db.Column(db.Integer, primary_key=True)
    content_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    author_id = db.Column(db.String(64), nullable=False, index=True)
    content_type = db.Column(db.String(20), nullable=False)  # text, image, video, audio
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    content_data = db.Column(db.Text)  # JSON格式的内容数据
    ipfs_hash = db.Column(db.String(64))  # IPFS存储哈希
    file_size = db.Column(db.Integer)  # 文件大小（字节）
    mime_type = db.Column(db.String(100))  # MIME类型
    tags = db.Column(db.Text)  # JSON格式的标签列表
    is_public = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 统计信息
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    share_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Content {self.id}: {self.title}>'
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'id': self.id,
            'content_hash': self.content_hash,
            'author_id': self.author_id,
            'content_type': self.content_type,
            'title': self.title,
            'description': self.description,
            'content_data': json.loads(self.content_data) if self.content_data else None,
            'ipfs_hash': self.ipfs_hash,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'tags': json.loads(self.tags) if self.tags else [],
            'is_public': self.is_public,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'share_count': self.share_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def generate_content_hash(content_data: str, author_id: str) -> str:
        """生成内容哈希"""
        data = f"{content_data}{author_id}{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()

class Comment(db.Model):
    """评论模型"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('contents.id'), nullable=False, index=True)
    author_id = db.Column(db.String(64), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))  # 回复的评论ID
    content = db.Column(db.Text, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 统计信息
    like_count = db.Column(db.Integer, default=0)
    reply_count = db.Column(db.Integer, default=0)
    
    # 关系
    content = db.relationship('Content', backref='comments')
    parent = db.relationship('Comment', remote_side=[id], backref='replies')
    
    def __repr__(self):
        return f'<Comment {self.id} on Content {self.content_id}>'
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'id': self.id,
            'content_id': self.content_id,
            'author_id': self.author_id,
            'parent_id': self.parent_id,
            'content': self.content,
            'like_count': self.like_count,
            'reply_count': self.reply_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Like(db.Model):
    """点赞模型"""
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), nullable=False, index=True)
    target_type = db.Column(db.String(20), nullable=False)  # content, comment
    target_id = db.Column(db.Integer, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 复合唯一索引，防止重复点赞
    __table_args__ = (db.UniqueConstraint('user_id', 'target_type', 'target_id'),)
    
    def __repr__(self):
        return f'<Like {self.user_id} -> {self.target_type}:{self.target_id}>'

class Share(db.Model):
    """分享模型"""
    __tablename__ = 'shares'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), nullable=False, index=True)
    content_id = db.Column(db.Integer, db.ForeignKey('contents.id'), nullable=False, index=True)
    platform = db.Column(db.String(50))  # 分享平台
    share_text = db.Column(db.Text)  # 分享时的文字
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    content = db.relationship('Content', backref='shares')
    
    def __repr__(self):
        return f'<Share {self.user_id} -> Content {self.content_id}>'
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_id': self.content_id,
            'platform': self.platform,
            'share_text': self.share_text,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ContentManager:
    """内容管理器"""
    
    @staticmethod
    def create_content(author_id: str, content_type: str, title: str = None, 
                      description: str = None, content_data: Dict = None, 
                      tags: List[str] = None, is_public: bool = True) -> Content:
        """创建内容"""
        content_data_str = json.dumps(content_data) if content_data else None
        content_hash = Content.generate_content_hash(content_data_str or "", author_id)
        
        content = Content(
            content_hash=content_hash,
            author_id=author_id,
            content_type=content_type,
            title=title,
            description=description,
            content_data=content_data_str,
            tags=json.dumps(tags) if tags else None,
            is_public=is_public
        )
        
        db.session.add(content)
        db.session.commit()
        return content
    
    @staticmethod
    def get_content(content_id: int) -> Optional[Content]:
        """获取内容"""
        return Content.query.filter_by(id=content_id, is_deleted=False).first()
    
    @staticmethod
    def get_content_by_hash(content_hash: str) -> Optional[Content]:
        """根据哈希获取内容"""
        return Content.query.filter_by(content_hash=content_hash, is_deleted=False).first()
    
    @staticmethod
    def get_user_contents(author_id: str, limit: int = 20, offset: int = 0) -> List[Content]:
        """获取用户的内容"""
        return Content.query.filter_by(
            author_id=author_id, 
            is_deleted=False, 
            is_public=True
        ).order_by(Content.created_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def get_public_contents(limit: int = 20, offset: int = 0, content_type: str = None) -> List[Content]:
        """获取公开内容"""
        query = Content.query.filter_by(is_deleted=False, is_public=True)
        
        if content_type:
            query = query.filter_by(content_type=content_type)
        
        return query.order_by(Content.created_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def search_contents(keyword: str, limit: int = 20, offset: int = 0) -> List[Content]:
        """搜索内容"""
        return Content.query.filter(
            Content.is_deleted == False,
            Content.is_public == True,
            db.or_(
                Content.title.contains(keyword),
                Content.description.contains(keyword)
            )
        ).order_by(Content.created_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def update_content_stats(content_id: int, stat_type: str, increment: int = 1):
        """更新内容统计"""
        content = Content.query.get(content_id)
        if content:
            if stat_type == 'view':
                content.view_count += increment
            elif stat_type == 'like':
                content.like_count += increment
            elif stat_type == 'comment':
                content.comment_count += increment
            elif stat_type == 'share':
                content.share_count += increment
            
            db.session.commit()
    
    @staticmethod
    def delete_content(content_id: int, author_id: str) -> bool:
        """删除内容（软删除）"""
        content = Content.query.filter_by(id=content_id, author_id=author_id).first()
        if content:
            content.is_deleted = True
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def add_comment(content_id: int, author_id: str, content: str, parent_id: int = None) -> Comment:
        """添加评论"""
        comment = Comment(
            content_id=content_id,
            author_id=author_id,
            content=content,
            parent_id=parent_id
        )
        
        db.session.add(comment)
        
        # 更新内容的评论数
        ContentManager.update_content_stats(content_id, 'comment')
        
        # 如果是回复，更新父评论的回复数
        if parent_id:
            parent_comment = Comment.query.get(parent_id)
            if parent_comment:
                parent_comment.reply_count += 1
        
        db.session.commit()
        return comment
    
    @staticmethod
    def get_comments(content_id: int, limit: int = 20, offset: int = 0) -> List[Comment]:
        """获取评论列表"""
        return Comment.query.filter_by(
            content_id=content_id, 
            is_deleted=False,
            parent_id=None  # 只获取顶级评论
        ).order_by(Comment.created_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def get_comment_replies(comment_id: int, limit: int = 10) -> List[Comment]:
        """获取评论的回复"""
        return Comment.query.filter_by(
            parent_id=comment_id,
            is_deleted=False
        ).order_by(Comment.created_at.asc()).limit(limit).all()
    
    @staticmethod
    def toggle_like(user_id: str, target_type: str, target_id: int) -> bool:
        """切换点赞状态"""
        like = Like.query.filter_by(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id
        ).first()
        
        if like:
            # 取消点赞
            db.session.delete(like)
            if target_type == 'content':
                ContentManager.update_content_stats(target_id, 'like', -1)
            elif target_type == 'comment':
                comment = Comment.query.get(target_id)
                if comment:
                    comment.like_count -= 1
            db.session.commit()
            return False
        else:
            # 添加点赞
            like = Like(user_id=user_id, target_type=target_type, target_id=target_id)
            db.session.add(like)
            if target_type == 'content':
                ContentManager.update_content_stats(target_id, 'like', 1)
            elif target_type == 'comment':
                comment = Comment.query.get(target_id)
                if comment:
                    comment.like_count += 1
            db.session.commit()
            return True
    
    @staticmethod
    def is_liked(user_id: str, target_type: str, target_id: int) -> bool:
        """检查是否已点赞"""
        return Like.query.filter_by(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id
        ).first() is not None
    
    @staticmethod
    def add_share(user_id: str, content_id: int, platform: str = None, share_text: str = None) -> Share:
        """添加分享记录"""
        share = Share(
            user_id=user_id,
            content_id=content_id,
            platform=platform,
            share_text=share_text
        )
        
        db.session.add(share)
        ContentManager.update_content_stats(content_id, 'share')
        db.session.commit()
        return share

