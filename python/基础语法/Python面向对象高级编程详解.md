# Python 面向对象高级编程详解

> 本文是《Python 面向对象编程详解》的进阶篇，聚焦于 Python 面向对象中更深入、更动态的特性：`__slots__`、`@property`、多重继承与 Mixin、定制类、抽象基类与元类。

## 1. 使用 __slots__ 限制实例属性

### 1.1 动态绑定的"烦恼"

Python 允许在运行时给实例**动态添加任意属性**，这很灵活，但也可能因拼写错误而埋下隐患：

```python
class Student:
    def __init__(self, name):
        self.name = name

s = Student('Alice')
s.score = 95        # 动态添加实例属性
s.socre = 95        # 拼写错误，Python 不会报错，却悄悄创建了一个新属性
print(s.score)      # 95
print(s.socre)      # 95（本应报错却没报）
```

此外，每个实例默认维护一个 `__dict__` 字典来存储属性，会占用较多内存。

### 1.2 用 __slots__ 限定属性

定义 `__slots__` 后，实例**只能拥有**列出的属性，不能再动态添加其他属性，同时省去 `__dict__`，节省内存：

```python
class Student:
    __slots__ = ('name', 'age', 'score')   # 用元组或列表声明允许的属性

    def __init__(self, name, age):
        self.name = name
        self.age = age

s = Student('Alice', 20)
s.score = 95       # 允许
s.address = 'BJ'   # AttributeError: 'Student' object has no attribute 'address'
```

### 1.3 __slots__ 的注意事项

- **`__slots__` 不影响类属性**，只限制实例属性。
- **子类需重新定义自己的 `__slots__`** 才能继续限制；若子类未定义，则子类实例仍会有 `__dict__`，限制失效。
- **继承时的属性集合**是父类与子类 `__slots__` 的并集。

```python
class Person:
    __slots__ = ('name',)

class Student(Person):
    __slots__ = ('score',)   # 子类实例允许 name 和 score

s = Student()
s.name = 'Alice'
s.score = 95
# s.age = 20   # AttributeError
```

> **适用场景**：当类的实例数量巨大（如百万级数据对象）时，`__slots__` 能显著降低内存占用；普通场景不必强求。

---

## 2. @property 属性装饰器

### 2.1 为什么需要 @property

为了让外部"像访问属性一样"调用方法，同时能在内部加入校验逻辑，Python 提供 `@property` 装饰器，把一个方法变成"只读属性"：

```python
class Student:
    def __init__(self, name, score):
        self.name = name
        self._score = score

    @property
    def score(self):
        """ getter：读取分数 """
        return self._score

    @score.setter
    def score(self, value):
        """ setter：设置分数，带校验 """
        if not isinstance(value, (int, float)):
            raise TypeError('score 必须是数字')
        if value < 0 or value > 100:
            raise ValueError('score 必须在 0~100 之间')
        self._score = value

s = Student('Alice', 80)
print(s.score)     # 80，像属性一样访问（实际调用 getter）
s.score = 95       # 像属性一样赋值（实际调用 setter，触发校验）
# s.score = 150    # ValueError: score 必须在 0~100 之间
# s.score = 'A'    # TypeError: score 必须是数字
```

### 2.2 只读属性

只定义 `@property`（getter）而不定义 setter，就得到**只读属性**：

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def area(self):
        """ 面积：只读，由半径计算得出 """
        return 3.14159 * self._radius ** 2

c = Circle(5)
print(c.area)     # 78.53975
# c.area = 100    # AttributeError: can't set attribute
```

### 2.3 使用要点

- 内部真实数据通常用 `_` 前缀（如 `_score`）表示"受保护"，对外暴露同名无下划线的 `@property`。
- `@property` 既能做参数校验，也能实现"由其他属性计算而来"的派生属性。
- 三个装饰器配套：`@property`（读）、`@xxx.setter`（写）、`@xxx.deleter`（删）。

---

## 3. 多重继承与 Mixin

### 3.1 Python 支持多重继承

Python 允许一个类继承**多个父类**：

```python
class Father:
    def work(self):
        print('working')

class Mother:
    def cook(self):
        print('cooking')

class Child(Father, Mother):
    pass

c = Child()
c.work()   # working
c.cook()   # cooking
```

### 3.2 Mixin 设计模式

**Mixin（混入）** 是一种通过多重继承为类**附加可选功能**的设计模式。Mixin 类通常：
- 功能单一，只负责一项额外能力；
- 不单独使用，而是被其他类继承来"混入"功能；
- 名称常以 `Mixin` 结尾以示区分。

```python
class SerializableMixin:
    """ 提供序列化为字典的能力 """
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

class LoggableMixin:
    """ 提供日志输出能力 """
    def log(self, msg):
        print(f'[{self.__class__.__name__}] {msg}')

class User(SerializableMixin, LoggableMixin):
    def __init__(self, name, age):
        self.name = name
        self.age = age

u = User('Alice', 20)
print(u.to_dict())   # {'name': 'Alice', 'age': 20}
u.log('created')     # [User] created
```

> **设计建议**：主体继承用于表达 "is-a" 的纵向关系，Mixin 用于横向补充 "can-do" 的能力。优先使用单一继承 + 多个 Mixin，避免复杂的菱形继承。

### 3.3 Mixin 与 __slots__

Mixin 与 `__slots__` 配合时需注意：若多个父类都定义了 `__slots__`，子类需显式声明自己的 `__slots__` 才能保持限制生效。

---

## 4. 方法解析顺序（MRO）

### 4.1 什么是 MRO

多重继承下，查找属性/方法时按什么顺序遍历父类？这就是 **MRO（Method Resolution Order）**。Python 使用 **C3 线性化**算法，保证顺序一致且无歧义。

查看类的 MRO：

```python
class A:
    def hello(self):
        print('A')

class B(A):
    def hello(self):
        print('B')

class C(A):
    def hello(self):
        print('C')

class D(B, C):
    pass

d = D()
d.hello()          # B（先找 B，再找 C，最后 A）

print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)
```

### 4.2 super() 的真实行为

`super()` 并非"调用父类方法"那么简单——它按 **MRO 顺序**调用**下一个类**的方法，而非字面上的父类：

```python
class A:
    def show(self):
        print('A.show')

class B(A):
    def show(self):
        print('B.show')
        super().show()      # MRO 中 B 的下一个是 A

class C(A):
    def show(self):
        print('C.show')
        super().show()      # MRO 中 C 的下一个是 A

class D(B, C):
    def show(self):
        print('D.show')
        super().show()      # MRO 中 D 的下一个是 B

# D 的 MRO: D -> B -> C -> A -> object
d = D()
d.show()
# D.show
# B.show
# C.show
# A.show
```

> **要点**：在多重继承中，每个类的 `show` 通过 `super().show()` 调用，会沿 MRO 链依次执行，从而让所有协作类都能被调用到。这就是"协作式多重继承"的核心。

---

## 5. 定制类（动态特性）

Python 提供大量**双下划线方法（dunder methods）**，让我们能定制类的行为。以下介绍几个常用且强大的动态特性。

### 5.1 __str__ 与 __repr__

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        """ print() / str() 调用，面向用户 """
        return f'Point({self.x}, {self.y})'

    def __repr__(self):
        """ 交互式环境 / repr() 调用，面向开发者，应能还原对象 """
        return f'Point({self.x!r}, {self.y!r})'

p = Point(1, 2)
print(p)       # Point(1, 2)        调用 __str__
print(repr(p)) # Point(1, 2)        调用 __repr__
```

> **约定**：`__repr__` 应返回一个能重建对象的合法表达式；若只实现 `__repr__`，`__str__` 未定义时会回退到 `__repr__`。

### 5.2 __iter__ 与 __next__：让对象可迭代

```python
class Fib:
    """ 斐波那契数列迭代器 """
    def __init__(self, max_n):
        self.max_n = max_n
        self.a, self.b = 0, 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.a >= self.max_n:
            raise StopIteration()
        value = self.a
        self.a, self.b = self.b, self.a + self.b
        return value

for n in Fib(20):
    print(n, end=' ')   # 0 1 1 2 3 5 8 13
```

### 5.3 __getitem__：支持索引与切片

```python
class CardDeck:
    """ 一副扑克牌，支持索引访问 """
    suits = ['♠', '♥', '♣', '♦']
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')

    def __getitem__(self, index):
        # 支持切片：返回切片对象时构造新列表
        if isinstance(index, slice):
            return [(r, s) for s in self.suits for r in self.ranks][index]
        # 支持整数索引
        suit = self.suits[index // len(self.ranks)]
        rank = self.ranks[index % len(self.ranks)]
        return (rank, suit)

    def __len__(self):
        return len(self.suits) * len(self.ranks)

deck = CardDeck()
print(deck[0])        # ('2', '♠')
print(deck[-1])       # ('A', '♦')
print(deck[0:3])      # [('2', '♠'), ('3', '♠'), ('4', '♠')]
```

> 实现了 `__getitem__` 的类，还能直接用于 `for` 循环（Python 会按索引依次取值，直到 `IndexError`）。

### 5.4 __getattr__：动态属性

当访问**不存在的属性**时，Python 会调用 `__getattr__`，可用于动态返回属性：

```python
class Chain:
    """ 链式调用：Chain().status.user.timeline 得到路径字符串 """
    def __init__(self, path=''):
        self._path = path

    def __getattr__(self, attr):
        # 拼接路径，返回新的 Chain 实例以支持继续链式调用
        return Chain(f'{self._path}/{attr}')

    def __str__(self):
        return self._path

print(Chain().status.user.timeline)   # /status/user/timeline
```

> **注意**：`__getattr__` 只在属性**未找到**时触发；已有属性（含 `__init__` 中设置的）不会走这里。务必避免在 `__getattr__` 中再次访问不存在的属性，否则会无限递归。

### 5.5 __call__：让实例像函数一样可调用

```python
class Adder:
    def __init__(self, n):
        self.n = n

    def __call__(self, x):
        return self.n + x

add5 = Adder(5)
print(add5(10))       # 15，实例像函数一样被调用
print(callable(add5)) # True
```

> 判断对象是否"可调用"用内置函数 `callable()`。函数、类、实现了 `__call__` 的实例都可调用。

---

## 6. 抽象基类（ABC）

### 6.1 为什么需要抽象基类

抽象基类（Abstract Base Class）用于**定义接口规范**：要求子类必须实现某些方法，否则不能实例化。

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    """ 抽象基类：定义动物接口 """

    @abstractmethod
    def speak(self):
        """ 子类必须实现 """
        ...

    @abstractmethod
    def move(self):
        """ 子类必须实现 """
        ...

class Dog(Animal):
    def speak(self):
        return '汪汪'

    def move(self):
        return '跑'

# a = Animal()    # TypeError: 无法实例化抽象类
d = Dog()
print(d.speak(), d.move())   # 汪汪 跑
```

### 6.2 抽象方法与具体方法

抽象基类中可以同时包含**抽象方法**（子类必须实现）和**具体方法**（子类可直接继承复用）：

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        ...

    def describe(self):           # 具体方法，子类可直接用
        return f'{self.__class__.__name__} 面积 = {self.area():.2f}'

class Circle(Shape):
    def __init__(self, r):
        self.r = r

    def area(self):
        return 3.14159 * self.r ** 2

print(Circle(2).describe())   # Circle 面积 = 12.57
```

> **与 Java 接口的区别**：Python 的 ABC 是"软约束"——它只在实例化时检查抽象方法是否被实现，不强制类型声明；Java 是编译期强检查。

---

## 7. 元类（Metaclass）

### 7.1 type：类的类

在 Python 中，**类本身也是对象**，而创建类的"类"就是 **元类**。默认的元类是 `type`。

```python
# 用 class 关键字定义类
class Dog:
    def bark(self):
        return 'woof'

# 等价于用 type 动态创建
def bark(self):
    return 'woof'

Dog = type('Dog', (object,), {'bark': bark})

d = Dog()
print(d.bark())        # woof
print(type(Dog))       # <class 'type'>，类的类型是 type
```

`type` 创建类的语法：`type(类名, (父类元组,), {属性字典})`。

### 7.2 自定义元类

自定义元类可拦截类的创建过程，在类定义时自动修改类（如添加方法、校验属性、注册类等）。自定义元类需继承 `type`：

```python
class LoggedMeta(type):
    """ 元类：创建类时打印日志，并自动给类添加一个 created 标记 """
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        print(f'[LoggedMeta] 创建类: {name}')
        cls._created_by_meta = True
        return cls

# 通过 metaclass 指定元类
class Service(metaclass=LoggedMeta):
    def run(self):
        return 'running'
# 控制台: [LoggedMeta] 创建类: Service

print(Service._created_by_meta)   # True
```

### 7.3 元类的典型应用

- **ORM 框架**：Django ORM、SQLAlchemy 用元类在类定义时收集字段信息，自动生成数据库映射。
- **插件注册**：类被定义时自动注册到全局注册表。
- **接口校验**：强制子类实现某些方法（替代 ABC 的另一种思路）。

### 7.4 使用建议

> **警告**：元类是 Python 中最"魔法"的特性，理解门槛高、调试难度大。**99% 的场景不需要自定义元类**。能用普通类、装饰器、`__init_subclass__` 解决的，就不要用元类。

`__init_subclass__` 是元类的轻量替代，能在父类被继承时执行逻辑：

```python
class PluginBase:
    _registry = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        PluginBase._registry.append(cls)   # 子类被定义时自动注册

class PluginA(PluginBase): pass
class PluginB(PluginBase): pass

print([c.__name__ for c in PluginBase._registry])   # ['PluginA', 'PluginB']
```

---

## 8. 综合应用示例

### 8.1 实现一个带校验与序列化的模型类

综合运用 `__slots__`、`@property`、Mixin：

```python
class SerializableMixin:
    def to_dict(self):
        return {k: getattr(self, k) for k in self.__slots__}

class Product(SerializableMixin):
    __slots__ = ('_name', '_price', '_stock')

    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value:
            raise ValueError('name 不能为空')
        self._name = value

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if value < 0:
            raise ValueError('price 不能为负')
        self._price = value

    @property
    def stock(self):
        return self._stock

    @stock.setter
    def stock(self, value):
        if value < 0:
            raise ValueError('stock 不能为负')
        self._stock = value

    def __repr__(self):
        return f'Product({self._name!r}, {self._price}, {self._stock})'

p = Product('笔记本', 5999.0, 100)
print(p.to_dict())    # {'name': '笔记本', 'price': 5999.0, 'stock': 100}
print(repr(p))        # Product('笔记本', 5999.0, 100)
# p.price = -1        # ValueError: price 不能为负
```

### 8.2 自定义可迭代容器

```python
class NumberRange:
    """ 可迭代、可索引、可求长的数字范围 """
    def __init__(self, start, end, step=1):
        self.data = list(range(start, end, step))

    def __getitem__(self, index):
        if isinstance(index, slice):
            return self.data[index]
        return self.data[index]

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __contains__(self, item):
        return item in self.data

r = NumberRange(1, 10)
print(len(r))        # 9
print(r[3])          # 4
print(r[2:5])        # [3, 4, 5]
print(5 in r)        # True
for x in r:
    print(x, end=' ')  # 1 2 3 4 5 6 7 8 9
```

---

## 9. 小结

### 9.1 核心要点

| 特性 | 作用 | 关键点 |
|------|------|--------|
| `__slots__` | 限制实例属性、节省内存 | 子类需重新定义才生效；不影响类属性 |
| `@property` | 把方法包装为属性 | 支持 getter/setter/deleter，可加校验 |
| 多重继承 / Mixin | 横向附加功能 | Mixin 功能单一、不单独使用 |
| MRO / `super()` | 方法查找顺序 | C3 线性化；`super()` 按 MRO 调用下一个类 |
| 定制类 | 改变对象行为 | `__str__`/`__repr__`/`__iter__`/`__getitem__`/`__getattr__`/`__call__` |
| 抽象基类 ABC | 定义接口规范 | `@abstractmethod`，未实现则不可实例化 |
| 元类 metaclass | 创建/修改类 | 默认是 `type`；优先用 `__init_subclass__` 替代 |

### 9.2 设计心法

1. **优先组合，而非继承**：能用组合（has-a）实现的，不必用继承（is-a）。
2. **Mixin 用于能力扩展**，主体继承用于关系表达，避免过深的继承树。
3. **`@property` 比直接暴露属性更安全**，尤其涉及校验时。
4. **元类是最后的手段**：先考虑普通类、装饰器、`__init_subclass__`、ABC。
5. **动态特性（`__getattr__`/`__call__`）能写出非常简洁的 API**，但要注意可读性与调试成本。

### 9.3 进阶学习路径

```
__slots__ / @property → 多重继承 & Mixin → MRO & super()
    → 定制类（魔术方法）→ 抽象基类 ABC → 元类 metaclass → __init_subclass__
```
