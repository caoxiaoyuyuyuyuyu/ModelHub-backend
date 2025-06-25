from datetime import datetime, timedelta
from typing import Optional

from flask import request
import jwt
from functools import wraps

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.forms.base import ErrorResponse
from app.mapper import UserMapper
from app.models.user import User

from app.config import Config

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def generate_jwt(id: int, name: str, email: str) -> str:
    payload = {
        'id': id,
        'name': name,
        'email': email,
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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
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
        request.user = User(id=payload['id'], name=payload['name'], email=payload['email'])
        return f(*args, **kwargs)
    return decorated_function