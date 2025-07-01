from ollama import ChatResponse


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