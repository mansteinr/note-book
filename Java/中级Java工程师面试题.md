# 中级Java工程师面试题

> 面向1-3年经验的中级Java工程师，涵盖核心基础、集合框架、IO、多线程、异常处理等领域。
> 题型包括：简答题、代码分析题、场景应用题。

---

## 目录

- [一、数组](#一数组)
- [二、对象及其继承](#二对象及其继承)
- [三、集合框架（List、Set、Map）](#三集合框架listsetmap)
- [四、日期、Math、枚举](#四日期math枚举)
- [五、数据流与文件操作](#五数据流与文件操作)
- [六、异常处理](#六异常处理)
- [七、多线程及其加锁](#七多线程及其加锁)
- [八、其他常见面试题](#八其他常见面试题)

---

## 一、数组

### 1.1 数组在内存中的存储方式是怎样的？数组的特点是什么？

**答：**

- **存储方式：** 数组在内存中占据**连续的空间**，每个元素大小相同。
- **数组对象本身存储在堆中**（如果是局部变量，引用存储在栈中）。
- **特点：**
  - 查找效率高（通过下标随机访问，时间复杂度 O(1)）。
  - 插入、删除效率低（需要移动元素，时间复杂度 O(n)）。
  - 大小固定，初始化后无法扩容。

### 1.2 如何实现数组的扩容？

**答：**

由于数组大小固定，扩容需要创建新数组并复制元素：

```java
public class ArrayResize {
    public static void main(String[] args) {
        int[] arr = {1, 2, 3, 4, 5};
        
        // 扩容为原长度的 2 倍
        int[] newArr = new int[arr.length * 2];
        
        // 复制元素
        System.arraycopy(arr, 0, newArr, 0, arr.length);
        // 或使用 Arrays.copyOf
        // int[] newArr = Arrays.copyOf(arr, arr.length * 2);
        
        System.out.println(Arrays.toString(newArr));
    }
}
```

**ArrayList 底层也是类似实现，每次扩容约 50%（JDK 1.8）。**

### 1.3 数组和 ArrayList 的区别？

**答：**

| 特性 | 数组 | ArrayList |
|------|------|-----------|
| 大小 | 固定 | 动态扩容 |
| 类型 | 支持基本类型和对象 | 仅支持对象（泛型） |
| 插入/删除 | 需手动移动元素 | 自动处理 |
| 性能 | 略高（无包装类开销） | 略低 |
| 操作 | 直接通过索引 | 提供丰富的 API |

### 1.4 什么是多维数组？如何遍历二维数组？

**答：**

```java
// 二维数组初始化
int[][] matrix = {
    {1, 2, 3},
    {4, 5, 6},
    {7, 8, 9}
};

// 方式一：双重 for 循环
for (int i = 0; i < matrix.length; i++) {
    for (int j = 0; j < matrix[i].length; j++) {
        System.out.print(matrix[i][j] + " ");
    }
    System.out.println();
}

// 方式二：增强 for 循环
for (int[] row : matrix) {
    for (int num : row) {
        System.out.print(num + " ");
    }
    System.out.println();
}
```

---

## 二、对象及其继承

### 2.1 简述面向对象的三大特征（封装、继承、多态）。

**答：**

| 特征 | 说明 | 实现方式 |
|------|------|---------|
| **封装** | 将数据和操作隐藏，对外暴露必要接口 | private 修饰属性，public get/set |
| **继承** | 子类继承父类，复用代码，扩展功能 | extends 关键字 |
| **多态** | 同一个方法在不同对象上有不同表现 | 方法重写（Overriding）、方法重载（Overloading）、向上转型 |

### 2.2 方法重写（Overriding）和方法重载（Overloading）的区别？

**答：**

| 特性 | 重写（Overriding） | 重载（Overloading） |
|------|-------------------|---------------------|
| 发生位置 | 父子类之间 | 同一个类中 |
| 方法名 | 必须相同 | 必须相同 |
| 参数列表 | 必须相同 | 必须不同（数量/类型/顺序） |
| 返回值 | 必须相同或协变 | 不限制 |
| 访问修饰符 | 不能更严格 | 不限制 |
| 异常 | 不能抛出更宽泛的异常 | 不限制 |

### 2.3 什么是向上转型和向下转型？有什么注意事项？

**答：**

```java
class Animal { void eat() {} }
class Dog extends Animal { void bark() {} }

// 向上转型（自动）
Animal animal = new Dog();
animal.eat();  // 调用 Dog 的 eat（多态）
// animal.bark();  // 编译报错，无法调用子类特有方法

// 向下转型（需强制）
Dog dog = (Dog) animal;
dog.bark();    // 可以调用
```

**注意事项：**

- 向下转型前最好用 `instanceof` 判断，避免 `ClassCastException`：
  ```java
  if (animal instanceof Dog) {
      Dog dog = (Dog) animal;
      dog.bark();
  }
  ```

### 2.4 `this` 和 `super` 的区别？

**答：**

| 关键字 | 作用 | 用法 |
|--------|------|------|
| `this` | 指代当前对象 | `this.属性`、`this.方法()`、`this()` 调用本类构造方法 |
| `super` | 指代父类对象 | `super.属性`、`super.方法()`、`super()` 调用父类构造方法 |

**构造方法中的调用：**

```java
class Parent {
    Parent() { System.out.println("父类构造"); }
}

class Child extends Parent {
    Child() {
        super();  // 调用父类构造，不写也会默认在第一行
        System.out.println("子类构造");
    }
}
```

### 2.5 `final` 关键字的作用是什么？可以修饰哪些内容？

**答：**

| 修饰内容 | 效果 |
|---------|------|
| 类 | 该类不可被继承（如 String、Math） |
| 方法 | 该方法不可被子类重写 |
| 变量（基本类型） | 值不可修改 |
| 变量（引用类型） | 引用不可修改，但对象内部可修改 |

```java
final int num = 10;
// num = 20;  // 报错

final List<String> list = new ArrayList<>();
list.add("a");    // 可以
// list = new LinkedList<>();  // 报错
```

---

## 三、集合框架（List、Set、Map）

### 3.1 简述 Java 集合框架的层次结构。

**答：**

```
┌─────────────────────────────────────────────┐
│           Collection (接口)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   List   │  │   Set    │  │  Queue   │   │
│  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│           Map (接口)                         │
│  (Key-Value 结构，不继承 Collection)         │
└─────────────────────────────────────────────┘
```

**主要实现类：**

| 接口 | 实现类 | 特点 |
|------|--------|------|
| List | ArrayList | 数组实现，查询快，插入慢 |
| List | LinkedList | 链表实现，查询慢，插入快 |
| List | Vector | 线程安全，性能差，已不推荐 |
| Set | HashSet | 哈希表，无序，不重复 |
| Set | TreeSet | 红黑树，有序，不重复 |
| Set | LinkedHashSet | 哈希表 + 链表，插入有序 |
| Map | HashMap | 哈希表，线程不安全 |
| Map | TreeMap | 红黑树，Key 有序 |
| Map | LinkedHashMap | 哈希表 + 链表，插入有序 |
| Map | Hashtable | 线程安全，性能差，已不推荐 |

### 3.2 List 的常用方法有哪些？

**答：**

```java
List<String> list = new ArrayList<>();

// 添加
list.add("a");
list.add(1, "b");  // 指定索引插入
list.addAll(Arrays.asList("c", "d"));

// 获取
String s = list.get(0);
int size = list.size();

// 删除
list.remove(0);        // 按索引删除
list.remove("a");      // 按对象删除
list.clear();

// 判断
boolean isEmpty = list.isEmpty();
boolean contains = list.contains("a");

// 遍历
for (String str : list) { ... }
list.forEach(s -> System.out.println(s));

// 转换
Object[] arr = list.toArray();
String[] strArr = list.toArray(new String[0]);
```

### 3.3 ArrayList 和 LinkedList 的区别？如何选择？

**答：**

| 特性 | ArrayList | LinkedList |
|------|-----------|------------|
| 底层 | 动态数组 | 双向链表 |
| 查询 | O(1) 快 | O(n) 慢 |
| 头部插入 | O(n) | O(1) |
| 内存 | 连续空间 | 额外存储前后指针 |
| 随机访问 | 支持 | 不支持 |

**选择建议：**
- 频繁查询 → ArrayList
- 频繁头部/中间插入删除 → LinkedList

### 3.4 Set 如何保证元素不重复？HashSet 的实现原理？

**答：**

**HashSet 底层基于 HashMap 实现：**

```java
// HashSet 源码
public class HashSet<E> extends AbstractSet<E> {
    private transient HashMap<E, Object> map;
    private static final Object PRESENT = new Object();

    public boolean add(E e) {
        return map.put(e, PRESENT) == null;
    }
}
```

- 元素作为 HashMap 的 key 存储，value 固定为 `PRESENT`（一个空对象）。
- 利用 HashMap 的 key 唯一性保证 Set 元素不重复。
- 判断重复依据：`hashCode()` + `equals()`，所以自定义类存入 HashSet 需重写这两个方法。

### 3.5 Map 的常用方法有哪些？

**答：**

```java
Map<String, Integer> map = new HashMap<>();

// 添加/修改
map.put("apple", 10);
map.putIfAbsent("banana", 20);

// 获取
Integer val = map.get("apple");
Integer valOrDefault = map.getOrDefault("orange", 0);

// 删除
map.remove("apple");

// 判断
boolean containsKey = map.containsKey("apple");
boolean containsValue = map.containsValue(10);

// 遍历 Key
for (String key : map.keySet()) { ... }

// 遍历 Entry（推荐）
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    System.out.println(entry.getKey() + ": " + entry.getValue());
}

// forEach
map.forEach((k, v) -> System.out.println(k + ": " + v));
```

### 3.6 HashMap 的工作原理是什么？简述 `put` 流程。

**答：**

**底层结构：** 数组 + 链表 + 红黑树（JDK 1.8）。

**put 流程：**

1. 计算 key 的 hash 值。
2. 如果数组为空，初始化数组（默认 16）。
3. 根据 hash 找到数组下标位置。
4. 如果该位置为空，直接插入。
5. 如果该位置有元素，遍历链表/红黑树：
   - key 相同则替换 value。
   - key 不同则插入链表尾部。
6. 链表长度 ≥ 8 且数组长度 ≥ 64 时，转为红黑树。
7. 检查 size 超过阈值（数组长度 × 0.75）则扩容。

### 3.7 什么是 fail-fast 机制？

**答：**

- **fail-fast：** 当迭代器遍历集合时，如果集合结构被修改（add/remove），会抛出 `ConcurrentModificationException`。
- **原理：** 维护一个 `modCount` 记录修改次数，迭代器创建时记录 `expectedModCount`，遍历过程中比较两者是否一致。

**避免方式：**
- 使用迭代器的 `remove()` 方法。
- 使用 `CopyOnWriteArrayList` 等并发集合。

---

## 四、日期、Math、枚举

### 4.1 JDK 8 新增的日期时间类有哪些？为什么要新增？

**答：**

**旧 API 问题：**
- Date、Calendar 可变，线程不安全。
- 设计混乱，月份从 0 开始。

**新 API（java.time 包）：**

| 类 | 说明 |
|----|------|
| `LocalDate` | 日期（年月日） |
| `LocalTime` | 时间（时分秒） |
| `LocalDateTime` | 日期 + 时间 |
| `ZonedDateTime` | 带时区的日期时间 |
| `Instant` | 时间戳 |
| `Duration` | 时间段（秒/纳秒） |
| `Period` | 日期间隔（年月日） |

### 4.2 LocalDate 和 LocalDateTime 的常用操作示例。

**答：**

```java
// 获取当前日期
LocalDate today = LocalDate.now();

// 指定日期
LocalDate date = LocalDate.of(2023, 10, 1);

// 获取信息
int year = date.getYear();
Month month = date.getMonth();
int day = date.getDayOfMonth();

// 日期运算
LocalDate tomorrow = today.plusDays(1);
LocalDate nextMonth = today.plusMonths(1);
LocalDate lastWeek = today.minusWeeks(1);

// 比较
boolean isAfter = today.isAfter(date);
boolean isBefore = today.isBefore(date);
boolean isEqual = today.isEqual(date);

// 格式化
DateTimeFormatter fmt = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
String str = LocalDateTime.now().format(fmt);
LocalDateTime parsed = LocalDateTime.parse("2023-10-01 12:00:00", fmt);
```

### 4.3 Math 类的常用方法有哪些？

**答：**

```java
// 绝对值
Math.abs(-5);  // 5

// 取整
Math.floor(3.8);   // 3.0 向下
Math.ceil(3.2);    // 4.0 向上
Math.round(3.5);   // 4 四舍五入

// 最值
Math.max(10, 20);  // 20
Math.min(10, 20);  // 10

// 幂运算
Math.pow(2, 3);    // 8.0

// 平方根
Math.sqrt(9);      // 3.0

// 随机数 [0.0, 1.0)
double random = Math.random();
int intRandom = (int) (Math.random() * 100);  // 0-99
```

### 4.4 什么是枚举？枚举的常见用法有哪些？

**答：**

**枚举（enum）**：表示一组固定常量的特殊类。

**基本用法：**

```java
// 定义枚举
public enum Season {
    SPRING, SUMMER, AUTUMN, WINTER
}

// 使用
Season s = Season.SPRING;
switch (s) {
    case SPRING: System.out.println("春天"); break;
    case SUMMER: System.out.println("夏天"); break;
}
```

**带属性的枚举：**

```java
public enum Color {
    RED("#FF0000"),
    GREEN("#00FF00"),
    BLUE("#0000FF");

    private String hex;

    Color(String hex) {
        this.hex = hex;
    }

    public String getHex() {
        return hex;
    }
}
```

**遍历枚举：**

```java
for (Color c : Color.values()) {
    System.out.println(c.name() + ": " + c.ordinal() + ", " + c.getHex());
}
```

---

## 五、数据流与文件操作

### 5.1 简述 Java IO 流的分类。

**答：**

| 分类方式 | 类型 |
|---------|------|
| **数据流向** | 输入流、输出流 |
| **数据单位** | 字节流、字符流 |
| **功能** | 节点流、处理流（缓冲流等） |

**四大基类：**

| 基类 | 类型 |
|------|------|
| `InputStream` | 字节输入流 |
| `OutputStream` | 字节输出流 |
| `Reader` | 字符输入流 |
| `Writer` | 字符输出流 |

### 5.2 使用 FileInputStream 和 FileOutputStream 复制文件。

**答：**

```java
public class FileCopy {
    public static void main(String[] args) {
        String src = "src.txt";
        String dest = "dest.txt";

        try (
            FileInputStream fis = new FileInputStream(src);
            FileOutputStream fos = new FileOutputStream(dest)
        ) {
            byte[] buffer = new byte[1024];
            int len;
            while ((len = fis.read(buffer)) != -1) {
                fos.write(buffer, 0, len);
            }
            System.out.println("复制成功");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

### 5.3 使用缓冲流提升 IO 性能。

**答：**

```java
// 字节缓冲流
try (
    BufferedInputStream bis = new BufferedInputStream(new FileInputStream(src));
    BufferedOutputStream bos = new BufferedOutputStream(new FileOutputStream(dest))
) {
    byte[] buffer = new byte[8192];
    int len;
    while ((len = bis.read(buffer)) != -1) {
        bos.write(buffer, 0, len);
    }
}

// 字符缓冲流
try (
    BufferedReader br = new BufferedReader(new FileReader("a.txt"));
    BufferedWriter bw = new BufferedWriter(new FileWriter("b.txt"))
) {
    String line;
    while ((line = br.readLine()) != null) {
        bw.write(line);
        bw.newLine();
    }
}
```

### 5.4 JDK 7 的 try-with-resources 语法是什么？

**答：**

- 自动关闭资源，无需在 `finally` 中手动 `close()`。
- 资源类需实现 `AutoCloseable` 或 `Closeable` 接口。

```java
// 旧写法
FileInputStream fis = null;
try {
    fis = new FileInputStream("file.txt");
    // 使用 fis
} catch (IOException e) {
    e.printStackTrace();
} finally {
    if (fis != null) {
        try {
            fis.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}

// 新写法
try (FileInputStream fis = new FileInputStream("file.txt")) {
    // 使用 fis
} catch (IOException e) {
    e.printStackTrace();
}
```

### 5.5 Files 类（JDK 7+）的常用操作。

**答：**

```java
import java.nio.file.*;

Path path = Paths.get("test.txt");

// 创建文件
Files.createFile(path);

// 删除文件
Files.delete(path);
Files.deleteIfExists(path);

// 复制
Files.copy(path, Paths.get("copy.txt"), StandardCopyOption.REPLACE_EXISTING);

// 移动/重命名
Files.move(path, Paths.get("new.txt"));

// 读取所有行
List<String> lines = Files.readAllLines(path, StandardCharsets.UTF_8);

// 写入
Files.write(path, lines, StandardCharsets.UTF_8);

// 判断
boolean exists = Files.exists(path);
boolean isDir = Files.isDirectory(path);
boolean isReadable = Files.isReadable(path);
```

---

## 六、异常处理

### 6.1 Java 异常的体系结构是怎样的？

**答：**

```
Throwable
├── Error（错误，系统级，无法处理）
│   ├── OutOfMemoryError
│   └── StackOverflowError
└── Exception（异常）
    ├── RuntimeException（运行时异常，非受检）
    │   ├── NullPointerException
    │   ├── IndexOutOfBoundsException
    │   ├── IllegalArgumentException
    │   └── ClassCastException
    └── 其他（受检异常）
        ├── IOException
        └── SQLException
```

### 6.2 受检异常和非受检异常的区别？

**答：**

| 特性 | 受检异常（Checked Exception） | 非受检异常（Unchecked Exception） |
|------|-----------------------------|----------------------------------|
| 继承 | Exception（除 RuntimeException） | RuntimeException / Error |
| 是否必须捕获 | 是 | 否 |
| 举例 | IOException、SQLException | NullPointerException、IndexOutOfBoundsException |
| 用途 | 外部依赖错误（如文件不存在） | 程序逻辑错误（如空指针、越界） |

### 6.3 `try-catch-finally` 的执行顺序？

**答：**

```java
try {
    // 可能异常的代码
} catch (Exception e) {
    // 捕获异常
} finally {
    // 无论是否异常都会执行
}
```

**注意：**
- `finally` 中最好不要 `return`，会覆盖 try/catch 中的返回值。
- 若 `try` 中 `System.exit(0)`，`finally` 不会执行。

### 6.4 项目中如何实现全局异常处理（Spring Boot）？

**答：**

**1. 自定义业务异常：**

```java
public class BusinessException extends RuntimeException {
    private int code;
    
    public BusinessException(int code, String message) {
        super(message);
        this.code = code;
    }
    
    public int getCode() { return code; }
}
```

**2. 统一响应类：**

```java
public class Result<T> {
    private int code;
    private String message;
    private T data;
    
    public static <T> Result<T> success(T data) { ... }
    public static <T> Result<T> error(int code, String message) { ... }
}
```

**3. 全局异常处理器：**

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public Result<?> handleBusinessException(BusinessException e) {
        return Result.error(e.getCode(), e.getMessage());
    }

    @ExceptionHandler(Exception.class)
    public Result<?> handleException(Exception e) {
        return Result.error(500, "系统错误");
    }
}
```

**4. 使用：**

```java
@Service
public class UserService {
    public User getUser(Long id) {
        if (id == null) {
            throw new BusinessException(400, "ID不能为空");
        }
        return userDao.findById(id);
    }
}
```

---

## 七、多线程及其加锁

### 7.1 线程的生命周期有哪些状态？

**答：**

```
New（新建） → Runnable（就绪/运行） → Blocked（阻塞） → Waiting（等待） → Timed Waiting（定时等待） → Terminated（终止）
```

**状态切换：**
- `sleep()` → Timed Waiting
- `wait()` → Waiting
- `join()` → Waiting
- `synchronized` 锁竞争 → Blocked

### 7.2 创建线程的几种方式？

**答：**

**方式一：继承 Thread 类**

```java
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("线程执行");
    }
}

new MyThread().start();
```

**方式二：实现 Runnable 接口**

```java
class MyRunnable implements Runnable {
    @Override
    public void run() {
        System.out.println("线程执行");
    }
}

new Thread(new MyRunnable()).start();

// 或 Lambda
new Thread(() -> System.out.println("线程执行")).start();
```

**方式三：实现 Callable + FutureTask（有返回值）**

```java
class MyCallable implements Callable<Integer> {
    @Override
    public Integer call() throws Exception {
        return 100;
    }
}

FutureTask<Integer> task = new FutureTask<>(new MyCallable());
new Thread(task).start();
Integer result = task.get();  // 阻塞等待结果
```

**方式四：线程池（推荐）**

```java
ExecutorService pool = Executors.newFixedThreadPool(5);
pool.execute(() -> System.out.println("线程执行"));
pool.shutdown();
```

### 7.3 `sleep()` 和 `wait()` 的区别？

**答：**

| 特性 | `Thread.sleep()` | `Object.wait()` |
|------|-----------------|-----------------|
| 所属类 | Thread | Object |
| 锁释放 | 不释放 | 释放 |
| 用途 | 暂停执行 | 线程通信 |
| 唤醒 | 时间到自动唤醒 | `notify()`/`notifyAll()` 唤醒 |

### 7.4 什么是 `synchronized`？如何使用？

**答：**

**作用：** 保证原子性、可见性、有序性。

**使用方式：**

```java
// 1. 修饰实例方法（锁 this）
public synchronized void method1() { ... }

// 2. 修饰静态方法（锁 Class 对象）
public static synchronized void method2() { ... }

// 3. 修饰代码块
public void method3() {
    synchronized (this) {  // 锁 this
        ...
    }
    
    synchronized (MyClass.class) {  // 锁 Class
        ...
    }
    
    Object lock = new Object();
    synchronized (lock) {  // 锁任意对象
        ...
    }
}
```

### 7.5 什么是线程安全？如何保证线程安全？

**答：**

**线程安全：** 多线程并发访问共享数据时，程序仍能正确执行。

**保证方式：**
1. 原子类（AtomicInteger、AtomicLong 等）。
2. 同步锁（synchronized、ReentrantLock）。
3. 并发集合（ConcurrentHashMap、CopyOnWriteArrayList）。
4. ThreadLocal 线程隔离。

---

## 八、其他常见面试题

### 8.1 `String`、`StringBuilder`、`StringBuffer` 的区别？

**答：**

| 特性 | String | StringBuilder | StringBuffer |
|------|--------|---------------|--------------|
| 可变性 | 不可变 | 可变 | 可变 |
| 线程安全 | - | 不安全 | 安全（synchronized） |
| 性能 | 低（频繁创建新对象） | 高 | 中 |
| 适用场景 | 少量字符串操作 | 单线程大量操作 | 多线程大量操作 |

**String 不可变的原因：**

```java
// String 源码
public final class String {
    private final char value[];  // final 数组，引用不可变
}
```

### 8.2 什么是装箱和拆箱？

**答：**

| 基本类型 | 包装类型 |
|---------|---------|
| int | Integer |
| long | Long |
| double | Double |
| boolean | Boolean |
| char | Character |

**示例：**

```java
// 装箱：基本类型 → 包装类型
Integer i = 10;  // 自动装箱，等价于 Integer.valueOf(10)

// 拆箱：包装类型 → 基本类型
int j = i;       // 自动拆箱，等价于 i.intValue()
```

**Integer 缓存池：**

```java
Integer a = 127;
Integer b = 127;
a == b;  // true（缓存池内）

Integer c = 128;
Integer d = 128;
c == d;  // false（超出缓存池 -128~127）
```

### 8.3 `equals()` 和 `==` 的区别？

**答：**

| 比较 | `==` | `equals()` |
|------|------|-----------|
| 基本类型 | 比较值 | - |
| 引用类型 | 比较内存地址 | 默认比较地址，可重写比较内容 |

```java
String s1 = new String("hello");
String s2 = new String("hello");
s1 == s2;        // false（不同对象）
s1.equals(s2);   // true（String 重写了 equals）
```

### 8.4 Java 中参数传递是值传递还是引用传递？

**答：**

**Java 只有值传递！**

- 基本类型：传递值的副本。
- 引用类型：传递引用的副本（副本指向同一个对象）。

```java
void test(int a) {
    a = 100;  // 不影响原变量
}

void test(Person p) {
    p.setName("Tom");  // 修改对象内容，原对象会改变
    p = new Person();  // 修改引用副本，不影响原引用
}
```

### 8.5 什么是抽象类和接口？它们的区别？

**答：**

| 特性 | 抽象类 | 接口 |
|------|--------|------|
| 关键字 | `abstract class` | `interface` |
| 构造方法 | 有 | 无 |
| 成员变量 | 可定义实例变量 | 只能是 `public static final` |
| 方法 | 抽象方法 + 普通方法 | JDK 8+ 可默认/静态方法 |
| 继承 | `extends` 单继承 | `implements` 多实现 |
| 设计目的 | 代码复用 | 定义契约 |

---

> 本题集适合中级 Java 工程师面试复习，涵盖 Java 核心基础的常见面试点，可结合代码练习加深理解。