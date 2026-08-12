# Java 集合常用操作 API 详解

---

## 目录

- [1. Java 集合框架总览](#1-java-集合框架总览)
  - [1.1 架构图](#11-架构图)
  - [1.2 核心接口对比](#12-核心接口对比)
  - [1.3 常用实现类选择](#13-常用实现类选择)
- [2. Collection 接口通用方法](#2-collection-接口通用方法)
  - [2.1 增操作](#21-增操作)
  - [2.2 删操作](#22-删操作)
  - [2.3 查操作](#23-查操作)
  - [2.4 判空与大小](#24-判空与大小)
  - [2.5 转数组](#25-转数组)
  - [2.6 批量操作](#26-批量操作)
  - [2.7 Java 8+ 新方法](#27-java-8-新方法)
- [3. List 接口](#3-list-接口)
  - [3.1 List 特有方法](#31-list-特有方法)
  - [3.2 ArrayList](#32-arraylist)
  - [3.3 LinkedList](#33-linkedlist)
  - [3.4 Vector 与 Stack](#34-vector-与-stack)
  - [3.5 List 实现类对比](#35-list-实现类对比)
- [4. Set 接口](#4-set-接口)
  - [4.1 Set 接口方法](#41-set-接口方法)
  - [4.2 HashSet](#42-hashset)
  - [4.3 LinkedHashSet](#43-linkedhashset)
  - [4.4 TreeSet](#44-treeset)
  - [4.5 Set 实现类对比](#45-set-实现类对比)
- [5. Map 接口](#5-map-接口)
  - [5.1 Map 核心方法](#51-map-核心方法)
  - [5.2 遍历方式](#52-遍历方式)
  - [5.3 HashMap](#53-hashmap)
  - [5.4 LinkedHashMap](#54-linkedhashmap)
  - [5.5 TreeMap](#55-treemap)
  - [5.6 Hashtable 与 ConcurrentHashMap](#56-hashtable-与-concurrenthashmap)
  - [5.7 Map 实现类对比](#57-map-实现类对比)
  - [5.8 Java 8+ Map 新方法](#58-java-8-map-新方法)
- [6. Queue / Deque 接口](#6-queue--deque-接口)
  - [6.1 Queue 接口方法](#61-queue-接口方法)
  - [6.2 Deque 接口方法](#62-deque-接口方法)
  - [6.3 LinkedList 作队列](#63-linkedlist-作队列)
  - [6.4 ArrayDeque](#64-arraydeque)
  - [6.5 PriorityQueue（优先级队列）](#65-priorityqueue优先级队列)
- [7. 迭代器 Iterator](#7-迭代器-iterator)
  - [7.1 Iterator 方法](#71-iterator-方法)
  - [7.2 ListIterator](#72-listiterator)
  - [7.3 增强 for 循环（for-each）](#73-增强-for-循环for-each)
  - [7.4 fail-fast 与 fail-safe](#74-fail-fast-与-fail-safe)
- [8. Collections 工具类](#8-collections-工具类)
  - [8.1 排序操作](#81-排序操作)
  - [8.2 查找与替换](#82-查找与替换)
  - [8.3 同步控制](#83-同步控制)
  - [8.4 不可变集合](#84-不可变集合)
  - [8.5 其他工具方法](#85-其他工具方法)
- [9. Stream API 常用操作](#9-stream-api-常用操作)
  - [9.1 Stream 创建](#91-stream-创建)
  - [9.2 中间操作](#92-中间操作)
  - [9.3 终端操作](#93-终端操作)
  - [9.4 Collectors 收集器](#94-collectors-收集器)
- [10. 常见面试题与实战场景](#10-常见面试题与实战场景)
  - [10.1 ArrayList 与 LinkedList 区别](#101-arraylist-与-linkedlist-区别)
  - [10.2 HashMap 底层原理](#102-hashmap-底层原理)
  - [10.3 HashMap 与 Hashtable 区别](#103-hashmap-与-hashtable-区别)
  - [10.4 去重的几种方式](#104-去重的几种方式)
  - [10.5 List 转 Map 与分组](#105-list-转-map-与分组)
  - [10.6 fail-fast 原理](#106-fail-fast-原理)

---

## 1. Java 集合框架总览

### 1.1 架构图

```
java.lang.Iterable<T>
    └── Collection<E>                          // 根接口
        ├── List<E>                            // 有序、可重复
        │   ├── ArrayList
        │   ├── LinkedList
        │   └── Vector
        │       └── Stack
        ├── Set<E>                             // 无序、不可重复
        │   ├── HashSet
        │   │   └── LinkedHashSet
        │   └── SortedSet<E>
        │       └── NavigableSet<E>
        │           └── TreeSet
        └── Queue<E>                           // 队列
            └── Deque<E>
                ├── LinkedList
                └── ArrayDeque

Map<K,V>                                       // 键值对（独立分支）
    ├── HashMap
    │   └── LinkedHashMap
    ├── Hashtable
    └── SortedMap<K,V>
        └── NavigableMap<K,V>
            └── TreeMap
```

---

### 1.2 核心接口对比

| 接口 | 是否允许重复 | 是否有序 | 线程安全 | 典型实现 |
|---|:---:|:---:|:---:|---|
| **List** | ✅ | ✅（插入顺序） | ❌ | ArrayList、LinkedList |
| **Set** | ❌ | ❌（HashSet）/ ✅（TreeSet） | ❌ | HashSet、TreeSet |
| **Queue** | ✅ | ✅（FIFO 等） | ❌ | ArrayDeque、PriorityQueue |
| **Map** | Key 不重复 | ❌（HashMap）/ ✅（TreeMap） | ❌ | HashMap、TreeMap |

---

### 1.3 常用实现类选择

```
选择 List：
  ├── 随机访问多 → ArrayList
  └── 头尾增删多 → LinkedList / ArrayDeque

选择 Set：
  ├── 无需排序 → HashSet
  ├── 保插入序 → LinkedHashSet
  └── 需自然/自定义排序 → TreeSet

选择 Map：
  ├── 通用场景 → HashMap
  ├── 保插入序 → LinkedHashMap
  ├── 需 Key 排序 → TreeMap
  └── 高并发 → ConcurrentHashMap
```

---

## 2. Collection 接口通用方法

> `Collection<E>` 是 List、Set、Queue 的父接口，以下方法它们全部继承可用。

### 2.1 增操作

```java
// 添加单个元素，成功返回 true
boolean add(E e);

List<String> list = new ArrayList<>();
list.add("Java");     // true
list.add("Python");   // true
```

---

### 2.2 删操作

```java
// 删除单个元素（删除第一个匹配项），成功返回 true
boolean remove(Object o);

list.remove("Java");  // true，删除第一个 "Java"
list.remove("C++");   // false，不存在

// 删除满足条件的元素（Java 8+）
default boolean removeIf(Predicate<? super E> filter);

list.removeIf(s -> s.length() > 5);
```

---

### 2.3 查操作

```java
boolean contains(Object o);

list.add("Java");
list.contains("Java");  // true
list.contains("Go");    // false
```

---

### 2.4 判空与大小

```java
int size();
boolean isEmpty();

list.size();     // 2
list.isEmpty();  // false
```

---

### 2.5 转数组

```java
Object[] toArray();
<T> T[] toArray(T[] a);

List<String> list = Arrays.asList("A", "B", "C");
Object[] arr1 = list.toArray();
String[] arr2 = list.toArray(new String[0]);   // 推荐写法
```

---

### 2.6 批量操作

```java
boolean addAll(Collection<? extends E> c);
boolean removeAll(Collection<?> c);
boolean retainAll(Collection<?> c);
boolean containsAll(Collection<?> c);
void clear();

List<String> a = new ArrayList<>(Arrays.asList("A","B","C","D"));
List<String> b = Arrays.asList("B","C","E");

a.removeAll(b);   // [A, D]
a.addAll(b);      // [A, D, B, C, E]
a.retainAll(b);   // [B, C, E]
```

---

### 2.7 Java 8+ 新方法

```java
default void forEach(Consumer<? super E> action);
default Stream<E> stream();
default Stream<E> parallelStream();

list.forEach(System.out::println);
long count = list.stream().filter(s -> s.startsWith("J")).count();
```

---

## 3. List 接口

### 3.1 List 特有方法

```java
// 增
void add(int index, E element);
boolean addAll(int index, Collection<? extends E> c);

// 删
E remove(int index);

// 改
E set(int index, E element);

// 查
E get(int index);
int indexOf(Object o);
int lastIndexOf(Object o);
List<E> subList(int fromIndex, int toIndex);  // 左闭右开，原列表视图

// Java 8+
default void replaceAll(UnaryOperator<E> operator);
default void sort(Comparator<? super E> c);

// 迭代
ListIterator<E> listIterator();
ListIterator<E> listIterator(int index);
```

### 3.2 ArrayList

**特点**：动态数组实现，默认初始容量 10，扩容 ~1.5 倍。随机访问快（O(1)），中间增删慢（O(n)），线程不安全。

```java
ArrayList()
ArrayList(int initialCapacity)          // 推荐：预估容量
ArrayList(Collection<? extends E> c)

// 缩容
((ArrayList<String>) list).trimToSize();
```

### 3.3 LinkedList

**特点**：双向链表。头尾增删 O(1)，随机访问 O(n)。同时实现 List、Deque，可作栈/队列。

```java
// 栈操作（LIFO）
LinkedList<String> stack = new LinkedList<>();
stack.push("A");
stack.pop();
stack.peek();

// 队列操作（FIFO）
LinkedList<String> queue = new LinkedList<>();
queue.offer("X");
queue.poll();
```

### 3.4 Vector 与 Stack

- **Vector**：线程安全版 ArrayList，全表 synchronized，性能差（淘汰）
- **Stack**：继承 Vector，LIFO 操作（淘汰，用 ArrayDeque 代替）

### 3.5 List 实现类对比

| 特性 | ArrayList | LinkedList | Vector |
|---|---|---|---|
| 底层 | 动态数组 | 双向链表 | 动态数组 |
| 随机访问 | O(1) | O(n) | O(1) |
| 头插 | O(n) | O(1) | O(n) |
| 线程安全 | ❌ | ❌ | ✅（慢） |

---

## 4. Set 接口

### 4.1 Set 接口方法

> 不允许重复元素（基于 equals + hashCode 判断）。

```java
Set<String> set = new HashSet<>();
set.add("A");  // true
set.add("A");  // false

// List 转 Set 去重
Set<Integer> noDup = new HashSet<>(Arrays.asList(1,2,2,3));  // [1,2,3]
```

### 4.2 HashSet

基于 HashMap 的 Key，无序。增删查 O(1)。允许一个 null。

### 4.3 LinkedHashSet

继承 HashSet，基于 LinkedHashMap，**保持插入顺序**。

### 4.4 TreeSet

基于 TreeMap（红黑树），**自动排序**。增删查 O(log n)。不允许 null。元素必须实现 Comparable 或传入 Comparator。

```java
TreeSet<Integer> ts = new TreeSet<>();
ts.add(3); ts.add(1); ts.add(2);  // [1, 2, 3]

// 范围查询
ts.first(); ts.last();
ts.lower(2);   // 1
ts.higher(2);  // 3
ts.subSet(1, 3);  // [1, 2]
```

### 4.5 Set 实现类对比

| | HashSet | LinkedHashSet | TreeSet |
|---|---|---|---|
| 有序性 | 无序 | 插入顺序 | 排序序 |
| 性能 | O(1) | O(1) | O(log n) |
| null | 一个 | 一个 | ❌ |

---

## 5. Map 接口

### 5.1 Map 核心方法

```java
V put(K key, V value);           // 添加/覆盖，返回旧 Value
V remove(Object key);            // 按 Key 删除，返回旧 Value
V get(Object key);               // 取值
V getOrDefault(Object key, V def); // Java 8+
boolean containsKey(Object key);
boolean containsValue(Object value);
Set<K> keySet();
Collection<V> values();
Set<Map.Entry<K,V>> entrySet();
void clear();
```

### 5.2 遍历方式

```java
// 1) entrySet（推荐，同时取 K-V）
for (Map.Entry<String, Integer> e : map.entrySet()) {
    String k = e.getKey(); Integer v = e.getValue();
}

// 2) keySet / values
for (String k : map.keySet()) { ... }
for (Integer v : map.values()) { ... }

// 3) forEach（Java 8+，最简洁）
map.forEach((k, v) -> System.out.println(k + "=" + v));

// 4) Iterator（可遍历时删除）
Iterator<Map.Entry<String,Integer>> it = map.entrySet().iterator();
while (it.hasNext()) {
    Map.Entry<String,Integer> e = it.next();
    if (cond) it.remove();
}
```

### 5.3 HashMap

**底层（JDK 1.8+）**：数组（Node[]） + 链表 + 红黑树
- 哈希：`hash = (h = key.hashCode()) ^ (h >>> 16)`
- 定位：`i = (n-1) & hash`
- 链转树：链表长度 > 8 且 table 长度 ≥ 64
- 树转链：节点数 < 6
- 扩容：负载因子 0.75，容量 2 的幂，扩容 2 倍

### 5.4 LinkedHashMap

继承 HashMap + 双向链表。支持插入顺序（默认）或访问顺序（accessOrder=true，可实现 LRU）。

**LRU 简易实现**：
```java
class LRUCache<K,V> extends LinkedHashMap<K,V> {
    private final int maxSize;
    public LRUCache(int maxSize) {
        super(16, 0.75f, true);
        this.maxSize = maxSize;
    }
    @Override
    protected boolean removeEldestEntry(Map.Entry<K,V> eldest) {
        return size() > maxSize;
    }
}
```

### 5.5 TreeMap

基于红黑树，Key 自动排序。增删查 O(log n)。支持范围查询：
`firstKey / lastKey / lowerKey / higherKey / headMap / tailMap / subMap`

### 5.6 Hashtable vs ConcurrentHashMap

- **Hashtable**：全表 synchronized（淘汰）
- **ConcurrentHashMap**：JDK8+ CAS + 细粒度锁，首选并发容器

### 5.7 Map 实现类对比

| | HashMap | LinkedHashMap | TreeMap | Hashtable | ConcurrentHashMap |
|---|---|---|---|---|---|
| 有序性 | 无序 | 插入/访问序 | Key 排序 | 无序 | 无序 |
| null | K 1 / V 多 | 同左 | ❌ K null | ❌ | ❌ |
| 线程安全 | ❌ | ❌ | ❌ | ✅（慢） | ✅（快） |

### 5.8 Java 8+ Map 新方法

```java
map.getOrDefault("C", 0);
map.putIfAbsent("A", 100);

map.compute("A", (k, oldV) -> oldV + 10);
map.computeIfAbsent("D", k -> k.length());
map.computeIfPresent("B", (k, v) -> v * 10);

map.merge("A", 5, Integer::sum);   // 存在则 sum，不存在放 5

map.replace("A", 99);
map.replace("A", old, newV);
map.replaceAll((k, v) -> v * 2);
```

---

## 6. Queue / Deque 接口

### 6.1 Queue 方法（FIFO）

| | 抛异常 | 返回特殊值 |
|---|---|---|
| 入队 | add(e) | offer(e) |
| 出队 | remove() | poll() |
| 查看 | element() | peek() |

### 6.2 Deque 方法（双端队列 + 栈）

| | 头（抛异常） | 头（特殊值） | 尾（抛异常） | 尾（特殊值） |
|---|---|---|---|---|
| 增 | addFirst | offerFirst | addLast | offerLast |
| 删 | removeFirst | pollFirst | removeLast | pollLast |
| 查 | getFirst | peekFirst | getLast | peekLast |

**作栈**：`push(e) / pop() / peek()`（均操作头）

### 6.3 ArrayDeque

基于循环数组的双端队列。作栈比 Stack 快，作队列比 LinkedList 快。头尾操作 O(1) 均摊。

### 6.4 PriorityQueue

基于最小堆（Object[]），出队按优先级（默认最小先出）。入/出队 O(log n)，查队首 O(1)。

```java
// 最小堆（默认）
PriorityQueue<Integer> pq = new PriorityQueue<>();
pq.offer(5); pq.offer(2); pq.offer(1);
pq.poll();  // 1

// 最大堆
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Comparator.reverseOrder());
```

---

## 7. 迭代器 Iterator

### 7.1 Iterator 方法

```java
Iterator<String> it = list.iterator();
it.hasNext();
it.next();
it.remove();           // 删除 next() 返回的元素
it.forEachRemaining(System.out::println);  // Java 8+
```

### 7.2 ListIterator（List 专属）

双向迭代，支持增/改：`hasPrevious() / previous() / add() / set()`

### 7.3 for-each 循环

编译后等价于 Iterator。⚠️ 遍历时调用 `list.remove()`（非 Iterator.remove）会抛 `ConcurrentModificationException`。

### 7.4 fail-fast vs fail-safe

| | fail-fast | fail-safe |
|---|---|---|
| 代表 | ArrayList、HashMap | ConcurrentHashMap、CopyOnWriteArrayList |
| 原理 | modCount 比对，不一致直接抛异常 | 迭代快照副本 |
| 并发修改 | ❌ 禁止 | ✅ 安全（但读不到最新） |

---

## 8. Collections 工具类

### 8.1 排序

```java
Collections.sort(list);
Collections.sort(list, Comparator.reverseOrder());
Collections.shuffle(list);   // 洗牌
Collections.reverse(list);
Collections.rotate(list, 2); // 旋转
```

### 8.2 查找与替换

```java
// 二分查找（必须先升序排序！）
int idx = Collections.binarySearch(list, 5);

Collections.max(list);
Collections.min(list);
Collections.frequency(list, "A");    // 出现次数
Collections.replaceAll(list, "A", "X");
Collections.fill(list, 0);
Collections.copy(dst, src);          // dst.size >= src.size
```

### 8.3 同步控制

```java
List<String> sList = Collections.synchronizedList(new ArrayList<>());
Set<String> sSet = Collections.synchronizedSet(new HashSet<>());
Map<String,Integer> sMap = Collections.synchronizedMap(new HashMap<>());
```

### 8.4 不可变集合

```java
List<String> uList = Collections.unmodifiableList(src);  // 修改抛异常

// Java 9+ 原生（真正不可变）
List<String> il = List.of("A","B","C");
Set<String> is = Set.of("X","Y");
Map<String,Integer> im = Map.of("A",1,"B",2);
```

### 8.5 其他工具

```java
Collections.nCopies(5, 100);       // 5 个 100
Collections.emptyList();           // 空集合
Collections.singletonList("ONE");  // 单元素
Collections.disjoint(a, b);        // 无交集则 true
```

---

## 9. Stream API 常用操作

### 9.1 Stream 创建

```java
list.stream();
list.parallelStream();
Stream.of(1,2,3);
Arrays.stream(new int[]{1,2,3});
Stream.generate(() -> 1).limit(5);
Stream.iterate(0, n -> n+2).limit(5);  // 0,2,4,6,8
IntStream.range(1, 10);        // 1..9
IntStream.rangeClosed(1, 10);  // 1..10
```

### 9.2 中间操作（懒执行，返回 Stream）

```java
list.stream()
    .filter(n -> n > 2)           // 过滤
    .distinct()                   // 去重
    .sorted()                     // 排序（可传 Comparator）
    .sorted(Comparator.reverseOrder())
    .limit(3)                     // 取前 N
    .skip(3)                      // 跳前 N
    .map(n -> n * 2)              // 映射
    .mapToInt(Integer::intValue)  // 转基本类型流
    .flatMap(Collection::stream)  // 打平嵌套
    .peek(n -> log(n));           // 调试
```

### 9.3 终端操作（触发计算）

```java
// 遍历
stream.forEach(System.out::println);

// 收集
List<Integer> l = stream.collect(Collectors.toList());
Set<Integer> s = stream.collect(Collectors.toSet());
Integer[] arr = stream.toArray(Integer[]::new);

// 规约
int sum = stream.reduce(0, (acc, n) -> acc + n);

// 聚合
stream.count();
stream.max(Integer::compareTo);
stream.min(Integer::compareTo);

// IntStream 专用（更高效）
IntStream.rangeClosed(1,5).sum();
IntStream.rangeClosed(1,5).average();
IntSummaryStatistics stat = IntStream.rangeClosed(1,5).summaryStatistics();
stat.getSum() / getMax() / getMin() / getAverage() / getCount();

// 匹配
stream.allMatch(n -> n > 0);    // 全满足
stream.anyMatch(n -> n > 4);    // 任一满足
stream.noneMatch(n -> n < 0);   // 全不满足

// 查找
stream.findFirst();   // 第一个
stream.findAny();     // 任意
```

### 9.4 Collectors 收集器

```java
// 分组
Map<String, List<User>> byCity = users.stream()
    .collect(Collectors.groupingBy(User::getCity));

// 分区（true/false 两组）
Map<Boolean, List<User>> part = users.stream()
    .collect(Collectors.partitioningBy(u -> u.getAge() >= 25));

// 分组 + 二级聚合
Map<String, Long> cityCount = users.stream()
    .collect(Collectors.groupingBy(User::getCity, Collectors.counting()));

Map<String, Double> cityAvg = users.stream()
    .collect(Collectors.groupingBy(User::getCity, Collectors.averagingInt(User::getAge)));

// 转 Map（处理冲突！）
Map<String, User> map = users.stream()
    .collect(Collectors.toMap(
        User::getName,
        u -> u,
        (oldV, newV) -> newV    // 冲突处理
    ));

// 拼接
String all = users.stream()
    .map(User::getName)
    .collect(Collectors.joining(", ", "[", "]"));
```

---

## 10. 常见面试题与实战场景

### 10.1 ArrayList vs LinkedList

| | ArrayList | LinkedList |
|---|---|---|
| 底层 | 动态数组 | 双向链表 |
| 随机访问 | O(1) | O(n/2) |
| 头插 | O(n) | O(1) |
| 中间插 | O(n) | 定位 O(n) + 指针 O(1) |
| 场景 | 读多写少，随机访问多 | 头尾/中间插入频繁 |

### 10.2 HashMap 底层原理（JDK 1.8+）

数组 + 链表 + 红黑树。put 流程：
1. `hash = key.hashCode() ^ (h >>> 16)`
2. `index = (n-1) & hash`
3. 空桶 → 直接放；非空桶 → 头匹配/链表遍历/树查找
4. 链表 > 8 && 数组 ≥ 64 → 转红黑树
5. size > threshold → 扩容 2 倍（重新哈希到原位或原位+旧容量）

### 10.3 HashMap vs Hashtable

| | HashMap | Hashtable |
|---|---|---|
| 线程安全 | ❌ | ✅（全表锁） |
| null | ✅ K1/V多 | ❌ |
| 初始容量 | 16 | 11 |
| 扩容 | ×2 | ×2+1 |
| 推荐 | ✅ | ✖️ 淘汰 |

### 10.4 去重方式

```java
// 1) HashSet（不保序）
new HashSet<>(list)

// 2) LinkedHashSet（保插入序，推荐）
new ArrayList<>(new LinkedHashSet<>(list))

// 3) Stream distinct（保序）
list.stream().distinct().collect(toList())

// 4) 按属性去重（Stream + Map）
users.stream().filter(distinctByKey(User::getName)).collect(toList());
// 辅助：
static <T> Predicate<T> distinctByKey(Function<T,?> f) {
    Map<Object,Boolean> seen = new ConcurrentHashMap<>();
    return t -> seen.putIfAbsent(f.apply(t), Boolean.TRUE) == null;
}
```

### 10.5 List 转 Map / 分组

见 9.4 Collectors 部分（groupingBy / partitioningBy / toMap）。

### 10.6 fail-fast 原理

迭代器内部记录 `expectedModCount = modCount`，每次 `next()` 检查，不一致抛 `ConcurrentModificationException`。
规避：
1. `Iterator.remove()` / `ListIterator` 增删
2. 并发容器：CopyOnWriteArrayList、ConcurrentHashMap
3. `list.removeIf(...)` 或 Stream `filter` 生成新集合

---

> 文档版本：v1.0 | 更新日期：2026-08-12
