# Kafka 简介及常用语法

## 目录
- [一、Kafka 简介](#一kafka-简介)
- [二、核心概念](#二核心概念)
- [三、安装与配置](#三安装与配置)
- [四、常用命令](#四常用命令)
- [五、Java API 使用](#五java-api-使用)
- [六、使用场景](#六使用场景)
- [七、性能优化](#七性能优化)
- [八、常见面试题](#八常见面试题)

---

## 一、Kafka 简介

### 1.1 什么是 Kafka

Apache Kafka 是一个分布式流处理平台,最初由 LinkedIn 开发,现为 Apache 顶级项目。它具有以下特点:

- **高吞吐量**: 能够处理百万级消息/秒
- **低延迟**: 消息发布和订阅的延迟时间在毫秒级别
- **可扩展性**: 支持水平扩展,通过增加节点提升处理能力
- **持久性**: 消息持久化到磁盘,支持数据备份
- **容错性**: 自动处理节点故障,保证服务可用性

### 1.2 Kafka 架构

```
Producer --> Broker Cluster --> Consumer Group
              |
              v
        Zookeeper/KRaft
```

**核心组件:**
- **Producer**: 消息生产者,负责发布消息到 Kafka
- **Consumer**: 消息消费者,负责订阅并处理消息
- **Broker**: Kafka 服务器节点,负责存储和转发消息
- **Topic**: 消息主题,消息的逻辑分类
- **Partition**: 分区,Topic 的物理分片,实现并行处理
- **Replica**: 副本,保证数据高可用
- **Consumer Group**: 消费者组,组内消费者共同消费 Topic

### 1.3 Kafka vs 其他消息队列

| 特性 | Kafka | RabbitMQ | RocketMQ |
|------|-------|----------|----------|
| 吞吐量 | 百万级/秒 | 万级/秒 | 十万级/秒 |
| 延迟 | 毫秒级 | 微秒级 | 毫秒级 |
| 消息回溯 | 支持 | 不支持 | 支持 |
| 分布式 | 天然支持 | 需要配置 | 天然支持 |
| 适用场景 | 大数据、日志收集 | 企业应用 | 电商、金融 |

---

## 二、核心概念

### 2.1 Topic 和 Partition

```
Topic: order-topic
├── Partition 0 (Leader: broker-0, Replicas: [0,1,2])
├── Partition 1 (Leader: broker-1, Replicas: [1,2,0])
└── Partition 2 (Leader: broker-2, Replicas: [2,0,1])
```

**关键特性:**
- 一个 Topic 可以有多个 Partition
- 每个 Partition 是一个有序的、不可变的消息序列
- Partition 分布在不同的 Broker 上
- 每个 Partition 可以有多个副本(Replica)

### 2.2 消息结构

```
Message
├── Key (可选): 用于分区路由
├── Value: 消息内容
├── Timestamp: 时间戳
├── Headers (可选): 消息头
└── Offset: 消息在 Partition 中的位置
```

### 2.3 Consumer Group

```
Consumer Group: order-service-group
├── Consumer-1 (消费 Partition 0)
├── Consumer-2 (消费 Partition 1)
└── Consumer-3 (消费 Partition 2)
```

**规则:**
- 一个 Partition 只能被组内一个消费者消费
- 一个消费者可以消费多个 Partition
- 不同消费者组可以独立消费同一个 Topic

### 2.4 Offset 管理

- **Consumer Offset**: 消费者在 Partition 中的消费位置
- **提交方式**:
  - 自动提交: `enable.auto.commit=true`
  - 手动提交: 同步提交 `commitSync()` 或异步提交 `commitAsync()`

---

## 三、安装与配置

### 3.1 下载安装

```bash
# 下载 Kafka
wget https://downloads.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz

# 解压
tar -xzf kafka_2.13-3.6.0.tgz
cd kafka_2.13-3.6.0
```

### 3.2 启动服务

```bash
# 1. 启动 Zookeeper (或使用 KRaft 模式)
bin/zookeeper-server-start.sh config/zookeeper.properties

# 2. 启动 Kafka Broker
bin/kafka-server-start.sh config/server.properties
```

### 3.3 核心配置

**server.properties 关键配置:**

```properties
# Broker 唯一标识
broker.id=0

# 监听地址
listeners=PLAINTEXT://localhost:9092

# 日志存储路径
log.dirs=/tmp/kafka-logs

# Zookeeper 连接地址
zookeeper.connect=localhost:2181

# 默认分区数
num.partitions=3

# 默认副本数
default.replication.factor=3

# 日志保留时间(小时)
log.retention.hours=168

# 日志段大小(bytes)
log.segment.bytes=1073741824
```

---

## 四、常用命令

### 4.1 Topic 操作

```bash
# 创建 Topic
bin/kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --topic order-topic \
  --partitions 3 \
  --replication-factor 3

# 查看所有 Topic
bin/kafka-topics.sh --list \
  --bootstrap-server localhost:9092

# 查看 Topic 详情
bin/kafka-topics.sh --describe \
  --bootstrap-server localhost:9092 \
  --topic order-topic

# 修改 Topic 配置
bin/kafka-topics.sh --alter \
  --bootstrap-server localhost:9092 \
  --topic order-topic \
  --partitions 6

# 删除 Topic
bin/kafka-topics.sh --delete \
  --bootstrap-server localhost:9092 \
  --topic order-topic
```

### 4.2 消息生产与消费

```bash
# 生产消息(控制台)
bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic order-topic

# 消费消息(从最新位置)
bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic order-topic \
  --from-beginning

# 消费消息(从头开始)
bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic order-topic \
  --from-beginning

# 指定消费者组
bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic order-topic \
  --group my-consumer-group
```

### 4.3 消费者组管理

```bash
# 查看所有消费者组
bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --list

# 查看消费者组详情
bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --group my-consumer-group

# 重置消费者组 Offset
bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group my-consumer-group \
  --reset-offsets \
  --to-earliest \
  --topic order-topic \
  --execute
```

### 4.4 性能测试

```bash
# 生产者性能测试
bin/kafka-producer-perf-test.sh \
  --topic order-topic \
  --num-records 1000000 \
  --record-size 1024 \
  --throughput -1 \
  --producer-props bootstrap.servers=localhost:9092

# 消费者性能测试
bin/kafka-consumer-perf-test.sh \
  --topic order-topic \
  --messages 1000000 \
  --bootstrap-server localhost:9092
```

---

## 五、Java API 使用

### 5.1 Maven 依赖

```xml
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-clients</artifactId>
    <version>3.6.0</version>
</dependency>
```

### 5.2 Producer 示例

```java
import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.serialization.StringSerializer;
import java.util.Properties;

public class KafkaProducerDemo {
    public static void main(String[] args) {
        // 1. 配置 Producer
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        
        // 可选配置
        props.put(ProducerConfig.ACKS_CONFIG, "all");           // 确认机制
        props.put(ProducerConfig.RETRIES_CONFIG, 3);            // 重试次数
        props.put(ProducerConfig.BATCH_SIZE_CONFIG, 16384);     // 批次大小
        props.put(ProducerConfig.LINGER_MS_CONFIG, 1);          // 延迟发送
        props.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 33554432); // 缓冲区大小
        
        // 2. 创建 Producer
        KafkaProducer<String, String> producer = new KafkaProducer<>(props);
        
        // 3. 发送消息
        for (int i = 0; i < 100; i++) {
            String key = "order-" + i;
            String value = "{\"orderId\":" + i + ",\"amount\":100}";
            
            ProducerRecord<String, String> record = 
                new ProducerRecord<>("order-topic", key, value);
            
            // 异步发送,带回调
            producer.send(record, (metadata, exception) -> {
                if (exception == null) {
                    System.out.println("发送成功: " + 
                        "Topic=" + metadata.topic() + 
                        ", Partition=" + metadata.partition() + 
                        ", Offset=" + metadata.offset());
                } else {
                    exception.printStackTrace();
                }
            });
        }
        
        // 4. 关闭 Producer
        producer.close();
    }
}
```

### 5.3 Consumer 示例

```java
import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.common.serialization.StringDeserializer;
import java.time.Duration;
import java.util.Collections;
import java.util.Properties;

public class KafkaConsumerDemo {
    public static void main(String[] args) {
        // 1. 配置 Consumer
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "order-consumer-group");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        
        // 可选配置
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");     // 从最早开始
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "false");       // 手动提交
        props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 500);             // 每次拉取最大条数
        props.put(ConsumerConfig.SESSION_TIMEOUT_MS_CONFIG, "45000");       // 会话超时
        
        // 2. 创建 Consumer
        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
        
        // 3. 订阅 Topic
        consumer.subscribe(Collections.singletonList("order-topic"));
        
        // 4. 拉取消息
        try {
            while (true) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                
                for (ConsumerRecord<String, String> record : records) {
                    System.out.printf("收到消息: Topic=%s, Partition=%d, Offset=%d, Key=%s, Value=%s%n",
                        record.topic(), record.partition(), record.offset(), 
                        record.key(), record.value());
                    
                    // 业务处理...
                }
                
                // 手动提交 Offset
                consumer.commitSync();
            }
        } finally {
            consumer.close();
        }
    }
}
```

### 5.4 Spring Boot 集成

**application.yml 配置:**

```yaml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.apache.kafka.common.serialization.StringSerializer
      acks: all
      retries: 3
      batch-size: 16384
      buffer-memory: 33554432
    consumer:
      group-id: order-consumer-group
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      auto-offset-reset: earliest
      enable-auto-commit: false
    listener:
      ack-mode: manual_immediate
      concurrency: 3
```

**Producer 服务:**

```java
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

@Service
public class OrderProducerService {
    
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    public void sendOrderMessage(String key, String message) {
        kafkaTemplate.send("order-topic", key, message)
            .addCallback(
                result -> System.out.println("发送成功"),
                ex -> System.err.println("发送失败: " + ex.getMessage())
            );
    }
}
```

**Consumer 服务:**

```java
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.stereotype.Service;

@Service
public class OrderConsumerService {
    
    @KafkaListener(topics = "order-topic", groupId = "order-consumer-group")
    public void processOrder(ConsumerRecord<String, String> record, Acknowledgment ack) {
        System.out.printf("处理订单: Key=%s, Value=%s%n", record.key(), record.value());
        
        // 业务处理...
        
        // 手动确认
        ack.acknowledge();
    }
}
```

---

## 六、使用场景

### 6.1 日志收集

**场景描述:**
收集分布式系统的日志,集中存储和分析。

**架构:**
```
App Server -> Kafka -> Logstash -> Elasticsearch -> Kibana
```

**优势:**
- 解耦日志生产者和消费者
- 高吞吐量,支持大量日志
- 消息持久化,可回溯

### 6.2 消息系统

**场景描述:**
异步处理业务逻辑,如订单处理、通知发送。

**示例:**
```
用户下单 -> 订单服务 -> Kafka -> 库存服务(扣减库存)
                            -> 积分服务(增加积分)
                            -> 通知服务(发送短信)
```

**优势:**
- 异步处理,提高响应速度
- 系统解耦,独立扩展
- 削峰填谷,保护下游系统

### 6.3 流处理

**场景描述:**
实时数据处理和分析。

**技术栈:**
- Kafka Streams
- Apache Flink
- Apache Spark Streaming

**示例:**
```
实时计算用户行为 -> 推荐系统
实时监控指标 -> 告警系统
实时数据聚合 -> 报表系统
```

### 6.4 事件溯源

**场景描述:**
将状态变化作为事件序列存储,支持回溯和重放。

**应用:**
- CQRS(命令查询职责分离)架构
- 审计日志
- 数据恢复

### 6.5 数据管道

**场景描述:**
在系统间传输数据,如 ETL 过程。

**示例:**
```
业务数据库 -> Kafka Connect -> Kafka -> Kafka Connect -> 数据仓库
```

---

## 七、性能优化

### 7.1 Producer 优化

#### 7.1.1 批量发送

```java
// 增大批次大小
props.put(ProducerConfig.BATCH_SIZE_CONFIG, 65536); // 64KB

// 增加延迟时间,等待更多消息
props.put(ProducerConfig.LINGER_MS_CONFIG, 10); // 10ms
```

#### 7.1.2 压缩消息

```java
// 启用 LZ4 压缩
props.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "lz4");

// 其他选项: none, gzip, snappy, lz4, zstd
```

#### 7.1.3 调整缓冲区

```java
// 增大缓冲区
props.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 67108864); // 64MB
```

#### 7.1.4 幂等性生产

```java
// 启用幂等性,防止重复
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
```

### 7.2 Consumer 优化

#### 7.2.1 增加并发

```java
// 增加消费者实例数
// 确保消费者数 <= 分区数
```

#### 7.2.2 调整拉取参数

```java
// 每次拉取最大条数
props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 1000);

// 拉取最小字节数
props.put(ConsumerConfig.FETCH_MIN_BYTES_CONFIG, 1048576); // 1MB

// 拉取最大等待时间
props.put(ConsumerConfig.FETCH_MAX_WAIT_MS_CONFIG, 500);
```

#### 7.2.3 优化 Offset 提交

```java
// 批量处理后提交,而不是每条提交
for (ConsumerRecord<String, String> record : records) {
    process(record);
}
consumer.commitSync();
```

### 7.3 Broker 优化

#### 7.3.1 磁盘 I/O 优化

```properties
# 使用多个日志目录,分散 I/O
log.dirs=/disk1/kafka-logs,/disk2/kafka-logs,/disk3/kafka-logs

# 增加页缓存
# 操作系统层面调整
```

#### 7.3.2 网络优化

```properties
# 增加网络线程数
num.network.threads=8

# 增加 IO 线程数
num.io.threads=16

# 增大 Socket 缓冲区
socket.send.buffer.bytes=1048576
socket.receive.buffer.bytes=1048576
```

#### 7.3.3 日志保留策略

```properties
# 基于时间保留
log.retention.hours=168

# 基于大小保留
log.retention.bytes=10737418240 # 10GB

# 日志清理策略
log.cleanup.policy=delete # 或 compact
```

#### 7.3.4 分区优化

```properties
# 增加分区数,提高并行度
num.partitions=12

# 调整副本数
default.replication.factor=3

# 最小同步副本数
min.insync.replicas=2
```

### 7.4 监控指标

**关键指标:**
- **Producer**: 发送速率、错误率、延迟
- **Consumer**: 消费速率、Lag(延迟)、重平衡次数
- **Broker**: CPU、内存、磁盘 I/O、网络流量
- **Topic**: 消息速率、分区分布

**监控工具:**
- Kafka Manager
- Prometheus + Grafana
- JMX Exporter

---

## 八、常见面试题

### 8.1 基础概念题

#### Q1: Kafka 为什么这么快?

**答案:**

1. **顺序写入**: 消息追加写入磁盘,顺序 I/O 比随机 I/O 快得多
2. **页缓存**: 利用操作系统的页缓存,减少磁盘 I/O
3. **零拷贝**: 使用 sendfile 系统调用,减少数据拷贝次数
4. **批量处理**: 消息批量发送和压缩,减少网络传输
5. **分区并行**: 多个分区并行处理,提高吞吐量
6. **高效序列化**: 支持高效的序列化/反序列化机制

#### Q2: Kafka 如何保证消息不丢失?

**答案:**

**Producer 端:**
- 设置 `acks=all`,确保所有副本确认
- 设置 `retries>0`,失败重试
- 启用幂等性 `enable.idempotence=true`

**Broker 端:**
- 设置 `replication.factor>=3`,多副本
- 设置 `min.insync.replicas>=2`,最小同步副本数
- 使用 RAID 磁盘,提高磁盘可靠性

**Consumer 端:**
- 关闭自动提交 `enable.auto.commit=false`
- 处理完消息后手动提交 Offset
- 使用幂等消费,防止重复处理

#### Q3: Kafka 如何保证消息顺序?

**答案:**

1. **单分区顺序**: 同一个 Partition 内消息有序
2. **Key 路由**: 相同 Key 的消息路由到同一 Partition
3. **单线程消费**: 一个 Partition 只被一个消费者线程消费

**注意:**
- 全局有序需要单分区,影响性能
- 通常只需要局部有序(如订单状态变更)

#### Q4: Kafka 的 Rebalance 机制是什么?

**答案:**

**触发条件:**
- 消费者组成员变化(加入/退出)
- Topic 分区数变化
- 消费者崩溃或超时

**过程:**
1. 协调器(Coordinator)检测变化
2. 所有消费者加入 Rebalance
3. 重新分配 Partition 给消费者
4. 完成分配,恢复消费

**优化:**
- 使用静态成员身份,减少不必要的 Rebalance
- 调整 `session.timeout.ms` 和 `heartbeat.interval.ms`
- 使用增量 Rebalance(Kafka 2.4+)

### 8.2 架构设计题

#### Q5: 如何设计一个高吞吐量的 Kafka 应用?

**答案:**

**Producer 设计:**
- 批量发送: 增大 `batch.size` 和 `linger.ms`
- 启用压缩: 使用 `lz4` 或 `zstd`
- 异步发送: 使用回调机制,不阻塞主线程
- 分区策略: 合理设计 Key,均匀分布到各分区

**Consumer 设计:**
- 增加消费者实例: 与分区数匹配
- 批量处理: 一次拉取多条消息
- 异步处理: 业务逻辑异步执行
- 优化提交: 批量处理后提交 Offset

**Broker 设计:**
- 增加分区数: 提高并行度
- 多磁盘目录: 分散 I/O
- 调整线程数: 增加网络和 I/O 线程
- 合理保留策略: 避免磁盘占满

#### Q6: Kafka 和 Zookeeper 的关系是什么?

**答案:**

**Zookeeper 的作用:**
- **元数据管理**: 存储 Topic、Partition、Broker 等元数据
- **Controller 选举**: 选举集群控制器
- **配置管理**: 存储 Broker 和 Topic 配置
- **消费者组管理**: 早期版本存储消费者 Offset

**KRaft 模式(Kafka 3.0+):**
- 移除 Zookeeper 依赖
- 使用 Raft 协议进行元数据管理
- 简化部署和运维
- 支持更多分区数

#### Q7: 如何处理 Kafka 的消息积压?

**答案:**

**临时方案:**
1. 增加消费者实例数
2. 增加 Topic 分区数
3. 临时创建新 Topic,快速转发消息

**根本方案:**
1. 优化消费逻辑,提高处理速度
2. 异步处理业务逻辑
3. 批量处理消息
4. 使用流处理框架(如 Flink)

**预防措施:**
1. 监控 Consumer Lag
2. 设置告警阈值
3. 容量规划,预留资源

### 8.3 实战应用题

#### Q8: Kafka 如何实现延迟消息?

**答案:**

**方案一: 多个延迟 Topic**
```
创建延迟 1s、5s、1min、5min 等 Topic
生产者根据延迟时间发送到对应 Topic
消费者消费后判断是否需要继续延迟
```

**方案二: 时间轮算法**
```
使用 Kafka Streams 实现时间轮
消息按延迟时间分桶
定时触发到期消息
```

**方案三: 外部延迟队列**
```
使用 Redis 或 RocketMQ 的延迟消息
到期后发送到 Kafka
```

#### Q9: Kafka 如何实现事务消息?

**答案:**

**Producer 事务:**

```java
props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "my-transaction-id");

producer.initTransactions();
try {
    producer.beginTransaction();
    producer.send(new ProducerRecord<>("topic1", "key1", "value1"));
    producer.send(new ProducerRecord<>("topic2", "key2", "value2"));
    producer.commitTransaction();
} catch (Exception e) {
    producer.abortTransaction();
}
```

**Consumer 事务:**

```java
props.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");
// 只读取已提交的消息
```

**应用场景:**
- 跨 Topic 的原子操作
- 保证消息生产和 Offset 提交的一致性

#### Q10: 如何监控 Kafka 集群?

**答案:**

**监控指标:**

1. **Broker 指标:**
   - CPU、内存、磁盘使用率
   - 网络入/出流量
   - 请求处理延迟
   - Leader 选举次数

2. **Topic 指标:**
   - 消息生产速率
   - 消息消费速率
   - 分区分布情况
   - 日志段大小

3. **Consumer 指标:**
   - Consumer Lag(消费延迟)
   - 重平衡次数
   - 提交 Offset 频率

**监控工具:**

1. **Kafka Manager:** 官方管理工具
2. **Prometheus + Grafana:** 指标收集和可视化
3. **JMX Exporter:** 导出 JMX 指标
4. **Burrow:** 专门的 Consumer Lag 监控

**告警规则:**
- Consumer Lag > 阈值
- Broker 下线
- Leader 选举频繁
- 磁盘使用率 > 80%

### 8.4 性能调优题

#### Q11: 如何优化 Kafka 的吞吐量?

**答案:**

**Producer 优化:**
```java
// 1. 增大批次大小
props.put(ProducerConfig.BATCH_SIZE_CONFIG, 65536);

// 2. 增加延迟时间
props.put(ProducerConfig.LINGER_MS_CONFIG, 20);

// 3. 启用压缩
props.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "lz4");

// 4. 增大缓冲区
props.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 67108864);
```

**Consumer 优化:**
```java
// 1. 增加拉取条数
props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 1000);

// 2. 调整拉取大小
props.put(ConsumerConfig.FETCH_MIN_BYTES_CONFIG, 1048576);

// 3. 增加消费者实例
// 确保消费者数 <= 分区数
```

**Broker 优化:**
```properties
# 1. 增加分区数
num.partitions=12

# 2. 多日志目录
log.dirs=/disk1/kafka-logs,/disk2/kafka-logs

# 3. 调整线程数
num.network.threads=8
num.io.threads=16
```

#### Q12: 如何降低 Kafka 的延迟?

**答案:**

**Producer 端:**
```java
// 1. 减少延迟时间
props.put(ProducerConfig.LINGER_MS_CONFIG, 0);

// 2. 减小批次大小
props.put(ProducerConfig.BATCH_SIZE_CONFIG, 1024);

// 3. 调整确认机制
props.put(ProducerConfig.ACKS_CONFIG, "1"); // 或 "0"
```

**Consumer 端:**
```java
// 1. 减少拉取等待时间
props.put(ConsumerConfig.FETCH_MAX_WAIT_MS_CONFIG, 100);

// 2. 减小拉取大小
props.put(ConsumerConfig.FETCH_MIN_BYTES_CONFIG, 1);
```

**Broker 端:**
```properties
# 1. 使用 SSD 磁盘
# 2. 增加页缓存
# 3. 优化网络配置
```

#### Q13: Kafka 的零拷贝是如何实现的?

**答案:**

**传统 I/O(4次拷贝):**
```
磁盘 -> 内核缓冲区 -> 用户缓冲区 -> Socket缓冲区 -> 网络
```

**零拷贝(2次拷贝):**
```
磁盘 -> 内核缓冲区 -> 网络(使用 sendfile)
```

**实现原理:**
- 使用 `sendfile()` 系统调用
- 数据不经过用户空间
- 减少 CPU 拷贝次数
- 提高网络传输效率

**Kafka 应用:**
- Consumer 拉取消息时使用零拷贝
- Broker 转发消息时使用零拷贝

---

## 附录: 常用配置参考

### Producer 配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| acks | 1 | 确认机制(0/1/all) |
| retries | 0 | 重试次数 |
| batch.size | 16384 | 批次大小(bytes) |
| linger.ms | 0 | 延迟发送时间(ms) |
| buffer.memory | 33554432 | 缓冲区大小(bytes) |
| compression.type | none | 压缩类型 |
| max.in.flight.requests.per.connection | 5 | 最大未确认请求数 |

### Consumer 配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| group.id | - | 消费者组 ID |
| auto.offset.reset | latest | Offset 重置策略 |
| enable.auto.commit | true | 自动提交 Offset |
| max.poll.records | 500 | 每次拉取最大条数 |
| session.timeout.ms | 45000 | 会话超时时间(ms) |
| fetch.min.bytes | 1 | 最小拉取字节数 |
| fetch.max.wait.ms | 500 | 最大等待时间(ms) |

### Broker 配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| broker.id | 0 | Broker 唯一标识 |
| log.dirs | /tmp/kafka-logs | 日志存储路径 |
| num.partitions | 1 | 默认分区数 |
| default.replication.factor | 1 | 默认副本数 |
| log.retention.hours | 168 | 日志保留时间(小时) |
| num.network.threads | 3 | 网络线程数 |
| num.io.threads | 8 | I/O 线程数 |

---

**文档版本:** v1.0  
**最后更新:** 2026-07-16  
**适用版本:** Kafka 3.x
