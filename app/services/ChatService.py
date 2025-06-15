from app.mapper.ChatMapper import ChatMapper
from typing import List, Dict, Tuple

class ChatService:
    def __init__(self, conversation_id: str) -> None:
        self.conversation_id = conversation_id
        self.ChatMapper = ChatMapper()

    def _format_message_(self, role: str, message: str) -> List:
        """
        将消息转为列表
        :param role: 角色
        :param message: 消息
        :return: 返回列表，列表的每一项都是一个字典
        """
        result = []
        result.append({"role":f"{role}", "content":f"{message}"})
        return result

    def saveMessage(self, role: str, message: str) -> str:
        """
        保存用户的问题
        :param message: 用户的问题
        :return: None
        """
        message = self._format_message_(role, message)
        print(f"message: \n{message}")
        res = self.ChatMapper.save_messages(self.conversation_id, message)
        return res

    def chat(self) -> str:
        """
        获取回答并保存
        :return:
        """
        response = "智能ai为您服务！下面是我的回答：......"
        res = self.saveMessage("ai", response)
        return res


