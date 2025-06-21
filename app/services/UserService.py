from app.mapper import UserMapper, ModelMapper, VectorMapper
from app.services import ModelService
from app.services.VectorService import VectorService
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
                "avatar": user.avatar,
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
                "avatar": user.avatar,
                "email": user.email,
                "token": token
            }
        else:
            raise Exception({'code': 401, 'msg': "密码错误"})

    @staticmethod
    def get_user_by_email(user_email):
        user = UserMapper.get_user_info(user_email)
        if not user:
            raise Exception({'code': 404, 'msg': "用户不存在"})
        user_id = user.id

        model_configs = ModelService.get_user_config(user)

        vector_dbs = VectorService.get_user_vector_dbs(user_id)
        vector_dbs_with_docs = [VectorService.get_vector_db(vector_db['id']) for vector_db in vector_dbs]

        return {
            "user_info": user.to_dict(),
            "model_configs": model_configs,
            "vector_dbs": vector_dbs_with_docs
        }


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

    @staticmethod
    def update_avatar(user_id, avatar):
        try:
            user = UserMapper.get_user_by_id(user_id)
            if not user:
                raise Exception({'code': 404, 'msg': "用户不存在"})
            user.avatar = avatar
            UserMapper.update_user(user)
            return user.avatar
        except Exception as e:
            raise e