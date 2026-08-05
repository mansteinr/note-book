# Python 函数式编程详解

## 1. 函数式编程概述

### 1.1 什么是函数式编程

函数式编程（Functional Programming）是一种编程范式，它将计算视为数学函数的求值，避免状态改变和可变数据。

**核心思想**：
- 函数是一等公民（可赋值、传递、返回）
- 纯函数：相同输入永远产生相同输出，无副作用
- 避免可变状态和副作用

### 1.2 Python 中的函数式编程

Python 不是纯函数式语言，但支持函数式编程特性：

- 函数是一等对象
- 支持高阶函数（map、filter、reduce）
- 支持 lambda 匿名函数
- 支持闭包和装饰器
- 支持偏函数

```python
# 函数是一等对象
def greet(name):
    return f"Hello, {name}"

# 赋值给变量
say_hello = greet
print(say_hello("Alice"))  # Hello, Alice

# 作为参数传递
def apply(func, value):
    return func(value)

print(apply(greet, "Bob"))  # Hello, Bob

# 作为返回值
def make_greeter(greeting):
    def greeter(name):
        return f"{greeting}, {name}"
    return greeter

hi = make_greeter("Hi")
print(hi("Charlie"))  # Hi, Charlie
```

---

## 2. 高阶函数

高阶函数是接受函数作为参数，或返回函数的函数。

### 2.1 map()

对可迭代对象的每个元素应用函数：

```python
# 语法：map(function, iterable)
nums = [1, 2, 3, 4, 5]

# 使用 lambda
squared = list(map(lambda x: x**2, nums))
print(squared)  # [1, 4, 9, 16, 25]

# 使用具名函数
def to_upper(s):
    return s.upper()

words = ['hello', 'world']
result = list(map(to_upper, words))
print(result)  # ['HELLO', 'WORLD']

# 多个可迭代对象
a = [1, 2, 3]
b = [10, 20, 30]
sums = list(map(lambda x, y: x + y, a, b))
print(sums)  # [11, 22, 33]

# 等价列表推导式（更 Pythonic）
squared = [x**2 for x in nums]
```

### 2.2 filter()

过滤可迭代对象，保留满足条件的元素：

```python
# 语法：filter(function, iterable)
nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# 过滤偶数
evens = list(filter(lambda x: x % 2 == 0, nums))
print(evens)  # [2, 4, 6, 8, 10]

# 过滤非空字符串
words = ['', 'hello', '', 'world', None]
non_empty = list(filter(None, words))  # None 表示过滤假值
print(non_empty)  # ['hello', 'world']

# 过滤满足复杂条件的元素
users = [
    {'name': 'Alice', 'age': 25},
    {'name': 'Bob', 'age': 17},
    {'name': 'Charlie', 'age': 30},
    {'name': 'David', 'age': 15},
]
adults = list(filter(lambda u: u['age'] >= 18, users))
print(adults)

# 等价列表推导式
adults = [u for u in users if u['age'] >= 18]
```

### 2.3 reduce()

对元素进行累积操作，最终得到一个值：

```python
from functools import reduce

# 语法：reduce(function, iterable[, initial])
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

# 找最大值
maximum = reduce(lambda x, y: x if x > y else y, nums)
print(maximum)  # 5

# 实用示例：将二维列表展平
nested = [[1, 2], [3, 4], [5, 6]]
flat = reduce(lambda x, y: x + y, nested, [])
print(flat)  # [1, 2, 3, 4, 5, 6]
```

### 2.4 sorted() 自定义排序

```python
# 按绝对值排序
nums = [-5, 3, -2, 8, -1]
sorted_nums = sorted(nums, key=abs)
print(sorted_nums)  # [-1, -2, 3, -5, 8]

# 按字符串长度排序
words = ['banana', 'apple', 'cherry', 'date']
sorted_words = sorted(words, key=len)
print(sorted_words)  # ['date', 'apple', 'banana', 'cherry']

# 多字段排序
students = [
    {'name': 'Alice', 'grade': 'A', 'age': 20},
    {'name': 'Bob', 'grade': 'B', 'age': 22},
    {'name': 'Charlie', 'grade': 'A', 'age': 19},
]
# 先按 grade，再按 age
sorted_students = sorted(students, key=lambda x: (x['grade'], x['age']))

# 使用 operator 模块（更高效）
from operator import itemgetter, attrgetter
sorted_students = sorted(students, key=itemgetter('grade', 'age'))
```

### 2.5 高阶函数对比

```python
# map/filter/reduce vs 列表推导式
nums = range(1, 11)

# 函数式风格
result = list(
    map(lambda x: x**2,
        filter(lambda x: x % 2 == 0, nums))
)
# [4, 16, 36, 64, 100]

# 列表推导式（推荐，更易读）
result = [x**2 for x in nums if x % 2 == 0]
# [4, 16, 36, 64, 100]
```

> **建议**：简单场景用列表推导式，复杂逻辑用高阶函数。

---

## 3. 匿名函数（Lambda）

### 3.1 基本语法

```python
# 语法：lambda 参数: 表达式
add = lambda x, y: x + y
print(add(3, 5))  # 8

square = lambda x: x**2
print(square(5))  # 25

# 无参数
get_pi = lambda: 3.14159
print(get_pi())  # 3.14159

# 默认参数
greet = lambda name, greeting="Hello": f"{greeting}, {name}"
print(greet("Alice"))           # Hello, Alice
print(greet("Bob", "Hi"))       # Hi, Bob
```

### 3.2 使用场景

```python
# 1. 排序的 key
students = [('Alice', 85), ('Bob', 92), ('Charlie', 78)]
students.sort(key=lambda x: x[1])

# 2. map/filter 的函数
nums = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, nums))

# 3. 字典排序
d = {'apple': 5, 'banana': 2, 'cherry': 8}
sorted_d = dict(sorted(d.items(), key=lambda x: x[1]))

# 4. 按多个字段排序
data = [(1, 'b'), (2, 'a'), (1, 'a')]
sorted_data = sorted(data, key=lambda x: (x[0], x[1]))
# [(1, 'a'), (1, 'b'), (2, 'a')]
```

### 3.3 lambda 的限制

```python
# lambda 只能包含单个表达式，不能有语句
# 以下都是错误的：
# lambda x: if x > 0: return x  # 语法错误

# 复杂逻辑应该用具名函数
def classify(x):
    if x > 0:
        return "正数"
    elif x < 0:
        return "负数"
    else:
        return "零"

# lambda 中可以使用条件表达式
classify_lambda = lambda x: "正" if x > 0 else ("负" if x < 0 else "零")
```

### 3.4 lambda 与闭包的陷阱

```python
# 陷阱：在循环中创建 lambda
funcs = []
for i in range(3):
    funcs.append(lambda: i)

print([f() for f in funcs])  # [2, 2, 2]，都是 2！

# 原因：lambda 捕获的是变量 i 的引用，循环结束时 i=2

# 解决方法1：使用默认参数
funcs = [lambda i=i: i for i in range(3)]
print([f() for f in funcs])  # [0, 1, 2]

# 解决方法2：使用 functools.partial
from functools import partial
funcs = [partial(lambda x: x, i) for i in range(3)]
print([f() for f in funcs])  # [0, 1, 2]
```

---

## 4. 闭包（Closure）

### 4.1 什么是闭包

闭包是引用了自由变量的函数，即使外部函数已返回，被引用的变量仍然可用。

```python
def make_counter():
    count = 0  # 自由变量

    def counter():
        nonlocal count
        count += 1
        return count

    return counter  # 返回内部函数

c = make_counter()
print(c())  # 1
print(c())  # 2
print(c())  # 3

# 每次调用 make_counter 创建独立的闭包
c2 = make_counter()
print(c2())  # 1，独立计数
```

### 4.2 闭包的应用

```python
# 1. 工厂函数
def make_multiplier(factor):
    def multiply(x):
        return x * factor
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5))   # 10
print(triple(5))   # 15

# 2. 记忆化（缓存）
def memoize(func):
    cache = {}
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper

@memoize
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

print(fib(50))  # 快速计算

# 3. 配置生成器
def make_formatter(prefix, suffix):
    def format(text):
        return f"{prefix}{text}{suffix}"
    return format

html_tag = make_formatter("<b>", "</b>")
print(html_tag("Hello"))  # <b>Hello</b>
```

### 4.3 闭包 vs 类

```python
# 闭包实现计数器
def make_counter_closure():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

# 类实现计数器
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1
        return self.count

# 使用对比
c1 = make_counter_closure()
print(c1(), c1(), c1())  # 1 2 3

c2 = Counter()
print(c2.increment(), c2.increment(), c2.increment())  # 1 2 3
```

---

## 5. 装饰器（Decorator）

### 5.1 什么是装饰器

装饰器是一种在**不修改原函数**的前提下，扩展函数功能的技术。本质是接受函数作为参数并返回新函数的高阶函数。

### 5.2 基本装饰器

```python
def log(func):
    """简单的日志装饰器"""
    def wrapper(*args, **kwargs):
        print(f"调用 {func.__name__}()")
        result = func(*args, **kwargs)
        print(f"{func.__name__}() 执行完毕")
        return result
    return wrapper

@log
def greet(name):
    """打招呼函数"""
    print(f"Hello, {name}")

greet("Alice")
# 输出：
# 调用 greet()
# Hello, Alice
# greet() 执行完毕

# @log 等价于：greet = log(greet)
```

### 5.3 带参数的装饰器

```python
def repeat(times):
    """重复执行装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(times):
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    return decorator

@repeat(3)
def say_hi(name):
    print(f"Hi, {name}")
    return name

say_hi("Alice")
# 打印3次 Hi, Alice
```

### 5.4 使用 functools.wraps 保留元信息

```python
from functools import wraps

def log(func):
    @wraps(func)  # 保留原函数的 __name__, __doc__ 等
    def wrapper(*args, **kwargs):
        """包装函数"""
        print(f"调用 {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log
def greet(name):
    """打招呼"""
    return f"Hello, {name}"

print(greet.__name__)  # greet（没有 @wraps 会是 wrapper）
print(greet.__doc__)   # 打招呼
```

### 5.5 常用装饰器示例

#### 计时装饰器

```python
import time

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} 耗时 {elapsed:.4f}秒")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "完成"

slow_function()  # slow_function 耗时 1.0012秒
```

#### 缓存装饰器

```python
def cache(func):
    """简单的缓存装饰器"""
    cached = {}
    @wraps(func)
    def wrapper(*args):
        if args not in cached:
            cached[args] = func(*args)
        return cached[args]
    return wrapper

# Python 内置缓存装饰器
from functools import lru_cache

@lru_cache(maxsize=128)
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

print(fib(100))  # 快速计算
```

#### 权限校验装饰器

```python
def require_login(func):
    @wraps(func)
    def wrapper(user, *args, **kwargs):
        if not user.get('is_login'):
            raise PermissionError("请先登录")
        return func(user, *args, **kwargs)
    return wrapper

@require_login
def view_profile(user):
    return f"用户：{user['name']}"

user = {'name': 'Alice', 'is_login': True}
print(view_profile(user))  # 用户：Alice
```

#### 重试装饰器

```python
import random

def retry(times=3, delay=1):
    """失败重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == times - 1:
                        raise
                    print(f"第{attempt+1}次失败：{e}，{delay}秒后重试")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(times=3, delay=0.5)
def unstable_api():
    if random.random() < 0.7:
        raise ConnectionError("网络错误")
    return "成功"
```

### 5.6 类装饰器

```python
# 类作为装饰器
class Counter:
    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"{self.func.__name__} 被调用 {self.count} 次")
        return self.func(*args, **kwargs)

@Counter
def greet(name):
    return f"Hello, {name}"

greet("Alice")  # greet 被调用 1 次
greet("Bob")    # greet 被调用 2 次
```

### 5.7 多个装饰器叠加

```python
def bold(func):
    def wrapper():
        return f"<b>{func()}</b>"
    return wrapper

def italic(func):
    def wrapper():
        return f"<i>{func()}</i>"
    return wrapper

@bold
@italic
def hello():
    return "Hello"

print(hello())  # <b><i>Hello</i></b>

# 执行顺序：从下往上装饰，从上往下执行
# 等价于：hello = bold(italic(hello))
```

---

## 6. 偏函数（Partial）

### 6.1 什么是偏函数

偏函数是固定原函数的部分参数，生成一个新函数。

```python
from functools import partial

# 基本用法
def power(base, exponent):
    return base ** exponent

# 固定 exponent 参数
square = partial(power, exponent=2)
cube = partial(power, exponent=3)

print(square(5))  # 25
print(cube(3))    # 27
```

### 6.2 实用示例

```python
# 1. 简化 int 的进制转换
int2 = partial(int, base=2)    # 二进制
int8 = partial(int, base=8)    # 八进制
int16 = partial(int, base=16)  # 十六进制

print(int2('1010'))    # 10
print(int16('FF'))     # 255

# 2. 创建特定日志器
import logging
error_log = partial(logging.log, logging.ERROR)
error_log("发生错误")

# 3. 简化 print
debug_print = partial(print, "[DEBUG]")
debug_print("启动服务")  # [DEBUG] 启动服务

# 4. 绑定方法参数
def connect(host, port, timeout=30):
    return f"连接 {host}:{port}（超时{timeout}秒）"

connect_default = partial(connect, host='localhost', port=8080)
print(connect_default())  # 连接 localhost:8080（超时30秒）
print(connect_default(timeout=10))  # 连接 localhost:8080（超时10秒）
```

### 6.3 偏函数 vs lambda

```python
# 偏函数
square = partial(pow, exp=2)

# lambda
square = lambda x: pow(x, 2)

# 两者等价，偏函数更适合固定已有函数的参数
```

---

## 7. 函数式编程工具

### 7.1 functools 模块

```python
from functools import (
    lru_cache,      # 缓存装饰器
    wraps,          # 保留函数元信息
    partial,        # 偏函数
    reduce,         # 归约
    cmp_to_key,     # 比较函数转 key 函数
    total_ordering, # 自动补充比较方法
)

# cmp_to_key：将旧式比较函数转为 key
def compare(a, b):
    if len(a) < len(b):
        return -1
    elif len(a) > len(b):
        return 1
    return 0

words = ['apple', 'kiwi', 'banana']
sorted_words = sorted(words, key=cmp_to_key(compare))
print(sorted_words)  # ['kiwi', 'apple', 'banana']
```

### 7.2 itertools 模块

```python
from itertools import (
    chain,          # 链接迭代器
    groupby,        # 分组
    accumulate,     # 累积
    takewhile,      # 取到条件不满足
    dropwhile,      # 丢弃到条件不满足
    starmap,        # 解包参数后调用
)

# accumulate：累积计算
import itertools
nums = [1, 2, 3, 4, 5]
print(list(itertools.accumulate(nums)))           # [1, 3, 6, 10, 15]
print(list(itertools.accumulate(nums, lambda x, y: x * y)))  # [1, 2, 6, 24, 120]

# groupby：分组（需先排序）
data = [('A', 1), ('A', 2), ('B', 3), ('B', 4)]
for key, group in itertools.groupby(data, key=lambda x: x[0]):
    print(f"{key}: {list(group)}")
# A: [('A', 1), ('A', 2)]
# B: [('B', 3), ('B', 4)]

# chain：链接多个迭代器
for x in itertools.chain([1, 2], [3, 4], [5]):
    print(x)  # 1, 2, 3, 4, 5

# takewhile / dropwhile
nums = [1, 2, 3, 4, 5, 1, 2]
print(list(itertools.takewhile(lambda x: x < 4, nums)))  # [1, 2, 3]
print(list(itertools.dropwhile(lambda x: x < 4, nums)))  # [4, 5, 1, 2]
```

### 7.3 operator 模块

```python
import operator

# 算术运算
print(operator.add(3, 5))      # 8
print(operator.sub(10, 3))     # 7
print(operator.mul(3, 4))      # 12
print(operator.truediv(10, 3)) # 3.33...

# 比较运算
print(operator.lt(3, 5))       # True，小于
print(operator.eq(3, 3))       # True，等于

# 取属性/元素
itemgetter_0_1 = operator.itemgetter(0, 1)
print(itemgetter_0_1([10, 20, 30]))  # (10, 20)

attrgetter_name = operator.attrgetter('name')
# 用于对象排序：sorted(objs, key=attrgetter_name)
```

---

## 8. 综合应用示例

### 8.1 函数式数据处理

```python
# 模拟 MapReduce
from functools import reduce

sales = [
    {'product': '苹果', 'amount': 100, 'qty': 5},
    {'product': '香蕉', 'amount': 50, 'qty': 10},
    {'product': '苹果', 'amount': 80, 'qty': 4},
    {'product': '橙子', 'amount': 120, 'qty': 6},
    {'product': '香蕉', 'amount': 60, 'qty': 8},
]

# 计算总销售额
total = reduce(
    lambda acc, s: acc + s['amount'],
    sales,
    0
)
print(f"总销售额：{total}")  # 410

# 按产品分组求和
from itertools import groupby
sorted_sales = sorted(sales, key=lambda x: x['product'])
product_totals = {
    product: reduce(lambda a, s: a + s['amount'], group, 0)
    for product, group in groupby(sorted_sales, key=lambda x: x['product'])
}
print(product_totals)  # {'苹果': 180, '橙子': 120, '香蕉': 110}
```

### 8.2 装饰器组合

```python
def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] 调用 {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"[TIMER] {func.__name__} 耗时 {time.time()-start:.4f}s")
        return result
    return wrapper

def cache(func):
    cached = {}
    @wraps(func)
    def wrapper(*args):
        if args not in cached:
            cached[args] = func(*args)
        return cached[args]
    return wrapper

@log
@timer
@cache
def expensive_computation(n):
    time.sleep(1)
    return n ** 2

expensive_computation(5)
# [LOG] 调用 expensive_computation
# [TIMER] expensive_computation 耗时 1.0012s
```

---

## 9. 小结

### 9.1 核心要点

- **函数是一等对象**：可赋值、传递、返回
- **高阶函数**：`map`、`filter`、`reduce`、`sorted`
- **lambda**：简洁的匿名函数，适合简单场景
- **闭包**：函数引用外部变量，即使外部已返回
- **装饰器**：不修改原函数扩展功能，用 `@` 语法
- **偏函数**：固定部分参数生成新函数
- **优先使用列表推导式**：比 `map`/`filter` 更 Pythonic

### 9.2 装饰器速查

```python
# 基本装饰器
def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 前置处理
        result = func(*args, **kwargs)
        # 后置处理
        return result
    return wrapper

# 带参数的装饰器
def decorator_with_args(arg):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### 9.3 最佳实践

1. **简单过滤/映射用列表推导式**，复杂逻辑用高阶函数
2. **装饰器务必使用 `@wraps`** 保留元信息
3. **避免在 lambda 中写复杂逻辑**，用具名函数
4. **注意闭包中的变量捕获**，循环中使用默认参数
5. **合理使用缓存**，但注意缓存失效问题
