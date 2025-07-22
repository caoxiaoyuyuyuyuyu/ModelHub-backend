from app.extensions import db

type_map = {
    1:  'Individual',
    2:  'Enterprise',
    3:  'Admin'
}

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    avatar  = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    describe = db.Column(db.String(255), nullable=True)
    type = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    create_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
        nullable=False
    )
    __table_args__ = (
        db.Index('idx_user_create_at', create_at),
        db.Index('idx_user_update_at', update_at),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'avatar': self.avatar,
            'email': self.email,
            'describe': self.describe,
            'type': type_map[self.type],
            'create_at': self.create_at,
            'update_at': self.update_at,
        }
