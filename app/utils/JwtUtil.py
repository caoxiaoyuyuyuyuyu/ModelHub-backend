# app/utils/JwtUtil.py
from datetime import datetime, timedelta
from typing import Optional

from flask import request
import jwt
from functools import wraps

from sqlalchemy.orm import Session

from app.forms.base import ErrorResponse
from app.mapper import UserMapper
from app.models.user import User

from app.config import Config
from app.utils.PasswordUtil import verify_password  # 导入验证密码函数

# 移除 get_password_hash 函数

def generate_jwt(id: int, name: str, email: str) -> str:
    payload = {
        'id': id,
        'name': name,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, Config.secret_key, Config.algorithm)

def authenticate_user(email: str, password: str) -> User | None:
    """验证用户凭据"""
    user = UserMapper.get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

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
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1].strip()
        else:
            token = auth_header.strip()

        if not token:
            return ErrorResponse(code=401, message='未提供有效的访问令牌').to_response()
        payload = verify_jwt(token)
        if 'error' in payload:
            return ErrorResponse(code=401, message=payload['error']).to_response()
        request.user = User(id=payload['id'], name=payload['name'], email=payload['email'])
        return f(*args, **kwargs)
    return decorated_function