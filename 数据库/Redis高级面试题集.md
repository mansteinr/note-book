# Redis 高级工程师面试题集

> 本面试题集面向 Redis 高级工程师岗位，系统覆盖核心原理与数据结构、持久化机制、内存管理与淘汰策略、高可用方案、缓存问题、性能优化、分布式锁与限流、实际应用场景等八大核心领域。每道题包含问题描述、深度参考答案、实际项目案例及评分要点，兼顾理论深度与工程实践。

---

## 目录

- [第一篇 核心原理与数据结构](#第一篇-核心原理与数据结构)
- [第二篇 持久化机制](#第二篇-持久化机制)
- [第三篇 内存管理与淘汰策略](#第三篇-内存管理与淘汰策略)
- [第四篇 高可用方案](#第四篇-高可用方案)
- [第五篇 缓存问题与解决方案](#第五篇-缓存问题与解决方案)
- [第六篇 性能优化](#第六篇-性能优化)
- [第七篇 分布式锁与限流](#第七篇-分布式锁与限流)
- [第八篇 实际应用场景](#第八篇-实际应用场景)
- [附录 评分标准与面试指南](#附录-评分标准与面试指南)

---

## 第一篇 核心原理与数据结构

### Q1.1 Redis 单线程模型为什么这么快？6.0 之后引入多线程的目的是什么？

**问题描述**：请说明 Redis 单线程为何能达到极高 QPS，以及 6.0 引入多线程的背景与机制。

**参考答案**：

**1. Redis 单线程为何快**

Redis 的"单线程"指**命令处理（接收、解析、执行、返回）在主线程中完成**，但其后台其实有线程做持久化、AOF 刷盘、惰性删除等辅助工作。单线程快的原因：

| 原因 | 说明 |
| --- | --- |
| **完全基于内存** | 数据全在内存，读写速度达 ns 级，无磁盘 IO 瓶颈 |
| **IO 多路复用** | epoll 单线程监听大量连接，非阻塞 IO，避免线程切换开销 |
| **单线程避免锁竞争** | 无加锁、无死锁、无线程切换，操作无竞争 |
| **数据结构高效** | SDS、跳表、压缩列表等针对性优化 |
| **C 语言实现** | 贴近底层，执行效率高 |

**2. IO 多路复用模型**

```
                    ┌─────────────────────────┐
   客户端1 ────────►│                         │
   客户端2 ────────►│   epoll (IO 多路复用)    │── 事件循环 ──► 命令执行
   客户端3 ────────►│   单线程监听所有 socket   │
   客户端N ────────►│                         │
                    └─────────────────────────┘
```

- 使用 epoll（Linux）、kqueue（Mac）、select（Windows）
- 单线程处理数万并发连接，事件驱动的 Reactor 模式

**3. 单线程的瓶颈**

- **CPU 密集命令阻塞**：`KEYS *`、`SORT`、`LRANGE 0 -1` 等慢命令会阻塞所有客户端
- **网络 IO 成为瓶颈**：高并发下读写网络 buffer 占用主线程时间，QPS 上限受限于单核

**4. Redis 6.0 多线程模型**

6.0 引入多线程**仅用于网络 IO**（读取请求、发送响应），**命令执行仍单线程**：

```
                ┌─────────────────────────────────────┐
   客户端1 ────►│  IO 线程1（读 socket、解析协议）     │
   客户端2 ────►│  IO 线程2（读 socket、解析协议）     │──┐
   客户端3 ────►│  IO 线程3（读 socket、解析协议）     │  │
                └─────────────────────────────────────┘  │
                                                          ▼
                                          ┌─────────────────────────┐
                                          │  主线程（命令执行，串行） │
                                          └─────────────────────────┘
                                                          │
                                                          ▼
                                          ┌─────────────────────────┐
                                          │  IO 线程（写回响应）     │
                                          └─────────────────────────┘
```

**开启方式**：

```conf
# redis.conf
io-threads 4              # IO 线程数（建议 CPU 核数的一半，不超过 8）
io-threads-do-reads yes   # IO 线程也参与读（默认只写）
```

**5. 为什么命令执行仍单线程**

- 保持命令原子性，无需加锁
- 避免线程切换开销
- Redis 瓶颈通常在网络 IO 而非 CPU，多线程 IO 已足够

**实际案例**：
- **项目背景**：社交 Feed 流服务，Redis QPS 达 12 万，CPU 单核 90%，P99 抖动到 5ms
- **问题分析**：主线程大量时间花在 socket 读写，命令执行只占 30%
- **优化方案**：升级 6.0+，开启 `io-threads 4`
- **最终效果**：QPS 提升到 18 万，P99 降到 1.5ms，CPU 利用更均衡

**评分要点**：
- ✅ 单线程快的 5 大原因（必备）
- ✅ epoll IO 多路复用（必备）
- ✅ 6.0 多线程仅用于网络 IO（核心）
- ✅ 命令执行为何仍单线程（加分）
- ✅ 实际性能数据（加分）

---

### Q1.2 Redis 的五种基本数据类型及底层实现？什么场景下编码会发生转换？

**问题描述**：请说明 String、List、Hash、Set、ZSet 五种类型的底层数据结构及编码转换条件。

**参考答案**：

**1. 类型与编码对应关系**

| 类型 | 底层编码（Redis 7.x） | 转换条件 |
| --- | --- | --- |
| **String** | int / embstr / raw | 数字用 int；≤44 字节用 embstr；否则 raw |
| **List** | listpack（7.0前为 quicklist） | 元素少且小用 listpack；否则 quicklist |
| **Hash** | listpack / hashtable | 元素 ≤128 且单值 ≤64 字节用 listpack；否则 hashtable |
| **Set** | intset / listpack / hashtable | 全整数且 ≤512 用 intset；少量字符串用 listpack；否则 hashtable |
| **ZSet** | listpack / skiplist | 元素 ≤128 且单值 ≤64 字节用 listpack；否则 skiplist+hashtable |

**2. String 三种编码**

```c
// int 编码：值是 long 范围内的整数
SET counter 100
OBJECT ENCODING counter  →  "int"

// embstr 编码：≤44 字节，SDS 与对象内存连续分配，一次 malloc
SET name "tom"
OBJECT ENCODING name  →  "embstr"

// raw 编码：>44 字节，SDS 与对象分开 malloc
SET desc "aaaa...（50个字符）"
OBJECT ENCODING desc  →  "raw"
```

**embstr 为何是 44 字节**：64 字节内存块减去 redisObject 头部（16B）+ SDS 头部（3B）+ 结尾 `\0`（1B）= 44 字节。

**3. SDS（Simple Dynamic String）**

Redis 自定义字符串，相比 C 字符串的优势：

| 特性 | C 字符串 | SDS |
| --- | --- | --- |
| 获取长度 | O(N) 遍历 | O(1)（len 字段） |
| 缓冲区溢出 | 可能溢出 | 自动扩容，不会溢出 |
| 修改性能 | 每次 realloc | 预分配 + 惰性释放，减少 realloc |
| 二进制安全 | ❌ 遇 `\0` 截断 | ✅ 用 len 判断结束，可存任意数据 |
| 兼容 | - | 兼容 `<string.h>` 函数 |

**4. List - quicklist（快速链表）**

quicklist = **双向链表 + 每个节点是 ziplist/listpack**，兼顾内存与性能：

```
quicklist:
┌────────┐    ┌────────┐    ┌────────┐
│ node1  │◄──►│ node2  │◄──►│ node3  │
│listpack│    │listpack│    │listpack│
│[a,b,c] │    │[d,e,f] │    │[g,h]   │
└────────┘    └────────┘    └────────┘
```

- 每个 listpack 节点存多个元素，减少指针开销
- 中间节点可 LZF 压缩，节省内存

**5. ZSet - skiplist（跳表）**

跳表是**多层有序链表**，通过概率性索引实现 O(logN) 查找：

```
Level 3:  HEAD ─────────────────────────────► 50 ─────► NULL
Level 2:  HEAD ───────► 20 ─────────────────► 50 ─────► NULL
Level 1:  HEAD ──► 10 ─► 20 ──────► 30 ────► 50 ─────► NULL
Level 0:  HEAD ──► 10 ─► 20 ─► 25 ─► 30 ─► 40 ─► 50 ─► NULL
```

**为什么用跳表而非红黑树**：
- 实现简单，代码量少
- 范围查询友好（链表顺序遍历）
- 并发友好（局部锁即可）
- 内存灵活，可调层数

**ZSet 实际用 skiplist + hashtable 双结构**：skiplist 支持范围查询，hashtable 支持 O(1) 单点查询。

**6. 编码转换示例**

```bash
# Hash 元素少时用 listpack
HSET user:1 name tom age 20
OBJECT ENCODING user:1  →  "listpack"

# 元素超过 128 或单值超过 64 字节，转 hashtable
HSET user:1 desc "aaa...（70个字符）"
OBJECT ENCODING user:1  →  "hashtable"
```

**转换不可逆**：从小对象转大对象后，即使元素再减少，也不会回退（避免抖动）。

**实际案例**：
- **项目背景**：排行榜存 100 万用户分数，ZSet 内存占用 800MB
- **优化**：将用户 ID 从字符串改为数字，利用 intset 节省内存
- **效果**：内存降至 320MB，节省 60%

**评分要点**：
- ✅ 五种类型与底层编码对应（必备）
- ✅ embstr/raw 转换边界 44 字节（加分）
- ✅ SDS 优势（O(1) 长度、二进制安全）（必备）
- ✅ 跳表原理及为何不用红黑树（核心）
- ✅ 编码转换条件（必备）

---

### Q1.3 Redis 的跳表（SkipList）原理？为什么 ZSet 用跳表而非红黑树？

**问题描述**：请详细说明跳表的查找、插入原理，并对比红黑树。

**参考答案**：

**1. 跳表结构**

跳表 = **多层链表**，每层是下层的"快速通道"。最底层（L0）包含所有元素，上层节点是下层节点的索引。

```
查找 30 的过程：

L3:  HEAD ─────────────────────────────► 50 ────► NULL
                                       │ 比较50>30，下一层
L2:  HEAD ───────► 20 ─────────────────► 50 ────► NULL
                    │ 找到20<30，向右   │ 比较50>30，下一层
L1:  HEAD ─► 10 ──► 20 ──────► 30 ────► 50 ────► NULL
                              │ 命中30 ✓
L0:  HEAD ─► 10 ──► 20 ─► 25 ─► 30 ─► 40 ─► 50 ─► NULL
```

**查找路径**：从最高层起，向右直到下一个节点大于目标，下降一层，重复。最终在 L0 命中。

**2. 插入过程**

1. 查找插入位置，记录每层的前驱节点
2. 在 L0 插入新节点
3. **随机决定层数**：抛硬币，p=0.5 升一层，最多 32 层（Redis ZSKIPLIST_MAXLEVEL）
4. 在升层的层级插入索引节点

```c
// Redis 跳表层数生成
int randomLevel() {
    int level = 1;
    while (random() & 0xFFFF) < (0.5 * 0xFFFF))  // p=0.5
        level++;
    return min(level, 32);
}
```

**3. 复杂度对比**

| 操作 | 跳表 | 红黑树 | 哈希表 |
| --- | --- | --- | --- |
| 单点查找 | O(logN) | O(logN) | O(1) |
| 范围查询 | O(logN + M) | O(logN + M) | ❌ 不支持 |
| 插入 | O(logN) | O(logN) | O(1) |
| 删除 | O(logN) | O(logN) | O(1) |
| 实现复杂度 | 简单 | 复杂（旋转、变色） | 简单 |
| 内存 | 多一倍指针 | 三指针+颜色位 | 最少 |

**4. 跳表相比红黑树的优势（Redis 选择跳表的原因）**

1. **范围查询高效**：ZSet 的 `ZRANGE`、`ZRANGEBYSCORE` 等命令高频，跳表底层是链表，找到起点后顺序遍历即可；红黑树需中序遍历，实现复杂
2. **实现简单**：跳表代码约 200 行，红黑树需处理多种旋转/变色情况，易出错
3. **并发友好**：跳表局部加锁即可（链表节点独立），红黑树旋转影响多个节点
4. **内存可调**：通过调整 p 值控制索引密度，平衡内存与速度
5. **缓存友好**：链表节点连续分配（Redis 用数组优化），比树节点分散好

**5. Redis 跳表细节**

```c
typedef struct zskiplistNode {
    sds ele;                       // 元素值
    double score;                  // 分数
    struct zskiplistNode *backward;// 后退指针（便于反向遍历 ZREVRANGE）
    struct zskiplistLevel {
        struct zskiplistNode *forward;  // 前进指针
        unsigned long span;             // 跨度（用于 ZRANK 计算）
    } level[];                     // 柔性数组，层数动态
} zskiplistNode;
```

**span（跨度）的作用**：记录节点在该层到下一节点的距离，累加即可得到排名，`ZRANK` 命令 O(logN)。

**实际案例**：
- **项目背景**：游戏排行榜，1 亿玩家，需实时 Top 100 与个人排名
- **方案**：Redis ZSet 存 score，利用跳表 O(logN) 查找 + span 算排名
- **效果**：`ZRANK` 与 `ZREVRANGE` 均在 1ms 内，扛住 5 万 QPS

**评分要点**：
- ✅ 跳表多层链表结构（必备）
- ✅ 查找/插入过程（必备）
- ✅ 随机层数生成（加分）
- ✅ 范围查询高效是选跳表主因（核心）
- ✅ span 实现排名（加分）

---

## 第二篇 持久化机制

### Q2.1 RDB 与 AOF 各自的原理与优缺点？如何选择？

**问题描述**：请对比 RDB 和 AOF 持久化机制，并说明选型策略。

**参考答案**：

**1. RDB（Redis Database）**

- **原理**：在某个时间点，将内存中所有数据生成快照，写入磁盘 `dump.rdb`
- **触发方式**：
  - `SAVE`：阻塞主线程，期间无法处理命令（生产禁用）
  - `BGSAVE`：fork 子进程，子进程写 RDB，主线程继续服务
  - 配置自动触发：`save 900 1`（900s 内 1 次修改触发）

```conf
# redis.conf
save 900 1      # 900秒内1次修改
save 300 10     # 300秒内10次修改
save 60 10000   # 60秒内10000次修改
stop-writes-on-bgsave-error yes
rdbcompression yes
dbfilename dump.rdb
```

**2. AOF（Append Only File）**

- **原理**：将每条写命令追加到 `appendonly.aof`，重启时重放命令恢复数据
- **三种刷盘策略**：

| 策略 | 配置 | 性能 | 数据安全 |
| --- | --- | --- | --- |
| `always` | 每条命令都 fsync | 最差 | 最安全（不丢） |
| `everysec` | 每秒 fsync 一次（默认） | 较好 | 最多丢 1 秒 |
| `no` | 由 OS 决定 fsync | 最好 | 丢数据风险大 |

```conf
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
```

**3. 对比**

| 维度 | RDB | AOF |
| --- | --- | --- |
| **数据安全** | 可能丢最近一次快照后数据 | everysec 最多丢 1 秒 |
| **文件大小** | 小（二进制压缩） | 大（文本命令，重写后会小） |
| **恢复速度** | 快（直接加载二进制） | 慢（重放所有命令） |
| **性能影响** | fork 时内存翻倍（COW） | 每条写命令追加文件，IO 多 |
| **可读性** | 不可读 | 可读（文本命令） |
| **适用场景** | 备份、容灾、允许少量丢失 | 数据安全要求高 |

**4. AOF 重写（Rewrite）**

AOF 文件越来越大，重写机制扫描内存，生成最小命令集：

```
原始 AOF：
SET k1 v1
SET k1 v2
SET k1 v3       ← 重写后只保留最后状态
LPUSH list a
LPUSH list b
LPUSH list c    ← 重写后：LPUSH list a b c 或 RPUSH list c b a
```

触发方式：
- 手动：`BGREWRITEAOF`
- 自动：`auto-aof-rewrite-percentage 100`（文件大小翻倍触发）
- `auto-aof-rewrite-min-size 64mb`（最小触发大小）

**5. Redis 4.0 混合持久化（推荐）**

```conf
aof-use-rdb-preamble yes  # 4.0+ 默认开启
```

AOF 重写时，**前半部分写 RDB 二进制（基础数据），后半部分写 AOF 命令（增量）**：

```
AOF 文件结构：
┌──────────────────┬──────────────────────┐
│  RDB 二进制快照   │  AOF 增量命令         │
│（重写时内存全量） │（重写后到宕机间的命令）│
└──────────────────┴──────────────────────┘
```

- **恢复快**：前半 RDB 加载快
- **数据全**：后半 AOF 补全增量
- **兼顾 RDB 速度与 AOF 安全**

**6. fork 的 COW（Copy-On-Write）机制**

`BGSAVE`/`BGREWRITEAOF` 时 fork 子进程：

- fork 瞬间：子进程与父进程共享同一份物理内存，仅复制页表（开销小）
- 父进程写入某页：OS 才复制该页给子进程，父进程写新页
- **风险**：若 fork 后父进程大量写操作，会触发大量 COW，内存可能翻倍

```
fork 前内存 8G：
┌─────────────────────────┐
│  父进程数据 8G           │
└─────────────────────────┘

fork 后（共享物理页）：
┌─────────────────────────┐
│  父进程    子进程         │
│  指向同 ──► 物理内存 8G  │
└─────────────────────────┘

父进程写入 page A：
┌─────────────────────────┐
│  父进程 8G + 新 page A   │ ← COW 复制 page A
│  子进程 8G（含旧 page A）│
└─────────────────────────┘
```

**防范**：`vm.overcommit_memory=1`，避免 fork 因内存不足失败。

**实际案例**：
- **项目背景**：电商缓存集群 32G 内存，AOF always 模式，QPS 2 万，写延迟 8ms
- **问题**：每次写都 fsync，磁盘成为瓶颈
- **优化**：改为 everysec + 4.0 混合持久化
- **效果**：写延迟降到 0.5ms，最多丢 1 秒数据，业务可接受

**评分要点**：
- ✅ RDB/AOF 原理与触发方式（必备）
- ✅ 三种 fsync 策略对比（必备）
- ✅ AOF 重写机制（必备）
- ✅ 4.0 混合持久化（核心）
- ✅ fork COW 机制与风险（加分）

---

### Q2.2 AOF 重写过程中有新写命令怎么办？fork 子进程如何保证数据一致？

**问题描述**：AOF 重写是耗时的，重写期间若有新命令写入，如何保证不丢失？

**参考答案**：

**1. AOF 重写全流程**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 主进程 fork 子进程                                       │
│    └─ 子进程开始扫描内存，生成新 AOF                        │
├─────────────────────────────────────────────────────────────┤
│ 2. 重写期间，主进程继续处理命令                             │
│    ├─ 命令正常执行                                          │
│    └─ 命令同时写入「AOF 重写缓冲区」（aof_rewrite_buf）     │
├─────────────────────────────────────────────────────────────┤
│ 3. 子进程完成新 AOF 生成，信号通知主进程                    │
├─────────────────────────────────────────────────────────────┤
│ 4. 主进程：                                                 │
│    ├─ 将 aof_rewrite_buf 中的命令追加到新 AOF               │
│    ├─ 原子替换旧 AOF 文件（rename）                         │
│    └─ 关闭旧 AOF                                            │
└─────────────────────────────────────────────────────────────┘
```

**2. 关键机制：AOF 重写缓冲区**

- 子进程 fork 时，已拥有当时内存的快照（COW 保证数据一致）
- 主进程在重写期间的**新写命令**会同时写入：
  - **旧 AOF 缓冲区**（保证旧 AOF 仍完整）
  - **AOF 重写缓冲区**（待子进程完成后追加到新 AOF）
- 子进程完成后，主进程将重写缓冲区内容追加到新 AOF，再原子替换

**3. 为什么子进程看到的是 fork 时的数据**

- fork 时子进程获得父进程内存的副本（COW）
- 子进程扫描的是 fork 瞬间的内存快照
- 即使父进程修改了原内存，子进程的副本不变（COW 保护）

**4. 重写期间的内存风险**

- AOF 重写缓冲区是**额外内存**，若重写期间写命令多，缓冲区可能很大
- 监控指标：`aof_rewrite_buffer_length`（重写缓冲区大小）
- **风险**：内存碎片率上升，甚至触发 OOM

**防范**：
- 在低峰期触发重写
- 限制重写缓冲区大小（业务控制写量）
- 保证机器有足够冗余内存（至少 50% 空闲）

**5. 重写失败的处理**

- 子进程崩溃：主进程收到信号，本次重写失败，旧 AOF 不受影响
- 主进程在追加重写缓冲区时崩溃：新 AOF 不完整，但旧 AOF 完好，重启后用旧 AOF 恢复
- `aof-load-truncated yes`：加载截断的 AOF 时自动修复

**实际案例**：
- **项目背景**：大促期间 AOF 重写触发，重写缓冲区涨到 2G，内存触顶
- **根因**：大促写量暴增，重写缓冲区累积过多
- **解决**：避开大促期，定时低峰手动 `BGREWRITEAOF`；机器扩容预留 50% 内存
- **效果**：重写平稳，无 OOM

**评分要点**：
- ✅ AOF 重写缓冲区机制（必备）
- ✅ fork COW 保证子进程数据一致（核心）
- ✅ 重写完成后的原子替换流程（必备）
- ✅ 重写缓冲区内存风险（加分）

---

## 第三篇 内存管理与淘汰策略

### Q3.1 Redis 的 8 种内存淘汰策略是什么？如何选择？

**问题描述**：请列举 Redis 的内存淘汰策略，并说明选型依据。

**参考答案**：

**1. 8 种淘汰策略**

| 策略 | 说明 | 适用场景 |
| --- | --- | --- |
| `noeviction` | 不淘汰，写入报错（默认） | 数据不能丢失，如锁、计数器 |
| `volatile-lru` | 在设过期键中，淘汰最久未使用 | 缓存场景，热数据保留 |
| `volatile-lfu` | 在设过期键中，淘汰最少使用（4.0+） | 缓存场景，访问频率优先 |
| `volatile-ttl` | 在设过期键中，淘汰 TTL 最短 | 优先淘汰快过期的 |
| `volatile-random` | 在设过期键中，随机淘汰 | 简单场景 |
| `allkeys-lru` | 在所有键中，淘汰最久未使用 | 纯缓存场景，推荐 |
| `allkeys-lfu` | 在所有键中，淘汰最少使用（4.0+） | 纯缓存，访问频率优先 |
| `allkeys-random` | 在所有键中，随机淘汰 | 无访问模式 |

**2. LRU 实现（近似 LRU）**

Redis 不维护全局链表（内存开销大），而是**采样近似 LRU**：

```conf
maxmemory-policy allkeys-lru
maxmemory-samples 5  # 随机采样 5 个，淘汰最久未用的
```

- 采样数越大越精确，但开销越大
- 5 是平衡点，效果接近真实 LRU
- Redis 3.0+ 引入**淘汰池**（eviction pool）：维护一个待淘汰候选池，提升精度

**3. LFU 实现（频率统计）**

4.0 引入 LFU（Least Frequently Used），基于访问频率：

```conf
maxmemory-policy allkeys-lfu
lfu-log-factor 10   # 越大越接近真实频率（计数器衰减慢）
lfu-decay-time 1    # 衰减周期（分钟）
```

- 用 **8 位计数器**（最大 255）+ 衰减机制，避免老热点永不淘汰
- 对比 LRU：LRU 防止偶发访问污染，LFU 防止扫描型访问污染

**4. 选择建议**

| 业务场景 | 推荐策略 | 原因 |
| --- | --- | --- |
| **纯缓存**（如商品页缓存） | `allkeys-lru` 或 `allkeys-lfu` | 缓存可全淘汰，保留热数据 |
| **混合存储**（缓存+持久数据） | `volatile-lru` | 仅淘汰设过期的，持久数据保留 |
| **数据不能丢**（如分布式锁） | `noeviction` | 不淘汰，写满报错人工介入 |
| **热点明显** | `allkeys-lfu` | 按频率保留热点 |
| **TTL 差异大** | `volatile-ttl` | 优先淘汰快过期的 |

**5. 配置与监控**

```conf
maxmemory 4gb                # 内存上限
maxmemory-policy allkeys-lru # 淘汰策略
```

```bash
# 监控淘汰情况
INFO memory
# evicted_keys: 12345       # 累计淘汰的 key 数
# mem_fragmentation_ratio   # 内存碎片率
```

**实际案例**：
- **项目背景**：商品详情缓存，5G 数据，内存 4G，原 `noeviction` 导致写满报错
- **问题**：高峰期缓存命中率从 95% 降到 60%
- **优化**：改为 `allkeys-lru`，`maxmemory-samples 10`
- **效果**：命中率回到 92%，淘汰的均为冷数据

**评分要点**：
- ✅ 8 种策略列举（必备）
- ✅ 近似 LRU 采样机制（核心）
- ✅ LFU 频率衰减（加分）
- ✅ 业务场景选型（必备）

---

### Q3.2 Redis 的过期键删除策略是什么？内存淘汰与过期删除有何区别？

**问题描述**：请说明 Redis 如何处理过期键，与内存淘汰策略的区别。

**参考答案**：

**1. Redis 过期键删除：惰性 + 定期**

**惰性删除**：
- 访问 key 时检查是否过期，过期则删除
- **优点**：CPU 友好，不主动扫描
- **缺点**：过期 key 长期不访问会一直占用内存

**定期删除**：
- 默认每秒 10 次（`hz 10`）扫描设过期键的字典
- 每次随机抽取 20 个 key，删除已过期的
- 若过期比例 > 25%，继续扫描；否则本次结束
- **优点**：防止过期 key 堆积
- **缺点**：可能漏掉部分过期 key

**2. 两者结合的必要性**

```
┌──────────────────────────────────────────┐
│  写入 key 并设过期时间                    │
│      │                                    │
│      ▼                                    │
│  ┌─ 惰性删除：访问时检查 ─┐               │
│  │                       │ ← 兜底         │
│  └─ 定期删除：后台扫描 ──┘               │
│      │                                    │
│      ▼                                    │
│  仍残留过期 key（内存仍占用）             │
│      │                                    │
│      ▼                                    │
│  内存达 maxmemory → 内存淘汰策略触发      │
└──────────────────────────────────────────┘
```

**3. 过期删除 vs 内存淘汰**

| 维度 | 过期删除 | 内存淘汰 |
| --- | --- | --- |
| **触发时机** | key 过期时（访问或扫描） | 内存达 `maxmemory` 上限时 |
| **作用对象** | 仅设过期的 key | 所有 key（或设过期的，看策略） |
| **目的** | 清理已过期数据 | 释放内存供新数据写入 |
| **配置** | `hz` | `maxmemory-policy` |

**4. 从库的过期键处理**

- 主库删除过期 key 后，向从库发 DEL 命令
- 从库**不会主动删除**过期 key，等主库命令
- 从库读过期 key 仍返回数据（4.0+ 可设不返回）

**5. 内存碎片优化**

```bash
INFO memory
# mem_fragmentation_ratio: 1.5  ← 碎片率，>1.5 需处理
# used_memory: 2gb
# used_memory_rss: 3gb          ← OS 分配的物理内存（含碎片）
```

碎片来源：
- 频繁修改/删除导致 allocator 无法回收
- jemalloc 分配对齐造成内部碎片

优化方式：

```conf
# 4.0+ 自动碎片整理
activedefrag yes
active-defrag-ignore-bytes 100mb      # 碎片超 100MB 触发
active-defrag-threshold-lower 10      # 碎片率超 10% 触发
active-defrag-cycle-min 1             # 最小 CPU 占比
active-defrag-cycle-max 25            # 最大 CPU 占比
```

或重启 Redis 让内存重新紧凑分配。

**实际案例**：
- **项目背景**：Redis 内存 8G，used_memory 4G，rss 7G，碎片率 1.75
- **问题**：实际数据只占一半，但内存快满
- **优化**：开启 `activedefrag`，碎片率降到 1.1，rss 降到 4.5G
- **效果**：释放 2.5G 内存，可承载更多数据

**评分要点**：
- ✅ 惰性 + 定期删除组合（必备）
- ✅ 定期删除扫描规则（加分）
- ✅ 过期删除 vs 内存淘汰区别（必备）
- ✅ 内存碎片优化（加分）

---

## 第四篇 高可用方案

### Q4.1 Redis 主从复制的原理是什么？全量复制与增量复制的触发条件？

**问题描述**：请详细说明 Redis 主从复制的流程，包括全量复制与增量复制。

**参考答案**：

**1. 主从复制总体流程**

```
┌─────────┐  SYNC/PSYNC   ┌─────────┐
│  Slave  │ ────────────► │  Master │
│         │ ◄───────────  │         │
│         │  1. RDB 快照   │         │
│         │  2. 增量命令   │         │
└─────────┘                └─────────┘
```

**2. 全量复制（Full Resync）**

触发场景：从库首次连接、从库断线太久（offset 失效）

流程：
1. 从库发送 `PSYNC ? -1`（首次）或 `PSYNC <runid> <offset>`
2. 主库判断需要全量复制，返回 `+FULLRESYNC <runid> <offset>`
3. 主库 `BGSAVE` 生成 RDB，期间新写命令存入**复制缓冲区**
4. 主库发送 RDB 给从库
5. 从库加载 RDB
6. 主库发送缓冲区中的增量命令
7. 之后进入增量复制阶段

```
Slave                  Master
  │                       │
  │── PSYNC ? -1 ────────►│
  │                       │── BGSAVE 生成 RDB
  │                       │── 写命令存入复制缓冲区
  │◄── +FULLRESYNC ───────│
  │                       │
  │◄── RDB 数据 ──────────│
  │── 加载 RDB             │
  │                       │
  │◄── 缓冲区增量命令 ─────│
  │── 执行增量命令          │
  │                       │
  │── 进入增量复制 ────────►│
```

**3. 增量复制（Partial Resync）**

触发场景：从库断线后重连，且 offset 仍在主库复制缓冲区内

流程：
1. 从库发送 `PSYNC <runid> <offset>`
2. 主库检查：
   - runid 匹配？offset 在 `repl_backlog` 内？
3. 若都满足，发送 offset 之后的命令
4. 若不满足，退化为全量复制

**4. 复制积压缓冲区（repl_backlog）**

```conf
repl-backlog-size 1mb       # 缓冲区大小，默认 1MB
repl-backlog-ttl 3600       # 缓冲区保留时长（无从库时）
```

- 主库维护一个**环形缓冲区**，存最近写命令
- 从库断线重连时，若 offset 在缓冲区内可增量复制
- **缓冲区大小估算**：`每秒写入量 × 断线时长 × 2`

```
计算示例：
- 每秒写入 1000 命令，平均每命令 100 字节 → 100KB/s
- 预计断线最长 30 秒
- 缓冲区大小 = 100KB × 30 × 2 = 6MB
```

**5. 主从复制风险**

| 风险 | 说明 | 防范 |
| --- | --- | --- |
| **全量复制阻塞主库** | BGSAVE + 发送 RDB 占用主库网络与 CPU | 避免频繁全量复制，调大 backlog |
| **复制风暴** | 多从库同时全量复制，主库被打垮 | 从库层级化（树形复制） |
| **数据延迟** | 异步复制，从库有延迟 | 强一致读走主库 |
| **脑裂** | 主库假死，哨兵切主，原主库仍有写入 | 配置 min-slaves-to-write |

**6. 树形复制（级联复制）**

```
Master ───► Slave1 ───► Slave2
        └──► Slave3 ───► Slave4
                     └──► Slave5
```

- Slave1 既是从库也是其他从库的主库
- 减轻 Master 复制压力

**实际案例**：
- **项目背景**：1 主 5 从，slave 全量复制时 master CPU 100% 影响业务
- **优化**：改为树形复制，master 只复制给 2 个 slave，其他 slave 从这 2 个复制
- **效果**：master CPU 降到 40%，全量复制对业务零影响

**评分要点**：
- ✅ 全量复制流程（必备）
- ✅ PSYNC 命令与 runid/offset（必备）
- ✅ 增量复制触发条件（核心）
- ✅ repl_backlog 大小估算（加分）
- ✅ 树形复制（加分）

---

### Q4.2 哨兵（Sentinel）的工作原理？如何实现自动故障转移？

**问题描述**：请说明 Sentinel 的监控、故障判定、 leader 选举与故障转移流程。

**参考答案**：

**1. Sentinel 架构**

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Sentinel1  │  │ Sentinel2  │  │ Sentinel3  │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └──── 监控 ─────┬┴────────────────┘
                     ┌─┴──────┐
                     │ Master │
                     └─┬──────┘
                ┌──────┴──────┐
            ┌───┴───┐    ┌────┴───┐
            │Slave1 │    │Slave2  │
            └───────┘    └────────┘
```

**2. 三类监控任务**

| 任务 | 频率 | 内容 |
| --- | --- | --- |
| **PING 主从** | 每秒 | 检查主从库存活（INFO 命令） |
| **INFO 主从** | 每 10 秒 | 获取从库信息，更新拓扑 |
| **Pub/Sub 发布** | 每 2 秒 | 在 `__sentinel__:hello` 频道发布自身信息 |
| **INFO 其他 Sentinel** | 每 2 秒 | 通过订阅频道发现其他 Sentinel |

**3. 故障判定（主观下线 → 客观下线）**

**主观下线（Subjectively Down, SDOWN）**：
- Sentinel 对某节点 `down-after-milliseconds`（默认 30 秒）无响应
- 标记为 SDOWN（仅本 Sentinel 判定）

**客观下线（Objectively Down, ODOWN）**：
- 多数 Sentinel（quorum）都判定 SDOWN
- 标记为 ODOWN，准备故障转移

```conf
sentinel monitor mymaster 192.168.1.10 6379 2   # quorum=2
sentinel down-after-milliseconds mymaster 30000 # 30s 无响应判主观下线
```

**4. Leader 选举（Raft 算法）**

- 客观下线后，Sentinel 之间选 Leader 主持故障转移
- 每个 Sentinel 候选，获得多数票（N/2+1）成为 Leader
- Leader 负责选新主、通知其他从库

**5. 故障转移流程**

```
1. 选新主
   ├─ 排除故障从库
   ├─ 按优先级（slave-priority）选，高的优先
   ├─ 优先级相同，选 offset 最大的（数据最新）
   └─ offset 相同，选 runid 最小的（确定性）

2. 提升新主
   ├─ Leader 向候选从库发 SLAVEOF NO ONE
   └─ 从库变为主库

3. 通知其他从库
   ├─ Leader 向其他从库发 SLAVEOF <新主IP> <端口>
   └─ 从库同步新主数据

4. 通知客户端
   ├─ Sentinel 通过 Pub/Sub 通知客户端新主地址
   └─ 客户端感知并切换连接

5. 旧主恢复后
   └─ 旧主作为从库加入集群（配置更新）
```

**6. 脑裂问题与防范**

**脑裂场景**：主库与 Sentinel 网络分区，Sentinel 误判主库下线选新主，原主库仍接受写入 → 数据丢失

**防范**：

```conf
min-slaves-to-write 1     # 至少 1 个从库同步成功才允许写
min-slaves-max-lag 10     # 从库延迟不超过 10 秒
```

主库若与所有从库失联，则拒绝写入，避免脑裂数据丢失。

**7. 客户端故障感知**

```java
// Jedis Sentinel 配置
Set<String> sentinels = new HashSet<>();
sentinels.add("192.168.1.20:26379");
sentinels.add("192.168.1.21:26379");
sentinels.add("192.168.1.22:26379");

JedisSentinelPool pool = new JedisSentinelPool("mymaster", sentinels);
// 内部自动订阅 Sentinel 频道，故障转移后自动切换连接
```

**实际案例**：
- **项目背景**：1 主 2 从 + 3 Sentinel，主库宕机后业务中断 5 分钟
- **问题**：原配置 down-after 60s + 客户端未订阅 Sentinel 通知
- **优化**：down-after 调到 10s，客户端用 JedisSentinelPool 自动切换
- **效果**：故障自动恢复，业务感知 < 30s

**评分要点**：
- ✅ 主观/客观下线区别（必备）
- ✅ quorum 与多数派（必备）
- ✅ Leader 选举 Raft（加分）
- ✅ 选新主规则（优先级→offset→runid）（必备）
- ✅ 脑裂防范 min-slaves-to-write（核心）

---

### Q4.3 Redis Cluster 的原理？数据如何分片？客户端如何路由？

**问题描述**：请说明 Redis Cluster 的槽位分片、节点通信、路由机制与扩缩容。

**参考答案**：

**1. Cluster 架构**

```
┌─────────────────────────────────────────────────────────────┐
│                    Redis Cluster                            │
├─────────────────────────────────────────────────────────────┤
│  节点 A（Master）      节点 B（Master）      节点 C（Master）│
│  槽 0-5461           槽 5462-10922          槽 10923-16383   │
│  Slave A1            Slave B1               Slave C1         │
└─────────────────────────────────────────────────────────────┘
```

- **16384 个槽**（slot），分布在所有 Master 节点
- **CRC16 算法**：`slot = CRC16(key) mod 16384`
- 每个节点负责一部分槽，Master 写、Slave 备份

**2. 为什么是 16384 个槽**

- Redis 作者 antirez 解释：
  - 心跳报文大小：每个槽 1 bit，16384 槽 = 2KB，可控
  - 集群规模：建议 ≤1000 节点，16384 槽足够划分
  - 65536 槽报文 8KB，过大

**3. 节点通信（Gossip 协议）**

- 每个节点每秒向 5 个随机节点发 PING
- PING/PONG 消息包含：自身状态 + 已知部分节点信息
- **去中心化**：无中心节点，信息逐步扩散
- 心跳报文含槽位图，便于感知集群拓扑

**4. 客户端路由**

```
客户端 SET k1 v1
  │
  ▼
1. 计算 slot = CRC16("k1") mod 16384 = 1234
2. 查本地槽位映射表，slot 1234 在节点 A
3. 向节点 A 发送命令
   │
   ├─ 若 k1 在 A：直接返回结果 ✓
   │
   └─ 若 k1 不在 A（迁移中）：
      A 返回 MOVED 错误：MOVED <slot> <ip:port>
      客户端更新本地映射表，重定向到正确节点
```

**MOVED 重定向**：

```
客户端 ──SET k1──► 节点 A
节点 A ──MOVED 1234 192.168.1.11:6379──► 客户端
客户端 ──SET k1──► 节点 B（正确节点）
```

**ASK 重定向**（槽迁移中）：

```
客户端 ──SET k1──► 节点 A（迁移中）
节点 A ──ASK 1234 192.168.1.11:6379──► 客户端
客户端 ──ASKING + SET k1──► 节点 B（临时询问，不更新映射）
```

- MOVED：永久重定向，更新本地映射
- ASK：临时重定向，不更新映射（迁移完成后自然消失）

**5. 槽迁移流程**

```
源节点 A                  目标节点 B
  │                          │
  │ 1. CLUSTER SETSLOT n IMPORTING B
  │ 2. CLUSTER SETSLOT n MIGRATING A
  │                          │
  │ 3. 迁移 key（逐个 MIGRATE）
  │    ├─ key 在 A：MIGRATE 到 B
  │    └─ key 不在 A：ASK 重定向
  │                          │
  │ 4. 迁移完成，通知集群
  │    CLUSTER SETSLOT n NODE B
  │                          │
  │ 5. 集群广播，更新槽映射
```

**6. 故障转移**

- 节点间 Gossip 检测，某 Master 下线
- 集群半数以上 Master 确认 → 标记客观下线
- 该 Master 的 Slave 发起选举（Raft）
- 选举胜出的 Slave 升级为新 Master，接管槽
- 集群广播新拓扑

**7. 集群限制**

| 限制 | 说明 |
| --- | --- |
| **只支持 0 号库** | Cluster 模式禁用 SELECT 0 以外的库 |
| **multi-key 限制** | 不同 key 必须在同一槽，否则报错 |
| **事务限制** | multi key 事务需同槽 |
| **客户端需支持 Cluster 协议** | 如 JedisCluster、Lettuce |

**multi-key 解决方案：用 hash tag**

```
# 用 {} 包裹部分 key，CRC16 只算 {} 内部分
SET {user:1000}:name "tom"
SET {user:1000}:age 20
# 两个 key 的 slot = CRC16("user:1000") mod 16384，相同槽
```

**8. 扩容流程**

```
1. 准备新节点（启动 Redis，CLUSTER MEET 加入集群）
2. 迁移部分槽到新节点（CLUSTER SETSLOT）
3. 逐 key MIGRATE
4. 更新槽映射
```

**实际案例**：
- **项目背景**：单机 Redis 50G 内存，QPS 8 万，CPU 接近上限
- **方案**：搭建 6 节点 Cluster（3 主 3 从），按 user_id hash 分片
- **挑战**：原 multi-key 操作报错，用 hash tag 改造
- **效果**：单节点 QPS 降到 1.5 万，内存 9G/节点，可水平扩展

**评分要点**：
- ✅ 16384 槽 + CRC16（必备）
- ✅ Gossip 协议通信（必备）
- ✅ MOVED vs ASK 区别（核心）
- ✅ hash tag 解决 multi-key（必备）
- ✅ 槽迁移流程（加分）

---

## 第五篇 缓存问题与解决方案

### Q5.1 什么是缓存穿透、缓存击穿、缓存雪崩？分别如何解决？

**问题描述**：请说明这三大经典缓存问题的成因与解决方案。

**参考答案**：

**1. 缓存穿透（Penetration）**

**定义**：查询**根本不存在**的数据，缓存和 DB 都没有，每次都打到 DB。

```
客户端 ──查询 id=-1──► 缓存（无）──► DB（无）──► 返回空
       ↑                                          │
       └──────── 反复查询，DB 压力大 ─────────────┘
```

**成因**：
- 恶意攻击（查询不存在的 ID）
- 业务 bug（参数错误）

**解决方案**：

| 方案 | 实现 | 优缺点 |
| --- | --- | --- |
| **缓存空值** | DB 查不到也缓存 `null`，设短过期 | 简单；但占内存、可能数据不一致 |
| **布隆过滤器** | 缓存前置布隆过滤器，过滤不存在 key | 内存高效；有误判率（假阳性） |
| **接口校验** | 参数合法性校验（ID>0） | 治标；无法防恶意 |

**布隆过滤器示例**：

```java
// 用 Redisson 布隆过滤器
RBloomFilter<Long> bloomFilter = redisson.getBloomFilter("user:exist");
bloomFilter.tryInit(100_000_00L, 0.01);  // 1亿容量，1% 误判

// 数据预热
for (Long userId : allUserIds) {
    bloomFilter.add(userId);
}

// 查询时先过滤
public User getUser(Long id) {
    if (!bloomFilter.contains(id)) {
        return null;  // 一定不存在，直接返回
    }
    // 走正常缓存逻辑
}
```

**2. 缓存击穿（Breakdown）**

**定义**：**热点 key** 过期瞬间，大量并发请求同时打到 DB。

```
热点 key 过期 ──► 1000 并发请求 ──► 同时查 DB ──► DB 瞬间压力骤增
```

**成因**：热点数据缓存过期，恰逢高并发访问。

**解决方案**：

| 方案 | 实现 | 优缺点 |
| --- | --- | --- |
| **互斥锁** | 只让一个请求查 DB，其他等待 | 简单可靠；但有等待延迟 |
| **逻辑过期** | 缓存不设过期，存逻辑过期时间，过期后台异步刷新 | 无阻塞；短暂数据不一致 |
| **热点预检** | 提前刷新热点 key | 主动；需识别热点 |

**互斥锁实现**：

```java
public String getWithMutex(String key) {
    String value = redis.get(key);
    if (value == null) {
        // 加互斥锁
        if (redis.setnx("lock:" + key, "1", 10, SECONDS)) {
            try {
                value = redis.get(key);  // 双重检查
                if (value == null) {
                    value = db.query(key);
                    redis.set(key, value, 3600, SECONDS);
                }
            } finally {
                redis.del("lock:" + key);
            }
        } else {
            Thread.sleep(50);
            return getWithMutex(key);  // 重试
        }
    }
    return value;
}
```

**逻辑过期实现**：

```java
// 缓存对象包含逻辑过期时间
class CacheData {
    String data;
    long expireTime;  // 逻辑过期时间
}

public String getWithLogicalExpire(String key) {
    CacheData cache = redis.get(key);
    if (cache == null) return null;  // 不缓存 null
    
    if (cache.expireTime > System.currentTimeMillis()) {
        return cache.data;  // 未过期，直接返回
    }
    
    // 逻辑过期，尝试加锁异步刷新
    if (redis.setnx("lock:" + key, "1", 10, SECONDS)) {
        executor.submit(() -> {
            try {
                String fresh = db.query(key);
                CacheData newData = new CacheData(fresh, 
                    System.currentTimeMillis() + 3600_000);
                redis.set(key, newData);
            } finally {
                redis.del("lock:" + key);
            }
        });
    }
    return cache.data;  // 返回旧数据，不阻塞
}
```

**3. 缓存雪崩（Avalanche）**

**定义**：**大量 key 同时过期**，或 Redis 宕机，请求全打到 DB。

```
大量 key 同时过期 ──► 缓存集体失效 ──► DB 瞬间压力暴增 ──► DB 宕机 ──► 服务雪崩
```

**成因**：
- 大批量 key 设相同过期时间
- Redis 宕机

**解决方案**：

| 场景 | 方案 |
| --- | --- |
| **大量 key 同时过期** | 过期时间加随机数：`expire = base + random(0, 300s)` |
| **Redis 宕机** | 集群高可用（主从+哨兵/Cluster） |
| **DB 雪崩兜底** | 熔断降级（Hystrix/Sentinel），限制 DB 访问 |
| **缓存预热** | 系统启动时预先加载热点数据 |

**过期时间加随机数**：

```java
// 基础过期 1 小时 + 随机 0-10 分钟
int expire = 3600 + ThreadLocalRandom.current().nextInt(600);
redis.setex(key, expire, value);
```

**4. 三者对比**

| 问题 | 本质 | 触发 | 解决核心 |
| --- | --- | --- | --- |
| 穿透 | 查不存在的数据 | 恶意/bug | 布隆过滤器 + 缓存空值 |
| 击穿 | 热点 key 过期 | 热点高并发 | 互斥锁 + 逻辑过期 |
| 雪崩 | 大量 key 过期 | 过期时间集中 | 随机过期 + 高可用 |

**实际案例**：
- **项目背景**：电商首页商品缓存，大促前预热 10 万商品，过期时间统一 1 小时
- **问题**：上线后 1 小时整点所有缓存同时过期，DB QPS 从 1 万飙到 20 万
- **优化**：过期时间改为 `3600 + random(0, 600)`，错峰过期；同时加互斥锁防击穿
- **效果**：DB QPS 平稳，峰值 2 万

**评分要点**：
- ✅ 三者定义与区别（必备）
- ✅ 布隆过滤器原理（必备）
- ✅ 互斥锁/逻辑过期实现（核心）
- ✅ 过期时间加随机数（必备）
- ✅ 实际案例与数据（加分）

---

### Q5.2 缓存与数据库如何保证一致性？有哪些方案？

**问题描述**：请说明缓存与 DB 一致性的各种方案及权衡。

**参考答案**：

**1. 一致性策略对比**

| 方案 | 写顺序 | 一致性 | 复杂度 |
| --- | --- | --- | --- |
| **Cache Aside（旁路缓存）** | 先更新 DB，再删缓存 | 最终一致 | 低 |
| **Read/Write Through** | 应用只操作缓存，缓存同步写 DB | 强 | 高 |
| **Write Behind** | 应用只写缓存，异步刷 DB | 弱 | 中 |
| **双删延迟** | 先删缓存→更新 DB→延迟再删缓存 | 较高 | 中 |

**2. Cache Aside（最常用）**

```
读：先查缓存，命中返回；未命中查 DB，写入缓存
写：先更新 DB，再删除缓存（注意是删，不是更新）
```

**为什么删而非更新缓存**：
- 避免并发更新顺序错乱（A 先更新，B 后更新，但缓存 B 先写 A 后写 → 数据错）
- 删除是幂等的，更新不是
- 懒加载：下次读时再回种缓存，避免无效写

**3. 先更新 DB 再删缓存的问题**

**异常场景 1：删缓存失败**
- DB 已更新，缓存还是旧值
- 数据不一致直到缓存过期

**异常场景 2：并发读写**

```
线程 A（写）        线程 B（读）
                    1. 读缓存（未命中）
                    2. 读 DB（旧值）
1. 更新 DB（新值）
2. 删缓存
                    3. 写入缓存（旧值）  ← 缓存存了旧值
```

此场景发生概率极低（需读线程先读 DB、写线程再完成更新删缓存、读线程最后回种），但理论存在。

**4. 延迟双删策略**

```
1. 删除缓存
2. 更新 DB
3. 延迟 N 秒（如 1 秒）
4. 再次删除缓存
```

```java
public void updateData(Long id, Data data) {
    redis.del("data:" + id);                  // 第一次删
    db.update(id, data);                       // 更新 DB
    executor.schedule(() -> {
        redis.del("data:" + id);              // 延迟第二次删
    }, 1, TimeUnit.SECONDS);
}
```

延迟时间需覆盖读线程的"读 DB + 写缓存"耗时。

**5. 基于 binlog 异步同步**

用 Canal 监听 MySQL binlog，异步更新缓存，解耦业务代码：

```
应用 ──更新 DB──► MySQL ──binlog──► Canal ──► 消费程序 ──► 删除/更新缓存
```

**优点**：
- 业务代码无需关心缓存
- binlog 顺序保证，避免并发问题
- 失败可重试

**缺点**：
- 引入额外组件
- 有延迟（毫秒级）

**6. 强一致性方案**

若业务要求强一致（如金融）：

| 方案 | 实现 |
| --- | --- |
| **分布式锁** | 读写都加锁，串行化 |
| **Read Through + 写锁** | 读加共享锁，写加排他锁 |
| **不缓存** | 直接读 DB |

```java
// 分布式锁保证强一致
public Data read(Long id) {
    RLock lock = redisson.getLock("lock:data:" + id);
    lock.lock();
    try {
        return db.query(id);  // 强一致，不缓存
    } finally {
        lock.unlock();
    }
}
```

**7. 方案选择建议**

```
弱一致（最终一致）  → Cache Aside + 短过期
中等一致           → Cache Aside + 延迟双删
较高一致           → binlog 异步同步
强一致             → 分布式锁 / 不缓存
```

**实际案例**：
- **项目背景**：商品信息缓存，原方案"先删缓存再更新 DB"，并发下频繁出现脏数据
- **根因**：删缓存后、更新 DB 前，其他线程读 DB 旧值并回种缓存
- **优化**：改为"先更新 DB 再删缓存" + binlog 异步双删兜底
- **效果**：一致性问题基本消除，偶发不一致在毫秒内自愈

**评分要点**：
- ✅ Cache Aside 流程（必备）
- ✅ 删缓存优于更新缓存的原因（核心）
- ✅ 延迟双删（必备）
- ✅ binlog 异步同步方案（加分）
- ✅ 强一致方案（加分）

---

## 第六篇 性能优化

### Q6.1 什么是 bigkey？如何发现与解决？有什么危害？

**问题描述**：请说明 bigkey 的定义、危害、发现方法与解决方案。

**参考答案**：

**1. bigkey 定义**

| 类型 | bigkey 阈值 |
| --- | --- |
| String | value > 10KB（或 1MB，按业务定） |
| Hash/List/Set/ZSet | 元素数 > 5000，或总大小 > 10MB |

**2. bigkey 危害**

| 危害 | 说明 |
| --- | --- |
| **网络阻塞** | 单条命令传输大 value，阻塞其他客户端 |
| **阻塞主线程** | 操作 bigkey 耗时长（如 `HGETALL` 大 hash），阻塞所有命令 |
| **内存不均** | Cluster 模式下某节点内存远超其他 |
| **删除阻塞** | `DEL` 大 key 是 O(N)，主线程阻塞数秒 |
| **过期触发问题** | 大 key 过期时一次性删除，阻塞主线程 |
| **持久化问题** | AOF 重写时 bigkey 影响性能 |

**3. 发现 bigkey**

```bash
# 1. redis-cli 自带工具
redis-cli --bigkeys
# 扫描所有 key，统计每种类型的最大 key

# 2. memory usage 命令（4.0+）
MEMORY USAGE key
# 返回 key 占用字节数

# 3. 离线分析 RDB
rdb-tools --bytes 10240 -f memory.csv dump.rdb
# 解析 RDB，找出大 key

# 4. 在线扫描
redis-cli --scan --pattern '*' | 
  xargs -I {} redis-cli memory usage {} |
  sort -rn | head -20
```

**4. 解决方案**

**① 拆分**

```bash
# 原：一个大 Hash
HSET huge_hash field1 v1 field2 v2 ... fieldN vN

# 拆：按字段哈希分到多个小 Hash
HSET huge_hash:0 field1 v1 field2 v2  ← field1.hash() % 10 = 0
HSET huge_hash:1 field3 v3            ← field3.hash() % 10 = 1
```

**② 压缩**

```java
// 原：存 JSON 字符串，10KB
redis.set("data", bigJson);

// 优化：压缩后存
byte[] compressed = compress(bigJson.getBytes());
redis.set("data".getBytes(), compressed);
```

**③ 业务控制**

- 限制单 key 大小（如 List 最多 1000 元素）
- 用 ZSet 分页而非全量

**5. 安全删除 bigkey**

```bash
# ❌ 危险：DEL 大 key 阻塞主线程
DEL huge_key

# ✅ 4.0+ UNLINK：异步删除，不阻塞
UNLINK huge_key

# ✅ 渐进删除（Hash）
HSCAN huge_hash 0
HDEL huge_hash field1 field2 ...  # 分批删

# ✅ 渐进删除（List）
LTRIM huge_list 0 -1000  # 每次删 1000 个
```

**6. 配置优化**

```conf
# 4.0+ 异步删除（DEL、过期、淘汰等均异步）
lazyfree-lazy-eviction yes       # 淘汰异步
lazyfree-lazy-expire yes         # 过期异步
lazyfree-lazy-server-del yes     # 服务端删除异步
replica-lazy-flush yes           # 从库 flush 异步
```

**实际案例**：
- **项目背景**：用户购物车用 Hash 存，某用户购物车 5 万商品，`HGETALL` 卡 2 秒
- **问题**：单 key 50MB，阻塞主线程影响所有用户
- **优化**：拆分为 `cart:{uid}:0` ~ `cart:{uid}:9` 共 10 个 Hash，按商品 ID hash 分桶
- **效果**：单 Hash 5K 元素，操作 < 10ms

**评分要点**：
- ✅ bigkey 定义与危害（必备）
- ✅ 发现方法（redis-cli --bigkeys、memory usage）（必备）
- ✅ 拆分方案（核心）
- ✅ UNLINK vs DEL（必备）
- ✅ lazyfree 配置（加分）

---

### Q6.2 什么是 hotkey？如何发现与解决？

**问题描述**：请说明 hotkey 的危害、发现方法与解决方案。

**参考答案**：

**1. hotkey 危害**

- **单节点 CPU 飙高**：Cluster 模式下某节点 QPS 远超其他
- **网络带宽打满**：热点 key 占用大量带宽
- **缓存击穿**：热点 key 过期瞬间 DB 压力骤增
- **集群倾斜**：某节点内存/CPU 远超其他

**2. 发现 hotkey**

```bash
# 1. redis-cli 自带（4.0+）
redis-cli --hotkeys
# 需配置 maxmemory-policy 为 allkeys-lfu

# 2. monitor 命令（生产慎用，影响性能）
redis-cli monitor | grep -o 'GET [^ ]*' | sort | uniq -c | sort -rn | head

# 3. 代理层统计（如有 twemproxy/codis）
# 4. 客户端统计（在 SDK 中采样）
# 5. redis-faina（Instagram 开源工具）
```

**3. 解决方案**

**① 本地缓存（多级缓存）**

```java
// Caffeine 本地缓存 + Redis 二级缓存
Cache<String, String> localCache = Caffeine.newBuilder()
    .maximumSize(10_000)
    .expireAfterWrite(10, TimeUnit.SECONDS)
    .build();

public String get(String key) {
    // 一级：本地缓存
    String value = localCache.getIfPresent(key);
    if (value != null) return value;
    
    // 二级：Redis
    value = redis.get(key);
    if (value != null) {
        localCache.put(key, value);
    }
    return value;
}
```

**优势**：本地缓存挡住 90% 请求，Redis QPS 大幅降低

**② 拆分热点 key**

```java
// 原：hot_key 被高频访问
redis.get("hot_key");

// 拆：复制多份，随机访问
String[] keys = {"hot_key:1", "hot_key:2", ..., "hot_key:10"};
String key = keys[random.nextInt(10)];
redis.get(key);

// 写时同步更新所有副本
for (String k : keys) {
    redis.set(k, value);
}
```

**优势**：分散到多个节点，单节点压力降低

**③ 读写分离**

热点 key 的读分散到从库：

```java
// 主库写，从库读（Jedis 读从库）
Set<HostAndPort> slaves = getSlaveNodes();
Jedis slave = new Jedis(slaves.iterator().next());
String value = slave.get("hot_key");
```

**④ 限流降级**

对热点接口限流，保护 DB：

```java
@SentinelResource(value = "hotApi", blockHandler = "fallback")
public String hotApi() {
    return redis.get("hot_key");
}
```

**4. 多级缓存架构**

```
客户端 ──► 本地缓存（Caffeine）──► Redis ──► DB
           10ms TTL               1s TTL    持久化
           命中率 90%             命中率 9%  命中率 1%
```

**实际案例**：
- **项目背景**：明星八卦热搜，单 key QPS 8 万，单节点 CPU 95%
- **优化**：本地缓存（Caffeine，5s TTL）+ 拆分 10 副本 key
- **效果**：Redis QPS 降到 8 千，CPU 降到 30%

**评分要点**：
- ✅ hotkey 危害（必备）
- ✅ 发现方法（必备）
- ✅ 本地缓存多级方案（核心）
- ✅ 拆分副本方案（必备）
- ✅ 限流降级（加分）

---

### Q6.3 Pipeline 的原理？与批量命令（MGET/MSET）有何区别？注意事项？

**问题描述**：请说明 Pipeline 的原理、使用场景与注意事项。

**参考答案**：

**1. Pipeline 原理**

普通命令：客户端发一条命令，等服务器返回，再发下一条（RTT 高）。

```
客户端 ──cmd1──► 服务端
       ◄──resp1─
客户端 ──cmd2──► 服务端       N 条命令 N 次 RTT
       ◄──resp2─
```

Pipeline：客户端**打包多条命令一次发送**，服务端依次执行后**打包返回**。

```
客户端 ──cmd1,cmd2,cmd3──► 服务端
       ◄──resp1,resp2,resp3─   1 次 RTT
```

**2. Pipeline vs MGET/MSET**

| 维度 | Pipeline | MGET/MSET |
| --- | --- | --- |
| **本质** | 通信层优化（批量发送） | 原子命令 |
| **原子性** | ❌ 非原子（中间可插入其他客户端命令） | ✅ 原子 |
| **支持命令** | 任意命令组合 | 仅 GET/SET |
| **服务端执行** | 逐条执行 | 单次执行 |
| **场景** | 大批量不同命令 | 批量同类型操作 |

**3. 性能对比**

```
1 万次 GET：
- 普通模式：10000 × 1ms(RTT) = 10s
- Pipeline（每批 1000）：10 × 1ms = 10ms
- MGET 1 万 key：1 × 5ms = 5ms（最优）
```

**4. Pipeline 使用示例**

```java
// Jedis Pipeline
Pipeline pipe = jedis.pipelined();
for (int i = 0; i < 10000; i++) {
    pipe.set("key" + i, "value" + i);
}
pipe.sync();  // 同步等待所有结果

// 或异步获取结果
List<Object> results = pipe.syncAndReturnAll();
```

```python
# Python redis-py
pipe = r.pipeline()
for i in range(10000):
    pipe.set(f'key{i}', f'value{i}')
pipe.execute()
```

**5. 注意事项**

| 注意点 | 说明 |
| --- | --- |
| **非原子** | Pipeline 中间可能插入其他客户端命令，不能用于需原子的场景 |
| **单批次大小** | 建议每批 ≤ 1000 命令，过大阻塞网络与内存 |
| **超时设置** | 大批量操作需调大 timeout，避免超时断开 |
| **Cluster 限制** | Pipeline 命令需在同一节点（同 slot），跨节点需客户端分片 |
| **内存占用** | 服务端缓存所有响应，批次过大可能 OOM |

**6. Cluster 模式下的 Pipeline**

```java
// JedisCluster 不直接支持 Pipeline，需用集合分片
Map<JedisPool, List<String>> grouped = groupBySlot(keys);
for (Map.Entry<JedisPool, List<String>> e : grouped.entrySet()) {
    try (Jedis jedis = e.getKey().getResource()) {
        Pipeline pipe = jedis.pipelined();
        for (String key : e.getValue()) {
            pipe.get(key);
        }
        pipe.sync();
    }
}
```

**实际案例**：
- **项目背景**：启动时预热 10 万商品到缓存，逐条 SET 耗时 100 秒
- **优化**：用 Pipeline 批量，每批 1000 条
- **效果**：耗时降到 2 秒

**评分要点**：
- ✅ Pipeline 原理（一次 RTT）（必备）
- ✅ 与 MGET 区别（原子性）（核心）
- ✅ 注意事项（批次大小、Cluster 限制）（必备）
- ✅ 性能数据（加分）

---

### Q6.4 Redis 慢查询如何排查与优化？

**问题描述**：线上 Redis 响应慢，请给出排查与优化流程。

**参考答案**：

**1. 慢查询日志**

```conf
# redis.conf
slowlog-log-slower-than 10000   # 慢查询阈值，微秒（10ms）
slowlog-max-len 128             # 最多保存 128 条
```

```bash
# 查看慢查询
SLOWLOG GET 10

# 输出示例：
1) 1) (integer) 14            # ID
   2) (integer) 1628000000    # 时间戳
   3) (integer) 25000         # 耗时（微秒，25ms）
   4) 1) "KEYS"
      2) "user:*"             # 命令与参数
```

**2. 排查流程**

```
1. SLOWLOG 看慢命令 → 2. 分析命令类型 → 3. 优化
                              │
                              ├─ O(N) 命令（KEYS、SORT）→ 避免或用 SCAN
                              ├─ bigkey 操作 → 拆分或用 HSCAN
                              ├─ 集中过期 → 随机过期
                              └─ fork 阻塞 → 调整持久化策略
```

**3. 常见慢命令与替代方案**

| 慢命令 | 复杂度 | 替代方案 |
| --- | --- | --- |
| `KEYS pattern` | O(N) | `SCAN`（游标迭代） |
| `SORT key` | O(N+M*logM) | 业务层排序或 ZSet |
| `HGETALL big_hash` | O(N) | `HSCAN` 或 `HMGET` 部分字段 |
| `LRANGE key 0 -1`（大 list） | O(N) | 分页 `LRANGE 0 99` |
| `SMEMBERS big_set` | O(N) | `SSCAN` |
| `FLUSHALL`/`FLUSHDB` | O(N) | `FLUSHALL ASYNC`（4.0+） |
| `DEL big_key` | O(N) | `UNLINK` |

**4. SCAN 替代 KEYS**

```bash
# KEYS 阻塞主线程
KEYS user:*           # ❌ 100 万 key 阻塞数秒

# SCAN 游标迭代，不阻塞
SCAN 0 MATCH user:* COUNT 100
# 返回：(next_cursor, [key1, key2, ...])
SCAN <next_cursor> MATCH user:* COUNT 100
# 重复直到 cursor=0
```

**5. 其他性能问题**

**持久化阻塞**：
- `BGSAVE`/`BGREWRITEAOF` fork 大内存实例耗时（10G 内存 fork 约 1 秒）
- 优化：控制单实例内存 < 10G

**AOF fsync 阻塞**：
- `always` 策略每条命令 fsync，磁盘慢时阻塞主线程
- 优化：改 `everysec`

**网络问题**：
- 客户端与 Redis 跨机房，RTT 高
- 优化：同机房部署，或用长连接

**6. 监控指标**

```bash
INFO commandstats    # 各命令调用统计
INFO stats           # ops/sec, rejected_connections
INFO memory          # 内存使用
LATENCY HISTORY event  # 延迟事件
LATENCY GRAPH event    # 延迟图表
```

**实际案例**：
- **项目背景**：定时任务用 `KEYS order:*` 扫描订单，每次阻塞 5 秒
- **优化**：改用 `SCAN` 迭代，每次 100 条
- **效果**：阻塞消除，扫描总耗时不变但分摊到多次

**评分要点**：
- ✅ 慢查询配置与查看（必备）
- ✅ O(N) 命令替代（KEYS→SCAN）（必备）
- ✅ bigkey 操作优化（必备）
- ✅ 持久化阻塞分析（加分）

---

## 第七篇 分布式锁与限流

### Q7.1 如何用 Redis 实现分布式锁？有哪些坑？Redlock 算法是什么？

**问题描述**：请说明 Redis 分布式锁的实现、常见问题与 Redlock。

**参考答案**：

**1. 基础实现**

```bash
# SET key value NX PX 30000
SET lock:order:123 uuid-xxx NX PX 30000
# NX：key 不存在才设置（互斥）
# PX 30000：过期 30 秒（防死锁）
# value 用唯一 UUID（防误删）
```

```java
String lockKey = "lock:order:123";
String requestId = UUID.randomUUID().toString();

// 加锁
boolean locked = "OK".equals(jedis.set(lockKey, requestId, "NX", "PX", 30000));

// 解锁（Lua 保证原子性）
String lua = 
    "if redis.call('get', KEYS[1]) == ARGV[1] then " +
    "  return redis.call('del', KEYS[1]) " +
    "else " +
    "  return 0 " +
    "end";
jedis.eval(lua, Collections.singletonList(lockKey), Collections.singletonList(requestId));
```

**2. 关键要点**

| 要点 | 说明 |
| --- | --- |
| **必须设过期** | 防止持锁进程崩溃导致死锁 |
| **value 用唯一 ID** | 防止 A 的锁被 B 误删（A 超时后 B 获得锁，A 恢复后删除 B 的锁） |
| **解锁用 Lua** | 保证"判断+删除"原子性 |
| **过期时间合理** | 大于业务最大执行时间 |

**3. 常见坑**

**坑 1：业务执行时间超过锁过期**

```
A 加锁（30s）→ A 业务执行 40s → 第 30s 锁过期，B 加锁 → A 执行完，删了 B 的锁
```

**解决：看门狗续期**

```java
// Redisson 看门狗自动续期
RLock lock = redisson.getLock("lock:order:123");
lock.lock();  // 默认 30s 过期，每 10s 续期一次
try {
    // 业务逻辑
} finally {
    lock.unlock();
}
```

**坑 2：主从切换丢锁**

```
A 在主库加锁 → 主库宕机 → 从库晋升为新主（未同步锁）→ B 在新主加锁成功 → A、B 同时持锁
```

**解决：Redlock 算法**

**坑 3：可重入**

同一线程多次加锁会失败，需可重入：

```java
// Redisson 可重入锁
RLock lock = redisson.getLock("lock:order:123");
lock.lock();      // 第一次加锁
lock.lock();      // 第二次加锁（计数+1，成功）
lock.unlock();    // 计数-1
lock.unlock();    // 释放
```

实现：用 Hash 存 `{thread_id: count}`，Lua 脚本判断。

**4. Redlock 算法**

针对主从切换丢锁问题，antirez 提出 Redlock：

```
1. 客户端获取当前时间 T1
2. 依次向 N 个（通常 5）独立 Redis 实例加锁（相同的 key、value、短过期）
3. 若多数实例（N/2+1）加锁成功，且总耗时 < 锁过期时间 → 加锁成功
4. 否则：向所有实例发解锁请求（即使某些未加锁）
```

```
Redis1 ────► 加锁成功 ✓
Redis2 ────► 加锁成功 ✓     3/5 多数 → 加锁成功
Redis3 ────► 加锁成功 ✓
Redis4 ────► 超时 ✗
Redis5 ────► 超时 ✗
```

**Redlock 争议**：Martin Kleppmann 批评其仍可能因 GC 暂停、时钟漂移导致问题。生产中需评估风险。

**5. Redisson 实现（推荐）**

```java
Config config = new Config();
config.useClusterServers().addNodeAddress("redis://...:6379");
RedissonClient redisson = Redisson.create(config);

RLock lock = redisson.getLock("lock:order:123");
try {
    // 尝试加锁，最多等 5 秒，锁自动释放 30 秒
    boolean locked = lock.tryLock(5, 30, TimeUnit.SECONDS);
    if (locked) {
        // 业务逻辑
    }
} finally {
    if (lock.isHeldByCurrentThread()) {
        lock.unlock();
    }
}
```

**Redisson 优势**：
- 看门狗自动续期
- 可重入
- 公平锁、读写锁、信号量
- Redlock 实现

**6. 分布式锁对比**

| 方案 | 一致性 | 性能 | 复杂度 |
| --- | --- | --- | --- |
| Redis 单机 | 弱 | 高 | 低 |
| Redlock | 中 | 中 | 中 |
| ZooKeeper | 强 | 中 | 高 |
| etcd | 强 | 中 | 高 |

**实际案例**：
- **项目背景**：订单防重，用 Redis 分布式锁，偶发重复下单
- **根因**：业务执行超过锁过期，看门狗未启用
- **优化**：改用 Redisson 看门狗续期 + 业务幂等（DB 唯一索引）双保险
- **效果**：重复下单清零

**评分要点**：
- ✅ SET NX PX 加锁（必备）
- ✅ Lua 脚本原子解锁（必备）
- ✅ 看门狗续期（核心）
- ✅ Redlock 原理与争议（加分）
- ✅ Redisson 使用（必备）

---

### Q7.2 用 Redis 实现限流？固定窗口、滑动窗口、令牌桶的原理？

**问题描述**：请说明三种限流算法的 Redis 实现与适用场景。

**参考答案**：

**1. 固定窗口计数器**

```lua
-- 每秒限 100 次
-- key: rate:user:123:202608021530 (含分钟)
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local current = redis.call('INCR', key)
if current == 1 then
    redis.call('EXPIRE', key, 1)  -- 首次设过期
end
if current > limit then
    return 0  -- 限流
else
    return 1  -- 放行
end
```

**缺点**：窗口边界突刺。如 1 秒限 100，第 0.9 秒来 100 次 + 第 1.0 秒来 100 次 = 0.1 秒内 200 次。

**2. 滑动窗口（ZSet 实现）**

```lua
-- 每秒限 100 次
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = 1000  -- 1 秒（毫秒）
local limit = 100

-- 移除窗口外的记录
redis.call('ZREMRANGEBYSCORE', key, 0, now - window)

-- 统计当前窗口内请求数
local count = redis.call('ZCARD', key)
if count >= limit then
    return 0
end

-- 添加当前请求
redis.call('ZADD', key, now, now)  -- member 用时间戳保证唯一
redis.call('EXPIRE', key, 2)  -- 过期清理
return 1
```

**优点**：平滑限流，无突刺。**缺点**：内存占用较高（每请求一个 member）。

**3. 令牌桶**

```lua
-- 每秒生成 10 个令牌，桶容量 20
local key = KEYS[1]
local capacity = 20        -- 桶容量
local rate = 10            -- 每秒生成令牌数
local now = tonumber(ARGV[1])
local requested = 1        -- 本次请求令牌数

-- 上次填充时间与剩余令牌
local last_time = tonumber(redis.call('HGET', key, 'last_time') or now)
local tokens = tonumber(redis.call('HGET', key, 'tokens') or capacity)

-- 计算新增令牌
local delta = math.max(0, now - last_time) / 1000 * rate
tokens = math.min(capacity, tokens + delta)

if tokens < requested then
    return 0  -- 限流
end

tokens = tokens - requested
redis.call('HMSET', key, 'tokens', tokens, 'last_time', now)
redis.call('EXPIRE', key, 10)
return 1
```

**优点**：允许突发（桶满时一次性消耗多个令牌）。**适用**：API 限流、网关。

**4. 三种算法对比**

| 算法 | 平滑度 | 突发支持 | 内存 | 适用 |
| --- | --- | --- | --- | --- |
| 固定窗口 | 差（边界突刺） | ❌ | 低 | 简单场景 |
| 滑动窗口 | 好 | ❌ | 高 | 严格限流 |
| 令牌桶 | 好 | ✅ | 中 | API 网关 |

**5. Redisson 限流实现**

```java
// 滑动窗口
RRateLimiter limiter = redisson.getRateLimiter("api:limiter");
limiter.trySetRate(RateType.OVERALL, 100, 1, RateIntervalUnit.SECONDS);

if (limiter.tryAcquire(1)) {
    // 放行
} else {
    // 限流
}
```

**实际案例**：
- **项目背景**：开放 API 限流，每用户每秒 100 次
- **方案**：滑动窗口 ZSet 实现，过期清理
- **效果**：精准限流，无边界突刺，内存可控

**评分要点**：
- ✅ 三种算法原理（必备）
- ✅ 滑动窗口 ZSet 实现（核心）
- ✅ 令牌桶突发支持（必备）
- ✅ Lua 保证原子性（加分）

---

## 第八篇 实际应用场景

### Q8.1 用 Redis 实现排行榜？如何处理实时更新与分页查询？

**问题描述**：请设计一个游戏排行榜，支持实时更新、Top N 查询、个人排名查询。

**参考答案**：

**1. 数据结构选型：ZSet**

```bash
ZADD rank:score 1000 user:1 2000 user:2 1500 user:3
# score 为分数，member 为用户 ID
```

**2. 核心操作**

```bash
# 更新分数（+100）
ZINCRBY rank:score 100 user:1

# Top 10（高分在前）
ZREVRANGE rank:score 0 9 WITHSCORES

# 个人排名（从 0 开始）
ZREVRANK rank:score user:1

# 个人分数
ZSCORE rank:score user:1

# 分数区间内的人数
ZCOUNT rank:score 1000 2000
```

**3. 实时更新优化**

```java
// 高频更新用 Pipeline 批量
Pipeline pipe = jedis.pipelined();
for (ScoreUpdate update : batchUpdates) {
    pipe.zincrby("rank:score", update.getDelta(), "user:" + update.getUserId());
}
pipe.sync();
```

**4. 分页查询**

```java
public List<RankItem> getRankPage(int page, int size) {
    int start = (page - 1) * size;
    int end = start + size - 1;
    
    // ZSet 范围查询 O(logN + M)
    Set<Tuple> tuples = jedis.zrevrangeWithScores("rank:score", start, end);
    
    return tuples.stream()
        .map(t -> new RankItem(t.getElement(), t.getScore()))
        .collect(Collectors.toList());
}
```

**5. 周榜/月榜**

```bash
# 每日榜
ZADD rank:daily:20260802 1000 user:1

# 周榜：合并 7 天的日榜
ZUNIONSTORE rank:weekly:202631 7 
    rank:daily:20260802 rank:daily:20260803 ... 
    AGGREGATE MAX   # 取最高分
```

**6. 性能优化**

- **冷热分离**：只缓存 Top 1000，超出查 DB
- **预计算**：定时任务预生成 Top N，前端直接读
- **分桶**：按分数段分多个 ZSet，避免单 key 过大

**7. 实际案例**

```java
// 游戏排行榜服务
@Service
public class RankService {
    private static final String RANK_KEY = "rank:score";
    
    @Autowired
    private JedisPool jedisPool;
    
    // 更新分数
    public void updateScore(Long userId, long delta) {
        try (Jedis jedis = jedisPool.getResource()) {
            jedis.zincrby(RANK_KEY, delta, "user:" + userId);
        }
    }
    
    // 获取 Top N
    public List<RankItem> getTopN(int n) {
        try (Jedis jedis = jedisPool.getResource()) {
            Set<Tuple> tuples = jedis.zrevrangeWithScores(RANK_KEY, 0, n - 1);
            List<RankItem> list = new ArrayList<>();
            int rank = 1;
            for (Tuple t : tuples) {
                list.add(new RankItem(rank++, 
                    Long.parseLong(t.getElement().split(":")[1]), 
                    (long) t.getScore()));
            }
            return list;
        }
    }
    
    // 获取个人排名（含前后各 2 名）
    public RankItem getMyRank(Long userId) {
        try (Jedis jedis = jedisPool.getResource()) {
            String member = "user:" + userId;
            Long rank = jedis.zrevrank(RANK_KEY, member);
            Double score = jedis.zscore(RANK_KEY, member);
            if (rank == null) return null;
            return new RankItem(rank + 1, userId, score.longValue());
        }
    }
}
```

**评分要点**：
- ✅ ZSet 实现排行榜（必备）
- ✅ ZINCRBY/ZREVRANGE/ZREVRANK（必备）
- ✅ 周榜 ZUNIONSTORE（加分）
- ✅ 分页与性能优化（必备）

---

### Q8.2 Redis 实现消息队列？List、Pub/Sub、Stream 的对比？

**问题描述**：请对比 Redis 三种消息队列方案的原理与适用场景。

**参考答案**：

**1. 三种方案对比**

| 方案 | 持久化 | 消费确认 | 消费组 | 多播 | 适用场景 |
| --- | --- | --- | --- | --- | --- |
| **List** | ✅ | ❌（需自行实现） | ❌ | ❌ | 简单队列 |
| **Pub/Sub** | ❌ | ❌ | ❌ | ✅ | 实时广播 |
| **Stream**（5.0+） | ✅ | ✅ | ✅ | ✅ | 完整 MQ |

**2. List 实现**

```bash
# 生产者
LPUSH queue:order "msg1" "msg2"

# 消费者（阻塞式）
BRPOP queue:order 0  # 阻塞直到有消息
```

**优点**：简单、持久化。**缺点**：
- 无消费确认（取出即删，处理失败消息丢失）
- 无消费组（一条消息只能一个消费者消费）
- 无多播（一条消息不能多消费者同时消费）

**改进消费确认**：

```bash
# 备份队列方案
BRPOPLPUSH queue:order queue:order:processing 0
# 处理完后 LREM queue:order:processing 1 msg
# 处理失败消息留在 processing 队列
```

**3. Pub/Sub 实现**

```bash
# 订阅
SUBSCRIBE channel:order

# 发布
PUBLISH channel:order "msg1"
```

**优点**：实时多播。**缺点**：
- **消息不持久化**：订阅前的消息丢失
- **无消费确认**：消息发出即丢，不管消费者是否收到
- **客户端断线丢消息**：重连后无法补回

**4. Stream 实现（推荐，5.0+）**

```bash
# 生产者（XADD）
XADD stream:order * order_id 123 user_id 456
# * 表示自动生成消息 ID

# 消费者组（XGROUP）
XGROUP CREATE stream:order group1 0  # 从头消费

# 消费（XREADGROUP）
XREADGROUP GROUP group1 consumer1 COUNT 10 BLOCK 5000 STREAMS stream:order >
# > 表示消费组未读的新消息

# 确认（XACK）
XACK stream:order group1 <message_id>

# 消费失败的消息可重新投递（XPENDING + XCLAIM）
XPENDING stream:order group1   # 查看未确认消息
XCLAIM stream:order group1 consumer2 5000 <message_id>  # 转给其他消费者
```

**Stream 特性**：
- ✅ 持久化（AOF/RDB）
- ✅ 消费组（多消费者分摊）
- ✅ 消费确认（XACK）
- ✅ 多播（多消费组各自消费）
- ✅ 死信队列（XPENDING 追踪未确认）
- ✅ 消息回溯（按 ID 查询历史）

**5. Stream 消费示例**

```java
// 生产者
Map<String, String> msg = new HashMap<>();
msg.put("order_id", "123");
msg.put("user_id", "456");
StreamEntryID id = jedis.xadd("stream:order", StreamEntryID.NEW_ENTRY, msg);

// 消费者
jedis.xgroupCreate("stream:order", "group1", new StreamEntryID(0, 0));
while (true) {
    List<Map.Entry<String, List<StreamEntry>>> entries = 
        jedis.xreadGroup("group1", "consumer1", 1, 5000, false, 
            XReadGroupParams.xReadGroupParams(), 
            new HashMap<String, StreamEntryID>() {{ put("stream:order", StreamEntryID.LAST_ENTRY); }});
    
    for (StreamEntry entry : entries.get(0).getValue()) {
        try {
            processOrder(entry.getFields());
            jedis.xack("stream:order", "group1", entry.getID());  // 确认
        } catch (Exception e) {
            // 不 ack，消息进 pending 列表，可被其他消费者 claim
        }
    }
}
```

**6. 死信处理**

```bash
# 查看 pending 列表（已读未确认）
XPENDING stream:order group1 - + 10

# 超时消息转给其他消费者
XCLAIM stream:order group1 consumer2 60000 <message_id>
# 60000 = 超过 60 秒未确认
```

**7. 实际案例**

```
项目背景：订单异步处理，原用 List + BRPOP，处理失败消息丢失
方案：改用 Stream + 消费组
- 多消费者分摊（消费组）
- 处理失败进 pending，可重试
- 超时消息转其他消费者（XCLAIM）
效果：消息零丢失，自动重试，吞吐提升 3 倍
```

**评分要点**：
- ✅ 三种方案对比（必备）
- ✅ Stream 消费组与 ACK 机制（核心）
- ✅ XPENDING/XCLAIM 死信处理（加分）
- ✅ 各方案适用场景（必备）

---

### Q8.3 用 Redis 实现附近的人？GEO 数据类型原理？

**问题描述**：请说明 Redis GEO 的原理，并实现"附近的人"功能。

**参考答案**：

**1. GEO 原理**

Redis GEO 基于 **ZSet + GeoHash 算法**：

- **GeoHash**：将经纬度编码为字符串，相近位置编码前缀相同
- **ZSet 存储**：member 为地点 ID，score 为 GeoHash 编码值（52 位整数）
- 利用 ZSet 的范围查询能力，查找附近地点

**2. GeoHash 编码**

```
经度范围 [-180, 180]，纬度范围 [-85, 85]

编码过程（二分法）：
经度 116.40（北京）：
[-180,180] → 116.40 在 [0,180] → 1
[0,180] → 在 [90,180] → 1
[90,180] → 在 [90,135] → 0
... 最终得到一串二进制

纬度 39.90：
类似二分，得到二进制串

合并：经度、纬度交替组合 → 转为 Base32 → "wx4g093k"
```

**GeoHash 精度**：

| 编码长度 | 范围 |
| --- | --- |
| 6 位 | 约 1.2km × 0.6km |
| 7 位 | 约 150m × 150m |
| 8 位 | 约 40m × 40m |

**3. Redis GEO 命令**

```bash
# 添加地点
GEOADD places 116.40 39.90 "user:1"  # 经度 纬度 member
GEOADD places 116.41 39.91 "user:2"
GEOADD places 116.50 40.00 "user:3"

# 计算距离
GEODIST places "user:1" "user:2" km
# 返回两点距离（千米）

# 查找附近的人（半径 5km 内，按距离排序，限制 10 个）
GEOSEARCH places FROMLONLAT 116.40 39.90 BYRADIUS 5 km ASC COUNT 10
# FROMLONLAT：从指定经纬度
# BYRADIUS 5 km：半径 5 公里
# ASC：按距离升序
# COUNT 10：最多 10 个

# 获取地点经纬度
GEOPOS places "user:1"

# 获取 GeoHash
GEOHASH places "user:1"
```

**4. "附近的人"实现**

```java
@Service
public class NearbyService {
    private static final String GEO_KEY = "user:location";
    
    @Autowired
    private Jedis jedis;
    
    // 更新用户位置
    public void updateLocation(Long userId, double lng, double lat) {
        jedis.geoadd(GEO_KEY, lng, lat, "user:" + userId);
    }
    
    // 查找附近 5km 内的用户
    public List<NearbyUser> findNearby(double lng, double lat, double radiusKm, int count) {
        // GEOSEARCH 返回成员、距离、坐标
        GeoSearchParam param = GeoSearchParam.geoSearchParam()
            .byRadius(radiusKm, GeoUnit.KM)
            .withCoord()
            .withDist()
            .ascending()
            .count(count);
        
        List<GeoRadiusResponse> responses = jedis.geosearch(GEO_KEY, 
            GeoCoord.geoCoord(lng, lat), param);
        
        return responses.stream()
            .map(r -> new NearbyUser(
                Long.parseLong(r.getMemberByString().split(":")[1]),
                r.getDistance(),
                r.getCoordinate().getLongitude(),
                r.getCoordinate().getLatitude()
            ))
            .collect(Collectors.toList());
    }
}
```

**5. 性能优化**

- **定期清理**：过期用户位置用 ZSet 过期机制清理（GEO 底层是 ZSet）
- **分城市存储**：避免单 key 过大，按城市分 `geo:beijing`、`geo:shanghai`
- **精度权衡**：GEOSEARCH 半径大时性能下降，可分级查询

**6. GEO 底层 ZSet 的过期问题**

GEO 本质是 ZSet，无法直接对单个 member 设过期。解决方案：

```java
// 方案 1：定时清理（移除超时未上报的用户）
jedis.zremrangebyscore(GEO_KEY, 0, System.currentTimeMillis() - 30 * 60 * 1000);

// 方案 2：用 ZSet score 存时间戳，GEO 用另一个 key，定期同步
```

**实际案例**：
- **项目背景**：社交 App "附近的人"，1 亿用户上报位置
- **方案**：Redis GEO + 按城市分桶 + 定时清理超时用户
- **效果**：5km 内查询 < 10ms，单城市 10 万用户无压力

**评分要点**：
- ✅ GEO 基于 ZSet + GeoHash（必备）
- ✅ GeoHash 编码原理（加分）
- ✅ GEOADD/GEOSEARCH 命令（必备）
- ✅ 分城市优化（加分）

---

### Q8.4 用 Redis 实现计数器与 HyperLogLog？

**问题描述**：请说明 Redis 计数器方案与 HyperLogLog 基数统计的原理。

**参考答案**：

**1. 简单计数器**

```bash
# 文章阅读数
INCR article:123:views

# 点赞数
INCR article:123:likes

# 自减
DECR article:123:likes
```

**2. 分布式计数器（防超卖）**

```lua
-- Lua 保证原子性
local key = KEYS[1]
local count = tonumber(ARGV[1])
local remaining = redis.call('GET', key)
if tonumber(remaining) >= count then
    redis.call('DECRBY', key, count)
    return 1  -- 成功
else
    return 0  -- 库存不足
end
```

**3. HyperLogLog 基数统计**

**场景**：统计 UV（独立访客数），1 亿用户去重。

**朴素方案**：用 Set 存所有用户 ID，1 亿 ID 占内存 ~1GB。

**HyperLogLog**：**概率算法**，固定 12KB 内存，误差 0.81%。

```bash
# 添加元素
PFADD page:uv:user1 123  # 用户 ID
PFADD page:uv:user1 456

# 统计 UV
PFCOUNT page:uv:user1

# 合并多个 HLL（多天合并月 UV）
PFMERGE page:uv:month page:uv:day1 page:uv:day2 ...
```

**4. HyperLogLog 原理**

- **伯努利试验**：抛硬币，统计连续正面的最大次数 k，估算试验次数 N ≈ 2^k
- **分桶平均**：将 hash 值分到 16384 个桶（2^14），每桶统计最大前导零数，调和平均减少误差
- **内存固定**：16384 桶 × 6 bit = 12KB

```
用户 ID hash → 0100110...（64 位）
                  │
   前 14 位 → 桶编号（0-16383）
   后 50 位 → 统计前导零数（最大 50）

桶 1234: 最大前导零 = 5
桶 5678: 最大前导零 = 3
...
估算基数 = 2^(调和平均) × 16384 × 修正因子
```

**5. HyperLogLog vs Set**

| 维度 | Set | HyperLogLog |
| --- | --- | --- |
| 内存 | 1 亿用户约 1GB | 固定 12KB |
| 精度 | 100% 精确 | 0.81% 误差 |
| 操作 | SADD/SCARD | PFADD/PFCOUNT |
| 能否取元素 | ✅ | ❌（只统计数量） |
| 适用 | 需要具体用户列表 | 只需数量（UV/PV） |

**6. 实际案例**

```java
// UV 统计服务
@Service
public class UVService {
    @Autowired
    private Jedis jedis;
    
    // 记录访问
    public void recordVisit(String page, Long userId) {
        String key = "uv:" + page + ":" + LocalDate.now();
        jedis.pfadd(key, "user:" + userId);
    }
    
    // 获取当日 UV
    public long getDailyUV(String page) {
        String key = "uv:" + page + ":" + LocalDate.now();
        return jedis.pfcount(key);
    }
    
    // 获取月 UV（合并 30 天）
    public long getMonthlyUV(String page) {
        String[] dailyKeys = IntStream.rangeClosed(1, 30)
            .mapToObj(i -> "uv:" + page + ":" + LocalDate.now().minusDays(i - 1))
            .toArray(String[]::new);
        
        String mergedKey = "uv:" + page + ":month:" + YearMonth.now();
        jedis.pfmerge(mergedKey, dailyKeys);
        return jedis.pfcount(mergedKey);
    }
}
```

**评分要点**：
- ✅ INCR 简单计数器（必备）
- ✅ Lua 防超卖（加分）
- ✅ HyperLogLog 12KB 固定内存（必备）
- ✅ 伯努利试验原理（加分）
- ✅ PFMERGE 合并（必备）

---

### Q8.5 用 Redis 实现位图统计？用户签到与活跃统计？

**问题描述**：请说明 Bitmap 的原理，并实现用户签到与活跃用户统计。

**参考答案**：

**1. Bitmap 原理**

- Redis String 类型支持位操作
- 每个 key 最多 2^32 位（512MB），可存 42 亿布尔值
- **内存极省**：1 亿用户在线状态仅 12.5MB

**2. 用户签到**

```bash
# 用户 123 在 2026-08-02 签到（一年第几天）
SETBIT sign:123:2026 214 1
# 第 214 天（8 月 2 日约一年第 214 天）

# 检查某天是否签到
GETBIT sign:123:2026 214

# 统计本年签到次数
BITCOUNT sign:123:2026

# 连续签到天数（从今天往前数）
BITFIELD sign:123:2026 GET u214 1  # 取第 214 位
```

**3. 连续签到计算**

```java
public int getContinuousSignDays(Long userId, int year) {
    String key = "sign:" + userId + ":" + year;
    int dayOfYear = LocalDate.now().getDayOfYear();
    int count = 0;
    
    // 从今天往前查
    for (int i = dayOfYear; i > 0; i--) {
        if (jedis.getbit(key, i)) {
            count++;
        } else {
            break;  // 遇到未签到，中断
        }
    }
    return count;
}
```

**4. 月签到日历**

```bash
# 用 BITFIELD 取本月所有签到位
# 假设本月 1 日是一年第 213 天
BITFIELD sign:123:2026 GET u31 213
# 返回 31 位无符号整数，每位代表一天
```

**5. 活跃用户统计（DAU/MAU）**

```bash
# 用户 123 在 2026-08-02 活跃
SETBIT active:2026-08-02 123 1

# 当日活跃用户数
BITCOUNT active:2026-08-02

# 7 日活跃用户（OR 合并，去重）
BITOP OR active:7days active:2026-08-02 active:2026-08-01 ... active:2026-07-27
BITCOUNT active:7days

# 7 日连续活跃（AND 合并）
BITOP AND active:continuous7 active:2026-08-02 active:2026-08-01 ... active:2026-07-27
BITCOUNT active:continuous7
```

**6. 三种统计方案对比**

| 场景 | 方案 | 内存（1亿用户） |
| --- | --- | --- |
| 用户签到 | Bitmap（按用户+年） | 1 用户 1 年 365 位 ≈ 46B |
| 日活 DAU | Bitmap（按日期） | 1 天 1 亿位 ≈ 12.5MB |
| 月活 MAU | BITOP OR 合并 30 天 | 12.5MB（结果） |
| UV 统计 | HyperLogLog | 12KB |

**7. 实际案例**

```java
@Service
public class ActiveUserService {
    @Autowired
    private Jedis jedis;
    
    // 记录用户活跃
    public void recordActive(Long userId) {
        String key = "active:" + LocalDate.now();
        jedis.setbit(key, userId, true);
        jedis.expire(key, 60);  // 保留 60 天
    }
    
    // 获取日活
    public long getDAU(LocalDate date) {
        return jedis.bitcount("active:" + date);
    }
    
    // 获取 7 日活跃（去重）
    public long getWeeklyActive() {
        String[] keys = IntStream.rangeClosed(0, 6)
            .mapToObj(i -> "active:" + LocalDate.now().minusDays(i))
            .toArray(String[]::new);
        
        String resultKey = "active:week:" + LocalDate.now();
        jedis.bitop(BitOP.AND, resultKey, keys);
        long count = jedis.bitcount(resultKey);
        jedis.del(resultKey);  // 临时结果清理
        return count;
    }
}
```

**评分要点**：
- ✅ Bitmap 原理与内存优势（必备）
- ✅ SETBIT/GETBIT/BITCOUNT（必备）
- ✅ BITOP OR/AND 合并（核心）
- ✅ 签到 vs 活跃统计场景（必备）

---

## 附录 评分标准与面试指南

### A.1 各能力维度评分标准

| 维度 | 初级（1-3分） | 中级（4-6分） | 高级（7-9分） | 专家（10分） |
| --- | --- | --- | --- | --- |
| **核心原理** | 知道 Redis 是内存数据库 | 懂单线程模型、IO 多路复用 | 懂 6.0 多线程、数据结构底层 | 能从源码层分析跳表、SDS |
| **数据结构** | 会用五大数据类型 | 懂编码转换 | 懂跳表、quicklist 原理 | 能设计自定义结构 |
| **持久化** | 会配 RDB/AOF | 懂两者区别 | 懂混合持久化、COW | 能调优 fork 性能 |
| **高可用** | 会搭主从 | 懂哨兵原理 | 懂 Cluster 分片、Gossip | 能设计容灾方案 |
| **缓存问题** | 知道三大问题 | 懂解决方案 | 懂布隆过滤器、Redlock | 能设计多级缓存 |
| **性能优化** | 会看慢日志 | 懂 bigkey/hotkey | 懂 Pipeline、Cluster 优化 | 能全链路调优 |
| **分布式锁** | 会 SET NX | 懂 Lua 原子性 | 懂看门狗、Redlock | 能设计高可用锁 |
| **应用场景** | 会缓存、计数 | 懂排行榜、限流 | 懂 Stream MQ、GEO | 能架构设计 |

### A.2 面试官提问策略

**由浅入深**：
1. **概念题**："Redis 为什么快？" → 考察基础
2. **原理题**："跳表如何实现？" → 考察深度
3. **应用题**："如何设计排行榜？" → 考察实践
4. **场景题**："缓存雪崩怎么解决？" → 考察综合能力
5. **设计题**："设计一个支持亿级用户的活跃统计" → 考察架构能力

**追问技巧**：
- 挖底层：从"用 Redis" → "为什么用跳表" → "GeoHash 编码细节"
- 挖实践：从"懂缓存穿透" → "实际遇到过吗" → "怎么监控与防范"
- 挖权衡：从"用分布式锁" → "Redlock 有什么问题" → "如何选型"

### A.3 红线问题（一票否决）

- 认为 Redis 是多线程执行命令（混淆 6.0 多线程 IO）
- 不知道 Redis 数据在内存（基础缺失）
- 用 Redis 存大量数据不设过期（无运维意识）
- 分布式锁不设过期（基础缺失）
- 认为主从复制是同步的（不懂异步）

### A.4 加分项

- 量化数据（"单实例 QPS 8 万"、"内存 12.5MB"）
- 结合真实项目案例（背景 → 问题 → 方案 → 效果）
- 提到 Redis 7.x 新特性（listpack、多线程 IO、ACL）
- 横向对比其他缓存（Memcached、Caffeine）
- 提到源码层理解（`evict.c`、`t_string.c`）
- 容灾与高可用设计（多机房、灾备）

### A.5 备考察重点

面试前重点准备：
1. **单线程模型 + 6.0 多线程**（必考）
2. **五种数据类型 + 底层编码**（必考）
3. **RDB/AOF + 混合持久化**（高频）
4. **主从 + 哨兵 + Cluster**（高频）
5. **缓存穿透/击穿/雪崩**（高频）
6. **分布式锁 + Redlock**（高频）
7. **bigkey/hotkey 优化**（中频）
8. **排行榜/限流/消息队列**（中频）

建议每题准备一个**真实项目案例**：项目背景 → 技术选型原因 → 实现步骤 → 挑战与解决 → 最终效果。

---

## 参考资料

- 官方文档：[Redis Documentation](https://redis.io/docs/)
- 《Redis 设计与实现》—— 黄健宏
- 《Redis 开发与运维》—— 付磊
- 《Redis 实战》—— Josiah L. Carlson
- Redis 源码：https://github.com/redis/redis
- Redisson 文档：https://redisson.org/
- antirez 博客：http://antirez.com/

---

> **文档说明**：本面试题集共 8 大篇章、30+ 道题目，覆盖 Redis 高级工程师所需的核心知识体系。所有题目均附问题描述、深度参考答案、实际项目案例与评分要点，适合面试备战、知识梳理、团队培训等场景。建议结合源码阅读与生产实践，从"会用 Redis"进阶到"懂 Redis"。
