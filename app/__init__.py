# backend/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from .extensions import db, migrate
from .config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['SECRET_KEY'] = 'your-secret-key'

    CORS(app, supports_credentials=True, origins=["http://localhost:5173"],
         allow_headers=["Authorization", "Content-Type"],
         methods=["GET", "POST", "OPTIONS"],
         expose_headers=["Authorization"])

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)

    # 初始化Socket.IO
    socketio.init_app(app)
    
    # 设置安全中间件以过滤扫描尝试
    try:
        from .middleware.security import setup_security_middleware
        setup_security_middleware(app)
    except ImportError:
        # 如果中间件不存在，继续运行（向后兼容）
        pass

    # 注册蓝图
    from .routes import user_bp, chat_bp
    from .routes import model_bp
    from .routes import vector_bp
    from .routes import finetuning_bp
    from .routes import ollama_bp, ollama_model_bp
    from .routes import permission_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(model_bp)
    app.register_blueprint(finetuning_bp)  # 新增注册 finetuning_bp

    app.register_blueprint(vector_bp)
    app.register_blueprint(ollama_bp)
    app.register_blueprint(ollama_model_bp)
    app.register_blueprint(permission_bp)

    return app

socketio = SocketIO(async_mode='threading', cors_allowed_origins="*")
@socketio.on('connect')
def handle_connect():
    print('客户端连接成功')
    return True  # 必须返回True接受连接

@socketio.on('disconnect')
def handle_disconnect(data=None):  # 添加可选参数
    print(f'客户端断开连接，数据: {data}')

# 添加错误处理
@socketio.on_error_default
def default_error_handler(e):
    print(f"WebSocket错误: {str(e)}")
    return False  # 返回False拒绝错误连接

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)

