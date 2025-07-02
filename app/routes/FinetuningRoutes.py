# app/routes/FinetuningRoutes.py
from flask import Blueprint, request, current_app, send_file
from app.forms.base import ErrorResponse, SuccessResponse
from app.services.FinetuningService import FinetuningService
from app.utils.JwtUtil import login_required
from app.utils.file_utils import save_uploaded_file
import os

finetuning_bp = Blueprint('finetuning', __name__, url_prefix='/finetuning')


# 辅助函数：处理异常
def handle_exception(e, default_error_code=500):
    try:
        if isinstance(e, ValueError):
            return ErrorResponse(400, f"参数错误: {str(e)}").to_json()
        else:
            return ErrorResponse(default_error_code, f"服务器错误: {str(e)}").to_json()
    except Exception as e2:
        return ErrorResponse(500, f'严重错误: {str(e2)}').to_json()


@finetuning_bp.route('/create', methods=['POST'])
@login_required
def create():
    try:
        # 获取表单数据
        data = request.form.to_dict()
        user_id = request.user.id

        # 获取单个文件 (字段名改为 'file')
        file = request.files.get('file')
        if not file:
            return ErrorResponse(400, "请上传文件").to_json()

        # 调用服务
        instance = FinetuningService.create(data, user_id, file)  # 传入单个文件
        return SuccessResponse("创建成功", instance.to_dict()).to_json()

    except ValueError as e:
        return ErrorResponse(400, f"参数错误: {str(e)}").to_json()
    except Exception as e:
        return handle_exception(e)


@finetuning_bp.route('/get/<int:model_id>', methods=['GET'])
@login_required
def get(model_id):
    try:
        instance = FinetuningService.get_model(model_id)
        if instance:
            return SuccessResponse("查询成功", instance).to_json()
        return ErrorResponse(404, "未找到该记录").to_json()
    except Exception as e:
        return handle_exception(e)

@finetuning_bp.route('/get_model_config/<int:model_id>', methods=['GET'])
@login_required
def get_model_config(model_id):
    try:
        instance = FinetuningService.get_model_base(model_id)
        if instance:
            return SuccessResponse("查询成功", instance).to_json()
        return ErrorResponse(404, "未找到该记录").to_json()
    except Exception as e:
        return handle_exception(e)

@finetuning_bp.route('/<model_name>/delete/<int:id>', methods=['DELETE'])
@login_required
def delete(model_name, id):
    try:
        if FinetuningService.delete(model_name, id):
            return SuccessResponse("删除成功").to_json()
        return ErrorResponse(404, "未找到该记录").to_json()
    except Exception as e:
        return handle_exception(e)

@finetuning_bp.route('/<model_name>/list', methods=['GET'])
@login_required
def get_list(model_name):
    try:
        user_id = request.user.id
        instances = FinetuningService.get_list(model_name, user_id)
        instance_list = [instance.to_dict() for instance in instances]
        return SuccessResponse("查询成功", instance_list).to_json()
    except Exception as e:
        return handle_exception(e)

from urllib.parse import quote


@finetuning_bp.route('/download_logs', methods=['GET'])
@login_required
def download_logs():
    try:
        user_id = request.user.id
        record_id = request.args.get('id')  # Note: Changed from 'record_id' to 'id' to match the request
        if not record_id:
            return ErrorResponse(400, "Record ID is required").to_json()

        file_path, original_name = FinetuningService.download_logs(record_id)

        # Validate file exists
        if not os.path.exists(file_path):
            return ErrorResponse(404, "Log file not found on server").to_json()

        # URL encode the filename
        safe_filename = quote(original_name)

        response = send_file(
            file_path,
            as_attachment=True,
            download_name=original_name,
            conditional=True
        )

        response.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{safe_filename}"
        return response

    except ValueError as e:
        return ErrorResponse(400, str(e)).to_json()
    except Exception as e:
        return handle_exception(e)

@finetuning_bp.route('/chat', methods=['POST'])
@login_required
def chat() -> str:
    """
    对话
    :return: 返回json格式的字符串
    """
    model_config_id = request.form.get("model_config_id")
    message = request.form.get("message")
    if not message:
        return ErrorResponse(400, "用户消息为空").to_json()
    try:
        response = FinetuningService.chat(model_config_id, message)  # 回答
        return SuccessResponse("对话成功！", response).to_json()
    except Exception as e:
        return ErrorResponse(500, str(e)).to_json()

@finetuning_bp.route('/base/chat', methods=['POST'])
@login_required
def base_chat() -> str:
    """
    对话
    :return: 返回json格式的字符串
    """
    data = request.get_json()
    print( data)
    model_config_id = data.get("model_config_id")
    messages = data.get("message")
    if not messages:
        return ErrorResponse(400, "用户消息为空").to_json()
    try:
        response = FinetuningService.base_chat(model_config_id, messages)  # 回答
        return SuccessResponse("对话成功！", response).to_json()
    except Exception as e:
        return ErrorResponse(500, str(e)).to_json()

@finetuning_bp.route('/base/create', methods=['POST'])
@login_required
def base_create() -> str:
    """
    创建模型
    :return: 创建模型结果
    """
    try:
        data = request.form.to_dict()
        instance = FinetuningService.create_base(data)
        return SuccessResponse("创建成功", instance.to_dict()).to_json()
    except ValueError as e:
        return ErrorResponse(400, f"参数错误: {str(e)}").to_json()
    except Exception as e:
        return handle_exception(e)

