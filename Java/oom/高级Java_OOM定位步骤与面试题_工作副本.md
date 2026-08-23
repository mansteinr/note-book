
## 目录

- [一、OOM 概述](#一oom-概述)
  - [1.1 什么是 OOM](#11-什么是-oom)
  - [1.2 OOM 与 StackOverflowError 的区别](#12-oom-与-stackoverflowerror-的区别)
  - [1.3 OOM 出现的触发点](#13-oom-出现的触发点)
- [二、JVM 内存模型与 OOM 对应关系](#二jvm-内存模型与-oom-对应关系)
  - [2.1 JVM 运行时数据区总览](#21-jvm-运行时数据区总览)
  - [2.2 各区域与 OOM 类型映射](#22-各区域与-oom-类型映射)
- [三、8 种 OOM 类型详解](#三8-种-oom-类型详解)
  - [3.1 Java heap space](#31-java-heap-space)
  - [3.2 GC overhead limit exceeded](#32-gc-overhead-limit-exceeded)
  - [3.3 PermGen space / Metaspace](#33-permgen-space--metaspace)
  - [3.4 Direct buffer memory](#34-direct-buffer-memory)
  - [3.5 unable to create new native thread](#35-unable-to-create-new-native-thread)
  - [3.6 Requested array size exceeds VM limit](#36-requested-array-size-exceeds-vm-limit)
  - [3.7 GC pause (G1 Evacuation Pause / Full GC)](#37-gc-pause-g1-evacuation-pause--full-gc)
  - [3.8 Compressed class space / Native allocation](#38-compressed-class-space--native-allocation)
- [四、标准 OOM 定位步骤](#四标准-oom-定位步骤)
  - [4.1 总览：五步定位法](#41-总览五步定位法)
  - [4.2 Step 1：现象确认与现场保护](#42-step-1现象确认与现场保护)
  - [4.3 Step 2：抓取堆转储与线程转储](#43-step-2抓取堆转储与线程转储)
    - [4.3.1 堆转储（Heap Dump）](#431-堆转储heap-dump)
    - [4.3.2 线程转储（Thread Dump）](#432-线程转储thread-dump)
    - [4.3.3 GC 实时监控](#433-gc-实时监控)
  - [4.4 Step 3：JVM 参数与启动参数核查](#44-step-3jvm-参数与启动参数核查)
  - [4.5 Step 4：根因定位（工具分析）](#45-step-4根因定位工具分析)
    - [4.5.1 GC 日志分析关键指标](#451-gc-日志分析关键指标)
    - [4.5.2 线程 dump 分析要点](#452-线程-dump-分析要点)
    - [4.5.3 堆转储分析（MAT）](#453-堆转储分析mat)
  - [4.6 Step 5：验证修复与复盘](#46-step-5验证修复与复盘)
- [五、核心工具详解](#五核心工具详解)
  - [5.1 JDK 内置工具速查](#51-jdk-内置工具速查)
  - [5.2 jmap：堆转储与对象统计](#52-jmap堆转储与对象统计)
    - [5.2.1 常用命令](#521-常用命令)
    - [5.2.2 jmap -histo 输出解读](#522-jmap--histo-输出解读)
  - [5.3 jstat：GC 实时监控](#53-jstatgc-实时监控)
    - [5.3.1 常用命令](#531-常用命令)
    - [5.3.2 实战判断](#532-实战判断)
  - [5.4 jstack：线程转储](#54-jstack线程转储)
    - [5.4.1 常用命令](#541-常用命令)
    - [5.4.2 手工分析脚本](#542-手工分析脚本)
    - [5.4.3 解读线程栈](#543-解读线程栈)
  - [5.5 jhat：离线堆分析](#55-jhat离线堆分析)
  - [5.6 jinfo：运行时参数查看](#56-jinfo运行时参数查看)
  - [5.7 VisualVM / MAT 图形化分析](#57-visualvm--mat-图形化分析)
    - [5.7.1 VisualVM（Oracle 官方，适合实时观察）](#571-visualvmoracle-官方适合实时观察)
    - [5.7.2 MAT（Eclipse Memory Analyzer，适合大 dump 深度分析）](#572-mateclipse-memory-analyzer适合大-dump-深度分析)
  - [5.8 Arthas：线上神器](#58-arthas线上神器)
    - [5.8.1 OOM 排查常用命令](#581-oom-排查常用命令)
    - [5.8.2 profiler 火焰图定位泄漏（杀手级功能）](#582-profiler-火焰图定位泄漏杀手级功能)
- [六、真实案例实战](#六真实案例实战)
  - [6.1 案例一：订单服务 heap space 溢出](#61-案例一订单服务-heap-space-溢出)
    - [场景](#场景)
    - [排查步骤](#排查步骤)
    - [修复前后对比](#修复前后对比)
    - [经验教训](#经验教训)
  - [6.2 案例二：Metaspace 溢出（反射类加载泄漏）](#62-案例二metaspace-溢出反射类加载泄漏)
    - [场景](#场景-1)
    - [排查步骤](#排查步骤-1)
  - [6.3 案例三：Direct Buffer 溢出（Netty 内存泄漏）](#63-案例三direct-buffer-溢出netty-内存泄漏)
    - [场景](#场景-2)
    - [排查步骤](#排查步骤-2)
  - [6.4 案例四：GC overhead limit exceeded](#64-案例四gc-overhead-limit-exceeded)
    - [场景](#场景-3)
    - [排查步骤](#排查步骤-3)
  - [6.5 案例五：native thread 无法创建](#65-案例五native-thread-无法创建)
    - [场景](#场景-4)
    - [排查步骤](#排查步骤-4)
  - [6.6 案例六：G1 Evacuation Pause 导致服务不可用](#66-案例六g1-evacuation-pause-导致服务不可用)
    - [场景](#场景-5)
    - [排查步骤](#排查步骤-5)
- [七、常见 OOM 场景与解决方案](#七常见-oom-场景与解决方案)
  - [7.1 内存泄漏场景](#71-内存泄漏场景)
    - [定义](#定义)
    - [泄漏判断标准](#泄漏判断标准)
    - [常见泄漏根因 Top 5](#常见泄漏根因-top-5)
  - [7.2 大对象场景](#72-大对象场景)
    - [典型](#典型)
    - [定位](#定位)
    - [解决](#解决)
  - [7.3 缓存不当场景](#73-缓存不当场景)
    - [错误](#错误)
    - [正确](#正确)
  - [7.4 集合类未释放场景](#74-集合类未释放场景)
    - [典型陷阱](#典型陷阱)
    - [修复](#修复)
  - [7.5 ThreadLocal 泄漏场景](#75-threadlocal-泄漏场景)
    - [错误](#错误-1)
    - [为什么会泄漏？](#为什么会泄漏)
    - [修复](#修复-1)
    - [面试题延伸](#面试题延伸)
  - [7.6 类加载器泄漏场景](#76-类加载器泄漏场景)
    - [典型](#典型-1)
    - [排查](#排查)
    - [修复](#修复-2)
  - [7.7 Netty / NIO Direct Buffer 泄漏](#77-netty--nio-direct-buffer-泄漏)
    - [泄漏模式](#泄漏模式)
    - [诊断](#诊断)
    - [修复原则](#修复原则)
- [八、JVM 参数调优建议](#八jvm-参数调优建议)
  - [8.1 堆参数](#81-堆参数)
  - [8.2 GC 相关参数](#82-gc-相关参数)
    - [8.2.1 G1（JDK 9+ 默认，推荐 8G+ 大堆）](#821-g1jdk-9-默认推荐-8g-大堆)
    - [8.2.2 CMS（JDK 8 中低版本）](#822-cmsjdk-8-中低版本)
    - [8.2.3 ZGC / Shenandoah（亚毫秒级停顿，JDK 11+）](#823-zgc--shenandoah亚毫秒级停顿jdk-11)
  - [8.3 Metaspace 参数](#83-metaspace-参数)
  - [8.4 OOM 现场保护参数](#84-oom-现场保护参数)
  - [8.5 生产环境推荐参数](#85-生产环境推荐参数)
- [九、面试高频题](#九面试高频题)
  - [9.1 原理篇](#91-原理篇)
    - [Q1：你知道哪几种 OutOfMemoryError？分别对应哪些内存区域？](#q1你知道哪几种-outofmemoryerror分别对应哪些内存区域)
    - [Q2：说一下 JVM 内存模型（运行时数据区），每个区域的作用？哪些会发生 OOM？](#q2说一下-jvm-内存模型运行时数据区每个区域的作用哪些会发生-oom)
    - [Q3：什么是内存泄漏？和内存溢出有什么区别？](#q3什么是内存泄漏和内存溢出有什么区别)
    - [Q4：GC overhead limit exceeded 和 Java heap space 有什么区别？实际工作中怎么看？](#q4gc-overhead-limit-exceeded-和-java-heap-space-有什么区别实际工作中怎么看)
    - [Q5：为什么会发生 Metaspace OOM？怎么排查？](#q5为什么会发生-metaspace-oom怎么排查)
  - [9.2 定位实战篇](#92-定位实战篇)
    - [Q6：线上出现 OOM，你第一时间做什么？请描述完整的排查流程。](#q6线上出现-oom你第一时间做什么请描述完整的排查流程)
    - [Q7：堆转储文件很大（几十 G），打开 MAT 分析很慢，有什么技巧？](#q7堆转储文件很大几十-g打开-mat-分析很慢有什么技巧)
    - [Q8：如何区分内存泄漏和内存溢出（堆太小）？](#q8如何区分内存泄漏和内存溢出堆太小)
    - [Q9：生产环境发生 OOM，但是没开 HeapDumpOnOutOfMemoryError，有什么补救办法？](#q9生产环境发生-oom但是没开-heapdumponoutofmemoryerror有什么补救办法)
  - [9.3 进阶调优篇](#93-进阶调优篇)
    - [Q10：大促前，如何做 OOM 预防？](#q10大促前如何做-oom-预防)
    - [Q11：Direct Buffer Memory 如何监控和定位泄漏？](#q11direct-buffer-memory-如何监控和定位泄漏)
    - [Q12：Full GC 频繁但不是泄漏，有什么调优思路？](#q12full-gc-频繁但不是泄漏有什么调优思路)
    - [Q13：ThreadLocal 为什么会导致内存泄漏？如何正确使用？](#q13threadlocal-为什么会导致内存泄漏如何正确使用)
    - [Q14：JDK 7 String.intern() 放到哪了？JDK 8 呢？PermGen vs Metaspace](#q14jdk-7-stringintern-放到哪了jdk-8-呢permgen-vs-metaspace)
    - [Q15：如何设计一个"线上 OOM 自动应急系统"？](#q15如何设计一个线上-oom-自动应急系统)
    - [Q16：G1 调优中常见的 Evacuation Failure 是什么？如何解决？](#q16g1-调优中常见的-evacuation-failure-是什么如何解决)
    - [Q17：Kubernetes Docker 环境里 JVM OOM 容易踩哪些坑？](#q17kubernetes-docker-环境里-jvm-oom-容易踩哪些坑)
- [十、最佳实践与 checklist](#十最佳实践与-checklist)
  - [10.1 上线前 OOM 防护 Checklist](#101-上线前-oom-防护-checklist)
  - [10.2 常见 6 种 OOM 速查表](#102-常见-6-种-oom-速查表)
  - [10.3 排查思路速记图](#103-排查思路速记图)
  - [10.4 推荐资源](#104-推荐资源)
  - [10.5 实战项目案例汇总（面试背诵）](#105-实战项目案例汇总面试背诵)
- [十一、OOM 应急响应 SOP](#十一oom-应急响应-sop)
  - [11.1 应急响应总览：黄金 5 分钟](#111-应急响应总览黄金-5-分钟)
  - [11.2 第一步：立即摘流（秒级动作）（黄金原则：先保命，再取证）](#112-第一步立即摘流秒级动作黄金原则先保命再取证)
    - [11.2.1 Kubernetes 环境（最常用）](#1121-kubernetes-环境最常用)
    - [11.2.2 Nginx / 网关 / F5 摘流](#1122-nginx--网关--f5-摘流)
    - [11.2.3 紧急 iptables（兜底）](#1123-紧急-iptables兜底)
  - [11.3 第二步：保留现场（销毁证据的 7 个禁忌）](#113-第二步保留现场销毁证据的-7-个禁忌)
    - [正确的现场保护操作 ✅](#正确的现场保护操作-)
  - [11.4 第三步：现场快照抓取（Dump 提取）](#114-第三步现场快照抓取dump-提取)
    - [11.4.1 抓取顺序与优先级](#1141-抓取顺序与优先级)
    - [11.4.2 一键抓取脚本](#1142-一键抓取脚本)
    - [11.4.3 非常大的堆怎么办（\>32G）？](#1143-非常大的堆怎么办32g)
  - [11.5 第四步：分析环境准备（MAT 调优）](#115-第四步分析环境准备mat-调优)
    - [11.5.1 MAT 配置调优](#1151-mat-配置调优)
    - [11.5.2 Linux 无头模式（推荐）](#1152-linux-无头模式推荐)
    - [11.5.3 解析失败怎么办？](#1153-解析失败怎么办)
  - [11.6 第五步：Dump 深入分析（四种核心技法）](#116-第五步dump-深入分析四种核心技法)
    - [技法 1：Leak Suspects Report（最省事）](#技法-1leak-suspects-report最省事)
    - [技法 2：Histogram → Retained Heap → Path to GC Roots（最精准）](#技法-2histogram--retained-heap--path-to-gc-roots最精准)
    - [技法 3：两次 Dump 对比（找"增长最快的类"=泄漏类）](#技法-3两次-dump-对比找增长最快的类泄漏类)
    - [技法 4：OQL（对象查询语言，高级排查）](#技法-4oql对象查询语言高级排查)
    - [四种技法组合拳（推荐顺序）](#四种技法组合拳推荐顺序)
  - [11.7 第六步：区分内存泄漏 vs 内存膨胀](#117-第六步区分内存泄漏-vs-内存膨胀)
    - [11.7.1 定义](#1171-定义)
    - [11.7.2 定量判断公式](#1172-定量判断公式)
    - [11.7.3 决策树](#1173-决策树)
  - [11.8 第七步：修复验证 + 复盘闭环](#118-第七步修复验证--复盘闭环)
    - [11.8.1 修复验证四步](#1181-修复验证四步)
    - [11.8.2 复盘模板（5Why）](#1182-复盘模板5why)
  - [11.9 应急响应全流程图](#119-应急响应全流程图)

---

# 一、OOM 概述

## 1.1 什么是 OOM

**OutOfMemoryError（简称 OOM）** 是 JVM 在无法为对象分配足够内存空间、无法创建必要的系统资源（线程、类、缓冲区）时抛出的致命错误。它继承自 `java.lang.Error`，属于**不可恢复的运行时错误**，意味着应用已处于不正常状态。

```java
package java.lang;

public class OutOfMemoryError extends VirtualMachineError {
    private static final long serialVersionUID = 8228564086184010517L;
    public OutOfMemoryError() { super(); }
    public OutOfMemoryError(String s) { super(s); }
}
```

**重要特征**：

| 特征 | 说明 |
|------|------|
| **错误类型** | `Error` 不是 `Exception`，一般应用代码不应捕获并吞掉 |
| **抛出时机** | 在 `new` 对象、数组创建、类加载、反射、线程创建等操作中 |
| **可预测** | 大多数情况（非瞬时突增）可通过监控提前预警 |
| **分类** | 约有 8 种常见 message，每种 message 对应不同根因 |

---

## 1.2 OOM 与 StackOverflowError 的区别

```
OutOfMemoryError：堆/元空间/直接内存/栈空间 总量不足
StackOverflowError：单线程的栈深度过大（递归等），每个线程栈空间还够用，但放不下当前栈帧
```

| 对比项 | OutOfMemoryError | StackOverflowError |
|--------|------------------|--------------------|
| **归属区域** | 堆/Metaspace/Direct/Native 等 | Java Stack |
| **典型原因** | 对象太多、内存泄漏、类太多 | 递归无终止、无限循环调用 |
| **影响范围** | 进程级，可能全局挂掉 | 线程级，只影响当前线程 |
| **JVM 参数** | `-Xmx`、`-XX:MaxMetaspaceSize` | `-Xss` |
| **是否常见** | 非常常见 | 少（写递归都会注意） |
| **处理方式** | 分析堆转储、优化代码 | 改递归为循环、或增大栈 |

```java
// 造成 StackOverflowError（栈深度溢出）
void recursive() { recursive(); }

// 造成 OutOfMemoryError（堆空间不足）
List<byte[]> leak = new ArrayList<>();
while (true) leak.add(new byte[1024 * 1024]);
```

---

## 1.3 OOM 出现的触发点

JVM 在多个执行路径中可能抛出 OOM：

```
JVM OOM 触发点分布：

  1. new 关键字 / 对象分配
        ↓
  ┌─────────────────┐    ┌───────────────────┐
  │  Young GC 失败  │ →  │ 晋升到老年代失败  │
  └─────────────────┘    └───────────────────┘
                               ↓
                       Full GC / 并发标记失败
                               ↓
                       java.lang.OutOfMemoryError: Java heap space

  2. ClassLoader 加载类
        ↓
     Metaspace / Compressed Class Space 满
        ↓
     java.lang.OutOfMemoryError: Metaspace

  3. allocateDirect()
        ↓
     Direct Buffer 达到 -XX:MaxDirectMemorySize
        ↓
     java.lang.OutOfMemoryError: Direct buffer memory

  4. new Thread()
        ↓
     系统资源耗尽（PID 上限、虚拟内存、用户线程数）
        ↓
     java.lang.OutOfMemoryError: unable to create new native thread
```

---

# 二、JVM 内存模型与 OOM 对应关系

## 2.1 JVM 运行时数据区总览

```
┌─────────────────────────────────────────────────────────────────┐
│                       JVM 内存结构（JDK 8+）                     │
├──────────────────────────────┬──────────────────────────────────┤
│                              │  线程共享                          │
│                              ├──────────────────────────────────┤
│                              │  Heap（堆）                       │
│                              │  ┌── Eden ──┐                    │
│                              │  │           │  Young Gen        │
│                              │  ├── S0/S1 ──┘                    │
│                              │  ├────────────── Old Gen ──────┐  │
│                              │  │                                ││
│                              │  └──────────────────────────────┘│
│                              ├──────────────────────────────────┤
│                              │  Metaspace                       │
│  线程私有                      │  ├ Class Metadata               │
│  ├────────────── PC           │  ├ JIT Compiled Code            │
│  ├────────────── JVM Stack    │  └ ClassLoader Refs             │
│  ├────────────── Native Stack ├──────────────────────────────────┤
│  └────────────── Heap Ref ──→ │  Code Cache                      │
│                              ├──────────────────────────────────┤
│                              │  Direct Memory（JVM 外）         │
│                              │  ├ ByteBuffer.allocateDirect     │
│                              │  └ Netty Unpooled                │
└──────────────────────────────┴──────────────────────────────────┘
```

---

## 2.2 各区域与 OOM 类型映射

| 区域 | 大小控制参数 | 对应 OOM 类型 |
|------|-------------|---------------|
| **堆（Heap）** | `-Xms` / `-Xmx` / `-XX:NewRatio` / `-XX:SurvivorRatio` | `Java heap space`、`GC overhead limit exceeded`、`Requested array size exceeds VM limit` |
| **Metaspace** | `-XX:MetaspaceSize` / `-XX:MaxMetaspaceSize` | `Metaspace`、`Compressed class space` |
| **Code Cache** | `-XX:InitialCodeCacheSize` / `-XX:ReservedCodeCacheSize` | `CodeCache is full` |
| **Direct Memory** | `-XX:MaxDirectMemorySize`（默认 = `-Xmx`） | `Direct buffer memory` |
| **Thread Stack** | `-Xss` × 线程数 | `unable to create new native thread` |
| **Compressed Class Space** | `-XX:CompressedClassSpaceSize` | `Compressed class space` |
| **Native Heap** | 操作系统限制 | `Native allocation failed` |

---

# 三、8 种 OOM 类型详解

## 3.1 Java heap space

**错误信息**：
```
java.lang.OutOfMemoryError: Java heap space
```

**含义**：堆内存满，经过 Young GC + Full GC 后仍无法分配新对象。

**最常见原因**：

1. **内存泄漏**（占 70%）：对象被错误引用无法回收。
2. **大对象分配失败**：单次分配超过剩余连续空间。
3. **堆设置太小**：业务增长超出预期。
4. **Finalizer 队列堆积**：`finalize()` 方法太慢，对象堆积。
5. **Class 未卸载**：动态生成大量 Class 实例。

**代码复现**：

```java
// 1. 无限循环创建大数组
public class HeapOOM {
    public static void main(String[] args) {
        // -Xms20m -Xmx20m -XX:+HeapDumpOnOutOfMemoryError
        List<byte[]> list = new ArrayList<>();
        int i = 0;
        while (true) {
            list.add(new byte[1 * 1024 * 1024]); // 每轮 1MB
            System.out.println("count: " + (++i));
        }
    }
}
```

**分析思路**：看堆转储，找最大对象、大对象的 dominator tree。

---

## 3.2 GC overhead limit exceeded

**错误信息**：
```
java.lang.OutOfMemoryError: GC overhead limit exceeded
```

**含义**：JVM 花费 98% 以上的时间做 GC，但回收回来的堆空间不到 2%（连续 5 次 GC 均如此），JVM 判定"做 GC 不如直接报 OOM"。

```
JDK 内部门槛（可以调）：
- GC 时间占比 > 98%  → 触发条件 A
- 回收内存占比 < 2%  → 触发条件 B
- A && B 连续 5 次    → 抛出 OOM
```

**典型场景**：

- 堆接近满了，每次 GC 只能收回少量对象（内存泄漏末期）。
- 大缓存 + 缓存命中率低 → 每次 GC 回收的缓存很少。

```java
// -Xms20m -Xmx20m
// 造成 GC Overhead：每次 GC 只回收 1-2 个弱引用对象
public class GCOverhead {
    public static void main(String[] args) {
        Map<String, String> cache = new HashMap<>();
        Random random = new Random();
        while (true) {
            cache.put("key_" + random.nextInt(100_000), 
                      "value_".repeat(random.nextInt(100)));
        }
    }
}
```

**与 heap space 的区别**：`heap space` 是"确实分配不了新对象"；`GC overhead` 是"还能勉强收回一点，但这样做性价比太低"，前者比后者更严重。

---

## 3.3 PermGen space / Metaspace

**错误信息**（JDK 7 及之前）：
```
java.lang.OutOfMemoryError: PermGen space
```

**错误信息**（JDK 8+）：
```
java.lang.OutOfMemoryError: Metaspace
```

**含义**：方法区（存储类元数据、常量池、静态变量、JIT 编译代码）满了。

| 版本 | 区域名 | 位置 | 大小参数 |
|------|--------|------|----------|
| JDK 6 及以前 | PermGen（永久代） | 堆内 | `-XX:PermSize` / `-XX:MaxPermSize` |
| JDK 7 | PermGen + 字符串常量池移到堆 | 部分堆内 | 同上 |
| JDK 8+ | Metaspace（元空间） | **本地内存** | `-XX:MaxMetaspaceSize` |

**典型原因**：

1. **类加载器泄漏**：动态加载类但 ClassLoader 无法被回收（如 CGLib/ByteBuddy 动态生成的类）。
2. **反射动态代理**：`Proxy.newProxyInstance()` 无限循环生成。
3. **Spring 热部署**：旧 ClassLoader 下的类没卸载。
4. **大量 JSP**：JSP 第一次访问生成 Servlet 类。
5. **字符串常量池**（JDK 6 特有）：`String.intern()` 太多。

**代码复现**：

```java
// 动态生成 10w 个类，造成 Metaspace 溢出
public class MetaspaceOOM {
    public static void main(String[] args) {
        // -XX:MaxMetaspaceSize=50m
        for (int i = 0; i < 100_000; i++) {
            Enhancer enhancer = new Enhancer();
            enhancer.setSuperclass(OOMObject.class);
            enhancer.setUseCache(false);
            enhancer.setCallback((MethodInterceptor) (obj, method, args1, proxy) ->
                    proxy.invokeSuper(obj, args1));
            enhancer.create();
        }
    }
}
```

---

## 3.4 Direct buffer memory

**错误信息**：
```
java.lang.OutOfMemoryError: Direct buffer memory
```

**含义**：堆外内存（Direct ByteBuffer / Unsafe.allocateMemory）已达上限。

```
JVM 进程总内存 ≈ Heap(-Xmx) + Metaspace + Code Cache + Direct Memory + Thread Stack + JIT/Native Overhead

Direct Memory 上限：-XX:MaxDirectMemorySize（默认 = -Xmx - Survivor，约等于 Xmx）
```

**典型原因**：

1. **Netty**：大量使用 `PooledByteBuf` 未 `release()`（最常见）。
2. **NIO**：`ByteBuffer.allocateDirect()` 创建未释放。
3. **Spark / Flink**：TaskManager 堆外内存设置过小。
4. **堆过大**：`-Xmx` 设得太满，操作系统剩余给 Direct 的不够。

**代码复现**：

```java
// -XX:MaxDirectMemorySize=10m
public class DirectMemoryOOM {
    private static final int _1MB = 1024 * 1024;

    public static void main(String[] args) {
        Field unsafeField = Unsafe.class.getDeclaredFields()[0];
        unsafeField.setAccessible(true);
        Unsafe unsafe = (Unsafe) unsafeField.get(null);
        while (true) {
            unsafe.allocateMemory(_1MB); // 分配堆外 1MB
        }
    }
}
```

---

## 3.5 unable to create new native thread

**错误信息**：
```
java.lang.OutOfMemoryError: unable to create new native thread
```

**含义**：JVM 要创建一个 Java Thread，底层调用 OS 的 `pthread_create()` 失败（内核线程已达上限）。

**触发条件（任一）**：

1. **用户级线程数超限**：`ulimit -u` 设置太低（如 1024）。
2. **PID 上限**：`/proc/sys/kernel/pid_max` 不够。
3. **虚拟内存耗尽**：每个线程栈 `-Xss512k`，1w 个线程占用 5GB 虚拟地址空间，32 位系统尤其严重。
4. **max_map_count 过低**：`/proc/sys/vm/max_map_count`（默认 65530）。

**代码复现**：

```java
public class ThreadOOM {
    public static void main(String[] args) {
        for (int i = 0; ; i++) {
            System.out.println("thread #" + i);
            new Thread(() -> {
                try { Thread.sleep(10_000_000L); } catch (InterruptedException e) {}
            }).start();
        }
    }
}
```

---

## 3.6 Requested array size exceeds VM limit

**错误信息**：
```
java.lang.OutOfMemoryError: Requested array size exceeds VM limit
```

**含义**：代码试图分配一个超过 JVM 实现上限（接近 `Integer.MAX_VALUE - 8` ≈ 21 亿）的数组，甚至还没真正分配就被 JVM 拒绝。

```java
// 直接抛出，跟堆大小无关
public class ArrayOOM {
    public static void main(String[] args) {
        int[] arr = new int[Integer.MAX_VALUE];  // 100% 会 OOM
    }
}
```

这种 OOM 通常是**代码 bug**（变量溢出或参数传错），不是真的内存不够。

---

## 3.7 GC pause (G1 Evacuation Pause / Full GC)

**严格讲不是 OOM**，但常被误判为 OOM：服务长时间 STW（Stop The World）导致业务超时、健康检查失败，表现"像 OOM 一样挂掉"。

| GC 类型 | 典型原因 |
|---------|----------|
| **Full GC 频繁** | Old Gen 满、Promotion Failure、Concurrent Mode Failure |
| **G1 Evacuation Failure** | 复制 Survivor 到 Old 时没有空 Region |
| **长时间 Remark** | 元数据区对象太多，引用处理慢 |

这种情况不一定抛出 OOM，但需要用 OOM 排查的相同思路分析：看 GC Log、看堆转储、看对象分布。

---

## 3.8 Compressed class space / Native allocation

**错误信息**：
```
java.lang.OutOfMemoryError: Compressed class space
java.lang.OutOfMemoryError: Native memory allocation (malloc) failed to allocate xxx bytes
```

- **Compressed class space**：Metaspace 下专门存放 Klass 对象的区域。类太多但单个类不是很大时触发。用 `-XX:+UseCompressedClassPointers` 时才会有。
- **Native allocation failed**：C++ 层 `malloc()` 失败，通常是操作系统本身内存已用尽（Docker cgroup 限制、swap 用完、物理内存满）。

---

# 四、标准 OOM 定位步骤

## 4.1 总览：五步定位法

```
          ┌──────────────────────────────────────┐
 Step 1 → │  现象确认与现场保护（不重启！）         │
          └──────────────┬───────────────────────┘
                         ↓
          ┌──────────────────────────────────────┐
 Step 2 → │  抓取堆转储 / 线程转储 / GC Log       │
          └──────────────┬───────────────────────┘
                         ↓
          ┌──────────────────────────────────────┐
 Step 3 → │  核查 JVM 启动参数 + 版本 + 环境      │
          └──────────────┬───────────────────────┘
                         ↓
          ┌──────────────────────────────────────┐
 Step 4 → │  工具分析 → 定位根因（泄漏/大对象/参数）│
          └──────────────┬───────────────────────┘
                         ↓
          ┌──────────────────────────────────────┐
 Step 5 → │  修复 → 验证 → 复盘 → 加监控告警       │
          └──────────────────────────────────────┘
```

---

## 4.2 Step 1：现象确认与现场保护

**第一要务：保留现场，不要急着重启。**

```bash
# 1. 确认进程活着
ps -ef | grep java
jps -lv                # 列出所有 Java 进程 + 启动参数

# 2. 查看进程状态
top -Hp <pid>          # 看哪几个线程耗 CPU 高
cat /proc/<pid>/status # 看 VmRSS/VmSize/Threads

# 3. 查看磁盘（堆转储需要足够磁盘空间）
df -h                  # 堆转储 = 堆大小，先确认 /tmp 或 dump 目录有空间

# 4. 临时限流（不要重启！先把入口流量切掉保留现场）
#    a. 从 Nginx/网关摘掉该实例
#    b. 或用 iptables 切断外部请求
#    c. 如果是 Spring Boot Actuator：
curl -X POST http://localhost:8080/actuator/service-registry?status=OUT_OF_SERVICE
```

**如果不保留现场的代价**：

- 重启后堆转储 = 0，根本没法查。
- 只能靠下一次复现，生产 OOM 复现可能要几天甚至几周。

---

## 4.3 Step 2：抓取堆转储与线程转储

> **原则：多个 dump 对比更能定位泄漏。** 至少间隔 10-30 秒抓两次。

### 4.3.1 堆转储（Heap Dump）

```bash
# 方式 1：jmap（最常用）
jmap -dump:format=b,file=heap_01.hprof <pid>
jmap -dump:format=b,file=heap_02.hprof <pid>     # 再抓一次做对比
jmap -dump:live,format=b,file=heap_live.hprof <pid>  # live 参数先做一次 Full GC

# 方式 2：jcmd（JDK 8+ 推荐）
jcmd <pid> GC.heap_dump heap_01.hprof
jcmd <pid> GC.heap_dump -all heap_01_all.hprof   # 含不可达对象

# 方式 3：OOM 自动 dump（强烈建议生产环境开启）
java -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/var/log/dumps/ \
     -jar app.jar

# 方式 4：kill -3（某些 JVM 实现会生成 dump，慎用）
kill -3 <pid>
```

### 4.3.2 线程转储（Thread Dump）

```bash
# 方式 1：jstack（间隔抓 3-5 次）
jstack <pid> > thread_01.txt
sleep 10
jstack <pid> > thread_02.txt
sleep 10
jstack <pid> > thread_03.txt

# 方式 2：jcmd
jcmd <pid> Thread.print > thread.txt

# 方式 3：kill -3（输出到 JVM stdout/logs）
kill -3 <pid>
```

### 4.3.3 GC 实时监控

```bash
# 方式 1：jstat
jstat -gcutil <pid> 1000 10   # 每 1 秒 1 次，共 10 次，打印各内存使用率
jstat -gccause <pid> 5000    # 每 5 秒打印 GC 原因
jstat -gcnew <pid>           # 只看年轻代

# 方式 2：打印 GC 详细日志（推荐启动时就开）
# 启动参数：
# JDK 8: -XX:+PrintGCDetails -XX:+PrintGCDateStamps -Xloggc:/var/log/gc.log -XX:+UseGCLogFileRotation -XX:NumberOfGCLogFiles=10 -XX:GCLogFileSize=100m
# JDK 9+: -Xlog:gc*:file=/var/log/gc.log:time,level,tags:filesize=100M:filecount=10
```

---

## 4.4 Step 3：JVM 参数与启动参数核查

```bash
# 1. 启动参数（最核心）
jinfo -flags <pid>                # 查看非默认的参数
jinfo -flag MaxHeapSize <pid>     # 单独看某个参数值值
jcmd <pid> VM.flags               # 另一种方式

# 2. 看系统属性
jinfo -sysprops <pid>             # 所有 -Dxxx
jcmd <pid> VM.system_properties

# 3. JDK 版本
java -version
jcmd <pid> VM.version

# 4. 内存总览
jmap -heap <pid>                  # 打印堆使用情况（G1 下可能不准）
jcmd <pid> GC.class_histogram | head -30  # top30 类实例数
```

**启动参数核查清单**：

```
□ -Xms / -Xmx       是否相等（生产建议相等，避免扩缩容抖动）
□ -Xmn / NewRatio   年轻代大小是否合理（建议堆 30%-40%）
□ +UseG1GC / +UseConcMarkSweepGC / +UseZGC  GC 选择是否匹配业务
□ MaxMetaspaceSize  是否设置了上限（不设理论上等于 OS 内存）
□ +HeapDumpOnOutOfMemoryError  是否开启
□ HeapDumpPath      路径是否有写权限、磁盘是否够
□ MaxDirectMemorySize  Direct 内存是否够用
```

---

## 4.5 Step 4：根因定位（工具分析）

```
优先级策略：

  1. 先看 GC 日志 → 是否 GC 频繁？
     ├→ 是：看 Old 使用率曲线是否趋势上升 → 内存泄漏特征
     └→ 否：瞬时流量 / 大对象

  2. 再看 thread dump → 是否 BLOCKED？是否 1w+ 线程？
     ├→ 大量 BLOCKED → 死锁 / DB 阻塞
     └→ 线程总数 1w+ → 线程数失控

  3. 最后看 heap dump（耗时间，成本最高）
     ├→ MAT Histogram → 什么类实例数最多 / 占用最大？
     ├→ Dominator Tree → 谁持有最大对象？
     ├→ Path to GC Roots → 为什么没被回收？
     └→ Leak Suspects Report → MAT 给出的泄漏嫌疑报告
```

### 4.5.1 GC 日志分析关键指标

```
指标                       正常值          危险值
Full GC 频率              <1 次/小时        >1 次/分钟
Young GC 频率             每秒数次          >20 次/秒
Young GC 耗时             <50ms             >200ms
Old 使用率趋势             平稳             持续上升不下降
Heap After Full GC         稳定             每次都更高（泄漏）
```

### 4.5.2 线程 dump 分析要点

```bash
# 用 fastthread.io / spotify threaddump analyzer 可视化
# 手工分析时关注：

# 1. 线程总数
grep -c '^"[^"]*"' thread_01.txt

# 2. 状态分布（RUNNABLE / BLOCKED / WAITING / TIMED_WAITING）
grep "java.lang.Thread.State" thread_01.txt | sort | uniq -c | sort -rn

# 3. 找死锁
jstack -l <pid> | grep -A 30 "Found one Java-level deadlock"
```

### 4.5.3 堆转储分析（MAT）

步骤：

1. 打开 MAT → File → Open Heap Dump。
2. 先跑 **Leak Suspects Report**，看是否有嫌疑泄漏点。
3. 点 **Histogram** → 按 `Retained Heap` 倒序 → 找到 Retained 最大的类。
4. 右键该类 → **Merge Shortest Path to GC Roots → exclude all phantom/weak/soft/etc references**。
5. 看谁持有引用 → 确定是代码哪里没释放。
6. 对前后两个 dump 做 **Compare Basket** → 看增长最多的类。

---

## 4.6 Step 5：验证修复与复盘

修复后，不要直接上生产：

```
1. 压测验证
   - 同模型压测环境，跑 N 小时，看内存曲线是否稳定。
   - 关键指标：Old Gen 是否持续上升？Full GC 是否频繁？

2. 灰度发布
   - 先上 1 台实例，观察足够长时间（> 典型泄漏周期）。
   - 监控：Heap / Metaspace / Direct / Thread / GC。

3. 复现 Case（可选但推荐）
   - 写单元测试复现泄漏路径，避免回归。

4. 复盘（5Why）
   - 为什么泄漏？   → 线程池中的 ThreadLocal 没 remove
   - 为什么没 remove？ → 开发遗忘
   - 为什么没被 review 发现？ → 缺少 checklist
   - 为什么没告警？ → Heap > 80% 没有告警
   - 行动项：补 checklist + 加 Heap 使用率告警 + Lint 规则

5. 加固
   - 加告警：Heap 80% / Full GC 每小时 > 3 次 / Metaspace 85%
   - 加测试：集成测试做 "内存稳定性测试"
   - 加参数：-XX:+HeapDumpOnOutOfMemoryError -XX:ExitOnOutOfMemoryError
```

---

# 五、核心工具详解

## 5.1 JDK 内置工具速查

| 工具 | 适用阶段 | 命令入口 | 用途 |
|------|----------|----------|------|
| `jps` | 排查前期 | `jps -lv` | 列出 Java 进程 + 启动参数 |
| `jstat` | 实时监控 | `jstat -gcutil <pid> 1000 10` | GC 实时统计 |
| `jmap` | 现场抓取 | `jmap -dump:file=x.hprof <pid>` | 堆转储、类实例直方图 |
| `jstack` | 现场抓取 | `jstack <pid> > t.txt` | 线程转储、死锁检测 |
| `jhat` | 离线分析 | `jhat x.hprof` | 浏览器方式浏览堆 dump |
| `jinfo` | 参数核查 | `jinfo -flags <pid>` | 查看/修改 JVM 参数 |
| `jcmd` | 万能工具 | `jcmd <pid> help` | JDK 8+ 推荐，能替代 jmap/jstack/jinfo |
| `jhsdb` | 调试 | `jhsdb jmap --pid <pid>` | JDK 9+，附加到运行中或 core dump |

---

## 5.2 jmap：堆转储与对象统计

### 5.2.1 常用命令

```bash
# 1. 堆转储（最常用）
jmap -dump:format=b,file=/tmp/dump_$(date +%s).hprof <pid>
# live 可选：dump 前强制执行一次 Full GC
jmap -dump:live,format=b,file=/tmp/dump_live.hprof <pid>

# 2. 类实例直方图（无需 dump，快）
jmap -histo <pid> | head -30           # 所有对象
jmap -histo:live <pid> | head -30       # 可达对象（会触发 Full GC！）

# 3. 堆配置概览
jmap -heap <pid>                        # 打印堆使用情况（G1 下不太准）

# 4. Finalizer 队列
jmap -finalizerinfo <pid>               # 查看等待 finalize 的对象

# 5. ClassLoader 统计
jmap -clstats <pid>                     # 各 ClassLoader 的类数、占用
```

### 5.2.2 jmap -histo 输出解读

```
 num     #instances         #bytes  class name
----------------------------------------------
   1:       8976523      718121840  [B          # byte[] 最多（可能是缓存）
   2:       5023124      120554976  java.lang.String
   3:       2011234       96723136  com.xxx.OrderDTO
   4:         48921        7662336  com.xxx.User
```

- 先看 `class name`，找到业务自定义类（非 JDK）。
- 如果一个业务类实例数"夸张"（比如 OrderDTO 200w 个），基本就是缓存没清。
- `[B` = byte[]、`[C` = char[]、`[Ljava.lang.String;` = String[]，数组类型开头是 `[`。

---

## 5.3 jstat：GC 实时监控

### 5.3.1 常用命令

```bash
# 最常用：-gcutil（概览）
jstat -gcutil <pid> 1000 5
# 每 1 秒打印一行，共 5 行
#
# 输出：
#  S0     S1     E      O      M     CCS    YGC     YGCT    FGC    FGCT     GCT
#  0.00 100.00  72.33  89.12  76.44  72.10    200   12.123     5    3.456   15.579
#
# S0/S1：Survivor 使用率%
# E：Eden 使用率%
# O：Old 使用率%        ← 关键！看是否持续上升
# M：Metaspace 使用率%
# CCS：Compressed Class Space 使用率%
# YGC：Young GC 次数
# YGCT：Young GC 累计耗时
# FGC：Full GC 次数         ← 关键！>0 就值得关注
# FGCT：Full GC 累计耗时
# GCT：所有 GC 累计耗时（= YGCT+FGCT）

# 其他常用子命令
jstat -gccause <pid> 5000      # 额外显示最近 GC 的原因
jstat -gc <pid> 1000           # 显示绝对容量（KB）而非%
jstat -gcnew <pid>             # 只看年轻代
jstat -gcold <pid>             # 只看老年代
jstat -gcmetacapacity <pid>    # 只看元空间
```

### 5.3.2 实战判断

```
场景 A（好）：
  O：23% -> 23% -> 24%  →  稳态
  FGC：0，YGCT 很低

场景 B（泄漏嫌疑）：
  O：30% -> 50% -> 70% -> 85% -> （Full GC 后）60% -> 75% -> 88% ...
  每次 Full GC 后老年代都不能回落
  → 内存泄漏！

场景 C（GC Overhead 嫌疑）：
  GCT 每秒都在增加，但堆没明显释放
  → GC 时间占比很高

场景 D（瞬时突增）：
  某时刻 YGC 突然飙升，之后恢复正常
  → 单次大对象 / 流量突增，不是泄漏
```

---

## 5.4 jstack：线程转储

### 5.4.1 常用命令

```bash
# 1. 基础线程 dump
jstack <pid> > t1.txt
sleep 5
jstack <pid> > t2.txt   # 间隔几秒多次抓，对比更准

# 2. 加 -l 打印锁（会慢一点）
jstack -l <pid> > t3.txt
# 输出末尾可能有：
#   Found one Java-level deadlock:
#   =============================
#   ...

# 3. 强制 dump（进程无响应时，-F）
jstack -F <pid>
```

### 5.4.2 手工分析脚本

```bash
# 统计各状态线程数
grep "java.lang.Thread.State" t.txt | sort | uniq -c | sort -rn

# 统计线程总数
grep -c '^"' t.txt

# 找 BLOCKED 线程
grep -B2 "java.lang.Thread.State: BLOCKED" t.txt

# 找死锁关键字
grep -A 30 "Found one Java-level deadlock" t.txt
```

### 5.4.3 解读线程栈

```
"OrderService-ThreadPool-123" #123 prio=5 os_prio=0 tid=0x00007f... nid=0x1a2b
 waiting for monitor entry [0x00007f..., 0x00007f...]
   java.lang.Thread.State: BLOCKED (on object monitor)
        at com.xxx.OrderService.placeOrder(OrderService.java:88)
        - waiting to lock <0x00000000deadbeef> (a java.lang.Object)
        ...
   Locked ownable synchronizers:
        - None
```

- **BLOCKED on object monitor**：等待进入 `synchronized` 块，找到 "waiting to lock <0xxxxx>"，再找 "locked <0xxxxx>" 是谁。
- **WAITING (on object monitor)**：`wait()` 调用，正常。
- **TIMED_WAITING (parking)**：`LockSupport.parkNanos`，通常是线程池 idle。
- **RUNNABLE (in socketRead)**：线程阻塞在网络 IO。

---

## 5.5 jhat：离线堆分析

```bash
jhat -J-Xmx8g dump.hprof   # -J 传内存给 jhat，dump 大时要调大
# 服务启动：
#   Started HTTP server on port 7000
#   Server is ready.
# 浏览器打开 http://localhost:7000
# 最有用的链接：
#   - Show heap histogram（直方图）
#   - Show all classes including platform（全部类）
#   - Show instance counts for all classes（实例数）
#   - Execute Object Query Language (OQL) query ← 类似 SQL 查堆
```

OQL 示例（Jhat / MAT / VisualVM 通用）：

```sql
// 查所有 Order 实例
SELECT o FROM com.xxx.Order o

// 查金额 > 10000 的订单
SELECT o FROM com.xxx.Order o WHERE o.amount > 10000

// 查字符串长度 > 10000（长字符串可能是问题）
SELECT s FROM java.lang.String s WHERE s.count > 10000
```

现代生产推荐用 **MAT**（Memory Analyzer Tool），jhat 主要是应急。

---

## 5.6 jinfo：运行时参数查看

```bash
# 1. 查看启动参数
jinfo -flags <pid>

# 2. 查看单个参数
jinfo -flag MaxHeapSize <pid>
jinfo -flag UseG1GC <pid>
jinfo -flag HeapDumpOnOutOfMemoryError <pid>

# 3. 运行时修改参数（只对 manageable 参数有效）
jinfo -flag +PrintGCDetails <pid>           # 开启打印 GC
jinfo -flag -PrintGCDetails <pid>           # 关闭
jinfo -flag HeapDumpAfterFullGC=true <pid>  # Full GC 后 dump

# 4. 系统属性
jinfo -sysprops <pid>
```

哪些参数支持运行时改？`java -XX:+PrintFlagsFinal -version | grep manageable`。

---

## 5.7 VisualVM / MAT 图形化分析

### 5.7.1 VisualVM（Oracle 官方，适合实时观察）

```
场景：开发环境 / 低负载时连到应用看实时数据
优势：CPU/内存/线程/GC 一体
```

操作步骤：

1. 启动 `jvisualvm`（JDK bin 目录自带；Oracle JDK 9+ 需独立下载）。
2. 左侧进程列表双击目标进程。
3. 标签页：
   - **监视（Monitor）**：堆/Metaspace/Classes/Threads 曲线
   - **线程（Threads）**：线程时间线、死锁检测按钮
   - **抽样器（Sampler）**：CPU/Memory Profiler（看方法耗时、分配热点）
   - **Visual GC**：各代实时大小

### 5.7.2 MAT（Eclipse Memory Analyzer，适合大 dump 深度分析）

```
场景：离线分析堆转储，定位泄漏
优势：速度快、支持几十 GB dump、Leak Suspects 自动分析
```

必用功能：

```
1. Leak Suspects Report
   → 打开 dump 后直接跑，自动给出疑似泄漏点和对象链。

2. Histogram → 按 Retained Heap 排序
   Retained Heap：该类所有对象 + 它们持有的对象，总和
   → 找出"谁占内存最大"。

3. Dominator Tree
   → 按"如果移除这个对象能回收多少内存"排序。
   → 顶行就是泄漏点的最大嫌疑人。

4. Path to GC Roots（右键对象 → 该选项）
   → 从对象一路向上引用，追到根（Thread/Static/ClassLoader）。
   → 核心就是看"为什么没被 GC"。

5. Compare Two Dumps
   → 两个时间点的 dump 做对比。
   → 泄漏类的实例数会显著增长。
```

**MAT 分析实战思路**：

```
步骤 A：看 Leak Suspects Report，看 MAT 自动给出的结论。
         → 80% 情况这里能直接定位。

步骤 B：如果结论模糊，打开 Histogram。
         → 找 20% 业务类（非 JDK）占了 80% Retained。
         → 右键 Path to GC Roots。

步骤 C：如果是集合类（ArrayList/HashMap）排在前面，
         → 不是集合自己问题，是集合里的元素。
         → 用 "immediate dominators" 看是谁持有这个集合。

步骤 D：对比两次以上 dump 的 Histogram 增量。
         → 泄漏类的实例数是稳定增长的。
```

---

## 5.8 Arthas：线上神器

Arthas 是阿里巴巴开源的 Java 诊断工具，无需重启应用。

### 5.8.1 OOM 排查常用命令

```bash
# 启动
curl -O https://arthas.aliyun.com/arthas-boot.jar
java -jar arthas-boot.jar
# 按数字选择进程

# 1. Dashboard（总览：堆/GC/线程/CPU）
dashboard -n 5       # 打印 5 次后退出

# 2. 内存直方图（等价 jmap -histo，轻量）
memory

# 3. 类加载详情
classloader

# 4. 找 Top N 热点对象（实时采样，不 dump，线上可用）
heapdump --live /tmp/live.hprof

# 5. 找某对象的分配堆栈（神器，不用大 dump 就能找泄漏点）
#    先启动 profiler
profiler start --event alloc
#    运行 5-10 分钟
profiler stop --file /tmp/alloc.html
#    打开 alloc.html，看火焰图，找内存分配最多的代码路径

# 6. 线程相关
thread                  # 概览 + Top N 耗 CPU 线程
thread -b               # 找 BLOCKED 的线程（死锁定位）
thread -n 3             # Top3 占用 CPU 的线程，直接打印栈

# 7. 监控某方法
monitor -c 10 com.xxx.OrderService createOrder  # 每 10 秒统计调用量/失败率

# 8. 观察入参出参
watch com.xxx.OrderService createOrder "{params, returnObj, throwExp}" -n 3
```

### 5.8.2 profiler 火焰图定位泄漏（杀手级功能）

```
场景：线上堆一直在涨，但不能 dump（dump 会 STW，且 dump 文件巨大）。
做法：
  1. profiler start --event alloc
  2. 等 10 分钟
  3. profiler stop --file alloc.html
     → 火焰图里 x 轴=分配量，y 轴=调用栈
     → 找到底部最宽的代码路径，就是"分配了最多内存的方法"
     → 再看该方法是否有不合理的集合累积/大对象
```

---

# 六、真实案例实战

## 6.1 案例一：订单服务 heap space 溢出

### 场景

电商大促，订单服务实例不断重启，报错：

```
java.lang.OutOfMemoryError: Java heap space
Dumping heap to /var/log/dumps/java_pid12345.hprof ...
Heap dump file created [16344432008 bytes in 182.4 secs]
```

`-Xmx8g`，Dump 16G？不对，Dump 其实是堆大小的倍数（因对象头和对齐差异）。

### 排查步骤

```
Step 1：现场保护
         摘除实例流量，没重启。

Step 2：抓 GC Log → jstat -gcutil 12345 1000
         O   =  95% → 94% → 96% → 93% → 97%
         FGC =  120 且 FGCT 增加很快
         → 每次 Full GC 只能收回 2-3% 的内存 = 严重泄漏

Step 3：抓 Histogram → jmap -histo:live 12345 | head -20
         #instances  class
         3200000    com.xxx.entity.Order    ← 320w 订单对象，不正常
         8000000    com.xxx.entity.OrderItem  ← 订单明细 800w
         （通常订单不会驻留内存，应是 DB 查询完就释放）

Step 4：Path to GC Roots（MAT 分析）
         Order 的 dominator 是 HashMap @ 0x12345678
         HashMap 是 com.xxx.cache.OrderCache#cache 静态字段
         → 代码有一个 static Map<Long, Order> cache，只 put 没 remove！

Step 5：看代码
         OrderCache.put(order.getId(), order);
         // 但是没有过期策略，也没有 remove
         → 典型静态缓存泄漏

Step 6：修复
         a. 改成本地缓存框架（Caffeine）并设置 expireAfterWrite=10m
         b. 或者改成 Redis，不占堆
```

### 修复前后对比

```
修复前：Old Gen 从 30% 涨到 95% 只用了 2 小时
修复后：Old Gen 稳定在 40%-60% 之间波动
```

### 经验教训

> 永远不要手写 `static HashMap` 做缓存。用 Caffeine/Guava Cache，有 TTL、有最大容量。

---

## 6.2 案例二：Metaspace 溢出（反射类加载泄漏）

### 场景

服务运行 1 周就挂：

```
java.lang.OutOfMemoryError: Metaspace
```

### 排查步骤

```
Step 1：启动参数核查
        -XX:MaxMetaspaceSize=256m（默认是无限，这里被设置了 256m）

Step 2：jcmd <pid> GC.class_stats
        类数量：65,000，其中 40,000 个类是：
          com.xxx.dto.OrderDTO$$EnhancerByCGLIB$$abcdef123
          com.xxx.dto.OrderDTO$$EnhancerByCGLIB$$abcdef124
          ...
        → 每个类名末尾哈希不一样，说明是每创建一次就新生成一个类

Step 3：看代码
        for (each request) {
            Enhancer enhancer = new Enhancer();
            enhancer.setSuperclass(clazz);
            enhancer.setCallback(...);
            enhancer.create();  // 每次请求都动态生成新的代理类！
        }
        enhancer.setUseCache(true);  // 默认应该是 true，但这里误设为 false 了

Step 4：jmap -clstats
        加载器：sun.misc.Launcher$AppClassLoader 下 3w+ 个类
        通常正常业务 ClassLoader 加载的类数是几千，3w+ 异常

Step 5：修复
        a. 将 CGLib 改为 ByteBuddy 并使用 TypeCache（强缓存）
        b. 或者使用 Spring AOP（单例时只会生成一次代理）
        c. MetaspaceSize 适当调大（但这是辅助，根因还是代码）
```

---

## 6.3 案例三：Direct Buffer 溢出（Netty 内存泄漏）

### 场景

API 网关偶尔 OOM，堆栈里有 Netty 调用：

```
java.lang.OutOfMemoryError: Direct buffer memory
    at java.nio.Bits.reserveMemory(Bits.java:694)
    at java.nio.DirectByteBuffer.<init>(DirectByteBuffer.java:123)
    at java.nio.ByteBuffer.allocateDirect(ByteBuffer.java:311)
    at io.netty.buffer.UnpooledByteBufAllocator.newDirectBuffer(...)
```

### 排查步骤

```
Step 1：参数检查
        -XX:MaxDirectMemorySize=1g
        -Xmx6g（总给够了但堆外只有 1g）

Step 2：用 Arthas profiler 查分配
        profiler start --event alloc
        # 运行一会儿后发现分配最多的：
        #   io.netty.buffer.UnpooledByteBufAllocator.newDirectBuffer
        #   调用栈都是 io.netty.handler... 解码相关

Step 3：打开 Netty 泄漏检测（生产慎用，先在预发）
        -Dio.netty.leakDetection.level=paranoid
        日志出现：
        LEAK: ByteBuf.release() was not called before it's garbage-collected.
        Recent access records: ...
          at com.xxx.filter.AuthFilter.filter(AuthFilter.java:120)

Step 4：看 AuthFilter
        ByteBuf buf = ...;
        try {
            byte[] bytes = new byte[buf.readableBytes()];
            buf.readBytes(bytes);   // 拿到了字节
            // 但没 buf.release() !
        } finally {
            // buf.release();   ← 缺了这一行！
        }

Step 5：修复 + 参数调优
        a. finally 中 release
        b. 升级 Netty 4.1.100+（修复了几个内部泄漏）
        c. DirectMemorySize 加到 2g（堆外 25% 左右合理）
```

---

## 6.4 案例四：GC overhead limit exceeded

### 场景

下午 3 点 CPU 打满，服务基本不可用，日志：

```
java.lang.OutOfMemoryError: GC overhead limit exceeded
```

### 排查步骤

```
Step 1：jstat -gcutil <pid> 1000
        S0  S1   E     O     M    YGC   YGCT  FGC  FGCT
        0   99  99    98.5  92   1244  123.4 112  445.2

        1 秒打印一行，YGC 秒涨 10 次，FGCT 每秒 +200ms
        → 98% 时间在 GC，回收极少

Step 2：jstack 看应用线程
        大多数应用线程 BLOCKED 在
        ConcurrentHashMap.computeIfAbsent
        锁对象是同一个：<0xdeadbeef>

Step 3：看业务场景
        下午 3 点是"报表导出"任务，Map 做报表缓存：
        Map<String, Report> cache = new ConcurrentHashMap<>();
        for (String user : allUsers) {  // allUsers = 80w
            cache.computeIfAbsent(user, this::computeReport);
        }
        每次 computeReport 生成 100KB，80w 用户 → 80GB？不，内存不够就 OOM

Step 4：定位
        computeReport 生成大量对象，老年代很快满，
        Full GC 也只能回收到死对象（每次 computeReport 的临时对象）
        → 回收比例 < 2% → GC overhead limit exceeded

Step 5：修复
        a. 分批处理 + 每批清理引用
        b. 改分页/流式，不一次加载 80w
        c. 缓存改为本地缓存 + 大小限制
```

---

## 6.5 案例五：native thread 无法创建

### 场景

半夜报警，服务报错：

```
java.lang.OutOfMemoryError: unable to create new native thread
```

### 排查步骤

```
Step 1：检查当前线程数
        cat /proc/<pid>/status | grep Threads
        Threads:  8192   ← 接近系统上限

Step 2：线程 dump
        jstack <pid> | grep '^"' | wc -l
        8191 个线程，其中 8000+ 个：
        "pool-xxx-thread-yyyy"
        → 大量线程池！

Step 3：查线程池配置
        代码里有 17 处：
        ExecutorService pool = Executors.newFixedThreadPool(500);
        new ThreadPoolExecutor(500, Integer.MAX_VALUE, ...)
        → 以为 500 核心够了，但高峰期 17 个池 × 500 = 8500

Step 4：系统限制
        ulimit -u  →  10240（用户进程数上限）
        8192 + 别的进程 ~= 10240
        → 线程数 + 其他进程数 超过 ulimit

Step 5：修复
        a. 所有线程池统一走配置中心，核心线程数按实际需要定（通常 CPU 核数几倍）
        b. 加一个全局线程池监控（线程数>阈值告警）
        c. ulimit -u 调到 65535（谨慎，线程太多其实有问题）
```

---

## 6.6 案例六：G1 Evacuation Pause 导致服务不可用

### 场景

G1 垃圾回收器，服务 30 分钟一次 STW，每次 3-8 秒，K8s 探针失败被重启。

### 排查步骤

```
Step 1：GC Log（-XX:+PrintGCDetails）
        关键错误：
        [GC pause (G1 Evacuation Pause) (young) (to-space exhausted), 3.214s]
        → to-space exhausted：Survivor 在复制时，没有 Region 可放

Step 2：看 Region 使用情况（GC Log 详细）
        Eden Regions  2048/2048 满
        Survivor Regions  64/64 满
        Old Regions  1800/2048 接近满
        → 整体堆太满了，G1 腾挪空间不够

Step 3：看对象年龄分布
        很多对象年龄直接达到 MaxTenuringThreshold（默认 15）就晋升
        → 但 Old 也满，晋升失败

Step 4：根因
        a. 堆设置太小：-Xmx4g，业务量增长了 2 倍
        b. XX:MaxGCPauseMillis=200 目标设得太低，G1 反而频繁停顿
        c. Mixed GC 迟迟不触发，因为 IHOP（InitiatingHeapOccupancyPercent）默认 45 过高

Step 5：修复参数
        -Xmx6g -Xms6g
        -XX:MaxGCPauseMillis=200 （保持，但 Xmx 加大）
        -XX:InitiatingHeapOccupancyPercent=35 （提前触发 Mixed GC）
        -XX:G1MixedGCLiveThresholdPercent=65
        -XX:G1HeapWastePercent=5

结果：Evacuation Failure 基本消失，Young GC P99<150ms
```

---

# 七、常见 OOM 场景与解决方案

## 7.1 内存泄漏场景

### 定义

对象本应被回收，但因为有"意外的强引用"导致没被回收 → 老年代堆持续上升 → Full GC 无法回落 → OOM。

### 泄漏判断标准

```bash
# 用 jstat 连续观察 1 小时，每 10 秒采样：
jstat -gcutil <pid> 10000
# 如果 Old（O 列）每次 Full GC 后：
#   baseline 越来越高（每次比前一次更高）
#   → 泄漏
```

### 常见泄漏根因 Top 5

| # | 根因 | 代码特征 | 修复 |
|---|------|----------|------|
| 1 | **static 集合** | `static List/Map` 只加不删 | 用 Caffeine/Guava，加容量和 TTL |
| 2 | **ThreadLocal** | 线程池复用，ThreadLocal 没 remove | try/finally 里 remove |
| 3 | **监听器/回调未注销** | registerXxxListener 后未 unregister | 弱引用 / 生命周期钩子注销 |
| 4 | **ClassLoader 泄漏** | 动态生成类、热部署 | 确保 ClassLoader 无强引用 |
| 5 | **缓存框架误用** | 本地缓存无限大 / Redis 序列化堆积 | 加最大容量 + 淘汰策略 |

---

## 7.2 大对象场景

### 典型

```java
// 一次从 DB 全表查出 100w 条记录
List<Order> orders = orderMapper.selectList(new QueryWrapper<>());
// orders.size() = 1_000_000

// 或一次分配超大数组
byte[] buf = new byte[Integer.MAX_VALUE - 2];
```

### 定位

- MAT 的 **Top Consumers** 直接列出最大对象。
- Arthas 的 `profiler start --event alloc` 火焰图看分配最多的地方。
- 启动参数 `-XX:+HeapDumpOnOutOfMemoryError` 生成的 dump 中看最大对象。

### 解决

1. **分页/流式**：MyBatis `ResultHandler` / `fetchSize`，JPA Stream。
2. **DB 聚合**：sum/count 尽量在 DB 层做，不要把数据拉到内存再算。
3. **批处理**：每次处理 1000 条，循环完释放引用。

---

## 7.3 缓存不当场景

### 错误

```java
// 1. 无界缓存
private static final Map<Long, Order> CACHE = new HashMap<>();  // 只 put 不清理

// 2. SoftReference 当无限缓存
// SoftReference 内存不足时会回收，但短时间内大量分配还是 OOM
```

### 正确

```java
// 用 Caffeine 最稳妥
LoadingCache<Long, Order> cache = Caffeine.newBuilder()
        .maximumSize(10_000)                  // 最多 1w 条
        .expireAfterWrite(30, TimeUnit.MINUTES) // 写入 30 分钟失效
        .expireAfterAccess(10, TimeUnit.MINUTES)// 访问后 10 分钟刷新
        .recordStats()                         // 记录命中率
        .removalListener((k, v, cause) -> log.info("removed:{}", k))
        .build(k -> queryFromDB(k));
```

---

## 7.4 集合类未释放场景

### 典型陷阱

```java
public List<String> handle() {
    List<String> all = new ArrayList<>();
    while (hasMore()) {
        List<String> batch = fetchBatch();
        all.addAll(batch);           // all 越来越大，不释放
    }
    return all;
}
```

### 修复

```java
// 方案 1：边处理边写 DB/文件，不驻留内存
while (hasMore()) {
    List<String> batch = fetchBatch();
    writeToFile(batch);
}
```

---

## 7.5 ThreadLocal 泄漏场景

### 错误

```java
private static final ThreadLocal<User> USER_TL = new ThreadLocal<>();

public void doFilter() {
    USER_TL.set(currentUser);
    try {
        chain.doFilter();
    } finally {
        // USER_TL.remove();  ← 缺了！
    }
}
```

### 为什么会泄漏？

```
线程池中的 Thread 会长期存在（比如存活 1 小时）
Thread → ThreadLocalMap (key=ThreadLocal, value=User)
key 是弱引用，value 是强引用
如果 ThreadLocal 本身没被回收，value 就一直被引用 → 泄漏
```

### 修复

```java
finally {
    USER_TL.remove();  // 必须 remove！
}

// 进一步：用 TransmittableThreadLocal（阿里 TTL）做父子线程传递
```

### 面试题延伸

> 为什么 ThreadLocalMap 的 key 是弱引用但 value 不是？
> 如果 key 是强引用 → ThreadLocal 实例永远无法被回收。
> 如果 value 也是弱引用 → 你 set 进去的 value 可能下一秒就没了。
> 所以 key 弱（防泄漏 ThreadLocal 类本身）、value 强（保证你还能取到值），**同时你必须手动 remove()**。

---

## 7.6 类加载器泄漏场景

### 典型

Spring Boot DevTools 热部署、Tomcat 应用 reload、OSGi 动态 bundle、动态代理重复生成。

```
旧 ClassLoader
   ├ MyClass@1
   └ MyClass$ByteBuddyProxy@1  ← 被某个静态引用持有 → 整个 ClassLoader 无法卸载
```

### 排查

MAT 里用 **ClassLoader Explorer**，对同一个 AppClassLoader 如果出现多份实例（每 reload 一份），就是泄漏。

### 修复

1. 确保所有自定义 ClassLoader 生命周期结束时，被引用类**无强引用**。
2. Tomcat：`-XX:+TraceClassUnloading` 看类是否真的卸载。
3. DevTools：生产环境必须关掉。

---

## 7.7 Netty / NIO Direct Buffer 泄漏

### 泄漏模式

ByteBuf 创建后 `release()` 调用路径没覆盖（异常分支、解码失败分支）。

### 诊断

```bash
# 1. 开发/预发环境打开泄漏检测
-Dio.netty.leakDetection.level=paranoid    # 性能损失大，只在测试环境
-Dio.netty.leakDetection.level=advanced    # 推荐预发
-Dio.netty.leakDetection.level=simple      # 生产可用（采样）

# 2. 监控 Direct Memory 使用（JMX / Arthas memory 命令）
#    注意：DirectMemory 用 JMX 的 BufferPoolMXBean 查看
#    java.nio:type=BufferPool,name=direct → Used
```

### 修复原则

1. 谁创建 ByteBuf，谁负责 release。
2. 入站 handler：`SimpleChannelInboundHandler` 会自动 release，不要手动再调。
3. 出站 handler：调用 writeAndFlush 后由 Netty 负责。
4. `try { ... } finally { buf.release(); }` 兜底。

---

# 八、JVM 参数调优建议

## 8.1 堆参数

| 参数 | 含义 | 推荐值（经验） | 备注 |
|------|------|----------------|------|
| `-Xms` | 初始堆 | = `-Xmx`（生产必相等） | 避免扩缩容触发 Full GC |
| `-Xmx` | 最大堆 | 物理内存 50%-75% | 留 OS、Direct、Metaspace |
| `-Xmn` | 年轻代大小 | 堆的 30%-40% | 或用 `-XX:NewRatio` |
| `-XX:NewRatio` | Old:Young 比例 | 2（Old=2，Young=1）| CMS 常用 |
| `-XX:SurvivorRatio` | Eden:S0:S1 | 8 | G1 下通常不设 |
| `-XX:MaxTenuringThreshold` | 晋升年龄阈值 | 15（默认） | CMS 调 6-10 |

```bash
# 示例：8 核 16G 机器，典型 Web 应用
-Xms8g -Xmx8g \
-Xmn3g \
-XX:SurvivorRatio=6 \
```

---

## 8.2 GC 相关参数

### 8.2.1 G1（JDK 9+ 默认，推荐 8G+ 大堆）

```bash
-XX:+UseG1GC \
-XX:MaxGCPauseMillis=200 \             # 目标停顿 ms，默认 200
-XX:G1HeapRegionSize=16m \              # Region 大小（1-32M，自动也可）
-XX:InitiatingHeapOccupancyPercent=45 \ # IHOP，触发并发标记的堆占比
-XX:G1MixedGCLiveThresholdPercent=85 \  # Old Region 存活<85% 才被回收
-XX:G1HeapWastePercent=5 \              # 允许浪费 5% 的 Region
-XX:G1MixedGCCountTarget=8 \            # 8 次 Mixed GC 回收老年代
```

### 8.2.2 CMS（JDK 8 中低版本）

```bash
-XX:+UseConcMarkSweepGC \
-XX:+CMSParallelRemarkEnabled \
-XX:+UseCMSCompactAtFullCollection \
-XX:CMSFullGCsBeforeCompaction=5 \      # 5 次 Full GC 后做压缩
-XX:+CMSScavengeBeforeRemark \
-XX:CMSInitiatingOccupancyFraction=70 \
-XX:+UseCMSInitiatingOccupancyOnly
```

### 8.2.3 ZGC / Shenandoah（亚毫秒级停顿，JDK 11+）

```bash
# ZGC（JDK 15+ 生产可用）
-XX:+UseZGC \
-XX:MaxGCPauseMillis=10 \
-XX:ZAllocationSpikeTolerance=2
```

---

## 8.3 Metaspace 参数

```bash
-XX:MetaspaceSize=256m \                 # 首次达到就触发并发类卸载
-XX:MaxMetaspaceSize=512m \              # 设上限防本地内存耗尽
-XX:+UseCompressedClassPointers \
-XX:CompressedClassSpaceSize=256m
```

> **注意**：`MetaspaceSize` 是"首次触发类卸载 GC 的阈值"，不是初始大小；不设 `MaxMetaspaceSize` 理论上可以吃满所有本地内存。

---

## 8.4 OOM 现场保护参数

```bash
# ⭐ 最重要：OOM 时自动 dump
-XX:+HeapDumpOnOutOfMemoryError \
-XX:HeapDumpPath=/var/log/dumps/app.hprof \

# 同时生成错误日志文件
-XX:ErrorFile=/var/log/dumps/hs_err_%p.log \

# OOM 后退出（K8s 会自动重启）
-XX:+ExitOnOutOfMemoryError \
# 或者：OOM 后执行脚本（发短信、钉钉通知、重启脚本）
-XX:OnOutOfMemoryError="/opt/oom_handler.sh %p"
```

---

## 8.5 生产环境推荐参数

```bash
# JDK 8 稳定版 + G1
export JAVA_OPTS="
-server \
-Xms8g -Xmx8g \
-XX:+UseG1GC \
-XX:MaxGCPauseMillis=200 \
-XX:InitiatingHeapOccupancyPercent=40 \
-XX:+ParallelRefProcEnabled \
-XX:MetaspaceSize=256m \
-XX:MaxMetaspaceSize=512m \
-XX:MaxDirectMemorySize=2g \
-XX:+HeapDumpOnOutOfMemoryError \
-XX:HeapDumpPath=/var/log/dumps/ \
-XX:+ExitOnOutOfMemoryError \
-XX:+PrintGCDetails \
-XX:+PrintGCDateStamps \
-XX:+PrintGCApplicationStoppedTime \
-XX:+PrintPromotionFailure \
-Xloggc:/var/log/gc.log \
-XX:+UseGCLogFileRotation \
-XX:NumberOfGCLogFiles=10 \
-XX:GCLogFileSize=100M \
-XX:-OmitStackTraceInFastThrow \
-Dfile.encoding=UTF-8 \
-Duser.timezone=Asia/Shanghai \
"

# JDK 11+（日志参数语法变了）
export JAVA_OPTS="
-server \
-Xms8g -Xmx8g \
-XX:+UseG1GC \
-XX:MaxGCPauseMillis=200 \
-XX:MetaspaceSize=256m \
-XX:MaxMetaspaceSize=512m \
-XX:MaxDirectMemorySize=2g \
-XX:+HeapDumpOnOutOfMemoryError \
-XX:HeapDumpPath=/var/log/dumps/ \
-XX:+ExitOnOutOfMemoryError \
-Xlog:gc*=debug,gc+age=debug,safepoint=info:file=/var/log/gc.log:utctime,level,tags:filecount=10,filesize=100m \
-XX:-OmitStackTraceInFastThrow \
-Dfile.encoding=UTF-8 \
"
```

---

# 九、面试高频题

## 9.1 原理篇

### Q1：你知道哪几种 OutOfMemoryError？分别对应哪些内存区域？

**答**：JVM 常见 8 种 OOM：

| OOM Message | 对应区域 | 原因 |
|-------------|----------|------|
| Java heap space | Heap | 对象多、泄漏、堆太小 |
| GC overhead limit exceeded | Heap | 98% 时间做 GC，回收 < 2% |
| Metaspace | Metaspace（本地内存） | 类太多，ClasssLoader 泄漏 |
| Compressed class space | Metaspace 子区域 | Klass 指针压缩区满 |
| Direct buffer memory | Direct Memory（堆外） | Netty/NIO ByteBuf 没释放 |
| unable to create new native thread | OS 层 | 线程数达系统上限 |
| Requested array size exceeds VM limit | Heap（分配前检查）| 数组 size ≥ Integer.MAX_VALUE |
| Native allocation failed | 本地内存 / OS | C++ 层 malloc 失败 |

补充：`StackOverflowError` 是单线程栈深度过大，不属于 OutOfMemoryError 家族，但在面试中常被并列提问。

---

### Q2：说一下 JVM 内存模型（运行时数据区），每个区域的作用？哪些会发生 OOM？

**答**：

```
1. Heap（堆）：
   - 存放对象实例和数组（几乎所有对象）
   - 所有线程共享
   - GC 主战场
   - 可调 -Xms/-Xmx
   - 会 OOM：Java heap space

2. Metaspace（元空间，JDK8+）：
   - 存放类元数据、常量池、字段描述、方法描述、JIT 编译代码
   - 本地内存（不是堆）
   - 会 OOM：Metaspace / Compressed class space

3. JVM Stack（虚拟机栈）：
   - 每个线程私有，存栈帧（局部变量表、操作数栈、方法出口...）
   - 可调 -Xss（单线程栈大小）
   - 深度超 → StackOverflowError；线程数多 → unable to create thread

4. Native Method Stack（本地方法栈）：
   - 类似 JVM Stack，服务于 native 方法
   - 一般 JVM 实现中合并在一起

5. Program Counter Register（程序计数器）：
   - 存当前线程执行到的字节码行号
   - 唯一不会 OOM 的区域（它只是个计数寄存器级别）

6. Direct Memory（直接内存）：
   - 不属于运行时数据区，但常被忽略
   - NIO ByteBuffer.allocateDirect / Unsafe
   - 会 OOM：Direct buffer memory
```

---

### Q3：什么是内存泄漏？和内存溢出有什么区别？

**答**：

- **内存泄漏（Memory Leak）**：对象本应被回收但被意外引用，GC 回收不了。**它是一种状态**，是"慢性 OOM"。
- **内存溢出（OutOfMemoryError）**：经过 GC 后确实没有足够空间分配新对象。**它是一个结果/异常**。

关系：

```
泄漏 → 老年代堆逐渐上涨 → Full GC 后 baseline 上升 → ... → 某天装不下了 → OOM
```

**如何判断是否泄漏**：做几次 Full GC 后看老年代基线。基线持续上升就是泄漏；基线稳定就不是泄漏，是瞬时大对象或堆太小。

---

### Q4：GC overhead limit exceeded 和 Java heap space 有什么区别？实际工作中怎么看？

**答**：

| 维度 | Java heap space | GC overhead limit exceeded |
|------|-----------------|----------------------------|
| 触发条件 | 真的分配失败（即使 GC 全部可用空间也不够） | GC 时间 >98%，回收 <2%，连续 5 次 |
| 严重程度 | 更严重 | 还能回收"一点点"，但效率太低被 JVM 主动拒绝 |
| 典型根因 | 内存泄漏末期 / 单超大对象 | 泄漏中期 / 小对象太多 / 缓存命中率低 |
| Full GC 表现 | 100% 后抛 | 做了非常多 Full GC，每次只回收 1-2% |
| 如何快速判断 | OOM 前后 GC 次数正常或少 | OOM 前 FGC 疯狂增加，FGCT 飙升 |

**实战口诀**：看到 OOM 先看是哪种。
- `heap space` + dump 里超大对象 → 大对象问题。
- `heap space` + Old 持续上涨 → 泄漏。
- `GC overhead` + FGC 特别多 → 中期泄漏/小对象泛滥。

---

### Q5：为什么会发生 Metaspace OOM？怎么排查？

**答**：

**原因**：

1. 动态生成类（CGLib/ByteBuddy）没缓存，每次都生成新的（最常见）。
2. ClassLoader 泄漏（Tomcat reload、热部署）。
3. JSP 太多 / 一次首次访问大量 JSP。
4. `MaxMetaspaceSize` 设置太小。

**排查**：

```bash
# 1. 看类数量是否异常
jcmd <pid> GC.class_stats
jmap -clstats <pid>

# 2. 观察类加载次数和卸载次数
jstat -class <pid> 1000
# Loaded Bytes  Unloaded Bytes     Time
# 如果 Unloaded 是 0，但 Loaded 一直涨 → 类泄漏

# 3. 加类卸载日志
-XX:+TraceClassUnloading -XX:+TraceClassLoading

# 4. MAT ClassLoader Explorer：
#    看同一个 ClassLoader 是否有 N 份实例
```

---

## 9.2 定位实战篇

### Q6：线上出现 OOM，你第一时间做什么？请描述完整的排查流程。

**答**：（面试必考！按照文档"五步定位法"答）

**第一步：现场保留，不要重启！**
- 从网关摘掉该实例（切流量 / OutOfService）。
- `jps` 确认 pid，`top`/`df` 看 CPU 和磁盘空间。

**第二步：抓现场数据**
- 间隔 10 秒以上抓两次堆转储：`jmap -dump:live,format=b,file=/tmp/heap_XX.hprof <pid>`。
- 抓至少 3 次线程 dump：`jstack <pid> > tX.txt`。
- GC 观察：`jstat -gcutil <pid> 1000 30` → 记录 GC 规律。
- 同时把 GC 日志文件保存下来。

**第三步：核查参数**
- `jinfo -flags <pid>`、`jinfo -sysprops <pid>`，看 `-Xmx`、`MaxMetaspaceSize`、`UseG1GC` 等。

**第四步：根因分析**
- 看 OOM 异常栈 message 判定类型（heap / metaspace / direct ...）。
- heap：MAT 分析 → Leak Suspects → Histogram → Dominator Tree → Path to GC Roots。
- metaspace：看类数、看动态代理类数量、看 ClassLoader 实例数。
- direct：检查 `-Dio.netty.leakDetection`、Netty release。
- GC overhead：看 Old Gen baseline 是否持续上升 → 泄漏。

**第五步：修复 + 验证**
- 先改代码（泄漏点修复）、再调参数（不要先调参数掩盖问题）。
- 压测验证：同模型压测 >1 小时，看 Heap/Metaspace 曲线。
- 灰度：先上一台，观察泄漏周期。
- 加固：加监控告警（Heap>80%、FullGC>3 次/小时、Class 数陡增）。

---

### Q7：堆转储文件很大（几十 G），打开 MAT 分析很慢，有什么技巧？

**答**：

1. **给 MAT 足够内存**：
   ```bash
   # MemoryAnalyzer.ini
   -Xmx32g       # 至少 dump 大小 1.5 倍
   -XX:-UseG1GC  # 大内存分析 G1 可能有问题，用 Parallel GC 更稳
   ```
2. **先做类直方图，不急着全量解析**：
   ```bash
   # 先用 jmap -histo:live 快速看 top 类，不一定需要 dump
   jmap -histo:live <pid> | head -50
   ```
3. **使用 live dump**：
   `jmap -dump:live,...` 只保留存活对象，dump 小非常多。
4. **Compare 前只跑 Leak Suspects**：
   打开 dump 时选 "Leak Suspects Report"，MAT 会生成一份小报告，不构建全索引。
5. **用线上命令式分析替代**：
   Arthas `profiler start --event alloc` 采样分配火焰图，不用 dump 也能定位热点分配代码。
6. **在服务器端用 jhat/GCViewer 做初筛**：
   服务器端跑一遍 jhat 直方图，下采样后再下载。

---

### Q8：如何区分内存泄漏和内存溢出（堆太小）？

**答**：关键看 **Full GC 后 Old Gen baseline 曲线**。

```bash
jstat -gcutil <pid> 10000 > gc.log
# 提取 O（Old 使用率列）
```

```
情形 1（不是泄漏，是堆小/瞬时大流量）：
时间    O%
t0      40%
t1      80%  ↑ 流量高峰
t2      41%  ↓ Full GC 后回到基线
t3      85%  ↑
t4      40%  ↓ Full GC 后仍回到基线
→ 基线稳定 40%，只是峰值逼近 Xmx

情形 2（泄漏！）：
时间    O%
t0      30%
t1      50%
t2      40%  ← Full GC 回落，但比 30% 高
t3      65%
t4      52%  ← Full GC 后 52%，更高
t5      78%
t6      68%  ← 越来越高
→ 基线阶梯式上升 = 泄漏
```

另外，对比前后 2 次 dump：
- 泄漏类在两次 dump 中实例数增长显著。
- 堆太小情形下：所有类按比例增长，没有"嫌疑类"。

---

### Q9：生产环境发生 OOM，但是没开 HeapDumpOnOutOfMemoryError，有什么补救办法？

**答**：

1. **别重启，现场抓**：
   ```bash
   # 进程还活着 → 立刻抓
   jmap -dump:live,format=b,file=heap_$(date +%Y%m%d_%H%M%S).hprof <pid>
   # 或者 jcmd（JDK 8+）
   jcmd <pid> GC.heap_dump heap.hprof
   ```
2. **进程快死了，dump 抓不动**：
   ```bash
   # 看 Histogram（快、轻量）
   jmap -histo:live <pid> | head -50 > histo_$(date +%s).txt
   # 或者 Arthas memory
   ```
3. **如果已经退出了**：
   - 找 hs_err_pid<pid>.log（JVM 崩溃自动生成），里面有类直方图快照。
   - 找 K8s/docker 的 core dump（需要 core_pattern 配置）。
4. **最后一招**：基于 GC 日志反推。
   - 如果是 Metaspace OOM → 回忆最近是否上线动态代理相关代码。
   - 如果是 Heap → 排查最近 1 天内上线的新缓存/集合累积逻辑。
5. **立刻加参数**，等下次复现：
   ```
   -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/var/log/dumps/
   ```

---

## 9.3 进阶调优篇

### Q10：大促前，如何做 OOM 预防？

**答**：

**1. 代码层面（最根本）**

```
□ 禁用 static Map 做缓存，统一用 Caffeine（带 maxSize + expireAfterWrite）
□ 所有 ThreadLocal 都有 remove() 在 finally
□ 监听器/回调注册 → 有对应的注销
□ 批量查询接口 → 分页/流式，避免全表一次 into memory
□ ResultSet/流 → 有 close()（try-with-resources）
□ Netty ByteBuf → finally release()
□ Executors.newFixedThreadPool 只建一次，不要每个请求 new 一个
```

**2. JVM 参数**

```
□ -Xms=-Xmx，防止扩缩容抖动
□ 设 -XX:MaxMetaspaceSize=512m 上限（避免本地内存无限吃）
□ 设 -XX:MaxDirectMemorySize=2g（框架默认值可能不够或太多）
□ 开 HeapDumpOnOutOfMemoryError + ExitOnOutOfMemoryError
□ 打印 GC 日志并做轮转
```

**3. 监控告警**

```
□ JVM 堆使用率 > 80% → 警告；> 90% → 严重
□ Full GC 次数 > 3 次/小时 → 警告
□ Metaspace 使用率 > 85% → 警告
□ 线程数 > 800 → 警告
□ Direct Memory 使用率 > 85% → 警告
□ 老年代使用率在 Full GC 后仍然 > 80% → 严重
```

**4. 压测**

```
□ 同模型 + 1.5 倍压 1 小时，监控 Heap/GC/线程曲线
□ 稳定性压测（模拟真实流量跑 24h），看内存是否上升
□ 关注 Heap after Full GC 曲线（判断泄漏）
```

---

### Q11：Direct Buffer Memory 如何监控和定位泄漏？

**答**：

**监控**：

```bash
# JMX 方式（生产最常用）
MBean: java.nio:type=BufferPool,name=direct
   - Count        # 分配的 ByteBuffer 个数
   - MemoryUsed   # 已使用字节数
   - TotalCapacity# 总容量

# Arthas 方式
memory         # 堆外使用会打印 NO_HEAP 的 used/max

# Prometheus + jmx_exporter
{
  "name": "jvm_buffer_memory_used_bytes",
  "type": "GAUGE",
  "labels": {"name": "direct"},
  "value": "MemoryUsed"
}
```

**定位**：

1. 打开 Netty 泄漏检测：`-Dio.netty.leakDetection.level=advanced`，日志会有栈。
2. Arthas profiler 分配事件：`profiler start --event alloc` 看 Direct ByteBuffer 的分配栈。
3. Java NMT（Native Memory Tracking）：
   ```bash
   # 启动加 -XX:NativeMemoryTracking=summary
   jcmd <pid> VM.native_memory summary
   # 看 Internal 项是否特别大
   ```

---

### Q12：Full GC 频繁但不是泄漏，有什么调优思路？

**答**：

| 方向 | 做法 |
|------|------|
| **升级年轻代** | `-Xmn` 加大，避免 Young 区装不下瞬时对象被过早晋升到 Old |
| **G1 IHOP 调小** | `-XX:InitiatingHeapOccupancyPercent=35`，更早触发并发标记 |
| **调大 Region** | `-XX:G1HeapRegionSize` 调大，Humongous 对象不再直接进 Old |
| **减少晋升** | `-XX:MaxTenuringThreshold=15` 调大，让对象在年轻代多熬几次 |
| **对象不要太老** | 本地缓存大时降低 maxSize / expire 时间，减少常驻对象 |
| **换更强的 GC** | 大堆 JDK11+ 尝试 ZGC/Shenandoah，停顿更短 |
| **检查 Humongous** | G1 超过 Region 一半的对象直接进 Old，日志找 "G1 Humongous Allocation" |

---

### Q13：ThreadLocal 为什么会导致内存泄漏？如何正确使用？

**答**：

**泄漏原因**：

```
线程池 Thread 长期存活（不会退出）
  ↓
Thread.threadLocals（ThreadLocalMap）不会被清
  ↓
ThreadLocalMap.Entry: key(Weak Reference<ThreadLocal>), value(Object)
  ↓
如果 ThreadLocal 被回收了，key.get() = null，Entry 的 key 变 null
  ↓
但是 value 还是强引用，而且 Thread 在 → ThreadLocalMap 在 → Entry 在 → value 在
  ↓
直到"下一次 ThreadLocal set/get/remove" 时，ThreadLocalMap 才会清理 stale entry
  ↓
如果线程复用后一直没再使用过 ThreadLocal，value 就泄漏了！
```

**正确使用**：

```java
private static final ThreadLocal<User> USER_HOLDER = new ThreadLocal<>();

public void doFilter(ServletRequest req) {
    try {
        USER_HOLDER.set(extractUser(req));
        chain.doFilter(req, res);
    } finally {
        USER_HOLDER.remove();  // ✅ 必须 remove！
    }
}
```

**更规范**：`static final` 修饰 ThreadLocal，避免重复创建 ThreadLocal 实例；父子线程传递时使用阿里的 `TransmittableThreadLocal`。

---

### Q14：JDK 7 String.intern() 放到哪了？JDK 8 呢？PermGen vs Metaspace

**答**：（经典面试题，考察 JVM 演进）

| 版本 | 字符串常量池位置 | 方法区实现 | OOM 类型 |
|------|------------------|------------|----------|
| JDK 6 | PermGen（堆内） | PermGen | `PermGen space` |
| JDK 7 | Heap | PermGen + 部分移到堆 | `PermGen space` / `Java heap space` |
| JDK 8+ | Heap | Metaspace（本地内存） | `Metaspace` / `Java heap space` |

影响：JDK 6 中大量 `intern()` 会撑爆 PermGen；JDK 8+ 中会占用 Heap。

---

### Q15：如何设计一个"线上 OOM 自动应急系统"？

**答**：（架构设计题，考察综合能力）

```
组件 1：数据采集（Prometheus + Grafana）
  - JVM Exporter：heap/memory/threads/gc/cpu
  - 每 15s 采样一次

组件 2：告警规则
  - Heap > 85% → 警告（抓 Histogram 快照）
  - Heap > 95% → 严重（抓堆转储 + 摘流量）
  - FullGC/hour > 5 → 警告
  - Metaspace > 85% → 警告

组件 3：自动化动作
  - 严重告警触发：
    1. 服务从注册中心摘除（Out of Service）
    2. jmap -dump:live 到共享存储
    3. jstack 3 次
    4. jstat 10 秒 × 30
    5. 堆转储上传 OSS + 记录工单
    6. （如果配置了）执行 K8s restart

组件 4：分析管道
  - dump > 10G → 上传后在分析服务器跑 MAT Leak Suspects
  - 自动生成"OOM 报告"：OOM 类型、Top 类、嫌疑路径、时间线
  - 推送到钉钉/企微 + 工单系统

组件 5：复盘闭环
  - 修复后必须有"压测报告"验证 Heap 稳定性
  - 复盘会输出行动项并跟踪完成
```

---

### Q16：G1 调优中常见的 Evacuation Failure 是什么？如何解决？

**答**：

Evacuation Failure（转移失败）发生在 G1 的 Young GC / Mixed GC 过程中：需要把存活对象从 Source Region 复制到 Target Region 时，**没有空闲 Region 可用**，只能退化为 Full GC（STW 严重）。

**常见原因 + 解决**：

1. **堆太小 / Region 太满**：加大 `-Xmx`。
2. **IHOP 太高**：Mixed GC 启动得太晚，Old 太满腾挪不开 → 降低 `-XX:InitiatingHeapOccupancyPercent` 至 35-40。
3. **对象晋升太猛**：加大 `-Xmn` 或调大 `MaxTenuringThreshold`，让对象多在 Young 待着。
4. **Humongous 太多**：超大对象直接 Old，占 Old 空间 → 调大 `-XX:G1HeapRegionSize` 让 50% 大小阈值变高，减少 Humongous。
5. **Mixed GC 回收力度不够**：调大 `-XX:G1MixedGCCountTarget` / 调小 `-XX:G1HeapWastePercent`。

---

### Q17：Kubernetes Docker 环境里 JVM OOM 容易踩哪些坑？

**答**：

```
坑 1：容器物理内存 ≠ JVM Xmx
  - 容器 limit=8g，Xmx=7g，看似合理
  - 但 JVM 实际使用 ≈ Xmx + Metaspace + Direct + ThreadStack + CodeCache ≈ 9g
  - 结果：超过 cgroup limit，被 OOM Killer 干掉！
    解决：
      - JDK 8u191+/JDK 10+ 加 UseContainerSupport（JDK 10 默认）
      - 容器 8G 时，Xmx 给 60%-70%（4.8g-5.6g），留 30% 给非堆

坑 2：CPU 数量被 cgroup 限制，默认 GC 线程数错
  - 容器 2 核，但宿主机 64 核，默认 ParallelGCThreads=64
  - 结果：GC 时大量线程争抢，性能差
    解决：
      - -XX:ParallelGCThreads=CPU_COUNT
      - -XX:ConcGCThreads=CPU_COUNT/4

坑 3：PID 1 进程问题
  - Java 是 PID 1 时，Kill/Heap Dump 有时不生效（SIGTERM 处理不一样）
    解决：用 tini 作为 PID 1

坑 4：容器被 OOMKilled 但 Java 内部没抛 OOM
  - 原因：Direct / Metaspace / Native 超了 cgroup
  - 表现：exit code 137，describe pod 看 Reason=OOMKilled
    解决：加 JVM NMT 追踪，合理分配 Xmx + 非堆
```

---

# 十、最佳实践与 checklist

## 10.1 上线前 OOM 防护 Checklist

```
代码审查
  □ 无 static Map/List 做无限缓存（替换为 Caffeine/Guava）
  □ ThreadLocal 全部有 try/finally 的 remove()
  □ Stream/ResultSet/IO 全部使用 try-with-resources
  □ 监听器/回调有对应的注销方法
  □ 批量查询接口有分页/流式，不能一次拉全表
  □ Netty ByteBuf/Buffer 有 finally release
  □ 线程池统一在容器启动时创建，有界队列

启动参数
  □ -Xms = -Xmx（推荐相等）
  □ -XX:+HeapDumpOnOutOfMemoryError 开启
  □ -XX:HeapDumpPath 指向可写且空间足够的目录
  □ -XX:+ExitOnOutOfMemoryError（K8s 环境推荐）
  □ -XX:MaxMetaspaceSize 设置上限
  □ -XX:MaxDirectMemorySize 设置上限
  □ GC 日志开启 + 文件轮转
  □ -XX:-OmitStackTraceInFastThrow（保留完整异常栈）

监控告警
  □ Heap 使用率告警（80%/90% 两档）
  □ Full GC 次数告警（>3 次/小时）
  □ Old Gen after Full GC 告警（基线趋势）
  □ Metaspace 使用率告警（>85%）
  □ Direct Memory 告警
  □ 线程总数告警
  □ Class 数量异常增长告警

压测
  □ 同模型 1.5x 流量压测 1 小时
  □ 稳定性压测 24 小时，关注 Heap 曲线
  □ 导出/报表等大接口做内存限制测试
```

---

## 10.2 常见 6 种 OOM 速查表

| OOM 类型 | 第一眼查什么 | 根因 Top 3 | 修复首选 |
|----------|--------------|------------|----------|
| Java heap space | Old Gen 是否趋势上升 → 泄漏；Histogram Top 类 | static 缓存、ThreadLocal、监听器泄漏 | 改 Caffeine / 加 remove |
| GC overhead limit | FGC 次数 + 回收比 | 中期泄漏、小对象泛滥、缓存命中率低 | 找泄漏；调大堆；改缓存策略 |
| Metaspace | 类总数 / 动态代理类数量 | 动态代理无缓存、热部署 | 加 TypeCache；关 DevTools |
| Direct buffer | BufferPool 监控、Netty leakDetection | ByteBuf 没 release | finally release；调 DirectSize |
| unable to create thread | `ps -eLf` 线程数；线程池配置 | 无限线程池、ulimit -u 低 | 统一线程池；调 ulimit |
| Array size exceeds limit | 异常栈的分配行 | 代码 bug（变量溢出、参数错） | 改代码，不是调参数 |

---

## 10.3 排查思路速记图

```
                        出现 OOM / 假死
                              │
                              ▼
                读异常 message → 判断 8 种类型中的哪一种
                              │
                   ┌──────────┼──────────┐
                   ▼          ▼          ▼
                Heap 类     Meta/Class   Direct/Thread
                   │          │          │
                   ▼          ▼          ▼
           jstat 看 GC    类数量是否↑   jstack 线程数
           Old 基线趋势   ClassLoader    arthas profiler
                   │          │          │
                   ▼          ▼          ▼
        基线上升？→泄漏   动态代理类多？  Netty release？
                   │          │          │
                   ▼          ▼          ▼
          MAT Leak Suspects   缓存复用    finally release
          Histogram Top 类   关 DevTools  调 DirectSize
          Path to GC Roots
                   │
                   ▼
          找到泄漏点 → 修复 → 压测 → 灰度
```

---

## 10.4 推荐资源

1. **《深入理解 Java 虚拟机（第 3 版）》** 周志明 - 第 2/3 章内存模型、第 5 章调优案例
2. **《Java 性能权威指南》** Scott Oaks - 第 5/6 章 GC 调优
3. **Eclipse MAT 官方文档** - Leak Suspects、Dominator Tree 教程
4. **Arthas 官方文档** - profiler、watch、thread 三个命令深度用法
5. **gceasy.io / fastthread.io** - 在线 GC Log / Thread Dump 可视化分析
6. **JDK Mission Control（JMC）+ JFR（Java Flight Recorder）** - 低开销事件追踪
7. **《Netty 官方内存泄漏文档》** - leakDetection 四级说明

---

## 10.5 实战项目案例汇总（面试背诵）

> 下面给一个"我在项目里遇到的 OOM"通用模板，按这个结构讲，面试官会觉得你真的做过：

```
项目背景：
  公司电商大促前夕，订单服务（JDK8 / G1 / -Xmx8g）测试环境稳定，
  但灰度 1 小时后实例不断重启，日志报 Java heap space。

排查过程：
  1. 线上实例没重启，先摘流量保留现场。
  2. jmap -dump:live 抓两次，间隔 20 秒，同时抓 3 次 jstack。
  3. jstat 观察到 Old Gen 从 30% 一路涨到 95%，Full GC 后基线也不断抬升 → 确认泄漏。
  4. MAT 分析：Histogram 发现 OrderDTO 实例 220 万个，远远超过正常值（正常几千）。
     Dominator Tree → 被一个 static ConcurrentHashMap 持有，来自自写的 OrderCache。
  5. 代码回溯：OrderCache 是一个同事手写的 static Map，只 put 没设置 expire/maxSize，
     本想做热点缓存，但实际演变为全量缓存。

修复：
  1. 把 static HashMap 改为 Caffeine LoadingCache。
     maximumSize=10_000，expireAfterWrite=15m。
  2. 压测环境同样流量跑 3 小时，Old Gen 稳定在 45-55%，不再增长。
  3. 灰度上线，观察 24h 无重启，OOM 告警清零。

加固：
  - 加了代码规范：禁止裸写 static 集合做缓存。
  - 加监控：Heap>80%、FullGC>3 次/小时告警。
  - 统一走 Caffeine 组件封装 CacheManager，防止再手写。
```

---

# 十一、OOM 应急响应 SOP

> **SOP（Standard Operating Procedure）**：线上 OOM 属于 **P0/P1 级事故**。按本章流程严格执行，既能第一时间止损，又能完整保留证据用于后续根因定位。**最关键的一条：不要一上来就重启进程，否则现场丢失只能等下次复现。**

---

## 11.1 应急响应总览：黄金 5 分钟

```
OOM 告警（监控报 Heap/FullGC/接口超时/重启）
          │
          ▼  0 ~ 30s  立即摘流
  Step 1：切断 Pod / VIP 流量，止损
          │
          ▼  30s ~ 3min  保留现场
  Step 2：任何破坏证据的动作都禁止（GC.run / 重启 / kill -9）
          │
          ▼  3min ~ 10min  抓证据
  Step 3：抓堆转储(×2) + 线程转储(×3) + GC快照 + 系统状态
          │
          ▼  10min ~ 30min  修复或恢复
  Step 4：
    ① 关键服务：回滚到上一版本或替换实例恢复业务
    ② 非关键：带现场继续分析（或重启单实例，保留dump）
          │
          ▼  场外分析（不影响业务）
  Step 5：分析环境准备（MAT调大内存）
  Step 6：Dump 深入分析 → 4 大技法
  Step 7：区分泄漏/膨胀 → 修复代码或参数 → 压测 → 灰度 → 复盘
```

**时间 SLA 要求**：

| 动作 | 时间要求 | 负责人 |
|------|----------|--------|
| 确认告警真实性 | 1 分钟 | 值班工程师 |
| 摘流止损 | 3 分钟内 | 值班工程师 |
| 现场证据抓完 | 10 分钟内 | 值班工程师 + 研发 |
| 业务恢复（非分析型） | 15 分钟内 | 值班 + SRE |
| 根因定位 | 2 小时内 | 主开发 + 架构 |
| 修复方案 + 压测通过 | 24 小时内 | 开发 |
| 复盘报告 | 3 个工作日内 | 事故 Owner |

---

## 11.2 第一步：立即摘流（秒级动作）（黄金原则：先保命，再取证）
  1. 立即摘流：若为关键服务，通过K8s Service摘除该Pod流量，或通过网关切走权重。
  2. 保留现场：禁止重启前执行任何jcmd <pid> GC.run（会清空强引用，丢失证据）。
  3. 提取Dump：
      ```
      # 若-XX:+HeapDumpOnOOM已生成，直接scp拉取；若无，手动触发：
      jcmd <pid> GC.heap_dump /tmp/manual-$(date +%s).hprof
      # 注意：jcmd方式比jmap更安全（不会强制FGC，但依然会STW）
      ```

   
### 11.2.1 Kubernetes 环境（最常用）

```bash
# === 方案 A：通过 Service 标签摘除 ===
# Pod 打 OOM 标签，Service selector 匹配不到，流量自然不再路由
kubectl label pod <pod-name> oom-incident=true --overwrite
# Service 的 selector 默认不含 oom-incident=true，此 Pod 自动被 Endpoints 移除

# 验证：看 endpoints 里该 Pod IP 是否已消失
kubectl get endpoints <svc-name> -o yaml | grep -E "ip:|<pod-name>"

# === 方案 B：通过 Nodeport/Ingress 降权重 ===
# 如果 Service 是 ClusterIP + Ingress Nginx，在 Ingress 注解降该实例为 0 权重
# 或更直接的：设置 Pod 为 NotReady 让 Endpoints Controller 摘除
kubectl patch pod <pod-name> --type=json \
  -p '[{"op":"add","path":"/status/conditions/-","value":{"type":"Ready","status":"False","reason":"OOMIncident","message":"摘除流量保留现场"}}]'

# === 方案 C：Deployment 直接替换单实例 ===
# 时间不等人时直接把有问题的 Pod kill（会自动重建），前提：dump 已经先抓完！
# kubectl delete pod <pod-name> --grace-period=0 --force
#  ⚠️ 只有在 dump 已经安全落盘后才能执行此操作！

# === 方案 D：Istio/VirtualService 流量路由（有服务网格时） ===
# subset 直接把该 Pod IP 踢出 destination 列表
```

### 11.2.2 Nginx / 网关 / F5 摘流

```bash
# Nginx（动态 upstream，动态摘除节点）
curl -X POST "http://<nginx-host>/upstream_conf" \
  -d "server=<pod-ip>:<port>&down=&upstream=myapp_upstream"

# Spring Cloud Gateway / Zuul：通过服务下线接口
curl -X POST "http://<pod-ip>:<port>/actuator/serviceregistry" \
     -H "Content-Type: application/json" \
     -d '{"status":"OUT_OF_SERVICE"}'

# Dubbo：通过 QOS 下线
telnet <pod-ip> 22222
offline
```

### 11.2.3 紧急 iptables（兜底）

```bash
# 若上述都不生效，最后的兜底：直接 DROP 入口请求
# 注意：22 端口要放通，否则自己也连不上
sudo iptables -I INPUT -p tcp --dport 8080 -j DROP   # 业务端口
sudo iptables -I INPUT -p tcp --dport 22   -j ACCEPT # 保留 SSH

# 事后恢复
sudo iptables -D INPUT -p tcp --dport 8080 -j DROP
```

---

## 11.3 第二步：保留现场（销毁证据的 7 个禁忌）

> 这是最容易犯错误的阶段。**现场一旦破坏，只能等下一次复现，而很多泄漏几个星期甚至几个月才复现一次。**

```
┌────────────────────────────────────────────────────────────────┐
│                     ❌ 绝对禁止的 7 个动作                      │
├────────────────────────────────────────────────────────────────┤
│  1.  ❌ 执行 jcmd <pid> GC.run / jmap -histo:live                │
│         都会触发 Full GC → 所有不可达/软引用被清 → dump 空了       │
│         泄漏的弱引用链条从此消失！                               │
│                                                                 │
│  2.  ❌ 直接重启 Java 进程 / kill -9 <pid>                      │
│         进程消失 → 线程栈/堆/元空间信息全部丢失                  │
│                                                                 │
│  3.  ❌ 重启机器 / 虚机                                         │
│         不仅丢失 JVM 现场，连 OS 的 dmesg / sar 记录也没了        │
│                                                                 │
│  4.  ❌ 在应用代码里手动调 System.gc() / Runtime.gc()            │
│         同上，破坏对象存活链                                     │
│                                                                 │
│  5.  ❌ 删除 / 覆盖 JVM 启动时生成的 dump/hs_err 日志            │
│                                                                 │
│  6.  ❌ 修改代码后热部署（Arthas redefine / Spring DevTools）    │
│         类加载器状态改变，类级引用关系变化                        │
│                                                                 │
│  7.  ❌ 连续 jmap dump 而不检查磁盘                              │
│         dump 写满磁盘 → 应用再崩溃时连新 dump 也生成不了          │
└────────────────────────────────────────────────────────────────┘
```

### 正确的现场保护操作 ✅

```bash
# 1. 先查磁盘（关键！8G dump 要至少 16G 空间）
df -h | grep -E "(tmp|var|data)"
# 若磁盘不够 → 挂新盘 / 挂载 NAS → 再 dump
mkdir -p /data/oom-dumps/$(date +%F_%H%M%S)_<podname>
chmod 777 /data/oom-dumps/...

# 2. 先保护日志
cp /var/log/app/*.log     /data/oom-dumps/.../logs/
cp /var/log/gc*.log       /data/oom-dumps/.../logs/
cp /var/log/dumps/*.hprof /data/oom-dumps/.../   2>/dev/null  # 已经自动 dump 的复制
cp hs_err_pid*.log       /data/oom-dumps/.../   2>/dev/null

# 3. 保护进程状态快照
ps -efL | grep java > /data/oom-dumps/.../ps_threads.txt
top -H -bn1 -p <pid>   > /data/oom-dumps/.../top_threads.txt
cat /proc/<pid>/status  > /data/oom-dumps/.../proc_status.txt
cat /proc/<pid>/maps    > /data/oom-dumps/.../proc_maps.txt
free -h                 > /data/oom-dumps/.../free.txt
vmstat 1 10             > /data/oom-dumps/.../vmstat.txt &
sar -n DEV 1 5          > /data/oom-dumps/.../sar_net.txt &
dmesg -T                > /data/oom-dumps/.../dmesg.txt  # 重要！看 OOM Killer

# 4. 如果是容器，别忘了保留容器级元数据
kubectl describe pod <pod-name>   > /data/oom-dumps/.../k8s_pod_desc.yaml
kubectl get pod <pod-name> -o yaml > /data/oom-dumps/.../k8s_pod.yaml
docker inspect <container-id>     > /data/oom-dumps/.../docker_inspect.json
```

---

## 11.4 第三步：现场快照抓取（Dump 提取）

### 11.4.1 抓取顺序与优先级

```
优先级：
  1. 线程 dump × 3（轻量、必抓，几乎不影响）
  2. jstat × N 次（观察 GC 趋势）
  3. jcmd GC.class_histogram（不用 Full GC，快但不准）
  4. jmap -dump 不带 live（完整 dump，含不可达对象，用于分析泄漏链条）
  5. jmap -dump:live（会做 Full GC，证据会变"干净"，作为对比 dump 放最后）
```

### 11.4.2 一键抓取脚本

把下面脚本保存到 **`/opt/oom-grab.sh`**，生产机器上直接 `./oom-grab.sh <pid>` 执行。

```bash
#!/bin/bash
# ============================================================
# OOM 现场一键抓取脚本
# Usage: ./oom-grab.sh <pid> [outdir]
# ============================================================
set -u

PID=$1
OUTDIR=${2:-/data/oom-dumps/$(date +%F_%H%M%S)_pid${PID}}

if ! kill -0 $PID 2>/dev/null; then
    echo "[ERROR] pid $PID not alive"
    exit 1
fi

mkdir -p "$OUTDIR/logs" "$OUTDIR/dumps" "$OUTDIR/sys"
echo "[INFO] output dir: $OUTDIR"
cd "$OUTDIR"

# ---------------- 0. 基础信息 ----------------
jps -lv > sys/jps.txt 2>&1
jinfo -flags "$PID"        > sys/jinfo_flags.txt 2>&1
jinfo -sysprops "$PID"     > sys/jinfo_sysprops.txt 2>&1
jcmd  "$PID" VM.version    > sys/vm_version.txt 2>&1
jcmd  "$PID" VM.system_properties > sys/sysprops_jcmd.txt 2>&1
date > sys/date.txt
echo "HOSTNAME=$(hostname)" > sys/hostname.txt

# ---------------- 1. 线程 dump x3（间隔 5s） ----------------
echo "[1/7] thread dumps x3 ..."
for i in 1 2 3; do
    jstack -l "$PID" > dumps/thread_$i.txt 2>&1
    sleep 5
done

# ---------------- 2. GC 观察 20 秒 ----------------
echo "[2/7] jstat 20s ..."
jstat -gcutil   "$PID" 1000 20 > dumps/jstat_gcutil.txt 2>&1 &
jstat -gccause  "$PID" 5000 5  > dumps/jstat_gccause.txt 2>&1 &

# ---------------- 3. 类直方图（不带 Full GC） ----------------
echo "[3/7] class histogram (no GC) ..."
jcmd "$PID" GC.class_histogram > dumps/class_histo_before_gc.txt 2>&1

# ---------------- 4. 检查磁盘 ----------------
NEED_MB=$(( $(jcmd "$PID" GC.heap_info 2>/dev/null | grep -oP '\d+(?=M used)' | head -1) * 2 ))
NEED_MB=${NEED_MB:-8192}   # 默认按 8G 预留
AVAIL_MB=$(df --output=avail -m "$OUTDIR/dumps" | tail -1 | tr -d ' ')
echo "[4/7] disk check: need ${NEED_MB}MB, avail ${AVAIL_MB}MB"
if [ "$AVAIL_MB" -lt "$NEED_MB" ]; then
    echo "[WARN] dump可能磁盘不足，请人工确认后继续"
fi

# ---------------- 5. Dump 1：完整 dump（不含 live，保留死对象链） ----------------
echo "[5/7] full heap dump (no live) ..."
DMP_FULL="dumps/heap_full.hprof"
if command -v jcmd >/dev/null 2>&1; then
    jcmd "$PID" GC.heap_dump "$(pwd)/$DMP_FULL" -all >/dev/null 2>&1
else
    jmap -dump:format=b,file="$DMP_FULL" "$PID" >/dev/null 2>&1
fi

# ---------------- 6. 间隔 20s 再抓第二份（对比，非常重要） ----------------
echo "[6/7] wait 20s and grab 2nd dump (live) ..."
sleep 20
DMP_LIVE="dumps/heap_live.hprof"
if command -v jcmd >/dev/null 2>&1; then
    jcmd "$PID" GC.heap_dump "$(pwd)/$DMP_LIVE" >/dev/null 2>&1
else
    jmap -dump:live,format=b,file="$DMP_LIVE" "$PID" >/dev/null 2>&1
fi

# ---------------- 7. 日志 & GC 文件 ----------------
echo "[7/7] collect logs ..."
# 这里的路径改成你实际的日志路径
for f in /var/log/app/*.log /var/log/gc*.log /var/log/dumps/*.hprof; do
    [ -f "$f" ] && cp "$f" logs/ 2>/dev/null
done
# hs_err / core dump
find / -maxdepth 4 -name "hs_err_pid${PID}*" -exec cp {} logs/ \; 2>/dev/null

wait   # 等待 jstat 后台进程
echo "[DONE] all artifacts saved to: $OUTDIR"
du -sh "$OUTDIR"
ls -la "$OUTDIR/dumps"
```

### 11.4.3 非常大的堆怎么办（>32G）？

```bash
# 方式 1：不要 dump 全堆，用 Arthas profiler 分配采样（优先）
as.sh <pid>
profiler start --event alloc
# 运行 10 分钟后：
profiler stop --file /data/alloc.html

# 方式 2：类直方图 + 采样 + Dominator 估算，不需要全量 dump
#   jmap -histo 2 次对比 → 找增长最快的 Top 类
#   Arthas heapdump 采样

# 方式 3：如果必须全 dump，挂载 SSD 盘 + 调大磁盘
#   注意：dump 过程中 JVM 会 STW（因为要保证快照一致性），生产要先摘流
```

---

## 11.5 第四步：分析环境准备（MAT 调优）

> **经验：直接用默认配置的 Eclipse MAT 打开大 dump，基本都会报 OOM 卡死。**

### 11.5.1 MAT 配置调优

找到 MAT 安装目录下的 `MemoryAnalyzer.ini`（Windows）或 `MemoryAnalyzer.app/Contents/Eclipse/MemoryAnalyzer.ini`（Mac）/ `ParseHeapDump.sh`（Linux 脚本版）：

```ini
# MemoryAnalyzer.ini（关键修改）
-startup
plugins/org.eclipse.equinox.launcher_xxx.jar
--launcher.library
plugins/org.eclipse.equinox.launcher.win32.win32.x86_64_xxx
-vmargs

# ⭐ 堆内存：建议 dump 文件大小的 1.5x ~ 2x
-Xmx32g

# ⭐ GC 选择：Parallel GC 比 G1 稳定处理大堆
-XX:+UseParallelGC
-XX:+UseParallelOldGC

# 元空间
-XX:MaxMetaspaceSize=512m

# 足够的线程栈
-Xss2m

# ⭐ 关闭 Eclipse 限制堆的默认阈值
-XX:SoftRefLRUPolicyMSPerMB=0

# ⭐ 临时工作目录：MAT 会在分析过程中产生大量 index 文件
-Djava.io.tmpdir=D:/mat_work/tmp

# 使用大页（OS 支持时开）
-XX:+UseLargePages
```

### 11.5.2 Linux 无头模式（推荐）

服务器上直接跑 MAT 解析，不启 UI：

```bash
# 下载 Linux MAT 并解压到 /opt/mat
cd /opt/mat
# MemoryAnalyzer.ini 先按上面调内存

# 解析：只跑 Leak Suspects + 组件报告（最快、最常用）
./ParseHeapDump.sh \
    /data/oom-dumps/xxx/heap_live.hprof \
    org.eclipse.mat.api:suspects \
    org.eclipse.mat.api:overview \
    org.eclipse.mat.api:top_components

# 输出：heap_live_Leak_Suspects.zip / heap_live_Top_Components.zip / ...
# 解压后 index.html 就是可视化报告，直接浏览器打开即可，无需装 MAT
```

### 11.5.3 解析失败怎么办？

| 错误 | 原因 | 解决 |
|------|------|------|
| `java.lang.OutOfMemoryError: Java heap space` in MAT | MAT 自己的 -Xmx 不够 | 继续加大，或换到更大内存的机器 |
| `GC overhead limit exceeded` in MAT | 同上，或 dump 损坏 | 加大 MAT 堆；换 ParallelGC |
| `Unknown HPROF Version` | dump 抓的过程中进程挂了 → 文件半截 | 重抓，抓的时候保证磁盘、内存、JVM 存活 |
| `Could not map view` | 32 位 MAT + 4G+ dump | 换 64 位版本 |

---

## 11.6 第五步：Dump 深入分析（四种核心技法）

### 技法 1：Leak Suspects Report（最省事）

打开 dump 后，第一步先跑 Leak Suspects Report（不跑白不跑，80% 情况能直接出结论）。

```
报告解读：
  Problem Suspect 1
  ================
  One instance of "com.xxx.cache.OrderCache" loaded by ...
  occupies 4,362,789,048 (67.23%) bytes.
  ← 一句话告诉你谁占了大部分内存

  Accumulated Objects in Dominator Tree
  ---------------------------------------------------------------------------
  Class Name                                        | Shallow Heap | Retained Heap | Percentage
  com.xxx.cache.OrderCache  @ 0x12345678            |           48 | 4,362,789,048 |    67.23%
  └─ java.util.HashMap$Node[] @ 0x22334455         |    8,388,608 | 4,362,789,000 |    67.23%
      └─ 大量 Order 对象实例（2,428,105 个）        |   58,274,520 | 4,354,400,392 |    67.10%

  ↓
  结论：OrderCache 里 HashMap 存了 240 万个订单，没清理 → 静态缓存泄漏
```

---

### 技法 2：Histogram → Retained Heap → Path to GC Roots（最精准）

```
步骤：
  1. Window → Show View → Histogram
  2. 点 "Retained Heap" 表头倒序
  3. 跳过 JDK 基础类（byte[]、String、HashMap$Node），找业务自定义类
  4. 找到可疑业务类 → 右键 List objects → with outgoing references
     （看它持有的引用，判断是否真的占了大对象）
  5. 或者 Merge Shortest Paths to GC Roots → exclude all phantom/weak/soft refs
     （去掉非强引用后，看看是谁一直握着不撒手）
```

Path to GC Roots 典型结果解读：

```
Class Name                                                          | Shallow Heap
------------------------------------------------------------------------------
com.xxx.entity.Order @ 0x7f001234                                    |           64
  ← elementData[1234] of java.util.ArrayList @ 0x7f00abcd            |        10240
     ← orders of com.xxx.service.OrderReportTask @ 0x7f00b000        |          128
        ← task of java.util.concurrent.FutureTask @ 0x7f00b001       |          ...
           ← workers[42] of java.util.concurrent.ThreadPoolExecutor   |
              ← thread of OrderReportThread-12 （线程池中）           |
                    ← 一直 RUNNABLE （任务卡住了？） → 这是根！

结论：一个长期卡住的后台线程任务 → 它里面 ArrayList 累积了 200w Order 没释放
修复：线程池任务加超时；或任务分批处理。
```

---

### 技法 3：两次 Dump 对比（找"增长最快的类"=泄漏类）

```
步骤：
  1. 打开 dump1（T0 时刻）→ File → Add to Compare Basket
  2. 打开 dump2（T1 时刻，晚 20 秒）→ File → Add to Compare Basket
  3. Compare Basket 视图 → 点击 Compare the results

  输出（重点关注 Delta 列）：

  Class Name                     #Instances(T0)  #Instances(T1)  ΔInstances
  -----------------------------------------------------------------------------
  com.xxx.Order                  1,200,000       1,800,000      +600,000   ← 20 秒涨了 60w！
  com.xxx.OrderItem              5,000,000       7,500,000      +2,500,000
  java.lang.String               8,000,000       8,120,000      +120,000     ← JDK 类基本不动

  → ΔInstances 最大的非 JDK 类就是嫌疑泄漏对象
```

---

### 技法 4：OQL（对象查询语言，高级排查）

当需要做更精细的查询时用 OQL（MAT/VisualVM/jhat 都支持）。

```sql
-- 1. 查金额异常大的订单
SELECT o FROM com.xxx.Order o WHERE o.amount.value > 1000000

-- 2. 查字符串超长的（可能是大 JSON 累积）
SELECT s FROM java.lang.String s WHERE s.value.length > 10000

-- 3. 查 HashMap 中 key 数量超过 10 万的（无界缓存）
SELECT h, h.table.length, h.size
FROM java.util.HashMap h
WHERE h.size > 100000

-- 4. 查 ThreadLocal Map 里值很多的（ThreadLocal泄漏嫌疑）
SELECT t.name, t.threadLocals.table.length
FROM java.lang.Thread t
WHERE t.threadLocals.table.length > 1000

-- 5. 查某个类的所有实例并计算总和
SELECT u.userId, COUNT(1)
FROM com.xxx.UserOrder u
GROUP BY u.userId
ORDER BY COUNT(1) DESC
```

---

### 四种技法组合拳（推荐顺序）

```
Leak Suspects 报告 → 80% 问题直接有结论
    ↓ 结论模糊？
Histogram Retained Top → 定位业务类
    ↓ 还是不清楚？
对比两次 Dump → 找出增长最快的类
    ↓ 想深挖引用链条？
Path to GC Roots → 定位 "谁持有"
    ↓ 精细筛选？
OQL → 按条件枚举对象
```

---

## 11.7 第六步：区分内存泄漏 vs 内存膨胀

> 这是分析 Dump 后必须得出的核心结论。两类 OOM 的修复方向完全不同。

### 11.7.1 定义

| 维度 | 内存泄漏（Memory Leak） | 内存膨胀（Memory Bloat） |
|------|--------------------------|---------------------------|
| 定义 | 对象本应被回收但被意外持有，GC 不了 | 真实有用对象太多、或单个对象太大、或数据结构冗余 |
| 核心特征 | Old Gen **基线持续上升**，Full GC 后不能回落 | Old Gen **基线稳定**，但峰值瞬时逼近或超过 Xmx |
| 典型场景 | static 集合、ThreadLocal 未 remove、监听器未注销 | 全表查 100w 条到内存、缓存命中率低、单个超大 JSON 解析 |
| 发生时间 | 慢慢积累，数小时 / 数天 / 数周后 OOM | 每次大促/大导出都容易 OOM，重启后能正常一段时间 |
| 代码修复方向 | 释放引用、remove、加 TTL、加注销钩子 | 分页/流式、DB 聚合、减小单对象体积、加对象池 |
| 参数调优帮助 | ✗ 调大 Xmx 只能延缓，根治不了 | ✓ 合理调大 Xmx 往往能立即见效 |
| 2 次 Dump 对比 | ΔInstances 高的非 JDK 类数量显著增长 | 各实例比例基本同比例增长，没有"出头鸟" |

### 11.7.2 定量判断公式

```
变量：
  B0 = 第一次 Full GC 后的 Old 占用
  B1 = 第二次 Full GC 后的 Old 占用（1 小时后）
  B2 = 第三次 Full GC 后的 Old 占用（2 小时后）

判断：
  若 B0 < B1 < B2 且差距 > 10%
     → 泄漏（基线阶梯上升）

  若 B0 ≈ B1 ≈ B2（±2%），只是瞬时峰值超 Xmx
     → 内存膨胀 / 堆太小 / 大对象

  若 Dump 的 Leak Suspects 报告里某个业务类 > 50% Retained Heap
     → 强泄漏嫌疑

  若 Top Retained 基本都是 HashMap$Node / byte[] / char[] 等数组头且分散
     → 通常是大流量膨胀，不是泄漏
```

### 11.7.3 决策树

```
Old Gen 趋势图
    │
    ├─ Full GC 后基线不断上升？
    │      是 ──→ 泄漏
    │      │         ├ static HashMap/List？→ 改 Caffeine 加 maxSize + TTL
    │      │         ├ ThreadLocal 无 remove？→ finally remove
    │      │         ├ Listener/Observer 未注销？→ 注销钩子
    │      │         └ ClassLoader 泄漏？→ 排查热部署/动态代理
    │      否
    │
    └─ 看峰值时刻：
        ├ 峰值伴随导出/报表/批量任务？
        │     → 大接口，改分页/流式 + MyBatis ResultHandler
        │
        ├ 峰值伴随 CMS/G1 Remark？
        │     → Full GC 参数调优
        │
        └ 所有类均匀占大堆？
              → 业务增长，堆不够
              动作：加机器 / 加大 Xmx / 拆分服务 / 增加本地缓存淘汰比例
```

---

## 11.8 第七步：修复验证 + 复盘闭环

### 11.8.1 修复验证四步

```
1. 单元测试复现
   - 写针对泄漏点的 UT：重复执行 N 次后 GC，验证对象数回落
   - OOM 断言：MXBean / JUnit Extension 监控堆占用

2. 稳定性压测
   - 同模型流量 × 1.5 倍 × 24 小时
   - 重点观察：
     □ Heap after Full GC 是否趋势平稳？
     □ Full GC 次数/小时？
     □ Metaspace 曲线？
     □ Direct Memory？

3. 灰度验证
   - 先上 1 台 / 2% 流量
   - 观察 ≥ 1 个典型泄漏周期（上次 OOM 用了 3 天，就观察至少 4 天）
   - 关键指标：
     □ Heap使用率、FullGC次数、Class 数、线程数
     □ GC 时间占比（SLA：< 5%）

4. 全量 & 持续观察
   - 至少 7 天内告警正常
   - 1 个月后看 Heap 曲线是否完全平稳
```

### 11.8.2 复盘模板（5Why）

```
事故：2024-03-15 订单服务 Heap OOM
影响：2 台实例重启，15 分钟用户下单失败率 23%

1. Why？为什么 OOM？
   → Old Gen 满，MAT 分析 OrderCache 静态 Map 累积了 240w 订单。

2. Why？为什么 OrderCache 累积了 240w？
   → put 了没 remove，也没 TTL。当时手写 HashMap 做本地缓存。

3. Why？为什么用手写 Map 不选 Caffeine？
   → 开发赶进度，"先跑起来再优化"，代码 Review 也没卡。

4. Why？Review 没发现？
   → 团队 Code Review Checklist 没有"静态缓存必须用框架+TTL"条目。
   → Heap>80% 告警阈值虽有，但告警到钉钉没值班人实时响应。

5. Why？告警没人管？
   → 值班表是 8 小时值班，OOM 发生在 18:40 下班时，第二个人轮班还没上。

=== 修复行动项 Action Items ===
P0：立刻替换所有手写 static Map 缓存为 Caffeine，强制 maxSize + TTL（1 周内）
P1：补 Code Review Checklist，增加静态缓存/ThreadLocal 条目（3 天内）
P2：告警通道接入电话 + 短信，值班交接半小时前提醒（1 周内）
P3：压测环境增加 24h 稳定性测试，自动生成 Heap 趋势报告（2 周内）
P4：所有应用默认开 Heap Dump on OOM，路径统一挂载共享盘（1 周内）

=== 责任人 & DDL ===
...
```

---

## 11.9 应急响应全流程图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        OOM 告警触发                                   │
│              (Heap>95% / FullGC>5次/h / K8s重启 / Pod健康失败)        │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ 1min 内
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  T+0 ~ T+3min                                                        │
│  ════════ 立即摘流 ════════                                         │
│  K8s label/NotReady   /   Nginx upstream down   /   Actuator下线     │
│  网关权重=0   /   兜底 iptables -j DROP                              │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ 摘流成功？
                 ┌───────────────┴───────────────┐
                 │ No （实例可能已挂/健康失败）     │ Yes
                 ▼                                 ▼
┌──────────────────────────────────┐ ┌────────────────────────────────┐
│ 立刻去 K8s worker 节点找         │ │ ════════ 保留现场 ════════      │
│ /var/log/dumps 下的自动 dump      │ │ ❌ 禁止 GC.run / 重启 / kill-9   │
│ dmesg 是否有 OOM Killer 记录       │ │ ✅ df -h 检查磁盘               │
│ Pod Events 看 Kill 原因           │ │ ✅ cp 日志 & GC 日志            │
│ kubectl logs --previous 捞旧容器   │ │ ✅ ps/top/vmstat/dmesg 快照    │
└──────────────┬───────────────────┘ └───────────────┬────────────────┘
               │                                     │
               └──────────────┬──────────────────────┘
                              │
                              ▼  T+3 ~ T+10min
┌─────────────────────────────────────────────────────────────────────┐
│  ════════ 抓取 Dump（一键脚本） ════════                             │
│  thread ×3 / jstat / class_histo_no_gc                              │
│  dump_full  (不 Full GC，保留死对象链)                                │
│  等待 20s                                                           │
│  dump_live  (会 Full GC，作为对比)                                   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ dump 安全落盘 ✓
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  T+10 ~ T+15min  业务恢复或重启                                       │
│  ════════ 恢复业务 ════════                                          │
│  关键服务：K8s 新 Pod 拉起 / 回滚到上一版本                            │
│  或：确认 dump 保存成功后 restart 实例                                │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ 场外分析（不影响业务）
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  分析环境：                                                           │
│  MAT MemoryAnalyzer.ini 调 -Xmx 1.5x dump 大小                       │
│  无头 Linux 跑 ParseHeapDump.sh suspects/overview/top_components     │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Dump 分析四技法：                                                    │
│  ① Leak Suspects（最省事）                                           │
│  ② Histogram → Retained → Path to GC Roots（最精准）                 │
│  ③ 两次 Dump 对比 → ΔInstances 增长 Top（区分泄漏/膨胀）              │
│  ④ OQL（精细筛选）                                                   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  定性：                                                              │
│  ├ Old Baseline 阶梯上升？ ──→ 泄漏  → 释放引用 + 注销钩子 + TTL     │
│  └ Old Baseline 平稳？    ──→ 膨胀  → 分页/流式 + 调参 + 加机器      │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  修复 + 验证 + 复盘闭环                                              │
│  UT → 稳定性压测 24h → 灰度 1 实例 → 全量 → 5Why 复盘 + ActionItems  │
└─────────────────────────────────────────────────────────────────────┘
```

---
如果线上 Java 服务发生 OOM，你如何定位？

首先我不会直接增加 Xmx，而是先根据异常日志确认具体的 OOM 类型，比如 Java Heap、Metaspace、Direct Memory 或 Native Thread，因为不同类型的排查方向不同。

如果是 Java Heap OOM，我首先会通过 jinfo 或 jcmd 查看 JVM 参数，然后使用 jstat -gcutil 观察 Old Gen 的变化以及 Full GC 后内存是否能够正常下降。

如果发现 Old Gen 持续上涨，Full GC 后也无法明显下降，我会怀疑存在内存泄漏。接下来通过 jcmd GC.heap_dump 获取 Heap Dump。

然后使用 MAT 分析 Heap Dump，重点查看 Leak Suspects、Histogram 和 Dominator Tree，找到 Retained Heap 最大的对象。

最后通过 Path to GC Roots 分析对象的引用链，定位为什么对象无法被 GC，例如 static Map、ThreadLocal、缓存、无界队列或者 Listener。

修复后会重新进行压测，并持续观察 Old Gen、Full GC 次数和进程 RSS，确认内存不会持续增长。

