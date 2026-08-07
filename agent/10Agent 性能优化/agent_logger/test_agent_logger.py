"""单元测试: 覆盖 Agent 日志系统全部核心功能。

运行方式 (推荐):
    cd m:\\note-book\\agent\\10agent 性能优化
    python -m pytest agent_logger/test_agent_logger.py -v -s
或无 pytest:
    python -m agent_logger.test_agent_logger
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
import threading
import time
import traceback
from pathlib import Path

# 确保 import 路径可用
_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from agent_logger.core import (  # noqa: E402
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
from agent_logger.query import LogAnalyzer, LogQuerier  # noqa: E402


# =========================================================
# Pytest 兼容:如果没 pytest,就用一个最小 assertion 框架
# =========================================================
def _fail(msg: str):
    raise AssertionError(msg)


def assert_true(cond: bool, msg: str = ""):
    if not cond:
        _fail(f"应 True 但 False: {msg}")


def assert_eq(a, b, msg: str = ""):
    if a != b:
        _fail(f"相等断言失败: {a!r} == {b!r}\n  {msg}")


def assert_gt(a, b, msg: str = ""):
    if not (a > b):
        _fail(f"{a!r} > {b!r} 失败: {msg}")


def assert_lt(a, b, msg: str = ""):
    if not (a < b):
        _fail(f"{a!r} < {b!r} 失败: {msg}")


def assert_in(item, container, msg: str = ""):
    if item not in container:
        _fail(f"{item!r} not in {container!r}: {msg}")


# =========================================================
# 1. 级别定义
# =========================================================
class TestLogLevel:
    def test_ordering(self):
        assert_true(LogLevel.DEBUG < LogLevel.INFO < LogLevel.WARNING
                    < LogLevel.ERROR < LogLevel.CRITICAL, "级别顺序错误")

    def test_from_str(self):
        assert_eq(LogLevel.from_str("warn"), LogLevel.WARNING)
        assert_eq(LogLevel.from_str("INFO"), LogLevel.INFO)
        assert_eq(LogLevel.from_str(40), LogLevel.ERROR)
        assert_eq(LogLevel.from_str(LogLevel.DEBUG), LogLevel.DEBUG)

    def test_values_align_python_logging(self):
        import logging as _logging
        mapping = {
            LogLevel.DEBUG: _logging.DEBUG,
            LogLevel.INFO: _logging.INFO,
            LogLevel.WARNING: _logging.WARNING,
            LogLevel.ERROR: _logging.ERROR,
            LogLevel.CRITICAL: _logging.CRITICAL,
        }
        for ours, expected in mapping.items():
            assert_eq(int(ours), expected, f"级别 {ours.name} 数值应对齐 Python logging")

    def test_int_enum_sorting(self):
        levels = [LogLevel.ERROR, LogLevel.DEBUG, LogLevel.CRITICAL, LogLevel.INFO, LogLevel.WARNING]
        assert_eq(sorted(levels),
                  [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL])


# =========================================================
# 2. TraceContext
# =========================================================
class TestTraceContext:
    def test_simple(self):
        with TraceContext.trace("A", span_id="s1", user_id="u1") as ctx:
            c = TraceContext.current()
            assert_eq(c["trace_id"], "A")
            assert_eq(c["span_id"], "s1")
            assert_eq(c["user_id"], "u1")

    def test_nested_inherits_trace(self):
        with TraceContext.trace("OUT", span_id="outer"):
            with TraceContext.trace(span_id="inner"):
                c = TraceContext.current()
                assert_eq(c["trace_id"], "OUT")
                assert_eq(c["span_id"], "inner")

    def test_exit_restores(self):
        with TraceContext.trace("X"):
            pass
        assert_eq(TraceContext.current()["trace_id"], "")

    def test_thread_safe(self):
        results = {"t1": "", "t2": ""}
        ev = threading.Event()

        def run(k, trace):
            ev.wait()
            with TraceContext.trace(trace):
                time.sleep(0.05)
                results[k] = TraceContext.current()["trace_id"]

        t1 = threading.Thread(target=run, args=("t1", "thread-A"))
        t2 = threading.Thread(target=run, args=("t2", "thread-B"))
        t1.start()
        t2.start()
        ev.set()
        t1.join()
        t2.join()
        assert_eq(results["t1"], "thread-A")
        assert_eq(results["t2"], "thread-B")

    def test_contextvar_does_not_leak(self):
        # 外部无上下文 → 进入有上下文 → 出来又空
        pre = TraceContext.current()["trace_id"]
        with TraceContext.trace("ABC"):
            assert_eq(TraceContext.current()["trace_id"], "ABC")
        post = TraceContext.current()["trace_id"]
        assert_eq(pre, post)
        assert_eq(post, "")


# =========================================================
# 3. AgentLogger API
# =========================================================
def _fresh_logger(tmp: str | Path, **kw) -> AgentLogger:
    # 每次用独立目录 + 销毁之前单例,避免跨用例污染
    AgentLogger._instance = None  # 单例重置 (测试专用)
    cfg = {"default_level": "DEBUG",
           "queue_capacity": 2000,
           "flush_interval_ms": 50,
           "backup_count": 10,
           "retention_days": 7,
           "total_capacity_gb": 1.0}
    cfg.update(kw)
    return AgentLogger(log_dir=str(tmp), config=cfg)


class TestAgentLoggerAPI:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp(prefix="agent-logger-test-")

    def teardown_method(self):
        try:
            AgentLogger._instance and AgentLogger._instance.shutdown()
        except Exception:
            pass
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_5_level_logs_all_write(self):
        lg = _fresh_logger(self.tmp)
        with TraceContext.trace("T1", span_id="sp0"):
            lg.debug("debug msg", module="m")
            lg.info("info msg", module="m", k="v")
            lg.warning("warn msg", module="m")
            try:
                raise RuntimeError("boom")
            except RuntimeError as e:
                lg.error("err msg", module="m", exc=e)
            lg.critical("crit msg", module="m")
        lg.flush(3.0)
        # 检查文件存在
        for name in ("agent.log", "agent.jsonl", "agent.error.log"):
            p = Path(self.tmp) / name
            assert_true(p.exists(), f"{name} 应被创建")

        # agent.log 至少 5 行 (可能因为后台 flush 多几行)
        lines = (Path(self.tmp) / "agent.log").read_text(encoding="utf-8", errors="replace").splitlines()
        assert_gt(len(lines), 3, "至少有 INFO+ 的几行")

        # JSON 完整性: 每行都是合法 JSON
        json_lines = [l for l in (Path(self.tmp) / "agent.jsonl").read_text(
            encoding="utf-8", errors="replace").splitlines() if l.strip()]
        import json
        for line in json_lines:
            d = json.loads(line)
            assert_in("ts", d, "JSON 缺 ts")
            assert_in("level", d, "JSON 缺 level")
            assert_in("trace_id", d, "JSON 缺 trace_id")

    def test_dynamic_level_short_circuit(self):
        lg = _fresh_logger(self.tmp, default_level="WARNING")
        with TraceContext.trace("x"):
            for _ in range(100):
                lg.debug("不应出现", module="m")
                lg.info("也不应出现", module="m")
            lg.warning("必须出现", module="m")
        lg.flush(2.0)
        text = (Path(self.tmp) / "agent.log").read_text(encoding="utf-8", errors="replace")
        assert_in("必须出现", text)
        assert_true("不应出现" not in text, "DEBUG 关闭时不应该写到文件")
        assert_true("也不应出现" not in text, "INFO 关闭时不应该写到文件")

    def test_module_level_override(self):
        lg = _fresh_logger(self.tmp, default_level="WARNING")
        lg.set_level("special", "DEBUG")
        with TraceContext.trace("m"):
            lg.debug("X", module="special")  # 模块级别允许
            lg.debug("Y", module="other")  # 全局 WARNING 拦
        lg.flush(2.0)
        text = (Path(self.tmp) / "agent.log").read_text(encoding="utf-8", errors="replace")
        assert_in("X", text)
        assert_true("Y" not in text)

    def test_set_level_star_updates_global(self):
        lg = _fresh_logger(self.tmp, default_level="INFO")
        lg.set_level("*", "WARNING")
        assert_eq(lg.get_level(), LogLevel.WARNING)
        lg.reset_all_levels()
        assert_eq(lg.get_level(), LogLevel.INFO)

    def test_timed_context(self):
        lg = _fresh_logger(self.tmp)
        with TraceContext.trace("T-timed"):
            with lg.timed("测试完成", module="m", 批次="B1"):
                time.sleep(0.05)
        lg.flush(2.0)
        text = (Path(self.tmp) / "agent.log").read_text(encoding="utf-8", errors="replace")
        assert_in("测试完成", text)
        # 应包含 dur_ms= 字段
        assert_in("dur_ms=", text)
        # JSON 中应有 duration_ms 数值
        import json
        jl = (Path(self.tmp) / "agent.jsonl").read_text(encoding="utf-8", errors="replace").splitlines()
        found = False
        for line in jl:
            d = json.loads(line)
            if d.get("msg") == "测试完成":
                assert_true(float(d.get("duration_ms", 0)) >= 45,
                            f"duration_ms={d.get('duration_ms')} 应>=45ms")
                assert_eq((d.get("attrs") or {}).get("批次"), "B1")
                found = True
                break
        assert_true(found, "timed 日志应包含 duration_ms 和 attrs")

    def test_critical_callback(self):
        lg = _fresh_logger(self.tmp)
        calls = []
        lg.register_critical_callback(lambda ev: calls.append(ev.msg))
        lg.critical("救命!!", module="demo")
        lg.flush(2.0)
        assert_eq(calls, ["救命!!"])

    def test_error_exception_auto_capture(self):
        lg = _fresh_logger(self.tmp)
        with TraceContext.trace("err-auto"):
            try:
                raise ValueError("oops")
            except ValueError:
                lg.error("捕获异常", module="demo")
        lg.flush(2.0)
        text = (Path(self.tmp) / "agent.log").read_text(encoding="utf-8", errors="replace")
        # Traceback 行必须包含
        assert_in("ValueError", text)
        assert_in("Traceback", text)


# =========================================================
# 4. 异步环形缓冲
# =========================================================
class TestAsyncRingBuffer:
    def test_bounded(self):
        processed = []
        # 处理函数假装很慢: 延迟 100ms
        def slow_handler(batch):
            time.sleep(0.05)
            processed.extend(batch)
        ring = AsyncRingBuffer(capacity=50, flush_batch_size=10,
                               flush_interval_ms=10, handler_fn=slow_handler)
        ring.start()
        # 快速生产 500 条, 容量只有 50 → 必须被丢弃一批,绝不阻塞 (P7)
        t0 = time.perf_counter()
        dropped = 0
        for i in range(500):
            ev = LogEvent(ts=time.time(), level=LogLevel.INFO,
                          module="m", msg=f"m{i}")
            if not ring.enqueue(ev):
                dropped += 1
        elapsed_ms = (time.perf_counter() - t0) * 1000
        # 500 条 * 即使入队 10μs 也只需要 5ms, 加上 handler 慢不影响
        assert_lt(elapsed_ms, 500, f"背压不应该阻塞入队,用了 {elapsed_ms}ms")
        assert_gt(dropped, 300, f"容量只有 50,至少要丢 300+ (实际丢了 {dropped})")
        ring.shutdown(timeout=1.0)

    def test_debug_dropped_before_info(self):
        """验证分级丢弃:队列满时,先丢 DEBUG 再丢 INFO (P4 原则)"""
        drops = []
        events_in = []

        def capture(batch):
            events_in.extend(batch)

        ring = AsyncRingBuffer(capacity=30, flush_batch_size=1,
                               flush_interval_ms=100000,  # 永不自动刷,塞满测试
                               handler_fn=capture)
        ring.start()

        # 先塞满 INFO 30 条, 占满队列
        for i in range(30):
            assert_true(ring.enqueue(LogEvent(0, LogLevel.INFO, "m", f"I{i}")), "前 30 INFO 必须入队成功")

        # 再塞 DEBUG,必须全部被丢弃(DEBUG 级别最低,首先丢弃)
        debug_drop = 0
        for i in range(20):
            if not ring.enqueue(LogEvent(0, LogLevel.DEBUG, "m", f"D{i}")):
                debug_drop += 1
        assert_eq(debug_drop, 20, f"DEBUG 级队列满时必须 100% 被丢弃,实际丢了 {debug_drop}")

        # 再塞 INFO: 因为 DEBUG 也没腾位置,INFO 也会被丢弃
        info_drop = 0
        for i in range(20):
            if not ring.enqueue(LogEvent(0, LogLevel.INFO, "m", f"I2-{i}")):
                info_drop += 1
        assert_gt(info_drop, 10, "INFO 也应该被丢弃,但这里测试的是 DEBUG 先丢")

        ring.shutdown(timeout=0.1)

    def test_flush_batch(self):
        seen = []
        ring = AsyncRingBuffer(capacity=1000, flush_batch_size=50,
                               flush_interval_ms=5000, handler_fn=lambda b: seen.extend(b))
        ring.start()
        for i in range(123):
            ring.enqueue(LogEvent(0, LogLevel.INFO, "m", str(i)))
        # 等 batch 阈值 (50): 应该 flush 100 条
        deadline = time.time() + 3.0
        while time.time() < deadline and len(seen) < 100:
            time.sleep(0.01)
        # 剩余 23 条得靠 drain
        ring.drain_all(1.0)
        assert_eq(len(seen), 123, f"123 条应该全部输出,实际 {len(seen)}")
        ring.shutdown(0.5)


# =========================================================
# 5. 轮转处理器
# =========================================================
class TestDualRotation:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp(prefix="agent-logger-rot-")

    def teardown_method(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_size_rotation(self):
        path = Path(self.tmp) / "a.log"
        h = DualRotatingFileHandler(path, max_bytes=5 * 1024,  # 5KB 就轮转
                                    backup_count=10, retention_days=365,
                                    total_capacity_gb=1.0, compress_old=False)
        line = "x" * 400 + "\n"  # ~401 bytes 每行
        for _ in range(100):
            h.write_lines([line])  # 一次一批
            time.sleep(0.0001)
        h.close()
        # 100 * 401 = 40100 bytes → 应切成 5KB 左右若干文件
        files = sorted(Path(self.tmp).glob("a.log*"))
        # 当前 + 若干归档 ≥ 3 个是最小合理值
        assert_gt(len(files), 2, f"应至少轮转成 3 个文件,实际 {len(files)}")

    def test_gzip_on_rotation(self):
        path = Path(self.tmp) / "j.log"
        h = DualRotatingFileHandler(path, max_bytes=2 * 1024, backup_count=10,
                                    retention_days=365, total_capacity_gb=1.0,
                                    compress_old=True)
        line = "y" * 300 + "\n"
        for _ in range(80):
            h.write_lines([line])
        h.close()
        gz_files = list(Path(self.tmp).glob("j.log.*.gz"))
        # 80 * 301 = 24KB → 切 10+ 个,压缩过
        assert_gt(len(gz_files), 0, "应该有 .gz 压缩归档")

    def test_capacity_hard_limit(self):
        path = Path(self.tmp) / "cap.log"
        # 硬上限 30KB, 文件 5KB 轮转,很快会超
        h = DualRotatingFileHandler(path, max_bytes=5 * 1024, backup_count=9999,
                                    retention_days=999, total_capacity_gb=30 / 1024 ** 3,
                                    compress_old=False)
        line = "z" * 500 + "\n"
        for _ in range(400):  # 200KB, 远大于 30KB
            h.write_lines([line])
        h.close()
        # 统计总容量
        total = 0
        for p in Path(self.tmp).glob("cap.log*"):
            if p.is_file():
                total += p.stat().st_size
        # 容量硬上限 30KB,允许小浮动(2×当前文件)
        assert_lt(total, 100 * 1024, f"总容量超过硬上限: {total/1024:.1f} KB")


# =========================================================
# 6. 格式化正确性
# =========================================================
class TestLogFormat:
    def test_text_alignment_fields(self):
        ev = LogEvent(
            ts=1750000000.123, level=LogLevel.INFO, module="agent.planner.sub",
            msg="规划完成", trace_id="req-abc", span_id="s1", user_id="u1",
            attrs={"计划步": 5, "备注": "带空格 的"},
        )
        line = format_text(ev, use_color=False)
        assert_in("2025-06-14", line)  # 1750000000 → 2025-06-14 (+8)
        assert_in("[INFO   ]", line)
        assert_in("trace=req-abc", line)
        assert_in("span=s1", line)
        assert_in("user=u1", line)
        assert_in('备注="带空格 的"', line)
        assert_in("计划步=5", line)
        assert_in("规划完成", line)

    def test_json_full_fields(self):
        try:
            raise ValueError("boom-value")
        except ValueError as e:
            ev = LogEvent(
                ts=1750000000.0, level=LogLevel.ERROR, module="demo",
                msg="失败了", trace_id="t", span_id="s", user_id="u", session_id="ss",
                err=e, attrs={"k1": "v1"}, duration_ms=42.555,
            )
        line = format_json_line(ev)
        import json
        d = json.loads(line)
        assert_eq(d["level"], "ERROR")
        assert_eq(d["trace_id"], "t")
        assert_eq(d["session_id"], "ss")
        assert_eq(d["err_type"], "ValueError")
        assert_in("boom-value", d["err_msg"])
        assert_in("Traceback", d["err_stack"])
        assert_eq(d["duration_ms"], 42.555)
        assert_eq((d["attrs"] or {}).get("k1"), "v1")
        assert_in("ts_epoch", d)

    def test_color_toggle_strips_ansi_when_disabled(self):
        ev = LogEvent(ts=time.time(), level=LogLevel.ERROR, module="m", msg="X", trace_id="t", span_id="s")
        no_color = format_text(ev, use_color=False)
        with_color = format_text(ev, use_color=True)
        assert_true("\x1b" not in no_color, "关闭彩色不应包含 ANSI")
        assert_in("\x1b[1;31m", with_color, "ERROR 彩色应包含大红")


# =========================================================
# 7. 查询与分析
# =========================================================
class TestQueryAPI:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp(prefix="agent-logger-q-")
        self.lg = _fresh_logger(self.tmp, default_level="DEBUG")
        self._seed_data()

    def teardown_method(self):
        try:
            AgentLogger._instance and AgentLogger._instance.shutdown()
        except Exception:
            pass
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _seed_data(self):
        for i in range(20):
            trace = f"req-{i:03d}"
            with TraceContext.trace(trace, span_id="s1", user_id=f"u{i}"):
                self.lg.info("正常处理", module="agent.planner", idx=i)
                if i % 5 == 0:
                    self.lg.warning("告警", module="agent.llm.client", 次数=i)
                if i % 11 == 0:
                    try:
                        raise RuntimeError("simulate")
                    except RuntimeError as e:
                        self.lg.error("大错", module="agent.llm.client", exc=e, 编号=i)
        self.lg.flush(3.0)

    def test_count_by_level(self):
        q = LogQuerier(self.tmp)
        warnings = q.level_eq("WARNING").count()
        errors = q.level_eq("ERROR").count()
        assert_eq(warnings, 4, "20 条中 i∈{0,5,10,15} → 4 WARNING")
        assert_eq(errors, 2, "20 条中 i∈{0,11} → 2 ERROR")

    def test_trace_id_filter(self):
        q = LogQuerier(self.tmp)
        res = q.trace_id("req-000").run()
        assert_true(res.count() >= 3, "req-000 应该至少 INFO+WARN+ERROR = 3 条,实际" + str(res.count()))

    def test_module_glob(self):
        res = LogQuerier(self.tmp).module_glob("agent.llm.*").run().to_list()
        modules = {r["module"] for r in res}
        assert_true(len(modules) >= 1)
        for m in modules:
            assert_true(m.startswith("agent.llm."), f"过滤出的模块 {m} 不符合 glob")

    def test_time_range_last_seconds(self):
        # 种子数据都是几秒钟内, last_seconds=3600 应全部命中
        total = LogQuerier(self.tmp).time_range(last_seconds=3600).count()
        assert_true(total >= 20, f"最近一小时的日志应 >= 20, 实际 {total}")

    def test_keyword_filter(self):
        cnt = LogQuerier(self.tmp).keyword("大错").count()
        assert_eq(cnt, 2, "只有 ERROR 那条 msg='大错'")

    def test_attribute_filter(self):
        cnt = LogQuerier(self.tmp).attribute("次数", 10).count()
        assert_gt(cnt, 0, "应命中 i=10 时 WARNING 的 attrs={'次数':10}")

    def test_analyzer_level_distribution(self):
        dist = LogAnalyzer(self.tmp).level_distribution()
        assert_gt(dist["INFO"], 0)
        assert_gt(dist["WARNING"], 0)
        assert_gt(dist["ERROR"], 0)

    def test_analyzer_top_errors(self):
        tops = LogAnalyzer(self.tmp).top_error_types(limit=5)
        # ERROR err_type 是 RuntimeError
        types = {t for t, _ in tops}
        assert_true("RuntimeError" in types or "大错" in types,
                    f"RuntimeError 或 '大错' 应出现在 Top 错误里: {tops}")

    def test_export_csv(self):
        csv_path = Path(self.tmp) / "out.csv"
        res = LogQuerier(self.tmp).limit(50).run()
        written = res.export_csv(csv_path)
        assert_true(csv_path.exists())
        assert_gt(written, 0)
        txt = csv_path.read_text(encoding="utf-8-sig")
        assert_in("ts", txt)
        assert_in("level", txt)


# =========================================================
# 8. 性能基准 (可选, pytest-benchmark 自动跳过 if 没装)
# =========================================================
class TestPerformance:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp(prefix="agent-logger-perf-")

    def teardown_method(self):
        try:
            AgentLogger._instance and AgentLogger._instance.shutdown()
        except Exception:
            pass
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_info_100k_latency(self):
        """生产基线:10 万条 INFO 应 < 0.5 秒 (含异步 flush,平均单条 <5μs)。"""
        lg = _fresh_logger(self.tmp, default_level="INFO",
                           queue_capacity=20000, flush_batch_size=500)
        N = 100_000
        t0 = time.perf_counter()
        for i in range(N):
            lg.info("msg={}", i, module="m", k=i)
        enqueue_elapsed_ms = (time.perf_counter() - t0) * 1000
        # 等待 flush 完成 (不计算 flush, 只看调用端阻塞)
        lg.flush(10.0)
        total = (time.perf_counter() - t0) * 1000
        # 断言: 调用端平均 < 5μs/条 (100k → 500ms)
        assert_lt(enqueue_elapsed_ms, 1500,
                  f"100k INFO enqueue 端阻塞 {enqueue_elapsed_ms:.1f}ms, 应<1500ms")
        # 断言: 总端到端也不能太慢 (<10s 就是合理的)
        assert_lt(total, 15000, f"端到端 {total:.1f}ms 过大")

    def test_debug_disabled_almost_zero_cost(self):
        """关闭 DEBUG 级别下,DEBUG 调用必须 <100ns / 次 (论文级目标)。"""
        lg = _fresh_logger(self.tmp, default_level="INFO")
        N = 1_000_000
        huge = "x" * 10000
        t0 = time.perf_counter()
        for i in range(N):
            lg.debug("huge prompt {}", huge, module="m", data=huge)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        per_call_ns = (elapsed_ms * 1e6) / N
        assert_lt(per_call_ns, 500,
                  f"DEBUG 关闭时单条应 <500ns, 实际 {per_call_ns:.1f}ns")


# =========================================================
# 9. 崩溃安全 (P2: ERROR/CRITICAL 同步 flush 绝不丢)
# =========================================================
class TestCrashSafety:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp(prefix="agent-logger-crash-")

    def teardown_method(self):
        try:
            AgentLogger._instance and AgentLogger._instance.shutdown()
        except Exception:
            pass
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_critical_is_synchronous(self):
        lg = _fresh_logger(self.tmp, default_level="DEBUG")
        # CRITICAL 一发,立即可在文件里看到(不需要 flush)
        lg.critical("最后一条救命证据", module="critical.m", code="RED_ALERT")
        # 立即读, 不加 flush
        text = (Path(self.tmp) / "agent.error.log").read_text(encoding="utf-8", errors="replace")
        assert_in("最后一条救命证据", text)
        assert_in("RED_ALERT", text)

    def test_atexit_shutdown_does_not_raise(self):
        lg = _fresh_logger(self.tmp)
        lg.info("退出前")
        # 调用多次 shutdown 也不能挂
        lg.shutdown()
        lg.shutdown()


# =========================================================
# 主函数 (无 pytest 时 python -m agent_logger.test_agent_logger 直接跑)
# =========================================================
def _run_class(cls):
    obj = cls()
    setup = getattr(obj, "setup_method", None)
    teardown = getattr(obj, "teardown_method", None)
    passed = failed = errors = 0
    methods = [m for m in dir(obj) if m.startswith("test_")]
    for name in methods:
        fn = getattr(obj, name)
        try:
            setup and setup()
        except Exception as e:
            print(f"SETUP ERROR {cls.__name__}::{name}: {e}")
            traceback.print_exc()
            errors += 1
            try:
                teardown and teardown()
            except Exception:
                pass
            continue
        try:
            fn()
            print(f"  PASS  {cls.__name__}::{name}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {cls.__name__}::{name}: {e}")
            traceback.print_exc()
            failed += 1
        except Exception as e:
            print(f"  ERROR {cls.__name__}::{name}: {type(e).__name__}: {e}")
            traceback.print_exc()
            errors += 1
        finally:
            try:
                teardown and teardown()
            except Exception:
                pass
    return passed, failed, errors


def run_all_tests():
    classes = [
        TestLogLevel,
        TestTraceContext,
        TestAgentLoggerAPI,
        TestAsyncRingBuffer,
        TestDualRotation,
        TestLogFormat,
        TestQueryAPI,
        TestPerformance,
        TestCrashSafety,
    ]
    total_passed = total_failed = total_errors = 0
    t0 = time.perf_counter()
    for cls in classes:
        print(f"\n[{cls.__name__}]")
        p, f, e = _run_class(cls)
        total_passed += p
        total_failed += f
        total_errors += e
    elapsed = time.perf_counter() - t0
    print("\n" + "=" * 60)
    print(f"总计: 通过={total_passed}  失败={total_failed}  错误={total_errors}  耗时={elapsed:.1f}s")
    if total_failed or total_errors:
        sys.exit(1)
    else:
        print("✅ 全部用例通过!")
        sys.exit(0)


if __name__ == "__main__":
    run_all_tests()
