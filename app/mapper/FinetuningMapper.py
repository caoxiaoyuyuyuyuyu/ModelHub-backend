# app/mapper/FinetuningMapper.py
from app.models.finetuning_document import FinetuningDocument
from app.models.finetuning_model import FinetuningModel
from app.models.pre_finetuning_model import PreFinetuningModel
from app.models.finetuning_records import FinetuningRecords
from app.extensions import db


class FinetuningMapper:
    @staticmethod
    def create(model_class, **kwargs):
        try:
            instance = model_class(**kwargs)
            db.session.add(instance)
            db.session.commit()
            db.session.refresh(instance)
            return instance
        except Exception as e:
            db.session.rollback()
            raise Exception(f"创建记录失败: {str(e)}")

    @staticmethod
    def update(model_class, id, **kwargs):
        try:
            instance = model_class.query.get(id)
            if not instance:
                return None
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            db.session.commit()
            db.session.refresh(instance)
            return instance
        except Exception as e:
            db.session.rollback()
            raise Exception(f"更新记录失败: {str(e)}")

    @staticmethod
    def delete(model_class, id):
        try:
            instance = model_class.query.get(id)
            if not instance:
                return False
            db.session.delete(instance)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"删除记录失败: {str(e)}")

    @staticmethod
    def get_list(model_class, user_id=None):
        try:
            if model_class == FinetuningModel and user_id is not None:
                instances = model_class.query.filter_by(user_id=user_id).all()
            else:
                instances = model_class.query.all()
            return instances
        except Exception as e:
            raise Exception(f"获取记录列表失败: {str(e)}")

    @staticmethod
    def get_model_base(record_id):
        try:
            record = FinetuningRecords.query.get(record_id)
            if not record:
                return None
            base_model = PreFinetuningModel.query.get(record.base_model_id)
            if not base_model:
                return None
            return base_model
        except Exception as e:
            raise Exception(f"获取基础模型失败: {str(e)}")