from flask import Blueprint, request, jsonify

from app.forms.base import ErrorResponse, SuccessResponse
from app.services.OllamaService import OllamaService
from app.utils.JwtUtil import login_required

ollama_bp = Blueprint('ollama', __name__, url_prefix='/ollama')

@ollama_bp.route("/chat", methods=['POST'])
@login_required
def chat() -> str:
    data = request.get_json()
    if not data:
        return ErrorResponse(400, "params missing").to_json()
    user_id = request.user.id
    message = data.get('message')
    model_config_id = data.get('model_config_id')
    conversation_id = data.get('conversation_id')
    response = OllamaService.chat(user_id, conversation_id, model_config_id, message)
    return SuccessResponse("success", response).to_json()
@ollama_bp.route("/config/chat", methods=['POST'])
@login_required
def config_chat() -> str:
    data = request.get_json()
    user_id = request.user.id
    message = data.get('message')
    model_config_id = data.get('model_config_id')
    if not (message and model_config_id):
        return ErrorResponse(400, "params missing").to_json()
    conversation_id = data.get('conversation_id')
    response = OllamaService.chat(user_id, conversation_id, model_config_id, message, type = 4)
    return SuccessResponse("success", response).to_json()