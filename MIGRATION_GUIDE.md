# BigTeam Django 升级迁移指南

## 迁移概述

本指南将帮助您从旧的Django 1.x BigTeam项目迁移到新的Django 4.2版本，同时添加Git支持。

## 迁移前准备

### 1. 备份数据
```bash
# 备份原始项目
cp -r /path/to/old/bigteam /path/to/backup/bigteam_backup_$(date +%Y%m%d)

# 备份数据库
cp bigteam.db bigteam_backup_$(date +%Y%m%d).db
```

### 2. 安装Python 3.8+
确保您的系统运行Python 3.8或更高版本：
```bash
python3 --version
```

### 3. 创建虚拟环境
```bash
python3 -m venv bigteam_env
source bigteam_env/bin/activate  # Linux/Mac
# 或者 Windows: bigteam_env\Scripts\activate
```

## 安装依赖

### 1. 安装Django 4.2和相关包
```bash
pip install -r requirements.txt
```

### 2. 安装VCS客户端库
```bash
# SVN支持（可选，如果系统没有）
sudo apt-get install python3-dev libsvn-dev  # Ubuntu/Debian
# 或者
brew install subversion  # macOS

# Git支持已包含在requirements.txt中
```

## 数据迁移

### 1. 复制数据库文件
```bash
cp /path/to/old/bigteam.db bigteam_new/bigteam.db
```

### 2. 运行Django迁移
```bash
cd bigteam_new
python manage.py makemigrations commits
python manage.py migrate
```

### 3. 数据模型更新
由于添加了新字段，需要更新现有数据：

```bash
python manage.py shell
```

在Django shell中执行：
```python
from commits.models import Repository, Author, CommitLog

# 为现有仓库设置VCS类型
Repository.objects.filter(vcs_type='').update(vcs_type='svn')

# 为现有作者添加显示名称
for author in Author.objects.filter(display=''):
    author.display = author.account
    author.save()

# 验证数据
print(f"Repositories: {Repository.objects.count()}")
print(f"Authors: {Author.objects.count()}")
print(f"Commits: {CommitLog.objects.count()}")
```

## 配置更新

### 1. 环境变量设置
创建 `.env` 文件（可选）：
```bash
# .env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///bigteam.db
```

### 2. 静态文件收集
```bash
python manage.py collectstatic
```

### 3. 创建超级用户
```bash
python manage.py createsuperuser
```

## 添加Git仓库

### 1. 通过Admin界面添加
1. 访问 `http://localhost:8000/admin/`
2. 进入 "Repositories" 管理
3. 点击 "Add repository"
4. 选择VCS类型为 "Git"
5. 填写仓库信息：
   - Name: 仓库名称
   - URL: Git仓库URL (https://github.com/user/repo.git)
   - Branch: 分支名称（默认main）
   - 认证信息（用户名/密码或访问令牌）

### 2. 认证配置

#### GitHub/GitLab访问令牌
1. 在GitHub/GitLab中生成个人访问令牌
2. 在仓库配置中填写Access Token字段
3. 用户名和密码字段可以留空

#### SSH密钥认证
1. 确保SSH密钥已配置
2. 在SSH Key Path字段中填写私钥路径
3. URL使用SSH格式：`git@github.com:user/repo.git`

## 验证迁移

### 1. 启动开发服务器
```bash
python manage.py runserver
```

### 2. 验证功能
访问 `http://localhost:8000` 并检查：
- [ ] 主页显示现有项目
- [ ] 项目详情页面正常
- [ ] 作者详情页面正常
- [ ] 能够添加新的Git仓库
- [ ] 更新仓库功能正常

### 3. 测试Git集成
1. 添加一个测试Git仓库
2. 点击"Update All"更新仓库
3. 检查是否成功获取提交记录

## 故障排除

### 常见问题

#### 1. 数据库迁移失败
```bash
# 如果迁移失败，尝试手动迁移
python manage.py migrate --fake-initial
python manage.py migrate
```

#### 2. SVN客户端不可用
```bash
# 检查pysvn安装
python -c "import pysvn; print('SVN OK')"

# 如果失败，重新安装
pip uninstall pysvn
pip install pysvn
```

#### 3. Git客户端不可用
```bash
# 检查GitPython安装
python -c "import git; print('Git OK')"

# 如果失败，重新安装
pip install GitPython
```

#### 4. 模板错误
确保模板文件正确复制：
```bash
cp -r commits/templates bigteam_new/templates
```

#### 5. 静态文件问题
```bash
python manage.py collectstatic --clear
```

### 性能优化

#### 1. 数据库索引
新的模型包含了性能优化的索引，运行迁移后会自动创建。

#### 2. 查询优化
新版本使用了select_related和prefetch_related来优化数据库查询。

#### 3. 缓存配置（可选）
在settings.py中添加缓存配置：
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'bigteam_cache_table',
    }
}
```

然后创建缓存表：
```bash
python manage.py createcachetable
```

## 定时任务设置

### 1. 使用Cron定时更新
创建 cron 任务来定期更新仓库：
```bash
# 编辑crontab
crontab -e

# 添加以下行（每小时更新一次）
0 * * * * cd /path/to/bigteam_new && python manage.py shell -c "from commits.models import UpdateRepositories; UpdateRepositories()"
```

### 2. 使用Django-Cron（推荐）
安装django-cron：
```bash
pip install django-cron
```

在settings.py中添加：
```python
INSTALLED_APPS = [
    # ... 其他应用
    'django_cron',
]

CRON_CLASSES = [
    'commits.cron.UpdateRepositoriesJob',
]
```

创建cron作业文件 `commits/cron.py`：
```python
from django_cron import CronJobBase, Schedule
from .models import UpdateRepositories

class UpdateRepositoriesJob(CronJobBase):
    RUN_EVERY_MINS = 60  # 每小时运行一次
    
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'commits.update_repositories'
    
    def do(self):
        UpdateRepositories()
```

## 后续维护

### 1. 监控日志
查看日志文件以监控系统状态：
```bash
tail -f bigteam.log
```

### 2. 定期备份
设置定期数据库备份：
```bash
# 创建备份脚本
cat > backup_bigteam.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp bigteam.db "backups/bigteam_$DATE.db"
# 保留最近30天的备份
find backups/ -name "bigteam_*.db" -mtime +30 -delete
EOF

chmod +x backup_bigteam.sh
```

### 3. 更新依赖
定期更新Python包：
```bash
pip list --outdated
pip install --upgrade package_name
```

## 迁移完成检查清单

- [ ] 数据库迁移成功
- [ ] 所有现有数据正确显示
- [ ] SVN仓库继续正常工作
- [ ] 能够添加和更新Git仓库
- [ ] 管理界面功能正常
- [ ] 静态文件正确加载
- [ ] 日志功能正常
- [ ] 定时任务设置完成
- [ ] 备份策略实施

恭喜！您已成功升级BigTeam到Django 4.2并添加了Git支持。