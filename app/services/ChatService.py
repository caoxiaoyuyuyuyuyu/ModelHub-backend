import logging

from app.mapper.ChatMapper import ChatMapper
from app.services.VectorService import VectorService
from typing import List, Dict, Tuple
from llama_index.core.llms import ChatMessage, ChatResponse


from app.services import ModelService
from app.services.VectorService import VectorService
from app.utils.TransUtil import get_chatllm
from llama_index.core.llms import ChatMessage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
class ChatService:
    @staticmethod
    def create_conversation(user_id: int, model_config_id: int | None, message: str) -> int:
        """
        创建对话
        :param user_id: 用户 id
        :param model_config_id: 模型配置 id
        :param chat_history: 上下文关联数量
        :return:
        """
        try:
            name = message[:10]
            if not model_config_id:
                raise Exception({'code': 401, 'msg': "模型配置不存在"})
            return ChatMapper.create_conversation(user_id, name, model_config_id)
        except Exception as e:
            raise Exception({'code': 500, 'msg': "创建对话失败"+str(e)})


    @staticmethod
    def _format_message_(role: str, message: str) -> dict:
        """
        将消息转为字典格式
        :param role: 角色
        :param message: 消息内容
        :return: 返回字典 {"role": role, "content": message}
        """
        return {"role": role, "content": message}

    @staticmethod
    def saveMessage(conversation_id: int, role: str, message: str) -> str:
        """
        保存用户的问题
        :param message: 用户的问题
        :return: None
        """
        res = ChatMapper().save_message(conversation_id, role, message)
        return res

    @staticmethod
    def extract_response_content(response: any) -> any:
        """
        从不同格式的响应中提取内容
        :param response: 
        :return: 
        """
        # 正确处理 ChatResponse 对象
        if isinstance(response, ChatResponse):
            # 提取助手响应内容
            if response.message and hasattr(response.message, 'content'):
                content = response.message.content
            elif hasattr(response, 'text'):
                content = response.text
            else:
                # 尝试从原始响应中提取
                content = str(response)
                # 如果以 "assistant: " 开头，去除前缀
                if content.startswith("assistant: "):
                    content = content[len("assistant: "):]
        else:
            # 如果不是 ChatResponse，尝试直接转换为字符串
            content = str(response)

        # 其他未知格式
        return content

    @staticmethod
    def chat(vector_db_id: int, conversation_id: int, model_config_id: int, chat_history: int, message: str) -> str:
        """
        获取回答并保存
        :param vector_db_id: 向量数据库ID
        :param conversation_id: 对话ID
        :param model_config_id: 模型配置ID
        :param chat_history: 历史消息数量
        :param message: 用户消息
        :return: 助手响应内容
        """
        from app.utils.TransUtil import get_chatllm

        model = get_chatllm(model_config_id)
        history = ChatMapper().get_history(conversation_id, chat_history) or {"messages": []}

        # 使用当前消息进行向量查询
        query_text = message

        try:
            # 获取向量查询结果
            context_results = VectorService.query_vectors(vector_db_id, query_text, chat_history)

            # 提取文本内容并连接成字符串
            context_texts = []
            for result in context_results:
                if 'text' in result and result['text']:
                    context_texts.append(result['text'])
                elif 'content' in result and result['content']:
                    context_texts.append(result['content'])

            context = "\n\n".join(context_texts) if context_texts else "没有找到相关上下文信息"
        except Exception as e:
            print(f"向量查询失败: {str(e)}")
            context = "无法获取相关上下文信息"

        # 构建消息列表 - 使用 ChatMessage 对象而不是字典
        messages = []

        print(f"context:\n{context}")
        # 添加上下文作为系统消息
        if context:
            messages.append(ChatMessage(role="system", content=f"相关上下文信息：{context}"))

        # 添加历史对话消息
        for msg in history.get("messages", []):
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if content and role in ["system", "user", "assistant"]:
                messages.append(ChatMessage(role=role, content=content))

        # 添加当前用户消息
        messages.append(ChatMessage(role="user", content=message))

        print(f"准备的消息序列长度: {len(messages)}")
        for i, msg in enumerate(messages):
            print(f"消息 {i + 1}: 角色={msg.role}, 内容长度={len(msg.content)}")

        try:
            # 调用模型 chat 方法
            response = model.chat(messages)
            print(f"模型响应类型: {type(response)}")

            # 正确处理 ChatResponse 对象
            content = ChatService.extract_response_content(response)

        except Exception as e:
            import traceback
            print(f"模型对话失败详情: {traceback.format_exc()}")
            return "处理您的请求时出错"

        # 保存助手响应
        res = ChatMapper().save_message(conversation_id, "assistant", content)
        return res  # 返回助手响应内容


    @staticmethod
    def get_conversation(user_id: int) -> List:
        """
        获取对话的历史信息
        :param user_id: 用户 id
        :return: 返回历史信息的列表
        """
        conversation_id_list = ChatMapper.get_conversation_id(user_id)
        histories = []
        for item in conversation_id_list:
            conversation_id = item["conversation_id"]
            history = ChatMapper.get_conversation(conversation_id, 10)
            histories.append(history)
        return histories

    @staticmethod
    def get_history(conversation_id: int) -> dict:
        """
        获取对话的历史信息
        :param start: 开始位置，默认从第一条开始
        :param end: 结束的位置，默认最后一条
        :return: 返回历史信息的字符串
        """
        conversation_info = ChatMapper.get_conversation_info(conversation_id)
        history = ChatMapper.get_all_history(conversation_id)
        return {
            "conversation_info":conversation_info,
            "history": history
        }

    @staticmethod
    def delete_conversation(conversation_id: int) -> int:
        """
        删除对话
        :param conversation_id: 对话 id
        :return:
        """
        res = ChatMapper().delete_conversation(conversation_id)
        return res

    @staticmethod
    def set_chat_history(conversation_id: int, chat_history: int) -> dict:
        """
        修改conversation.chat_history参数
        :param conversation_id: id
        :param chat_history:
        :return:
        """
        res = ChatMapper.set_chat_history(conversation_id, chat_history)
        return res
    @staticmethod
    def query_contexts(model_config_id, message):
        return VectorService.query_vector_by_model(model_config_id, message)
