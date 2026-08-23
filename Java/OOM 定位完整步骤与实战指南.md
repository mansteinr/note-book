# 高级 Java：线上 OOM 定位完整步骤与实战指南

> 本文从**高级 Java 工程师生产环境排障视角**讲解 OOM 的完整定位流程，包括：
>
> - 如何判断 OOM 类型
> - 如何采集现场
> - 如何使用 `jstat`、`jcmd`、`jmap`、`jstack`
> - 如何分析 GC
> - 如何生成 Heap Dump
> - 如何使用 MAT 定位内存泄漏
> - 如何分析 GC Roots
> - 如何排查 Metaspace、Direct Memory、Native Thread 和容器 OOM

---

# 目录

- [1. OOM 定位的总体思路](#1-oom-定位的总体思路)
- [2. 常见 OOM 类型](#2-常见-oom-类型)
- [3. 生产环境 OOM 标准排查流程](#3-生产环境-oom-标准排查流程)
- [4. 第一步：确认进程和错误类型](#4-第一步确认进程和错误类型)
- [5. 第二步：查看 JVM 内存参数](#5-第二步查看-jvm-内存参数)
- [6. 第三步：观察 JVM 内存和 GC](#6-第三步观察-jvm-内存和-gc)
- [7. 第四步：生成 Heap Dump](#7-第四步生成-heap-dump)
- [8. 第五步：使用 MAT 分析 Heap Dump](#8-第五步使用-mat-分析-heap-dump)
- [9. 第六步：通过 GC Roots 定位代码](#9-第六步通过-gc-roots-定位代码)
- [10. Java Heap OOM 排查](#10-java-heap-oom-排查)
- [11. Metaspace OOM 排查](#11-metaspace-oom-排查)
- [12. Direct Memory OOM 排查](#12-direct-memory-oom-排查)
- [13. Native Thread OOM 排查](#13-native-thread-oom-排查)
- [14. Native Memory OOM 排查](#14-native-memory-oom-排查)
- [15. Kubernetes OOMKilled 排查](#15-kubernetes-oomkilled-排查)
- [16. MAT 实战案例](#16-mat-实战案例)
- [17. 常见 Java 内存泄漏场景](#17-常见-java-内存泄漏场景)
- [18. OOM 生产环境命令清单](#18-oom-生产环境命令清单)
- [19. 高级 Java 面试回答模板](#19-高级-java-面试回答模板)
- [20. 总结：一套完整 OOM 定位方法](#20-总结一套完整-oom-定位方法)

---

# 1. OOM 定位的总体思路

高级 Java 工程师定位 OOM，核心不是：

```text
发生 OOM
    ↓
增加 -Xmx
```

而是回答两个问题：

```text
1. 什么东西占用了大量内存？
```

以及：

```text
2. 为什么这些对象没有被 GC？
```

完整流程如下：

```text
                    OOM
                     │
                     ▼
              查看异常日志
                     │
                     ▼
              判断 OOM 类型
                     │
                     ▼
              查看 JVM 参数
                     │
                     ▼
              查看 GC 状态
                     │
                     ▼
              获取 Heap Dump
                     │
                     ▼
              MAT 分析对象
                     │
                     ▼
             Dominator Tree
                     │
                     ▼
              找到大对象
                     │
                     ▼
             Path to GC Roots
                     │
                     ▼
              分析引用链
                     │
                     ▼
              定位业务代码
                     │
                     ▼
              修复 + 压测
```

---

# 2. 常见 OOM 类型

Java 中常见的 OOM 并不只有一种。

## 2.1 Java Heap Space

```text
java.lang.OutOfMemoryError: Java heap space
```

表示：

```text
Java 堆内存不足
```

常见原因：

- 缓存无限增长
- `List`、`Map` 无限增长
- 大量对象无法释放
- 一次性查询大量数据
- 无界队列
- 内存泄漏

---

## 2.2 GC Overhead Limit Exceeded

```text
java.lang.OutOfMemoryError: GC overhead limit exceeded
```

说明 JVM：

```text
大量时间用于 GC
```

但是：

```text
GC 回收不了多少内存
```

通常表现：

```text
Young GC
    ↓
Full GC
    ↓
Young GC
    ↓
Full GC
    ↓
CPU 很高
```

---

## 2.3 Metaspace

```text
java.lang.OutOfMemoryError: Metaspace
```

通常和：

```text
动态代理
CGLIB
ByteBuddy
Groovy
ClassLoader 泄漏
```

有关。

---

## 2.4 Direct Buffer Memory

```text
java.lang.OutOfMemoryError: Direct buffer memory
```

常见于：

```text
Netty
NIO
Kafka
RocketMQ
文件 IO
```

---

## 2.5 Unable to Create New Native Thread

```text
java.lang.OutOfMemoryError:
unable to create new native thread
```

通常是：

```text
线程数量过多
```

或者：

```text
操作系统资源耗尽
```

---

## 2.6 Native Memory Allocation Failed

例如：

```text
Native memory allocation failed
```

说明：

```text
操作系统无法继续给 JVM 分配 Native Memory
```

---

# 3. 生产环境 OOM 标准排查流程

推荐记住：

```text
一看
二查
三监控
四 Dump
五分析
六定位
七修复
八验证
```

具体：

```text
① 看错误

② 查 JVM 参数

③ 看 GC

④ Dump Heap

⑤ MAT 分析

⑥ GC Roots 找引用链

⑦ 修改代码

⑧ 压测验证
```

---

# 4. 第一步：确认进程和错误类型

首先查看 Java 进程：

```bash
jps -l
```

例如：

```text
12345 com.example.Application
```

确认 PID：

```text
12345
```

然后查看：

```text
应用日志
```

例如：

```text
java.lang.OutOfMemoryError: Java heap space
```

那么排查方向就是：

```text
Java Heap
```

如果是：

```text
java.lang.OutOfMemoryError: Metaspace
```

则重点检查：

```text
Class
ClassLoader
动态代理
```

如果是：

```text
unable to create new native thread
```

则重点检查：

```text
线程数量
Xss
操作系统限制
```

> **第一原则：不同 OOM 类型，排查工具和方向不同。**

---

# 5. 第二步：查看 JVM 内存参数

查看 JVM 参数：

```bash
jinfo -flags 12345
```

或者：

```bash
jcmd 12345 VM.flags
```

重点关注：

```text
-Xms
-Xmx
-Xss
-XX:MaxMetaspaceSize
-XX:MaxDirectMemorySize
```

例如：

```text
-Xms4g
-Xmx4g
-Xss1m
-XX:MaxMetaspaceSize=512m
-XX:MaxDirectMemorySize=1g
```

注意：

```text
JVM 进程总内存
≠
-Xmx
```

JVM 实际内存大致包括：

```text
Java Heap
    +
Metaspace
    +
Direct Memory
    +
Thread Stack
    +
Code Cache
    +
JVM Native Memory
```

因此：

```text
-Xmx=4G
```

并不意味着 Java 进程只会占用：

```text
4G
```

可能最终占用：

```text
6G
8G
甚至更多
```

---

# 6. 第三步：观察 JVM 内存和 GC

推荐使用：

```bash
jstat -gcutil 12345 1000
```

表示：

```text
每 1 秒查看一次 GC 状态
```

可能看到：

```text
S0     S1      E      O      M
0.00   50.0    70.0   85.0   95.0
```

重点关注：

```text
O
```

即：

```text
Old Generation
```

如果发现：

```text
60%

↓

70%

↓

80%

↓

90%

↓

95%
```

持续增长。

然后发生 Full GC：

```text
95%

↓

92%
```

几乎没有下降。

那么通常说明：

```text
大量对象仍然存活
```

可能存在：

```text
内存泄漏
缓存无限增长
静态集合
ThreadLocal
无界队列
```

---

## 6.1 观察对象数量

可以执行：

```bash
jcmd 12345 GC.class_histogram
```

例如：

```text
 num     #instances         #bytes  class name
------------------------------------------------
   1:       5000000       240000000  java.lang.String
   2:       3000000       192000000  java.util.HashMap$Node
   3:       1000000       128000000  byte[]
```

此时可以快速发现：

```text
String 数量异常
```

或者：

```text
HashMap 节点数量异常
```

但是需要注意：

> `class_histogram` 只能帮助发现异常对象，真正定位原因通常还需要 Heap Dump。

---

# 7. 第四步：生成 Heap Dump

推荐优先使用：

```bash
jcmd 12345 GC.heap_dump /data/heap/heap.hprof
```

如果 JVM 已经 OOM，建议提前配置：

```bash
-XX:+HeapDumpOnOutOfMemoryError
```

同时指定路径：

```bash
-XX:HeapDumpPath=/data/heapdump
```

完整示例：

```bash
JAVA_OPTS="
-Xms4g
-Xmx4g
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/data/heapdump
"
```

发生 OOM 时会自动生成：

```text
java_pid12345.hprof
```

---

## 7.1 jmap 和 jcmd 的区别

传统方式：

```bash
jmap -dump:format=b,file=heap.hprof 12345
```

更推荐：

```bash
jcmd 12345 GC.heap_dump heap.hprof
```

生产环境中建议优先：

```text
jcmd
```

因为：

```text
功能更统一
HotSpot 官方工具链更推荐
```

但无论使用哪种方式：

> Heap Dump 都可能带来明显 IO 和暂停开销，必须评估生产环境影响。

---

# 8. 第五步：使用 MAT 分析 Heap Dump

推荐工具：

```text
Eclipse Memory Analyzer Tool
```

简称：

```text
MAT
```

打开：

```text
heap.hprof
```

重点使用以下功能。

---

## 8.1 Leak Suspects

MAT 会自动分析：

```text
可能存在的内存泄漏
```

例如：

```text
One instance of java.util.HashMap
retains 4.2GB
```

说明：

```text
某个 HashMap
```

通过引用关系：

```text
持有了 4.2GB 内存
```

---

## 8.2 Histogram

查看：

```text
对象类型

实例数量

Shallow Heap

Retained Heap
```

例如：

```text
byte[]

实例：

5000000

占用：

3GB
```

此时需要进一步分析：

```text
这些 byte[] 是谁创建的？
```

---

## 8.3 Dominator Tree

这是 OOM 分析中最重要的功能之一。

假设：

```text
ConcurrentHashMap

Retained Heap:

5.6GB
```

展开：

```text
ConcurrentHashMap
        │
        ▼
UserCache
        │
        ▼
static CACHE
        │
        ▼
User
```

说明：

```text
static CACHE
```

持有大量：

```text
User
```

对象。

---

# 9. 第六步：通过 GC Roots 定位代码

假设发现：

```text
List

Retained Heap:

3GB
```

下一步：

```text
右键

Path to GC Roots
```

可能看到：

```text
GC Root
    │
    ▼
static field
    │
    ▼
CacheManager
    │
    ▼
HashMap
    │
    ▼
List
    │
    ▼
大量对象
```

此时真正的问题不是：

```text
List
```

而是：

```text
CacheManager.static HashMap
```

因为：

```text
static 变量生命周期
=
JVM 生命周期
```

如果：

```text
HashMap
```

不断增加：

```text
对象永远无法释放
```

最终：

```text
OOM
```

---

# 10. Java Heap OOM 排查

异常：

```text
java.lang.OutOfMemoryError: Java heap space
```

完整步骤：

## 第一步

查看：

```bash
jstat -gcutil PID 1000
```

判断：

```text
Old Gen 是否持续增长
```

---

## 第二步

查看对象：

```bash
jcmd PID GC.class_histogram
```

找：

```text
实例数量异常的对象
```

---

## 第三步

生成 Heap Dump：

```bash
jcmd PID GC.heap_dump heap.hprof
```

---

## 第四步

MAT：

```text
Leak Suspects
```

↓

```text
Histogram
```

↓

```text
Dominator Tree
```

---

## 第五步

找到：

```text
Retained Heap 最大的对象
```

---

## 第六步

执行：

```text
Path to GC Roots
```

找到：

```text
谁一直引用这个对象
```

---

## 第七步

定位代码。

例如：

```java
private static final Map<String, User> CACHE =
        new ConcurrentHashMap<>();
```

问题：

```text
缓存无限增长
```

修复：

```text
设置最大容量
```

和：

```text
设置过期时间
```

---

# 11. Metaspace OOM 排查

异常：

```text
java.lang.OutOfMemoryError: Metaspace
```

Metaspace 主要保存：

```text
Class Metadata
Method Metadata
```

常见问题：

```text
动态生成 Class
```

例如：

```text
CGLIB

ByteBuddy

ASM

动态代理
```

---

## 排查 ClassLoader

可以查看：

```bash
jcmd PID VM.classloaders
```

或者：

```bash
jmap -clstats PID
```

如果：

```text
ClassLoader 数量
```

不断增长：

```text
1000

↓

5000

↓

10000

↓

50000
```

可能存在：

```text
ClassLoader 泄漏
```

---

# 12. Direct Memory OOM 排查

异常：

```text
java.lang.OutOfMemoryError: Direct buffer memory
```

例如：

```java
ByteBuffer buffer =
        ByteBuffer.allocateDirect(
                1024 * 1024
        );
```

Direct Memory：

```text
不属于 Java Heap
```

因此：

```text
-Xmx
```

不能直接限制 Direct Memory。

需要关注：

```bash
-XX:MaxDirectMemorySize
```

例如：

```bash
-XX:MaxDirectMemorySize=1g
```

常见场景：

```text
Netty ByteBuf

NIO Buffer

Kafka Client

大文件传输
```

---

# 13. Native Thread OOM 排查

异常：

```text
java.lang.OutOfMemoryError:
unable to create new native thread
```

首先查看线程数量：

```bash
ps -eLf | grep java | wc -l
```

查看 JVM 线程：

```bash
jcmd PID Thread.print
```

或者：

```bash
jstack PID
```

如果发现：

```text
5000

10000

20000
```

线程。

需要检查：

```text
线程池配置

是否重复创建线程池

是否无限创建 Thread

线程是否泄漏
```

例如错误代码：

```java
while (true) {

    new Thread(() -> {

        try {
            Thread.sleep(1000000);
        } catch (Exception e) {
        }

    }).start();
}
```

最终：

```text
unable to create new native thread
```

---

# 14. Native Memory OOM 排查

JVM 进程：

```text
RSS = 20GB
```

但是：

```text
-Xmx = 8GB
```

说明还有：

```text
12GB
```

Native Memory。

建议 JVM 启动：

```bash
-XX:NativeMemoryTracking=summary
```

然后查看：

```bash
jcmd PID VM.native_memory summary
```

例如：

```text
Total:

reserved=12GB

committed=10GB
```

细分：

```text
Java Heap

Class

Thread

Code

GC

Compiler

Internal
```

如果：

```text
Thread
```

特别大。

说明：

```text
线程数量过多
```

如果：

```text
Class
```

特别大。

可能：

```text
Metaspace

ClassLoader
```

存在问题。

---

# 15. Kubernetes OOMKilled 排查

Kubernetes 中可能看到：

```text
OOMKilled
```

但 Java 日志中：

```text
没有 OutOfMemoryError
```

这是因为：

```text
Linux Kernel
```

直接杀死 Java 进程。

查看：

```bash
kubectl describe pod pod-name
```

可能看到：

```text
Reason: OOMKilled
```

例如：

```yaml
resources:
  limits:
    memory: 4Gi
```

但是：

```text
Java Heap = 3GB

Direct Memory = 1GB

Metaspace = 500MB

Thread Stack = 500MB
```

实际：

```text
5GB+
```

超过：

```text
4Gi
```

因此被：

```text
OOMKilled
```

---

# 16. MAT 实战案例

假设线上服务：

```text
启动：

2GB

1 小时后：

3GB

2 小时后：

5GB

4 小时后：

8GB

最终：

OOM
```

---

## 第一步：jstat

```bash
jstat -gcutil PID 1000
```

发现：

```text
Old Gen：

60%

↓

70%

↓

80%

↓

90%

↓

95%
```

Full GC 后：

```text
95%

↓

92%
```

说明：

```text
对象大量存活
```

---

## 第二步：Dump

```bash
jcmd PID GC.heap_dump heap.hprof
```

---

## 第三步：MAT

Dominator Tree：

```text
ConcurrentHashMap

Retained Heap:

5.2GB
```

继续展开：

```text
ConcurrentHashMap
        │
        ▼
UserCache
        │
        ▼
static CACHE
        │
        ▼
User
```

代码：

```java
public class UserCache {

    private static final Map<Long, User> CACHE =
            new ConcurrentHashMap<>();

    public User getUser(Long id) {

        User user = CACHE.get(id);

        if (user == null) {

            user = queryUser(id);

            CACHE.put(id, user);
        }

        return user;
    }
}
```

问题：

```text
缓存没有：

maximumSize

TTL
```

因此：

```text
用户越多
```

↓

```text
CACHE 越大
```

↓

```text
对象无法释放
```

↓

```text
OOM
```

---

## 修复

使用 Caffeine：

```java
Cache<Long, User> cache =
        Caffeine.newBuilder()
                .maximumSize(100_000)
                .expireAfterWrite(
                        30,
                        TimeUnit.MINUTES
                )
                .build();
```

最终：

```text
缓存容量可控

对象可以淘汰

Old Gen 稳定

GC 正常
```

---

# 17. 常见 Java 内存泄漏场景

## 17.1 static 集合

```java
private static final Map<String, Object> CACHE =
        new ConcurrentHashMap<>();
```

如果没有：

```text
最大容量

过期时间
```

风险非常高。

---

## 17.2 ThreadLocal

错误：

```java
ThreadLocal<User> threadLocal =
        new ThreadLocal<>();

threadLocal.set(user);
```

线程池环境：

```text
线程长期存在
```

正确：

```java
try {

    threadLocal.set(user);

    process();

} finally {

    threadLocal.remove();
}
```

---

## 17.3 无界队列

错误：

```java
BlockingQueue<Task> queue =
        new LinkedBlockingQueue<>();
```

默认：

```text
容量非常大
```

如果：

```text
生产速度

>

消费速度
```

那么：

```text
消息不断堆积
```

↓

```text
OOM
```

正确：

```java
BlockingQueue<Task> queue =
        new LinkedBlockingQueue<>(10000);
```

同时需要：

```text
限流

拒绝策略

背压
```

---

## 17.4 Listener 未注销

例如：

```java
eventBus.register(listener);
```

但是：

```text
没有 unregister
```

引用链：

```text
EventBus
    │
    ▼
Listener
    │
    ▼
业务对象
```

最终：

```text
业务对象无法 GC
```

---

## 17.5 一次性加载大数据

错误：

```java
List<User> users =
        userMapper.selectAll();
```

如果数据库：

```text
1000 万数据
```

全部加载到 JVM：

```text
OOM
```

应该使用：

```text
分页

流式查询

批处理
```

---

# 18. OOM 生产环境命令清单

## 查看 Java 进程

```bash
jps -l
```

## 查看 JVM 参数

```bash
jinfo -flags PID
```

## 查看 GC

```bash
jstat -gcutil PID 1000
```

## 查看 Heap 信息

```bash
jcmd PID GC.heap_info
```

## 查看对象统计

```bash
jcmd PID GC.class_histogram
```

## 获取 Heap Dump

```bash
jcmd PID GC.heap_dump /data/heap.hprof
```

## 查看线程

```bash
jcmd PID Thread.print
```

或者：

```bash
jstack PID
```

## 查看 Native Memory

```bash
jcmd PID VM.native_memory summary
```

前提：

```bash
-XX:NativeMemoryTracking=summary
```

---

# 19. 高级 Java 面试回答模板

## 面试题

> 如果线上 Java 服务发生 OOM，你如何定位？

推荐回答：

> 首先我不会直接增加 Xmx，而是先根据异常日志确认具体的 OOM 类型，比如 Java Heap、Metaspace、Direct Memory 或 Native Thread，因为不同类型的排查方向不同。
>
> 如果是 Java Heap OOM，我首先会通过 `jinfo` 或 `jcmd` 查看 JVM 参数，然后使用 `jstat -gcutil` 观察 Old Gen 的变化以及 Full GC 后内存是否能够正常下降。
>
> 如果发现 Old Gen 持续上涨，Full GC 后也无法明显下降，我会怀疑存在内存泄漏。接下来通过 `jcmd GC.heap_dump` 获取 Heap Dump。
>
> 然后使用 MAT 分析 Heap Dump，重点查看 `Leak Suspects`、`Histogram` 和 `Dominator Tree`，找到 Retained Heap 最大的对象。
>
> 最后通过 `Path to GC Roots` 分析对象的引用链，定位为什么对象无法被 GC，例如 static Map、ThreadLocal、缓存、无界队列或者 Listener。
>
> 修复后会重新进行压测，并持续观察 Old Gen、Full GC 次数和进程 RSS，确认内存不会持续增长。

---

# 20. 总结：一套完整 OOM 定位方法

高级 Java 工程师建议牢记下面这套流程：

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

第一步：确认 OOM 类型

Java Heap？
Metaspace？
Direct Memory？
Native Thread？
Container OOM？

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

第二步：查看 JVM 参数

-Xms
-Xmx
-Xss
MaxMetaspaceSize
MaxDirectMemorySize

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

第三步：查看 GC

jstat -gcutil

重点：

Old Gen

Full GC

GC 后内存是否下降

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

第四步：查看对象

jcmd GC.class_histogram

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

第五步：Heap Dump

jcmd GC.heap_dump

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

第六步：MAT

Leak Suspects

Histogram

Dominator Tree

Retained Heap

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

第七步：GC Roots

Path to GC Roots

找到引用链

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

第八步：定位代码

static

Cache

ThreadLocal

Queue

Listener

大对象

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

第九步：修复

限制缓存

设置 TTL

有界队列

remove ThreadLocal

分页 / 流式处理

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

第十步：压测验证

观察：

Heap

Old Gen

Full GC

RSS

CPU

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 最终口诀

```text
看异常
查参数
观 GC
Dump 堆
看 MAT
找大对象
查 Roots
定代码
做修复
压测验证
```

真正高级的 OOM 排查能力，不是会执行几个 JVM 命令，而是能够从：

```text
异常

→ JVM 内存区域

→ GC 行为

→ Heap Dump

→ Dominator Tree

→ GC Roots

→ 业务代码
```

形成一条完整的排查链路。