# Python Agent 服务部署完整指南

> **文档定位**:本文档系统阐述 Python Agent 服务从开发环境到生产环境的**完整部署流程**,涵盖环境配置、依赖管理、服务启动、配置文件、进程管理、反向代理、日志监控、验证步骤与生产级稳定性保障,为 Java/Pascal 背景开发者提供一份可直接落地的 Python Agent 部署手册。
>
> **阅读建议**:本文是 `12Java-Python Agent 开发` 系列的部署实践篇,建议结合 [151为什么Agent开发选择Python语言.md](./151为什么Agent开发选择Python语言.md) 一并阅读,理解"为何选 Python"后再读"如何部署 Python Agent"。
>
> **适用场景**:基于 LangChain / LangGraph / CrewAI / AutoGen / FastAPI 等框架构建的 Agent 服务,部署到 Linux(Ubuntu/CentOS)生产环境。

---

## 目录

- [一、部署概述与架构总览](#一部署概述与架构总览)
- [二、环境配置要求](#二环境配置要求)
- [三、项目结构设计](#三项目结构设计)
- [四、依赖管理与方法](#四依赖管理与方法)
- [五、配置文件设置](#五配置文件设置)
- [六、服务启动命令](#六服务启动命令)
- [七、进程管理方式](#七进程管理方式)
- [八、反向代理与负载均衡](#八反向代理与负载均衡)
- [九、日志与监控](#九日志与监控)
- [十、部署后验证步骤](#十部署后验证步骤)
- [十一、容器化部署方案](#十一容器化部署方案)
- [十二、生产环境稳定性保障](#十二生产环境稳定性保障)
- [十三、常见问题与最佳实践](#十三常见问题与最佳实践)
- [十四、完整部署脚本与总结](#十四完整部署脚本与总结)

---

## 一、部署概述与架构总览

### 1.1 部署的核心目标

Python Agent 服务的部署不只是"把代码放到服务器上跑起来",而是要达成**四大生产级目标**:

```mermaid
mindmap
  root((部署目标))
    可用性
      服务持续在线
      故障自动恢复
      健康检查机制
    性能
      高并发响应
      低延迟
      资源高效利用
    可维护
      日志可追溯
      配置可热更新
      版本可回滚
    安全性
      依赖隔离
      权限最小化
      通信加密
```

### 1.2 生产部署架构总览

一个典型的 Python Agent 生产环境部署架构如下:

```mermaid
graph TB
    subgraph 客户端
        C1[Web 前端]
        C2[移动端]
        C3[第三方调用方]
    end

    subgraph 接入层
        LB[负载均衡<br/>Nginx/HAProxy]
        FW[防火墙/WAF]
    end

    subgraph 应用层
        P1[Python Agent 进程 1<br/>Gunicorn + Uvicorn Worker]
        P2[Python Agent 进程 2<br/>Gunicorn + Uvicorn Worker]
        P3[Python Agent 进程 3<br/>Gunicorn + Uvicorn Worker]
        P4[Python Agent 进程 4<br/>Gunicorn + Uvicorn Worker]
    end

    subgraph 进程管理
        SUP[Supervisor / Systemd]
    end

    subgraph 数据层
        DB[(PostgreSQL<br/>会话/消息)]
        REDIS[(Redis<br/>缓存/队列)]
        VDB[(向量数据库<br/>Milvus/Qdrant)]
    end

    subgraph LLM 服务
        LLM[OpenAI API / 本地模型<br/>vLLM/Ollama]
    end

    subgraph 可观测
        LOG[日志中心<br/>ELK/Loki]
        MON[监控告警<br/>Prometheus+Grafana]
    end

    C1 & C2 & C3 --> FW
    FW --> LB
    LB --> P1 & P2 & P3 & P4
    SUP -.管理.-> P1 & P2 & P3 & P4
    P1 & P2 & P3 & P4 --> DB & REDIS & VDB
    P1 & P2 & P3 & P4 --> LLM
    P1 & P2 & P3 & P4 -.日志.-> LOG
    P1 & P2 & P3 & P4 -.指标.-> MON

    style LB fill:#fff3cd,stroke:#d39e00,stroke-width:2px
    style SUP fill:#d1ecf1,stroke:#0c5460,stroke-width:2px
    style P1 fill:#d4edda,stroke:#155724
```

### 1.3 部署流程全景

```mermaid
flowchart LR
    A[1. 环境准备] --> B[2. 代码部署]
    B --> C[3. 依赖安装]
    C --> D[4. 配置设置]
    D --> E[5. 进程管理配置]
    E --> F[6. 反向代理配置]
    F --> G[7. 日志监控接入]
    G --> H[8. 验证测试]
    H --> I[9. 上线发布]
    I --> J[10. 持续运维]

    style A fill:#d4edda,stroke:#155724
    style H fill:#fff3cd,stroke:#d39e00,stroke-width:2px
    style J fill:#d1ecf1,stroke:#0c5460
```

### 1.4 与 Java 部署的核心区别

| 维度 | Java 部署 | Python Agent 部署 | 关键差异 |
|------|----------|------------------|---------|
| **运行时** | JVM(一次编译到处运行) | Python 解释器(需匹配版本) | Python 对版本敏感,3.10 ≠ 3.11 |
| **打包方式** | Jar/War | 源码 + requirements.txt / wheel | Python 通常源码部署 |
| **依赖隔离** | Maven/Gradle 依赖树 | venv / conda 虚拟环境 | Python 必须用虚拟环境隔离 |
| **应用服务器** | Tomcat/Undertow | Gunicorn + Uvicorn / uvicorn | Python ASGI 服务器 |
| **进程管理** | systemd / Java 服务化 | Supervisor / systemd | 类似,但 Python 需指定解释器路径 |
| **启动速度** | 慢(JVM 预热) | 快(解释执行) | Python 冷启动快 |
| **内存占用** | 较高且稳定(JVM 堆) | 较低但波动(GC 不可控) | Python 需限制 worker 数 |
| **典型框架** | Spring Boot | FastAPI / LangChain | Python 以 ASGI 框架为主 |

> **关键认知**:Java 开发者转 Python 部署,最大的思维转变是——**Python 没有内置的应用服务器**,需要 Gunicorn(进程管理器)+ Uvicorn(ASGI 服务器)的组合来替代 Tomcat 的角色。

---

## 二、环境配置要求

### 2.1 操作系统要求

```mermaid
graph LR
    subgraph 推荐生产环境
        OS1[Ubuntu 22.04 LTS]
        OS2[CentOS 8 / RHEL 9]
        OS3[Debian 12]
    end
    subgraph 容器环境
        DK[Docker 24+]
        K8S[Kubernetes 1.28+]
    end
    subgraph 开发环境
        WIN[Windows 10/11 + WSL2]
        MAC[macOS 13+]
    end

    style OS1 fill:#d4edda,stroke:#155724,stroke-width:2px
    style DK fill:#d1ecf1,stroke:#0c5460,stroke-width:2px
```

| 项目 | 最低要求 | 推荐配置 | 说明 |
|------|---------|---------|------|
| **操作系统** | Ubuntu 20.04 LTS | Ubuntu 22.04 LTS x86_64 | LTS 版本保障 5 年支持 |
| **内核版本** | 5.4+ | 5.15+ | 新内核性能更优 |
| **CPU** | 2 核 | 4 核+ | Agent 主要是 IO 密集,LLM 调用不占 CPU |
| **内存** | 4 GB | 8 GB+ | 每个 Uvicorn worker 约 200-500MB |
| **磁盘** | 20 GB | 50 GB+ SSD | 日志 + 依赖 + 向量索引 |
| **网络** | 100 Mbps | 1 Gbps | LLM API 调用需稳定外网 |

### 2.2 Python 版本选择

```mermaid
graph TB
    subgraph Python 版本选型决策
        START[开始选型] --> Q1{是否需要<br/>最新 ML 库?}
        Q1 -- 是 --> Q2{是否使用<br/>PyTorch 2.x?}
        Q2 -- 是 --> R1[Python 3.11<br/>最佳兼容性]
        Q2 -- 否 --> R2[Python 3.12<br/>性能提升 5%]
        Q1 -- 否 --> Q3{是否需要<br/>长期稳定?}
        Q3 -- 是 --> R3[Python 3.10<br/>支持到 2026-10]
        Q3 -- 否 --> R4[Python 3.12<br/>最新稳定版]
    end

    style R1 fill:#d4edda,stroke:#155724
    style R3 fill:#fff3cd,stroke:#d39e00
```

| Python 版本 | 性能 | 主流库兼容性 | 支持截止 | 推荐场景 |
|------------|:----:|:----------:|---------|---------|
| 3.9 | 基准 | ✅ 全部兼容 | 2025-10 | 遗留系统维护 |
| 3.10 | +10% | ✅ 全部兼容 | 2026-10 | **生产稳定首选** |
| 3.11 | +25% | ✅ 大部分兼容 | 2027-10 | 性能敏感场景 |
| 3.12 | +30% | ⚠️ 部分 ML 库滞后 | 2028-10 | 新项目尝鲜 |

> **推荐**:Agent 服务选 **Python 3.10 或 3.11**——3.10 兼容性最佳,3.11 性能提升显著且生态已成熟。**避免 3.12** 用于含 PyTorch/TensorFlow 的场景。

### 2.3 系统依赖安装

#### Ubuntu / Debian 系

```bash
# 1. 更新系统包索引
sudo apt update && sudo apt upgrade -y

# 2. 安装 Python 编译与运行依赖
sudo apt install -y \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    wget \
    curl \
    unzip \
    git \
    pkg-config

# 3. 安装 Python 3.11(以 Ubuntu 22.04 为例,使用 deadsnakes PPA)
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils

# 4. 验证
python3.11 --version
# 输出: Python 3.11.x
```

#### CentOS / RHEL 系

```bash
# 1. 安装编译依赖
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y \
    openssl-devel \
    bzip2-devel \
    libffi-devel \
    wget \
    git \
    zlib-devel \
    readline-devel \
    sqlite-devel

# 2. 安装 Python 3.11(需源码编译)
cd /tmp
wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz
tar xzf Python-3.11.9.tgz
cd Python-3.11.9
./configure --enable-optimizations --prefix=/usr/local
make -j $(nproc)
sudo make altinstall

# 3. 验证
python3.11 --version
```

### 2.4 创建专用部署用户

**生产环境严禁用 root 运行 Python 服务**,应创建专用低权限用户:

```bash
# 1. 创建专用用户与组
sudo groupadd -r agent
sudo useradd -r -g agent -d /opt/agent -s /bin/bash -m agent

# 2. 创建标准目录结构
sudo mkdir -p /opt/agent/{app,venv,logs,config,data}
sudo chown -R agent:agent /opt/agent

# 3. 切换到 agent 用户测试
sudo su - agent
whoami  # 输出: agent
pwd     # 输出: /opt/agent
```

```mermaid
flowchart TB
    subgraph 目录结构
        ROOT[/opt/agent/] --> APP[app/<br/>应用代码]
        ROOT --> VENV[venv/<br/>虚拟环境]
        ROOT --> LOGS[logs/<br/>运行日志]
        ROOT --> CONFIG[config/<br/>配置文件]
        ROOT --> DATA[data/<br/>运行数据]
    end

    style ROOT fill:#fff3cd,stroke:#d39e00,stroke-width:2px
    style APP fill:#d4edda,stroke:#155724
    style VENV fill:#d1ecf1,stroke:#0c5460
```

---

## 三、项目结构设计

### 3.1 推荐项目结构

一个可维护、可部署的 Python Agent 项目应遵循以下结构:

```
agent-service/                         # 项目根目录
├── app/                                # 应用主目录
│   ├── __init__.py
│   ├── main.py                         # FastAPI 应用入口
│   ├── api/                            # API 路由层
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py                 # 对话接口
│   │   │   ├── session.py              # 会话管理
│   │   │   └── health.py               # 健康检查
│   │   └── deps.py                     # 依赖注入
│   ├── core/                           # 核心业务
│   │   ├── __init__.py
│   │   ├── agent.py                    # Agent 核心
│   │   ├── llm.py                      # LLM 客户端
│   │   ├── memory.py                   # 记忆管理
│   │   └── tools.py                    # 工具集
│   ├── models/                         # 数据模型
│   │   ├── __init__.py
│   │   ├── session.py
│   │   └── message.py
│   ├── services/                       # 业务服务
│   │   ├── __init__.py
│   │   ├── chat_service.py
│   │   └── session_service.py
│   └── utils/                          # 工具函数
│       ├── __init__.py
│       ├── logger.py
│       └── config.py
├── config/                             # 配置文件目录
│   ├── settings.yaml                   # 主配置
│   ├── settings.prod.yaml              # 生产配置
│   ├── settings.dev.yaml               # 开发配置
│   └── logging.yaml                    # 日志配置
├── tests/                              # 测试目录
│   ├── __init__.py
│   ├── test_api/
│   └── test_core/
├── scripts/                            # 运维脚本
│   ├── start.sh                        # 启动脚本
│   ├── stop.sh                         # 停止脚本
│   └── deploy.sh                       # 部署脚本
├── .env.example                        # 环境变量模板
├── .gitignore
├── requirements.txt                    # 依赖清单(基础)
├── requirements-prod.txt               # 依赖清单(生产)
├── pyproject.toml                      # 项目元数据(可选)
├── Dockerfile                          # 容器构建文件
├── docker-compose.yml                  # 编排文件
├── README.md
└── Makefile                            # 常用命令快捷方式
```

### 3.2 关键文件说明

#### `app/main.py` —— 应用入口

```python
"""
Python Agent 服务入口
基于 FastAPI 框架,通过 Gunicorn + Uvicorn 启动
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import chat, session, health
from app.core.agent import AgentManager
from app.utils.config import load_config
from app.utils.logger import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理:启动时初始化资源,关闭时释放"""
    # === 启动阶段 ===
    logger.info("Agent 服务启动中...")
    config = load_config()
    app.state.agent = AgentManager(config)
    await app.state.agent.initialize()
    logger.info("Agent 初始化完成")
    
    yield  # 服务运行期间
    
    # === 关闭阶段 ===
    logger.info("Agent 服务关闭中...")
    await app.state.agent.shutdown()
    logger.info("Agent 资源已释放")


def create_app() -> FastAPI:
    """应用工厂"""
    setup_logging()
    
    app = FastAPI(
        title="Python Agent Service",
        description="AI Agent 服务 API",
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境改为具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 全局异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(f"未处理异常: {exc}, 路径: {request.url.path}")
        return JSONResponse(
            status_code=500,
            content={"error": "internal_error", "message": str(exc)},
        )
    
    # 路由注册
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
    app.include_router(session.router, prefix="/api/v1/sessions", tags=["session"])
    
    return app


app = create_app()
```

#### `app/api/routes/health.py` —— 健康检查

```python
"""健康检查接口 —— 进程管理器与负载均衡依赖此接口判断服务状态"""
from fastapi import APIRouter, Depends
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """轻量级存活检查(LB 用)"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@router.get("/health/ready")
async def readiness_check():
    """就绪检查 —— 验证依赖服务连通性"""
    checks = {
        "database": await _check_database(),
        "redis": await _check_redis(),
        "llm": await _check_llm(),
    }
    all_ok = all(checks.values())
    return {
        "status": "ready" if all_ok else "not_ready",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
    }


async def _check_database() -> bool:
    try:
        # 实际:执行 SELECT 1
        return True
    except Exception:
        return False


async def _check_redis() -> bool:
    try:
        # 实际:执行 PING
        return True
    except Exception:
        return False


async def _check_llm() -> bool:
    try:
        # 实际:轻量 LLM 调用或检查配额
        return True
    except Exception:
        return False
```

---

## 四、依赖管理与方法

### 4.1 依赖管理工具对比

```mermaid
graph TB
    subgraph 依赖管理工具选型
        A[需求] --> B{是否新项目?}
        B -- 是 --> C{是否追求<br/>现代化工具链?}
        C -- 是 --> D[Poetry / PDM<br/>推荐 Poetry]
        C -- 否 --> E[venv + pip +<br/>requirements.txt]
        B -- 否 --> F{是否科学计算<br/>重依赖?}
        F -- 是 --> G[Conda<br/>隔离非 Python 依赖]
        F -- 否 --> E
    end

    style D fill:#d4edda,stroke:#155724,stroke-width:2px
    style E fill:#fff3cd,stroke:#d39e00,stroke-width:2px
```

| 工具 | 锁文件 | 优势 | 劣势 | 推荐场景 |
|------|--------|------|------|---------|
| **pip + venv** | requirements.txt | 简单、通用、无学习成本 | 依赖解析弱、无锁版本传递 | 简单项目、CI 友好 |
| **Poetry** | poetry.lock | 现代化、锁文件精确、打包一体化 | 学习曲线、CI 慢 | **新项目首选** |
| **PDM** | pdm.lock | 符合 PEP 标准、快 | 生态小 | 纯粹主义者 |
| **Conda** | environment.yml | 隔离非 Python 依赖(C 库) | 占用大、慢 | ML/科学计算 |

> **生产建议**:简单 Agent 服务用 **venv + pip + requirements.txt**(最通用);复杂项目用 **Poetry**(锁文件更可靠)。本文以 venv + pip 为主示例。

### 4.2 创建虚拟环境

虚拟环境是 Python 部署的**第一原则**——每个项目独立隔离依赖,避免系统级污染。

```bash
# 切换到部署用户
sudo su - agent

# 1. 创建虚拟环境(指定 Python 版本)
python3.11 -m venv /opt/agent/venv

# 2. 激活虚拟环境
source /opt/agent/venv/bin/activate

# 3. 升级 pip 与基础工具
pip install --upgrade pip setuptools wheel

# 4. 验证
which python   # 应输出: /opt/agent/venv/bin/python
python --version  # 应输出: Python 3.11.x
```

```mermaid
flowchart LR
    subgraph 系统Python
        SP[/usr/bin/python3.11]
    end
    subgraph 虚拟环境
        VP[/opt/agent/venv/bin/python]
        VS[site-packages<br/>独立依赖]
    end
    subgraph 另一项目虚拟环境
        OP[/opt/other/venv/bin/python]
        OS[site-packages<br/>独立依赖]
    end

    SP -.基础解释器.-> VP
    SP -.基础解释器.-> OP
    VP --- VS
    OP --- OS

    style VS fill:#d4edda,stroke:#155724
    style OS fill:#d1ecf1,stroke:#0c5460
```

### 4.3 依赖清单编写

#### `requirements.txt` —— 基础依赖

```txt
# === Web 框架 ===
fastapi==0.111.0
uvicorn[standard]==0.30.1
gunicorn==22.0.0
python-multipart==0.0.9

# === Agent 框架(按需选一) ===
langchain==0.2.7
langchain-core==0.2.12
langchain-openai==0.1.14
langgraph==0.1.5

# === LLM 客户端 ===
openai==1.35.10
anthropic==0.28.0

# === 数据层 ===
sqlalchemy[asyncio]==2.0.30
asyncpg==0.29.0            # PostgreSQL 异步驱动
redis==5.0.7
qdrant-client==1.9.1       # 向量数据库

# === 配置与校验 ===
pydantic==2.7.4
pydantic-settings==2.3.4
pyyaml==6.0.1

# === 日志与监控 ===
structlog==24.2.0
prometheus-client==0.20.0

# === 工具库 ===
httpx==0.27.0              # 异步 HTTP 客户端
tenacity==8.4.1            # 重试机制
tiktoken==0.7.0            # Token 计数
python-dotenv==1.0.1
```

#### `requirements-prod.txt` —— 生产环境依赖

```txt
# 包含基础依赖
-r requirements.txt

# 生产环境额外依赖
sentry-sdk==2.6.0          # 错误追踪
opentelemetry-api==1.25.0  # 分布式追踪
opentelemetry-instrumentation-fastapi==0.46b0
```

> **关键原则**:依赖必须**锁版本**(用 `==` 而非 `>=`),避免部署时拉到不兼容的新版本。

### 4.4 安装依赖

```bash
# 激活虚拟环境
source /opt/agent/venv/bin/activate

# 1. 安装基础依赖
cd /opt/agent/app
pip install -r requirements.txt

# 2. 生产环境追加生产依赖
pip install -r requirements-prod.txt

# 3. 验证关键依赖
python -c "import fastapi; print(f'fastapi {fastapi.__version__}')"
python -c "import langchain; print(f'langchain {langchain.__version__}')"
python -c "import openai; print(f'openai {openai.__version__}')"

# 4. 导出当前环境的精确依赖(用于复现)
pip freeze > requirements-frozen.txt
```

### 4.5 Poetry 方式(可选)

```bash
# 安装 Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 在项目根目录初始化
cd /opt/agent/app
poetry init --no-interaction \
    --name agent-service \
    --version 1.0.0 \
    --description "Python Agent Service"

# 添加依赖
poetry add fastapi@0.111.0 uvicorn[standard]@0.30.1 gunicorn@22.0.0
poetry add langchain@0.2.7 langchain-openai@0.1.14
poetry add sqlalchemy[asyncio]@2.0.30 asyncpg@0.29.0 redis@5.0.7

# 安装(自动创建虚拟环境)
poetry install --no-dev

# 在 Poetry 环境中执行命令
poetry run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 五、配置文件设置

### 5.1 配置管理策略

```mermaid
graph TB
    subgraph 配置分层策略
        L1[1. 默认配置<br/>config/settings.yaml<br/>随代码版本管理]
        L2[2. 环境配置<br/>config/settings.prod.yaml<br/>按环境覆盖]
        L3[3. 环境变量<br/>.env / OS ENV<br/>敏感信息与覆盖]
        L4[4. 启动参数<br/>命令行参数<br/>临时覆盖]
    end

    L1 --> L2 --> L3 --> L4
    L4 -.最终生效.-> FINAL[运行时配置]

    style L3 fill:#f8d7da,stroke:#721c24,stroke-width:2px
    style FINAL fill:#d4edda,stroke:#155724
```

**核心原则**:
- **敏感信息**(API Key、密码)→ 环境变量,不进代码库
- **环境差异**(URL、端口)→ 环境配置文件
- **通用默认** → 默认配置文件

### 5.2 YAML 配置文件

#### `config/settings.yaml` —— 默认配置

```yaml
# ========================================
# Python Agent 服务配置 - 默认
# ========================================

app:
  name: "python-agent-service"
  version: "1.0.0"
  env: "development"           # development / staging / production
  debug: false

server:
  host: "0.0.0.0"
  port: 8000
  workers: 4                   # Gunicorn worker 数(通常 CPU 数 × 2 + 1)
  timeout: 120                 # 请求超时(秒),LLM 调用需较长
  keepalive: 5
  max_requests: 1000           # worker 处理多少请求后重启(防内存泄漏)
  max_requests_jitter: 50      # 重启抖动,避免所有 worker 同时重启

llm:
  provider: "openai"           # openai / anthropic / local
  model: "gpt-4o-mini"
  temperature: 0.7
  max_tokens: 2000
  timeout: 60
  retry_max: 3
  retry_backoff: 1.5

agent:
  framework: "langchain"       # langchain / langgraph / crewai
  max_iterations: 10           # Agent 最大迭代次数
  memory_window: 20            # 上下文消息条数
  enable_tools: true

database:
  url: "postgresql+asyncpg://agent:password@localhost:5432/agent"
  pool_size: 10
  max_overflow: 20
  pool_timeout: 30
  pool_recycle: 1800

redis:
  url: "redis://localhost:6379/0"
  max_connections: 20
  session_ttl: 86400           # 会话缓存 TTL(秒)

vector_db:
  url: "http://localhost:6333"
  collection: "agent_memory"
  dimension: 1536

logging:
  level: "INFO"                # DEBUG / INFO / WARNING / ERROR
  format: "json"               # json / text
  file: "/opt/agent/logs/app.log"
  max_size_mb: 100
  backup_count: 10
  rotation: "daily"

monitoring:
  enabled: true
  metrics_path: "/metrics"
  sentry_dsn: ""               # 由环境变量注入
```

#### `config/settings.prod.yaml` —— 生产覆盖配置

```yaml
# ========================================
# 生产环境覆盖配置
# ========================================

app:
  env: "production"
  debug: false

server:
  workers: 8                   # 生产环境更多 worker
  timeout: 180

llm:
  model: "gpt-4o"              # 生产用更强模型
  temperature: 0.3             # 生产降低随机性

database:
  pool_size: 20
  max_overflow: 30

logging:
  level: "INFO"                # 生产不输出 DEBUG
  format: "json"               # JSON 格式便于日志聚合
```

### 5.3 环境变量配置

#### `.env` 文件 —— 敏感信息

```bash
# === .env 文件 (chmod 600,不进 git) ===

# LLM API Keys
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx

# 数据库密码
DATABASE_URL=postgresql+asyncpg://agent:StrongPwd2026@db.internal:5432/agent

# Redis 密码
REDIS_URL=redis://:RedisPwd2026@redis.internal:6379/0

# 应用密钥
APP_SECRET_KEY=your-super-secret-key-here
JWT_SECRET=another-secret-key

# Sentry DSN
SENTRY_DSN=https://xxx@sentry.io/123

# 运行环境标识
APP_ENV=production
```

#### `.env.example` —— 模板(进 git)

```bash
# 复制为 .env 并填入实际值
cp .env.example .env

OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
REDIS_URL=redis://:pass@host:6379/0
APP_SECRET_KEY=generate-a-random-secret
SENTRY_DSN=
APP_ENV=development
```

```bash
# 设置文件权限(仅 owner 可读)
chmod 600 .env
```

### 5.4 配置加载实现

```python
"""
配置加载器:支持 YAML + 环境变量分层覆盖
"""
import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    timeout: int = 120
    keepalive: int = 5
    max_requests: int = 1000
    max_requests_jitter: int = 50


class LLMConfig(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 60
    retry_max: int = 3
    retry_backoff: float = 1.5
    api_key: str = Field(default="", alias="OPENAI_API_KEY")


class AppConfig(BaseModel):
    name: str
    version: str = "1.0.0"
    env: str = "development"
    debug: bool = False
    server: ServerConfig = ServerConfig()
    llm: LLMConfig = LLMConfig()


def load_config(env: str = None) -> AppConfig:
    """
    分层加载配置:
    1. 默认 settings.yaml
    2. 环境特定 settings.{env}.yaml 覆盖
    3. 环境变量最终覆盖(敏感信息)
    """
    config_dir = Path(__file__).parent.parent.parent / "config"
    env = env or os.getenv("APP_ENV", "development")
    
    # 1. 加载默认配置
    with open(config_dir / "settings.yaml") as f:
        config_data = yaml.safe_load(f)
    
    # 2. 加载环境特定配置并覆盖
    env_config = config_dir / f"settings.{env}.yaml"
    if env_config.exists():
        with open(env_config) as f:
            env_data = yaml.safe_load(f)
        config_data = _deep_merge(config_data, env_data)
    
    # 3. 环境变量覆盖(敏感信息)
    config_data["llm"]["api_key"] = os.getenv("OPENAI_API_KEY", "")
    
    return AppConfig(**config_data)


def _deep_merge(base: dict, override: dict) -> dict:
    """深度合并两个字典"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
```

### 5.5 日志配置

#### `config/logging.yaml`

```yaml
version: 1
disable_existing_loggers: false

formatters:
  default:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  json:
    class: pythonjsonlogger.jsonlogger.JsonFormatter
    format: '%(asctime)s %(name)s %(levelname)s %(message)s %(module)s %(funcName)s %(lineno)d'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: default
    stream: ext://sys.stdout

  file:
    class: logging.handlers.RotatingFileHandler
    level: INFO
    formatter: json
    filename: /opt/agent/logs/app.log
    maxBytes: 104857600        # 100 MB
    backupCount: 10
    encoding: utf-8

  error_file:
    class: logging.handlers.RotatingFileHandler
    level: ERROR
    formatter: json
    filename: /opt/agent/logs/error.log
    maxBytes: 104857600
    backupCount: 5
    encoding: utf-8

loggers:
  app:
    level: INFO
    handlers: [console, file, error_file]
    propagate: false
  uvicorn:
    level: INFO
    handlers: [console, file]
    propagate: false
  sqlalchemy:
    level: WARNING
    handlers: [console]
    propagate: