from app.mapper import OllamaModelMapper
from app.mapper import UserMapper
from flask import request


class OllamaModelService:
    """模型服务类"""

    # 获取info列表
    @staticmethod
    def get_all_info():
        try:
            info_list = OllamaModelMapper.get_all_model_info()
            model_info_list = []
            for info in info_list:
                model_info_list.append(
                    {
                        "id": info.id,
                        "model_name": info.model_name,
                        "supplier": info.model_supplier,
                        "describe": info.describe,
                    }
                )
            return model_info_list
        except Exception as e:
            raise Exception({'code': 500, 'msg': "获取info列表失败" + str(e)})

    # 根据id获取model_info
    @staticmethod
    def get_info(info_id):
        try:
            model_info = OllamaModelMapper.get_model_info_by_id(info_id)
            return {
                "id": model_info.id,
                "model_name": model_info.model_name,
                "supplier": model_info.model_supplier,
                "describe": model_info.describe,
            }
        except Exception as e:
            raise Exception({'code': 500, 'msg': "获取info失败" + str(e)})

    @staticmethod
    def get_user_config(user):
        try:
            user_id = user.id
            config_list = OllamaModelMapper.get_model_config_by_user_id(user_id)
            model_config_list = []
            for config in config_list:
                model_config_list.append(
                    {
                        "id": config.id,
                        "name": config.name,
                        "describe": config.describe,
                        "base_model_id": config.base_model_id,
                        "temperature": config.temperature,
                        "top_p": config.top_p,
                        "top_k": config.top_k,
                        "num_keep": config.num_keep,
                        "num_predict": config.num_predict,
                        "created_at": config.create_at,
                        "updated_at": config.update_at
                    }
                )
            return model_config_list
        except Exception as e:
            raise Exception({'code': 500, 'msg': "获取用户配置失败" + str(e)})

    @staticmethod
    def create_model_config(user_id, base_model_id, name, temperature, top_p, top_k, num_keep, num_predict, describe):
        try:
            config = OllamaModelMapper.create_model_config(
                user_id=user_id,
                base_model_id=base_model_id,
                name=name,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                num_keep=num_keep,
                num_predict=num_predict,
                describe=describe
            )
            return {
                "id": config.id,
                "name": config.name,
                "base_model_id": config.base_model_id,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "top_k": config.top_k,
                "num_keep": config.num_keep,
                "num_predict": config.num_predict,
                "create_at": config.create_at,
                "update_at": config.update_at,
                "describe": config.describe
            }

        except Exception as e:
            raise Exception({'code': 500, 'msg': "创建模型配置失败" + str(e)})

    @staticmethod
    def update_model_config(
            model_config_id: int,
            base_model_id: int | None,
            name: str | None,
            temperature: float | None,
            top_p: float | None,
            top_k: int | None,
            num_keep: int | None,
            num_predict: int | None,
            describe: str | None
    ):
        try:
            config = OllamaModelMapper.update_model_config_by_id(
                model_config_id=model_config_id,
                base_model_id=base_model_id,
                name=name,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                num_keep=num_keep,
                num_predict=num_predict,
                describe=describe
            )
            return {
                "id": config.id,
                "name": config.name,
                "base_model_id": config.base_model_id,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "top_k": config.top_k,
                "num_keep": config.num_keep,
                "num_predict": config.num_predict,
                "create_at": config.create_at,
                "update_at": config.update_at,
                "describe": config.describe
            }
        except Exception as e:
            raise Exception({'code': 500, 'msg': "更新模型配置失败" + str(e)})

    @staticmethod
    def delete_model_config(config_id):
        try:
            config = OllamaModelMapper.delete_model_config_by_id(config_id)
            return {
                "id": config.id,
                "name": config.name,
                "base_model_id": config.base_model_id,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "top_k": config.top_k,
                "num_keep": config.num_keep,
                "num_predict": config.num_predict,
                "create_at": config.create_at,
                "update_at": config.update_at,
                "describe": config.describe
            }
        except Exception as e:
            raise Exception({'code': 500, 'msg': "删除模型配置失败" + str(e)})
