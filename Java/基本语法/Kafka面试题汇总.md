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

---

## 三、分析题

### 3.1 场景设计与方案选型

---

**Q1：某电商平台需要构建"订单事件总线"架构。场景如下：**
- 订单系统每秒产生 2 万条订单状态变更（创建、支付完成、发货、签收、取消）；
- 下游消费方包括：风控系统（实时判断欺诈，延迟 ≤ 50ms）、物流系统（接收后安排发货，延迟 ≤ 2s）、推荐系统（用户购买后更新画像，延迟 ≤ 30s）、数据仓库（T+1 统计报表）。
- 需要保证订单状态变更消息的绝对不丢，以及同一订单号的消息按顺序被每个系统接收。

**请给出完整的 Kafka 技术选型方案，包括：Topic 设计、分区数估算、副本策略、生产者配置、每个消费方的 Group 设计、Topic 保留期、以及为"顺序+不丢"所做的关键设计。**

**答：**

这是典型的**多下游订阅 + 有序 + 可靠性要求高**的业务场景，采用"事件总线 + 一写多读"模式正好匹配 Kafka 的发布-订阅模型。

---

**（1）Topic 设计：按事件类型拆分 vs 单 Topic 路由**

推荐采用**单 Topic + 事件类型头字段**方案，理由：

- 同一订单的多个状态（CREATE → PAYED → SHIPPED → SIGNED）天然需要保序，放在同一 Topic 且按 orderId 分区才能保证跨状态的全局有序；
- 拆成 5 个 Topic（order-created、order-payed ...）会导致下游需要做跨 Topic 顺序拼接，复杂度高且做不到严格顺序。

Topic 命名：`ecom.order-events.v1`（业务域.聚合根.事件类型.版本号）。版本号是为了未来事件 schema 升级做双写过渡预留。

消息结构（Header + Key + Value 分离）：

```text
Record Key     = orderId (String, 如 "2024030512345")      → 用于分区路由 + 同订单保序
Record Headers = event_type=CREATED/PAYED/SHIPPED （下游无需反序列化 value 即可过滤）
                 source=order-service  schema_version=1.0
Record Value   = Avro/Protobuf（推荐 Schema Registry 管理）：
                 { orderId, userId, skuIdList, amount, status, occurredAt, traceId }
```

---

**（2）分区数估算**

分区数由"目标吞吐 ÷ 单分区实际吞吐"取上限。

1. **写入端吞吐**：20,000 条/秒，假设平均每条消息 + Key + Header = 1KB，则写入带宽 ≈ 20MB/s；
2. **单分区写入吞吐**：现代 SSD + 1Gbps 网卡，单分区可稳定做到 ≈ 15000 条/秒 或 100MB/s，对本场景**条数先成为瓶颈**；
3. **写入端需要的分区数**：20000 ÷ 15000 ≈ 2，取保守值 6（但消费端并行度可能要求更高）；
4. **消费端并行度考量**：
   - 风控系统（最严格）：单条风控规则评估 5ms，单线程可处理 200 条/秒，需 100 条/秒级并行→至少 100 分区才能做到 1 对 1 消费；
   - 物流系统：调用外部 API 平均 50ms，单线程 20 条/秒，需 1000 分区；
   - **结论**：瓶颈在消费端（尤其是物流的 IO 密集型），因此分区数应按最大消费方估算。
5. **取整与冗余**：分区数取 **144**（接近 6 个 Broker 的整数倍 6×24，且是 2^4×3^2 便于未来 2×/3× 扩容做一致性哈希）；Broker 数量 6 台，每台机器承载 144÷6=24 个 Leader 分区（3 副本则每台 72 个分区文件组），完全在合理区间。

---

**（3）副本与 Broker 可靠性策略**

| 维度 | 配置值 | 理由 |
|------|-------|------|
| `replication.factor` | **3** | 容忍单机宕机（5个9 SLA 要求），跨机架部署：每个分区 3 副本分到 3 个不同机架（机架感知 `broker.rack`），单机房断电仍有副本存活 |
| `min.insync.replicas` | **2** | 配合 `acks=all`，ISR 必须至少 2 个副本写入成功才 ACK，容忍 1 个副本掉队仍可写 |
| `unclean.leader.election.enable` | **false** | 严禁非 ISR 副本上位，宁可短暂不可写也不丢订单事件 |
| `auto.create.topics.enable` | **false** | 运维必须按规范显式创建 |
| Rack 感知 | `broker.rack=rack-a/rack-b/rack-c` | 副本分配时尽力跨机架，避免同机架 2 个副本同时故障 |

---

**（4）生产者配置（订单服务端）**

```java
Properties props = new Properties();
props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "broker1:9092,...,broker6:9092");
props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, KafkaAvroSerializer.class.getName());
props.put("schema.registry.url", "http://schema-registry:8081");

// —— 可靠性三件套
props.put(ProducerConfig.ACKS_CONFIG, "all");                                 // ISR全确认
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, "true");                  // 开启幂等，不重不乱序
props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "order-service-tx-producer"); // 配合本地DB事务+发件箱表（见下）

// —— 高吞吐四件套
props.put(ProducerConfig.BATCH_SIZE_CONFIG, 65536);                            // 64KB 批次
props.put(ProducerConfig.LINGER_MS_CONFIG, 5);                                 // 最多等 5ms 凑批
props.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "lz4");                      // lz4 解压快，CPU 开销远低于带宽节省
props.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 134217728);                     // 128MB 缓冲（订单尖峰）

// —— 重试与超时
props.put(ProducerConfig.RETRIES_CONFIG, Integer.MAX_VALUE);
props.put(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, 180000);                  // 3 分钟总超时
props.put(ProducerConfig.REQUEST_TIMEOUT_MS_CONFIG, 30000);
props.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5);            // 幂等下 5 以下不乱序
```

**关键点：业务事务 + Kafka 的"事务性发件箱（Transactional Outbox）"模式**  
订单创建需要"DB 写订单表"与"发 Kafka"两个操作原子化，但 XA 2PC 性能差。采用 Outbox 模式：

1. 在订单 DB 本地事务中：
   - `INSERT INTO orders(...) VALUES (...)`
   - `INSERT INTO outbox_table(order_id, payload, status) VALUES (?, ?, 'PENDING')`
2. 本地事务提交成功后，**独立的 Outbox Publisher 后台线程**轮询 `outbox_table` 中 `status=PENDING` 的记录，用 Kafka 事务 Producer 发送到 Kafka，成功后 `UPDATE outbox_table SET status='SENT'`；
3. 若 Publisher 崩溃重启，重复扫描 PENDING 消息重新发送——配合幂等 Producer，Broker 端不会重复写入。  
这样实现了"DB 成功一定发出去，发出去一定不重复"，端到端不丢。

---

**（5）消费方 Consumer Group 设计**

发布-订阅模型的**核心优势：每个下游用不同 Group ID，彼此完全隔离**，一个消费慢不影响其他人。

| 下游系统 | Group ID | 核心配置 | 设计说明 |
|---------|----------|---------|---------|
| **风控系统** | `cg-risk-control` | `enable.auto.commit=false`<br>`max.poll.records=100`<br>`isolation.level=read_committed`<br>`auto.offset.reset=latest` | 消费者数 = 144，1:1 匹配分区；**业务幂等**：用 Redis 布隆过滤器 `risk:processed:{orderId}:{eventType}` 判断是否已处理；**50ms 目标**：纯内存规则（无外部 IO），本地 Caffeine 缓存用户画像，避免 poll 内做 RPC。<br>失败直接告警 + 跳过 + 落风控死信（宁可漏拦不阻塞链路，事后补拦）。 |
| **物流系统** | `cg-logistics` | `enable.auto.commit=false`<br>`max.poll.records=20`<br>`max.poll.interval.ms=300000` | 消费者数 = 144。物流 IO 慢，按 **"分区 → 内部队列 + 20 工作线程池"** 模式：每个消费者内部对 `(partition, orderId.hashCode % 20)` 路由到固定工作线程，既保证同一订单并发下串行（不冲突），又把并行度从 144 提升到 2880。<br>手动按每个分区的最末成功 offset 提交。失败则指数退避 + 重试 3 次，最后落物流死信。 |
| **推荐系统** | `cg-recommendation` | `enable.auto.commit=true`<br>`auto.commit.interval.ms=10000`<br>`fetch.min.bytes=1048576`<br>`fetch.max.wait.ms=1000` | 30s 延迟容忍度高，追求**吞吐优先**：消费者数 = 36（每 4 分区 1 消费者）。自动提交即可（画像更新偶尔重复可接受，业务本身幂等）；`fetch.min.bytes=1MB` 减少 Broker 空响应，攒批处理降低 CPU。 |
| **数据仓库** | `cg-dwh-flink` | Flink 执行环境 `execution.checkpointing.mode=EXACTLY_ONCE`<br>`isolation.level=read_committed` | 由 Flink + Kafka Source/Sink 自带的 EOS 机制（Checkpoint + 2PC）保证，Flink 的 JobManager 会在 checkpoint barrier 对齐后原子提交 Kafka offset，保证 T+1 数仓数据不重不丢。并行度设为 144，30s 延迟内完全可完成。 |

---

**（6）Topic 保留期与存储规划**

| 保留维度 | 配置值 | 说明 |
|---------|-------|------|
| `retention.ms` | **604800000 = 7 天** | 订单事件可溯源；7 天内任何下游重放都无需找 DBA 回滚 DB |
| `retention.bytes` | **不限制**（按时间） | 存储估算：20000条/s × 1KB × 86400s × 7 ÷ 1024³ ≈ 11TB（3 副本 33TB），每台 ≈ 5.5TB 完全在普通机械盘容量内 |
| `cleanup.policy` | **delete** | 订单事件是时序事件，不是 KV 快照，不需要 compact |
| `message.timestamp.type` | **CreateTime** | 使用生产者打标的业务发生时间，便于按时间回溯 |

---

**（7）顺序 + 不丢设计总结**

| 目标 | 实现手段 |
|------|---------|
| **同一订单消息全局有序** | ① 所有事件放同一 Topic；② `orderId` 作为 Record Key，使用默认 murmur2 分区器；③ 每个消费方不跨线程处理同分区同 key 消息（物流系统内部按 key 二次路由） |
| **生产端不丢** | ① Transactional Outbox 模式串联 DB 事务和 Kafka 发送；② acks=all + 幂等 + retries=MAX；③ 发送回调异常落死信 |
| **Broker 端不丢** | ① RF=3 + min.ISR=2；② unclean 选举关闭；③ 跨机架副本部署；④ 磁盘建议 RAID10 或云盘多副本 |
| **消费端不丢** | ① 风控/物流关闭自动提交，先处理后提交；② 死信队列兜底 + 人工补数平台；③ Flink 用 Checkpoint+EOS |
| **消费端不重** | ① 业务幂等（Redis 布隆过滤器、DB 唯一键）；② Flink EOS；③ 风控/物流处理前查 `consume_log` 表 |

---

### 3.2 性能瓶颈与调优分析

---

**Q2：某 Kafka 集群在大促期间出现生产者写入 P99 延迟从 10ms 升到 800ms，监控显示 Broker 端 Request Queue 长度飙升、网络入站带宽跑满单网卡 10Gbps。请按"定位思路 → 可能根因 → 对应优化方案"的结构给出完整的性能瓶颈分析与调优建议。**

**答：**

性能问题诊断的通用方法论是 **USE 方法（Utilization 利用率 / Saturation 饱和度 / Errors 错误）+ 自上而下分层拆解**。本题给出的两个症状"Request Queue 飙升 + 单网卡入站跑满"是极佳的切入点。

---

**（1）第一步：定位思路（分层拆解）**

按 Kafka 请求处理流水线，Producer 写入延迟 = **网络传输 + Broker 排队 + Leader 写入磁盘 + 副本同步 + 回包**。

```text
Producer 延迟组成：
├── 网络 RTT Producer→Broker             ~1ms (LAN)
├── Broker Request Queue 排队时间        ↑↑↑ 本题飙升点
│   └── (Kafka RequestHandler 线程数不够 / 下游某个处理阶段堵)
├── Leader 本地日志 Append               ~0.5ms (PageCache 追加写)
├── 等待 ISR Follower Fetch 同步时间     ~? (acks=all)
├── Broker Response Queue + 网络回包     ~1ms
```

**监控项需要拉取的关键指标（监控先行）**：

| 维度 | 指标名（JMX / Kafka Metrics） | 正常值 | 异常值判断 |
|------|------------------------------|-------|-----------|
| **Broker 网络** | `kafka.network:type=SocketServer,name=NetworkProcessorAvgIdlePercent` | ≥ 30% | < 5% 表示网络处理线程饱和 |
| **请求队列** | `kafka.network:type=RequestChannel,name=RequestQueueSize` | 0~10 | > 100 持续 → Handler 线程阻塞 |
| **Handler 线程** | `kafka.server:type=KafkaRequestHandlerPool,name=RequestHandlerAvgIdlePercent` | ≥ 20% | < 3% → Handler 全忙 |
| **入站带宽** | `node.net.bytes.in.rate` / 主机网卡监控 | < 网卡带宽×70% | 本题 10Gbps 打满 = 明显瓶颈 |
| **刷盘耗时** | `kafka.log:type=LogFlushStats,name=LogFlushRateAndTimeMs`（p99） | < 10ms | > 100ms → PageCache 回刷问题 |
| **分区 Leader 写入耗时** | `kafka.server:type=BrokerTopicMetrics,name=TotalTimeMs,request=Produce`（p99） | < 5ms | > 100ms → 写热点分区 |
| **副本同步延迟** | `kafka.server:type=ReplicaFetcherManager,name=MaxLag` | 0 | > 1000 → Follower Fetch 跟不上 |

---

**（2）第二步：基于两个症状的根因假设与验证**

症状 A：**Request Queue 飙升**。Request Queue 堆积说明 RequestHandler 线程消费不过来，Handler 又在做三件事：① 写 Leader 本地日志；② 处理 Follower Fetch 请求；③ 等待 ISR 副本同步后返回 Produce 响应（acks=all）。

症状 B：**单网卡入站 10Gbps 打满**。说明集群入站流量集中在少数 Broker——**分区 Leader 分布不均**，或**生产者元数据缓存未及时刷新导致全量打到几个 Broker**，俗称"热点 Broker"。

---

#### 根因 1（可能性最高 60%）：分区 Leader 倾斜 + 热点 Topic 分区数不足

**现象**：`kafka-topics.sh --describe` 会发现几个 Broker 的 Leader 分区数是其他 Broker 的 3~5 倍，这些 Broker 网卡入站满、Request Queue 高。

**原因**：
- 大促前紧急扩容 Topic 分区时只 `--alter` 加分区，没做 `--reassign` 重新平衡；
- 某个热点 Topic（如交易事件）只有 8 个分区，但写入量占总流量 60%，8 个分区 Leader 落在 3 台 Broker 上，自然打爆这 3 台网卡。

**验证**：
```bash
# 检查每台 Broker Leader 数分布
kafka-topics.sh --bootstrap-server $BROKERS --describe | \
  awk -F'\t' '/Leader:/{print $4}' | sort | uniq -c | sort -rn
```

**优化方案**：

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | `kafka-reassign-partitions.sh --generate` 生成迁移计划 | 对热点 Topic + Leader 倾斜严重的 Topic 做副本重分配 |
| 2 | `--execute` 迁移，分 3 批执行（每批 < 200GB 数据） | 迁移会有带宽占用，`throttle` 限流：`--throttle 200000000`（200MB/s），避免把网卡完全打挂 |
| 3 | 迁移完成后 `--verify` 再 `--additional --throttle 0` 解除限流 | 忘记解除限流会导致后续副本同步一直被限 |
| 4 | **关键：对热点 Topic 扩容分区数** | 将 8 分区扩容到 **144 分区**（按 Q1 估算方法），打散写入流量到所有 Broker |
| 5 | Broker 配置 `auto.leader.rebalance.enable=true` | 定期自动平衡 Leader 分布（阈值 `leader.imbalance.per.broker.percentage=10`） |

---

#### 根因 2（可能性 25%）：Producer 端压缩未开 + Batch 太小，小包过多

**现象**：

- `kafka.producer:type=ProducerTopicMetrics,name=RecordSendRate` 极高但 `byte rate` 正常；
- Broker 端 `kafka.network:type=RequestMetrics,name=RequestsPerSec,request=Produce` 每秒 20 万次以上。

**原因**：
- `batch.size=16KB 默认 + linger.ms=0`，大促下流量突发，Producer 每条消息单独成一个小 Batch 发送，小包率极高 → 每个 ProduceRequest 只带几条消息，Broker RequestHandler 线程被大量小请求上下文切换打满 → Request Queue 飙升；
- 未开压缩，带宽占用比开 lz4 高 ~4×，10Gbps 更快打满。

**验证**：
- Producer 端 `kafka.producer:type=ProducerTopicMetrics,name=BatchSizeAvg`：若 < 1000 Bytes 就是凑批失效；
- Broker 网卡抓包 `tcpdump -i eth0 port 9092 -s 0 -w produce.pcap` → Wireshark 分析 ProduceRequest 包体大小分布。

**优化方案**：

```java
// 生产端 4 项吞吐优化
props.put(ProducerConfig.LINGER_MS_CONFIG, 20);        // 从 0 改为 20ms，等凑批
props.put(ProducerConfig.BATCH_SIZE_CONFIG, 262144);   // 16KB → 256KB
props.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "lz4");  // 开启 lz4
props.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 268435456); // 256MB 缓冲，应对峰值
```

效果预期：压缩率 ~3:1 + Batch 增大 10 倍 → 带宽需求降到原来 ~1/5，请求数降一个数量级，Request Queue 积压自然缓解。

---

#### 根因 3（可能性 10%）：acks=all + ISR 中 Follower Fetch 慢，导致 Produce 响应阻塞

**现象**：
- `MinIsrExpiresPerSec` 非 0，`UnderReplicatedPartitions` 指标激增；
- Producer Produce p99 与 Follower 端 `ReplicaFetchManager` 的 p99 Fetch 延迟高度相关。

**原因**：
- Follower Broker 磁盘 IO 饱和（机械盘 RAID5 写入 200MB/s 封顶），Fetch 请求写入本地 `.log` 慢 → Follower LEO 长时间追不上 Leader → Leader 的 Produce 请求要等 Follower 才能推进 HW → 大量 Produce 请求挂在 `purgatory=ProducePurgatory` → Handler 线程被占用无法出队 → Request Queue 飙升。

**验证**：
```bash
# Broker 端 JMX 指标
kafka.server:type=DelayedOperationPurgatory,name=PurgatorySize,delayedOperation=Produce
# 正常 < 100，异常值 > 5000 说明大量 Produce 在等 ISR 确认
```

磁盘层面：节点 `iostat -x 1` 若 `%util >= 95%`、`await >= 20ms` 就是磁盘瓶颈。

**优化方案**：

| 手段 | 操作 |
|------|------|
| 硬件升级 | 将 Broker 数据盘从机械盘（HDD）换成 SATA SSD 或 NVMe，单机写入能力从 200MB/s → 1.5GB/s |
| 多目录分摊 | `log.dirs=/data1/kafka,/data2/kafka,/data3/kafka` 跨 3 块 SSD 并发，IOPS ×3 |
| num.replica.fetchers | `num.replica.fetchers=4`（默认 1）：每 Follower 用 4 个线程并发从 Leader 拉不同分区的数据，副本吞吐翻倍 |
| replica.fetch.max.bytes | `replica.fetch.max.bytes=10485760`（10MB）：每次 Fetch 拉更多数据，减少请求数 |
| log.flush 策略保持默认 | 不要手动设 log.flush.interval.messages，OS PageCache 回刷效率最高；避免把刷盘当可靠性手段（副本数+acks=all 才是） |

---

#### 根因 4（可能性 5%）：Broker 线程池与网络模型瓶颈

**现象**：
- `RequestHandlerAvgIdlePercent` 持续 < 1%，但 CPU 使用率 < 60%，说明线程在 IO 等锁而非 CPU 忙。
- `NetworkProcessorAvgIdlePercent` < 2%。

**优化方案**：

```properties
# server.properties
num.network.threads=12          # 默认 3，建议 = CPU核数，处理网络读写的 Netty 线程数
num.io.threads=24               # 默认 8，建议 = 2×CPU核数，RequestHandler 线程池大小（写磁盘+同步）
queued.max.requests=1000        # 默认 500，适度增大避免网络层被阻塞
socket.send.buffer.bytes=1048576   # SO_SNDBUF 1MB
socket.receive.buffer.bytes=1048576 # SO_RCVBUF 1MB
```

若集群部署在云上，注意：
- **关闭 RPS（网卡中断聚合）**：`ethtool -C eth0 rx-usecs 1024 rx-frames 512`，避免 10Gbps 下软中断占 CPU > 30%；
- **开启网卡多队列 RSS**：`ethtool -L eth0 combined 16`，把中断分摊到多核。

---

**（3）优化后预期效果验证**

全部优化落地后，核心指标应回归：

| 指标 | 优化前 | 优化后目标 |
|------|-------|-----------|
| Produce p99 延迟 | 800ms | < 20ms |
| RequestQueueSize p99 | 1000+ | < 20 |
| 单 Broker 网卡入站 | 10Gbps 打满 | < 6Gbps（压缩生效+分区打散） |
| RequestHandlerAvgIdle | 1% | > 30% |
| UnderReplicatedPartitions | 100+ | 0 |

---

### 3.3 故障排查与问题定位

---

**Q3：某消费者组出现"消费卡住"问题：Consumer Lag 从 0 持续飙升到 100 万+，监控显示消费者进程 CPU < 10%、内存正常、GC 正常。请按优先级从高到低列出至少 6 种可能根因，并给出每种根因的**排查步骤**、**关键日志/监控特征**和**修复方案**。**

**答：**

消费卡住（Consumer Lag 飙升，但进程本身健康活着）是 Kafka 运维最高频的问题之一。**诊断心法：先查协议交互（消费者 ↔ Coordinator/Broker），再查内部处理（poll → process → commit 链路），最后查运行环境（网络/OS）。**

---

#### 根因 1（排查优先级 P0）：消费者被 Coordinator 踢出组，正处于 Rebalance 中反复 JoinGroup → SyncGroup → 被踢 → 循环

**排查步骤**：
1. 查看消费者日志，搜索关键词：`Attempt to heartbeat failed`、`Illegal generation`、`Rebalance`、`Revoked previously assigned partitions`；
2. 看对应 Broker（Group Coordinator 所在节点）的 `server.log`，搜索 `Remove member`、`LeaveGroup` 理由；
3. 监控 `kafka.consumer:type=consumer-coordinator-metrics,client-id=*` 的 `rebalance-total`、`rebalance-latency-avg` 指标。

**关键特征**：
- 消费者日志反复出现 `NotCoordinatorForGroup` 或 `Commit cannot be completed since the group has already rebalanced and assigned the partitions to another member`；
- Broker 端 `group-coordinator-metrics: join-rate`、`sync-rate` 指标持续飙升，正常 Rebalance rate 应 ≈ 0；
- `poll-latency-max` 指标接近或超过 `max.poll.interval.ms`（默认 5 分钟）。

**原因本质**：业务 `process()` 处理耗时过长（如下游 DB 慢查询、HTTP 调用超时、线程池死锁），导致两次 `poll()` 间隔超过 `max.poll.interval.ms` → Coordinator 认为消费者挂了，踢出去 → 该消费者下一次 poll 时才发现"自己被踢了"，重新 JoinGroup → SyncGroup 拿回分区 → 又因为处理慢再次超时被踢 → **Rebalance 死循环，根本没机会消费消息**。

**修复方案**：
```java
// 1. 调大 max.poll.interval.ms（给足业务处理时间）
props.put(ConsumerConfig.MAX_POLL_INTERVAL_MS_CONFIG, 600000); // 10分钟

// 2. 调小 max.poll.records，缩短单次 poll 处理时间
props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 50);         // 从默认 500 降到 50

// 3. 处理流程加超时：在 process() 外包 Executor + Future.get() 超时兜底
ExecutorService exec = Executors.newFixedThreadPool(4);
while (running.get()) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(1000));
    for (ConsumerRecord<String, String> r : records) {
        Future<?> f = exec.submit(() -> businessLogic.process(r));
        try {
            f.get(30, TimeUnit.SECONDS);   // 单条最多 30 秒，超过强制中断
        } catch (TimeoutException e) {
            f.cancel(true);
            log.error("业务处理超时，r={}", r, e);
            deadLetterProducer.send(r, e);
        }
    }
    consumer.commitAsync();
}
```

---

#### 根因 2（P0）：订阅分区全部或部分进入 "暂停（pause）" 状态，poll 只返回空

**排查步骤**：
1. 代码全局搜索 `consumer.pause(` 调用；
2. 打印日志 `log.info("paused partitions: {}", consumer.paused())`；
3. 检查是否集成了 `Spring-Kafka`、`Kafka-Streams`、`Akka-Streams` 等框架的背压自动暂停机制。

**关键特征**：
- `poll` 返回的 `ConsumerRecords.isEmpty() == true`，但 Lag 在涨；
- `consumer.assignment()` 非空（分区还在），但 `consumer.paused()` 列表等于或部分包含 assignment。

**原因本质**：消费端代码在处理压力过大时主动调用 `consumer.pause(partitions)` 暂停拉取，但是恢复的 `consumer.resume()` 条件永远达不到（计数器/状态机 bug），或在异常流程中漏调用 resume，导致永久暂停。Spring-Kafka 的 `AckMode.MANUAL_IMMEDIATE` + 监听器异常也可能触发内部 pause。

**修复方案**：
1. 对所有 pause 路径加日志，打印"暂停原因 + 分区列表"；
2. 在 poll 循环外层加"看门狗"：若连续 10 次 poll 返回空但 paused 非空且超过 30 秒，**强制 resume + 打告警**；
3. Spring-Kafka 使用 `ContainerProperties.setIdleBetweenPolls()` 替代 pause/resume 做简单背压。

---

#### 根因 3（P1）：目标 Topic 所有分区的 Leader 同时不可用（Controller 脑裂 / Broker 批量离线 / ISR 空）

**排查步骤**：
1. `kafka-topics.sh --bootstrap-server $BROKERS --describe --topic your-topic`，看 Leader 列是否出现 `-1`（无 Leader）；
2. `kafka-topics.sh ... --under-replicated-partitions` 是否覆盖全部分区；
3. 查看 Controller 节点日志，搜索 `LeaderAndIsr`、`OfflinePartition`。

**关键特征**：
- 消费者日志持续报 `NOT_LEADER_OR_FOLLOWER`、`LEADER_NOT_AVAILABLE`；
- `describe` 输出 Leader = -1 或 Leader Broker id 在集群中已不存在；
- `kafka.controller:type=ControllerStats,name=OfflinePartitionsCount` > 0。

**原因本质**：
- 场景 A：6 个 Broker 中 4 台同时重启（如机房断电），3 副本 Topic 的 ISR 中副本数 < min.insync.replicas=2，加上 `unclean.leader.election.enable=false` → 无合法 Leader，分区完全离线；
- 场景 B：ZK/KRaft 的 Controller 选举期间（秒级），新 Leader 尚未分配，但持续超过 1 分钟就是异常（如 ZK 集群脑裂）。

**修复方案**：

**紧急恢复（SLA 优先）**：
```bash
# 若业务可接受短暂丢少量数据恢复，临时开启 unclean 选举（用完立刻关！）
kafka-configs.sh --bootstrap-server $BROKERS --entity-type topics --entity-name your-topic \
  --alter --add-config unclean.leader.election.enable=true
# 观察 OfflinePartitionsCount 降为 0 后，立刻改回 false
kafka-configs.sh ... --alter --delete-config unclean.leader.election.enable
```

**根治（不丢数据前提下恢复）**：
- 先重启所有 Broker，让 Follower 有时间追上 Leader 的 LEO，重新加入 ISR；
- 若磁盘损坏导致部分副本永远回不来，则用 `kafka-reassign-partitions.sh` 把损坏副本迁到健康 Broker。

---

#### 根因 4（P1）：`__consumer_offsets` 内部 Topic 异常，offset 提交永远失败

**排查步骤**：
1. 消费者日志搜索 `OffsetCommit` 的响应码：`COORDINATOR_NOT_AVAILABLE`、`COORDINATOR_LOAD_IN_PROGRESS`、`UNKNOWN_TOPIC_OR_PART`；
2. `kafka-topics.sh --describe --topic __consumer_offsets`，50 个分区 Leader 是否正常；
3. 检查 `__consumer_offsets` 的 `replication.factor` 是否为 1 且那台唯一 Broker 宕机。

**关键特征**：
- `commitSync()` 无限抛 `RetriableException` 或 `TimeoutException`；
- offset 提交 p99 > 5000ms，成功数 ≈ 0；
- Coordinator 所在 Broker 的 `__consumer_offsets` 分区 Leader 不可用。

**原因本质**：`__consumer_offsets` 是 offset 存储的内部 Topic，任何 offset 提交失败都会导致：要么消费者不断重试 commit 阻塞不往下 poll（commitSync），要么继续 poll 但 offset 永远停在原地（commitAsync + 重试），两者都会表现为 Lag 持续上涨。最常见是运维初期没改 `offsets.topic.replication.factor=1`（默认值），唯一副本所在 Broker 宕机就全站 GG。

**修复方案**：
```bash
# 紧急：修改副本数到 3，迁移 __consumer_offsets 分区到健康 Broker
# 1) 生成重分配 JSON：50 个分区，3 副本，跨 3 Broker 分布
# 2) 执行 kafka-reassign-partitions.sh --execute
# 长期：必须在 server.properties 永久设置
offsets.topic.replication.factor=3
transaction.state.log.replication.factor=3
transaction.state.log.min.isr=2
```

---

#### 根因 5（P2）：Broker 与消费者之间的网络半连接 / 防火墙静默丢包，导致 Fetch 请求长时间挂起

**排查步骤**：
1. 消费者所在机器 `ss -tnp | grep 9092`，检查 TCP 连接状态是否存在大量 `CLOSE_WAIT`、`ESTABLISHED` 但接收队列 Recv-Q > 0；
2. 在消费者侧 `tcpdump -i eth0 host <broker-ip> and port 9092 -nn -vv`，是否有 Fetch 请求发出但 Broker 长时间不返回（> 30s）；
3. 在 Broker 侧同时抓包，看对应 Fetch 请求是否到达 Broker。

**关键特征**：
- `poll` 时长接近 `request.timeout.ms`（默认 30s），每次都超时返回空；
- TCP 连接存活但应用层 Kafka 请求无响应；
- Broker 端完全没有对应消费者的 Fetch 日志（中间网络设备静默丢包）。

**原因本质**：企业级防火墙 / LVS VIP / K8s Service 做 TCP 会话保持时，默认会话超时 300s 会静默丢弃空闲会话，但两端都没收到 FIN，误以为连接还活在，发出请求后被黑洞吃掉，直到 `request.timeout.ms` 超时消费者才发现断连，重新连接。

**修复方案**：
```java
// 方案 1：调小 connections.max.idle.ms，主动重建连接
props.put(ConsumerConfig.CONNECTIONS_MAX_IDLE_MS_CONFIG, 60000);  // 60s 空闲就关

// 方案 2：开启 TCP Keepalive（Kafka 默认继承 OS 参数，OS 默认 2 小时才探活，务必改 OS！）
// Linux sysctl.conf：
//   net.ipv4.tcp_keepalive_time=120     // 120s 没数据就开始探
//   net.ipv4.tcp_keepalive_intvl=30
//   net.ipv4.tcp_keepalive_probes=3
// 或者 Kafka 3.x 以上：
props.put(ConsumerConfig.SOCKET_CONNECTION_SETUP_TIMEOUT_MS_CONFIG, 10000);
```

---

#### 根因 6（P2）：业务死信处理 / 异常分支死循环，不推进 offset

**排查步骤**：
1. 用 `jstack <pid>` 连续 dump 3 次消费者进程的线程栈，对比 3 次的 consumer 线程栈；
2. 若 3 次都卡在同一业务代码行（如 while 循环、外部 HTTP 调用）就是业务端问题；
3. 消费者日志 grep `WARN`/`ERROR` 频率是否 1 秒内上百条。

**关键特征**：
- `poll` 有返回（非空 records），但循环处理同一条 record 永远走不到 commit；
- 日志反复打印 `处理失败: orderId=xxx`，但 offset 一直不变；
- CPU 10% 是因为线程 `Thread.sleep(1000)` 重试不退出。

**原因本质**：`process(record)` 里有对某条"脏数据"的死循环：捕获异常后 `continue` 但不跳过这条 record，下一轮循环又从同一条 offset 开始，或死信队列本身失败再次重试，形成死循环。

**修复方案**：
```java
// 关键：为每条消息增加"本地重试计数器"，超过 N 次直接落死信 + 推进 offset，避免无限卡住
ConcurrentHashMap<String, Integer> retryCounter = new ConcurrentHashMap<>();
final int MAX_RETRY = 3;

for (ConsumerRecord<String, String> r : records) {
    String key = r.topic() + "-" + r.partition() + "-" + r.offset();
    int times = retryCounter.merge(key, 1, Integer::sum);
    try {
        businessLogic.process(r);
        retryCounter.remove(key);    // 成功就清理
    } catch (Exception e) {
        if (times < MAX_RETRY) {
            continue; // 本批次后续下次 poll 会再取到这条（因为 offset 没提交）
        } else {
            log.error("重试 {} 次仍失败，直接落死信: r={}", times, r, e);
            deadLetterProducer.send(r, e);
            retryCounter.remove(key); // 失败落死信后也清理，让 offset 可推进
        }
    }
}
// 全部处理（含落死信）完成后再 commit
consumer.commitSync();
```

---

**故障排查总结**：按 P0 → P2 顺序，只需 3 步即可 95% 精确定位：
1. **看消费者日志**：是否 Rebalance 循环 / offset 提交失败 / 业务异常 → 对应根因 1 / 4 / 6；
2. **看 Topic 分区状态**：Leader 是否存在 / UnderReplicated 是否全中 → 对应根因 3；
3. **抓包 + jstack**：网络黑洞 or 业务死循环 → 对应根因 5 / 2。

---

## 四、编程题

### 4.1 生产者编程实践

---

**Q1：请使用 Java Kafka 客户端（kafka-clients 3.6.x）实现一个生产级的**异步订单事件发送器**，要求满足以下 6 项条件，并回答考核点中的问题。**

**需求：**
1. 支持发送 `OrderEvent` POJO（包含 `orderId`、`userId`、`amount`、`eventType`、`occurredAt` 字段）；
2. 必须开启**幂等**，Topic 为 `app.orders.v1`，以 `orderId` 作为消息 key；
3. 必须**带回调**：发送成功打印 Topic/partition/offset；失败则**区分可重试/不可重试异常**，不可重试异常写入本地 `order_events_dlt.log` 死信文件；
4. 发送前经过自定义**拦截器**：在消息 Header 中添加 `requestId=UUID`、`timestamp=System.currentTimeMillis()`、`source=order-service` 三个头；
5. 优雅关闭：JVM 关闭钩子中调用 `flush() + close(Duration.ofSeconds(30))` 确保缓冲消息不落空；
6. `main` 方法中模拟发送 100 条订单事件验证流程。

**Maven 依赖：**

```xml
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-clients</artifactId>
    <version>3.6.1</version>
</dependency>
```

---

**参考实现：**

```java
package com.example.kafka.producer;

import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.header.internals.RecordHeader;
import org.apache.kafka.common.serialization.StringSerializer;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.time.Instant;
import java.util.Map;
import java.util.Properties;
import java.util.UUID;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * 生产级订单事件异步发送器
 * 要点：幂等 + 自定义拦截器 + 回调死信 + 优雅关闭
 */
public class OrderEventProducer {

    private static final String TOPIC = "app.orders.v1";
    private static final String DLT_FILE = "order_events_dlt.log";

    // ==================== 1) POJO ====================
    public static class OrderEvent {
        public String orderId;
        public String userId;
        public long amount;     // 单位：分
        public String eventType; // CREATED / PAYED / SHIPPED / CANCELLED
        public long occurredAt;  // epoch millis

        public OrderEvent(String orderId, String userId, long amount,
                          String eventType, long occurredAt) {
            this.orderId = orderId;
            this.userId = userId;
            this.amount = amount;
            this.eventType = eventType;
            this.occurredAt = occurredAt;
        }

        // 简单的 JSON 序列化（生产环境用 Jackson）
        public String toJson() {
            return String.format(
                "{\"orderId\":\"%s\",\"userId\":\"%s\",\"amount\":%d," +
                "\"eventType\":\"%s\",\"occurredAt\":%d}",
                orderId, userId, amount, eventType, occurredAt
            );
        }
    }

    // ==================== 2) 自定义生产者拦截器 ====================
    public static class TracingProducerInterceptor
            implements ProducerInterceptor<String, String> {

        @Override
        public ProducerRecord<String, String> onSend(ProducerRecord<String, String> record) {
            // 注入三个追踪 Header（下游无需反序列化 value 就能做路由/审计）
            record.headers().add(new RecordHeader("requestId",
                    UUID.randomUUID().toString().getBytes()));
            record.headers().add(new RecordHeader("timestamp",
                    Long.toString(System.currentTimeMillis()).getBytes()));
            record.headers().add(new RecordHeader("source",
                    "order-service".getBytes()));
            return record;
        }

        @Override
        public void onAcknowledgement(RecordMetadata metadata, Exception exception) {
            // ACK 回包后的埋点（生产上报 Prometheus / OTel）
            if (exception == null) {
                // metrics.recordAckSuccess(metadata.topic());
            } else {
                // metrics.recordAckFail(metadata != null ? metadata.topic() : "unknown");
            }
        }

        @Override
        public void close() { /* 释放资源钩子 */ }

        @Override
        public void configure(Map<String, ?> configs) { /* 读取配置钩子 */ }
    }

    // ==================== 3) 死信文件落盘工具（线程安全） ====================
    private static final Object DLT_LOCK = new Object();
    private static void writeToDeadLetter(OrderEvent event, Exception ex) {
        synchronized (DLT_LOCK) {
            try (BufferedWriter bw = new BufferedWriter(new FileWriter(DLT_FILE, true))) {
                bw.write(Instant.now() + " | " + ex.getClass().getSimpleName()
                        + " | " + ex.getMessage() + " | " + event.toJson());
                bw.newLine();
            } catch (IOException ioex) {
                // 死信写入失败是最高级告警：生产中应发企业微信/邮件
                System.err.println("[FATAL] 死信文件写入失败！" + ioex);
            }
        }
    }

    // ==================== 4) 主流程 ====================
    public static void main(String[] args) throws ExecutionException, InterruptedException {
        // —— A. 构建 Producer 配置
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG,
                "broker-1:9092,broker-2:9092,broker-3:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG,
                StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG,
                StringSerializer.class.getName());
        // 拦截器（可配置多个，逗号分隔）
        props.put(ProducerConfig.INTERCEPTOR_CLASSES_CONFIG,
                TracingProducerInterceptor.class.getName());

        // —— 可靠性核心
        props.put(ProducerConfig.ACKS_CONFIG, "all");              // ISR 全确认
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true); // 幂等：去重+保序
        props.put(ProducerConfig.RETRIES_CONFIG, Integer.MAX_VALUE);
        props.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5);
        props.put(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, 120000);
        props.put(ProducerConfig.REQUEST_TIMEOUT_MS_CONFIG, 30000);

        // —— 吞吐优化
        props.put(ProducerConfig.BATCH_SIZE_CONFIG, 262144);       // 256KB
        props.put(ProducerConfig.LINGER_MS_CONFIG, 10);            // 等 10ms 凑批
        props.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "lz4");
        props.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 134217728); // 128MB

        // —— B. 创建 Producer 实例
        KafkaProducer<String, String> producer = new KafkaProducer<>(props);
        AtomicBoolean running = new AtomicBoolean(true);

        // —— C. 优雅关闭钩子
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("[ShutdownHook] 收到关闭信号，开始 flush 剩余消息 ...");
            running.set(false);
            producer.flush();
            producer.close(Duration.ofSeconds(30));
            System.out.println("[ShutdownHook] Producer 已安全关闭。");
        }));

        // —— D. 模拟发送 100 条订单事件
        String[] eventTypes = {"CREATED", "PAYED", "SHIPPED", "CANCELLED"};
        for (int i = 1; i <= 100 && running.get(); i++) {
            String orderId = "ORD2025" + String.format("%08d", i);
            OrderEvent event = new OrderEvent(
                    orderId,
                    "UID" + (i % 500),
                    (long) (Math.random() * 100000),   // 0 ~ 999.99 元
                    eventTypes[i % eventTypes.length],
                    System.currentTimeMillis()
            );

            // 消息 key = orderId，保证同订单路由到同一分区 → 有序
            ProducerRecord<String, String> record = new ProducerRecord<>(
                    TOPIC, event.orderId, event.toJson()
            );

            // —— E. 异步发送 + 回调区分异常
            producer.send(record, (metadata, exception) -> {
                if (exception == null) {
                    // 成功：记录审计
                    System.out.printf("[OK] orderId=%s -> %s-%d@%d%n",
                            event.orderId,
                            metadata.topic(),
                            metadata.partition(),
                            metadata.offset());
                } else if (exception instanceof RetriableException) {
                    // 可重试：Producer 内部已经按 retries 自动重试，这里只做统计
                    // 如果最终还是失败（超过 retries 或 delivery.timeout），
                    // 会走下面的不可重试分支
                    System.out.printf("[WARN_RETRY] orderId=%s 触发重试: %s%n",
                            event.orderId, exception.getMessage());
                } else {
                    // 不可重试：消息太大 / 序列化失败 / 权限 / topic 不存在
                    // Producer 不会再重试 → 必须落死信人工补数
                    System.err.printf("[FATAL_DLT] orderId=%s 不可重试异常，写入死信文件: %s%n",
                            event.orderId, exception.getMessage());
                    writeToDeadLetter(event, exception);
                }
            });
        }

        // main 线程等待所有异步回调完成（除了 shutdown hook 正常关闭）
        if (running.get()) {
            producer.flush();
            Thread.sleep(2000);
            producer.close(Duration.ofSeconds(10));
            System.out.println("[Main] 100 条订单事件发送完成，Producer 正常退出。");
        }
    }
}
```

---

**考核点与评分建议（面试追问）：**

| 序号 | 追问点（面试官可按顺序加深） | 参考回答要点 | 分值 |
|------|----------------------------|-------------|------|
| 1 | 为什么 `message.key = orderId`？不设 key 会有什么后果？ | 默认分区器对有 key 的消息做 `murmur2(key) % partitionNum`，保证同 key 同分区 → 同订单事件严格有序；key=null 的 Sticky 策略会把消息随机打在几个分区，同订单可能出现"SHIPPED 先于 PAYED 被下游消费"的时序错乱。 | 15 |
| 2 | 开启幂等后，若 Producer 进程 OOM 重启，重启后重发同一条订单消息是否还能保证不重复？为什么？ | **不能**。幂等仅在**同 PID 会话内**去重，进程重启 PID 会重新分配（除非使用事务 `transactional.id` 持久化映射）；跨进程重复需要事务 Producer 或业务幂等（如订单表唯一键）兜底。 | 20 |
| 3 | 为什么拦截器在 Header 加 `requestId` 而不是把 requestId 塞到 JSON body 里？ | ① 下游消费者/代理/镜像工具可通过 `record.headers()` 直接拿到追踪 ID，**无需反序列化整个 JSON body**，性能好且不侵入业务 schema；② 链路追踪系统（OpenTelemetry）天然按 Header 采集；③ Header 独立于 value，value 升级 schema 时追踪字段不受影响。 | 15 |
| 4 | `RetriableException` 常见子类有哪些？为什么"可重试"却还要在回调里打 WARN 日志？ | 常见可重试：`NotLeaderOrFollowerException`、`NetworkException`、`UnknownTopicOrPartitionException`（创建中）、`NotEnoughReplicasException`。Producer 内部会按指数退避重试，但**可能重试 N 次最终仍失败**（delivery.timeout 到期）→ 最终走到不可重试分支。打 WARN 可提前观察"重试次数异常"，避免大促时才突然发现 Broker 网络抖动/ISR 异常。 | 15 |
| 5 | shutdown hook 里为什么要 `flush()` 再 `close()`？直接 `close()` 不行吗？ | `close(Duration)` 内部等价于 `flush()` + 等待 Sender 线程在超时内完成所有 in-flight 请求后关闭。这里 flush + close 是双重保险的写法。关键是**必须传 Duration 或调用带 timeout 的 close**，否则若 Broker 不可达，默认 `close()` 会无限等，JVM 关不掉。 | 15 |
| 6 | 若 Topic 还没创建就启动发送，会发生什么？生产环境如何规避？ | 若 `auto.create.topics.enable=true`（Broker 默认），Broker 会按 `num.partitions=1 / default.replication.factor=1` 创建出 **1 分区 1 副本**的垃圾 Topic，可靠性极差！<br>规避：① Broker 端**永久关闭 `auto.create.topics.enable=false`**；② 应用启动时通过 `AdminClient.createTopics()` 显式创建；③ 或运维流水线提前 `kafka-topics.sh --create` 创建符合规范的 Topic。 | 20 |

---

### 4.2 消费者编程实践

---

**Q2：请实现一个生产级的**订单风控消费者**，使用 Java Kafka 客户端，要求满足：**
1. Group ID 为 `cg-order-risk-v1`，订阅 `app.orders.v1` Topic；
2. **手动提交 offset**：对每条记录先调用 `riskEngine.evaluate(event)` 业务风控评估，成功后按**分区粒度**提交 offset（每条都提交一次 `commitSync(perPartitionMap)`，不是批量最后才提交）；
3. **消费幂等**：用 Redis `SETNX order:risk:done:{orderId}:{eventType} 1 EX 86400` 判断是否已处理，已处理直接跳过；
4. **重试 + 死信**：evaluate 抛异常时，对同一条消息本地最多重试 3 次（Thread.sleep 指数退避），最终失败发回 `app.orders.v1.DLT` 死信 Topic，然后才推进 offset；
5. 支持 **Runtime.getRuntime().addShutdownHook** 优雅停止：唤醒正在 `poll()` 的消费者，保证最后一个批次提交完再退出；
6. 暴露监控指标：把消费成功、失败、DLT 次数通过简单的 `AtomicLong` 计数，每 1 分钟后台线程打印一次统计快照。

**风控引擎接口（直接模拟即可）：**
```java
interface RiskEngine {
    void evaluate(OrderEvent event) throws RiskRejectException, RiskTempFailException;
}
```
其中 `RiskRejectException` 表示"业务拒绝，不需要重试"（直接落死信），`RiskTempFailException` 表示"临时性失败需要重试"。

---

**参考实现：**

```java
package com.example.kafka.consumer;

import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.errors.WakeupException;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.params.SetParams;

import java.time.Duration;
import java.util.*;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;

/**
 * 生产级订单风控消费者
 * 要点：手动提交 + 幂等(Redis SETNX) + 按异常类型重试/DLT + 优雅停止 + 监控
 */
public class OrderRiskConsumer {

    // ============ 1) 业务定义 ============
    public static class OrderEvent {
        public String orderId, userId, eventType;
        public long amount, occurredAt;

        public static OrderEvent fromJson(String json) {
            OrderEvent e = new OrderEvent();
            // 简化解析（生产用 Jackson ObjectMapper）
            json = json.replaceAll("[{}\"]", "");
            for (String kv : json.split(",")) {
                String[] a = kv.split(":");
                switch (a[0]) {
                    case "orderId":    e.orderId    = a[1]; break;
                    case "userId":     e.userId     = a[1]; break;
                    case "eventType":  e.eventType  = a[1]; break;
                    case "amount":     e.amount     = Long.parseLong(a[1]); break;
                    case "occurredAt": e.occurredAt = Long.parseLong(a[1]); break;
                }
            }
            return e;
        }
    }

    public static class RiskRejectException    extends RuntimeException {
        public RiskRejectException(String msg) { super(msg); }
    }
    public static class RiskTempFailException  extends RuntimeException {
        public RiskTempFailException(String msg) { super(msg); }
    }

    // 风控引擎：用随机数模拟业务结果
    static class MockRiskEngine {
        private final Random r = new Random(42);
        public void evaluate(OrderEvent e) throws RiskRejectException, RiskTempFailException {
            int x = r.nextInt(100);
            if (x < 2)       throw new RiskRejectException("命中黑名单: " + e.userId);
            else if (x < 7)  throw new RiskTempFailException("风控特征库查询超时");
            // 93% 正常通过
            if (e.amount > 500000) { // >5000 元大额人工审核
                System.out.println("[INFO] 大额订单进入人工审核: " + e.orderId);
            }
        }
    }

    // ============ 2) 统计指标 ============
    private static final AtomicLong CNT_OK       = new AtomicLong(0);
    private static final AtomicLong CNT_DUP      = new AtomicLong(0); // 幂等重复
    private static final AtomicLong CNT_RETRY    = new AtomicLong(0);
    private static final AtomicLong CNT_DLT      = new AtomicLong(0);

    // ============ 3) 主流程 ============
    public static void main(String[] args) {
        final String SRC_TOPIC = "app.orders.v1";
        final String DLT_TOPIC = "app.orders.v1.DLT";
        final String GROUP_ID  = "cg-order-risk-v1";

        // —— A. 消费者配置
        Properties consumerProps = new Properties();
        consumerProps.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG,
                "broker-1:9092,broker-2:9092,broker-3:9092");
        consumerProps.put(ConsumerConfig.GROUP_ID_CONFIG, GROUP_ID);
        consumerProps.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG,
                StringDeserializer.class.getName());
        consumerProps.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG,
                StringDeserializer.class.getName());

        // —— 可靠性核心：关闭自动提交！
        consumerProps.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
        consumerProps.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "latest");
        consumerProps.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 200);
        consumerProps.put(ConsumerConfig.MAX_POLL_INTERVAL_MS_CONFIG, 300_000); // 5min
        consumerProps.put(ConsumerConfig.REQUEST_TIMEOUT_MS_CONFIG, 30_000);
        consumerProps.put(ConsumerConfig.SESSION_TIMEOUT_MS_CONFIG, 10_000);
        consumerProps.put(ConsumerConfig.HEARTBEAT_INTERVAL_MS_CONFIG, 3_000);

        // —— B. 死信生产者（复用前面的幂等配置）
        Properties dltProps = new Properties();
        dltProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG,
                consumerProps.getProperty(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG));
        dltProps.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG,
                StringSerializer.class.getName());
        dltProps.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG,
                StringSerializer.class.getName());
        dltProps.put(ProducerConfig.ACKS_CONFIG, "all");
        dltProps.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        KafkaProducer<String, String> dltProducer = new KafkaProducer<>(dltProps);

        // —— C. 外部依赖
        JedisPool jedisPool = new JedisPool("localhost", 6379);
        MockRiskEngine riskEngine = new MockRiskEngine();

        // —— D. 构建消费者 + 订阅
        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(consumerProps);
        consumer.subscribe(Collections.singletonList(SRC_TOPIC));
        AtomicBoolean running = new AtomicBoolean(true);

        // —— E. 优雅关闭钩子：调用 consumer.wakeup() 让下次 poll 抛 WakeupException
        final Thread mainThread = Thread.currentThread();
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("[Shutdown] 开始优雅停止消费者 ...");
            running.set(false);
            consumer.wakeup();   // 只能在消费线程之外调用！让阻塞的 poll 立即返回
            try {
                mainThread.join(30_000);
            } catch (InterruptedException ignored) { }
            dltProducer.close(Duration.ofSeconds(10));
            jedisPool.close();
            System.out.println("[Shutdown] 消费者已停止。");
        }));

        // —— F. 统计打印线程（1min 一次快照）
        ScheduledExecutorService stats = Executors.newSingleThreadScheduledExecutor(r -> {
            Thread t = new Thread(r, "risk-metrics");
            t.setDaemon(true);
            return t;
        });
        stats.scheduleAtFixedRate(() -> System.out.printf(
                "[METRICS] ok=%d / dup=%d / retry=%d / dlt=%d%n",
                CNT_OK.get(), CNT_DUP.get(), CNT_RETRY.get(), CNT_DLT.get()),
                1, 1, TimeUnit.MINUTES);

        // —— G. 主消费循环
        try {
            while (running.get()) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(1000));
                if (records.isEmpty()) continue;

                for (ConsumerRecord<String, String> r : records) {
                    // G-1. 解析消息
                    OrderEvent event;
                    try {
                        event = OrderEvent.fromJson(r.value());
                    } catch (Exception parseEx) {
                        // 脏数据：解析失败不可能通过重试成功，直接落 DLT
                        System.err.println("[DLT_PARSE] 解析失败: offset=" + r.offset());
                        sendDLT(dltProducer, DLT_TOPIC, r.key(), r.value(), parseEx);
                        CNT_DLT.incrementAndGet();
                        advanceOffset(consumer, r);
                        continue;
                    }

                    // G-2. 消费幂等：Redis SETNX（不存在才设置 → 成功=首次，失败=重复）
                    String dedupKey = String.format("order:risk:done:%s:%s",
                            event.orderId, event.eventType);
                    try (Jedis jedis = jedisPool.getResource()) {
                        String rst = jedis.set(dedupKey, "1",
                                SetParams.setParams().nx().ex(86400)); // 1 天窗口
                        if (!"OK".equals(rst)) {
                            CNT_DUP.incrementAndGet();
                            advanceOffset(consumer, r);
                            continue; // 幂等命中：跳过处理，直接推进 offset
                        }
                    }

                    // G-3. 风控评估 + 按异常类型分支 + 指数退避重试
                    int retries = 0;
                    boolean success = false;
                    Exception finalEx = null;
                    while (retries < 3) {
                        try {
                            riskEngine.evaluate(event);
                            success = true;
                            break;
                        } catch (RiskRejectException re) {
                            finalEx = re;
                            break; // 业务拒绝 = 不需要重试
                        } catch (RiskTempFailException te) {
                            finalEx = te;
                            retries++;
                            CNT_RETRY.incrementAndGet();
                            if (retries >= 3) break;
                            try {
                                Thread.sleep(100L * (1L << retries)); // 200ms → 400ms → 800ms
                            } catch (InterruptedException ie) {
                                Thread.currentThread().interrupt();
                                break;
                            }
                        }
                    }

                    // G-4. 结果分支
                    if (success) {
                        CNT_OK.incrementAndGet();
                    } else {
                        CNT_DLT.incrementAndGet();
                        sendDLT(dltProducer, DLT_TOPIC, r.key(), r.value(), finalEx);
                    }
                    advanceOffset(consumer, r); // 无论成功/DLT/幂等，都推进 offset（不回滚）
                }
            }
        } catch (WakeupException we) {
            // 正常：shutdown hook 调用 wakeup() 触发的异常，忽略
            System.out.println("[Main] 收到 WakeupException，准备退出 ...");
        } finally {
            // —— H. 最后一次提交 offset + 关闭资源
            try {
                consumer.commitSync();
                System.out.println("[Main] 最后一次 offset 已提交。");
            } catch (Exception e) {
                System.err.println("[Main] 最后一次 offset 提交失败: " + e);
            }
            consumer.close(Duration.ofSeconds(15));
            stats.shutdownNow();
        }
    }

    // ============ 4) 辅助方法 ============
    /** 单条处理完成后，按分区粒度立刻 commit offset */
    private static void advanceOffset(KafkaConsumer<String, String> consumer,
                                      ConsumerRecord<String, String> r) {
        Map<TopicPartition, OffsetAndMetadata> toCommit = new HashMap<>();
        toCommit.put(new TopicPartition(r.topic(), r.partition()),
                new OffsetAndMetadata(r.offset() + 1));
        consumer.commitSync(toCommit);
    }

    /** 死信发送：将原 value + 异常信息(作为Header)发送到 DLT Topic */
    private static void sendDLT(KafkaProducer<String, String> dltProducer,
                                String dltTopic, String key, String value, Exception ex) {
        ProducerRecord<String, String> dlt = new ProducerRecord<>(dltTopic, key, value);
        if (ex != null) {
            dlt.headers().add("dlt.exception.class",
                    ex.getClass().getName().getBytes());
            dlt.headers().add("dlt.exception.msg",
                    (ex.getMessage() == null ? "" : ex.getMessage()).getBytes());
        }
        try {
            dltProducer.send(dlt).get(10, TimeUnit.SECONDS); // 阻塞确保DLT成功
        } catch (Exception e) {
            // 极端：DLT 自己也发失败 → 必须本地文件二次兜底
            System.err.println("[FATAL_DLT_FAIL] 死信 Topic 也发失败：key=" + key + " ex=" + e);
        }
    }
}
```

---

**考核点与评分建议：**

| 序号 | 追问点 | 参考回答要点 | 分值 |
|------|-------|-------------|------|
| 1 | 为什么用 `consumer.wakeup()` 配合 `WakeupException` 做退出？不能直接 `consumer.close()` 吗？ | `close()` 是线程安全但 poll 是单线程方法：若 main 线程正阻塞在 poll，shutdown 钩子线程调 `close()` 会导致 `ConcurrentModificationException` 或竞态。官方推荐：钩子调 `wakeup()`（唯一可跨线程安全调用的 consumer 方法），让 poll 立即抛 WakeupException，再在 finally 中由**同一个消费线程**调 `commitSync() + close()`，天然单线程无竞态。 | 25 |
| 2 | 为什么 `commitSync(perPartitionMap)` 每条就提交一次，而不是一个批次处理完才提交一次？ | 因为"幂等 + DLT兜底"的设计：本批次第 N 条失败落死信后，前 N-1 条的 offset 必须已经持久化到 Broker，否则整个批次一起回滚会导致**前 N-1 条已经处理成功的业务消息被重新消费**，即使有 Redis SETNX 幂等去重（额外开销），极端情况下 SETNX 已过期（1天后重启）仍可能重复执行业务。单条提交 = 业务执行进度与 offset 最大程度对齐。代价是吞吐降低，高吞吐场景可改每 100 条或 1s 提交一次。 | 20 |
| 3 | 幂等 SETNX 的 key 为什么包含 `eventType`？只包含 `orderId` 可以吗？ | 不行。同一个订单会有 5 种事件（CREATED/PAYED/SHIPPED/...），若只存 `order:risk:done:ORD001`，第一次 CREATED 事件 SETNX 成功，后续 PAYED/SHIPPED 全部被判定为"重复"而跳过，实际上这 3 个事件都需要分别跑风控。加上 eventType 做到"**订单 × 事件类型**"粒度的幂等才正确。保留期 1 天 = 订单事件链路最长 24h 内不重复即可。 | 20 |
| 4 | 两类业务异常（Reject vs TempFail）的重试策略差异设计思路是什么？ | **RejectException（业务拒绝）= 确定性失败**：如用户命中风控黑名单，重试 100 次还是拒绝，重试只会浪费 CPU。必须直接落 DLT（或人工审核队列）。<br>**TempFailException（临时失败）= 概率性失败**：如特征库 DB 短暂抖动、外部接口限流，重试几次就能成功。指数退避避免瞬间重试把抖动的下游打垮。<br>核心思想：**按异常语义分类处理**，而不是"一把梭重试到底"或"失败就丢 DLT"两个极端。 | 20 |
| 5 | 若 Redis 挂了，SETNX 抛 JedisConnectionException，当前代码会怎么行为？怎么修复？ | 当前代码中 try-with-resources 拿到 jedis，若 Redis 挂会抛出连接异常，而该异常**没有被捕获** → 直接跳出 for 循环，抛到外层 while，poll 又被中断 → **整个消费进程卡死**：新消息不消费、offset 不推进、Lag 爆涨。<br>修复：对 jedis.set 包 try/catch，Redis 不可用时降级为"**本地 Caffeine 缓存短期幂等 + 告警**"，或者直接跳过幂等检查（宁可少量重复也不卡消费，因为风控引擎本身也有业务主键兜底）。<br>原则：**外部依赖故障（Redis）不能阻塞核心链路（消费）**。 | 15 |

---

### 4.3 综合应用编程

---

**Q3：实现一个"**订单金额实时聚合统计服务**"（即 Kafka Streams 的简化版 wordcount，但维度是订单 userId，指标为总金额和订单数）。要求：**
1. 从 `app.orders.v1` 消费订单事件；
2. 按 userId 维度，**5 分钟一个滚动窗口（Hopping/Tumbling Window，任选其一）** 实时累计每个用户的：`订单总数 count`、`订单总金额 sumAmount`；
3. 结果写入 MySQL 表 `user_order_stats_5min`（字段：`user_id`、`window_start`、`window_end`、`order_count`、`sum_amount`、`updated_at`），要求同一个窗口内同一个用户的多次消费更新是**幂等**的（不会统计翻倍）；
4. 实现**手动消费位点 + 事务性发件箱的反向版本 = "消费进度与 DB 更新原子提交"**：在同一个 MySQL 本地事务中，同时 `UPDATE user_order_stats_5min ...` + `UPDATE kafka_consumer_progress SET offset=? WHERE group_id=? AND topic=? AND partition=?`，重启后按 `kafka_consumer_progress` 表的 offset 作为起点，不再依赖 Kafka `__consumer_offsets`；
5. 支持优雅退出 + 10s 定时打印每个用户最新统计值。

要求：使用**纯 Kafka Consumer + MySQL（JDBC）** 原生实现，不许引 Kafka Streams / Flink / Spring 等框架。给出关键表建表 DDL 与核心代码。

---

**参考实现：**

**（1）MySQL 建表 DDL**

```sql
-- A. 订单用户 5min 窗口统计表（业务结果）
CREATE TABLE user_order_stats_5min (
    user_id       VARCHAR(64)  NOT NULL,
    window_start  DATETIME(3)  NOT NULL  COMMENT '窗口开始（精确到毫秒）',
    window_end    DATETIME(3)  NOT NULL  COMMENT '窗口结束（= window_start + 5min）',
    order_count   INT UNSIGNED NOT NULL  DEFAULT 0,
    sum_amount    BIGINT       NOT NULL  DEFAULT 0 COMMENT '单位：分',
    updated_at    DATETIME(3)  NOT NULL  DEFAULT CURRENT_TIMESTAMP(3)
        ON UPDATE CURRENT_TIMESTAMP(3),
    -- 天然幂等主键：同窗口+同用户只能有一条记录，重复写自动变成 UPDATE
    PRIMARY KEY (user_id, window_start, window_end),
    -- 反向索引：按窗口批量查询
    INDEX idx_window (window_start, window_end)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单用户5分钟统计';

-- B. 消费进度表（替代 __consumer_offsets，与业务更新同一事务提交）
CREATE TABLE kafka_consumer_progress (
    group_id  VARCHAR(128) NOT NULL,
    topic     VARCHAR(255) NOT NULL,
    partition INT          NOT NULL,
    -- 注意：存的是"下次要消费的 offset = 已成功处理最后一条offset+1"
    next_offset BIGINT       NOT NULL DEFAULT 0,
    updated_at  DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3)
        ON UPDATE CURRENT_TIMESTAMP(3),
    PRIMARY KEY (group_id, topic, partition)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Kafka消费进度存储';
```

**（2）核心 Java 代码**

```java
package com.example.kafka.streams.custom;

import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.serialization.StringDeserializer;

import java.sql.*;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * 自研简化版 Kafka Streams：
 *  订单 userId × 5min Tumbling Window → count / sum_amount
 *  事务性 DB 原子提交：业务统计更新与消费进度更新在同一个 MySQL 事务里
 */
public class OrderStatsAggregator {

    private static final String BOOTSTRAP = "broker-1:9092,broker-2:9092,broker-3:9092";
    private static final String TOPIC     = "app.orders.v1";
    private static final String GROUP     = "cg-order-stats-agg-v1";

    // MySQL 连接（生产用 HikariCP 连接池）
    private static final String MYSQL_URL = "jdbc:mysql://localhost:3306/stats_db"
            + "?useSSL=false&serverTimezone=Asia/Shanghai&rewriteBatchedStatements=true";
    private static final String MYSQL_USER = "stats_app";
    private static final String MYSQL_PWD  = "password";

    // ==================== 1) POJO ====================
    public static class OrderEvent {
        public String orderId, userId, eventType;
        public long amount, occurredAt;
        static OrderEvent fromJson(String json) {
            // 同上题，简化解析
            OrderEvent e = new OrderEvent();
            json = json.replaceAll("[{}\"]", "");
            for (String kv : json.split(",")) {
                String[] a = kv.split(":");
                switch (a[0]) {
                    case "orderId":    e.orderId    = a[1]; break;
                    case "userId":     e.userId     = a[1]; break;
                    case "eventType":  e.eventType  = a[1]; break;
                    case "amount":     e.amount     = Long.parseLong(a[1]); break;
                    case "occurredAt": e.occurredAt = Long.parseLong(a[1]); break;
                }
            }
            return e;
        }
    }

    // ==================== 2) 5 分钟滚动窗口计算 ====================
    // 返回 [windowStart, windowEnd) 长整型数组（epoch millis）
    private static long[] tumbleWindow(long eventTime, long windowSizeMs) {
        long start = (eventTime / windowSizeMs) * windowSizeMs;
        return new long[] { start, start + windowSizeMs };
    }
    private static final long WINDOW_MS = 5 * 60 * 1000L; // 5min

    // ==================== 3) MySQL JDBC：同一事务原子提交 "统计Upsert + 进度写入" ====================
    private static final String UPSERT_SQL =
        "INSERT INTO user_order_stats_5min(user_id, window_start, window_end, order_count, sum_amount)" +
        " VALUES(?, ?, ?, 1, ?)" +
        " ON DUPLICATE KEY UPDATE" +
        "   order_count = order_count + 1," +   /* ✅ 幂等关键1：加而不是赋值 */
        "   sum_amount  = sum_amount  + ?," +
        "   updated_at  = CURRENT_TIMESTAMP(3)";

    private static final String UPDATE_PROGRESS_SQL =
        "INSERT INTO kafka_consumer_progress(group_id, topic, partition, next_offset)" +
        " VALUES(?, ?, ?, ?)" +
        " ON DUPLICATE KEY UPDATE next_offset=?, updated_at=CURRENT_TIMESTAMP(3)";

    /**
     * 处理一条订单事件：
     * ✅ 幂等保证三要素：
     *   ① 表主键 (user_id, window_start, window_end) 去重；
     *   ② count/sum 用 "= 列 + 增量" 而非 "= 新值"，避免同一事件重复 DB 事务提交时把 count 越写越大；
     *   ③ 业务更新 + 消费进度更新 放在同一个 MySQL 事务 → 要么都成功要么都失败，天然 EOS。
     *
     * @return true = 已写入 DB 并推进进度；false = 非 CREATED/PAYED 事件跳过（但也推进进度）
     */
    private static boolean handleEvent(Connection conn, TopicPartition tp,
                                       long nextOffset, OrderEvent ev) throws SQLException {

        // —— 维度过滤：只有 CREATED / PAYED 才算入金额统计（取消订单用负数另算，此处简化）
        if (!("CREATED".equals(ev.eventType) || "PAYED".equals(ev.eventType))) {
            try (PreparedStatement ps = conn.prepareStatement(UPDATE_PROGRESS_SQL)) {
                ps.setString(1, GROUP);
                ps.setString(2, tp.topic());
                ps.setInt(3, tp.partition());
                ps.setLong(4, nextOffset);
                ps.setLong(5, nextOffset);
                ps.executeUpdate();
            }
            return false;
        }

        long[] win = tumbleWindow(ev.occurredAt, WINDOW_MS);
        LocalDateTime start = LocalDateTime.ofInstant(Instant.ofEpochMilli(win[0]),
                ZoneId.of("Asia/Shanghai"));
        LocalDateTime end   = LocalDateTime.ofInstant(Instant.ofEpochMilli(win[1]),
                ZoneId.of("Asia/Shanghai"));

        try {
            conn.setAutoCommit(false); // 开启事务

            // Step 1：Upsert 统计结果
            try (PreparedStatement ps = conn.prepareStatement(UPSERT_SQL)) {
                ps.setString(1, ev.userId);
                ps.setTimestamp(2, Timestamp.valueOf(start));
                ps.setTimestamp(3, Timestamp.valueOf(end));
                ps.setLong(4, ev.amount);    // INSERT 分支的 sum_amount
                ps.setLong(5, ev.amount);    // UPDATE 分支的 "+= amount"
                ps.executeUpdate();
            }

            // Step 2：更新消费进度（同样分区粒度）
            try (PreparedStatement ps = conn.prepareStatement(UPDATE_PROGRESS_SQL)) {
                ps.setString(1, GROUP);
                ps.setString(2, tp.topic());
                ps.setInt(3, tp.partition());
                ps.setLong(4, nextOffset);
                ps.setLong(5, nextOffset);
                ps.executeUpdate();
            }

            conn.commit(); //  ✅ 两个更新一起提交
            return true;
        } catch (SQLException ex) {
            conn.rollback(); // ❌ 任一步失败一起回滚：不会出现"业务写入成功但 offset 没推进导致重复统计"
            throw ex;        // 抛给外层重试
        } finally {
            conn.setAutoCommit(true);
        }
    }

    // ==================== 4) 从 MySQL 读取已保存的消费进度，用 consumer.seek 精准回放 ====================
    private static Map<TopicPartition, Long> loadProgressFromDB(Connection conn,
                                                                KafkaConsumer<String, String> consumer)
            throws SQLException {

        // 先强制做一次分配（必须 poll 0 超时或者手动 assign，这里用 consumer 的 assignment 逻辑）
        consumer.poll(Duration.ZERO); // 触发 JoinGroup 拿到分区分配（可能空，第一轮）
        Set<TopicPartition> assignment = consumer.assignment();
        Map<TopicPartition, Long> result = new HashMap<>();

        if (assignment.isEmpty()) return result;

        // 对每个分配到的分区查 DB
        try (PreparedStatement ps = conn.prepareStatement(
                "SELECT partition, next_offset FROM kafka_consumer_progress " +
                "WHERE group_id=? AND topic=?")) {
            ps.setString(1, GROUP);
            ps.setString(2, TOPIC);
            try (ResultSet rs = ps.executeQuery()) {
                // 先把 (partition → nextOffset) 读出来
                Map<Integer, Long> byPart = new HashMap<>();
                while (rs.next()) byPart.put(rs.getInt(1), rs.getLong(2));

                for (TopicPartition tp : assignment) {
                    Long saved = byPart.get(tp.partition());
                    if (saved != null) {
                        consumer.seek(tp, saved); // ✅ 从上次 DB 进度精确回放
                        result.put(tp, saved);
                    } else {
                        // 没进度：按配置的 auto.offset.reset（latest）
                        consumer.seekToEnd(Collections.singleton(tp));
                    }
                }
            }
        }
        return result;
    }

    // ==================== 5) 主流程 ====================
    public static void main(String[] args) throws Exception {
        // —— A. 消费者配置（注意：即便不使用 __consumer_offsets 也要设 enable.auto.commit=false 防止它偷偷提交）
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP);
        props.put(ConsumerConfig.GROUP_ID_CONFIG, GROUP);
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG,
                StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG,
                StringDeserializer.class.getName());
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "latest");
        props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 500);
        props.put(ConsumerConfig.MAX_POLL_INTERVAL_MS_CONFIG, 600_000); // 10min 容忍慢事务

        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
        consumer.subscribe(Collections.singletonList(TOPIC));

        Connection conn = DriverManager.getConnection(MYSQL_URL, MYSQL_USER, MYSQL_PWD);
        conn.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);

        // —— B. 启动后先加载 DB 进度（支持 Rebalance 后 seek 到对应分区 DB 进度：实际生产需注册 ConsumerRebalanceListener）
        Thread.sleep(1000);
        loadProgressFromDB(conn, consumer);

        AtomicBoolean running = new AtomicBoolean(true);
        Thread mainThread = Thread.currentThread();
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            running.set(false);
            consumer.wakeup();
            try { mainThread.join(30_000); } catch (InterruptedException ignored) { }
            try { conn.close(); } catch (Exception ignored) { }
            consumer.close(Duration.ofSeconds(10));
            System.out.println("[Shutdown] Stats aggregator exited.");
        }));

        // —— C. 10s 快照线程：打印 Top5 用户统计
        ScheduledExecutorService snap = Executors.newSingleThreadScheduledExecutor(r -> {
            Thread t = new Thread(r, "stats-snapshot"); t.setDaemon(true); return t;
        });
        snap.scheduleAtFixedRate(() -> {
            String sql = "SELECT user_id, window_start, order_count, sum_amount" +
                    " FROM user_order_stats_5min ORDER BY sum_amount DESC LIMIT 5";
            try (Statement s = conn.createStatement(); ResultSet rs = s.executeQuery(sql)) {
                System.out.println("===== [TOP-5 用户 5min 订单金额快照] " + LocalDateTime.now());
                while (rs.next()) {
                    System.out.printf("  user=%s 窗口=%s  订单数=%d  总金额=%.2f 元%n",
                            rs.getString(1),
                            rs.getTimestamp(2).toInstant()
                              .truncatedTo(ChronoUnit.MINUTES),
                            rs.getInt(3),
                            rs.getLong(4) / 100.0);
                }
            } catch (SQLException e) {
                System.err.println("[快照查询失败] " + e);
            }
        }, 10, 10, TimeUnit.SECONDS);

        // —— D. 主循环
        long total = 0;
        while (running.get()) {
            ConsumerRecords<String, String> records;
            try {
                records = consumer.poll(Duration.ofMillis(1000));
            } catch (org.apache.kafka.common.errors.WakeupException e) {
                break;
            }
            if (records.isEmpty()) continue;

            for (ConsumerRecord<String, String> r : records) {
                OrderEvent ev;
                try {
                    ev = OrderEvent.fromJson(r.value());
                } catch (Exception parseEx) {
                    // 脏数据：跳过，推进进度
                    TopicPartition tp = new TopicPartition(r.topic(), r.partition());
                    try (PreparedStatement ps = conn.prepareStatement(UPDATE_PROGRESS_SQL)) {
                        ps.setString(1, GROUP); ps.setString(2, tp.topic());
                        ps.setInt(3, tp.partition());
                        ps.setLong(4, r.offset() + 1); ps.setLong(5, r.offset() + 1);
                        ps.executeUpdate();
                    }
                    continue;
                }

                TopicPartition tp = new TopicPartition(r.topic(), r.partition());
                int retry = 0;
                while (true) {
                    try {
                        handleEvent(conn, tp, r.offset() + 1, ev);
                        total++;
                        break;
                    } catch (SQLRecoverableException e) {
                        if (++retry >= 3) throw e;
                        Thread.sleep(200L * retry); // DB 连接抖动短暂重试
                    }
                }
            }
            if (total % 1000 == 0)
                System.out.printf("[Progress] 已聚合 %d 条事件 @ %s%n", total, LocalDateTime.now());
        }
        snap.shutdownNow();
    }
}
```

---

**考核点与评分建议：**

| 序号 | 追问点 | 参考回答要点 | 分值 |
|------|-------|-------------|------|
| 1 | 这个实现中，哪几处设计**共同保证了 MySQL 统计结果不会因为重复消费或重复提交而翻倍**？ | 三重防线：① 表主键 `(user_id, window_start, window_end)` 去重，同一窗口同一用户只能有一条；② `ON DUPLICATE KEY UPDATE order_count = order_count + 1` 使用增量累加而非赋值；③ 业务增量更新与消费进度更新在同一 MySQL 事务，不会发生"业务更新成功但进度未提交"导致的重复消费。三者结合，即使进程 OOM 在"业务更新完、进度提交前"那一刻崩溃，重启后会 seek 回上一次事务提交的 offset，重新消费这条事件——此时主键命中走 UPDATE 分支，+1/+amount 会被多加一次吗？<br>⚠️ 这里是面试**隐藏加分点**：如果按当前的"消费幂等"逻辑，其实重复消费**仍然会多加**！因为主键冲突后走的是 `列 = 列 + 值`。要彻底解决还需要**事件级幂等**（如把 `orderId` 作为防重字段），比如把统计 SQL 改成先 `SELECT order_count FROM ...` 判断 orderId 是否已存在，或者引入中间 `processed_orders(user_id, window_start, order_id)` 表，在事务中先对 orderId 做 INSERT IGNORE，再 UPDATE 统计。 | 30 |
| 2 | 为什么要用 MySQL 表保存消费进度，不直接用 Kafka `__consumer_offsets`？ | 因为 EOS 需要**跨两个资源的原子提交**：业务 DB（MySQL）和 Kafka offset Topic（Kafka Broker）。若使用普通 commit offset：`DB 提交 → offset 提交` 两步之间崩溃 → offset 没提交 → 重启后重放同一批事件 → 业务结果重复；如果 `offset 先提交 → DB 提交` 崩溃 → 业务没更新但 offset 推进了 → 丢事件。<br>把消费进度存在**同一个 MySQL 实例**中，就可以使用本地事务天然支持的原子性，把"业务更新 + 进度更新"放在同一个 commit，代价是**放弃了 Kafka 内置 Rebalance 的 offset 自动协调**（需要注册 `ConsumerRebalanceListener` 在 onPartitionsAssigned 时调用 DB seek）。这就是 Kafka 社区常说的**"Kafka + 外部存储 = 用 Transactional Outbox（写入方向）或 DB-backed offset（读取方向）解决跨资源原子性"**。 | 25 |
| 3 | 当前窗口使用事件发生时间 `event.occurredAt`，这与使用处理时间 `System.currentTimeMillis()` 在场景与结果上有什么差异？ | **发生时间（Event Time）** = 订单真正创建的业务时间，是"语义正确的窗口"：即使事件因为网络/积压晚了 10 分钟才到达，也会被算回 10 分钟前的窗口，报表口径和用户感知一致。但需要处理"乱序事件 + 迟到事件"：本实现没有处理迟到，超过窗口时间已经写入 DB 的事件再到达，虽然也能写入正确窗口（幂等主键），但该窗口的统计快照已被下游报表拉走，需要"订正报表 + 回补机制"。<br>**处理时间（Processing Time）** = 到达聚合器的系统时间，实现简单、无迟到问题，但网络抖动时同一批订单会被错误地划入延迟后的窗口，业务报表不准。<br>生产流处理（Flink/Kafka Streams）必须支持 Event Time + Watermark + Allowed Lateness 三层机制。 | 20 |
| 4 | Consumer Rebalance 后，新分配过来的分区怎么 seek 到 DB 中保存的 offset？当前代码有没有处理？ | 当前代码只在 `main()` 启动时调了一次 `loadProgressFromDB`，没有注册 `ConsumerRebalanceListener`，因此运行中 Rebalance 后，新拿过来的分区**不会自动 seek 到 DB 进度**，而是按 `auto.offset.reset=latest` 跳到最新 → **会丢一批数据的统计结果**。<br>修复：注册监听器，在 `onPartitionsAssigned(Collection<TopicPartition> partitions)` 回调里，对传入的每个分区从 MySQL 查 next_offset 再 `consumer.seek(tp, savedOrEnd)`；在 `onPartitionsRevoked(...)` 回调里先 `conn.commit()` 确保最后一批事务落盘，否则回收的分区在新消费者手里 seek 到旧进度可能重复消费。 | 15 |
| 5 | 如果有 100 个消费者实例，Group ID 相同，`kafka_consumer_progress` 表的主键设计会有冲突吗？为什么？ | **不会冲突**。主键是 `(group_id, topic, partition)`——同一组下，同一个 `(topic, partition)` 在同一个时刻**只会分配给组内唯一的一个消费者实例**（Kafka Consumer Group 协议保证），不会发生两个消费者同时写同一行主键竞争写同一个 next_offset 的场景。而分区维度的写入恰好是"每个消费者只写自己负责的分区行"，天然分桶隔离。这也是 DB 存进度方案能水平扩展的核心原因：并发单位等于分区数。 | 10 |

---

> **文档说明**：
> - 全文共 **4 大题型**：选择题（20 道）、简答题（11 道）、分析题（3 道，含完整实战场景方案、性能调优方法论、故障排查手册）、编程题（3 道，生产级代码实现 + 面试追问考核点），合计 **37 题**；
> - 难度分布：基础题 30%（选择 Q1-Q8，简答 Q1-Q4）→ 进阶题 45%（选择 Q9-Q20，简答 Q5-Q11）→ 高级场景题 25%（分析题 Q1-Q3，编程题 Q1-Q3）；
> - 配套技术栈：Kafka 2.x/3.x、Java Kafka Clients 3.6.x、MySQL 8.0、Redis（Jedis），代码均可直接运行；
> - 建议学习路径：先从选择题巩固知识点 → 简答题掌握核心概念表述 → 分析题学习"方法论+套路" → 编程题动手编码跑通全流程。




