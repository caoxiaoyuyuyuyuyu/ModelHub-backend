import ollama
from tqdm import tqdm  # 导入进度条库

from app.mapper import UserMapper
from app.models.ollama_base_model_info import OllamaBaseModelInfo
from app.models.ollama_model_config import OllamaModelConfig
from sqlalchemy.orm import Session
from app.extensions import db


class OllamaModelMapper:
    # 使用 id 查询 model_info
    @staticmethod
    def get_model_info_by_id(model_info_id: int):
        return OllamaBaseModelInfo.query.get(model_info_id)

    # 获取全部model_info列表
    @staticmethod
    def get_all_model_info():
        return OllamaBaseModelInfo.query.all()

    # 使用id 查询 model_config
    @staticmethod
    def get_model_config_by_id(model_config_id: int):
        try:
            config = OllamaModelConfig.query.get(model_config_id)
            if not config:
                raise ValueError("model config not exist")
            return config
        except ValueError as ve:
            raise ve
        except Exception as e:
            raise Exception(f"模型配置获取失败:{str(e)}")

    # 根据 user_id 得到 用户model_config列表
    @staticmethod
    def get_model_config_by_user_id(user_id: int):
        return OllamaModelConfig.query.filter_by(user_id=user_id).all()


    # 创建一个新的model_config
    @staticmethod
    def create_model_config(
            user_id: int,
            base_model_id: int,
            name: str,
            temperature: float | None,
            top_p: float | None,
            top_k: int | None,
            num_keep: int | None,
            num_predict: int | None,
            describe: str | None
    ):
        try:
            # 检查存在用户
            if not UserMapper.get_user_by_id(user_id):
                raise ValueError("user not exist")

            if not OllamaModelMapper.get_model_info_by_id(base_model_id):
                raise ValueError("base_model not exist")

            model_config = OllamaModelConfig(
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
            model_config = OllamaModelMapper.get_model_config_by_id(model_config_id)
            if not model_config:
                raise ValueError("model config not exist")

            if base_model_id:
                model_config.base_model_id = base_model_id
            if name:
                model_config.name = name
            if temperature:
                model_config.temperature = temperature
            if top_p:
                model_config.top_p = top_p
            if top_k:
                model_config.top_k = top_k
            if num_keep:
                model_config.num_keep = num_keep
            if num_predict:
                model_config.num_predict = num_predict
            if describe:
                model_config.describe = describe
            db.session.commit()
            db.session.refresh(model_config)
            return model_config
        except Exception as e:
            db.session.rollback()
            raise Exception("更新模型配置失败" + str(e))

    # 删除模型配置
    @staticmethod
    def delete_model_config_by_id(config_id: int):
        try:
            model_config = OllamaModelConfig.query.get(config_id)
            if not model_config:
                raise ValueError("model config not exist")

            db.session.delete(model_config)
            db.session.commit()
            return model_config

        except ValueError as ve:
            db.session.rollback()
            raise ve
        except Exception as e:
            db.session.rollback()
            raise Exception(f"模型配置删除失败:{str(e)}")

    @staticmethod
    def create_model_info(
            model_name,
            model_supplier,
            describe):
        try:
            try:
                ollama.show(model_name)  # 尝试获取模型信息
            except Exception as e:
                print(f"模型 {model_name} 不存在，尝试拉取...")

                # 创建进度条
                with tqdm(
                    desc=f"拉取模型 {model_name}",
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024
                ) as pbar:
                    # 流式拉取模型并更新进度
                    for progress in ollama.pull(model_name, stream=True):
                        if 'completed' in progress and 'total' in progress:
                            # 更新进度条
                            pbar.total = progress['total']
                            pbar.update(progress['completed'] - pbar.n)
                        elif 'status' in progress:
                            # 更新状态描述
                            pbar.set_postfix_str(progress['status'])

                print(f"模型 {model_name} 拉取完成!")

            model_info = OllamaBaseModelInfo(
                model_name=model_name,
                model_supplier=model_supplier,
                describe=describe
            )
            db.session.add(model_info)
            db.session.commit()
            db.session.refresh(model_info)
            return model_info
        except Exception as e:
            db.session.rollback()
            raise Exception(f"模型信息创建失败:{str(e)}")