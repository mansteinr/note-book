# Python Agent 工程化实践详解

> 本文档系统介绍 Python Agent 开发中的关键工程化实践，涵盖环境变量管理、日志记录管理、异常处理、成本控制四大核心模块，包含具体实现代码、最佳实践与常见问题解决方案，确保内容具备可操作性与工程实用性。

---

## 目录

- [一、环境变量管理](#一环境变量管理)
  - [1.1 配置文件设计](#11-配置文件设计)
  - [1.2 敏感信息处理](#12-敏感信息处理)
  - [1.3 多环境配置策略](#13-多环境配置策略)
- [二、日志记录管理](#二日志记录管理)
  - [2.1 日志级别设置](#21-日志级别设置)
  - [2.2 日志格式规范](#22-日志格式规范)
  - [2.3 日志存储与轮转机制](#23-日志存储与轮转机制)
- [三、异常处理](#三异常处理)
  - [3.1 自定义异常类设计](#31-自定义异常类设计)
  - [3.2 异常捕获与恢复策略](#32-异常捕获与恢复策略)
  - [3.3 错误上报机制](#33-错误上报机制)
- [四、成本控制](#四成本控制)
  - [4.1 循环次数限制](#41-循环次数限制)
  - [4.2 API 请求频率控制](#42-api-请求频率控制)
  - [4.3 模型选择策略](#43-模型选择策略)
  - [4.4 缓存重复请求](#44-缓存重复请求)
  - [4.5 资源使用优化方案](#45-资源使用优化方案)
- [五、最佳实践指南](#五最佳实践指南)
- [六、常见问题解决方案](#六常见问题解决方案)

---

## 一、环境变量管理

### 1.1 配置文件设计

#### 1.1.1 为什么需要配置管理

Agent 应用涉及大量配置项：LLM API Key、模型名称、数据库连接、向量库地址、工具配置等。硬编码到代码中会导致三大问题：①安全风险（Key 泄露）；②环境难切换（dev/test/prod）；③协作冲突（多人改同一份代码）。

#### 1.1.2 分层配置架构

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    subgraph 配置优先级从高到低
        ENV[1. 环境变量<br/>最高优先级<br/>生产环境用]
        ENV_FILE[2. .env 文件<br/>本地开发用]
        YAML[3. config.yaml<br/>项目默认配置]
        DEFAULT[4. 代码默认值<br/>兜底]
    end

    ENV --> ENV_FILE --> YAML --> DEFAULT
```

#### 1.1.3 配置文件实现

**项目结构**：

```
agent_project/
├── config/
│   ├── config.yaml          # 项目默认配置
│   ├── config.dev.yaml      # 开发环境覆盖
│   ├── config.prod.yaml     # 生产环境覆盖
├── .env                     # 本地敏感信息(gitignore)
├── .env.example             # 敏感信息模板(提交到 git)
└── src/
    └── config.py            # 配置加载逻辑
```

**config.yaml（项目默认配置）**：

```yaml
# 项目默认配置
app:
  name: "agent-service"
  version: "1.0.0"
  environment: "dev"

llm:
  model: "gpt-4o-mini"
  temperature: 0.0
  max_tokens: 2000
  timeout: 30

vector_db:
  host: "localhost"
  port: 6334
  collection: "knowledge_base"

tools:
  weather_api:
    url: "https://api.weather.com"
    timeout: 10
  search_api:
    url: "https://api.search.com"
    max_results: 5

logging:
  level: "INFO"
  format: "json"
  file: "logs/agent.log"
  max_size_mb: 50
  backup_count: 10

cost_control:
  max_iterations: 8
  max_tokens_per_task: 50000
  daily_budget_usd: 10.0
```

**.env.example（敏感信息模板）**：

```bash
# 复制此文件为 .env 并填入真实值
# 永远不要将 .env 提交到 git

# LLM API Keys
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# 数据库
DATABASE_URL=postgresql://user:pass@localhost:5432/agent_db

# 向量库
QDRANT_API_KEY=your-qdrant-key

# 第三方工具
WEATHER_API_KEY=your-weather-key
SEARCH_API_KEY=your-search-key

# 监控
SENTRY_DSN=https://xxx@sentry.io/xxx
```

**config.py（配置加载逻辑）**：

```python
import os
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    model: str = "gpt-4o-mini"
    api_key: str = Field(..., description="LLM API Key")
    temperature: float = 0.0
    max_tokens: int = 2000
    timeout: int = 30
    base_url: Optional[str] = None


class VectorDBConfig(BaseModel):
    host: str = "localhost"
    port: int = 6334
    api_key: Optional[str] = None
    collection: str = "knowledge_base"


class LoggingConfig(BaseModel):
    level: str = "INFO"
    format: str = "json"  # json / text
    file: str = "logs/agent.log"
    max_size_mb: int = 50
    backup_count: int = 10


class CostControlConfig(BaseModel):
    max_iterations: int = 8
    max_tokens_per_task: int = 50000
    daily_budget_usd: float = 10.0
    cache_ttl: int = 3600


class AppConfig(BaseModel):
    """全局配置根类"""
    app_name: str
    environment: str
    llm: LLMConfig
    vector_db: VectorDBConfig
    logging: LoggingConfig
    cost_control: CostControlConfig


class ConfigLoader:
    """分层配置加载器:环境变量 > .env > yaml > 默认值"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        # 1. 加载 .env 文件
        load_dotenv()

    def load(self, environment: Optional[str] = None) -> AppConfig:
        """加载配置:默认 → 环境覆盖 → .env → 环境变量"""
        env = environment or os.getenv("APP_ENV", "dev")

        # 1. 加载默认配置
        with open(self.config_dir / "config.yaml") as f:
            config_data = yaml.safe_load(f)

        # 2. 加载环境覆盖配置
        env_config_file = self.config_dir / f"config.{env}.yaml"
        if env_config_file.exists():
            with open(env_config_file) as f:
                env_data = yaml.safe_load(f)
            config_data = self._deep_merge(config_data, env_data)

        # 3. 敏感信息从环境变量注入(优先级最高)
        config_data["llm"]["api_key"] = os.getenv("OPENAI_API_KEY")
        config_data["llm"]["base_url"] = os.getenv("OPENAI_BASE_URL")
        config_data["vector_db"]["api_key"] = os.getenv("QDRANT_API_KEY")
        config_data["environment"] = env

        return AppConfig(**config_data)

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """深度合并两个配置字典"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result


# 全局配置单例
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """获取全局配置(单例模式)"""
    global _config
    if _config is None:
        loader = ConfigLoader()
        _config = loader.load()
    return _config
```

### 1.2 敏感信息处理

| 原则 | 做法 | 示例 |
|------|------|------|
| **不入库** | API Key 永远不提交到 git | `.env` 加入 `.gitignore` |
| **环境变量** | 敏感信息通过环境变量注入 | `os.getenv("OPENAI_API_KEY")` |
| **模板引导** | 提供 `.env.example` 模板 | 新成员复制即用 |
| **脱敏日志** | 日志中 Key 用 `sk-***xxxx` 脱敏 | `mask_secret(key)` |
| **密钥管理** | 生产用 Vault/KMS，不用 .env | AWS Secrets Manager |
| **定期轮换** | API Key 定期更换 | 90 天轮换一次 |

**密钥脱敏工具**：

```python
import re


def mask_secret(secret: str, visible_chars: int = 4) -> str:
    """脱敏密钥:sk-abc123456 → sk-***3456"""
    if not secret or len(secret) <= visible_chars:
        return "***"
    return f"{secret[:3]}***{secret[-visible_chars:]}"


def mask_secrets_in_text(text: str) -> str:
    """脱敏文本中的所有密钥"""
    patterns = [
        (r"sk-[a-zA-Z0-9]{20,}", "sk-***"),
        (r"password=[^&\s]+", "password=***"),
        (r"api_key=[^&\s]+", "api_key=***"),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text
```

### 1.3 多环境配置策略

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart LR
    DEV[开发环境<br/>dev<br/>用 .env + config.dev.yaml]
    TEST[测试环境<br/>test<br/>用环境变量 + config.test.yaml]
    PROD[生产环境<br/>prod<br/>用 Vault + config.prod.yaml]

    DEV -->|代码合并| TEST
    TEST -->|发布| PROD

    style DEV fill:#e8f5e9,stroke:#2e7d32
    style TEST fill:#fff3e0,stroke:#e65100
    style PROD fill:#ffcdd2,stroke:#c62828
```

| 环境 | 配置来源 | 模型 | 日志级别 | 预算 |
|------|----------|------|----------|------|
| **dev** | .env + config.dev.yaml | gpt-4o-mini | DEBUG | $1/天 |
| **test** | 环境变量 + config.test.yaml | gpt-4o-mini | INFO | $5/天 |
| **prod** | Vault + config.prod.yaml | gpt-4o | WARN | $50/天 |

**环境切换方式**：

```bash
# 开发环境(默认)
export APP_ENV=dev
python main.py

# 测试环境
export APP_ENV=test
python main.py

# 生产环境
export APP_ENV=prod
python main.py
```

---

## 二、日志记录管理

### 2.1 日志级别设置

```python
import logging

# Agent 专用日志级别指南
LOG_LEVEL_GUIDE = {
    "DEBUG": "详细调试信息,如 LLM Prompt/Response 全文,仅开发环境",
    "INFO": "关键业务节点,如任务开始/结束、工具调用,生产环境默认",
    "WARNING": "可恢复异常,如重试、降级、预算接近上限",
    "ERROR": "不可恢复错误,如 API Key 失效、数据库连接失败",
    "CRITICAL": "系统级故障,如服务不可用、数据损坏",
}
```

| 场景 | 级别 | 示例 |
|------|------|------|
| LLM 完整 Prompt | DEBUG | `DEBUG: Prompt: {prompt}` |
| 工具调用开始 | INFO | `INFO: 调用工具 search_weather(北京)` |
| LLM 重试 | WARNING | `WARNING: LLM 超时,第2次重试` |
| API Key 无效 | ERROR | `ERROR: OpenAI API Key 无效` |
| 数据库连接失败 | CRITICAL | `CRITICAL: 无法连接数据库,服务不可用` |
| 预算用至 80% | WARNING | `WARNING: 日预算已用 80%($8/$10)` |

### 2.2 日志格式规范

**结构化 JSON 日志（推荐生产环境）**：

```python
import json
import logging
from datetime import datetime
from typing import Any


class JsonFormatter(logging.Formatter):
    """JSON 结构化日志格式器"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 追加 Agent 专有字段
        for attr in ["trace_id", "task_id", "user_id", "tool_name",
                     "tokens_used", "cost_usd", "iteration"]:
            if hasattr(record, attr):
                log_data[attr] = getattr(record, attr)

        # 追加异常信息
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        return json.dumps(log_data, ensure_ascii=False)


class AgentLoggerAdapter(logging.LoggerAdapter):
    """Agent 日志适配器:自动注入 trace_id/task_id"""

    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        # 自动注入追踪字段
        for field in ["trace_id", "task_id", "user_id"]:
            if field not in extra:
                extra[field] = self.extra.get(field, "unknown")
        kwargs["extra"] = extra
        return msg, kwargs
```

**日志输出示例**：

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "agent.tool",
  "message": "调用工具 search_weather 成功",
  "module": "weather_tool",
  "function": "execute",
  "line": 45,
  "trace_id": "trace-abc123",
  "task_id": "task-456",
  "user_id": "user-789",
  "tool_name": "search_weather",
  "tokens_used": 150,
  "cost_usd": 0.0002,
  "iteration": 2
}
```

### 2.3 日志存储与轮转机制

```python
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path


def setup_logging(config: LoggingConfig, trace_id: str = None):
    """初始化日志系统"""
    log_format = JsonFormatter() if config.format == "json" else None

    # 根 Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.level.upper()))

    # 1. 控制台输出(开发环境)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    if log_format:
        console_handler.setFormatter(log_format)
    else:
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
    root_logger.addHandler(console_handler)

    # 2. 文件输出 + 按大小轮转
    log_dir = Path(config.file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        config.file,
        maxBytes=config.max_size_mb * 1024 * 1024,  # MB → bytes
        backupCount=config.backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    if log_format:
        file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)

    # 3. 错误日志单独文件
    error_handler = RotatingFileHandler(
        str(log_dir / "error.log"),
        maxBytes=config.max_size_mb * 1024 * 1024,
        backupCount=config.backup_count,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    if log_format:
        error_handler.setFormatter(log_format)
    root_logger.addHandler(error_handler)

    # 4. 按时间轮转(每天一个文件,保留 30 天)
    daily_handler = TimedRotatingFileHandler(
        str(log_dir / "agent_daily.log"),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    daily_handler.setLevel(logging.INFO)
    if log_format:
        daily_handler.setFormatter(log_format)
    root_logger.addHandler(daily_handler)
```

**轮转策略对比**：

| 策略 | 机制 | 适用场景 |
|------|------|----------|
| **按大小轮转** | 文件达到 N MB 后切换，保留 M 个备份 | 通用场景 |
| **按时间轮转** | 每天/每小时切换，保留 N 天 | 审计需求 |
| **两者结合** | 大小+时间双重触发 | 高流量生产 |

---

## 三、异常处理

### 3.1 自定义异常类设计

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    Base[AgentException<br/>所有 Agent 异常基类]

    Base --> Config[ConfigException<br/>配置错误]
    Base --> LLM[LLMException<br/>LLM 调用异常]
    Base --> Tool[ToolException<br/>工具执行异常]
    Base --> Cost[CostLimitException<br/>成本超限异常]
    Base --> Validation[ValidationException<br/>参数校验异常]

    LLM --> LLM_TO[LLMTimeoutException<br/>LLM 超时]
    LLM --> LLM_KEY[LLMAuthException<br/>认证失败]
    LLM --> LLM_RATE[LLMRateLimitException<br/>频率限制]

    Tool --> TOOL_NOT[ToolNotFoundException<br/>工具不存在]
    Tool --> TOOL_EXEC[ToolExecutionException<br/>执行失败]
```

**异常类实现**：

```python
from typing import Optional, Any


class AgentException(Exception):
    """所有 Agent 异常的基类"""

    def __init__(
        self,
        message: str,
        error_code: str = "AGENT_ERROR",
        details: Optional[dict] = None,
        recoverable: bool = False,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.recoverable = recoverable

    def to_dict(self) -> dict:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "recoverable": self.recoverable,
        }


class ConfigException(AgentException):
    """配置错误"""
    def __init__(self, message: str, config_key: str = None):
        super().__init__(
            message,
            error_code="CONFIG_ERROR",
            details={"config_key": config_key},
            recoverable=False,
        )


class LLMException(AgentException):
    """LLM 调用异常基类"""
    pass


class LLMTimeoutException(LLMException):
    """LLM 超时"""
    def __init__(self, model: str, timeout: int):
        super().__init__(
            f"LLM 调用超时:模型 {model},超时 {timeout}s",
            error_code="LLM_TIMEOUT",
            details={"model": model, "timeout": timeout},
            recoverable=True,  # 可重试
        )


class LLMAuthException(LLMException):
    """LLM 认证失败"""
    def __init__(self, provider: str):
        super().__init__(
            f"LLM 认证失败:{provider} API Key 无效",
            error_code="LLM_AUTH_ERROR",
            details={"provider": provider},
            recoverable=False,  # 不可重试,需换 Key
        )


class LLMRateLimitException(LLMException):
    """LLM 频率限制"""
    def __init__(self, provider: str, retry_after: int = 60):
        super().__init__(
            f"LLM 频率限制:{provider},请 {retry_after}s 后重试",
            error_code="LLM_RATE_LIMIT",
            details={"provider": provider, "retry_after": retry_after},
            recoverable=True,
        )


class ToolException(AgentException):
    """工具执行异常基类"""
    pass


class ToolNotFoundException(ToolException):
    """工具不存在"""
    def __init__(self, tool_name: str):
        super().__init__(
            f"工具不存在:{tool_name}",
            error_code="TOOL_NOT_FOUND",
            details={"tool_name": tool_name},
            recoverable=False,
        )


class ToolExecutionException(ToolException):
    """工具执行失败"""
    def __init__(self, tool_name: str, original_error: str):
        super().__init__(
            f"工具执行失败:{tool_name},错误:{original_error}",
            error_code="TOOL_EXECUTION_ERROR",
            details={"tool_name": tool_name, "original_error": original_error},
            recoverable=True,
        )


class CostLimitException(AgentException):
    """成本超限异常"""
    def __init__(self, used: float, budget: float):
        super().__init__(
            f"成本超限:已用 ${used:.2f},预算 ${budget:.2f}",
            error_code="COST_LIMIT_EXCEEDED",
            details={"used": used, "budget": budget},
            recoverable=False,
        )
```

### 3.2 异常捕获与恢复策略

```python
import asyncio
import functools
from typing import Callable, Type, Tuple
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep_log
)
import logging

logger = logging.getLogger(__name__)


# —— 策略一:指数退避重试(适用于可恢复异常) ——
def with_retry(
    max_attempts: int = 3,
    initial_wait: float = 1.0,
    max_wait: float = 30.0,
    retry_exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """重试装饰器"""
    def decorator(func):
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=initial_wait, max=max_wait),
            retry=retry_if_exception_type(retry_exceptions),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True,
        )
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


# —— 策略二:降级处理(主模型失败用备用模型) ——
class LLMCaller:
    """带降级的 LLM 调用器"""

    def __init__(self, primary_model: str, fallback_model: str):
        self.primary = primary_model
        self.fallback = fallback_model

    @with_retry(
        max_attempts=3,
        retry_exceptions=(LLMTimeoutException, LLMRateLimitException),
    )
    async def call(self, prompt: str) -> str:
        """调用 LLM,失败时降级"""
        try:
            return await self._call_model(self.primary, prompt)
        except (LLMAuthException, LLMTimeoutException) as e:
            logger.warning(f"主模型 {self.primary} 失败,降级到 {self.fallback}: {e}")
            return await self._call_model(self.fallback, prompt)

    async def _call_model(self, model: str, prompt: str) -> str:
        # 实际调用逻辑
        pass


# —— 策略三:工具异常容错(返回错误信息给 LLM,而非崩溃) ——
async def safe_tool_execute(tool_name: str, args: dict) -> str:
    """安全的工具执行:异常转为 LLM 可理解的消息"""
    try:
        result = await execute_tool(tool_name, args)
        return result
    except ToolNotFoundException as e:
        logger.error(f"工具不存在: {e}")
        return f"错误:工具 {tool_name} 不存在,请选择其他工具"
    except ToolExecutionException as e:
        logger.warning(f"工具执行失败: {e}")
        return f"错误:工具 {tool_name} 执行失败({e.details.get('original_error')}),请重试或换工具"
    except Exception as e:
        logger.exception(f"工具未知异常: {e}")
        return f"错误:工具 {tool_name} 发生未知异常,请联系管理员"


# —— 策略四:全局异常处理(兜底) ——
class AgentErrorHandler:
    """全局异常处理器"""

    RECOVERY_STRATEGIES = {
        LLMTimeoutException: "retry_with_backoff",
        LLMRateLimitException: "wait_and_retry",
        LLMAuthException: "switch_provider",
        ToolExecutionException: "return_error_to_llm",
        CostLimitException: "abort_and_notify",
    }

    async def handle(self, exception: AgentException, context: dict) -> dict:
        """处理异常,返回统一错误响应"""
        strategy = self.RECOVERY_STRATEGIES.get(type(exception), "abort")

        logger.error(
            f"Agent 异常: {exception.error_code} - {exception.message}",
            extra={
                "trace_id": context.get("trace_id"),
                "error_code": exception.error_code,
                "recoverable": exception.recoverable,
                "strategy": strategy,
            },
        )

        return {
            "success": False,
            "error": exception.to_dict(),
            "recovery_strategy": strategy,
            "context": context,
        }
```

### 3.3 错误上报机制

```python
import sentry_sdk
from typing import Optional


class ErrorReporter:
    """错误上报器:Sentry + 自定义上报"""

    def __init__(self, sentry_dsn: Optional[str] = None):
        if sentry_dsn:
            sentry_sdk.init(
                dsn=sentry_dsn,
                environment=os.getenv("APP_ENV", "dev"),
                traces_sample_rate=0.1,  # 10% 采样
                before_send=self._filter_sensitive,
            )

    @staticmethod
    def _filter_sensitive(event: dict, hint: dict) -> Optional[dict]:
        """过滤敏感信息后上报"""
        # 脱敏 API Key
        if "request" in event and "headers" in event["request"]:
            headers = event["request"]["headers"]
            for key in list(headers.keys()):
                if "key" in key.lower() or "auth" in key.lower():
                    headers[key] = "***"
        return event

    def report(self, exception: Exception, context: dict):
        """上报异常到 Sentry"""
        with sentry_sdk.push_scope() as scope:
            # 设置上下文
            for key, value in context.items():
                scope.set_context(key, value)
            # 设置标签
            scope.set_tag("error_code", getattr(exception, "error_code", "UNKNOWN"))
            scope.set_tag("recoverable", getattr(exception, "recoverable", False))
            # 上报
            sentry_sdk.capture_exception(exception)

    def report_cost_alert(self, used: float, budget: float):
        """成本告警"""
        if used / budget > 0.8:
            sentry_sdk.capture_message(
                f"成本告警:已用 {used}/{budget} ({used/budget*100:.0f}%)",
                level="warning",
            )
```

---

## 四、成本控制

### 4.1 循环次数限制

```python
from dataclasses import dataclass, field
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class IterationGuard:
    """循环次数限制器"""

    max_iterations: int = 8
    warning_threshold: float = 0.75  # 75% 时告警
    _current: int = 0
    _history: list = field(default_factory=list)

    def increment(self, action: str = "") -> None:
        """递增迭代计数"""
        self._current += 1
        self._history.append({"iteration": self._current, "action": action})

        # 告警阈值
        if self._current == int(self.max_iterations * self.warning_threshold):
            logger.warning(
                f"迭代次数告警:已 {self._current}/{self.max_iterations} 次",
                extra={"iteration": self._current, "max": self.max_iterations},
            )

        # 超限抛异常
        if self._current >= self.max_iterations:
            logger.error(
                f"迭代超限:{self._current}/{self.max_iterations},强制终止",
                extra={"iteration": self._current, "max": self.max_iterations},
            )
            raise CostLimitException(
                used=float(self._current),
                budget=float(self.max_iterations),
            )

    def remaining(self) -> int:
        """剩余迭代次数"""
        return max(0, self.max_iterations - self._current)

    def reset(self):
        """重置计数器"""
        self._current = 0
        self._history.clear()


# 在 Agent 循环中使用
class ReActAgent:
    def __init__(self, config: CostControlConfig):
        self.guard = IterationGuard(max_iterations=config.max_iterations)

    async def run(self, question: str) -> str:
        """带迭代限制的 Agent 执行"""
        while True:
            try:
                self.guard.increment(action="think")
                thought = await self._think(question)

                if thought.get("finish"):
                    return thought["answer"]

                self.guard.increment(action="act")
                observation = await self._act(thought["action"])
                self._update_context(observation)

            except CostLimitException:
                logger.warning("迭代超限,返回当前最佳答案")
                return await self._get_best_answer()
```

### 4.2 API 请求频率控制

```python
import asyncio
import time
from collections import deque
from typing import Optional


class RateLimiter:
    """滑动窗口频率限制器"""

    def __init__(self, max_calls: int, period: float = 60.0):
        """
        Args:
            max_calls: 时间窗口内最大调用次数
            period: 时间窗口(秒),默认 60 秒
        """
        self.max_calls = max_calls
        self.period = period
        self._calls: deque = deque()
        self._lock = asyncio.Lock()

    async def acquire(self):
        """获取调用许可(超限时等待)"""
        async with self._lock:
            now = time.monotonic()

            # 清理过期记录
            while self._calls and self._calls[0] < now - self.period:
                self._calls.popleft()

            # 超限则等待
            if len(self._calls) >= self.max_calls:
                wait_time = self._calls[0] + self.period - now
                logger.warning(f"频率限制,等待 {wait_time:.1f}s")
                await asyncio.sleep(wait_time)

            self._calls.append(time.monotonic())

    async def call_with_limit(self, func, *args, **kwargs):
        """带频率限制的函数调用"""
        await self.acquire()
        return await func(*args, **kwargs)


# 不同模型的频率限制
RATE_LIMITS = {
    "gpt-4o": RateLimiter(max_calls=500, period=60),       # 500 RPM
    "gpt-4o-mini": RateLimiter(max_calls=2000, period=60), # 2000 RPM
    "claude-3.5-sonnet": RateLimiter(max_calls=1000, period=60),
}


class RateLimitedLLMCaller:
    """带频率限制的 LLM 调用器"""

    def __init__(self, model: str):
        self.model = model
        self.rate_limiter = RATE_LIMITS.get(model, RateLimiter(max_calls=100))

    async def call(self, prompt: str) -> str:
        """带频率控制的 LLM 调用"""
        await self.rate_limiter.acquire()
        return await self._raw_call(prompt)

    async def _raw_call(self, prompt: str) -> str:
        # 实际 LLM 调用
        pass
```

### 4.3 模型选择策略

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    Input[用户输入] --> Analyze[任务复杂度分析]
    Analyze --> Q1{输入长度?}

    Q1 -->|短(<100字)| Simple[简单任务]
    Q1 -->|长(≥100字)| Q2{需工具调用?}

    Simple --> Mini[用 mini 模型<br/>gpt-4o-mini<br/>$0.15/1M tokens]
    Q2 -->|是| Complex[复杂任务]
    Q2 -->|否| Medium[中等任务]

    Medium --> Sonnet[用中档模型<br/>gpt-4o<br/>$2.5/1M tokens]
    Complex --> Pro[用旗舰模型<br/>gpt-4o<br/>或 claude-3.5-sonnet]

    style Mini fill:#e8f5e9,stroke:#2e7d32
    style Sonnet fill:#fff3e0,stroke:#e65100
    style Pro fill:#ffcdd2,stroke:#c62828
```

**模型选择实现**：

```python
from typing import Dict
from dataclasses import dataclass


@dataclass
class ModelConfig:
    name: str
    input_price: float   # $/1M tokens
    output_price: float  # $/1M tokens
    max_tokens: int
    capability: str      # simple/medium/complex


# 模型成本表(2025 年价格)
MODEL_CATALOG: Dict[str, ModelConfig] = {
    "gpt-4o-mini": ModelConfig("gpt-4o-mini", 0.15, 0.60, 128000, "simple"),
    "gpt-4o": ModelConfig("gpt-4o", 2.50, 10.00, 128000, "complex"),
    "claude-3.5-sonnet": ModelConfig("claude-3.5-sonnet", 3.00, 15.00, 200000, "complex"),
    "claude-3-haiku": ModelConfig("claude-3-haiku", 0.25, 1.25, 200000, "simple"),
}


class ModelSelector:
    """智能模型选择器"""

    def __init__(self, catalog: Dict[str, ModelConfig] = MODEL_CATALOG):
        self.catalog = catalog

    def select(self, task: dict) -> str:
        """根据任务复杂度选择模型"""
        complexity = self._analyze_complexity(task)

        # 按能力匹配最便宜的模型
        candidates = [m for m in self.catalog.values() if m.capability == complexity]
        candidates.sort(key=lambda m: m.input_price)
        return candidates[0].name if candidates else "gpt-4o-mini"

    def _analyze_complexity(self, task: dict) -> str:
        """分析任务复杂度"""
        input_length = len(task.get("input", ""))
        needs_tools = bool(task.get("required_tools"))
        needs_reasoning = task.get("requires_reasoning", False)

        if needs_tools or needs_reasoning:
            return "complex"
        elif input_length > 100:
            return "medium"
        else:
            return "simple"
```

### 4.4 缓存重复请求

```python
import hashlib
import json
import time
from typing import Optional, Any
import redis.asyncio as aioredis
import functools


class ResponseCache:
    """LLM 响应缓存:Redis 后端"""

    def __init__(self, redis_url: str = "redis://localhost:6379", ttl: int = 3600):
        self.redis = aioredis.from_url(redis_url)
        self.ttl = ttl

    def _make_key(self, model: str, prompt: str, **kwargs) -> str:
        """生成缓存 Key"""
        content = json.dumps(
            {"model": model, "prompt": prompt, "kwargs": kwargs},
            sort_keys=True, ensure_ascii=False
        )
        return f"llm_cache:{hashlib.md5(content.encode()).hexdigest()}"

    async def get(self, model: str, prompt: str, **kwargs) -> Optional[str]:
        """获取缓存"""
        key = self._make_key(model, prompt, **kwargs)
        cached = await self.redis.get(key)
        if cached:
            logger.debug(f"缓存命中: {key}")
            return cached.decode()
        return None

    async def set(self, model: str, prompt: str, response: str, **kwargs):
        """写入缓存"""
        key = self._make_key(model, prompt, **kwargs)
        await self.redis.setex(key, self.ttl, response)
        logger.debug(f"缓存写入: {key}, TTL={self.ttl}s")


class CachedLLMCaller:
    """带缓存的 LLM 调用器"""

    def __init__(self, cache: ResponseCache):
        self.cache = cache

    async def call(self, model: str, prompt: str, **kwargs) -> str:
        """带缓存的 LLM 调用"""
        # 1. 查缓存
        cached = await self.cache.get(model, prompt, **kwargs)
        if cached:
            return cached

        # 2. 实际调用
        response = await self._raw_call(model, prompt, **kwargs)

        # 3. 写缓存(仅缓存确定性输出,temperature=0)
        if kwargs.get("temperature", 0) == 0:
            await self.cache.set(model, prompt, response, **kwargs)

        return response

    async def _raw_call(self, model, prompt, **kwargs):
        pass
```

**缓存策略**：

| 策略 | 做法 | 适用场景 |
|------|------|----------|
| **相同输入缓存** | 相同 prompt+model+params 命中缓存 | FAQ、固定模板 |
| **语义相似缓存** | 向量相似度 > 0.95 命中 | 用户改述同一问题 |
| **TTL 过期** | 缓存 1 小时自动失效 | 时效性数据 |
| **仅缓存 temperature=0** | 非确定性输出不缓存 | 避免缓存错误 |

### 4.5 资源使用优化方案

```python
class CostTracker:
    """成本追踪器"""

    def __init__(self, daily_budget: float):
        self.daily_budget = daily_budget
        self.used = 0.0
        self.calls = 0
        self._start_time = time.time()

    def record(self, model: str, input_tokens: int, output_tokens: int):
        """记录一次调用成本"""
        config = MODEL_CATALOG.get(model)
        if not config:
            return

        cost = (
            input_tokens / 1_000_000 * config.input_price
            + output_tokens / 1_000_000 * config.output_price
        )

        self.used += cost
        self.calls += 1

        logger.info(
            f"LLM 调用: {model}, tokens={input_tokens}+{output_tokens}, cost=${cost:.4f}",
            extra={
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost,
                "total_used": self.used,
                "total_budget": self.daily_budget,
            }
        )

        # 预算检查
        if self.used >= self.daily_budget:
            raise CostLimitException(used=self.used, budget=self.daily_budget)

        # 80% 告警
        if self.used >= self.daily_budget * 0.8:
            logger.warning(
                f"预算告警:已用 ${self.used:.2f}/${self.daily_budget:.2f} "
                f"({self.used/self.daily_budget*100:.0f}%)"
            )

    def summary(self) -> dict:
        """成本汇总"""
        return {
            "total_cost": self.used,
            "budget": self.daily_budget,
            "remaining": self.daily_budget - self.used,
            "total_calls": self.calls,
            "avg_cost_per_call": self.used / max(self.calls, 1),
        }
```

**综合优化方案**：

| 优化维度 | 方案 | 节省效果 |
|----------|------|----------|
| **模型分级** | 简单任务用 mini | 成本降 90% |
| **缓存** | 相同请求缓存 | 重复调用零成本 |
| **频率控制** | 防止突发调用 | 避免限流罚款 |
| **迭代限制** | 防死循环 | 单任务成本上限 |
| **Token 优化** | Prompt 精简、历史压缩 | Token 降 30% |
| **预算监控** | 实时成本追踪 | 防超支 |
| **批处理** | 多请求合并 | 减少 API 调用次数 |

---

## 五、最佳实践指南

### 5.1 配置管理最佳实践

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    subgraph 配置管理清单
        C1[1. 配置与代码分离]
        C2[2. 敏感信息用环境变量]
        C3[3. 多环境配置文件]
        C4[4. Pydantic 校验配置]
        C5[5. .env 不入库]
        C6[6. 生产用 Vault/KMS]
    end
```

| 实践 | 说明 |
|------|------|
| ✅ 配置与代码分离 | 配置在 yaml/.env，代码只读取 |
| ✅ Pydantic 校验 | 配置加载时校验类型与必填 |
| ✅ 敏感信息环境变量 | API Key 通过 `os.getenv` 注入 |
| ✅ .env 加入 .gitignore | 防止泄露 |
| ✅ 提供 .env.example | 引导新成员配置 |
| ✅ 生产用密钥管理服务 | Vault/AWS Secrets Manager |
| ❌ 硬编码 API Key | 永远不要 |
| ❌ 提交 .env 到 git | 永远不要 |

### 5.2 日志最佳实践

| 实践 | 说明 |
|------|------|
| ✅ 结构化 JSON 日志 | 便于 ELK/Loki 检索 |
| ✅ trace_id 贯穿全链路 | 跨函数/跨 Agent 追踪 |
| ✅ 日志轮转 | 防止磁盘满 |
| ✅ 错误日志单独文件 | 快速定位问题 |
| ✅ 敏感信息脱敏 | Key/密码不进日志 |
| ❌ 日志记录完整 Prompt | 太长且可能含敏感信息(截断记录) |
| ❌ 用 print 代替 logger | 无级别无格式无轮转 |

### 5.3 异常处理最佳实践

| 实践 | 说明 |
|------|------|
| ✅ 自定义异常层次结构 | 精确区分错误类型 |
| ✅ 区分可恢复/不可恢复 | 可恢复重试，不可恢复上报 |
| ✅ 工具异常返回给 LLM | 让 LLM 调整策略而非崩溃 |
| ✅ 全局兜底处理器 | 防止未捕获异常导致服务挂 |
| ✅ Sentry 上报 | 生产异常可观测 |
| ❌ 裸 except Exception | 吞掉异常难排查 |
| ❌ 异常后不记录日志 | 问题无法追溯 |

### 5.4 成本控制最佳实践

| 实践 | 说明 |
|------|------|
| ✅ 模型分级路由 | 简单用 mini，复杂用旗舰 |
| ✅ 缓存重复请求 | 相同输入零成本 |
| ✅ 迭代次数硬限制 | 防死循环 |
| ✅ 频率限制 | 防 API 限流 |
| ✅ 实时成本追踪 | 防超支 |
| ✅ 预算告警 | 80% 时告警 |
| ❌ 所有任务用旗舰模型 | 成本爆炸 |
| ❌ 不缓存直接调用 | 重复浪费 |

---

## 六、常见问题解决方案

### 6.1 配置相关问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `API Key 为 None` | 环境变量未设置 | 检查 .env 文件，确认 `load_dotenv()` 已调用 |
| 配置不生效 | 优先级覆盖 | 检查环境变量 > .env > yaml 优先级 |
| 生产环境泄露 Key | .env 提交到 git | ①从 git 历史删除 ②轮换 Key ③改用 Vault |

### 6.2 日志相关问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 日志文件过大 | 未配置轮转 | 用 `RotatingFileHandler` |
| 日志中含 API Key | 未脱敏 | 用 `mask_secrets_in_text` |
| 日志找不到 trace_id | 未注入适配器 | 用 `AgentLoggerAdapter` |
| JSON 日志无法解析 | 格式错误 | 用 `JsonFormatter` 标准化 |

### 6.3 异常相关问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| Agent 偶发崩溃 | 未捕获异常 | 加全局兜底处理器 |
| 工具异常导致整个任务失败 | 异常未隔离 | 用 `safe_tool_execute` 包装 |
| LLM 超时频繁 | 未设超时或重试 | 配置 timeout + 指数退避重试 |
| 重试导致重复副作用 | 幂等性未保证 | 工具执行加 request_id 去重 |

### 6.4 成本相关问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 月账单超预期 | 无成本追踪 | 接入 `CostTracker` 实时监控 |
| 简单任务成本高 | 全用旗舰模型 | 模型分级路由 |
| 重复请求浪费 | 无缓存 | 接入 `ResponseCache` |
| Agent 死循环 | 无迭代限制 | 配置 `IterationGuard` |
| API 频率超限 | 无频率控制 | 接入 `RateLimiter` |

---

## 七、总结

| 模块 | 核心实践 | 关键工具 |
|------|----------|----------|
| **环境变量管理** | 分层配置 + 敏感信息隔离 | Pydantic + python-dotenv + YAML |
| **日志记录管理** | 结构化 JSON + 轮转 + trace_id | logging + RotatingFileHandler |
| **异常处理** | 自定义异常层次 + 重试降级 + 全局兜底 | tenacity + Sentry |
| **成本控制** | 模型分级 + 缓存 + 迭代限制 + 频率控制 | CostTracker + RateLimiter + ResponseCache |

**工程化口诀**：
> **配置分层不泄露，日志结构带追踪，异常分类可恢复，成本监控防超支。**
