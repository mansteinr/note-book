# ClickHouse 面试题汇总

## 目录
- [一、ClickHouse 简介](#一clickhouse-简介)
- [二、常用语法](#二常用语法)
- [三、使用场景与选型](#三使用场景与选型)
- [四、性能优化](#四性能优化)
  - [4.5 项目案例](#45-项目案例)
- [五、高级特性与实战](#五高级特性与实战)

---

## 一、ClickHouse 简介

### 1.1 核心概念

**ClickHouse** 是一个用于在线分析处理（OLAP）的开源列式数据库管理系统，由俄罗斯 Yandex 公司开发并于 2016 年开源。它以极快的查询性能著称，特别适合处理海量数据的实时分析场景。

### 1.2 发展背景

- **起源**：2009 年 Yandex 为 Metrica 项目（网络分析平台）开发
- **开源**：2016 年 6 月在 GitHub 开源
- **发展**：已成为最流行的 OLAP 数据库之一，被 Uber、eBay、京东、小米等公司采用
- **定位**：专注于 OLAP 场景，与 MySQL/PostgreSQL 等 OLTP 数据库互补

### 1.3 核心特性

| 特性 | 说明 |
|-----|------|
| **列式存储** | 按列存储数据，适合分析查询，压缩率高 |
| **向量化执行** | 利用 CPU SIMD 指令加速查询 |
| **分布式查询** | 原生支持分布式查询，数据分片存储 |
| **实时性** | 支持实时数据插入和查询 |
| **SQL 支持** | 支持标准 SQL，扩展了部分函数 |
| **高吞吐** | 每秒可插入数百万行数据 |
| **低延迟** | 毫秒级查询响应（百亿级数据） |

### 1.4 架构特点

```text
┌─────────────────────────────────────────┐
│           ClickHouse 架构               │
├─────────────────────────────────────────┤
│  Client (HTTP/TCP/CLI)                  │
├─────────────────────────────────────────┤
│  Query Parser → Planner → Executor      │
├─────────────────────────────────────────┤
│  Distributed Query Engine               │
├─────────────────────────────────────────┤
│  Storage Engine (MergeTree family)      │
├─────────────────────────────────────────┤
│  Column Storage + Compression           │
└─────────────────────────────────────────┘
```

**核心组件：**
- **MergeTree 引擎家族**：核心存储引擎，支持主键排序、分区、索引
- **分布式表引擎**：将查询路由到多个分片
- **物化视图**：预计算聚合数据，加速查询
- **字典**：内存中的键值映射，加速维度表查询

### 1.5 面试题

**Q1：什么是 ClickHouse？它与 MySQL 有什么区别？**

**答：**
ClickHouse 是一个列式数据库管理系统，专注于 OLAP（在线分析处理）场景。

| 对比维度 | ClickHouse | MySQL |
|---------|-----------|-------|
| **定位** | OLAP（分析型） | OLTP（事务型） |
| **存储方式** | 列式存储 | 行式存储 |
| **查询模式** | 少查询、大扫描 | 多查询、小扫描 |
| **写入模式** | 批量写入（推荐） | 单条/小批量写入 |
| **事务支持** | 不支持完整事务 | 完整 ACID 事务 |
| **更新删除** | 不推荐频繁更新删除 | 支持频繁更新删除 |
| **并发能力** | 低并发（数百 QPS） | 高并发（数千 QPS） |
| **数据规模** | PB 级 | TB 级 |
| **查询延迟** | 毫秒级（大数据量） | 毫秒级（小数据量） |

**评分要点：**
- 明确 OLAP vs OLTP 定位差异（2分）
- 列式 vs 行式存储区别（2分）
- 查询和写入模式差异（2分）
- 事务支持差异（1分）
- 适用场景差异（1分）

---

**Q2：ClickHouse 为什么查询这么快？请分析其高性能的原因。**

**答：**

ClickHouse 高性能的核心原因：

1. **列式存储**
   - 只读取查询需要的列，减少 I/O
   - 同列数据类型相同，压缩率高（通常 10:1 以上）
   - CPU 缓存命中率高

2. **向量化执行引擎**
   - 利用 CPU 的 SIMD（单指令多数据）指令
   - 一次处理一批数据（而非逐行处理）
   - 充分利用现代 CPU 的并行计算能力

3. **多线程并行**
   - 单个查询内部多线程并行执行
   - 充分利用多核 CPU

4. **分布式查询**
   - 数据分片存储，查询并行下推
   - 本地计算优先，减少网络传输

5. **索引优化**
   - 稀疏索引（主键索引）
   - 跳数索引（二级索引）
   - 分区裁剪

6. **代码级优化**
   - C++ 编写，底层优化
   - 自定义内存分配器
   - 高效的压缩算法（LZ4、Zstd）

7. **物化视图和预聚合**
   - 提前计算聚合结果
   - 查询时直接读取预计算数据

**评分要点：**
- 列式存储优势（2分）
- 向量化执行（2分）
- 多线程和分布式（2分）
- 索引优化（1分）
- 代码级优化（1分）

---

**Q3：ClickHouse 的 MergeTree 引擎家族有哪些？各自适用什么场景？**

**答：**

| 引擎 | 特点 | 适用场景 |
|-----|------|---------|
| **MergeTree** | 基础引擎，支持主键排序、分区、索引 | 单表大数据量存储 |
| **ReplacingMergeTree** | 合并时去重（按主键） | 维度表、状态表（最终一致） |
| **SummingMergeTree** | 合并时对数值列求和 | 预聚合场景（如每日汇总） |
| **AggregatingMergeTree** | 合并时执行聚合函数 | 物化视图预聚合 |
| **CollapsingMergeTree** | 通过 +1/-1 标记实现更新删除 | 需要频繁更新删除的场景 |
| **VersionedCollapsingMergeTree** | 带版本号的 Collapsing | 需要版本控制的场景 |
| **GraphiteMergeTree** | 存储 Graphite 时序数据 | 时序数据、监控系统 |

**核心区别：**
- **MergeTree**：基础存储，无特殊合并逻辑
- **ReplacingMergeTree**：按主键去重，保留最新版本
- **SummingMergeTree**：数值列自动求和
- **AggregatingMergeTree**：配合物化视图做预聚合
- **CollapsingMergeTree**：通过行标记实现更新删除

**评分要点：**
- 列举至少 4 种引擎（2分）
- 说明各引擎核心特点（3分）
- 给出适用场景（2分）
- 理解合并逻辑差异（1分）

---

**Q4：什么是 ClickHouse 的分区和排序键？它们的作用是什么？**

**答：**

**分区键（Partition Key）：**
- 决定数据如何分布到不同的分区（目录）
- 查询时通过分区裁剪减少扫描范围
- 常用：按时间分区（`toYYYYMM(date)`）

```sql
CREATE TABLE events (
    date Date,
    user_id UInt64,
    event_type String,
    value Float64
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)  -- 按月分区
ORDER BY (date, user_id)     -- 排序键
```

**排序键（Order By / Primary Key）：**
- 决定数据在分区内的物理存储顺序
- 用于构建稀疏索引（index.granularity = 8192）
- 查询时加速数据定位
- 常用：高频查询字段组合

**作用对比：**

| 特性 | 分区键 | 排序键 |
|-----|-------|-------|
| 物理组织 | 数据分目录存储 | 分区内数据排序 |
| 查询优化 | 分区裁剪 | 索引加速 |
| 数据粒度 | 粗粒度（月/天） | 细粒度（行级） |
| 修改成本 | 可重建分区 | 需重建表 |

**评分要点：**
- 分区键定义和作用（2分）
- 排序键定义和作用（2分）
- 两者区别（2分）
- 给出示例（1分）
- 理解索引机制（1分）

---

**Q5：ClickHouse 的副本和分片机制是如何工作的？**

**答：**

**分片（Shard）：**
- 数据水平拆分到多个节点
- 每个分片存储部分数据
- 通过分布式表引擎实现查询路由

```sql
-- 分布式表（不存储数据，只路由查询）
CREATE TABLE events_distributed AS events
ENGINE = Distributed(
    'cluster_name',  -- 集群名称
    'default',       -- 数据库名
    'events',        -- 本地表名
    rand()           -- 分片键
);
```

**副本（Replica）：**
- 同一分片的数据在多个节点上有备份
- 提供高可用性和读扩展
- 通过 ReplicatedMergeTree 引擎实现

```sql
-- 副本表
CREATE TABLE events ON CLUSTER cluster (
    date Date,
    user_id UInt64
) ENGINE = ReplicatedMergeTree(
    '/clickhouse/tables/{shard}/events',  -- ZooKeeper 路径
    '{replica}'                           -- 副本标识
)
PARTITION BY toYYYYMM(date)
ORDER BY (date, user_id);
```

**工作流程：**
1. 写入分布式表 → 路由到对应分片 → 写入本地表 → 同步到副本
2. 查询分布式表 → 并行查询所有分片 → 合并结果返回

**评分要点：**
- 分片机制说明（2分）
- 副本机制说明（2分）
- 分布式表引擎使用（2分）
- ReplicatedMergeTree 配置（1分）
- 读写流程（1分）

---

**Q6：ClickHouse 适合什么场景？不适合什么场景？**

**答：**

**适合的场景：**
1. **日志分析**：Web 日志、应用日志、访问日志
2. **用户行为分析**：PV/UV、留存分析、漏斗分析
3. **实时数仓**：实时报表、实时大屏
4. **时序数据**：监控指标、IoT 数据
5. **BI 分析**：多维分析、即席查询
6. **点击流分析**：广告点击、推荐效果

**不适合的场景：**
1. **OLTP 事务处理**：不支持完整事务，不适合订单、支付
2. **频繁更新删除**：更新删除成本高（异步合并）
3. **小数据量**：数据量小于千万级，优势不明显
4. **高并发点查**：并发能力有限（数百 QPS）
5. **复杂关联查询**：JOIN 性能不如专业 OLTP 数据库
6. **Blob 数据**：不适合存储大文本、图片

**评分要点：**
- 列举至少 4 个适合场景（2分）
- 列举至少 3 个不适合场景（2分）
- 理解 OLAP vs OLTP 差异（2分）
- 给出实际案例（1分）
- 理解性能边界（1分）

---

**Q7：ClickHouse 的数据压缩机制是怎样的？**

**答：**

ClickHouse 支持多级压缩：

**1. 数据压缩（磁盘压缩）**
- **LZ4**：默认压缩算法，压缩速度快，压缩率中等
- **Zstd**：压缩率更高，但速度较慢（适合冷数据）

```sql
CREATE TABLE events (
    date Date,
    data String
) ENGINE = MergeTree()
ORDER BY date
SETTINGS compression = 'ZSTD';  -- 指定压缩算法
```

**2. 列式压缩**
- 同列数据类型相同，压缩效果好
- 数值类型：Delta 编码 + 压缩
- 字符串：字典编码 + 压缩

**3. 压缩比参考：**
- 原始数据：100%
- LZ4 压缩：10%-20%
- Zstd 压缩：5%-10%

**评分要点：**
- 支持 LZ4 和 Zstd（2分）
- 列式压缩原理（2分）
- 压缩比参考（1分）
- 配置方式（1分）

---

## 二、常用语法

### 2.1 DDL（数据定义语言）

```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS analytics;

-- 创建表（MergeTree 引擎）
CREATE TABLE events (
    event_date Date,
    event_time DateTime,
    user_id UInt64,
    event_type String,
    page_url String,
    duration UInt32,
    country String,
    device_type LowCardinality(String)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id, event_type)
TTL event_date + INTERVAL 3 MONTH  -- 数据保留3个月
SETTINGS index_granularity = 8192;

-- 创建分布式表
CREATE TABLE events_distributed AS events
ENGINE = Distributed(
    'analytics_cluster',
    'analytics',
    'events',
    cityHash64(user_id)
);

-- 创建物化视图
CREATE MATERIALIZED VIEW daily_stats
ENGINE = SummingMergeTree()
ORDER BY (event_date, event_type)
AS SELECT
    event_date,
    event_type,
    count() AS event_count,
    sum(duration) AS total_duration
FROM events
GROUP BY event_date, event_type;

-- 创建字典
CREATE DICTIONARY countries_dict (
    country_code String,
    country_name String
) PRIMARY KEY country_code
SOURCE(CLICKHOUSE(
    HOST 'localhost'
    PORT 9000
    DB 'analytics'
    TABLE 'countries'
))
LAYOUT(HASHED())
LIFETIME(1 HOUR);

-- 修改表结构
ALTER TABLE events ADD COLUMN browser LowCardinality(String) AFTER device_type;
ALTER TABLE events MODIFY COLUMN duration UInt64;
ALTER TABLE events DROP COLUMN browser;

-- 删除表和数据库
DROP TABLE IF EXISTS events;
DROP DATABASE IF EXISTS analytics;
```

### 2.2 DML（数据操作语言）

```sql
-- 插入数据（单条）
INSERT INTO events VALUES (
    '2024-01-15',
    '2024-01-15 10:30:00',
    123456,
    'page_view',
    'https://example.com/page1',
    120,
    'CN',
    'mobile'
);

-- 批量插入（推荐）
INSERT INTO events (event_date, event_time, user_id, event_type, page_url, duration, country, device_type)
VALUES
('2024-01-15', '2024-01-15 10:30:00', 123456, 'page_view', 'https://example.com/page1', 120, 'CN', 'mobile'),
('2024-01-15', '2024-01-15 10:31:00', 123457, 'click', 'https://example.com/page2', 5, 'CN', 'desktop'),
('2024-01-15', '2024-01-15 10:32:00', 123458, 'page_view', 'https://example.com/page3', 80, 'US', 'mobile');

-- 从其他表插入
INSERT INTO events_archive
SELECT * FROM events
WHERE event_date < '2023-01-01';

-- 更新数据（异步，不推荐频繁使用）
ALTER TABLE events UPDATE duration = duration * 2 WHERE user_id = 123456;

-- 删除数据（异步，不推荐频繁使用）
ALTER TABLE events DELETE WHERE event_date < '2023-01-01';

-- 清空表
TRUNCATE TABLE events;
```

### 2.3 DQL（数据查询语言）

```sql
-- 基础查询
SELECT event_date, user_id, event_type
FROM events
WHERE event_date = '2024-01-15'
  AND country = 'CN'
ORDER BY event_time DESC
LIMIT 100;

-- 聚合查询
SELECT
    event_date,
    event_type,
    count() AS event_count,
    count(DISTINCT user_id) AS unique_users,
    avg(duration) AS avg_duration,
    sum(duration) AS total_duration
FROM events
WHERE event_date BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY event_date, event_type
ORDER BY event_date, event_count DESC;

-- 窗口函数
SELECT
    event_date,
    user_id,
    event_type,
    count() OVER (PARTITION BY user_id) AS user_event_count,
    row_number() OVER (PARTITION BY user_id ORDER BY event_time) AS user_event_seq
FROM events
WHERE event_date = '2024-01-15';

-- JOIN 查询
SELECT
    e.event_date,
    e.user_id,
    u.user_name,
    e.event_type
FROM events e
INNER JOIN users u ON e.user_id = u.id
WHERE e.event_date = '2024-01-15';

-- 子查询
SELECT event_date, event_count
FROM (
    SELECT
        event_date,
        count() AS event_count
    FROM events
    GROUP BY event_date
)
WHERE event_count > 10000;

-- 数组函数
SELECT
    user_id,
    groupArray(event_type) AS event_types,
    arrayJoin(event_types) AS single_event
FROM events
WHERE event_date = '2024-01-15'
GROUP BY user_id;

-- 时间函数
SELECT
    event_date,
    toStartOfMonth(event_date) AS month_start,
    toDayOfWeek(event_date) AS day_of_week,
    dateDiff('day', event_date, now()) AS days_ago
FROM events;

-- 条件函数
SELECT
    user_id,
    multiIf(
        duration < 10, 'short',
        duration < 60, 'medium',
        'long'
    ) AS duration_category
FROM events;

-- 字典查询
SELECT
    e.event_date,
    e.country,
    dictGet('countries_dict', 'country_name', e.country) AS country_name
FROM events e
WHERE e.event_date = '2024-01-15';
```

### 2.4 面试题

**Q1：ClickHouse 中如何高效地批量插入数据？**

**答：**

**推荐方式：**

1. **批量 INSERT（最常用）**
```sql
INSERT INTO events (event_date, user_id, event_type) VALUES
('2024-01-15', 1, 'view'),
('2024-01-15', 2, 'click'),
('2024-01-15', 3, 'view');
-- 每批建议 1000-10000 行
```

2. **INSERT SELECT（从其他表导入）**
```sql
INSERT INTO events_archive
SELECT * FROM events
WHERE event_date < '2023-01-01';
```

3. **HTTP 接口批量插入**
```bash
curl 'http://localhost:8123/?query=INSERT%20INTO%20events%20FORMAT%20CSV' \
  --data-binary @events.csv
```

4. **命令行工具**
```bash
cat events.csv | clickhouse-client --query="INSERT INTO events FORMAT CSV"
```

**注意事项：**
- 避免单条 INSERT（每秒只能处理几次写入）
- 每批数据量：1000-10000 行
- 每秒写入次数：不超过 1 次/秒
- 使用异步插入（`async_insert`）提高吞吐

**评分要点：**
- 批量 INSERT 方式（2分）
- 每批数据量建议（2分）
- 避免单条插入（1分）
- 其他导入方式（1分）

---

**Q2：ClickHouse 的物化视图是什么？如何使用？**

**答：**

**物化视图（Materialized View）** 是预计算的聚合结果，数据写入源表时自动更新。

**创建物化视图：**
```sql
-- 源表
CREATE TABLE events (
    event_date Date,
    event_type String,
    user_id UInt64,
    duration UInt32
) ENGINE = MergeTree()
ORDER BY (event_date, event_type);

-- 物化视图（预聚合）
CREATE MATERIALIZED VIEW daily_stats
ENGINE = SummingMergeTree()
ORDER BY (event_date, event_type)
AS SELECT
    event_date,
    event_type,
    count() AS event_count,
    sum(duration) AS total_duration,
    uniq(user_id) AS unique_users
FROM events
GROUP BY event_date, event_type;
```

**工作原理：**
1. 数据写入 `events` 表
2. 自动触发物化视图计算
3. 结果写入 `daily_stats` 表
4. 查询时直接读取 `daily_stats`

**查询物化视图：**
```sql
-- 直接查询物化视图（速度快）
SELECT * FROM daily_stats
WHERE event_date = '2024-01-15';

-- 物化视图会自动更新
INSERT INTO events VALUES ('2024-01-15', 'view', 123, 60);
SELECT * FROM daily_stats WHERE event_date = '2024-01-15';
-- 结果已自动包含新数据
```

**适用场景：**
- 实时报表（预聚合加速查询）
- 数据汇总（分钟/小时/天级别）
- 指标计算（PV/UV/转化率）

**评分要点：**
- 物化视图定义（2分）
- 创建语法（2分）
- 工作原理（2分）
- 适用场景（1分）
- 与源表关系（1分）

---

**Q3：ClickHouse 中如何实现数据的更新和删除？**

**答：**

ClickHouse 不推荐频繁更新删除，但提供了轻量级删除（Lightweight Delete）和变更（Mutation）机制。

**1. 轻量级删除（推荐）**
```sql
-- 标记删除（异步执行）
ALTER TABLE events DELETE WHERE event_date < '2023-01-01';

-- 查看删除进度
SELECT * FROM system.mutations WHERE is_done = 0;
```

**2. 轻量级更新**
```sql
-- 标记更新（异步执行）
ALTER TABLE events UPDATE duration = duration * 2 WHERE user_id = 123456;
```

**3. ReplacingMergeTree（去重）**
```sql
CREATE TABLE events_latest (
    event_date Date,
    user_id UInt64,
    event_type String,
    version UInt64
) ENGINE = ReplacingMergeTree(version)
ORDER BY (event_date, user_id);

-- 插入新版本数据
INSERT INTO events_latest VALUES ('2024-01-15', 123, 'view', 1);
INSERT INTO events_latest VALUES ('2024-01-15', 123, 'click', 2);

-- 合并后只保留最新版本（version=2）
-- 需要执行 OPTIMIZE 或等待后台合并
OPTIMIZE TABLE events_latest FINAL;
```

**4. CollapsingMergeTree（更新删除）**
```sql
CREATE TABLE events_collapse (
    event_date Date,
    user_id UInt64,
    event_type String,
    sign Int8  -- 1 表示新增，-1 表示删除
) ENGINE = CollapsingMergeTree(sign)
ORDER BY (event_date, user_id);

-- 插入数据
INSERT INTO events_collapse VALUES ('2024-01-15', 123, 'view', 1);

-- "删除"数据（插入 sign=-1 的行）
INSERT INTO events_collapse VALUES ('2024-01-15', 123, 'view', -1);

-- 合并后数据消失
```

**注意事项：**
- Mutation 是异步操作，不立即生效
- 频繁更新删除会影响性能
- 设计时尽量避免更新删除需求

**评分要点：**
- ALTER DELETE/UPDATE 语法（2分）
- ReplacingMergeTree 去重（2分）
- CollapsingMergeTree 更新删除（2分）
- 异步执行特性（1分）
- 不推荐频繁使用（1分）

---

**Q4：ClickHouse 的 JOIN 操作有哪些注意事项？**

**答：**

**JOIN 类型：**
```sql
-- INNER JOIN
SELECT e.*, u.name
FROM events e
INNER JOIN users u ON e.user_id = u.id;

-- LEFT JOIN
SELECT e.*, u.name
FROM events e
LEFT JOIN users u ON e.user_id = u.id;

-- RIGHT JOIN
SELECT e.*, u.name
FROM events e
RIGHT JOIN users u ON e.user_id = u.id;

-- FULL OUTER JOIN
SELECT e.*, u.name
FROM events e
FULL OUTER JOIN users u ON e.user_id = u.id;
```

**注意事项：**

1. **小表放在右边**
```sql
-- 推荐：小表在右，加载到内存
SELECT e.*, d.dict_value
FROM events e  -- 大表
LEFT JOIN dict_table d ON e.dict_id = d.id;  -- 小表
```

2. **使用字典替代 JOIN（推荐）**
```sql
-- 创建字典
CREATE DICTIONARY users_dict (
    id UInt64,
    name String
) PRIMARY KEY id
SOURCE(CLICKHOUSE(HOST 'localhost' PORT 9000 DB 'default' TABLE 'users'))
LAYOUT(HASHED())
LIFETIME(1 HOUR);

-- 使用字典（性能更好）
SELECT
    e.*,
    dictGet('users_dict', 'name', e.user_id) AS user_name
FROM events e;
```

3. **分布式 JOIN**
```sql
-- 本地 JOIN（每个分片独立执行）
SELECT * FROM events_distributed e
LOCAL JOIN users u ON e.user_id = u.id;

-- 全局 JOIN（广播小表到所有分片）
SELECT * FROM events_distributed e
GLOBAL JOIN users u ON e.user_id = u.id;
```

4. **避免大表 JOIN 大表**
- 性能差，内存消耗大
- 考虑使用物化视图预计算

**评分要点：**
- JOIN 类型（1分）
- 小表在右原则（2分）
- 字典替代 JOIN（2分）
- 分布式 JOIN（2分）
- 性能注意事项（1分）

---

**Q5：ClickHouse 中如何处理时间序列数据？**

**答：**

**1. 表设计**
```sql
CREATE TABLE metrics (
    metric_time DateTime,
    metric_name LowCardinality(String),
    host LowCardinality(String),
    value Float64
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(metric_time)  -- 按天分区
ORDER BY (metric_name, host, metric_time)
TTL metric_time + INTERVAL 30 DAY;  -- 保留30天
```

**2. 时间函数**
```sql
-- 时间截断
SELECT
    toStartOfMinute(metric_time) AS minute,
    avg(value) AS avg_value
FROM metrics
WHERE metric_name = 'cpu_usage'
GROUP BY minute;

-- 时间窗口
SELECT
    toStartOfInterval(metric_time, INTERVAL 5 MINUTE) AS window_start,
    avg(value) AS avg_value
FROM metrics
GROUP BY window_start;

-- 时间差计算
SELECT
    metric_time,
    dateDiff('second', metric_time, lagInFrame(metric_time) OVER (ORDER BY metric_time)) AS interval_seconds
FROM metrics;
```

**3. 时序聚合**
```sql
-- 降采样（从秒级到分钟级）
CREATE MATERIALIZED VIEW metrics_minute
ENGINE = AggregatingMergeTree()
ORDER BY (metric_name, host, minute)
AS SELECT
    toStartOfMinute(metric_time) AS minute,
    metric_name,
    host,
    avgState(value) AS avg_value,
    maxState(value) AS max_value,
    minState(value) AS min_value
FROM metrics
GROUP BY minute, metric_name, host;

-- 查询聚合结果
SELECT
    minute,
    avgMerge(avg_value) AS avg_value,
    maxMerge(max_value) AS max_value
FROM metrics_minute
WHERE metric_name = 'cpu_usage'
GROUP BY minute;
```

**评分要点：**
- 表设计（分区、排序键）（2分）
- 时间函数使用（2分）
- 降采样方法（2分）
- 物化视图预聚合（2分）

---

**Q6：ClickHouse 的数组和嵌套数据结构如何使用？**

**答：**

**1. 数组类型**
```sql
-- 创建包含数组的表
CREATE TABLE events (
    event_date Date,
    user_id UInt64,
    tags Array(String),
    scores Array(Float64)
) ENGINE = MergeTree()
ORDER BY (event_date, user_id);

-- 插入数据
INSERT INTO events VALUES (
    '2024-01-15',
    123,
    ['tag1', 'tag2', 'tag3'],
    [0.8, 0.9, 0.7]
);

-- 数组函数
SELECT
    user_id,
    tags,
    arrayJoin(tags) AS single_tag,  -- 展开数组
    has(tags, 'tag1') AS has_tag1,  -- 判断包含
    length(tags) AS tag_count,      -- 数组长度
    arrayElement(tags, 1) AS first_tag  -- 取元素
FROM events;
```

**2. 嵌套数据结构（Nested）**
```sql
-- 创建嵌套结构表
CREATE TABLE users (
    user_id UInt64,
    devices Nested (
        device_id String,
        device_type String,
        last_login DateTime
    )
) ENGINE = MergeTree()
ORDER BY user_id;

-- 插入数据
INSERT INTO users VALUES (
    123,
    ['device1', 'device2'],
    ['mobile', 'desktop'],
    ['2024-01-15 10:00:00', '2024-01-15 11:00:00']
);

-- 查询嵌套数据
SELECT
    user_id,
    devices.device_id,
    devices.device_type
FROM users
ARRAY JOIN devices;  -- 展开嵌套结构
```

**3. Map 类型**
```sql
CREATE TABLE configs (
    id UInt64,
    settings Map(String, String)
) ENGINE = MergeTree()
ORDER BY id;

INSERT INTO configs VALUES (1, {'key1': 'value1', 'key2': 'value2'});

SELECT
    id,
    settings['key1'] AS value1,
    mapKeys(settings) AS all_keys
FROM configs;
```

**评分要点：**
- 数组类型和函数（2分）
- arrayJoin 使用（2分）
- Nested 结构（2分）
- ARRAY JOIN 语法（1分）
- Map 类型（1分）

---

## 三、使用场景与选型

### 3.1 适用场景分析

| 场景 | ClickHouse 适用性 | 原因 |
|-----|------------------|------|
| **日志分析** | ⭐⭐⭐⭐⭐ | 写入快、查询快、压缩率高 |
| **用户行为分析** | ⭐⭐⭐⭐⭐ | 适合宽表、聚合快 |
| **实时数仓** | ⭐⭐⭐⭐⭐ | 实时写入、低延迟查询 |
| **BI 报表** | ⭐⭐⭐⭐⭐ | 多维分析、即席查询 |
| **时序数据** | ⭐⭐⭐⭐ | 适合监控指标、IoT |
| **点击流分析** | ⭐⭐⭐⭐⭐ | 高吞吐、快速聚合 |
| **OLTP 事务** | ⭐ | 不支持事务、更新删除成本高 |
| **频繁更新** | ⭐⭐ | Mutation 异步、性能差 |
| **高并发点查** | ⭐⭐ | 并发能力有限 |
| **小数据量** | ⭐⭐ | 优势不明显 |

### 3.2 与其他 OLAP 数据库对比

| 对比维度 | ClickHouse | Apache Druid | Apache Doris | Presto |
|---------|-----------|--------------|--------------|--------|
| **查询性能** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **写入性能** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **实时性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **SQL 支持** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **运维复杂度** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **社区活跃度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **适用规模** | PB 级 | PB 级 | PB 级 | PB 级 |

### 3.3 面试题

**Q1：ClickHouse 与 Elasticsearch 有什么区别？各自适用什么场景？**

**答：**

| 对比维度 | ClickHouse | Elasticsearch |
|---------|-----------|---------------|
| **定位** | OLAP 分析数据库 | 搜索引擎 |
| **存储方式** | 列式存储 | 行式存储（倒排索引） |
| **查询性能** | 聚合查询快 | 全文检索快 |
| **写入性能** | 批量写入快 | 近实时写入 |
| **全文检索** | 支持（有限） | 强项 |
| **聚合分析** | 强项 | 支持（性能一般） |
| **存储压缩** | 高（10:1+） | 低（2:1） |
| **资源消耗** | 低 | 高（内存占用大） |
| **适用场景** | 日志分析、报表 | 全文搜索、日志检索 |

**选择建议：**
- **ClickHouse**：需要快速聚合分析、报表统计、数据量大
- **Elasticsearch**：需要全文检索、复杂搜索、日志检索
- **混合使用**：ES 做检索，CH 做分析

**评分要点：**
- 定位差异（2分）
- 存储方式差异（2分）
- 查询性能差异（2分）
- 适用场景（2分）

---

**Q2：ClickHouse 适合做实时数仓吗？为什么？**

**答：**

**适合，原因如下：**

1. **实时写入能力**
   - 每秒可插入数百万行数据
   - 支持批量实时写入
   - 写入后立即可查询

2. **低延迟查询**
   - 毫秒级查询响应
   - 支持高并发查询（数百 QPS）
   - 适合实时报表和大屏

3. **物化视图**
   - 预计算聚合结果
   - 数据写入时自动更新
   - 加速实时查询

4. **数据时效性**
   - 支持 TTL 自动清理过期数据
   - 支持分区管理
   - 可设置数据保留策略

**实时数仓架构示例：**
```text
数据源 → Kafka → Flink（实时计算）→ ClickHouse（存储）→ 实时报表
```

**注意事项：**
- 避免高频小批量写入（建议每秒 1 次）
- 使用物化视图预聚合
- 合理设置分区和 TTL

**评分要点：**
- 实时写入能力（2分）
- 低延迟查询（2分）
- 物化视图（2分）
- 架构示例（1分）
- 注意事项（1分）

---

**Q3：ClickHouse 在日志分析场景中的优势是什么？**

**答：**

**核心优势：**

1. **高压缩率**
   - 列式存储 + LZ4/Zstd 压缩
   - 压缩比可达 10:1 以上
   - 节省存储空间

2. **快速写入**
   - 每秒可写入数百万行日志
   - 批量写入性能优异
   - 支持实时日志接入

3. **快速查询**
   - 毫秒级查询响应
   - 支持 PB 级数据
   - 适合即席查询

4. **丰富的分析函数**
   - 时间序列函数
   - 聚合函数
   - 窗口函数
   - 数组函数

5. **数据生命周期管理**
   - TTL 自动清理
   - 分区管理
   - 冷热数据分离

**典型应用：**
- Web 访问日志分析
- 应用日志分析
- 安全日志分析
- 系统监控日志

**评分要点：**
- 压缩率优势（2分）
- 写入性能（2分）
- 查询性能（2分）
- 分析函数（1分）
- 生命周期管理（1分）

---

**Q4：ClickHouse 与 MySQL 如何配合使用？**

**答：**

**配合模式：**

```text
MySQL（OLTP）→ 数据同步 → ClickHouse（OLAP）→ 分析查询
```

**1. 数据同步方案**

**方案一：Canal + Kafka + Flink**
```text
MySQL → Canal（binlog解析）→ Kafka → Flink（实时计算）→ ClickHouse
```

**方案二：ClickHouse MySQL 引擎**
```sql
-- 直接查询 MySQL 表
CREATE TABLE mysql_users
ENGINE = MySQL('mysql_host:3306', 'mydb', 'users', 'user', 'password');

SELECT * FROM mysql_users WHERE id > 1000;
```

**方案三：定期批量同步**
```bash
# 使用 clickhouse-mysql 工具
clickhouse-mysql \
  --src-host=mysql_host \
  --dst-host=clickhouse_host \
  --table-replicate=mydb.users
```

**2. 职责分工**

| 职责 | MySQL | ClickHouse |
|-----|-------|-----------|
| 数据存储 | 业务数据（订单、用户） | 分析数据（报表、统计） |
| 写入模式 | 单条/小批量写入 | 批量写入 |
| 查询模式 | 高并发点查 | 低并发分析查询 |
| 事务支持 | ACID 事务 | 无事务 |
| 数据更新 | 频繁更新 | 少量更新 |

**3. 典型架构**
```text
用户请求 → MySQL（写入订单）
         → 同步到 ClickHouse
         → 运营人员查询 ClickHouse（报表分析）
```

**评分要点：**
- 数据同步方案（3分）
- 职责分工（2分）
- 架构示例（2分）
- 工具使用（1分）

---

**Q5：ClickHouse 适合做用户画像系统吗？如何设计？**

**答：**

**适合，设计方案如下：**

**1. 表结构设计**
```sql
-- 用户画像宽表
CREATE TABLE user_profile (
    stat_date Date,
    user_id UInt64,
    -- 基础属性
    age UInt8,
    gender LowCardinality(String),
    city LowCardinality(String),
    -- 行为属性
    total_orders UInt32,
    total_amount Decimal(10,2),
    last_login_date Date,
    -- 标签
    tags Array(LowCardinality(String)),
    -- 偏好
    preference_categories Array(LowCardinality(String))
) ENGINE = ReplacingMergeTree()
PARTITION BY toYYYYMM(stat_date)
ORDER BY (stat_date, user_id);
```

**2. 标签计算**
```sql
-- 物化视图：每日用户行为统计
CREATE MATERIALIZED VIEW user_daily_stats
ENGINE = SummingMergeTree()
ORDER BY (stat_date, user_id)
AS SELECT
    toDate(event_time) AS stat_date,
    user_id,
    count() AS event_count,
    sum(amount) AS total_amount,
    uniq(category) AS category_count
FROM user_events
GROUP BY stat_date, user_id;

-- 标签生成
INSERT INTO user_profile
SELECT
    today() AS stat_date,
    user_id,
    25 AS age,  -- 从其他系统获取
    'male' AS gender,
    'Beijing' AS city,
    event_count AS total_orders,
    total_amount,
    today() AS last_login_date,
    ['high_value', 'active'] AS tags,
    ['electronics', 'books'] AS preference_categories
FROM user_daily_stats
WHERE stat_date = today();
```

**3. 查询应用**
```sql
-- 查询高价值用户
SELECT user_id, total_amount, tags
FROM user_profile
WHERE stat_date = today()
  AND has(tags, 'high_value')
ORDER BY total_amount DESC
LIMIT 100;

-- 用户分群统计
SELECT
    arrayJoin(tags) AS tag,
    count() AS user_count,
    avg(total_amount) AS avg_amount
FROM user_profile
WHERE stat_date = today()
GROUP BY tag;
```

**优势：**
- 宽表结构，查询无需 JOIN
- 列式存储，压缩率高
- 快速聚合分析
- 支持数组类型（标签）

**评分要点：**
- 表结构设计（2分）
- 标签计算方法（2分）
- 物化视图使用（2分）
- 查询示例（2分）

---

**Q6：ClickHouse 适合做推荐系统吗？有什么限制？**

**答：**

**部分适合，有限制：**

**适合的场景：**

1. **离线特征计算**
```sql
-- 用户特征统计
CREATE MATERIALIZED VIEW user_features
ENGINE = SummingMergeTree()
ORDER BY user_id
AS SELECT
    user_id,
    count() AS total_views,
    uniq(item_id) AS unique_items,
    avg(duration) AS avg_duration,
    groupArray(category) AS categories
FROM user_behavior
GROUP BY user_id;
```

2. **物品特征统计**
```sql
-- 物品特征统计
CREATE MATERIALIZED VIEW item_features
ENGINE = SummingMergeTree()
ORDER BY item_id
AS SELECT
    item_id,
    count() AS total_views,
    uniq(user_id) AS unique_users,
    avg(rating) AS avg_rating
FROM item_behavior
GROUP BY item_id;
```

3. **召回结果存储**
```sql
-- 存储召回结果
CREATE TABLE recall_results (
    user_id UInt64,
    item_ids Array(UInt64),
    scores Array(Float64),
    update_time DateTime
) ENGINE = ReplacingMergeTree()
ORDER BY user_id;
```

**不适合的场景：**

1. **实时特征计算**
   - 延迟较高（秒级）
   - 不适合毫秒级实时计算

2. **模型训练**
   - 不是机器学习框架
   - 需要配合 Spark/Python

3. **向量检索**
   - 不支持向量索引
   - 需要使用 Milvus/Faiss

**推荐架构：**
```text
ClickHouse（特征存储）→ Spark（模型训练）→ Redis（在线服务）→ 推荐结果
```

**评分要点：**
- 适合场景（3分）
- 不适合场景（2分）
- 架构示例（2分）
- 限制说明（1分）

---

## 四、性能优化

### 4.1 查询优化

**1. 分区裁剪**
```sql
-- 推荐：指定分区
SELECT * FROM events
WHERE event_date = '2024-01-15';

-- 不推荐：全表扫描
SELECT * FROM events
WHERE user_id = 123;
```

**2. 索引优化**
```sql
-- 排序键设计（高频查询字段）
ORDER BY (event_date, user_id, event_type)

-- 跳数索引（二级索引）
CREATE TABLE events (
    event_date Date,
    user_id UInt64,
    event_type String,
    INDEX idx_type event_type TYPE set(10) GRANULARITY 3
) ENGINE = MergeTree()
ORDER BY (event_date, user_id);
```

**3. 预计算（物化视图）**
```sql
-- 预聚合加速查询
CREATE MATERIALIZED VIEW daily_stats
ENGINE = SummingMergeTree()
ORDER BY event_date
AS SELECT
    event_date,
    count() AS event_count
FROM events
GROUP BY event_date;
```

**4. 避免 SELECT ***
```sql
-- 推荐：只查询需要的列
SELECT event_date, user_id FROM events;

-- 不推荐：查询所有列
SELECT * FROM events;
```

### 4.2 表引擎选择

| 场景 | 推荐引擎 | 原因 |
|-----|---------|------|
| 日志存储 | MergeTree | 基础引擎，性能最好 |
| 维度表 | ReplacingMergeTree | 自动去重 |
| 实时汇总 | SummingMergeTree | 自动求和 |
| 物化视图 | AggregatingMergeTree | 支持聚合函数 |
| 需要更新删除 | CollapsingMergeTree | 支持行级更新删除 |

### 4.3 数据分区策略

**1. 按时间分区（最常用）**
```sql
PARTITION BY toYYYYMM(event_date)  -- 按月
PARTITION BY toYYYYMMDD(event_date)  -- 按天
PARTITION BY toYear(event_date)  -- 按年
```

**2. 分区粒度选择**
- 数据量 < 1000 万：不分区或按年
- 数据量 1000 万 - 1 亿：按月
- 数据量 > 1 亿：按天

**3. 分区管理**
```sql
-- 查看分区
SELECT partition, count() FROM events GROUP BY partition;

-- 删除旧分区
ALTER TABLE events DROP PARTITION 202301;

-- 重建分区
ALTER TABLE events OPTIMIZE PARTITION 202401;
```

### 4.4 面试题

**Q1：ClickHouse 查询性能优化的主要方法有哪些？**

**答：**

**1. 分区裁剪**
```sql
-- 查询条件包含分区键
WHERE event_date = '2024-01-15'
```

**2. 索引优化**
- 合理设计排序键（ORDER BY）
- 使用跳数索引（二级索引）
- 避免索引失效（函数运算、类型转换）

**3. 预计算**
- 使用物化视图预聚合
- 提前计算常用指标

**4. 查询优化**
- 避免 SELECT *
- 使用 LIMIT 限制结果集
- 避免大表 JOIN
- 使用字典替代 JOIN

**5. 数据模型优化**
- 使用 LowCardinality 类型
- 合理设计数据类型
- 避免过度嵌套

**6. 资源配置**
- 调整 max_threads（并发线程数）
- 调整 max_memory_usage（内存限制）
- 使用缓存（mark_cache）

**评分要点：**
- 分区裁剪（2分）
- 索引优化（2分）
- 预计算（2分）
- 查询优化（2分）

---

**Q2：如何选择合适的表引擎？**

**答：**

**选择原则：**

| 需求 | 推荐引擎 | 说明 |
|-----|---------|------|
| 纯写入、查询 | MergeTree | 基础引擎，性能最好 |
| 需要去重 | ReplacingMergeTree | 按主键去重，保留最新 |
| 需要汇总 | SummingMergeTree | 数值列自动求和 |
| 需要聚合 | AggregatingMergeTree | 配合物化视图 |
| 需要更新删除 | CollapsingMergeTree | 通过行标记实现 |
| 时序数据 | GraphiteMergeTree | 存储 Graphite 数据 |

**选择流程：**
1. 是否需要更新删除？
   - 是 → CollapsingMergeTree
   - 否 → 继续
2. 是否需要预聚合？
   - 是 → AggregatingMergeTree / SummingMergeTree
   - 否 → 继续
3. 是否需要去重？
   - 是 → ReplacingMergeTree
   - 否 → MergeTree

**评分要点：**
- 列举主要引擎（2分）
- 说明各引擎特点（3分）
- 给出选择原则（2分）
- 选择流程（1分）

---

**Q3：ClickHouse 的分区策略如何设计？**

**答：**

**1. 分区键选择**
```sql
-- 按时间分区（最常用）
PARTITION BY toYYYYMM(event_date)  -- 按月
PARTITION BY toYYYYMMDD(event_date)  -- 按天

-- 按业务维度分区
PARTITION BY region  -- 按地区
```

**2. 分区粒度**
- 数据量 < 1000 万：不分区或按年
- 数据量 1000 万 - 1 亿：按月
- 数据量 > 1 亿：按天

**3. 分区数量**
- 建议：100-1000 个分区
- 过多：元数据管理开销大
- 过少：分区裁剪效果差

**4. 分区管理**
```sql
-- 查看分区
SELECT partition, count() FROM events GROUP BY partition;

-- 删除旧分区（TTL）
ALTER TABLE events DROP PARTITION 202301;

-- 自动清理（TTL）
TTL event_date + INTERVAL 3 MONTH
```

**评分要点：**
- 分区键选择（2分）
- 分区粒度（2分）
- 分区数量建议（2分）
- 分区管理（2分）

---

**Q4：ClickHouse 的索引机制是怎样的？如何优化？**

**答：**

**1. 稀疏索引（主键索引）**
- 基于排序键（ORDER BY）构建
- 每 8192 行（index_granularity）一个索引项
- 索引项存储：主键值 → 数据块位置

**2. 跳数索引（二级索引）**
```sql
CREATE TABLE events (
    event_date Date,
    user_id UInt64,
    event_type String,
    -- 跳数索引
    INDEX idx_type event_type TYPE set(10) GRANULARITY 3,
    INDEX idx_user user_id TYPE minmax GRANULARITY 3
) ENGINE = MergeTree()
ORDER BY (event_date, user_id);
```

**索引类型：**
- `set`：集合索引，适合低基数字段
- `minmax`：范围索引，适合数值字段
- `ngrambf_v1`：字符串索引
- `bloom_filter`：布隆过滤器索引

**3. 索引优化**
- 合理设计排序键（高频查询字段在前）
- 使用跳数索引加速过滤
- 避免索引失效（函数运算、类型转换）
- 调整 index_granularity（默认 8192）

**评分要点：**
- 稀疏索引原理（2分）
- 跳数索引类型（3分）
- 索引优化方法（2分）
- 避免索引失效（1分）

---

**Q5：ClickHouse 的内存管理策略是什么？**

**答：**

**1. 内存限制配置**
```xml
<!-- config.xml -->
<max_memory_usage>10000000000</max_memory_usage>  <!-- 10GB -->
<max_memory_usage_for_all_queries>20000000000</max_memory_usage_for_all_queries>  <!-- 20GB -->
```

**2. 内存使用场景**
- **查询执行**：JOIN、GROUP BY、ORDER BY
- **索引缓存**：mark_cache（索引块缓存）
- **字典缓存**：dict_cache（字典数据缓存）

**3. 内存优化**
```sql
-- 调整并发线程数
SET max_threads = 8;

-- 调整内存限制
SET max_memory_usage = 10000000000;

-- 使用外部聚合（数据量大时）
SET max_bytes_before_external_group_by = 1000000000;

-- 使用外部排序
SET max_bytes_before_external_sort = 1000000000;
```

**4. 内存监控**
```sql
-- 查看内存使用
SELECT
    metric,
    value
FROM system.asynchronous_metrics
WHERE metric LIKE '%Memory%';

-- 查看查询内存使用
SELECT
    query_id,
    memory_usage
FROM system.query_log
WHERE type = 'QueryFinish'
ORDER BY memory_usage DESC
LIMIT 10;
```

**评分要点：**
- 内存限制配置（2分）
- 内存使用场景（2分）
- 内存优化方法（2分）
- 内存监控（2分）

---

**Q6：ClickHouse 如何处理大数据量的 JOIN？**

**答：**

**问题：** 大表 JOIN 大表会导致内存溢出或性能下降。

**解决方案：**

**1. 小表放在右边**
```sql
-- 推荐：小表在右，加载到内存
SELECT e.*, d.dict_value
FROM events e  -- 大表
LEFT JOIN dict_table d ON e.dict_id = d.id;  -- 小表
```

**2. 使用字典替代 JOIN**
```sql
-- 创建字典
CREATE DICTIONARY users_dict (
    id UInt64,
    name String
) PRIMARY KEY id
SOURCE(CLICKHOUSE(HOST 'localhost' PORT 9000 DB 'default' TABLE 'users'))
LAYOUT(HASHED())
LIFETIME(1 HOUR);

-- 使用字典（性能更好）
SELECT
    e.*,
    dictGet('users_dict', 'name', e.user_id) AS user_name
FROM events e;
```

**3. 预计算（物化视图）**
```sql
-- 提前计算 JOIN 结果
CREATE MATERIALIZED VIEW events_with_user
ENGINE = MergeTree()
ORDER BY (event_date, user_id)
AS SELECT
    e.event_date,
    e.user_id,
    u.user_name,
    e.event_type
FROM events e
LEFT JOIN users u ON e.user_id = u.id;
```

**4. 分布式 JOIN**
```sql
-- 全局 JOIN（广播小表到所有分片）
SELECT * FROM events_distributed e
GLOBAL JOIN users u ON e.user_id = u.id;
```

**5. 避免大表 JOIN**
- 使用宽表设计
- 使用嵌套数据结构
- 使用数组类型

**评分要点：**
- 小表在右原则（2分）
- 字典替代 JOIN（2分）
- 物化视图预计算（2分）
- 分布式 JOIN（1分）
- 避免大表 JOIN（1分）

### 4.5 项目案例

---

#### 案例一：Web 日志分析系统性能优化

**项目背景：** 某电商平台日均产生 50 亿条 Web 访问日志，原始架构使用 Elasticsearch 存储，查询 7 天数据的 PV/UV 耗时 30 秒以上，无法满足运营实时分析需求。

**原始架构问题：**

| 问题 | 表现 | 影响 |
|-----|------|------|
| 存储成本高 | 7 天日志占用 2TB 磁盘 | 运维成本大 |
| 聚合查询慢 | 7 天 PV/UV 查询 > 30s | 运营无法实时分析 |
| 数据保留短 | 只能保留 7 天数据 | 无法做长期趋势分析 |
| 并发能力弱 | 5 个并发查询即超时 | 多人同时使用卡顿 |

**优化方案：**

```text
┌──────────────────────────────────────────────────────┐
│                  优化后架构                            │
├──────────────────────────────────────────────────────┤
│  Nginx 日志 → Filebeat → Kafka → ClickHouse → Grafana │
│                                          ↓            │
│                                    物化视图预聚合       │
└──────────────────────────────────────────────────────┘
```

**实施步骤：**

**Step 1：设计优化表结构**

```sql
-- 原始表（ES 同步过来的宽表，未优化）
CREATE TABLE raw_logs (
    timestamp DateTime,
    user_id String,
    url String,
    status UInt16,
    response_time UInt32,
    user_agent String,
    ip String,
    referer String
) ENGINE = MergeTree()
ORDER BY timestamp;
-- 问题：排序键单薄，查询常需全表扫描

-- 优化后的表结构
CREATE TABLE access_logs (
    event_date Date,
    event_time DateTime,
    user_id UInt64,
    url String,
    url_path LowCardinality(String),      -- 路径提取为低基数列
    status UInt16,
    response_time UInt32,
    country LowCardinality(String),       -- IP 解析为低基数列
    device_type LowCardinality(String),   -- UA 解析为低基数列
    browser LowCardinality(String)
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_date)       -- 按天分区
ORDER BY (event_date, url_path, status)   -- 高频查询字段做排序键
TTL event_date + INTERVAL 90 DAY         -- 保留 90 天
SETTINGS index_granularity = 8192;
```

**Step 2：添加跳数索引加速过滤**

```sql
-- 对响应时间范围查询添加 minmax 索引
ALTER TABLE access_logs
ADD INDEX idx_response_time response_time TYPE minmax GRANULARITY 4;

-- 对状态码添加 set 索引
ALTER TABLE access_logs
ADD INDEX idx_status status TYPE set(10) GRANULARITY 4;
```

**Step 3：创建分层物化视图**

```sql
-- 一级聚合：分钟级 PV/UV
CREATE MATERIALIZED VIEW access_stats_minute
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(event_date)
ORDER BY (event_date, minute, url_path)
AS SELECT
    event_date,
    toStartOfMinute(event_time) AS minute,
    url_path,
    status,
    countState() AS pv,
    uniqState(user_id) AS uv,
    avgState(response_time) AS avg_response,
    quantileState(0.95)(response_time) AS p95_response
FROM access_logs
GROUP BY event_date, minute, url_path, status;

-- 二级聚合：小时级汇总（从分钟级聚合）
CREATE MATERIALIZED VIEW access_stats_hour
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(event_date)
ORDER BY (event_date, hour, url_path)
AS SELECT
    event_date,
    toStartOfHour(minute) AS hour,
    url_path,
    countMerge(pv) AS pv,
    uniqMerge(uv) AS uv,
    avgMerge(avg_response) AS avg_response,
    quantileMerge(0.95)(p95_response) AS p95_response
FROM access_stats_minute
GROUP BY event_date, hour, url_path;
```

**Step 4：查询对比**

```sql
-- 优化前：直接查询原始表（30s+）
SELECT
    toDate(event_time) AS day,
    count() AS pv,
    uniq(user_id) AS uv
FROM raw_logs
WHERE event_time BETWEEN '2024-01-01' AND '2024-01-07'
GROUP BY day;

-- 优化后：查询物化视图（< 100ms）
SELECT
    event_date AS day,
    sum(pv) AS pv,
    uniqMerge(uv) AS uv
FROM access_stats_hour
WHERE event_date BETWEEN '2024-01-01' AND '2024-01-07'
  AND url_path = '/product/detail'
GROUP BY day;
```

**效果评估：**

| 指标 | 优化前（ES） | 优化后（CH） | 提升倍数 |
|-----|------------|------------|---------|
| 7 天 PV/UV 查询 | 30s+ | < 100ms | **300x** |
| 存储空间（7天） | 2TB | 150GB（压缩后） | **13x 压缩** |
| 数据保留时长 | 7 天 | 90 天 | **12x** |
| 并发查询能力 | 5 QPS | 50 QPS | **10x** |
| 写入吞吐 | 5 万条/秒 | 50 万条/秒 | **10x** |
| 硬件成本 | 5 台高配服务器 | 3 台中配服务器 | **降低 40%** |

---

#### 案例二：实时数仓大屏报表优化

**项目背景：** 某金融平台需要展示实时交易大屏，包含交易金额、笔数、成功率、区域分布等 20+ 指标。原方案使用 MySQL 存储聚合结果，每分钟跑一次定时任务计算，数据延迟 1 分钟以上，且高峰时段计算超时。

**原始架构问题：**

```text
MySQL 交易表 → 定时任务（每分钟）→ 聚合计算 → 写入 MySQL 报表表 → 大屏展示
问题：定时任务执行 30s+，数据延迟 1-2 分钟，高峰时计算失败
```

**优化方案：**

```text
交易系统 → Kafka → Flink(实时ETL) → ClickHouse → 物化视图(实时聚合) → 大屏直接查询
延迟：秒级（从写入到可查询 < 1 秒）
```

**实施步骤：**

**Step 1：交易明细表设计**

```sql
CREATE TABLE transactions (
    txn_date Date,
    txn_time DateTime64(3),          -- 毫秒级精度
    txn_id String,
    user_id UInt64,
    merchant_id UInt64,
    amount Decimal(18, 2),
    txn_type LowCardinality(String),  -- 支付/退款/转账
    status LowCardinality(String),    -- 成功/失败/处理中
    channel LowCardinality(String),   -- 渠道
    region LowCardinality(String),    -- 区域
    currency LowCardinality(String)
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(txn_date)
ORDER BY (txn_date, txn_type, status, region)
TTL txn_date + INTERVAL 180 DAY;
```

**Step 2：多粒度物化视图（实时聚合链路）**

```sql
-- 分钟级实时聚合（大屏核心数据源）
CREATE MATERIALIZED VIEW txn_stats_minute
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(txn_date)
ORDER BY (txn_date, minute, txn_type, region)
AS SELECT
    txn_date,
    toStartOfMinute(txn_time) AS minute,
    txn_type,
    region,
    channel,
    status,
    countState() AS txn_count,
    sumState(amount) AS txn_amount,
    uniqState(user_id) AS txn_users,
    uniqState(merchant_id) AS txn_merchants
FROM transactions
GROUP BY txn_date, minute, txn_type, region, channel, status;

-- 大屏查询 SQL（从物化视图查询，毫秒级响应）
SELECT
    minute,
    sum(txn_count) AS total_count,
    sum(txn_amount) AS total_amount,
    uniqMerge(txn_users) AS total_users,
    -- 成功率计算
    sumIf(txn_count, status = '成功') / sum(txn_count) AS success_rate
FROM txn_stats_minute
WHERE txn_date = today()
  AND minute >= now() - INTERVAL 1 HOUR
GROUP BY minute
ORDER BY minute;
```

**Step 3：热点数据预加载（字典加速）**

```sql
-- 商户信息字典（减少 JOIN）
CREATE DICTIONARY merchant_dict (
    merchant_id UInt64,
    merchant_name String,
    category LowCardinality(String)
) PRIMARY KEY merchant_id
SOURCE(CLICKHOUSE(
    HOST 'localhost' PORT 9000
    DB 'analytics' TABLE 'merchants'
))
LAYOUT(FLAT())
LIFETIME(1 HOUR);

-- 查询时直接使用字典
SELECT
    minute,
    dictGet('merchant_dict', 'merchant_name', merchant_id) AS merchant_name,
    sum(txn_amount) AS amount
FROM txn_stats_minute
WHERE txn_date = today()
GROUP BY minute, merchant_id
ORDER BY amount DESC
LIMIT 10;
```

**Step 4：冷热数据分离**

```sql
-- 热数据：近 7 天，SSD 存储，LZ4 快速压缩
CREATE TABLE transactions_hot AS transactions
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(txn_date)
ORDER BY (txn_date, txn_type, status, region)
TTL txn_date + INTERVAL 7 DAY TO VOLUME 'cold'
SETTINGS storage_policy = 'hot_and_cold';

-- 冷数据：7 天以前，HDD 存储，ZSTD 高压缩比
-- 通过 TTL 自动迁移到冷存储卷
```

**效果评估：**

| 指标 | 优化前（MySQL） | 优化后（CH） | 提升 |
|-----|---------------|------------|------|
| 数据延迟 | 1-2 分钟 | < 1 秒 | **100x** |
| 大屏刷新时间 | 3-5 秒 | < 50ms | **100x** |
| 高峰计算成功率 | 85% | 100% | 稳定 |
| 存储成本 | 500GB（SSD） | 200GB（SSD+HDD） | **降低 60%** |
| 支持指标数 | 10 个 | 20+ 个 | **2x** |
| 历史数据回溯 | 30 天 | 180 天 | **6x** |

---

#### 案例三：多维度用户行为分析优化

**项目背景：** 某内容平台需要分析用户行为漏斗（浏览→点击→收藏→购买），涉及 10+ 维度交叉分析（时间、渠道、内容类型、用户画像等）。原方案使用 Hive/Spark 离线计算，T+1 产出，业务方要求实时分析能力。

**原始架构问题：**

| 问题 | 表现 |
|-----|------|
| 数据延迟 | T+1，当天行为第二天才能分析 |
| 查询复杂度 | 10+ 维度交叉分析，Spark SQL 执行 10 分钟+ |
| 多维组合爆炸 | 预处理所有维度组合需要 200+ 张表 |
| 存储冗余 | 预计算表占用 5TB+ |

**优化方案：**

采用 ClickHouse 宽表 + 投影（Projection） + 物化视图的组合策略，避免维度组合爆炸。

**实施步骤：**

**Step 1：设计用户行为宽表**

```sql
CREATE TABLE user_behaviors (
    event_date Date,
    event_time DateTime64(3),
    user_id UInt64,
    session_id String,
    -- 行为类型
    event_type LowCardinality(String),   -- view / click / favorite / purchase
    -- 内容维度
    content_id UInt64,
    content_type LowCardinality(String), -- 文章/视频/直播
    category LowCardinality(String),     -- 分类
    author_id UInt64,
    -- 渠道维度
    channel LowCardinality(String),      -- 渠道
    device_type LowCardinality(String),  -- 设备
    os LowCardinality(String),           -- 操作系统
    -- 用户画像维度（冗余到行为表）
    user_gender LowCardinality(String),
    user_age_group LowCardinality(String),
    user_city LowCardinality(String),
    -- 行为指标
    duration UInt32,                     -- 停留时长（秒）
    scroll_depth Float32,                -- 滚动深度
    interaction_count UInt8              -- 互动次数
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_date)
ORDER BY (event_date, event_type, content_type, category)
SETTINGS index_granularity = 8192;
```

**Step 2：创建投影（Projection）优化多维度查询**

```sql
-- 投影 1：按渠道+设备维度聚合
ALTER TABLE user_behaviors
ADD PROJECTION proj_channel_device (
    SELECT
        event_date,
        channel,
        device_type,
        event_type,
        count(),
        uniq(user_id),
        avg(duration)
    GROUP BY event_date, channel, device_type, event_type
);

-- 投影 2：按用户画像维度聚合
ALTER TABLE user_behaviors
ADD PROJECTION proj_user_profile (
    SELECT
        event_date,
        user_gender,
        user_age_group,
        user_city,
        event_type,
        count(),
        uniq(user_id),
        avg(duration)
    GROUP BY event_date, user_gender, user_age_group, user_city, event_type
);

-- 投影 3：按内容维度聚合
ALTER TABLE user_behaviors
ADD PROJECTION proj_content (
    SELECT
        event_date,
        content_type,
        category,
        event_type,
        count(),
        uniq(user_id),
        uniq(content_id),
        avg(duration)
    GROUP BY event_date, content_type, category, event_type
);
```

**Step 3：漏斗分析物化视图**

```sql
-- 用户行为漏斗实时计算
CREATE MATERIALIZED VIEW behavior_funnel
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(event_date)
ORDER BY (event_date, hour, content_type, channel)
AS SELECT
    event_date,
    toStartOfHour(event_time) AS hour,
    content_type,
    channel,
    -- 漏斗各阶段计数
    countIfState(event_type = 'view') AS view_count,
    countIfState(event_type = 'click') AS click_count,
    countIfState(event_type = 'favorite') AS favorite_count,
    countIfState(event_type = 'purchase') AS purchase_count,
    -- 用户数
    uniqIfState(user_id, event_type = 'view') AS view_users,
    uniqIfState(user_id, event_type = 'click') AS click_users,
    uniqIfState(user_id, event_type = 'favorite') AS favorite_users,
    uniqIfState(user_id, event_type = 'purchase') AS purchase_users
FROM user_behaviors
GROUP BY event_date, hour, content_type, channel;

-- 漏斗转化率查询（毫秒级响应）
SELECT
    content_type,
    channel,
    countMerge(view_count) AS views,
    countMerge(click_count) AS clicks,
    countMerge(favorite_count) AS favorites,
    countMerge(purchase_count) AS purchases,
    -- 各阶段转化率
    round(clicks / views * 100, 2) AS view_to_click_rate,
    round(favorites / clicks * 100, 2) AS click_to_favorite_rate,
    round(purchases / favorites * 100, 2) AS favorite_to_purchase_rate,
    round(purchases / views * 100, 2) AS overall_conversion_rate
FROM behavior_funnel
WHERE event_date = today()
  AND hour >= now() - INTERVAL 24 HOUR
GROUP BY content_type, channel
ORDER BY views DESC;
```

**Step 4：查询性能对比**

```sql
-- 场景 1：按渠道+设备+用户画像三维交叉分析
-- 优化前（Spark SQL）：10 分钟+
-- 优化后（ClickHouse 投影）：< 500ms
SELECT
    channel,
    device_type,
    user_age_group,
    count() AS pv,
    uniq(user_id) AS uv,
    avg(duration) AS avg_duration
FROM user_behaviors
WHERE event_date BETWEEN '2024-01-01' AND '2024-01-07'
  AND event_type = 'view'
GROUP BY channel, device_type, user_age_group
ORDER BY pv DESC;

-- 场景 2：实时漏斗分析（过去 1 小时）
-- 优化前：无法实时计算
-- 优化后：< 100ms
SELECT
    toStartOfInterval(event_time, INTERVAL 5 MINUTE) AS window_start,
    countIf(event_type = 'view') AS views,
    countIf(event_type = 'click') AS clicks,
    countIf(event_type = 'purchase') AS purchases,
    round(countIf(event_type = 'click') / countIf(event_type = 'view') * 100, 2) AS ctr
FROM user_behaviors
WHERE event_time >= now() - INTERVAL 1 HOUR
GROUP BY window_start
ORDER BY window_start;
```

**效果评估：**

| 指标 | 优化前（Hive/Spark） | 优化后（CH） | 提升 |
|-----|---------------------|------------|------|
| 数据时效 | T+1（24 小时延迟） | 实时（秒级） | **实时化** |
| 多维交叉查询 | 10 分钟+ | < 500ms | **1200x** |
| 漏斗分析 | 不支持实时 | < 100ms | **新增能力** |
| 存储空间 | 5TB（预计算表） | 800GB（宽表+投影） | **6x 压缩** |
| 预计算表数量 | 200+ 张 | 0（投影自动维护） | **零维护** |
| 查询并发 | 5 QPS | 30 QPS | **6x** |

---

#### 案例总结：性能优化核心方法论

| 优化维度 | 具体方法 | 适用场景 | 预期效果 |
|---------|---------|---------|---------|
| **数据模型** | 宽表设计、LowCardinality、合理分区 | 所有场景 | 减少 JOIN，提升压缩率 |
| **索引优化** | 排序键设计、跳数索引 | 条件过滤查询 | 跳过无关数据块 |
| **预计算** | 物化视图、投影（Projection） | 聚合查询、报表 | 10x-1000x 加速 |
| **字典加速** | 字典替代 JOIN | 维度表查询 | 避免 JOIN 开销 |
| **冷热分离** | SSD+HDD 分层存储 | 海量历史数据 | 降低存储成本 |
| **写入优化** | 批量写入、异步插入 | 高吞吐写入 | 百万行/秒写入 |

---

## 五、高级特性与实战

### 5.1 面试题

**Q1：ClickHouse 的物化视图有哪些类型？如何使用？**

**答：**

**1. 普通物化视图**
```sql
CREATE MATERIALIZED VIEW daily_stats
ENGINE = MergeTree()
ORDER BY event_date
AS SELECT
    event_date,
    count() AS event_count
FROM events
GROUP BY event_date;
```

**2. 带 TO 子句的物化视图**
```sql
-- 目标表已存在
CREATE TABLE daily_stats_table (
    event_date Date,
    event_count UInt64
) ENGINE = MergeTree()
ORDER BY event_date;

-- 物化视图写入目标表
CREATE MATERIALIZED VIEW daily_stats
TO daily_stats_table
AS SELECT
    event_date,
    count() AS event_count
FROM events
GROUP BY event_date;
```

**3. 聚合物化视图**
```sql
CREATE MATERIALIZED VIEW daily_stats
ENGINE = AggregatingMergeTree()
ORDER BY event_date
AS SELECT
    event_date,
    countState() AS event_count,
    sumState(duration) AS total_duration
FROM events
GROUP BY event_date;

-- 查询时需要使用 Merge 函数
SELECT
    event_date,
    countMerge(event_count) AS event_count,
    sumMerge(total_duration) AS total_duration
FROM daily_stats
GROUP BY event_date;
```

**评分要点：**
- 普通物化视图（2分）
- TO 子句物化视图（2分）
- 聚合物化视图（2分）
- 使用场景（2分）

---

**Q2：ClickHouse 如何实现数据的多租户隔离？**

**答：**

**方案一：数据库隔离**
```sql
-- 每个租户一个数据库
CREATE DATABASE tenant1;
CREATE DATABASE tenant2;

-- 权限控制
CREATE USER tenant1_user IDENTIFIED BY 'password';
GRANT ALL ON tenant1.* TO tenant1_user;
```

**方案二：表隔离**
```sql
-- 同一数据库，不同表
CREATE TABLE tenant1_events (...) ENGINE = MergeTree();
CREATE TABLE tenant2_events (...) ENGINE = MergeTree();
```

**方案三：字段隔离（推荐）**
```sql
-- 同一张表，通过租户字段隔离
CREATE TABLE events (
    tenant_id UInt32,
    event_date Date,
    user_id UInt64
) ENGINE = MergeTree()
ORDER BY (tenant_id, event_date, user_id);

-- 查询时强制加上租户条件
SELECT * FROM events WHERE tenant_id = 1;
```

**方案四：集群隔离**
- 大租户：独立集群
- 小租户：共享集群

**评分要点：**
- 数据库隔离（1分）
- 表隔离（2分）
- 字段隔离（3分）
- 集群隔离（1分）
- 权限控制（1分）

---

**Q3：ClickHouse 如何进行数据备份和恢复？**

**答：**

**1. 备份工具：clickhouse-backup**
```bash
# 安装
wget https://github.com/AlexAkulov/clickhouse-backup/releases/download/v2.0.0/clickhouse-backup-linux-amd64.tar.gz

# 创建备份
clickhouse-backup create 2024-01-15

# 查看备份
clickhouse-backup list

# 恢复备份
clickhouse-backup restore 2024-01-15

# 上传到远程存储
clickhouse-backup upload 2024-01-15
```

**2. 配置文件**
```yaml
# clickhouse-backup.yml
clickhouse:
  host: localhost
  port: 9000
  username: default
  password: ""

remote_storage: s3
s3:
  bucket: clickhouse-backup
  access_key: xxx
  secret_key: xxx
  region: us-east-1
```

**3. 定期备份**
```bash
# crontab 定期备份
0 2 * * * /usr/bin/clickhouse-backup create $(date +\%Y-\%m-\%d)
0 3 * * * /usr/bin/clickhouse-backup upload $(date +\%Y-\%m-\%d)
```

**4. 手动备份**
```sql
-- 导出表数据
SELECT * FROM events FORMAT CSV > events.csv

-- 导入表数据
cat events.csv | clickhouse-client --query="INSERT INTO events FORMAT CSV"
```

**评分要点：**
- clickhouse-backup 工具（3分）
- 配置文件（2分）
- 定期备份（2分）
- 手动备份（1分）

---

**Q4：ClickHouse 集群如何部署和运维？**

**答：**

**1. 集群架构**
```text
┌─────────────────────────────────────────┐
│           ClickHouse 集群               │
├─────────────────────────────────────────┤
│  ZooKeeper（元数据管理）                 │
├─────────────────────────────────────────┤
│  Shard 1          │  Shard 2            │
│  ├─ Replica 1     │  ├─ Replica 1       │
│  └─ Replica 2     │  └─ Replica 2       │
└─────────────────────────────────────────┘
```

**2. 部署步骤**
```bash
# 1. 安装 ClickHouse
curl https://clickhouse.com/ | sh

# 2. 配置集群（config.xml）
<clickhouse>
    <cluster>
        <node>
            <host>ch-node1</host>
            <port>9000</port>
        </node>
        <node>
            <host>ch-node2</host>
            <port>9000</port>
        </node>
    </cluster>
    
    <zookeeper>
        <node>
            <host>zk-node1</host>
            <port>2181</port>
        </node>
    </zookeeper>
</clickhouse>

# 3. 创建副本表
CREATE TABLE events ON CLUSTER cluster (
    event_date Date,
    user_id UInt64
) ENGINE = ReplicatedMergeTree(
    '/clickhouse/tables/{shard}/events',
    '{replica}'
)
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id);

# 4. 创建分布式表
CREATE TABLE events_distributed ON CLUSTER cluster AS events
ENGINE = Distributed(cluster, default, events, rand());
```

**3. 运维监控**
```sql
-- 查看集群状态
SELECT * FROM system.clusters;

-- 查看副本状态
SELECT * FROM system.replicas;

-- 查看查询性能
SELECT * FROM system.query_log WHERE type = 'QueryFinish';
```

**评分要点：**
- 集群架构（2分）
- 部署步骤（3分）
- 副本表配置（2分）
- 运维监控（1分）

---

**Q5：ClickHouse 如何处理数据倾斜问题？**

**答：**

**问题：** 数据分布不均匀，导致某些分片或节点负载过高。

**解决方案：**

**1. 优化分片键**
```sql
-- 不推荐：使用 user_id（可能集中在某些用户）
ENGINE = Distributed(cluster, default, events, user_id);

-- 推荐：使用随机数或哈希
ENGINE = Distributed(cluster, default, events, rand());
ENGINE = Distributed(cluster, default, events, cityHash64(user_id));
```

**2. 数据预处理**
```sql
-- 打散热点数据
INSERT INTO events
SELECT
    event_date,
    user_id,
    event_type,
    -- 添加随机后缀
    concat(event_type, '_', toString(rand() % 10)) AS event_type_shard
FROM events_source;
```

**3. 使用 ReplicatedMergeTree**
```sql
-- 副本分散到不同节点
CREATE TABLE events ON CLUSTER cluster (
    event_date Date,
    user_id UInt64
) ENGINE = ReplicatedMergeTree(
    '/clickhouse/tables/{shard}/events',
    '{replica}'
)
ORDER BY (event_date, user_id);
```

**4. 监控和调优**
```sql
-- 查看各分片数据量
SELECT
    shard_num,
    count() AS row_count,
    sum(bytes_on_disk) AS size_bytes
FROM cluster('cluster', system.parts)
GROUP BY shard_num;
```

**评分要点：**
- 优化分片键（2分）
- 数据预处理（2分）
- 副本分散（2分）
- 监控调优（2分）

---

**Q6：ClickHouse 的故障排查方法有哪些？**

**答：**

**1. 查看系统表**
```sql
-- 查看查询日志
SELECT * FROM system.query_log
WHERE type = 'ExceptionWhileProcessing'
ORDER BY event_time DESC
LIMIT 10;

-- 查看副本状态
SELECT * FROM system.replicas
WHERE is_readonly = 1 OR is_session_expired = 1;

-- 查看分区状态
SELECT * FROM system.parts
WHERE active = 0;

-- 查看进程状态
SELECT * FROM system.processes;
```

**2. 常用排查命令**
```bash
# 查看 ClickHouse 状态
systemctl status clickhouse-server

# 查看日志
tail -f /var/log/clickhouse-server/clickhouse-server.log

# 查看错误日志
tail -f /var/log/clickhouse-server/clickhouse-server.err.log

# 查看进程
ps aux | grep clickhouse
```

**3. 常见故障及处理**

| 故障 | 原因 | 处理方法 |
|-----|------|---------|
| 查询超时 | 数据量大、索引失效 | 优化查询、添加索引 |
| 内存溢出 | JOIN 过大、GROUP BY 数据量大 | 调整内存限制、使用外部聚合 |
| 副本不同步 | ZooKeeper 故障、网络问题 | 检查 ZooKeeper、重建副本 |
| 写入失败 | 磁盘满、权限问题 | 清理磁盘、检查权限 |

**4. 性能分析**
```sql
-- 查看查询执行计划
EXPLAIN PIPELINE SELECT * FROM events WHERE user_id = 123;

-- 查看查询性能指标
SELECT
    query_id,
    query_duration_ms,
    memory_usage,
    read_rows,
    written_rows
FROM system.query_log
WHERE type = 'QueryFinish'
ORDER BY query_duration_ms DESC
LIMIT 10;
```

**评分要点：**
- 系统表查询（3分）
- 常用命令（2分）
- 常见故障处理（2分）
- 性能分析（1分）

---

## 附录：快速参考

### ClickHouse 常用命令

```sql
-- 查看版本
SELECT version();

-- 查看数据库
SHOW DATABASES;

-- 查看表
SHOW TABLES;

-- 查看表结构
DESCRIBE events;

-- 查看分区
SELECT partition, count() FROM events GROUP BY partition;

-- 查看索引
SELECT * FROM system.data_skipping_indices WHERE table = 'events';

-- 查看集群
SELECT * FROM system.clusters;

-- 查看副本
SELECT * FROM system.replicas;
```

### 性能优化检查清单

- [ ] 合理设计分区键和排序键
- [ ] 使用合适的表引擎
- [ ] 使用物化视图预聚合
- [ ] 避免 SELECT *
- [ ] 使用 LowCardinality 类型
- [ ] 避免大表 JOIN
- [ ] 使用字典替代 JOIN
- [ ] 合理设置内存限制
- [ ] 监控查询性能
- [ ] 定期清理过期数据
