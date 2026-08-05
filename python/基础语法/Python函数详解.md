# Python 函数详解

## 1. 函数基础

### 1.1 为什么需要函数

函数是最基本的代码抽象方式。当代码出现有规律的重复时，应该将其封装为函数：

- **减少重复代码**：写一次，调用多次
- **提高可读性**：函数名表达意图，代码更清晰
- **便于维护**：修改逻辑只需改一处
- **代码复用**：可在不同程序中调用

### 1.2 调用内置函数

Python 内置了许多常用函数：

```python
# 数学相关
print(abs(-5))          # 5，绝对值
print(max(1, 2, 3))     # 3，最大值
print(min(1, 2, 3))     # 1，最小值
print(sum([1, 2, 3]))   # 6，求和
print(pow(2, 10))       # 1024，幂运算
print(round(3.14159, 2))# 3.14，四舍五入

# 类型转换
print(int("123"))       # 123
print(float("3.14"))    # 3.14
print(str(100))         # "100"
print(bool(0))          # False
print(list("abc"))      # ['a', 'b', 'c']

# 序列相关
print(len("hello"))     # 5，长度
print(range(5))         # range(0, 5)
print(sorted([3, 1, 2]))# [1, 2, 3]
print(reversed([1, 2, 3]))  # 反转迭代器

# 查看函数帮助
help(len)
```

### 1.3 数据类型转换函数

```python
# int()
print(int("123"))       # 字符串 → 整数：123
print(int(3.99))        # 浮点数 → 整数：3（截断）
print(int("ff", 16))    # 16进制字符串 → 整数：255

# float()
print(float("3.14"))    # 3.14
print(float(5))         # 5.0

# str()
print(str(123))         # "123"
print(str([1, 2]))      # "[1, 2]"

# bool()
print(bool(""))         # False
print(bool([0]))        # True（非空列表）
print(bool(None))       # False
```

---

## 2. 定义函数

### 2.1 基本语法

```python
def function_name(parameters):
    """文档字符串（docstring）"""
    # 函数体
    return result
```

**示例**：

```python
def greet(name):
    """向指定的人打招呼"""
    return f"Hello, {name}!"

# 调用函数
message = greet("Alice")
print(message)  # Hello, Alice!
```

### 2.2 空函数

```python
# 使用 pass 占位（还没想好怎么实现）
def not_implemented():
    pass

# 也可以用 ... 
def todo():
    ...
```

### 2.3 返回值

```python
# 返回单个值
def square(x):
    return x * x

# 返回多个值（本质是返回 tuple）
def min_max(numbers):
    return min(numbers), max(numbers)

result = min_max([3, 1, 4, 1, 5])
print(result)       # (1, 5)
smallest, largest = min_max([3, 1, 4, 1, 5])  # 解包
print(smallest, largest)  # 1 5

# 无返回值（返回 None）
def print_info(name):
    print(f"Name: {name}")
    # 隐式 return None

result = print_info("Alice")  # 打印 Name: Alice
print(result)                  # None
```

### 2.4 函数文档

```python
def calculate_bmi(weight, height):
    """
    计算 BMI 指数

    参数：
        weight: 体重（千克）
        height: 身高（米）

    返回：
        BMI 值（保留1位小数）

    示例：
        >>> calculate_bmi(70, 1.75)
        22.9
    """
    bmi = weight / (height ** 2)
    return round(bmi, 1)

# 查看文档
help(calculate_bmi)
print(calculate_bmi.__doc__)
```

---

## 3. 函数参数

Python 函数参数非常灵活，支持多种参数类型。

### 3.1 位置参数

```python
def power(x, n):
    """计算 x 的 n 次方"""
    return x ** n

# 按位置传递
print(power(2, 3))   # 8，x=2, n=3
print(power(3, 2))   # 9，x=3, n=2
```

### 3.2 默认参数

```python
def power(x, n=2):
    """n 默认为 2，计算平方"""
    return x ** n

print(power(5))      # 25，使用默认 n=2
print(power(5, 3))   # 125，指定 n=3
```

> **注意**：默认参数必须放在必选参数之后。

**默认参数的陷阱**：

```python
# 错误：使用可变对象作为默认参数
def add_item(item, lst=[]):
    lst.append(item)
    return lst

print(add_item(1))  # [1]
print(add_item(2))  # [1, 2]  ← 默认参数被修改了！

# 正确：使用 None 作为默认值
def add_item(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst

print(add_item(1))  # [1]
print(add_item(2))  # [2]
```

### 3.3 可变参数（*args）

允许传入任意数量的参数，函数内接收为 tuple：

```python
def calculate_sum(*numbers):
    """计算任意数量数字的和"""
    total = 0
    for n in numbers:
        total += n
    return total

print(calculate_sum(1, 2, 3))        # 6
print(calculate_sum(1, 2, 3, 4, 5))  # 15
print(calculate_sum())               # 0

# 传入 list 或 tuple 时，用 * 解包
nums = [1, 2, 3, 4]
print(calculate_sum(*nums))          # 10
```

### 3.4 关键字参数（**kwargs）

允许传入任意数量的键值对，函数内接收为 dict：

```python
def print_info(name, **kwargs):
    """打印用户信息"""
    print(f"姓名：{name}")
    for key, value in kwargs.items():
        print(f"{key}：{value}")

print_info("张三", age=25, city="北京", job="工程师")

# 传入 dict 时，用 ** 解包
info = {'age': 25, 'city': '北京'}
print_info("李四", **info)
```

### 3.5 命名关键字参数

限制关键字参数的名称，用 `*` 分隔：

```python
def create_user(name, age, *, city, job):
    """city 和 job 必须用关键字传递"""
    print(f"{name}, {age}岁, {city}, {job}")

# 正确
create_user("张三", 25, city="北京", job="工程师")

# 错误：city 和 job 不能用位置传递
# create_user("张三", 25, "北京", "工程师")  # TypeError
```

### 3.6 参数组合

参数定义顺序：**位置参数 → 默认参数 → 可变参数 → 命名关键字参数 → 关键字参数**

```python
def func(a, b=10, *args, c, d=20, **kwargs):
    """
    a: 必选位置参数
    b: 默认参数
    *args: 可变参数
    c: 命名关键字参数（必传）
    d: 命名关键字参数（带默认值）
    **kwargs: 关键字参数
    """
    print(f"a={a}, b={b}")
    print(f"args={args}")
    print(f"c={c}, d={d}")
    print(f"kwargs={kwargs}")

func(1, 2, 3, 4, c=5, e=6)
# a=1, b=2
# args=(3, 4)
# c=5, d=20
# kwargs={'e': 6}
```

### 3.7 参数类型提示（Python 3.5+）

```python
def greet(name: str, times: int = 1) -> str:
    """带类型提示的函数"""
    return (f"Hello, {name}! " * times).strip()

from typing import List, Optional

def process_items(items: List[int], factor: Optional[int] = None) -> List[int]:
    if factor is None:
        factor = 2
    return [item * factor for item in items]
```

---

## 4. 递归函数

### 4.1 什么是递归

函数在内部调用自身，称为递归。递归需要满足两个条件：

1. **基线条件**：不再递归，直接返回结果
2. **递归条件**：问题分解为更小的子问题

### 4.2 经典示例：阶乘

```python
def factorial(n):
    """计算 n 的阶乘：n! = n × (n-1) × ... × 1"""
    if n <= 1:           # 基线条件
        return 1
    return n * factorial(n - 1)  # 递归条件

print(factorial(5))  # 120 = 5 × 4 × 3 × 2 × 1
```

**递归执行过程**：
```
factorial(5)
→ 5 * factorial(4)
→ 5 * (4 * factorial(3))
→ 5 * (4 * (3 * factorial(2)))
→ 5 * (4 * (3 * (2 * factorial(1))))
→ 5 * (4 * (3 * (2 * 1)))
→ 5 * (4 * (3 * 2))
→ 5 * (4 * 6)
→ 5 * 24
→ 120
```

### 4.3 斐波那契数列

```python
# 基础递归（效率低，有重复计算）
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

# 优化：使用缓存
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_cached(n):
    if n <= 1:
        return n
    return fib_cached(n - 1) + fib_cached(n - 2)

print(fib_cached(50))  # 快速计算
```

### 4.4 递归 vs 迭代

```python
# 递归实现
def sum_recursive(n):
    if n == 1:
        return 1
    return n + sum_recursive(n - 1)

# 迭代实现（推荐）
def sum_iterative(n):
    total = 0
    for i in range(1, n + 1):
        total += i
    return total

# 数学公式（最优）
def sum_formula(n):
    return n * (n + 1) // 2
```

### 4.5 递归的注意事项

- **栈溢出**：递归深度过大时会栈溢出（默认限制约 1000 层）
- **效率问题**：递归可能有重复计算，可用缓存优化
- **尾递归优化**：Python 不支持尾递归优化

```python
import sys
print(sys.getrecursionlimit())  # 查看递归深度限制
sys.setrecursionlimit(2000)     # 修改限制（不推荐）
```

---

## 5. 变量作用域

### 5.1 LEGB 规则

Python 查找变量的顺序：**L → E → G → B**

| 层级 | 名称 | 说明 |
|------|------|------|
| L | Local | 函数内局部作用域 |
| E | Enclosing | 外层嵌套函数作用域 |
| G | Global | 模块全局作用域 |
| B | Built-in | 内置作用域 |

```python
x = "global"  # 全局变量

def outer():
    x = "enclosing"  # 外层函数变量

    def inner():
        x = "local"  # 局部变量
        print(x)     # local

    inner()
    print(x)         # enclosing

outer()
print(x)             # global
```

### 5.2 global 关键字

在函数内修改全局变量：

```python
count = 0

def increment():
    global count  # 声明使用全局变量
    count += 1

increment()
increment()
print(count)  # 2
```

### 5.3 nonlocal 关键字

在嵌套函数中修改外层函数变量：

```python
def make_counter():
    count = 0

    def counter():
        nonlocal count  # 声明使用外层变量
        count += 1
        return count

    return counter

c = make_counter()
print(c())  # 1
print(c())  # 2
print(c())  # 3
```

---

## 6. 高级函数特性

### 6.1 匿名函数（Lambda）

```python
# 语法：lambda 参数: 表达式
square = lambda x: x ** 2
print(square(5))  # 25

add = lambda x, y: x + y
print(add(3, 4))  # 7

# 常用于排序、过滤等
students = [('Alice', 85), ('Bob', 92), ('Charlie', 78)]
students.sort(key=lambda x: x[1])  # 按成绩排序

# 与 map、filter 配合
nums = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, nums))
evens = list(filter(lambda x: x % 2 == 0, nums))
```

### 6.2 闭包

```python
def make_multiplier(factor):
    """返回一个乘法函数"""
    def multiplier(x):
        return x * factor  # 引用外层变量
    return multiplier

double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))  # 10
print(triple(5))  # 15
```

### 6.3 装饰器基础

```python
def log_execution(func):
    """记录函数执行的装饰器"""
    def wrapper(*args, **kwargs):
        print(f"调用 {func.__name__}，参数：{args}, {kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} 返回：{result}")
        return result
    return wrapper

@log_execution
def add(a, b):
    return a + b

add(3, 5)
# 调用 add，参数：(3, 5), {}
# add 返回：8
```

### 6.4 偏函数

```python
from functools import partial

# 固定部分参数，创建新函数
def power(base, exponent):
    return base ** exponent

# 创建平方和立方函数
square = partial(power, exponent=2)
cube = partial(power, exponent=3)

print(square(5))  # 25
print(cube(3))    # 27

# 实用示例：固定 int 的进制
int2 = partial(int, base=2)   # 二进制转换
print(int2('1010'))  # 10
```

---

## 7. 函数式编程工具

### 7.1 map()

对可迭代对象的每个元素应用函数：

```python
nums = [1, 2, 3, 4, 5]

# map 返回迭代器
squared = list(map(lambda x: x**2, nums))
print(squared)  # [1, 4, 9, 16, 25]

# 等价的列表推导式（推荐）
squared = [x**2 for x in nums]

# 多个可迭代对象
a = [1, 2, 3]
b = [10, 20, 30]
sums = list(map(lambda x, y: x + y, a, b))
print(sums)  # [11, 22, 33]
```

### 7.2 filter()

过滤可迭代对象：

```python
nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# 过滤偶数
evens = list(filter(lambda x: x % 2 == 0, nums))
print(evens)  # [2, 4, 6, 8, 10]

# 等价的列表推导式（推荐）
evens = [x for x in nums if x % 2 == 0]
```

### 7.3 reduce()

对元素进行累积操作：

```python
from functools import reduce

nums = [1, 2, 3, 4, 5]

# 累加
total = reduce(lambda x, y: x + y, nums)
print(total)  # 15

# 累乘
product = reduce(lambda x, y: x * y, nums)
print(product)  # 120

# 带初始值
total = reduce(lambda x, y: x + y, nums, 100)
print(total)  # 115
```

### 7.4 sorted() 自定义排序

```python
students = [
    {'name': 'Alice', 'score': 85},
    {'name': 'Bob', 'score': 92},
    {'name': 'Charlie', 'score': 78},
]

# 按 score 排序
sorted_by_score = sorted(students, key=lambda x: x['score'])
print(sorted_by_score)

# 多字段排序：先按 score 降序，再按 name 升序
sorted_multi = sorted(students, key=lambda x: (-x['score'], x['name']))

# 使用 operator 模块（更高效）
from operator import itemgetter
sorted_students = sorted(students, key=itemgetter('score'))
```

---

## 8. 综合应用示例

### 8.1 通用计算器

```python
def calculator():
    """简单计算器"""
    operations = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y if y != 0 else "除零错误",
    }

    while True:
        expr = input("输入表达式（如 3 + 5），输入 q 退出：").strip()
        if expr.lower() == 'q':
            break
        try:
            x, op, y = expr.split()
            x, y = float(x), float(y)
            if op in operations:
                result = operations[op](x, y)
                print(f"= {result}")
            else:
                print("不支持的运算符")
        except ValueError:
            print("输入格式错误")

calculator()
```

### 8.2 装饰器实现计时

```python
import time
from functools import wraps

def timer(func):
    """计时装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} 执行耗时：{elapsed:.4f}秒")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "完成"

slow_function()  # slow_function 执行耗时：1.0012秒
```

### 8.3 缓存装饰器

```python
def memoize(func):
    """缓存函数结果"""
    cache = {}
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper

@memoize
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(100))  # 快速计算
```

---

## 9. 小结

### 9.1 核心要点

- 函数是代码抽象的基本方式，**减少重复、提高复用**
- Python 函数参数灵活：位置参数、默认参数、可变参数、关键字参数
- **默认参数避免使用可变对象**，用 `None` 代替
- 递归需要**基线条件**和**递归条件**，注意栈溢出
- 变量作用域遵循 **LEGB** 规则
- `global` 修改全局变量，`nonlocal` 修改外层函数变量
- 匿名函数 `lambda` 适合简单的一次性函数
- 装饰器是修改函数行为的优雅方式

### 9.2 参数类型速查

| 参数类型 | 语法 | 说明 |
|----------|------|------|
| 位置参数 | `def f(a, b)` | 按顺序传递 |
| 默认参数 | `def f(a, b=10)` | 可省略，有默认值 |
| 可变参数 | `def f(*args)` | 收集为 tuple |
| 关键字参数 | `def f(**kwargs)` | 收集为 dict |
| 命名关键字 | `def f(*, c)` | 必须用关键字传递 |

### 9.3 最佳实践

1. **函数名见名知意**：`calculate_bmi` 比 `calc` 更清晰
2. **函数单一职责**：一个函数只做一件事
3. **添加文档字符串**：说明参数、返回值、用途
4. **控制函数长度**：建议不超过 50 行
5. **避免过多参数**：超过 5 个考虑用对象封装
6. **优先用列表推导式**：比 `map`/`filter` 更 Pythonic
7. **使用类型提示**：提高代码可读性和 IDE 提示
