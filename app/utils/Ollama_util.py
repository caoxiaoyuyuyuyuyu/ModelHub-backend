from ollama import ChatResponse
from app.models.ollama_model_config import OllamaModelConfig
from app.models.ollama_base_model_info import OllamaBaseModelInfo
from app.utils.OllamaModel import OllamaModel

def generate_response_to_dict(response: ChatResponse):
    res_dict = {
        "model": response.model,
        "created_at": response.created_at,
        "response": response.response,
        "done": response.done,
        "context": response.context,
        "total_duration": response.total_duration,
        "load_duration": response.load_duration,
        "prompt_eval_count": response.prompt_eval_count,
        "prompt_eval_duration": response.prompt_eval_duration,
        "eval_count": response.eval_count,
        "eval_duration": response.eval_duration
    }
    return res_dict


def chat_response_to_dict(response: ChatResponse):
    res_dict = {
        "model": response.model,
        "response": response.message['content'],  # 注意这里是 message['content']
        "created_at": response.created_at,
        "done": response.done
    }
    return res_dict


def get_ollama_chat_model(model_config: int):
    model_config = OllamaModelConfig.query.get(model_config)
    if not model_config:
        raise Exception("模型配置不存在")

    base_model_id = model_config.base_model_id
    temperature = model_config.temperature
    top_p = model_config.top_p
    top_k = model_config.top_k
    num_keep = model_config.num_keep
    num_predict = model_config.num_predict

    base_model_info = OllamaBaseModelInfo.query.get(base_model_id)
    if not base_model_info:
        raise Exception("基础模型信息不存在")

    model_name = base_model_info.model_name

    try:
        ChatModel = OllamaModel(
            model_name=model_name,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            num_keep=num_keep,
            num_predict=num_predict
        )
        return ChatModel
    except Exception as e:
        raise Exception("聊天模型创建失败："+str(e))
