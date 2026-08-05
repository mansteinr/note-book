# Python 模块与错误处理详解

## 1. 模块基础

### 1.1 什么是模块

在 Python 中，一个 `.py` 文件就称为一个模块（Module）。模块的好处：

- **提高代码可维护性**：将相关功能组织在一起
- **代码复用**：可在不同程序中导入使用
- **避免命名冲突**：模块形成独立的命名空间
- **按需加载**：提升启动速度

### 1.2 创建模块

创建一个 `my_math.py` 文件：

```python
# my_math.py
"""自定义数学工具模块"""

PI = 3.141592653589793

def square(x):
    """计算平方"""
    return x * x

def cube(x):
    """计算立方"""
    return x * x * x

class Calculator:
    """计算器类"""
    def __init__(self, name):
        self.name = name

    def add(self, a, b):
        return a + b

if __name__ == '__main__':
    # 仅在直接运行此文件时执行，被导入时不执行
    print(f"square(5) = {square(5)}")
    print(f"cube(3) = {cube(3)}")
```

### 1.3 导入模块

```python
# 方式1：导入整个模块
import my_math
print(my_math.square(5))          # 25
print(my_math.PI)                 # 3.14159...
calc = my_math.Calculator('Test')

# 方式2：导入特定内容
from my_math import square, cube, PI
print(square(5))                  # 25
print(PI)                         # 3.14159...

# 方式3：导入并起别名
import my_math as mm
print(mm.square(5))

from my_math import square as sq
print(sq(5))

# 方式4：导入所有内容（不推荐，可能冲突）
from my_math import *
print(square(5))
```

### 1.4 `__name__` 的作用

```python
# 每个模块都有 __name__ 属性
# 直接运行时：__name__ == '__main__'
# 被导入时：__name__ == '模块名'

if __name__ == '__main__':
    # 这里的代码只在直接运行时执行
    # 被导入时不执行，常用于测试代码
    print("正在测试模块")
```

---

## 2. 包（Package）

### 2.1 什么是包

包是包含多个模块的目录，通过**点分路径**访问。包目录下必须有 `__init__.py` 文件（Python 3.3+ 可省略，但建议保留）。

```
my_package/
├── __init__.py          # 包初始化文件
├── module1.py
├── module2.py
└── subpackage/
    ├── __init__.py
    └── module3.py
```

### 2.2 创建和使用包

```python
# my_package/__init__.py
"""包的初始化文件"""
print("my_package 被导入")

# 可以在这里定义包级别的初始化代码
__version__ = '1.0.0'

# my_package/module1.py
def func1():
    return "这是 module1 的函数"

# my_package/module2.py
def func2():
    return "这是 module2 的函数"

# 使用包
import my_package.module1
my_package.module1.func1()

from my_package import module1, module2
module1.func1()
module2.func2()

from my_package.module1 import func1
func1()
```

### 2.3 `__init__.py` 的作用

```python
# my_package/__init__.py
"""控制包的导入行为"""

# 方式1：暴露子模块
from .module1 import func1
from .module2 import func2

# 这样用户可以直接：from my_package import func1, func2

# 方式2：使用 __all__ 控制导入范围
__all__ = ['module1', 'module2', 'func1']

# 定义包级别变量
__version__ = '1.0.0'
__author__ = 'Author Name'
```

---

## 3. 常用标准库

### 3.1 常用标准库一览

| 模块 | 用途 | 示例 |
|------|------|------|
| `os` | 操作系统接口 | 文件/目录操作 |
| `sys` | Python 解释器交互 | 命令行参数 |
| `datetime` | 日期时间处理 | 时间计算 |
| `json` | JSON 编解码 | 数据序列化 |
| `re` | 正则表达式 | 字符串匹配 |
| `math` | 数学函数 | 三角函数等 |
| `random` | 随机数 | 生成随机数 |
| `collections` | 高级数据结构 | Counter, defaultdict |
| `itertools` | 迭代工具 | 排列组合 |
| `functools` | 函数工具 | 装饰器, 缓存 |
| `pathlib` | 路径处理 | 现代文件路径API |
| `logging` | 日志记录 | 程序日志 |

### 3.2 常用模块示例

```python
# os 模块：操作系统接口
import os

# 路径操作
print(os.getcwd())              # 当前工作目录
print(os.path.join('a', 'b', 'c'))  # 拼接路径
print(os.path.exists('test.txt'))   # 文件是否存在
print(os.path.isdir('mydir'))       # 是否是目录

# 文件操作
os.mkdir('newdir')               # 创建目录
os.makedirs('a/b/c')             # 递归创建
os.rename('old.txt', 'new.txt')  # 重命名
os.remove('file.txt')            # 删除文件

# 环境变量
print(os.environ.get('PATH'))

# sys 模块
import sys

print(sys.version)              # Python 版本
print(sys.platform)             # 操作系统平台
print(sys.argv)                 # 命令行参数
sys.exit(0)                     # 退出程序

# datetime 模块
from datetime import datetime, date, timedelta

now = datetime.now()            # 当前时间
today = date.today()            # 今天
tomorrow = today + timedelta(days=1)  # 明天
formatted = now.strftime('%Y-%m-%d %H:%M:%S')

# json 模块
import json

data = {'name': 'Alice', 'age': 25}
json_str = json.dumps(data)     # 字典 → JSON 字符串
parsed = json.loads(json_str)   # JSON 字符串 → 字典

# 读写 JSON 文件
with open('data.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open('data.json') as f:
    data = json.load(f)

# collections 模块
from collections import Counter, defaultdict, OrderedDict, namedtuple

# Counter：计数器
words = ['apple', 'banana', 'apple', 'cherry', 'banana', 'apple']
counter = Counter(words)
print(counter.most_common(2))  # [('apple', 3), ('banana', 2)]

# defaultdict：带默认值的字典
dd = defaultdict(list)
dd['a'].append(1)  # 自动创建空列表
dd['a'].append(2)

# namedtuple：具名元组
Point = namedtuple('Point', ['x', 'y'])
p = Point(3, 4)
print(p.x, p.y)  # 3 4

# pathlib 模块（推荐替代 os.path）
from pathlib import Path

p = Path('.')
print(list(p.glob('*.py')))      # 当前目录的 .py 文件
p = Path('test.txt')
print(p.exists())                # 是否存在
print(p.suffix)                  # 文件后缀
print(p.stem)                    # 文件名（不含后缀）
```

### 3.3 安装第三方模块

```bash
# 使用 pip 安装
pip install requests
pip install numpy pandas matplotlib

# 指定版本
pip install requests==2.28.0

# 使用 requirements.txt
pip install -r requirements.txt
```

```python
# 使用第三方库示例
import requests

response = requests.get('https://api.github.com')
print(response.status_code)  # 200
print(response.json())       # 解析 JSON 响应
```

---

## 4. 错误处理

### 4.1 错误类型

Python 的错误分为两类：

- **语法错误（SyntaxError）**：代码不符合语法规则，运行前就能发现
- **异常（Exception）**：运行时发生的错误

```python
# 语法错误
# print("hello)  # SyntaxError: 未闭合的字符串

# 常见异常
print(10 / 0)           # ZeroDivisionError
print(unknown_var)      # NameError
print([1, 2][10])       # IndexError
print({'a': 1}['b'])    # KeyError
print(int("abc"))       # ValueError
print(1 + "2")          # TypeError
open("not_exist.txt")   # FileNotFoundError
```

### 4.2 try-except 语句

```python
# 基本用法
try:
    result = 10 / 0
except ZeroDivisionError:
    print("不能除以零！")

# 捕获多种异常
try:
    value = int(input("输入数字："))
    result = 100 / value
except ValueError:
    print("输入的不是数字")
except ZeroDivisionError:
    print("不能除以零")
except Exception as e:
    print(f"其他错误：{e}")

# 捕获异常信息
try:
    [1, 2][10]
except IndexError as e:
    print(f"错误类型：{type(e).__name__}")  # IndexError
    print(f"错误信息：{e}")                  # list index out of range
```

### 4.3 try-except-else-finally

```python
try:
    # 可能出错的代码
    f = open('data.txt')
    content = f.read()
except FileNotFoundError:
    print("文件不存在")
except IOError as e:
    print(f"读取错误：{e}")
else:
    # 没有异常时执行
    print(f"读取成功：{len(content)} 字符")
finally:
    # 无论是否异常都执行（清理资源）
    if 'f' in locals():
        f.close()
    print("清理完成")
```

**执行流程**：

```
try → 异常？ → except（处理） → finally
    ↓否
    else（无异常时执行） → finally
```

### 4.4 抛出异常

```python
def set_age(age):
    if not isinstance(age, int):
        raise TypeError("age 必须是整数")
    if age < 0 or age > 150:
        raise ValueError("age 必须在 0-150 之间")
    return age

# 自定义异常信息
try:
    set_age(-5)
except ValueError as e:
    print(f"设置失败：{e}")

# 重新抛出
def process_data(data):
    try:
        result = parse(data)
    except ValueError:
        print("记录错误日志")
        raise  # 重新抛出当前异常
```

### 4.5 自定义异常

```python
class AppError(Exception):
    """应用基础异常"""
    pass

class ValidationError(AppError):
    """数据验证异常"""
    def __init__(self, field, message):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

class NotFoundError(AppError):
    """资源未找到异常"""
    pass

# 使用自定义异常
def get_user(user_id):
    if user_id < 0:
        raise ValidationError('user_id', '不能为负数')
    user = find_in_db(user_id)
    if user is None:
        raise NotFoundError(f"用户 {user_id} 不存在")
    return user

# 捕获自定义异常
try:
    user = get_user(-1)
except ValidationError as e:
    print(f"验证错误：{e.field} - {e.message}")
except NotFoundError as e:
    print(f"未找到：{e}")
except AppError as e:
    # 捕获所有应用异常
    print(f"应用错误：{e}")
```

### 4.6 异常链

```python
def parse_config(filename):
    try:
        with open(filename) as f:
            return json.load(f)
    except FileNotFoundError as e:
        # raise from：保留原始异常链
        raise ConfigError(f"配置文件 {filename} 不存在") from e
    except json.JSONDecodeError as e:
        raise ConfigError(f"配置文件格式错误") from e

class ConfigError(Exception):
    pass

try:
    config = parse_config('config.json')
except ConfigError as e:
    print(f"错误：{e}")
    print(f"原因：{e.__cause__}")  # 原始异常
```

### 4.7 异常处理最佳实践

```python
# 1. 不要捕获所有异常（避免隐藏 bug）
# 错误
try:
    do_something()
except:  # 捕获所有异常，包括 KeyboardInterrupt
    pass

# 正确：捕获具体异常
try:
    do_something()
except (ValueError, TypeError) as e:
    logger.error(f"处理失败：{e}")

# 2. 不要用异常处理替代条件判断
# 错误
try:
    value = d['key']
except KeyError:
    value = None

# 正确
value = d.get('key')

# 3. 资源管理用 with 语句
# 错误
try:
    f = open('file.txt')
    content = f.read()
finally:
    f.close()

# 正确
with open('file.txt') as f:
    content = f.read()
```

---

## 5. 调试与测试

### 5.1 print 调试

```python
def calculate(data):
    print(f"[DEBUG] 输入数据：{data}")  # 调试输出
    result = sum(data) / len(data)
    print(f"[DEBUG] 计算结果：{result}")
    return result

# 使用 logging 替代 print
import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def calculate(data):
    logging.debug(f"输入数据：{data}")
    result = sum(data) / len(data)
    logging.debug(f"计算结果：{result}")
    return result
```

### 5.2 使用 logging 模块

```python
import logging

# 基本配置
logging.basicConfig(
    level=logging.DEBUG,  # 日志级别
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    filename='app.log',   # 输出到文件
)

logger = logging.getLogger(__name__)

# 日志级别（从低到高）
logger.debug("调试信息")      # 详细信息
logger.info("一般信息")       # 确认程序正常工作
logger.warning("警告")        # 可能有问题
logger.error("错误")          # 程序出错
logger.critical("严重错误")   # 程序可能无法继续

# 异常日志
try:
    1 / 0
except:
    logger.exception("发生异常")  # 自动包含堆栈信息
```

### 5.3 使用断言

```python
def divide(a, b):
    # assert 条件, 错误信息
    assert b != 0, "除数不能为零"
    return a / b

# 断言失败时抛出 AssertionError
# divide(10, 0)  # AssertionError: 除数不能为零

# 注意：断言可用于调试，但不要用于生产环境的错误处理
# 因为 Python -O 模式会忽略断言
```

### 5.4 单元测试

```python
# 使用 unittest 模块
import unittest

def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b

class TestMathFunctions(unittest.TestCase):
    """数学函数的测试类"""

    def test_add(self):
        # 测试加法
        self.assertEqual(add(1, 2), 3)
        self.assertEqual(add(-1, 1), 0)
        self.assertEqual(add(0, 0), 0)

    def test_divide(self):
        # 测试除法
        self.assertEqual(divide(10, 2), 5)
        self.assertAlmostEqual(divide(1, 3), 0.3333, places=4)

        # 测试异常
        with self.assertRaises(ValueError):
            divide(10, 0)

    def setUp(self):
        """每个测试方法前执行"""
        print("测试开始")

    def tearDown(self):
        """每个测试方法后执行"""
        print("测试结束")

# 运行测试
if __name__ == '__main__':
    unittest.main()
```

### 5.5 pytest（第三方测试框架）

```python
# test_math.py（pytest 风格，更简洁）
import pytest

def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b

def test_add():
    assert add(1, 2) == 3
    assert add(-1, 1) == 0

def test_divide():
    assert divide(10, 2) == 5

def test_divide_zero():
    with pytest.raises(ValueError):
        divide(10, 0)

# 参数化测试
@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add_parametrize(a, b, expected):
    assert add(a, b) == expected

# 运行：pytest test_math.py -v
```

---

## 6. 综合应用示例

### 6.1 配置文件管理

```python
"""config_manager.py - 配置文件管理模块"""
import json
import os
from pathlib import Path

class ConfigManager:
    """配置管理器"""

    DEFAULT_CONFIG = {
        'app_name': 'MyApp',
        'version': '1.0.0',
        'debug': False,
        'max_connections': 10,
    }

    def __init__(self, config_path='config.json'):
        self.config_path = Path(config_path)
        self.config = self.DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        """加载配置"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
        except json.JSONDecodeError as e:
            raise ConfigError(f"配置文件格式错误：{e}")
        except IOError as e:
            raise ConfigError(f"读取配置失败：{e}")

    def save(self):
        """保存配置"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except IOError as e:
            raise ConfigError(f"保存配置失败：{e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value

class ConfigError(Exception):
    """配置错误"""
    pass

# 使用
if __name__ == '__main__':
    try:
        config = ConfigManager('app_config.json')
        print(config.get('app_name'))
        config.set('debug', True)
        config.save()
    except ConfigError as e:
        print(f"配置错误：{e}")
```

### 6.2 带日志和错误处理的工具

```python
"""file_processor.py - 文件处理工具"""
import logging
from pathlib import Path
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileProcessor:
    def __init__(self, base_dir='.'):
        self.base_dir = Path(base_dir)

    def process_files(self, pattern='*.txt') -> List[str]:
        """处理匹配的所有文件"""
        results = []
        files = list(self.base_dir.glob(pattern))

        if not files:
            logger.warning(f"未找到匹配 {pattern} 的文件")
            return results

        for filepath in files:
            try:
                content = self.read_file(filepath)
                word_count = len(content.split())
                results.append(f"{filepath.name}: {word_count} 词")
                logger.info(f"处理完成：{filepath.name}")
            except FileNotFoundError:
                logger.error(f"文件不存在：{filepath}")
            except PermissionError:
                logger.error(f"无权限访问：{filepath}")
            except Exception as e:
                logger.exception(f"处理 {filepath} 时发生未知错误：{e}")

        return results

    def read_file(self, filepath):
        """读取文件内容"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

if __name__ == '__main__':
    processor = FileProcessor('.')
    results = processor.process_files('*.py')
    for r in results:
        print(r)
```

---

## 7. 小结

### 7.1 核心要点

- **模块**是 `.py` 文件，**包**是含 `__init__.py` 的目录
- 使用 `import` 导入模块，`from ... import` 导入特定内容
- `if __name__ == '__main__'` 区分直接运行和被导入
- 错误分为**语法错误**和**异常**
- `try-except-else-finally` 处理异常
- `raise` 抛出异常，可自定义异常类
- **优先用 `with` 语句**管理资源
- 使用 `logging` 模块记录日志，替代 `print`
- 使用 `unittest` 或 `pytest` 编写单元测试

### 7.2 异常处理原则

```
1. 捕获具体异常，不要裸 except
2. 在合适的位置处理异常（知道如何处理的地方）
3. 记录异常日志，便于排查
4. 清理资源放在 finally
5. 不要用异常替代条件判断
```

### 7.3 常用标准库速查

```python
# 文件/系统
import os, sys
from pathlib import Path

# 时间
from datetime import datetime, timedelta

# 数据处理
import json
import re
import math

# 数据结构
from collections import Counter, defaultdict, namedtuple, deque

# 函数工具
from functools import lru_cache, partial, wraps
import itertools

# 日志与调试
import logging
import pdb  # 调试器
```
