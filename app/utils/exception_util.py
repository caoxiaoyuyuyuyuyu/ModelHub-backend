from app.forms.base import ErrorResponse


def error_500_print(prompt: str, e):
    # 打印错误信息便于调试
    print(f"{prompt}: {str(e)}")

    # 直接使用异常中的错误信息
    error_info = getattr(e, 'args', [{}])[0]
    code = error_info.get('code', 500)
    msg = error_info.get('msg', str(e))
    # 打印错误信息到控制台
    print(f"Error: {code} - {msg}")
    return ErrorResponse(code, msg).to_json()
