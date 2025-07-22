from datetime import datetime, timedelta
from typing import Optional

from flask import request, current_app
import jwt
from functools import wraps

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.forms.base import ErrorResponse
from app.mapper import UserMapper
from app.models.permission import Role, Route, RoleRoute
from app.models.user import User

from app.config import Config

from app.extensions import db

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def generate_jwt(id: int, name: str, email: str, type: int) -> str:
    payload = {
        'id': id,
        'name': name,
        'email': email,
        'type': type,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, Config.secret_key, Config.algorithm)

def authenticate_user(user: User, email: str, password: str):
    """验证用户凭据"""
    if not verify_password(password, user.password):
        return False
    return True

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def verify_jwt(token: str):
    try:
        return jwt.decode(token, Config.secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return {'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}


from flask import request, current_app
from werkzeug.exceptions import Forbidden
from urllib.parse import urlparse
import re


def verify_permission(role_id: int, path: str, method: str) -> bool:
    """
    验证指定角色是否有权限访问指定路由

    参数:
        role_id: 用户角色ID
        path: 要验证的路径 (可以是实际路径或带变量的路由模式)
        method: HTTP方法 (GET, POST, PUT, DELETE等)

    返回:
        bool: 有权限返回True，否则返回False

    异常:
        Forbidden: 当权限检查失败需要阻止访问时抛出
    """
    try:
        # 1. 验证角色是否存在
        role = Role.query.get(role_id)
        if not role:
            current_app.logger.warning(f"无效角色ID: {role_id}")
            return False

        # 2. 标准化路径（移除查询参数）
        clean_path = urlparse(path).path

        # 3. 获取所有路由定义
        all_routes = Route.query.filter_by(method=method.upper()).all()

        # 4. 查找匹配的路由
        matched_route = None
        for route in all_routes:
            # 将路由路径中的变量部分转换为通配符
            route_pattern = re.sub(r'<[^>]+>', r'[^/]+', route.path)
            if re.fullmatch(route_pattern, clean_path):
                matched_route = route
                break

        if not matched_route:
            current_app.logger.warning(f"未找到匹配路由: {method} {clean_path}")
            return False

        # 5. 检查角色是否有该路由权限
        has_permission = db.session.query(
            RoleRoute.query.filter_by(
                route_id=matched_route.id,
                role_id=role_id
            ).exists()
        ).scalar()

        if has_permission:
            current_app.logger.debug(
                f"权限验证通过: 角色[{role.name}]可以访问 {method} {clean_path} "
                f"(匹配路由: {matched_route.path})"
            )
            return True

        current_app.logger.info(
            f"权限不足: 角色[{role.name}]无法访问 {method} {clean_path}"
        )
        return False

    except Exception as e:
        current_app.logger.error(
            f"权限验证失败: {method} {path}. 错误: {str(e)}"
        )
        raise Forbidden("权限验证失败")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(request.path, request.method)
        # 打印所有请求头（调试用）
        # current_app.logger.debug(f"所有请求头: {request.headers}")
        auth_header = request.headers.get('Authorization', '')
        # current_app.logger.debug(f"原始Authorization头: {auth_header}")

        # 提取Token（兼容Bearer前缀和直接Token）
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1].strip()
        else:
            token = auth_header.strip()

        # current_app.logger.debug(f"提取的Token: {token}")

        if not token:
            return ErrorResponse(code=401, message='未提供有效的访问令牌').to_json()
        payload = verify_jwt(token)
        if 'error' in payload:
            return ErrorResponse(code=401, message=payload['error']).to_json()
        payload = verify_jwt(token)

        if not verify_permission(int(payload['type']), request.path, request.method):
            return ErrorResponse(code=403, message='无权限访问').to_json()

        request.user = User(id=payload['id'], name=payload['name'], email=payload['email'], type=payload['type'])
        return f(*args, **kwargs)
    return decorated_function