import decimal

from app.extensions import db
from app.models.vector_db import VectorDb


class ModelConfig(db.Model):
    __tablename__ = 'model_config'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    share_id = db.Column(db.String(255), unique=True, nullable=False)
    base_model_id = db.Column(db.Integer, db.ForeignKey('model_info.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    temperature = db.Column(db.Numeric(10, 2), default=decimal.Decimal('0.70'), nullable=False)
    top_p = db.Column(db.Numeric(10, 2), default=decimal.Decimal('0.70'), nullable=False)
    prompt = db.Column(db.Text, nullable=True)
    vector_db_id = db.Column(db.Integer, db.ForeignKey('vector_db.id'), nullable=False)
    create_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
        nullable=False
    )
    is_private = db.Column(db.Boolean, default=False, nullable=False)
    describe = db.Column(db.String(255), nullable=True)

    user = db.relationship('User', backref=db.backref('model_configs', lazy=True))
    base_model = db.relationship('ModelInfo', backref=db.backref('model_configs', lazy=True))
    vector_db = db.relationship('VectorDb', backref=db.backref('model_configs', lazy=True))
    __table_args__ = (
        db.Index('idx_model_config_base_model_id', base_model_id),
        db.Index('idx_model_config_user_id', user_id),
        db.Index('idx_model_config_vector_db_id', vector_db_id),
    )

    def to_dict(self):
        create_at_str = self.create_at.strftime('%Y-%m-%d %H:%M:%S') if self.create_at else None
        update_at_str = self.update_at.strftime('%Y-%m-%d %H:%M:%S') if self.update_at else None
        return {
            'id': self.id,
            'user_id': self.user_id,
            'share_id': self.share_id,
            'base_model_id': self.base_model_id,
            'name': self.name,
            'temperature': float(self.temperature),
            'top_p': float(self.top_p),
            'prompt': self.prompt,
            'vector_db_id': self.vector_db_id,
            'create_at': create_at_str,
            'update_at': update_at_str,
            'is_private': self.is_private
        }
