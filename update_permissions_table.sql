-- 更新permissions表结构
-- 添加新的权限字段

-- 添加基础权限字段
ALTER TABLE permissions ADD COLUMN can_confirm BOOLEAN DEFAULT FALSE COMMENT '确认项目权限';
ALTER TABLE permissions ADD COLUMN can_execute BOOLEAN DEFAULT FALSE COMMENT '执行任务权限';
ALTER TABLE permissions ADD COLUMN can_manage BOOLEAN DEFAULT FALSE COMMENT '管理权限';
ALTER TABLE permissions ADD COLUMN can_view_all BOOLEAN DEFAULT FALSE COMMENT '查看所有项目权限';

-- 添加专业权限字段
ALTER TABLE permissions ADD COLUMN can_edit_paper BOOLEAN DEFAULT FALSE COMMENT '编辑论文项目权限';
ALTER TABLE permissions ADD COLUMN can_edit_patent BOOLEAN DEFAULT FALSE COMMENT '编辑专利项目权限';
ALTER TABLE permissions ADD COLUMN is_expert BOOLEAN DEFAULT FALSE COMMENT '专家权限';

-- 更新position枚举类型
ALTER TABLE permissions MODIFY COLUMN position ENUM('普通业务员', '项目执行者', '论文编辑', '专利编辑', '专家', '系统管理员') NOT NULL COMMENT '职务';

-- 删除现有权限记录
DELETE FROM permissions;

-- 插入新的权限记录
INSERT INTO permissions (position, can_confirm, can_execute, can_manage, can_view_all, can_edit_paper, can_edit_patent, is_expert, execute_permission, update_serial_permission) VALUES
('普通业务员', TRUE, FALSE, FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE),
('项目执行者', FALSE, TRUE, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE),
('论文编辑', TRUE, TRUE, FALSE, TRUE, TRUE, FALSE, TRUE, TRUE, FALSE),
('专利编辑', TRUE, TRUE, FALSE, TRUE, FALSE, TRUE, TRUE, TRUE, FALSE),
('专家', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE),
('系统管理员', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE);
