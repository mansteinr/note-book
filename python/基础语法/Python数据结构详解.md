# Python 数据结构详解

## 1. list 列表

### 1.1 什么是 list

`list` 是 Python 内置的**有序、可变**集合，可以随时添加和删除元素。

```python
# 创建 list
fruits = ['apple', 'banana', 'cherry']
numbers = [1, 2, 3, 4, 5]
mixed = ['apple', 123, True]              # 元素类型可不同
nested = [[1, 2], [3, 4], [5, 6]]          # 嵌套列表
empty = []                                  # 空列表

# 使用 list() 创建
nums = list(range(5))                       # [0, 1, 2, 3, 4]
chars = list("Hello")                       # ['H', 'e', 'l', 'l', 'o']
```

### 1.2 访问元素

```python
fruits = ['apple', 'banana', 'cherry', 'date']

# 索引访问（从 0 开始）
print(fruits[0])    # 'apple'
print(fruits[1])    # 'banana'

# 负数索引（从末尾开始）
print(fruits[-1])   # 'date'，最后一个
print(fruits[-2])   # 'cherry'，倒数第二个

# 切片
print(fruits[0:2])  # ['apple', 'banana']
print(fruits[:2])   # ['apple', 'banana']
print(fruits[2:])   # ['cherry', 'date']
print(fruits[:])    # 完整副本
print(fruits[::-1]) # 反转列表

# 获取长度
print(len(fruits))  # 4
```

### 1.3 修改元素

```python
fruits = ['apple', 'banana', 'cherry']

# 修改单个元素
fruits[0] = 'apricot'
print(fruits)  # ['apricot', 'banana', 'cherry']

# 修改多个元素（切片赋值）
fruits[1:3] = ['blueberry', 'coconut']
print(fruits)  # ['apricot', 'blueberry', 'coconut']
```

### 1.4 添加元素

```python
fruits = ['apple', 'banana']

# append：末尾添加
fruits.append('cherry')
print(fruits)  # ['apple', 'banana', 'cherry']

# insert：指定位置插入
fruits.insert(1, 'avocado')
print(fruits)  # ['apple', 'avocado', 'banana', 'cherry']

# extend：合并另一个列表
fruits.extend(['date', 'elderberry'])
print(fruits)  # ['apple', 'avocado', 'banana', 'cherry', 'date', 'elderberry']

# 使用 + 合并（返回新列表）
new_list = [1, 2] + [3, 4]
print(new_list)  # [1, 2, 3, 4]
```

### 1.5 删除元素

```python
fruits = ['apple', 'banana', 'cherry', 'banana', 'date']

# pop：删除并返回指定位置元素（默认末尾）
removed = fruits.pop()       # 'date'
removed = fruits.pop(1)      # 'banana'

# remove：删除第一个匹配的值
fruits.remove('banana')      # 删除第一个 'banana'

# del 语句
del fruits[0]

# clear：清空列表
fruits.clear()
```

### 1.6 常用方法

```python
nums = [3, 1, 4, 1, 5, 9, 2, 6]

# 排序
nums.sort()              # 原地排序：[1, 1, 2, 3, 4, 5, 6, 9]
nums.sort(reverse=True)  # 降序：[9, 6, 5, 4, 3, 2, 1, 1]

# 按自定义规则排序
students = [('Alice', 85), ('Bob', 92), ('Charlie', 78)]
students.sort(key=lambda x: x[1], reverse=True)
# [('Bob', 92), ('Alice', 85), ('Charlie', 78)]

# sorted：返回新列表，不修改原列表
sorted_nums = sorted(nums)

# 反转
nums.reverse()           # 原地反转
reversed_nums = list(reversed(nums))  # 返回新列表

# 统计
nums = [1, 2, 2, 3, 3, 3]
print(nums.count(3))     # 3，出现次数
print(nums.index(2))     # 1，首次出现的索引

# 查找
print(3 in nums)         # True
print(5 not in nums)     # True
```

---

## 2. tuple 元组

### 2.1 什么是 tuple

`tuple` 是**有序、不可变**的集合，一旦创建不能修改。

```python
# 创建 tuple
t1 = (1, 2, 3)
t2 = ('apple', 'banana', 'cherry')
t3 = ()                    # 空元组
t4 = (1,)                  # 单元素元组（必须加逗号！）
t5 = 1, 2, 3               # 不加括号也可以

# 使用 tuple() 创建
t6 = tuple([1, 2, 3])      # 从列表转换
t7 = tuple("abc")          # ('a', 'b', 'c')
```

> **注意**：单元素元组必须加逗号 `(1,)`，否则 `(1)` 会被当作数学表达式，结果是整数 `1`。

**不可变性的含义**：tuple 的元素不能增删改，试图修改会直接报错：

```python
t = (1, 2, 3)
# t[0] = 10   # TypeError: 'tuple' object does not support item assignment
# t.append(4) # AttributeError: 'tuple' object has no attribute 'append'

# 注意：若元素本身是可变对象（如 list），该元素内部仍可修改
t2 = (1, [2, 3])
t2[1].append(4)
print(t2)     # (1, [2, 3, 4])  —— 元组"指向"的对象没变，变的是对象内部
```

### 2.2 访问与操作

```python
t = ('a', 'b', 'c', 'd', 'e')

# 索引访问
print(t[0])    # 'a'
print(t[-1])   # 'e'

# 切片
print(t[1:3])  # ('b', 'c')

# 长度
print(len(t))  # 5

# 拼接与重复
print((1, 2) + (3, 4))   # (1, 2, 3, 4)
print((1, 2) * 3)        # (1, 2, 1, 2, 1, 2)

# 解包
a, b, c = (1, 2, 3)
print(a, b, c)  # 1 2 3

# 扩展解包
first, *rest = (1, 2, 3, 4, 5)
print(first)    # 1
print(rest)     # [2, 3, 4, 5]
```

### 2.3 tuple 的"可变"陷阱

tuple 本身不可变，但如果元素是可变对象（如 list），该对象内容可变：

```python
t = ('a', 'b', ['A', 'B'])

# t[0] = 'x'      # 报错！tuple 不可变
t[2][0] = 'X'      # 可以！修改的是 list 内容
t[2][1] = 'Y'
print(t)           # ('a', 'b', ['X', 'Y'])
```

**理解**：tuple 的"不可变"是指**每个元素的指向不变**，而非元素内容不变。

### 2.4 list 与 tuple 对比

| 特性 | list | tuple |
|------|------|-------|
| 可变性 | 可变 | 不可变 |
| 语法 | `[1, 2]` | `(1, 2)` |
| 方法 | 多（append等） | 少（count, index） |
| 性能 | 稍慢 | 稍快（创建快、内存小） |
| 安全性 | 可被修改 | 更安全 |
| 用途 | 可变数据 | 常量、字典键、函数多返回值 |

> **建议**：能用 tuple 就用 tuple，代码更安全。

---

## 3. dict 字典

### 3.1 什么是 dict

`dict` 是**键值对（key-value）**的无序（Python 3.7+ 保持插入顺序）集合，通过键快速查找值。

```python
# 创建 dict
student = {
    'name': '张三',
    'age': 20,
    'score': 95.5
}

# 使用 dict() 创建
d1 = dict(name='Alice', age=25)
d2 = dict([('name', 'Bob'), ('age', 30)])
d3 = dict.fromkeys(['a', 'b', 'c'], 0)  # {'a': 0, 'b': 0, 'c': 0}

# 空字典
empty = {}
```

### 3.2 访问元素

```python
student = {'name': '张三', 'age': 20, 'score': 95.5}

# 通过键访问
print(student['name'])           # '张三'
# print(student['gender'])       # KeyError！键不存在

# 使用 get()：安全访问
print(student.get('gender'))         # None，键不存在返回 None
print(student.get('gender', '未设置'))  # '未设置'，指定默认值

# 判断键是否存在
print('name' in student)         # True
print('gender' not in student)   # True

# 获取所有键、值、键值对
print(student.keys())    # dict_keys(['name', 'age', 'score'])
print(student.values())  # dict_values(['张三', 20, 95.5])
print(student.items())   # dict_items([('name', '张三'), ...])
```

### 3.3 修改与添加

```python
student = {'name': '张三', 'age': 20}

# 添加/修改键值对
student['score'] = 95      # 添加
student['age'] = 21        # 修改

# update：合并另一个字典
student.update({'gender': '男', 'class': '三年二班'})

# setdefault：键不存在时设置默认值
student.setdefault('grade', 'A')   # 添加 'grade': 'A'
student.setdefault('grade', 'B')   # 已存在，不修改
```

### 3.4 删除元素

```python
student = {'name': '张三', 'age': 20, 'score': 95}

# pop：删除并返回值
score = student.pop('score')   # 95

# del 语句
del student['age']

# popitem：删除并返回最后一个键值对（Python 3.7+）
last = student.popitem()

# clear：清空
student.clear()
```

### 3.5 遍历字典

```python
student = {'name': '张三', 'age': 20, 'score': 95}

# 遍历键
for key in student:
    print(key)

# 遍历键值对（推荐）
for key, value in student.items():
    print(f"{key}: {value}")

# 遍历值
for value in student.values():
    print(value)
```

### 3.6 字典推导式

```python
# 基本推导式
squares = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# 带条件
even_squares = {x: x**2 for x in range(10) if x % 2 == 0}
# {0: 0, 2: 4, 4: 16, 6: 36, 8: 64}

# 字典键值互换
original = {'a': 1, 'b': 2, 'c': 3}
swapped = {v: k for k, v in original.items()}
# {1: 'a', 2: 'b', 3: 'c'}
```

### 3.7 字典的特性

- **键必须不可变**：可用 `str`、`int`、`tuple`，不能用 `list`、`dict`、`set`
- **键唯一**：重复赋值会覆盖
- **查找速度快**：基于哈希表，时间复杂度接近 O(1)

```python
# 错误：list 不能作为键
# d = {[1, 2]: 'value'}  # TypeError

# 正确：tuple 可以作为键
d = {(1, 2): '坐标', 'name': '张三'}
```

---

## 4. set 集合

### 4.1 什么是 set

`set` 是一组**无序、不重复**的元素集合，主要用于去重和集合运算。

```python
# 创建 set
s1 = {1, 2, 3, 4, 5}
s2 = set([1, 2, 2, 3, 3, 3])  # {1, 2, 3}，自动去重
s3 = set()                     # 空集合（注意：{} 是空字典！）

# 从字符串创建
s4 = set("hello")              # {'h', 'e', 'l', 'o'}
```

> **注意**：创建空集合必须用 `set()`，`{}` 创建的是空字典。

### 4.2 添加与删除

```python
s = {1, 2, 3}

# 添加
s.add(4)          # {1, 2, 3, 4}
s.add(2)          # 已存在，无变化

# update：添加多个元素
s.update([5, 6])  # {1, 2, 3, 4, 5, 6}
s.update({7, 8}, [9])

# 删除
s.remove(9)       # 删除指定元素，不存在则报错
s.discard(100)    # 删除指定元素，不存在不报错
removed = s.pop() # 随机删除并返回一个元素
s.clear()         # 清空
```

### 4.3 集合运算

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

# 交集
print(a & b)             # {3, 4}
print(a.intersection(b)) # {3, 4}

# 并集
print(a | b)          # {1, 2, 3, 4, 5, 6}
print(a.union(b))     # {1, 2, 3, 4, 5, 6}

# 差集（a 有但 b 没有）
print(a - b)              # {1, 2}
print(a.difference(b))    # {1, 2}

# 对称差集（只在 a 或只在 b 中）
print(a ^ b)                       # {1, 2, 5, 6}
print(a.symmetric_difference(b))   # {1, 2, 5, 6}

# 子集与超集
c = {1, 2}
print(c.issubset(a))     # True，c 是 a 的子集
print(a.issuperset(c))   # True，a 是 c 的超集
print(a.isdisjoint(b))   # False，是否有交集
```

### 4.4 frozenset 不可变集合

```python
# frozenset：不可变的 set，可作为字典键
fs = frozenset([1, 2, 3])
# fs.add(4)  # 报错！不可变

d = {fs: 'value'}  # 可以作为键
```

### 4.5 set 的应用场景

```python
# 1. 列表去重
numbers = [1, 2, 2, 3, 3, 3, 4]
unique = list(set(numbers))         # 顺序可能变化
unique_ordered = list(dict.fromkeys(numbers))  # 保持顺序

# 2. 判断元素是否存在（set 比 list 快）
valid_users = {'alice', 'bob', 'charlie'}  # 大数据集时优势明显
if 'alice' in valid_users:
    print("有效用户")

# 3. 找出两个列表的差异
old = {1, 2, 3, 4}
new = {3, 4, 5, 6}
added = new - old      # {5, 6}，新增
removed = old - new    # {1, 2}，删除
```

---

## 5. 数据结构对比与选择

### 5.1 四种数据结构对比

| 特性 | list | tuple | dict | set |
|------|------|-------|------|-----|
| 有序 | ✅ | ✅ | ❌（3.7+有序） | ❌ |
| 可变 | ✅ | ❌ | ✅ | ✅ |
| 重复元素 | ✅ | ✅ | 键不可重复 | ❌ |
| 索引访问 | ✅ | ✅ | ❌（用键） | ❌ |
| 查找速度 | 慢(O(n)) | 慢(O(n)) | 快(O(1)) | 快(O(1)) |
| 语法 | `[]` | `()` | `{k:v}` | `{}` |

### 5.2 选择建议

```
需要存储数据 →
├── 有序、可变 → list
├── 有序、不可变 → tuple
├── 键值对 → dict
└── 去重/集合运算 → set
```

### 5.3 可变与不可变总结

| 类型 | 可变性 | 元素要求 |
|------|--------|----------|
| list | 可变 | 任意类型 |
| tuple | 不可变 | 任意类型（但元素指向不变） |
| dict | 可变 | 键必须不可变 |
| set | 可变 | 元素必须不可变 |
| frozenset | 不可变 | 元素必须不可变 |

---

## 6. 综合应用示例

### 6.1 学生成绩管理

```python
# 使用 dict + list 管理学生信息
students = [
    {'name': '张三', 'scores': {'语文': 85, '数学': 92, '英语': 78}},
    {'name': '李四', 'scores': {'语文': 90, '数学': 88, '英语': 95}},
    {'name': '王五', 'scores': {'语文': 72, '数学': 95, '英语': 80}},
]

# 计算每个学生的平均分
for student in students:
    scores = student['scores']
    avg = sum(scores.values()) / len(scores)
    student['average'] = round(avg, 2)

# 按平均分排序
students.sort(key=lambda x: x['average'], reverse=True)

# 输出排名
print("成绩排名：")
for i, student in enumerate(students, 1):
    print(f"第{i}名：{student['name']}，平均分 {student['average']}")
```

### 6.2 统计单词频率

```python
text = "the quick brown fox jumps over the lazy dog the fox"
words = text.split()

# 方法1：使用 dict
word_count = {}
for word in words:
    word_count[word] = word_count.get(word, 0) + 1

# 方法2：使用 collections.Counter（推荐）
from collections import Counter
word_count = Counter(words)

# 输出前3个高频词
for word, count in word_count.most_common(3):
    print(f"{word}: {count}次")
```

### 6.3 矩阵操作

```python
# 使用嵌套 list 表示矩阵
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]

# 访问元素
print(matrix[1][2])  # 6，第2行第3列

# 矩阵转置
transposed = [[row[i] for row in matrix] for i in range(len(matrix[0]))]
# [[1, 4, 7], [2, 5, 8], [3, 6, 9]]

# 使用 zip 转置（更简洁）
transposed = list(zip(*matrix))
# [(1, 4, 7), (2, 5, 8), (3, 6, 9)]
```

---

## 7. 小结

### 7.1 核心要点

- **list**：有序可变，最常用的数据结构
- **tuple**：有序不可变，更安全，可用于多返回值和字典键
- **dict**：键值对，查找快 O(1)，键必须不可变
- **set**：无序不重复，用于去重和集合运算
- **优先使用内置数据结构**，避免过度依赖 NumPy 等第三方库

### 7.2 常用方法速查

```python
# list
lst.append(x)        # 末尾添加
lst.insert(i, x)     # 指定位置插入
lst.pop(i)           # 删除并返回
lst.remove(x)        # 删除指定值
lst.sort()           # 排序
lst.reverse()        # 反转
len(lst)             # 长度

# dict
d[key]               # 访问
d.get(key, default)  # 安全访问
d[key] = value       # 添加/修改
d.pop(key)           # 删除
d.update(other)      # 合并
d.keys() / values() / items()

# set
s.add(x)             # 添加
s.remove(x) / discard(x)  # 删除
s1 & s2              # 交集
s1 | s2              # 并集
s1 - s2              # 差集
```

### 7.3 性能对比

| 操作 | list | dict / set |
|------|------|-----------|
| 按索引/键访问 | O(1) | O(1) |
| 按值查找 | O(n) | O(1) |
| 添加元素 | O(1)（末尾） | O(1) |
| 删除元素 | O(n) | O(1) |

> **大数据查找场景**：优先使用 `set` 或 `dict`，避免 `list` 的 `in` 操作。
