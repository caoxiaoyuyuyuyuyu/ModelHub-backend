from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from .extensions import db
from .config import Config


def create_app(config_class=Config):
    # 指定模板目录为 templates 文件夹，注意这里路径分隔符在 Python 字符串里的正确写法
    app = Flask(__name__, template_folder='E:\\pycharm\\PyCharm 2024.3.5\\CODE\\chixing\\week13\\ModelHub-backend\\templates')
    app.config.from_object(config_class)

    CORS(app, supports_credentials=True, origins=["http://localhost:5173"],
         allow_headers=["Authorization", "Content-Type"],
         methods=["GET", "POST", "OPTIONS"],
         expose_headers=["Authorization"])

    # 初始化扩展
    db.init_app(app)
    migrate = Migrate(app, db)

    # 创建所有数据库表
    with app.app_context():
        db.create_all()

    # 注册蓝图
    from .routes import user_bp, chat_bp, model_bp, vector_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(model_bp)
    app.register_blueprint(vector_bp)

    return app