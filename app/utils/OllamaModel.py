import ollama
from ollama import ChatResponse
from typing import Optional, List, Any, Sequence, Dict, Tuple
from app.utils.Ollama_util import generate_response_to_dict


# Ollama模型类封装
class OllamaModel:
    model_name: str = "deepseek-r1:1.5b"
    stream: bool = False
    num_keep: int = 1024
    num_predict: int = 1024
    top_k: int = 40
    top_p: float = 0.7
    temperature: float = 0.7

    def __init__(
            self,
            model_name: str = "deepseek-r1:1.5b",
            stream: bool = False,
            num_keep: int = 1024,
            num_predict: int = 1024,
            top_k: int = 40,
            top_p: float = 0.7,
            temperature: float = 0.7,
    ) -> None:
        self.model_name = model_name
        self.stream = stream
        self.num_keep = num_keep
        self.num_predict = num_predict
        self.top_k = top_k
        self.top_p = top_p
        self.temperature = temperature
        self._client = None

    # 获取参数
    def get_option(self):
        options = {
            "num_keep": self.num_keep,
            "num_predict": self.num_predict,
            "top_k": self.top_k,
            "top_p": self.top_p,
            "temperature": self.temperature,
        }
        return options

    # 单次文本生成
    def generate(self, prompt: str):
        try:

            response: ChatResponse = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                stream=self.stream,
                options=self.get_option()
            )
            return response
        except Exception as e:
            print(f"generate error : {e}")

    def chat(self, message: List[Dict]):
        try:
            response: ChatResponse = ollama.chat(
                model=self.model_name,
                messages=message,
                stream=self.stream
            )
            return response
        except Exception as e:
            print(f"chat error : {e}")


# generate响应dict
# {
#     "model": "llama3.2",
#     "created_at": "2023-08-04T19:22:45.499127Z",
#     "response": "The sky is blue because it is the color of the sky.",
#     "done": true,
#     "context": [1, 2, 3],
#     "total_duration": 4935886791,
#     "load_duration": 534986708,
#     "prompt_eval_count": 26,
#     "prompt_eval_duration": 107345000,
#     "eval_count": 237,
#     "eval_duration": 4289432000
# }

# chat响应dict
# {
#     "model": "llama3.2",
#     "created_at": "2023-12-12T14:13:43.416799Z",
#     "message": {
#         "role": "assistant",
#         "content": "Hello! How are you today?"
#     },
#     "done": true,
#     "total_duration": 5191566416,
#     "load_duration": 2154458,
#     "prompt_eval_count": 26,
#     "prompt_eval_duration": 383809000,
#     "eval_count": 298,
#     "eval_duration": 4799921000
# }


if __name__ == "__main__":
    model = OllamaModel()
    print(generate_response_to_dict(model.generate(prompt="写一首春天的诗")))
