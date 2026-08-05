# Java 集合框架详解

> 本文档系统梳理 Java 集合框架的完整体系，涵盖 List、Set、Map 三大接口家族的核心类、底层实现原理、源码级解析及实战选择策略。

---

## 目录

- [一、集合体系架构](#一集合体系架构)
- [二、List 系列](#二list-系列)
  - [2.1 ArrayList 底层实现与源码分析](#21-arraylist-底层实现与源码分析)
  - [2.2 LinkedList 底层实现](#22-linkedlist-底层实现)
  - [2.3 ArrayList vs LinkedList 选择策略](#23-arraylist-vs-linkedlist-选择策略)
  - [2.4 CopyOnWriteArrayList（并发）](#24-copyonwritearraylist并发)
- [三、Set 系列](#三set-系列)
  - [3.1 HashSet 实现原理](#31-hashset-实现原理)
  - [3.2 TreeSet 实现原理](#32-treeset-实现原理)
  - [3.3 LinkedHashSet 实现原理](#33-linkedhashset-实现原理)
- [四、Map 系列](#四map-系列)
  - [4.1 HashMap 深度解析](#41-hashmap-深度解析)
  - [4.2 ConcurrentHashMap 解析](#42-concurrenthashmap-解析)
  - [4.3 TreeMap 与红黑树](#43-treemap-与红黑树)
  - [4.4 LinkedHashMap（LRU 缓存实现）](#44-linkedhashmaplru-缓存实现)
- [五、Queue 与 Deque](#五queue-与-deque)
- [六、集合算法与工具](#六集合算法与工具)
- [七、常见面试题](#七常见面试题)

---

## 一、集合体系架构

```
                 Iterable (可迭代)
                      │
                 Collection (集合)
                /      |       \
              List    Set      Queue
             /   \    |  \     /   |   \
          ArrayList LinkedList HashSet TreeSet Deque
             │        │    |      |      │
             │        │    |      |   ArrayDeque
             │        │    |      │   LinkedList
             │        │    |      │      │
             └────────┴────┴──────┘      │
                       │                   │
                    Map (接口)             │
                   /   |   \              │
               HashMap TreeMap LinkedHashMap
```

### 核心接口关系

| 接口 | 特点 | 实现类 |
|------|------|--------|
| **List** | 有序、可重复、可通过索引访问 | ArrayList, LinkedList, Vector |
| **Set** | 无序（除 TreeSet）、不可重复 | HashSet, TreeSet, LinkedHashSet |
| **Map** | 键值对存储、键不可重复 | HashMap, TreeMap, LinkedHashMap, ConcurrentHashMap |
| **Queue** | 先进先出（FIFO） | LinkedList, ArrayDeque, PriorityQueue |
| **Deque** | 双端队列，可作栈使用 | ArrayDeque, LinkedList |

### 底层数据结构分类

| 结构类型 | 代表类 | 特点 |
|---------|--------|------|
| **动态数组** | ArrayList | 随机访问快，尾部添加快 |
| **双向链表** | LinkedList | 头尾操作快，随机访问慢 |
| **哈希表+链表** | HashMap, HashSet | 快速查找和插入 |
| **哈希表+红黑树** | HashMap (JDK8+) | 哈希冲突严重时自动转换 |
| **红黑树** | TreeMap, TreeSet | 有序，查找插入 O(log n) |
| **跳表** | ConcurrentSkipListMap | 并发友好的有序结构 |

---

## 二、List 系列

### 2.1 ArrayList 底层实现与源码分析

#### 底层结构

```java
public class ArrayList<E> extends AbstractList<E>
        implements List<E>, RandomAccess, Cloneable, java.io.Serializable {
    
    // 默认初始容量
    private static final int DEFAULT_CAPACITY = 10;
    
    // 存储元素的数组（Object 类型）
    private transient Object[] elementData;
    
    // 实际元素数量
    private int size;
    
    // 最大数组容量（避免内存溢出）
    private static final int MAX_ARRAY_SIZE = Integer.MAX_VALUE - 8;
}
```

#### 核心方法解析

**add() 方法 - 尾部添加**

```java
public boolean add(E e) {
    // 1. 检查容量是否足够
    ensureCapacityInternal(size + 1);
    // 2. 在尾部添加元素
    elementData[size++] = e;
    return true;
}

// 扩容检查
private void ensureCapacityInternal(int minCapacity) {
    // 如果数组为空，使用默认容量或需求容量
    if (elementData == DEFAULTCAPACITY_EMPTY_ELEMENTDATA) {
        minCapacity = Math.max(DEFAULT_CAPACITY, minCapacity);
    }
    ensureExplicitCapacity(minCapacity);
}

// 实际扩容
private void grow(int minCapacity) {
    int oldCapacity = elementData.length;
    // 新容量 = 旧容量 + 旧容量/2 = 1.5倍
    int newCapacity = oldCapacity + (oldCapacity >> 1);
    
    // 如果新容量仍然不够，直接使用所需容量
    if (newCapacity - minCapacity < 0) {
        newCapacity = minCapacity;
    }
    
    // 防止溢出
    if (newCapacity - MAX_ARRAY_SIZE > 0) {
        newCapacity = hugeCapacity(minCapacity);
    }
    
    // 数组拷贝（创建新数组，将旧数据复制过去）
    elementData = Arrays.copyOf(elementData, newCapacity);
}
```

**get() 方法 - 随机访问**

```java
public E get(int index) {
    // 检查索引合法性
    rangeCheck(index);
    // 直接通过数组下标访问，O(1)
    return elementData[index];
}

private void rangeCheck(int index) {
    if (index >= size) {
        throw new IndexOutOfBoundsException(outOfBoundsMsg(index));
    }
}
```

**remove() 方法 - 删除元素**

```java
public E remove(int index) {
    rangeCheck(index);
    E oldValue = elementData(index);
    
    // 需要移动元素的个数
    int numMoved = size - index - 1;
    if (numMoved > 0) {
        // 数组拷贝：将后面的元素前移
        System.arraycopy(elementData, index+1, elementData, index, numMoved);
    }
    
    // 清空最后一个位置（便于 GC）
    elementData[--size] = null;
    return oldValue;
}
```

#### ArrayList 特点总结

| 特性 | 说明 |
|------|------|
| 底层结构 | Object[] 动态数组 |
| 随机访问 | O(1) |
| 尾部添加 | O(1)（平均） |
| 中间插入/删除 | O(n) |
| 扩容机制 | 1.5 倍扩容 |
| 线程安全 | 否 |
| 空元素 | 允许 null |

#### 使用建议

```java
// 1. 指定初始容量（重要！）
// 避免频繁扩容（扩容涉及数组复制，非常消耗性能）
ArrayList<String> list = new ArrayList<>(1000);

// 2. 批量添加时使用 ensureCapacity
list.ensureCapacity(10000);
for (int i = 0; i < 10000; i++) {
    list.add("item" + i);
}

// 3. 遍历方式选择
// 优先使用增强 for 循环（效率高）
for (String item : list) {
    System.out.println(item);
}

// 需要删除元素时使用 Iterator
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    String item = it.next();
    if (item.startsWith("remove")) {
        it.remove(); // 安全删除
    }
}

// 多线程环境使用 Collections.synchronizedList
List<String> syncList = Collections.synchronizedList(new ArrayList<>());
```

---

### 2.2 LinkedList 底层实现

#### 底层结构

```java
public class LinkedList<E> extends AbstractSequentialList<E>
        implements List<E>, Deque<E>, Cloneable, java.io.Serializable {
    
    // 元素数量
    transient int size = 0;
    
    // 头节点
    transient Node<E> first;
    
    // 尾节点
    transient Node<E> last;
    
    // 内部节点类（双向链表）
    private static class Node<E> {
        E item;       // 元素值
        Node<E> next; // 后继节点
        Node<E> prev; // 前驱节点
        
        Node(Node<E> prev, E element, Node<E> next) {
            this.item = element;
            this.next = next;
            this.prev = prev;
        }
    }
}
```

#### 核心方法

```java
// 尾部添加（O(1)）
public boolean add(E e) {
    linkLast(e);
    return true;
}

void linkLast(E e) {
    final Node<E> l = last;
    final Node<E> newNode = new Node<>(l, e, null);
    last = newNode;
    if (l == null) {
        first = newNode;
    } else {
        l.next = newNode;
    }
    size++;
    modCount++;
}

// 头部添加（O(1)）
public void addFirst(E e) {
    linkFirst(e);
}

private void linkFirst(E e) {
    final Node<E> f = first;
    final Node<E> newNode = new Node<>(null, e, f);
    first = newNode;
    if (f == null) {
        last = newNode;
    } else {
        f.prev = newNode;
    }
    size++;
}

// 随机访问（O(n) - 需要遍历链表）
public E get(int index) {
    checkElementIndex(index);
    return node(index).item;
}

// 优化：根据索引位置选择从头或尾遍历
Node<E> node(int index) {
    // 如果 index < size/2，从头开始
    if (index < (size >> 1)) {
        Node<E> x = first;
        for (int i = 0; i < index; i++) {
            x = x.next;
        }
        return x;
    } else {
        // 否则从尾开始
        Node<E> x = last;
        for (int i = size - 1; i > index; i--) {
            x = x.prev;
        }
        return x;
    }
}
```

#### LinkedList 作为队列和栈

```java
// 作为队列（FIFO - 先进先出）
public void queueDemo() {
    Queue<String> queue = new LinkedList<>();
    queue.offer("first");   // 入队
    queue.offer("second");
    String first = queue.poll();  // 出队：返回 "first"
    String peek = queue.peek();   // 查看队头：返回 "second"（不移除）
}

// 作为栈（LIFO - 后进先出）
public void stackDemo() {
    Deque<String> stack = new LinkedList<>();
    stack.push("bottom");    // 压栈
    stack.push("top");
    String top = stack.pop(); // 出栈：返回 "top"
    String peek = stack.peek();// 查看栈顶：返回 "bottom"
}
```

---

### 2.3 ArrayList vs LinkedList 选择策略

| 操作 | ArrayList | LinkedList |
|------|-----------|------------|
| 随机访问（get） | O(1) 快 | O(n) 慢 |
| 尾部添加（add） | O(1) 快 | O(1) 快 |
| 头部添加 | O(n) 慢 | O(1) 快 |
| 头部删除 | O(n) 慢 | O(1) 快 |
| 中间插入/删除 | O(n) 慢 | O(n) 慢 |
| 内存占用 | 较小 | 较大（每个节点额外两个指针） |

**选择建议：**
- 绝大多数场景使用 `ArrayList`（随机访问快、CPU 缓存友好）
- `LinkedList` 适合频繁在头部/中间插入删除的场景
- 作为栈/队列使用时，`LinkedList` 效率高

---

### 2.4 CopyOnWriteArrayList（并发）

```java
/**
 * CopyOnWriteArrayList - 线程安全的 List
 * 核心思想：写操作时复制整个数组（Copy On Write）
 * 适合读多写少的场景
 */
public class CopyOnWriteArrayList<E> implements List<E> {
    
    // 使用 volatile 保证可见性
    private transient volatile Object[] array;
    
    // 读操作：无锁，直接读取
    public E get(int index) {
        return getArray()[index];
    }
    
    // 写操作：加锁，复制新数组
    public boolean add(E e) {
        final ReentrantLock lock = this.lock;
        lock.lock();
        try {
            Object[] elements = getArray();
            int len = elements.length;
            // 创建新数组
            Object[] newElements = Arrays.copyOf(elements, len + 1);
            newElements[len] = e;
            // 替换数组引用
            setArray(newElements);
            return true;
        } finally {
            lock.unlock();
        }
    }
    
    public E set(int index, E element) {
        final ReentrantLock lock = this.lock;
        lock.lock();
        try {
            Object[] elements = getArray();
            E oldValue = (E) elements[index];
            if (oldValue != element) {
                int len = elements.length;
                Object[] newElements = Arrays.copyOf(elements, len);
                newElements[index] = element;
                setArray(newElements);
            }
            return oldValue;
        } finally {
            lock.unlock();
        }
    }
}
```

**使用场景：**
- 白名单、黑名单配置
- 事件监听器列表
- 配置项列表（读多写少）
- 迭代时不会抛 ConcurrentModificationException

---

## 三、Set 系列

### 3.1 HashSet 实现原理

#### 底层结构

```java
/**
 * HashSet 底层使用 HashMap
 * 元素作为 HashMap 的 key
 * value 是固定的 Object 常量
 */
public class HashSet<E> implements Set<E> {
    
    private transient HashMap<E, Object> map;
    
    // 固定的 value
    private static final Object PRESENT = new Object();
    
    public HashSet() {
        map = new HashMap<>();
    }
    
    public HashSet(int initialCapacity) {
        map = new HashMap<>(initialCapacity);
    }
    
    // 添加元素
    public boolean add(E e) {
        // 如果 key 不存在，put 返回 null
        // 如果 key 已存在，put 返回旧值（PRESENT）
        return map.put(e, PRESENT) == null;
    }
    
    // 判断包含
    public boolean contains(Object o) {
        return map.containsKey(o);
    }
    
    // 删除
    public boolean remove(Object o) {
        return map.remove(o) == PRESENT;
    }
}
```

#### HashSet 去重原理

```java
/**
 * HashSet 判断元素重复的过程：
 * 1. 计算元素的 hashCode
 * 2. 通过 hash 定位到数组的某个位置（桶）
 * 3. 遍历该桶内的链表/红黑树
 * 4. 使用 equals() 比较元素是否相等
 * 5. 如果找到相等元素 → 不添加（返回 false）
 * 6. 如果未找到 → 添加到链表/红黑树中
 */

// 示例：自定义对象必须正确重写 hashCode 和 equals
public class Student {
    private String id;
    private String name;
    
    @Override
    public int hashCode() {
        return Objects.hash(id, name);
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (!(obj instanceof Student)) return false;
        Student other = (Student) obj;
        return Objects.equals(this.id, other.id);
    }
}

// 使用
Set<Student> set = new HashSet<>();
set.add(new Student("001", "Alice"));
set.add(new Student("002", "Bob"));
set.add(new Student("001", "Alice")); // 重复，不会添加
```

---

### 3.2 TreeSet 实现原理

```java
/**
 * TreeSet 底层使用 TreeMap（红黑树）
 * 元素按自然顺序或自定义比较器排序
 */
public class TreeSet<E> implements NavigableSet<E> {
    
    private NavigableMap<E, Object> m;
    
    // 自然排序（元素必须实现 Comparable）
    public TreeSet() {
        this.m = new TreeMap<>();
    }
    
    // 自定义排序
    public TreeSet(Comparator<? super E> comparator) {
        this.m = new TreeMap<>(comparator);
    }
    
    // 添加元素
    public boolean add(E e) {
        return m.put(e, PRESENT) == null;
    }
    
    // 支持范围操作
    public NavigableSet<E> subSet(E fromElement, E toElement) {
        return m.subMap(fromElement, true, toElement, false).keySet();
    }
    
    public NavigableSet<E> headSet(E toElement) {
        return m.headMap(toElement, false).keySet();
    }
    
    public NavigableSet<E> tailSet(E fromElement) {
        return m.tailMap(fromElement, true).keySet();
    }
}

// 使用示例
public class TreeSetDemo {
    public static void main(String[] args) {
        // 自然排序
        Set<String> words = new TreeSet<>();
        words.add("banana");
        words.add("apple");
        words.add("cherry");
        // 输出：[apple, banana, cherry]
        
        // 自定义排序（按字符串长度）
        Set<String> byLength = new TreeSet<>(Comparator.comparingInt(String::length));
        byLength.add("a");
        byLength.add("bb");
        byLength.add("ccc");
        byLength.add("d"); // 长度相同，会被认为重复！
        
        // 解决：比较器增加次级比较
        Set<String> byLengthV2 = new TreeSet<>(
            Comparator.comparingInt(String::length)
                .thenComparing(Comparator.naturalOrder())
        );
        byLengthV2.add("a");
        byLengthV2.add("bb");
        byLengthV2.add("d"); // 长度相同，但内容不同，会保留
    }
}
```

---

### 3.3 LinkedHashSet 实现原理

```java
/**
 * LinkedHashSet 继承自 HashSet
 * 底层使用 LinkedHashMap
 * 保持元素的插入顺序
 */
public class LinkedHashSet<E> extends HashSet<E> {
    
    // 调用父类构造方法，指定 LinkedHashMap
    public LinkedHashSet(int initialCapacity, float loadFactor) {
        super(initialCapacity, loadFactor, true);
        // super(initialCapacity, loadFactor, dummy) 
        // dummy 参数为 true 时创建 LinkedHashMap
    }
    
    public LinkedHashSet() {
        super(16, .75f, true);
    }
    
    public LinkedHashSet(Collection<? extends E> c) {
        super(Math.max(2 * c.size(), 11), .75f, true);
        addAll(c);
    }
}

// 使用场景：需要保持插入顺序且元素唯一
public class LinkedHashSetDemo {
    public static void main(String[] args) {
        // 去重同时保持顺序
        Set<String> uniqueWords = new LinkedHashSet<>(Arrays.asList(
            "hello", "world", "hello", "java", "world"
        ));
        // 输出：[hello, world, java]
        
        // 推荐用于：
        // 1. 需要保持插入顺序的去重场景
        // 2. 日志分析（按首次出现顺序统计不同 IP）
    }
}
```

---

## 四、Map 系列

### 4.1 HashMap 深度解析

#### 底层结构（JDK 8+）

```java
public class HashMap<K,V> extends AbstractMap<K,V> {
    
    // 默认初始容量 16
    static final int DEFAULT_INITIAL_CAPACITY = 1 << 4;
    
    // 最大容量 2^30
    static final int MAXIMUM_CAPACITY = 1 << 30;
    
    // 默认负载因子 0.75
    static final float DEFAULT_LOAD_FACTOR = 0.75f;
    
    // 树化阈值：链表长度 >= 8 时转为红黑树
    static final int TREEIFY_THRESHOLD = 8;
    
    // 树退化阈值：红黑树节点 <= 6 时转为链表
    static final int UNTREEIFY_THRESHOLD = 6;
    
    // 最小树化容量：数组长度 >= 64 才进行树化
    static final int MIN_TREEIFY_CAPACITY = 64;
    
    // 存储节点的数组
    transient Node<K,V>[] table;
    
    // 元素数量
    transient int size;
    
    // 扩容阈值
    int threshold;
    
    // 负载因子
    final float loadFactor;
    
    // 链表节点
    static class Node<K,V> implements Map.Entry<K,V> {
        final int hash;
        final K key;
        V value;
        Node<K,V> next;
        
        Node(int hash, K key, V value, Node<K,V> next) {
            this.hash = hash;
            this.key = key;
            this.value = value;
            this.next = next;
        }
    }
}
```

#### hash 计算（扰动函数）

```java
// HashMap 的 hash 方法
static final int hash(Object key) {
    int h;
    // 高 16 位与低 16 位异或
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}

/**
 * 为什么要这样设计？
 * 1. 防止 hashCode 计算得太烂
 * 2. 让高位信息参与运算，减少哈希冲突
 * 3. 性能开销极小（一个位移加一个异或）
 */
```

#### put 方法流程

```java
public V put(K key, V value) {
    return putVal(hash(key), key, value, false, true);
}

final V putVal(int hash, K key, V value, boolean onlyIfAbsent, boolean evict) {
    Node<K,V>[] tab; 
    Node<K,V> p; 
    int n, i;
    
    // 1. 如果 table 为空，初始化
    if ((tab = table) == null || (n = tab.length) == 0) {
        n = (tab = resize()).length;
    }
    
    // 2. 计算位置：(n-1) & hash
    // 等价于 hash % n，但位运算更快
    if ((p = tab[i = (n - 1) & hash]) == null) {
        // 该位置为空，直接创建新节点
        tab[i] = newNode(hash, key, value, null);
    } else {
        Node<K,V> e; 
        K k;
        
        // 3. 检查第一个节点
        if (p.hash == hash && ((k = p.key) == key || (key != null && key.equals(k)))) {
            e = p; // 键完全匹配
        } else if (p instanceof TreeNode) {
            // 4. 如果是红黑树，调用树的插入方法
            e = ((TreeNode<K,V>)p).putTreeVal(this, tab, hash, key, value);
        } else {
            // 5. 遍历链表
            for (int binCount = 0; ; ++binCount) {
                if ((e = p.next) == null) {
                    // 到达链表尾部，创建新节点
                    p.next = newNode(hash, key, value, null);
                    
                    // 6. 链表长度超过阈值，树化
                    if (binCount >= TREEIFY_THRESHOLD - 1) {
                        treeifyBin(tab, hash);
                    }
                    break;
                }
                
                // 如果找到相同的 key
                if (e.hash == hash && ((k = e.key) == key || (key != null && key.equals(k)))) {
                    break;
                }
                p = e;
            }
        }
        
        // 7. 更新已有节点的值
        if (e != null) {
            V oldValue = e.value;
            if (!onlyIfAbsent || oldValue == null) {
                e.value = value;
            }
            return oldValue;
        }
    }
    
    ++modCount;
    
    // 8. 检查是否需要扩容
    if (++size > threshold) {
        resize();
    }
    return null;
}
```

#### 扩容机制

```java
final Node<K,V>[] resize() {
    Node<K,V>[] oldTab = table;
    int oldCap = (oldTab == null) ? 0 : oldTab.length;
    int oldThr = threshold;
    int newCap, newThr = 0;
    
    // 1. 计算新容量（2倍）
    if (oldCap > 0) {
        if (oldCap >= MAXIMUM_CAPACITY) {
            threshold = Integer.MAX_VALUE;
            return oldTab;
        } else if ((newCap = oldCap << 1) < MAXIMUM_CAPACITY && oldCap >= DEFAULT_INITIAL_CAPACITY) {
            newThr = oldThr << 1;
        }
    }
    
    // 2. 创建新数组
    Node<K,V>[] newTab = (Node<K,V>[])new Node[newCap];
    
    // 3. 遍历旧数组，重新分配每个节点
    for (int j = 0; j < oldCap; ++j) {
        Node<K,V> e;
        if ((e = oldTab[j]) != null) {
            oldTab[j] = null;
            
            if (e.next == null) {
                // 单节点：直接计算新位置
                newTab[e.hash & (newCap - 1)] = e;
            } else if (e instanceof TreeNode) {
                // 红黑树：拆分
                ((TreeNode<K,V>)e).split(this, newTab, j, oldCap);
            } else {
                // 链表：拆分为两条链表
                Node<K,V> loHead = null, loTail = null;
                Node<K,V> hiHead = null, hiTail = null;
                Node<K,V> next;
                
                do {
                    next = e.next;
                    // 计算节点在新数组中的位置
                    if ((e.hash & oldCap) == 0) {
                        // 位置不变
                        if (loTail == null) loHead = e;
                        else loTail.next = e;
                        loTail = e;
                    } else {
                        // 位置变为 j + oldCap
                        if (hiTail == null) hiHead = e;
                        else hiTail.next = e;
                        hiTail = e;
                    }
                } while ((e = next) != null);
                
                if (loTail != null) {
                    loTail.next = null;
                    newTab[j] = loHead;
                }
                if (hiTail != null) {
                    hiTail.next = null;
                    newTab[j + oldCap] = hiHead;
                }
            }
        }
    }
    
    table = newTab;
    threshold = newThr;
    return newTab;
}
```

#### HashMap 关键参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 默认容量 | 16 | 初始数组大小 |
| 负载因子 | 0.75 | 容量利用率阈值 |
| 树化阈值 | 8 | 链表长度转红黑树 |
| 树退化阈值 | 6 | 红黑树转链表 |
| 最小树化容量 | 64 | 数组长度要求 |

---

### 4.2 ConcurrentHashMap 解析

#### JDK 7：分段锁

```java
/**
 * JDK 7 ConcurrentHashMap 使用分段锁（Segment）
 * - 将数据分成多个 Segment
 * - 每个 Segment 独立加锁
 * - 默认 16 个 Segment，并发度为 16
 */
public class ConcurrentHashMap<K,V> {
    
    static final int DEFAULT_CONCURRENCY_LEVEL = 16;
    
    final Segment<K,V>[] segments;
    
    static final class Segment<K,V> extends ReentrantLock implements Serializable {
        volatile int count;
        HashEntry<K,V>[] table;
        int threshold;
        final float loadFactor;
    }
    
    public V put(K key, V value) {
        int hash = hash(key);
        // 找到对应的 Segment
        Segment<K,V> seg = segmentFor(hash);
        return seg.put(key, hash, value, false);
    }
    
    // Segment 的 put 方法
    V put(K key, int hash, V value, boolean onlyIfAbsent) {
        HashEntry<K,V> node = tryLock() ? null : scanAndLockForPut(key, hash, value);
        
        V oldValue;
        try {
            HashEntry<K,V>[] tab = table;
            int index = (tab.length - 1) & hash;
            HashEntry<K,V> first = entryForHash(tab, index);
            
            for (HashEntry<K,V> e = first;;) {
                if (e != null) {
                    K k;
                    if ((k = e.key) == key || (hash == e.hash && key.equals(k))) {
                        oldValue = e.value;
                        if (!onlyIfAbsent) {
                            e.value = value;
                            ++modCount;
                        }
                        return oldValue;
                    }
                    HashEntry<K,V> next = e.next;
                    if (next == null) {
                        node = new HashEntry<>(hash, key, value, first);
                        int c = count++;
                        if (c > threshold && tab.length < MAXIMUM_CAPACITY) {
                            rehash(node);
                        }
                        break;
                    }
                    e = next;
                } else {
                    node = new HashEntry<>(hash, key, value, first);
                    int c = count++;
                    if (c > threshold && tab.length < MAXIMUM_CAPACITY) {
                        rehash(node);
                    }
                    break;
                }
            }
        } finally {
            unlock();
        }
        return null;
    }
}
```

#### JDK 8：CAS + synchronized

```java
/**
 * JDK 8 ConcurrentHashMap 改进：
 * - 取消 Segment 分段锁
 * - 使用 CAS + synchronized
 * - 锁粒度细化到桶（Node）级别
 * - 结构与 HashMap 类似
 */
public class ConcurrentHashMap<K,V> extends AbstractMap<K,V> {
    
    private static final int DEFAULT_INITIAL_CAPACITY = 16;
    private static final float LOAD_FACTOR = 0.75f;
    static final int TREEIFY_THRESHOLD = 8;
    
    transient volatile Node<K,V>[] table;
    private transient volatile Node<K,V>[] nextTable;
    
    final V putVal(K key, V value, boolean onlyIfAbsent) {
        if (key == null || value == null) throw new NullPointerException();
        
        int hash = spread(key.hashCode());
        int binCount = 0;
        
        for (Node<K,V>[] tab = table;;) {
            Node<K,V> f; 
            int n, i, fh;
            
            // 1. 表为空则初始化
            if (tab == null) {
                tab = initTable();
            }
            // 2. 目标桶为空 → CAS 直接写入
            else if ((f = tabAt(tab, i = (n-1) & hash)) == null) {
                if (casTabAt(tab, i, null, new Node<>(hash, key, value)))
                    break; // CAS 成功
            }
            // 3. 正在扩容，协助迁移
            else if ((fh = f.hash) == MOVED) {
                tab = helpTransfer(tab, f);
            }
            // 4. 桶不为空 → 加 synchronized 锁
            else {
                V oldVal = null;
                synchronized (f) {
                    // 再次确认桶头节点
                    if (tabAt(tab, i) == f) {
                        if (fh >= 0) {
                            // 链表处理
                            binCount = 1;
                            for (Node<K,V> e = f;; ++binCount) {
                                if (e.hash == hash && 
                                    ((k = e.key) == key || (key != null && key.equals(k)))) {
                                    oldVal = e.val;
                                    if (!onlyIfAbsent) {
                                        e.val = value;
                                    }
                                    break;
                                }
                                
                                Node<K,V> pred = e;
                                if ((e = e.next) == null) {
                                    pred.next = new Node<>(hash, key, value);
                                    break;
                                }
                            }
                        } else if (f instanceof TreeBin) {
                            // 红黑树处理
                            Node<K,V> p;
                            binCount = 2;
                            if ((p = ((TreeBin<K,V>)f).putTreeVal(hash, key, value)) != null) {
                                oldVal = p.val;
                                if (!onlyIfAbsent) {
                                    p.val = value;
                                }
                            }
                        }
                    }
                }
                
                if (binCount != 0) {
                    if (binCount >= TREEIFY_THRESHOLD - 1) {
                        treeifyBin(tab, hash);
                    }
                    break;
                }
            }
        }
        
        if (binCount != 0) {
            if (binCount >= TREEIFY_THRESHOLD - 1) {
                treeifyBin(tab, hash);
            }
        }
        return null;
    }
}
```

---

### 4.3 TreeMap 与红黑树

#### 红黑树特性

```java
/**
 * 红黑树是一种自平衡的二叉搜索树
 * 
 * 特性：
 * 1. 节点是红色或黑色
 * 2. 根节点是黑色
 * 3. 所有叶子节点（NIL）是黑色
 * 4. 红色节点的子节点必须是黑色
 *    （不能有连续的红色节点）
 * 5. 从任一节点到其每个叶子的所有路径
 *    包含相同数量的黑色节点
 * 
 * 这些约束保证：最长路径不超过最短路径的两倍
 * 因此查找、插入、删除都是 O(log n)
 */

public class TreeMap<K,V> extends AbstractMap<K,V> {
    
    private final Comparator<? super K> comparator;
    private transient Entry<K,V> root;
    private transient int size;
    private transient int modCount;
    
    // 红黑树节点
    static final class Entry<K,V> implements Map.Entry<K,V> {
        K key;
        V value;
        Entry<K,V> left;
        Entry<K,V> right;
        Entry<K,V> parent;
        boolean color = BLACK;
        
        // 旋转操作（插入/删除时保持平衡）
        // 左旋：以 x 为支点，x 的右子节点 y 上移
        // 右旋：以 x 为支点，x 的左子节点 y 上移
        
        // 变色操作
        // 违反规则时需要调整颜色
    }
}
```

---

### 4.4 LinkedHashMap（LRU 缓存实现）

```java
/**
 * LinkedHashMap 在 HashMap 基础上增加了双向链表
 * 可以实现 LRU（最近最少使用）缓存
 */
public class LinkedHashMap<K,V> extends HashMap<K,V> {
    
    // 双向链表节点
    static class Entry<K,V> extends HashMap.Node<K,V> {
        Entry<K,V> before, after;
        
        Entry(int hash, K key, V value, HashMap.Node<K,V> next) {
            super(hash, key, value, next);
        }
    }
    
    // 双向链表头尾
    transient Entry<K,V> head;
    transient Entry<K,V> tail;
    
    // 迭代顺序：false=插入顺序，true=访问顺序
    final boolean accessOrder;
}

// 经典 LRU 缓存实现
public class LRUCache<K, V> extends LinkedHashMap<K, V> {
    
    private final int maxSize;
    
    public LRUCache(int maxSize) {
        super(16, 0.75f, true); // accessOrder = true
        this.maxSize = maxSize;
    }
    
    // 重写淘汰策略
    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        // 当缓存超过最大容量时，移除最久未访问的
        return size() > maxSize;
    }
    
    public V get(K key) {
        V value = super.get(key);
        // 这里会触发 afterNodeAccess，将节点移到链表尾部
        return value;
    }
    
    public void put(K key, V value) {
        super.put(key, value);
    }
}

// 使用示例
public class LRUDemo {
    public static void main(String[] args) {
        LRUCache<String, Integer> cache = new LRUCache<>(3);
        
        cache.put("A", 1);
        cache.put("B", 2);
        cache.put("C", 3);
        // 缓存：[A, B, C]（从最久到最新）
        
        cache.get("A"); // 访问 A，将 A 移到最新
        // 缓存：[B, C, A]
        
        cache.put("D", 4); // 添加 D，超过容量，淘汰最久的 B
        // 缓存：[C, A, D]
        
        System.out.println(cache); // {C=3, A=1, D=4}
    }
}
```

---

## 五、Queue 与 Deque

### 优先队列 PriorityQueue

```java
/**
 * PriorityQueue - 基于最小堆
 * 不是先进先出，而是按优先级排序
 */
public class PriorityQueueDemo {
    
    public static void main(String[] args) {
        // 默认：自然顺序（最小的先出）
        PriorityQueue<Integer> minHeap = new PriorityQueue<>();
        minHeap.offer(5);
        minHeap.offer(1);
        minHeap.offer(3);
        
        System.out.println(minHeap.poll()); // 1（最小）
        System.out.println(minHeap.poll()); // 3
        System.out.println(minHeap.poll()); // 5
        
        // 最大堆
        PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Comparator.reverseOrder());
        maxHeap.offer(5);
        maxHeap.offer(1);
        maxHeap.offer(3);
        
        System.out.println(maxHeap.poll()); // 5（最大）
        
        // 自定义对象排序
        PriorityQueue<Task> taskQueue = new PriorityQueue<>(
            (t1, t2) -> t2.priority - t1.priority
        );
        taskQueue.offer(new Task("低优先级", 1));
        taskQueue.offer(new Task("高优先级", 10));
        taskQueue.offer(new Task("中优先级", 5));
        
        // 按优先级从高到低执行
        while (!taskQueue.isEmpty()) {
            System.out.println("执行：" + taskQueue.poll().name);
        }
    }
    
    static class Task {
        String name;
        int priority;
        
        Task(String name, int priority) {
            this.name = name;
            this.priority = priority;
        }
    }
}
```

### ArrayDeque 与 LinkedList 对比

```java
/**
 * ArrayDeque vs LinkedList
 * 
 * ArrayDeque：
 * - 基于循环数组
 * - 头尾添加删除都是 O(1)
 * - 比 LinkedList 性能更好
 * - 作为栈时推荐使用
 * 
 * LinkedList：
 * - 基于双向链表
 * - 随机访问 O(n)
 * - 内存开销更大
 * - 支持 null 元素
 */

public class DequeComparison {
    
    public static void main(String[] args) {
        // 推荐使用 ArrayDeque 作为栈
        Deque<String> stack = new ArrayDeque<>();
        stack.push("first");
        stack.push("second");
        String top = stack.pop(); // "second"
        
        // 推荐使用 ArrayDeque 作为队列
        Deque<String> queue = new ArrayDeque<>();
        queue.offer("first");
        queue.offer("second");
        String head = queue.poll(); // "first"
    }
}
```

---

## 六、集合算法与工具

### Collections 工具类

```java
public class CollectionsDemo {
    
    public static void main(String[] args) {
        List<Integer> list = Arrays.asList(5, 3, 8, 1, 9, 2);
        
        // 排序
        Collections.sort(list);
        // [1, 2, 3, 5, 8, 9]
        
        // 自定义排序
        Collections.sort(list, (a, b) -> b - a);
        // [9, 8, 5, 3, 2, 1]
        
        // 二分查找（必须有序）
        int index = Collections.binarySearch(list, 5);
        
        // 打乱顺序
        Collections.shuffle(list);
        
        // 反转
        Collections.reverse(list);
        
        // 查找最大/最小
        int max = Collections.max(list);
        int min = Collections.min(list);
        
        // 统计频率
        int freq = Collections.frequency(list, 5);
        
        // 不可变集合
        List<String> immutableList = Collections.unmodifiableList(new ArrayList<>());
        Map<String, Integer> immutableMap = Collections.unmodifiableMap(new HashMap<>());
        
        // 同步集合（线程安全）
        List<String> syncList = Collections.synchronizedList(new ArrayList<>());
        Set<String> syncSet = Collections.synchronizedSet(new HashSet<>());
    }
}
```

### Arrays 工具类

```java
public class ArraysDemo {
    
    public static void main(String[] args) {
        int[] arr = {5, 3, 8, 1, 9, 2};
        
        // 排序
        Arrays.sort(arr);
        // [1, 2, 3, 5, 8, 9]
        
        // 二分查找
        int index = Arrays.binarySearch(arr, 5);
        
        // 填充
        int[] filled = new int[5];
        Arrays.fill(filled, 10);
        // [10, 10, 10, 10, 10]
        
        // 复制
        int[] copy = Arrays.copyOf(arr, arr.length);
        
        // 转字符串
        String str = Arrays.toString(arr);
        // "[1, 2, 3, 5, 8, 9]"
        
        // 转 List
        List<Integer> list = Arrays.asList(1, 2, 3);
        
        // 深度比较
        int[][] matrix1 = {{1, 2}, {3, 4}};
        int[][] matrix2 = {{1, 2}, {3, 4}};
        boolean equal = Arrays.deepEquals(matrix1, matrix2);
    }
}
```

### Java 9+ 工厂方法

```java
public class ModernCollectionDemo {
    
    public static void main(String[] args) {
        // 不可变集合（Java 9+）
        List<String> list = List.of("A", "B", "C");
        Set<String> set = Set.of("X", "Y", "Z");
        Map<String, Integer> map = Map.of("one", 1, "two", 2);
        
        // 创建后不可修改
        // list.add("D"); // UnsupportedOperationException
        
        // 也可以使用 var（Java 10+）
        var names = List.of("Alice", "Bob", "Charlie");
        var scores = Map.of("math", 95, "english", 88);
    }
}
```

---

## 七、常见面试题

### Q1: HashMap 和 ConcurrentHashMap 的区别？

| 特性 | HashMap | ConcurrentHashMap |
|------|---------|-------------------|
| 线程安全 | 否 | 是 |
| null key | 允许 | 不允许 |
| null value | 允许 | 不允许 |
| 加锁方式 | 无锁 | CAS + synchronized |
| 并发度 | 1 | JDK7:16 / JDK8:桶级别 |

### Q2: HashMap 的扩容过程？

1. 触发条件：`size > capacity * loadFactor`
2. 新容量 = 旧容量 × 2
3. 创建新数组
4. 遍历旧数组每个桶
5. 链表节点：根据 `(hash & oldCap)` 判断位置是否改变
   - 结果为 0：位置不变
   - 结果不为 0：位置变为 `j + oldCap`
6. 红黑树：先拆分成两条链表，再分别处理

### Q3: 为什么 HashMap 用红黑树而不是 AVL 树？

- **红黑树**：插入/删除时最多 2 次旋转，性能更高
- **AVL 树**：严格平衡，插入/删除可能需要多次旋转
- HashMap 中**哈希冲突通常不会很严重**，红黑树足够用
- 红黑树保证**最长路径不超过最短路径的两倍**

### Q4: ArrayList 和 LinkedList 如何选择？

- **ArrayList**：随机访问多、尾部操作多
- **LinkedList**：头部/中间插入删除多
- 绝大多数情况选 `ArrayList`（CPU 缓存友好）

### Q5: 如何实现线程安全的 List？

1. `Collections.synchronizedList()` - 简单但效率低
2. `CopyOnWriteArrayList` - 读多写少
3. `ConcurrentLinkedQueue` - 非阻塞队列
4. 手动同步（synchronized 或 ReentrantLock）

### Q6: HashSet 如何保证元素不重复？

- 先比较 `hashCode()` 定位桶位置
- 再用 `equals()` 比较链表中的元素
- **必须同时正确重写 `hashCode` 和 `equals`**

### Q7: HashMap 的 key 能用自定义对象吗？

可以，但必须满足：
1. 正确重写 `hashCode()` 和 `equals()`
2. 对象最好是不可变的（final 类或只提供 getter）
3. 如果是可变对象，修改后 hash 变化会导致无法查找

### Q8: 什么是快速失败（Fail-Fast）？

```java
// 迭代时修改集合会抛 ConcurrentModificationException
List<String> list = new ArrayList<>(Arrays.asList("A", "B", "C"));
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    String s = it.next();
    list.add("D"); // 抛异常！
}

// 解决方法：使用 Iterator.remove()
while (it.hasNext()) {
    String s = it.next();
    if ("A".equals(s)) {
        it.remove(); // 正确删除方式
    }
}
```

### Q9: Map 的遍历方式有哪些？

```java
Map<String, Integer> map = new HashMap<>();

// 方式一：遍历 key
for (String key : map.keySet()) {
    System.out.println(key);
}

// 方式二：遍历 value
for (Integer value : map.values()) {
    System.out.println(value);
}

// 方式三：遍历 entry（推荐，效率高）
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    System.out.println(entry.getKey() + " = " + entry.getValue());
}

// 方式四：Java 8+ Lambda
map.forEach((key, value) -> System.out.println(key + " = " + value));
```

### Q10: 如何优化集合性能？

1. **指定初始容量**：避免频繁扩容
   ```java
   HashMap<String, Integer> map = new HashMap<>(1000);
   ```
2. **使用合适的集合类型**：根据需求选择
3. **使用 `System.arraycopy` 批量操作**
4. **使用并行流**处理大数据集（Java 8+）
5. **避免在循环中频繁调用 `size()`**
   ```java
   int size = list.size();
   for (int i = 0; i < size; i++) { ... }
   ```
6. **使用 `Set`/`Map` 时正确实现 `hashCode`/`equals`**
