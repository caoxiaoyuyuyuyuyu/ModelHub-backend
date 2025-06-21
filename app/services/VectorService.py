# app/services/VectorService.py
from app.mapper import VectorMapper
from app.utils.chromadb_utils import get_chromadb_client
from app.utils.EmbbedingModel import ChatEmbeddings
from app.utils.file_utils import save_uploaded_file
from app.models.vector_db import VectorDb
from app.models.document import Document
from app.extensions import db
from chromadb import HttpClient
import chromadb.errors  # 新增导入
import logging
import os
import uuid
import shutil
import asyncio
import time
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext, load_index_from_storage
)
from llama_index.vector_stores.chroma import ChromaVectorStore

# 初始化日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VectorService")

MAX_RETRIES = 5
RETRY_DELAY = 2
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB文件大小限制
BASE_DOCS_DIR = "data\\vector_docs\\"  # 文档存储基础目录


class VectorService:
    # ... [保持 create_chroma_collection, create_vector_db 等方法不变] ...
    @staticmethod
    async def create_chroma_collection(vector_db_id):
        client = get_chromadb_client()
        if not client:
            logger.error("无法获取 ChromaDB 客户端")
            return False

        collection_name = f"vector_db_{vector_db_id}"
        retries = 0

        while retries < MAX_RETRIES:
            try:
                # 尝试创建集合
                client.create_collection(name=collection_name)
                logger.info(f"成功创建集合: {collection_name}")
                return True
            except chromadb.errors.ChromaError as e:
                # 如果集合已存在，则忽略错误
                if "already exists" in str(e).lower():
                    logger.info(f"集合已存在: {collection_name}")
                    return True

                retries += 1
                logger.warning(f"集合创建失败 (尝试 {retries}/{MAX_RETRIES}): {str(e)}")
                await asyncio.sleep(RETRY_DELAY)
            except Exception as e:
                retries += 1
                logger.error(f"集合操作异常 (尝试 {retries}/{MAX_RETRIES}): {str(e)}")
                await asyncio.sleep(RETRY_DELAY)

        logger.error(f"无法创建集合 {collection_name}，达到最大重试次数")
        return False
    @staticmethod
    async def create_vector_db(user_id, name, embedding_id, describe=None, document_similarity=0.7):
        """创建向量数据库并确保集合存在"""
        vector_db = VectorMapper.create_vector_db(user_id, name, embedding_id, describe, document_similarity)
        if not vector_db or not vector_db.id:
            logger.error("创建向量数据库记录失败")
            return None

        # 确保集合创建成功
        success = await VectorService.create_chroma_collection(vector_db.id)
        if not success:
            logger.error(f"无法为向量数据库 {vector_db.id} 创建ChromaDB集合")

        return vector_db

    @staticmethod
    def ensure_collection_exists(vector_db_id):
        client = get_chromadb_client()
        if not client:
            logger.error("无法获取 ChromaDB 客户端")
            return False

        collection_name = f"vector_db_{vector_db_id}"
        try:
            client.get_collection(name=collection_name)
            return True
        except (ValueError, chromadb.errors.CollectionNotFound):  # 修改异常类型
            try:
                client.create_collection(name=collection_name)
                logger.info(f"同步创建集合: {collection_name}")
                return True
            except Exception as e:
                logger.error(f"同步创建集合失败: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"集合检查异常: {str(e)}")
            return False

    @staticmethod
    def get_vector_db(vector_db_id):
        vector_db = VectorMapper.get_vector_db(vector_db_id)
        if vector_db:
            vector_db_dict = vector_db.to_dict()
            # 确保 model_configs 和 documents 字段包含前端所需的所有字段
            model_configs = []
            for config in vector_db.model_configs:
                config_dict = {
                    'id': config.id,
                    'name': config.name,
                    'describe': config.describe,
                    'created_at': config.create_at.strftime('%Y-%m-%d %H:%M:%S') if config.create_at else None,
                    'updated_at': config.update_at.strftime('%Y-%m-%d %H:%M:%S') if config.update_at else None
                }
                model_configs.append(config_dict)

            documents = []
            for doc in vector_db.stored_documents:
                doc_dict = {
                    'id': doc.id,
                    'name': doc.name,
                    'original_name': doc.original_name,
                    'type': doc.type,
                    'size': doc.size,
                    'save_path': doc.save_path,
                    'describe': doc.describe,
                    'upload_at': doc.upload_at.strftime('%Y-%m-%d %H:%M:%S') if doc.upload_at else None
                }
                documents.append(doc_dict)

            vector_db_dict['model_configs'] = model_configs
            vector_db_dict['documents'] = documents
            return vector_db_dict
        return None

    @staticmethod
    def update_vector_db(vector_db_id, name=None, embedding_id=None, describe=None, document_similarity=None):
        return VectorMapper.update_vector_db(vector_db_id, name, embedding_id, describe, document_similarity)

    @staticmethod
    def delete_vector_db(vector_db_id):
        result = VectorMapper.delete_vector_db(vector_db_id)
        if result:
            try:
                # 删除 ChromDB 集合
                client = get_chromadb_client()
                client.delete_collection(name=f"vector_db_{vector_db_id}")
                logger.info(f"已删除ChromaDB集合: vector_db_{vector_db_id}")
            except ValueError:
                logger.warning(f"ChromaDB 集合 {f'vector_db_{vector_db_id}'} 不存在，无需删除。")
            except Exception as e:
                logger.error(f"删除集合失败: {str(e)}", exc_info=True)
        return result

    @staticmethod
    def insert_vectors(vector_db_id, vectors, metadatas=None, ids=None):
        """插入向量到集合，确保集合存在"""
        # 确保集合存在
        if not VectorService.ensure_collection_exists(vector_db_id):
            logger.error(f"无法确保集合存在: vector_db_{vector_db_id}")
            return False

        client = get_chromadb_client()
        collection_name = f"vector_db_{vector_db_id}"

        try:
            collection = client.get_collection(name=collection_name)
        except Exception as e:
            logger.error(f"获取集合失败: {str(e)}")
            return False

        # 确保ids不为None且长度匹配
        if ids is None:
            ids = [f"id_{i}_{time.time()}" for i in range(len(vectors))]
        elif len(ids) != len(vectors):
            logger.error(f"ID数量({len(ids)})与向量数量({len(vectors)})不匹配")
            return False

        try:
            # 分批次插入以避免过大请求
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch_vectors = vectors[i:i + batch_size]
                batch_metadatas = metadatas[i:i + batch_size] if metadatas else None
                batch_ids = ids[i:i + batch_size]

                collection.add(
                    embeddings=batch_vectors,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )

            logger.info(f"成功插入{len(vectors)}个向量到集合{collection_name}")
            return True
        except Exception as e:
            logger.error(f"向量插入失败: {str(e)}", exc_info=True)
            return False

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
    def upload_file(vector_db_id, file, user_id, describe):  # 添加 user_id 参数
        """上传文件并处理为向量存储 (使用 LlamaIndex + ChromaDB)"""
        filename = getattr(file, 'filename', 'unknown')
        logger.info(f"开始上传文件到向量数据库 {vector_db_id}: {filename}")

        # 1. 保存文件到指定目录
        vector_db_dir = os.path.join(BASE_DOCS_DIR, f"vector_db_{vector_db_id}")
        os.makedirs(vector_db_dir, exist_ok=True)  # 确保目录存在

        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        save_path = os.path.join(vector_db_dir, unique_filename)
        file_saved = False  # 文件保存状态标志

        try:
            # 保存上传的文件
            if hasattr(file, 'save'):
                file.save(save_path)
            elif hasattr(file, 'write'):
                with open(save_path, 'wb') as f:
                    f.write(file.read())
            else:
                with open(save_path, 'wb') as f:
                    shutil.copyfileobj(file, f)

            file_saved = True  # 标记文件已成功保存
            logger.info(f"文件保存成功: {save_path}")

            # 2. 使用 LlamaIndex 处理文件
            # 获取 ChromaDB 集合
            chroma_collection = VectorService.get_chroma_collection(vector_db_id)
            if not chroma_collection:
                logger.error("无法获取 ChromaDB 集合")
                raise Exception("无法获取 ChromaDB 集合")

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
            logger.info(f"成功加载 {len(documents)} 个文档片段")
            for doc in documents:
                print(f"文档元数据: {doc.metadata}")  # 查看默认元数据字段

            # 创建索引并存储
            index = VectorStoreIndex.from_documents(
                documents=documents,
                storage_context=storage_context,
                embed_model=embedding_model
            )
            nodes = storage_context.docstore.docs
            for node_id, node in nodes.items():
                print(f"Node ID: {node_id}")
                print(f"Content: {node.text}")  # 文本内容
                print(f"Metadata: {node.metadata}")  # 元数据
                print("---")

            # 3. 保存文档信息到数据库
            file_extension = os.path.splitext(filename)[1]
            file_type = file_extension[1:] if file_extension else "unknown"

            document = Document(
                user_id=user_id,  # 使用传入的用户ID
                vector_db_id=vector_db_id,
                name=unique_filename,
                describe=describe,
                original_name=filename,
                type=file_type,
                size=os.path.getsize(save_path),
                save_path=save_path,
            )

            db.session.add(document)
            db.session.commit()
            logger.info(f"文件信息已保存到 document 数据库，ID: {document.id}")
            return document.id  # 返回文档ID

        except Exception as e:
            logger.error(f"处理过程中发生错误: {str(e)}", exc_info=True)

            # 错误处理：清理已保存的文件
            if file_saved and os.path.exists(save_path):
                try:
                    os.remove(save_path)
                    logger.info(f"已删除文件: {save_path}")
                except Exception as delete_error:
                    logger.error(f"删除文件失败: {str(delete_error)}")

            # 回滚数据库操作
            db.session.rollback()
            raise Exception(f"文件处理失败: {str(e)}")

    @staticmethod
    def delete_file(document_id):
        try:
            # 从数据库中获取文件记录
            document = Document.query.get(document_id)
            if not document:
                return False

            # 删除文件夹中的文件
            file_path = document.save_path
            if os.path.exists(file_path):
                os.remove(file_path)

            # 删除数据库记录
            db.session.delete(document)
            db.session.commit()

            # 删除向量集合中的相关数据（假设向量集合根据文件名或ID存储数据）
            vector_db_id = document.vector_db_id
            client = get_chromadb_client()
            if client:
                collection_name = f"vector_db_{vector_db_id}"
                try:
                    collection = client.get_collection(name=collection_name)
                    # 假设向量集合中使用文件名作为ID
                    collection.delete(where={"file_name": document.name})
                    # collection.delete(ids=[document.name])
                except Exception as e:
                    print(f"删除向量集合中的数据失败: {str(e)}")

            return True
        except Exception as e:
            db.session.rollback()
            print(f"删除文件失败: {str(e)}")
            return False

    @staticmethod
    def get_user_vector_dbs(user_id):
        try:
            vector_dbs = VectorDb.query.filter_by(user_id=user_id).all()
            vector_db_list = []
            for vector_db in vector_dbs:
                vector_db_dict = {
                    'id': vector_db.id,
                    'name': vector_db.name,
                    'describe': vector_db.describe,
                    'created_at': vector_db.create_at.strftime('%Y-%m-%d %H:%M:%S') if vector_db.create_at else None,
                    'updated_at': vector_db.update_at.strftime('%Y-%m-%d %H:%M:%S') if vector_db.update_at else None
                }
                vector_db_list.append(vector_db_dict)
            return vector_db_list
        except Exception as e:
            logger.error(f"获取用户向量数据库列表失败: {str(e)}")
            return []
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

            # 初始化嵌入模型
            embedding_model = ChatEmbeddings(
                model="text-embedding-v3",
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                api_key="sk-1d8575bdb4ab4b64abde2da910ef578b"
            )

            # 加载索引
            index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                embed_model=embedding_model
            )

            # 创建查询引擎
            retriever = index.as_retriever(similarity_top_k=n_results)
            nodes = retriever.retrieve(query_text)

            document_similarity = VectorMapper.get_vector_db(vector_db_id).document_similarity

            res = []
            for node in nodes:
                if node.score < document_similarity:
                    continue
                file_name = node.metadata.get("file_name")
                if file_name:
                    document = Document.query.filter_by(name=file_name).first()
                    if document:
                        res.append({"text": node.text, "document_name": document.original_name, "score": node.score, "document_id": document.id})

            # 执行查询
            return res
        except Exception as e:
            logger.error(f"向量查询失败: {str(e)}", exc_info=True)
            return None
