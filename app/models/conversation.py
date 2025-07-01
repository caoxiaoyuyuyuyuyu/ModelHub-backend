from app.extensions import db


class Conversation(db.Model):
    __tablename__ = 'conversation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(255), nullable=True)
    model_config_id = db.Column(db.Integer, db.ForeignKey('model_config.id'), nullable=False)
    chat_history = db.Column(db.Integer, default=20, nullable=False)
    type = db.Column(db.Integer, default=0, nullable=False)
    create_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
        nullable=False
    )
    user = db.relationship('User', backref=db.backref('conversations', lazy=True))
    model_config = db.relationship('ModelConfig', backref=db.backref('conversations', lazy=True))
    __table_args__ = (
        db.Index('idx_conversation_model_config_id', model_config_id),
        db.Index('idx_conversation_user_id', user_id),
    )
