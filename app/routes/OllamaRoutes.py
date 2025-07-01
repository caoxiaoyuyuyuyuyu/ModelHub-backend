from flask import Blueprint, request, jsonify

from app.forms.base import ErrorResponse, SuccessResponse
from app.services.OllamaService import OllamaService
from app.utils.JwtUtil import login_required

ollama_bp = Blueprint('ollama', __name__, url_prefix='/ollama')

@ollama_bp.route("/chat", methods=['POST'])
@login_required
def chat() -> str:
    """
    对话
    :return: 返回json格式的字符串
    """
    conversation_id = request.form.get("conversation_id")
    message = request.form.get("message")
    model_config_id = request.form.get("model_config_id")
    chat_history = request.form.get("chat_history")
    ollama_config_id = request.form.get('ollama_config_id')
    model_type = request.form.get("model_type")

    user_id = request.headers.get("User-Id")

    try:
        if not conversation_id: # 创建对话
            id = OllamaService.create_conversation(int(user_id), int(model_config_id),
                                                   int(chat_history), int(model_type))
            conversation_id = id

        mes = OllamaService.saveMessage(int(conversation_id), "user", str(message)) # 问题
        res = OllamaService.chat(int(conversation_id), int(ollama_config_id), message)  # 回答
        return SuccessResponse("对话成功！",
                               {"conversation_id": conversation_id, "response": res}).to_json()
    except Exception as e:
        return ErrorResponse(500, str(e)).to_json()


@ollama_bp.route("/history", methods=['POST'])
@login_required
def get_history() -> str:
    """
    获取单个对话的历史记录
    :return: 返回json格式的字符串
    """
    conversation_id = request.form.get("conversation_id")
    if not conversation_id:
        return ErrorResponse(400, "conversation_id and model_type is null").to_json()
    try:
        history = OllamaService.get_history(int(conversation_id))
        return SuccessResponse("历史记录获取成功！", history).to_json()
    except Exception as e:
        return ErrorResponse(500, str(e)).to_json()

@ollama_bp.route("/histories", methods=['GET'])
@login_required
def get_conversation() -> str:
    """
    获取对话的列表
    :return: 返回json格式的字符串
    """
    user_id = request.user.id
    if not user_id:
        return ErrorResponse(400, "user_id is null").to_json()
    try:
        histories = OllamaService.get_conversation(int(user_id))
        return SuccessResponse("历史记录获取成功！", histories).to_json()
    except Exception as e:
        return ErrorResponse(500, str(e)).to_json()

@ollama_bp.route("/delete", methods=['POST', 'DELETE'])
@login_required
def delete_conversation() -> str:
    conversation_id = request.form.get("conversation_id")
    if not conversation_id:
        return ErrorResponse(400, "conversation_id is null").to_json()
    try:
        res = OllamaService.delete_conversation(int(conversation_id))
        return SuccessResponse("删除对话成功！", {"delete": res, "msg": conversation_id+"已成功删除"}).to_json()
    except Exception as e:
        return ErrorResponse(500, str(e)).to_json()

@ollama_bp.route("/rechat", methods=['POST'])
@login_required
def rechat() -> str:
    """
    重新回答该问题
    :return:
    """
    conversation_id_str = request.form.get("conversation_id")
    conversation_id = int(conversation_id_str)

    if not conversation_id:
        return ErrorResponse(400, "Params missing").to_json()

    try:
        response = OllamaService.rechat(conversation_id)  # 回答
        return SuccessResponse("对话成功", response).to_json()
    except Exception as e:
        return ErrorResponse(500, str(e)).to_json()





@ollama_bp.route("/download", methods=['POST'])
@login_required
def download() -> str:
    """
    下载模型
    :return:
    """
    data = request.get_json()
    model_name = data.get('model_name')
    response = OllamaService.download(model_name)

    return response

@ollama_bp.route("/delete", methods=['POST', 'DELETE'])
@login_required
def delete_model() -> str:
    """
    删除模型
    :return:
    """
    data = request.get_json()
    model_name = data.get('model_name')
    response = OllamaService.delete_model(model_name)

    return response

@ollama_bp.route("/local_list", methods=['GET'])
@login_required
def get_model_list() -> str:
    """
    获取模型列表
    :return:
    """
    response = OllamaService.get_model_list()

    return response
