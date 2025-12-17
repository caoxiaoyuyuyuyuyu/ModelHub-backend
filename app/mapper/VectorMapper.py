import json
from app.models.vector_db import VectorDb
from app.extensions import db

class VectorMapper:
    @staticmethod
    def create_vector_db(user_id, name, embedding_id, describe=None, document_similarity=0.7,
                         distance='cosine', metadata=None, chunk_size=1024, chunk_overlap=200, topk=10):
        try:
            # 处理metadata，如果是dict则转为JSON字符串
            metadata_str = None
            if metadata:
                if isinstance(metadata, dict):
                    metadata_str = json.dumps(metadata)
                elif isinstance(metadata, str):
                    metadata_str = metadata
                    
            vector_db = VectorDb(
                user_id=user_id, 
                name=name, 
                embedding_id=embedding_id, 
                describe=describe,
                document_similarity=document_similarity,
                distance=distance,
                collection_metadata=metadata_str,  # 使用collection_metadata字段
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                topk=topk
            )
            db.session.add(vector_db)
            db.session.commit()
            db.session.refresh(vector_db)
            return vector_db
        except Exception as e:
            db.session.rollback()
            raise Exception(f"创建向量数据库失败: {str(e)}")

    @staticmethod
    def get_vector_db(vector_db_id):
        return VectorDb.query.get(vector_db_id)

    @staticmethod
    def update_vector_db(vector_db_id, name=None, embedding_id=None, describe=None, document_similarity=None,
                        distance=None, metadata=None, chunk_size=None, chunk_overlap=None, topk=None):
        try:
            vector_db = VectorMapper.get_vector_db(vector_db_id)
            if not vector_db:
                return None
            if name is not None:
                vector_db.name = name
            if embedding_id is not None:
                vector_db.embedding_id = embedding_id
            if describe is not None:
                vector_db.describe = describe
            if document_similarity is not None:
                vector_db.document_similarity = document_similarity
            if distance is not None:
                vector_db.distance = distance
            if metadata is not None:
                # 处理metadata，如果是dict则转为JSON字符串
                if isinstance(metadata, dict):
                    vector_db.collection_metadata = json.dumps(metadata)  # 使用collection_metadata字段
                elif isinstance(metadata, str):
                    vector_db.collection_metadata = metadata
            if chunk_size is not None:
                vector_db.chunk_size = chunk_size
            if chunk_overlap is not None:
                vector_db.chunk_overlap = chunk_overlap
            if topk is not None:
                vector_db.topk = topk
            db.session.commit()
            db.session.refresh(vector_db)
            return vector_db
        except Exception as e:
            db.session.rollback()
            raise Exception(f"更新向量数据库失败: {str(e)}")

    @staticmethod
    def delete_vector_db(vector_db_id):
        try:
            vector_db = VectorMapper.get_vector_db(vector_db_id)
            if not vector_db:
                return False
            db.session.delete(vector_db)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"删除向量数据库失败: {str(e)}")
