from app.utils.JwtUtil import generate_jwt
from app.config import Config

# 模拟用户信息
user_id = 1
user_name = "test_user"
user_email = "test@example.com"

# 生成 JWT Token
token = generate_jwt(user_id, user_name, user_email)

print(f"生成的 JWT Token: {token}")

# 验证 JWT Token（可选）
from app.utils.JwtUtil import verify_jwt
payload = verify_jwt(token)
if 'error' in payload:
    print(f"Token 验证失败: {payload['error']}")
else:
    print(f"Token 验证成功，有效载荷: {payload}")