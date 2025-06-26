from flask import Blueprint, request, jsonify
from app.forms.base import ErrorResponse, SuccessResponse
from app.services import ModelService
from app.utils.JwtUtil import login_required
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
        return SuccessResponse("获取公共模型配置成功", config_list).to_json()
    except Exception as e:
        return error_500_print("Model error", e)


@model_bp.route('/modelconfig/get/<int:config_id>')
def get_config_by_id(config_id: int):
    try:
        config = ModelService.get_model_config_by_id(config_id)
        return SuccessResponse("获取模型配置成功", config).to_json()
    except Exception as e:
        return error_500_print("Model error", e)


@model_bp.route('/modelconfig/getuser/<int:user_id>', methods=['GET'])
def get_user_config_by_id(user_id):
    try:
        config_list = ModelService.get_user_config_by_id(user_id)
        return SuccessResponse("获取用户模型配置成功", config_list).to_json()
    except Exception as e:
        return error_500_print("Model error", e)


@model_bp.route('/modelconfig/getuser', methods=['GET'])
@login_required
def get_user_config():
    try:
        user = request.user
        config_list = ModelService.get_user_config(user)
        return SuccessResponse("获取用户模型配置成功", config_list).to_json()
    except Exception as e:
        return error_500_print("Model error", e)


@model_bp.route('/modelconfig/create', methods=['POST'])
@login_required
def create_model_config():
    user = request.user
    data = request.get_json()
    if not data:
        return ErrorResponse(400, "请求数据不能为空").to_json()

    user_id = user.id
    share_id = data.get("share_id")
    base_model_id = data.get("base_model_id")
    name = data.get("name")
    temperature = data.get("temperature")
    top_p = data.get("top_p")
    prompt = data.get("prompt")
    vector_db_id = data.get("vector_db_id")
    is_private = data.get("is_private")
    describe = data.get("describe")

    if not all([user_id, share_id, base_model_id, name, temperature, top_p]):
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
            is_private,
            describe
        )
        return SuccessResponse("创建模型配置成功", config).to_json()
    except Exception as e:
        return error_500_print("Model error", e)


@model_bp.route('/modelconfig/update', methods=['POST'])
@login_required
def update_model_config():
    data = request.get_json()
    if not data:
        return ErrorResponse(400, "请求数据不能为空").to_json()

    model_config_id = data.get("id")
    share_id = data.get("share_id")
    base_model_id = data.get("base_model_id")
    name = data.get("name")
    temperature = data.get("temperature")
    top_p = data.get("top_p")
    prompt = data.get("prompt")
    vector_db_id = data.get("vector_db_id")
    is_private = data.get("is_private")
    describe = data.get("describe")

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
            is_private=is_private,
            describe=describe
        )
        return SuccessResponse("模型配置更新成功", config).to_json()
    except Exception as e:
        return error_500_print("Model error", e)


@model_bp.route('/modelconfig/delete/<int:config_id>', methods=["DELETE"])
@login_required
def delete_model_config(config_id: int):
    try:
        config = ModelService.delete_model_config(config_id)
        return SuccessResponse("模型配置删除成功", config).to_json()
    except Exception as e:
        return error_500_print("Model error", e)

@model_bp.route('/modelconfig/getshare', methods=["POST"])
@login_required
def get_share_model_config():
    try:
        data = request.get_json()
        share_id = data.get("share_id")
        if not share_id:
            return ErrorResponse(400, "share_id is null").to_json()
        config = ModelService.get_share_model_config(share_id)
        return SuccessResponse("获取模型配置成功", config).to_json()
    except Exception as e:
        return error_500_print("Model error", e)