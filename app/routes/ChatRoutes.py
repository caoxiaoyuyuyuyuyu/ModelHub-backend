from flask import Blueprint, request, jsonify

from app.forms.base import ErrorResponse, SuccessResponse
from app.services.ChatService import ChatService
from app.utils.JwtUtil import login_required

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route("/", methods=['POST'])
def chat() -> str:
    """
    对话
    :return: 返回json格式的字符串
    """
    message = request.form.get("message")
    if not message:
        return ErrorResponse(400, "Message is null").to_json()
    try:
        service = ChatService("0001")
        mes = service.saveMessage("user", message) # 问题
        res = service.chat()  # 回答
    #     return jsonify({"mes": mes, "res": res})
        return SuccessResponse("读取历史信息成功！", {"mes": mes, "res": res}).to_json()
    except Exception as e:
        return ErrorResponse(500, str(e)).to_json()