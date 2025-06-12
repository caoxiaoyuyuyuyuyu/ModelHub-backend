from app.mapper import UserMapper
from app.utils import JwtUtil


class UserService:
    """用户服务类"""
    @staticmethod
    def register(name, email, password,describe=None):
        if UserMapper.get_user_by_email(email):
            raise Exception("邮箱已存在")
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
            raise