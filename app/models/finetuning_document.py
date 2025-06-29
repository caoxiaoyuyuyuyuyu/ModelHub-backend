# app/models/finetuning_document.py
from app.extensions import db

class FinetuningDocument(db.Model):
    __tablename__ = 'finetuning_document'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 修改为外键关联 user 表的 id 字段
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('finetuning_records.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(64), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    save_path = db.Column(db.Text, nullable=False)
    describe = db.Column(db.String(255), nullable=True)
    upload_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    # 建立与 User 模型的关系
    user = db.relationship('User', backref=db.backref('finetuning_documents', lazy=True))

    def to_dict(self):
        upload_at_str = self.upload_at.strftime('%Y-%m-%d %H:%M:%S') if self.upload_at else None
        return {
            'id': self.id,
            'user_id': self.user_id,
            'record_id': self.record_id,
            'name': self.name,
            'original_name': self.original_name,
            'type': self.type,
            'size': self.size,
            'save_path': self.save_path,
            'describe': self.describe,
            'upload_at': upload_at_str
        }