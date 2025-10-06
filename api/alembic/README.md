# Alembic数据库迁移

本目录包含Alembic数据库迁移脚本和配置。

## 快速开始

### 创建新迁移

**自动生成迁移**(推荐):
```bash
# 基于模型变更自动生成迁移
alembic revision --autogenerate -m "描述你的改动"
```

**手动创建迁移**:
```bash
alembic revision -m "描述你的改动"
```

### 执行迁移

**升级到最新版本**:
```bash
alembic upgrade head
```

**升级到特定版本**:
```bash
alembic upgrade <revision_id>
```

**降级一个版本**:
```bash
alembic downgrade -1
```

**降级到特定版本**:
```bash
alembic downgrade <revision_id>
```

### 查看迁移状态

**查看当前版本**:
```bash
alembic current
```

**查看迁移历史**:
```bash
alembic history --verbose
```

**查看待执行的迁移**:
```bash
alembic show head
```

## 目录结构

```
api/alembic/
├── env.py              # Alembic环境配置
├── script.py.mako      # 迁移脚本模板
├── versions/           # 迁移版本目录
│   └── YYYYMMDD_HHMM_<rev>_<slug>.py
└── README.md           # 本文件
```

## 最佳实践

### 1. 迁移命名规范

使用清晰描述性的消息:
- ✅ `alembic revision --autogenerate -m "add user email index"`
- ✅ `alembic revision --autogenerate -m "create audit_logs table"`
- ❌ `alembic revision --autogenerate -m "update"`

### 2. 审查自动生成的迁移

自动生成后务必检查:
```bash
# 生成后立即查看
cat api/alembic/versions/<latest_file>.py
```

检查项:
- [ ] 升级和降级操作是否正确
- [ ] 是否包含不需要的改动
- [ ] 索引是否正确创建
- [ ] 数据迁移逻辑是否完整

### 3. 测试迁移

在应用到生产前测试:
```bash
# 1. 升级
alembic upgrade head

# 2. 降级
alembic downgrade -1

# 3. 再次升级
alembic upgrade head
```

### 4. 生产环境迁移

```bash
# 1. 备份数据库
pg_dump dbname > backup.sql

# 2. 查看待执行的迁移
alembic current
alembic history

# 3. 执行迁移
alembic upgrade head

# 4. 验证
alembic current
```

## 常见场景

### 添加新表

1. 在 `api/database/models.py` 中定义模型
2. 自动生成迁移:
```bash
alembic revision --autogenerate -m "create new_table"
```
3. 执行迁移:
```bash
alembic upgrade head
```

### 添加列

1. 在模型中添加新字段
2. 自动生成迁移:
```bash
alembic revision --autogenerate -m "add column_name to table_name"
```
3. 执行迁移:
```bash
alembic upgrade head
```

### 数据迁移

对于需要迁移数据的场景,手动创建迁移:

```python
"""migrate user data

Revision ID: xxx
"""
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # 1. 添加新列
    op.add_column('users', sa.Column('new_field', sa.String(50)))

    # 2. 迁移数据
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE users SET new_field = old_field WHERE old_field IS NOT NULL")
    )

    # 3. 删除旧列(可选)
    op.drop_column('users', 'old_field')

def downgrade() -> None:
    # 反向操作
    op.add_column('users', sa.Column('old_field', sa.String(50)))
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE users SET old_field = new_field WHERE new_field IS NOT NULL")
    )
    op.drop_column('users', 'new_field')
```

### 创建索引

```python
def upgrade() -> None:
    op.create_index(
        'idx_users_email',
        'users',
        ['email'],
        unique=True
    )

def downgrade() -> None:
    op.drop_index('idx_users_email', 'users')
```

## 故障排除

### 问题: 迁移冲突

**症状**: Multiple heads detected

**解决**:
```bash
# 查看所有head
alembic heads

# 合并heads
alembic merge heads -m "merge heads"
```

### 问题: 无法降级

**症状**: downgrade操作失败

**解决**:
1. 检查降级脚本是否正确实现
2. 手动修复数据库状态
3. 使用 `alembic stamp <revision>` 标记版本

### 问题: 自动生成未检测到变更

**症状**: `alembic revision --autogenerate` 没有生成改动

**解决**:
1. 确保模型已导入到 `env.py`
2. 检查 `target_metadata` 配置
3. 确认数据库连接URL正确

## 环境变量

Alembic使用应用配置中的数据库URL:

```bash
# .env
DB_URL=postgresql://user:password@localhost:5432/dbname
```

## 相关文档

- [Alembic官方文档](https://alembic.sqlalchemy.org/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
- 项目数据库模型: `api/database/models.py`
- 数据库配置: `core/config.py`
