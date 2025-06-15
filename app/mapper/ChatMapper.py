from app.utils.Redis import ConversationStore
from typing import List, Dict, Tuple

class ChatMapper:
    def __init__(self):
        self.redis_client = ConversationStore().getRedis_client()
        self.prefix = "chat:"  # 键前缀，用于区分不同类型的数据

    def _format_key(self, conversation_id: str) -> str:
        """格式化对话键"""
        return f"{self.prefix}{conversation_id}"

    def save_message(self, conversation_id: str, role: str, content: str) -> int:
        """
        保存单条消息到对话历史
        :param conversation_id: 对话ID
        :param role: 角色（user或ai）
        :param content: 消息内容
        :return: 操作后列表的长度
        """
        key = self._format_key(conversation_id)
        # 使用JSON格式序列化消息，保留角色和内容
        message = {"role": role, "content": content}
        return self.redis_client.rpush(key, str(message))

    def save_messages(self, conversation_id: str, messages: List[Dict[str, str]]) -> str:
        """
        批量保存多条消息
        :param conversation_id: 对话ID
        :param messages: 消息列表，每个消息是包含role和content的字典
        """
        key = self._format_key(conversation_id)
        with self.redis_client.pipeline() as pipe:
            for msg in messages:
                pipe.rpush(key, str(msg))
            pipe.execute()
        return f"{messages}\n保存成功！"

    def get_conversation(self, conversation_id: str, start: int = 0, end: int = -1) -> List[Dict[str, str]]:
        """
        获取对话历史
        :param conversation_id: 对话ID
        :param start: 起始位置（默认0，即第一条消息）
        :param end: 结束位置（默认-1，即最后一条消息）
        :return: 消息列表
        """
        key = self._format_key(conversation_id)
        messages = self.redis_client.lrange(key, start, end)

        # 将字符串格式的消息转换为字典
        result = []
        for msg in messages:
            try:
                # 安全地解析字符串为字典
                msg_dict = eval(msg)  # 注意：这里使用eval，更安全的方式是使用JSON
                result.append(msg_dict)
            except Exception as e:
                print(f"解析消息失败: {e}")
                result.append({"role": "system", "content": f"[消息解析失败: {msg}]"})
        return result

    def get_latest_message(self, conversation_id: str) -> Dict[str, str]:
        """获取最新的一条消息"""
        messages = self.get_conversation(conversation_id, -1, -1)
        return messages[0] if messages else {}

    def get_conversation_length(self, conversation_id: str) -> int:
        """获取对话长度（消息数量）"""
        key = self._format_key(conversation_id)
        return self.redis_client.llen(key)

    def trim_conversation(self, conversation_id: str, max_length: int) -> None:
        """
        修剪对话历史，保留最近的max_length条消息
        :param conversation_id: 对话ID
        :param max_length: 保留的最大消息数
        """
        key = self._format_key(conversation_id)
        self.redis_client.ltrim(key, -max_length, -1)

    def delete_conversation(self, conversation_id: str) -> int:
        """删除整个对话"""
        key = self._format_key(conversation_id)
        return self.redis_client.delete(key)