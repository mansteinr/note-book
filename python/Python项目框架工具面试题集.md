# Python 项目框架工具面试题集

> 本文档系统覆盖 Python 开发中常见的**项目框架与工具链**面试题，涵盖 Web 框架、数据处理框架、机器学习框架及开发工具四大领域，按"基础题 → 进阶题 → 高级题"分级，每题附详细参考答案与评分标准。
> 适合初/中/高级 Python 工程师面试准备，也可作为技术自测与团队考核参考。

---

## 目录

- [模块一：Web 框架 — Django](#模块一web-框架--django)
- [模块二：Web 框架 — Flask](#模块二web-框架--flask)
- [模块三：Web 框架 — FastAPI](#模块三web-框架--fastapi)
- [模块四：数据处理框架 — NumPy](#模块四数据处理框架--numpy)
- [模块五：数据处理框架 — Pandas](#模块五数据处理框架--pandas)
- [模块六：机器学习框架 — TensorFlow](#模块六机器学习框架--tensorflow)
- [模块七：机器学习框架 — PyTorch](#模块七机器学习框架--pytorch)
- [模块八：开发工具 — Pytest](#模块八开发工具--pytest)
- [模块九：开发工具 — Poetry](#模块九开发工具--poetry)
- [模块十：开发工具 — Docker](#模块十开发工具--docker)

---

## 模块一：Web 框架 — Django

### 题目 1.1 Django MTV 架构模式（基础）

**题目描述：** 请解释 Django 的 MTV 架构模式，说明 Model、Template、View 各自的职责，并与传统的 MVC 模式进行对比。

**考察知识点：** Django 核心架构 | **能力等级：** 初级

**参考答案：**

Django 采用 MTV（Model-Template-View）架构模式，与传统 MVC 对应关系如下：

| 组件 | 职责 | MVC 对应 | 说明 |
|------|------|----------|------|
| **Model** | 数据层 | Model | 负责数据库交互、数据验证、业务逻辑 |
| **Template** | 表现层 | View | 负责 HTML 渲染、数据展示 |
| **View** | 业务逻辑层 | Controller | 接收请求、处理业务、返回响应 |
| URLconf | URL 路由 | — | Django 独有的 URL 分发机制 |

```python
# models.py — Model 层
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']

# views.py — View 层
from django.shortcuts import render
from .models import Article

def article_list(request):
    articles = Article.objects.all()
    return render(request, 'article_list.html', {'articles': articles})

# urls.py — URL 分发
from django.urls import path
from . import views

urlpatterns = [
    path('articles/', views.article_list, name='article_list'),
]
```

```html
<!-- templates/article_list.html — Template 层 -->
{% for article in articles %}
  <h2>{{ article.title }}</h2>
  <p>{{ article.pub_date }}</p>
{% endfor %}
```

**请求处理流程：**
1. 浏览器发送请求 → URLconf 路由匹配
2. 路由找到对应 View 函数/类
3. View 调用 Model 获取数据
4. View 将数据传入 Template 渲染
5. 返回 HTTP 响应给浏览器

**评分标准：**
- 准确说明 MTV 三组件职责及与 MVC 对应关系（5 分）
- 能画出请求处理流程图（3 分）
- 给出可运行代码示例（2 分）

---

### 题目 1.2 Django ORM 查询优化（进阶）

**题目描述：** 在 Django 项目中，你发现某个列表页每次请求会产生几百次数据库查询（N+1 问题）。请分析原因并给出优化方案，说明 `select_related` 和 `prefetch_related` 的区别。

**考察知识点：** ORM 优化、查询性能 | **能力等级：** 中级

**参考答案：**

**N+1 问题产生原因：**

```python
# 典型 N+1 问题代码
articles = Article.objects.all()          # 1 次查询
for article in articles:
    print(article.author.name)            # N 次查询（每次访问外键都查库）
```

**优化方案：**

1. **`select_related`** — 适用于 **ForeignKey / OneToOne** 关系（SQL JOIN）

```python
# 优化后：1 次查询完成
articles = Article.objects.select_related('author').all()
# 生成 SQL: SELECT * FROM article INNER JOIN author ON ...
```

2. **`prefetch_related`** — 适用于 **ManyToMany / 反向 ForeignKey** 关系（Python 层面拼接）

```python
# 适用于多对多关系
articles = Article.objects.prefetch_related('tags').all()
# 生成 SQL: SELECT * FROM article; SELECT * FROM tag WHERE ...
# Python 层面自动关联
```

| 特性 | select_related | prefetch_related |
|------|---------------|-----------------|
| 实现方式 | SQL JOIN | 两条独立 SQL + Python 拼接 |
| 适用关系 | ForeignKey / OneToOne | ManyToMany / 反向 ForeignKey |
| 性能 | 一次查询，JOIN 可能大 | 多次查询，但单次轻量 |
| 适用场景 | 关联表数据量小 | 关联表数据量大或多对多 |

3. **其他优化手段：**

```python
# 只查询需要的字段
Article.objects.values('title', 'author__name')

# 仅查询需要的记录
Article.objects.only('title', 'author_id')

# 使用 iterator() 减少内存占用（大数据集）
for article in Article.objects.all().iterator(chunk_size=2000):
    process(article)

# 使用 bulk_create / bulk_update 批量操作
Article.objects.bulk_create([Article(title=f'Title {i}') for i in range(1000)])
```

**评分标准：**
- 准确解释 N+1 问题产生原因（3 分）
- 正确区分 select_related 和 prefetch_related 的使用场景（4 分）
- 能举出其他优化方法（3 分）

---

### 题目 1.3 Django 中间件与请求生命周期（进阶）

**题目描述：** 请描述 Django 中间件的工作原理和请求生命周期，并实现一个自定义中间件用于记录每个请求的处理时间。

**考察知识点：** 中间件机制、请求生命周期 | **能力等级：** 中级

**参考答案：**

**Django 请求生命周期：**

```
浏览器请求
    ↓
WSGI Server (gunicorn/uwsgi)
    ↓
Django 中间件链 (request 阶段，自上而下)
    ├── SecurityMiddleware
    ├── SessionMiddleware
    ├── CommonMiddleware
    ├── CsrfViewMiddleware
    ├── AuthenticationMiddleware
    ├── MessageMiddleware
    └── ...
    ↓
URLconf 路由匹配
    ↓
View 函数/类 (业务逻辑)
    ↓
Model 层 (数据库操作)
    ↓
Template 渲染
    ↓
Django 中间件链 (response 阶段，自下而上)
    ↓
HTTP 响应返回浏览器
```

**实现请求耗时统计中间件：**

```python
# middleware.py
import time
import logging

logger = logging.getLogger(__name__)

class RequestTimingMiddleware:
    """记录每个请求处理时间的中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # 可以在此做一次性初始化配置

    def __call__(self, request):
        # 请求到达时的处理（request 阶段）
        start_time = time.time()
        
        # 调用下一个中间件或视图
        response = self.get_response(request)
        
        # 响应返回时的处理（response 阶段）
        duration = time.time() - start_time
        logger.info(
            f'[{request.method}] {request.path} '
            f'耗时: {duration:.3f}s '
            f'状态码: {response.status_code}'
        )
        
        # 可在响应头中附加耗时信息
        response['X-Request-Duration'] = f'{duration:.3f}s'
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """在视图被调用前执行"""
        # 可在此记录视图名称或做权限校验
        pass
    
    def process_exception(self, request, exception):
        """在视图抛出异常时执行"""
        logger.error(f'请求异常: {request.path} - {exception}')
        return None  # 返回 None 让默认异常处理接管

# settings.py 中注册
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # ...
    'myapp.middleware.RequestTimingMiddleware',  # 添加自定义中间件
]
```

**中间件的五个钩子方法：**

| 钩子方法 | 执行时机 | 用途 |
|---------|---------|------|
| `__init__` | 服务器启动时一次 | 初始化配置 |
| `__call__` | 每次请求 | 主要处理逻辑 |
| `process_view` | 视图调用前 | 权限校验、参数预处理 |
| `process_exception` | 视图抛出异常时 | 异常记录、自定义错误页 |
| `process_template_response` | 模板渲染后 | 修改模板上下文 |

**评分标准：**
- 准确描述请求生命周期各阶段（4 分）
- 正确实现自定义中间件（4 分）
- 了解中间件五个钩子方法（2 分）

---

### 题目 1.4 Django 信号机制（高级）

**题目描述：** 请解释 Django 信号（Signal）的工作原理，并说明其优缺点。实现一个场景：用户注册后自动发送欢迎邮件和创建个人资料。

**考察知识点：** 信号机制、解耦设计 | **能力等级：** 高级

**参考答案：**

**信号原理：** Django 信号基于观察者模式（发布-订阅），使用 `Signal.send()` 触发信号，`@receiver` 装饰器注册接收者。

```python
# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """用户创建后自动创建个人资料"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    """用户创建后发送欢迎邮件"""
    if created:
        send_mail(
            subject='欢迎注册',
            message=f'Hi {instance.username}，欢迎加入！',
            from_email='admin@example.com',
            recipient_list=[instance.email],
            fail_silently=True,
        )

# apps.py 中确保信号注册
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'users'

    def ready(self):
        import users.signals  # 导入信号模块以注册接收者
```

**优点：**
- 解耦：发送者和接收者相互独立，易于扩展
- 复用：Django 内置多种信号（pre_save, post_save, pre_delete 等）
- 灵活：一个信号可被多个接收者处理

**缺点与注意事项：**
- **隐式依赖**：代码执行流不直观，调试困难
- **事务问题**：信号默认在事务内同步执行，接收者报错会导致操作回滚
- **性能**：同步执行会阻塞请求，大数据量场景需谨慎
- **测试复杂度**：单元测试时需注意信号发送与接收

**最佳实践：**
```python
# 避免信号中执行耗时操作，改用异步任务
from django.db import transaction

@receiver(post_save, sender=User)
def async_welcome_email(sender, instance, created, **kwargs):
    if created:
        # 使用 transaction.on_commit 确保事务提交后再执行
        transaction.on_commit(
            lambda: send_welcome_email_task.delay(instance.id)
        )
```

**评分标准：**
- 正确解释信号原理及观察者模式（3 分）
- 完成用户注册场景实现（3 分）
- 能分析信号优缺点及最佳实践（4 分）

---

## 模块二：Web 框架 — Flask

### 题目 2.1 Flask 核心概念（基础）

**题目描述：** 请说明 Flask 的核心设计理念（微框架），解释 Flask 中的路由、请求钩子和上下文（Application Context 与 Request Context）的概念。

**考察知识点：** Flask 核心架构 | **能力等级：** 初级

**参考答案：**

**Flask 设计理念：**
- **微框架**：核心极简，只提供路由、请求/响应、模板渲染等基础功能
- **可扩展**：通过丰富的扩展生态（Flask-SQLAlchemy、Flask-Login 等）按需添加功能
- **灵活**：不强制项目结构，开发者可自由组织代码

**路由系统：**

```python
from flask import Flask

app = Flask(__name__)

# 基础路由
@app.route('/')
def index():
    return 'Hello, Flask!'

# 动态路由
@app.route('/user/<username>')
def show_user(username):
    return f'User: {username}'

# 指定类型转换器
@app.route('/post/<int:post_id>')
def show_post(post_id):
    return f'Post: {post_id}'

# 限定请求方法
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return '处理登录'
    return '显示登录页面'
```

**请求钩子（Hooks）：**

| 钩子 | 执行时机 |
|------|---------|
| `before_request` | 每次请求前 |
| `after_request` | 每次请求后（无异常时） |
| `teardown_request` | 每次请求后（无论有无异常） |
| `before_first_request` | 首次请求前（Flask 2.3+ 已废弃） |

```python
@app.before_request
def before_request():
    # 请求前处理，如：记录请求日志、校验权限
    g.start_time = time.time()

@app.after_request
def after_request(response):
    # 请求后处理，如：添加响应头
    response.headers['X-Process-Time'] = str(time.time() - g.start_time)
    return response
```

**上下文机制：**

| 上下文 | 生命周期 | 代表对象 | 用途 |
|--------|---------|---------|------|
| **Application Context** | 应用启动到关闭 | `current_app`, `g` | 访问应用配置、全局变量 |
| **Request Context** | 单个请求处理期间 | `request`, `session` | 访问请求数据、会话 |

```python
from flask import current_app, g, request, session

@app.route('/context-demo')
def context_demo():
    # 请求上下文
    user_agent = request.headers.get('User-Agent')
    session['user_id'] = 123
    
    # 应用上下文
    debug_mode = current_app.config['DEBUG']
    g.user = '当前用户'  # g 是请求级别的全局变量
    
    return f'UA: {user_agent}, Debug: {debug_mode}'
```

**评分标准：**
- 清楚解释 Flask 微框架设计理念（3 分）
- 正确演示路由定义与请求钩子（4 分）
- 能区分 Application Context 和 Request Context（3 分）

---

### 题目 2.2 Flask 蓝图与大型应用结构（进阶）

**题目描述：** 请说明 Flask 蓝图（Blueprint）的作用，并设计一个中型 Flask 项目的目录结构，包含用户模块、文章模块和 API 模块。

**考察知识点：** 蓝图、项目架构 | **能力等级：** 中级

**参考答案：**

**蓝图作用：**
- 将应用拆分为可复用的模块化组件
- 支持 URL 前缀统一管理
- 可独立注册中间件、错误处理器和模板

**推荐项目结构：**

```
myapp/
├── app/
│   ├── __init__.py          # 应用工厂
│   ├── models.py            # 公共数据模型
│   ├── extensions.py        # 扩展初始化（db, login_manager 等）
│   ├── config.py            # 配置类
│   ├── users/               # 用户模块蓝图
│   │   ├── __init__.py
│   │   ├── views.py
│   │   ├── models.py
│   │   └── forms.py
│   ├── articles/            # 文章模块蓝图
│   │   ├── __init__.py
│   │   ├── views.py
│   │   └── models.py
│   ├── api/                 # API 模块蓝图
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   └── views.py
│   │   └── v2/
│   │       └── views.py
│   ├── templates/           # 模板
│   └── static/              # 静态文件
├── migrations/              # 数据库迁移
├── tests/
├── requirements.txt
└── run.py
```

**核心代码实现：**

```python
# app/__init__.py — 应用工厂
from flask import Flask
from app.extensions import db, migrate, login_manager
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # 注册蓝图
    from app.users import users_bp
    from app.articles import articles_bp
    from app.api import api_bp
    
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(articles_bp, url_prefix='/articles')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

# app/users/__init__.py
from flask import Blueprint

users_bp = Blueprint('users', __name__,
                     template_folder='templates',
                     static_folder='static')

from app.users import views  # 导入视图以注册路由

# app/users/views.py
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.users import users_bp

@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 登录逻辑
        pass
    return render_template('users/login.html')

@users_bp.route('/profile')
@login_required
def profile():
    return render_template('users/profile.html')

# app/api/__init__.py
from flask import Blueprint

api_bp = Blueprint('api', __name__)

from app.api.v1 import views as v1_views
from app.api.v2 import views as v2_views

# app/api/v1/views.py
from app.api import api_bp
from flask import jsonify

@api_bp.route('/v1/users')
def get_users():
    users = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
    return jsonify(users)
```

**评分标准：**
- 正确解释蓝图作用及优势（3 分）
- 设计合理的项目目录结构（4 分）
- 给出应用工厂与蓝图注册的完整代码（3 分）

---

### 题目 2.3 Flask 与 Django 对比选型（进阶）

**题目描述：** 从架构设计、性能、生态、适用场景等维度对比 Flask 和 Django，并说明在什么场景下选择哪个框架。

**考察知识点：** 框架选型能力 | **能力等级：** 中级

**参考答案：**

| 维度 | Django | Flask |
|------|--------|-------|
| **设计理念** | "开箱即用"全栈框架 | "微内核"最小化核心 |
| **内置功能** | ORM、Admin、认证、表单、中间件等 | 仅路由、模板、请求/响应 |
| **项目结构** | 强约定（startapp 自动生成） | 自由组织，无强制结构 |
| **ORM** | Django ORM（功能完备） | 通过 Flask-SQLAlchemy 等扩展 |
| **Admin 后台** | 内置强大的 Admin 系统 | 需第三方扩展（Flask-Admin） |
| **学习曲线** | 较陡，概念多 | 平缓，上手快 |
| **性能** | 较重，但可通过优化 | 较轻，默认更快 |
| **扩展性** | 内置机制完善 | 依赖扩展生态 |
| **社区生态** | 庞大，企业级解决方案多 | 活跃，扩展丰富但需自行组合 |

**选型建议：**

| 场景 | 推荐框架 | 原因 |
|------|---------|------|
| 内容管理系统、电商平台 | **Django** | 内置 Admin、ORM、认证，快速开发 |
| 微服务、API 服务 | **Flask** / FastAPI | 轻量灵活，按需扩展 |
| 快速原型验证 | **Flask** | 简单直接，快速迭代 |
| 大型企业级应用 | **Django** | 规范统一，团队协作成本低 |
| AI/ML 模型服务 | **Flask** / FastAPI | 轻量，易于集成模型推理 |
| 中小型后端服务 | **Flask** | 灵活，不引入多余组件 |

**评分标准：**
- 多维度对比至少 5 项（5 分）
- 能结合具体场景给出选型建议（5 分）

---

## 模块三：Web 框架 — FastAPI

### 题目 3.1 FastAPI 核心特性（基础）

**题目描述：** 请说明 FastAPI 的核心优势，演示如何创建一个包含路径参数、查询参数和请求体的 RESTful API，并说明 FastAPI 如何自动生成 API 文档。

**考察知识点：** FastAPI 基础、类型注解 | **能力等级：** 初级

**参考答案：**

**FastAPI 核心优势：**
- **高性能**：基于 Starlette（ASGI）和 Pydantic，性能比肩 Node.js 和 Go
- **自动文档**：基于 OpenAPI 规范自动生成 Swagger UI 和 ReDoc 文档
- **类型安全**：利用 Python 类型注解实现请求验证、序列化、编辑器智能提示
- **异步支持**：原生支持 `async/await`，处理高并发场景
- **数据验证**：基于 Pydantic 自动验证请求数据

```python
from fastapi import FastAPI, Path, Query, Body, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

app = FastAPI(
    title="文章管理 API",
    description="一个简单的文章 CRUD 示例",
    version="1.0.0"
)

# ---- 数据模型 ----
class ArticleStatus(str, Enum):
    draft = "draft"
    published = "published"
    archived = "archived"

class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="文章标题")
    content: str = Field(..., min_length=1, description="文章内容")
    tags: List[str] = Field(default=[], description="标签列表")
    status: ArticleStatus = Field(default=ArticleStatus.draft)

class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: List[str]
    status: ArticleStatus

# 模拟数据库
fake_db = {}
counter = 0

# ---- API 接口 ----
@app.get("/", summary="根路径")
async def root():
    """API 根路径，返回欢迎信息"""
    return {"message": "Welcome to FastAPI"}

@app.post("/articles/", response_model=ArticleResponse, status_code=201,
          summary="创建文章", tags=["文章管理"])
async def create_article(article: ArticleCreate):
    """创建一篇新文章"""
    global counter
    counter += 1
    fake_db[counter] = article.dict()
    return {"id": counter, **article.dict()}

@app.get("/articles/{article_id}", response_model=ArticleResponse,
         summary="获取文章详情", tags=["文章管理"])
async def get_article(
    article_id: int = Path(..., ge=1, description="文章 ID"),
    include_content: bool = Query(True, description="是否包含正文内容")
):
    """根据 ID 获取文章详情"""
    article = fake_db.get(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    result = {"id": article_id, **article}
    if not include_content:
        result.pop("content", None)
    return result

@app.get("/articles/", response_model=List[ArticleResponse],
         summary="文章列表", tags=["文章管理"])
async def list_articles(
    status: Optional[ArticleStatus] = Query(None, description="按状态筛选"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(10, ge=1, le=100, description="返回数量")
):
    """获取文章列表，支持分页和状态筛选"""
    result = [
        {"id": k, **v} for k, v in fake_db.items()
        if status is None or v.get("status") == status
    ]
    return result[skip : skip + limit]

@app.put("/articles/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    article: ArticleCreate
):
    """更新文章（全量更新）"""
    if article_id not in fake_db:
        raise HTTPException(status_code=404, detail="文章不存在")
    fake_db[article_id] = article.dict()
    return {"id": article_id, **article.dict()}

@app.delete("/articles/{article_id}", status_code=204)
async def delete_article(article_id: int):
    """删除文章"""
    if article_id not in fake_db:
        raise HTTPException(status_code=404, detail="文章不存在")
    del fake_db[article_id]
```

**自动文档访问：**
- Swagger UI：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`

**评分标准：**
- 能说明 FastAPI 核心优势（3 分）
- 正确实现 CRUD API 并展示参数类型（4 分）
- 了解自动文档生成机制（3 分）

---

### 题目 3.2 FastAPI 依赖注入（进阶）

**题目描述：** 请解释 FastAPI 依赖注入（Depends）机制，并实现一个完整的认证鉴权依赖：包括 JWT Token 验证、当前用户获取和权限校验。

**考察知识点：** 依赖注入、认证鉴权 | **能力等级：** 中级

**参考答案：**

**依赖注入原理：** FastAPI 的 `Depends` 是一个强大的依赖注入系统，允许将可复用的逻辑（认证、数据库连接、参数校验等）声明为函数依赖，通过 `Depends()` 注入到路由处理函数中。依赖可以嵌套，形成依赖链。

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

# ---- 配置 ----
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# ---- 数据模型 ----
class User(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool = True
    is_superuser: bool = False

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None

# ---- JWT 工具函数 ----
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ---- 依赖函数（可组合的依赖链） ----

# 依赖 1: 获取数据库会话
def get_db():
    """模拟数据库连接，实际项目中连接真实的 DB"""
    db = {"connected": True}
    try:
        yield db
    finally:
        db["connected"] = False  # 清理资源

# 依赖 2: 解析并验证 Token
async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    从请求头中提取 Bearer Token，验证并返回当前用户。
    自动处理 401 未认证错误。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 实际项目中从数据库查询用户
    user = User(id=user_id, username=username, email=f"{username}@example.com")
    return user

# 依赖 3: 校验活跃用户
async def get_current_active_user(
    current_user: User = Depends(get_current_user)  # 嵌套依赖
) -> User:
    """在 get_current_user 基础上，额外校验用户是否激活"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user

# 依赖 4: 超级管理员权限校验
class PermissionChecker:
    """可复用权限检查器（类依赖）"""
    def __init__(self, required_permission: str):
        self.required_permission = required_permission
    
    def __call__(self, current_user: User = Depends(get_current_active_user)):
        # 实际项目中查数据库权限表
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要 {self.required_permission} 权限"
            )
        return current_user

# ---- 使用依赖的 API 路由 ----
@app.get("/users/me", summary="获取当前用户信息")
async def read_users_me(
    current_user: User = Depends(get_current_active_user),  # 组合依赖
    db: dict = Depends(get_db)                              # 组合依赖
):
    """需要登录才能访问，返回当前用户信息"""
    return {
        "user": current_user,
        "db_connected": db["connected"]
    }

@app.get("/admin/dashboard", summary="管理员仪表盘")
async def admin_dashboard(
    current_user: User = Depends(
        PermissionChecker("admin:access")  # 使用类依赖 + 权限校验
    )
):
    """仅管理员可访问"""
    return {"message": "欢迎来到管理员面板", "user": current_user.username}

@app.post("/token", summary="登录获取 Token")
async def login(username: str, password: str):
    """登录接口，验证用户名密码后返回 JWT Token"""
    # 实际项目中验证密码
    if password != "secret":
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    access_token = create_access_token(
        data={"sub": username, "user_id": 1},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}
```

**依赖注入的优势：**
- 依赖链自动执行，路由函数只需声明需要什么
- 依赖可复用，避免代码重复
- 类型安全，编辑器自动补全
- 测试友好，可轻松 Mock 依赖

**评分标准：**
- 正确解释 Depends 机制（3 分）
- 完成 Token 验证 + 权限校验的依赖链（5 分）
- 展示类依赖和嵌套依赖用法（2 分）

---

### 题目 3.3 FastAPI 异步与并发处理（高级）

**题目描述：** 请说明 ASGI 与 WSGI 的区别，以及 FastAPI 中的 `async/await` 如何使用。实现一个场景：接收批量文章 URL 列表，并发爬取内容，同时将结果异步写入数据库，并返回处理进度。

**考察知识点：** ASGI、异步编程、并发处理 | **能力等级：** 高级

**参考答案：**

**ASGI vs WSGI：**

| 特性 | WSGI | ASGI |
|------|------|------|
| 全称 | Web Server Gateway Interface | Asynchronous Server Gateway Interface |
| 并发模型 | 同步，每个请求一个线程/进程 | 异步，单线程事件循环 |
| 协议支持 | 仅 HTTP | HTTP、WebSocket、HTTP/2 |
| 代表框架 | Django、Flask | FastAPI、Starlette、Django Channels |
| 性能 | 受限于线程数 | 高并发场景显著更优 |

**异步并发处理实现：**

```python
import asyncio
import aiohttp
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List
import time

app = FastAPI()

# ---- 模拟异步数据库 ----
class AsyncDatabase:
    async def insert_article(self, article: dict):
        """模拟异步数据库写入"""
        await asyncio.sleep(0.1)  # 模拟 IO 延迟
        print(f"插入文章: {article['title'][:30]}")

db = AsyncDatabase()

# ---- 进度存储 ----
progress_store = {}

class TaskRequest(BaseModel):
    urls: List[str]

class TaskResponse(BaseModel):
    task_id: str
    total: int
    message: str

class ProgressResponse(BaseModel):
    task_id: str
    completed: int
    total: int
    percentage: float
    results: List[dict]

# ---- 异步爬虫 ----
async def fetch_article(session: aiohttp.ClientSession, url: str) -> dict:
    """异步抓取单个文章"""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status == 200:
                html = await resp.text()
                return {
                    "url": url,
                    "status": "success",
                    "content_length": len(html),
                    "title": f"文章来自 {url}"  # 实际应解析 HTML
                }
            else:
                return {"url": url, "status": "error", "code": resp.status}
    except Exception as e:
        return {"url": url, "status": "error", "error": str(e)}

async def process_urls(
    task_id: str,
    urls: List[str],
    concurrency: int = 10
):
    """
    并发处理 URL 列表：
    1. 使用信号量控制并发数
    2. 抓取文章内容
    3. 异步写入数据库
    4. 更新进度
    """
    semaphore = asyncio.Semaphore(concurrency)
    progress_store[task_id] = {"completed": 0, "total": len(urls), "results": []}
    
    async def process_one(url: str):
        async with semaphore:
            async with aiohttp.ClientSession() as session:
                # 抓取文章
                result = await fetch_article(session, url)
                
                # 异步写入数据库
                if result["status"] == "success":
                    await db.insert_article(result)
                
                # 更新进度
                progress_store[task_id]["completed"] += 1
                progress_store[task_id]["results"].append(result)
                return result
    
    # 并发执行所有任务
    tasks = [process_one(url) for url in urls]
    await asyncio.gather(*tasks, return_exceptions=True)

@app.post("/articles/crawl", response_model=TaskResponse)
async def start_crawl(
    req: TaskRequest,
    background_tasks: BackgroundTasks = None
):
    """启动批量爬取任务（后台执行）"""
    import uuid
    task_id = str(uuid.uuid4())[:8]
    
    # 使用 BackgroundTasks 在后台执行异步任务
    # 注意：实际生产环境建议使用 Celery 或 ARQ 做任务队列
    background_tasks.add_task(
        asyncio.create_task,
        process_urls(task_id, req.urls)
    )
    
    return TaskResponse(
        task_id=task_id,
        total=len(req.urls),
        message="任务已启动，请轮询进度接口"
    )

@app.get("/articles/crawl/{task_id}/progress", response_model=ProgressResponse)
async def get_progress(task_id: str):
    """查询任务进度"""
    if task_id not in progress_store:
        return {"task_id": task_id, "completed": 0, "total": 0, 
                "percentage": 0, "results": []}
    
    data = progress_store[task_id]
    return ProgressResponse(
        task_id=task_id,
        completed=data["completed"],
        total=data["total"],
        percentage=round(data["completed"] / max(data["total"], 1) * 100, 2),
        results=data["results"]
    )

# ---- 同步 vs 异步对比 ----
@app.get("/sync-test")
def sync_test():
    """同步接口：耗时 3 秒"""
    time.sleep(3)
    return {"message": "同步处理完成"}

@app.get("/async-test")
async def async_test():
    """异步接口：非阻塞等待 3 秒"""
    await asyncio.sleep(3)
    return {"message": "异步处理完成"}
```

**使用 `async def` 的注意事项：**

```python
# ✅ 正确：路由函数是 async，内部 await 异步操作
@app.get("/correct")
async def correct():
    result = await some_async_db_query()
    return result

# ❌ 错误：async 路由中调用同步阻塞函数会阻塞事件循环
@app.get("/wrong")
async def wrong():
    time.sleep(5)  # 阻塞整个事件循环！
    return {"message": "done"}

# ✅ 正确：同步阻塞函数用普通 def 路由（FastAPI 会在线程池执行）
@app.get("/sync-correct")
def sync_correct():
    time.sleep(5)  # 在线程池中执行，不阻塞事件循环
    return {"message": "done"}

# ✅ 正确：异步路由中调用同步函数，用 run_in_executor
@app.get("/async-correct")
async def async_correct():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, time.sleep, 5)
    return {"message": "done"}
```

**评分标准：**
- 准确解释 ASGI vs WSGI 区别（3 分）
- 正确实现并发爬取 + 异步写入的完整流程（5 分）
- 能说明 async def 的注意事项（2 分）

---

## 模块四：数据处理框架 — NumPy

### 题目 4.1 NumPy 数组基础（基础）

**题目描述：** 请说明 NumPy 数组（ndarray）相比 Python 原生列表的优势，并演示 NumPy 数组的创建、索引、切片和广播（Broadcasting）机制。

**考察知识点：** NumPy 核心概念 | **能力等级：** 初级

**参考答案：**

**NumPy 优势：**

| 对比维度 | Python 列表 | NumPy ndarray |
|---------|------------|---------------|
| 内存存储 | 存储对象引用（分散） | 连续内存存储（紧凑） |
| 数据类型 | 元素类型可不同 | 所有元素同类型 |
| 运算方式 | 逐元素循环（Python 层） | 向量化运算（C 层） |
| 性能 | 较慢 | 快 10-100 倍 |
| 科学计算 | 需手动实现 | 内置大量数学函数 |

```python
import numpy as np

# ---- 1. 数组创建 ----
# 从列表创建
arr = np.array([1, 2, 3, 4, 5])
print(arr)  # [1 2 3 4 5]

# 特殊数组
zeros = np.zeros((3, 4))        # 3×4 全零矩阵
ones = np.ones((2, 3))          # 2×3 全一矩阵
identity = np.eye(3)            # 3×3 单位矩阵
random_arr = np.random.randn(3, 3)  # 3×3 标准正态分布

# 序列数组
range_arr = np.arange(0, 10, 2)    # [0 2 4 6 8]
linspace = np.linspace(0, 1, 5)    # [0. 0.25 0.5 0.75 1.]

# ---- 2. 索引与切片 ----
arr2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# 基础切片
print(arr2d[0, 1])       # 2（第 0 行第 1 列）
print(arr2d[:, 1])        # [2 5 8]（所有行第 1 列）
print(arr2d[1:, :2])      # [[4 5] [7 8]]

# 花式索引（Fancy Indexing）
print(arr2d[[0, 2]])      # [[1 2 3] [7 8 9]]（取第 0 行和第 2 行）

# 布尔索引
mask = arr2d > 5
print(arr2d[mask])         # [6 7 8 9]（所有 >5 的元素）

# ---- 3. 广播（Broadcasting） ----
# 不同形状的数组在运算时自动扩展
a = np.array([[1, 2, 3], [4, 5, 6]])  # shape (2, 3)
b = np.array([10, 20, 30])             # shape (3,)

# b 广播为 shape (2, 3)：[[10, 20, 30], [10, 20, 30]]
result = a + b
print(result)
# [[11 22 33]
#  [14 25 36]]

# 广播规则示例
c = np.array([[1], [2], [3]])  # shape (3, 1)
d = np.array([10, 20])         # shape (2,)
# c 广播为 (3,2)，d 广播为 (3,2)
print(c + d)
# [[11 21]
#  [12 22]
#  [13 23]]

# ---- 4. 向量化运算 ----
x = np.arange(1_000_000)

# 向量化运算（C 层执行，极快）
y = x * 2 + 1
z = np.sqrt(x)
w = np.sum(x)

# 对比：Python 循环（慢）
# y = [i * 2 + 1 for i in x]  # 慢 10-100 倍
```

**广播规则（从后往前比较）：**
1. 如果维度数不同，在较小数组前面补 1
2. 如果某维度大小不同且不为 1，则报错
3. 如果某维度为 1，则沿该维度复制扩展

**评分标准：**
- 能说明 NumPy 相比列表的优势（3 分）
- 正确演示多种创建和索引方式（3 分）
- 解释广播机制并给出示例（4 分）

---

### 题目 4.2 NumPy 性能优化（进阶）

**题目描述：** 请说明 NumPy 中向量化运算的原理，以及如何避免常见的性能陷阱。给出一个实际场景：计算两个 1000×1000 矩阵的欧氏距离，并对比不同实现方式的性能。

**考察知识点：** 向量化、性能优化 | **能力等级：** 中级

**参考答案：**

**向量化原理：** NumPy 的核心是用 C/Fortran 编写的底层循环替代 Python 层的显式循环，利用 CPU 的 SIMD 指令集和连续内存布局实现高效计算。

```python
import numpy as np
import time

# ---- 场景：计算矩阵 A 中每行与矩阵 B 中每行的欧氏距离 ----
# 结果 shape: (1000, 1000)，result[i][j] = ||A[i] - B[j]||
np.random.seed(42)
n, d = 1000, 100

A = np.random.randn(n, d)
B = np.random.randn(n, d)

# 方法 1：Python 双重循环（最慢，禁止使用）
def euclidean_loop(A, B):
    n = A.shape[0]
    result = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            result[i, j] = np.sqrt(np.sum((A[i] - B[j]) ** 2))
    return result

# 方法 2：部分向量化（单循环）
def euclidean_partial_vec(A, B):
    n = A.shape[0]
    result = np.zeros((n, n))
    for i in range(n):
        # 每行与整个 B 矩阵运算（广播）
        result[i] = np.sqrt(np.sum((A[i] - B) ** 2, axis=1))
    return result

# 方法 3：完全向量化（最优）
def euclidean_full_vec(A, B):
    """
    利用公式: ||A_i - B_j||² = ||A_i||² + ||B_j||² - 2·A_i·B_j^T
    """
    # A 的每行平方和 → shape (n,)
    A_norm = np.sum(A ** 2, axis=1)
    # B 的每行平方和 → shape (n,)
    B_norm = np.sum(B ** 2, axis=1)
    # 内积 → shape (n, n)
    dot_product = A @ B.T
    
    # 广播: (n,1) + (1,n) - 2*(n,n) = (n,n)
    dist_sq = A_norm[:, np.newaxis] + B_norm[np.newaxis, :] - 2 * dot_product
    # 防止负数（浮点误差）
    dist_sq = np.maximum(dist_sq, 0)
    return np.sqrt(dist_sq)

# 方法 4：使用 einsum
def euclidean_einsum(A, B):
    A_norm = np.einsum('ij,ij->i', A, A)
    B_norm = np.einsum('ij,ij->i', B, B)
    dot = np.einsum('ik,jk->ij', A, B)
    return np.sqrt(np.maximum(
        A_norm[:, None] + B_norm[None, :] - 2 * dot, 0
    ))

# ---- 性能对比 ----
# 预期结果（相对速度）：
# 方法 1 (双重循环): ~100x 基准
# 方法 2 (部分向量化): ~10x 基准
# 方法 3 (完全向量化): 1x 基准（最快）
# 方法 4 (einsum): ~1.2x 基准
```

**常见性能陷阱与优化技巧：**

```python
# ❌ 陷阱 1：在循环中动态追加数组
result = np.array([])
for i in range(10000):
    result = np.append(result, i)  # 每次创建新数组，O(n²)

# ✅ 正确：预分配数组
result = np.empty(10000)
for i in range(10000):
    result[i] = i

# ❌ 陷阱 2：不必要的拷贝
a = np.random.randn(1000, 1000)
b = a.copy()  # 如果不是必须，避免拷贝

# ✅ 使用视图（切片）而不是拷贝
b = a[:500, :]  # 视图，不拷贝数据

# ❌ 陷阱 3：在 NumPy 和 Python 之间频繁转换
for i in range(1000):
    val = arr[i].item()  # 逐个转换为 Python 标量

# ✅ 保持数据在 NumPy 中处理
result = np.sum(arr * 2 + 1)  # 全程 NumPy 运算

# ❌ 陷阱 4：使用 Python 循环处理数组
sum_val = sum(arr)  # Python sum，慢

# ✅ 使用 NumPy 内置函数
sum_val = np.sum(arr)  # NumPy sum，快

# 常用优化技巧：
# 1. 使用 np.where 替代条件循环
# 2. 使用 np.select 处理多条件
# 3. 使用 np.clip 限制值范围
# 4. 使用 np.digitize 离散化
# 5. 优先使用 in-place 操作: arr += 1 而非 arr = arr + 1
```

**评分标准：**
- 解释向量化运算原理（3 分）
- 给出至少 3 种实现并对比性能（4 分）
- 能列举 3 个以上常见性能陷阱（3 分）

---

## 模块五：数据处理框架 — Pandas

### 题目 5.1 Pandas 核心数据结构（基础）

**题目描述：** 请说明 Pandas 中 Series 和 DataFrame 的区别，演示常用操作：数据筛选、分组聚合、缺失值处理、合并连接。

**考察知识点：** Pandas 基础操作 | **能力等级：** 初级

**参考答案：**

```python
import pandas as pd
import numpy as np

# ---- 创建数据结构 ----
# Series：一维带标签数组
s = pd.Series([10, 20, 30, 40], index=['a', 'b', 'c', 'd'])
print(s['b'])  # 20

# DataFrame：二维表格
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'age': [25, 30, 35, 28, 32],
    'city': ['Beijing', 'Shanghai', 'Beijing', 'Shenzhen', 'Shanghai'],
    'salary': [15000, 20000, 25000, 18000, 22000],
    'department': ['Tech', 'Sales', 'Tech', 'HR', 'Sales']
})

# ---- 1. 数据筛选 ----
# 条件筛选
tech_employees = df[df['department'] == 'Tech']
#    name  age     city  salary department
# 0  Alice   25  Beijing   15000       Tech
# 2  Charlie 35  Beijing   25000       Tech

# 多条件筛选
high_salary_tech = df[(df['salary'] > 15000) & (df['department'] == 'Tech')]
# 使用 query 方法（更简洁）
high_salary_tech = df.query('salary > 15000 and department == "Tech"')

# loc 和 iloc
print(df.loc[0, 'name'])          # 'Alice'（标签索引）
print(df.iloc[0, 0])              # 'Alice'（位置索引）
print(df.loc[0:2, ['name', 'age']])  # 切片（loc 包含右端点）

# ---- 2. 分组聚合 ----
# 按部门统计
dept_stats = df.groupby('department').agg({
    'salary': ['mean', 'max', 'min', 'count'],
    'age': 'mean'
})
print(dept_stats)

# 按城市分组，计算薪资统计
city_stats = df.groupby('city')['salary'].agg(['mean', 'sum', 'count'])
#             mean    sum  count
# Beijing   20000  40000      2
# Shanghai  21000  42000      2
# Shenzhen  18000  18000      1

# transform：保持原形状
df['salary_dept_avg'] = df.groupby('department')['salary'].transform('mean')
# 每人薪资与部门平均薪资对比

# ---- 3. 缺失值处理 ----
df2 = pd.DataFrame({
    'A': [1, 2, np.nan, 4],
    'B': [5, np.nan, np.nan, 8],
    'C': [9, 10, 11, 12]
})

# 检测缺失值
print(df2.isna().sum())  # 每列缺失值数量

# 删除含缺失值的行
df2.dropna()             # 删除任何含 NaN 的行
df2.dropna(subset=['A']) # 仅根据 A 列删除

# 填充缺失值
df2.fillna(0)                      # 填充为 0
df2.fillna(method='ffill')         # 前向填充（用前一个值填充）
df2['A'].fillna(df2['A'].mean())   # 用均值填充

# ---- 4. 合并连接 ----
left = pd.DataFrame({
    'id': [1, 2, 3, 4],
    'name': ['Alice', 'Bob', 'Charlie', 'Diana']
})
right = pd.DataFrame({
    'id': [1, 2, 3, 5],
    'score': [90, 85, 95, 88]
})

# 内连接
inner_join = pd.merge(left, right, on='id', how='inner')
# 只保留两边都有的 id

# 左连接
left_join = pd.merge(left, right, on='id', how='left')
# 保留左表所有行，右表缺失填 NaN

# 外连接
outer_join = pd.merge(left, right, on='id', how='outer')

# 纵向拼接
df_concat = pd.concat([left, right], axis=0)  # 纵向
df_concat = pd.concat([left, right], axis=1)  # 横向
```

**Series vs DataFrame：**

| 特性 | Series | DataFrame |
|------|--------|-----------|
| 维度 | 1 维 | 2 维（行列） |
| 类比 | Excel 中的一列 | Excel 中的整个表格 |
| 索引 | 单索引 | 行索引 + 列索引 |
| 数据类型 | 单一类型 | 每列可不同类型 |

**评分标准：**
- 正确创建并操作 Series/DataFrame（3 分）
- 熟练使用分组聚合和条件筛选（4 分）
- 正确处理缺失值和合并连接（3 分）

---

### 题目 5.2 Pandas 时间序列与窗口函数（进阶）

**题目描述：** 请说明 Pandas 处理时间序列数据的核心能力，演示重采样、滚动窗口、移动平均等操作。实现场景：给定某股票一年日线数据，计算 5 日、20 日移动均线，并识别金叉/死叉信号。

**考察知识点：** 时间序列、窗口函数 | **能力等级：** 中级

**参考答案：**

```python
import pandas as pd
import numpy as np

# ---- 模拟股票日线数据 ----
np.random.seed(42)
dates = pd.date_range('2024-01-01', '2024-12-31', freq='B')  # 工作日

# 模拟价格走势（随机游走）
returns = np.random.randn(len(dates)) * 0.02
price = 100 * np.exp(np.cumsum(returns))

df = pd.DataFrame({
    'date': dates,
    'open': price * (1 + np.random.randn(len(dates)) * 0.005),
    'high': price * (1 + np.abs(np.random.randn(len(dates)) * 0.01)),
    'low': price * (1 - np.abs(np.random.randn(len(dates)) * 0.01)),
    'close': price,
    'volume': np.random.randint(1000000, 10000000, len(dates))
})
df.set_index('date', inplace=True)

# ---- 1. 时间序列基础操作 ----
# 索引切片
df_jan = df['2024-01']        # 2024年1月数据
df_q1 = df['2024-01':'2024-03']  # 第一季度数据

# 重采样（Resample）
# 日线 → 周线
weekly = df.resample('W').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
})

# 日线 → 月线（OHLC）
monthly = df.resample('ME').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
})

# ---- 2. 滚动窗口与移动平均 ----
# 计算移动均线
df['MA5'] = df['close'].rolling(window=5).mean()   # 5 日均线
df['MA20'] = df['close'].rolling(window=20).mean()  # 20 日均线
df['MA60'] = df['close'].rolling(window=60).mean()  # 60 日均线

# 指数加权移动平均（EMA）
df['EMA12'] = df['close'].ewm(span=12, adjust=False).mean()
df['EMA26'] = df['close'].ewm(span=26, adjust=False).mean()

# 布林带（Bollinger Bands）
df['BB_MID'] = df['close'].rolling(20).mean()
df['BB_STD'] = df['close'].rolling(20).std()
df['BB_UPPER'] = df['BB_MID'] + 2 * df['BB_STD']
df['BB_LOWER'] = df['BB_MID'] - 2 * df['BB_STD']

# ---- 3. 金叉/死叉识别 ----
# 金叉：短期均线从下方上穿长期均线
# 死叉：短期均线从上方下穿长期均线

# 计算均线差值
df['MA_diff'] = df['MA5'] - df['MA20']

# 金叉条件：前一天差值 < 0 且当天差值 > 0
df['golden_cross'] = (df['MA_diff'] > 0) & (df['MA_diff'].shift(1) < 0)

# 死叉条件：前一天差值 > 0 且当天差值 < 0
df['death_cross'] = (df['MA_diff'] < 0) & (df['MA_diff'].shift(1) > 0)

# 统计信号
golden_count = df['golden_cross'].sum()
death_count = df['death_cross'].sum()
print(f"金叉信号: {golden_count} 次, 死叉信号: {death_count} 次")

# 获取信号出现日期
golden_dates = df[df['golden_cross']].index
death_dates = df[df['death_cross']].index

# ---- 4. 滚动窗口高级应用 ----
# 滚动波动率
df['volatility'] = df['close'].pct_change().rolling(20).std() * np.sqrt(252)

# 滚动相关系数
df['price_vol_corr'] = df['close'].rolling(60).corr(df['volume'])

# 滚动最大回撤
def max_drawdown(series):
    rolling_max = series.cummax()
    drawdown = (series - rolling_max) / rolling_max
    return drawdown.min()

df['max_dd_60d'] = df['close'].rolling(60).apply(max_drawdown)

# ---- 5. shift 与 pct_change 常用操作 ----
df['prev_close'] = df['close'].shift(1)     # 前一日收盘价
df['daily_return'] = df['close'].pct_change()  # 日收益率
df['cum_return'] = (1 + df['daily_return']).cumprod() - 1  # 累计收益率

# ---- 6. 日期功能 ----
df['year'] = df.index.year
df['month'] = df.index.month
df['day_of_week'] = df.index.dayofweek  # 周一=0, 周日=6
df['is_month_end'] = df.index.is_month_end

# 按月份统计月收益
monthly_returns = df.groupby(['year', 'month'])['daily_return'].apply(
    lambda x: (1 + x).prod() - 1
)
```

**常见时间频率代码：**

| 代码 | 含义 | 代码 | 含义 |
|------|------|------|------|
| `D` | 日历日 | `W` | 周 |
| `B` | 工作日 | `ME` | 月末 |
| `H` | 小时 | `QE` | 季末 |
| `T/min` | 分钟 | `YE` | 年末 |
| `S` | 秒 | `MS` | 月初 |

**评分标准：**
- 熟练使用重采样和滚动窗口（4 分）
- 正确实现金叉/死叉信号识别（3 分）
- 展示时间序列的高级操作（3 分）

---

### 题目 5.3 Pandas 大数据处理优化（高级）

**题目描述：** 你有一个 10GB 的 CSV 文件需要处理，内存只有 8GB。请说明 Pandas 处理大数据的策略，并演示分块读取、类型优化、并行处理等方法。

**考察知识点：** 大数据处理、内存优化 | **能力等级：** 高级

**参考答案：**

```python
import pandas as pd
import numpy as np
from multiprocessing import Pool
import gc

# ---- 策略 1：分块读取（Chunking） ----
def process_large_csv_chunked(filepath, chunksize=100000):
    """
    分块读取大文件，逐块处理并聚合结果
    """
    results = []
    
    # 使用 chunksize 参数分块读取
    for chunk in pd.read_csv(filepath, chunksize=chunksize):
        # 在当前块上操作
        chunk['new_col'] = chunk['col_a'] + chunk['col_b']
        
        # 聚合当前块的结果
        agg_result = chunk.groupby('category')['value'].agg(['sum', 'count'])
        results.append(agg_result)
        
        # 手动释放内存
        del chunk
        gc.collect()
    
    # 合并所有块的结果
    final_result = pd.concat(results).groupby(level=0).sum()
    return final_result

# 使用迭代器方式
reader = pd.read_csv('large_file.csv', chunksize=100000)
total_rows = 0
for chunk in reader:
    total_rows += len(chunk)
    # 处理逻辑...

# ---- 策略 2：指定数据类型优化内存 ----
# 查看每列内存占用
df_sample = pd.read_csv('large_file.csv', nrows=1000)
print(df_sample.dtypes)
print(df_sample.memory_usage(deep=True))

# 手动指定低精度类型
dtype_dict = {
    'id': 'int32',               # 默认 int64 → int32（节省 50%）
    'category': 'category',      # 字符串 → category（大幅节省）
    'flag': 'bool',              # int → bool
    'score': 'float32',          # float64 → float32（节省 50%）
    'small_int': 'int8',         # 0-255 范围的值用 int8
    'date': 'string',            # 使用 PyArrow string 类型
}

# 使用指定的数据类型读取
df = pd.read_csv(
    'large_file.csv',
    dtype=dtype_dict,
    parse_dates=['date_column'],  # 直接解析日期列
    low_memory=False
)

# 读取后优化现有 DataFrame
def optimize_dataframe(df):
    """优化 DataFrame 内存占用"""
    for col in df.columns:
        col_type = df[col].dtype
        
        # 整数列优化
        if col_type == 'int64':
            c_min, c_max = df[col].min(), df[col].max()
            if c_min >= 0:
                if c_max < 256:
                    df[col] = df[col].astype('uint8')
                elif c_max < 65536:
                    df[col] = df[col].astype('uint16')
                elif c_max < 4294967296:
                    df[col] = df[col].astype('uint32')
            else:
                if c_min > -128 and c_max < 127:
                    df[col] = df[col].astype('int8')
                elif c_min > -32768 and c_max < 32767:
                    df[col] = df[col].astype('int16')
                elif c_min > -2147483648 and c_max < 2147483647:
                    df[col] = df[col].astype('int32')
        
        # 浮点列优化
        elif col_type == 'float64':
            df[col] = df[col].astype('float32')
        
        # 字符串列优化
        elif col_type == 'object':
            # 如果唯一值很少，转为 category
            if df[col].nunique() / len(df) < 0.5:
                df[col] = df[col].astype('category')
    
    return df

# ---- 策略 3：仅读取需要的列 ----
df = pd.read_csv(
    'large_file.csv',
    usecols=['col_a', 'col_b', 'col_c'],  # 只读取需要的列
    nrows=1000000  # 如果只需要前 N 行
)

# ---- 策略 4：使用替代引擎 ----
# 使用 PyArrow 引擎（更快，内存更省）
df = pd.read_csv('large_file.csv', engine='pyarrow')

# 使用 Parquet 格式替代 CSV（列式存储，压缩比高，读取快）
df.to_parquet('data.parquet', compression='snappy')
df = pd.read_parquet('data.parquet')

# 使用 Dask 处理超大数据集（类似 Pandas API，支持分布式）
import dask.dataframe as dd
ddf = dd.read_csv('large_file.csv')
# Dask 延迟计算，只在需要时求值
result = ddf.groupby('category')['value'].mean().compute()

# ---- 策略 5：并行处理 ----
def parallel_process_chunk(filepath):
    """并行处理文件分片"""
    return process_chunk(filepath)

# 使用 multiprocessing
with Pool(processes=4) as pool:
    results = pool.map(parallel_process_chunk, file_chunks)

# 使用 pandas 的 apply 并行（需要 swifter 库）
# import swifter
# df['new_col'] = df['col'].swifter.apply(heavy_function)

# ---- 策略 6：迭代逐行处理（适用于极大数据） ----
# 使用迭代器逐行处理（最慢但最省内存）
with open('large_file.csv') as f:
    header = f.readline()
    for line in f:
        # 逐行处理
        process_single_line(line)

# ---- 内存监控 ----
def print_memory_usage(df):
    """打印 DataFrame 内存占用"""
    mem_usage = df.memory_usage(deep=True)
    total_mb = mem_usage.sum() / 1024 / 1024
    print(f"总内存占用: {total_mb:.2f} MB")
    print("各列内存占用:")
    for col, mem in mem_usage.items():
        print(f"  {col}: {mem / 1024 / 1024:.2f} MB")
```

**策略总结：**

| 策略 | 适用场景 | 内存节省 | 性能影响 |
|------|---------|---------|---------|
| 分块读取 | 需聚合计算 | 高 | 中 |
| 类型优化 | 通用 | 50-80% | 无 |
| 只读所需列 | 列数多但只用到少数 | 按列数比例 | 提升 |
| 使用 Parquet | 长期存储/反复读取 | 高 | 显著提升 |
| 使用 Dask | 多文件/分布式 | 高 | 提升 |
| 使用 category | 字符串列唯一值少 | 90%+ | 提升 |

**评分标准：**
- 说明至少 3 种大数据处理策略（3 分）
- 展示分块读取和类型优化的完整代码（4 分）
- 了解 Dask 等替代方案（3 分）

---

## 模块六：机器学习框架 — TensorFlow

### 题目 6.1 TensorFlow 核心概念（基础）

**题目描述：** 请说明 TensorFlow 中张量（Tensor）、计算图（Graph）和会话（Session）的关系，并演示 TensorFlow 2.x 中 Keras 的 Sequential API 和 Functional API 构建模型的方式。

**考察知识点：** TensorFlow 基础 | **能力等级：** 初级

**参考答案：**

**核心概念：**

| 概念 | 说明 | TensorFlow 1.x | TensorFlow 2.x |
|------|------|---------------|---------------|
| **Tensor** | 多维数组，数据载体 | 同 | 同 |
| **Graph** | 计算图，定义计算流程 | 静态图，需显式构建 | 动态图（Eager Execution），自动构建 |
| **Session** | 执行计算图的环境 | 必须创建 Session 运行 | 无需 Session，直接执行 |

```python
import tensorflow as tf
import numpy as np

# ---- 张量基础操作 ----
# 创建张量
tensor = tf.constant([[1, 2], [3, 4]], dtype=tf.float32)
print(tensor.shape)   # (2, 2)
print(tensor.dtype)   # tf.float32

# 张量运算
a = tf.constant([1, 2, 3])
b = tf.constant([4, 5, 6])
c = tf.add(a, b)          # [5, 7, 9]
d = tf.matmul(a, b)       # 报错（一维不支持矩阵乘）
e = tf.tensordot(a, b, axes=1)  # 32（点积）

# 转换为 NumPy
np_array = tensor.numpy()

# GPU 检测
print("GPU 可用:", tf.config.list_physical_devices('GPU'))

# ---- 1. Sequential API（顺序模型） ----
# 适用于层与层之间线性堆叠的简单模型
model_seq = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu', input_shape=(784,)),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(10, activation='softmax')
])

model_seq.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# 训练（模拟 MNIST 数据）
# model_seq.fit(x_train, y_train, epochs=5, validation_split=0.2)

# ---- 2. Functional API（函数式模型） ----
# 适用于多输入/多输出、共享层、残差连接等复杂拓扑
inputs = tf.keras.Input(shape=(784,))
x = tf.keras.layers.Dense(128, activation='relu')(inputs)
x = tf.keras.layers.Dropout(0.2)(x)
x = tf.keras.layers.Dense(64, activation='relu')(x)
x = tf.keras.layers.Dropout(0.2)(x)
outputs = tf.keras.layers.Dense(10, activation='softmax')(x)

model_func = tf.keras.Model(inputs=inputs, outputs=outputs, name='functional_model')

model_func.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# ---- 多输入多输出示例（Functional API 优势） ----
# 场景：同时输入图片和元数据，输出分类和回归结果
image_input = tf.keras.Input(shape=(224, 224, 3), name='image')
metadata_input = tf.keras.Input(shape=(10,), name='metadata')

# 图片分支
x = tf.keras.layers.Conv2D(32, 3, activation='relu')(image_input)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dense(64, activation='relu')(x)

# 合并分支
combined = tf.keras.layers.Concatenate()([x, metadata_input])
combined = tf.keras.layers.Dense(32, activation='relu')(combined)

# 多输出
class_output = tf.keras.layers.Dense(10, activation='softmax', name='class')(combined)
reg_output = tf.keras.layers.Dense(1, name='regression')(combined)

multi_model = tf.keras.Model(
    inputs=[image_input, metadata_input],
    outputs=[class_output, reg_output]
)

multi_model.compile(
    optimizer='adam',
    loss={'class': 'categorical_crossentropy', 'regression': 'mse'},
    loss_weights={'class': 1.0, 'regression': 0.5},
    metrics={'class': 'accuracy'}
)
```

**评分标准：**
- 准确解释 Tensor、Graph、Session 关系（3 分）
- 演示 Sequential API 构建模型（3 分）
- 演示 Functional API 及多输入多输出（4 分）

---

### 题目 6.2 TensorFlow 自定义训练与模型保存（进阶）

**题目描述：** 请实现一个自定义训练循环（不使用 model.fit），包括自定义损失函数和梯度计算，并说明 TensorFlow 模型保存的不同方式（SavedModel、H5、Checkpoint）及其适用场景。

**考察知识点：** 自定义训练、模型持久化 | **能力等级：** 中级

**参考答案：**

```python
import tensorflow as tf
import numpy as np

# ---- 自定义模型 ----
class MyModel(tf.keras.Model):
    def __init__(self):
        super().__init__()
        self.dense1 = tf.keras.layers.Dense(128, activation='relu')
        self.dropout = tf.keras.layers.Dropout(0.2)
        self.dense2 = tf.keras.layers.Dense(10)
    
    def call(self, inputs, training=False):
        x = self.dense1(inputs)
        x = self.dropout(x, training=training)
        return self.dense2(x)

# ---- 自定义损失函数 ----
def custom_loss(y_true, y_pred):
    """
    组合损失：交叉熵 + L2 正则化 + 自定义惩罚项
    """
    # 交叉熵损失
    cce = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    ce_loss = cce(y_true, y_pred)
    
    # L2 正则化
    l2_loss = tf.reduce_sum([
        tf.nn.l2_loss(var) for var in model.trainable_variables
    ]) * 0.001
    
    # 自定义惩罚项：惩罚预测概率过于集中在单一类别
    probs = tf.nn.softmax(y_pred)
    entropy = -tf.reduce_sum(probs * tf.math.log(probs + 1e-8), axis=-1)
    entropy_penalty = tf.reduce_mean(entropy) * 0.01
    
    return ce_loss + l2_loss + entropy_penalty

# ---- 自定义评估指标 ----
class F1Score(tf.keras.metrics.Metric):
    def __init__(self, name='f1_score', **kwargs):
        super().__init__(name=name, **kwargs)
        self.tp = self.add_weight(name='tp', initializer='zeros')
        self.fp = self.add_weight(name='fp', initializer='zeros')
        self.fn = self.add_weight(name='fn', initializer='zeros')
    
    def update_state(self, y_true, y_pred, sample_weight=None):
        y_pred = tf.argmax(y_pred, axis=1)
        y_true = tf.cast(y_true, tf.int64)
        
        tp = tf.cast(tf.math.count_nonzero(y_pred * y_true), tf.float32)
        fp = tf.cast(tf.math.count_nonzero(y_pred * (1 - y_true)), tf.float32)
        fn = tf.cast(tf.math.count_nonzero((1 - y_pred) * y_true), tf.float32)
        
        self.tp.assign_add(tp)
        self.fp.assign_add(fp)
        self.fn.assign_add(fn)
    
    def result(self):
        precision = self.tp / (self.tp + self.fp + 1e-7)
        recall = self.tp / (self.tp + self.fn + 1e-7)
        return 2 * precision * recall / (precision + recall + 1e-7)
    
    def reset_state(self):
        self.tp.assign(0.0)
        self.fp.assign(0.0)
        self.fn.assign(0.0)

# ---- 自定义训练循环 ----
model = MyModel()
optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
loss_metric = tf.keras.metrics.Mean(name='train_loss')
accuracy_metric = tf.keras.metrics.SparseCategoricalAccuracy()
f1_metric = F1Score()

# 检查点管理器
checkpoint = tf.train.Checkpoint(
    model=model,
    optimizer=optimizer
)
checkpoint_manager = tf.train.CheckpointManager(
    checkpoint, './checkpoints', max_to_keep=3
)

# 模拟数据
x_train = np.random.randn(1000, 784).astype(np.float32)
y_train = np.random.randint(0, 10, 1000).astype(np.int32)
train_dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train))
train_dataset = train_dataset.shuffle(1000).batch(32)

@tf.function  # 编译为计算图，加速训练
def train_step(x, y):
    with tf.GradientTape() as tape:
        predictions = model(x, training=True)
        loss = custom_loss(y, predictions)
    
    # 计算梯度并更新参数
    gradients = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))
    
    # 更新指标
    loss_metric.update_state(loss)
    accuracy_metric.update_state(y, predictions)
    f1_metric.update_state(y, predictions)
    
    return loss

# 训练循环
EPOCHS = 10
best_loss = float('inf')

for epoch in range(EPOCHS):
    # 重置指标
    loss_metric.reset_state()
    accuracy_metric.reset_state()
    f1_metric.reset_state()
    
    for step, (x_batch, y_batch) in enumerate(train_dataset):
        loss = train_step(x_batch, y_batch)
    
    # 打印指标
    print(f'Epoch {epoch + 1}: '
          f'Loss: {loss_metric.result():.4f}, '
          f'Accuracy: {accuracy_metric.result():.4f}, '
          f'F1: {f1_metric.result():.4f}')
    
    # 保存最佳模型
    if loss_metric.result() < best_loss:
        best_loss = loss_metric.result()
        checkpoint_manager.save()
        print(f'  → 保存最佳模型 (loss: {best_loss:.4f})')

# ---- 模型保存的三种方式 ----
# 方式 1：SavedModel（推荐，TensorFlow Serving 部署）
model.save('saved_model/my_model', save_format='tf')
# 加载
loaded_model = tf.keras.models.load_model('saved_model/my_model')

# 方式 2：H5 格式（单个文件，兼容性好）
model.save('my_model.h5')
# 加载
loaded_model = tf.keras.models.load_model('my_model.h5')

# 方式 3：Checkpoint（仅保存权重，训练中断恢复）
model.save_weights('./checkpoints/my_weights')
# 加载权重
model.load_weights('./checkpoints/my_weights')

# 恢复训练状态（包括优化器状态）
checkpoint.restore(checkpoint_manager.latest_checkpoint)
```

**三种保存方式对比：**

| 方式 | 保存内容 | 文件 | 适用场景 |
|------|---------|------|---------|
| **SavedModel** | 完整模型 + 计算图 | 目录 | 生产部署、TF Serving |
| **H5** | 模型架构 + 权重 + 配置 | 单个 .h5 | 模型交换、简单部署 |
| **Checkpoint** | 权重 + 优化器状态 | 多个文件 | 训练中断恢复、微调 |

**评分标准：**
- 正确实现自定义训练循环（5 分）
- 实现自定义损失函数和指标（3 分）
- 区分三种保存方式并说明适用场景（2 分）

---

## 模块七：机器学习框架 — PyTorch

### 题目 7.1 PyTorch 核心概念（基础）

**题目描述：** 请说明 PyTorch 中 Tensor、Autograd 和 nn.Module 的关系，并演示使用 PyTorch 构建一个简单的全连接神经网络完成 MNIST 分类任务。

**考察知识点：** PyTorch 基础 | **能力等级：** 初级

**参考答案：**

**核心概念：**

| 概念 | 说明 | 作用 |
|------|------|------|
| **Tensor** | 多维数组，类似 NumPy ndarray | 数据载体，支持 GPU 加速 |
| **Autograd** | 自动微分引擎 | 自动计算梯度，支持反向传播 |
| **nn.Module** | 神经网络模块基类 | 封装层、参数和 forward 逻辑 |

```python
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# ---- 设备配置 ----
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'使用设备: {device}')

# ---- 数据加载 ----
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))  # MNIST 均值和标准差
])

train_dataset = datasets.MNIST(
    './data', train=True, download=True, transform=transform
)
test_dataset = datasets.MNIST(
    './data', train=False, transform=transform
)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False)

# ---- 模型定义 ----
class MNISTNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(28 * 28, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, 10)
        self.dropout = nn.Dropout(0.2)
        self.bn1 = nn.BatchNorm1d(512)
        self.bn2 = nn.BatchNorm1d(256)
    
    def forward(self, x):
        x = x.view(-1, 28 * 28)  # 展平
        x = self.bn1(F.relu(self.fc1(x)))
        x = self.dropout(x)
        x = self.bn2(F.relu(self.fc2(x)))
        x = self.dropout(x)
        x = self.fc3(x)  # 不在这里用 softmax，CrossEntropyLoss 内置了
        return x

model = MNISTNet().to(device)

# ---- 损失函数与优化器 ----
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

# ---- 训练函数 ----
def train(model, loader, criterion, optimizer, epoch):
    model.train()
    total_loss = 0
    correct = 0
    
    for batch_idx, (data, target) in enumerate(loader):
        data, target = data.to(device), target.to(device)
        
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        pred = output.argmax(dim=1)
        correct += pred.eq(target).sum().item()
    
    accuracy = 100. * correct / len(loader.dataset)
    avg_loss = total_loss / len(loader)
    print(f'Train Epoch {epoch}: Loss={avg_loss:.4f}, Accuracy={accuracy:.2f}%')

# ---- 测试函数 ----
@torch.no_grad()  # 禁用梯度计算，节省内存和计算
def test(model, loader, criterion):
    model.eval()
    test_loss = 0
    correct = 0
    
    for data, target in loader:
        data, target = data.to(device), target.to(device)
        output = model(data)
        test_loss += criterion(output, target).item()
        pred = output.argmax(dim=1)
        correct += pred.eq(target).sum().item()
    
    test_loss /= len(loader)
    accuracy = 100. * correct / len(loader.dataset)
    print(f'Test: Loss={test_loss:.4f}, Accuracy={accuracy:.2f}%')
    return accuracy

# ---- 训练循环 ----
for epoch in range(1, 11):
    train(model, train_loader, criterion, optimizer, epoch)
    test(model, test_loader, criterion)
    scheduler.step()

# ---- 保存模型 ----
torch.save(model.state_dict(), 'mnist_model.pth')
# 加载模型
# model.load_state_dict(torch.load('mnist_model.pth'))
```

**评分标准：**
- 解释 Tensor、Autograd、nn.Module 关系（3 分）
- 正确构建全连接网络并训练（4 分）
- 展示 train/test 模式切换和 GPU 使用（3 分）

---

### 题目 7.2 PyTorch 动态图与梯度机制（进阶）

**题目描述：** 请解释 PyTorch 动态计算图的优势，对比 TensorFlow 1.x 的静态图。演示 `torch.no_grad()`、`detach()`、`zero_grad()` 的使用场景，并实现一个自定义的 `autograd.Function`。

**考察知识点：** 动态图、自动微分 | **能力等级：** 中级

**参考答案：**

**动态图 vs 静态图：**

| 特性 | PyTorch（动态图） | TensorFlow 1.x（静态图） |
|------|-----------------|----------------------|
| 图构建 | 运行时动态构建 | 先定义后执行 |
| 调试 | 可用 Python 调试器 | 难以调试（图中执行） |
| 控制流 | 原生 Python if/for | 需要 tf.cond/tf.while_loop |
| 灵活性 | 高（可变长度输入等） | 低（需预先定义） |
| 性能 | 较慢（图重建开销） | 较快（图编译优化） |
| 部署 | 需 TorchScript | 直接导出 |

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

# ---- 动态图演示 ----
# 每次前向传播可以有不同的计算图结构
model = nn.Linear(10, 2)

# 输入 1：batch_size=3
x1 = torch.randn(3, 10)
out1 = model(x1)  # 计算图形状: (3, 10) -> (3, 2)

# 输入 2：batch_size=5（不同形状，动态适应）
x2 = torch.randn(5, 10)
out2 = model(x2)  # 计算图形状: (5, 10) -> (5, 2)

# 动态控制流（每次前向传播图结构可以不同）
class DynamicNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(10, 10)
        self.fc2 = nn.Linear(10, 10)
    
    def forward(self, x, num_layers=2):
        """根据参数动态决定网络层数"""
        x = F.relu(self.fc1(x))
        if num_layers > 1:
            x = F.relu(self.fc2(x))  # 动态添加层
        return x

dynet = DynamicNet()
print(dynet(torch.randn(3, 10), num_layers=1).shape)  # 使用 1 层
print(dynet(torch.randn(3, 10), num_layers=2).shape)  # 使用 2 层

# ---- no_grad() vs detach() vs zero_grad() ----

# 1. torch.no_grad()：上下文管理器，禁用梯度计算
# 适用场景：推理、评估时节省内存和加速
@torch.no_grad()
def inference(model, data):
    return model(data)

# 等价于：
with torch.no_grad():
    output = model(data)

# 2. tensor.detach()：从计算图中分离张量
# 适用场景：需要张量的值但不需梯度，如日志记录、可视化
x = torch.tensor([1., 2., 3.], requires_grad=True)
y = x ** 2
z = y.detach()  # z 与 y 值相同，但无梯度
z_np = y.detach().cpu().numpy()  # 转换为 numpy 的常用方式

# 3. optimizer.zero_grad()：清零梯度
# 适用场景：每次反向传播前必须清零，否则梯度会累积
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
for data, target in dataloader:
    optimizer.zero_grad()  # 必须清零！否则梯度累积
    output = model(data)
    loss = criterion(output, target)
    loss.backward()
    optimizer.step()

# 梯度累积技巧（模拟大 batch size）
accumulation_steps = 4
for i, (data, target) in enumerate(dataloader):
    output = model(data)
    loss = criterion(output, target) / accumulation_steps
    loss.backward()  # 梯度累积
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()    # 更新参数
        optimizer.zero_grad()  # 清零梯度

# ---- 自定义 autograd.Function ----
class MyReLU(torch.autograd.Function):
    """
    自定义 ReLU 激活函数的前向和反向传播
    """
    @staticmethod
    def forward(ctx, input):
        """
        ctx: 上下文对象，用于保存反向传播需要的信息
        """
        ctx.save_for_backward(input)  # 保存输入，用于反向传播
        return input.clamp(min=0)     # max(0, x)
    
    @staticmethod
    def backward(ctx, grad_output):
        """
        grad_output: 上游传来的梯度
        """
        input, = ctx.saved_tensors  # 取出保存的输入
        grad_input = grad_output.clone()
        grad_input[input < 0] = 0   # ReLU 导数: x>0 时为 1，否则为 0
        return grad_input

# 使用自定义函数
class MyModel(nn.Module):
    def forward(self, x):
        return MyReLU.apply(x)  # 使用 .apply() 调用自定义 Function

# ---- 自定义更复杂的 Function 示例 ----
class GradientReversal(torch.autograd.Function):
    """
    梯度反转层（用于域对抗训练）
    前向传播：恒等映射
    反向传播：梯度乘以 -lambda
    """
    @staticmethod
    def forward(ctx, x, lambda_):
        ctx.lambda_ = lambda_
        return x.view_as(x)
    
    @staticmethod
    def backward(ctx, grad_output):
        return grad_output.neg() * ctx.lambda_, None  # 反转梯度

# 使用梯度反转
def grad_reverse(x, lambda_=1.0):
    return GradientReversal.apply(x, lambda_)
```

**评分标准：**
- 解释动态图优势并与静态图对比（3 分）
- 区分 no_grad/detach/zero_grad 使用场景（3 分）
- 正确实现自定义 autograd.Function（4 分）

---

### 题目 7.3 PyTorch 分布式训练（高级）

**题目描述：** 请说明 PyTorch 分布式训练的主要方式（DataParallel、DistributedDataParallel），对比其优缺点，并演示使用 DDP 进行多卡训练的完整代码。

**考察知识点：** 分布式训练 | **能力等级：** 高级

**参考答案：**

**DataParallel vs DistributedDataParallel：**

| 特性 | DataParallel (DP) | DistributedDataParallel (DDP) |
|------|------------------|-------------------------------|
| 实现方式 | 单进程多线程 | 多进程（每 GPU 一个进程） |
| Python GIL | 受 GIL 限制 | 不受 GIL 限制 |
| 通信方式 | 主 GPU 聚合 → 广播 | all-reduce 环形通信 |
| 性能 | 较差（主 GPU 负载不均） | 优秀（负载均衡） |
| 梯度同步 | 每次前向传播都同步 | 反向传播时异步通信 |
| 代码修改 | 简单（一行包装） | 需要进程管理 |
| 多机训练 | 不支持 | 支持 |
| 推荐度 | 不推荐（已废弃） | 强烈推荐 |

```python
# ---- DDP 训练脚本：train_ddp.py ----
import torch
import torch.nn as nn
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, DistributedSampler
import os

# 1. 模型定义
class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(784, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 10),
        )
    
    def forward(self, x):
        return self.net(x.view(x.size(0), -1))

# 2. 训练函数
def train(rank, world_size):
    """每个进程执行的训练函数"""
    # ---- 初始化进程组 ----
    dist.init_process_group(
        backend='nccl',  # GPU 使用 nccl，CPU 使用 gloo
        init_method='env://',  # 从环境变量读取配置
        rank=rank,
        world_size=world_size
    )
    
    # ---- 设置设备 ----
    torch.cuda.set_device(rank)
    device = torch.device(f'cuda:{rank}')
    
    # ---- 模型初始化 ----
    model = MyModel().to(device)
    model = DDP(
        model,
        device_ids=[rank],
        output_device=rank,
        find_unused_parameters=False  # 如果模型有未使用的参数设置为 True
    )
    
    # ---- 数据加载（使用 DistributedSampler） ----
    dataset = torch.utils.data.TensorDataset(
        torch.randn(10000, 784),
        torch.randint(0, 10, (10000,))
    )
    sampler = DistributedSampler(
        dataset,
        num_replicas=world_size,
        rank=rank,
        shuffle=True,
        drop_last=True
    )
    dataloader = DataLoader(
        dataset,
        batch_size=64,
        sampler=sampler,  # 注意：使用 sampler 时不设 shuffle
        num_workers=4,
        pin_memory=True
    )
    
    # ---- 损失函数与优化器 ----
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.5)
    
    # ---- 训练循环 ----
    for epoch in range(10):
        # 每个 epoch 设置 sampler 的 epoch（确保数据打乱）
        sampler.set_epoch(epoch)
        
        model.train()
        total_loss = torch.tensor(0.0).to(device)
        correct = torch.tensor(0).to(device)
        total_samples = torch.tensor(0).to(device)
        
        for data, target in dataloader:
            data, target = data.to(device), target.to(device)
            
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item() * data.size(0)
            pred = output.argmax(dim=1)
            correct += pred.eq(target).sum()
            total_samples += data.size(0)
        
        # 跨进程聚合指标
        dist.all_reduce(total_loss, op=dist.ReduceOp.SUM)
        dist.all_reduce(correct, op=dist.ReduceOp.SUM)
        dist.all_reduce(total_samples, op=dist.ReduceOp.SUM)
        
        # 只在 rank 0 进程打印
        if rank == 0:
            epoch_loss = total_loss.item() / total_samples.item()
            epoch_acc = 100. * correct.item() / total_samples.item()
            print(f'Epoch {epoch + 1}: Loss={epoch_loss:.4f}, Accuracy={epoch_acc:.2f}%')
        
        scheduler.step()
    
    # ---- 模型保存（只在 rank 0 保存） ----
    if rank == 0:
        # 保存时去掉 DDP 包装
        torch.save(model.module.state_dict(), 'ddp_model.pth')
        print('模型已保存')
    
    # 清理
    dist.destroy_process_group()

# 3. 启动入口
def main():
    # 设置环境变量（由 torchrun 自动设置，这里仅示例）
    world_size = torch.cuda.device_count()
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '12355'
    
    mp.spawn(
        train,
        args=(world_size,),
        nprocs=world_size,
        join=True
    )

if __name__ == '__main__':
    main()
```

**启动命令：**

```bash
# 方式 1：使用 torchrun（推荐）
torchrun --nproc_per_node=4 train_ddp.py

# 方式 2：使用 python -m torch.distributed.launch（旧版）
python -m torch.distributed.launch --nproc_per_node=4 train_ddp.py

# 方式 3：手动指定（多机多卡）
# 在机器 0 (主节点) 上：
python train_ddp.py --rank 0 --world_size 8 \
    --master_addr 192.168.1.100 --master_port 12355

# 在机器 1 上：
python train_ddp.py --rank 4 --world_size 8 \
    --master_addr 192.168.1.100 --master_port 12355
```

**混合精度训练（AMP）加速：**

```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

for data, target in dataloader:
    optimizer.zero_grad()
    
    # 前向传播使用自动混合精度
    with autocast():
        output = model(data)
        loss = criterion(output, target)
    
    # 反向传播使用梯度缩放
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

**评分标准：**
- 对比 DP 和 DDP 的优缺点（4 分）
- 给出完整 DDP 训练代码（4 分）
- 了解混合精度训练（2 分）

---

## 模块八：开发工具 — Pytest

### 题目 8.1 Pytest 基础（基础）

**题目描述：** 请说明 Pytest 相比 unittest 的优势，演示 Pytest 中 fixture、参数化（parametrize）、断言和 conftest 的使用方法。

**考察知识点：** Pytest 基础 | **能力等级：** 初级

**参考答案：**

**Pytest vs unittest：**

| 特性 | Pytest | unittest |
|------|--------|----------|
| 断言方式 | 原生 `assert` | `self.assertEqual` 等 |
| 测试发现 | 自动发现 `test_*.py` | 需继承 TestCase |
| 参数化 | `@pytest.mark.parametrize` | 需手动实现 |
| Fixture | 灵活的函数级依赖注入 | `setUp/tearDown` |
| 插件生态 | 丰富（pytest-cov, pytest-xdist 等） | 有限 |
| 输出 | 详细的失败信息 | 较简洁 |

```python
# ---- conftest.py（共享 fixture） ----
import pytest
import tempfile
import os

@pytest.fixture(scope='session')
def temp_dir():
    """会话级别的临时目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def sample_db(temp_dir):
    """函数级别的测试数据库（依赖 temp_dir fixture）"""
    db_path = os.path.join(temp_dir, 'test.db')
    # 创建数据库
    db = create_test_db(db_path)
    yield db
    # 清理：关闭连接
    db.close()

@pytest.fixture
def sample_user():
    """提供测试用户数据"""
    return {
        'id': 1,
        'name': 'Alice',
        'email': 'alice@example.com',
        'age': 25
    }

# ---- test_user_service.py ----
import pytest
from user_service import UserService, UserNotFoundError

class TestUserService:
    """用户服务测试类"""
    
    # 使用 fixture
    def test_create_user(self, sample_db, sample_user):
        """测试创建用户"""
        service = UserService(sample_db)
        user = service.create_user(sample_user)
        
        assert user['id'] == sample_user['id']
        assert user['name'] == sample_user['name']
        assert 'created_at' in user
    
    # 参数化测试
    @pytest.mark.parametrize('name,email,expected_valid', [
        ('Alice', 'alice@example.com', True),       # 正常数据
        ('', 'alice@example.com', False),           # 空名字
        ('Alice', '', False),                       # 空邮箱
        ('Alice', 'invalid-email', False),          # 无效邮箱
        ('A' * 100, 'a@b.com', False),              # 名字过长
        ('Alice', 'a@b.com', True),                 # 边界值
    ])
    def test_validate_user(self, name, email, expected_valid):
        """参数化测试用户验证"""
        service = UserService(None)
        result = service.validate_user(name, email)
        assert result == expected_valid
    
    # 测试异常
    def test_get_user_not_found(self, sample_db):
        """测试用户不存在时抛出异常"""
        service = UserService(sample_db)
        with pytest.raises(UserNotFoundError, match='用户不存在'):
            service.get_user(999)
    
    # 测试异常详细信息
    def test_update_user_not_found(self, sample_db):
        """测试更新不存在用户时抛出异常"""
        service = UserService(sample_db)
        with pytest.raises(UserNotFoundError) as exc_info:
            service.update_user(999, {'name': 'Bob'})
        
        assert exc_info.value.user_id == 999
        assert '999' in str(exc_info.value)
    
    # 跳过测试
    @pytest.mark.skip(reason='功能尚未实现')
    def test_delete_user(self, sample_db):
        pass
    
    # 条件跳过
    @pytest.mark.skipif(not has_redis(), reason='需要 Redis')
    def test_cache_user(self, sample_db):
        pass
    
    # 标记为预期失败
    @pytest.mark.xfail(reason='已知 Bug，下个版本修复')
    def test_edge_case(self):
        assert 1 + 1 == 3

# ---- 运行测试 ----
# $ pytest test_user_service.py -v          # 详细输出
# $ pytest test_user_service.py -k "create"  # 只运行包含 "create" 的测试
# $ pytest test_user_service.py --cov=src    # 带覆盖率
# $ pytest -n auto                           # 并行运行所有测试
```

**Fixture 作用域（scope）：**

| scope | 生命周期 | 说明 |
|-------|---------|------|
| `function`（默认） | 每个测试函数 | 最常用，隔离性好 |
| `class` | 每个测试类 | 类内共享 |
| `module` | 每个测试模块 | 模块内共享 |
| `package` | 每个测试包 | 包内共享 |
| `session` | 整个测试会话 | 全局共享 |

**评分标准：**
- 对比 Pytest 和 unittest 的优势（3 分）
- 正确使用 fixture 和参数化（4 分）
- 展示异常测试和跳过标记（3 分）

---

### 题目 8.2 Pytest 高级特性（进阶）

**题目描述：** 请演示 Pytest 的 Mock 和 Monkeypatch 的使用，说明如何对数据库、网络请求等外部依赖进行测试。实现一个完整的测试场景：对调用外部 API 的服务进行单元测试。

**考察知识点：** Mock、Monkeypatch | **能力等级：** 中级

**参考答案：**

```python
# ---- weather_service.py（被测代码） ----
import requests
from datetime import datetime

class WeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://api.weather.com/v1'
    
    def get_current_weather(self, city: str) -> dict:
        """获取当前天气（调用外部 API）"""
        url = f'{self.base_url}/current'
        response = requests.get(
            url,
            params={'city': city, 'api_key': self.api_key},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def get_forecast(self, city: str, days: int = 3) -> list:
        """获取天气预报"""
        url = f'{self.base_url}/forecast'
        response = requests.get(
            url,
            params={'city': city, 'days': days, 'api_key': self.api_key},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return data['forecast']
    
    def is_raining(self, city: str) -> bool:
        """判断是否下雨"""
        weather = self.get_current_weather(city)
        return weather.get('condition') == 'rain'

# ---- test_weather_service.py（测试代码） ----
import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from weather_service import WeatherService

class TestWeatherService:
    """天气服务测试"""
    
    @pytest.fixture
    def weather_service(self):
        return WeatherService(api_key='test_key')
    
    @pytest.fixture
    def mock_weather_response(self):
        return {
            'city': 'Beijing',
            'temperature': 25,
            'humidity': 60,
            'condition': 'sunny',
            'updated_at': '2024-01-01T12:00:00Z'
        }
    
    # ---- 方法 1：使用 unittest.mock.patch ----
    @patch('weather_service.requests.get')
    def test_get_current_weather_mock(self, mock_get, weather_service, mock_weather_response):
        """使用 patch 装饰器 Mock 外部 API 调用"""
        # 配置 Mock 对象
        mock_response = Mock()
        mock_response.json.return_value = mock_weather_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = weather_service.get_current_weather('Beijing')
        
        assert result['city'] == 'Beijing'
        assert result['temperature'] == 25
        assert result['condition'] == 'sunny'
        
        # 验证 API 调用参数
        mock_get.assert_called_once()
        call_args = mock_get.call_args[1]['params']
        assert call_args['city'] == 'Beijing'
        assert call_args['api_key'] == 'test_key'
    
    # ---- 方法 2：使用 patch 上下文管理器 ----
    def test_get_forecast_context_manager(self, weather_service):
        """使用 with patch 上下文管理器"""
        mock_forecast = [
            {'date': '2024-01-02', 'high': 28, 'low': 18, 'condition': 'cloudy'},
            {'date': '2024-01-03', 'high': 26, 'low': 17, 'condition': 'sunny'},
            {'date': '2024-01-04', 'high': 24, 'low': 16, 'condition': 'rain'},
        ]
        
        with patch('weather_service.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {'forecast': mock_forecast}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            result = weather_service.get_forecast('Shanghai', days=3)
            
            assert len(result) == 3
            assert result[0]['condition'] == 'cloudy'
            assert result[2]['condition'] == 'rain'
    
    # ---- 方法 3：使用 monkeypatch（pytest 内置） ----
    def test_is_raining_monkeypatch(self, weather_service, monkeypatch):
        """使用 monkeypatch 替换方法"""
        # 替换 get_current_weather 方法
        def mock_get_weather(city):
            return {'city': city, 'condition': 'rain'}
        
        monkeypatch.setattr(
            weather_service, 'get_current_weather', mock_get_weather
        )
        
        assert weather_service.is_raining('Beijing') == True
        
        # 修改 mock 返回晴天
        monkeypatch.setattr(
            weather_service, 'get_current_weather',
            lambda city: {'city': city, 'condition': 'sunny'}
        )
        assert weather_service.is_raining('Beijing') == False
    
    # ---- 方法 4：使用 MagicMock（自动模拟） ----
    def test_with_magic_mock(self, weather_service):
        """MagicMock 自动处理未定义的方法调用"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'city': 'Shenzhen',
            'temperature': 30,
            'condition': 'sunny'
        }
        
        with patch('weather_service.requests.get', return_value=mock_response):
            result = weather_service.get_current_weather('Shenzhen')
            assert result['temperature'] == 30
    
    # ---- 测试异常场景 ----
    def test_api_timeout(self, weather_service):
        """测试 API 超时"""
        with patch('weather_service.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout('请求超时')
            
            with pytest.raises(requests.exceptions.Timeout, match='请求超时'):
                weather_service.get_current_weather('Beijing')
    
    def test_api_error_response(self, weather_service):
        """测试 API 返回错误"""
        with patch('weather_service.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = \
                requests.exceptions.HTTPError('500 Server Error')
            mock_get.return_value = mock_response
            
            with pytest.raises(requests.exceptions.HTTPError):
                weather_service.get_current_weather('Beijing')
    
    # ---- 测试多次调用 ----
    def test_multiple_calls(self, weather_service):
        """测试多次调用 API 返回不同结果"""
        with patch('weather_service.requests.get') as mock_get:
            mock_response = Mock()
            # side_effect 为列表时，每次调用依次返回
            mock_response.json.side_effect = [
                {'city': 'Beijing', 'temperature': 25},
                {'city': 'Shanghai', 'temperature': 28},
                {'city': 'Shenzhen', 'temperature': 30},
            ]
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            assert weather_service.get_current_weather('Beijing')['temperature'] == 25
            assert weather_service.get_current_weather('Shanghai')['temperature'] == 28
            assert weather_service.get_current_weather('Shenzhen')['temperature'] == 30
```

**Mock vs Monkeypatch：**

| 特性 | Mock (unittest.mock) | Monkeypatch (pytest) |
|------|---------------------|---------------------|
| 来源 | 标准库 | pytest 内置 |
| 功能 | 功能更丰富 | 简洁轻量 |
| 使用方式 | `patch` 装饰器/上下文 | `monkeypatch.setattr` |
| 适用场景 | 复杂 Mock 场景 | 简单替换场景 |

**评分标准：**
- 演示 patch 装饰器和上下文管理器（3 分）
- 使用 monkeypatch 进行替换（2 分）
- 测试异常和多次调用场景（3 分）
- 完整的外部服务测试覆盖（2 分）

---

## 模块九：开发工具 — Poetry

### 题目 9.1 Poetry 依赖管理（基础）

**题目描述：** 请说明 Poetry 相比 pip + requirements.txt 的优势，演示如何使用 Poetry 创建项目、添加依赖、管理虚拟环境，并解释 pyproject.toml 的结构。

**考察知识点：** Poetry 基础 | **能力等级：** 初级

**参考答案：**

**Poetry vs pip + requirements.txt：**

| 特性 | pip + requirements.txt | Poetry |
|------|----------------------|--------|
| 依赖解析 | 无（需手动 resolve） | 自动 SAT 求解器 |
| 依赖锁定 | 手动 `pip freeze > requirements.txt` | 自动生成 `poetry.lock` |
| 虚拟环境 | 需手动创建（venv/virtualenv） | 自动管理 |
| 发布打包 | 手动 `setup.py` | 一条命令 |
| 开发依赖 | 需要多个 requirements 文件 | `[tool.poetry.group.dev]` |
| 版本约束 | 自定格式 | `^` `~` 语义化版本 |

**Poetry 使用流程：**

```bash
# 1. 安装 Poetry
# Windows (PowerShell):
# (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# 2. 创建新项目
poetry new my-project
cd my-project

# 或在现有项目中初始化
poetry init

# 3. 添加依赖
poetry add flask fastapi
poetry add numpy pandas

# 4. 添加开发依赖
poetry add --group dev pytest pytest-cov black mypy
poetry add --group dev pre-commit

# 5. 安装所有依赖
poetry install

# 6. 激活虚拟环境
poetry shell

# 7. 运行命令
poetry run python main.py
poetry run pytest
poetry run black .

# 8. 更新依赖
poetry update            # 更新所有依赖
poetry update flask      # 更新指定包

# 9. 查看依赖树
poetry show --tree

# 10. 构建发布
poetry build             # 构建 wheel 和 tar.gz
poetry publish           # 发布到 PyPI
```

**pyproject.toml 详解：**

```toml
[tool.poetry]
name = "my-project"
version = "0.1.0"
description = "A sample Python project"
authors = ["Your Name <email@example.com>"]
readme = "README.md"
license = "MIT"
repository = "https://github.com/user/my-project"
keywords = ["sample", "demo"]

[tool.poetry.dependencies]
python = "^3.10"          # >=3.10, <4.0
flask = "^3.0.0"           # >=3.0.0, <4.0.0
fastapi = "~0.109.0"       # >=0.109.0, <0.110.0
sqlalchemy = ">=2.0,<3.0"  # 手动指定范围
numpy = "*"                # 任意版本（不推荐）

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
pytest-cov = "^5.0.0"
black = "^24.0.0"
mypy = "^1.8.0"
ruff = "^0.2.0"

[tool.poetry.group.test.dependencies]
# 额外的测试依赖组
factory-boy = "^3.3.0"

[tool.poetry.scripts]
# CLI 入口点
my-cli = "my_project.cli:main"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 100
target-version = ['py310']

[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --cov=src --cov-report=term-missing"
testpaths = ["tests"]
```

**版本约束符号：**

| 符号 | 示例 | 含义 |
|------|------|------|
| `^` | `^1.2.3` | >=1.2.3, <2.0.0（兼容版本） |
| `~` | `~1.2.3` | >=1.2.3, <1.3.0（近似版本） |
| `>=` | `>=1.2.3` | 大于等于 1.2.3 |
| `*` | `*` | 任意版本（不推荐） |
| 精确 | `1.2.3` | 精确版本 1.2.3 |

**评分标准：**
- 对比 Poetry 与 pip 方式的优势（3 分）
- 演示完整项目创建和依赖管理流程（4 分）
- 解释 pyproject.toml 结构和版本约束（3 分）

---

## 模块十：开发工具 — Docker

### 题目 10.1 Docker 基础与 Python 应用容器化（基础）

**题目描述：** 请说明 Docker 的核心概念（镜像、容器、Dockerfile、Docker Compose），并编写一个 Dockerfile 将 FastAPI 应用容器化，要求使用多阶段构建优化镜像大小。

**考察知识点：** Docker 基础、容器化 | **能力等级：** 初级

**参考答案：**

**核心概念：**

| 概念 | 说明 | 类比 |
|------|------|------|
| **镜像（Image）** | 只读模板，包含运行环境和依赖 | 类（Class） |
| **容器（Container）** | 镜像的运行实例 | 对象（Object） |
| **Dockerfile** | 构建镜像的指令文件 | 构建脚本 |
| **Docker Compose** | 多容器编排工具 | 编排文件 |
| **Registry** | 镜像仓库（Docker Hub 等） | GitHub |

**FastAPI 应用示例：**

```python
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello from Docker"}

@app.get("/health")
def health():
    return {"status": "healthy"}
```

**Dockerfile（多阶段构建）：**

```dockerfile
# ---- 阶段 1：构建阶段 ----
FROM python:3.11-slim AS builder

# 设置工作目录
WORKDIR /app

# 安装 Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# 复制依赖文件
COPY pyproject.toml poetry.lock ./

# 导出依赖到 requirements.txt
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# ---- 阶段 2：运行阶段 ----
FROM python:3.11-slim AS runner

# 创建非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# 安装依赖
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 切换到非 root 用户
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**.dockerignore：**

```
__pycache__
*.pyc
*.pyo
*.egg-info
.env
.git
.gitignore
.venv
venv
.pytest_cache
*.md
docker-compose.yml
Dockerfile
```

**Docker Compose 编排：**

```yaml
# docker-compose.yml
version: '3.8'

services:
  # FastAPI 应用
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/mydb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./app:/app   # 开发模式：挂载代码目录
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - app-network

  # PostgreSQL 数据库
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: mydb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  # Redis 缓存
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  # Celery Worker（如需要异步任务）
  worker:
    build: .
    command: celery -A app.tasks worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/mydb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

**常用命令：**

```bash
# 构建镜像
docker build -t my-fastapi-app .

# 运行容器
docker run -d -p 8000:8000 --name myapp my-fastapi-app

# 查看日志
docker logs -f myapp

# 进入容器
docker exec -it myapp bash

# Docker Compose 操作
docker compose up -d          # 启动所有服务
docker compose logs -f app    # 查看应用日志
docker compose exec app bash  # 进入应用容器
docker compose down           # 停止并删除所有容器
docker compose restart app    # 重启应用容器
```

**评分标准：**
- 解释 Docker 核心概念（3 分）
- 编写多阶段构建 Dockerfile（4 分）
- 编写 Docker Compose 编排文件（3 分）

---

### 题目 10.2 Docker 最佳实践与优化（进阶）

**题目描述：** 请说明 Docker 镜像优化的最佳实践，包括镜像大小优化、层缓存利用、安全最佳实践和生产环境部署注意事项。

**考察知识点：** Docker 优化、安全实践 | **能力等级：** 中级

**参考答案：**

**生产级 Dockerfile 最佳实践：**

```dockerfile
# ===== 生产级 Python Dockerfile =====

# 1. 使用特定版本标签，避免 latest
# 2. 优先使用 slim/alpine 镜像
FROM python:3.11.8-slim-bookworm AS builder

# 3. 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# 4. 先安装系统依赖，利用缓存
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 5. 先复制依赖文件（不复制代码，利用层缓存）
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# ===== 运行阶段 =====
FROM python:3.11.8-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# 6. 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 7. 创建非 root 用户
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --create-home appuser

# 8. 从 builder 复制依赖
COPY --from=builder /root/.local /home/appuser/.local

# 9. 复制应用代码（放最后，利用缓存）
COPY --chown=appuser:appuser . .

# 10. 切换用户
USER appuser

EXPOSE 8000

# 11. 使用 exec 形式的 CMD（避免 shell 子进程）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**镜像优化技巧总结：**

| 技巧 | 说明 | 效果 |
|------|------|------|
| 多阶段构建 | 分离构建和运行环境 | 减小 50-70% |
| `--no-install-recommends` | 不安装推荐包 | 减小 100-200MB |
| 清理 apt 缓存 | `rm -rf /var/lib/apt/lists/*` | 减小 50-100MB |
| 使用 slim/alpine 基础镜像 | 精简系统包 | 减小 500MB+ |
| 合并 RUN 指令 | 减少镜像层数 | 减小每层开销 |
| 正确排序 COPY | 先放不常变的文件 | 加速构建 |
| `.dockerignore` | 排除不需要的文件 | 减小上下文 |

**安全最佳实践：**

```dockerfile
# 安全加固 Dockerfile
FROM python:3.11-slim

# 1. 非 root 用户运行
RUN useradd -m -s /bin/bash appuser
USER appuser

# 2. 不要暴露敏感信息
# ❌ 错误：ENV DATABASE_PASSWORD=secret123
# ✅ 正确：运行时通过 secrets 或环境变量注入

# 3. 使用固定版本，避免 latest 标签
FROM python:3.11.8-slim  # ✅ 精确版本
# FROM python:latest      # ❌ 不确定

# 4. 扫描镜像漏洞
# docker scan my-image
# trivy image my-image
```

**docker-compose 生产配置：**

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    restart: always  # 崩溃自动重启
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 256M
    logging:
      driver: json-file
      options:
        max-size: '10m'
        max-file: '3'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    environment:
      - DATABASE_URL=${DATABASE_URL}  # 从 .env 文件读取
    secrets:
      - db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

**评分标准：**
- 列举至少 5 个镜像优化技巧（5 分）
- 说明安全最佳实践（3 分）
- 展示生产级配置（2 分）

---

### 题目 10.3 Docker 网络与编排（高级）

**题目描述：** 请说明 Docker 网络模式（bridge、host、overlay）的区别，并设计一个微服务架构的 Docker Compose 编排方案，包含 API 网关、多个后端服务、消息队列和监控组件。

**考察知识点：** Docker 网络、微服务编排 | **能力等级：** 高级

**参考答案：**

**Docker 网络模式：**

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| **bridge**（默认） | 容器通过虚拟网桥通信，NAT 访问外网 | 单机开发，容器间通信 |
| **host** | 容器直接使用宿主机网络栈 | 高性能场景，端口冲突需注意 |
| **overlay** | 跨主机的容器网络 | Swarm 集群，多机部署 |
| **none** | 无网络 | 安全性要求极高的场景 |
| **macvlan** | 容器具有独立 MAC 地址 | 容器需像物理设备一样接入网络 |

**微服务编排方案：**

```yaml
# docker-compose.microservices.yml
version: '3.8'

# ===== 网络定义 =====
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # 内部网络，不暴露给外部
  monitoring:
    driver: bridge

# ===== 卷定义 =====
volumes:
  postgres_data:
  redis_data:
  rabbitmq_data:
  prometheus_data:
  grafana_data:
  elasticsearch_data:

# ===== 密钥定义 =====
secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    file: ./secrets/api_key.txt

services:
  # ===== API 网关（Nginx） =====
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
    networks:
      - frontend
    depends_on:
      - user-service
      - order-service
      - product-service
    restart: always
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M

  # ===== 用户服务 =====
  user-service:
    build:
      context: ./services/user
      dockerfile: Dockerfile
    expose:
      - "8000"
    environment:
      - DATABASE_URL=postgresql://user:password@user-db:5432/users
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
    networks:
      - frontend
      - backend
    depends_on:
      user-db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ===== 订单服务 =====
  order-service:
    build:
      context: ./services/order
      dockerfile: Dockerfile
    expose:
      - "8000"
    environment:
      - DATABASE_URL=postgresql://user:password@order-db:5432/orders
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
      - USER_SERVICE_URL=http://user-service:8000
    networks:
      - frontend
      - backend
    depends_on:
      order-db:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    restart: always

  # ===== 商品服务 =====
  product-service:
    build:
      context: ./services/product
      dockerfile: Dockerfile
    expose:
      - "8000"
    environment:
      - DATABASE_URL=postgresql://user:password@product-db:5432/products
      - REDIS_URL=redis://redis:6379/1
    networks:
      - frontend
      - backend
    depends_on:
      product-db:
        condition: service_healthy
    restart: always

  # ===== 数据库集群 =====
  user-db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: users
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d users"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: always

  order-db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: orders
    volumes:
      - ./data/order-db:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d orders"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: always

  product-db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: products
    networks:
      - backend
    restart: always

  # ===== 缓存 =====
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - backend
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: always

  # ===== 消息队列 =====
  rabbitmq:
    image: rabbitmq:3.13-management-alpine
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    ports:
      - "15672:15672"  # 管理界面
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    networks:
      - backend
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "check_port_connectivity"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: always

  # ===== 异步任务 Worker =====
  celery-worker:
    build:
      context: ./services/order
      dockerfile: Dockerfile
    command: celery -A tasks worker --loglevel=info --concurrency=4
    environment:
      - DATABASE_URL=postgresql://user:password@order-db:5432/orders
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
    networks:
      - backend
    depends_on:
      - rabbitmq
      - order-db
    restart: always
    deploy:
      replicas: 2  # 多副本

  # ===== 监控：Prometheus =====
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - monitoring
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: always

  # ===== 监控：Grafana =====
  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    ports:
      - "3000:3000"
    networks:
      - monitoring
    depends_on:
      - prometheus
    restart: always

  # ===== 日志收集：ELK Stack（简化版） =====
  elasticsearch:
    image: elasticsearch:8.12.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
    networks:
      - monitoring
    restart: always

  logstash:
    image: logstash:8.12.0
    volumes:
      - ./logstash/logstash.conf:/usr/share/logstash/pipeline/logstash.conf:ro
    networks:
      - monitoring
    depends_on:
      - elasticsearch
    restart: always

  kibana:
    image: kibana:8.12.0
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    networks:
      - monitoring
    depends_on:
      - elasticsearch
    restart: always
```

**架构设计要点说明：**

| 组件 | 作用 | 网络 |
|------|------|------|
| **Nginx** | API 网关，反向代理，负载均衡 | frontend |
| **user-service / order-service / product-service** | 微服务核心业务 | frontend + backend |
| **PostgreSQL** | 各服务独立数据库 | backend（internal） |
| **Redis** | 分布式缓存、会话管理 | backend（internal） |
| **RabbitMQ** | 消息队列，异步解耦 | backend（internal） |
| **Celery Worker** | 异步任务处理 | backend（internal） |
| **Prometheus + Grafana** | 监控告警 | monitoring |
| **ELK Stack** | 日志收集分析 | monitoring |

**网络隔离策略：**
- `frontend` 网络：Nginx 和后端服务通信
- `backend` 网络（internal）：服务间内部通信，不暴露给外部
- `monitoring` 网络：监控组件独立网络

**评分标准：**
- 正确解释 Docker 网络模式（4 分）
- 设计合理的微服务编排方案（4 分）
- 展示网络隔离和安全策略（2 分）

---

## 附录：考点分布总览

| 模块 | 框架/工具 | 题目数 | 难度分布 |
|------|---------|--------|---------|
| Web 框架 | Django | 4 | 基础×1 / 进阶×2 / 高级×1 |
| Web 框架 | Flask | 3 | 基础×1 / 进阶×2 |
| Web 框架 | FastAPI | 3 | 基础×1 / 进阶×1 / 高级×1 |
| 数据处理 | NumPy | 2 | 基础×1 / 进阶×1 |
| 数据处理 | Pandas | 3 | 基础×1 / 进阶×1 / 高级×1 |
| 机器学习 | TensorFlow | 2 | 基础×1 / 进阶×1 |
| 机器学习 | PyTorch | 3 | 基础×1 / 进阶×1 / 高级×1 |
| 开发工具 | Pytest | 2 | 基础×1 / 进阶×1 |
| 开发工具 | Poetry | 1 | 基础×1 |
| 开发工具 | Docker | 3 | 基础×1 / 进阶×1 / 高级×1 |
| **合计** | **10 个方向** | **26 题** | 初级 10 / 中级 11 / 高级 5 |

---

## 使用建议

**面试官使用：**
- 初级岗位：重点考察基础题，关注代码基本功和概念理解
- 中级岗位：增加进阶题，考察实际项目经验和问题解决能力
- 高级岗位：涵盖高级题，关注架构设计、性能优化和系统思维

**求职者使用：**
- 按模块系统学习，先掌握基础题再挑战进阶题
- 每个代码示例建议手写一遍，加深理解
- 评分标准可作为自测参考，10 分制中 6 分及格、8 分良好、9 分以上优秀