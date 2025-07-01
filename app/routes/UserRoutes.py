from flask import Blueprint, request, jsonify
from app.forms.base import ErrorResponse, SuccessResponse
from app.services.UserService import UserService
from app.utils.JwtUtil import login_required
from app.utils.file_utils import save_uploaded_file

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

        # # 直接使用异常中的错误信息
        # error_info = getattr(e, 'args', [{}])[0]
        # code = error_info.get('code', 500)
        # msg = error_info.get('msg', str(e))
        # # 打印错误信息到控制台
        # print(f"Error: {code} - {msg}")
        return ErrorResponse(500, "登陆失败").to_json()

@user_bp.route('/test', methods=['GET'])
@login_required
def test():
    user = request.user
    return SuccessResponse("测试成功", user.to_dict()).to_json()

@user_bp.route('/info', methods=['GET'])
@login_required
def get_user_info():
    user_email = request.user.email
    try:
        user = UserService.get_user_by_email(user_email)
        if not user:
            return ErrorResponse(404, "用户不存在").to_json()
        return SuccessResponse("获取成功", user).to_json()
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


import os
from flask import send_from_directory, current_app, abort
from werkzeug.utils import safe_join, secure_filename


@user_bp.route('/avatar/<path:filename>', methods=['GET'])
def get_avatar(filename):
    """
    提供用户头像文件（存储在应用外层的uploads文件夹）

    参数:
        filename: 头像文件名（可包含相对路径）

    返回:
        头像文件内容或404错误
    """
    uploads_dir = current_app.config['UPLOADS_DIR']

    # 3. 使用Flask的safe_join确保路径安全
    try:
        safe_path = safe_join(uploads_dir, filename)
    except ValueError:
        # 路径不安全（尝试目录遍历）
        current_app.logger.warning(f"非法路径访问尝试: {filename}")
        abort(403)  # 禁止访问

    # 4. 检查文件是否存在
    if not os.path.isfile(safe_path):
        # 5. 返回默认头像（如果存在）
        default_avatar = os.path.join(uploads_dir, 'image.png')
        if os.path.isfile(default_avatar):
            return send_from_directory(uploads_dir, 'image.png')

        # 6. 没有默认头像则返回404
        abort(404)

    # 7. 发送文件并设置缓存
    response = send_from_directory(
        uploads_dir,
        filename,
        conditional=True,  # 支持条件GET请求
    )
    # 防止浏览器将图片当作HTML执行
    response.headers['Content-Disposition'] = 'inline'
    # 防止点击劫持
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@user_bp.route('/avatar', methods=['PUT'])
@login_required
def update_avatar():
    file = request.files.get('file')
    if not file:
        return ErrorResponse(400, "请上传文件").to_json()
    save_path = save_uploaded_file(file, current_app.config['UPLOADS_DIR'])
    if not save_path:
        return ErrorResponse(500, "文件保存失败").to_json()
    avatar = UserService.update_avatar(request.user.id, save_path)
    return SuccessResponse("更新成功", avatar).to_json()