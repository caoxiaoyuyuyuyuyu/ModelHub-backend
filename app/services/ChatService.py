from app.mapper.ChatMapper import ChatMapper
from typing import List, Dict, Tuple

class ChatService:
    @staticmethod
    def create_conversation(user_id: int, model_config_id: int, chat_history: int) -> str:
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
            return Exception({'code': 500, 'msg': "创建对话失败"+str(e)})

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
    def chat(conversation_id: int) -> str:
        """
        获取回答并保存
        :return:
        """
        response = "智能ai为您服务！下面是我的回答：......"
        res = ChatMapper().save_message(conversation_id, "system", response)
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
    def set_chat_history(chat_history: int) -> str:
        pass