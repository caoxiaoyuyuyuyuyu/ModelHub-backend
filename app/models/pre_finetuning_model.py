from app.extensions import db
from datetime import datetime

class PreFinetuningModel(db.Model):
    __tablename__ = 'pre_finetuning_model'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    path = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    describe = db.Column(db.String(255), nullable=True)
    type = db.Column(db.String(64), nullable=False)

    def to_dict(self):
        created_at_str = self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'created_at': created_at_str,
            'describe': self.describe,
            'type': self.type
        }