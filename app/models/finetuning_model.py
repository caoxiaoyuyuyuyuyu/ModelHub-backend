from app.extensions import db

class FinetuningModel(db.Model):
    __tablename__ = 'finetuning_model'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    describe = db.Column(db.String(255), nullable=True)
    record_id = db.Column(db.Integer, db.ForeignKey('finetuning_records.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('finetuning_models', lazy=True))
    record = db.relationship('FinetuningRecords', backref=db.backref('finetuning_models', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'describe': self.describe,
            'record_id': self.record_id
        }