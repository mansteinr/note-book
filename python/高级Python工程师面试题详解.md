# 高级 Python 工程师面试题详解

> 本文档系统覆盖高级 Python 工程师面试的**八大核心模块**，每模块按"基础题 → 进阶题 → 高级题"分级，附详细参考答案与解题思路。
> 适合中高级 Python 工程师面试准备，也可作为技术自测与团队考核参考。

---

## 目录

- [一、Python 核心语法](#一python-核心语法)
- [二、Python 高级特性](#二python-高级特性)
- [三、性能优化](#三性能优化)
- [四、并发编程](#四并发编程)
- [五、Web 框架应用](#五web-框架应用)
- [六、数据库设计与优化](#六数据库设计与优化)
- [七、系统架构设计](#七系统架构设计)
- [八、项目经验与工程实践](#八项目经验与工程实践)
- [九、总结](#九总结)

---

## 一、Python 核心语法

### 基础题

#### Q1.1 Python 中 `is` 和 `==` 的区别？

```
==: 比较两个对象的"值"是否相等（调用 __eq__ 方法）
is: 比较两个对象的"身份"是否相同（即 id() 是否相同，是否指向同一内存地址）

示例:
  a = [1, 2, 3]
  b = [1, 2, 3]
  
  a == b  → True   (值相等)
  a is b  → False  (不同对象)

小整数池陷阱:
  a = 256
  b = 256
  a is b  → True   (Python 缓存 -5~256 的整数)
  
  a = 257
  b = 257
  a is b  → False  (超出缓存范围)

面试要点:
  • 比较值用 ==，比较单例（None/True/False）用 is
  • is None 比 == None 更规范（避免 __eq__ 被重载）
  • 小整数池和字符串驻留（interning）是常见追问点
```

#### Q1.2 可变对象与不可变对象的区别？举例说明陷阱。

```
不可变对象（Immutable）:
  • int, float, str, tuple, frozenset, bool
  • 修改会创建新对象
  
可变对象（Mutable）:
  • list, dict, set
  • 修改在原对象上进行

陷阱 1: 函数默认参数
  def append_to(item, lst=[]):   # ❌ 危险
      lst.append(item)
      return lst
  
  print(append_to(1))  → [1]
  print(append_to(2))  → [1, 2]  ← 默认参数只创建一次！
  
  正确写法:
  def append_to(item, lst=None):
      if lst is None:
          lst = []
      lst.append(item)
      return lst

陷阱 2: 闭包捕获
  funcs = []
  for i in range(3):
      funcs.append(lambda: i)
  
  print([f() for f in funcs])  → [2, 2, 2]  ← 都捕获最后的 i
  
  正确写法:
  funcs = [lambda i=i: i for i in range(3)]
  print([f() for f in funcs])  → [0, 1, 2]

陷阱 3: 元组"不可变"的假象
  t = ([1, 2], 3)
  t[0].append(3)
  print(t)  → ([1, 2, 3], 3)  ← 元组里存的是引用，引用本身不变
```

### 进阶题

#### Q1.3 Python 的 GIL 是什么？对多线程有什么影响？

```
GIL (Global Interpreter Lock，全局解释器锁):
  • CPython 解释器的机制
  • 同一时刻只有一个线程执行 Python 字节码
  • 目的: 保护 CPython 内部数据结构（引用计数）的线程安全

影响:
  • CPU 密集型任务: 多线程无法利用多核，甚至比单线程慢
  • I/O 密集型任务: 多线程仍有效（I/O 时释放 GIL）

示例对比:
  # CPU 密集型（多线程无优势）
  def cpu_task():
      s = 0
      for i in range(10**7):
          s += i
  
  单线程:  2.0s
  多线程:  2.1s  ← GIL 限制，无提升
  
  # I/O 密集型（多线程有优势）
  def io_task():
      time.sleep(1)
  
  单线程:  10s   (10 个任务串行)
  多线程:  1s    (10 个任务并发)

应对方案:
  • CPU 密集型 → multiprocessing（多进程）
  • I/O 密集型 → threading / asyncio
  • 计算密集型 C 扩展 → 释放 GIL（如 NumPy）

GIL 的影响范围:
  • 仅 CPython 有 GIL
  • Jython、IronPython 无 GIL
  • Python 3.13+ 实验性支持 No-GIL（PEP 703）
```

#### Q1.4 深拷贝与浅拷贝的区别？如何实现？

```
浅拷贝（Shallow Copy）:
  • 创建新对象，但内部元素是原对象元素的引用
  • 修改内层可变对象会影响原对象

深拷贝（Deep Copy）:
  • 递归复制所有层级，完全独立
  • 修改任何层级都不影响原对象

示例:
  import copy
  
  original = [[1, 2], [3, 4]]
  
  # 浅拷贝
  shallow = copy.copy(original)
  shallow[0].append(99)
  print(original)  → [[1, 2, 99], [3, 4]]  ← 内层被修改
  
  # 深拷贝
  original = [[1, 2], [3, 4]]
  deep = copy.deepcopy(original)
  deep[0].append(99)
  print(original)  → [[1, 2], [3, 4]]  ← 完全独立

实现方式:
  浅拷贝:
    • copy.copy(obj)
    • list.copy()
    • list[:]  /  dict.copy()
    • obj.copy()
  
  深拷贝:
    • copy.deepcopy(obj)

自定义对象的拷贝:
  class MyClass:
      def __copy__(self):
          # 浅拷贝逻辑
          ...
      def __deepcopy__(self, memo):
          # 深拷贝逻辑
          ...
```

### 高级题

#### Q1.5 Python 的方法解析顺序（MRO）是什么？C3 线性化如何工作？

```
MRO (Method Resolution Order):
  • 多继承时，方法查找的顺序
  • Python 3 使用 C3 线性化算法

查看 MRO:
  class A: pass
  class B(A): pass
  class C(A): pass
  class D(B, C): pass
  
  print(D.__mro__)
  → (D, B, C, A, object)

C3 线性化规则:
  • 子类在父类之前
  • 多继承按声明顺序
  • 满足"局部顺序优先"和"单调性"

菱形继承示例:
       A
      / \
     B   C
      \ /
       D
  
  MRO(D) = D → B → C → A → object
  
  • D 最先（子类优先）
  • B 在 C 前（声明顺序）
  • A 在 object 前（继承关系）
  • A 只出现一次（避免重复）

为什么不用深度优先/广度优先?
  • 深度优先: 可能跳过父类，违反局部顺序
  • 广度优先: 可能破坏继承层次
  • C3: 保证单调性（不会出现前后矛盾）

经典面试陷阱:
  class X: pass
  class Y: pass
  class A(X, Y): pass
  class B(Y, X): pass
  class C(A, B): pass  # ❌ TypeError: 无法创建一致的 MRO
  
  原因:
    A 的 MRO: A → X → Y
    B 的 MRO: B → Y → X
    C 继承 A, B，但 A 要求 X 在 Y 前，B 要求 Y 在 X 前
    → 矛盾，C3 无法线性化
```

---

## 二、Python 高级特性

### 基础题

#### Q2.1 装饰器的原理是什么？写一个带参数的装饰器。

```
装饰器本质:
  • 接收函数作为参数，返回新函数（或类）
  • 语法糖 @decorator 等价于 func = decorator(func)

简单装饰器:
  def log(func):
      def wrapper(*args, **kwargs):
          print(f"调用 {func.__name__}")
          result = func(*args, **kwargs)
          print(f"结束 {func.__name__}")
          return result
      return wrapper
  
  @log
  def hello():
      print("Hello!")
  
  hello()
  # 输出:
  # 调用 hello
  # Hello!
  # 结束 hello

带参数的装饰器:
  def repeat(times):
      def decorator(func):
          def wrapper(*args, **kwargs):
              for _ in range(times):
                  result = func(*args, **kwargs)
              return result
          return wrapper
      return decorator
  
  @repeat(3)
  def greet(name):
      print(f"Hi {name}")
  
  greet("Alice")  # 打印 3 次

保留元信息（functools.wraps）:
  from functools import wraps
  
  def log(func):
      @wraps(func)  # 保留原函数的 __name__, __doc__ 等
      def wrapper(*args, **kwargs):
          return func(*args, **kwargs)
      return wrapper

类装饰器:
  class CountCalls:
      def __init__(self, func):
          self.func = func
          self.count = 0
      
      def __call__(self, *args, **kwargs):
          self.count += 1
          print(f"第 {self.count} 次调用")
          return self.func(*args, **kwargs)
  
  @CountCalls
  def say_hi():
      print("Hi!")
```

#### Q2.2 生成器与迭代器的区别？生成器的应用场景。

```
迭代器（Iterator）:
  • 实现了 __iter__ 和 __next__ 的对象
  • 惰性计算，节省内存

生成器（Generator）:
  • 一种特殊的迭代器
  • 用 yield 关键字定义
  • 自动实现迭代器协议

区别:
  ┌──────────┬──────────────────┬──────────────────┐
  │          │   迭代器          │   生成器          │
  ├──────────┼──────────────────┼──────────────────┤
  │ 实现方式  │ 类 + __iter/next │ 函数 + yield     │
  │ 代码量    │ 较多             │ 简洁             │
  │ 状态管理  │ 手动             │ 自动             │
  └──────────┴──────────────────┴──────────────────┘

生成器示例:
  def fib():
      a, b = 0, 1
      while True:
          yield a
          a, b = b, a + b
  
  f = fib()
  print([next(f) for _ in range(10)])
  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

应用场景:
  1. 处理大文件（避免全部读入内存）
     def read_large_file(path):
         with open(path) as f:
             for line in f:
                 yield line.strip()
  
  2. 无限序列
     def counter():
         i = 0
         while True:
             yield i
             i += 1
  
  3. 流式数据处理
     def process_stream(stream):
         for chunk in stream:
             data = parse(chunk)
             if data:
                 yield data

生成器表达式（省内存）:
  # 列表推导（一次性生成）
  squares_list = [x**2 for x in range(10**6)]  # 占用内存
  
  # 生成器表达式（惰性）
  squares_gen = (x**2 for x in range(10**6))   # 几乎不占内存
  
  sum(squares_gen)  # 逐个计算求和

yield from（委托生成器）:
  def sub_gen():
      yield 1
      yield 2
      yield 3
  
  def main_gen():
      yield 0
      yield from sub_gen()  # 委托给子生成器
      yield 4
  
  list(main_gen())  → [0, 1, 2, 3, 4]
```

### 进阶题

#### Q2.3 上下文管理器的实现方式？写一个自定义上下文管理器。

```
方式 1: 类实现（__enter__ / __exit__）

  class FileManager:
      def __init__(self, filename, mode):
          self.filename = filename
          self.mode = mode
          self.file = None
      
      def __enter__(self):
          self.file = open(self.filename, self.mode)
          return self.file
      
      def __exit__(self, exc_type, exc_val, exc_tb):
          if self.file:
              self.file.close()
          # 返回 True 则吞掉异常，返回 False/None 则抛出
          if exc_type:
              print(f"捕获异常: {exc_val}")
          return True  # 吞掉异常
  
  with FileManager('test.txt', 'w') as f:
      f.write('Hello')

方式 2: contextlib.contextmanager 装饰器

  from contextlib import contextmanager
  
  @contextmanager
  def timer():
      import time
      start = time.time()
      try:
          yield  # yield 之前相当于 __enter__，之后相当于 __exit__
      finally:
          duration = time.time() - start
          print(f"耗时: {duration:.2f}s")
  
  with timer():
      # 业务代码
      sum(range(10**6))

方式 3: contextlib suppress（忽略指定异常）

  from contextlib import suppress
  
  with suppress(FileNotFoundError):
      os.remove('nonexistent.txt')  # 不会抛异常

应用场景:
  • 文件/连接管理（自动关闭）
  • 锁的获取与释放
  • 事务管理
  • 资源清理
  • 计时/日志
```

#### Q2.4 元类（Metaclass）的作用？何时使用？

```
元类 = "类的类"
  • type 是所有类的元类
  • 元类控制类的创建行为

普通类创建:
  class MyClass: pass
  # 等价于: MyClass = type('MyClass', (), {})

自定义元类:
  class SingletonMeta(type):
      _instances = {}
      
      def __call__(cls, *args, **kwargs):
          if cls not in cls._instances:
              cls._instances[cls] = super().__call__(*args, **kwargs)
          return cls._instances[cls]
  
  class Database(metaclass=SingletonMeta):
      def __init__(self):
          print("初始化数据库连接")
  
  db1 = Database()  # 初始化
  db2 = Database()  # 不再初始化（返回同一实例）
  print(db1 is db2)  → True

元类的应用场景:
  1. 单例模式
  2. ORM 框架（Django Models、SQLAlchemy）
  3. 插件系统（自动注册）
  4. 接口/抽象类强制
  5. 自动添加方法/属性

Django Model 示例:
  class User(models.Model):
      name = models.CharField(max_length=100)
      # 元类自动将 name 字段注册到 _meta.fields
  
  User.objects.filter(name='Alice')  # 由元类生成

何时使用元类?
  ✅ 框架级开发（ORM、DI 容器）
  ✅ 需要控制类的创建逻辑
  ✅ 需要自动修改类属性
  ❌ 普通业务代码（过度设计）
  
  "Metaclasses are deeper magic than 99% of users should ever worry about."
  — Tim Peters
```

### 高级题

#### Q2.5 描述 Python 的内存管理机制。

```
Python 内存管理三大机制:

1. 引用计数（Reference Counting）
   • 每个对象有引用计数
   • 引用 +1，删除 -1
   • 归零时立即回收
   
   import sys
   a = [1, 2, 3]
   print(sys.getrefcount(a))  # 2 (a 本身 + getrefcount 的参数)
   
   b = a
   print(sys.getrefcount(a))  # 3
   
   del b
   print(sys.getrefcount(a))  # 2
   
   优点: 实时回收，简单高效
   缺点: 无法处理循环引用

2. 标记清除（Mark and Sweep）— 解决循环引用
   • 专门处理容器对象（list, dict, 自定义对象等）
   • 从根对象出发，标记可达对象
   • 清除不可达对象
   
   循环引用示例:
   a = []
   b = [a]
   a.append(b)
   del a, b
   # 引用计数都不为 0，但已无外部引用
   # → 标记清除可识别并回收

3. 分代回收（Generational Collection）
   • 新对象 → 第 0 代
   • 经历 GC 存活 → 升级到第 1 代、第 2 代
   • 越老的代，扫描频率越低
   • 基于"越新越易失效"的假设
   
   import gc
   print(gc.get_threshold())  # (700, 10, 10)
   # 第 0 代分配 700 次触发，第 0 代 10 次触发第 1 代...

内存池机制（pymalloc）:
   • 小对象（≤512B）使用内存池，减少系统调用
   • 大对象直接 malloc
   • arena → pool → block 三级结构

内存优化技巧:
   • 使用 __slots__ 减少实例内存
   • 生成器替代列表
   • 及时 del 大对象
   • 使用 weakref 弱引用
```

---

## 三、性能优化

### 基础题

#### Q3.1 如何定位 Python 程序的性能瓶颈？

```
工具链:

1. timeit（微基准测试）
   import timeit
   timeit.timeit('sum(range(1000))', number=10000)

2. cProfile（函数级性能分析）
   import cProfile
   cProfile.run('my_function()')
   
   输出:
   ncalls  tottime  percall  cumtime  filename:lineno(function)
   1       2.5      2.5      2.5      my_module.py:10(slow_func)

3. line_profiler（行级性能分析）
   from line_profiler import LineProfiler
   lp = LineProfiler()
   lp_wrapper = lp(my_function)
   lp_wrapper()
   lp.print_stats()
   
   输出每行的执行时间

4. memory_profiler（内存分析）
   from memory_profiler import profile
   
   @profile
   def my_func():
       a = [1] * (10 ** 6)
       return a

5. py-spy（采样式分析，无需改代码）
   py-spy record -o profile.svg -- python my_script.py
   生成火焰图

定位流程:
  1. cProfile 找出耗时最多的函数
  2. line_profiler 分析该函数的具体行
  3. 针对热点优化
  4. 重新测试验证
```

#### Q3.2 列举常见的 Python 性能优化技巧。

```
1. 选择合适的数据结构
   • 查找: set/dict O(1) > list O(n)
   
   # ❌ 慢
   if item in my_list: ...    # O(n)
   
   # ✅ 快
   if item in my_set: ...     # O(1)

2. 使用生成器节省内存
   # ❌ 一次性生成
   squares = [x**2 for x in range(10**7)]
   
   # ✅ 惰性计算
   squares = (x**2 for x in range(10**7))

3. 字符串拼接用 join
   # ❌ 慢（每次创建新字符串）
   s = ""
   for word in words:
       s += word
   
   # ✅ 快
   s = "".join(words)

4. 列表推导优于 for 循环
   # ❌
   result = []
   for i in range(1000):
       result.append(i * 2)
   
   # ✅
   result = [i * 2 for i in range(1000)]

5. 局部变量优于全局变量
   # ❌ 慢（全局查找）
   import math
   def compute():
       return math.sqrt(100)
   
   # ✅ 快（局部查找）
   def compute():
       sqrt = math.sqrt  # 局部引用
       return sqrt(100)

6. 使用内置函数（C 实现）
   # ❌
   total = 0
   for x in numbers:
       total += x
   
   # ✅
   total = sum(numbers)  # C 实现，快 5~10 倍

7. 使用 __slots__
   class Point:
       __slots__ = ['x', 'y']  # 禁用 __dict__，省内存
       def __init__(self, x, y):
           self.x = x
           self.y = y

8. 延迟导入
   def rarely_used():
       import heavy_module  # 仅在需要时导入
       ...

9. 使用 collections 优化
   from collections import deque, Counter, defaultdict
   
   # 频繁头部操作用 deque
   q = deque([1, 2, 3])
   q.appendleft(0)  # O(1)，list 是 O(n)

10. 多进程处理 CPU 密集任务
    from multiprocessing import Pool
    with Pool(4) as p:
        results = p.map(heavy_func, data)
```

### 进阶题

#### Q3.3 如何优化 Python 的内存占用？

```
1. __slots__ 优化对象
   # 普通: 每个实例有 __dict__，占内存
   class Point:
       def __init__(self, x, y):
           self.x = x
           self.y = y
   # 100 万个实例 ≈ 150 MB
   
   # __slots__: 禁用 __dict__
   class Point:
       __slots__ = ['x', 'y']
   # 100 万个实例 ≈ 56 MB（节省 60%+）

2. 使用生成器
   # ❌ 一次加载全部
   def read_all(path):
       with open(path) as f:
           return f.readlines()  # 全部读入内存
   
   # ✅ 逐行读取
   def read_lines(path):
       with open(path) as f:
           for line in f:
               yield line

3. 选择紧凑的数据结构
   # ❌ 列表存对象
   points = [Point(1,2), Point(3,4), ...]  # 每个对象有开销
   
   # ✅ NumPy 数组
   import numpy as np
   points = np.array([[1,2], [3,4], ...])  # 紧凑存储

4. 字符串驻留（interning）
   # 频繁使用的字符串驻留
   import sys
   s = sys.intern("very_long_string_repeated_many_times")

5. 使用 array 替代 list（同类型数据）
   import array
   # list: 每个元素是指针，开销大
   nums_list = [1, 2, 3, 4, 5]
   
   # array: 紧凑存储
   nums_array = array.array('i', [1, 2, 3, 4, 5])  # C int 存储

6. 弱引用（避免强引用导致无法回收）
   import weakref
   cache = weakref.WeakValueDictionary()
   # 当外部引用消失时，缓存自动清理

7. 及时释放大对象
   data = load_huge_data()
   result = process(data)
   del data  # 立即释放，不等作用域结束
```

#### Q3.4 Cython 和 ctypes 优化原理？何时使用？

```
Cython:
  • Python 的超集，支持静态类型声明
  • 编译为 C 扩展，性能提升 10~100 倍
  • 适合 CPU 密集型计算

示例:
  # slow.py
  def sum_squares(n):
      total = 0
      for i in range(n):
          total += i * i
      return total
  
  # fast.pyx (Cython)
  def sum_squares(int n):
      cdef long total = 0
      cdef int i
      for i in range(n):
          total += i * i
      return total
  
  性能: Python 2.5s → Cython 0.02s（125 倍）

ctypes:
  • 调用 C 共享库（.so / .dll）
  • 无需重写代码，直接调用现有 C 库
  • 适合集成已有 C 代码

示例:
  from ctypes import CDLL, c_double
  
  libm = CDLL('libm.so.6')
  libm.sqrt.restype = c_double
  libm.sqrt.argtypes = [c_double]
  
  print(libm.sqrt(16.0))  # 4.0

何时使用:
  • Cython: Python 代码需要极致性能（数值计算、循环）
  • ctypes: 调用现有 C 库（无需重写）
  • Numba: JIT 编译数值计算（@jit 装饰器，最简单）
  • Rust + PyO3: 现代替代 C 的方案

Numba 示例（最易用）:
  from numba import jit
  
  @jit(nopython=True)
  def sum_squares(n):
      total = 0
      for i in range(n):
          total += i * i
      return total
  # 自动 JIT 编译，接近 C 速度
```

### 高级题

#### Q3.5 解释 Python 的字节码执行过程，如何优化？

```
Python 执行流程:

  源码 (.py)
      │
      ▼
  词法分析 + 语法分析
      │
      ▼
  AST（抽象语法树）
      │
      ▼
  编译器
      │
      ▼
  字节码 (.pyc)
      │
      ▼
  PVM（Python 虚拟机）逐条执行字节码

查看字节码:
  import dis
  
  def add(a, b):
      return a + b
  
  dis.dis(add)
  # 输出:
  # LOAD_FAST   0 (a)
  # LOAD_FAST   1 (b)
  # BINARY_ADD
  # RETURN_VALUE

优化策略:

1. 减少字节码数量
   # 慢
   if a == 1: ...
   elif a == 2: ...
   elif a == 3: ...
   
   # 快（dict 查找是 O(1)，且只有一条字节码）
   handlers = {1: f1, 2: f2, 3: f3}
   handler = handlers.get(a)
   if handler: handler()

2. 利用 .pyc 缓存
   • Python 自动缓存字节码到 __pycache__
   • 避免重复编译
   • 部署时确保 .pyc 可写

3. 使用 PyPy（JIT 编译）
   • PyPy 运行时 JIT 编译热点代码为机器码
   • 平均比 CPython 快 4~5 倍
   • 兼容大部分 Python 代码

4. 使用 mypyc（静态类型编译）
   • mypyc 将带类型注解的 Python 编译为 C 扩展
   • 性能提升 2~10 倍
   • Instagram 在生产环境使用

5. 避免属性访问
   # 慢
   for item in items:
       process(item.x, item.y, item.z)
   
   # 快（解包到局部变量）
   for x, y, z in items:
       process(x, y, z)

6. 内联小函数
   # 频繁调用的小函数可手动内联
   # 或使用 functools.lru_cache 缓存结果
```

---

## 四、并发编程

### 基础题

#### Q4.1 进程、线程、协程的区别？适用场景？

```
┌──────────┬──────────────┬──────────────┬──────────────┐
│          │   进程        │   线程        │   协程        │
├──────────┼──────────────┼──────────────┼──────────────┤
│ 资源     │ 独立内存空间   │ 共享进程内存   │ 共享线程栈    │
│ 创建开销  │ 大（MB 级）   │ 中（KB 级）   │ 小（字节级）  │
│ 切换开销  │ 大            │ 中            │ 小            │
│ 通信     │ IPC（管道/队列）│ 共享内存+锁   │ 同线程内直接  │
│ GIL 影响 │ 无            │ 有            │ 无            │
│ 并发数   │ 数十~数百      │ 数百~数千      │ 数万~数十万    │
│ 适用场景  │ CPU 密集      │ I/O 密集      │ 高并发 I/O    │
└──────────┴──────────────┴──────────────┴──────────────┘

选择决策:
  CPU 密集型（计算）→ multiprocessing
  I/O 密集型（网络/文件）→ threading 或 asyncio
  超高并发 I/O → asyncio（协程）

代码对比:

  # 多进程（CPU 密集）
  from multiprocessing import Pool
  with Pool(4) as p:
      results = p.map(cpu_task, data)
  
  # 多线程（I/O 密集）
  from concurrent.futures import ThreadPoolExecutor
  with ThreadPoolExecutor(10) as ex:
      results = list(ex.map(io_task, data))
  
  # 协程（高并发 I/O）
  import asyncio
  async def main():
      tasks = [async_task(d) for d in data]
      results = await asyncio.gather(*tasks)
```

#### Q4.2 threading 中的锁有哪些？区别是什么？

```
1. Lock（互斥锁）
   • 最基本的锁
   • 一次只允许一个线程访问
   
   lock = threading.Lock()
   with lock:
       shared_resource += 1

2. RLock（可重入锁）
   • 同一线程可多次 acquire，需对应次数 release
   • 避免递归死锁
   
   rlock = threading.RLock()
   def recursive_func():
       with rlock:
           if condition:
               recursive_func()  # 同线程再次获取，不阻塞

3. Semaphore（信号量）
   • 允许 N 个线程同时访问
   • 用于限流
   
   sem = threading.Semaphore(5)  # 最多 5 个并发
   with sem:
       make_api_call()

4. Event（事件）
   • 线程间通知机制
   • 一个线程设置，多个线程等待
   
   event = threading.Event()
   
   def waiter():
       event.wait()  # 阻塞直到 set
       print("收到通知")
   
   event.set()  # 通知所有等待者

5. Condition（条件变量）
   • 结合锁和通知
   • 用于生产者-消费者模式
   
   cond = threading.Condition()
   
   def consumer():
       with cond:
           while queue.empty():
               cond.wait()  # 释放锁并等待
           item = queue.get()
   
   def producer():
       with cond:
           queue.put(item)
           cond.notify()  # 通知一个等待者

6. BoundedSemaphore
   • release 次数不能超过 acquire 次数
   • 防止编程错误

死锁的四个必要条件:
  1. 互斥
  2. 持有并等待
  3. 不可剥夺
  4. 循环等待
  
避免死锁:
  • 按固定顺序获取锁
  • 使用 acquire(timeout=)
  • 使用 with 语法确保释放
```

### 进阶题

#### Q4.3 asyncio 的原理？写一个异步爬虫示例。

```
asyncio 原理:
  • 基于事件循环（Event Loop）
  • 单线程内通过协程切换实现并发
  • I/O 操作时让出控制权，事件循环调度其他协程

核心概念:
  • coroutine: 协程函数（async def）
  • Task: 包装协程，可被调度
  • Future: 底层结果容器
  • Event Loop: 调度器

执行流程:
  1. 协程遇到 await（I/O）→ 让出控制权
  2. 事件循环调度其他就绪协程
  3. I/O 完成后，协程恢复执行

异步爬虫示例:
  import asyncio
  import aiohttp
  
  async def fetch(session, url):
      async with session.get(url) as response:
          return await response.text()
  
  async def crawl(urls):
      async with aiohttp.ClientSession() as session:
          tasks = [fetch(session, url) for url in urls]
          results = await asyncio.gather(*tasks)
          return results
  
  urls = ['http://example.com/1', 'http://example.com/2', ...]
  results = asyncio.run(crawl(urls))

对比同步版本:
  # 同步（串行）
  import requests
  results = [requests.get(url).text for url in urls]
  # 100 个 URL × 1s = 100s
  
  # 异步（并发）
  results = asyncio.run(crawl(urls))
  # 100 个 URL 并发 ≈ 1~2s

asyncio 关键 API:
  • asyncio.run(coro):  运行顶层协程
  • asyncio.gather(*coros):  并发执行多个协程
  • asyncio.create_task(coro):  创建 Task
  • asyncio.wait_for(coro, timeout):  超时控制
  • asyncio.Queue:  异步队列
  • asyncio.Lock/Semaphore:  异步锁/信号量

异步限制并发数:
  sem = asyncio.Semaphore(10)  # 最多 10 并发
  
  async def fetch_limited(session, url):
      async with sem:
          return await fetch(session, url)
```

#### Q4.4 如何实现线程安全的单例模式？

```
方式 1: 模块级单例（最简单）
  # singleton.py
  class _Singleton:
      def __init__(self):
          self.config = {}
  
  instance = _Singleton()  # 模块只加载一次，天然单例
  
  # 使用
  from singleton import instance

方式 2: 装饰器 + 锁
  import threading
  
  def singleton(cls):
      instances = {}
      lock = threading.Lock()
      
      def get_instance(*args, **kwargs):
          if cls not in instances:  # 双重检查
              with lock:
                  if cls not in instances:
                      instances[cls] = cls(*args, **kwargs)
          return instances[cls]
      
      return get_instance
  
  @singleton
  class Database:
      pass

方式 3: 元类
  class SingletonMeta(type):
      _instances = {}
      _lock = threading.Lock()
      
      def __call__(cls, *args, **kwargs):
          if cls not in cls._instances:
              with cls._lock:
                  if cls not in cls._instances:
                      cls._instances[cls] = super().__call__(*args, **kwargs)
          return cls._instances[cls]
  
  class Database(metaclass=SingletonMeta):
      pass

方式 4: __new__ 方法
  class Singleton:
      _instance = None
      _lock = threading.Lock()
      
      def __new__(cls, *args, **kwargs):
          if cls._instance is None:
              with cls._lock:
                  if cls._instance is None:
                      cls._instance = super().__new__(cls)
          return cls._instance

双重检查锁定（Double-Checked Locking）:
  • 第一次检查不加锁（性能）
  • 第二次检查加锁（安全）
  • 避免每次都获取锁的开销
```

### 高级题

#### Q4.5 生产者-消费者模式如何用 Python 实现？对比几种方案。

```
方案 1: threading + Queue（最经典）
  import threading
  import queue
  
  q = queue.Queue(maxsize=10)
  
  def producer():
      for i in range(100):
          q.put(i)  # 队列满时阻塞
      q.put(None)  # 结束信号
  
  def consumer():
      while True:
          item = q.get()  # 队列空时阻塞
          if item is None:
              break
          process(item)
          q.task_done()
  
  t1 = threading.Thread(target=producer)
  t2 = threading.Thread(target=consumer)
  t1.start(); t2.start()
  t1.join(); t2.join()
  
  特点: 线程安全，自动阻塞，适合多线程

方案 2: asyncio + Queue（高并发）
  import asyncio
  
  async def producer(queue):
      for i in range(100):
          await queue.put(i)
          await asyncio.sleep(0.01)
      await queue.put(None)
  
  async def consumer(queue):
      while True:
          item = await queue.get()
          if item is None:
              break
          await process(item)
          queue.task_done()
  
  async def main():
      q = asyncio.Queue(maxsize=10)
      await asyncio.gather(
          producer(q),
          consumer(q)
      )
  
  asyncio.run(main())
  
  特点: 协程级，万级并发，适合 I/O 密集

方案 3: multiprocessing + Queue（多进程）
  from multiprocessing import Process, Queue
  
  def producer(q):
      for i in range(100):
          q.put(i)
  
  def consumer(q):
      while True:
          item = q.get()
          if item is None:
              break
          process(item)
  
  q = Queue(maxsize=10)
  p1 = Process(target=producer, args=(q,))
  p2 = Process(target=consumer, args=(q,))
  p1.start(); p2.start()
  
  特点: 跨进程，避开 GIL，适合 CPU 密集

方案 4: concurrent.futures（高级抽象）
  from concurrent.futures import ThreadPoolExecutor
  
  def process(item):
      return item ** 2
  
  with ThreadPoolExecutor(max_workers=4) as ex:
      futures = [ex.submit(process, item) for item in range(100)]
      results = [f.result() for f in futures]
  
  特点: 简洁，自动管理线程池
```

---

## 五、Web 框架应用

### 基础题

#### Q5.1 Django 和 Flask 的核心区别？如何选择？

```
Django（全栈框架）:
  • "Batteries included"（自带全套）
  • ORM、Admin、Form、Auth、Session 等开箱即用
  • 适合中大型项目，快速开发
  • 约定优于配置

Flask（微框架）:
  • 轻量，核心只含路由和模板
  • 通过扩展添加功能（SQLAlchemy、Login 等）
  • 灵活，适合小型项目或 API 服务
  • 自由组合组件

对比表:
  ┌────────────┬─────────────────┬─────────────────┐
  │            │   Django         │   Flask          │
  ├────────────┼─────────────────┼─────────────────┤
  │ 定位       │ 全栈             │ 微框架           │
  │ ORM        │ 自带 Django ORM  │ 需搭配 SQLAlchemy│
  │ Admin      │ 自带             │ 需扩展           │
  │ 路由       │ MTV 模式         │ 装饰器           │
  │ 模板       │ DTL              │ Jinja2           │
  │ 学习曲线   │ 较陡             │ 平缓             │
  │ 适合       │ 内容/管理后台    │ API/微服务       │
  └────────────┴─────────────────┴─────────────────┘

选择建议:
  • 内容管理/后台系统 → Django
  • RESTful API → Flask + Flask-RESTful 或 Django REST Framework
  • 微服务 → Flask / FastAPI
  • 快速原型 → Flask
  • 团队规范统一 → Django
  
  FastAPI 是现代替代（异步+类型提示+自动文档），适合新项目
```

#### Q5.2 Django ORM 的查询优化有哪些手段？

```
1. select_related（一对一/外键，JOIN 查询）
   # ❌ N+1 查询问题
   for book in Book.objects.all():
       print(book.author.name)  # 每次都查 author
   
   # ✅ 一次 JOIN 查询
   for book in Book.objects.select_related('author'):
       print(book.author.name)

2. prefetch_related（多对多/反向外键，额外查询）
   # ❌ N+1 查询
   for author in Author.objects.all():
       print(author.books.all())  # 每个 author 查一次
   
   # ✅ 两次查询（authors + books）
   for author in Author.objects.prefetch_related('books'):
       print(author.books.all())

3. only / defer（只查需要的字段）
   # 只查 name 和 age
   users = User.objects.only('name', 'age')
   
   # 排除大字段
   articles = Article.objects.defer('content')

4. values / values_list（返回字典/元组，不创建对象）
   # 返回字典
   users = User.objects.values('name', 'age')
   # [{'name': 'Alice', 'age': 25}, ...]
   
   # 返回元组
   names = User.objects.values_list('name', flat=True)
   # ['Alice', 'Bob', ...]

5. bulk_create / bulk_update（批量操作）
   # ❌ 逐条创建
   for item in items:
       Item.objects.create(**item)  # 1000 次 SQL
   
   # ✅ 批量创建
   Item.objects.bulk_create([Item(**item) for item in items])  # 1 次 SQL

6. explain 分析查询
   query = User.objects.filter(age__gt=18)
   print(query.explain())
   # 查看 SQL 执行计划

7. 索引优化
   class User(models.Model):
       email = models.EmailField(db_index=True)  # 单字段索引
       
       class Meta:
           indexes = [
               models.Index(fields=['last_name', 'first_name']),  # 联合索引
           ]

8. count 存在性检查
   # ❌ 加载所有对象
   if User.objects.filter(email=email).exists():
   
   # ✅ 只查是否存在
   if User.objects.filter(email=email).exists():
   
   # ✅ 计数不加载
   count = User.objects.filter(age__gt=18).count()
```

### 进阶题

#### Q5.3 Django 中间件的工作原理？执行顺序？

```
中间件（Middleware）:
  • 请求/响应处理的钩子层
  • 类似"洋葱模型"，层层包裹视图

中间件结构:
  class SimpleMiddleware:
      def __init__(self, get_response):
          self.get_response = get_response
      
      def __call__(self, request):
          # 1. 请求到达视图前的处理
          # ...（请求阶段，从外到内）
          
          response = self.get_response(request)
          
          # 2. 视图返回响应后的处理
          # ...（响应阶段，从内到外）
          
          return response
      
      def process_view(self, request, view_func, args, kwargs):
          # 视图调用前
          pass
      
      def process_exception(self, request, exception):
          # 视图抛异常时
          pass

执行顺序（洋葱模型）:

  请求 → [MW1 → MW2 → MW3] → View → [MW3 → MW2 → MW1] → 响应
  
  MIDDLEWARE = [
      'SecurityMiddleware',        # 1. 请求最先，响应最后
      'SessionMiddleware',         # 2.
      'CommonMiddleware',          # 3.
      'AuthenticationMiddleware',  # 4.
      'MyCustomMiddleware',        # 5. 请求最后，响应最先
  ]
  
  请求阶段: 1 → 2 → 3 → 4 → 5 → View
  响应阶段: View → 5 → 4 → 3 → 2 → 1

应用场景:
  • 认证（检查用户登录）
  • 日志（记录请求/响应）
  • 限流
  • CORS 处理
  • 压缩响应
  • 安全头

自定义中间件示例（API 限流）:
  from django.http import JsonResponse
  from collections import defaultdict
  import time
  
  class RateLimitMiddleware:
      def __init__(self, get_response):
          self.get_response = get_response
          self.requests = defaultdict(list)
      
      def __call__(self, request):
          ip = request.META.get('REMOTE_ADDR')
          now = time.time()
          
          # 清理 1 分钟前的记录
          self.requests[ip] = [t for t in self.requests[ip] if now - t < 60]
          
          # 每分钟最多 60 次
          if len(self.requests[ip]) >= 60:
              return JsonResponse({'error': '请求过于频繁'}, status=429)
          
          self.requests[ip].append(now)
          return self.get_response(request)
```

#### Q5.4 FastAPI 相比 Flask/Django 的优势？

```
FastAPI 特点:
  • 基于 Starlette（异步）+ Pydantic（数据验证）
  • 原生支持 async/await
  • 类型提示驱动文档生成
  • 性能接近 Go/Node.js

优势对比:

  1. 性能
     FastAPI > Flask > Django（异步 I/O 优势）
     
     基准测试（简单 JSON 响应）:
     FastAPI:  ~25000 req/s
     Flask:    ~4000 req/s
     Django:   ~2500 req/s

  2. 异步支持
     # FastAPI 原生异步
     @app.get("/users/{id}")
     async def get_user(id: int):
         user = await db.fetch_user(id)
         return user
     
     # Flask 2.0+ 支持但不够成熟
     # Django 异步支持逐步完善中

  3. 自动文档
     FastAPI 自动生成 OpenAPI/Swagger 文档
     访问 /docs 即可看到交互式 API 文档
     
     # 类型提示 → 自动验证 + 文档
     @app.post("/users")
     async def create_user(user: UserCreate):
         # user 已通过 Pydantic 验证
         ...

  4. 数据验证
     from pydantic import BaseModel
     
     class UserCreate(BaseModel):
         name: str
         email: str
         age: int = Field(ge=0, le=150)
     
     # 自动验证请求体，错误自动返回 422

  5. 依赖注入
     from fastapi import Depends
     
     async def get_db():
         async with get_session() as db:
             yield db
     
     @app.get("/users")
     async def list_users(db = Depends(get_db)):
         return await db.query(User)

何时选 FastAPI:
  ✅ 新项目，重 API，需要高性能
  ✅ 微服务架构
  ✅ 异步 I/O 密集（实时通信、爬虫 API）
  
  何时选 Django:
  ✅ 需要完整后台管理
  ✅ 团队熟悉 Django
  ✅ CMS/内容管理
  
  何时选 Flask:
  ✅ 小型项目
  ✅ 极致灵活
  ✅ 已有 Flask 技术栈
```

### 高级题

#### Q5.5 设计一个高并发的短链系统，技术方案？

```
需求:
  • 长链接 → 短链接
  • 访问短链 → 重定向到长链
  • QPS: 10万+
  • 数据量: 10亿+

架构设计:

  ┌──────────┐     ┌──────────┐     ┌──────────┐
  │  Client   │────→│  Nginx   │────→│  FastAPI │
  │           │←────│  (LB)    │←────│  (API)   │
  └──────────┘     └──────────┘     └────┬─────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
              ┌──────────┐        ┌──────────┐        ┌──────────┐
              │  Redis   │        │  MySQL   │        │  Kafka   │
              │  (缓存)  │        │  (持久化)│        │  (异步)  │
              └──────────┘        └──────────┘        └──────────┘

短码生成方案:
  
  方案 A: 自增 ID + Base62
    • ID: 12345678
    • Base62: "7N42"
    • 优点: 简单，无冲突
    • 缺点: 可预测，需发号器
  
  方案 B: Hash（MD5/MurmurHash）取前 6~7 位
    • 优点: 无需协调
    • 缺点: 可能冲突，需处理
  
  方案 C: 预生成短码池
    • 提前生成一批短码存 Redis
    • 使用时 pop 一个
    • 优点: 高性能，无冲突
    • 推荐方案

数据模型:
  CREATE TABLE url_mapping (
      id BIGINT PRIMARY KEY AUTO_INCREMENT,
      short_code VARCHAR(7) UNIQUE NOT NULL,
      long_url TEXT NOT NULL,
      created_at TIMESTAMP,
      expire_at TIMESTAMP,
      INDEX idx_short_code (short_code)
  );

访问流程:
  1. 用户访问 https://t.co/abc123
  2. Nginx → API
  3. 查 Redis（短码 → 长链）
     - 命中 → 302 重定向
  4. 未命中 → 查 MySQL
     - 命中 → 回填 Redis → 302
  5. 都未命中 → 404

缓存策略:
  • Redis 缓存热点短链（LRU 淘汰）
  • 布隆过滤器快速判断短链是否存在（避免缓存穿透）
  • 缓存空值防止穿透
  • 缓存预热（启动时加载热门短链）

高可用:
  • API 多实例 + 负载均衡
  • Redis 主从 + 哨兵
  • MySQL 读写分离 + 分库分表
  • 短码分片（按首字母分库）

监控:
  • QPS、延迟、错误率
  • 缓存命中率
  • 短链生成速率

扩展:
  • 访问统计（异步写 Kafka → ClickHouse）
  • 防滥用（频控、黑名单）
  • 自定义短链（用户指定）
```

---

## 六、数据库设计与优化

### 基础题

#### Q6.1 MySQL 索引的原理？如何优化索引？

```
索引原理: B+ Tree
  • 平衡多路查找树
  • 叶子节点存储数据，非叶子节点存储索引
  • 叶子节点用链表连接，支持范围查询

 优点:
  • 查询 O(log n)
  • 范围查询高效
  • 排序优化

索引类型:
  1. 主键索引（聚簇索引）
     • 数据按主键顺序存储
     • 一个表只有一个
  
  2. 普通索引
     CREATE INDEX idx_name ON users(name);
  
  3. 唯一索引
     CREATE UNIQUE INDEX idx_email ON users(email);
  
  4. 联合索引
     CREATE INDEX idx_name_age ON users(name, age);
     • 最左前缀原则: (name) ✅, (name, age) ✅, (age) ❌
  
  5. 覆盖索引
     • 索引包含查询所需的所有字段，无需回表
     SELECT name, age FROM users WHERE name = 'Alice';
     • 若 idx_name_age 存在，直接从索引取数据

索引优化原则:
  1. 查询频繁的字段加索引
  2. 区分度高的字段优先（sex 区分度低，不合适）
  3. 联合索引按区分度排序
  4. 避免索引失效:
     • 不在索引列做运算: WHERE age + 1 = 20 ❌
     • 不用函数: WHERE DATE(create_time) = '2024-01-01' ❌
     • 不用 LIKE 左模糊: WHERE name LIKE '%abc' ❌
     • 不用 !=: WHERE status != 1 (可能全表扫描)
  5. 使用 EXPLAIN 分析执行计划
  
     EXPLAIN SELECT * FROM users WHERE email = 'test@test.com';
     
     关注:
     • type: const > eq_ref > ref > range > index > ALL
     • key: 实际使用的索引
     • rows: 预估扫描行数
     • Extra: Using index（覆盖索引，好）

联合索引示例:
  -- 索引 (a, b, c)
  WHERE a = 1              ✅ 用到 a
  WHERE a = 1 AND b = 2    ✅ 用到 a, b
  WHERE a = 1 AND b = 2 AND c = 3  ✅ 用到 a, b, c
  WHERE b = 2              ❌ 不符合最左前缀
  WHERE a = 1 AND c = 3    ⚠️ 只用到 a（c 用不到，中间断了）
```

#### Q6.2 事务的 ACID 特性？隔离级别？

```
ACID:
  • Atomicity（原子性）: 事务要么全部成功，要么全部回滚
  • Consistency（一致性）: 事务前后数据状态一致
  • Isolation（隔离性）: 并发事务互不干扰
  • Durability（持久性）: 提交后永久保存

隔离级别（从低到高）:
  ┌──────────────┬─────────┬───────────┬───────────┐
  │              │ 脏读     │ 不可重复读 │ 幻读       │
  ├──────────────┼─────────┼───────────┼───────────┤
  │ Read Uncommit│ ✅ 可能  │ ✅ 可能    │ ✅ 可能    │
  │ Read Committed│ ❌ 不可能│ ✅ 可能    │ ✅ 可能    │
  │ Repeatable   │ ❌      │ ❌         │ ✅ 可能    │
  │ Serializable │ ❌      │ ❌         │ ❌         │
  └──────────────┴─────────┴───────────┴───────────┘

  • 脏读: 读到未提交的数据
  • 不可重复读: 同一事务两次读结果不同（别人修改了）
  • 幻读: 同一事务两次查询，结果集行数不同（别人新增了）

MySQL 默认: Repeatable Read（可重复读）
  • 通过 MVCC 实现
  • 间隙锁解决幻读

MVCC（多版本并发控制）:
  • 每行数据有版本号
  • 读操作读快照（不阻塞写）
  • 写操作创建新版本
  
  优点: 读写不冲突，高并发性能好

锁机制:
  • 共享锁（S锁）: 读锁，多个事务可同时持有
  • 排他锁（X锁）: 写锁，独占
  • 行锁: 锁单行
  • 表锁: 锁整表
  • 间隙锁: 锁范围（防幻读）
```

### 进阶题

#### Q6.3 如何处理 MySQL 的大表性能问题？

```
1. 分库分表

  水平分表（按行）:
    user_0: id % 4 == 0
    user_1: id % 4 == 1
    user_2: id % 4 == 2
    user_3: id % 4 == 3
  
  垂直分表（按列）:
    user_base: id, name, age
    user_extra: id, bio, avatar  （不常用字段拆出）

  分库分表中间件:
    • ShardingSphere
    • MyCAT
    • Vitess

2. 读写分离
  • 主库写，从库读
  • 主从复制（binlog）
  • 应用层通过中间件路由

3. 数据归档
  • 历史数据迁移到归档表
  • 主表只保留近期数据
  • 定期清理（cron + 分区）

4. 分区表
  CREATE TABLE logs (
      id BIGINT,
      created_at DATETIME,
      content TEXT
  ) PARTITION BY RANGE (TO_DAYS(created_at)) (
      PARTITION p202401 VALUES LESS THAN (TO_DAYS('2024-02-01')),
      PARTITION p202402 VALUES LESS THAN (TO_DAYS('2024-03-01')),
      ...
  );
  
  • 按时间分区，查询自动裁剪
  • 可快速删除旧分区: ALTER TABLE logs DROP PARTITION p202401

5. 冷热分离
  • 热数据: Redis 缓存
  • 温数据: MySQL（SSD）
  • 冷数据: HBase / S3（HDD）

6. 查询优化
  • 避免 SELECT *
  • 用 LIMIT 分页
  • 深度分页优化:
    
    # ❌ 慢（OFFSET 越大越慢）
    SELECT * FROM orders ORDER BY id LIMIT 1000000, 20;
    
    # ✅ 快（游标分页）
    SELECT * FROM orders WHERE id > 1000000 ORDER BY id LIMIT 20;

7. 索引优化
  • 分析慢查询日志
  • EXPLAIN 分析执行计划
  • 补充缺失索引
```

#### Q6.4 Redis 的常用数据结构及场景？缓存策略？

```
Redis 数据结构:

  1. String
     场景: 缓存、计数器、分布式锁
     SET key value
     INCR counter
     
     # 分布式锁
     SET lock "value" NX PX 30000  # 原子设置+过期
  
  2. Hash
     场景: 对象存储
     HSET user:1 name "Alice" age 25
     HGET user:1 name
  
  3. List
     场景: 消息队列、最新列表
     LPUSH messages "hello"
     RPOP messages  # 队列
     LRANGE messages 0 -1
  
  4. Set
     场景: 标签、去重、共同好友
     SADD tags "python" "django"
     SINTER set1 set2  # 交集
  
  5. ZSet（有序集合）
     场景: 排行榜、延迟队列
     ZADD ranking 100 "Alice" 95 "Bob"
     ZREVRANGE ranking 0 9  # Top 10
     
     # 延迟队列
     ZADD delay_queue timestamp "task"
     # 定时扫描到期的任务

  6. Bitmap
     场景: 用户签到、统计
     SETBIT sign:202401:1 0 1  # 用户1第0天签到
     BITCOUNT sign:202401:1    # 统计签到天数
  
  7. HyperLogLog
     场景: UV 统计（基数估计）
     PFADD page_uv "user1" "user2"
     PFCOUNT page_uv  # 估算独立访客数
  
  8. Stream（5.0+）
     场景: 消息队列
     XADD stream * key value
     XREAD COUNT 10 STREAMS stream 0

缓存策略:

  1. Cache Aside（旁路缓存，最常用）
     读: 先查缓存，未命中查 DB 并回填
     写: 更新 DB，删除缓存
     
     # 伪代码
     def get_user(id):
         user = redis.get(f"user:{id}")
         if not user:
             user = db.query(id)
             redis.set(f"user:{id}", user, ttl=3600)
         return user
     
     def update_user(user):
         db.update(user)
         redis.delete(f"user:{user.id}")

  2. Write Through
     写: 同时写缓存和 DB
     优点: 缓存总是最新
     缺点: 写延迟高

  3. Write Behind
     写: 只写缓存，异步写 DB
     优点: 写性能极高
     缺点: 可能丢数据

缓存问题:
  • 缓存穿透: 查不存在的数据 → 布隆过滤器 / 缓存空值
  • 缓存击穿: 热点 key 失效 → 互斥锁 / 永不过期
  • 缓存雪崩: 大量 key 同时失效 → 过期时间加随机值

  # 防穿透: 缓存空值
  if user is None:
      redis.set(key, "", ttl=60)  # 短 TTL
  
  # 防击穿: 互斥锁
  def get_with_lock(key):
      value = redis.get(key)
      if value is None:
          if redis.set("lock:" + key, 1, nx=True, ex=10):
              try:
                  value = db.query(key)
                  redis.set(key, value, ttl=3600)
              finally:
                  redis.delete("lock:" + key)
          else:
              time.sleep(0.1)
              return get_with_lock(key)
      return value
```

### 高级题

#### Q6.5 设计一个分布式限流方案。

```
需求: 保护 API，限制每个用户每秒 100 次请求

方案 1: Redis + 滑动窗口
  import redis
  import time
  
  r = redis.Redis()
  
  def rate_limit(user_id, limit=100, window=1):
      key = f"rate:{user_id}:{int(time.time() // window)}"
      current = r.incr(key)
      if current == 1:
          r.expire(key, window)
      return current <= limit

方案 2: Redis + 令牌桶
  def token_bucket(user_id, capacity=100, rate=100):
      key = f"bucket:{user_id}"
      now = time.time()
      
      # Lua 脚本保证原子性
      lua = """
      local capacity = tonumber(ARGV[1])
      local rate = tonumber(ARGV[2])
      local now = tonumber(ARGV[3])
      
      local bucket = redis.call('HMGET', KEYS[1], 'tokens', 'last_time')
      local tokens = tonumber(bucket[1]) or capacity
      local last_time = tonumber(bucket[2]) or now
      
      -- 补充令牌
      tokens = math.min(capacity, tokens + (now - last_time) * rate)
      
      if tokens >= 1 then
          tokens = tokens - 1
          redis.call('HMSET', KEYS[1], 'tokens', tokens, 'last_time', now)
          return 1
      else
          redis.call('HMSET', KEYS[1], 'tokens', tokens, 'last_time', now)
          return 0
      end
      """
      return r.eval(lua, 1, key, capacity, rate, now)

方案 3: 分布式限流服务
  • 独立限流微服务
  • 所有 API 网关调用限流服务
  • 支持复杂规则（用户/IP/接口）

架构:
  Client → API Gateway → 限流中间件 → 业务服务
                         ↓
                      Redis（计数）

限流算法对比:
  ┌──────────┬────────────────┬──────────────────┐
  │ 算法      │ 优点            │ 缺点              │
  ├──────────┼────────────────┼──────────────────┤
  │ 计数器    │ 简单            │ 临界点突刺        │
  │ 滑动窗口  │ 平滑            │ 内存开销          │
  │ 令牌桶    │ 允许突发        │ 实现复杂          │
  │ 漏桶      │ 平滑输出        │ 无法突发          │
  └──────────┴────────────────┴──────────────────┘

高可用:
  • Redis 集群
  • 本地缓存兜底（Redis 挂了用本地限流）
  • 降级策略（限流服务不可用时放行或拒绝）
```

---

## 七、系统架构设计

### 基础题

#### Q7.1 单体架构 vs 微服务架构？如何选择？

```
单体架构:
  • 所有功能在一个应用中
  • 简单，开发部署方便
  • 适合小团队/早期项目

微服务架构:
  • 按业务拆分为多个服务
  • 独立部署、独立扩展
  • 适合大团队/复杂业务

对比:
  ┌──────────┬─────────────────┬─────────────────┐
  │          │   单体            │   微服务          │
  ├──────────┼─────────────────┼─────────────────┤
  │ 复杂度    │ 低               │ 高               │
  │ 开发效率  │ 早期高，后期低    │ 早期低，后期高    │
  │ 部署      │ 一次部署          │ 多服务独立部署    │
  │ 扩展      │ 整体扩展          │ 按需扩展          │
  │ 技术栈    │ 统一              │ 可异构            │
  │ 团队      │ 小团队            │ 多团队            │
  │ 运维      │ 简单              │ 复杂（需 K8s）    │
  └──────────┴─────────────────┴─────────────────┘

选择建议:
  • 早期项目 → 单体（快速验证）
  • 业务复杂 → 微服务（拆分管理）
  • 团队 < 10 人 → 单体
  • 团队 > 50 人 → 微服务
  
  "先单体，后微服务"（ strangler pattern 渐进式拆分）
```

### 进阶题

#### Q7.2 设计一个秒杀系统。

```
需求:
  • 10 万人抢 1000 件商品
  • 防止超卖
  • 高并发、低延迟

架构设计:

  ┌──────────┐
  │  CDN     │  ← 静态资源缓存
  └────┬─────┘
       │
  ┌────▼─────┐
  │  Nginx   │  ← 限流（IP/用户级）
  └────┬─────┘
       │
  ┌────▼─────┐
  │  API     │  ← 业务校验
  │  Gateway │
  └────┬─────┘
       │
  ┌────▼──────────────────┐
  │  Redis（库存预扣减）   │  ← 原子操作 DECR
  └────┬──────────────────┘
       │
  ┌────▼─────┐
  │  MQ      │  ← 异步下单
  │ (Kafka)  │
  └────┬─────┘
       │
  ┌────▼─────┐
  │  Order   │  ← 消费者创建订单
  │  Service │
  └────┬─────┘
       │
  ┌────▼─────┐
  │  MySQL   │  ← 最终持久化
  └──────────┘

核心流程:

  1. 活动前: 库存预热到 Redis
     SET stock:1001 1000
  
  2. 用户下单:
     # 原子扣减库存
     remaining = redis.decr("stock:1001")
     if remaining < 0:
         return "售罄"
     
     # 发送 MQ 异步创建订单
     mq.send({
         "user_id": user_id,
         "product_id": product_id,
         "order_id": generate_order_id()
     })
  
  3. 消费者处理:
     def consume(message):
         # 幂等检查
         if order_exists(message["order_id"]):
             return
         
         # 创建订单
         db.create_order(message)
         # 扣减数据库库存
         db.decr_stock(message["product_id"])

防超卖:
  • Redis DECR 原子操作（库存不会负）
  • 数据库乐观锁:
    UPDATE stock SET count = count - 1
    WHERE product_id = 1001 AND count > 0

高可用:
  • Redis 集群（主从+哨兵）
  • MQ 集群
  • 服务多实例

优化:
  • 页面静态化（CDN）
  • 按钮防重复提交（前端禁用 + 后端幂等）
  • 限流（令牌桶）
  • 风控（黑名单、验证码）
  • 库存预热 + 缓存
  • 异步下单（MQ 削峰）

扩展:
  • 分时段释放库存（未支付回收）
  • 库存预热分桶（避免热点 key）
```

### 高级题

#### Q7.3 设计一个分布式任务调度系统。

```
需求:
  • 定时执行任务（如每日报表、数据同步）
  • 支持任务依赖（A 完成后执行 B）
  • 高可用、可扩展
  • 失败重试、告警

架构:

  ┌──────────────┐
  │  Scheduler    │  ← 调度器（选举主节点）
  │  (主备)       │
  └──────┬───────┘
         │
  ┌──────▼───────┐
  │  Task Queue   │  ← 任务队列（Redis/RabbitMQ）
  └──────┬───────┘
         │
  ┌──────▼───────┐
  │  Workers      │  ← 执行器集群（水平扩展）
  │  (多个)       │
  └──────┬───────┘
         │
  ┌──────▼───────┐
  │  Storage      │  ← 任务状态存储（MySQL）
  └──────────────┘

核心组件:

  1. Scheduler（调度器）
     • 解析 cron 表达式
     • 到时间触发任务
     • 主备切换（ZooKeeper/etcd 选主）
  
  2. Task Queue
     • 存储待执行任务
     • 支持优先级
     • 持久化（防止丢失）
  
  3. Worker
     • 从队列拉取任务
     • 执行任务
     • 上报状态
  
  4. 监控告警
     • 任务失败告警
     • 任务超时告警
     • 指标采集（Prometheus）

任务依赖:
  
  # DAG（有向无环图）描述依赖
  dag = DAG()
  dag.add_task("extract", extract_func)
  dag.add_task("transform", transform_func, depends_on=["extract"])
  dag.add_task("load", load_func, depends_on=["transform"])
  
  # extract 完成后触发 transform，再触发 load

失败处理:
  • 自动重试（最多 N 次）
  • 指数退避
  • 超时熔断
  • 死信队列（多次失败后人工处理）

幂等性:
  • 任务必须幂等（可重复执行无副作用）
  • 用任务 ID 去重
  • 数据库唯一约束

技术选型:
  • Celery: Python 生态成熟
  • Airflow: 数据管道，DAG 支持
  • XXL-Job: Java 生态
  • 自研: 基于需求定制

Celery 示例:
  from celery import Celery, chain
  
  app = Celery('tasks', broker='redis://localhost')
  
  @app.task
  def extract():
      ...
  
  @app.task
  def transform(data):
      ...
  
  @app.task
  def load(data):
      ...
  
  # 链式调用
  workflow = chain(extract.s(), transform.s(), load.s())
  workflow.apply_async()
```

---

## 八、项目经验与工程实践

### 基础题

#### Q8.1 描述一个你做过的有挑战的项目。

```
回答框架（STAR 法）:

  S (Situation) 背景:
    • 项目是什么？解决什么问题？
    • 技术栈？
    • 团队规模？
  
  T (Task) 任务:
    • 你的角色？
    • 负责什么？
    • 面临什么挑战？
  
  A (Action) 行动:
    • 你做了什么？
    • 技术方案？
    • 解决了什么问题？
    • 如何决策的？
  
  R (Result) 结果:
    • 量化成果（性能提升 X%、成本降低 Y%）
    • 学到了什么？
    • 有什么不足？

示例:
  S: 电商平台，日活百万，订单服务用 Django 单体架构
  
  T: 我负责订单服务，QPS 从 500 涨到 3000，单体扛不住，
     接口延迟从 200ms 升到 2s
  
  A: 
    1. 分析瓶颈: MySQL 慢查询 + Django ORM N+1 问题
    2. 优化数据库:
       - 加索引（查询从 800ms → 50ms）
       - 读写分离（主写从读）
       - 分库分表（按用户 ID）
    3. 引入缓存:
       - Redis 缓存热门商品
       - 本地缓存二级缓存
    4. 异步化:
       - Celery 处理非核心逻辑（发短信、统计）
       - Kafka 削峰
    5. 服务拆分:
       - 订单服务独立部署
       - FastAPI 重写 API（异步）
  
  R:
    • QPS: 500 → 5000（10 倍）
    • 延迟: 2s → 100ms（20 倍）
    • 可用性: 99.5% → 99.95%
    • 学到了: 系统演进式优化，不要过度设计

面试要点:
  • 突出"你的"贡献（不是团队的）
  • 量化结果（数字最有说服力）
  • 展示技术深度（能说清原理）
  • 体现权衡思考（为什么选 A 不选 B）
```

### 进阶题

#### Q8.2 如何做代码质量保障？

```
1. 代码规范
   • Linter: flake8 / pylint / ruff
   • 格式化: black / autopep8
   • 类型检查: mypy / pyright
   
   # pyproject.toml
   [tool.ruff]
   line-length = 100
   
   [tool.mypy]
   strict = true

2. 单元测试
   • 框架: pytest
   • 覆盖率: pytest-cov
   • Mock: pytest-mock
   
   def test_create_user():
       user = create_user("Alice", "alice@test.com")
       assert user.name == "Alice"
       assert user.email == "alice@test.com"
   
   # 覆盖率目标: 80%+
   pytest --cov=app --cov-report=html

3. CI/CD
   • GitHub Actions / GitLab CI
   • 自动化: lint → test → build → deploy
   
   # .github/workflows/ci.yml
   jobs:
     test:
       steps:
         - run: pip install -r requirements.txt
         - run: ruff check .
         - run: mypy app/
         - run: pytest --cov

4. 代码审查
   • PR 必须至少 1 人 approve
   • 检查: 逻辑、规范、安全、性能
   • 使用工具: Reviewable / Gerrit

5. 集成测试
   • 测试 API 端到端
   • Docker Compose 启动依赖
   
   def test_user_flow():
       # 创建用户
       resp = client.post("/users", json={...})
       assert resp.status_code == 201
       user_id = resp.json()["id"]
       
       # 查询
       resp = client.get(f"/users/{user_id}")
       assert resp.json()["name"] == "Alice"

6. 性能测试
   • Locust / k6 压测
   • 关注 P99 延迟、吞吐量
   
   from locust import HttpUser, task
   
   class ApiUser(HttpUser):
       @task
       def get_users(self):
           self.client.get("/users")

7. 监控告警
   • Prometheus + Grafana
   • Sentry 错误追踪
   • 日志: ELK / Loki

8. 安全
   • 依赖扫描: safety / pip-audit
   • SAST: bandit
   • 密钥管理: 不硬编码，用环境变量/Vault
```

### 高级题

#### Q8.3 线上故障排查流程？举例说明。

```
故障排查 SOP:

  1. 发现问题
     • 监控告警（Prometheus/Sentry）
     • 用户反馈
     • 日志异常
  
  2. 快速止血
     • 回滚最近发布
     • 降级（关闭非核心功能）
     • 限流
     • 扩容
  
  3. 定位原因
     • 查日志
     • 查监控指标
     • 查链路追踪
     • 复现问题
  
  4. 修复
     • 修复代码
     • 灰度发布
     • 验证
  
  5. 复盘
     • 5 Why 分析根因
     • 改进措施
     • 防止复发

案例: 订单服务 500 错误突增

  发现:
    • Sentry 报错: OperationalError: (2003, "Can't connect to MySQL")
    • 错误率从 0.1% → 30%
    • 延迟从 100ms → 5s
  
  止血:
    • 开启限流（QPS 降为 1/3）
    • 切换到备用数据库
    • 错误率下降到 5%
  
  定位:
    • 查 MySQL 监控: 连接数打满（1000/1000）
    • 查慢日志: 某个 SELECT 查询耗时 10s
    • 查代码: 发现一个缺失索引的查询，全表扫描 1000 万行
  
  根因:
    • 新上线代码引入了一个无索引查询
    • 高并发下连接数耗尽
    • 连锁导致其他查询也超时
  
  修复:
    • 紧急加索引
    • 优化查询（添加 LIMIT）
    • 增加连接池上限（1000 → 2000）
    • 恢复正常流量
  
  复盘:
    • 5 Why:
      1. 为什么报错？→ 数据库连不上
      2. 为什么连不上？→ 连接数满
      3. 为什么连接数满？→ 慢查询堆积
      4. 为什么慢查询？→ 缺索引
      5. 为什么缺索引？→ 代码审查未发现
    
    • 改进:
      - 上线前必须 EXPLAIN 检查
      - 慢查询告警（>1s 立即告警）
      - 连接池监控
      - 自动化测试增加 SQL 性能测试

工具链:
  • 日志: ELK (Elasticsearch + Logstash + Kibana)
  • 监控: Prometheus + Grafana
  • 链路追踪: Jaeger / SkyWalking
  • 错误追踪: Sentry
  • 告警: Alertmanager / PagerDuty
```

---

## 九、总结

### 高级 Python 工程师能力图谱

```
高级 Python 工程师
│
├── 核心语法
│   ├── 可变/不可变对象、引用语义
│   ├── GIL 原理与影响
│   ├── 深浅拷贝
│   └── MRO（C3 线性化）
│
├── 高级特性
│   ├── 装饰器（带参数/类装饰器）
│   ├── 生成器/迭代器
│   ├── 上下文管理器
│   ├── 元类
│   └── 内存管理（引用计数+GC+内存池）
│
├── 性能优化
│   ├── 性能分析工具（cProfile/line_profiler）
│   ├── 数据结构选择
│   ├── 内存优化（__slots__/生成器）
│   ├── Cython/Numba/ctypes
│   └── 字节码优化
│
├── 并发编程
│   ├── 进程/线程/协程选型
│   ├── 锁机制（Lock/RLock/Semaphore）
│   ├── asyncio 原理与实践
│   ├── 线程安全单例
│   └── 生产者-消费者模式
│
├── Web 框架
│   ├── Django（ORM优化/中间件）
│   ├── Flask（轻量灵活）
│   ├── FastAPI（异步/类型/文档）
│   └── 架构选型
│
├── 数据库
│   ├── MySQL（索引/事务/分库分表）
│   ├── Redis（数据结构/缓存策略）
│   ├── 缓存问题（穿透/击穿/雪崩）
│   └── 分布式限流
│
├── 系统设计
│   ├── 单体 vs 微服务
│   ├── 秒杀系统
│   ├── 分布式任务调度
│   └── 短链系统
│
└── 工程实践
    ├── 代码质量（测试/CI/CD）
    ├── 故障排查（SOP/工具链）
    └── 项目经验（STAR 法则）
```

### 面试准备清单

```
□ Python 原理
  □ GIL、内存管理、MRO
  □ 装饰器、生成器、元类
  □ 深浅拷贝、可变性陷阱

□ 性能优化
  □ cProfile / line_profiler
  □ __slots__ / 生成器 / NumPy
  □ Cython / Numba

□ 并发编程
  □ 进程/线程/协程对比
  □ asyncio 实战
  □ 线程安全与锁

□ Web 框架
  □ Django ORM 优化
  □ FastAPI 异步优势
  □ 中间件原理

□ 数据库
  □ MySQL 索引/事务/分表
  □ Redis 数据结构/缓存策略
  □ 缓存三大问题

□ 系统设计
  □ 秒杀/短链/任务调度
  □ 微服务架构

□ 工程实践
  □ 测试/CI/CD
  □ 故障排查 SOP
  □ STAR 项目讲述
```

### 面试回答通用技巧

```
1. 结构化回答
   • 总-分-总: 先结论，再展开，再总结
   • 分点陈述: 第一/第二/第三
   • 举例说明: 用具体案例支撑观点

2. 展示深度
   • 不只说"怎么做"，还说"为什么"
   • 展示权衡思考: A 方案 vs B 方案
   • 提及实际经验: "在我做的项目中..."

3. 量化成果
   • "优化后 QPS 从 500 提升到 5000"
   • "延迟从 2s 降到 100ms"
   • "成本降低 30%"

4. 诚实
   • 不会就说"不太了解"，不要编
   • 可以说"我的理解是...，可能需要查证"

5. 反问
   • 展示思考深度
   • "这个场景的 QPS 大概多少？"
   • "团队技术栈是怎样的？"
```
