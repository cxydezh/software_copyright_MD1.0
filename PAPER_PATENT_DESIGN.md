# 论文指导和专利申请功能设计文档

## 1. 项目概述

### 1.1 背景
基于现有的软件著作权管理系统，扩展"论文指导和发表"以及"专利申请和保护"两大业务模块，为郑州医企创医疗科技有限公司提供更全面的知识产权服务。

### 1.2 设计目标
- 建立统一的业务管理平台，支持软件著作权、论文指导、专利申请三大业务
- 提供标准化的业务流程和状态管理
- 实现客户、业务员、执行者的协同工作
- 支持文件管理和进度跟踪

## 2. 功能需求分析

### 2.1 论文指导和发表模块

#### 2.1.1 业务类型
1. **论文指导服务**
   - 学术论文写作指导
   - 期刊投稿指导
   - 论文修改润色
   - 学术规范培训

2. **论文发表服务**
   - 期刊推荐与匹配
   - 投稿流程管理
   - 审稿意见处理
   - 发表状态跟踪

3. **学术咨询服务**
   - 研究方向规划
   - 学术会议推荐
   - 学术合作对接
   - 成果转化指导

#### 2.1.2 申请人类型
- **个人学者**：高校教师、研究人员、博士生
- **医疗机构**：医院、医学研究所、医学院
- **企业研发**：医疗设备公司、制药企业研发部门
- **联合申请**：多机构合作项目

#### 2.1.3 服务等级
- **基础服务**：论文格式规范、投稿指导
- **标准服务**：内容修改、期刊推荐、全程跟踪
- **高级服务**：深度指导、专家审稿、快速发表

### 2.2 专利申请和保护模块

#### 2.2.1 业务类型
1. **专利申请服务**
   - 发明专利代理
   - 实用新型专利代理
   - 外观设计专利代理
   - 国际专利申请（PCT）

2. **专利管理服务**
   - 专利年费管理
   - 专利转化
   - 专利价值评估
   - 专利组合优化

#### 2.2.2 申请人类型
- **个人发明者**：独立发明人
- **企业申请**：公司法人申请
- **科研院所**：高校、研究所
- **联合申请**：多方合作申请

#### 2.2.3 申请领域
- **医疗设备**：医疗器械、诊断设备
- **生物医药**：药物研发、生物技术
- **数字医疗**：医疗软件、AI诊断
- **其他领域**：相关技术领域

## 3. 系统架构设计

### 3.1 数据库设计

#### 3.1.1 新增数据表

**论文项目表 (paper_projects)**
```sql
CREATE TABLE paper_projects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_name VARCHAR(200) NOT NULL COMMENT '项目名称',
    project_type ENUM('论文指导', '论文发表', '学术咨询') NOT NULL COMMENT '项目类型',
    service_level ENUM('基础服务', '标准服务', '高级服务') NOT NULL COMMENT '服务等级',
    applicant_type ENUM('个人学者', '医疗机构', '企业研发', '联合申请') NOT NULL COMMENT '申请人类型',
    
    -- 论文信息
    paper_title VARCHAR(500) COMMENT '论文标题',
    research_field VARCHAR(100) COMMENT '研究领域',
    target_journal VARCHAR(200) COMMENT '目标期刊',
    paper_status ENUM('初稿', '修改中', '已投稿', '审稿中', '已录用', '已发表', '被拒稿') DEFAULT '初稿' COMMENT '论文状态',
    
    -- 时间管理
    apply_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '申请时间',
    confirm_time DATETIME COMMENT '确认时间',
    start_time DATETIME COMMENT '开始时间',
    submit_time DATETIME COMMENT '投稿时间',
    accept_time DATETIME COMMENT '录用时间',
    publish_time DATETIME COMMENT '发表时间',
    
    -- 财务信息
    price DECIMAL(10,2) COMMENT '项目价格',
    discount DECIMAL(5,2) DEFAULT 0 COMMENT '优惠折扣',
    
    -- 状态管理
    status ENUM('待确认', '已确认', '进行中', '已投稿', '审稿中', '已录用', '已发表', '已完成', '已归档') DEFAULT '待确认' COMMENT '项目状态',
    is_archived BOOLEAN DEFAULT FALSE COMMENT '是否归档',
    
    -- 外键关联
    applicant_id INT NOT NULL COMMENT '申请者ID',
    confirmer_id INT COMMENT '确认者ID',
    executor_id INT COMMENT '执行者ID',
    
    remarks TEXT COMMENT '项目备注',
    
    FOREIGN KEY (applicant_id) REFERENCES users(id),
    FOREIGN KEY (confirmer_id) REFERENCES staff(id),
    FOREIGN KEY (executor_id) REFERENCES staff(id)
);
```

**专利项目表 (patent_projects)**
```sql
CREATE TABLE patent_projects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_name VARCHAR(200) NOT NULL COMMENT '项目名称',
    project_type ENUM('发明专利申请', '实用新型申请', '外观设计申请', '国际申请', '专利保护', '专利管理') NOT NULL COMMENT '项目类型',
    applicant_type ENUM('个人发明者', '企业申请', '科研院所', '联合申请') NOT NULL COMMENT '申请人类型',
    application_field ENUM('医疗设备', '生物医药', '数字医疗', '其他领域') NOT NULL COMMENT '申请领域',
    
    -- 专利信息
    invention_title VARCHAR(500) COMMENT '发明名称',
    technical_field VARCHAR(100) COMMENT '技术领域',
    application_number VARCHAR(50) COMMENT '申请号',
    publication_number VARCHAR(50) COMMENT '公开号',
    patent_number VARCHAR(50) COMMENT '专利号',
    patent_status ENUM('申请中', '公开', '实审', '授权', '维持', '终止', '无效') DEFAULT '申请中' COMMENT '专利状态',
    
    -- 时间管理
    apply_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '申请时间',
    confirm_time DATETIME COMMENT '确认时间',
    file_time DATETIME COMMENT '递交时间',
    publish_time DATETIME COMMENT '公开时间',
    grant_time DATETIME COMMENT '授权时间',
    
    -- 财务信息
    price DECIMAL(10,2) COMMENT '项目价格',
    discount DECIMAL(5,2) DEFAULT 0 COMMENT '优惠折扣',
    annual_fee DECIMAL(10,2) COMMENT '年费',
    
    -- 状态管理
    status ENUM('待确认', '已确认', '准备中', '已递交', '审查中', '已授权', '维持中', '已完成', '已归档') DEFAULT '待确认' COMMENT '项目状态',
    is_archived BOOLEAN DEFAULT FALSE COMMENT '是否归档',
    
    -- 外键关联
    applicant_id INT NOT NULL COMMENT '申请者ID',
    confirmer_id INT COMMENT '确认者ID',
    executor_id INT COMMENT '执行者ID',
    
    remarks TEXT COMMENT '项目备注',
    
    FOREIGN KEY (applicant_id) REFERENCES users(id),
    FOREIGN KEY (confirmer_id) REFERENCES staff(id),
    FOREIGN KEY (executor_id) REFERENCES staff(id)
);
```

**文件管理表 (project_files)**
```sql
CREATE TABLE project_files (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL COMMENT '项目ID',
    project_type ENUM('software', 'paper', 'patent') NOT NULL COMMENT '项目类型',
    file_name VARCHAR(255) NOT NULL COMMENT '文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '文件路径',
    file_type VARCHAR(50) NOT NULL COMMENT '文件类型',
    file_size BIGINT COMMENT '文件大小',
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    uploader_id INT NOT NULL COMMENT '上传者ID',
    file_category ENUM('申请材料', '技术文档', '证书文件', '其他文件') NOT NULL COMMENT '文件分类',
    
    FOREIGN KEY (uploader_id) REFERENCES users(id)
);
```

#### 3.1.2 扩展现有表

**用户表扩展字段**
```sql
ALTER TABLE users ADD COLUMN user_category ENUM('软件著作权', '论文指导', '专利申请', '综合服务') DEFAULT '软件著作权' COMMENT '用户类别';
ALTER TABLE users ADD COLUMN organization VARCHAR(200) COMMENT '所属机构';
ALTER TABLE users ADD COLUMN research_field VARCHAR(100) COMMENT '研究领域';
```

**员工表扩展字段**
```sql
ALTER TABLE staff ADD COLUMN expertise_area VARCHAR(200) COMMENT '专业领域';
ALTER TABLE staff ADD COLUMN service_types VARCHAR(200) COMMENT '服务类型';
```

### 3.2 业务流程设计

#### 3.2.1 论文指导业务流程

```
用户申请 → 业务员确认 → 专家匹配 → 开始指导 → 论文修改 → 期刊推荐 → 投稿跟踪 → 发表完成 → 项目归档
```

**详细流程：**
1. **用户申请**：填写论文信息、研究领域、目标期刊
2. **业务员确认**：审核申请材料，确认服务等级
3. **专家匹配**：根据研究领域匹配合适的指导专家
4. **开始指导**：专家开始论文指导和修改工作
5. **论文修改**：多轮修改和完善
6. **期刊推荐**：推荐合适的期刊并协助投稿
7. **投稿跟踪**：跟踪审稿进度，处理审稿意见
8. **发表完成**：论文成功发表
9. **项目归档**：整理项目文件，归档保存

#### 3.2.2 专利申请业务流程

```
用户申请 → 业务员确认 → 专利检索 → 技术分析 → 申请文件准备 → 递交申请 → 审查跟踪 → 授权维护 → 项目归档
```

**详细流程：**
1. **用户申请**：提交技术方案，选择申请类型
2. **业务员确认**：审核技术方案，确认申请策略
3. **专利检索**：进行现有技术检索，分析新颖性
4. **技术分析**：深入分析技术方案，确定保护范围
5. **申请文件准备**：撰写说明书、权利要求书等
6. **递交申请**：向专利局递交申请文件
7. **审查跟踪**：跟踪审查进度，处理审查意见
8. **授权维护**：获得授权后，进行年费管理
9. **项目归档**：整理项目文件，归档保存

### 3.3 用户界面设计

#### 3.3.1 用户端功能

**论文指导模块**
- 论文项目申请页面
- 论文进度查看页面
- 专家指导记录页面
- 期刊推荐页面
- 论文文件管理页面

**专利申请模块**
- 专利项目申请页面
- 专利申请进度页面
- 技术方案提交页面
- 专利检索结果页面
- 专利文件管理页面

#### 3.3.2 业务员端功能

**论文管理**
- 论文项目列表
- 专家资源管理
- 期刊信息管理
- 论文质量评估

**专利管理**
- 专利项目列表
- 技术领域管理
- 专利检索工具
- 申请策略规划

#### 3.3.3 执行者端功能

**论文执行**
- 论文指导工作台
- 专家匹配系统
- 论文修改工具
- 期刊投稿助手

**专利执行**
- 专利申请工作台
- 技术分析工具
- 申请文件生成
- 审查意见处理

## 4. 技术实现方案

### 4.1 后端架构

#### 4.1.1 新增蓝图模块
```
web_app/views/
├── paper.py          # 论文相关视图
├── patent.py         # 专利相关视图
├── expert.py         # 专家管理视图
└── journal.py        # 期刊管理视图
```

#### 4.1.2 新增服务模块
```
web_app/services/
├── paper_service.py  # 论文业务逻辑
├── patent_service.py # 专利业务逻辑
├── expert_service.py # 专家匹配服务
└── file_service.py   # 文件管理服务
```

### 4.2 前端组件

#### 4.2.1 新增模板
```
templates/
├── paper/            # 论文相关模板
│   ├── apply.html
│   ├── dashboard.html
│   └── detail.html
├── patent/           # 专利相关模板
│   ├── apply.html
│   ├── dashboard.html
│   └── detail.html
└── expert/           # 专家相关模板
    ├── list.html
    └── profile.html
```

#### 4.2.2 新增静态资源
```
static/
├── js/
│   ├── paper.js      # 论文相关JS
│   ├── patent.js     # 专利相关JS
│   └── expert.js     # 专家相关JS
└── css/
    ├── paper.css     # 论文相关样式
    └── patent.css    # 专利相关样式
```

### 4.3 数据库迁移

#### 4.3.1 迁移脚本
```python
# migrate_paper_patent.py
def create_paper_tables():
    """创建论文相关表"""
    pass

def create_patent_tables():
    """创建专利相关表"""
    pass

def extend_existing_tables():
    """扩展现有表"""
    pass
```

## 5. 系统集成方案

### 5.1 与现有系统集成

#### 5.1.1 统一用户管理
- 扩展现有用户表，支持多业务类型
- 统一登录认证，支持业务切换
- 统一权限管理，支持角色分配

#### 5.1.2 统一项目管理
- 基于现有Project模型，扩展业务类型
- 统一状态管理，支持不同业务流程
- 统一文件管理，支持分类存储

#### 5.1.3 统一消息系统
- 扩展现有Message模型，支持业务分类
- 统一通知机制，支持多种提醒方式
- 统一沟通平台，支持多方协作

### 5.2 数据迁移策略

#### 5.2.1 现有数据保护
- 备份现有数据库
- 创建数据迁移脚本
- 验证数据完整性

#### 5.2.2 渐进式部署
- 先部署数据库结构
- 再部署后端功能
- 最后部署前端界面

## 6. 质量保证

### 6.1 测试策略

#### 6.1.1 单元测试
- 模型测试
- 服务测试
- 视图测试

#### 6.1.2 集成测试
- 业务流程测试
- 数据库集成测试
- 前后端集成测试

#### 6.1.3 用户验收测试
- 功能完整性测试
- 用户体验测试
- 性能压力测试

### 6.2 安全考虑

#### 6.2.1 数据安全
- 敏感信息加密
- 访问权限控制
- 操作日志记录

#### 6.2.2 文件安全
- 文件类型验证
- 病毒扫描
- 访问控制

## 7. 部署计划

### 7.1 开发阶段
1. **第一阶段**：数据库设计和模型创建
2. **第二阶段**：后端API开发
3. **第三阶段**：前端界面开发
4. **第四阶段**：系统集成测试

### 7.2 部署阶段
1. **测试环境**：功能验证和性能测试
2. **预生产环境**：用户验收测试
3. **生产环境**：正式上线部署

### 7.3 维护阶段
1. **监控运维**：系统监控和性能优化
2. **用户培训**：功能培训和使用指导
3. **持续改进**：根据用户反馈优化功能

## 8. 风险评估

### 8.1 技术风险
- 数据库性能影响
- 系统复杂度增加
- 集成兼容性问题

### 8.2 业务风险
- 用户接受度
- 业务流程变更
- 数据迁移风险

### 8.3 缓解措施
- 充分测试验证
- 渐进式部署
- 用户培训支持

---

**文档版本**：v1.0  
**创建日期**：2024年9月28日  
**最后更新**：2024年9月28日  
**审核状态**：待审核
