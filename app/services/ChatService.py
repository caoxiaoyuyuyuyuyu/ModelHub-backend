from app.mapper.ChatMapper import ChatMapper
from app.services.VectorService import VectorService
from typing import List, Dict, Tuple

class ChatService:
    @staticmethod
    def create_conversation(user_id: int, model_config_id: int, chat_history: int) -> int:
        """
        创建对话
        :param user_id: 用户 id
        :param model_config_id: 模型配置 id
        :param chat_history: 上下文关联数量
        :return:
        """
        try:
            res = ChatMapper().create_conversation(user_id, model_config_id, chat_history)
            return res
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
    def chat(user_id: int, conversation_id: int, model_config_id: int, chat_history: int, message: str) -> str:
        """
        获取回答并保存
        :param conversation_id: 对话 id
        :param model_config_id: 模型配置 id
        :param message: 消息
        :return:
        """
        from app.utils.TransUtil import get_chatllm

        model = get_chatllm(model_config_id) # 获取模型
        history = ChatMapper().get_history(conversation_id, chat_history) # 获取历史记录
        m_message = { # 组合
            "message": message,
            "history": history["messages"]
        }
        vector_db_id = VectorService.get_vectordb_id(user_id) # 获取 vector_db_id

        chat_content = VectorService.query_vectors(vector_db_id, m_message) # 检索
        response = model.chat(chat_content) # 对话
        # 使用通用提取函数
        content = ChatService.extract_response_content(response)

        # 保存处理后的内容
        res = ChatMapper().save_message(conversation_id, "assistant", content)
        return res

    @staticmethod
    def get_conversation(user_id: int) -> str:
        """
        获取对话的历史信息
        :param user_id: 用户 id
        :return: 返回历史信息的列表
        """
        conversation_id_list = ChatMapper().get_conversation_id(user_id)
        histories = []
        for item in conversation_id_list:
            conversation_id = item["conversation_id"]
            history = ChatMapper().get_conversation(conversation_id)
            histories.append(history)
        return histories

    @staticmethod
    def get_history(conversation_id: int) -> str:
        """
        获取对话的历史信息
        :param start: 开始位置，默认从第一条开始
        :param end: 结束的位置，默认最后一条
        :return: 返回历史信息的字符串
        """
        history = ChatMapper().get_history(conversation_id)
        return history

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
    def set_chat_history(conversation_id: int, chat_history: int) -> str:
        """
        修改conversation.chat_history参数
        :param conversation_id: id
        :param chat_history:
        :return:
        """
        res = ChatMapper().set_chat_history(conversation_id, chat_history)
        return res