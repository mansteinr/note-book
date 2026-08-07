# Python FastAPI 框架搭建功能完整的 Agent 服务

> **文档定位**:本文档是「Java-Python Agent 开发」系列的第三篇核心文档,基于 [151号文档](./151为什么Agent开发选择Python语言.md) 说明的Python语言优势和 [152号文档](./152Python-Agent服务部署完整指南.md) 的部署指南,提供一套**完整、可运行、生产级**的FastAPI Agent服务实现方案,包含项目结构、依赖管理、核心模块、API设计、错误处理、Java交互、测试验证和部署配置。
>
> **与系列文档的关系**:151号文档回答「为什么选Python」,152号文档回答「如何部署」,本文档回答「如何从零搭建」,三者构成「选型→实现→部署」的完整链路。
>
> **关键设计原则**:
> - **配置外置**:端口/密钥/URL全部走环境变量,不硬编码(参考经验ID:551121)
> - **默认值友好**:可选组件提供默认值,不因可选依赖缺失导致服务无法启动(经验ID:551121)
> - **类型安全**:全程Pydantic模型+类型注解,启用FastAPI自动校验
> - **分层架构**:API层→Service层→Agent层→基础设施层,解耦便于测试
> - **安全第一**:密钥/口令使用占位符,不写入真实敏感信息(经验ID:551121)

---

## 目录

- [一、项目结构设计](#一项目结构设计)
- [二、依赖包安装与环境配置](#二依赖包安装与环境配置)
- [三、配置层设计(Pydantic Settings)](#三配置层设计pydantic-settings)
- [四、核心功能模块:数据模型](#四核心功能模块数据模型)
  - [4.1 请求与响应模型](#41-请求与响应模型)
  - [4.2 Agent 内部状态模型](#42-agent-内部状态模型)
- [五、核心功能模块:Agent 逻辑实现](#五核心功能模块agent-逻辑实现)
  - [5.1 基类与接口定义](#51-基类与接口定义)
  - [5.2 ReAct Agent 实现](#52-react-agent-实现)
  - [5.3 工具注册与调用](#53-工具注册与调用)
- [六、核心功能模块:Service 业务层](#六核心功能模块service-业务层)
  - [6.1 AgentService 编排器](#61-agentservice-编排器)
  - [6.2 SessionService 会话管理](#62-sessionservice-会话管理)
- [七、API 接口定义(路由层)](#七api-接口定义路由层)
  - [7.1 健康检查接口](#71-健康检查接口)
  - [7.2 聊天接口(同步+流式)](#72-聊天接口同步流式)
  - [7.3 会话管理接口](#73-会话管理接口)
  - [7.4 工具管理接口](#74-工具管理接口)
- [八、错误处理机制](#八错误处理机制)
  - [8.1 自定义异常体系](#81-自定义异常体系)
  - [8.2 全局异常处理器](#82-全局异常处理器)
  - [8.3 请求参数校验错误](#83-请求参数校验错误)
- [九、与 Java 组件交互方案](#九与-java-组件交互方案)
  - [9.1 HTTP REST 调用](#91-http-rest-调用)
  - [9.2 gRPC 高性能调用](#92-grpc-高性能调用)
  - [9.3 消息队列解耦(Kafka/RabbitMQ)](#93-消息队列解耦kafkarabbitmq)
- [十、单元测试编写](#十单元测试编写)
  - [10.1 测试框架与依赖](#101-测试框架与依赖)
  - [10.2 核心模块测试用例](#102-核心模块测试用例)
  - [10.3 API 接口测试用例](#103-api-接口测试用例)
- [十一、服务部署配置](#十一服务部署配置)
  - [11.1 Uvicorn/Gunicorn 生产级启动](#111-uvicorngunicorn-生产级启动)
  - [11.2 Docker 容器化部署](#112-docker-容器化部署)
  - [11.3 Nginx 反向代理配置](#113-nginx-反向代理配置)
  - [11.4 日志与监控配置](#114-日志与监控配置)
- [十二、服务启动与测试命令](#十二服务启动与测试命令)
  - [12.1 本地开发启动](#121-本地开发启动)
  - [12.2 单元测试执行](#122-单元测试执行)
  - [12.3 API 手动测试(curl)](#123-api-手动测试curl)
  - [12.4 API 文档访问](#124-api-文档访问)
- [十三、FastAPI 最佳实践清单](#十三fastapi-最佳实践清单)
- [十四、总结](#十四总结)

---

## 一、项目结构设计

遵循 **FastAPI 分层架构 + 领域驱动设计(DDD)** 最佳实践,按职责清晰划分模块,便于测试和扩展。

```
agent_service/                              # 项目根目录
├── app/                                     # 应用主目录
│   ├── __init__.py
│   ├── main.py                              # [入口] FastAPI应用工厂,注册路由和中间件
│   │
│   ├── core/                                # [配置层] 全局配置、日志、安全
│   │   ├── __init__.py
│   │   ├── config.py                        # Pydantic Settings,从环境变量加载所有配置
│   │   ├── logging.py                       # 结构化日志配置(JSON+控制台)
│   │   ├── exceptions.py                    # 自定义异常体系
│   │   ├── handlers.py                      # 全局异常处理器
│   │   └── security.py                      # API Key / JWT 鉴权
│   │
│   ├── models/                              # [数据模型层] Pydantic + 内部状态
│   │   ├── __init__.py
│   │   ├── schemas.py                       # 请求/响应模型(DTO)
│   │   └── agent_state.py                   # Agent运行时状态模型
│   │
│   ├── agent/                               # [Agent层] 核心推理逻辑
│   │   ├── __init__.py
│   │   ├── base.py                          # Agent抽象基类
│   │   ├── react_agent.py                   # ReAct模式Agent实现
│   │   ├── llm_client.py                    # LLM调用封装(OpenAI/Ollama/Deepseek)
│   │   ├── memory.py                        # 短期记忆/会话上下文管理
│   │   └── tools/                           # 工具注册表
│   │       ├── __init__.py
│   │       ├── registry.py                  # 工具注册中心
│   │       ├── calculator.py                # 示例:计算器工具
│   │       └── web_search.py                # 示例:搜索工具
│   │
│   ├── services/                            # [Service层] 业务编排
│   │   ├── __init__.py
│   │   ├── agent_service.py                 # Agent流程编排
│   │   ├── session_service.py               # 会话生命周期管理
│   │   └── java_bridge.py                   # Java组件交互桥接
│   │
│   ├── api/                                 # [API层] 路由 + 依赖注入
│   │   ├── __init__.py
│   │   ├── deps.py                          # 依赖注入(DB/Service/Auth)
│   │   ├── health.py                        # /health 健康检查
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py                      # /api/v1/chat 聊天接口
│   │   │   ├── session.py                   # /api/v1/sessions 会话管理
│   │   │   └── tools.py                     # /api/v1/tools 工具管理
│   │
│   ├── integrations/                        # [基础设施层] 外部系统集成
│   │   ├── __init__.py
│   │   ├── http_client.py                   # 统一HTTP客户端(带重试+超时)
│   │   ├── grpc_client.py                   # gRPC客户端骨架
│   │   └── mq_client.py                     # Kafka/RabbitMQ客户端骨架
│   │
│   └── tests/                               # 测试目录
│       ├── __init__.py
│       ├── conftest.py                      # pytest fixture & TestClient
│       ├── unit/
│       │   ├── test_react_agent.py          # Agent逻辑单元测试
│       │   ├── test_tools.py                # 工具调用测试
│       │   └── test_session_service.py      # Service层测试
│       └── api/
│           ├── test_health.py               # 健康检查API测试
│           ├── test_chat.py                 # 聊天API测试
│           └── test_session.py              # 会话API测试
│
├── config/                                  # 配置文件目录
│   ├── .env.example                         # 环境变量模板(仅占位符,无真实密钥)
│   ├── logging.json                         # 日志配置JSON
│   └── nginx.conf                           # Nginx反向代理模板
│
├── scripts/                                 # 运维脚本
│   ├── start_dev.sh                         # 开发启动(.bat/windows版需另写)
│   ├── start_prod.sh                        # 生产启动
│   └── run_tests.sh                         # 测试执行脚本
│
├── requirements.txt                         # 依赖清单(分层)
├── requirements-dev.txt                     # 开发依赖(测试/格式化)
├── Dockerfile                               # 多阶段构建Dockerfile
├── docker-compose.yml                       # 本地三剑客:agent+redis+ollama
├── pytest.ini                               # pytest配置
└── README.md                                # 项目说明
```

**结构设计原则**:

| 层级 | 目录 | 职责 | 依赖方向 |
|------|------|------|---------|
| API层 | `app/api/` | 路由定义、参数校验、鉴权、响应序列化 | 仅依赖Service层 |
| Service层 | `app/services/` | 业务流程编排、跨模块协调、事务边界 | 依赖Agent层+Infrastructure层 |
| Agent层 | `app/agent/` | 推理决策、LLM调用、记忆、工具调用 | 仅依赖models层+配置层 |
| 模型层 | `app/models/` | Pydantic DTO、状态数据结构 | 无业务依赖 |
| 配置层 | `app/core/` | Settings、日志、异常、安全 | 最底层,零业务依赖 |
| 基础设施 | `app/integrations/` | HTTP/gRPC/MQ外部客户端 | 依赖配置层 |

> **依赖箭头永远朝上**:API → Service → Agent → Models,任何层都可以依赖配置层和基础设施层,但**不能反向依赖**。

---

## 二、依赖包安装与环境配置

### 2.1 依赖分层清单

按「核心必选 + 功能可选 + 开发专用」分层管理,最小化生产镜像体积。

**`requirements.txt`(生产依赖)**:

```
# ========== FastAPI 核心 ==========
fastapi>=0.115.0,<0.116.0           # Web框架本体
uvicorn[standard]>=0.30.0,<0.31.0  # ASGI服务器(生产级worker)
pydantic>=2.9.0,<2.10.0             # 数据校验+类型注解
pydantic-settings>=2.5.0,<2.6.0     # 环境变量配置加载
python-dotenv>=1.0.0,<2.0.0         # .env文件加载

# ========== LLM & Agent ==========
httpx>=0.27.0,<0.28.0               # 异步HTTP客户端(调用LLM和Java)
tenacity>=8.5.0,<9.0.0              # 重试装饰器(LLM失败自动重试)
langchain-core>=0.3.0,<0.4.0        # 可选:轻量Agent框架(如需RAG/复杂链)

# ========== 基础设施 ==========
redis>=5.0.0,<6.0.0                 # 可选:会话/缓存存储(默认本地内存兜底)
orjson>=3.10.0,<4.0.0               # 高性能JSON序列化
```

**`requirements-dev.txt`(开发依赖)**:

```
-r requirements.txt                 # 先继承生产依赖

# 测试
pytest>=8.3.0,<9.0.0
pytest-asyncio>=0.24.0,<0.25.0      # 异步代码测试
pytest-cov>=5.0.0,<6.0.0            # 覆盖率
httpx>=0.27.0                       # TestClient的依赖

# 代码质量
ruff>=0.6.0,<0.7.0                  # lint + formatter一体化(替代flake8+black)
mypy>=1.11.0,<1.12.0                # 静态类型检查
```

### 2.2 安装命令(Windows + Linux/Mac通用)

```bash
# 1. 创建虚拟环境(推荐,避免污染系统Python)
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux/Mac Bash
python3 -m venv .venv
source .venv/bin/activate

# 2. 升级pip
python -m pip install --upgrade pip

# 3. 安装生产依赖
pip install -r requirements.txt

# 4. 开发时额外安装开发+测试依赖
pip install -r requirements-dev.txt
```

### 2.3 `.env.example` 配置模板(仅占位符,无真实密钥)

遵循经验ID:551121的教训——**端口、密钥、URL全部配置化,必填字段仅LLM API,其余均有默认值,不因可选组件缺失导致服务崩溃**。

```dotenv
# config/.env.example —— 复制为 config/.env 后填入真实值
# ========== 服务基础配置(端口不要写死,从环境变量读) ==========
APP_NAME="FastAPI Agent Service"
APP_ENV=dev                          # dev/staging/prod
HOST=0.0.0.0
PORT=8000                            # 参考经验:不要硬编码8000或8002,统一在这里
DEBUG=true
LOG_LEVEL=INFO

# ========== LLM 配置(唯一必填项,否则Agent无法推理) ==========
LLM_PROVIDER=ollama                  # ollama | openai | deepseek | custom_openai
LLM_API_KEY=REPLACE_WITH_YOUR_KEY    # ⚠️ 用你的真实key替换,不要提交到git
LLM_BASE_URL=http://localhost:11434  # Ollama本地默认;OpenAI用 https://api.openai.com/v1
LLM_MODEL_NAME=qwen2.5:7b            # 根据provider调整

# ========== 可选:Redis缓存和会话存储(不填则降级为进程内内存) ==========
REDIS_URL=                           # 例: redis://localhost:6379/0; 留空=禁用Redis
REDIS_PASSWORD=
SESSION_TTL_SECONDS=86400            # 会话默认1天过期

# ========== 可选:Java服务桥接(不填则不启用) ==========
JAVA_BACKEND_BASE_URL=               # 例: http://java-service:8080; 留空=不桥接
JAVA_BACKEND_TIMEOUT_MS=10000
JAVA_BACKEND_API_KEY=                # 若Java侧需要鉴权

# ========== 可选:消息队列(流式异步场景,留空=不启用) ==========
KAFKA_BOOTSTRAP_SERVERS=             # 例: kafka:9092
KAFKA_TOPIC_AGENT_EVENTS=agent.events

# ========== 安全 ==========
API_KEY_HEADER_NAME=X-API-Key
API_KEYS=                            # 逗号分隔,留空=不开启鉴权(开发友好)
```

> **Windows 端口冲突提示(经验ID:551121)**:如果启动时报 `WinError 10013`,先查端口占用:`netstat -ano | findstr :8000`,找到PID后 `taskkill /F /PID <PID>`,或修改 `PORT` 环境变量换端口。

---

## 三、配置层设计(Pydantic Settings)

核心原则(经验ID:551121):
1. **所有可变项走环境变量**,代码中不写死任何端口/URL/密钥
2. **可选组件给默认值或Optional**,Redis/Java桥接不配置时自动降级,**绝不因为可选组件缺失导致API启动失败**
3. **Settings支持向上搜索`.env`**,默认路径可覆盖

**文件路径**: `app/core/config.py`

```python
"""全局配置: 基于pydantic-settings, 自动从环境变量加载

设计要点(经验ID:551121):
- LLM配置是唯一真正必填的(否则Agent无推理能力)
- Redis、Java桥接、Kafka都是 Optional, 未配置时用进程内存/空实现
- 端口/host/debug/log_level 均有生产安全默认值, 但可被.env覆盖
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal, Optional

from pydantic import AnyHttpUrl, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 允许显式指定.env路径;向上搜索到项目根
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ENV_PATH = PROJECT_ROOT / "config" / ".env"


class Settings(BaseSettings):
    """全局应用配置, 所有字段均可通过环境变量覆盖"""

    model_config = SettingsConfigDict(
        env_file=str(DEFAULT_ENV_PATH),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ===== 基础服务 =====
    APP_NAME: Annotated[str, Field(default="FastAPI Agent Service")]
    APP_ENV: Annotated[Literal["dev", "staging", "prod"], Field(default="dev")]
    HOST: Annotated[str, Field(default="0.0.0.0")]
    PORT: Annotated[int, Field(default=8000, ge=1, le=65535)]
    DEBUG: Annotated[bool, Field(default=False)]
    LOG_LEVEL: Annotated[Literal["DEBUG", "INFO", "WARNING", "ERROR"], Field(default="INFO")]

    CORS_ORIGINS: Annotated[list[str], Field(default_factory=lambda: ["*"])]

    # ===== LLM(唯一必填) =====
    LLM_PROVIDER: Annotated[Literal["ollama", "openai", "deepseek", "custom_openai"], Field(default="ollama")]
    LLM_API_KEY: Annotated[SecretStr, Field(default=SecretStr(""))]
    LLM_BASE_URL: Annotated[Optional[AnyHttpUrl], Field(default=None)]
    LLM_MODEL_NAME: Annotated[str, Field(default="qwen2.5:7b")]
    LLM_TIMEOUT_MS: Annotated[int, Field(default=60_000)]
    LLM_TEMPERATURE: Annotated[float, Field(default=0.0, ge=0.0, le=2.0)]
    LLM_MAX_TOKENS: Annotated[int, Field(default=2048)]

    # ===== 可选:Redis(留空=进程内内存会话/缓存) =====
    REDIS_URL: Annotated[Optional[str], Field(default=None)]
    REDIS_PASSWORD: Annotated[SecretStr, Field(default=SecretStr(""))]
    SESSION_TTL_SECONDS: Annotated[int, Field(default=24 * 3600)]

    # ===== 可选:Java后端桥接(留空=不启用) =====
    JAVA_BACKEND_BASE_URL: Annotated[Optional[AnyHttpUrl], Field(default=None)]
    JAVA_BACKEND_TIMEOUT_MS: Annotated[int, Field(default=10_000)]
    JAVA_BACKEND_API_KEY: Annotated[SecretStr, Field(default=SecretStr(""))]

    # ===== 可选:Kafka =====
    KAFKA_BOOTSTRAP_SERVERS: Annotated[Optional[str], Field(default=None)]
    KAFKA_TOPIC_AGENT_EVENTS: Annotated[str, Field(default="agent.events")]

    # ===== 安全:API Key白名单(留空=不鉴权,仅开发用) =====
    API_KEY_HEADER_NAME: Annotated[str, Field(default="X-API-Key")]
    API_KEYS: Annotated[list[str], Field(default_factory=list)]

    @field_validator("API_KEYS", mode="before")
    @classmethod
    def _split_api_keys(cls, v):
        """支持逗号分隔的字符串或列表"""
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    # ===== 便捷属性 =====
    @property
    def is_dev(self) -> bool:
        return self.APP_ENV == "dev"

    @property
    def redis_enabled(self) -> bool:
        return bool(self.REDIS_URL)

    @property
    def java_bridge_enabled(self) -> bool:
        return self.JAVA_BACKEND_BASE_URL is not None

    @property
    def auth_enabled(self) -> bool:
        return len(self.API_KEYS) > 0


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """单例获取配置, 生产环境可热更新时去掉lru_cache"""
    return Settings()


if __name__ == "__main__":  # pragma: no cover - 开发时快速打印当前配置(脱敏)
    s = get_settings()
    print(f"✅ Config loaded. APP_ENV={s.APP_ENV}, PORT={s.PORT}")
    print(f"   LLM provider={s.LLM_PROVIDER}, model={s.LLM_MODEL_NAME}")
    print(f"   Redis={'enabled' if s.redis_enabled else 'disabled (in-memory)'}")
    print(f"   Java bridge={'enabled' if s.java_bridge_enabled else 'disabled'}")
    print(f"   API Key auth={'enabled' if s.auth_enabled else 'disabled'}")
```

---

## 四、核心功能模块:数据模型

### 4.1 请求与响应模型

使用Pydantic v2,所有模型启用严格模式,`ModelSignature` + 类型注解驱动FastAPI自动生成OpenAPI文档。

**文件路径**: `app/models/schemas.py`

```python
"""API请求/响应DTO (Data Transfer Object)

所有模型均使用Pydantic v2 strict模式, 提供:
- 自动字段校验(类型/range/enum)
- 自动生成OpenAPI Schema → 出现在/docs和/redoc
- 类型安全,拒绝未声明字段(extra=forbid)
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ========== 通用 ==========
class BaseSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",          # 拒绝请求中出现未声明的字段(安全)
        frozen=False,
        use_enum_values=True,
        json_schema_extra={"examples": []},
    )


class PaginationQuery(BaseSchema):
    page: int = Field(default=1, ge=1, description="页码,从1开始")
    page_size: int = Field(default=20, ge=1, le=100, description="每页条数,最大100")


class StandardResponse[T](BaseSchema):
    """统一响应包装: {code, message, data, trace_id}"""
    code: int = Field(default=0, description="业务码,0=成功,非0=失败")
    message: str = Field(default="ok", description="人类可读描述")
    data: Optional[T] = Field(default=None, description="业务数据")
    trace_id: Optional[str] = Field(default=None, description="请求追踪ID,便于排查")
    took_ms: Optional[int] = Field(default=None, description="服务端耗时(毫秒)")


# ========== 聊天相关 ==========
class ChatRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ChatMessage(BaseSchema):
    role: ChatRole = Field(..., description="消息角色")
    content: str = Field(..., min_length=1, max_length=200_000, description="消息内容")
    tool_call_id: Optional[str] = Field(default=None, description="工具调用ID(仅role=tool时使用)")
    created_at: Optional[datetime] = Field(default=None, description="消息时间,服务端自动填充")


class ChatRequest(BaseSchema):
    """POST /api/v1/chat 请求体"""
    session_id: Optional[str] = Field(
        default=None,
        pattern=r"^[a-zA-Z0-9_-]{1,64}$",
        description="会话ID,不传则服务端创建新会话",
    )
    message: str = Field(..., min_length=1, max_length=50_000, description="用户本轮消息")
    system_prompt: Optional[str] = Field(
        default=None,
        max_length=50_000,
        description="可选:自定义本次会话的系统提示词(只在会话首次生效)",
    )
    tools_whitelist: Optional[list[str]] = Field(
        default=None,
        description="可选:只允许Agent调用列表中的工具;None=全部已注册工具",
    )
    stream: bool = Field(
        default=False,
        description="是否流式响应(SSE),开启后响应为text/event-stream",
    )
    enable_java_bridge: bool = Field(
        default=False,
        description="是否允许Agent通过Java桥接调用Java侧能力(需配置JAVA_BACKEND_BASE_URL)",
    )


class ToolCallData(BaseSchema):
    tool_name: str
    arguments: dict[str, Any]
    result: Optional[Any] = None


class ChatResponse(BaseSchema):
    """非流式聊天响应"""
    session_id: str
    reply: str = Field(..., description="Agent最终回复")
    messages: list[ChatMessage] = Field(..., description="完整对话历史(含本次)")
    tool_calls: list[ToolCallData] = Field(default_factory=list, description="本次Agent调用过的工具")
    thinking_trace: list[str] = Field(default_factory=list, description="思考轨迹(ReAct中的Thought)")
    created_at: datetime


# ========== 会话管理 ==========
class SessionSummary(BaseSchema):
    session_id: str
    message_count: int
    first_message_at: datetime
    last_message_at: datetime
    last_user_preview: Optional[str] = None


class SessionListResponse(BaseSchema):
    items: list[SessionSummary]
    total: int
    page: int
    page_size: int


# ========== 工具管理 ==========
class ToolInfo(BaseSchema):
    name: str
    description: str
    input_schema: dict[str, Any]
    category: str = Field(default="general", description="工具分类标签")


# ========== 错误响应 ==========
class ErrorDetail(BaseSchema):
    code: str = Field(..., description="机器可读错误码,如 TOOL_NOT_FOUND")
    message: str = Field(..., description="人类可读错误信息")
    field: Optional[str] = Field(default=None, description="关联字段(参数校验错误时)")
    suggestion: Optional[str] = Field(default=None, description="修复建议")


class ErrorResponse(BaseSchema):
    code: int = Field(..., ge=400, description="HTTP状态码语义")
    error: ErrorDetail
    trace_id: Optional[str] = None
```

### 4.2 Agent 内部状态模型

**文件路径**: `app/models/agent_state.py`

```python
"""Agent运行时状态模型 —— 与API层DTO解耦, 只在Agent/Service层内部流通"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class AgentStep(str, Enum):
    THINK = "THINK"           # 推理
    ACTION = "ACTION"         # 选工具/参数
    OBSERVATION = "OBSERVATION"  # 工具结果观察
    FINAL_ANSWER = "FINAL_ANSWER"  # 结束


@dataclass
class ToolExecution:
    tool_name: str
    arguments: dict[str, Any]
    result: Any = None
    error: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None

    @property
    def success(self) -> bool:
        return self.error is None


@dataclass
class AgentRunState:
    """单次Agent执行的可变状态"""
    session_id: str
    user_input: str
    system_prompt: Optional[str]
    tools_whitelist: Optional[list[str]]
    enable_java_bridge: bool

    messages: list[dict] = field(default_factory=list)        # OpenAI格式消息
    tool_executions: list[ToolExecution] = field(default_factory=list)
    thinking_trace: list[str] = field(default_factory=list)

    current_step: AgentStep = AgentStep.THINK
    iterations: int = 0
    max_iterations: int = 10
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None
    final_answer: Optional[str] = None

    # 限制迭代次数,防止LLM进入死循环
    @property
    def should_continue(self) -> bool:
        return self.iterations < self.max_iterations and self.final_answer is None
```

---

## 五、核心功能模块:Agent 逻辑实现

### 5.1 基类与接口定义

**文件路径**: `app/agent/base.py`

```python
"""Agent抽象基类 —— 用依赖倒置原则, Service层只依赖抽象"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator

from app.models.agent_state import AgentRunState
from app.models.schemas import ToolCallData


class BaseAgent(ABC):
    @abstractmethod
    async def run(self, state: AgentRunState) -> str:
        """同步执行到结束, 返回最终回复字符串"""
        ...

    @abstractmethod
    async def run_stream(self, state: AgentRunState) -> AsyncIterator[str]:
        """流式执行, yield增量token字符串"""
        ...

    @abstractmethod
    def extract_tool_calls(self, state: AgentRunState) -> list[ToolCallData]:
        """从运行时状态中提取本轮执行的工具调用记录"""
        ...
```

**文件路径**: `app/agent/llm_client.py`

```python
"""LLM调用统一封装 —— 屏蔽Provider差异(OpenAI/Ollama/Deepseek)

设计要点:
- 失败自动重试(tenacity) —— LLM经常因为网络/限流临时失败
- Provider通过URL+兼容模式切换,不需要多套SDK
- 流式+非流式都支持
"""

from __future__ import annotations

from typing import AsyncIterator, Optional

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import Settings, get_settings


class LLMClient:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        base = (
            str(self.settings.LLM_BASE_URL).rstrip("/")
            if self.settings.LLM_BASE_URL
            else self._default_base_url()
        )
        self._base_url = base
        self._api_key = self.settings.LLM_API_KEY.get_secret_value()
        self._model = self.settings.LLM_MODEL_NAME
        self._timeout = httpx.Timeout(self.settings.LLM_TIMEOUT_MS / 1000.0)

    def _default_base_url(self) -> str:
        return {
            "ollama": "http://localhost:11434/v1",
            "openai": "https://api.openai.com/v1",
            "deepseek": "https://api.deepseek.com/v1",
            "custom_openai": "http://localhost:8080/v1",
        }.get(self.settings.LLM_PROVIDER, "http://localhost:11434/v1")

    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self._api_key:
            h["Authorization"] = f"Bearer {self._api_key}"
        return h

    # ===== 非流式 =====
    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=0.5, max=8),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TransportError, TimeoutError)),
    )
    async def chat_completion(self, messages: list[dict], **extra) -> str:
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": self.settings.LLM_TEMPERATURE,
            "max_tokens": self.settings.LLM_MAX_TOKENS,
            "stream": False,
            **extra,
        }
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.post(f"{self._base_url}/chat/completions",
                                  headers=self._headers(), json=payload)
            r.raise_for_status()
            data = r.json()

        # OpenAI兼容: choices可能为None(经验ID:1503562),需要兜底
        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError(f"LLM返回空choices,原始响应={data}")
        return choices[0]["message"].get("content") or ""

    # ===== 流式 =====
    async def chat_completion_stream(self, messages: list[dict], **extra) -> AsyncIterator[str]:
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": self.settings.LLM_TEMPERATURE,
            "max_tokens": self.settings.LLM_MAX_TOKENS,
            "stream": True,
            **extra,
        }
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            async with client.stream(
                "POST", f"{self._base_url}/chat/completions",
                headers=self._headers(), json=payload,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    line = line.strip()
                    if not line.startswith("data:"):
                        continue
                    chunk = line[len("data:"):].strip()
                    if chunk in ("", "[DONE]"):
                        continue
                    try:
                        import json as _json
                        obj = _json.loads(chunk)
                    except Exception:
                        continue
                    delta = (obj.get("choices") or [{}])[0].get("delta", {})
                    token = delta.get("content")
                    if token:
                        yield token
```

### 5.2 ReAct Agent 实现

**文件路径**: `app/agent/react_agent.py`

```python
"""ReAct模式Agent实现 —— Thought -> Action -> Observation 循环

经典ReAct论文: https://arxiv.org/abs/2210.03629
我们用结构化输出驱动工具调用, 不依赖Function Calling API, 从而兼容所有LLM。
"""

from __future__ import annotations

import json
import re
from typing import AsyncIterator
from uuid import uuid4

from app.agent.base import BaseAgent
from app.agent.llm_client import LLMClient
from app.agent.tools.registry import ToolRegistry
from app.core.config import Settings, get_settings
from app.core.exceptions import AgentExecutionError, ToolExecutionError
from app.models.agent_state import AgentRunState, AgentStep, ToolExecution
from app.models.schemas import ToolCallData


SYSTEM_PROMPT_TEMPLATE = """你是一个专业的Agent助手,采用ReAct方式解决用户问题。

**必须严格遵循以下格式,每行只能出现其中一种标签:**

```
Thought: <你在这一步的推理>
Action: {"tool": "<工具名>", "arguments": {<参数对象>}}
Observation: <工具返回的结果>
... (可以多次重复 Thought/Action/Observation) ...
Final Answer: <你给用户的最终回复>
```

**规则:**
1. 必须先 Thought, 再 Action(或直接 Final Answer)
2. Action 必须是合法JSON, tool 只能从 [{tool_names}] 中选
3. 遇到不会的问题,用工具查,不要编造
4. 工具结果在 Observation 标签里,不要篡改
5. 最终结论必须在 Final Answer 标签后给出,一次只能有一个 Final Answer

**工具清单:**
{tool_list}

{custom_system_prompt}
"""


class ReActAgent(BaseAgent):
    def __init__(
        self,
        llm: LLMClient | None = None,
        tools: ToolRegistry | None = None,
        settings: Settings | None = None,
    ):
        self.settings = settings or get_settings()
        self.llm = llm or LLMClient(self.settings)
        self.tools = tools or ToolRegistry.default()

    # ---------- 核心: 非流式 ----------
    async def run(self, state: AgentRunState) -> str:
        self._bootstrap(state)

        while state.should_continue:
            state.iterations += 1
            state.current_step = AgentStep.THINK

            prompt_messages = self._build_prompt_messages(state)
            try:
                raw = await self.llm.chat_completion(prompt_messages)
            except Exception as e:
                raise AgentExecutionError(f"LLM推理失败: {e}") from e

            state.thinking_trace.append(raw)
            state.messages.append({"role": "assistant", "content": raw})

            # 解析标签
            final_answer = _extract_tag(raw, "Final Answer")
            if final_answer:
                state.final_answer = final_answer.strip()
                state.current_step = AgentStep.FINAL_ANSWER
                state.finished_at = __import__("datetime").datetime.now()
                return state.final_answer

            action_json = _extract_tag(raw, "Action")
            if action_json:
                state.current_step = AgentStep.ACTION
                tool_result_text = await self._execute_tool(action_json, state)
                obs_message = f"Observation: {tool_result_text}"
                state.messages.append({"role": "user", "content": obs_message})
                # 继续循环 → 下一轮Thought
                continue

            # 既没有Final Answer也没有Action —— 格式错误,让LLM重做
            state.messages.append({
                "role": "user",
                "content": "请严格按照 Thought/Action/Final Answer 格式回答,缺少任一标签均不可。",
            })

        # 达到迭代上限
        return state.final_answer or (
            "抱歉,经过多轮推理仍未得到最终结论,请换一种方式提问或减少问题复杂度。"
        )

    # ---------- 流式(简化版,只流式Final Answer增量) ----------
    async def run_stream(self, state: AgentRunState) -> AsyncIterator[str]:
        final = await self.run(state)
        if final:
            for ch in final:
                yield ch

    # ---------- 工具调用提取 ----------
    def extract_tool_calls(self, state: AgentRunState) -> list[ToolCallData]:
        return [
            ToolCallData(
                tool_name=t.tool_name,
                arguments=t.arguments,
                result=t.result,
            )
            for t in state.tool_executions
        ]

    # ---------- 内部 ----------
    def _bootstrap(self, state: AgentRunState) -> None:
        """准备初始消息 + 系统提示词"""
        allowed = (
            self.tools.filtered(state.tools_whitelist)
            if state.tools_whitelist else self.tools.list_all()
        )
        tool_list_md = "\n".join(
            f"- `{t.name}`: {t.description}; 参数: {json.dumps(t.input_schema, ensure_ascii=False)}"
            for t in allowed
        )
        sys = SYSTEM_PROMPT_TEMPLATE.format(
            tool_names=",".join(t.name for t in allowed),
            tool_list=tool_list_md,
            custom_system_prompt=state.system_prompt or "",
        ).strip()
        bootstrap = [{"role": "system", "content": sys}]
        bootstrap.extend(state.messages)  # Service层传入的历史
        bootstrap.append({"role": "user", "content": state.user_input})
        state.messages = bootstrap

    def _build_prompt_messages(self, state: AgentRunState) -> list[dict]:
        # 防止Token爆炸:保留系统词+最近N轮(经验ID:55号文档Token优化)
        system = state.messages[0]
        recent = state.messages[1:][-20:]  # 最近20条
        return [system, *recent]

    async def _execute_tool(self, action_json_text: str, state: AgentRunState) -> str:
        try:
            payload = json.loads(action_json_text)
            tool_name = payload["tool"]
            arguments = payload["arguments"] if isinstance(payload["arguments"], dict) else json.loads(payload["arguments"])
        except Exception as e:
            return f"[Error] Action标签JSON解析失败: {e}, Action原文={action_json_text[:200]}"

        # 白名单检查
        if state.tools_whitelist and tool_name not in state.tools_whitelist:
            return f"[Error] 工具 {tool_name} 不在本次会话白名单中,已被拒绝调用。"

        # Java桥接工具前缀:java:<java方法名>
        if tool_name.startswith("java:") and state.enable_java_bridge:
            return await self._java_bridge(tool_name, arguments, state)

        execution = ToolExecution(tool_name=tool_name, arguments=arguments)
        try:
            result = await self.tools.call(tool_name, arguments)
            execution.result = result
        except ToolExecutionError as e:
            execution.error = str(e)
            result = f"[ToolError] {e}"
        except Exception as e:
            execution.error = f"未预期异常: {e}"
            result = f"[ToolFatal] {execution.error}"
        finally:
            from datetime import datetime
            execution.finished_at = datetime.now()
            state.tool_executions.append(execution)
        return str(result)

    async def _java_bridge(self, tool_name: str, arguments: dict, state: AgentRunState) -> str:
        from app.services.java_bridge import get_java_bridge
        bridge = get_java_bridge()
        method = tool_name.split(":", 1)[1]
        try:
            return await bridge.invoke(method, arguments) or ""
        except Exception as e:
            return f"[JavaBridgeError] 调用Java方法{method}失败: {e}"


# ========== 工具函数:从文本中提取标签 ==========
_TAG_RE = re.compile(r"^(?P<tag>Thought|Action|Observation|Final Answer)\s*:\s*(?P<body>.*?)(?=\n(?:Thought|Action|Observation|Final Answer)\s*:|\Z)", re.S | re.M)


def _extract_tag(text: str, tag_name: str) -> str | None:
    """找到指定标签最后一次出现的内容(LLM可能重复输出标签)"""
    matches = [m.group("body").strip() for m in _TAG_RE.finditer(text) if m.group("tag") == tag_name]
    return matches[-1] if matches else None
```

### 5.3 工具注册与调用

**文件路径**: `app/agent/tools/registry.py`

```python
"""工具注册中心 —— 集中式管理工具的元数据 + 实际调用"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Optional

from app.core.exceptions import ToolNotFoundError, ToolExecutionError


@dataclass
class ToolMeta:
    name: str
    description: str
    input_schema: dict[str, Any]
    category: str
    handler: Callable[[dict[str, Any]], Awaitable[Any]]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolMeta] = {}

    def register(
        self,
        name: str,
        handler: Callable[[dict[str, Any]], Awaitable[Any]],
        *,
        description: str,
        input_schema: dict[str, Any],
        category: str = "general",
    ) -> None:
        if not asyncio.iscoroutinefunction(handler):
            raise ValueError(f"工具{name}的handler必须是async函数")
        self._tools[name] = ToolMeta(
            name=name,
            description=description,
            input_schema=input_schema,
            category=category,
            handler=handler,
        )

    def list_all(self) -> list[ToolMeta]:
        return list(self._tools.values())

    def filtered(self, whitelist: list[str]) -> list[ToolMeta]:
        return [t for t in self._tools.values() if t.name in whitelist]

    def get(self, name: str) -> Optional[ToolMeta]:
        return self._tools.get(name)

    async def call(self, name: str, arguments: dict[str, Any]) -> Any:
        tool = self._tools.get(name)
        if not tool:
            raise ToolNotFoundError(f"工具 {name} 未注册,已注册工具: {list(self._tools)}")
        try:
            return await tool.handler(arguments)
        except ToolExecutionError:
            raise
        except Exception as e:
            raise ToolExecutionError(f"工具{name}执行异常: {e}") from e

    # ===== 默认注册的内置工具(示例) =====
    @classmethod
    def default(cls) -> "ToolRegistry":
        from app.agent.tools.calculator import calculator
        from app.agent.tools.web_search import web_search_mock

        r = cls()
        r.register(
            "calculator",
            calculator,
            description="计算数学表达式(仅支持加减乘除/括号),输入表达式字符串",
            input_schema={"type": "object", "properties": {"expression": {"type": "string"}}},
            category="math",
        )
        r.register(
            "web_search",
            web_search_mock,
            description="搜索网页(演示用Mock,返回固定示例)",
            input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
            category="search",
        )
        return r
```

**文件路径**: `app/agent/tools/calculator.py`

```python
"""示例工具: 安全计算器(禁止eval, 使用AST解析)"""

from __future__ import annotations

import ast
import operator

ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


async def calculator(args: dict) -> float | int:
    expr = str(args.get("expression", "")).strip()
    if not expr:
        raise ValueError("expression不能为空")
    if len(expr) > 200:
        raise ValueError("expression过长,拒绝执行")
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise ValueError(f"表达式语法错误: {e}") from e
    return _eval_node(tree.body)


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPS:
        return ALLOWED_OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPS:
        return ALLOWED_OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError(f"包含非法节点: {type(node).__name__}")
```

**文件路径**: `app/agent/tools/web_search.py`

```python
"""示例工具: Mock网页搜索 —— 生产可替换为SerpAPI/Bing/Vector检索"""

from __future__ import annotations


async def web_search_mock(args: dict) -> list[dict]:
    q = str(args.get("query", "")).strip() or ""
    return [
        {"title": f"「{q}」- 维基百科", "snippet": f"这是关于[{q}]的百科示例条目(演示数据)", "url": "https://example.com/a"},
        {"title": f"「{q}」- 官方文档", "snippet": f"文档中与[{q}]相关的章节摘要(演示数据)", "url": "https://example.com/b"},
    ]
```

---

## 六、核心功能模块:Service 业务层

### 6.1 AgentService 编排器

**文件路径**: `app/services/agent_service.py`

```python
"""Agent业务编排: 串联 Session + Agent + Tools + Memory

Service层不直接依赖FastAPI, 便于单元测试。
"""

from __future__ import annotations

from datetime import datetime
from typing import AsyncIterator
from uuid import uuid4

from app.agent.base import BaseAgent
from app.agent.react_agent import ReActAgent
from app.models.agent_state import AgentRunState
from app.models.schemas import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ChatRole,
)
from app.services.session_service import SessionService, get_session_service


class AgentService:
    def __init__(self, agent: BaseAgent | None = None, session_svc: SessionService | None = None):
        self.agent = agent or ReActAgent()
        self.session_svc = session_svc or get_session_service()

    async def chat(self, req: ChatRequest) -> ChatResponse:
        """同步聊天: 读历史 → 执行Agent → 写回会话"""
        session_id, history = await self._load_or_create_session(req)
        state = AgentRunState(
            session_id=session_id,
            user_input=req.message,
            system_prompt=req.system_prompt,
            tools_whitelist=req.tools_whitelist,
            enable_java_bridge=req.enable_java_bridge,
            messages=[m.model_dump(mode="json", exclude_none=True) for m in history],
        )

        reply = await self.agent.run(state)

        # 构造完整消息列表并持久化
        new_messages = [
            ChatMessage(role=ChatRole.USER, content=req.message, created_at=datetime.now()),
            ChatMessage(role=ChatRole.ASSISTANT, content=reply, created_at=datetime.now()),
        ]
        await self.session_svc.append_messages(session_id, new_messages)

        return ChatResponse(
            session_id=session_id,
            reply=reply,
            messages=(await self.session_svc.get_messages(session_id)),
            tool_calls=self.agent.extract_tool_calls(state),
            thinking_trace=state.thinking_trace,
            created_at=datetime.now(),
        )

    async def chat_stream(self, req: ChatRequest) -> tuple[str, AsyncIterator[str]]:
        """流式聊天"""
        session_id, history = await self._load_or_create_session(req)
        state = AgentRunState(
            session_id=session_id,
            user_input=req.message,
            system_prompt=req.system_prompt,
            tools_whitelist=req.tools_whitelist,
            enable_java_bridge=req.enable_java_bridge,
            messages=[m.model_dump(mode="json", exclude_none=True) for m in history],
        )
        stream = self.agent.run_stream(state)
        return session_id, stream

    async def _load_or_create_session(self, req: ChatRequest) -> tuple[str, list[ChatMessage]]:
        if req.session_id:
            history = await self.session_svc.get_messages(req.session_id)
            if not history and req.system_prompt:
                # 会话为空 + 指定了自定义system,直接写一条系统消息(可选)
                pass
            return req.session_id, history
        # 新建会话
        new_id = f"sess-{uuid4().hex[:12]}"
        return new_id, []


# 单例获取(配合FastAPI Depends)
_instance: AgentService | None = None

def get_agent_service() -> AgentService:
    global _instance
    if _instance is None:
        _instance = AgentService()
    return _instance
```

### 6.2 SessionService 会话管理

**文件路径**: `app/services/session_service.py`

```python
"""会话管理: 内存实现(默认) + Redis实现(配置REDIS_URL后自动切换)"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from app.core.config import Settings, get_settings
from app.models.schemas import ChatMessage


class SessionService:
    async def create(self, session_id: str) -> None: ...
    async def get_messages(self, session_id: str) -> list[ChatMessage]: ...
    async def append_messages(self, session_id: str, messages: list[ChatMessage]) -> None: ...
    async def list_sessions(self, page: int, page_size: int) -> tuple[list[dict], int]: ...
    async def delete(self, session_id: str) -> None: ...


# ========== 进程内内存实现(无依赖,默认兜底) ==========
class InMemorySessionService(SessionService):
    def __init__(self, ttl_seconds: int = 86400):
        from collections import OrderedDict
        self._store: OrderedDict[str, list[ChatMessage]] = OrderedDict()
        self._ttl = ttl_seconds

    async def create(self, session_id: str) -> None:
        if session_id not in self._store:
            self._store[session_id] = []

    async def get_messages(self, session_id: str) -> list[ChatMessage]:
        return list(self._store.get(session_id, []))

    async def append_messages(self, session_id: str, messages: list[ChatMessage]) -> None:
        self._store.setdefault(session_id, []).extend(messages)
        self._store.move_to_end(session_id)

    async def list_sessions(self, page: int, page_size: int) -> tuple[list[dict], int]:
        items = list(self._store.items())
        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        summaries = []
        for sid, msgs in items[start:end]:
            user_msgs = [m for m in msgs if m.role.value == "user"]
            summaries.append({
                "session_id": sid,
                "message_count": len(msgs),
                "first_message_at": msgs[0].created_at or datetime.now(),
                "last_message_at": msgs[-1].created_at or datetime.now(),
                "last_user_preview": (user_msgs[-1].content[:50] if user_msgs else None),
            })
        return summaries, total

    async def delete(self, session_id: str) -> None:
        self._store.pop(session_id, None)


# ========== Redis实现(可选) ==========
class RedisSessionService(SessionService):
    def __init__(self, settings: Settings):
        import redis.asyncio as aioredis
        url = settings.REDIS_URL or ""
        if settings.REDIS_PASSWORD.get_secret_value():
            # 注入password到url参数(略)
            pass
        self._redis = aioredis.from_url(url, decode_responses=True)
        self._ttl = settings.SESSION_TTL_SECONDS
        self._prefix = "agent:session:"

    async def create(self, session_id: str) -> None:
        key = f"{self._prefix}{session_id}"
        await self._redis.setnx(key, "[]")
        await self._redis.expire(key, self._ttl)

    async def get_messages(self, session_id: str) -> list[ChatMessage]:
        raw = await self._redis.get(f"{self._prefix}{session_id}")
        if not raw:
            return []
        return [ChatMessage(**x) for x in json.loads(raw)]

    async def append_messages(self, session_id: str, messages: list[ChatMessage]) -> None:
        key = f"{self._prefix}{session_id}"
        raw = await self._redis.get(key) or "[]"
        all_msgs = json.loads(raw) + [m.model_dump(mode="json") for m in messages]
        await self._redis.setex(key, self._ttl, json.dumps(all_msgs, ensure_ascii=False))

    async def list_sessions(self, page: int, page_size: int) -> tuple[list[dict], int]:
        return [], 0  # Redis实现需要额外索引,演示略

    async def delete(self, session_id: str) -> None:
        await self._redis.delete(f"{self._prefix}{session_id}")


# ========== 工厂: 根据配置自动选实现 ==========
_instance: SessionService | None = None

def get_session_service() -> SessionService:
    global _instance
    if _instance is not None:
        return _instance
    s = get_settings()
    if s.redis_enabled:
        try:
            _instance = RedisSessionService(s)
            return _instance
        except Exception:
            # Redis配置存在但连不上 → 降级内存,不影响服务启动
            _instance = InMemorySessionService(s.SESSION_TTL_SECONDS)
            return _instance
    _instance = InMemorySessionService(s.SESSION_TTL_SECONDS)
    return _instance
```

---

## 七、API 接口定义(路由层)

### 入口工厂

**文件路径**: `app/main.py`

```python
"""FastAPI应用工厂 —— create_app 模式便于测试"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.handlers import register_exception_handlers
from app.core.logging import setup_logging, logger
from app.api.health import router as health_router
from app.api.v1.chat import router as chat_router
from app.api.v1.session import router as session_router
from app.api.v1.tools import router as tools_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """生命周期: 启动时初始化日志/配置校验, 关闭时清理资源"""
    settings = get_settings()
    setup_logging(settings.LOG_LEVEL)
    logger.info(
        f"🚀 {settings.APP_NAME} starting env={settings.APP_ENV} "
        f"port={settings.PORT} llm_provider={settings.LLM_PROVIDER}"
    )
    yield
    logger.info(f"👋 {settings.APP_NAME} shutting down")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        description="基于FastAPI + ReAct模式的功能完整Agent服务",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.is_dev else None,  # 生产关闭swagger
        redoc_url="/redoc" if settings.is_dev else None,
        openapi_url="/openapi.json" if settings.is_dev else None,
    )

    # ========== 中间件 ==========
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def _request_logger(request: Request, call_next):
        """请求入口: 统一耗时 + trace_id + 响应包装(非流式)"""
        import uuid
        trace_id = request.headers.get("X-Trace-Id", str(uuid.uuid4()))
        start = time.perf_counter()
        # 把trace_id塞进state,便于异常处理和service层取
        request.state.trace_id = trace_id
        response = await call_next(request)
        took_ms = int((time.perf_counter() - start) * 1000)
        response.headers["X-Trace-Id"] = trace_id
        response.headers["X-Took-Ms"] = str(took_ms)
        logger.info(f"{request.method} {request.url.path} -> {response.status_code} took={took_ms}ms trace={trace_id}")
        return response

    # ========== 异常处理器 ==========
    register_exception_handlers(app)

    # ========== 路由注册 ==========
    app.include_router(health_router, prefix="/health", tags=["健康检查"])
    app.include_router(chat_router, prefix="/api/v1/chat", tags=["聊天"])
    app.include_router(session_router, prefix="/api/v1/sessions", tags=["会话管理"])
    app.include_router(tools_router, prefix="/api/v1/tools", tags=["工具管理"])

    # ========== 兜底 404,返回统一JSON格式 ==========
    @app.exception_handler(404)
    async def _404(_, __):
        return JSONResponse(status_code=404, content={
            "code": 404,
            "error": {"code": "NOT_FOUND", "message": "路由不存在,请检查URL和方法",
                      "suggestion": "访问 /docs 查看API清单(仅开发环境)"},
        })

    return app


# uvicorn app.main:app 会加载这个变量
app = create_app()


if __name__ == "__main__":  # pragma: no cover - 开发入口
    import uvicorn
    s = get_settings()
    uvicorn.run(
        "app.main:app",
        host=s.HOST,
        port=s.PORT,
        reload=s.is_dev,
        log_level=s.LOG_LEVEL.lower(),
    )
```

### 7.1 健康检查接口

**文件路径**: `app/api/health.py`

```python
"""健康检查: K8s liveness/readiness探针友好"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends

from app.api.deps import get_api_key_if_enabled
from app.agent.tools.registry import ToolRegistry
from app.services.session_service import get_session_service
from app.core.config import get_settings

router = APIRouter(dependencies=[Depends(get_api_key_if_enabled)])


@router.get("")
@router.get("/livez")
async def liveness() -> dict:
    """纯存活探针,不查任何依赖"""
    return {"status": "ok", "time": datetime.now().isoformat(timespec="seconds")}


@router.get("/readyz")
async def readiness(settings=Depends(get_settings)) -> dict:
    """就绪探针: 检查会话存储 + 工具注册情况"""
    try:
        session_svc = get_session_service()
        msgs = await session_svc.get_messages("probe")  # 读一下,不写
    except Exception as e:
        return {"status": "degraded", "reason": f"session service down: {e}"}

    tools = ToolRegistry.default().list_all()
    return {
        "status": "ok",
        "checks": {
            "session_service": "ok",
            "registry_tools": len(tools),
            "auth_enabled": settings.auth_enabled,
            "redis_enabled": settings.redis_enabled,
            "java_bridge_enabled": settings.java_bridge_enabled,
        },
        "time": datetime.now().isoformat(timespec="seconds"),
    }
```

### 7.2 聊天接口(同步+流式)

**文件路径**: `app/api/v1/chat.py`

```python
"""聊天API: 同步JSON + 流式SSE双通道"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import get_api_key_if_enabled
from app.core.config import get_settings
from app.models.schemas import ChatRequest, ChatResponse, StandardResponse
from app.services.agent_service import AgentService, get_agent_service

router = APIRouter(dependencies=[Depends(get_api_key_if_enabled)])


@router.post("", response_model=StandardResponse[ChatResponse])
async def chat_sync(
    req: ChatRequest,
    agent_svc: AgentService = Depends(get_agent_service),
) -> StandardResponse[ChatResponse]:
    """同步聊天接口。等待Agent执行完毕后一次性返回完整JSON。

    适用场景: 传统Web端、后端间调用、需要完整JSON结构的客户端。
    """
    start = time.perf_counter()
    result = await agent_svc.chat(req)
    took_ms = int((time.perf_counter() - start) * 1000)
    return StandardResponse(data=result, took_ms=took_ms)


@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    agent_svc: AgentService = Depends(get_agent_service),
    settings = Depends(get_settings),
):
    """流式聊天接口。返回 `text/event-stream` SSE事件流。

    事件格式:
        event: session_id
        data: sess-xxxxxxxxx

        event: token
        data: 你

        event: token
        data: 好

        event: done
        data: {"took_ms":1234}
    """
    if not req.stream:
        req.stream = True  # 强制流式

    session_id, stream_iter = await agent_svc.chat_stream(req)
    started_at = time.perf_counter()

    async def sse():
        yield f"event: session_id\ndata: {session_id}\n\n"
        async for token in stream_iter:
            yield f"event: token\ndata: {token}\n\n"
            await asyncio.sleep(0)
        took_ms = int((time.perf_counter() - started_at) * 1000)
        yield f"event: done\ndata: {{\x22took_ms\x22:{took_ms}}}\n\n"

    return StreamingResponse(
        sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",  # Nginx反向代理时关闭缓冲
        },
    )
```

### 7.3 会话管理接口

**文件路径**: `app/api/v1/session.py`

```python
"""会话管理API: 列表/详情/删除"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_api_key_if_enabled
from app.models.schemas import (
    ChatMessage,
    PaginationQuery,
    SessionListResponse,
    SessionSummary,
    StandardResponse,
)
from app.services.session_service import SessionService, get_session_service

router = APIRouter(dependencies=[Depends(get_api_key_if_enabled)])


@router.get("", response_model=StandardResponse[SessionListResponse])
async def list_sessions(
    q: PaginationQuery = Depends(),
    svc: SessionService = Depends(get_session_service),
) -> StandardResponse[SessionListResponse]:
    items, total = await svc.list_sessions(q.page, q.page_size)
    return StandardResponse(data=SessionListResponse(
        items=[SessionSummary(**x) for x in items],
        total=total, page=q.page, page_size=q.page_size,
    ))


@router.get("/{session_id}/messages", response_model=StandardResponse[list[ChatMessage]])
async def get_messages(
    session_id: str,
    svc: SessionService = Depends(get_session_service),
) -> StandardResponse[list[ChatMessage]]:
    msgs = await svc.get_messages(session_id)
    return StandardResponse(data=msgs)


@router.delete("/{session_id}", response_model=StandardResponse[bool])
async def delete_session(
    session_id: str,
    svc: SessionService = Depends(get_session_service),
) -> StandardResponse[bool]:
    await svc.delete(session_id)
    return StandardResponse(data=True)
```

### 7.4 工具管理接口

**文件路径**: `app/api/v1/tools.py`

```python
"""工具元数据查询, 方便前端/调试查看已注册的工具"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.agent.tools.registry import ToolRegistry
from app.api.deps import get_api_key_if_enabled
from app.models.schemas import StandardResponse, ToolInfo

router = APIRouter(dependencies=[Depends(get_api_key_if_enabled)])


@router.get("", response_model=StandardResponse[list[ToolInfo]])
async def list_tools(category: str | None = None) -> StandardResponse[list[ToolInfo]]:
    tools = ToolRegistry.default().list_all()
    if category:
        tools = [t for t in tools if t.category == category]
    return StandardResponse(data=[
        ToolInfo(
            name=t.name,
            description=t.description,
            input_schema=t.input_schema,
            category=t.category,
        ) for t in tools
    ])
```

**依赖注入: 可选API Key鉴权**

**文件路径**: `app/api/deps.py`

```python
"""FastAPI Depends 工厂"""

from __future__ import annotations

from fastapi import Header, HTTPException, status

from app.core.config import Settings, get_settings


async def get_api_key_if_enabled(
    settings: Settings = Depends(get_settings),
    api_key: str | None = Header(default=None, alias=lambda s: s.API_KEY_HEADER_NAME),
) -> None:
    """API Key鉴权(可选)。没配置API_KEYS时直接放行。"""
    if not settings.auth_enabled:
        return
    if api_key not in settings.API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_API_KEY",
                "message": f"需要提供合法的{settings.API_KEY_HEADER_NAME}请求头",
            },
        )
```

---

## 八、错误处理机制

### 8.1 自定义异常体系

**文件路径**: `app/core/exceptions.py`

```python
"""分层自定义异常, 业务异常 vs 系统异常分离"""

from __future__ import annotations

from typing import Any


class AppException(Exception):
    """业务异常基类, 不打印堆栈,只返回业务码"""
    http_status: int = 400
    code: str = "APP_ERROR"
    suggestion: str | None = None
    field: str | None = None

    def __init__(self, message: str, *, suggestion: str | None = None, field: str | None = None):
        super().__init__(message)
        self.message = message
        if suggestion:
            self.suggestion = suggestion
        if field:
            self.field = field


class ToolNotFoundError(AppException):
    http_status = 404
    code = "TOOL_NOT_FOUND"
    suggestion = "请使用 GET /api/v1/tools 查看可用工具列表"


class ToolExecutionError(AppException):
    http_status = 422
    code = "TOOL_EXECUTION_FAILED"
    suggestion = "请检查工具参数或稍后重试"


class AgentExecutionError(AppException):
    http_status = 502
    code = "AGENT_EXECUTION_FAILED"
    suggestion = "请稍后重试;若持续失败,请检查LLM配置或联系管理员"


class SessionNotFoundError(AppException):
    http_status = 404
    code = "SESSION_NOT_FOUND"
    suggestion = "请检查session_id是否正确,或创建新会话"


class ConfigException(AppException):
    http_status = 500
    code = "INVALID_CONFIG"
    suggestion = "请核对 config/.env 中的必填配置项"
```

### 8.2 全局异常处理器

**文件路径**: `app/core/handlers.py`

```python
"""全局异常处理器: 统一输出 ErrorResponse 格式"""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException
from app.core.logging import logger


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def _app_exception(request: Request, exc: AppException):
        trace_id = getattr(request.state, "trace_id", None)
        body = {
            "code": exc.http_status,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "field": exc.field,
                "suggestion": exc.suggestion,
            },
            "trace_id": trace_id,
        }
        logger.warning(f"AppException[{exc.code}]: {exc.message} trace={trace_id}")
        return JSONResponse(status_code=exc.http_status, content=jsonable_encoder(body))

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, exc: RequestValidationError):
        trace_id = getattr(request.state, "trace_id", None)
        # Pydantic v2 errors: [{loc, msg, type}]
        first = exc.errors()[0] if exc.errors() else {}
        field = ".".join(str(x) for x in first.get("loc", [])) or None
        message = first.get("msg", str(exc))
        suggestion = _validation_suggestion(first.get("type", ""))
        body = {
            "code": 422,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": f"请求参数校验失败: {message}",
                "field": field,
                "suggestion": suggestion,
            },
            "trace_id": trace_id,
        }
        logger.info(f"ValidationError field={field} msg={message} trace={trace_id}")
        return JSONResponse(status_code=422, content=jsonable_encoder(body))

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception):
        trace_id = getattr(request.state, "trace_id", None)
        logger.exception(f"UnhandledException: {exc} trace={trace_id}")
        body = {
            "code": 500,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "服务内部错误,请稍后重试或联系管理员提供trace_id",
                "suggestion": "请保存trace_id,运维人员可通过日志快速定位",
            },
            "trace_id": trace_id,
        }
        return JSONResponse(status_code=500, content=body)


def _validation_suggestion(err_type: str) -> str | None:
    return {
        "missing": "请检查请求体中是否缺少该字段",
        "string_too_long": "请缩短该字段内容长度",
        "int_parsing": "请确保该字段是合法整数",
        "literal_error": "请从枚举允许的取值中选择",
    }.get(err_type)
```

### 8.3 请求参数校验错误

所有接口使用Pydantic模型声明,错误自动被 `_validation` 处理器捕获,返回统一错误格式,前端可精准提示字段。配合严格模式(`extra="forbid"`)还能拦截多余字段,防止用户误传。

---

## 九、与 Java 组件交互方案

Python Agent 与 Java 服务并存是常见的企业场景(Java写业务主数据、事务处理, Python做AI推理、流式NLP交互)。提供 **HTTP / gRPC / MQ** 三档,按需选择。

### 9.1 HTTP REST 调用(推荐:中小规模,快速对接)

**文件路径**: `app/services/java_bridge.py`

```python
"""Java后端桥接: 同步HTTP调用 + 超时/重试

Agent中可用 `java:<methodName>` 作为工具名触发:
    - 在ToolRegistry中注册java工具即可让Agent选择调用
    - 也可在工具名硬编码前缀 `java:queryUserOrders` 直接指定Java方法
"""

from __future__ import annotations

from typing import Any, Optional

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import Settings, get_settings


class JavaBridge:
    def __init__(self, settings: Optional[Settings] = None):
        s = settings or get_settings()
        base = str(s.JAVA_BACKEND_BASE_URL).rstrip("/") if s.JAVA_BACKEND_BASE_URL else ""
        self._base = base
        self._timeout = httpx.Timeout(s.JAVA_BACKEND_TIMEOUT_MS / 1000.0)
        self._api_key = s.JAVA_BACKEND_API_KEY.get_secret_value()

    async def invoke(self, method: str, arguments: dict) -> Any:
        if not self._base:
            raise RuntimeError("Java bridge未启用,请配置JAVA_BACKEND_BASE_URL")
        return await self._post(f"/agent/tools/{method}", arguments)

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=0.2, max=4),
        retry=retry_if_exception_type((httpx.TransportError, httpx.HTTPStatusError)),
    )
    async def _post(self, path: str, payload: dict) -> Any:
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["X-Api-Key"] = self._api_key
        url = f"{self._base}{path}"
        async with httpx.AsyncClient(timeout=self._timeout) as c:
            r = await c.post(url, headers=headers, json=payload)
            r.raise_for_status()
            return r.json()


_instance: JavaBridge | None = None

def get_java_bridge() -> JavaBridge:
    global _instance
    if _instance is None:
        _instance = JavaBridge()
    return _instance
```

**Java侧Spring Boot接口示例(伪代码)**:

```java
// Java侧 controller
@RestController @RequestMapping("/agent/tools")
public class AgentBridgeController {

    // 允许Python Agent调用Java业务方法
    @PostMapping("/queryUserOrders")
    public ApiResp<List<OrderDTO>> queryUserOrders(@RequestBody Map<String,Object> args) {
        Long userId = Long.valueOf(args.get("userId").toString());
        return ApiResp.ok(orderService.findByUserId(userId));
    }
}
```

### 9.2 gRPC 高性能调用(推荐:高并发、低延迟)

当Java与Python需要高频、低延迟调用(1000+ QPS)时,HTTP的JSON序列化开销不可忽略,切换为gRPC。

**核心步骤**:
1. 定义 `.proto`(跨语言契约,放在单独Git仓库)
2. Java侧 `protobuf-maven-plugin` 生成Server stub + 业务实现
3. Python侧 `pip install grpcio grpcio-tools` + `python -m grpc_tools.protoc` 生成Client stub
4. 在 `java_bridge.py` 里替换HTTP Client为 gRPC Client,保留方法签名不变(Service层零改动)

**`integrations/grpc_client.py`(骨架)**:

```python
# app/integrations/grpc_client.py  骨架
import grpc
from app.core.config import get_settings

class JavaGrpcClient:
    def __init__(self):
        s = get_settings()
        channel = grpc.aio.insecure_channel("java-service:6565")  # gRPC端口
        # self.stub = JavaAgentServiceStub(channel)
        ...
```

### 9.3 消息队列解耦(Kafka/RabbitMQ)(推荐:异步、削峰、事件驱动)

**场景**:Java侧想触发Agent后台任务、或Agent把大结果异步推给Java,HTTP就不合适(超时/阻塞)。

**核心步骤**:
1. Docker/docker-compose起Kafka或RabbitMQ(或复用现有)
2. Python `integrations/mq_client.py` 生产者+消费者
3. Java侧Spring Boot `spring-kafka` 对应Producer/Consumer
4. Topic约定:
   - `agent.commands` Java→Python: 下发Agent任务
   - `agent.results`  Python→Java: 推送任务结果
   - `agent.events`   Python→Java: 流式事件

**骨架**:

```python
# app/integrations/mq_client.py  骨架
from __future__ import annotations
import json

class KafkaEventPublisher:
    def __init__(self, brokers: str, topic: str):
        from aiokafka import AIOKafkaProducer
        self._producer = AIOKafkaProducer(bootstrap_servers=brokers)
        self._topic = topic
    async def publish(self, key: str, payload: dict):
        await self._producer.send_and_wait(
            self._topic, key=key.encode(), value=json.dumps(payload, ensure_ascii=False).encode()
        )
    async def start(self): await self._producer.start()
    async def stop(self):  await self._producer.stop()
```

---

## 十、单元测试编写

### 10.1 测试框架与依赖

已在 `requirements-dev.txt` 中声明 `pytest / pytest-asyncio / pytest-cov / httpx`。

**`pytest.ini`**:

```ini
[pytest]
asyncio_mode = auto
testpaths = app/tests
python_files = test_*.py
addopts = -v --cov=app --cov-report=term-missing --cov-report=html
```

### 10.2 conftest.py TestClient+Mock配置

**文件路径**: `app/tests/conftest.py`

```python
"""测试公共fixture"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

import pytest
from fastapi.testclient import TestClient

from app.agent.base import BaseAgent
from app.agent.llm_client import LLMClient
from app.agent.react_agent import ReActAgent
from app.agent.tools.registry import ToolRegistry
from app.main import create_app
from app.models.agent_state import AgentRunState
from app.services.agent_service import AgentService
from app.services.session_service import InMemorySessionService


class FakeLLM(LLMClient):
    """Mock LLM: 完全可控, 不发真实请求"""

    RESPONSE_SEQUENCE: list[str] = []

    async def chat_completion(self, messages, **extra) -> str:
        if not self.RESPONSE_SEQUENCE:
            return "Final Answer: 你好,来自Mock LLM。"
        return self.RESPONSE_SEQUENCE.pop(0)


@pytest.fixture
def client(monkeypatch) -> Iterator[TestClient]:
    """FastAPI TestClient, 注入Mock LLM+内存会话"""
    monkeypatch.setenv("APP_ENV", "dev")
    monkeypatch.setenv("DEBUG", "true")
    app = create_app()
    with TestClient(app) as tc:
        yield tc


@pytest.fixture
def fake_agent() -> BaseAgent:
    """用于Service/Agent层的单测Agent(Fake LLM驱动)"""
    registry = ToolRegistry.default()
    agent = ReActAgent(llm=FakeLLM(), tools=registry)
    return agent


@pytest.fixture
async def agent_service(fake_agent) -> AgentService:
    return AgentService(agent=fake_agent, session_svc=InMemorySessionService())
```

### 10.2 核心模块测试用例

**`app/tests/unit/test_react_agent.py`**:

```python
"""Agent ReAct核心逻辑测试"""

import pytest

from app.agent.llm_client import LLMClient
from app.agent.react_agent import ReActAgent
from app.agent.tools.registry import ToolRegistry
from app.models.agent_state import AgentRunState


class _FixedLLM(LLMClient):
    def __init__(self, replies: list[str]):
        super().__init__()
        self._q = list(replies)

    async def chat_completion(self, messages, **extra) -> str:
        return self._q.pop(0) if self._q else "Final Answer: (默认)"


@pytest.mark.asyncio
async def test_agent_direct_final_answer():
    """场景: LLM一轮就给出Final Answer"""
    agent = ReActAgent(
        llm=_FixedLLM(["Final Answer: 北京是中华人民共和国首都。"]),
        tools=ToolRegistry.default(),
    )
    state = AgentRunState(
        session_id="t1", user_input="北京的首都是什么?",
        system_prompt=None, tools_whitelist=None, enable_java_bridge=False,
    )
    result = await agent.run(state)
    assert "北京" in result
    assert state.iterations == 1
    assert state.final_answer is not None


@pytest.mark.asyncio
async def test_agent_action_then_final():
    """场景: 先调用计算器,再给结论"""
    agent = ReActAgent(
        llm=_FixedLLM([
            "Thought: 需要计算表达式\nAction: {\"tool\":\"calculator\",\"arguments\":{\"expression\":\"(1+2)*3\"}}\n",
            "Thought: 计算器返回9,可以总结\nFinal Answer: 算式(1+2)*3的结果是9。",
        ]),
        tools=ToolRegistry.default(),
    )
    state = AgentRunState(
        session_id="t2", user_input="(1+2)*3等于多少?",
        system_prompt=None, tools_whitelist=None, enable_java_bridge=False,
    )
    result = await agent.run(state)
    assert "9" in result
    assert len(state.tool_executions) == 1
    assert state.tool_executions[0].result == 9
    assert len(state.thinking_trace) == 2


@pytest.mark.asyncio
async def test_agent_max_iteration_stop():
    """场景: LLM总输出格式错误,到达上限应优雅终止"""
    nonsense = "我随便说点啥不带任何标签..."
    agent = ReActAgent(llm=_FixedLLM([nonsense] * 20), tools=ToolRegistry.default())
    state = AgentRunState(
        session_id="t3", user_input="随便问",
        system_prompt=None, tools_whitelist=None, enable_java_bridge=False,
        max_iterations=3,
    )
    result = await agent.run(state)
    assert state.iterations == 3
    assert "多轮推理仍未得到" in result
```

### 10.3 API 接口测试用例

**`app/tests/api/test_health.py`**:

```python
def test_livez(client):
    resp = client.get("/health/livez")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_readyz(client):
    resp = client.get("/health/readyz")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["checks"]["session_service"] == "ok"
```

**`app/tests/api/test_chat.py`**:

```python
import json


def test_chat_returns_trace_and_took(client):
    resp = client.post("/api/v1/chat", json={
        "message": "你好",
        "stream": False,
    })
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["code"] == 0
    assert body["data"]["reply"], "需要返回非空reply"
    assert isinstance(body["data"]["messages"], list)
    assert isinstance(body["took_ms"], int)


def test_chat_validation_error_field(client):
    """message字段缺失 → 422 + 字段精准定位"""
    resp = client.post("/api/v1/chat", json={})
    assert resp.status_code == 422, resp.text
    err = resp.json()["error"]
    assert err["code"] == "VALIDATION_ERROR"
    assert err["field"] == "body.message"


def test_chat_stream_sse(client):
    resp = client.post("/api/v1/chat/stream", json={
        "message": "你好", "stream": True,
    })
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")
    chunks = list(resp.iter_lines())
    events = [line for line in chunks if line.startswith("event:")]
    # 至少有 session_id + 若干token + done
    assert events, "需要至少SSE事件"
    assert any("session_id" in e for e in events)
    assert any("done" in e for e in events)
```

---

## 十一、服务部署配置

### 11.1 Uvicorn/Gunicorn 生产级启动

**开发模式(热重载)**: `python -m app.main` (见 main.py 底部)

**生产模式(Gunicorn + UvicornWorker,多进程)**:

```bash
# 1 worker = 1进程; 一般设为 CPU核数 * (1~2)
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:${PORT:-8000} \
  --access-logfile - \
  --error-logfile - \
  --log-level ${LOG_LEVEL:-info}
```

> Windows下没有 `gunicorn`,生产推荐直接上WSL2/Docker,或者用 `uvicorn --workers 4 app.main:app`。

### 11.2 Docker 容器化部署

**`Dockerfile`(多阶段构建,减小镜像体积)**:

```dockerfile
# ========== Builder: 安装依赖并缓存wheel ==========
FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir -w /wheels -r requirements.txt

# ========== Runtime: 只装二进制wheel,不保留编译链 ==========
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# 时区(可选,亚洲/上海)
RUN apt-get update && apt-get install -y --no-install-recommends tzdata ca-certificates && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
COPY requirements.txt ./
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && \
    rm -rf /wheels /root/.cache

COPY app ./app
COPY config ./config

EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -fs http://localhost:8000/health/livez || exit 1

CMD ["sh", "-c", "gunicorn app.main:app --workers ${WORKERS:-2} --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --access-logfile - --error-logfile - --log-level ${LOG_LEVEL:-info}"]
```

**`docker-compose.yml`(本地全家桶:Agent + Redis + Ollama)**:

```yaml
services:
  agent:
    build: .
    env_file: ./config/.env
    ports:
      - "${PORT:-8000}:8000"
    depends_on:
      - redis
      - ollama
    restart: unless-stopped
    networks: [agent-net]

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --save 60 1
    volumes: [redis-data:/data]
    networks: [agent-net]

  ollama:
    image: ollama/ollama:latest
    volumes: [ollama-data:/root/.ollama]
    # GPU: deploy.resources.reservations.devices.driver=nvidia count=all
    ports: ["11434:11434"]
    networks: [agent-net]

volumes:
  redis-data:
  ollama-data:
networks:
  agent-net:
```

### 11.3 Nginx 反向代理配置

**`config/nginx.conf` 片段**:

```nginx
upstream agent_servers {
    server 127.0.0.1:8000;
    # server 127.0.0.1:8001;  # 多实例负载均衡
    keepalive 32;
}

server {
    listen 80;
    server_name agent.example.com;

    client_max_body_size 10M;

    # 非流式正常代理
    location / {
        proxy_pass http://agent_servers;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 120s;
    }

    # 流式SSE: 关闭缓冲+长连接
    location ~ /chat/stream$ {
        proxy_pass http://agent_servers;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection "";
        proxy_set_header X-Accel-Buffering no;
        chunked_transfer_encoding off;
        proxy_read_timeout 600s;  # 流式可能持续久
    }
}
```

### 11.4 日志与监控配置

**`app/core/logging.py`**:

```python
"""结构化日志: 控制台+可选JSON文件"""

from __future__ import annotations

import logging
import sys
from typing import Optional

_logger: Optional[logging.Logger] = None


def setup_logging(level: str = "INFO") -> logging.Logger:
    global _logger
    if _logger:
        return _logger
    log_level = logging.getLevelName(level.upper())
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s | %(pathname)s:%(lineno)d",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(fmt)

    logger = logging.getLogger("agent_service")
    logger.setLevel(log_level)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False

    # 屏蔽第三方的嘈杂日志
    for noisy in ("httpx", "httpcore", "uvicorn.access"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _logger = logger
    return logger


def logger() -> logging.Logger:
    if _logger is None:
        return setup_logging()
    return _logger
```

---

## 十二、服务启动与测试命令

### 12.1 本地开发启动

前置步骤: 按[第二章](#二依赖包安装与环境配置)创建虚拟环境、安装依赖、复制`config/.env.example`→`config/.env`并填入LLM参数。

```bash
# Windows PowerShell (推荐先在IDE终端激活 .venv)
# 先拷贝配置模板 -> 编辑LLM密钥等
Copy-Item config\.env.example config\.env

# 验证配置(可选,会打印脱敏后的当前配置)
python -m app.core.config

# 启动开发服务器(热重载 + /docs + /redoc)
python -m app.main
```

启动成功看到:
```
✅ Config loaded. APP_ENV=dev, PORT=8000
   LLM provider=ollama, model=qwen2.5:7b
🚀 FastAPI Agent Service starting env=dev port=8000 llm_provider=ollama
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 12.2 单元测试执行

```bash
# 跑全部测试 + 覆盖率报告(终端+HTML)
pytest

# 只跑API测试,并行(如装了 pytest-xdist)
pytest app/tests/api -n auto

# 结果解读:
# - 终端显示 PASS / FAIL 统计
# - HTML覆盖率页面: ./htmlcov/index.html (浏览器打开)
```

> 测试目标: 单元测试 **80%+ 覆盖率**,API接口 **100% 覆盖**关键路径(成功/参数校验/鉴权)。

### 12.3 API 手动测试(curl)

```bash
# 1) 健康检查
curl http://localhost:8000/health/readyz

# 2) 查已注册工具
curl http://localhost:8000/api/v1/tools

# 3) 同步聊天(计算器场景: 命中Action→计算器→Final Answer)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo-001",
    "message": "请计算 (123 + 456) * 2 的结果",
    "stream": false
  }' | python -m json.tool

# 4) 流式聊天(前端EventSource友好)
curl -N -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"用你自己的话介绍ReAct模式","stream":true}'

# 5) 会话列表
curl http://localhost:8000/api/v1/sessions?page=1&page_size=10
```

### 12.4 API 文档访问

只要 `config/.env` 里 `APP_ENV=dev`(默认),即可在浏览器中查看:

| 文档 | URL | 功能 |
|------|-----|------|
| Swagger UI(可在线调试) | http://localhost:8000/docs | 填参数→点「Try it out」→执行 |
| ReDoc(阅读友好) | http://localhost:8000/redoc | 三栏式,适合打印/PDF |
| OpenAPI Schema(JSON) | http://localhost:8000/openapi.json | 前端/Java可据此生成SDK |

---

## 十三、FastAPI 最佳实践清单

| # | 实践 | 本项目体现 | 收益 |
|:-:|------|-----------|------|
| 1 | **应用工厂模式** `create_app()` | `main.py` 集中注册中间件/路由/异常 | 测试/不同环境配置隔离 |
| 2 | **Pydantic严格模式DTO** | `BaseSchema(extra=forbid)` | 拒绝未声明字段,防注入+文档 |
| 3 | **分层解耦,依赖倒置** | Service依赖Agent抽象(BaseAgent) | 替换实现零影响,易测 |
| 4 | **可选组件降级** | Redis/Java/Kafka未配置时→内存/空实现 | 不因为可选组件挂掉API |
| 5 | **配置外置环境变量** | `config.py` Pydantic Settings | 端口/密钥/URL可改不改代码 |
| 6 | **LLM调用带重试** | `tenacity` + wait_exponential | 网络抖动时自动重试,用户无感 |
| 7 | **统一异常+标准响应** | `handlers.py` + `StandardResponse[T]` | 前端只处理1种格式 |
| 8 | **全链路trace_id** | 中间件注入,X-Trace-Id响应头 | 前端/运维可精确定位 |
| 9 | **非流式+流式SSE双通道** | `/chat` 和 `/chat/stream` | 覆盖Web/小程序/APP各种客户端 |
| 10 | **异步优先** | 路由/LLM/工具/Redis都是async | 单机支持几千并发 |
| 11 | **API Key可选鉴权** | `deps.get_api_key_if_enabled` | 开发免配,生产一把开启 |
| 12 | **API版本前缀** | `/api/v1/xxx` | 未来迭代平滑过渡 |
| 13 | **健康检查双探针** | `/health/livez` + `/readyz` | K8s/容器编排友好 |
| 14 | **单元+API双测** | `unit/` + `api/` 分离,覆盖率目标80% | 重构不敢改代码的噩梦 |
| 15 | **Docker多阶段+HEALTHCHECK** | Dockerfile builder/runtime分离 | 镜像体积小+自动重启异常实例 |
| 16 | **Nginx SSE配置** | `config/nginx.conf` 关掉proxy_buffering | 流式响应不会被Nginx攒到最后才发 |

---

## 十四、总结

本文档从零搭建了一套**生产可运行、测试完善、部署完整**的FastAPI Agent服务。

**交付物总览**:

| 交付物 | 文件/路径 | 说明 |
|-------|----------|------|
| **代码架构** | `app/{main,core,models,agent,services,api,integrations}` | 分层解耦,可单测可替换 |
| **配置体系** | `app/core/config.py` + `config/.env.example` | 全环境变量,可选组件默认降级不崩溃 |
| **Agent核心** | `ReActAgent` + `ToolRegistry` + 示例工具 | 不依赖框架SDK,兼容任何OpenAI兼容LLM |
| **API接口** | 健康检查/聊天/流式/会话/工具 | 全部Pydantic声明,自动生成文档 |
| **错误处理** | 3类异常 + 全局处理器 + 参数校验 | 统一JSON错误格式,字段级定位 |
| **Java交互** | HTTP桥(开箱)+gRPC骨架+MQ骨架 | 三档方案覆盖中小规模到大规模 |
| **测试** | `app/tests` 单元+API 用例+mock LLM | 运行 `pytest` 即可验证 |
| **部署** | Dockerfile + compose + nginx + gunicorn | 本地→生产一套配置通吃 |
| **文档** | `/docs` + `/redoc` + 本章启动/测试/curl命令 | 无经验同学也能快速跑通 |

**快速落地三步骤**:
1. `pip install -r requirements.txt` + 复制 `config/.env.example` 为 `config/.env` 填入LLM密钥
2. `python -m app.main` → 浏览器打开 http://localhost:8000/docs
3. `pytest` 验证核心逻辑 → 开始在 `app/agent/tools/` 目录新增你的业务工具

从这里出发,你可以很自然地扩展:把工具接入真正的搜索/RAG向量库、把会话存储切换为Redis、把Java桥接换成gRPC、把监控接入Prometheus+Grafana。骨架已就位,剩下的就是往里面填肉。

---

> **相关文档**
>
> - [151为什么Agent开发选择Python语言.md](./151为什么Agent开发选择Python语言.md): 选型理由
> - [152Python-Agent服务部署完整指南.md](./152Python-Agent服务部署完整指南.md): 更详细的生产部署、监控、备份
