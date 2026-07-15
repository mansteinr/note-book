# MySQL 简介及常用语法

> 本文档系统整理 MySQL 数据库的核心概念、常用 SQL 语法、典型使用场景以及高频面试题，适用于学习复习与面试准备。

---

## 目录

- [一、MySQL 简介](#一mysql-简介)
- [二、常用语法](#二常用语法)
- [三、使用场景](#三使用场景)
- [四、常见面试题](#四常见面试题)
- [五、性能优化建议](#五性能优化建议)
- [六、MySQL 与 MongoDB 对比](#六mysql-与-mongodb-对比)
- [附录：MySQL 版本特性对比](#附录mysql-版本特性对比)

---

## 一、MySQL 简介

### 1.1 什么是 MySQL

MySQL 是一个**关系型数据库管理系统**（RDBMS），由瑞典 MySQL AB 公司开发，目前属于 Oracle 旗下产品。它使用 **SQL（Structured Query Language）** 作为标准语言，用于访问和管理数据库。

### 1.2 核心特点

| 特点 | 说明 |
|------|------|
| 开源免费 | 社区版免费使用，企业版提供商业支持 |
| 跨平台 | 支持 Windows、Linux、macOS 等多种操作系统 |
| 高性能 | 支持大型数据库，处理速度快 |
| 支持事务 | 支持 ACID 特性，保证数据一致性 |
| 多存储引擎 | InnoDB、MyISAM、Memory 等，可按需选择 |
| 支持多种连接方式 | JDBC、ODBC、.NET、PHP 等多种语言连接 |
| 复制与集群 | 支持主从复制、读写分离、分库分表 |

### 1.3 常用存储引擎对比

| 特性 | InnoDB | MyISAM | Memory |
|------|--------|--------|--------|
| 事务支持 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 |
| 锁粒度 | 行级锁 | 表级锁 | 表级锁 |
| 外键 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 |
| 全文索引 | ✅ 支持（5.6+） | ✅ 支持 | ❌ 不支持 |
| 适用场景 | OLTP、高并发写 | 读密集型、统计 | 临时表、缓存 |
| 崩溃恢复 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 |

> **MySQL 5.5 之后默认存储引擎为 InnoDB**，推荐生产环境使用。

### 1.4 MySQL 体系架构

```
客户端（PHP/Java/Python...）
        │
        ▼
┌─────────────────────────────┐
│   连接层（Connection Pool）   │  管理连接、授权认证
├─────────────────────────────┤
│   SQL 层（Server Layer）     │
│   ├─ 查询缓存（Query Cache） │  8.0 已移除
│   ├─ 解析器（Parser）        │  词法/语法分析
│   ├─ 优化器（Optimizer）     │  生成执行计划
│   └─ 执行器（Executor）      │  调用存储引擎接口
├─────────────────────────────┤
│   存储引擎层（Storage Engine）│  数据读写、索引管理
├─────────────────────────────┤
│   文件系统（File System）    │  数据文件、日志文件
└─────────────────────────────┘
```

---

## 二、常用语法

### 2.1 数据库操作

#### 2.1.1 创建与删除数据库

```sql
-- 创建数据库（指定字符集）
CREATE DATABASE IF NOT EXISTS mydb
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

-- 查看所有数据库
SHOW DATABASES;

-- 使用数据库
USE mydb;

-- 删除数据库
DROP DATABASE IF EXISTS mydb;
```

#### 2.1.2 数据库信息查看

```sql
-- 查看数据库创建语句
SHOW CREATE DATABASE mydb;

-- 查看当前数据库
SELECT DATABASE();
```

### 2.2 表操作

#### 2.2.1 创建表

```sql
CREATE TABLE IF NOT EXISTS `user` (
    `id`          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `username`    VARCHAR(50)  NOT NULL COMMENT '用户名',
    `password`    VARCHAR(100) NOT NULL COMMENT '密码',
    `email`       VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    `age`         TINYINT      DEFAULT NULL COMMENT '年龄',
    `status`      TINYINT      DEFAULT 1 COMMENT '状态：0-禁用 1-启用',
    `create_time` DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    KEY `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

#### 2.2.2 修改表结构

```sql
-- 添加列
ALTER TABLE `user` ADD COLUMN `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号';

-- 修改列类型
ALTER TABLE `user` MODIFY COLUMN `phone` VARCHAR(30) NOT NULL COMMENT '手机号';

-- 修改列名
ALTER TABLE `user` CHANGE COLUMN `phone` `mobile` VARCHAR(30) NOT NULL COMMENT '手机号';

-- 删除列
ALTER TABLE `user` DROP COLUMN `mobile`;

-- 重命名表
RENAME TABLE `user` TO `t_user`;
-- 或
ALTER TABLE `user` RENAME TO `t_user`;
```

#### 2.2.3 删除与查看表

```sql
-- 删除表
DROP TABLE IF EXISTS `user`;

-- 清空表（保留结构，重置自增ID）
TRUNCATE TABLE `user`;

-- 查看表结构
DESC `user`;

-- 查看建表语句
SHOW CREATE TABLE `user`;
```

### 2.3 数据操作（DML）

#### 2.3.1 插入数据

```sql
-- 插入单条
INSERT INTO `user` (username, password, email, age)
VALUES ('zhangsan', '123456', 'zs@qq.com', 25);

-- 插入多条
INSERT INTO `user` (username, password, email, age)
VALUES
    ('lisi', '123456', 'ls@qq.com', 30),
    ('wangwu', '123456', 'ww@qq.com', 28);

-- 插入查询结果
INSERT INTO `user_bak` (username, password, email)
SELECT username, password, email FROM `user` WHERE status = 1;

-- 主键冲突时更新（UPSERT）
INSERT INTO `user` (id, username, password)
VALUES (1, 'zhangsan', 'newpwd')
ON DUPLICATE KEY UPDATE password = 'newpwd';
```

#### 2.3.2 更新数据

```sql
-- 条件更新
UPDATE `user` SET age = 26, status = 1 WHERE username = 'zhangsan';

-- 关联更新
UPDATE `user` u
INNER JOIN `user_detail` d ON u.id = d.user_id
SET u.age = d.real_age;
```

#### 2.3.3 删除数据

```sql
-- 条件删除
DELETE FROM `user` WHERE status = 0;

-- 关联删除
DELETE u FROM `user` u
INNER JOIN `order` o ON u.id = o.user_id
WHERE o.status = 'cancelled';
```

### 2.4 数据查询（DQL）

#### 2.4.1 基础查询

```sql
-- 查询所有字段
SELECT * FROM `user`;

-- 查询指定字段
SELECT id, username, email FROM `user`;

-- 别名
SELECT username AS `name`, age AS `年龄` FROM `user`;

-- 去重
SELECT DISTINCT age FROM `user`;
```

#### 2.4.2 条件查询

```sql
-- 比较运算符
SELECT * FROM `user` WHERE age > 25;
SELECT * FROM `user` WHERE age >= 20 AND age <= 30;
SELECT * FROM `user` WHERE age BETWEEN 20 AND 30;

-- 逻辑运算符
SELECT * FROM `user` WHERE age > 25 AND status = 1;
SELECT * FROM `user` WHERE age < 20 OR age > 60;
SELECT * FROM `user` WHERE status != 0;

-- IN / NOT IN
SELECT * FROM `user` WHERE age IN (25, 30, 35);

-- LIKE 模糊查询
SELECT * FROM `user` WHERE username LIKE 'zhang%';   -- 以 zhang 开头
SELECT * FROM `user` WHERE username LIKE '%san';      -- 以 san 结尾
SELECT * FROM `user` WHERE username LIKE '%ang%';     -- 包含 ang

-- NULL 判断
SELECT * FROM `user` WHERE email IS NULL;
SELECT * FROM `user` WHERE email IS NOT NULL;
```

#### 2.4.3 排序与分页

```sql
-- 排序（ASC 升序，DESC 降序）
SELECT * FROM `user` ORDER BY age DESC, create_time ASC;

-- 分页（LIMIT offset, count）
-- 每页 10 条，查询第 2 页
SELECT * FROM `user` ORDER BY id DESC LIMIT 10, 10;

-- 推荐写法（可读性更好）
SELECT * FROM `user` ORDER BY id DESC LIMIT 10 OFFSET 10;
```

#### 2.4.4 聚合函数与分组

```sql
-- 聚合函数
SELECT
    COUNT(*)         AS 总人数,
    COUNT(email)     AS 有邮箱人数,
    AVG(age)         AS 平均年龄,
    SUM(age)         AS 年龄总和,
    MAX(age)         AS 最大年龄,
    MIN(age)         AS 最小年龄
FROM `user`;

-- 分组查询
SELECT
    status,
    COUNT(*)  AS 人数,
    AVG(age)  AS 平均年龄
FROM `user`
GROUP BY status;

-- 分组后过滤（使用 HAVING）
SELECT
    status,
    COUNT(*) AS 人数
FROM `user`
GROUP BY status
HAVING COUNT(*) > 10;

-- 多字段分组
SELECT status, age, COUNT(*) FROM `user` GROUP BY status, age;
```

> **WHERE 与 HAVING 区别**：WHERE 在分组前过滤行，HAVING 在分组后过滤组。

#### 2.4.5 连接查询

```sql
-- 内连接（INNER JOIN）：只返回匹配的行
SELECT u.id, u.username, o.order_no, o.amount
FROM `user` u
INNER JOIN `order` o ON u.id = o.user_id;

-- 左外连接（LEFT JOIN）：返回左表所有行，右表无匹配返回 NULL
SELECT u.id, u.username, o.order_no
FROM `user` u
LEFT JOIN `order` o ON u.id = o.user_id;

-- 右外连接（RIGHT JOIN）：返回右表所有行
SELECT u.id, u.username, o.order_no
FROM `user` u
RIGHT JOIN `order` o ON u.id = o.user_id;

-- 多表连接
SELECT u.username, o.order_no, p.product_name
FROM `user` u
INNER JOIN `order` o ON u.id = o.user_id
INNER JOIN `order_item` oi ON o.id = oi.order_id
INNER JOIN `product` p ON oi.product_id = p.id;

-- 自连接（查询员工及其上级）
SELECT e.name AS 员工, m.name AS 上级
FROM `employee` e
LEFT JOIN `employee` m ON e.manager_id = m.id;
```

#### 2.4.6 子查询

```sql
-- 标量子查询（返回单个值）
SELECT * FROM `user`
WHERE age > (SELECT AVG(age) FROM `user`);

-- 列子查询（返回一列）
SELECT * FROM `user`
WHERE id IN (SELECT user_id FROM `order` WHERE amount > 1000);

-- 行子查询（返回一行）
SELECT * FROM `user`
WHERE (username, age) = (SELECT username, age FROM `user` WHERE id = 1);

-- 表子查询（作为临时表）
SELECT t.status, t.cnt
FROM (
    SELECT status, COUNT(*) AS cnt
    FROM `user`
    GROUP BY status
) t
WHERE t.cnt > 10;

-- EXISTS 子查询
SELECT * FROM `user` u
WHERE EXISTS (
    SELECT 1 FROM `order` o WHERE o.user_id = u.id
);
```

#### 2.4.7 联合查询

```sql
-- UNION：合并结果集并去重
SELECT username, email FROM `user` WHERE status = 1
UNION
SELECT username, email FROM `user_bak` WHERE status = 1;

-- UNION ALL：合并不去重（性能更好）
SELECT username FROM `user`
UNION ALL
SELECT username FROM `user_bak`;
```

> **UNION 与 UNION ALL 区别**：UNION 会对结果去重并排序，UNION ALL 直接合并，性能更好。如果确认无重复数据，优先使用 UNION ALL。

### 2.5 索引操作

#### 2.5.1 创建索引

```sql
-- 普通索引
CREATE INDEX idx_username ON `user`(username);
-- 或
ALTER TABLE `user` ADD INDEX idx_username(username);

-- 唯一索引
CREATE UNIQUE INDEX uk_email ON `user`(email);

-- 主键索引
ALTER TABLE `user` ADD PRIMARY KEY (id);

-- 联合索引（最左前缀原则）
CREATE INDEX idx_status_age ON `user`(status, age);

-- 全文索引
CREATE FULLTEXT INDEX ft_content ON `article`(content);
```

#### 2.5.2 查看与删除索引

```sql
-- 查看索引
SHOW INDEX FROM `user`;

-- 删除索引
DROP INDEX idx_username ON `user`;
-- 或
ALTER TABLE `user` DROP INDEX idx_username;
```

#### 2.5.3 执行计划分析

```sql
-- 查看查询执行计划
EXPLAIN SELECT * FROM `user` WHERE username = 'zhangsan';
```

执行计划关键字段说明：

| 字段 | 说明 |
|------|------|
| id | 查询序号，越大越先执行 |
| select_type | 查询类型（SIMPLE/PRIMARY/SUBQUERY 等） |
| table | 表名 |
| type | 访问类型（**system > const > eq_ref > ref > range > index > ALL**） |
| possible_keys | 可能使用的索引 |
| key | 实际使用的索引 |
| key_len | 索引长度（越短越好） |
| ref | 索引比较的列 |
| rows | 估算扫描行数 |
| Extra | 额外信息（Using index/Using where/Using filesort 等） |

### 2.6 事务与锁

#### 2.6.1 事务操作

```sql
-- 开启事务
START TRANSACTION;
-- 或
BEGIN;

-- 提交
COMMIT;

-- 回滚
ROLLBACK;

-- 设置保存点
SAVEPOINT sp1;
-- 回滚到保存点
ROLLBACK TO sp1;

-- 示例：转账事务
START TRANSACTION;
UPDATE `account` SET balance = balance - 500 WHERE id = 1;
UPDATE `account` SET balance = balance + 500 WHERE id = 2;
-- 确认无误后提交
COMMIT;
-- 出错则回滚
-- ROLLBACK;
```

#### 2.6.2 事务隔离级别

```sql
-- 查看隔离级别
SELECT @@transaction_isolation;

-- 设置隔离级别
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET GLOBAL TRANSACTION ISOLATION LEVEL REPEATABLE READ;
```

| 隔离级别 | 脏读 | 不可重复读 | 幻读 |
|---------|------|----------|------|
| READ UNCOMMITTED（读未提交） | 可能 | 可能 | 可能 |
| READ COMMITTED（读已提交） | ❌ | 可能 | 可能 |
| REPEATABLE READ（可重复读） | ❌ | ❌ | 可能（InnoDB 通过 MVCC 解决） |
| SERIALIZABLE（串行化） | ❌ | ❌ | ❌ |

> **MySQL 默认隔离级别为 REPEATABLE READ**，InnoDB 通过 MVCC + Next-Key Lock 解决了幻读问题。

#### 2.6.3 锁语句

```sql
-- 共享锁（S锁，读锁）
SELECT * FROM `user` WHERE id = 1 LOCK IN SHARE MODE;

-- 排他锁（X锁，写锁）
SELECT * FROM `user` WHERE id = 1 FOR UPDATE;
```

---

## 三、使用场景

### 3.1 OLTP 在线事务处理

**场景**：电商系统订单、支付、库存管理。

```sql
-- 下单扣库存（事务保证一致性）
START TRANSACTION;
-- 1. 检查库存
SELECT stock FROM `product` WHERE id = 1001 FOR UPDATE;
-- 2. 扣减库存
UPDATE `product` SET stock = stock - 1 WHERE id = 1001 AND stock > 0;
-- 3. 创建订单
INSERT INTO `order` (user_id, product_id, amount, status)
VALUES (1, 1001, 99.00, 'unpaid');
-- 4. 提交
COMMIT;
```

### 3.2 读多写少的统计场景

**场景**：日志统计、报表查询。可以采用读写分离 + 索引优化。

```sql
-- 每日活跃用户统计
SELECT
    DATE(login_time) AS login_date,
    COUNT(DISTINCT user_id) AS dau
FROM `login_log`
WHERE login_time >= '2026-01-01'
GROUP BY DATE(login_time)
ORDER BY login_date DESC;

-- 分组取 TopN（每个部门薪资最高的前 3 名）
SELECT * FROM (
    SELECT
        e.*,
        ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rn
    FROM `employee` e
) t
WHERE rn <= 3;
```

### 3.3 树形结构数据查询

**场景**：组织架构、分类层级、评论楼层。

```sql
-- 递归查询所有子部门（MySQL 8.0+ CTE）
WITH RECURSIVE dept_tree AS (
    -- 锚点：起始节点
    SELECT id, name, parent_id, 1 AS level
    FROM `department`
    WHERE id = 1
    UNION ALL
    -- 递归：查询子节点
    SELECT d.id, d.name, d.parent_id, dt.level + 1
    FROM `department` d
    INNER JOIN dept_tree dt ON d.parent_id = dt.id
)
SELECT * FROM dept_tree ORDER BY level, id;
```

### 3.4 数据去重场景

**场景**：清洗重复数据。

```sql
-- 查找重复数据
SELECT username, COUNT(*) AS cnt
FROM `user`
GROUP BY username
HAVING COUNT(*) > 1;

-- 删除重复数据（保留 id 最小的）
DELETE FROM `user`
WHERE id NOT IN (
    SELECT min_id FROM (
        SELECT MIN(id) AS min_id FROM `user` GROUP BY username
    ) t
);
```

### 3.5 分页优化场景

**场景**：深分页性能问题。

```sql
-- 传统分页（深分页性能差）
SELECT * FROM `order` ORDER BY id LIMIT 1000000, 10;

-- 优化方案1：子查询 + 索引覆盖
SELECT * FROM `order` o
INNER JOIN (
    SELECT id FROM `order` ORDER BY id LIMIT 1000000, 10
) t ON o.id = t.id;

-- 优化方案2：记住上一页最后一个 id（游标分页）
SELECT * FROM `order`
WHERE id > 1000000
ORDER BY id LIMIT 10;
```

### 3.6 JSON 数据处理（MySQL 5.7+）

**场景**：存储动态结构数据。

```sql
-- 建表
CREATE TABLE `config` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(50),
    `data` JSON
);

-- 插入 JSON 数据
INSERT INTO `config` (name, data)
VALUES ('site', '{"host": "localhost", "port": 3306, "debug": true}');

-- 查询 JSON 字段
SELECT
    data->'$.host'  AS host,
    data->'$.port'  AS port,
    data->'$.debug' AS debug
FROM `config`
WHERE name = 'site';

-- 修改 JSON 字段
UPDATE `config` SET data = JSON_SET(data, '$.port', 8080) WHERE name = 'site';
```

---

## 四、常见面试题

### 4.1 基础概念类

#### Q1：MySQL 中 MyISAM 与 InnoDB 的区别？

| 对比项 | MyISAM | InnoDB |
|--------|--------|--------|
| 事务支持 | 不支持 | 支持 |
| 锁粒度 | 表级锁 | 行级锁 |
| 外键 | 不支持 | 支持 |
| 崩溃恢复 | 不支持 | 支持（redo log） |
| 全文索引 | 支持 | 5.6+ 支持 |
| 适用场景 | 读密集、统计 | OLTP、高并发 |

#### Q2：什么是 ACID？

- **Atomicity（原子性）**：事务中的操作要么全部成功，要么全部失败回滚。
- **Consistency（一致性）**：事务执行前后，数据库从一个一致状态变为另一个一致状态。
- **Isolation（隔离性）**：并发事务之间相互隔离，互不干扰。
- **Durability（持久性）**：事务提交后，对数据的修改是永久的。

#### Q3：MySQL 默认隔离级别是什么？为什么？

MySQL 默认隔离级别是 **REPEATABLE READ（可重复读）**。

原因：
1. 相比 READ COMMITTED，能避免不可重复读问题；
2. InnoDB 通过 **MVCC（多版本并发控制）** + **Next-Key Lock** 解决了幻读问题；
3. 在保证数据一致性的同时，兼顾了并发性能。

### 4.2 索引类

#### Q4：MySQL 索引底层使用什么数据结构？为什么？

MySQL InnoDB 索引底层使用 **B+ 树**。

原因：
1. **非叶子节点不存储数据**，只存储索引，一个节点能存储更多索引，树更矮，磁盘 IO 次数更少；
2. **所有数据都存储在叶子节点**，且叶子节点之间通过双向链表连接，**范围查询效率高**；
3. 相比 B 树，B+ 树查询性能更稳定（每次都要查到叶子节点）；
4. 相比哈希索引，B+ 树支持范围查询、排序、最左前缀匹配。

#### Q5：什么是聚簇索引和非聚簇索引？

| 类型 | 说明 | InnoDB |
|------|------|--------|
| 聚簇索引 | 数据行和索引存储在一起，叶子节点就是数据行 | 主键索引 |
| 非聚簇索引（二级索引） | 叶子节点存储主键值，需回表查询 | 非主键索引 |

**回表过程**：
1. 通过二级索引找到主键值；
2. 再通过主键索引（聚簇索引）找到完整数据行。

#### Q6：什么是覆盖索引？

当查询的字段全部包含在索引中时，称为**覆盖索引**，无需回表查询。

```sql
-- 假设有联合索引 idx_name_age (username, age)
-- 覆盖索引：直接从索引获取数据，无需回表
SELECT username, age FROM `user` WHERE username = 'zhangsan';
```

在执行计划中 Extra 列会出现 `Using index`。

#### Q7：什么是联合索引的最左前缀原则？

联合索引 `(a, b, c)` 相当于创建了 `(a)`、`(a,b)`、`(a,b,c)` 三个索引，查询时必须从最左列开始使用。

```sql
-- 能命中索引
SELECT * FROM t WHERE a = 1;
SELECT * FROM t WHERE a = 1 AND b = 2;
SELECT * FROM t WHERE a = 1 AND b = 2 AND c = 3;

-- 不能命中索引（缺少最左列 a）
SELECT * FROM t WHERE b = 2;
SELECT * FROM t WHERE c = 3;

-- 部分命中（只能用到 a）
SELECT * FROM t WHERE a = 1 AND c = 3;
```

#### Q8：什么情况下索引会失效？

```sql
-- 1. 对索引列使用函数或表达式
SELECT * FROM `user` WHERE YEAR(create_time) = 2026;  -- 失效
-- 优化：改为范围查询
SELECT * FROM `user` WHERE create_time >= '2026-01-01' AND create_time < '2027-01-01';

-- 2. 隐式类型转换
SELECT * FROM `user` WHERE phone = 13800138000;  -- phone 是 varchar，失效
-- 优化：加引号
SELECT * FROM `user` WHERE phone = '13800138000';

-- 3. LIKE 以 % 开头
SELECT * FROM `user` WHERE username LIKE '%san';  -- 失效
SELECT * FROM `user` WHERE username LIKE 'san%';  -- 有效

-- 4. OR 连接非索引列
SELECT * FROM `user` WHERE age = 25 OR address = '北京';  -- 若 address 无索引则失效

-- 5. 不符合最左前缀原则
SELECT * FROM `user` WHERE age = 25;  -- 若索引是 (status, age) 则失效

-- 6. != 或 <> （可能导致全表扫描）
SELECT * FROM `user` WHERE status != 1;

-- 7. IS NOT NULL（视数据分布而定）
SELECT * FROM `user` WHERE email IS NOT NULL;
```

### 4.3 事务与锁类

#### Q9：MySQL 有哪些锁？

**按粒度分**：
- **表锁**：锁整张表，开销小，并发低。MyISAM 默认使用。
- **行锁**：锁单行数据，开销大，并发高。InnoDB 默认使用。
- **页锁**：锁一页数据，介于表锁和行锁之间。

**按类型分**：
- **共享锁（S锁 / 读锁）**：`LOCK IN SHARE MODE`，多个事务可同时持有。
- **排他锁（X锁 / 写锁）**：`FOR UPDATE`，只有一个事务能持有。

**InnoDB 行锁算法**：
- **Record Lock（记录锁）**：锁住单条记录。
- **Gap Lock（间隙锁）**：锁住记录之间的间隙，防止插入。
- **Next-Key Lock（临键锁）**：Record Lock + Gap Lock，锁住记录及其前面的间隙，是 RR 隔离级别下默认的行锁算法。

#### Q10：什么是 MVCC？

**MVCC（Multi-Version Concurrency Control，多版本并发控制）** 是 InnoDB 在 RC 和 RR 隔离级别下实现非阻塞读的机制。

**核心组件**：
1. **隐藏字段**：每行数据有 `DB_TRX_ID`（事务ID）、`DB_ROLL_PTR`（回滚指针）。
2. **Undo Log（回滚日志）**：存储数据的历史版本，形成版本链。
3. **Read View（读视图）**：事务执行查询时生成的快照，决定能看到哪些版本。

**工作原理**：
- 在 RC 隔离级别下，每次 SELECT 都生成新的 Read View，能看到最新已提交数据；
- 在 RR 隔离级别下，只在第一次 SELECT 时生成 Read View，后续复用，保证可重复读。

#### Q11：如何解决死锁？

**死锁产生原因**：两个或多个事务互相持有对方需要的锁。

**排查方式**：
```sql
-- 查看最近一次死锁信息
SHOW ENGINE INNODB STATUS;

-- 查看当前锁信息（MySQL 5.7）
SELECT * FROM information_schema.INNODB_LOCKS;
SELECT * FROM information_schema.INNODB_LOCK_WAITS;

-- MySQL 8.0
SELECT * FROM performance_schema.data_locks;
SELECT * FROM performance_schema.data_lock_waits;
```

**避免死锁的方法**：
1. 按**固定顺序**访问表和行；
2. 事务**尽量短小**，尽快提交；
3. 降低隔离级别（如使用 RC）；
4. 为等待锁设置超时时间：`SET innodb_lock_wait_timeout = 50;`
5. 使用索引访问数据，避免行锁升级为表锁。

### 4.4 日志类

#### Q12：MySQL 有哪些重要日志？

| 日志 | 作用 | 默认开启 |
|------|------|---------|
| **redo log（重做日志）** | 保证事务持久性，崩溃恢复 | ✅ |
| **undo log（回滚日志）** | 保证事务原子性，支持 MVCC | ✅ |
| **binlog（二进制日志）** | 主从复制、数据恢复 | ❌（需配置） |
| **slow query log（慢查询日志）** | 记录执行慢的 SQL | ❌（需配置） |
| **error log（错误日志）** | 记录启动、运行、停止时的错误 | ✅ |

#### Q13：redo log 和 binlog 的区别？

| 对比项 | redo log | binlog |
|--------|----------|--------|
| 层级 | 存储引擎层（InnoDB） | Server 层 |
| 内容 | 物理日志（数据页修改） | 逻辑日志（SQL 语句/行变更） |
| 写入方式 | 循环写（覆盖） | 追加写（不覆盖） |
| 用途 | 崩溃恢复 | 主从复制、数据恢复 |
| 大小 | 固定大小 | 无上限 |

#### Q14：什么是两阶段提交（2PC）？

为了保证 redo log 和 binlog 的一致性，MySQL 采用**两阶段提交**：

1. **Prepare 阶段**：写入 redo log，状态置为 prepare；
2. **Commit 阶段**：写入 binlog，并将 redo log 状态置为 commit。

崩溃恢复时：
- 若 redo log 已 commit，直接恢复；
- 若 redo log 是 prepare，则检查 binlog 是否完整：
  - 完整 → 提交事务；
  - 不完整 → 回滚事务。

### 4.5 SQL 优化类

#### Q15：如何定位和优化慢 SQL？

**定位方式**：
```sql
-- 1. 开启慢查询日志
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 1;  -- 超过 1 秒的 SQL

-- 2. 查看慢查询日志位置
SHOW VARIABLES LIKE 'slow_query_log_file';

-- 3. 使用 SHOW PROCESSLIST 查看当前执行的 SQL
SHOW PROCESSLIST;
```

**优化步骤**：
1. 使用 `EXPLAIN` 分析执行计划；
2. 检查 `type` 字段，避免 `ALL`（全表扫描）；
3. 检查 `key` 字段，确认是否使用索引；
4. 检查 `rows` 字段，扫描行数是否过多；
5. 检查 `Extra` 字段，是否出现 `Using filesort`、`Using temporary`。

#### Q16：COUNT(*)、COUNT(1)、COUNT(字段) 的区别？

| 写法 | 说明 | 性能 |
|------|------|------|
| `COUNT(*)` | 统计总行数（包括 NULL） | InnoDB 优化过，**推荐使用** |
| `COUNT(1)` | 统计总行数（包括 NULL） | 与 `COUNT(*)` 相当 |
| `COUNT(字段)` | 统计该字段非 NULL 的行数 | 需要读取字段值，性能稍差 |
| `COUNT(主键)` | 统计主键非 NULL 的行数 | 优化器会使用最小索引扫描 |

> **MySQL 8.0.13 起，InnoDB 对 `COUNT(*)` 做了并行扫描优化**。

#### Q17：什么情况下不建议使用索引？

1. **数据量小的表**：全表扫描可能比走索引快；
2. **频繁更新的字段**：索引维护成本高；
3. **字段区分度低**：如性别（男/女），索引效果差；
4. **WHERE 中很少使用的字段**；
5. **大量重复值的字段**。

### 4.6 主从复制与高可用

#### Q18：MySQL 主从复制原理？

**三个步骤**：
1. **Master 写入 binlog**：主库执行事务后，写入 binlog；
2. **Slave 拉取 binlog**：从库的 IO 线程连接主库，拉取 binlog，写入 relay log（中继日志）；
3. **Slave 重放 SQL**：从库的 SQL 线程读取 relay log，重放 SQL，完成数据同步。

```
Master                              Slave
  │                                   │
  │ binlog                            │
  │  │                                │
  │  └──[IO Thread]────拉取──────► relay log
  │                                   │  │
  │                                   │  └──[SQL Thread]──重放──► 数据
```

#### Q19：主从延迟如何解决？

**原因**：从库单线程重放 SQL，速度可能跟不上主库。

**解决方案**：
1. **MySQL 5.7+ 并行复制**：基于组提交（GROUP COMMIT）的多线程复制；
2. **降低主库写入压力**：分库分表；
3. **从库使用更好的硬件**；
4. **业务读策略**：关键业务读主库，非关键读从库；
5. **半同步复制**：主库至少等待一个从库接收 binlog 后再提交。

### 4.7 分库分表

#### Q20：什么时候需要分库分表？

**分表**：单表数据量超过 **1000 万** 或表文件超过 **10GB**。
**分库**：单库并发量大、CPU/IO/内存压力大、单库连接数不足。

#### Q21：分库分表有哪些策略？

**垂直分库**：按业务拆分，如用户库、订单库、商品库。
**垂直分表**：按字段拆分，如将大字段单独拆出。
**水平分库**：按规则（如用户 ID 取模）将数据分散到多个库。
**水平分表**：按规则将数据分散到多个表。

**分片策略**：
- **范围分片**：按 ID 范围，如 0-1000 万一张表；
- **哈希分片**：取模运算 `user_id % N`；
- **一致性哈希**：解决节点扩容问题；
- **地理位置分片**：按地区分片。

#### Q22：分库分表后如何处理跨库查询/分页？

1. **使用中间件**：ShardingSphere、MyCat；
2. **全局表**：字典数据冗余到所有库；
3. **数据冗余**：将关联字段冗余存储；
4. **ElasticSearch**：将数据同步到 ES 做复杂查询；
5. **分页方案**：各分片查询后合并，或使用游标分页。

---

## 五、性能优化建议

### 5.1 索引优化

1. **优先使用覆盖索引**，避免回表；
2. **联合索引遵循最左前缀原则**；
3. **索引列顺序**：区分度高的放前面，等值查询在前，范围查询在后；
4. **避免索引失效场景**；
5. **单表索引数量建议不超过 5 个**，联合索引字段不超过 5 个。

### 5.2 SQL 优化

1. **只查需要的字段**，避免 `SELECT *`；
2. **大表分页使用游标分页**；
3. **UNION ALL 优先于 UNION**；
4. **大批量插入使用批量 INSERT**；
5. **避免在 WHERE 子句中对字段进行函数操作**；
6. **IN 操作符的列表不宜过长**（建议不超过 1000）；
7. **JOIN 时小表驱动大表**。

### 5.3 表设计优化

1. **选择合适的数据类型**：能用 TINYINT 不用 INT，能用 VARCHAR(50) 不用 VARCHAR(255)；
2. **避免使用 NULL**：使用 NOT NULL DEFAULT ''；
3. **时间存储**：用 DATETIME 或 TIMESTAMP；
4. **金额存储**：用 DECIMAL，不用 FLOAT/DOUBLE；
5. **大文本单独拆表**。

### 5.4 配置优化

```ini
# my.cnf 关键参数
[mysqld]
# InnoDB 缓冲池大小（建议物理内存的 50-70%）
innodb_buffer_pool_size = 4G

# 日志文件大小
innodb_log_file_size = 256M

# 刷盘策略（0-每秒刷, 1-每次提交刷, 2-每次提交写OS Cache）
innodb_flush_log_at_trx_commit = 1

# binlog 刷盘策略
sync_binlog = 1

# 连接数
max_connections = 500

# 慢查询
slow_query_log = ON
long_query_time = 1
```

---

## 六、MySQL 与 MongoDB 对比

### 6.1 基本定位对比

| 对比维度 | MySQL | MongoDB |
|---------|-------|---------|
| 数据模型 | **关系型**（二维表，行与列） | **文档型**（BSON/JSON 文档） |
| Schema | 严格 Schema，需预定义表结构 | **动态 Schema**，同一集合中文档结构可不同 |
| 存储格式 | 行存储在 InnoDB 页中 | BSON（Binary JSON）文档存储 |
| 主键 | 自增 ID / UUID | 自动生成 `_id`（ObjectId） |
| 查询语言 | **SQL**（标准结构化查询语言） | **MQL**（MongoDB Query Language），基于 JSON 的查询 |
| 事务支持 | 完整 ACID 事务（InnoDB） | 4.0+ 支持多文档事务，4.2+ 支持分布式事务 |
| 默认端口 | 3306 | 27017 |

### 6.2 数据结构对比

```
MySQL                          MongoDB
─────────────────────          ─────────────────────
数据库 (Database)       →      数据库 (Database)
表 (Table)              →      集合 (Collection)
行 (Row)                →      文档 (Document)
列 (Column)             →      字段 (Field)
索引 (Index)            →      索引 (Index)
JOIN                    →      $lookup（聚合管道）
```

### 6.3 语法对比示例

#### 创建数据

```sql
-- MySQL：建表 + 插入
CREATE TABLE user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    age INT,
    address VARCHAR(100)
);
INSERT INTO user (name, age, address) VALUES ('张三', 25, '北京');
```

```javascript
// MongoDB：无需建表，直接插入
db.user.insertOne({
    name: "张三",
    age: 25,
    address: "北京"
})
```

#### 查询数据

```sql
-- MySQL
SELECT name, age FROM user WHERE age > 20 ORDER BY age DESC;
```

```javascript
// MongoDB
db.user.find(
    { age: { $gt: 20 } },
    { name: 1, age: 1, _id: 0 }
).sort({ age: -1 })
```

#### 更新数据

```sql
-- MySQL
UPDATE user SET age = 26 WHERE name = '张三';
```

```javascript
// MongoDB
db.user.updateOne(
    { name: "张三" },
    { $set: { age: 26 } }
)
```

#### 关联查询

```sql
-- MySQL：JOIN
SELECT u.name, o.order_no
FROM user u
INNER JOIN order o ON u.id = o.user_id;
```

```javascript
// MongoDB：$lookup（聚合管道）
db.user.aggregate([
    {
        $lookup: {
            from: "order",
            localField: "_id",
            foreignField: "user_id",
            as: "orders"
        }
    },
    { $unwind: "$orders" },
    { $project: { name: 1, "orders.order_no": 1 } }
])
```

### 6.4 MySQL 的优势

| 优势 | 说明 |
|------|------|
| **成熟的事务支持** | InnoDB 从诞生起就支持完整的 ACID 事务，适合金融、订单等强一致性场景 |
| **SQL 标准化** | SQL 是通用标准语言，学习成本低，生态工具丰富（BI 报表、ORM、数据迁移等） |
| **复杂查询能力强** | 支持多表 JOIN、子查询、窗口函数、CTE 递归等，适合复杂关联分析 |
| **数据一致性保障** | 严格的 Schema 约束 + 外键约束，数据完整性有保障 |
| **生态成熟** | 备份恢复（mysqldump/xtrabackup）、主从复制、分库分表中间件等非常成熟 |
| **索引优化丰富** | B+ 树索引、覆盖索引、联合索引、全文索引、执行计划分析（EXPLAIN）等 |
| **人才储备充足** | SQL 开发者群体庞大，招聘和维护成本低 |

### 6.5 MongoDB 的优势

| 优势 | 说明 |
|------|------|
| **灵活的 Schema** | 文档结构无需预定义，适合快速迭代、字段频繁变化的业务（如内容管理、用户画像） |
| **横向扩展能力强** | 原生支持 **分片（Sharding）**，水平扩展比 MySQL 分库分表更简单 |
| **高写入吞吐** | 默认 **写关注级别较低**（可配置），写入性能优于 MySQL，适合日志、监控等写密集场景 |
| **内嵌文档模型** | 支持嵌套文档和数组，一个文档可存储一对多关系，**减少 JOIN 操作** |
| **水平扩展简单** | 自带自动分片、副本集，扩容只需加节点 |
| **地理空间查询** | 内置 2dsphere / 2d 索引，原生支持 LBS 地理位置查询 |
| **Change Stream** | 原生支持数据变更订阅（类似 binlog），便于构建实时数据管道 |
| **适合半结构化数据** | 天然适合存储 JSON 结构数据，无需像 MySQL 那样使用 JSON 列 + 函数提取 |

### 6.6 适用场景对比

| 场景 | 推荐 | 原因 |
|------|------|------|
| 电商订单/支付系统 | **MySQL** | 强事务、数据一致性要求高 |
| 用户信息/权限管理 | **MySQL** | 关系明确，Schema 稳定 |
| 内容管理/CMS | **MongoDB** | 文章结构多变，文档模型灵活 |
| 日志/监控数据 | **MongoDB** | 写入量大，Schema 不固定，TTL 索引自动过期 |
| 物联网（IoT） | **MongoDB** | 设备数据格式多样，写入吞吐要求高 |
| 地理位置应用 | **MongoDB** | 原生地理空间索引支持 |
| 金融/银行系统 | **MySQL** | ACID 事务、审计合规要求严格 |
| 商品 catalog / 属性多变 | **MongoDB** | 不同商品属性差异大，文档模型天然适合 |
| 复杂报表/BI 分析 | **MySQL** | SQL 生态与 BI 工具无缝对接 |
| 实时数据管道/事件流 | **MongoDB** | Change Stream + 灵活的文档结构 |

### 6.7 核心差异总结

| 维度 | MySQL | MongoDB |
|------|-------|---------|
| 数据一致性 | ★★★★★（强一致性） | ★★★☆☆（最终一致性，可调） |
| 查询灵活性 | ★★★★★（SQL 功能强大） | ★★★☆☆（聚合管道功能逐步增强） |
| 写入性能 | ★★★☆☆ | ★★★★★ |
| 水平扩展 | ★★☆☆☆（需分库分表中间件） | ★★★★★（原生分片） |
| 事务支持 | ★★★★★（完整 ACID） | ★★★☆☆（4.0+ 支持，性能有损耗） |
| Schema 灵活性 | ★★☆☆☆（严格定义） | ★★★★★（动态 Schema） |
| 生态与工具 | ★★★★★（极其成熟） | ★★★★☆（快速发展中） |
| 学习成本 | ★★★☆☆（SQL 通用） | ★★★★☆（MQL 较直观） |

### 6.8 如何选择？

**选 MySQL 的场景**：
- 业务逻辑复杂，需要多表关联查询
- 对事务和数据一致性有严格要求（金融、订单、库存）
- 团队 SQL 经验丰富，已有成熟的 MySQL 运维体系
- 需要对接 BI 报表、数据分析平台

**选 MongoDB 的场景**：
- 数据结构不固定或频繁变化（快速迭代的互联网产品）
- 写入量大，需要水平扩展（日志、监控、IoT）
- 数据天然具有嵌套/文档结构（商品属性、用户画像）
- 需要地理空间查询或实时数据变更订阅

**混合使用**：很多大型系统会同时使用 MySQL + MongoDB，核心交易数据放 MySQL，灵活/海量数据放 MongoDB，通过数据同步工具（如 Canal、MongoDB Connector）实现数据流转。

---

## 附录：MySQL 版本特性对比

| 版本 | 重要特性 |
|------|---------|
| 5.6 | InnoDB 全文索引、在线 DDL、GTID 复制 |
| 5.7 | JSON 支持、Generated Column、多源复制 |
| 8.0 | 窗口函数、CTE 递归查询、降序索引、不可见索引、角色管理、原子 DDL |
| 8.0.13 | `COUNT(*)` 并行优化、函数索引 |
| 8.0.17 | Clone Plugin、X Protocol 增强 |

---

> **文档说明**：本文档基于 MySQL 8.0 整理，部分语法在低版本可能不支持。面试题答案参考官方文档及社区实践，建议结合实际场景理解。
