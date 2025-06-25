from app.extensions import db

class Document(db.Model):
    __tablename__ = 'document'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vector_db_id = db.Column(db.Integer, db.ForeignKey('vector_db.id'), nullable=False)
    name = db.Column(db.String(255), unique=True, nullable=False)
    original_name = db.Column(db.String(255), unique=True, nullable=False)
    type = db.Column(db.String(64), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    save_path = db.Column(db.Text, nullable=False)
    describe = db.Column(db.String(255), nullable=True)
    upload_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    user = db.relationship('User', backref=db.backref('documents', lazy=True))
    vector_db = db.relationship('VectorDb', back_populates='stored_documents')
    __table_args__ = (
        db.Index('idx_document_type', type),
        db.Index('idx_document_upload_at', upload_at),
        db.Index('idx_document_user_id', user_id),
        db.Index('idx_document_vector_db_id', vector_db_id),
    )

    def to_dict(self):
        upload_at_str = self.upload_at.strftime('%Y-%m-%d %H:%M:%S') if self.upload_at else None
        return {
            'id': self.id,
            'original_name': self.original_name,
            'type': self.type,
            'size': self.size,
            'save_path': self.save_path,
            'describe': self.describe,
            'upload_at': upload_at_str
        }