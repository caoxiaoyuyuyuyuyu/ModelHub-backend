# models.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Enum

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    describe = db.Column(db.String(255))
    create_at = db.Column(db.DateTime, nullable=False)
    update_at = db.Column(db.DateTime, nullable=False)

    # 关联模型 [[3]](https://zhuanlan.zhihu.com/p/684204406)
    model_configs = db.relationship('ModelConfig', backref='user')
    documents = db.relationship('Document', backref='user')
    vector_dbs = db.relationship('VectorDb', backref='user')
    conversations = db.relationship('Conversation', backref='user')

# 模型信息表模型 [[6]](https://helloflask.com/tutorial/database.html)
class ModelInfo(db.Model):
    __tablename__ = 'model_info'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model_name = db.Column(db.String(255), unique=True, nullable=False)
    base_url = db.Column(db.String(255), unique=True, nullable=False)
    api_key = db.Column(db.String(255), unique=True, nullable=False)
    describe = db.Column(db.String(255))
    create_at = db.Column(db.DateTime, nullable=False)
    update_at = db.Column(db.DateTime, nullable=False)

    # 关联模型
    model_configs = db.relationship('ModelConfig', backref='base_model')

# 模型配置表模型 [[8]](https://blog.csdn.net/weixin_43252548/article/details/136934332)
class ModelConfig(db.Model):
    __tablename__ = 'model_config'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    share_id = db.Column(db.String(255), unique=True, nullable=False)
    base_model_id = db.Column(db.Integer, db.ForeignKey('model_info.id'), nullable=False)
    temprature = db.Column(db.DECIMAL(10,2), nullable=False)
    top_p = db.Column(db.DECIMAL(10,2), nullable=False)
    prompt = db.Column(db.Text)
    vector_db_id = db.Column(db.Integer, db.ForeignKey('vector_db.id'), nullable=False)
    create_at = db.Column(db.DateTime, nullable=False)
    update_at = db.Column(db.DateTime, nullable=False)

# 向量数据库表模型
class VectorDb(db.Model):
    __tablename__ = 'vector_db'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(255), unique=True, nullable=False)
    document_similarity = db.Column(db.DECIMAL(5,2))
    describe = db.Column(db.String(255))
    create_at = db.Column(db.DateTime, nullable=False)
    update_at = db.Column(db.DateTime, nullable=False)

    # 关联模型
    documents = db.relationship('Document', backref='vector_db')
    model_configs = db.relationship('ModelConfig', backref='vector_db')

# 文档表模型 [[4]](https://blog.csdn.net/m0_64346565/article/details/128473201)
class Document(db.Model):
    __tablename__ = 'document'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vector_db_id = db.Column(db.Integer, db.ForeignKey('vector_db.id'), nullable=False)
    name = db.Column(db.String(255), unique=True, nullable=False)
    original_name = db.Column(db.String(255), unique=True, nullable=False)
    type = db.Column(db.String(64), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    save_path = db.Column(db.Text, nullable=False)
    describe = db.Column(db.String(255))
    upload_at = db.Column(db.DateTime, nullable=False)

# 会话表模型
class Conversation(db.Model):
    __tablename__ = 'conversation'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(255))
    model_config_id = db.Column(db.Integer, db.ForeignKey('model_config.id'), nullable=False)
    chat_history = db.Column(db.Integer)
    create_at = db.Column(db.DateTime, nullable=False)
    update_at = db.Column(db.DateTime, nullable=False)

    # 关联模型
    messages = db.relationship('Message', backref='conversation')

# 消息表模型 [[1]](https://zhuanlan.zhihu.com/p/575434515)
class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    role = db.Column(Enum('user', 'assistant', 'system'), nullable=False)
    content = db.Column(db.Text)
    create_at = db.Column(db.DateTime, nullable=False)