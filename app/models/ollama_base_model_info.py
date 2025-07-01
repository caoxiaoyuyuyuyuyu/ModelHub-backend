from sqlalchemy import Enum
from app.extensions import db


class OllamaBaseModelInfo(db.Model):
    __tablename__ = 'ollama_base_model_info'
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(255), unique=True, nullable=False)
    model_supplier = db.Column(db.String(255), nullable=True)
    describe = db.Column(db.String(255), nullable=True)
    create_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
        nullable=False
    )
