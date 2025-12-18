import decimal
import json
from app.extensions import db
from datetime import datetime
from .document import Document

class VectorDb(db.Model):
    __tablename__ = 'vector_db'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    embedding_id = db.Column(db.Integer, db.ForeignKey('model_info.id'), nullable=False)
    name = db.Column(db.String(255), unique=True, nullable=False)
    document_similarity = db.Column(db.Numeric(5, 2), default=decimal.Decimal('0.70'), nullable=True)
    describe = db.Column(db.String(255), nullable=True)
    # 新增字段
    distance = db.Column(db.String(20), default='cosine', nullable=True)  # 距离度量方式: cosine, l2, ip
    collection_metadata = db.Column(db.Text, nullable=True)  # JSON格式的元数据（使用collection_metadata避免与SQLAlchemy的metadata冲突）
    chunk_size = db.Column(db.Integer, default=1024, nullable=True)  # chunk大小
    chunk_overlap = db.Column(db.Integer, default=200, nullable=True)  # chunk重叠
    topk = db.Column(db.Integer, default=10, nullable=True)  # 检索时的top k
    stored_documents = db.relationship('Document', back_populates='vector_db', lazy=True)
    create_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
        nullable=False
    )
    user = db.relationship('User', backref=db.backref('vector_dbs', lazy=True))
    __table_args__ = (
        db.Index('idx_vector_db_create_at', create_at),
        db.Index('idx_user_id', user_id),
    )

    def to_dict(self):
        created_at_str = self.create_at.strftime('%Y-%m-%d %H:%M:%S') if self.create_at else None
        updated_at_str = self.update_at.strftime('%Y-%m-%d %H:%M:%S') if self.update_at else None
        model_configs = [config.to_dict() for config in self.model_configs]
        # 确保返回所有文档，包括 save_path 为 None 的文档
        documents = [doc.to_dict() for doc in self.stored_documents]
        # 解析collection_metadata JSON
        metadata_dict = None
        if self.collection_metadata:
            try:
                metadata_dict = json.loads(self.collection_metadata)
            except:
                metadata_dict = None
        return {
            'id': self.id,
            'name': self.name,
            'describe': self.describe,
            'embedding_id': self.embedding_id,
            'document_similarity': float(self.document_similarity) if self.document_similarity else 0.7,
            'distance': self.distance or 'cosine',
            'metadata': metadata_dict,  # 对外接口仍使用metadata名称
            'chunk_size': self.chunk_size or 1024,
            'chunk_overlap': self.chunk_overlap or 200,
            'topk': self.topk or 10,
            'created_at': created_at_str,
            'updated_at': updated_at_str,
            'model_configs': model_configs,
            'documents': documents  # 返回所有文档，不过滤 save_path 为 None 的文档
        }