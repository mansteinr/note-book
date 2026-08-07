"""日志查询与分析接口 (LogQuerier + LogAnalyzer)。

提供结构化查询 API: 按级别 / 时间 / trace_id / module / keyword / attribute 过滤,
并内置统计分析: 级别分布、Top 错误、模块热力图、耗时 P50/P95/P99。

只依赖 Python 标准库, 零第三方。
"""
from __future__ import annotations

import csv
import fnmatch
import io
import json
import os
import re
import time
from contextlib import contextmanager
from dataclasses import dataclass
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
    Set,
    Tuple,
    Union,
)

# 共享 BJ 时区
_TZ_BJ = timezone(timedelta(hours=8))

# =========================================================
# 工具: 时间解析
# =========================================================
def _parse_time_str(s: Optional[Union[str, int, float]]) -> Optional[float]:
    """把 "YYYY-MM-DD HH:MM:SS" 或 epoch 秒 统一成 epoch 秒浮点。"""
    if s is None or s == "":
        return None
    if isinstance(s, (int, float)):
        return float(s)
    s = str(s).strip()
    # ISO 8601 epoch number string
    try:
        if all(c.isdigit() or c == "." for c in s) and s.count(".") <= 1:
            return float(s)
    except Exception:
        pass
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d",
    ]
    # 如果有 +08:00 这样的时区, 先做兼容处理 (datetime.fromisoformat Python 3.11+ 更强)
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except Exception:
        pass
    for fmt in formats:
        try:
            dt = datetime.strptime(s, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=_TZ_BJ)
            return dt.timestamp()
        except Exception:
            continue
    raise ValueError(f"无法解析时间字符串: {s}")


def _line_is_json(line: str) -> bool:
    stripped = line.lstrip()
    return bool(stripped) and stripped[0] == "{"


# =========================================================
# 单行解析 (Text / JSON 双格式)
# =========================================================
_TEXT_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d{3})?)\s+"
    r"\[(?P<level>DEBUG|INFO|WARN|WARNING|ERROR|CRIT|CRITICAL)\s*\]\s+"
    r"\[(?P<module>[^\]]{1,40})\]\s+"
    r"trace=(?P<trace>\S+)\s+span=(?P<span>\S+)"
    r"(?P<rest>.*)$"
)


def _parse_text_line(line: str) -> Optional[Dict[str, Any]]:
    line = line.rstrip("\n")
    if not line:
        return None
    m = _TEXT_RE.match(line)
    if not m:
        return None
    ts_str = m.group("ts")
    try:
        if "." in ts_str:
            dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=_TZ_BJ)
        else:
            dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=_TZ_BJ)
        ts_epoch = dt.timestamp()
    except Exception:
        ts_epoch = 0.0
    level = m.group("level")
    if level == "WARN":
        level = "WARNING"
    if level == "CRIT":
        level = "CRITICAL"
    module = m.group("module").strip()
    trace_id = m.group("trace")
    span_id = m.group("span")
    rest = m.group("rest") or ""

    # 拆 rest: " user=u1  k=v  dur_ms=42.0  消息内容"
    # 约定:第一个 "  " (两个空格) 就是 attrs 和 msg 的分界
    parts = rest.split("  ", 2)
    attrs_part = parts[1] if len(parts) >= 2 else ""
    msg = parts[2] if len(parts) >= 3 else (parts[0].lstrip() if parts else "")

    attrs: Dict[str, Any] = {}
    # 解析 k=v / k="spaced value" / dur_ms=X  user=...
    pat = re.compile(r'(\w+)=("[^"]*"|\S+)')
    for km in pat.finditer(attrs_part):
        k, v = km.group(1), km.group(2)
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        else:
            # 尝试转数字
            try:
                if "." in v:
                    v = float(v)
                elif v.lstrip("-").isdigit():
                    v = int(v)
            except Exception:
                pass
        if k == "dur_ms":
            try:
                attrs["duration_ms"] = float(v)
            except Exception:
                pass
        else:
            attrs[k] = v

    return {
        "ts": ts_str,
        "ts_epoch": ts_epoch,
        "level": level,
        "module": module,
        "trace_id": trace_id,
        "span_id": span_id,
        "attrs": attrs,
        "msg": msg,
    }


def _parse_json_line(line: str) -> Optional[Dict[str, Any]]:
    line = line.strip()
    if not line:
        return None
    try:
        d = json.loads(line)
    except Exception:
        return None
    if not isinstance(d, dict):
        return None
    # JSON 本身字段齐全, 直接用; 但补一个 ts_epoch 标准键
    if "ts_epoch" not in d and "ts" in d:
        try:
            d["ts_epoch"] = _parse_time_str(d["ts"])
        except Exception:
            d["ts_epoch"] = 0.0
    return d


# =========================================================
# 文件发现 & 流式产出 (支持 .gz 解压)
# =========================================================
def _discover_log_files(log_dir: str | Path, *,
                        prefer_jsonl: bool = True,
                        include_text: bool = True) -> List[Path]:
    d = Path(log_dir).expanduser().resolve()
    if not d.is_dir():
        return []
    files: List[Path] = []
    patterns = (["agent.jsonl*"] if prefer_jsonl else []) + (["agent.log*"] if include_text else [])
    # 再加 error log (可被 keyword "ERROR" 命中)
    seen: Set[Path] = set()
    for pattern in patterns:
        for p in sorted(d.glob(pattern), key=lambda x: x.stat().st_mtime if x.exists() else 0, reverse=True):
            if p.is_file() and p not in seen:
                files.append(p)
                seen.add(p)
    return files


def _open_maybe_gz(path: Path):
    name = str(path).lower()
    if name.endswith(".gz"):
        import gzip as _gzip
        return _gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return open(path, "r", encoding="utf-8", errors="replace")


@contextmanager
def _smart_open(path: Path):
    fh = _open_maybe_gz(path)
    try:
        yield fh
    finally:
        try:
            fh.close()
        except Exception:
            pass


def _iter_events(files: Sequence[Path]) -> Generator[Dict[str, Any], None, None]:
    for f in files:
        try:
            with _smart_open(f) as fh:
                for line in fh:
                    if not line:
                        continue
                    ev: Optional[Dict[str, Any]]
                    if _line_is_json(line):
                        ev = _parse_json_line(line)
                    else:
                        ev = _parse_text_line(line)
                    if ev:
                        yield ev
        except Exception:
            continue


# =========================================================
# LogQuerier: 链式查询
# =========================================================
@dataclass
class _QueryFilters:
    trace_id: Optional[str] = None
    trace_prefix: Optional[str] = None
    levels: Optional[Set[str]] = None
    level_min: Optional[str] = None
    modules_include: Optional[Set[str]] = None
    modules_patterns: List[str] = None  # fnmatch patterns, e.g. "agent.llm.*"
    time_start: Optional[float] = None
    time_end: Optional[float] = None
    keywords: List[Tuple[str, str, bool]] = None    # (pattern, field, case_sensitive)
    attrs_eq: List[Tuple[str, Any]] = None
    limit: Optional[int] = None
    order_field: str = "ts_epoch"
    order_desc: bool = True


_LEVELS_RANK = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "WARN": 30,
                "ERROR": 40, "CRITICAL": 50, "CRIT": 50, "FATAL": 50}


def _level_rank(name: str) -> int:
    return _LEVELS_RANK.get(str(name).upper(), 0)


class LogQuerier:
    """结构化日志查询 API,链式调用。

    Example::

        q = LogQuerier("./logs")
        rows = (q.trace_id("req-abc")
                 .time_range("2026-08-08 14:00:00", "2026-08-08 18:00:00")
                 .level_ge("WARNING")
                 .keyword("RateLimit")
                 .limit(100)
                 .run().to_list())
    """

    def __init__(self, log_dir: str | Path = "./logs") -> None:
        self.log_dir = Path(log_dir)
        self._f = _QueryFilters(
            modules_patterns=[],
            keywords=[],
            attrs_eq=[],
        )

    # --------- 过滤链 ---------
    def trace_id(self, trace_id: str, *, prefix: bool = False) -> "LogQuerier":
        if prefix:
            self._f.trace_prefix = trace_id
        else:
            self._f.trace_id = trace_id
        return self

    def level_eq(self, level: str) -> "LogQuerier":
        self._f.levels = {str(level).upper()}
        return self

    def level_in(self, levels: Iterable[str]) -> "LogQuerier":
        self._f.levels = {l.upper() for l in levels}
        return self

    def level_ge(self, level: str) -> "LogQuerier":
        self._f.level_min = str(level).upper()
        return self

    def module_in(self, modules: Iterable[str]) -> "LogQuerier":
        self._f.modules_include = set(modules)
        return self

    def module_glob(self, pattern: str) -> "LogQuerier":
        """支持通配符模块匹配,例如 module_glob("agent.llm.*")"""
        self._f.modules_patterns.append(pattern)
        return self

    def time_range(self, start: Optional[Union[str, int, float]] = None,
                   end: Optional[Union[str, int, float]] = None,
                   *, last_seconds: Optional[int] = None) -> "LogQuerier":
        if last_seconds is not None:
            now = time.time()
            self._f.time_start = now - float(last_seconds)
            self._f.time_end = now + 1.0
            return self
        self._f.time_start = _parse_time_str(start) if start is not None else None
        self._f.time_end = _parse_time_str(end) if end is not None else None
        return self

    def keyword(self, pattern: str, *, case_sensitive: bool = False,
                field: str = "msg") -> "LogQuerier":
        self._f.keywords.append((pattern, field or "msg", bool(case_sensitive)))
        return self

    def attribute(self, key: str, value: Any) -> "LogQuerier":
        self._f.attrs_eq.append((key, value))
        return self

    def limit(self, n: int) -> "LogQuerier":
        self._f.limit = max(0, int(n))
        return self

    def order_by(self, field: str = "ts", *, desc: bool = True) -> "LogQuerier":
        mapping = {"ts": "ts_epoch", "ts_epoch": "ts_epoch",
                   "level": "level", "module": "module"}
        self._f.order_field = mapping.get(field, "ts_epoch")
        self._f.order_desc = bool(desc)
        return self

    # --------- 执行 ---------
    def _filter_one(self, ev: Dict[str, Any]) -> bool:
        f = self._f
        # trace
        if f.trace_id and ev.get("trace_id") != f.trace_id:
            return False
        if f.trace_prefix and not (ev.get("trace_id") or "").startswith(f.trace_prefix):
            return False
        # levels
        lv = str(ev.get("level", "")).upper()
        if f.levels and lv not in f.levels:
            return False
        if f.level_min and _level_rank(lv) < _level_rank(f.level_min):
            return False
        # modules
        mod = ev.get("module", "") or ""
        if f.modules_include:
            if mod not in f.modules_include:
                return False
        if f.modules_patterns:
            hit_any = False
            for pat in f.modules_patterns:
                if fnmatch.fnmatchcase(mod, pat):
                    hit_any = True
                    break
            if not hit_any:
                return False
        # time
        ts = float(ev.get("ts_epoch") or 0.0)
        if f.time_start is not None and ts < f.time_start:
            return False
        if f.time_end is not None and ts > f.time_end:
            return False
        # keyword
        for pat, field, cs in f.keywords:
            if field == "*":
                haystack = json.dumps(ev, ensure_ascii=False)
            else:
                haystack = ""
                if field in ev and ev[field] is not None:
                    try:
                        haystack = str(ev[field])
                    except Exception:
                        haystack = ""
                if not haystack and field in (ev.get("attrs") or {}):
                    try:
                        haystack = str((ev.get("attrs") or {})[field])
                    except Exception:
                        haystack = ""
            if cs:
                if pat not in haystack:
                    return False
            else:
                if pat.lower() not in haystack.lower():
                    return False
        # attrs_eq
        attrs_dict = ev.get("attrs") or {}
        for k, v in f.attrs_eq:
            found_val = attrs_dict.get(k)
            if found_val is None and ev.get(k) is not None:
                found_val = ev.get(k)
            if found_val != v:
                try:
                    if str(found_val) != str(v):
                        return False
                except Exception:
                    return False
        return True

    def run(self) -> "QueryResult":
        files = _discover_log_files(self.log_dir, prefer_jsonl=True, include_text=True)
        it = (ev for ev in _iter_events(files) if self._filter_one(ev))

        results: List[Dict[str, Any]]
        if self._f.limit is not None:
            results = []
            for ev in it:
                results.append(ev)
                if len(results) >= self._f.limit:
                    break
        else:
            results = list(it)

        # 排序
        ofield = self._f.order_field
        if ofield == "level":
            results.sort(key=lambda e: _level_rank(e.get("level", "")), reverse=self._f.order_desc)
        else:
            def _k(ev):
                v = ev.get(ofield)
                if v is None:
                    return 0
                if isinstance(v, (int, float)):
                    return float(v)
                return v
            results.sort(key=_k, reverse=self._f.order_desc)
        return QueryResult(results, querier=self)

    def count(self) -> int:
        return self.run().count()


# =========================================================
# QueryResult: 查询结果封装 + 多格式导出
# =========================================================
class QueryResult:
    def __init__(self, rows: List[Dict[str, Any]], querier: Optional[LogQuerier] = None) -> None:
        self.rows: List[Dict[str, Any]] = rows
        self.querier = querier

    def __iter__(self):
        return iter(self.rows)

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, idx):
        return self.rows[idx]

    def count(self) -> int:
        return len(self.rows)

    def first(self) -> Optional[Dict[str, Any]]:
        return self.rows[0] if self.rows else None

    def to_list(self) -> List[Dict[str, Any]]:
        return list(self.rows)

    def to_pandas(self):
        """如果环境有 pandas, 转为 DataFrame 便于 Jupyter 分析。"""
        try:
            import pandas as pd  # type: ignore
        except ImportError as e:
            raise RuntimeError("pandas 未安装,请先 pip install pandas") from e
        return pd.DataFrame(self.rows)

    # ---------- 导出 ----------
    def export_json(self, path: str | Path) -> int:
        import json as _json
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            _json.dump(self.rows, f, ensure_ascii=False, indent=2, default=repr)
        return len(self.rows)

    def export_csv(self, path: str | Path) -> int:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        # 扁平 keys: 提取所有出现过的列
        cols: List[str] = []
        seen: Set[str] = set()
        def _touch(c: str):
            if c not in seen:
                seen.add(c)
                cols.append(c)
        for r in self.rows:
            for k in r.keys():
                if k == "attrs":
                    continue
                _touch(k)
        # attrs 的 keys 单独展开
        attr_keys: List[str] = []
        ak_seen: Set[str] = set()
        for r in self.rows:
            attrs = r.get("attrs") or {}
            if isinstance(attrs, dict):
                for k in attrs.keys():
                    if k not in ak_seen:
                        ak_seen.add(k)
                        attr_keys.append(k)
        all_cols = cols + [f"attr_{k}" for k in attr_keys]
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=all_cols, extrasaction="ignore")
            w.writeheader()
            for r in self.rows:
                row: Dict[str, Any] = {k: r.get(k) for k in cols}
                attrs = r.get("attrs") or {}
                if isinstance(attrs, dict):
                    for ak in attr_keys:
                        try:
                            row[f"attr_{ak}"] = json.dumps(attrs[ak], ensure_ascii=False) \
                                if isinstance(attrs[ak], (dict, list)) else attrs[ak]
                        except KeyError:
                            row[f"attr_{ak}"] = ""
                w.writerow(row)
        return len(self.rows)

    def export_logfmt(self, path: str | Path) -> int:
        """导出 logfmt (k=v 空格分隔), Loki/Victorialogs 友好。"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for r in self.rows:
                parts: List[str] = []
                for k, v in r.items():
                    if k == "attrs":
                        if isinstance(v, dict):
                            for ak, av in v.items():
                                parts.append(self._logfmt_kv(f"attrs_{ak}", av))
                        continue
                    parts.append(self._logfmt_kv(k, v))
                f.write(" ".join(p for p in parts if p) + "\n")
        return len(self.rows)

    @staticmethod
    def _logfmt_kv(k: str, v: Any) -> str:
        if v is None or v == "":
            return ""
        try:
            if isinstance(v, bool):
                s = "true" if v else "false"
            elif isinstance(v, (int, float)):
                s = repr(v)
            else:
                s = str(v)
        except Exception:
            s = repr(v)
        # 需引号的字符:空格 / = / " / 控制字符
        if any(c.isspace() or c in ('"', "=") for c in s) or s == "":
            escaped = s.replace("\\", "\\\\").replace('"', '\\"')
            return f'{k}="{escaped}"'
        return f"{k}={s}"


# =========================================================
# LogAnalyzer: 统计分析 API
# =========================================================
class LogAnalyzer:
    def __init__(self, log_dir: str | Path = "./logs") -> None:
        self.log_dir = Path(log_dir)

    # --------- 基础工具 ---------
    def _stream(self, *, last_seconds: Optional[int] = None
                ) -> Generator[Dict[str, Any], None, None]:
        q = LogQuerier(self.log_dir)
        if last_seconds is not None:
            q = q.time_range(last_seconds=last_seconds)
        yield from q.run()

    # --------- 统计 API ---------
    def level_distribution(self, *, last_seconds: Optional[int] = None) -> Dict[str, int]:
        result: Dict[str, int] = {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}
        for ev in self._stream(last_seconds=last_seconds):
            lv = str(ev.get("level", "")).upper()
            if lv == "WARN":
                lv = "WARNING"
            if lv == "CRIT" or lv == "FATAL":
                lv = "CRITICAL"
            if lv in result:
                result[lv] += 1
            else:
                result[lv] = result.get(lv, 0) + 1
        return result

    def top_error_types(self, *, limit: int = 10,
                        last_seconds: Optional[int] = None) -> List[Tuple[str, int]]:
        counter: Dict[str, int] = {}
        for ev in self._stream(last_seconds=last_seconds):
            if _level_rank(ev.get("level", "")) < _level_rank("WARNING"):
                continue
            key = ev.get("err_type") or (
                (ev.get("attrs") or {}).get("错误")
                if isinstance(ev.get("attrs"), dict) else None
            ) or ev.get("msg") or "<unknown>"
            try:
                key = str(key)[:200]
            except Exception:
                key = "<unprintable>"
            counter[key] = counter.get(key, 0) + 1
        items = sorted(counter.items(), key=lambda x: x[1], reverse=True)
        return items[:max(1, int(limit))]

    def module_heatmap(self, *, top_n: int = 10,
                       last_seconds: Optional[int] = None) -> List[Tuple[str, int]]:
        counter: Dict[str, int] = {}
        total = 0
        for ev in self._stream(last_seconds=last_seconds):
            m = ev.get("module") or "agent.unknown"
            counter[m] = counter.get(m, 0) + 1
            total += 1
        items = sorted(counter.items(), key=lambda x: x[1], reverse=True)
        return items[:max(1, int(top_n))]

    def duration_analysis(self, msg_keyword: str, *,
                          duration_field: str = "duration_ms",
                          last_seconds: Optional[int] = None) -> Dict[str, Any]:
        values: List[float] = []
        kw = msg_keyword.lower()
        for ev in self._stream(last_seconds=last_seconds):
            msg = str(ev.get("msg", "")).lower()
            if kw and kw not in msg:
                continue
            # 查找耗时字段
            d = ev.get(duration_field)
            if d is None and isinstance(ev.get("attrs"), dict):
                d = (ev.get("attrs") or {}).get(duration_field)
            try:
                values.append(float(d))
            except Exception:
                continue
        if not values:
            return {"count": 0, "p50_ms": 0, "p95_ms": 0, "p99_ms": 0,
                    "avg_ms": 0, "min_ms": 0, "max_ms": 0}
        values.sort()
        n = len(values)

        def pct(p: float) -> float:
            if n == 1:
                return values[0]
            idx = min(n - 1, max(0, int(round((n - 1) * p))))
            return values[idx]

        return {
            "count": n,
            "min_ms": round(values[0], 3),
            "max_ms": round(values[-1], 3),
            "avg_ms": round(sum(values) / n, 3),
            "p50_ms": round(pct(0.50), 3),
            "p95_ms": round(pct(0.95), 3),
            "p99_ms": round(pct(0.99), 3),
        }


__all__ = ["LogQuerier", "QueryResult", "LogAnalyzer"]
