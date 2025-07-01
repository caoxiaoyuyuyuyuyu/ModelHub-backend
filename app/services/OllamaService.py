import logging
from app.mapper import OllamaMapper
from app.utils.OllamaModel import OllamaModel
from app.utils.Ollama_util import generate_response_to_dict, chat_response_to_dict
from typing import List, Dict, Tuple
from llama_index.core.llms import ChatMessage, ChatResponse

from app.utils.TransUtil import get_chatllm
from llama_index.core.llms import ChatMessage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class OllamaService:
    @staticmethod
    def chat(message: str) -> str:
        message = [
            {
                "role":"user",
                "content":message
            }
        ]
        try:
            model = OllamaModel()
            # 确保模型调用返回有效响应
            # model_response = model.generate(message)
            model_response = model.chat(message)

            # 添加空响应检查
            if model_response is None:
                raise ValueError("模型返回了空响应")

            # response = generate_response_to_dict(model_response)
            response = chat_response_to_dict(model_response)
            return response
        except Exception as e:
            # 包含原始错误信息
            raise Exception({'code': 500, 'msg': f"对话失败: {str(e)}"})