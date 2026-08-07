"""Agent 日志系统包。

核心组件:
    - AgentLogger: 单例门面, 对外 5 级 API 主入口
    - TraceContext: 全链路追踪上下文 (线程/协程安全 contextvars)
    - LogLevel / LogEvent: 级别枚举与事件数据类
    - AsyncRingBuffer: 有界环形队列 + 后台批量 flush 线程

配套文件:
    - handlers.py: 双轮转处理器 + 双格式 Formatter
    - query.py:    日志查询分析 API (LogQuerier / LogAnalyzer)
    - example.py:  使用示例
    - test_agent_logger.py: 单元测试
"""
from __future__ import annotations

import atexit
import contextvars
import enum
import gzip
import importlib.util
import os
import queue
import random
import shutil
import string
import sys
import threading
import time
import traceback
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

# ============================================================
# 0. 级别的标准定义
# ============================================================
class LogLevel(enum.IntEnum):
    """五级标准日志级别,数值对齐 Python logging,保持兼容习惯。"""

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

    @classmethod
    def from_str(cls, s: Union[str, int, "LogLevel"]) -> "LogLevel":
        if isinstance(s, LogLevel):
            return s
        if isinstance(s, int):
            for lv in cls:
                if lv.value == s:
                    return lv
            raise ValueError(f"未知级别数值: {s}")
        mapping = {
            "DEBUG": cls.DEBUG,
            "INFO": cls.INFO,
            "WARN": cls.WARNING,
            "WARNING": cls.WARNING,
            "ERROR": cls.ERROR,
            "FATAL": cls.CRITICAL,
            "CRIT": cls.CRITICAL,
            "CRITICAL": cls.CRITICAL,
        }
        try:
            return mapping[str(s).strip().upper()]
        except KeyError as e:
            raise ValueError(f"未知级别字符串: {s}") from e


# ============================================================
# 1. 日志事件数据类
# ============================================================
@dataclass
class LogEvent:
    """一条日志事件的结构化数据。"""

    ts: float  # time.time() 秒 (float)
    level: LogLevel
    module: str
    msg: str
    args: Tuple[Any, ...] = ()
    attrs: Dict[str, Any] = field(default_factory=dict)
    trace_id: str = ""
    span_id: str = ""
    user_id: str = ""
    session_id: str = ""
    duration_ms: Optional[float] = None
    err: Optional[BaseException] = None
    host: str = field(default_factory=lambda: _HOSTNAME)
    pid: int = field(default_factory=lambda: os.getpid())
    thread_id: int = field(default_factory=lambda: threading.get_ident())

    # ---- 便捷方法 (不抛异常, 遵循 P6) ----
    def safe_msg(self) -> str:
        """带 args 的懒格式化,失败时回退原始 msg + repr(args)。"""
        try:
            if self.args:
                return self.msg.format(*self.args)
            return self.msg
        except Exception:
            try:
                return self.msg + " [args=" + repr(self.args) + "]"
            except Exception:
                return self.msg or ""


# ============================================================
# 2. 全局常量 & 上下文 (contextvars 线程/协程安全)
# ============================================================
try:
    _HOSTNAME: str = os.environ.get("AGENT_HOST", "") or os.uname().nodename  # type: ignore[attr-defined]
except Exception:
    try:
        import socket
        _HOSTNAME = socket.gethostname()
    except Exception:
        _HOSTNAME = "unknown-host"


_CONTEXT_TRACE_ID: contextvars.ContextVar[str] = contextvars.ContextVar(
    "agent_log_trace_id", default=""
)
_CONTEXT_SPAN_ID: contextvars.ContextVar[str] = contextvars.ContextVar(
    "agent_log_span_id", default=""
)
_CONTEXT_USER_ID: contextvars.ContextVar[str] = contextvars.ContextVar(
    "agent_log_user_id", default=""
)
_CONTEXT_SESSION_ID: contextvars.ContextVar[str] = contextvars.ContextVar(
    "agent_log_session_id", default=""
)


class TraceContext:
    """全链路追踪上下文管理器,使用 contextvars,线程和 asyncio 协程都安全。

    使用示例::

        with TraceContext.trace("req-abc123", span_id="plan-01", user_id="u1"):
            logger.info("收到请求")          # 自动携带 trace_id
            with TraceContext.trace(span_id="llm-02"):   # 继承外层 trace_id
                logger.info("LLM 调用")      # trace_id=req-abc123, span_id=llm-02
    """

    @staticmethod
    @contextmanager
    def trace(
        trace_id: Optional[str] = None,
        *,
        span_id: str = "",
        user_id: str = "",
        session_id: str = "",
    ) -> Generator[Dict[str, str], None, None]:
        tokens: list[Any] = []
        current = TraceContext.current()

        # trace_id 未传时, 继承当前; 传了就覆盖
        new_trace = trace_id if trace_id else current["trace_id"] or _gen_trace_id()
        new_span = span_id if span_id else current["span_id"]
        new_user = user_id if user_id else current["user_id"]
        new_session = session_id if session_id else current["session_id"]

        tokens.append(_CONTEXT_TRACE_ID.set(new_trace))
        tokens.append(_CONTEXT_SPAN_ID.set(new_span))
        tokens.append(_CONTEXT_USER_ID.set(new_user))
        tokens.append(_CONTEXT_SESSION_ID.set(new_session))
        try:
            yield {
                "trace_id": new_trace,
                "span_id": new_span,
                "user_id": new_user,
                "session_id": new_session,
            }
        finally:
            try:
                _CONTEXT_TRACE_ID.reset(tokens[0])
                _CONTEXT_SPAN_ID.reset(tokens[1])
                _CONTEXT_USER_ID.reset(tokens[2])
                _CONTEXT_SESSION_ID.reset(tokens[3])
            except Exception:
                # P6: 上下文 reset 失败不影响业务
                pass

    @staticmethod
    def current() -> Dict[str, str]:
        return {
            "trace_id": _CONTEXT_TRACE_ID.get(),
            "span_id": _CONTEXT_SPAN_ID.get(),
            "user_id": _CONTEXT_USER_ID.get(),
            "session_id": _CONTEXT_SESSION_ID.get(),
        }


def _gen_trace_id() -> str:
    """生成默认 trace_id: req-{8字节hex}"""
    return "req-" + uuid.uuid4().hex[:12]


# ============================================================
# 3. 异步环形缓冲 (P1 / P7 核心机制)
# ============================================================
class AsyncRingBuffer:
    """有界环形缓冲队列, 批量 flush 到下游 handlers。

    设计要点:
        - 容量固定 (默认 10000),绝不 OOM。
        - 高水位分级丢弃: DEBUG → INFO → WARNING, ERROR+ 始终保留(走紧急通道)。
        - 后台线程批量出队 + 批量写入,降低 syscall 次数。
    """

    LEVEL_DROP_ORDER: List[LogLevel] = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING]

    def __init__(
        self,
        capacity: int = 10000,
        flush_batch_size: int = 200,
        flush_interval_ms: float = 250.0,
        handler_fn: Optional[Callable[[List[LogEvent]], None]] = None,
        daemon: bool = True,
    ) -> None:
        self.capacity = capacity
        self.flush_batch_size = max(1, flush_batch_size)
        self.flush_interval_s = max(0.001, flush_interval_ms / 1000.0)

        self._q: "queue.Queue[LogEvent]" = queue.Queue(maxsize=capacity)
        self._handler_fn = handler_fn
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._daemon = daemon
        self._lock = threading.Lock()

        # 指标
        self._total_enqueued = 0
        self._total_dropped = {lv.name: 0 for lv in LogLevel}

    # ---------- 对外 API ----------
    def start(self) -> None:
        """启动后台 flush 线程。重复调用安全。"""
        with self._lock:
            if self._thread and self._thread.is_alive():
                return
            self._stop.clear()
            self._thread = threading.Thread(
                target=self._run, name="agent-logger-flush", daemon=self._daemon
            )
            self._thread.start()

    def enqueue(self, event: LogEvent) -> bool:
        """事件入队。返回 True=成功入队, False=被丢弃(背压)。

        注意: ERROR/CRITICAL 永远不应调用这个方法,它们走同步紧急通道。
        """
        # 快速路径: queue 没满直接塞
        try:
            self._q.put_nowait(event)
            self._total_enqueued += 1
            return True
        except queue.Full:
            pass

        # 背压分级丢弃: 从最轻微等级开始丢, 腾出位置
        for drop_lv in self.LEVEL_DROP_ORDER:
            if event.level > drop_lv:
                continue
            # 当前事件属于这个可以丢的级别, 直接丢
            self._total_dropped[drop_lv.name] += 1
            return False

        # 级别比所有可丢弃级别都高(WARNNING以上,但还不是ERROR/CRITICAL)
        # 还是尝试阻塞极短时间, 给 flush 线程机会
        try:
            self._q.put(event, timeout=0.002)
            self._total_enqueued += 1
            return True
        except queue.Full:
            self._total_dropped.setdefault(event.level.name, 0)
            self._total_dropped[event.level.name] += 1
            return False

    @property
    def qsize(self) -> int:
        return self._q.qsize()

    @property
    def dropped_stats(self) -> Dict[str, int]:
        return dict(self._total_dropped)

    def drain_all(self, timeout: float = 5.0) -> None:
        """尽可能把队列中的所有事件 flush 完。"""
        deadline = time.time() + timeout
        batch: List[LogEvent] = []
        while time.time() < deadline:
            try:
                ev = self._q.get_nowait()
                batch.append(ev)
                if len(batch) >= self.flush_batch_size:
                    self._safe_handle_batch(batch)
                    batch = []
            except queue.Empty:
                break
        if batch:
            self._safe_handle_batch(batch)

    def shutdown(self, timeout: float = 5.0) -> None:
        self._stop.set()
        t = self._thread
        if t:
            t.join(timeout=timeout)
        self.drain_all(timeout=min(timeout, 1.0))

    # ---------- 内部 ----------
    def _run(self) -> None:
        last_flush = time.time()
        batch: List[LogEvent] = []
        while not self._stop.is_set():
            try:
                ev = self._q.get(timeout=0.01)
                batch.append(ev)
            except queue.Empty:
                ev = None

            now = time.time()
            time_up = (now - last_flush) >= self.flush_interval_s
            batch_full = len(batch) >= self.flush_batch_size

            if (time_up or batch_full) and batch:
                self._safe_handle_batch(batch)
                batch = []
                last_flush = now

        # 退出前清理残余
        if batch:
            self._safe_handle_batch(batch)

    def _safe_handle_batch(self, batch: List[LogEvent]) -> None:
        if not self._handler_fn:
            return
        try:
            self._handler_fn(batch)
        except Exception:
            # P6: handlers 绝对不能把异常回抛到业务或 flush 线程
            # 此时退化成 stderr 打印,避免死循环
            try:
                print(f"[agent-logger] handler 异常,丢弃 {len(batch)} 条",
                      file=sys.stderr)
            except Exception:
                pass


# ============================================================
# 4. 格式化 + 处理器 (精简版 handlers 内嵌实现)
# ============================================================
_ANSI = {
    LogLevel.DEBUG: "\x1b[90m",
    LogLevel.INFO: "\x1b[32m",
    LogLevel.WARNING: "\x1b[33m",
    LogLevel.ERROR: "\x1b[1;31m",
    LogLevel.CRITICAL: "\x1b[1;41;37m",
}
_ANSI_RESET = "\x1b[0m"

_LEVEL_SHORT = {
    LogLevel.DEBUG: "DEBUG",
    LogLevel.INFO: "INFO",
    LogLevel.WARNING: "WARN",
    LogLevel.ERROR: "ERROR",
    LogLevel.CRITICAL: "CRIT",
}

_TZ_BJ = timezone(timedelta(hours=8))


def _format_ts(ts: float) -> str:
    """格式化为 YYYY-MM-DD HH:MM:SS.mmm"""
    dt = datetime.fromtimestamp(ts, tz=_TZ_BJ)
    return dt.strftime("%Y-%m-%d %H:%M:%S.") + f"{dt.microsecond // 1000:03d}"


def _format_ts_iso(ts: float) -> str:
    dt = datetime.fromtimestamp(ts, tz=_TZ_BJ)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}+08:00"


def _safe_repr(v: Any) -> str:
    """把值转成可嵌入 k=v 空格分隔格式的字符串,空格自动引号。"""
    try:
        s = str(v)
    except Exception:
        return "<repr_err>"
    if any(c.isspace() for c in s) or (s and s[0] in ('"', "'")):
        # JSON-like 双引号
        escaped = s.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return s


def _import_json():
    """延迟 import json,关闭 DEBUG 时不需要 json 模块。"""
    import json  # noqa: WPS433
    return json


def format_text(event: LogEvent, *, use_color: bool) -> str:
    """Text 人类可读格式化 (P6: 永不抛异常)。"""
    try:
        lv_short = _LEVEL_SHORT.get(event.level, "?????")
        prefix_color = _ANSI.get(event.level, "") if use_color else ""
        suffix_color = _ANSI_RESET if use_color else ""

        ts = _format_ts(event.ts)
        module = event.module or "agent.unknown"
        if len(module) > 20:
            module_display = module[:17] + "..."
        else:
            module_display = module.ljust(20)

        ctx = TraceContext.current()
        trace_id = event.trace_id or ctx["trace_id"] or "NO_TRACE"
        span_id = event.span_id or ctx["span_id"] or "-"

        # 自定义 attrs k=v
        parts: List[str] = []
        for k, v in (event.attrs or {}).items():
            parts.append(f"{k}={_safe_repr(v)}")
        if event.duration_ms is not None:
            parts.append(f"dur_ms={event.duration_ms:.2f}" if isinstance(event.duration_ms, float)
                         else f"dur_ms={event.duration_ms}")
        user = event.user_id or ctx["user_id"]
        if user:
            parts.append(f"user={user}")
        attr_str = ("  " + " ".join(parts)) if parts else ""

        message = prefix_color + event.safe_msg() + suffix_color

        header = (f"{prefix_color}{ts} [{lv_short:<7}]{suffix_color} "
                  f"[{module_display}] trace={trace_id} span={span_id}{attr_str}  {message}")

        if event.err:
            try:
                tb = "".join(traceback.format_exception(
                    type(event.err), event.err, event.err.__traceback__
                ))
                header += "\n" + tb.rstrip()
            except Exception:
                header += "\n<traceback format error>"
        return header
    except Exception:
        # P6 最后兜底:哪怕格式化全崩,也要尽力输出
        try:
            return f"{time.time():.3f} [LOG_FMT_ERR] {repr(event.msg)}"
        except Exception:
            return ""


def format_json_line(event: LogEvent) -> str:
    """JSON 单行格式,字段完整 (P6: 永不抛异常)。"""
    json = _import_json()
    ctx = TraceContext.current()
    trace_id = event.trace_id or ctx["trace_id"] or "NO_TRACE"
    span_id = event.span_id or ctx["span_id"] or ""
    user_id = event.user_id or ctx["user_id"] or ""
    session_id = event.session_id or ctx["session_id"] or ""

    d: Dict[str, Any] = {
        "ts": _format_ts_iso(event.ts),
        "ts_epoch": round(event.ts, 6),
        "level": event.level.name,
        "module": event.module or "agent.unknown",
        "trace_id": trace_id,
        "span_id": span_id,
        "user_id": user_id,
        "session_id": session_id,
        "host": event.host or "UNKNOWN",
        "pid": event.pid,
        "thread_id": event.thread_id,
        "msg": event.safe_msg(),
    }
    if event.attrs:
        try:
            clean_attrs = {}
            for k, v in event.attrs.items():
                try:
                    json.dumps({k: v})  # 可序列化性测试
                    clean_attrs[k] = v
                except Exception:
                    clean_attrs[k] = repr(v)
            d["attrs"] = clean_attrs
        except Exception:
            d["attrs"] = {}
    if event.duration_ms is not None:
        d["duration_ms"] = round(float(event.duration_ms), 3)
    if event.err:
        d["err_type"] = type(event.err).__name__
        d["err_msg"] = str(event.err)
        try:
            d["err_stack"] = "".join(traceback.format_exception(
                type(event.err), event.err, event.err.__traceback__
            ))
        except Exception:
            d["err_stack"] = "<traceback unavailable>"

    try:
        return json.dumps(d, ensure_ascii=False, default=repr)
    except Exception:
        try:
            d["msg"] = "<json serialize error, original dropped>"
            d["attrs"] = {}
            return json.dumps(d, ensure_ascii=False)
        except Exception:
            return "{\"ts\":\"" + _format_ts_iso(event.ts) + "\",\"level\":\"" + \
                   event.level.name + "\",\"msg\":\"<serialize fail>\"}"


# ============================================================
# 5. 双轮转文件处理器 (简化可用版,完整高级版见 handlers.py)
# ============================================================
class DualRotatingFileHandler:
    """文件大小 + 跨日 双轮转; GZIP 压缩归档; 总容量硬上限。

    最小可用实现 (无需第三方依赖)。完整版见同目录 handlers.py。
    """

    def __init__(
        self,
        base_path: str | Path,
        *,
        max_bytes: int = 50 * 1024 * 1024,
        backup_count: int = 100,
        retention_days: int = 30,
        total_capacity_gb: float = 10.0,
        compress_old: bool = True,
    ) -> None:
        self.base_path = Path(base_path).expanduser().resolve()
        self.base_path.parent.mkdir(parents=True, exist_ok=True)
        self.max_bytes = max(1024 * 1024, int(max_bytes))
        self.backup_count = max(1, int(backup_count))
        self.retention_days = retention_days
        self.total_capacity_bytes = int(total_capacity_gb * 1024 ** 3)
        self.compress_old = compress_old

        self._lock = threading.Lock()
        self._fh = open(self.base_path, "a", encoding="utf-8", buffering=1)
        self._current_day = datetime.now(tz=_TZ_BJ).date()
        self._size: int = self.base_path.stat().st_size if self.base_path.exists() else 0

    def write_lines(self, lines: Iterable[str]) -> int:
        """批量写多行 (每行需自带换行)。返回写入字节数。"""
        written = 0
        with self._lock:
            try:
                for line in lines:
                    if not line.endswith("\n"):
                        line = line + "\n"
                    b = line.encode("utf-8")
                    self._fh.buffer.write(b)
                    self._size += len(b)
                    written += len(b)
                    if self._size >= self.max_bytes:
                        self._rotate_locked()
                self._fh.flush()
            except Exception:
                # P6: 写失败不能抛
                try:
                    print("[agent-logger] 写入失败,可能磁盘故障", file=sys.stderr)
                except Exception:
                    pass
            # 跨日检测 (不严格每条都看, 每次写入批结束检查一次)
            today = datetime.now(tz=_TZ_BJ).date()
            if today != self._current_day:
                try:
                    self._rotate_locked(force=True)
                    self._current_day = today
                except Exception:
                    pass
            self._cleanup_policy_locked()
        return written

    def flush(self) -> None:
        with self._lock:
            try:
                self._fh.flush()
            except Exception:
                pass

    def close(self) -> None:
        with self._lock:
            try:
                self._fh.flush()
                self._fh.close()
            except Exception:
                pass

    # --------------------- 内部 ---------------------
    def _rotate_locked(self, force: bool = False) -> None:
        try:
            self._fh.flush()
            self._fh.close()
        except Exception:
            pass
        try:
            if self.base_path.exists() and self.base_path.stat().st_size > 0:
                suffix = datetime.now(tz=_TZ_BJ).strftime("%Y-%m-%d_%H-%M-%S")
                target = self.base_path.with_name(self.base_path.name + "." + suffix)
                try:
                    shutil.move(str(self.base_path), str(target))
                    if self.compress_old:
                        self._gzip_compress(target)
                except Exception:
                    # 轮转失败回退: 尝试直接清空文件继续写
                    try:
                        self.base_path.unlink()
                    except Exception:
                        pass
        finally:
            self._fh = open(self.base_path, "a", encoding="utf-8", buffering=1)
            self._size = 0

    @staticmethod
    def _gzip_compress(path: Path) -> Path:
        gz = path.with_suffix(path.suffix + ".gz")
        try:
            with open(path, "rb") as fin, gzip.open(gz, "wb", compresslevel=6) as fout:
                shutil.copyfileobj(fin, fout, length=1024 * 1024)
            path.unlink()
        except Exception:
            # 压缩失败保留原文件,不影响后续
            pass
        return gz

    def _cleanup_policy_locked(self) -> None:
        try:
            parent = self.base_path.parent
            prefix = self.base_path.name + "."
            all_archives: List[Path] = sorted(
                [p for p in parent.glob(prefix + "*")],
                key=lambda p: p.stat().st_mtime if p.exists() else 0,
                reverse=False,  # 最旧的在前
            )

            # 1. 按保留数量 删除超过 backup_count 的最旧文件
            while len(all_archives) > self.backup_count:
                victim = all_archives.pop(0)
                try:
                    victim.unlink()
                except Exception:
                    pass

            # 2. 按保留天数
            if self.retention_days and self.retention_days > 0:
                deadline = time.time() - self.retention_days * 86400
                for p in list(all_archives):
                    try:
                        if p.exists() and p.stat().st_mtime < deadline:
                            p.unlink()
                            all_archives.remove(p)
                    except Exception:
                        pass

            # 3. 总容量硬上限 (最彻底的兜底)
            total_used = self._total_size_bytes(parent, prefix + "*") + self._size
            target = self.total_capacity_bytes // 2  # 2 份 log (agent + jsonl)
            while total_used > target and all_archives:
                victim = all_archives.pop(0)
                try:
                    sz = victim.stat().st_size if victim.exists() else 0
                    victim.unlink()
                    total_used -= sz
                except Exception:
                    pass
        except Exception:
            pass

    @staticmethod
    def _total_size_bytes(directory: Path, pattern: str) -> int:
        total = 0
        for p in directory.glob(pattern):
            try:
                if p.is_file():
                    total += p.stat().st_size
            except Exception:
                pass
        return total


class ConsoleHandler:
    """控制台输出, 自动 TTY 检测彩色。"""

    def __init__(self, *, force_color: Optional[bool] = None) -> None:
        if force_color is None:
            try:
                self._use_color = bool(sys.stdout.isatty())
            except Exception:
                self._use_color = False
        else:
            self._use_color = bool(force_color)
        self._lock = threading.Lock()

    def write_lines(self, lines_events: Iterable[Tuple[str, LogEvent]]) -> None:
        with self._lock:
            try:
                for formatted_line, ev in lines_events:
                    if not formatted_line.endswith("\n"):
                        formatted_line = formatted_line + "\n"
                    # 控制台只用 Text 格式 (format_text 已带颜色),直接 sys.stdout
                    sys.stdout.write(formatted_line)
                sys.stdout.flush()
            except Exception:
                # P6: 控制台挂了也不能抛
                pass


# ============================================================
# 6. AgentLogger 门面类 (单例)
# ============================================================
_DEFAULT_CONFIG: Dict[str, Any] = {
    "log_dir": "./logs",
    "max_bytes_per_file": 50 * 1024 * 1024,
    "backup_count": 100,
    "retention_days": 30,
    "total_capacity_gb": 10.0,
    "compress_old": True,
    "default_level": "INFO",
    "console_level": "INFO",
    "file_text_level": "DEBUG",
    "file_json_level": "DEBUG",
    "error_log_level": "WARNING",
    "module_levels": {},
    "queue_capacity": 10000,
    "flush_batch_size": 200,
    "flush_interval_ms": 250.0,
    "enable_console": True,
    "enable_text_file": True,
    "enable_json_file": True,
    "enable_error_file": True,
}


class AgentLogger:
    """Agent 日志门面类 (线程安全单例)。

    使用::

        logger = AgentLogger(log_dir="./logs")
        logger.info("用户登录 OK", user_id="u1001")
        logger.error("LLM 调用失败", exc=e, 重试=3)
    """

    _instance: Optional["AgentLogger"] = None
    _instance_lock = threading.Lock()

    def __init__(self, log_dir: Optional[str | Path] = None, config: Optional[Dict[str, Any]] = None) -> None:
        # ---- 合并配置 ----
        cfg: Dict[str, Any] = dict(_DEFAULT_CONFIG)
        cfg.update(config or {})
        if log_dir is not None:
            cfg["log_dir"] = str(log_dir)
        # 允许环境变量覆盖 (符合 5.1 节优先级)
        env_map = {
            "AGENT_LOG_DIR": "log_dir",
            "AGENT_LOG_MAX_BYTES": ("max_bytes_per_file", int),
            "AGENT_LOG_RETENTION_DAYS": ("retention_days", int),
            "AGENT_LOG_LEVEL": "default_level",
            "AGENT_LOG_TOTAL_GB": ("total_capacity_gb", float),
        }
        for k, v in os.environ.items():
            if k in env_map:
                target = env_map[k]
                if isinstance(target, tuple):
                    key, cast = target
                    try:
                        cfg[key] = cast(v)
                    except Exception:
                        pass
                else:
                    cfg[target] = v

        self.config = cfg
        self._log_dir = Path(cfg["log_dir"]).expanduser().resolve()
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._meta_dir = self._log_dir / "meta"
        self._meta_dir.mkdir(parents=True, exist_ok=True)

        # 级别控制
        self._global_level: LogLevel = LogLevel.from_str(cfg["default_level"])
        self._module_levels: Dict[str, LogLevel] = {
            m: LogLevel.from_str(lv) for m, lv in (cfg["module_levels"] or {}).items()
        }
        self._console_level = LogLevel.from_str(cfg["console_level"])
        self._file_text_level = LogLevel.from_str(cfg["file_text_level"])
        self._file_json_level = LogLevel.from_str(cfg["file_json_level"])
        self._error_level = LogLevel.from_str(cfg["error_log_level"])

        # 处理器
        self._console = ConsoleHandler() if cfg["enable_console"] else None
        self._text_handler: Optional[DualRotatingFileHandler] = None
        self._json_handler: Optional[DualRotatingFileHandler] = None
        self._error_handler: Optional[DualRotatingFileHandler] = None

        if cfg["enable_text_file"]:
            self._text_handler = DualRotatingFileHandler(
                self._log_dir / "agent.log",
                max_bytes=cfg["max_bytes_per_file"],
                backup_count=cfg["backup_count"],
                retention_days=cfg["retention_days"],
                total_capacity_gb=cfg["total_capacity_gb"] / 2 if cfg["enable_json_file"] else cfg["total_capacity_gb"],
                compress_old=cfg["compress_old"],
            )
        if cfg["enable_json_file"]:
            self._json_handler = DualRotatingFileHandler(
                self._log_dir / "agent.jsonl",
                max_bytes=cfg["max_bytes_per_file"],
                backup_count=cfg["backup_count"],
                retention_days=cfg["retention_days"],
                total_capacity_gb=cfg["total_capacity_gb"] / 2 if cfg["enable_text_file"] else cfg["total_capacity_gb"],
                compress_old=cfg["compress_old"],
            )
        if cfg["enable_error_file"]:
            self._error_handler = DualRotatingFileHandler(
                self._log_dir / "agent.error.log",
                max_bytes=10 * 1024 * 1024,
                backup_count=10,
                retention_days=90,
                total_capacity_gb=2.0,
                compress_old=True,
            )

        # CRITICAL 告警回调
        self._critical_cbs: List[Callable[[LogEvent], None]] = []

        # 异步缓冲队列
        self._ring = AsyncRingBuffer(
            capacity=cfg["queue_capacity"],
            flush_batch_size=cfg["flush_batch_size"],
            flush_interval_ms=cfg["flush_interval_ms"],
            handler_fn=self._handle_batch,
        )
        self._ring.start()

        # atexit 优雅退出 + CRITICAL 同步 flush 机制注册
        self._shutdown = False
        atexit.register(self.shutdown)

    # =========================================================
    # 单例工厂
    # =========================================================
    @classmethod
    def get_instance(cls) -> "AgentLogger":
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = AgentLogger()
        return cls._instance

    # =========================================================
    # 级别控制 (3.3 节 动态级别热更新)
    # =========================================================
    def set_level(self, module: str, level: Union[str, int, LogLevel]) -> None:
        lv = LogLevel.from_str(level)
        if module in ("*", "", None):
            self._global_level = lv
        else:
            self._module_levels[module] = lv

    def get_level(self, module: str = "") -> LogLevel:
        if module:
            # 最长前缀匹配
            best: Optional[str] = None
            for m in self._module_levels:
                if (module == m or module.startswith(m + ".")) and (best is None or len(m) > len(best)):
                    best = m
            if best is not None:
                return self._module_levels[best]
        return self._global_level

    def reset_level(self, module: str) -> None:
        if module in ("*", "", None):
            self._global_level = LogLevel.from_str(self.config["default_level"])
        else:
            self._module_levels.pop(module, None)

    def reset_all_levels(self) -> None:
        self._global_level = LogLevel.from_str(self.config["default_level"])
        self._module_levels = {
            m: LogLevel.from_str(lv) for m, lv in (self.config.get("module_levels") or {}).items()
        }

    def reload_config(self, config_path: Optional[str | Path] = None) -> bool:
        """简化版 reload: 当检测到同目录 logger.yaml / logger.json 时重新载入 module_levels。"""
        if not config_path:
            for cand in ["logger.json", "logger.yaml", "logger.yml"]:
                p = Path(cand)
                if p.exists():
                    config_path = p
                    break
        if not config_path:
            return False
        try:
            path = Path(config_path)
            if path.suffix == ".json":
                import json as _json
                with open(path, "r", encoding="utf-8") as f:
                    new_cfg = _json.load(f)
            else:
                if importlib.util.find_spec("yaml") is None:
                    # 没有 PyYAML 就不支持 yaml 重载
                    return False
                import yaml  # type: ignore
                with open(path, "r", encoding="utf-8") as f:
                    new_cfg = yaml.safe_load(f) or {}
            ml = new_cfg.get("module_levels") or {}
            for m, lv in ml.items():
                self.set_level(m, lv)
            gl = new_cfg.get("default_level")
            if gl:
                self.set_level("*", gl)
            return True
        except Exception:
            return False

    # =========================================================
    # 5 级日志 API
    # =========================================================
    def _should_log(self, level: LogLevel, module: str) -> bool:
        return level >= self.get_level(module)

    def _enqueue_or_sync(self, event: LogEvent) -> None:
        """路由策略:
            ERROR/CRITICAL: 同步写入 + 触发回调 (防止崩溃丢证据)
            DEBUG/WARNING/INFO: 异步环形队列
        """
        if event.level >= LogLevel.ERROR:
            # 紧急: 直接同步 flush (P2 原则)
            try:
                self._handle_batch([event])
            except Exception:
                pass
            if event.level >= LogLevel.CRITICAL:
                self._fire_critical(event)
            return

        # 其他级别: 异步
        if self._shutdown:
            # 关闭后直接同步, 避免进入队列丢失
            try:
                self._handle_batch([event])
            except Exception:
                pass
            return
        self._ring.enqueue(event)

    def _make_event(self, level: LogLevel, msg: str, args: Tuple[Any, ...],
                    module: str, attrs: Dict[str, Any],
                    exc: Optional[BaseException]) -> LogEvent:
        ctx = TraceContext.current()
        return LogEvent(
            ts=time.time(),
            level=level,
            module=module or "agent",
            msg=msg,
            args=tuple(args),
            attrs=attrs,
            trace_id=ctx["trace_id"],
            span_id=ctx["span_id"],
            user_id=ctx["user_id"],
            session_id=ctx["session_id"],
            err=exc,
        )

    def debug(self, msg: str, *args: Any, module: str = "", **attrs: Any) -> None:
        if not self._should_log(LogLevel.DEBUG, module):
            return  # 关键: 关闭时零操作,延迟 <100ns (7.1 节)
        ev = self._make_event(LogLevel.DEBUG, msg, args, module, attrs, None)
        self._enqueue_or_sync(ev)

    def info(self, msg: str, *args: Any, module: str = "", **attrs: Any) -> None:
        if not self._should_log(LogLevel.INFO, module):
            return
        ev = self._make_event(LogLevel.INFO, msg, args, module, attrs, None)
        self._enqueue_or_sync(ev)

    def warning(self, msg: str, *args: Any, module: str = "",
                exc: Optional[BaseException] = None, **attrs: Any) -> None:
        if not self._should_log(LogLevel.WARNING, module):
            return
        ev = self._make_event(LogLevel.WARNING, msg, args, module, attrs, exc)
        self._enqueue_or_sync(ev)

    warn = warning

    def error(self, msg: str, *args: Any, module: str = "",
              exc: Optional[BaseException] = None, **attrs: Any) -> None:
        # ERROR 级别永远不做 "不开就跳过" 的短路, 因为 ERROR 必须要能打出来
        # 但是 module_level 可以压制 (比如 silent 模式)
        if not self._should_log(LogLevel.ERROR, module):
            return
        if exc is None:
            # 自动捕获当前正在处理的异常 (logger.exception 模式)
            exc_info = sys.exc_info()
            if exc_info[1] is not None:
                exc = exc_info[1]
        ev = self._make_event(LogLevel.ERROR, msg, args, module, attrs, exc)
        self._enqueue_or_sync(ev)

    def exception(self, msg: str, *args: Any, module: str = "", **attrs: Any) -> None:
        self.error(msg, *args, module=module, **attrs)

    def critical(self, msg: str, *args: Any, module: str = "",
                 exc: Optional[BaseException] = None, **attrs: Any) -> None:
        if not self._should_log(LogLevel.CRITICAL, module):
            return
        if exc is None:
            exc_info = sys.exc_info()
            if exc_info[1] is not None:
                exc = exc_info[1]
        ev = self._make_event(LogLevel.CRITICAL, msg, args, module, attrs, exc)
        self._enqueue_or_sync(ev)

    # =========================================================
    # 测量上下文 (自动计时 + 打 INFO)
    # =========================================================
    @contextmanager
    def timed(self, msg_on_end: str, *, level: Union[str, LogLevel] = LogLevel.INFO,
              module: str = "", on_error: str = "", **extra_attrs: Any
              ) -> Generator[Dict[str, Any], None, None]:
        """with logger.timed("LLM调用完成", module="llm", model="gpt-4o"):
                do_something()
        结束时自动写: {msg} dur_ms=XXX  model=gpt-4o
        """
        lv = LogLevel.from_str(level)
        t0 = time.perf_counter()
        info: Dict[str, Any] = {"start": t0}
        try:
            yield info
            dur_ms = (time.perf_counter() - t0) * 1000.0
            self._log_timed(lv, msg_on_end, module, dur_ms, extra_attrs)
        except BaseException as e:
            dur_ms = (time.perf_counter() - t0) * 1000.0
            err_msg = on_error or (msg_on_end + " 失败")
            self.error(err_msg, module=module, exc=e, dur_ms=dur_ms, **extra_attrs)
            raise

    def _log_timed(self, lv: LogLevel, msg: str, module: str,
                   dur_ms: float, extra: Dict[str, Any]) -> None:
        if not self._should_log(lv, module):
            return
        extra["duration_ms"] = dur_ms
        ev = self._make_event(lv, msg, (), module, extra, None)
        ev.duration_ms = dur_ms
        self._enqueue_or_sync(ev)

    # =========================================================
    # CRITICAL 告警回调
    # =========================================================
    def register_critical_callback(self, cb: Callable[[LogEvent], None]) -> None:
        self._critical_cbs.append(cb)

    def _fire_critical(self, ev: LogEvent) -> None:
        for cb in list(self._critical_cbs):
            try:
                cb(ev)
            except Exception:
                # P6: 回调挂了不能影响后续
                try:
                    print("[agent-logger] CRITICAL 回调异常", file=sys.stderr)
                except Exception:
                    pass

    # =========================================================
    # 批量处理器 (被异步 Ring / 同步 ERROR 调用)
    # =========================================================
    def _handle_batch(self, events: List[LogEvent]) -> None:
        # 1. 先分流每个输出渠道的级别过滤 (每个渠道独立级别)
        text_lines: List[str] = []
        json_lines: List[str] = []
        console_items: List[Tuple[str, LogEvent]] = []
        err_lines: List[str] = []

        use_color_console = bool(self._console and self._console._use_color)

        for ev in events:
            if self._console and ev.level >= self._console_level:
                console_items.append((format_text(ev, use_color=use_color_console), ev))
            if self._text_handler and ev.level >= self._file_text_level:
                text_lines.append(format_text(ev, use_color=False))
            if self._json_handler and ev.level >= self._file_json_level:
                json_lines.append(format_json_line(ev))
            if self._error_handler and ev.level >= self._error_level:
                err_lines.append(format_text(ev, use_color=False))

        # 2. 批量写入每个渠道
        if console_items:
            try:
                self._console.write_lines(console_items)  # type: ignore[union-attr]
            except Exception:
                pass
        if text_lines and self._text_handler:
            try:
                self._text_handler.write_lines(text_lines)
            except Exception:
                pass
        if json_lines and self._json_handler:
            try:
                self._json_handler.write_lines(json_lines)
            except Exception:
                pass
        if err_lines and self._error_handler:
            try:
                self._error_handler.write_lines(err_lines)
            except Exception:
                pass

    # =========================================================
    # 生命周期
    # =========================================================
    def flush(self, timeout: float = 5.0) -> None:
        self._ring.drain_all(timeout=timeout)
        for h in (self._text_handler, self._json_handler, self._error_handler):
            if h is not None:
                try:
                    h.flush()
                except Exception:
                    pass

    def shutdown(self) -> None:
        if self._shutdown:
            return
        self._shutdown = True
        try:
            self.flush(timeout=3.0)
        except Exception:
            pass
        try:
            self._ring.shutdown(timeout=2.0)
        except Exception:
            pass
        for h in (self._text_handler, self._json_handler, self._error_handler):
            if h is not None:
                try:
                    h.close()
                except Exception:
                    pass
        # 关闭后清空单例引用, 方便测试下一个用例
        if __class__._instance is self:  # type: ignore[name-defined]
            __class__._instance = None  # type: ignore[name-defined]


# 便于 `from agent_logger import get_logger, TraceContext`
def get_logger(log_dir: Optional[str] = None, **config: Any) -> AgentLogger:
    if AgentLogger._instance is None or log_dir or config:
        with AgentLogger._instance_lock:
            if AgentLogger._instance is None or log_dir or config:
                AgentLogger._instance = AgentLogger(log_dir=log_dir, config=config or None)
    return AgentLogger._instance


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
