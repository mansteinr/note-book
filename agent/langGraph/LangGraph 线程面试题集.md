# LangGraph 线程面试题集

> 面试目标：系统化评估候选人对 LangGraph 线程（Thread）模型的核心概念、实现原理、使用场景、并发控制与问题排查能力的掌握程度。
> 本文档共 **15 道题**，覆盖选择题、简答题、编程题、案例分析题四种类型，难度涵盖基础、中级、高级三个层次。

---

## 目录

- [一、选择题（4题）](#一选择题4题)
- [二、简答题（4题）](#二简答题4题)
- [三、编程题（4题）](#三编程题4题)
- [四、案例分析题（3题）](#四案例分析题3题)
- [五、评分总览](#五评分总览)

---

## 一、选择题（4题）

### Q1：关于 LangGraph 中 Thread（线程）的概念，下列说法正确的是？

**难度**：基础　**考察点**：核心概念理解

**问题描述**：
请从以下选项中选出关于 LangGraph Thread 描述正确的说法。

- A. Thread 是操作系统的物理线程，每个节点运行在独立 OS 线程上
- B. Thread 是一次完整的图执行会话，通过 `thread_id` 标识，是状态隔离的基本单位
- C. Thread 必须在编译图时通过 `builder.compile(thread_id=...)` 指定
- D. 一个 `thread_id` 只能被 `invoke` 调用一次，重复调用会抛异常

**参考答案**：**B**

**解析**：

| 选项 | 正误 | 说明 |
|------|------|------|
| A | ✗ | LangGraph 的 Thread 是**逻辑会话**概念，与 OS 线程无关 |
| B | ✓ | Thread 代表一次完整的图执行会话，由 `thread_id` 标识，是 Checkpoint 与 State 隔离的核心维度 |
| C | ✗ | `thread_id` 在运行时通过 `config` 传入，不在编译期指定 |
| D | ✗ | 同一 `thread_id` 可多次调用 `invoke`，这是实现**多轮对话记忆**的关键 |

```python
# 同一 thread_id 可多次调用，自动加载历史 State
config = {"configurable": {"thread_id": "user_001_session_A"}}
graph.invoke({"messages": [("user", "你好")]}, config)
graph.invoke({"messages": [("user", "再问一个问题")]}, config)  # 自动继承上下文
```

**评分标准**：选对得 5 分，选错 0 分。

---

### Q2：下列关于 `thread_id` 与 `checkpoint_id` 的区别，说法错误的是？

**难度**：基础　**考察点**：核心标识辨析

**问题描述**：
请选出说法**错误**的选项。

- A. `thread_id` 是会话级标识，粒度最粗；`checkpoint_id` 是快照级标识，粒度最细
- B. 同一 `thread_id` 下可以有多个 `checkpoint_id`，形成一条时间线
- C. 在 `config["configurable"]` 中必须同时提供 `thread_id` 和 `checkpoint_id` 才能执行图
- D. `checkpoint_id` 主要用于精确回溯到某个历史状态，而 `thread_id` 用于会话隔离

**参考答案**：**C**

**解析**：

- **A、B、D 均正确**：三者关系为 `thread_id`（会话）→ 多个 `checkpoint_id`（快照）。
- **C 错误**：执行图时只需提供 `thread_id`，系统会自动加载该 thread 下最新的 `checkpoint_id`。`checkpoint_id` 仅在"时间旅行"回溯到指定历史快照时才需要显式传入。

```python
# 常规调用：只需 thread_id
config = {"configurable": {"thread_id": "sess-1"}}
graph.invoke(input, config)

# 时间旅行：指定 checkpoint_id 回溯
history = list(graph.get_state_history(config))
old_config = history[2].config  # 包含 checkpoint_id
graph.invoke(None, old_config)  # 从历史快照续跑
```

**评分标准**：选对得 5 分，选错 0 分。

---

### Q3：在多用户客服系统中，关于 `thread_id` 的设计策略，最佳实践是？

**难度**：中级　**考察点**：工程实践与隔离设计

**问题描述**：
某客服系统同时服务 1000+ 用户，每个用户可能有多轮对话。下列 `thread_id` 设计方案中，**最佳**的是：

- A. 全局共享一个 `thread_id`，如 `"customer_service"`，所有用户共用一份状态
- B. 每个用户一个 `thread_id`，如 `f"user_{user_id}"`，跨会话共享所有上下文
- C. 每个用户每次会话一个 `thread_id`，如 `f"user_{user_id}_session_{session_id}"`，会话间隔离
- D. 每次调用动态生成随机 `thread_id`，如 `str(uuid.uuid4())`

**参考答案**：**C**

**解析**：

| 方案 | 问题 |
|------|------|
| A | 所有用户状态混在一起，数据串号，严重事故 |
| B | 用户跨会话上下文无法隔离，旧会话污染新会话 |
| C | **最佳**：用户级 + 会话级双层隔离，符合业务语义 |
| D | 每次调用都是新会话，丢失多轮记忆能力 |

```python
# 最佳实践：用户ID + 会话ID 组合
def get_thread_id(user_id: str, session_id: str) -> str:
    return f"user_{user_id}_session_{session_id}"

config = {"configurable": {"thread_id": get_thread_id("u_123", "s_456")}}
```

**补充说明**：若需要跨会话共享用户画像等长期记忆，应配合 **Store**（而非复用 `thread_id`）实现跨 thread 持久化。

**评分标准**：选对得 5 分，选错 0 分。

---

### Q4：关于 LangGraph 的并发与异步执行，下列说法正确的是？

**难度**：高级　**考察点**：并发模型理解

**问题描述**：
请从以下选项中选出**正确**的说法。

- A. 同一 `thread_id` 可以被多个协程同时 `ainvoke` 调用，State 通过 Reducer 自动保证一致性
- B. `Send` API 用于实现 fan-out 并行，多个分支节点在同一超级步内并发执行，通过 Reducer 合并 State 更新
- C. 异步执行 `ainvoke` 与同步 `invoke` 可以混用于同一 `thread_id`，无需额外处理
- D. `MemorySaver` 支持跨进程并发安全，适合多 worker 共享状态

**参考答案**：**B**

**解析**：

| 选项 | 正误 | 说明 |
|------|------|------|
| A | ✗ | 同一 `thread_id` 并发调用会产生**写冲突**，需通过队列串行化或使用 `PostgresSaver` 配合行锁 |
| B | ✓ | `Send` API 是 LangGraph 实现 fan-out 并行的标准方式，同一超级步内多个节点并发执行，Reducer 负责合并 |
| C | ✗ | 混用易引发状态不一致，建议统一使用同步或异步接口 |
| D | ✗ | `MemorySaver` 仅单进程内有效，跨进程需用 `PostgresSaver` / `RedisSaver` |

```python
# Send API 实现 fan-out 并行
from langgraph.types import Send

def route(state):
    return [Send("worker", {"task": t}) for t in state["tasks"]]

builder.add_conditional_edges("splitter", route)
# 多个 worker 节点并发执行，通过 Reducer 合并结果
```

**评分标准**：选对得 5 分，选错 0 分。

---

## 二、简答题（4题）

### Q5：请阐述 LangGraph 中 Thread（线程）的定义、作用与生命周期。

**难度**：基础　**考察点**：概念理解

**问题描述**：
请说明 LangGraph 中 Thread 的定义、它在图执行中的作用，以及一个 Thread 从创建到结束的完整生命周期。

**参考答案**：

**定义**：
Thread 是 LangGraph 中的一次完整的图执行会话，通过 `thread_id` 唯一标识，是 **State 隔离**与 **Checkpoint 组织**的基本单位。

**作用**：
1. **状态隔离**：不同 `thread_id` 的 State 互不干扰，实现多用户/多会话隔离。
2. **记忆载体**：同一 `thread_id` 的多次调用自动加载历史 State，实现多轮对话记忆。
3. **Checkpoint 组织**：同一 Thread 下的多个 Checkpoint 按时间顺序形成时间线，支持回溯。
4. **HITL 钩子**：人工中断/恢复以 `thread_id` 为锚点，跨进程重启可续跑。

**生命周期**：

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart LR
    A([Thread 创建<br/>首次 invoke 指定 thread_id]) --> B[执行阶段<br/>节点循环 + Checkpoint 落盘]
    B --> C{结束?}
    C -->|否| D[多轮调用<br/>同 thread_id 自动加载历史]
    D --> B
    C -->|是| E[Thread 终止<br/>可选 delete_thread 清理]
    E -.->|历史保留| F([可回溯时间线])
```

**生命周期阶段**：
1. **创建**：首次以某 `thread_id` 调用 `invoke` / `stream` 时自动创建。
2. **执行**：每个超级步完成后落盘一个 Checkpoint，形成时间线。
3. **多轮续跑**：同 `thread_id` 再次调用，自动加载最新 Checkpoint。
4. **中断与恢复**：`interrupt` 暂停后，可通过 `Command(resume=...)` 在同 thread 上续跑。
5. **终止与清理**：业务结束后可调用 `delete_thread` 删除该 thread 的所有 Checkpoint。

**评分标准**：定义 1 分 / 作用 2 分 / 生命周期阶段 2 分（满分 5）。

---

### Q6：请说明 `thread_id`、`checkpoint_ns`、`checkpoint_id` 三个标识的作用与区别，并举例说明何时需要同时使用。

**难度**：中级　**考察点**：核心标识体系

**问题描述**：
LangGraph 持久化体系中有三个关键标识：`thread_id`、`checkpoint_ns`、`checkpoint_id`。请对比三者的作用、粒度与典型场景，并给出需要同时使用三者的代码示例。

**参考答案**：

| 标识 | 作用 | 粒度 | 典型场景 |
|------|------|------|----------|
| `thread_id` | 会话唯一标识 | 最粗（会话级） | 多用户/多会话隔离，**最常用** |
| `checkpoint_ns` | 命名空间 | 中等（子图级） | 子图、多分支的状态隔离，默认空字符串即可 |
| `checkpoint_id` | 检查点唯一 ID | 最细（快照级） | 精确回溯到某个历史版本 |

**三者的层级关系**：

```
thread_id (会话)
└── checkpoint_ns (子图命名空间)
    └── checkpoint_id (具体快照)
```

**同时使用三者的场景**：在含子图的复杂图中，需要回溯到某个子图的特定历史快照。

```python
# 主图包含一个子图 sub_agent，需回溯到子图的某个历史快照
config = {
    "configurable": {
        "thread_id": "user_001_session_A",       # 会话级：定位用户会话
        "checkpoint_ns": "sub_agent",             # 子图级：定位子图命名空间
        "checkpoint_id": "01J5X8Z...H9K3"         # 快照级：定位具体历史检查点
    }
}
state = graph.get_state(config)  # 读取该子图的指定历史快照
graph.invoke(None, config)       # 从该快照续跑子图
```

**典型用法**：
- **常规多轮对话**：只需 `thread_id`。
- **子图状态管理**：`thread_id` + `checkpoint_ns`。
- **时间旅行回溯**：`thread_id` + `checkpoint_id`（通过 `get_state_history` 获取）。
- **子图历史回溯**：三者同时使用。

**评分标准**：三者作用各 1 分 / 层级关系 1 分 / 代码示例 1 分（满分 5）。

---

### Q7：LangGraph 如何实现并发执行？请说明 Send API 的 fan-out 机制与 Reducer 的协同工作原理。

**难度**：高级　**考察点**：并发模型与原理

**问题描述**：
请描述 LangGraph 中并发执行的实现方式，重点说明 `Send` API 如何实现 fan-out 并行，以及 Reducer 如何保证多个并发分支的 State 合并正确性。

**参考答案**：

**并发执行的两层机制**：

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    subgraph 超级步["超级步 N"]
        direction TB
        Split[路由节点] --> S1[Send worker task1]
        Split --> S2[Send worker task2]
        Split --> S3[Send worker task3]
        S1 --> W1[Worker 1]
        S2 --> W2[Worker 2]
        S3 --> W3[Worker 3]
    end
    W1 --> Merge[Reducer 合并]
    W2 --> Merge
    W3 --> Merge
    Merge --> Next([超级步 N+1])
```

**1. Send API 实现 fan-out 并行**：
- 路由函数返回 `list[Send]` 而非单一节点名，触发多个分支节点并发执行。
- 每个 `Send` 携带独立的 State 副本，避免分支间互相污染。
- 所有分支在同一**超级步**内执行，超级步结束后统一进入下一个节点。

```python
from langgraph.types import Send

def split_tasks(state):
    # 为每个任务创建一个 Send，并发分发到 worker 节点
    return [Send("worker", {"task": t, "idx": i}) 
            for i, t in enumerate(state["tasks"])]

builder.add_conditional_edges("splitter", split_tasks)
builder.add_edge("worker", "aggregator")  # 所有 worker 完成后聚合
```

**2. Reducer 保证并发合并正确性**：
- 多个分支同时更新同一字段时，LangGraph 通过 Reducer 函数**确定性合并**，而非简单覆盖。
- 内置 Reducer：`add_messages`（消息追加）、`operator.add`（列表拼接）、`dict_merge`（字典合并）。
- 自定义 Reducer 需满足**结合律**与**交换律**，保证合并顺序无关。

```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import add_messages
import operator

class State(TypedDict):
    messages: Annotated[list, add_messages]   # 并发追加消息
    results: Annotated[list, operator.add]     # 并发拼接结果列表
    total: Annotated[int, operator.add]        # 并发累加计数

def worker(state):
    return {"results": [f"result_{state['idx']}"], "total": 1}
```

**3. 协同工作原理**：
1. 超级步开始，路由节点产生 N 个 `Send`。
2. N 个 worker 节点并发执行，各自返回 State 更新。
3. 框架收集所有更新，按字段调用对应 Reducer 合并。
4. 合并后的 State 写入 Checkpoint，进入下一超级步。

**关键约束**：
- 并发分支必须**无副作用依赖**（不能依赖彼此执行顺序）。
- Reducer 必须是**纯函数**且满足交换律，否则合并结果不确定。
- 同一 `thread_id` 的 `invoke` 调用本身不可并发（写冲突），并发仅发生在图内部的 fan-out 分支。

**评分标准**：Send API 机制 2 分 / Reducer 协同 2 分 / 约束说明 1 分（满分 5）。

---

### Q8：请说明 LangGraph 中同步 `invoke` 与异步 `ainvoke` 的区别，以及异步执行的优势与注意事项。

**难度**：中级　**考察点**：异步模型

**问题描述**：
请对比 LangGraph 的同步执行接口（`invoke` / `stream`）与异步执行接口（`ainvoke` / `astream`），说明异步执行的优势、适用场景与使用注意事项。

**参考答案**：

**接口对比**：

| 维度 | 同步接口 | 异步接口 |
|------|----------|----------|
| API | `invoke` / `stream` | `ainvoke` / `astream` |
| 阻塞 | 阻塞主线程 | 非阻塞，基于协程 |
| 并发 | 难以高并发 | 可用 `asyncio.gather` 高并发 |
| 节点实现 | 普通函数 | `async def` 函数 |
| 适用场景 | 脚本、CLI、简单服务 | Web 服务、高并发 API |

**异步执行的优势**：
1. **高并发**：单进程内可同时处理大量请求，I/O 等待时不占用 CPU。
2. **资源效率**：协程比线程轻量，上下文切换开销小。
3. **流式响应**：`astream` 可在 Web 服务中实现实时 Token 流式输出。

**代码示例**：

```python
import asyncio
from langgraph.graph import StateGraph, START, END

# 异步节点定义
async def agent_node(state):
    # 模拟异步 LLM 调用
    response = await async_llm.ainvoke(state["messages"])
    return {"messages": [response]}

builder = StateGraph(dict)
builder.add_node("agent", agent_node)
builder.add_edge(START, "agent")
builder.add_edge("agent", END)
graph = builder.compile(checkpointer=checkpointer)

# 异步单次调用
async def single_call():
    config = {"configurable": {"thread_id": "sess-1"}}
    result = await graph.ainvoke({"messages": [("user", "你好")]}, config)
    return result

# 高并发批量调用（不同 thread_id，互不干扰）
async def batch_calls():
    inputs = [{"messages": [("user", f"问题{i}")]} for i in range(100)]
    configs = [{"configurable": {"thread_id": f"sess-{i}"}} for i in range(100)]
    tasks = [graph.ainvoke(inp, cfg) for inp, cfg in zip(inputs, configs)]
    results = await asyncio.gather(*tasks)
    return results
```

**注意事项**：
1. **同 thread_id 不可并发**：同一 `thread_id` 的多次 `ainvoke` 并发调用会导致 Checkpoint 写冲突，需用队列串行化或加锁。
2. **混用风险**：同步与异步接口混用于同一 thread 易引发状态不一致，建议统一。
3. **节点必须 async**：使用 `ainvoke` 时，节点函数应为 `async def`，否则无法获得异步收益。
4. **Checkpointer 也要 async**：高并发场景应使用 `AsyncPostgresSaver` / `AsyncSqliteSaver`，避免同步 I/O 阻塞事件循环。
5. **事件循环**：`ainvoke` 必须在事件循环中调用，不能在同步函数中直接 `await`。

**评分标准**：接口对比 1 分 / 优势 1 分 / 代码示例 1 分 / 注意事项 2 分（满分 5）。

---

## 三、编程题（4题）

### Q9：请实现一个基于 `thread_id` 的多用户客服 Agent，支持新会话创建、多轮对话与历史会话恢复。

**难度**：基础　**考察点**：thread_id 基础使用

**问题描述**：
请用 LangGraph 实现一个客服 Agent，要求：
1. 每个（用户, 会话）组合使用独立 `thread_id`，格式为 `user_{uid}_session_{sid}`。
2. 同一 `thread_id` 内支持多轮对话，自动保留上下文。
3. 提供查询某用户所有历史会话当前状态的接口。
4. 支持从历史会话继续对话。

请给出完整代码。

**参考答案**：

```python
from typing import Annotated, TypedDict
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage

# 1. State 定义
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str

# 2. 模拟 LLM
def fake_llm(messages):
    last = messages[-1].content if messages else ""
    return AIMessage(content=f"客服回复：已收到『{last}』，正在为您处理")

# 3. 节点定义
def agent_node(state: AgentState):
    reply = fake_llm(state["messages"])
    return {"messages": [reply]}

# 4. 构建图
builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_edge(START, "agent")
builder.add_edge("agent", END)

checkpointer = SqliteSaver.from_conn_string("./data/customer_service.db")
graph = builder.compile(checkpointer=checkpointer)

# 5. 会话管理服务
class CustomerService:
    def __init__(self, graph):
        self.graph = graph

    def _thread_id(self, user_id: str, session_id: str) -> str:
        return f"user_{user_id}_session_{session_id}"

    def chat(self, user_id: str, session_id: str, message: str) -> str:
        """多轮对话：同 thread_id 自动加载历史"""
        config = {"configurable": {"thread_id": self._thread_id(user_id, session_id)}}
        result = self.graph.invoke(
            {"messages": [HumanMessage(content=message)], "user_id": user_id},
            config
        )
        return result["messages"][-1].content

    def list_user_sessions(self, user_id: str) -> list:
        """查询用户所有历史会话的当前状态（需配合 thread 列表存储）"""
        # 实际项目应维护用户会话索引表
        sessions = self._load_session_index(user_id)
        results = []
        for sid in sessions:
            config = {"configurable": {"thread_id": self._thread_id(user_id, sid)}}
            state = self.graph.get_state(config)
            if state.values:
                results.append({
                    "session_id": sid,
                    "last_message": state.values["messages"][-1].content,
                    "message_count": len(state.values["messages"]),
                })
        return results

    def resume_session(self, user_id: str, session_id: str, message: str) -> str:
        """恢复历史会话继续对话（与 chat 实现一致，复用 thread_id）"""
        return self.chat(user_id, session_id, message)

    def _load_session_index(self, user_id: str) -> list:
        # 简化示例：实际应从数据库读取该用户的 session 列表
        return ["sess_001", "sess_002"]

# 6. 使用示例
service = CustomerService(graph)
# 首次会话
print(service.chat("u_123", "sess_001", "我的订单号是 12345"))
# 同会话第二轮（自动带上下文）
print(service.chat("u_123", "sess_001", "查一下物流"))
# 查询用户所有会话
for s in service.list_user_sessions("u_123"):
    print(s)
```

**关键点**：
1. `thread_id` 由 `user_id + session_id` 组合，实现双层隔离。
2. 同 `thread_id` 的多次 `invoke` 自动加载历史，无需手动拼接 messages。
3. `get_state(config)` 读取该 thread 的最新状态，用于历史会话列表展示。
4. 生产环境应维护用户→会话索引表，避免全表扫描。

**评分标准**：thread_id 设计 1 分 / 多轮对话 1 分 / 历史查询 1 分 / 会话恢复 1 分 / 代码完整 1 分（满分 5）。

---

### Q10：请实现一个支持人工审批的转账 Agent，使用 `interrupt` + `thread_id` 实现跨进程恢复。

**难度**：中级　**考察点**：HITL 与 thread 续跑

**问题描述**：
请用 LangGraph 实现一个金融转账 Agent，要求：
1. 转账金额 > 10000 时触发 `interrupt`，等待人工审批。
2. 审批结果通过 `Command(resume=...)` 注入恢复。
3. 服务重启后，凭 `thread_id` 可从断点继续执行。
4. 给出审批通过与拒绝两条路径的处理代码。

**参考答案**：

```python
from typing import TypedDict
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
import psycopg

# 1. State 定义
class TransferState(TypedDict):
    user_id: str
    payee: str
    amount: float
    tx_id: str | None
    status: str  # pending / approved / rejected / done / cancelled

# 2. 节点定义
def transfer_node(state: TransferState):
    if state["amount"] > 10000:
        # 触发中断，Checkpointer 自动落盘
        decision = interrupt({
            "action": "transfer",
            "payee": state["payee"],
            "amount": state["amount"],
        })
        if decision == "reject":
            return {"status": "cancelled", "tx_id": None}
        # 通过则继续执行转账
    # 实际转账逻辑
    tx_id = f"TX_{state['user_id']}_{state['payee']}_{int(state['amount'])}"
    return {"status": "done", "tx_id": tx_id}

def notify_node(state: TransferState):
    if state["status"] == "done":
        print(f"[通知] 转账成功，交易号 {state['tx_id']}")
    else:
        print(f"[通知] 转账已取消")
    return {}

# 3. 构建图
builder = StateGraph(TransferState)
builder.add_node("transfer", transfer_node)
builder.add_node("notify", notify_node)
builder.add_edge(START, "transfer")
builder.add_edge("transfer", "notify")
builder.add_edge("notify", END)

# 4. 使用 PostgresSaver（支持跨进程恢复）
DB_URI = "postgresql://user:pass@localhost/lg"
conn = psycopg.connect(DB_URI, autocommit=True)
checkpointer = PostgresSaver(conn)
checkpointer.setup()  # 自动建表
graph = builder.compile(checkpointer=checkpointer)

# 5. 发起转账（触发中断）
def initiate_transfer(user_id, payee, amount):
    thread_id = f"tx_{user_id}_{payee}_{int(amount)}_{id(user_id)}"
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke(
        {"user_id": user_id, "payee": payee, "amount": amount, "tx_id": None, "status": "pending"},
        config
    )
    # 检查是否处于中断态
    state = graph.get_state(config)
    if state.next:  # 还有待执行节点 = 已中断
        print(f"[等待审批] thread_id={thread_id}")
    return thread_id

# 6. 审批恢复（可跨进程重启）
def approve_transfer(thread_id: str, decision: str):
    """decision: 'approve' 或 'reject'"""
    config = {"configurable": {"thread_id": thread_id}}
    # 检查是否确实处于中断态
    state = graph.get_state(config)
    if not state.next:
        print("[错误] 该 thread 未处于中断态")
        return
    # 注入审批结果，从断点续跑
    result = graph.invoke(Command(resume=decision), config)
    print(f"[完成] 最终状态：{result['status']}")

# === 使用示例 ===
if __name__ == "__main__":
    # 进程 A：发起转账
    tid = initiate_transfer("u_001", "payee_abc", 20000)

    # 进程 B（或重启后）：审批通过
    approve_transfer(tid, "approve")
    # 或审批拒绝
    # approve_transfer(tid, "reject")
```

**关键设计点**：
1. **`thread_id` 绑定业务单号**：便于审计与精确恢复。
2. **`interrupt` 自动落盘**：中断前 Checkpointer 保存当前 State，进程重启不丢失。
3. **`Command(resume=...)`**：注入审批结果，图从断点续跑。
4. **`state.next` 判断中断态**：非空表示有待执行节点，即处于中断暂停。
5. **必须用持久化 Checkpointer**：`MemorySaver` 重启即失忆，生产禁用。

**评分标准**：State 设计 1 分 / interrupt 触发 1 分 / Command 恢复 1 分 / 跨进程续跑 1 分 / 完整代码 1 分（满分 5）。

---

### Q11：请使用 `Send` API 实现一个 MapReduce 风格的并行文档处理 Agent，支持动态任务分发与结果聚合。

**难度**：高级　**考察点**：Send API 与 Reducer 协同

**问题描述**：
请用 LangGraph 实现一个文档处理 Agent：
1. 输入一批文档， splitter 节点通过 `Send` API 为每个文档分发一个 worker 并发处理。
2. worker 节点并发执行（模拟 LLM 摘要），通过 Reducer 合并结果。
3. aggregator 节点汇总所有 worker 的结果输出最终摘要。
4. 要求支持失败重试与结果计数。

**参考答案**：

```python
from typing import Annotated, TypedDict
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
import operator
import random

# 1. 主图 State
class MapState(TypedDict):
    documents: list[str]
    results: Annotated[list[str], operator.add]       # 并发拼接
    total: Annotated[int, operator.add]                # 并发累加
    failures: Annotated[list[str], operator.add]       # 失败记录
    final_summary: str

# 2. Worker 节点的独立 State（每个 Send 一份）
class WorkerState(TypedDict):
    document: str
    idx: int

# 3. 节点定义
def splitter(state: MapState):
    """fan-out：为每个文档创建一个 Send"""
    documents = state["documents"]
    return [Send("worker", {"document": doc, "idx": i}) 
            for i, doc in enumerate(documents)]

def worker(state: WorkerState):
    """并发执行：模拟 LLM 摘要，可能失败"""
    doc = state["document"]
    idx = state["idx"]
    # 模拟 20% 失败率
    if random.random() < 0.2:
        return {"failures": [f"doc_{idx}_failed"], "total": 0}
    # 模拟摘要
    summary = f"摘要[{idx}]：{doc[:20]}..."
    return {"results": [summary], "total": 1}

def aggregator(state: MapState):
    """fan-in：汇总所有 worker 结果"""
    success_count = state["total"]
    fail_count = len(state["failures"])
    summary = f"成功处理 {success_count} 篇，失败 {fail_count} 篇。\n"
    summary += "\n".join(state["results"])
    return {"final_summary": summary}

# 4. 构建图
builder = StateGraph(MapState)
builder.add_node("splitter", splitter)
builder.add_node("worker", worker)
builder.add_node("aggregator", aggregator)

builder.add_edge(START, "splitter")
builder.add_conditional_edges("splitter", splitter)  # fan-out
builder.add_edge("worker", "aggregator")             # fan-in
builder.add_edge("aggregator", END)

graph = builder.compile()

# 5. 执行
result = graph.invoke({
    "documents": [
        "LangGraph 是一个用于构建 Agent 应用的框架...",
        "State 是 LangGraph 的核心数据结构...",
        "Reducer 机制处理并发更新...",
        "Checkpoint 实现状态持久化...",
        "Send API 实现 fan-out 并行...",
    ],
    "results": [],
    "total": 0,
    "failures": [],
    "final_summary": "",
})
print(result["final_summary"])
```

**执行流程图**：

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    Start([START]) --> Split[splitter 节点]
    Split -->|Send 1| W1[Worker 1]
    Split -->|Send 2| W2[Worker 2]
    Split -->|Send 3| W3[Worker 3]
    Split -->|Send N| WN[Worker N]
    W1 --> Agg[aggregator 节点]
    W2 --> Agg
    W3 --> Agg
    WN --> Agg
    Agg --> End([END])
    Agg -.->|Reducer 合并<br/>results/total/failures| State[(State)]
```

**关键设计点**：
1. **`Send` 携带独立 State**：每个 worker 收到自己的 `WorkerState`，互不污染。
2. **Reducer 字段定义**：`results`、`total`、`failures` 均使用 `operator.add` 实现并发合并。
3. **`add_conditional_edges` + `Send`**：splitter 既作为节点又作为路由函数，实现 fan-out。
4. **fan-in 收敛**：所有 worker 完成后自动进入 aggregator，无需手动等待。
5. **失败隔离**：单个 worker 失败不影响其他 worker，失败记录单独收集。

**评分标准**：Send API 用法 1 分 / Reducer 定义 1 分 / 失败处理 1 分 / 流程图 1 分 / 代码完整 1 分（满分 5）。

---

### Q12：请实现一个支持异步高并发的多用户查询服务，使用 `ainvoke` + `AsyncPostgresSaver` 处理并发请求。

**难度**：高级　**考察点**：异步并发与线程安全

**问题描述**：
请用 LangGraph 实现一个异步多用户查询服务：
1. 使用 `AsyncPostgresSaver` 支持异步持久化。
2. 节点使用 `async def` 实现，模拟异步 LLM 调用。
3. 同时接收 100 个不同用户的请求，通过 `asyncio.gather` 并发处理。
4. 同一用户的多次请求需串行（避免同 `thread_id` 写冲突），不同用户可并行。

**参考答案**：

```python
import asyncio
from typing import Annotated, TypedDict
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
import asyncpg

# 1. State 定义
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str

# 2. 模拟异步 LLM
class FakeAsyncLLM:
    async def ainvoke(self, messages):
        await asyncio.sleep(0.05)  # 模拟网络 IO
        last = messages[-1].content
        return AIMessage(content=f"回复：{last}")

llm = FakeAsyncLLM()

# 3. 异步节点
async def agent_node(state: AgentState):
    reply = await llm.ainvoke(state["messages"])
    return {"messages": [reply]}

# 4. 构建图
builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_edge(START, "agent")
builder.add_edge("agent", END)

# 5. 异步 Checkpointer
async def build_graph():
    checkpointer = AsyncPostgresSaver.from_conn_string(
        "postgresql://user:pass@localhost/lg"
    )
    await checkpointer.setup()  # 异步建表
    return builder.compile(checkpointer=checkpointer)

# 6. 用户级串行锁 + 跨用户并行
class QueryService:
    def __init__(self, graph):
        self.graph = graph
        self.user_locks: dict[str, asyncio.Lock] = {}

    def _get_lock(self, user_id: str) -> asyncio.Lock:
        if user_id not in self.user_locks:
            self.user_locks[user_id] = asyncio.Lock()
        return self.user_locks[user_id]

    async def query(self, user_id: str, session_id: str, message: str) -> str:
        """单次查询：同 user_id 串行，跨 user_id 并行"""
        # 用户级锁：保证同一用户的多次调用串行，避免 thread_id 写冲突
        async with self._get_lock(user_id):
            thread_id = f"user_{user_id}_session_{session_id}"
            config = {"configurable": {"thread_id": thread_id}}
            result = await self.graph.ainvoke(
                {"messages": [HumanMessage(content=message)], "user_id": user_id},
                config
            )
            return result["messages"][-1].content

# 7. 高并发批量处理
async def batch_concurrent(service: QueryService, requests: list[tuple]):
    """requests: [(user_id, session_id, message), ...]"""
    tasks = [service.query(uid, sid, msg) for uid, sid, msg in requests]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

# 8. 主函数
async def main():
    graph = await build_graph()
    service = QueryService(graph)

    # 模拟 100 个并发请求（不同用户）
    requests = [
        (f"u_{i:03d}", f"sess_{i}", f"用户{i}的问题")
        for i in range(100)
    ]
    results = await batch_concurrent(service, requests)
    
    success = sum(1 for r in results if not isinstance(r, Exception))
    print(f"成功 {success}/100")

    # 同一用户多次请求（自动串行）
    multi_requests = [
        ("u_001", "sess_A", "第一问"),
        ("u_001", "sess_A", "第二问"),  # 同 thread_id，串行执行
        ("u_001", "sess_A", "第三问"),
    ]
    results = await batch_concurrent(service, multi_requests)
    for r in results:
        print(r)

if __name__ == "__main__":
    asyncio.run(main())
```

**关键设计点**：
1. **`AsyncPostgresSaver`**：异步 I/O，不阻塞事件循环，适合高并发。
2. **`async def` 节点**：节点函数必须为协程，否则无法获得异步收益。
3. **用户级 `asyncio.Lock`**：保证同一 `thread_id` 串行调用，避免 Checkpoint 写冲突。
4. **跨用户并行**：不同 `thread_id` 之间无锁竞争，可完全并行。
5. **`asyncio.gather`**：批量并发，`return_exceptions=True` 防止单个失败影响整体。

**评分标准**：异步 Checkpointer 1 分 / async 节点 1 分 / 用户级锁 1 分 / 并发批量 1 分 / 代码完整 1 分（满分 5）。

---

## 四、案例分析题（3题）

### Q13：某线上客服系统出现"用户 A 看到用户 B 的对话记录"事故，请分析原因并给出修复方案。

**难度**：中级　**考察点**：thread_id 隔离与事故排查

**问题描述**：
某客服系统上线后收到多起用户投诉，称看到了他人的订单信息和对话记录。经排查：
- 系统使用 LangGraph + PostgresSaver。
- `thread_id` 生成规则为 `f"session_{session_id}"`，其中 `session_id` 由前端传入。
- 日志显示，事故时段有多个请求的 `session_id` 为 `null` 或空字符串。
- 部分用户反映刷新页面后会看到不同人的对话。

请分析事故根因，并给出完整的修复方案。

**参考答案**：

**根因分析**：

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    A[前端传入 session_id=null] --> B[thread_id = session_null]
    C[另一用户 session_id=null] --> D[thread_id = session_null]
    E[第三用户刷新页面<br/>生成新 session_id] --> F[thread_id 变化<br/>丢失历史]
    B --> G[共享同一 Checkpoint]
    D --> G
    G --> H([数据串号事故])
    F --> I([历史丢失])
```

**问题点**：
1. **`thread_id` 缺少用户维度**：仅用 `session_id` 生成，未绑定 `user_id`，不同用户可能撞车。
2. **空值未校验**：`session_id=null` 导致 `thread_id="session_null"`，所有空值用户共享一份状态。
3. **刷新页面生成新 `session_id`**：前端未持久化 `session_id`，刷新后 `thread_id` 变化，历史丢失。
4. **无后端校验**：完全信任前端传入，未做合法性校验。

**修复方案**：

```python
import uuid
from functools import lru_cache

class ThreadIdGenerator:
    """线程 ID 生成器：保证隔离性与稳定性"""
    
    @staticmethod
    def generate(user_id: str, session_id: str | None = None) -> str:
        # 1. 严格校验 user_id
        if not user_id or not isinstance(user_id, str):
            raise ValueError("user_id 不能为空")
        
        # 2. session_id 为空时由后端生成（不信任前端）
        if not session_id or session_id == "null":
            session_id = f"sess_{uuid.uuid4().hex[:12]}"
        
        # 3. 组合 user_id + session_id，保证用户级隔离
        return f"user_{user_id}_session_{session_id}"

class SessionManager:
    """会话管理：session_id 持久化与校验"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def get_or_create_session(self, user_id: str, session_id: str | None) -> str:
        # 从 Redis 恢复或新建 session_id
        key = f"user_session:{user_id}"
        if not session_id:
            session_id = await self.redis.get(key)
            if not session_id:
                session_id = f"sess_{uuid.uuid4().hex[:12]}"
                await self.redis.set(key, session_id, ex=86400)  # 1天过期
        else:
            # 校验 session_id 归属该用户
            stored = await self.redis.get(key)
            if stored and stored != session_id:
                raise PermissionError("session_id 与用户不匹配")
        return session_id

# 修复后的调用
async def chat_safe(user_id: str, session_id: str | None, message: str):
    # 1. 后端校验/生成 session_id
    session_id = await session_manager.get_or_create_session(user_id, session_id)
    # 2. 生成隔离的 thread_id
    thread_id = ThreadIdGenerator.generate(user_id, session_id)
    config = {"configurable": {"thread_id": thread_id}}
    return await graph.ainvoke({"messages": [HumanMessage(message)]}, config)
```

**预防措施**：
1. **`thread_id` 必须含 `user_id`**：从源头保证用户级隔离。
2. **后端生成 `session_id`**：不信任前端传入，空值由后端补齐。
3. **`session_id` 持久化**：存入 Redis/Cookie，刷新页面不丢失。
4. **校验归属**：每次请求校验 `session_id` 确实属于该 `user_id`。
5. **监控告警**：对 `thread_id` 重复率、空值率设监控，异常时告警。
6. **单元测试**：编写多用户隔离测试，覆盖空值、撞车等边界场景。

**评分标准**：根因分析 2 分 / 修复方案 2 分 / 预防措施 1 分（满分 5）。

---

### Q14：某 LangGraph 服务在高并发下出现"State 写冲突"错误，请分析原因并设计解决方案。

**难度**：高级　**考察点**：并发控制与线程安全

**问题描述**：
某 LangGraph 服务（PostgresSaver + FastAPI）在 QPS 达到 50 时出现以下错误：
```
psycopg.errors.SerializationFailure: could not serialize access due to concurrent update
```
且同一用户的多个请求返回的 State 不一致。系统现状：
- 每个用户使用 `thread_id = f"user_{user_id}"`（不含 session_id）。
- 前端允许用户同时发起多个请求（如同时点"查询订单"和"咨询客服"）。
- 使用同步 `invoke` 接口。

请分析根因，并设计完整解决方案。

**参考答案**：

**根因分析**：

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    subgraph 问题1["问题1：thread_id 粒度过粗"]
        A1[请求1: 查询订单<br/>thread_id=user_001] --> C1[Checkpoint 写入]
        A2[请求2: 咨询客服<br/>thread_id=user_001] --> C2[Checkpoint 写入]
        C1 -.->|同时写入<br/>行锁冲突| X1([SerializationFailure])
    end
    subgraph 问题2["问题2：同 thread 并发破坏 State 一致性"]
        B1[请求1 读取 State v1] --> B2[请求2 读取 State v1]
        B2 --> B3[请求2 写入 State v2]
        B1 --> B4[请求1 写入 State v2<br/>覆盖请求2]
        B4 --> X2([State 不一致])
    end
```

**核心问题**：
1. **`thread_id` 粒度过粗**：用户级而非会话级，多个无关请求共享同一 thread，产生写冲突。
2. **同 `thread_id` 并发调用**：LangGraph 的 Checkpoint 机制不保证同 thread 并发安全，多个写入竞争同一行。
3. **同步接口阻塞**：同步 `invoke` 在高并发下占用 worker，加剧排队与超时。

**解决方案**：

| 方案 | 适用场景 | 复杂度 |
|------|----------|--------|
| **A. 细化 thread_id**：加入 session_id 区分会话 | 多业务线并行 | 低 |
| **B. 用户级串行锁**：同 user_id 请求排队执行 | 单业务线强一致 | 中 |
| **C. 异步接口 + 锁**：`ainvoke` + `asyncio.Lock` | 高并发服务 | 中 |
| **D. 业务分流**：不同业务用不同 thread_id 前缀 | 业务隔离 | 低 |

**推荐方案：A + D 组合（业务隔离） + C（异步化）**：

```python
import asyncio
from collections import defaultdict

class ConcurrencySafeService:
    def __init__(self, graph):
        self.graph = graph
        self.user_locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
    
    def _thread_id(self, user_id: str, business: str, session_id: str) -> str:
        """业务级隔离：不同业务用不同 thread_id 前缀"""
        return f"{business}_{user_id}_{session_id}"
    
    async def invoke_business(
        self, user_id: str, business: str, session_id: str, input_state: dict
    ):
        """按业务+用户维度调用，同维度串行"""
        thread_id = self._thread_id(user_id, business, session_id)
        config = {"configurable": {"thread_id": thread_id}}
        # 同一 (business, user) 串行，避免 Checkpoint 写冲突
        lock_key = f"{business}_{user_id}"
        async with self.user_locks[lock_key]:
            return await self.graph.ainvoke(input_state, config)

# 业务分流示例
service = ConcurrencySafeService(graph)

async def handle_request(user_id: str, action: str, message: str):
    if action == "query_order":
        # 订单查询业务：独立 thread_id
        return await service.invoke_business(
            user_id, "order", "sess_001",
            {"messages": [HumanMessage(message)]}
        )
    elif action == "consult":
        # 客服咨询业务：独立 thread_id
        return await service.invoke_business(
            user_id, "consult", "sess_001",
            {"messages": [HumanMessage(message)]}
        )

# 同一用户可同时发起两个不同业务请求（不冲突）
# 同一业务的多次请求会串行（保证一致性）
```

**配套优化**：
1. **改用 `AsyncPostgresSaver`**：避免同步 I/O 阻塞事件循环。
2. **连接池配置**：PostgresSaver 连接池大小 ≥ 预期并发量。
3. **重试机制**：对 `SerializationFailure` 实现指数退避重试。
4. **监控指标**：QPS、平均延迟、锁等待时间、错误率。
5. **限流降级**：单用户 QPS 限制，防止恶意并发。

**评分标准**：根因分析 2 分 / 方案设计 2 分 / 代码实现 1 分（满分 5）。

---

### Q15：设计一个支持"会话分支"的 Agent 系统，允许从历史某节点分叉出新会话，且不影响原会话。

**难度**：高级　**考察点**：时间旅行与 thread 分叉

**问题描述**：
某 AI 编程助手需要支持"会话分支"功能：
1. 用户在对话过程中可回溯到任意历史节点。
2. 从该节点分叉出一条**新的对话分支**，独立演进。
3. 原会话不受影响，继续保留完整历史。
4. 分支会话与原会话可共存，用户可随时切换。

请设计完整方案，包括 thread_id 设计、分叉逻辑、状态管理，并给出关键代码。

**参考答案**：

**设计方案**：

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    subgraph 原会话["原会话 thread_id=main_001"]
        M1[Checkpoint 1] --> M2[Checkpoint 2]
        M2 --> M3[Checkpoint 3]
        M3 --> M4[Checkpoint 4 当前]
    end
    subgraph 分支会话["分支会话 thread_id=branch_001"]
        M2 -.->|分叉点| B1[复制 Checkpoint 2]
        B1 --> B2[Branch Checkpoint 1]
        B2 --> B3[Branch Checkpoint 2 当前]
    end
    subgraph 分支会话2["分支会话 thread_id=branch_002"]
        M3 -.->|分叉点| B4[复制 Checkpoint 3]
        B4 --> B5[Branch Checkpoint 1 当前]
    end
```

**核心思路**：
1. **每个分支独立 `thread_id`**：原会话 `main_xxx`，分支 `branch_xxx`，互不干扰。
2. **分叉时复制 Checkpoint**：从原会话历史 Checkpoint 复制 State，作为分支的起点。
3. **分支独立演进**：分支会话的后续写入只影响自己的 `thread_id`。
4. **分支元数据**：记录分支来源（原 thread_id + checkpoint_id），支持溯源。

**代码实现**：

```python
import uuid
from typing import TypedDict
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import Annotated

class ChatState(TypedDict):
    messages: Annotated[list, add_messages]
    branch_meta: dict  # 分支元数据

# 构建图（略）
builder = StateGraph(ChatState)
# ... 添加节点 ...
graph = builder.compile(checkpointer=PostgresSaver(conn))

class BranchManager:
    """会话分支管理器"""
    
    def __init__(self, graph):
        self.graph = graph
    
    def list_history(self, main_thread_id: str) -> list:
        """列出原会话的所有历史 Checkpoint"""
        config = {"configurable": {"thread_id": main_thread_id}}
        history = list(self.graph.get_state_history(config))
        return [
            {
                "checkpoint_id": cp.config["configurable"]["checkpoint_id"],
                "step": cp.metadata.get("step"),
                "messages_count": len(cp.values.get("messages", [])),
                "last_message": cp.values["messages"][-1].content if cp.values.get("messages") else "",
            }
            for cp in history
        ]
    
    def fork_branch(
        self, main_thread_id: str, checkpoint_id: str, branch_name: str | None = None
    ) -> str:
        """从原会话的指定 Checkpoint 分叉出新会话"""
        # 1. 读取原会话的历史快照
        source_config = {
            "configurable": {
                "thread_id": main_thread_id,
                "checkpoint_id": checkpoint_id,
            }
        }
        source_state = self.graph.get_state(source_config)
        if not source_state.values:
            raise ValueError("源 Checkpoint 不存在或为空")
        
        # 2. 生成新分支的 thread_id
        branch_id = branch_name or f"branch_{uuid.uuid4().hex[:8]}"
        branch_thread_id = f"branch_{branch_id}_from_{main_thread_id}"
        
        # 3. 用源 State 初始化新分支（首次 invoke 写入起点）
        init_config = {"configurable": {"thread_id": branch_thread_id}}
        # 添加分支元数据
        init_state = {
            **source_state.values,
            "branch_meta": {
                "source_thread": main_thread_id,
                "source_checkpoint": checkpoint_id,
                "fork_step": source_state.metadata.get("step"),
            },
        }
        # 用 update_state 注入初始 State
        self.graph.update_state(init_config, init_state, as_node=START)
        
        return branch_thread_id
    
    def continue_branch(self, branch_thread_id: str, message: str):
        """在分支会话上继续对话"""
        config = {"configurable": {"thread_id": branch_thread_id}}
        return self.graph.invoke(
            {"messages": [("user", message)]}, config
        )
    
    def get_branch_tree(self, main_thread_id: str) -> dict:
        """获取会话分支树（原会话 + 所有分支）"""
        # 实际项目应维护分支索引表
        # 此处简化为查询所有 branch_xxx_from_main_xxx 的 thread
        pass

# 使用示例
bm = BranchManager(graph)

# 1. 原会话对话
main_tid = "main_001"
graph.invoke({"messages": [("user", "你好")]}, {"configurable": {"thread_id": main_tid}})
graph.invoke({"messages": [("user", "帮我写个函数")]}, {"configurable": {"thread_id": main_tid}})
graph.invoke({"messages": [("user", "改成类")]}, {"configurable": {"thread_id": main_tid}})

# 2. 查看历史，选择分叉点
history = bm.list_history(main_tid)
print(history)
# 选择第 2 个 Checkpoint（"帮我写个函数"之后）

# 3. 从该点分叉
branch_tid = bm.fork_branch(main_tid, history[1]["checkpoint_id"], "v2_类实现")

# 4. 在分支上继续对话（不影响原会话）
bm.continue_branch(branch_tid, "用 dataclass 实现")

# 5. 原会话不受影响
state = graph.get_state({"configurable": {"thread_id": main_tid}})
print("原会话最后消息:", state.values["messages"][-1].content)
```

**关键设计点**：
1. **独立 `thread_id`**：分支用 `branch_xxx_from_main_xxx` 命名，便于溯源与隔离。
2. **`get_state` + `update_state`**：读取源快照后，通过 `update_state` 注入新 thread 作为起点。
3. **`as_node=START`**：将注入的 State 视为起始节点，后续 `invoke` 从此续跑。
4. **分支元数据**：记录 `branch_meta` 字段保存来源信息，支持溯源与可视化。
5. **原会话零影响**：分支的所有写入都在新 `thread_id` 下，原 Checkpoint 链不变。

**扩展能力**：
- **多层分支**：分支可继续分叉，形成分支树。
- **分支合并**：将分支的最终 State 合并回原会话（业务层处理冲突）。
- **分支对比**：对比两个分支的 State 差异，辅助用户选择最佳路径。
- **分支可视化**：用 LangGraph Studio 展示分支树，支持交互式切换。

**评分标准**：方案设计 2 分 / 分叉逻辑 2 分 / 代码实现 1 分（满分 5）。

---

## 五、评分总览

| 题号 | 类型 | 难度 | 考察重点 | 满分 |
|------|------|------|----------|------|
| Q1 | 选择题 | 基础 | Thread 概念理解 | 5 |
| Q2 | 选择题 | 基础 | thread_id vs checkpoint_id | 5 |
| Q3 | 选择题 | 中级 | thread_id 设计策略 | 5 |
| Q4 | 选择题 | 高级 | 并发与异步模型 | 5 |
| Q5 | 简答题 | 基础 | Thread 定义与生命周期 | 5 |
| Q6 | 简答题 | 中级 | 三大标识体系 | 5 |
| Q7 | 简答题 | 高级 | Send API 与 Reducer 协同 | 5 |
| Q8 | 简答题 | 中级 | 同步 vs 异步执行 | 5 |
| Q9 | 编程题 | 基础 | 多用户客服 Agent | 5 |
| Q10 | 编程题 | 中级 | HITL 跨进程恢复 | 5 |
| Q11 | 编程题 | 高级 | Send API MapReduce | 5 |
| Q12 | 编程题 | 高级 | 异步高并发服务 | 5 |
| Q13 | 案例分析 | 中级 | thread_id 隔离事故排查 | 5 |
| Q14 | 案例分析 | 高级 | 并发写冲突解决方案 | 5 |
| Q15 | 案例分析 | 高级 | 会话分支设计 | 5 |

**面试官使用指南**：

- **初级岗位**（1-3 年）：重点考察 Q1、Q2、Q5、Q9，要求概念清晰、能正确使用 `thread_id`。
- **中级岗位**（3-5 年）：增加 Q3、Q6、Q8、Q10、Q13，要求理解隔离设计、HITL 与异步模型，能排查常见问题。
- **高级岗位**（5 年+）：重点考察 Q4、Q7、Q11、Q12、Q14、Q15，要求掌握并发原理、能设计高并发服务与复杂场景方案。

**面试建议**：
1. **概念先行**：先用选择题（Q1-Q4）快速判断候选人基础。
2. **原理深挖**：用简答题（Q5-Q8）考察对底层机制的理解深度。
3. **代码能力**：用编程题（Q9-Q12）验证实际动手能力，建议现场编码或白板书写。
4. **综合应用**：用案例分析题（Q13-Q15）评估架构设计与问题排查能力，关注方案的可落地性与扩展性。
5. **追问延展**：每题可追问"为什么这样设计""还有什么替代方案""生产环境有哪些坑"，考察思维广度。
