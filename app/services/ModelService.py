from app.mapper import ModelMapper


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
                        "describe": info.describe,
                        "type": info.type
                    }
                )
            return model_info_list
        except Exception as e:
            raise

    # 根据id获取model_info
    @staticmethod
    def get_info(info_id):
        try:
            model_info = ModelMapper.get_model_info_by_id(info_id)
            return {
                "id": model_info.id,
                "model_name": model_info.name,
                "describe": model_info.describe,
                "type": model_info.type
            }
        except Exception as e:
            raise

    # 获取所有公开模型配置
    @staticmethod
    def get_public_config():
        try:
            config_list = ModelMapper.get_all_public_model_config()
            model_config_list = []
            for config in config_list:
                model_config_list.append(
                    {
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
                        "is_private": config.is_private
                    }
                )
            return model_config_list
        except Exception as e:
            raise

    @staticmethod
    def get_user_config(user_id):
        try:
            config_list = ModelMapper.get_model_config_by_user_id(user_id)
            model_config_list = []
            for config in config_list:
                model_config_list.append(
                    {
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
                        "is_private": config.is_private
                    }
                )
            return model_config_list
        except Exception as e:
            raise

    @staticmethod
    def create_model_config(user_id, share_id, base_model_id, name, temperature, top_p, prompt, vector_db_id, is_private):
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
                is_private=is_private
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
                "is_private": config.is_private
            }

        except Exception as e:
            raise

