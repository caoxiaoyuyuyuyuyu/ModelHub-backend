import logging
from app.mapper.OllamaMapper import OllamaMapper
from app.utils.OllamaModel import OllamaModel
from typing import List, Dict, Tuple, Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class OllamaService:
    @staticmethod
    def create_conversation(user_id: int, model_config_id: int | None, message: str, model_type: int) -> int:
        """
        创建对话
        :param user_id: 用户 id
        :param model_config_id: 模型配置 id
        :param chat_history: 上下文关联数量
        :param model_type: 模型类型
        :return:
        """
        try:
            name = message[:10]
            if not model_config_id:
                raise Exception({'code': 401, 'msg': "模型配置不存在"})
            return OllamaMapper.create_conversation(user_id, name, model_config_id, model_type)
        except Exception as e:
            raise Exception({'code': 500, 'msg': "创建对话失败" + str(e)})

    @staticmethod
    def saveMessage(conversation_id: int, role: str, message: str) -> str:
        """
        保存用户的问题
        :param message: 用户的问题
        :return: None
        """
        res = OllamaMapper.save_message(conversation_id, role, message)
        return res

    @staticmethod
    def chat(conversation_id: int, message: str) -> str:
        """
        获取回答并保存
        :param conversation_id: 对话ID
        :param message: 用户消息
        :return: 助手响应内容
        """
        try:
            message = [
                {
                    "role":"user",
                    "content":message
                }
            ]
            model = OllamaModel()
            content = model.chat(message)
            # 保存助手响应
            res = OllamaMapper.save_message(conversation_id, "assistant", content)
            return res  # 返回助手响应内容
        except Exception as e:
            raise Exception({'status': 'error', 'message': "聊天失败！"+str(e)})

    @staticmethod
    def get_conversation(user_id: int) -> List:
        """
        获取对话的历史信息
        :param user_id: 用户 id
        :return: 返回历史信息的列表
        """
        conversation_id_list = OllamaMapper.get_conversation_id(user_id)
        histories = []
        for item in conversation_id_list:
            conversation_id = item["conversation_id"]
            history = OllamaMapper.get_conversation(conversation_id, 10)
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
        conversation_info = OllamaMapper.get_conversation_info(conversation_id)
        history = OllamaMapper.get_history(conversation_id)
        return {
            "conversation_info": conversation_info,
            "history": history
        }

    @staticmethod
    def delete_conversation(conversation_id: int) -> int:
        """
        删除对话
        :param conversation_id: 对话 id
        :return:
        """
        res = OllamaMapper.delete_conversation(conversation_id)
        return res






    @staticmethod
    def download(model_name: str) -> Dict[str, Any]:
        """
        下载模型
        :return:
        """
        logger.info(f"开始下载模型: {model_name}")
        try:
            model_details = OllamaModel.pull_model(model_name)
            logger.info(f"模型下载完成: {model_name}")

            return {'status': 'success', 'model': model_details}
        except Exception as e:
            logger.error(f"下载模型失败: {e}")
            raise Exception({'status': 'error', 'message': str(e)})

    @staticmethod
    def delete_model(model_name: str) -> Dict[str, Any]:
        """删除模型"""
        logger.info(f"开始删除模型: {model_name}")
        try:
            delete_info = OllamaModel.delete_model(model_name)
            logger.info(f"模型删除成功: {model_name}")

            return delete_info
        except Exception as e:
            logger.error(f"删除模型失败: {e}")
            raise Exception({'status': 'error', 'message': str(e)})


    @staticmethod
    def get_model_list() -> List[Dict[str, Any]]:
        """列出所有模型（本地+数据库）"""
        local_models = OllamaModel.local_model_list()

        # 获取数据库中的模型
        db_models = []
        try:
            pass
        except Exception as e:
            logger.error(f"获取数据库模型失败: {e}")
            raise Exception({"code":500, "msg":"数据库中的模型获取失败！"+str(e)})

        # 合并结果
        return {
            'local_models': local_models,
            'db_models': db_models
        }

