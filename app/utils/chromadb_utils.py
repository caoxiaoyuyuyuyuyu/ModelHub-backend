import chromadb
import logging
from app.config import Config
from chromadb.config import Settings

# 初始化日志记录器
logger = logging.getLogger("chromadb_utils")
logger.setLevel(logging.INFO)

# 初始化 ChromDB 客户端
def get_chromadb_client():
    try:
        logger.info(f"尝试连接到 ChromaDB: {Config.CHROMA_SERVER_HOST}:{Config.CHROMA_SERVER_PORT}")

        # 使用新版配置方式
        client = chromadb.HttpClient(
            host=Config.CHROMA_SERVER_HOST,
            port=Config.CHROMA_SERVER_PORT,
            settings=Settings(
                chroma_api_impl="rest",
                chroma_server_host=Config.CHROMA_SERVER_HOST,
                chroma_server_http_port=Config.CHROMA_SERVER_PORT,
            )
        )

        # 检查连接状态
        heartbeat = client.heartbeat()
        logger.info(f"成功连接到 ChromaDB: {heartbeat}")
        return client
    except Exception as e:
        logger.error(f"ChromaDB 连接失败: {str(e)}")
        return None