from app.extensions import db
from sqlalchemy import Enum
from datetime import datetime

class FinetuningRecords(db.Model):
    __tablename__ = 'finetuning_records'
    # 自增主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 基础模型 ID，外键关联 pre_finetuning_model 表的 id 字段
    base_model_id = db.Column(db.Integer, db.ForeignKey('pre_finetuning_model.id'), nullable=False)
    # 配置 4-bit 量化，布尔类型
    load_in_4bit = db.Column(db.Boolean, nullable=False)
    # 启用 LoRA 微调，布尔类型
    use_lora = db.Column(db.Boolean, nullable=False)
    # LoRA 的 r 值
    lora_r = db.Column(db.Integer, nullable=True)
    # LoRA 的 alpha 值
    lora_alpha = db.Column(db.Float, nullable=True)
    # LoRA 的 dropout 值
    lora_dropout = db.Column(db.Float, nullable=True)
    # 梯度累积步数
    gradient_accumulation_steps = db.Column(db.Integer, nullable=True)
    # 训练轮数
    num_train_epochs = db.Column(db.Integer, nullable=True)
    # 日志记录间隔
    logging_steps = db.Column(db.Integer, nullable=True)
    # 保存策略，使用枚举类型
    save_strategy = db.Column(Enum('steps', 'epoch', 'no'), nullable=True)
    # fp16 配置，布尔类型
    fp16 = db.Column(db.Boolean, nullable=True)
    # 优化器
    optim = db.Column(db.String(255), nullable=True)
    # 输出目录
    output_dir = db.Column(db.Text, nullable=True)
    # 日志路径
    log_path = db.Column(db.Text, nullable=True)
    # 创建时间，默认为当前时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 关联 finetuning_model 表
    base_model = db.relationship('PreFinetuningModel', backref=db.backref('finetuning_records', lazy=True))

    def to_dict(self):
        created_at_str = self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        return {
            'id': self.id,
            'base_model_id': self.base_model_id,
            'load_in_4bit': self.load_in_4bit,
            'use_lora': self.use_lora,
            'lora_r': self.lora_r,
            'lora_alpha': self.lora_alpha,
            'lora_dropout': self.lora_dropout,
            'gradient_accumulation_steps': self.gradient_accumulation_steps,
            'num_train_epochs': self.num_train_epochs,
            'logging_steps': self.logging_steps,
            'save_strategy': self.save_strategy,
            'fp16': self.fp16,
            'optim': self.optim,
            'output_dir': self.output_dir,
            'log_path': self.log_path,
            'created_at': created_at_str
        }