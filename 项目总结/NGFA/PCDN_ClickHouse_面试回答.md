# PCDN 项目 ClickHouse 选型与性能优化

## 一、项目背景

在 NGFA（新一代流量计费系统）的 PCDN 流量分析模块中，主要处理：

- DNS 流量数据
- 网络设备数据
- BGP 数据
- Radius 数据
- 多源流量关联数据

系统需要对大量流量数据进行：

- 数据查询
- 多维度统计
- 聚合分析
- 流量趋势分析
- 区域数据分析
- PCDN 风险识别
- 风险评分
- 报表展示

---

# 二、为什么选择 ClickHouse？

## 面试回答

> 我们 PCDN 项目选择 ClickHouse，主要是因为业务属于典型的大数据分析场景。
>
> PCDN 系统每天会产生大量 DNS、网络设备以及其他网络流量数据，这类数据具有数据量大、持续写入、查询主要以统计分析和聚合计算为主的特点。
>
> 我们经常需要按照时间、省份、城市、协议、端口等多个维度进行查询，同时需要执行 SUM、COUNT、GROUP BY 等聚合操作。
>
> 因此，我们选择 ClickHouse 作为流量分析数据的主要存储和查询数据库。
>
> ClickHouse 是面向 OLAP 场景的列式数据库，非常适合大规模数据的统计分析和聚合查询。相比 MySQL，它在大范围数据扫描、多维度 GROUP BY 和聚合计算方面更有优势。
>
> 在项目中，我们采用小时级明细表和天级预聚合表结合的方式，通过 MergeTree 和 SummingMergeTree 引擎、时间分区和排序键优化，降低报表查询时的数据扫描量，提高整体查询性能。

---

# 三、为什么 PCDN 场景适合 ClickHouse？

PCDN 流量数据具有以下特点：

```text
数据量大
    ↓
持续产生
    ↓
需要进行多维度查询
    ↓
需要大量聚合计算
    ↓
主要用于统计分析和报表
```

例如系统可能需要查询：

- 最近 24 小时流量趋势
- 最近 7 天流量统计
- 最近 30 天流量统计
- 各省份流量排名
- 各城市流量分布
- 上下行流量比例
- UDP 协议占比
- TOP5 源端口占比
- TOP5 目的端口占比
- 本省用户占比
- PCDN 特征域名统计
- 不同风险等级的数据分布

这些查询通常具有明显的特点：

```text
时间范围查询
+
多维度过滤
+
GROUP BY
+
SUM
+
COUNT
+
AVG
```

这正是 ClickHouse 擅长的场景。

---

# 四、为什么不用 MySQL？

## 1. MySQL 更适合 OLTP 场景

MySQL 更适合：

- 用户信息
- 系统配置
- 评分规则
- 风险等级
- 模型配置
- 订单数据
- 事务型业务

例如 PCDN 系统中的：

```text
流量模型配置
评分规则
风险等级
业务配置
```

这些数据具有以下特点：

```text
数据量较小
更新频繁
需要事务
按主键查询较多
```

因此可以使用 MySQL。

## 2. ClickHouse 更适合 OLAP

PCDN 流量数据的主要特点是：

```text
数据量大
写入持续
查询时间范围长
统计计算多
GROUP BY 较多
报表查询频繁
```

例如：

```sql
SELECT
    province,
    SUM(upload_traffic) AS upload_traffic,
    SUM(download_traffic) AS download_traffic
FROM traffic_hour
WHERE stat_time >= ?
  AND stat_time < ?
GROUP BY province;
```

如果数据量达到每天千万级甚至更高，使用 MySQL 进行大范围扫描和聚合查询，性能压力会比较大。

因此：

> MySQL 主要负责业务数据，ClickHouse 主要负责大规模流量分析数据。

---

# 五、PCDN 数据处理架构

```text
                DNS 数据
                   │
                   ▼
              ┌─────────┐
              │  Kafka  │
              └────┬────┘
                   │
                   ▼
        ┌────────────────────┐
        │   数据消费服务       │
        │                    │
        │  数据清洗           │
        │  数据转换           │
        │  数据关联           │
        │  特征计算           │
        └─────────┬──────────┘
                  │
                  ▼
           ┌───────────────┐
           │  ClickHouse   │
           └───────┬───────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
     小时明细表          天级预聚合表
     MergeTree       SummingMergeTree
          │                 │
          └────────┬────────┘
                   ▼
             PCDN分析服务
                   │
          ┌────────┼────────┐
          ▼        ▼        ▼
       报表查询   风险分析   数据可视化
```

---

# 六、为什么设计小时明细表？

项目中使用：

> **小时级明细表 + 天级预聚合表**

的结构设计。

小时级明细表主要保存：

```text
统计时间
省份
城市
运营商
协议
源端口
目的端口
域名
上行流量
下行流量
```

小时明细表主要用于：

- 查询最近 24 小时数据
- 查询详细流量趋势
- 风险分析
- 特征计算
- 多维度灵活查询

例如：

```sql
SELECT
    stat_hour,
    SUM(upload_traffic) AS upload_traffic,
    SUM(download_traffic) AS download_traffic
FROM traffic_hour
WHERE stat_hour >= ?
  AND stat_hour < ?
GROUP BY stat_hour
ORDER BY stat_hour;
```

---

# 七、为什么设计天级预聚合表？

如果每次报表查询都直接查询小时明细表，会存在性能问题。

例如用户查询：

```text
最近 30 天
全国
所有省份
流量统计
```

如果直接查询明细表：

```text
扫描大量数据
      ↓
过滤
      ↓
GROUP BY
      ↓
SUM
      ↓
返回结果
```

随着数据量增加，查询性能会越来越差。

因此对于一些：

```text
固定
+
高频
+
统计型
```

的查询，我们采用预聚合。

例如提前计算：

```text
日期
省份
城市
运营商
总上行流量
总下行流量
用户数量
风险数据量
```

查询报表时：

```text
原来：

30天明细数据
     ↓
实时聚合


优化后：

30天天级聚合数据
     ↓
直接查询
```

因此可以显著降低查询压力。

---

# 八、预计算优化的核心思想

面试时可以这样回答：

> 对于一些固定的高频统计查询，我们没有每次都实时扫描大量明细数据，而是采用预计算或者预聚合的方式，把一部分计算提前完成。
>
> 这样查询报表时可以直接查询聚合后的结果，减少实时计算和数据扫描。

核心思想：

> **用空间换时间。**

即：

```text
增加部分聚合数据存储
        ↓
减少实时计算
        ↓
降低查询延迟
```

---

# 九、为什么使用 MergeTree？

## 1. MergeTree 用于明细数据

对于 PCDN 小时级流量数据，可以使用：

```text
MergeTree
```

示例：

```sql
CREATE TABLE traffic_hour
(
    stat_time DateTime,
    province String,
    city String,
    protocol String,
    upload_traffic UInt64,
    download_traffic UInt64
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(stat_time)
ORDER BY (
    stat_time,
    province,
    city
);
```

MergeTree 适合：

```text
大规模数据写入
+
时间范围查询
+
多维度分析
+
明细数据存储
```

主要保存：

```text
小时级数据
流量明细
分析数据
```

---

# 十、为什么使用 SummingMergeTree？

对于一些统计型数据，例如：

```text
日期
省份
城市
上行流量
下行流量
用户数量
```

这些数据中的部分指标属于：

```text
SUM
COUNT
```

类型。

因此可以使用：

```text
SummingMergeTree
```

示例：

```sql
CREATE TABLE traffic_day
(
    stat_date Date,
    province String,
    city String,
    upload_traffic UInt64,
    download_traffic UInt64
)
ENGINE = SummingMergeTree
PARTITION BY toYYYYMM(stat_date)
ORDER BY (
    stat_date,
    province,
    city
);
```

假设存在：

```text
2026-09-08 江苏 南京 100
2026-09-08 江苏 南京 200
2026-09-08 江苏 南京 300
```

对于相同维度的数据：

```text
日期
+
省份
+
城市
```

可以进行累加聚合。

最终逻辑上可以得到：

```text
2026-09-08 江苏 南京 600
```

因此适合：

> **可累加指标的预聚合场景。**

---

# 十一、MergeTree 和 SummingMergeTree 如何选择？

| 引擎 | 主要用途 | 数据特点 |
|---|---|---|
| MergeTree | 明细数据 | 保留完整数据 |
| SummingMergeTree | 聚合数据 | 自动处理可累加字段 |
| MergeTree | 小时流量数据 | 支持灵活分析 |
| SummingMergeTree | 天级统计数据 | 降低报表查询压力 |

项目中可以理解为：

```text
MergeTree
    │
    ▼
小时级明细数据
    │
    ▼
灵活分析


SummingMergeTree
    │
    ▼
天级预聚合数据
    │
    ▼
高频报表查询
```

---

# 十二、分区策略如何设计？

PCDN 流量数据属于时间序列数据，因此通常可以根据：

```text
时间
```

进行分区。

例如：

```sql
PARTITION BY toYYYYMM(stat_time)
```

即：

```text
202601
202602
202603
202604
```

按照月份进行分区。

## 为什么按照时间分区？

### 1. 大多数查询带时间条件

例如：

```sql
WHERE stat_time >= ?
AND stat_time < ?
```

用户通常查询：

```text
最近24小时
最近7天
最近30天
某个月的数据
```

按照时间分区后，可以减少无关历史数据的扫描。

例如查询 2026 年 9 月的数据：

```text
不扫描：

2026年1月
2026年2月
2026年3月

只扫描：

2026年9月
```

这就是：

> **分区裁剪。**

### 2. 方便历史数据管理

PCDN 流量数据会持续增长。

例如：

```text
只保留最近6个月明细数据
```

可以通过：

```text
TTL
```

或者分区管理进行数据生命周期处理。

例如：

```sql
TTL stat_time + INTERVAL 180 DAY
```

## 注意：分区不是越细越好

ClickHouse 分区不能设计得过细。

例如：

```text
每天一个分区
甚至每小时一个分区
```

如果产生大量分区和 Part，会增加后台 Merge 压力。

因此：

> 分区粒度需要结合数据量、查询时间范围和数据生命周期综合设计。

---

# 十三、排序键为什么重要？

ClickHouse 中：

```sql
ORDER BY
```

不仅仅是排序。

对于 MergeTree 来说：

> **ORDER BY 决定数据在表中的组织方式，也是查询优化的重要设计。**

例如：

```sql
ORDER BY (
    stat_time,
    province,
    city
)
```

说明数据会按照：

```text
时间
    ↓
省份
    ↓
城市
```

进行组织。

## 高频查询场景

例如业务经常查询：

```sql
WHERE stat_time BETWEEN ? AND ?
AND province = ?
AND city = ?
```

那么：

```sql
ORDER BY (
    stat_time,
    province,
    city
)
```

就比较符合查询路径。

## 排序键设计原则

主要考虑：

### 1. 高频 WHERE 条件

例如：

```text
时间
省份
城市
运营商
```

### 2. 常见查询组合

例如：

```text
时间 + 省份
时间 + 省份 + 城市
```

### 3. 数据过滤能力

排序键的目标之一就是：

> 尽可能减少查询需要扫描的数据范围。

---

# 十四、ClickHouse 查询为什么快？

面试官可能问：

> ClickHouse 为什么查询性能高？

可以回答：

## 1. 列式存储

只读取需要查询的列。

例如：

```sql
SELECT
    province,
    SUM(upload_traffic)
```

可能只需要读取：

```text
province
upload_traffic
```

不需要读取：

```text
IP
端口
域名
其他无关字段
```

减少 IO。

## 2. 分区裁剪

例如：

```sql
WHERE stat_time >= ?
AND stat_time < ?
```

可以减少不相关时间分区的数据扫描。

## 3. 排序键优化

通过：

```sql
ORDER BY
```

合理组织数据，根据查询条件减少扫描范围。

## 4. 适合大规模聚合

ClickHouse 对：

```text
SUM
COUNT
AVG
GROUP BY
```

等分析计算进行了优化。

因此非常适合：

```text
流量统计
数据报表
趋势分析
多维度分析
```

## 5. 预聚合

对于高频查询：

```text
提前计算
```

减少：

```text
实时扫描
+
实时 GROUP BY
+
实时 SUM
```

---

# 十五、为什么不用 Redis？

面试回答：

> Redis 更适合热点数据缓存，但是我们的 PCDN 流量分析查询维度比较多，用户可能按照不同时间、省份、城市、运营商、协议等条件组合查询。
>
> 如果把所有组合都放到 Redis 中，缓存设计会非常复杂，而且数据量也会比较大。
>
> 所以我们的核心分析数据还是使用 ClickHouse，通过预聚合解决高频查询问题。
>
> Redis 更适合缓存重复度非常高的热点查询，例如首页核心指标或者访问频率非常高的固定数据。

---

# 十六、为什么不用 Elasticsearch？

面试回答：

> Elasticsearch 更擅长全文检索、日志搜索以及文本检索。
>
> 而我们的 PCDN 项目主要需求是大规模流量数据的统计和聚合，比如按照时间、省份、城市等维度执行 SUM、COUNT、GROUP BY。
>
> 所以相比 Elasticsearch，ClickHouse 更符合我们的 OLAP 数据分析场景。

简单理解：

```text
Elasticsearch
    ↓
搜索 / 检索


ClickHouse
    ↓
统计 / 聚合 / 数据分析
```

---

# 十七、完整的 PCDN 项目回答

## 推荐面试版本

> 在 PCDN 流量分析模块中，我们主要处理 DNS、网络设备以及 BGP、Radius 等多源数据，通过 Kafka 进行数据消费，然后进行数据清洗、关联和特征计算。
>
> 由于流量数据量比较大，而且业务查询主要是按照时间、省份、城市、协议、端口等维度进行统计和聚合，所以我们选择 ClickHouse 作为主要的流量分析数据库。
>
> ClickHouse 属于列式 OLAP 数据库，非常适合大规模数据扫描和 SUM、COUNT、GROUP BY 等聚合分析场景。
>
> 在数据表设计上，我们采用小时级明细表和天级预聚合表相结合的方式。小时级明细表主要用于详细趋势分析和风险分析，而对于高频报表查询，我们通过预计算生成天级聚合数据。
>
> 存储引擎方面，明细数据主要使用 MergeTree，聚合数据使用 SummingMergeTree，对于可以累加的流量指标提前进行聚合。
>
> 同时，我们结合时间维度设计分区策略，例如按月分区，并根据实际高频查询条件设计 ORDER BY 排序键，比如时间、省份、城市等字段。
>
> 最终通过列式存储、分区裁剪、排序键以及预聚合的方式，减少查询扫描的数据量和实时计算压力，从而提升 PCDN 大规模流量数据的查询性能。

---

# 十八、30 秒精简回答

> 我们选择 ClickHouse，主要是因为 PCDN 流量数据属于典型的 OLAP 场景，数据量大、持续写入，而且查询主要是时间范围过滤和多维度聚合分析，比如按省市统计流量、查询流量趋势、协议占比等。
>
> 所以我们采用 ClickHouse 存储流量分析数据，通过 MergeTree 存小时级明细数据，通过 SummingMergeTree 存天级预聚合数据，再结合时间分区和排序键优化，减少报表查询的数据扫描和实时计算压力，从而提升查询性能。

---

# 十九、一句话总结

> **PCDN 数据量大、查询以统计分析为主，所以选择 ClickHouse；通过小时明细 + 天级预聚合、MergeTree + SummingMergeTree、时间分区和排序键优化，实现大规模流量数据的高效查询和聚合分析。**
