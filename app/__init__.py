# backend/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from .extensions import db
from .config import Config

socketio = SocketIO()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app, supports_credentials=True, origins=["http://localhost:5173"],
         allow_headers=["Authorization", "Content-Type"],
         methods=["GET", "POST", "OPTIONS"],
         expose_headers=["Authorization"])

    # 初始化扩展
    db.init_app(app)

    # 注册蓝图
    from .routes import user_bp, chat_bp
    from .routes import model_bp
    from .routes import vector_bp
    from .routes import finetuning_bp
    from .routes import ollama_bp, ollama_model_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(model_bp)
    app.register_blueprint(finetuning_bp)  # 新增注册 finetuning_bp

    app.register_blueprint(vector_bp)
    app.register_blueprint(ollama_bp)
    app.register_blueprint(ollama_model_bp)

    socketio = SocketIO(app)
    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)

