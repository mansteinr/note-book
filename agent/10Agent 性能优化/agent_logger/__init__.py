"""Agent 结构化日志系统包 (零第三方依赖)。

快速开始
=========

```python
from agent_logger import AgentLogger, TraceContext, get_logger
from agent_logger.query import LogQuerier, LogAnalyzer

# 初始化
logger = get_logger("./logs", default_level="INFO")

# 打日志
logger.info("用户登录", user_id="u123")
logger.warning("LLM 重试中", 重试次数=2)
try:
    1/0
except:
    logger.error("失败", 模块="module_a")  # 自动捕获异常堆栈

# trace_id 全链路串联 (线程/协程安全)
with TraceContext.trace("req-abc", span_id="planner-01"):
    with logger.timed("LLM 完成", 模型="gpt-4o"):
        call_llm(...)

# 查询
rows = (LogQuerier("./logs")
    .trace_id("req-abc")
    .level_ge("WARNING")
    .time_range(last_seconds=3600)
    .limit(100)
    .run().to_list())

# 统计
print(LogAnalyzer("./logs").level_distribution())
```

模块文件
=========
- `core.py`      : 核心门面 AgentLogger / 级别 / TraceContext / 环形缓冲 / 双轮转 / 格式化
- `query.py`     : 查询与统计 API (LogQuerier / LogAnalyzer)
- `handlers.py`  : 生产级 Alert Webhook (飞书/企微/钉钉/PagerDuty)、可选增强 Handler
- `example.py`   : 端到端使用演示 (`python -m agent_logger.example`)
- `test_agent_logger.py` : 9 大类 50+ 用例 (`python -m agent_logger.test_agent_logger`)
"""
from .core import (
    AgentLogger,
    AsyncRingBuffer,
    ConsoleHandler,
    DualRotatingFileHandler,
    LogEvent,
    LogLevel,
    TraceContext,
    format_json_line,
    format_text,
    get_logger,
)

__all__ = [
    "AgentLogger",
    "LogLevel",
    "LogEvent",
    "TraceContext",
    "AsyncRingBuffer",
    "DualRotatingFileHandler",
    "ConsoleHandler",
    "get_logger",
    "format_text",
    "format_json_line",
]

__version__ = "1.0.0"
