from app.utils.Redis import ConversationStore
from typing import List, Dict, Tuple
from app.models.conversation import Conversation
from app.models.message import Message
from app.extensions import db

class ChatMapper:
    def __init__(self):
        self.redis_client = ConversationStore().getRedis_client()
        self.prefix = "chat:"  # 键前缀，用于区分不同类型的数据

    def create_conversation(self, user_id: int, model_config_id: int, chat_history: int) -> str:
        """
        创建对话
        :param user_id: 用户 id
        :param model_config_id: 模型配置 id
        :param chat_history: 上下文关联数量
        :return:
        """
        try:
            conversation = Conversation(user_id=user_id, model_config_id=model_config_id, chat_history=chat_history)
            db.session.add(conversation)
            db.session.commit()
            db.session.refresh(conversation)
            return {
                "user_id": conversation.user_id,
                "model_config_id": conversation.model_config_id,
                "chat_history": conversation.chat_history
            }
        except Exception as e:
            db.session.rollback()
            raise Exception("创建对话失败"+str(e))

    def _format_key(self, conversation_id: str) -> str:
        """格式化对话键"""
        return f"{self.prefix}{conversation_id}"

    def save_message(self, conversation_id: int, role: str, content: str) -> str:
        """
        保存单条消息到对话历史
        :param conversation_id: 对话ID
        :param role: 角色（user或ai）
        :param content: 消息内容
        :return: 返回消息的字符串
        """
        try:
            key = self._format_key(conversation_id)
            # 使用JSON格式序列化消息，保留角色和内容
            message = {"role": role, "content": content}
             # 保存到数据库中
            message_db = Message(conversation_id=conversation_id, role=role, content=content)
            db.session.add(message_db)
            db.session.commit()
            db.session.refresh(message_db)
            # 保存到redis中
            self.redis_client.rpush(key, str(message))
            return {
                "conversation_id": message_db.conversation_id,
                "role": message_db.role,
                "content": message_db.content
            }
        except Exception as e:
            db.session.rollback()
            print(f"消息添加失败: {e}")
            raise Exception({"code": 500, "msg": "保存消息失败" + str(e)})

    def get_conversation_id(self, user_id: int) -> list:
        """
        根据用户 id 查询对话
        :param user_id:
        :return:
        """
        try:
            conversation_ids = Conversation.query.filter_by(user_id=user_id).all()

            conversation_id_list = []
            for conversation_id in conversation_ids:
                conversation_id_list.append({
                    "conversation_id": conversation_id.id
                })
            return conversation_id_list
        except Exception as e:
            raise Exception({"code":500, "msg":"查询错误！获取用户对话失败"+str(e)})

    def get_conversation(self, conversation_id: str) -> List[Dict[str, str]]:
        """
        获取对话历史
        :param conversation_id: 对话ID
        :return: 消息列表
        """
        try:
            history = self.get_history(conversation_id)
            return history
        except Exception as e:
            raise Exception({"code":500, "msg":"查询错误！获取用户对话失败"+str(e)})


    def get_history(self, conversation_id: int) -> str:
        """
        获取单个对话的历史记录
        :param conversation_id: 对话 id
        :return: 返回历史记录的列表
        """
        try:
            # 获取所有消息记录
            history = Message.query.filter_by(conversation_id=conversation_id).all()

            # 将消息转换为字典格式
            messages = []
            for message in history:
                messages.append({
                    "role": message.role,
                    "content": message.content
                })

            return {
                "conversation_id": conversation_id,
                "messages": messages  # 返回消息列表而不是单个消息
            }
        except Exception as e:
            raise Exception({"code":500, "msg": "查询历史记录失败"+str(e)})

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

    def delete_conversation(self, conversation_id: int) -> int:
        """删除整个对话"""
        try:
            # 删除 redis 中的对话
            key = self._format_key(conversation_id)
            # 删除数据库中的对话
            Message.query.filter_by(conversation_id=conversation_id).delete()
            Conversation.query.filter_by(id=conversation_id).delete()
            db.session.commit()
            return self.redis_client.delete(key)
        except Exception as e:
            db.session.rollback()
            raise Exception({"code":500, "msg":"对话删除失败"+str(e)})