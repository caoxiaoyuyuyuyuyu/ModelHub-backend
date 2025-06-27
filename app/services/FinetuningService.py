# app/services/FinetuningService.py
from app.mapper.FinetuningMapper import FinetuningMapper
from app.models.finetuning_document import FinetuningDocument
from app.models.finetuning_model import FinetuningModel
from app.models.pre_finetuning_model import PreFinetuningModel
from app.models.finetuning_records import FinetuningRecords


class FinetuningService:
    @staticmethod
    def create(model_name, **kwargs):
        model_class = {
            'finetuning_document': FinetuningDocument,
            'finetuning_model': FinetuningModel,
            'pre_finetuning_model': PreFinetuningModel,
            'finetuning_records': FinetuningRecords
        }.get(model_name)
        if not model_class:
            raise ValueError("无效的模型名称")
        return FinetuningMapper.create(model_class, **kwargs)

    @staticmethod
    def get(model_name, id):
        model_class = {
            'finetuning_document': FinetuningDocument,
            'finetuning_model': FinetuningModel,
            'pre_finetuning_model': PreFinetuningModel,
            'finetuning_records': FinetuningRecords
        }.get(model_name)
        if not model_class:
            raise ValueError("无效的模型名称")
        return FinetuningMapper.get(model_class, id)

    @staticmethod
    def update(model_name, id, **kwargs):
        model_class = {
            'finetuning_document': FinetuningDocument,
            'finetuning_model': FinetuningModel,
            'pre_finetuning_model': PreFinetuningModel,
            'finetuning_records': FinetuningRecords
        }.get(model_name)
        if not model_class:
            raise ValueError("无效的模型名称")
        return FinetuningMapper.update(model_class, id, **kwargs)

    @staticmethod
    def delete(model_name, id):
        model_class = {
            'finetuning_document': FinetuningDocument,
            'finetuning_model': FinetuningModel,
            'pre_finetuning_model': PreFinetuningModel,
            'finetuning_records': FinetuningRecords
        }.get(model_name)
        if not model_class:
            raise ValueError("无效的模型名称")
        return FinetuningMapper.delete(model_class, id)