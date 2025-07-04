import logging
from app.mapper import OllamaMapper, ChatMapper
from app.models.ollama_base_model_info import OllamaBaseModelInfo
from app.models.ollama_model_config import OllamaModelConfig
from app.services import ChatService
from app.utils.OllamaModel import OllamaModel
from app.utils.Ollama_util import generate_response_to_dict
from typing import List, Dict, Tuple
from llama_index.core.llms import ChatMessage, ChatResponse

from app.utils.TransUtil import get_chatllm
from llama_index.core.llms import ChatMessage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class OllamaService:
    @staticmethod
    def chat(user_id: int, conversation_id, model_config_id, message, type: int = 1) -> dict:
        try:
            if not conversation_id:
                if not model_config_id:
                    raise Exception({'code': 401, 'msg': "模型配置不存在"})
                conversation_id = ChatService.create_conversation(user_id, model_config_id, message, type)
                if not conversation_id:
                    raise Exception({'code': 500, 'msg': "对话创建失败"})
            ChatMapper.save_message(conversation_id, "user", message)
            print("conversation_id:", conversation_id)
            conversation = ChatMapper.get_conversation(conversation_id)

            conversation_info = conversation['conversation_info']
            model_config_id = conversation_info['model_config_id']
            history = conversation['history']["messages"]
            print("history:", history)
            if type == 1:
                model_name = OllamaBaseModelInfo.query.filter_by(id=model_config_id).first().model_name
                model = OllamaModel(model_name=model_name)
            else:
                model_config = OllamaModelConfig.query.filter_by(id=model_config_id).first()
                if not model_config:
                    raise Exception({'code': 401, 'msg': "模型配置不存在"})
                base_model_name = OllamaBaseModelInfo.query.filter_by(id=model_config.base_model_id).first().model_name
                model = OllamaModel(model_name=base_model_name,
                                    temperature=model_config.temperature,
                                    top_p=model_config.top_p,
                                    top_k=model_config.top_k,
                                    num_keep=model_config.num_keep,
                                    num_predict=model_config.num_predict
                                    )
            model_response = model.chat(history)

            # 添加空响应检查
            if model_response is None:
                raise ValueError("模型返回了空响应")

            # response = generate_response_to_dict(model_response)
            response = model_response.message.get('content')
            print("response:", response)
            res = ChatMapper.save_message(conversation_id, "assistant", response)
            return {
                "response": res,
                "conversation_id": conversation_id,
                "conversation_name": conversation_info['name']
            }
        except Exception as e:
            # 包含原始错误信息
            raise Exception({'code': 500, 'msg': f"对话失败: {str(e)}"})
