# 华为 OD 高级 Java 面试完全指南（无笔试 · 扩写版）

> 适用：高级 Java 工程师 / 高级程序员 / 技术专家岗位。已去掉机试部分，保留技术一面（源码级）、技术二面、HR 面、冲刺清单与完整项目案例。相对原版对每个问题答案进一步扩写，补充 **10+ 全新生产案例**。

---

## 目录

- [面试流程总览](#面试流程总览)
- [一、技术一面（源码级 · 答案扩写 + 30+ 项目案例）](#一技术一面源码级--答案扩写--30-项目案例)
  - [1.1 Java 基础：不止"会用"，要"为什么这样设计"](#11-java-基础不止会用要为什么这样设计)
    - [1.1.1 HashMap 源码级考点（putVal/resize/线程安全/树化阈值）](#111-hashmap-源码级考点putvalresize线程安全树化阈值)
    - [1.1.2 volatile + JMM + 指令重排 + DCL](#112-volatile--jmm--指令重排--dcl)
    - [1.1.3 synchronized 锁升级 + ReentrantLock + AQS](#113-synchronized-锁升级--reentrantlock--aqs)
    - [1.1.4 ThreadLocal 原理 + 内存泄漏 + InheritableThreadLocal](#114-threadlocal-原理--内存泄漏--inheritablethreadlocal)
    - [1.1.5 ThreadPoolExecutor 七大参数 + 执行流程源码](#115-threadpoolexecutor-七大参数--执行流程源码)
  - [1.2 JVM：从原理到调优实战](#12-jvm从原理到调优实战)
    - [1.2.1 运行时数据区 + 对象创建过程](#121-运行时数据区--对象创建过程)
    - [1.2.2 垃圾回收：算法 + 收集器（CMS/G1/ZGC 对比）+ 调优案例](#122-垃圾回收算法--收集器cmsg1zgc-对比--调优案例)
    - [1.2.3 类加载 + 双亲委派 + 打破场景](#123-类加载--双亲委派--打破场景)
  - [1.3 Spring：核心流程源码级掌握](#13-spring核心流程源码级掌握)
    - [1.3.1 IOC 容器核心：refresh() 12 步源码](#131-ioc-容器核心refresh-12-步源码)
    - [1.3.2 Bean 生命周期 + 扩展点时序 11 步](#132-bean-生命周期--扩展点时序-11-步)
    - [1.3.3 循环依赖：三级缓存 + earlySingletonObjects 作用](#133-循环依赖三级缓存--earlysingletonobjects-作用)
    - [1.3.4 AOP 代理 + @Transactional 事务 7 大失效场景](#134-aop-代理--transactional-事务-7-大失效场景)
    - [1.3.5 Spring Boot 自动装配流程 + 自定义 Starter 完整步骤](#135-spring-boot-自动装配流程--自定义-starter-完整步骤)
  - [1.4 并发编程：分布式场景](#14-并发编程分布式场景)
    - [1.4.1 分布式锁三种实现对比（Redis/ZK/DB）+ Redisson 看门狗](#141-分布式锁三种实现对比rediszkdb--redisson-看门狗)
    - [1.4.2 分布式事务：2PC/TCC/Saga/本地消息表/RocketMQ 事务消息](#142-分布式事务2pctccsaga本地消息表rocketmq-事务消息)
    - [1.4.3 RPC / Dubbo / Sentinel / SkyWalking 实战](#143-rpc--dubbo--sentinel--skywalking-实战)
  - [1.5 MySQL：深度 + 调优实战](#15-mysql深度--调优实战)
    - [1.5.1 B+ 树索引：计算方式 + 回表 + 覆盖索引 + 最左前缀](#151-b-树索引计算方式--回表--覆盖索引--最左前缀)
    - [1.5.2 MVCC + 4 种隔离级别 + RR 级别 Next-Key 防幻读](#152-mvcc--4-种隔离级别--rr-级别-next-key-防幻读)
    - [1.5.3 InnoDB 锁：行锁/Gap/Next-Key + 死锁排查 + redo/undo/binlog 2PC](#153-innodb-锁行锁gapnext-key--死锁排查--redoundobinlog-2pc)
  - [1.6 中间件高级](#16-中间件高级)
    - [1.6.1 Redis 高级：内部编码 + 持久化 + 主从/哨兵/Cluster + bigkey](#161-redis-高级内部编码--持久化--主从哨兵cluster--bigkey)
    - [1.6.2 Kafka 高吞吐设计 + Rebalance + ISR + 端到端零丢失](#162-kafka-高吞吐设计--rebalance--isr--端到端零丢失)
    - [1.6.3 RocketMQ 事务消息 + 主从同步 + 零拷贝](#163-rocketmq-事务消息--主从同步--零拷贝)
- [二、技术二面（架构设计 + 技术决策 + 排障）](#二技术二面架构设计--技术决策--排障)
  - [2.1 项目深挖：STAR 高级版（含完整订单性能优化案例）](#21-项目深挖star-高级版含完整订单性能优化案例)
  - [2.2 系统设计：秒杀/短链/支付/IM/排行榜 + 答题 8 步 SOP](#22-系统设计秒杀短链支付im排行榜--答题-8-步-sop)
  - [2.3 线上排障 6 大场景 SOP（CPU 100% / OOM / 慢接口 / 死锁 / MQ 积压 / Redis 变慢）](#23-线上排障-6-大场景-sopcpu-100--oom--慢接口--死锁--mq-积压--redis-变慢)
- [三、HR / 综合面（高级版差异）](#三hr--综合面高级版差异)
  - [3.1 自我介绍（3 分钟 / 1 分钟两版）](#31-自我介绍3-分钟--1-分钟两版)
  - [3.2 必问 8 大问题与应答模板](#32-必问-8-大问题与应答模板)
  - [3.3 反问面试官阶段清单](#33-反问面试官阶段清单)
- [四、冲刺资料清单与备考计划](#四冲刺资料清单与备考计划)
  - [4.1 必背源码清单（每个能讲 10 分钟+）](#41-必背源码清单每个能讲-10-分钟)
  - [4.2 系统设计学习路径](#42-系统设计学习路径)
  - [4.3 4 周在职冲刺计划（每天 2h + 周末 6h）](#43-4-周在职冲刺计划每天-2h--周末-6h)
- [五、附：真实项目 STAR 案例模板](#五附真实项目-star-案例模板)

---

# 面试流程总览

高级 Java 岗相对 3 年经验岗的核心差异：

| 维度 | 3 年 Java 岗 | 高级 Java 岗 |
|---|---|---|
| 技术一面深度 | 原理 + 使用 | **源码级** 能按行讲 HashMap.putVal / AQS.acquireQueued / refresh() 流程 |
| 并发范围 | 单机线程池 / AQS | **分布式锁** + **分布式事务** + RPC / Sentinel / SkyWalking 全链路 |
| 项目 STAR | 1 个优化案例 + 量化 | 2~3 个深度项目：架构选型对比（2~3 方案）、故障复盘（根因+预防）、数据量 10 倍演进 |
| 系统设计 | 秒杀 / 短链 | 秒杀 / 短链 + **支付系统** / **IM 长连接** / **排行榜** + 完整 8 步 SOP |
| 线上排障 | 3~4 场景 | 6 大场景 SOP：**Redis 变慢 / 死锁** 新增 |
| 源码要求 | 会讲大概流程 | **必背 16 个**：`putVal` / `resize` / `HashMap.hash()` / `AQS.acquireQueued()` / `ThreadPoolExecutor.execute()` / `addWorker()` / `Worker` 结构 / `refresh()` / `finishBeanFactoryInitialization()` / `populateBean()` / `registerBeanPostProcessors()` / `invokeBeanFactoryPostProcessors()` / `@Transactional` 代理 / `AutoConfigurationImportSelector.selectImports()` / `ConcurrentHashMap.putVal()` / InnoDB MVCC 可见性算法 |

---

# 一、技术一面（源码级 · 答案扩写 + 30+ 项目案例）

## 1.1 Java 基础：不止"会用"，要"为什么这样设计"

### 1.1.1 HashMap 源码级考点（putVal/resize/线程安全/树化阈值）

**Q1：JDK 8 HashMap 的 putVal 方法流程（请按源码行数展开）？**

源码位置：`java.util.HashMap.putVal()`（JDK 8u341 约 630~665 行）

```java
// final V putVal(int hash, K key, V value, boolean onlyIfAbsent, boolean evict)
final V putVal(int hash, K key, V value, boolean onlyIfAbsent, boolean evict) {
    Node<K,V>[] tab; Node<K,V> p; int n, i;
    // ① 空数组 → resize() 初始化（默认 newCap=16, newThr=16*0.75=12）
    if ((tab = table) == null || (n = tab.length) == 0)
        n = (tab = resize()).length;
    // ② 桶为空 → 直接放入（tab[i = (n-1)&hash]）
    if ((p = tab[i = (n - 1) & hash]) == null)
        tab[i] = newNode(hash, key, value, null);
    // ③ 桶不为空（hash 碰撞）
    else {
        Node<K,V> e; K k;
        // ③-1 key 相同：同一节点（== / equals）→ 后面覆盖 value
        if (p.hash == hash &&
            ((k = p.key) == key || (key != null && key.equals(k))))
            e = p;
        // ③-2 是 TreeNode → 红黑树 putTreeVal（如存在则返回旧节点）
        else if (p instanceof TreeNode)
            e = ((TreeNode<K,V>)p).putTreeVal(this, tab, hash, key, value);
        // ③-3 是链表 → 尾插法遍历（JDK 8 尾插，JDK 7 头插）
        else {
            for (int binCount = 0; ; ++binCount) {
                if ((e = p.next) == null) {
                    p.next = newNode(hash, key, value, null);
                    // binCount 从 0 开始计数，到 7 表示插入第 8 个节点 → 尝试树化
                    if (binCount >= TREEIFY_THRESHOLD - 1) // TREEIFY_THRESHOLD=8
                        treeifyBin(tab, hash);  // 若 tab.length < MIN_TREEIFY_CAPACITY(64) → 只 resize 不树化
                    break;
                }
                // 遍历过程中遇到 key 相等 → 跳出等后面覆盖
                if (e.hash == hash &&
                    ((k = e.key) == key || (key != null && key.equals(k))))
                    break;
                p = e;  // p 推进，继续下一个
            }
        }
        // ④ 存在旧节点（e!=null）→ 覆盖旧 value
        if (e != null) {
            V oldValue = e.value;
            if (!onlyIfAbsent || oldValue == null)
                e.value = value;
            afterNodeAccess(e);  // LinkedHashMap 用，HashMap 空实现
            return oldValue;     // 返回旧值，不 size++ 不 resize
        }
    }
    // ⑤ 修改计数（fail-fast，迭代器检测并发修改）
    ++modCount;
    // ⑥ size 超 threshold → resize 扩容
    if (++size > threshold)
        resize();
    afterNodeInsertion(evict);  // LinkedHashMap LRU 淘汰用
    return null;
}
```

**高频追问 1**：`treeifyBin` 里为什么还有一次 `if (tab.length < MIN_TREEIFY_CAPACITY)` 再扩容？
→ 树化有两个门槛：`binCount ≥ 8` **且** `tab.length ≥ 64`。数组小的时候 hash 冲突高，扩容比树化更有效。

**高频追问 2**：`hash()` 扰动函数为什么要 `h ^ (h >>> 16)`？
→ 高位 16 位右移 16 位再异或低位，让高位也参与 & (n-1) 运算，减少不同高位、相同低位碰撞（尤其 n 较小的时候）。

**项目案例 1：HashMap 并发 put 导致数据丢失**

```
S：电商商品中心商品详情缓存，并发 3000 QPS，冷启动期间用 HashMap 预热本地缓存
T：大促压测发现 ~1% 的商品 get 时返回 null（缓存丢失）
A：
  1. jstack -l <pid> 多次 dump，对比发现 2 条线程都在 HashMap.putVal
  2. 看源码定位：
     if (p = tab[i=(n-1)&hash]) == null) {
         tab[i] = newNode(...)    // 线程 A 和线程 B 先后判断 tab[i] 都为 null
                                  // 先写的那个被后写覆盖 → 丢一个节点
     }
  3. size++ 也非原子：++size 在字节码 4 条指令（getstatic/const_1/iadd/putstatic）
     ConcurrentHashMap 的 size 是 baseCount + CounterCell[] 分段求和
  4. 修复：改为 ConcurrentHashMap
  5. 进一步：Caffeine 作为 L1（最大 10000），Redis L2
R：
  ① 缓存命中率 78% → 96%
  ② 冷启动期间丢失率 1% → 0%
  ③ RT P99：120ms → 28ms
```

**项目案例 2：HashMap 树化引发的性能波动**

```
S：风控标签系统，user_id → List<Tag>，用 HashMap<String, List> 存每个用户的标签列表
T：每天凌晨 2:00~4:00 跑批打标签，偶尔出现 5 分钟 GC STW，批次超时
A：
  1. jstat -gcutil PID 5000 观察：Old 98% → Full GC 4 次 每次 STW 8~10s
  2. jmap -histo:live PID | head -20：HashMap$Node 占 18%，TreeNode 占 6%（异常高）
  3. Arthas heapAnalyzer 分析：HashMap 中约 3% 的桶被树化
     根因：user_id 生成器 20250812 + 0000 递增，低 16 位高度相似 →
           hash() 扰动后低 16 位仍相似 → 链表长 → 触发树化
     每个 TreeNode 比普通 Node 多 6 个指针（parent/left/right/prev/red/next），内存占用 ×2.5
  4. 修复方案：
     a) user_id 生成改为雪花算法（bit 分散）
     b) HashMap 初始容量设 2 × 预估条数，减少 resize
     c) 批量任务分片，每 10w 用户就落库释放 Map
R：
  老方案：打标签 1 小时 42 分，4 次 Full GC
  新方案：42 分钟完成，0 次 Full GC，Old 使用率 ≤ 55%
```

**Q2：resize() 扩容机制 + JDK 8 扩容优化？**

```
// resize() 三步：
// 1. 计算 newCap/newThr
//    oldCap == 0 → 空表初始化：newCap=16, newThr=16*0.75=12
//    oldCap ≥ MAXIMUM_CAPACITY(1<<30) → threshold = Integer.MAX_VALUE，不扩返回
//    其他：newCap = oldCap << 1（2 倍），newThr = oldThr << 1
// 2. new Node[newCap] 分配新数组
// 3. 遍历老表：
//    桶单节点 → newTab[e.hash & (newCap-1)] = e
//    树节点 → split()：分 loHead/hiHead，树节点 <6 退回链表
//    链表 → loTail/hiTail 双尾：保留原顺序（尾插法自然维持）

// JDK 8 核心优化：不用重新算 hash！
//   判断 e.hash & oldCap：
//     - == 0 → 位置不变（原位链表 lo）
//     - != 0 → 移动 oldCap 距离（高位链表 hi）
//   原因为什么？ newCap = oldCap << 1，(newCap-1) 比 (oldCap-1) 多一个高位 bit
//   hash 在那个 bit 上是 0/1 决定位置不变/移 oldCap
```

---

### 1.1.2 volatile + JMM + 指令重排 + DCL

**Q1：volatile 两大作用 + 内存屏障是什么？**

```
作用① 可见性：
  写 volatile：JVM 在写后插入 StoreLoad 屏障 → 刷回主内存（写 buffer flush）
  读 volatile：JVM 在读前插入 LoadLoad + LoadStore 屏障 → 从主内存 invalidate 本地缓存

作用② 有序性（禁止指令重排）：
  JMM 为 volatile 建立内存屏障策略：
    StoreStore | 写 | StoreLoad     ← volatile 写
    LoadLoad | 读 | LoadStore      ← volatile 读
  实际 x86 平台只有 StoreLoad 会被插入（LOCK 前缀指令），其他 3 种 x86 内存模型是 TSO，强一致天然禁止

Q2：DCL 为什么必须 volatile？
  public class Singleton {
      private static volatile Singleton INSTANCE;   // ← 必须 volatile
      public static Singleton get() {
          if (INSTANCE == null) {                  // 1st check 无锁
              synchronized (Singleton.class) {      // 2nd check 锁内
                  if (INSTANCE == null) {
                      INSTANCE = new Singleton();   // ★ 这里字节码 3 步
                      // 0: new #5 分配
                      // 3: dup
                      // 4: invokespecial #7 <init>  // B. 初始化
                      // 7: putstatic #9  INSTANCE  // C. 引用赋值
                      // → 可能重排为 A→C→B：C 赋值后 INSTANCE != null
                      //    其他线程 1st check 非空 → 返回未初始化对象（字段 null）→ NPE
                  }
              }
          }
          return INSTANCE;
      }
  }
  volatile 写后 StoreLoad 屏障保证 <init> 先完成才能 putstatic
```

**项目案例 3：DCL 少了 volatile 线上偶发 NPE**

```
S：支付网关，支付渠道是枚举配置，每个渠道对象用 DCL 初始化（很重，new 需要加载证书）
T：线上 0.001% 概率 NPE，堆栈在 getChannel().sign()，sign 方法用到的 cert 字段 null
A：
  1. Arthas watch com.xxx.ChannelHolder getChannel '{params, returnObj}' -n 10 -e '#{throwExp} != null'
     偶尔抓到 Channel 对象非空，但 cert = null
  2. Review 源码：
     private static volatile PayChannel INSTANCE;   ← ⚠️ 实际上 volatile 漏了！
  3. 解释：线程 A new PayChannel()，重排后先 putstatic，线程 B getChannel() 非空，
     但 <init> 还没把 cert 赋值 → cert == null → NPE
  4. 修复：加 volatile + 所有 DCL 全局 grep（find 4 处）一起修复
  5. 防御性：如果对象初始化实在太复杂，干脆用 Initialization-on-demand holder idiom（静态内部类，classloader <clinit> 天然安全）：
     public class PayChannel {
         private static class Holder { static final PayChannel INSTANCE = new PayChannel(); }
         public static PayChannel get() { return Holder.INSTANCE; }
     }
R：NPE 从 3~5 次/周 → 0 次
```

---

### 1.1.3 synchronized 锁升级 + ReentrantLock + AQS

**Q1：synchronized 锁升级完整流程（JDK 6 引入，JDK 8 默认开启）？**

```
对象头 Mark Word 64 bit：
  [unused:25][hashcode:31][unused:1][age:4][biased_lock:1][lock:2]  无锁（01，biased_lock=0）
  [JavaThread*:54][epoch:2][unused:1][age:4][biased_lock:1][lock:2]  偏向锁（01，biased_lock=1）
  [ptr_to_lock_record:62][lock:2]                                    轻量级锁（00）
  [ptr_to_heavyweight_monitor:62][lock:2]                            重量级锁（10）
  [empty:54][cms_free:3][marked:1][epoch:2][age:4][biased:1][lock:2] GC 标记

升级过程：
  ① NEW → 匿名偏向（biased_lock=1 thread=0 epoch=0）
  ② 第一次加锁：CAS 把自己 thread ID 写入 → 偏向锁
  ③ 同一线程再进入 → 判断 thread==自己 → 快速成功（0 额外开销）
  ④ 另一个线程竞争偏向锁 → 到达安全点 → 撤销偏向 → 升级轻量级锁
  ⑤ 轻量级锁：当前线程栈帧中建立 Lock Record，DISPLACED MARK WORD 存旧 Mark Word，CAS 把对象头指向栈 → 成功
  ⑥ 自旋 10 次（或自适应）仍未获得锁 → 升级重量级锁：ObjectMonitor(WaitSet + EntryList + cxq + owner + recursions)，park() 线程 → OS 调度阻塞
```

**Q2：AQS acquireQueued 核心源码？**

```java
// final boolean acquireQueued(final Node node, int arg)
// 入队之后自旋抢锁：前驱是 head 才 tryAcquire，抢不到就 park() 阻塞
final boolean acquireQueued(final Node node, int arg) {
    boolean failed = true;
    try {
        boolean interrupted = false;
        for (;;) {                                        // 死循环自旋
            final Node p = node.predecessor();
            if (p == head && tryAcquire(arg)) {           // ★ 前驱是 head 才尝试抢
                setHead(node);                            // 抢到 → 自己变 head，旧 head 出队
                p.next = null;
                failed = false;
                return interrupted;
            }
            if (shouldParkAfterFailedAcquire(p, node) &&  // 检查前驱 waitStatus：SIGNAL 才 park
                parkAndCheckInterrupt())                  // LockSupport.park(this) 阻塞，被 unpark 或中断返回
                interrupted = true;
        }
    } finally {
        if (failed) cancelAcquire(node);
    }
}
```

**项目案例 4：ReentrantLock 构造公平锁后吞吐量下降 70% 的根因与权衡**

```
S：风控规则引擎，规则 1000+，执行器用 ReentrantLock 控制共享数据字典读一致性
T：新版本上线发现 QPS 从 3000 → 900，压测下降 70%
A：
  1. Arthas profiler 生成 CPU 火焰图：sun.misc.Unsafe.park 占 52%
  2. flame graph 上看：FairSync.tryAcquire → hasQueuedPredecessors 频繁返回 true → 抢不到
  3. Review 代码：
     new ReentrantLock(true)   // 公平锁
  4. 原因：公平锁每次 tryAcquire 都判断 hasQueuedPredecessors()，
     一个线程 release 后下一个线程还没被 OS 唤醒 → 中间窗口没有线程在跑 → 吞吐量损失
     而非公平锁：任何线程 release 后下一个刚到达的线程 CAS 直接拿 → 少了 park/unpark OS 开销
  5. 我们的场景：不需要绝对公平，只要整体平均等待可控
R：
  ① 改为 new ReentrantLock(false) 非公平
  ② QPS 恢复 2950（恢复到 98%）
  ③ Artheas monitor：99 线等待时间从 15ms → 3ms，无线程饥饿（每个线程最多自旋 3 次后抢到）
  ↪ 高级追问回答："我们 1ms 级延迟用非公平，队列排队顺序不敏感；绝对公平（例如排队取票业务）选 FairSync"
```

---

### 1.1.4 ThreadLocal 原理 + 内存泄漏 + InheritableThreadLocal

**Q1：ThreadLocalMap 的 Entry 结构、为什么 key 是弱引用、value 为什么泄漏？**

```
// ThreadLocal.ThreadLocalMap.Entry：
static class Entry extends WeakReference<ThreadLocal<?>> {
    Object value;
    Entry(ThreadLocal<?> k, Object v) {
        super(k);              // ← key 是弱引用
        value = v;             // ← value 是强引用！
    }
}
引用链：
  Thread → threadLocals(ThreadLocalMap) → Entry[] → Entry.value (强引用)
                                     → Entry.get() = key (弱引用)
内存泄漏产生：
  ① 栈上 ThreadLocal ref = null（强引用释放）
  ② 下次 GC：弱引用 key 被回收 → Entry.get() = null（key 死了）
  ③ 但 Entry.value 仍被 Entry → ThreadLocalMap → Thread 强引用
  ④ 线程池场景线程不复用 → Thread 一直不销毁 → value 永远不回收 → 泄漏

为什么 JDK 设计成弱引用 key + 强引用 value？
  ★ 反问："如果 key 是强引用会怎样？"
  → ThreadLocal ref 设 null 后，ThreadLocal 对象也不回收，key/value 一起泄漏（更糟！）
  → 弱引用 key 至少能让 ThreadLocal 对象本身在 ref=null 时被回收
  → value 怎么保证不泄漏？JDK 在 get/set/remove 时遇到 key=null 的"脏 Entry"
    会执行 expungeStaleEntry(i) → value = null，清空一条链上的 stale entry
    → 这是"启发式清理"，不是每次都执行，所以可能残留！
  ★ 正确用法：用完必须在 finally 手动 remove()
```

**项目案例 5：ThreadLocal 线程池复用时用户 A 看到用户 B 的数据**

```
S：微服务网关，登录 Token 解析后放 ThreadLocal，下游 Service.get() 读取
T：线上 0.1% 请求出现"用户数据错乱"：请求用户是 A，结果写了 B 的订单
A：
  1. Arthas trace 全链路 + watch UserContext.get '{returnObj}'
     发现错乱请求都发生在 Tomcat http-nio-8080-exec-XX 同一个线程上，线程号重复利用
  2. Review 代码：
     public class AuthInterceptor implements HandlerInterceptor {
         preHandle 里 UserContext.set(userInfo);
         postHandle 里 // 什么都没做 ❌
         // afterCompletion 也没有 remove() ❌
     }
  3. 解释：Tomcat 线程池，exec-1 线程先跑用户 A → ThreadLocal 存 A，A 请求结束，
     exec-1 还给池子没销毁；下一个分配给用户 B → 如果 B 没登录，preHandle 不 set，
     Service.get() 直接拿到 exec-1 里**残留的 A 的 ThreadLocal** → 越权！
  4. 修复：
     afterCompletion 一定 UserContext.clear() → remove()
     另外在 UserContext.get() 里如果取不到直接抛异常（防开发忘记 set），避免 silent failure
R：
  错乱 0.1% → 0
  另外加了 2 个 defense：
  ① @RestControllerAdvice 里 finally 兜底 remove
  ② 自定义 ThreadFactory 包装：每个 Runnable 跑完之后自动 clear 所有 ThreadLocal（阿里 transmittable-thread-local TTL 库更通用）
```

**Q2：父子线程怎么传 ThreadLocal？**

```
InheritableThreadLocal：
  - Thread 类还有 inheritableThreadLocals（也是 ThreadLocalMap）
  - new Thread() 时：
    parent = currentThread
    if (parent.inheritableThreadLocals != null)
        this.inheritableThreadLocals = createInheritedMap(parent.inheritableThreadLocals)
  → ★ 一次性在子线程创建时拷贝，父线程之后 set 子线程看不到；子线程 set 也不会回传父线程

⚠️ 线程池里 InheritableThreadLocal 有坑！
  Executor.execute() 时 Worker 线程已经创建好了，不会再 new Thread() → 没法 inherit
  ✅ 生产上建议：阿里 TransmittableThreadLocal (TTL)
    TtlCallable / TtlRunnable 包装 → 提交时捕获，执行时 replay，结束后 restore
```

**项目案例 6：异步线程池丢链路 TraceId 导致排查困难**

```
S：订单服务 createOrder 同步 + 异步发短信，AsyncConfiguration 用 @Async
T：日志 grep TraceId 只查到同步部分，异步线程日志里 MDC.get("traceId") = null
A：
  1. AsyncConfig 默认 SimpleAsyncTaskExecutor：没继承 TraceId
  2. 尝试用 InheritableThreadLocal 包装 MDC → 线程复用后只在创建时 copy，后续任务拿到旧的
  3. 换成 TTL：
     a) 依赖 com.alibaba:transmittable-thread-local
     b) 自定义 ThreadPoolTaskExecutor：
        threadPoolTaskExecutor.setTaskDecorator(runnable -> {
            Map<String, String> ctx = MDC.getCopyOfContextMap();
            return () -> {
                try {
                    if (ctx != null) MDC.setContextMap(ctx);
                    runnable.run();
                } finally { MDC.clear(); }
            };
        });
R：
  异步日志全部能通过同一个 traceId 串起来
  问题排查时间从平均 35min → 5min
  另外 3 个内部系统都用了这个 TaskDecorator，统一推广
```

---

### 1.1.5 ThreadPoolExecutor 七大参数 + 执行流程源码

**Q1：七大参数 + execute() 4 步源码？**

```java
public ThreadPoolExecutor(
  int corePoolSize,                    // ① 核心线程（长期保留，allowCoreThreadTimeOut=true 可回收）
  int maximumPoolSize,                 // ② 最大线程（核心 + 非核心上限）
  long keepAliveTime, TimeUnit unit,   // ③ 非核心线程空闲多久回收
  BlockingQueue<Runnable> workQueue,   // ④ 等待队列：有界（推荐）/ 无界 / 同步移交
  ThreadFactory threadFactory,         // ⑤ 线程工厂（必须自定义命名 + 是否 daemon）
  RejectedExecutionHandler handler     // ⑥ 拒绝策略 4 种
) {}

// execute() 三步 ctl（高三位 state | 低 29 位 workerCount）
//   RUNNING    111  接受新任务 + 处理队列
//   SHUTDOWN   000  不接受新 + 处理队列
//   STOP       001  不接受 + 不处理队列 + 中断运行中
//   TIDYING    010  任务清空 → terminated()
//   TERMINATED 011  terminated() 完成
public void execute(Runnable command) {
    int c = ctl.get();
    if (workerCountOf(c) < corePoolSize) {                    // ① < core → 新建核心
        if (addWorker(command, true)) return;
        c = ctl.get();
    }
    if (isRunning(c) && workQueue.offer(command)) {          // ② 入队
        int recheck = ctl.get();
        if (! isRunning(recheck) && remove(command))         // 状态变了 → 回滚 + 拒绝
            reject(command);
        else if (workerCountOf(recheck) == 0)                // 极端：所有 worker 死了 → 补一个
            addWorker(null, false);
    }
    else if (!addWorker(command, false))                     // ③ 队列满 → 新建非核心
        reject(command);                                     // ④ 也满 → 拒绝
}
```

**Q2：`addWorker` 和 `Worker` 类的核心作用？**

```
Worker extends AQS implements Runnable：
  ① AQS 用来控制 runWorker 的独占（不是重入锁）
  ② thread 是 Worker 自己持有的线程（ThreadFactory.newThread(Worker.this)）
  ③ firstTask 是第一个任务（避免入队就立即启动就出队）
  ④ completedTasks：个人完成任务计数（shutdown 统计用）

runWorker(Worker w) 循环：
  while ((task = getTask()) != null) { ... }
  正常跳出（getTask 返回 null，因为超时 / 线程池停了）→ processWorkerExit

getTask() 4 个返回 null 场景（worker 销毁）：
  ① rs >= STOP + SHUTDOWN 且 queue 空
  ② poolSize > maxPoolSize（外部 setMaximumPoolSize 调小了）
  ③ timed && timedOut（非核心 or allowCoreTimeOut + keepAliveTime 超时 poll）
  ④ ④ workQueue.poll(keepAliveTime) 超时没拿到任务
```

**项目案例 7：Executors.newFixedThreadPool 导致 OOM，替换为自定义池 + 监控**

```
S：订单导出服务，大量异步导出任务
T：大促期间 2 次 OOM，日志显示 java.lang.OutOfMemoryError: GC overhead limit exceeded
A：
  1. HeapDump → MAT → 2.3GB LinkedBlockingQueue 的 Node 节点
     原来 Executors.newFixedThreadPool(10)：队列是 Integer.MAX_VALUE，任务 18w 没消费
  2. 线程名 pool-N-thread-M，无法定位业务，监控只有线程池对象无 activeCount/queueSize
  3. 重建：
     ThreadPoolExecutor exportPool = new ThreadPoolExecutor(
       8, 16, 60, SECONDS,
       new ArrayBlockingQueue<>(500),                          // 有界！
       new ThreadFactoryBuilder().setNameFormat("export-pool-%d").setDaemon(false).build(),
       new ThreadPoolExecutor.CallerRunsPolicy());             // 降级：HTTP 线程自己跑，自然背压
  4. 加 Micrometer：
     meterRegistry.gauge("export.pool.queue", exportPool, p -> p.getQueue().size());
     meterRegistry.gauge("export.pool.active", exportPool, p -> p.getActiveCount());
     meterRegistry.gauge("export.pool.reject", rejectCount);
  5. Grafana 告警：queue>400（80%）告警 → 扩容或降级
R：
  OOM 0 次；大促 8w 导出任务 0 丢失
  CallerRunsPolicy 效果：queue 满了 HTTP 调用方自己跑 → RT 升高但没有丢
  其他 6 个业务池统一改造，全公司没有再出现线程池型 OOM
```

---

（以下内容继续扩写 1.2 JVM → 1.3 Spring → 1.4 分布式 → 1.5 MySQL → 1.6 中间件，见 Part2）


## 1.2 JVM：从原理到调优实战

### 1.2.1 运行时数据区 + 对象创建过程

**Q1：JDK 8 内存模型分区 + 各部分 OOM 条件？**

```
线程私有：
  ① PC 寄存器：线程数多不 OOM。唯一无 OOM
  ② 虚拟机栈：
     - 递归无出口：StackOverflowError
     - -Xss512k 太小：同样递归深度更小
     - 扩展栈时内存不足：OutOfMemoryError: unable to create new native thread（线程数过多）
  ③ 本地方法栈：JNI 调用，StackOverflowError / OOM same as VM Stack

线程共享：
  ④ 堆：新生代 (Eden:S0:S1=8:1:1) + 老年代
     OOM: Java heap space → 常见：HashMap 无限增长，一次查 500 万行无分页
     调参: -Xms4g -Xmx4g (equal=禁用动态扩展)
  ⑤ 方法区 = 元空间（Metaspace，Native Memory）
     JDK 8 默认 MaxMetaspaceSize = unlimited（物理内存限制）→ 一定要配上限！
     -XX:MaxMetaspaceSize=512m（否则 CGLIB/SPI 动态生成类多了吃爆物理机）
     OOM: Metaspace
  ⑥ 运行时常量池 → JDK 7 开始从方法区移到堆（String.intern()），JDK 8 same in heap
  ⑦ 直接内存（NIO DirectByteBuffer）：-XX:MaxDirectMemorySize
     OOM: Direct buffer memory → 常见 Netty 应用，用 Cleaner 的虚引用 + ReferenceQueue 释放
```

**Q2：对象 5 步创建过程（按 HotSpot 源码顺序）**

```
① 类加载检查：
  解析常量池符号引用 → 类已加载/验证/准备/解析？
  没有 → 执行双亲委派 ClassLoader.loadClass

② 分配内存（2 种方式 + TLAB）：
  内存规整（Serial/ParNew + 标记整理/复制）→ 指针碰撞 Bump the Pointer:
    加锁：CAS + 失败重试；或每个线程预分配 TLAB（Thread Local Allocation Buffer），
    TLAB 满了再重新分配 TLAB，使用 CAS
  内存碎片（CMS + 标记清除）→ 空闲列表 Free List:
    维护可用块链表，找足够大的切块，更新链表

③ 初始化零值：
  int=0, long=0, boolean=false, reference=null
  对象字段在这步就有默认值了

④ 设置对象头（Mark Word + Klass Word + 可选数组长度）：
  Mark Word: hashcode(0, 延迟计算第一次hashCode才写入) / GC age(0) / biased_lock(1 or 0) / lock(01)
  Klass Word: 指向 Metaspace 中类元数据 InstanceKlass*
  数组长度: 数组对象额外 4 bytes

⑤ 执行 <init> 方法：构造函数 + 字段赋值 + 非 static 代码块
  由 <clinit>（类初始化，static 变量和 static{}）与 <init>（实例构造）区别
```

**项目案例 8：一次 Full GC 引发的事故——直接内存泄漏排查**

```
S：API 网关，Netty 作为 HTTP server，堆 4G，运行正常 3 个月
T：某天运维突然告警机器 Swap 80%，SSH 连不上，重启后 20 天又复现
A：
  1. top: RES 12.6G（-Xmx4g 但实际 12.6G → 堆外泄漏！）
  2. pmap -x <pid> | sort -k3 -n -r | head -20 → 多段 64MB 对齐的大匿名映射（典型 DirectByteBuffer）
  3. Arthas vmtool --action getInstances --className java.nio.DirectByteBuffer --limit 10
     → instances 有 8w+，sum(capacity) ≈ 7.5GB
  4. Reference: java.lang.ref.Cleaner 负责释放（PhantomReference + ReferenceQueue）
     检查 ReferenceHandler 线程：多次 jstack 没有 BLOCKED
     → Cleaner 正常工作 → 为什么没释放？
     用 gcore + MAT：多数 DirectByteBuffer 还被业务 HandlerContext 引用
  5. 代码审查：
     CompletableFuture.supplyAsync(() -> rpc.call(xx), businessExecutor)
       .whenCompleteAsync((r,e) -> ctx.writeAndFlush(response))  // ❌ 没指定 Executor
       // 默认走 ForkJoinPool.commonPool()，commonPool 线程不会退出
       // 但 ctx 被 Netty NIO Worker 持有 → 循环引用
  6. 修复：whenCompleteAsync(..., businessExecutor) 指定同一个
R：
  修复前 20 天 RSS 涨到 12.6G；修复后稳定 5.2G（堆 4G + 元空间/代码缓存/堆外 1.2G）
  另加：-XX:MaxDirectMemorySize=1g + Micrometer gauge BufferPoolMXBean "direct" used → 超 80% 告警
```

---

### 1.2.2 垃圾回收：算法 + 收集器（CMS/G1/ZGC 对比）+ 调优案例

**Q1：CMS/G1/ZGC 三款收集器核心流程对比 + 适用场景？**

| | CMS（JDK 5-8 低延迟先锋） | G1（JDK 9 默认，面向大堆） | ZGC（JDK 15 正式，亚毫秒级） |
|---|---|---|---|
| 分区 | 物理分代（新/老两块连续） | 物理 Region（1~32MB，2048 个），逻辑分代 | 物理 Region，可变 2MB~32MB，不分代 |
| 算法 | 老年代并发标记-清除 | 全 Region：复制算法（humongous 超大对象单独） | 全 Region：复制 + Load Barrier 着色指针 |
| 最大停顿 | Full GC 退化 Serial Old → 秒级 | MaxGCPauseMillis 默认 200ms，目标预测 | 10ms 级 STW（标记开始/结束 + 重映射），不随堆和对象数增长 |
| 核心步骤 | ① 初始标记 STW ② 并发标记 ③ 重新标记 STW（增量） ④ 并发清除 | ① 初始标记 STW ② 并发标记 ③ 最终标记 STW ④ 筛选回收 STW（按收益排序 Region） | ① 开始标记 STW ② 并发标记 ③ 结束标记 STW ④ 并发 PrepareRelocate ⑤ 并发转移（内存就地复制，读屏障自愈） |
| 缺点 | 标记清除碎片→ Full GC；浮动垃圾无法回收；并发占用 (NCPU+3)/4 | 记忆集 Remembered Set 维护重；G1 自己也吃 5~10% 内存 | 读屏障 + 着色指针 3~5% overhead；JDK 15+ 才正式 |
| 适用 | JDK 8 Web 应用 4~8G 堆，RT P99 < 300ms | 8G+ 大堆，RT 目标可预测 200ms | 大堆 32G+，超低延迟（交易/支付/游戏） |

**Q2：G1 为什么能做到"可预测停顿"？**

```
核心机制——Region 分区 + 预测模型 + 收益优先回收：
  ① Region 大小 2^n，最大 2048 块（老年代/新生代/大对象 Humongous 混存，逻辑分代）
  ② Remembered Set（RSet）：每个 Region 有一个 HashTable 记录"谁引用了我（反向指针）"，避免全堆扫描
  ③ CSet（Collection Set）：每次回收选哪些 Region？
     G1 可预测停顿模型：
     ① 历史数据记录每个 Region 回收耗时 T，回收对象大小 D
     ② pause_goal = MaxGCPauseMillis（默认 200ms）
     ③ Greedy 算法依次挑 Region：按 D/T（"收益比"）排序
     ④ 累加 ΣT ≤ pause_goal 就停 → 选出来 CSet 复制回收
```

**项目案例 9：CMS 频繁 Full GC → G1 调优前后对比（完整参数清单 + 指标）**

```
S：订单服务 8 核 16G，堆 8G，CMS，RT P99 400ms
T：618 压测 CMS Old 90% 触发 ConcurrentMark → concurrent mode failure（分配速度 > 回收）→ Fallback Serial Old 单线程 Full GC → STW 6.8s → 超时 300+ 笔
A：
  1. 原参数（坑）：
     -Xms8g -Xmx8g -XX:+UseConcMarkSweepGC -XX:+UseCMSCompactAtFullCollection
     -XX:CMSInitiatingOccupancyFraction=80（太保守反而触发频繁 CMS）
     没配 MaxMetaspaceSize，PermGen 元空间 420MB 已经占 410MB 快 OOM
  2. 新 G1 参数：
     -Xms8g -Xmx8g
     -XX:+UseG1GC -XX:MaxGCPauseMillis=200
     -XX:G1HeapRegionSize=16m                // 8G/2048=4MB 偏小，16MB 让 Humongous 少（>50% Region 才算）
     -XX:MetaspaceSize=512m -XX:MaxMetaspaceSize=1024m   // 防元空间 Full GC 触发
     -XX:InitiatingHeapOccupancyPercent=45   // IHOP 45% 开始并发标记（默认 45，堆大的话调）
     -XX:+ParallelRefProcEnabled             // 并行引用处理（soft/weak 等）
     -XX:+UnlockExperimentalVMOptions -XX:G1MixedGCLiveThresholdPercent=60
     -XX:G1MixedGCCountTarget=16
  3. 代码层面：
     a) 批量导出逻辑改流式，减少 400MB+ 大对象（直接触发 Humongous，难回收）
     b) 订单 DO → DTO 映射替换：Dozer → MapStruct（ASM 字节码生成，反射对象少）
R：
  3 天压测对比：
  指标          旧 CMS       新 G1
  Young GC 次   321          298
  Young GC avg  40ms         28ms
  Full GC 次    4 次         0 次
  RT P99        400ms        195ms
  超时订单      300+         0
  Humongous Obj 18%          3%
  最终 618 当天零 Full GC，2 倍目标 QPS 稳过
```

---

### 1.2.3 类加载 + 双亲委派 + 打破场景

**Q1：3 种类加载器 + 双亲委派执行流程（ClassLoader.loadClass 源码）？**

```
3 层 Bootstrap（非 ClassLoader 子类，native）→ Platform（Ext 改名 JDK 9+）→ Application

protected Class<?> loadClass(String name, boolean resolve) {
    synchronized (getClassLoadingLock(name)) {
        Class<?> c = findLoadedClass(name);          // ① findLoadedClass0 查缓存
        if (c == null) {
            try {
                if (parent != null) {
                    c = parent.loadClass(name, false); // ② 向上委派 parent
                } else {
                    c = findBootstrapClassOrNull(name); // ③ parent 是 null → Bootstrap
                }
            } catch (ClassNotFoundException ignore) {}
            if (c == null) {
                c = findClass(name);                  // ④ 上层找不到 → 自己 findClass
            }
        }
        if (resolve) resolveClass(c);                 // ⑤ 链接阶段
        return c;
    }
}
好处：① 沙箱安全（java.lang.String 只能 Bootstrap 加载）② 避免重复加载
```

**Q2：4 种打破双亲委派的真实场景 + 每一种如何打破？**

```
打破方式①：自定义 ClassLoader 重写 loadClass()
  Tomcat WebAppClassLoader：
    ① 先自己加载本地 WEB-INF/classes, WEB-INF/lib
    ② 找不到 → 委派 parent（Common/Shared → Bootstrap/Platform/App）
    → 目的：war 包隔离，A.war logback v1.2, B.war logback v1.3 互不影响
  代码：重写 loadClass()，如果不是 java.* / javax.* 包，就先自己 findClass()；失败再委派

打破方式②：SPI + Thread Context ClassLoader（TCCL）
  java.sql.DriverManager（Bootstrap 加载的类）要 load 厂商驱动（classpath 下）
  Bootstrap 找不到 classpath 的类 → 打破双亲
  解决：DriverManager.getConnection() 会
    ClassLoader cl = Thread.currentThread().getContextClassLoader();
    Class.forName(driverClass, true, cl);  // 用 Application CL 去加载

打破方式③：OSGi 模块化
  每个 Bundle 独立 ClassLoader，互相 Import-Package / Export-Package
  形成网状委派（非树状），Bundle 更新热替换

打破方式④：热部署 class，自定义 findClass 不缓存
  如 JRebel：instrument agent + ByteBuddy 字节码增强
```

**项目案例 10：CGLIB 代理类打爆元空间——Spring @Transactional 过多接口导致**

```
S：老系统 4700+ DAO，Spring 事务，启动 -XX:MaxMetaspaceSize=256m
T：启动到 3800 个 DAO OOM: Metaspace
A：
  1. jcmd <pid> VM.metaspace → Klass Metaspace 241MB，其中 182MB 是 CGLIB 动态类
     Spring 在 Bean 初始化阶段为每个 DAO 创建 CGLIB 代理
     一个 DAO 默认有 14 个 Method → FastClass 为每个方法生成 index 跳转
     一个 DAO 实际产生 3~4 个 CGLIB 类
  2. 计算：4700 × 3 = 14100 类，每个约 12~15KB → 200MB → 256MB 不够
  3. 优化：
     a) 改为 JDK 动态代理（DAO 都有接口），开启
        @EnableTransactionManagement(proxyTargetClass = false)  // 默认 JDK 代理
        JDK 代理一个接口只生成 1 个 $Proxy 类（按接口缓存，相同接口只 1 个）
     b) 扩大 MaxMetaspaceSize=512m，预防未来 2 倍增长
R：
  启动后 Metaspace 占用：241MB → 78MB（减少 67%）
  启动时间：42 秒 → 26 秒
```

---

## 1.3 Spring：核心流程源码级掌握

### 1.3.1 IOC 容器核心：refresh() 12 步源码

```java
// org.springframework.context.support.AbstractApplicationContext.refresh()
public void refresh() throws BeansException, IllegalStateException {
    synchronized (this.startupShutdownMonitor) {
        // ① prepareRefresh：前戏：initPropertySources（留给子类扩展，替换 ServletContext 占位符）+ earlyApplicationListeners
        prepareRefresh();
        // ② obtainFreshBeanFactory()：
        //    XML 场景：XmlBeanDefinitionReader 读 XML，生成 RootBeanDefinition(bdMap)
        //    注解场景：ConfigurationClassPostProcessor 解析 @Configuration/@ComponentScan → 扫包 register bd
        ConfigurableListableBeanFactory beanFactory = obtainFreshBeanFactory();
        // ③ prepareBeanFactory：BeanFactory 补标准组件
        //    - beanClassLoader / spel ExpressionParser
        //    - 加 3 个 BeanPostProcessor：ApplicationContextAwareProcessor, ApplicationListenerDetector
        //    - 忽略 Aware 接口的依赖注入
        //    - 注册 3 个内置单例：environment/systemProperties/systemEnvironment
        prepareBeanFactory(beanFactory);
        try {
            // ④ postProcessBeanFactory：子类扩展点（WebApplicationContext 加 ServletContextAwareProcessor / 注册 scope: request/session）
            postProcessBeanFactory(beanFactory);
            // ⑤ invokeBeanFactoryPostProcessors：★★★ 执行 BFPP / BDRPP
            //    PriorityOrdered.class -> Ordered.class -> 无排序 -> 递归（新扫出来的 @Configuration）
            //    ConfigurationClassPostProcessor 这一步扫 @ComponentScan/@Bean/@Import
            invokeBeanFactoryPostProcessors(beanFactory);
            // ⑥ registerBeanPostProcessors：★★★ 实例化并注册所有 BPP
            //    PriorityOrdered -> Ordered -> non-ordered -> 最后 BeanPostProcessorChecker（日志检测未完全初始化）
            //    重点：ImportAwareBeanPostProcessor, AutowiredAnnotationBeanPostProcessor, CommonAnnotationBeanPostProcessor, AspectJAwareAdvisorAutoProxyCreator（AOP）
            registerBeanPostProcessors(beanFactory);
            // ⑦ initMessageSource：国际化
            initMessageSource();
            // ⑧ initApplicationEventMulticaster：事件广播器
            initApplicationEventMulticaster();
            // ⑨ onRefresh：子类扩展，Spring Boot 创建 Tomcat 就在这步 ServletWebServerApplicationContext.createWebServer()
            onRefresh();
            // ⑩ registerListeners：注册 ApplicationListener bean，发布早期事件
            registerListeners();
            // ⑪ finishBeanFactoryInitialization：★★★ 核心！实例化所有非 lazy-init 单例 Bean
            //    beanFactory.preInstantiateSingletons()
            //    遍历 beanDefinitionNames -> getBean(beanName) -> doCreateBean
            //    createBeanInstance（构造） -> populateBean（属性注入）-> initializeBean（Aware + BPP Before/After, @PostConstruct, init-method）
            finishBeanFactoryInitialization(beanFactory);
            // ⑫ finishRefresh：
            //    LifecycleProcessor, ContextRefreshedEvent, Live Beans View, 启动 JMX Endpoint
            finishRefresh();
        } catch (BeansException ex) {
            destroyBeans();    // 异常销毁
            throw ex;
        } finally {
            resetCommonCaches(); // 清理反射缓存
        }
    }
}
```

**追问：beanFactory.preInstantiateSingletons 如何保证单例不重复？**
→ DefaultSingletonBeanRegistry.getSingleton(beanName, ObjectFactory)：
  1. 先查 singletonObjects（一级缓存）
  2. 没查到 → 加 singletonObjects 互斥锁
  3. 再查 singletonObjects → 还没 → 调用 ObjectFactory.getObject() → createBean()
  4. addSingleton 放 singletonObjects（一级），从二级三级 remove

**项目案例 11：Spring Boot 启动慢——BFPP 顺序错误导致重复扫描 3 次**

```
S：公司架构组包 3 + 业务包，Spring Boot 启动 82 秒（4C 8G 机器）
T：要求 ≤ 30 秒
A：
  1. 启动参数加 -Dlogging.level.org.springframework=DEBUG -Dspring.application.admin.enabled=true
     + 火焰图：耗时前两位
     a) ConfigurationClassPostProcessor.parse 3 次
     b) JdkDynamicAopProxy.getProxy 被调 2100 次（实际 Bean 680）
  2. 原因分析：
     a) 业务 3 个自定义 @Configuration 都写了@ComponentScan("com.company")
        -> invokeBeanFactoryPostProcessors 中每个 @Configuration 都是一个新的 ConfigClass，递归 parse
     b) 自定义一个 BeanFactoryPostProcessor 里手动 new AnnotationConfigApplicationContext 又扫一次
     → bd 数量 680，但 parse 工作 3 遍
     c) AOP：global-logging-starter 写了 @Pointcut("execution(* com.company..*.*(..))")，
        每个 680 Bean 的所有 12 method 都过 canApply 匹配（680×12=8160 次 method 匹配）
  3. 修复：
     a) 留根目录一个启动类 @SpringBootApplication(scanBasePackages = "com.company")，其他 @Configuration 去掉 scan，拆出多个 AutoConfiguration + @ConditionalOnClass
     b) 自定义 BFPP 用已经创建好的 beanFactory，不要再 new ApplicationContext
     c) AOP 切点缩窄：@Pointcut("@within(com.company.log.annotation.Log) || @annotation(Log)")
        改成 annotation match（method.getAnnotation 一次，正则匹配 O(1) vs execution *.*(..) 每次要解析 aspectj weaver AST）
R：
  启动 82 秒 → 21 秒，节省 74%
  BD 注册：重复 2000+ → 去重后 680
  AOP 匹配：8160 → 1400
  后来推广：全公司 12 个 Spring Boot 服务平均启动时间减少 60%+
```

---

### 1.3.2 Bean 生命周期 + 扩展点时序 11 步

```
完整 11 步（按时间顺序）：
1. createBeanInstance          // 实例化：构造函数 / Supplier / CGLIB / factory-method
2. MergedBeanDefinitionPostProcessor.postProcessMergedBeanDefinition   // 例如 @Autowired/@Value 元数据提前查找缓存，CommonAnnotationBeanPostProcessor 找 @Resource
3. SmartInstantiationAwareBeanPostProcessor.getEarlyBeanReference  // ★ 循环依赖时通过 ObjectFactory 提前暴露引用（A 早期代理）
4. populateBean              // 属性注入
     → InstantiationAwareBeanPostProcessor.postProcessAfterInstantiation
     → InstantiationAwareBeanPostProcessor.postProcessProperties     // AutowiredAnnotationBeanPostProcessor：反射字段注入
5. 各种 Aware 回调（BeanNameAware / BeanClassLoaderAware / BeanFactoryAware / EnvironmentAware / EmbeddedValueResolverAware / ApplicationContextAware）顺序依次
6. BeanPostProcessor.postProcessBeforeInitialization  // ★ @PostConstruct (CommonAnnotationBeanPostProcessor) 在这里
7. afterPropertiesSet()         // InitializingBean 接口
8. <init-method>                // @Bean(initMethod = "xx") 或 XML init-method
9. BeanPostProcessor.postProcessAfterInitialization   // ★ AOP 代理（AnnotationAwareAspectJAutoProxyCreator.wrapIfNecessary()）在这里
10. Bean 使用（业务方法调用）
11. DisposableBean.destroy() + @PreDestroy + <destroy-method>

注意：
- @PostConstruct（JSR-250）→ before afterPropertiesSet（Spring）→ before init-method（XML）
- 销毁顺序：@PreDestroy → DisposableBean.destroy → destroy-method
```

**项目案例 12：@PostConstruct + Feign 调用启动失败——怎么让远程调用晚一点？**

```
S：库存服务启动要从配置中心拉一份白名单，@PostConstruct 里用 Feign 调配置中心 API
T：启动失败：LoadBalancerClient not initialized yet（Nacos 还没 register）
A：
  1. 原因时序：
     refresh() 第 11 步 finishBeanFactoryInitialization 开始实例化 Bean，
     此时 Nacos ServiceRegistry 还没到 SmartLifecycle.start 阶段（finishRefresh 最后）
  2. 3 种方案对比：
     ① SmartLifecycle 接口：start() 回调在 finishRefresh 的 getLifecycleProcessor().onRefresh() → 所有 Bean 初始化完才调用
     ② @EventListener(ContextRefreshedEvent.class)：事件发布在 finishRefresh()，此时容器完全初始化
     ③ ApplicationRunner / CommandLineRunner：Spring Boot 的启动最后一步
  3. 我们最终选方案①：因为还要控制启动顺序和 isRunning 状态
R：
  @Component
  public class ConfigLoader implements SmartLifecycle {
      private volatile boolean running;
      @Override public void start() {
          whitelist = configFeignClient.fetchAll();    // Nacos 已初始化，OK
          running = true;
      }
      @Override public int getPhase() { return Integer.MAX_VALUE - 1; }  // 最后启动
  }
  稳定运行 0 启动失败
```

---

### 1.3.3 循环依赖：三级缓存 + earlySingletonObjects 作用

```
三级缓存定义 DefaultSingletonBeanRegistry：
  private final Map<String, Object> singletonObjects = new ConcurrentHashMap<>(256);  // 一级：完整 Bean
  private final Map<String, Object> earlySingletonObjects = new HashMap<>(16);        // 二级：半初始化 Bean
  private final Map<String, ObjectFactory<?>> singletonFactories = new HashMap<>(16);  // 三级：ObjectFactory Lambda

A 依赖 B，B 依赖 A，加 @Transactional 需要 AOP 代理的流程：
  1. doGetBean("a") → createBean("a") → createBeanInstance(a)（实例化 A，空属性）
     → addSingletonFactory("a", getEarlyBeanReference("a", bd, beanA))
       singletonFactories.put("a", () -> 
           applyBeanPostProcessorsBeforeInstantiation(beanA, "a")  // ★ 如果需要代理就返回 proxy
       );  // ★ populate 前就放三级缓存

  2. populateBean(a)：@Autowired B → doGetBean("b") → createBean("b") → put 三级
  3. populateBean(b)：@Autowired A → doGetBean("a")
     → getSingleton("a", allowEarlyReference=true)
       ① singletonObjects.get("a") null
       ② earlySingletonObjects.get("a") null
       ③ singletonFactories.get("a").getObject() → Lambda 执行：
         ★ AbstractAutoProxyCreator.getEarlyBeanReference：提前创建代理 proxyA ★
         → earlySingletonObjects.put("a", proxyA)，singletonFactories remove
  4. B 拿到的是 proxyA（早期代理），B.initializeBean + put singletonObjects("b")
  5. A 继续 initializeBean，走到 BPP postProcessAfterInitialization（AOP 再进来）：
     wrapIfNecessary(beanA, "a")：发现 earlyProxyReferences 已经缓存过 proxyA（getEarlyBeanReference 时塞的）
     → 不再重复 wrap，直接返回原 beanA？
     ★ No！exposedObject = proxyA！
     -> 因为：AbstractAutoProxyCreator.postProcessAfterInitialization：
        if (this.earlyProxyReferences.remove(cacheKey) != bean) return wrapIfNecessary(...)
        如果能从 earlyProxyReferences 拿到且 == bean → 说明已经 getEarlyBeanReference 代理了 → 直接 return bean（不重复代理）
     → 但实际返回的是 initializeBean 返回的 exposedObject 吗？
        不！Spring 在 doCreateBean 末尾有一段：
        if (earlySingletonExposure) {
          Object earlySingletonReference = getSingleton(beanName, false);  // false 不从三级取
          if (earlySingletonReference != null) {
            if (exposedObject == bean) exposedObject = earlySingletonReference;  // ★ 把 early proxy 替换出去
          }
        }
  6. addSingleton("a", proxyA)
```

**高频追问：为什么要 3 级？2 级（去掉 singletonFactories）行不行？**

→ 不行。核心：没有 AOP 的简单场景是可以；但有 AOP 时，一个 Bean 在 AOP 之前如果没经过 ObjectFactory，只能塞普通对象。但循环依赖的另一方拿到的应当是"代理后的对象"。
→ singletonFactories 的 Lambda 就是"如果用户真的引用了我（B 引用 A），我就立即创建 A 的代理"（懒汉式），而不是一开始就 eager 创建。
→ earlySingletonObjects 的作用：singletonFactories 里的 Lambda 只要被调用了就把结果放二级，下次直接拿，避免多次调用 `applyBeanPostProcessorsBeforeInstantiation`（重复代理）。

---

### 1.3.4 AOP 代理 + @Transactional 事务 7 大失效场景

**@Transactional 7 大失效场景（每个必记 + 踩坑案例）**

```
失效①：方法非 public
  原因：AbstractFallbackTransactionAttributeSource.getTransactionAttribute
    if (allowPublicMethodsOnly() && !Modifier.isPublic(method.getModifiers())) return null;
    CGLIB 虽然也能代理 protected/private，但 Spring 选择了统一拦截 public。
  修复：改 public；或 @EnableTransactionManagement(proxyTargetClass=true, mode=AdviceMode.ASPECTJ) 字节码织入

失效②：同类互调 this.method()，不走代理
  // ❌
  @Service public class OrderService {
      public void create() { this.insertOrder(); }  // this 直接调用目标对象，不经过 proxy
      @Transactional public void insertOrder() { ... }
  }
  修复3种：
    a) 注入自己 @Autowired OrderService self; self.insertOrder();
    b) AopContext.currentProxy() → ((OrderService)AopContext.currentProxy()).insertOrder()，@EnableAspectJAutoProxy(exposeProxy = true)
    c) 抽出去：新建 InsertOrderService，OrderService 注入它

失效③：异常类型不对，默认 rollbackFor = RuntimeException.class
  @Transactional 默认：
    rollbackFor = { RuntimeException.class, Error.class }
    业务抛 IOException / SQLException（Checked）→ 不回滚！
  修复：@Transactional(rollbackFor = Exception.class) （最佳实践统一标配）

失效④：自己 try-catch 吞了异常
  try { orderMapper.insert(o); pointMapper.add(u, 100); } 
  catch (Exception e) { log.error("e", e); }  // 异常没抛出 → 切面 catch 不到 → commit
  修复：catch 最后再 throw e；或 TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();

失效⑤：非事务方法调事务方法 + 类内部代理
  同失效②，this 互调；或事务方法 private

失效⑥：数据库引擎不支持事务
  MySQL MyISAM → 建表 ENGINE=InnoDB

失效⑦：propagation 配置错误
  REQUIRES_NEW：挂起外层，新事务独立提交；外层失败内层已提交
  NOT_SUPPORTED：外层事务挂起，以非事务运行；中间插入 DB 不回滚
```

**项目案例 13：失效场景②+④ 组合事故——积分发放 catch 后订单还在**

```
S：下单 + 扣库存 + 发积分（积分服务远程 HTTP 调用）
T：日志显示积分服务超时 → 积分没发 → 但订单还在 DB，库存扣了
A：
  1. Review 代码：
     @Transactional
     public void createOrder(OrderDTO dto) {
         try {
             orderMapper.insert(order);
             productMapper.deductStock(productId, qty);
             pointHttpClient.add(userId, 100);   // 积分 HTTP，可能 IOException
         } catch (Exception e) {
             log.error("create failed", e);       // ❌ 吞了！
             // ❌ 没 throw；也没 setRollbackOnly
         }
     }
     // ① catch 吞异常（失效④）
     // ② 另外：pointHttpClient.add 抛 ConnectException（Checked）→ 默认 @Transactional 默认不 rollback
  2. 修复：
     a) catch 后 throw new BizException("POINT_ERROR", e);
     b) @Transactional(rollbackFor = Exception.class)
     c) 架构上：积分发 MQ 异步，本地消息表同一本地事务保证最终一致性
R：
  事故前：每月 3~5 次不一致，运营手工补单 2h
  事故后：0 次不一致；MQ 异步峰值下单 RT 300ms → 150ms
```

---

### 1.3.5 Spring Boot 自动装配流程 + 自定义 Starter 完整步骤

```
SpringFactoriesLoader 流程：
  @SpringBootApplication → @EnableAutoConfiguration
    → @Import(AutoConfigurationImportSelector.class)
    → selectImports(AnnotationMetadata)
      ① getAutoConfigurationEntry(annotationMetadata)
      ② getCandidateConfigurations()：
        SpringFactoriesLoader.loadFactoryNames(EnableAutoConfiguration.class, classLoader)
        → 读所有 META-INF/spring.factories
        key = org.springframework.boot.autoconfigure.EnableAutoConfiguration
        value = 127 个配置类（spring-boot-autoconfigure 包自带）
      ③ removeDuplicates + getExclusions（exclude/excludeName）
      ④ filter()：onClassCondition/@ConditionalOnClass + onBeanCondition/@ConditionalOnMissingBean + OnPropertyCondition/@ConditionalOnProperty
      ⑤ 最终剩下真正生效的 30~60 个 AutoConfiguration
```

**项目案例 14：自研审计 Starter——公司 8 个业务线复用 3000+ 行重复代码**

```
S：每个项目 Controller 层都写一段日志 + 审计：
  log.info("{} 操作 {} param {}", userId, methodName, JSON.toJSONString(param));
  auditMapper.insert(opLog);
  8 条业务线重复写，代码 3000+ 行；写法不统一，字段 3 个版本
T：抽取审计 Starter，一行 @EnableAudit 开启
A：
  1. 新建 xxx-audit-spring-boot-starter 模块
  2. 目录：
     starter/
       autoconfigure/
         AuditAutoConfiguration.java
         AuditProperties.java             @ConfigurationProperties(prefix="audit")
           enabled: true
           module:  # 模块名 默认取 spring.application.name
           skipUrls: /actuator/**,/error
       aop/AuditAspect.java                @Around + @AuditLog annotation
       spi/AuditReporter.java              interface report(AuditEvent)
       impl/DbAuditReporter                默认 jdbc 写 audit_log
       impl/KafkaAuditReporter             可选配置 audit.reporter=kafka
       META-INF/spring.factories
         org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
           com.xxx.audit.autoconfigure.AuditAutoConfiguration
       META-INF/additional-spring-configuration-metadata.json
         IDE 自动补全 properties（可选）

  3. AuditAutoConfiguration：
     @Configuration
     @EnableConfigurationProperties(AuditProperties.class)
     @ConditionalOnClass(AuditAspect.class)
     @ConditionalOnProperty(prefix="audit", name="enabled", havingValue="true", matchIfMissing=true)
     public class AuditAutoConfiguration {
         @Bean @ConditionalOnMissingBean
         public AuditAspect auditAspect(AuditProperties p, ObjectProvider<AuditReporter> reporter) {...}
         @Bean @ConditionalOnMissingBean @ConditionalOnBean(DataSource.class)
         public AuditReporter dbAuditReporter(DataSource ds) { return new DbAuditReporter(ds); }
     }

  4. 使用方：
     <dependency> <groupId>com.xxx</groupId> <artifactId>xxx-audit-spring-boot-starter</artifactId> </dependency>
     application.yml: audit.module = order-service
     Controller 方法加 @AuditLog(action = "创建订单", biz = "#order.orderNo")
R：
  3000 行重复代码删除
  全公司审计字段统一，合规审计一次性过
  KafkaReporter 后，审计写入不影响主业务 DB，RT <1ms
```

---

## 1.4 并发编程：分布式场景

### 1.4.1 分布式锁三种实现对比（Redis/ZK/DB）+ Redisson 看门狗

| 维度 | Redis 分布式锁（Redisson RLock） | ZooKeeper 临时有序节点 | MySQL 乐观锁/悲观锁 |
|---|---|---|---|
| 原理 | SETNX + Lua + pubsub 解锁通知 + 看门狗 Watchdog | 临时有序节点 + 前缀 min 序号 | version 字段 CAS；或 SELECT ... FOR UPDATE |
| 可用性 | Redis Sentinel / Cluster 高可用 | ZAB 协议，过半即写 | DB 主从 |
| 锁释放可靠性 | ❌ 原始 SETNX key TTL 到期还没执行完就释放 → Redisson Watchdog | ✅ Session 断了临时节点自动删除 | ❌ DB 悲观锁事务回滚/提交才释放，长事务坑 |
| 阻塞等待 | 自旋 + pubsub 通知，不忙等 | Watcher 回调 | 不支持；要么 NOWAIT 报错，要么无限等 |
| 可重入 | Redisson RLock 哈希结构（threadId: count） | 线程级 ThreadLocal 记录可重入次数 | 不支持 |
| 读写锁/联锁/红锁 | Redisson 支持 RReadWriteLock / MultiLock / RedLock | 自行实现 | 不支持 |
| 生产推荐 | ✅ 首选（吞吐高 + 生态成熟） | 次选（强一致但吞吐低） | 小规模/应急场景 |

**Redisson Watchdog 续命机制（关键！）**

```
默认锁超时 30 秒（internalLockLeaseTime = 30000）
看门狗：
  如果加锁时没指定 leaseTime（-1），启动定时任务：
    new TimerTask() { 每 internalLockLeaseTime/3（10 秒）执行一次
      if (isHeldByCurrentThread()) {
          renewExpiration() → Lua: pttl + expire(key, 30s)
      } else cancel();
    }
→ 只要持有线程不断续期，锁永远不释放
→ 如果 Redisson 进程 crash：10 秒没续期，30 秒 TTL 到自动解锁
→ 必须最终一致性的支付订单场景：加 lock(10, TimeUnit.SECONDS) 手动指定 TTL，避免看门狗无限续期
```

**项目案例 15：库存扣减三方案演进（最终 Redisson RLock + Lua + DB 兜底）**

```
S：秒杀活动，商品 100 件 / 库存 10 万，QPS 目标 10000
T：
  方案① DB 乐观锁：
    UPDATE stock SET remain = remain - #{qty}, version = version + 1
    WHERE product_id = #{pid} AND version = #{v} AND remain >= #{qty}
    → 10000 QPS 时，失败率 85%（10 次重试还失败），DB CPU 100%
    → 不满足
  方案② Redis 简单 SETNX：
    SET lock:product:1001 random_value NX EX 30
    stock = GET stock:1001
    if stock>0: DECRBY stock:1001 qty → MQ异步写DB
    问题：
      a) 业务执行 40 秒（大促期间 GC），30 秒锁自动到期 → 第二个线程拿到锁 → 两人同时扣 → 超卖！
      b) 误删别人锁：A到期、B加锁（value=B_rand），A 执行完 DEL key 删掉 B 的锁
  方案③ Redisson RLock + Lua 原子预扣 + DB 兜底：
    a) RLock lock = redisson.getLock("stock:" + pid);
       lock.lock();   // 看门狗自动续期 + 重入 + pubsub 通知
    b) Redis Lua 原子扣减：
       local stock = redis.call('GET', KEYS[1])
       if (stock ~= false and tonumber(stock) >= tonumber(ARGV[1])) then
           return redis.call('DECRBY', KEYS[1], ARGV[1])
       end return -1
    c) 预扣成功 → 发 RocketMQ 事务消息 half → 本地事务（写订单）→ commit
       MQ 消费 → DB 最终扣库存
    d) DB 兜底 UPDATE stock SET remain=remain-#{qty} WHERE pid=? AND remain>=?
       （最终防线，永远不开玩笑）
R：
  QPS：9800（达标）
  超卖：0 单（压测 1 亿次模拟）
  RT P99：28ms（方案① 的 1s+ → 28ms）
  GC 长 STW 也没有超卖（Watchdog 续期）
```

---

### 1.4.2 分布式事务：2PC/TCC/Saga/本地消息表/RocketMQ 事务消息

**5 种方案对比表 + 适用场景：**

| 方案 | 一致性 | 吞吐量 | 实现复杂度 | 侵入代码 | 适用场景 |
|---|---|---|---|---|---|
| 2PC (Seata AT) | 强一致（一阶段就锁全局） | 低 | 中（需 TC/TM/RM） | 低，@GlobalTransactional | 中小规模、短事务、不允许最终一致（资金、交易） |
| TCC (Try/Confirm/Cancel) | 最终一致 | 中 | 高（每接口写 3 方法 + 空回滚/悬挂/幂等） | 高（写 Try/Confirm/Cancel 三个） | 核心交易、资源预留（余额冻结/扣减）、强业务语义 |
| Saga（正向/逆向补偿） | 最终一致 | 高 | 中（状态机 + 补偿接口） | 中（每步写 Compensate） | 长流程、多服务、参与者多（订单-库存-物流-积分），允许中间态 |
| 本地消息表 + MQ | 最终一致 | 高 | 低 | 低 | 通用解耦场景，失败重试，数据对账 |
| RocketMQ 事务消息（半消息） | 最终一致 | 高 | 低 | 中（executeLocalTransaction + check） | 已有 RocketMQ 基础设施，不想额外维护消息表 |

**TCC 三大坑（必背！）**

```
① 空回滚：Try 没收到，Cancel 先到（丢包/网络分区）
   解决：每张 TCC 事务记录表 try_state(0=INIT,1=TRY_OK,2=CONFIRM_OK,3=CANCEL_OK)
     Cancel 时发现还是 0 → 空回滚，直接标记 3，返回 OK（不执行业务）

② 幂等：Confirm/Cancel 重复调用
   解决：状态机 + DB 唯一约束（xid+branchId），重复请求直接返回成功

③ 悬挂：Try 比 Cancel 晚到（TC 先判定超时发 Cancel；之后 Try 才到达）
   解决：执行 Try 时查状态，如果 已经 CANCEL_OK(3) → 不执行业务 Try，直接返回
```

**项目案例 16：下单+库存+物流 Saga 状态机实现（3 步正向 + 3 步逆向 + 状态持久化）**

```
S：订单流程：创建订单 → 扣库存 → 生成运单；任何一步失败都要回滚前面
T：不能用强一致 2PC（跨 3 个部门微服务，对方不开放）
A：
  1. 状态机定义：
     订单状态：PENDING → STOCK_DEDUCTED → SHIPMENT_CREATED → PAID（终态）
              → FAIL_ORDER / FAIL_STOCK / FAIL_SHIPMENT（回滚中）
  2. 正向流程异步编排（CompletableFuture 链式）：
     orderService.create(dto)
       .thenCompose(o -> stockService.deduct(o))
       .thenCompose(o -> shipService.create(o))
       .exceptionally(e -> compensate(o, currentStep, e))
  3. 补偿：
     FAIL_SHIPMENT → shipCompensate.rollbackCreate() → state=FAIL_STOCK → stockCompensate.rollbackDeduct() → state=FAIL_ORDER
  4. 可靠性：
     - 每一步状态变更都带 DB 本地事务（订单状态和业务操作在同一本地事务）
     - 定时任务 OutdatedOrderRecoveryJob：每 5 分钟捞 PENDING 超过 3 分钟的订单 → 驱动补偿或重试
     - T+1 对账：order DB vs stock DB vs ship DB
R：
  数据一致性 0 人工修复（之前 15~20 单/月 → 0）
  正向流程 300ms → 180ms（异步编排 + 3 步并行 2 步）
  另外做成公司通用 Saga 编排框架：JSON DSL + 反射生成状态机，推广到 5 个业务线
```

---

### 1.4.3 RPC / Dubbo / Sentinel / SkyWalking 实战

（篇幅略，完整见合并版全文。Part2 继续）

**项目案例 17：Sentinel 热点参数限流保护秒杀商品不崩溃 + 案例 18：SkyWalking traceId 串 Kafka + 异步线程，排查慢调用（详见完整文件 Part2 1.4.3）**

---

## 1.5 MySQL：深度 + 调优实战

### 1.5.1 B+ 树索引：计算方式 + 回表 + 覆盖索引 + 最左前缀

```
InnoDB 页大小 16KB（innodb_page_size），一行指针 6B：
  ① 非叶子节点（存索引 + 指针）：
     BIGINT id = 8B + 指针 6B = 14B/项
     16KB / 14B ≈ 1170 个索引项
  ② 叶子节点（存数据行，按 id 聚簇）：
     假设每行 1KB → 16 行/页
  → 3 层 B+ 树存多少行？
     1170 × 1170 × 16 ≈ 21,902,400（约 2200 万行！3 次 I/O）
  → 4 层：1170^3 × 16 ≈ 256 亿行
  所以 1 亿行的表 id 查询也只要 3~4 次 I/O，毫秒级

最左前缀 & 范围查询截断：
  idx(a,b,c) 联合索引，B+ 树按 a 排序 → a 相同按 b → b 相同按 c
  WHERE a=1 AND b>2 AND c=3    → a,b 用得上，c 用不上（b 是范围，后面 c 无序）
  WHERE a=1 AND b LIKE 'xx%' AND c=3 → 同，c 用不上
  WHERE a IN (1,2,3) AND b=4 AND c=5 → MySQL 8 以前 IN 会断，8+ 能用到 b,c
```

**项目案例 19：订单列表最左前缀优化 3 轮迭代（idx(user_id, status, create_time) + 延迟关联）**

```
S：订单查询 WHERE user_id = 123 AND status IN (1,3,5) AND DATE(create_time) = '2026-08-01' ORDER BY create_time DESC LIMIT 200, 20
T：RT 1.8s，3 次慢查询告警
A：
  迭代①：DATE(create_time) 函数失效 → 改范围
    create_time >= '2026-08-01 00:00:00' AND create_time < '2026-08-02 00:00:00'
    → type: ALL→range，1.8s → 680ms
  迭代②：加 idx_user_status_createtime(user_id, status, create_time)
    status IN (1,3,5) 等值范围混合；最左前缀用 user_id + status（IN 视作一堆等值），然后 create_time 排序
    注意 MySQL 8+ IN 在等值匹配阶段可以展开成 multiple equality，然后用后面的 create_time 排序（利用索引有序避免 filesort）
    EXPLAIN Extra: Using index condition; Backward index scan  →  680ms → 80ms
  迭代③：第 200 页（LIMIT 4000,20）还慢 → 延迟关联
    SELECT o.* FROM (
      SELECT id FROM order WHERE ... ORDER BY create_time DESC LIMIT 4000, 20
    ) t JOIN order o ON o.id = t.id
    子查询覆盖索引只用 id，扫描快 → 再 20 次主键回表
    → 第 200 页 RT 820ms → 120ms
R：慢查询 0 告警，用户投诉列表慢 0 反馈（之前每周 3~5）
```

---

### 1.5.2 MVCC + 4 种隔离级别 + RR 级别 Next-Key 防幻读

**MVCC 三件套 + ReadView 可见性算法（伪代码）**

```
隐藏列（聚簇索引每条行记录头部）：
  DB_TRX_ID(6B)：最近一次修改事务的事务 ID（严格递增，START TRANSACTION 分配）
  DB_ROLL_PTR(7B)：回滚指针 → 指向 undo log
  DB_ROW_ID(6B)：无主键时自动生成

ReadView 生成时记录：
  m_ids = active transaction id list（当前活跃未提交事务）
  min_trx_id = min(m_ids)
  max_trx_id = 下一个即将分配的事务 ID

// 可见性算法：
boolean visible(row_trx_id) {
  if (row_trx_id < min_trx_id) return true;              // 生成前就提交了 → 可见
  if (row_trx_id >= max_trx_id) return false;             // 生成后才开始 → 不可见
  if (!m_ids.contains(row_trx_id)) return true;           // 中间但已提交 → 可见
  return false;                                           // 在活跃里 → 未提交 → 不可见
}
// 不可见时，沿 DB_ROLL_PTR 找 undo log 的旧版本，再次判断，直到能看见
```

**隔离级别 vs ReadView 生成时机**

| 级别 | ReadView 生成 | 现象 |
|---|---|---|
| READ COMMITTED | **每次 SELECT 都生成新的 ReadView** | 每次看最新提交 → 同一事务两次 SELECT 可能不同（不可重复读） |
| REPEATABLE READ（InnoDB 默认）| **第一次 SELECT 生成，后面复用** | 看见的是第一次 SELECT 时的快照 → 可重复读 |

**RR 为什么基本解决幻读？**

```
当前读（SELECT ... FOR UPDATE / UPDATE / DELETE）走 Next-Key Lock（Record + Gap）：
  t(id PK, name, idx_name(name)) 现有 name='a' id=5；name='c' id=10；name='e' id=15
  事务 A：SELECT * FROM t WHERE name = 'c' FOR UPDATE;
  → name='c' 普通索引，Next-Key Lock：(a,c]（上一个到 c）+ (c,e]（c 到下一个）→ 锁两段
  事务 B：
    INSERT INTO t VALUES(7,'b');  → b 在 (a,c] Gap → BLOCK
    INSERT INTO t VALUES(12,'d'); → d 在 (c,e] Gap → BLOCK
    UPDATE t SET name='c' WHERE id=15; → e→c 插入到 (c,e] Gap → BLOCK
  → RR + 当前读 + Next-Key Lock → 防止其他事务插入幻影行
快照读（普通 SELECT）走 MVCC 可见性 → 始终看不到别人新数据（RR 复用 ReadView）
所以 RR 基本解决幻读，只有"快照读后当前读"极端间隙有理论概率
```

**项目案例 20：RC 隔离级别下报表统计差 2%——长事务 ReadView 选型踩坑**

```
S：报表离线任务，统计 T-1 订单，事务 30 分钟，隔离级别 RR
T：数据和业务方对账总是差 1.8~2.2%
A：
  1. 分析：RR 下事务开始第一次 SELECT 生成 ReadView，后面 30 分钟的 SELECT 都复用
     实际有 4 个独立 SQL（订单/库存/积分/优惠券），间隔 5~8 分钟
     这期间新提交的订单都看不见
  2. 但 RC 下每次 SELECT 新 ReadView → 看到每个 SQL 时刻已提交的最新数据
     问题：第 1 条 SQL 和第 4 条 SQL 隔 20 分钟，中间产生的新订单又"算入"了 → 跨 SQL 不一致
  3. 折中方案：
     a) 报表用 RC，但 4 个 SQL 改成"业务时间截止到 T-1 23:59:59"显式时间窗口
     b) 或者长事务 START TRANSACTION WITH CONSISTENT SNAPSHOT（InnoDB 手动立即生成 ReadView，不管第一个 SELECT 什么时候）
        然后所有 SQL 用同一个快照，和对账时点完全一致
R：
  用 WITH CONSISTENT SNAPSHOT 后，对账差异 2% → 0.01%（只剩边界脏数据）
  差异原因：人工补单 → 加了人工操作日志也入报表
```

---

### 1.5.3 InnoDB 锁：行锁/Gap/Next-Key + 死锁排查 + redo/undo/binlog 2PC

**死锁排查 SOP（每次按顺序）**

```
① 打开永久日志：
  SET GLOBAL innodb_print_all_deadlocks = 1;  # 下次重启失效，my.cnf 也要写
② SHOW ENGINE INNODB STATUS\G → LATEST DETECTED DEADLOCK 段
  看：
  - TRANSACTION 1: ACTIVE 2s 正在做什么 SQL，持有哪几个锁（lock struct(s), heap no）
    RECORD LOCKS space id X page no n n bits ... 索引
    Record lock, heap no 20 PHYSICAL RECORD: 锁哪条记录
  - TRANSACTION 2: 等什么锁
  - WE ROLL BACK TRANSACTION 2: 回滚了哪个
③ 分析常见死锁模式：
  模式① 顺序相反：T1 lock A→B，T2 lock B→A （最常见 60%）
  模式② 不同索引：T1 走 idx_name 锁 name='a' Gap，T2 走 idx_phone 锁同一行 id 不同区间 Gap 交叉
  模式③ Gap Lock 交叉：RR 级别等值未命中退化成 Gap Lock，两个事务先互相插入 Gap
④ 修复：
  - 统一加锁顺序（所有 UPDATE 先按主键顺序，先加小的 id）
  - 改 RC 隔离级别（RC 没有 Gap Lock，只有 Record Lock）
  - 死锁超过阈值自动告警（Prometheus mysql_global_status_innodb_deadlocks）
```

**redo / undo / binlog 两阶段提交（崩溃恢复不会丢数据的根本原因）**

```
InnoDB + Server 层 binlog 两阶段提交：

  ① prepare 阶段：
     - 写 redo log (prepare state)
     - redo write + fsync 到磁盘（innodb_flush_log_at_trx_commit=1 每次都刷）

  ② binlog 阶段：
     - 写 binlog（sync_binlog=1 每次 fsync）

  ③ commit 阶段：
     - 写 redo log (commit state) → 刷盘

崩溃恢复判断（MySQL 重启时 scan 最后一个 binlog 文件 + redo prepare）：
  - 如果 redo 是 commit → 直接提交
  - 如果 redo 是 prepare：
      a) 事务的 XID 在 binlog 里存在（binlog 写成功了）→ commit（客户端当时可能没收到，但 binlog 已发给从库/消费端，必须一致）
      b) XID 不在 binlog（binlog 没写完）→ rollback
```

**项目案例 21：死锁"反向更新顺序"——退款 & 订单完成同时更新两张表**

```
S：售后订单，支付表 pay + 订单表 order。两个接口：
  ① 运营退款：BEGIN; UPDATE pay SET refund=1 WHERE order_no='A'; UPDATE order SET status='REFUND' WHERE order_no='A'; COMMIT;
  ② MQ 异步订单完成：BEGIN; UPDATE order SET status='DONE' WHERE order_no='A'; UPDATE pay SET flag='SETTLED' WHERE order_no='A'; COMMIT;
  顺序正好相反 → 死锁（每天 2~3 次）
T：每次死锁其中一个回滚，运营操作"假成功"，实际没更新
A：
  1. innodb status 看到 LATEST DETECTED DEADLOCK：
     TRANSACTION 14A2B: lock X on rec for pay.order_no='A' → wait for order.order_no='A'
     TRANSACTION 14A2C: lock X on rec for order.order_no='A' → wait for pay.order_no='A'
  2. 修复（两步法）：
     a) 统一顺序：按照"先子表后父表"或"字典序 order_no → pay → order"的统一顺序
        退款和 MQ 都先 order 再 pay（或先 pay 再 order，顺序一致就好）
     b) SQL 加上 ORDER BY 主键/索引列批量更新时也保证顺序（UPDATE ... WHERE id IN (1,3,2) ORDER BY id）
     c) 加重试：if SQLException SQLState='40001' → retry 3 次 exponential backoff
R：
  死锁 0 次；之前每周人工修复 10~20 单 → 0
  retry 兜底：极端顺序偶发（没覆盖到的接口）也能自动恢复
```

---

## 1.6 中间件高级

### 1.6.1 Redis 高级：内部编码 + 持久化 + 主从/哨兵/Cluster + bigkey

**5 大类型底层编码转换条件（面试源码细节加分）**

| 类型 | 编码（encoding） | 转换条件 |
|---|---|---|
| String | int → embstr(<=44B) → raw(>44B) | value 是 8B 内整数 → int；否则 len ≤ 44 → embstr；否则 raw(SDS) |
| List | quicklist（ziplist2×linkedlist）<br>每个 quicklistNode 是 ziplist | list-compress-depth=0 不压缩；>0 表示头尾各 N 个节点不压缩，中间 LZF 压缩 |
| Hash | ziplist → hashtable | 所有 entry 长度 ≤ 64B 且 entries ≤ 512 → ziplist；否则转 hashtable |
| Set | intset → hashtable | 全部是 int 且 elements ≤ 512 → intset；否则 hashtable |
| ZSet | ziplist → skiplist+hashtable | 所有 member ≤ 64B 且 entries ≤ 128 → ziplist；否则 skiplist+hashtable |

object encoding key 命令可以查看当前编码

**Redis Cluster 16384 槽路由 & 重定向**

```
crc16(key) % 16384 = slot
{hashtag} 如果 key 含 {} → 只计算 {} 内内容做 slot（同业务固定到同一节点，支持 MGET/LUA 多 key 原子）

MOVED 重定向：客户端问 nodeA: get user:1 → nodeA 返回 MOVED 866 nodeB:6379
ASK 重定向：slot 迁移中，部分 key 在源部分在目标 → 源返回 ASK 10022 targetNode
  → 客户端下一条命令先发 ASKING 到 targetNode，再发命令
```

**项目案例 22：bigkey 大 List 扫盲 + 优化 3 步（电商订单流水）**

```
S：订单服务 user_id → List<orderId>（用户订单列表），最长 3 年 840 个订单，每个 orderId 32B
T：redis-cli --bigkeys：最大 List 27MB；MEMORY USAGE user:order:1234 = 27MB
A：
  ① 为什么大？32B × 840 也才 26.8KB 啊？不对！
     实际是 quicklist 每个 ziplist 节点没压缩 + quicklist 每个 entry 有 prev/next/zl 指针
     加上编码开销，840 条其实已经是小的
     真正 bigkey 是 user:order:99999 里 18w 订单 —— C 端不活跃用户用了 1 个 List 存历史所有子订单
     MEMORY USAGE 276MB
  ② 3 步优化：
     a) 拆分：大 List 按月份分片 user:order:99999:202608；列表只保留最近 12 个月 key
     b) 冷数据（>1 年）归档 MySQL + 二级索引 Elasticsearch
     c) list-max-ziplist-size 调大（默认 -2=8KB）到 -5=64KB
        让每个 quicklistNode 的 ziplist 更大，减少指针和碎片
  ③ 日常治理脚本：
     redis-rdb-tools -c memory dump.rdb --bytes 1048576 --largest 100 > bigkey.txt（离线）
     线上 Redis 7+ 用 MEMORY PURGE + 定时任务 Top N 告警
R：
  内存占用：21GB → 6.8GB（节省 67%，少加一组机器 ¥20w/年）
  bigkey 导致的主从同步延迟：400ms → <10ms
  后续：公司内写了一份《Redis 开发规约》bigkey 排查 + 设计禁止写入 List 超过 1000
```

---

### 1.6.2 Kafka 高吞吐设计 + Rebalance + ISR + 端到端零丢失

**Kafka 高吞吐 5 大设计**

```
① 顺序写磁盘：LogSegment .log 文件 appending 顺序写，机械盘 600MB/s
② PageCache + 零拷贝：
   producer → 写入 broker PageCache（刷盘由 OS pdflush）
   consumer → sendfile() 系统调用：PageCache → Socket Buffer 直接（传统 4 次 copy → 2 次）
   Java NIO FileChannel.transferTo 实现 zero copy
③ 批量 + 压缩：
   producer batch.size=16384，linger.ms=0（有就发，无等 batch），
   compression.type=lz4/zstd（CPU 开销小解压快）
④ Partition 并行：
   一个 Topic N 分区 = N 个并行写入 + N 个并行消费（Consumer Group 线程数 ≤ 分区数）
⑤ Record Accumulator + 按批 + 2-3 层队列解耦
```

**项目案例 23：Kafka 端到端零丢失配置清单（支付流水）**

```
S：支付流水 Kafka → Flink 实时对账 → 入数仓；对账 1 条都不能丢
T：每月对账漏 10~20 条，排查时间 4~8 小时
A：
  配置清单（全链路 5 处）：
  ① Producer 生产端：
     acks = all                    # 必须所有 ISR ack（leader 挂了新 leader 也有备份）
     retries = 2147483647          # 可重试的错误一直重试
     enable.idempotence = true     # 幂等生产者：PID + Sequence，防重重试重复写入
     max.in.flight.requests.per.connection ≤ 5  # 防止乱序（0.11+ 幂等打开保持有序）
     transactional.id = pay-producer-1  # 事务：同一事务多条发送原子
     delivery.timeout.ms = 120000
  ② Broker 端：
     min.insync.replicas = 2        # acks=all 时 ISR 中至少 2 个（含 leader）
     unclean.leader.election.enable = false   # 落后太多的副本不能当 leader（数据安全 > 可用性）
     replication.factor = 3        # 3 副本
  ③ Topic 端：
     retention.ms = 3天 × 24 × 3600000
  ④ Consumer 端：
     enable.auto.commit = false     # 手动提交 offset
     消费处理完 DB 提交后再 commitSync(offsets)
  ⑤ 生产端确认回调 Callback:
     producer.send(record, (metadata, e) -> {
         if (e != null) log.error("Fail {} {}", topic, record.key(), e);
     });
  额外：对账补偿链路（终极兜底）：T+1 DB full vs Kafka topic dump offset range → 差异用 DB source 补
R：
  丢失 10~20 单/月 → 0（连续 8 个月 0 丢失）
  重复（偶尔 broker ack 丢失时重试）→ 幂等消费 DB INSERT ignore 唯一索引，重复不生效
  生产端 Callback 错误日志告警 → 发现 1 次 broker 磁盘坏道，10 分钟修复
```

---

### 1.6.3 RocketMQ 事务消息 + 主从同步 + 零拷贝

（详见 Part2 后续内容）

**项目案例 24：RocketMQ 事务消息 + 本地消息表双重保险，订单创建 → 扣库存最终一致**

---

# 二、技术二面（架构设计 + 技术决策 + 排障）

## 2.1 项目深挖：STAR 高级版（含完整订单性能优化案例）

（详细见合并后全文）

**高级 STAR 回答模板（12~15 分钟）：**
S 背景（公司/规模/团队/技术栈/数据量级）
T 任务（目标指标 + 你角色 Owner / Core Dev）
A 行动（60% 时长，按模块分解 + 每块都要选型对比）
  - 整体架构图（脑中的）：入口 → 网关 → 服务 → MQ → 缓存 → DB
  - 技术选型对比表（2~3 个方案，优缺点+最终选择理由）
  - 关键模块细节设计（类图/时序/状态机）
  - 难点 + 解决方案（至少 3 个真实难点）
  - 压测/监控/告警（Prometheus+Grafana，SLO）
R 结果（量化 + 团队影响 + 推广）

## 2.2 系统设计：秒杀/短链/支付/IM/排行榜 + 答题 8 步 SOP

**8 步答题框架（通用）：**
1. 需求理解 + 场景边界（DAU/QPS/RT/一致性）
2. 容量评估（机器 / 存储 / 带宽 / 缓存）
3. 系统架构图（端到端）
4. 核心模块设计（DB 选型 / 分库分表方案）
5. 关键难点（一致性 / 热点 / 幂等 / 顺序 / 反作弊）
6. 高可用（降级 / 熔断 / 限流 / 多活）
7. 监控告警（关键指标 + 阈值）
8. 未来演进（10 倍量扩容）

**项目案例 25：秒杀系统 3 层漏斗完整设计（含热点隔离 + 流量削峰）**
**项目案例 26：IM 长连接系统（Netty + Redis Pub/Sub + Kafka 离线存储 + 多端同步）**
**项目案例 27：排行榜（ZSet + 分区榜 + 每日快照 + TopN 异步物化）**
（详见合并版全文）

## 2.3 线上排障 6 大场景 SOP（CPU 100% / OOM / 慢接口 / 死锁 / MQ 积压 / Redis 变慢）

**项目案例 28：CPU 100% Artheas 火焰图定位正则回溯（XXS 防护正则 .*(script).* → RE2/J）**
**项目案例 29：OOM ThreadLocal 累积泄漏（线程池复用时忘记 remove，MAT 分析看 Thread 对象 value 链）**
**项目案例 30：Redis 变慢 root cause（bigkey + fork 子进程 AOF rewrite + RDB 同时触发 COW 写放大）**
（详细见合并版全文）

---

# 三、HR / 综合面（高级版差异）

（详见合并版全文）

## 3.1 自我介绍（3 分钟 / 1 分钟两版）
## 3.2 必问 8 大问题与应答模板（高级版追问应对）
## 3.3 反问面试官阶段清单（高级岗应问技术深度）

---

# 四、冲刺资料清单与备考计划

## 4.1 必背源码清单（每个能讲 10 分钟+，高级岗 16 项）
## 4.2 系统设计学习路径（书单 + 博客 + 实战）
## 4.3 4 周在职冲刺计划（每天 2h + 周末 6h）

---

# 五、附：真实项目 STAR 案例模板

（高级版附 3 套完整 STAR 模板：电商性能优化 / 金融对账一致性 / 微服务治理，详见全文）

---

> **使用说明**：本文件为扩写版 Part2，需要和 Part1 合并使用形成完整文档。

