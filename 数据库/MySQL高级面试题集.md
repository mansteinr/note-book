# MySQL 高级工程师面试题集

> 本面试题集面向 MySQL 高级工程师岗位，系统覆盖性能优化、大数据量查询解决方案、事务与锁机制、主从复制与读写分离、MySQL 架构原理、高可用运维等六大核心领域。每道题包含问题描述、深度参考答案、实际项目案例及评分要点，兼顾理论深度与工程实践。

---

## 目录

- [第一篇 性能优化专题](#第一篇-性能优化专题)
  - [一、索引优化](#一索引优化)
  - [二、查询语句优化](#二查询语句优化)
  - [三、数据库结构优化](#三数据库结构优化)
- [第二篇 大数据量查询性能问题解决方案](#第二篇-大数据量查询性能问题解决方案)
- [第三篇 事务与锁机制](#第三篇-事务与锁机制)
- [第四篇 主从复制与读写分离](#第四篇-主从复制与读写分离)
- [第五篇 MySQL 架构与原理](#第五篇-mysql-架构与原理)
- [第六篇 高可用与运维](#第六篇-高可用与运维)
- [附录 评分标准与面试指南](#附录-评分标准与面试指南)

---

## 第一篇 性能优化专题

### 一、索引优化

#### Q1.1 为什么 MySQL InnoDB 选择 B+ 树作为索引结构？对比 B 树、哈希索引、红黑树有何优劣？

**问题描述**：请说明 InnoDB 为何采用 B+ 树而非其他数据结构作为索引，并对比分析各结构的适用场景。

**参考答案**：

**1. 各数据结构对比**

| 结构 | 查找复杂度 | 范围查询 | 磁盘 IO | 适用场景 |
| --- | --- | --- | --- | --- |
| 哈希表 | O(1) | ❌ 不支持 | 少 | 等值查询（Memory 引擎） |
| 二叉搜索树 / 红黑树 | O(logN) | ✅ 但树高，IO 多 | 多 | 内存结构 |
| B 树 | O(logN) | ⚠️ 需中序遍历 | 中 | 文件系统 |
| **B+ 树** | O(logN) | ✅ 高效（叶子链表） | 少 | **数据库索引** |

**2. B+ 树相比 B 树的核心优势**

- **非叶子节点不存数据，只存索引键**：一个节点能容纳更多键，树更矮，磁盘 IO 更少
- **所有数据都在叶子节点**：查询性能稳定，每次查询路径长度相同
- **叶子节点通过双向链表相连**：范围查询极高效，只需定位起点然后顺链扫描
- **查询稳定**：B 树可能在非叶子节点命中就返回（快），也可能到叶子（慢）；B+ 树每次都到叶子，性能稳定

**3. 为什么不用红黑树**

- 红黑树是二叉树，树高 = log₂N，百万数据树高约 20，每次查询需 20 次磁盘 IO
- B+ 树是多路树，InnoDB 默认页大小 16KB，假设主键 bigint（8B）+ 指针（6B），一个节点可存 16384/14 ≈ 1170 个键。三层 B+ 树可存 1170³ ≈ 16 亿条记录，查询只需 3 次 IO

**4. 为什么不用哈希索引**

- 哈希索引 O(1) 等值查询极快，但不支持范围查询、排序、最左前缀匹配
- InnoDB 内部有**自适应哈希索引（AHI）**：对热点数据自动建哈希，兼顾两者优点
- Memory 引擎默认哈希索引，适合 KV 场景

**5. InnoDB B+ 树索引细节**

```
                    [非叶子节点：只存键 + 指针]
                          ┌─────────┐
                          │ 10 | 20 │
                          └────┬────┘
              ┌────────────────┼────────────────┐
        ┌─────┴─────┐    ┌─────┴─────┐    ┌─────┴─────┐
        │ 3 | 7     │    │ 13| 17    │    │ 23| 27    │
        └─────┬─────┘    └─────┬─────┘    └─────┬─────┘
              ↓                  ↓                  ↓
  [叶子节点] 3↔7  [叶子节点] 10↔13↔17  [叶子节点] 20↔23↔27
  （存完整行数据，双向链表相连 →）
```

**实际案例**：
- **项目背景**：电商订单表 `orders` 单表 2 亿条，按订单号查询偶发慢（200ms+）
- **问题分析**：原用 UUID 字符串作主键，B+ 树页分裂频繁、索引体积大、缓存命中率低
- **解决方案**：主键改为自增 bigint，并增加 `order_no` 唯一索引；UUID 改为雪花 ID
- **最终效果**：查询降到 2ms，索引体积缩小 40%，Buffer Pool 命中率从 70% 升至 99%

**评分要点**：
- ✅ 准确对比 B 树与 B+ 树差异（非叶子节点不存数据、叶子链表）（必备）
- ✅ 量化分析：三层 B+ 树存 16 亿数据（加分）
- ✅ 提到自适应哈希索引 AHI（加分）
- ✅ 结合实际案例说明主键选择影响（加分）

---

#### Q1.2 聚簇索引与非聚簇索引（二级索引）的区别？什么是回表？如何避免？

**问题描述**：请解释聚簇索引和二级索引的概念，说明回表机制及避免方法。

**参考答案**：

**1. 聚簇索引（Clustered Index）**

- **数据即索引**：叶子节点存储**完整行数据**，索引与数据合一
- 一张表只能有一个聚簇索引，默认是主键
- 若无主键，InnoDB 会选第一个唯一非空索引；若无则生成隐藏 6 字节 `ROW_ID`

**2. 二级索引（Secondary Index / 非聚簇索引）**

- 叶子节点存储的是**索引列值 + 主键值**（而非完整行）
- 一张表可有多个二级索引
- 查询时若需要的列不在索引中，需用主键回表查聚簇索引

**3. 回表（Table Lookup）**

```sql
-- 假设有索引 idx_name(name)
SELECT name, age, address FROM users WHERE name = 'Tom';
```

执行过程：
1. 在 `idx_name` B+ 树中查找 `name='Tom'` → 得到主键 id=5
2. **回表**：用 id=5 去聚簇索引 B+ 树查完整行 → 取 age、address
3. 两次 B+ 树查找，IO 翻倍

**4. 避免回表——覆盖索引**

若查询的列全部包含在索引中，则只需查一次索引树，无需回表：

```sql
-- 建联合索引 idx_name_age(name, age)
SELECT name, age FROM users WHERE name = 'Tom';  -- ✅ 覆盖索引，无需回表
SELECT name, age, address FROM users WHERE name = 'Tom'; -- ❌ address 不在索引，需回表

-- 强制使用覆盖索引：Extra 列显示 Using index
EXPLAIN SELECT name, age FROM users WHERE name = 'Tom';
-- Extra: Using index  → 表示用了覆盖索引
```

**5. 索引下推（Index Condition Pushdown, ICP）**

MySQL 5.6+ 特性，在存储引擎层过滤，减少回表次数：

```sql
-- 联合索引 idx_name_age(name, age)
SELECT * FROM users WHERE name LIKE 'T%' AND age > 20;
```

- **无 ICP**：存储引擎用 `name LIKE 'T%'` 过滤出所有 T 开头记录 → 逐条回表 → Server 层过滤 `age>20`
- **有 ICP**：存储引擎用 `name LIKE 'T%' AND age>20` 同时过滤 → 只对满足条件的回表
- EXPLAIN Extra 显示 `Using index condition`

**实际案例**：
- **项目背景**：用户列表查询 `SELECT id,name,phone FROM users WHERE name LIKE '张%' AND status=1`，1000 万数据查询 3 秒
- **问题分析**：`idx_name(name)` 索引下 name 命中 50 万条，逐条回表查 status 过滤，回表次数爆炸
- **解决方案**：建联合索引 `idx_name_status(name, status)`，并让查询列覆盖 `id,name,phone` → `idx_name_status_phone(name, status, phone)`
- **最终效果**：覆盖索引 + ICP，查询降到 50ms，回表从 50 万次降到 0

**评分要点**：
- ✅ 聚簇索引 vs 二级索引叶子节点存储内容差异（必备）
- ✅ 回表机制说明（必备）
- ✅ 覆盖索引避免回表（必备）
- ✅ 索引下推 ICP 原理（加分）
- ✅ EXPLAIN 中 Extra 字段含义（加分）

---

#### Q1.3 联合索引的最左前缀原则是什么？请分析以下查询哪些能命中索引 `idx_a_b_c(a, b, c)`。

**问题描述**：给定联合索引 `idx_a_b_c(a, b, c)`，判断各查询是否走索引并解释原因。

**参考答案**：

**最左前缀原则**：联合索引按字段顺序建立 B+ 树，查询必须从最左列开始连续使用，才能命中索引。

```sql
-- 索引：idx_a_b_c(a, b, c)
-- B+ 树先按 a 排序，a 相同按 b 排序，b 相同按 c 排序

-- ✅ 走索引
WHERE a = 1                       -- 走 a
WHERE a = 1 AND b = 2             -- 走 a, b
WHERE a = 1 AND b = 2 AND c = 3   -- 走 a, b, c
WHERE a = 1 AND c = 3             -- 走 a（c 无法用索引，但 a 能用）
WHERE a = 1 AND b > 2 AND c = 3   -- 走 a, b（b 是范围，c 无法用）

-- ❌ 不走索引
WHERE b = 2                       -- 缺少最左列 a
WHERE c = 3                       -- 缺少 a, b
WHERE b = 2 AND c = 3             -- 缺少 a
```

**关键细节**：

1. **范围查询后的列无法用索引**：`a = 1 AND b > 2 AND c = 3`，b 用了范围，c 无法用索引（因为 b 范围内 c 无序）

2. **MySQL 优化器会自动调整顺序**：
   ```sql
   WHERE b = 2 AND a = 1  -- 等价于 a = 1 AND b = 2，优化器自动调整，✅ 走索引
   ```

3. **LIKE 的最左前缀**：
   ```sql
   WHERE a LIKE 'abc%'   -- ✅ 走索引（前缀匹配）
   WHERE a LIKE '%abc'   -- ❌ 不走索引（前缀通配）
   WHERE a LIKE '%abc%'  -- ❌ 不走索引
   ```

4. **索引列上做运算/函数会导致失效**：
   ```sql
   WHERE YEAR(create_time) = 2024       -- ❌ 函数，失效
   WHERE create_time >= '2024-01-01'    -- ✅ 改为范围
   WHERE a + 1 = 2                      -- ❌ 运算，失效
   WHERE a = 1                          -- ✅ 改为等值
   ```

**5. 索引设计原则（建联合索引的字段顺序）**

- **等值查询的列放前面**：过滤性强的优先
- **范围查询的列放后面**：避免范围查询截断后续索引
- **排序列放最后**：可利用索引有序性避免 filesort

```sql
-- 业务：WHERE status=1 AND create_time > '2024-01-01' ORDER BY user_id
-- 推荐索引：idx_status_time_user(status, create_time, user_id)
```

**实际案例**：
- **项目背景**：订单查询 `WHERE shop_id=? AND status=? AND create_time BETWEEN ? AND ? ORDER BY id` 慢
- **错误索引**：`idx_create_time(create_time)` + `idx_shop(shop_id)`，优化器只选一个
- **正确索引**：`idx_shop_status_time(shop_id, status, create_time)`，三个条件都走索引，且利用索引有序避免 filesort
- **最终效果**：从 1.5s 降到 10ms

**评分要点**：
- ✅ 最左前缀原则准确说明（必备）
- ✅ 范围查询截断后续索引（必备）
- ✅ 优化器自动调整等值条件顺序（加分）
- ✅ LIKE、函数、运算导致失效（必备）
- ✅ 索引设计原则：等值在前、范围在后、排序最后（加分）

---

#### Q1.4 请列举常见的索引失效场景，并说明如何排查。

**问题描述**：哪些 SQL 写法会导致索引失效？如何用 EXPLAIN 排查？

**参考答案**：

**常见索引失效场景**：

| 场景 | 示例 | 原因 | 解决方案 |
| --- | --- | --- | --- |
| **函数运算** | `YEAR(time)=2024` | 索引存原值，函数后无法匹配 | 改范围 `time >= '2024-01-01'` |
| **隐式类型转换** | `WHERE phone=13800138000`（phone 是 varchar） | 转换为字符串比较，全表扫 | 加引号 `phone='13800138000'` |
| **联合索引非最左** | `idx(a,b)` 查 `b=1` | 缺最左列 | 调整查询或建独立索引 |
| **LIKE 前缀通配** | `LIKE '%abc'` | B+ 树无法定位 | 用全文索引或 ES |
| **OR 两边非全索引** | `a=1 OR b=2`（b 无索引） | 必须全表扫 b | 给 b 加索引或改 UNION |
| **!= / NOT IN** | `WHERE status != 1` | 选择性差，优化器放弃索引 | 改为 IN 或反向 |
| **IS NOT NULL** | `WHERE a IS NOT NULL` | 选择性差 | 视数据分布 |
| **计算** | `a + 1 = 2` | 同函数 | 改 `a = 1` |
| **字符集不一致** | JOIN 两表字符集不同 | 隐式转换 | 统一字符集 |
| **优化器认为全表扫更快** | 索引选择性差 | 大表 30%+ 命中 | 强制 FORCE INDEX |

**EXPLAIN 排查关键字段**：

```sql
EXPLAIN SELECT * FROM users WHERE phone = 13800138000;
```

| 字段 | 含义 | 关注点 |
| --- | --- | --- |
| **type** | 访问类型 | system > const > eq_ref > ref > range > index > ALL（ALL 最差，全表扫） |
| **key** | 实际用的索引 | NULL 表示没用索引 |
| **rows** | 预估扫描行数 | 越小越好 |
| **Extra** | 额外信息 | Using index（覆盖索引好）、Using filesort（差）、Using temporary（差） |
| **possible_keys** | 可能用的索引 | 有可能但没用上需排查 |
| **key_len** | 索引使用长度 | 判断联合索引用了几个字段 |

**key_len 计算示例**（判断联合索引用了几列）：

```sql
-- idx_a_b_c(a INT, b VARCHAR(20), c INT) utf8mb4
-- a: 4字节, b: 20*4+2=82字节, c: 4字节
EXPLAIN SELECT * FROM t WHERE a=1 AND b='x' AND c=1;
-- key_len = 4 + 82 + 4 = 90 → 三列都用上了

EXPLAIN SELECT * FROM t WHERE a=1;
-- key_len = 4 → 只用了 a
```

**隐式类型转换经典坑**：

```sql
-- phone 是 varchar(11)
SELECT * FROM users WHERE phone = 13800138000;  -- ❌ 传入数字，MySQL 把每行 phone 转数字比较，全表扫
SELECT * FROM users WHERE phone = '13800138000'; -- ✅ 字符串比较，走索引
```

**实际案例**：
- **项目背景**：用户登录接口偶发慢，`SELECT * FROM users WHERE phone=13800138000` 在 500 万表上 8 秒
- **排查过程**：EXPLAIN 显示 type=ALL 全表扫，发现 Java 代码传入 Long 而非 String
- **解决方案**：DAO 层参数类型改为 String
- **最终效果**：查询降到 1ms

**评分要点**：
- ✅ 列举 6+ 种失效场景（必备）
- ✅ EXPLAIN 各字段含义（必备）
- ✅ key_len 判断联合索引用了几列（加分）
- ✅ 隐式类型转换陷阱（必备）
- ✅ FORCE INDEX 强制索引（加分）

---

#### Q1.5 如何分析一条慢 SQL？请给出完整的优化流程。

**问题描述**：线上有一条慢 SQL，请描述你的优化方法论。

**参考答案**：

**完整优化流程**：

```
1. 开启慢查询日志 → 2. EXPLAIN 分析 → 3. 定位瓶颈 → 4. 优化 → 5. 验证
```

**1. 开启慢查询日志**

```sql
-- 临时开启
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 1;  -- 超过 1 秒记录
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';

-- 慢日志分析工具
mysqldumpslow -s t -t 10 /var/log/mysql/slow.log  -- 按时间取前10条
pt-query-digest /var/log/mysql/slow.log           -- Percona 工具更强大
```

**2. EXPLAIN 分析执行计划**

```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 100 AND status = 1 ORDER BY create_time DESC LIMIT 20;
```

重点关注：
- **type=ALL**：全表扫描，必须优化
- **rows 过大**：扫描行数多
- **Extra: Using filesort**：额外排序，需优化
- **Extra: Using temporary**：用了临时表，需优化
- **key=NULL**：没用索引

**3. 定位瓶颈类型**

| 瓶颈 | 现象 | 优化方向 |
| --- | --- | --- |
| 无索引 | type=ALL, rows=全表 | 加合适索引 |
| 索引失效 | possible_keys 有但 key=NULL | 修正 SQL 写法 |
| 回表过多 | rows 大但扫描少 | 覆盖索引 |
| 排序慢 | Using filesort | 索引有序或 limit |
| 临时表 | Using temporary | 优化 GROUP BY |
| 锁等待 | Show processlist 有 Waiting | 优化事务、加索引 |

**4. 优化手段（按优先级）**

```sql
-- ① 加索引（最有效）
ALTER TABLE orders ADD INDEX idx_user_status_time(user_id, status, create_time);

-- ② 覆盖索引避免回表
SELECT user_id, status, create_time FROM orders WHERE user_id=100;  -- 覆盖索引

-- ③ 深分页优化
-- 慢：SELECT * FROM orders ORDER BY id LIMIT 1000000, 20;
-- 快：SELECT * FROM orders WHERE id > 上次最大id ORDER BY id LIMIT 20;

-- ④ 只查需要的列（避免 SELECT *）
SELECT id, order_no FROM orders WHERE user_id=100;

-- ⑤ JOIN 优化：小表驱动大表
SELECT * FROM small_table s JOIN big_table b ON s.id = b.sid WHERE s.status=1;
```

**5. 验证优化效果**

```sql
-- 开启 profiling 看各阶段耗时
SET profiling = 1;
SELECT ...;
SHOW PROFILE;
-- 或
SHOW PROFILE FOR QUERY 1;
```

**实际案例**：
- **项目背景**：报表系统一条统计 SQL 执行 40 秒，影响日报产出
- **原 SQL**：3 表 JOIN + GROUP BY + 子查询 + LIKE '%关键词%'
- **排查过程**：
  1. EXPLAIN 发现驱动表选错（大表驱动小表），type=ALL，Using temporary + Using filesort
  2. LIKE '%关键词%' 导致索引失效
  3. 子查询未走索引
- **优化方案**：
  1. STRAIGHT_JOIN 强制 JOIN 顺序，小表驱动
  2. LIKE 改前端搜索 + ES
  3. 子查询改为 JOIN
  4. 加联合索引覆盖 GROUP BY
- **最终效果**：40s → 0.8s

**评分要点**：
- ✅ 完整流程：慢日志 → EXPLAIN → 定位 → 优化 → 验证（必备）
- ✅ EXPLAIN 关键字段解读（必备）
- ✅ 至少 3 种优化手段（必备）
- ✅ 深分页、JOIN 顺序等具体技巧（加分）
- ✅ 真实案例佐证（加分）

---

#### Q1.6 唯一索引与普通索引在性能上有何差异？如何选择？change buffer 是什么？

**问题描述**：唯一索引和普通索引在查询和写入性能上有何不同？change buffer 机制是什么？

**参考答案**：

**1. 查询性能差异**

- **普通索引**：找到第一条满足条件的记录后，还需继续查找下一条判断是否结束（因为可能有重复）
- **唯一索引**：找到一条就停止（因为唯一）

但实际上差异极小，因为 InnoDB 是按页读取，第一条和第二条记录通常在同一页，多读一次的代价几乎为零。

**2. 写入性能差异（关键）**

- **唯一索引**：写入前必须检查唯一性约束 → 必须将数据页读入内存 → **不能用 change buffer**
- **普通索引**：写入时若数据页不在内存，可直接先写 change buffer → 后台合并 → **写入更快**

**3. Change Buffer 机制**

- **作用**：对普通索引的写操作（INSERT/UPDATE/DELETE），若目标数据页不在 Buffer Pool，不立即读磁盘，而是先记录到 change buffer，待下次读取或后台合并时再应用
- **目的**：减少随机磁盘 IO，提升写入性能
- **限制**：仅对普通索引有效，唯一索引不适用（需即时校验）
- **配置**：`innodb_change_buffer_max_size`（默认 25%，占 Buffer Pool 最大比例）

```
写入流程对比：
唯一索引：写操作 → 读磁盘页到内存 → 检查唯一性 → 写入        （1次随机IO）
普通索引：写操作 → 数据页不在内存？→ 写 change buffer → 完成  （0次随机IO，后台合并）
```

**4. 选择建议**

| 场景 | 推荐 | 原因 |
| --- | --- | --- |
| 业务上必须唯一（手机号、身份证） | 唯一索引 | 数据正确性优先 |
| 写多读少 + 可接受重复 | 普通索引 | 利用 change buffer 提升写性能 |
| 写后立即读 | 普通索引优势小 | change buffer 立即 merge，无收益 |
| 历史数据归档表 | 普通索引 | 写多读少，change buffer 收益大 |

**实际案例**：
- **项目背景**：日志表每日写入 5000 万条，原所有字段都建唯一索引防重
- **问题**：写入慢，IO 高，change buffer 失效
- **优化**：业务层用 Redis 去重，DB 只保留普通索引；唯一约束改为业务逻辑保证
- **最终效果**：写入吞吐提升 3 倍，IO 下降 50%

**评分要点**：
- ✅ 查询差异小、写入差异大（必备）
- ✅ change buffer 原理：仅普通索引可用（必备）
- ✅ 唯一索引需即时校验所以不能用 change buffer（核心）
- ✅ 写多读少场景的选择建议（加分）

---

### 二、查询语句优化

#### Q1.7 MySQL 的 JOIN 有哪些类型？Nested Loop Join、Block Nested Loop、Hash Join 的原理和适用场景？

**问题描述**：请说明 MySQL JOIN 的实现算法及优化策略。

**参考答案**：

**1. JOIN 算法**

| 算法 | 版本 | 原理 | 适用场景 |
| --- | --- | --- | --- |
| **Simple Nested Loop Join (SNLJ)** | 朴素 | 驱动表每行去被驱动表全表扫 | 实际不用（太慢） |
| **Index Nested Loop Join (INLJ)** | 经典 | 被驱动表 JOIN 列有索引，用索引查找 | 被驱动表有索引（最常用） |
| **Block Nested Loop Join (BNLJ)** | 5.6及之前 | 把驱动表数据分批放 join_buffer，减少被驱动表扫描次数 | 被驱动表无索引 |
| **Hash Join** | 8.0.18+ | 构建端建哈希表，探测端哈希查找 | 等值 JOIN 无索引（替代 BNLJ） |

**2. Index Nested Loop Join（最常用）**

```sql
SELECT * FROM t1 JOIN t2 ON t1.id = t2.tid WHERE t1.age > 20;
-- 假设 t2.tid 有索引，t1 是驱动表
```

执行过程：
1. 遍历 t1 满足条件的行（逐行）
2. 对每行用 `t1.id` 去 t2 的 `idx_tid` 索引树查找（B+ 树，快）
3. 命中后回表取 t2 完整行

**关键**：被驱动表 JOIN 列必须有索引，否则退化为 BNLJ。

**3. Block Nested Loop Join**

```sql
-- t2.tid 无索引
SELECT * FROM t1 JOIN t2 ON t1.id = t2.tid;
```

执行过程：
1. 把 t1（驱动表）的一批数据放入 `join_buffer`
2. 扫描 t2 全表，对每行与 join_buffer 中所有行比较
3. t1 分批处理，t2 只需全表扫一次（而不是 t1 每行扫一次 t2）

**优化**：调大 `join_buffer_size` 让驱动表全部放入，被驱动表只扫一次。

**4. Hash Join（MySQL 8.0+）**

- 构建端（小表）建内存哈希表
- 探测端（大表）逐行哈希查找
- 比 BNLJ 快很多，O(N) 复杂度
- MySQL 8.0.20 起完全替代 BNLJ

**5. JOIN 优化原则**

- **小表驱动大表**：让行数少的表做驱动表，减少循环次数
- **被驱动表 JOIN 列加索引**：转化为 INLJ
- **控制 join_buffer_size**：BNLJ 时调大
- **减少 JOIN 表数量**：拆分子查询或冗余字段
- **STRAIGHT_JOIN 强制顺序**：优化器选错时强制

```sql
-- 强制 t1 驱动 t2
SELECT STRAIGHT_JOIN * FROM t1 JOIN t2 ON t1.id = t2.tid;
```

**实际案例**：
- **项目背景**：订单 JOIN 用户 JOIN 商品三表查询，1.2 亿订单，慢 15 秒
- **问题**：用户表 JOIN 列无索引，退化为 BNLJ，join_buffer 不足导致用户表被扫多次
- **优化**：用户表 JOIN 列加索引 + 调大 join_buffer_size + 拆分冗余商品名到订单表
- **最终效果**：15s → 300ms

**评分要点**：
- ✅ 三种 JOIN 算法原理（必备）
- ✅ 小表驱动大表原则（必备）
- ✅ 被驱动表需有索引（必备）
- ✅ Hash Join 是 8.0+ 新特性替代 BNLJ（加分）
- ✅ STRAIGHT_JOIN 强制顺序（加分）

---

#### Q1.8 深分页查询（LIMIT 1000000, 20）为什么慢？有哪些优化方案？

**问题描述**：`LIMIT 1000000, 20` 查询很慢，请分析原因并给出优化方案。

**参考答案**：

**1. 慢的原因**

```sql
SELECT * FROM orders ORDER BY create_time DESC LIMIT 1000000, 20;
```

MySQL 需要扫描前 1000020 条记录，丢弃前 100 万条，返回后 20 条。虽然只返回 20 条，但**扫描和排序成本是 100 万+**，且 100 万条的回表 IO 巨大。

**2. 优化方案**

**方案一：游标分页（推荐，适合连续翻页）**

利用主键或唯一索引的有序性，记住上一页最后一条的 ID：

```sql
-- 第一页
SELECT * FROM orders WHERE id > 0 ORDER BY id ASC LIMIT 20;
-- 假设最后一条 id = 1000020

-- 第二页（用上一页最后的 id）
SELECT * FROM orders WHERE id > 1000020 ORDER BY id ASC LIMIT 20;
```

优点：每次只扫 20 条，无论翻到第几页都 O(1)。
缺点：不支持跳页（只能上一页/下一页）。

**方案二：子查询延迟关联（推荐，支持跳页）**

先通过覆盖索引查出主键，再关联原表：

```sql
-- 慢：SELECT * FROM orders ORDER BY create_time DESC LIMIT 1000000, 20;

-- 快：先用索引查出 id，再 JOIN 回表
SELECT * FROM orders o
INNER JOIN (
    SELECT id FROM orders ORDER BY create_time DESC LIMIT 1000000, 20
) t ON o.id = t.id;
```

子查询走覆盖索引（只查 id），不回表，扫描 100 万但全是索引 IO，快很多；最后只对 20 条回表。

**方案三： Between...And（已知边界）**

```sql
-- 假设知道每页起止 id
SELECT * FROM orders WHERE id BETWEEN 1000001 AND 1000020;
```

**方案四：产品层规避**

- 限制最大翻页数（如只允许看前 100 页）
- 超过用搜索/筛选代替翻页
- 大数据导出用异步任务

**方案五：缓存热门页**

前几页缓存到 Redis，避免重复查询。

**实际案例**：
- **项目背景**：运营后台订单列表翻到 5 万页后超时（10s+）
- **优化方案**：子查询延迟关联 + 限制最大翻页 1 万页 + 超过用筛选条件
- **最终效果**：10s → 50ms，且产品上引导用户用筛选而非翻页

**评分要点**：
- ✅ 准确说明慢的原因：扫描+回表成本（必备）
- ✅ 游标分页方案（必备）
- ✅ 子查询延迟关联方案（必备）
- ✅ 各方案优缺点对比（加分）
- ✅ 产品层规避思路（加分）

---

#### Q1.9 ORDER BY 和 GROUP BY 如何优化？Using filesort 和 Using temporary 如何消除？

**问题描述**：请说明排序和分组如何利用索引优化，filesort 和 temporary 产生的原因及消除方法。

**参考答案**：

**1. ORDER BY 利用索引**

B+ 树索引本身有序，若 ORDER BY 的列与索引顺序一致，可避免 filesort：

```sql
-- 索引 idx_a_b_c(a, b, c)

-- ✅ 无 filesort（索引有序）
SELECT * FROM t WHERE a=1 ORDER BY b, c;       -- 等值 a 后，b,c 在索引中有序
SELECT * FROM t WHERE a=1 AND b=2 ORDER BY c;   -- 等值 a,b 后 c 有序
SELECT * FROM t WHERE a=1 ORDER BY b;           -- a 等值后 b 有序

-- ❌ 产生 filesort
SELECT * FROM t WHERE a>1 ORDER BY b;           -- a 是范围，b 在范围内无序
SELECT * FROM t WHERE a=1 ORDER BY c;           -- 跳过 b，c 无序
SELECT * FROM t WHERE a=1 ORDER BY b DESC, c ASC; -- 排序方向不一致
```

**filesort 排序算法**：
- **单路排序**：一次取出所有字段在内存排（sort_buffer），数据小用
- **双路排序**：只取排序字段+行指针排，排完再回表取数据，数据大用
- 若数据超大，分块排序后归并（临时文件）

**2. GROUP BY 优化**

GROUP BY 本质是先排序后分组，同样可利用索引：

```sql
-- ✅ 无 temporary（索引有序，直接分组）
SELECT a, COUNT(*) FROM t WHERE a=1 GROUP BY b;

-- ❌ 产生 temporary（无序需建临时表分组）
SELECT a, COUNT(*) FROM t GROUP BY b;  -- 缺 a 条件
```

**3. Using filesort 消除方法**

- ORDER BY 列加联合索引，顺序一致
- WHERE 等值过滤 + ORDER BY 同索引
- 排序方向一致（全 ASC 或全 DESC）
- 限制结果集（LIMIT 减少 sort 数据量）

**4. Using temporary 消除方法**

- GROUP BY 列走索引
- 避免 DISTINCT（本质也是分组）
- 避免 UNION（用 UNION ALL）
- 减少子查询

**5. 排序方向不一致的坑**

```sql
-- 索引 idx_a_b(a, b) 默认 ASC
SELECT * FROM t WHERE a=1 ORDER BY b DESC;  -- ✅ MySQL 8.0 支持降序索引
-- MySQL 5.7 需建索引时指定 DESC：INDEX(a, b DESC)
```

**实际案例**：
- **项目背景**：排行榜 `SELECT user_id, SUM(score) FROM scores GROUP BY user_id ORDER BY SUM(score) DESC LIMIT 100`
- **问题**：1000 万行，GROUP BY 产生 temporary，ORDER BY 产生 filesort，耗时 8 秒
- **优化**：
  1. 离线预计算：每小时跑一次统计写入 `rank_cache` 表
  2. 查询直接读缓存表 `SELECT * FROM rank_cache ORDER BY score DESC LIMIT 100`
- **最终效果**：8s → 5ms

**评分要点**：
- ✅ ORDER BY 利用索引有序避免 filesort（必备）
- ✅ 范围查询导致后续列无序（必备）
- ✅ GROUP BY 产生 temporary 原因（必备）
- ✅ filesort 单路/双路算法（加分）
- ✅ 降序索引 MySQL 8.0 特性（加分）

---

### 三、数据库结构优化

#### Q1.10 数据库表设计有哪些最佳实践？字段类型如何选择？

**问题描述**：请总结 MySQL 表结构和字段设计的最佳实践。

**参考答案**：

**1. 字段类型选择原则**

| 场景 | 推荐 | 避免 | 原因 |
| --- | --- | --- | --- |
| 主键 | BIGINT UNSIGNED 自增 | UUID 字符串 | 自增有序，页分裂少 |
| 短文本 | VARCHAR(n) | TEXT | TEXT 单独存溢出页 |
| 长文本 | TEXT / LONGTEXT | VARCHAR(10000) | 超长 varchar 浪费 |
| 状态/枚举 | TINYINT | VARCHAR | 数值更省空间 |
| 布尔 | TINYINT(1) | BOOLEAN | 一致性 |
| 金额 | DECIMAL(18,2) | FLOAT/DOUBLE | 浮点精度问题 |
| 时间 | DATETIME / TIMESTAMP | VARCHAR | 时间计算方便 |
| IP | INT UNSIGNED (INET_ATON) | VARCHAR | 省空间可计算 |
| 大对象 | 外部存储 (OSS) | BLOB | DB 不适合存大文件 |

**2. 表设计原则**

- **适当反范式**：高频 JOIN 的字段冗余到一张表，用空间换时间
- **垂直拆分**：将大字段（TEXT/BLOB）拆到扩展表，减少主表体积
- **预留字段慎用**：无类型约束的预留字段是反模式
- **NOT NULL + 默认值**：NULL 影响索引、占空间、计算需 IS NULL
- **字符集统一 utf8mb4**：支持 emoji，避免乱码
- **时间字段统一 UTC**：避免时区问题

**3. 主键设计**

```sql
-- ✅ 推荐：自增 bigint
id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY

-- ⚠️ 分布式场景：雪花 ID
id BIGINT UNSIGNED NOT NULL PRIMARY KEY  -- 应用层生成

-- ❌ 避免：UUID 字符串作主键
id VARCHAR(36) PRIMARY KEY  -- 随机插入导致页分裂、索引体积大
```

**UUID 作主键的问题**：
- 随机性导致插入时 B+ 树页分裂频繁
- 36 字符体积大，二级索引存主键，所有索引都变大
- Buffer Pool 命中率低（随机访问）

**4. 索引设计原则**

- 单表索引数建议 5 个以内
- 联合索引优先于多个单列索引
- 选择性高的列建索引（区分度 = 不同值/总行数）
- 频繁更新的列少建索引（维护成本）
- 长字符串用前缀索引 `INDEX(name(20))`

**实际案例**：
- **项目背景**：用户表 80 个字段（含 5 个 TEXT），单表 1.2 GB，查询慢
- **优化**：
  1. 垂直拆分：5 个 TEXT 拆到 `user_ext` 表
  2. 主键从 UUID 改雪花 ID
  3. 高频查询字段冗余（如 last_login_ip 从日志表冗余）
- **最终效果**：主表缩到 300MB，查询提升 5 倍

**评分要点**：
- ✅ 字段类型选择合理（金额 DECIMAL、IP 用 INT）（必备）
- ✅ NOT NULL、utf8mb4、UTC 时间（必备）
- ✅ UUID 主键的问题（必备）
- ✅ 垂直拆分、反范式（加分）
- ✅ 前缀索引、选择性（加分）

---

#### Q1.11 什么是分区表？适用于什么场景？有什么限制？

**问题描述**：请说明 MySQL 分区表的原理、类型、适用场景及限制。

**参考答案**：

**1. 分区表概念**

分区表是将一张逻辑表在物理存储上拆分为多个分区文件，对应用透明。MySQL 负责分区路由，SQL 无需感知。

```
逻辑表 orders
  ├── 分区 p2023 (物理文件 ibd)
  ├── 分区 p2024 (物理文件 ibd)
  └── 分区 p2025 (物理文件 ibd)
```

**2. 分区类型**

| 类型 | 说明 | 示例 |
| --- | --- | --- |
| **RANGE** | 范围分区（最常用） | 按时间：`< 2024`, `2024-2025`, `>= 2025` |
| **LIST** | 列表分区 | 按地区：北京/上海/广州 |
| **HASH** | 哈希分区 | `HASH(user_id) PARTITIONS 4` |
| **KEY** | 类似 HASH 但用 MySQL 内置哈希 | `KEY(id) PARTITIONS 4` |

**3. RANGE 分区示例（时间维度，最常见）**

```sql
CREATE TABLE orders (
    id BIGINT NOT NULL AUTO_INCREMENT,
    order_no VARCHAR(32),
    create_time DATETIME NOT NULL,
    amount DECIMAL(10,2),
    PRIMARY KEY (id, create_time)  -- 分区键必须是主键一部分
)
PARTITION BY RANGE (TO_DAYS(create_time)) (
    PARTITION p2023 VALUES LESS THAN (TO_DAYS('2024-01-01')),
    PARTITION p2024 VALUES LESS THAN (TO_DAYS('2025-01-01')),
    PARTITION p2025 VALUES LESS THAN (TO_DAYS('2026-01-01')),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);

-- 查询时带分区键，触发分区裁剪
SELECT * FROM orders WHERE create_time BETWEEN '2024-06-01' AND '2024-06-30';
-- 只扫 p2024 分区，不扫其他
```

**4. 适用场景**

- **时间序列数据**：日志、订单按月/年分区，老数据归档只需 DROP 分区（瞬间完成）
- **分区裁剪**：查询带分区键，只扫目标分区
- **数据生命周期管理**：DROP PARTITION 比 DELETE 快几个数量级

**5. 限制**

- 分区键必须是主键/唯一键的一部分
- 最多 1024 个分区
- 跨分区查询无优势（甚至更慢）
- 不支持外键
- 分区表上的唯一索引必须包含分区键

**6. 分区表 vs 分表**

| 维度 | 分区表 | 分库分表 |
| --- | --- | --- |
| 透明度 | 对应用透明 | 需中间件路由 |
| 跨分区事务 | 支持（单机） | 分布式事务复杂 |
| 扩展性 | 单机上限 | 可水平扩展 |
| 运维 | 简单 | 复杂 |
| 适用 | 中等数据量、时间维度 | 海量数据、需扩展 |

**实际案例**：
- **项目背景**：订单表 3 亿条，按月查询 + 每年归档 1 年前数据
- **问题**：DELETE 老数据耗时几小时，锁表影响业务
- **方案**：按月 RANGE 分区，归档改 `ALTER TABLE orders DROP PARTITION p2022`
- **最终效果**：归档从 3 小时降到秒级，查询带时间条件提速 10 倍

**评分要点**：
- ✅ 四种分区类型（必备）
- ✅ 分区裁剪原理（必备）
- ✅ 分区键必须是主键一部分（必备）
- ✅ DROP PARTITION 归档优势（必备）
- ✅ 分区表 vs 分库分表对比（加分）

---

## 第二篇 大数据量查询性能问题解决方案

> 本篇系统回答"数据量大了查询慢怎么办"这一高频面试题，给出从定位到解决的完整方法论。

### Q2.1 当一张表数据量到千万级查询变慢，你的排查和优化思路是什么？

**问题描述**：线上 MySQL 单表 5000 万条数据，查询越来越慢，请给出完整的解决思路。

**参考答案**：

**完整排查优化方法论**：

```
第1步：定位慢查询 → 第2步：分析执行计划 → 第3步：分层优化 → 第4步：架构升级
```

**第 1 步：定位慢查询**

```sql
-- 开启慢查询日志
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 1;

-- 用 pt-query-digest 分析 TOP N 慢 SQL
pt-query-digest slow.log | head -50
```

**第 2 步：分析执行计划**

```sql
EXPLAIN SELECT ...;
-- 看 type、key、rows、Extra
```

**第 3 步：分层优化（由易到难）**

| 层级 | 手段 | 见效快慢 |
| --- | --- | --- |
| **SQL 层** | 加索引、改写 SQL、避免回表 | 立竿见影 |
| **表结构层** | 垂直拆分、字段优化、分区表 | 中等 |
| **缓存层** | Redis 缓存热点、本地缓存 | 快 |
| **架构层** | 读写分离、分库分表 | 慢但治本 |
| **业务层** | 异步、预计算、降级 | 快 |

**具体优化手段**：

1. **索引优化**（参考第一篇）：加联合索引、覆盖索引、修正失效 SQL
2. **SQL 重构**：
   - `SELECT *` → 只查需要的列
   - 子查询 → JOIN
   - OR → UNION ALL
   - 深分页 → 游标/延迟关联
3. **分区表**：按时间分区，分区裁剪 + 快速归档
4. **冷热分离**：热数据近期表，冷数据归档表
5. **缓存**：Redis 缓存查询结果，DB 只作兜底
6. **读写分离**：读走从库，减轻主库压力
7. **分库分表**：水平拆分到多库多表（终极方案）
8. **预计算**：复杂统计离线跑，结果写汇总表
9. **引入搜索引擎**：复杂搜索走 ES，DB 只存 ID

**第 4 步：架构升级（数据量持续增长时）**

```
单表 → 分区表 → 读写分离 → 垂直分库 → 水平分表 → 引入 ES/ClickHouse
```

**实际案例**：
- **项目背景**：电商订单表 8000 万条，用户查询"我的订单"列表 P99 3 秒
- **排查过程**：
  1. 慢 SQL：`SELECT * FROM orders WHERE user_id=? ORDER BY create_time DESC LIMIT 20`
  2. EXPLAIN：type=ALL 全表扫，user_id 无索引
  3. 加索引 `idx_user_time(user_id, create_time)` 后 3s → 50ms
- **后续演进**：数据涨到 3 亿后单索引不够，按 user_id 哈希分 16 表 + 冷热分离
- **最终效果**：3 亿数据查询稳定 30ms

**评分要点**：
- ✅ 完整方法论：定位→分析→优化→架构（必备）
- ✅ 分层优化思路（SQL/表结构/缓存/架构/业务）（必备）
- ✅ 给出架构演进路径（加分）
- ✅ 真实案例佐证（加分）

---

### Q2.2 分库分表的方案有哪些？如何选择分片键？分库分表后带来哪些问题？

**问题描述**：请详细说明分库分表的策略、分片键选择原则及带来的挑战。

**参考答案**：

**1. 拆分方式**

| 方式 | 说明 | 适用 |
| --- | --- | --- |
| **垂直分库** | 按业务拆库（订单库、用户库、商品库） | 业务耦合度高 |
| **垂直分表** | 大字段拆到扩展表 | 单表字段多、体积大 |
| **水平分库** | 同一表数据按规则分散到多个库 | 单库数据量大、并发高 |
| **水平分表** | 同一库内单表拆多表 | 单表数据量大 |

```
垂直分库：  订单库 | 用户库 | 商品库
水平分库：  订单库0 | 订单库1 | 订单库2 | 订单库3
水平分表：  orders_0 | orders_1 | orders_2 | orders_3 (同库)
```

**2. 分片策略**

| 策略 | 说明 | 优缺点 |
| --- | --- | --- |
| **范围分片** | 按 ID/时间范围切分（0-1000万一张表） | 易扩容，但热点集中 |
| **哈希分片** | `shard = hash(key) % N` | 均匀，但扩容需 rehash 迁移 |
| **一致性哈希** | 哈希环 | 扩容只迁移相邻数据 |
| **路由表** | 维护 key→shard 映射表 | 灵活，但路由表是瓶颈 |

**3. 分片键选择原则**

- **高频查询条件优先**：用 `WHERE` 最多的字段（如 `user_id`）
- **数据分布均匀**：避免热点（如按 user_id 哈希均匀）
- **避免跨片查询**：分片键能覆盖绝大多数查询
- **不可变**：分片键值不能改变（否则需迁移数据）

**常见分片键**：
- 电商订单：`user_id`（用户查自己订单不跨片）
- 社交动态：`user_id`（看自己主页不跨片）
- 日志：`create_time`（按时间范围查）

**4. 分库分表带来的问题**

| 问题 | 说明 | 解决方案 |
| --- | --- | --- |
| **跨片查询** | 非分片键查询需扫所有片 | 路由表/双写/ES 同步 |
| **分布式事务** | 跨库事务 | XA/TCC/Saga/本地消息表 |
| **全局唯一 ID** | 自增 ID 冲突 | 雪花算法/号段模式 |
| **跨片 JOIN** | 不同片无法 JOIN | 冗余字段/应用层组装 |
| **跨片分页** | LIMIT 需各片取 N 再合并 | 禁止深分页/CQRS |
| **扩容迁移** | 加片需 rehash 迁移 | 一致性哈希/双写迁移 |
| **聚合统计** | COUNT/SUM 跨片 | 预计算汇总表 |

**5. 跨片分页难题**

```sql
-- 用户查询第 3 页，每页 20，按时间倒序
-- 错误：每片取前 60 条，合并后取 41-60
-- 问题：第 3 页可能某片贡献 0 条，需各片取更多

-- 正确思路：各片取 offset+limit 条，内存合并排序再取目标段
-- 深分页几乎不可行 → 产品限制或用游标
```

**6. 主流中间件**

| 中间件 | 模式 | 特点 |
| --- | --- | --- |
| **ShardingSphere-JDBC** | Client 端 | 轻量、无额外进程、Java 生态 |
| **ShardingSphere-Proxy** | Proxy 端 | 多语言支持、运维友好 |
| **MyCat** | Proxy 端 | 老牌、社区活跃度下降 |
| **Vitess** | Proxy 端 | YouTube 开源、云原生 |
| **TDDL** | Client 端 | 阿里内部、未开源 |

**实际案例**：
- **项目背景**：订单表 5 亿条，单库扛不住读写压力
- **方案**：
  - 分片键：`user_id`（80% 查询是用户查自己订单）
  - 策略：`hash(user_id) % 16` 分 16 库 × 4 表 = 64 片
  - ID：雪花算法生成全局唯一
  - 商家查询（非分片键）：通过 ES 同步，按 `shop_id` 索引
  - 全局统计：离线跑，写汇总表
- **挑战**：跨片分页用游标限制；扩容用双写迁移
- **最终效果**：单库数据降到 800 万，查询稳定 20ms，QPS 提升 10 倍

**评分要点**：
- ✅ 垂直/水平、分库/分表区分（必备）
- ✅ 分片键选择原则（必备）
- ✅ 分库分表带来的 5+ 个问题及解决方案（必备）
- ✅ 跨片分页难题分析（加分）
- ✅ 主流中间件对比（加分）

---

### Q2.3 如何用缓存缓解大数据量查询压力？缓存策略有哪些？如何保证缓存与 DB 一致性？

**问题描述**：请设计一套缓存方案应对大数据量查询，并解决一致性问题。

**参考答案**：

**1. 多级缓存架构**

```
请求 → 本地缓存(L1) → Redis(L2) → DB
        (毫秒级过期)    (秒级过期)   (兜底)
```

- **L1 本地缓存**（Caffeine/Guava）：极快、单机、容量小、适合热点
- **L2 Redis**：分布式、容量大、跨实例共享
- **DB**：兜底数据源

**2. 缓存策略**

| 策略 | 说明 | 适用 |
| --- | --- | --- |
| **Cache-Aside** | 先查缓存，miss 查 DB 回填 | 通用（最常用） |
| **Read-Through** | 缓存层代理读 DB | 缓存中间件支持 |
| **Write-Through** | 写缓存，缓存同步写 DB | 强一致 |
| **Write-Behind** | 写缓存，异步刷 DB | 高写入、容忍丢失 |

**3. 缓存穿透、击穿、雪崩**

| 问题 | 原因 | 解决 |
| --- | --- | --- |
| **穿透** | 查不存在的数据，缓存和 DB 都没有 | 布隆过滤器 / 缓存空值 |
| **击穿** | 热点 key 失效瞬间大量请求打 DB | 互斥锁 / 永不过期+异步刷新 |
| **雪崩** | 大量 key 同时失效 | 过期时间加随机 / 多级缓存 |

**4. 缓存与 DB 一致性**

**Cache-Aside 读写策略**：
- 读：缓存 miss → 查 DB → 回填缓存
- 写：先更新 DB → 再删缓存（删而非更新）

**为什么删而非更新缓存**：
- 避免并发写导致缓存与 DB 不一致
- 避免更新一个没人读的缓存（浪费）

**延迟双删（防脏读）**：
```java
1. 删缓存
2. 更新 DB
3. 延迟 500ms 再删缓存（防读旧值回填）
```

**最终一致方案**：监听 binlog（Canal）异步刷缓存，保证最终一致。

**5. 缓存设计要点**

- **key 设计**：`业务:维度:ID`，如 `user:profile:1001`
- **TTL 设置**：热点短 TTL（5min），冷数据长 TTL（1day），基础数据永不过期+主动更新
- **序列化**：用 Protobuf/MessagePack 代替 JSON，省内存
- **大 Value 拆分**：单 key 控制在 10KB 内，大对象拆 hash 或分片

**实际案例**：
- **项目背景**：商品详情页 QPS 5 万，DB 扛不住
- **方案**：
  - L1：Caffeine 缓存热门商品（容量 1 万，TTL 10s）
  - L2：Redis 缓存全量商品（TTL 5min）
  - 写：更新 DB → 删 Redis → 发 MQ 异步刷
  - 防穿透：布隆过滤器过滤不存在的商品 ID
- **最终效果**：DB QPS 从 5 万降到 500，详情页 P99 5ms

**评分要点**：
- ✅ 多级缓存架构（必备）
- ✅ 穿透/击穿/雪崩及解决方案（必备）
- ✅ Cache-Aside + 删缓存策略（必备）
- ✅ 延迟双删 / Canal binlog 最终一致（加分）
- ✅ 大 Value 拆分、序列化优化（加分）

---

### Q2.4 SQL 语句重构有哪些常见技巧？请举例说明如何把一条慢 SQL 改快。

**问题描述**：SQL 重构有哪些套路？请举例说明。

**参考答案**：

**常见 SQL 重构技巧**：

**1. SELECT * → 明确列**

```sql
-- 慢：回表取所有列
SELECT * FROM orders WHERE user_id = 100;

-- 快：覆盖索引，不回表
SELECT id, order_no, amount FROM orders WHERE user_id = 100;
```

**2. 子查询 → JOIN**

```sql
-- 慢：子查询可能产生临时表
SELECT * FROM orders WHERE user_id IN (SELECT id FROM users WHERE vip = 1);

-- 快：JOIN 优化器更友好
SELECT o.* FROM orders o INNER JOIN users u ON o.user_id = u.id WHERE u.vip = 1;
```

**3. OR → UNION ALL**

```sql
-- 慢：OR 可能放弃索引
SELECT * FROM orders WHERE user_id = 1 OR shop_id = 2;

-- 快：UNION ALL 各走各的索引
SELECT * FROM orders WHERE user_id = 1
UNION ALL
SELECT * FROM orders WHERE shop_id = 2;
```

**4. 函数 → 范围**

```sql
-- 慢：函数导致索引失效
SELECT * FROM orders WHERE YEAR(create_time) = 2024 AND MONTH(create_time) = 6;

-- 快：范围查询走索引
SELECT * FROM orders WHERE create_time >= '2024-06-01' AND create_time < '2024-07-01';
```

**5. LIKE '%xxx' → 全文索引/ES**

```sql
-- 慢：前缀通配索引失效
SELECT * FROM goods WHERE name LIKE '%手机%';

-- 快：全文索引
SELECT * FROM goods WHERE MATCH(name) AGAINST('手机');
-- 或同步到 ES 搜索
```

**6. NOT IN → LEFT JOIN IS NULL**

```sql
-- 慢：NOT IN 效率低
SELECT * FROM orders WHERE user_id NOT IN (SELECT id FROM blacklist);

-- 快：LEFT JOIN IS NULL
SELECT o.* FROM orders o LEFT JOIN blacklist b ON o.user_id = b.id WHERE b.id IS NULL;
```

**7. 大 IN → 临时表/JOIN**

```sql
-- 慢：IN 列表过长（10万+）
SELECT * FROM orders WHERE id IN (1,2,3,...,100000);

-- 快：用临时表 JOIN
CREATE TEMPORARY TABLE tmp_ids (id BIGINT PRIMARY KEY);
INSERT INTO tmp_ids VALUES ...;  -- 批量插入
SELECT o.* FROM orders o INNER JOIN tmp_ids t ON o.id = t.id;
```

**8. COUNT(*) 优化**

```sql
-- 慢：全表扫计数
SELECT COUNT(*) FROM orders WHERE status = 1;

-- 快：缓存计数 / 汇总表
-- 方案1：Redis 计数器
-- 方案2：维护统计表 stats(status, count)
SELECT count FROM stats WHERE status = 1;
```

**9. 复杂统计 → 预计算**

```sql
-- 慢：实时聚合千万数据
SELECT shop_id, SUM(amount) FROM orders WHERE create_time > '2024-01-01' GROUP BY shop_id;

-- 快：定时预计算汇总表
-- 每小时跑：INSERT INTO shop_daily_summary ... 
SELECT shop_id, total FROM shop_daily_summary WHERE date = '2024-06-01';
```

**实际案例**：
- **项目背景**：报表 SQL `SELECT COUNT(DISTINCT user_id) FROM orders WHERE create_time BETWEEN ? AND ?`，3000 万数据跑 40 秒
- **重构**：
  1. 离线预计算：每日凌晨跑 `INSERT INTO user_stats SELECT date, COUNT(DISTINCT user_id) ...`
  2. 查询改读汇总表
- **最终效果**：40s → 10ms

**评分要点**：
- ✅ 至少 5 种重构技巧（必备）
- ✅ 子查询→JOIN、OR→UNION、函数→范围（必备）
- ✅ 大 IN、COUNT 优化（加分）
- ✅ 预计算思路（加分）

---

### Q2.5 冷热数据分离如何实现？有什么好处？

**问题描述**：什么是冷热数据分离？如何落地？

**参考答案**：

**1. 概念**

将访问频率高的"热数据"和几乎不访问的"冷数据"分开存储：
- 热数据：近期数据（如近 3 个月订单），放高性能存储（SSD、内存）
- 冷数据：历史数据（如 1 年前订单），放廉价存储（HDD、归档库）

**2. 好处**

- 热表体积小，查询快、缓存命中率高
- 冷数据不影响生产库性能
- 降低存储成本（冷数据可用廉价介质）

**3. 实现方案**

**方案 A：分区表（最简单）**

按时间 RANGE 分区，老分区自动成"冷数据"，查询带时间条件自动裁剪。

**方案 B：归档表**

```sql
-- 1. 创建归档表（结构相同）
CREATE TABLE orders_archive LIKE orders;

-- 2. 定时迁移（低峰期）
INSERT INTO orders_archive SELECT * FROM orders WHERE create_time < '2024-01-01';
DELETE FROM orders WHERE create_time < '2024-01-01';

-- 3. 应用层路由：查近期走 orders，查历史走 orders_archive
```

**方案 C：跨库归档**

冷数据迁移到独立归档库（可用廉价机器/低配实例），生产库只保留热数据。

**方案 D：TTL + 自动归档**

用工具（如 pt-archiver）自动按 TTL 归档：

```bash
pt-archiver --source h=prod --dest h=archive \
  --where "create_time < '2024-01-01'" --no-delete --bulk-insert
```

**4. 查询路由**

应用层根据时间范围路由到不同表/库：
```java
if (queryDate.after(threeMonthsAgo)) {
    return ordersMapper.query(queryDate);      // 热表
} else {
    return ordersArchiveMapper.query(queryDate); // 冷表
}
```

**5. 冷数据查询优化**

- 冷数据访问少但偶尔要查，可建索引但不必太精细
- 冷库可用更便宜的存储（如 HDD、对象存储）
- 超冷数据可导出到 Parquet 文件，用 ClickHouse/Spark 查询

**实际案例**：
- **项目背景**：订单表 5 亿条，90% 是 6 个月前数据，单表查询慢
- **方案**：
  - 热表保留近 6 个月（5000 万），放 SSD 高配实例
  - 冷数据归档到独立库（4.5 亿），放 HDD 低配实例
  - 每日凌晨用 pt-archiver 迁移过期数据
- **最终效果**：热表查询从 2s 降到 50ms，存储成本降 60%

**评分要点**：
- ✅ 冷热分离概念与好处（必备）
- ✅ 至少 2 种实现方案（必备）
- ✅ 查询路由设计（必备）
- ✅ pt-archiver 等工具（加分）

---

## 第三篇 事务与锁机制

### Q3.1 请详细说明事务的 ACID 特性，以及 InnoDB 是如何实现这四个特性的？

**问题描述**：ACID 各指什么？InnoDB 用什么机制保证它们？

**参考答案**：

**ACID 四大特性**：

| 特性 | 含义 | InnoDB 实现机制 |
| --- | --- | --- |
| **A（Atomicity）原子性** | 事务要么全成功要么全回滚 | **undo log**（回滚日志） |
| **C（Consistency）一致性** | 事务前后数据一致 | A + I + 业务约束共同保证 |
| **I（Isolation）隔离性** | 并发事务互不干扰 | **锁 + MVCC** |
| **D（Durability）持久性** | 提交后永久保存 | **redo log**（重做日志） + Buffer Pool |

**1. 原子性——undo log**

- 事务执行前，先把"修改前的旧值"写入 undo log
- 回滚时根据 undo log 恢复
- undo log 还用于 MVCC 读取历史版本

```
事务：UPDATE user SET age=30 WHERE id=1;
1. undo log 记录：(id=1, age=20)  -- 旧值
2. 修改 Buffer Pool 中的数据页：age=30
3. 若回滚 → 用 undo log 恢复 age=20
4. 若提交 → undo log 保留（供 MVCC）后由 purge 线程清理
```

**2. 持久性——redo log**

- 修改数据时，先写 redo log（记录"改了什么"），再写数据页
- **WAL（Write-Ahead Logging）**：先写日志再写数据，保证崩溃恢复
- redo log 是物理日志（记录页号+偏移+新值），顺序写，速度快
- 崩溃后用 redo log 重做未落盘的修改

```
事务提交流程（两阶段提交）：
1. 写 redo log（prepare 状态）
2. 写 binlog
3. 写 redo log（commit 状态）
4. 返回成功
```

**3. 隔离性——锁 + MVCC**

- 写写并发：用**锁**（行锁、间隙锁）串行化
- 读写并发：用 **MVCC**（多版本并发控制）让读不阻塞写、写不阻塞读

**4. 一致性**

一致性是最终目标，由 A（回滚保证不破坏）+ I（隔离保证不干扰）+ D（持久保证不丢失）+ 业务约束（唯一键、外键、触发器）共同实现。

**评分要点**：
- ✅ ACID 含义准确（必备）
- ✅ undo log 实现原子性、redo log 实现持久性（必备）
- ✅ WAL 机制（必备）
- ✅ 一致性是目标，由 AID + 约束共同保证（加分）

---

### Q3.2 MySQL 的四种事务隔离级别分别解决了什么问题？InnoDB 默认是哪个？

**问题描述**：请说明四种隔离级别及各并发问题（脏读、不可重复读、幻读）。

**参考答案**：

**1. 三种并发异常**

| 异常 | 说明 | 示例 |
| --- | --- | --- |
| **脏读** | 读到其他事务**未提交**的修改 | A 改 age=30 未提交，B 读到 30，A 回滚→B 读到脏数据 |
| **不可重复读** | 同一事务两次读**同一行**结果不同 | A 第一次读 age=20，B 提交 age=30，A 第二次读 age=30 |
| **幻读** | 同一事务两次查询**行数**不同 | A 第一次查 age>20 有 5 行，B 插入 1 行，A 第二次查有 6 行 |

**2. 四种隔离级别**

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 实现方式 |
| --- | --- | --- | --- | --- |
| **READ UNCOMMITTED** 读未提交 | ❌ 可能 | ❌ 可能 | ❌ 可能 | 无锁无 MVCC |
| **READ COMMITTED** 读已提交 | ✅ 防止 | ❌ 可能 | ❌ 可能 | MVCC（每条语句新快照） |
| **REPEATABLE READ** 可重复读（默认） | ✅ 防止 | ✅ 防止 | ⚠️ InnoDB 基本防止 | MVCC（事务开始快照）+ 间隙锁 |
| **SERIALIZABLE** 串行化 | ✅ 防止 | ✅ 防止 | ✅ 防止 | 加锁串行 |

**3. InnoDB 默认 REPEATABLE READ**

- 用 **MVCC** 防止不可重复读：事务内多次读同一数据结果一致
- 用 **间隙锁（Next-Key Lock）** 防止幻读：对查询范围加锁，阻止其他事务插入

**4. RC vs RR 的 MVCC 差异**

- **RC（读已提交）**：每条 SELECT 都生成新 ReadView，能看到最新已提交数据
- **RR（可重复读）**：事务第一条 SELECT 生成 ReadView，整个事务复用，保证可重复读

**5. RR 下快照读仍可能幻读**

```sql
BEGIN;
SELECT * FROM t WHERE id > 10;  -- 快照读，5 行
-- 事务 B 插入 id=15 并提交
SELECT * FROM t WHERE id > 10;  -- 仍 5 行（RR 快照）
UPDATE t SET name='x' WHERE id > 10;  -- 当前读，更新了 6 行（含新插入）
SELECT * FROM t WHERE id > 10;  -- 6 行！幻读出现
```

**实际案例**：
- **项目背景**：金融对账系统，需严格一致读，曾因幻读导致对账不平
- **方案**：关键查询用 `SELECT ... FOR UPDATE`（当前读 + 加锁）或升级 SERIALIZABLE
- **权衡**：锁粒度大影响并发，仅核心场景用

**评分要点**：
- ✅ 三种异常定义（必备）
- ✅ 四种隔离级别对应解决的问题（必备）
- ✅ InnoDB 默认 RR（必备）
- ✅ RC vs RR 的 MVCC 快照差异（加分）
- ✅ RR 下快照读仍可能幻读（高级）

---

### Q3.3 请详细说明 InnoDB 的 MVCC（多版本并发控制）原理。

**问题描述**：MVCC 是如何实现的？ReadView、undo log 版本链如何协作？

**参考答案**：

**1. MVCC 目的**

让**读写不互斥**：读操作读历史版本（快照），写操作写新版本，互不阻塞，提升并发性能。

**2. 实现基础——三个组件**

**① 隐藏字段**：每行有三个隐藏字段
- `DB_TRX_ID`（6 字节）：最后修改该行的事务 ID
- `DB_ROLL_PTR`（7 字节）：回滚指针，指向 undo log 中的上一版本
- `DB_ROW_ID`（6 字节）：无主键时的隐藏主键

**② undo log 版本链**

每次修改都生成一条 undo log，通过 `DB_ROLL_PTR` 链接，形成版本链：

```
当前行: id=1, age=30, trx_id=200, roll_ptr → 
  undo log: age=25, trx_id=150, roll_ptr →
    undo log: age=20, trx_id=100, roll_ptr → NULL
```

**③ ReadView（读视图）**

事务执行 SELECT 时生成 ReadView，包含：
- `m_ids`：当前活跃（未提交）事务 ID 列表
- `min_trx_id`：m_ids 中最小值
- `max_trx_id`：下一个将分配的事务 ID
- `creator_trx_id`：当前事务 ID

**3. 可见性判断规则**

对版本链中某个版本，判断是否可见：

```
设该版本 trx_id = T：
1. T == creator_trx_id → 本事务修改的，可见 ✅
2. T < min_trx_id → 修改时事务已提交，可见 ✅
3. T >= max_trx_id → 修改时事务在 ReadView 之后，不可见 ❌
4. min_trx_id <= T < max_trx_id：
   - T 在 m_ids 中 → 活跃事务，不可见 ❌
   - T 不在 m_ids 中 → 已提交，可见 ✅
```

不可见时，沿 `roll_ptr` 找上一版本，重复判断。

**4. RC vs RR 的 ReadView 生成时机**

- **RC**：每次 SELECT 都生成新 ReadView → 能看到最新已提交数据
- **RR**：事务第一次 SELECT 生成 ReadView，整个事务复用 → 可重复读

**5. 当前读 vs 快照读**

| 类型 | 说明 | 何时用 |
| --- | --- | --- |
| **快照读** | 读 ReadView 可见版本 | 普通 SELECT |
| **当前读** | 读最新版本 + 加锁 | `SELECT ... FOR UPDATE`、UPDATE、DELETE、INSERT |

```sql
SELECT * FROM t WHERE id=1;              -- 快照读（MVCC）
SELECT * FROM t WHERE id=1 FOR UPDATE;   -- 当前读（加锁，读最新）
UPDATE t SET age=30 WHERE id=1;          -- 当前读（先读最新再改）
```

**评分要点**：
- ✅ 三个隐藏字段（必备）
- ✅ undo log 版本链（必备）
- ✅ ReadView 四个字段 + 可见性判断规则（必备）
- ✅ RC vs RR 的 ReadView 生成时机差异（加分）
- ✅ 快照读 vs 当前读（必备）

---

### Q3.4 InnoDB 的锁有哪些？行锁、间隙锁、Next-Key Lock 的区别？

**问题描述**：请说明 InnoDB 的锁体系，特别是行锁、间隙锁、Next-Key Lock。

**参考答案**：

**1. 行锁的两种模式**

| 模式 | 说明 | 兼容性 |
| --- | --- | --- |
| **共享锁（S）** | 读锁，`SELECT ... LOCK IN SHARE MODE` | S 之间兼容 |
| **排他锁（X）** | 写锁，UPDATE/DELETE/`FOR UPDATE` | 与任何锁互斥 |

**2. 行锁的三种算法**

| 算法 | 锁定范围 | 说明 |
| --- | --- | --- |
| **Record Lock** 记录锁 | 单行 | 锁定索引上的一条记录 |
| **Gap Lock** 间隙锁 | 范围（不含记录） | 锁定记录间的间隙，防插入 |
| **Next-Key Lock** | 记录 + 前间隙 | Record Lock + Gap Lock，左开右闭 `(a, b]` |

**示例**：表有 id = 10, 15, 20

```sql
-- 事务 A
SELECT * FROM t WHERE id BETWEEN 10 AND 20 FOR UPDATE;
-- 加 Next-Key Lock：(−∞, 10], (10, 15], (15, 20], (20, +∞)

-- 事务 B 尝试
INSERT INTO t VALUES (12);  -- ❌ 阻塞（在 10~15 间隙）
INSERT INTO t VALUES (25);  -- ❌ 阻塞（在 20~+∞ 间隙）
```

**3. 不同隔离级别的锁差异**

- **RR**：用 Next-Key Lock 防幻读（锁范围）
- **RC**：只用 Record Lock（不锁间隙），可能幻读

**4. 意向锁（Intention Lock）**

表级锁，表示事务"打算"在行上加锁：
- **IS（意向共享）**：打算加行 S 锁
- **IX（意向排他）**：打算加行 X 锁

作用：快速判断表是否有行锁，避免逐行检查。

**5. 死锁与排查**

两个事务互相等待对方释放锁。**死锁检测**：`innodb_deadlock_detect=ON`（默认开启），自动回滚代价小的事务。

```sql
SHOW ENGINE INNODB STATUS;  -- 看 LATEST DETECTED DEADLOCK
SET GLOBAL innodb_status_output_locks = ON;
```

**死锁预防**：
- 事务按相同顺序加锁（如按 id 升序）
- 事务尽量短小
- 降低隔离级别（RC 比 RR 锁少）

**实际案例**：
- **项目背景**：高并发下单，多个订单锁同一商品库存导致死锁
- **排查**：`SHOW ENGINE INNODB STATUS` 发现事务 A 锁商品 1 等商品 2，B 反之
- **解决**：统一按商品 ID 升序加锁；缩短事务（库存预扣后立即提交）
- **最终效果**：死锁消除

**评分要点**：
- ✅ S/X 锁、共享/排他兼容性（必备）
- ✅ Record/Gap/Next-Key Lock 区别（必备）
- ✅ Next-Key Lock 左开右闭范围（必备）
- ✅ 意向锁作用（加分）
- ✅ 死锁检测与预防（必备）

---

### Q3.5 乐观锁与悲观锁的区别？各自适用什么场景？如何用 SQL 实现？

**问题描述**：请对比乐观锁和悲观锁，并给出实现。

**参考答案**：

| 维度 | 悲观锁 | 乐观锁 |
| --- | --- | --- |
| 思想 | 假设会冲突，先加锁 | 假设不冲突，提交时检查 |
| 实现 | `SELECT ... FOR UPDATE` | version 字段 + CAS |
| 并发性 | 低（锁等待） | 高（无锁） |
| 冲突多 | ✅ 适合 | ❌ 重试成本高 |
| 冲突少 | ❌ 浪费 | ✅ 适合 |
| 死锁 | 可能 | 不可能 |

**悲观锁实现**：

```sql
BEGIN;
SELECT stock FROM goods WHERE id=1 FOR UPDATE;  -- 加 X 锁
-- 业务判断
UPDATE goods SET stock = stock - 1 WHERE id=1;
COMMIT;
```

**乐观锁实现**（version 字段）：

```sql
ALTER TABLE goods ADD COLUMN version INT DEFAULT 0;

-- 1. 先查当前 version
SELECT stock, version FROM goods WHERE id=1;  -- 假设 version=5

-- 2. 更新时带 version 条件（CAS）
UPDATE goods SET stock = stock - 1, version = version + 1
WHERE id=1 AND version=5;
-- affected_rows=1 → 成功；affected_rows=0 → 有人先改了，重试
```

**选择建议**：
- 冲突频繁（如秒杀库存）：悲观锁（避免大量重试）
- 冲突少（如用户更新资料）：乐观锁（无锁高并发）

**实际案例**：
- **秒杀场景**：库存预扣用 Redis 原子操作 + DB 乐观锁兜底
  ```sql
  UPDATE goods SET stock=stock-1 WHERE id=1 AND stock>0 AND version=5;
  ```
- **用户资料更新**：用乐观锁，避免 FOR UPDATE 阻塞其他读

**评分要点**：
- ✅ 思想差异（必备）
- ✅ 两种 SQL 实现（必备）
- ✅ 适用场景判断（必备）
- ✅ version CAS 机制（加分）

---

## 第四篇 主从复制与读写分离

### Q4.1 MySQL 主从复制的原理是什么？有哪些复制方式？

**问题描述**：请详细说明主从复制的流程及三种复制方式（异步、半同步、组复制）。

**参考答案**：

**1. 主从复制原理**

基于 **binlog**（二进制日志）实现，三个线程协作：

```
主库                          从库
┌──────────────┐           ┌──────────────────┐
│ 客户端写入    │           │                  │
│      ↓       │           │                  │
│  写 binlog   │           │                  │
│      ↓       │  网络      │                  │
│ Binlog Dump  │ ────────→ │ IO Thread        │
│  Thread      │  传 binlog │   ↓              │
│              │           │ 写 relay log     │
│              │           │   ↓              │
│              │           │ SQL Thread       │
│              │           │   ↓              │
│              │           │ 重放 SQL → 数据   │
└──────────────┘           └──────────────────┘
```

**流程**：
1. 主库执行 SQL，写 binlog
2. 从库 IO Thread 连主库，请求 binlog
3. 主库 Binlog Dump Thread 推送 binlog
4. 从库 IO Thread 写入 relay log（中继日志）
5. 从库 SQL Thread 读 relay log，重放 SQL，更新数据

**2. 三种复制方式**

| 方式 | 原理 | 数据安全 | 性能 | 适用 |
| --- | --- | --- | --- | --- |
| **异步复制** | 主库写完 binlog 即返回，不等从库 | ❌ 主挂可能丢数据 | 高 | 默认，容忍丢失 |
| **半同步复制** | 主库等至少一个从库收到 binlog 才返回 | ✅ 至少一份从库有 | 中 | 强一致要求 |
| **全同步复制** | 主库等所有从库应用完才返回 | ✅ 完全一致 | 低 | 极少用 |
| **组复制（MGR）** | Paxos 协议多数派写入 | ✅ 多数派一致 | 中 | 高可用集群 |

**3. 复制格式**

| 格式 | 说明 | 优缺点 |
| --- | --- | --- |
| **STATEMENT** | 记录 SQL 语句 | 日志小，但非确定性函数（NOW/UUID）可能不一致 |
| **ROW** | 记录每行变更（默认） | 数据一致，但日志大 |
| **MIXED** | 混合（一般 SQL 用 STATEMENT，含不确定函数用 ROW） | 折中 |

**4. 主从延迟原因与解决**

**延迟原因**：
- 主库并发写，从库 SQL Thread 单线程重放（5.7 前从库单线程）
- 大事务：一个事务执行很久
- 网络延迟
- 从库性能差

**解决**：
- **并行复制**（MySQL 5.7+）：从库多线程按库/组并行重放
  ```sql
  -- 从库配置
  SET GLOBAL slave_parallel_type = 'LOGICAL_CLOCK';
  SET GLOBAL slave_parallel_workers = 16;
  ```
- **避免大事务**：拆分批量操作
- **从库高性能**：SSD、足够内存
- **业务容忍**：读不要求实时的走从库，强一致读走主库

**5. 主从一致性级别**

```sql
-- 从库延迟检查
SHOW SLAVE STATUS \G
-- 关注 Seconds_Behind_Master、Slave_IO_Running、Slave_SQL_Running

-- GTID 复制（推荐，5.6+）
-- 每个事务有全局唯一 ID，便于追踪和故障切换
```

**实际案例**：
- **项目背景**：电商系统读写分离后，用户下单后立即查订单列表查不到（从库延迟 5 秒）
- **方案**：
  1. 关键查询（下单后查订单）走主库
  2. 非关键查询（历史订单）走从库
  3. 开启并行复制，从库延迟降到 1 秒内
- **最终效果**：用户感知消除，延迟降到 500ms

**评分要点**：
- ✅ 三个线程 + 复制流程（必备）
- ✅ 异步/半同步/组复制区别（必备）
- ✅ 主从延迟原因与并行复制（必备）
- ✅ GTID（加分）
- ✅ ROW vs STATEMENT 复制格式（加分）

---

### Q4.2 读写分离如何实现？有哪些坑？如何保证读到的数据是最新的？

**问题描述**：请设计读写分离方案，并解决"主从延迟导致读到旧数据"问题。

**参考答案**：

**1. 读写分离架构**

```
应用 → 写请求 → 主库
     → 读请求 → 从库（1...N）
```

**2. 实现方式**

| 方式 | 说明 | 优缺点 |
| --- | --- | --- |
| **代码层** | 业务代码根据操作类型选数据源 | 灵活但侵入性强 |
| **中间件** | ShardingSphere/MyCat/ProxySQL 自动路由 | 透明，无侵入 |
| **驱动层** | MySQL Router / JDBC 多数据源 | 较透明 |

**ShardingSphere 读写分离配置示例**：
```yaml
rules:
  - !READWRITE_SPLITTING
    dataSources:
      readwrite_ds:
        writeDataSourceName: master_ds
        readDataSourceNames:
          - slave_ds_0
          - slave_ds_1
        transactionalReadQueryStrategy: PRIMARY
        loadBalancerName: round_robin
    loadBalancers:
      round_robin:
        type: ROUND_ROBIN
```

**3. 主从延迟导致读到旧数据的场景**

```
用户写（主库）→ 立即读（从库）→ 从库还没同步 → 读到旧数据
```

**4. 解决方案**

**方案一：关键读走主库**

```java
// 写后立即读的场景（如下单后查订单）强制走主库
@Master  // 注解强制主库
public Order getLatestOrder(Long userId) { ... }
```

**方案二：写后短时间走主库**

```java
// 用 ThreadLocal/Redis 标记，写后 N 秒内读走主库
redis.setex("force_master:" + userId, 3, "1");  // 写后 3 秒

if (redis.exists("force_master:" + userId)) {
    return readFromMaster();  // 走主库
} else {
    return readFromSlave();   // 走从库
}
```

**方案三：等待从库同步**

```sql
-- MySQL 5.7+ 等待从库同步到指定 GTID
SELECT WAIT_FOR_EXECUTED_GTID_SET('uuid:seq', 1);
```

**方案四：半同步复制**

主库写后确保至少一个从库收到，降低延迟窗口。

**5. 读写分离的坑**

| 坑 | 说明 | 解决 |
| --- | --- | --- |
| 主从延迟 | 读到旧数据 | 上述方案 |
| 事务跨读写 | 事务内先读后写可能不一致 | 事务内全走主库 |
| 从库压力不均 | 某些从库负载高 | 负载均衡 |
| 主库宕机 | 写不可用 | MHA/MGR 自动切换 |
| 复制中断 | 从库停止同步 | 监控 + 修复 |

**实际案例**：
- **项目背景**：社交动态，用户发帖后立即刷新看不到新帖
- **方案**：发帖后 5 秒内该用户的查询走主库（ThreadLocal 标记）
- **最终效果**：用户感知消除，从库压力未明显增加

**评分要点**：
- ✅ 读写分离实现方式（必备）
- ✅ 主从延迟导致读到旧数据（必备）
- ✅ 至少 2 种解决方案（必备）
- ✅ 事务跨读写问题（加分）
- ✅ 中间件方案（加分）

---

## 第五篇 MySQL 架构与原理

### Q5.1 请描述 MySQL 的整体架构，以及一条 SQL 语句的执行流程。

**问题描述**：MySQL 分为哪几层？一条 SELECT 语句和一条 UPDATE 语句分别如何执行？

**参考答案**：

**1. MySQL 整体架构**

```
┌─────────────────────────────────────────┐
│           客户端 / 连接器                 │  连接管理、认证
├─────────────────────────────────────────┤
│              Server 层                   │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐  │
│  │ 查询缓存 │ │ 分析器    │ │ 优化器    │  │
│  │(8.0删除) │ │词法/语法  │ │执行计划   │  │
│  └─────────┘ └──────────┘ └──────────┘  │
│  ┌──────────────────────────────────┐   │
│  │           执行器                  │   │
│  └──────────────────────────────────┘   │
├─────────────────────────────────────────┤
│            存储引擎层（InnoDB/MyISAM）    │  数据存取
├─────────────────────────────────────────┤
│            文件系统 / 磁盘                │
└─────────────────────────────────────────┘
```

- **连接器**：管理连接、认证、权限
- **查询缓存**（8.0 已删除）：缓存查询结果，命中率低且失效频繁
- **分析器**：词法分析（识别关键字）、语法分析（检查语法）、生成解析树
- **优化器**：生成执行计划（选择索引、JOIN 顺序、决定走索引还是全表扫）
- **执行器**：调用存储引擎接口执行
- **存储引擎**：负责数据存取（InnoDB 默认）

**2. SELECT 执行流程**

```sql
SELECT * FROM users WHERE id = 1;
```

1. **连接器**：建立连接、验证权限
2. **查询缓存**（8.0 前）：查缓存，命中直接返回
3. **分析器**：识别 `SELECT`、表名、条件，生成解析树
4. **优化器**：选择主键索引，生成执行计划
5. **执行器**：调用 InnoDB 接口，按索引查行
6. **InnoDB**：在 B+ 树索引中查找，返回行数据
7. **执行器**：返回结果集给客户端

**3. UPDATE 执行流程（涉及日志）**

```sql
UPDATE users SET age = 30 WHERE id = 1;
```

1. 执行器调 InnoDB 接口查 id=1 的行
2. InnoDB 从 Buffer Pool 取（未命中则从磁盘读页）
3. 执行器把 age 改为 30，调 InnoDB 接口写入
4. InnoDB 把**旧值写入 undo log**（用于回滚和 MVCC）
5. InnoDB 更新 Buffer Pool 中的数据页（脏页）
6. InnoDB 写 **redo log**（prepare 状态）
7. 执行器写 **binlog**
8. InnoDB 写 redo log（commit 状态）——**两阶段提交**
9. 返回成功
10. 后台：Buffer Pool 脏页异步刷盘（redo log 已保证持久性）

**4. 两阶段提交（2PC）**

```
redo log (prepare) → binlog → redo log (commit)
```

**为什么需要两阶段提交**：保证 redo log 和 binlog 一致。若不用 2PC：
- 先写 redo 后写 binlog：redo 写完崩溃，binlog 没写，从库用 binlog 恢复会缺这条
- 先写 binlog 后写 redo：binlog 写完崩溃，redo 没写，主库恢复后没这条但从库有

崩溃恢复规则：
- redo log 是 commit 状态：都已写完，正常
- redo log 是 prepare 状态：查 binlog 是否完整
  - binlog 完整：提交（binlog 已写完，可对外）
  - binlog 不完整：回滚（保证主从一致）

**评分要点**：
- ✅ 三层架构（连接/Server/引擎）（必备）
- ✅ SELECT 执行流程（必备）
- ✅ UPDATE 涉及 undo/redo/binlog（必备）
- ✅ 两阶段提交原理与崩溃恢复（加分）
- ✅ 查询缓存 8.0 删除（加分）

---

### Q5.2 redo log、undo log、binlog 的区别？各自的作用？

**问题描述**：请对比这三种日志的作用、内容、写入时机。

**参考答案**：

| 日志 | 作用 | 层级 | 内容 | 写入时机 | 物理/逻辑 |
| --- | --- | --- | --- | --- | --- |
| **redo log** | 崩溃恢复（持久性） | InnoDB | 页的物理修改 | 事务执行中持续写 | 物理日志 |
| **undo log** | 回滚 + MVCC（原子性） | InnoDB | 修改前的旧值 | 修改前写 | 逻辑日志 |
| **binlog** | 复制 + 备份恢复 | Server | SQL/行变更 | 事务提交时写 | 逻辑日志 |

**1. redo log（重做日志）**

- **目的**：保证持久性。先写 redo log（顺序写，快），再异步刷数据页（随机写，慢）。崩溃后用 redo log 恢复未刷盘的修改
- **WAL 机制**：Write-Ahead Logging，先写日志再写数据
- **大小固定**：循环写，`innodb_log_file_size` 配置，写满触发刷盘
- **crash-safe**：redo log 保证崩溃不丢已提交事务

```
redo log 循环写：
[checkpoint] ──→ write pos
    ↑ 已刷盘          ↑ 待刷盘
    └───── 可写区域 ─┘
```

**2. undo log（回滚日志）**

- **目的**：保证原子性（回滚）+ MVCC（读历史版本）
- 记录修改前的反向操作
- 事务提交后不立即删除（MVCC 需要旧版本），由 purge 线程清理

**3. binlog（二进制日志）**

- **目的**：主从复制 + 数据恢复（基于时间点恢复 PITR）
- Server 层日志，所有引擎都有
- 三种格式：STATEMENT / ROW / MIXED
- 事务提交时一次性写入（可能分多个 binlog 文件）

**4. 三者协作（UPDATE 为例）**

```
UPDATE users SET age=30 WHERE id=1;

1. 查 id=1 的行（Buffer Pool）
2. 写 undo log：(id=1, age=20)  ← 旧值
3. 修改 Buffer Pool 数据页：age=30（脏页）
4. 写 redo log（prepare）：page=X, offset=Y, value=30
5. 写 binlog：UPDATE users SET age=30 WHERE id=1
6. 写 redo log（commit）
7. 返回成功
8. 后台：脏页刷盘 + undo log 清理（无活跃事务引用时）
```

**5. 基于时间点恢复（PITR）**

```bash
# 用全量备份 + binlog 恢复到指定时间点
mysqlbinlog --start-datetime="2024-06-01 00:00:00" \
            --stop-datetime="2024-06-01 12:00:00" \
            mysql-bin.000123 | mysql -u root -p
```

**评分要点**：
- ✅ 三种日志作用对比（必备）
- ✅ redo log 保证持久性、undo log 保证原子性（必备）
- ✅ WAL 机制（必备）
- ✅ redo log 循环写、binlog 追加写（加分）
- ✅ PITR 恢复（加分）

---

### Q5.3 InnoDB 的 Buffer Pool 是什么？如何调优？

**问题描述**：请说明 Buffer Pool 的工作原理及调优方法。

**参考答案**：

**1. Buffer Pool 作用**

InnoDB 的内存缓存区，缓存数据页和索引页，减少磁盘 IO。所有读写都先经过 Buffer Pool。

```
查询流程：
1. 查 Buffer Pool 是否有目标页
   - 命中 → 直接读内存
   - 未命中 → 从磁盘读页到 Buffer Pool
2. 修改也是在 Buffer Pool 中改（脏页），异步刷盘
```

**2. Buffer Pool 组成**

```
Buffer Pool
├── 数据页（data page）
├── 索引页（index page）
├── change buffer（普通索引的写缓存）
├── 自适应哈希索引（AHI）
├── 锁信息
└── undo 页
```

**3. 页面管理——LRU 链表（改进版）**

普通 LRU 问题：全表扫描会刷掉热点数据。InnoDB 改进：

```
LRU 链表分为两段：
┌─────────────────┬─────────────────┐
│   young 区(5/8)   │   old 区(3/8)    │
│   热点数据        │   新读入的页      │
└─────────────────┴─────────────────┘
```

- 新读入的页放到 **old 区头部**
- old 区的页若**第二次被访问且间隔超过 `innodb_old_blocks_time`**（默认 1s），才提升到 young 区
- 全表扫描的页只在 old 区短暂停留，不污染 young 区

**4. 关键参数调优**

```sql
-- Buffer Pool 大小（通常设为物理内存 60-80%）
innodb_buffer_pool_size = 16G

-- Buffer Pool 实例数（多实例减少锁竞争，>= 1G 时建议多实例）
innodb_buffer_pool_instances = 8

-- 预读配置
innodb_read_ahead_threshold = 56  -- 顺序读多少页触发预读

-- 脏页刷盘
innodb_max_dirty_pages_pct = 75   -- 脏页占比超此值触发刷盘

-- old 区停留时间
innodb_old_blocks_time = 1000     -- 1 秒
```

**5. 监控指标**

```sql
SHOW ENGINE INNODB STATUS\G
-- 关注：
-- Buffer pool hit rate: 1000/1000（命中率，应 > 99%）
-- young-making rate
-- pages made young / not young

-- 或查 information_schema
SELECT * FROM performance_schema.memory_summary_global_by_event_name
WHERE EVENT_NAME LIKE 'innodb_buffer_pool%';
```

**实际案例**：
- **项目背景**：64G 内存服务器，Buffer Pool 设 8G，命中率 85%，磁盘 IO 高
- **调优**：Buffer Pool 调到 48G（75%），实例数 8
- **最终效果**：命中率 99.5%，磁盘 IO 下降 80%，查询提升 3 倍

**评分要点**：
- ✅ Buffer Pool 作用（必备）
- ✅ 改进版 LRU（young/old 区）（必备）
- ✅ old 区停留时间防全表扫污染（必备）
- ✅ 关键参数调优（加分）
- ✅ 命中率监控（加分）

---

### Q5.4 MySQL 的两阶段提交（2PC）是什么？为什么需要？如何保证 redo log 和 binlog 的一致性？

**问题描述**：请说明两阶段提交的流程，以及为什么必须用它来保证 redo log 与 binlog 的一致性。

**参考答案**：

**1. 为什么需要两阶段提交**

redo log（InnoDB 引擎层）和 binlog（Server 层）是两个独立的日志。若不用两阶段提交，可能出现两者不一致：

- **先写 redo log，后写 binlog**：写完 redo log 崩溃 → 重启后主库有数据，但 binlog 没写 → 从库同步缺失这条数据 → **主从不一致**
- **先写 binlog，后写 redo log**：写完 binlog 崩溃 → 重启后主库没数据，但 binlog 已写 → 从库同步了一条不存在的数据 → **主从不一致**

**2. 两阶段提交流程**

```
                    ┌─────────────────────────────────┐
                    │  1. 写入 redo log (prepare 状态) │  ← 阶段一：准备
                    └─────────────────────────────────┘
                                  ↓
                    ┌─────────────────────────────────┐
                    │  2. 写入 binlog                  │
                    └─────────────────────────────────┘
                                  ↓
                    ┌─────────────────────────────────┐
                    │  3. 写入 redo log (commit 状态)  │  ← 阶段二：提交
                    └─────────────────────────────────┘
```

**3. 崩溃恢复规则**

重启时扫描 redo log：
- **redo log 是 commit 状态**：事务已提交完成，正常恢复
- **redo log 是 prepare 状态**：检查对应 binlog 是否完整
  - **binlog 完整（有 XID end）**：说明 binlog 已写完，提交事务
  - **binlog 不完整**：说明 binlog 没写完，回滚事务

**4. 为什么这样能保证一致**

- 若在阶段一后崩溃：binlog 未写 → 回滚 → 主从都没数据 ✅
- 若在阶段二前崩溃（binlog 写完但 redo log 没 commit）：binlog 完整 → 提交 → 主从都有数据 ✅
- 不会出现"主有从无"或"主无从有"的不一致状态

**5. group commit 优化**

5.7+ 引入组提交，多个事务的 redo log prepare、binlog 写盘、redo log commit 合并成一次 fsync，大幅提升性能：

```sql
-- 控制组提交行为
binlog_group_commit_sync_delay = 0       -- 等待多少微秒凑组
binlog_group_commit_sync_no_delay_count = 0  -- 凑够多少个事务提交
```

**实际案例**：
- **项目背景**：金融交易系统主从偶发数据不一致，审计发现某些主库已提交事务在从库缺失
- **排查过程**：早期版本关闭了 binlog（`skip-log-bin`）做性能优化，导致 2PC 失效；后又曾用 `sync_binlog=0` 提性能，崩溃时丢 binlog
- **解决方案**：开启 binlog + `sync_binlog=1` + `innodb_flush_log_at_trx_commit=1`（双 1 配置），保证强一致
- **最终效果**：主从数据完全一致，写入性能下降约 15%，可接受

**评分要点**：
- ✅ 不用 2PC 会导致主从不一致的两个场景（必备）
- ✅ prepare → binlog → commit 三步流程（必备）
- ✅ 崩溃恢复时根据 binlog 完整性决定提交/回滚（核心）
- ✅ group commit 优化（加分）
- ✅ 双 1 配置（加分）

---

## 第六篇 高可用与运维

### Q6.1 MySQL 常见的高可用方案有哪些？请对比 MHA、MGR、Orchestrator、keepalived+双主 的优劣。

**问题描述**：请列举主流 MySQL 高可用方案，分析各自的故障切换机制、数据一致性保证及适用场景。

**参考答案**：

**1. 主流方案对比**

| 方案 | 切换方式 | 数据一致性 | 部署复杂度 | 数据丢失风险 | 适用场景 |
| --- | --- | --- | --- | --- | --- |
| **Keepalived + 双主** | VIP 漂移 | 弱（异步复制） | 低 | 高（脑裂） | 小规模、可容忍少量丢失 |
| **MHA** | Manager 选新主 | 中（补全 relay log） | 中 | 中 | 传统异步复制集群 |
| **Orchestrator** | 拓扑感知自动切换 | 中 | 中 | 中 | 复杂拓扑、需可视化 |
| **MGR（Group Replication）** | Paxos 协议自动选主 | 强（多数派） | 高 | 低 | 金融级强一致 |
| **PXC / Galera** | 多主同步 | 强（wsrep） | 高 | 低 | 多写强一致 |
| **MySQL InnoDB Cluster** | MGR + MySQL Router + Shell | 强 | 高 | 低 | 官方全套方案 |

**2. MHA（Master High Availability）**

- **原理**：Manager 节点监控主库，主库宕机时从多个从库中选一个提升为新主，并尝试把原主未同步的 binlog 补到新主
- **切换流程**：
  1. 检测主库宕机（多次心跳失败）
  2. 从所有从库中选出数据最新的（relay log 最完整）
  3. 把其他从库的 relay log 差异应用到候选从库
  4. 提升候选从库为新主
  5. 其他从库重新指向新主
- **优点**：成熟稳定、社区资料多、对应用透明
- **缺点**：Manager 单点、不支持自动重建、已逐渐停止维护

**3. MGR（MySQL Group Replication）**

- **基于 Paxos 协议**：事务需多数派节点（>N/2）确认才能提交
- **单主模式**：自动选主，只有主可写
- **多主模式**：所有节点可写，但有冲突检测（乐观锁）
- **故障切换**：节点故障自动剔除/加入，主故障自动重选

```
MGR 集群（3 节点单主模式）：
┌──────┐   ┌──────┐   ┌──────┐
│ M1   │◄─►│ M2   │◄─►│ M3   │
│ 主   │   │ 从   │   │ 从   │
└──────┘   └──────┘   └──────┘
   │  Paxos 多数派确认（2/3 节点确认即提交）
   └─ 强一致，无脑裂
```

**4. Orchestrator**

- GitHub 出品的 MySQL 拓扑管理与自动故障切换工具
- **核心特性**：
  - 可视化拓扑（Web UI）
  - 智能故障切换：考虑复制拓扑、延迟、数据完整性
  - 支持手动调整拓扑（拖拽改主从关系）
  - 支持钩子（hook）集成到运维流程
- **比 MHA 优势**：拓扑感知更强、支持复杂级联复制、活跃维护

**5. Keepalived + 双主**

- 两台 MySQL 互为主从，VIP 通过 Keepalived 漂移
- **致命问题——脑裂**：网络分区时两台都升 VIP，双写导致数据冲突
- **缓解**：fencing 机制（关对方电源）、仲裁节点、应用层去重
- **不推荐用于生产强一致场景**

**6. 选型建议**

```
金融级强一致（核心交易）     → MGR / PXC
互联网中等一致（用户、订单）  → MHA / Orchestrator + 半同步复制
小规模可容忍丢失（内部系统）  → Keepalived + 双主
官方全套方案                → InnoDB Cluster (MGR + Router)
```

**实际案例**：
- **项目背景**：支付核心库原用 Keepalived + 双主，脑裂导致一笔交易双写，对账失败
- **选型过程**：评估 MHA（运维复杂）、MGR（强一致但需升级 8.0）、PXC（多写冲突多）
- **最终方案**：升级 MySQL 8.0，采用 MGR 单主模式 3 节点 + MySQL Router 读写分离
- **最终效果**：RPO=0（零数据丢失），RTO<30s 自动切换，再未出现脑裂问题

**评分要点**：
- ✅ 至少对比 3 种方案（必备）
- ✅ MGR 基于 Paxos 多数派（必备）
- ✅ MHA 切换流程（加分）
- ✅ Keepalived 脑裂问题（必备）
- ✅ 结合业务选型（加分）

---

### Q6.2 半同步复制（Semi-Sync）是什么？与异步复制、全同步复制的区别？如何配置？

**问题描述**：请说明 MySQL 半同步复制的原理，以及它如何权衡一致性和性能。

**参考答案**：

**1. 三种复制模式对比**

| 模式 | 主库等待 | 一致性 | 性能 | 可用性 |
| --- | --- | --- | --- | --- |
| **异步复制** | 不等从库 | 弱（可能丢） | 最好 | 最高 |
| **半同步复制** | 等至少 1 个从库 ACK | 中 | 较好 | 较高 |
| **全同步复制** | 等所有从库 ACK | 强 | 差 | 低 |

**2. 半同步复制原理**

```
主库                          从库
 │                             │
 │── binlog 写盘 ─────────────►│
 │                             │
 │── 等待 ACK ◄───────────────│── 应用 relay log
 │                             │
 │── 事务 commit               │
```

- 主库提交事务时，需等待至少一个从库 ACK 收到 binlog 才返回客户端
- **超时降级**：若超时（`rpl_semi_sync_master_timeout`，默认 10s）没收到 ACK，降级为异步，避免主库卡死

**3. AFTER_COMMIT vs AFTER_SYNC（5.7+）**

- **AFTER_COMMIT（5.5 行为，lossy）**：主库先 commit 再等 ACK。若主库 commit 后崩溃，从库可能没收到 → 丢数据
- **AFTER_SYNC（5.7+ 默认，lossless）**：主库等 ACK 后再 commit。即使主库崩溃，从库已收到 binlog，不丢数据

**4. 配置示例**

```sql
-- 主库
INSTALL PLUGIN rpl_semi_sync_master SONAME 'semisync_master.so';
SET GLOBAL rpl_semi_sync_master_enabled = 1;
SET GLOBAL rpl_semi_sync_master_timeout = 1000;  -- 1 秒超时降级
SET GLOBAL rpl_semi_sync_master_wait_for_slave_count = 1;  -- 至少几个从库 ACK

-- 从库
INSTALL PLUGIN rpl_semi_sync_slave SONAME 'semisync_slave.so';
SET GLOBAL rpl_semi_sync_slave_enabled = 1;
STOP SLAVE IO_THREAD; START SLAVE IO_THREAD;  -- 重启 IO 线程生效

-- 查看状态
SHOW GLOBAL STATUS LIKE 'Rpl_semi_sync_master%';
-- Rpl_semi_sync_master_status: ON      是否启用半同步
-- Rpl_semi_sync_master_clients: 2      半同步从库数
-- Rpl_semi_sync_master_no_tx: 0        未走半同步的事务数（降级了）
-- Rpl_semi_sync_master_yes_tx: 1234    走半同步的事务数
```

**5. 一主多从的"多数派"配置**

为保证"至少 N 个从库确认"，配合多从：

```sql
-- 主库配 3 从，要求至少 2 个 ACK
SET GLOBAL rpl_semi_sync_master_wait_for_slave_count = 2;
```

**6. 降级风险与防范**

- **风险**：超时自动降级为异步，可能丢数据
- **防范**：
  - 设大超时（如 30s），但影响性能
  - 监控 `Rpl_semi_sync_master_status`，降级即告警
  - 配合 MGR 用多数派，避免单点 ACK

**实际案例**：
- **项目背景**：电商订单库原异步复制，主库宕机丢 200 条订单，影响 200 用户
- **方案**：升级到半同步复制（AFTER_SYNC），3 从库要求至少 1 个 ACK，超时 3s
- **挑战**：跨机房从库网络抖动导致偶发降级
- **优化**：本地机房从库优先 ACK（同机房低延迟），降级时告警人工介入
- **最终效果**：再未丢数据，写入延迟增加约 2ms，可接受

**评分要点**：
- ✅ 三种复制模式对比（必备）
- ✅ 半同步"等至少 1 个 ACK + 超时降级"机制（必备）
- ✅ AFTER_SYNC 比 AFTER_COMMIT 安全（核心）
- ✅ 配置参数（加分）
- ✅ 降级风险与监控（加分）

---

### Q6.3 MySQL 常见备份方案有哪些？如何实现"热备 + 增量 + 时间点恢复"？

**问题描述**：请说明 mysqldump、XtraBackup、binlog 备份的适用场景，并设计一个完整的备份恢复策略。

**参考答案**：

**1. 备份方案对比**

| 方案 | 类型 | 锁影响 | 速度 | 增量 | 一致性 | 适用场景 |
| --- | --- | --- | --- | --- | --- | --- |
| **mysqldump** | 逻辑备份 | FTWRL（事务表可 single-transaction） | 慢 | 否 | 强 | 小库（<50G）、跨版本迁移 |
| **mysqlpump** | 逻辑备份 | 同上 | 较快（并行） | 否 | 强 | 中小库 |
| **Percona XtraBackup** | 物理备份 | 不锁（InnoDB） | 快 | 是 | 强 | 大库（>50G） |
| **MySQL Enterprise Backup** | 物理备份 | 不锁 | 快 | 是 | 强 | 企业版 |
| **binlog** | 增量日志 | 无 | - | 是 | - | 任意方案补充，做时间点恢复 |
| **LVM 快照** | 物理快照 | 短暂 FTWRL | 极快 | 否 | 强 | 应急备份 |

**2. mysqldump（逻辑备份）**

```bash
# 全量备份（InnoDB 一致性读，不锁表）
mysqldump --single-transaction --master-data=2 \
  --routines --triggers --events \
  --databases db1 db2 > backup.sql

# --single-transaction: 用 RR 隔离级别快照，不锁表（仅 InnoDB）
# --master-data=2: 记录 binlog 位点（注释形式），用于增量恢复
# --routines/triggers/events: 备份存储过程/触发器/事件
```

**恢复**：`mysql < backup.sql`（慢，需重放 SQL）

**3. Percona XtraBackup（物理备份，推荐大库）**

```bash
# 全量备份
xtrabackup --backup --target-dir=/backup/full -u root -p xxx

# 准备（apply log，使备份一致）
xtrabackup --prepare --target-dir=/backup/full

# 增量备份（基于全量）
xtrabackup --backup --target-dir=/backup/inc1 \
  --incremental-basedir=/backup/full

# 恢复全量
xtrabackup --copy-back --target-dir=/backup/full

# 增量恢复：先 prepare 全量 + apply 增量
xtrabackup --prepare --apply-log-only --target-dir=/backup/full
xtrabackup --prepare --target-dir=/backup/full --incremental-dir=/backup/inc1
xtrabackup --copy-back --target-dir=/backup/full
```

**原理**：复制 InnoDB 数据文件 + 后台持续记录 redo log，prepare 阶段回放 redo 使备份一致。不锁表（仅短暂备份 MDL）。

**4. binlog 增量 + 时间点恢复（PITR）**

```bash
# 1. 定期全量备份（如每天凌晨）
mysqldump --single-transaction --master-data=2 --flush-logs > full_$(date +%F).sql

# 2. 持续备份 binlog（每小时滚动）
mysqladmin flush-logs
cp /var/lib/mysql/mysql-bin.* /backup/binlog/

# 3. 恢复到任意时间点
#  a. 恢复全量
mysql < full_2026-08-01.sql

#  b. 找到全量备份的 binlog 位点
grep "CHANGE MASTER" full_2026-08-01.sql
# CHANGE MASTER TO MASTER_LOG_FILE='mysql-bin.000123', MASTER_LOG_POS=154;

#  c. 用 mysqlbinlog 重放到目标时间
mysqlbinlog --start-position=154 \
  --stop-datetime='2026-08-02 14:30:00' \
  mysql-bin.000123 mysql-bin.000124 | mysql

#  d. 或基于 GTID 恢复
mysqlbinlog --skip-gtids=true \
  --include-gtids='uuid:1-100' \
  mysql-bin.000123 | mysql
```

**5. 完整备份策略（生产推荐）**

```
备份策略：
├── 每周日 02:00  XtraBackup 全量（保留 4 周）
├── 每天 02:00    XtraBackup 增量（保留 7 天）
├── 每小时        binlog 备份到 OSS（保留 30 天）
├── 实时          主从复制（异地机房热备）
└── 每月          异地全量归档（保留 1 年）

恢复目标：
- RPO（数据丢失）< 1 小时（binlog 备份间隔）
- RTO（恢复时间）< 2 小时（XtraBackup 恢复 + binlog 重放）
```

**6. 验证与演练**

- **定期恢复测试**：每月把备份恢复到测试库，验证可读性
- **自动校验**：备份后计算 checksum，恢复时校验
- **混沌演练**：模拟主库宕机，演练从备份恢复全流程

**实际案例**：
- **项目背景**：误删表 `DROP TABLE orders`，需恢复到删除前一刻
- **恢复流程**：
  1. 用昨夜全量备份恢复到临时库（XtraBackup，30 分钟）
  2. 查 binlog 找到 DROP 操作的 GTID
  3. 重放 binlog 到 DROP 前（跳过该 GTID）
  4. 用临时库反补生产库丢失数据
- **最终效果**：1.5 小时完成恢复，丢失 < 1 小时数据
- **教训**：上线"延迟从库"（延迟 1 小时同步），后续误删可直接切延迟从

**评分要点**：
- ✅ 逻辑备份 vs 物理备份区别（必备）
- ✅ XtraBackup 增量原理（加分）
- ✅ binlog 时间点恢复流程（必备）
- ✅ 完整备份策略（全量+增量+binlog+异地）（必备）
- ✅ 定期恢复演练（加分）

---

### Q6.4 如何构建 MySQL 监控体系？核心指标有哪些？慢查询如何发现与治理？

**问题描述**：请设计一套 MySQL 监控告警方案，并说明慢查询治理的方法论。

**参考答案**：

**1. 监控架构**

```
mysqld_exporter ─┐
node_exporter ───┼─► Prometheus ──► Grafana 看板
slowlog ─────────┘                  │
                                    ▼
                                AlertManager ──► 钉钉/电话
```

- **mysqld_exporter**：采集 MySQL 性能指标（SHOW GLOBAL STATUS、INFORMATION_SCHEMA）
- **node_exporter**：采集服务器指标（CPU、内存、磁盘、网络）
- **慢日志采集**：Filebeat → Logstash → ES，或 pt-query-digest 定期分析
- **APM**：应用层 trace 关联 SQL，定位慢 SQL 来源

**2. 核心监控指标**

| 类别 | 指标 | 告警阈值 |
| --- | --- | --- |
| **可用性** | `mysql_up` | = 0 立即告警 |
| | `slave_io_running` / `slave_sql_running` | = No 告警 |
| | `seconds_behind_master` | > 60s 告警 |
| **性能** | `mysql_global_status_queries` QPS | 突增/骤降告警 |
| | `mysql_global_status_slow_queries` 慢查询数 | 增长告警 |
| | `mysql_global_status_innodb_row_ops_*` TPS | - |
| **连接** | `threads_connected` | > 80% max_connections 告警 |
| | `threads_running` | > 100 告警 |
| | `aborted_connects` | 突增告警（可能是密码错误/攻击） |
| **缓存** | `innodb_buffer_pool_read_requests` vs `reads` 算命中率 | < 95% 告警 |
| **锁** | `innodb_row_lock_waits` | > 0 持续告警 |
| | `innodb_row_lock_time_avg` | > 1000ms 告警 |
| | `deadlocks` | 任何死锁告警 |
| **复制** | `seconds_behind_master` | > 60s |
| | `slave_io_running` | = No |
| **容量** | 磁盘使用率 | > 80% 告警，> 90% 紧急 |
| | 表空间增长速率 | 突增告警 |

**3. 慢查询发现**

```sql
-- 1. 开启慢日志
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 0.1;  -- 100ms
SET GLOBAL log_queries_not_using_indexes = ON;

-- 2. 查看当前正在执行的 SQL
SHOW PROCESSLIST;
-- 或
SELECT * FROM information_schema.PROCESSLIST 
WHERE TIME > 10 ORDER BY TIME DESC;

-- 3. 查看锁等待
SELECT * FROM performance_schema.data_lock_waits;
SELECT * FROM sys.innodb_lock_waits;

-- 4. 查看最近死锁
SHOW ENGINE INNODB STATUS\G
```

**4. 慢日志分析工具**

```bash
# mysqldumpslow（自带，简单）
mysqldumpslow -s t -t 10 slow.log  # 按时间取前 10

# pt-query-digest（Percona，强大）
pt-query-digest slow.log > report.txt
# 报告按"指纹"聚合，显示：
# - 慢 SQL 排行（按总耗时/次数/锁等）
# - 每条 SQL 的统计分布（min/avg/max/p95/p99）
# - 示例 SQL 与 EXPLAIN 建议
```

**5. 慢查询治理方法论**

```
发现 → 量化 → 分析 → 优化 → 验证 → 持续
 ↓       ↓       ↓       ↓       ↓       ↓
慢日志  pt报表  EXPLAIN 加索引  profiling 周扫描
```

**步骤**：
1. **发现**：慢日志 + APM trace
2. **量化**：pt-query-digest 出报表，按"总耗时 = 次数 × 平均耗时"排序，优先治理 Top10
3. **分析**：EXPLAIN 看执行计划，定位全表扫/回表/filesort
4. **优化**：加索引、改 SQL、覆盖索引、深分页改造
5. **验证**：profiling 对比优化前后耗时
6. **持续**：上线 SQL 审核流程（如 Yearning/Apache ShardingSphere），卡慢 SQL 上线

**6. SQL 审核机制**

- **上线前审核**：DBA 工单系统，所有 DDL/DML 上线前 EXPLAIN 检查
- **自动化审核**：用 `soar`（小米开源 SQL 优化工具）自动给建议
- **慢 SQL 告警**：生产慢日志每 5 分钟扫描，新增慢 SQL 自动推钉钉

**实际案例**：
- **项目背景**：监控系统上线后，发现某接口 P99 飙到 5s，但慢日志只有 1s 阈值
- **排查**：调低慢日志阈值到 100ms，发现一条 800ms 的 SQL 每分钟执行 2000 次
- **优化**：加联合索引 + 覆盖索引，从 800ms 降到 5ms
- **长效机制**：建立 SQL 审核流程 + Grafana 慢 SQL 看板 + 钉钉告警，慢 SQL 数量从月增 50 条降到 0

**评分要点**：
- ✅ Prometheus + exporter 监控架构（必备）
- ✅ 核心指标分类（可用性/性能/连接/锁/复制/容量）（必备）
- ✅ pt-query-digest 慢日志分析（必备）
- ✅ 慢查询治理方法论（发现→量化→分析→优化→验证→持续）（核心）
- ✅ SQL 上线审核机制（加分）

---

### Q6.5 生产环境发生死锁如何排查？请结合一个真实场景说明排查与解决过程。

**问题描述**：线上出现死锁告警，请描述完整的排查流程和解决方案。

**参考答案**：

**1. 死锁概念回顾**

- **死锁**：两个或多个事务互相持有对方需要的锁，导致永久阻塞
- InnoDB 有**死锁检测**（`innodb_deadlock_detect=ON`），检测到死锁会主动回滚代价较小的事务
- 默认 `innodb_lock_wait_timeout=50s`，超时也会回滚

**2. 排查流程**

```
1. 捕获死锁日志 → 2. 还原死锁场景 → 3. 分析锁等待 → 4. 优化
```

**步骤 1：开启死锁日志**

```sql
SET GLOBAL innodb_print_all_deadlocks = ON;
-- 死锁信息写入 error log（默认只写最后一条到 SHOW ENGINE INNODB STATUS）
```

**步骤 2：查看死锁日志**

```sql
SHOW ENGINE INNODB STATUS\G
-- 找到 LATEST DETECTED DEADLOCK 段
```

死锁日志示例：

```
*** (1) TRANSACTION:
TRANSACTION 12345, ACTIVE 2 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1136, 2 row lock(s)
MySQL thread id 8, OS thread handle 0x..., query id 100 localhost root updating
UPDATE account SET balance = balance - 100 WHERE id = 2   ← 事务1 持有 id=1 锁，等 id=2 锁

*** (1) WAITING FOR THIS LOCK TO BE GRANTED:
RECORD LOCKS space id 50 page no 3 n bits 72 index PRIMARY of table `test`.`account`
trx id 12345 lock_mode X locks rec but not gap waiting

*** (2) TRANSACTION:
TRANSACTION 12346, ACTIVE 2 sec starting index read
UPDATE account SET balance = balance - 100 WHERE id = 1   ← 事务2 持有 id=2 锁，等 id=1 锁

*** (2) HOLDS THE LOCK(S):
RECORD LOCKS space id 50 page no 3 n bits 72 index PRIMARY of table `test`.`account`
trx id 12346 lock_mode X locks rec but not gap

*** (2) WAITING FOR THIS LOCK TO BE GRANTED:
... trx id 12346 lock_mode X locks rec but not gap waiting

*** WE ROLL BACK TRANSACTION (2)   ← 回滚事务2
```

**步骤 3：还原死锁场景**

从日志提取：
- **事务 1**：`UPDATE account SET balance=balance-100 WHERE id=2`（持有 id=1，等 id=2）
- **事务 2**：`UPDATE account SET balance=balance-100 WHERE id=1`（持有 id=2，等 id=1）

死锁形成：

```
时间  事务1 (转账 A→B)        事务2 (转账 B→A)
t1    UPDATE id=1 ✓ 持锁
t2                              UPDATE id=2 ✓ 持锁
t3    UPDATE id=2 ⏳ 等锁
t4                              UPDATE id=1 ⏳ 等锁
                                ↓
                          死锁！回滚事务2
```

**步骤 4：分析与解决**

**根因**：两个转账事务以**不同顺序**加锁，导致循环等待。

**解决方案**：

1. **统一加锁顺序**（最推荐）：
   ```java
   // 转账前对账户 id 排序，始终先锁小 id
   void transfer(long from, long to, BigDecimal amount) {
     long first = Math.min(from, to);
     long second = Math.max(from, to);
     // 先锁 first，再锁 second
     jdbcTemplate.update("UPDATE account SET balance=balance-? WHERE id=?", amount, first);
     jdbcTemplate.update("UPDATE account SET balance=balance+? WHERE id=?", amount, second);
   }
   ```

2. **一次性锁所有资源**：用 `SELECT ... FOR UPDATE` 预先锁定两行
   ```sql
   BEGIN;
   SELECT * FROM account WHERE id IN (1,2) ORDER BY id FOR UPDATE;
   UPDATE account SET balance=balance-100 WHERE id=1;
   UPDATE account SET balance=balance+100 WHERE id=2;
   COMMIT;
   ```

3. **缩短事务**：减少事务持有锁的时间，降低死锁概率

4. **降低隔离级别**：RR 改 RC，减少间隙锁（但需评估业务）

**3. 死锁监控与告警**

```sql
-- 监控死锁次数
SHOW GLOBAL STATUS LIKE 'Innodb_deadlocks';

-- Prometheus 告警规则
# 死锁次数 5 分钟内增加 > 0 即告警
- alert: MysqlDeadlock
  expr: rate(mysql_global_status_innodb_deadlocks[5m]) > 0
  for: 1m
  annotations:
    summary: "MySQL 发生死锁"
```

**4. 常见死锁场景**

| 场景 | 原因 | 解决 |
| --- | --- | --- |
| 转账/库存对调 | 加锁顺序不一致 | 统一排序加锁 |
| 唯一索引并发插入 | S 锁与 X 锁冲突 | 业务去重 + INSERT IGNORE |
| 间隙锁冲突（RR） | 范围更新重叠 | 改 RC 或缩小范围 |
| 外键级联更新 | 父子表锁顺序 | 避免并发更新外键 |
| 大事务持锁过久 | 长事务阻塞 | 拆分事务 |

**实际案例**：
- **项目背景**：电商库存系统，并发下单偶发死锁，每分钟 10+ 次
- **排查**：死锁日志显示两个扣库存事务以不同顺序锁 `sku_id`
- **解决**：扣库存 SQL 改为 `UPDATE stock SET num=num-? WHERE sku_id=? AND num>=?`，且业务层按 sku_id 排序后批量扣
- **最终效果**：死锁降至 0，扣库存 TPS 提升 30%

**评分要点**：
- ✅ 开启 `innodb_print_all_deadlocks`（必备）
- ✅ 能读懂死锁日志（事务、SQL、锁等待）（必备）
- ✅ 统一加锁顺序解决死锁（核心）
- ✅ 常见死锁场景（加分）
- ✅ 死锁监控告警（加分）

---

### Q6.6 MySQL 主从延迟如何排查与优化？从库延迟几十秒怎么解决？

**问题描述**：生产环境主从延迟严重（Seconds_Behind_Master 持续增长），请给出排查思路和优化方案。

**参考答案**：

**1. 主从延迟原因分析**

```
主库                       从库
 │                          │
 │── binlog 写盘 ────────► IO Thread ──► relay log
 │                                          │
 │                                    SQL Thread ──► 应用
 │
延迟点：① 网络传输 ② IO 写 relay log ③ SQL 重放（最常见）
```

| 延迟点 | 原因 | 排查 |
| --- | --- | --- |
| **主库大事务** | 单事务 binlog 几十 MB，从库重放慢 | 看主库大事务 `information_schema.innodb_trx` |
| **主库 DDL** | DDL 在从库需重建表，耗时长 | 看主库是否有 DDL |
| **从库硬件差** | CPU/IO 比主库弱 | 对比硬件配置 |
| **从库被业务读压垮** | 从库承载读 + 复制，资源争抢 | 看从库负载 |
| **单线程重放** | 5.6 之前 SQL 线程单线程，无法并行 | 看版本与并行配置 |
| **网络抖动** | 跨机房延迟 | ping 延迟 |
| **索引缺失** | 从库重放 UPDATE/DELETE 需扫表 | 对比从库索引 |

**2. 排查步骤**

```sql
-- 1. 查看延迟
SHOW SLAVE STATUS\G
-- 关注：
-- Seconds_Behind_Master: 30
-- Slave_IO_Running: Yes
-- Slave_SQL_Running: Yes
-- Relay_Log_Pos vs Master position

-- 2. 查看从库当前执行的 SQL
SELECT * FROM performance_schema.replication_applier_status_by_worker;
-- 或查 PROCESSLIST
SHOW PROCESSLIST;

-- 3. 主库大事务
SELECT trx_id, trx_started, trx_weight, trx_query
FROM information_schema.innodb_trx
ORDER BY trx_weight DESC LIMIT 10;

-- 4. 主库 binlog 大事务
mysqlbinlog mysql-bin.000123 | grep -A 5 "BEGIN"
```

**3. 优化方案**

**① 多线程复制（MTS，5.7+ 推荐）**

```sql
-- 基于组提交的并行复制（5.7+，推荐）
STOP SLAVE;
SET GLOBAL slave_parallel_type = 'LOGICAL_CLOCK';
SET GLOBAL slave_parallel_workers = 16;  -- 并行线程数
SET GLOBAL slave_preserve_commit_order = ON;  -- 保持提交顺序
START SLAVE;

-- 对比 5.6 基于库并行（DATABASE 级别，库少时无效）
SET GLOBAL slave_parallel_type = 'DATABASE';
```

**② 主库避免大事务**

```sql
-- ❌ 一次性删除 1000 万
DELETE FROM log WHERE create_time < '2025-01-01';

-- ✅ 分批删除
DELETE FROM log WHERE create_time < '2025-01-01' LIMIT 1000;
-- 重复执行，每次 1000 行
```

**③ 从库优化**

```sql
-- 从库关闭 binlog（不作为他人主库时）
SET GLOBAL log_bin = OFF;
SET GLOBAL log_slave_updates = OFF;

-- 从库降低刷盘强度（牺牲一点持久性换性能）
SET GLOBAL sync_binlog = 0;
SET GLOBAL innodb_flush_log_at_trx_commit = 2;

-- 从库加大 Buffer Pool
SET GLOBAL innodb_buffer_pool_size = 32G;
```

**④ 写多读少场景用多级从库**

```
主库 ──► 一级从库（专做复制）
              ├──► 二级从库1（业务读）
              ├──► 二级从库2（业务读）
              └──► 二级从库3（备份）
```

一级从库专注复制无业务干扰，二级从库分担读。

**⑤ 半同步 + 延迟从库**

```sql
-- 延迟从库（如延迟 1 小时），用于误操作恢复
STOP SLAVE;
CHANGE MASTER TO MASTER_DELAY = 3600;
START SLAVE;
```

**4. 读写分离中的延迟容忍策略**

- **强一致读主**：写后立即读，强制走主库（可用 threadlocal 标记）
- **写后短暂延迟读**：写操作后等待 N 秒再读从
- **GTID 校验**：读从库前检查 GTID 是否已同步

**实际案例**：
- **项目背景**：社交平台 5.6 单线程从库延迟 30 分钟，业务读从库数据陈旧
- **排查**：主库每日有大事务（清理日志表 1000 万行）
- **优化**：
  1. 升级 5.7，开启 LOGICAL_CLOCK 16 线程并行
  2. 大事务改分批（每次 1000 行）
  3. 从库关闭 binlog + 调大 Buffer Pool
- **最终效果**：延迟从 30 分钟降到 < 1 秒

**评分要点**：
- ✅ 延迟原因分类（主库大事务/单线程/硬件/网络）（必备）
- ✅ MTS 多线程复制配置（必备）
- ✅ 大事务拆分（必备）
- ✅ 多级从库架构（加分）
- ✅ 读写分离延迟容忍策略（加分）

---

### Q6.7 线上磁盘满了如何紧急处理？大表 DDL 如何在线执行？

**问题描述**：生产环境 MySQL 磁盘满了导致服务异常，请给出应急方案；并说明大表 DDL 的在线执行方案。

**参考答案**：

**1. 磁盘满应急处理**

**快速释放空间**：

```sql
-- 1. 定位大表
SELECT table_schema, table_name, 
  ROUND(data_length/1024/1024/1024, 2) AS data_gb,
  ROUND(index_length/1024/1024/1024, 2) AS index_gb
FROM information_schema.tables
ORDER BY data_length DESC LIMIT 10;

-- 2. 清理无用 binlog（最有效）
PURGE BINARY LOGS BEFORE NOW() - INTERVAL 1 DAY;

-- 3. 临时关闭 binlog 写入（紧急）
SET GLOBAL sql_log_bin = 0;  -- 仅当前会话
-- 或关闭全局 binlog（需重启，谨慎）

-- 4. 清理慢日志、错误日志
-- 在 OS 层 truncate 慢日志文件

-- 5. 删除无用临时表、备份文件
```

**长期方案**：
- binlog 保留 7 天（`expire_logs_days = 7`）
- 监控磁盘使用率，> 80% 预警
- 定期归档冷数据
- 大表分区，按时间删除旧分区

**2. 大表 DDL 的痛点**

```sql
ALTER TABLE orders ADD COLUMN remark VARCHAR(100);
```

传统 `ALTER TABLE` 问题：
- **锁表**：DDL 期间表不可写（部分 DDL 5.6+ 支持 ONLINE，但仍有 MDL 锁）
- **复制延迟**：DDL 在从库重放，单线程，可能延迟几小时
- **磁盘翻倍**：ALTER 需要复制新表，磁盘占用 ×2
- **风险高**：执行到一半失败回滚成本极高

**3. 在线 DDL 方案对比**

| 方案 | 原理 | 锁影响 | 适用 |
| --- | --- | --- | --- |
| **原生 ONLINE DDL** | 5.6+ InnoDB 支持 | 部分操作仍锁（如加全文索引） | 小改动 |
| **pt-online-schema-change** | 触发器 + 影子表 | 不锁表 | 通用，最流行 |
| **gh-ost** | binlog + 影子表，无触发器 | 不锁表 | GitHub 出品，更稳 |
| **原生 INSTANT DDL** | 8.0.12+ 仅改元数据 | 零影响 | 加列/删列等 |

**4. pt-online-schema-change（pt-osc）**

```bash
pt-online-schema-change \
  --alter "ADD COLUMN remark VARCHAR(100)" \
  --execute \
  --chunk-size=1000 \
  --max-lag=1 \
  D=db,t=orders,h=localhost,u=root,p=xxx
```

原理：
1. 创建影子表 `_orders_new`（结构与原表相同 + DDL 变更）
2. 在原表建三个触发器（INSERT/UPDATE/DELETE 同步到影子表）
3. 分批（chunk）把原表数据复制到影子表
4. 用 RENAME TABLE 原子切换（毫秒级锁）
5. 删除旧表

**关键参数**：
- `--chunk-size`：每批行数，控制复制速度
- `--max-lag`：从库延迟超过此值则暂停，保护从库
- `--max-load`：主库负载超过阈值则暂停

**5. gh-ost（GitHub 出品，更推荐）**

```bash
gh-ost \
  --host=localhost --user=root --password=xxx \
  --database=db --table=orders \
  --alter="ADD COLUMN remark VARCHAR(100)" \
  --execute \
  --max-lag-millis=1000 \
  --throttle-control-replicas="slave1,slave2"
```

**与 pt-osc 区别**：
- **无触发器**：通过解析 binlog 同步变更，避免触发器性能影响
- **可控可暂停**：可随时暂停、调整速率
- **从库负载感知**：根据从库延迟动态调速

**6. 原生 INSTANT DDL（MySQL 8.0.12+）**

```sql
ALTER TABLE orders ADD COLUMN remark VARCHAR(100), ALGORITHM=INSTANT;
```

- 只修改数据字典元数据，零数据复制
- 秒级完成
- 限制：仅支持加列（默认末尾）、删列、改列默认值等
- 8.0.28+ 支持任意位置加列

**7. DDL 上线最佳实践**

```
1. 评估：DDL 类型 → 选 INSTANT / pt-osc / gh-ost
2. 测试：测试库执行，验证耗时与影响
3. 备份：DDL 前全量备份
4. 低峰：业务低峰期执行
5. 监控：监控主从延迟、负载，超阈值暂停
6. 回滚：准备回滚 SQL
```

**实际案例**：
- **项目背景**：1.5 亿订单表加字段，用原生 ALTER 跑了 6 小时锁表，业务全挂
- **改造**：引入 gh-ost，分批 + binlog 同步，全程不锁表
- **执行**：业务低峰执行，2 小时完成，对业务零影响
- **进阶**：升级 8.0 后简单加列用 INSTANT DDL，秒级完成

**评分要点**：
- ✅ 磁盘满应急：清理 binlog、定位大表（必备）
- ✅ 大表 DDL 痛点（锁表、磁盘翻倍、复制延迟）（必备）
- ✅ pt-osc / gh-ost 原理对比（必备）
- ✅ gh-ost 无触发器优势（加分）
- ✅ MySQL 8.0 INSTANT DDL（加分）

---

### Q6.8 MySQL 安全加固清单？如何防范 SQL 注入、敏感数据泄露？

**问题描述**：请列出 MySQL 生产环境的安全加固措施，并说明 SQL 注入防范方案。

**参考答案**：

**1. MySQL 安全加固清单**

**账号权限**：
```sql
-- 1. 删除匿名账号
DELETE FROM mysql.user WHERE User='';
-- 2. 禁止远程 root 登录
UPDATE mysql.user SET Host='localhost' WHERE User='root';
-- 3. 最小权限原则
CREATE USER 'app'@'10.0.%' IDENTIFIED BY '强密码';
GRANT SELECT, INSERT, UPDATE, DELETE ON db.* TO 'app'@'10.0.%';
-- 不授 ALL PRIVILEGES，不授 SUPER、FILE、PROCESS
-- 4. 密码策略
SET GLOBAL validate_password.policy = 'STRONG';
SET GLOBAL validate_password.length = 12;
-- 5. 定期改密 + 审计
```

**网络层**：
- MySQL 不暴露公网，仅内网访问
- 防火墙白名单限制来源 IP
- 强制 SSL 连接：`REQUIRE SSL` 或 `REQUIRE X509`

**数据层**：
- 敏感字段加密存储（密码 bcrypt、身份证 AES）
- binlog 加密（8.0+ `binlog_encryption=ON`）
- 表空间加密（`innodb_encrypt_tables=ON`）
- 审计日志（MySQL Enterprise Audit 或 MariaDB Audit Plugin）

**2. SQL 注入防范**

**漏洞示例**：
```java
// ❌ 拼接 SQL，可注入
String sql = "SELECT * FROM users WHERE name='" + name + "'";
stmt.execute(sql);
// 攻击：name = ' OR '1'='1 → SELECT * FROM users WHERE name='' OR '1'='1
```

**防范措施**：

1. **预编译语句（参数化查询）——最有效**：
   ```java
   // ✅ PreparedStatement 自动转义
   String sql = "SELECT * FROM users WHERE name = ?";
   PreparedStatement ps = conn.prepareStatement(sql);
   ps.setString(1, name);
   ```

2. **ORM 框架**：MyBatis 用 `#{}` 而非 `${}`
   ```xml
   <!-- ✅ 预编译 -->
   <select id="findByName">SELECT * FROM users WHERE name = #{name}</select>
   <!-- ❌ 字符串拼接，可注入 -->
   <select id="orderBy">SELECT * FROM users ORDER BY ${field}</select>
   ```

3. **输入校验**：白名单校验（如订单号只允许数字+字母）

4. **最小权限**：应用账号无 DROP、FILE 权限，即使注入也无法删库

5. **WAF**：Web 应用防火墙拦截 SQL 注入特征

**3. 敏感数据保护**

```sql
-- 密码：bcrypt（不可逆 + 加盐）
-- 应用层用 bcrypt，DB 只存 hash

-- 身份证/手机号：AES 加密 + 应用层解密
-- 或脱敏存储：130****1234

-- 8.0+ 透明数据加密（TDE）
INSTALL PLUGIN keyring_file SONAME 'keyring_file.so';
CREATE TABLE kms_secret (
  id INT PRIMARY KEY,
  secret VARBINARY(255) NOT NULL  -- 应用层加密后存
);

-- 字段级加密（应用层实现）
AES_ENCRYPT('13800138000', 'key');
AES_DECRYPT(encrypted_col, 'key');
```

**4. 审计与追溯**

```sql
-- 开启审计插件（企业版 / MariaDB Audit Plugin）
INSTALL PLUGIN server_audit SONAME 'server_audit.so';
SET GLOBAL server_audit_events = 'CONNECT,QUERY,TABLE';
SET GLOBAL server_audit_logging = ON;
-- 记录谁在什么时间执行了什么 SQL
```

**5. 备份与容灾安全**

- 备份文件加密（XtraBackup `--encrypt`）
- 备份传输走加密通道
- 异地容灾，防勒索

**实际案例**：
- **项目背景**：某系统被 SQL 注入，攻击者用 `UNION SELECT` 拖库，10 万用户信息泄露
- **根因**：旧代码用字符串拼接 SQL + 应用账号是 root 权限
- **整改**：
  1. 全量排查代码，改用 PreparedStatement / MyBatis `#{}`
  2. 应用账号降权，仅 CRUD，无 DDL/DROP
  3. 上 WAF 拦截 SQL 注入特征
  4. 敏感字段（手机号、身份证）加密存储
  5. 开启审计日志，便于追溯
- **最终效果**：通过安全等保三级测评，再无注入事件

**评分要点**：
- ✅ 账号最小权限 + 删匿名 + 禁 root 远程（必备）
- ✅ 预编译语句防注入（必备）
- ✅ MyBatis `#{}` vs `${}` 区别（加分）
- ✅ 敏感数据加密方案（必备）
- ✅ 审计日志（加分）

---

## 附录 评分标准与面试指南

### A.1 各能力维度评分标准

| 维度 | 初级（1-3分） | 中级（4-6分） | 高级（7-9分） | 专家（10分） |
| --- | --- | --- | --- | --- |
| **索引原理** | 知道索引加速查询 | 懂 B+ 树、聚簇/二级索引 | 懂回表、覆盖索引、ICP | 能量化分析页分裂、AHI 调优 |
| **查询优化** | 会看 EXPLAIN | 能定位全表扫、加索引 | 懂 JOIN 算法、深分页、覆盖索引 | 能做慢 SQL 全流程治理 |
| **事务锁机制** | 知道 ACID | 懂 4 隔离级别 | 懂 MVCC、行锁/间隙锁/Next-Key | 能分析死锁日志、设计无死锁方案 |
| **主从复制** | 会搭主从 | 懂异步/半同步 | 懂 GTID、并行复制、延迟优化 | 能设计高可用架构、PITR 恢复 |
| **大数据量** | 会分页 | 懂分区表 | 懂分库分表、冷热分离 | 能设计 ShardingSphere 方案 |
| **架构原理** | 知道 Server/引擎分层 | 懂 Buffer Pool | 懂 redo/undo/binlog、2PC | 能从源码层分析 InnoDB |
| **高可用运维** | 会备份恢复 | 懂监控告警 | 懂 MHA/MGR、慢 SQL 治理 | 能设计 RPO/RTO 容灾方案 |

### A.2 面试官提问策略

**由浅入深**：
1. **概念题**："说说 B+ 树" → 考察基础
2. **原理题**："为什么 InnoDB 用 B+ 树" → 考察深度
3. **应用题**："这条 SQL 怎么优化" → 考察实践
4. **场景题**："线上慢 SQL 怎么排查" → 考察综合能力
5. **设计题**："设计一个支撑亿级订单的 MySQL 架构" → 考察架构能力

**追问技巧**：
- 候选人答完一个点，追问"为什么"、"还有别的方案吗"、"实际项目怎么做"
- 挖到底层：从"加索引" → "为什么 B+ 树快" → "页分裂怎么影响性能"
- 挖到实践：从"懂 MVCC" → "实际遇到过幻读吗" → "怎么解决的"

### A.3 红线问题（一票否决）

- 把 MySQL 说成"单线程"（混淆 Node.js）
- 认为索引越多越好（不懂索引代价）
- 不知道事务隔离级别（基础缺失）
- 用 `SELECT *` 还觉得没问题（无优化意识）
- 主从延迟只会说"加从库"（无深度）
- 答不上 ACID 任意一项（基础缺失）

### A.4 加分项

- 主动画架构图、流程图
- 量化数据（"3 层 B+ 树存 16 亿"、"Buffer Pool 命中率 99%"）
- 结合真实项目案例（项目背景 → 问题 → 方案 → 效果）
- 提到 MySQL 8.0 新特性（MGR、Hash Join、INSTANT DDL、降序索引）
- 横向对比其他数据库（PostgreSQL、TiDB、ClickHouse）
- 提到源码层理解（`row_search_mvcc`、`buf_LRU_*`）

### A.5 备考察重点

面试前重点准备：
1. **B+ 树 + 索引失效场景**（必考）
2. **EXPLAIN 各字段 + 慢 SQL 优化流程**（必考）
3. **MVCC + 隔离级别 + 锁机制**（高频）
4. **主从复制 + 读写分离 + 半同步**（高频）
5. **分库分表 + 大数据量方案**（高频）
6. **redo/undo/binlog + 2PC**（中频）
7. **Buffer Pool + LRU**（中频）
8. **高可用方案 + 备份恢复**（中频）

建议每题准备一个**真实项目案例**：项目背景 → 技术选型原因 → 实现步骤 → 挑战与解决 → 最终效果。

---

## 参考资料与延伸阅读

- 官方文档：[MySQL 8.0 Reference Manual](https://dev.mysql.com/doc/refman/8.0/en/)
- 《高性能 MySQL》（第三版）—— Baron Schwartz 等
- 《MySQL 实战 45 讲》—— 林晓斌（极客时间）
- 《MySQL 是怎样运行的》—— 小孩子4919
- Percona Blog：https://www.percona.com/blog/
- GitHub gh-ost：https://github.com/github/gh-ost
- pt-toolkit 文档：https://www.percona.com/doc/percona-toolkit/

---

> **文档说明**：本面试题集共 6 大篇章、30+ 道题目，覆盖 MySQL 高级工程师所需的核心知识体系。所有题目均附问题描述、深度参考答案、实际项目案例与评分要点，适合面试备战、知识梳理、团队培训等场景。建议结合源码阅读与生产实践，从"会用 MySQL"进阶到"懂 MySQL"。
