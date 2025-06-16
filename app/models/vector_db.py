import decimal
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
        documents = [doc.to_dict() for doc in self.documents]
        return {
            'id': self.id,
            'name': self.name,
            'describe': self.describe,
            'created_at': created_at_str,
            'updated_at': updated_at_str,
            'model_configs': model_configs,
            'documents': documents
        }