import chromadb
import logging
import os
from app.config import Config
from chromadb.config import Settings

# 初始化日志记录器
logger = logging.getLogger("chromadb_utils")
logger.setLevel(logging.INFO)

# 初始化 ChromDB 客户端
def get_chromadb_client():
    """
    获取 ChromaDB 客户端
    优先尝试 HTTP 客户端（Docker 服务），如果失败则使用本地持久化客户端
    """
    # 首先尝试使用 HTTP 客户端（Docker 服务）
    try:
        logger.info(f"尝试连接到 ChromaDB 服务器: {Config.CHROMA_SERVER_HOST}:{Config.CHROMA_SERVER_PORT}")
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
        logger.info(f"成功连接到 ChromaDB 服务器: {heartbeat}")
        return client
    except Exception as e:
        logger.warning(f"ChromaDB 服务器连接失败: {str(e)}，尝试使用本地持久化模式")
    
    # 如果 HTTP 客户端失败，使用本地持久化客户端
    try:
        # 创建本地数据目录
        chroma_data_dir = os.path.join(Config.PROJECT_ROOT, "chroma_data")
        os.makedirs(chroma_data_dir, exist_ok=True)
        
        logger.info(f"使用本地 ChromaDB 持久化模式，数据目录: {chroma_data_dir}")
        client = chromadb.PersistentClient(path=chroma_data_dir)
        logger.info("成功初始化本地 ChromaDB 客户端")
        return client
    except Exception as e:
        logger.error(f"本地 ChromaDB 初始化失败: {str(e)}")
        return None