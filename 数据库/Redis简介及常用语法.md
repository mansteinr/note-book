# Redis 简介及常用语法

## 目录
- [一、Redis 简介](#一redis-简介)
- [二、Redis 数据类型](#二redis-数据类型)
- [三、常用命令语法](#三常用命令语法)
- [四、使用场景](#四使用场景)
- [五、性能优化](#五性能优化)
- [六、持久化机制](#六持久化机制)
- [七、高可用架构](#七高可用架构)
- [八、常见面试题](#八常见面试题)

---

## 一、Redis 简介

### 1.1 什么是 Redis

Redis（Remote Dictionary Server）是一个开源的、基于内存的数据结构存储系统，可用作数据库、缓存和消息中间件。

### 1.2 核心特点

- **高性能**：基于内存操作，读写性能极高（读 110000 次/s，写 81000 次/s）
- **丰富的数据结构**：支持 String、Hash、List、Set、Sorted Set 等
- **持久化**：支持 RDB 和 AOF 两种持久化方式
- **原子性**：所有操作都是原子的
- **丰富的功能**：支持发布/订阅、事务、Lua 脚本、管道等
- **高可用**：支持主从复制、哨兵模式、集群模式

### 1.3 Redis vs Memcached

| 特性 | Redis | Memcached |
|------|-------|-----------|
| 数据结构 | 丰富（String、Hash、List、Set、ZSet 等） | 仅支持简单的 Key-Value |
| 持久化 | 支持 RDB 和 AOF | 不支持 |
| 集群 | 原生支持 Cluster | 客户端分片 |
| 线程模型 | 单线程（6.0 后引入多线程） | 多线程 |
| 内存管理 | 多种淘汰策略 | LRU |
| 事务 | 支持（WATCH/MULTI/EXEC） | 不支持 |
| 发布订阅 | 支持 | 不支持 |

---

## 二、Redis 数据类型

### 2.1 String（字符串）

最基本的类型，可以存储字符串、整数或浮点数。

```bash
# 设置值
SET key value
SET name "张三"

# 获取值
GET key
GET name

# 设置值并设置过期时间（秒）
SETEX key seconds value
SETEX session 3600 "user_session_data"

# 设置值并设置过期时间（毫秒）
PSETEX key milliseconds value

# 设置值，如果 key 不存在
SETNX key value
SETNX lock "locked"

# 批量设置
MSET key1 value1 key2 value2
MSET name "张三" age 25

# 批量获取
MGET key1 key2
MGET name age

# 自增/自减
INCR counter        # 自增 1
DECR counter        # 自减 1
INCRBY counter 5    # 增加指定值
DECRBY counter 3    # 减少指定值

# 追加字符串
APPEND key "追加内容"

# 获取字符串长度
STRLEN key
```

### 2.2 Hash（哈希）

适合存储对象，是 field-value 的映射表。

```bash
# 设置单个字段
HSET key field value
HSET user:1001 name "张三"
HSET user:1001 age 25

# 获取单个字段
HGET key field
HGET user:1001 name

# 批量设置
HMSET key field1 value1 field2 value2
HMSET user:1001 name "张三" age 25 email "zhangsan@example.com"

# 批量获取
HMGET key field1 field2
HMGET user:1001 name age

# 获取所有字段和值
HGETALL key
HGETALL user:1001

# 获取所有字段
HKEYS key

# 获取所有值
HVALS key

# 获取字段数量
HLEN key

# 删除字段
HDEL key field1 field2

# 字段是否存在
HEXISTS key field

# 字段值增加
HINCRBY key field increment
HINCRBY user:1001 age 1
```

### 2.3 List（列表）

有序的字符串列表，支持从两端推入/弹出元素。

```bash
# 从左侧推入（头部）
LPUSH key value1 value2
LPUSH list "a" "b" "c"    # 列表顺序：c b a

# 从右侧推入（尾部）
RPUSH key value1 value2
RPUSH list "x" "y" "z"    # 列表顺序：c b a x y z

# 从左侧弹出（头部）
LPOP key
LPOP list                  # 返回 "c"

# 从右侧弹出（尾部）
RPOP key
RPOP list                  # 返回 "z"

# 获取指定范围的元素
LRANGE key start stop
LRANGE list 0 -1          # 获取所有元素
LRANGE list 0 2           # 获取前 3 个元素

# 获取列表长度
LLEN key

# 获取指定索引的元素
LINDEX key index
LINDEX list 0             # 获取第一个元素

# 设置指定索引的值
LSET key index value
LSET list 0 "new_value"

# 删除指定数量的元素
LREM key count value
LREM list 2 "a"           # 从左到右删除 2 个 "a"

# 截取列表
LTRIM key start stop
LTRIM list 0 9            # 只保留前 10 个元素

# 阻塞弹出
BLPOP key timeout
BRPOP key timeout

# 将元素从一个列表移到另一个列表
RPOPLPUSH source destination
```

### 2.4 Set（集合）

无序的字符串集合，成员唯一。

```bash
# 添加成员
SADD key member1 member2
SADD set "a" "b" "c"

# 移除成员
SREM key member1 member2

# 获取所有成员
SMEMBERS key

# 判断成员是否存在
SISMEMBER key member

# 获取集合大小
SCARD key

# 随机返回并移除一个成员
SPOP key count

# 随机返回成员（不移除）
SRANDMEMBER key count

# 交集
SINTER key1 key2
SINTER set1 set2

# 并集
SUNION key1 key2
SUNION set1 set2

# 差集
SDIFF key1 key2
SDIFF set1 set2          # set1 - set2

# 将交集/并集/差集存储到新集合
SINTERSTORE destination key1 key2
SUNIONSTORE destination key1 key2
SDIFFSTORE destination key1 key2

# 移动成员到另一个集合
SMOVE source destination member
```

### 2.5 Sorted Set（有序集合）

有序且唯一的字符串集合，每个成员关联一个分数。

```bash
# 添加成员
ZADD key score1 member1 score2 member2
ZADD leaderboard 100 "player1" 200 "player2"

# 获取成员分数
ZSCORE key member
ZSCORE leaderboard "player1"

# 增加成员分数
ZINCRBY key increment member
ZINCRBY leaderboard 50 "player1"

# 获取排名（从低到高）
ZRANK key member
ZRANK leaderboard "player1"

# 获取排名（从高到低）
ZREVRANK key member

# 获取指定范围的成员（按分数）
ZRANGE key start stop [WITHSCORES]
ZRANGE leaderboard 0 -1 WITHSCORES

# 获取指定范围的成员（按分数从高到低）
ZREVRANGE key start stop [WITHSCORES]

# 按分数范围获取
ZRANGEBYSCORE key min max [WITHSCORES] [LIMIT offset count]
ZRANGEBYSCORE leaderboard 100 200

# 按分数范围获取成员数量
ZCOUNT key min max
ZCOUNT leaderboard 100 200

# 获取集合大小
ZCARD key

# 移除成员
ZREM key member1 member2

# 按排名范围移除
ZREMRANGEBYRANK key start stop

# 按分数范围移除
ZREMRANGEBYSCORE key min max

# 交集
ZINTERSTORE destination numkeys key1 key2 [WEIGHTS weight1 weight2] [AGGREGATE SUM|MIN|MAX]

# 并集
ZUNIONSTORE destination numkeys key1 key2 [WEIGHTS weight1 weight2] [AGGREGATE SUM|MIN|MAX]
```

### 2.6 其他数据类型

#### Bitmap（位图）

```bash
# 设置位
SETBIT key offset value
SETBIT user:1001:online 0 1

# 获取位
GETBIT key offset
GETBIT user:1001:online 0

# 统计位为 1 的数量
BITCOUNT key [start end]
BITCOUNT user:1001:online

# 位运算
BITOP operation destkey key1 key2
BITOP AND result key1 key2
```

#### HyperLogLog（基数统计）

```bash
# 添加元素
PFADD key element1 element2
PFADD users "user1" "user2" "user3"

# 统计基数
PFCOUNT key
PFCOUNT users

# 合并
PFMERGE destkey sourcekey1 sourcekey2
```

#### Geospatial（地理位置）

```bash
# 添加地理位置
GEOADD key longitude latitude member
GEOADD locations 116.40 39.90 "北京" 121.47 31.23 "上海"

# 获取位置
GEOPOS key member
GEOPOS locations "北京"

# 计算距离
GEODIST key member1 member2 [unit]
GEODIST locations "北京" "上海" km

# 获取指定范围内的成员
GEORADIUS key longitude latitude radius unit [WITHCOORD] [WITHDIST]
GEORADIUS locations 116.40 39.90 100 km

# 获取指定成员范围内的成员
GEORADIUSBYMEMBER key member radius unit
```

---

## 三、常用命令语法

### 3.1 Key 管理命令

```bash
# 查看所有 key
KEYS pattern
KEYS *              # 查看所有
KEYS user:*         # 查看 user: 开头的

# 安全遍历 key（生产环境推荐）
SCAN cursor [MATCH pattern] [COUNT count]
SCAN 0 MATCH user:* COUNT 100

# 判断 key 是否存在
EXISTS key
EXISTS user:1001

# 删除 key
DEL key1 key2
DEL user:1001

# 设置过期时间
EXPIRE key seconds
EXPIRE user:1001 3600

# 设置过期时间（毫秒）
PEXPIRE key milliseconds

# 设置过期时间（时间戳）
EXPIREAT key timestamp
PEXPIREAT key milliseconds-timestamp

# 获取过期时间
TTL key             # 返回秒
PTTL key            # 返回毫秒

# 移除过期时间
PERSIST key

# 查看 key 的类型
TYPE key

# 重命名 key
RENAME key newkey

# 安全重命名（新 key 不存在时）
RENAMENX key newkey

# 随机返回一个 key
RANDOMKEY

# 序列化 key
DUMP key

# 反序列化
RESTORE key ttl serialized-value

# 迁移 key
MIGRATE host port key destination-db timeout [COPY] [REPLACE]

# 移动 key 到指定数据库
MOVE key db
```

### 3.2 数据库管理命令

```bash
# 切换数据库
SELECT index
SELECT 1

# 清空当前数据库
FLUSHDB

# 清空所有数据库
FLUSHALL

# 异步清空
FLUSHDB ASYNC
FLUSHALL ASYNC

# 查看数据库 key 数量
DBSIZE

# 查看服务器信息
INFO [section]
INFO server
INFO memory
INFO replication
INFO keyspace

# 监控命令执行
MONITOR

# 配置管理
CONFIG GET parameter
CONFIG SET parameter value
CONFIG RESETSTAT
```

### 3.3 事务管理

```bash
# 开始事务
MULTI

# 执行命令（进入队列）
SET key1 value1
SET key2 value2

# 提交事务
EXEC

# 取消事务
DISCARD

# 乐观锁
WATCH key1 key2
MULTI
SET key1 value1
EXEC

# 取消监听
UNWATCH
```

### 3.4 发布/订阅

```bash
# 订阅频道
SUBSCRIBE channel1 channel2

# 取消订阅
UNSUBSCRIBE channel1 channel2

# 发布消息
PUBLISH channel message

# 订阅模式
PSUBSCRIBE pattern1 pattern2
PSUBSCRIBE news.*

# 取消模式订阅
PUNSUBSCRIBE pattern1
```

### 3.5 Lua 脚本

```bash
# 执行 Lua 脚本
EVAL script numkeys key1 key2 arg1 arg2
EVAL "return redis.call('set', KEYS[1], ARGV[1])" 1 mykey myvalue

# 加载脚本
SCRIPT LOAD script
SCRIPT LOAD "return redis.call('set', KEYS[1], ARGV[1])"

# 执行加载的脚本
EVALSHA sha1 numkeys key1 key2 arg1 arg2

# 脚本管理
SCRIPT EXISTS sha1 [sha1 ...]
SCRIPT FLUSH
SCRIPT KILL
```

### 3.6 管道（Pipeline）

```bash
# 客户端使用管道批量执行命令
# Redis CLI
redis-cli --pipe < commands.txt

# Python 示例
import redis
r = redis.Redis()
pipe = r.pipeline()
pipe.set('key1', 'value1')
pipe.set('key2', 'value2')
pipe.get('key1')
results = pipe.execute()
```

---

## 四、使用场景

### 4.1 缓存

#### 4.1.1 数据库查询缓存

```bash
# 缓存用户信息
HSET user:1001 name "张三" age 25 email "zhangsan@example.com"
EXPIRE user:1001 3600

# 缓存商品详情
HSET product:2001 name "iPhone 15" price 7999 stock 100
EXPIRE product:2001 1800
```

#### 4.1.2 Session 共享

```bash
# 存储用户 Session
SET session:abc123 {"user_id": 1001, "login_time": 1234567890}
EXPIRE session:abc123 1800

# 验证 Session
GET session:abc123
```

#### 4.1.3 热点数据缓存

```bash
# 缓存首页数据
SET homepage:data {"articles": [...], "banners": [...]}
EXPIRE homepage:data 300

# 缓存排行榜
ZADD ranking 100 "user1" 200 "user2" 300 "user3"
EXPIRE ranking 60
```

### 4.2 分布式锁

```bash
# 获取锁（SETNX + EXPIRE 原子操作）
SET lock:resource unique_value NX EX 30

# 释放锁（Lua 脚本保证原子性）
EVAL "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end" 1 lock:resource unique_value

# 可重入锁（使用 Hash）
HSET lock:resource client_id 1
EXPIRE lock:resource 30
HINCRBY lock:resource client_id 1    # 重入
HINCRBY lock:resource client_id -1   # 释放一次
```

### 4.3 计数器

```bash
# 文章阅读量
INCR article:1001:views

# 用户点赞数
INCR article:1001:likes

# 接口调用次数
INCR api:calls:2024-01-01

# 限流器（滑动窗口）
MULTI
ZADD rate:limit:1001 timestamp request_id
ZREMRANGEBYSCORE rate:limit:1001 0 (timestamp - 60)
ZCARD rate:limit:1001
EXEC
```

### 4.4 消息队列

```bash
# 简单消息队列（List）
LPUSH queue:tasks {"task_id": 1, "type": "email"}
BRPOP queue:tasks 0

# 延迟队列（Sorted Set）
ZADD delay:queue timestamp {"task_id": 1, "execute_at": timestamp}

# 发布/订阅模式
PUBLISH channel:order {"order_id": 1001, "status": "paid"}
SUBSCRIBE channel:order
```

### 4.5 排行榜

```bash
# 游戏排行榜
ZADD leaderboard 1500 "player1"
ZADD leaderboard 2000 "player2"
ZADD leaderboard 1800 "player3"

# 获取 Top 10
ZREVRANGE leaderboard 0 9 WITHSCORES

# 获取玩家排名
ZREVRANK leaderboard "player1"

# 更新分数
ZINCRBY leaderboard 100 "player1"
```

### 4.6 分布式 Session

```bash
# 存储 Session
HSET session:token123 user_id 1001
HSET session:token123 username "zhangsan"
HSET session:token123 login_time 1234567890
EXPIRE session:token123 1800

# 验证 Session
HGETALL session:token123

# 刷新 Session
EXPIRE session:token123 1800
```

### 4.7 限流器

```bash
# 固定窗口限流
INCR rate:limit:user:1001:202401011200
EXPIRE rate:limit:user:1001:202401011200 60

# 滑动窗口限流（Lua 脚本）
EVAL "
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local current = tonumber(ARGV[3])

redis.call('ZADD', key, current, current .. math.random())
redis.call('ZREMRANGEBYSCORE', key, 0, current - window)
local count = redis.call('ZCARD', key)

if count > limit then
    return 0
else
    redis.call('EXPIRE', key, window / 1000)
    return 1
end
" 1 rate:limit:user:1001 100 60000 1234567890000
```

### 4.8 签到打卡

```bash
# 用户签到（使用 Bitmap）
SETBIT sign:user:1001:202401 0 1    # 1 月 1 日签到
SETBIT sign:user:1001:202401 1 1    # 1 月 2 日签到

# 查询是否签到
GETBIT sign:user:1001:202401 0

# 统计签到天数
BITCOUNT sign:user:1001:202401

# 连续签到检查
BITCOUNT sign:user:1001:202401 0 6  # 检查前 7 天
```

---

## 五、性能优化

### 5.1 内存优化

#### 5.1.1 内存淘汰策略

```conf
# redis.conf 配置
maxmemory 2gb                    # 最大内存
maxmemory-policy allkeys-lru     # 淘汰策略

# 可选策略：
# noeviction        - 不淘汰，内存满时拒绝写入
# allkeys-lru       - 所有 key 中淘汰最近最少使用的
# volatile-lru      - 设置了过期时间的 key 中淘汰
# allkeys-random    - 随机淘汰
# volatile-random   - 设置了过期时间的 key 中随机淘汰
# volatile-ttl      - 淘汰剩余时间最短的
# allkeys-lfu       - 所有 key 中淘汰最不常用的（4.0+）
# volatile-lfu      - 设置了过期时间的 key 中淘汰最不常用的
```

#### 5.1.2 内存编码优化

```bash
# Hash 优化（使用 ziplist 编码）
hash-max-ziplist-entries 512     # 元素数量阈值
hash-max-ziplist-value 64        # 值大小阈值

# List 优化（使用 ziplist 编码）
list-max-ziplist-size -2         # -2 表示 8KB

# Set 优化（使用 intset 编码）
set-max-intset-entries 512

# ZSet 优化（使用 ziplist 编码）
zset-max-ziplist-entries 128
zset-max-ziplist-value 64

# HyperLogLog 优化
hll-sparse-max-bytes 3000
```

#### 5.1.3 内存分配优化

```bash
# 使用小内存对象
# 避免大 key
HSET user:1001 name "张三"
HSET user:1001 age 25
# 而不是
SET user:1001 {"name":"张三","age":25,...}  # 大 JSON

# 拆分大 key
# 不好：
SET article:1001 {"title":"...", "content":"很长的内容...", "comments":[...]}

# 好：
SET article:1001:meta {"title":"...", "author":"..."}
SET article:1001:content "很长的内容..."
LPUSH article:1001:comments "comment1" "comment2"
```

### 5.2 连接优化

#### 5.2.1 连接池配置

```java
// Java Jedis 连接池配置
JedisPoolConfig config = new JedisPoolConfig();
config.setMaxTotal(100);           // 最大连接数
config.setMaxIdle(50);             // 最大空闲连接
config.setMinIdle(10);             // 最小空闲连接
config.setMaxWaitMillis(5000);     // 获取连接最大等待时间
config.setTestOnBorrow(true);      // 获取连接时检测
config.setTestOnReturn(false);     // 归还连接时检测
config.setTestWhileIdle(true);     // 空闲时检测

JedisPool pool = new JedisPool(config, "localhost", 6379);
```

#### 5.2.2 管道优化

```java
// 使用 Pipeline 批量操作
Jedis jedis = pool.getResource();
Pipeline pipeline = jedis.pipelined();

for (int i = 0; i < 1000; i++) {
    pipeline.set("key:" + i, "value:" + i);
}

List<Object> results = pipeline.syncAndReturnAll();
jedis.close();

// 对比：不用 Pipeline
for (int i = 0; i < 1000; i++) {
    jedis.set("key:" + i, "value:" + i);  // 1000 次网络往返
}
```

### 5.3 命令优化

#### 5.3.1 避免慢查询

```bash
# 避免使用 KEYS *
# 不好：
KEYS *

# 好：
SCAN 0 MATCH * COUNT 100

# 避免大 key 操作
# 不好：
DEL big_key  # 大 key 删除会阻塞

# 好：
# 使用 UNLINK（异步删除，4.0+）
UNLINK big_key

# 或者分批删除
EVAL "
local key = KEYS[1]
local batch = tonumber(ARGV[1])
local cursor = redis.call('HSCAN', key, 0, 'COUNT', batch)
for i, field in ipairs(cursor[2]) do
    if i % 2 == 1 then
        redis.call('HDEL', key, field)
    end
end
return cursor[1]
" 1 big_hash 100
```

#### 5.3.2 合理使用数据结构

```bash
# 场景：存储用户信息
# 不好：
SET user:1001:name "张三"
SET user:1001:age 25
SET user:1001:email "zhangsan@example.com"

# 好：
HSET user:1001 name "张三" age 25 email "zhangsan@example.com"

# 场景：存储有序列表
# 不好：
LPUSH list "item1"
LPUSH list "item2"
# 需要排序时还要额外操作

# 好：
ZADD sorted_list 1 "item1"
ZADD sorted_list 2 "item2"
```

### 5.4 持久化优化

#### 5.4.1 RDB 优化

```conf
# redis.conf
save 900 1          # 900 秒内至少 1 个 key 改变
save 300 10         # 300 秒内至少 10 个 key 改变
save 60 10000       # 60 秒内至少 10000 个 key 改变

# 优化配置
rdbcompression yes          # 压缩 RDB 文件
rdbchecksum yes             # 校验和
dbfilename dump.rdb         # 文件名
dir /var/lib/redis          # 存储目录

# 禁用 RDB（纯缓存场景）
save ""
```

#### 5.4.2 AOF 优化

```conf
# AOF 配置
appendonly yes
appendfilename "appendonly.aof"

# 刷盘策略
# always  - 每次写入都刷盘（最安全，最慢）
# everysec - 每秒刷盘（推荐，折中方案）
# no      - 由操作系统决定（最快，可能丢失数据）
appendfsync everysec

# AOF 重写优化
no-appendfsync-on-rewrite yes     # 重写时不同步
auto-aof-rewrite-percentage 100   # 文件大小增长 100% 时重写
auto-aof-rewrite-min-size 64mb    # 最小重写大小

# 混合持久化（4.0+，推荐）
aof-use-rdb-preamble yes
```

### 5.5 主从复制优化

```conf
# 主节点配置
repl-backlog-size 1mb         # 复制积压缓冲区大小
repl-backlog-ttl 3600         # 积压缓冲区超时时间

# 从节点配置
replica-serve-stale-data yes  # 复制中断时是否提供旧数据
replica-read-only yes         # 从节点只读
replica-priority 100          # 从节点优先级

# 优化配置
repl-diskless-sync yes        # 无磁盘复制
repl-diskless-sync-delay 5    # 延迟同步时间
repl-timeout 60               # 复制超时时间
```

### 5.6 集群优化

```conf
# 集群配置
cluster-enabled yes
cluster-config-file nodes-6379.conf
cluster-node-timeout 15000

# 优化配置
cluster-require-full-coverage no    # 允许部分节点不可用
cluster-allow-reads-when-down no    # 集群下线时是否允许读

# 插槽分配优化
# 均匀分配插槽到不同节点
# 避免热点 key 集中在一个节点
```

---

## 六、持久化机制

### 6.1 RDB（快照）

#### 6.1.1 工作原理

- 在指定时间间隔内将内存数据集快照写入磁盘
- 触发条件：
  - 配置自动触发（save 配置）
  - 手动执行 `BGSAVE` 命令
  - 执行 `SHUTDOWN` 命令
  - 接收到 `SAVE` 命令（阻塞主进程）

#### 6.1.2 执行流程

```
1. Redis 父进程 fork 出子进程
2. 子进程将内存数据写入临时 RDB 文件
3. 写入完成后，替换旧的 RDB 文件
4. 父进程继续处理命令（期间产生的写入通过写时复制机制处理）
```

#### 6.1.3 优缺点

**优点：**
- 文件紧凑，适合备份
- 恢复速度快
- 对性能影响小（fork 子进程）

**缺点：**
- 可能丢失最后一次快照后的数据
- fork 过程可能阻塞（数据量大时）

### 6.2 AOF（追加文件）

#### 6.2.1 工作原理

- 记录每个写入命令到 AOF 文件
- 重启时重放 AOF 文件恢复数据

#### 6.2.2 AOF 重写

```
1. fork 子进程
2. 子进程根据内存数据生成新的 AOF 文件
3. 父进程继续处理命令，同时将新命令写入旧 AOF 文件和重写缓冲区
4. 子进程完成新 AOF 文件后，通知父进程
5. 父进程将重写缓冲区的命令追加到新 AOF 文件
6. 替换旧 AOF 文件
```

#### 6.2.3 优缺点

**优点：**
- 数据安全性高（最多丢失 1 秒数据）
- 文件可读（命令格式）

**缺点：**
- 文件体积大
- 恢复速度慢
- 对性能影响相对较大

### 6.3 混合持久化（推荐）

```conf
# Redis 4.0+ 支持
aof-use-rdb-preamble yes

# 工作原理
# AOF 重写时，前半部分是 RDB 格式，后半部分是 AOF 格式
# 结合了 RDB 恢复快和 AOF 数据安全的优点
```

---

## 七、高可用架构

### 7.1 主从复制

#### 7.1.1 配置

```conf
# 从节点配置
replicaof 192.168.1.100 6379
masterauth master_password

# 从节点只读
replica-read-only yes
```

#### 7.1.2 工作原理

```
1. 从节点连接主节点
2. 从节点发送 PSYNC 命令
3. 主节点执行 BGSAVE 生成 RDB，同时将新命令写入缓冲区
4. 主节点将 RDB 发送给从节点
5. 从节点加载 RDB 到内存
6. 主节点将缓冲区的命令发送给从节点执行
7. 后续命令实时同步
```

### 7.2 哨兵模式（Sentinel）

#### 7.2.1 配置

```conf
# sentinel.conf
sentinel monitor mymaster 192.168.1.100 6379 2
sentinel auth-pass mymaster password
sentinel down-after-milliseconds mymaster 30000
sentinel parallel-syncs mymaster 1
sentinel failover-timeout mymaster 180000
```

#### 7.2.2 功能

- **监控**：持续检查主从节点是否正常
- **通知**：节点故障时发送通知
- **自动故障转移**：主节点故障时自动将从节点提升为主节点
- **配置提供者**：客户端通过哨兵获取主节点地址

#### 7.2.3 故障转移流程

```
1. 哨兵检测到主节点不可达（主观下线）
2. 多个哨兵确认主节点不可达（客观下线）
3. 选举领头哨兵
4. 领头哨兵选择最优从节点
5. 将从节点提升为主节点
6. 通知其他从节点跟随新主节点
7. 通知客户端新主节点地址
```

### 7.3 集群模式（Cluster）

#### 7.3.1 架构特点

- **数据分片**：16384 个插槽分配到不同节点
- **去中心化**：所有节点通过 Gossip 协议通信
- **高可用**：每个节点可以有从节点

#### 7.3.2 配置

```conf
# redis.conf
cluster-enabled yes
cluster-config-file nodes-6379.conf
cluster-node-timeout 15000

# 启动集群
redis-cli --cluster create \
  192.168.1.1:6379 192.168.1.2:6379 192.168.1.3:6379 \
  --cluster-replicas 1
```

#### 7.3.3 数据路由

```
客户端发送命令 -> 计算 key 的 CRC16 值 -> 对 16384 取模 -> 确定插槽 -> 路由到对应节点
```

#### 7.3.4 集群限制

- 不支持跨插槽的事务
- 不支持跨插槽的管道
- 批量操作需要确保 key 在同一插槽（使用 hash tag）

```bash
# 使用 hash tag 确保 key 在同一插槽
SET {user}:1001:name "张三"
SET {user}:1001:age 25
# {user} 部分决定插槽
```

---

## 八、常见面试题

### 8.1 基础概念

#### Q1: Redis 为什么这么快？

**答：**
1. **基于内存操作**：内存响应时间远快于磁盘
2. **单线程模型**：避免上下文切换和锁竞争（6.0 后引入多线程处理网络 IO）
3. **高效数据结构**：针对场景优化的数据结构（如 ziplist、quicklist）
4. **IO 多路复用**：使用 epoll 处理大量连接
5. **协议简单**：RESP 协议解析高效

#### Q2: Redis 是单线程的，为什么还能处理高并发？

**答：**
1. **IO 多路复用**：使用 epoll 同时监听多个连接
2. **纯内存操作**：没有磁盘 IO 瓶颈
3. **单线程避免锁竞争**：不需要处理复杂的并发控制
4. **高效数据结构**：底层数据结构经过优化
5. **6.0 后多线程**：网络 IO 使用多线程，命令执行仍单线程

#### Q3: Redis 和 Memcached 的区别？

**答：**

| 特性 | Redis | Memcached |
|------|-------|-----------|
| 数据结构 | 丰富（String、Hash、List、Set、ZSet 等） | 仅 Key-Value |
| 持久化 | 支持 RDB 和 AOF | 不支持 |
| 集群 | 原生支持 | 客户端分片 |
| 线程模型 | 单线程（6.0 后多线程 IO） | 多线程 |
| 事务 | 支持 | 不支持 |
| 发布订阅 | 支持 | 不支持 |
| Lua 脚本 | 支持 | 不支持 |

### 8.2 数据类型

#### Q4: Redis 有哪些数据类型？应用场景？

**答：**

| 类型 | 应用场景 |
|------|---------|
| String | 缓存、计数器、分布式锁、Session |
| Hash | 对象存储、用户信息、商品详情 |
| List | 消息队列、时间线、排行榜 |
| Set | 标签、共同关注、去重 |
| ZSet | 排行榜、延迟队列、带权重的任务 |
| Bitmap | 签到、在线状态、布隆过滤器 |
| HyperLogLog | UV 统计、基数统计 |
| Geospatial | 地理位置、附近的人 |

#### Q5: String 和 Hash 存储对象有什么区别？

**答：**

| 对比项 | String（JSON） | Hash |
|--------|---------------|------|
| 结构 | 序列化的 JSON 字符串 | 字段-值映射 |
| 内存占用 | 较大（需要序列化） | 较小（ziplist 优化） |
| 读取单个字段 | 需要反序列化整个对象 | 直接读取，无需反序列化 |
| 修改单个字段 | 需要反序列化、修改、再序列化 | 直接修改 |
| 内存优化 | 无特殊优化 | ziplist 编码节省内存 |

**建议：** 对象字段较多且需要单独访问某些字段时，使用 Hash。

#### Q6: ZSet 的实现原理？

**答：**

底层使用两种编码：
1. **ziplist**：数据量小时使用，连续内存块
2. **skiplist + hashtable**：数据量大时使用
   - **跳表**：用于范围查询，平均 O(log N) 时间复杂度
   - **哈希表**：用于 O(1) 时间复杂度获取分数

跳表结构：
```
Level 3:  1 --------> 4 --------> 7
Level 2:  1 ----> 3 ----> 5 ----> 7
Level 1:  1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7
```

### 8.3 持久化

#### Q7: RDB 和 AOF 的区别？如何选择？

**答：**

| 对比项 | RDB | AOF |
|--------|-----|-----|
| 持久化方式 | 快照 | 追加命令 |
| 文件大小 | 小（二进制压缩） | 大（文本命令） |
| 恢复速度 | 快 | 慢 |
| 数据安全性 | 可能丢失最后一次快照后的数据 | 最多丢失 1 秒数据 |
| 性能影响 | fork 时可能阻塞 | 相对较大 |
| 适用场景 | 备份、灾难恢复 | 数据安全要求高 |

**建议：**
- 纯缓存场景：禁用持久化或仅用 RDB
- 数据安全要求高：使用混合持久化（AOF + RDB 前置）
- 备份场景：使用 RDB

#### Q8: Redis 4.0 的混合持久化了解吗？

**答：**

混合持久化结合了 RDB 和 AOF 的优点：
- AOF 重写时，前半部分是 RDB 格式
- 后半部分是增量 AOF 格式
- 恢复时先加载 RDB，再重放 AOF 命令
- 既保证了恢复速度，又保证了数据安全

### 8.4 高可用

#### Q9: Redis 主从复制的原理？

**答：**

1. **全量复制**：从节点首次连接主节点
   - 从节点发送 `PSYNC ? -1`
   - 主节点执行 `BGSAVE` 生成 RDB
   - 主节点将 RDB 发送给从节点
   - 从节点加载 RDB
   - 主节点发送缓冲区的命令

2. **增量复制**：网络中断后重连
   - 从节点发送 `PSYNC runid offset`
   - 主节点从偏移量开始发送命令
   - 如果偏移量过旧，退化为全量复制

#### Q10: 哨兵模式的工作原理？

**答：**

1. **监控**：哨兵每秒向主从节点发送 `PING`
2. **主观下线**：单个哨兵认为节点不可达
3. **客观下线**：超过配置的 quorum 个哨兵认为不可达
4. **选举领头哨兵**：通过 Raft 算法选举
5. **故障转移**：
   - 选择最优从节点（优先级、复制偏移量、runid）
   - 将从节点提升为主节点
   - 通知其他从节点跟随新主节点
6. **通知客户端**：客户端通过哨兵获取新主节点地址

#### Q11: Redis Cluster 的数据分片原理？

**答：**

1. **哈希槽**：16384 个插槽分配到不同节点
2. **key 路由**：`CRC16(key) % 16384` 确定插槽
3. **节点通信**：Gossip 协议交换状态
4. **故障检测**：节点间互相 `PING/PONG`
5. **故障转移**：从节点选举提升为主节点

**限制：**
- 跨插槽操作需要客户端处理
- 批量操作需要使用 hash tag

### 8.5 缓存问题

#### Q12: 什么是缓存穿透？如何解决？

**答：**

**定义：** 查询不存在的数据，导致请求穿透到数据库。

**解决方案：**
1. **布隆过滤器**：预先存储所有可能的 key
2. **空值缓存**：缓存空值，设置较短过期时间
3. **互斥锁**：只允许一个线程查询数据库

```java
// 布隆过滤器方案
if (!bloomFilter.mightContain(key)) {
    return null;  // 直接返回，不查数据库
}

// 空值缓存方案
String value = redis.get(key);
if (value == null) {
    value = db.query(key);
    if (value == null) {
        redis.setex(key, 60, "");  // 缓存空值
    } else {
        redis.setex(key, 3600, value);
    }
}
```

#### Q13: 什么是缓存击穿？如何解决？

**答：**

**定义：** 热点 key 过期瞬间，大量并发请求打到数据库。

**解决方案：**
1. **互斥锁**：只允许一个线程重建缓存
2. **逻辑过期**：不设置实际过期时间，在值中记录逻辑过期时间
3. **永不过期**：热点 key 永不过期，后台异步更新

```java
// 互斥锁方案
String getWithLock(String key) {
    String value = redis.get(key);
    if (value == null) {
        // 尝试获取锁
        if (redis.setnx("lock:" + key, "1", 10)) {
            try {
                value = db.query(key);
                redis.setex(key, 3600, value);
            } finally {
                redis.del("lock:" + key);
            }
        } else {
            Thread.sleep(100);  // 等待
            return getWithLock(key);  // 重试
        }
    }
    return value;
}
```

#### Q14: 什么是缓存雪崩？如何解决？

**答：**

**定义：** 大量 key 同时过期，或 Redis 宕机，导致请求全部打到数据库。

**解决方案：**
1. **随机过期时间**：避免 key 同时过期
2. **高可用**：使用哨兵或集群模式
3. **多级缓存**：本地缓存 + Redis
4. **限流降级**：保护数据库

```java
// 随机过期时间
int expireTime = 3600 + random.nextInt(300);  // 3600-3900 秒
redis.setex(key, expireTime, value);

// 多级缓存
String value = localCache.get(key);  // 本地缓存
if (value == null) {
    value = redis.get(key);  // Redis 缓存
    if (value != null) {
        localCache.put(key, value);
    } else {
        value = db.query(key);  // 数据库
        localCache.put(key, value);
        redis.setex(key, 3600, value);
    }
}
```

### 8.6 分布式锁

#### Q15: 如何用 Redis 实现分布式锁？

**答：**

**基本实现：**
```bash
# 获取锁
SET lock:resource unique_value NX EX 30

# 释放锁（Lua 脚本）
EVAL "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end" 1 lock:resource unique_value
```

**关键要点：**
1. **互斥性**：使用 `SETNX` 保证只有一个客户端获取锁
2. **防死锁**：设置过期时间，避免客户端崩溃后锁无法释放
3. **原子性**：加锁和设置过期时间必须是原子操作
4. **唯一性**：value 使用唯一标识（如 UUID），防止误删他人锁
5. **释放锁原子性**：使用 Lua 脚本保证判断和删除的原子性

**问题与优化：**
- **锁过期但业务未完成**：使用看门狗机制自动续期（Redisson）
- **主从切换丢锁**：使用 RedLock 算法（多节点加锁）

#### Q16: RedLock 算法了解吗？

**答：**

**背景：** 解决主从切换导致的锁丢失问题。

**实现步骤：**
1. 获取当前时间
2. 依次向 N 个独立的 Redis 节点请求锁
3. 计算获取锁的总耗时
4. 只有当超过半数节点获取成功，且总耗时小于锁过期时间，才认为获取成功
5. 锁的实际过期时间 = 原过期时间 - 获取耗时

**争议：**
- Martin Kleppmann 质疑：时钟跳跃、GC 停顿等问题
- Antirez 反驳：极端场景下的权衡

**建议：** 如果对一致性要求极高，使用 ZooKeeper 实现分布式锁。

### 8.7 性能优化

#### Q17: Redis 的内存淘汰策略有哪些？

**答：**

| 策略 | 说明 |
|------|------|
| noeviction | 不淘汰，内存满时拒绝写入 |
| allkeys-lru | 所有 key 中淘汰最近最少使用的 |
| volatile-lru | 设置了过期时间的 key 中淘汰 |
| allkeys-random | 随机淘汰 |
| volatile-random | 设置了过期时间的 key 中随机淘汰 |
| volatile-ttl | 淘汰剩余时间最短的 |
| allkeys-lfu | 所有 key 中淘汰最不常用的（4.0+） |
| volatile-lfu | 设置了过期时间的 key 中淘汰最不常用的 |

**选择建议：**
- 缓存场景：allkeys-lru 或 allkeys-lfu
- 部分持久化：volatile-lru 或 volatile-lfu

#### Q18: 如何发现和优化慢查询？

**答：**

**发现慢查询：**
```bash
# 配置慢查询日志
slowlog-log-slower-than 10000  # 超过 10ms 记录
slowlog-max-len 128            # 最多记录 128 条

# 查看慢查询
SLOWLOG GET [count]
SLOWLOG LEN
SLOWLOG RESET
```

**常见慢查询：**
- `KEYS *`：使用 `SCAN` 替代
- 大 key 操作：拆分大 key，使用 `UNLINK` 异步删除
- 复杂命令：`SORT`、`ZRANGEBYSCORE` 等，优化数据结构

**优化建议：**
1. 定期分析慢查询日志
2. 使用 `redis-cli --bigkeys` 扫描大 key
3. 使用 `redis-cli --hotkeys` 扫描热 key
4. 合理设计数据结构，避免复杂操作

#### Q19: 什么是 Pipeline？有什么优势？

**答：**

**定义：** 管道，将多个命令打包一次性发送到服务器，减少网络往返。

**优势：**
- 减少网络 RTT（Round Trip Time）
- 提升吞吐量（可达 10 倍以上）

**使用示例：**
```java
Pipeline pipeline = jedis.pipelined();
for (int i = 0; i < 1000; i++) {
    pipeline.set("key:" + i, "value:" + i);
}
List<Object> results = pipeline.syncAndReturnAll();
```

**注意事项：**
- Pipeline 不是原子操作
- 单个 Pipeline 命令不宜过多（建议 500-1000）
- 跨插槽操作在集群模式下需要特殊处理

### 8.8 实战场景

#### Q20: 如何实现延迟队列？

**答：**

**方案一：Sorted Set**
```bash
# 添加延迟任务
ZADD delay:queue timestamp "task_data"

# 轮询消费（Lua 脚本）
EVAL "
local tasks = redis.call('ZRANGEBYSCORE', KEYS[1], 0, ARGV[1], 'LIMIT', 0, 1)
if #tasks > 0 then
    redis.call('ZREM', KEYS[1], tasks[1])
    return tasks[1]
end
return nil
" 1 delay:queue current_timestamp
```

**方案二：使用 Redisson 的 DelayedQueue**
```java
RBlockingQueue<String> queue = redisson.getBlockingQueue("queue");
RDelayedQueue<String> delayedQueue = redisson.getDelayedQueue(queue);

// 添加延迟任务
delayedQueue.offer("task", 10, TimeUnit.SECONDS);

// 消费任务
String task = queue.take();
```

#### Q21: 如何实现限流器？

**答：**

**方案一：固定窗口**
```bash
# 每分钟最多 100 次请求
INCR rate:limit:user:1001:202401011200
EXPIRE rate:limit:user:1001:202401011200 60
```

**方案二：滑动窗口**
```bash
# Lua 脚本实现
EVAL "
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local current = tonumber(ARGV[3])

redis.call('ZADD', key, current, current .. math.random())
redis.call('ZREMRANGEBYSCORE', key, 0, current - window)
local count = redis.call('ZCARD', key)

if count > limit then
    return 0
else
    redis.call('EXPIRE', key, window / 1000)
    return 1
end
" 1 rate:limit:user:1001 100 60000 1234567890000
```

**方案三：令牌桶（Redisson）**
```java
RRateLimiter rateLimiter = redisson.getRateLimiter("rate_limiter");
rateLimiter.trySetRate(RateType.OVERALL, 100, 1, RateIntervalUnit.MINUTES);

if (rateLimiter.tryAcquire()) {
    // 处理请求
} else {
    // 限流
}
```

#### Q22: 如何实现分布式 Session？

**答：**

**方案一：Redis 存储 Session**
```java
// 登录时创建 Session
String sessionId = UUID.randomUUID().toString();
Map<String, String> sessionData = new HashMap<>();
sessionData.put("user_id", "1001");
sessionData.put("username", "zhangsan");
sessionData.put("login_time", String.valueOf(System.currentTimeMillis()));

jedis.hmset("session:" + sessionId, sessionData);
jedis.expire("session:" + sessionId, 1800);  // 30 分钟过期

// 验证 Session
Map<String, String> data = jedis.hgetAll("session:" + sessionId);
if (data != null && !data.isEmpty()) {
    jedis.expire("session:" + sessionId, 1800);  // 刷新过期时间
    return data;
}
```

**方案二：Spring Session + Redis**
```yaml
# application.yml
spring:
  session:
    store-type: redis
    timeout: 1800
  redis:
    host: localhost
    port: 6379
```

```java
@Configuration
@EnableRedisHttpSession
public class SessionConfig {
    // 自动配置
}
```

---

## 附录：常用配置参考

### 基础配置

```conf
# 绑定地址
bind 127.0.0.1

# 端口
port 6379

# 后台运行
daemonize yes

# 日志
logfile /var/log/redis/redis.log
loglevel notice

# 数据库数量
databases 16

# 密码
requirepass your_password

# 最大连接数
maxclients 10000

# 最大内存
maxmemory 2gb
maxmemory-policy allkeys-lru

# 超时时间
timeout 300
tcp-keepalive 300
```

### 持久化配置

```conf
# RDB
save 900 1
save 300 10
save 60 10000
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /var/lib/redis

# AOF
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite yes
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-use-rdb-preamble yes
```

### 复制配置

```conf
# 主节点
repl-backlog-size 1mb
repl-backlog-ttl 3600

# 从节点
replicaof 192.168.1.100 6379
masterauth master_password
replica-serve-stale-data yes
replica-read-only yes
replica-priority 100
```

---

**文档说明：** 本文档涵盖了 Redis 的核心知识点，包括基础概念、数据类型、常用命令、使用场景、性能优化、持久化机制、高可用架构以及常见面试题。适合 Redis 初学者和面试准备参考。
