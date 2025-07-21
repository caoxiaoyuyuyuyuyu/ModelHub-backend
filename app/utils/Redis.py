import redis

class ConversationStore:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        """初始化Redis连接"""
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True  # 自动解码字节数据为字符串
        )

    def get_redis_client(self):
        return self.redis_client

