from typing import List, Sequence, Dict
from llama_index.core.llms import ChatMessage


# 将模型消息转换成字典
def to_messages_dicts(messages: Sequence[ChatMessage]) -> List:
    return [
        {
            "role": message.role.value,
            "content": message.content
        }
        for message in messages
    ]


# 得到模型响应的额外信息
def get_additional_kwargs(response) -> Dict:
    return {
        "token_counts": response.usage.total_tokens,
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens
    }
