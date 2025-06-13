from sqlalchemy import Enum
from app.extensions import db


class ModelInfo(db.Model):
    __tablename__ = 'model_info'
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(255), unique=True, nullable=False)
    type = db.Column(Enum('chatllm', 'embedding'), nullable=False)
    base_url = db.Column(db.String(255), unique=True, nullable=False)
    api_key = db.Column(db.String(255), unique=True, nullable=False)
    describe = db.Column(db.String(255), nullable=True)
    create_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
        nullable=False
    )
