from flask import Blueprint, request, jsonify
from app.forms.base import ErrorResponse, SuccessResponse
from app.services.UserService import UserService
from app.utils.JwtUtil import login_required

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()  # 使用JSON格式请求体
    if not data:
        return ErrorResponse(400, "请求数据不能为空").to_json()

    # 提取参数并验证
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    describe = data.get('describe')

    if not all([name, email, password]):
        return ErrorResponse(400, "缺少必要参数: name, email 或 password").to_json()

    try:
        token = UserService.register(name, email, password, describe)
        return SuccessResponse("注册成功", token).to_json()
    except Exception as e:
        # 打印错误信息便于调试
        print(f"Login error: {str(e)}")

        # 直接使用异常中的错误信息
        error_info = getattr(e, 'args', [{}])[0]
        code = error_info.get('code', 500)
        msg = error_info.get('msg', str(e))
        # 打印错误信息到控制台
        print(f"Error: {code} - {msg}")
        return ErrorResponse(code, msg).to_json()

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return ErrorResponse(400, "请求数据不能为空").to_json()

    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return ErrorResponse(400, "缺少必要参数: email 或 password").to_json()

    try:
        user = UserService.login(email, password)
        return SuccessResponse("登录成功", user).to_json()
    except Exception as e:
        # 打印错误信息便于调试
        print(f"Login error: {str(e)}")

        # 直接使用异常中的错误信息
        error_info = getattr(e, 'args', [{}])[0]
        code = error_info.get('code', 500)
        msg = error_info.get('msg', str(e))
        # 打印错误信息到控制台
        print(f"Error: {code} - {msg}")
        return ErrorResponse(code, msg).to_json()

@user_bp.route('/test', methods=['GET'])
@login_required
def test():
    user = request.user
    return SuccessResponse("测试成功", user.to_dict()).to_json()

@user_bp.route('/info', methods=['GET'])
@login_required
def get_user_info():
    user_email = request.args.get('user_email')
    try:
        user = UserService.get_user_by_email(user_email)
        if not user:
            return ErrorResponse(404, "用户不存在").to_json()
        return SuccessResponse("获取成功", user.to_dict()).to_json()
    except Exception as e:
        # 打印错误信息便于调试
        print(f"Login error: {str(e)}")

        # 直接使用异常中的错误信息
        error_info = getattr(e, 'args', [{}])[0]
        code = error_info.get('code', 500)
        msg = error_info.get('msg', str(e))
        # 打印错误信息到控制台
        print(f"Error: {code} - {msg}")
        return ErrorResponse(code, msg).to_json()

@user_bp.route('/enterprise', methods=['GET'])
def get_enterprise_users():
    try:
        users = UserService.get_enterprise_users()
        return SuccessResponse("获取配置商成功", users).to_json()
    except Exception as e:
        return ErrorResponse(500, str(e)).to_json()
