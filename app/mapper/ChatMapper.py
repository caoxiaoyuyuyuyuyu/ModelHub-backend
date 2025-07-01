from app.utils.Redis import ConversationStore
from typing import Dict
from app.models.conversation import Conversation
from app.models.message import Message
from app.extensions import db

class ChatMapper:
    redis_client = ConversationStore().getRedis_client()
    prefix = "chat:"  # 键前缀，用于区分不同类型的数据

    @staticmethod
    def create_conversation(user_id: int, name: str, model_config_id: int, chat_history: int = 10) -> int:
        """
        创建对话
        :param user_id: 用户 id
        :param model_config_id: 模型配置 id
        :param chat_history: 上下文关联数量
        :return: 返回对话的 id
        """
        try:
            conversation = Conversation(user_id=user_id, name = name, model_config_id=model_config_id, chat_history=chat_history)
            db.session.add(conversation)
            db.session.commit()
            db.session.refresh(conversation)
            return conversation.id
        except Exception as e:
            db.session.rollback()
            raise Exception("创建对话失败"+str(e))
    @staticmethod
    def _format_key(conversation_id: int) -> str:
        """格式化对话键"""
        return f"{ChatMapper.prefix}{conversation_id}"
    @staticmethod
    def save_message(conversation_id: int, role: str, content: str) -> dict:
        """
        保存单条消息到对话历史
        :param conversation_id: 对话ID
        :param role: 角色（user或ai）
        :param content: 消息内容
        :return: 返回消息的字符串
        """
        try:
            key = ChatMapper._format_key(conversation_id)
            # 使用JSON格式序列化消息，保留角色和内容
            message = {"role": role, "content": content}
            # 保存到数据库中
            message_db = Message(conversation_id=conversation_id, role=role, content=content)
            db.session.add(message_db)
            db.session.commit()
            db.session.refresh(message_db)
            # 保存到redis中
            ChatMapper.redis_client.rpush(key, str(message))
            return {
                "role": message_db.role,
                "content": message_db.content
            }
        except Exception as e:
            db.session.rollback()
            print(f"消息添加失败: {e}")
            raise Exception({"code": 500, "msg": "保存消息失败" + str(e)})
    @staticmethod
    def get_conversation_id(user_id: int) -> list:
        """
        根据用户 id 查询对话
        :param user_id: 用户 id
        :return: 返回 conversation_id 的列表
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
    @staticmethod
    def get_conversation(conversation_id: int, length: int | None = None) -> dict:
        """
        获取对话历史
        :param conversation_id: 对话ID
        :return: 对话信息列表
        """
        try:
            conversation_info = ChatMapper.get_conversation_info(conversation_id)
            if not length:
                length = conversation_info["chat_history"]
            history = ChatMapper.get_history(conversation_id, length)
            return {
                "conversation_info": conversation_info,
                "history": history
            }
        except Exception as e:
            raise Exception({"code":500, "msg":"查询错误！获取用户对话失败"+str(e)})

    @staticmethod
    def get_conversation_info(conversation_id: int) -> dict:
        """
        获取对话的信息
        :param conversation_id: 对话 id
        :return: 返回该对话的信息
        """
        try:
            info = Conversation.query.get(conversation_id)
            return {
                "id":info.id,
                "name": info.name,
                "model_config_id": info.model_config_id,
                "chat_history": info.chat_history,
                "update_at": info.update_at.isoformat() if info.update_at else None
            }
        except Exception as e:
            raise Exception({"code":500, "msg":"获取对话信息失败！"+str(e)})


    @staticmethod
    def get_history(self, conversation_id: int, chat_history: int = 10) -> str:
        """
        获取单个对话的历史记录
        :param conversation_id: 对话 id
        :param chat_history: 获取的条数，默认为 10 条
        :return: 返回历史记录的列表
        """
        try:
            # 获取最新的前10条消息
            history = Message.query.filter_by(conversation_id=conversation_id)\
                .order_by(Message.create_at.desc())\
                .limit(chat_history)\
                .all()

            # 处理空结果
            if not history:
                return {
                    "messages": [],
                    "message": "该对话暂无历史消息"
                }

            # 转换为字典列表（使用列表推导式更简洁）
            messages = [{
                "role": m.role,
                "content": m.content,
                "create_at": m.create_at.isoformat() if m.create_at else None
            } for m in history]

            # 如果需要时间正序（最旧在前），取消下面这行的注释
            # messages.reverse()

            return {
                "messages": messages,
                "count": len(messages)
            }
        except Exception as e:
            # 更详细的错误信息
            error_msg = f"查询对话 {conversation_id} 的历史记录失败: {str(e)}"
            raise Exception({"code": 500, "msg": error_msg})

    @staticmethod
    def get_latest_message(conversation_id: int) -> Dict[str, str]:
        """获取最新的一条消息"""
        messages = ChatMapper.get_conversation(conversation_id,1)
        return messages[0] if messages else {}

    @staticmethod
    def get_conversation_length(conversation_id: int) -> int:
        """获取对话长度（消息数量）"""
        key = ChatMapper._format_key(conversation_id)
        return ChatMapper.redis_client.llen(key)

    @staticmethod
    def trim_conversation(conversation_id: int, max_length: int) -> None:
        """
        修剪对话历史，保留最近的max_length条消息
        :param conversation_id: 对话ID
        :param max_length: 保留的最大消息数
        """
        key = ChatMapper._format_key(conversation_id)
        ChatMapper.redis_client.ltrim(key, -max_length, -1)

    @staticmethod
    def delete_conversation(conversation_id: int) -> int:
        """
        删除对话
        :param conversation_id:
        :return:
        """
        try:
            # 删除 redis 中的对话
            key = ChatMapper._format_key(conversation_id)
            # 删除数据库中的对话
            conversation = Conversation.query.get(conversation_id)
            if conversation:
                Message.query.filter_by(conversation_id=conversation_id).delete()
                db.session.delete(conversation)
                db.session.commit()
            return ChatMapper.redis_client.delete(key)
        except Exception as e:
            db.session.rollback()
            raise Exception({"code":500, "msg":"对话删除失败"+str(e)})

    @staticmethod
    def set_chat_history(conversation_id: int, chat_history: int) -> dict:
        """
        修改conversation.chat_history参数
        :param conversation_id:
        :param chat_history:
        :return:
        """
        old_chat_history=-1
        try:
            conv=Conversation.query.get(conversation_id)
            old_chat_history = conv.chat_history
            conv.chat_history = chat_history
            db.session.commit()
            db.session.refresh(conv)
            return {
                "conversation_id": conversation_id,
                "old_chat_history": old_chat_history,
                "new_chat_history": conv.chat_history
            }
        except Exception as e:
            db.session.rollback()
            raise Exception({"code":500, "msg":"参数修改失败"+str(e)})
