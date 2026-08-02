# Node.js 高级工程师面试题集

> 本面试题集面向 Node.js 高级工程师岗位，覆盖核心原理、性能优化、工程化、异步并发、流处理、Web 服务、数据库、安全、架构设计、调试排错等十大技术领域。每个领域包含**基础概念题、原理分析题、实践应用题、场景设计题**四类题型，并提供参考答案、评分要点及真实项目案例。

---

## 目录

- [第一篇 核心原理篇](#第一篇-核心原理篇)
- [第二篇 性能优化篇](#第二篇-性能优化篇)
- [第三篇 工程化篇](#第三篇-工程化篇)
- [第四篇 异步编程与并发控制篇](#第四篇-异步编程与并发控制篇)
- [第五篇 流与数据处理篇](#第五篇-流与数据处理篇)
- [第六篇 Web 服务与网络篇](#第六篇-web-服务与网络篇)
- [第七篇 数据库与存储篇](#第七篇-数据库与存储篇)
- [第八篇 安全篇](#第八篇-安全篇)
- [第九篇 架构设计篇](#第九篇-架构设计篇)
- [第十篇 调试与排错篇](#第十篇-调试与排错篇)
- [附录 评分标准与面试官指南](#附录-评分标准与面试官指南)

---

## 第一篇 核心原理篇

### Q1.1【基础概念题】请说明 Node.js 的整体架构，以及 V8、Libuv、事件循环三者的关系。

**参考答案**：

Node.js 架构自上而下分为四层：

```
┌─────────────────────────────────────┐
│        Node API (JS 层)             │  fs / http / stream / crypto ...
├─────────────────────────────────────┤
│      Node Core (C++ 绑定层)         │  把 V8 / Libuv 能力暴露给 JS
├──────────────────┬──────────────────┤
│   V8 引擎        │   Libuv          │
│  (JS→机器码执行)  │ (事件循环/异步IO) │
├──────────────────┴──────────────────┤
│        操作系统 (网络/文件/线程池)    │
└─────────────────────────────────────┘
```

- **V8**：Google 的 JS 引擎，负责把 JavaScript 编译成机器码执行，提供 GC、JIT、对象模型等能力。Node.js 只用了 V8 的运行时能力，去掉了浏览器相关的 DOM/BOM。
- **Libuv**：C 语言编写的跨平台异步 I/O 库，是 Node.js 异步能力的核心。它提供了**事件循环**、**线程池**（默认 4 个线程，可通过 `UV_THREADPOOL_SIZE` 调整）、统一的 I/O 多路复用封装（Linux epoll、macOS kqueue、Windows IOCP）。
- **事件循环**：Libuv 实现的循环结构，Node.js 主线程在启动后进入该循环，不断从各阶段队列中取出回调执行。它是"单线程异步"模型的实现载体。

三者关系：V8 执行 JS 代码，当代码调用异步 API（如 `fs.readFile`）时，Node C++ 层会把任务交给 Libuv，Libuv 通过线程池或系统 I/O 多路复用处理，完成后把回调放入事件循环对应阶段队列，主线程在循环中取出执行。

**评分要点**：
- ✅ 能准确画出/描述四层架构（必备）
- ✅ 说明 V8 与 Libuv 各自职责分工（必备）
- ✅ 提到线程池默认 4 个、`UV_THREADPOOL_SIZE` 可调（加分）
- ✅ 提到不同平台 I/O 多路复用实现差异（加分）
- ❌ 仅说"Node 是单线程"而不知线程池存在（扣分）

---

### Q1.2【原理分析题】详细描述 Node.js 事件循环的六个阶段，以及微任务（microtask）在每个阶段的执行时机。

**参考答案**：

事件循环一次迭代经历六个阶段：

1. **timers**：执行到期的 `setTimeout` / `setInterval` 回调
2. **pending callbacks**：执行上一轮循环延迟执行的系统级回调（如 TCP `ECONNREFUSED` 错误）
3. **idle, prepare**：Libuv 内部使用，开发者不接触
4. **poll**：获取新 I/O 事件，执行 I/O 回调。若队列为空：若有 `setImmediate` 待执行则跳到 check 阶段；否则阻塞等待 I/O 事件到来（或有 timer 到期则限时等待）
5. **check**：执行 `setImmediate` 回调
6. **close callbacks**：执行关闭事件回调（如 `socket.on('close')`）

**微任务执行时机**：**每次阶段切换之间**（即每完成一个阶段的回调后，准备进入下一阶段前），都会清空微任务队列。微任务有两类，执行顺序为：

1. **`process.nextTick` 队列**：优先级最高
2. **Promise 微任务队列**：通过 `queueMicrotask` 或 `.then` 注册

```
阶段1 → 清空 nextTick + Promise 微任务 → 阶段2 → 清空微任务 → ...
```

**经典执行顺序题**：
```js
console.log('1');
setTimeout(() => console.log('2'), 0);
setImmediate(() => console.log('3'));
Promise.resolve().then(() => console.log('4'));
process.nextTick(() => console.log('5'));
console.log('6');
// 输出：1 6 5 4 2 3（主模块中 2/3 顺序不保证，但通常 2 先）
```

**评分要点**：
- ✅ 准确列出六个阶段及职责（必备）
- ✅ 明确微任务在"阶段切换之间"清空，而非"每个宏任务后"（与浏览器差异，关键点）
- ✅ 说明 `nextTick` 优先级高于 `Promise`（必备）
- ✅ 能解释主模块中 setTimeout/setImmediate 顺序不确定，但 I/O 回调中 setImmediate 一定先（加分）
- ❌ 把 Node 事件循环与浏览器混为一谈（扣分）

---

### Q1.3【原理分析题】Node.js 的"单线程"到底是单线程还是多线程？请从 JavaScript 主线程、Libuv 线程池、Worker Threads 三个层面详细分析。

**参考答案**：

Node.js 的"单线程"是个**易混淆的简化说法**，实际情况分三层：

**1. JavaScript 主线程——单线程**
- 用户编写的 JS 代码、事件循环、回调执行都在**唯一的主线程**中运行
- 这是"单线程"说法的来源，也意味着 CPU 密集型 JS 计算会阻塞整个事件循环

**2. Libuv 线程池——多线程（默认 4）**
- Libuv 维护一个线程池处理无法异步的 I/O（主要是**磁盘文件 I/O**，因为 Linux 没有完美的异步文件 I/O）和 CPU 密集型任务（如 DNS 解析 `dns.lookup`、加密 `crypto.pbkdf2`）
- 默认 4 个线程，通过 `UV_THREADPOOL_SIZE` 环境变量可调（最大 1024）
- 线程池完成任务后，把回调交给主线程在事件循环 poll 阶段执行
- ⚠️ 注意：**网络 I/O 不走线程池**，而是用 epoll/kqueue/IOCP 多路复用

**3. Worker Threads——多线程（用户级）**
- Node 10+ 提供的 `worker_threads` 模块，允许用户创建真正的 JS 工作线程
- 每个 Worker 有独立的 V8 实例、独立的事件循环、独立的内存空间
- 通过 `SharedArrayBuffer` 或 `MessagePort` 通信
- 用于 CPU 密集型计算（图像处理、加密、大数据计算）

**结论**：Node.js 是"**主线程单线程 + Libuv 线程池辅助 I/O + 用户可扩展 Worker Threads**"的混合模型。说"单线程"是指 JS 执行层面，不代表底层没有多线程。

**评分要点**：
- ✅ 明确区分三个层面（必备）
- ✅ 指出文件 I/O 走线程池而网络 I/O 不走（关键区分点）
- ✅ 提到 `UV_THREADPOOL_SIZE` 可调（加分）
- ✅ 能说明 Worker Threads 适用场景与通信机制（加分）

---

### Q1.4【实践应用题】请实现一个可取消的、支持并发的 Promise 任务调度器，要求同时运行的任务数不超过 `limit`，并能返回每个任务结果或失败原因。

**参考答案**：

```js
class AsyncTaskScheduler {
  constructor(limit = 5) {
    this.limit = limit;
    this.activeCount = 0;
    this.queue = []; // 待执行任务
    this.cancelledIds = new Set();
  }

  /**
   * @param {() => Promise} task 返回 Promise 的函数
   * @param {string} id 任务标识，用于取消
   */
  add(task, id = Math.random().toString(36)) {
    return new Promise((resolve, reject) => {
      const run = () => {
        // 取消检查
        if (this.cancelledIds.has(id)) {
          this.cancelledIds.delete(id);
          reject(new Error(`Task ${id} cancelled`));
          return;
        }
        this.activeCount++;
        task()
          .then(resolve)
          .catch(reject)
          .finally(() => {
            this.activeCount--;
            this.next();
          });
      };

      if (this.activeCount < this.limit) {
        run();
      } else {
        this.queue.push(run);
      }
    });
  }

  next() {
    if (this.queue.length > 0 && this.activeCount < this.limit) {
      const run = this.queue.shift();
      run();
    }
  }

  cancel(id) {
    this.cancelledIds.add(id);
  }
}

// 使用示例
const scheduler = new AsyncTaskScheduler(3);
const urls = Array.from({ length: 10 }, (_, i) => `https://api.example.com/${i}`);

const results = await Promise.allSettled(
  urls.map((url, i) =>
    scheduler.add(() => fetch(url).then((r) => r.json()), `task-${i}`)
  )
);

// 取消某个任务
scheduler.cancel('task-5');
```

**评分要点**：
- ✅ 用队列 + 活跃计数实现并发限制（必备）
- ✅ 在 `finally` 中触发下一个任务（必备）
- ✅ 支持取消机制（加分）
- ✅ 返回 Promise 以便 `Promise.allSettled` 聚合（加分）
- ✅ 考虑取消竞态（任务已在队列但未执行时取消）（高级）

**真实项目案例**：
- **项目背景**：电商商品详情页聚合服务，需并发调用 20+ 个下游服务（价格、库存、评价、推荐等）
- **技术选型原因**：直接 `Promise.all` 并发会打垮下游，需限流；自研调度器可控性高
- **实现步骤**：调度器 + 任务超时 + 熔断降级 + 结果缓存
- **挑战**：个别下游慢导致整体超时；解决：单任务超时 + 部分降级返回兜底数据
- **最终效果**：详情页 P99 从 1.2s 降至 400ms，下游错误率下降 80%

---

### Q1.5【场景设计题】你的 Node.js 服务在某次大促时突然响应变慢，监控发现 CPU 没满但请求堆积，事件循环延迟（event loop lag）飙到 2 秒。请给出完整的排查思路和解决方案。

**参考答案**：

**排查思路**：

1. **确认事件循环延迟根因**——CPU 没满但 lag 高，说明主线程被同步操作阻塞，而非 CPU 瓶颈。常见原因：
   - 同步 I/O 调用（`fs.readFileSync`、`JSON.parse` 大对象）
   - 复杂正则匹配（catastrophic backtracking）
   - 大循环 / 深递归
   - 加密同步 API（`crypto` 的 `*Sync` 方法）

2. **采集证据**：
   ```js
   // 监控事件循环延迟
   const { monitorEventLoopDelay } = require('perf_hooks');
   const h = monitorEventLoopDelay();
   h.enable();
   setInterval(() => {
     console.log({ min: h.min, max: h.max, mean: h.mean, p99: h.percentile(99) });
   }, 1000);

   // 用 --prof 采集 CPU profile
   // node --prof app.js
   // node --prof-process isolate-*.log > profile.txt

   // 或用 clinic.js doctor
   // clinic doctor --on-port 'autocannon localhost:3000' -- node app.js
   ```

3. **火焰图定位**：用 `0x` 或 `clinic flame` 生成火焰图，找到宽的调用栈

4. **典型场景与方案**：

   | 根因 | 解决方案 |
   | --- | --- |
   | `JSON.parse` 大 payload | 流式解析（`JSONStream`）或换 `simdjson` |
   | 同步 `readFileSync` | 改异步或预加载到内存 |
   | 正则灾难性回溯 | 改用字符串方法或安全正则 |
   | CPU 密集计算 | 拆分到 Worker Threads 或独立服务 |
   | 大量同步日志 | 改异步日志（pino）或写日志服务 |

5. **长效机制**：
   - 接入 APM（Prometheus + Grafana）监控事件循环 lag、内存、句柄数
   - Code Review 卡 `*Sync` 调用
   - 压测准入（每次发版前 `autocannon` 压测）

**评分要点**：
- ✅ 准确判断"CPU 不满但 lag 高 = 同步阻塞"（核心洞察）
- ✅ 给出具体工具（`monitorEventLoopDelay`、`--prof`、`clinic`、`0x`）（必备）
- ✅ 列出常见根因与对应方案（必备）
- ✅ 提出长效监控与预防机制（加分）

**真实项目案例**：
- **项目背景**：物流轨迹查询服务，大促时 QPS 涨 5 倍后响应从 50ms 飙到 5s
- **排查过程**：`clinic doctor` 显示事件循环 lag 3s，火焰图定位到 `JSON.parse` 一个 8MB 的轨迹包
- **解决方案**：下游接口改造分页 + 本地流式解析 + Redis 缓存热点轨迹
- **最终效果**：lag 降到 50ms 以内，P99 60ms，扛住 5 倍流量

---

## 第二篇 性能优化篇

### Q2.1【基础概念题】请列举 Node.js 常见的内存泄漏场景及检测方法。

**参考答案**：

**常见内存泄漏场景**：

1. **全局变量未释放**：`global.cache = hugeObject`
2. **闭包持有大对象**：闭包引用未使用的大变量
3. **事件监听器累积**：反复 `on` 未 `off`，尤其中间件每次请求 `on`
4. **定时器未清理**：`setInterval` 未 `clearInterval`
5. **缓存无上限**：用 `Map` 当缓存但无淘汰策略
6. **数据库/Redis 连接未归还**：连接池泄漏
7. **Stream 未正确关闭**：可读流未消费完未 destroy
8. **Promise 未 resolve/reject**：永远 pending，闭包不释放

**检测方法**：

```js
// 1. 进程内存监控
setInterval(() => {
  const m = process.memoryUsage();
  console.log({
    rss: (m.rss / 1024 / 1024).toFixed(1) + 'MB',
    heapUsed: (m.heapUsed / 1024 / 1024).toFixed(1) + 'MB',
    heapTotal: (m.heapTotal / 1024 / 1024).toFixed(1) + 'MB',
    external: (m.external / 1024 / 1024).toFixed(1) + 'MB',
  });
}, 10000);

// 2. 堆快照对比（--inspect + Chrome DevTools）
//    Memory → Take heap snapshot → 操作前后各拍一张 → Comparison 对比

// 3. 代码中触发堆快照
const v8 = require('v8');
const snap = v8.writeHeapSnapshot(); // 生成 .heapsnapshot 文件

// 4. 自动检测：node-memwatch / heapdump
// 5. 生产环境：用 --max-old-space-size 限制 + OOM 自动重启
```

**评分要点**：
- ✅ 列举 5+ 种泄漏场景（必备）
- ✅ 提到堆快照对比法（必备）
- ✅ 提到 `process.memoryUsage` 各字段含义（rss/heapUsed/heapTotal/external）（加分）
- ✅ 提到生产环境限制 + 自动重启策略（加分）

---

### Q2.2【原理分析题】V8 的垃圾回收机制是怎样的？在 Node.js 中如何减少 GC 对事件循环的影响？

**参考答案**：

**V8 GC 机制**：

V8 采用**分代式垃圾回收**，堆分为**新生代**（Young Generation）和**老生代**（Old Generation）：

1. **新生代（Scavenge 算法）**：
   - 存放短生命周期对象，容量小（1~8MB）
   - 采用 **Cheney 算法**：堆分为 From 和 To 两个半区
   - GC 时把 From 中存活对象复制到 To，清空 From，角色互换
   - 晋升条件：经历过一次 Scavenge 仍存活，或 To 空间使用超 25%

2. **老生代（Mark-Sweep + Mark-Compact）**：
   - 存放长生命周期对象，容量大（GB 级）
   - **Mark-Sweep（标记清除）**：从根遍历标记可达对象，清除未标记
   - **Mark-Compact（标记整理）**：解决碎片化，移动存活对象到一端
   - 采用**增量标记（Incremental Marking）**和**并发标记（Concurrent Marking）**减少停顿

3. **Orinoco**：V8 现代 GC 优化，将标记、清理、整理并发/并行化，主线程停顿从百毫秒级降到毫秒级

**减少 GC 影响的策略**：

1. **避免频繁创建短命大对象**：复用对象、对象池
2. **避免"对象抖动"**：循环内不要反复 `new` 大对象
3. **合理使用 Buffer**：Buffer 不在 V8 堆，不参与 V8 GC
4. **控制堆大小**：`--max-old-space-size` 避免老生代过大导致长 GC
5. **流式处理大数据**：避免一次性加载大 JSON/文件
6. **复用正则对象**：避免循环内 `new RegExp`
7. **监控 GC**：
   ```js
   const { PerformanceObserver } = require('perf_hooks');
   const obs = new PerformanceObserver((list) => {
     list.getEntries().forEach((e) => {
       console.log(`${e.kind}: ${e.duration}ms`);
     });
   });
   obs.observe({ entryTypes: ['gc'] });
   ```

**评分要点**：
- ✅ 准确描述分代回收（新生代 Scavenge、老生代 Mark-Sweep/Compact）（必备）
- ✅ 提到晋升条件（加分）
- ✅ 提到增量/并发标记减少停顿（加分）
- ✅ 给出至少 3 条减少 GC 影响的实践（必备）

---

### Q2.3【实践应用题】请设计一个高吞吐的 Node.js 日志方案，要求：异步写入不阻塞主线程、支持按级别/日期切分、不丢日志（进程异常退出也能落盘）。

**参考答案**：

**方案设计**：

1. **异步非阻塞写入**：
   - 使用 `pino`（基于 `sonic-boom`，无锁队列 + `fsync` 异步）
   - 避免 `console.log`（同步、阻塞、无缓冲）
   - 用 `WriteStream` 或 `pino` 的 `destination` 异步写

2. **日志切分**：
   - 用 `pino-roll` 或 `rotating-file-stream` 按日期/大小切分
   - 或用 `logrotate`（系统级，配合 `SIGUSR1` 重开日志句柄）

3. **不丢日志**：
   - **同步 flush**：在 `process.on('exit')` 中同步 flush 缓冲
   - **捕获异常**：`process.on('uncaughtException')` 中先写日志再退出
   - **AOF 思路**：先写内存队列，定时批量 flush；进程退出前 flush
   - **借助 stdout + 外部采集**：日志直接 `process.stdout.write`，由 PM2/Fluentd/Filebeat 采集落盘（推荐生产用法）

```js
// 生产级方案：pino + stdout + 采集器
const pino = require('pino');
const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: process.env.NODE_ENV === 'production'
    ? undefined
    : { target: 'pino-pretty' },
});

// 安全退出 + flush
async function gracefulExit(signal) {
  logger.info({ signal }, '收到退出信号');
  logger.flush(); // 同步 flush
  process.exit(0);
}
['SIGINT', 'SIGTERM', 'uncaughtException', 'unhandledRejection'].forEach((e) =>
  process.on(e, (arg) => {
    if (e.startsWith('un')) {
      logger.fatal({ err: arg?.stack || arg }, e);
      logger.flush();
      process.exit(1);
    } else {
      gracefulExit(e);
    }
  })
);
```

4. **采集架构**：
   ```
   Node 进程 → stdout → PM2/Filebeat → Kafka → ES/日志系统
   ```

**评分要点**：
- ✅ 指出 `console.log` 同步阻塞的问题（必备）
- ✅ 提到 `pino` 或同类高性能库（必备）
- ✅ 切分方案（库或 logrotate）（必备）
- ✅ 不丢日志：`exit`/`uncaughtException` flush（必备）
- ✅ 生产推荐 stdout + 采集器分离（高级）

**真实项目案例**：
- **项目背景**：千万级 DAU 的社交服务，单机 QPS 5000，原用 `winston` 同步写文件导致事件循环 lag
- **技术选型**：`pino` 输出 stdout + Filebeat 采集到 Kafka + ELK
- **挑战**：日志格式不统一影响检索；解决：统一 JSON 格式 + traceId 贯穿
- **最终效果**：日志开销从 15% CPU 降到 2%，P99 降 30ms，日志检索秒级

---

### Q2.4【场景设计题】你的 Node.js 服务是 CPU 密集型（图像处理），单实例无法横向扩展 CPU 利用率。请设计一个方案，使单台 16 核服务器 CPU 利用率达到 80%+，且请求能均匀分配。

**参考答案**：

**方案：Cluster + 任务分发**

1. **Cluster 模式**：用 Node.js `cluster` 模块启动 16 个 worker，每个 worker 占一核，独立事件循环
2. **负载均衡**：`cluster.schedulingPolicy = cluster.SCHED_RR`（Linux 默认 RR 轮询），主进程接受连接分发给 worker
3. **CPU 亲和性**：用 `taskset` 或 `numactl` 把每个 worker 绑定到指定核，减少上下文切换
4. **优雅重启**：文件监听 + `worker.send('disconnect')` 逐个重启，零停机
5. **监控**：每个 worker 上报 CPU/内存，主进程汇总

```js
// cluster 主进程
const cluster = require('cluster');
const os = require('os');
const numCPUs = os.cpus().length;

cluster.schedulingPolicy = cluster.SCHED_RR;

if (cluster.isPrimary) {
  for (let i = 0; i < numCPUs; i++) {
    const worker = cluster.fork();
    worker.on('exit', (code) => {
      console.log(`worker ${worker.process.pid} 退出，重启`);
      cluster.fork();
    });
  }
  process.on('SIGUSR2', () => {
    Object.values(cluster.workers).forEach((w) => w.send('graceful-shutdown'));
  });
} else {
  require('./image-worker');
  process.on('message', (msg) => {
    if (msg === 'graceful-shutdown') {
      server.close(() => process.exit(0));
    }
  });
}
```

**替代方案对比**：

| 方案 | 优点 | 缺点 |
| --- | --- | --- |
| Cluster | 原生、简单、共享端口 | worker 间内存不共享，状态需外部存储 |
| Worker Threads | 内存共享、轻量 | 仍单进程，崩溃影响全局 |
| 多进程 + Nginx | 灵活、隔离性好 | 需额外组件、端口管理 |
| PM2 cluster | 自动化、带监控 | 黑盒、定制性差 |

**进阶优化**：
- 大图分块并行：把单张大图切割，分发到不同 worker 处理后合并（MapReduce 模式）
- 用 `sharp`（基于 libvips，本身多线程）替代 `jimp`，单线程性能就高
- 任务队列化：用 Redis 队列 + worker 池，削峰填谷

**评分要点**：
- ✅ Cluster 方案 + 16 worker（必备）
- ✅ 提到 SCHED_RR 负载均衡（必备）
- ✅ 优雅重启 / 崩溃自愈（必备）
- ✅ 对比 Cluster / Worker Threads / Nginx 多方案（加分）
- ✅ 提到任务分块并行 / sharp 等进阶优化（高级）

---

### Q2.5【场景设计题】请设计一个 Node.js 服务的全链路性能监控体系，需覆盖应用层、运行时层、系统层，并能定位到具体慢接口和慢 SQL。

**参考答案**：

**监控分层架构**：

```
┌─────────────── 应用层 ───────────────┐
│ 接口 RT/QPS/错误率 | 慢 SQL | 依赖调用 │
├─────────────── 运行时层 ─────────────┤
│ 事件循环 lag | GC | 堆内存 | 句柄数    │
├─────────────── 系统层 ───────────────┤
│ CPU | 内存 | 磁盘 IO | 网络 | 句柄     │
└──────────────────────────────────────┘
        ↓ Prometheus 拉取
   Grafana 展示 + AlertManager 告警
```

**1. 应用层监控（APM）**

```js
// 中间件：记录接口 RT、状态码、慢请求
app.use(async (ctx, next) => {
  const start = Date.now();
  const traceId = ctx.headers['x-trace-id'] || uuid();
  ctx.state.traceId = traceId;
  await next();
  const duration = Date.now() - start;
  httpRequestDuration.labels(ctx.method, ctx.path, ctx.status).observe(duration);
  if (duration > 1000) {
    logger.warn({ traceId, path: ctx.path, duration }, '慢请求');
  }
});

// 慢 SQL：knex/prisma 中间件
db.on('query', (data) => { data.__start = Date.now(); });
db.on('query-response', (response, data) => {
  const duration = Date.now() - data.__start;
  dbQueryDuration.labels(data.sql.slice(0, 50)).observe(duration);
  if (duration > 500) logger.warn({ sql: data.sql, duration }, '慢 SQL');
});
```

**2. 运行时监控**

```js
// 事件循环延迟
const { monitorEventLoopDelay } = require('perf_hooks');
const h = monitorEventLoopDelay({ resolution: 20 });
h.enable();
setInterval(() => { eventLoopLag.set(h.percentile(99)); }, 5000);

// GC 监控
const { PerformanceObserver } = require('perf_hooks');
new PerformanceObserver((list) => {
  list.getEntries().forEach((e) => gcTime.observe(e.duration));
}).observe({ entryTypes: ['gc'] });

// 内存
setInterval(() => {
  const m = process.memoryUsage();
  heapUsed.set(m.heapUsed);
  heapTotal.set(m.heapTotal);
}, 5000);
```

**3. 系统层**：用 `node_exporter` 采集 CPU、内存、磁盘、网络

**4. 链路追踪**：OpenTelemetry SDK 注入 traceId，跨服务透传，定位慢在哪个环节

```
请求 → API 网关(traceId生成) → 服务A → 服务B → DB
        ↓每个环节上报 span
   Jaeger 展示调用树 + 各段耗时
```

**5. 告警规则**：
- P99 RT > 500ms 持续 3 分钟
- 事件循环 lag > 100ms
- 错误率 > 1%
- 堆内存 > 80% 上限

**评分要点**：
- ✅ 三层监控分层清晰（必备）
- ✅ 事件循环 lag + GC + 内存监控（必备）
- ✅ 慢接口 + 慢 SQL 定位（必备）
- ✅ OpenTelemetry / traceId 全链路（加分）
- ✅ 告警规则设计（加分）

---

## 第三篇 工程化篇

### Q3.1【基础概念题】请对比 CommonJS 和 ES Modules 在 Node.js 中的差异，并说明混合使用时的兼容性问题。

**参考答案**：

| 维度 | CommonJS (CJS) | ES Modules (ESM) |
| --- | --- | --- |
| 加载时机 | 运行时（动态） | 编译时（静态分析） |
| 是否同步 | 同步 `require` | 异步 `import` |
| `this` 顶层 | `module.exports` | `undefined` |
| `__dirname`/`__filename` | 内置 | 需用 `import.meta.url` 模拟 |
| 循环依赖 | 返回已执行部分（部分对象） | 引用绑定，可能 TDZ 报错 |
| Tree-shaking | 不支持 | 支持 |
| 顶层 `await` | 不支持 | 支持 |
| 动态导入 | `require` | `import()` |

**混合使用的兼容性**：

```js
// ✅ ESM 中导入 CJS（用 default）
// app.mjs
import pkg from 'cjs-package'; // pkg = module.exports
const { named } = pkg;

// ⚠️ CJS 中导入 ESM（必须用 async import）
// app.cjs
const esm = await import('./esm-module.mjs');

// ❌ 不支持：CJS 中静态 import ESM 命名导出
// （Node 22+ 实验性支持 require(esm)）
```

**循环依赖差异**：
```js
// CJS：循环引用时返回部分执行结果
// a.js
const b = require('./b');
console.log(b.x); // 可能是 undefined（b 还没执行到赋值）
module.exports = { x: 1 };

// ESM：循环引用时返回绑定（live binding），可能 TDZ
// a.mjs
import { x } from './b.mjs'; // x 是绑定，访问时若 b 未初始化则 ReferenceError
export const y = x;
```

**评分要点**：
- ✅ 列出 5+ 维度差异（必备）
- ✅ 准确说明混合导入规则（必备）
- ✅ 循环依赖行为差异（加分）
- ✅ 提到 Node 22 `require(esm)` 实验特性（高级）

---

### Q3.2【原理分析题】请描述 `require` 模块加载的完整流程，包括缓存、路径解析、扩展名查找、目录加载等。

**参考答案**：

`require(X)` 的完整流程（Node.js 官方文档规范）：

**1. 缓存检查**：先查 `require.cache`，命中直接返回 `module.exports`

**2. 路径解析**（`Module._resolveFilename`）：

- 若 `X` 是**核心模块**（如 `fs`、`http`）：直接返回
- 若 `X` 以 `./` `/` `../` 开头（**相对/绝对路径**）：
  1. 尝试 `X` 作为文件：`X` 本身、`X.js`、`X.json`、`X.node`
  2. 尝试 `X` 作为目录：`X/package.json` 的 `main` 字段、`X/index.js`、`X/index.json`、`X/index.node`
- 若 `X` **无路径前缀**（第三方包）：
  - 从当前目录 `node_modules` 查找，逐级向上到根目录
  - 命中后按"目录加载"规则
  - 支持 `exports` 字段（现代包）做子路径映射

**3. 编译执行**（`Module._compile`）：
- 把模块代码包装进函数：
  ```js
  (function (exports, require, module, __filename, __dirname) {
    // 模块代码
  });
  ```
- 用 V8 编译执行，传入 5 个参数
- `module.exports` 作为返回值

**4. 缓存写入**：执行后把 `module` 写入 `require.cache[filename]`

**关键细节**：
- **缓存键是绝对路径**：不同路径引用同一文件会缓存同一对象
- **首次加载同步阻塞**：所以 `require` 必须在模块顶层用，避免运行时阻塞
- **JSON 模块**：`require('./data.json')` 自动 `JSON.parse`
- **`require.extensions`**：可注册自定义扩展名处理器（已弃用但可用）

**评分要点**：
- ✅ 完整描述四步流程（必备）
- ✅ 准确说明文件 → 目录 → node_modules 查找顺序（必备）
- ✅ 提到模块代码包装函数及 5 个参数（加分）
- ✅ 提到 `exports` 字段、缓存键是绝对路径（加分）

---

### Q3.3【实践应用题】如何为一个大型 Node.js Monorepo 设计构建、依赖管理、发布流程？请给出技术选型和关键配置。

**参考答案**：

**技术选型**：
- **包管理**：`pnpm`（硬链接节省磁盘、严格依赖、workspace 支持）
- **Monorepo 工具**：`pnpm workspace` + `Turborepo`（增量构建 + 远程缓存）
- **构建**：`tsup`（基于 esbuild，TS→CJS/ESM 双格式）
- **代码规范**：`ESLint` + `Prettier` + `Commitlint` + `Husky`
- **测试**：`Vitest`（兼容 Jest API、原生 ESM、快）
- **发布**：`Changesets`（管理版本 + CHANGELOG + 发布）

**目录结构**：
```
my-monorepo/
├── packages/
│   ├── core/           # 核心库
│   ├── utils/          # 工具库
│   └── cli/            # CLI 工具
├── apps/
│   ├── web/            # 前端
│   └── api/            # 后端
├── pnpm-workspace.yaml
├── turbo.json
├── .changeset/
└── package.json
```

**关键配置**：

```yaml
# pnpm-workspace.yaml
packages:
  - 'packages/*'
  - 'apps/*'
```

```json
// turbo.json - 增量构建 + 缓存
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    },
    "test": { "dependsOn": ["build"] },
    "lint": {}
  }
}
```

```json
// packages/core/package.json - 双格式发布
{
  "name": "@my/core",
  "version": "1.0.0",
  "main": "./dist/index.cjs",
  "module": "./dist/index.mjs",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs"
    }
  },
  "files": ["dist"]
}
```

**发布流程**（Changesets）：
1. 开发者改代码后 `npx changeset` 描述变更（patch/minor/major + 说明）
2. PR 合并后自动生成 `.changeset/*.md`
3. CI 跑 `changeset version`：根据变更更新各包版本 + CHANGELOG
4. `changeset publish`：发布到 npm，自动打 git tag

**评分要点**：
- ✅ 选 pnpm + Turborepo（必备）
- ✅ 双格式（CJS+ESM）发布配置（必备）
- ✅ Changesets 版本管理（加分）
- ✅ 增量构建 + 缓存机制（必备）
- ✅ 提到依赖隔离、严格依赖（加分）

**真实项目案例**：
- **项目背景**：公司组件库 + 工具库 + 业务应用共 30+ 包，原多仓库协作成本高
- **技术选型原因**：pnpm 节省 70% 磁盘、Turborepo 缓存让 CI 从 12 分钟降到 3 分钟
- **挑战**：循环依赖；解决：`madge` 检测 + 重构拆分
- **最终效果**：发布频率从每周 1 次到每天多次，跨包联调零等待

---

### Q3.4【场景设计题】设计一个 Node.js 服务的 CI/CD 流程，要求：代码提交即测试、灰度发布、可一键回滚、具备一定安全合规（依赖扫描、镜像扫描）。

**参考答案**：

**CI/CD 流水线**（以 GitLab CI / GitHub Actions 为例）：

```
代码提交 → Lint → 单测 → 构建 → 安全扫描 → 镜像构建 → 推送仓库 → 灰度部署 → 全量 → 监控
                                                                                      ↓
                                                                                   异常回滚
```

**1. CI 阶段（提交触发）**

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm typecheck
      - run: pnpm test:coverage
      - run: pnpm build

  security:
    needs: test
    steps:
      - run: pnpm audit --audit-level=high
      - uses: snyk/actions/node@master
      - uses: aquasecurity/trivy-action@master
        with: { image: 'myapp:${{ github.sha }}' }
```

**2. CD 阶段（构建镜像 + 灰度）**

```dockerfile
# 多阶段构建，生产镜像最小化
FROM node:20-alpine AS builder
WORKDIR /app
COPY pnpm-lock.yaml package.json ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
USER node
EXPOSE 3000
HEALTHCHECK CMD wget -qO- http://localhost:3000/health || exit 1
CMD ["node", "dist/main.js"]
```

**3. 灰度发布**（K8s + Argo Rollouts）：
```yaml
strategy:
  canary:
    steps:
      - setWeight: 10
      - pause: { duration: 10m }
      - setWeight: 30
      - pause: { duration: 5m }
      - setWeight: 100
```

**4. 一键回滚**：
- 保留最近 5 个版本镜像
- `kubectl rollout undo deployment/myapp`
- 数据库变更需向前兼容（双写期 + 兼容期）

**5. 安全合规**：
- 依赖扫描：`pnpm audit` + Snyk
- 镜像扫描：Trivy（CVE 漏洞）
- 密钥管理：Vault / Sealed Secrets，不入镜像
- 镜像签名：Cosign 签名防篡改
- 最小权限：Pod 用非 root、只读根文件系统

**评分要点**：
- ✅ 完整流水线：lint/test/build/scan/deploy（必备）
- ✅ 多阶段 Docker 构建 + 非 root（必备）
- ✅ 灰度发布 + 自动回滚（必备）
- ✅ 依赖扫描 + 镜像扫描（必备）
- ✅ 数据库向前兼容的回滚策略（加分）

---

### Q3.5【场景设计题】如何设计一个 Node.js 微服务的可观测性体系？要求覆盖日志、指标、链路追踪三支柱，并说明三者如何关联。

**参考答案**：

**可观测性三支柱**：

```
┌────────── 日志 (Logs) ──────────┐
│  离散事件、文本/JSON、带上下文    │  工具：pino → Filebeat → Kafka → ES
├────────── 指标 (Metrics) ───────┤
│  时序数值、聚合、告警             │  工具：prom-client → Prometheus → Grafana
├────────── 追踪 (Traces) ────────┤
│  请求链路、 span 树、依赖关系     │  工具：OpenTelemetry → Jaeger/Tempo
└─────────────────────────────────┘
              ↓
         统一 traceId 关联
```

**1. 日志**：
```js
const pino = require('pino');
const logger = pino();
app.use((ctx, next) => {
  const span = trace.getActiveSpan();
  ctx.logger = logger.child({
    traceId: span?.spanContext().traceId,
    spanId: span?.spanContext().spanId,
  });
  await next();
});
```

**2. 指标**（prom-client）：
```js
const client = require('prom-client');
const httpRequestDuration = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP 请求耗时',
  labelNames: ['method', 'route', 'status'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 5],
});
app.use(async (ctx, next) => {
  const start = Date.now();
  await next();
  httpRequestDuration.labels(ctx.method, ctx.route, ctx.status)
    .observe((Date.now() - start) / 1000);
});
app.get('/metrics', async (ctx) => {
  ctx.body = await client.register.metrics();
});
```

**3. 链路追踪**（OpenTelemetry）：
```js
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({ url: 'http://otel-collector:4318/v1/traces' }),
  instrumentations: [httpInstrumentation, expressInstrumentation, knexInstrumentation],
});
sdk.start();
// 自动给 HTTP、DB、Redis 调用打 span，traceId 跨服务透传
```

**三者关联**：用**统一的 traceId** 串联：
- 日志中带 traceId → 在 Jaeger 看到 trace 后，用 traceId 查 ES 拿到该请求所有日志
- 指标中的 exemplar 关联 traceId → Grafana 中点某个高延迟点直接跳到对应 trace
- 排查流程：告警（指标异常）→ 找 trace（定位慢在哪个环节）→ 看日志（具体错误）

**评分要点**：
- ✅ 三支柱定义清晰（必备）
- ✅ 各自技术选型（pino/prom-client/OTel）（必备）
- ✅ traceId 关联三者（核心）
- ✅ 排查流程串联（指标→trace→日志）（加分）

---

## 第四篇 异步编程与并发控制篇

### Q4.1【基础概念题】`process.nextTick`、`setImmediate`、`setTimeout(fn, 0)` 三者的区别和执行顺序。

**参考答案**：

| API | 所属 | 执行阶段 | 优先级 |
| --- | --- | --- | --- |
| `process.nextTick` | Node 私有 | 每个阶段切换间（微任务，最高优先级） | 最高 |
| `Promise.then` | JS 标准 | 每个阶段切换间（微任务，仅次于 nextTick） | 次高 |
| `setImmediate` | Node | check 阶段 | 较低 |
| `setTimeout(fn, 0)` | JS 标准 | timers 阶段 | 较低 |

**执行顺序规律**：
1. **微任务永远优先于宏任务**：nextTick > Promise > setImmediate/setTimeout
2. **nextTick 优先于 Promise**：nextTick 队列清空后才清 Promise 队列
3. **主模块中 setTimeout(0) 与 setImmediate 顺序不确定**：取决于 1ms 计时器是否已触发
4. **I/O 回调中 setImmediate 一定先于 setTimeout(0)**：poll 阶段后必进 check，再到下轮 timers

```js
// I/O 回调中顺序确定
fs.readFile('./file', () => {
  setTimeout(() => console.log('timeout'), 0);
  setImmediate(() => console.log('immediate'));
  // 一定输出：immediate, timeout
});
```

**陷阱**：递归调用 `process.nextTick` 会饿死 I/O，因为每次清空 nextTick 后又产生新的，永远进不到 poll 阶段。

**评分要点**：
- ✅ 四者阶段归属准确（必备）
- ✅ nextTick > Promise 优先级（必备）
- ✅ I/O 回调中 setImmediate 必先（必备）
- ✅ 提到 nextTick 饿死 I/O 陷阱（加分）

---

### Q4.2【原理分析题】Promise 的状态机是如何实现的？请手写一个符合 Promise/A+ 规范的 Promise（核心部分）。

**参考答案**：

**状态机要点**：
- 三态：`pending` → `fulfilled` / `rejected`，状态一旦改变不可逆
- `then` 返回新 Promise，实现链式调用
- 值穿透：`then` 非函数参数被忽略，值向下传递
- 异步执行：`then` 回调必须异步执行（微任务）

**手写 Promise（核心）**：

```js
const PENDING = 'pending';
const FULFILLED = 'fulfilled';
const REJECTED = 'rejected';

class MyPromise {
  constructor(executor) {
    this.state = PENDING;
    this.value = undefined;
    this.reason = undefined;
    this.onFulfilledCbs = [];
    this.onRejectedCbs = [];

    const resolve = (value) => {
      if (this.state !== PENDING) return;
      if (value instanceof MyPromise) {
        return value.then(resolve, reject);
      }
      this.state = FULFILLED;
      this.value = value;
      this.onFulfilledCbs.forEach((fn) => fn());
    };
    const reject = (reason) => {
      if (this.state !== PENDING) return;
      this.state = REJECTED;
      this.reason = reason;
      this.onRejectedCbs.forEach((fn) => fn());
    };
    try {
      executor(resolve, reject);
    } catch (err) {
      reject(err);
    }
  }

  then(onFulfilled, onRejected) {
    onFulfilled = typeof onFulfilled === 'function' ? onFulfilled : (v) => v;
    onRejected = typeof onRejected === 'function' ? onRejected : (e) => { throw e; };

    const promise2 = new MyPromise((resolve, reject) => {
      const handle = (cb, value) => {
        queueMicrotask(() => {
          try {
            const x = cb(value);
            if (x instanceof MyPromise) x.then(resolve, reject);
            else resolve(x);
          } catch (err) {
            reject(err);
          }
        });
      };

      if (this.state === FULFILLED) handle(onFulfilled, this.value);
      else if (this.state === REJECTED) handle(onRejected, this.reason);
      else {
        this.onFulfilledCbs.push(() => handle(onFulfilled, this.value));
        this.onRejectedCbs.push(() => handle(onRejected, this.reason));
      }
    });
    return promise2;
  }

  catch(fn) { return this.then(null, fn); }
  static resolve(v) { return v instanceof MyPromise ? v : new MyPromise((r) => r(v)); }
  static reject(e) { return new MyPromise((_, r) => r(e)); }
  static all(promises) {
    return new MyPromise((resolve, reject) => {
      const result = [];
      let count = 0;
      promises.forEach((p, i) => {
        MyPromise.resolve(p).then((v) => {
          result[i] = v;
          if (++count === promises.length) resolve(result);
        }, reject);
      });
    });
  }
}
```

**评分要点**：
- ✅ 三态 + 不可逆（必备）
- ✅ then 返回新 Promise 实现链式（必备）
- ✅ 回调异步执行（微任务）（必备）
- ✅ 处理 thenable / 值穿透（加分）
- ✅ 提到 Promise/A+ 解决程序 `resolvePromise`（高级）

---

### Q4.3【实践应用题】请实现一个带并发限制、超时、重试、熔断的批量异步任务执行器。

**参考答案**：

```js
class ResilientExecutor {
  constructor({
    concurrency = 5,
    timeout = 5000,
    retries = 3,
    retryDelay = 1000,
    circuitThreshold = 5,
    circuitResetTime = 30000,
  } = {}) {
    this.concurrency = concurrency;
    this.timeout = timeout;
    this.retries = retries;
    this.retryDelay = retryDelay;
    this.circuitThreshold = circuitThreshold;
    this.circuitResetTime = circuitResetTime;
    this.activeCount = 0;
    this.queue = [];
    this.failCount = 0;
    this.circuitOpen = false;
    this.circuitOpenAt = 0;
  }

  withTimeout(promiseFn) {
    return () =>
      new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error('Timeout')), this.timeout);
        promiseFn().then(
          (v) => { clearTimeout(timer); resolve(v); },
          (e) => { clearTimeout(timer); reject(e); }
        );
      });
  }

  async runWithRetry(task) {
    let lastErr;
    for (let i = 0; i <= this.retries; i++) {
      try {
        const result = await this.withTimeout(task)();
        this.failCount = 0;
        return result;
      } catch (err) {
        lastErr = err;
        if (i < this.retries) {
          await new Promise((r) => setTimeout(r, this.retryDelay * (i + 1)));
        }
      }
    }
    this.failCount++;
    if (this.failCount >= this.circuitThreshold) {
      this.circuitOpen = true;
      this.circuitOpenAt = Date.now();
    }
    throw lastErr;
  }

  checkCircuit() {
    if (this.circuitOpen) {
      if (Date.now() - this.circuitOpenAt > this.circuitResetTime) {
        this.circuitOpen = false;
        this.failCount = 0;
      } else {
        throw new Error('Circuit breaker open');
      }
    }
  }

  add(task) {
    return new Promise((resolve, reject) => {
      const run = async () => {
        try {
          this.checkCircuit();
          this.activeCount++;
          const result = await this.runWithRetry(task);
          resolve(result);
        } catch (err) {
          reject(err);
        } finally {
          this.activeCount--;
          this.next();
        }
      };
      if (this.activeCount < this.concurrency) run();
      else this.queue.push(run);
    });
  }

  next() {
    if (this.queue.length && this.activeCount < this.concurrency) {
      this.queue.shift()();
    }
  }
}

// 使用
const executor = new ResilientExecutor({ concurrency: 10, timeout: 3000, retries: 2 });
const results = await Promise.allSettled(
  urls.map((url) => executor.add(() => fetch(url)))
);
```

**评分要点**：
- ✅ 并发限制（必备）
- ✅ 超时 + 重试 + 指数退避（必备）
- ✅ 熔断器（开/半开/关三态）（加分）
- ✅ 代码健壮性（错误处理、资源释放）（必备）

**真实项目案例**：
- **项目背景**：第三方短信/支付网关调用，下游偶发抖动 + 限流
- **技术选型**：自研执行器比 opossum 等库更贴合业务（需定制退避策略）
- **挑战**：熔断半开时大量请求涌入再次打垮；解决：半开态只放 10% 试探
- **最终效果**：下游故障时业务方 5 秒内熔断降级，不再雪崩

---

### Q4.4【场景设计题】你的服务需要从 Kafka 消费消息并写库，要求：不丢消息、不重复消费、能扛突发流量（背压）。请设计完整方案。

**参考答案**：

**方案设计**：

**1. 不丢消息——手动提交 offset**
```js
consumer.run({
  eachMessage: async ({ topic, partition, message }) => {
    try {
      await processMessage(message);
      await consumer.commitOffsets([{ topic, partition, offset: message.offset }]);
    } catch (err) {
      logger.error({ err, offset: message.offset }, '处理失败，不提交，下次重投');
    }
  },
});
```

**2. 不重复消费——幂等 + 唯一约束**
```sql
ALTER TABLE orders ADD UNIQUE KEY uk_msg_id (msg_id);
```
```js
async function processMessage(message) {
  const msgId = message.key.toString();
  await db.query('INSERT IGNORE INTO orders (msg_id, ...) VALUES (?)', [msgId, ...]);
}
```

**3. 背压控制——限制并发 + 暂停消费**
```js
let inflight = 0;
const MAX_INFLIGHT = 100;

consumer.run({
  eachMessage: async ({ message }) => {
    inflight++;
    if (inflight >= MAX_INFLIGHT) consumer.pause();
    try {
      await processMessage(message);
      await consumer.commitOffsets([...]);
    } finally {
      inflight--;
      if (inflight < MAX_INFLIGHT * 0.8) consumer.resume();
    }
  },
});
```

**4. 突发流量——批量处理 + 异步落库**
```js
let batch = [];
const FLUSH_SIZE = 50;
async function processMessage(message) {
  batch.push(message);
  if (batch.length >= FLUSH_SIZE) await flush();
}
async function flush() {
  if (!batch.length) return;
  const items = batch.splice(0);
  await db.batchInsert(items);
}
setInterval(flush, 1000);
```

**5. 死信队列**：处理失败超过 N 次的消息投到 DLQ，人工介入

**6. 优雅关闭**：收到 SIGTERM 后停止拉取 → 处理完 inflight → 提交 offset → 退出

**评分要点**：
- ✅ 手动提交 offset 实现不丢（必备）
- ✅ 幂等 + 唯一约束实现不重复（必备）
- ✅ 背压（pause/resume 或队列限流）（必备）
- ✅ 批量落库提升吞吐（加分）
- ✅ 死信队列 + 优雅关闭（加分）

---

### Q4.5【场景设计题】设计一个分布式定时任务系统，要求：任务不重复执行、故障自动转移、可动态调整、有执行日志和重试。

**参考答案**：

**方案：Redis 分布式锁 + 任务表 + 多 Worker**

```
┌─── 调度器（多实例，抢锁成为 leader）───┐
│  1. 扫任务表，到点的任务              │
│  2. Redis SETNX 抢锁（防多实例重复）  │
│  3. 投递到任务队列                    │
└────────────────────────────────────┘
              ↓
┌─── Worker 池（多实例）─────────────┐
│  1. 从队列拉任务                   │
│  2. 执行业务逻辑                   │
│  3. 写执行日志 + 更新任务状态       │
│  4. 失败重试（指数退避）            │
└────────────────────────────────────┘
```

**核心实现**：

```js
// 1. Leader 选举（Redis 分布式锁）
const REDLOCK = require('redlock');
const redlock = new REDLOCK([redisClient]);
async function tryAcquireLeader() {
  try {
    const lock = await redlock.lock('scheduler:leader', 10000);
    return lock;
  } catch {
    return null;
  }
}

// 2. 任务表结构
// CREATE TABLE jobs (
//   id, name, cron, payload, next_run_at,
//   status, retry_count, max_retries, ...
// );

// 3. 调度循环
async function scheduleLoop() {
  const lock = await tryAcquireLeader();
  if (!lock) return;
  try {
    const due = await db.query(
      'SELECT * FROM jobs WHERE next_run_at <= NOW() AND status = "pending" FOR UPDATE SKIP LOCKED'
    );
    for (const job of due) {
      await db.query('UPDATE jobs SET status="running", next_run_at=? WHERE id=?', [
        nextCronTime(job.cron), job.id
      ]);
      await queue.push('jobs', job);
    }
  } finally {
    await lock.unlock();
  }
}

// 4. Worker 执行
async function executeJob(job) {
  const logId = await db.insert('job_logs', { job_id: job.id, start: new Date() });
  try {
    await handlers[job.name](job.payload);
    await db.update('job_logs', logId, { status: 'success', end: new Date() });
    await db.update('jobs', job.id, { status: 'pending', retry_count: 0 });
  } catch (err) {
    await db.update('job_logs', logId, { status: 'failed', error: err.message });
    if (job.retry_count < job.max_retries) {
      await db.update('jobs', job.id, {
        retry_count: job.retry_count + 1,
        next_run_at: new Date(Date.now() + 2 ** job.retry_count * 1000),
      });
    } else {
      await notifyAlert(job, err);
    }
  }
}
```

**关键设计点**：
- **不重复执行**：Leader 锁 + DB `FOR UPDATE SKIP LOCKED` + 任务状态机
- **故障转移**：Leader 锁 TTL 10s，崩溃后其他实例自动接管
- **动态调整**：管理后台改 `jobs` 表，调度器下轮生效
- **重试**：指数退避，超阈值告警
- **日志**：`job_logs` 表记录每次执行

**技术选型对比**：

| 方案 | 适用场景 |
| --- | --- |
| Redis 锁 + 自研 | 中小规模，灵活 |
| BullMQ | 单 Redis 即可，社区成熟 |
| XXL-JOB | 中心化调度，Java 生态 |
| Kubernetes CronJob | 容器化，简单任务 |

**评分要点**：
- ✅ 分布式锁防重复（必备）
- ✅ Leader 选举 + 故障转移（必备）
- ✅ DB 任务表 + 状态机（必备）
- ✅ 重试 + 告警 + 日志（必备）
- ✅ 对比成熟方案选型（加分）

---

## 第五篇 流与数据处理篇

### Q5.1【基础概念题】请说明 Stream 的四种类型，以及 pipe 背压（backpressure）的工作原理。

**参考答案**：

**四种 Stream 类型**：

| 类型 | 说明 | 示例 |
| --- | --- | --- |
| **Readable** 可读流 | 可从中读取数据 | `fs.createReadStream`、HTTP 请求体 |
| **Writable** 可写流 | 可向其写入数据 | `fs.createWriteStream`、HTTP 响应 |
| **Duplex** 双工流 | 同时可读可写（两个独立通道） | TCP Socket |
| **Transform** 转换流 | 读写间转换数据 | `zlib.createGzip()`、加密流 |

**背压（Backpressure）原理**：

当生产者（Readable）速度 > 消费者（Writable）速度时，数据会在 Writable 的内部缓冲区堆积，可能导致内存溢出。背压机制通过反馈让生产者暂停：

1. Writable 有 `highWaterMark`（高水位线，默认 64KB / 对象流 16 个）
2. `writable.write(chunk)` 返回 `false` 表示缓冲区已超水位线
3. Readable 监听 Writable 的 `'drain'` 事件（缓冲区排空），暂停/恢复读取
4. `pipe()` 内部自动处理背压：

```js
// pipe 内部等价实现
readable.on('data', (chunk) => {
  const ok = writable.write(chunk);
  if (!ok) readable.pause();
});
writable.on('drain', () => readable.resume());
readable.on('end', () => writable.end());
```

**⚠️ 不处理背压的后果**：内存堆积 → OOM。手动 `on('data')` 不暂停就会内存泄漏。

**评分要点**：
- ✅ 四类型准确（必备）
- ✅ highWaterMark + write 返回 false 机制（必备）
- ✅ drain 事件恢复（必备）
- ✅ 提到手动 on('data') 不处理的后果（加分）

---

### Q5.2【原理分析题】请实现一个自定义 Transform 流，用于行处理：把输入流按行切分，对每行做转换后输出。要求正确处理跨 chunk 的行。

**参考答案**：

```js
const { Transform } = require('stream');

class LineTransform extends Transform {
  constructor(transformFn, options) {
    super({ ...options, readableObjectMode: false, writableObjectMode: false });
    this.transformFn = transformFn;
    this.remainder = ''; // 跨 chunk 的不完整行
  }

  _transform(chunk, encoding, callback) {
    const text = this.remainder + chunk.toString();
    const lines = text.split('\n');
    this.remainder = lines.pop(); // 最后一段可能不完整，留着下次拼

    for (const line of lines) {
      const result = this.transformFn(line);
      if (result != null) this.push(result + '\n');
    }
    callback();
  }

  _flush(callback) {
    if (this.remainder) {
      const result = this.transformFn(this.remainder);
      if (result != null) this.push(result + '\n');
    }
    callback();
  }
}

// 使用：把日志文件每行转大写
const fs = require('fs');
fs.createReadStream('./log.txt')
  .pipe(new LineTransform((line) => line.toUpperCase()))
  .pipe(fs.createWriteStream('./log-upper.txt'));
```

**关键点**：
1. **跨 chunk 处理**：用 `remainder` 保存不完整行，下次拼接
2. **`_flush`**：流结束时处理最后的剩余数据
3. **对象模式**：若输出对象，需 `readableObjectMode: true`

**进阶**：Node 内置 `readline` 模块更适合按行读取：
```js
const readline = require('readline');
const rl = readline.createInterface({ input: fs.createReadStream('./log.txt') });
rl.on('line', (line) => console.log(line.toUpperCase()));
```

**评分要点**：
- ✅ 用 remainder 处理跨 chunk（核心）
- ✅ _flush 处理结尾（必备）
- ✅ 提到 readline 内置方案（加分）

---

### Q5.3【实践应用题】请实现一个支持断点续传的文件上传服务：客户端可中断后继续上传，服务端校验完整性。

**参考答案**：

**方案：分片上传 + 秒传 + 断点续传**

**1. 协议设计**：
```
POST /upload/init        → 返回 uploadId，检查是否已存在（秒传）
POST /upload/:id/chunk   → 上传分片（带序号 + hash）
POST /upload/:id/complete→ 合并所有分片，校验 hash
GET  /upload/:id/status  → 查询已上传分片（断点续传）
```

**2. 服务端实现**：

```js
const express = require('express');
const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');
const multer = require('multer');

const app = express();
const UPLOAD_DIR = './uploads';
const CHUNK_DIR = './chunks';

// 初始化：检查秒传 + 创建上传会话
app.post('/upload/init', async (req, res) => {
  const { fileHash, size, name } = req.body;
  const existFile = path.join(UPLOAD_DIR, fileHash);
  if (await exists(existFile)) {
    return res.json({ code: 'INSTANT', url: `/files/${fileHash}` });
  }
  const uploadId = crypto.randomUUID();
  await fs.mkdir(path.join(CHUNK_DIR, uploadId), { recursive: true });
  res.json({ code: 'NEW', uploadId });
});

// 查询已上传分片（断点续传）
app.get('/upload/:id/status', async (req, res) => {
  const dir = path.join(CHUNK_DIR, req.params.id);
  if (!(await exists(dir))) return res.json({ chunks: [] });
  const chunks = await fs.readdir(dir);
  res.json({ chunks: chunks.sort((a, b) => +a - +b) });
});

// 上传分片
app.post('/upload/:id/chunk', multer().single('chunk'), async (req, res) => {
  const { index, hash } = req.body;
  const chunkPath = path.join(CHUNK_DIR, req.params.id, index);
  const buf = req.file.buffer;
  const actualHash = crypto.createHash('md5').update(buf).digest('hex');
  if (actualHash !== hash) return res.status(400).json({ err: 'chunk corrupt' });
  await fs.writeFile(chunkPath, buf);
  res.json({ ok: true });
});

// 合并 + 校验
app.post('/upload/:id/complete', async (req, res) => {
  const { fileHash } = req.body;
  const dir = path.join(CHUNK_DIR, req.params.id);
  const chunks = (await fs.readdir(dir)).sort((a, b) => +a - +b);
  const dest = path.join(UPLOAD_DIR, fileHash);
  const hash = crypto.createHash('md5');
  const ws = fs.createWriteStream(dest);
  for (const c of chunks) {
    const buf = await fs.readFile(path.join(dir, c));
    hash.update(buf);
    ws.write(buf);
  }
  ws.end();
  await new Promise((r) => ws.on('finish', r));
  if (hash.digest('hex') !== fileHash) {
    await fs.unlink(dest);
    return res.status(400).json({ err: 'file corrupt' });
  }
  await fs.rm(dir, { recursive: true });
  res.json({ url: `/files/${fileHash}` });
});
```

**评分要点**：
- ✅ 分片上传协议设计（必备）
- ✅ 秒传（hash 检查）（必备）
- ✅ 断点续传（查询已传分片）（必备）
- ✅ 分片 + 整体 hash 校验（必备）
- ✅ 流式合并避免内存爆（加分）

---

### Q5.4【场景设计题】设计一个支持 TB 级 CSV 文件处理的 Node.js 服务：读取、转换、入库，要求内存占用稳定 < 500MB。

**参考答案**：

**方案：流式管道 + 批量入库 + 背压**

```
S3/文件 → ReadStream → CSV解析(流) → Transform(清洗) → 批量攒批 → DB批量插入
```

**1. 流式 CSV 解析**：用 `csv-parser` 或 `papaparse` 流式版
```js
const csv = require('csv-parser');
fs.createReadStream('huge.csv')
  .pipe(csv())
  .on('data', (row) => { /* 行数据 */ })
```

**2. Transform 清洗**：
```js
const { Transform } = require('stream');
const cleanTransform = new Transform({
  objectMode: true,
  transform(row, enc, cb) {
    const cleaned = {
      name: row.name?.trim(),
      price: Number(row.price) || 0,
      date: new Date(row.date),
    };
    if (cleaned.name) this.push(cleaned);
    cb();
  },
});
```

**3. 批量攒批 + 入库**（处理背压）：
```js
class BatchInsert extends Transform {
  constructor(size = 1000) {
    super({ objectMode: true });
    this.batch = [];
    this.size = size;
  }
  async _transform(row, enc, cb) {
    this.batch.push(row);
    if (this.batch.length >= this.size) await this.flush();
    cb();
  }
  async _flush(cb) {
    await this.flush();
    cb();
  }
  async flush() {
    if (!this.batch.length) return;
    const items = this.batch.splice(0);
    for (let i = 0; i < 3; i++) {
      try {
        await db.batchInsert(items);
        return;
      } catch (err) {
        if (i === 2) throw err;
        await sleep(1000 * (i + 1));
      }
    }
  }
}
```

**4. 完整管道**：
```js
fs.createReadStream('huge.csv')
  .pipe(csv())
  .pipe(cleanTransform)
  .pipe(new BatchInsert(1000))
  .on('finish', () => console.log('完成'))
  .on('error', (err) => console.error(err));
```

**5. 内存控制**：
- `highWaterMark` 调小（如 16 个对象），让背压及时生效
- 用 `--max-old-space-size=512` 限制堆
- 监控 `process.memoryUsage()`，超阈值告警

**6. 断点续传**：记录已处理行号到 Redis，重启从该行续传（`fs.createReadStream({ start: byteOffset })`）

**7. 分布式处理**：TB 级单机不够，按文件分片到多个 worker 并行：
- 用 `split` 命令按行切分
- 每个 worker 处理一个分片
- 结果汇总

**评分要点**：
- ✅ 全链路流式（必备）
- ✅ objectMode Transform 清洗（必备）
- ✅ 批量入库 + 重试（必备）
- ✅ 背压 + 内存控制（必备）
- ✅ 断点续传 / 分布式分片（加分）

---

## 第六篇 Web 服务与网络篇

### Q6.1【基础概念题】HTTP/1.1、HTTP/2、HTTP/3 的核心区别？Node.js 如何启用 HTTP/2？

**参考答案**：

| 特性 | HTTP/1.1 | HTTP/2 | HTTP/3 |
| --- | --- | --- | --- |
| 传输层 | TCP | TCP | QUIC（UDP） |
| 多路复用 | ❌（队头阻塞） | ✅ | ✅（无 TCP 队头阻塞） |
| 二进制分帧 | ❌ 文本 | ✅ | ✅ |
| 头部压缩 | ❌ | ✅ HPACK | ✅ QPACK |
| 服务端推送 | ❌ | ✅（已逐步弃用） | ✅ |
| 连接建立 | 多次 RTT | 1-RTT（TLS 1.3） | 0-RTT/1-RTT |
| 队头阻塞 | 有（应用层 + TCP） | 有（TCP 层） | 无 |

**Node.js 启用 HTTP/2**：

```js
const http2 = require('http2');
const fs = require('fs');

const server = http2.createSecureServer({
  key: fs.readFileSync('server.key'),
  cert: fs.readFileSync('server.crt'),
});

server.on('stream', (stream, headers) => {
  stream.respond({
    'content-type': 'text/html; charset=utf-8',
    ':status': 200,
  });
  stream.end('<h1>Hello HTTP/2</h1>');
});

server.listen(8443, () => console.log('HTTP/2 on 8443'));
```

**注意**：HTTP/2 必须基于 TLS（h2），明文版 h2c 浏览器不支持。生产环境通常由 Nginx 终结 TLS 并代理到 Node。

**评分要点**：
- ✅ 三版核心差异（多路复用、队头阻塞、传输层）（必备）
- ✅ HTTP/2 必须基于 TLS（必备）
- ✅ Node http2 模块基本用法（必备）
- ✅ 提到 Nginx 终结 TLS 的生产实践（加分）

---

### Q6.2【原理分析题】请描述 TCP 三次握手和四次挥手，以及为什么需要 TIME_WAIT 状态。在 Node.js 高并发服务中如何优化连接？

**参考答案**：

**三次握手（建立连接）**：
1. 客户端 → SYN → 服务端（客户端进入 SYN_SENT）
2. 服务端 → SYN+ACK → 客户端（服务端进入 SYN_RCVD）
3. 客户端 → ACK → 服务端（双方 ESTABLISHED）

**为什么三次**：防止历史失效的连接请求重新到达服务端导致资源浪费。两次握无法确认客户端的接收能力。

**四次挥手（断开连接）**：
1. 主动方 → FIN → 被动方（主动方 FIN_WAIT_1）
2. 被动方 → ACK → 主动方（主动方 FIN_WAIT_2，被动方 CLOSE_WAIT）
3. 被动方 → FIN → 主动方（被动方 LAST_ACK）
4. 主动方 → ACK → 被动方（主动方 TIME_WAIT，2MSL 后 CLOSED）

**为什么四次**：TCP 全双工，每个方向需独立关闭。被动方收到 FIN 后可能还有数据要发，故先 ACK，发完再 FIN。

**TIME_WAIT 存在原因**（持续 2MSL，通常 60s）：
1. **保证最后 ACK 到达**：若被动方重发 FIN，主动方还能再发 ACK
2. **让旧连接报文消失**：防止新连接复用端口时收到旧报文

**TIME_WAIT 过多的问题**：占用端口（默认端口 65535），新连接无法建立。

**Node.js 高并发连接优化**：

1. **连接复用**：HTTP Keep-Alive（默认开启）
2. **长连接 + 连接池**：DB/Redis 用连接池
3. **系统参数调优**（Linux）：
   ```bash
   sysctl -w net.ipv4.ip_local_port_range="10000 65535"
   sysctl -w net.ipv4.tcp_tw_reuse=1
   sysctl -w net.core.somaxconn=65535
   ```
4. **Node 层**：
   ```js
   const agent = new http.Agent({ keepAlive: true, maxSockets: 50 });
   server.keepAliveTimeout = 65000;
   server.headersTimeout = 66000;
   ```

**评分要点**：
- ✅ 三次握手 + 四次挥手准确（必备）
- ✅ TIME_WAIT 两个原因（必备）
- ✅ 系统参数调优（必备）
- ✅ Node Agent + keepAliveTimeout（加分）

---

### Q6.3【实践应用题】请基于 WebSocket 实现一个百万连接的实时推送服务，要求：心跳保活、断线重连、按频道订阅、消息可达性保证。

**参考答案**：

**架构**：

```
客户端 ←→ LB(nginx/sticky) ←→ WS 网关集群 ←→ Redis Pub/Sub ←→ 业务服务
                                       ↓
                                  用户-连接路由表
```

**1. WebSocket 服务（ws 库）**：

```js
const WebSocket = require('ws');
const redis = require('redis');

const wss = new WebSocket.Server({ port: 8080 });
const subscriber = redis.createClient();
const publisher = redis.createClient();

const connections = new Map(); // userId -> Set<ws>

wss.on('connection', (ws, req) => {
  const userId = authenticate(req);
  ws.userId = userId;
  ws.isAlive = true;
  ws.subscriptions = new Set();

  if (!connections.has(userId)) connections.set(userId, new Set());
  connections.get(userId).add(ws);

  ws.on('pong', () => { ws.isAlive = true; });

  ws.on('message', (msg) => {
    const data = JSON.parse(msg);
    if (data.type === 'subscribe') {
      ws.subscriptions.add(data.channel);
      subscriber.subscribe(data.channel);
    }
  });

  ws.on('close', () => {
    connections.get(userId)?.delete(ws);
  });
});

// 心跳检测（30s 一次，无响应则断开）
setInterval(() => {
  wss.clients.forEach((ws) => {
    if (!ws.isAlive) return ws.terminate();
    ws.isAlive = false;
    ws.ping();
  });
}, 30000);

// Redis 订阅：收到消息推给本机所有订阅该频道的连接
subscriber.on('message', (channel, msg) => {
  wss.clients.forEach((ws) => {
    if (ws.subscriptions.has(channel) && ws.readyState === WebSocket.OPEN) {
      ws.send(msg);
    }
  });
});

async function push(channel, message) {
  await publisher.publish(channel, JSON.stringify(message));
}
```

**2. 消息可达性保证**：
- 客户端发 ACK，服务端未收到 ACK 的消息存离线表
- 重连后拉取离线消息
- 消息带递增 seq，客户端去重

**3. 百万连接优化**：
- **单机连接数**：调 `ulimit -n 1000000`（文件描述符）
- **内存**：每连接约 50KB，百万连接需 50GB 内存 → 多机分摊
- **粘性会话**：Nginx `ip_hash` 或 cookie sticky，保证同用户连同一网关
- **CPU 优化**：用 `cluster` 多核，或切到 `uWebSockets.js`（C++ 实现，性能 10x）
- **零拷贝**：广播用 `Buffer` 复用

**4. 客户端断线重连**：
```js
function connect() {
  const ws = new WebSocket('wss://example.com/ws');
  ws.onclose = () => {
    setTimeout(connect, Math.min(1000 * 2 ** retries, 30000));
  };
  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    ws.send(JSON.stringify({ type: 'ack', id: msg.id }));
  };
}
```

**评分要点**：
- ✅ Redis Pub/Sub 跨节点广播（必备）
- ✅ 心跳 ping/pong 保活（必备）
- ✅ ACK + 离线消息保证可达（必备）
- ✅ 文件描述符 / 内存估算（加分）
- ✅ uWebSockets.js / 粘性会话（高级）

---

### Q6.4【场景设计题】设计一个 Node.js 服务的限流方案：要求支持 IP 限流、用户限流、接口限流三种维度，且分布式部署下生效。

**参考答案**：

**方案：多维度 + Redis + 滑动窗口**

**1. 限流算法选型**：

| 算法 | 特点 | 适用 |
| --- | --- | --- |
| 固定窗口 | 简单，临界点突刺 | 粗粒度 |
| 滑动窗口 | 平滑，无突刺 | 通用 |
| 令牌桶 | 允许突发 | API 网关 |
| 漏桶 | 严格匀速 | 整流 |

**2. Redis 滑动窗口实现**（Lua 保证原子）：

```lua
-- rate_limit.lua
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])

redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
local count = redis.call('ZCARD', key)
if count >= limit then return 0 end
redis.call('ZADD', key, now, now .. '-' .. math.random())
redis.call('PEXPIRE', key, window)
return 1
```

```js
const limitScript = fs.readFileSync('./rate_limit.lua', 'utf8');

async function rateLimit(key, limit, windowMs) {
  const allowed = await redis.eval(limitScript, 1, key, Date.now(), windowMs, limit);
  return allowed === 1;
}
```

**3. 多维度限流中间件**：

```js
async function rateLimitMiddleware(ctx, next) {
  const ip = ctx.ip;
  const userId = ctx.state.userId;
  const route = ctx.path;

  const checks = [
    rateLimit(`rl:ip:${ip}`, 1000, 60000),
    rateLimit(`rl:user:${userId}`, 200, 60000),
    rateLimit(`rl:route:${route}`, 5000, 60000),
  ];
  const results = await Promise.all(checks);

  if (results.some((r) => !r)) {
    ctx.status = 429;
    ctx.set('Retry-After', '60');
    ctx.body = { err: '请求过于频繁' };
    return;
  }
  await next();
}
```

**4. 优化**：
- **本地预限流**：先用内存令牌桶挡掉明显刷的，减少 Redis 压力
- **多级缓存**：热点接口用本地窗口兜底
- **降级**：Redis 故障时降级为本地限流（宁可误伤不可击穿）
- **可观测**：限流次数、命中率上报 Prometheus

**评分要点**：
- ✅ 多算法对比选型（必备）
- ✅ Redis + Lua 原子滑动窗口（必备）
- ✅ 三维度并行限流（必备）
- ✅ 本地预限流降 Redis 压力（加分）
- ✅ 故障降级策略（加分）

---

## 第七篇 数据库与存储篇

### Q7.1【基础概念题】请说明数据库连接池的工作原理，以及为什么 Node.js 服务必须用连接池。

**参考答案**：

**连接池原理**：

连接池预先建立一批数据库连接（`min` 个），复用而非每次新建/销毁。请求从池中借连接，用完归还。

```
请求 → 池.borrow() → 有空闲？返回 : 等待/新建(未达 max) 
   → 执行 SQL → 池.release(conn) → 连接回池
```

**关键参数**：
- `min`：最小保持连接数
- `max`：最大连接数（受 DB `max_connections` 限制）
- `acquireTimeout`：借连接超时
- `idleTimeout`：空闲连接超时回收

**为什么 Node.js 必须用连接池**：

1. **建立连接成本高**：TCP 三次握手 + 认证 + 会话设置，每次几十到几百 ms
2. **Node 单线程特性**：单连接会串行化所有查询，并发能力归零
3. **DB 连接数有限**：MySQL 默认 `max_connections=151`，无池每请求一连接会打满
4. **避免泄漏**：池统一管理生命周期，自动回收

**Node.js 常见连接池**：
- `mysql2/promise` 自带池
- `pg` 自带池
- `knex` / `typeorm` / `prisma` 都内置池

```js
const mysql = require('mysql2/promise');
const pool = mysql.createPool({
  host: 'localhost',
  user: 'root',
  database: 'test',
  waitForConnections: true,
  connectionLimit: 20,
  queueLimit: 100,
  idleTimeout: 60000,
});

// 直接用 pool.query 自动借还
const [rows] = await pool.query('SELECT * FROM users WHERE id = ?', [id]);

// 事务需要手动借
const conn = await pool.getConnection();
try {
  await conn.beginTransaction();
  await conn.query('...');
  await conn.commit();
} catch (err) {
  await conn.rollback();
  throw err;
} finally {
  conn.release();
}
```

**连接数估算**：`总连接数 = 实例数 × connectionLimit ≤ DB max_connections × 0.8`（留 20% 给运维）

**评分要点**：
- ✅ 池原理 + 关键参数（必备）
- ✅ Node 单线程串行化问题（必备）
- ✅ 连接数估算公式（加分）
- ✅ 事务需手动 getConnection（必备）

---

### Q7.2【原理分析题】请分析"缓存穿透、缓存击穿、缓存雪崩"三种问题，并给出对应的解决方案。

**参考答案**：

| 问题 | 定义 | 危害 | 解决方案 |
| --- | --- | --- | --- |
| **穿透** | 查询不存在的数据，缓存和 DB 都没有 | 大量请求打到 DB | 布隆过滤器 / 缓存空值 |
| **击穿** | 热点 key 失效瞬间，大量请求穿透到 DB | DB 瞬时压力 | 互斥锁 / 永不过期 + 异步刷新 |
| **雪崩** | 大量 key 同时失效或 Redis 宕机 | DB 被压垮 | 过期时间加随机 / 多级缓存 / 限流降级 |

**详细方案**：

**1. 缓存穿透**：

```js
// 方案 A：缓存空值（简单）
async function getUser(id) {
  const cached = await redis.get(`user:${id}`);
  if (cached === 'NULL') return null;
  if (cached) return JSON.parse(cached);
  const user = await db.query('SELECT * FROM users WHERE id = ?', [id]);
  if (!user) {
    await redis.set(`user:${id}`, 'NULL', 'EX', 60);
    return null;
  }
  await redis.set(`user:${id}`, JSON.stringify(user), 'EX', 3600);
  return user;
}

// 方案 B：布隆过滤器（更省内存）
const BloomFilter = require('bloom-filters');
const filter = BloomFilter.create(1000000, 0.01);
const ids = await db.query('SELECT id FROM users');
ids.forEach((id) => filter.add(id));

async function getUser(id) {
  if (!filter.has(id)) return null;
  // 再查缓存 / DB
}
```

**2. 缓存击穿**：

```js
// 互斥锁（单飞模式）
async function getWithLock(key, loader, ttl = 3600) {
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const lockKey = `lock:${key}`;
  const locked = await redis.set(lockKey, '1', 'NX', 'EX', 10);
  if (locked) {
    try {
      const value = await loader();
      await redis.set(key, JSON.stringify(value), 'EX', ttl);
      return value;
    } finally {
      await redis.del(lockKey);
    }
  } else {
    await sleep(50);
    return getWithLock(key, loader, ttl);
  }
}
```

**3. 缓存雪崩**：

```js
// 过期时间加随机
const ttl = 3600 + Math.floor(Math.random() * 600);
await redis.set(key, value, 'EX', ttl);

// 多级缓存：本地缓存 → Redis → DB
const LRU = require('lru-cache');
const local = new LRU({ max: 1000, ttl: 10000 });

async function get(key) {
  if (local.has(key)) return local.get(key);
  const v = await redis.get(key);
  if (v) { local.set(key, v); return v; }
  const dbv = await db.query(...);
  await redis.set(key, dbv, 'EX', ttl);
  local.set(key, dbv);
  return dbv;
}
```

**评分要点**：
- ✅ 三者定义准确区分（必备）
- ✅ 每种 2+ 方案（必备）
- ✅ 布隆过滤器原理 + 误判率（加分）
- ✅ 互斥锁单飞实现（加分）
- ✅ 多级缓存（高级）

---

### Q7.3【实践应用题】请实现一个分布式锁，要求：互斥、可重入、防误删、自动续期、故障释放。

**参考答案**：

基于 Redis 的分布式锁，使用 **Redisson 风格的看门狗续期**：

```js
class DistributedLock {
  constructor(redis, options = {}) {
    this.redis = redis;
    this.retryCount = options.retryCount || 3;
    this.retryDelay = options.retryDelay || 100;
    this.ttl = options.ttl || 30000;
    this.renewInterval = this.ttl / 3;
    this.watchdog = new Map();
  }

  async acquire(key, ownerId = uuid()) {
    const lockKey = `lock:${key}`;
    const script = `
      if redis.call('EXISTS', KEYS[1]) == 0 then
        redis.call('HSET', KEYS[1], KEYS[2], 1)
        redis.call('PEXPIRE', KEYS[1], ARGV[1])
        return 1
      end
      if redis.call('HEXISTS', KEYS[1], KEYS[2]) == 1 then
        redis.call('HINCRBY', KEYS[1], KEYS[2], 1)
        redis.call('PEXPIRE', KEYS[1], ARGV[1])
        return 1
      end
      return 0
    `;
    for (let i = 0; i < this.retryCount; i++) {
      const ok = await this.redis.eval(script, 2, lockKey, ownerId, this.ttl);
      if (ok) {
        this.startWatchdog(lockKey, ownerId);
        return ownerId;
      }
      await sleep(this.retryDelay);
    }
    throw new Error('获取锁失败');
  }

  startWatchdog(lockKey, ownerId) {
    const timer = setInterval(async () => {
      const script = `
        if redis.call('HEXISTS', KEYS[1], KEYS[2]) == 1 then
          return redis.call('PEXPIRE', KEYS[1], ARGV[1])
        end
        return 0
      `;
      const ok = await this.redis.eval(script, 2, lockKey, ownerId, this.ttl);
      if (!ok) this.stopWatchdog(lockKey);
    }, this.renewInterval);
    this.watchdog.set(lockKey, timer);
  }

  stopWatchdog(lockKey) {
    clearInterval(this.watchdog.get(lockKey));
    this.watchdog.delete(lockKey);
  }

  async release(key, ownerId) {
    const lockKey = `lock:${key}`;
    this.stopWatchdog(lockKey);
    const script = `
      if redis.call('HEXISTS', KEYS[1], KEYS[2]) == 0 then return 0 end
      local count = redis.call('HINCRBY', KEYS[1], KEYS[2], -1)
      if count <= 0 then
        redis.call('DEL', KEYS[1])
        return 1
      end
      return 0
    `;
    return (await this.redis.eval(script, 2, lockKey, ownerId)) === 1;
  }
}

// 使用
const lock = new DistributedLock(redis);
const ownerId = await lock.acquire('order:123');
try {
  await processOrder(123);
} finally {
  await lock.release('order:123', ownerId);
}
```

**特性实现要点**：
- **互斥**：`SET NX` / Hash + Lua
- **可重入**：Hash 结构记录 owner 重入次数
- **防误删**：Lua 校验 owner 后才删
- **自动续期**：看门狗定时 PEXPIRE（TTL/3 间隔）
- **故障释放**：TTL 到期自动释放（持有者崩溃则续期停止）

**Redlock 算法**：多 Redis 节点过半数加锁成功才算成功，防单点故障。

**评分要点**：
- ✅ Lua 保证原子性（必备）
- ✅ Hash 实现可重入（必备）
- ✅ owner 校验防误删（必备）
- ✅ 看门狗续期（必备）
- ✅ 提到 Redlock 多节点（加分）

---

### Q7.4【场景设计题】设计一个电商订单服务的缓存与 DB 一致性方案，要求：强一致读、最终一致写、高并发下不超卖。

**参考答案**：

**方案：Cache-Aside + 延迟双删 + 乐观锁防超卖**

**1. 读写策略**：
- **读**：先查缓存，miss 查 DB 回填
- **写**：先更新 DB，再删缓存（删而非更新，避免并发写脏）

**2. 缓存一致性——延迟双删**：

```js
async function updateStock(itemId, delta) {
  await redis.del(`stock:${itemId}`);              // 1. 先删缓存
  const result = await db.query(                    // 2. 更新 DB（带乐观锁防超卖）
    'UPDATE items SET stock = stock - ? WHERE id = ? AND stock >= ?',
    [delta, itemId, delta]
  );
  if (result.affectedRows === 0) throw new Error('库存不足');
  setTimeout(() => redis.del(`stock:${itemId}`), 500); // 3. 延迟再删
}
```

**3. 防超卖——DB 乐观锁 + Redis 预扣**：

```js
// 秒杀场景：Redis 预扣 + DB 兜底
async function seckill(itemId, userId) {
  const stock = await redis.decr(`stock:${itemId}`);
  if (stock < 0) {
    await redis.incr(`stock:${itemId}`); // 回滚
    throw new Error('已售罄');
  }
  await mq.publish('order', { itemId, userId });
  return { ok: true };
}

// 消费者：DB 真正扣减（带乐观锁）
async function processOrder({ itemId, userId }) {
  const result = await db.query(
    'UPDATE items SET stock = stock - 1 WHERE id = ? AND stock > 0',
    [itemId]
  );
  if (result.affectedRows === 0) {
    await redis.incr(`stock:${itemId}`); // 补偿
    return;
  }
  await db.query('INSERT INTO orders (item_id, user_id) VALUES (?, ?)', [itemId, userId]);
}
```

**4. 强一致读**：
- 关键场景（支付前查余额）直接读 DB，绕过缓存
- 或用 `SELECT ... FOR UPDATE` + 读最新值

**5. 兜底**：
- 缓存设置 TTL 防止永久脏数据
- 定时对账任务：每小时扫一遍缓存与 DB 差异并修复
- Canal 监听 DB binlog，异步刷缓存（最终一致）

**评分要点**：
- ✅ Cache-Aside + 删缓存策略（必备）
- ✅ 延迟双删防旧值回填（必备）
- ✅ DB 乐观锁防超卖（必备）
- ✅ Redis 预扣 + MQ 削峰（加分）
- ✅ Canal binlog 同步缓存（高级）

---

## 第八篇 安全篇

### Q8.1【基础概念题】请列举 Node.js Web 服务常见的安全漏洞及防御措施。

**参考答案**：

| 漏洞 | 说明 | 防御 |
| --- | --- | --- |
| **SQL 注入** | 拼接 SQL 导致执行恶意语句 | 参数化查询、ORM |
| **XSS** | 注入恶意脚本到页面 | 输出转义、CSP、httpOnly cookie |
| **CSRF** | 跨站伪造请求 | CSRF token、SameSite cookie |
| **命令注入** | `child_process.exec` 拼接命令 | 用 `execFile` + 参数数组 |
| **路径穿越** | `../` 读敏感文件 | `path.resolve` + 白名单 |
| **SSRF** | 服务端伪造请求访问内网 | URL 白名单、禁内网 IP |
| **XXE** | XML 外部实体注入 | 禁用 DTD |
| **反序列化** | 恶意序列化数据执行代码 | 不用 `eval`、`Function`、`node-serialize` |
| **依赖漏洞** | 第三方包含漏洞 | `npm audit`、Snyk |
| **原型链污染** | 修改 `__proto__` 影响对象 | `Object.create(null)`、`Object.freeze` |

**Node.js 特有防御**：

```js
// 1. 参数化查询防 SQL 注入
db.query('SELECT * FROM users WHERE id = ?', [id]); // ✅
db.query(`SELECT * FROM users WHERE id = ${id}`);  // ❌

// 2. 命令执行防注入
execFile('convert', [inputPath, outputPath]); // ✅
exec(`convert ${inputPath} ${outputPath}`);   // ❌

// 3. 路径穿越防御
const safePath = path.resolve(baseDir, userInput);
if (!safePath.startsWith(baseDir)) throw new Error('非法路径');

// 4. 原型链污染防御
const obj = Object.create(null);
Object.freeze(Object.prototype);

// 5. helmet 设置安全头
const helmet = require('helmet');
app.use(helmet());

// 6. 限制请求体大小
app.use(express.json({ limit: '100kb' }));

// 7. 速率限制
const rateLimit = require('express-rate-limit');
app.use(rateLimit({ windowMs: 60000, max: 100 }));
```

**评分要点**：
- ✅ 列举 6+ 漏洞及防御（必备）
- ✅ Node 特有：命令注入、原型链污染（必备）
- ✅ 参数化查询、execFile 等具体代码（必备）
- ✅ helmet / rate-limit / npm audit（加分）

---

### Q8.2【原理分析题】JWT 的原理是什么？相比 Session 有何优劣？如何解决 JWT 注销难题？

**参考答案**：

**JWT 原理**：

JWT（JSON Web Token）由三部分组成：`Header.Payload.Signature`

```
Base64(Header).Base64(Payload).HMACSHA256(Header.Payload, secret)
```

- **Header**：算法类型（如 HS256）
- **Payload**：声明（如 `userId`、`exp`、`iat`）
- **Signature**：用服务端密钥对前两部分签名

服务端收到 JWT 后：Base64 解码 Header/Payload → 用密钥重新算签名 → 对比是否一致（防篡改）→ 检查 `exp` 是否过期。

**JWT vs Session**：

| 维度 | Session | JWT |
| --- | --- | --- |
| 存储 | 服务端（内存/Redis） | 客户端 |
| 扩展 | 需共享 session 存储 | 无状态，天然分布式 |
| 注销 | 删除即可立即生效 | 难（签发后无法撤回） |
| 大小 | 短（session id） | 长（含 payload） |
| 安全 | 可信服务端 | 防篡改但 payload 可读 |
| 续期 | 容易 | 需 refresh token |

**JWT 注销难题与解决方案**：

JWT 一旦签发，在 `exp` 前一直有效，无法主动失效。解决方案：

1. **黑名单**：注销时把 JWT 加入 Redis 黑名单（TTL = 剩余有效期），每次请求查黑名单
   ```js
   async function logout(token) {
     const payload = jwt.decode(token);
     await redis.set(`jwt:black:${payload.jti}`, '1', 'EX', payload.exp - now);
   }
   async function verify(token) {
     const payload = jwt.verify(token, secret);
     if (await redis.get(`jwt:black:${payload.jti}`)) throw new Error('已注销');
     return payload;
   }
   ```

2. **短 TTL + Refresh Token**：access token 5 分钟，refresh token 7 天。注销时删 refresh token，access 自然过期

3. **版本号**：用户表加 `token_version`，改密码时 +1，JWT payload 带 version，校验时比对

4. **双 token + Redis 校验**：JWT 仅作传输载体，每次请求查 Redis 是否有效（退化成 session）

**评分要点**：
- ✅ JWT 三段结构 + 签名验证（必备）
- ✅ 与 Session 对比维度（必备）
- ✅ 注销方案：黑名单 + 短 TTL + refresh（必备）
- ✅ 提到 payload 可读不能放敏感信息（加分）

---

### Q8.3【实践应用题】请设计一个 Node.js 服务的认证授权方案：支持微信扫码登录、JWT 鉴权、RBAC 权限控制、接口级权限校验。

**参考答案**：

**整体流程**：

```
微信扫码 → 拿 openid → 生成 JWT(access + refresh) → 请求带 JWT → 中间件校验 + RBAC
```

**1. 微信扫码登录**：

```js
// 步骤1：生成二维码
app.get('/auth/wechat/qrcode', (req, res) => {
  const state = uuid();
  const url = `https://open.weixin.qq.com/connect/qrconnect?appid=${APPID}&redirect_uri=${REDIRECT_URI}&response_type=code&scope=snsapi_login&state=${state}`;
  redis.set(`wx:state:${state}`, '1', 'EX', 300);
  res.json({ url, state });
});

// 步骤2：回调换 openid
app.get('/auth/wechat/callback', async (req, res) => {
  const { code, state } = req.query;
  if (!(await redis.get(`wx:state:${state}`))) return res.status(400).end();
  const tokenRes = await fetch(`https://api.weixin.qq.com/sns/oauth2/access_token?appid=${APPID}&secret=${SECRET}&code=${code}&grant_type=authorization_code`);
  const { openid, access_token } = await tokenRes.json();
  const userRes = await fetch(`https://api.weixin.qq.com/sns/userinfo?access_token=${access_token}&openid=${openid}`);
  const wxUser = await userRes.json();

  let user = await db.query('SELECT * FROM users WHERE wx_openid = ?', [openid]);
  if (!user) {
    user = await db.query('INSERT INTO users (wx_openid, nickname, avatar) VALUES (?, ?, ?)', [openid, wxUser.nickname, wxUser.headimgurl]);
  }

  const access = jwt.sign({ uid: user.id, jti: uuid() }, SECRET, { expiresIn: '2h' });
  const refresh = jwt.sign({ uid: user.id, type: 'refresh' }, REFRESH_SECRET, { expiresIn: '7d' });
  await redis.set(`refresh:${user.id}`, refresh, 'EX', 7 * 86400);
  res.json({ access, refresh, user });
});
```

**2. JWT 中间件**：

```js
async function authMiddleware(ctx, next) {
  const token = ctx.headers.authorization?.replace('Bearer ', '');
  if (!token) return ctx.throw(401, '未登录');
  try {
    const payload = jwt.verify(token, SECRET);
    if (await redis.get(`jwt:black:${payload.jti}`)) return ctx.throw(401, '已注销');
    ctx.state.user = { id: payload.uid };
    ctx.state.tokenJti = payload.jti;
  } catch (err) {
    return ctx.throw(401, 'token 无效');
  }
  await next();
}
```

**3. RBAC 权限控制**：

```sql
CREATE TABLE roles (id, name);
CREATE TABLE permissions (id, name, resource, action);
CREATE TABLE user_roles (user_id, role_id);
CREATE TABLE role_permissions (role_id, permission_id);
```

```js
function requirePermission(resource, action) {
  return async (ctx, next) => {
    const userId = ctx.state.user.id;
    let perms = await redis.get(`perms:${userId}`);
    if (!perms) {
      perms = await db.query(`
        SELECT p.resource, p.action FROM permissions p
        JOIN role_permissions rp ON rp.permission_id = p.id
        JOIN user_roles ur ON ur.role_id = rp.role_id
        WHERE ur.user_id = ?`, [userId]);
      await redis.set(`perms:${userId}`, JSON.stringify(perms), 'EX', 300);
    }
    const has = perms.some((p) => p.resource === resource && p.action === action);
    if (!has) return ctx.throw(403, '无权限');
    await next();
  };
}

router.post('/orders', authMiddleware, requirePermission('order', 'create'), createOrder);
```

**4. 权限变更即时生效**：改角色后清 `perms:${userId}` 缓存 + access token 加黑名单强制重登

**评分要点**：
- ✅ 微信扫码 OAuth 流程（必备）
- ✅ JWT access + refresh 双 token（必备）
- ✅ RBAC 四表设计 + 中间件（必备）
- ✅ 权限缓存 + 变更生效（加分）
- ✅ 黑名单注销（加分）

---

### Q8.4【场景设计题】你的服务收到安全应急报告：生产环境被植入挖矿程序。请给出完整的应急响应流程。

**参考答案**：

**应急响应六步法**：

**1. 隔离止损（最优先）**：
- 立即下线受影响实例（安全组/负载均衡摘除）
- 保留现场：内存 dump、磁盘快照（取证，勿直接重启）
- 撤销可能泄露的凭证：DB 密码、JWT secret、SSH key、云 AK/SK

**2. 评估影响范围**：
- 检查所有实例 CPU/网络异常
- 查云监控、日志，确定入侵时间和入口
- 排查是否有数据外泄（出站流量异常）

**3. 定位入侵入口**：
- **常见入口**：依赖漏洞（如 `event-stream` 投毒）、SSRF 打内网、命令注入（`exec` 拼接）、凭证泄露、容器逃逸
- **排查手段**：
  - 查 `~/.bash_history`、`/tmp`、`/var/tmp` 异常文件
  - 查 crontab（挖矿常驻 cron）
  - 查异常进程 `ps auxf`、网络连接 `netstat -antp`
  - 查启动项 `systemctl list-unit-files`
  - 比对进程二进制与官方包哈希

**4. 清除与修复**：
- 不要在受感染环境清理，**重建全新实例**
- 重新部署干净镜像（确认镜像未被篡改）
- 修复漏洞：升级依赖、修补代码、关闭危险 API
- 轮换所有密钥

**5. 加固防御**：
- 镜像最小化（distroless / alpine）
- 容器以非 root 运行、只读根文件系统
- 依赖扫描入 CI（Snyk / Trivy）
- 出站白名单（限制外联，挖矿连不上矿池）
- 文件完整性监控（AIDE / Tripwire）
- 日志审计 + 告警（异常 CPU、外联、文件变更）

**6. 复盘与合规**：
- 写事故报告：时间线、根因、影响、改进
- 安全合规上报（如涉及用户数据需按法规通知）
- 落地改进措施并跟踪

**评分要点**：
- ✅ 隔离优先 + 保留现场（必备）
- ✅ 列举常见入侵入口（必备）
- ✅ 重建而非清理（关键，避免后门残留）
- ✅ 加固措施：非 root、依赖扫描、出站白名单（必备）
- ✅ 合规上报意识（加分）

---

## 第九篇 架构设计篇

### Q9.1【基础概念题】请说明单体架构、微服务架构、Serverless 各自的适用场景与权衡。

**参考答案**：

| 维度 | 单体 | 微服务 | Serverless |
| --- | --- | --- | --- |
| 部署 | 一个包 | 多服务独立部署 | 函数级，平台托管 |
| 扩展 | 整体扩 | 按服务扩 | 自动按请求扩 |
| 团队 | 小团队 | 多团队 | 任意 |
| 复杂度 | 低 | 高（分布式） | 中（平台屏蔽） |
| 运维 | 简单 | 复杂（需 K8s） | 极简（托管） |
| 冷启动 | 无 | 无 | 有（Fn 场景） |
| 成本 | 固定 | 固定 + 资源浪费 | 按用量 |
| 适用 | MVP、小项目 | 复杂业务、大团队 | 突发流量、事件驱动 |

**适用场景**：

- **单体**：初创期、业务边界清晰、团队 < 10 人。快速迭代，避免过早微服务化
- **微服务**：业务复杂、多团队、需独立扩展。Netflix、亚马逊级别
- **Serverless**：突发流量（秒杀）、事件驱动（Webhook、定时任务）、长尾低频接口

**权衡要点**：
- 微服务引入分布式复杂性：网络不可靠、数据一致性、链路追踪、运维成本
- Serverless 有冷启动（几百 ms）、厂商锁定、长任务受限（超时）
- 演进路径：单体 → 模块化单体 → 微服务 → 部分 Serverless

**评分要点**：
- ✅ 三架构特性对比（必备）
- ✅ 各自适用场景（必备）
- ✅ 微服务分布式复杂性（必备）
- ✅ 演进路径建议（加分）

---

### Q9.2【原理分析题】请描述 CAP 定理与 BASE 理论，并说明在分布式事务中如何取舍。

**参考答案**：

**CAP 定理**：分布式系统三选二
- **C（Consistency）一致性**：所有节点同一时刻数据一致
- **A（Availability）可用性**：每个请求都能收到响应（不保证最新）
- **P（Partition tolerance）分区容错**：网络分区时仍能工作

由于网络分区不可避免，实际是 **CP** 或 **AP** 二选一：
- **CP**：ZooKeeper、etcd、HBase（分区时部分请求拒绝以保证一致）
- **AP**：Cassandra、Eureka、Redis Cluster（分区时各分区继续服务，允许数据不一致）

**BASE 理论**（对 CAP 的实践补充）：
- **B**asically Available：基本可用（允许降级）
- **S**oft state：软状态（允许中间状态）
- **E**ventually consistent：最终一致性

**分布式事务方案对比**：

| 方案 | 一致性 | 性能 | 复杂度 | 适用 |
| --- | --- | --- | --- | --- |
| 2PC / XA | 强 | 低 | 高 | 传统 DB |
| TCC | 强 | 中 | 高（需写补偿） | 资金类 |
| Saga | 最终 | 高 | 中 | 长事务 |
| 本地消息表 | 最终 | 高 | 低 | 异步解耦 |
| 事务消息（RocketMQ） | 最终 | 高 | 低 | 消息驱动 |

**TCC 示例**（订单 + 库存）：
```js
// Try：预留资源
orderService.tryCreate(orderId);     // 创建待确认订单
stockService.tryDeduct(itemId);      // 预扣库存

// Confirm：确认提交
orderService.confirmCreate(orderId); // 订单生效
stockService.confirmDeduct(itemId);  // 库存真扣

// Cancel：回滚
orderService.cancelCreate(orderId);  // 订单作废
stockService.cancelDeduct(itemId);   // 释放预扣
```

**实践建议**：
- 优先避免分布式事务：合理设计边界、最终一致
- 资金类强一致用 TCC
- 普通业务用本地消息表 / Saga
- 引入对账兜底

**评分要点**：
- ✅ CAP 定义 + CP/AP 选型（必备）
- ✅ BASE 三要素（必备）
- ✅ 至少 2 种分布式事务方案对比（必备）
- ✅ TCC/Saga 具体实现（加分）

---

### Q9.3【实践应用题】设计一个 Node.js 服务的高可用方案，要求：单点故障不影响整体、自动故障转移、零停机发布、故障自愈。

**参考答案**：

**高可用架构**：

```
                    ┌─── DNS ───┐
                    │           │
                多机房 LB（主备/双活）
                    │
            ┌───────┴───────┐
        Node 集群 A       Node 集群 B（多机房/多可用区）
        （K8s 部署）       （K8s 部署）
            │                  │
        Redis 主从          MySQL 主从
```

**1. 多副本部署（无单点）**：
- K8s Deployment `replicas: 3+`，跨可用区调度
- Service 负载均衡到所有 Pod
- 数据库主从 + ProxySQL 读写分离

**2. 健康检查 + 自动摘除**：
```yaml
livenessProbe:
  httpGet: { path: /health, port: 3000 }
  periodSeconds: 10
  failureThreshold: 3
readinessProbe:
  httpGet: { path: /ready, port: 3000 }
  periodSeconds: 5
```
```js
app.get('/health', (ctx) => { ctx.body = 'ok'; });
app.get('/ready', async (ctx) => {
  await db.ping();
  await redis.ping();
  ctx.body = 'ready';
});
```

**3. 自动故障转移**：
- **Pod 故障**：K8s 自动重启 / 重建
- **节点故障**：K8s 调度器把 Pod 迁移到健康节点
- **DB 主挂**：MHA / Orchestrator 自动提升从为主
- **可用区故障**：LB 自动切到健康可用区

**4. 零停机发布**：
- **滚动更新**：K8s `RollingUpdate` 策略，逐个替换 Pod
- **蓝绿发布**：新版本独立部署，流量一次性切换
- **金丝雀发布**：先放 10% 流量到新版本，观察无异常再全量
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0    # 零停机
```

**5. 故障自愈**：
- HPA 自动扩容（CPU > 70% 扩 Pod）
- 熔断降级（Hystrix / opossum）防止级联故障
- 限流保护（避免被压垮）
- 超时 + 重试（指数退避）

**6. 优雅关闭**（避免请求中断）：
```js
process.on('SIGTERM', async () => {
  server.close(() => process.exit(0));
  setTimeout(() => process.exit(0), 30000);
});
```

**7. 容灾**：异地多活 / 备份恢复演练

**评分要点**：
- ✅ 多副本 + 多可用区（必备）
- ✅ 健康检查 + 自动摘除（必备）
- ✅ 滚动 / 蓝绿 / 金丝雀发布（必备）
- ✅ HPA + 熔断 + 限流自愈（必备）
- ✅ 优雅关闭 + 容灾演练（加分）

---

### Q9.4【场景设计题】设计一个秒杀系统：10 万人抢 1000 件商品，要求不超卖、不少卖、抗高并发、用户体验流畅。

**参考答案**：

**整体架构**：

```
用户 → CDN(静态页) → 网关(限流+鉴权) → Node 集群 → Redis(预扣) → MQ → DB
                                                       ↓
                                                  异步落单
```

**1. 流量层层削减**：

| 层 | 手段 | 削减比例 |
| --- | --- | --- |
| CDN | 静态页 + 倒计时 | 80% 流量不进后端 |
| 网关 | IP/用户限流 | 90% 请求拒绝 |
| Node | 令牌桶 + 验证码 | 挡机器人 |
| Redis | 库存原子扣减 | 真正下单的少量 |
| MQ | 削峰 | DB 不被打垮 |

**2. 防超卖——Redis 原子扣减**：

```js
async function seckill(itemId, userId) {
  const script = `
    local bought = redis.call('SISMEMBER', KEYS[2], ARGV[1])
    if bought == 1 then return -1 end
    local stock = redis.call('GET', KEYS[1])
    if not stock or tonumber(stock) <= 0 then return 0 end
    redis.call('DECR', KEYS[1])
    redis.call('SADD', KEYS[2], ARGV[1])
    return 1
  `;
  const result = await redis.eval(script, 2, `stock:${itemId}`, `bought:${itemId}`, userId);
  if (result === 1) {
    await mq.publish('seckill:order', { itemId, userId });
    return { code: 'QUEUED', msg: '排队中' };
  } else if (result === 0) {
    return { code: 'SOLD_OUT' };
  } else {
    return { code: 'DUPLICATE' };
  }
}
```

**3. 异步落单（MQ 削峰）**：

```js
async function consume({ itemId, userId }) {
  const conn = await pool.getConnection();
  try {
    await conn.beginTransaction();
    const r = await conn.query(
      'UPDATE items SET stock = stock - 1 WHERE id = ? AND stock > 0', [itemId]
    );
    if (r.affectedRows === 0) {
      await redis.incr(`stock:${itemId}`);
      await redis.srem(`bought:${itemId}`, userId);
      await conn.rollback();
      return;
    }
    await conn.query('INSERT INTO orders (item_id, user_id, status) VALUES (?, ?, "created")', [itemId, userId]);
    await conn.commit();
    await pushService.notify(userId, '抢购成功');
  } catch (err) {
    await conn.rollback();
    throw err;
  } finally {
    conn.release();
  }
}
```

**4. 不少卖——失败补偿**：
- Redis 扣成功但 MQ 投递失败：本地事务表 + 重投
- DB 扣失败：Redis 回滚（上面已实现）
- 消费者宕机：MQ 重投 + 幂等（`order_id` 唯一约束）

**5. 用户体验**：
- 前端按钮防抖 + 倒计时
- 异步通知：抢到推送，没抢到提示
- 排队进度查询接口

**6. 防刷**：
- 用户维度限流（每人 1 次）
- 风控：设备指纹、行为分析
- 验证码 / 滑块

**7. 数据预热**：
- 活动前把库存同步到 Redis
- 商品信息预热到本地缓存

**评分要点**：
- ✅ 流量层层削减（必备）
- ✅ Redis Lua 原子扣减防超卖（必备）
- ✅ MQ 异步落单削峰（必备）
- ✅ 失败补偿不少卖（必备）
- ✅ 防刷 + 风控（加分）

---

### Q9.5【场景设计题】设计一个支持千万级消息的 Node.js IM 系统（类似微信），要求：消息有序、不丢、已读回执、多端同步。

**参考答案**：

**整体架构**：

```
客户端 ←→ 接入层(WS 网关集群) ←→ 逻辑层(消息路由) ←→ 存储层
                  ↓                      ↓                ↓
             连接路由表(Redis)      消息队列(Kafka)    MySQL + MongoDB
```

**1. 接入层——长连接网关**：
- 多机部署，每机承载 10w 连接（参考 Q6.3）
- 连接路由表：`userId → {gatewayIP, ws}` 存 Redis
- 粘性会话：同用户多端连同一网关

**2. 消息模型与有序性**：

```
消息结构：{ msgId, from, to, content, seq, timestamp }
```

- **会话内有序**：每个会话维护单调递增 `seq`（Redis INCR）
- **全局唯一 ID**：Snowflake（时间 + 机器 + 序列）
- **客户端按 seq 排序展示**

**3. 不丢消息——存储 + ACK**：

```js
async function sendMessage(from, to, content) {
  const msgId = snowflake.next();
  // 1. 落库（先存后发）
  await db.insert('messages', { msgId, from, to, content, seq: await nextSeq(from, to) });
  // 2. 投递到接收方网关
  const targetGateway = await redis.get(`route:${to}`);
  if (targetGateway) {
    await gatewayRPC.send(targetGateway, { type: 'msg', msgId, from, content });
  } else {
    await redis.sadd(`offline:${to}`, msgId);
  }
  // 3. 客户端 ACK 确认
}
```

**4. 已读回执**：
```js
// 客户端收到消息后发回执
{ type: 'ack', msgId, read: true }
// 服务端更新已读位置
await db.query('UPDATE conversations SET read_seq = ? WHERE user_id = ? AND peer_id = ?', [seq, userId, peerId]);
// 通知发送方"已读"
await sendMessage(peerId, { type: 'read_receipt', msgId });
```

**5. 多端同步**：
- 每个会话维护 `max_seq`
- 客户端登录时上报本地 `last_seq`，服务端推送 `last_seq+1 ~ max_seq` 的消息
- 离线消息表保留 7 天

**6. 群聊**：
- 写扩散 vs 读扩散权衡
- 小群（< 200 人）：写扩散（每人收件箱各存一份）
- 大群：读扩散（群 timeline 存一份，成员主动拉）
- 用 Kafka 异步扩散

**7. 存储分层**：
- 热数据（近 3 个月）：MongoDB / TiDB
- 冷数据：归档到对象存储
- 索引：MySQL 存会话列表 + 最后一条消息

**8. 性能优化**：
- 消息批量推送（攒 10 条或 100ms）
- 连接复用 + 二进制协议（Protobuf）
- 接入层无状态，逻辑层水平扩展

**评分要点**：
- ✅ 接入/逻辑/存储三层分离（必备）
- ✅ seq 会话内有序（必备）
- ✅ 落库 + ACK 不丢（必备）
- ✅ 多端同步基于 last_seq（必备）
- ✅ 群聊读写扩散权衡（加分）
- ✅ 冷热分层（加分）

---

## 第十篇 调试与排错篇

### Q10.1【基础概念题】Node.js 有哪些调试和性能分析工具？分别适用于什么场景？

**参考答案**：

| 工具 | 类型 | 适用场景 |
| --- | --- | --- |
| `node --inspect` + Chrome DevTools | 交互调试 | 断点、变量查看、堆快照 |
| VS Code Debugger | IDE 调试 | 断点、条件断点、日志点 |
| `console.log` / `debug` | 日志 | 简单变量查看 |
| `--prof` | CPU profile | 函数耗时分析 |
| `0x` | 火焰图 | CPU 热点可视化 |
| `clinic.js` | 综合诊断 | doctor/flame/bubble 三件套 |
| `--trace-warnings` | 警告追踪 | 定位 Promise 未处理等 |
| `--trace-event-categories` | 事件追踪 | v8/node/http 异步追踪 |
| `process.report` | 进程报告 | 诊断卡死、内存（含堆栈、libuv 状态） |
| `heapdump` / `v8.writeHeapSnapshot` | 堆快照 | 内存泄漏 |
| `node --max-old-space-size` | 内存限制 | 防 OOM |
| `--abort-on-uncaught-exception` | 核心 dump | 未捕获异常生成 core 文件 |
| `llnode` | core 分析 | 用 lldb 分析 core dump |
| APM（Dynatrace/New Relic） | 生产监控 | 实时性能追踪 |

**关键场景速查**：
- CPU 高 → `--prof` / `0x` 火焰图
- 内存涨 → 堆快照对比
- 事件循环卡 → `clinic doctor` / `monitorEventLoopDelay`
- 异步未处理 → `--trace-warnings`
- 进程卡死 → `process.report.writeReport()`

**评分要点**：
- ✅ 列举 8+ 工具及场景（必备）
- ✅ CPU/内存/事件循环三类问题对应工具（必备）
- ✅ 提到 `process.report` 诊断卡死（加分）

---

### Q10.2【原理分析题】线上 Node 服务偶发 OOM（堆内存超限崩溃），日志无异常。请给出完整的排查方法论。

**参考答案**：

**排查方法论**：

**1. 确认是否真 OOM**：
- 查 `dmesg` / `journalctl` 是否有 OOM Killer 记录
- 查 Node 是否报 `FATAL ERROR: ... JavaScript heap out of memory`
- 区分：系统 OOM（RSS 涨）vs V8 堆 OOM（heapUsed 涨）

**2. 采集堆内存增长曲线**：
```js
setInterval(() => {
  const m = process.memoryUsage();
  logger.info({
    rss: m.rss, heapUsed: m.heapUsed,
    heapTotal: m.heapTotal, external: m.external
  });
}, 10000);
```
- 看 `heapUsed` 是阶梯式增长（泄漏）还是平稳锯齿（正常 GC）
- `external` 涨可能是 Buffer / C++ 对象泄漏

**3. 堆快照对比法**（核心手段）：
```js
const v8 = require('v8');
app.post('/debug/heapdump', (ctx) => {
  const file = `./heap-${Date.now()}.heapsnapshot`;
  v8.writeHeapSnapshot(file);
  ctx.body = { file };
});
```
- 启动后拍快照 A
- 压测一段时间后再拍快照 B
- Chrome DevTools → Memory → Comparison 对比 A/B
- 按 `Retained Size` 排序，找增长最多的对象

**4. 定位泄漏根因**（常见模式）：

| 模式 | 现象 | 排查 |
| --- | --- | --- |
| 全局缓存无上限 | Map 持续增长 | 搜 `new Map`、`global.` |
| 事件监听累积 | EventEmitter listener 数涨 | `getMaxListeners`、`listenerCount` |
| 闭包持有大对象 | 大对象在闭包中不释放 | 看堆快照引用链 |
| 定时器未清 | setInterval 引用不释放 | 搜 `setInterval` |
| Stream 未关 | fd 累积 | `lsof -p <pid>` |
| Promise 未 settle | 闭包挂起 | `--trace-warnings` |

**5. 监听器泄漏检测**：
```js
process.on('warning', (warning) => {
  if (warning.name === 'MaxListenersExceededWarning') {
    logger.error(warning);
  }
});
```

**6. 验证修复**：
- 压测复现 + 监控 heapUsed 是否平稳
- 长时间运行观察

**7. 兜底机制**：
- `--max-old-space-size=2048` 限制
- 监控超阈值自动重启（PM2 `max_memory_restart`）
- 周期性 graceful restart

**评分要点**：
- ✅ 区分系统 OOM vs V8 堆 OOM（必备）
- ✅ 堆快照对比法（必备）
- ✅ 列举 4+ 泄漏模式（必备）
- ✅ 兜底：max-old-space-size + 自动重启（加分）

---

### Q10.3【实践应用题】线上接口偶发慢（P99 800ms，平均 50ms），但 DB 慢日志正常、CPU 不高。请给出排查思路。

**参考答案**：

**分析方向**：平均快但 P99 慢，说明是长尾请求。常见原因：

**1. 是否 GC 停顿**：
```js
const { PerformanceObserver } = require('perf_hooks');
new PerformanceObserver((list) => {
  list.getEntries().forEach((e) => {
    if (e.duration > 100) logger.warn({ duration: e.duration, kind: e.kind }, '长 GC');
  });
}).observe({ entryTypes: ['gc'] });
```
- 若 GC 单次 > 100ms 且与慢请求时间吻合 → GC 问题
- 解法：减少对象分配、调 `--max-old-space-size`

**2. 是否事件循环阻塞**：
```js
const { monitorEventLoopDelay } = require('perf_hooks');
const h = monitorEventLoopDelay({ resolution: 20 });
h.enable();
setInterval(() => {
  if (h.percentile(99) > 100) logger.warn({ p99: h.percentile(99) }, '事件循环 lag');
}, 5000);
```
- lag 高 → 主线程被同步操作阻塞（参考 Q1.5）

**3. 是否连接池等待**：
- DB 连接池打满时请求排队等连接
- 排查：监控 `pool.waitingCount`，慢请求时是否在涨
- 解法：调大连接数、缩短 SQL 执行时间、引入二级缓存

**4. 是否下游依赖抖动**：
- 第三方接口偶发慢
- 排查：APM 看下游调用耗时分布
- 解法：超时 + 熔断 + 降级

**5. 是否冷启动 / JIT 优化失效**：
- 部署后前几个请求慢（JIT 未优化）
- 或函数被 deoptimize（V8 反优化）
- 用 `--trace-deopt` 排查

**6. 是否网络抖动**：
- LB / 网络偶发延迟
- 用 `tcpdump` / `mtr` 分析网络

**7. 是否锁竞争**：
- 分布式锁等待
- 全局锁（如 config 热加载）

**8. 系统级排查**：
- `iostat` 看磁盘 IO 是否抖动
- `vmstat` 看上下文切换
- `top -H -p <pid>` 看线程

**完整排查脚本**：
```js
app.use(async (ctx, next) => {
  const start = Date.now();
  const startHeap = process.memoryUsage().heapUsed;
  await next();
  const duration = Date.now() - start;
  if (duration > 500) {
    logger.warn({
      path: ctx.path, duration,
      heapDelta: process.memoryUsage().heapUsed - startHeap,
      eventLoopLag: h.percentile(99),
      poolWaiting: pool.waitingCount,
    }, '慢请求诊断');
  }
});
```

**评分要点**：
- ✅ 区分长尾 vs 平均（核心洞察）
- ✅ GC / 事件循环 / 连接池 / 下游 四大方向（必备）
- ✅ 具体监控代码（必备）
- ✅ APM + 系统工具配合（加分）

---

### Q10.4【场景设计题】设计一个 Node.js 服务的灰度发布 + 故障自动回滚机制，要求：异常自动检测、自动回滚、用户无感知。

**参考答案**：

**整体方案**：

```
新版本发布 → 灰度 5% → 监控指标 → 正常？扩量 : 回滚
                ↓
          自动判定（错误率/RT/业务指标）
```

**1. 灰度发布（金丝雀）**：

用 Argo Rollouts（K8s）：
```yaml
strategy:
  canary:
    canaryService: myapp-canary
    stableService: myapp-stable
    trafficRouting:
      nginx:
        stableIngress: myapp-ingress
    steps:
      - setWeight: 5
      - pause: { duration: 5m }
      - setWeight: 25
      - pause: { duration: 5m }
      - setWeight: 50
      - pause: { duration: 5m }
      - setWeight: 100
    analysis:                   # 自动分析
      templates:
        - templateName: success-rate
      startingStep: 1           # 第 2 步开始分析
```

**2. 自动回滚判定**（AnalysisTemplate）：
```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  metrics:
    - name: success-rate
      interval: 30s
      successCondition: result[0] >= 0.99
      failureLimit: 3            # 连续 3 次不达标回滚
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            sum(rate(http_requests_total{status!~"5.."}[1m]))
            /
            sum(rate(http_requests_total[1m]))
    - name: p99-latency
      interval: 30s
      successCondition: result[0] < 500
      failureLimit: 3
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[1m])) * 1000
```

**3. 业务指标校验**：
除了技术指标，还看业务指标：
- 下单成功率不下降
- 支付成功率不下降
- 核心转化率不下降

**4. 用户无感知保障**：
- 数据库向前兼容（新版本不能删旧字段，需双写期）
- 接口向后兼容（不删字段、不改语义）
- 会话保持（灰度用户固定在新版本，不反复跳）

**5. 回滚机制**：
- Argo Rollouts 检测到 `failureLimit` 触发自动 `abort`，流量切回 stable
- 镜像保留最近 10 版本，秒级回滚
- DB 变更需配套回滚脚本（DDL 反向操作）

**6. 手动兜底**：
- 一键回滚按钮（CI/CD 平台）
- 紧急回滚 SOP 文档
- 回滚演练（每季度一次）

**7. 灰度策略进阶**：
- 按用户标签灰度（VIP 用户先试）
- 按地域灰度（先小城市再大城市）
- 按时间灰度（避开高峰期）

**评分要点**：
- ✅ 灰度发布 + 流量分割（必备）
- ✅ 自动分析指标（错误率/RT/业务）（必备）
- ✅ failureLimit 自动回滚机制（必备）
- ✅ DB 向前兼容 / 接口向后兼容（加分）
- ✅ 按用户/地域/时间多维灰度（高级）

**真实项目案例**：
- **项目背景**：支付核心服务，每次发版如履薄冰，曾因一次发布事故影响 30 分钟
- **技术选型**：Argo Rollouts + Prometheus + 自研业务指标采集
- **挑战**：业务指标采集延迟导致误判；解决：用滑动窗口 + 多指标联合判定
- **最终效果**：发布事故从月均 1 次降到全年 0 次，回滚时间从 15 分钟到 30 秒

---

## 附录 评分标准与面试官指南

### A. 评分等级

| 等级 | 标准 | 对应薪资段 |
| --- | --- | --- |
| **P6（初级）** | 能回答基础概念题，知道 API 用法 | 15-25k |
| **P7（中级）** | 能解释原理，有实践项目经验 | 25-40k |
| **P8（高级）** | 能做场景设计，权衡多种方案，有踩坑经验 | 40-60k |
| **P9（专家）** | 能从 0 设计系统，懂底层源码，能带团队 | 60k+ |

### B. 题型考察重点

| 题型 | 考察能力 | 答题要点 |
| --- | --- | --- |
| **基础概念题** | 知识广度 | 准确、完整、有深度 |
| **原理分析题** | 技术深度 | 源码级理解、能画图、能举例 |
| **实践应用题** | 动手能力 | 代码规范、考虑边界、有工程素养 |
| **场景设计题** | 系统思维 | 多方案对比、权衡取舍、有真实经验 |

### C. 面试官追问技巧

1. **深挖细节**：候选人提到某个技术，追问"底层怎么实现""遇到过什么坑"
2. **反向质疑**：候选人给出方案后，问"如果流量翻 10 倍呢""如果 DB 挂了呢"
3. **真实案例**：让候选人讲一个他做过的最复杂的 Node 项目，深挖技术决策
4. **白板编码**：让候选人在白板写代码，观察思维过程而非结果
5. **开放讨论**：抛出无标准答案的问题（如"Node 适合做 XX 吗"），看思维深度

### D. 红旗信号（淘汰项）

- ❌ 把 Node 单线程当口头禅，不知线程池存在
- ❌ 只会用框架（Express/Nest）不懂底层
- ❌ 写 Promise 手写题不会异步执行
- ❌ 问内存泄漏只知道"变量没释放"
- ❌ 设计题只给单一方案，不会权衡
- ❌ 没有任何生产环境踩坑经验

### E. 加分项

- ✅ 阅读 Node.js / Libuv 源码，能讲清内部机制
- ✅ 给 Node.js 或开源项目贡献过 PR
- ✅ 有大型 Node.js 生产环境（百万 QPS / 千万 DAU）经验
- ✅ 了解 Deno / Bun 等新一代运行时
- ✅ 能对比 Node.js 与 Go / Java 的优劣
- ✅ 关注性能极致优化（如 V8 隐藏类、内联缓存）
- ✅ 有技术博客 / 技术分享 / 开源项目

### F. 题目分布建议

针对不同岗位级别，建议侧重不同篇章：

| 岗位 | 重点篇章 | 题量 |
| --- | --- | --- |
| **初/中级 Node 工程师** | 核心原理、异步编程、Web 服务、数据库 | 5-8 题 |
| **高级 Node 工程师** | 性能优化、工程化、架构设计、调试排错 | 8-12 题 |
| **Node 技术专家** | 全部，侧重架构设计、场景设计 | 12-15 题 |

### G. 配套实战考察建议

理论面试外，建议搭配实战考察：

1. **代码题（30 分钟）**：从实践应用题中选一道，现场编码
   - 任务调度器、Promise 手写、流处理等
2. **系统设计（45 分钟）**：从场景设计题中选一道，画图 + 讨论
   - 秒杀系统、IM 系统、限流方案等
3. **Bug 排查（30 分钟）**：给一段有问题的代码，让候选人定位
   - 内存泄漏、事件循环阻塞、并发问题等
4. **Pair Programming**：和候选人一起改一个真实 PR，观察协作

---

## 结语

本面试题集覆盖了 Node.js 高级工程师所需的核心能力维度。需要强调的是：

1. **答案不是唯一的**：参考答案仅为评分依据，候选人可有更优方案
2. **重思维轻记忆**：考察分析过程而非死记结论
3. **结合项目经验**：让候选人结合自身项目作答，更能反映真实水平
4. **持续更新**：Node.js 生态演进快，题目需定期更新跟进新技术（如 Bun、Deno、Node 22+ 新特性）

> 📌 **使用建议**：面试官可根据岗位需求挑选 8-15 道题，覆盖至少 4 个篇章，包含基础、原理、实践、场景四类题型，全面评估候选人能力。

---

**文档统计**：
- 篇章数：10 大领域
- 题目数：50 道
- 题型：基础概念题 / 原理分析题 / 实践应用题 / 场景设计题
- 每题含：参考答案 + 评分要点 + 部分含真实项目案例