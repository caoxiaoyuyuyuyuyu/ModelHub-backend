# backend/__init__.py
from flask import Flask
from flask_cors import CORS

from .extensions import db
from .config import Config


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
    from .routes import user_bp, chat_bp, model_bp, vector_bp, ollama_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(model_bp)
    app.register_blueprint(vector_bp)
    app.register_blueprint(ollama_bp)


    return app
