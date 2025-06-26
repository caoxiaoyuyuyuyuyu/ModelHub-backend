from flask import Blueprint, request, jsonify

from app.forms.base import ErrorResponse, SuccessResponse
from app.services.ChatService import ChatService
from app.utils.JwtUtil import login_required

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')


@chat_bp.route("/", methods=['POST'])
@login_required
def chat() -> str:
    """
    对话
    :return: 返回json格式的字符串
    """
    conversation_id = request.form.get("conversation_id")
    message = request.form.get("message")

    user_id = request.headers.get("User-Id")
    model_config_id = request.form.get("model_config_id")
    chat_history = request.form.get("chat_history")
    vector_db_id = request.form.get("vector_db_id")

    try:
        if not conversation_id: # 创建对话
            id = ChatService.create_conversation(int(user_id), int(model_config_id), int(chat_history))
            conversation_id = id

        mes = ChatService.saveMessage(int(conversation_id), "user", str(message)) # 问题
        res = ChatService.chat(int(vector_db_id), int(conversation_id),
                               int(model_config_id), int(chat_history), message)  # 回答
        return SuccessResponse("对话成功！",
                               {"conversation_id": conversation_id, "response": res}).to_json()
    except Exception as e:
        return ErrorResponse(500, str(e)).to_json()

@chat_bp.route("/history", methods=['POST'])
@login_required
def get_history() -> str:
    """
    获取单个对话的历史记录
    :return: 返回json格式的字符串
    """
    conversation_id = request.form.get("conversation_id")
    if not conversation_id:
        return ErrorResponse(400, "conversation_id is null").to_json()
    try:
        history = ChatService.get_history(int(conversation_id))
        return SuccessResponse("历史记录获取成功！", history).to_json()
    except Exception as e:
        return ErrorResponse(500, str(e)).to_json()

@chat_bp.route("/histories", methods=['GET'])
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
        histories = ChatService.get_conversation(int(user_id))
        return SuccessResponse("历史记录获取成功！", histories).to_json()
    except Exception as e:
        return ErrorResponse(500, str(e)).to_json()

@chat_bp.route("/delete", methods=['POST', 'DELETE'])
@login_required
def delete_conversation() -> str:
    conversation_id = request.form.get("conversation_id")
    if not conversation_id:
        return ErrorResponse(400, "conversation_id is null").to_json()
    try:
        res = ChatService.delete_conversation(int(conversation_id))
        return SuccessResponse("删除对话成功！", {"delete": res, "msg": conversation_id+"已成功删除"}).to_json()
    except Exception as e:
        return ErrorResponse(500, str(e)).to_json()

@chat_bp.route("/set", methods=['POST', 'PUT'])
@login_required
def set_chat_history() -> str:
    """
    修改对话的 chat_history 参数
    :return: 返回字符串
    """
    chat_history = request.form.get("chat_history")
    conversation_id = request.form.get("conversation_id")
    if not chat_history and not conversation_id:
        return ErrorResponse(400, "params missing").to_json()
    try:
        res = ChatService.set_chat_history(int(conversation_id), int(chat_history))
        return SuccessResponse("修改chat_history成功！", {"res": res}).to_json()
    except Exception as e:
        return ErrorResponse(500, str(e)).to_json()

@chat_bp.route("/rechat", methods=['POST'])
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
        response = ChatService.rechat(conversation_id)  # 回答
        return SuccessResponse("对话成功", response).to_json()
    except Exception as e:
        return ErrorResponse(500, str(e)).to_json()