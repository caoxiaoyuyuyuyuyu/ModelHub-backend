from app.mapper import ModelMapper
from app.mapper import UserMapper
from flask import request


class ModelService:
    """模型服务类"""
    # 获取info列表
    @staticmethod
    def get_all_info():
        try:
            info_list = ModelMapper.get_all_model_info()
            model_info_list = []
            for info in info_list:
                model_info_list.append(
                    {
                        "id": info.id,
                        "model_name": info.model_name,
                        "supplier": info.supplier,
                        "describe": info.describe,
                        "type": info.type
                    }
                )
            return model_info_list
        except Exception as e:
            raise Exception({'code': 500, 'msg': "获取info列表失败"+str(e)})

    # 根据id获取model_info
    @staticmethod
    def get_info(info_id):
        try:
            model_info = ModelMapper.get_model_info_by_id(info_id)
            return {
                "id": model_info.id,
                "model_name": model_info.model_name,
                "supplier": model_info.supplier,
                "describe": model_info.describe,
                "type": model_info.type
            }
        except Exception as e:
            raise Exception({'code': 500, 'msg': "获取info失败"+str(e)})

    # 获取所有公开模型配置
    @staticmethod
    def get_public_config():
        try:
            config_list = ModelMapper.get_all_public_model_config()
            model_config_list = []
            for config in config_list:
                user_id = config.user_id
                user = UserMapper.get_user_by_id(user_id)

                base_model_id = config.base_model_id
                base_model = ModelMapper.get_model_info_by_id(base_model_id)

                model_config_list.append(
                    {
                        "id": config.id,
                        "name": config.name,
                        "author": user.name,
                        "base_model_name": base_model.model_name,
                        "share_id": config.share_id,
                        "describe": config.describe,
                        "update_at": config.update_at
                    }
                )
            return model_config_list
        except Exception as e:
            raise Exception({'code': 500, 'msg': "获取公共配置失败"+str(e)})

    # 根据config_id获取model_config
    @staticmethod
    def get_model_config_by_id(config_id: int):
        try:
            config = ModelMapper.get_model_config_by_id(config_id)
            user_id = config.user_id
            user = UserMapper.get_user_by_id(user_id)

            base_model_id = config.base_model_id
            base_model = ModelMapper.get_model_info_by_id(base_model_id)

            return {
                "id": config.id,
                "name": config.name,
                "author": user.name,
                "base_model_name": base_model.model_name,
                "share_id": config.share_id,
                "describe": config.describe,
                "update_at": config.update_at
            }
        except Exception as e:
            raise Exception({'code': 500, 'msg': "获取模型配置失败"+str(e)})

    @staticmethod
    def get_user_config_by_id(user_id):
        try:
            config_list = ModelMapper.get_model_config_by_user_id(user_id)
            model_config_list = []
            for config in config_list:
                if config.is_private is False:
                    user = UserMapper.get_user_by_id(user_id)

                    base_model_id = config.base_model_id
                    base_model = ModelMapper.get_model_info_by_id(base_model_id)

                    model_config_list.append(
                        {
                            "id": config.id,
                            "name": config.name,
                            "author": user.name,
                            "base_model_name": base_model.model_name,
                            "share_id": config.share_id,
                            "describe": config.describe,
                            "update_at": config.update_at
                        }
                    )

            return model_config_list
        except Exception as e:
            raise Exception({'code': 500, 'msg': "获取用户配置失败"+str(e)})

    @staticmethod
    def get_user_config(user):
        try:
            user_id = user.id
            config_list = ModelMapper.get_model_config_by_user_id(user_id)
            model_config_list = []
            for config in config_list:
                model_config_list.append(
                    {
                        "id": config.id,
                        "name": config.name,
                        "describe": config.describe,
                        "base_model_id": config.base_model_id,
                        "share_id": config.share_id,
                        "temperature": config.temperature,
                        "top_p": config.top_p,
                        "prompt": config.prompt,
                        "vector_db_id": config.vector_db_id,
                        "created_at": config.create_at,
                        "updated_at": config.update_at,
                        "is_private": config.is_private
                    }
                )
            return model_config_list
        except Exception as e:
            raise Exception({'code': 500, 'msg': "获取用户配置失败"+str(e)})


    @staticmethod
    def create_model_config(user_id, share_id, base_model_id, name, temperature, top_p, prompt, vector_db_id, is_private, describe):
        try:
            config = ModelMapper.create_model_config(
                user_id=user_id,
                share_id=share_id,
                base_model_id=base_model_id,
                name=name,
                temperature=temperature,
                top_p=top_p,
                prompt=prompt,
                vector_db_id=vector_db_id,
                is_private=is_private,
                describe=describe
            )
            return {
                "id": config.id,
                "name": config.name,
                "share_id": config.share_id,
                "base_model_id": config.base_model_id,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "prompt": config.prompt,
                "vector_db_id": config.vector_db_id,
                "create_at": config.create_at,
                "update_at": config.update_at,
                "is_private": config.is_private,
                "describe": config.describe
            }

        except Exception as e:
            raise Exception({'code': 500, 'msg': "创建模型配置失败"+str(e)})

    @staticmethod
    def update_model_config(
            model_config_id: int,
            share_id: str | None,
            base_model_id: int | None,
            name: str | None,
            temperature: float | None,
            top_p: float | None,
            prompt: str | None,
            vector_db_id: int | None,
            is_private: bool | None,
            describe: str | None
    ):
        try:
            config = ModelMapper.update_model_config_by_id(
                model_config_id=model_config_id,
                share_id=share_id,
                base_model_id=base_model_id,
                name=name,
                temperature=temperature,
                top_p=top_p,
                prompt=prompt,
                vector_db_id=vector_db_id,
                is_private=is_private,
                describe=describe
            )
            return {
                "id": config.id,
                "name": config.name,
                "share_id": config.share_id,
                "base_model_id": config.base_model_id,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "prompt": config.prompt,
                "vector_db_id": config.vector_db_id,
                "create_at": config.create_at,
                "update_at": config.update_at,
                "is_private": config.is_private,
                "describe": config.describe
            }
        except Exception as e:
            raise Exception({'code': 500, 'msg': "更新模型配置失败"+str(e)})

    @staticmethod
    def delete_model_config(config_id):
        try:
            config = ModelMapper.delete_model_config_by_id(config_id)
            return {
                "id": config.id,
                "name": config.name,
                "share_id": config.share_id,
                "base_model_id": config.base_model_id,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "prompt": config.prompt,
                "vector_db_id": config.vector_db_id,
                "create_at": config.create_at,
                "update_at": config.update_at,
                "is_private": config.is_private,
                "describe": config.describe
            }
        except Exception as e:
            raise Exception({'code': 500, 'msg': "删除模型配置失败"+str(e)})

