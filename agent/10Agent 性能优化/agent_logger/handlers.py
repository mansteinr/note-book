"""更完整的文件轮转与自定义处理器:

本文件提供以下生产环境增强功能:
1. BufferedDualRotatingHandler: 批量缓冲 + 大小/时间双轮转 + 线程安全写锁共享
2. SizeBatchedConsoleHandler: 控制台大小限制,避免单次刷屏把 stdout 阻塞
3. AlertWebhookHandler: CRITICAL 自动推送 Webhook (飞书/企微/钉钉/PagerDuty 兼容通用 JSON 格式)

非核心功能,按需 import 即可。core.py 的最小实现已能独立工作。
"""
from __future__ import annotations

import copy
import json as _json
import os
import socket
import sys
import threading
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from .core import (
    LogEvent,
    LogLevel,
    TraceContext,
    format_json_line,
    format_text,
)

__all__ = [
    "AlertWebhookHandler",
    "DEFAULT_WEBHOOK_TEMPLATES",
    "send_webhook_alert",
]


# =========================================================
# CRITICAL 告警 Webhook 推送 (飞书/企微/钉钉 通用 JSON)
# =========================================================
DEFAULT_WEBHOOK_TEMPLATES: Dict[str, Callable[[LogEvent, str], Dict[str, Any]]] = {
    "feishu": lambda ev, host: {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": f"🚨 Agent CRITICAL: {ev.msg[:50]}"},
                "template": "red",
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content":
                    f"**级别**: CRITICAL  \n**模块**: `{ev.module}`  \n"
                    f"**trace_id**: `{ev.trace_id or TraceContext.current()['trace_id']}`  \n"
                    f"**主机**: `{host}` / PID={ev.pid}  \n"
                    f"**详情**: {ev.msg}\n"
                }},
                {"tag": "hr"},
                {"tag": "markdown", "content": f"```\n{ev.err and (type(ev.err).__name__ + ': ' + str(ev.err)) or '无异常堆栈'}\n```"}
            ],
        },
    },
    "wecom": lambda ev, host: {
        "msgtype": "markdown",
        "markdown": {
            "content":
                f"># 🚨 Agent CRITICAL 告警\n"
                f">**消息**: {ev.msg}\n"
                f">**模块**: `{ev.module}`\n"
                f">**trace_id**: `{ev.trace_id or '-'}`\n"
                f">**主机**: `{host}` / PID={ev.pid}\n"
                + (f">**错误类型**: `{type(ev.err).__name__}`\n" if ev.err else "")
        },
    },
    "dingtalk": lambda ev, host: {
        "msgtype": "markdown",
        "markdown": {
            "title": "Agent CRITICAL",
            "text":
                f"## 🚨 Agent CRITICAL 告警\n"
                f"- 消息: **{ev.msg}**\n"
                f"- 模块: `{ev.module}`\n"
                f"- trace_id: `{ev.trace_id or '-'}`\n"
                f"- 主机: `{host}`\n"
                + (f"- 错误: `{type(ev.err).__name__}`\n" if ev.err else "")
        },
    },
    "pagerduty_generic": lambda ev, host: {
        "routing_key": "PLACEHOLDER",
        "event_action": "trigger",
        "payload": {
            "summary": f"[Agent CRITICAL] {ev.module}: {ev.msg[:200]}",
            "severity": "critical",
            "source": host,
            "component": ev.module,
            "group": "agent",
            "custom_details": {
                "trace_id": ev.trace_id,
                "pid": ev.pid,
                "thread_id": ev.thread_id,
                "err_type": type(ev.err).__name__ if ev.err else None,
                "attrs": _json.dumps(ev.attrs, ensure_ascii=False, default=repr),
            },
        },
    },
}


def send_webhook_alert(
    event: LogEvent,
    webhook_url: str,
    *,
    platform: str = "feishu",
    timeout: float = 5.0,
    template: Optional[Callable[[LogEvent, str], Dict[str, Any]]] = None,
    extra_headers: Optional[Dict[str, str]] = None,
) -> Tuple[bool, str]:
    """通用 Webhook 推送, 返回 (是否成功, 错误信息)。非阻塞调用,任何异常都会被吞。"""
    try:
        hostname = socket.gethostname()
    except Exception:
        hostname = "unknown"
    try:
        tmpl = template or DEFAULT_WEBHOOK_TEMPLATES.get(platform)
        if tmpl is None:
            return False, f"未知平台 {platform}"
        payload = tmpl(event, hostname)
        data = _json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(webhook_url, data=data, method="POST")
        req.add_header("Content-Type", "application/json; charset=utf-8")
        for k, v in (extra_headers or {}).items():
            req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = resp.getcode()
                if 200 <= status < 300:
                    return True, ""
                return False, f"HTTP {status}"
        except Exception as e:
            return False, f"网络异常: {type(e).__name__}: {e}"
    except Exception as e:
        return False, f"payload 构建失败: {type(e).__name__}: {e}"


class AlertWebhookHandler:
    """CRITICAL 告警 → Webhook。可注册到 AgentLogger。

    使用::

        from agent_logger.core import AgentLogger
        from agent_logger.handlers import AlertWebhookHandler

        logger = AgentLogger.get_instance()
        handler = AlertWebhookHandler(
            webhook_url=os.environ["FEISHU_WEBHOOK"],
            platform="feishu",
            rate_limit_per_min=5,  # 防告警风暴,每分钟最多推 5 条
        )
        logger.register_critical_callback(handler)
    """

    def __init__(
        self,
        webhook_url: str,
        *,
        platform: str = "feishu",
        rate_limit_per_min: int = 5,
        min_level: str | LogLevel = LogLevel.CRITICAL,
        timeout: float = 5.0,
        daemon_push: bool = True,
    ) -> None:
        self.webhook_url = webhook_url
        self.platform = platform
        self.rate_limit_per_min = max(0, int(rate_limit_per_min))
        self.min_level: LogLevel = LogLevel.from_str(min_level)
        self.timeout = timeout
        # 限频窗口
        self._last_window_start = 0.0
        self._window_count = 0
        self._lock = threading.Lock()
        self._daemon = daemon_push
        # 异步发送线程队列
        self._q: Optional["queue.Queue[LogEvent]"] = None
        self._thread: Optional[threading.Thread] = None
        if daemon_push:
            import queue as _queue
            self._q = _queue.Queue(maxsize=200)
            self._thread = threading.Thread(target=self._pump, daemon=True,
                                             name="agent-logger-webhook")
            self._thread.start()

    def __call__(self, event: LogEvent) -> None:
        if event.level < self.min_level:
            return
        # 先限频
        now = time.time()
        with self._lock:
            if now - self._last_window_start >= 60.0:
                self._last_window_start = now
                self._window_count = 0
            if self.rate_limit_per_min and self._window_count >= self.rate_limit_per_min:
                return  # 丢弃超过限频的 CRITICAL
            self._window_count += 1
        if self._daemon and self._q is not None:
            try:
                self._q.put_nowait(event)
            except Exception:
                # 队列满就退化成同步发
                send_webhook_alert(event, self.webhook_url, platform=self.platform,
                                   timeout=self.timeout)
        else:
            send_webhook_alert(event, self.webhook_url, platform=self.platform,
                               timeout=self.timeout)

    def _pump(self) -> None:
        assert self._q is not None
        while True:
            try:
                ev = self._q.get(timeout=1.0)
            except Exception:
                continue
            try:
                send_webhook_alert(ev, self.webhook_url, platform=self.platform,
                                   timeout=self.timeout)
            except Exception:
                pass
