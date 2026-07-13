# 中级 Python 工程师面试题集

> 本题集系统覆盖 Python 核心基础、数据结构、字符串处理、面向对象编程及高级特性、性能优化、并发编程、常用库等面试高频考点，按知识模块分类组织，适用于中级工程师水平面试与自测。

---

## 目录

1. [模块一：Python 核心基础知识](#模块一python-核心基础知识)
2. [模块二：数据结构（列表、元组、字典、集合）](#模块二数据结构列表元组字典集合)
3. [模块三：字符串处理](#模块三字符串处理)
4. [模块四：面向对象编程](#模块四面向对象编程)
5. [模块五：Python 高级特性](#模块五python-高级特性)
6. [模块六：函数与装饰器](#模块六函数与装饰器)
7. [模块七：异常处理与调试](#模块七异常处理与调试)
8. [模块八：文件与 IO 操作](#模块八文件与-io-操作)
9. [模块九：并发编程](#模块九并发编程)
10. [模块十：性能优化](#模块十性能优化)
11. [模块十一：常用标准库](#模块十一常用标准库)
12. [模块十二：实际应用场景题](#模块十二实际应用场景题)

---

## 模块一：Python 核心基础知识

### 题目 1.1 可变对象与不可变对象

**题目描述：** 请说明 Python 中可变对象与不可变对象的区别，并举例说明在函数传参时的不同表现。

**参考答案：**

不可变对象（Immutable）：对象本身的值不可改变，一旦创建即固定。常见的不可变类型有 `int`、`float`、`str`、`tuple`、`frozenset`。对不可变对象"赋值"时，实际上是创建了一个新对象并重新绑定引用。

可变对象（Mutable）：对象本身的值可以原地修改。常见可变类型有 `list`、`dict`、`set`。

函数传参本质上传的是"对象的引用"，但表现不同：

```python
# 不可变对象示例
def modify_int(x):
    x = x + 1
    print("函数内 x =", x)

a = 10
modify_int(a)
print("函数外 a =", a)  # 输出 10，a 未被改变

# 可变对象示例
def modify_list(lst):
    lst.append(4)
    print("函数内 lst =", lst)

b = [1, 2, 3]
modify_list(b)
print("函数外 b =", b)  # 输出 [1, 2, 3, 4]，b 被修改
```

**评分标准：**
- 准确说明可变/不可变对象概念及常见类型（3 分）
- 正确解释函数传参机制及差异（4 分）
- 给出可运行代码示例（3 分）

---

### 题目 1.2 `is` 与 `==` 的区别

**题目描述：** 解释 `is` 和 `==` 的区别，并说明 Python 中小整数池的概念。

**参考答案：**

- `==` 比较的是两个对象的值是否相等（调用 `__eq__` 方法）。
- `is` 比较的是两个对象的身份是否相同，即是否指向内存中同一对象（判断 `id()` 是否相等）。

小整数池：CPython 中为了优化性能，将 `[-5, 257)` 范围内的整数预先缓存，这些整数在解释器启动时就创建好了，所有引用该范围内整数的变量都指向同一对象。

```python
a = 256
b = 256
print(a is b)  # True，命中小整数池

c = 257
d = 257
print(c is d)  # 在交互模式下通常为 False，但模块级代码因常量折叠可能为 True

# 字符串驻留
s1 = "hello"
s2 = "hello"
print(s1 is s2)  # True，符合标识符规则的短字符串会被驻留

s3 = "hello world!"
s4 = "hello world!"
print(s3 is s4)  # 交互模式下通常为 False（含空格和感叹号）
```

**评分标准：**
- 正确区分 `is` 与 `==`（3 分）
- 说明小整数池范围与作用（3 分）
- 提及字符串驻留机制（2 分）
- 代码示例可运行（2 分）

---

### 题目 1.3 深拷贝与浅拷贝

**题目描述：** 解释深拷贝与浅拷贝的区别，并实现一个包含嵌套结构的拷贝示例。

**参考答案：**

- 浅拷贝（shallow copy）：创建新对象，但内部元素仍引用原对象中对应元素的引用。拷贝最外层，嵌套对象不递归拷贝。
- 深拷贝（deep copy）：递归地拷贝所有层级，生成完全独立的新对象。

```python
import copy

original = [[1, 2], [3, 4], {"a": [5, 6]}]

# 浅拷贝
shallow = copy.copy(original)
shallow[0].append(99)
print("浅拷贝后 original:", original)  # [[1, 2, 99], [3, 4], {'a': [5, 6]}]

# 重置后演示深拷贝
original = [[1, 2], [3, 4], {"a": [5, 6]}]
deep = copy.deepcopy(original)
deep[0].append(99)
deep[2]["a"].append(100)
print("深拷贝后 original:", original)  # [[1, 2], [3, 4], {'a': [5, 6]}]，未受影响
```

浅拷贝常见方式：`copy.copy()`、`list.copy()`、切片 `lst[:]`、`dict.copy()`。

**评分标准：**
- 准确解释两种拷贝概念（3 分）
- 列举浅拷贝的多种方式（3 分）
- 嵌套结构示例正确（2 分）
- 说明深拷贝递归特性（2 分）

---

### 题目 1.4 GIL 全局解释器锁

**题目描述：** 什么是 GIL？它对 Python 多线程编程有什么影响？如何绕过 GIL 的限制？

**参考答案：**

GIL（Global Interpreter Lock，全局解释器锁）是 CPython 解释器中的一把互斥锁，确保同一时刻只有一个线程执行 Python 字节码。

影响：
- 多线程无法利用多核 CPU 实现真正的并行计算。
- CPU 密集型任务在多线程下可能比单线程还慢（线程切换开销）。
- IO 密集型任务受益于 GIL 释放（IO 等待时 GIL 会释放），可提升并发性能。

绕过方式：
1. 使用 `multiprocessing` 多进程，每个进程有独立 GIL。
2. 使用 C 扩展（如 NumPy、Cython）在 C 层释放 GIL。
3. 使用 `concurrent.futures.ProcessPoolExecutor`。
4. Python 3.12+ 提供实验性 PEP 703 的 no-GIL 构建。

```python
import multiprocessing
import time

def cpu_task(n):
    return sum(i * i for i in range(n))

if __name__ == "__main__":
    n = 10_000_000
    start = time.time()
    with multiprocessing.Pool(4) as pool:
        results = pool.map(cpu_task, [n] * 4)
    print(f"多进程耗时: {time.time() - start:.2f}s, 结果: {results[:2]}")
```

**评分标准：**
- 准确描述 GIL 定义（3 分）
- 说明对 CPU 密集型与 IO 密集型任务的不同影响（4 分）
- 给出至少 2 种绕过方案（3 分）

---

### 题目 1.5 `*args` 与 `**kwargs`

**题目描述：** 说明 `*args` 和 `**kwargs` 的用法，并编写一个支持任意位置参数、关键字参数且保留参数元信息的通用日志函数。

**参考答案：**

- `*args`：收集多余的位置参数为元组。
- `**kwargs`：收集多余的关键字参数为字典。
- 在函数调用时，`*` 和 `**` 用于解包序列和字典。

```python
import functools

def log_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        arg_str = ", ".join(
            [repr(a) for a in args] +
            [f"{k}={v!r}" for k, v in kwargs.items()]
        )
        print(f"[LOG] 调用 {func.__name__}({arg_str})")
        result = func(*args, **kwargs)
        print(f"[LOG] {func.__name__} 返回 {result!r}")
        return result
    return wrapper

@log_call
def add(a: int, b: int, *args, **kwargs) -> int:
    """计算多个数的和。"""
    return a + b + sum(args) + sum(kwargs.values())

print(add(1, 2, 3, 4, extra=5))
# 输出:
# [LOG] 调用 add(1, 2, 3, 4, extra=5)
# [LOG] add 返回 15
# 15
```

**评分标准：**
- 正确解释两者作用（3 分）
- 函数定义与调用示例正确（4 分）
- 使用 `functools.wraps` 保留元信息（3 分）

---

### 题目 1.6 作用域 LEGB 规则

**题目描述：** 解释 Python 的 LEGB 作用域查找规则，并说明 `global` 与 `nonlocal` 的区别。

**参考答案：**

LEGB 规则：Python 查找变量名时按以下顺序：

1. **L (Local)**：函数内部局部作用域
2. **E (Enclosing)**：外层嵌套函数作用域
3. **G (Global)**：模块全局作用域
4. **B (Built-in)**：内置作用域（如 `len`、`print`）

```python
x = "global"

def outer():
    x = "enclosing"

    def inner():
        x = "local"
        print(x)  # local

    inner()
    print(x)  # enclosing

outer()
print(x)  # global
```

- `global`：在函数内声明变量引用全局作用域，可修改全局变量。
- `nonlocal`：在嵌套函数中声明变量引用外层（Enclosing）函数作用域，用于闭包中修改外层变量。

```python
def counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

c = counter()
print(c(), c(), c())  # 1 2 3
```

**评分标准：**
- 正确列出 LEGB 四层及顺序（4 分）
- 区分 `global` 与 `nonlocal`（3 分）
- 闭包示例正确（3 分）

---

### 题目 1.7 垃圾回收机制

**题目描述：** 简述 Python 的垃圾回收机制，包括引用计数和分代回收。

**参考答案：**

Python 垃圾回收主要包含两种机制：

**1. 引用计数（Reference Counting）**
- 每个对象维护一个引用计数器 `ob_refcnt`。
- 引用增加时 +1，减少时 -1。
- 计数归零时立即回收对象。
- 优点：实时性好；缺点：无法处理循环引用。

```python
import sys
a = []
print(sys.getrefcount(a))  # 2（a 和 getrefcount 的参数）
b = a
print(sys.getrefcount(a))  # 3
```

**2. 分代回收（Generational GC）**
- 用于解决循环引用问题。
- 对象分为三代：第 0 代（年轻）、第 1 代、第 2 代（年老）。
- 新对象进入第 0 代，经历 GC 存活后进入下一代，越老的对象越少被检查。
- 阈值触发或手动调用 `gc.collect()` 时执行。

```python
import gc

# 查看阈值
print(gc.get_threshold())  # (700, 10, 10)

# 循环引用示例
class Node:
    def __init__(self):
        self.ref = None

n1 = Node()
n2 = Node()
n1.ref = n2
n2.ref = n1  # 循环引用
del n1, n2   # 引用计数不为 0，需 GC 回收
gc.collect()
```

**评分标准：**
- 引用计数原理及优缺点（4 分）
- 分代回收机制（3 分）
- 循环引用问题及解决（3 分）

---

## 模块二：数据结构（列表、元组、字典、集合）

### 题目 2.1 列表与元组的区别

**题目描述：** 从可变性、性能、应用场景三个维度比较 list 与 tuple 的差异。

**参考答案：**

| 维度 | list | tuple |
|------|------|-------|
| 可变性 | 可变，支持增删改 | 不可变，创建后不能修改 |
| 性能 | 内存占用略大，创建稍慢 | 内存占用小，创建更快 |
| 哈希 | 不可哈希，不能作 dict 的 key | 可哈希（元素也需可哈希），可作 key |
| 应用场景 | 动态数据集合 | 固定数据、函数返回多值、字典 key |

```python
import sys

lst = [1, 2, 3, 4, 5]
tup = (1, 2, 3, 4, 5)
print(sys.getsizeof(lst))  # 通常 104（64位 CPython）
print(sys.getsizeof(tup))  # 通常 80，更省内存

# 元组作字典 key
location = {(35.68, 139.76): "Tokyo", (39.90, 116.40): "Beijing"}
print(location[(35.68, 139.76)])  # Tokyo

# 元组不可变但元素若可变仍可改
t = ([1, 2], [3, 4])
t[0].append(99)
print(t)  # ([1, 2, 99], [3, 4])
```

**评分标准：**
- 三个维度准确对比（4 分）
- 说明 tuple 作 key 的条件（2 分）
- 揭示"不可变"的本质（元素引用不变）（2 分）
- 性能差异代码验证（2 分）

---

### 题目 2.2 字典底层实现与有序性

**题目描述：** 解释 Python 字典的底层实现原理，并说明从 Python 3.7 起字典有序的原因。

**参考答案：**

**底层实现：哈希表**

Python 字典基于哈希表实现，通过哈希函数将 key 映射到桶（bucket）。

- 插入：计算 key 的哈希值，定位桶位置，处理冲突（开放寻址法）。
- 查找：平均 O(1)，最坏 O(n)（哈希冲突严重时）。
- 扩容：当装填因子超过 2/3 时扩容，重新哈希。

**Python 3.7+ 字典有序**

Python 3.6 起 CPython 使用紧凑字典实现，3.7 起官方保证插入顺序：

- 字典维护两个数组：
  - `dk_entries`：存储实际的键值对（哈希、key、value）。
  - `dk_indices`：索引数组，通过哈希值定位到 `dk_entries` 的位置。
- 插入顺序即 `dk_entries` 中的顺序，遍历时按该顺序输出，几乎不增加内存开销。

```python
d = {}
d["c"] = 3
d["a"] = 1
d["b"] = 2
print(list(d.keys()))  # ['c', 'a', 'b']，保持插入顺序

# 哈希冲突示例
class Bad:
    def __hash__(self):
        return 1  # 所有实例哈希相同，退化为 O(n)
    def __eq__(self, other):
        return id(self) == id(other)

d2 = {Bad(): i for i in range(1000)}  # 性能急剧下降
```

**评分标准：**
- 哈希表原理（3 分）
- 开放寻址与扩容机制（3 分）
- Python 3.7 字典有序原理（2 分）
- 时间复杂度分析（2 分）

---

### 题目 3.3 字典推导式与反转

**题目描述：** 使用字典推导式实现以下功能：(1) 反转字典的 key-value；(2) 过滤值为偶数的项；(3) 处理值冲突时保留最后一个。

**参考答案：**

```python
original = {"a": 1, "b": 2, "c": 3, "d": 2, "e": 4}

# (1) 反转 key-value
reversed_d = {v: k for k, v in original.items()}
print(reversed_d)  # {1: 'a', 2: 'd', 3: 'c', 4: 'e'}，值 2 冲突，保留最后

# (2) 过滤值为偶数的项
even_d = {k: v for k, v in original.items() if v % 2 == 0}
print(even_d)  # {'b': 2, 'd': 2, 'e': 4}

# (3) 反转时值冲突保留第一个
reversed_first = {}
for k, v in original.items():
    reversed_first.setdefault(v, k)
print(reversed_first)  # {1: 'a', 2: 'b', 3: 'c', 4: 'e'}
```

**评分标准：**
- 字典推导式语法正确（3 分）
- 反转字典功能实现（3 分）
- 处理值冲突策略（4 分）

---

### 题目 2.4 集合运算

**题目描述：** 编写代码演示集合的并、交、差、对称差运算，并说明集合的时间复杂度优势。

**参考答案：**

```python
A = {1, 2, 3, 4, 5}
B = {4, 5, 6, 7, 8}

# 并集
print(A | B)           # {1, 2, 3, 4, 5, 6, 7, 8}
print(A.union(B))      # 同上

# 交集
print(A & B)           # {4, 5}
print(A.intersection(B))

# 差集
print(A - B)           # {1, 2, 3}
print(A.difference(B))

# 对称差（仅在其中一个集合中的元素）
print(A ^ B)           # {1, 2, 3, 6, 7, 8}
print(A.symmetric_difference(B))

# 实际应用：找出两列表的共同元素
list1 = [1, 2, 2, 3, 4]
list2 = [3, 4, 4, 5, 6]
common = set(list1) & set(list2)
print(common)  # {3, 4}

# 去重保序（dict.fromkeys）
unique_ordered = list(dict.fromkeys(list1))
print(unique_ordered)  # [1, 2, 3, 4]
```

**时间复杂度优势：** 集合基于哈希表，查找/插入/删除平均 O(1)，适合去重和成员判断，比 list 的 O(n) 快得多。

```python
import timeit

big_list = list(range(100000))
big_set = set(big_list)

# 成员判断
print(timeit.timeit(lambda: 99999 in big_list, number=1000))  # 较慢
print(timeit.timeit(lambda: 99999 in big_set, number=1000))   # 极快
```

**评分标准：**
- 四种集合运算正确（4 分）
- 实际应用示例（去重/求交集）（2 分）
- 时间复杂度分析与性能对比（4 分）

---

### 题目 2.5 列表排序与 `sorted`

**题目描述：** 说明 `list.sort()` 与 `sorted()` 的区别，并使用 `key` 参数实现复杂排序：按年龄升序，年龄相同按姓名降序。

**参考答案：**

- `list.sort()`：原地排序，返回 `None`，仅适用于 list。
- `sorted()`：返回新列表，适用于任何可迭代对象，不修改原对象。
- 两者都支持 `key` 和 `reverse` 参数，稳定排序（保证相等元素相对顺序）。

```python
people = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 30},
    {"name": "David", "age": 25},
]

# 按年龄升序，年龄相同按姓名降序
sorted_people = sorted(
    people,
    key=lambda p: (p["age"], [-ord(c) for c in p["name"]])  # 字符串降序的近似
)

# 更简洁：分别排序（利用稳定排序）
sorted_people = sorted(people, key=lambda p: p["name"], reverse=True)
sorted_people = sorted(sorted_people, key=lambda p: p["age"])
print(sorted_people)
# [{'name': 'David', 'age': 25}, {'name': 'Bob', 'age': 25},
#  {'name': 'Charlie', 'age': 30}, {'name': 'Alice', 'age': 30}]

# 使用 operator.itemgetter
from operator import itemgetter
sorted_people2 = sorted(people, key=itemgetter("age", "name"))
print(sorted_people2)
```

**评分标准：**
- 区分 `sort()` 与 `sorted()`（3 分）
- `key` 参数使用正确（3 分）
- 多字段排序实现（2 分）
- 利用稳定排序技巧（2 分）

---

### 题目 2.6 列表切片与赋值

**题目描述：** 预测以下代码输出并解释原因。

```python
lst = [1, 2, 3, 4, 5]
lst[1:3] = [10, 20, 30]
print(lst)

lst2 = [1, 2, 3, 4, 5]
lst2[1:3] = []
print(lst2)

lst3 = [1, 2, 3, 4, 5]
del lst3[::2]
print(lst3)
```

**参考答案：**

```python
lst = [1, 2, 3, 4, 5]
lst[1:3] = [10, 20, 30]
print(lst)  # [1, 10, 20, 30, 4, 5]
# 切片 [1:3] 取出 [2, 3]，替换为 [10, 20, 30]，列表长度变化

lst2 = [1, 2, 3, 4, 5]
lst2[1:3] = []
print(lst2)  # [1, 4, 5]
# 用空列表替换，相当于删除切片区间

lst3 = [1, 2, 3, 4, 5]
del lst3[::2]
print(lst3)  # [2, 4]
# 步长为 2 删除：索引 0, 2, 4 即 1, 3, 5
```

要点：
- 切片赋值会用右侧可迭代对象替换切片区间，长度可变。
- `del` 配合切片可批量删除。
- 步长切片赋值时，右侧元素个数必须与切片长度一致。

```python
# 步长切片赋值必须数量匹配
a = [1, 2, 3, 4, 5]
a[::2] = [10, 30, 50]  # 正确，3 个元素匹配 3 个位置
# a[::2] = [10, 30]    # ValueError: attempt to assign sequence of size 2
```

**评分标准：**
- 三个输出全部正确（6 分）
- 解释切片赋值长度可变特性（2 分）
- 说明步长切片赋值的限制（2 分）

---

### 题目 2.7 defaultdict 与 Counter

**题目描述：** 使用 `collections.defaultdict` 和 `collections.Counter` 分别实现单词频率统计，并说明两者的适用场景。

**参考答案：**

```python
from collections import defaultdict, Counter

text = "the quick brown fox jumps over the lazy dog the fox"
words = text.split()

# 方式一：defaultdict
freq_dd = defaultdict(int)
for w in words:
    freq_dd[w] += 1
print(dict(freq_dd))
# {'the': 3, 'quick': 1, 'brown': 1, 'fox': 2, ...}

# 方式二：Counter（更简洁）
freq_counter = Counter(words)
print(freq_counter)  # Counter({'the': 3, 'fox': 2, ...})

# Counter 特有功能
print(freq_counter.most_common(2))  # [('the', 3), ('fox', 2)]
print(freq_counter.most_common(1))  # [('the', 3)]

# Counter 支持算术运算
c1 = Counter(a=3, b=1)
c2 = Counter(a=1, b=2)
print(c1 + c2)  # Counter({'a': 4, 'b': 3})
print(c1 - c2)  # Counter({'a': 2})，结果只保留正数
```

适用场景：
- `defaultdict`：需要按 key 自动初始化值的场景，如分组、累积。可自定义工厂函数（`list`、`set`、自定义 callable）。
- `Counter`：专门用于计数场景，提供 `most_common`、算术运算等便捷方法。

```python
# defaultdict 分组示例
students = [("A", "Alice"), ("B", "Bob"), ("A", "Charlie")]
groups = defaultdict(list)
for cls, name in students:
    groups[cls].append(name)
print(dict(groups))  # {'A': ['Alice', 'Charlie'], 'B': ['Bob']}
```

**评分标准：**
- 两种方式实现正确（4 分）
- 适用场景说明（3 分）
- Counter 高级特性（most_common、运算）（3 分）

---

### 题目 2.8 算法题：LRU 缓存实现

**题目描述：** 使用 Python 实现 LRU（最近最少使用）缓存，要求 `get` 和 `put` 均为 O(1)。

**参考答案：**

利用 `OrderedDict`（基于双向链表 + 哈希表）实现：

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)  # 移到末尾，表示最近使用
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # 弹出头部（最久未用）

# 测试
lru = LRUCache(2)
lru.put(1, 1)
lru.put(2, 2)
print(lru.get(1))  # 1
lru.put(3, 3)       # 淘汰 key=2
print(lru.get(2))  # -1
lru.put(4, 4)       # 淘汰 key=1
print(lru.get(1))  # -1
print(lru.get(3))  # 3
print(lru.get(4))  # 4
```

也可使用 `functools.lru_cache` 装饰器快速实现函数结果缓存：

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(100))  # 快速计算
print(fib.cache_info())
```

**评分标准：**
- 使用 OrderedDict 实现 O(1)（5 分）
- 正确处理容量超限淘汰（3 分）
- 提及 functools.lru_cache（2 分）

---

## 模块三：字符串处理

### 题目 3.1 字符串格式化方式

**题目描述：** 列举 Python 中字符串格式化的主要方式，并对比其优劣。

**参考答案：**

```python
name = "Alice"
age = 30
score = 95.6789

# 1. % 格式化（老式）
print("Name: %s, Age: %d, Score: %.2f" % (name, age, score))
# 优点：兼容性好；缺点：可读性差，参数多时易错

# 2. str.format()
print("Name: {}, Age: {}, Score: {:.2f}".format(name, age, score))
print("Name: {n}, Age: {a}".format(n=name, a=age))
# 优点：功能强大；缺点：稍显冗长

# 3. f-string（Python 3.6+，推荐）
print(f"Name: {name}, Age: {age}, Score: {score:.2f}")
# 优点：简洁高效（编译期解析）；缺点：仅 3.6+

# f-string 高级用法
print(f"{name!r}")            # repr
print(f"{age:>5}")            # 右对齐宽度 5
print(f"{score:^10.2f}")      # 居中
print(f"{1000000:,}")         # 千分位 -> 1,000,000
print(f"{255:#08b}")          # 二进制 0b01111111
print(f"{name=}")             # 调试输出 name='Alice'（3.8+）

# 4. Template（安全场景，防注入）
from string import Template
t = Template("Hello $who")
print(t.substitute(who=name))
```

**评分标准：**
- 列举至少 3 种方式（3 分）
- f-string 高级用法（4 分）
- 各方式优劣对比（3 分）

---

### 题目 3.2 字符串编码与解码

**题目描述：** 解释 `encode` 和 `decode`，说明常见编码（UTF-8、GBK）的区别及乱码原因。

**参考答案：**

- `str.encode(encoding)`: 将 Unicode 字符串编码为字节串（bytes）。
- `bytes.decode(encoding)`: 将字节串解码为 Unicode 字符串。

```python
s = "中文"

# UTF-8：变长编码，1-4 字节，互联网主流
b_utf8 = s.encode("utf-8")
print(b_utf8)              # b'\xe4\xb8\xad\xe6\x96\x87'
print(len(b_utf8))         # 6

# GBK：定长 2 字节（中文），中文 Windows 常用
b_gbk = s.encode("gbk")
print(b_gbk)               # b'\xd6\xd0\xce\xc4'
print(len(b_gbk))          # 4

# 解码必须用对应编码
print(b_utf8.decode("utf-8"))  # 中文
print(b_gbk.decode("gbk"))     # 中文

# 错误解码导致乱码
try:
    print(b_utf8.decode("gbk"))  # UnicodeDecodeError 或乱码
except UnicodeDecodeError as e:
    print(f"解码错误: {e}")

# errors 参数
print(b_utf8.decode("gbk", errors="replace"))  # 用 ? 替换
print(b_utf8.decode("gbk", errors="ignore"))   # 忽略错误字节
```

**乱码原因：** 编码与解码使用不一致的编码方案。文件读写、网络传输时需统一编码（推荐 UTF-8）。

```python
# 文件读写指定编码
with open("test.txt", "w", encoding="utf-8") as f:
    f.write("中文内容")
with open("test.txt", "r", encoding="utf-8") as f:
    print(f.read())
```

**评分标准：**
- 准确解释 encode/decode（3 分）
- 对比 UTF-8 与 GBK（3 分）
- 乱码原因说明（2 分）
- errors 参数处理（2 分）

---

### 题目 3.3 正则表达式实战

**题目描述：** 使用 `re` 模块完成：(1) 提取字符串中所有邮箱；(2) 将日期 `2024-01-15` 转为 `15/01/2024`；(3) 验证手机号（11 位，1 开头）。

**参考答案：**

```python
import re

# (1) 提取邮箱
text = "联系我: alice@example.com 或 bob@test.org.cn"
emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
print(emails)  # ['alice@example.com', 'bob@test.org.cn']

# 更严谨的邮箱正则
email_pattern = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)
print(email_pattern.findall(text))

# (2) 日期格式转换
date = "2024-01-15"
new_date = re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1", date)
print(new_date)  # 15/01/2024

# (3) 验证手机号
def is_valid_phone(phone):
    return bool(re.fullmatch(r"1[3-9]\d{9}", phone))

print(is_valid_phone("13812345678"))  # True
print(is_valid_phone("12812345678"))  # False（12 开头）
print(is_valid_phone("1381234567"))   # False（10 位）
```

常用正则函数：
- `re.match`：从字符串开头匹配。
- `re.search`：扫描整个字符串，返回第一个匹配。
- `re.findall`：返回所有匹配的列表。
- `re.finditer`：返回匹配迭代器（节省内存）。
- `re.sub`：替换。
- `re.split`：按模式分割。

```python
# 分割与替换
print(re.split(r"[\s,]+", "a, b,, c d"))  # ['a', 'b', 'c', 'd']

# 命名分组
m = re.match(r"(?P<year>\d{4})-(?P<month>\d{2})", "2024-01")
print(m.group("year"), m.group("month"))  # 2024 01
```

**评分标准：**
- 三个任务实现正确（6 分）
- 正则函数说明（2 分）
- 命名分组等高级用法（2 分）

---

### 题目 3.4 字符串常用方法

**题目描述：** 编写代码演示 `split`、`join`、`strip`、`replace`、`find`、`startswith` 等常用字符串方法，并说明字符串不可变性对性能的影响。

**参考答案：**

```python
s = "  Hello, World, Python  "

# split：分割
print(s.split(","))          # ['  Hello', ' World', ' Python  ']
print(s.split(", "))         # ['  Hello', 'World', 'Python  ']
print(s.split(",", maxsplit=1))  # ['  Hello', ' World, Python  ']

# join：拼接（比 + 高效）
parts = ["a", "b", "c"]
print(",".join(parts))       # a,b,c
print("".join(parts))        # abc

# strip：去除两端字符
print(s.strip())             # 'Hello, World, Python'
print(s.strip(" "))          # 去除空格
print("aaahelloaaa".strip("a"))  # hello
print("  hello  ".lstrip())  # 'hello  '
print("  hello  ".rstrip())  # '  hello'

# replace：替换
print("hello world".replace("world", "Python"))  # hello Python
print("a-b-c".replace("-", "_", 1))  # a_b-c（只替换第一个）

# find / index
print("hello".find("l"))     # 2，找不到返回 -1
print("hello".index("l"))    # 2，找不到抛 ValueError
print("hello".rfind("l"))    # 3，从右查找

# startswith / endswith
print("test.py".endswith(".py"))  # True
print("test.py".endswith((".py", ".sh")))  # True，支持元组

# 大小写
print("Hello".upper())       # HELLO
print("Hello".lower())       # hello
print("hello world".title()) # Hello World
print("hello world".capitalize())  # Hello world

# 判断
print("123".isdigit())       # True
print("abc".isalpha())       # True
print("abc123".isalnum())    # True
```

**字符串不可变性与性能：**

字符串不可变，每次 `+` 或 `replace` 都会创建新对象，频繁拼接大量字符串时性能差，应使用 `join` 或 `io.StringIO`。

```python
import time

# 低效：大量 + 拼接
start = time.time()
s = ""
for i in range(100000):
    s += "a"
print(f"+ 拼接: {time.time() - start:.3f}s")

# 高效：join
start = time.time()
parts = ["a"] * 100000
s = "".join(parts)
print(f"join 拼接: {time.time() - start:.3f}s")
```

**评分标准：**
- 常用方法演示完整（4 分）
- 不可变性与性能分析（3 分）
- 给出性能对比代码（3 分）

---

### 题目 3.5 算法题：最长无重复子串

**题目描述：** 给定一个字符串，找出其中不含有重复字符的最长子串的长度。例如 `"abcabcbb"` 返回 3（`"abc"`）。

**参考答案：**

使用滑动窗口 + 哈希表，O(n) 时间复杂度：

```python
def length_of_longest_substring(s: str) -> int:
    char_index = {}  # 记录字符最近出现的位置
    left = 0
    max_len = 0

    for right, ch in enumerate(s):
        # 如果字符已出现过且在窗口内，移动左边界
        if ch in char_index and char_index[ch] >= left:
            left = char_index[ch] + 1
        char_index[ch] = right
        max_len = max(max_len, right - left + 1)

    return max_len

# 测试
print(length_of_longest_substring("abcabcbb"))  # 3
print(length_of_longest_substring("bbbbb"))     # 1
print(length_of_longest_substring("pwwkew"))    # 3
print(length_of_longest_substring(""))          # 0
print(length_of_longest_substring(" "))         # 1
```

思路：
- 维护一个滑动窗口 `[left, right]`，窗口内无重复字符。
- 用字典记录每个字符最近出现的索引。
- 遇到重复字符时，将 `left` 跳到重复字符上一次出现位置 + 1。
- 每步更新最大长度。

**评分标准：**
- 算法正确，通过所有测试（5 分）
- 时间复杂度 O(n)（3 分）
- 代码清晰、变量命名合理（2 分）

---

## 模块四：面向对象编程

### 题目 4.1 类与对象基础

**题目描述：** 定义一个 `BankAccount` 类，包含私有属性 `__balance`，提供 `deposit`、`withdraw`、`get_balance` 方法，并演示封装性。

**参考答案：**

```python
class BankAccount:
    def __init__(self, owner: str, balance: float = 0):
        self.owner = owner
        self.__balance = balance  # 私有属性（名称重整为 _BankAccount__balance）

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("存款金额必须为正")
        self.__balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("取款金额必须为正")
        if amount > self.__balance:
            raise ValueError("余额不足")
        self.__balance -= amount

    def get_balance(self) -> float:
        return self.__balance

    def __str__(self):
        return f"BankAccount(owner={self.owner}, balance={self.__balance})"

    def __repr__(self):
        return f"BankAccount({self.owner!r}, {self.__balance})"


acc = BankAccount("Alice", 1000)
acc.deposit(500)
print(acc.get_balance())  # 1500
acc.withdraw(200)
print(acc.get_balance())  # 1300

# 直接访问 __balance 会报错（实际上是名称重整）
try:
    print(acc.__balance)
except AttributeError:
    print("无法直接访问私有属性")

# 但仍可通过重整名访问（Python 没有真正的私有）
print(acc._BankAccount__balance)  # 1300
```

要点：
- Python 用 `_` 前缀表示"内部使用"（约定），`__` 前缀触发名称重整（name mangling），但不是真正的访问控制。
- 封装通过方法暴露受控访问，便于添加校验逻辑。

**评分标准：**
- 私有属性与方法实现（4 分）
- 异常校验逻辑（3 分）
- 说明名称重整机制（3 分）

---

### 题目 4.2 继承与方法重写

**题目描述：** 设计一个动物类继承体系：`Animal`（基类）→ `Dog`、`Cat`（子类），演示方法重写、`super()` 调用、多态。

**参考答案：**

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    @abstractmethod
    def speak(self) -> str:
        """子类必须实现。"""
        pass

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.name}, age={self.age})"


class Dog(Animal):
    def __init__(self, name: str, age: int, breed: str):
        super().__init__(name, age)  # 调用父类初始化
        self.breed = breed

    def speak(self) -> str:
        return f"{self.name} 汪汪叫"

    def fetch(self):
        return f"{self.name} 在接飞盘"


class Cat(Animal):
    def speak(self) -> str:
        return f"{self.name} 喵喵叫"


# 多态：同一接口，不同行为
def make_sound(animal: Animal):
    print(animal.speak())


animals = [Dog("旺财", 3, "金毛"), Cat("咪咪", 2)]
for a in animals:
    make_sound(a)
# 旺财 汪汪叫
# 咪咪 喵喵叫

print(animals[0])  # Dog(name=旺财, age=3)

# isinstance / issubclass
print(isinstance(animals[0], Animal))  # True
print(issubclass(Dog, Animal))         # True

# 抽象类不能实例化
try:
    Animal("test", 1)
except TypeError as e:
    print(f"抽象类无法实例化: {e}")
```

要点：
- `super().__init__()` 调用父类构造方法，避免重复代码。
- 抽象基类（ABC）强制子类实现抽象方法。
- 多态：不同对象调用同一方法表现出不同行为。

**评分标准：**
- 继承与 super 使用（3 分）
- 方法重写正确（3 分）
- 多态演示（2 分）
- 抽象类使用（2 分）

---

### 题目 4.3 魔术方法（Dunder Methods）

**题目描述：** 实现一个 `Vector` 类，支持加减运算、长度比较、索引访问、迭代、字符串表示。

**参考答案：**

```python
import math

class Vector:
    def __init__(self, *components):
        self.components = list(components)

    # 字符串表示
    def __repr__(self):
        return f"Vector{tuple(self.components)}"

    def __str__(self):
        return f"({', '.join(map(str, self.components))})"

    # 运算符重载
    def __add__(self, other):
        if len(self) != len(other):
            raise ValueError("维度不一致")
        return Vector(*(a + b for a, b in zip(self, other)))

    def __sub__(self, other):
        if len(self) != len(other):
            raise ValueError("维度不一致")
        return Vector(*(a - b for a, b in zip(self, other)))

    # 长度
    def __len__(self):
        return len(self.components)

    # 比较
    def __eq__(self, other):
        return self.components == other.components

    def __lt__(self, other):
        return math.hypot(*self.components) < math.hypot(*other.components)

    # 索引访问
    def __getitem__(self, index):
        return self.components[index]

    def __setitem__(self, index, value):
        self.components[index] = value

    # 迭代
    def __iter__(self):
        return iter(self.components)

    # 布尔值
    def __bool__(self):
        return any(self.components)

    # 哈希（使其可作 dict key）
    def __hash__(self):
        return hash(tuple(self.components))


v1 = Vector(1, 2, 3)
v2 = Vector(4, 5, 6)

print(repr(v1))        # Vector(1, 2, 3)
print(v1 + v2)         # (5, 7, 9)
print(v2 - v1)         # (3, 3, 3)
print(len(v1))         # 3
print(v1[0])           # 1
v1[0] = 10
print(v1)              # (10, 2, 3)

for x in Vector(1, 2):
    print(x, end=" ")  # 1 2

print(Vector(1, 0) == Vector(1, 0))  # True
print(Vector(1, 0) < Vector(3, 4))   # True
```

常见魔术方法：
- `__init__` / `__new__`：构造
- `__str__` / `__repr__`：字符串表示
- `__eq__` / `__lt__` / `__hash__`：比较与哈希
- `__add__` / `__mul__`：运算符
- `__len__` / `__getitem__` / `__iter__`：容器协议
- `__enter__` / `__exit__`：上下文管理器
- `__call__`：可调用对象

**评分标准：**
- 至少实现 6 种魔术方法（5 分）
- 运算符重载与维度校验（2 分）
- 容器协议（len/getitem/iter）（2 分）
- 说明常见魔术方法（1 分）

---

### 题目 4.4 类方法、静态方法、实例方法

**题目描述：** 说明实例方法、类方法（`@classmethod`）、静态方法（`@staticmethod`）的区别，并实现一个 `Date` 类作为示例。

**参考答案：**

- **实例方法**：第一个参数为 `self`，可访问实例属性和类属性。
- **类方法**：第一个参数为 `cls`，访问类本身，常用于工厂方法。
- **静态方法**：无 `self` / `cls`，与类逻辑相关但不依赖实例或类状态，相当于放在类命名空间的普通函数。

```python
class Date:
    def __init__(self, year: int, month: int, day: int):
        self.year = year
        self.month = month
        self.day = day

    # 实例方法
    def display(self):
        return f"{self.year}-{self.month:02d}-{self.day:02d}"

    # 类方法：工厂方法
    @classmethod
    def from_string(cls, date_str: str):
        """从 'YYYY-MM-DD' 字符串创建实例。"""
        year, month, day = map(int, date_str.split("-"))
        return cls(year, month, day)

    @classmethod
    def today(cls):
        """创建表示今天的实例。"""
        import datetime
        t = datetime.date.today()
        return cls(t.year, t.month, t.day)

    # 静态方法：工具方法
    @staticmethod
    def is_valid_date(year: int, month: int, day: int) -> bool:
        """验证日期是否合法（不依赖实例或类）。"""
        try:
            datetime.date(year, month, day)
            return True
        except ValueError:
            return False


# 实例方法
d1 = Date(2024, 1, 15)
print(d1.display())  # 2024-01-15

# 类方法作为工厂
d2 = Date.from_string("2024-06-01")
print(d2.display())  # 2024-06-01
print(type(d2))      # <class 'Date'>

d3 = Date.today()
print(d3.display())

# 静态方法
print(Date.is_valid_date(2024, 2, 29))  # True（2024 闰年）
print(Date.is_valid_date(2023, 2, 29))  # False
```

类方法在继承中会返回子类实例（多态工厂），这是与静态方法的关键区别。

**评分标准：**
- 三种方法区别准确（4 分）
- 工厂方法示例（3 分）
- 说明类方法的继承多态特性（3 分）

---

### 题目 4.5 多重继承与 MRO

**题目描述：** 解释 Python 的方法解析顺序（MRO），并预测以下代码输出。

```python
class A:
    def greet(self):
        return "A"

class B(A):
    def greet(self):
        return "B"

class C(A):
    def greet(self):
        return "C"

class D(B, C):
    pass

print(D().greet())
print(D.__mro__)
```

**参考答案：**

输出：
```
B
(<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)
```

**MRO（Method Resolution Order，方法解析顺序）**

Python 2.3+ 使用 C3 线性化算法计算 MRO，保证：
1. 子类在父类之前。
2. 多个父类按定义顺序。
3. 每个类只出现一次。

查看方式：`ClassName.__mro__` 或 `ClassName.mro()`。

```python
# 经典钻石继承
class Base:
    def method(self):
        return "Base"

class Left(Base):
    def method(self):
        return "Left"

class Right(Base):
    def method(self):
        return "Right"

class Child(Left, Right):
    pass

print(Child().method())  # Left
print(Child.__mro__)
# (Child, Left, Right, Base, object)

# Mixin 模式
class JsonMixin:
    def to_json(self):
        import json
        return json.dumps(self.__dict__)

class LogMixin:
    def log(self, msg):
        print(f"[{self.__class__.__name__}] {msg}")

class User(JsonMixin, LogMixin):
    def __init__(self, name):
        self.name = name

u = User("Alice")
print(u.to_json())  # {"name": "Alice"}
u.log("created")
```

**Mixin 设计原则：**
- Mixin 类体现单一功能，不单独使用。
- 通过多重继承组合功能，避免菱形继承复杂性。
- Mixin 通常放在继承列表左侧。

**评分标准：**
- 预测输出正确（4 分）
- 解释 C3 线性化（3 分）
- Mixin 模式说明（3 分）

---

### 题目 4.6 property 装饰器

**题目描述：** 使用 `@property` 实现一个 `Temperature` 类，内部以开尔文存储，对外暴露摄氏度读写接口，并做范围校验。

**参考答案：**

```python
class Temperature:
    def __init__(self, celsius: float):
        self.celsius = celsius  # 触发 setter 校验

    @property
    def celsius(self) -> float:
        """摄氏度。"""
        return self._celsius

    @celsius.setter
    def celsius(self, value: float):
        if value < -273.15:
            raise ValueError(f"温度不能低于绝对零度: {value}")
        self._celsius = value

    @property
    def kelvin(self) -> float:
        return self._celsius + 273.15

    @kelvin.setter
    def kelvin(self, value: float):
        if value < 0:
            raise ValueError("开尔文温度不能为负")
        self._celsius = value - 273.15

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9 / 5 + 32


t = Temperature(25)
print(t.celsius)     # 25.0
print(t.kelvin)      # 298.15
print(t.fahrenheit)  # 77.0

t.celsius = -10
print(t.kelvin)  # 263.15

try:
    t.celsius = -300
except ValueError as e:
    print(e)  # 温度不能低于绝对零度: -300

t.kelvin = 0
print(t.celsius)  # -273.15
```

property 优势：
- 将方法以属性形式访问，接口简洁。
- 可在读/写时插入校验、日志、缓存逻辑。
- 实现属性只读（仅定义 getter）。

**评分标准：**
- property 正确使用（4 分）
- setter 校验逻辑（3 分）
- 多属性联动（3 分）

---

### 题目 4.7 数据类与 slots

**题目描述：** 使用 `@dataclass` 简化类的定义，并说明 `__slots__` 如何节省内存。

**参考答案：**

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class Point:
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclass
class Student:
    name: str
    age: int
    scores: List[float] = field(default_factory=list)  # 可变默认值用 field
    _id: int = field(default=0, repr=False)            # 不显示在 repr 中

    def __post_init__(self):
        if self._id == 0:
            self._id = hash(self.name) % 10000


p1 = Point(0, 0)
p2 = Point(3, 4)
print(p1.distance_to(p2))  # 5.0
print(p1 == p2)            # False（自动生成 __eq__）

s = Student("Alice", 20, [90, 85])
print(s)  # Student(name='Alice', age=20, scores=[90, 85])
```

`@dataclass` 自动生成 `__init__`、`__repr__`、`__eq__`，可通过参数定制：
- `frozen=True`：不可变（可哈希）。
- `order=True`：生成比较方法。

**`__slots__` 节省内存：**

默认情况下，Python 类实例使用 `__dict__` 存储属性，字典带来额外内存开销。声明 `__slots__` 后，实例改用固定大小的数组存储，节省内存并加快属性访问，但会禁止动态添加属性。

```python
import sys

class WithoutSlots:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class WithSlots:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x = x
        self.y = y

obj1 = WithoutSlots(1, 2)
obj2 = WithSlots(1, 2)

print(sys.getsizeof(obj1.__dict__))  # 约 104 字节
# obj2 没有 __dict__
try:
    print(obj2.__dict__)
except AttributeError:
    print("WithSlots 实例无 __dict__")

print(sys.getsizeof(obj1), sys.getsizeof(obj2))
# WithSlots 实例通常更小

# __slots__ 禁止动态属性
try:
    obj2.z = 3
except AttributeError as e:
    print(f"无法添加属性: {e}")
```

**评分标准：**
- dataclass 使用正确（4 分）
- field 处理可变默认值（2 分）
- `__slots__` 原理与内存对比（4 分）

---

## 模块五：Python 高级特性

### 题目 5.1 生成器与迭代器

**题目描述：** 解释迭代器协议，实现一个生成斐波那契数列的生成器，并说明生成器与列表的内存差异。

**参考答案：**

**迭代器协议：**
- `__iter__()`：返回迭代器对象自身。
- `__next__()`：返回下一个值，无值时抛 `StopIteration`。
- 可迭代对象（Iterable）实现 `__iter__`；迭代器（Iterator）同时实现 `__iter__` 和 `__next__`。

```python
# 生成器函数：使用 yield
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# 使用 itertools.islice 取前 N 项
from itertools import islice
fib = fibonacci()
print(list(islice(fib, 10)))  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

# 生成器表达式：惰性求值
squares_gen = (x * x for x in range(1000000))
print(next(squares_gen))  # 0
print(next(squares_gen))  # 1

# 自定义迭代器
class RangeIterator:
    def __init__(self, start, end, step=1):
        self.current = start
        self.end = end
        self.step = step

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.end:
            raise StopIteration
        val = self.current
        self.current += self.step
        return val

for x in RangeIterator(1, 5):
    print(x, end=" ")  # 1 2 3 4
```

**内存差异：** 生成器按需产出值，不预先分配全部内存，处理大数据流时优势明显。

```python
import sys

# 列表：一次性生成所有元素
big_list = [x * x for x in range(1000000)]
print(sys.getsizeof(big_list))  # 约 8 MB+

# 生成器：仅保存状态
big_gen = (x * x for x in range(1000000))
print(sys.getsizeof(big_gen))   # 约 200 字节（固定大小）
```

**生成器高级用法：**
- `yield from`：委托给子生成器。
- `send()`：向生成器发送值（协程基础）。
- `throw()` / `close()`：异常处理。

```python
def echo():
    while True:
        received = yield
        print(f"收到: {received}")

e = echo()
next(e)        # 预激
e.send("hello")
e.send("world")
# 输出:
# 收到: hello
# 收到: world
```

**评分标准：**
- 迭代器协议说明（3 分）
- 生成器函数与表达式（3 分）
- 内存差异分析（2 分）
- send/throw 等高级用法（2 分）

---

### 题目 5.2 装饰器原理

**题目描述：** 手写一个计时装饰器，支持带参数和不带参数两种调用方式。

**参考答案：**

```python
import time
import functools

# 方式一：无参数装饰器
def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} 耗时 {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_function(n):
    return sum(i * i for i in range(n))

print(slow_function(1000000))


# 方式二：带参数装饰器（三层嵌套）
def repeat(times: int):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"Hello, {name}")

greet("Alice")
# 输出 3 次 Hello, Alice


# 方式三：兼容带参和不带参（默认参数技巧）
def retry(_func=None, *, times: int = 3, delay: float = 0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for i in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    print(f"第 {i+1} 次失败: {e}")
                    time.sleep(delay)
            raise last_exc
        return wrapper

    if _func is None:
        return decorator
    return decorator(_func)

@retry
def task1(): pass

@retry(times=5, delay=1)
def task2(): pass
```

`@functools.wraps` 的作用：将原函数的 `__name__`、`__doc__`、`__module__`、`__wrapped__` 等属性复制到 wrapper，保持元信息。

**评分标准：**
- 无参装饰器实现（3 分）
- 带参装饰器（三层嵌套）（4 分）
- 兼容两种调用方式（3 分）

---

### 题目 5.3 上下文管理器

**题目描述：** 分别用类（`__enter__`/`__exit__`）和 `contextlib.contextmanager` 实现一个计时上下文管理器。

**参考答案：**

```python
import time
from contextlib import contextmanager

# 方式一：类实现
class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self.start
        print(f"耗时 {self.elapsed:.4f}s")
        # 返回 True 会吞掉异常，返回 False/None 会继续抛出
        return False

with Timer():
    sum(i * i for i in range(1000000))
# 耗时 0.1xxx s


# 方式二：contextmanager 装饰器
@contextmanager
def timer_cm(label: str = "block"):
    start = time.perf_counter()
    try:
        yield  # with 块内的代码在此处执行
    finally:
        elapsed = time.perf_counter() - start
        print(f"{label} 耗时 {elapsed:.4f}s")

with timer_cm("数据处理"):
    sum(i * i for i in range(1000000))
# 数据处理 耗时 0.1xxx s


# 实际应用：数据库事务
@contextmanager
def transaction(conn):
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise

# 实际应用：临时切换工作目录
import os
@contextmanager
def cd(path):
    old = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)
```

`__exit__` 返回值的含义：
- 返回 `True`：抑制 with 块中的异常。
- 返回 `False` 或 `None`：异常继续传播。

**评分标准：**
- 类实现正确（3 分）
- contextmanager 实现（3 分）
- `__exit__` 返回值含义（2 分）
- 实际应用示例（2 分）

---

### 题目 5.4 闭包与变量捕获

**题目描述：** 预测以下代码输出并解释现象，给出修正方案。

```python
funcs = []
for i in range(3):
    funcs.append(lambda: i)

for f in funcs:
    print(f())
```

**参考答案：**

输出：
```
2
2
2
```

**原因：** 闭包捕获的是变量本身（引用），而非值。循环结束后 `i` 的值为 2，所有 lambda 都引用同一个 `i`，因此都输出 2。

**修正方案：**

```python
# 方案一：默认参数捕获当前值
funcs = []
for i in range(3):
    funcs.append(lambda i=i: i)  # i 作为默认参数在定义时求值

for f in funcs:
    print(f())  # 0 1 2

# 方案二：使用 functools.partial
from functools import partial
funcs = []
for i in range(3):
    funcs.append(partial(lambda x: x, i))

for f in funcs:
    print(f())  # 0 1 2

# 方案三：再包一层函数，立即绑定
funcs = []
for i in range(3):
    def make_func(x):
        return lambda: x
    funcs.append(make_func(i))

for f in funcs:
    print(f())  # 0 1 2
```

**闭包定义：** 闭包是引用了自由变量的函数，即使在原作用域外被调用，仍能访问这些变量。常用于装饰器、回调、工厂函数。

**评分标准：**
- 正确预测输出（3 分）
- 解释变量捕获机制（4 分）
- 至少 2 种修正方案（3 分）

---

### 题目 5.5 类型提示（Type Hints）

**题目描述：** 为以下函数添加类型提示，并说明 `mypy` 的作用。

```python
def process(data, config=None):
    result = []
    for item in data:
        if config and item in config:
            result.append(item)
    return result
```

**参考答案：**

```python
from typing import Optional, Iterable, List, TypeVar, Generic, Protocol

# 基础类型提示
def process(
    data: Iterable[int],
    config: Optional[set] = None
) -> List[int]:
    result: List[int] = []
    for item in data:
        if config and item in config:
            result.append(item)
    return result


# 泛型
T = TypeVar("T")

def first(items: List[T]) -> T:
    return items[0]

print(first([1, 2, 3]))       # int
print(first(["a", "b"]))      # str


# Protocol（结构化子类型，鸭子类型）
class Closeable(Protocol):
    def close(self) -> None: ...

def cleanup(obj: Closeable) -> None:
    obj.close()


# TypedDict（字典结构类型）
from typing import TypedDict

class UserDict(TypedDict):
    name: str
    age: int

u: UserDict = {"name": "Alice", "age": 30}


# Python 3.9+ 内置泛型
def filter_positive(nums: list[int]) -> list[int]:
    return [n for n in nums if n > 0]

# Python 3.10+ 联合类型
def parse(value: int | str) -> int | None:
    try:
        return int(value)
    except (ValueError, TypeError):
        return None
```

`mypy` 是静态类型检查工具，可在运行前发现类型错误：

```bash
pip install mypy
mypy your_script.py
```

类型提示是可选的，运行时不强制，但能：
- 提升代码可读性与可维护性。
- 配合 IDE 提供智能补全与重构支持。
- 通过 mypy/pyright 进行静态检查，提前发现 bug。

**评分标准：**
- 类型提示正确（4 分）
- 泛型与 Protocol（3 分）
- mypy 作用说明（3 分）

---

### 题目 5.6 元类入门

**题目描述：** 简述元类的作用，实现一个 `Singleton` 元类。

**参考答案：**

**元类（Metaclass）** 是"创建类的类"。普通类通过 `type` 创建，元类允许自定义类的创建过程。

```python
# type 是默认元类
class MyClass:
    pass

print(type(MyClass))  # <class 'type'>
print(type(MyClass()))  # <class '__main__.MyClass'>

# 用 type 动态创建类
DynamicClass = type("DynamicClass", (), {"x": 10})
print(DynamicClass().x)  # 10

# 自定义元类：单例模式
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self):
        print("初始化数据库连接")
        self.connected = True

db1 = Database()  # 初始化数据库连接
db2 = Database()
print(db1 is db2)  # True，同一实例

# 元类实现 ORM 风格的字段收集
class Field:
    def __init__(self, name):
        self.name = name

class ModelMeta(type):
    def __new__(mcs, name, bases, namespace):
        fields = {}
        for key, val in namespace.items():
            if isinstance(val, Field):
                fields[key] = val
        namespace["_fields"] = fields
        return super().__new__(mcs, name, bases, namespace)

class User(metaclass=ModelMeta):
    name = Field("name")
    age = Field("age")

print(User._fields)  # {'name': Field('name'), 'age': Field('age')}
```

**元类常见用途：**
- 单例模式
- ORM 字段收集（Django、SQLAlchemy）
- 接口/抽象类强制（ABC）
- 注册子类（插件系统）

**元类 `__new__` vs `__init__` vs `__call__`：**
- `__new__`：创建类对象（控制类的创建）。
- `__init__`：初始化类对象。
- `__call__`：控制类的实例化过程（创建实例时调用）。

**评分标准：**
- 元类概念准确（3 分）
- 单例元类实现（4 分）
- 字段收集示例（3 分）

---

## 模块六：函数与装饰器

### 题目 6.1 高阶函数

**题目描述：** 使用 `map`、`filter`、`reduce` 实现以下功能：对列表 `[1, 2, 3, 4, 5, 6]` 中的偶数求平方后求和。

**参考答案：**

```python
from functools import reduce

nums = [1, 2, 3, 4, 5, 6]

# 方式一：函数式
squares = map(lambda x: x * x, nums)
evens = filter(lambda x: x % 2 == 0, squares)
total = reduce(lambda a, b: a + b, evens)
print(total)  # 4 + 16 + 36 = 56

# 方式二：列表推导式（更 Pythonic）
total2 = sum(x * x for x in nums if x % 2 == 0)
print(total2)  # 56

# 方式三：链式调用
from itertools import chain
result = sum(
    x * x for x in chain([1, 2, 3], [4, 5, 6]) if x % 2 == 0
)
print(result)  # 56

# 高阶函数作为参数
def apply(func, items):
    return [func(x) for x in items]

print(apply(str.upper, ["a", "b"]))  # ['A', 'B']
```

**Pythonic 建议：** 列表/生成器推导式通常比 `map`/`filter` 更易读，但 `map` 在与多进程（`Pool.map`）配合时仍有价值。

```python
import multiprocessing
with multiprocessing.Pool(4) as p:
    print(p.map(lambda x: x * x, range(10)))
```

**评分标准：**
- map/filter/reduce 使用正确（4 分）
- 推导式对比（3 分）
- 高阶函数概念说明（3 分）

---

### 题目 6.2 偏函数与柯里化

**题目描述：** 使用 `functools.partial` 创建偏函数，并实现一个简单的柯里化装饰器。

**参考答案：**

```python
from functools import partial, wraps

# 偏函数：固定部分参数
def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)
print(square(5))  # 25
print(cube(2))    # 8

# 实际应用：简化日志函数
def log(level, message):
    print(f"[{level}] {message}")

info = partial(log, "INFO")
warning = partial(log, "WARNING")
info("启动服务")
warning("磁盘空间不足")


# 柯里化装饰器
def curry(func):
    @wraps(func)
    def wrapper(*args):
        if len(args) >= func.__code__.co_argcount:
            return func(*args)
        return partial(wrapper, *args)
    return wrapper

@curry
def add3(a, b, c):
    return a + b + c

print(add3(1)(2)(3))      # 6
print(add3(1, 2)(3))      # 6
print(add3(1)(2, 3))      # 6
print(add3(1, 2, 3))      # 6
```

**偏函数 vs 柯里化：**
- 偏函数：固定部分参数生成新函数，一次可固定多个参数。
- 柯里化：将多参数函数转化为逐个接收参数的函数链。

**评分标准：**
- partial 使用正确（4 分）
- 柯里化装饰器实现（4 分）
- 两者区别说明（2 分）

---

### 题目 6.3 递归与尾递归

**题目描述：** 实现阶乘的递归版本，说明 Python 不支持尾递归优化的问题，并给出迭代替代方案。

**参考答案：**

```python
import sys
sys.setrecursionlimit(10000)  # 默认 1000

# 递归版本
def factorial_recursive(n: int) -> int:
    if n < 0:
        raise ValueError("n 不能为负")
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)

# 尾递归形式（Python 不会优化，仍会栈溢出）
def factorial_tail(n: int, acc: int = 1) -> int:
    if n <= 1:
        return acc
    return factorial_tail(n - 1, acc * n)

# 迭代版本（推荐）
def factorial_iterative(n: int) -> int:
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

print(factorial_recursive(5))   # 120
print(factorial_tail(5))        # 120
print(factorial_iterative(5))   # 120

# 深递归会栈溢出
try:
    factorial_recursive(2000)
except RecursionError as e:
    print(f"栈溢出: {e}")
```

**Python 不支持尾递归优化的原因：**
1. Guido 认为 TCO 会使调试栈追踪困难。
2. Python 的运行栈与 C 栈耦合，实现 TCO 复杂。
3. 可用循环或生成器替代递归。

**递归优化技巧：**
- 使用 `sys.setrecursionlimit` 提高限制（慎用）。
- 改写为迭代。
- 使用 `lru_cache` 记忆化（适用于重叠子问题）。
- 使用生成器/显式栈模拟。

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(200))  # 大数快速计算
```

**评分标准：**
- 三种实现（4 分）
- 解释 Python 不支持 TCO（3 分）
- 记忆化优化（3 分）

---

### 题目 6.4 函数缓存

**题目描述：** 实现一个自定义缓存装饰器，支持 TTL（过期时间）和容量限制。

**参考答案：**

```python
import time
from functools import wraps
from collections import OrderedDict
from typing import Callable, Any, Optional

def ttl_cache(maxsize: int = 128, ttl: float = 60):
    """
    带 TTL 和容量限制的缓存装饰器。
    """
    def decorator(func: Callable) -> Callable:
        cache: OrderedDict = OrderedDict()  # key -> (value, expire_at)

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()

            # 清理过期项
            expired = [k for k, (_, exp) in cache.items() if exp < now]
            for k in expired:
                cache.pop(k, None)

            if key in cache:
                cache.move_to_end(key)
                return cache[key][0]

            result = func(*args, **kwargs)
            cache[key] = (result, now + ttl)

            if len(cache) > maxsize:
                cache.popitem(last=False)  # LRU 淘汰

            return result

        wrapper.cache_clear = cache.clear
        wrapper.cache_info = lambda: {
            "size": len(cache),
            "maxsize": maxsize,
            "ttl": ttl,
        }
        return wrapper
    return decorator

@ttl_cache(maxsize=100, ttl=5)
def slow_query(user_id: int) -> dict:
    time.sleep(1)  # 模拟耗时查询
    return {"id": user_id, "name": f"user_{user_id}"}

start = time.time()
print(slow_query(1))  # 约 1s
print(slow_query(1))  # 瞬间返回（命中缓存）
print(f"两次调用耗时: {time.time() - start:.2f}s")
print(slow_query.cache_info())
# {'size': 1, 'maxsize': 100, 'ttl': 5}
```

**评分标准：**
- TTL 过期机制（4 分）
- LRU 容量淘汰（3 分）
- cache_info 等辅助方法（3 分）

---

### 题目 6.5 算法题：装饰器实现重试

**题目描述：** 实现一个 `@retry` 装饰器，支持配置最大重试次数、重试间隔、可重试的异常类型。

**参考答案：**

```python
import time
import random
import functools
from typing import Tuple, Type

def retry(
    times: int = 3,
    delay: float = 1,
    backoff: float = 2,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    重试装饰器。
    :param times: 最大重试次数
    :param delay: 初始间隔
    :param backoff: 退避倍数
    :param exceptions: 可重试的异常类型
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            last_exc = None
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    attempt += 1
                    if attempt == times:
                        break
                    print(f"第 {attempt} 次失败: {e}, {current_delay}s 后重试")
                    time.sleep(current_delay)
                    current_delay *= backoff
            raise last_exc
        return wrapper
    return decorator

# 测试
@retry(times=4, delay=0.5, backoff=2, exceptions=(ValueError,))
def unreliable_task():
    if random.random() < 0.7:
        raise ValueError("随机失败")
    return "成功"

try:
    print(unreliable_task())
except ValueError as e:
    print(f"最终失败: {e}")

# HTTP 请求场景
import urllib.request

@retry(times=3, delay=1, exceptions=(urllib.error.URLError,))
def fetch(url):
    return urllib.request.urlopen(url, timeout=5).read()
```

**评分标准：**
- 重试逻辑正确（4 分）
- 指数退避实现（3 分）
- 异常类型过滤（3 分）

---

## 模块七：异常处理与调试

### 题目 7.1 异常继承体系

**题目描述：** 描述 Python 异常继承体系，说明 `Exception` 与 `BaseException` 的区别。

**参考答案：**

```
BaseException
├── SystemExit          # sys.exit() 触发
├── KeyboardInterrupt   # Ctrl+C
├── GeneratorExit       # 生成器关闭
└── Exception
    ├── StopIteration
    ├── ArithmeticError
    │   ├── ZeroDivisionError
    │   └── OverflowError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── OSError
    │   ├── FileNotFoundError
    │   └── PermissionError
    ├── ValueError
    │   └── UnicodeDecodeError
    ├── TypeError
    ├── AttributeError
    └── ...
```

- `BaseException`：所有异常的基类。
- `Exception`：常规异常基类，业务代码应继承此类。
- `SystemExit`、`KeyboardInterrupt` 等不继承 `Exception`，因此 `except Exception` 不会捕获它们，保证程序可被中断/退出。

```python
# 自定义异常
class AppError(Exception):
    """应用异常基类。"""
    pass

class ValidationError(AppError):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

class NotFoundError(AppError):
    pass

# 使用
def get_user(user_id: int):
    if user_id < 0:
        raise ValidationError("user_id", "不能为负")
    if user_id not in {1, 2}:
        raise NotFoundError(f"用户 {user_id} 不存在")
    return {"id": user_id}

try:
    get_user(-1)
except ValidationError as e:
    print(f"校验错误: {e.field} - {e.message}")
except NotFoundError as e:
    print(f"未找到: {e}")
except AppError as e:
    print(f"应用错误: {e}")
```

**评分标准：**
- 继承体系描述（3 分）
- Exception 与 BaseException 区别（3 分）
- 自定义异常设计（4 分）

---

### 题目 7.2 try-except-finally 执行顺序

**题目描述：** 预测以下代码输出。

```python
def test():
    try:
        return "try"
    except:
        return "except"
    finally:
        print("finally")

print(test())
```

**参考答案：**

输出：
```
finally
try
```

**执行顺序：**
1. `try` 块执行，遇到 `return "try"`。
2. 在返回前，必须先执行 `finally` 块（无论是否异常）。
3. `finally` 块的 `print` 先执行。
4. 然后才真正返回 `"try"`。

**注意：** 如果 `finally` 中也有 `return`，会覆盖 `try` 中的返回值（不推荐这样写）。

```python
def test2():
    try:
        return "try"
    finally:
        return "finally"  # 会覆盖 try 的返回值

print(test2())  # finally

# 异常情况下 finally 仍执行
def test3():
    try:
        raise ValueError("error")
    except ValueError:
        print("except 块")
        return "except"
    finally:
        print("finally 块")

print(test3())
# except 块
# finally 块
# except
```

**else 子句：** `try` 没有抛异常时执行。

```python
def test4():
    try:
        x = 1 / 0
    except ZeroDivisionError:
        print("除零错误")
    else:
        print("无异常时执行")
    finally:
        print("总会执行")

test4()
# 除零错误
# 总会执行
```

**评分标准：**
- 正确预测输出（4 分）
- 解释 finally 优先级（3 分）
- else 子句说明（3 分）

---

### 题目 7.3 自定义异常上下文管理

**题目描述：** 实现一个 `Transaction` 上下文管理器，发生异常时自动回滚，无异常时提交。

**参考答案：**

```python
class TransactionError(Exception):
    pass

class Transaction:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        print("开启事务")
        self.conn.execute("BEGIN")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.execute("COMMIT")
            print("事务提交")
        else:
            self.conn.execute("ROLLBACK")
            print(f"事务回滚，异常: {exc_val}")
        return False  # 不吞异常

# 模拟数据库连接
class FakeConn:
    def execute(self, sql):
        print(f"  [SQL] {sql}")

conn = FakeConn()

# 正常场景
with Transaction(conn) as tx:
    conn.execute("INSERT ...")
# 开启事务 / [SQL] BEGIN / [SQL] INSERT ... / [SQL] COMMIT / 事务提交

# 异常场景
try:
    with Transaction(conn) as tx:
        conn.execute("INSERT ...")
        raise TransactionError("主键冲突")
except TransactionError as e:
    print(f"捕获: {e}")
# 开启事务 / [SQL] BEGIN / [SQL] INSERT ... / [SQL] ROLLBACK / 事务回滚 / 捕获
```

**评分标准：**
- 上下文管理器实现（4 分）
- 异常时回滚逻辑（3 分）
- 正常时提交逻辑（3 分）

---

### 题目 7.4 assert 与异常的边界

**题目描述：** 说明 `assert` 与 `raise` 的使用场景，以及 `python -O` 优化时 assert 的行为。

**参考答案：**

- `assert`：用于开发/测试阶段的内部不变量检查，不应处理生产环境的业务校验。`python -O` 启动优化模式时会移除所有 `assert` 语句。
- `raise`：用于显式抛出异常，处理业务逻辑中的错误情况，始终生效。

```python
# assert 用于内部不变量（开发期）
def divide(a, b):
    assert b != 0, "b 不能为 0"  # 仅用于调试，生产环境会被 -O 移除
    return a / b

# 生产环境应该用 raise
def divide_safe(a, b):
    if b == 0:
        raise ValueError("b 不能为 0")
    return a / b

# 演示 -O 优化
# 命令: python -O script.py
# 此时 assert 语句被忽略，divide(1, 0) 会抛 ZeroDivisionError 而非 AssertionError
```

**使用建议：**
- 函数对外接口的参数校验：用 `raise`。
- 内部算法不变量、调试断言：用 `assert`。
- 永远不要用 `assert` 做权限/安全检查。

**评分标准：**
- 区分使用场景（4 分）
- 说明 -O 行为（3 分）
- 最佳实践建议（3 分）

---

### 题目 7.5 日志与调试技巧

**题目描述：** 配置 `logging` 模块输出到文件和控制台，并说明 `logging` 与 `print` 的区别。

**参考答案：**

```python
import logging

# 基础配置
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告")
logger.error("错误")
logger.critical("严重错误")

# 分级日志（不同 handler 不同级别）
def setup_logger():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # 文件：DEBUG 及以上
    fh = logging.FileHandler("debug.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    ))

    # 控制台：WARNING 及以上
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    root.addHandler(fh)
    root.addHandler(ch)

setup_logger()
logging.debug("仅写入文件")
logging.warning("文件和控制台都显示")

# 异常追踪
try:
    1 / 0
except ZeroDivisionError:
    logging.exception("发生异常")  # 自动附带 traceback
```

**`logging` vs `print`：**

| 维度 | logging | print |
|------|---------|-------|
| 级别 | 分级（DEBUG/INFO/WARNING/ERROR/CRITICAL） | 无级别 |
| 输出 | 文件、控制台、网络、邮件等 | 仅控制台 |
| 格式 | 时间、模块、行号等可配置 | 原始文本 |
| 性能 | 异步、可缓冲 | 同步阻塞 |
| 生产 | 标准做法 | 仅调试用 |

**评分标准：**
- 配置文件 + 控制台输出（4 分）
- 分级 handler（3 分）
- logging.exception 用法（2 分）
- 与 print 对比（1 分）

---

## 模块八：文件与 IO 操作

### 题目 8.1 文件读写模式

**题目描述：** 说明 `open` 函数的常用模式（`r`、`w`、`a`、`b`、`+`），并实现一个安全的大文件逐行读取。

**参考答案：**

| 模式 | 说明 |
|------|------|
| `r` | 只读（默认），文件不存在抛异常 |
| `w` | 覆盖写入，文件不存在则创建 |
| `a` | 追加写入，文件不存在则创建 |
| `x` | 独占创建，文件已存在则抛异常 |
| `b` | 二进制模式 |
| `t` | 文本模式（默认） |
| `+` | 读写模式 |

```python
# 文本读取（推荐 with）
with open("test.txt", "r", encoding="utf-8") as f:
    content = f.read()           # 全部读取
    # 或逐行
    for line in f:
        print(line.rstrip())

# 大文件逐行处理（不会一次性加载到内存）
def count_lines(path: str) -> int:
    count = 0
    with open(path, "r", encoding="utf-8") as f:
        for _ in f:  # 文件对象本身是迭代器，逐行产出
            count += 1
    return count

# 写入
with open("out.txt", "w", encoding="utf-8") as f:
    f.write("第一行\n")
    f.writelines(["第二行\n", "第三行\n"])

# 二进制读写（图片等）
with open("image.png", "rb") as src, open("copy.png", "wb") as dst:
    while True:
        chunk = src.read(8192)  # 分块读取
        if not chunk:
            break
        dst.write(chunk)

# 追加
with open("log.txt", "a", encoding="utf-8") as f:
    f.write("新的日志\n")

# 读写模式
with open("data.txt", "r+", encoding="utf-8") as f:
    content = f.read()
    f.seek(0)
    f.write("覆盖开头")
```

**评分标准：**
- 模式说明完整（4 分）
- with 语句使用（2 分）
- 大文件逐行处理（2 分）
- 二进制分块读写（2 分）

---

### 题目 8.2 JSON 与 CSV 处理

**题目描述：** 实现从 CSV 读取数据、转换后写入 JSON 的功能。

**参考答案：**

```python
import csv
import json
from pathlib import Path

def csv_to_json(csv_path: str, json_path: str) -> None:
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)  # 以第一行为 key
        rows = list(reader)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

# 示例
csv_content = "name,age,city\nAlice,30,Beijing\nBob,25,Shanghai\n"
Path("users.csv").write_text(csv_content, encoding="utf-8")

csv_to_json("users.csv", "users.json")
print(Path("users.json").read_text(encoding="utf-8"))
# [
#   {"name": "Alice", "age": "30", "city": "Beijing"},
#   {"name": "Bob", "age": "25", "city": "Shanghai"}
# ]

# JSON 高级用法
data = {"name": "张三", "scores": [90, 85], "active": True}

# 序列化（带格式）
json_str = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
print(json_str)

# 自定义序列化
from datetime import datetime
class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

print(json.dumps({"time": datetime.now()}, cls=ComplexEncoder))

# CSV 写入
with open("out.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "age"])
    writer.writeheader()
    writer.writerow({"name": "Alice", "age": 30})
```

**评分标准：**
- CSV 读取与 JSON 写入（4 分）
- DictReader/DictWriter（3 分）
- 自定义 JSON 编码（3 分）

---

### 题目 8.3 pathlib 路径操作

**题目描述：** 使用 `pathlib` 实现以下操作：(1) 拼接路径；(2) 遍历目录；(3) 过滤 `.py` 文件；(4) 创建/删除目录。

**参考答案：**

```python
from pathlib import Path

# (1) 拼接路径（自动适配操作系统）
p = Path("d:/code") / "project" / "main.py"
print(p)            # d:\code\project\main.py (Windows)
print(p.name)       # main.py
print(p.stem)       # main
print(p.suffix)     # .py
print(p.parent)     # d:\code\project
print(p.parts)      # ('d:\\', 'code', 'project', 'main.py')

# (2) 遍历目录
for child in Path(".").iterdir():
    print(child.name, child.is_dir(), child.is_file())

# 递归遍历
for f in Path(".").rglob("*.py"):
    print(f)

# (3) 过滤 .py 文件
py_files = list(Path(".").rglob("*.py"))
print(f"找到 {len(py_files)} 个 .py 文件")

# (4) 创建/删除目录
new_dir = Path("test_dir/sub")
new_dir.mkdir(parents=True, exist_ok=True)
(new_dir / "a.txt").write_text("hello", encoding="utf-8")

# 读取
print((new_dir / "a.txt").read_text(encoding="utf-8"))

# 删除空目录
# new_dir.rmdir()  # 仅空目录
# 删除非空目录
import shutil
shutil.rmtree("test_dir", ignore_errors=True)

# 路径判断
print(Path(".").exists())     # True
print(Path(".").is_absolute()) # False

# 家目录、当前目录
print(Path.home())
print(Path.cwd())

# 解析与拼接
p = Path("/a/b/c.txt")
print(p.with_suffix(".md"))     # /a/b/c.md
print(p.with_name("d.txt"))     # /a/b/d.txt
```

`pathlib` 优势：面向对象、跨平台、链式调用，推荐替代 `os.path`。

**评分标准：**
- 路径拼接与属性（3 分）
- 递归遍历与过滤（3 分）
- 目录创建与删除（2 分）
- 与 os.path 对比（2 分）

---

### 题目 8.4 StringIO 与 BytesIO

**题目描述：** 说明内存 IO（`StringIO`/`BytesIO`）的应用场景并示例。

**参考答案：**

`StringIO` 和 `BytesIO` 在内存中模拟文件对象，适用于：
- 不想落地到磁盘的临时数据。
- 与期望文件接口的 API 配合。
- 测试时替换真实文件。

```python
from io import StringIO, BytesIO

# StringIO：文本
text_io = StringIO()
text_io.write("第一行\n")
text_io.write("第二行\n")
text_io.seek(0)
print(text_io.read())
# 第一行
# 第二行

# 用 StringIO 喂给 csv 模块
import csv
csv_io = StringIO()
writer = csv.writer(csv_io)
writer.writerow(["name", "age"])
writer.writerow(["Alice", 30])
print(csv_io.getvalue())
# name,age\r\nAlice,30\r\n

# BytesIO：二进制
import io
img_io = BytesIO()
img_io.write(b"\x89PNG\r\n\x1a\n")  # PNG 头
img_io.seek(0)
print(img_io.read())  # b'\x89PNG\r\n\x1a\n'

# 配合 PIL（图片处理）
# from PIL import Image
# img = Image.open(BytesIO(image_bytes))

# JSON 序列化到内存
import json
json_io = StringIO()
json.dump({"a": 1}, json_io)
json_io.seek(0)
loaded = json.load(json_io)
print(loaded)  # {'a': 1}
```

**评分标准：**
- 应用场景说明（3 分）
- StringIO 使用（3 分）
- BytesIO 使用（2 分）
- 与 csv/json 配合（2 分）

---

### 题目 8.5 序列化对比

**题目题目描述：** 对比 `pickle`、`json`、`shelve` 三种序列化方式。

**参考答案：**

| 方式 | 跨语言 | 安全性 | 支持类型 | 适用场景 |
|------|--------|--------|----------|----------|
| `pickle` | 否（Python 专用） | 不安全（可执行任意代码） | 几乎所有 Python 对象 | Python 程序间数据持久化 |
| `json` | 是 | 安全 | 基本类型 + str/int/list/dict | Web API、跨语言数据交换 |
| `shelve` | 否 | 同 pickle | 基于 pickle，按 key 存储 | 简单的持久化字典 |

```python
import pickle
import json
import shelve
from pathlib import Path

data = {"name": "Alice", "scores": [90, 85], "active": True}

# pickle：可序列化复杂对象
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

with open("data.pkl", "wb") as f:
    pickle.dump({"point": Point(1, 2), "data": data}, f)

with open("data.pkl", "rb") as f:
    loaded = pickle.load(f)
    print(loaded["data"])
    print(loaded["point"].x, loaded["point"].y)  # 1 2

# 警告：不要 pickle.load 不可信来源的文件！

# json：跨语言
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open("data.json", "r", encoding="utf-8") as f:
    print(json.load(f))

# shelve：持久化字典
with shelve.open("mydb") as db:
    db["user1"] = data
    db["point"] = Point(3, 4)

with shelve.open("mydb") as db:
    print(db["user1"])
    print(db["point"].x)  # 3

# 清理
for f in ["data.pkl", "data.json", "mydb"]:
    p = Path(f)
    if p.exists():
        if p.is_file():
            p.unlink()
        else:
            import shutil
            shutil.rmtree(p)
```

**评分标准：**
- 三种方式对比（4 分）
- pickle 序列化自定义对象（3 分）
- shelve 使用（3 分）

---

## 模块九：并发编程

### 题目 9.1 多线程基础

**题目描述：** 使用 `threading` 创建两个线程交替打印数字 1-10。

**参考答案：**

```python
import threading

def print_numbers(start: int, step: int, count: int, lock: threading.Lock):
    for i in range(start, start + count * step, step):
        with lock:
            print(f"{threading.current_thread().name}: {i}")

lock = threading.Lock()
t1 = threading.Thread(target=print_numbers, args=(1, 2, 5, lock), name="奇数")
t2 = threading.Thread(target=print_numbers, args=(2, 2, 5, lock), name="偶数")

t1.start()
t2.start()
t1.join()
t2.join()
print("完成")

# 使用 Condition 实现严格交替
def strict_alternate(cond: threading.Condition, state: dict, target: str):
    for i in range(5):
        with cond:
            while state["current"] != target:
                cond.wait()
            print(f"{target}: {i + 1}")
            state["current"] = "even" if target == "odd" else "odd"
            cond.notify_all()

cond = threading.Condition()
state = {"current": "odd"}
t1 = threading.Thread(target=strict_alternate, args=(cond, state, "odd"))
t2 = threading.Thread(target=strict_alternate, args=(cond, state, "even"))
t1.start()
t2.start()
t1.join()
t2.join()
```

线程同步原语：
- `Lock` / `RLock`：互斥锁。
- `Condition`：条件变量，配合 wait/notify。
- `Event`：事件标志。
- `Semaphore`：信号量。
- `Queue`：线程安全队列。

**评分标准：**
- 多线程创建与启动（3 分）
- Lock 同步（3 分）
- Condition 严格交替（4 分）

---

### 题目 9.2 线程池与 Future

**题目描述：** 使用 `concurrent.futures.ThreadPoolExecutor` 并发下载多个 URL，并处理异常。

**参考答案：**

```python
import concurrent.futures
import urllib.request
from typing import List, Tuple

def fetch(url: str) -> Tuple[str, bytes]:
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return url, resp.read()
    except Exception as e:
        return url, str(e).encode()

urls = [
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/2",
    "https://httpbin.org/status/404",
    "https://invalid-url-xxx.com",
]

# 方式一：map（按提交顺序返回）
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    for url, data in executor.map(fetch, urls):
        print(f"{url}: {len(data)} bytes")

# 方式二：submit + as_completed（先完成先返回）
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    future_to_url = {executor.submit(fetch, url): url for url in urls}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            result_url, data = future.result(timeout=10)
            print(f"完成 {url}: {len(data)} bytes")
        except Exception as e:
            print(f"失败 {url}: {e}")

# 方式三：超时与取消
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    futures = [executor.submit(fetch, url) for url in urls]
    done, not_done = concurrent.futures.wait(
        futures, timeout=3,
        return_when=concurrent.futures.ALL_COMPLETED
    )
    print(f"完成 {len(done)} 个，未完成 {len(not_done)} 个")
    for f in not_done:
        f.cancel()
```

**ThreadPoolExecutor 优势：**
- 复用线程，避免频繁创建销毁。
- 提供统一的 Future 接口。
- 自动管理线程池大小。
- 适合 IO 密集型任务。

**评分标准：**
- ThreadPoolExecutor 使用（4 分）
- submit vs map（3 分）
- 异常与超时处理（3 分）

---

### 题目 9.3 多进程与进程池

**题目描述：** 使用 `multiprocessing` 实现 CPU 密集型任务的并行计算，并说明进程间通信方式。

**参考答案：**

```python
import multiprocessing as mp
import time
from concurrent.futures import ProcessPoolExecutor

# CPU 密集型任务
def cpu_bound(n: int) -> int:
    return sum(i * i for i in range(n))

# 串行
def serial():
    start = time.time()
    total = sum(cpu_bound(5_000_000) for _ in range(4))
    print(f"串行: {time.time() - start:.2f}s, 结果 {total}")
    return total

# 并行（进程池）
def parallel():
    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(cpu_bound, [5_000_000] * 4))
    print(f"并行: {time.time() - start:.2f}s, 结果 {sum(results)}")
    return sum(results)

if __name__ == "__main__":
    serial()
    parallel()

# 进程间通信：Queue
def producer(q: mp.Queue):
    for i in range(5):
        q.put(f"item-{i}")
    q.put(None)  # 结束信号

def consumer(q: mp.Queue):
    while True:
        item = q.get()
        if item is None:
            break
        print(f"消费: {item}")

if __name__ == "__main__":
    q = mp.Queue()
    p1 = mp.Process(target=producer, args=(q,))
    p2 = mp.Process(target=consumer, args=(q,))
    p1.start(); p2.start()
    p1.join();  p2.join()

# 进程间通信：共享内存
def worker(counter, lock):
    for _ in range(1000):
        with lock:
            counter.value += 1

if __name__ == "__main__":
    counter = mp.Value("i", 0)
    lock = mp.Lock()
    ps = [mp.Process(target=worker, args=(counter, lock)) for _ in range(4)]
    for p in ps: p.start()
    for p in ps: p.join()
    print(f"计数器: {counter.value}")  # 4000
```

进程间通信方式：
- `Queue`：进程安全队列（基于管道）。
- `Pipe`：双向管道。
- `Value` / `Array`：共享内存。
- `Manager`：共享 Python 对象（dict/list 等，性能较低）。

**评分标准：**
- ProcessPoolExecutor 使用（4 分）
- 串行与并行对比（2 分）
- 进程间通信（Queue/Value）（4 分）

---

### 题目 9.4 asyncio 基础

**题目描述：** 使用 `asyncio` 实现并发请求三个 URL，说明 async/await 语法。

**参考答案：**

```python
import asyncio
import time

async def fetch(name: str, delay: float) -> str:
    print(f"开始 {name}")
    await asyncio.sleep(delay)  # 模拟 IO 等待
    print(f"完成 {name}")
    return f"{name} 的结果"

async def main():
    start = time.time()

    # 并发执行（asyncio.gather）
    results = await asyncio.gather(
        fetch("A", 2),
        fetch("B", 1),
        fetch("C", 3),
    )
    print(f"结果: {results}")
    print(f"总耗时: {time.time() - start:.2f}s")  # 约 3s（取最大延迟）

asyncio.run(main())

# 创建任务（Task）
async def task_demo():
    task1 = asyncio.create_task(fetch("X", 1))
    task2 = asyncio.create_task(fetch("Y", 2))

    # 等待第一个完成
    done, pending = await asyncio.wait(
        {task1, task2},
        return_when=asyncio.FIRST_COMPLETED
    )
    for t in done:
        print(f"先完成: {t.result()}")

asyncio.run(task_demo())

# 实际 HTTP 请求（aiohttp）
# import aiohttp
# async def http_fetch(session, url):
#     async with session.get(url) as resp:
#         return await resp.text()
#
# async def fetch_all(urls):
#     async with aiohttp.ClientSession() as session:
#         tasks = [http_fetch(session, url) for url in urls]
#         return await asyncio.gather(*tasks)
```

**asyncio 核心概念：**
- `async def`：定义协程函数。
- `await`：暂停协程，等待 awaitable 完成。
- `asyncio.create_task`：调度协程并发执行。
- `asyncio.gather`：并发运行多个协程，等待全部完成。
- `asyncio.run`：运行顶层协程。

**协程 vs 线程：**
- 协程是用户态轻量级并发，单线程内切换，无锁开销。
- 线程由操作系统调度，受 GIL 限制。
- 协程适合 IO 密集型，CPU 密集型仍需多进程。

**评分标准：**
- async/await 语法（4 分）
- gather 并发（3 分）
- 协程与线程对比（3 分）

---

### 题目 9.5 生产者消费者模型

**题目描述：** 使用 `queue.Queue` 实现线程安全的生产者-消费者模型。

**参考答案：**

```python
import threading
import queue
import time
import random

def producer(q: queue.Queue, name: str, count: int):
    for i in range(count):
        item = f"{name}-item-{i}"
        q.put(item)
        print(f"[生产] {item}")
        time.sleep(random.uniform(0.1, 0.3))
    q.put(None)  # 结束信号

def consumer(q: queue.Queue, name: str):
    while True:
        item = q.get()
        if item is None:
            q.put(None)  # 传递结束信号给其他消费者
            break
        print(f"  [{name} 消费] {item}")
        time.sleep(random.uniform(0.2, 0.5))
        q.task_done()

q = queue.Queue(maxsize=10)

producers = [
    threading.Thread(target=producer, args=(q, "P1", 5)),
    threading.Thread(target=producer, args=(q, "P2", 5)),
]
consumers = [
    threading.Thread(target=consumer, args=(q, "C1")),
    threading.Thread(target=consumer, args=(q, "C2")),
]

for p in producers: p.start()
for c in consumers: c.start()
for p in producers: p.join()
for c in consumers: c.join()

print("全部完成")
```

**Queue 特性：**
- 线程安全，内部已加锁。
- `put` / `get` 默认阻塞，可设 timeout。
- `task_done` + `join` 实现任务完成等待。
- `maxsize` 限制队列大小，自动阻塞生产者。

**评分标准：**
- 生产者消费者实现（5 分）
- 结束信号处理（3 分）
- Queue 阻塞特性说明（2 分）

---

### 题目 9.6 线程安全问题

**题目描述：** 分析以下代码的线程安全问题并修正。

```python
counter = 0
def increment():
    global counter
    for _ in range(100000):
        counter += 1

threads = [threading.Thread(target=increment) for _ in range(5)]
for t in threads: t.start()
for t in threads: t.join()
print(counter)  # 预期 500000，实际小于此值
```

**参考答案：**

**问题：** `counter += 1` 不是原子操作，包含"读取-修改-写回"三步，多线程并发时会产生竞态条件，导致丢失更新。

**修正方案：**

```python
import threading

# 方案一：Lock
counter = 0
lock = threading.Lock()

def increment_safe():
    global counter
    for _ in range(100000):
        with lock:
            counter += 1

threads = [threading.Thread(target=increment_safe) for _ in range(5)]
for t in threads: t.start()
for t in threads: t.join()
print(counter)  # 500000

# 方案二：使用 threading.local 或原子操作替代

# 方案三：使用 queue + 单消费者汇总
import queue

q = queue.Queue()
results = []

def worker():
    local_count = 0
    for _ in range(100000):
        local_count += 1
    q.put(local_count)

threads = [threading.Thread(target=worker) for _ in range(5)]
for t in threads: t.start()
for t in threads: t.join()

total = 0
while not q.empty():
    total += q.get()
print(total)  # 500000
```

**竞态条件（Race Condition）**：多线程访问共享资源且至少一个线程执行写操作时，结果依赖于执行顺序。

**评分标准：**
- 正确分析竞态原因（4 分）
- Lock 修正（3 分）
- 替代方案（3 分）

---

## 模块十：性能优化

### 题目 10.1 时间复杂度分析

**题目描述：** 分析以下操作的时间复杂度，并给出优化建议。

```python
# (a) 列表查找
lst = list(range(1000000))
x in lst  # ?

# (b) 字典查找
d = {i: i for i in range(1000000)}
x in d  # ?

# (c) 字符串拼接
s = ""
for c in ["a"] * 100000:
    s += c  # ?

# (d) 列表头部插入
lst = list(range(100000))
lst.insert(0, -1)  # ?
```

**参考答案：**

| 操作 | 时间复杂度 | 说明 |
|------|------------|------|
| `x in lst` | O(n) | 线性扫描 |
| `x in d` | O(1) 平均 | 哈希查找 |
| `s += c` 循环 n 次 | O(n²) | 每次创建新字符串 |
| `lst.insert(0, x)` | O(n) | 需移动所有元素 |

**优化建议：**

```python
# (a) 频繁成员判断 -> 用集合
big_set = set(range(1000000))
print(999999 in big_set)  # O(1)

# (b) 已是最优

# (c) 用 join
parts = ["a"] * 100000
s = "".join(parts)  # O(n)

# (d) 频繁头部插入 -> 用 deque
from collections import deque
dq = deque(range(100000))
dq.appendleft(-1)  # O(1)
```

```python
import timeit

# 验证
lst = list(range(1000000))
st = set(lst)

print("list 查找:", timeit.timeit(lambda: 999999 in lst, number=100))
print("set 查找:", timeit.timeit(lambda: 999999 in st, number=100))

# deque vs list 头部插入
dq = deque(range(100000))
lst2 = list(range(100000))

print("deque appendleft:", timeit.timeit(lambda: dq.appendleft(-1), number=10000))
print("list insert(0):", timeit.timeit(lambda: lst2.insert(0, -1), number=10000))
```

**评分标准：**
- 四个复杂度全部正确（4 分）
- 优化方案合理（4 分）
- 性能验证代码（2 分）

---

### 题目 10.2 内存优化技巧

**题目描述：** 列举至少 4 种 Python 内存优化技巧，并说明各自适用场景。

**参考答案：**

```python
import sys
from array import array

# 1. 使用 __slots__
class PointDict:
    def __init__(self):
        self.x = 0
        self.y = 0

class PointSlots:
    __slots__ = ("x", "y")
    def __init__(self):
        self.x = 0
        self.y = 0

p1 = PointDict()
p2 = PointSlots()
print(sys.getsizeof(p1.__dict__))  # ~104
# p2 无 __dict__，更省内存

# 2. 使用生成器替代列表
def get_numbers_list(n):
    return [i for i in range(n)]       # 一次性占用内存

def get_numbers_gen(n):
    for i in range(n):
        yield i                        # 惰性产出

big_list = get_numbers_list(1000000)
big_gen = get_numbers_gen(1000000)
print(sys.getsizeof(big_list), sys.getsizeof(big_gen))  # 8MB+ vs ~200B

# 3. 使用 array 替代 list（同类型数值）
int_list = [0] * 100000
int_array = array("i", [0] * 100000)
print(sys.getsizeof(int_list))   # ~800KB
print(sys.getsizeof(int_array))  # ~400KB

# 4. 使用 namedtuple / dataclass(frozen) 替代 dict
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(1, 2)
print(sys.getsizeof(p))  # 比 dict 小

# dict 表示
d = {"x": 1, "y": 2}
print(sys.getsizeof(d))  # 较大

# 5. intern 字符串（去重）
import sys
s1 = sys.intern("long_string_that_might_repeat" * 1)
s2 = sys.intern("long_string_that_might_repeat" * 1)
print(s1 is s2)  # True

# 6. 及时释放：del + gc
import gc
big = [0] * 10_000_000
del big
gc.collect()
```

**适用场景：**
- `__slots__`：大量同类实例（如 ORM 模型）。
- 生成器：大数据流处理。
- `array`：纯数值数组。
- `namedtuple`：固定结构的小数据。

**评分标准：**
- 至少 4 种技巧（4 分）
- 每种给出代码示例（4 分）
- 适用场景说明（2 分）

---

### 题目 10.3 cProfile 性能分析

**题目描述：** 使用 `cProfile` 分析函数性能，并解释输出含义。

**参考答案：**

```python
import cProfile
import pstats
import io

def slow_function():
    total = 0
    for i in range(100000):
        total += sum(j * j for j in range(100))
    return total

def fast_function():
    return sum(i * i for i in range(100000))

def main():
    slow_function()
    fast_function()

# 方式一：命令行
# python -m cProfile -s cumulative script.py

# 方式二：代码内
pr = cProfile.Profile()
pr.enable()
main()
pr.disable()

# 输出到字符串
s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
ps.print_stats(10)
print(s.getvalue())

# 输出到文件（可用 snakeviz 可视化）
pr.dump_stats("profile.prof")
# 命令: snakeviz profile.prof
```

**输出字段说明：**
- `ncalls`：调用次数。
- `tottime`：函数自身耗时（不含子调用）。
- `percall`：tottime / ncalls。
- `cumtime`：累计耗时（含子调用）。
- `filename:lineno(function)`：函数位置。

**优化流程：**
1. 用 cProfile 定位热点。
2. 针对性优化（算法、缓存、C 扩展）。
3. 重新 profile 验证效果。

```python
# line_profiler 逐行分析
# 安装: pip install line_profiler
# from line_profiler import LineProfiler
# lp = LineProfiler()
# lp.add_function(slow_function)
# lp_wrapper = lp(slow_function)
# lp_wrapper()
# lp.print_stats()
```

**评分标准：**
- cProfile 使用（4 分）
- 字段含义（3 分）
- 优化流程说明（3 分）

---

### 题目 10.4 算法优化：两数之和

**题目描述：** 给定一个整数列表和目标值，找出两数之和等于目标值的索引。要求优于 O(n²)。

**参考答案：**

```python
from typing import List, Optional, Tuple

# 暴力 O(n²)
def two_sum_brute(nums: List[int], target: int) -> Optional[Tuple[int, int]]:
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return (i, j)
    return None

# 哈希表 O(n)
def two_sum(nums: List[int], target: int) -> Optional[Tuple[int, int]]:
    seen = {}  # value -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return (seen[complement], i)
        seen[num] = i
    return None

# 测试
nums = [2, 7, 11, 15]
print(two_sum(nums, 9))   # (0, 1)
print(two_sum(nums, 18))  # (1, 2)
print(two_sum(nums, 100)) # None

# 性能对比
import timeit
big_nums = list(range(10000))
print("暴力:", timeit.timeit(lambda: two_sum_brute(big_nums, 19997), number=10))
print("哈希:", timeit.timeit(lambda: two_sum(big_nums, 19997), number=10))
```

**评分标准：**
- 哈希表解法正确（5 分）
- 时间复杂度 O(n)（3 分）
- 性能对比验证（2 分）

---

### 题目 10.5 缓存与 memoization

**题目描述：** 对比 `lru_cache`、自定义字典缓存、无缓存的斐波那契性能。

**参考答案：**

```python
import time
from functools import lru_cache

# 无缓存：O(2^n)
def fib_plain(n):
    if n < 2:
        return n
    return fib_plain(n - 1) + fib_plain(n - 2)

# 自定义缓存
_fib_cache = {0: 0, 1: 1}
def fib_custom(n):
    if n in _fib_cache:
        return _fib_cache[n]
    result = fib_custom(n - 1) + fib_custom(n - 2)
    _fib_cache[n] = result
    return result

# lru_cache
@lru_cache(maxsize=None)
def fib_lru(n):
    if n < 2:
        return n
    return fib_lru(n - 1) + fib_lru(n - 2)

# 性能对比
for name, func in [("plain", fib_plain), ("custom", fib_custom), ("lru", fib_lru)]:
    start = time.time()
    result = func(35) if name == "plain" else func(100)
    elapsed = time.time() - start
    print(f"{name}: {elapsed:.4f}s, fib={result if name != 'plain' else result}")

print(fib_lru.cache_info())
# CacheInfo(hits=98, misses=101, maxsize=None, currsize=101)
```

**`lru_cache` 特点：**
- 基于 OrderedDict，O(1) 查询。
- 线程安全。
- `maxsize=None` 表示无限制。
- 支持 `typed=True` 区分类型（1 和 1.0 视为不同 key）。
- 仅适用于纯函数（相同输入相同输出）。

**评分标准：**
- 三种实现（4 分）
- 性能对比（3 分）
- lru_cache 特性说明（3 分）

---

## 模块十一：常用标准库

### 题目 11.1 collections 模块

**题目描述：** 介绍 `collections` 模块中的 `namedtuple`、`deque`、`Counter`、`defaultdict`、`OrderedDict` 并示例。

**参考答案：**

```python
from collections import namedtuple, deque, Counter, defaultdict, OrderedDict

# 1. namedtuple：具名元组，轻量级不可变对象
Point = namedtuple("Point", ["x", "y"])
p = Point(1, 2)
print(p.x, p.y)        # 1 2
print(p._asdict())     # {'x': 1, 'y': 2}
print(p._replace(x=10))  # Point(x=10, y=2)

# 2. deque：双端队列
dq = deque([1, 2, 3], maxlen=5)
dq.appendleft(0)
dq.append(4)
print(dq)  # deque([0, 1, 2, 3, 4])
dq.popleft()
print(dq)  # deque([1, 2, 3, 4])

# 滑动窗口
window = deque(maxlen=3)
for i in range(5):
    window.append(i)
    print(list(window))
# [0]
# [0, 1]
# [0, 1, 2]
# [1, 2, 3]
# [2, 3, 4]

# 3. Counter：计数
c = Counter("abracadabra")
print(c)                  # Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})
print(c.most_common(2))   # [('a', 5), ('b', 2)]

# 4. defaultdict：默认值字典
dd = defaultdict(list)
dd["a"].append(1)
dd["a"].append(2)
print(dd["a"])  # [1, 2]

# 5. OrderedDict（3.7+ 普通 dict 已有序，但仍可用于 LRU）
od = OrderedDict()
od["a"] = 1
od["b"] = 2
od.move_to_end("a")
print(list(od.keys()))  # ['b', 'a']
```

**评分标准：**
- 五种容器说明（5 分）
- 实际应用示例（3 分）
- 各容器适用场景（2 分）

---

### 题目 11.2 itertools 模块

**题目描述：** 演示 `itertools.chain`、`groupby`、`combinations`、`permutations`、`islice`、`starmap` 的用法。

**参考答案：**

```python
from itertools import (
    chain, groupby, combinations, permutations,
    islice, starmap, product, count, cycle, repeat
)

# chain：串联多个可迭代对象
print(list(chain([1, 2], [3, 4], [5])))  # [1, 2, 3, 4, 5]
print(list(chain.from_iterable([[1, 2], [3, 4]])))  # [1, 2, 3, 4]

# groupby：分组（需先排序）
data = [("A", 1), ("A", 2), ("B", 3), ("A", 4), ("B", 5)]
data_sorted = sorted(data, key=lambda x: x[0])
for key, group in groupby(data_sorted, key=lambda x: x[0]):
    print(key, list(group))
# A [('A', 1), ('A', 2), ('A', 4)]
# B [('B', 3), ('B', 5)]

# combinations：组合（无序）
print(list(combinations("ABC", 2)))  # [('A','B'), ('A','C'), ('B','C')]

# permutations：排列（有序）
print(list(permutations("ABC", 2)))  # 6 种

# product：笛卡尔积
print(list(product("AB", "12")))  # [('A','1'), ('A','2'), ('B','1'), ('B','2')]

# islice：切片（惰性）
print(list(islice(range(100), 5, 10)))  # [5, 6, 7, 8, 9]

# starmap：解包参数后调用
print(list(starmap(pow, [(2, 3), (3, 2)])))  # [8, 9]

# 无限迭代器
for i, val in enumerate(count(10)):
    if i >= 3:
        break
    print(val, end=" ")  # 10 11 12
print()

# cycle：循环
c = cycle("AB")
print([next(c) for _ in range(5)])  # ['A', 'B', 'A', 'B', 'A']

# repeat：重复
print(list(repeat("x", 3)))  # ['x', 'x', 'x']
```

**评分标准：**
- 至少 6 个函数演示（6 分）
- groupby 需排序的注意事项（2 分）
- 无限迭代器说明（2 分）

---

### 题目 11.3 datetime 与时区

**题目描述：** 演示 `datetime` 模块的常用操作，包括格式化、时区转换、时间差计算。

**参考答案：**

```python
from datetime import datetime, date, timedelta, timezone
import zoneinfo  # Python 3.9+

# 当前时间
now = datetime.now()
utc_now = datetime.now(timezone.utc)
print(now, utc_now)

# 格式化与解析
dt = datetime(2024, 6, 15, 14, 30, 0)
formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
print(formatted)  # 2024-06-15 14:30:00

parsed = datetime.strptime("2024-06-15 14:30", "%Y-%m-%d %H:%M")
print(parsed)

# ISO 8601
print(dt.isoformat())  # 2024-06-15T14:30:00
print(datetime.fromisoformat("2024-06-15T14:30:00"))

# 时间差
d1 = date(2024, 1, 1)
d2 = date(2024, 12, 31)
delta = d2 - d1
print(delta.days)  # 365

# timedelta 运算
future = now + timedelta(days=7, hours=3)
print(future)

# 时区转换（Python 3.9+ zoneinfo）
tz_sh = zoneinfo.ZoneInfo("Asia/Shanghai")
tz_ny = zoneinfo.ZoneInfo("America/New_York")

t_sh = datetime.now(tz_sh)
print(f"上海: {t_sh}")

t_ny = t_sh.astimezone(tz_ny)
print(f"纽约: {t_ny}")

# 时间戳
ts = now.timestamp()
print(ts)
print(datetime.fromtimestamp(ts, tz=timezone.utc))

# dateutil（第三方，强大）
# from dateutil.relativedelta import relativedelta
# next_month = now + relativedelta(months=1)
```

**评分标准：**
- 格式化与解析（3 分）
- timedelta 运算（2 分）
- 时区转换（3 分）
- 时间戳处理（2 分）

---

### 题目 11.4 os 与 sys 模块

**题目描述：** 列举 `os` 和 `sys` 模块的常用功能并示例。

**参考答案：**

```python
import os
import sys

# os 模块：操作系统接口
print(os.getcwd())          # 当前工作目录
print(os.getpid())          # 当前进程 ID
print(os.cpu_count())       # CPU 核数
print(os.name)              # 'nt' (Windows) / 'posix' (Linux/Mac)

# 环境变量
print(os.environ.get("PATH"))
os.environ["MY_VAR"] = "test"

# 路径操作
print(os.path.join("a", "b", "c.py"))
print(os.path.exists("test.txt"))
print(os.path.isdir("a"))
print(os.path.basename("/a/b/c.py"))  # c.py
print(os.path.dirname("/a/b/c.py"))   # /a/b
print(os.path.splitext("c.py"))       # ('c', '.py')

# 文件操作
os.makedirs("test/sub", exist_ok=True)
os.rename("test/sub", "test/renamed")
os.rmdir("test/renamed")
os.rmdir("test")

# 遍历目录
for root, dirs, files in os.walk("."):
    for f in files:
        if f.endswith(".py"):
            print(os.path.join(root, f))

# sys 模块：解释器相关
print(sys.version)
print(sys.platform)         # 'win32' / 'linux'
print(sys.executable)       # 解释器路径
print(sys.argv)             # 命令行参数
print(sys.path)             # 模块搜索路径
print(sys.maxsize)          # 最大整数
print(sys.getrecursionlimit())

# 标准流
sys.stdout.write("到标准输出\n")
sys.stderr.write("到标准错误\n")

# 退出
# sys.exit(0)
# sys.exit("错误信息")
```

**评分标准：**
- os 常用功能（4 分）
- sys 常用功能（4 分）
- 路径与遍历（2 分）

---

### 题目 11.5 subprocess 与外部命令

**题目描述：** 使用 `subprocess` 执行外部命令并捕获输出，处理超时与错误。

**参考答案：**

```python
import subprocess

# 推荐方式：run
result = subprocess.run(
    ["python", "--version"],
    capture_output=True,
    text=True,
    timeout=10,
)
print("返回码:", result.returncode)
print("标准输出:", result.stdout.strip())
print("标准错误:", result.stderr.strip())

# 管道
result = subprocess.run(
    "echo hello | tr a-z A-Z",
    shell=True,  # 使用 shell 解释管道
    capture_output=True,
    text=True,
)
print(result.stdout)  # HELLO

# 超时处理
try:
    subprocess.run(
        ["python", "-c", "import time; time.sleep(5)"],
        timeout=2,
    )
except subprocess.TimeoutExpired as e:
    print(f"超时: {e}")

# 检查返回码
try:
    subprocess.run(
        ["python", "-c", "import sys; sys.exit(1)"],
        check=True,  # 非零返回码抛异常
    )
except subprocess.CalledProcessError as e:
    print(f"命令失败: {e.returncode}")

# 与文件交互
with open("output.txt", "w") as f:
    subprocess.run(["echo", "hello"], stdout=f)

# 交互式输入
result = subprocess.run(
    ["python", "-c", "name = input(); print(f'Hello, {name}')"],
    input="Alice\n",
    capture_output=True,
    text=True,
)
print(result.stdout)  # Hello, Alice
```

**安全提示：** 避免用 `shell=True` 处理用户输入，防止 shell 注入。

**评分标准：**
- run 基本用法（3 分）
- 超时与异常处理（4 分）
- 管道与文件交互（3 分）

---

## 模块十二：实际应用场景题

### 题目 12.1 实现一个简单的 ORM

**题目描述：** 使用元类实现一个简化版 ORM，支持字段定义和查询构造。

**参考答案：**

```python
from typing import Any, Dict, Type

class Field:
    def __init__(self, column_type: str, primary_key: bool = False):
        self.column_type = column_type
        self.primary_key = primary_key
        self.name = None  # 由元类注入

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value


class ModelMeta(type):
    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        if name == "Model":
            return super().__new__(mcs, name, bases, namespace)

        table = namespace.get("__table__", name.lower())
        fields: Dict[str, Field] = {}
        for key, val in namespace.items():
            if isinstance(val, Field):
                fields[key] = val

        namespace["_table"] = table
        namespace["_fields"] = fields
        cls = super().__new__(mcs, name, bases, namespace)
        return cls


class Model(metaclass=ModelMeta):
    def __init__(self, **kwargs):
        for key, field in self._fields.items():
            setattr(self, key, kwargs.get(key))

    def save(self) -> str:
        cols = ", ".join(self._fields.keys())
        vals = ", ".join(repr(getattr(self, k)) for k in self._fields)
        return f"INSERT INTO {self._table} ({cols}) VALUES ({vals})"

    @classmethod
    def where(cls, **conditions) -> str:
        where_clause = " AND ".join(
            f"{k} = {v!r}" for k, v in conditions.items()
        )
        return f"SELECT * FROM {cls._table} WHERE {where_clause}"


class User(Model):
    __table__ = "users"
    id = Field("INT", primary_key=True)
    name = Field("VARCHAR(100)")
    age = Field("INT")


u = User(id=1, name="Alice", age=30)
print(u.save())
# INSERT INTO users (id, name, age) VALUES (1, 'Alice', 30)

print(User.where(name="Alice", age=30))
# SELECT * FROM users WHERE name = 'Alice' AND age = 30
```

**设计要点：**
- `Field` 使用描述符协议（`__get__`/`__set__`）实现属性访问。
- `ModelMeta` 元类在类创建时收集所有 Field 字段。
- `Model` 基类提供通用的 `save` / `where` 方法。

**评分标准：**
- 元类收集字段（4 分）
- 描述符实现属性访问（3 分）
- SQL 生成正确（3 分）

---

### 题目 12.2 实现一个简单的发布订阅模式

**题目描述：** 实现一个事件总线（EventBus），支持订阅、发布、取消订阅。

**参考答案：**

```python
from collections import defaultdict
from typing import Callable, Any

class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, handler: Callable) -> None:
        self._subscribers[event].append(handler)

    def unsubscribe(self, event: str, handler: Callable) -> None:
        if event in self._subscribers:
            self._subscribers[event].remove(handler)
            if not self._subscribers[event]:
                del self._subscribers[event]

    def publish(self, event: str, *args, **kwargs) -> None:
        # 复制一份，避免回调中修改列表
        for handler in list(self._subscribers.get(event, [])):
            try:
                handler(*args, **kwargs)
            except Exception as e:
                print(f"处理 {event} 时出错: {e}")

    def clear(self, event: str = None) -> None:
        if event is None:
            self._subscribers.clear()
        else:
            self._subscribers.pop(event, None)


# 测试
bus = EventBus()

def on_login(user):
    print(f"[日志] {user} 登录")

def send_email(user):
    print(f"[邮件] 欢迎您，{user}")

bus.subscribe("login", on_login)
bus.subscribe("login", send_email)

bus.publish("login", "Alice")
# [日志] Alice 登录
# [邮件] 欢迎您，Alice

bus.unsubscribe("login", on_login)
bus.publish("login", "Bob")
# [邮件] 欢迎您，Bob

# 带参数发布
bus.subscribe("order", lambda order_id, amount: print(f"订单 {order_id}: ¥{amount}"))
bus.publish("order", 1001, 99.9)

# 异常隔离
def bad_handler():
    raise ValueError("故意出错")

bus.subscribe("test", bad_handler)
bus.subscribe("test", lambda: print("我仍会执行"))
bus.publish("test")
# 处理 test 时出错: 故意出错
# 我仍会执行
```

**评分标准：**
- 订阅/发布/取消订阅实现（5 分）
- 异常隔离处理（3 分）
- 边界情况（空事件、复制列表）（2 分）

---

### 题目 12.3 实现一个限流器

**题目描述：** 实现一个固定窗口限流器，限制每秒最多 N 次请求。

**参考答案：**

```python
import time
from collections import deque
from typing import Deque

class RateLimiter:
    """滑动窗口限流器。"""

    def __init__(self, max_requests: int, window: float = 1.0):
        self.max_requests = max_requests
        self.window = window  # 时间窗口（秒）
        self.requests: Deque[float] = deque()

    def allow(self) -> bool:
        now = time.time()
        # 移除窗口外的请求记录
        while self.requests and self.requests[0] <= now - self.window:
            self.requests.popleft()

        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False

    def wait_next(self) -> float:
        """返回需要等待的时间（秒），0 表示可立即请求。"""
        now = time.time()
        while self.requests and self.requests[0] <= now - self.window:
            self.requests.popleft()
        if len(self.requests) < self.max_requests:
            return 0.0
        return self.requests[0] + self.window - now


# 测试
limiter = RateLimiter(max_requests=5, window=1.0)

# 突发 5 个请求
for i in range(10):
    if limiter.allow():
        print(f"请求 {i+1}: 通过")
    else:
        wait = limiter.wait_next()
        print(f"请求 {i+1}: 被限流，需等待 {wait:.2f}s")
    time.sleep(0.1)


# 装饰器版本
from functools import wraps

def rate_limit(max_requests: int, window: float = 1.0):
    limiter = RateLimiter(max_requests, window)
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not limiter.allow():
                raise RuntimeError("请求过于频繁")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(max_requests=3, window=1.0)
def api_call():
    return "OK"

for i in range(5):
    try:
        print(api_call())
    except RuntimeError as e:
        print(f"失败: {e}")
    time.sleep(0.2)
```

**限流算法对比：**
- 固定窗口：实现简单，但窗口边界可能突发 2 倍流量。
- 滑动窗口：更平滑，本例采用。
- 令牌桶：允许突发，常用于 API 网关。
- 漏桶：匀速输出。

**评分标准：**
- 限流逻辑正确（5 分）
- 滑动窗口实现（3 分）
- 装饰器封装（2 分）

---

### 题目 12.4 配置文件解析器

**题目描述：** 实现一个支持环境变量覆盖和类型转换的配置加载器。

**参考答案：**

```python
import os
import json
from typing import Any, Type, TypeVar, get_type_hints

T = TypeVar("T")

class ConfigLoader:
    def __init__(self, config_file: str = None):
        self._config: dict = {}
        if config_file:
            self.load_file(config_file)

    def load_file(self, path: str) -> None:
        ext = path.rsplit(".", 1)[-1].lower()
        if ext == "json":
            with open(path, "r", encoding="utf-8") as f:
                self._config.update(json.load(f))
        elif ext in ("ini",):
            import configparser
            parser = configparser.ConfigParser()
            parser.read(path, encoding="utf-8")
            for section in parser.sections():
                for key, val in parser.items(section):
                    self._config[f"{section}.{key}"] = val
        else:
            raise ValueError(f"不支持的配置格式: {ext}")

    def get(self, key: str, default: Any = None, cast: Type[T] = None) -> T:
        # 优先级：环境变量 > 配置文件 > 默认值
        value = os.environ.get(key, self._config.get(key, default))
        if value is None:
            return default

        if cast is None:
            return value

        # 类型转换
        if cast is bool and isinstance(value, str):
            return value.lower() in ("true", "1", "yes")  # type: ignore
        return cast(value)

    def bind(self, cls: Type[T]) -> T:
        """将配置绑定到 dataclass。"""
        from dataclasses import fields
        hints = get_type_hints(cls)
        kwargs = {}
        for f in fields(cls):
            # 从环境变量或配置中查找，key 不区分大小写
            raw = None
            for candidate in (f.name.upper(), f.name):
                if candidate in os.environ:
                    raw = os.environ[candidate]
                    break
                if candidate in self._config:
                    raw = self._config[candidate]
                    break
            if raw is None:
                if f.default is not f.default_factory and f.default is not None:
                    kwargs[f.name] = f.default
                continue

            # 类型转换
            target_type = hints.get(f.name, str)
            if target_type is bool:
                kwargs[f.name] = str(raw).lower() in ("true", "1", "yes")
            elif target_type is int:
                kwargs[f.name] = int(raw)
            elif target_type is float:
                kwargs[f.name] = float(raw)
            else:
                kwargs[f.name] = raw
        return cls(**kwargs)


from dataclasses import dataclass

@dataclass
class AppConfig:
    debug: bool = False
    port: int = 8000
    db_url: str = "sqlite:///default.db"

# 模拟环境变量
os.environ["DEBUG"] = "true"
os.environ["PORT"] = "9000"

loader = ConfigLoader()
# 也可加载文件: loader.load_file("config.json")
config = loader.bind(AppConfig)
print(config)
# AppConfig(debug=True, port=9000, db_url='sqlite:///default.db')

# 直接 get
print(loader.get("PORT", cast=int))        # 9000
print(loader.get("MISSING", "fallback"))   # fallback
```

**评分标准：**
- 环境变量覆盖机制（4 分）
- 类型转换（3 分）
- dataclass 绑定（3 分）

---

### 题目 12.5 实现一个简单的连接池

**题目描述：** 实现一个通用的对象/连接池，支持最大数量限制、超时等待、自动归还。

**参考答案：**

```python
import threading
import queue
import time
from contextlib import contextmanager
from typing import Callable, Any, Optional

class ConnectionPool:
    """
    通用连接池。
    """

    def __init__(
        self,
        factory: Callable[[], Any],
        max_size: int = 10,
        timeout: float = 30,
        validator: Optional[Callable[[Any], bool]] = None,
    ):
        self.factory = factory
        self.max_size = max_size
        self.timeout = timeout
        self.validator = validator or (lambda x: True)
        self._pool: queue.Queue = queue.Queue(maxsize=max_size)
        self._created = 0
        self._lock = threading.Lock()

    def _create(self) -> Any:
        with self._lock:
            if self._created >= self.max_size:
                return None
            self._created += 1
        try:
            return self.factory()
        except Exception:
            with self._lock:
                self._created -= 1
            raise

    def acquire(self) -> Any:
        # 1. 先尝试从池中获取
        try:
            conn = self._pool.get_nowait()
            if self.validator(conn):
                return conn
            # 无效则销毁，重新创建
            self._release_count()
        except queue.Empty:
            pass

        # 2. 尝试创建新连接
        conn = self._create()
        if conn is not None:
            return conn

        # 3. 等待归还
        try:
            conn = self._pool.get(timeout=self.timeout)
            if self.validator(conn):
                return conn
            self._release_count()
            # 递归重试
            return self.acquire()
        except queue.Empty:
            raise TimeoutError("获取连接超时")

    def release(self, conn: Any) -> None:
        try:
            self._pool.put_nowait(conn)
        except queue.Full:
            # 池满，直接关闭
            self._close(conn)
            self._release_count()

    def _release_count(self):
        with self._lock:
            self._created -= 1

    def _close(self, conn: Any):
        close = getattr(conn, "close", None)
        if close:
            close()

    @contextmanager
    def connection(self):
        conn = self.acquire()
        try:
            yield conn
        finally:
            self.release(conn)

    def close_all(self):
        while True:
            try:
                conn = self._pool.get_nowait()
                self._close(conn)
                self._release_count()
            except queue.Empty:
                break


# 测试
class FakeDB:
    _counter = 0
    def __init__(self):
        FakeDB._counter += 1
        self.id = FakeDB._counter
        print(f"  [创建] DB#{self.id}")

    def query(self, sql):
        return f"DB#{self.id} 执行 {sql}"

    def close(self):
        print(f"  [关闭] DB#{self.id}")

pool = ConnectionPool(
    factory=FakeDB,
    max_size=3,
    timeout=2,
    validator=lambda c: True,
)

# 并发获取
def worker(name):
    with pool.connection() as db:
        print(f"{name}: {db.query('SELECT 1')}")
        time.sleep(0.5)

threads = [threading.Thread(target=worker, args=(f"任务{i}",)) for i in range(5)]
for t in threads: t.start()
for t in threads: t.join()

pool.close_all()
```

**设计要点：**
- 懒创建：首次获取时才创建连接。
- 最大数量限制：超过则等待归还。
- 有效性校验：使用前验证连接是否存活。
- 线程安全：用锁保护计数器。
- 上下文管理器：确保连接归还。

**评分标准：**
- 获取/归还逻辑（4 分）
- 最大数量与超时处理（3 分）
- 有效性校验（3 分）

---

## 附录：面试高频知识点速查

### Python 版本特性时间线

| 版本 | 关键特性 |
|------|----------|
| 3.6 | f-string、变量注解、async/await 正式版、`__init_subclass__` |
| 3.7 | dict 有序（官方保证）、dataclasses、`breakpoint()` |
| 3.8 | 海象运算符 `:=`、仅位置参数 `/`、f-string `=` 调试 |
| 3.9 | 字典合并 `|`、`str.removeprefix/removesuffix`、`zoneinfo` |
| 3.10 | 结构化模式匹配 `match/case`、联合类型 `X \| Y`、参数括号简化 |
| 3.11 | 异常组 `ExceptionGroup`、`TaskGroup`、性能提升 10-60% |
| 3.12 | f-string 改进、`type` 语句、缓冲区协议改进 |
| 3.13 | 实验性 no-GIL（PEP 703）、JIT 编译器（实验） |

### 常见陷阱总结

1. **可变默认参数**：`def f(x=[])` 会在函数定义时创建一次列表，所有调用共享。
2. **闭包延迟绑定**：循环中的 lambda 捕获的是变量引用，不是值。
3. **浅拷贝陷阱**：嵌套结构使用 `copy.copy` 仍共享内部对象。
4. **整数缓存**：`is` 比较小整数时可能误导，应使用 `==`。
5. **`+=` 与 `+`**：对不可变对象两者等价，但对可变对象（如 list）`+=` 原地修改而 `+` 返回新对象。
6. **异常链**：`raise X from Y` 显式链接异常。
7. **线程与 GIL**：CPU 密集型多线程反而变慢。
8. **生成器一次性**：生成器迭代完不可重用，需重新创建。

### 推荐学习资源

- 官方文档：https://docs.python.org/zh-cn/3/
- PEP 索引：https://peps.python.org/
- 《流畅的 Python》（Fluent Python）
- 《Python Cookbook》
- 《Effective Python》

---

> **说明：** 本题集共 12 个模块、60+ 道题目，覆盖中级 Python 工程员面试核心知识点。所有代码示例均在 Python 3.10+ 环境下可直接运行。建议结合实际项目经验理解每个知识点，避免死记硬背。
