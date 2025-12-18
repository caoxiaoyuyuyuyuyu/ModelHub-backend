-- 添加 /vector/documents/<int:vector_db_id> 路由到数据库
-- 这个路由用于分页获取向量数据库的文档列表

-- 1. 插入路由（如果不存在）
INSERT INTO routes (path, name, component, method, created_at, updated_at)
SELECT 
    '/vector/documents/<int:vector_db_id>',
    '获取向量数据库文档列表（分页）',
    'VectorDbDetail',
    'GET',
    NOW(),
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM routes 
    WHERE path = '/vector/documents/<int:vector_db_id>' 
    AND method = 'GET'
);

-- 2. 获取路由ID
SET @route_id = (SELECT id FROM routes WHERE path = '/vector/documents/<int:vector_db_id>' AND method = 'GET' LIMIT 1);

-- 3. 为 admin 角色添加权限（直接插入，如果已存在则忽略）
INSERT INTO role_routes (role_id, route_id, created_at)
SELECT 
    (SELECT id FROM roles WHERE name = 'admin' LIMIT 1),
    @route_id,
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM role_routes 
    WHERE role_id = (SELECT id FROM roles WHERE name = 'admin' LIMIT 1)
    AND route_id = @route_id
);

-- 4. 为 user 角色添加权限（如果存在user角色）
INSERT INTO role_routes (role_id, route_id, created_at)
SELECT 
    (SELECT id FROM roles WHERE name = 'user' LIMIT 1),
    @route_id,
    NOW()
WHERE EXISTS (SELECT 1 FROM roles WHERE name = 'user')
AND NOT EXISTS (
    SELECT 1 FROM role_routes 
    WHERE role_id = (SELECT id FROM roles WHERE name = 'user' LIMIT 1)
    AND route_id = @route_id
);

