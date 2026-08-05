# Python 高级特性详解

## 1. 切片（Slice）

### 1.1 什么是切片

切片用于获取 list、tuple、字符串等**有序序列**的一部分，是 Python 中非常强大且简洁的特性。

### 1.2 切片语法

```python
sequence[start:stop:step]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `start` | 起始索引（包含） | 0 |
| `stop` | 结束索引（不包含） | 序列长度 |
| `step` | 步长 | 1 |

### 1.3 基本用法

```python
L = ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank']

# 基本切片
print(L[0:3])    # ['Alice', 'Bob', 'Charlie']，前3个
print(L[:3])     # 同上，省略 start
print(L[3:])     # ['David', 'Eve', 'Frank']，从索引3到末尾
print(L[:])      # 完整副本

# 负数索引
print(L[-2:])    # ['Eve', 'Frank']，最后2个
print(L[-3:-1])  # ['David', 'Eve']

# 步长
print(L[::2])    # ['Alice', 'Charlie', 'Eve']，每隔一个取一个
print(L[1::2])   # ['Bob', 'David', 'Frank']
print(L[::-1])   # 反转列表
print(L[::-2])   # ['Frank', 'David', 'Alice']，反向每隔一个
```

### 1.4 切片的应用

```python
# 字符串切片
s = "Hello, World"
print(s[:5])      # 'Hello'
print(s[7:])      # 'World'
print(s[::-1])    # 'dlroW ,olleH'，反转字符串

# tuple 切片
t = (1, 2, 3, 4, 5)
print(t[1:4])     # (2, 3, 4)

# 切片赋值（list 可变）
nums = [1, 2, 3, 4, 5]
nums[1:3] = [20, 30, 40]
print(nums)       # [1, 20, 30, 40, 4, 5]

# 删除切片
nums = [1, 2, 3, 4, 5]
del nums[1:3]
print(nums)       # [1, 4, 5]
```

### 1.5 实用技巧

```python
# 取前 N 个元素
def first_n(lst, n):
    return lst[:n]

# 取后 N 个元素
def last_n(lst, n):
    return lst[-n:] if n > 0 else []

# 每 N 个取一个
def every_n(lst, n):
    return lst[::n]

# 去掉首尾
def trim(s):
    return s[1:-1]

print(first_n([1,2,3,4,5], 3))  # [1, 2, 3]
print(last_n([1,2,3,4,5], 2))   # [4, 5]
print(every_n(list(range(10)), 3))  # [0, 3, 6, 9]
print(trim("Hello"))  # 'ell'
```

---

## 2. 迭代（Iteration）

### 2.1 for 循环与迭代

Python 的 `for` 循环可以遍历任何**可迭代对象（Iterable）**：

```python
# 遍历列表
for x in [1, 2, 3]:
    print(x)

# 遍历字符串
for ch in "ABC":
    print(ch)

# 遍历字典
d = {'name': 'Alice', 'age': 25}
for key in d:                  # 默认遍历键
    print(key)
for value in d.values():       # 遍历值
    print(value)
for key, value in d.items():   # 遍历键值对
    print(f"{key}: {value}")
```

### 2.2 判断可迭代对象

```python
from collections.abc import Iterable

print(isinstance([1, 2, 3], Iterable))   # True
print(isinstance("abc", Iterable))       # True
print(isinstance(123, Iterable))         # False
print(isinstance((x for x in range(3)), Iterable))  # True
```

### 2.3 enumerate：带索引迭代

```python
# 同时获取索引和值
fruits = ['apple', 'banana', 'cherry']
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# 指定起始索引
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}: {fruit}")

# 输出：
# 1: apple
# 2: banana
# 3: cherry
```

### 2.4 zip：并行迭代

```python
names = ['Alice', 'Bob', 'Charlie']
ages = [25, 30, 35]
cities = ['北京', '上海', '广州']

# 同时遍历多个序列
for name, age, city in zip(names, ages, cities):
    print(f"{name}, {age}岁, {city}")

# zip 返回迭代器，需要 list 转换
pairs = list(zip(names, ages))
print(pairs)  # [('Alice', 25), ('Bob', 30), ('Charlie', 35)]

# 长度不一致时，以最短的为准
print(list(zip([1, 2, 3], ['a', 'b'])))  # [(1, 'a'), (2, 'b')]

# zip_longest：以最长的为准（需导入）
from itertools import zip_longest
print(list(zip_longest([1, 2, 3], ['a', 'b'], fillvalue='?')))
# [(1, 'a'), (2, 'b'), (3, '?')]
```

### 2.5 同时引用多个变量

```python
# 列表解包
x, y, z = [1, 2, 3]
print(x, y, z)  # 1 2 3

# 嵌套解包
for x, y in [(1, 'a'), (2, 'b'), (3, 'c')]:
    print(f"{x} -> {y}")

# 字典项解包
for key, value in {'a': 1, 'b': 2}.items():
    print(f"{key} = {value}")
```

### 2.6 itertools 迭代工具

```python
import itertools

# 无限计数器
for i, val in enumerate(itertools.count(10, 2)):
    if i >= 5:
        break
    print(val)  # 10, 12, 14, 16, 18

# 循环重复
cycle = itertools.cycle('ABC')
print([next(cycle) for _ in range(5)])  # ['A', 'B', 'C', 'A', 'B']

# 排列组合
print(list(itertools.permutations([1, 2, 3], 2)))
# [(1,2),(1,3),(2,1),(2,3),(3,1),(3,2)]
print(list(itertools.combinations([1, 2, 3], 2)))
# [(1,2),(1,3),(2,3)]

# 链接多个迭代器
for x in itertools.chain([1, 2], [3, 4], [5]):
    print(x)  # 1, 2, 3, 4, 5
```

---

## 3. 列表推导式（List Comprehension）

### 3.1 基本语法

列表推导式是用简洁语法创建列表的方式：

```python
# 语法
[expression for item in iterable if condition]

# 等价于
result = []
for item in iterable:
    if condition:
        result.append(expression)
```

### 3.2 基本示例

```python
# 生成平方数列表
squares = [x**2 for x in range(10)]
print(squares)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# 带条件过滤
evens = [x for x in range(20) if x % 2 == 0]
print(evens)  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

# 复杂表达式
words = ['hello', 'world', 'python']
upper_words = [w.upper() for w in words]
print(upper_words)  # ['HELLO', 'WORLD', 'PYTHON']

# 使用 if-else
labels = ['偶' if x % 2 == 0 else '奇' for x in range(5)]
print(labels)  # ['偶', '奇', '偶', '奇', '偶']
```

### 3.3 多重循环

```python
# 两个 for
pairs = [(x, y) for x in range(3) for y in range(3)]
print(pairs)
# [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2)]

# 笛卡尔积
colors = ['red', 'blue']
sizes = ['S', 'M', 'L']
combinations = [(c, s) for c in colors for s in sizes]
print(combinations)
# [('red','S'),('red','M'),('red','L'),('blue','S'),('blue','M'),('blue','L')]
```

### 3.4 嵌套列表推导式

```python
# 展平二维列表
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [num for row in matrix for num in row]
print(flat)  # [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 矩阵转置
transposed = [[row[i] for row in matrix] for i in range(len(matrix[0]))]
print(transposed)  # [[1, 4, 7], [2, 5, 8], [3, 6, 9]]

# 等价于 zip(*matrix)
transposed = [list(col) for col in zip(*matrix)]
```

### 3.5 其他推导式

```python
# 字典推导式
squares_dict = {x: x**2 for x in range(5)}
print(squares_dict)  # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# 集合推导式
unique_chars = {ch for ch in "hello world"}
print(unique_chars)  # {'h', 'e', 'l', 'o', ' ', 'w', 'r', 'd'}

# 生成器表达式（用圆括号，返回生成器）
squares_gen = (x**2 for x in range(5))
print(squares_gen)  # <generator object>
print(list(squares_gen))  # [0, 1, 4, 9, 16]
```

### 3.6 推导式 vs 循环

```python
# 推导式（推荐，简洁高效）
result = [x**2 for x in range(10) if x % 2 == 0]

# 传统循环（冗长）
result = []
for x in range(10):
    if x % 2 == 0:
        result.append(x**2)
```

> **原则**：代码越少越好，越简单越好。1 行能实现的功能，不写 5 行。

---

## 4. 生成器（Generator）

### 4.1 为什么需要生成器

列表推导式会一次性生成所有元素，占用内存。生成器**边循环边计算**，节省内存，适合处理大数据。

### 4.2 生成器表达式

```python
# 列表推导式：一次性创建，占用内存
squares_list = [x**2 for x in range(1000000)]

# 生成器表达式：惰性计算，节省内存
squares_gen = (x**2 for x in range(1000000))

# 逐个获取
print(next(squares_gen))  # 0
print(next(squares_gen))  # 1
print(next(squares_gen))  # 4

# 遍历
for val in (x**2 for x in range(5)):
    print(val)  # 0, 1, 4, 9, 16
```

### 4.3 生成器函数：yield

使用 `yield` 关键字定义生成器函数：

```python
def fib(max):
    """生成斐波那契数列"""
    a, b = 0, 1
    while a < max:
        yield a      # 返回值并暂停
        a, b = b, a + b

# 使用
for n in fib(100):
    print(n, end=' ')  # 0 1 1 2 3 5 8 13 21 34 55 89

# 手动调用 next()
g = fib(10)
print(next(g))  # 0
print(next(g))  # 1
print(next(g))  # 1
```

**yield 执行流程**：
1. 调用生成器函数，返回生成器对象（不执行函数体）
2. `next()` 触发执行，遇到 `yield` 暂停并返回值
3. 再次 `next()` 从上次暂停处继续执行
4. 函数结束时抛出 `StopIteration`

### 4.4 生成器示例

```python
# 读取大文件
def read_large_file(file_path, chunk_size=1024):
    """分块读取大文件"""
    with open(file_path, 'r') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

# 生成无限序列
def natural_numbers(start=1):
    """生成自然数序列"""
    n = start
    while True:
        yield n
        n += 1

# 取前 10 个
nums = natural_numbers()
first_ten = [next(nums) for _ in range(10)]
print(first_ten)  # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# 杨辉三角
def pascal_triangle(n):
    row = [1]
    for _ in range(n):
        yield row
        row = [1] + [row[i] + row[i+1] for i in range(len(row)-1)] + [1]

for row in pascal_triangle(5):
    print(row)
# [1]
# [1, 1]
# [1, 2, 1]
# [1, 3, 3, 1]
# [1, 4, 6, 4, 1]
```

### 4.5 生成器的方法

```python
def counter():
    n = 0
    while True:
        received = yield n    # yield 可以接收值
        if received is not None:
            n = received
        else:
            n += 1

g = counter()
print(next(g))        # 0，启动生成器
print(next(g))        # 1
print(g.send(10))     # 10，发送值并继续
print(next(g))        # 11

# close() 关闭生成器
g.close()
# next(g)  # 抛出 StopIteration
```

---

## 5. 迭代器（Iterator）

### 5.1 可迭代对象 vs 迭代器

| 概念 | 说明 | 判断方法 |
|------|------|----------|
| Iterable | 可迭代对象，能用于 for 循环 | `isinstance(x, Iterable)` |
| Iterator | 迭代器，实现了 `__next__()` | `isinstance(x, Iterator)` |

```python
from collections.abc import Iterable, Iterator

# 可迭代对象
lst = [1, 2, 3]
print(isinstance(lst, Iterable))   # True
print(isinstance(lst, Iterator))   # False，list 不是迭代器

# 迭代器
it = iter(lst)
print(isinstance(it, Iterator))    # True
print(next(it))  # 1
print(next(it))  # 2
print(next(it))  # 3
# next(it)  # StopIteration
```

### 5.2 iter() 与 next()

```python
# iter()：将可迭代对象转为迭代器
s = "Hello"
it = iter(s)
print(next(it))  # 'H'
print(next(it))  # 'e'

# for 循环的本质
for ch in "Hello":
    print(ch)
# 等价于：
it = iter("Hello")
while True:
    try:
        ch = next(it)
        print(ch)
    except StopIteration:
        break
```

### 5.3 自定义迭代器

实现 `__iter__()` 和 `__next__()` 方法：

```python
class CountDown:
    """倒计时迭代器"""
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self  # 返回迭代器对象本身

    def __next__(self):
        if self.current <= 0:
            raise StopIteration  # 结束迭代
        self.current -= 1
        return self.current + 1

# 使用
for n in CountDown(5):
    print(n)  # 5, 4, 3, 2, 1
```

### 5.4 生成器 vs 迭代器

```python
# 生成器是一种特殊的迭代器，自动实现了 __iter__ 和 __next__
def my_range(start, end):
    n = start
    while n < end:
        yield n
        n += 1

g = my_range(1, 4)
print(isinstance(g, Iterator))  # True
for n in g:
    print(n)  # 1, 2, 3
```

| 特性 | 迭代器（类实现） | 生成器（yield） |
|------|------------------|-----------------|
| 实现方式 | 定义 `__iter__` 和 `__next__` | 使用 `yield` 关键字 |
| 代码量 | 较多 | 简洁 |
| 状态保存 | 手动管理 | 自动 |
| 适用场景 | 复杂迭代逻辑 | 简单序列生成 |

---

## 6. 综合应用示例

### 6.1 扁平化嵌套列表

```python
def flatten(nested):
    """递归展平任意深度的嵌套列表"""
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

nested = [1, [2, [3, 4], 5], 6, [7, 8]]
print(flatten(nested))  # [1, 2, 3, 4, 5, 6, 7, 8]

# 生成器版本（惰性计算）
def flatten_gen(nested):
    for item in nested:
        if isinstance(item, list):
            yield from flatten_gen(item)
        else:
            yield item

print(list(flatten_gen(nested)))  # [1, 2, 3, 4, 5, 6, 7, 8]
```

### 6.2 数据处理管道

```python
def read_lines(filename):
    """读取文件每一行"""
    with open(filename) as f:
        yield from f

def strip_lines(lines):
    """去除空白"""
    for line in lines:
        yield line.strip()

def filter_empty(lines):
    """过滤空行"""
    for line in lines:
        if line:
            yield line

def parse_csv(lines):
    """解析 CSV"""
    for line in lines:
        yield line.split(',')

# 组合管道
pipeline = parse_csv(filter_empty(strip_lines(read_lines('data.csv'))))
for row in pipeline:
    print(row)
```

### 6.3 滑动窗口

```python
from collections import deque

def sliding_window(iterable, n):
    """滑动窗口迭代器"""
    it = iter(iterable)
    window = deque(itertools.islice(it, n), maxlen=n)
    if len(window) == n:
        yield tuple(window)
    for item in it:
        window.append(item)
        yield tuple(window)

# 求移动平均
import itertools
data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
for window in sliding_window(data, 3):
    avg = sum(window) / len(window)
    print(f"{window} -> 平均: {avg:.2f}")
```

---

## 7. 小结

### 7.1 核心要点

- **切片** `[start:stop:step]`：简洁地获取序列片段
- **迭代**：`for` 循环可遍历任何可迭代对象
- **列表推导式** `[expr for x in iterable if cond]`：简洁创建列表
- **生成器** `yield`：惰性计算，节省内存
- **迭代器**：实现 `__iter__` 和 `__next__` 的对象
- **原则**：代码越少越好，越简单越好

### 7.2 性能对比

| 方式 | 内存 | 速度 | 适用场景 |
|------|------|------|----------|
| 列表推导式 | 高（全加载） | 快 | 小数据 |
| 生成器表达式 | 低（惰性） | 略慢 | 大数据 |
| 生成器函数 | 低 | 灵活 | 复杂逻辑 |

### 7.3 速查表

```python
# 切片
L[start:stop:step]   # 通用切片
L[::-1]              # 反转
L[::2]               # 每隔一个

# 推导式
[expr for x in iter if cond]       # 列表
{key: val for ...}                 # 字典
{expr for ...}                     # 集合
(expr for ...)                     # 生成器

# 迭代工具
enumerate(iter, start)             # 带索引
zip(iter1, iter2)                  # 并行
itertools.chain(*iters)            # 链接
itertools.permutations(iter, r)    # 排列
itertools.combinations(iter, r)    # 组合

# 生成器
def gen():
    yield value
next(gen())                        # 获取下一个值
```
