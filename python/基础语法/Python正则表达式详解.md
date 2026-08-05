# Python 正则表达式详解

## 1. 正则表达式概述

### 1.1 什么是正则表达式

正则表达式（Regular Expression，简称 regex）是一种描述字符串模式的**微型语言**，用于在文本中进行匹配、查找、替换等操作。它通过一组特殊的元字符组合成"模式字符串"，再用该模式去匹配目标文本。

**典型应用场景**：

- **数据校验**：校验邮箱、手机号、身份证号、密码强度等格式
- **文本提取**：从日志、网页中提取特定信息
- **文本替换**：批量修改符合规则的字符串
- **字符串拆分**：按复杂规则切分字符串

### 1.2 Python 中的 re 模块

Python 内置 `re` 模块提供正则表达式支持，所有功能都基于该模块：

```python
import re

# 最简单的匹配示例
m = re.match(r'Hello', 'Hello, World')
if m:
    print(m.group())   # Hello
    print(m.span())    # (0, 5)
```

> **提示**：正则模式字符串建议使用 **原始字符串**（前缀 `r`），避免反斜杠被 Python 转义。例如 `r'\d'` 表示数字字符，而 `'\d'` 在某些情况下会被解释为无效转义（Python 3.12+ 会产生 DeprecationWarning）。

---

## 2. re 模块核心函数

### 2.1 常用函数一览

| 函数 | 说明 | 返回值 |
|------|------|--------|
| `re.match(pattern, string)` | 从**字符串开头**匹配 | Match 对象或 None |
| `re.fullmatch(pattern, string)` | 要求**整个字符串**完全匹配 | Match 对象或 None |
| `re.search(pattern, string)` | 扫描**整个字符串**找第一个匹配 | Match 对象或 None |
| `re.findall(pattern, string)` | 返回**所有**匹配的子串 | 字符串列表 |
| `re.finditer(pattern, string)` | 返回所有匹配的迭代器 | Match 对象迭代器 |
| `re.sub(pattern, repl, string)` | 替换所有匹配子串 | 新字符串 |
| `re.subn(pattern, repl, string)` | 替换并返回替换次数 | (新字符串, 次数) |
| `re.split(pattern, string)` | 按模式拆分字符串 | 列表 |

### 2.2 match 与 search 的区别

```python
import re

text = "Python 3.13 released"

# match 只从开头匹配
m1 = re.match(r'\d+', text)
print(m1)                  # None（开头不是数字）

# search 扫描整个字符串
m2 = re.search(r'\d+', text)
print(m2.group())          # 3
print(m2.group())          # 实际匹配 "3.13" 中的 "3"？见下文说明
```

> **注意**：`\d+` 是贪婪匹配，上例中 `search` 实际匹配到的是 `3.13` 中连续数字部分 `"3"` 吗？并非如此——`.` 不是数字，所以 `\d+` 只匹配到 `"3"`。若要匹配 `3.13`，需要模式 `\d+\.\d+`。

```python
m = re.search(r'\d+\.\d+', text)
print(m.group())   # 3.13
```

### 2.3 Match 对象的常用方法

```python
m = re.search(r'(\d+)\.(\d+)', 'Python 3.13 released')
m.group()       # '3.13'   整个匹配
m.group(1)      # '3'      第 1 个分组
m.group(2)      # '13'     第 2 个分组
m.groups()      # ('3', '13')  所有分组
m.start()       # 7   匹配起始位置
m.end()         # 11  匹配结束位置
m.span()        # (7, 11)
```

### 2.4 findall 与分组的关系

`findall` 的返回值受模式中**分组数量**影响，这是常见坑点：

```python
import re

s = "2026-08-05 and 2026-12-31"

# 无分组：返回匹配的整个子串列表
print(re.findall(r'\d{4}-\d{2}-\d{2}', s))
# ['2026-08-05', '2026-12-31']

# 有 1 个分组：返回该分组内容列表
print(re.findall(r'\d{4}-(\d{2})-\d{2}', s))
# ['08', '12']

# 有多个分组：返回由各分组组成的元组列表
print(re.findall(r'(\d{4})-(\d{2})-(\d{2})', s))
# [('2026', '08', '05'), ('2026', '12', '31')]

# 想要"整个匹配"但又不影响分组：用非捕获分组 (?:)
print(re.findall(r'(?:\d{4})-(?:\d{2})-(?:\d{2})', s))
# ['2026-08-05', '2026-12-31']
```

---

## 3. 基本元字符与语法

### 3.1 元字符速查表

| 元字符 | 含义 | 示例 | 匹配 |
|--------|------|------|------|
| `.` | 匹配除换行符外任意一个字符 | `a.c` | `abc`, `a1c` |
| `^` | 匹配字符串开头 | `^Hello` | 以 Hello 开头 |
| `$` | 匹配字符串结尾 | `world$` | 以 world 结尾 |
| `*` | 前一个字符出现 0 次或多次 | `ab*c` | `ac`, `abc`, `abbbc` |
| `+` | 前一个字符出现 1 次或多次 | `ab+c` | `abc`, `abbbc` |
| `?` | 前一个字符出现 0 次或 1 次 | `ab?c` | `ac`, `abc` |
| `{n}` | 恰好出现 n 次 | `\d{4}` | 4 位数字 |
| `{n,}` | 至少出现 n 次 | `\d{2,}` | 2 位及以上数字 |
| `{n,m}` | 出现 n 到 m 次 | `\d{2,4}` | 2~4 位数字 |
| `[]` | 字符集合，匹配其中任意一个 | `[aeiou]` | 任一元音 |
| `[^]` | 否定字符集合 | `[^0-9]` | 非数字 |
| `|` | 或 | `cat\|dog` | cat 或 dog |
| `()` | 分组与捕获 | `(ab)+` | ab, abab |
| `\` | 转义特殊字符 | `\.` | 字面量点号 |

### 3.2 字符集合 `[]`

```python
import re

# [a-z] 匹配任意小写字母
print(re.findall(r'[a-z]+', 'Hello World 2026'))
# ['ello', 'orld']

# [a-zA-Z0-9] 匹配字母和数字
print(re.findall(r'[a-zA-Z0-9]+', 'Hello World 2026!'))
# ['Hello', 'World', '2026']

# [^aeiou] 匹配非元音字符（^ 在集合内表示取反）
print(re.findall(r'[^aeiou ]', 'hello world'))
# ['h', 'l', 'l', 'w', 'r', 'l', 'd']

# 在集合内，特殊字符大多无需转义
print(re.findall(r'[.+*]+', 'a.b+c*d'))
# ['.', '+', '*']
```

> **注意**：在 `[]` 内，`-` 表示范围。若想匹配字面量 `-`，应放在集合**最前或最后**，如 `[-a]` 或 `[a-]`。

### 3.3 预定义字符类

| 写法 | 等价于 | 含义 |
|------|--------|------|
| `\d` | `[0-9]` | 数字 |
| `\D` | `[^0-9]` | 非数字 |
| `\w` | `[a-zA-Z0-9_]` | 单词字符（含中文等 Unicode 字母，受标志位影响） |
| `\W` | `[^\w]` | 非单词字符 |
| `\s` | `[ \t\n\r\f\v]` | 空白字符 |
| `\S` | `[^\s]` | 非空白字符 |
| `\b` | — | 单词边界（零宽） |
| `\B` | — | 非单词边界（零宽） |

```python
import re

text = "联系电话: 138-1234-5678, 邮编: 100089"

# \d+ 匹配连续数字
print(re.findall(r'\d+', text))
# ['138', '1234', '5678', '100089']

# \w+ 匹配连续单词字符
print(re.findall(r'\w+', text))
# ['联系电话', '138', '1234', '5678', '邮编', '100089']

# \b 单词边界
print(re.findall(r'\bcat\b', 'cat catalog catch cat'))
# ['cat', 'cat']
```

> **关于 `\w` 与中文**：默认（Unicode 模式）下，`\w` 能匹配中文字符。若使用 `re.A`（ASCII）标志位，则 `\w` 只匹配 `[a-zA-Z0-9_]`。

---

## 4. 分组与捕获

### 4.1 普通分组

用 `()` 将模式的一部分括起来，形成**捕获组**，可后续引用：

```python
import re

# 提取日期中的年月日
m = re.search(r'(\d{4})-(\d{2})-(\d{2})', '今天是 2026-08-05')
print(m.group(1), m.group(2), m.group(3))   # 2026 08 05
print(m.groups())                            # ('2026', '08', '05')
```

### 4.2 命名分组

通过 `(?P<name>...)` 给分组命名，提高可读性：

```python
import re

m = re.search(r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})', '2026-08-05')
print(m.group('year'))     # 2026
print(m.group('month'))    # 08
print(m.groupdict())       # {'year': '2026', 'month': '08', 'day': '05'}
```

### 4.3 后向引用

在同一模式中引用前面捕获的内容，用 `\1`、`\2` 或 `(?P=name)`：

```python
import re

# 匹配成对引号包围的内容
print(re.findall(r'(["\'])(.*?)\1', "say 'hi' and \"hello\""))
# [("'", 'hi'), ('"', 'hello')]

# 匹配重复的单词
print(re.search(r'\b(\w+)\s+\1\b', 'the the quick brown').group())
# 'the the'
```

### 4.4 非捕获分组

使用 `(?:...)` 表示**只分组不捕获**，不占用分组编号，提升性能：

```python
import re

# 想匹配 "http://" 或 "https://" 但不需要单独捕获协议
urls = 'visit https://example.com or http://test.org'
print(re.findall(r'https?://(?:[\w-]+\.)+[a-z]{2,}', urls))
# ['https://example.com', 'http://test.org']
```

---

## 5. 贪婪与非贪婪

### 5.1 贪婪匹配（默认）

默认情况下，`*`、`+`、`?`、`{n,m}` 会尽可能多地匹配字符：

```python
import re

s = '<div>hello</div><div>world</div>'

# 贪婪：.* 会一直匹配到最后的 </div>
print(re.findall(r'<div>.*</div>', s))
# ['<div>hello</div><div>world</div>']
```

### 5.2 非贪婪匹配

在量词后加 `?` 变为**非贪婪**（懒惰）模式，尽可能少地匹配：

| 贪婪 | 非贪婪 |
|------|--------|
| `*` | `*?` |
| `+` | `+?` |
| `?` | `??` |
| `{n,m}` | `{n,m}?` |

```python
import re

s = '<div>hello</div><div>world</div>'

# 非贪婪：.*? 匹配到第一个 </div> 就停止
print(re.findall(r'<div>.*?</div>', s))
# ['<div>hello</div>', '<div>world</div>']
```

> **实践建议**：处理 HTML/XML 时，非贪婪配合特定边界比贪婪更安全。但复杂 HTML 解析应使用专门的解析库（如 `BeautifulSoup`），正则不适合解析嵌套结构。

---

## 6. 零宽断言（Lookaround）

零宽断言用于"匹配某个位置，但该位置前/后需满足某种条件"，断言本身**不消耗字符**。

| 语法 | 名称 | 含义 |
|------|------|------|
| `(?=...)` | 正向先行断言 | 右侧必须匹配 … |
| `(?!...)` | 负向先行断言 | 右侧不能匹配 … |
| `(?<=...)` | 正向后行断言 | 左侧必须匹配 … |
| `(?<!...)` | 负向后行断言 | 左侧不能匹配 … |

```python
import re

text = 'price: $100, $200, and $300'

# 提取 $ 后面的数字（不包含 $）
print(re.findall(r'(?<=\$)\d+', text))
# ['100', '200', '300']

# 匹配后面跟有 "元" 的数字
s = '苹果5元，香蕉8个，橙子3元'
print(re.findall(r'\d+(?=元)', s))
# ['5', '3']

# 匹配后面不是 "元" 的数字
print(re.findall(r'\d+(?!元)', s))
# ['8']
```

> **注意**：Python 3.7 之前，后行断言内的模式必须是固定长度；3.7+ 放宽了该限制，但仍建议保持固定长度以兼容旧版本。

---

## 7. 标志位（Flags）

通过标志位可调整匹配行为，多个标志位用 `|` 组合：

| 标志位 | 缩写 | 含义 |
|--------|------|------|
| `re.IGNORECASE` | `re.I` | 忽略大小写 |
| `re.MULTILINE` | `re.M` | 多行模式，`^` 和 `$` 匹配每行开头/结尾 |
| `re.DOTALL` | `re.S` | 使 `.` 匹配包括换行符在内的所有字符 |
| `re.VERBOSE` | `re.X` | 允许在模式中加空白和注释，提高可读性 |
| `re.ASCII` | `re.A` | 使 `\w`、`\d`、`\s` 只匹配 ASCII 字符 |

```python
import re

# 忽略大小写
print(re.findall(r'python', 'Python PYTHON python', re.I))
# ['Python', 'PYTHON', 'python']

# 多行模式
text = "line1\nline2\nline3"
print(re.findall(r'^line\d', text, re.M))
# ['line1', 'line2', 'line3']

# DOTALL：让 . 匹配换行
html = '<div>\nhello\n</div>'
print(re.search(r'<div>(.*?)</div>', html, re.S).group(1))
# '\nhello\n'
```

### 使用 VERBOSE 编写复杂正则

```python
import re

email_re = re.compile(r"""
    ^                   # 字符串开头
    [a-zA-Z0-9._%+-]+   # 用户名部分
    @                   # @ 符号
    [a-zA-Z0-9.-]+      # 域名部分
    \.[a-zA-Z]{2,}      # 顶级域名
    $                   # 字符串结尾
""", re.VERBOSE)

print(email_re.match('user@example.com'))   # <Match object>
```

---

## 8. 预编译与性能

### 8.1 re.compile

当同一个正则会被**多次使用**时，用 `re.compile()` 预编译可提升性能（编译一次，复用多次）：

```python
import re

# 预编译
phone_re = re.compile(r'1[3-9]\d{9}')

texts = ['电话13812345678', '联系13987654321', '无电话']
for t in texts:
    m = phone_re.search(t)
    if m:
        print(m.group())
# 13812345678
# 13987654321
```

编译后的 Pattern 对象拥有与 `re` 模块同名的方法（`match`、`search`、`findall`、`sub` 等），用法一致。

### 8.2 性能与安全注意事项

- **避免灾难性回溯**：嵌套量词（如 `(a+)+b`）在匹配失败时可能引发指数级回溯，导致程序卡死。应简化模式或使用更具体的字符类。
- **慎用 `.*`**：能确定字符范围时尽量用 `[^"]*` 等具体形式代替 `.*`。
- **超时保护**：处理不可信输入时，可借助 `signal` 或第三方库 `regex`（支持超时参数）防范 ReDoS 攻击。

---

## 9. 常见实战案例

### 9.1 校验邮箱格式

```python
import re

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

print(is_valid_email('user@example.com'))      # True
print(is_valid_email('user.name+tag@sub.example.org'))  # True
print(is_valid_email('invalid@@example'))      # False
print(is_valid_email('@example.com'))          # False
```

> **说明**：该正则覆盖大多数常见邮箱，但并非严格遵循 RFC 5322。生产环境建议使用专门的库（如 `email_validator`）。

### 9.2 校验中国大陆手机号

```python
import re

def is_valid_phone(phone):
    # 1 开头，第二位 3-9，共 11 位
    return bool(re.fullmatch(r'1[3-9]\d{9}', phone))

print(is_valid_phone('13812345678'))   # True
print(is_valid_phone('12345678901'))   # False（第二位是 2）
print(is_valid_phone('1381234567'))    # False（位数不足）
```

### 9.3 提取网页中的所有 URL

```python
import re

html = '''
<a href="https://www.example.com/page1">Page1</a>
<a href="http://test.org">Test</a>
<a href="/relative/path">Relative</a>
'''

# 只提取 http/https 开头的绝对 URL
urls = re.findall(r'https?://[^\s"\'<>]+', html)
print(urls)
# ['https://www.example.com/page1', 'http://test.org']
```

### 9.4 提取 HTML 标签内容

```python
import re

html = '<p>第一段</p><p>第二段</p>'
contents = re.findall(r'<p>(.*?)</p>', html)
print(contents)   # ['第一段', '第二段']
```

### 9.5 驼峰命名转下划线命名

```python
import re

def camel_to_snake(name):
    # 在大写字母前插入下划线，再全部转小写
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

print(camel_to_snake('getUserInfo'))     # get_user_info
print(camel_to_snake('HTTPResponse'))    # http_response
print(camel_to_snake('simpleXMLParser')) # simple_xml_parser
```

### 9.6 敏感词脱敏

```python
import re

# 手机号中间 4 位脱敏
phone = '联系方式：13812345678'
masked = re.sub(r'(1[3-9]\d)\d{4}(\d{4})', r'\1****\2', phone)
print(masked)   # 联系方式：138****5678

# 邮箱用户名脱敏（保留首字符和域名）
email = 'username@example.com'
masked_email = re.sub(r'(?<=.).(?=[^@]*@.{2,})', '*', email)
print(masked_email)   # *********@example.com
```

### 9.7 按多种分隔符拆分字符串

```python
import re

s = 'hello,world;python|java  go'
# 按逗号、分号、竖线或空白拆分
parts = re.split(r'[,;|\s]+', s)
print(parts)   # ['hello', 'world', 'python', 'java', 'go']
```

---

## 10. 小结

### 10.1 核心要点

- 使用 `re` 模块进行正则操作，模式字符串建议加 `r` 前缀（原始字符串）
- `match` 从开头匹配，`search` 扫描全串，`fullmatch` 要求完全匹配，`findall` 返回所有匹配
- `findall` 的返回值受分组数量影响：无分组返回整个匹配，有分组返回分组内容
- 掌握元字符（`. * + ? ^ $ [] | () \`）与预定义字符类（`\d \w \s \b`）
- 分组用 `()`，命名分组 `(?P<name>)`，非捕获分组 `(?:)`，后向引用 `\1`
- 默认贪婪匹配，加 `?` 变非贪婪（`*?` `+?`）
- 零宽断言（`(?=) (?!) (?<=) (?<!)`）匹配位置但不消耗字符
- 常用标志位：`re.I`（忽略大小写）、`re.M`（多行）、`re.S`（`.` 匹配换行）、`re.X`（注释模式）
- 复杂正则用 `re.compile` 预编译，用 `re.X` 提升可读性

### 10.2 学习建议

1. 先掌握基本元字符与 `re` 模块函数，再逐步学习分组、断言等高级用法
2. 善用在线工具（如 regex101.com）调试正则，可视化匹配过程
3. **正则不是万能的**：解析嵌套结构（HTML、JSON）应使用专用解析库
4. 注意性能与安全：避免灾难性回溯，处理不可信输入需加超时保护

### 10.3 常用模式速查

| 场景 | 正则模式 |
|------|----------|
| 整数 | `-?\d+` |
| 浮点数 | `-?\d+\.\d+` |
| 邮箱 | `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}` |
| 中国手机号 | `1[3-9]\d{9}` |
| 日期（YYYY-MM-DD） | `\d{4}-\d{2}-\d{2}` |
| 时间（HH:MM:SS） | `([01]?\d|2[0-3]):[0-5]\d:[0-5]\d` |
| IPv4 | `(\d{1,3}\.){3}\d{1,3}` |
| URL | `https?://[^\s"\'<>]+` |
| 中文字符 | `[\u4e00-\u9fa5]` |
| 身份证号（18位） | `[1-9]\d{5}(19|20)\d{2}(0[1-9]\|1[0-2])(0[1-9]\|[12]\d\|3[01])\d{3}[\dXx]` |
