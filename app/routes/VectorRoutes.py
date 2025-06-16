from flask import Blueprint, request
from app.forms.base import ErrorResponse, SuccessResponse
from app.services.VectorService import VectorService
from app.utils.JwtUtil import login_required
from flask import Blueprint, request, jsonify  # 确保导入 jsonify

vector_bp = Blueprint('vector', __name__, url_prefix='/vector')

# 辅助函数：处理异常
def handle_exception(e, default_error_code=500):
    try:
        if isinstance(e, ValueError):
            return ErrorResponse(400, f"参数错误: {str(e)}").to_json()  # 确保调用 to_json()
        else:
            return ErrorResponse(default_error_code, f"服务器错误: {str(e)}").to_json()  # 确保调用 to_json()
    except Exception as e2:
        # 双重异常保护
        return jsonify({
            'code': 500,
            'message': f'严重错误: {str(e2)}',
            'data': None
        }), 500

@vector_bp.route('/create', methods=['POST'])
@login_required
def create_vector_db():
    data = request.form
    if not data or "name" not in data or "embedding_id" not in data:
        return ErrorResponse(400, "请求参数错误").to_json()

    # 处理 embedding_id
    embedding_id_str = data.get('embedding_id')
    try:
        embedding_id = int(embedding_id_str)
    except ValueError:
         return ErrorResponse(400, f"embedding_id 必须为有效的整数，当前传入的值为: {embedding_id_str}").to_json()


    # 处理 document_similarity
    document_similarity_str = data.get('document_similarity')
    if document_similarity_str:
        try:
            document_similarity = float(document_similarity_str)
        except ValueError:
            document_similarity = 0.7
    else:
        document_similarity = 0.7

    try:
        vector_db = VectorService.create_vector_db(
            user_id=request.user.id,
            name=data.get('name'),
            embedding_id=data.get('embedding_id'),
            describe=data.get('describe'),
            document_similarity=document_similarity
        )
        return SuccessResponse(
            "创建成功",
            vector_db.to_dict() if hasattr(vector_db, 'to_dict') else vector_db
        ).to_json()
    except Exception as e:
        return handle_exception(e)

@vector_bp.route('/get/<int:vector_db_id>', methods=['GET'])
@login_required
def get_vector_db(vector_db_id):
    try:
        vector_db = VectorService.get_vector_db(vector_db_id)
        if vector_db:
            return SuccessResponse(
                "查询成功",
                vector_db
            ).to_json()
        return ErrorResponse(404, "未找到该向量数据库").to_json()
    except Exception as e:
        return handle_exception(e)

@vector_bp.route('/update/<int:vector_db_id>', methods=['POST'])
@login_required
def update_vector_db(vector_db_id):
    data = request.form

    # 处理 document_similarity
    document_similarity_str = data.get('document_similarity')
    if document_similarity_str:
        try:
            document_similarity = float(document_similarity_str)
        except ValueError:
            document_similarity = 0.7
    else:
        document_similarity = 0.7

    try:
        vector_db = VectorService.update_vector_db(
            vector_db_id=vector_db_id,
            name=data.get('name'),
            embedding_id=data.get('embedding_id'),
            describe=data.get('describe'),
            document_similarity=document_similarity
        )
        if vector_db:
            return SuccessResponse(
                "更新成功",
                vector_db.to_dict() if hasattr(vector_db, 'to_dict') else vector_db
            ).to_json()
        return ErrorResponse(404, "未找到该向量数据库").to_json()
    except Exception as e:
        return handle_exception(e)

@vector_bp.route('/delete/<int:vector_db_id>', methods=['DELETE'])
@login_required
def delete_vector_db(vector_db_id):
    try:
        if VectorService.delete_vector_db(vector_db_id):
            return SuccessResponse("删除成功").to_json()
        return ErrorResponse(404, "未找到该向量数据库").to_json()
    except Exception as e:
        return handle_exception(e)

@vector_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return ErrorResponse(400, "未提供文件").to_json()

    file = request.files['file']
    if file.filename == '':
        return ErrorResponse(400, "未选择文件").to_json()

    vector_db_id = request.form.get('vector_db_id')
    if not vector_db_id:
        return ErrorResponse(400, "未提供向量数据库ID").to_json()

    try:
        VectorService.upload_file(vector_db_id, file)
        return SuccessResponse("文件上传成功").to_json()
    except Exception as e:
        return handle_exception(e)