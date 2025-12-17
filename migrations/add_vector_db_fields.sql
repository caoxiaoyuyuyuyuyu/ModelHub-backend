-- 添加向量数据库配置字段的 SQL 脚本
-- 如果使用 Flask-Migrate，可以忽略此文件

ALTER TABLE vector_db 
ADD COLUMN distance VARCHAR(20) DEFAULT 'cosine' NULL COMMENT '距离度量方式: cosine, l2, ip',
ADD COLUMN collection_metadata TEXT NULL COMMENT 'JSON格式的元数据',
ADD COLUMN chunk_size INT DEFAULT 1024 NULL COMMENT 'chunk大小',
ADD COLUMN chunk_overlap INT DEFAULT 200 NULL COMMENT 'chunk重叠',
ADD COLUMN topk INT DEFAULT 10 NULL COMMENT '检索时的top k';

