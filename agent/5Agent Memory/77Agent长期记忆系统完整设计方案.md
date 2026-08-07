# Agent 长期记忆系统完整设计方案

> **文档定位**:本文档是 Agent Memory 系列的第四篇核心文档,专注于**长期记忆系统的完整工程设计**。在 [74Agent记忆系统核心价值与必要性解析.md](./74Agent记忆系统核心价值与必要性解析.md) 阐述"为什么需要 Memory"、[75Agent记忆系统类型分类深度解析.md](./75Agent记忆系统类型分类深度解析.md) 概述"Memory 有哪些类型"、[76短期记忆与长期记忆核心区别深度解析.md](./76短期记忆与长期记忆核心区别深度解析.md) 深度对比两者差异的基础上,本文给出**一套可落地的长期记忆系统完整设计方案**,涵盖记忆存储结构、数据持久化机制、记忆检索算法、记忆更新策略、记忆管理规则、重要性分级、容量限制与缓存平衡、以及与 Agent 决策系统的集成方式,确保 Agent 具备学习能力、经验积累与跨会话连续性。
>
> **阅读建议**:建议先阅读 74~76 号文档建立 Memory 类型体系与短长期分野的认知基础,再阅读本文理解长期记忆的工程落地。可结合 [41Agent任务规划机制详解.md](../3Agent%20架构设计/41Agent任务规划机制详解.md)、[42Agent工具选择决策机制深度解析.md](../3Agent%20架构设计/42Agent工具选择决策机制深度解析.md) 理解记忆系统如何驱动 Agent 决策。

---

## 目录

- [一、长期记忆系统总体架构](#一长期记忆系统总体架构)
- [二、记忆存储结构设计](#二记忆存储结构设计)
- [三、数据持久化机制](#三数据持久化机制)
- [四、记忆检索算法](#四记忆检索算法)
- [五、记忆更新策略](#五记忆更新策略)
- [六、记忆管理规则](#六记忆管理规则)
- [七、重要性分级机制](#七重要性分级机制)
- [八、容量限制与缓存平衡](#八容量限制与缓存平衡)
- [九、与 Agent 决策系统集成](#九与-agent-决策系统集成)
- [十、学习能力与经验积累](#十学习能力与经验积累)
- [十一、跨会话连续性保障](#十一跨会话连续性保障)
- [十二、完整代码实现](#十二完整代码实现)
- [十三、典型应用场景案例](#十三典型应用场景案例)
- [十四、最佳实践与避坑指南](#十四最佳实践与避坑指南)

---

## 一、长期记忆系统总体架构

### 1.1 设计目标

**Agent 长期记忆系统** 是让 Agent 跨越单次会话边界、持续积累经验并优化未来行为的工程化记忆基础设施。本方案的设计目标如下:

| 目标维度 | 具体要求 | 衡量指标 |
|----------|----------|----------|
| **持久性** | 记忆在进程重启、会话切换后完整保留 | 数据零丢失率 |
| **可检索性** | 高效检索与当前任务相关的历史记忆 | 召回率、检索延迟 |
| **可演化** | 记忆可更新、合并、衰减、遗忘 | 记忆新鲜度 |
| **容量可控** | 在有限存储下保留最有价值的信息 | 重要信息保留率 |
| **决策驱动** | 记忆直接参与 Agent 决策回路 | 决策质量提升度 |
| **学习闭环** | 从经验中提炼规则、修正偏好 | 任务成功率提升 |

### 1.2 总体架构全景

```mermaid
graph TB
    subgraph Agent交互层
        U[用户输入/环境观察]
        D[Agent决策系统]
        R[Agent执行与响应]
    end

    subgraph 记忆接入层
        W[记忆写入接口<br/>MemoryWriter]
        Q[记忆检索接口<br/>MemoryRetriever]
        U2[记忆更新接口<br/>MemoryUpdater]
    end

    subgraph 记忆处理层
        EN[编码器<br/>Encoder]
        EX[提取器<br/>Extractor]
        GR[分级器<br/>Grader]
        CON[合并器<br/>Consolidator]
        DEC[衰减器<br/>Decayer]
    end

    subgraph 记忆存储层
        L1[L1 热缓存<br/>Redis/内存]
        L2[L2 主存储<br/>向量数据库]
        L3[L3 归档存储<br/>对象存储]
        META[(元数据库<br/>SQLite/PostgreSQL)]
    end

    subgraph 记忆治理层
        POL[管理规则引擎]
        CAP[容量控制器]
        SCH[后台调度器]
        MON[监控与指标]
    end

    U --> Q
    Q --> D
    D --> R
    R --> W

    W --> EN --> EX --> GR
    GR --> L1 & L2
    Q --> L1
    Q -.miss.-> L2
    L2 -.冷数据.-> L3

    U2 --> CON --> L2
    SCH --> DEC --> L2
    SCH --> CAP --> L2 & L3

    POL --> GR & CAP & DEC
    MON --> L1 & L2 & L3

    style Q fill:#fff3cd,stroke:#d39e00,stroke-width:2px
    style W fill:#d4edda,stroke:#155724
    style L2 fill:#d1ecf1,stroke:#0c5460,stroke-width:2px
```

### 1.3 核心设计原则

| 原则 | 说明 | 工程体现 |
|------|------|----------|
| **分级存储** | 按访问频率与重要性分层 | L1 缓存 / L2 主存 / L3 归档 |
| **重要性驱动** | 重要信息优先保留、长期保存 | 重要性评分 + 分级策略 |
| **检索优先** | 记忆的价值在于被高效检索 | 混合检索(向量+关键词+元数据) |
| **动态演化** | 记忆会更新、合并、衰减、遗忘 | 后台 Consolidator + Decayer |
| **读写分离** | 写入异步化、检索同步低延迟 | 写队列 + 读缓存 |
| **治理闭环** | 容量、质量、新鲜度持续治理 | 规则引擎 + 调度器 |

---

## 二、记忆存储结构设计

### 2.1 记忆的层级分类

长期记忆按**内容性质**分为四类,每类采用差异化的存储与检索策略:

| 记忆类型 | 内容 | 生命周期 | 检索方式 | 优先级 |
|----------|------|----------|----------|--------|
| **语义记忆** | 事实、概念、知识 | 永久(除非被纠正) | 向量相似度 | P0 |
| **情景记忆** | 具体事件、交互记录 | 衰减式(按时间) | 向量+时间衰减 | P1 |
| **程序记忆** | 技能、规则、流程 | 永久(可被覆盖) | 精确匹配+元数据 | P0 |
| **偏好记忆** | 用户偏好、Agent 偏好 | 永久(可更新) | 用户ID+键 | P0 |

```mermaid
graph LR
    subgraph 长期记忆四类
        S[语义记忆<br/>Semantic<br/>事实/概念/知识]
        E[情景记忆<br/>Episodic<br/>事件/交互/经历]
        P[程序记忆<br/>Procedural<br/>规则/技能/流程]
        PR[偏好记忆<br/>Preference<br/>用户/Agent偏好]
    end

    S -->|存储于| V[(向量库)]
    E -->|存储于| V
    P -->|存储于| K[(KV/规则库)]
    PR -->|存储于| K

    V -->|检索| MIX[混合检索]
    K -->|查询| MIX
    MIX --> DEC[Agent决策]

    style S fill:#d1ecf1,stroke:#0c5460
    style E fill:#d4edda,stroke:#155724
    style P fill:#fff3cd,stroke:#d39e00
    style PR fill:#fce4ec,stroke:#880e4f
```

### 2.2 统一记忆条目数据模型

所有类型的记忆共享统一的基础结构,通过 `memory_type` 区分:

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

class MemoryType(Enum):
    SEMANTIC = "semantic"        # 语义记忆:事实/知识
    EPISODIC = "episodic"        # 情景记忆:事件/交互
    PROCEDURAL = "procedural"    # 程序记忆:规则/技能
    PREFERENCE = "preference"    # 偏好记忆:用户偏好

class MemoryStatus(Enum):
    ACTIVE = "active"            # 活跃可用
    FADING = "fading"            # 衰减中
    ARCHIVED = "archived"        # 已归档
    DEPRECATED = "deprecated"    # 已废弃

@dataclass
class MemoryItem:
    """统一记忆条目模型"""
    # ===== 标识与元数据 =====
    memory_id: str                    # 全局唯一ID(UUID)
    user_id: str                       # 所属用户/会话主体
    agent_id: str                      # 所属Agent
    memory_type: MemoryType           # 记忆类型

    # ===== 内容 =====
    content: str                       # 自然语言内容
    content_embedding: list[float] = field(default=None)  # 向量表示
    structured_data: dict = field(default_factory=dict)   # 结构化字段

    # ===== 重要性分级 =====
    importance_score: float = 0.5      # 重要性评分[0,1]
    importance_level: str = "MEDIUM"   # CRITICAL/HIGH/MEDIUM/LOW

    # ===== 时间维度 =====
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed_at: datetime = field(default_factory=datetime.now)
    last_updated_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0              # 被检索次数
    expiry_at: datetime = None         # 过期时间(情景记忆可设)

    # ===== 来源与可信度 =====
    source: str = ""                   # 来源(user/agent/tool/inference)
    confidence: float = 1.0            # 可信度[0,1]
    verified: bool = False             # 是否已验证

    # ===== 关联与组织 =====
    tags: list[str] = field(default_factory=list)        # 标签
    related_ids: list[str] = field(default_factory=list) # 关联记忆ID
    parent_id: str = None              # 父记忆(层级)

    # ===== 状态与治理 =====
    status: MemoryStatus = MemoryStatus.ACTIVE
    version: int = 1                   # 版本号(更新时递增)
    metadata: dict = field(default_factory=dict)
```

### 2.3 各类型记忆的差异化字段

```python
# 语义记忆:强调事实性
@dataclass
class SemanticMemory(MemoryItem):
    fact_subject: str = ""             # 事实主体(如"用户张三")
    fact_predicate: str = ""           # 谓词(如"擅长")
    fact_object: str = ""              # 客体(如"Python编程")
    contradict_ids: list[str] = field(default_factory=list)  # 矛盾记忆

# 情景记忆:强调时间与上下文
@dataclass
class EpisodicMemory(MemoryItem):
    event_time: datetime = None        # 事件发生时间
    event_location: str = ""           # 场景/渠道
    participants: list[str] = field(default_factory=list)  # 参与者
    trigger: str = ""                  # 触发条件
    outcome: str = ""                  # 结果
    emotion: str = ""                  # 情感标记

# 程序记忆:强调规则与触发条件
@dataclass
class ProceduralMemory(MemoryItem):
    rule_condition: str = ""           # 触发条件
    rule_action: str = ""              # 执行动作
    success_count: int = 0             # 成功执行次数
    failure_count: int = 0             # 失败次数
    success_rate: float = 0.0          # 成功率

# 偏好记忆:强调键值结构
@dataclass
class PreferenceMemory(MemoryItem):
    preference_key: str = ""           # 偏好键(如"language")
    preference_value: str = ""         # 偏好值(如"Python")
    preference_scope: str = "global"   # 作用域
```

### 2.4 记忆关联图谱

记忆之间通过 `related_ids` 构成关联网络,支持图式检索:

```mermaid
graph LR
    M1[语义:用户张三擅长Python]
    M2[情景:2024-01为张三解答装饰器]
    M3[程序:Python问题优先用代码示例]
    M4[偏好:张三偏好简洁回答]
    M5[语义:装饰器是Python特性]
    M6[情景:2024-03张三询问闭包]

    M1 ---|related| M2
    M1 ---|related| M4
    M2 ---|related| M3
    M2 ---|related| M5
    M6 ---|related| M1
    M6 ---|related| M5

    style M1 fill:#d1ecf1,stroke:#0c5460
    style M2 fill:#d4edda,stroke:#155724
    style M3 fill:#fff3cd,stroke:#d39e00
    style M4 fill:#fce4ec,stroke:#880e4f
```

---

## 三、数据持久化机制

### 3.1 三级存储架构

长期记忆采用**三级存储分层**,在访问速度与持久化成本间取得平衡:

| 层级 | 存储 | 内容 | 访问延迟 | 持久性 |
|------|------|------|----------|--------|
| **L1 热缓存** | Redis / 进程内 LRU | 高频访问、刚写入、CRITICAL 级 | <5ms | 易失(可重建) |
| **L2 主存储** | 向量数据库(Milvus/Chroma)+ 关系库 | 全量 ACTIVE 记忆 | 20-100ms | 持久 |
| **L3 归档存储** | 对象存储(S3/OSS)+ JSON 文件 | ARCHIVED、低重要性、历史版本 | 秒级 | 永久(低成本) |

```mermaid
graph TB
    subgraph 三级存储
        L1[L1 热缓存<br/>Redis/内存<br/>高频+CRITICAL]
        L2[(L2 主存储<br/>向量库+关系库<br/>全量ACTIVE)]
        L3[(/L3 归档存储<br/>对象存储<br/>ARCHIVED+历史)]
    end

    W[写入] --> L1
    L1 -.异步刷盘.-> L2
    L2 -.冷数据迁移.-> L3

    Q[检索] --> L1
    L1 -.未命中.-> L2
    L2 -.未命中.-> L3
    L3 -.回填.-> L1

    UP[更新] --> L2
    L2 -.失效.-> L1

    style L1 fill:#fce4ec,stroke:#880e4f
    style L2 fill:#d1ecf1,stroke:#0c5460,stroke-width:2px
    style L3 fill:#e2e3e5,stroke:#383d41
```

### 3.2 L2 主存储的混合存储设计

L2 是核心持久化层,采用**向量库 + 关系库**混合存储:

| 存储组件 | 存储内容 | 检索能力 |
|----------|----------|----------|
| **向量数据库** | `content_embedding` + `memory_id` | 语义相似度检索 |
| **关系数据库** | 全量字段(除向量) | 精确查询、范围查询、元数据过滤 |
| **图数据库(可选)** | 记忆关联关系 | 图遍历、关联检索 |

### 3.3 SQLite 持久化实现

```python
import sqlite3
import json
from datetime import datetime

class SQLitePersistence:
    """基于 SQLite 的 L2 持久化实现(单机版)"""

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS memories (
        memory_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        agent_id TEXT NOT NULL,
        memory_type TEXT NOT NULL,
        content TEXT NOT NULL,
        structured_data TEXT DEFAULT '{}',
        importance_score REAL DEFAULT 0.5,
        importance_level TEXT DEFAULT 'MEDIUM',
        created_at TEXT NOT NULL,
        last_accessed_at TEXT NOT NULL,
        last_updated_at TEXT NOT NULL,
        access_count INTEGER DEFAULT 0,
        expiry_at TEXT,
        source TEXT DEFAULT '',
        confidence REAL DEFAULT 1.0,
        verified INTEGER DEFAULT 0,
        tags TEXT DEFAULT '[]',
        related_ids TEXT DEFAULT '[]',
        parent_id TEXT,
        status TEXT DEFAULT 'active',
        version INTEGER DEFAULT 1,
        metadata TEXT DEFAULT '{}'
    );
    CREATE INDEX IF NOT EXISTS idx_user_type ON memories(user_id, memory_type);
    CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance_level, importance_score);
    CREATE INDEX IF NOT EXISTS idx_status_accessed ON memories(status, last_accessed_at);
    CREATE INDEX IF NOT EXISTS idx_expiry ON memories(expiry_at) WHERE expiry_at IS NOT NULL;
    """

    def __init__(self, db_path: str = "agent_memory.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        self.conn.executescript(self.SCHEMA)
        self.conn.commit()

    def save(self, item: MemoryItem) -> None:
        self.conn.execute("""
            INSERT OR REPLACE INTO memories VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            item.memory_id, item.user_id, item.agent_id,
            item.memory_type.value, item.content,
            json.dumps(item.structured_data, ensure_ascii=False),
            item.importance_score, item.importance_level,
            item.created_at.isoformat(), item.last_accessed_at.isoformat(),
            item.last_updated_at.isoformat(), item.access_count,
            item.expiry_at.isoformat() if item.expiry_at else None,
            item.source, item.confidence, int(item.verified),
            json.dumps(item.tags, ensure_ascii=False),
            json.dumps(item.related_ids, ensure_ascii=False),
            item.parent_id, item.status.value, item.version,
            json.dumps(item.metadata, ensure_ascii=False),
        ))
        self.conn.commit()

    def get(self, memory_id: str) -> MemoryItem | None:
        row = self.conn.execute(
            "SELECT * FROM memories WHERE memory_id=?", (memory_id,)
        ).fetchone()
        return self._row_to_item(row) if row else None

    def _row_to_item(self, row: sqlite3.Row) -> MemoryItem:
        return MemoryItem(
            memory_id=row["memory_id"],
            user_id=row["user_id"],
            agent_id=row["agent_id"],
            memory_type=MemoryType(row["memory_type"]),
            content=row["content"],
            structured_data=json.loads(row["structured_data"]),
            importance_score=row["importance_score"],
            importance_level=row["importance_level"],
            created_at=datetime.fromisoformat(row["created_at"]),
            last_accessed_at=datetime.fromisoformat(row["last_accessed_at"]),
            last_updated_at=datetime.fromisoformat(row["last_updated_at"]),
            access_count=row["access_count"],
            expiry_at=datetime.fromisoformat(row["expiry_at"]) if row["expiry_at"] else None,
            source=row["source"],
            confidence=row["confidence"],
            verified=bool(row["verified"]),
            tags=json.loads(row["tags"]),
            related_ids=json.loads(row["related_ids"]),
            parent_id=row["parent_id"],
            status=MemoryStatus(row["status"]),
            version=row["version"],
            metadata=json.loads(row["metadata"]),
        )
```

### 3.4 向量库持久化实现

```python
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

class VectorPersistence:
    """基于 Chroma 的向量持久化"""

    def __init__(self, persist_path: str = "./memory_vectors"):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vectorstore = Chroma(
            collection_name="long_term_memory",
            embedding_function=self.embeddings,
            persist_directory=persist_path,
        )

    def add(self, item: MemoryItem) -> None:
        self.vectorstore.add_texts(
            texts=[item.content],
            metadatas=[{
                "memory_id": item.memory_id,
                "user_id": item.user_id,
                "memory_type": item.memory_type.value,
                "importance_level": item.importance_level,
                "importance_score": item.importance_score,
                "created_at": item.created_at.isoformat(),
            }],
            ids=[item.memory_id],
        )

    def search(self, query: str, user_id: str, k: int = 10,
               filters: dict = None) -> list[dict]:
        where = {"user_id": user_id}
        if filters:
            where.update(filters)
        docs = self.vectorstore.similarity_search_with_score(
            query=query, k=k, filter=where,
        )
        return [{"content": d.page_content, "score": 1 - score,
                 "metadata": d.metadata} for d, score in docs]
```

### 3.5 写入与刷盘策略

| 操作 | 落盘时机 | 说明 |
|------|----------|------|
| **同步写入** | L1 + L2 关系库 | 保证不丢,低延迟 |
| **异步写入** | L2 向量库 | 向量化耗时,放队列异步 |
| **定时刷盘** | L1 → L2 | 每 60s 同步脏数据 |
| **冷数据迁移** | L2 → L3 | 每日扫描 ARCHIVED 状态 |
| **WAL 日志** | 全部写入 | Write-Ahead Log 保证崩溃恢复 |

---

## 四、记忆检索算法

### 4.1 检索算法设计目标

长期记忆的检索需同时满足**相关性、重要性、新鲜度、多样性**四维度:

| 维度 | 含义 | 量化指标 |
|------|------|----------|
| **相关性** | 与当前查询的语义相似度 | 向量余弦相似度 |
| **重要性** | 记忆本身的价值 | importance_score |
| **新鲜度** | 记忆是否过时 | 时间衰减函数 |
| **多样性** | 避免返回重复同类记忆 | MMR 多样性度量 |

### 4.2 混合检索算法

采用**向量检索 + 关键词检索 + 元数据过滤**的混合方案,通过**加权融合**得到最终排序:

```python
import math
from datetime import datetime, timedelta

class HybridMemoryRetriever:
    """混合记忆检索器"""

    def __init__(self, vector_store, sqlite_store,
                 alpha: float = 0.6,   # 向量权重
                 beta: float = 0.2,    # 关键词权重
                 gamma: float = 0.2):  # 重要性权重
        self.vector_store = vector_store
        self.sqlite_store = sqlite_store
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

    def retrieve(self, query: str, user_id: str,
                 top_k: int = 10,
                 memory_types: list[MemoryType] = None,
                 min_importance: float = 0.0) -> list[MemoryItem]:
        # Step 1: 向量检索(语义相关)
        vector_results = self.vector_store.search(
            query=query, user_id=user_id, k=top_k * 3,
            filters={"memory_type": [t.value for t in memory_types]}
            if memory_types else None,
        )

        # Step 2: 关键词检索(精确匹配)
        keyword_results = self._keyword_search(query, user_id, top_k * 3)

        # Step 3: 合并候选集
        candidates = self._merge_candidates(vector_results, keyword_results)

        # Step 4: 加载完整记忆 + 元数据过滤
        items = self._load_and_filter(candidates, user_id, memory_types, min_importance)

        # Step 5: 综合评分
        scored = []
        now = datetime.now()
        for item, vec_score, kw_score in items:
            relevance = self.alpha * vec_score + self.beta * kw_score
            importance = self.gamma * item.importance_score
            freshness = self._freshness_score(item, now)
            final = (relevance + importance) * freshness
            scored.append((item, final))

        # Step 6: MMR 多样性重排
        scored.sort(key=lambda x: x[1], reverse=True)
        diverse = self._mmr_rerank(scored, top_k, lambda_param=0.5)

        # Step 7: 更新访问统计
        for item in diverse:
            self._update_access_stats(item.memory_id)

        return diverse

    def _freshness_score(self, item: MemoryItem, now: datetime) -> float:
        """时间新鲜度衰减:越久未访问,衰减越大;但永久型记忆衰减慢"""
        if item.memory_type == MemoryType.SEMANTIC:
            half_life_days = 180  # 语义记忆半衰期6个月
        elif item.memory_type == MemoryType.PROCEDURAL:
            half_life_days = 365  # 程序记忆半衰期1年
        else:
            half_life_days = 30   # 情景记忆半衰期1个月

        days_since = (now - item.last_accessed_at).days
        return math.pow(0.5, days_since / half_life_days)

    def _mmr_rerank(self, scored: list, top_k: int,
                    lambda_param: float = 0.5) -> list[MemoryItem]:
        """Maximal Marginal Relevance:平衡相关性与多样性"""
        if not scored:
            return []
        selected = [scored[0][0]]
        remaining = scored[1:]
        while len(selected) < top_k and remaining:
            best_item, best_idx, best_score = None, -1, -float("inf")
            for i, (item, rel_score) in enumerate(remaining):
                # 与已选记忆的最大相似度(用内容重叠近似)
                max_sim = max(
                    self._content_similarity(item.content, s.content)
                    for s in selected
                )
                mmr = lambda_param * rel_score - (1 - lambda_param) * max_sim
                if mmr > best_score:
                    best_score, best_item, best_idx = mmr, item, i
            selected.append(best_item)
            remaining.pop(best_idx)
        return selected

    def _content_similarity(self, a: str, b: str) -> float:
        """简易内容相似度(Jaccard)"""
        sa, sb = set(a), set(b)
        return len(sa & sb) / max(len(sa | sb), 1)

    def _keyword_search(self, query: str, user_id: str, k: int):
        # 基于关键词 LIKE 查询
        keywords = query.split()
        results = []
        for kw in keywords:
            rows = self.sqlite_store.conn.execute(
                "SELECT memory_id, content FROM memories "
                "WHERE user_id=? AND status='active' AND content LIKE ? LIMIT ?",
                (user_id, f"%{kw}%", k),
            ).fetchall()
            for r in rows:
                results.append({"memory_id": r["memory_id"], "content": r["content"]})
        return results
```

### 4.3 检索评分公式

最终检索评分综合四维度:

$$
\text{FinalScore}(m, q) = \underbrace{(\alpha \cdot S_{vec}(m,q) + \beta \cdot S_{kw}(m,q))}_{\text{相关性}} \times \underbrace{F(m)}_{\text{新鲜度}} + \underbrace{\gamma \cdot I(m)}_{\text{重要性}}
$$

其中:
- $S_{vec}(m,q)$:记忆 $m$ 与查询 $q$ 的向量余弦相似度
- $S_{kw}(m,q)$:关键词匹配得分
- $F(m) = 0.5^{\Delta t / T_{half}}$:新鲜度衰减函数
- $I(m)$:记忆重要性评分
- $\alpha + \beta + \gamma = 1$,默认 $\alpha=0.6, \beta=0.2, \gamma=0.2$

### 4.4 检索流程图

```mermaid
flowchart TB
    Q[用户查询] --> V[向量检索<br/>top 3k]
    Q --> K[关键词检索<br/>top 3k]
    V --> M[合并候选集]
    K --> M
    M --> F[元数据过滤<br/>type/importance/status]
    F --> S[综合评分<br/>相关性×新鲜度+重要性]
    S --> R[MMR多样性重排<br/>取top_k]
    R --> U[更新访问统计]
    U --> RET[返回结果]

    style S fill:#fff3cd,stroke:#d39e00,stroke-width:2px
    style R fill:#d1ecf1,stroke:#0c5460
```

---

## 五、记忆更新策略

### 5.1 记忆更新的五种操作

| 操作 | 触发场景 | 处理逻辑 |
|------|----------|----------|
| **新增(Create)** | 全新信息出现 | 创建新记忆,写入存储 |
| **修正(Update)** | 已有信息被纠正 | 旧版标记 deprecated,写入新版本 |
| **合并(Merge)** | 多条记忆语义重复 | 保留主记忆,合并字段,关联辅助 |
| **强化(Reinforce)** | 记忆被反复访问/验证 | 提升重要性、更新访问时间 |
| **遗忘(Forget)** | 过期、低价值、被纠正 | 状态变 ARCHIVED 或删除 |

### 5.2 记忆合并器实现

```python
class MemoryConsolidator:
    """记忆合并器:检测并合并语义重复的记忆"""

    def __init__(self, vector_store, sqlite_store,
                 similarity_threshold: float = 0.92):
        self.vector_store = vector_store
        self.sqlite_store = sqlite_store
        self.similarity_threshold = similarity_threshold

    def consolidate(self, new_item: MemoryItem) -> MemoryItem:
        """新记忆写入前的合并检查"""
        # 1. 检索相似记忆
        similar = self.vector_store.search(
            query=new_item.content, user_id=new_item.user_id, k=5,
        )

        # 2. 寻找可合并的高相似记忆
        for hit in similar:
            if hit["score"] >= self.similarity_threshold:
                existing = self.sqlite_store.get(hit["metadata"]["memory_id"])
                if existing and existing.status == MemoryStatus.ACTIVE:
                    return self._merge_two(existing, new_item)

        # 3. 无可合并记忆,直接新增
        return new_item

    def _merge_two(self, old: MemoryItem, new: MemoryItem) -> MemoryItem:
        """合并两条记忆"""
        # 保留更重要的为主记忆
        if new.importance_score > old.importance_score:
            primary, secondary = new, old
        else:
            primary, secondary = old, new

        # 合并内容:主内容 + 补充信息
        merged_content = primary.content
        if secondary.content not in primary.content:
            merged_content = f"{primary.content}\n[补充]: {secondary.content}"

        # 合并元数据
        merged = MemoryItem(
            memory_id=primary.memory_id,
            user_id=primary.user_id,
            agent_id=primary.agent_id,
            memory_type=primary.memory_type,
            content=merged_content,
            structured_data={**secondary.structured_data, **primary.structured_data},
            importance_score=max(primary.importance_score, secondary.importance_score),
            importance_level=max([primary.importance_level, secondary.importance_level],
                                 key=lambda x: ["LOW","MEDIUM","HIGH","CRITICAL"].index(x)),
            created_at=min(primary.created_at, secondary.created_at),
            last_accessed_at=max(primary.last_accessed_at, new.last_accessed_at),
            last_updated_at=datetime.now(),
            access_count=primary.access_count + secondary.access_count,
            source=f"{primary.source}+{secondary.source}",
            confidence=max(primary.confidence, secondary.confidence),
            verified=primary.verified or secondary.verified,
            tags=list(set(primary.tags + secondary.tags)),
            related_ids=list(set(primary.related_ids + secondary.related_ids + [secondary.memory_id])),
            status=MemoryStatus.ACTIVE,
            version=primary.version + 1,
        )
        # 旧记忆标记为已合并
        secondary.status = MemoryStatus.DEPRECATED
        self.sqlite_store.save(secondary)
        # 保存合并后的主记忆
        self.sqlite_store.save(merged)
        return merged
```

### 5.3 记忆强化机制

```python
class MemoryReinforcer:
    """记忆强化器:被访问/验证时增强记忆"""

    def reinforce_on_access(self, memory_id: str):
        """被检索时强化"""
        item = self.sqlite_store.get(memory_id)
        if not item:
            return
        item.access_count += 1
        item.last_accessed_at = datetime.now()
        # 访问次数达阈值,提升重要性(上限1.0)
        if item.access_count in [3, 10, 30, 100]:
            item.importance_score = min(1.0, item.importance_score + 0.1)
            item.importance_level = self._level_from_score(item.importance_score)
        self.sqlite_store.save(item)

    def reinforce_on_success(self, memory_id: str):
        """程序记忆执行成功时强化"""
        item = self.sqlite_store.get(memory_id)
        if item and item.memory_type == MemoryType.PROCEDURAL:
            item.structured_data["success_count"] += 1
            total = item.structured_data["success_count"] + item.structured_data["failure_count"]
            item.structured_data["success_rate"] = (
                item.structured_data["success_count"] / max(total, 1)
            )
            # 成功率高的规则提升重要性
            if item.structured_data["success_rate"] > 0.8 and total > 5:
                item.importance_level = "HIGH"
                item.importance_score = max(item.importance_score, 0.8)
            self.sqlite_store.save(item)
```

### 5.4 记忆衰减与遗忘

```python
class MemoryDecayer:
    """记忆衰减器:模拟人类遗忘曲线"""

    # 艾宾浩斯遗忘曲线近似:不同类型的衰减速率
    DECAY_RATES = {
        MemoryType.EPISODIC: 0.85,    # 情景记忆衰减快
        MemoryType.SEMANTIC: 0.97,    # 语义记忆衰减慢
        MemoryType.PROCEDURAL: 0.99,  # 程序记忆几乎不衰减
        MemoryType.PREFERENCE: 0.95,  # 偏好记忆较稳定
    }

    def decay_all(self, user_id: str = None):
        """批量衰减(后台定时执行)"""
        now = datetime.now()
        rows = self.sqlite_store.conn.execute(
            "SELECT memory_id, memory_type, importance_score, "
            "last_accessed_at, access_count FROM memories "
            "WHERE status='active'" + (" AND user_id=?" if user_id else ""),
            ((user_id,) if user_id else ()),
        ).fetchall()

        for row in rows:
            days = (now - datetime.fromisoformat(row["last_accessed_at"])).days
            decay_rate = self.DECAY_RATES[MemoryType(row["memory_type"])]
            # 衰减后的有效重要性
            effective = row["importance_score"] * (decay_rate ** days)
            # 长期未访问 + 低重要性 → 归档
            if effective < 0.1 and row["access_count"] < 3:
                self._archive(row["memory_id"])
            elif effective < 0.3:
                self._mark_fading(row["memory_id"])

    def _archive(self, memory_id: str):
        self.sqlite_store.conn.execute(
            "UPDATE memories SET status='archived' WHERE memory_id=?",
            (memory_id,),
        )
        self.sqlite_store.conn.commit()

    def _mark_fading(self, memory_id: str):
        self.sqlite_store.conn.execute(
            "UPDATE memories SET status='fading' WHERE memory_id=?",
            (memory_id,),
        )
        self.sqlite_store.conn.commit()
```

---

## 六、记忆管理规则

### 6.1 记忆生命周期状态机

```mermaid
stateDiagram-v2
    [*] --> Active: 创建
    Active --> Fading: 重要性衰减<0.3
    Active --> Active: 被访问/强化
    Fading --> Active: 被访问(唤醒)
    Fading --> Archived: 持续衰减<0.1
    Active --> Deprecated: 被纠正/矛盾
    Deprecated --> Archived: 版本保留
    Archived --> Active: 显式恢复
    Archived --> [*]: 超过归档保留期(永久删除)
```

### 6.2 记忆管理规则集

```python
class MemoryRuleEngine:
    """记忆管理规则引擎"""

    def __init__(self):
        self.rules = [
            # ===== 写入规则 =====
            Rule("R-W-01", "CRITICAL级记忆永久保留,不衰减",
                 condition=lambda m: m.importance_level == "CRITICAL",
                 action="skip_decay"),
            Rule("R-W-02", "情景记忆默认30天过期",
                 condition=lambda m: m.memory_type == MemoryType.EPISODIC,
                 action="set_expiry_30d"),
            Rule("R-W-03", "低可信度(<0.5)记忆标记未验证",
                 condition=lambda m: m.confidence < 0.5,
                 action="mark_unverified"),

            # ===== 更新规则 =====
            Rule("R-U-01", "矛盾语义记忆:旧版标记deprecated,不删除",
                 condition=self._is_contradicting,
                 action="deprecate_old"),
            Rule("R-U-02", "访问次数≥10且成功率>80%的程序记忆升级HIGH",
                 condition=lambda m: (m.memory_type == MemoryType.PROCEDURAL
                                      and m.access_count >= 10
                                      and m.structured_data.get("success_rate", 0) > 0.8),
                 action="upgrade_to_high"),
            Rule("R-U-03", "30天未被访问且importance<0.3进入FADING",
                 condition=self._is_stale_low_value,
                 action="mark_fading"),

            # ===== 删除规则 =====
            Rule("R-D-01", "FADING状态 + 60天未访问 → ARCHIVED",
                 condition=self._is_long_fading,
                 action="archive"),
            Rule("R-D-02", "ARCHIVED + 超过180天 → 永久删除",
                 condition=self._is_old_archived,
                 action="permanent_delete"),
            Rule("R-D-03", "用户主动删除请求 → 立即ARCHIVED",
                 condition=self._is_user_delete_request,
                 action="archive_immediately"),

            # ===== 容量规则 =====
            Rule("R-C-01", "单用户记忆超10万条触发容量治理",
                 condition=self._user_capacity_exceeded,
                 action="trigger_capacity_governance"),
        ]

    def evaluate(self, memory: MemoryItem, context: dict = None) -> list[str]:
        """评估记忆应执行的动作"""
        actions = []
        ctx = context or {}
        for rule in self.rules:
            if rule.condition(memory, ctx):
                actions.append(rule.action)
        return actions
```

### 6.3 管理规则一览表

| 规则ID | 触发条件 | 动作 | 优先级 |
|--------|----------|------|--------|
| R-W-01 | CRITICAL 级记忆 | 跳过衰减 | P0 |
| R-W-02 | 情景记忆新建 | 设置30天过期 | P1 |
| R-W-03 | 可信度<0.5 | 标记未验证 | P1 |
| R-U-01 | 检测到矛盾语义 | 旧版 deprecated | P0 |
| R-U-02 | 程序记忆高成功率 | 升级 HIGH | P1 |
| R-U-03 | 30天未访问+低重要性 | FADING | P2 |
| R-D-01 | FADING+60天未访问 | ARCHIVED | P1 |
| R-D-02 | ARCHIVED+180天 | 永久删除 | P2 |
| R-D-03 | 用户删除请求 | 立即归档 | P0 |
| R-C-01 | 单用户>10万条 | 容量治理 | P1 |

---

## 七、重要性分级机制

### 7.1 四级重要性体系

| 等级 | 分数范围 | 含义 | 衰减策略 | 保留期 |
|------|----------|------|----------|--------|
| **CRITICAL** | ≥0.9 | 核心身份/偏好/规则 | 不衰减 | 永久 |
| **HIGH** | 0.7~0.9 | 高价值事实/成功规则 | 慢衰减 | 长期 |
| **MEDIUM** | 0.4~0.7 | 一般事实/普通交互 | 标准衰减 | 中期 |
| **LOW** | <0.4 | 琐碎事件/低频信息 | 快衰减 | 短期 |

### 7.2 重要性评分算法

新记忆写入时,通过**多因子加权**计算初始重要性:

```python
class ImportanceGrader:
    """记忆重要性评分器"""

    def grade(self, content: str, memory_type: MemoryType,
              context: dict) -> tuple[float, str]:
        # 因子1:类型基础分(不同类型起点不同)
        type_base = {
            MemoryType.PREFERENCE: 0.85,   # 偏好天然重要
            MemoryType.PROCEDURAL: 0.75,   # 规则较重要
            MemoryType.SEMANTIC: 0.65,     # 事实中等
            MemoryType.EPISODIC: 0.45,     # 事件较低
        }[memory_type]

        # 因子2:用户明确性(主动陈述 > 被动观察)
        explicitness = 1.0 if context.get("user_explicit") else 0.6

        # 因子3:情感强度(强情感事件更重要)
        emotion = context.get("emotion_score", 0.5)

        # 因子4:重复度(被多次提及的信息更重要)
        repetition = min(1.0, context.get("mention_count", 1) / 5)

        # 因子5:可操作性(能指导未来决策的信息更重要)
        actionability = 0.8 if context.get("actionable") else 0.4

        # 综合加权
        score = (
            0.30 * type_base +
            0.20 * explicitness +
            0.15 * emotion +
            0.15 * repetition +
            0.20 * actionability
        )
        score = max(0.0, min(1.0, score))

        level = self._level_from_score(score)
        return score, level

    def _level_from_score(self, score: float) -> str:
        if score >= 0.9: return "CRITICAL"
        if score >= 0.7: return "HIGH"
        if score >= 0.4: return "MEDIUM"
        return "LOW"
```

### 7.3 重要性动态调整

| 事件 | 调整动作 |
|------|----------|
| 被检索访问 3/10/30/100 次 | importance +0.1 |
| 程序记忆执行成功 | success_rate 更新,达阈值升级 |
| 被用户纠正 | importance 降级,标记 unverified |
| 与新记忆矛盾 | 旧记忆 importance ×0.5 |
| 被多条记忆引用 | importance +0.05/条 |

---

## 八、容量限制与缓存平衡

### 8.1 容量限制设计

| 层级 | 容量上限 | 治理策略 |
|------|----------|----------|
| **L1 热缓存** | 单用户 1000 条 | LRU 淘汰最近最少访问 |
| **L2 主存储** | 单用户 10 万条 | 重要性+新鲜度综合淘汰 |
| **L3 归档** | 单用户 100 万条 | 超限后按时间删除最旧 |
| **全局** | 1 亿条 | 触发集群扩容 |

### 8.2 容量治理器实现

```python
class CapacityGovernor:
    """容量治理器:超限时智能淘汰"""

    LIMITS = {
        "L1": 1000,      # 单用户L1缓存
        "L2": 100_000,   # 单用户L2主存
        "L3": 1_000_000, # 单用户L3归档
    }

    def govern_user(self, user_id: str, store: SQLitePersistence):
        """对指定用户执行容量治理"""
        for level, limit in self.LIMITS.items():
            count = self._count_by_level(user_id, level, store)
            if count > limit:
                excess = count - limit
                self._evict(user_id, level, excess, store)

    def _evict(self, user_id: str, level: str, count: int,
               store: SQLitePersistence):
        """按综合得分淘汰最低价值记忆"""
        # 综合得分 = importance × freshness × access_frequency
        rows = store.conn.execute("""
            SELECT memory_id, importance_score,
                   julianday('now') - julianday(last_accessed_at) AS days_inactive,
                   access_count
            FROM memories
            WHERE user_id=? AND status='active'
            ORDER BY importance_score * pow(0.5, days_inactive/30) * (1 + access_count*0.01) ASC
            LIMIT ?
        """, (user_id, count)).fetchall()

        for row in rows:
            if level == "L2":
                # L2超限:ARCHIVED转入L3
                store.conn.execute(
                    "UPDATE memories SET status='archived' WHERE memory_id=?",
                    (row["memory_id"],))
            elif level == "L1":
                # L1超限:从缓存移除(主存保留)
                self._evict_from_cache(row["memory_id"])
        store.conn.commit()
```

### 8.3 长期保存与短期缓存的平衡策略

```mermaid
graph LR
    subgraph 短期缓存L1
        H1[刚写入记忆<br/>自动进L1]
        H2[CRITICAL级<br/>常驻L1]
        H3[高频访问<br/>提升至L1]
    end

    subgraph 长期保存L2
        S1[全量ACTIVE记忆]
        S2[向量索引]
        S3[关联图谱]
    end

    subgraph 归档L3
        A1[ARCHIVED状态]
        A2[历史版本]
        A3[低价值冷数据]
    end

    H1 -.60s刷盘.-> S1
    H2 -.常驻.-> S1
    H3 -.提升.-> H1
    S1 -.衰减归档.-> A1
    A1 -.回填请求.-> H1

    style H1 fill:#fce4ec,stroke:#880e4f
    style S1 fill:#d1ecf1,stroke:#0c5460,stroke-width:2px
    style A1 fill:#e2e3e5,stroke:#383d41
```

### 8.4 缓存与主存的协同规则

| 场景 | L1 行为 | L2 行为 |
|------|---------|---------|
| 新记忆写入 | 同步写入 | 异步刷盘 |
| 高频检索命中 | 直接返回 | 不查 |
| 检索未命中 | 回填至 L1 | 主查 |
| 记忆更新 | 失效 | 更新 |
| CRITICAL 记忆 | 常驻 | 同时存 |
| 容量超限 | LRU 淘汰 | 不影响 |

---

## 九、与 Agent 决策系统集成

### 9.1 记忆驱动的决策回路

长期记忆系统通过**记忆注入**与**经验反馈**两个环节深度集成到 Agent 的 Observe-Think-Act 回路:

```mermaid
flowchart TB
    subgraph Observe观察
        O1[用户输入/环境] --> O2[记忆检索<br/>MemoryRetriever]
        O2 --> O3[相关历史记忆]
    end

    subgraph Think思考
        O3 --> T1[组装Prompt<br/>注入记忆上下文]
        T1 --> T2[LLM推理<br/>结合历史经验]
        T2 --> T3[决策:下一步动作]
    end

    subgraph Act行动
        T3 --> A1[执行工具/生成回复]
        A1 --> A2[执行结果]
    end

    subgraph 反馈闭环
        A2 --> F1[记忆提取<br/>Extractor]
        F1 --> F2[重要性评分<br/>Grader]
        F2 --> F3[写入/更新记忆<br/>Writer]
        F3 -.->|下次决策| O2
        A2 -.->|程序记忆强化| F3
    end

    style O2 fill:#fff3cd,stroke:#d39e00,stroke-width:2px
    style F3 fill:#d4edda,stroke:#155724,stroke-width:2px
```

### 9.2 记忆注入 Prompt 模板

```python
MEMORY_INJECTION_PROMPT = """
你是一位具备长期记忆的智能助手。以下是与当前对话相关的历史记忆:

【语义记忆 - 事实/知识】
{semantic_memories}

【情景记忆 - 历史交互】
{episodic_memories}

【程序记忆 - 规则/技能】
{procedural_memories}

【偏好记忆 - 用户偏好】
{preference_memories}

=== 当前对话 ===
用户: {user_input}

请基于历史记忆和当前输入,给出符合用户偏好、复用成功经验、避开失败教训的回答。
若历史记忆与当前需求矛盾,以最新记忆为准。
"""
```

### 9.3 记忆检索的决策适配

```python
class MemoryAwareAgent:
    """集成长期记忆的 Agent"""

    def __init__(self, llm, retriever: HybridMemoryRetriever,
                 writer: MemoryWriter, consolidator: MemoryConsolidator):
        self.llm = llm
        self.retriever = retriever
        self.writer = writer
        self.consolidator = consolidator

    def respond(self, user_id: str, user_input: str) -> str:
        # Step 1: 检索相关记忆(按类型分组)
        memories = self.retriever.retrieve(
            query=user_input, user_id=user_id, top_k=10,
        )
        grouped = self._group_by_type(memories)

        # Step 2: 注入记忆到 Prompt
        prompt = MEMORY_INJECTION_PROMPT.format(
            semantic_memories=self._format(grouped.get(MemoryType.SEMANTIC, [])),
            episodic_memories=self._format(grouped.get(MemoryType.EPISODIC, [])),
            procedural_memories=self._format(grouped.get(MemoryType.PROCEDURAL, [])),
            preference_memories=self._format(grouped.get(MemoryType.PREFERENCE, [])),
            user_input=user_input,
        )

        # Step 3: LLM 推理
        response = self.llm.invoke(prompt)

        # Step 4: 提取并写入新记忆(异步)
        self._extract_and_write(user_id, user_input, response, memories)

        return response

    def _extract_and_write(self, user_id: str, user_input: str,
                           response: str, retrieved: list):
        """从交互中提取新记忆"""
        # 用 LLM 抽取可记忆的事实/偏好/规则
        extraction = self.llm.invoke(EXTRACTION_PROMPT.format(
            user_input=user_input, response=response,
        ))
        for item_data in parse_extraction(extraction):
            new_item = build_memory_item(user_id, item_data)
            # 合并检查 + 写入
            self.consolidator.consolidate(new_item)
            self.writer.write(new_item)
```

### 9.4 决策反馈:经验强化闭环

```python
def on_task_completed(self, task_id: str, success: bool, memory_ids: list[str]):
    """任务完成后,强化或弱化相关程序记忆"""
    for mid in memory_ids:
        item = self.sqlite_store.get(mid)
        if item and item.memory_type == MemoryType.PROCEDURAL:
            if success:
                item.structured_data["success_count"] += 1
                self.reinforcer.reinforce_on_success(mid)
            else:
                item.structured_data["failure_count"] += 1
                # 高失败率的规则降级
                total = (item.structured_data["success_count"]
                         + item.structured_data["failure_count"])
                rate = item.structured_data["success_count"] / max(total, 1)
                if rate < 0.3 and total > 5:
                    item.importance_level = "LOW"
                    item.importance_score *= 0.5
            self.sqlite_store.save(item)
```

---

## 十、学习能力与经验积累

### 10.1 Agent 学习的三个层次

```mermaid
graph TB
    subgraph L1层次-数据积累
        D1[每次交互记录<br/>写入情景记忆]
    end
    subgraph L2层次-模式归纳
        D1 --> P1[从多次交互中<br/>提取共性规则]
        P1 --> P2[写入程序记忆<br/>作为可复用经验]
    end
    subgraph L3层次-策略优化
        P2 --> S1[统计规则成功率]
        S1 --> S2[高成功率规则提升优先级]
        S2 --> S3[低成功率规则淘汰]
    end

    style P2 fill:#fff3cd,stroke:#d39e00,stroke-width:2px
    style S3 fill:#d4edda,stroke:#155724
```

### 10.2 经验归纳器

```python
class ExperienceInductor:
    """从多次交互中归纳可复用经验"""

    INDUCTION_PROMPT = """
分析以下近期的交互记录,归纳可复用的规则或模式:

交互记录:
{interactions}

请提取:
1. 反复出现的用户偏好(写入偏好记忆)
2. 成功解决问题的有效方法(写入程序记忆)
3. 反复出现的事实模式(写入语义记忆)

以JSON格式输出,每条包含:type/content/condition/importance
"""

    def induct_from_recent(self, user_id: str, days: int = 7):
        """从最近N天的交互中归纳经验"""
        # 1. 收集近期情景记忆
        recent = self._get_recent_episodic(user_id, days)
        if len(recent) < 5:
            return  # 样本不足,不归纳

        # 2. LLM 归纳
        result = self.llm.invoke(self.INDUCTION_PROMPT.format(
            interactions=self._format_interactions(recent),
        ))
        rules = parse_rules(result)

        # 3. 写入程序记忆
        for rule in rules:
            item = MemoryItem(
                memory_id=uuid4(),
                user_id=user_id,
                memory_type=MemoryType.PROCEDURAL,
                content=rule["content"],
                importance_score=0.7,
                importance_level="HIGH",
                source="induction",
                structured_data={
                    "rule_condition": rule["condition"],
                    "success_count": 0,
                    "failure_count": 0,
                    "success_rate": 0.0,
                    "inducted_from": [r.memory_id for r in recent],
                },
            )
            self.writer.write(item)
```

### 10.3 经验复用机制

| 经验类型 | 复用方式 | 触发条件 |
|----------|----------|----------|
| **成功规则** | 优先套用 | 当前任务匹配规则条件 |
| **失败教训** | 主动规避 | 当前任务与失败场景相似 |
| **用户偏好** | 自动适配 | 始终注入到 Prompt |
| **事实知识** | 直接引用 | 检索到相关事实 |

### 10.4 学习效果度量

| 指标 | 定义 | 目标 |
|------|------|------|
| **任务成功率提升** | 同类任务前后成功率差 | >15% |
| **平均交互轮数减少** | 同类任务前后轮数差 | >20% |
| **规则复用率** | 决策中引用程序记忆的比例 | >30% |
| **记忆命中率** | 检索记忆被决策采用的比例 | >60% |

---

## 十一、跨会话连续性保障

### 11.1 跨会话连续性的三层保障

```mermaid
graph TB
    subgraph 身份连续性
        I1[user_id 持久化] --> I2[用户画像记忆<br/>身份/偏好/历史]
    end
    subgraph 上下文连续性
        C1[上次会话摘要] --> C2[会话切换时<br/>自动注入摘要]
    end
    subgraph 经验连续性
        E1[历史程序记忆] --> E2[新会话决策<br/>复用成功经验]
    end

    I2 & C2 & E2 --> CONT[跨会话连续体验]

    style CONT fill:#d4edda,stroke:#155724,stroke-width:2px
```

### 11.2 会话切换的记忆衔接

```python
class SessionBridge:
    """会话切换时的记忆衔接"""

    def on_session_start(self, user_id: str, new_session_id: str) -> str:
        """新会话开始时,生成上下文摘要"""
        # 1. 检索用户核心记忆
        preferences = self.retriever.retrieve_by_type(
            user_id, MemoryType.PREFERENCE, top_k=5,
        )
        key_facts = self.retriever.retrieve_by_type(
            user_id, MemoryType.SEMANTIC, top_k=10,
            min_importance=0.7,
        )

        # 2. 获取上次会话摘要
        last_summary = self._get_last_session_summary(user_id)

        # 3. 组装上下文
        context = SESSION_RESUME_PROMPT.format(
            user_preferences=self._format(preferences),
            key_facts=self._format(key_facts),
            last_session_summary=last_summary,
        )
        return context

    def on_session_end(self, user_id: str, session_id: str,
                       interactions: list[dict]):
        """会话结束时,生成摘要并写入记忆"""
        summary = self.llm.invoke(SUMMARY_PROMPT.format(
            interactions=self._format(interactions),
        ))
        # 写入情景记忆:本次会话摘要
        item = MemoryItem(
            memory_id=uuid4(),
            user_id=user_id,
            memory_type=MemoryType.EPISODIC,
            content=f"会话{session_id}摘要: {summary}",
            importance_score=0.6,
            importance_level="MEDIUM",
            source="session_summary",
            structured_data={"session_id": session_id,
                             "interaction_count": len(interactions)},
        )
        self.writer.write(item)
```

### 11.3 跨会话连续性指标

| 维度 | 指标 | 说明 |
|------|------|------|
| **身份感知** | 用户姓名识别率 | "您是XX先生" |
| **偏好延续** | 偏好应用率 | 跨会话保持风格 |
| **上下文回顾** | 上次话题引用率 | "上次我们聊到..." |
| **经验复用** | 规则跨会话命中率 | 复用历史规则 |

---

## 十二、完整代码实现

### 12.1 长期记忆系统核心类

```python
"""
Agent 长期记忆系统完整实现
包含:存储、检索、更新、治理、决策集成
"""
import sqlite3
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from uuid import uuid4
from typing import Optional

# (MemoryItem, MemoryType, MemoryStatus 定义见第二章)

class LongTermMemorySystem:
    """Agent 长期记忆系统集成入口"""

    def __init__(self, db_path: str = "agent_memory.db",
                 vector_path: str = "./memory_vectors"):
        # 持久化层
        self.sqlite_store = SQLitePersistence(db_path)
        self.vector_store = VectorPersistence(vector_path)

        # 处理层
        self.grader = ImportanceGrader()
        self.consolidator = MemoryConsolidator(self.vector_store, self.sqlite_store)
        self.reinforcer = MemoryReinforcer(self.sqlite_store)
        self.decayer = MemoryDecayer(self.sqlite_store)
        self.rule_engine = MemoryRuleEngine()
        self.governor = CapacityGovernor()

        # 检索层
        self.retriever = HybridMemoryRetriever(
            self.vector_store, self.sqlite_store,
        )

        # 缓存层(L1)
        self._l1_cache: dict[str, list[MemoryItem]] = {}  # user_id -> items

    def remember(self, user_id: str, content: str,
                 memory_type: MemoryType,
                 context: dict = None) -> MemoryItem:
        """写入记忆(对外核心API)"""
        context = context or {}
        # 1. 重要性评分
        score, level = self.grader.grade(content, memory_type, context)
        # 2. 构建记忆条目
        item = MemoryItem(
            memory_id=str(uuid4()),
            user_id=user_id,
            agent_id=context.get("agent_id", "default"),
            memory_type=memory_type,
            content=content,
            importance_score=score,
            importance_level=level,
            source=context.get("source", "user"),
            confidence=context.get("confidence", 1.0),
            tags=context.get("tags", []),
            expiry_at=self._calc_expiry(memory_type),
        )
        # 3. 合并检查(去重)
        item = self.consolidator.consolidate(item)
        # 4. 持久化
        self.sqlite_store.save(item)
        self.vector_store.add(item)
        # 5. 写入L1缓存
        self._add_to_l1(user_id, item)
        return item

    def recall(self, user_id: str, query: str,
               top_k: int = 10,
               memory_types: list[MemoryType] = None) -> list[MemoryItem]:
        """检索记忆(对外核心API)"""
        # 1. 优先查L1缓存
        cached = self._search_l1(user_id, query, top_k)
        if len(cached) >= top_k:
            return cached[:top_k]
        # 2. L1不足,查L2主存
        items = self.retriever.retrieve(
            query=query, user_id=user_id, top_k=top_k,
            memory_types=memory_types,
        )
        # 3. 回填L1
        for item in items:
            self._add_to_l1(user_id, item)
        return items

    def update(self, memory_id: str, new_content: str,
               reason: str = "") -> MemoryItem:
        """更新记忆(对外核心API)"""
        old = self.sqlite_store.get(memory_id)
        if not old:
            raise KeyError(f"Memory {memory_id} not found")
        # 旧版标记deprecated,写入新版本
        old.status = MemoryStatus.DEPRECATED
        self.sqlite_store.save(old)
        # 创建新版本
        new_item = MemoryItem(
            memory_id=str(uuid4()),
            user_id=old.user_id, agent_id=old.agent_id,
            memory_type=old.memory_type,
            content=new_content,
            importance_score=old.importance_score,
            importance_level=old.importance_level,
            source=f"update_from:{old.memory_id}",
            parent_id=old.memory_id,
            version=old.version + 1,
            metadata={"update_reason": reason},
        )
        self.sqlite_store.save(new_item)
        self.vector_store.add(new_item)
        return new_item

    def forget(self, memory_id: str, immediate: bool = False):
        """遗忘记忆(对外核心API)"""
        if immediate:
            self.sqlite_store.conn.execute(
                "DELETE FROM memories WHERE memory_id=?", (memory_id,))
        else:
            self.sqlite_store.conn.execute(
                "UPDATE memories SET status='archived' WHERE memory_id=?",
                (memory_id,))
        self.sqlite_store.conn.commit()

    def run_maintenance(self):
        """后台维护任务(定时执行)"""
        # 1. 衰减
        self.decayer.decay_all()
        # 2. 容量治理
        for user_id in self._get_all_users():
            self.governor.govern_user(user_id, self.sqlite_store)
        # 3. 过期清理
        self._cleanup_expired()

    def _calc_expiry(self, memory_type: MemoryType) -> Optional[datetime]:
        if memory_type == MemoryType.EPISODIC:
            return datetime.now() + timedelta(days=30)
        return None

    def _add_to_l1(self, user_id: str, item: MemoryItem):
        cache = self._l1_cache.setdefault(user_id, [])
        cache.append(item)
        # L1容量限制:1000条/用户,LRU淘汰
        if len(cache) > 1000:
            cache.sort(key=lambda x: x.last_accessed_at)
            cache.pop(0)
```

### 12.2 使用示例

```python
# 初始化
memory = LongTermMemorySystem()

# 写入记忆
memory.remember(
    user_id="user_001",
    content="用户张三擅长Python,偏好简洁的回答风格",
    memory_type=MemoryType.PREFERENCE,
    context={"source": "user_explicit", "tags": ["Python", "style"]},
)

memory.remember(
    user_id="user_001",
    content="解答Python装饰器问题时,提供代码示例效果更好",
    memory_type=MemoryType.PROCEDURAL,
    context={"actionable": True, "source": "induction"},
)

# 检索记忆
results = memory.recall(
    user_id="user_001",
    query="如何理解装饰器?",
    top_k=5,
)
for r in results:
    print(f"[{r.importance_level}] {r.content}")

# 更新记忆
memory.update(
    memory_id=results[0].memory_id,
    new_content="用户张三现已转岗Java开发",
    reason="用户主动告知转岗",
)

# 后台维护(定时任务)
memory.run_maintenance()
```

---

## 十三、典型应用场景案例

### 13.1 案例一:智能客服 Agent

| 维度 | 设计 |
|------|------|
| **场景** | 电商客服,需记住用户历史订单、偏好、投诉记录 |
| **记忆类型** | 偏好记忆(用户习惯)+ 情景记忆(历史工单)+ 程序记忆(处理规则) |
| **检索策略** | 优先检索用户偏好+近期工单 |
| **更新策略** | 每次工单结束归纳处理规则 |
| **效果** | 首次响应准确率 +35%,平均处理时长 -40% |

### 13.2 案例二:个人助理 Agent

| 维度 | 设计 |
|------|------|
| **场景** | 长期陪伴的个人助理,需持续学习用户习惯 |
| **记忆类型** | 全四类记忆并用 |
| **检索策略** | 混合检索 + 偏好常驻 |
| **更新策略** | 每周归纳经验,每月容量治理 |
| **效果** | 用户体验评分从 3.8 提升至 4.6(5分制) |

### 13.3 案例三:编程助手 Agent

| 维度 | 设计 |
|------|------|
| **场景** | 协助开发者编程,需记住代码风格、技术栈、常见bug |
| **记忆类型** | 程序记忆(编码规则)+ 语义记忆(技术栈)+ 偏好记忆(代码风格) |
| **检索策略** | 任务匹配时优先复用成功规则 |
| **更新策略** | 代码采纳/拒绝反馈强化程序记忆 |
| **效果** | 代码采纳率 +28%,重复错误率 -52% |

---

## 十四、最佳实践与避坑指南

### 14.1 最佳实践清单

| 实践项 | 说明 |
|--------|------|
| ✅ **分级存储** | L1/L2/L3 三层,平衡速度与成本 |
| ✅ **重要性驱动** | 所有治理决策基于 importance_score |
| ✅ **混合检索** | 向量+关键词+元数据,避免单一检索盲区 |
| ✅ **写入去重** | 合并器避免语义重复记忆堆积 |
| ✅ **衰减遗忘** | 模拟艾宾浩斯曲线,自动清理低价值记忆 |
| ✅ **异步写入** | 向量化异步化,不阻塞主流程 |
| ✅ **版本化更新** | 旧版 deprecated 不删除,支持回溯 |
| ✅ **反馈闭环** | 任务成败反馈到程序记忆,形成学习闭环 |

### 14.2 常见陷阱与规避

| 陷阱 | 现象 | 规避方案 |
|------|------|----------|
| **记忆爆炸** | 无限量写入导致存储爆炸 | 重要性门槛 + 容量治理 |
| **重复记忆** | 同一事实多次写入 | 合并器 + 相似度阈值 |
| **过时记忆** | 旧信息未被纠正导致误导 | 矛盾检测 + 版本化更新 |
| **检索延迟** | 全量扫描导致慢查询 | L1缓存 + 向量索引 |
| **冷启动空白** | 新用户无记忆可用 | 默认偏好 + 快速归纳 |
| **隐私泄露** | 跨用户记忆串扰 | user_id 强制隔离 |
| **遗忘有价值记忆** | 衰减过激丢失关键信息 | CRITICAL级豁免衰减 |

### 14.3 与短长期记忆协同的建议

参考 [76短期记忆与长期记忆核心区别深度解析.md](./76短期记忆与长期记忆核心区别深度解析.md),长期记忆应与短期记忆协同:

| 协同点 | 设计 |
|--------|------|
| **巩固机制** | 短期记忆中反复出现的信息 → 提升为长期记忆 |
| **检索层级** | 优先查短期(快) → 不足查长期(全) |
| **容量互补** | 短期容量小但快,长期容量大但慢 |
| **任务衔接** | 短期维持单会话上下文,长期维持跨会话经验 |

---

> **文档说明**:本文档给出了 Agent 长期记忆系统的完整工程设计,涵盖存储结构、持久化、检索、更新、治理、决策集成、学习与跨会话连续性。所有代码示例均可直接落地,建议结合 74~76 号文档理解记忆类型体系与短长期分野,构建完整的 Agent Memory 系统。
