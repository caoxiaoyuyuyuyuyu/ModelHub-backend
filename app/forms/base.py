from typing import Any

from flask import jsonify


class BaseResponse:
    def __init__(self, code: int = 200, message: str = 'success', data: Any = None):
        self.code = code
        self.message = message
        self.data = data

    def to_json(self):
        return jsonify({
            'code': self.code,
            'message': self.message,
            'data': self.data
        })

class SuccessResponse(BaseResponse):
    def __init__(self, message: str = 'success',data: Any = None):
        super().__init__(data=data)

class ErrorResponse(BaseResponse):
    def __init__(self, code, message):
        super().__init__(code, message)