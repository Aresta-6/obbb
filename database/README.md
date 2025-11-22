# 图书馆数据库设置指南

本目录包含用于创建和初始化图书馆管理系统数据库的 SQL 脚本。

## 文件说明

- `schema.sql`: 用于创建数据库 `library_db` 以及其中所有的表结构。
- `data.sql`: 用于向已创建的表中插入示例数据，方便开发和测试。

## 环境要求

- **MySQL**: 请确保您的系统上已安装 MySQL 服务器。

## 设置步骤

### 1. 登录 MySQL

首先，使用 root 用户或具有创建数据库权限的用户登录到您的 MySQL 服务器。在终端或命令行中运行以下命令，并根据提示输入您的密码：

```bash
mysql -u root -p
```

### 2. 创建并使用数据库

`schema.sql` 脚本中包含了创建数据库的语句 (`CREATE SCHEMA IF NOT EXISTS 
library_db
`)，但如果您想手动创建，可以执行以下命令：

```sql
CREATE DATABASE library_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE library_db;
```

### 3. 执行 SQL 脚本

您可以通过 `source` 命令在 MySQL 客户端中依次执行这两个脚本。

**请务必先执行 `schema.sql`，再执行 `data.sql`**，因为后者依赖于前者创建的表结构。

```bash
-- 登录 MySQL 后
mysql> USE library_db;

-- 执行 schema.sql 来创建表
mysql> source /path/to/your/project/database/schema.sql;

-- 执行 data.sql 来填充数据
mysql> source /path/to/your/project/database/data.sql;
```

**注意**: 请将 `/path/to/your/project/` 替换为您本地项目中 `database` 目录的实际绝对路径。

### 4. 验证安装

执行完脚本后，您可以检查是否成功创建了表并插入了数据。

```sql
-- 查看所有表
mysql> SHOW TABLES;

-- 查询 Users 表中的数据
mysql> SELECT * FROM Users;

-- 查询 Books 表中的数据
mysql> SELECT * FROM Books;
```

如果能看到表和数据，说明数据库已成功设置。
