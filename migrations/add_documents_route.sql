-- 添加 /vector/documents/<int:vector_db_id> 路由到数据库
-- 这个路由用于分页获取向量数据库的文档列表

-- 插入路由（如果不存在）
INSERT IGNORE INTO routes (path, name, component, method, created_at, updated_at)
VALUES ('/vector/documents/<int:vector_db_id>', '获取向量数据库文档列表（分页）', 'VectorDbDetail', 'GET', NOW(), NOW());

-- 获取路由ID
SET @route_id = (SELECT id FROM routes WHERE path = '/vector/documents/<int:vector_db_id>' AND method = 'GET' LIMIT 1);

-- 为 admin 角色添加该路由权限（如果还没有）
INSERT IGNORE INTO role_routes (role_id, route_id, created_at)
SELECT r.id, @route_id, NOW()
FROM roles r
WHERE r.name = 'admin'
AND NOT EXISTS (
    SELECT 1 FROM role_routes rr 
    WHERE rr.role_id = r.id AND rr.route_id = @route_id
);

-- 为 user 角色添加该路由权限（如果还没有，如果存在user角色的话）
INSERT IGNORE INTO role_routes (role_id, route_id, created_at)
SELECT r.id, @route_id, NOW()
FROM roles r
WHERE r.name = 'user'
AND NOT EXISTS (
    SELECT 1 FROM role_routes rr 
    WHERE rr.role_id = r.id AND rr.route_id = @route_id
);

-- 如果上面的 INSERT IGNORE 不支持，使用以下替代方案：
-- 直接插入，忽略重复键错误
-- INSERT INTO role_routes (role_id, route_id, created_at)
-- SELECT r.id, @route_id, NOW()
-- FROM roles r
-- WHERE r.name = 'admin'
-- ON DUPLICATE KEY UPDATE created_at = created_at;

