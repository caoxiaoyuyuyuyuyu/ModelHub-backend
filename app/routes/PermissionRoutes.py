from flask import Blueprint, jsonify, request, current_app
from werkzeug.exceptions import BadRequest, NotFound

from app.models.permission import Role, Permission, Route, RolePermission, RoleRoute
from app.extensions import db
from app.utils.JwtUtil import login_required

permission_bp = Blueprint('permission', __name__, url_prefix='/permission')

@permission_bp.route('/roles', methods=['GET'])
def get_roles():
    roles = Role.query.all()
    return jsonify([{
        'id': role.id,
        'name': role.name,
        'description': role.description,
        'permissions': [p.code for p in role.permissions],
    } for role in roles])


@permission_bp.route('/roles/<int:role_id>', methods=['PUT'])
def update_role_permissions(role_id):
    """
    更新角色权限
    :param role_id: 角色ID
    :body { permission_codes: [str] } 权限代码列表
    :return: 更新后的角色信息
    """
    try:
        # 1. 获取请求数据
        data = request.get_json()
        if not data or 'permissions' not in data:
            raise BadRequest("缺少权限数据")

        permission_codes = data['permissions']
        if not isinstance(permission_codes, list):
            raise BadRequest("权限数据格式不正确")

        # 2. 验证角色是否存在
        role = Role.query.get(role_id)
        if not role:
            raise NotFound("角色不存在")

        # 3. 验证权限是否存在并获取权限对象
        permissions = Permission.query.filter(
            Permission.code.in_(permission_codes)
        ).all()

        # 检查请求的权限是否都有效
        if len(permissions) != len(permission_codes):
            found_codes = {p.code for p in permissions}
            missing = set(permission_codes) - found_codes
            raise BadRequest(f"以下权限不存在: {', '.join(missing)}")

        # 4. 开始事务
        db.session.begin_nested()

        # 5. 删除现有权限关联
        RolePermission.query.filter_by(role_id=role_id).delete()

        # 6. 添加新的权限关联
        for permission in permissions:
            role_permission = RolePermission(
                role_id=role_id,
                permission_id=permission.id
            )
            db.session.add(role_permission)

        # 7. 提交事务
        db.session.commit()

        # 8. 返回更新后的角色信息
        role_permissions = [p.code for p in role.permissions]

        return jsonify({
            "success": True,
            "message": "角色权限更新成功",
            "data": {
                "role_id": role.id,
                "role_name": role.name,
                "permissions": role_permissions
            }
        })

    except BadRequest as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except NotFound as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "服务器错误",
            "error": str(e)
        }), 500
@permission_bp.route('', methods=['GET'])
def get_permissions():
    permissions = Permission.query.all()
    return jsonify([{
        'id': p.id,
        'code': p.code,
        'name': p.name,
        'description': p.description
    } for p in permissions])


@permission_bp.route('/routes', methods=['GET'])
def get_routes():
    """
    Get all routes in hierarchical structure
    ---
    tags:
      - Permission
    responses:
      200:
        description: Returns hierarchical route structure
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Route'
      500:
        description: Internal server error
    """
    try:
        # Get all routes from database
        all_routes = Route.query.order_by(Route.path).all()

        # Build hierarchical structure
        def build_tree(routes, parent_id=None):
            tree = []
            for route in routes:
                if route.parent_id == parent_id:
                    route_data = {
                        'id': route.id,
                        'path': route.path,
                        'name': route.name,
                        'component': route.component,
                        'method': route.method,
                        'meta': route.meta or {},
                        'children': build_tree(routes, route.id)
                    }
                    tree.append(route_data)
            return tree

        # Get flat list of route permissions
        route_permissions = db.session.query(
            RoleRoute.route_id,
            Role.name
        ).join(Role).all()

        # Convert to dictionary {route_id: [role_names]}
        permissions_dict = {}
        for route_id, role_name in route_permissions:
            if route_id not in permissions_dict:
                permissions_dict[route_id] = []
            permissions_dict[route_id].append(role_name)

        # Build final response with permissions
        def add_permissions(routes_tree):
            for route in routes_tree:
                route['roles'] = permissions_dict.get(route['id'], [])
                if route['children']:
                    add_permissions(route['children'])
            return routes_tree

        routes_tree = add_permissions(build_tree(all_routes))

        return jsonify({
            'code': 200,
            'message': 'Success',
            'data': routes_tree
        })

    except Exception as e:
        current_app.logger.error(f"Failed to get routes: {str(e)}")
        return jsonify({
            'code': 500,
            'message': 'Failed to get routes',
            'error': str(e)
        }), 500

@permission_bp.route('/routes/<int:route_id>', methods=['PUT'])
def update_route_permissions(route_id):
    """
    更新路由权限
    :param route_id: 路由ID
    :body { roles: [str] } 角色名称列表
    :return: 更新后的路由信息
    """
    try:
        # 1. 获取请求数据
        data = request.get_json()
        if not data or 'roles' not in data:
            raise BadRequest("缺少角色数据")

        role_names = data['roles']
        if not isinstance(role_names, list):
            raise BadRequest("角色数据格式不正确")

        # 2. 验证路由是否存在
        route = Route.query.get(route_id)
        if not route:
            raise NotFound("路由不存在")

        # 3. 验证角色是否存在并获取角色对象
        roles = Role.query.filter(
            Role.name.in_(role_names)
        ).all()

        # 检查请求的角色是否都有效
        if len(roles) != len(role_names):
            found_names = {r.name for r in roles}
            missing = set(role_names) - found_names
            raise BadRequest(f"以下角色不存在: {', '.join(missing)}")

        # 4. 开始事务
        db.session.begin_nested()

        # 5. 删除现有角色关联
        RoleRoute.query.filter_by(route_id=route_id).delete()

        # 6. 添加新的角色关联
        for role in roles:
            role_route = RoleRoute(
                route_id=route_id,
                role_id=role.id
            )
            db.session.add(role_route)

        # 7. 提交事务
        db.session.commit()

        # 8. 返回更新后的路由信息
        route_roles = [r.name for r in route.roles]

        return jsonify({
            "success": True,
            "message": "路由权限更新成功",
            "data": {
                "route_id": route.id,
                "route_path": route.path,
                "roles": route_roles
            }
        })

    except BadRequest as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except NotFound as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to update route permissions: {str(e)}")
        return jsonify({
            "success": False,
            "message": "服务器错误",
            "error": str(e)
        }), 500

# 检查权限
@permission_bp.route('/check', methods=['POST'])
@login_required
def check_permission():
    """
    检查当前用户是否具有指定权限
    """
    data = request.get_json()
    code = data['permission']
    permission_id = Permission.query.filter_by(code=code).first().id
    user = request.user
    role_id = user.type
    if not [permission_id, role_id]:
        return jsonify(
            {
                "success": False,
                "message": "权限验证失败",
            }
        )
    print(permission_id,role_id)
    if not RolePermission.query.filter_by(permission_id=permission_id, role_id=role_id).first():
        return jsonify(
            {
                "success": False,
                "message": "权限验证失败",
            }
        )
    return jsonify(
        {
            "success": True,
            "message": "权限验证成功",
        }
    )