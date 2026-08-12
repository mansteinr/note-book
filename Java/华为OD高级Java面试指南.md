# 华为 OD 高级 Java 面试完全指南（5 年+ / 高级程序员版）

---

## 目录

- [华为 OD 高级 Java 面试完全指南（5 年+ / 高级程序员版）](#华为-od-高级-java-面试完全指南5-年--高级程序员版)
  - [目录](#目录)
- [二、技术一面（深入源码级）](#二技术一面深入源码级)
  - [2.1 Java 基础：不止"会用"，要"为什么这样设计"](#21-java-基础不止会用要为什么这样设计)
    - [2.1.1 HashMap 全链路源码级问答](#211-hashmap-全链路源码级问答)
    - [2.1.2 volatile 与 JMM](#212-volatile-与-jmm)
    - [2.1.3 synchronized 与锁升级](#213-synchronized-与锁升级)
    - [2.1.4 ThreadLocal 原理与内存泄漏](#214-threadlocal-原理与内存泄漏)
    - [2.1.5 AQS 框架深度解析](#215-aqs-框架深度解析)
  - [2.2 JVM：从原理到调优实战](#22-jvm从原理到调优实战)
    - [2.2.1 JVM 内存模型深入](#221-jvm-内存模型深入)
    - [2.2.2 垃圾回收器底层原理与对比](#222-垃圾回收器底层原理与对比)
    - [2.2.3 类加载机制与双亲委派](#223-类加载机制与双亲委派)
    - [2.2.4 OOM 排查与调优完整流程](#224-oom-排查与调优完整流程)
  - [2.3 Spring：核心流程源码级掌握](#23-spring核心流程源码级掌握)
    - [2.3.1 IOC 启动流程（refresh() 12 步）](#231-ioc-启动流程refresh-12-步)
    - [2.3.2 Bean 生命周期 + 扩展点时序（10+ 步，按执行顺序）](#232-bean-生命周期--扩展点时序10-步按执行顺序)
    - [2.3.3 循环依赖 + 三级缓存](#233-循环依赖--三级缓存)
    - [2.3.4 AOP 源码解析](#234-aop-源码解析)
    - [2.3.5 Spring Boot 自动装配原理](#235-spring-boot-自动装配原理)
  - [2.4 并发编程：分布式场景](#24-并发编程分布式场景)
    - [2.4.1 分布式锁深入](#241-分布式锁深入)
    - [2.4.2 分布式事务选型与对比](#242-分布式事务选型与对比)
    - [2.4.3 微服务 \& RPC](#243-微服务--rpc)
  - [2.5 MySQL：深度 + 调优实战](#25-mysql深度--调优实战)
    - [2.5.1 ~ 2.5.3（B+树、MVCC、锁机制）简述](#251--253b树mvcc锁机制简述)
    - [2.5.4 三大日志（redo/undo/binlog）与两阶段提交](#254-三大日志redoundobinlog与两阶段提交)
    - [2.5.5 主从复制原理](#255-主从复制原理)
  - [2.6 中间件高级](#26-中间件高级)
    - [2.6.1 Redis 底层实现](#261-redis-底层实现)
    - [2.6.2 Redis 持久化与高可用](#262-redis-持久化与高可用)
    - [2.6.3 Kafka 底层原理](#263-kafka-底层原理)
    - [2.6.4 RocketMQ 特色功能](#264-rocketmq-特色功能)
- [三、技术二面（架构设计 + 技术决策 + 排障）](#三技术二面架构设计--技术决策--排障)
  - [3.1 项目深挖：STAR 高级版](#31-项目深挖star-高级版)
    - [3.1.1 项目 STAR 模板（高级版）](#311-项目-star-模板高级版)
    - [3.1.2 典型追问方向与应答策略](#312-典型追问方向与应答策略)
  - [3.2 系统设计：高频题目 + 答题框架](#32-系统设计高频题目--答题框架)
    - [3.2.1 系统设计评分维度（8 步 SOP）](#321-系统设计评分维度8-步-sop)
    - [3.2.2 设计一：百万级 QPS 秒杀系统](#322-设计一百万级-qps-秒杀系统)
  - [3.3 线上排障：灵魂拷问 6 大场景](#33-线上排障灵魂拷问-6-大场景)
    - [3.3.1 线上 CPU 100% 排查](#331-线上-cpu-100-排查)
    - [3.3.2 线上 OOM 排查](#332-线上-oom-排查)
    - [3.3.3 接口响应变慢排查](#333-接口响应变慢排查)
    - [3.3.4 数据库死锁排查](#334-数据库死锁排查)
    - [3.3.5 MQ 消息大量堆积排查](#335-mq-消息大量堆积排查)
    - [3.3.6 Redis 响应变慢排查](#336-redis-响应变慢排查)

---

# 二、技术一面（深入源码级）

## 2.1 Java 基础：不止"会用"，要"为什么这样设计"

### 2.1.1 HashMap 全链路源码级问答

```
Q1：HashMap 底层结构（JDK8）？
A：Node<K,V>[] table 数组 + （单链表 + 红黑树 TreeNode）。

Q2：put 方法完整流程？
A：
  1. 计算 hash：h = key.hashCode(); hash = h ^ (h >>> 16);
     - 为什么右移 16 位异或？高位参与运算，减少高位不同低位相同的冲突概率
  2. 判断 table 为空则 resize() 初始化（默认 16，loadFactor 0.75）
  3. 定位桶下标：i = (n - 1) & hash
     - 为什么不用 %？位运算更快；n 必须是 2 的幂保证 [0,n-1]
  4. 桶无元素 → CAS 插入（putVal 中），成功转 7
  5. 桶有元素（hash 碰撞）：
     a) 与头节点 hash 相等 && (key 同引用 || equals) → 覆盖 value
     b) 节点是 TreeNode → 红黑树插入 putTreeVal
     c) 是普通链表 → 尾插遍历（JDK7 头插 JDK8 尾插，防扩容死循环）
        · 找到相同 key → 覆盖
        · 未找到 → 尾插 newNode，此时判断 binCount >= TREEIFY_THRESHOLD-1(7)
          → 若 table.length < 64 则 resize 扩容，否则 treeifyBin 转红黑树
  6. 若第 5 步是覆盖旧 value → 返回旧值，不进下一步
  7. ++modCount，++size
  8. 若 size > threshold（capacity * loadFactor）→ resize 扩容（2 倍）
     - 扩容时重哈希：元素要么在"原位 i"，要么在"i + oldCap 位置"（因 2 倍扩容，
       最高位 hash bit 0/1 决定），避免完整重算

Q3：树化阈值为什么是 8？
A：HashMap 源码注释里给了答案：
   理想情况下，随机 hashCode 使得桶中节点频率服从泊松分布(λ=0.5)，
   一个桶中出现 8 个节点概率仅 0.00000006（约 6 千万次才 1 次），
   所以 8 是概率极小的阈值，防止频繁树化/链化。退化阈值是 6（留缓冲）。

Q4：为什么 loadFactor = 0.75？
A：时间与空间的折中：
   - 太小（如 0.5）→ 碰撞少，查询快，但浪费内存、频繁扩容
   - 太大（如 1.0）→ 省内存，但碰撞多，链表长，查询慢
   - 0.75 是泊松分布最佳平衡点（源码注释：0.75 对数正态分布拐点）

Q5：HashMap 线程不安全的表现（2 种经典 bug）？
A：
  ① JDK7 扩容头插 → 并发扩容时链表形成环 → get 时死循环 CPU100%
     JDK8 改成尾插，虽然不会成环，但仍不安全
  ② 并发 put：两个线程同时计算到空桶位置，都 CAS 其中一个成功
     另一个失败后在 putVal 里的"遍历判断覆盖"逻辑可能丢数据
  ③ size++ 不是原子操作，多线程加统计不准

Q6：HashMap 为什么用红黑树不用 AVL？
A：红黑树是弱平衡（最长路径 ≤ 2 × 最短路径），插入删除旋转次数更少（最多 3 次），
   而 AVL 是严格平衡，查询稍快但修改慢。HashMap 场景是插入删除查询频率均衡，
   所以红黑树更合适。

Q7：可以自定义对象作为 HashMap 的 Key 吗？需要满足什么？
A：可以。必须：
   ① 重写 equals()：业务相等判断
   ② 重写 hashCode()：保证 equals 相等的对象 hashCode 必须相同
      - 两个对象 equals 相等 → hashCode 必须相等（约束）
      - hashCode 相等 → equals 不一定相等（哈希碰撞允许）
   ③ 最好不可变（如 String、Integer），否则 put 后修改字段导致 hashCode 变了，
     就 get 不到了（内存泄漏的一种）
```

---

### 2.1.2 volatile 与 JMM

```
Q1：volatile 的两大作用？
A：
  ① 可见性：写 volatile 变量时，JMM 把本地内存变量值立即刷回主内存；
            读 volatile 变量时，JMM 把本地内存对应行置无效，重新从主内存读。
            本质：写加 StoreLoad 屏障；读加 LoadLoad + LoadStore 屏障。
  ② 有序性（禁止指令重排）：volatile 前后插入内存屏障，
     阻止编译器 + CPU 层面的指令重排。
     - volatile 写之前的操作不能重排到写之后
     - volatile 读之后的操作不能重排到读之前
     - 写后读：StoreLoad 屏障（最耗性能）

Q2：DCL 单例为什么必须加 volatile？
```java
public class Singleton {
    private static volatile Singleton INSTANCE;   // ← 必须 volatile
    private Singleton() {}
    public static Singleton getInstance() {
        if (INSTANCE == null) {                    // ① 第一次无锁检查
            synchronized (Singleton.class) {
                if (INSTANCE == null) {            // ② 加锁后再检查
                    INSTANCE = new Singleton();    // ③ 创建对象
                }
            }
        }
        return INSTANCE;
    }
}
// new Singleton() 字节码 3 步：
//   1. memory = allocate()        分配内存
//   2. ctorInstance(memory)       初始化对象（构造方法）
//   3. INSTANCE = memory          引用指向内存
// JVM 可能重排为 1→3→2：此时线程 A 执行到 3（还没 2），INSTANCE != null
// 线程 B 在①判断非空，直接返回未初始化对象！→ NPE 风险
// volatile 禁止 1-3 的 StoreStore 重排，保证 2 先于 3 完成
```

Q3：volatile 能保证原子性吗？和 synchronized 的区别？
A：不能！volatile 只保证可见性 + 顺序性，i++ 这种读改写三步不是原子的。

| 特性 | volatile | synchronized |
|---|---|---|
| 可见性 | ✅ | ✅（解锁前刷回主存） |
| 顺序性 | ✅（局部） | ✅（串行执行天然有序） |
| 原子性 | ❌ | ✅（锁住临界区） |
| 粒度 | 变量级 | 对象 / 方法 / 代码块 |
| 阻塞 | ❌ 无锁 | ✅ 可能阻塞 |
| 适用场景 | 状态标记位（run flag）、DCL | 复杂临界区、需要原子操作 |

Q4：JMM 8 种内存交互操作？
A：lock（主存变量标记线程独占）、unlock、
   read（主存→工作内存）、load（工作内存→变量副本）、
   use（工作内存→执行引擎）、assign（执行引擎→工作内存）、
   store（工作内存→主存）、write（主存变量值更新）。
   规则：read/load 必须连续出现，store/write 必须连续出现，等共 8 条规则。

---

### 2.1.3 synchronized 与锁升级

```
Q1：synchronized 底层原理？对象头结构？
A：
  【对象头（64 位 JVM，普通对象）】
  ┌────────────────────── Mark Word (64bit) ──────────────────────┬── Klass Word(64bit) ─┐
  │ 加锁状态存储：hashcode/GC age/偏向锁ID/锁标志/monitor 地址...  │ 指向类元数据指针    │
  └──────────────────────────────────────────────────────────────┴──────────────────────┘
  （数组对象多 32bit 数组长度）

  Mark Word 不同状态 64bit 分配（64 位 JVM，开启压缩指针时）：
  ┌───────────────┬───────┬───────┬──────────┬────┬────────────┐
  │  无锁         │ unused│ hash  │  GC age  │  0 │  01        │ ← lock=01 biased=0
  │  偏向锁       │ thread │ epoch │ GC age  │  1 │  01        │ ← lock=01 biased=1
  │  轻量级锁     │ 指向栈中 Lock Record 的指针              │ 00 │ ← lock=00
  │  重量级锁     │ 指向 ObjectMonitor 的指针                │ 10 │ ← lock=10
  │  GC 标记     │ 空（标记要 GC）                         │ 11 │ ← lock=11
  └───────────────┴───────┴───────┴──────────┴────┴────────────┘

  synchronized 加在代码块：
   - 编译后加 monitorenter 指令（进入），monitorexit 指令两个（正常退出 + 异常保证释放）
  synchronized 加在方法：
   - 方法访问标志 ACC_SYNCHRONIZED，JVM 调用方法时自动加对象锁 / 类锁

Q2：锁升级 4 级过程（JDK6 引入优化，JDK15 偏向锁默认关闭）？
A： 无锁 → 偏向锁 → 轻量级锁（CAS 自旋） → 重量级锁（操作系统 Mutex）
  升级是单向的，只能升不能降（除了批量重偏向/批量撤销在安全点降级）。

  ① 【偏向锁】：只有一个线程访问时
     - 第一个线程进入同步块：CAS 把 Mark Word 的 thread 字段设为自己的线程 ID
     - 成功则获取偏向锁；每次进入只判断 thread 是否是自己（零开销）
     - 第二个线程来竞争：进入安全点，检查偏向线程是否存活
       * 原线程死亡 → 撤销偏向，恢复无锁重新偏向新线程
       * 原线程还活着（栈中有 Lock Record） → 升级到轻量级锁
     - 问题：竞争多撤销开销大，所以 JDK15 默认 -XX:+UseBiasedLocking=false

  ② 【轻量级锁（CAS 自旋）】：两个线程交替访问
     - 进入同步块前，在当前线程栈帧中创建 Lock Record，复制 Mark Word 到 LR
     - CAS 把对象 Mark Word 改为指向当前线程 LR 的指针
       * 成功 → 获得轻量级锁
       * 失败 → 说明其他线程持有，当前线程自旋几次（默认 Adaptive Self Spinning）
       * 自旋一定次数（JDK7 后自适应，看上次成功概率）仍没拿到 → 膨胀为重量级锁

  ③ 【重量级锁】：多线程同时竞争
     - Mark Word 改为指向 ObjectMonitor 对象（C++ 实现）
     - ObjectMonitor 关键字段：
       _owner：当前持有线程
       _EntryList：阻塞等待锁的线程队列（双向链表）
       _WaitSet：wait() 后等待的线程队列
       _recursions：重入次数
     - 竞争失败的线程 park 到 _EntryList，等待被 unpark（涉及用户态→内核态切换，开销大）

Q3：synchronized 与 ReentrantLock 对比（高级版）？

| 维度 | synchronized | ReentrantLock |
|---|---|---|
| 实现层面 | JVM 内置（C++ ObjectMonitor） | JDK API 层（Java AQS + CAS） |
| 锁类型 | 非公平 + 可重入 + 独占 | 默认非公平 / 可公平 + 可重入 + 独占 |
| 等待可中断 | ❌ 死等 | ✅ lockInterruptibly() / tryLock(timeout) |
| 公平锁 | ❌ | ✅ new ReentrantLock(true) |
| 多条件条件变量 | ❌ 只有 1 个 wait/notify 集合 | ✅ newCondition() 多个 Condition |
| 获取锁状态 | ❌ 无 | ✅ isLocked() / isHeldByCurrentThread() / getHoldCount() |
| 性能（竞争少） | 相当 | 相当 |
| 性能（竞争激烈） | 锁膨胀性能一般 | AQS+CAS 更灵活，性能更好 |
| 自动释放 | ✅（异常/结束自动 monitorexit） | ❌ 必须 finally { lock.unlock() } |

Q4：synchronized 锁重入原理？
A：同一线程可重复进入 synchronized，计数+1：
  - 偏向锁：判断 thread 是自己，偏向次数++（记录在线程栈的 LR）
  - 轻量级锁：判断 Mark Word 指向的 LR 还是本线程，再加一个新的 LR 栈顶，null disheader
  - 重量级锁：ObjectMonitor._recursions++，退出--，到 0 才释放锁

Q5：锁降级了解吗？
A：写线程在持有写锁的同时降级为读锁（不释放写锁先获取读锁，再释放写锁）。
   注意这里不是指 synchronized 的锁级别降级（JVM 锁升级是单向的，锁降级只在
   G1 的 safe point 批量操作时会做），而是指 ReentrantReadWriteLock 支持写→读降级。
   降级的意义：防止写后立刻被其他写线程插入修改，保证读到的数据是自己刚写的一致数据。
```

---

### 2.1.4 ThreadLocal 原理与内存泄漏

```
Q1：ThreadLocal 实现原理？
A：
  每个 Thread 线程对象内部都有一个 threadLocals（ThreadLocal.ThreadLocalMap 引用，初始 null）
  ThreadLocal.set(value):
    1. 获取当前线程 Thread.currentThread()
    2. 取出其 threadLocals（ThreadLocalMap）
       - map 为空 → createMap(t, value) 创建（首次）
    3. map.set(this, value) → key = 当前 ThreadLocal 对象（弱引用），value = 值

  ThreadLocal.ThreadLocalMap：
    - Entry[] table 结构（不像 HashMap 链地址，ThreadLocalMap 是线性探测法解决冲突）
    - Entry<K,V> 继承 WeakReference<K>：
        class Entry extends WeakReference<ThreadLocal<?>> { Object value; }
        即：key 指向 ThreadLocal 是弱引用，value 指向值是强引用

Q2：key 为什么设计成弱引用？内存泄漏怎么产生的？
A：
  【如果 key 是强引用】：
  ThreadLocalRef（栈上强引用）→ ThreadLocal 对象 → 被 Entry.key 强引用
  当业务代码把 ThreadLocalRef = null 想释放 ThreadLocal 对象时，
  因为 Entry.key 还强引用，导致 ThreadLocal 无法 GC，内存泄漏。

  【现在 key 是弱引用】：
  ThreadLocalRef = null 后，下次 GC 时弱引用会回收 ThreadLocal 对象，
  Entry.key = null，但 Entry 本身仍在 table 数组中，Entry.value 仍强引用着 value 对象。
  此时 value 无法通过任何方式 get 到，但仍占内存 → 产生内存泄漏！

  【为什么 value 不也设计成弱引用？】
  value 如果是弱引用 → 你业务还在使用的 value，可能 GC 时就被随便回收了，这是不可接受的！
  所以必须强引用 value，那靠谁清理？

  【ThreadLocalMap 启发式清理机制（3 种）】：
    ① set()：线性探测过程中碰到 key=null 的脏 Entry，调用 replaceStaleEntry() 清理
    ② get()：探测到 key 不匹配时遇到脏 Entry，调用 expungeStaleEntry(i)
       - 清理当前脏 slot
       - 向后遍历连续的非空段，进行 rehash（探测式清理 expungeStaleEntries）
       - 超过 2/3 阈值再 rehash
    ③ remove()：最推荐！显式调用 expungeStaleEntry 清理

  ✅ 最佳实践：try-finally 块中一定手动 threadLocal.remove()，彻底避免泄漏！

Q3：父子线程如何传递 ThreadLocal？
A：
  ① InheritableThreadLocal（JDK 自带）：
     - 子线程 new Thread() 时会调用 init() → inheritableThreadLocals = parent.inheritableThreadLocals.clone()
     - 仅在创建子线程那一刻拷贝一次，之后各自独立不互通
  ② ThreadLocal + TransmittableThreadLocal（阿里 TTL，开源）：
     - 解决线程池场景下 Runnable 被线程复用时 ThreadLocal 传递问题
     - 原理：TtlRunnable/Runnable 包装：提交前捕获 TTL 值 → run 前回放 → run 后恢复
     - 使用：TtlExecutors.getTtlExecutor(executor) 包装线程池

Q4：ThreadLocalMap 线性探测 vs HashMap 链地址，各自优缺点？
A：
  - 线性探测法（开放寻址）：冲突时依次找下一个空 slot
    优点：不用额外指针结构，Entry 数组连续紧凑，CPU cache 友好
    缺点：聚集问题（连续满段，哈希冲突越来越严重，探测距离很长）；删除复杂（伪删除或 rehash）
    适用：数据量少，负载因子低（ThreadLocalMap 阈值 len*2/3）
  - 链地址法：冲突挂链表/红黑树
    优点：无聚集问题，删除简单，负载因子高可到 0.75
    缺点：链表节点分散，链表长还要转红黑树，指针开销
    适用：数据量大，冲突频繁
```

---

### 2.1.5 AQS 框架深度解析

```
Q1：AQS 整体原理？
A：AbstractQueuedSynchronizer 队列同步器：
  - 核心 state（volatile int）：表示锁的状态（0=空闲，1=被占，>1=重入次数）
  - 双向链表 CLH 变体队列：没抢到锁的线程 Node 入队排队（head 哨兵哑节点，tail 尾指针）
  - 两种模式：
    · 独占（Exclusive）：同一时刻只允许一个线程持有（ReentrantLock）
    · 共享（Share）：允许多个线程同时持有（Semaphore/CountDownLatch/ReadLock）
  - 模板方法模式：子类只需重写 tryAcquire / tryRelease（独占）
    或 tryAcquireShared / tryReleaseShared（共享），排队/阻塞/唤醒 AQS 做

Q2：独占锁 acquire(int) 完整流程（ReentrantLock.lock() 最终调用）？
```java
public final void acquire(int arg) {
    // 1. 先 tryAcquire 尝试抢一次（子类实现，非公平直接 CAS）
    if (!tryAcquire(arg) &&
        // 2. 失败则 addWaiter：包装成 Node.EXCLUSIVE 节点
        //    队列为空时先 enq 初始化 head 哑节点 + CAS 入队尾
        acquireQueued(addWaiter(Node.EXCLUSIVE), arg))
        // 7. 如果 acquireQueued 返回 true 表示等待中被中断过
        //    AQS 不响应中断直接被唤醒，需要"补一次中断标记"
        selfInterrupt();
}

final boolean acquireQueued(final Node node, int arg) {
    boolean failed = true;
    try {
        boolean interrupted = false;
        for (;;) {                            // 3. 自旋
            final Node p = node.predecessor();
            if (p == head && tryAcquire(arg)) {  // 4. 前驱是 head，才敢 tryAcquire
                setHead(node); p.next = null;    // 抢成功：head 指向自己（移除老 head）
                failed = false;
                return interrupted;
            }
            // 5. 抢不到，判断是否 park 阻塞
            // shouldParkAfterFailedAcquire：
            //   检查前驱 waitStatus：
            //     SIGNAL(-1) → 前驱释放时会 unpark 我，可以安全 park（返回 true）
            //     CANCELLED(1) → 前驱取消了，for 循环往前跳过取消的节点，找到非 1 的前驱，链接
            //     0/PROPAGATE → CAS 把前驱设为 SIGNAL（这次不 park，下次再检查）
            if (shouldParkAfterFailedAcquire(p, node) &&
                // 6. parkAndCheckInterrupt：LockSupport.park(this) 阻塞当前线程
                //    被 unpark/中断 后醒来返回是否中断标记
                parkAndCheckInterrupt())
                interrupted = true;
        }
    } finally {
        if (failed) cancelAcquire(node);  // 异常则把当前 Node ws 设为 CANCELLED
    }
}
```

Q3：为什么 AQS 用 CLH 变体队列？原来的 CLH 是啥？
A：
  - 原版 CLH（Craig, Landin, Hagersten）：单向链表 + 自旋前驱节点的 locked 状态
    每个节点自旋前驱状态，适合无缓存一致的 NUMA 架构
  - AQS 变体：双向链表 + 前驱 ws 状态 + LockSupport.park/unpark 阻塞（不忙等）
    - 为什么双向？cancelAcquire 时需要找到前驱 prev，断开取消节点
    - 为什么不用原版自旋？Java 是高并发调度，忙等浪费 CPU，用 park 让出 CPU 更合理

Q4：为什么 acquireQueued 里被中断只是记标记，不直接抛？最后 selfInterrupt？
A：AQS 的 acquire 是"忽略中断的独占获取"语义——被中断唤醒后不立即响应异常退出，
   而是继续抢锁（不然已经入队等半天了，中断就白等了？），
   但不能吞掉中断标记，所以等到 finally 出来后补一次 Thread.currentThread().interrupt()
   让调用者能感知到（如果真要响应中断用 acquireInterruptibly）。

Q5：释放锁 release(int) 流程？
```java
public final boolean release(int arg) {
    if (tryRelease(arg)) {            // 子类实现：ReentrantLock state-count 直到 0 才返回 true
        Node h = head;
        if (h != null && h.waitStatus != 0)  // 头节点非空且状态不是 0 说明有后继等待
            unparkSuccessor(h);        // 唤醒后继：找到 head.next 第一个非 cancelled 节点 unpark
        return true;
    }
    return false;
}
```

Q6：Condition（await / signal）原理？
A：ReentrantLock.newCondition() 返回 ConditionObject（AQS 内部类）：
  - ConditionObject 有自己的等待队列 firstWaiter / lastWaiter（单向，不是 AQS 的同步队列）
  - await()：
    ① 检查当前线程是否持有锁（不持锁抛 IllegalMonitorStateException）
    ② 新建 Node 加入 Condition 等待队列尾部
    ③ fullyRelease：完全释放当前重入锁（记录 saveState = 重入次数，release(state)）
    ④ while(!isOnSyncQueue) LockSupport.park(this) // 阻塞，等待 signal 或中断
    ⑤ 被 signal 到同步队列：从 condition 队列移除，transferForSignal
       → CAS 设置前驱 ws = SIGNAL → enq 进同步队列尾部
    ⑥ acquireQueued 重新在同步队列排队抢锁
    ⑦ 抢到后根据 saveState 恢复重入次数
  - signal() / signalAll()：
    从 condition 队列头（signalAll 遍历全部）依次 doSignal：transferForSignal 送到同步队列

Q7：公平锁 vs 非公平锁（ReentrantLock）源码差异？
A：都基于 AQS，差别在 tryAcquire：
  - 非公平（默认 NonfairSync）：任何线程来都先 CAS(state 0→1) 抢一次，
    抢到直接获得，抢不到再进同步队列排队。优点：吞吐量大，减少 park/unpark。缺点：可能插队饥饿。
  - 公平（FairSync）：每次 tryAcquire 前必须判断 hasQueuedPredecessors()，
    即同步队列中除 head 外是否有更早的等待线程（有就排队，不抢）。优点：绝对公平。缺点：吞吐量略低。

Q8：AQS 为什么是 CLH 变体，为什么要虚拟 head 节点？
A：虚拟 head（哨兵节点）简化逻辑：
   - 如果没有 head，第一个入队节点还要和"当前持有锁的非队列线程"竞争
   - 有了哨兵 head，规则统一：**只有 head.next 才有资格抢锁**
   - 空队列时 head == tail == null → 第一个线程入队时 enq：
     compareAndSetHead(new Node()) → tail = head，此时 head 是哨兵，再 CAS 把 node 挂 tail.next
```

---

### 2.1.6 线程池源码级理解

```
Q1：线程池 7 大参数？拒绝策略？
```java
public ThreadPoolExecutor(
    int corePoolSize,              // 核心线程数（长期保留，不回收）
    int maximumPoolSize,           // 最大线程数
    long keepAliveTime,            // 非核心线程空闲超时存活时间
    TimeUnit unit,                 // 时间单位
    BlockingQueue<Runnable> workQueue,  // 任务等待队列
    ThreadFactory threadFactory,          // 创建线程工厂（默认 DefaultThreadFactory，线程名 pool-N-thread-M）
    RejectedExecutionHandler handler      // 拒绝策略：队列+最大线程都满了怎么办
) {}

// 4 种拒绝策略：
// AbortPolicy（默认）    → 抛 RejectedExecutionException
// CallerRunsPolicy       → 调用者所在线程自己执行（降级，不丢任务）
// DiscardPolicy          → 直接丢弃新任务
// DiscardOldestPolicy    → 丢弃队列头部最老任务，重新提交新任务
```

Q2：execute(Runnable) 3 步提交流程？
```
提交任务 command：
1. if 当前 worker 数 < corePoolSize → addWorker(command, true) 创建核心线程
   · 创建成功 → 直接执行 command → 结束
   · 创建失败（并发下其他线程也在创建）→ 往下走
2. if 线程池还在 RUNNING 且 workQueue.offer(command) 入队成功
   · 双重检查：
     · 若线程池已非 RUNNING → 回滚 remove + reject
     · 若当前 worker 数 == 0（核心线程都没了，比如 allowCoreThreadTimeOut）
       → addWorker(null, false) 补一个救急线程处理队列
   · 结束
3. if 入队失败（队列满了）→ addWorker(command, false) 尝试创建非核心线程
   · 成功 → 执行 command
   · 失败（已经到 maxPoolSize 或 SHUTDOWN）→ reject(command) 调用拒绝策略
```

Q3：Worker 结构？为什么 Worker 继承 AQS + Runnable？
```java
// Worker 是 AQS 简化版独占锁（不支持重入）
private final class Worker
    extends AbstractQueuedSynchronizer
    implements Runnable {
    final Thread thread;         // 工作线程（ThreadFactory 创建）
    Runnable firstTask;          // 初始任务（可 null，null 就从队列取）
    volatile long completedTasks; // 完成任务计数

    // 构造：new Worker(firstTask) → state=-1（初始禁止被中断，runWorker 时才 state=0 允许）
    Worker(Runnable firstTask) { setState(-1); this.firstTask = firstTask;
        this.thread = getThreadFactory().newThread(this); }

    public void run() { runWorker(this); }
    // 简化版 AQS 锁：state=0 未占，state=1 已占（tryAcquire 是 CAS，tryRelease 直接 set）
    // 不重入原因：worker 运行中已经持锁，防止 setCorePoolSize/shutdownNow 等中断重复操作
}
```

Q4：runWorker 主循环？getTask 从队列取任务 + 回收线程逻辑？
```java
final void runWorker(Worker w) {
    Thread wt = Thread.currentThread();
    Runnable task = w.firstTask; w.firstTask = null;
    w.unlock(); // state 从 -1 设为 0，允许中断（Worker 构造时 -1 防止被中断）
    boolean completedAbruptly = true;
    try {
        while (task != null || (task = getTask()) != null) {  // 核心循环
            w.lock();  // worker 独占锁：标记"正在执行任务"，shutdown 时不会中断运行中 worker
            // 检查 SHUTDOWN 且线程池 stop → 中断当前线程
            beforeExecute(wt, task);  // 钩子方法，可扩展
            Throwable thrown = null;
            try { task.run(); } catch (Throwable x) { thrown = x; throw x; }
            finally { afterExecute(task, thrown); ++w.completedTasks; w.unlock(); }
            task = null;
        }
        completedAbruptly = false;
    } finally {
        processWorkerExit(w, completedAbruptly);
        // 退出处理：如果是执行中抛异常（abruptly=true），必须 addWorker 补一个 worker
        //                   正常退出（getTask 返回 null）说明线程超回收条件，减少 worker
    }
}

// getTask 核心：4 种情况返回 null（触发 worker 被回收）
private Runnable getTask() {
    boolean timedOut = false;
    for (;;) {
        int c = ctl.get(); int rs = runStateOf(c);

        // ✅ 情况 1：STOP/TIDYING/TERMINATED 或 (SHUTDOWN 且队列空) → 返回 null，worker 回收
        if (rs >= SHUTDOWN && (rs >= STOP || workQueue.isEmpty())) { decrementWorkerCount(); return null; }

        int wc = workerCountOf(c);
        // allowCoreThreadTimeOut 或 当前 worker 超过核心数 → 允许超时回收
        boolean timed = allowCoreThreadTimeOut || wc > corePoolSize;

        // ✅ 情况 2：worker 超 maxPoolSize（可能 setMaximumPoolSize 调小）
        //    或 (timed && 上次 poll 超时 timedOut) 且 (队列空或还有别线程兜底)
        if ((wc > maximumPoolSize || (timed && timedOut))
            && (wc > 1 || workQueue.isEmpty())) {
            if (compareAndDecrementWorkerCount(c)) return null;  // CAS 减数量失败 continue
            continue;
        }

        try {
            Runnable r = timed ?
                workQueue.poll(keepAliveTime, TimeUnit.NANOSECONDS) : // 非核心/可超时：poll 限时取
                workQueue.take();                                      // 核心：take 死等
            if (r != null) return r;
            timedOut = true;  // 限时 poll 返回 null → 标记超时，下次循环走 情况 2
        } catch (InterruptedException retry) {
            timedOut = false;
        }
    }
}
```

Q5：为什么不推荐 Executors 自带线程池？
```java
// Executors 4 个工厂方法的缺陷（《阿里巴巴开发手册》强制禁用）：

// 1) FixedThreadPool / SingleThreadPool
new ThreadPoolExecutor(nThreads, nThreads, 0L, TimeUnit.MILLISECONDS,
    new LinkedBlockingQueue<Runnable>());  // ❌ 队列容量 = Integer.MAX_VALUE
    // 问题：队列无界！任务堆积 → OOM

// 2) CachedThreadPool
new ThreadPoolExecutor(0, Integer.MAX_VALUE, 60L, TimeUnit.SECONDS,
    new SynchronousQueue<Runnable>());  // ❌ maxPoolSize = Integer.MAX_VALUE
    // 问题：高并发下无限制创建 10w+ 线程 → OOM / CPU 100%（线程切换开销）

// 3) ScheduledThreadPool / SingleScheduledExecutor
    // DelayedWorkQueue 初始容量 16，扩容无限，同上 OOM 风险

// ✅ 正确做法：显式 new ThreadPoolExecutor，自定义参数
int core = Runtime.getRuntime().availableProcessors();
ThreadPoolExecutor pool = new ThreadPoolExecutor(
    core, core * 2 + 1, 60L, TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(500),
    new ThreadFactoryBuilder().setNameFormat("my-pool-%d").build(), // Guava
    new ThreadPoolExecutor.CallerRunsPolicy()
);
```

Q6：如何优雅关闭线程池？
```java
// 1. shutdown()：温和关闭
pool.shutdown();
//  - 修改状态 SHUTDOWN：不接受新任务，已在队列的任务继续执行完
//  - 中断所有空闲 worker（tryTerminate 尝试终止）

// 2. shutdownNow()：暴力关闭
List<Runnable> pending = pool.shutdownNow();
//  - 修改状态 STOP：不接受新任务，队列中未执行的任务返回 List<Runnable>
//  - 中断 ALL worker（运行中的也中断，任务抛出 InterruptedException）

// 3. 优雅关闭模板（推荐）：
public void gracefulShutdown(ExecutorService pool, int timeoutSec) {
    pool.shutdown();                                                     // 1. 温和停止新任务
    try {
        if (!pool.awaitTermination(timeoutSec, TimeUnit.SECONDS)) {     // 2. 等 timeout 内完成
            List<Runnable> drop = pool.shutdownNow();                   // 3. 超时就强制
            log.warn("超时强制关闭，丢弃任务数:{}", drop.size());
            if (!pool.awaitTermination(5, TimeUnit.SECONDS))            // 4. 再等强制收尾
                log.error("线程池仍未完全终止！");
        }
    } catch (InterruptedException e) {
        pool.shutdownNow();                                              // 当前线程被中断也强制
        Thread.currentThread().interrupt();                             // 恢复中断标记
    }
}
```

Q7：核心参数如何设置（CPU 密集 vs IO 密集）？
```
① CPU 密集型（大量计算，少等待）
  corePoolSize = CPU 核心数 + 1   （+1 是防止一个线程偶然缺页中断）
  maxPoolSize = corePoolSize      （多了反而线程切换慢）
  队列：ArrayBlockingQueue(较小)
  例：8 核 → 9 核心 / 9 最大

② IO 密集型（DB/RPC 调用多，大部分时间阻塞等待）
  核心公式：线程数 = CPU核数 * CPU利用率 * (1 + 等待时间/计算时间)
  简化经验值：corePoolSize = CPU 核心数 * 2
              maxPoolSize = CPU 核心数 * 5 ~ 20（看 IO 阻塞比）
  例：8 核，DB 查询等待 500ms，计算 50ms → 10*(1+500/50) ≈ 110 线程
  队列：LinkedBlockingQueue(有容量上限，如 500~2000)，别无界

③ 混合场景
  建议拆为两个独立线程池：CPU 型 + IO 型，各自独立配置互不影响

最终：不要拍脑袋，一定要做"压测调参"！
  - 关键指标：队列积压量、活跃线程数、任务完成数、任务平均 RT、拒绝次数
  - 监控：Spring Boot Actuator / Micrometer 暴露指标，Prometheus 观测
```

---

## 2.2 JVM：从原理到调优实战

### 2.2.1 JVM 内存模型深入

```
运行时数据区：
┌───────────────────────────────────────────────────────────────┐
│ 【线程私有】                                                    │
│  ① 程序计数器（PC Register）                                     │
│    - 当前线程执行的字节码行号指示器，唯一一个 JVM 规范没规定 OOM 的区│
│    - 执行 Java 方法存字节码地址，执行 Native 方法空                │
│  ② Java 虚拟机栈（VM Stack）                                      │
│    - 每个方法调用创建一个栈帧 StackFrame：                          │
│      ├ 局部变量表：基本类型 + 对象引用（reference）+ returnAddress   │
│      ├ 操作数栈：字节码指令操作的临时栈（i++ 压栈出栈）               │
│      ├ 动态链接：当前方法指向运行时常量池的方法引用（invokevirtual 解析）│
│      └ 方法返回地址：方法退出后下一条指令地址                         │
│    - 栈深度溢出 → StackOverflowError（递归无出口）                    │
│    - 栈扩展失败 → OutOfMemoryError（一般 HotSpot 不支持动态扩展）     │
│    - 参数 -Xss 每个线程栈大小（默认 64 位 JDK8 Linux 1024KB = 1M）     │
│  ③ 本地方法栈（Native Method Stack）                                │
│    - 为 Native 方法服务（HotSpot 与 VM Stack 合二为一）               │
│    - 异常同 StackOverflowError / OOM                                 │
├───────────────────────────────────────────────────────────────┤
│ 【线程共享】                                                      │
│  ④ Java 堆（Heap）                                               │
│    - 最大一块，new 对象 / 数组都在这里，GC 主战场                    │
│    - 分代：Young(Eden + S0 + S1 默认 8:1:1)  /  Old              │
│      Eden 满 → YGC（复制算法 Eden → S0，或 Eden+S0 存活 → S1）      │
│      多次存活超过 15 次 → 晋升 Old；大对象直接 Old                   │
│    - 参数：-Xms 初始堆 / -Xmx 最大堆（建议设一样，避免动态扩容抖动）    │
│           -Xmn 年轻代大小 / -XX:NewRatio=2 Old:Young = 2:1          │
│           -XX:SurvivorRatio=8 Eden:S0:S1 = 8:1:1                     │
│  ⑤ 方法区（Method Area → JDK7/8 演进）                               │
│    · JDK7：永久代（PermGen），堆中，-XX:PermSize / -XX:MaxPermSize    │
│    · JDK8+：元空间（Metaspace），本地内存，不连续                  │
│           -XX:MetaspaceSize 初始触发 Full GC 阈值 21MB             │
│           -XX:MaxMetaspaceSize 默认无上限（可能吃满机器内存！必须设！）│
│    - 存储：类元信息（字段、方法、字节码）、常量、静态变量（JDK7后移堆） │
│  ⑥ 运行时常量池（Runtime Constant Pool）                             │
│    - 方法区的一部分，Class 常量池表运行期加载后                      │
│    - 字面量 + 符号引用 → 直接引用（解析阶段）                         │
│    - String.intern() 入池                                            │
│  ⑦ 字符串常量池（StringTable）                                       │
│    - JDK6：方法区中；JDK7+：堆中，是一个哈希表（类似 HashMap）          │
│    - new String("a") 创建 1~2 个对象：常量池有则只在堆 new；无则在 CP 入1个+堆 new1个│
├───────────────────────────────────────────────────────────────┤
│ 【其他】                                                          │
│  ⑧ 直接内存（Direct Memory / NIO）                                 │
│    - Native 堆外内存，Unsafe.allocateMemory / ByteBuffer.allocateDirect │
│    - 不经过 JVM 内存管理，省一次用户态→内核态拷贝（零拷贝）            │
│    - -XX:MaxDirectMemorySize 默认 = -Xmx（未配置时）                 │
│    - 达到阈值触发 Full GC 清理 Cleaner → Unsafe.freeMemory          │
└───────────────────────────────────────────────────────────────┘

容易混淆的 3 个"常量池"：
  Class 文件常量池：.class 文件里的静态表，类加载时解析
  运行时常量池：方法区（元空间）里，Class 加载后动态内容
  字符串常量池：堆里的 HashTable，只存字符串字面量
```

### 2.2.2 垃圾回收器底层原理与对比

```
【垃圾判断算法】
  ① 引用计数法（Python / COM）：对象头引用计数 +1/-1，计数 0 回收
     × 循环引用问题：A↔B 互相引用，计数都=1，永远不回收
  ② 可达性分析（根搜索，Java JVM 采用）：从 GC Roots 往下引用链走，
     走不到的对象就是可回收的
        GC Roots 包括：
          · VM Stack 中局部变量表引用的对象
          · 方法区中静态变量 / 常量引用的对象
          · Native 方法栈 JNI 引用的对象
          · synchronized 锁持有的对象
          · JVM 内部引用：Class 对象、异常对象、系统类加载器等

4 种引用强度（强→弱依次减弱）：
  ① 强引用 Object o = new Object(); 永不回收
  ② 软引用 SoftReference：内存不足（OOM前）才回收，适合缓存
  ③ 弱引用 WeakReference：下次 GC 必回收（ThreadLocal Entry.key）
  ④ 虚引用 PhantomReference：不影响生命周期，唯一用途：对象被 GC 时收到系统通知（管理堆外内存）

Finalizer 机制：
  对象不可达后，先判断是否覆盖 finalize() & 未被执行过 → 放入 F-Queue，
  由低优先级 Finalizer 线程执行 finalize()（执行前对象可在 finalize 中自救=重新赋值引用链）
  但只能自救一次（下次不会再进 F-Queue）。⚠️ finalize 不推荐（Finalizer 线程慢、不确定、可能 OOM）

【4 种 GC 算法】
  ① 标记-清除 Mark-Sweep：先标记可达，再清除不可达
     × 碎片多（下次分配大对象找不到连续空间提前 Full GC）
     ✅ 不需要移动对象，效率高
  ② 复制 Copying：内存分两块，存活对象全复制到另一半，前半清光
     ✅ 无碎片，连续分配（TLAB Bump-pointer）
     × 浪费一半空间；存活对象多则复制慢
     → 适合年轻代：98% 朝生夕死，存活少
  ③ 标记-整理 Mark-Compact：标记后，把存活对象向一端移动，边界外全清
     ✅ 无碎片，老年代适合（存活多）
     × 移动对象要更新所有引用，STW 时间更长
  ④ 分代收集：
     Young 用复制算法（对象存活率低），Old 用标记-清除 或 标记-整理

【7 款经典垃圾回收器连线】：
  新生代：Serial / ParNew / Parallel Scavenge
  老年代：Serial Old / Parallel Old / CMS
  整代（新+老）：G1 / ZGC / Shenandoah

【经典垃圾回收器对比】：
```

| 回收器 | 代 | 算法 | 线程 | 特点 | 适用场景 | STW |
|---|---|---|---|---|---|---|
| Serial | 新 | 复制 | 单 | 简单无交互开销 | 客户端 / 小堆（几十 MB） | 长 |
| Serial Old | 老 | 标记整理 | 单 | Serial 的老年代版；CMS 后备方案 | 同上 + CMS 失败兜底 | 长 |
| ParNew | 新 | 复制 | 多 | Serial 的多线程版，只有它能配合 CMS | 配合 CMS 老年代 | 中 |
| Parallel Scavenge | 新 | 复制 | 多 | 高吞吐量优先（代码执行时间 / (代码+GC)） | 后台计算任务 | 中 |
| Parallel Old | 老 | 标记整理 | 多 | 配合 Parallel Scavenge 吞吐优先组合 | 后台批处理 | 中 |
| CMS | 老 | 标记清除 | 多并发 | **低延迟**，用户线程与 GC 并发 | Web/响应型应用 JDK8 前主流 | **短 + 并发标记** |
| G1 | 整 | 复制+标记整理 | 多并发 | 分 Region（1~32M 2048 块），可预测停顿时间 | JDK9 默认，大堆（4G~64G） | **短（可控）** |
| ZGC | 整 | 标记整理 + 染色指针 | 并发 | **最大 STW < 1ms**，不分代（JDK21 分代） | 大内存（128G~）+ 超低延迟 JDK11+ | **<1ms** |
| Shenandoah | 整 |  Brooks 转发指针 | 并发 | 和 ZGC 类似，OpenJDK 开源 | 同上，红帽主导 JDK12+ | 超短 |

```
【CMS 完整 7 步流程（Concurrent Mark Sweep）】
  ① 初始标记 Initial Mark：STW，只标记 GC Roots 直接引用的对象（很快）
  ② 并发标记 Concurrent Mark：用户线程并行，从 GC Roots 往下全链标记
     · 期间漏标（三色标记：黑/灰/白）解决方案：增量更新 Incremental Update（黑→白 记录）
  ③ 重新标记 Remark：STW，修正②期间用户线程变动的引用（比①长，比②短得多）
  ④ 并发清除 Concurrent Sweep：用户线程并行，清除白色不可达
  ⑤ 重置线程状态 Reset
  CMS 问题：
    × 标记清除 → 老年代碎片多（Full GC 时退化成 Serial Old 单线程标记整理，STW 超长）
    × 并发阶段占用 CPU 线程（默认 (核数+3)/4 条），吞吐下降
    × 浮动垃圾：并发清除期间新产生的垃圾只能下次清理
    × 老年代到阈值（默认 68%）必须开始 CMS，等不及满了 → 触发 Serial Old 巨长 STW

【G1 核心思想（Garbage First）】
  - 物理不分代，逻辑分代：Region 2048 块，每块 1~32M（2 的幂）
    每块可能是 Eden / Survivor / Old / Humongous（大对象 > 半 Region）
  - 可预测的停顿：-XX:MaxGCPauseMillis=200（默认 200ms）
    G1 后台维护每个 Region 回收价值（回收得到空间 / 所需时间），
    每次只挑性价比最高的 Region 组成 CSet（Collection Set）回收，
    用复制算法，把 CSet 中存活对象拷贝到空 Region
  - Remembered Set（每个 Region 一个 Hash 表）：记录 Old→Young 跨 Region 引用卡表
    避免 YGC 扫全老年代
  - G1 4 种模式：
    ① Young GC：Eden 满，Young Region 复制到 Survivor/Old
    ② Mixed GC：老年代 IHOP 阈值（默认堆 45% 老年代），回收 Young + 部分 Old Region
    ③ Full GC：Mixed GC 回收速度 < 分配速度，退化到单线程 Full GC（要避免！）
    ④ Humongous：超大对象直接老年代，特殊处理

【ZGC 关键技术】
  - 着色指针 Colored Pointers（64 位地址高几位存标记位）
    读屏障 + 指针染色，GC 移动对象时，读操作自跳转转发表，完全并发
  - 负载屏障 Load Barrier：访问对象前检查标记，自修复地址
  - 不分代时 4 步：STW 始标 → 并发标记/处理 → STW 再标 → 并发迁移/重映射
  - JDK21 分代 ZGC：ZGC Generational，分 Young/Old 代，吞吐大幅提升
```

### 2.2.3 类加载机制与双亲委派

```
【类加载 5 个步骤（生命周期 7 步：加载→验证→准备→解析→初始化→使用→卸载）】
  1. 加载 Loading：
     · 通过全限定名获取类的二进制字节流（class 文件 / 网络 / 动态生成 ASM）
     · 字节流 → 方法区（元空间）的运行时数据结构
     · 堆中生成 java.lang.Class 对象（访问入口）
  2. 验证 Verification：确保 Class 文件字节流符合 JVM 规范（魔数 0xCAFEBABE / 版本 / 语义 / 符号引用）
  3. 准备 Preparation：为静态变量分配内存并赋"零值"
     · static int a = 123 → 准备阶段 a=0，初始化阶段才 a=123
     · static final int b = 456（ConstantValue 属性）→ 准备阶段直接 b=456
  4. 解析 Resolution：符号引用 → 直接引用（把 "com.foo.A" 换成实际内存地址 / 偏移量）
     · 类/接口、字段、类方法、接口方法、方法类型/句柄/调用点
  5. 初始化 Initialization：执行 <clinit>() 方法（编译器自动收集 static{} + static 变量赋值）
     · JVM 保证 <clinit>() 线程安全加锁（多线程初始化同一个类只有一个执行，其他阻塞）
     · 触发初始化的 5 种场景（有且仅有，称为"主动引用"）：
       ① new、getstatic、putstatic、invokestatic（除 final 常量）
       ② java.lang.reflect 反射调用
       ③ 初始化子类时先触发父类初始化（接口不一定）
       ④ 启动主类（main 方法）
       ⑤ JDK7 MethodHandle 解析得到 REF_getStatic/putStatic/invokeStatic 且类未初始化

【双亲委派模型 Parents Delegation Model】
  三层类加载器（JDK8+）：
    ┌ Bootstrap ClassLoader（C++ 实现，非 ClassLoader 子类）
    │   加载 JAVA_HOME/jre/lib 下的核心类（rt.jar、resources.jar 等）
    │   -Dsun.boot.class.path 指定
    ├ Platform ClassLoader（JDK9+，取代 Extension ClassLoader）
    │   JDK9+ 平台模块；JDK8 ExtClassLoader 加载 jre/lib/ext 下扩展包
    └ Application ClassLoader / System ClassLoader
        加载用户 classpath 下的类（我们写的类默认它加载）
        再下是自定义 ClassLoader（热部署、加密解密、跨项目隔离）

  委派流程（ClassLoader.loadClass()）：
    ① 先 findLoadedClass(name) 看是否已经加载过
    ② 未加载过：委派 parent.loadClass(name)（递归）
       → 直到 Bootstrap（parent=null 就调启动加载器）
    ③ 上层都找不到 → 自己的 findClass(name) 去加载
  好处：
    · 安全：防止篡改核心类（自己写个 java.lang.String，Bootstrap 先加载了 rt.jar 的，不会用你写的）
    · 有序：避免重复加载（parent 已加载的 child 不用再加载）

【打破双亲委派的经典场景】：
  1) Tomcat 类加载器（WAR 包互相隔离 + 共享类）
     · 每个 WebAppClassLoader 先自己 WEB-INF/classes 找，找不到才委派父
     · 反向委派：要加载 Spring 等库交给 CommonClassLoader / SharedClassLoader
  2) SPI（Service Provider Interface）
     · DriverManager 需要加载数据库驱动（com.mysql.cj.jdbc.Driver）
       但启动加载器不认识 classpath 的厂商驱动
     · 解决方案：Thread.currentThread().getContextClassLoader()
       DriverManager 初始化通过"线程上下文类加载器"（通常是 AppClassLoader）绕过
       双亲委派，从上层反向加载下层类
  3) OSGi：模块化热部署，每个 Bundle 自己的 ClassLoader，网状互相委派
  4) 自定义：重写 loadClass() 不委派 parent，直接自己 findClass

【自定义类加载器】：
```java
public class MyClassLoader extends ClassLoader {
    @Override
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        byte[] bytes = loadClassBytes(name);  // 从加密文件/网络读字节
        return defineClass(name, bytes, 0, bytes.length);
    }
}
// 应用场景：热部署 / 代码加密防反编译 / 不同版本类隔离
```

### 2.2.4 OOM 排查与调优完整流程

```
常见 OOM 8 种：
  ① java.lang.OutOfMemoryError: Java heap space                  → 堆内存满
  ② java.lang.OutOfMemoryError: GC overhead limit exceeded        → GC 98% 时间回收不到 2% 堆
  ③ java.lang.OutOfMemoryError: Metaspace / PermGen space         → 元空间/永久代满（反射/动态类多）
  ④ java.lang.OutOfMemoryError: unable to create new native thread → 创建线程超 OS 限制
  ⑤ java.lang.OutOfMemoryError: Direct buffer memory              → NIO 堆外内存满
  ⑥ java.lang.OutOfMemoryError: Requested array size exceeds VM limit → 超大数组
  ⑦ java.lang.StackOverflowError （其实是 Error 不是 OOM，但常见）→ 递归太深
  ⑧ Out of Memory Error（JNI 层 native 分配失败）                 → C/C++ 层内存泄漏

完整排查 SOP：
  ① 第一反应：先加 JVM 参数，让 OOM 时自动 dump 堆快照（事后复盘必备）
     -XX:+HeapDumpOnOutOfMemoryError
     -XX:HeapDumpPath=/var/log/xxx.hprof
     -XX:OnOutOfMemoryError='jstack %p > /var/log/oom_threads.log'   （可选）
  ② 拿到 hprof 文件 → 用 Eclipse MAT (Memory Analyzer Tool) / JProfiler 分析
     · 查看：Histogram（类实例数 + 占用大小）
     · 查看：Dominator Tree（支配树：谁占内存最多，GC Roots 链找泄漏点）
     · 查看：Leak Suspects Report（MAT 自动分析疑似泄漏）
     · 常见泄漏：HashMap/ArrayList 无限增长、ThreadLocal 未 remove、缓存未淘汰、
                监听器未注销、大对象一次性入内存（如一次查全表 List）
  ③ 用 jmap（实时，慎用！会触发 Full GC STW）：
     jmap -heap <pid>        打印堆摘要（分代大小、使用率）
     jmap -histo:live <pid>  打印存活对象直方图（触发 Full GC）
     jmap -dump:live,format=b,file=heap.hprof <pid>  手动 dump
  ④ 配合 jstat（低侵入性，5 秒间隔看 GC 趋势）：
     jstat -gcutil <pid> 5000
     列：S0 S1 E O M CCS YGC YGCT FGC FGCT GCT
     关注：YGC 频率？每次 YGCT 多少？FGC 是不是频繁？Old 代是不是一直涨（泄漏）？
  ⑤ Arthas（线上神器，零侵入 Java Agent）：
     dashboard 总览（内存/GC/线程）
     heapdump / classloader（看动态类加载情况）
     profiler 火焰图（CPU 热点，也可找内存分配热点）

调优实操（举例：G1 GC）：
```bash
# 8 核 16G 机器，堆给 12G，G1 目标 150ms STW
java -Xms12g -Xmx12g                        # 堆 12G，Xms=Xmx 避免动态扩展
     -XX:+UseG1GC                             # 用 G1
     -XX:MaxGCPauseMillis=150                 # 停顿目标
     -XX:G1HeapRegionSize=8m                   # 2048 块，每块 8m（16G 堆 16m）
     -XX:InitiatingHeapOccupancyPercent=45    # 老年代 45% 触发 Mixed GC（默认 45）
     -XX:+ParallelRefProcEnabled               # 并行处理 Reference
     -XX:+HeapDumpOnOutOfMemoryError
     -XX:HeapDumpPath=/opt/logs/heap.hprof
     -Xloggc:/opt/logs/gc.log
     -XX:+PrintGCDetails -XX:+PrintGCDateStamps -XX:+PrintGCApplicationStoppedTime
```

---

## 2.3 Spring：核心流程源码级掌握

### 2.3.1 IOC 启动流程（refresh() 12 步）

> AbstractApplicationContext.refresh()，所有上下文（AnnotationConfigApplicationContext / ClassPathXmlApplicationContext / SpringBoot）都走它。
> 每一步高级面试都要讲清楚"干了什么 + 关键扩展点 + 自己写过什么扩展"。

```
┌ refresh() 12 步完整流程：
│
│ 1. prepareRefresh()          【刷新前准备】
│   ├── 设置启动日期、激活状态
│   ├── initPropertySources()  初始化属性资源（可覆盖：从配置文件/环境变量/注册中心取）
│   ├── getEnvironment().validateRequiredProperties()  校验必须存在的属性
│   └── 早期事件集合初始化
│
│ 2. obtainFreshBeanFactory()  【获取新的 BeanFactory】
│   ├── refreshBeanFactory()
│   │     · XML 方式：DefaultListableBeanFactory
│   │       解析 XML → BeanDefinition（DocumentReader、BeanDefinitionParser）
│   │     · 注解方式：GenericApplicationContext 直接返回已有的 Factory，
│   │       BeanDefinition 是在构造 context 时 register(componentClasses) 注册的
│   └── 返回 getBeanFactory()：拿到新鲜的 BeanFactory
│
│ 3. prepareBeanFactory(beanFactory)  【准备 BeanFactory，加通用组件】
│   ├── 类加载器、SpEL 解析器（#{}）、属性编辑器注册器（Spring 3.x 用）
│   ├── addBeanPostProcessor：ApplicationContextAwareProcessor（注入 Aware）
│   ├── ignoreDependencyInterface：忽略 Aware 回调接口（不自动装配）
│   ├── 特殊依赖自动注入：BeanFactory / ResourceLoader / ApplicationEventPublisher / ApplicationContext
│   └── 注册环境相关单例 bean：environment / systemProperties / systemEnvironment
│
│ 4. postProcessBeanFactory(beanFactory)   【空实现模板方法，子类覆盖扩展】
│   （AnnotationConfigServletWebServerApplicationContext 在这里加 ServletAwareProcessor 等）
│
│ 5. invokeBeanFactoryPostProcessors(beanFactory) 【最关键一步之一：执行 BFPP】
│   ├── BeanDefinitionRegistryPostProcessor extends BeanFactoryPostProcessor
│   │     · 先执行 PriorityOrdered 组 → Ordered 组 → 无排序组
│   │     · ★★★ ConfigurationClassPostProcessor：
│   │         解析 @Configuration 配置类
│   │           → @ComponentScan 包扫描（asm 读 class 注解 → 生成 ScannedGenericBeanDefinition）
│   │           → @Bean 方法 → ConfigurationClassBeanDefinitionReader 注册
│   │           → @Import（ImportSelector / ImportBeanDefinitionRegistrar / 普通类）
│   │           → @ImportResource 引入 XML
│   │           → @PropertySource 加载 @Value 用的 properties
│   │         处理完后，所有"配置的 bean"全变为 BeanDefinition
│   ├── 再执行普通 BeanFactoryPostProcessor（相同顺序：PriorityOrdered/Ordered/无排序）
│   │     · 典型：PropertySourcesPlaceholderConfigurer 解析 ${} 占位符
│   │     · 自定义：修改 BeanDefinition（如把 scope 改了、加属性值）
│
│ 6. registerBeanPostProcessors(beanFactory) 【注册 BeanPostProcessor，不执行，只是注册进 Factory】
│   顺序：PriorityOrdered → Ordered → 无排序 → 最后单独注册 MergedBeanDefinitionPostProcessor
│   （MergedBeanDefinitionPostProcessor：生命周期中@PostConstruct等需要，稍后第9步实例化时用）
│   典型 BPP：AutowiredAnnotationBeanPostProcessor（@Autowired @Value 注入）
│              CommonAnnotationBeanPostProcessor（@Resource @PostConstruct @PreDestroy）
│              AnnotationAwareAspectJAutoProxyCreator（AOP 自动代理，InstantiationAwareBeanPostProcessor）
│
│ 7. initMessageSource()        【初始化国际化资源】
│
│ 8. initApplicationEventMulticaster()  【初始化事件广播器（多播器）】
│   用户可以自定义名字 applicationEventMulticaster 的 bean，覆盖默认 SimpleApplicationEventMulticaster
│
│ 9. onRefresh()                【子类钩子】SpringBoot web 场景在此创建内嵌 Tomcat！
│   ServletWebServerApplicationContext.onRefresh() → createWebServer()
│   → ServletWebServerFactory.getWebServer(ServletContextInitializer initializers) → Tomcat.start()
│
│ 10. registerListeners()       【注册事件监听器】
│    · 先从 BeanFactory 拿 ApplicationListener 类型，加到多播器集合
│    · 广播早期事件（之前 prepareRefresh 暂存的）
│
│ 11. finishBeanFactoryInitialization(beanFactory) 【★★★ Bean 实例化！！】
│    ├── beanFactory.setConversionService（类型转换器，String→Date 之类）
│    ├── registerDefaultEditableValues（@Value 里的 ${} 支持）
│    ├── LoadTimeWeaverAwareProcessor 注册
│    ├── freezeConfiguration()：冻结 BeanDefinition（实例化阶段不能再改 BD）
│    └── ★★★ beanFactory.preInstantiateSingletons() 实例化所有非懒加载的单例
│        遍历所有 beanName → getBean(beanName) → doGetBean → createBean（见下 2.3.2 生命周期）
│        最后再遍历 SmartInitializingSingleton 的 afterSingletonsInstantiated()
│
│ 12. finishRefresh()           【收尾 + 发布 ContextRefreshedEvent】
│    ├── clearResourceCaches
│    ├── initLifecycleProcessor（生命周期处理器，管理 Lifecycle Bean 的 start/stop）
│    ├── getLifecycleProcessor().onRefresh()  → 启动所有 Lifecycle Bean (SmartLifecycle 自动 start)
│    ├── publishEvent(new ContextRefreshedEvent(this))
│    └── LiveBeansView.registerApplicationContext（JMX MBean，可观察）
└
```

### 2.3.2 Bean 生命周期 + 扩展点时序（10+ 步，按执行顺序）

```
doGetBean()
  ① 处理 FactoryBean（beanName 前缀 &）
  ② 先 getSingleton(beanName) 从一/二/三级缓存找（解决循环依赖，见 2.3.3）
  ③ 没找到 → 判断当前是否有 prototype 正在创建的循环依赖（有直接抛）
  ④ parentBeanFactory 先查父容器有没有
  ⑤ getMergedLocalBeanDefinition() 合并父 BD 和子 BD
  ⑥ depends-on 依赖的 Bean 先递归 getBean 创建
  ⑦ 按 scope 创建：
     · singleton → createBean + getSingleton(beanName, ObjectFactory)（锁 singletonObjects 放一级缓存）
     · prototype → 直接 createBean（每次 new）
     · 其他 scope（request/session/websocket）→ scope.get(name, ObjectFactory)

【★★ createBean() 生命周期完整时序】：
  AbstractAutowireCapableBeanFactory.createBean()

  【一、实例化前阶段（对象还没 new）】
  1. resolveBeforeInstantiation(beanName, mbd)
     → 遍历 InstantiationAwareBeanPostProcessor.postProcessBeforeInstantiation(beanClass, beanName)
        一旦某个 IABPP 返回非 null 对象（AOP 可能提前返回代理）→ 直接跳第 9 步 postProcessAfterInitialization

  → 没被拦截，走真正实例化
  【二、实例化阶段（对象创建出来，属性还没注入）】
  2. doCreateBean 中 createBeanInstance(beanName, mbd, args)
     → ① 推断构造函数：SmartInstantiationAwareBeanPostProcessor.determineCandidateConstructors
        （@Autowired 构造函数）
     → ② 策略实例化：SimpleInstantiationStrategy
        · 有 @Lookup 方法 → CGLIB 子类重写
        · 无 lookup → 反射 Constructor.newInstance()
     → 此时得到一个"半初始化对象"（字段全为零值，属性还没注入）
     → ③ 如果是单例且 allowCircularReferences && 当前 bean 正在创建中
        addSingletonFactory(beanName, new ObjectFactory())：放入第三级缓存 singletonFactories
        · ObjectFactory.getObject() → getEarlyBeanReference 调 SmartIABPP
        · AnnotationAwareAspectJAutoProxyCreator 在这里返回 AOP 代理（循环依赖需要提前代理）
  3. applyMergedBeanDefinitionPostProcessors(mbd, beanType, beanName)
     → MergedBeanDefinitionPostProcessor.postProcessMergedBeanDefinition
       （CommonAnnotationBeanPostProcessor 这里扫描 @PostConstruct / @PreDestroy 方法缓存）

  【三、属性注入阶段（populateBean）】
  4. InstantiationAwareBeanPostProcessor.postProcessAfterInstantiation(bw.getWrappedInstance(), beanName)
     返回 false → 跳过属性注入（高级扩展点）
  5. postProcessProperties(pvs, bw.getWrappedInstance(), beanName) 【★ 注入点扫描 + 注入！】
     · AutowiredAnnotationBeanPostProcessor：扫描 @Autowired / @Value 字段和方法
       → InjectionMetadata.inject → 通过 beanFactory.resolveDependency() 按类型/名称找被依赖的 Bean
       · resolveDependency 中如果依赖类型是 List/Map/Array 会一次性注入同类型多个 Bean
     · CommonAnnotationBeanPostProcessor：扫描 @Resource 按名称注入（JSR 250）
  6. applyPropertyValues：把 pvs（XML/注解解析的属性值）set 进 BeanWrapper（反射 setXxx）

  【四、初始化阶段（initializeBean）】
  7. invokeAwareMethods：*Aware 回调（按顺序）
     BeanNameAware.setBeanName → BeanClassLoaderAware → BeanFactoryAware.setBeanFactory
     （ApplicationContextAware 是在第 6 步注册的 ApplicationContextAwareProcessor.postProcessBeforeInitialization 里执行）
  8. applyBeanPostProcessorsBeforeInitialization(wrappedBean, beanName)
     → BeanPostProcessor.postProcessBeforeInitialization
       典型：CommonAnnotationBeanPostProcessor 执行 @PostConstruct 方法
             InitDestroyAnnotationBeanPostProcessor（@PostConstruct）
  9. invokeInitMethods：
     → ① 实现 InitializingBean 的 bean 执行 afterPropertiesSet()
     → ② 执行 <bean init-method=""> / @Bean(initMethod = "") 自定义初始化
  10. applyBeanPostProcessorsAfterInitialization(wrappedBean, beanName)
      → BeanPostProcessor.postProcessAfterInitialization  【★ AOP 代理创建！】
        AnnotationAwareAspectJAutoProxyCreator：
          → wrapIfNecessary(bean, beanName, cacheKey)
          → 获取切面（Advisor：Pointcut + Advice）、排序
          → createAopProxy：接口用 JdkDynamicAopProxy，否则 ObjenesisCglibAopProxy
        循环依赖的 Bean 因为第 2 步已经提前代理过，这里直接返回原引用

  【五、销毁阶段（容器 close / registerShutdownHook）】
  11. 注册 DisposableBeanAdapter（销毁适配器）到 disposableBeans 哈希表
      销毁时按序：
      @PreDestroy（CommonAnnotationBeanPostProcessor）
        → DisposableBean.destroy()
        → destroy-method / @Bean(destroyMethod = "")

【扩展点总结表格（面试按顺序背）】：
  执行时机              接口 + 方法                                    典型应用
  ─────────────────────────────────────────────────────────────────────────────────
  1. 解析 BD 前         BeanDefinitionRegistryPostProcessor.postProcessBeanDefinitionRegistry   自定义 Bean 扫描、ConfigurationClassPostProcessor
  2. BD 解析后          BeanFactoryPostProcessor.postProcessBeanFactory                      修改 BD 值（PropertySourcesPlaceholderConfigurer）
  3. 实例化前           InstantiationAwareBeanPostProcessor.postProcessBeforeInstantiation    提前返回代理对象
  4. 实例化后           MergedBeanDefinitionPostProcessor.postProcessMergedBeanDefinition     扫描生命周期注解缓存
  5. 属性注入前（是否跳过）  IABPP.postProcessAfterInstantiation                                自定义属性注入流程开关
  6. 属性注入           IABPP.postProcessProperties / postProcessPropertyValues               @Autowired @Resource @Value 注入
  7. Aware 回调         BeanNameAware / BeanFactoryAware / ApplicationContextAware            获得上下文/工厂引用
  8. 初始化前           BeanPostProcessor.postProcessBeforeInitialization                      @PostConstruct
  9. 初始化             InitializingBean.afterPropertiesSet / init-method                     自定义初始化逻辑
  10. 初始化后          BeanPostProcessor.postProcessAfterInitialization                       【★ AOP 代理创建】、事务代理、自定义包装
  11. 销毁前            @PreDestroy / DisposableBean.destroy / destroy-method                  资源释放
```

### 2.3.3 循环依赖 + 三级缓存

```
什么是循环依赖？
  A 依赖 B，B 又依赖 A（setter 注入）
  构造函数注入：A(B b) + B(A a) → 无解（A 还没 new 出来就要 B，B 反过来要 A）→ 直接抛 BeanCurrentlyInCreationException

三级缓存是什么？
  DefaultSingletonBeanRegistry：
    · singletonObjects（一级，Map<String, Object>）：完整 Bean（已走完实例化→注入→初始化）
    · earlySingletonObjects（二级，Map<String, Object>）：早期 Bean（刚 new，半初始化，没注入没初始化）
    · singletonFactories（三级，Map<String, ObjectFactory<?>>）：ObjectFactory 函数式接口，Lambda

【解决 A ↔ B 循环依赖的完整时序】：
 1. 容器启动，开始创建 A
    - doGetBean(A) → getSingleton(A) 三级都空
    - beforeSingletonCreation：singletonsCurrentlyInCreation.add("A")（标记 A 正在创建）
    - createBeanInstance(A)：反射 new A() → 得到 A@123（半初始化，b字段=null）
    - addSingletonFactory(A, ()→getEarlyBeanReference(A)) → 放入第三级缓存 singletonFactories
 2. populateBean(A)：发现 A 依赖 B → resolveDependency → getBean(B)
 3. 开始创建 B
    - getSingleton(B) 空
    - singletonsCurrentlyInCreation.add("B")
    - createBeanInstance(B) → new B() → B@456（半初始化，a字段=null）
    - addSingletonFactory(B, ObjectFactory) → 放入第三级
 4. populateBean(B)：发现 B 依赖 A → getBean(A)
 5. getSingleton(A)：
    - 一级 singletonObjects 没 → 二级 earlySingletonObjects 没
    - 三级 singletonFactories.get("A") 有！
    - ObjectFactory.getObject() → getEarlyBeanReference(A@123)：
       遍历 SmartInstantiationAwareBeanPostProcessor.getEarlyBeanReference
       → AnnotationAwareAspectJAutoProxyCreator：如果 A 需要 AOP，这里提前返回代理 A$Proxy@789
       → 如果 A 不需要 AOP，原封不动返回 A@123
    - 从 singletonFactories 移除，放入 earlySingletonObjects（二级，避免下次再调 ObjectFactory）
    - 返回（代理或原生）A 的引用给 B
 6. B 的 a 字段 = A（引用），B 完成注入+初始化+销毁注册
    - B 创建完毕 → removeSingletonCreation("B")
    - getSingleton 加入一级 singletonObjects，清除二三级
 7. 回到 A 第 2 步 resolveDependency，b 字段 = B，A 继续完成后续初始化
    - 这里注意：A 的"代理对象"在第 5 步已经创建，但当前执行的 A 初始化是用的 A 原生对象，
      最终 beanFactory.getBean("A") 返回的是二级里取到的代理对象。
 8. A 完全初始化完 → addSingleton 移到一级缓存

【常见面试题】：
Q1：为什么二级缓存不够，必须三级？
A：如果不用 AOP，二级缓存（半初始化对象引用）确实够用。但有 AOP 场景：
   循环依赖的 Bean 需要被提前代理（AOP 本来在 postProcessAfterInitialization 第 10 步做，
   但循环依赖需要第 2 步 new 完就产出代理）。getEarlyBeanReference 只能执行一次，
   如果每次 getSingleton 都 getEarlyBeanReference 会产出多个代理（不一致）。
   三级 ObjectFactory 的意义：**只有第一次需要时才计算（代理），之后从二级缓存拿**。

Q2：构造器注入的循环依赖为什么解决不了？
A：三级缓存要"实例化完成"才能放（addSingletonFactory 是 createBeanInstance 之后）。
   构造注入时，A 在"推断构造函数 → 执行构造函数"阶段就要 getBean(B)，
   此时 new A() 还没执行完，连第三级缓存都还没放进去，直接死循环检测到抛异常。

Q3：Prototype 作用域循环依赖？
A：Prototype Bean 根本不缓存，每次 new。检测到正在创建的集合里有（beforePrototypeCreation）
   → 直接抛 BeanCurrentlyInCreationException，无法解决。
```

### 2.3.4 AOP 源码解析

```
AOP 底层原理：动态代理
  · JDK 动态代理：只能代理接口，InvocationHandler + Proxy.newProxyInstance
  · CGLIB 动态代理：Enhancer 创建目标类子类，MethodInterceptor 拦截（final 类/方法不行）
  Spring 自动选择：有接口用 JDK，无接口用 CGLIB（可强制 spring.aop.proxy-target-class=true）

AOP 创建时机（2 处，二选一）：
  1. 普通情况：第 10 步初始化后 BeanPostProcessor.postProcessAfterInitialization
     AnnotationAwareAspectJAutoProxyCreator.wrapIfNecessary 创建代理
  2. 循环依赖提前代理：三级缓存 ObjectFactory.getObject() 时 getEarlyBeanReference
     同一 Bean 只会代理一次（earlyProxyReferences 缓存检查）

AOP 完整创建流程（wrapIfNecessary）：
  1. getAdvicesAndAdvisorsForBean() 获取切面
     · findCandidateAdvisors()：
       a) 从 BeanFactory 拿所有 Advisor 类型的 Bean（事务 BeanFactoryTransactionAttributeSourceAdvisor）
       b) @Aspect 类：ReflectiveAspectJAdvisorFactory.getAdvisors(factory)
          每个@Around/@Before/@After/@AfterReturning/@AfterThrowing 方法
          → 包装成 InstantiationModelAwarePointcutAdvisorImpl
          · 包含 AspectJExpressionPointcut（切点表达式匹配）+ AbstractAspectJAdvice（通知方法）
     · findAdvisorsThatCanApply：用 Pointcut 匹配目标类（类匹配 + 方法匹配）
     · sortAdvisors：按 @Order / Ordered 排序（@Around > @Before > @After > @AfterReturning > @AfterThrowing）
  2. 创建代理 createAopProxy()：
     · 有用户自定义接口 → JdkDynamicAopProxy
     · 否则 → ObjenesisCglibAopProxy（用 Objenesis 不用调构造）

AOP 调用流程（以 JdkDynamicAopProxy.invoke() 为例）：
  1. 被代理方法调用 → invoke(proxy, method, args)
  2. 获取拦截器链（advised.getInterceptorsAndDynamicInterceptionAdvice(method, targetClass)）
     · 每个 Advisor 适配 MethodInterceptor（@Before / @After / @Around）
  3. 拦截器链为空 → 直接反射调用 target.method
  4. 不为空 → new ReflectiveMethodInvocation(proxy, target, method, args, interceptors[])
     .proceed()：递归调用拦截器链
     · proceed 逻辑：index++，currentInterceptor = interceptors[index]
       每个 MethodInterceptor 再回调 mi.proceed()（责任链 + 递归）
       最终链末尾：invokeJoinpoint()（反射执行目标方法）

【事务 AOP】：
  启用 @EnableTransactionManagement
  → @Import(TransactionManagementConfigurationSelector)
  → 导入 AutoProxyRegistrar（注册 InfrastructureAdvisorAutoProxyCreator，AOP 自动代理）
     + ProxyTransactionManagementConfiguration
       · BeanFactoryTransactionAttributeSourceAdvisor（事务切面 Advisor）
         - TransactionAttributeSource：解析 @Transactional 注解属性
           (propagation / isolation / timeout / rollbackFor 等)
         - TransactionInterceptor：MethodInterceptor 实现
           invokeWithinTransaction()：
             · 获取事务属性 + TransactionManager
             · 不同传播行为（7 种）不同逻辑（required/requires_new/nested...）
             · 获得 Connection（事务同步管理器 bind 到当前线程 DataSourceUtils）
             · 执行 proceed()（业务代码）
             · try 正常 → commit；catch 异常 → 判断是否在 rollbackFor → rollback 或 commit
  @Transactional 失效 N 种场景（必背）：
    ① 方法非 public（Spring AOP 默认拦截 public，除非 AspectJ）
    ② 同一个类中方法互调（this 调用不走代理对象，事务切面没执行）
       解决：① 注入自己 @Autowired UserService self; self.xxx()
             ② AopContext.currentProxy() 拿代理 + @EnableAspectJAutoProxy(exposeProxy = true)
             ③ 拆成两个 Service
    ③ 异常类型不对：默认只回滚 RuntimeException / Error，checked Exception（IOException）不回滚
       解决：@Transactional(rollbackFor = Exception.class)
    ④ 自己 try-catch 吞了异常：事务切面感知不到异常
       解决：catch 后手动 throw；或 TransactionAspectSupport.currentTransactionStatus().setRollbackOnly()
    ⑤ 数据库引擎不支持事务（MyISAM 改 InnoDB）
    ⑥ 多数据源：事务管理器没选对 / 分布式事务场景用本地事务
```

### 2.3.5 Spring Boot 自动装配原理

```
启动入口：SpringApplication.run(MyApp.class, args)

【SpringApplication.run() 启动流程】：
  1. 构造 SpringApplication
     · 推断 WebApplicationType（Servlet / Reactive / None）
     · spring.factories 加载 BootstrapRegistryInitializer / ApplicationContextInitializer / ApplicationListener
     · 推断主类（MainMethodClass）：new RuntimeException().getStackTrace() 找 main() 所在类
  2. run(args)
     ① StopWatch 计时开始
     ② createBootstrapContext() 初始化启动上下文（BootstrapRegistry 存 Spring Cloud 启动前置组件）
     ③ getSpringFactoriesInstances(SpringApplicationRunListener.class) → EventPublishingRunListener
        listener.starting() 广播 ApplicationStartingEvent
     ④ prepareEnvironment：
        · 创建 ApplicationServletEnvironment（StandardEnvironment）
        · 依次加载：commandLineArgs → systemProperties → systemEnvironment
        · 关键：调用 listener.environmentPrepared() 广播 ApplicationEnvironmentPreparedEvent
           → 【★ ConfigFileApplicationListener / ConfigDataEnvironmentPostProcessor】
              加载 application.yml / application-{profile}.yml / application.properties
              从 spring.config.location 路径；profile 激活顺序激活
           → Nacos/Apollo 的配置中心也是这一步把远程配置塞 Environment
        · 绑定 spring.main.* 到 SpringApplication
     ⑤ configureIgnoreBeanInfo（系统属性）
     ⑥ prepareContext：
        · 创建 ApplicationContext（web 用 AnnotationConfigServletWebServerApplicationContext）
        · beanFactory 中注册 singleton: springApplicationArguments / springBootBanner
        · applyInitializers：调用 ApplicationContextInitializer.initialize(ctx)
        · listener.contextPrepared() 广播
        · load 源：把主类 MyApp.class（@SpringBootApplication 类）注册为 BeanDefinition
        · listener.contextLoaded()
     ⑦ refreshContext(context) → 【★ 内部就是调用前面讲的 AbstractApplicationContext.refresh() 12 步！】
        · 其中 onRefresh() 步骤：ServletWebServerApplicationContext 在这里启动内嵌 Tomcat/Jetty
     ⑧ afterRefresh：空扩展
     ⑨ StopWatch 停止（打印启动耗时秒数）
     ⑩ listener.started() → ApplicationStartedEvent
        · 调用 ApplicationRunner / CommandLineRunner 两个启动回调 run()
     ⑪ listener.ready() → ApplicationReadyEvent
     ⑫ 整个过程任何异常 → handleRunFailure + listener.failed()

【自动装配原理核心 @SpringBootApplication】是个组合注解（3 合 1）：
  ① @SpringBootConfiguration  → 就是 @Configuration（Spring 配置类）
  ② @EnableAutoConfiguration  → 【★ 自动装配的灵魂】
    └── @Import(AutoConfigurationImportSelector.class)
      → 这个 ImportSelector 实现 DeferredImportSelector（ConfigurationClassPostProcessor 解析 @Import 时调用）
      → selectImports(annotationMetadata)：
         · 【关键】SpringFactoriesLoader.loadFactoryNames(EnableAutoConfiguration.class, classLoader)
           读取所有 spring.factories 文件（CLASSPATH/META-INF/spring.factories，包括 starter 里的）
           拿到 org.springframework.boot.autoconfigure.EnableAutoConfiguration 对应的全限定类名列表
           （有 100+ 个：RedisAutoConfiguration、DataSourceAutoConfiguration、WebMvcAutoConfiguration...）
         · 去重、排除 exclude/excludeName 配置的类
         · getAutoConfigurationEntry → 返回要导入的配置类全名数组
  ③ @ComponentScan              → 包扫描：默认扫描主类所在包及其子包（@SpringBootApplication 注解定义的 basePackages 未指定则从主类所在包开始）
     → 对应 ClassPathBeanDefinitionScanner / ClassPathMapperScanner（MyBatis）

【@Conditional 条件装配家族（自动装配类几乎都带）】：
  - @ConditionalOnClass        classpath 有指定类才生效
  - @ConditionalOnMissingClass classpath 没指定类
  - @ConditionalOnBean         Spring 容器中有指定 Bean 才生效
  - @ConditionalOnMissingBean  容器中没有指定 Bean 才生效（给用户自定义覆盖的机会：你写了就用你的，没写用默认）
  - @ConditionalOnProperty     配置文件有指定属性值才生效（matchIfMissing 可选）
  - @ConditionalOnWebApplication / @ConditionalOnNotWebApplication
  - @ConditionalOnJava         JDK 版本
  - @ConditionalOnSingleCandidate 容器中某类型 Bean 只有一个（或有 @Primary）

【自定义一个 Spring Boot Starter 步骤】：
  需求：封装一个"短信发送 starter"，别人引入后自动装配 SmsService
  1. 新建 xxx-spring-boot-autoconfigure 模块：
     · 写 SmsProperties：@ConfigurationProperties(prefix = "sms") 封装配置项（url、ak、sk）
     · 写 SmsService（业务类，发送短信 API），构造函数注入 SmsProperties
     · 写 SmsAutoConfiguration：
       @Configuration(proxyBeanMethods = false)
       @EnableConfigurationProperties(SmsProperties.class)
       @ConditionalOnClass(SmsService.class)
       @ConditionalOnProperty(prefix = "sms", name = "enabled", havingValue = "true", matchIfMissing = true)
       public class SmsAutoConfiguration {
           @Bean
           @ConditionalOnMissingBean
           public SmsService smsService(SmsProperties p) { return new SmsService(p); }
       }
  2. 新建 xxx-spring-boot-starter 模块（空 pom），仅依赖 autoconfigure 模块（依赖隔离）
  3. 在 autoconfigure 的 resources/META-INF/spring.factories：
     org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
       com.xxx.sms.autoconfigure.SmsAutoConfiguration
  4. (可选) 额外配置 META-INF 元数据：spring-configuration-metadata.json 给 IDE 自动补全
  5. 别人引用 starter → 在 application.yml 填 sms.xxx → 注入 SmsService 直接用
```

---

## 2.4 并发编程：分布式场景

### 2.4.1 分布式锁深入

```
3 大分布式锁方案对比：
```

| 方案 | 实现原理 | 互斥性 | 安全性 | 性能 | 实现难度 | 适用 |
|---|---|---|---|---|---|---|
| **DB 悲观锁** | select ... for update 行锁（事务中） | ✅ | ✅ 事务提交释放 | ❌ 低（数据库瓶颈） | 低 | 并发量小、非核心 |
| **Redis** | SET key random NX PX 30000 + LUA 解锁 | ✅ 原子 CAS | ⚠️ 锁续期问题/RedLock | ✅ 高（内存） | 中 | 主流、绝大多数场景 |
| **ZooKeeper** | 临时顺序节点 + watcher（Curator InterProcessMutex） | ✅ | ✅ 临时节点会话断开自动删 | ❌ 中（zab 协议网络） | 中 | 一致性极高场景 |

【Redis 分布式锁 - 正确加锁】：
```java
// 正确：NX + PX + 唯一 value（不能"谁都能解锁"）
Boolean ok = redisTemplate.execute((RedisCallback<Boolean>) conn ->
    ((JedisCommands) conn.getNativeConnection()).set(key, uuid, "NX", "PX", 30000)
);
// Redis SET 命令（Redis 2.6.12+ 原生参数）：
// SET lock:order:123 unique-uuid-xxxx NX PX 30000
// 参数: NX=不存在才设, PX=毫秒过期, EX=秒过期
```
- 为什么 value 必须唯一？解锁时要"只能我解我自己加的锁"：
  A 加锁→业务慢→锁自动过期→B 获得锁→此时 A 执行完，A 如果 DEL key 就错删了 B 的锁

【Redis 分布式锁 - 正确解锁（LUA 保证 GET+比对+DEL 原子性！）】：
```java
String luaUnlock =
    "if redis.call('GET', KEYS[1]) == ARGV[1] then" +
    "    return redis.call('DEL', KEYS[1])" +
    "else return 0 end";
// 必须 LUA 脚本原子执行！否则：
// if (value.equals(GET key)) { DEL key } 之间可能发生 GC 停顿 → 锁过期+B拿到锁→A醒后误删
Long r = (Long) redisTemplate.execute(
    new DefaultRedisScript<>(luaUnlock, Long.class),
    Collections.singletonList(key),
    uuid);
```

【看门狗 Watchdog（Redisson 实现原理）】：
- 加锁后起后台定时线程（默认 lockWatchdogTimeout=30s，每 10s 续期）
- 如果业务还在跑（线程还持有锁）就不断 PEXPIRE 续命 30s
- 如果线程被 kill / 宕机 → watchdog 也挂 → 30s 后锁自动过期（不死锁）
- 可重入：Redisson 用 Hash 结构（key = threadId, field = 重入计数）
  HINCRBY lock_key thread_id 1  加锁 +1；HDEL 计数 0 时才 DEL key

【RedLock 红锁算法（Redis 官方提出解决单实例故障）】：
- N 个独立 Redis 节点（5 个推荐，互不依赖，非主从）
- 客户端步骤：
  ① 获取当前时间戳 t1
  ② 依次向 5 个节点加锁（相同 key + value，超时时间很短如 50ms，防止一个节点卡住）
  ③ 成功加锁节点数 ≥ N/2 + 1（即 3 个）且 总耗时 < 锁过期时间 → 加锁成功
     · 否则回滚所有已成功节点的 DEL 解锁
  ④ 业务执行期间锁自动过期时间 = 原过期 - 总耗时
  ⑤ 解锁：向所有节点发起 DEL（无论之前是否加锁成功，防止遗漏）
- 生产使用：Redisson 的 RedissonRedLock 封装（多数场景单 Redis+主从哨兵够了）

【Redis 锁 vs ZK 锁选型】：
  - Redis 性能好（10w QPS），实现简单，但是 CAP 里更偏 AP（极端情况下 master 挂、
    锁还没同步到 slave，主从切 slave 丢锁）。追求高吞吐、容忍极端极小概率出错。
  - ZK CP（CP ZAB 协议），临时节点 + 会话心跳，安全不丢锁，
    但性能一般（几千 QPS），实现复杂。追求极致一致性、金融支付级。

---

### 2.4.2 分布式事务选型与对比

```
理论基础：
  CAP（C 一致性 / A 可用性 / P 分区容错）：分布式系统 P 必选，C 和 A 二选一
  BASE（Basically Available 基本可用 / Soft state 软状态 / Eventually consistent 最终一致）
     → 大多数互联网不用强一致性（牺牲太大），接受"段时间不一致，最终一致"

6 大分布式事务方案：
```

| 方案 | 一致性 | 侵入性 | 性能 | 场景 | 原理简述 |
|---|---|---|---|---|---|
| 2PC（XA） | 强一致 | 低（DB 原生支持） | 差（长事务锁资源） | 传统单体、银行内部 | 协调者 prepare → 所有参与者 OK → commit，任意 no → rollback；阻塞问题 |
| 3PC | 强一致 | 低 | 差 | 理论为主 | CanCommit → PreCommit → DoCommit；引入超时，减少 2PC 阻塞但仍阻塞 |
| TCC（Try-Confirm-Cancel） | 最终一致 | 极高（3 接口 per 业务） | 好 | 金融核心、高并发 | Try 预留资源 + Confirm 确认 / Cancel 补偿回滚；3 大问题：空回滚/悬挂/幂等 |
| Saga（长事务） | 最终一致 | 中（每个服务正向 + 反向） | 好 | 微服务链长、跨公司业务 | 正向服务按序调用；失败则反向逆序补偿（回滚策略）；日志驱动 |
| 本地消息表（可靠事件） | 最终一致 | 中 | 好 | 通用业务（推荐） | 本地事务：业务表 + 消息表同一库本地事务 → 定时任务轮询发 MQ → 消费端幂等 |
| RocketMQ 事务消息 | 最终一致 | 低（MQ 自带） | 好 | 已用 RocketMQ 场景 | 半消息 Half → 本地事务 → commit/rollback → 事务回查；MQ 内置 |

【TCC 详解（Try-Confirm-Cancel 两阶段 3 接口）】：
  - 接口要求：每个参与分支写 3 个接口
    ① Try：**预留**业务资源（检查、冻结，不真正提交）
       例：账户 A 扣款 → Try 阶段：冻结 A.frozen += 100，A.available -= 100（可用减少）
    ② Confirm：**确认**执行（Try 成功才会进 Confirm，TCC 框架保证必执行，空 confirm 容忍）
       例：A.frozen -= 100，直接把冻结扣掉（钱真正出账）
    ③ Cancel：**取消**回滚（Try 任一失败 / 超时，Cancel 把 Try 预留释放）
       例：A.frozen -= 100，A.available += 100（把冻结释放回可用）
  - 3 大经典问题 + 解决方案：
    ① 空回滚：Try 没收到（网络丢包）→ 先收到 Cancel → 直接回滚没预留的
      · 解决：每个分支事务日志表，Try 前 INSERT tcc_log(status=TRYING)
        Cancel 执行前查表：TRY 日志不存在 → 视为空回滚，直接 INSERT(status=CANCELED) 返回成功
    ② 幂等：Confirm/Cancel 重试多次（MQ/RPC 超时重试）
      · 解决：状态机：TRYING → CONFIRMING → DONE；相同 XID + BranchID 收到已 CONFIRMED 的请求直接返回成功
    ③ 悬挂：Cancel 先执行完，Try 后来到（网络拥堵、乱序）→ Try 预留资源后无人释放
      · 解决：INSERT tcc_log 时唯一键（xid+branch）。Cancel 先到：记录 status=CANCELED。
        后到的 Try 再 INSERT 键冲突 → 抛异常拒绝执行
  - 框架：Seata TCC 模式（注解 @TwoPhaseBusinessAction + @BusinessActionContextParameter）

【Saga 详解（长事务）】：
  - 核心思想：正向 + 反向补偿
    T1 → T2 → T3 → ... → Tn 全部成功 → 完成
    任一步失败（例 T3 失败）：
    ① 先执行 T3 的正向补偿（如果 T3 本身半成功）
    ② 按逆序 C3 不用 → C2（T2 的补偿）→ C1（T1 的补偿）
  - 补偿链执行：
    · 执行图编排 OR 事件驱动（状态机）
  - 优点：无锁、长流程、高吞吐
  - 缺点：不保证隔离（T2 完成时数据已经对外部可见，后来又回滚了，脏读）
  - 框架：Seata Saga 模式、Apache ServiceComb Pack、流程引擎（Camunda）

【本地消息表 + MQ（最通用的"最终一致"方案）】：
  步骤：
  1. 下单业务和"待发送消息表"放同一个 DB 中，走本地事务：
     BEGIN;
       INSERT INTO order ...;
       INSERT INTO msg_outbox(id, biz, payload, status=0, create_time)
         VALUES (uuid(), 'order_created', JSON(...));
     COMMIT;
  2. 后台定时任务（或监听 binlog CDC）：
     SELECT * FROM msg_outbox WHERE status=0 LIMIT 100;
     每条 → 发 RocketMQ/Kafka（send 异常继续下次重试）
     成功 → UPDATE msg_outbox SET status=1, send_time=NOW() WHERE id=?
  3. 消费方（下游服务）：
     ① 消息重复？→ 幂等处理（msg_id 去重表 / Redis SETNX / DB 唯一键）
     ② 消费失败？→ 重试；死信队列告警人工介入
  4. 对账兜底：定时 T+1 比对双方表，补偿差异

【RocketMQ 事务消息（半消息）】：
  RocketMQ Broker 提供的能力：
  1. Producer 发送【Half 消息（半消息）】到 Broker
     → Broker 收到后存到 Topic RMQ_SYS_TRANS_HALF_TOPIC（消费者不可见）
     → Broker 返回 ACK OK
  2. Producer 收到 ACK → 执行【本地事务】（业务 DB 更新）
     · 成功 → commit() 发送 COMMIT 消息给 Broker
     · 失败 → rollback() 发送 ROLLBACK 消息给 Broker
     · UNKNOWN（超时）→ 进入第 3 步
  3. 【事务回查】：Broker 定时（60s）扫描 Half 消息未 COMMIT/ROLLBACK
     → 回调 Producer 的 checkLocalTransaction(MessageExt msg)
     · Producer 查事务日志表 / DB 状态 → 返回 COMMIT / ROLLBACK
     · 多次（15 次默认）回查仍未 UNKNOWN → 默认回滚（可配置）
  4. Broker 收到 COMMIT → Half 投递到真实 Topic，消费者可见；ROLLBACK → 删除 Half

---

### 2.4.3 微服务 & RPC

```
【Dubbo 核心（面试问：Dubbo SPI、集群容错、负载均衡、服务暴露/引入流程）】：
Dubbo 分层架构（10 层，Service / Config 顶层）：
  0. Service 业务层
  1. Config 配置层（ServiceConfig/ReferenceConfig 对应 Provider/Consumer）
  2. Proxy 代理层（ProxyFactory 生成服务端/消费端 Stub，默认 Javassist 字节码生成）
  3. Registry 注册中心层（RegistryFactory → Zookeeper/Nacos/Redis，Subscribe/Publish）
  4. Cluster 路由集群层（Failover/Failsafe/Failfast/Forking，Router + LoadBalance）
  5. Monitor 监控层
  6. Protocol 调用协议层（Dubbo/REST/Thrift/gRPC，核心 invoke()）
  7. Exchange 信息交换层（Request/Response，同步转异步 DefaultFuture）
  8. Transport 网络传输层（Netty/Mina，默认 Netty）
  9. Serialize 序列化层（Hessian2 / Kryo / FST / Protostuff / JSON / JDK）

★ Dubbo SPI（和 JDK SPI 区别）：
  - JDK SPI（ServiceLoader）：一次性加载 META-INF/services/接口所有实现，遍历取，不按需
  - Dubbo SPI：按需加载 + Key-Value 命名 + 自动包装 Wrapper + IoC 注入 + AOP + 自适应
    文件：META-INF/dubbo/接口全限定名
    内容：key=全限定类名  （如 random=org.apache.dubbo.rpc.cluster.loadbalance.RandomLoadBalance）
    @SPI("dubbo")：接口默认 key
    @Adaptive：自适应类注解（运行时根据 URL 参数选择真正实现，编译时动态生成字节码 Xxx$Adaptive）
    @Activate：自动激活（按 group/provider/consumer + value/key 满足条件自动加载）

服务暴露（Provider 启动）流程：
  ServiceConfig.export()
    → 检查配置、拼 URL（dubbo://ip:port/com.xxx.UserService?xxx=yyy）
    → ProxyFactory.getInvoker(service, type, URL) （JDK Proxy + AbstractProxyInvoker）
    → Protocol.export(wrapperInvoker)：
       · 先记录数据到 RegistryProtocol（export）
       · ProtocolFilterWrapper 构造过滤器链（EchoFilter / ClassLoaderFilter / GenericFilter ...）
       · ProtocolListenerWrapper 加监听器
       · DubboProtocol：启动 Netty Server（ExchangeServer.bind），端口默认 20880
       · 把 invoker 以 key=服务名 存 exporterMap（收到请求后拿 invoker 调）
    → RegistryProtocol.register()：向 ZK 注册 /dubbo/接口名/providers/URL 临时节点
    → RegistryProtocol.subscribe()：订阅 configurators 节点（动态配置推送）

服务引入（Consumer 启动）流程：
  ReferenceConfig.get()
    → ProxyFactory.getProxy(protocol.refer(type, url)) 返回接口代理
    · Protocol.refer：
      RegistryProtocol 先向 ZK subscribe providers / consumers / routers / configs
      → 拿到 providers URL 列表，变化时通知
    · Cluster.join(directory)：把多个 Provider invoker 伪装成一个（Cluster Invoker）
      FailoverCluster 默认：失败重试（重试 2 次 + 其他 provider）
    · 调用方法时：代理 → Cluster Invoker
      → Router 路由（标签路由、条件路由）过滤 provider
      → LoadBalance 从多个 provider 中选 1 个（Random/RoundRobin/LeastActive/ConsistentHash）
      → Filter 链（ConsumerContextFilter / FutureFilter / MonitorFilter）
      → DubboInvoker → ExchangeClient.request(id, req)
         · Netty 长连接发请求
         · DefaultFuture(id, timeout) 挂起等待，超时抛异常
         · 响应回来时 NettyHandler 收到 → 根据 id 找到 DefaultFuture → doReceived(res) → 唤醒等待线程
         · 同步返回结果（也支持 AsyncRpcResult 异步返回 CompletableFuture）

【Sentinel 核心原理（滑动窗口 + 令牌桶 / 漏桶）】：
  - 滑动窗口统计：
    · 默认 1s = 2 个 500ms window（LeapArray 环形数组）
    · WindowWrap：窗口 start + 统计 Metric（pass/block/exception/rt/success）
    · 取当前时间定位 slot，cas 递增计数；过期窗口重置
  - 流量控制：
    · QPS 模式：滑动窗口中 PASS 计数 > count → 直接 block
    · 线程数隔离：当前资源并发线程 > N → block（类似 Hystrix 信号量隔离）
    · 冷启动 WarmUp：token 令牌桶蓄水模式，冷启动因子 3，QPS 逐步达到阈值
    · 匀速排队：漏桶算法，每次 sleep 精确控制（1/count 秒）突发均匀排队
  - 熔断降级：
    · 慢调用比例：RT > max 的占比超阈值 → 熔断 X 秒
    · 异常比例 / 异常数：超比例或数量 → 熔断
    · 3 状态机：Closed → Open（阈值触发）→ HalfOpen（恢复期探测一次）→ Closed / Open
  - 系统自适应保护：系统 load1 / avgRT / QPS / 线程数 达到阈值全局限流

【SkyWalking 原理（链路追踪）】：
  - Java Agent 无侵入：-javaagent:skywalking-agent.jar
    premain 阶段 ByteBuddy 插桩（AOP 字节码增强）：
    插件化增强 Tomcat/DispatcherServlet/Dubbo/Feign/RocketMQ/MySQL/Redis...
  - 数据格式：
    · TraceId（全局唯一，整条链路）
    · SpanId（每一个调用片段，父子关系）→ Segment（同一线程内多个 Span）
    · ContextCarrier 跨线程/跨进程透传（Feign HTTP Header: sw8，Dubbo attachment）
  - 采样策略：默认全部采集，可配置采样率 / 慢操作 100% 采集 / 错误 100%
  - 存储：默认 H2（单机），生产 Elasticsearch 7.x / 8.x，ClickHouse 也支持
```

---

## 2.5 MySQL：深度 + 调优实战

### 2.5.1 ~ 2.5.3（B+树、MVCC、锁机制）简述

```
B+ 树计算：16K 页，BIGINT 主键 + 6B 指针 → 非叶子页存 ~1170 索引项 → 3 层 B+ 树 ≈ 1170²×16 ≈ 2200w 行。
  B+ vs B：B+ 只在叶子存数据，非叶子纯索引项 → 树更矮、I/O 更少；叶双向链表 → 范围查询高效。

MVCC 三件套：隐藏列 DB_TRX_ID(6B)+DB_ROLL_PTR(7B)+DB_ROW_ID(6B)；Undo 版本链；
  ReadView（m_ids/min_trx_id/max_trx_id/creator_trx_id）。可见性算法：
    · trx_id < min → 可见
    · trx_id >= max → 不可见
    · min ≤ trx_id < max：在 m_ids（活跃）→ 不可见；不在 m_ids → 可见
  RC vs RR：RC 每次 SELECT 全新 ReadView；RR 第一次 SELECT 生成后复用。

InnoDB 锁 3 种：Record Lock（单记录）/ Gap Lock（开区间）/ Next-Key Lock（左开右闭）。
  RR 默认 Next-Key Lock；唯一索引等值命中 → 退化成 Record；
  唯一索引等值未命中 → 退化成 Gap；普通索引等值向右遍历到第一个不等。
  死锁检测：InnoDB waits-for graph 环检测；统一加锁顺序 / 乐观锁 / RC 隔离级别避免死锁。
```

### 2.5.4 三大日志（redo/undo/binlog）与两阶段提交

```
3 大日志对比：
```

| 日志 | 作用 | 内容 | 产生时机 | 持久化时机 | 物理/逻辑 |
|---|---|---|---|---|---|
| **redo log** | 崩溃恢复（WAL） | 物理页级修改 | 事务执行中写 redo log buffer | commit 时刷盘（innodb_flush_log_at_trx_commit） | 物理 |
| **undo log** | MVCC + 回滚 | 逻辑反向操作（UPDATE 存旧值整行） | 数据修改前写入 Undo Segment | purge 线程异步清理 | 逻辑 |
| **binlog** | 主从复制 + 归档恢复（Server 层） | SQL/行变更 | commit 前整体写入 binlog cache | sync_binlog=1 每次事务刷盘 | 逻辑 |

```
两阶段提交（保证 redo + binlog 一致）：
  阶段 1 PREPARE：redo log 写入刷盘，状态 = PREPARED
  阶段 2 COMMIT：① 写 binlog 刷盘 ② redo 状态 PREPARED → COMMITTED（内存，不必刷盘）
  崩溃恢复：redo 只有 PREPARED + binlog 存在（XID 对应）→ commit；否则 rollback
  双 1 配置：innodb_flush_log_at_trx_commit=1 + sync_binlog=1（金融级）

undo purge：Undo history list 长事务 ReadView 阻止清理 → 长事务会导致 Undo 无限膨胀！
binlog 格式：STATEMENT（不确定函数问题）/ ROW（5.7+ 默认，绝对一致 + 支持闪回）/ MIXED
```

### 2.5.5 主从复制原理

```
3 步复制：Master Binlog Dump 线程 → Slave I/O 线程写入 Relay Log → Slave SQL 线程重放。
  3 种模式：异步（默认，性能好可能丢）/ 半同步（5.5 插件，Slave ACK 才返回）
    / 增强半同步（5.7 Loss-less AFTER_SYNC：Slave ACK 落盘 relay log 后才 Master commit 用户可见）
  并行复制：5.6 按库并行；5.7 LOGICAL_CLOCK（同组 commit 并行）；
    8.0 writeset（主键不冲突可并行，并行度最高）
  GTID：全局事务 ID source_id:transaction_id，主从切换自动找未执行 GTID 补全（不用 file+pos）
  高可用方案：MHA（Master HA，选最新 Slave + 补偿差异 + VIP 漂移）主流

### 2.5.6 慢 SQL 完整排查 SOP

7 步排障：
  ① 定位来源：slow_query_log + mysqldumpslow / show processlist
  ② EXPLAIN 10 列：type（system/const/eq_ref/ref/range/index/ALL）、
     key（实际选的索引=NULL就没走）、rows（预估行数）、
     Extra（Using index 覆盖 / Using where Server层过滤 / ICP 索引下推 /
            Using temporary 临时表 ✖ / Using filesort 外部排序 ✖）
  ③ OPTIMIZER_TRACE 看优化器为什么选了 A 不选 B
  ④ SHOW PROFILE CPU,BLOCK IO FOR QUERY 看阶段消耗
  ⑤ performance_schema + sys 库：sys.schema_unused_indexes 冗余索引 / sys.innodb_lock_waits 锁等待
  ⑥ 优化方案优先级：加索引 → 改 SQL → 架构优化
     大分页优化：延迟关联（INNER JOIN (SELECT id LIMIT 100w,10) x）或游标分页 WHERE id > ? LIMIT 10
  ⑦ 验证：再 EXPLAIN + 看慢查询是否消失
```


## 2.6 中间件高级

### 2.6.1 Redis 底层实现

```
Redis 数据结构 → 底层编码实现：
  · OBJ_STRING：
    OBJ_ENCODING_INT（整数字符串 < long）
    OBJ_ENCODING_EMBSTR（短字符串 < 44B，redisObject + sdshdr 连续内存）
    OBJ_ENCODING_RAW（长字符串，SDS 独立）
  · OBJ_LIST（Redis 3.2+ 只一种）：OBJ_ENCODING_QUICKLIST
  · OBJ_HASH：ZIPLIST（键少值短，hash-max-ziplist-entries=512, value<64B）
               / HT（超过阈值 dict HashTable）
  · OBJ_SET：INTSET（整数集合，全部整数且数量少）/ HT
  · OBJ_ZSET：ZIPLIST（小数据量）/ SKIPLIST（跳表 + 哈希表双层）

【SDS 简单动态字符串】：
  struct sdshdr { int len; int free; char buf[]; }
  相比 C 字符串：① O(1) len；② 二进制安全（不靠 \0）；③ 杜绝缓冲区溢出；
  ④ 预分配 + 惰性释放减少内存分配次数

【QuickList】：
  双向链表，每个节点 = 一个 ziplist（默认 list-max-listpack-size=-2：每个 ziplist ≤ 8KB）
  折中 ziplist 紧凑省内存 + linkedlist O(1) 修改

【Ziplist 压缩列表】：
  连续内存段 <zlbytes><zltail><zllen><entry1>...<entryN><zlend>
  每个 entry ：<prevlen><encoding><content>
  优点：紧凑；缺点：插入删除 memmove + 连锁更新 prevlen
  → Redis 控制 ziplist 大小避免连锁更新

【ZSet skiplist 跳表】：
  为什么同时用 skiplist + hashtable？
    skiplist：O(log n) 范围查询、按 score 排名、有序输出
    hashtable（dict[member] = score）：查询某 member 分数 O(1)
  → 两者互补，空间上存两份但引用共享数据
  跳表原理：多层 level 1 完整链表，上层每层按 P=1/4 概率升一级（max level=32）
    查询从最高层 head → 找到 ≤ 目标且下一个 > 目标 → 往下跳层；平均 O(log n)
  vs 红黑树：跳表实现简单、范围查询更自然（层 1 就是链表）、并发好（局部旋转少）
```

### 2.6.2 Redis 持久化与高可用

```
【RDB 快照】：
  · BGSAVE：fork() 子进程 + 操作系统 Copy-On-Write
    fork 瞬间共享物理页；父进程写 key → 缺页中断 → OS 复制该物理页给父进程
    优点：rdb 文件紧凑二进制，恢复快，适合冷备
    缺点：两次快照之间宕机 → 几分钟数据全丢

【AOF（Append Only File）】：
  · appendfsync：always（每条刷盘）/ everysec（默认，最多丢 1s）/ no（OS 决定）
  · AOF Rewrite 重写：BGREWRITEAOF（不读老 AOF，直接读当前内存生成最小等价新 AOF）
    触发：auto-aof-rewrite-percentage 100 + auto-aof-rewrite-min-size 64MB
    fork 子进程期间父进程写命令存入 aof_rewrite_buf_blocks → 子进程完成后 buf 追加到新 AOF
  · Redis 4.0+ 混合持久化（aof-use-rdb-preamble yes）：
    AOF 开头 RDB 全量 + 增量 AOF 命令 → 快速加载 + 安全

RDB vs AOF：RDB 文件小恢复快；AOF 安全丢 1s；生产推荐两种都开（混合持久化）

【主从复制 + 哨兵 Sentinel】：
  · 全量同步：slave psync ? -1 → master BGSAVE + replication buffer → RDB + buffer 给 slave
  · 部分重同步（断线重连）：repl_backlog 环形缓冲，断线期间 offset 还在 → 补发即可
  · Sentinel 3 大职责：监控 / 通知 / 自动故障转移
    a) 主观下线 sdown（单个 Sentinel 认为 master 挂）
    b) 客观下线 odown（quorum ≥ N/2+1 都认为挂）
    c) Sentinel leader 选举（Raft）
    d) 选新 master：优先级最高 → offset 最大 → runid 最小
    e) 老 master 其他 slave SLAVEOF 新 master
    f) 老 master 恢复 → 新 master 的 slave

【Redis Cluster】：
  · 16384 哈希槽（CRC16(key) mod 16384；为什么 16384？心跳包槽位/8=2KB 适中）
  · 至少 3 主 3 从（奇数主）
  · MOVED：客户端访问错节点 → 返回 MOVED slot ip:port，客户端重定向（JedisCluster 自动）
  · ASK：槽迁移期间，临时 MOVED（不更新本地路由）
  · Gossip 协议检测节点存活；pfail → fail（过半标记）从节点选举新主节点
```

### 2.6.3 Kafka 底层原理

```
Kafka 为什么快？
  ① 顺序写磁盘（log append-only，随机 I/O 慢 1000 倍 → 顺序写内存级）
  ② PageCache + sendfile() 零拷贝（磁盘 → socket buffer 直接 DMA，2 次拷贝 1 syscall）
  ③ 批量 + 压缩（batch.size / linger.ms 攒一批发；lz4/snappy/zstd）
  ④ 分区并行：Topic 分 N 个 Partition，Consumer Group 并发消费（并发度 = Partition 数）

核心概念：
  · Broker / Topic / Partition（1 leader + N follower 副本）
  · Segment：每 Partition 多段，00000.log 消息 + .index 稀疏索引 + .timeindex 时间索引
    查 offset=X：二分 index 文件找 ≤ X 最大 entry → log 文件 position 顺序扫
  · Producer acks：0（不等）/ 1（leader OK）/ -1 all（ISR 全部 OK）
  · ISR（In-Sync Replicas）：leader + 落后 < replica.lag.time.max.ms(30s) 的 follower；
    只有 ISR 有资格当选 leader
  · HW（High Watermark）高水位：ISR 全部同步到的最小 offset，consumer 最多消费到 HW
    （防止消费 leader 写了但 follower 没同步的脏数据）
  · LEO（Log End Offset）：各副本追加到的最新 offset

Exactly-Once 语义：
  · 幂等 Producer（enable.idempotence=true）：<PID, Partition, SeqNum> Broker 去重
    保证单个会话单分区内不重复
  · 事务（exactly_once 跨分区多原子）：transactional.id 绑定 PID + Broker 事务日志

Rebalance 消费者重平衡：
  触发：消费者增减 / 订阅 topic 增减 / 分区数增减
  协议：JoinGroup → 选 leader consumer + SyncGroup 下发分配方案
  Eager：全组 STOP（STW）；Cooperative Sticky（增量）：几轮调整，大部分分区不动
  问题：慢消费者心跳超时频繁 rebalance = 雪崩
  解决：Static Membership（group.instance.id 静态成员，重启不 rebalance）

```

### 2.6.4 RocketMQ 特色功能

```
架构：NameServer（无状态，Broker 心跳注册）+ Broker（Master/Slave）+ Producer/Consumer

存储零拷贝：
  · CommitLog 单文件（1G 顺序写）+ MappedByteBuffer（mmap 零拷贝）
  · TransientStorePool 堆外内存 + 异步 flush（减少 PageCache 锁）

高可用刷盘 + 主从：
  · flushDiskType：ASYNC_FLUSH / SYNC_FLUSH
  · brokerRole：ASYNC_MASTER / SYNC_MASTER（同步双写，主+从都成功才 OK，金融级）

事务消息：COMMIT / ROLLBACK / UNKNOW；回查 15 次（transactionCheckMax），超过默认回滚

延迟消息 18 级（1s~2h）：SCHEDULE_TOPIC_XXXX 延迟消息 Topic + 时间轮 DeliverDelayedMessageTimerTask 到点投递

消息零丢失三端方案：
  ① Producer：同步 send + sendMsgTimeout + retryTimesWhenSendFailed 自动重试 + 事务消息
  ② Broker：SYNC_FLUSH + SYNC_MASTER + DLedger（基于 Raft 协议高可用）
  ③ Consumer：消费成功才 return CONSUME_SUCCESS；异常 RECONSUME_LATER 重试 16 次
     → 最后进 DLQ 死信队列（%DLQ%groupName）人工补偿
```

---

# 三、技术二面（架构设计 + 技术决策 + 排障）

## 3.1 项目深挖：STAR 高级版

### 3.1.1 项目 STAR 模板（高级版）

```
高级版 STAR（每个项目讲 15 分钟，含量化 + 决策 + 复盘）：
```

| 部分 | 回答要点（必须量化） | 时间 |
|---|---|---|
| **S 背景** | 公司业务、团队规模、你所在的技术部门、项目在业务的位置 | 1 min |
| **T 任务** | 项目的目标与指标（QPS / 数据量 / RT 目标 / 稳定性 99.x%）、你作为 **Owner / 核心开发**承担的模块 | 2 min |
| **A 行动（核心，60%）** | ① 整体架构图（画）<br>② **技术选型对比**：为什么选 A 不选 B/C？（N 条理由）<br>③ **关键模块设计与实现**（3~5 个）：类图 / 时序图 / 核心代码（设计模式：策略/模板/责任链/状态机）<br>④ **遇到的 3 大难点 + 解决方案（最关键！）**：现象 + 根因 + 2~3 方案对比 + 最终解决 + 复盘<br>⑤ **性能调优**：压测报告、前后指标对比 | 9 min |
| **R 结果** | **量化数据**（接口 RT、QPS 支撑、成功率、可用性、代码行数、BUG 率）；节省成本、GMV 等更好 | 2 min |
| **复盘反思** | 如果重做，有哪些可以优化？学到什么新技术？ | 1 min |

### 3.1.2 典型追问方向与应答策略

| 面试官追问 | 应对策略 |
|---|---|
| 为什么选技术 A？ | ✅ **对比 2~3 个方案 + 业务约束**："我们 N 个约束：① QPS X；② 保留 X 天；③ 团队熟悉 X；对比 A/B/C：优缺点；综合选 A，实际效果 X。"❌ 别答：A 流行 / 大家都用 |
| 这个难点你怎么想到这个解法的？ | ✅ **结构化思路**："复现 → A 工具现象 B → 初步假设 C/D/E → 逐一排除 C 和 D → 定位 E（证据：日志/堆栈/指标）→ 方案 F1/F2 权衡选 F2 因为..." |
| 数据量增长 10 倍方案还撑得住吗？怎么升级？ | ✅ **先评估瓶颈 + 演进路径**："目前瓶颈在 X，增长 10 倍：① 加缓存 + 读写分离 → ② 垂直拆库 → ③ ShardingSphere 水平分库分表（分片键 user_id，4 库 16 表）→ ④ OLAP 迁 ClickHouse..." |
| 最大技术挑战？ | ✅ **选一个真困难的**：高并发超卖 / 性能调优（2s→50ms）/ P0 OOM / 单体→微服务迁移 |
| 线上出过什么大事故？ | ✅ **主导过不致命 + 有复盘改进**："大促后 OOM，①②③ 恢复 → dump 分析 ThreadLocal 未 remove 在 Tomcat 线程池泄漏 → hotfix + Arthas 告警 + CheckStyle 扫描" |
| 主导过技术选型/架构升级？ | ✅ **背景+方案+量化+阻力**："单体 100w 行代码，发布 40 分钟，DB 100% CPU；DDD 拆 6 微服务，Spring Cloud Alibaba，3 月灰度 1%→5%→50%→100%，发布 10 分钟，CPU 25%，RT 降 30%，坑点：分布式事务超时重试→TCC+幂等解决" |

---

## 3.2 系统设计：高频题目 + 答题框架

### 3.2.1 系统设计评分维度（8 步 SOP）

> 千万不要一上来就画图！缺一步扣 1 档：

```
系统设计 8 步模板：
  ① 需求澄清（5 分钟，最关键！）
     DAU/MAU？QPS 峰值？读写比？一致性要求？数据保留多久？核心功能边界？
  ② 数据量级估算（3 分钟，不拍脑袋）
     QPS = DAU × 人均日请求 / 86400
     峰值 QPS = 平均 × 3~5（热点 × 10）
     存储 = 每天新增 × 保留天 × 副本数 × 150% 冗余
     缓存命中率 90%~99% 时 DB QPS？
  ③ 整体架构分层（5 分钟，顶层设计）
     客户端 → CDN/DNS/LVS/Nginx 接入 → Gateway + 业务服务 → DB/缓存/MQ/搜索/对象存储 → 配置中心/注册中心/链路追踪
  ④ 核心模块详细设计（15 分钟，拉分项）
     API 定义；库表设计 + 索引 + 分库分表分片键；典型链路时序图
  ⑤ 高可用设计（3 分钟）
     限流/降级/熔断；多活容灾；服务无状态水平扩展、主从切换、MQ 死信
  ⑥ 高性能设计（3 分钟）
     多级缓存（CDN+Nginx+Caffeine+Redis）异步化（批量/聚合）索引+读写分离+分库分表+冷热分离
  ⑦ 一致性设计（2 分钟）
     CAP 选择；分布式事务方案；幂等方案
  ⑧ 可观测性 & 安全 & 收尾
     日志/指标/链路/告警；鉴权/签名/防刷/加密
     "以上是我的思路，哪些地方需要我再展开？"
```

### 3.2.2 设计一：百万级 QPS 秒杀系统

```
核心：全链路 7 层漏斗 + 削峰（流量层层过滤，真正到 DB 的极少）

① CDN + 浏览器缓存 + 前端按钮置灰 3s
② Nginx：limit_req_zone 按 IP 10r/s；黑白名单；LVS + Nginx 横向扩展
③ Gateway + Sentinel：接口集群流控 50w QPS；用户级 1s 3 次；人机验证码防刷作弊
④ 本地 Caffeine 缓存：活动信息 / 售罄标记位 sold_out_flag=true → 99% 请求在内存挡住
   · 热点 key 分片：热点商品单 key 拆成 100 个本地子缓存（避免 Redis 网卡打爆）
⑤ Redis 预扣库存（核心 Lua 原子，绝对不超卖）：
```lua
local stock = tonumber(redis.call('GET', KEYS[1]))
if stock and stock >= tonumber(ARGV[1]) then
    return redis.call('DECRBY', KEYS[1], ARGV[1])
else return -1 end
```
⑥ RocketMQ 事务消息异步下单：
   · Redis 预扣 OK → 发半消息 → commit → 订单消费者（顺序消费+幂等）写订单表 + DB 实际扣减
   · MQ 重试 16 次 → DLQ → 人工兜底
⑦ DB（最后一道防线）：乐观锁 UPDATE goods_stock SET stock=stock-1 WHERE id=? AND stock>=1
   · 订单表 user_id + activity_id 唯一索引防重复
细节：T+5 分钟对账（Redis+订单表 vs 原始库存）自动补偿回滚
量化：100w QPS 峰值 → DB 仅写入 1000 订单 + 1000 库存（漏斗极好）

```

### 3.2.3 设计二：百万级在线 IM 系统

```
100 万同时在线 + 1w QPS 消息，消息必达率 99.99%

① Netty IM Gateway（10 台 × 10w 连接 = 100w）：
   · Epoll 模式 + SO_REUSEPORT 多核；堆外内存 + PooledByteBufAllocator
   · 心跳：客户端 30s Ping，服务端 90s 没心跳踢下线
   · 单机 10w 连接调优：fs.file-max=1048576，-Xms8g -Xmx8g -XX:MaxDirectMemorySize=4g
② 用户路由 + 会话：
   · 用户登录 Redis SETNX user:123:gateway gateway-ip:port
   · 发消息查路由 → 目标在哪台 Gateway → 那台推对应 Channel
   · 2 次 ACK：A 发 → 服务端 sendACK；B 收 → deliverACK；未 ACK MQ 延迟 10s/30s/2min 重推 3 次
③ 存储：
   · HBase 消息历史 RowKey=conversationId_minUid_maxUid + timestamp + seq
     （同会话 RowKey 前缀聚集，范围查询极快）
   · Redis List 离线消息（7 天），用户上线 LPOP 拉完
   · 小群 ≤100 写扩散（每个成员收件箱各写 1 份）；大群 >100 读扩散（群收件箱 + readPoint）
④ 跨机房地域就近接入 + SkyWalking 长连接自定义 TraceId 透传 + Prometheus 指标

```

### 3.2.4 设计三：高一致性支付系统

```
1000w 笔/天，QPS 峰值 2w，账绝对不能错！

6 大模块：
  ① Pay Gateway：商户 RSA2048 签名验签 + 幂等校验（商户订单号唯一）+ 限流降级
     · 适配支付宝/微信/银联（适配器模式隔离渠道 SDK）
  ② 支付订单中心：
     · 状态机 INIT→PAYING→PAID/FAIL/CLOSED
     · 唯一索引 uk_merchant_order(merchant_id, merchant_order_no) 防重复
  ③ 资金账本（核心）：
     · user_id, balance, frozen, version（乐观锁）
     · UPDATE account SET balance=balance-100, version=version+1 WHERE user_id=? AND balance>=100 AND version=?
       AffectRows=0 → 重试 3 次 → 再失败回滚
     · **TCC 模式**：
       Try：可用-100，冻结+100；Confirm：冻结-100（出账）；Cancel：冻结-100，可用+100
       · tcc_fence_log（xid+branch 唯一键）防悬挂/空回滚/幂等
  ④ 风控：Drools/LiteFlow 规则引擎（异常金额/IP/地区/黑名单 → 拦截/人工/短信）
  ⑤ T+1 对账：三方渠道对账文件 FTP 解析 → 我方 vs 三方逐笔勾兑
     · 长款（我方没渠道有）补记账 / 短款（我方 PAID 渠道没有）告警人工介入
     · 差错池 + 自动补偿 + 人工兜底
  ⑥ 通知：商户回调指数退避（15s~24h 12 次）直到返回 "SUCCESS" + 商户主动查询补单

一致性保障：所有操作幂等；所有接口可重试；所有支付行为 insert-only（只 INSERT 不 UPDATE 旧单，新流水）；对账+补偿+差错三条线

```

### 3.2.5 设计四：亿级短链系统

```
1 亿 QPS 访问 + 10w/s 创建；自定义短码、过期、PV/UV 统计

① 发号器（推荐号段模式：美团 Leaf / 滴滴 TinyId）：
   · DB 号段表 max_id=999, step=1000, UPDATE seq SET max_id=max_id+step WHERE biz_tag='short_url'
     → 内存 AtomicLong 1000 次用完再拿；10w QPS → DB 仅 100 次/s
   · 转 base62(id)（0-9a-zA-Z），打乱表顺序防预测
   （Hash 方案千万级 1e-6 冲突，自增永不冲突）
② 301 vs 302：302（临时重定向，每次都请求服务器，可统计 PV/UV；301 浏览器缓存不支持统计）
③ 存储 + 读：
   · 写：short_code 主键表 + Redis SET short:{code} long_url（TTL）
   · 读：Redis 命中 → Kafka 写 PV/UV 日志 → 302；Redis 没命中 → MySQL 主键查 → 回写 Redis → 302
     · 空短码也写 "null" Redis 60s（防穿透攻击）
   · 数据规模 1 亿 × 200B = 20GB MySQL，Redis 热点 5% 1GB
④ 统计：Kafka → Flink 1min 窗口实时聚合 PV/UV，Redis + ClickHouse T+1 报表
   · UV HyperLogLog（12KB 估算百万，误差 0.8%）
⑤ 优化：Caffeine 本地 top 0.1% 热短码缓存；布隆过滤器（125MB 误判 0.1%）不存在的短码直接 404

```

### 3.2.6 设计五：实时排行榜系统

```
1000w 用户战力实时更新；top100 查询<50ms；日/周/月榜 + 分区/全球/好友榜

核心 Redis Sorted Set（ZSet）：
  ZADD / ZINCRBY、ZREVRANGE（前 N）、ZRANK（查某用户排名），复杂度 O(log N)

① 分数变更数据流：DB 战力更新 → Canal binlog → Kafka → 消费服务 ZINCRBY day/week/month ZSet
② 多维度：
   · 分区榜：shard:{regionId}:day:rank:xxx（独立 ZSet）
   · 好友榜：好友变更时同步好友 ZSet，查询直接 ZREVRANGE（好体验）
③ 分页：ZREVRANGE WITHSCORES 0-99；大分页用游标（last_score + 偏移量 ZREVRANGEBYSCORE）
④ 周榜/月榜：实时累计写 3 份 ZSet（实时准）或每日 Flink UNION 聚合（省资源）
⑤ 全球榜（1000w 用户分片）：
   rank_shard_0~63，写入 user_id%64 片
   查询 top100：每片 top100 → 64 个结果内存合并排序得全球 top100
   查某用户排名：自己分片 rank + 其他 63 片 score>我分数的 count 之和

---

## 3.3 线上排障：灵魂拷问 6 大场景

### 3.3.1 线上 CPU 100% 排查

```
SOP 8 步：
  ① top → 定位高 CPU Java 进程 PID
     · load 1min >> CPU核数 → CPU 饱和
  ② top -H -p <pid> → 高 CPU 线程 TID
  ③ printf "%x" <TID> → 十六进制
  ④ jstack <pid> > jstack.log
  ⑤ grep "nid=0x<hex>" jstack.log → 看堆栈（常见：死循环、GC 线程、正则回溯 ReDoS、JSON 序列化）
  ⑥ Arthas（推荐跳过 2~5）：
     · thread -n 5 → Top 5 高 CPU 堆栈
     · profiler start → 等 1min → profiler stop → 火焰图 HTML（看 CPU 热点方法）
  ⑦ 针对性修复（正则改 RE2/J；代码死循环 hotfix；GC 问题转 OOM 排查）
  ⑧ 事后加 CPU>80% 5 分钟告警

经验案例：双 11 订单 CPU 98% RT 50ms→5s，Arthas profiler 60% 在 regex Pattern.match，
  根因：防 XSS 正则嵌套量词 .*(script).*，恶意构造长字符串触发回溯；
  紧急替换 RE2/J + 输入长度限制，1 分钟恢复；CodeQL 全公司扫描出 12 个高危正则全部修复。
```

### 3.3.2 线上 OOM 排查

```
SOP 7 步：
  ① 生产必开：
     -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=... -XX:OnOutOfMemoryError="jstack -l %p >> ..."
  ② OOM + 重启 + 老年代 90% 告警
  ③ hprof → MAT / JProfiler：
     a) Histogram（类实例数 + 深堆）Top1 通常泄漏
     b) Dominator Tree：GC Root 引用链（例 Thread→threadLocals→Entry.value→大 HashMap）
     c) Leak Suspects Report 自动结论
  ④ 常见泄漏 8 根因：
     ThreadLocal 未 remove（线程池复用）/ 集合无限增长 / 监听器未注销 /
     static Map cache 不淘汰 / 大查询拉 500w 行 / NIO DirectByteBuffer 堆外泄漏 /
     连接池拿了没 close / 动态生成类（Metaspace 满）
  ⑤ Arthas：heapdump / classloader -t 类加载数 / memory 各代占用
  ⑥ 紧急止血：扩容机器 / 临时调小缓存 TTL / 重启实例
  ⑦ 修复 + 单测复现 + Watch 监控类实例数
```

### 3.3.3 接口响应变慢排查

```
SOP 7 步：
  ① 大盘：CPU/LOAD/MEM/SWAP/带宽/disk util；JVM GC 频率耗时；Redis RT/MySQL 慢查询/MQ 积压
  ② TraceId 瀑布图（SkyWalking/Pinpoint）→ 定位最慢 Span（MySQL/Redis/RPC/代码）
  ③ Arthas：
     trace xxx.XXXService method '#cost>200' → 调树 >200ms 的子方法
     watch xxx.XXXService method '{params,returnObj,throwExp}' → 出入参异常
     profiler start/stop → Async-profiler 火焰图（ALLOC 模式找对象分配热点）
  ④ DB 慢 SQL 走 EXPLAIN（2.5.6）
  ⑤ 常见变慢：代码 N+1 查询；缓存命中雪崩；DB 索引失效锁等待；线程池/连接池耗尽；Full GC 频繁
  ⑥ JMeter 压测复现 + 指标对比
  ⑦ 接口 P99 RT 告警 + 自动采 TraceId
```

### 3.3.4 数据库死锁排查

```
SOP 4 步：
  ① SET GLOBAL innodb_print_all_deadlocks = 1; SHOW ENGINE INNODB STATUS \G
     LATEST DETECTED DEADLOCK 给出两事务：持锁 X 等锁 Y / 持 Y 等 X，以及执行 SQL，谁被回滚
  ② 画等锁图找环
  ③ 根因分类解决方案：
```

| 死锁类型 | 典型场景 | 解决方案 |
|---|---|---|
| 加锁顺序不一致 | 事务 1 先 A 后 B；事务 2 先 B 后 A | 全局**统一加锁顺序**（ID 从小到大） |
| 不同索引顺序 | SQL A FORCE INDEX idx_1 顺序 1-2-3；SQL B 主键顺序 3-2-1 | 强制同索引 |
| Gap/Record 交叉 | RR 级 Gap 锁交叉 | 改 RC（业务允许）或唯一索引退化成 Record |
| IN 乱序 | UPDATE ... IN (2,1,3) vs (3,2,1) | 应用层**排序升序**后传 IN |
| 外键级联 | 父删加子表锁，另事务改子表 | 应用外键替代 DB 外键 + 定时对账 |

```
  ④ 监控 Innodb_deadlocks 次数阈值告警 + 死锁日志自动推

```

### 3.3.5 MQ 消息大量堆积排查

```
SOP 6 步：
  ① 紧急止血：扩容 Consumer + Topic 分区（同组消费者数 ≤ 分区数）
     · 非核心配置消费跳过；批量重发 DLQ 消息回 Topic
  ② Inflow >> Outflow → 消费能力不足；Inflow 突发涨 → 上游生产端 bug
  ③ 生产端排查：上游变更 / retry 死循环（发失败不断 retry 发 10w 重复）
  ④ 消费端 Top5 慢根因：
     a) RPC 慢（3.3.3） b) 慢 SQL（2.5.6） c) 大循环/JSON 正则
     d) Consumer 线程少（调 consumeThreadMin/Max 20→64~128）
     e) 异常连续 16 次失败进 DLQ（%RETRY% 重试 Topic 暴涨）
  ⑤ 永久解决：批量消费 consumeMessageBatchMaxSize=32；轻逻辑+异步 worker 重逻辑；
     线程池隔离消费线程池 vs 重逻辑池；优先级 Topic 独立机器
  ⑥ T+1 对账 + 补偿

```

### 3.3.6 Redis 响应变慢排查

```
SOP 6 步：
  ① 测延迟：redis-cli --latency-history -i 1 / --intrinsic-latency 60
     · 内部延迟 >1ms → 宿主机 steal 高 / 网络抖动
  ② 慢命令：slowlog get 100
     · KEYS * / FLUSHALL / HGETALL bigkey（>10KB）→ 改 SCAN / HLEN / 批量渐进式
  ③ bigkey 扫描：redis-cli --bigkeys / RMA / 自研脚本遍历
     · 大 String：>10KB 图片存对象存储，Redis 只存 URL；
     · 大 Hash/ZSet：拆桶 hash_key_{i % 100}，每次操作定位 1 桶
  ④ 阻塞点：info stats 看 latest_fork_usec（BGSAVE/AOF Rewrite fork 子进程大内存
     fork > 1000ms = 阻塞主线程）；aof_delayed_fsync（AOF fsync 阻塞）
  ⑤ 内存：used_memory > maxmemory，evicted_keys 持续增长（淘汰策略频繁 evict 慢）
     → 调 maxmemory-policy（allkeys-lru 比 volatile-ttl 好）/ 扩容 Cluster
  ⑥ 内存碎片：mem_fragmentation_ratio > 1.5 → activedefrag yes（4.0+ 自动整理）
     / 重启节点（主从切换）

---

# 四、HR / 综合面（高级版差异）

## 4.1 自我介绍（3 分钟 / 1 分钟两版）

```
3 分钟版（高级推荐）：
  【开场 10s】"面试官您好，我叫 XXX，X 年 Java 开发经验，目前在 XX 公司担任高级开发工程师 / 模块 Owner。"
  【学习经历 30s】"20XX 年毕业于 XX 大学 XX 专业（本科/硕士），校招加入 XX 开始做 Java。"
  【第一段工作 40s】"第一家在 XX（公司）做 XX 行业（电商/金融/物流），主要做了 XX 系统，负责订单/支付模块，用的是 Spring + Dubbo + MySQL 技术栈，我主导了 XX 改造，性能提升 40%。"
  【第二段工作（现任，重点）1min10s】"目前在 XX 做 XX 业务，担任 XX 核心系统的 Owner，技术栈是 Spring Cloud Alibaba + Nacos + Sentinel + RocketMQ + MySQL 分库分表。
     我主导了 3 件核心事情：
     ① XX 系统从 0 到 1 搭建，支撑 DAU X 百万，目前 QPS 峰值 X 万，可用性 99.99%；
     ② 解决 XX 技术难点（如大促 OOM / 分布式事务一致性），最终方案 X；
     ③ 推动组内 XX 升级（如单体拆微服务/引入全链路监控），发布时间 40min→10min，线上故障下降 70%。
     团队规模 X 人，我除了自己开发，还带 3 人的小组做 Code Review + 技术分享。"
  【结尾 30s】"我最近在学 XX（如 ZGC / JDK21 虚拟线程 / LLM Agent），想在更大的平台挑战更复杂的业务场景。以上是我的自我介绍。"

1 分钟版（HR 面或面试官忙时）：
  "面试官您好，我是 XXX，X 年 Java 经验。目前是 XX 公司的模块 Owner，带领 3 人小组，主要负责 XX 系统（1000w 月活，1w+ QPS），用 Spring Cloud Alibaba + RocketMQ + ShardingSphere 技术栈。
   过去两年主导过 XX 架构升级和 XX 技术攻关（量化一句）。
   想加入华为 OD 挑战更大规模的业务。谢谢。"
```

## 4.2 必问 8 大问题与应答模板

| 问题 | 错误回答 | ✅ 高级版模板 |
|---|---|---|
| **1. 为什么从上家公司离职？** | "996 太累 / 老板傻逼 / 钱太少" | "目前的项目进入了成熟期，未来 2 年的技术规划偏向运维和稳定性，**技术成长空间受限**。我自己希望在技术上再突破一层，接触更大规模的分布式系统和更复杂的业务场景。华为是国内顶尖的技术公司，相信在这边能获得更快的成长。" |
| **2. 为什么选择华为？** | "工资高 / 大厂背书" | "有三点：<br>① **业务体量**：华为的业务规模（XX 产品亿级用户 / 千万级并发）是我目前接触不到的，这对我的技术能力提升非常大；<br>② **技术深度**：华为在 JVM、中间件、分布式、AI 领域都有深厚的自研和沉淀，我希望有机会向优秀的同事学习；<br>③ **职业路径**：华为的晋升和技术分级体系非常清晰，我可以在架构师/技术专家的路径上长期发展。" |
| **3. 你的优缺点？** | 缺点：追求完美 / 太拼了 / 英语不好 | **优点（结合岗位 3 个）**：<br>① 技术沉淀扎实：阅读过 Spring/Dubbo/RocketMQ 核心源码，能从底层定位并解决复杂问题（如之前 XX OOM 根因定位）；<br>② 有 Owner 意识：项目遇到难题不甩锅，跨组协调推动问题最终解决（如 XX 事故连夜 36 小时修复）；<br>③ 有团队影响力：负责组内 Code Review、每周技术分享，带出 2 个新人独立承担模块。<br>**缺点（无伤大雅 + 正在改进）**：<br>之前做方案有时过分追求技术完美，导致项目进度略紧。现在改进了：做方案前先对齐业务 SLA，**技术方案匹配业务优先级**，加了 2~3 个备选方案按时间/成本权衡，目前基本都能按时交付。 |
| **4. 遇到最大的困难 + 最大成就？** | 困难："还没有遇到特别大的困难"；成就："拿了 XX 优秀员工奖" | **困难（STAR 3 分钟版，准备 1 个真困难）**：<br>S：24 年双 11 前 2 周，压测发现订单系统 5000 QPS 就大量超时，原本目标是 2w QPS，压测只剩 2 周。<br>T：作为模块 Owner 牵头全链路优化。<br>A：① Arthas profiler 火焰图定位 3 大瓶颈：DB 订单表 5 千万行无索引慢查询；Redis 热点商品单 key 网卡打爆；日志同步刷盘。<br>② 制定三步走方案：a) 联合索引 + ShardingSphere 分表；b) 热点 key Caffeine 本地缓存分片；c) 日志异步化 + 丢弃 debug。<br>③ 每天凌晨压测一次 + 每日进度同步，协调 DBA/运维 4 个团队，改了 180+ 个 commit。<br>R：最终双 11 当天天猫 QPS 峰值 2.3w，RT P99 320ms（目标 500ms），无 P0 P1 故障。<br>事后获得公司年度技术突破奖。<br>**成就（同一项目关联）**：这次调优文档沉淀为公司《大促性能调优手册》，在全公司 6 个业务线推广复用，后续 618 准备时间从 1 个月缩短到 14 天。 |
| **5. 职业规划？** | "3 年当管理 / 先做好本职" | "分两个阶段：<br>**短期（1~2 年）**：在华为 XXX 产品线（面试的那个 BU）快速熟悉业务和技术栈，成为团队的核心技术骨干，独立负责 1~2 个核心模块的设计和交付，争取 1~1.5 年达到更高技术等级。<br>**长期（3~5 年）**：向架构师 / 技术专家方向发展，一方面能独立承担 XX 系统的整体架构设计和技术选型，另一方面在 1~2 个技术方向（如分布式一致性 / 高并发调优 / 大数据实时计算）形成自己的技术专长，能代表团队对外输出技术分享和专利。<br>带团队方面：如果公司和业务有需要，我也愿意带领 3~5 人的小组往 TL 方向发展，但目前前 2 年我希望先把技术深耕扎实。" |
| **6. 是否接受加班 / 外派 / 出差？** | "绝对不接受 / 当然可以，命都可以给" | "我在做项目的时候，**项目交付优先**——比如之前双 11、版本发布、P0 故障我都主动加班甚至通宵，这在我之前几份工作都是常态。<br>只要是工作需要、项目紧急，**加班和短期出差我完全可以接受**。<br>（如果问长期外派）长期外派（比如超过 1 年常驻外地）我需要和家人沟通一下，目前我有 X 岁小孩在上学，家属需要长期照料，短期（3 个月内）完全没问题，长期可以再具体商量。"（根据个人实际情况） |
| **7. 期望薪资？** | "25k，你们看着给吧 / 越多越好" | "我目前的薪资结构是：月薪 XXk × 12 + 年终奖 X 个月 + 股票期权 X 万/年，**总包约 XX 万**。<br>我期望的涨幅是 **30% 左右（总包约 XX 万，对应月薪 XXk）**。<br>理由有三个：<br>① 我目前在原公司已经是高级开发，3 年绩效都 A / B+，本身在原公司也有涨薪空间；<br>② 我有 XX（高并发/分库分表/架构设计）的实战经验，可以直接承担高级岗位的职责；<br>③ 从整体市场行情看，这个级别高级 Java 这个涨幅是合理范围。<br>当然我也相信华为有非常规范的薪酬体系，如果面试评估后有其他的定级，咱们可以再讨论。" |
| **8. 你和领导有不同意见怎么办？** | "听领导的 / 据理力争到底" | "我一般分三步：<br>① **先倾听+复盘**：领导信息比我全，先理解他为什么这么选（时间要求？成本？业务风险？），是不是我掌握的信息不全？<br>② **数据+方案沟通**：我还是觉得我的方案更优时，不会嘴上争执，而是准备一份对比文档：两种方案的时间、成本、风险、性能指标对比，用压测数据、线上数据、技术文档支撑我的观点，和领导做一次 1 对 1 的沟通。<br>③ **最终执行**：沟通后领导坚持他的方案，那我**先按照领导的方案执行，并做好兜底预案**。上线后看真实数据反馈：如果领导的方案确实更好，我学习经验；如果实际真的有问题，带着真实数据再提出调整，领导也更容易接受。<br>总之：**对事不对人，业务结果优先，决策前充分提建议，决策后坚决执行。**"<br>（举 1 个真案例：例"XX 方案领导要 A，我提 B，结果 A 上线果然 OOM，我们按 B 预案切回，领导认可了我的方案，后续类似问题我来主导"） |

## 4.3 反问面试官阶段清单（千万不要说"没问题"！）

```
推荐高级问 3~4 个：
  ① **业务方向**（最优先问）：
     "请问咱们 XX 团队（面试的 BU）目前的核心业务是什么？现在的挑战和未来 1 年的业务规划是什么？"
     · 目的：确认业务是否有前景、是否和你想发展的方向匹配
  ② **团队技术栈 + 架构**：
     "咱们团队目前的技术栈是什么样的？有哪些自研中间件或技术沉淀？微服务规模大概多少个服务？DB 是单主还是分库分表？"
  ③ **团队规模 + 汇报关系**：
     "我要入职的话，会加入哪个小组？团队多少人？汇报对象的背景是什么？晋升的路径是怎样的？"
  ④ **技术氛围 / 培养机制**（高级很看重）：
     "团队的技术分享机制是怎样的？有没有类似 Code Review / Tech Design Review 的机制？新人入职有没有 mentor 带？"
  ⑤ **考核机制**：
     "团队的绩效怎么考核？除了业务交付，技术沉淀（专利/分享/文档）是否算入考核？"

❌ 面试前几轮千万不要问：
  - "加班多吗？有没有加班费？"（问 HR，不要问技术面，显得你怕吃苦）
  - "几点上班？年假多少天？"（入职前问 HR 或 Offer 阶段问）
  - "这个职级最低多少工资？"（技术面不谈钱，HR 面再谈）

```

---

# 五、冲刺资料清单与备考计划

## 5.1 必背源码清单（每个能讲 10 分钟+）

```
✅ Java/JUC：
  1. HashMap JDK8 putVal / resize / treeifyBin
  2. ConcurrentHashMap JDK8 initTable / putVal（CAS+synchronized）/ transfer 扩容
  3. AQS：acquire / acquireQueued / shouldPark / release / Condition await+signal
  4. ThreadPoolExecutor：execute / addWorker / runWorker / getTask
  5. Thread / ThreadLocal / ThreadLocalMap set + expungeStaleEntry 清理
  6. Synchronized 相关：ObjectMonitor C++ 源码结构 + 锁升级 4 级过程

✅ Spring 全家桶：
  7. AbstractApplicationContext.refresh() 12 步
  8. AbstractAutowireCapableBeanFactory.doCreateBean（生命周期 11 步）
  9. DefaultSingletonBeanRegistry.getSingleton 三级缓存
  10. ConfigurationClassPostProcessor.processConfigBeanDefinitions（@ComponentScan/@Bean/@Import 解析）
  11. AnnotationAwareAspectJAutoProxyCreator.wrapIfNecessary（AOP 代理创建）
  12. SpringApplication.run() 启动流程 + AutoConfigurationImportSelector（自动装配）

✅ 中间件（简历写了就背）：
  13. Dubbo：ProtocolFilterWrapper.export / DubboInvoker.doInvoke；FailoverCluster.join
  14. Sentinel：StatisticSlot.entry / FlowSlot（滑动窗口）/ DegradeSlot
  15. ShardingSphere / MyBatis 核心（有就背）

✅ MySQL：
  16. InnoDB B+ 树页结构 + lock_rec_lock 行锁加锁流程（选看）

```

## 5.2 算法刷题路径

```
3 阶段 5 周计划：
  阶段 1（1 周）快速重基础：牛客华为 OD 机试 TOP 100（HOT 按通过率刷）
    · 目标：基础题 5 分钟 AC；ACM BufferedReader 模板直接默写
  阶段 2（2 周）专题突破 1：图论 + DP + 单调栈 + 并查集
    · 力扣 + 代码随想录专题版，每个专题刷 30 道 Medium + 10 道 Hard
    · DP：背包九讲 9 种全部自己推一遍；区间 DP；状态压缩 DP
  阶段 3（1 周）专题突破 2：线段树 / Trie / 字符串 KMP / 其他高级
    · 宫水三叶 【宫水三叶】LeetCode 所有 Hard 题解
  阶段 4（1 周）真题 + 模拟：
    · 近 6 个月华为 OD 真题（CSDN / 小红书 / 朋友分享）
    · 牛客周赛 2 场 + Codeforces Div3 2 场（全真模拟 2.5h 计时）

✅ 刷题记录 Excel：每道题 字段：题号 / 题目 / 考点 / 一次 AC？ / 错因 / 三刷时间
   错题三刷法：第 2 天再做一次；第 7 天再做一次；第 30 天再做一次

✅ 每周错题合集打印，地铁通勤时反复看思路！

```

## 5.3 系统设计学习路径

```
3 阶段：
  ① 输入（2 周）：
     · 书：《System Design Interview》Alex Xu 1+2 中文版（必读）
     · 视频：B站 "系统设计面试"（高畅 / Lucifer 系列）
     · 必读：DDIA《数据密集型应用系统设计》前 6 章（存储/复制/分区/事务）
  ② 案例仿写（2 周）：
     · 选 5 个高频系统：短链/秒杀/IM/支付/排行榜
     · 每个：按照 3.2.1 的 8 步 SOP → 自己写在 Notion 上（画图 + 估算 + 细节）
     · 然后对照网上的标准答案找差距（知乎/博客"XX 系统设计"）
  ③ 真人模拟（1 周）：
     · 找同 level 朋友互面：朋友当面试官 40 分钟系统设计，全程录音
     · 听回放找自己的问题：是不是没需求澄清？是不是直接画图没说思路？

✅ 高级加分项：每道系统设计都主动画 CAP 权衡 + 说出 3~5 个量化数字（QPS/存储/带宽）
✅ 一定不要：一上来就画图！一定走 8 步 SOP！

```

## 5.4 4 周冲刺计划示例（在职，每天晚上 2 小时 + 周末 6 小时）

```
Week 1：Java + JVM + 算法基础
  工作日（每天 2h）：
    Mon：HashMap/AQS 源码 + 八股 1 轮背诵 + 算法 10 题（简单）
    Tue：JVM 内存模型 + GC 调优 1 轮背诵 + 算法 8 题（中）
    Wed：类加载 + 双亲委派 + 反序列化 1 轮 + 算法 8 题（中）
    Thu：线程池 7 大参数 + 拒绝策略 + 优雅关闭 + 算法 10 题
    Fri：ThreadLocal/volatile/synchronized 复习 + 算法并查集专题 6 题
  周末（每天 6h）：
    Sat：上午 2 套 JVM/Java 八股自测；下午 JDK 源码 3 个类手写；晚上 LeetCode 周赛 3h
    Sun：上午 Math / Arthas / MAT 工具实操（写一个模拟内存泄漏定位）；下午 10 道中等算法

Week 2：Spring 全家桶 + 并发分布式 + 算法 DP
  工作日：Spring IOC 12 步、Bean 生命周期、三级缓存、AOP 事务 8 步
    → 自动装配；Dubbo SPI 流程；分布式锁/事务对比；DP 背包/区间专题
  周末：写一个自定义 Spring Boot Starter（含 @Conditional 系列）
        手写一个分布式锁（Redis + LUA，含续期看门狗）完整代码
        1 次牛客模拟机试（3 题 2.5h）

Week 3：MySQL + 中间件（Redis/MQ/Kafka）+ 算法图论
  工作日：MySQL B+ 树计算 + MVCC + 锁 + EXPLAIN + SQL 调优
    Redis 持久化 + 跳表；Kafka/RocketMQ 原理 + 对比
    图论（拓扑/最短路）算法专题
  周末：自己搭 MySQL 主从 + Canal + Kafka，玩一次 CDC
        安装 Prometheus + Grafana 连 MySQL/Redis，做 3 个监控仪表盘
        1 次牛客困难版 3 题模拟机试

Week 4：系统设计 + 项目整理 + HR + 模拟面试
  工作日（每天 2h）：
    Mon：秒杀系统 + 短链系统 2 套 8 步 SOP 写稿背熟
    Tue：IM 系统 + 支付系统 写稿背熟
    Wed：排行榜 / 延迟任务系统 + 6 大排障 SOP 背熟
    Thu：2 个项目 STAR 稿子（写出来 1500 字/每个）+ 技术选型 3 个对比表格
    Fri：8 大 HR 问题稿子背熟 + 自我介绍 3 分钟 / 1 分钟版本 练习录音 3 遍
  周末：
    Sat：上午 朋友 / 前辈 1 小时技术模拟面试（录音）
          下午 回放修正答案，项目 STAR 稿子修改
    Sun：全天 压力模拟：上午 2.5h 机试；下午 1h 技术面八股；晚上 30min HR 面
        最后：早点睡觉，保持好状态，面试前 1h 过一遍脑图

✅ 全程贯穿：
  · 每周末一次自测：对着 Xmind 目录导图不看内容，口述每个知识点，卡住的标记
  · 标记为"不会/不熟"的点，下周反复 3 轮（艾宾浩斯遗忘曲线）
  · 所有稿子写出来：不要只在脑子里想，写出来 3000 字才会发现逻辑漏洞

```

---

# 附：真实项目 STAR 案例模板

## 附例 1：电商订单系统性能优化项目（高级版）

```
【S 背景】
我在 XX 电商公司（年 GMV 50 亿）担任订单域高级开发。订单系统是全链路核心，日订单量 200w，
24 年 618 大促前压测只有 5000 QPS（目标 3w），P99 RT 2.2s，远不达标，
离大促只剩 3 周，且团队还有 2 个新人经验不足。

【T 任务】
作为订单模块 Owner，牵头全链路性能优化。目标：3w QPS，RT P99 < 400ms，
可用性 99.99%。直接向技术总监汇报，协调 DBA、运维、压测、前端 4 个团队。

【A 行动（核心）】

一、整体架构改造 + 技术选型
  原架构：Spring Boot + MyBatis + MySQL 单库（订单表 5000w 行）+ Redis 主从。
  ① 数据库层：订单量暴涨 → 选型 ShardingSphere-JDBC 4.1.1 分库分表
     - 为什么不选 MyCat？Sharding-JDBC 是客户端分片，无中间节点少一跳，
       运维成本低（我们没有专职中间件团队），性能高 15%~20%；
       Sharding-Proxy 对我们业务透明，但要维护 3 节点 Proxy 集群；
       综合选 Sharding-JDBC（开发成本高一点，但我们能 Hold 住）。
     - 分片键 user_id（买家维度，80% 查询按用户查）；4 库 16 表（4 台 16C64G MySQL）
       主键雪花算法（ShardingSphere 内置 SNOWFLAKE）
       冷热分：半年前订单归档到历史库（T+1 离线任务），历史查询走独立接口

  ② 缓存层：
     - 只 Redis 热点不够 → 加 Caffeine 本地 L1 缓存（top 5% 热点订单）
       命中率：Redis 85% → 加本地缓存后 97%
       本地缓存失效：Spring Event + RocketMQ 异步广播（写成功后，所有实例收到消息 CACHE_INVALIDATE）
     - 缓存穿透：布隆过滤器 RedissonBloomFilter（预计容量 1 亿，误判率 0.1%），
       不存在的订单号直接返回，不用打 DB
     - 缓存击穿（查热门订单）：热点单订单 key 分片 100 份，互斥锁 RedissonRLock

  ③ 异步化：
     - 下单主流程：写订单 → 立即返回订单号；
       扣库存 / 发短信 / 发优惠券 → 发 RocketMQ 异步处理（事务消息，不丢）
     - 为什么选 RocketMQ 不选 Kafka？
       业务有事务消息需求（RocketMQ 原生半消息支持，Kafka 需要自己实现）
       团队 5 人都有 RocketMQ 经验，Kafka 经验 2 人；维护成本更低
       延迟消息功能（取消订单 30 分钟超时自动关单）RocketMQ 直接用，Kafka 自己实现时间轮

二、关键模块实现 + 核心代码
  1. 分库分表算法 + 雪花算法 ID（ShardingSphere Complex 分片算法自定义类）
  2. 下单本地消息表 + RocketMQ 事务消息：
     · 下单 + 本地消息表同一 DB 事务写
     · MQ 消费失败重试 16 次 + DLQ 钉钉告警 + T+1 对账补偿
  3. 订单查询聚合层：Spring WebFlux 聚合订单/商品/物流/优惠券，减少串行调用 6 次→并行 2 次

三、遇到的 3 大难点 + 解决方案（最关键）
  难点 1：ShardingSphere 深分页问题（LIMIT 100000,10 扫所有分片）
    - 最初方案：ShardingSphere 默认 ORDER BY xxx LIMIT m,n → 每个分片都查 LIMIT m+n → 内存合并排序，
      m=100w 时 JVM OOM。
    - 方案 A（游标分页 / 延迟关联）：
      前端传 last_id + last_create_time，下一页 WHERE id < ? AND create_time < ? ORDER BY DESC LIMIT 10
      只扫 1 个分片，直接走主键索引，O(1) 性能。
      但产品要求支持"跳第 X 页"（用户运营查历史订单），游标不满足。
    - 方案 B（二次查询 + ES）：列表查询走 Elasticsearch（Canal binlog 同步），
      ES 原生支持深分页 search_after 游标 + 页码 max_result_window = 10000（业务够用），
      详情再走 DB 主表（一致性保证）。
    - 最终：A + B 结合。前台用户端（90% 流量）走方案 A 游标；
      后台运营跳页（10%）走方案 B ES。上线后深分页 P99 3.5s → 80ms。

  难点 2：分布式事务超时重试导致重复
    - TCC Cancel 比 Try 先到（网络乱序），产生悬挂
    - TCC 幂等：多次 Confirm 重复扣库存
    - 解决方案：tcc_fence_log（事务日志表）+ 唯一键（xid + branch_id）
      ① Try 前 INSERT status=TRYING（已存在键冲突抛异常拒绝执行）
      ② Cancel 执行前：TRY 不存在 → 视为空回滚，直接 INSERT CANCELED 返回成功
      ③ Confirm/Cancel 状态机（TRYING→CONFIRMING→DONE），已 DONE 请求直接返回成功
    - 上线后用 JMeter 造 5% 乱序重试，无 1 条数据不一致

  难点 3：大促前压测遇到 Redis 主从全同步阻塞（主节点执行 BGSAVE，主线程 fork 20G 内存 4s 阻塞）
    - 临时方案：压测期间 config set save "" 关掉 RDB（事后恢复）
    - 长期方案：Redis Cluster 8 主 8 从（每主 5G 内存，fork < 200ms）
      再加 2 个独立从节点（持久化专用），读写分离主负责写，持久化专从负责 BGSAVE
    - 同时开启 repl-diskless-sync yes（无盘复制，Socket 直传 RDB，不写本地文件）

四、性能调优全过程（量化前后对比）
  - 调优工具：JMeter 5.0 + Arthas profiler + SkyWalking P99 Trace
  - 调优步骤（3 轮迭代）：
    第一轮：加索引 + 去掉 18 条 N+1 查询 → 5000 QPS → 8000 QPS（+60%）
    第二轮：分库分表 + 缓存层改造 → 1.2w QPS → 2.1w QPS
    第三轮：异步化 + Tomcat 线程池（maxThreads 200→800）+ G1 GC 参数调优
      + MySQL sync_binlog=0（大促 24h 期间折中，24h 后改回 1）
      → 最终：3.2w QPS，RT P99 360ms，JVM Young GC 1.1s 调优后 450ms/次，Full GC 0。

【R 结果（量化）】：
  - 618 大促当天 0 点峰值 3.4w QPS，**无 P0/P1 故障**，全天订单量 800w（+300% 同比）
  - RT P99：2.2s → 360ms（降低 84%）
  - 数据库成本：单 DB 4 台主 16 台从总磁盘 12T → 分库分表后 8T 磁盘（降低 33%）
  - 团队沉淀：《大促性能调优手册》+《ShardingSphere 最佳实践》公司 Wiki
    后续 618/双 11 准备时间从 4 周 → 1.5 周
  - 个人：年度绩效 A，晋升候选人提名

【复盘反思】
  如果重做我有两个优化：
  ① ShardingSphere 当时用的 4.x，后续 5.x 有 DistSQL 管理分片规则更灵活，可以提前做技术预研升级；
  ② 订单号生成除了雪花算法，还要加"业务前缀 + 日期码"（比如 DD20260812 + 雪花），
    方便客服根据订单号肉眼判断日期，当时漏了，后加了个转换层（有一定维护成本）。
  通过这个项目我完整掌握了 ShardingSphere 源码 + 分布式事务 TCC 落地实战 + 性能调优全流程，
  带出的 2 个新人现在独立负责订单查询和订单历史两个子模块，年底也拿了 A 绩效。

```

---

> **文档使用建议**：
> 1. 把 Part1 + Part2a + Part2b 按顺序通读一遍，标记出"不会/不熟"的点；
> 2. 用艾宾浩斯遗忘曲线反复 3 轮复习（第 2 天、第 7 天、第 30 天）；
> 3. 算法 + 八股 + 系统设计 + 项目 STAR **一定要自己写出来，不要只在脑子里想**，写出来的东西面试时才不会紧张忘；
> 4. 每次模拟面试录音，回放找自己的口头禅（嗯…/那个…）和逻辑断点，刻意练习。

祝面试顺利！Offer 稳拿！🚀
