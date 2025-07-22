from datetime import datetime

from sqlalchemy.ext.associationproxy import association_proxy

from app.extensions import db

# 角色模型
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    permissions = db.relationship('Permission', secondary='role_permissions', back_populates='roles', lazy=True)
    route_associations = db.relationship('RoleRoute', back_populates='role', lazy=True)

    # Proxy for easier access to route paths
    route_paths = association_proxy('routes', 'path')

    @property
    def routes(self):
        return [assoc.route for assoc in self.route_associations]
# 权限模型
class Permission(db.Model):
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    roles = db.relationship('Role', secondary='role_permissions', back_populates='permissions', lazy=True)

# 角色-权限关联模型
class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Route(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(100),
                     nullable=False)  # Removed unique constraint as paths can be same with different methods
    name = db.Column(db.String(100), nullable=False)
    component = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(10), default='GET')  # HTTP methods: GET, POST, PUT, DELETE, etc.
    parent_id = db.Column(db.Integer, db.ForeignKey('routes.id'))  # For hierarchical structure
    meta = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    children = db.relationship('Route', backref=db.backref('parent', remote_side=[id]))
    route_associations = db.relationship('RoleRoute', back_populates='route', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('path', 'method', name='uq_route_path_method'),
    )

    @property
    def roles(self):
        return [assoc.role for assoc in self.route_associations]


class RoleRoute(db.Model):
    __tablename__ = 'role_routes'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships (optional, for easier access)
    role = db.relationship('Role', backref='role_route_associations')
    route = db.relationship('Route', back_populates='route_associations')
