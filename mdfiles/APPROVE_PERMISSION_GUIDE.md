# 立项权限控制说明文档

## 修改概述

根据用户需求，将立项权限从普通业务员中分离，实现更细粒度的权限控制：
- **普通业务员**：只能确认申请，不能立项
- **有立项权限的人员**（如主管、管理员）：可以确认申请并立项
- **项目执行者**：接受已立项的项目并执行

## 业务流程变更

### 原流程
```
用户申请 → 业务员确认 → 业务员立项（自动成为执行者） → 执行中
```

### 新流程
```
用户申请 → 业务员确认 → 有权限人员立项 → 执行者接受 → 执行中
       (待确认)     (已确认)        (已立项)      (执行中)
```

## 主要变更

### 1. 数据库模型变更 (`database/models.py`)

#### Permission 模型新增字段
```python
can_approve = db.Column(db.Boolean, default=False, comment='立项权限（项目立项，指定执行者）')
```

**权限说明**：
- `can_confirm`: 确认项目权限（业务员基础权限）
- `can_approve`: 立项权限（高级业务权限，如主管）
- `can_execute`: 执行任务权限（执行者权限）

### 2. 后端逻辑变更 (`web_app/views/staff.py`)

#### approve_project 函数重构

**原逻辑问题**：
1. 任何业务员都可以立项
2. 立项时自动成为执行者
3. 错误地设置了 `settle_time` 而非执行时间

**新逻辑**：
```python
@staff_bp.route('/project/<int:project_id>/approve', methods=['POST'])
def approve_project(project_id):
    # 1. 检查是否为员工
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    # 2. 检查立项权限（新增）
    if not (hasattr(current_user, 'position') and current_user.position 
            and current_user.position.can_approve):
        return jsonify({'success': False, 'message': '您没有立项权限，请联系主管'})
    
    # 3. 检查是否为项目确认者
    if project.confirmer_id != current_user.id:
        return jsonify({'success': False, 'message': '您不是该项目的确认者，无权立项'})
    
    # 4. 立项（不设置执行者）
    project.status = '已立项'
    # project.executor_id 保持为 None，等待执行者接受
```

**关键变化**：
- ✅ 添加 `can_approve` 权限检查
- ✅ 确认者和立项者一致性检查
- ✅ 不再自动设置执行者
- ✅ 移除错误的 `settle_time` 设置

#### take_project 函数（保持不变）

执行者通过此函数接受已立项的项目：
```python
@staff_bp.route('/project/<int:project_id>/take', methods=['POST'])
def take_project(project_id):
    # 1. 检查是否为项目执行者角色
    if not (hasattr(current_user, 'position') and current_user.position 
            and current_user.position.position == '项目执行者'):
        return jsonify({'success': False, 'message': '您不是项目执行者'})
    
    # 2. 检查项目状态
    if project.status != '已立项' or project.executor_id is not None:
        return jsonify({'success': False, 'message': '项目状态不允许此操作'})
    
    # 3. 接受项目
    project.executor_id = current_user.id
    project.execute_time = datetime.utcnow()
    project.status = '执行中'
```

### 3. 前端界面变更

#### 项目详情页 (`templates/staff/project_detail.html`)

**立项按钮权限控制**：
```jinja2
{% if project.status == '已确认' 
      and project.confirmer_id == current_user.id 
      and current_user.position is defined 
      and current_user.position 
      and current_user.position.can_approve %}
    <button class="btn btn-info w-100 mb-2" onclick="approveProject(PROJECT_ID)">
        <i class="fas fa-arrow-right"></i> 项目立项
    </button>
{% endif %}
```

**接受项目按钮**（保持不变）：
```jinja2
{% if project.status == '已立项' 
      and not project.executor_id 
      and current_user.position is defined 
      and current_user.position 
      and current_user.position.position == '项目执行者' %}
    <button class="btn btn-warning w-100 mb-2" onclick="takeProject(PROJECT_ID)">
        <i class="fas fa-hand-paper"></i> 接受项目
    </button>
{% endif %}
```

#### 业务员仪表板 (`templates/staff/business_dashboard.html`)

在项目列表中的立项按钮也添加了相同的权限检查。

## 数据迁移

### 迁移脚本：`migrate_approve_permission.py`

```bash
python migrate_approve_permission.py
```

**脚本功能**：
1. 添加 `can_approve` 字段到 `permissions` 表
2. 根据职位设置默认权限：
   - ✅ **系统管理员**：拥有立项权限
   - ❌ **普通业务员**：无立项权限（仅能确认项目）
   - ❌ **项目执行者**：无立项权限（专注执行）
   - ❌ **其他角色**：默认无立项权限

### 手动授权

如需为特定业务员授予立项权限：

```sql
-- 查看当前权限
SELECT * FROM permissions;

-- 为特定权限记录授予立项权限
UPDATE permissions 
SET can_approve = TRUE 
WHERE id = <权限ID>;

-- 或为某个职位的所有人授权（谨慎使用）
UPDATE permissions 
SET can_approve = TRUE 
WHERE position = '普通业务员';
```

## 权限矩阵

| 角色 | 确认申请<br>(can_confirm) | 立项<br>(can_approve) | 执行任务<br>(can_execute) | 备注 |
|------|:---:|:---:|:---:|------|
| 系统管理员 | ✅ | ✅ | ✅ | 拥有所有权限 |
| 普通业务员 | ✅ | ❌ | ❌ | 只能确认申请 |
| 项目执行者 | ❌ | ❌ | ✅ | 专注执行 |
| 论文编辑 | ❌ | ❌ | ✅ | 论文项目 |
| 专利编辑 | ❌ | ❌ | ✅ | 专利项目 |
| 专家 | ❌ | ❌ | ❌ | 顾问角色 |

## 使用场景

### 场景1：普通业务员确认项目

```
1. 用户提交申请 → 待确认
2. 普通业务员审核并确认 → 已确认
3. 普通业务员看不到"立项"按钮
4. 需要通知主管或管理员进行立项
```

### 场景2：主管立项

```
1. 主管登录系统
2. 查看已确认的项目
3. 点击"项目立项"按钮
4. 项目状态变为"已立项"，等待执行者接受
```

### 场景3：执行者接受项目

```
1. 执行者查看"可接受项目"列表
2. 选择合适的项目
3. 点击"接受项目"按钮
4. 成为该项目的执行者，项目状态变为"执行中"
```

### 场景4：一人身兼多职

如果某人同时是业务员和主管：
```
1. 作为业务员：确认申请
2. 作为主管：立项（如果有 can_approve 权限）
3. 项目流转到执行队列
```

## 权限设置建议

### 小型团队（5人以下）

```
- 1-2名系统管理员（全权限）
- 所有员工都是业务员兼执行者
- 管理员负责立项分配
```

### 中型团队（5-20人）

```
- 1名系统管理员
- 1-2名业务主管（can_confirm + can_approve）
- 3-5名普通业务员（can_confirm）
- 5-10名执行者（can_execute）
```

### 大型团队（20人以上）

```
- 1名系统管理员
- 多名部门主管（各自部门的 can_approve）
- 多名普通业务员（分组管理）
- 专门的执行团队
- 分工明确，权责清晰
```

## 测试检查清单

### 功能测试

- [ ] 普通业务员不能看到"立项"按钮
- [ ] 普通业务员尝试立项被拒绝（API测试）
- [ ] 有权限的人员能看到"立项"按钮
- [ ] 有权限的人员能成功立项
- [ ] 立项后执行者字段为空
- [ ] 执行者能看到"可接受项目"列表
- [ ] 执行者能成功接受项目
- [ ] 接受后项目状态变为"执行中"
- [ ] 接受后执行者被正确设置

### 权限测试

- [ ] 系统管理员拥有立项权限
- [ ] 普通业务员没有立项权限
- [ ] 项目执行者没有立项权限
- [ ] 非确认者无法立项他人确认的项目
- [ ] 权限检查在前端和后端都生效

### 界面测试

- [ ] 项目详情页按钮显示正确
- [ ] 业务员仪表板按钮显示正确
- [ ] 错误提示信息友好清晰
- [ ] 立项成功后提示正确

## 常见问题

### Q1: 为什么要分离确认和立项权限？

**A:** 
- **确认**是基础审核，确保申请信息完整准确
- **立项**是重要决策，涉及资源分配和项目优先级
- 分离权限可以实现更好的管理层级和责任划分

### Q2: 普通业务员确认后如何通知主管立项？

**A:** 可以通过以下方式：
1. 系统内消息通知
2. 邮件提醒
3. 定期查看"已确认待立项"列表
4. 实施内部流程规范

### Q3: 执行者如何知道有新项目可接受？

**A:** 
- 查看"可接受项目"页面
- 系统可以发送通知（待实现）
- 定期检查执行者仪表板

### Q4: 如果需要立项时直接指定执行者怎么办？

**A:** 当前实现是执行者自主接受模式。如需指定执行者：
1. 修改立项接口，添加 `executor_id` 参数
2. 前端添加执行者选择下拉框
3. 立项时直接设置执行者
4. 跳过"接受"步骤，直接进入"执行中"

### Q5: 能否让业务员既能确认又能立项？

**A:** 可以！为该业务员的权限记录设置：
```sql
UPDATE permissions 
SET can_confirm = TRUE, can_approve = TRUE 
WHERE id = <该业务员的权限ID>;
```

## 后续优化建议

1. **职位细分**
   - 增加"业务主管"职位
   - 增加"项目经理"职位
   - 更细粒度的角色划分

2. **通知机制**
   - 立项后通知执行者团队
   - 长时间未接受的项目预警
   - 权限不足时的友好提示

3. **项目分配策略**
   - 自动分配算法
   - 负载均衡
   - 技能匹配

4. **审批流程**
   - 多级审批
   - 审批记录
   - 审批意见

5. **权限管理界面**
   - 可视化权限配置
   - 批量授权
   - 权限模板

## 影响范围

### 修改的文件
- `database/models.py` - 添加 can_approve 字段
- `web_app/views/staff.py` - 修改立项逻辑
- `templates/staff/project_detail.html` - 添加权限检查
- `templates/staff/business_dashboard.html` - 添加权限检查

### 新增的文件
- `migrate_approve_permission.py` - 权限迁移脚本
- `APPROVE_PERMISSION_GUIDE.md` - 本文档

### 不兼容变更
- 普通业务员无法再进行立项操作
- 需要重新分配立项权限
- 可能需要调整现有工作流程

## 回滚方案

如需回滚此功能：

```sql
-- 为所有业务员授予立项权限
UPDATE permissions 
SET can_approve = TRUE 
WHERE position IN ('普通业务员', '系统管理员');

-- 或直接删除权限检查（不推荐）
-- 在代码中移除 can_approve 检查即可
```

