# Python 基础语法学习资料

> 本目录收录 Python 3.x 基础语法系统学习资料，按由浅入深的路径组织，每篇聚焦一个主题，包含概念解释、语法规则、可运行代码示例与综合应用。

## 📚 学习路径与文件索引

建议按以下顺序学习（序号即推荐学习顺序）：

| 序号 | 文档 | 核心内容 | 难度 |
|------|------|----------|------|
| 1 | [Python环境搭建与入门.md](./Python环境搭建与入门.md) | Python 简介、安装、解释器、第一个程序、代码规范、pip 与虚拟环境 | ⭐ |
| 2 | [Python基础语法详解.md](./Python基础语法详解.md) | 变量与数据类型、字符串与编码、运算符、条件判断、循环 | ⭐ |
| 3 | [Python数据结构详解.md](./Python数据结构详解.md) | list、tuple、dict、set 及其对比选择 | ⭐⭐ |
| 4 | [Python函数详解.md](./Python函数详解.md) | 函数定义、参数（位置/默认/可变/关键字）、递归、作用域、装饰器基础、偏函数 | ⭐⭐ |
| 5 | [Python高级特性详解.md](./Python高级特性详解.md) | 切片、迭代、列表推导式、生成器、迭代器 | ⭐⭐⭐ |
| 6 | [Python函数式编程详解.md](./Python函数式编程详解.md) | 高阶函数、Lambda、闭包、装饰器、偏函数、函数式工具 | ⭐⭐⭐ |
| 7 | [Python面向对象编程详解.md](./Python面向对象编程详解.md) | 类与实例、封装、继承多态、魔术方法、静态/类方法、枚举、dataclass | ⭐⭐⭐ |
| 8 | [Python面向对象高级编程详解.md](./Python面向对象高级编程详解.md) | `__slots__`、`@property`、多重继承与 Mixin、MRO、定制类、ABC、元类 | ⭐⭐⭐⭐ |
| 9 | [Python模块与错误处理详解.md](./Python模块与错误处理详解.md) | 模块与包、标准库、错误处理、调试与测试、logging | ⭐⭐⭐ |
| 10 | [PythonIO编程详解.md](./PythonIO编程详解.md) | 文件读写、with 语句、文件目录操作、StringIO/BytesIO、序列化 | ⭐⭐⭐ |
| 11 | [Python正则表达式详解.md](./Python正则表达式详解.md) | re 模块、元字符、分组捕获、贪婪非贪婪、零宽断言、实战案例 | ⭐⭐⭐ |
| 12 | [Python日期时间处理详解.md](./Python日期时间处理详解.md) | time/datetime/timedelta、格式化解析、时区处理、calendar | ⭐⭐⭐ |

## 🗺️ 知识体系图

```
环境搭建 → 基础语法 → 数据结构 → 函数
                                    ↓
                            高级特性 → 函数式编程
                                    ↓
                  面向对象基础 → 面向对象高级
                                    ↓
        模块与错误处理 → IO 编程 → 正则表达式 → 日期时间
```

## 🎯 各篇学习要点速览

### 1. 环境搭建与入门
- Python 3.x 跨平台安装，务必勾选 `Add Python to PATH`
- 缩进表示代码块（4 空格），遵循 PEP 8
- pip 管理第三方包，venv/conda 隔离依赖

### 2. 基础语法
- 动态类型，五大基本类型：int / float / str / bool / NoneType
- 运算符（含海象运算符 `:=`）、条件判断、循环（while / for-in）
- 判断 `None` 用 `is` 而非 `==`

### 3. 数据结构
- list 可变有序、tuple 不可变、dict 键值映射、set 去重集合
- 掌握推导式（list/dict/set comprehension）与解包

### 4. 函数
- 参数五种形式：位置、默认、可变位置 `*args`、关键字 `**kwargs`、仅关键字
- 可变默认参数陷阱（用 `None` 代替 `[]`）
- 类型提示（Type Hints）、`@functools.wraps` 装饰器

### 5. 高级特性
- 切片 `[start:stop:step]`、迭代协议 `__iter__`/`__next__`
- 列表推导式 vs 生成器表达式（内存差异）
- 生成器（yield）与迭代器

### 6. 函数式编程
- 高阶函数 map / filter / reduce（reduce 来自 functools）
- 闭包变量捕获陷阱、装饰器原理与 `@wraps`
- 偏函数 `functools.partial`

### 7. 面向对象基础
- 类与实例、`__init__`、访问限制（`_`/`__`）、继承与多态
- 魔术方法（`__str__`/`__repr__`/`__eq__` 等）
- `@staticmethod`/`@classmethod`、枚举 Enum、dataclass

### 8. 面向对象高级
- `__slots__` 限制属性省内存、`@property` 属性校验
- 多重继承与 Mixin、MRO 与 `super()` 真实行为
- 定制类（`__getattr__`/`__call__`/`__getitem__`）、ABC、元类

### 9. 模块与错误处理
- 模块导入（避免 `import *`）、包 `__init__.py`、`__name__ == '__main__'`
- try/except/else/finally、自定义异常、`raise ... from e`
- logging 日志、assert（`-O` 模式失效）、unittest/pytest

### 10. IO 编程
- 文件读写 `open()` 必带 `encoding`、`with` 上下文管理器
- pathlib 面向对象路径操作、StringIO/BytesIO
- JSON 序列化（安全）；⚠️ pickle 不安全，勿加载不可信数据

### 11. 正则表达式
- re 模块函数：match / search / findall / sub / split
- 元字符、预定义字符类、分组捕获（命名/非捕获/后向引用）
- 贪婪 vs 非贪婪、零宽断言、标志位、`re.compile` 预编译

### 12. 日期时间
- 三种表示：时间戳 / struct_time / 格式化字符串
- datetime 四类：date / time / datetime / timedelta
- strftime/strptime、ISO 8601、zoneinfo 时区（3.9+）
- `datetime.utcnow()` 已弃用，改用 `datetime.now(timezone.utc)`

## 📌 通用约定

- 所有示例基于 **Python 3.x**（建议 3.10+）
- 代码块标注语言标签，可直接复制运行
- `# ` 后为注释或运行结果
- ⚠️ 标记表示重要注意事项或常见陷阱

## 🔗 参考资源

- [Python 官方文档](https://docs.python.org/zh-cn/3/)
- [廖雪峰 Python 教程](https://liaoxuefeng.com/books/python/introduction/index.html)
- [PEP 8 代码风格指南](https://peps.python.org/pep-0008/)
- [正则表达式在线调试](https://regex101.com/)
