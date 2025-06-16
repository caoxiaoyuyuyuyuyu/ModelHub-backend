# app/services/VectorService.py
from app.mapper import VectorMapper
from app.utils.chromadb_utils import get_chromadb_client
from app.utils.EmbbedingModel import ChatEmbeddings
from app.utils.file_utils import save_uploaded_file
import logging
import os
import uuid
import shutil
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext
)
from llama_index.vector_stores.chroma import ChromaVectorStore

# 初始化日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VectorService")

MAX_RETRIES = 5
RETRY_DELAY = 2
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB文件大小限制
BASE_DOCS_DIR = "./data/vector_docs/"  # 文档存储基础目录


class VectorService:
    # ... [保持 create_chroma_collection, create_vector_db 等方法不变] ...

    @staticmethod
    def get_chroma_collection(vector_db_id):
        """获取 ChromaDB 集合对象"""
        client = get_chromadb_client()
        if not client:
            logger.error("无法获取 ChromaDB 客户端")
            return None

        collection_name = f"vector_db_{vector_db_id}"
        try:
            collection = client.get_collection(name=collection_name)
            return collection
        except Exception as e:
            logger.error(f"获取集合失败: {str(e)}")
            return None

    @staticmethod
    def upload_file(vector_db_id, file):
        """上传文件并处理为向量存储 (使用 LlamaIndex + ChromaDB)"""
        logger.info(f"开始上传文件到向量数据库 {vector_db_id}: {getattr(file, 'filename', 'unknown')}")

        # 1. 保存文件到指定目录
        vector_db_dir = os.path.join(BASE_DOCS_DIR, f"vector_db_{vector_db_id}")
        if not os.path.exists(vector_db_dir):
            os.makedirs(vector_db_dir)

        try:
            # 保存上传的文件
            filename = getattr(file, 'filename', 'unknown')
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            save_path = os.path.join(vector_db_dir, unique_filename)

            if hasattr(file, 'save'):
                file.save(save_path)
            elif hasattr(file, 'write'):
                with open(save_path, 'wb') as f:
                    f.write(file.read())
            else:
                with open(save_path, 'wb') as f:
                    shutil.copyfileobj(file, f)

            logger.info(f"文件保存成功: {save_path}")
        except Exception as e:
            logger.error(f"文件保存失败: {str(e)}")
            return False

        # 2. 使用 LlamaIndex 处理文件
        try:
            # 获取 ChromaDB 集合
            chroma_collection = VectorService.get_chroma_collection(vector_db_id)
            if not chroma_collection:
                logger.error("无法获取 ChromaDB 集合")
                return False

            # 创建向量存储
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)

            # 初始化嵌入模型
            embedding_model = ChatEmbeddings(
                model="text-embedding-v3",
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                api_key="sk-1d8575bdb4ab4b64abde2da910ef578b"
            )

            # 读取并处理文件
            documents = SimpleDirectoryReader(input_files=[save_path]).load_data()

            # 创建索引并存储
            index = VectorStoreIndex.from_documents(
                documents=documents,
                storage_context=storage_context,
                embed_model=embedding_model
            )

            logger.info(f"文件处理成功: {filename}，添加了 {len(documents)} 个文档片段")
            return True
        except Exception as e:
            logger.error(f"向量处理失败: {str(e)}", exc_info=True)
            return False

    @staticmethod
    def query_vectors(vector_db_id, query_text, n_results=10):
        """查询向量数据库 (使用 LlamaIndex)"""
        # 获取 ChromaDB 集合
        chroma_collection = VectorService.get_chroma_collection(vector_db_id)
        if not chroma_collection:
            logger.error("无法获取 ChromaDB 集合")
            return None

        try:
            # 创建向量存储
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)

            # 初始化嵌入模型
            embedding_model = ChatEmbeddings(
                model="text-embedding-v3",
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                api_key="sk-1d8575bdb4ab4b64abde2da910ef578b"
            )

            # 加载索引
            index = VectorStoreIndex([], storage_context=storage_context, embed_model=embedding_model)

            # 创建查询引擎
            query_engine = index.as_query_engine(similarity_top_k=n_results)

            # 执行查询
            response = query_engine.query(query_text)
            return response
        except Exception as e:
            logger.error(f"向量查询失败: {str(e)}", exc_info=True)
            return None