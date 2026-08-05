# Python 基础语法详解

## 1. 变量与数据类型

### 1.1 变量

Python 是动态类型语言，变量无需声明类型，直接赋值即可使用：

```python
# 变量赋值
name = "张三"        # 字符串
age = 25             # 整数
height = 1.75        # 浮点数
is_student = True    # 布尔值

# 多变量赋值
a, b, c = 1, 2, 3
x = y = z = 0

# 查看变量类型
print(type(name))      # <class 'str'>
print(type(age))       # <class 'int'>
```

**变量命名规则**：
- 只能包含字母、数字、下划线
- 不能以数字开头
- 不能使用关键字（如 `if`、`for`、`class`）
- 区分大小写

### 1.2 基本数据类型

| 类型 | 关键字 | 示例 | 说明 |
|------|--------|------|------|
| 整数 | `int` | `100`, `-5`, `0` | 任意大小，无溢出 |
| 浮点数 | `float` | `3.14`, `-0.5` | 64位双精度 |
| 字符串 | `str` | `"Hello"` | 不可变序列 |
| 布尔值 | `bool` | `True`, `False` | 真值类型 |
| 空值 | `NoneType` | `None` | 表示没有值 |

```python
# 整数：支持任意大小
big_number = 10 ** 100
print(big_number)

# 浮点数：注意精度问题
print(0.1 + 0.2)  # 0.30000000000000004

# 使用 Decimal 处理精确小数
from decimal import Decimal
print(Decimal('0.1') + Decimal('0.2'))  # 0.3

# 布尔值
print(True + True)  # 2，True 等价于 1
print(False + 1)    # 1，False 等价于 0
```

### 1.3 类型转换

```python
# 自动转换（低精度 → 高精度）
result = 10 + 3.14   # int + float → float
print(result)        # 13.14

# 强制转换
int_num = int("123")       # 字符串 → 整数：123
float_num = float("3.14")  # 字符串 → 浮点数：3.14
str_num = str(100)         # 整数 → 字符串："100"
bool_val = bool(0)         # 0 → False
bool_val2 = bool("")       # 空字符串 → False
bool_val3 = bool([1, 2])   # 非空列表 → True
```

**假值（Falsy）列表**：
- `False`、`None`
- `0`、`0.0`
- `""`（空字符串）
- `[]`、`{}`、`()`（空容器）
- `set()`

---

## 2. 字符串与编码

### 2.1 字符串基础

Python 字符串是**不可变**的字符序列，可用单引号、双引号或三引号表示：

```python
s1 = 'Hello'
s2 = "World"
s3 = '''多行
字符串'''
s4 = """也是多行
字符串"""

# 转义字符
print("Hello\tWorld")     # 制表符
print("Hello\nWorld")     # 换行
print("路径：C:\\Users")   # 反斜杠
print("It's a book")      # 单引号内用双引号，无需转义
```

### 2.2 字符串编码

计算机只能处理数字，文本字符需要编码为字节。常见编码：

| 编码 | 特点 | 字节数 |
|------|------|--------|
| ASCII | 英文+控制字符 | 1字节 |
| UTF-8 | 万国码，可变长 | 1-4字节 |
| GBK | 中文编码 | 2字节（中文） |

**编码与解码**：

```python
# 字符串（str）↔ 字节（bytes）转换
s = "中文"
print(type(s))  # <class 'str'>

# 编码：str → bytes
b = s.encode('utf-8')
print(b)         # b'\xe4\xb8\xad\xe6\x96\x87'
print(type(b))   # <class 'bytes'>

# 解码：bytes → str
s2 = b.decode('utf-8')
print(s2)        # 中文

# 指定编码读取文件
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()
```

### 2.3 字符串格式化

```python
# 方式1：% 格式化（旧式）
name = "张三"
age = 25
print("我叫%s，今年%d岁" % (name, age))

# 方式2：str.format()
print("我叫{}，今年{}岁".format(name, age))
print("我叫{0}，{0}今年{1}岁".format(name, age))
print("我叫{name}，今年{age}岁".format(name="李四", age=30))

# 方式3：f-string（Python 3.6+，推荐）
print(f"我叫{name}，今年{age}岁")

# 格式化数字
pi = 3.14159265
print(f"π = {pi:.2f}")        # 保留2位小数：3.14
print(f"π = {pi:10.4f}")      # 总宽10，保留4位：    3.1416
print(f"百分比：{0.85:.1%}")  # 百分比：85.0%
print(f"数字：{42:05d}")      # 补零：00042
```

### 2.4 字符串常用方法

```python
s = "  Hello, World  "

# 大小写转换
print(s.upper())        # "  HELLO, WORLD  "
print(s.lower())        # "  hello, world  "
print(s.title())        # "  Hello, World  "
print(s.capitalize())   # "  hello, world  "
print(s.swapcase())     # 大小写互换

# 去除空白
print(s.strip())    # "Hello, World"
print(s.lstrip())   # 去左空白
print(s.rstrip())   # 去右空白

# 查找与替换
print(s.find("World"))   # 返回索引，找不到返回-1
print(s.index("World"))  # 同 find，但找不到抛异常
print(s.replace("World", "Python"))

# 分割与合并
csv = "a,b,c,d"
parts = csv.split(",")       # ['a', 'b', 'c', 'd']
joined = "-".join(parts)     # "a-b-c-d"

# 判断方法
print("123".isdigit())       # True，是否全数字
print("abc".isalpha())       # True，是否全字母
print("abc123".isalnum())    # True，是否全字母数字
print("Hello".startswith("He"))  # True
print("Hello".endswith("lo"))    # True
```

### 2.5 字符串切片

```python
s = "Hello, World"

print(s[0])       # 'H'，第一个字符
print(s[-1])      # 'd'，最后一个字符
print(s[0:5])     # 'Hello'，切片 [0,5)
print(s[:5])      # 'Hello'，省略开头
print(s[7:])      # 'World'，省略结尾
print(s[:])       # 完整副本
print(s[::2])     # 'HloWrd'，步长为2
print(s[::-1])    # 'dlroW ,olleH'，反转字符串
```

---

## 3. 运算符

### 3.1 算术运算符

```python
print(10 + 3)   # 13，加
print(10 - 3)   # 7，减
print(10 * 3)   # 30，乘
print(10 / 3)   # 3.333...，除（返回浮点数）
print(10 // 3)  # 3，地板除（向下取整）
print(10 % 3)   # 1，取余
print(10 ** 3)  # 1000，幂运算
print(2 ** 0.5) # 1.414...，开平方

# 字符串和列表的运算
print("ab" + "cd")    # "abcd"，拼接
print("ab" * 3)       # "ababab"，重复
print([1, 2] + [3])   # [1, 2, 3]
print([0] * 5)        # [0, 0, 0, 0, 0]
```

### 3.2 比较运算符

```python
print(3 > 2)       # True
print(3 < 2)       # False
print(3 == 3)      # True，相等
print(3 != 4)      # True，不等
print(3 >= 3)      # True
print(3 <= 2)      # False

# 链式比较
x = 5
print(1 < x < 10)  # True，等价于 1 < x and x < 10
```

### 3.3 逻辑运算符

```python
# and：都为 True 才 True
print(True and False)   # False
print(True and True)    # True

# or：有一个 True 就 True
print(True or False)    # True

# not：取反
print(not True)         # False

# 短路特性
x = 0
print(x != 0 and 10 / x > 1)  # False，短路避免除零错误

# 真值判断：直接判断变量真假
name = ""
if name:
    print("非空")
else:
    print("空字符串")  # 输出这个
```

### 3.4 成员与身份运算符

```python
# in：判断是否包含
print("a" in "abc")          # True
print(3 in [1, 2, 3])        # True
print("name" in {"name": "张三"})  # True，判断键

# not in：判断是否不包含
print(5 not in [1, 2, 3])    # True

# is：判断是否同一对象（内存地址）
a = [1, 2]
b = [1, 2]
c = a
print(a == b)   # True，值相等
print(a is b)   # False，不同对象
print(a is c)   # True，同一对象

# None 判断
x = None
print(x is None)  # True，推荐用法
```

### 3.5 赋值运算符

```python
x = 10
x += 5    # x = x + 5 → 15
x -= 3    # x = x - 3 → 12
x *= 2    # x = x * 2 → 24
x /= 4    # x = x / 4 → 6.0
x //= 2   # x = x // 2 → 3.0
x %= 2    # x = x % 2 → 1.0
x **= 3   # x = x ** 3 → 1.0

# 海象运算符 :=（Python 3.8+）
if (n := len("hello")) > 3:
    print(f"长度 {n} 超过3")
```

---

## 4. 条件判断

### 4.1 if 语句

```python
age = 18

if age >= 18:
    print("成年")
elif age >= 12:
    print("青少年")
else:
    print("儿童")
```

### 4.2 if 表达式（三元运算符）

```python
score = 85

# 传统写法
if score >= 60:
    result = "及格"
else:
    result = "不及格"

# 三元表达式（推荐）
result = "及格" if score >= 60 else "不及格"
print(result)

# 嵌套使用
level = "优" if score >= 90 else ("良" if score >= 80 else "中")
```

### 4.3 条件判断的简写

```python
# 多条件判断
x = 5

# 使用 and / or
if x > 0 and x < 10:
    print("0-10之间")

# 使用链式比较（更简洁）
if 0 < x < 10:
    print("0-10之间")

# 使用 in 判断多个值
if x in [1, 2, 3, 4, 5]:
    print("在列表中")

# 使用 any / all
conditions = [x > 0, x < 10, x != 5]
if all(conditions):
    print("所有条件满足")
if any(conditions):
    print("至少一个条件满足")
```

### 4.4 match-case 语句（Python 3.10+）

```python
def handle_command(command):
    match command.split():
        case ["quit"]:
            print("退出")
        case ["go", direction]:
            print(f"向{direction}移动")
        case ["drop", *items]:
            print(f"丢弃：{items}")
        case _:
            print("未知命令")

handle_command("go north")   # 向north移动
handle_command("drop sword shield")  # 丢弃：['sword', 'shield']
```

---

## 5. 循环

### 5.1 for 循环

```python
# 遍历列表
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# 遍历字符串
for char in "Hello":
    print(char)

# 使用 range()
for i in range(5):        # 0, 1, 2, 3, 4
    print(i)
for i in range(2, 8):     # 2, 3, 4, 5, 6, 7
    print(i)
for i in range(0, 10, 2): # 0, 2, 4, 6, 8
    print(i)

# enumerate：同时获取索引和值
for index, value in enumerate(fruits):
    print(f"{index}: {value}")
```

### 5.2 while 循环

```python
# 基本用法
count = 0
while count < 5:
    print(f"第 {count + 1} 次")
    count += 1

# 猜数字游戏
import random
target = random.randint(1, 100)
while True:
    guess = int(input("猜一个数字（1-100）："))
    if guess < target:
        print("小了")
    elif guess > target:
        print("大了")
    else:
        print("猜对了！")
        break
```

### 5.3 break 与 continue

```python
# break：跳出整个循环
for i in range(10):
    if i == 5:
        break    # i=5 时结束循环
    print(i)     # 输出 0,1,2,3,4

# continue：跳过本次，进入下次
for i in range(10):
    if i % 2 == 0:
        continue  # 跳过偶数
    print(i)      # 输出 1,3,5,7,9

# 循环的 else 子句（正常结束才执行）
for i in range(5):
    if i == 10:
        break
else:
    print("循环正常结束，没有 break")  # 会执行
```

### 5.4 嵌套循环

```python
# 九九乘法表
for i in range(1, 10):
    for j in range(1, i + 1):
        print(f"{j}×{i}={i*j}", end="\t")
    print()  # 换行

# 输出：
# 1×1=1
# 1×2=2  2×2=4
# 1×3=3  2×3=6  3×3=9
# ...
```

### 5.5 循环的常见模式

```python
# 累加求和
total = 0
for i in range(1, 101):
    total += i
print(f"1到100的和：{total}")  # 5050

# 查找元素
numbers = [3, 7, 2, 9, 5]
target = 9
found = False
for num in numbers:
    if num == target:
        found = True
        break

# 使用 Python 风格
found = target in numbers

# 同时遍历多个序列
names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]
for name, age in zip(names, ages):
    print(f"{name}: {age}岁")

# 无限循环 + 用户输入
while True:
    text = input("输入 quit 退出：")
    if text == "quit":
        break
    print(f"你输入了：{text}")
```

---

## 6. 小结

### 6.1 核心要点

- Python 是**动态类型**语言，变量无需声明类型
- 基本数据类型：`int`、`float`、`str`、`bool`、`NoneType`
- 字符串是**不可变**的，操作后返回新字符串
- 字符编码推荐使用 **UTF-8**，处理中文时务必指定编码
- 字符串格式化优先使用 **f-string**（Python 3.6+）
- 条件判断可用 `if-elif-else`，支持链式比较和 `in` 判断
- `for` 循环用于遍历可迭代对象，`while` 用于条件循环
- `break` 跳出循环，`continue` 跳过本次

### 6.2 易错点

| 易错点 | 说明 |
|--------|------|
| `==` vs `is` | `==` 比较值，`is` 比较内存地址 |
| `/` vs `//` | `/` 返回浮点数，`//` 地板除 |
| 可变与不可变 | 字符串不可变，修改返回新对象 |
| 浮点数精度 | `0.1 + 0.2 != 0.3`，用 `Decimal` |
| 短路求值 | `and` 前为 False 不计算后，`or` 前为 True 不计算后 |

### 6.3 速查表

```python
# 类型转换
int(x)        # 转整数
float(x)      # 转浮点数
str(x)        # 转字符串
bool(x)       # 转布尔值
list(x)       # 转列表
type(x)       # 查看类型
isinstance(x, int)  # 判断类型

# 字符串方法
s.upper() / s.lower()     # 大小写
s.strip()                 # 去空白
s.split(sep)              # 分割
sep.join(list)            # 合并
s.replace(old, new)       # 替换
s.find(sub)               # 查找

# 循环
for x in iterable:        # for 循环
while condition:          # while 循环
range(start, stop, step)  # 生成数字序列
enumerate(iterable)       # 带索引遍历
zip(iter1, iter2)         # 并行遍历
```
