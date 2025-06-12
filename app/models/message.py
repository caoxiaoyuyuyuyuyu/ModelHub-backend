from app.extensions import db

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 可扩展为枚举校验
    content = db.Column(db.Text, nullable=True)
    create_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    conversation = db.relationship('Conversation', backref=db.backref('messages', lazy=True))
    __table_args__ = (
        db.Index('idx_message_conversation_id', conversation_id),
        db.Index('idx_message_role', role),
    )