# app/services/FinetuningService.py
import os

from flask import current_app, send_file
from scipy.stats import describe

from app.mapper import ChatMapper
from app.mapper.FinetuningMapper import FinetuningMapper
from app.models import FinetuningDocument
from app.models import FinetuningModel
from app.models import PreFinetuningModel
from app.models import FinetuningRecords
from app.services import ChatService
from app.utils.PEFT.ChatWithBase import chat_with_base
from app.utils.PEFT.ChatWithFintuned import chat_with_finetuned
from app.utils.PEFT.DownloadModel import robust_download_model
from app.utils.PEFT.ModelTrainer import finetune
from app.utils.file_utils import save_uploaded_file
from app.utils.PEFT.ModelTrainer import ProgressCallback

class FinetuningService:
    @staticmethod
    def create(data, user_id, file, socketio):
        params = {
            "base_model_id": int(data.get('base_model_id')),
            "load_in_4bit": bool(data.get('load_in_4bit')),
            "use_lora": bool(data.get('use_lora')),
            "lora_r": int(data.get('lora_r')),
            "lora_alpha": int(data.get('lora_alpha')),
            "lora_dropout": float(data.get('lora_dropout')),
            "gradient_accumulation_steps": int(data.get('gradient_accumulation_steps')),
            "num_train_epochs": int(data.get('num_train_epochs')),
            "logging_steps": int(data.get('logging_steps')),
            "save_strategy": "epoch",
            "fp16": bool(data.get('fp16')),
            "optim": "paged_adamw_8bit",
        }
        base_model_path = PreFinetuningModel.query.get(data.get('base_model_id')).path
        if not base_model_path:
            raise ValueError("无效的模型ID")
        finetuning_dir = current_app.config.get('FINETUNING_DIR')
        if not finetuning_dir:
            raise ValueError("Finetuning directory not configured")
        os.makedirs(finetuning_dir, exist_ok=True)
        file_name = save_uploaded_file(file, current_app.config['FINETUNING_DIR'])
        if not file_name:
            raise ValueError("上传文件失败")
        try:
            output_dir = os.path.join(current_app.config.get('FINETUNING_DIR'), "outputs", str(user_id), data.get('model_name'))
            log_path = os.path.join(current_app.config.get('FINETUNING_DIR'), "outputs", str(user_id), data.get('model_name')+"training_logs.json")
            # 创建回调实例并传入 socketio
            progress_callback = ProgressCallback(log_path, socketio)

            finetune(
                base_model_path,
                os.path.join(current_app.config['FINETUNING_DIR'], file_name),
                data.get('training_type'),
                output_dir,
                log_path,
                callbacks=[progress_callback],  # 传入回调
                **params
            )
            params["output_dir"]=output_dir
            params["log_path"]=log_path
            record =  FinetuningMapper.create(FinetuningRecords, **params)
            FinetuningMapper.create(FinetuningDocument, **{
                "user_id": user_id,
                "record_id": record.id,
                "name": file_name,
                "original_name": file.filename,
                "type": data.get('training_type'),
                "size": file.content_length,
                "save_path": file_name,
                "describe": data.get('describe'),
            })
            FinetuningModelParams = {
                "user_id": user_id,
                "name": data.get('model_name'),
                "describe": data.get('describe'),
                "record_id": record.id,
                "status": "completed"
            }
            return FinetuningMapper.create(FinetuningModel, **FinetuningModelParams)
        except Exception as e:
            current_app.logger.error(f"模型微调失败: {str(e)}")
            return None

    @staticmethod
    def get_model_info(model_id):
        try:
            finetuning_model = FinetuningModel.query.get(model_id)
            finetuning_record = FinetuningRecords.query.get(finetuning_model.record_id)
            pre_finetuning_model = PreFinetuningModel.query.get(finetuning_record.base_model_id)

            # 确保 FinetuningDocument 是模型类，而不是字符串
            from app.models.finetuning_document import FinetuningDocument  # 显式导入

            finetuning_document = FinetuningDocument.query.filter_by(record_id=finetuning_record.id).first()
            if not finetuning_document:
                raise ValueError("No document found for this record")

            finetuning_record = finetuning_record.to_dict()
            finetuning_record['fine_tuned_model'] = finetuning_model.to_dict()
            finetuning_record['base_model'] = pre_finetuning_model.to_dict()
            finetuning_record['fine_tune_document'] = finetuning_document.to_dict()
            return finetuning_record
        except Exception as e:
            raise e

    @staticmethod

    def get_model(model_id):
        try:
            info = FinetuningService.get_model_info(model_id)
            return {
                'model_path': info['base_model']['path'],
                'name': info['fine_tuned_model']['name'],
                'peft_model_path':  info['output_dir'],
                'load_in_4bit': info['load_in_4bit'],
            }
        except Exception as e:
            raise e
    @staticmethod
    def get_model_base(model_id):
        model = PreFinetuningModel.query.get(model_id)
        return {
            "model_path": model.path,
            "name": model.name,
        }
        
    
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

    @staticmethod
    def get_list(model_name, user_id):
        model_class = {
            'finetuning_model': FinetuningModel,
            'pre_finetuning_model': PreFinetuningModel,
        }.get(model_name)
        if not model_class:
            raise ValueError("无效的模型名称")
        if model_name == 'finetuning_model':
            return FinetuningMapper.get_list(model_class, user_id)
        return FinetuningMapper.get_list(model_class)

    @staticmethod
    def download_logs(record_id):
        log_path = FinetuningRecords.query.get(record_id).log_path
        file_name = log_path.split('/')[-1]
        print("log_path", log_path)
        return file_name, log_path

    @staticmethod
    def chat(user_id: int, conversation_id, model_config_id, message):
        """
        获取回答并保存
        :param model_config_id: 模型配置 id
        :param message: 消息
        :return:
        """
        try:
            if not conversation_id:
                if not model_config_id:
                    raise Exception({'code': 401, 'msg': "模型配置不存在"})
                conversation_id = ChatService.create_conversation(user_id, model_config_id, message, 3)
                if not conversation_id:
                    raise Exception({'code': 500, 'msg': "对话创建失败"})
            ChatMapper.save_message(conversation_id, "user", message)
            print("conversation_id:", conversation_id)
            conversation = ChatMapper.get_conversation(conversation_id)

            conversation_info = conversation['conversation_info']
            model_config_id = conversation_info['model_config_id']
            history = conversation['history']["messages"]
            print("history:", history)
            model = FinetuningService.get_model(model_config_id)
            if isinstance(message, str):
                messages = [{"role": "user", "content": message}]
            print(message)
            response = chat_with_finetuned(model['model_path'], model['peft_model_path'], model['load_in_4bit'], messages[-1]['content'])
            res = ChatMapper.save_message(conversation_id, "assistant", response)
            return {
                "response": res,
                "conversation_id": conversation_id,
                "conversation_name": conversation_info['name']
            }
        except Exception as e:
            raise  e
    @staticmethod
    def base_chat(user_id: int, conversation_id, model_config_id, message) -> dict:
        """
        获取回答并保存
        :param model_config_id: 模型配置 id
        :param message: 消息
        :return:
        """
        try:
            if not conversation_id:
                if not model_config_id:
                    raise Exception({'code': 401, 'msg': "模型配置不存在"})
                conversation_id = ChatService.create_conversation(user_id, model_config_id, message, 2)
                if not conversation_id:
                    raise Exception({'code': 500, 'msg': "对话创建失败"})
            ChatMapper.save_message(conversation_id, "user", message)
            print("conversation_id:", conversation_id)
            conversation = ChatMapper.get_conversation(conversation_id)

            conversation_info = conversation['conversation_info']
            model_config_id = conversation_info['model_config_id']
            history = conversation['history']["messages"]
            print("history:", history)
            model = FinetuningService.get_model_base(model_config_id)
            print("model:", model)
            response = chat_with_base(model['model_path'], message)
            res = ChatMapper.save_message(conversation_id, "assistant", response)
            return {
                "response": res,
                "conversation_id": conversation_id,
                "conversation_name": conversation_info['name']
            }
        except Exception as e:
            raise  e

    @staticmethod
    def create_base(data):
        try:
            name = data.get('name')
            path = current_app.config['MODEL_DIR'] + '\\' + name
            describe = data.get('describe', '')
            type = data.get('type', 'chatllm')
            # 从HuggingFace下载模型
            robust_download_model(name, path)
            instance = FinetuningMapper.create(PreFinetuningModel, **{
                "name": name,
                "path": path,
                "describe": describe,
                "type": type
            })
            return instance
        except Exception as e:
            current_app.logger.error(f"创建基础模型失败: {str(e)}")
            raise  e
