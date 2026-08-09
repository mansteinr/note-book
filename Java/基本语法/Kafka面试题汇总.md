# Kafka 面试题汇总

> 适用版本：Kafka 2.x ~ 3.x | 适合 Java 开发人员、大数据工程师面试准备及知识巩固

## 目录

- [Kafka 面试题汇总](#kafka-面试题汇总)
  - [目录](#目录)
  - [一、选择题](#一选择题)
    - [1.1 基础概念篇](#11-基础概念篇)
    - [1.2 架构设计篇](#12-架构设计篇)
    - [1.3 工作原理篇](#13-工作原理篇)
    - [1.4 性能优化篇](#14-性能优化篇)
  - [二、简答题](#二简答题)
    - [2.1 核心概念与架构](#21-核心概念与架构)
    - [2.2 消息生产与消费](#22-消息生产与消费)

---

## 一、选择题

### 1.1 基础概念篇

---

**Q1：以下关于 Kafka 的描述，错误的是？**

A. Kafka 是一个分布式发布-订阅消息系统  
B. Kafka 的消息是不可变的，一旦写入就不能修改  
C. Kafka 只能处理文本消息，不支持二进制数据  
D. Kafka 采用拉模式（Pull）由消费者主动拉取消息  

**答案：C**

**解析：**

- **标准结论**：Kafka 完全支持二进制数据传输，其消息体本身就是字节数组（byte array），没有类型限制。
- **依据要点**：
  1. Kafka 的消息格式定义中，value 字段是可选的字节数组，可以存储任意序列化后的数据（JSON、Avro、Protobuf、图片等）；
  2. ProducerRecord 的构造函数允许传入任意类型，经过 Serializer 序列化为 byte[]；
  3. 选项 A、B、D 均为 Kafka 的正确特性：Kafka 是分布式发布订阅系统（A对），消息采用追加写，日志段文件不可修改（B对），消费者使用 poll() 主动拉取消息（D对）。
- **排除其他选项理由**：A/B/D 三个选项均是 Kafka 的核心设计，只有 C 的表述与 Kafka 实际机制相悖。

---

**Q2：在 Kafka 中，以下哪个组件负责存储消息？**

A. Producer  
B. Consumer  
C. Broker  
D. ZooKeeper  

**答案：C**

**解析：**

- **标准结论**：Broker 是 Kafka 集群中的消息存储节点，负责接收生产者写入的消息并持久化到磁盘。
- **依据要点**：
  1. **Producer（生产者）**：负责创建消息并发送到 Broker，不存储消息，排除 A；
  2. **Consumer（消费者）**：从 Broker 拉取消息并处理，本地只维护消费位移（offset），不存储消息本体，排除 B；
  3. **Broker**：Kafka 服务端进程，每个 Broker 管理若干分区的日志段（.log/.index/.timeindex 文件），承担消息持久化职责，C 正确；
  4. **ZooKeeper**：在 Kafka 2.8 之前用于集群元数据管理（Broker 列表、Topic 配置、Controller 选举等），不存储业务消息，排除 D。注意 Kafka 3.x 已支持 KRaft 模式移除 ZooKeeper 依赖。
- **排除其他选项理由**：A、B 为客户端角色，D 为元数据协调组件，均不存储业务消息。

---

**Q3：关于 Kafka Topic 和 Partition 的关系，以下说法正确的是？**

A. 一个 Topic 只能对应一个 Partition  
B. 一个 Partition 可以属于多个 Topic  
C. Partition 内的消息是全局有序的  
D. Partition 是 Kafka 并行处理的最小单位  

**答案：D**

**解析：**

- **标准结论**：Partition 是 Kafka 并行处理和数据分片的最小粒度，生产者和消费者都可以针对不同 Partition 实现并行读写。
- **依据要点**：
  1. 一个 Topic 可以配置一个或多个 Partition，分区数决定了该 Topic 的最大并行消费能力，A 错误；
  2. Partition 从属于特定 Topic，命名格式为 `<topic>-<partitionId>`，不能跨 Topic 共享，B 错误；
  3. Kafka 只保证 **单个 Partition 内有序**，不保证整个 Topic 全局有序，C 错误；
  4. 生产者端按分区并行写入，消费者组内每个消费者实例消费若干个独立分区，因此 Partition 是并行处理最小单位，D 正确。
- **排除其他选项理由**：A 与 Kafka 分片设计矛盾；B 违反分区从属关系；C 将分区有序误解为全局有序，均应排除。

---

**Q4：Kafka Consumer Group 的作用不包括以下哪项？**

A. 实现消息的广播和单播模式  
B. 实现消费者的负载均衡  
C. 自动管理消费者的 offset  
D. 直接参与 Broker 端的数据复制  

**答案：D**

**解析：**

- **标准结论**：Consumer Group 是纯客户端概念，与 Broker 端的数据副本复制机制完全无关。
- **依据要点**：
  1. 广播模式：不同 Consumer Group 消费同一份消息，互不影响；单播模式：同一 Consumer Group 内的消费者分摊分区，一条消息只被组内一个消费者处理，A 是 Group 的作用；
  2. 同一 Group 内，分区会按 Range/RoundRobin/Sticky/CooperativeSticky 等策略分配给消费者实现负载均衡，B 是 Group 的作用；
  3. Group Coordinator 会协助管理 offset，消费者可通过 `enable.auto.commit` 自动提交或手动提交 offset 到 `__consumer_offsets` 主题，C 是 Group 的作用；
  4. Broker 端副本复制由 Leader/Follower Replica 之间通过 Fetch 请求完成，和 Consumer Group 没有任何关联，D 不属于 Group 作用。
- **排除其他选项理由**：A/B/C 都是 Consumer Group 的核心功能，只有 D 属于 Broker 端副本机制范畴。

---

**Q5：Kafka 中关于 offset 的描述，正确的是？**

A. offset 是消息在整个 Topic 中的全局唯一编号  
B. 消费者提交的 offset 表示"下一条要消费的消息位置"  
C. offset 必须永久保存在 ZooKeeper 中  
D. 同一个 Consumer Group 内的不同消费者共享同一个 offset  

**答案：B**

**解析：**

- **标准结论**：消费者提交的 committed offset 语义是"下次消费开始的位置"，即已经成功处理完的最后一条消息的 offset + 1。
- **依据要点**：
  1. offset 是**分区内**的单调递增编号，不同分区各自独立计数，不是 Topic 全局唯一，A 错误；
  2. `commitSync()` 提交 offset N 时，含义是"0 ~ N-1 位置的消息已处理完毕，下次从 N 开始拉取"，B 正确；
  3. 新版本 Kafka（0.9+）offset 默认存储在内部 Topic `__consumer_offsets` 中，不再依赖 ZooKeeper（旧版本 /consumers/<group>/offsets 节点已废弃），C 错误；
  4. 同一 Group 内按分区分配 offset 管理粒度，每个消费者对自己负责的分区维护独立的消费进度，不是"共享同一个 offset"，D 错误。
- **排除其他选项理由**：A 混淆了分区 offset 与全局 offset；C 还停留在旧版架构认知；D 忽略了 Group 内按分区隔离 offset 的事实。

---

### 1.2 架构设计篇

---

**Q6：Kafka 副本（Replica）机制中，关于 Leader 和 Follower 的说法错误的是？**

A. 每个 Partition 有且仅有一个 Leader 副本  
B. 生产者和消费者的读写请求都直接发给 Leader  
C. Follower 通过 Fetch 请求从 Leader 同步数据  
D. Leader 宕机后，任意 Follower 都可以自动成为新 Leader  

**答案：D**

**解析：**

- **标准结论**：只有处于 ISR（In-Sync Replicas，同步副本集合）中的 Follower 才有资格被选举为新 Leader，并非任意 Follower。
- **依据要点**：
  1. 每个分区在创建时会选举一个副本作为 Leader，其余为 Follower，Leader 唯一性由 Controller 保证，A 正确；
  2. 为保证一致性，所有读写均由 Leader 处理，Follower 只做备份不对外服务，B 正确；
  3. Follower 会周期性（`replica.lag.time.max.ms` 内）向 Leader 发送 Fetch 请求拉取消息，C 正确；
  4. 当 Leader 宕机时，Controller 会从 ISR 列表中挑选第一个副本作为新 Leader。若所有 Follower 都落后过多（不在 ISR 中），则需依赖 `unclean.leader.election.enable` 配置决定是否允许非 ISR 副本参与选举（默认 false），因此"任意 Follower 自动成为新 Leader"是错误的，D 当选。
- **排除其他选项理由**：A/B/C 均是副本机制的正确描述，只有 D 违背了 ISR 选举规则。

---

**Q7：ISR（In-Sync Replicas）集合中，副本满足以下哪个条件才会被保留？**

A. Follower 的消息条数与 Leader 完全相等  
B. Follower 在 `replica.lag.time.max.ms` 时间内向 Leader 发起过 Fetch 请求且滞后消息量不超过阈值  
C. Follower 与 Leader 部署在同一台物理机上  
D. Follower 已经向 ZooKeeper 注册了临时节点  

**答案：B**

**解析：**

- **标准结论**：Kafka 判断副本是否"同步"的标准是时间维度 + 消息滞后量的双重阈值，并非要求 100% 完全相等。
- **依据要点**：
  1. 早期版本 Kafka 使用 `replica.lag.max.messages`（条数阈值）和 `replica.lag.time.max.ms`（时间阈值）双维度判断；新版本（0.10.1+）主要以**时间阈值**为准：只要 Follower 在 `replica.lag.time.max.ms`（默认 30s）内持续向 Leader Fetch，且最终落后的消息量不会超过配置阈值，就被视为 in-sync，B 描述正确；
  2. "完全相等"不现实——Follower 异步复制天然存在延迟，短暂落后几条是正常的，A 过于绝对且错误；
  3. 同机部署与 ISR 判定完全无关，C 错误；
  4. 副本注册节点属于集群元数据管理，不参与 ISR 动态判定逻辑，D 错误。
- **排除其他选项理由**：A 过于绝对、C 同机与 ISR 无关、D 混淆了元数据注册和 ISR 判定。

---

**Q8：Kafka Controller 的主要职责不包括？**

A. 分区 Leader 选举  
B. 管理 Topic 的创建与删除  
C. 直接处理生产者的消息写入请求  
D. 监听 Broker 上下线并触发重分配  

**答案：C**

**解析：**

- **标准结论**：Controller 是集群的"大脑"负责元数据管理与协调，不参与业务数据面的消息读写。
- **依据要点**：
  1. Controller 在分区 Leader 副本宕机时，从 ISR 中选举新 Leader，并通过 UpdateMetadata 请求同步给所有 Broker，A 属于职责；
  2. 创建/删除 Topic 实际上是 Controller 监听 ZooKeeper 或 KRaft 元数据变更后，分配分区副本并下发指令给各 Broker，B 属于职责；
  3. 生产者的消息写入请求由目标分区 Leader 所在的 Broker 直接处理，Controller 不接触业务消息，C 不属于 Controller 职责，当选；
  4. Broker 宕机时 Controller 会感知其会话失效，进而将该 Broker 上的 Leader 分区触发重新选举，并将元数据更新到集群，D 属于职责。
- **排除其他选项理由**：A/B/D 都是 Controller 核心职责，只有 C 混淆了控制面与数据面角色。

---

**Q9：以下哪种情况不会触发 Consumer Group 的 Rebalance？**

A. 消费者组内新增一个消费者实例  
B. 消费者实例宕机（超过 `session.timeout.ms` 未发心跳）  
C. 向 Topic 新增了分区  
D. 生产者发送消息的速率突然翻倍  

**答案：D**

**解析：**

- **标准结论**：Rebalance 的触发条件是"消费者组成员变化"或"订阅的 Topic/分区数量变化"，与生产者发送速率无关。
- **依据要点**：
  1. 新增消费者（A）：组协议会触发 Sticky/Range/RoundRobin 等策略重新分配分区；
  2. 消费者掉线（B）：Coordinator 检测到心跳超时，认为成员退出，需要回收并再分配其分区；
  3. 订阅的 Topic 新增分区（C）：分区元数据变化，新增的分区需要被分配给组内成员消费；
  4. 生产者速率变化只会影响消费延迟（Lag），不会改变消费者数量或分区数量，因此不会触发 Rebalance，D 当选。
- **排除其他选项理由**：A、B 属于成员变化，C 属于订阅分区数变化，都是 Rebalance 触发条件。

---

**Q10：Kafka 3.x 引入的 KRaft 模式，相对于 ZooKeeper 模式的主要改进不包括？**

A. 移除了对 ZooKeeper 的外部依赖，简化部署运维  
B. 将元数据直接存储在 Kafka 内部 Topic 中，扩展性更好  
C. 支持单节点 Controller 故障不再依赖 ZK 选举  
D. 可以在 KRaft 模式下直接使用传统的 ZooKeeper CLI 命令  

**答案：D**

**解析：**

- **标准结论**：KRaft 模式下 ZooKeeper 已被完全移除，原有的 zk-shell、zkCli 等工具完全不适用。
- **依据要点**：
  1. KRaft 使用 Raft 一致性算法在 Controller Quorum 内部选举和复制元数据，不再部署 ZooKeeper 集群，运维复杂度降低，A 正确；
  2. KRaft 模式下元数据存储在内部元数据日志（__cluster_metadata）中，不再受 ZooKeeper znode 1MB 大小限制和 Watcher 扩展性瓶颈，B 正确；
  3. Raft 协议自带 Leader 选举机制，Controller 故障由 Controller Quorum 内部快速选举新的 Active Controller，C 正确；
  4. KRaft 模式下必须使用 Kafka 自带的 `kafka-metadata-shell.sh` 或 AdminClient API 管理元数据，ZooKeeper CLI 无法连接和操作，D 错误，当选。
- **排除其他选项理由**：A、B、C 都是 KRaft 的官方设计目标和实际改进。

---

### 1.3 工作原理篇

---

**Q11：Kafka 生产者发送消息时，`acks` 参数设置为 `all`（或 `-1`）时，以下说法正确的是？**

A. 只要 Leader 写入成功就返回 ACK  
B. Leader 和所有 Follower 都写入磁盘后才返回 ACK  
C. Leader 写入成功且 ISR 中所有副本都同步完成后才返回 ACK  
D. 生产者不会收到任何 ACK，吞吐量最高  

**答案：C**

**解析：**

- **标准结论**：`acks=all` 的语义是"Leader 写入 + ISR 中全部副本确认同步完成"后，Broker 才向生产者返回 ACK。
- **依据要点**：
  1. `acks=0`：生产者不等 Broker ACK，发完就忘，吞吐最高但可能丢消息，对应 D；
  2. `acks=1`（默认）：Leader 写入本地日志即返回 ACK，不等待 Follower，若 Leader 刚写成功就宕机会丢消息，对应 A；
  3. `acks=all` / `acks=-1`：Leader 不仅要本地写入，还要等待 ISR 中**所有** Follower 都 Fetch 到这条消息并写入各自日志，才向生产者返回 ACK，C 正确；
  4. B 的"所有 Follower"错误——非 ISR 的落后副本不参与 ACK 判定，否则会被慢节点拖死。
- **排除其他选项理由**：A 对应 acks=1；D 对应 acks=0；B 将"ISR 中副本"偷换为"所有 Follower"。

---

**Q12：关于 Kafka 的日志存储结构，以下排序正确的是？**

A. Topic → Partition → Segment → .log / .index / .timeindex 文件  
B. Topic → Segment → Partition → .log / .index 文件  
C. Partition → Topic → Segment → Message  
D. Broker → Topic → Segment → Partition → File  

**答案：A**

**解析：**

- **标准结论**：Kafka 磁盘存储的层次关系为 Topic → Partition（目录）→ Segment（一对 .log / .index / .timeindex 文件组成一个段）。
- **依据要点**：
  1. 磁盘目录结构：`/kafka-logs/<topic-name>-<partition-id>/` 是 Partition 级目录；
  2. 每个 Partition 目录下由多个 Segment 组成，每个 Segment 包含三个文件：
     - `.log`：实际消息数据（Record Batch）；
     - `.index`：稀疏索引，存储 offset → .log 文件物理位置的映射；
     - `.timeindex`：时间索引，存储时间戳 → offset 的映射；
  3. Segment 的触发切分条件：超过 `log.segment.bytes`（默认 1GB）或超过 `log.roll.hours`（默认 7 天）。
  4. B、C、D 的层级顺序均不符合真实目录结构。
- **排除其他选项理由**：B 将 Segment 放在 Partition 之上颠倒了从属关系；C 把 Topic 和 Partition 倒置；D 多了无关层级且顺序错乱。

---

**Q13：Kafka 消费者 `poll()` 方法内部执行流程的关键步骤，正确的顺序是？**

① 加入消费者组并获取分配的分区  
② 从 Coordinator 获取已提交的 offset  
③ 向 Fetcher 发送 Fetch 请求拉取消息  
④ 心跳检测（Heartbeat）维持会话  
⑤ 反序列化并返回 ConsumerRecords  

A. ①→②→③→④→⑤  
B. ④→①→②→③→⑤  
C. ①→④→②→③→⑤  
D. ②→①→④→③→⑤  

**答案：C**

**解析：**

- **标准结论**：消费者 poll 的核心顺序是"加入组 → 心跳 → 获取已提交 offset → Fetch 拉取 → 反序列化返回"。
- **依据要点**：
  1. 新消费者第一次 poll 会先向 Coordinator 发起 JoinGroup → SyncGroup 流程，完成分区分配（①），因此排除 B、D（不以①开头）；
  2. 分区分配完成后，消费者会启动后台心跳线程（HeartbeatThread）定期向 Coordinator 发送心跳（④），保持 session 不过期；
  3. 然后针对分配到的每个分区，向 Coordinator 发送 OffsetFetch 请求拿到上次提交的 offset（②），作为 fetch 起点；
  4. Fetcher 根据起点 offset 向各分区 Leader 所在 Broker 发 Fetch 请求（③）；
  5. 拉回的 Record Batch 经过反序列化、拦截器处理，封装为 ConsumerRecords 返回给调用方（⑤）；
  6. 顺序为 ①→④→②→③→⑤，对应 C。A 把心跳放在 offset 获取之后不合理，因为心跳在分配完成就启动。
- **排除其他选项理由**：B 心跳先于加入组逻辑错误；D 取 offset 先于加入组没有分区信息；A 的心跳位置晚于实际启动时机。

---

**Q14：Kafka 的幂等生产者（Idempotent Producer）可以解决以下哪种重复问题？**

A. 消费者端重复处理同一消息  
B. 生产者因 Retry 导致同一消息写入 Broker 多次  
C. Broker 磁盘故障导致的分区数据重复  
D. 消费者 Rebalance 后重新消费  

**答案：B**

**解析：**

- **标准结论**：幂等生产者通过在 Broker 端去重 `<PID, Partition, Sequence Number>` 三元组，只解决"生产者重试导致的单分区内重复写入"问题。
- **依据要点**：
  1. 幂等生产者原理：Producer 初始化时被分配一个 PID（Producer ID），每条消息携带单调递增的 Sequence Number，Broker 在 `<PID, Partition>` 维度缓存最新 Seq，若收到的 Seq ≤ 缓存值则直接丢弃该写入请求，保证一条消息只写一次；
  2. A 属于消费端重复，需消费端业务幂等或事务配合解决，与生产者幂等无关；
  3. B 是幂等生产者的直接解决场景——网络抖动下 ACK 丢失，Producer 重试，Broker 端去重；
  4. C 属于存储级错误，幂等不涉及副本/磁盘恢复逻辑；
  5. D 属于 Rebalance 后 offset 回溯导致重新消费，是消费端问题，需由消费端 offset 管理解决。
- **排除其他选项理由**：A、D 是消费端问题，C 是存储问题，均不在幂等生产者覆盖范围内。

---

**Q15：以下哪个场景下 Kafka 可以实现端到端的 Exactly-Once 语义？**

A. 普通生产者 + 手动提交 offset 的消费者  
B. 幂等生产者 + 消费端先处理业务再提交 offset  
C. Kafka 事务（读-处理-写流程）+ 幂等生产者 + 事务型消费者  
D. acks=all + min.insync.replicas=2 的生产者配置  

**答案：C**

**解析：**

- **标准结论**：Kafka 原生 Exactly-Once 语义（EOS）需要事务 API 串联"消费 → 处理 → 写回"全链路，并配合幂等与事务型消费读取已提交消息。
- **依据要点**：
  1. 选项 A：普通生产者可能重复写入，手动提交若业务成功但提交失败会导致重复消费，最多 At-Least-Once；
  2. 选项 B：幂等生产者仅解决单会话单分区内写入重复，跨 Topic 写回 + 消费 offset 提交无法原子化，仍可能"消费后写回失败但 offset 已提交"导致丢消息或反之；
  3. 选项 C：完整 EOS 流程——`consumer.beginOffsetsForTimes()` → 业务处理 → `producer.beginTransaction()` → 发送到目标 Topic → `producer.sendOffsetsToTransaction(offsets, groupId)` → `producer.commitTransaction()`。Broker 通过事务标记控制 `read_committed` 消费者只能读到已提交消息，配合幂等保证事务内写入不重复，实现全链路 EOS；
  4. 选项 D：acks/min.insync 解决的是副本层面的"不丢消息"（At-Least-Once），和 Exactly-Once 不是一回事。
- **排除其他选项理由**：A 最多 At-Least-Once；B 缺少事务串联消费偏移和写回消息的原子性；D 只是副本可靠性配置。

---

### 1.4 性能优化篇

---

**Q16：以下哪个配置不会提升 Kafka 生产者的吞吐量？**

A. 增大 `batch.size`（批次大小）  
B. 增大 `linger.ms`（等待时间）  
C. 开启 `compression.type`（如 snappy、lz4）  
D. 将 `acks` 从 `1` 改为 `all`  

**答案：D**

**解析：**

- **标准结论**：`acks=all` 需要等待 ISR 全部副本确认，会显著增加单条消息的写入延迟，降低吞吐；其余三项均为吞吐优化的典型手段。
- **依据要点**：
  1. `batch.size`（默认 16KB）：Producer 会将同一分区内多条消息打包为一个 Batch 发送，增大批次可减少网络请求次数，A 提升吞吐；
  2. `linger.ms`（默认 0ms）：即使 batch 未满，也等待一段时间让更多消息凑批，配合 batch.size 形成"时间+大小"双阈值凑批策略，B 提升吞吐；
  3. `compression.type`：Producer 端压缩消息体积，减少网络传输量和磁盘写入量（snappy/lz4 的压缩/解压耗时很低），C 提升吞吐；
  4. `acks=all`：相较于 `acks=1` 需要多等待若干次副本 Fetch → ACK 的往返，显著增加 P99 延迟，单位时间完成的写入数下降，D **不会提升反而降低**吞吐。
- **排除其他选项理由**：A、B、C 均为官方文档推荐的生产者吞吐优化三要素。

---

**Q17：Kafka Broker 端采用"零拷贝"技术提升消费性能，主要是为了减少以下哪两个环节的 CPU 拷贝和上下文切换？**

A. 磁盘 → 内核缓冲区 和 内核缓冲区 → 应用程序缓冲区  
B. 应用程序缓冲区 → Socket 缓冲区 和 Socket 缓冲区 → 网卡  
C. 磁盘 → 内核缓冲区（PageCache）和 内核缓冲区（PageCache）→ Socket 缓冲区  
D. 应用程序缓冲区 → 内核缓冲区 和 内核缓冲区 → 磁盘  

**答案：C**

**解析：**

- **标准结论**：Kafka 消费端零拷贝基于 Linux `sendfile()` 系统调用，绕过"PageCache → 用户态"这一步，直接把 PageCache 数据 DMA 到 Socket 缓冲区。
- **依据要点**：
  1. 传统文件读取并网络发送流程：磁盘 → 内核 PageCache → 用户态缓冲区 → 内核 Socket 缓冲区 → 网卡，共 4 次 CPU 拷贝 + 4 次上下文切换；
  2. Kafka 消费使用零拷贝（`FileChannel.transferTo()` → `sendfile()`）后流程：磁盘 → 内核 PageCache（DMA），然后 PageCache → Socket 缓冲区（DMA + 少量 CPU 元数据拷贝），最后网卡发送。用户态缓冲区被完全跳过，减少 2 次 CPU 拷贝 + 2 次上下文切换，对应选项 C 描述的两个关键环节；
  3. A、B、D 均遗漏了核心的"PageCache 直连 Socket"路径，且混入了应用程序缓冲区参与，均不是零拷贝针对的场景。
- **排除其他选项理由**：A 多了应用程序缓冲区参与，零拷贝正是跳过用户态；B 描述的是 Socket→网卡本身就是硬件 DMA；D 方向反了（零拷贝是消费方向，不是写入）。

---

**Q18：关于 Kafka 的日志清理策略（Log Cleanup Policy），以下说法正确的是？**

A. `delete` 策略按 key 去重，仅保留每个 key 最新版本的消息  
B. `compact` 策略按时间或大小阈值直接删除旧的 Segment  
C. `compact` 策略只针对消费 offset 之前的消息进行去重  
D. `delete` 和 `compact` 可以同时启用，即先按时间删除再按 key 去重  

**答案：D**

**解析：**

- **标准结论**：Kafka 的 Topic 级别配置 `cleanup.policy` 支持 `delete,compact` 同时配置，两者叠加生效（通常是 `delete` 先淘汰超过保留期的数据，`compact` 在保留期内去重）。
- **依据要点**：
  1. `delete` 策略：按 `retention.ms`（时间，默认 7 天）或 `retention.bytes`（大小）阈值，将过期的 Segment 整个删除，不涉及按 key 去重，因此 A 的前半句把 delete 和 compact 功能搞反了，A 错误；
  2. `compact` 策略（Log Compaction）：按 key 维度去重，保留每个 key 的最新 value，用于"用 Kafka 存 KV 快照/配置/用户画像"等场景。它的触发条件是"dirty ratio（未合并比例）超过 `min.cleanable.dirty.ratio`（默认 0.5）"，不按时间，B 错误；
  3. `compact` 在工作时会确保保留所有"消费端头部 offset 之前"的消息（即消费者还可能读到的位置之前不去重），称为"消费者头部保护"，但并非"只"去重 offset 之前的（而是跳过头部之前那段，对之后做去重），C 表述不准确；
  4. D 正确：`cleanup.policy=delete,compact` 是合法配置，两个 Cleaner 线程池会分别按各自策略清理。
- **排除其他选项理由**：A 将 delete 和 compact 功能倒置；B 将 compact 描述为时间删除；C 把消费者头部保护机制说成唯一去重范围。

---

**Q19：关于消费者 `max.poll.records`、`max.poll.interval.ms` 和 `fetch.min.bytes` 三者的说法，错误的是？**

A. `max.poll.records` 控制单次 `poll()` 最多返回多少条消息  
B. `max.poll.interval.ms` 规定两次 `poll()` 调用之间的最大间隔，超时会被踢出组  
C. `fetch.min.bytes` 控制 Broker 攒够多少字节才返回 Fetch 响应，可减少请求数量  
D. 三者值都设置得越大，消费吞吐越高  

**答案：D**

**解析：**

- **标准结论**：三项参数并非"越大越好"，`fetch.min.bytes` 过大会显著增加单条消息延迟；`max.poll.interval.ms` 过大可能掩盖消费线程卡死的问题。
- **依据要点**：
  1. `max.poll.records`（默认 500）：单次 poll 返回的最大记录数，控制一次业务处理批次大小，A 正确；
  2. `max.poll.interval.ms`（默认 5min）：消费端业务处理若超过该间隔还未调用下一次 poll，Coordinator 会认为该消费者"卡死"，触发 LeaveGroup → Rebalance，B 正确；
  3. `fetch.min.bytes`（默认 1B）+ `fetch.max.wait.ms`（默认 500ms）：Broker 收到 Fetch 请求后，只有攒够 `fetch.min.bytes` 字节或等待 `fetch.max.wait.ms` 超时才返回，减少空响应降低网络开销，C 正确；
  4. D 错误：若 `fetch.min.bytes` 设置为 10MB，而 Topic 流量很低（每秒仅几十字节），消费者会每次都等满 500ms 才拿到几条消息，端到端延迟暴涨，吞吐反而更差。`max.poll.interval.ms` 设置过大则消费挂死时不能及时发现并 failover，影响可用性。
- **排除其他选项理由**：A、B、C 分别对应三个参数的标准语义，只有 D 过度绝对化。

---

**Q20：某 Kafka 集群的 Topic 有 12 个分区，3 副本，部署在 6 个 Broker 上。为了最大化消费并行度，以下哪个 Consumer Group 的配置最合适？**

A. 组内消费者数量 = 3，每个消费者分配 4 个分区  
B. 组内消费者数量 = 12，每个消费者分配 1 个分区  
C. 组内消费者数量 = 18，会有 6 个消费者空闲待命  
D. 组内消费者数量 = 1，避免 Rebalance  

**答案：B**

**解析：**

- **标准结论**：同一 Consumer Group 内，**消费者数量 ≤ 分区数**时，每增加一个消费者都会线性增加并行度；超过分区数后多出来的消费者处于空闲，浪费资源。
- **依据要点**：
  1. 分区是并行消费的最小粒度，Kafka 不允许两个消费者同时消费同一分区（同一 Group 内），因此 Group 的最大并行度上限就是分区数（本题 12）；
  2. A：消费者 = 3，每个分到 4 个分区，并行度为 3，没有充分利用分区能力；
  3. B：消费者 = 12，正好 1 对 1 匹配 12 个分区，每个消费者只负责 1 个分区，Rebalance 影响范围最小，并行度达到上限，B 最合适；
  4. C：消费者 = 18，其中 6 个消费者没有任何分区可消费，白白占用连接和心跳资源，且 Rebalance 时会增加协议协商耗时，不如只启动 12 个；
  5. D：消费者 = 1，串行消费 12 个分区，并行度最低，吞吐量最差。
- **排除其他选项理由**：A 没有打满并行度；C 出现空闲消费者；D 并行度最低，均非最优。

---

## 二、简答题

### 2.1 核心概念与架构

---

**Q1：请简述 Kafka 的整体架构，并说明 Producer、Broker、Consumer、ZooKeeper/KRaft 四者之间的关系。**

**答：**

Kafka 采用经典的**发布-订阅式分布式消息队列**架构，可划分为"客户端集群 + 服务端集群 + 元数据协调集群"三层。

**（1）核心组件职责**

| 组件 | 角色定位 | 核心职责 |
|------|---------|---------|
| **Producer（生产者）** | 客户端，写入方 | 创建消息，按分区路由到对应 Broker；支持批量、压缩、重试、幂等、事务 |
| **Broker（Kafka 服务端）** | 服务端，存储节点 | 接收 Producer 写入，持久化到磁盘日志段；响应 Consumer 的 Fetch 请求；管理副本复制 |
| **Consumer（消费者）** | 客户端，读取方 | 通过 Consumer Group 形式，按分区拉取并处理消息；提交 offset |
| **ZooKeeper / KRaft** | 元数据协调层 | 维护集群元数据（Topic/分区/副本/ISR/Broker 列表）；选举 Controller；KRaft 模式下用 Raft 替代 ZK |

**（2）组件之间的协作关系**

```text
Producer ──(元数据请求)──→ Broker(任意) ──→ 返回各分区Leader所在Broker
   │
   └──(produce请求)──→ 分区Leader所在Broker ──→ 写入本地.log/.index ──→ Follower Fetch 同步

Consumer ──(找Coordinator)──→ 发送 FindCoordinator ──→ 得到 Group Coordinator 所在 Broker
   │
   ├──(JoinGroup/SyncGroup/Heartbeat/OffsetCommit)──→ Group Coordinator
   └──(Fetch请求)──→ 各分区Leader所在Broker ──→ 从 PageCache 零拷贝返回数据

Controller(特殊Broker) ──(ZK或KRaft选举)──→ 负责Topic创建/分区Leader选举/Broker宕机重平衡
```

**（3）关键设计要点**

1. **无状态 Broker + 有状态客户端**：路由信息、消费 offset 均由 Producer/Consumer 或 `__consumer_offsets` 管理，Broker 不保存客户端状态，扩容极其容易；
2. **解耦**：Producer 只写 Leader，Consumer 只从 Leader 读，各自独立扩展；
3. **ZK → KRaft 演进**：2.8 之前用 ZK 做协调，3.3+ KRaft 生产可用，去掉对 ZK 的依赖，Controller 变为 Raft Quorum。

---

**Q2：什么是分区（Partition）？Kafka 为什么要对 Topic 进行分区？分区数是不是越多越好？**

**答：**

**（1）分区的定义**  
分区是 Topic 下的**物理分片**，每个分区本质上是一个**追加写的有序日志队列**，消息在分区内按 offset 严格递增并保证消费顺序。一个 Topic 可以有 1 个或多个分区，分布在不同 Broker 上。

**（2）分区的设计动机（为什么分区）**

| 维度 | 解决的问题 | 说明 |
|------|-----------|------|
| **水平扩展 / 吞吐量** | 单机磁盘、网络、CPU 瓶颈 | 分区分散到多台 Broker，多机并行读写，吞吐 = ∑单分区吞吐 |
| **并行消费能力** | 单消费者处理不过来 | Consumer Group 内消费者数最多 = 分区数，分区决定消费并行上限 |
| **消息顺序 + 负载均衡折中** | 全局有序代价太高 | 单分区有序满足大多数场景（按 key 分区 → 同 key 有序），同时分区之间可负载均衡 |
| **容灾（配合副本）** | 单机宕机数据丢失 | 每个分区可以有多副本跨 Broker 部署，Leader 挂了自动切换 |

**（3）分区数**不是**越多越好**

过多分区会带来如下副作用：

1. **文件句柄开销**：每个分区每个副本都要打开 `.log / .index / .timeindex` 等一组文件，分区数 × 副本数 × 3 个文件 × Topic 数，可能超过 Linux ulimit 限制；
2. **Controller 元数据管理压力**：分区越多，Controller 选举和 UpdateMetadata 请求的规模越大，恢复时间越长；
3. **端到端延迟上升**：Producer 凑批（batch.size / linger.ms）是按分区维度的，过多分区会导致每个分区单独凑一批，batch 偏小，吞吐下降延迟上升；
4. **ISR 伸缩抖动**：每个分区都要维持独立的 ISR，故障时 Controller 需要处理的 Leader 选举数量爆炸；
5. **Rebalance 成本**：分区数越多，Rebalance 时分区迁移和 offset 恢复成本越高。

**（4）经验值**

- 单 Broker 建议分区数上限：2000 ~ 4000；
- 单集群分区总数建议：不超过 20,000（KRaft 模式可更高）；
- 分区数规划公式：`分区数 = Max(生产者目标吞吐 / 单分区写入吞吐, 消费者目标吞吐 / 单分区消费吞吐)`，再向上取整到接近 Broker 数的整数倍，便于均匀分布。

---

**Q3：请解释 Consumer Group 的 Rebalance 机制，包括触发条件、协议流程以及常见分区分配策略。**

**答：**

Rebalance 是 Consumer Group 将订阅 Topic 的分区在**组内成员之间重新分配**的过程，是"水平扩展 + 容错"的核心机制。

**（1）触发条件**

| 类型 | 具体场景 |
|------|---------|
| 组成员变化 | 消费者启动并加入组 / 消费者优雅退出 / 消费者 crash / `max.poll.interval.ms` 超时被踢 |
| 订阅 Topic 数变化 | 运行中调用 `subscribe(Pattern)` 匹配到新的 Topic |
| 订阅分区数变化 | Admin 对订阅 Topic 执行了 `alterPartition` 增加分区 |

**（2）Rebalance 协议流程（以 Eager 协议为例）**

由 Group Coordinator（Broker 端）协调，分 5 步：

```text
① JoinGroup 阶段：
   所有消费者向 Coordinator 发 JoinGroupRequest，携带订阅信息、协议类型。
   Coordinator 选出第一个加入的消费者作为"Leader 消费者"。
   所有成员返回 JoinGroupResponse，Leader 拿到全组成员列表。

② SyncGroup 阶段：
   Leader 消费者根据分配策略（Range/Sticky 等）计算"成员→分区列表"的分配方案，
   放入 SyncGroupRequest 发给 Coordinator；其他成员发空 SyncGroupRequest。
   Coordinator 将最终分配结果下发给所有成员。

③ Heartbeat 启动：
   分配完成后，每个成员启动 HeartbeatThread，按 heartbeat.interval.ms 周期发心跳。

④ OffsetFetch：
   成员对分配到的分区，向 Coordinator 发 OffsetFetchRequest 获取上次提交的 committed offset。

⑤ 开始消费：
   Fetcher 从 committed offset（或 earliest/latest）开始发 Fetch 请求拉数据。
```

> 注意：Kafka 2.4+ 引入 **Incremental Cooperative Rebalance**（增量再平衡），通过 `ConsumerPartitionAssignor` 新接口实现"只迁移需要调整的分区"，避免 Stop-The-World 式全量回收。

**（3）4 种常见分区分配策略**

| 策略 | 算法思路 | 特点 |
|------|---------|------|
| **RangeAssignor**（默认历史） | 按 Topic 维度：对 Topic 的分区排序，消费者排序后按"分区数/消费者数 + 余数"均分 | 单 Topic 均衡；多 Topic 场景下前面消费者会多分；可能不均匀 |
| **RoundRobinAssignor** | 将所有 Topic 所有分区轮询依次分配给各消费者 | 多 Topic 下比 Range 更均匀；但 Rebalance 时几乎全量重分配 |
| **StickyAssignor** | 尽量保留上一次的分配结果，只对"无归属"的分区做重新分配 | Rebalance 迁移分区数最少；避免消费者本地缓存大规模失效 |
| **CooperativeStickyAssignor** | Sticky + 增量协作 | 支持多轮次小步重平衡，每轮只改一小部分，非 Stop-The-World（新版本推荐） |

---

**Q4：什么是 ISR？ISR 的伸缩条件、Leader 选举规则，以及 `min.insync.replicas` 的作用。**

**答：**

ISR（In-Sync Replicas，同步副本集合）是 Kafka 副本机制中"**与 Leader 保持同步的 Follower 列表**"，是可靠性与可用性之间权衡的核心概念。

**（1）ISR 伸缩条件（如何判断一个副本是否在 ISR 中）**

Kafka 以**时间维度**作为主要判定标准（`replica.lag.time.max.ms`，默认 30 秒）：

- Follower 在 `replica.lag.time.max.ms` 内**持续向 Leader 发送 Fetch 请求**，并且**最终落后的消息量**不超过阈值，则被视为 in-sync，保留在 ISR 中；
- 如果 Follower 卡住（GC 暂停、网络断开）超过时间阈值未 Fetch，或者落后的 offset 差距过大，**会被 Controller 从 ISR 中剔除**；
- 当 Follower 恢复后持续追上 Leader 的 LEO（Log End Offset），达到 in-sync 条件后，**会被重新加回 ISR**。

> ISR 列表的变更会写入 ZK 或 KRaft 元数据，并触发 UpdateMetadata 同步给所有 Broker。

**（2）Leader 选举规则**

当分区 Leader 所在的 Broker 宕机时，Controller 执行选举：

1. **优先从 ISR 列表中**选择第一个存活的 Follower 作为新 Leader（因为它的数据最新）；
2. 如果 ISR 为空（所有副本都落后了），则进入分支：
   - `unclean.leader.election.enable = false`（默认值，生产推荐）：该分区进入离线状态，停止读写，直到某个副本追上并回到 ISR，**可靠性优先**；
   - `unclean.leader.election.enable = true`：允许从"非 ISR 但存活"的副本里挑一个当 Leader，**可用性优先**，但会**丢失**该 Follower 上没有的消息，存在数据丢失风险。

**（3）`min.insync.replicas` 的作用**

该参数是 Topic/Broker 级别的配置，和 `acks=all` 配合使用，含义是：

> 当 Producer 以 `acks=all` 写入时，要求 ISR 中**至少要有 `min.insync.replicas` 个副本**，否则 Producer 会收到 `NotEnoughReplicasException`，写入失败。

**为什么需要它？**

假设副本数 = 3，ISR 中只剩 Leader 自己（两个 Follower 都卡了），如果没有 `min.insync.replicas`，`acks=all` 退化为"只要 Leader 确认"就写入成功——此时 Leader 一旦宕机且 `unclean.leader.election.enable=false`，数据就永久丢失了。

设置 `min.insync.replicas=2` 可强制保证"必须至少有 2 个副本收到"才允许写入，杜绝"单点写入成功又宕机"的风险。

**推荐配置组合（3 副本场景）**：`replication.factor=3` + `min.insync.replicas=2` + `acks=all`，容忍 1 个副本故障同时仍然可写。

---

### 2.2 消息生产与消费

---

**Q5：Kafka 生产者发送消息的完整流程是怎样的？请说明拦截器、序列化器、分区器、RecordAccumulator、Sender 线程的分工。**

**答：**

Producer 发送消息采用**双线程 + 异步批量**的架构，`send()` 方法只做入队，实际发送由后台 Sender 线程执行。

```text
业务线程调用 producer.send(record)
        │
        ▼
  ┌──────────────┐
  │  拦截器链     │──→ onSend() 可用于修改消息、埋点统计、灰度打标
  └──────────────┘
        │
        ▼
  ┌──────────────┐
  │  序列化器     │──→ key.serializer / value.serializer 将对象 → byte[]
  └──────────────┘
        │
        ▼
  ┌──────────────┐
  │   分区器      │──→ 指定partition？→ 用指定；有key？→ murmur2(key) % partitionNum；
  └──────────────┘    否则按 sticky partition（批满或超时后切分区）
        │
        ▼
  ┌──────────────────────────────────────────┐
  │        RecordAccumulator（队列缓冲）      │
  │  结构：ConcurrentMap<TopicPartition, Deque<ProducerBatch>>
  │  同一 TP 多条消息拼成 ProducerBatch（<=batch.size）
  │  凑批条件：batch.size 满 或 linger.ms 到点
  └──────────────────────────────────────────┘
        │
        ▼  Sender 后台线程
  ┌──────────────────────────────────────────┐
  │  Sender 线程（单线程事件循环）            │
  │  ① 遍历所有就绪的 ProducerBatch          │
  │  ② 按 Broker 聚合 → Map<Node, ClientRequest>
  │  ③ 通过 Java NIO Selector 多路复用发送     │
  │  ④ 收到响应：成功 → 回调onCompletion；    │
  │     失败 → 可重试（NotLeaderForPartition/│
  │     NetworkException），否则抛异常给回调   │
  └──────────────────────────────────────────┘
```

**各组件职责**

| 组件 | 职责说明 | 关键配置 |
|------|---------|---------|
| **拦截器（ProducerInterceptor）** | 在 send 前后、Broker 响应后做横切逻辑，可配置多个组成拦截器链 | `interceptor.classes` |
| **序列化器（Serializer）** | 将业务对象序列化为 byte[]，常见 StringSerializer、ByteArraySerializer、JsonSerializer | `key.serializer`、`value.serializer` |
| **分区器（Partitioner）** | 决定消息进入哪个分区。新版默认 Sticky Partitioner（提升批次命中率） | `partitioner.class` |
| **RecordAccumulator** | 内存缓冲队列，按 TopicPartition 聚合消息为 Batch，是"业务线程 → Sender 线程"的桥梁 | `buffer.memory`（默认 32MB）、`batch.size`（16KB）、`linger.ms`（0） |
| **Sender 线程** | 唯一网络 IO 线程，处理与各 Broker 的 TCP 连接、请求响应、重试、ACK，保证单连接内有序发送 | `connections.max.idle.ms`、`max.in.flight.requests.per.connection` |

**发送语义保证**：若 `enable.idempotence=true` 且 `max.in.flight.requests.per.connection ≤ 5`，可保证即使发生重试，Broker 端也不会出现"乱序 + 重复"。

---

**Q6：Kafka 消费者如何保证消息的顺序消费？什么场景下会出现乱序？**

**答：**

**（1）Kafka 的顺序保证的前提**

Kafka 只保证**单个 Partition 内的消息按 offset 递增有序消费**，不保证 Topic 全局有序。因此：

- 若 Topic 只有 1 个分区 → 天然全局有序（但牺牲了并行度）；
- 若 Topic 有多个分区 → 只能保证**相同 key 的消息进入同一分区**，从而实现"按 key 维度局部有序"。

**（2）实现顺序消费的正确姿势**

```java
// 关键：按业务唯一键做分区路由，保证同 key 消息进入同一分区
ProducerRecord<String, OrderEvent> record = new ProducerRecord<>(
    "order-events",
    order.getOrderId(),   // 以 OrderId 作为 key
    orderEvent
);
producer.send(record);
```

消费端保证：
1. **单分区单消费者**（一个分区同一时刻只会被同一消费者组内的一个消费者消费，这是 Kafka 协议保证的，天然满足）；
2. **单分区内不要并发处理**：不要把 poll 出来的消息丢到线程池异步处理，否则 offset 顺序不能和业务完成顺序对齐；
3. **手动提交 offset 而非自动提交**：确保"业务处理成功后才提交 offset"，避免异常后回溯导致的顺序感知错乱。

```java
// 消费端：单线程处理 + 手动提交
while (true) {
    ConsumerRecords<String, OrderEvent> records = consumer.poll(Duration.ofMillis(1000));
    for (ConsumerRecord<String, OrderEvent> r : records) {
        processOrderEvent(r.value());  // 严格按 offset 顺序业务处理
    }
    consumer.commitSync(); // 处理完整个批次才提交
}
```

**（3）可能出现乱序的场景（反模式）**

| 场景 | 为什么会乱序 | 规避方式 |
|------|------------|---------|
| 消息 key 为 null + 默认分区器 | RoundRobin/Sticky 随机分配分区，同业务消息落到不同分区 | 必须指定业务 key |
| Producer 开启重试且 `max.in.flight>1` + 幂等未开 | 先发的消息因网络失败重试，后发的消息先被 Broker 确认写入 | 开启幂等 `enable.idempotence=true`（推荐）或设置 `max.in.flight=1`（不推荐） |
| 消费端多线程异步处理 poll 结果 | poll 得到按 offset 有序的消息，扔到线程池后哪个先处理完不可控 | 按分区维度独立线程队列处理 |
| 修改分区数 | 同 key 的 hash % N 在 N 变化后路由到新分区，新旧分区消息时间交叉 | 尽量不缩分区；扩容时新建 Topic 迁移或做双写过渡 |
| acks=0 模式下发送抖动 | Broker 接收顺序不一定等于 Producer 发送顺序 | 至少使用 acks=1 |
| Log Compaction 后消费 | Compact 会删除旧版本 key，读取时 offset 存在空洞，不影响每条记录内部顺序，但会"跳过旧值" | 这是语义使然，不算异常乱序 |

---

**Q7：请说明 Kafka 消费者提交 offset 的几种方式及各自优缺点。如何避免"消息丢失"和"重复消费"？**

**答：**

offset 提交的本质是告诉 Broker（通过 `__consumer_offsets` 内部 Topic）："我已经消费到这里了，下次请从这个位置之后给我消息。"

**（1）三种提交方式**

| 提交方式 | 触发条件 | 优点 | 缺点 |
|---------|---------|------|------|
| **自动提交** `enable.auto.commit=true` | 后台线程按 `auto.commit.interval.ms`（默认 5s）周期性提交上次 poll 的最大 offset + 1 | 代码简单，零心智负担 | 1) 可能"还没处理完就自动提交了"，进程挂了 → **丢消息**；2) interval 内重复 poll 但异常 → 重启后重复消费大 |
| **手动同步提交** `consumer.commitSync()` | 业务代码显式调用，阻塞直到 Broker 返回 ACK 或重试失败抛异常 | 强语义，"处理完再提交"不丢消息；失败自动重试 | 阻塞业务线程，吞吐有损耗；批量粒度提交（按最后一条）会有少量重复消费 |
| **手动异步提交** `consumer.commitAsync()` | 业务线程发起提交，立即返回；完成后回调 `OffsetCommitCallback` | 不阻塞业务线程，吞吐高 | 失败不自动重试（可能后发的先成功，重试会覆盖最新 offset）；需要业务自己处理回调异常 |

**（2）最佳实践组合**

```java
try {
    while (true) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofSeconds(1));
        for (ConsumerRecord<String, String> r : records) {
            processRecord(r);   // 业务处理
        }
        // 正常路径：先做一次异步提交（不阻塞）
        consumer.commitAsync((offsets, ex) -> {
            if (ex != null) log.error("async commit fail", ex);
        });
    }
} catch (Exception e) {
    log.error("consume error", e);
} finally {
    try {
        // 退出前：同步提交兜底，确保最后一段不丢
        consumer.commitSync();
    } finally {
        consumer.close();
    }
}
```

**（3）如何避免丢消息（保证至少 At-Least-Once）**

核心原则：**先业务处理成功，后提交 offset**。

1. 必须关闭 `enable.auto.commit`，改为手动提交；
2. `processRecord()` 的业务逻辑要做好异常捕获：只有真正处理成功（DB 写成功、下游调用成功等）才算完成；
3. 进程退出钩子中调用 `commitSync()` 兜底最后一次 offset；
4. 生产端配合：`acks=all` + `min.insync.replicas≥2` 保证 Broker 端不丢。

**（4）如何避免重复消费（做到 Exactly-Once 或幂等）**

Kafka 协议本身在消费端**最多只能保证 At-Least-Once**（因为业务处理和 offset 提交不是一个原子事务，除非使用 Kafka 事务 API），因此需要业务层配合：

1. **业务幂等**（最常用、成本最低）：
   - 在 DB 中维护一张 `consume_log(msg_id)` 表，处理前先查是否存在，存在直接跳过；
   - 或利用业务表的唯一键约束（如下单场景 `INSERT ... ON DUPLICATE KEY UPDATE`），天然去重。
2. **Kafka 事务 API**：如果处理结果是写回另一个 Kafka Topic，则使用 `producer.sendOffsetsToTransaction(offsets, groupId)` 将"写结果 + 提交 offset"封装在一个事务里，实现 EOS（Exactly-Once Semantics）。
3. **Exactly-Once 支持的外部系统**：如 MySQL + Kafka 可采用"两阶段事务"（XA）或"事务性发件箱（Transactional Outbox）"模式，保障 DB 操作与 offset 提交的一致性。

---

### 2.3 存储与副本机制

---

**Q8：请详细描述 Kafka 的日志存储结构，包括 Segment 切分规则、.log/.index/.timeindex 三个文件的作用与协作方式。**

**答：**

Kafka 使用**分段（Segment）、追加写（Append-Only）、稀疏索引（Sparse Index）**的磁盘存储方案，兼顾写入性能、查找速度和可清理性。

**（1）分层目录结构**

```text
${log.dirs}/                          # Broker 数据根目录（可配置多个，逗号分隔）
├── order-events-0/                   # Topic: order-events, Partition: 0
│   ├── 00000000000000000000.log      # Segment-0 的实际消息
│   ├── 00000000000000000000.index    # Segment-0 的 offset → 物理位置索引
│   ├── 00000000000000000000.timeindex# Segment-0 的 timestamp → offset 索引
│   ├── 00000000000000051234.log      # Segment-1，baseOffset = 51234
│   ├── 00000000000000051234.index
│   └── 00000000000000051234.timeindex
├── order-events-1/                   # Partition: 1
│   └── ...
└── __consumer_offsets-14/            # 内部 offset Topic，共 50 个分区
    └── ...
```

每个 Segment 的文件名就是该 Segment 的**基础 offset（baseOffset）**，即该段中第一条消息的 offset，使用 20 位十进制补零命名。

**（2）Segment 切分触发条件（满足任一即切分）**

1. `log.segment.bytes`（默认 1GB）：`.log` 文件大小达到阈值；
2. `log.roll.hours`（默认 168h = 7 天）：当前 Segment 持续写入时间到达上限；
3. 可在 Topic 级别覆盖，如 `log.segment.bytes=536870912`（512MB）。

> 切分后旧 Segment 变为"只读"（实际上是**不可变文件**，Kafka 不会修改已落盘的任何字节，只会在清理策略触发时整段删除）。

**（3）三个文件的作用与协作**

| 文件 | 结构 | 作用 |
|------|------|------|
| **.log** | 实际消息数据，按 Record Batch 分组存储，每个 Batch 含 CRC、长度、压缩类型、timestamp、offset 序列、消息体 | 承载真实消息字节 |
| **.index** | 稀疏索引条目：`relativeOffset(4B) + position(4B)`，每写入 `index.interval.bytes`（默认 4KB）消息插一条索引 | 将"目标 offset"快速定位到 ".log 文件中某 4KB 附近的物理字节位置" |
| **.timeindex** | 稀疏索引条目：`timestamp(8B) + relativeOffset(4B)`，与 .index 同密度 | 将"目标时间戳"映射到最近的 offset，供 `offsetsForTimes()` API 查询 |

**索引查找消息的流程（以 offset = 61234 为例）**

```text
Step 1：二分查找 Segment 文件 → 找到
        baseOffset=51234（≤61234）的 .log 文件，
        下一段 baseOffset>61234，因此目标在 51234.log

Step 2：计算 relativeOffset = 61234 - 51234 = 10000

Step 3：对 51234.index 做二分查找，找 ≤10000 的最大相对 offset，
        得到条目 (9980, position=0x3F1A20)

Step 4：从 51234.log 的 0x3F1A20 位置开始，
        顺序扫描 ~4KB 的 Record Batch，
        直到找到 offset = 61234 的那条消息并返回
```

> **稀疏索引的设计巧思**：如果做稠密索引（每条消息一条索引），索引体积会和消息本体差不多大；稀疏索引使索引体积降到 ~1/1000，可常驻 PageCache，用一次"局部顺序扫描"换"极小的内存占用"，综合性能最优。

---

**Q9：HW（High Watermark）和 LEO（Log End Offset）分别是什么？它们与副本同步、消费者可见性之间是什么关系？**

**答：**

HW 和 LEO 是 Kafka 副本同步机制中两个核心的 offset 指针，决定了"数据写到哪了"和"消费者能读到哪"。

**（1）概念定义**

针对**单个分区副本**（无论 Leader 还是 Follower）：

| 指针 | 含义 | 谁维护 |
|------|------|-------|
| **LEO（Log End Offset）** | 该副本日志**下一条要写入的位置**，即"当前已写消息数 = LEO"（offset 0 ~ LEO-1 是已落盘的） | 每个副本独立维护，写入新消息后 +1 |
| **HW（High Watermark）** | 该分区**所有 ISR 副本都已确认同步到的 offset**，即 offset 0 ~ HW-1 的消息是"已提交"的，对消费者可见 | Leader 维护，周期性更新；Follower 只被动同步 Leader 的 HW 值 |

**（2）三者关系（同一时刻）**

对 Leader 而言，必须满足：

```text
Consumer 可见消息范围     = [0, Leader.HW)
Leader 已写入消息范围     = [0, Leader.LEO)
最慢 Follower 已写入范围 = [0, min{ Follower_i.LEO for i in ISR })

因此 Leader.HW = min(Leader.LEO, min{Follower_i.LEO for i in ISR})
```

即：**HW = ISR 中所有副本 LEO 的最小值**，也叫"最小同步点"。

**（3）更新流程（一条消息从写入到可见的生命周期）**

```text
时刻 T0：
  Producer 向 Leader 发 msg(offset=N)，acks=all
  Leader 本地写入 → Leader.LEO = N+1
  Leader 更新 HW 仍为 min(N+1, 旧FollowerLEO) = 旧值  // Follower 还没同步
  Consumer Fetch 时，Leader 只返回 < HW 的消息 → N 不可见

时刻 T1：
  Follower A Fetch 到 N，写入本地，FetchRequest 中携带 A.LEO = N+1
  Leader 收到后记录 A.LEO = N+1

时刻 T2：
  Follower B 也 Fetch 到 N，B.LEO = N+1
  Leader 此时 ISR 中所有 LEO 均为 N+1
  → Leader 更新 HW = min(Leader.LEO=N+1, A.LEO=N+1, B.LEO=N+1) = N+1

时刻 T3：
  下次 Follower Fetch 响应或下次 Fetch 请求的 response header 中携带 Leader.HW = N+1
  Follower 据此更新自己的 HW
  下次 Consumer Fetch → N 落入 [0, HW)，可见，正常返回

时刻 T4：
  Leader 向 Producer 发送 ProduceResponse(ACK)，acks=all 语义完成
```

**（4）关键结论**

1. **消费者永远读不到 ≥ HW 的消息**——这是 Kafka 实现"读一致性"的核心，即使 Follower 追上来但 Leader 的 HW 还没更新，消息对消费端也不可见；
2. **Leader 切换时的一致性保证**：新 Leader 的 HW 被认为是"至少所有旧 ISR 都有的消息"，因此切换后消费者不会读到丢失的消息（实际上切换后新 Leader 还会执行一次"HW 截断对齐"，保证自己不会暴露旧 HW 之后的不一致消息）；
3. **LeaderEpoch 的引入**：早期版本仅靠 HW 会有"新 Leader 选上但 LEO 没到 HW，Follower 按照旧 HW 截断自己日志导致数据丢失"的边界问题，Kafka 0.11+ 引入 LeaderEpoch（每次 Leader 切换 +1）+ EpochStartOffset 做更细粒度截断，彻底修复此问题。

---

### 2.4 可靠性与一致性

---

**Q10：从生产者、Broker、消费者三个层面，说明如何配置和设计才能实现 Kafka 的"不丢消息"（At-Least-Once 语义）。**

**答：**

Kafka 的 At-Least-Once（至少不丢）语义需要**生产端 + Broker 端 + 消费端三方协同配置**，任何一方配置不当都会引入数据丢失风险。

**（1）生产者端：保证消息至少被 Broker 成功接收**

| 配置项 | 推荐值 | 作用 |
|--------|-------|------|
| `acks` | `all`（或 `-1`） | 必须等 ISR 全部副本确认才 ACK，避免"Leader 刚写就宕机"丢失 |
| `enable.idempotence` | `true` | 配合 acks=all，开启幂等防止重试导致重复写入，同时避免乱序 |
| `retries` | ≥ 3（如 `2147483647` 即 IntMax） | 对可重试异常（NotLeader、NetworkException、Timeout）自动重试，**不要设为 0** |
| `retry.backoff.ms` | 100 ~ 1000 | 重试间隔，避免瞬间打满 Broker |
| `max.in.flight.requests.per.connection` | ≤ 5 | 幂等模式下该值 ≤5 才能保证单分区内顺序不颠倒 |
| `buffer.memory` | ≥ 33554432（32MB 以上） | 避免业务高峰时 RecordAccumulator 打满导致 `send()` 阻塞超时抛异常 |
| `delivery.timeout.ms` | ≥ 120000（2min） | 单次发送的总超时（含等待入缓冲 + 凑批 + 发送 + 重试），需 ≥ `request.timeout.ms + linger.ms` |
| **代码层面** | 使用带 Callback 的 `send()` + 处理异常 | 回调中捕获异常；对不可重试异常（MessageTooLarge、RecordTooLarge）打告警并持久化到死信队列，**不能只 fire-and-forget** |

```java
// 推荐的生产端发送代码
producer.send(record, (metadata, exception) -> {
    if (exception != null) {
        if (exception instanceof RetriableException) {
            log.warn("可重试异常，已自动重试 {} 次", record, exception);
        } else {
            log.error("发送失败，落至死信表 {}", record, exception);
            deadLetterService.save(record, exception);   // 关键：不可重试不能丢
        }
    }
});
```

**（2）Broker 端：保证写入的消息被持久化且副本一致**

| 配置项 | 推荐值 | 作用 |
|--------|-------|------|
| `replication.factor` | ≥ 3（生产环境） | 多副本容忍单机/单机房故障 |
| `min.insync.replicas` | `replication.factor - 1`（3 副本时设为 2） | 和 acks=all 配合，ISR 至少有 N 个写成功才允许提交 |
| `unclean.leader.election.enable` | `false` | **严禁非 ISR 副本参与选举**，防止数据丢失换可用性 |
| `auto.create.topics.enable` | `false` | 禁止隐式创建 Topic（默认 1 分区 1 副本！），所有 Topic 必须显式按规范创建 |
| `log.flush.interval.messages` / `log.flush.interval.ms` | **不建议手动调**（交给 OS PageCache flush） | Kafka 依赖 OS 的 write-behind 策略做异步刷盘，手动强制 flush 会严重降低性能；副本数 + acks=all 已经提供了足够的不丢保证 |

**（3）消费者端：保证业务至少处理成功**

| 配置项 | 推荐值 | 作用 |
|--------|-------|------|
| `enable.auto.commit` | `false` | 关闭自动提交，避免"还没处理完就提交了，进程挂了 → 丢消息" |
| **代码层面** | "先处理，后提交" 原则 | 只有业务逻辑（DB 写成功、下游调用成功、文件落盘成功）真正执行完，才调用 `commitSync()` 或 `commitAsync()` |
| **代码层面** | 死信队列 + 告警兜底 | 对 `process()` 中抛出的业务异常，重试 N 次仍失败后写入 `{topic}.DLT`（死信队列）或 DB 死信表，人工介入补数，**禁止 catch 后直接跳过不处理也不告警** |

```java
// 推荐消费模板：处理成功才提交；失败落死信
while (running.get()) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofSeconds(1));
    Map<TopicPartition, OffsetAndMetadata> toCommit = new HashMap<>();
    for (ConsumerRecord<String, String> r : records) {
        try {
            businessLogic.process(r);                          // 业务处理
        } catch (Exception e) {
            log.error("处理失败，record={}", r, e);
            deadLetterProducer.send(r.topic() + ".DLT", r.key(), r.value(), e);
        }
        // 无论成功或失败（失败的已经落死信了），都认为"消费端完成"，推进 offset
        toCommit.put(new TopicPartition(r.topic(), r.partition()),
                     new OffsetAndMetadata(r.offset() + 1));
    }
    if (!toCommit.isEmpty()) {
        consumer.commitSync(toCommit);
    }
}
```

**（4）总结：三层不丢的闭环**

```text
Producer 端：acks=all + 幂等 + 重试 + 回调异常落死信
       ↓ (保证到达Broker副本)
Broker 端：RF=3 + min.ISR=2 + unclean选举关闭
       ↓ (保证副本持久化)
Consumer 端：enable.auto.commit=false + 先处理后提交 + 死信兜底
```

三层都做到时，Kafka 可以在 "1 个 Broker 故障、1 次网络闪断、1 次消费进程 OOM" 等常见故障组合下，保证**业务数据零丢失**（At-Least-Once + 业务幂等 = 业务视角 Exactly-Once）。

---

**Q11：什么是 Kafka 的幂等生产者？什么是事务？两者的区别与适用场景是什么？**

**答：**

幂等生产者和事务是 Kafka 0.11 版本推出的两大 Exactly-Once 基础能力，前者解决"单生产者写单分区不重复"，后者在其基础上提供"跨分区、跨 Topic、消费-生产全链路的原子写入"。

**（1）幂等生产者（Idempotent Producer）**

- **开启方式**：`props.put("enable.idempotence", "true")`（开启后 acks 默认 = all，max.in.flight 默认 = 5，retries 默认 = IntMax）
- **解决的问题**：Producer 发送请求因网络抖动 ACK 丢失，Producer 重试但 Broker 实际已经写入的情况下，**不会出现"同一条消息被写入两次"**，也不会出现乱序。
- **原理（三元组去重）**：
  1. Producer 初始化时，Broker 分配一个全局唯一的 PID（Producer ID），客户端无感知；
  2. 同一 PID 下，每个 `<PID, Partition>` 维度维护一个单调递增的 Sequence Number；
  3. 消息携带 `<PID, Partition, Seq>` 三元组写入 Broker；
  4. Broker 端为每个 `<PID, Partition>` 缓存最新的 Seq：
     - 收到的 Seq == 缓存 Seq + 1 → 正常写入，缓存更新；
     - 收到的 Seq ≤ 缓存 Seq → **判定为重复写入，直接丢弃，返回成功**（保证幂等）；
     - 收到的 Seq > 缓存 Seq + 1 → 出现空洞，抛 `OutOfOrderSequenceException`。
- **局限性**：
  1. **PID 跨进程/跨会话不持久**：Producer 重启后 PID 变了，跨重启的重复消息无法去重；
  2. **只能在单 Partition 内生效**：跨多个分区的写入是否"要么都成功要么都失败"，幂等生产者管不了；
  3. **无法串联 offset 提交**：如果是"消费 A → 处理 → 写回 B"场景，幂等只能保证写回 B 不重复，但"写回 B 成功但 offset 提交失败"这种跨操作的原子性管不了。

**（2）Kafka 事务（Transactions）**

- **开启方式**：
  ```java
  props.put("transactional.id", "my-tx-producer-001");  // 指定事务ID，跨进程持久
  producer.initTransactions();
  ```
- **解决的问题**：
  1. 跨多个 Topic、多个 Partition 的多条消息"**原子写入**"——要么全部对外可见，要么全部不可见；
  2. 串联"消费 Source Topic → 处理 → 写回 Sink Topic + 提交 Source Offset"全流程的原子性，即所谓的"读-处理-写（Read-Process-Write）"模式，实现端到端 EOS。
- **原理简述**：
  1. Transactional ID 与 PID 通过 `transactional.id → PID` 映射持久保存在 Broker 端（内部 Topic `__transaction_state`，默认 50 分区），Producer 重启后通过相同 Transactional ID 拿回原 PID，跨重启去重；
  2. 事务开始后，Producer 向 Broker 发 `AddPartitionsToTxnRequest` 标记哪些分区属于该事务；
  3. 写消息时在 Record Batch 中打事务标记位，消息写入目标分区后 Broker 暂时对 `isolation.level=read_committed` 的消费者隐藏；
  4. `commitTransaction()` 时：
     - 先 `sendOffsetsToTransaction(offsets, groupId)` 把消费 offset 作为一种"特殊消息"写入 `__consumer_offsets` 的事务分区；
     - 向事务协调者发 `EndTxnRequest(COMMIT)`，协调者写 `COMMITTED` 标记；
     - 各目标分区的 Leader 在 `.log` 末尾追加一个事务 Marker（CONTROL_BATCH，标记 COMMIT/ABORT）；
  5. 消费者 `isolation.level=read_committed`（事务型消费）：Fetch 时遇到事务 Marker 前的未提交消息一律"跳过不返回"，只返回已 COMMIT 的消息，以及所有非事务消息。
- **适用场景**：
  - Kafka Streams、KSQL 的内部计算（map/filter/join/aggregation 要求 EOS）；
  - 自己实现的流式 ETL：`TopicA → ETL 加工 → TopicB`，中间不能丢也不能重复；
  - 金融级场景：扣款事件 + 账单事件必须同时出现或同时不出现。

**（3）两者对比总结**

| 维度 | 幂等生产者 | 事务 |
|------|----------|-----|
| **开启代价** | 非常低，几乎无性能损耗 | 较高（写事务标记、协调者 RPC、Marker 追加），吞吐下降 10%~30% |
| **去重范围** | 单 PID 会话内、单分区内 | 跨 PID 重启、跨分区、跨 Topic |
| **原子性** | 无原子性保障（每条消息独立） | 提供 ACID 中的原子性（一批消息要么全可见要么全不可见） |
| **串联消费 offset** | 不支持 | 支持 `sendOffsetsToTransaction` |
| **消费者要求** | 无特殊要求 | 消费端需设置 `isolation.level=read_committed` |
| **失败语义** | 单条消息失败不影响其他 | 一批消息整体回滚（ABORT），对消费端不可见 |
| **最适合场景** | 普通业务写入（90% 场景够用） | Kafka Streams / 跨 Topic 原子写入 / 端到端 EOS / 金融级场景 |

> 一个常见误解：`enable.idempotence=true` 不是事务的子集。事务内部**必须**开启幂等——但事务是建立在幂等 + 事务协调者 + 事务标记 + read_committed 之上的一整套机制。


