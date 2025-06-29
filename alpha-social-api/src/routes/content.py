"""
内容管理API路由
提供内容创建、获取、互动等功能
"""

from flask import Blueprint, request, jsonify
from src.models.content import ContentManager, db
from src.models.blockchain import blockchain_client
import json
from datetime import datetime

content_bp = Blueprint('content', __name__)

@content_bp.route('/contents', methods=['POST'])
def create_content():
    """创建内容"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['author_id', 'content_type', 'content_data']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # 创建内容
        content = ContentManager.create_content(
            author_id=data['author_id'],
            content_type=data['content_type'],
            title=data.get('title'),
            description=data.get('description'),
            content_data=data['content_data'],
            tags=data.get('tags', []),
            is_public=data.get('is_public', True)
        )
        
        # 将内容发布到区块链
        blockchain_result = blockchain_client.create_post(
            account_id=data['author_id'],
            content_hash=content.content_hash
        )
        
        response_data = content.to_dict()
        response_data['blockchain_tx'] = blockchain_result.tx_hash if blockchain_result.success else None
        
        return jsonify({
            'success': True,
            'data': response_data
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/contents/<int:content_id>', methods=['GET'])
def get_content(content_id):
    """获取单个内容"""
    try:
        content = ContentManager.get_content(content_id)
        if not content:
            return jsonify({'error': 'Content not found'}), 404
        
        # 增加浏览次数
        ContentManager.update_content_stats(content_id, 'view')
        
        return jsonify({
            'success': True,
            'data': content.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/contents', methods=['GET'])
def get_contents():
    """获取内容列表"""
    try:
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = int(request.args.get('offset', 0))
        content_type = request.args.get('type')
        author_id = request.args.get('author_id')
        keyword = request.args.get('search')
        
        if author_id:
            contents = ContentManager.get_user_contents(author_id, limit, offset)
        elif keyword:
            contents = ContentManager.search_contents(keyword, limit, offset)
        else:
            contents = ContentManager.get_public_contents(limit, offset, content_type)
        
        return jsonify({
            'success': True,
            'data': [content.to_dict() for content in contents],
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': len(contents) == limit
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/contents/<int:content_id>', methods=['DELETE'])
def delete_content(content_id):
    """删除内容"""
    try:
        data = request.get_json()
        author_id = data.get('author_id')
        
        if not author_id:
            return jsonify({'error': 'Missing author_id'}), 400
        
        success = ContentManager.delete_content(content_id, author_id)
        if not success:
            return jsonify({'error': 'Content not found or unauthorized'}), 404
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/contents/<int:content_id>/comments', methods=['POST'])
def add_comment(content_id):
    """添加评论"""
    try:
        data = request.get_json()
        
        required_fields = ['author_id', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        comment = ContentManager.add_comment(
            content_id=content_id,
            author_id=data['author_id'],
            content=data['content'],
            parent_id=data.get('parent_id')
        )
        
        return jsonify({
            'success': True,
            'data': comment.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/contents/<int:content_id>/comments', methods=['GET'])
def get_comments(content_id):
    """获取评论列表"""
    try:
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = int(request.args.get('offset', 0))
        
        comments = ContentManager.get_comments(content_id, limit, offset)
        
        # 为每个评论获取回复
        comments_data = []
        for comment in comments:
            comment_dict = comment.to_dict()
            if comment.reply_count > 0:
                replies = ContentManager.get_comment_replies(comment.id)
                comment_dict['replies'] = [reply.to_dict() for reply in replies]
            else:
                comment_dict['replies'] = []
            comments_data.append(comment_dict)
        
        return jsonify({
            'success': True,
            'data': comments_data,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': len(comments) == limit
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/contents/<int:content_id>/like', methods=['POST'])
def toggle_content_like(content_id):
    """切换内容点赞状态"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        is_liked = ContentManager.toggle_like(user_id, 'content', content_id)
        
        # 发送到区块链
        if is_liked:
            blockchain_result = blockchain_client.like_post(user_id, content_id)
        
        return jsonify({
            'success': True,
            'data': {
                'is_liked': is_liked,
                'blockchain_tx': blockchain_result.tx_hash if is_liked and blockchain_result.success else None
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/comments/<int:comment_id>/like', methods=['POST'])
def toggle_comment_like(comment_id):
    """切换评论点赞状态"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        is_liked = ContentManager.toggle_like(user_id, 'comment', comment_id)
        
        return jsonify({
            'success': True,
            'data': {'is_liked': is_liked}
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/contents/<int:content_id>/share', methods=['POST'])
def share_content(content_id):
    """分享内容"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        share = ContentManager.add_share(
            user_id=user_id,
            content_id=content_id,
            platform=data.get('platform'),
            share_text=data.get('share_text')
        )
        
        return jsonify({
            'success': True,
            'data': share.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/contents/<int:content_id>/like-status', methods=['GET'])
def get_like_status(content_id):
    """获取点赞状态"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Missing user_id parameter'}), 400
        
        is_liked = ContentManager.is_liked(user_id, 'content', content_id)
        
        return jsonify({
            'success': True,
            'data': {'is_liked': is_liked}
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/trending', methods=['GET'])
def get_trending_contents():
    """获取热门内容"""
    try:
        limit = min(int(request.args.get('limit', 20)), 100)
        time_range = request.args.get('range', '24h')  # 24h, 7d, 30d
        
        # 这里应该根据时间范围和互动数据计算热门内容
        # 为了演示，我们返回按点赞数排序的内容
        from src.models.content import Content
        
        contents = Content.query.filter_by(
            is_deleted=False,
            is_public=True
        ).order_by(
            Content.like_count.desc(),
            Content.created_at.desc()
        ).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [content.to_dict() for content in contents],
            'meta': {
                'time_range': time_range,
                'algorithm': 'like_count_desc'
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/feed', methods=['GET'])
def get_user_feed():
    """获取用户个性化推荐内容"""
    try:
        user_id = request.args.get('user_id')
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = int(request.args.get('offset', 0))
        
        if not user_id:
            return jsonify({'error': 'Missing user_id parameter'}), 400
        
        # 这里应该根据用户的关注列表、兴趣标签等生成个性化推荐
        # 为了演示，我们返回最新的公开内容
        contents = ContentManager.get_public_contents(limit, offset)
        
        return jsonify({
            'success': True,
            'data': [content.to_dict() for content in contents],
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': len(contents) == limit
            },
            'meta': {
                'algorithm': 'latest_public',
                'personalized': False
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/stats', methods=['GET'])
def get_content_stats():
    """获取内容统计信息"""
    try:
        from src.models.content import Content, Comment, Like, Share
        
        total_contents = Content.query.filter_by(is_deleted=False).count()
        total_comments = Comment.query.filter_by(is_deleted=False).count()
        total_likes = Like.query.count()
        total_shares = Share.query.count()
        
        # 今日新增内容
        today = datetime.utcnow().date()
        today_contents = Content.query.filter(
            Content.created_at >= today,
            Content.is_deleted == False
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_contents': total_contents,
                'total_comments': total_comments,
                'total_likes': total_likes,
                'total_shares': total_shares,
                'today_contents': today_contents
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

