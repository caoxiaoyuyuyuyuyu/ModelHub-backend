from app.extensions import db

class ModelConfig(db.Model):
    __tablename__ = 'model_config'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    share_id = db.Column(db.String(255), unique=True, nullable=False)
    base_model_id = db.Column(db.Integer, db.ForeignKey('model_info.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    temprature = db.Column(db.Numeric(10, 2), default=decimal.Decimal('0.70'), nullable=False)
    top_p = db.Column(db.Numeric(10, 2), default=decimal.Decimal('0.70'), nullable=False)
    top_k = db.Column(db.Integer, default=50, nullable=False)
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

    user = db.relationship('User', backref=db.backref('model_configs', lazy=True))
    base_model = db.relationship('ModelInfo', backref=db.backref('model_configs', lazy=True))
    vector_db = db.relationship('VectorDb', backref=db.backref('model_configs', lazy=True))
    __table_args__ = (
        db.Index('idx_model_config_base_model_id', base_model_id),
        db.Index('idx_model_config_user_id', user_id),
        db.Index('idx_model_config_vector_db_id', vector_db_id),
    )