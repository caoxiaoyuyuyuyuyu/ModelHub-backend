-- 修改 document 表的 save_path 字段为可空
-- 支持临时存储模式：文件处理完成后会被删除，save_path 可以为空

ALTER TABLE document 
MODIFY COLUMN save_path TEXT NULL COMMENT '文件保存路径（临时存储模式下，文件处理完成后会被删除，此字段可为空）';

