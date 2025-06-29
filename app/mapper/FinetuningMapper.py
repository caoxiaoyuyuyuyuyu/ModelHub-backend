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
    def get(model_class, id):
        return model_class.query.get(id)

    @staticmethod
    def update(model_class, id, **kwargs):
        try:
            instance = FinetuningMapper.get(model_class, id)
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
            instance = FinetuningMapper.get(model_class, id)
            if not instance:
                return False
            db.session.delete(instance)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"删除记录失败: {str(e)}")