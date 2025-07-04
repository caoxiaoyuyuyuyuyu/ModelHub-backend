import logging

from app.mapper.ChatMapper import ChatMapper
from typing import List, Dict, Tuple

from app.services import ModelService
from app.services.VectorService import VectorService
from app.utils.TransUtil import get_chatllm
from llama_index.core.llms import ChatMessage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
class ChatService:
    @staticmethod
    def create_conversation(user_id: int, model_config_id: int | None, message: str, type: int = 0 ) -> int:
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
            return ChatMapper.create_conversation(user_id, name, model_config_id, type=type)
        except Exception as e:
            raise e

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
    def extract_response_content(response: any) -> str:
        """
        从不同格式的响应中提取内容
        :param response:
        :return:
        """
        # 情况1: ChatResponse对象（llama_index）
        if hasattr(response, 'message') and hasattr(response.message, 'content'):
            return response.message.content

        # 情况2: 字符串格式的响应
        if isinstance(response, str):
            # 尝试去除常见前缀
            for prefix in ["assistant: ", "Assistant: ", "AI: "]:
                if response.startswith(prefix):
                    return response[len(prefix):]
            return response

        # 情况3: 字典格式的响应
        if isinstance(response, dict):
            return response.get('content', response.get('response', str(response)))

        # 其他未知格式
        return str(response)

    @staticmethod
    def chat(user_id: int, conversation_id: int |  None, model_config_id, message: str) -> dict:
        """
        获取回答并保存
        :param conversation_id: 对话 id
        :param model_config_id: 模型配置 id
        :param message: 消息
        :return:
        """
        try:
            if not conversation_id:
                if not model_config_id:
                    raise Exception({'code': 401, 'msg': "模型配置不存在"})
                conversation_id = ChatService.create_conversation(user_id, model_config_id, message, 0)
            if not conversation_id:
                raise Exception({'code': 500, 'msg': "对话创建失败"})
            ChatMapper.save_message(conversation_id, "user", message)

            conversation = ChatMapper.get_conversation(conversation_id)

            conversation_info = conversation['conversation_info']
            model_config_id = conversation_info['model_config_id']
            history = conversation['history']["messages"]

            chat_messages_list = []
            for msg in reversed(history):
                chat_messages_list.append(ChatMessage(role=msg['role'], content=msg['content']))
            contexts = ChatService.query_contexts(model_config_id,message)
            context_result = "通过检索知识库已知：" + str(contexts) + "\n请根据检索结果和上下文回答用户问题，如果没有检索到知识，和用户说明情况"
            if contexts:
                chat_messages_list.append(ChatMessage(role="system", content=context_result))
                # logger.info(f"{msg['role']}:{msg['content']}")
            model = get_chatllm(model_config_id)
            response = model.chat(chat_messages_list)
            # 使用通用提取函数
            content = ChatService.extract_response_content(response)
            # 保存处理后的内容
            res = ChatMapper.save_message(conversation_id, "assistant", content)
            return {
                "response": res,
                "conversation_id": conversation_id,
                "conversation_name": conversation_info['name']
            }
        except Exception as e:
            raise
    @staticmethod
    def rechat(conversation_id: int) -> dict:
        """
        获取最新的一条消息
        :param conversation_id: 对话 id
        :return:
        """
        conversation = ChatMapper.get_conversation(conversation_id)
        # logger.info(f"conversation: {conversation}")
        conversation_info = conversation['conversation_info']
        model_config_id = conversation_info['model_config_id']
        history = conversation['history']["messages"]
        # logger.info(f"history: {len(history)}")

        chat_messages_list = []
        for msg in reversed(history):
            chat_messages_list.append(ChatMessage(role=msg['role'], content=msg['content']))
        chat_messages_list.append(ChatMessage(role="user", content='重新回答'))

        model = get_chatllm(model_config_id)
        response = model.chat(chat_messages_list)
        content = ChatService.extract_response_content(response)
        res = ChatMapper.save_message(conversation_id, "assistant", content)
        return {
            "response": res,
            "conversation_id": conversation_id,
            "conversation_name": conversation_info['name']
        }


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
