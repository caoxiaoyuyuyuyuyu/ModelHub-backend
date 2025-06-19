from app.models.vector_db import VectorDb
from app.extensions import db

class VectorMapper:
    @staticmethod
    def create_vector_db(user_id, name, embedding_id, describe=None, document_similarity=0.7):
        try:
            vector_db = VectorDb(user_id=user_id, name=name, embedding_id=embedding_id, describe=describe,
                                 document_similarity=document_similarity)
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
    def update_vector_db(vector_db_id, name=None, embedding_id=None, describe=None, document_similarity=None):
        try:
            vector_db = VectorMapper.get_vector_db(vector_db_id)
            if not vector_db:
                return None
            if name:
                vector_db.name = name
            if embedding_id:
                vector_db.embedding_id = embedding_id
            if describe:
                vector_db.describe = describe
            if document_similarity:
                vector_db.document_similarity = document_similarity
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
    #
    # @staticmethod
    # def get_vectordb_id(user_id: int):
    #     try:
    #         vector_db = VectorDb.query.filter_by(user_id=user_id)
    #         id_list = []
    #         for item in vector_db:
    #             id_list.append(vector_db.id)
    #         return id_list
    #     except Exception as e:
    #         raise Exception(f"查询vectordb_id失败：{str(e)}")