from flask import Blueprint, request, jsonify
from app.forms.base import ErrorResponse, SuccessResponse
from app.services import ModelService
from app.utils.exception_util import error_500_print

model_bp = Blueprint('model', __name__, url_prefix='/model')


@model_bp.route('/modelinfo/getlist', methods=['GET'])
def get_all_info():
    try:
        info_list = ModelService.get_all_info()
        return SuccessResponse("获取model_info列表成功", info_list).to_json()
    except Exception as e:
        return error_500_print("Model error", e)


@model_bp.route('/modelinfo/get/<int:info_id>', methods=['GET'])
def get_info(info_id):
    try:
        model_info = ModelService.get_info(info_id)
        return SuccessResponse("获取model_info成功", model_info).to_json()
    except Exception as e:
        return error_500_print("Model error", e)


@model_bp.route('/modelconfig/getpublic', methods=['GET'])
def get_public_config():
    try:
        config_list = ModelService.get_public_config()
        return SuccessResponse("获取model_info成功", config_list).to_json()
    except Exception as e:
        return error_500_print("Model error", e)


@model_bp.route('/modelconfig/getuser/<int:user_id>', methods=['GET'])
def get_user_config(user_id):
    try:
        config_list = ModelService.get_user_config(user_id)
        return SuccessResponse("获取model_info成功", config_list).to_json()
    except Exception as e:
        return error_500_print("Model error", e)


@model_bp.route('/modelconfig/create', methods=['POST'])
def create_model_config():
    data = request.get_json()
    if not data:
        return ErrorResponse(400, "请求数据不能为空").to_json()

    user_id = data.get("user_id")
    share_id = data.get("share_id")
    base_model_id = data.get("base_model_id")
    name = data.get("name")
    temperature = data.get("temperature")
    top_p = data.get("top_p")
    prompt = data.get("prompt")
    vector_db_id = data.get("vector_db_id")
    is_private = data.get("is_private")

    if not all([user_id, share_id, base_model_id, name, temperature, top_p, is_private]):
        return ErrorResponse(400, "缺少必要参数").to_json()

    try:
        config = ModelService.create_model_config(
            user_id,
            share_id,
            base_model_id,
            name,
            temperature,
            top_p,
            prompt,
            vector_db_id,
            is_private
        )
        return SuccessResponse("创建模型配置成功", config).to_json()
    except Exception as e:
        return error_500_print("Model error", e)


@model_bp.route('/modelconfig/update', methods=['POST'])
def update_model_config():
    data = request.get_json()
    if not data:
        return ErrorResponse(400, "请求数据不能为空").to_json()

    model_config_id = data.get("model_config_id")
    share_id = data.get("share_id")
    base_model_id = data.get("base_model_id")
    name = data.get("name")
    temperature = data.get("temperature")
    top_p = data.get("top_p")
    prompt = data.get("prompt")
    vector_db_id = data.get("vector_db_id")
    is_private = data.get("is_private")

    if not model_config_id:
        return ErrorResponse(400, "更新配置id不能为空").to_json()

    try:
        config = ModelService.update_model_config(
            model_config_id=model_config_id,
            share_id=share_id,
            base_model_id=base_model_id,
            name=name,
            temperature=temperature,
            top_p=top_p,
            prompt=prompt,
            vector_db_id=vector_db_id,
            is_private=is_private
        )
        return SuccessResponse("模型配置更新成功", config).to_json()
    except Exception as e:
        return error_500_print("Model error", e)
