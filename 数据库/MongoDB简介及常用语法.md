# MongoDB 简介及常用语法

> 本文档系统整理 MongoDB 文档数据库的核心概念、常用操作语法、典型使用场景、与 MySQL 的对比分析以及高频面试题，适用于学习复习与面试准备。

---

## 目录

- [一、MongoDB 简介](#一mongodb-简介)
- [二、常用语法](#二常用语法)
- [三、使用场景](#三使用场景)
- [四、MongoDB 与 MySQL 对比](#四mongodb-与-mysql-对比)
- [五、常见面试题](#五常见面试题)
- [六、性能优化建议](#六性能优化建议)

---

## 一、MongoDB 简介

### 1.1 什么是 MongoDB

MongoDB 是一个基于**分布式文件存储**的 **NoSQL 文档数据库**，由 C++ 编写，旨在为 Web 应用提供高性能、高可扩展性的数据存储方案。数据以 **BSON（Binary JSON）** 格式存储，结构灵活，无需预定义 Schema。

### 1.2 核心概念对比

| MongoDB（文档数据库） | MySQL（关系数据库） | 说明 |
|----------------------|--------------------|------|
| Database | Database | 数据库 |
| Collection | Table | 集合/表 |
| Document | Row | 文档/行 |
| Field | Column | 字段/列 |
| Index | Index | 索引 |
| Embedded Document | JOIN（子表） | 内嵌文档/关联表 |
| `_id` | Primary Key | 主键 |

### 1.3 核心特点

| 特点 | 说明 |
|------|------|
| 文档模型 | 数据以 BSON（类 JSON）格式存储，结构灵活 |
| 无固定 Schema | 同一集合中的文档可以有不同字段 |
| 水平扩展 | 原生支持分片（Sharding），易于水平扩展 |
| 高可用 | 内置副本集（Replica Set），自动故障转移 |
| 丰富查询 | 支持 CRUD、聚合管道、全文搜索、地理空间查询 |
| 高性能 | 内存映射引擎，适合高并发读写 |
| 弱事务 | 4.0+ 支持多文档事务，但不如关系数据库成熟 |

### 1.4 数据模型示例

```json
{
    "_id": ObjectId("64a1b2c3d4e5f6a7b8c9d0e1"),
    "username": "zhangsan",
    "age": 25,
    "email": "zs@qq.com",
    "address": {
        "city": "北京",
        "district": "朝阳区"
    },
    "hobbies": ["reading", "coding", "running"],
    "orders": [
        {
            "orderNo": "ORD001",
            "amount": 99.00,
            "createTime": ISODate("2026-01-15T10:30:00Z")
        }
    ],
    "createTime": ISODate("2026-01-01T00:00:00Z"),
    "status": 1
}
```

### 1.5 架构组成

```
┌──────────────────────────────────────────┐
│              mongos（路由）                │  客户端连接入口
├──────────────────────────────────────────┤
│              Config Server                │  存储分片配置信息
├──────────────────────────────────────────┤
│   Shard 1          Shard 2          ...  │  数据分片存储
│  (Replica Set)   (Replica Set)           │  每个分片是副本集
│  ┌────┐ ┌────┐   ┌────┐ ┌────┐          │
│  │ P  │ │ S1 │   │ P  │ │ S1 │          │  P=主节点 S=从节点
│  └────┘ └────┘   └────┘ └────┘          │
└──────────────────────────────────────────┘
```

---

## 二、常用语法

### 2.1 数据库操作

```javascript
// 查看所有数据库
show dbs

// 切换/创建数据库（插入数据后才会真正创建）
use mydb

// 查看当前数据库
db

// 查看当前数据库下的集合
show collections

// 删除当前数据库
db.dropDatabase()

// 查看数据库状态
db.stats()
```

### 2.2 集合操作

```javascript
// 创建集合
db.createCollection("user", {
    validator: {
        $jsonSchema: {
            required: ["username", "email"],
            properties: {
                username: { bsonType: "string" },
                email: { bsonType: "string" },
                age: { bsonType: "int", minimum: 0 }
            }
        }
    }
})

// 查看所有集合
show collections

// 删除集合
db.user.drop()

// 重命名集合
db.user.renameCollection("t_user")
```

### 2.3 插入数据

```javascript
// 插入单条文档
db.user.insertOne({
    username: "zhangsan",
    email: "zs@qq.com",
    age: 25,
    address: { city: "北京", district: "朝阳区" },
    hobbies: ["reading", "coding"],
    createTime: new Date()
})

// 插入多条文档
db.user.insertMany([
    {
        username: "lisi",
        email: "ls@qq.com",
        age: 30,
        address: { city: "上海", district: "浦东新区" },
        hobbies: ["music", "travel"],
        createTime: new Date()
    },
    {
        username: "wangwu",
        email: "ww@qq.com",
        age: 28,
        address: { city: "广州", district: "天河区" },
        hobbies: ["gaming", "cooking"],
        createTime: new Date()
    }
])
```

### 2.4 查询数据

#### 2.4.1 基础查询

```javascript
// 查询所有
db.user.find()

// 格式化输出
db.user.find().pretty()

// 查询第一条
db.user.findOne()

// 条件查询
db.user.find({ username: "zhangsan" })

// 指定返回字段（投影）
db.user.find({}, { username: 1, email: 1, _id: 0 })
// 1 表示返回，0 表示排除
```

#### 2.4.2 条件查询

```javascript
// 比较运算符：$eq, $gt, $gte, $lt, $lte, $ne
db.user.find({ age: { $gt: 25 } })                    // age > 25
db.user.find({ age: { $gte: 20, $lte: 30 } })         // 20 <= age <= 30
db.user.find({ age: { $ne: 25 } })                     // age != 25

// AND 条件（多个条件并列）
db.user.find({ age: { $gt: 25 }, status: 1 })

// OR 条件：$or
db.user.find({
    $or: [
        { age: { $lt: 20 } },
        { age: { $gt: 60 } }
    ]
})

// IN 查询：$in
db.user.find({ age: { $in: [25, 30, 35] } })

// NOT IN：$nin
db.user.find({ age: { $nin: [25, 30] } })

// 嵌套文档查询
db.user.find({ "address.city": "北京" })

// 数组包含某元素
db.user.find({ hobbies: "coding" })

// 数组包含所有元素：$all
db.user.find({ hobbies: { $all: ["coding", "reading"] } })

// 数组大小：$size
db.user.find({ hobbies: { $size: 2 } })

// 正则匹配
db.user.find({ username: { $regex: /^zhang/ } })

// NULL 判断
db.user.find({ phone: null })

// EXISTS 判断字段是否存在
db.user.find({ phone: { $exists: true } })
db.user.find({ phone: { $exists: false } })

// 类型判断：$type
db.user.find({ age: { $type: "int" } })
```

#### 2.4.3 排序、分页、计数

```javascript
// 排序：1 升序，-1 降序
db.user.find().sort({ age: -1, createTime: 1 })

// 跳过 & 限制（分页：第 2 页，每页 10 条）
db.user.find().skip(10).limit(10)

// 计数
db.user.find({ status: 1 }).count()

// 去重
db.user.distinct("age")
db.user.distinct("age", { status: 1 })
```

#### 2.4.4 聚合管道

聚合管道是 MongoDB 最强大的数据处理工具，类似 SQL 中的 GROUP BY + 聚合函数。

```javascript
// 聚合管道语法
db.collection.aggregate([
    { $stage1: { ... } },
    { $stage2: { ... } },
    ...
])
```

**常用管道阶段**：

| 阶段 | 说明 | 类比 SQL |
|------|------|---------|
| `$match` | 过滤文档 | WHERE |
| `$group` | 分组 | GROUP BY |
| `$sort` | 排序 | ORDER BY |
| `$limit` | 限制数量 | LIMIT |
| `$skip` | 跳过数量 | OFFSET |
| `$project` | 字段投影 | SELECT |
| `$unwind` | 展开数组 | - |
| `$lookup` | 关联查询 | LEFT JOIN |
| `$addFields` | 添加字段 | - |
| `$count` | 计数 | COUNT |

**聚合示例**：

```javascript
// 1. 分组统计：每个城市的用户数量和平均年龄
db.user.aggregate([
    { $match: { status: 1 } },
    {
        $group: {
            _id: "$address.city",
            count: { $sum: 1 },
            avgAge: { $avg: "$age" },
            maxAge: { $max: "$age" },
            minAge: { $min: "$age" }
        }
    },
    { $sort: { count: -1 } },
    { $limit: 10 }
])

// 2. 展开数组 + 分组统计：统计每个爱好的用户数量
db.user.aggregate([
    { $unwind: "$hobbies" },
    {
        $group: {
            _id: "$hobbies",
            count: { $sum: 1 }
        }
    },
    { $sort: { count: -1 } }
])

// 3. 关联查询（$lookup 类似 LEFT JOIN）
db.order.aggregate([
    {
        $lookup: {
            from: "user",           // 关联的集合
            localField: "userId",   // 当前集合的字段
            foreignField: "_id",    // 被关联集合的字段
            as: "userInfo"          // 输出数组字段名
        }
    },
    { $unwind: "$userInfo" },       // 展开关联结果
    {
        $project: {
            orderNo: 1,
            amount: 1,
            username: "$userInfo.username"
        }
    }
])

// 4. 分组取 TopN：每个城市年龄最大的前 3 名
db.user.aggregate([
    { $sort: { age: -1 } },
    {
        $group: {
            _id: "$address.city",
            topUsers: { $push: "$$ROOT" }
        }
    },
    {
        $project: {
            _id: 1,
            topUsers: { $slice: ["$topUsers", 3] }
        }
    }
])

// 5. 多阶段管道：按月统计订单金额
db.order.aggregate([
    { $match: { createTime: { $gte: ISODate("2026-01-01") } } },
    {
        $group: {
            _id: {
                year: { $year: "$createTime" },
                month: { $month: "$createTime" }
            },
            totalAmount: { $sum: "$amount" },
            orderCount: { $sum: 1 },
            avgAmount: { $avg: "$amount" }
        }
    },
    { $sort: { "_id.year": 1, "_id.month": 1 } }
])
```

**常用聚合表达式**：

| 表达式 | 说明 |
|--------|------|
| `$sum` | 求和 |
| `$avg` | 平均值 |
| `$min` / `$max` | 最小/最大值 |
| `$first` / `$last` | 第一个/最后一个 |
| `$push` | 将值加入数组 |
| `$addToSet` | 将值加入数组（去重） |

### 2.5 更新数据

```javascript
// 更新单条
db.user.updateOne(
    { username: "zhangsan" },
    { $set: { age: 26, email: "zs_new@qq.com" } }
)

// 更新多条
db.user.updateMany(
    { status: 0 },
    { $set: { status: 1 } }
)

// upsert：存在则更新，不存在则插入
db.user.updateOne(
    { username: "newuser" },
    { $set: { age: 25, email: "new@qq.com" } },
    { upsert: true }
)

// 替换整个文档（注意：会丢失未指定的字段）
db.user.replaceOne(
    { username: "zhangsan" },
    { username: "zhangsan", age: 27, email: "zs@qq.com" }
)
```

**常用更新操作符**：

| 操作符 | 说明 | 示例 |
|--------|------|------|
| `$set` | 设置字段值 | `{ $set: { age: 26 } }` |
| `$unset` | 删除字段 | `{ $unset: { phone: "" } }` |
| `$inc` | 数值自增 | `{ $inc: { age: 1 } }` |
| `$push` | 向数组追加元素 | `{ $push: { hobbies: "swimming" } }` |
| `$pull` | 从数组中移除元素 | `{ $pull: { hobbies: "gaming" } }` |
| `$addToSet` | 向数组添加（去重） | `{ $addToSet: { hobbies: "reading" } }` |
| `$rename` | 重命名字段 | `{ $rename: { phone: "mobile" } }` |
| `$min` / `$max` | 取最小/最大值 | `{ $max: { score: 100 } }` |

### 2.6 删除数据

```javascript
// 删除单条
db.user.deleteOne({ username: "zhangsan" })

// 删除多条
db.user.deleteMany({ status: 0 })

// 删除集合所有文档
db.user.deleteMany({})

// 删除集合（包括索引）
db.user.drop()
```

### 2.7 索引操作

```javascript
// 创建普通索引
db.user.createIndex({ username: 1 })    // 1 升序，-1 降序

// 创建唯一索引
db.user.createIndex({ email: 1 }, { unique: true })

// 创建复合索引
db.user.createIndex({ status: 1, age: -1 })

// 创建 TTL 索引（文档过期自动删除）
db.session.createIndex(
    { expireAt: 1 },
    { expireAfterSeconds: 3600 }    // 1 小时后过期
)

// 创建文本索引（全文搜索）
db.article.createIndex({ title: "text", content: "text" })

// 查看集合所有索引
db.user.getIndexes()

// 删除索引
db.user.dropIndex("username_1")

// 查看索引使用情况
db.user.aggregate([
    { $indexStats: {} }
])
```

**全文搜索**：

```javascript
// 使用文本索引搜索
db.article.find({ $text: { $search: "MongoDB 教程" } })

// 搜索并排序相关性
db.article.find(
    { $text: { $search: "MongoDB 教程" } },
    { score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } })
```

### 2.8 事务操作（MongoDB 4.0+）

```javascript
// 开启会话
const session = db.getMongo().startSession()

// 开启事务
session.startTransaction()

try {
    // 事务内操作
    session.getDatabase("mydb").account.updateOne(
        { _id: 1 },
        { $inc: { balance: -500 } }
    )
    session.getDatabase("mydb").account.updateOne(
        { _id: 2 },
        { $inc: { balance: 500 } }
    )

    // 提交事务
    session.commitTransaction()
} catch (error) {
    // 回滚事务
    session.abortTransaction()
} finally {
    session.endSession()
}
```

> **注意**：多文档事务仅在副本集（4.0+）和分片集群（4.2+）中支持，且必须在已存在的集合上操作。

### 2.9 常用管理命令

```javascript
// 查看集合文档数量
db.user.countDocuments()

// 查看集合存储信息
db.user.stats()

// 查看集合数据大小
db.user.dataSize()

// 查看集合索引大小
db.user.totalIndexSize()

// 验证集合
db.user.validate()

// 导出为 JSON
// mongoexport --db=mydb --collection=user --out=user.json

// 导入 JSON
// mongoimport --db=mydb --collection=user --file=user.json
```

---

## 三、使用场景

### 3.1 适合使用 MongoDB 的场景

#### 场景 1：灵活的 Schema（字段不固定）

```javascript
// 用户画像数据，不同用户属性差异大
{
    _id: ObjectId("..."),
    userId: 1001,
    baseInfo: { name: "张三", age: 25 },
    tags: ["高消费", "活跃用户"],
    preferences: {
        theme: "dark",
        language: "zh-CN"
    },
    // 部分用户有额外字段
    vipLevel: 3,
    inviteCode: "ABC123"
}
```

**适用**：用户画像、商品属性、配置信息。

#### 场景 2：嵌套数据结构

```javascript
// 订单数据，包含多个订单项
{
    _id: ObjectId("..."),
    orderNo: "ORD202601150001",
    userId: 1001,
    items: [
        { productId: "P001", name: "手机", price: 2999, qty: 1 },
        { productId: "P002", name: "耳机", price: 199, qty: 2 }
    ],
    address: {
        province: "北京",
        city: "北京",
        detail: "朝阳区xxx路xxx号"
    },
    totalAmount: 3397,
    status: "paid",
    createTime: ISODate("2026-01-15T10:30:00Z")
}
```

**适用**：订单、评论（含回复）、文章（含标签/附件）。

#### 场景 3：高并发读写

- 日志系统：应用日志、操作日志、审计日志
- 实时数据：聊天消息、实时通知
- 缓存替代：替代部分 Redis 缓存场景

#### 场景 4：地理位置查询

```javascript
// 存储位置信息
db.restaurant.insertOne({
    name: "海底捞",
    location: {
        type: "Point",
        coordinates: [116.46, 39.92]  // [经度, 纬度]
    }
})

// 创建 2dsphere 索引
db.restaurant.createIndex({ location: "2dsphere" })

// 查询附近 5km 内的餐厅
db.restaurant.find({
    location: {
        $near: {
            $geometry: { type: "Point", coordinates: [116.46, 39.92] },
            $maxDistance: 5000
        }
    }
})
```

**适用**：外卖、打车、LBS 应用。

#### 场景 5：大数据量水平扩展

- 社交动态 Feed 流
- 物联网（IoT）设备数据
- 内容管理系统（CMS）

### 3.2 不适合使用 MongoDB 的场景

| 场景 | 原因 | 推荐方案 |
|------|------|---------|
| 复杂事务 | 事务支持不如关系数据库成熟 | MySQL/PostgreSQL |
| 复杂关联查询 | JOIN 操作性能差 | MySQL/PostgreSQL |
| 强一致性要求 | 默认最终一致性 | MySQL/PostgreSQL |
| 固定 Schema | 灵活 Schema 优势无法发挥 | MySQL |
| 报表分析 | 聚合性能不如专业 OLAP | ClickHouse/Elasticsearch |

---

## 四、MongoDB 与 MySQL 对比

### 4.1 核心对比

| 对比项 | MongoDB | MySQL |
|--------|---------|-------|
| **数据模型** | 文档模型（BSON/JSON） | 关系模型（表/行/列） |
| **Schema** | 灵活，无需预定义 | 严格，需预定义表结构 |
| **查询语言** | MQL（MongoDB Query Language） | SQL |
| **事务支持** | 4.0+ 支持多文档事务 | 完善的事务支持 |
| **JOIN 操作** | `$lookup`（性能较差） | 原生 JOIN（性能优秀） |
| **索引** | B 树、哈希、文本、地理空间 | B+ 树、全文、哈希 |
| **扩展方式** | 水平扩展（分片） | 垂直扩展为主，分库分表复杂 |
| **一致性** | 最终一致性（可配置） | 强一致性（ACID） |
| **存储引擎** | WiredTiger | InnoDB / MyISAM |
| **内存使用** | 大量使用内存做缓存 | 缓冲池缓存数据页 |
| **部署复杂度** | 较简单 | 较简单 |
| **运维复杂度** | 中等 | 中等 |
| **社区生态** | 活跃，NoSQL 生态 | 非常活跃，成熟生态 |
| **适用场景** | 灵活 Schema、高并发、大数据 | 复杂查询、事务、强一致性 |

### 4.2 MongoDB 优势

#### 优势 1：灵活的文档模型

```javascript
// 同一集合可以存储不同结构的文档
// 文档 1
{ name: "张三", age: 25, email: "zs@qq.com" }

// 文档 2（多了 vipLevel 字段，少了 email）
{ name: "李四", age: 30, vipLevel: 3 }

// 文档 3（嵌套结构）
{ name: "王五", age: 28, address: { city: "上海" }, hobbies: ["reading"] }
```

**MySQL 对比**：需要预定义所有列，NULL 字段浪费空间。

#### 优势 2：水平扩展更容易

- MongoDB 原生支持**分片**，自动将数据分散到多个节点；
- MySQL 分库分表需要中间件（ShardingSphere/MyCat），运维复杂。

#### 优势 3：嵌套数据避免 JOIN

```javascript
// MongoDB：订单和订单项存在一起，一次查询获取全部
{
    orderNo: "ORD001",
    items: [
        { product: "手机", price: 2999 },
        { product: "耳机", price: 199 }
    ]
}

// MySQL：需要 JOIN 两张表
SELECT o.order_no, p.product_name, p.price
FROM `order` o
JOIN `order_item` oi ON o.id = oi.order_id
JOIN `product` p ON oi.product_id = p.id
WHERE o.order_no = 'ORD001';
```

**性能优势**：避免多次 JOIN，读取性能更高。

#### 优势 4：写入性能更高

- MongoDB 默认**写关注（Write Concern）** 较低，写入速度快；
- 无需维护复杂的索引和约束；
- 适合日志、事件等高频写入场景。

#### 优势 5：内置数据类型丰富

- 原生支持数组、嵌套文档、地理空间、正则等；
- MySQL 需要额外表或 JSON 字段来实现类似功能。

### 4.3 MongoDB 劣势

#### 劣势 1：事务支持较弱

- MongoDB 4.0+ 才支持多文档事务；
- 事务性能不如 MySQL；
- 不支持 DDL 事务。

#### 劣势 2：JOIN 性能差

- `$lookup` 本质是嵌套循环，大数据量下性能差；
- 不支持外键约束；
- 复杂关联查询需要应用层处理。

#### 劣势 3：无标准查询语言

- 没有类似 SQL 的标准查询语言；
- 学习成本较高，调试不如 SQL 直观；
- SQL 开发人员迁移成本高。

#### 劣势 4：内存消耗大

- WiredTiger 引擎默认使用 50% 内存做缓存；
- 大数据量下内存需求高；
- 不如 MySQL 可控。

#### 劣势 5：数据冗余

- 为避免 JOIN，通常采用嵌套/冗余存储；
- 数据一致性维护成本高；
- 存储空间浪费。

#### 劣势 6：不支持复杂报表

- 聚合管道功能有限，不如 SQL 灵活；
- 复杂统计报表性能差；
- 通常需要配合 Elasticsearch/ClickHouse。

### 4.4 选型建议

| 需求 | 推荐方案 |
|------|---------|
| 电商订单系统 | MySQL（事务 + 复杂查询） |
| 用户画像/商品属性 | MongoDB（灵活 Schema） |
| 日志/事件存储 | MongoDB（高写入性能） |
| 支付/金融系统 | MySQL（强一致性） |
| 社交 Feed 流 | MongoDB（水平扩展） |
| 地理位置应用 | MongoDB（地理空间索引） |
| 复杂报表分析 | MySQL + ClickHouse |
| 物联网数据 | MongoDB（大数据量 + 灵活 Schema） |
| 内容管理系统 | MongoDB（文档嵌套） |
| 传统企业应用 | MySQL（成熟生态） |

> **最佳实践**：很多项目采用 **MySQL + MongoDB 混合架构**，核心业务数据用 MySQL，灵活数据/日志/缓存用 MongoDB。

---

## 五、常见面试题

### 5.1 基础概念类

#### Q1：MongoDB 的数据存储结构是什么样的？

MongoDB 使用 **BSON（Binary JSON）** 格式存储数据，结构如下：

- **Database**（数据库）→ **Collection**（集合）→ **Document**（文档）
- 文档以键值对形式存储，类似 JSON 但支持更多数据类型（Date、ObjectId、Binary 等）
- 每个文档自动创建 `_id` 字段作为主键

#### Q2：ObjectId 的组成是什么？

ObjectId 是 12 字节（24 位十六进制）的唯一标识符：

```
|---- 4 字节 ----|-- 5 字节 --|-- 3 字节 --|
   时间戳(秒)     随机值       计数器
```

- **时间戳**：文档创建时间（精确到秒）
- **随机值**：每台机器唯一
- **计数器**：同一秒内递增

**优势**：
1. 包含时间信息，可按时间排序；
2. 分布式生成，无需中心节点；
3. 比自增 ID 更适合分布式环境。

#### Q3：MongoDB 的存储引擎有哪些？

| 引擎 | 说明 |
|------|------|
| **WiredTiger** | 默认引擎（3.2+），支持文档级并发控制、压缩 |
| **In-Memory** | 内存引擎，数据不持久化，适合缓存场景 |
| **MMAPv1** | 旧引擎（3.0 之前），已废弃 |

**WiredTiger 特点**：
- 文档级并发控制（类似行级锁）
- 支持 snappy/zlib 压缩
- 使用前缀压缩优化索引

### 5.2 索引类

#### Q4：MongoDB 索引底层使用什么数据结构？

MongoDB 索引底层使用 **B-Tree（B 树）**，与 MySQL 的 B+ 树略有不同：

| 对比 | MongoDB（B 树） | MySQL（B+ 树） |
|------|-----------------|---------------|
| 数据存储 | 所有节点都存数据 | 只有叶子节点存数据 |
| 范围查询 | 需要中序遍历 | 叶子节点链表连接，效率高 |
| 查询稳定性 | 不稳定（可能在非叶子节点命中） | 稳定（必须到叶子节点） |

**MongoDB 索引类型**：
- **单字段索引**：`{ field: 1 }`
- **复合索引**：`{ field1: 1, field2: -1 }`
- **多键索引**（数组字段）：自动为数组每个元素创建索引
- **文本索引**：`{ field: "text" }`
- **地理空间索引**：`{ field: "2dsphere" }`
- **哈希索引**：`{ field: "hashed" }`
- **TTL 索引**：自动过期删除

#### Q5：MongoDB 索引失效的场景有哪些？

```javascript
// 1. 对索引字段使用正则
db.user.find({ name: { $regex: /^zhang/ } })  // 以 ^ 开头可利用索引，否则失效

// 2. 类型不匹配
// 索引字段是 string，查询用 number
db.user.find({ age: "25" })  // age 索引是 int，类型不匹配失效

// 3. $or 中有非索引字段
db.user.find({ $or: [{ age: 25 }, { address: "北京" }] })  // address 无索引

// 4. 不符合最左前缀原则（复合索引）
// 索引 { status: 1, age: 1 }
db.user.find({ age: 25 })  // 缺少最左字段 status

// 5. 使用 $ne / $not
db.user.find({ status: { $ne: 1 } })  // 可能全表扫描
```

### 5.3 副本集与分片

#### Q6：MongoDB 副本集的工作原理？

**副本集（Replica Set）** 是 MongoDB 实现高可用的机制：

```
┌─────────┐     数据同步     ┌─────────┐
│ Primary │ ──────────────► │ Secondary│
│ (主节点) │                 │ (从节点) │
└─────────┘                 └─────────┘
     │                            │
     │  写入请求                   │ 读取请求（可选）
     ▼                            ▼
  处理写操作                  处理读操作
```

**工作原理**：
1. **写入流程**：客户端写请求发到 Primary → Primary 写入 Oplog → Secondary 拉取 Oplog 并重放
2. **选举机制**：Primary 宕机时，Secondary 通过选举产生新的 Primary
3. **读写分离**：默认读写都在 Primary，可配置 Secondary 读

**Oplog（操作日志）**：
- 记录所有数据修改操作
- 类似 MySQL 的 binlog
- 存储在 `local.oplog.rs` 集合中

#### Q7：MongoDB 分片（Sharding）的原理？

**分片**是将数据分散到多个 MongoDB 实例中，实现水平扩展。

**组件**：
- **mongos**：路由进程，客户端连接入口，负责请求路由和结果合并
- **Config Server**：存储集群元数据（分片规则、chunk 分布）
- **Shard**：存储实际数据，每个 Shard 是一个副本集

**分片策略**：
- **Hash 分片**：按字段哈希值分片，数据分布均匀
- **Range 分片**：按字段值范围分片，范围查询效率高
- **基于 Zone 的分片**：按地理位置或业务规则分片

```javascript
// 启用分片
sh.enableSharding("mydb")

// 对集合进行分片（使用 userId 的哈希）
sh.shardCollection("mydb.user", { userId: "hashed" })
```

#### Q8：MongoDB 的写关注（Write Concern）有哪些级别？

| 级别 | 说明 | 安全性 | 性能 |
|------|------|--------|------|
| `{ w: 0 }` | 不等待确认 | 最低 | 最高 |
| `{ w: 1 }` | Primary 写入确认（默认） | 低 | 高 |
| `{ w: "majority" }` | 多数节点写入确认 | 高 | 中 |
| `{ w: "all" }` | 所有节点写入确认 | 最高 | 最低 |

**搭配 `j: true`**：确保写入 Journal 日志，防止崩溃丢失。

```javascript
// 高安全性写入
db.user.insertOne(
    { name: "张三" },
    { writeConcern: { w: "majority", j: true } }
)
```

#### Q9：MongoDB 的读关注（Read Concern）有哪些级别？

| 级别 | 说明 | 类比 MySQL |
|------|------|-----------|
| `local` | 返回最新数据，不保证已复制（默认） | READ UNCOMMITTED |
| `available` | 返回最新可用数据 | - |
| `majority` | 返回多数节点已确认的数据 | READ COMMITTED |
| `linearizable` | 保证读取到最新已提交数据 | SERIALIZABLE |
| `snapshot` | 返回事务开始时的快照 | REPEATABLE READ |

### 5.4 与 MySQL 对比类

#### Q10：MongoDB 和 MySQL 如何选择？

**选 MySQL**：
1. 需要复杂 JOIN 查询
2. 需要强事务保证（金融、支付）
3. 数据结构固定，关系明确
4. 团队 SQL 经验丰富

**选 MongoDB**：
1. Schema 灵活，字段不固定
2. 高并发读写（日志、事件）
3. 数据量大，需要水平扩展
4. 嵌套/文档型数据结构
5. 地理空间查询

**混合使用**：核心业务数据用 MySQL，灵活数据/日志/缓存用 MongoDB。

#### Q11：MongoDB 的文档模型相比 MySQL 的关系模型有什么优缺点？

**优点**：
1. **读取性能好**：相关数据存在一起，避免 JOIN；
2. **Schema 灵活**：同一集合可以存储不同结构的文档；
3. **水平扩展容易**：原生支持分片；
4. **开发效率高**：文档模型与编程语言对象模型匹配。

**缺点**：
1. **数据冗余**：为避免 JOIN，需要冗余存储；
2. **更新成本高**：修改冗余数据需要更新多处；
3. **一致性维护难**：冗余数据可能不一致；
4. **复杂查询弱**：JOIN 性能差。

#### Q12：MongoDB 如何处理关联查询？

```javascript
// 方式 1：$lookup（类似 LEFT JOIN）
db.order.aggregate([
    {
        $lookup: {
            from: "user",
            localField: "userId",
            foreignField: "_id",
            as: "userInfo"
        }
    }
])

// 方式 2：手动关联（应用层处理）
const order = db.order.findOne({ _id: orderId })
const user = db.user.findOne({ _id: order.userId })

// 方式 3：冗余存储（推荐）
// 将用户信息直接嵌入订单文档
{
    orderNo: "ORD001",
    userId: 1001,
    userName: "张三",  // 冗余
    items: [...]
}
```

### 5.5 性能优化类

#### Q13：MongoDB 如何优化查询性能？

1. **创建合适的索引**：
   - 为常用查询字段创建索引
   - 复合索引遵循最左前缀原则
   - 使用覆盖索引（Covered Query）

2. **避免全表扫描**：
   ```javascript
   // 使用 explain 分析
   db.user.find({ age: { $gt: 25 } }).explain("executionStats")
   ```

3. **限制返回字段**：
   ```javascript
   // 只返回需要的字段
   db.user.find({}, { username: 1, email: 1, _id: 0 })
   ```

4. **使用分页**：
   ```javascript
   db.user.find().skip(100).limit(10)
   ```

5. **避免大数组**：
   - 数组过大会影响性能
   - 考虑拆分子文档

6. **使用聚合管道优化**：
   - `$match` 放在管道最前面
   - 尽早过滤数据

#### Q14：MongoDB 的内存使用机制是什么？

**WiredTiger 引擎内存管理**：
- **默认使用 50% 物理内存**（减去 1GB）做缓存
- 缓存包括：数据页、索引页
- 内存不足时，按 LRU 算法淘汰

**调优参数**：
```javascript
// 配置 WiredTiger 缓存大小
storage:
  wiredTiger:
    engineConfig:
      cacheSizeGB: 4  // 设置缓存大小
```

**监控内存**：
```javascript
db.stats()  // 查看数据库统计
db.serverStatus().mem  // 查看服务器内存使用
```

#### Q15：MongoDB 如何保证数据一致性？

**副本集一致性**：
1. **Write Concern**：控制写入确认级别
2. **Read Concern**：控制读取一致性级别
3. **因果一致性**（3.6+）：保证因果关系的操作顺序

**事务一致性**：
- 4.0+ 支持多文档事务
- 事务内操作要么全部成功，要么全部回滚

**最终一致性**：
- 默认情况下，MongoDB 是最终一致性
- 通过调整 Write/Read Concern 可以提高一致性级别

### 5.6 实战场景类

#### Q16：如何用 MongoDB 实现计数器？

```javascript
// 方式 1：$inc 原子操作
db.counter.updateOne(
    { _id: "order_seq" },
    { $inc: { seq: 1 } },
    { upsert: true }
)

// 方式 2：findOneAndUpdate（返回更新后的值）
const result = db.counter.findOneAndUpdate(
    { _id: "order_seq" },
    { $inc: { seq: 1 } },
    { returnDocument: "after", upsert: true }
)
print(result.seq)  // 返回新的序列号
```

#### Q17：MongoDB 如何处理过期数据？

**方式 1：TTL 索引**
```javascript
// 创建 TTL 索引，文档在 expireAt 字段时间后 3600 秒过期
db.session.createIndex(
    { expireAt: 1 },
    { expireAfterSeconds: 3600 }
)

// 插入文档
db.session.insertOne({
    userId: 1001,
    expireAt: new Date()  // 1 小时后过期
})
```

**方式 2：定时任务清理**
```javascript
// 定时删除过期数据
db.logs.deleteMany({
    createTime: { $lt: ISODate("2026-01-01") }
})
```

#### Q18：MongoDB 如何实现全文搜索？

```javascript
// 1. 创建文本索引
db.article.createIndex({
    title: "text",
    content: "text"
})

// 2. 全文搜索
db.article.find({
    $text: { $search: "MongoDB 教程" }
})

// 3. 排除关键词
db.article.find({
    $text: { $search: "MongoDB -MySQL" }
})

// 4. 精确匹配短语
db.article.find({
    $text: { $search: "\"MongoDB 教程\"" }
})

// 5. 按相关性排序
db.article.find(
    { $text: { $search: "MongoDB" } },
    { score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } })
```

> **注意**：MongoDB 全文搜索功能有限，复杂搜索建议使用 Elasticsearch。

#### Q19：MongoDB 的聚合管道和 MapReduce 有什么区别？

| 对比项 | 聚合管道 | MapReduce |
|--------|---------|-----------|
| **性能** | 更快 | 较慢 |
| **易用性** | 声明式，易理解 | 需要编写 JS 函数 |
| **功能** | 丰富（$lookup, $unwind 等） | 灵活但复杂 |
| **推荐度** | 推荐使用 | 已不推荐（官方建议用聚合管道） |

**聚合管道示例**：
```javascript
db.order.aggregate([
    { $match: { status: "paid" } },
    { $group: { _id: "$userId", total: { $sum: "$amount" } } },
    { $sort: { total: -1 } },
    { $limit: 10 }
])
```

#### Q20：MongoDB 的备份与恢复怎么做？

**备份**：
```bash
# 备份整个数据库
mongodump --db=mydb --out=/backup/

# 备份指定集合
mongodump --db=mydb --collection=user --out=/backup/

# 压缩备份
mongodump --db=mydb --gzip --out=/backup/
```

**恢复**：
```bash
# 恢复整个数据库
mongorestore --db=mydb /backup/mydb/

# 恢复指定集合
mongorestore --db=mydb --collection=user /backup/mydb/user.bson
```

**导出/导入 JSON**：
```bash
# 导出为 JSON
mongoexport --db=mydb --collection=user --out=user.json

# 导入 JSON
mongoimport --db=mydb --collection=user --file=user.json
```

---

## 六、性能优化建议

### 6.1 索引优化

1. **为常用查询字段创建索引**；
2. **复合索引遵循最左前缀原则**；
3. **使用覆盖索引**（Covered Query），避免回表；
4. **避免过多索引**，影响写入性能；
5. **定期分析索引使用情况**。

### 6.2 查询优化

1. **使用 `projection` 限制返回字段**；
2. **使用 `limit` 限制返回数量**；
3. **避免大数组操作**；
4. **聚合管道中 `$match` 放在最前面**；
5. **使用 `explain` 分析查询性能**。

### 6.3 写入优化

1. **批量写入**：使用 `insertMany` 替代多次 `insertOne`；
2. **调整 Write Concern**：非关键数据可降低写入确认级别；
3. **关闭不必要的索引**：大批量导入时先删除索引，导入后重建。

### 6.4 架构优化

1. **读写分离**：读操作分散到 Secondary；
2. **分片**：大数据量使用分片水平扩展；
3. **合理选择数据类型**：使用合适的数据类型减少存储空间；
4. **预分配空间**：避免频繁分配磁盘空间。

### 6.5 监控与调优

```javascript
// 查看服务器状态
db.serverStatus()

// 查看慢查询
db.currentOp()

// 查看集合统计
db.user.stats()

// 查看索引使用
db.user.aggregate([{ $indexStats: {} }])
```

---

## 附录：MongoDB 版本特性对比

| 版本 | 重要特性 |
|------|---------|
| 3.2 | WiredTiger 成为默认引擎，文档级锁 |
| 3.6 | 因果一致性，变更流（Change Streams） |
| 4.0 | 多文档事务（副本集） |
| 4.2 | 多文档事务（分片集群），分布式事务 |
| 4.4 | 增强索引，改进的副本集协议 |
| 5.0 | 时序集合（Time Series Collections），可恢复索引构建 |
| 6.0 | 集群到集群同步，改进的查询优化 |
| 7.0 | 改进的分片操作，性能优化 |

---

> **文档说明**：本文档基于 MongoDB 6.0+ 整理，部分语法在低版本可能不支持。面试题答案参考官方文档及社区实践，建议结合实际场景理解。
