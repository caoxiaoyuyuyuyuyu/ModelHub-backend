from flask import Blueprint, request, jsonify

from app.forms.base import ErrorResponse, SuccessResponse
from app.services.UserService import UserService
from app.utils.JwtUtil import login_required

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('register', methods=['POST'])
def register():
    data = request.form

    if not data or "name" not in data or "email" not in data or "password" not in data:
        return ErrorResponse(400, "请求参数错误").to_json()

    name, email, password, describe = data.get('name'), data.get('email'), data.get('password'), data.get('describe')
    try:
        token = UserService.register(name, email, password, describe)
        return SuccessResponse("注册成功", token).to_json()
    except Exception as e:
        return ErrorResponse(500, str(e)).to_json()

@user_bp.route('test', methods=['GET'])
@login_required
def test():
    user = request.user
    return SuccessResponse("测试成功", user.to_dict()).to_json()