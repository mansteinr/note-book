# Python IO 编程详解

## 1. IO 编程概述

### 1.1 什么是 IO

IO 指 Input/Output，即输入和输出。以程序为中心：

- **输入**：从外部读取数据到内存（读文件、接收网络数据）
- **输出**：将数据从内存写到外部（写文件、发送网络数据）

### 1.2 同步与异步 IO

| 模式 | 说明 | Python 支持 |
|------|------|-------------|
| 同步 IO | 读写时阻塞，等待操作完成 | `open()` 等 |
| 异步 IO | 发起请求后不等待，通过回调处理 | `asyncio` 模块 |

本文档主要介绍**同步 IO**，这是日常开发中最常用的模式。

---

## 2. 文件读写

### 2.1 打开文件

使用 `open()` 函数打开文件：

```python
# 基本语法
open(file, mode='r', encoding=None)

# mode 参数
# 'r'  - 只读（默认）
# 'w'  - 只写（覆盖）
# 'a'  - 追加
# 'r+' - 读写
# 'b'  - 二进制模式（如 'rb', 'wb'）
# 'x'  - 独占创建（文件已存在则报错）
```

### 2.2 读取文件

```python
# 方式1：读取整个文件（小文件）
with open('test.txt', 'r', encoding='utf-8') as f:
    content = f.read()
    print(content)

# 方式2：逐行读取（大文件推荐）
with open('test.txt', 'r', encoding='utf-8') as f:
    for line in f:
        print(line.strip())  # strip() 去除换行符

# 方式3：读取所有行为列表
with open('test.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()  # ['第一行\n', '第二行\n', ...]

# 方式4：读取指定字节数
with open('test.txt', 'r', encoding='utf-8') as f:
    chunk = f.read(100)    # 读取100个字符
    line = f.readline()    # 读取一行
```

### 2.3 写入文件

```python
# 覆盖写入
with open('output.txt', 'w', encoding='utf-8') as f:
    f.write("第一行\n")
    f.write("第二行\n")

# 追加写入
with open('output.txt', 'a', encoding='utf-8') as f:
    f.write("追加的内容\n")

# 写入多行
lines = ['apple\n', 'banana\n', 'cherry\n']
with open('fruits.txt', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# 使用 print 写入文件
with open('output.txt', 'w', encoding='utf-8') as f:
    print("Hello", file=f)
    print("World", file=f)
```

> **注意**：`write()` 不会自动添加换行符，需要手动加 `\n`。

### 2.4 二进制文件读写

```python
# 读取二进制文件（图片、视频等）
with open('image.png', 'rb') as f:
    data = f.read()
    print(f"文件大小：{len(data)} 字节")

# 写入二进制文件
with open('copy.png', 'wb') as f:
    f.write(data)

# 复制文件
def copy_file(src, dst):
    with open(src, 'rb') as fin, open(dst, 'wb') as fout:
        while True:
            chunk = fin.read(8192)  # 每次读 8KB
            if not chunk:
                break
            fout.write(chunk)

copy_file('source.png', 'target.png')
```

### 2.5 文件指针

```python
with open('test.txt', 'r+') as f:
    content = f.read()       # 读取后指针在末尾
    print(f"位置：{f.tell()}")  # 查看当前位置

    f.seek(0)                # 移动指针到开头
    content2 = f.read()      # 重新读取

    f.seek(0, 2)             # 0=开头, 1=当前位置, 2=末尾
    print(f"文件大小：{f.tell()}")
```

---

## 3. with 语句与上下文管理

### 3.1 为什么用 with

文件使用后必须关闭，否则会导致资源泄漏。`with` 语句确保文件**自动关闭**，即使发生异常。

```python
# 传统方式（繁琐且不安全）
f = open('test.txt')
try:
    content = f.read()
finally:
    f.close()

# with 语句（推荐）
with open('test.txt') as f:
    content = f.read()
# 离开 with 块后自动调用 f.close()
```

### 3.2 同时操作多个文件

```python
# 同时打开多个文件
with open('input.txt') as fin, open('output.txt', 'w') as fout:
    for line in fin:
        fout.write(line.upper())
```

### 3.3 自定义上下文管理器

```python
# 方式1：实现 __enter__ 和 __exit__
class Timer:
    def __enter__(self):
        import time
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.elapsed = time.time() - self.start
        print(f"耗时：{self.elapsed:.4f}秒")
        return False  # 不抑制异常

with Timer():
    sum(range(1000000))

# 方式2：使用 contextlib
from contextlib import contextmanager

@contextmanager
def file_manager(filename, mode):
    f = open(filename, mode)
    try:
        yield f  # 将文件对象交给 with 块使用
    finally:
        f.close()

with file_manager('test.txt', 'w') as f:
    f.write('Hello')
```

---

## 4. 文件和目录操作

### 4.1 使用 os 模块

```python
import os

# 当前工作目录
print(os.getcwd())              # 获取当前目录
os.chdir('/path/to/dir')        # 切换目录

# 创建目录
os.mkdir('newdir')              # 创建单级目录
os.makedirs('a/b/c')            # 递归创建多级目录

# 删除
os.remove('file.txt')           # 删除文件
os.rmdir('emptydir')            # 删除空目录
os.removedirs('a/b/c')          # 递归删除空目录

# 重命名/移动
os.rename('old.txt', 'new.txt')

# 路径操作
os.path.join('dir', 'file.txt')     # 拼接路径
os.path.split('/a/b/c.txt')         # ('/a/b', 'c.txt')
os.path.splitext('file.txt')        # ('file', '.txt')
os.path.dirname('/a/b/c.txt')       # '/a/b'
os.path.basename('/a/b/c.txt')      # 'c.txt'

# 路径判断
os.path.exists('test.txt')          # 是否存在
os.path.isfile('test.txt')          # 是否是文件
os.path.isdir('mydir')              # 是否是目录
os.path.abspath('test.txt')         # 绝对路径
```

### 4.2 使用 pathlib（推荐）

`pathlib` 是 Python 3.4+ 的现代路径操作模块，比 `os.path` 更优雅：

```python
from pathlib import Path, PurePath

# 创建 Path 对象
p = Path('.')
p = Path('/usr/bin/python')
p = Path.home()           # 用户主目录
p = Path.cwd()            # 当前工作目录

# 路径拼接（用 / 运算符，非常直观）
p = Path('mydir') / 'subdir' / 'file.txt'

# 路径属性
p = Path('/usr/bin/python3')
p.name        # 'python3'，文件名
p.stem        # 'python3'，不含后缀
p.suffix      # ''，后缀
p.parent      # Path('/usr/bin')，父目录
p.parents     # 所有父目录
p.parts       # ('/', 'usr', 'bin', 'python3')

# 路径操作
p = Path('test.txt')
p.exists()              # 是否存在
p.is_file()             # 是否是文件
p.is_dir()              # 是否是目录
p.absolute()            # 绝对路径
p.resolve()             # 解析为绝对路径（解析符号链接）
p.with_suffix('.md')    # 替换后缀
p.with_name('new.txt')  # 替换文件名

# 文件操作
p = Path('test.txt')
p.touch()               # 创建空文件
p.unlink()              # 删除文件
p.rename('new.txt')     # 重命名

# 目录操作
p = Path('mydir')
p.mkdir()               # 创建目录
p.mkdir(parents=True, exist_ok=True)  # 递归创建，已存在不报错
p.rmdir()               # 删除空目录

# 遍历目录
for item in Path('.').iterdir():
    print(item)

# glob 匹配
for py_file in Path('.').glob('*.py'):
    print(py_file)

for py_file in Path('.').rglob('*.py'):  # 递归
    print(py_file)
```

### 4.3 遍历目录树

```python
# 方式1：os.walk
import os

for root, dirs, files in os.walk('.'):
    print(f"目录：{root}")
    print(f"  子目录：{dirs}")
    print(f"  文件：{files}")

# 方式2：pathlib 递归遍历
from pathlib import Path

def walk_path(path):
    for item in Path(path).iterdir():
        if item.is_dir():
            print(f"📁 {item}/")
            walk_path(item)
        else:
            print(f"📄 {item}")

walk_path('.')
```

### 4.4 获取文件信息

```python
from pathlib import Path
import os
import datetime

p = Path('test.txt')

# 文件大小
print(p.stat().st_size)           # 字节数
print(os.path.getsize('test.txt'))

# 修改时间
timestamp = p.stat().st_mtime
mod_time = datetime.datetime.fromtimestamp(timestamp)
print(f"最后修改：{mod_time}")

# 完整 stat 信息
stat = p.stat()
print(f"大小：{stat.st_size}")
print(f"权限：{oct(stat.st_mode)}")
print(f"修改时间：{datetime.datetime.fromtimestamp(stat.st_mtime)}")
```

---

## 5. StringIO 和 BytesIO

### 5.1 内存中读写

`StringIO` 和 `BytesIO` 在内存中模拟文件操作，适用于不需要落盘的场景。

```python
# StringIO：操作文本
from io import StringIO

# 写入
output = StringIO()
output.write('Hello\n')
output.write('World\n')
output.write('Python\n')

# 获取全部内容
print(output.getvalue())

# 读取
output.seek(0)  # 移动指针到开头
for line in output:
    print(line.strip())

output.close()

# BytesIO：操作二进制
from io import BytesIO

bio = BytesIO()
bio.write(b'Hello')
bio.write(b' World')
print(bio.getvalue())  # b'Hello World'

# 读取
bio.seek(0)
data = bio.read()
print(data)  # b'Hello World'
```

### 5.2 实用场景

```python
# 替代临时文件
import csv
from io import StringIO

# 在内存中生成 CSV
output = StringIO()
writer = csv.writer(output)
writer.writerow(['Name', 'Age'])
writer.writerow(['Alice', 25])
writer.writerow(['Bob', 30])

csv_content = output.getvalue()
print(csv_content)

# 处理网络数据
import requests
from io import BytesIO

# response = requests.get('https://example.com/image.png')
# image_data = BytesIO(response.content)
# 直接传递给需要文件对象的函数
```

---

## 6. 序列化与反序列化

### 6.1 JSON（推荐）

JSON 是跨语言的数据交换格式，适合存储配置和传输数据：

```python
import json

# Python 对象 → JSON 字符串
data = {
    'name': '张三',
    'age': 25,
    'scores': [85, 92, 78],
    'active': True,
    'address': None
}

json_str = json.dumps(data, ensure_ascii=False, indent=2)
print(json_str)

# JSON 字符串 → Python 对象
parsed = json.loads(json_str)
print(parsed['name'])  # 张三

# 读写 JSON 文件
# 写入
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 读取
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
```

### 6.2 处理自定义对象

```python
import json
from datetime import datetime

class Student:
    def __init__(self, name, age, enroll_date):
        self.name = name
        self.age = age
        self.enroll_date = enroll_date

# 自定义编码器
class StudentEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Student):
            return {
                'name': obj.name,
                'age': obj.age,
                'enroll_date': obj.enroll_date.isoformat()
            }
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# 自定义解码器
def student_decoder(dct):
    if 'enroll_date' in dct and 'name' in dct:
        dct['enroll_date'] = datetime.fromisoformat(dct['enroll_date'])
        return Student(dct['name'], dct['age'], dct['enroll_date'])
    return dct

# 使用
student = Student('Alice', 20, datetime(2024, 9, 1))

# 序列化
json_str = json.dumps(student, cls=StudentEncoder, ensure_ascii=False, indent=2)
print(json_str)

# 反序列化
student2 = json.loads(json_str, object_hook=student_decoder)
print(f"{student2.name}, {student2.age}岁, 入学：{student2.enroll_date}")
```

### 6.3 pickle（Python 专用）

`pickle` 可以序列化任意 Python 对象，但**不安全**，不要加载不受信任的 pickle 数据：

> ⚠️ **安全警告**：`pickle` 反序列化时可以构造任意 Python 对象，攻击者可借此在 `pickle.load()` 时**执行任意代码**（远程代码执行 RCE）。因此：① 只 `pickle.load` 自己信任的数据；② 跨进程/跨网络传输请改用 `json`；③ 处理不可信输入可考虑 `pickle` 的受限替代方案（如 `json`、`shelve` 配合校验）。

```python
import pickle

class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

student = Student('Alice', 20)

# 序列化到文件
with open('student.pkl', 'wb') as f:
    pickle.dump(student, f)

# 反序列化
with open('student.pkl', 'rb') as f:
    student2 = pickle.load(f)
    print(f"{student2.name}, {student2.age}岁")

# 序列化为字节
data = pickle.dumps(student)
student3 = pickle.loads(data)
```

### 6.4 JSON vs pickle

| 特性 | JSON | pickle |
|------|------|--------|
| 格式 | 文本 | 二进制 |
| 跨语言 | ✅ | ❌ 仅 Python |
| 安全性 | ✅ 安全 | ❌ 不安全 |
| 支持类型 | 基本类型 | 任意 Python 对象 |
| 可读性 | ✅ 好 | ❌ 差 |
| 推荐场景 | 数据交换、配置 | Python 内部对象持久化 |

---

## 7. 综合应用示例

### 7.1 日志文件分析

```python
"""分析日志文件，统计访问次数"""
from collections import Counter
from pathlib import Path
from datetime import datetime

def analyze_log(log_file):
    """分析访问日志"""
    ip_counter = Counter()
    status_counter = Counter()

    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            # 假设日志格式：IP - - [时间] "请求" 状态码 大小
            parts = line.split()
            if len(parts) >= 9:
                ip = parts[0]
                status = parts[8]
                ip_counter[ip] += 1
                status_counter[status] += 1

    return ip_counter, status_counter

def write_report(ip_counter, status_counter, report_file):
    """生成报告"""
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=== 访问日志分析报告 ===\n\n")

        f.write("Top 10 访问IP：\n")
        for ip, count in ip_counter.most_common(10):
            f.write(f"  {ip}: {count}次\n")

        f.write("\n状态码统计：\n")
        for status, count in status_counter.most_common():
            f.write(f"  {status}: {count}次\n")

# 使用
ip_stats, status_stats = analyze_log('access.log')
write_report(ip_stats, status_stats, 'report.txt')
```

### 7.2 文件搜索工具

```python
"""在目录中搜索包含特定内容的文件"""
from pathlib import Path

def search_in_files(directory, keyword, file_pattern='*'):
    """搜索目录中包含关键词的文件"""
    results = []

    for filepath in Path(directory).rglob(file_pattern):
        if not filepath.is_file():
            continue
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if keyword in line:
                        results.append({
                            'file': str(filepath),
                            'line': line_num,
                            'content': line.strip()
                        })
        except (UnicodeDecodeError, PermissionError):
            continue  # 跳过无法读取的文件

    return results

# 使用
results = search_in_files('.', 'import', '*.py')
for r in results[:10]:  # 显示前10个结果
    print(f"{r['file']}:{r['line']} - {r['content']}")
```

### 7.3 CSV 文件处理

```python
import csv
from pathlib import Path

def read_csv(filename):
    """读取 CSV 文件"""
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)  # 以字典方式读取
        return list(reader)

def write_csv(filename, data, fieldnames):
    """写入 CSV 文件"""
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# 使用
students = [
    {'name': 'Alice', 'age': 20, 'score': 92},
    {'name': 'Bob', 'age': 22, 'score': 85},
    {'name': 'Charlie', 'age': 21, 'score': 78},
]

write_csv('students.csv', students, ['name', 'age', 'score'])

data = read_csv('students.csv')
for row in data:
    print(row)
# {'name': 'Alice', 'age': '20', 'score': '92'}
# ...
```

### 7.4 配置文件管理

```python
"""多格式配置文件读取"""
import json
from pathlib import Path

class Config:
    """配置管理器"""

    def __init__(self, config_path):
        self.path = Path(config_path)
        self.data = {}

    def load(self):
        """根据扩展名加载配置"""
        suffix = self.path.suffix.lower()

        if suffix == '.json':
            with open(self.path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            raise ValueError(f"不支持的配置格式：{suffix}")

        return self

    def get(self, key, default=None):
        """支持点分访问：config.get('database.host')"""
        keys = key.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    def save(self):
        """保存配置"""
        suffix = self.path.suffix.lower()
        if suffix == '.json':
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)

# 使用
config = Config('config.json').load()
host = config.get('database.host', 'localhost')
port = config.get('database.port', 3306)
print(f"数据库：{host}:{port}")
```

---

## 8. 小结

### 8.1 核心要点

- 文件读写用 `open()`，务必用 `with` 语句自动关闭
- 读取大文件用**逐行读取**，避免 `read()` 占满内存
- 文本文件指定 `encoding='utf-8'`，二进制文件用 `'rb'`/`'wb'`
- 文件/目录操作优先用 `pathlib`，比 `os.path` 更优雅
- `StringIO`/`BytesIO` 在内存中模拟文件，适合临时处理
- 数据序列化优先用 **JSON**（跨语言、安全），pickle 仅限 Python 内部
- `shutil` 模块提供高级文件操作（复制、压缩等）

### 8.2 文件读写模式速查

| 模式 | 说明 | 文件不存在 | 文件已存在 |
|------|------|------------|------------|
| `r` | 只读 | 报错 | 从头读 |
| `w` | 只写 | 创建 | 覆盖 |
| `a` | 追加 | 创建 | 从末尾写 |
| `r+` | 读写 | 报错 | 从头读写 |
| `rb` | 二进制读 | 报错 | 从头读 |
| `wb` | 二进制写 | 创建 | 覆盖 |

### 8.3 最佳实践

```python
# 1. 总是用 with 语句
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# 2. 大文件逐行处理
with open('large.txt', 'r', encoding='utf-8') as f:
    for line in f:
        process(line)

# 3. 用 pathlib 操作路径
from pathlib import Path
p = Path('data') / 'file.txt'

# 4. JSON 存储配置
import json
with open('config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

# 5. 处理编码错误
with open('file.txt', errors='ignore') as f:  # 忽略错误
    content = f.read()
with open('file.txt', errors='replace') as f:  # 替换错误字符
    content = f.read()
```

### 8.4 常用模块速查

```python
# 文件读写
open(file, mode, encoding)

# 路径操作
from pathlib import Path, PurePath

# 高级文件操作
import shutil  # copy, move, rmtree, make_archive

# 临时文件
import tempfile  # NamedTemporaryFile, TemporaryDirectory

# 序列化
import json    # JSON 格式（推荐）
import pickle  # Python 专用

# CSV 处理
import csv

# 日志
import logging
```
