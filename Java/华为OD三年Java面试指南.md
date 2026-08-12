# 华为 OD Java 面试完全指南（3 年经验版）

> 本文档针对 3 年 Java 开发经验的候选人，覆盖技术一面、技术二面、HR 综合面全流程，不含机试部分。每个知识点均配备详细解答与真实项目案例。

---

## 目录

- [一、面试流程总览](#一面试流程总览)
- [二、技术一面（基础 + 框架 + 数据库）](#二技术一面基础--框架--数据库)
  - [2.1 Java 基础核心](#21-java-基础核心)
    - [2.1.1 集合框架（HashMap 为主）](#211-集合框架hashmap-为主)
    - [2.1.2 String 相关](#212-string-相关)
    - [2.1.3 异常体系](#213-异常体系)
    - [2.1.4 泛型与反射](#214-泛型与反射)
    - [2.1.5 Java 8+ 新特性](#215-java-8-新特性)
  - [2.2 JVM 基础](#22-jvm-基础)
    - [2.2.1 内存模型](#221-内存模型)
    - [2.2.2 垃圾回收](#222-垃圾回收)
    - [2.2.3 类加载机制](#223-类加载机制)
  - [2.3 并发编程](#23-并发编程)
    - [2.3.1 线程基础与 synchronized](#231-线程基础与-synchronized)
    - [2.3.2 volatile 与 JMM](#232-volatile-与-jmm)
    - [2.3.3 线程池](#233-线程池)
    - [2.3.4 AQS 与 Lock](#234-aqs-与-lock)
    - [2.3.5 ThreadLocal](#235-threadlocal)
  - [2.4 Spring / Spring Boot](#24-spring--spring-boot)
    - [2.4.1 IOC 与 AOP](#241-ioc-与-aop)
    - [2.4.2 Spring Bean 生命周期](#242-spring-bean-生命周期)
    - [2.4.3 Spring Boot 自动装配](#243-spring-boot-自动装配)
    - [2.4.4 事务管理](#244-事务管理)
  - [2.5 MySQL 数据库](#25-mysql-数据库)
    - [2.5.1 索引原理](#251-索引原理)
    - [2.5.2 事务与隔离级别](#252-事务与隔离级别)
    - [2.5.3 锁机制](#253-锁机制)
    - [2.5.4 SQL 优化实战](#254-sql-优化实战)
  - [2.6 Redis 缓存](#26-redis-缓存)
    - [2.6.1 数据结构与场景](#261-数据结构与场景)
    - [2.6.2 缓存三大问题](#262-缓存三大问题)
    - [2.6.3 持久化与高可用](#263-持久化与高可用)
- [三、技术二面（项目深挖 + 系统设计 + 场景题）](#三技术二面项目深挖--系统设计--场景题)
  - [3.1 项目深挖 STAR 法则](#31-项目深挖-star-法则)
  - [3.2 高频系统设计题](#32-高频系统设计题)
  - [3.3 场景题与线上排障](#33-场景题与线上排障)
- [四、HR / 综合面](#四hr--综合面)
  - [4.1 自我介绍模板](#41-自我介绍模板)
  - [4.2 必问问题与应答](#42-必问问题与应答)
  - [4.3 反问面试官](#43-反问面试官)
- [五、备考清单](#五备考清单)

---

# 一、面试流程总览

华为 OD Java 面试（3 年经验）一般经历以下环节：

| 环节 | 时长 | 面试官 | 核心考察 |
|---|---|---|---|
| 技术一面 | 45~60 分钟 | 技术面试官 | Java 基础、JVM、并发、Spring、MySQL、Redis |
| 技术二面 | 45~60 分钟 | 技术面试官 / 架构师 | 项目深挖、系统设计、场景排障、技术决策 |
| HR / 综合面 | 30~45 分钟 | HR / 主管 | 自我介绍、离职原因、职业规划、薪资期望 |

> **3 年经验定位**：能独立承担模块开发，理解常用框架原理，有一定调优和排障经验，不需要达到架构师级别，但必须能讲清楚"为什么这样做"而不只是"会用"。

---

# 二、技术一面（基础 + 框架 + 数据库）

## 2.1 Java 基础核心

### 2.1.1 集合框架（HashMap 为主）

**Q1：HashMap 的底层结构（JDK 8）？**

HashMap 在 JDK 8 中采用 **数组 + 链表 + 红黑树** 的结构：

```
Node<K,V>[] table  →  每个槽位是一个链表头节点
  桶下标计算：i = (n - 1) & hash
  
  table[0] → null
  table[1] → Node → Node → Node → null        （链表）
  table[2] → TreeNode（红黑树）                （链表长度 ≥ 8 且 table.length ≥ 64 时转树）
  table[3] → null
  ...
```

**put 方法完整流程**：

1. 计算 hash：`h = key.hashCode(); hash = h ^ (h >>> 16)` — 高 16 位异或低位，让高位也参与运算，减少碰撞
2. table 为空 → `resize()` 初始化（默认容量 16，loadFactor 0.75）
3. 定位桶下标：`i = (n - 1) & hash` — 用位运算代替取模，前提是 n 是 2 的幂
4. 桶为空 → 直接放入
5. 桶不为空（hash 碰撞）：
   - key 相同（== 或 equals）→ 覆盖旧 value
   - 是 TreeNode → 红黑树插入
   - 是链表 → 尾插法，插入后判断 `binCount >= 7`（第 8 个节点）→ 若 `table.length < 64` 则扩容，否则树化
6. `++size`，若 `size > threshold`（capacity × loadFactor）→ `resize()` 扩容 2 倍

> **为什么 JDK 8 改为尾插法？** JDK 7 头插法在并发扩容时可能形成链表环，导致 get 死循环。尾插法避免了这个问题，但 HashMap 依然不是线程安全的。

**Q2：HashMap 扩容机制？**

```
扩容触发：size > threshold（capacity × loadFactor）
扩容方式：容量翻倍（newCap = oldCap << 1）

JDK 8 扩容优化 —— 重哈希时元素位置要么不变，要么移动 oldCap 位置：
  原位置：i
  新位置：i 或 i + oldCap
  
  判断依据：hash & oldCap == 0 → 留原位；== oldCap → 移到 i + oldCap
  这样避免了重新计算每个元素的 hash，只需判断最高位 bit。
```

**Q3：HashMap 树化阈值为什么是 8？**

源码注释中解释：理想情况下随机 hashCode 服从泊松分布（λ=0.5），一个桶中出现 8 个节点的概率仅 0.00000006（约 6 千万次才 1 次）。8 是概率极小的阈值，防止频繁树化/链化。退化阈值是 6（留缓冲）。

**Q4：HashMap 线程不安全的表现？**

1. 并发 put 可能丢数据：两个线程同时计算到空桶，CAS 只有一个成功
2. size++ 不是原子操作，统计不准
3. JDK 7 头插法扩容时链表成环 → get 死循环（JDK 8 尾插已修复此问题）

> **替代方案**：`ConcurrentHashMap`（JDK 8 用 CAS + synchronized 锁单个桶，并发度更高）

**项目案例**：

```
项目场景：电商订单系统中，用 HashMap 缓存商品信息（productId → ProductInfo）
问题：大促期间并发写入导致缓存数据丢失，部分商品信息查询不到
排查：通过 jstack 发现 HashMap 内部数据不一致
解决方案：
  ① 改为 ConcurrentHashMap，并发安全
  ② 进一步优化：加 Caffeine 本地缓存（TTL 5 分钟，最大容量 1 万），Redis 作为二级缓存
  效果：缓存命中率 85% → 97%，接口 RT 从 80ms 降到 20ms
```

---

### 2.1.2 String 相关

**Q1：String 为什么不可变？**

```
String 类用 final 修饰，不可被继承；
内部 char[]（JDK 9+ 为 byte[]）用 final + private 修饰，不可修改。

好处：
  ① 线程安全：多线程共享无需同步
  ② 安全性：String 作为 HashMap 的 Key 不会变，防止 hashCode 变化导致 get 不到
  ③ 字符串常量池：不可变才能安全共享同一个引用
  ④ 安全：防止网络连接 / 文件路径被恶意篡改
```

**Q2：String、StringBuilder、StringBuffer 区别？**

| 类 | 可变性 | 线程安全 | 性能 | 适用场景 |
|---|---|---|---|---|
| String | 不可变 | 安全（不可变） | 拼接慢（每次 new） | 少量字符串操作 |
| StringBuilder | 可变 | 不安全 | 最快 | 单线程大量拼接 |
| StringBuffer | 可变 | 安全（synchronized） | 较慢 | 多线程大量拼接 |

**Q3：`new String("abc")` 创建了几个对象？**

- 如果常量池中没有 "abc"：创建 2 个对象 — 常量池中的 "abc" + 堆中的 String 对象
- 如果常量池中已有 "abc"：创建 1 个对象 — 堆中的 String 对象

```java
String s1 = "abc";              // 常量池中创建 "abc"
String s2 = new String("abc");  // 堆中创建新对象，常量池中已有不重复创建
String s3 = "abc";              // 指向常量池中同一个 "abc"

s1 == s3        // true（同一引用）
s1 == s2        // false（s2 是堆对象）
s1.equals(s2)   // true（值相等）
s2.intern() == s1  // true（intern 返回常量池引用）
```

**项目案例**：

```
项目场景：日志系统中循环拼接 JSON 字符串
问题代码：String result = ""; for (Order o : orders) { result += o.toJson(); }
  → 每次拼接都创建新 String 对象和 StringBuilder，5000 条订单产生 5000+ 临时对象
优化：改用 StringBuilder.append()，减少对象创建
效果：GC 频率降低 60%，接口 RT 从 200ms 降到 50ms
```

---

### 2.1.3 异常体系

**Q1：Java 异常体系结构？**

```
Throwable
  ├── Error（不应捕获，程序无法恢复）
  │     ├── OutOfMemoryError        堆溢出
  │     ├── StackOverflowError      栈溢出
  │     └── VirtualMachineError
  └── Exception
        ├── RuntimeException（非受检，编译器不强制处理）
        │     ├── NullPointerException
        │     ├── ClassCastException
        │     ├── ArrayIndexOutOfBoundsException
        │     └── IllegalArgumentException
        └── 其他 Exception（受检，必须 try-catch 或 throws）
              ├── IOException
              ├── SQLException
              └── ClassNotFoundException
```

**Q2：受检异常 vs 非受检异常？**

| 类型 | 例子 | 处理方式 | 设计意义 |
|---|---|---|---|
| 受检异常（Checked） | IOException, SQLException | 必须 try-catch 或 throws | 编译期检查，提醒调用者处理可恢复的异常 |
| 非受检异常（Unchecked） | NPE, ClassCastException | 不强制 | 程序逻辑错误，应该修代码而不是捕获 |

**项目案例**：

```
项目场景：订单服务调用支付服务
设计：
  ① 自定义业务异常 BizException extends RuntimeException（非受检）
     - 优点：不污染接口签名，业务代码干净
     - 全局异常处理器 @ControllerAdvice 统一捕获返回错误码
  
  ② 自定义支付异常 PaymentException extends Exception（受检）
     - 支付类异常调用方必须处理（try-catch 或 throws）
     - 提醒调用者：支付可能失败，需要降级或重试

  // 全局异常处理
  @RestControllerAdvice
  public class GlobalExceptionHandler {
      @ExceptionHandler(BizException.class)
      public Result<?> handleBiz(BizException e) {
          log.warn("业务异常: code={}, msg={}", e.getCode(), e.getMessage());
          return Result.fail(e.getCode(), e.getMessage());
      }
      @ExceptionHandler(Exception.class)
      public Result<?> handleSystem(Exception e) {
          log.error("系统异常", e);
          return Result.fail("SYSTEM_ERROR", "系统繁忙");
      }
  }
```

---

### 2.1.4 泛型与反射

**Q1：泛型擦除机制？**

Java 泛型是编译期特性，编译后类型信息被擦除：

```java
List<String> list1 = new ArrayList<>();
List<Integer> list2 = new ArrayList<>();
// 编译后都是 ArrayList，运行时 list1.getClass() == list2.getClass() → true

// 为什么要擦除？JDK 5 引入泛型时的兼容性考虑，让泛型代码和旧版 JVM 兼容
```

**Q2：泛型上下界？**

```java
// 上界 <? extends T>：可读不可写（生产者）
public static double sum(List<? extends Number> list) {
    double total = 0;
    for (Number n : list) total += n.doubleValue();  // ✅ 可读
    // list.add(1);  // ❌ 不可写（不知道实际类型）
    return total;
}

// 下界 <? super T>：可写不可读（消费者）
public static void addNumbers(List<? super Integer> list) {
    list.add(1);  // ✅ 可写 Integer
    // Number n = list.get(0);  // ❌ 不可读（返回 Object）
}
// PECS 原则：Producer Extends, Consumer Super
```

**Q3：反射的应用场景？**

```
1. Spring IOC：读取 @Component 注解，反射创建 Bean 实例
2. MyBatis：Mapper 接口代理，反射调用 SQL 方法
3. JSON 序列化：反射读取对象字段生成 JSON
4. 动态代理：JDK Proxy / CGLIB
5. 注解处理：@Autowired 注入依赖时反射 set 字段
```

**项目案例**：

```
项目场景：设计通用的 Excel 导出工具
需求：传入任意 List<T>，自动根据注解导出 Excel

实现：
  ① 自定义注解 @ExcelColumn(name = "订单号", order = 1)
  ② 反射读取 T 的 Class → getDeclaredFields() → 扫描 @ExcelColumn 注解
  ③ 按注解 order 排序 → 反射 getter 方法获取值 → 写入 Excel

  public <T> void export(List<T> data, Class<T> clazz, OutputStream out) {
      Field[] fields = clazz.getDeclaredFields();
      List<Field> annotated = Arrays.stream(fields)
          .filter(f -> f.isAnnotationPresent(ExcelColumn.class))
          .sorted(Comparator.comparingInt(f -> f.getAnnotation(ExcelColumn.class).order()))
          .collect(Collectors.toList());
      // 写表头 → 反射取值写数据行...
  }

效果：全公司 8 个业务线复用，减少重复代码 3000+ 行
```

---

### 2.1.5 Java 8+ 新特性

**Q1：Stream API 常用操作？**

```java
List<Order> orders = ...;

// 过滤 + 映射 + 收集
List<String> paidOrderNos = orders.stream()
    .filter(o -> o.getStatus() == OrderStatus.PAID)
    .map(Order::getOrderNo)
    .collect(Collectors.toList());

// 分组
Map<Long, List<Order>> byUser = orders.stream()
    .collect(Collectors.groupingBy(Order::getUserId));

// 按用户分组并求总金额
Map<Long, BigDecimal> userAmount = orders.stream()
    .collect(Collectors.groupingBy(
        Order::getUserId,
        Collectors.reducing(BigDecimal.ZERO, Order::getAmount, BigDecimal::add)
    ));

// 并行流（数据量大时）
long count = orders.parallelStream()
    .filter(o -> o.getAmount().compareTo(new BigDecimal("1000")) > 0)
    .count();
```

**Q2：Optional 怎么用？**

```java
// 避免空指针的链式调用
String city = Optional.ofNullable(user)
    .map(User::getAddress)
    .map(Address::getCity)
    .orElse("未知城市");

// ifPresent：存在才执行
Optional.ofNullable(order).ifPresent(o -> sendNotification(o));

// orElseThrow：不存在抛异常
Order order = Optional.ofNullable(orderMapper.findById(id))
    .orElseThrow(() -> new BizException("订单不存在"));
```

**Q3：Lambda 表达式本质？**

Lambda 本质是函数式接口的匿名实现。编译后生成 `invokedynamic` 指令，运行时通过 `LambdaMetafactory` 生成代理类。

```java
// 函数式接口
@FunctionalInterface
public interface OrderProcessor {
    void process(Order order);
}

// Lambda 简写
OrderProcessor processor = o -> System.out.println(o.getOrderNo());

// 常用四大函数式接口：
// Function<T,R>   → R apply(T t)         转换
// Predicate<T>    → boolean test(T t)    判断
// Consumer<T>     → void accept(T t)     消费
// Supplier<T>     → T get()              生产
```

**项目案例**：

```
项目场景：订单导出功能，需要按多条件过滤
优化前：多层 if-else 嵌套，代码 200+ 行，维护困难
优化后：使用 Stream + 策略模式

  public List<Order> filterOrders(List<Order> orders, OrderQuery query) {
      return orders.stream()
          .filter(o -> query.getStatus() == null || o.getStatus() == query.getStatus())
          .filter(o -> query.getUserId() == null || o.getUserId().equals(query.getUserId()))
          .filter(o -> query.getMinAmount() == null || o.getAmount().compareTo(query.getMinAmount()) >= 0)
          .filter(o -> query.getStartDate() == null || !o.getCreateTime().isBefore(query.getStartDate()))
          .filter(o -> query.getEndDate() == null || !o.getCreateTime().isAfter(query.getEndDate()))
          .sorted(Comparator.comparing(Order::getCreateTime).reversed())
          .skip((long) (query.getPage() - 1) * query.getSize())
          .limit(query.getSize())
          .collect(Collectors.toList());
  }

效果：代码从 200 行 → 15 行，可读性大幅提升，新增过滤条件只需加一行 filter
```

---

## 2.2 JVM 基础

### 2.2.1 内存模型

**Q1：JVM 运行时数据区？**

```
┌──────────────────────────────────────────────────────────┐
│ 【线程私有】                                                │
│  ① 程序计数器（PC Register）                                │
│    - 当前线程执行的字节码行号，唯一不会 OOM 的区               │
│                                                              │
│  ② 虚拟机栈（VM Stack）                                      │
│    - 每个方法调用创建一个栈帧：                                 │
│      ├ 局部变量表：基本类型 + 对象引用                          │
│      ├ 操作数栈：字节码指令操作的临时栈                         │
│      ├ 动态链接：指向运行时常量池的方法引用                      │
│      └ 方法返回地址                                          │
│    - StackOverflowError：递归太深                             │
│    - 参数 -Xss 设置栈大小（默认 512KB~1MB）                   │
│                                                              │
│  ③ 本地方法栈（Native Method Stack）                          │
│    - 为 Native 方法服务                                       │
│                                                              │
├──────────────────────────────────────────────────────────┤
│ 【线程共享】                                                  │
│  ④ 堆（Heap） — GC 主战场                                    │
│    - 新生代（Eden : S0 : S1 = 8:1:1）                        │
│    - 老年代                                                   │
│    - 参数：-Xms 初始 / -Xmx 最大                              │
│                                                              │
│  ⑤ 方法区（JDK 8+ 为元空间 Metaspace，使用本地内存）           │
│    - 存储类元信息、常量、静态变量                             │
│    - -XX:MaxMetaspaceSize（默认无上限，必须设！）              │
│                                                              │
└──────────────────────────────────────────────────────────┘
```

**Q2：JDK 7 vs JDK 8 方法区变化？**

```
JDK 7：永久代（PermGen），在堆中，-XX:PermSize / -XX:MaxPermSize
JDK 8+：元空间（Metaspace），使用本地内存（Native Memory），-XX:MetaspaceSize / -XX:MaxMetaspaceSize

变化原因：
  ① 永久代大小固定，容易 OOM（尤其是动态生成类多的场景如 CGLIB、Groovy）
  ② GC 效率低，Full GC 才回收永久代
  ③ 方便与 JRockit 合并
```

**Q3：对象创建过程？**

```
new Object() 的完整过程：
  1. 类加载检查：检查常量池中类的符号引用是否已加载、解析、初始化
  2. 分配内存：
     - 指针碰撞（内存规整）：Serial/ParNew 收集器
     - 空闲列表（内存碎片）：CMS 收集器
     - TLAB（Thread Local Allocation Buffer）：每个线程预分配一块，避免 CAS
  3. 内存清零：分配的空间初始化为零值
  4. 设置对象头：设置 Mark Word（hash、GC age、锁状态）+ Klass Pointer（类元数据指针）
  5. 执行 <init>：构造方法初始化
```

**项目案例**：

```
项目场景：线上服务突然 OOM，堆内存溢出
现象：日志报 java.lang.OutOfMemoryError: Java heap space
排查步骤：
  ① JVM 启动参数加了 -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/opt/logs/heap.hprof
  ② OOM 后拿到 hprof 文件，用 Eclipse MAT 分析
  ③ Dominator Tree 发现一个 HashMap 占了 2.5G（总堆 4G）
  ④ 查看引用链：一个定时任务把 3 个月的订单全部加载到内存做统计
  ⑤ 根因：SELECT * FROM order WHERE create_time > '3个月前' 一次查 500 万行
解决方案：
  ① 改为分页查询，每页 1000 条流式处理
  ② 统计改为 SQL 聚合（SUM/COUNT），不在 Java 内存中算
  ③ 加上 -Xmx4g -Xms4g（避免动态扩容）
效果：内存占用从 4G 降到 800M，再无 OOM
```

---

### 2.2.2 垃圾回收

**Q1：如何判断对象可回收？**

```
可达性分析算法：从 GC Roots 出发，沿引用链走，走不到的对象就是可回收的。

GC Roots 包括：
  ① 虚拟机栈中局部变量引用的对象
  ② 方法区中静态变量 / 常量引用的对象
  ③ 本地方法栈 JNI 引用的对象
  ④ synchronized 持有的对象
```

**Q2：四种引用类型？**

| 引用类型 | 回收时机 | 用途 | 代码示例 |
|---|---|---|---|
| 强引用 | 永不回收（除非断开引用） | 普通对象 | `Object o = new Object()` |
| 软引用 | 内存不足时回收 | 缓存 | `SoftReference<Object>` |
| 弱引用 | 下次 GC 必回收 | ThreadLocal key | `WeakReference<Object>` |
| 虚引用 | 不影响生命周期，仅通知 | 堆外内存管理 | `PhantomReference` |

**Q3：GC 算法有哪些？**

```
① 标记-清除（Mark-Sweep）
   - 标记可达对象 → 清除不可达
   - 缺点：内存碎片
   - 适用：CMS 老年代

② 复制算法（Copying）
   - 内存分两块，存活对象复制到另一半，前半清空
   - 优点：无碎片
   - 缺点：浪费一半空间
   - 适用：新生代（98% 朝生夕死，存活少）

③ 标记-整理（Mark-Compact）
   - 标记后，存活对象向一端移动，边界外清除
   - 优点：无碎片
   - 缺点：移动对象慢
   - 适用：老年代

④ 分代收集
   - 新生代用复制算法，老年代用标记-清除或标记-整理
```

**Q4：常用垃圾回收器对比？**

| 回收器 | 适用代 | 算法 | 特点 | 适用场景 |
|---|---|---|---|---|
| Serial / Serial Old | 新/老 | 复制/整理 | 单线程，STW 长 | 客户端、小堆 |
| ParNew | 新 | 复制 | 多线程，配合 CMS | 配合 CMS |
| Parallel Scavenge / Parallel Old | 新/老 | 复制/整理 | 吞吐量优先 | 后台计算 |
| CMS | 老 | 标记-清除 | **低延迟**，并发标记 | Web 应用（JDK 8 前主流） |
| G1 | 整代 | 复制+整理 | **可预测停顿**，Region 分区 | JDK 9 默认，大堆 |

**CMS 四步流程**（重点）：

```
① 初始标记（STW）：标记 GC Roots 直接引用的对象（很快）
② 并发标记：用户线程并行，从 GC Roots 往下全链标记
③ 重新标记（STW）：修正并发标记期间用户线程变动的引用
④ 并发清除：用户线程并行，清除不可达对象

问题：
  - 标记-清除 → 内存碎片（Full GC 时退化为 Serial Old 单线程整理，STW 超长）
  - 浮动垃圾：并发清除期间新产生的垃圾只能下次回收
  - CPU 占用：并发阶段占用 (核数+3)/4 条线程
```

**项目案例**：

```
项目场景：订单服务使用 CMS 收集器，大促期间频繁 Full GC，STW 3~5 秒
排查：
  ① jstat -gcutil <pid> 5000 观察 GC 趋势
  ② 发现 Old 代 85%+ 触发 CMS，但并发回收赶不上分配速度
  ③ 退化成 Serial Old 单线程 Full GC，STW 5 秒 → 接口超时
  
优化方案：
  ① 升级到 G1 收集器（-XX:+UseG1GC -XX:MaxGCPauseMillis=200）
  ② -Xms4g -Xmx4g（初始堆 = 最大堆，避免动态扩容）
  ③ -XX:G1HeapRegionSize=8m（Region 8MB）
  ④ 代码层面优化：减少大对象分配（批量查询改为流式）
  
效果：Full GC 0 次，Young GC STW 50ms，接口 P99 RT 300ms
```

---

### 2.2.3 类加载机制

**Q1：类加载过程？**

```
加载 → 验证 → 准备 → 解析 → 初始化 → 使用 → 卸载

  1. 加载：通过全限定名获取类的二进制字节流，堆中生成 Class 对象
  2. 验证：确保 Class 文件符合 JVM 规范（魔数 0xCAFEBABE 等）
  3. 准备：静态变量分配内存并赋零值
     - static int a = 123 → 准备阶段 a=0，初始化阶段才 a=123
     - static final int b = 456 → 准备阶段直接 b=456（ConstantValue 属性）
  4. 解析：符号引用 → 直接引用
  5. 初始化：执行 <clinit>() 方法（static 变量赋值 + static 块）
     - JVM 保证 <clinit>() 线程安全（多线程只有一个执行，其他阻塞）
```

**Q2：双亲委派模型？**

```
三层类加载器：
  Bootstrap ClassLoader → 加载 JDK 核心类（rt.jar）
    ↓ 委派
  Extension/Platform ClassLoader → 加载扩展类（jre/lib/ext）
    ↓ 委派
  Application ClassLoader → 加载用户 classpath
  
委派流程（ClassLoader.loadClass）：
  ① 先 findLoadedClass(name) 查是否已加载
  ② 未加载 → parent.loadClass(name) 向上委派
  ③ 上层都找不到 → 自己 findClass(name) 加载

好处：
  ① 安全：防止篡改核心类（自己写 java.lang.String，Bootstrap 先加载了真的）
  ② 避免重复加载（parent 已加载的 child 不再加载）
```

**Q3：打破双亲委派的场景？**

```
① Tomcat：每个 WebApp 有自己的 ClassLoader，先自己找再委派父（实现 WAR 包隔离）
② SPI 机制：DriverManager 需要加载 classpath 的数据库驱动
   → 通过 Thread.currentThread().getContextClassLoader() 反向加载
③ OSGi：每个 Bundle 独立 ClassLoader，网状委派
④ 热部署：自定义 ClassLoader 重写 loadClass()，不委派 parent
```

**项目案例**：

```
项目场景：公司自研规则引擎，支持热更新规则
需求：运营修改规则后不重启服务，动态加载新的规则类
实现：
  ① 自定义 RuleClassLoader extends ClassLoader
  ② 重写 findClass()：从指定目录读取 .class 文件字节流
  ③ 规则变更时：new RuleClassLoader() → loadClass("NewRule") → 创建新实例
  ④ 旧 ClassLoader 不再被引用 → GC 时卸载旧类

  public class RuleClassLoader extends ClassLoader {
      private String ruleDir;
      @Override
      protected Class<?> findClass(String name) throws ClassNotFoundException {
          byte[] bytes = Files.readAllBytes(Paths.get(ruleDir, name + ".class"));
          return defineClass(name, bytes, 0, bytes.length);
      }
  }

效果：规则热更新秒级生效，不需要重启服务
```

---

## 2.3 并发编程

### 2.3.1 线程基础与 synchronized

**Q1：创建线程的方式？**

```java
// 1. 继承 Thread
class MyThread extends Thread {
    public void run() { System.out.println("running"); }
}
new MyThread().start();

// 2. 实现 Runnable（推荐，接口多继承）
new Thread(() -> System.out.println("running")).start();

// 3. 实现 Callable + FutureTask（有返回值）
FutureTask<String> future = new FutureTask<>(() -> "result");
new Thread(future).start();
String result = future.get();  // 阻塞等待

// 4. 线程池（生产环境推荐）
executor.submit(() -> System.out.println("running"));
```

**Q2：synchronized 底层原理？**

```
synchronized 加在代码块：编译后加 monitorenter / monitorexit 指令
synchronized 加在方法：方法访问标志 ACC_SYNCHRONIZED

对象头 Mark Word 存储锁状态（64 位 JVM）：
  ┌─────────────┬──────┬─────┐
  │ 锁状态       │ 标志 │ 说明 │
  ├─────────────┼──────┼─────┤
  │ 无锁         │ 01   │     │
  │ 偏向锁       │ 01   │ CAS 记录线程 ID，零开销 │
  │ 轻量级锁     │ 00   │ CAS 自旋 │
  │ 重量级锁     │ 10   │ OS Mutex，park/unpark │
  └─────────────┴──────┴─────┘

锁升级过程（JDK 6 引入优化）：
  无锁 → 偏向锁 → 轻量级锁（CAS 自旋）→ 重量级锁（OS Mutex）
  升级是单向的，只能升不能降
```

**Q3：synchronized 与 ReentrantLock 区别？**

| 维度 | synchronized | ReentrantLock |
|---|---|---|
| 实现 | JVM 内置（monitorenter/exit） | JDK API 层（AQS + CAS） |
| 锁类型 | 非公平 + 可重入 | 可公平 / 可非公平 + 可重入 |
| 可中断 | 不可 | `lockInterruptibly()` 可 |
| 超时获取 | 不可 | `tryLock(timeout)` 可 |
| 多条件变量 | 只有 1 个 wait/notify | `newCondition()` 可多个 |
| 自动释放 | 是（异常/结束自动释放） | 否（必须 finally unlock） |
| 性能（竞争少） | 相当 | 相当 |
| 性能（竞争激烈） | 一般 | AQS+CAS 更灵活 |

**项目案例**：

```
项目场景：库存扣减并发问题
问题代码：
  public boolean deductStock(Long productId, int qty) {
      Integer stock = mapper.getStock(productId);
      if (stock >= qty) {
          mapper.updateStock(productId, stock - qty);
          return true;
      }
      return false;
  }
  → 并发下"检查-扣减"不是原子的，超卖

方案演进：
  ① synchronized 同步方法
     → 问题：性能差，单线程串行；分布式多 JVM 无效
  ② 数据库乐观锁
     UPDATE product SET stock = stock - #{qty} WHERE id = #{id} AND stock >= #{qty}
     → 问题：高并发下大量失败重试
  ③ Redis 预扣库存（Lua 原子操作）
     local stock = redis.call('GET', KEYS[1])
     if tonumber(stock) >= tonumber(ARGV[1]) then
         return redis.call('DECRBY', KEYS[1], ARGV[1])
     else return -1 end
     → 最终方案：Redis 预扣 + MQ 异步下单 + DB 兜底
  效果：支撑 1w QPS，0 超卖
```

---

### 2.3.2 volatile 与 JMM

**Q1：volatile 的两大作用？**

```
① 可见性：写 volatile 变量立即刷回主内存，读 volatile 变量从主内存重新读
② 有序性：禁止指令重排（volatile 前后插入内存屏障）

注意：volatile 不保证原子性！i++ 仍然不是线程安全的
```

**Q2：DCL 单例为什么必须加 volatile？**

```java
public class Singleton {
    private static volatile Singleton INSTANCE;  // ← 必须 volatile
    private Singleton() {}
    public static Singleton getInstance() {
        if (INSTANCE == null) {
            synchronized (Singleton.class) {
                if (INSTANCE == null) {
                    INSTANCE = new Singleton();  // ← 这行可能重排
                }
            }
        }
        return INSTANCE;
    }
}
// new Singleton() 三步：
//   1. 分配内存  2. 初始化对象  3. 引用指向内存
// JVM 可能重排为 1→3→2：线程 A 执行到 3（还没 2），INSTANCE != null
// 线程 B 判断非空，直接返回未初始化对象 → NPE！
// volatile 禁止 1-3 的重排，保证 2 先于 3 完成
```

**Q3：Java 内存模型（JMM）？**

```
JMM 定义了线程和主内存之间的关系：
  - 每个线程有本地工作内存（CPU 缓存 / 寄存器）
  - 所有变量存储在主内存
  - 线程不能直接读写主内存，必须通过工作内存

JMM 8 种操作：
  lock → unlock → read → load → use → assign → store → write
  规则：read/load 必须连续，store/write 必须连续

happens-before 原则（保证前一个操作的结果对后一个可见）：
  ① 程序顺序规则（同线程内代码顺序）
  ② volatile 变量规则（volatile 写先于读）
  ③ 锁规则（unlock 先于后续 lock）
  ④ 线程启动规则（Thread.start() 先于线程内所有操作）
  ⑤ 线程终止规则（线程内所有操作先于 Thread.isAlive() 返回 false）
  ⑥ 传递性（A happens-before B，B happens-before C → A happens-before C）
```

**项目案例**：

```
项目场景：订单处理系统中，工作线程根据 run flag 决定是否继续运行
问题代码：
  private static boolean running = true;  // ← 非 volatile
  // 线程 A：while(running) { process(); }
  // 线程 B：running = false; // 停止
  → 线程 A 可能永远看不到 running = false（CPU 缓存，可见性问题）
  → 线程 A 一直运行，无法停止

修复：private static volatile boolean running = true;
效果：线程 B 修改后，线程 A 立即可见，正常退出

进一步：如果 running 还需要保证自增原子性，用 AtomicBoolean
  private static AtomicBoolean running = new AtomicBoolean(true);
```

---

### 2.3.3 线程池

**Q1：线程池 7 大参数？**

```java
public ThreadPoolExecutor(
    int corePoolSize,              // 核心线程数（长期保留）
    int maximumPoolSize,           // 最大线程数
    long keepAliveTime,            // 非核心线程空闲存活时间
    TimeUnit unit,                 // 时间单位
    BlockingQueue<Runnable> workQueue,    // 任务等待队列
    ThreadFactory threadFactory,          // 创建线程工厂
    RejectedExecutionHandler handler      // 拒绝策略
)
```

**Q2：execute 提交任务流程？**

```
提交任务 command：
1. 当前线程数 < corePoolSize → 创建核心线程执行
2. 核心满了 → workQueue.offer(command) 入队等待
3. 队列满了 → 创建非核心线程（不超过 maxPoolSize）
4. maxPoolSize 也满了 → 执行拒绝策略
```

**Q3：4 种拒绝策略？**

| 策略 | 行为 | 适用场景 |
|---|---|---|
| AbortPolicy（默认） | 抛 RejectedExecutionException | 标准场景，快速失败 |
| CallerRunsPolicy | 调用者线程自己执行 | 不丢任务，降级 |
| DiscardPolicy | 直接丢弃新任务 | 允许丢失 |
| DiscardOldestPolicy | 丢弃队列最老任务，重新提交 | 优先新任务 |

**Q4：为什么不推荐 Executors 自带线程池？**

```java
// 阿里开发手册强制禁用：
new ThreadPoolExecutor(nThreads, nThreads, 0L, MILLISECONDS,
    new LinkedBlockingQueue<>());  // ❌ 队列容量 = Integer.MAX_VALUE
    // → 任务堆积 → OOM

new ThreadPoolExecutor(0, Integer.MAX_VALUE, 60L, SECONDS,
    new SynchronousQueue<>());  // ❌ maxPoolSize = Integer.MAX_VALUE
    // → 无限创建线程 → OOM / CPU 100%

// ✅ 正确做法：显式 new ThreadPoolExecutor
ThreadPoolExecutor pool = new ThreadPoolExecutor(
    8, 16, 60L, TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(500),
    new ThreadFactoryBuilder().setNameFormat("order-pool-%d").build(),
    new ThreadPoolExecutor.CallerRunsPolicy()
);
```

**Q5：核心参数如何设置？**

```
① CPU 密集型（大量计算）：corePoolSize = CPU 核心数 + 1
② IO 密集型（DB/RPC 调用多）：corePoolSize = CPU 核心数 × 2（经验值）
  公式：线程数 = CPU核数 × CPU利用率 × (1 + 等待时间/计算时间)
③ 混合场景：拆成两个独立线程池
最终：一定要压测调参！
```

**项目案例**：

```
项目场景：订单服务使用 Executors.newFixedThreadPool(10)，大促时 OOM
问题：
  ① LinkedBlockingQueue 无界（Integer.MAX_VALUE），任务堆积
  ② 线程名 pool-1-thread-N，出问题无法定位是哪个业务
  ③ 没有监控指标，不知道队列积压情况

优化：
  ① 自定义线程池：
     ThreadPoolExecutor orderPool = new ThreadPoolExecutor(
         8, 20, 60L, TimeUnit.SECONDS,
         new ArrayBlockingQueue<>(500),  // 有界队列
         new ThreadFactoryBuilder().setNameFormat("order-pool-%d").build(),
         new ThreadPoolExecutor.CallerRunsPolicy()  // 降级
     );
  ② 加监控：暴露 activeCount、queueSize、completedTaskCount 到 Prometheus
  ③ 优雅关闭：
     pool.shutdown();
     if (!pool.awaitTermination(60, SECONDS)) {
         pool.shutdownNow();
     }

效果：大促无 OOM，队列积压可观测，问题定位时间从 30 分钟降到 5 分钟
```

---

### 2.3.4 AQS 与 Lock

**Q1：AQS 核心原理？**

```
AQS（AbstractQueuedSynchronizer）：
  - 核心 state（volatile int）：表示锁状态（0=空闲，1=被占，>1=重入次数）
  - CLH 变体双向链表：没抢到锁的线程入队排队
  - 两种模式：独占（ReentrantLock）/ 共享（Semaphore、CountDownLatch）
  - 模板方法：子类重写 tryAcquire/tryRelease，排队/阻塞由 AQS 做

acquire 流程（ReentrantLock.lock()）：
  1. tryAcquire → CAS 抢锁
  2. 失败 → addWaiter 入队
  3. acquireQueued 自旋 → 前驱是 head 才尝试抢锁
  4. 抢不到 → park 阻塞 → 被 unpark 唤醒后继续
```

**Q2：公平锁 vs 非公平锁？**

```
非公平锁（默认）：任何线程来都先 CAS 抢一次，抢到直接获得
  优点：吞吐量大  缺点：可能饥饿

公平锁：每次 tryAcquire 前判断 hasQueuedPredecessors()（队列中有没有更早的等待者）
  优点：绝对公平  缺点：吞吐量略低

new ReentrantLock(true)  // 公平锁
new ReentrantLock(false) // 非公平锁（默认）
```

**项目案例**：

```
项目场景：基于 AQS 实现限流器（简易版）
需求：限制某接口每秒最多 100 次调用

实现思路：用 Semaphore（基于 AQS 共享模式）
  private Semaphore semaphore = new Semaphore(100);
  
  public void access() {
      if (!semaphore.tryAcquire()) {
          throw new BizException("系统繁忙，请稍后重试");
      }
      try {
          // 业务逻辑
      } finally {
          semaphore.release();
      }
  }
  
  // 定时补充令牌（每秒重置为 100）
  @Scheduled(fixedRate = 1000)
  public void resetPermit() {
      semaphore.drainPermits();  // 清空
      semaphore.release(100);     // 重新发 100 个
  }

效果：接口限流 100 QPS，超出请求快速失败，保护后端服务
（生产环境推荐 Sentinel / RateLimiter）
```

---

### 2.3.5 ThreadLocal

**Q1：ThreadLocal 原理？**

```
每个 Thread 对象内部有 ThreadLocalMap（类似 HashMap）
  ThreadLocal.set(value)：
    → 获取当前线程
    → 取出 threadLocals（ThreadLocalMap）
    → map.set(this, value)  // key = ThreadLocal 对象，value = 值

ThreadLocalMap 的 Entry 继承 WeakReference：
  - key（ThreadLocal）是弱引用 → ThreadLocal 被 GC 后 key = null
  - value 是强引用 → value 不会被自动回收 → 内存泄漏！
```

**Q2：ThreadLocal 内存泄漏怎么产生的？**

```
线程池场景下，线程被复用，不销毁：
  ① ThreadLocal 对象被 GC（弱引用 key = null）
  ② 但 Entry.value 仍被 ThreadLocalMap 强引用
  ③ value 无法回收 → 内存泄漏

解决方案：
  使用完后一定手动 remove()！
  try {
      threadLocal.set(user);
      // 业务逻辑
  } finally {
      threadLocal.remove();  // ← 必须手动清理
  }
```

**Q3：ThreadLocal 使用场景？**

```
① 用户上下文传递（不用每次传参）：
   private static ThreadLocal<User> currentUser = new ThreadLocal<>();
   // 拦截器中 set，Service 中 get，finally 中 remove

② 数据库连接管理：
   每个线程一个 Connection，保证事务用同一个连接

③ 线程安全的 SimpleDateFormat：
   private static ThreadLocal<SimpleDateFormat> sdf =
       ThreadLocal.withInitial(() -> new SimpleDateFormat("yyyy-MM-dd HH:mm:ss"));
   // SimpleDateFormat 非线程安全，每个线程一份
```

**项目案例**：

```
项目场景：微服务架构中，需要在整个请求链路中传递用户信息
问题：Controller → Service → DAO 层层传 userId，参数污染
实现：
  ① 网关拦截器解析 Token → 提取 userId
  ② 放入 ThreadLocal
  ③ Service / DAO 直接 get

  public class UserContext {
      private static ThreadLocal<UserInfo> context = new ThreadLocal<>();
      public static void set(UserInfo user) { context.set(user); }
      public static UserInfo get() { return context.get(); }
      public static void clear() { context.remove(); }
  }
  
  // 拦截器
  @Component
  public class AuthInterceptor implements HandlerInterceptor {
      public boolean preHandle(HttpServletRequest req, ...) {
          UserInfo user = parseToken(req.getHeader("Authorization"));
          UserContext.set(user);
          return true;
      }
      public void afterCompletion(...) {
          UserContext.clear();  // ← 必须！线程池复用下不清理会泄漏
      }
  }

效果：代码干净，无需传参，用户信息全链路可用
踩坑：曾经忘记 remove()，导致 Tomcat 线程池复用时，用户 A 的信息出现在用户 B 的请求中
```

## 2.4 Spring / Spring Boot

### 2.4.1 IOC 与 AOP

**Q1：IOC 的理解？**

```
IOC（Inversion of Control）控制反转：
  - 传统：对象自己 new 依赖（主动控制）
  - IOC：容器创建对象并注入依赖（反转控制权）
  - 目的：解耦

DI（Dependency Injection）依赖注入是 IOC 的实现方式：
  ① 构造函数注入（推荐）
  ② Setter 注入
  ③ 字段注入（@Autowired on field，不推荐）

Spring IOC 容器：BeanFactory（基础）→ ApplicationContext（增强）
```

**Q2：AOP 原理？**

```
AOP（面向切面编程）：在不修改源码的情况下增强方法

底层实现：动态代理
  - JDK 动态代理：只能代理接口，InvocationHandler + Proxy.newProxyInstance
  - CGLIB：创建目标类子类，MethodInterceptor 拦截（final 类/方法不行）
  - Spring 自动选择：有接口用 JDK，无接口用 CGLIB

核心概念：
  - 切面 Aspect：@Aspect 注解的类
  - 切点 Pointcut：定义在哪些方法上切入（execution 表达式）
  - 通知 Advice：@Before / @After / @Around / @AfterReturning / @AfterThrowing
  - 织入 Weaving：Spring 在运行时通过动态代理织入
```

```java
// AOP 示例：日志切面
@Aspect
@Component
public class LogAspect {
    @Around("execution(* com.example.service.*.*(..))")
    public Object log(ProceedingJoinPoint pjp) throws Throwable {
        String method = pjp.getSignature().getName();
        long start = System.currentTimeMillis();
        try {
            Object result = pjp.proceed();
            long cost = System.currentTimeMillis() - start;
            log.info("方法 {} 执行完成，耗时 {}ms", method, cost);
            return result;
        } catch (Exception e) {
            log.error("方法 {} 执行异常", method, e);
            throw e;
        }
    }
}
```

**项目案例**：

```
项目场景：统一接口耗时监控
需求：统计所有 Controller 接口的执行耗时，超过 1s 告警
实现：AOP + 滑动窗口

  @Aspect
  @Component
  public class RTMonitorAspect {
      @Around("@annotation(org.springframework.web.bind.annotation.RequestMapping)")
      public Object monitor(ProceedingJoinPoint pjp) throws Throwable {
          long start = System.currentTimeMillis();
          try {
              return pjp.proceed();
          } finally {
              long cost = System.currentTimeMillis() - start;
              String method = pjp.getSignature().toShortString();
              // 上报 Micrometer / Prometheus
              Metrics.timer("api.rt", "method", method).record(cost, TimeUnit.MILLISECONDS);
              if (cost > 1000) {
                  log.warn("慢接口 {} 耗时 {}ms", method, cost);
              }
          }
      }
  }

效果：零侵入监控全量接口，慢接口告警，Grafana 可视化
发现并优化了 5 个慢接口（平均 RT 从 800ms 降到 150ms）
```

---

### 2.4.2 Spring Bean 生命周期

**Q1：Bean 生命周期？**

```
Bean 生命周期 4 大阶段：

1. 实例化（Instantiation）
   → 调用构造函数 / 工厂方法创建对象

2. 属性赋值（Populate Properties）
   → @Autowired / @Value / @Resource 注入依赖

3. 初始化（Initialization）
   → BeanNameAware / BeanFactoryAware 等 Aware 回调
   → BeanPostProcessor.postProcessBeforeInitialization
   → @PostConstruct / afterPropertiesSet() / init-method
   → BeanPostProcessor.postProcessAfterInitialization（AOP 代理在这里创建）

4. 销毁（Destruction）
   → @PreDestroy / destroy() / destroy-method
```

**Q2：循环依赖怎么解决？**

```
Spring 用三级缓存解决 setter 注入的循环依赖：

  singletonObjects（一级缓存）：完整 Bean
  earlySingletonObjects（二级缓存）：半初始化 Bean
  singletonFactories（三级缓存）：ObjectFactory（Lambda 提前暴露引用）

A 依赖 B，B 依赖 A 的解决流程：
  1. 创建 A → 实例化 A → 放入三级缓存（ObjectFactory）
  2. A 注入属性 B → getBean(B)
  3. 创建 B → 实例化 B → 放入三级缓存
  4. B 注入属性 A → getBean(A) → 从三级缓存拿到 A 的早期引用 → 放入二级缓存
  5. B 完成初始化 → 放入一级缓存
  6. A 继续初始化 → 放入一级缓存

注意：
  ① 构造器注入的循环依赖无法解决（实例化阶段就需要依赖，还没放入三级缓存）
  ② prototype 作用域的循环依赖无法解决（不缓存）
```

**项目案例**：

```
项目场景：系统启动报错 BeanCurrentlyInCreationException
排查：
  ① 类 A 构造函数注入 B，B 构造函数注入 A → 构造器循环依赖
  ② Spring 无法解决构造器循环依赖

解决方案：
  方案 1：改为 setter 注入（或 @Autowired 字段注入）
  方案 2：其中一方加 @Lazy 延迟加载
    public A(@Lazy B b) { this.b = b; }
    → Spring 注入 B 的代理对象，真正使用时才创建
  方案 3：重构，引入中间层（C 依赖 A 和 B，A 和 B 不互相依赖）

最终选方案 2，最小改动，启动正常
复盘：设计时应避免循环依赖，遵循单向依赖原则
```

---

### 2.4.3 Spring Boot 自动装配

**Q1：自动装配原理？**

```
@SpringBootApplication = @SpringBootConfiguration + @EnableAutoConfiguration + @ComponentScan

@EnableAutoConfiguration 核心流程：
  → @Import(AutoConfigurationImportSelector.class)
  → selectImports()：
    → SpringFactoriesLoader.loadFactoryNames(EnableAutoConfiguration.class, classLoader)
    → 读取所有 META-INF/spring.factories 文件
    → 拿到 org.springframework.boot.autoconfigure.EnableAutoConfiguration 对应的配置类列表（100+ 个）
    → 去重 + 排除 exclude + @Conditional 条件过滤
    → 最终只有满足条件的配置类被导入

@Conditional 条件装配：
  @ConditionalOnClass        classpath 有指定类才生效
  @ConditionalOnMissingBean  容器中没有指定 Bean 才生效（给用户覆盖的机会）
  @ConditionalOnProperty     配置有指定属性才生效
```

**Q2：自定义 Starter？**

```
需求：封装一个短信发送 Starter，引入后自动装配 SmsService

步骤：
  1. SmsProperties（配置类）
     @ConfigurationProperties(prefix = "sms")
     public class SmsProperties {
         private String url;
         private String accessKey;
         private String secretKey;
     }
  
  2. SmsService（业务类）
     public class SmsService {
         private SmsProperties properties;
         public SmsService(SmsProperties p) { this.properties = p; }
         public boolean send(String phone, String content) { ... }
     }
  
  3. SmsAutoConfiguration（自动配置类）
     @Configuration
     @EnableConfigurationProperties(SmsProperties.class)
     @ConditionalOnClass(SmsService.class)
     @ConditionalOnProperty(prefix = "sms", name = "enabled", havingValue = "true", matchIfMissing = true)
     public class SmsAutoConfiguration {
         @Bean
         @ConditionalOnMissingBean
         public SmsService smsService(SmsProperties p) {
             return new SmsService(p);
         }
     }
  
  4. resources/META-INF/spring.factories：
     org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
       com.example.sms.autoconfigure.SmsAutoConfiguration
  
  5. 其他项目引入依赖 → application.yml 配 sms.url/ak/sk → 直接注入 SmsService 使用
```

---

### 2.4.4 事务管理

**Q1：Spring 事务原理？**

```
Spring 事务基于 AOP 动态代理：
  ① @Transactional 注解 → Spring 创建事务代理对象
  ② 调用事务方法时，TransactionInterceptor 拦截
  ③ 开启事务（获取 Connection，setAutoCommit(false)）
  ④ 执行业务方法
  ⑤ 正常返回 → commit；抛异常 → 判断是否在 rollbackFor → rollback/commit

事务传播行为（7 种）：
  REQUIRED（默认）：有事务加入，没有就新建
  REQUIRES_NEW：总是新建事务，挂起当前事务
  NESTED：嵌套事务（Savepoint）
  SUPPORTS：有事务加入，没有就非事务运行
  NOT_SUPPORTED：非事务运行，挂起当前事务
  MANDATORY：必须在事务中，否则抛异常
  NEVER：不能在事务中，否则抛异常
```

**Q2：@Transactional 失效的场景？**

```
① 方法非 public（Spring AOP 默认只拦截 public 方法）
② 同类方法互调（this 调用不走代理对象）
   解决：注入自己 self.xxx() 或 AopContext.currentProxy()
③ 异常类型不对（默认只回滚 RuntimeException，checked 异常不回滚）
   解决：@Transactional(rollbackFor = Exception.class)
④ 自己 try-catch 吞了异常
   解决：catch 后 throw 或 setRollbackOnly()
⑤ 数据库引擎不支持事务（MyISAM → InnoDB）
```

**项目案例**：

```
项目场景：订单创建 + 库存扣减 + 积分发放，需要事务一致
问题：@Transactional 加在 createOrder 方法上，但积分发放失败后订单没回滚
排查：
  ① 积分服务抛的是 IOException（checked exception）
  ② @Transactional 默认只回滚 RuntimeException
  ③ 订单没回滚

解决方案：
  @Transactional(rollbackFor = Exception.class)
  public void createOrder(OrderDTO dto) {
      orderMapper.insert(order);           // 1. 创建订单
      productMapper.deductStock(...);     // 2. 扣库存
      pointService.addPoints(...);        // 3. 发积分（可能抛 IOException）
  }

进一步优化（分布式场景）：
  ① 本地消息表 + MQ 最终一致（订单和消息表同一本地事务）
  ② MQ 消费方（积分服务）幂等处理
  效果：数据一致性 100%，不再因积分服务故障阻塞下单
```

---

## 2.5 MySQL 数据库

### 2.5.1 索引原理

**Q1：为什么用 B+ 树？**

```
B+ 树的优势：
  ① 非叶子节点只存索引（不存数据），一个 16KB 页能存 ~1170 个索引项
  ② 3 层 B+ 树：1170 × 1170 × 16 ≈ 2200 万行，只需 3 次 I/O
  ③ 叶子节点双向链表 → 范围查询高效（SELECT WHERE id > 100）
  
对比：
  - B 树：非叶子也存数据 → 树更高 → I/O 更多
  - 哈希：等值查询 O(1) 快，但范围查询无能为力
  - 红黑树/AVL：树高远大于 B+ 树（2 叉 vs 多叉），I/O 次数多
```

**Q2：聚簇索引 vs 非聚簇索引？**

| 类型 | 叶子节点存什么 | InnoDB | MyISAM |
|---|---|---|---|
| 聚簇索引 | 完整行数据 | 主键索引是聚簇索引 | 不支持 |
| 非聚簇索引（二级索引） | 主键值 / 行地址 | 二级索引存主键值，需要回表 | 存行地址 |

```
回表过程：
  SELECT * FROM user WHERE name = '张三';
  ① name 索引（二级索引）查到主键 id = 123
  ② 再到主键索引（聚簇索引）查 id = 123 的完整行数据
  
  覆盖索引避免回表：
  SELECT id, name FROM user WHERE name = '张三';
  → name 索引中已经有 id 和 name，不需要回表
```

**Q3：索引失效场景？**

```
① 不符合最左前缀（联合索引 idx(a,b,c)）
   WHERE b = 1 AND c = 2  → 不走索引（缺 a）
   WHERE a = 1 AND c = 2  → 只用到 a

② 索引列做运算/函数
   WHERE YEAR(create_time) = 2024  → 不走索引
   WHERE create_time >= '2024-01-01' AND create_time < '2025-01-01'  → 走索引

③ 类型隐式转换
   WHERE phone = 13800138000  → phone 是 varchar，传入 int → 隐式转换不走索引

④ LIKE 以 % 开头
   WHERE name LIKE '%张三'  → 不走索引
   WHERE name LIKE '张三%'  → 走索引

⑤ OR 连接（一边没索引）
   WHERE a = 1 OR b = 2  → b 没索引 → 全表扫描

⑥ 不等于 / NOT IN / IS NOT NULL（部分场景）
```

**项目案例**：

```
项目场景：订单查询接口慢，RT 2s+
排查：
  EXPLAIN SELECT * FROM order WHERE user_id = 123 AND status = 1 
    ORDER BY create_time DESC LIMIT 10;
  
  发现 type=ALL（全表扫描），key=NULL（没走索引），rows=500万

分析：
  ① 没有联合索引
  ② user_id 单独有索引但只过滤了一部分，status 和 create_time 没索引
  
优化方案：
  ① 创建联合索引 idx_user_status_time(user_id, status, create_time)
  ② 最左前缀：user_id 等值 → status 等值 → create_time 排序（利用索引有序，避免 filesort）
  
  再次 EXPLAIN：
  type=ref（走索引），key=idx_user_status_time，rows=15，Extra=Using index（覆盖索引）
  
效果：RT 从 2s 降到 20ms
```

---

### 2.5.2 事务与隔离级别

**Q1：ACID 四大特性？**

```
A 原子性（Atomicity）：事务内操作要么全做要么全不做（undo log 回滚）
C 一致性（Consistency）：事务前后数据一致（转账前后总额不变）
I 隔离性（Isolation）：并发事务互不干扰（锁 + MVCC）
D 持久性（Durability）：提交后永久保存（redo log）
```

**Q2：4 种隔离级别？**

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | InnoDB 默认 |
|---|---|---|---|---|
| READ UNCOMMITTED | 可能 | 可能 | 可能 | |
| READ COMMITTED（RC） | 不可能 | 可能 | 可能 | Oracle/PostgreSQL 默认 |
| REPEATABLE READ（RR） | 不可能 | 不可能 | InnoDB 基本解决 | **InnoDB 默认** |
| SERIALIZABLE | 不可能 | 不可能 | 不可能 | 性能差 |

```
脏读：读到其他事务未提交的数据
不可重复读：同一事务两次读取同一行，结果不同（其他事务修改了）
幻读：同一事务两次查询，结果集行数不同（其他事务新增/删除了行）
```

**Q3：MVCC 原理？**

```
MVCC（多版本并发控制）—— InnoDB 在 RC/RR 级别下实现非阻塞读

三件套：
  ① 隐藏列：DB_TRX_ID（事务 ID）、DB_ROLL_PTR（回滚指针 → undo log）
  ② Undo 版本链：每次修改生成一条 undo log，通过回滚指针串联
  ③ ReadView：生成时记录当前活跃事务列表

可见性判断：
  - trx_id < min_trx_id → 可见（事务在 ReadView 之前已提交）
  - trx_id >= max_trx_id → 不可见（事务在 ReadView 之后才开始）
  - min ≤ trx_id < max → 在活跃列表中 → 不可见（还没提交）；不在 → 可见

RC vs RR 的 ReadView 差异：
  RC：每次 SELECT 都生成新的 ReadView → 能读到已提交的最新数据
  RR：第一次 SELECT 生成 ReadView 后，整个事务复用 → 可重复读
```

**项目案例**：

```
项目场景：报表系统统计订单金额，使用 RR 隔离级别
问题：长事务期间，其他事务新订单已提交但报表统计不到
分析：
  ① RR 级别下，事务第一次 SELECT 生成 ReadView
  ② 后续 SELECT 复用 ReadView → 看不到其他事务提交的新数据
  ③ 这是 RR 的正常行为（可重复读），但对报表场景不合适

解决方案：
  ① 报表查询使用 RC 级别（每次 SELECT 新 ReadView，看到最新已提交数据）
  ② 或用 ReadCommited 隔离级别的事务
  ③ 长事务拆短（批量处理，每 1000 条提交一次）

效果：报表数据实时性提升，数据偏差 < 1 秒
复盘：不同业务场景选不同隔离级别，不要一刀切
```

---

### 2.5.3 锁机制

**Q1：InnoDB 有哪些锁？**

```
① 行级锁（InnoDB 特有）
   - Record Lock：锁单条记录
   - Gap Lock：锁间隙（防止幻读，开区间）
   - Next-Key Lock：Record + Gap（左开右闭，RR 默认）

② 意向锁（表级，IS/IX）
   - 快速判断表中是否有行锁，避免全表扫描行锁

③ MDL 锁（元数据锁）
   - DDL 操作时加，防止 DML 和 DDL 冲突
```

**Q2：RR 级别下加锁规则？**

```
① 唯一索引等值命中 → 退化成 Record Lock（只锁记录）
② 唯一索引等值未命中 → 退化成 Gap Lock（锁间隙）
③ 普通索引等值 → Next-Key Lock + 向右遍历到第一个不等 → Gap Lock
④ 范围查询 → 所有覆盖区间 Next-Key Lock

例：表 t(id PK, name) 有数据 1,5,10,15,20
  WHERE id = 10 → Record Lock(10)
  WHERE id = 7  → Gap Lock(5, 10)
  WHERE id > 10 → Next-Key Lock(10,15], (15,20], (20,+∞)
```

**Q3：死锁怎么排查？**

```
① SET GLOBAL innodb_print_all_deadlocks = 1
② SHOW ENGINE INNODB STATUS \G → LATEST DETECTED DEADLOCK
   看到两个事务分别持有什么锁、等什么锁
③ 常见死锁原因：
   - 加锁顺序不一致（A 先锁 X 后 Y，B 先 Y 后 X）
   - 不同索引路径导致加锁顺序不同
   - Gap Lock 交叉
④ 解决方案：
   - 统一加锁顺序（如按主键 ID 从小到大）
   - 缩短事务
   - 改 RC 隔离级别（没有 Gap Lock）
```

**项目案例**：

```
项目场景：高并发下两个接口互相死锁
  接口 A：更新订单 + 更新库存（先锁 order 再锁 stock）
  接口 B：扣库存 + 记录库存流水（先锁 stock 再锁 order）
  
  → A 持有 order 锁等 stock 锁，B 持有 stock 锁等 order 锁 → 死锁

排查：
  ① SHOW ENGINE INNODB STATUS 看到 LATEST DETECTED DEADLOCK
  ② 两个事务分别执行 UPDATE order 和 UPDATE stock，顺序相反

解决方案：
  ① 统一加锁顺序：所有涉及 order + stock 的操作，都先锁 order 再锁 stock
  ② 代码层面抽取公共方法 lockAndUpdate(orderId, productId, ...)
  ③ 加死锁监控告警（innodb_deadlocks 指标）

效果：死锁 0 次，并发性能正常
```

---

### 2.5.4 SQL 优化实战

**Q1：EXPLAIN 关键字段？**

| 字段 | 含义 | 重点关注 |
|---|---|---|
| type | 访问类型 | system > const > eq_ref > ref > range > index > ALL |
| key | 实际使用的索引 | NULL = 没走索引 |
| rows | 预估扫描行数 | 越少越好 |
| Extra | 额外信息 | Using index（覆盖索引好）/ Using filesort（坏）/ Using temporary（坏） |

**Q2：慢 SQL 排查 SOP？**

```
① 开启慢查询日志：SET GLOBAL slow_query_log = ON; long_query_time = 1;
② mysqldumpslow 分析 TOP N 慢 SQL
③ EXPLAIN 分析执行计划
④ 优化方案优先级：
   a) 加索引（联合索引遵循最左前缀）
   b) 改 SQL（避免 SELECT *，避免索引列运算）
   c) 架构优化（读写分离、分库分表、缓存）
⑤ 验证：再 EXPLAIN + 看慢查询是否消失
```

**Q3：大分页优化？**

```sql
-- ❌ 慢：LIMIT 1000000, 10 → 扫描 100 万行再丢弃
SELECT * FROM order ORDER BY create_time DESC LIMIT 1000000, 10;

-- ✅ 方案 1：延迟关联
SELECT * FROM order o
INNER JOIN (SELECT id FROM order ORDER BY create_time DESC LIMIT 1000000, 10) t
ON o.id = t.id;
-- 子查询走覆盖索引，只查 id，速度快

-- ✅ 方案 2：游标分页（推荐）
-- 前端传上一次最后一条的 id
SELECT * FROM order WHERE id < #{last_id} ORDER BY id DESC LIMIT 10;
-- 走主键索引，O(1) 性能
```

**项目案例**：

```
项目场景：后台订单查询，分页到第 5 万页时 RT 10s+
SQL：SELECT * FROM order WHERE status = 1 ORDER BY create_time DESC LIMIT 500000, 20;
EXPLAIN：type=ALL，rows=500万，Extra=Using filesort（没走索引 + 文件排序）

优化：
  ① 加联合索引 idx_status_create_time(status, create_time)
     → 走索引 + 利用索引有序，去掉 filesort
  ② 大分页改延迟关联
     SELECT * FROM order o
     INNER JOIN (
       SELECT id FROM order WHERE status = 1 
       ORDER BY create_time DESC LIMIT 500000, 20
     ) t ON o.id = t.id
  ③ 前端加约束：最多翻 100 页，超过用搜索条件缩小范围
  ④ 超大分页场景改游标分页（移动端推荐）

效果：RT 从 10s 降到 50ms
```

---

## 2.6 Redis 缓存

### 2.6.1 数据结构与场景

**Q1：Redis 5 大数据类型及底层实现？**

| 类型 | 底层编码 | 典型场景 |
|---|---|---|
| String | int / embstr / raw(SDS) | 计数器、缓存对象、分布式锁 |
| List | quicklist（ziplist + linkedlist） | 消息队列、最新消息列表 |
| Hash | ziplist / hashtable | 对象存储（用户信息） |
| Set | intset / hashtable | 标签、共同好友 |
| ZSet | ziplist / skiplist+hashtable | 排行榜、延迟队列 |

**Q2：ZSet 为什么用跳表？**

```
跳表（Skip List）：
  - 多层链表，上层稀疏下层密集
  - 查询从最高层开始，类似二分查找，平均 O(log N)
  - 范围查询天然支持（底层就是有序链表）

vs 红黑树：
  - 跳表实现更简单
  - 范围查询更自然
  - 并发友好（局部修改少）

ZSet 同时用 skiplist + hashtable：
  - skiplist：范围查询、排名
  - hashtable：O(1) 查某 member 的 score
```

**项目案例**：

```
项目场景：实时排行榜（用户战力排名）
需求：1000 万用户，Top 100 查询 < 50ms，支持周榜/月榜

实现：
  ① 数据结构：Redis Sorted Set
     ZADD rank:week {score} {userId}
     ZINCRBY rank:week {delta} {userId}    -- 战力变化
     ZREVRANGE rank:week 0 99 WITHSCORES  -- Top 100
     ZREVRANK rank:week {userId}           -- 查某用户排名
  
  ② 数据同步：DB 战力更新 → Canal binlog → Kafka → 消费 → ZINCRBY
  
  ③ 周榜/月榜：每天凌晨定时任务合并日榜到周榜/月榜
  
  ④ 分区榜：每个区独立 ZSet（rank:region:{regionId}:week）

效果：Top 100 查询 5ms，支撑 10w QPS 读取
```

---

### 2.6.2 缓存三大问题

**Q1：缓存穿透？**

```
问题：查询不存在的数据，缓存和 DB 都没有 → 每次打 DB
攻击场景：恶意请求 id = -1

解决方案：
  ① 缓存空值：DB 查不到也缓存 null（设短 TTL 60s）
  ② 布隆过滤器：请求前先过布隆过滤器，不存在直接返回
     - RedissonBloomFilter（预计容量 1 亿，误判率 0.1%）
  ③ 接口层参数校验（id > 0）
```

**Q2：缓存击穿？**

```
问题：热点 key 过期瞬间，大量并发请求打 DB

解决方案：
  ① 互斥锁（推荐）：只让一个线程查 DB，其他等待
     String value = redis.get(key);
     if (value == null) {
         if (redis.setnx(lockKey, "1", 10s)) {  // 加锁成功
             try {
                 value = db.query();
                 redis.set(key, value, 30m);
             } finally {
                 redis.del(lockKey);
             }
         } else {
             Thread.sleep(50);  // 等一下重试
             return get(key);
         }
     }
  ② 热点 key 永不过期（后台异步更新）
  ③ Redisson 分布式锁（RLock）
```

**Q3：缓存雪崩？**

```
问题：大量 key 同时过期 → DB 瞬间压力大

解决方案：
  ① 过期时间加随机值：TTL = 30min + random(0, 5min)
  ② 多级缓存：Caffeine 本地缓存 + Redis
  ③ 限流降级：Sentinel 限流保护 DB
  ④ 提前预热：大促前提前加载热点数据到缓存
```

**项目案例**：

```
项目场景：大促期间商品详情接口缓存雪崩
原因：预热时所有商品设置了相同 TTL 30 分钟 → 30 分钟后集中过期 → DB 被 5w QPS 打垮

解决方案：
  ① 过期时间加随机：TTL = 30min + ThreadLocalRandom.nextInt(0, 600)  // 0~10 分钟随机
  ② 多级缓存：
     L1 Caffeine 本地缓存（TTL 5 分钟，最大 1 万条）→ 命中率 60%
     L2 Redis（TTL 30 分钟）→ 命中率 35%
     DB → 只剩 5% 流量
  ③ 互斥锁防击穿：热点 key 用 Redisson RLock
  ④ 限流降级：DB QPS > 5000 时 Sentinel 限流返回降级数据

效果：DB QPS 从 5w 降到 2500，接口 RT 稳定 30ms，大促 0 故障
```

---

### 2.6.3 持久化与高可用

**Q1：RDB vs AOF？**

| 方式 | 原理 | 优点 | 缺点 |
|---|---|---|---|
| RDB | fork 子进程 + COW 写快照 | 文件小恢复快 | 两次快照间数据丢失 |
| AOF | 追加写命令到文件 | 丢数据少（最多 1s） | 文件大恢复慢 |
| 混合 | AOF 开头 RDB + 增量 AOF | 快速加载 + 安全 | Redis 4.0+ |

**Q2：Redis 主从复制 + 哨兵？**

```
主从复制：
  ① 全量同步：slave → master PSYNC → master BGSAVE → RDB + buffer → slave
  ② 部分重同步：断线重连，repl_backlog 环形缓冲区补发

哨兵 Sentinel：
  ① 监控：检测 master/slave 存活
  ② 通知：通知运维
  ③ 自动故障转移：
     - 主观下线 sdown（单个 Sentinel 认为挂）
     - 客观下线 odown（quorum ≥ N/2+1 认为挂）
     - 选举新 master：优先级最高 → offset 最大 → runid 最小
```

**项目案例**：

```
项目场景：Redis 主节点宕机，从节点升级为主节点后丢失部分数据
原因：主从异步复制，主节点写入后还没同步到从节点就宕机 → 数据丢失

排查：
  ① 查看 repl_backlog 配置过小（repl-backlog-size 1mb），高写入时容易覆盖
  ② 主从延迟较大（>1s）

解决方案：
  ① 增大 repl-backlog-size（256mb）
  ② 业务层面：关键数据写入后同步等待从节点 ACK（WAIT 1 1000）
  ③ 半同步：Redis 不原生支持，但可以用 Redis Sentinel + 客户端确认机制
  ④ 对账补偿：T+1 对比主从数据差异，补偿修复

效果：数据丢失率 < 0.01%，主从延迟 < 100ms
```

---

# 三、技术二面（项目深挖 + 系统设计 + 场景题）

## 3.1 项目深挖 STAR 法则

**项目讲法模板**：

```
用 STAR 法则讲项目，每个项目 10~15 分钟：

S（Situation）背景：公司业务、团队规模、项目目标
T（Task）任务：你负责的模块、目标指标（QPS / RT / 数据量）
A（Action）行动（核心 60%）：
  ① 整体架构
  ② 技术选型对比（为什么选 A 不选 B）
  ③ 关键模块设计
  ④ 遇到的难点 + 解决方案
  ⑤ 性能调优（前后对比）
R（Result）结果：量化数据 + 团队收益

面试官追问方向及应对：
  Q：为什么选技术 A？
  A：对比 2~3 个方案 + 业务约束 + 最终选择理由
  
  Q：数据量增长 10 倍怎么办？
  A：先评估瓶颈 → 演进路径（加缓存 → 读写分离 → 分库分表）
  
  Q：线上出过什么事故？
  A：说一个真实的 + 复盘改进（根因 + 修复 + 预防措施）
```

**完整项目案例**：

```
S 背景：
  电商公司，年 GMV 20 亿，日订单 50 万。订单系统是核心，支撑下单/支付/履约。
  团队 6 人，我负责订单核心模块。

T 任务：
  618 大促前压测，订单系统 2000 QPS 就大量超时（目标 5000 QPS），RT P99 2s。
  作为模块 Owner，牵头全链路优化。目标：5000 QPS，RT P99 < 500ms。

A 行动：

  ① 数据库优化：
     - 订单表 3000 万行，查询慢
     - 加联合索引 idx_user_status_time(user_id, status, create_time)
     - 大分页改延迟关联
     - 读写分离：写主库，读从库 + Redis 缓存
     → RT 从 2s 降到 800ms

  ② 缓存优化：
     - 加 Caffeine 本地缓存（top 5% 热点订单）
     - Redis 二级缓存，命中率 85% → 加本地缓存后 97%
     - 布隆过滤器防缓存穿透
     - 过期时间加随机值防雪崩
     → DB QPS 从 8000 降到 1000

  ③ 异步化：
     - 下单主流程只写订单表 → 立即返回
     - 扣库存 / 发短信 / 发优惠券 → 发 RocketMQ 异步处理
     - 消费端幂等处理
     → 接口 RT 从 800ms 降到 150ms

  ④ 线程池优化：
     - 原来 Executors.newFixedThreadPool(10) → 改为自定义 ThreadPoolExecutor
     - core=16, max=32, queue=500, CallerRunsPolicy
     - 加监控：activeCount / queueSize / rejectCount
     → 无 OOM，线程池可观测

  ⑤ JVM 调优：
     - CMS → G1（-XX:+UseG1GC -XX:MaxGCPauseMillis=200）
     - -Xms4g -Xmx4g -Xloggc + PrintGCDetails
     - 减少 Full GC（从每天 3 次 → 0 次）

R 结果：
  - 618 当天峰值 5500 QPS，无 P0 故障
  - RT P99：2s → 320ms（降低 84%）
  - DB CPU：85% → 25%
  - Full GC：3 次/天 → 0 次
  - 沉淀《性能调优 SOP》文档，全公司 3 个业务线复用
```

---

## 3.2 高频系统设计题

### 设计一：秒杀系统（简化版）

```
需求：1000 QPS 秒杀，防超卖，防刷

方案（3 层漏斗）：
  ① 前端：按钮置灰 3s + 验证码
  ② Nginx + Gateway：限流（Sentinel 50 QPS 单机）+ 用户级 1s 3 次
  ③ Redis 预扣库存（Lua 原子操作）：
     local stock = redis.call('GET', KEYS[1])
     if tonumber(stock) >= tonumber(ARGV[1]) then
         return redis.call('DECRBY', KEYS[1], ARGV[1])
     else return -1 end
  ④ MQ 异步下单：Redis 预扣成功 → 发 MQ → 消费者写订单 + DB 扣库存
  ⑤ DB 兜底：UPDATE stock SET stock = stock - 1 WHERE id = ? AND stock >= 1

关键点：
  - 防超卖：Redis Lua + DB 乐观锁双重保障
  - 防重复：用户 ID + 活动 ID 唯一索引
  - 限流防刷：Sentinel 多维度限流
```

### 设计二：短链系统

```
需求：长链转短链，10w/s 创建，1 亿 QPS 访问

方案：
  ① 发号器：DB 号段表 → 内存 AtomicLong → base62 编码生成短码
  ② 存储：MySQL 短码主键表 + Redis 缓存（short:{code} → long_url）
  ③ 访问流程：
     读 Redis → 命中 → 302 重定向 + Kafka 写 PV
     未命中 → 查 MySQL → 回写 Redis → 302
     不存在 → 布隆过滤器拦截 → 404
  ④ 统计：Kafka → Flink 实时聚合 PV/UV
  ⑤ 优化：Caffeine 缓存 top 0.1% 热短码

关键点：
  - 302 而非 301（302 不缓存，每次请求可统计 PV）
  - 布隆过滤器防穿透
  - 空短码也缓存 60s
```

### 设计三：延迟任务系统

```
需求：订单 30 分钟未支付自动关单

方案对比：
  ① 数据库轮询（简单，适合小量）
     定时任务每分钟扫描超时订单 → 关单
     缺点：数据量大时扫描慢
  
  ② Redis ZSet（中等量推荐）
     ZADD delay_queue {过期时间戳} {orderId}
     定时任务 ZRANGEBYSCORE delay_queue 0 {now} → 取出 → 关单 → ZREM
  
  ③ RocketMQ 延迟消息（推荐）
     发送延迟消息 → 30 分钟后消费 → 关单
     优点：分布式可靠，MQ 自带重试 + 死信
  
  ④ 时间轮（Netty HashedWheelTimer）
     内存级延迟，适合短延迟大量任务

项目案例：
  最终选 RocketMQ 延迟消息（已有 RocketMQ 基础设施）
  关单消费端幂等处理（订单状态机：UNPAID → CLOSED）
  死信队列告警 + 人工兜底
```

---

## 3.3 场景题与线上排障

### 场景一：线上 CPU 100% 排查

```
SOP 步骤：
  ① top → 定位高 CPU 的 Java 进程 PID
  ② top -H -p <pid> → 找到高 CPU 线程 TID
  ③ printf "%x" <TID> → 十六进制
  ④ jstack <pid> | grep "nid=0x<hex>" → 看线程堆栈
  ⑤ 分析堆栈：死循环 / GC 频繁 / 正则回溯 / JSON 序列化

  更快的方式：Arthas
  ① thread -n 5 → Top 5 高 CPU 线程堆栈
  ② profiler start → 等待 1 分钟 → profiler stop → 火焰图

项目案例：
  订单接口 CPU 95%，Arthas 火焰图显示 60% 在 Pattern.matches()
  根因：防 XSS 正则 .*(<script>).* 对长字符串回溯
  修复：限制输入长度 + 换成 RE2/J 正则引擎
  效果：CPU 降到 15%，RT 从 5s 降到 50ms
```

### 场景二：线上 OOM 排查

```
SOP 步骤：
  ① 启动参数必须加：-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/opt/logs/heap.hprof
  ② OOM 后拿到 hprof → Eclipse MAT 分析
  ③ Histogram → 看哪个类实例最多
  ④ Dominator Tree → 看占用最大的对象 → GC Roots 引用链
  ⑤ 常见原因：
     - HashMap / ArrayList 无限增长
     - ThreadLocal 未 remove（线程池复用）
     - 大查询一次拉全表
     - 缓存不淘汰

项目案例：
  线上 OOM，MAT 分析发现 ThreadLocal 中存了 2G 的用户上下文
  根因：拦截器中 ThreadLocal.set(user) 后忘记 remove()
  线程池复用 → ThreadLocal 中的 value 一直不释放 → 累积泄漏
  修复：finally 中 ThreadLocal.remove() + Code Review 规范
  效果：OOM 0 次
```

### 场景三：接口响应变慢

```
SOP 步骤：
  ① 查监控：CPU / GC / Redis / MySQL 慢查询 / MQ 积压
  ② TraceId 追踪（SkyWalking）→ 定位最慢的 Span
  ③ Arthas trace 命令定位方法耗时
     trace com.example.OrderService createOrder '#cost > 200'
  ④ 常见原因：
     - DB 慢 SQL（EXPLAIN 分析）
     - N+1 查询（循环中查 DB）
     - 缓存命中率低
     - 线程池满
     - Full GC 频繁
     - 网络抖动

项目案例：
  接口 RT 从 100ms 涨到 800ms
  SkyWalking 发现 80% 耗时在 MySQL 查询
  EXPLAIN 发现索引失效（统计信息过期 → 优化器选错索引）
  修复：ANALYZE TABLE 更新统计信息 + 加 FORCE INDEX
  效果：RT 降回 100ms
```

### 场景四：MQ 消息堆积

```
SOP 步骤：
  ① 紧急：扩容 Consumer + 增加 Topic 分区
  ② 排查生产端：是否异常大量发消息
  ③ 排查消费端：
     - 消费速度 < 生产速度
     - 消费者线程太少
     - 消费逻辑慢（DB 慢 / RPC 慢）
  ④ 优化：
     - 批量消费（consumeMessageBatchMaxSize=32）
     - 轻逻辑 + 异步处理重逻辑
     - 消费线程池调大
  ⑤ 死信队列处理 + T+1 对账

项目案例：
  订单消息堆积 50 万条，消费速度 200/s
  根因：消费逻辑中有同步 HTTP 调用（RT 200ms），单线程
  修复：HTTP 调用改异步 + 消费线程从 20 调到 64 + 批量消费
  效果：消费速度 200/s → 2000/s，1 小时消化完积压
```

---

# 四、HR / 综合面

## 4.1 自我介绍模板

```
3 分钟版（推荐）：

  【开场】面试官好，我叫 XXX，3 年 Java 开发经验，目前在 XX 公司做后端开发。

  【工作经历】
  毕业后在 XX 公司做电商 / 金融 / 物流行业，主要负责 XX 系统。
  技术栈是 Spring Boot + MyBatis + MySQL + Redis + RocketMQ。
  
  【核心项目】
  过去一年主导了 XX 系统的性能优化，QPS 从 2000 提升到 5000，
  RT P99 从 2 秒降到 300 毫秒。过程中解决了 XX 问题（如缓存雪崩 / 数据库死锁 / 
  消息堆积），最终大促 0 故障。
  
  【技术成长】
  工作之余在学 XX（如分布式事务 / JVM 调优 / 微服务架构），写过 XX 技术博客。
  
  【求职动机】
  希望在华为这样的大平台接触更大规模的业务，提升技术深度。

1 分钟版（HR 面）：
  面试官好，我叫 XXX，3 年 Java 经验，目前在 XX 公司做 XX 系统，
  技术栈 Spring Cloud + MySQL + Redis + RocketMQ。
  过去做过 XX 性能优化和 XX 问题排查（量化一句）。
  想加入华为挑战更大规模业务。谢谢。
```

## 4.2 必问问题与应答

| 问题 | 应答模板 |
|---|---|
| 为什么从上家公司离职？ | "目前项目进入成熟期，技术成长空间受限。希望在更大的平台接触更复杂的业务场景，华为是我的首选。" |
| 为什么选择华为？ | "① 业务体量大，能接触更大规模的分布式系统；② 技术深度好，有很多自研中间件；③ 职业路径清晰。" |
| 你的优缺点？ | 优点：基础扎实（读过 Spring / 集合源码），有责任心（线上排障随叫随到），学习能力强。缺点：有时过于追求技术完美，现在会按业务优先级权衡。 |
| 遇到最大的困难？ | 用 STAR 讲一个真实困难：如大促前性能不达标 → 全链路优化 → 达标。 |
| 职业规划？ | "短期 1~2 年成为团队核心骨干，长期 3~5 年向技术专家 / 架构师方向发展。" |
| 期望薪资？ | "目前月薪 XXk × 12 + 年终奖 X 个月，总包约 XX 万。期望涨幅 20%~30%，具体可以再讨论。" |
| 接受加班吗？ | "项目需要时完全可以加班，之前大促 / 版本发布 / 故障处理都主动加班。长期可以和家人商量。" |
| 和领导有分歧？ | "先倾听理解 → 数据方案沟通 → 最终执行领导决策，事后看数据反馈。" |

## 4.3 反问面试官

```
推荐问 3 个：
  ① "咱们团队目前的核心业务和未来规划是什么？"
  ② "技术栈是什么样的？有没有自研中间件？微服务规模多大？"
  ③ "入职后会有 mentor 带吗？团队的技术分享机制怎样？"

不要问（技术面）：
  - 加班多吗？薪资多少？（HR 面再问）
  - 面试结果什么时候出？（显得急躁）
```

---

# 五、备考清单

## 3 年经验复习重点

```
✅ 必背（面试必问）：
  1. HashMap 底层 + 扩容 + 线程安全
  2. synchronized 与 ReentrantLock 区别
  3. volatile 可见性 + DCL 单例
  4. 线程池 7 参数 + execute 流程 + 拒绝策略
  5. ThreadLocal 原理 + 内存泄漏
  6. JVM 内存模型 + GC 回收器（CMS / G1）
  7. Spring IOC / AOP 原理
  8. Spring Bean 生命周期
  9. @Transactional 失效场景
  10. MySQL 索引原理 + 索引失效
  11. MVCC + 隔离级别
  12. Redis 缓存穿透/击穿/雪崩

✅ 项目准备：
  - 准备 2 个项目 STAR 稿子（写出来 1000 字以上）
  - 技术选型对比表格（至少 2~3 个方案）
  - 量化数据（QPS / RT / 数据量 / 命中率）

✅ 系统设计：
  - 秒杀系统（3 层漏斗）
  - 短链系统（发号器 + 缓存）
  - 延迟任务（MQ 延迟消息）

✅ 排障场景：
  - CPU 100%（top + jstack + Arthas）
  - OOM（HeapDump + MAT）
  - 慢接口（TraceId + EXPLAIN）
  - MQ 堆积（扩容 + 优化消费）

✅ HR 面准备：
  - 自我介绍 1 分钟 + 3 分钟两版
  - 8 大问题应答稿子写出来
  - 反问面试官 3 个问题
```

---

> **文档使用建议**：
> 1. 通读一遍，标记"不会 / 不熟"的点
> 2. 重点准备项目 STAR 稿子，写出来不要只在脑子里想
> 3. 每个知识点能用 2~3 分钟讲清楚，配合项目案例
> 4. 模拟面试录音，回放找逻辑断点和口头禅

祝面试顺利，Offer 稳拿！

