import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.content import content_bp
from src.routes.social import social_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'alpha_social_secret_key_2025'

# 启用CORS支持跨域请求
CORS(app, origins="*")

# 注册蓝图
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(content_bp, url_prefix='/api')
app.register_blueprint(social_bp, url_prefix='/api')

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 创建数据库表
with app.app_context():
    db.create_all()

# API根路径
@app.route('/api', methods=['GET'])
def api_info():
    """API信息"""
    return jsonify({
        'name': 'Alpha Social API',
        'version': '1.0.0',
        'description': 'Alpha区块链社交网络API服务',
        'endpoints': {
            'users': '/api/users',
            'contents': '/api/contents',
            'social': '/api/follow, /api/messages',
            'blockchain': '/api/blockchain-info'
        },
        'blockchain': {
            'network': 'Alpha Network',
            'consensus': 'BABE + GRANDPA',
            'token': 'AlphaCoin (ALC)'
        }
    })

# 区块链信息接口
@app.route('/api/blockchain-info', methods=['GET'])
def blockchain_info():
    """获取区块链信息"""
    from src.models.blockchain import blockchain_client
    
    try:
        chain_info = blockchain_client.get_chain_info()
        block_number = blockchain_client.get_block_number()
        
        return jsonify({
            'success': True,
            'data': {
                'chain': chain_info.get('result', 'Alpha Network'),
                'block_number': block_number,
                'rpc_url': blockchain_client.config.rpc_url,
                'ws_url': blockchain_client.config.ws_url
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 健康检查接口
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': os.popen('date').read().strip(),
        'version': '1.0.0'
    })

# 前端路由处理
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({
                'message': 'Alpha Social API Server',
                'version': '1.0.0',
                'api_docs': '/api'
            })

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Alpha Social API Server...")
    print("📡 Blockchain: Alpha Network")
    print("🔗 API Docs: http://localhost:5000/api")
    print("💾 Database: SQLite")
    print("🌐 CORS: Enabled")
    app.run(host='0.0.0.0', port=5000, debug=True)

