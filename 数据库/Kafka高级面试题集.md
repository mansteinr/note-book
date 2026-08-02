# Kafka 高级工程师面试题集

> 本面试题集面向 Kafka 高级工程师岗位，系统覆盖架构原理、生产者与消费者、分区策略、高可用设计、数据一致性保证、性能优化、实际应用场景等七大核心领域。每道题包含问题描述、深度参考答案、实际业务场景案例（问题背景→解决方案→实施步骤→效果评估）及评分要点，兼顾理论深度与工程实践。

---

## 目录

- [第一篇 架构原理](#第一篇-架构原理)
- [第二篇 生产者与消费者](#第二篇-生产者与消费者)
- [第三篇 分区策略](#第三篇-分区策略)
- [第四篇 高可用设计](#第四篇-高可用设计)
- [第五篇 数据一致性保证](#第五篇-数据一致性保证)
- [第六篇 性能优化](#第六篇-性能优化)
- [第七篇 实际应用场景](#第七篇-实际应用场景)
- [附录 评分标准与面试指南](#附录-评分标准与面试指南)

---

## 第一篇 架构原理

### Q1.1 请详细描述 Kafka 的整体架构，以及核心概念（Broker、Topic、Partition、Replica、Producer、Consumer、Consumer Group、ZooKeeper/KRaft）之间的关系。

**问题描述**：请说明 Kafka 的整体架构设计，以及各核心组件的协作关系。

**参考答案**：

**1. Kafka 整体架构**

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Kafka 集群                                    │
│                                                                     │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐                       │
│   │ Broker 0 │   │ Broker 1 │   │ Broker 2 │   ... N 个 Broker     │
│   │ (Leader) │   │(Follower)│   │ (Leader) │                       │
│   │ P0,P2    │   │ P0,P1,P2 │   │ P1       │                       │
│   └────┬─────┘   └────┬─────┘   └────┬─────┘                       │
│        └──────────────┴──────────────┘                              │
│                        │                                            │
│                        ▼                                            │
│   ┌──────────────────────────────────────┐                          │
│   │  Controller（某个 Broker 选举产生）   │                          │
│   │  管理分区/副本状态、Leader 选举       │                          │
│   └──────────────────────────────────────┘                          │
│                        │                                            │
│                        ▼                                            │
│   ┌──────────────────────────────────────┐                          │
│   │  ZooKeeper / KRaft（元数据存储）      │                          │
│   │  选举、配置、集群元数据               │                          │
│   └──────────────────────────────────────┘                          │
└─────────────────────────────────────────────────────────────────────┘
         ▲                                    ▲
         │                                    │
   ┌─────┴─────┐                       ┌──────┴──────┐
   │ Producer  │                       │  Consumer   │
   │ (生产者)  │                       │  Group      │
   └───────────┘                       │ ┌─────────┐ │
                                       │ │Consumer1│ │
                                       │ │Consumer2│ │
                                       │ │Consumer3│ │
                                       │ └─────────┘ │
                                       └─────────────┘
```

**2. 核心概念**

| 概念 | 说明 |
| --- | --- |
| **Broker** | Kafka 节点，多个 Broker 组成集群，负责消息存储与转发 |
| **Topic** | 消息主题，逻辑分类，类似数据库表 |
| **Partition** | 分区，Topic 的物理分片，是并行度的基本单位 |
| **Replica** | 副本，每个分区有多个副本，分 Leader 和 Follower |
| **Producer** | 生产者，发布消息到 Topic |
| **Consumer** | 消费者，从 Topic 拉取消息 |
| **Consumer Group** | 消费者组，组内消费者分摊分区，组间广播 |
| **Offset** | 消息在分区中的位置标识 |

**3. 关键关系**

- **Topic → Partition**：一个 Topic 分为多个 Partition，分布在不同 Broker 上
- **Partition → Replica**：每个 Partition 有 N 个副本（ replication.factor），1 个 Leader + N-1 Follower
- **Consumer Group → Partition**：组内一个 Partition 只能被一个 Consumer 消费，组间独立
- **Producer → Leader**：生产者只与分区的 Leader 通信，Follower 从 Leader 拉取数据

**4. ZooKeeper 与 KRaft**

- **ZooKeeper（传统）**：存储集群元数据、Controller 选举、Broker 注册、消费者 offset（旧版）
- **KRaft（2.8+）**：Kafka 自研元数据管理，替代 ZooKeeper，元数据以日志形式存于内部 Topic

**KRaft 优势**：
- 减少外部依赖，架构简化
- 元数据操作性能提升
- 支持更大规模集群

**5. 一条消息的完整流转**

```
1. Producer 根据 Key 计算分区：partition = hash(key) % numPartitions
2. Producer 连接该分区的 Leader Broker
3. Leader 将消息追加到本地日志
4. Follower 从 Leader 拉取消息
5. 所有 ISR 副本同步后，Leader 更新 HW（High Watermark）
6. Producer 收到 ack
7. Consumer 从 Leader 拉取消息（offset <= HW 可见）
```

**实际业务场景案例**：

- **问题背景**：某电商订单系统，日均订单 5000 万，原用 RabbitMQ 处理订单消息，高峰期消息堆积严重，扩展性差
- **解决方案**：迁移到 Kafka，按业务拆分 Topic（order-create、order-pay、order-ship）
- **实施步骤**：
  1. 搭建 6 节点 Kafka 集群（3 Broker + 3 ZK）
  2. 设计 Topic：`order-create`（12 分区，3 副本）、`order-pay`（6 分区，3 副本）
  3. 生产者按 order_id 做 Key，保证同一订单消息有序
  4. 消费者组按业务隔离：订单服务、支付服务、物流服务各自独立消费组
- **效果评估**：吞吐量从 5 万 TPS 提升到 30 万 TPS，消息堆积清零，水平扩展能力大幅提升

**评分要点**：
- ✅ 准确描述架构与核心概念（必备）
- ✅ Producer 只连 Leader、Follower 拉取同步（必备）
- ✅ Consumer Group 内分区独占、组间广播（核心）
- ✅ KRaft 替代 ZooKeeper（加分）
- ✅ 消息完整流转链路（加分）

---

### Q1.2 Kafka 的日志存储结构是怎样的？如何通过索引实现快速查找？

**问题描述**：请说明 Kafka 消息存储格式与索引机制。

**参考答案**：

**1. 日志存储结构**

```
Topic: order-create  Partition: 0
└── /kafka-logs/order-create-0/
    ├── 00000000000000000000.log          ← 日志段（实际消息）
    ├── 00000000000000000000.index        ← 偏移量索引
    ├── 00000000000000000000.timeindex    ← 时间戳索引
    ├── 00000000000005367851.log          ← 下一个日志段
    ├── 00000000000005367851.index
    ├── 00000000000005367851.timeindex
    └── leader-epoch-checkpoint            ← Leader 纪元检查点
```

**2. 日志段（LogSegment）**

- 每个 Partition 由多个 LogSegment 组成
- 当前活跃段（active segment）追加写入，写满（`log.segment.bytes` 默认 1GB）或超时（`log.segment.ms` 默认 7 天）后滚动新段
- 旧段可被删除或压缩

**3. 消息格式（RecordBatch）**

```
RecordBatch:
┌─────────────────────────────────────────────────┐
│ baseOffset │ length │ partitionLeaderEpoch │    │
│ magic      │ CRC    │ attributes           │    │
│ lastOffsetDelta │ baseTimestamp │ maxTimestamp │
│ producerId │ producerEpoch │ baseSequence    │
│ records count │                                   │
├─────────────────────────────────────────────────┤
│ Record 1: offsetDelta │ timestampDelta │        │
│           keyLength │ key │ valueLen │ value │  │
│           headers                             │  │
├─────────────────────────────────────────────────┤
│ Record 2: ...                                    │
└─────────────────────────────────────────────────┘
```

- 批量存储：多条消息打包成 RecordBatch，减少网络与存储开销
- 增量编码：offset、timestamp 用 delta 编码，节省空间

**4. 索引机制**

**偏移量索引（.index）**：

```
┌──────────────────┬──────────────────┐
│ relativeOffset   │ position         │
│ (相对偏移量)      │ (物理位置)        │
├──────────────────┼──────────────────┤
│ 0                │ 0                │
│ 100              │ 1520             │
│ 200              │ 3120             │
│ 356              │ 5480             │  ← 稀疏索引，每隔 4KB 一条
└──────────────────┴──────────────────┘
```

- **稀疏索引**：不是每条消息都有索引，默认每写入 4KB（`index.interval.bytes`）加一条
- 查找 offset=300 的消息：
  1. 二分查找索引，找到 ≤300 的最大索引项（offset=200, position=3120）
  2. 从 position=3120 顺序扫描 log 文件，找到 offset=300

**时间戳索引（.timeindex）**：

```
┌──────────────────┬──────────────────┐
│ timestamp        │ relativeOffset   │
├──────────────────┼──────────────────┤
│ 1628000000000    │ 0                │
│ 1628000005000    │ 100              │
│ 1628000010000    │ 200              │
└──────────────────┴──────────────────┘
```

- 按时间查找消息（如 `--from-timestamp`）
- 先在 timeindex 找到 timestamp 对应的 offset，再到 .index 找物理位置

**5. 查找流程**

```
查找 offset=12345 的消息：

1. 定位 LogSegment：找到 baseOffset ≤ 12345 的最大段
   └─ 段 00000000000000120000.log（baseOffset=12000）

2. 计算相对偏移量：12345 - 12000 = 345

3. 二分查找 .index：找 ≤345 的最大索引项
   └─ (relativeOffset=300, position=4800)

4. 顺序扫描 .log：从 position=4800 开始扫描，找到 offset=12345
```

**6. 零拷贝（Zero Copy）**

Kafka 用 `sendfile` 系统调用，消息从磁盘直接到网卡，无需经过用户空间：

```
传统方式：
磁盘 → 内核缓冲区 → 用户空间 → Socket 缓冲区 → 网卡
         (4 次拷贝，2 次系统调用)

零拷贝（sendfile）：
磁盘 → 内核缓冲区 → 网卡
         (2 次拷贝，1 次系统调用)
```

**实际业务场景案例**：

- **问题背景**：日志系统每日 100GB 日志，Kafka 存储压力大，查询特定时间日志慢
- **解决方案**：优化日志段与索引配置
- **实施步骤**：
  1. 日志段大小调到 512MB（`log.segment.bytes=536870912`），便于精准删除
  2. 索引间隔调到 4KB（默认），平衡查找速度与索引大小
  3. 按时间戳索引实现"按时间范围查询"
  4. 配置 `log.retention.hours=72`，3 天后自动清理
- **效果评估**：存储空间减少 40%，按 offset 查询 < 5ms，按时间查询 < 20ms

**评分要点**：
- ✅ LogSegment 滚动机制（必备）
- ✅ 稀疏索引原理（核心）
- ✅ 偏移量索引查找流程（必备）
- ✅ 时间戳索引（加分）
- ✅ 零拷贝 sendfile（加分）

---

### Q1.3 Kafka 的 Controller 机制是什么？如何实现 Leader 选举与故障转移？

**问题描述**：请说明 Controller 的职责、选举机制及故障处理流程。

**参考答案**：

**1. Controller 角色**

Controller 是集群中**某个 Broker** 选举产生的特殊角色，负责：

| 职责 | 说明 |
| --- | --- |
| **分区 Leader 选举** | Leader 宕机时，从 ISR 选新 Leader |
| **副本管理** | 监听副本上线/下线，更新元数据 |
| **Broker 上下线** | 监听 ZK 中 `/brokers/ids` 变化 |
| **Topic 管理** | 创建/删除 Topic，分配分区 |
| **Preferred Leader 选举** | 均衡 Leader 分布 |

**2. Controller 选举**

```
1. 所有 Broker 启动时尝试在 ZK 创建临时节点 /controller
2. 第一个创建成功的 Broker 成为 Controller
3. 其他 Broker 监听 /controller 节点变化
4. Controller 宕机，临时节点消失，触发新一轮选举
```

KRaft 模式下，Controller 节点通过 Raft 协议选举 Leader。

**3. 分区 Leader 选举流程**

```
Broker 1 宕机（原 Leader 在此）：
                    │
                    ▼
1. ZK 监听 /brokers/ids 变化，感知 Broker 1 下线
2. Controller 找出 Broker 1 上的所有 Leader 分区
3. 对每个分区，从 ISR（In-Sync Replicas）中选第一个作为新 Leader
4. Controller 更新 ZK 中的 Leader 状态
5. Controller 向所有 Broker 发送 LeaderAndIsrRequest
6. 生产者/消费者感知新 Leader，重新连接
```

**4. ISR 机制**

ISR（In-Sync Replicas）= 与 Leader 保持同步的副本集合：

```
Partition 的副本集合（AR）：
┌─────────────────────────────────────┐
│  Leader（Broker 0）                  │
│  ISR: Broker 0, Broker 1            │  ← 同步的副本
│  OSR: Broker 2（落后太多）           │  ← 不同步的副本
│  AR = ISR + OSR                      │
└─────────────────────────────────────┘
```

- Follower 从 Leader 拉取数据，落后超过 `replica.lag.time.max.ms`（默认 10s）被踢出 ISR
- 重新追上后重新加入 ISR
- Leader 选举**仅从 ISR 中选**（默认），保证数据不丢失

**5. Unclean Leader Election**

```
场景：ISR 只剩 Leader 一个，Leader 宕机
- unclean.leader.election.enable=false（默认）：
  分区不可用，等待原 Leader 恢复  ← 牺牲可用性保数据
- unclean.leader.election.enable=true：
  从非 ISR 副本选 Leader  ← 牺牲数据保可用性，可能丢消息
```

**6. Preferred Leader 选举**

集群运行一段时间后，Leader 可能集中在少数 Broker（如原 Leader 恢复后未夺回 Leader），导致负载不均。

```
Preferred Leader = 副本列表中的第一个副本
自动均衡：auto.leader.rebalance.enable=true（默认）
  - Controller 定期检查 Leader 分布
  - 若 preferred Leader 在 ISR 中且非当前 Leader，触发切换
```

**实际业务场景案例**：

- **问题背景**：金融交易消息系统，某次 Broker 宕机后，开启了 unclean 选举，导致 200 条交易消息丢失
- **解决方案**：严格关闭 unclean 选举，保证数据完整性
- **实施步骤**：
  1. `unclean.leader.election.enable=false`
  2. `min.insync.replicas=2`（至少 2 个 ISR 副本才允许写入）
  3. `replication.factor=3`（3 副本）
  4. 监控 ISR 数量，<2 时告警
- **效果评估**：后续多次 Broker 故障，零数据丢失，故障切换 < 10 秒

**评分要点**：
- ✅ Controller 职责与选举（必备）
- ✅ ISR 机制（必备）
- ✅ Leader 选举流程（必备）
- ✅ Unclean Leader Election 权衡（核心）
- ✅ Preferred Leader 均衡（加分）

---

## 第二篇 生产者与消费者

### Q2.1 Kafka 生产者发送消息的完整流程？ack 参数与重试机制如何配置？

**问题描述**：请描述生产者发送消息的流程，以及 acks、retries 等关键参数的配置。

**参考答案**：

**1. 生产者发送流程**

```
应用调用 send()
    │
    ▼
┌─────────────┐
│  拦截器链    │  ProducerInterceptor.onSend()
└──────┬──────┘
       ▼
┌─────────────┐
│  序列化器    │  Serializer，Key/Value → byte[]
└──────┬──────┘
       ▼
┌─────────────┐
│  分区器      │  Partitioner，决定发往哪个分区
│  - 有 Key：hash(key) % numPartitions        │
│  - 无 Key：轮询 / 粘性分区（2.4+）           │
└──────┬──────┘
       ▼
┌─────────────┐
│  消息累加器  │  RecordAccumulator，按分区攒批
│  (缓冲区)    │  buffer.memory=32MB
│              │  batch.size=16KB
└──────┬──────┘
       ▼
┌─────────────┐
│  Sender 线程 │  后台线程，将 batch 发往 Broker
│              │  linger.ms=0（立即发）
│              │  max.in.flight.requests.per.connection=5
└──────┬──────┘
       ▼
┌─────────────┐
│  Broker      │  Leader 处理写入，Follower 同步
└──────┬──────┘
       ▼
┌─────────────┐
│  回调        │  Callback.onCompletion()
│              │  失败 → 重试（retries）
└─────────────┘
```

**2. acks 参数**

| acks | 含义 | 可靠性 | 性能 | 适用场景 |
| --- | --- | --- | --- | --- |
| `0` | 不等任何确认 | 最低（可能丢） | 最高 | 日志采集，可容忍丢失 |
| `1` | 等 Leader 确认 | 中（Leader 故障可能丢） | 较高 | 一般业务 |
| `all`/`-1` | 等 ISR 全部确认 | 高（不丢） | 较低 | 金融、订单等关键业务 |

**acks=all 的完整含义**：
- Leader 写入后，等待所有 ISR 副本同步
- 配合 `min.insync.replicas`：要求 ISR 至少 N 个副本，否则拒绝写入

```properties
# 生产者
acks=all
# Broker
min.insync.replicas=2
replication.factor=3
# 含义：3 副本中至少 2 个同步成功才算写入成功
```

**3. 重试机制**

```properties
# 重试次数（2.1+ 默认 Integer.MAX_VALUE）
retries=3
# 重试间隔
retry.backoff.ms=100
# 消息投递超时（包含重试时间）
delivery.timeout.ms=120000
# 请求超时
request.timeout.ms=30000
```

**重试的副作用——消息乱序**：

```
场景：max.in.flight.requests.per.connection=5，retries>0
1. 发送 msg1（batch1）→ 失败，重试中
2. 发送 msg2（batch2）→ 成功
3. msg1 重试成功
结果：msg2 先于 msg1 写入，乱序！

解决：
- 方案1：max.in.flight.requests.per.connection=1（牺牲并发）
- 方案2：开启幂等性（enable.idempotence=true），自动保证顺序
```

**4. 幂等性生产者**

```properties
enable.idempotence=true
```

- 2.8+ 默认开启
- 为每个 Producer 分配 PID（Producer ID）
- 每条消息带 SequenceNumber
- Broker 根据 <PID, Partition, SequenceNumber> 去重

**5. 关键参数汇总**

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `acks` | all（2.8+） | 确认级别 |
| `retries` | MAX_INT | 重试次数 |
| `batch.size` | 16KB | 批次大小 |
| `linger.ms` | 0 | 等待攒批时间 |
| `buffer.memory` | 32MB | 缓冲区总大小 |
| `compression.type` | none | 压缩（lz4/snappy/gzip/zstd） |
| `max.in.flight.requests.per.connection` | 5 | 每连接未确认请求数 |
| `enable.idempotence` | true（2.8+） | 幂等性 |

**实际业务场景案例**：

- **问题背景**：订单创建消息，原 acks=1，Broker Leader 故障时丢失 100 条订单
- **解决方案**：配置 acks=all + 幂等性 + 重试
- **实施步骤**：
  1. 生产者：`acks=all`、`enable.idempotence=true`、`retries=3`、`max.in.flight.requests.per.connection=5`
  2. Broker：`min.insync.replicas=2`、`replication.factor=3`
  3. 监控 `record-error-rate`，异常告警
- **效果评估**：3 个月运行零消息丢失，发送延迟从 2ms 增到 5ms，可接受

**评分要点**：
- ✅ 发送流程（拦截器→序列化→分区→攒批→发送）（必备）
- ✅ acks 三种值区别（必备）
- ✅ acks=all 配合 min.insync.replicas（核心）
- ✅ 重试导致乱序与幂等性解决（必备）
- ✅ 关键参数调优（加分）

---

### Q2.2 Kafka 消费者组（Consumer Group）机制？Rebalance 如何触发？有何问题与优化？

**问题描述**：请说明 Consumer Group 工作原理、Rebalance 触发条件与优化方案。

**参考答案**：

**1. Consumer Group 机制**

```
Topic: order（3 分区 P0/P1/P2）

Consumer Group A（订单服务）：
┌─────────────┬─────────────┬─────────────┐
│ Consumer 1  │ Consumer 2  │ Consumer 3  │
│   P0        │   P1        │   P2        │  ← 每个 Consumer 消费 1 分区
└─────────────┴─────────────┴─────────────┘

Consumer Group B（数据分析）：
┌─────────────┬─────────────┐
│ Consumer 4  │ Consumer 5  │
│   P0,P1     │   P2        │  ← 2 个 Consumer 分 3 分区
└─────────────┴─────────────┘
```

- **组内**：一个分区只能被一个消费者消费（独占）
- **组间**：各组独立消费全量消息（广播）
- **消费进度独立**：每组维护自己的 offset

**2. Rebalance 触发条件**

| 触发条件 | 说明 |
| --- | --- |
| **消费者加入** | 新消费者加入组 |
| **消费者离开** | 消费者主动关闭或被判定宕机（`session.timeout.ms`） |
| **消费者心跳超时** | `session.timeout.ms` 内未收到心跳 |
| **分区数变化** | Topic 分区增加 |
| **订阅 Topic 变化** | 正则订阅，新建匹配 Topic |

**3. Rebalance 流程**

```
1. 消费者发送 JoinGroupRequest 给 Group Coordinator
2. Coordinator 选一个 Consumer 作为 Leader
3. Leader 根据分配策略制定分区分配方案
4. Leader 发送 SyncGroupRequest（含分配方案）
5. Coordinator 把方案分发给所有 Consumer
6. 各 Consumer 按新方案消费

期间：所有消费者停止消费（Stop The World），等待 Rebalance 完成
```

**4. 分区分配策略**

| 策略 | 说明 |
| --- | --- |
| **Range（默认）** | 按分区范围分配，可能不均（多 Topic 时） |
| **RoundRobin** | 轮询分配所有分区，较均匀 |
| **Sticky** | 尽量保持原分配，减少迁移 |
| **CooperativeSticky（2.4+）** | 增量 Rebalance，不停止消费 |

**5. Rebalance 的问题**

**Stop The World**：Rebalance 期间所有消费者暂停消费，可能持续数十秒。

**Rebalance 风暴**：消费者频繁上下线（如 GC 停顿），反复触发 Rebalance。

**优化方案**：

```properties
# 心跳与超时
session.timeout.ms=30000          # 心跳超时（30s）
heartbeat.interval.ms=10000       # 心跳间隔（10s）
max.poll.interval.ms=300000       # 两次 poll 最大间隔（5 分钟）

# 消费控制
max.poll.records=500              # 单次 poll 最大记录数

# 分配策略
partition.assignment.strategy=org.apache.kafka.clients.consumer.CooperativeStickyAssignor
```

**6. 避免不必要的 Rebalance**

```java
// 消费者优雅退出
Runtime.getRuntime().addShutdownHook(new Thread(() -> {
    consumer.close();  // 主动离开，触发一次性 Rebalance
}));

// 处理慢导致 max.poll.interval.ms 超时
// 方案1：减少 max.poll.records，单批处理快
// 方案2：异步处理 + 手动提交 offset
// 方案3：调大 max.poll.interval.ms
```

**7. Offset 管理**

```java
// 自动提交（可能重复消费或丢失）
enable.auto.commit=true
auto.commit.interval.ms=5000

// 手动提交（推荐）
enable.auto.commit=false
// 同步提交（阻塞，可靠）
consumer.commitSync();
// 异步提交（非阻塞，可能失败）
consumer.commitAsync((offsets, exception) -> {
    if (exception != null) log.error("提交失败", exception);
});
```

**实际业务场景案例**：

- **问题背景**：订单消费服务，每次发布新版本触发 Rebalance，期间消费暂停 30 秒，消息堆积
- **解决方案**：增量 Rebalance + 优雅退出
- **实施步骤**：
  1. 分配策略改为 `CooperativeStickyAssignor`，仅迁移变更的分区
  2. 退出时先 `consumer.wakeup()`，等待处理完再 close
  3. `max.poll.interval.ms` 调到 5 分钟，避免处理慢被踢
  4. `max.poll.records` 从 1000 调到 200，单批处理更快
- **效果评估**：Rebalance 期间消费不中断，发布对业务零影响，消息堆积清零

**评分要点**：
- ✅ 组内独占、组间广播（必备）
- ✅ Rebalance 触发条件（必备）
- ✅ Stop The World 问题（核心）
- ✅ CooperativeStickyAssignor 增量 Rebalance（加分）
- ✅ 参数调优避免误踢（必备）

---

### Q2.3 Kafka 消息投递语义有哪些？如何实现 Exactly-Once？

**问题描述**：请说明三种投递语义及 Exactly-Once 的实现方案。

**参考答案**：

**1. 三种投递语义**

| 语义 | 含义 | 实现 |
| --- | --- | --- |
| **At Most Once** | 至多一次，可能丢 | acks=0，自动提交 offset（先提交后处理） |
| **At Least Once** | 至少一次，可能重复 | acks=all，手动提交 offset（先处理后提交） |
| **Exactly Once** | 恰好一次，不丢不重 | 幂等生产者 + 事务 |

**2. At Least Once（最常用）**

```
1. 消费者拉取消息
2. 处理业务逻辑
3. 提交 offset

问题：步骤 2 成功、步骤 3 失败 → 重新消费 → 重复
解决：业务幂等（如数据库唯一约束、Redis 去重）
```

**3. 幂等性生产者（单分区 Exactly-Once）**

```properties
enable.idempotence=true
```

- Producer 分配 PID + SequenceNumber
- Broker 去重：同一 <PID, Partition, SeqNum> 的重复消息被丢弃
- **限制**：仅保证单分区单会话不重复，跨分区/跨会话需事务

**4. 事务（跨分区 Exactly-Once）**

```properties
transactional.id=my-transactional-producer
enable.idempotence=true
```

```java
// 事务生产者
producer.initTransactions();  // 初始化事务

try {
    producer.beginTransaction();
    
    // 发送多条消息到不同分区/Topic
    producer.send(new ProducerRecord<>("topic1", "k1", "v1"));
    producer.send(new ProducerRecord<>("topic2", "k2", "v2"));
    
    // 提交消费者的 offset（将 offset 提交纳入事务）
    producer.sendOffsetsToTransaction(
        Collections.singletonMap(
            new TopicPartition("source-topic", 0),
            new OffsetAndMetadata(lastConsumedOffset)
        ),
        consumer.groupMetadata()
    );
    
    producer.commitTransaction();  // 提交事务
} catch (Exception e) {
    producer.abortTransaction();  // 回滚事务
}
```

**事务原理**：

```
1. Producer 向 TransactionCoordinator 注册 transactional.id
2. TransactionCoordinator 分配 epoch，记录事务状态
3. Producer 发送消息前，向 Coordinator 标记"事务开始"
4. 消息带有事务标记（begin/commit/abort）
5. 消费者根据 isolation.level 决定是否读未提交事务：
   - read_uncommitted（默认）：读所有消息
   - read_committed：只读已提交事务的消息
6. Producer commit/abort → Coordinator 更新事务状态
7. Coordinator 向各 Broker 发送 TransactionMarker（commit/abort）
8. Broker 标记消息可见性
```

**5. Kafka Streams 的 Exactly-Once**

```properties
processing.guarantee=exactly_once_v2  # 2.5+ 推荐版本
```

- 内部自动用事务保证处理一次
- 适合流处理场景（消费 → 处理 → 生产）

**6. Exactly-Once 的限制**

| 限制 | 说明 |
| --- | --- |
| **仅 Kafka 内部** | 消费 Kafka → 处理 → 生产 Kafka，可保证 |
| **外部系统不保证** | 如写 MySQL，需业务幂等 |
| **性能开销** | 事务降低吞吐约 20-30% |

**实际业务场景案例**：

- **问题背景**：支付系统，消费订单消息 → 处理 → 写入支付 Topic，原 At Least Once 导致重复扣款
- **解决方案**：Kafka 事务保证消费-处理-生产 Exactly-Once
- **实施步骤**：
  1. 生产者配置 `transactional.id=pay-service-1`、`enable.idempotence=true`
  2. 消费者 `isolation.level=read_committed`
  3. 代码：消费消息 → 开启事务 → 写支付 Topic → 提交消费 offset → commit
  4. 对外写入 MySQL 仍用幂等（订单号唯一索引）兜底
- **效果评估**：重复扣款清零，吞吐从 1 万 TPS 降到 8000，业务可接受

**评分要点**：
- ✅ 三种投递语义（必备）
- ✅ 幂等性 PID + SequenceNumber（核心）
- ✅ 事务 API 使用（必备）
- ✅ isolation.level=read_committed（必备）
- ✅ Exactly-Once 仅限 Kafka 内部（加分）

---

## 第三篇 分区策略

### Q3.1 Kafka 的分区数如何选择？过多过少有什么问题？

**问题描述**：请说明分区数选择的原则，以及过多/过少的危害。

**参考答案**：

**1. 分区的作用**

- **并行度**：分区是 Kafka 并行的基本单位，分区数 = 最大消费者并发数
- **吞吐量**：分区分布在多个 Broker，提升整体吞吐
- **负载均衡**：消息分散到不同分区，避免热点

**2. 分区数选择公式**

```
分区数 = max(目标吞吐量 / 单分区吞吐量, 目标消费者并发数)

示例：
- 目标吞吐量：100 MB/s
- 单分区吞吐量：10 MB/s（生产）+ 20 MB/s（消费）
- 则生产侧分区数 ≥ 100/10 = 10
- 消费侧分区数 ≥ 100/20 = 5
- 取大值：≥ 10 个分区
```

**3. 分区过少的问题**

- **吞吐瓶颈**：消费者并行度受限，无法水平扩展
- **单分区数据量大**：日志段大，清理慢，查询慢

**4. 分区过多的问题**

| 问题 | 说明 |
| --- | --- |
| **Broker 元数据开销** | 每个分区在 ZK/KRaft 存元数据，分区数 × 副本数过多导致元数据膨胀 |
| **文件句柄** | 每个分区对应多个文件（.log/.index/.timeindex），过多耗尽 fd |
| **内存开销** | 消费者每个分区有缓冲区，分区多内存占用大 |
| **Rebalance 慢** | 分区多，分配计算慢，Rebalance 耗时长 |
| **端到端延迟** | 分区多，单个分区数据稀疏，攒批效果差，延迟增加 |

**5. 分区数经验值**

- 单 Broker 分区数建议 < 4000（含副本）
- 集群总分区数建议 < 200,000
- 单 Topic 分区数：小规模 6-12，中规模 24-48，大规模 100+

**6. 分区扩容注意事项**

```bash
# 扩容分区（只能增加，不能减少）
kafka-topics.sh --alter --topic order --partitions 24
```

**重要**：扩容后，有 Key 的消息路由可能变化：
- 原 12 分区：`hash(key) % 12`
- 扩容到 24 分区：`hash(key) % 24`
- 同一 Key 可能从 P0 变到 P13，**破坏顺序性**

**解决方案**：
- 提前规划分区数，预留扩容空间
- 如必须保证顺序，新建 Topic 重导数据
- 用自定义分区器，基于一致性哈希

**7. 分区与 Key 的关系**

```
有 Key：partition = hash(key) % numPartitions
  - 同 Key 永远进同一分区（分区数不变时）
  - 适合需顺序的场景（如订单 ID）

无 Key：
  - 2.4 前：轮询（RoundRobin）
  - 2.4+：粘性分区（Sticky Partitioner）
    - 攒批时固定一个分区，batch 满或 linger.ms 到再换
    - 提升攒批率，减少小批次
```

**实际业务场景案例**：

- **问题背景**：日志 Topic 原设 6 分区，业务量增长后消费跟不上，单分区 100 万消息积压
- **解决方案**：扩容分区 + 调整消费者并发
- **实施步骤**：
  1. 评估目标吞吐量 20 万 TPS，单分区 2 万 TPS → 需 10 分区，预留扩容到 16
  2. 扩容：`--partitions 16`
  3. 消费者从 6 个扩到 16 个
  4. 日志无 Key（不要求顺序），路由变化无影响
- **效果评估**：积压清零，吞吐提升 2.5 倍

**评分要点**：
- ✅ 分区数选择公式（必备）
- ✅ 分区过多的 5 个问题（必备）
- ✅ 分区扩容破坏 Key 顺序（核心）
- ✅ 粘性分区器（加分）
- ✅ 实际容量规划（加分）

---

### Q3.2 如何保证 Kafka 消息的顺序性？多分区的全局有序如何实现？

**问题描述**：请说明 Kafka 顺序消息的实现方案与权衡。

**参考答案**：

**1. Kafka 顺序保证层次**

| 层次 | 保证 |
| --- | --- |
| **单分区** | 分区内消息严格有序（按写入顺序） |
| **多分区** | 不保证全局有序 |
| **多 Topic** | 不保证 |

**2. 单分区顺序**

```
Producer 写入：msg1 → msg2 → msg3
Partition 内顺序：msg1, msg2, msg3
Consumer 按序消费：msg1 → msg2 → msg3
```

**前提**：
- 生产者用相同 Key（路由到同一分区）
- `max.in.flight.requests.per.connection=1` 或开启幂等性（防重试乱序）
- 消费者单线程消费该分区

**3. 多分区全局有序方案**

**方案1：单分区 Topic**

```
Topic: order（1 个分区）
所有消息进同一分区，全局有序
```

- 优点：简单
- 缺点：**无并行度**，吞吐极低，不适合高吞吐场景

**方案2：按业务 Key 分区，组内有序**

```
Topic: order（10 分区）
Producer 用 order_id 做 Key：
  - order_1 → P3（hash 后）
  - order_2 → P7
  - 同一订单的所有消息（创建/支付/发货）进同一分区，保证该订单事件有序
```

- 优点：兼顾顺序与并行度
- 缺点：不同订单间无序

**方案3：多分区 + 序列号 + 消费者缓冲重排**

```
1. Producer 为每条消息加全局序列号（如 Snowflake ID）
2. 消费者拉取后，按序列号排序
3. 缺号则缓冲等待
```

- 优点：多分区实现"近似全局有序"
- 缺点：复杂，延迟高，仅特殊场景用

**4. 消费者侧保序消费**

```java
// 单消费者单线程消费一个分区（天然有序）
while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<String, String> record : records) {
        process(record);  // 顺序处理
    }
}

// 多线程消费的顺序问题
// ❌ 直接多线程处理：破坏顺序
for (ConsumerRecord<String, String> record : records) {
    executor.submit(() -> process(record));  // 乱序！
}

// ✅ 按 Key 分发到固定线程
Map<String, ExecutorService> executors = new ConcurrentHashMap<>();
for (ConsumerRecord<String, String> record : records) {
    String key = record.key();
    ExecutorService exec = executors.computeIfAbsent(key, 
        k -> Executors.newSingleThreadExecutor());
    exec.submit(() -> process(record));  // 同 Key 同线程，保序
}
```

**5. 实际场景：订单状态变更顺序**

```
订单 123 的事件：
1. order_created（order_id=123）
2. order_paid（order_id=123）
3. order_shipped（order_id=123）

必须按 1→2→3 顺序处理，否则状态错乱

方案：用 order_id=123 做 Key，所有事件进同一分区
```

**实际业务场景案例**：

- **问题背景**：订单状态机，消费乱序导致"已发货"先于"已支付"处理，状态错误
- **解决方案**：按订单 ID 分区保证同订单有序
- **实施步骤**：
  1. Topic `order-event` 24 分区
  2. 生产者用 `order_id` 做 Key，同订单事件进同分区
  3. 消费者单线程消费每分区，按 offset 顺序处理
  4. 多线程优化：按 order_id hash 分发到固定线程
- **效果评估**：状态错乱清零，吞吐通过多分区并行保证（24 分区 24 并发）

**评分要点**：
- ✅ 单分区有序、多分区无序（必备）
- ✅ 按 Key 分区保证组内有序（核心）
- ✅ max.in.flight 或幂等性防乱序（必备）
- ✅ 消费者多线程保序方案（加分）
- ✅ 全局有序的代价（加分）

---

## 第四篇 高可用设计

### Q4.1 Kafka 的高可用机制？HW、LEO、ISR 是什么？

**问题描述**：请详细说明 Kafka 的副本同步机制及 HW/LEO 的作用。

**参考答案**：

**1. 核心概念**

| 概念 | 全称 | 说明 |
| --- | --- | --- |
| **LEO** | Log End Offset | 每个副本的日志末端 offset（下一条写入位置） |
| **HW** | High Watermark | 所有 ISR 副本中最小的 LEO，消费者只能读 offset < HW 的消息 |
| **ISR** | In-Sync Replicas | 与 Leader 保持同步的副本集合 |

**2. 副本同步流程**

```
Leader (LEO=10)        Follower1 (LEO=8)     Follower2 (LEO=9)
     │                       │                       │
     │   ◄── 拉取 offset=8 ──│                       │
     │   ── 返回消息 ────────►│                       │
     │                       │ Follower1 LEO=9        │
     │   ◄── 拉取 offset=9 ──────────────────────────│
     │   ── 返回消息 ────────────────────────────────►│
     │                                                │ Follower2 LEO=10
     │                                                │
     │ HW = min(Leader LEO, Follower1 LEO, Follower2 LEO)
     │ HW = min(10, 9, 10) = 9
     │ 消费者只能读 offset < 9 的消息
```

**3. Follower 同步机制**

- Follower **主动拉取**（Pull）Leader 数据，非 Leader 推送
- Follower 维护自己的 LEO，每次拉取时告诉 Leader 自己的 LEO
- Leader 根据 Follower LEO 更新 HW

**4. HW 的更新**

```
Leader 维护每个 Follower 的 LEO：
- Follower1 LEO = 8
- Follower2 LEO = 9
- Leader LEO = 10

HW = min(所有 ISR 副本的 LEO) = 8

Follower1 继续拉取，LEO 变为 9：
HW = min(10, 9, 9) = 9  ← HW 前进

HW 更新频率：replica.fetch.min.bytes、replica.fetch.wait.max.ms
```

**5. Leader 故障切换**

```
Leader 宕机：
1. Controller 从 ISR 选新 Leader
2. 新 Leader 的 LEO 可能 < 旧 HW（数据可能丢失）

旧 Leader（LEO=10，HW=9）宕机
新 Leader（原 Follower2，LEO=9）
1. 新 Leader 截断日志到 HW（offset 9 之后的消息丢弃）
2. 原 Leader 恢复后作为 Follower，截断到 HW，从新 Leader 同步
```

**6. Leader Epoch 机制（解决 HW 截断丢数据问题）**

旧版基于 HW 截断有"数据丢失"和"数据不一致"问题，2.0+ 引入 Leader Epoch：

```
Leader Epoch = (epoch, startOffset)
- epoch：Leader 纪元，每次切主递增
- startOffset：该 epoch 的起始 offset

Follower 重启后：
1. 向 Leader 发送 OffsetsForLeaderEpochRequest(epoch)
2. Leader 返回该 epoch 的 endOffset
3. Follower 截断到 endOffset（而非 HW）

优势：
- 避免基于 HW 截断导致的数据丢失
- 更精确的日志对齐
```

**7. ISR 动态调整**

```
Follower 滞后 > replica.lag.time.max.ms（默认 10s）：
  - 从 ISR 移除，加入 OSR
  - Leader 不再等它，HW 可能前进

Follower 追上 Leader：
  - 从 OSR 加入 ISR
  - Leader 等待其确认
```

**8. 高可用配置**

```properties
# Broker
replication.factor=3                    # 3 副本
min.insync.replicas=2                   # 至少 2 个同步
unclean.leader.election.enable=false    # 禁止非 ISR 选举
default.replication.factor=3

# Topic 创建
kafka-topics.sh --create --topic order \
  --partitions 12 --replication-factor 3 \
  --config min.insync.replicas=2
```

**实际业务场景案例**：

- **问题背景**：3 副本集群，Broker 故障后消费者重复消费（HW 截断导致）
- **解决方案**：升级 Kafka 版本启用 Leader Epoch
- **实施步骤**：
  1. 升级到 Kafka 2.5+，Leader Epoch 默认启用
  2. 配置 `replication.factor=3`、`min.insync.replicas=2`
  3. `unclean.leader.election.enable=false`
  4. 监控 ISR 收缩告警
- **效果评估**：故障切换后无重复消费，数据一致，切换时间 < 10 秒

**评分要点**：
- ✅ LEO/HW/ISR 定义（必备）
- ✅ Follower 主动拉取同步（必备）
- ✅ HW 更新机制（核心）
- ✅ Leader Epoch 解决截断问题（加分）
- ✅ 高可用配置（必备）

---

## 第五篇 数据一致性保证

### Q5.1 如何保证 Kafka 消息不丢失？生产者、Broker、消费者各需如何配置？

**问题描述**：请从三个层面说明 Kafka 消息不丢失的配置方案。

**参考答案**：

**1. 消息丢失场景**

```
生产者 → Broker → 消费者
  │         │         │
  │         │         └─ 消费者：拉取后未处理完就提交 offset → 丢
  │         └─ Broker：Leader 写入未同步，Leader 故障 → 丢
  └─ 生产者：acks=0 或网络异常 → 丢
```

**2. 生产者层面**

```properties
# 确认所有 ISR 副本
acks=all

# 重试
retries=2147483647            # 无限重试（2.1+ 默认）
delivery.timeout.ms=120000    # 总投递超时
retry.backoff.ms=100          # 重试间隔

# 幂等性（防重试重复）
enable.idempotence=true

# 异步发送变同步（极端可靠场景）
# producer.send(record).get();  // 同步等待
```

**3. Broker 层面**

```properties
# 副本数
replication.factor=3              # 至少 3 副本

# 最少同步副本
min.insync.replicas=2             # 至少 2 个 ISR 才允许写

# 禁止非 ISR 选举
unclean.leader.election.enable=false

# 刷盘策略（权衡性能与可靠）
log.flush.interval.messages=10000   # 每 1 万条刷盘
log.flush.interval.ms=1000          # 每 1 秒刷盘
# 注意：Kafka 默认依赖 OS page cache 刷盘，强制刷盘降低性能
```

**4. 消费者层面**

```properties
# 关闭自动提交
enable.auto.commit=false

# 手动提交（处理完后）
# consumer.commitSync();
```

```java
// 处理 + 提交的可靠模式
try {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<String, String> record : records) {
        process(record);  // 业务处理
    }
    consumer.commitSync();  // 处理完同步提交
} catch (Exception e) {
    log.error("处理失败，不提交 offset，下次重新消费", e);
    // 不提交，下次 poll 会重新拉取
}
```

**5. 端到端不丢失检查清单**

| 层面 | 配置 | 说明 |
| --- | --- | --- |
| 生产者 | `acks=all` | ISR 全确认 |
| 生产者 | `retries=MAX` | 失败重试 |
| 生产者 | `enable.idempotence=true` | 防重试重复 |
| Broker | `replication.factor=3` | 多副本 |
| Broker | `min.insync.replicas=2` | 至少 2 同步 |
| Broker | `unclean.leader.election.enable=false` | 禁非 ISR 选举 |
| 消费者 | `enable.auto.commit=false` | 手动提交 |
| 消费者 | 处理后 `commitSync()` | 处理完才提交 |

**6. 不丢失 vs 性能权衡**

```
高可靠配置：
- acks=all + 3 副本 + min.insync.replicas=2
- 吞吐：约 50% of acks=1
- 延迟：增加 2-5ms（等 Follower 同步）

高吞吐配置（可容忍少量丢失）：
- acks=1 + 2 副本
- 吞吐：高
- 适合日志采集
```

**实际业务场景案例**：

- **问题背景**：金融交易系统，某次 Broker 故障丢失 500 条交易，导致对账异常
- **解决方案**：端到端不丢失配置
- **实施步骤**：
  1. 生产者：`acks=all`、`retries=MAX`、`enable.idempotence=true`
  2. Broker：`replication.factor=3`、`min.insync.replicas=2`、`unclean.leader.election.enable=false`
  3. 消费者：`enable.auto.commit=false`，处理后 `commitSync()`
  4. 业务层：数据库唯一索引兜底（防重复处理）
  5. 监控：`record-error-rate`、ISR 收缩、消费延迟
- **效果评估**：3 个月零丢失，吞吐降低约 30%，业务可接受

**评分要点**：
- ✅ 三层丢失场景（必备）
- ✅ 生产者 acks=all + 重试 + 幂等（必备）
- ✅ Broker min.insync.replicas + 禁 unclean（核心）
- ✅ 消费者手动提交（必备）
- ✅ 性能权衡（加分）

---

### Q5.2 Kafka 事务的原理？如何实现跨分区 Exactly-Once？

**问题描述**：请详细说明 Kafka 事务机制的实现原理。

**参考答案**：

**1. 事务场景**

```
消费-处理-生产（Consume-Process-Produce）：
  消费 Topic A → 处理 → 生产 Topic B + 提交 A 的 offset
  要求：要么全部成功，要么全部回滚
```

**2. 事务组件**

| 组件 | 职责 |
| --- | --- |
| **TransactionCoordinator** | 事务协调器（Broker 端），管理事务状态 |
| **TransactionalId** | 事务 ID（Producer 配置），跨会话标识 |
| **PID** | Producer ID，事务内部标识 |
| **Epoch** | 纪元，防僵尸 Producer |
| **__transaction_state** | 内部 Topic，存事务状态 |
| **TransactionMarker** | 事务标记（Commit/Abort），写入分区 |

**3. 事务流程**

```
1. Producer 初始化事务
   └─ 向 Coordinator 注册 transactional.id
   └─ Coordinator 分配 PID + Epoch

2. 开启事务
   └─ Producer 调用 beginTransaction()
   └─ Coordinator 记录事务状态 = Ongoing

3. 发送消息（带事务标记）
   └─ 每条消息写入分区时标记为"事务中"
   └─ Coordinator 跟踪涉及的分区

4. 提交消费 offset（纳入事务）
   └─ producer.sendOffsetsToTransaction(offsets, groupMetadata)
   └─ Coordinator 把 offset 提交纳入事务

5. 提交/回滚事务
   ┌─ commit：
   │   Coordinator 写 TransactionMarker(COMMIT) 到所有涉及分区
   │   事务状态 = Complete
   └─ abort：
       Coordinator 写 TransactionMarker(ABORT) 到所有涉及分区
       消费者读 read_committed 时跳过 abort 的消息

6. 消费者可见性
   └─ isolation.level=read_committed：
      只读已 commit 事务的消息，跳过 abort 的
```

**4. 僵尸 Producer 防护**

```
场景：
1. Producer A（epoch=1）发送消息，网络延迟
2. Coordinator 以为 A 挂了，重新分配 epoch=2 给新 Producer B
3. A 恢复，继续发送（僵尸）

防护：
- 每条消息带 PID + Epoch
- Broker 收到 epoch < 当前 epoch 的消息，拒绝
- A 的消息被拒，避免覆盖 B 的数据
```

**5. 事务配置**

```properties
# 生产者
transactional.id=my-app-instance-1  # 每个实例唯一
enable.idempotence=true              # 事务必须开启幂等
transaction.timeout.ms=60000         # 事务超时

# 消费者
isolation.level=read_committed       # 只读已提交
```

```java
// 完整事务示例
props.put("transactional.id", "order-processor-" + instanceId);
KafkaProducer<String, String> producer = new KafkaProducer<>(props);
producer.initTransactions();

KafkaConsumer<String, String> consumer = new KafkaConsumer<>(consumerProps);
consumer.subscribe(Collections.singleton("order-input"));

while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    if (records.isEmpty()) continue;
    
    try {
        producer.beginTransaction();
        
        // 处理并发送
        for (ConsumerRecord<String, String> record : records) {
            String result = process(record.value());
            producer.send(new ProducerRecord<>("order-output", record.key(), result));
        }
        
        // 提交消费 offset（纳入事务）
        producer.sendOffsetsToTransaction(
            getOffsetsToCommit(records), 
            consumer.groupMetadata()
        );
        
        producer.commitTransaction();
    } catch (Exception e) {
        producer.abortTransaction();
        log.error("事务失败，回滚", e);
    }
}
```

**6. 事务的性能开销**

| 开销 | 说明 |
| --- | --- |
| **吞吐降低** | 事务涉及多次 RPC，吞吐降低 20-30% |
| **延迟增加** | 等 commit marker 写入所有分区 |
| **Broker 负载** | __transaction_state 读写、marker 写入 |

**7. 事务 vs 幂等**

| 维度 | 幂等性 | 事务 |
| --- | --- | --- |
| 范围 | 单分区单会话 | 跨分区跨 Topic |
| 保证 | 不重复 | 不丢不重 + 原子性 |
| 配置 | `enable.idempotence=true` | + `transactional.id` |
| 开销 | 小 | 较大 |

**实际业务场景案例**：

- **问题背景**：库存系统，消费扣减消息 → 计算新库存 → 生产库存更新消息，需原子性
- **解决方案**：Kafka 事务保证消费-处理-生产原子
- **实施步骤**：
  1. 生产者 `transactional.id=inventory-service-1`
  2. 消费者 `isolation.level=read_committed`
  3. 事务内：消费扣减 → 计算库存 → 生产新库存 → 提交 offset
  4. 失败回滚，消息不生效
- **效果评估**：库存数据零不一致，吞吐 8000 TPS（原 1 万），可接受

**评分要点**：
- ✅ 事务场景（消费-处理-生产）（必备）
- ✅ TransactionCoordinator + transactional.id（必备）
- ✅ 僵尸 Producer 防护（Epoch）（核心）
- ✅ read_committed 隔离（必备）
- ✅ 事务 vs 幂等区别（加分）

---

## 第六篇 性能优化

### Q6.1 Kafka 高性能的原因是什么？从存储、网络、批量等角度分析。

**问题描述**：请说明 Kafka 高吞吐、低延迟的核心技术手段。

**参考答案**：

**1. 高性能核心手段**

```
┌─────────────────────────────────────────────────┐
│  顺序写磁盘  │  页缓存  │  零拷贝  │  批量处理    │
│  分区并行    │  压缩    │  异步发送 │  稀疏索引    │
└─────────────────────────────────────────────────┘
```

**2. 顺序写磁盘**

```
随机写：磁头寻道，HDD 约 100 IOPS，速度慢
顺序写：磁头不移动，HDD 可达 100+ MB/s，接近内存
```

Kafka 消息追加到日志末尾（顺序写），不修改已有数据：
- HDD 顺序写 100 MB/s，随机写 100 KB/s（1000 倍差距）
- SSD 顺序写也优于随机写

**3. 页缓存（Page Cache）**

Kafka 不维护应用层缓存，依赖 OS Page Cache：

```
Producer 写消息：
  用户空间 → Page Cache → OS 异步刷盘
  
Consumer 读消息：
  Page Cache 命中 → 直接返回（不读磁盘）
  Page Cache 未命中 → 磁盘读取
```

- 写入：先到 Page Cache，OS 异步刷盘（性能高，但有丢数据风险）
- 读取：热点数据在 Page Cache，命中率高的场景几乎不读磁盘
- 重启后 Page Cache 仍有效（OS 管理）

**避免强制刷盘**：
```properties
# 不推荐（性能差）
log.flush.interval.messages=1   # 每条刷盘
# 推荐（依赖 OS）
# 不配置，OS 决定刷盘时机
# 靠副本保证可靠，而非单机刷盘
```

**4. 零拷贝（Zero Copy）**

```
传统文件传输（4 次拷贝 + 2 次系统调用）：
磁盘 → 内核缓冲区 → 用户空间 → Socket 缓冲区 → 网卡

零拷贝 sendfile（2 次拷贝 + 1 次系统调用）：
磁盘 → 内核缓冲区 → 网卡
```

Kafka 消费者拉取消息时，Broker 用 `sendfile` 直接从日志文件发到网卡，不经过 JVM。

**5. 批量处理**

- **生产者攒批**：`linger.ms` + `batch.size`，多条消息打包发送
- **Broker 批量写**：一次追加一个 batch 到日志
- **消费者批量拉取**：一次 poll 多条消息
- **批量压缩**：整个 batch 压缩，减少网络开销

```properties
# 生产者攒批
linger.ms=10           # 等 10ms 攒批
batch.size=65536       # 批次上限 64KB
compression.type=lz4   # 压缩
```

**6. 分区并行**

- 分区分布在多 Broker，生产/消费并行
- 消费者组内每分区独立消费，并行度 = 分区数

**7. 压缩**

| 算法 | 压缩率 | 速度 | 推荐 |
| --- | --- | --- | --- |
| none | - | 最快 | 低延迟 |
| lz4 | 中 | 快 | **推荐（平衡）** |
| snappy | 中 | 快 | 兼容性好 |
| gzip | 高 | 慢 | 高带宽节省 |
| zstd | 高 | 较快 | 2.1+ 推荐 |

压缩在生产者端完成，Broker 直接存压缩数据，消费者端解压，端到端压缩。

**8. 性能对比**

| 场景 | 单 Broker 吞吐 |
| --- | --- |
| acks=0，无副本 | 200 MB/s+ |
| acks=1，单副本 | 100 MB/s |
| acks=all，3 副本 | 50 MB/s |
| 事务 | 30-40 MB/s |

**实际业务场景案例**：

- **问题背景**：日志采集系统，单 Broker 吞吐 30 MB/s，需提升到 100 MB/s
- **解决方案**：综合优化批量、压缩、页缓存
- **实施步骤**：
  1. 生产者：`linger.ms=20`、`batch.size=131072`（128KB）、`compression.type=lz4`
  2. Broker：不强制刷盘，依赖 Page Cache + 副本
  3. 消费者：`fetch.min.bytes=1024`、`max.poll.records=1000`
  4. JVM：`-Xmx6g -Xms6g`，给 Page Cache 留足内存
- **效果评估**：吞吐提升到 120 MB/s，CPU 下降 30%

**评分要点**：
- ✅ 顺序写磁盘（必备）
- ✅ Page Cache 利用（核心）
- ✅ 零拷贝 sendfile（必备）
- ✅ 批量处理 + 压缩（必备）
- ✅ 分区并行（加分）

---

### Q6.2 生产者与消费者如何调优？关键参数有哪些？

**问题描述**：请分别说明生产者与消费者的调优参数与策略。

**参考答案**：

**1. 生产者调优**

| 参数 | 默认值 | 调优建议 | 说明 |
| --- | --- | --- | --- |
| `linger.ms` | 0 | 5-20 | 攒批等待时间，提升吞吐 |
| `batch.size` | 16KB | 64-128KB | 批次大小 |
| `compression.type` | none | lz4/zstd | 压缩 |
| `buffer.memory` | 32MB | 64-128MB | 缓冲区大小 |
| `acks` | all | 视场景 | 可靠性 |
| `max.in.flight.requests.per.connection` | 5 | 5（幂等可保序） | 并发请求数 |
| `max.request.size` | 1MB | 视消息大小 | 单请求上限 |

**吞吐优先配置**：

```properties
linger.ms=20
batch.size=131072
compression.type=lz4
buffer.memory=134217728
acks=1
```

**延迟优先配置**：

```properties
linger.ms=0
batch.size=16384
compression.type=none
acks=1
```

**2. 消费者调优**

| 参数 | 默认值 | 调优建议 | 说明 |
| --- | --- | --- | --- |
| `fetch.min.bytes` | 1 | 1024-10240 | 最小拉取字节数 |
| `fetch.max.wait.ms` | 500 | 500 | 最大等待 |
| `max.poll.records` | 500 | 100-1000 | 单次 poll 记录数 |
| `max.partition.fetch.bytes` | 1MB | 视消息大小 | 单分区拉取上限 |
| `session.timeout.ms` | 45000 | 30000 | 心跳超时 |
| `max.poll.interval.ms` | 300000 | 视处理时长 | poll 间隔 |
| `fetch.max.bytes` | 50MB | 50-100MB | 总拉取上限 |

**3. 消费者多线程模型**

```java
// 方案1：单消费者单线程（保序，吞吐低）
while (true) {
    ConsumerRecords<K,V> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<K,V> r : records) process(r);
    consumer.commitSync();
}

// 方案2：多消费者 + 多线程（高吞吐）
// N 个消费者实例，每个单线程消费自己的分区

// 方案3：单消费者 + worker 线程池（需处理顺序与 offset）
ExecutorService executor = Executors.newFixedThreadPool(10);
while (true) {
    ConsumerRecords<K,V> records = consumer.poll(Duration.ofMillis(100));
    // 按 Key 分发到固定线程，保序
    Map<Integer, List<ConsumerRecord<K,V>>> grouped = groupByKey(records);
    for (Map.Entry<Integer, List<ConsumerRecord<K,V>>> e : grouped.entrySet()) {
        executor.submit(() -> processBatch(e.getValue()));
    }
    // 注意：offset 提交复杂，需等所有 worker 完成
}
```

**4. 消费者 offset 提交策略**

```java
// 同步提交（可靠，慢）
consumer.commitSync();

// 异步提交（快，可能失败）
consumer.commitAsync();

// 混合（推荐）
try {
    consumer.commitSync();  // 正常用同步
} catch (CommitFailedException e) {
    // 重试
} finally {
    consumer.commitAsync();  // 关闭前异步提交
}
```

**5. 消费者积压处理**

```
积压原因：
1. 消费速度 < 生产速度
2. 消费者处理慢（业务逻辑复杂/外部依赖慢）
3. Rebalance 频繁

解决方案：
1. 增加消费者实例（≤ 分区数）
2. 增加分区数 + 消费者
3. 优化业务逻辑（异步化、批量）
4. 多线程消费（注意顺序与 offset）
5. 临时扩容（如跳过非关键处理）
```

**6. 监控指标**

| 指标 | 说明 |
| --- | --- |
| `consumer-lag` | 消费延迟（Log End Offset - Consumer Offset） |
| `records-consumed-rate` | 消费速率 |
| `records-lag-max` | 最大积压 |
| `fetch-rate` | 拉取频率 |
| `commit-latency-avg` | 提交延迟 |

**实际业务场景案例**：

- **问题背景**：日志消费服务，单消费者处理 1 万条/秒，生产 5 万条/秒，积压 1000 万
- **解决方案**：多消费者 + 多线程 + 批量优化
- **实施步骤**：
  1. 分区从 6 扩到 24
  2. 消费者实例从 1 扩到 6（每实例 4 线程）
  3. `max.poll.records=1000`，批量处理
  4. 写入 ES 改批量（Bulk API）
- **效果评估**：消费速度 6 万条/秒，积压 1 小时清零

**评分要点**：
- ✅ 生产者关键参数（linger.ms/batch.size/compression）（必备）
- ✅ 消费者关键参数（max.poll.records/max.poll.interval.ms）（必备）
- ✅ 多线程消费模型与顺序问题（核心）
- ✅ offset 提交策略（必备）
- ✅ 消费积压处理（加分）

---

## 第七篇 实际应用场景

### Q7.1 Kafka 在日志收集系统中的应用？如何设计高吞吐日志管道？

**问题描述**：请设计一个基于 Kafka 的日志收集系统。

**参考答案**：

**1. 整体架构**

```
应用服务器               Kafka 集群              日志处理
┌──────────┐           ┌──────────┐          ┌──────────┐
│  App     │           │          │          │ Flink    │
│  +Filebeat│──日志──►│  Kafka   │───消费──►│ Spark    │──►ES/HDFS
│          │           │  (多Topic)│          │ Storm    │
└──────────┘           │          │          └──────────┘
                       │          │
┌──────────┐           │          │          ┌──────────┐
│  App     │           │          │          │ 告警服务  │
│  +Filebeat│──日志──►│          │───消费──►│          │
└──────────┘           └──────────┘          └──────────┘
```

**2. Topic 设计**

| Topic | 分区 | 副本 | 说明 |
| --- | --- | --- | --- |
| `log-nginx-access` | 24 | 3 | Nginx 访问日志 |
| `log-app-error` | 12 | 3 | 应用错误日志 |
| `log-metric` | 12 | 3 | 指标日志 |
| `log-audit` | 6 | 3 | 审计日志 |

**3. 生产者配置**

```properties
# 日志场景：吞吐优先，可容忍少量丢失
acks=1
linger.ms=50
batch.size=262144          # 256KB
compression.type=lz4
buffer.memory=134217728    # 128MB
retries=3
```

**4. 日志收集 Agent 选型**

| Agent | 特点 |
| --- | --- |
| **Filebeat** | 轻量，Go 实现，Kafka 原生支持 |
| **Fluentd** | 插件丰富，Ruby 实现 |
| **Logstash** | 功能强，JVM 较重 |
| **Vector** | Rust 实现，高性能 |

Filebeat 配置示例：

```yaml
filebeat.inputs:
- type: log
  paths:
    - /var/log/nginx/access.log
  fields:
    log_type: nginx-access

output.kafka:
  hosts: ["kafka1:9092", "kafka2:9092", "kafka3:9092"]
  topic: 'log-nginx-access'
  partition.round_robin:
    reachable_only: false
  required_acks: 1
  compression: lz4
  max_message_bytes: 1000000
```

**5. 消费者设计**

```java
// 日志写入 ES，批量提升性能
public class LogToEsConsumer {
    private BulkProcessor bulkProcessor;
    
    public void consume() {
        while (true) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(500));
            if (records.isEmpty()) continue;
            
            for (ConsumerRecord<String, String> record : records) {
                // 解析日志
                LogEntry log = parse(record.value());
                // 加入 ES 批量请求
                IndexRequest request = new IndexRequest("log-" + log.getDate())
                    .source(log.toJson(), XContentType.JSON);
                bulkProcessor.add(request);
            }
            
            consumer.commitSync();
        }
    }
}
```

**6. 日志清理与归档**

```properties
# 按时间清理
log.retention.hours=72          # 保留 3 天
log.retention.check.interval.ms=300000  # 5 分钟检查一次

# 按大小清理
log.retention.bytes=10737418240 # 单分区上限 10GB

# 日志压缩（key 为业务 ID，保留最新值）
cleanup.policy=compact          # 或 delete, compact
```

**7. 监控告警**

- 生产者：发送速率、错误率
- Broker：磁盘使用、ISR 数、分区均衡
- 消费者：消费延迟、积压量

**实际业务场景案例**：

- **问题背景**：日均 500GB 日志，原 Flume + HDFS 架构扩展性差，查询慢
- **解决方案**：Filebeat + Kafka + Flink + ES
- **实施步骤**：
  1. 50 台应用服务器装 Filebeat，收集日志发往 Kafka
  2. Kafka 6 节点集群，按日志类型分 Topic，共 60 分区
  3. Flink 消费 Kafka，实时清洗 + 写 ES（实时查询）+ 写 HDFS（归档）
  4. ES 按 1 天 1 索引，7 天自动删除
- **效果评估**：日志查询从分钟级到秒级，吞吐 100MB/s，无丢失

**评分要点**：
- ✅ 整体架构（必备）
- ✅ Topic 设计与分区（必备）
- ✅ 生产者吞吐优化配置（核心）
- ✅ 消费者批量写入 ES（加分）
- ✅ 日志清理策略（必备）

---

### Q7.2 Kafka 在事件驱动架构（EDA）中的应用？如何保证事件可靠传递？

**问题描述**：请设计一个基于 Kafka 的事件驱动架构，并说明可靠性保证。

**参考答案**：

**1. 事件驱动架构（EDA）**

```
┌─────────┐    事件    ┌─────────┐    事件    ┌─────────┐
│ 订单服务 │───发布───►│  Kafka  │───订阅───►│ 库存服务 │
└─────────┘           │         │           └─────────┘
                      │  事件   │
┌─────────┐    事件    │  总线   │    事件    ┌─────────┐
│ 支付服务 │───发布───►│         │───订阅───►│ 通知服务 │
└─────────┘           └─────────┘           └─────────┘
                          │
                          │ 事件
                          ▼
                     ┌─────────┐
                     │ 风控服务 │
                     └─────────┘
```

- **解耦**：服务间通过事件通信，无需直接调用
- **异步**：事件发布后立即返回，处理异步
- **扩展**：新增消费者无需改生产者

**2. 事件设计**

```java
// 事件基类
public abstract class DomainEvent {
    private String eventId;        // 事件 ID（UUID）
    private String eventType;      // 事件类型
    private Long timestamp;        // 时间戳
    private String source;         // 来源服务
    private String traceId;        // 链路追踪 ID
}

// 订单创建事件
public class OrderCreatedEvent extends DomainEvent {
    private Long orderId;
    private Long userId;
    private BigDecimal amount;
    private List<OrderItem> items;
}
```

**3. 事件 Topic 设计**

| Topic | 事件 | 生产者 | 消费者 |
| --- | --- | --- | --- |
| `order-events` | OrderCreated/Paid/Cancelled | 订单服务 | 库存、通知、风控 |
| `payment-events` | PaymentSucceeded/Failed | 支付服务 | 订单、通知 |
| `inventory-events` | StockLocked/Released | 库存服务 | 订单 |

**4. 可靠性保证**

**① 事件不丢失（生产端）**

```java
// 本地事务 + Kafka 事务
@Transactional
public void createOrder(Order order) {
    // 1. 写订单库（本地事务）
    orderRepository.save(order);
    
    // 2. 发布事件（Kafka 事务）
    kafkaTemplate.executeInTransaction(template -> {
        template.send("order-events", 
            new OrderCreatedEvent(order.getId(), order.getUserId()));
        return true;
    });
}
```

**问题**：DB 事务与 Kafka 事务非原子，可能 DB 成功 Kafka 失败。

**解决方案——Outbox 模式**：

```
1. 业务操作 + 写事件到 outbox 表（同一 DB 事务）
2. 独立线程/CDC 读取 outbox 表，发往 Kafka
3. 发送成功后标记 outbox 为已发送

┌─────────────────────────────────┐
│ DB 事务                          │
│  ├─ INSERT INTO orders ...       │
│  └─ INSERT INTO outbox ...       │  ← 同一事务
└─────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│ Outbox Publisher（Debezium CDC） │
│  监听 outbox 表变更 → Kafka      │
└─────────────────────────────────┘
```

**② 事件不丢（消费端）**

```java
// 幂等消费 + 手动提交
public void consume() {
    while (true) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
        for (ConsumerRecord<String, String> record : records) {
            DomainEvent event = parse(record.value());
            
            // 幂等检查（已处理则跳过）
            if (eventStore.exists(event.getEventId())) {
                continue;
            }
            
            // 处理事件
            handle(event);
            
            // 记录已处理
            eventStore.markProcessed(event.getEventId());
        }
        consumer.commitSync();
    }
}
```

**③ 事件顺序保证**

- 同一聚合根的事件用相同 Key（如 orderId）路由到同分区
- 单分区单消费者，保证顺序

**5. 死信队列（DLQ）**

```java
// 处理失败的消息发到 DLQ
try {
    handle(event);
} catch (Exception e) {
    // 发到死信 Topic
    kafkaTemplate.send("order-events-dlq", 
        new DeadLetterEvent(event, e.getMessage()));
    // 不影响主流程，继续消费
}
consumer.commitSync();
```

**6. 事件回溯**

Kafka 消息保留期长，可按 offset 回溯重放：

```java
// 从指定时间重新消费
consumer.assign(partitions);
consumer.seekToBeginning(partitions);  // 从头消费
// 或
Map<TopicPartition, Long> offsets = consumer.offsetsForTimes(
    partitions.stream().collect(Collectors.toMap(
        p -> p, p -> startTime
    ))
);
offsets.forEach(consumer::seek);
```

**7. Saga 模式（分布式事务）**

事件驱动架构中，跨服务事务用 Saga：

```
订单创建 Saga：
1. 订单服务：创建订单（待支付）
2. 发布 OrderCreatedEvent
3. 库存服务：锁定库存
   ├─ 成功：发布 StockLockedEvent
   │  └─ 支付服务：发起支付
   └─ 失败：发布 StockLockFailedEvent
      └─ 订单服务：取消订单（补偿）
```

**实际业务场景案例**：

- **问题背景**：电商微服务，原同步调用导致级联故障，下单接口 P99 5 秒
- **解决方案**：事件驱动 + Outbox 模式
- **实施步骤**：
  1. 订单、库存、支付服务通过 Kafka 事件通信
  2. 用 Outbox 表 + Debezium CDC 保证事件可靠发布
  3. 消费者幂等 + DLQ 处理失败
  4. 同订单事件按 orderId 分区，保证顺序
- **效果评估**：下单 P99 降到 200ms（异步），服务解耦，单服务故障不影响下单

**评分要点**：
- ✅ EDA 架构与解耦（必备）
- ✅ Outbox 模式保证事件发布（核心）
- ✅ 幂等消费 + 手动提交（必备）
- ✅ 死信队列（加分）
- ✅ Saga 分布式事务（加分）

---

### Q7.3 Kafka 在流处理中的应用？Kafka Streams 与 Flink 如何选型？

**问题描述**：请说明 Kafka 在流处理场景的应用，对比 Kafka Streams 与 Flink。

**参考答案**：

**1. 流处理场景**

| 场景 | 说明 |
| --- | --- |
| **实时统计** | UV/PV、点击量、销售额 |
| **窗口聚合** | 每分钟订单量、每小时 Top N |
| **实时 ETL** | 数据清洗、转换、富化 |
| **实时告警** | 异常检测、阈值监控 |
| **CEP** | 复杂事件处理（如登录失败 5 次告警） |

**2. Kafka Streams 简介**

Kafka Streams 是 Kafka 内置的流处理库（非独立集群）：

```java
// 词频统计
StreamsBuilder builder = new StreamsBuilder();
KStream<String, String> source = builder.stream("input-topic");

KTable<String, Long> wordCounts = source
    .flatMapValues(value -> Arrays.asList(value.toLowerCase().split(" ")))
    .groupBy((key, word) -> word)
    .count();

wordCounts.toStream().to("output-topic");

KafkaStreams streams = new KafkaStreams(builder.build(), props);
streams.start();
```

**3. Kafka Streams 特性**

| 特性 | 说明 |
| --- | --- |
| **轻量级** | 库形式，无独立集群，嵌入应用 |
| **Exactly-Once** | 事务支持 |
| **状态管理** | 本地 RocksDB + Kafka changelog |
| **窗口** | 滚动、滑动、会话窗口 |
| **DSL + API** | 高级 DSL + 低级 Processor API |

**4. Flink 简介**

```java
// Flink 词频统计
DataStream<String> stream = env.addSource(
    new FlinkKafkaConsumer<>("input-topic", new SimpleStringSchema(), props));

DataStream<Tuple2<String, Integer>> counts = stream
    .flatMap((String value, Collector<Tuple2<String, Integer>> out) -> 
        Arrays.stream(value.split(" ")).forEach(w -> out.collect(Tuple2.of(w, 1)))
    )
    .returns(Types.TUPLE(Types.STRING, Types.INT))
    .keyBy(t -> t.f0)
    .window(TumblingEventTimeWindows.of(Time.minutes(1)))
    .sum(1);

counts.addSink(new FlinkKafkaProducer<>("output-topic", 
    new SimpleStringSchema(), props));
```

**5. Kafka Streams vs Flink**

| 维度 | Kafka Streams | Flink |
| --- | --- | --- |
| **部署** | 库（嵌入应用） | 独立集群 |
| **状态** | 本地 RocksDB | RocksDB（可配置） |
| **窗口** | 滚动/滑动/会话 | 更丰富（含全局窗口） |
| **时间语义** | 事件时间/处理时间 | 事件时间/处理时间/摄入时间 |
| **水位线** | 简单 | 完善（Watermark） |
| **CEP** | 弱 | 强（CEP 库） |
| **批流统一** | 仅流 | 批流统一 |
| **Exactly-Once** | ✅ | ✅ |
| **运维** | 简单（无集群） | 复杂（集群管理） |
| **生态** | Kafka 生态 | 多 Source/Sink |
| **适合** | Kafka 内流处理 | 复杂流处理 |

**6. 选型建议**

| 场景 | 推荐 |
| --- | --- |
| 简单聚合，仅 Kafka 数据源 | Kafka Streams |
| 复杂 CEP、多数据源 | Flink |
| 无独立集群运维能力 | Kafka Streams |
| 大规模流处理 | Flink |
| 批流统一 | Flink |
| 低延迟、高吞吐 | 两者均可 |

**7. Kafka Streams 状态管理**

```
本地状态：RocksDB（每个实例本地）
容错：changelog topic（状态变更日志）
恢复：实例故障后，新实例从 changelog 重建状态

┌─────────────────────────────────┐
│  Kafka Streams 应用实例          │
│  ┌──────────┐  ┌──────────┐     │
│  │ 处理逻辑  │─►│ RocksDB  │     │  ← 本地状态
│  └──────────┘  │ (状态)   │     │
│       ▲        └────┬─────┘     │
│       │             │ 变更      │
│       │             ▼           │
│  ┌────┴─────────────────────┐   │
│  │ changelog topic          │   │  ← 容错
│  └──────────────────────────┘   │
└─────────────────────────────────┘
```

**8. 实时窗口聚合示例**

```java
// 每小时订单金额统计（Kafka Streams）
KStream<String, Order> orders = builder.stream("orders");

KTable<Windowed<String>, BigDecimal> hourlyStats = orders
    .groupBy((key, order) -> order.getShopId())
    .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofHours(1)))
    .aggregate(
        () -> BigDecimal.ZERO,
        (shopId, order, total) -> total.add(order.getAmount()),
        Materialized.as("hourly-stats-store")
    );

hourlyStats.toStream().to("shop-hourly-stats");
```

**实际业务场景案例**：

- **问题背景**：实时销售大屏，需每分钟更新各店铺销售额
- **解决方案**：Kafka Streams 窗口聚合
- **实施步骤**：
  1. 订单事件发往 `orders` Topic，按 shopId 分区
  2. Kafka Streams 消费，按 1 分钟窗口聚合销售额
  3. 结果写入 `shop-minute-stats` Topic
  4. 大屏服务订阅结果，WebSocket 推前端
- **效果评估**：大屏数据延迟 < 5 秒，扛住 10 万订单/分钟

**评分要点**：
- ✅ 流处理场景（必备）
- ✅ Kafka Streams 与 Flink 对比（核心）
- ✅ 选型建议（必备）
- ✅ 状态管理与 changelog（加分）
- ✅ 窗口聚合实现（加分）

---

## 附录 评分标准与面试指南

### A.1 各能力维度评分标准

| 维度 | 初级（1-3分） | 中级（4-6分） | 高级（7-9分） | 专家（10分） |
| --- | --- | --- | --- | --- |
| **架构原理** | 知道 Kafka 是消息队列 | 懂 Broker/Topic/Partition | 懂 Controller、日志存储、索引 | 能从源码层分析 |
| **生产者/消费者** | 会基本 API | 懂 acks、Rebalance | 懂事务、幂等、Rebalance 优化 | 能设计 Exactly-Once 方案 |
| **分区策略** | 会设分区数 | 懂 Key 路由 | 懂扩容影响、顺序保证 | 能规划大规模分区 |
| **高可用** | 会搭集群 | 懂副本机制 | 懂 HW/LEO/ISR、Leader Epoch | 能设计容灾方案 |
| **一致性** | 知道丢消息 | 懂三层不丢配置 | 懂事务、幂等原理 | 能设计端到端 Exactly-Once |
| **性能优化** | 会调参数 | 懂批量、压缩 | 懂零拷贝、Page Cache | 能全链路调优 |
| **应用场景** | 会用 Kafka | 懂日志收集 | 懂 EDA、流处理 | 能架构设计 |

### A.2 面试官提问策略

**由浅入深**：
1. **概念题**："说说 Kafka 架构" → 考察基础
2. **原理题**："HW 和 LEO 的区别？" → 考察深度
3. **应用题**："如何保证消息不丢？" → 考察实践
4. **场景题**："消费积压怎么处理？" → 考察综合能力
5. **设计题**："设计一个实时日志分析系统" → 考察架构能力

**追问技巧**：
- 挖底层：从"用 Kafka" → "为什么快" → "零拷贝原理"
- 挖实践：从"懂 Rebalance" → "遇到过什么问题" → "怎么优化的"
- 挖权衡：从"Exactly-Once" → "性能开销" → "如何选型"

### A.3 红线问题（一票否决）

- 认为 Kafka 是推模式（实际消费者拉取）
- 不知道分区是并行度单位
- 用 Kafka 还开 `acks=0` 处理关键业务
- 认为 Kafka 能保证全局有序（仅单分区）
- 不懂 Rebalance，认为消费者固定消费某分区

### A.4 加分项

- 量化数据（"单 Broker 100MB/s"、"事务降 30% 吞吐"）
- 结合真实项目案例（背景 → 方案 → 步骤 → 效果）
- 提到 Kafka 3.x 新特性（KRaft、增量 Rebalance、Sticky 分区）
- 横向对比其他 MQ（RabbitMQ、RocketMQ、Pulsar）
- 提到源码层理解（日志结构、索引实现）
- 容灾与高可用设计（多机房、灾备）

### A.5 备考察重点

面试前重点准备：
1. **架构与核心概念**（必考）
2. **HW/LEO/ISR + 副本同步**（必考）
3. **acks + 不丢失配置**（高频）
4. **Rebalance 机制与优化**（高频）
5. **幂等 + 事务 Exactly-Once**（高频）
6. **分区数选择 + 顺序保证**（高频）
7. **性能优化（批量/压缩/零拷贝）**（中频）
8. **应用场景（日志/EDA/流处理）**（中频）

建议每题准备一个**真实项目案例**：问题背景 → 解决方案 → 实施步骤 → 效果评估。

---

## 参考资料

- 官方文档：[Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- 《Kafka 权威指南》—— Neha Narkhede
- 《深入理解 Kafka：核心设计与实践原理》—— 朱忠华
- Kafka 源码：https://github.com/apache/kafka
- Kafka KRaft 模式：https://kafka.apache.org/documentation/#kraft
- Confluent 博客：https://www.confluent.io/blog/

---

> **文档说明**：本面试题集共 7 大篇章、20+ 道题目，覆盖 Kafka 高级工程师所需的核心知识体系。所有题目均附问题描述、深度参考答案、实际业务场景案例与评分要点，适合面试备战、知识梳理、团队培训等场景。建议结合源码阅读与生产实践，从"会用 Kafka"进阶到"懂 Kafka"。
