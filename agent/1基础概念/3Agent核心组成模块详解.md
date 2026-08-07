# AI Agent 核心组成模块详解

> **文档说明**：本文档聚焦于 AI Agent 的**工程实现视角**，详细拆解构成 Agent 系统的核心模块、模块间的交互机制及协同工作流。与侧重概念与应用的《AI Agent 基础概念详解》不同，本文侧重于架构设计、设计模式与核心代码逻辑，旨在为开发者提供构建健壮、可扩展 Agent 系统的蓝图。

## 目录

- [一、核心模块全景图](#一核心模块全景图)
- [二、核心模块深度解析](#二核心模块深度解析)
  - [2.1 大脑：LLM 推理引擎](#21大脑llm-推理引擎)
  - [2.2 感知模块 (Perception)](#22感知模块-perception)
  - [2.3 规划模块 (Planner)](#23规划模块-planner)
  - [2.4 执行引擎 (Executor)](#24执行引擎-executor)
  - [2.5 记忆系统 (Memory)](#25记忆系统-memory)
  - [2.6 工具层 (Tools)](#26工具层-tools)
  - [2.7 安全与可观测性 (Safety & Observability)](#27安全与可观测性-safety--observability)
- [三、模块交互工作流](#三模块交互工作流)
- [四、核心设计模式](#四核心设计模式)
- [五、模块协同代码示例](#五模块协同代码示例)
- [六、构建生产级 Agent 的最佳实践](#六构建生产级-agent-的最佳实践)

---

## 一、核心模块全景图

一个健壮的 AI Agent 系统由以下 **七大核心模块** 构成。它们通过明确的接口协作，共同完成从“理解目标”到“交付结果”的闭环。

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI Agent 核心架构                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      用户交互层 (Interface)                     │   │
│  │         负责接收用户输入 (Input) 与展示最终输出 (Output)        │   │
│  └──────────────────────────┬──────────────────────────────────────┘   │
│                             │                                           │
│  ┌──────────────────────────▼──────────────────────────────────────┐   │
│  │                    ① 感知模块 (Perception)                      │   │
│  │  * 意图识别 (Intent Recognition)                              │   │
│  │  * 实体提取 (Entity Extraction)                               │   │
│  │  * 上下文构建 (Context Building)                              │   │
│  └──────────────────────────┬──────────────────────────────────────┘   │
│                             │                                           │
│  ┌──────────────────────────▼──────────────────────────────────────┐   │
│  │                     ② 记忆系统 (Memory)                         │   │
│  │  * 短期记忆 (Short-term): 当前会话状态、历史对话               │   │
│  │  * 长期记忆 (Long-term): 用户画像、知识库、历史经验            │   │
│  │  * 工作记忆 (Working): 中间计算结果、子任务状态                │   │
│  └──────────────────────────┬──────────────────────────────────────┘   │
│                             │                                           │
│  ┌──────────────────────────▼──────────────────────────────────────┐   │
│  │                  ③ 规划模块 (Planner / Reasoner)                │   │
│  │  * 任务分解 (Task Decomposition)                               │   │
│  │  * 策略选择 (Strategy Selection)                              │   │
│  │  * 路径规划 (Path Planning)                                   │   │
│  └──────────────────────────┬──────────────────────────────────────┘   │
│                             │                                           │
│  ┌──────────────────────────▼──────────────────────────────────────┐   │
│  │                  ④ 大脑：LLM 推理引擎 (Brain)                  │   │
│  │  * Prompt 模板管理                                            │   │
│  │  * 决策生成与解析 (Output Parsing)                            │   │
│  │  * 自我反思 (Self-Reflection)                                │   │
│  └──────────────────────────┬──────────────────────────────────────┘   │
│                             │                                           │
│  ┌──────────────────────────▼──────────────────────────────────────┐   │
│  │                   ⑤ 执行引擎 (Executor)                        │   │
│  │  * 工具路由 (Tool Routing)                                    │   │
│  │  * 动作执行 (Action Execution)                                │   │
│  │  * 错误处理与重试 (Error Handling & Retry)                    │   │
│  └──────────────────────────┬──────────────────────────────────────┘   │
│                             │                                           │
│  ┌──────────────────────────▼──────────────────────────────────────┐   │
│  │                     ⑥ 工具层 (Tools / Actuators)               │   │
│  │  * 外部 API 调用、文件操作、系统命令、代码解释器...             │   │
│  └──────────────────────────┬──────────────────────────────────────┘   │
│                             │                                           │
│  ┌──────────────────────────▼──────────────────────────────────────┐   │
│  │          ⑦ 安全与可观测性 (Safety & Observability)             │   │
│  │  * 权限控制、输入输出安全过滤、执行追踪、性能监控              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 模块核心职责速查表

| 模块 | 比喻 | 核心职责 | 关键输入 | 关键输出 |
|------|------|---------|---------|---------|
| **感知模块** | 五官 | 将用户输入转化为机器可理解的结构化数据 | 自然语言、图片 | `Intent`, `Entities` |
| **记忆系统** | 大脑皮层 | 存储、检索、管理 Agent 所需的全部信息 | `Query`, `Event` | `Context`, `Knowledge` |
| **规划模块** | 项目经理 | 将复杂目标分解为有序的执行步骤 | `Goal`, `Context` | `Plan`, `Subtasks` |
| **LLM 引擎** | 思考中枢 | 基于上下文生成决策、推理和行动指令 | `Prompt` (指令+记忆+规划) | `Action`, `Thought` |
| **执行引擎** | 四肢 | 调度工具执行具体动作并获取结果 | `Action`指令 | `Observation` (执行结果) |
| **工具层** | 工具箱 | 提供标准化的外部能力接口 | `Tool Call` | `Tool Result` |
| **安全模块** | 门卫 | 确保所有操作合法、安全、可追溯 | `Action`, `Input` | `Approval`, `Log` |

---

## 二、核心模块深度解析

### 2.1 大脑：LLM 推理引擎

#### 2.1.1 核心职责
作为 Agent 的**认知中枢**，负责理解、推理、生成和决策。它接收来自感知、记忆和规划模块的信息，融合后生成下一步的执行指令。

#### 2.1.2 关键子组件

| 子组件 | 功能说明 | 技术实现要点 |
|--------|---------|-------------|
| **Prompt 构建器 (Builder)** | 组装发送给 LLM 的完整提示词 | 组合 System Prompt + Context (Memory) + History + User Goal + Available Tools |
| **推理器 (Reasoner)** | 驱动 LLM 完成任务理解与决策 | 支持 `CoT` (Chain-of-Thought), `ToT` (Tree-of-Thought), `ReAct` 等多种推理范式 |
| **输出解析器 (Parser)** | 将 LLM 输出的非结构化文本解析为结构化指令 | 解析 `Thought`, `Action`, `Observation` 等标签或 JSON 格式的 Function Call |
| **反思器 (Reflector)** | 在任务受阻或完成后，评估自身表现并优化后续策略 | 对比目标与结果，生成 `Reflection` 记忆存入长期记忆 |

#### 2.1.3 Prompt 模板结构

一个健壮的 Agent Prompt 通常包含以下分层结构：

```text
# System Prompt (角色与核心指令)
你是一个专业的代码审查 Agent。你的任务是分析代码并提供改进建议。

# Constraints (约束条件)
- 必须遵循用户的代码风格
- 优先考虑性能

# Context from Memory (从记忆中检索的上下文)
- 用户偏好: "偏好函数式编程"
- 历史教训: "上次因未检查空指针报错"

# History (当前会话历史，包含之前的思考与行动)
## Thought 1: 我需要查看文件内容
## Action 1: read_file("main.py")
## Observation 1: [文件内容摘要]
## ...

# Current Goal (当前目标)
目标: "重构 main.py 中的 calculate 函数"

# Available Tools (可用工具列表及说明)
Tools:
- read_file: 读取文件
- edit_file: 编辑文件
- run_tests: 运行测试

# Response Format (响应格式约束)
请严格按照以下 JSON 格式响应：
{
  "thought": "你的思考过程...",
  "action": {
    "name": "工具名称",
    "params": {...}
  }
}
```

#### 2.1.4 输出解析机制

LLM 的输出可能不稳定，因此解析器需要具备容错能力。

```python
# 伪代码：Output Parser
class OutputParser:
    def parse(self, llm_output: str) -> AgentAction:
        try:
            # 1. 尝试按 JSON 解析
            return self._parse_json(llm_output)
        except json.JSONDecodeError:
            # 2. 尝试按 ReAct 格式解析 (Thought/Action/Observation)
            if "Action:" in llm_output:
                return self._parse_react(llm_output)
            # 3. 尝试通过正则提取
            action_match = re.search(r'Action:\s*(.+)', llm_output)
            if action_match:
                return self._extract_action(action_match.group(1))
            # 4. 兜底：将整个输出作为 Final Answer
            return FinalAnswer(content=llm_output)
```

---

### 2.2 感知模块 (Perception)

#### 2.2.1 核心职责
**“理解用户”** —— 将用户的原始输入（文本、语音、图像）转化为 Agent 内部可执行的结构化指令。

#### 2.2.2 处理流水线

感知模块通常通过一个 **Pipeline** 完成输入处理：

```
原始输入 ("帮我看看服务器 CPU 高不高")
    │
    ▼
[1. 输入适配器 (Input Adapter)]
    * 文本: 直接传递
    * 语音: ASR 转文本
    * 图像: VLM 描述
    │
    ▼
[2. 预处理 (Preprocessing)]
    * 格式化、清洗、去除无用字符
    * 语言检测 (LID)
    │
    ▼
[3. 意图识别 (Intent Recognition)]
    * 分类用户想做什么 (e.g., "monitor_system", "ask_weather")
    * 方法: LLM Zero-Shot / Few-Shot 分类, 或专用分类模型
    │
    ▼
[4. 实体提取 (Entity Extraction)]
    * 提取关键参数 (e.g., "服务器", "CPU", "高不高" => {"metric": "cpu"})
    * 方法: NER 模型, LLM 信息抽取
    │
    ▼
[5. 置信度评估 (Confidence)]
    * 评估解析结果的可信度
    * 若低于阈值，触发澄清对话 (Clarification)
    │
    ▼
结构化指令:
{
  "intent": "monitor_system",
  "entities": { "metric": "cpu" },
  "confidence": 0.95
}
```

#### 2.2.3 澄清机制 (Clarification)

当感知模块无法确切理解用户意图时，不应盲目执行，而应主动询问。

```python
# 伪代码：澄清机制
def process_input(user_input: str) -> AgentState:
    parsed = perception_module.parse(user_input)
    
    if parsed.confidence < 0.7:
        # 意图模糊，触发澄清
        return AgentState(
            status="clarification_needed",
            message=f"您是想查询服务器的 CPU 使用率，还是内存使用情况？",
            options=["CPU 使用率", "内存使用", "磁盘空间"]
        )
    else:
        # 解析成功，进入规划阶段
        planner.create_plan(parsed)
```

---

### 2.3 规划模块 (Planner)

#### 2.3.1 核心职责
**“分解任务”** —— 将一个复杂的、高层的用户目标，分解为一系列具体的、可执行的子任务（Subtasks），并决定执行顺序和策略。

#### 2.3.2 核心规划策略

规划模块并非单一算法，而是根据任务类型动态选择策略的策略集。

| 策略类型 | 适用场景 | 核心逻辑 | 示例 |
|---------|---------|---------|------|
| **单层规划 (Single-Shot)** | 简单任务 | 直接生成执行计划 | “翻译这句话” |
| **链式规划 (Chain)** | 有严格先后顺序的任务 | 生成线性步骤列表 | “注册账号→登录→下单” |
| **层级规划 (Hierarchical)** | 复杂、可分治的任务 | 生成“主计划”+“子计划” | “开发一个 App”→ [前端, 后端, 数据库] |
| **动态规划 (Dynamic/ReAct)** | 需要根据中间结果调整的任务 | `思考→行动→观察→再思考` 循环 | “调研市场并生成报告” |
| **图状规划 (Graph)** | 复杂依赖关系的任务 | 使用 DAG（有向无环图）管理任务依赖 | “数据管道处理” |

#### 2.3.3 计划结构 (Plan Structure)

一个标准的执行计划通常包含以下结构：

```json
{
  "goal": "优化项目构建速度",
  "plan_id": "plan_001",
  "current_step": 0,
  "strategy": "hierarchical",
  "steps": [
    {
      "id": 1,
      "description": "分析当前构建流程的耗时瓶颈",
      "status": "pending",
      "tool": "profile_build",
      "dependencies": [],
      "subtasks": null
    },
    {
      "id": 2,
      "description": "优化依赖加载速度",
      "status": "pending",
      "tool": "optimize_deps",
      "dependencies": [1],
      "subtasks": [
        {"id": 2.1, "description": "分析 package.json"},
        {"id": 2.2, "description": "实施依赖缓存"}
      ]
    },
    {
      "id": 3,
      "description": "验证构建速度是否提升",
      "status": "pending",
      "tool": "run_benchmark",
      "dependencies": [2]
    }
  ]
}
```

#### 2.3.4 Plan-and-Execute 流程

```
[感知模块] 传入结构化目标 ("重构代码以提升性能")
    │
    ▼
[规划模块 - Phase 1: 生成计划]
    Planner: 
      1. 分析当前代码结构
      2. 识别性能瓶颈
      3. 制定优化方案
      4. 执行优化
      5. 验证效果
    │
    ▼
[执行引擎 - Phase 2: 逐步执行]
    Step 1: 执行 "分析代码" → 获取代码结构
    Step 2: 执行 "识别瓶颈" → 发现 N+1 查询问题
    Step 3: 生成方案
    Step 4: 执行 "优化代码" → 修改为批量查询
    Step 5: 执行 "验证" → 性能提升 50%
    │
    ▼
[规划模块 - Phase 3: 计划评估]
    检查: 是否所有步骤完成？
    评估: 是否达成目标？ (性能提升 50% > 目标 30%)
    决策: 任务成功，结束。
```

---

### 2.4 执行引擎 (Executor)

#### 2.4.1 核心职责
**“调度与执行”** —— 负责接收规划模块生成的 Action 指令，路由到对应的工具层 (Tools) 执行，并处理执行过程中的异常和结果收集。

#### 2.4.2 核心子系统

| 子系统 | 功能说明 | 关键机制 |
|--------|---------|---------|
| **路由分发器 (Dispatcher)** | 接收 Action 指令，找到对应的 Tool 并调用 | 基于 Action 名称的路由表 (`Tool Registry`) |
| **执行器 (Runner)** | 真正调用工具，管理执行上下文 | 支持同步/异步执行、超时控制 |
| **错误处理器 (Error Handler)** | 捕获工具执行错误，决定重试、降级或上报 | 重试策略 (指数退避)、错误分类 |
| **结果收集器 (Collector)** | 收集工具执行的 Observation（观察结果） | 格式化、摘要、传递回 LLM |

#### 2.4.3 执行流程时序图

```
[LLM] 请求执行 Action: { "name": "search", "params": {"query": "AI"} }
    │
    ▼
[Executor] 
    │
    ├── 1. Dispatcher: 查找 "search" 对应的工具
    │       → 找到 WebSearchTool 实例
    │
    ├── 2. Runner: 执行 tool.execute({"query": "AI"})
    │       ├── [Start Timer]
    │       ├── [Call API: search_api("AI")]
    │       └── [End Timer]
    │
    ├── 3. Error Handler: 检查执行状态
    │       ├── 状态: Success (200ms)
    │       └── (若失败) 决定是否重试 (Retries Left: 3)
    │
    └── 4. Collector: 收集结果
            → 格式化 Observation: 
            {
              "status": "success",
              "data": [{"title": "AI News", "url": "..."}],
              "metadata": {"latency_ms": 200, "tool": "search"}
            }
    │
    ▼
[LLM] 接收 Observation，更新上下文，进入下一轮思考
```

#### 2.4.4 错误处理与重试策略

```python
# 伪代码：执行引擎错误处理
async def execute_action(self, action: AgentAction) -> Observation:
    try:
        # 1. 路由到具体工具
        tool = self.dispatcher.resolve(action.name)
        
        # 2. 带超时的异步执行
        result = await asyncio.wait_for(
            tool.execute(action.params),
            timeout=self.get_timeout(action)
        )
        
        # 3. 返回成功的观察结果
        return Observation(status="success", data=result)
        
    except ToolExecutionError as e:
        # 4. 分类错误
        error_type = self.classify_error(e)
        
        if error_type == "transient" and self.retry_count < self.max_retries:
            # 瞬时错误（如网络波动），指数退避重试
            self.retry_count += 1
            await asyncio.sleep(2 ** self.retry_count)
            return await self.execute_action(action)  # 递归重试
            
        elif error_type == "permanent":
            # 永久错误（如参数错误），直接上报
            return Observation(
                status="error", 
                data=str(e),
                error_message=f"执行失败: {e.message}, 请检查参数"
            )
            
    except asyncio.TimeoutError:
        # 超时错误
        return Observation(status="timeout", data="执行超时")
```

---

### 2.5 记忆系统 (Memory)

#### 2.5.1 核心职责
**“存储与检索”** —— 为 Agent 提供完整的历史信息支持，使其具备“记住过去”、“利用经验”、“积累知识”的能力。

#### 2.5.2 分层记忆架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Agent 记忆分层架构                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  1. 工作记忆 (Working Memory) 【易失，生命周期: < 1小时】        │   │
│  │  ----------------------------------------------------------------  │
│  │  * 存储: 当前任务的中间计算结果、子任务状态、临时变量           │   │
│  │  * 载体: 内存 (Runtime State), LLM Context Window               │   │
│  │  * 示例: 代码重构过程中识别出的“待替换函数列表”                 │   │
│  └──────────────────────────┬──────────────────────────────────────┘   │
│                             │ 结束时归档                               │
│  ┌──────────────────────────▼──────────────────────────────────────┐   │
│  │  2. 短期/会话记忆 (Short-term/Session Memory) 【易失，生命周期: 会话】│   │
│  │  ----------------------------------------------------------------  │
│  │  * 存储: 当前会话的完整对话历史、上下文信息                     │   │
│  │  * 载体: 数据库 (SQLite), Redis                                  │   │
│  │  * 示例: 用户在本次会话中提到的“偏好使用 TypeScript”             │   │
│  └──────────────────────────┬──────────────────────────────────────┘   │
│                             │ 结束时提炼                               │
│  ┌──────────────────────────▼──────────────────────────────────────┐   │
│  │  3. 长期记忆 (Long-term Memory) 【持久，生命周期: 永久】          │   │
│  │  ----------------------------------------------------------------  │
│  │  * 存储: 用户画像、核心知识库、历史成功/失败经验、规则库        │   │
│  │  * 载体: 向量数据库 (Milvus, FAISS), 关系型数据库 (PostgreSQL)   │   │
│  │  * 示例: "用户偏好函数式编程", "上次修复 N+1 查询的最佳方案"    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 2.5.3 关键记忆模式

| 模式 | 技术实现 | 适用场景 | 优缺点 |
|------|---------|---------|--------|
| **滚动摘要 (Summary)** | 定期压缩历史对话，保留摘要 | 长对话上下文管理 | 优: 节省Token<br>缺: 丢失细节 |
| **向量检索 (Vector RAG)** | 将知识嵌入向量，按相似度检索 | 大规模知识库问答 | 优: 语义匹配<br>缺: 计算开销 |
| **图结构记忆 (Graph Memory)** | 以知识图谱形式存储实体关系 | 复杂关联推理 | 优: 关系清晰<br>缺: 构建复杂 |
| **事件溯源 (Event Sourcing)** | 只追加日志，保留完整历史 | 审计、回放、分析 | 优: 可追溯<br>缺: 查询慢 |

#### 2.5.4 记忆读写流程

```
写入流程 (Write)：
    [事件发生] → [数据序列化] → [Embedding 向量化] → [存入向量DB + 存入关系库]

读取流程 (Read)：
    [查询请求] 
        → [1. 检查工作记忆 (最快)]
            ↓ (未命中)
        → [2. 检查短期会话记忆]
            ↓ (未命中)
        → [3. 向量化查询长期记忆 (Vector Search)]
            ↓
        → [返回 Top-K 相关记忆片段]
            ↓
        → [注入到 LLM 的 Context Window 中]
```

---

### 2.6 工具层 (Tools)

#### 2.6.1 核心职责
**“能力扩展”** —— 作为 Agent 与外部世界（系统、应用、服务）交互的标准化接口。每一个 Tool 都是一个原子能力单元。

#### 2.6.2 Tool 的标准接口定义

为了实现可插拔和统一管理，所有工具必须遵循相同的接口规范：

```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    """工具基类定义"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """工具的唯一标识符，供 LLM 调用"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """功能描述，告诉 LLM 该工具的用途"""
        pass
    
    @property
    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """参数的 JSON Schema 定义，约束 LLM 生成的参数格式"""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        工具的核心执行逻辑。
        kwargs 参数由 LLM 根据 parameters_schema 生成。
        """
        pass

# =================================================================
# 示例：定义一个“搜索天气”的工具
# =================================================================
class WeatherTool(BaseTool):
    @property
    def name(self) -> str:
        return "get_weather"

    @property
    def description(self) -> str:
        return "获取指定城市的实时天气信息，包括温度、湿度和天气状况"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，如 '北京'、'上海'"
                }
            },
            "required": ["city"]
        }

    async def execute(self, city: str) -> str:
        # 实际场景下，这里会调用天气 API
        # 此处为伪代码
        response = await weather_api_client.fetch(city)
        return f"{city}现在的天气是 {response.condition}，温度 {response.temperature}°C"
```

#### 2.6.3 工具注册与发现 (Tool Registry)

Agent 启动时，需要知道自己“拥有哪些超能力”。这通过工具注册表实现。

```python
class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        """注册工具"""
        self._tools[tool.name] = tool

    def get_all_for_llm(self) -> str:
        """
        获取所有已注册工具的描述，用于构建 LLM Prompt。
        这是 LLM “知道”自己能做什么的途径。
        """
        tools_description = []
        for name, tool in self._tools.items():
            tools_description.append({
                "name": name,
                "description": tool.description,
                "parameters": tool.parameters_schema
            })
        return json.dumps({"tools": tools_description})

    async def execute(self, tool_name: str, **params) -> Any:
        """执行指定工具"""
        if tool_name not in self._tools:
            raise ValueError(f"工具 {tool_name} 不存在！")
        
        return await self._tools[tool_name].execute(**params)
```

---

### 2.7 安全与可观测性 (Safety & Observability)

#### 2.7.1 核心职责
**“保驾护航”** —— 确保 Agent 的行为始终处于可控、可追溯、可审计的状态，防止幻觉、滥用和安全事故。

#### 2.7.2 安全防线 (Safety Guardrails)

| 防线层级 | 具体措施 | 实现位置 |
|---------|---------|---------|
| **1. 输入过滤** | 检测 Prompt Injection 攻击、敏感词过滤 | 感知模块之前 |
| **2. 权限校验** | 检查 Agent 是否拥有执行该 Action 的权限 | 执行引擎之前 |
| **3. 参数校验** | 对 LLM 生成的参数进行严格的 Schema 验证 | 执行引擎内部 |
| **4. 沙箱执行** | 在隔离的环境（Docker, Firecracker）中执行代码或系统命令 | 工具层内部 |
| **5. 人在回路 (HITL)** | 对高风险操作（删除、支付）强制人工确认 | 执行引擎之前 |
| **6. 输出审查** | 检查最终输出是否包含敏感信息或不当内容 | 用户交互层之前 |

#### 2.7.3 可观测性设计 (Observability)

为了更好地调试和优化 Agent，必须记录其完整的思考和行为轨迹。

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Agent 执行追踪 (Trace)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Trace ID: trace_abc123                                                 │
│  Start Time: 2026-08-08T10:00:00Z                                      │
│  User Goal: "分析项目代码并生成报告"                                    │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Step 1: LLM Call (Reasoning)                                  │   │
│  │  ----------------------------------------------------------------                              │   │
│  │  Prompt: [System] + [History] + [Goal: 分析项目...] + [Tools...]│   │
│  │  Response: Action({name: "list_dir", params: {path: "./"}})    │   │
│  │  Latency: 1.2s                                                  │   │
│  │  Tokens: 1500 (Input) / 200 (Output)                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Step 2: Tool Execution                                         │   │
│  │  ----------------------------------------------------------------                              │   │
│  │  Tool: list_dir                                                  │   │
│  │  Params: {"path": "./"}                                          │   │
│  │  Result: ["src", "public", "package.json"]                       │   │
│  │  Status: Success                                                 │   │
│  │  Latency: 0.05s                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Step 3: LLM Call (Reasoning)                                   │   │
│  │  ----------------------------------------------------------------                              │   │
│  │  Prompt: [System] + [History] + [Observation: ["src"...]]       │   │
│  │  Response: Action({name: "read_file", params: {file: "package.json"}})│
│  │  Latency: 1.1s                                                   │   │
│  │  Tokens: 1600 (Input) / 150 (Output)                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ▼                                          │
│                             ... (循环)                                  │
│                                                                         │
│  End Time: 2026-08-08T10:00:05Z                                        │
│  Total Time: 5.5s                                                      │
│  Total LLM Calls: 3                                                    │
│  Total Tool Calls: 2                                                   │
│  Outcome: Success                                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**关键实现工具**：
*   **LangSmith / LangFuse**: 专为 LLM 应用设计的追踪、评估和调试平台。
*   **OpenTelemetry**: 通用的可观测性标准，可将 Agent Trace 集成到现有监控体系（如 Jaeger, Zipkin）。

---

## 三、模块交互工作流

以一个完整的任务为例，展示各模块如何协同工作。

**用户请求**: “帮我查一下北京明天的天气，如果下雨就提醒我带伞。”

```
时间轴  模块          行为与数据
─────────────────────────────────────────────────────────────────────────
T0     [用户]      → 输入: "帮我查一下北京明天的天气，如果下雨就提醒我带伞。"
─────────────────────────────────────────────────────────────────────────
T1     [感知模块]  ← 解析输入
                  → 输出: 
                    {
                      "intent": "weather_query_and_alert",
                      "entities": {"city": "北京", "condition": "rain", "action": "remind"},
                      "confidence": 0.98
                    }
─────────────────────────────────────────────────────────────────────────
T2     [记忆系统]  → 检索长期记忆
                  → 输出: 
                    {
                      "user_profile": {"location": "北京", "communication_style": "简洁"},
                      "historical_preferences": ["喜欢直接的提醒"]
                    }
─────────────────────────────────────────────────────────────────────────
T3     [规划模块]  → 结合意图和记忆，生成计划
                  → 输出: 
                    {
                      "strategy": "sequential",
                      "steps": [
                        {"id": 1, "action": "get_weather", "params": {"city": "北京", "date": "tomorrow"}},
                        {"id": 2, "action": "evaluate_condition", "params": {"condition": "rain", "threshold": 0.5}},
                        {"id": 3, "action": "send_notification", "params": {"message": "明天北京有雨，记得带伞！"}}
                      ]
                    }
─────────────────────────────────────────────────────────────────────────
T4     [执行引擎]  ← 接收步骤 1
                  → 路由到 [工具层: get_weather]
                  → 执行工具...
─────────────────────────────────────────────────────────────────────────
T5     [工具层]    → 调用天气 API
                  → 输出 (Observation): 
                    {
                      "status": "success",
                      "data": {"city": "北京", "date": "2026-08-09", "condition": "小雨", "probability": 0.85}
                    }
─────────────────────────────────────────────────────────────────────────
T6     [执行引擎]  ← 接收结果
                  → 更新 [LLM] 的上下文
                  → 推进到步骤 2: 条件判断 (这一步通常由 LLM 直接推理完成)
─────────────────────────────────────────────────────────────────────────
T7     [LLM 引擎]  ← 接收 Observation
                  → 推理: "降雨概率 85% > 阈值 50%，条件满足"
                  → 请求执行步骤 3: send_notification
─────────────────────────────────────────────────────────────────────────
T8     [安全模块]  ← 检查权限
                  → 输出: (Approved)
─────────────────────────────────────────────────────────────────────────
T9     [执行引擎]  → 执行通知...
        [工具层]    → 调用短信/推送 API
                  → 输出: "通知发送成功"
─────────────────────────────────────────────────────────────────────────
T10    [记忆系统]  → 存储本次交互日志到短期记忆
                  → 提炼经验："用户对降雨很敏感，阈值设为 50%" → 存入长期记忆
─────────────────────────────────────────────────────────────────────────
T11    [用户]      ← 收到短信: "明天北京有雨，记得带伞！"
                  ← 界面反馈: 任务完成
```

---

## 四、核心设计模式

为了构建可扩展、可维护的 Agent 系统，推荐使用以下设计模式：

### 4.1 中介者模式 (Mediator Pattern)
*   **应用**：Agent Controller 作为中枢，协调 LLM、Tools、Memory 之间的所有通信，避免模块间的直接依赖。
*   **优点**：解耦模块，易于替换。

### 4.2 策略模式 (Strategy Pattern)
*   **应用**：规划模块内部的不同算法（Chain, ReAct, Plan-and-Execute）被封装为独立的策略类，Agent 可根据任务类型动态选择。
*   **优点**：符合开闭原则，易于新增规划算法。

### 4.3 责任链模式 (Chain of Responsibility)
*   **应用**：安全过滤、日志记录、参数校验等横切关注点，可通过中间件（Middleware）形式串联。
*   **优点**：灵活组合切面逻辑。

### 4.4 观察者模式 (Observer Pattern)
*   **应用**：执行事件（Step Started, Step Completed, Error Occurred）作为事件，被监控、日志、UI 等多个观察者订阅。
*   **优点**：实现松耦合的事件驱动架构。

---

## 五、模块协同代码示例

以下伪代码展示了一个简化 Agent 如何将上述模块串联起来。

```python
class SimpleAgent:
    def __init__(self, llm_client, perception, planner, executor, memory, safety):
        self.llm = llm_client
        self.perception = perception
        self.planner = planner
        self.executor = executor
        self.memory = memory
        self.safety = safety

    async def run(self, user_input: str):
        # 1. 感知: 解析用户意图
        parsed_intent = self.perception.parse(user_input)

        # 2. 记忆: 检索上下文
        context = self.memory.retrieve(parsed_intent.entities)

        # 3. 规划: 生成执行计划
        plan = self.planner.create_plan(parsed_intent, context)

        # 4. 执行循环 (ReAct 模式)
        while not plan.is_complete():
            # 4.1 LLM 思考: 生成下一步 Action
            llm_prompt = self._build_prompt(parsed_intent, context, plan)
            action = await self.llm.generate_action(llm_prompt)

            # 4.2 安全检查
            if not self.safety.check(action):
                # 中断或修改动作
                action = self.safety.sanitize(action)

            # 4.3 执行
            observation = await self.executor.execute(action)

            # 4.4 更新状态
            plan.update_progress(action, observation)
            self.memory.add_to_working_memory(action, observation)

        # 5. 记忆: 归档会话
        self.memory.archive_session()

        # 6. 交付结果
        return plan.get_final_answer()

    def _build_prompt(self, intent, context, plan):
        # 组装 Prompt: System + Context + History + Goal + Tools
        return f"""
        [System] 你是一个智能助手...
        [Context] {context}
        [History] {plan.history}
        [Goal] {intent.goal}
        [Available Tools] {self.executor.get_tools_description()}
        ...
        """
```

---

## 六、构建生产级 Agent 的最佳实践

1.  **模块化设计**：确保感知、规划、执行、记忆、工具、安全各模块边界清晰，通过接口交互，便于独立测试和替换。
2.  **状态持久化**：使用数据库（如 Redis, PostgreSQL）持久化 Agent 的完整状态（包括规划中的 Plan、执行历史），支持任务中断后续跑。
3.  **异常处理**：在每个环节（LLM 调用、工具执行）都要有健壮的异常捕获和重试机制，避免单点故障导致整个 Agent 崩溃。
4.  **成本控制**：监控 Token 消耗、LLM 调用延迟，通过缓存、摘要、模型分级（小模型处理简单任务）控制成本。
5.  **灰度发布**：新功能或新 Prompt 策略上线时，采用灰度发布（A/B Testing），对比效果和成本。
6.  **完善的日志与追踪**：如章节 2.7 所述，必须有完整的执行链路追踪，这是排查线上问题和优化 Agent 行为的基础。
