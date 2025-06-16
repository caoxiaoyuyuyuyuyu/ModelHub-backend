from app.mapper import UserMapper
from app.utils import JwtUtil


class UserService:
    """用户服务类"""
    @staticmethod
    def register(name, email, password,describe=None):
        if UserMapper.get_user_by_email(email):
            raise Exception({'code': 401, 'msg': "邮箱已存在"})
        try:
            user = UserMapper.create_user(name, email, password,describe)
            token = JwtUtil.generate_jwt(user.id, user.name, user.email)
            return {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "token": token
            }
        except Exception as e:
            raise Exception({'code': 500, 'msg': "注册失败"+str(e)})

    @staticmethod
    def login(email, password):
        user = UserMapper.get_user_by_email(email)
        if not user:
            raise Exception({'code': 404, 'msg': "用户不存在"})
        if JwtUtil.authenticate_user(user, email, password):
            token = JwtUtil.generate_jwt(user.id, user.name, user.email)
            return {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "token": token
            }
        else:
            raise Exception({'code': 401, 'msg': "密码错误"})

    @staticmethod
    def get_user_by_email(user_email):
        return UserMapper.get_user_by_email(user_email)

    @staticmethod
    def get_enterprise_users():
        try:
            users = UserMapper.get_enterprise_users()
            return [{
                "id": user.id,
                "name": user.name,
            } for user in users]
        except Exception as e:
            raise e

