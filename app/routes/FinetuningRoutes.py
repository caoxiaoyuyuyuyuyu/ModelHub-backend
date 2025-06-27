# app/routes/FinetuningRoutes.py
from flask import Blueprint, request
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


@finetuning_bp.route('/<model_name>/create', methods=['POST'])
@login_required
def create(model_name):
    data = request.form.to_dict()
    file = request.files.get('file')
    if file:
        save_dir = os.path.join('uploads', 'finetuning_documents')
        save_path = save_uploaded_file(file, save_dir)
        if save_path:
            data['save_path'] = save_path
            data['name'] = file.filename
            data['original_name'] = file.filename
            data['type'] = file.content_type
            data['size'] = file.content_length
        else:
            return ErrorResponse(500, "文件保存失败").to_json()
    try:
        instance = FinetuningService.create(model_name, **data)
        return SuccessResponse("创建成功", instance.to_dict()).to_json()
    except Exception as e:
        return handle_exception(e)


@finetuning_bp.route('/<model_name>/get/<int:id>', methods=['GET'])
@login_required
def get(model_name, id):
    try:
        instance = FinetuningService.get(model_name, id)
        if instance:
            return SuccessResponse("查询成功", instance.to_dict()).to_json()
        return ErrorResponse(404, "未找到该记录").to_json()
    except Exception as e:
        return handle_exception(e)


@finetuning_bp.route('/<model_name>/update/<int:id>', methods=['POST'])
@login_required
def update(model_name, id):
    data = request.form.to_dict()  # 将 ImmutableMultiDict 转换为普通字典
    data.pop('id', None)  # 移除 id 字段，如果不存在则不报错
    try:
        instance = FinetuningService.update(model_name, id, **data)
        if instance:
            return SuccessResponse("更新成功", instance.to_dict()).to_json()
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

@finetuning_bp.route('/finetuning_records/get_record/<int:id>', methods=['GET'])
@login_required
def get_finetuning_record(id):
    try:
        instance = FinetuningService.get('finetuning_records', id)
        if instance:
            return SuccessResponse("查询成功", instance.to_dict()).to_json()
        return ErrorResponse(404, "未找到该记录").to_json()
    except Exception as e:
        return handle_exception(e)