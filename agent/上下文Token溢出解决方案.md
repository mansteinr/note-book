# 上下文 Token 溢出解决方案

> 本文档针对 AI Agent 系统中频发的"上下文 Token 溢出"问题，提供一套从根因定位、方案设计、实施步骤到验证回滚的完整闭环方案，并包含至少一种可独立运行的兜底方案，确保主方案失效时系统仍能稳定提供基础功能。

---

## 目录

- [1. 问题分析与根本原因定位](#1-问题分析与根本原因定位)
  - [1.1 问题现象](#11-问题现象)
  - [1.2 根本原因定位](#12-根本原因定位)
  - [1.3 影响面评估](#13-影响面评估)
- [2. 技术解决方案设计与实现细节](#2-技术解决方案设计与实现细节)
  - [2.1 总体架构](#21-总体架构)
  - [2.2 预算计量层：Token 预算控制器](#22-预算计量层token-预算控制器)
  - [2.3 压缩层：分层摘要与选择性保留](#23-压缩层分层摘要与选择性保留)
  - [2.4 检索层：外部记忆与 RAG 回填](#24-检索层外部记忆与-rag-回填)
  - [2.5 调度层：滑动窗口 + 优先级队列](#25-调度层滑动窗口--优先级队列)
  - [2.6 兼容性与性能保障](#26-兼容性与性能保障)
- [3. 实施步骤与资源需求](#3-实施步骤与资源需求)
  - [3.1 实施阶段划分](#31-实施阶段划分)
  - [3.2 资源需求清单](#32-资源需求清单)
  - [3.3 关键里程碑](#33-关键里程碑)
- [4. 测试验证方法与成功标准](#4-测试验证方法与成功标准)
  - [4.1 测试矩阵](#41-测试矩阵)
  - [4.2 成功标准（可量化）](#42-成功标准可量化)
- [5. 兜底方案：Token 硬截断 + 工具降级](#5-兜底方案token-硬截断--工具降级)
  - [5.1 设计目标与触发条件](#51-设计目标与触发条件)
  - [5.2 执行流程](#52-执行流程)
  - [5.3 资源消耗](#53-资源消耗)
  - [5.4 恢复机制](#54-恢复机制)
- [6. 评估指标与回滚策略](#6-评估指标与回滚策略)
  - [6.1 可量化评估指标](#61-可量化评估指标)
  - [6.2 回滚策略](#62-回滚策略)
- [7. 风险与兼容性说明](#7-风险与兼容性说明)
- [8. 附录](#8-附录)

---

## 1. 问题分析与根本原因定位

### 1.1 问题现象

在长会话、多工具调用、大文档处理等场景下，Agent 系统出现以下典型症状：

| 现象 | 表现 | 触发频率 |
|------|------|----------|
| API 调用失败 | 返回 `context_length_exceeded` 错误码 | 高 |
| 响应截断 | 输出中途停止，`finish_reason=length` | 中 |
| 性能劣化 | 单轮响应时延从 2s 飙升至 15s+ | 高 |
| 成本飙升 | 单会话 Token 消耗较基线增长 5–10 倍 | 高 |
| 上下文丢失 | Agent"忘记"早期约定（角色、约束、变量） | 中 |

### 1.2 根本原因定位

通过五问法（5 Why）层层下钻：

```
现象：API 报 context_length_exceeded
 └─ Why1：发送给 LLM 的 prompt 总 token 超过模型上限（如 GPT-4o 128K）
     └─ Why2：上下文中累积了完整历史消息 + 工具返回 + 系统提示，未做裁剪
         └─ Why3：缺少统一的 Token 预算管理与预检机制
             └─ Why4：架构上把"上下文"等同于"全部历史"，无分层与外置策略
                 └─ Why5（根因）：缺少"记忆分层 + 预算控制 + 检索回填"三位一体的上下文治理体系
```

**根因结论**：问题本质是 **"无界上下文增长"与"有限模型窗口"之间的结构性矛盾**，而非单纯的工程 Bug。

**根因分类**：

1. **架构根因（70%）**：上下文全量保留，无压缩、无外置、无淘汰。
2. **工程根因（20%）**：缺少 Token 预检、无重试降级、工具返回未截断。
3. **业务根因（10%）**：任务设计鼓励超长上下文（如全量文档塞入 prompt）。

### 1.3 影响面评估

| 维度 | 影响 |
|------|------|
| 功能 | 长会话不可用、多轮工具调用中断、RAG 场景召回失败 |
| 性能 | P95 时延劣化 5–8 倍，首 Token 时延显著增加 |
| 成本 | 单会话成本增长 5–10 倍，规模化后月度账单失控 |
| 体验 | 用户感知"Agent 失忆""答非所问""任务中断" |
| 稳定性 | 错误率峰值达 30%+，触发限流与级联失败风险 |

---

## 2. 技术解决方案设计与实现细节

### 2.1 总体架构

采用 **"预算计量 + 分层压缩 + 检索回填 + 滑动窗口"** 四层架构：

```
┌─────────────────────────────────────────────────────────┐
│                  用户请求 / 工具返回                       │
└───────────────────────┬─────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────┐
│  L1 预算计量层（Token Budget Controller）                 │
│  - 实时估算当前上下文 Token 数                            │
│  - 预留输出预算（output_reserved）                       │
│  - 触发压缩 / 截断 / 外置阈值                             │
└───────────────────────┬─────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────┐
│  L2 压缩层（Hierarchical Summarizer）                    │
│  - 滚动摘要：旧消息 → 摘要段                              │
│  - 选择性保留：关键消息（系统/工具/用户约定）原样保留        │
│  - 有损压缩：冗余工具输出 → 关键字段                       │
└───────────────────────┬─────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────┐
│  L3 检索层（External Memory + RAG）                      │
│  - 被压缩/外置的消息写入向量库                             │
│  - 当前请求作为 query，召回 Top-K 相关片段回填             │
│  - 知识图谱存储实体关系，避免重复展开                      │
└───────────────────────┬─────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────┐
│  L4 调度层（Sliding Window + Priority Queue）            │
│  - 滑动窗口：保留最近 N 轮原文                            │
│  - 优先级队列：System > Tool > Recent User > History      │
│  - 组装最终 prompt，确保 ≤ 模型上限                       │
└───────────────────────┬─────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────┐
│                    LLM 调用                              │
└─────────────────────────────────────────────────────────┘
```

### 2.2 预算计量层：Token 预算控制器

**职责**：在每次 LLM 调用前，精确估算上下文 Token 数，并根据预算策略触发上层动作。

**核心参数**：

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `MODEL_LIMIT` | 模型上下文上限 | 128000（GPT-4o） |
| `OUTPUT_RESERVED` | 预留输出 Token | 4096 |
| `SAFE_MARGIN` | 安全裕度（估算误差缓冲） | 1024 |
| `COMPRESS_THRESHOLD` | 触发压缩阈值 | 80% × (MODEL_LIMIT - OUTPUT_RESERVED) |
| `TRUNCATE_THRESHOLD` | 触发硬截断阈值（兜底） | 95% × (MODEL_LIMIT - OUTPUT_RESERVED) |
| `EXTERNALIZE_THRESHOLD` | 触发外置存储阈值 | 60% × (MODEL_LIMIT - OUTPUT_RESERVED) |

**实现要点**：

- 使用与目标模型一致的 Tokenizer（如 `tiktoken` for OpenAI）进行精确计数，避免字符数近似带来的 ±15% 误差。
- 维护一个 `ContextBudget` 对象，记录各类消息的 Token 占用：

```python
from dataclasses import dataclass, field
from typing import List, Dict
import tiktoken

@dataclass
class MessageToken:
    role: str
    content: str
    tokens: int
    priority: int          # 1=System, 2=Tool, 3=Recent, 4=History
    compressible: bool     # 是否可压缩
    externalized: bool = False

@dataclass
class ContextBudget:
    model_limit: int = 128000
    output_reserved: int = 4096
    safe_margin: int = 1024
    messages: List[MessageToken] = field(default_factory=list)

    def _enc(self):
        return tiktoken.encoding_for_model("gpt-4o")

    def available_input(self) -> int:
        return self.model_limit - self.output_reserved - self.safe_margin

    def current_tokens(self) -> int:
        return sum(m.tokens for m in self.messages if not m.externalized)

    def usage_ratio(self) -> float:
        return self.current_tokens() / self.available_input()

    def should_externalize(self) -> bool:
        return self.usage_ratio() >= 0.60

    def should_compress(self) -> bool:
        return self.usage_ratio() >= 0.80

    def should_truncate(self) -> bool:
        return self.usage_ratio() >= 0.95
```

### 2.3 压缩层：分层摘要与选择性保留

**策略矩阵**：

| 消息类型 | 压缩策略 | 保留方式 |
|----------|----------|----------|
| System Prompt | 不压缩 | 原样保留（最高优先级） |
| 用户关键约定（含"请记住""约定""规则"等关键词） | 不压缩 | 原样保留 + 标记 |
| 最近 N 轮对话（N=3~5） | 不压缩 | 原样保留 |
| 工具调用结果（大块 JSON/HTML） | 有损压缩 | 保留关键字段 + 截断体 |
| 历史对话（超出滑动窗口） | 滚动摘要 | 替换为摘要段 |
| 重复/冗余信息 | 去重 | 仅保留最新版本 |

**滚动摘要算法**：

```python
def rolling_summarize(old_messages: List[MessageToken], llm_client) -> str:
    """
    将一批旧消息压缩为摘要。
    - 输入：待压缩的消息列表
    - 输出：摘要文本（约 200~400 tokens）
    - 策略：使用小模型（如 gpt-4o-mini）降低成本
    """
    conversation = "\n".join(f"[{m.role}] {m.content}" for m in old_messages)
    prompt = (
        "请将以下对话压缩为 300 tokens 以内的摘要，保留：\n"
        "1. 用户的核心目标与约束\n"
        "2. 已完成的决策与结论\n"
        "3. 关键实体名称、数值、时间\n"
        "4. 未解决的问题\n"
        "丢弃寒暄、重复、中间过程细节。\n\n"
        f"对话内容：\n{conversation}"
    )
    summary = llm_client.complete(model="gpt-4o-mini", prompt=prompt, max_tokens=400)
    return summary
```

**工具结果压缩示例**：

```python
def compress_tool_result(raw: str, max_tokens: int = 500) -> str:
    """
    对工具返回的大块结果进行结构化压缩。
    """
    # 1. 若为 JSON，提取关键字段
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            keys_to_keep = {"id", "title", "name", "status", "error", "summary", "result"}
            compressed = {k: v for k, v in data.items() if k in keys_to_keep}
            compressed["_omitted_keys"] = list(set(data.keys()) - keys_to_keep)
            return json.dumps(compressed, ensure_ascii=False)[:max_tokens * 4]
    except Exception:
        pass
    # 2. 非 JSON：保留首尾 + 中间截断
    if len(raw) > max_tokens * 4:
        head = raw[: max_tokens * 2]
        tail = raw[-max_tokens * 2 :]
        return f"{head}\n...[truncated {len(raw) - max_tokens*4} chars]...\n{tail}"
    return raw
```

### 2.4 检索层：外部记忆与 RAG 回填

**目标**：将"不常用但需要时可取回"的上下文外置，避免常驻 prompt。

**存储后端选型**：

| 后端 | 用途 | 优势 | 成本 |
|------|------|------|------|
| 向量数据库（Milvus / Qdrant / pgvector） | 语义相似召回 | 高召回率 | 中 |
| Redis（按会话 ID 分区） | 热缓存 | 低延迟 | 低 |
| 关系型 DB（PostgreSQL） | 结构化事实存储 | 事务一致 | 低 |
| 知识图谱（Neo4j） | 实体关系存储 | 多跳推理 | 高 |

**回填流程**：

```
当前用户请求 → embedding → 向量库 Top-K 召回 → 相关性过滤（score>0.75）
                                                ↓
                    组装为 [retrieved_context] 块注入 prompt
```

**实现要点**：

- 每条被外置的消息写入向量库时，记录元数据：`session_id`、`turn_id`、`role`、`timestamp`、`importance_score`。
- 回填时优先返回高 `importance_score` 的片段，防止低价值信息挤占预算。
- 单次回填 Token 上限建议 ≤ 2000，避免回填本身又造成溢出。

### 2.5 调度层：滑动窗口 + 优先级队列

**最终 prompt 组装顺序**（从前往后）：

```
1. System Prompt（必留）
2. 用户关键约定（必留，标记 [PERSISTENT_RULES]）
3. 检索回填片段（[RETRIEVED_CONTEXT]）
4. 滚动摘要段（[CONVERSATION_SUMMARY]）
5. 最近 N 轮原文（[RECENT_TURNS]）
6. 当前用户输入
```

**优先级淘汰算法**：

```python
def assemble_prompt(budget: ContextBudget, recent_n: int = 4) -> List[dict]:
    """
    按优先级组装最终 prompt，确保不超过预算。
    """
    available = budget.available_input()
    result = []

    # P1: System（必留）
    sys_msgs = [m for m in budget.messages if m.priority == 1]
    result.extend(sys_msgs)
    available -= sum(m.tokens for m in sys_msgs)

    # P2: 用户关键约定（必留）
    rule_msgs = [m for m in budget.messages if m.priority == 2]
    result.extend(rule_msgs)
    available -= sum(m.tokens for m in rule_msgs)

    # P3: 最近 N 轮原文
    recent = [m for m in budget.messages if m.priority == 3][-recent_n:]
    for m in recent:
        if available - m.tokens >= 0:
            result.append(m)
            available -= m.tokens

    # P4: 历史摘要（剩余预算允许则加入）
    history = [m for m in budget.messages if m.priority == 4]
    for m in history:
        if available - m.tokens >= 0:
            result.append(m)
            available -= m.tokens

    return [{"role": m.role, "content": m.content} for m in result]
```

### 2.6 兼容性与性能保障

| 维度 | 保障措施 |
|------|----------|
| 模型兼容 | Tokenizer 按目标模型动态切换；对无官方 Tokenizer 的模型用 `len(text)/3.5` 近似并放大 10% 裕度 |
| 框架兼容 | 以中间件形式接入 LangChain / LlamaIndex / 自研框架，提供 `pre_llm_call` 钩子 |
| 性能 | 摘要使用小模型（gpt-4o-mini / Claude Haiku）；向量召回设 100ms 超时；预算计量本地计算，无网络开销 |
| 并发 | 预算控制器按会话 ID 加锁，防止并发写入导致预算失准 |
| 可观测 | 每次调用记录 `input_tokens / output_tokens / compressed_tokens / externalized_count`，输出结构化日志 |

---

## 3. 实施步骤与资源需求

### 3.1 实施阶段划分

#### 阶段一：止血（1–2 天）

- 上线 **Token 预算控制器** + **硬截断兜底**（见第 5 章）
- 接入结构化日志，统计溢出错误率基线
- **目标**：溢出错误率从 30% 降至 < 1%

#### 阶段二：治标（1–2 周）

- 实现 **滚动摘要** + **工具结果压缩**
- 实现 **滑动窗口调度**
- 灰度 10% → 50% → 100%
- **目标**：单会话 Token 消耗降低 60%+

#### 阶段三：治本（3–6 周）

- 接入 **向量库外置记忆** + **RAG 回填**
- 接入 **知识图谱**（可选，针对实体密集场景）
- 全量上线 + 监控大盘
- **目标**：长会话（50 轮+）稳定可用，成本回到基线 1.2 倍内

### 3.2 资源需求清单

| 资源类型 | 规格 | 数量 | 用途 |
|----------|------|------|------|
| 计算资源（CPU/内存） | 4C8G | 2 实例 | 预算控制器 + 调度层 |
| 向量数据库 | Milvus 单节点 / pgvector | 1 | 外置记忆存储 |
| 缓存 | Redis 4G | 1 | 热会话上下文缓存 |
| 小模型 API | gpt-4o-mini / Claude Haiku | 按量 | 滚动摘要压缩 |
| Embedding API | text-embedding-3-small | 按量 | 外置记忆向量化 |
| 监控 | Prometheus + Grafana | 1 套 | 指标采集与告警 |
| 人力 | 后端 1 + 算法 1 + 测试 1 | 6 周 | 开发与验证 |

### 3.3 关键里程碑

| 里程碑 | 交付物 | 验收标准 |
|--------|--------|----------|
| M1 止血上线 | 预算控制器 + 兜底截断 | 错误率 < 1% |
| M2 压缩上线 | 摘要 + 工具压缩 + 滑动窗口 | Token 消耗降 60% |
| M3 外置记忆 | 向量库 + RAG 回填 | 50 轮长会话通过 |
| M4 全量监控 | 指标大盘 + 告警 | P0 告警 5 分钟内响应 |

---

## 4. 测试验证方法与成功标准

### 4.1 测试矩阵

| 测试类别 | 场景 | 方法 | 通过标准 |
|----------|------|------|----------|
| 单元测试 | Token 计数准确性 | 构造已知 Token 数的文本，断言计数误差 < 1% | 覆盖率 ≥ 90% |
| 单元测试 | 预算触发阈值 | 模拟不同 usage_ratio，验证 externalize/compress/truncate 触发 | 100% 触发正确 |
| 集成测试 | 长会话压力 | 构造 100 轮对话 + 20 次工具调用 | 0 次 context_length_exceeded |
| 集成测试 | 大文档注入 | 单次注入 200K Token 文档 | 不溢出，关键信息保留率 ≥ 90% |
| 压测 | 并发会话 | 100 并发 × 50 轮 | P95 时延 < 5s，错误率 < 0.1% |
| 回归测试 | 业务功能 | 既有用例全量回归 | 功能回归通过率 100% |
| 用户评估 | 上下文连贯性 | 人工评估 50 轮后 Agent 是否"记得"早期约定 | 连贯性评分 ≥ 4/5 |
| 成本评估 | 单会话成本 | 对比上线前后 Token 消耗 | 成本降低 ≥ 50% |

### 4.2 成功标准（可量化）

| 指标 | 基线 | 目标 |
|------|------|------|
| 溢出错误率 | 30% | < 0.1% |
| 单会话 Token 消耗 | 基线 100% | ≤ 40% |
| P95 响应时延 | 15s | < 5s |
| 50 轮长会话成功率 | 20% | ≥ 99% |
| 关键信息保留率 | N/A | ≥ 90% |
| 单会话成本 | 基线 100% | ≤ 50% |

---

## 5. 兜底方案：Token 硬截断 + 工具降级

> **定位**：当主方案（压缩 + 外置 + 调度）因模型不可用、向量库故障、预算估算偏差等原因失效时，作为最后一道防线，确保系统不崩、基础功能可用。

### 5.1 设计目标与触发条件

**设计目标**：

- 绝对防止 `context_length_exceeded` 错误外泄给用户
- 在 100ms 内完成截断决策
- 保留 System Prompt 与当前用户输入，确保 Agent 仍能响应
- 不依赖任何外部服务（向量库、小模型），具备"断网可用"能力

**触发条件**（满足任一即触发）：

| 编号 | 触发条件 | 检测方式 |
|------|----------|----------|
| T1 | 预算控制器判定 `should_truncate() == True`（usage ≥ 95%） | 本地计算 |
| T2 | LLM 返回 `context_length_exceeded` 错误 | API 错误码 |
| T3 | 摘要/外置服务连续失败 ≥ 3 次 | 熔断器状态 |
| T4 | 摘要/外置服务响应超时 > 2s | 超时检测 |
| T5 | 预算估算与实际 Token 偏差 > 15%（模型更换等） | 调用后校验 |

### 5.2 执行流程

```
┌────────────────────────────────────────────────────┐
│  兜底截断器（FallbackTruncator）触发                │
└───────────────────────┬────────────────────────────┘
                        ▼
┌────────────────────────────────────────────────────┐
│ Step 1：保留必留段（不可截断）                       │
│  - System Prompt                                    │
│  - 当前用户输入                                     │
│  - 用户关键约定（含关键词的消息）                    │
└───────────────────────┬────────────────────────────┘
                        ▼
┌────────────────────────────────────────────────────┐
│ Step 2：计算剩余预算                                │
│  remaining = MODEL_LIMIT - OUTPUT_RESERVED          │
│              - tokens(System) - tokens(UserInput)   │
│              - tokens(Rules) - SAFE_MARGIN          │
└───────────────────────┬────────────────────────────┘
                        ▼
┌────────────────────────────────────────────────────┐
│ Step 3：按优先级逆序填充历史                         │
│  - 优先填充最近 N 轮原文                            │
│  - 若仍有预算，填充历史摘要                          │
│  - 超出预算的 oldest-first 丢弃                     │
└───────────────────────┬────────────────────────────┘
                        ▼
┌────────────────────────────────────────────────────┐
│ Step 4：工具降级                                    │
│  - 关闭非必要工具调用（仅保留 search/retrieval）     │
│  - 工具返回强制压缩至 max 500 tokens                │
│  - 单轮工具调用次数上限降为 3                        │
└───────────────────────┬────────────────────────────┘
                        ▼
┌────────────────────────────────────────────────────┐
│ Step 5：注入降级提示                                │
│  在 System Prompt 末尾追加：                         │
│  "[FALLBACK_MODE] 上下文已被截断，请优先处理当前     │
│   请求，避免引用早期对话细节。"                      │
└───────────────────────┬────────────────────────────┘
                        ▼
┌────────────────────────────────────────────────────┐
│ Step 6：调用 LLM + 双重校验                         │
│  - 调用前再次估算 Token，确保 ≤ 上限                 │
│  - 若仍超限，对历史段做 50% 二次截断                 │
│  - 调用后若仍报错，降级到纯文本回复（不引用历史）     │
└───────────────────────┬────────────────────────────┘
                        ▼
┌────────────────────────────────────────────────────┐
│ Step 7：告警与记录                                  │
│  - 上报 P1 告警（兜底触发 = 主方案异常）             │
│  - 记录截断前 Token 数、截断段数、丢失信息摘要        │
└────────────────────────────────────────────────────┘
```

**核心实现**：

```python
class FallbackTruncator:
    def __init__(self, model_limit: int, output_reserved: int = 4096):
        self.model_limit = model_limit
        self.output_reserved = output_reserved
        self.safe_margin = 1024
        self.max_tool_result_tokens = 500
        self.max_tool_calls_per_turn = 3

    def truncate(self, messages: List[dict], rules_keywords: List[str]) -> List[dict]:
        """
        兜底截断：保证返回的 messages 一定不超限。
        """
        # Step 1: 分离必留段
        system_msgs = [m for m in messages if m["role"] == "system"]
        current_user = [m for m in messages if m["role"] == "user"][-1:]
        rule_msgs = [
            m for m in messages
            if any(kw in m.get("content", "") for kw in rules_keywords)
        ]

        # Step 2: 计算剩余预算
        must_keep = system_msgs + rule_msgs + current_user
        must_keep_tokens = self._count_tokens(must_keep)
        remaining = (
            self.model_limit - self.output_reserved
            - self.safe_margin - must_keep_tokens
        )

        if remaining <= 0:
            # 极端情况：连必留段都超限，仅保留 system + current user
            return system_msgs + current_user

        # Step 3: 逆序填充历史
        history = [
            m for m in messages
            if m not in must_keep and m["role"] != "system"
        ][:-1]  # 排除 current user
        history.reverse()  # 最近优先

        filled = []
        for m in history:
            t = self._count_tokens([m])
            if remaining - t >= 0:
                filled.append(m)
                remaining -= t
            else:
                break
        filled.reverse()

        return system_msgs + rule_msgs + filled + current_user

    def _count_tokens(self, messages: List[dict]) -> int:
        # 使用 tiktoken 或近似算法
        total = 0
        for m in messages:
            total += len(m.get("content", "")) // 3  # 近似
        return total + len(messages) * 4  # 角色标记开销
```

### 5.3 资源消耗

| 资源 | 消耗 | 说明 |
|------|------|------|
| CPU | < 5% | 仅本地 Token 计数与字符串操作 |
| 内存 | < 50MB | 临时存储消息副本 |
| 网络 | 0 | 不依赖任何外部服务 |
| 延迟开销 | < 100ms | 截断决策 + 字符串拼接 |
| LLM 调用 | 1 次 | 仅调用主模型，无摘要小模型依赖 |

**对比主方案**：

| 维度 | 主方案 | 兜底方案 |
|------|--------|----------|
| 功能完整性 | 高（保留摘要 + 回填） | 中（仅保留最近 + 必留） |
| 上下文连贯性 | 高 | 中低（可能丢失早期细节） |
| 外部依赖 | 向量库 + 小模型 | 无 |
| 响应延迟 | +2~5s（摘要 + 检索） | +<100ms |
| 成本 | 中（额外小模型调用） | 低 |

### 5.4 恢复机制

**自动恢复**：

1. **熔断器半开探测**：兜底触发后，每 60s 探测一次主方案依赖服务（向量库、小模型）。
2. **恢复条件**：连续 3 次探测成功 → 切回主方案。
3. **状态保留**：兜底期间被截断的消息仍写入持久化日志，恢复后异步补入向量库，不丢失。

**手动恢复**：

- 运维可通过配置中心开关 `fallback_mode=off` 强制切回主方案（需确认依赖已恢复）。
- 提供管理 API `POST /admin/context/recover`，触发一次全量上下文重建（从持久化日志重放）。

**数据补偿**：

- 兜底期间每条被截断的消息写入 `truncation_log` 表：`session_id, turn_id, original_tokens, truncated_tokens, omitted_summary`。
- 恢复后批量回放 `truncation_log`，对被截断段重新执行摘要与外置，补全向量库索引。

---

## 6. 评估指标与回滚策略

### 6.1 可量化评估指标

| 类别 | 指标 | 采集方式 | 目标值 |
|------|------|----------|--------|
| 稳定性 | 溢出错误率 | LLM API 错误码统计 | < 0.1% |
| 稳定性 | 兜底触发率 | FallbackTruncator 调用计数 | < 1% |
| 性能 | P95 响应时延 | APM 链路追踪 | < 5s |
| 性能 | 预算计量耗时 | 本地计时 | < 20ms |
| 成本 | 单会话 Token 消耗 | API 用量统计 | 较基线降 50%+ |
| 成本 | 摘要小模型调用成本 | API 账单 | < 主模型成本 10% |
| 质量 | 关键信息保留率 | 人工 + 自动评估 | ≥ 90% |
| 质量 | 50 轮长会话连贯性评分 | 人工 5 分制 | ≥ 4.0 |
| 可用性 | 向量库召回 P99 延迟 | 向量库监控 | < 200ms |
| 可用性 | 主方案可用率 | 熔断器状态统计 | ≥ 99.5% |

### 6.2 回滚策略

**分级回滚**：

| 级别 | 触发条件 | 动作 | 影响范围 |
|------|----------|------|----------|
| L1 软回滚 | 指标劣化但未故障 | 关闭 RAG 回填，仅保留压缩 + 滑动窗口 | 召回质量下降，功能可用 |
| L2 中回滚 | 主方案错误率 > 5% | 关闭压缩 + 外置，仅保留预算控制 + 兜底截断 | 长会话体验下降，短会话正常 |
| L3 硬回滚 | 系统不可用 | 回退到上线前版本（全量上下文 + 硬截断） | 溢出错误率回升，但系统可用 |
| L4 熔断 | 兜底也失败 | 降级为纯规则回复（模板应答） | 无 LLM 能力，保底可用 |

**回滚操作**：

- 所有策略通过配置中心（如 Nacos / Apollo）热切换，无需重启。
- 每次发布保留前两版本镜像，L3 硬回滚在 5 分钟内完成。
- 回滚后自动触发根因分析任务，输出事故报告。

**回滚验证 checklist**：

- [ ] 回滚后溢出错误率符合该级别预期
- [ ] 现有会话不中断（优雅降级）
- [ ] 监控大盘指标恢复正常
- [ ] 事故报告 24h 内产出

---

## 7. 风险与兼容性说明

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| Tokenizer 估算偏差（模型更换） | 中 | 截断过早或过晚 | 双重校验 + 10% 裕度 + 动态切换 Tokenizer |
| 摘要丢失关键信息 | 中 | Agent 决策偏差 | 关键消息不压缩 + 摘要后人工抽检 |
| 向量库故障 | 低 | RAG 回填失效 | 熔断 + 兜底截断自动接管 |
| 并发会话预算竞争 | 低 | 预算失准 | 按会话 ID 加锁 + Redis 原子操作 |
| 小模型摘要成本失控 | 中 | 成本超预期 | 摘要调用限流 + 缓存 + 成本告警 |
| 模型上下文上限变更 | 低 | 阈值失效 | 配置中心动态下发 `MODEL_LIMIT` |

**兼容性矩阵**：

| 模型/框架 | 兼容性 | 适配说明 |
|-----------|--------|----------|
| GPT-4o / GPT-4o-mini | ✅ 原生 | tiktoken 精确计数 |
| Claude 3.5 Sonnet | ✅ 适配 | 用 anthropic SDK 计数 |
| Gemini 1.5 Pro | ⚠️ 近似 | 无官方 Tokenizer，字符数 /3.5 + 10% 裕度 |
| 开源模型（Llama 3 / Qwen） | ✅ 适配 | 使用对应 tokenizer 库 |
| LangChain | ✅ 中间件 | 提供 `BaseMemory` 实现接入 |
| LlamaIndex | ✅ 钩子 | 提供 `CallbackManager` 钩子 |
| 自研框架 | ✅ SDK | 提供 Python/Java SDK |

---

## 8. 附录

### 8.1 关键参数推荐值汇总

| 参数 | 推荐值 | 调整建议 |
|------|--------|----------|
| `OUTPUT_RESERVED` | 4096 | 复杂任务调至 8192 |
| `SAFE_MARGIN` | 1024 | 估算不准时调至 2048 |
| `COMPRESS_THRESHOLD` | 80% | 高并发场景调至 70% |
| `TRUNCATE_THRESHOLD` | 95% | 固定不变（兜底最后防线） |
| `EXTERNALIZE_THRESHOLD` | 60% | 向量库性能差时调至 70% |
| `recent_n`（滑动窗口） | 4 | 简单任务调至 2，复杂任务调至 6 |
| `max_tool_result_tokens` | 500 | 数据分析场景调至 1000 |
| `max_tool_calls_per_turn` | 5（正常）/ 3（兜底） | 按 Agent 复杂度调整 |
| 向量召回 Top-K | 5 | 召回精度低时调至 8 |
| 回填 Token 上限 | 2000 | 预算紧张时调至 1000 |

### 8.2 监控告警阈值

| 告警 | 阈值 | 级别 |
|------|------|------|
| 溢出错误率 | > 0.5% | P1 |
| 兜底触发率 | > 5% | P1 |
| P95 时延 | > 8s | P2 |
| 向量库 P99 | > 500ms | P2 |
| 摘要小模型失败率 | > 5% | P2 |
| 单会话 Token 消耗 | > 基线 1.5 倍 | P3 |

### 8.3 术语表

| 术语 | 定义 |
|------|------|
| 上下文窗口 | 模型单次调用可处理的最大 Token 数 |
| Token 预算 | 为输入预留的 Token 上限 = 模型上限 - 输出预留 - 安全裕度 |
| 滚动摘要 | 将旧消息压缩为摘要段，定期滚动更新 |
| 外置记忆 | 将不常用上下文存入外部存储（向量库），按需召回 |
| 滑动窗口 | 仅保留最近 N 轮原文的策略 |
| 兜底截断 | 主方案失效时，强制裁剪上下文至安全范围的最后防线 |
| 熔断器 | 连续失败达阈值后自动切断对依赖服务的调用 |

---

> **文档版本**：v1.0  
> **适用范围**：AI Agent 系统上下文治理  
> **维护说明**：参数与阈值应随模型迭代与业务规模动态调整，建议每季度复核一次。
