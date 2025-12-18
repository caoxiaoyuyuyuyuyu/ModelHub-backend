# ModelHub-backend/app/routes/VectorRoutes.py
import os

from flask import Blueprint, request, current_app, send_file, send_from_directory
from app.forms.base import ErrorResponse, SuccessResponse
from app.services.VectorService import VectorService
from app.utils.JwtUtil import login_required
from flask import jsonify  # 确保导入 jsonify
from app.models import Document
import asyncio  # 新增导入

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
    data = request.get_json()
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

    # 处理新字段
    distance = data.get('distance', 'cosine')
    metadata = data.get('metadata')
    chunk_size = data.get('chunk_size', 1024)
    chunk_overlap = data.get('chunk_overlap', 200)
    topk = data.get('topk', 10)
    
    # 类型转换
    try:
        chunk_size = int(chunk_size) if chunk_size else 1024
    except (ValueError, TypeError):
        chunk_size = 1024
    try:
        chunk_overlap = int(chunk_overlap) if chunk_overlap else 200
    except (ValueError, TypeError):
        chunk_overlap = 200
    try:
        topk = int(topk) if topk else 10
    except (ValueError, TypeError):
        topk = 10

    try:
        # 异步操作需要在事件循环中运行
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        vector_db = loop.run_until_complete(VectorService.create_vector_db(
            user_id=request.user.id,
            name=data.get('name'),
            embedding_id=embedding_id,
            describe=data.get('describe'),
            document_similarity=document_similarity,
            distance=distance,
            metadata=metadata,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            topk=topk
        ))
        loop.close()

        if vector_db:
            return SuccessResponse(
                "创建成功",
                vector_db.to_dict() if hasattr(vector_db, 'to_dict') else vector_db
            ).to_json()
        else:
            return ErrorResponse(500, "创建向量数据库失败").to_json()
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
    data = request.get_json()
    # 处理 document_similarity
    document_similarity_str = data.get('document_similarity')
    if document_similarity_str:
        try:
            document_similarity = float(document_similarity_str)
        except ValueError:
            document_similarity = None
    else:
        document_similarity = None

    # 处理新字段
    distance = data.get('distance')
    metadata = data.get('metadata')
    chunk_size = data.get('chunk_size')
    chunk_overlap = data.get('chunk_overlap')
    topk = data.get('topk')
    
    # 类型转换
    if chunk_size is not None:
        try:
            chunk_size = int(chunk_size)
        except (ValueError, TypeError):
            chunk_size = None
    if chunk_overlap is not None:
        try:
            chunk_overlap = int(chunk_overlap)
        except (ValueError, TypeError):
            chunk_overlap = None
    if topk is not None:
        try:
            topk = int(topk)
        except (ValueError, TypeError):
            topk = None

    try:
        vector_db = VectorService.update_vector_db(
            vector_db_id=vector_db_id,
            name=data.get('name'),
            embedding_id=data.get('embedding_id'),
            describe=data.get('describe'),
            document_similarity=document_similarity,
            distance=distance,
            metadata=metadata,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            topk=topk
        )
        if vector_db:
            if isinstance(vector_db, dict):
                return SuccessResponse(
                    "更新成功",
                    vector_db
                ).to_json()
            elif hasattr(vector_db, 'to_dict'):
                return SuccessResponse(
                    "更新成功",
                    vector_db.to_dict()
                ).to_json()
            else:
                return ErrorResponse(500, "返回对象格式错误").to_json()
        return ErrorResponse(404, "未找到该向量数据库").to_json()
    except Exception as e:
        return handle_exception(e)

@vector_bp.route('/delete/<int:vector_db_id>', methods=['DELETE'])
@login_required
def delete_vector_db(vector_db_id):
    try:
        documents = Document.query.filter_by(vector_db_id=vector_db_id).all()
        for document in documents:
            VectorService.delete_file(document.id)
        if VectorService.delete_vector_db(vector_db_id):
            return SuccessResponse("删除成功").to_json()
        return ErrorResponse(404, "未找到该向量数据库").to_json()
    except Exception as e:
        return handle_exception(e)

@vector_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    print("Request headers:", request.headers)  # 打印请求头
    print("Request form data:", request.form)  # 打印表单数据
    print("Request files:", request.files)  # 打印文件数据
    
    # 支持 'file' 和 'files' 两种字段名（兼容单数和复数）
    files = []
    if 'file' in request.files:
        files = request.files.getlist('file')
    elif 'files' in request.files:
        files = request.files.getlist('files')
    
    if not files or all(file.filename == '' for file in files):
        return ErrorResponse(400, "未提供文件或未选择文件").to_json()

    describe = request.form.get('describe', '').strip() or None  # 允许为空，空字符串转为None

    vector_db_id = request.form.get('vector_db_id')
    if not vector_db_id:
        return ErrorResponse(400, "未提供向量数据库ID").to_json()

    document_ids = []
    try:
        # 串行处理文件，一个接一个
        for file in files:
            # 传递当前登录用户ID
            document_id = VectorService.upload_file(
                vector_db_id=vector_db_id,
                file=file,
                user_id=request.user.id,  # 添加用户ID
                describe=describe
            )
            if document_id:
                document_ids.append(document_id)
        return SuccessResponse("文件上传成功", data={"document_ids": document_ids}).to_json()
    except Exception as e:
        return handle_exception(e)

@vector_bp.route('/delete_file/<int:document_id>', methods=['DELETE'])
@login_required
def delete_file(document_id):
    try:
        if VectorService.delete_file(document_id):
            return SuccessResponse("文件删除成功").to_json()
        return ErrorResponse(404, "未找到该文件").to_json()
    except Exception as e:
        return handle_exception(e)

@vector_bp.route('/list', methods=['GET'])
@login_required
def get_user_vector_db_list():
    try:
        user_id = request.user.id
        vector_db_list = VectorService.get_user_vector_dbs(user_id)
        return SuccessResponse(
            "查询成功",
            vector_db_list
        ).to_json()
    except Exception as e:
        return handle_exception(e)

@vector_bp.route('/document/<int:document_id>', methods=['GET'])
@login_required
def get_document(document_id):
    try:
        document = Document.query.get(document_id)
        if document:
            return SuccessResponse(
                "查询成功",
                document.to_dict()
            ).to_json()
        return ErrorResponse(404, "未找到该文件").to_json()
    except Exception as e:
        return handle_exception(e)

@vector_bp.route('/documents/<int:vector_db_id>', methods=['GET'])
@login_required
def get_documents(vector_db_id):
    """获取向量数据库的文档列表（分页）"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 验证参数
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20
        
        result = VectorService.get_documents_paginated(vector_db_id, page, page_size)
        if result:
            return SuccessResponse(
                "查询成功",
                result
            ).to_json()
        return ErrorResponse(404, "未找到该向量数据库").to_json()
    except Exception as e:
        return handle_exception(e)

@vector_bp.route('/connect/<int:vector_id>', methods=['GET'])
@login_required
def connect_vector(vector_id):
    try:
        VectorService.ensure_collection_exists(vector_id)
        return SuccessResponse("连接成功").to_json()
    except Exception as e:
        return handle_exception(e)

@vector_bp.route('/query/<int:vector_id>', methods=['POST'])
@login_required
def query_vectors(vector_id):
    result = VectorService.query_vectors(vector_id, request.json.get('query_text'), request.json.get('n_results', 10))
    return SuccessResponse("查询成功", data=result).to_json()


from werkzeug.utils import safe_join
from urllib.parse import quote


@vector_bp.route('/download_file/<int:document_id>', methods=['GET'])
@login_required
def download_file(document_id):
    try:
        # 临时存储模式下，文件在处理完成后已被删除
        # 获取完整文件路径和原始文件名
        file_path, original_name = VectorService.get_document_file(document_id)

        if not file_path or not original_name:
            return ErrorResponse(404, "文件不存在（临时存储模式：文件在处理完成后已删除，仅保留向量数据）").to_json()

        # 对文件名进行URL编码（处理中文等特殊字符）
        safe_filename = quote(original_name)

        # 使用send_file发送文件
        response = send_file(
            file_path,
            as_attachment=True,
            download_name=original_name,  # 原始文件名
            conditional=True
        )

        # 设置Content-Disposition头部（关键修复）
        response.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{safe_filename}"

        return response
    except Exception as e:
        return handle_exception(e)