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

    message = data.get('message')
    response = OllamaService.chat(message)

    return response
