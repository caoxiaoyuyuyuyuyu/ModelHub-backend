from app.mapper import UserMapper
from app.models.model_config import ModelConfig
from app.models.model_info import ModelInfo
from sqlalchemy.orm import Session
from app.extensions import db


class ModelMapper:
    # 使用 id 查询 model_info
    @staticmethod
    def get_model_info_by_id(model_info_id: int):
        return ModelInfo.query.get(model_info_id)

    # 获取全部model_info列表
    @staticmethod
    def get_all_model_info():
        return ModelInfo.query.all()

    # 使用id 查询 model_config
    @staticmethod
    def get_model_config_by_id(model_config_id: int):
        return ModelConfig.query.get(model_config_id)

    # 根据 user_id 得到 用户model_config列表
    @staticmethod
    def get_model_config_by_user_id(user_id: int):
        return ModelConfig.query.filter_by(user_id=user_id).all()

    # 获取全部公开的model_config
    @staticmethod
    def get_all_public_model_config():
        return ModelConfig.query.filter_by(is_private=False).all()

    # 创建一个新的model_config
    @staticmethod
    def create_model_config(
            user_id: int,
            share_id: str,
            base_model_id: int,
            name: str,
            temperature: float,
            top_p: float,
            prompt: str | None,
            vector_db_id: int | None,
            is_private: bool,
            describe: str | None
    ):
        try:
            # 检查存在用户
            if not UserMapper.get_user_by_id(user_id):
                raise ValueError("user not exist")

            if not ModelMapper.get_model_info_by_id(base_model_id):
                raise ValueError("base_model not exist")

            model_config = ModelConfig(
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
            db.session.add(model_config)
            db.session.commit()
            db.session.refresh(model_config)
            return model_config

        except ValueError as ve:
            db.session.rollback()
            raise ve
        except Exception as e:
            db.session.rollback()
            raise Exception(f"模型配置创建失败:{str(e)}")

    # 更新model_config
    @staticmethod
    def update_model_config_by_id(
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
            model_config = ModelMapper.get_model_config_by_id(model_config_id)
            if not model_config:
                raise ValueError("model config not exist")

            if share_id:
                model_config.share_id = share_id
            if base_model_id:
                model_config.base_model_id = base_model_id
            if name:
                model_config.name = name
            if temperature:
                model_config.temperature = temperature
            if top_p:
                model_config.top_p = top_p
            if prompt:
                model_config.prompt = prompt
            if vector_db_id:
                model_config.vector_db_id = vector_db_id
            if is_private:
                model_config.is_private = is_private
            if describe:
                model_config.describe = describe
            db.session.commit()
            db.session.refresh(model_config)
            return model_config
        except Exception as e:
            db.session.rollback()
            raise Exception("更新模型配置失败"+str(e))
