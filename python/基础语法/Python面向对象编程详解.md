# Python 面向对象编程详解

## 1. 面向对象编程概述

### 1.1 什么是面向对象

面向对象编程（Object Oriented Programming, OOP）是一种程序设计思想，把对象作为程序的基本单元，对象包含数据和操作数据的方法。

**OOP 三大特性**：
- **封装**：隐藏内部实现细节，对外提供接口
- **继承**：子类继承父类的属性和方法，实现代码复用
- **多态**：不同对象对同一消息做出不同响应

### 1.2 面向过程 vs 面向对象

```python
# 面向过程：以函数为中心
std1 = {'name': 'Alice', 'score': 98}
std2 = {'name': 'Bob', 'score': 81}

def print_score(std):
    print(f"{std['name']}: {std['score']}")

print_score(std1)
print_score(std2)

# 面向对象：以对象为中心
class Student:
    def __init__(self, name, score):
        self.name = name
        self.score = score

    def print_score(self):
        print(f"{self.name}: {self.score}")

s1 = Student('Alice', 98)
s2 = Student('Bob', 81)
s1.print_score()
s2.print_score()
```

---

## 2. 类和实例

### 2.1 定义类

```python
class Student(object):
    """学生类"""

    # 类属性（所有实例共享）
    school = '北京大学'

    # 构造方法（初始化实例属性）
    def __init__(self, name, score):
        self.name = name        # 实例属性
        self.score = score

    # 实例方法
    def print_score(self):
        print(f"{self.name}: {self.score}")

    def get_grade(self):
        if self.score >= 90:
            return 'A'
        elif self.score >= 60:
            return 'B'
        else:
            return 'C'
```

### 2.2 创建实例

```python
# 创建实例
s1 = Student('Alice', 98)
s2 = Student('Bob', 81)

# 调用方法
s1.print_score()      # Alice: 98
print(s2.get_grade())  # B

# 访问属性
print(s1.name)         # Alice
print(s1.school)       # 北京大学（类属性）

# 动态添加实例属性（Python 特有）
s1.age = 20
print(s1.age)          # 20
# print(s2.age)        # AttributeError，s2 没有 age
```

### 2.3 类属性 vs 实例属性

```python
class Dog:
    # 类属性：所有实例共享
    species = 'Canis lupus'
    count = 0

    def __init__(self, name):
        # 实例属性：每个实例独有
        self.name = name
        Dog.count += 1    # 访问类属性

d1 = Dog('Rex')
d2 = Dog('Buddy')

print(d1.species)      # Canis lupus
print(d2.species)      # Canis lupus
print(Dog.count)       # 2

# 注意：实例属性会遮蔽同名类属性
d1.species = 'Custom'  # 创建实例属性，不影响类属性
print(d1.species)      # Custom
print(d2.species)      # Canis lupus
print(Dog.species)     # Canis lupus
```

---

## 3. 访问限制（封装）

### 3.1 私有属性

Python 通过**命名约定**实现访问控制：

| 命名 | 访问级别 | 说明 |
|------|----------|------|
| `name` | 公开 | 可外部访问 |
| `_name` | 受保护 | 约定不直接访问（但可访问） |
| `__name` | 私有 | 名称改写，外部不能直接访问 |
| `__name__` | 特殊 | Python 内置方法/属性 |

```python
class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner        # 公开属性
        self._type = 'savings'    # 受保护属性
        self.__balance = balance  # 私有属性

    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
            return True
        return False

    def withdraw(self, amount):
        if 0 < amount <= self.__balance:
            self.__balance -= amount
            return amount
        return 0

    def get_balance(self):
        return self.__balance

account = BankAccount('Alice', 1000)
print(account.owner)          # Alice
print(account._type)          # savings（能访问但不建议）
# print(account.__balance)    # AttributeError！
print(account.get_balance())  # 1000，通过方法访问
```

### 3.2 名称改写（Name Mangling）

```python
# __balance 实际被改写为 _BankAccount__balance
print(account._BankAccount__balance)  # 1000（能访问但不推荐）

# 双下划线开头且结尾的不是私有属性
class MyClass:
    def __init__(self):
        self.__data__ = "特殊属性"  # 不是私有！

obj = MyClass()
print(obj.__data__)  # 特殊属性
```

### 3.3 使用 property 装饰器

```python
class Temperature:
    def __init__(self, celsius):
        self._celsius = celsius

    @property
    def celsius(self):
        """获取摄氏温度"""
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        """设置摄氏温度，带校验"""
        if value < -273.15:
            raise ValueError("温度不能低于绝对零度")
        self._celsius = value

    @property
    def fahrenheit(self):
        """华氏温度（只读）"""
        return self._celsius * 9 / 5 + 32

t = Temperature(25)
print(t.celsius)      # 25，自动调用 getter
t.celsius = 30        # 自动调用 setter
print(t.fahrenheit)   # 86.0
# t.fahrenheit = 100  # AttributeError，只读属性
```

---

## 4. 继承和多态

### 4.1 基本继承

```python
class Animal(object):
    """父类（基类）"""
    def __init__(self, name):
        self.name = name

    def speak(self):
        print(f"{self.name} 发出声音")

    def eat(self):
        print(f"{self.name} 正在进食")

class Dog(Animal):
    """子类，继承 Animal"""
    def speak(self):
        print(f"{self.name} 汪汪叫")

    def fetch(self):
        print(f"{self.name} 在接飞盘")

class Cat(Animal):
    """子类，继承 Animal"""
    def speak(self):
        print(f"{self.name} 喵喵叫")

dog = Dog('Rex')
cat = Cat('Whiskers')

dog.speak()   # Rex 汪汪叫（子类方法）
dog.eat()     # Rex 正在进食（继承的方法）
dog.fetch()   # Rex 在接飞盘（子类独有）

cat.speak()   # Whiskers 喵喵叫
```

### 4.2 多态

```python
def make_speak(animal):
    """多态：不同对象调用同一方法，行为不同"""
    animal.speak()

make_speak(dog)  # Rex 汪汪叫
make_speak(cat)  # Whiskers 喵喵叫

# 只要是 Animal 的子类，都能传入
class Duck(Animal):
    def speak(self):
        print(f"{self.name} 嘎嘎叫")

make_speak(Duck('Donald'))  # Donald 嘎嘎叫
```

### 4.3 调用父类方法

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def info(self):
        return f"{self.name}, {self.age}岁"

class Student(Person):
    def __init__(self, name, age, school):
        # 调用父类构造方法
        super().__init__(name, age)  # Python 3 推荐写法
        # Person.__init__(self, name, age)  # 旧式写法
        self.school = school

    def info(self):
        # 调用父类方法并扩展
        return f"{super().info()}, 就读于{self.school}"

s = Student('Alice', 20, '北京大学')
print(s.info())  # Alice, 20岁, 就读于北京大学
```

### 4.4 多重继承

```python
class Runnable:
    def run(self):
        print("奔跑中...")

class Swimmable:
    def swim(self):
        print("游泳中...")

class Flyable:
    def fly(self):
        print("飞行中...")

# 多重继承
class SuperHero(Runnable, Swimmable, Flyable):
    pass

hero = SuperHero()
hero.run()    # 奔跑中...
hero.swim()   # 游泳中...
hero.fly()    # 飞行中...
```

### 4.5 MixIn 模式

```python
# MixIn：为类添加额外功能，约定以 MixIn 结尾
class SerializableMixin:
    """序列化功能"""
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()
                if not k.startswith('_')}

class LoggableMixin:
    """日志功能"""
    def log(self, message):
        print(f"[{self.__class__.__name__}] {message}")

class User(SerializableMixin, LoggableMixin):
    def __init__(self, name, age):
        self.name = name
        self.age = age

user = User('Alice', 25)
print(user.to_dict())  # {'name': 'Alice', 'age': 25}
user.log("用户创建")    # [User] 用户创建
```

---

## 5. 特殊方法（魔术方法）

### 5.1 常用特殊方法

```python
class Vector:
    """二维向量类，演示特殊方法"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # 字符串表示
    def __str__(self):
        """print() 时调用，面向用户"""
        return f"Vector({self.x}, {self.y})"

    def __repr__(self):
        """开发调试时调用，面向开发者"""
        return f"Vector(x={self.x!r}, y={self.y!r})"

    # 运算符重载
    def __add__(self, other):
        """+ 运算"""
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """- 运算"""
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        """* 运算"""
        return Vector(self.x * scalar, self.y * scalar)

    # 比较
    def __eq__(self, other):
        """== 运算"""
        return self.x == other.x and self.y == other.y

    # 长度与迭代
    def __len__(self):
        return int((self.x**2 + self.y**2)**0.5)

    def __getitem__(self, index):
        return (self.x, self.y)[index]

    # 布尔值
    def __bool__(self):
        return self.x != 0 or self.y != 0

    # 可调用
    def __call__(self, scalar):
        return self * scalar

v1 = Vector(3, 4)
v2 = Vector(1, 2)

print(v1)           # Vector(3, 4)
print(repr(v1))     # Vector(x=3, y=4)
print(v1 + v2)      # Vector(4, 6)
print(v1 * 2)       # Vector(6, 8)
print(v1 == v2)     # False
print(len(v1))      # 5
print(v1[0])        # 3
print(v1(3))        # Vector(9, 12)
```

### 5.2 容器类特殊方法

```python
class MyList:
    """自定义列表类"""
    def __init__(self, data=None):
        self._data = data or []

    def __len__(self):
        """len()"""
        return len(self._data)

    def __getitem__(self, key):
        """obj[key]"""
        if isinstance(key, slice):
            return MyList(self._data[key])
        return self._data[key]

    def __setitem__(self, key, value):
        """obj[key] = value"""
        self._data[key] = value

    def __delitem__(self, key):
        """del obj[key]"""
        del self._data[key]

    def __contains__(self, item):
        """item in obj"""
        return item in self._data

    def __iter__(self):
        """迭代支持"""
        return iter(self._data)

    def __reversed__(self):
        """reversed()"""
        return MyList(list(reversed(self._data)))

ml = MyList([1, 2, 3, 4, 5])
print(len(ml))       # 5
print(ml[2])         # 3
print(ml[1:3])       # MyList
ml[0] = 100
print(3 in ml)       # True
for x in ml:
    print(x)
```

### 5.3 上下文管理器

```python
class FileManager:
    """文件管理器，支持 with 语句"""
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        """进入 with 块时调用"""
        print(f"打开文件：{self.filename}")
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        """离开 with 块时调用"""
        print(f"关闭文件：{self.filename}")
        if self.file:
            self.file.close()
        # 返回 True 表示不抛出异常
        return False

# 使用
with FileManager('test.txt', 'w') as f:
    f.write('Hello, World!')
```

### 5.4 常用特殊方法一览

| 方法 | 触发场景 | 说明 |
|------|----------|------|
| `__init__` | 创建实例 | 初始化 |
| `__str__` | `print()` / `str()` | 用户友好字符串 |
| `__repr__` | 直接显示 / `repr()` | 开发调试字符串 |
| `__len__` | `len()` | 长度 |
| `__getitem__` | `obj[key]` | 索引访问 |
| `__setitem__` | `obj[key] = v` | 索引赋值 |
| `__delitem__` | `del obj[key]` | 索引删除 |
| `__contains__` | `in` | 成员判断 |
| `__iter__` | `for` / `iter()` | 迭代 |
| `__next__` | `next()` | 迭代下一项 |
| `__add__` | `+` | 加法 |
| `__sub__` | `-` | 减法 |
| `__mul__` | `*` | 乘法 |
| `__eq__` | `==` | 等于 |
| `__lt__` | `<` | 小于 |
| `__call__` | `obj()` | 调用对象 |
| `__enter__` / `__exit__` | `with` | 上下文管理 |

---

## 6. 静态方法和类方法

### 6.1 三种方法对比

```python
class MyClass:
    class_var = '类属性'

    def instance_method(self):
        """实例方法：第一个参数是 self（实例）"""
        return f"实例方法，访问 {self.class_var}"

    @classmethod
    def class_method(cls):
        """类方法：第一个参数是 cls（类）"""
        return f"类方法，访问 {cls.class_var}"

    @staticmethod
    def static_method():
        """静态方法：无 self/cls 参数"""
        return "静态方法，不访问类或实例"

obj = MyClass()

# 实例方法
print(obj.instance_method())   # 通过实例调用
# print(MyClass.instance_method())  # 报错，缺少 self

# 类方法
print(MyClass.class_method())  # 通过类调用
print(obj.class_method())      # 也可通过实例调用

# 静态方法
print(MyClass.static_method())
print(obj.static_method())
```

### 6.2 类方法的应用：工厂模式

```python
class Date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    @classmethod
    def from_string(cls, date_str):
        """从字符串创建：'2024-01-15'"""
        year, month, day = map(int, date_str.split('-'))
        return cls(year, month, day)

    @classmethod
    def today(cls):
        """创建今天的日期"""
        import datetime
        t = datetime.date.today()
        return cls(t.year, t.month, t.day)

    def __str__(self):
        return f"{self.year}-{self.month:02d}-{self.day:02d}"

d1 = Date(2024, 1, 15)
d2 = Date.from_string('2024-01-15')
d3 = Date.today()
print(d1, d2, d3)
```

### 6.3 静态方法的应用

```python
class MathUtils:
    """数学工具类"""
    @staticmethod
    def is_even(n):
        return n % 2 == 0

    @staticmethod
    def factorial(n):
        if n <= 1:
            return 1
        return n * MathUtils.factorial(n - 1)

print(MathUtils.is_even(4))      # True
print(MathUtils.factorial(5))    # 120
```

---

## 7. 枚举类

### 7.1 使用 enum 模块

```python
from enum import Enum, unique

@unique  # 确保值唯一
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

# 访问方式
print(Color.RED)           # Color.RED
print(Color.RED.name)      # 'RED'
print(Color.RED.value)     # 1
print(Color['RED'])        # Color.RED，通过名称访问
print(Color(1))            # Color.RED，通过值访问

# 遍历
for color in Color:
    print(color)

# 比较
print(Color.RED == Color.RED)     # True
print(Color.RED is Color.RED)     # True
# print(Color.RED < Color.GREEN)  # TypeError，不能比较大小
```

### 7.2 IntEnum

```python
from enum import IntEnum

class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

# IntEnum 可以比较大小
print(Priority.LOW < Priority.HIGH)  # True
print(Priority.HIGH > 2)             # True，可与整数比较
```

---

## 8. 数据类（dataclass）

### 8.1 Python 3.7+ 数据类

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class Student:
    name: str
    age: int
    scores: List[float] = field(default_factory=list)

    def average(self):
        return sum(self.scores) / len(self.scores) if self.scores else 0

# 自动生成 __init__, __repr__, __eq__
s1 = Student('Alice', 20, [85, 90, 78])
s2 = Student('Bob', 22, [92, 88, 95])

print(s1)                    # Student(name='Alice', age=20, scores=[85, 90, 78])
print(s1.average())          # 84.33...

# 不可变数据类
@dataclass(frozen=True)
class Point:
    x: float
    y: float

p = Point(1.0, 2.0)
# p.x = 3.0  # 报错！不可变
```

---

## 9. 综合应用示例

### 9.1 完整的类设计

```python
from dataclasses import dataclass, field
from typing import List
from abc import ABC, abstractmethod

# 抽象基类
class Shape(ABC):
    """图形基类"""
    @abstractmethod
    def area(self) -> float:
        """计算面积"""
        pass

    @abstractmethod
    def perimeter(self) -> float:
        """计算周长"""
        pass

    def __str__(self):
        return f"{self.__class__.__name__}(面积={self.area():.2f}, 周长={self.perimeter():.2f})"

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14159 * self.radius ** 2

    def perimeter(self):
        return 2 * 3.14159 * self.radius

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

# 使用多态
shapes = [Circle(5), Rectangle(3, 4), Circle(2)]
for shape in shapes:
    print(shape)
# Circle(面积=78.54, 周长=31.42)
# Rectangle(面积=12.00, 周长=14.00)
# Circle(面积=12.57, 周长=12.57)
```

### 9.2 单例模式

```python
class Singleton:
    """单例模式：一个类只有一个实例"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, value):
        if not hasattr(self, '_initialized'):
            self.value = value
            self._initialized = True

s1 = Singleton(1)
s2 = Singleton(2)
print(s1 is s2)     # True，同一实例
print(s1.value)     # 1，只初始化一次
```

---

## 10. 小结

### 10.1 核心要点

- **类是模板，实例是对象**：类定义属性和方法，实例是具体对象
- **封装**：用 `__` 前缀实现私有属性，用 `@property` 控制访问
- **继承**：子类继承父类，用 `super()` 调用父类方法
- **多态**：不同子类对同一方法有不同实现
- **特殊方法**：`__str__`、`__repr__`、`__add__` 等实现运算符重载
- **类方法**用 `@classmethod`，**静态方法**用 `@staticmethod`
- **优先使用组合而非继承**，降低耦合

### 10.2 方法选择指南

```
需要访问实例属性？ → 实例方法（def method(self)）
需要访问类属性/工厂方法？ → 类方法（@classmethod）
工具函数，与类无关？ → 静态方法（@staticmethod）
```

### 10.3 最佳实践

1. **类名用驼峰命名**：`MyClass`
2. **一个类只做一件事**：单一职责原则
3. **优先组合而非继承**：`has-a` 优于 `is-a`
4. **合理使用私有属性**：保护内部实现
5. **使用 `@property` 替代直接 getter/setter**
6. **数据类用 `@dataclass`**：减少样板代码
7. **使用类型提示**：提高可读性
