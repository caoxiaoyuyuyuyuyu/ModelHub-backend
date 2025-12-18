# app/services/VectorService.py
from app.mapper import VectorMapper, ModelMapper
from app.utils.TransUtil import get_embedding
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
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.vector_stores.chroma import ChromaVectorStore
from app.models.model_info import ModelInfo

# 初始化日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VectorService")

MAX_RETRIES = 5
RETRY_DELAY = 2
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB文件大小限制
BASE_DOCS_DIR = os.path.join("data", "vector_docs")  # 文档存储基础目录（跨平台路径）


class VectorService:
    @staticmethod
    async def create_chroma_collection(vector_db_id):
        client = get_chromadb_client()
        if not client:
            logger.error("无法获取 ChromaDB 客户端")
            return False

        # 获取向量数据库配置
        vector_db = VectorMapper.get_vector_db(vector_db_id)
        if not vector_db:
            logger.error(f"未找到向量数据库: {vector_db_id}")
            return False

        collection_name = f"vector_db_{vector_db_id}"
        retries = 0

        # 准备集合配置
        distance = vector_db.distance or 'cosine'
        metadata = {}
        if vector_db.collection_metadata:  # 使用collection_metadata字段
            try:
                import json
                metadata = json.loads(vector_db.collection_metadata)
                if not isinstance(metadata, dict):
                    metadata = {}
            except:
                metadata = {}

        while retries < MAX_RETRIES:
            try:
                # 尝试创建集合，使用配置的distance和metadata
                # ChromaDB的distance参数可以直接传递，或者通过metadata设置
                collection_kwargs = {
                    'name': collection_name,
                }
                
                # 如果metadata不为空，添加metadata
                if metadata:
                    collection_kwargs['metadata'] = metadata
                
                # 尝试直接传递distance参数（如果ChromaDB支持）
                try:
                    collection = client.create_collection(**collection_kwargs)
                    # 如果创建成功，尝试设置distance（某些版本可能需要通过其他方式设置）
                    logger.info(f"成功创建集合: {collection_name}, distance: {distance}")
                except TypeError:
                    # 如果不支持distance参数，则只使用name，只有当metadata不为空时才传递
                    if metadata:
                        collection = client.create_collection(name=collection_name, metadata=metadata)
                    else:
                        collection = client.create_collection(name=collection_name)
                    logger.info(f"成功创建集合: {collection_name} (使用默认distance)")
                
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
    async def create_vector_db(user_id, name, embedding_id, describe=None, document_similarity=0.7,
                              distance='cosine', metadata=None, chunk_size=1024, chunk_overlap=200, topk=10):
        """创建向量数据库并确保集合存在"""
        vector_db = VectorMapper.create_vector_db(
            user_id, name, embedding_id, describe, document_similarity,
            distance, metadata, chunk_size, chunk_overlap, topk
        )
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
        except (ValueError, chromadb.errors.NotFoundError):  # 修改异常类型
            try:
                # 获取向量数据库配置
                vector_db = VectorMapper.get_vector_db(vector_db_id)
                if vector_db:
                    metadata = {}
                    if vector_db.collection_metadata:  # 使用collection_metadata字段
                        try:
                            import json
                            metadata = json.loads(vector_db.collection_metadata)
                            if not isinstance(metadata, dict):
                                metadata = {}
                        except:
                            metadata = {}
                    
                    collection_kwargs = {
                        'name': collection_name,
                    }
                    if metadata:
                        collection_kwargs['metadata'] = metadata
                    
                    try:
                        client.create_collection(**collection_kwargs)
                    except TypeError:
                        # 只有当metadata不为空时才传递metadata参数
                        if metadata:
                            client.create_collection(name=collection_name, metadata=metadata)
                        else:
                            client.create_collection(name=collection_name)
                else:
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
            # 添加日志，查看文档数量和详情
            documents_count = len(vector_db_dict.get('documents', []))
            logger.info(f"获取向量数据库 {vector_db_id} 的文档列表，共 {documents_count} 个文档")
            # 记录每个文档的 save_path 状态（用于调试）
            for doc in vector_db_dict.get('documents', []):
                logger.debug(f"文档 ID: {doc.get('id')}, 名称: {doc.get('original_name')}, save_path: {doc.get('save_path')}")
            # 确保返回所有文档，不过滤 save_path 为空的文档
            # to_dict() 已经包含了所有文档，不需要额外处理
            return vector_db_dict
        return None

    @staticmethod
    def get_documents_paginated(vector_db_id, page=1, page_size=20):
        """获取向量数据库的文档列表（分页）"""
        vector_db = VectorMapper.get_vector_db(vector_db_id)
        if not vector_db:
            return None
        
        # 查询文档总数
        total = Document.query.filter_by(vector_db_id=vector_db_id).count()
        
        # 分页查询文档
        offset = (page - 1) * page_size
        documents = Document.query.filter_by(vector_db_id=vector_db_id)\
            .order_by(Document.upload_at.desc())\
            .offset(offset)\
            .limit(page_size)\
            .all()
        
        # 转换为字典列表
        documents_list = [doc.to_dict() for doc in documents]
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        logger.info(f"获取向量数据库 {vector_db_id} 的文档列表，页码: {page}, 每页: {page_size}, 总数: {total}, 当前页文档数: {len(documents_list)}")
        
        return {
            'documents': documents_list,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': total_pages
            }
        }

    @staticmethod
    def update_vector_db(vector_db_id, name=None, embedding_id=None, describe=None, document_similarity=None,
                        distance=None, metadata=None, chunk_size=None, chunk_overlap=None, topk=None):
        return VectorMapper.update_vector_db(
            vector_db_id, name, embedding_id, describe, document_similarity,
            distance, metadata, chunk_size, chunk_overlap, topk
        )

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
        """获取 ChromaDB 集合对象，如果不存在则创建"""
        client = get_chromadb_client()
        if not client:
            logger.error("无法获取 ChromaDB 客户端")
            return None

        collection_name = f"vector_db_{vector_db_id}"
        try:
            # 尝试获取集合
            collection = client.get_collection(name=collection_name)
            return collection
        except (ValueError, chromadb.errors.NotFoundError) as e:
            # 集合不存在，尝试创建
            logger.info(f"集合 {collection_name} 不存在，尝试创建...")
            try:
                # 获取向量数据库配置
                vector_db = VectorMapper.get_vector_db(vector_db_id)
                if vector_db:
                    distance = vector_db.distance or 'cosine'
                    metadata = {}
                    if vector_db.collection_metadata:
                        try:
                            import json
                            metadata = json.loads(vector_db.collection_metadata)
                            if not isinstance(metadata, dict):
                                metadata = {}
                        except:
                            metadata = {}
                    
                    # 创建集合
                    try:
                        # 只有当 metadata 不为空时才传递 metadata 参数
                        if metadata:
                            collection = client.create_collection(
                                name=collection_name,
                                metadata=metadata
                            )
                        else:
                            collection = client.create_collection(
                                name=collection_name
                            )
                        logger.info(f"成功创建集合: {collection_name}")
                        return collection
                    except chromadb.errors.ChromaError as create_error:
                        # 如果集合已存在（并发创建），尝试再次获取
                        if "already exists" in str(create_error).lower():
                            try:
                                collection = client.get_collection(name=collection_name)
                                logger.info(f"集合已存在，获取成功: {collection_name}")
                                return collection
                            except Exception as get_error:
                                logger.error(f"获取已存在的集合失败: {str(get_error)}")
                                return None
                        else:
                            logger.error(f"创建集合失败: {str(create_error)}")
                            return None
                    except Exception as create_error:
                        logger.error(f"创建集合时发生异常: {str(create_error)}")
                        return None
                else:
                    # 如果没有配置，使用默认配置创建
                    collection = client.create_collection(name=collection_name)
                    logger.info(f"使用默认配置创建集合: {collection_name}")
                    return collection
            except Exception as create_error:
                logger.error(f"创建集合时发生错误: {str(create_error)}")
                return None
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

            # 获取向量数据库配置
            vector_db = VectorMapper.get_vector_db(vector_db_id)
            if not vector_db:
                raise Exception("向量数据库不存在")
            
            # 初始化嵌入模型
            model_info_id = vector_db.embedding_id
            if not model_info_id:
                raise Exception("模型配置ID为空")
            embedding_model = get_embedding(model_info_id)

            # 读取并处理文件
            documents = SimpleDirectoryReader(input_files=[save_path]).load_data()
            logger.info(f"成功加载 {len(documents)} 个文档片段")
            
            # 使用配置的chunk_size和chunk_overlap创建节点解析器
            chunk_size = vector_db.chunk_size or 1024
            chunk_overlap = vector_db.chunk_overlap or 200
            node_parser = SimpleNodeParser.from_defaults(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
            # 创建索引并存储，使用节点解析器
            logger.info(f"开始创建向量索引，文档数量: {len(documents)}")
            index = VectorStoreIndex.from_documents(
                documents=documents,
                storage_context=storage_context,
                embed_model=embedding_model,
                node_parser=node_parser
            )
            logger.info("向量索引创建完成")
            nodes = storage_context.docstore.docs
            logger.info(f"生成的节点数量: {len(nodes)}")
            for node_id, node in nodes.items():
                print(f"Node ID: {node_id}")
                print(f"Content: {node.text}")  # 文本内容
                print(f"Metadata: {node.metadata}")  # 元数据
                print("---")

            # 3. 保存文档信息到数据库
            logger.info("开始保存文档信息到数据库")
            file_extension = os.path.splitext(filename)[1]
            file_type = file_extension[1:] if file_extension else "unknown"
            
            # 获取文件大小（如果文件已被删除，使用之前保存的大小）
            try:
                file_size = os.path.getsize(save_path) if os.path.exists(save_path) else 0
            except:
                file_size = 0

            logger.info(f"准备保存文档信息到数据库: {filename}, 类型: {file_type}, 大小: {file_size}")
            document = Document(
                user_id=user_id,  # 使用传入的用户ID
                vector_db_id=vector_db_id,
                name=unique_filename,
                describe=describe if describe else None,  # 确保空字符串转为None
                original_name=filename,
                type=file_type,
                size=file_size,
                save_path=save_path,
            )

            db.session.add(document)
            db.session.commit()
            logger.info(f"文件信息已保存到 document 数据库，ID: {document.id}, 文档名称: {document.original_name}")
            
            # 向量化处理完成后，删除临时文件（改为临时存储逻辑）
            if file_saved and os.path.exists(save_path):
                try:
                    os.remove(save_path)
                    logger.info(f"向量化完成，已删除临时文件: {save_path}")
                    # 更新文档记录，标记文件已删除
                    document.save_path = None  # 或者设置为空字符串，表示文件已删除
                    db.session.commit()
                except Exception as delete_error:
                    logger.warning(f"删除临时文件失败: {str(delete_error)}，但不影响向量数据")
            
            return document.id  # 返回文档ID

        except Exception as e:
            logger.error(f"处理过程中发生错误: {str(e)}", exc_info=True)

            # 错误处理：清理已保存的文件
            if file_saved and os.path.exists(save_path):
                try:
                    os.remove(save_path)
                    logger.info(f"处理失败，已删除临时文件: {save_path}")
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

            # 临时存储逻辑：文件可能已经不存在，只删除向量数据
            # 如果文件还存在（异常情况），也删除它
            if document.save_path and os.path.exists(document.save_path):
                try:
                    os.remove(document.save_path)
                    logger.info(f"删除残留文件: {document.save_path}")
                except Exception as e:
                    logger.warning(f"删除文件失败: {str(e)}")

            # 删除向量集合中的相关数据
            vector_db_id = document.vector_db_id
            client = get_chromadb_client()
            if client:
                collection_name = f"vector_db_{vector_db_id}"
                try:
                    collection = client.get_collection(name=collection_name)
                    # 删除向量集合中与该文档相关的数据
                    collection.delete(where={"file_name": document.name})
                    logger.info(f"已删除向量集合中的数据: {document.name}")
                except Exception as e:
                    logger.error(f"删除向量集合中的数据失败: {str(e)}")

            # 删除数据库记录
            db.session.delete(document)
            db.session.commit()

            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除文档失败: {str(e)}")
            return False

    @staticmethod
    def get_user_vector_dbs(user_id):
        try:
            # 按创建时间降序排序，最新创建的靠前
            vector_dbs = VectorDb.query.filter_by(user_id=user_id).order_by(VectorDb.create_at.desc()).all()
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
    def query_vectors(vector_db_id, query_text, n_results=None):
        """查询向量数据库 (使用 LlamaIndex)"""
        # 获取向量数据库配置
        vector_db = VectorMapper.get_vector_db(vector_db_id)
        if not vector_db:
            logger.error(f"未找到向量数据库: {vector_db_id}")
            return None
            
        # 使用配置的topk，如果没有传入n_results
        if n_results is None:
            n_results = vector_db.topk or 10
        
        # 获取 ChromaDB 集合
        chroma_collection = VectorService.get_chroma_collection(vector_db_id)
        if not chroma_collection:
            logger.error("无法获取 ChromaDB 集合")
            return None

        try:
            # 创建向量存储
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

            # 初始化嵌入模型
            model_info_id = vector_db.embedding_id
            if not model_info_id:
                raise Exception("模型配置ID为空")
            embedding_model = get_embedding(model_info_id)

            # 加载索引
            index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                embed_model=embedding_model
            )

            # 创建查询引擎，使用配置的topk
            retriever = index.as_retriever(similarity_top_k=n_results)
            nodes = retriever.retrieve(query_text)

            document_similarity = vector_db.document_similarity

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
    @staticmethod
    def query_vector_by_model(model_config_id, query_text, n_results=10):
        try:
            vector_db_id = ModelMapper.get_vector_db_id(model_config_id)
            if vector_db_id is None:
                logger.error("无法获取向量数据库ID")
                return None
        except Exception as e:
            logger.error(f"获取向量数据库ID失败: {str(e)}")
            return None
        return VectorService.query_vectors(vector_db_id, query_text, n_results)

    @staticmethod
    def get_document_file(document_id):
        """获取文档文件信息（临时存储模式下，文件已删除，返回None）"""
        try:
            document = Document.query.get(document_id)
            if not document:
                logger.error(f"未找到文档记录: {document_id}")
                return None, None

            # 临时存储逻辑：文件在处理完成后已被删除
            if not document.save_path:
                logger.warning(f"文档 {document_id} 的文件已删除（临时存储模式）")
                return None, None

            file_path = document.save_path
            original_name = document.original_name

            # 确保路径是绝对路径
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)

            # 检查文件是否存在（可能已经被删除）
            if not os.path.isfile(file_path):
                logger.warning(f"文件不存在: {file_path}（可能已被删除）")
                return None, None

            return file_path, original_name
        except Exception as e:
            logger.error(f"获取文档文件信息失败: {str(e)}", exc_info=True)
            return None, None