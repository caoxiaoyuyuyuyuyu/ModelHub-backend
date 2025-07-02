from flask import Blueprint, request, jsonify
from app.forms.base import ErrorResponse, SuccessResponse
from app.services import OllamaModelService
from app.utils.JwtUtil import login_required
from app.utils.exception_util import error_500_print

ollama_model_bp = Blueprint('ollama_model', __name__, url_prefix='/ollama_model')


@ollama_model_bp.route('/modelinfo/getlist', methods=['GET'])
def get_all_info():
    try:
        info_list = OllamaModelService.get_all_info()
        return SuccessResponse("获取model_info列表成功", info_list).to_json()
    except Exception as e:
        return error_500_print("Model error", e)


@ollama_model_bp.route('/modelinfo/get/<int:info_id>', methods=['GET'])
def get_info(info_id):
    try:
        model_info = OllamaModelService.get_info(info_id)
        return SuccessResponse("获取model_info成功", model_info).to_json()
    except Exception as e:
        return error_500_print("Model error", e)


@ollama_model_bp.route('/modelconfig/getuser', methods=['GET'])
@login_required
def get_user_config():
    try:
        user = request.user
        config_list = OllamaModelService.get_user_config(user)
        return SuccessResponse("获取用户模型配置成功", config_list).to_json()
    except Exception as e:
        return error_500_print("Model error", e)


@ollama_model_bp.route('/modelconfig/create', methods=['POST'])
@login_required
def create_model_config():
    user = request.user
    data = request.get_json()
    if not data:
        return ErrorResponse(400, "请求数据不能为空").to_json()

    user_id = user.id
    base_model_id = data.get("base_model_id")
    name = data.get("name")
    temperature = data.get("temperature")
    top_p = data.get("top_p")
    top_k = data.get("top_k")
    num_keep = data.get("num_keep")
    num_predict = data.get("num_predict")
    describe = data.get("describe")

    if not all([user_id, base_model_id, name, temperature, top_p, top_k, num_keep, num_predict]):
        return ErrorResponse(400, "缺少必要参数").to_json()

    try:
        config = OllamaModelService.create_model_config(
            user_id,
            base_model_id,
            name,
            temperature,
            top_p,
            top_k,
            num_keep,
            num_predict,
            describe
        )
        return SuccessResponse("创建模型配置成功", config).to_json()
    except Exception as e:
        return error_500_print("Model error", e)


@ollama_model_bp.route('/modelconfig/update', methods=['POST'])
@login_required
def update_model_config():
    data = request.get_json()
    if not data:
        return ErrorResponse(400, "请求数据不能为空").to_json()

    model_config_id = data.get("id")
    base_model_id = data.get("base_model_id")
    name = data.get("name")
    temperature = data.get("temperature")
    top_p = data.get("top_p")
    top_k = data.get("top_k")
    num_keep = data.get("num_keep")
    num_predict = data.get("num_predict")
    describe = data.get("describe")

    if not model_config_id:
        return ErrorResponse(400, "更新配置id不能为空").to_json()

    try:
        config = OllamaModelService.update_model_config(
            model_config_id=model_config_id,
            base_model_id=base_model_id,
            name=name,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            num_keep=num_keep,
            num_predict=num_predict,
            describe=describe
        )
        return SuccessResponse("模型配置更新成功", config).to_json()
    except Exception as e:
        return error_500_print("Model error", e)


@ollama_model_bp.route('/modelconfig/delete/<int:config_id>', methods=["DELETE"])
@login_required
def delete_model_config(config_id: int):
    try:
        config = OllamaModelService.delete_model_config(config_id)
        return SuccessResponse("模型配置删除成功", config).to_json()
    except Exception as e:
        return error_500_print("Model error", e)
