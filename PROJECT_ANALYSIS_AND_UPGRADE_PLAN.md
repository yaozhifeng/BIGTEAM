# BigTeam 项目分析和升级方案

## 项目概述

### 项目功能
BigTeam 是一个简单的Web应用程序，用于测量团队生产力。它通过检查SVN代码库来提供团队成员表现的概览。

**主要功能：**
1. **主页视图** - 显示所有项目和团队成员表现的概览
2. **项目视图** - 显示项目内成员表现
3. **个人视图** - 显示每个人的详细信息，包括对各项目的贡献、所有提交和详细提交日志
4. **统计周期** - 按月提供统计，可在整个历史记录中滚动不同时期

### 当前技术栈分析

#### Django版本
- **当前版本**: Django 1.x (基于manage.py使用`execute_manager`判断)
- **特征**: 使用了非常老的Django架构，包括：
  - `execute_manager` (Django 1.4之前)
  - `django.conf.urls.defaults` (Django 1.4之前)
  - South数据库迁移工具 (Django 1.7之前)
  - 老式的template配置

#### 依赖包分析
```python
# 核心依赖
django (1.x)
pysvn                  # SVN客户端
south                  # 数据库迁移
debug_toolbar          # 调试工具
coffin                 # Jinja2模板引擎
django_cron           # 定时任务
fabric                # 部署工具
```

#### 数据模型
```python
class Repository(models.Model):
    name = models.CharField(max_length=50)
    desc = models.CharField(max_length=250, null=True, blank=True)
    url = models.CharField(max_length=500)           # SVN URL
    username = models.CharField(max_length=50)       # SVN 用户名
    password = models.CharField(max_length=50)       # SVN 密码
    sourceview = models.CharField(max_length=500, null=True, blank=True)

class Author(models.Model):
    account = models.CharField(max_length=50)
    display = models.CharField(max_length=50)

class CommitLog(models.Model):
    repository = models.ForeignKey(Repository, related_name='commits')
    revision = models.IntegerField()                 # SVN修订号
    time = models.DateTimeField()
    author = models.ForeignKey(Author, related_name='commits')
    comment = models.TextField()
```

#### SVN集成架构
- **SVNLogClient**: 封装pysvn库，处理SVN连接和认证
- **SVNRevLogIter**: 迭代SVN提交日志
- 支持增量更新（只获取新的修订版本）
- 支持差异分析和行数统计

## 升级方案

### 阶段1: Django框架升级 (Django 1.x → Django 4.2 LTS)

#### 升级目标
- **目标版本**: Django 4.2 LTS (2023年4月发布)
- **支持周期**: 至少3年安全更新
- **Python兼容性**: Python 3.8-3.12

#### 主要变更项目

**1. 项目结构调整**
```bash
# 原结构 (Django 1.x)
bigteam/
├── manage.py
├── settings.py
├── urls.py
├── commits/
└── ...

# 新结构 (Django 4.2)
bigteam/
├── manage.py
├── bigteam/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── commits/
└── requirements.txt
```

**2. settings.py 核心更改**
- 移除 `TEMPLATE_*` 配置，改用 `TEMPLATES`
- 移除 `MIDDLEWARE_CLASSES`，改用 `MIDDLEWARE`
- 更新 `SECRET_KEY` 配置
- 添加 `DEFAULT_AUTO_FIELD`
- 更新静态文件配置使用 `STORAGES`

**3. URL配置更新**
```python
# 原版本 (Django 1.x)
from django.conf.urls.defaults import patterns, include, url

# 新版本 (Django 4.2)
from django.urls import path, include
```

**4. 视图和模板更新**
- 移除 `coffin` 依赖，使用Django原生模板
- 更新 `render_to_response` 为 `render`
- 更新查询集API

**5. 数据库迁移**
- 移除 `south`，使用Django内置迁移
- 重新生成迁移文件
- 添加 `DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'`

### 阶段2: 添加Git支持

#### 设计思路
1. **保持向后兼容**: SVN功能继续工作
2. **统一接口**: 创建通用的VCS接口
3. **插件化架构**: 便于未来添加其他VCS支持

#### 技术实现

**1. 抽象VCS接口**
```python
# commits/vcs/base.py
from abc import ABC, abstractmethod

class BaseVCSClient(ABC):
    @abstractmethod
    def get_logs(self, start_rev, end_rev):
        pass
    
    @abstractmethod
    def get_latest_revision(self):
        pass
    
    @abstractmethod
    def authenticate(self, username, password):
        pass
```

**2. Git客户端实现**
```python
# commits/vcs/git_client.py
import git
from .base import BaseVCSClient

class GitClient(BaseVCSClient):
    def __init__(self, repo_url, branch='main'):
        self.repo_url = repo_url
        self.branch = branch
        self.repo = None
    
    def clone_or_update(self):
        # 克隆或更新Git仓库
        pass
    
    def get_logs(self, since_commit=None):
        # 获取提交日志
        pass
```

**3. 数据模型扩展**
```python
class Repository(models.Model):
    VCS_CHOICES = [
        ('svn', 'Subversion'),
        ('git', 'Git'),
    ]
    
    name = models.CharField(max_length=50)
    desc = models.CharField(max_length=250, null=True, blank=True)
    url = models.CharField(max_length=500)
    vcs_type = models.CharField(max_length=10, choices=VCS_CHOICES, default='svn')
    branch = models.CharField(max_length=100, default='main')  # Git分支
    username = models.CharField(max_length=50, blank=True)
    password = models.CharField(max_length=50, blank=True)
    ssh_key_path = models.CharField(max_length=500, blank=True)  # Git SSH密钥
    access_token = models.CharField(max_length=500, blank=True)  # Git访问令牌
    
    def get_vcs_client(self):
        if self.vcs_type == 'svn':
            return SVNLogClient(self.url, username=self.username, password=self.password)
        elif self.vcs_type == 'git':
            return GitClient(self.url, branch=self.branch)
```

**4. 统一更新逻辑**
```python
def update(self):
    client = self.get_vcs_client()
    try:
        last_stored_rev = self.getLastStoredRev()
        commits = client.get_new_commits(after=last_stored_rev)
        
        for commit in commits:
            self.store_commit(commit)
            
        self.save()
    except Exception as e:
        logger.error(f'Exception updating project - {e}')
```

#### Git特性支持
1. **分支支持**: 默认监控main/master分支，可配置
2. **认证方式**:
   - HTTPS用户名/密码
   - SSH密钥
   - 访问令牌 (GitHub/GitLab)
3. **增量更新**: 基于上次更新时间或提交SHA
4. **作者映射**: Git作者邮箱 → 系统用户

### 阶段3: 界面和功能增强

#### 管理界面升级
1. **现代化Admin界面**: 利用Django 4.2新特性
2. **VCS类型选择**: 在添加仓库时选择SVN或Git
3. **认证配置**: 不同VCS的认证方式配置

#### API增强
1. **RESTful API**: 使用Django REST Framework
2. **实时更新**: WebSocket支持
3. **导出功能**: CSV/JSON导出统计数据

#### 前端升级
1. **响应式设计**: Bootstrap 5
2. **图表库升级**: Chart.js最新版本
3. **PWA支持**: 渐进式Web应用特性

## 实施计划

### 第一周: Django核心升级
1. 创建requirements.txt
2. 更新项目结构
3. 升级settings.py
4. 修复URL配置
5. 更新视图和模板

### 第二周: 数据库和依赖升级
1. 移除South，设置Django迁移
2. 更新第三方包
3. 测试数据迁移
4. 修复兼容性问题

### 第三周: Git支持开发
1. 设计VCS抽象层
2. 实现Git客户端
3. 扩展数据模型
4. 统一更新逻辑

### 第四周: 测试和完善
1. 单元测试
2. 集成测试
3. 性能优化
4. 文档更新

## 风险评估

### 高风险项
1. **数据库迁移**: South → Django migrations
2. **模板系统**: Coffin → Django templates
3. **第三方包兼容性**: 特别是pysvn在新Python版本下

### 缓解策略
1. **数据备份**: 升级前完整备份
2. **渐进式升级**: 分阶段测试
3. **回滚计划**: 保留原版本环境
4. **充分测试**: 覆盖所有核心功能

## 预期收益

1. **安全性提升**: 最新安全补丁和特性
2. **性能改进**: Django 4.2性能优化
3. **功能扩展**: Git支持，覆盖更多项目
4. **维护性**: 现代化代码，易于维护
5. **扩展性**: 为未来添加其他VCS做准备

## 总结

这个升级方案将把老旧的Django 1.x项目升级到现代的Django 4.2 LTS，同时保持所有现有功能的完整性，并添加Git支持。整个过程采用渐进式方法，最大化降低风险，确保项目的稳定性和可扩展性。