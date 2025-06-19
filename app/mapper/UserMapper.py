# app/mapper/UserMapper.py
from app.models.user import User
from sqlalchemy.orm import Session

from app.utils.PasswordUtil import get_password_hash  # 从新模块导入
from app.extensions import db

class UserMapper:
    @staticmethod
    def get_user_by_id(id: int):
        return User.query.get(id)

    @staticmethod
    def create_user(name: str, email: str, password: str, describe: str | None):
        try:
            # Check if email already exists
            if UserMapper.get_user_by_email(email):
                raise ValueError("Email already exists")

            user = User(name=name, email=email, password=get_password_hash(password), describe=describe)
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)
            return user
        except ValueError as ve:
            db.session.rollback()
            raise ve  # Re-raise validation errors
        except Exception as e:
            db.session.rollback()
            raise Exception(f"创建用户失败: {str(e)}")

    @staticmethod
    def update_user_by_id(id: int, name: str | None, email: str | None, password: str | None, describe: str | None):
        try:
            user = UserMapper.get_user_by_id(id)
            if name:
                user.name = name
            if email:
                user.email = email
            if password:
                user.password = password
            if describe:
                user.describe = describe
            db.commit()
            db.refresh(user)
            return user
        except:
            db.rollback()
            raise Exception("更新用户失败")

    @staticmethod
    def get_user_by_email(email):
        user = User.query.filter_by(email=email).first()
        return user if user else None