# BigTeam - Django 4.2

一个现代化的团队生产力分析工具，支持SVN和Git版本控制系统。

## 概述

BigTeam是一个Web应用程序，用于分析和可视化软件开发团队的生产力指标。它可以从版本控制系统中提取提交数据，并提供直观的图表和统计信息来帮助团队了解其开发活动。

## 特性

### 🚀 版本控制系统支持
- **SVN (Subversion)**: 完整支持，包括增量更新
- **Git**: 新增支持，包括GitHub、GitLab等
- **统一接口**: 一致的管理体验

### 📊 数据分析功能
- **团队概览**: 所有项目和成员的总体表现
- **项目详情**: 项目内成员贡献分析
- **个人统计**: 个人跨项目贡献详情
- **时间序列**: 按月统计和历史趋势

### 🔐 认证支持
- **用户名/密码**: 传统认证方式
- **SSH密钥**: Git仓库SSH认证
- **访问令牌**: GitHub/GitLab个人访问令牌

### 🎯 现代化界面
- **响应式设计**: 适配各种设备
- **AJAX更新**: 无刷新数据加载
- **Django Admin**: 强化的管理界面

## 技术栈

- **后端**: Django 4.2 LTS
- **数据库**: SQLite (可扩展到PostgreSQL/MySQL)
- **前端**: Bootstrap + jQuery
- **VCS客户端**: pysvn + GitPython
- **部署**: WSGI/ASGI兼容

## 快速开始

### 1. 环境要求

- Python 3.8+
- Git (用于Git仓库支持)
- SVN客户端 (用于SVN仓库支持，可选)

### 2. 安装

```bash
# 克隆仓库
git clone <repository-url>
cd bigteam

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或者 Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置

```bash
# 运行数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 收集静态文件
python manage.py collectstatic
```

### 4. 运行

```bash
# 启动开发服务器
python manage.py runserver

# 访问应用
# http://localhost:8000 - 主应用
# http://localhost:8000/admin/ - 管理界面
```

## 使用指南

### 添加SVN仓库

1. 登录管理界面 (`/admin/`)
2. 进入 "Repositories" 管理
3. 点击 "Add repository"
4. 填写基本信息：
   - **Name**: 项目名称
   - **URL**: SVN仓库URL
   - **VCS Type**: 选择 "Subversion"
   - **Username/Password**: SVN认证信息

### 添加Git仓库

1. 进入 "Repositories" 管理
2. 点击 "Add repository" 
3. 填写信息：
   - **Name**: 项目名称
   - **URL**: Git仓库URL
   - **VCS Type**: 选择 "Git"
   - **Branch**: 分支名称 (默认: main)
   - **认证信息**: 选择以下之一
     - Username/Password
     - Access Token
     - SSH Key Path

### 更新数据

#### 手动更新
- 在管理界面选择仓库，执行 "Update selected repositories"
- 或访问 `/update_all/` 更新所有仓库

#### 自动更新
设置定时任务：
```bash
# 添加到crontab (每小时更新)
0 * * * * cd /path/to/bigteam && python manage.py shell -c "from commits.models import UpdateRepositories; UpdateRepositories()"
```

## 配置选项

### 环境变量

创建 `.env` 文件：
```bash
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
DATABASE_URL=sqlite:///bigteam.db
```

### 数据库配置

默认使用SQLite，可配置其他数据库：

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bigteam',
        'USER': 'username',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 缓存配置

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'bigteam_cache_table',
    }
}
```

## API接口

### AJAX端点

应用提供以下AJAX API：

- `GET /ajax/graph/summary/` - 总体提交统计
- `GET /ajax/graph/project/` - 项目提交统计
- `GET /ajax/graph/person/` - 个人提交统计
- `GET /ajax/commits/detail/` - 提交详情列表
- `GET /ajax/commits/stats/` - 贡献者统计
- `GET /ajax/commits/project/` - 项目统计

#### 参数
- `author`: 作者ID过滤
- `project`: 项目ID过滤
- `year`: 年份过滤
- `month`: 月份过滤

## 从旧版本迁移

### 迁移步骤

1. **备份数据**
```bash
cp bigteam.db bigteam_backup.db
```

2. **运行迁移脚本**
```bash
python migrate_data.py --old-db /path/to/old/bigteam.db
```

3. **验证迁移**
```bash
python migrate_data.py --verify-only
```

详细迁移指南请参考 [MIGRATION_GUIDE.md](../MIGRATION_GUIDE.md)

## 部署

### 生产环境配置

```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECRET_KEY = os.environ['SECRET_KEY']

# 使用PostgreSQL
DATABASES = {
    'default': dj_database_url.parse(os.environ['DATABASE_URL'])
}
```

### 使用Nginx + Gunicorn

```bash
# 安装Gunicorn
pip install gunicorn

# 启动应用
gunicorn bigteam.wsgi:application --bind 0.0.0.0:8000
```

### Docker部署

```dockerfile
# Dockerfile示例
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "bigteam.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 监控和维护

### 日志查看

```bash
# 查看应用日志
tail -f bigteam.log

# 查看Django日志
python manage.py shell -c "import logging; logging.getLogger('commits').info('Test')"
```

### 性能监控

- 使用Django Debug Toolbar (开发环境)
- 监控数据库查询
- 跟踪内存使用

### 定期维护

```bash
# 清理临时文件
python manage.py clearsessions

# 更新数据库统计
python manage.py dbshell -c "ANALYZE;"

# 备份数据库
cp bigteam.db backups/bigteam_$(date +%Y%m%d).db
```

## 故障排除

### 常见问题

#### Git认证失败
```bash
# 检查SSH密钥
ssh -T git@github.com

# 检查访问令牌
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

#### SVN连接问题
```bash
# 检查SVN客户端
svn info https://your-svn-server/repo

# 检查pysvn安装
python -c "import pysvn; print('SVN OK')"
```

#### 数据库问题
```bash
# 重新运行迁移
python manage.py migrate --fake-initial

# 检查数据一致性
python migrate_data.py --verify-only
```

## 开发

### 代码结构

```
bigteam/
├── bigteam/           # 项目配置
├── commits/           # 主应用
│   ├── vcs/          # VCS抽象层
│   ├── templates/    # 模板文件
│   └── static/       # 静态文件
├── requirements.txt   # 依赖
└── migrate_data.py   # 迁移脚本
```

### 添加新VCS支持

1. 在 `commits/vcs/` 下创建新客户端
2. 继承 `BaseVCSClient`
3. 实现必需的抽象方法
4. 在 `Repository.get_vcs_client()` 中添加支持

### 运行测试

```bash
# 运行所有测试
python manage.py test

# 运行特定应用测试
python manage.py test commits
```

## 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 创建Pull Request

## 许可证

本项目基于MIT许可证开源。详见 [LICENSE](LICENSE) 文件。

## 支持

如有问题或建议，请：

1. 查看 [FAQ](docs/FAQ.md)
2. 阅读 [故障排除指南](docs/TROUBLESHOOTING.md)
3. 提交 [Issue](https://github.com/your-repo/issues)

## 更新日志

### v2.0.0 (Django 4.2)
- ✨ 升级到Django 4.2 LTS
- ✨ 新增Git支持
- ✨ VCS抽象层
- ✨ 现代化管理界面
- ✨ 性能优化
- 🔧 数据库迁移工具
- 📚 完整文档

### v1.x (Django 1.x)
- 基础SVN支持
- 团队统计功能
- 简单Web界面