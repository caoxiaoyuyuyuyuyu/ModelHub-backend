from pathlib import Path
from dotenv import load_dotenv
import os

# 确保从项目根目录加载.env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)  # 显式加载

class Config:
    """
    配置类，用于加载环境变量并设置默认值。
    """
    # 数据库配置
    DB_CONNECTION = os.getenv("DB_CONNECTION", "mysql")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_DATABASE = os.getenv("DB_DATABASE", "modelhub")
    DB_USERNAME = os.getenv("DB_USERNAME", "root")
    # DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    from urllib.parse import quote_plus

    # 修改配置类中的连接字符串
    password = os.getenv("DB_PASSWORD", "")
    encoded_password = quote_plus(password)  # 编码特殊字符

    SQLALCHEMY_DATABASE_URI = f"{DB_CONNECTION}://{DB_USERNAME}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    # SQLALCHEMY_DATABASE_URI = f"{DB_CONNECTION}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 300,
        'pool_pre_ping': True
    }

    # 安全配置
    secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")
    algorithm = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

    # 嵌入模型配置
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")
    EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", "sk-1d8575bdb4ab4b64abde2da910ef578b")

    # ChromaDB 配置
    CHROMA_SERVER_HOST = "localhost"  # 如果使用 Docker 改为 "host.docker.internal"
    CHROMA_SERVER_PORT = 8000

    # 添加 API 路径配置
    CHROMA_API_PATH = "/api/v1"  # 新版本 ChromaDB 使用 /api/v1

    # 获取项目根目录 (Flask应用的上层目录)
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # 上传目录路径
    UPLOADS_DIR = os.path.join(PROJECT_ROOT, 'uploads')