# Python 环境搭建与入门

## 1. Python 简介

### 1.1 什么是 Python

Python 是一种高级、解释型、通用型编程语言，由 Guido van Rossum 于 1989 年圣诞节期间开发，1991 年正式发布。

**Python 的核心特点**：

- **简洁优雅**：语法清晰，代码可读性强，接近自然语言
- **解释执行**：无需编译，运行时由解释器逐行执行
- **跨平台**：支持 Windows、macOS、Linux 等多种操作系统
- **动态类型**：变量无需声明类型，运行时自动推断
- **面向对象**：原生支持面向对象编程范式
- **丰富的生态**：拥有大量第三方库，覆盖 Web、AI、数据分析等领域

### 1.2 Python 的应用领域

| 领域 | 典型应用 | 常用库 |
|------|----------|--------|
| Web 开发 | 网站后端、API 服务 | Django, Flask, FastAPI |
| 数据科学 | 数据分析、可视化 | NumPy, Pandas, Matplotlib |
| 人工智能 | 机器学习、深度学习 | TensorFlow, PyTorch, scikit-learn |
| 自动化运维 | 脚本、运维工具 | Ansible, Fabric |
| 网络爬虫 | 数据采集 | Scrapy, BeautifulSoup, Requests |
| 自动化办公 | Excel、Word 处理 | openpyxl, python-docx |

### 1.3 Python 2 与 Python 3

目前 Python 有两个主要版本：

- **Python 2.x**：已停止维护（2020年1月1日）
- **Python 3.x**：当前主流版本，与 2.x 不兼容

> **注意**：本系列文档以 Python 3.x 为基础，请确保安装最新版本。

---

## 2. 安装 Python

### 2.1 在 Windows 上安装

**方式一：官方安装包**

1. 访问 [Python 官网下载页面](https://www.python.org/downloads/windows/)
2. 下载 `Windows installer (64-bit)`
3. 运行安装程序，**务必勾选 `Add Python 3.x to PATH`**
4. 点击 `Install Now` 完成安装

**方式二：使用 Scoop 包管理器**

```powershell
# 先安装 Scoop（如未安装）
# 然后执行
scoop install python
```

### 2.2 在 macOS 上安装

**方式一：官方安装包**

从 [Python 官网](https://www.python.org/downloads/macos/) 下载 macOS 版安装程序，双击运行。

**方式二：使用 Homebrew**

```bash
brew install python3
```

### 2.3 在 Linux 上安装

大多数 Linux 发行版自带 Python 3，如需手动安装：

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3
```

### 2.4 验证安装

打开命令行，输入：

```bash
# Windows
python --version

# macOS / Linux
python3 --version
```

输出类似 `Python 3.13.x` 即表示安装成功。

> **提示**：Python 在 Linux/macOS 上的命令是 `python3`，在 Windows 上是 `python`，后续请根据系统自行选择。

---

## 3. Python 解释器

### 3.1 交互式环境

安装成功后，在命令行输入 `python`（或 `python3`）进入交互式环境：

```python
$ python3
Python 3.13.0 (main, Oct  8 2024, ...)
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

在 `>>>` 提示符下可以直接输入 Python 代码并立即执行：

```python
>>> print("Hello, Python!")
Hello, Python!
>>> 100 + 200
300
>>> exit()   # 退出交互式环境
```

### 3.2 常见解释器类型

| 解释器 | 说明 |
|--------|------|
| **CPython** | 官方默认解释器，用 C 语言实现 |
| **IPython** | 基于 CPython 的增强交互式解释器 |
| **PyPy** | 采用 JIT 技术，执行速度快 |
| **Jython** | 运行在 Java 平台，可调用 Java 库 |
| **IronPython** | 运行在 .NET 平台 |

> 除非特别说明，本系列文档均基于 **CPython**。

### 3.3 运行 Python 文件

将代码保存为 `.py` 文件，例如 `hello.py`：

```python
# hello.py
print("Hello, World!")
name = "Python"
print(f"Welcome to {name}!")
```

在命令行执行：

```bash
python hello.py      # Windows
python3 hello.py     # macOS / Linux
```

---

## 4. 第一个 Python 程序

### 4.1 Hello World

```python
print("Hello, World!")
```

`print()` 是 Python 的内置函数，用于输出内容到控制台。

### 4.2 使用 IDE

推荐使用以下开发工具：

| 工具 | 特点 | 适用场景 |
|------|------|----------|
| **VS Code** | 轻量、插件丰富、免费 | 通用开发 |
| **PyCharm** | 专业 Python IDE，功能强大 | 大型项目 |
| **Jupyter Notebook** | 交互式、可视化 | 数据分析、学习 |
| **Sublime Text** | 轻量快速 | 快速编辑 |

### 4.3 代码注释

```python
# 这是单行注释，以 # 开头

"""
这是多行注释（使用三引号字符串）
可以跨越多行
通常用于函数或类的文档说明
"""

# 以下代码计算圆的面积
radius = 5
area = 3.14159 * radius ** 2
print(f"半径为 {radius} 的圆，面积是 {area:.2f}")
```

### 4.4 输入与输出

```python
# 输出
print("Hello")
print("Hello", "World")          # 默认用空格分隔
print("Hello", "World", sep="-") # 自定义分隔符
print("Hello", end="")           # 不换行
print("World")

# 输入（返回字符串）
name = input("请输入你的名字：")
print(f"你好，{name}！")

# 输入数字时需要类型转换
age = int(input("请输入你的年龄："))
print(f"你明年 {age + 1} 岁")
```

---

## 5. Python 代码规范

### 5.1 缩进

Python 使用缩进表示代码块，**而非大括号**。约定使用 **4 个空格** 缩进：

```python
# 正确：使用 4 个空格
if True:
    print("缩进正确")

# 错误：混用空格和 Tab
# if True:
#     \tprint("混用 Tab 和空格")  # 会报错
```

### 5.2 PEP 8 规范要点

PEP 8 是 Python 官方代码风格指南，要点包括：

- 缩进使用 4 个空格
- 每行不超过 79 个字符
- 函数和类之间空两行
- 方法之间空一行
- 运算符两侧加空格：`x = 1 + 2`
- 逗号后加空格：`[1, 2, 3]`
- 使用小写字母加下划线命名变量：`my_variable`
- 类名使用驼峰命名：`MyClass`

### 5.3 命名规范

| 类型 | 命名规则 | 示例 |
|------|----------|------|
| 变量名 | 小写 + 下划线 | `user_name` |
| 函数名 | 小写 + 下划线 | `get_user_info()` |
| 类名 | 驼峰命名 | `StudentInfo` |
| 常量 | 全大写 + 下划线 | `MAX_SIZE` |
| 模块名 | 小写 + 下划线 | `my_module.py` |
| 私有成员 | 单下划线前缀 | `_private_var` |

---

## 6. 包管理工具 pip

### 6.1 pip 常用命令

```bash
# 安装包
pip install package_name

# 安装指定版本
pip install package_name==1.2.3

# 卸载包
pip uninstall package_name

# 查看已安装的包
pip list

# 查看包信息
pip show package_name

# 导出依赖
pip freeze > requirements.txt

# 批量安装依赖
pip install -r requirements.txt

# 升级包
pip install --upgrade package_name
```

### 6.2 使用国内镜像源加速

```bash
# 临时使用
pip install package_name -i https://pypi.tuna.tsinghua.edu.cn/simple

# 永久配置
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

常用国内镜像源：

| 镜像源 | URL |
|--------|-----|
| 清华大学 | https://pypi.tuna.tsinghua.edu.cn/simple |
| 阿里云 | https://mirrors.aliyun.com/pypi/simple/ |
| 中科大 | https://pypi.mirrors.ustc.edu.cn/simple/ |
| 豆瓣 | https://pypi.douban.com/simple/ |

### 6.3 虚拟环境

为不同项目创建独立的 Python 环境，避免依赖冲突：

```bash
# 使用 venv（Python 内置）
python -m venv myenv           # 创建虚拟环境
myenv\Scripts\activate         # Windows 激活
source myenv/bin/activate      # macOS/Linux 激活
deactivate                     # 退出虚拟环境
```

```bash
# 使用 conda（需安装 Anaconda/Miniconda）
conda create -n myenv python=3.13
conda activate myenv
conda deactivate
```

---

## 7. 小结

### 7.1 核心要点

- Python 是跨平台、解释型、面向对象的高级语言
- 当前主流版本为 Python 3.x，安装时务必勾选 `Add Python to PATH`
- Windows 命令为 `python`，macOS/Linux 命令为 `python3`
- Python 使用缩进表示代码块，约定 4 个空格
- 遵循 PEP 8 代码规范，提高代码可读性
- 使用 pip 管理第三方包，推荐配置国内镜像源
- 使用虚拟环境隔离项目依赖

### 7.2 学习路径建议

```
环境搭建 → 基础语法 → 数据结构 → 函数 → 高级特性
    → 函数式编程 → 面向对象 → 模块与错误处理 → IO 编程
```

### 7.3 常用命令速查

| 命令 | 说明 |
|------|------|
| `python --version` | 查看 Python 版本 |
| `python script.py` | 运行脚本文件 |
| `python` | 进入交互式环境 |
| `pip install xxx` | 安装包 |
| `pip list` | 查看已安装包 |
| `pip freeze > requirements.txt` | 导出依赖 |
| `python -m venv myenv` | 创建虚拟环境 |
