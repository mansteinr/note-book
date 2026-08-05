# Java 多线程与并发基础

## 1. 多线程概述

### 1.1 什么是线程

**进程（Process）**：操作系统分配资源的基本单位，一个进程包含内存空间和系统资源。

**线程（Thread）**：CPU调度的基本单位，是进程内的一个执行流。一个进程可以包含多个线程，它们共享进程的内存空间和资源。

### 1.2 多线程的优势

- **提高响应速度**：主线程处理用户交互，工作线程处理耗时任务
- **提高吞吐量**：多核CPU上并行执行多个任务
- **节省资源**：线程比进程更轻量，创建和切换成本更低
- **简化开发**：将复杂任务拆分为多个独立执行的子任务

### 1.3 线程与进程的对比

| 特性 | 进程 | 线程 |
|------|------|------|
| 定义 | 资源分配单位 | CPU调度单位 |
| 内存 | 独立地址空间 | 共享进程内存 |
| 开销 | 较大 | 较小 |
| 独立性 | 相互独立 | 相互影响 |
| 通信 | 需要IPC机制 | 直接共享内存 |

---

## 2. 创建线程的方式

### 2.1 继承 Thread 类

```java
public class MyThread extends Thread {
    @Override
    public void run() {
        for (int i = 0; i < 5; i++) {
            System.out.println(getName() + ": " + i);
            try {
                Thread.sleep(1000);  // 休眠1秒
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    public static void main(String[] args) {
        MyThread t1 = new MyThread();
        t1.setName("线程A");
        t1.start();  // 启动线程
    }
}
```

### 2.2 实现 Runnable 接口

```java
public class MyRunnable implements Runnable {
    @Override
    public void run() {
        System.out.println(Thread.currentThread().getName() + " 正在执行");
    }

    public static void main(String[] args) {
        MyRunnable task = new MyRunnable();
        Thread thread = new Thread(task, "工作线程");
        thread.start();
    }
}
```

### 2.3 使用 Lambda 表达式（Java 8+）

```java
public class LambdaThread {
    public static void main(String[] args) {
        // 方式1：直接创建
        new Thread(() -> {
            System.out.println(Thread.currentThread().getName() + " 执行任务");
        }, "Lambda线程").start();

        // 方式2：使用线程池（推荐）
        ExecutorService executor = Executors.newFixedThreadPool(3);
        for (int i = 0; i < 5; i++) {
            executor.submit(() -> {
                System.out.println(Thread.currentThread().getName() + " 处理任务");
            });
        }
        executor.shutdown();
    }
}
```

### 2.4 实现 Callable 接口（有返回值）

```java
import java.util.concurrent.Callable;
import java.util.concurrent.FutureTask;

public class MyCallable implements Callable<String> {
    @Override
    public String call() throws Exception {
        int sum = 0;
        for (int i = 1; i <= 100; i++) {
            sum += i;
        }
        return "计算结果: " + sum;
    }

    public static void main(String[] args) throws Exception {
        MyCallable callable = new MyCallable();
        FutureTask<String> futureTask = new FutureTask<>(callable);
        Thread thread = new Thread(futureTask);
        thread.start();

        String result = futureTask.get();  // 阻塞等待结果
        System.out.println(result);
    }
}
```

### 2.5 三种方式对比

| 方式 | 优点 | 缺点 |
|------|------|------|
| 继承 Thread | 写法简单 | Java单继承，无法继承其他类 |
| 实现 Runnable | 可继承其他类，任务可复用 | 无返回值，需手动处理异常 |
| 实现 Callable | 有返回值，可抛出异常 | 写法稍复杂 |

---

## 3. 线程生命周期

### 3.1 线程状态

```java
public enum State {
    NEW,       // 新建
    RUNNABLE,  // 可运行（就绪 + 运行中）
    BLOCKED,   // 阻塞（等待锁释放）
    WAITING,   // 等待（等待其他线程通知）
    TIMED_WAITING,  // 计时等待
    TERMINATED;  // 终止
}
```

### 3.2 状态转换图

```
         start()
  NEW ──────────→ RUNNABLE
                     │    │
        获得CPU时间片  │    │  等待锁/IO阻塞
                     ↓    ↓
                  运行中  BLOCKED
                     │
    sleep/wait/join  │
                     ↓
               TIMED_WAITING / WAITING
                     │
    被唤醒/超时/结束  │
                     ↓
                  RUNNABLE
                     │  run()结束
                     ↓
                  TERMINATED
```

### 3.3 常用方法

```java
Thread thread = new Thread(() -> { ... });

thread.start();           // 启动线程
thread.sleep(1000);       // 当前线程休眠1秒（静态方法）
thread.join();            // 等待该线程结束
thread.interrupt();       // 中断线程
thread.isAlive();         // 线程是否存活

Thread.currentThread();   // 获取当前线程
Thread.sleep(1000);       // 静态方法，休眠当前线程
Thread.yield();           // 让出CPU时间片
```

---

## 4. 线程同步机制

### 4.1 为什么需要同步

多个线程同时访问共享资源时，可能发生**竞态条件（Race Condition）**，导致数据不一致。

```java
// 问题示例：无同步导致计数错误
public class Counter {
    private int count = 0;

    public void increment() {
        count++;  // 非原子操作，多线程下不安全
    }

    public int getCount() {
        return count;
    }
}
```

### 4.2 synchronized 关键字

#### 同步实例方法

```java
public class BankAccount {
    private double balance;

    // 同步方法，锁的是this对象
    public synchronized void deposit(double amount) {
        balance += amount;
    }

    public synchronized void withdraw(double amount) {
        if (balance >= amount) {
            balance -= amount;
        }
    }
}
```

#### 同步代码块

```java
public class Counter {
    private int count = 0;
    private final Object lock = new Object();  // 专用锁对象

    public void increment() {
        synchronized (lock) {  // 使用专用锁
            count++;
        }
    }

    // 使用 Class 对象作为锁
    public static void staticMethod() {
        synchronized (Counter.class) {
            // 同步静态方法的锁
        }
    }
}
```

#### synchronized 特性

- **可重入性**：同一线程可重复获取同一把锁
- **互斥性**：同一时刻只有一个线程能获取锁
- **内存可见性**：解锁前的修改对后续获取锁的线程可见

### 4.3 Lock 接口（JUC）

```java
import java.util.concurrent.locks.ReentrantLock;

public class LockCounter {
    private int count = 0;
    private final ReentrantLock lock = new ReentrantLock();

    public void increment() {
        lock.lock();
        try {
            count++;
        } finally {
            lock.unlock();  // 必须在finally中释放
        }
    }

    // 尝试获取锁，支持超时和中断
    public boolean tryIncrement() {
        if (lock.tryLock()) {
            try {
                count++;
                return true;
            } finally {
                lock.unlock();
            }
        }
        return false;
    }
}
```

#### synchronized vs ReentrantLock

| 特性 | synchronized | ReentrantLock |
|------|--------------|---------------|
| 实现层面 | JVM层面 | JDK层面 |
| 释放方式 | 自动释放 | 需手动unlock() |
| 可中断 | 不支持 | 支持lockInterruptibly() |
| 超时获取 | 不支持 | 支持tryLock(timeout) |
| 公平锁 | 不支持 | 支持new FairLock() |
| 条件变量 | 单一(notify) | 多个Condition |
| 性能 | 优化后良好 | 高竞争下更优 |

### 4.4 volatile 关键字

```java
public class VolatileExample {
    private volatile boolean running = true;  // 保证可见性

    public void stop() {
        running = false;
    }

    public void run() {
        while (running) {
            // 执行任务
        }
    }
}
```

**volatile 特性**：
- **可见性**：一个线程修改后，其他线程立即可见
- **有序性**：禁止指令重排序
- **不保证原子性**：不能替代 synchronized

### 4.5 CAS 与原子类

```java
import java.util.concurrent.atomic.AtomicInteger;

public class AtomicCounter {
    private AtomicInteger count = new AtomicInteger(0);

    public void increment() {
        count.incrementAndGet();  // 原子递增
    }

    public int getCount() {
        return count.get();
    }

    // CAS 操作示例
    public void update() {
        int oldValue = count.get();
        int newValue = oldValue + 1;
        boolean success = count.compareAndSet(oldValue, newValue);
    }
}
```

**常用原子类**：
- `AtomicInteger` / `AtomicLong` / `AtomicBoolean`
- `AtomicReference`（引用类型原子操作）
- `AtomicStampedReference`（带时间戳，解决ABA问题）

---

## 5. 线程通信

### 5.1 wait/notify 机制

```java
public class ProducerConsumer {
    private final Object lock = new Object();
    private int stock = 0;
    private static final int MAX_STOCK = 10;

    // 生产者
    public void produce() {
        synchronized (lock) {
            while (stock >= MAX_STOCK) {
                try {
                    lock.wait();  // 等待，释放锁
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
            stock++;
            System.out.println("生产: " + stock);
            lock.notifyAll();  // 唤醒等待的线程
        }
    }

    // 消费者
    public void consume() {
        synchronized (lock) {
            while (stock <= 0) {
                try {
                    lock.wait();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
            stock--;
            System.out.println("消费: " + stock);
            lock.notifyAll();
        }
    }
}
```

### 5.2 Condition 条件变量

```java
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.ReentrantLock;

public class ConditionExample {
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition notFull = lock.newCondition();
    private final Condition notEmpty = lock.newCondition();
    private int stock = 0;
    private static final int MAX = 10;

    public void produce() throws InterruptedException {
        lock.lock();
        try {
            while (stock >= MAX) {
                notFull.await();
            }
            stock++;
            notEmpty.signal();
        } finally {
            lock.unlock();
        }
    }

    public void consume() throws InterruptedException {
        lock.lock();
        try {
            while (stock <= 0) {
                notEmpty.await();
            }
            stock--;
            notFull.signal();
        } finally {
            lock.unlock();
        }
    }
}
```

### 5.3 CountDownLatch

```java
import java.util.concurrent.CountDownLatch;

public class CountDownLatchExample {
    public static void main(String[] args) throws InterruptedException {
        int threadCount = 5;
        CountDownLatch latch = new CountDownLatch(threadCount);

        for (int i = 0; i < threadCount; i++) {
            final int taskId = i;
            new Thread(() -> {
                System.out.println("任务 " + taskId + " 开始执行");
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                System.out.println("任务 " + taskId + " 完成");
                latch.countDown();
            }).start();
        }

        latch.await();  // 等待所有任务完成
        System.out.println("所有任务已完成");
    }
}
```

### 5.4 CyclicBarrier

```java
import java.util.concurrent.CyclicBarrier;

public class CyclicBarrierExample {
    public static void main(String[] args) {
        int threadCount = 5;
        CyclicBarrier barrier = new CyclicBarrier(threadCount, () -> {
            System.out.println("所有线程就绪，开始执行");
        });

        for (int i = 0; i < threadCount; i++) {
            new Thread(() -> {
                System.out.println(Thread.currentThread().getName() + " 准备好了");
                try {
                    barrier.await();  // 等待所有线程到达
                    System.out.println(Thread.currentThread().getName() + " 开始执行任务");
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }).start();
        }
    }
}
```

---

## 6. 线程池

### 6.1 为什么需要线程池

- **降低资源消耗**：重复利用线程，避免频繁创建销毁
- **提高响应速度**：任务到达时无需等待线程创建
- **统一管理**：集中分配、调优和监控线程
- **防止过载**：限制最大并发线程数

### 6.2 核心参数

```java
public ThreadPoolExecutor(
    int corePoolSize,           // 核心线程数
    int maximumPoolSize,        // 最大线程数
    long keepAliveTime,         // 空闲线程存活时间
    TimeUnit unit,              // 时间单位
    BlockingQueue<Runnable> workQueue,  // 任务队列
    ThreadFactory threadFactory,         // 线程工厂
    RejectedExecutionHandler handler     // 拒绝策略
)
```

### 6.3 拒绝策略

| 策略 | 说明 |
|------|------|
| `AbortPolicy` | 抛出异常（默认） |
| `CallerRunsPolicy` | 调用者线程执行 |
| `DiscardPolicy` | 直接丢弃 |
| `DiscardOldestPolicy` | 丢弃最旧任务 |

### 6.4 创建线程池

```java
import java.util.concurrent.*;

public class ThreadPoolExample {
    public static void main(String[] args) {
        // 方式1：使用 Executors 工具类（简单场景）
        ExecutorService fixedPool = Executors.newFixedThreadPool(5);
        ExecutorService singlePool = Executors.newSingleThreadExecutor();
        ScheduledExecutorService scheduledPool = Executors.newScheduledThreadPool(3);

        // 方式2：自定义 ThreadPoolExecutor（推荐）
        ThreadPoolExecutor executor = new ThreadPoolExecutor(
            4,                           // 核心线程数
            8,                           // 最大线程数
            60,                          // 空闲线程存活时间
            TimeUnit.SECONDS,
            new LinkedBlockingQueue<>(100),  // 有界队列
            new ThreadFactory() {
                private final AtomicInteger counter = new AtomicInteger(0);
                @Override
                public Thread newThread(Runnable r) {
                    Thread t = new Thread(r);
                    t.setName("worker-" + counter.incrementAndGet());
                    return t;
                }
            },
            new ThreadPoolExecutor.CallerRunsPolicy()
        );

        // 提交任务
        executor.execute(() -> {
            System.out.println(Thread.currentThread().getName() + " 执行任务");
        });

        // 提交有返回值的任务
        Future<String> future = executor.submit(() -> {
            return "任务结果";
        });

        // 关闭线程池
        executor.shutdown();
    }
}
```

### 6.5 提交任务的两种方式

```java
ExecutorService executor = Executors.newFixedThreadPool(4);

// execute：提交Runnable，无返回值
executor.execute(() -> {
    // 执行任务
});

// submit：提交Callable/Runnable，有返回值
Future<String> future = executor.submit(() -> {
    return "执行结果";
});

try {
    String result = future.get();       // 阻塞获取结果
    String result2 = future.get(5, TimeUnit.SECONDS);  // 超时获取
    boolean done = future.isDone();     // 是否已完成
    future.cancel(true);                // 取消任务
} catch (Exception e) {
    e.printStackTrace();
}
```

### 6.6 线程池大小配置

```java
// CPU密集型任务：线程数 = CPU核心数 + 1
int cpuCores = Runtime.getRuntime().availableProcessors();
int cpuPoolSize = cpuCores + 1;

// IO密集型任务：线程数 = CPU核心数 * 2
int ioPoolSize = cpuCores * 2;

// 混合型任务：根据实际情况调整
// 建议压测确定最优值
```

---

## 7. 并发集合

### 7.1 为什么需要并发集合

普通集合在多线程环境下不安全：

```java
// 不安全的示例
List<Integer> list = new ArrayList<>();  // 多线程下不安全
Map<String, Integer> map = new HashMap<>();  // 多线程下不安全
```

### 7.2 常用并发集合

| 集合类 | 对应普通类 | 并发机制 |
|--------|------------|----------|
| `ConcurrentHashMap` | `HashMap` | CAS + synchronized（JDK 8+） |
| `CopyOnWriteArrayList` | `ArrayList` | 写时复制 |
| `CopyOnWriteArraySet` | `HashSet` | 基于CopyOnWriteArrayList |
| `BlockingQueue` | `Queue` | 阻塞队列接口 |
| `ConcurrentLinkedQueue` | `LinkedList` | CAS非阻塞 |

### 7.3 ConcurrentHashMap

```java
import java.util.concurrent.ConcurrentHashMap;

public class ConcurrentMapExample {
    public static void main(String[] args) {
        ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

        // 原子操作
        map.put("key1", 1);
        map.putIfAbsent("key2", 2);  // 仅当key不存在时插入

        // 遍历（弱一致性，不阻塞）
        map.forEach((key, value) -> {
            System.out.println(key + ": " + value);
        });

        // 并发计数
        map.compute("counter", (k, v) -> v == null ? 1 : v + 1);
    }
}
```

### 7.4 BlockingQueue 阻塞队列

```java
import java.util.concurrent.*;

public class BlockingQueueExample {
    public static void main(String[] args) throws InterruptedException {
        // ArrayBlockingQueue：有界数组
        BlockingQueue<Integer> queue = new ArrayBlockingQueue<>(10);

        // LinkedBlockingQueue：链表实现，默认无界
        // BlockingQueue<Integer> queue = new LinkedBlockingQueue<>();

        // PriorityBlockingQueue：优先级队列
        // BlockingQueue<Integer> queue = new PriorityBlockingQueue<>();

        // 插入元素
        queue.put(1);        // 满时阻塞
        queue.offer(2, 1, TimeUnit.SECONDS);  // 超时插入

        // 获取元素
        Integer val = queue.take();  // 空时阻塞
        Integer val2 = queue.poll(1, TimeUnit.SECONDS);  // 超时获取

        // 生产消费示例
        ProducerConsumerExample.example();
    }
}
```

### 7.5 CopyOnWriteArrayList

```java
import java.util.concurrent.CopyOnWriteArrayList;

public class CopyOnWriteExample {
    public static void main(String[] args) {
        CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();

        // 写操作：复制整个数组后修改
        list.add("元素1");
        list.addIfAbsent("元素2");

        // 读操作：无锁，直接读当前数组
        String item = list.get(0);

        // 适用场景：读多写少，遍历操作多
        // 缺点：写操作开销大（复制数组）
    }
}
```

---

## 8. 锁的进阶知识

### 8.1 AQS（AbstractQueuedSynchronizer）

AQS是ReentrantLock、CountDownLatch等同步组件的基础。

```java
public abstract class AbstractQueuedSynchronizer {
    private int state;  // 同步状态
    private Node head;  // 队列头
    private Node tail;  // 队列尾

    // 核心方法（子类实现）
    protected boolean tryAcquire(int arg) { ... }
    protected boolean tryRelease(int arg) { ... }
    protected int tryAcquireShared(int arg) { ... }
    protected boolean tryReleaseShared(int arg) { ... }
}
```

**同步队列结构**：
```
Head ↔ Node1 ↔ Node2 ↔ ... ↔ Tail
         ｜           ｜
      持有线程       等待线程
```

### 8.2 公平锁与非公平锁

```java
// 非公平锁（默认）：允许插队，吞吐量高
ReentrantLock unfairLock = new ReentrantLock();

// 公平锁：按顺序获取，避免饥饿
ReentrantLock fairLock = new ReentrantLock(true);
```

### 8.3 ReadWriteLock 读写锁

```java
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

public class ReadWriteLockExample {
    private final ReadWriteLock rwLock = new ReentrantReadWriteLock();
    private int data = 0;

    // 读操作：多个线程可同时读
    public int read() {
        rwLock.readLock().lock();
        try {
            return data;
        } finally {
            rwLock.readLock().unlock();
        }
    }

    // 写操作：独占，阻塞所有读写
    public void write(int value) {
        rwLock.writeLock().lock();
        try {
            data = value;
        } finally {
            rwLock.writeLock().unlock();
        }
    }
}
```

### 8.4 StampedLock（JDK 8+）

```java
import java.util.concurrent.locks.StampedLock;

public class StampedLockExample {
    private final StampedLock stampedLock = new StampedLock();
    private double x, y;

    // 写锁
    public void move(double deltaX, double deltaY) {
        long stamp = stampedLock.writeLock();
        try {
            x += deltaX;
            y += deltaY;
        } finally {
            stampedLock.unlockWrite(stamp);
        }
    }

    // 乐观读（无锁，适合读多写少）
    public double distance() {
        long stamp = stampedLock.tryOptimisticRead();
        double currentX = x, currentY = y;
        if (!stampedLock.validate(stamp)) {
            stamp = stampedLock.readLock();
            try {
                currentX = x;
                currentY = y;
            } finally {
                stampedLock.unlockRead(stamp);
            }
        }
        return Math.sqrt(currentX * currentX + currentY * currentY);
    }
}
```

---

## 9. 并发编程最佳实践

### 9.1 避免的陷阱

#### 不要使用 stop() 方法

```java
// 错误：stop() 已废弃，可能导致资源不一致
// thread.stop();

// 正确：使用标志位优雅停止
public class StoppableThread implements Runnable {
    private volatile boolean running = true;

    @Override
    public void run() {
        while (running) {
            // 执行任务
        }
    }

    public void stop() {
        running = false;
    }
}
```

#### 不要滥用 synchronized

```java
// 错误：锁粒度过大，降低并发
public synchronized void process() {
    // 大量非同步操作
    doSomething();
    // 仅少量代码需要同步
    updateState();
}

// 正确：缩小锁范围
public void process() {
    doSomething();  // 无需同步

    synchronized (this) {
        updateState();  // 仅必要部分加锁
    }
}
```

### 9.2 选择合适的同步方式

| 场景 | 推荐方案 |
|------|----------|
| 简单互斥 | `synchronized` |
| 需要超时/中断 | `ReentrantLock` |
| 只读多读 | `ReadWriteLock` |
| 状态标志 | `volatile` |
| 计数器 | `AtomicInteger/Long` |
| 多阶段协调 | `CountDownLatch` / `CyclicBarrier` |
| 生产者-消费者 | `BlockingQueue` |

### 9.3 线程池使用规范

```java
// 推荐：自定义 ThreadPoolExecutor
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    Runtime.getRuntime().availableProcessors(),  // 核心数
    Runtime.getRuntime().availableProcessors() * 2,  // 最大数
    60L, TimeUnit.SECONDS,
    new LinkedBlockingQueue<>(200),
    new ThreadFactory() { ... },
    new ThreadPoolExecutor.CallerRunsPolicy()
);

// 不推荐：直接使用 Executors（可能 OOM）
// Executors.newFixedThreadPool()  // 无界队列
// Executors.newCachedThreadPool()  // 最大线程数为Integer.MAX_VALUE
```

### 9.4 其他建议

- **优先使用并发集合**：避免使用 `Collections.synchronizedList()` 等包装方法
- **使用 try-with-resources**：配合 `Lock` 时注意在 `finally` 中 `unlock()`
- **避免死锁**：确保获取锁的顺序一致
- **使用 `ThreadLocal`**：避免在方法参数中传递非线程安全对象
- **合理设置线程名称**：便于问题排查

```java
// 设置有意义的线程名
Thread thread = new Thread(() -> { ... }, "订单处理线程-" + orderId);

// 使用 ThreadLocal 保存线程上下文
public class UserContext {
    private static final ThreadLocal<User> currentUser = new ThreadLocal<>();

    public static void set(User user) {
        currentUser.set(user);
    }

    public static User get() {
        return currentUser.get();
    }

    public static void remove() {
        currentUser.remove();  // 必须清理，防止内存泄漏
    }
}
```

---

## 10. 核心知识点总结

### 10.1 线程创建方式对比

| 方式 | 返回值 | 异常处理 | 使用场景 |
|------|--------|----------|----------|
| `Thread` 继承 | 无 | 需try-catch | 简单演示 |
| `Runnable` 实现 | 无 | 需try-catch | 需继承其他类 |
| `Callable` 实现 | 有 | 可抛出 | 有返回结果 |
| 线程池 | 有Future | 可捕获 | 生产环境首选 |

### 10.2 同步机制选型指南

```
需要同步？
├── 是 → 简单场景 → synchronized
│       ├── 需要中断？
│       │   └── ReentrantLock.lockInterruptibly()
│       ├── 需要超时？
│       │   └── ReentrantLock.tryLock(timeout)
│       ├── 公平性？
│       │   └── new ReentrantLock(true)
│       ├── 多条件变量？
│       │   └── Lock.newCondition()
│       └── 读写分离？
│           └── ReadWriteLock
└── 否 → 可见性问题？
    └── volatile
```

### 10.3 常见面试考点

1. **synchronized 与 Lock 的区别**
2. **volatile 的作用与原理**
3. **ThreadLocal 的实现原理与内存泄漏**
4. **AQS 的核心原理**
5. **synchronized 升级过程（偏向锁→轻量级锁→重量级锁）**
6. **线程池的核心参数与拒绝策略**
7. **ConcurrentHashMap 的实现原理**
8. **CAS 原理与 ABA 问题**
9. **CountDownLatch 与 CyclicBarrier 的区别**
10. **死锁的产生条件与避免方法**

---

## 附录：常用API速查

### Thread 类方法

| 方法 | 说明 |
|------|------|
| `Thread.currentThread()` | 获取当前线程 |
| `Thread.sleep(ms)` | 休眠当前线程 |
| `Thread.yield()` | 让出CPU时间片 |
| `thread.start()` | 启动线程 |
| `thread.join()` | 等待线程结束 |
| `thread.interrupt()` | 中断线程 |
| `thread.isAlive()` | 线程是否存活 |
| `thread.setName(name)` | 设置线程名 |
| `thread.getName()` | 获取线程名 |

### Lock 接口方法

| 方法 | 说明 |
|------|------|
| `lock.lock()` | 获取锁（阻塞） |
| `lock.tryLock()` | 尝试获取锁（非阻塞） |
| `lock.tryLock(timeout, unit)` | 超时获取锁 |
| `lock.lockInterruptibly()` | 可中断获取锁 |
| `lock.unlock()` | 释放锁 |
| `lock.newCondition()` | 创建条件变量 |

### ExecutorService 方法

| 方法 | 说明 |
|------|------|
| `execute(Runnable)` | 提交任务（无返回值） |
| `submit(Callable)` | 提交任务（有返回值） |
| `shutdown()` | 关闭线程池（等待任务完成） |
| `shutdownNow()` | 立即关闭（尝试中断） |
| `awaitTermination(timeout)` | 等待关闭完成 |
| `isShutdown()` | 是否已关闭 |

### 同步工具类

| 类 | 说明 |
|----|------|
| `CountDownLatch` | 倒计时门闩，等待多线程完成 |
| `CyclicBarrier` | 循环屏障，多线程相互等待 |
| `Semaphore` | 信号量，控制并发数量 |
| `Phaser` | 相位器（JDK 7+），复杂同步场景 |
| `Exchanger` | 两个线程交换数据 |