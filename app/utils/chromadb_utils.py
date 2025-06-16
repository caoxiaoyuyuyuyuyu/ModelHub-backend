import chromadb
import logging
from app.config import Config

# 初始化日志记录器
logger = logging.getLogger("chromadb_utils")
logger.setLevel(logging.INFO)

# 初始化 ChromDB 客户端
def get_chromadb_client():
    try:
        logger.info(f"尝试连接到 ChromaDB: {Config.CHROMA_SERVER_HOST}:{Config.CHROMA_SERVER_PORT}")
        client = chromadb.HttpClient(host=Config.CHROMA_SERVER_HOST, port=Config.CHROMA_SERVER_PORT)
        logger.info(f"成功连接到 ChromaDB: {client.heartbeat()}")
        return client
    except Exception as e:
        logger.error(f"ChromaDB 连接失败: {str(e)}")
        return None