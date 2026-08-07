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
    propagate: false

root:
  level: WARNING
  handlers: [console, file]
```

---

## 六、服务启动命令

### 6.1 开发环境启动

开发环境使用 Uvicorn 直接启动,支持热重载:

```bash
# 激活虚拟环境
source /opt/agent/venv/bin/activate

# 进入项目目录
cd /opt/agent/app

# 设置环境变量
export APP_ENV=development
export OPENAI_API_KEY=sk-xxx

# 启动(热重载)
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --reload-dir app \
    --log-level debug

# 访问
# API: http://localhost:8000/api/v1/health
# 文档: http://localhost:8000/docs
```

### 6.2 生产环境启动(Gunicorn + Uvicorn Worker)

生产环境使用 **Gunicorn** 作为进程管理器,**Uvicorn** 作为 ASGI worker:

```mermaid
graph TB
    subgraph Gunicorn 主进程
        MASTER[Master Process<br/>进程管理/信号处理]
    end
    
    subgraph Uvicorn Worker 进程
        W1[Worker 1<br/>独立事件循环]
        W2[Worker 2<br/>独立事件循环]
        W3[Worker 3<br/>独立事件循环]
        W4[Worker 4<br/>独立事件循环]
    end
    
    MASTER --> W1 & W2 & W3 & W4
    MASTER -.监控.-> W1 & W2 & W3 & W4
    MASTER -.重启崩溃 worker.-> W1
    
    style MASTER fill:#fff3cd,stroke:#d39e00,stroke-width:2px
    style W1 fill:#d4edda,stroke:#155724
```

```bash
# 激活虚拟环境
source /opt/agent/venv/bin/activate

# 进入项目目录
cd /opt/agent/app

# 设置环境
export APP_ENV=production
export OPENAI_API_KEY=sk-xxx

# 启动 Gunicorn
gunicorn app.main:app \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 180 \
    --keepalive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --graceful-timeout 30 \
    --access-logfile /opt/agent/logs/access.log \
    --error-logfile /opt/agent/logs/gunicorn-error.log \
    --log-level info
```

#### Gunicorn 关键参数详解

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `--bind` | `0.0.0.0:8000` | 监听地址,生产建议 `127.0.0.1:8000`(由 Nginx 反代) |
| `--workers` | `CPU × 2 + 1` | worker 数,IO 密集可略多 |
| `--worker-class` | `uvicorn.workers.UvicornWorker` | ASGI worker,支持异步 |
| `--timeout` | `180` | worker 处理请求超时,LLM 调用需较长 |
| `--keepalive` | `5` | keep-alive 连接秒数 |
| `--max-requests` | `1000` | worker 处理 N 请求后重启,防内存泄漏 |
| `--max-requests-jitter` | `50` | 重启抖动,避免所有 worker 同时重启 |
| `--graceful-timeout` | `30` | 优雅关闭等待时间 |
| `--preload` | (谨慎) | 预加载应用,省内存但崩溃影响所有 worker |

> **workers 数量公式**: `(CPU 核数 × 2) + 1`。例如 4 核服务器 = 9 workers。Agent 主要是 IO 密集(LLM 调用等待),可适当增加。

### 6.3 启动脚本封装

#### `scripts/start.sh`

```bash
#!/bin/bash
# ============================================
# Python Agent 服务启动脚本
# ============================================

set -e

# === 路径定义 ===
APP_DIR="/opt/agent/app"
VENV_DIR="/opt/agent/venv"
LOG_DIR="/opt/agent/logs"
PID_FILE="$LOG_DIR/agent.pid"

# === 环境加载 ===
source "$VENV_DIR/bin/activate"
cd "$APP_DIR"

# 加载 .env
if [ -f "$APP_DIR/.env" ]; then
    set -a
    source "$APP_DIR/.env"
    set +a
fi

# === 前置检查 ===
mkdir -p "$LOG_DIR"

if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "[ERROR] 服务已在运行, PID: $OLD_PID"
        exit 1
    fi
    rm -f "$PID_FILE"
fi

# === 启动 Gunicorn ===
echo "[INFO] 启动 Python Agent 服务..."

exec gunicorn app.main:app \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 180 \
    --keepalive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --graceful-timeout 30 \
    --access-logfile "$LOG_DIR/access.log" \
    --error-logfile "$LOG_DIR/gunicorn-error.log" \
    --log-level info \
    --pid "$PID_FILE"
```

#### `scripts/stop.sh`

```bash
#!/bin/bash
# ============================================
# Python Agent 服务停止脚本
# ============================================

PID_FILE="/opt/agent/logs/agent.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "[INFO] PID 文件不存在,服务可能未运行"
    exit 0
fi

PID=$(cat "$PID_FILE")

if kill -0 "$PID" 2>/dev/null; then
    echo "[INFO] 优雅停止服务, PID: $PID"
    kill -TERM "$PID"
    
    # 等待最多 30 秒
    for i in $(seq 1 30); do
        if ! kill -0 "$PID" 2>/dev/null; then
            echo "[INFO] 服务已停止"
            rm -f "$PID_FILE"
            exit 0
        fi
        sleep 1
    done
    
    echo "[WARN] 优雅停止超时,强制终止"
    kill -KILL "$PID"
    rm -f "$PID_FILE"
else
    echo "[INFO] 进程不存在,清理 PID 文件"
    rm -f "$PID_FILE"
fi
```

```bash
# 赋予执行权限
chmod +x scripts/start.sh scripts/stop.sh

# 使用
./scripts/start.sh   # 启动
./scripts/stop.sh    # 停止
```

### 6.4 Makefile 快捷命令

```makefile
# === Python Agent 服务 Makefile ===

.PHONY: install dev prod start stop restart logs test

install:
	pip install -r requirements.txt

dev:
	APP_ENV=development uvicorn app.main:app --reload --port 8000

prod:
	APP_ENV=production ./scripts/start.sh

start: prod

stop:
	./scripts/stop.sh

restart: stop start

logs:
	tail -f /opt/agent/logs/app.log

test:
	pytest tests/ -v --cov=app
```

---

## 七、进程管理方式

### 7.1 进程管理方案对比

```mermaid
graph TB
    subgraph 进程管理方案选型
        A[选型需求] --> B{是否容器化?}
        B -- 是 --> C[Docker / K8s<br/>容器编排管理]
        B -- 否 --> D{是否 systemd 系统?}
        D -- 是 --> E[systemd<br/>Linux 原生]
        D -- 否 --> F[Supervisor<br/>跨平台]
        
        E --> G[推荐:systemd<br/>生产首选]
        F --> H[备选:Supervisor<br/>老服务器]
    end

    style G fill:#d4edda,stroke:#155724,stroke-width:2px
    style C fill:#d1ecf1,stroke:#0c5460,stroke-width:2px
```

| 方案 | 优势 | 劣势 | 推荐场景 |
|------|------|------|---------|
| **systemd** | Linux 原生、零依赖、功能强大 | 仅限 Linux | **生产首选** |
| **Supervisor** | 跨平台、配置简单、Web UI | 需额外安装、本身需被管理 | 老旧系统、多平台 |
| **Docker** | 环境隔离、易于迁移 | 需 Docker 运行时 | 容器化部署 |
| **screen/tmux** | 简单 | 不可靠、无监控 | 仅临时调试 |

### 7.2 方案一:systemd(生产推荐)

systemd 是现代 Linux 的 init 系统,提供完整的进程管理、自动重启、日志收集能力。

#### `/etc/systemd/system/agent.service`

```ini
[Unit]
Description=Python Agent Service
Documentation=https://github.com/your-org/agent-service
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
# === 用户与权限 ===
User=agent
Group=agent

# === 工作目录 ===
WorkingDirectory=/opt/agent/app

# === 环境变量 ===
Environment="APP_ENV=production"
Environment="PYTHONPATH=/opt/agent/app"
EnvironmentFile=/opt/agent/app/.env

# === 虚拟环境 ===
Environment="PATH=/opt/agent/venv/bin:/usr/local/bin:/usr/bin:/bin"

# === 启动命令 ===
ExecStart=/opt/agent/venv/bin/gunicorn app.main:app \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 180 \
    --keepalive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --graceful-timeout 30 \
    --access-logfile /opt/agent/logs/access.log \
    --error-logfile /opt/agent/logs/gunicorn-error.log \
    --log-level info

# === 重启策略 ===
Restart=always
RestartSec=5
StartLimitInterval=60
StartLimitBurst=3

# === 资源限制 ===
LimitNOFILE=65536
LimitNPROC=65536
MemoryMax=2G
CPUQuota=300%

# === 优雅停止 ===
KillSignal=SIGTERM
TimeoutStopSec=30
KillMode=mixed

# === 安全加固 ===
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/agent/logs /opt/agent/data

# === 日志 ===
StandardOutput=journal
StandardError=journal
SyslogIdentifier=agent-service

[Install]
WantedBy=multi-user.target
```

#### systemd 管理命令

```bash
# 1. 重新加载 systemd 配置(修改 service 文件后必须执行)
sudo systemctl daemon-reload

# 2. 启用开机自启
sudo systemctl enable agent

# 3. 启动服务
sudo systemctl start agent

# 4. 查看状态
sudo systemctl status agent

# 5. 停止服务
sudo systemctl stop agent

# 6. 重启服务
sudo systemctl restart agent

# 7. 重新加载配置(不重启,仅 reload)
sudo systemctl reload agent

# 8. 查看日志
sudo journalctl -u agent -f           # 实时跟踪
sudo journalctl -u agent --since "1 hour ago"
sudo journalctl -u agent -p err       # 仅错误
```

#### systemd 优势图解

```mermaid
flowchart TB
    subgraph systemd 管理能力
        A[开机自启] --> S[系统启动时自动拉起]
        B[崩溃重启] --> R[Restart=always<br/>5秒后自动重启]
        C[依赖管理] --> D[After/Wants<br/>DB/Redis 就绪后再启]
        E[资源限制] --> L[MemoryMax/CPUQuota<br/>防资源耗尽]
        F[日志收集] --> J[journald<br/>统一日志]
        G[安全隔离] --> SE[ProtectSystem<br/>最小权限]
    end

    style R fill:#d4edda,stroke:#155724,stroke-width:2px
    style D fill:#d1ecf1,stroke:#0c5460
```

### 7.3 方案二:Supervisor

Supervisor 是独立的进程管理工具,跨平台,配置简单。

#### 安装 Supervisor

```bash
# Ubuntu/Debian
sudo apt install -y supervisor

# CentOS/RHEL
sudo dnf install -y supervisor
sudo systemctl enable supervisord
sudo systemctl start supervisord
```

#### `/etc/supervisor/conf.d/agent.conf`

```ini
[program:agent]
command=/opt/agent/venv/bin/gunicorn app.main:app \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 180 \
    --max-requests 1000

directory=/opt/agent/app
user=agent

# 环境变量
environment=APP_ENV="production",PYTHONPATH="/opt/agent/app",OPENAI_API_KEY="%(ENV_OPENAI_API_KEY)s"

# 自动启动与重启
autostart=true
autorestart=true
startsecs=5
startretries=3
stopwaitsecs=30

# 日志
stdout_logfile=/opt/agent/logs/supervisor-stdout.log
stdout_logfile_maxbytes=100MB
stdout_logfile_backups=10
stderr_logfile=/opt/agent/logs/supervisor-stderr.log
stderr_logfile_maxbytes=100MB
stderr_logfile_backups=10

# 信号
stopsignal=TERM
killasgroup=true
stopasgroup=true
```

#### Supervisor 管理命令

```bash
# 重新加载配置
sudo supervisorctl reread
sudo supervisorctl update

# 启动/停止/重启
sudo supervisorctl start agent
sudo supervisorctl stop agent
sudo supervisorctl restart agent

# 查看状态
sudo supervisorctl status
sudo supervisorctl status agent

# 查看日志
sudo supervisorctl tail -f agent stderr
```

### 7.4 systemd vs Supervisor 对比

| 维度 | systemd | Supervisor |
|------|---------|-----------|
| **依赖** | Linux 内置 | 需额外安装 |
| **平台** | 仅 Linux | Linux/Mac/Unix |
| **配置** | INI 格式,功能丰富 | INI 格式,简洁 |
| **开机自启** | 原生支持 | 需 supervisord 自启 |
| **依赖管理** | After/Wants | priority |
| **资源限制** | MemoryMax/CPUQuota | 需外部工具 |
| **安全隔离** | ProtectSystem 等 | 无 |
| **日志** | journald 统一 | 独立日志文件 |
| **Web UI** | 无 | 内置 |
| **生产推荐** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 八、反向代理与负载均衡

### 8.1 为何需要反向代理

```mermaid
graph LR
    subgraph 无反向代理
        C1[客户端] --> P1[Gunicorn:8000<br/>单点暴露]
    end
    
    subgraph 有反向代理
        C2[客户端] --> N[Nginx:443<br/>SSL终结/限流/压缩]
        N --> P2[Gunicorn:127.0.0.1:8000<br/>内网隔离]
    end

    style N fill:#d4edda,stroke:#155724,stroke-width:2px
    style P2 fill:#d1ecf1,stroke:#0c5460
```

反向代理(Nginx)的五大作用:
1. **SSL 终结**:HTTPS 加解密在 Nginx 处理,后端走 HTTP
2. **负载均衡**:多 Agent 实例间分发请求
3. **限流防护**:防止恶意刷接口
4. **静态资源**:API 文档、前端静态文件
5. **安全隔离**:Gunicorn 仅监听 127.0.0.1

### 8.2 Nginx 配置

#### `/etc/nginx/sites-available/agent`

```nginx
# ========================================
# Python Agent 服务 Nginx 反向代理
# ========================================

# 上游服务器:多个 Agent 实例做负载均衡
upstream agent_backend {
    # least_conn: 最少连接数策略(适合 LLM 长请求)
    least_conn;
    
    server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8002 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8003 max_fails=3 fail_timeout=30s;
    
    # 备用服务器
    server 127.0.0.1:8004 backup;
    
    keepalive 32;
}

# 限流区
limit_req_zone $binary_remote_addr zone=agent_api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=agent_chat:10m rate=2r/s;

# HTTP -> HTTPS 跳转
server {
    listen 80;
    server_name agent.example.com;
    
    # 健康检查允许 HTTP
    location /api/v1/health {
        proxy_pass http://agent_backend;
    }
    
    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS 主服务
server {
    listen 443 ssl http2;
    server_name agent.example.com;
    
    # === SSL 配置 ===
    ssl_certificate     /etc/letsencrypt/live/agent.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/agent.example.com/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;
    ssl_session_cache   shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # === 安全头 ===
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # === 请求体大小(LLM 可能有大输入) ===
    client_max_body_size 50m;
    
    # === 通用代理设置 ===
    proxy_set_header Host              $host;
    proxy_set_header X-Real-IP         $remote_addr;
    proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host  $host;
    
    # === 超时(LLM 调用较慢) ===
    proxy_connect_timeout 10s;
    proxy_send_timeout    300s;
    proxy_read_timeout    300s;
    
    # === 健康检查(无限流) ===
    location /api/v1/health {
        access_log off;
        proxy_pass http://agent_backend;
    }
    
    # === 对话接口(严格限流) ===
    location /api/v1/chat {
        limit_req zone=agent_chat burst=5 nodelay;
        proxy_pass http://agent_backend;
        proxy_buffering off;              # 流式响应需关闭缓冲
        proxy_cache off;
        proxy_http_version 1.1;
        proxy_set_header Connection "";   # keepalive
    }
    
    # === 通用 API(适度限流) ===
    location /api/v1/ {
        limit_req zone=agent_api burst=20 nodelay;
        proxy_pass http://agent_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
    
    # === API 文档(仅内网) ===
    location /docs {
        # allow 10.0.0.0/8;
        # deny all;
        proxy_pass http://agent_backend;
    }
    
    # === Prometheus 指标(仅内网) ===
    location /metrics {
        allow 127.0.0.1;
        allow 10.0.0.0/8;
        deny all;
        proxy_pass http://agent_backend;
    }
}
```

#### 启用配置

```bash
# 1. 创建软链启用站点
sudo ln -s /etc/nginx/sites-available/agent /etc/nginx/sites-enabled/

# 2. 测试配置语法
sudo nginx -t

# 3. 重新加载 Nginx
sudo systemctl reload nginx

# 4. 申请 SSL 证书(Let's Encrypt)
sudo certbot --nginx -d agent.example.com
```

### 8.3 负载均衡策略选择

```mermaid
graph TB
    subgraph 负载均衡策略
        RR[轮询<br/>round_robin<br/>默认]
        LC[最少连接<br/>least_conn<br/>推荐 LLM]
        IP[IP Hash<br/>ip_hash<br/>会话粘性]
        WL[权重<br/>weight<br/>异构服务器]
    end

    LC --> BEST[✅ 推荐<br/>LLM 请求耗时不均<br/>最少连接最公平]

    style LC fill:#d4edda,stroke:#155724,stroke-width:2px
    style BEST fill:#d4edda,stroke:#155724
```

| 策略 | 指令 | 适用场景 | LLM 场景评价 |
|------|------|---------|:----------:|
| 轮询 | (默认) | 请求耗时均匀 | ❌ LLM 耗时差异大,易倾斜 |
| 最少连接 | `least_conn` | 请求耗时不均 | ✅ **推荐** |
| IP Hash | `ip_hash` | 需会话粘性 | ⚠️ 会话应存在共享存储 |
| 权重 | `weight=N` | 异构服务器 | ✅ 配合最少连接 |

---

## 九、日志与监控

### 9.1 日志架构

```mermaid
flowchart TB
    subgraph 日志来源
        A1[Gunicorn 访问日志]
        A2[应用日志<br/>structlog]
        A3[systemd journal]
        A4[Nginx 访问/错误日志]
    end
    
    subgraph 日志收集
        F[Filebeat/Fluentd]
    end
    
    subgraph 日志存储与分析
        E[Elasticsearch<br/>/ Loki]
        K[Kibana<br/>/ Grafana]
    end
    
    A1 & A2 & A3 & A4 --> F
    F --> E
    E --> K

    style F fill:#fff3cd,stroke:#d39e00,stroke-width:2px
    style E fill:#d1ecf1,stroke:#0c5460
```

### 9.2 结构化日志实现

```python
"""
结构化日志:JSON 格式,便于 ELK/Loki 聚合分析
"""
import logging
import structlog
import sys


def setup_logging(env: str = "production"):
    """配置结构化日志"""
    
    if env == "production":
        # 生产:JSON 格式
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
            cache_logger_on_first_use=True,
        )
    else:
        # 开发:彩色控制台
        structlog.configure(
            processors=[
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                structlog.dev.ConsoleRenderer(colors=True),
            ],
        )


# 使用示例
logger = structlog.get_logger()

# 结构化日志
logger.info("agent_request_start",
            session_id="sess_123",
            user_id="u_456",
            query_length=len("你好"),
            model="gpt-4o")

logger.info("agent_request_end",
            session_id="sess_123",
            duration_ms=1234,
            tokens_used=150,
            status="success")

logger.error("llm_call_failed",
             provider="openai",
             error_type="RateLimitError",
             retry_count=3)
```

### 9.3 Prometheus 指标暴露

```python
"""
Prometheus 指标:暴露 /metrics 端点供 Prometheus 抓取
"""
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
from fastapi import FastAPI

# === 指标定义 ===
REQUEST_COUNT = Counter(
    "agent_requests_total",
    "Total request count",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "agent_request_duration_seconds",
    "Request latency in seconds",
    ["endpoint"],
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60, 120, 300]
)

LLM_CALL_COUNT = Counter(
    "agent_llm_calls_total",
    "LLM API call count",
    ["provider", "model", "status"]
)

LLM_TOKENS_USED = Counter(
    "agent_llm_tokens_total",
    "LLM tokens consumed",
    ["provider", "model", "type"]  # type: prompt/completion
)

ACTIVE_SESSIONS = Gauge(
    "agent_active_sessions",
    "Currently active sessions"
)


def setup_metrics(app: FastAPI):
    """注册 Prometheus 指标端点"""
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
```

### 9.4 Grafana 监控面板

关键监控指标:

| 指标类别 | 指标名 | 告警阈值 |
|---------|--------|---------|
| **可用性** | 服务存活(health) | 连续 3 次失败 |
| **流量** | QPS | 突增 200% |
| **延迟** | P99 请求延迟 | > 30s |
| **错误** | HTTP 5xx 比例 | > 1% |
| **LLM** | LLM 调用失败率 | > 5% |
| **资源** | CPU 使用率 | > 80% |
| **资源** | 内存使用率 | > 85% |
| **业务** | 活跃会话数 | 异常波动 |

```mermaid
graph LR
    subgraph Prometheus 抓取
        P[Prometheus]
        P -->|每 15s| M[/metrics]
    end
    
    subgraph Grafana 可视化
        G[Grafana]
        P --> G
        G --> D1[服务概览面板]
        G --> D2[LLM 调用面板]
        G --> D3[资源监控面板]
    end
    
    subgraph 告警
        AM[AlertManager]
        P --> AM
        AM --> SL[Slack/钉钉]
        AM --> EM[邮件]
    end

    style P fill:#fff3cd,stroke:#d39e00,stroke-width:2px
    style G fill:#d4edda,stroke:#155724
```

---

## 十、部署后验证步骤

### 10.1 验证流程总览

```mermaid
flowchart TB
    D[部署完成] --> V1[1. 进程状态验证]
    V1 --> V2[2. 端口监听验证]
    V2 --> V3[3. 健康检查验证]
    V3 --> V4[4. API 功能验证]
    V4 --> V5[5. LLM 调用验证]
    V5 --> V6[6. 数据层连通验证]
    V6 --> V7[7. 日志输出验证]
    V7 --> V8[8. 性能基线验证]
    V8 --> V9[9. 故障恢复验证]
    V9 --> OK[✅ 部署成功]

    style V1 fill:#d4edda,stroke:#155724
    style OK fill:#d4edda,stroke:#155724,stroke-width:2px
```

### 10.2 步骤 1:进程状态验证

```bash
# 1.1 检查 systemd 服务状态
sudo systemctl status agent

# 期望输出:
# ● agent.service - Python Agent Service
#      Loaded: loaded (/etc/systemd/system/agent.service; enabled)
#      Active: active (running)
#      Main PID: 12345 (gunicorn)
#        Tasks: 5
#       Memory: 256.0M
#          CPU: 1.234s

# 1.2 检查所有 worker 进程
ps aux | grep gunicorn | grep -v grep

# 期望输出:1 主进程 + N worker 进程
# agent  12345  0.0  1.2  ...  gunicorn: master [app.main:app]
# agent  12346  0.5  1.5  ...  gunicorn: worker [uvicorn] [app.main:app]
# agent  12347  0.4  1.5  ...  gunicorn: worker [uvicorn] [app.main:app]
# ...

# 1.3 检查进程数是否符合配置
ps aux | grep -c "[g]unicorn: worker"
# 期望: 4 (与 --workers 一致)
```

### 10.3 步骤 2:端口监听验证

```bash
# 2.1 检查端口监听
sudo ss -tlnp | grep 8000

# 期望输出:
# LISTEN  0  2048  127.0.0.1:8000  0.0.0.0:*  users:(("gunicorn",pid=12345,fd=7))

# 2.2 检查 Nginx 监听 443
sudo ss -tlnp | grep -E ':(80|443)'

# 2.3 本地连通性测试
curl -v http://127.0.0.1:8000/api/v1/health

# 期望输出:
# < HTTP/1.1 200 OK
# < Server: gunicorn
# {"status":"ok","timestamp":"2026-08-07T..."}
```

### 10.4 步骤 3:健康检查验证

```bash
# 3.1 存活检查(Liveness)
curl -s http://127.0.0.1:8000/api/v1/health | python3 -m json.tool

# 期望:
# {
#     "status": "ok",
#     "timestamp": "2026-08-07T10:00:00.000000"
# }

# 3.2 就绪检查(Readiness)—— 验证依赖
curl -s http://127.0.0.1:8000/api/v1/health/ready | python3 -m json.tool

# 期望:
# {
#     "status": "ready",
#     "checks": {
#         "database": true,
#         "redis": true,
#         "llm": true
#     },
#     "timestamp": "2026-08-07T10:00:00.000000"
# }

# 3.3 通过 Nginx 验证(外部访问)
curl -s https://agent.example.com/api/v1/health | python3 -m json.tool
```

### 10.5 步骤 4:API 功能验证

```bash
# 4.1 验证 API 文档可访问
curl -s https://agent.example.com/docs | head -5

# 4.2 创建会话
SESSION=$(curl -s -X POST https://agent.example.com/api/v1/sessions \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"title":"部署验证"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")

echo "Session ID: $SESSION"

# 4.3 发送消息
curl -s -X POST "https://agent.example.com/api/v1/chat" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{\"session_id\":\"$SESSION\",\"message\":\"你好,请做个自我介绍\"}" \
    | python3 -m json.tool

# 期望:返回 AI 回复
```

### 10.6 步骤 5:LLM 调用验证

```bash
# 5.1 验证 OpenAI API 连通性
curl -s https://api.openai.com/v1/models \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    | python3 -c "import sys,json; data=json.load(sys.stdin); print(f'可用模型数: {len(data[\"data\"])}')"

# 5.2 通过应用验证 LLM 调用
curl -s -X POST https://agent.example.com/api/v1/chat \
    -H "Content-Type: application/json" \
    -d '{"message":"1+1等于几?"}' \
    | python3 -m json.tool

# 5.3 检查 LLM 调用日志
sudo journalctl -u agent | grep "llm_call" | tail -5
```

### 10.7 步骤 6:数据层连通验证

```bash
# 6.1 PostgreSQL 连通性
PGPASSWORD=$DB_PASSWORD psql -h localhost -U agent -d agent -c "SELECT 1 AS test;"

# 6.2 Redis 连通性
redis-cli -a $REDIS_PASSWORD PING
# 期望: PONG

# 6.3 向量数据库连通性
curl -s http://localhost:6333/health | python3 -m json.tool
```

### 10.8 步骤 7:日志输出验证

```bash
# 7.1 检查应用日志
ls -lh /opt/agent/logs/
# 期望: app.log, access.log, gunicorn-error.log 等文件存在

# 7.2 实时查看日志
sudo journalctl -u agent -f

# 7.3 检查是否有错误
sudo journalctl -u agent -p err --since "10 minutes ago"
# 期望: 无输出或仅少量警告

# 7.4 验证 JSON 格式日志
tail -1 /opt/agent/logs/app.log | python3 -m json.tool
# 期望: 能正常解析为 JSON
```

### 10.9 步骤 8:性能基线验证

```bash
# 8.1 简单压测(需安装 wrk 或 ab)
# 安装 wrk
sudo apt install -y wrk

# 压测健康检查接口
wrk -t4 -c50 -d30s http://127.0.0.1:8000/api/v1/health

# 期望基线:
# Requests/sec:  > 5000
# Latency P99:   < 50ms
# Non-2xx:       0

# 8.2 对话接口压测(注意 LLM 成本)
wrk -t2 -c10 -d10s -s chat_script.lua http://127.0.0.1:8000/api/v1/chat

# 8.3 资源占用检查
top -b -n 1 | head -20
free -h
df -h
```

### 10.10 步骤 9:故障恢复验证

```bash
# 9.1 模拟 worker 崩溃 —— systemd 应自动重启
WORKER_PID=$(ps aux | grep "[g]unicorn: worker" | head -1 | awk '{print $2}')
echo "Killing worker PID: $WORKER_PID"
kill -9 $WORKER_PID

# 等待 5 秒后检查
sleep 5
ps aux | grep "[g]unicorn: worker" | wc -l
# 期望: worker 数量恢复(自动拉起新 worker)

# 9.2 模拟服务崩溃 —— 验证 systemd 自动重启
sudo systemctl kill agent --signal=KILL
sleep 10
sudo systemctl status agent
# 期望: active (running),且 Restart 计数 +1

# 9.3 验证日志中的重启记录
sudo journalctl -u agent | grep -i "restart" | tail -5
```

### 10.11 验证检查清单

| # | 验证项 | 验证方法 | 期望结果 | ✓ |
|---|--------|---------|---------|---|
| 1 | 服务状态 | `systemctl status agent` | active (running) | ☐ |
| 2 | Worker 进程 | `ps aux \| grep gunicorn` | 1 主 + N worker | ☐ |
| 3 | 端口监听 | `ss -tlnp \| grep 8000` | LISTEN | ☐ |
| 4 | 存活检查 | `curl /health` | 200 + status:ok | ☐ |
| 5 | 就绪检查 | `curl /health/ready` | 所有 checks: true | ☐ |
| 6 | API 文档 | `curl /docs` | HTML 页面 | ☐ |
| 7 | 创建会话 | POST /sessions | 200 + session_id | ☐ |
| 8 | 对话调用 | POST /chat | 200 + AI 回复 | ☐ |
| 9 | LLM 连通 | journalctl 日志 | llm_call success | ☐ |
| 10 | DB 连通 | psql SELECT 1 | 返回 1 | ☐ |
| 11 | Redis 连通 | redis-cli PING | PONG | ☐ |
| 12 | 日志输出 | `ls /opt/agent/logs/` | 文件存在且更新 | ☐ |
| 13 | 日志格式 | `tail app.log` | JSON 可解析 | ☐ |
| 14 | 性能基线 | `wrk` 压测 | QPS > 5000 | ☐ |
| 15 | 崩溃恢复 | kill worker | 自动重启 | ☐ |
| 16 | 开机自启 | `systemctl is-enabled` | enabled | ☐ |

---

## 十一、容器化部署方案

### 11.1 Dockerfile

```dockerfile
# ============================================
# Python Agent 服务 Dockerfile (多阶段构建)
# ============================================

# === 阶段 1: 依赖构建 ===
FROM python:3.11-slim AS builder

WORKDIR /build

# 安装编译依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt requirements-prod.txt ./

# 安装依赖到指定目录(便于复制)
RUN pip install --user --no-cache-dir -r requirements-prod.txt

# === 阶段 2: 运行时镜像 ===
FROM python:3.11-slim AS runtime

# 安装运行时系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN groupadd -r agent && useradd -r -g agent -d /app -s /bin/bash agent

# 复制依赖
COPY --from=builder /root/.local /home/agent/.local

# 复制应用代码
COPY --chown=agent:agent . /app

WORKDIR /app

# 切换用户
USER agent

# 环境变量
ENV PATH=/home/agent/.local/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV=production

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "app.main:app", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--timeout", "180", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "50", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]
```

### 11.2 docker-compose.yml

```yaml
version: "3.9"

services:
  agent:
    build: .
    image: agent-service:1.0.0
    container_name: agent-service
    restart: unless-stopped
    ports:
      - "127.0.0.1:8000:8000"
    env_file:
      - .env
    environment:
      - APP_ENV=production
      - DATABASE_URL=postgresql+asyncpg://agent:pass@postgres:5432/agent
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config:ro
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - agent-net
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 2G
        reservations:
          memory: 512M

  postgres:
    image: postgres:16-alpine
    container_name: agent-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: agent
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: agent
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agent"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - agent-net

  redis:
    image: redis:7-alpine
    container_name: agent-redis
    restart: unless-stopped
    command: redis-server --requirepass pass
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "pass", "PING"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - agent-net

  nginx:
    image: nginx:1.25-alpine
    container_name: agent-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./certs:/etc/letsencrypt:ro
    depends_on:
      - agent
    networks:
      - agent-net

volumes:
  postgres-data:
  redis-data:

networks:
  agent-net:
    driver: bridge
```

### 11.3 容器化部署命令

```bash
# 1. 构建镜像
docker compose build

# 2. 启动全部服务
docker compose up -d

# 3. 查看状态
docker compose ps

# 4. 查看日志
docker compose logs -f agent

# 5. 重新构建并启动
docker compose up -d --build

# 6. 停止
docker compose down

# 7. 停止并删除数据卷(谨慎!)
docker compose down -v
```

---

## 十二、生产环境稳定性保障

### 12.1 稳定性保障体系

```mermaid
flowchart TB
    subgraph 稳定性保障五道防线
        D1[1. 资源限制<br/>防资源耗尽]
        D2[2. 自动重启<br/>防进程崩溃]
        D3[3. 健康检查<br/>防僵尸服务]
        D4[4. 熔断降级<br/>防级联故障]
        D5[5. 监控告警<br/>防故障扩散]
    end
    
    D1 --> D2 --> D3 --> D4 --> D5 --> STABLE[服务稳定]

    style D1 fill:#d4edda,stroke:#155724
    style STABLE fill:#d4edda,stroke:#155724,stroke-width:2px
```

### 12.2 资源限制配置

#### systemd 资源限制

```ini
# /etc/systemd/system/agent.service 中的 [Service] 段

# 内存限制(超过则 OOM kill)
MemoryMax=2G
MemoryHigh=1500M

# CPU 限制(300% = 3 核)
CPUQuota=300%

# 文件描述符
LimitNOFILE=65536

# 进程数
LimitNPROC=4096

# 禁止产生 core dump
LimitCORE=0
```

#### Gunicorn worker 自动重启防泄漏

```bash
# 每个 worker 处理 1000 个请求后自动重启
--max-requests 1000
--max-requests-jitter 50    # 抖动避免同时重启
```

### 12.3 熔断与降级

```python
"""
熔断器:LLM 调用失败率过高时自动熔断,保护系统
"""
import asyncio
from datetime import datetime, timedelta
from enum import Enum
from tenacity import retry, stop_after_attempt, wait_exponential


class CircuitState(Enum):
    CLOSED = "closed"      # 正常
    OPEN = "open"          # 熔断(拒绝请求)
    HALF_OPEN = "half_open"  # 半开(试探)


class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 half_open_max: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max = half_open_max
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
        self._lock = asyncio.Lock()
    
    async def call(self, func, *args, **kwargs):
        """通过熔断器调用函数"""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_try_recover():
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise CircuitOpenError("熔断器开启,请求被拒绝")
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise
    
    def _should_try_recover(self) -> bool:
        if self.last_failure_time is None:
            return True
        return datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)
    
    async def _on_success(self):
        async with self._lock:
            self.failure_count = 0
            self.state = CircuitState.CLOSED
    
    async def _on_failure(self):
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN


# === 降级策略 ===
class AgentService:
    def __init__(self):
        self.llm_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
    
    async def chat(self, message: str) -> dict:
        """带熔断与降级的对话"""
        try:
            # 主路径:调用 LLM
            return await self.llm_breaker.call(self._call_llm, message)
        except CircuitOpenError:
            # 降级 1:返回缓存结果
            cached = await self._get_cached_response(message)
            if cached:
                return {"reply": cached, "degraded": True, "reason": "cache"}
            
            # 降级 2:返回预设回复
            return {
                "reply": "服务繁忙,请稍后重试",
                "degraded": True,
                "reason": "circuit_open"
            }
        except Exception as e:
            logger.error("chat_failed", error=str(e))
            return {"reply": "服务异常", "degraded": True, "reason": str(e)}
```

### 12.4 优雅关闭

```python
"""
优雅关闭:收到 SIGTERM 后,停止接收新请求,等待正在处理的请求完成
"""
import signal
import asyncio
from fastapi import FastAPI

app = FastAPI()
shutdown_event = asyncio.Event()


@app.on_event("shutdown")
async def graceful_shutdown():
    """应用关闭时的清理"""
    logger.info("开始优雅关闭...")
    
    # 1. 停止接收新任务
    shutdown_event.set()
    
    # 2. 等待进行中的请求完成(最多 30 秒)
    await asyncio.wait_for(
        _wait_pending_requests(),
        timeout=30
    )
    
    # 3. 释放资源
    await app.state.agent.shutdown()
    
    logger.info("优雅关闭完成")


# systemd 配置配合:
# KillSignal=SIGTERM
# TimeoutStopSec=30
```

### 12.5 多实例部署与水平扩展

```mermaid
graph TB
    subgraph 单实例部署
        LB1[Nginx] --> P1[Gunicorn<br/>4 workers]
    end
    
    subgraph 多实例水平扩展
        LB2[Nginx<br/>负载均衡] --> P2[实例1<br/>127.0.0.1:8001]
        LB2 --> P3[实例2<br/>127.0.0.1:8002]
        LB2 --> P4[实例3<br/>127.0.0.1:8003]
        
        P2 & P3 & P4 --> DB[(PostgreSQL<br/>共享)]
        P2 & P3 & P4 --> RD[(Redis<br/>共享)]
    end

    style LB2 fill:#d4edda,stroke:#155724,stroke-width:2px
    style DB fill:#d1ecf1,stroke:#0c5460
```

> **关键**:多实例部署时,**会话状态必须存共享存储**(Redis/DB),不能存进程内存,否则不同实例间状态不一致。

### 12.6 蓝绿部署与灰度发布

```mermaid
flowchart LR
    subgraph 蓝绿部署
        B[蓝组<br/>当前版本 v1] --> LB[负载均衡]
        G[绿组<br/>新版本 v2]
        
        LB -->|100%| B
        
        B -.切换.-> G
        LB -.切换后.-> G
    end

    style LB fill:#fff3cd,stroke:#d39e00,stroke-width:2px
```

```bash
# 蓝绿部署脚本示例
# 1. 部署新版本到绿组
sudo systemctl start agent-green

# 2. 验证绿组健康
curl -s http://127.0.0.1:8001/api/v1/health

# 3. 切换 Nginx 上游(灰度:先 10%)
# 修改 nginx.conf: 权重 green=1, blue=9
sudo nginx -s reload

# 4. 观察 10 分钟无异常后全量切换
# 修改 nginx.conf: 仅 green
sudo nginx -s reload

# 5. 停止蓝组
sudo systemctl stop agent-blue
```

---

## 十三、常见问题与最佳实践

### 13.1 常见部署问题

| # | 问题 | 原因 | 解决方案 |
|---|------|------|---------|
| 1 | `ModuleNotFoundError` | 虚拟环境未激活 | `source venv/bin/activate` |
| 2 | `Permission denied` | 文件权限不足 | `chown agent:agent` |
| 3 | `Address already in use` | 端口被占 | `lsof -i:8000` 查杀 |
| 4 | LLM 调用超时 | 网络/API Key | 检查 `OPENAI_API_KEY` 与网络 |
| 5 | worker 频繁重启 | `max-requests` 过小 | 调大至 1000+ |
| 6 | 内存持续增长 | 代码内存泄漏 | 用 `tracemalloc` 排查 |
| 7 | 日志不输出 | 日志路径无权限 | 检查 `logs/` 目录权限 |
| 8 | systemd 启动失败 | `.env` 文件格式 | 检查 `EnvironmentFile` 格式 |
| 9 | Nginx 502 | Gunicorn 未启/端口错 | 检查 upstream 与 gunicorn bind |
| 10 | CPU 100% | worker 过多或死循环 | 减少 worker 或排查死循环 |

### 13.2 故障排查流程

```mermaid
flowchart TB
    F[服务异常] --> S1{服务状态?}
    S1 -- inactive --> S2[检查 systemd 日志<br/>journalctl -u agent]
    S1 -- active 但 502 --> S3[检查 Gunicorn 端口<br/>ss -tlnp]
    S1 -- active 但 500 --> S4[检查应用日志<br/>app.log]
    
    S2 --> S5{配置错误?}
    S5 -- 是 --> S6[修复配置<br/>systemctl daemon-reload]
    S5 -- 否 --> S7[检查依赖/权限]
    
    S3 --> S8{端口监听?}
    S8 -- 否 --> S9[重启 Gunicorn]
    S8 -- 是 --> S10[检查 Nginx upstream]
    
    S4 --> S11{错误类型?}
    S11 -- DB 连接 --> S12[检查 PostgreSQL]
    S11 -- LLM 调用 --> S13[检查 API Key/网络]
    S11 -- 代码异常 --> S14[修复代码]

    style F fill:#f8d7da,stroke:#721c24
    style S6 fill:#d4edda,stroke:#155724
    style S9 fill:#d4edda,stroke:#155724
```

### 13.3 生产环境最佳实践(Do's)

| # | 实践 | 说明 |
|---|------|------|
| ✅1 | **强制使用虚拟环境** | 每个项目独立 venv,避免依赖污染 |
| ✅2 | **依赖锁版本** | requirements.txt 用 `==`,不用 `>=` |
| ✅3 | **专用低权限用户** | 禁止 root 运行 Python 服务 |
| ✅4 | **systemd 管理进程** | 生产首选,自动重启+资源限制 |
| ✅5 | **Nginx 反向代理** | SSL 终结+负载均衡+限流 |
| ✅6 | **健康检查接口** | /health 与 /health/ready 双接口 |
| ✅7 | **结构化日志** | JSON 格式,便于日志聚合 |
| ✅8 | **Prometheus 监控** | 关键指标暴露 + Grafana 告警 |
| ✅9 | **max-requests 防泄漏** | worker 定期重启回收内存 |
| ✅10 | **优雅关闭** | SIGTERM + 等待请求完成 |
| ✅11 | **配置分层** | 默认 + 环境覆盖 + 环境变量 |
| ✅12 | **蓝绿部署** | 零停机发布,快速回滚 |

### 13.4 常见踩坑(Don'ts)

| # | 踩坑 | 后果 | 避坑 |
|---|------|------|------|
| ❌1 | **用 root 跑服务** | 安全风险 | 创建专用用户 |
| ❌2 | **不用虚拟环境** | 依赖冲突 | 强制 venv |
| ❌3 | **依赖不锁版本** | 部署不可复现 | 用 `==` 锁定 |
| ❌4 | **单 worker 部署** | 无法利用多核 | workers = CPU×2+1 |
| ❌5 | **timeout 过短** | LLM 调用被杀 | 设 180s+ |
| ❌6 | **无健康检查** | 僵尸服务不重启 | 配置 HEALTHCHECK |
| ❌7 | **日志写本地不轮转** | 磁盘打满 | RotatingFileHandler |
| ❌8 | **会话存内存** | 多实例不一致 | 存 Redis/DB |
| ❌9 | **无熔断降级** | LLM 故障拖垮全站 | 加 CircuitBreaker |
| ❌10 | **直接暴露 Gunicorn** | 无 SSL 无防护 | 必须 Nginx 反代 |

### 13.5 性能调优清单

```mermaid
mindmap
  root((性能调优))
    Gunicorn
      workers 数量
      worker-class 选择
      max-requests 防泄漏
      keepalive 复用连接
    Uvicorn
      异步 IO
      事件循环 uvloop
      http 协议 httptools
    数据层
      连接池大小
      异步驱动 asyncpg
      Redis 连接池
      查询优化
    LLM 调用
      流式响应
      请求批处理
      结果缓存
      超时与重试
    缓存
      多级缓存
      LRU 策略
      TTL 过期
```

---

## 十四、完整部署脚本与总结

### 14.1 一键部署脚本

#### `scripts/deploy.sh`

```bash
#!/bin/bash
# ============================================
# Python Agent 服务一键部署脚本
# 使用: ./deploy.sh [version]
# ============================================

set -euo pipefail

# === 配置 ===
APP_NAME="agent-service"
APP_DIR="/opt/agent/app"
VENV_DIR="/opt/agent/venv"
LOG_DIR="/opt/agent/logs"
CONFIG_DIR="/opt/agent/config"
SERVICE_FILE="/etc/systemd/system/agent.service"
NGINX_CONF="/etc/nginx/sites-available/agent"
PYTHON_VERSION="3.11"
VERSION="${1:-latest}"

echo "========================================"
echo "  Python Agent 服务部署 v$VERSION"
echo "========================================"

# === 1. 系统依赖检查与安装 ===
echo "[1/10] 检查系统依赖..."
if ! command -v python3.11 &> /dev/null; then
    echo "  安装 Python 3.11..."
    sudo apt update
    sudo apt install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install -y python3.11 python3.11-venv python3.11-dev
fi
echo "  ✓ Python $(python3.11 --version)"

# === 2. 创建用户与目录 ===
echo "[2/10] 创建用户与目录..."
if ! id "agent" &>/dev/null; then
    sudo groupadd -r agent
    sudo useradd -r -g agent -d /opt/agent -s /bin/bash -m agent
fi
sudo mkdir -p "$APP_DIR" "$VENV_DIR" "$LOG_DIR" "$CONFIG_DIR" "$LOG_DIR"
sudo chown -R agent:agent /opt/agent
echo "  ✓ 用户与目录就绪"

# === 3. 创建虚拟环境 ===
echo "[3/10] 创建虚拟环境..."
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    sudo -u agent python3.11 -m venv "$VENV_DIR"
    sudo -u agent "$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel
fi
echo "  ✓ 虚拟环境就绪"

# === 4. 部署代码 ===
echo "[4/10] 部署代码..."
# 此处假设代码已在 $APP_DIR(通过 git pull 或 rsync 同步)
if [ ! -f "$APP_DIR/app/main.py" ]; then
    echo "  [ERROR] 未找到应用代码: $APP_DIR/app/main.py"
    exit 1
fi
echo "  ✓ 代码就绪"

# === 5. 安装依赖 ===
echo "[5/10] 安装依赖..."
sudo -u agent "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements-prod.txt"
echo "  ✓ 依赖安装完成"

# === 6. 配置文件检查 ===
echo "[6/10] 检查配置文件..."
if [ ! -f "$APP_DIR/.env" ]; then
    echo "  [WARN] .env 文件不存在,请参考 .env.example 创建"
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    echo "  [INFO] 已从模板创建 .env,请编辑填入实际值"
    sudo chown agent:agent "$APP_DIR/.env"
    sudo chmod 600 "$APP_DIR/.env"
fi
echo "  ✓ 配置文件就绪"

# === 7. systemd 服务配置 ===
echo "[7/10] 配置 systemd 服务..."
cat > /tmp/agent.service << 'SYSTEMD_EOF'
[Unit]
Description=Python Agent Service
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
User=agent
Group=agent
WorkingDirectory=/opt/agent/app
Environment="APP_ENV=production"
Environment="PYTHONPATH=/opt/agent/app"
EnvironmentFile=/opt/agent/app/.env
Environment="PATH=/opt/agent/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/opt/agent/venv/bin/gunicorn app.main:app --bind 127.0.0.1:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker --timeout 180 --max-requests 1000 --max-requests-jitter 50 --access-logfile /opt/agent/logs/access.log --error-logfile /opt/agent/logs/gunicorn-error.log --log-level info
Restart=always
RestartSec=5
LimitNOFILE=65536
MemoryMax=2G
CPUQuota=300%
KillSignal=SIGTERM
TimeoutStopSec=30
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/opt/agent/logs /opt/agent/data

[Install]
WantedBy=multi-user.target
SYSTEMD_EOF

sudo mv /tmp/agent.service "$SERVICE_FILE"
sudo chown root:root "$SERVICE_FILE"
sudo systemctl daemon-reload
sudo systemctl enable agent
echo "  ✓ systemd 服务配置完成"

# === 8. 启动服务 ===
echo "[8/10] 启动服务..."
sudo systemctl restart agent
sleep 3

if sudo systemctl is-active --quiet agent; then
    echo "  ✓ 服务已启动"
else
    echo "  [ERROR] 服务启动失败"
    sudo journalctl -u agent --since "1 minute ago" --no-pager
    exit 1
fi

# === 9. 健康检查 ===
echo "[9/10] 健康检查..."
for i in $(seq 1 10); do
    if curl -sf http://127.0.0.1:8000/api/v1/health > /dev/null 2>&1; then
        echo "  ✓ 健康检查通过"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "  [ERROR] 健康检查失败"
        exit 1
    fi
    sleep 2
done

# === 10. 部署完成 ===
echo "[10/10] 部署完成!"
echo ""
echo "========================================"
echo "  部署成功!"
echo "========================================"
echo ""
echo "服务状态: sudo systemctl status agent"
echo "实时日志: sudo journalctl -u agent -f"
echo "应用日志: tail -f $LOG_DIR/app.log"
echo "API 文档: http://localhost:8000/docs"
echo "健康检查: curl http://localhost:8000/api/v1/health"
echo ""
echo "如需配置 Nginx 反向代理,请参考文档第八节。"
```

```bash
# 赋予执行权限并运行
chmod +x scripts/deploy.sh
sudo ./scripts/deploy.sh 1.0.0
```

### 14.2 部署架构总览回顾

```mermaid
graph TB
    subgraph 完整生产部署架构
        CLIENT[客户端] --> FW[防火墙]
        FW --> NGINX[Nginx 443<br/>SSL/限流/LB]
        NGINX --> G1[Gunicorn Master<br/>实例1]
        NGINX --> G2[Gunicorn Master<br/>实例2]
        
        G1 --> W1[Uvicorn Worker ×4]
        G2 --> W2[Uvicorn Worker ×4]
        
        W1 & W2 --> APP[FastAPI App<br/>Agent 逻辑]
        
        APP --> DB[(PostgreSQL<br/>会话/消息)]
        APP --> RD[(Redis<br/>缓存/队列)]
        APP --> VDB[(Qdrant<br/>向量检索)]
        APP --> LLM[OpenAI API<br/>LLM 调用]
        
        SYSTEMD[systemd] -.管理.-> G1 & G2
        
        APP -.日志.-> LOG[日志文件<br/>+ journald]
        APP -.指标.-> PROM[Prometheus]
        PROM --> GRAF[Grafana 监控]
        
        APP -.错误.-> SENTRY[Sentry]
    end

    style NGINX fill:#fff3cd,stroke:#d39e00,stroke-width:2px
    style SYSTEMD fill:#d1ecf1,stroke:#0c5460,stroke-width:2px
    style APP fill:#d4edda,stroke:#155724,stroke-width:2px
```

### 14.3 部署检查清单(生产上线前)

| # | 检查项 | 命令 | ✓ |
|---|--------|------|---|
| 1 | Python 版本 | `python3.11 --version` | ☐ |
| 2 | 虚拟环境激活 | `which python` | ☐ |
| 3 | 依赖已安装 | `pip list \| grep fastapi` | ☐ |
| 4 | .env 配置 | `cat .env \| grep KEY` | ☐ |
| 5 | 文件权限 | `ls -la .env` (600) | ☐ |
| 6 | 专用用户 | `id agent` | ☐ |
| 7 | systemd 服务 | `systemctl status agent` | ☐ |
| 8 | 开机自启 | `systemctl is-enabled agent` | ☐ |
| 9 | 端口监听 | `ss -tlnp \| grep 8000` | ☐ |
| 10 | 健康检查 | `curl /health` | ☐ |
| 11 | 就绪检查 | `curl /health/ready` | ☐ |
| 12 | Nginx 配置 | `nginx -t` | ☐ |
| 13 | SSL 证书 | `openssl s_client` | ☐ |
| 14 | 日志输出 | `tail -f app.log` | ☐ |
| 15 | 监控接入 | `curl /metrics` | ☐ |
| 16 | 备份配置 | 数据库备份脚本 | ☐ |
| 17 | 回滚方案 | 旧版本保留 | ☐ |
| 18 | 文档更新 | 运维手册 | ☐ |

---

> **文档结语**:本文系统阐述了 Python Agent 服务从零到生产的完整部署流程,涵盖**环境配置、依赖管理、项目结构、配置文件、服务启动、进程管理(systemd/Supervisor)、反向代理(Nginx)、日志监控、部署验证、容器化(Docker)、稳定性保障、最佳实践**十二大维度。**核心部署哲学**是"**虚拟环境隔离依赖,systemd 管理进程,Gunicorn+Uvicorn 运行应用,Nginx 反向代理,多级监控保障稳定**"。
>
> **与 Java 部署的关键差异**:Java 开发者需特别注意——Python 没有"开箱即用"的应用服务器(Tomcat),需要 **Gunicorn(进程管理)+ Uvicorn(ASGI 服务器)** 的组合替代;Python 对版本与依赖隔离更敏感,**虚拟环境是强制要求**;Python 的内存管理不如 JVM 精细,需要 **max-requests 定期重启 worker** 防泄漏。
>
> **后续演进方向**:① 探索 Kubernetes 编排部署,实现自动扩缩容;② 引入服务网格(Istio)管理多实例通信;③ 集成 OpenTelemetry 实现分布式追踪;④ 探索 Serverless 部署(适用于低频调用场景)。
>
> **相关阅读**:[151为什么Agent开发选择Python语言.md](./151为什么Agent开发选择Python语言.md) 解释了"为何选 Python",本文则回答了"如何部署 Python Agent"——两文搭配,完成 Python Agent 开发部署的完整闭环。
