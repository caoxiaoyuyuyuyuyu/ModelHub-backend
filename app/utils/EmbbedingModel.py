from typing import Optional
from typing import Any, List
from llama_index.core.bridge.pydantic import Field, PrivateAttr
from llama_index.core.embeddings import BaseEmbedding
from openai import OpenAI
import asyncio  # 添加 asyncio 导入

# 嵌入模型封装类
class ChatEmbeddings(BaseEmbedding):
    model: str = Field(description="使用的词嵌入模型")
    api_key: str = Field(description="API key.")
    base_url: str = Field(description="Base Url")
    reuse_client: bool = Field(default=True, description=(
        "Reuse the client between requests. When doing anything with large "
        "volumes of async API calls, setting this to false can improve stability."
    ),
                               )
    _client: Optional[Any] = PrivateAttr()

    # 初始化函数
    def __init__(
            self,
            model: str,
            api_key: Optional[str],
            base_url: Optional[str],
            reuse_client: bool = True,
            **kwargs: Any,
    ) -> None:
        super().__init__(
            model=model,
            api_key=api_key,
            base_url=base_url,
            reuse_client=reuse_client,
            **kwargs,
        )
        self._client = None

    # 客户端管理
    def _get_client(self) -> OpenAI:
        if not self.reuse_client:
            return OpenAI(api_key=self.api_key, base_url=self.base_url)

        if self._client is None:
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client

    @classmethod
    def class_name(cls) -> str:
        return "ChatEmbeddings"

    # 通用嵌入生成方法
    def get_general_text_embedding(self, prompt: str) -> List[float]:
        response = self._get_client().embeddings.create(
            model=self.model,
            input=prompt,
        )
        return response.data[0].embedding

    # 文本嵌入方法
    def _get_text_embedding(self, text: str) -> List[float]:
        return self.get_general_text_embedding(text)

    # 批量文本嵌入方法
    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        embedding_list: List[List[float]] = []

        for text in texts:
            embeddings = self.get_general_text_embedding(text)
            embedding_list.append(embeddings)

        return embedding_list

    # 查询嵌入方法
    def _get_query_embedding(self, query: str) -> List[float]:
        return self.get_general_text_embedding(query)

    # 异步查询嵌入方法
    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self.get_general_text_embedding(query)

    # 异步文本嵌入方法
    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self.get_general_text_embedding(text)

    # 异步批量文本嵌入方法
    async def _aget_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self._get_text_embeddings(texts)


if __name__ == "__main__":
    test_embedding = ChatEmbeddings(
        model="text-embedding-v3",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key="sk-1d8575bdb4ab4b64abde2da910ef578b"
    )
    print(len(test_embedding.get_general_text_embedding('test')))