import decimal

from app.extensions import db


class OllamaModelConfig(db.Model):
    __tablename__ = 'ollama_model_config'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    base_model_id = db.Column(db.Integer, db.ForeignKey('ollama_base_model_info.id'))
    name = db.Column(db.String(255), nullable=False)
    temperature = db.Column(db.Numeric(10, 2), default=decimal.Decimal('0.70'), nullable=False)
    top_p = db.Column(db.Numeric(10, 2), default=decimal.Decimal('0.70'), nullable=False)
    top_k = db.Column(db.Integer, default=50, nullable=False)
    num_keep = db.Column(db.Integer, default=1024, nullable=False)
    num_predict = db.Column(db.Integer, default=1024, nullable=False)
    describe = db.Column(db.String(255), nullable=True)
    create_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
        nullable=False
    )

    user = db.relationship('User', backref=db.backref('ollama_model_configs', lazy=True))
    base_model = db.relationship('OllamaBaseModelInfo', backref=db.backref('ollama_model_configs', lazy=True))
    __table_args__ = (
        db.Index('idx_ollama_model_config_base_model_id', base_model_id),
        db.Index('idx_ollama_model_config_user_id', user_id),
    )

    def to_dict(self):
        create_at_str = self.create_at.strftime('%Y-%m-%d %H:%M:%S') if self.create_at else None
        update_at_str = self.update_at.strftime('%Y-%m-%d %H:%M:%S') if self.update_at else None
        return {
            'id': self.id,
            'user_id': self.user_id,
            'base_model_id': self.base_model_id,
            'name': self.name,
            'temperature': float(self.temperature),
            'top_p': float(self.top_p),
            'top_k': int(self.top_k),
            'num_keep': int(self.num_keep),
            'num_predict': int(self.num_predict),
            'describe': self.describe,
            'create_at': create_at_str,
            'update_at': update_at_str,
        }
