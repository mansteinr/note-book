# Kafka 面试题汇总

> 适用版本：Kafka 2.x ~ 3.x | 适合 Java 开发人员、大数据工程师面试准备及知识巩固

## 目录

- [一、选择题](#一选择题)
  - [1.1 基础概念篇](#11-基础概念篇)
  - [1.2 架构设计篇](#12-架构设计篇)
  - [1.3 工作原理篇](#13-工作原理篇)
  - [1.4 性能优化篇](#14-性能优化篇)
- [二、简答题](#二简答题)
  - [2.1 核心概念与架构](#21-核心概念与架构)
  - [2.2 消息生产与消费](#22-消息生产与消费)
  - [2.3 存储与副本机制](#23-存储与副本机制)
  - [2.4 可靠性与一致性](#24-可靠性与一致性)
- [三、分析题](#三分析题)
  - [3.1 场景设计与方案选型](#31-场景设计与方案选型)
  - [3.2 性能瓶颈与调优分析](#32-性能瓶颈与调优分析)
  - [3.3 故障排查与问题定位](#33-故障排查与问题定位)
- [四、编程题](#四编程题)
  - [4.1 生产者编程实践](#41-生产者编程实践)
  - [4.2 消费者编程实践](#42-消费者编程实践)
  - [4.3 综合应用编程](#43-综合应用编程)

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
