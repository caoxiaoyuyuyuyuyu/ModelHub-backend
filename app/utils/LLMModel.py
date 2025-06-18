from typing import Optional, List, Any, Sequence
from llama_index.core.bridge.pydantic import Field, PrivateAttr
from llama_index.core.constants import DEFAULT_CONTEXT_WINDOW, DEFAULT_NUM_OUTPUTS  # type ignore
from llama_index.core.llms import (
    CustomLLM,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
    ChatMessage,
    ChatResponse,
    MessageRole,
)
from openai import OpenAI


# 聊天模型类
class ChatGLM(CustomLLM):
    num_output: int = DEFAULT_NUM_OUTPUTS
    context_window: int = Field(default=DEFAULT_CONTEXT_WINDOW, description="模型文本的最大token数量", gt=0, )
    model: str = Field(description="基础模型名")
    api_key: str = Field(description="API key.")
    base_url: str = Field(description="base URL")
    top_p: float = Field(default=0.8, description="控制生成文本的多样性，值越大生成的文本越多样。")
    temperature: float = Field(default=0.7, description="控制生成文本的随机性，值越大生成的文本越随机。")
    system_prompt: str = Field(description="模型的系统提示")
    reuse_client: bool = Field(default=True, description=(
        "在多个请求间复用client。当处理大量的异步API请求时，设置该选项为FALSE可以提高稳定性。"
    ),
                               )
    _client: Optional[Any] = PrivateAttr()

    # 初始化函数
    def __init__(
            self,
            model: str,
            api_key: Optional[str],
            base_url: Optional[str],
            system_prompt: str,
            top_p: Optional[float] = 0.8,
            temperature: Optional[float] = 0.7,
            reuse_client: bool = True,
            **kwargs: Any,
    ) -> None:
        super().__init__(
            model=model,
            api_key=api_key,
            base_url=base_url,
            reuse_client=reuse_client,
            top_p=top_p,
            temperature=temperature,
            system_prompt=system_prompt,
            **kwargs,
        )
        self._client = None

    # 获取模型client
    def _get_client(self) -> OpenAI:
        if not self.reuse_client:
            return OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

        if self._client is None:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client

    @classmethod
    def class_name(cls) -> str:
        return "chat_llm"

    # 获取模型元数据
    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.num_output,
            model_name=self.model
        )

    # 封装OpenAI chat请求
    def _chat(self, messages: List, stream=False) -> Any:
        response = self._get_client().chat.completions.create(
            model=self.model,
            messages=messages,
            stream=stream,
            top_p=self.top_p,
            temperature=self.temperature,
        )
        return response

    # 聊天功能实现
    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        from .TransUtil import to_messages_dicts, get_additional_kwargs
        if isinstance(messages, str):
            messages = [ChatMessage(content=messages, role=MessageRole.USER)]

        message_dicts: List = to_messages_dicts(messages)
        response = self._chat(message_dicts, stream=False)

        rsp = ChatResponse(
            message=ChatMessage(
                content=response.choices[0].message.content,
                role=MessageRole(response.choices[0].message.role),
                additional_kwargs={}
            ),
            raw=response,
            additional_kwargs=get_additional_kwargs(response)
        )
        return rsp

    # 流式聊天功能实现
    def stream_chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> CompletionResponseGen:
        if isinstance(messages, str):
            messages = [ChatMessage(content=messages, role=MessageRole.USER)]

        response_text = ""
        message_dicts: List = to_messages_dicts(messages)
        response = self._chat(message_dicts, stream=False)

        for chunk in response:
            token = chunk.choices[0].delta.content
            if token is not None:
                response_text += token
                yield ChatResponse(
                    message=ChatMessage(
                        content=response_text,
                        role=MessageRole.ASSISTANT,
                        additional_kwargs={}
                    ),
                    delta=token,
                    raw=chunk
                )

    # 对话完成功能
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        messages = [
            {
                "role": MessageRole.USER,
                "content": prompt
            }
        ]

        try:
            response = self._chat(messages, stream=False)
            rsp = CompletionResponse(
                text=str(response.choices[0].message.content),
                raw=response,
                additional_kwargs=get_additional_kwargs(response)
            )

            return rsp
        except Exception as e:
            print(f"complete: exception {e}")

    # 流式对话完成功能
    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        response_text = ""
        messages = [
            {
                "role": MessageRole.USER,
                "prompt": prompt
            }
        ]
        response = self._chat(messages, stream=True)

        for chunk in response:
            token = chunk.choices[0].delta.content
            if token is not None:
                response_text += token
                yield CompletionResponse(text=response_text, delta=token)


if __name__ == "__main__":
    # 测试代码
    test_llm = ChatGLM(
        model="qwen-plus",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key="sk-1d8575bdb4ab4b64abde2da910ef578b",
        system_prompt="你是一个高中女孩"
    )
    # messages = [ChatMessage(content="讲个简短的笑话", role=MessageRole("user"))]
    # res = test_llm.chat(messages) # 测试传入列表
    # print(res.message.content)
    # print("--------------------------------")
    res = test_llm.chat("介绍一下你自己")  # 测试传入字符串
    print(res.message.content)
