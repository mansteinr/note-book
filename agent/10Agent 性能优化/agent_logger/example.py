"""Agent Logger 使用示例。

运行: python -m agent_logger.example
(需在 agent_logger 父目录下执行,或将该父目录加入 sys.path)

查看日志产物: ls -la ./logs/
"""
from __future__ import annotations

import os
import sys
import time

# 保证从任意目录运行都能 import agent_logger
_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from agent_logger.core import (  # noqa: E402
    AgentLogger,
    LogLevel,
    TraceContext,
    get_logger,
)
from agent_logger.query import LogAnalyzer, LogQuerier  # noqa: E402


def simulate_agent_planning_and_tools(logger: AgentLogger, user_id: str, prompt: str) -> None:
    """模拟一次 Agent 调用完整链路,展示 trace_id 贯穿 + timed 计时。"""
    import random

    # 一次请求 → 一个独立 trace_id
    trace_id = "req-" + os.urandom(6).hex()
    with TraceContext.trace(trace_id, span_id="entry", user_id=user_id, session_id="s-001"):
        logger.info("收到用户请求", module="agent.entry", prompt_len=len(prompt))

        # 1) Planner 规划 (自动计时 + INFO 完成日志)
        with logger.timed("Planner 规划完成", module="agent.planner", steps=5):
            time.sleep(0.02)
            # 超大 Prompt DEBUG 级才打印:关闭时零成本
            logger.debug("Planner 完整 System Prompt: {}", prompt * 100, module="agent.planner")

        # 2) 模拟 LLM 调用 3 次重试,第 3 次成功
        for i in range(1, 4):
            with TraceContext.trace(span_id=f"llm-call-0{i}"):
                try:
                    with logger.timed("LLM 调用完成", module="agent.llm.client",
                                      模型="qwen2-72b", 重试次数=i):
                        time.sleep(0.05 * i)
                        if i < 3:
                            raise TimeoutError(f"Upstream timeout attempt {i}/3")
                        logger.info("LLM 返回成功", module="agent.llm.client",
                                    prompt_tokens=1200, completion_tokens=480)
                        break
                except TimeoutError as e:
                    logger.warning("LLM 自动重试中", module="agent.llm.client",
                                   exc=e, 第几次=i, 最多=3, 错误=type(e).__name__)
        else:
            # 循环没 break 就是全失败了
            logger.error("LLM 3 次重试全部失败,标记本次请求降级",
                         module="agent.llm.client", 模型="qwen2-72b")

        # 3) 工具调用 (RAG 检索 + 计算器)
        with TraceContext.trace(span_id="tool-01-rag"):
            try:
                with logger.timed("RAG 检索完成", module="agent.tool.rag", 候选=8, topk=3):
                    time.sleep(0.03)
                    logger.debug("RAG 候选文档相似度: {}",
                                 [0.92, 0.81, 0.77, 0.64, 0.55],
                                 module="agent.tool.rag")
            except Exception as e:
                logger.error("RAG 异常", module="agent.tool.rag", exc=e)

        # 4) 偶尔抛一个 WARNING 级的示例
        if random.random() < 0.3:
            logger.warning("检测到低置信度输出,已追加置信度标签",
                           module="agent.safety", conf=random.uniform(0.4, 0.7))

        with TraceContext.trace(span_id="final"):
            logger.info("Agent 响应完成", module="agent.entry",
                        总耗时_ms=420.5, 最终步=5)


def demo_logger_query(log_dir: str) -> None:
    """查询与分析 API 演示。"""
    print("\n====== 查询演示 ======")
    q = LogQuerier(log_dir)

    # 1. WARNING 及以上
    print("\n[1] WARNING+ 总数:",
          q.level_ge("WARNING").count())

    # 2. Agent LLM 客户端模块
    print("\n[2] agent.llm.client 模块日志 (最新5条):")
    rows = (LogQuerier(log_dir)
            .module_glob("agent.llm.*")
            .limit(5)
            .order_by("ts", desc=True)
            .run()
            .to_list())
    for r in rows:
        print(f"  - {r.get('ts','')[:23]} [{r.get('level',''):>7}] {r.get('module','')} -> {r.get('msg','')}")

    # 3. 统计分析
    print("\n[3] 过去全部日志的级别分布:")
    for lv, c in LogAnalyzer(log_dir).level_distribution().items():
        if c > 0:
            print(f"    {lv:<8}: {c:>6} 条")

    print("\n[4] Top 错误类型:")
    for key, cnt in LogAnalyzer(log_dir).top_error_types(limit=5):
        if key == "<unknown>":
            continue
        print(f"    {cnt:>4} 次  {str(key)[:80]}")

    print("\n[5] Planner/LLM 耗时 P50/P95/P99:")
    for kw in ["Planner 规划完成", "LLM 调用完成"]:
        stats = LogAnalyzer(log_dir).duration_analysis(kw)
        if stats["count"]:
            print(f"    {kw:20s} count={stats['count']:>3} P50={stats['p50_ms']:>7.2f}ms "
                  f"P95={stats['p95_ms']:>7.2f}ms P99={stats['p99_ms']:>7.2f}ms")

    # 4. 导出
    rows = LogQuerier(log_dir).level_ge("WARNING").limit(100).run()
    csv_path = os.path.join(log_dir, "_sample_warnings.csv")
    rows.export_csv(csv_path)
    print(f"\n[6] WARNING+ 前 100 条已导出到 CSV: {csv_path}")


def main() -> int:
    print("=" * 60)
    print("Agent 日志系统 — 使用示例运行中...")
    print("=" * 60)

    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
    print(f"日志目录: {log_dir}\n")

    # 每次示例重跑,清理上次产物 (可选)
    # for f in Path(log_dir).glob("*"):
    #     if f.is_file():
    #         f.unlink()

    # ============ 1. 初始化日志 =============
    logger = get_logger(
        log_dir=log_dir,
        default_level="DEBUG",  # 示例全开
        queue_capacity=5000,
        flush_interval_ms=100,
    )

    # 注册 CRITICAL 告警回调 (模拟飞书/钉钉推送)
    def fake_pagerduty_cb(ev):
        print(f"\n  [P0 飞书告警已发送] {ev.level.name}: {ev.msg}\n")

    logger.register_critical_callback(fake_pagerduty_cb)

    # ============ 2. 动态级别演示 =============
    print("-> 默认全局级别 =", logger.get_level().name)
    logger.set_level("agent.planner", "WARNING")  # 临时静默 planner 的 DEBUG/INFO
    print("-> 之后 agent.planner 级别 =", logger.get_level("agent.planner").name)
    logger.reset_level("agent.planner")

    # ============ 3. 模拟若干并发请求 =============
    N_USERS = 5
    print(f"\n-> 模拟 {N_USERS} 个用户请求... (每请求完整链路)")
    for i in range(1, N_USERS + 1):
        simulate_agent_planning_and_tools(
            logger,
            user_id=f"u{i:04d}",
            prompt=f"你好,请帮我分析订单 #{1000 + i} 的物流情况。",
        )

    # ============ 4. 演示一次 ERROR 和一次 CRITICAL ============
    print("\n-> 演示 ERROR 捕获 (自动附带 traceback):")
    with TraceContext.trace("req-demo-error", span_id="demo-err"):
        try:
            1 / 0
        except ZeroDivisionError:
            logger.error("演示: 除以零捕获", module="demo", 附加字段="hello")

    print("-> 演示 CRITICAL (同步 flush + 触发告警回调):")
    logger.critical("演示: 系统级 CRITICAL,将立即触发告警回调",
                    module="agent.scheduler", 队列长度=9999)

    # ============ 5. flush 然后退出 ============
    logger.flush(timeout=3.0)

    # ============ 6. 查询 & 分析 ============
    demo_logger_query(log_dir)

    # ============ 7. 文件清单 ============
    print("\n====== 生成的日志文件 ======")
    for f in sorted(os.listdir(log_dir)):
        fp = os.path.join(log_dir, f)
        if os.path.isfile(fp):
            size_kb = os.stat(fp).st_size / 1024
            print(f"  {size_kb:7.1f} KB  {f}")

    print("\n✅ 示例运行完成。")
    logger.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
