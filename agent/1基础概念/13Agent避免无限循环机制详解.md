# AI Agent 避免无限循环机制详解

> **文档说明**：本文档系统阐述 AI Agent 系统中**避免无限循环执行任务**的机制与实现方法。内容涵盖常见无限循环场景分析、预防策略（任务状态跟踪、执行次数限制、循环检测算法）、中断机制设计、异常处理流程，并结合具体案例说明各方法的适用场景与优缺点。文档提供可落地的技术方案与代码示例，旨在帮助开发者全面理解并有效规避 Agent 执行过程中的无限循环问题，提升系统稳定性与资源利用率。

## 目录

- [一、问题背景：无限循环是 Agent 的“沉默杀手”](#一问题背景无限循环是-agent-的沉默杀手)
- [二、常见无限循环场景分析](#二常见无限循环场景分析)
- [三、预防策略体系](#三预防策略体系)
- [四、循环检测算法详解](#四循环检测算法详解)
- [五、中断机制设计](#五中断机制设计)
- [六、异常处理流程](#六异常处理流程)
- [七、完整工程实现](#七完整工程实现)
- [八、案例分析与实践指南](#八案例分析与实践指南)
- [九、总结与最佳实践](#九总结与最佳实践)

---

## 一、问题背景：无限循环是 Agent 的“沉默杀手”

在 AI Agent 的工程实践中，**无限循环（Infinite Loop）** 是最具破坏性的故障模式之一。它不像明确的错误那样会立即抛出异常并终止，而是让 Agent 在“看似正常工作”的状态下持续消耗资源，直至 Token 配额耗尽、API 调用超限或系统崩溃。

### 1.1 为什么 Agent 容易陷入无限循环？

Agent 的核心决策依赖于 LLM，而 LLM 的**概率性输出**与 Agent 的**自主循环执行**机制结合，天然地埋下了无限循环的隐患：

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  Agent 无限循环的根因分析                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   根因 1: LLM 的概率性输出                                             │
│   ┌───────────────────────────────────────────────────────────────┐    │
│   │ • 同一状态可能产出不同决策                                     │    │
│   │ • 可能反复选择已失败的动作                                     │    │
│   │ • 无法稳定判断"任务已完成"                                     │    │
│   └───────────────────────────────────────────────────────────────┘    │
│                                                                         │
│   根因 2: ReAct 等循环执行范式                                          │
│   ┌───────────────────────────────────────────────────────────────┐    │
│   │ • Thought → Action → Observation → Thought ... 循环            │    │
│   │ • 缺乏明确的终止条件判断                                       │    │
│   │ • 错误恢复可能导致回到起点                                     │    │
│   └───────────────────────────────────────────────────────────────┘    │
│                                                                         │
│   根因 3: 环境的动态性与不确定性                                        │
│   ┌───────────────────────────────────────────────────────────────┐    │
│   │ • 工具调用失败后的重试逻辑可能无界                              │    │
│   │ • 环境状态变化导致 Agent 反复尝试                              │    │
│   │ • 部分可观测性导致 Agent 无法确认任务完成                      │    │
│   └───────────────────────────────────────────────────────────────┘    │
│                                                                         │
│   根因 4: 规划与反思机制的副作用                                        │
│   ┌───────────────────────────────────────────────────────────────┐    │
│   │ • 反思后重新规划可能导致循环                                   │    │
│   │ • 任务分解不当形成环状依赖                                     │    │
│   │ • 自我修正机制过度触发                                         │    │
│   └───────────────────────────────────────────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 无限循环的危害

| 危害类型 | 具体表现 | 影响程度 |
|---------|---------|:--------:|
| **资源耗尽** | Token 消耗呈指数级增长，API 配额迅速耗尽 | ⭐⭐⭐⭐⭐ |
| **成本失控** | 单次任务成本可能从几元飙升到几百元 | ⭐⭐⭐⭐⭐ |
| **服务阻塞** | 长时间占用计算资源，影响其他任务执行 | ⭐⭐⭐⭐ |
| **用户体验崩塌** | 任务迟迟无响应，用户被迫手动中断 | ⭐⭐⭐⭐ |
| **数据污染** | 循环产生的无效日志污染记忆库和审计日志 | ⭐⭐⭐ |
| **级联故障** | 多 Agent 系统中，一个 Agent 循环可能拖垮整个系统 | ⭐⭐⭐⭐⭐ |

> **与文档 10 的关联**：在 [10Agent技术挑战与未来展望](file:///m:/note-book/agent/1基础概念/10Agent技术挑战与未来展望.md) 的“可靠性挑战”章节中，已将“死循环与无限重试”列为 Agent 的头号可靠性问题。本文档将针对这一问题提供系统性的解决方案。

---

## 二、常见无限循环场景分析

要有效预防无限循环，首先需要识别其出现的典型场景。

### 2.1 场景一：工具调用失败后的盲目重试

**场景描述**：Agent 调用某个工具（如 API）失败后，不分析失败原因，直接重试，形成循环。

```
Agent 执行轨迹:
─────────────────────────────────────────────────────────────────────
Step 1: Thought: 我需要查询数据库
        Action: query_db(sql="SELECT * FROM users")
        Observation: Error: Connection refused

Step 2: Thought: 数据库连接失败，我再试一次
        Action: query_db(sql="SELECT * FROM users")   ← 完全相同的动作
        Observation: Error: Connection refused

Step 3: Thought: 还是失败，继续尝试
        Action: query_db(sql="SELECT * FROM users")   ← 再次重复
        Observation: Error: Connection refused

... (无限循环)
─────────────────────────────────────────────────────────────────────
```

**根因分析**：
- Agent 缺乏对“相同动作相同结果”的认知
- 没有记录已失败的动作序列
- 缺乏针对瞬时错误与永久错误的区分

**常见触发条件**：
- 网络波动导致的超时
- API 服务临时不可用
- 认证过期导致的 401 错误（Agent 却误以为是网络问题）

### 2.2 场景二：任务状态判断失败导致的目标未达成循环

**场景描述**：Agent 已经完成了任务，但由于无法正确判断“任务已完成”，继续执行。

```
Agent 执行轨迹:
─────────────────────────────────────────────────────────────────────
目标: "在项目中创建一个 README.md 文件"

Step 1: Action: create_file("README.md", "# My Project")
        Observation: File created successfully

Step 2: Thought: 我需要确认文件是否创建成功
        Action: read_file("README.md")
        Observation: "# My Project"

Step 3: Thought: 文件内容看起来对，但我不确定是否符合要求
        Action: create_file("README.md", "# My Project")   ← 重复创建
        Observation: File already exists, overwritten

Step 4: Thought: 让我再确认一下
        Action: read_file("README.md")
        Observation: "# My Project"

... (Agent 无法确信任务完成，持续循环)
─────────────────────────────────────────────────────────────────────
```

**根因分析**：
- 缺乏明确的“任务完成判据（Termination Criteria）”
- LLM 对“是否完成”的判断过于保守
- 缺乏完成状态的外部确认机制

### 2.3 场景三：反思机制导致的“修复-破坏”循环

**场景描述**：Agent 在反思中发现问题并修复，但修复过程引入了新问题，反思后又“修复”回原状，形成震荡。

```
Agent 执行轨迹:
─────────────────────────────────────────────────────────────────────
目标: "优化函数性能"

Step 1: Action: edit_code(添加缓存优化)
        Observation: 性能提升，但引入了内存泄漏

Step 2: [反思] 发现内存泄漏
        Action: edit_code(移除缓存优化)   ← 回到原始状态
        Observation: 内存泄漏修复，但性能下降

Step 3: [反思] 发现性能下降
        Action: edit_code(添加缓存优化)   ← 又回到 Step 1 的状态

Step 4: [反思] 又发现内存泄漏
        ... (A → B → A → B 震荡循环)
─────────────────────────────────────────────────────────────────────
```

**根因分析**：
- 反思缺乏对历史尝试的记忆
- 缺乏对“已尝试方案”的去重检测
- 修复策略空间有限，反复在几个方案间切换

### 2.4 场景四：子任务间的环状依赖

**场景描述**：在多步骤任务或多 Agent 协作中，子任务之间形成了环状依赖。

```
Agent 执行轨迹:
─────────────────────────────────────────────────────────────────────
任务分解:
  Task A: 设计数据库 schema → 需要先知道 API 接口设计 (依赖 Task B)
  Task B: 设计 API 接口     → 需要先知道数据库 schema (依赖 Task A)

执行:
  Agent 尝试 Task A → 发现需要 Task B → 尝试 Task B → 
  发现需要 Task A → 尝试 Task A → ... (环状依赖循环)
─────────────────────────────────────────────────────────────────────
```

**根因分析**：
- 任务分解时未检测依赖关系中的环
- 缺乏对依赖图（DAG）的拓扑排序验证

### 2.5 场景五：环境状态漂移导致的“追逐”循环

**场景描述**：Agent 试图达到某个目标状态，但环境在不断变化，Agent 永远“追不上”。

```
Agent 执行轨迹:
─────────────────────────────────────────────────────────────────────
目标: "将服务器 CPU 使用率降低到 50% 以下"

Step 1: 当前 CPU: 85% → Action: 扩容 → CPU 降到 45%
Step 2: [检测] CPU: 45% ✅
        但扩容触发了负载均衡重新分配，CPU 又升到 70%
Step 3: Action: 再次扩容 → CPU 降到 48%
Step 4: [检测] CPU: 48% → 又因负载均衡升到 65%
        ... (Agent 持续追逐一个移动的目标)
─────────────────────────────────────────────────────────────────────
```

**根因分析**：
- Agent 的行动本身在改变环境状态
- 缺乏对“稳态”的判断（系统是否已收敛）
- 目标设定过于刚性，缺乏容忍区间

---

## 三、预防策略体系

针对上述场景，我们需要构建一个**多层次的预防策略体系**。

### 3.1 预防策略全景图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  Agent 无限循环预防策略体系                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  层级 1: 前置预防 (事前)                                                │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │ • 任务依赖图无环验证 (DAG Validation)                          │     │
│  │ • 明确的终止条件定义 (Termination Criteria)                    │     │
│  │ • 资源预算预分配 (Budget Allocation)                           │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                                                         │
│  层级 2: 过程监控 (事中)                                                │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │ • 任务状态跟踪 (State Tracking)                                │     │
│  │ • 执行次数限制 (Step Limit)                                    │     │
│  │ • 循环检测算法 (Loop Detection)                                │     │
│  │ • 重复动作检测 (Duplicate Action Detection)                    │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                                                         │
│  层级 3: 中断与恢复 (事中)                                              │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │ • 主动中断机制 (Active Interruption)                           │     │
│  │ • 降级策略 (Graceful Degradation)                              │     │
│  │ • 人工介入请求 (Human Escalation)                              │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                                                         │
│  层级 4: 异常处理与学习 (事后)                                          │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │ • 异常分类与处理 (Error Classification)                        │     │
│  │ • 循环原因分析与记录 (Root Cause Analysis)                     │     │
│  │ • 经验学习与策略更新 (Experience Learning)                     │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 策略一：任务状态跟踪（State Tracking）

**核心思想**：为 Agent 的每一步执行维护一个完整的状态记录，使其能“知道自己做过什么”。

#### 3.2.1 状态指纹（State Fingerprint）

通过为每个状态计算一个唯一的“指纹”（哈希值），可以高效地检测 Agent 是否回到了之前的状态。

```python
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExecutionState:
    """Agent 执行状态的快照"""
    step: int
    action_name: str
    action_params: Dict[str, Any]
    observation_summary: str
    goal_progress: float  # 0.0 - 1.0
    fingerprint: str = field(default="")  # 状态指纹
    
    def __post_init__(self):
        """计算状态指纹"""
        # 将关键状态信息序列化并哈希
        fingerprint_data = {
            "action": self.action_name,
            "params": self._normalize_params(self.action_params),
            "obs_hash": hashlib.md5(
                self.observation_summary.encode()
            ).hexdigest()[:8],
            "progress": round(self.goal_progress, 2),
        }
        self.fingerprint = hashlib.sha256(
            json.dumps(fingerprint_data, sort_keys=True).encode()
        ).hexdigest()[:16]
    
    def _normalize_params(self, params: Dict) -> Dict:
        """规范化参数，忽略不影响结果的微小差异"""
        normalized = {}
        for key, value in params.items():
            # 字符串类型去除首尾空格并统一大小写
            if isinstance(value, str):
                normalized[key] = value.strip().lower()
            else:
                normalized[key] = value
        return normalized


class StateTracker:
    """任务状态跟踪器"""
    
    def __init__(self):
        self.state_history: List[ExecutionState] = []
        self.fingerprint_counts: Dict[str, int] = {}  # 指纹出现次数
    
    def record(self, state: ExecutionState):
        """记录新的执行状态"""
        self.state_history.append(state)
        self.fingerprint_counts[state.fingerprint] = \
            self.fingerprint_counts.get(state.fingerprint, 0) + 1
    
    def get_repeat_count(self, fingerprint: str) -> int:
        """获取某状态的出现次数"""
        return self.fingerprint_counts.get(fingerprint, 0)
    
    def is_repeated_state(self, state: ExecutionState, threshold: int = 2) -> bool:
        """判断是否为重复状态"""
        return self.get_repeat_count(state.fingerprint) >= threshold
    
    def get_recent_actions(self, window: int = 5) -> List[ExecutionState]:
        """获取最近的 N 步执行记录"""
        return self.state_history[-window:]
```

#### 3.2.2 优缺点分析

| 优点 | 缺点 |
|------|------|
| 实现简单，计算开销小 | 指纹冲突可能导致误判 |
| 能精确检测完全相同的状态 | 对“相似但不完全相同”的状态不敏感 |
| 适用于任何类型的 Agent | 需要合理设计哪些字段纳入指纹 |

### 3.3 策略二：执行次数限制（Step Limit）

**核心思想**：为 Agent 的执行设置硬性上限，作为防止无限循环的“最后防线”。

#### 3.3.1 多层级限制设计

```python
from enum import Enum
from typing import Callable, Optional


class LimitType(Enum):
    """限制类型"""
    TOTAL_STEPS = "total_steps"           # 总步数限制
    TOOL_CALLS = "tool_calls"             # 单工具调用次数限制
    LLM_CALLS = "llm_calls"               # LLM 调用次数限制
    TOKEN_USAGE = "token_usage"           # Token 消耗限制
    EXECUTION_TIME = "execution_time"     # 执行时间限制
    COST = "cost"                         # 成本限制（美元）


@dataclass
class LimitConfig:
    """限制配置"""
    limit_type: LimitType
    max_value: float
    current_value: float = 0
    warning_threshold: float = 0.8  # 80% 时发出警告
    hard_stop: bool = True          # 是否硬性停止
    on_exceed: Optional[Callable] = None  # 超限时的回调
    
    @property
    def usage_ratio(self) -> float:
        return self.current_value / self.max_value
    
    @property
    def is_exceeded(self) -> bool:
        return self.current_value >= self.max_value
    
    @property
    def is_warning(self) -> bool:
        return self.usage_ratio >= self.warning_threshold


class ExecutionLimiter:
    """多层级执行限制器"""
    
    def __init__(self):
        self.limits: Dict[LimitType, LimitConfig] = {}
        self._setup_default_limits()
    
    def _setup_default_limits(self):
        """设置默认限制"""
        self.limits[LimitType.TOTAL_STEPS] = LimitConfig(
            limit_type=LimitType.TOTAL_STEPS,
            max_value=50,
            hard_stop=True
        )
        self.limits[LimitType.TOOL_CALLS] = LimitConfig(
            limit_type=LimitType.TOOL_CALLS,
            max_value=10,  # 每个工具最多调用 10 次
            hard_stop=True
        )
        self.limits[LimitType.TOKEN_USAGE] = LimitConfig(
            limit_type=LimitType.TOKEN_USAGE,
            max_value=500000,
            hard_stop=True
        )
        self.limits[LimitType.EXECUTION_TIME] = LimitConfig(
            limit_type=LimitType.EXECUTION_TIME,
            max_value=300,  # 5 分钟
            hard_stop=True
        )
    
    def increment(self, limit_type: LimitType, amount: float = 1):
        """增加某种限制的计数"""
        if limit_type in self.limits:
            self.limits[limit_type].current_value += amount
    
    def check_limits(self) -> Dict[str, Any]:
        """
        检查所有限制
        返回: {exceeded: bool, warnings: List, stop_reason: str}
        """
        result = {
            "exceeded": False,
            "warnings": [],
            "stop_reason": None
        }
        
        for limit_type, config in self.limits.items():
            if config.is_exceeded and config.hard_stop:
                result["exceeded"] = True
                result["stop_reason"] = (
                    f"已达到 {limit_type.value} 上限: "
                    f"{config.current_value}/{config.max_value}"
                )
                if config.on_exceed:
                    config.on_exceed(config)
                break
            elif config.is_warning:
                result["warnings"].append(
                    f"警告: {limit_type.value} 即将达到上限 "
                    f"({config.usage_ratio:.0%})"
                )
        
        return result
    
    def get_remaining_budget(self, limit_type: LimitType) -> float:
        """获取某项限制的剩余预算"""
        if limit_type not in self.limits:
            return float('inf')
        config = self.limits[limit_type]
        return max(0, config.max_value - config.current_value)
```

#### 3.3.2 优缺点分析

| 优点 | 缺点 |
|------|------|
| 实现简单，绝对可靠 | 可能过早中断合法的长任务 |
| 作为最后防线，确保系统安全 | 阈值难以通用化设定 |
| 支持多维度限制 | 无法区分“正常的长任务”和“循环” |

> **设计建议**：执行次数限制应作为**兜底策略**，而非主要检测手段。合理的上限需要根据具体任务类型动态调整。

### 3.4 策略三：明确的终止条件定义（Termination Criteria）

**核心思想**：在任务开始前，明确定义“什么情况下算任务完成”，避免 Agent 因无法判断完成状态而持续循环。

#### 3.4.1 终止条件的设计模式

```python
from abc import ABC, abstractmethod
from typing import Any


class TerminationCriterion(ABC):
    """终止条件抽象基类"""
    
    @abstractmethod
    def is_satisfied(self, state: Dict[str, Any], history: List) -> bool:
        """判断终止条件是否满足"""
        pass
    
    @abstractmethod
    def describe(self) -> str:
        """描述终止条件（用于 Prompt 注入）"""
        pass


class OutputExistsCriterion(TerminationCriterion):
    """输出存在终止条件：检查目标文件/资源是否已创建"""
    
    def __init__(self, target_path: str):
        self.target_path = target_path
    
    def is_satisfied(self, state: Dict[str, Any], history: List) -> bool:
        import os
        return os.path.exists(self.target_path)
    
    def describe(self) -> str:
        return f"当文件 {self.target_path} 存在时，任务完成"


class GoalAchievedCriterion(TerminationCriterion):
    """目标达成终止条件：通过 LLM 判断目标是否达成"""
    
    def __init__(self, goal: str, llm_validator):
        self.goal = goal
        self.llm_validator = llm_validator
    
    def is_satisfied(self, state: Dict[str, Any], history: List) -> bool:
        validation_prompt = f"""
        目标: {self.goal}
        当前状态: {state}
        历史步骤: {history[-3:]}  # 只看最近 3 步
        
        问题: 目标是否已经达成？
        请只回答 "YES" 或 "NO"，并附上一句话理由。
        """
        response = self.llm_validator.generate(validation_prompt)
        return response.strip().upper().startswith("YES")
    
    def describe(self) -> str:
        return f"当以下目标达成时，任务完成: {self.goal}"


class CompositeTerminationCriterion(TerminationCriterion):
    """组合终止条件：支持 AND / OR 逻辑"""
    
    def __init__(self, criteria: List[TerminationCriterion], mode: str = "AND"):
        self.criteria = criteria
        self.mode = mode  # "AND" 或 "OR"
    
    def is_satisfied(self, state: Dict[str, Any], history: List) -> bool:
        results = [c.is_satisfied(state, history) for c in self.criteria]
        if self.mode == "AND":
            return all(results)
        else:
            return any(results)
    
    def describe(self) -> str:
        connector = " 且 " if self.mode == "AND" else " 或 "
        descriptions = [c.describe() for c in self.criteria]
        return connector.join(descriptions)


# 使用示例
termination = CompositeTerminationCriterion([
    OutputExistsCriterion("/project/README.md"),
    GoalAchievedCriterion("创建项目说明文档", llm_validator),
], mode="OR")
```

---

## 四、循环检测算法详解

循环检测是预防无限循环的**核心技术**。本节介绍三种由浅入深的检测算法。

### 4.1 算法一：重复动作检测（Duplicate Action Detection）

**适用场景**：检测 Agent 是否在执行完全相同或高度相似的动作。

#### 4.1.1 算法实现

```python
from typing import List, Tuple
from difflib import SequenceMatcher


class DuplicateActionDetector:
    """重复动作检测器"""
    
    def __init__(self, similarity_threshold: float = 0.85, 
                 lookback_window: int = 10):
        self.similarity_threshold = similarity_threshold
        self.lookback_window = lookback_window
        self.action_history: List[Tuple[str, Dict]] = []
    
    def check(self, action_name: str, action_params: Dict) -> Dict[str, Any]:
        """
        检查当前动作是否与历史动作重复
        返回: {is_duplicate: bool, similar_count: int, 
               most_similar: Tuple, similarity: float}
        """
        current_action = (action_name, action_params)
        duplicates = []
        
        # 只检查最近 N 步
        for i, past_action in enumerate(
            self.action_history[-self.lookback_window:]
        ):
            similarity = self._compute_similarity(current_action, past_action)
            if similarity >= self.similarity_threshold:
                duplicates.append((i, past_action, similarity))
        
        result = {
            "is_duplicate": len(duplicates) > 0,
            "similar_count": len(duplicates),
            "most_similar": duplicates[0] if duplicates else None,
        }
        
        # 记录当前动作
        self.action_history.append(current_action)
        
        return result
    
    def _compute_similarity(self, action1: Tuple[str, Dict], 
                              action2: Tuple[str, Dict]) -> float:
        """计算两个动作的相似度 (0-1)"""
        # 动作名称必须相同
        if action1[0] != action2[0]:
            return 0.0
        
        # 比较参数
        params1 = action1[1]
        params2 = action2[1]
        
        if params1 == params2:
            return 1.0  # 完全相同
        
        # 对字符串参数使用序列匹配
        param_similarities = []
        all_keys = set(params1.keys()) | set(params2.keys())
        
        for key in all_keys:
            val1 = str(params1.get(key, ""))
            val2 = str(params2.get(key, ""))
            
            if val1 and val2:
                similarity = SequenceMatcher(None, val1, val2).ratio()
            elif not val1 and not val2:
                similarity = 1.0
            else:
                similarity = 0.0
            
            param_similarities.append(similarity)
        
        return sum(param_similarities) / len(param_similarities) \
            if param_similarities else 0.0


# 使用示例
detector = DuplicateActionDetector(similarity_threshold=0.85)

# 模拟 Agent 执行
actions = [
    ("query_db", {"sql": "SELECT * FROM users"}),
    ("query_db", {"sql": "SELECT * FROM users"}),      # 完全重复
    ("query_db", {"sql": "SELECT * FROM users "}),      # 几乎相同
    ("query_db", {"sql": "SELECT name FROM users"}),   # 不同查询
]

for action_name, params in actions:
    result = detector.check(action_name, params)
    print(f"Action: {action_name}({params})")
    print(f"  重复: {result['is_duplicate']}, 相似次数: {result['similar_count']}")
```

#### 4.1.2 优缺点

| 优点 | 缺点 |
|------|------|
| 实现简单，计算开销低 | 只能检测“相同动作”，无法检测“不同动作但相同效果” |
| 实时性好 | 对参数的微小变化可能过于敏感或不敏感 |
| 可配置相似度阈值 | 不适合检测复杂的循环模式 |

### 4.2 算法二：状态序列模式匹配（State Sequence Pattern Matching）

**适用场景**：检测 Agent 是否陷入了一个“状态序列循环”（如 A→B→C→A→B→C→...）。

#### 4.2.1 基于周期检测的算法

```python
from typing import List, Optional


class SequenceLoopDetector:
    """状态序列循环检测器"""
    
    def __init__(self, min_cycle_length: int = 2, 
                 min_repeat_count: int = 2,
                 max_history_size: int = 100):
        self.min_cycle_length = min_cycle_length
        self.min_repeat_count = min_repeat_count
        self.max_history_size = max_history_size
        self.state_sequence: List[str] = []
    
    def add_state(self, state_fingerprint: str):
        """添加新的状态指纹"""
        self.state_sequence.append(state_fingerprint)
        # 限制历史长度，避免内存无限增长
        if len(self.state_sequence) > self.max_history_size:
            self.state_sequence = self.state_sequence[-self.max_history_size:]
    
    def detect_loop(self) -> Optional[Dict]:
        """
        检测序列中是否存在循环
        返回: {cycle_length: int, cycle_start: int, 
               repeat_count: int, cycle_states: List} 或 None
        """
        n = len(self.state_sequence)
        if n < self.min_cycle_length * self.min_repeat_count:
            return None
        
        # 尝试不同的循环长度
        for cycle_len in range(self.min_cycle_length, n // 2 + 1):
            # 从序列末尾向前查找循环
            cycle_candidate = self.state_sequence[-cycle_len:]
            
            # 检查这个模式重复了多少次
            repeat_count = 0
            pos = n - cycle_len
            
            while pos >= 0:
                segment = self.state_sequence[pos:pos + cycle_len]
                if segment == cycle_candidate:
                    repeat_count += 1
                    pos -= cycle_len
                else:
                    break
            
            if repeat_count >= self.min_repeat_count:
                return {
                    "cycle_length": cycle_len,
                    "cycle_start": n - repeat_count * cycle_len,
                    "repeat_count": repeat_count,
                    "cycle_states": cycle_candidate,
                }
        
        return None
    
    def is_in_loop(self) -> bool:
        """快速判断是否处于循环中"""
        return self.detect_loop() is not None


# 使用示例
detector = SequenceLoopDetector(min_cycle_length=2, min_repeat_count=2)

# 模拟一个 A→B→C→A→B→C 的循环
states = ["A", "B", "C", "A", "B", "C", "A", "B"]

for state in states:
    detector.add_state(state)

loop_info = detector.detect_loop()
if loop_info:
    print(f"检测到循环!")
    print(f"  循环长度: {loop_info['cycle_length']}")
    print(f"  重复次数: {loop_info['repeat_count']}")
    print(f"  循环状态: {loop_info['cycle_states']}")
    print(f"  循环起点: {loop_info['cycle_start']}")
```

#### 4.2.2 优缺点

| 优点 | 缺点 |
|------|------|
| 能检测复杂的循环模式（A→B→C→A→...） | 对状态指纹的准确性依赖高 |
| 能精确定位循环的起点和长度 | 时间复杂度为 O(n²)，不适合超长序列 |
| 能区分“正常重复”和“循环” | 需要积累一定历史才能检测 |

### 4.3 算法三：基于有向图的环检测（Graph-based Cycle Detection）

**适用场景**：检测任务依赖关系或状态转移图中是否存在环，适用于多步骤规划和多 Agent 协作场景。

#### 4.3.1 深度优先搜索（DFS）环检测

```python
from typing import Dict, List, Set


class TaskDependencyGraph:
    """任务依赖图与环检测"""
    
    def __init__(self):
        # 邻接表表示: {task_id: [dependency_task_ids]}
        self.graph: Dict[str, List[str]] = {}
    
    def add_task(self, task_id: str, dependencies: List[str] = None):
        """添加任务及其依赖"""
        self.graph[task_id] = dependencies or []
        # 确保依赖的任务也在图中
        for dep in (dependencies or []):
            if dep not in self.graph:
                self.graph[dep] = []
    
    def has_cycle(self) -> tuple:
        """
        使用 DFS 检测图中是否有环
        返回: (has_cycle: bool, cycle_path: List[str])
        """
        # 节点状态: 0=未访问, 1=访问中(在当前路径上), 2=已完成
        color = {node: 0 for node in self.graph}
        
        for start_node in self.graph:
            if color[start_node] == 0:
                cycle = self._dfs_cycle_detect(start_node, color, [])
                if cycle:
                    return True, cycle
        
        return False, []
    
    def _dfs_cycle_detect(self, node: str, color: Dict[str, int], 
                          path: List[str]) -> List[str]:
        """DFS 递归检测环"""
        color[node] = 1  # 标记为访问中
        path.append(node)
        
        for neighbor in self.graph.get(node, []):
            if color[neighbor] == 1:
                # 发现环：从路径中提取环
                cycle_start = path.index(neighbor)
                return path[cycle_start:] + [neighbor]
            elif color[neighbor] == 0:
                result = self._dfs_cycle_detect(neighbor, color, path)
                if result:
                    return result
        
        path.pop()
        color[node] = 2  # 标记为已完成
        return []
    
    def topological_sort(self) -> List[str]:
        """
        拓扑排序（仅当无环时有效）
        返回任务的执行顺序
        """
        has_cycle, _ = self.has_cycle()
        if has_cycle:
            raise ValueError("图中存在环，无法进行拓扑排序")
        
        visited = set()
        order = []
        
        def dfs(node):
            if node in visited:
                return
            visited.add(node)
            for dep in self.graph.get(node, []):
                dfs(dep)
            order.append(node)
        
        for node in self.graph:
            dfs(node)
        
        return order


# 使用示例
graph = TaskDependencyGraph()

# 添加任务依赖
graph.add_task("task_A", ["task_B"])  # A 依赖 B
graph.add_task("task_B", ["task_C"])  # B 依赖 C
graph.add_task("task_C", ["task_A"])  # C 依赖 A → 形成环!

has_cycle, cycle_path = graph.has_cycle()
if has_cycle:
    print(f"检测到环状依赖: {' → '.join(cycle_path)}")
    # 输出: 检测到环状依赖: task_A → task_B → task_C → task_A
```

#### 4.3.2 优缺点

| 优点 | 缺点 |
|------|------|
| 能在任务执行前检测环状依赖 | 仅适用于离散的任务/状态节点 |
| 时间复杂度 O(V+E)，效率高 | 无法检测执行过程中动态形成的循环 |
| 能精确定位环的路径 | 需要明确的依赖关系定义 |

---

## 五、中断机制设计

当检测到循环时，需要有一套完善的中断机制来停止 Agent 并采取恢复措施。

### 5.1 中断机制架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Agent 中断机制架构                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────────┐                                                      │
│   │ 循环检测器   │──── 发现循环 ────┐                                  │
│   └──────────────┘                  │                                   │
│                                     ▼                                   │
│   ┌──────────────┐         ┌─────────────────┐                        │
│   │ 限制检查器   │────────►│   中断决策器    │                        │
│   └──────────────┘ 超限    └────────┬────────┘                        │
│                                      │                                  │
│                    ┌─────────────────┼─────────────────┐              │
│                    ▼                 ▼                 ▼              │
│              ┌──────────┐     ┌──────────┐     ┌──────────┐          │
│              │ 软中断   │     │ 硬中断   │     │ 人工中断 │          │
│              │(Soft)    │     │(Hard)    │     │(Human)   │          │
│              └────┬─────┘     └────┬─────┘     └────┬─────┘          │
│                   │                │                │                 │
│                   ▼                ▼                ▼                 │
│           ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│           │ 注入反思提示 │  │ 立即停止执行 │  │ 暂停并请求   │       │
│           │ 让Agent自我  │  │ 记录当前状态 │  │ 人工干预     │       │
│           │ 纠正         │  │ 触发恢复流程 │  │              │       │
│           └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 三种中断级别

```python
from enum import Enum
from typing import Any, Callable, Optional


class InterruptionLevel(Enum):
    """中断级别"""
    SOFT = "soft"    # 软中断：注入提示，让 Agent 自我纠正
    HARD = "hard"    # 硬中断：立即停止执行
    HUMAN = "human"  # 人工中断：暂停并请求人工干预


@dataclass
class InterruptionContext:
    """中断上下文"""
    level: InterruptionLevel
    reason: str
    detected_loop: Optional[Dict] = None
    exceeded_limit: Optional[LimitConfig] = None
    current_state: Optional[Dict] = None
    timestamp: str = ""


class InterruptionHandler:
    """中断处理器"""
    
    def __init__(self, agent):
        self.agent = agent
        self.interruption_history: List[InterruptionContext] = []
    
    def handle(self, context: InterruptionContext) -> Dict[str, Any]:
        """处理中断"""
        self.interruption_history.append(context)
        
        if context.level == InterruptionLevel.SOFT:
            return self._handle_soft_interruption(context)
        elif context.level == InterruptionLevel.HARD:
            return self._handle_hard_interruption(context)
        elif context.level == InterruptionLevel.HUMAN:
            return self._handle_human_interruption(context)
    
    def _handle_soft_interruption(self, context: InterruptionContext) -> Dict:
        """
        软中断：向 Agent 的上下文注入反思提示
        Agent 有机会自我纠正，继续执行
        """
        reflection_prompt = self._build_reflection_prompt(context)
        
        return {
            "action": "inject_prompt",
            "prompt": reflection_prompt,
            "allow_continue": True,
            "message": f"检测到潜在循环，已注入反思提示: {context.reason}"
        }
    
    def _handle_hard_interruption(self, context: InterruptionContext) -> Dict:
        """
        硬中断：立即停止 Agent 执行
        保存状态，准备恢复
        """
        # 保存当前执行状态
        saved_state = {
            "step": len(self.agent.state_history),
            "state": context.current_state,
            "reason": context.reason,
            "timestamp": context.timestamp,
        }
        
        return {
            "action": "stop_immediately",
            "allow_continue": False,
            "saved_state": saved_state,
            "message": f"执行已被硬中断: {context.reason}"
        }
    
    def _handle_human_interruption(self, context: InterruptionContext) -> Dict:
        """
        人工中断：暂停执行，请求人工干预
        """
        return {
            "action": "pause_and_escalate",
            "allow_continue": False,
            "requires_human": True,
            "context": context,
            "message": (
                f"检测到严重循环，已暂停执行并请求人工干预。\n"
                f"原因: {context.reason}\n"
                f"请审核后决定是否继续执行。"
            )
        }
    
    def _build_reflection_prompt(self, context: InterruptionContext) -> str:
        """构建反思提示"""
        loop_info = context.detected_loop
        
        prompt = f"""
        ⚠️ 系统检测到你可能陷入了循环执行。
        
        检测信息:
        - 原因: {context.reason}
        """
        
        if loop_info:
            prompt += f"""
        - 循环长度: {loop_info.get('cycle_length', '未知')}
        - 重复次数: {loop_info.get('repeat_count', '未知')}
        - 循环状态: {loop_info.get('cycle_states', '未知')}
        """
        
        prompt += """
        
        请反思以下问题:
        1. 你是否在重复执行相同的动作？如果是，为什么？
        2. 之前的尝试为什么失败？是否有根本性的障碍？
        3. 是否有其他完全不同的方法可以达到目标？
        4. 是否应该寻求人工帮助或放弃当前目标？
        
        请制定一个与之前不同的策略，或明确声明无法完成任务。
        """
        
        return prompt
```

### 5.3 中断级别选择策略

```python
class InterruptionPolicy:
    """中断级别选择策略"""
    
    def __init__(self):
        # 软中断阈值：允许 Agent 自我纠正的次数
        self.soft_interruption_limit = 2
        self.soft_interruption_count = 0
    
    def determine_level(self, detection_result: Dict, 
                         limiter: ExecutionLimiter) -> InterruptionLevel:
        """根据检测结果决定中断级别"""
        
        # 1. 如果硬限制超限，直接硬中断
        limit_check = limiter.check_limits()
        if limit_check["exceeded"]:
            return InterruptionLevel.HARD
        
        # 2. 检测到循环
        if detection_result.get("is_in_loop"):
            repeat_count = detection_result.get("repeat_count", 0)
            
            # 循环重复次数少：先尝试软中断
            if self.soft_interruption_count < self.soft_interruption_limit:
                self.soft_interruption_count += 1
                return InterruptionLevel.SOFT
            
            # 软中断后仍然循环：升级为人工中断
            return InterruptionLevel.HUMAN
        
        # 3. 检测到重复动作但未形成循环
        if detection_result.get("is_duplicate"):
            duplicate_count = detection_result.get("similar_count", 0)
            if duplicate_count >= 3:
                return InterruptionLevel.SOFT
        
        # 4. 未检测到问题
        return None
```

---

## 六、异常处理流程

### 6.1 完整异常处理流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  Agent 循环异常处理完整流程                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   [Agent 执行循环]                                                      │
│        │                                                                │
│        ▼                                                                │
│   ┌─────────────┐                                                       │
│   │ 执行一步    │                                                       │
│   └──────┬──────┘                                                       │
│          │                                                              │
│          ▼                                                              │
│   ┌─────────────────────────────────┐                                   │
│   │ 1. 更新状态跟踪器               │                                   │
│   │    记录状态指纹                  │                                   │
│   └──────────────┬──────────────────┘                                   │
│                  │                                                      │
│                  ▼                                                      │
│   ┌─────────────────────────────────┐                                   │
│   │ 2. 运行循环检测                  │                                   │
│   │    • 重复动作检测                │                                   │
│   │    • 序列循环检测                │                                   │
│   └──────────────┬──────────────────┘                                   │
│                  │                                                      │
│          ┌───────┴───────┐                                              │
│          ▼               ▼                                              │
│     [未检测到]      [检测到循环]                                        │
│          │               │                                              │
│          │               ▼                                              │
│          │      ┌─────────────────────┐                                 │
│          │      │ 3. 确定中断级别      │                                 │
│          │      │    (软/硬/人工)      │                                 │
│          │      └──────────┬──────────┘                                 │
│          │                 │                                            │
│          │         ┌───────┴───────┐───────────┐                        │
│          │         ▼               ▼           ▼                        │
│          │    [软中断]         [硬中断]     [人工中断]                  │
│          │         │               │           │                        │
│          │         ▼               ▼           ▼                        │
│          │   ┌──────────┐   ┌──────────┐  ┌──────────┐                 │
│          │   │注入反思  │   │保存状态  │  │暂停执行  │                 │
│          │   │提示      │   │停止循环  │  │通知人工  │                 │
│          │   └────┬─────┘   └────┬─────┘  └────┬─────┘                 │
│          │        │              │              │                        │
│          │        ▼              ▼              ▼                        │
│          │   ┌──────────┐   ┌──────────┐  ┌──────────┐                 │
│          │   │Agent 自我│   │触发恢复  │  │等待人工  │                 │
│          │   │纠正      │   │流程      │  │指令      │                 │
│          │   └────┬─────┘   └────┬─────┘  └────┬─────┘                 │
│          │        │              │              │                        │
│          │        ▼              ▼              ▼                        │
│          │   ┌──────────┐   ┌──────────────────────┐                   │
│          │   │继续执行  │   │ 4. 异常分类与记录    │                   │
│          │   │(下一轮)  │   │    • 记录循环原因    │                   │
│          │   └────┬─────┘   │    • 更新经验库      │                   │
│          │        │         │    • 优化检测策略    │                   │
│          │        │         └──────────────────────┘                   │
│          ▼        ▼                                                    │
│   ┌─────────────────┐                                                  │
│   │ 5. 检查终止条件  │                                                  │
│   └────────┬────────┘                                                  │
│            │                                                            │
│     ┌──────┴──────┐                                                    │
│     ▼             ▼                                                    │
│  [已完成]      [未完成]                                                │
│     │             │                                                    │
│     ▼             └──────► [返回执行下一步]                            │
│   [任务结束]                                                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.2 异常分类与处理

```python
from enum import Enum


class LoopExceptionType(Enum):
    """循环异常类型"""
    EXACT_DUPLICATE = "exact_duplicate"           # 完全重复的动作
    SIMILAR_DUPLICATE = "similar_duplicate"       # 高度相似的动作
    SEQUENCE_LOOP = "sequence_loop"               # 序列循环
    DEPENDENCY_CYCLE = "dependency_cycle"         # 依赖环
    GOAL_NOT_CONVERGING = "goal_not_converging"  # 目标未收敛
    RESOURCE_EXHAUSTED = "resource_exhausted"     # 资源耗尽


@dataclass
class LoopException:
    """循环异常"""
    type: LoopExceptionType
    message: str
    detected_at_step: int
    context: Dict
    suggested_action: str = ""


class LoopExceptionHandler:
    """循环异常处理器"""
    
    def __init__(self):
        self.exception_history: List[LoopException] = []
        self.recovery_strategies = {
            LoopExceptionType.EXACT_DUPLICATE: self._recover_exact_duplicate,
            LoopExceptionType.SIMILAR_DUPLICATE: self._recover_similar_duplicate,
            LoopExceptionType.SEQUENCE_LOOP: self._recover_sequence_loop,
            LoopExceptionType.DEPENDENCY_CYCLE: self._recover_dependency_cycle,
            LoopExceptionType.GOAL_NOT_CONVERGING: self._recover_non_converging,
            LoopExceptionType.RESOURCE_EXHAUSTED: self._recover_resource_exhausted,
        }
    
    def handle(self, exception: LoopException) -> Dict[str, Any]:
        """处理循环异常"""
        self.exception_history.append(exception)
        
        strategy = self.recovery_strategies.get(exception.type)
        if strategy:
            return strategy(exception)
        else:
            return self._default_recovery(exception)
    
    def _recover_exact_duplicate(self, exc: LoopException) -> Dict:
        """恢复策略：完全重复的动作"""
        return {
            "strategy": "skip_and_alternative",
            "description": "跳过重复动作，要求 Agent 寻找替代方案",
            "action": "inject_prompt",
            "prompt": (
                "你已经执行过完全相同的动作并得到了相同的结果。"
                "请不要重复这个动作，而是尝试一种完全不同的方法。"
            ),
            "should_continue": True
        }
    
    def _recover_sequence_loop(self, exc: LoopException) -> Dict:
        """恢复策略：序列循环"""
        cycle_info = exc.context.get("cycle_states", [])
        return {
            "strategy": "break_cycle",
            "description": "打破循环，要求 Agent 跳出当前模式",
            "action": "inject_prompt",
            "prompt": (
                f"你正在重复以下动作序列: {cycle_info}。"
                f"这个循环无法达成目标。请停下来，重新思考整体策略，"
                f"考虑是否需要：\n"
                f"1. 修改目标分解方式\n"
                f"2. 使用不同的工具组合\n"
                f"3. 寻求人工帮助"
            ),
            "should_continue": True
        }
    
    def _recover_dependency_cycle(self, exc: LoopException) -> Dict:
        """恢复策略：依赖环"""
        cycle_path = exc.context.get("cycle_path", [])
        return {
            "strategy": "break_dependency",
            "description": "打破依赖环，重新分解任务",
            "action": "replan",
            "prompt": (
                f"检测到任务间存在环状依赖: {' → '.join(cycle_path)}。\n"
                f"无法按当前依赖关系执行。请重新分解任务，"
                f"消除环状依赖。建议：\n"
                f"1. 合并有循环依赖的任务为一个原子任务\n"
                f"2. 引入外部信息打破循环\n"
                f"3. 重新定义任务边界"
            ),
            "should_continue": True
        }
    
    def _recover_non_converging(self, exc: LoopException) -> Dict:
        """恢复策略：目标未收敛"""
        return {
            "strategy": "relax_criteria",
            "description": "放宽终止条件或调整目标",
            "action": "adjust_goal",
            "options": [
                "放宽终止条件的严格度",
                "将目标分解为更小的可达成子目标",
                "请求用户确认是否接受当前结果",
            ],
            "should_continue": True
        }
    
    def _recover_resource_exhausted(self, exc: LoopException) -> Dict:
        """恢复策略：资源耗尽"""
        return {
            "strategy": "graceful_termination",
            "description": "优雅终止，保存已完成的进度",
            "action": "stop_and_save",
            "should_continue": False,
            "message": "资源已耗尽，任务被终止。已保存当前进度。"
        }
    
    def _default_recovery(self, exc: LoopException) -> Dict:
        """默认恢复策略"""
        return {
            "strategy": "escalate",
            "description": "升级为人工处理",
            "action": "human_escalation",
            "should_continue": False,
            "message": f"检测到未知类型的循环异常: {exc.type.value}"
        }
```

---

## 七、完整工程实现

将上述所有机制整合为一个完整的循环防护系统。

```python
"""
Agent 循环防护系统完整实现
整合：状态跟踪、循环检测、中断机制、异常处理
"""

import time
from typing import Any, Dict, List, Optional


class LoopGuardSystem:
    """
    Agent 循环防护系统
    作为 Agent 执行循环的"护栏"，防止无限循环
    """
    
    def __init__(self, config: Optional[Dict] = None):
        config = config or {}
        
        # 核心组件
        self.state_tracker = StateTracker()
        self.duplicate_detector = DuplicateActionDetector(
            similarity_threshold=config.get("similarity_threshold", 0.85),
            lookback_window=config.get("lookback_window", 10)
        )
        self.sequence_detector = SequenceLoopDetector(
            min_cycle_length=config.get("min_cycle_length", 2),
            min_repeat_count=config.get("min_repeat_count", 2)
        )
        self.limiter = ExecutionLimiter()
        self.interruption_handler = InterruptionHandler(self)
        self.interruption_policy = InterruptionPolicy()
        self.exception_handler = LoopExceptionHandler()
        
        # 终止条件
        self.termination_criterion: Optional[TerminationCriterion] = None
        
        # 统计信息
        self.stats = {
            "total_steps": 0,
            "loops_detected": 0,
            "interruptions": 0,
            "recoveries_successful": 0,
        }
    
    def set_termination_criterion(self, criterion: TerminationCriterion):
        """设置终止条件"""
        self.termination_criterion = criterion
    
    def pre_step_check(self, action_name: str, 
                        action_params: Dict) -> Dict[str, Any]:
        """
        执行前的检查（在 Agent 决定动作后、实际执行前调用）
        返回: {should_proceed: bool, intervention: Optional[Dict]}
        """
        self.stats["total_steps"] += 1
        
        # 1. 检查执行限制
        self.limiter.increment(LimitType.TOTAL_STEPS)
        limit_check = self.limiter.check_limits()
        if limit_check["exceeded"]:
            return {
                "should_proceed": False,
                "intervention": {
                    "level": "hard",
                    "reason": limit_check["stop_reason"],
                    "action": "stop_immediately"
                }
            }
        
        # 2. 重复动作检测
        dup_result = self.duplicate_detector.check(action_name, action_params)
        
        # 3. 状态序列循环检测
        temp_fingerprint = f"{action_name}:{hash(str(action_params))}"
        self.sequence_detector.add_state(temp_fingerprint)
        loop_result = self.sequence_detector.detect_loop()
        
        # 4. 综合判断是否需要中断
        detection_result = {
            "is_duplicate": dup_result["is_duplicate"],
            "similar_count": dup_result["similar_count"],
            "is_in_loop": loop_result is not None,
            "repeat_count": loop_result["repeat_count"] if loop_result else 0,
            "loop_info": loop_result,
        }
        
        if detection_result["is_in_loop"] or detection_result["is_duplicate"]:
            self.stats["loops_detected"] += 1
            
            # 确定中断级别
            level = self.interruption_policy.determine_level(
                detection_result, self.limiter
            )
            
            if level:
                self.stats["interruptions"] += 1
                
                # 构建中断上下文
                context = InterruptionContext(
                    level=level,
                    reason=self._build_reason(detection_result, limit_check),
                    detected_loop=loop_result,
                    exceeded_limit=limit_check,
                    current_state={"step": self.stats["total_steps"]}
                )
                
                # 处理中断
                intervention = self.interruption_handler.handle(context)
                
                # 如果是软中断，允许继续但注入提示
                if intervention.get("allow_continue"):
                    return {
                        "should_proceed": True,
                        "intervention": intervention,
                        "inject_prompt": intervention.get("prompt")
                    }
                else:
                    return {
                        "should_proceed": False,
                        "intervention": intervention
                    }
        
        return {"should_proceed": True, "intervention": None}
    
    def post_step_check(self, action_name: str, action_params: Dict,
                         observation: str, goal_progress: float) -> Dict:
        """
        执行后的检查（在动作执行完毕后调用）
        返回: {task_completed: bool, should_continue: bool}
        """
        # 1. 记录状态
        state = ExecutionState(
            step=self.stats["total_steps"],
            action_name=action_name,
            action_params=action_params,
            observation_summary=observation[:200],  # 截断观察结果
            goal_progress=goal_progress
        )
        self.state_tracker.record(state)
        
        # 2. 检查终止条件
        if self.termination_criterion:
            current_state = {
                "step": self.stats["total_steps"],
                "observation": observation,
                "progress": goal_progress,
            }
            
            if self.termination_criterion.is_satisfied(
                current_state, 
                self.state_tracker.state_history
            ):
                return {
                    "task_completed": True,
                    "should_continue": False,
                    "reason": "终止条件已满足"
                }
        
        # 3. 检查目标进度是否停滞
        if self._is_progress_stagnant():
            exception = LoopException(
                type=LoopExceptionType.GOAL_NOT_CONVERGING,
                message="目标进度连续多步无增长",
                detected_at_step=self.stats["total_steps"],
                context={"recent_progress": self._get_recent_progress()}
            )
            recovery = self.exception_handler.handle(exception)
            if not recovery.get("should_continue", True):
                return {
                    "task_completed": False,
                    "should_continue": False,
                    "intervention": recovery
                }
        
        return {"task_completed": False, "should_continue": True}
    
    def _is_progress_stagnant(self, window: int = 5, 
                               threshold: float = 0.01) -> bool:
        """检查目标进度是否停滞"""
        recent = self.state_tracker.get_recent_actions(window)
        if len(recent) < window:
            return False
        
        progress_values = [s.goal_progress for s in recent]
        progress_change = max(progress_values) - min(progress_values)
        return progress_change < threshold
    
    def _get_recent_progress(self) -> List[float]:
        """获取最近的进度值"""
        return [s.goal_progress for s in 
                self.state_tracker.get_recent_actions(10)]
    
    def _build_reason(self, detection: Dict, limit: Dict) -> str:
        """构建中断原因描述"""
        reasons = []
        if detection.get("is_in_loop"):
            reasons.append(
                f"检测到序列循环 (重复 {detection['repeat_count']} 次)"
            )
        if detection.get("is_duplicate"):
            reasons.append(
                f"检测到重复动作 (相似 {detection['similar_count']} 次)"
            )
        if limit.get("warnings"):
            reasons.extend(limit["warnings"])
        return "; ".join(reasons) if reasons else "未知原因"
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            "limiter_status": {
                lt.value: {
                    "current": config.current_value,
                    "max": config.max_value,
                    "usage": f"{config.usage_ratio:.0%}"
                }
                for lt, config in self.limiter.limits.items()
            }
        }


# ============================================================
# 使用示例：将 LoopGuard 集成到 Agent 执行循环
# ============================================================

class GuardedAgent:
    """带有循环防护的 Agent"""
    
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        self.guard = LoopGuardSystem(config={
            "similarity_threshold": 0.85,
            "min_cycle_length": 2,
            "min_repeat_count": 2,
        })
    
    async def run(self, goal: str) -> Dict:
        """执行任务（带循环防护）"""
        
        # 设置终止条件
        self.guard.set_termination_criterion(
            GoalAchievedCriterion(goal, self.llm)
        )
        
        history = []
        
        for iteration in range(100):  # 最大 100 轮
            # 1. LLM 决策
            action = await self.llm.decide_action(goal, history)
            
            # 2. 执行前检查
            pre_check = self.guard.pre_step_check(
                action.name, action.params
            )
            
            if not pre_check["should_proceed"]:
                # 被中断
                intervention = pre_check["intervention"]
                if intervention.get("action") == "stop_immediately":
                    return {
                        "success": False,
                        "reason": intervention["message"],
                        "stats": self.guard.get_stats()
                    }
            
            # 如果有注入的提示，加入历史
            injected_prompt = pre_check.get("inject_prompt")
            if injected_prompt:
                history.append({"role": "system", "content": injected_prompt})
            
            # 3. 执行动作
            try:
                observation = await self.tools.execute(
                    action.name, action.params
                )
            except Exception as e:
                observation = f"Error: {str(e)}"
            
            # 4. 评估进度
            progress = await self._evaluate_progress(goal, observation)
            
            # 5. 执行后检查
            post_check = self.guard.post_step_check(
                action.name, action.params,
                str(observation), progress
            )
            
            if post_check["task_completed"]:
                return {
                    "success": True,
                    "result": observation,
                    "stats": self.guard.get_stats()
                }
            
            if not post_check.get("should_continue", True):
                intervention = post_check.get("intervention", {})
                return {
                    "success": False,
                    "reason": intervention.get("message", "任务终止"),
                    "stats": self.guard.get_stats()
                }
            
            # 6. 记录历史，继续下一轮
            history.append({
                "step": iteration,
                "action": action,
                "observation": observation,
                "progress": progress
            })
        
        return {
            "success": False,
            "reason": "达到最大迭代次数",
            "stats": self.guard.get_stats()
        }
    
    async def _evaluate_progress(self, goal, observation) -> float:
        """评估目标完成进度 (0-1)"""
        # 实际实现中可以使用 LLM 或启发式方法
        return 0.5  # 简化示例
```

---

## 八、案例分析与实践指南

### 8.1 案例一：编程 Agent 的“修复-破坏”循环

**问题描述**：一个编程 Agent 在修复 Bug 时，反复在两个状态间震荡——修复了 Bug A 但引入了 Bug B，修复 Bug B 又导致 Bug A 复现。

**解决方案**：

```python
# 1. 使用状态序列检测器识别震荡
detector = SequenceLoopDetector(min_cycle_length=2, min_repeat_count=2)

# 2. 当检测到震荡时，注入"全局视角"提示
recovery_prompt = """
你正在以下状态间震荡:
  状态 1: 修复了 Bug A，但引入了 Bug B
  状态 2: 修复了 Bug B，但 Bug A 复现

这表明两个 Bug 可能存在关联。请:
1. 分析两个 Bug 的根本原因是否相同
2. 寻找一个能同时解决两个 Bug 的方案
3. 如果无法同时解决，请说明权衡并寻求人工建议
"""

# 3. 记录已尝试的方案，避免重复
attempted_solutions = set()
def should_try_solution(solution_hash):
    if solution_hash in attempted_solutions:
        return False  # 已尝试过，不再重复
    attempted_solutions.add(solution_hash)
    return True
```

**效果**：Agent 能在 2-3 次震荡后被检测到，并通过反思提示找到根本原因，或寻求人工帮助。

### 8.2 案例二：数据查询 Agent 的盲目重试

**问题描述**：Agent 查询数据库失败后，不分析原因直接重试，消耗大量 Token。

**解决方案**：

```python
# 使用重复动作检测器 + 错误分类
class SmartRetryHandler:
    def __init__(self):
        self.detector = DuplicateActionDetector()
        self.error_classifier = ErrorClassifier()
    
    def should_retry(self, action, error):
        # 1. 检查是否重复
        dup_result = self.detector.check(action.name, action.params)
        if dup_result["is_duplicate"]:
            return False, "动作已重复，不再重试"
        
        # 2. 分类错误
        error_type = self.error_classifier.classify(error)
        
        # 3. 根据错误类型决定是否重试
        retryable_types = ["timeout", "rate_limit", "temporary_unavailable"]
        if error_type in retryable_types:
            return True, f"错误类型 {error_type} 可重试"
        else:
            return False, f"错误类型 {error_type} 不可重试，需改变策略"
```

### 8.3 实践指南：如何为你的 Agent 配置循环防护

| Agent 类型 | 推荐配置 | 关键参数 |
|-----------|---------|---------|
| **编程 Agent** | 序列检测 + 进度停滞检测 | `min_cycle_length=2`, `stagnation_window=5` |
| **数据分析 Agent** | 重复动作检测 + Token 限制 | `similarity_threshold=0.90`, `max_tokens=200000` |
| **客服 Agent** | 步数限制 + 时间限制 | `max_steps=15`, `max_time=60s` |
| **研究 Agent** | 序列检测 + 人工中断升级 | `min_cycle_length=3`, `soft_limit=3` |
| **多 Agent 系统** | 依赖图环检测 + 全局步数限制 | DAG 验证 + `max_total_steps=200` |

---

## 九、总结与最佳实践

### 9.1 核心要点速记

| 维度 | 核心策略 | 关键技术 |
|------|---------|---------|
| **前置预防** | 任务依赖无环验证、明确终止条件 | DAG 拓扑排序、终止条件定义 |
| **过程监控** | 状态跟踪、执行限制、循环检测 | 状态指纹、多维度限制器、序列模式匹配 |
| **中断机制** | 软中断→硬中断→人工中断的分级响应 | 反思提示注入、状态保存、人工升级 |
| **异常处理** | 分类处理不同类型的循环异常 | 错误分类器、恢复策略库 |
| **学习改进** | 从循环中学习，优化检测策略 | 经验记录、策略更新 |

### 9.2 最佳实践清单

1.  **✅ 始终设置执行限制**：作为最后防线，确保即使其他检测失效，系统也不会无限运行。
2.  **✅ 定义明确的终止条件**：在每个任务开始前，明确“什么情况算完成”。
3.  **✅ 使用多层检测**：不要依赖单一检测算法，组合使用重复检测、序列检测和进度检测。
4.  **✅ 分级中断**：先软中断给 Agent 自我纠正的机会，再升级为硬中断或人工中断。
5.  **✅ 记录和分析循环原因**：将每次循环事件记录下来，用于优化检测策略和 Agent Prompt。
6.  **✅ 在 Prompt 中告知 Agent 循环防护机制**：让 Agent 知道系统会检测循环，鼓励它主动避免重复。
7.  **✅ 对多 Agent 系统进行依赖图验证**：在任务分解后、执行前，验证依赖关系无环。
8.  **❌ 不要仅依赖步数限制**：步数限制是兜底，不能作为主要的循环检测手段。
9.  **❌ 不要忽视软中断的价值**：很多时候，Agent 只需要一个“反思提示”就能跳出循环。

### 9.3 与已有文档的关联

*   [10Agent技术挑战与未来展望](file:///m:/note-book/agent/1基础概念/10Agent技术挑战与未来展望.md)：本文是对该文档中“死循环与无限重试”挑战的系统性解决方案。
*   [12Agent自主决策机制深度解析](file:///m:/note-book/agent/1基础概念/12Agent自主决策机制深度解析.md)：本文的 `AdaptiveFaultHandler` 是对该文档中容错机制的扩展和深化。
*   [3Agent核心组成模块详解](file:///m:/note-book/agent/1基础概念/3Agent核心组成模块详解.md)：本文的循环防护系统是 Agent 执行引擎的重要补充组件。

> **最终建议**：循环防护不是可选项，而是生产级 Agent 系统的**必备组件**。一个没有循环防护的 Agent 系统，就像一辆没有刹车的汽车——动力越强，危险越大。通过本文介绍的多层防护策略，可以显著提升 Agent 系统的稳定性和可靠性，使其能够安全地在生产环境中运行。
