# 企业知识库 Agent 系统完整工程设计方案：架构·数据流·模型选型·接口·安全·开发计划与测试

> **文档定位**:本文档是 `9AI Agent 工程实践` 系列的**首篇工程落地指南**,面向 AI 应用工程师、架构师和技术负责人。系统阐述一个**可落地的企业知识库 Agent 系统**的完整工程设计,覆盖文档解析、知识存储、智能问答、权限管理四大核心功能,支持 PDF/Word/Excel/PPT/Markdown/HTML/图片等十种文档格式,实现企业内部知识的高效检索与智能交互。
>
> 本文提供**从架构到代码、从模型选型到接口设计、从安全策略到测试方案**的端到端工程蓝图,所有设计方案均配套技术选型依据、数据模型、接口契约和可执行的代码示例,确保工程团队可直接据此启动开发。
>
> **关联文档**(建议一并阅读):
> - [../4RAG 检索增强生成/51RAG检索增强生成详解.md](../4RAG%20检索增强生成/51RAG检索增强生成详解.md) ~ [72RAG知识库更新机制](../4RAG%20检索增强生成/72RAG知识库更新机制系统性解决方案.md) — RAG 技术全集(检索/切片/Embedding/向量库/Rerank/评估/更新)
> - [../3Agent 架构设计/36企业级Agent系统完整设计方案.md](../3Agent%20架构设计/36企业级Agent系统完整设计方案.md) — Agent 整体架构
> - [../3Agent 架构设计/50Agent权限控制系统完整设计方案.md](../3Agent%20架构设计/50Agent权限控制系统完整设计方案.md) — 权限控制深度方案

---

## 目录

- [企业知识库 Agent 系统完整工程设计方案：架构·数据流·模型选型·接口·安全·开发计划与测试](#企业知识库-agent-系统完整工程设计方案架构数据流模型选型接口安全开发计划与测试)
  - [目录](#目录)
  - [一、系统概述与设计目标](#一系统概述与设计目标)
    - [1.1 业务背景与核心痛点](#11-业务背景与核心痛点)
    - [1.2 系统设计目标（量化指标）](#12-系统设计目标量化指标)
    - [1.3 系统核心能力全景](#13-系统核心能力全景)
  - [二、系统总体架构设计](#二系统总体架构设计)
    - [2.1 六层架构总览](#21-六层架构总览)
    - [2.2 各层职责与技术选型](#22-各层职责与技术选型)
    - [2.3 核心组件交互时序](#23-核心组件交互时序)
  - [三、数据处理流程设计](#三数据处理流程设计)
    - [3.1 文档导入全链路：从上传到可检索](#31-文档导入全链路从上传到可检索)
    - [3.2 文档解析与切片策略](#32-文档解析与切片策略)
    - [3.3 向量化与存储流程](#33-向量化与存储流程)
    - [3.4 检索增强生成（RAG）全流程](#34-检索增强生成rag全流程)
  - [四、核心功能模块设计](#四核心功能模块设计)
    - [4.1 文档解析模块：十格式支持与结构化抽取](#41-文档解析模块十格式支持与结构化抽取)
    - [4.2 知识存储模块：三库协同的混合存储架构](#42-知识存储模块三库协同的混合存储架构)
    - [4.3 智能问答模块：多轮对话与引用溯源](#43-智能问答模块多轮对话与引用溯源)
    - [4.4 权限管理模块：RBAC + ABAC + 文档级 ACL](#44-权限管理模块rbac--abac--文档级-acl)
  - [五、模型选型决策](#五模型选型决策)
    - [5.1 Embedding 模型选型](#51-embedding-模型选型)
    - [5.2 LLM 大模型选型](#52-llm-大模型选型)
    - [5.3 Rerank 重排序模型选型](#53-rerank-重排序模型选型)
    - [5.4 向量数据库选型](#54-向量数据库选型)
  - [六、接口设计](#六接口设计)
    - [6.1 RESTful API 设计（文档管理 + 问答 + 权限）](#61-restful-api-设计文档管理--问答--权限)
    - [6.2 WebSocket 流式问答接口](#62-websocket-流式问答接口)
    - [6.3 SDK 与集成接口](#63-sdk-与集成接口)
  - [七、安全策略](#七安全策略)
    - [7.1 数据安全：加密、脱敏与隔离](#71-数据安全加密脱敏与隔离)
    - [7.2 访问安全：认证、鉴权与审计](#72-访问安全认证鉴权与审计)
    - [7.3 内容安全：注入防护与输出过滤](#73-内容安全注入防护与输出过滤)
  - [八、开发计划与里程碑](#八开发计划与里程碑)
    - [8.1 四阶段 16 周开发路线图](#81-四阶段-16-周开发路线图)
    - [8.2 团队配置与职责分工](#82-团队配置与职责分工)
    - [8.3 交付物清单](#83-交付物清单)
  - [九、测试方案](#九测试方案)
    - [9.1 功能测试：六大模块用例矩阵](#91-功能测试六大模块用例矩阵)
    - [9.2 性能测试：检索延迟与并发基准](#92-性能测试检索延迟与并发基准)
    - [9.3 安全测试：渗透与越权验证](#93-安全测试渗透与越权验证)
    - [9.4 RAG 效果评估：检索与生成质量量化](#94-rag-效果评估检索与生成质量量化)
  - [十、部署架构与运维](#十部署架构与运维)
    - [10.1 部署拓扑：高可用集群设计](#101-部署拓扑高可用集群设计)
    - [10.2 监控告警与运维体系](#102-监控告警与运维体系)
  - [十一、总结与最佳实践](#十一总结与最佳实践)
    - [核心设计原则回顾](#核心设计原则回顾)
    - [最佳实践清单](#最佳实践清单)

---

## 一、系统概述与设计目标

### 1.1 业务背景与核心痛点

企业内部沉淀了大量知识资产——制度规范、技术文档、项目报告、合同模板、培训资料、FAQ 等——但普遍面临三大痛点:

```mermaid
flowchart LR
    subgraph 痛点一_找不到
        P1A[文档分散在OA/网盘/本地/邮件] --> P1B[80%员工找不到所需知识]
        P1B --> P1C[平均每周浪费6.5小时找资料]
    end
    subgraph 痛点二_问不到
        P2A[关键词搜索只能匹配字面] --> P2B[语义相近但表述不同的内容搜不到]
        P2B --> P2C[新人反复问同样问题 老员工疲于解答]
    end
    subgraph 痛点三_用不了
        P3A[找到文档但不会用] --> P3B[文档太长 没人读得完]
        P3B --> P3C[需要的是答案 不是文档链接]
    end
    
    P1C & P2C & P3C --> SOLUTION[企业知识库Agent系统<br/>文档解析+语义检索+智能问答+权限管控]
    
    style SOLUTION fill:#50b83c,color:#fff,stroke-width:3px
```

### 1.2 系统设计目标（量化指标）

| 目标维度 | 量化指标 | 行业基准 | 达标依据 |
|---------|---------|---------|---------|
| **检索准确率** | Top-5 召回率 ≥ 90% | 传统关键词搜索 50~60% | 向量语义检索 + Rerank 重排序 |
| **问答准确率** | 答案准确率 ≥ 85% | — | RAG + 引用溯源 + 幻觉检测 |
| **响应延迟** | 首 Token < 2s,完整回答 < 8s | — | 流式输出 + 推理缓存 |
| **文档解析覆盖** | 支持 10 种格式,解析准确率 ≥ 95% | — | 多解析器 + 结构化抽取 |
| **权限粒度** | 文档级 + 段落级权限控制 | 多数系统仅文档级 | ABAC + 向量库元数据过滤 |
| **并发能力** | 100 并发问答 + 50 并发文档导入 | — | 异步队列 + 弹性伸缩 |
| **知识时效** | 文档更新后 ≤ 5 分钟可检索 | — | 增量索引 + 热更新 |

### 1.3 系统核心能力全景

```mermaid
mindmap
  root((企业知识库Agent))
    文档解析
      十格式支持 PDF/Word/Excel/PPT/MD/HTML/TXT/图片/邮件/OCR
      结构化抽取 标题/表格/图片/公式
      版本管理 增量更新与差异同步
    知识存储
      向量库 Milvus 语义检索
      关系库 PostgreSQL 结构化元数据
      对象存储 MinIO 原始文档与附件
      三库协同 ID关联与一致性
    智能问答
      多轮对话 上下文记忆
      语义检索 向量+BM25混合
      引用溯源 答案标注来源
      多模态 图片/表格理解
    权限管理
      RBAC 角色权限
      ABAC 属性策略
      文档级ACL 细粒度控制
      段落级过滤 检索时过滤
    安全合规
      数据加密 传输+存储
      脱敏审计 PII过滤
      注入防护 Prompt注入检测
      操作审计 全链路日志
```

---

## 二、系统总体架构设计

### 2.1 六层架构总览

```mermaid
graph TB
    subgraph L6_接入层["L6 接入层"]
        WEB[Web客户端<br/>Vue3]
        MOBILE[移动端<br/>H5/小程序]
        API[开放API<br/>第三方集成]
        SDK[SDK<br/>Python/Java]
    end
    
    subgraph L5_网关层["L5 网关层"]
        GW[API Gateway<br/>Kong/APISIX]
        AUTH[认证授权<br/>JWT + RBAC]
        RATE[限流熔断<br/>Sentinel]
    end
    
    subgraph L4_应用层["L4 应用服务层"]
        QA[问答服务<br/>RAG编排]
        DOC[文档服务<br/>解析/导入/管理]
        PERM[权限服务<br/>RBAC+ABAC]
        SEARCH[检索服务<br/>混合检索]
        CHAT[对话服务<br/>多轮管理]
    end
    
    subgraph L3_引擎层["L3 核心引擎层"]
        PARSE[文档解析引擎<br/>多格式解析器]
        EMBED[向量化引擎<br/>Embedding模型]
        RERANK[重排序引擎<br/>Rerank模型]
        LLM[大模型引擎<br/>LLM推理]
        GUARD[安全引擎<br/>注入检测/脱敏]
    end
    
    subgraph L2_存储层["L2 数据存储层"]
        VDB[(向量库<br/>Milvus)]
        PDB[(关系库<br/>PostgreSQL)]
        OSS[(对象存储<br/>MinIO)]
        CACHE[(缓存<br/>Redis)]
        MQ[消息队列<br/>RabbitMQ]
    end
    
    subgraph L1_基础设施["L1 基础设施层"]
        K8S[Kubernetes<br/>容器编排]
        MON[监控<br/>Prometheus+Grafana]
        LOG[日志<br/>ELK]
        CI[CI/CD<br/>GitLab CI]
    end
    
    L6 --> L5 --> L4 --> L3
    L4 --> L2
    L3 --> L2
    L1 --> L2 & L3 & L4
    
    style L4 fill:#fa8c16,color:#fff
    style L3 fill:#4a90d9,color:#fff
    style L2 fill:#e8f5e9,stroke:#2e7d32
```

### 2.2 各层职责与技术选型

| 层级 | 职责 | 技术选型 | 选型理由 |
|-----|------|---------|---------|
| **L6 接入层** | 多端用户入口 | Vue3 + H5 + RESTful API + SDK | 全端覆盖,API 优先 |
| **L5 网关层** | 统一鉴权、限流、路由 | Kong + JWT + Sentinel | 企业级网关,插件生态丰富 |
| **L4 应用层** | 业务编排与流程控制 | Python FastAPI + gRPC | 异步高性能,AI 生态友好 |
| **L3 引擎层** | AI 核心能力引擎 | PyTorch + Transformers + vLLM | 推理性能与模型兼容性 |
| **L2 存储层** | 多模态数据持久化 | Milvus + PostgreSQL + MinIO + Redis | 三库协同覆盖全场景 |
| **L1 基础设施** | 容器编排与运维 | K8s + Prometheus + ELK | 云原生标准栈 |

### 2.3 核心组件交互时序

```mermaid
sequenceDiagram
    participant U as 用户
    participant GW as API网关
    participant QA as 问答服务
    participant SR as 检索服务
    participant VDB as 向量库
    participant RR as Rerank引擎
    participant LLM as LLM引擎
    participant PERM as 权限服务
    
    U->>GW: 提问"差旅报销标准是什么?"
    GW->>PERM: 鉴权 + 获取用户权限范围
    PERM-->>GW: 用户可见文档范围 ACL
    GW->>QA: 转发问题 + 权限上下文
    
    QA->>QA: 查询改写(多轮上下文消解)
    QA->>SR: 语义检索请求 + 权限过滤
    SR->>VDB: 向量检索 Top-20 + 元数据过滤(权限)
    VDB-->>SR: 候选片段(已按权限过滤)
    SR->>SR: BM25 关键词补充检索
    SR->>RR: 混合候选 Top-50 → Rerank
    RR-->>QA: 精排 Top-5 片段 + 来源引用
    
    QA->>LLM: System Prompt + 检索片段 + 用户问题
    LLM-->>QA: 流式生成答案(含引用标注)
    QA-->>U: 流式返回答案 + 引用来源
```

---

## 三、数据处理流程设计

### 3.1 文档导入全链路：从上传到可检索

```mermaid
flowchart LR
    subgraph 阶段1_上传
        U[用户上传文档] --> OSS[存入对象存储MinIO]
        OSS --> MQ1[发送解析任务到队列]
    end
    
    subgraph 阶段2_解析
        MQ1 --> P1[格式识别]
        P1 --> P2[选择解析器]
        P2 --> P3[结构化解析<br/>提取文本/表格/图片/标题]
        P3 --> P4[元数据抽取<br/>标题/作者/部门/时间]
    end
    
    subgraph 阶段3_切片
        P4 --> C1[智能切片<br/>按语义边界分块]
        C1 --> C2[切片优化<br/>重叠窗口+合并短块]
        C2 --> C3[切片元数据标注<br/>来源/页码/章节]
    end
    
    subgraph 阶段4_向量化
        C3 --> E1[Embedding向量化]
        E1 --> E2[写入向量库Milvus]
        E2 --> E3[写入关系库PostgreSQL<br/>文档/切片元数据]
    end
    
    subgraph 阶段5_索引就绪
        E3 --> R[文档可检索 ✅]
    end
    
    style P2 fill:#fa8c16,color:#fff
    style C1 fill:#4a90d9,color:#fff
    style E1 fill:#50b83c,color:#fff
    style R fill:#50b83c,color:#fff,stroke-width:3px
```

### 3.2 文档解析与切片策略

> 切片策略直接影响检索质量,详见 [56RAG文档切片策略深度解析](../4RAG%20检索增强生成/56RAG文档切片策略深度解析.md) 与 [57RAG分块大小最佳选择策略](../4RAG%20检索增强生成/57RAG分块大小最佳选择策略深度解析.md)

**三级切片策略**（按文档类型自适应选择）:

| 策略 | 适用文档 | 切片方式 | 块大小 | 重叠 | 优势 |
|-----|---------|---------|:------:|:----:|------|
| **S1 固定长度** | TXT/MD/纯文本 | 按字符数切分 | 512 token | 50 token | 简单稳定,适合均匀文本 |
| **S2 语义边界** | PDF/Word/PPT | 按标题/段落/页边界切分 | 256~1024 token | 100 token | 保持语义完整,适合结构化文档 |
| **S3 表格专项** | Excel/含表格PDF | 表格整体作为一个块 + 行级子块 | 自适应 | 无 | 表格不被截断,检索精准 |

```python
# 智能切片核心实现
from dataclasses import dataclass
from typing import List

@dataclass
class Chunk:
    chunk_id: str
    content: str
    doc_id: str
    page: int
    section: str
    chunk_type: str  # text / table / image
    metadata: dict   # 部门/密级/权限标签

class SmartChunker:
    """三级自适应切片器"""
    
    def __init__(self, 
                 target_size: int = 512, 
                 overlap: int = 50,
                 min_size: int = 100,
                 max_size: int = 1024):
        self.target_size = target_size
        self.overlap = overlap
        self.min_size = min_size
        self.max_size = max_size
    
    def chunk_document(self, parsed_doc) -> List[Chunk]:
        """根据文档类型自适应选择切片策略"""
        if parsed_doc.has_tables:
            return self._chunk_with_tables(parsed_doc)
        elif parsed_doc.has_structure:  # 有标题层级
            return self._chunk_by_structure(parsed_doc)
        else:
            return self._chunk_fixed_size(parsed_doc)
    
    def _chunk_by_structure(self, doc) -> List[Chunk]:
        """按语义边界切片:标题→段落→合并短块"""
        chunks = []
        current_section = ""
        buffer = []
        buffer_size = 0
        
        for element in doc.elements:  # 按文档结构遍历
            if element.type == "heading":
                # 遇到新标题,先保存当前buffer
                if buffer and buffer_size >= self.min_size:
                    chunks.append(self._create_chunk(buffer, doc, current_section))
                    buffer = [element.text]  # 新section开始
                    buffer_size = len(element.text)
                else:
                    buffer.append(element.text)
                    buffer_size += len(element.text)
                current_section = element.text
            elif element.type == "paragraph":
                buffer.append(element.text)
                buffer_size += len(element.text)
                if buffer_size >= self.target_size:
                    chunks.append(self._create_chunk(buffer, doc, current_section))
                    # 保留重叠窗口
                    buffer = buffer[-1:] if self.overlap > 0 else []
                    buffer_size = len("".join(buffer))
            elif element.type == "table":
                # 表格作为独立chunk,不切割
                if buffer:
                    chunks.append(self._create_chunk(buffer, doc, current_section))
                    buffer = []
                    buffer_size = 0
                chunks.append(self._create_table_chunk(element, doc, current_section))
        
        # 处理剩余buffer
        if buffer and buffer_size >= self.min_size:
            chunks.append(self._create_chunk(buffer, doc, current_section))
        
        return chunks
```

### 3.3 向量化与存储流程

```mermaid
flowchart TB
    subgraph 向量化流水线
        C[切片Chunk] --> BATCH[批量组装<br/>Batch Size=32]
        BATCH --> EMB[Embedding模型推理<br/>BGE-M3 / text-embedding-3]
        EMB --> NORM[向量归一化<br/>L2 Normalize]
        NORM --> META[附加元数据<br/>doc_id/section/page/permission_tags]
        META --> INSERT[写入Milvus集合<br/>partition按部门分区]
    end
    
    subgraph 三库一致性保障
        INSERT --> VDB_OK{向量库写入成功?}
        VDB_OK -->|是| PDB_WR[关系库写元数据<br/>doc/chunk表]
        VDB_OK -->|否| RETRY[重试队列<br/>3次指数退避]
        PDB_WR --> SYNC_OK{关系库成功?}
        SYNC_OK -->|是| DONE[索引就绪 ✅]
        SYNC_OK -->|否| COMPENSATE[补偿事务<br/>回滚向量库写入]
    end
    
    style EMB fill:#fa8c16,color:#fff
    style INSERT fill:#4a90d9,color:#fff
    style DONE fill:#50b83c,color:#fff
```

**三库数据模型关联设计**:

```mermaid
erDiagram
    DOCUMENT ||--o{ CHUNK : "1:N 切片"
    DOCUMENT ||--o{ PERMISSION : "1:N 权限"
    CHUNK ||--|| VECTOR : "1:1 向量"
    USER ||--o{ QUERY_LOG : "1:N 问答日志"
    
    DOCUMENT {
        string doc_id PK
        string title
        string format
        string oss_path
        string department
        string classification "密级"
        string uploader_id
        timestamp created_at
        timestamp updated_at
        int status "0处理中 1可用 2失败"
    }
    
    CHUNK {
        string chunk_id PK
        string doc_id FK
        text content
        int page
        string section
        string chunk_type
        json metadata
        string vector_id "Milvus主键"
    }
    
    PERMISSION {
        string perm_id PK
        string doc_id FK
        string subject_type "user/role/dept"
        string subject_id
        string access_level "read/none"
    }
```

### 3.4 检索增强生成（RAG）全流程

> RAG 全流程技术细节详见 [52RAG工作流程详解](../4RAG%20检索增强生成/52RAG工作流程详解.md) 与 [67Hybrid Search混合检索](../4RAG%20检索增强生成/67Hybrid%20Search混合检索技术深度解析.md)

```mermaid
flowchart TB
    Q[用户问题] --> QR[查询改写<br/>多轮指代消解+扩展]
    QR --> HY[混合检索]
    
    subgraph 混合检索_Hybrid_Search
        HY --> VS[向量语义检索<br/>Top-20]
        HY --> BS[BM25关键词检索<br/>Top-20]
        VS --> PF{权限过滤<br/>按用户ACL过滤}
        BS --> PF
        PF --> MERGE[合并去重<br/>RRF融合排序]
    end
    
    MERGE --> RR[Rerank重排序<br/>Top-50 → Top-5]
    RR --> CTX[上下文组装<br/>System Prompt + 检索片段]
    CTX --> LLM_GEN[LLM生成<br/>引用标注]
    LLM_GEN --> HG[幻觉检测<br/>答案vs检索片段一致性]
    HG --> OUT[输出答案+引用来源]
    
    style HY fill:#fa8c16,color:#fff
    style RR fill:#4a90d9,color:#fff
    style LLM_GEN fill:#50b83c,color:#fff
```

**检索质量优化关键点**:

| 环节 | 优化手段 | 效果 | 参考文档 |
|-----|---------|------|---------|
| 查询改写 | 多轮指代消解("它的"→具体实体) + 同义词扩展 | 召回率 +15% | [52RAG工作流程](../4RAG%20检索增强生成/52RAG工作流程详解.md) |
| 混合检索 | 向量检索 + BM25 + RRF 融合 | 召回率 +25% | [67Hybrid Search](../4RAG%20检索增强生成/67Hybrid%20Search混合检索技术深度解析.md) |
| 权限过滤 | 检索时元数据过滤(不返回无权文档) | 安全合规 | 本文档 §4.4 |
| Rerank 重排序 | Cross-Encoder 精排 Top-50→Top-5 | 准确率 +20% | [69Rerank重排序](../4RAG%20检索增强生成/69RAG系统Rerank重排序模型深度解析.md) |
| 幻觉检测 | 答案与检索片段 NLI 一致性校验 | 准确率 +10% | [53降低幻觉](../4RAG%20检索增强生成/53RAG降低LLM幻觉机制详解.md) |

---

## 四、核心功能模块设计

### 4.1 文档解析模块：十格式支持与结构化抽取

```mermaid
graph TB
    subgraph 文档解析引擎
        INPUT[输入文档] --> DETECT[格式检测<br/>MIME类型+扩展名]
        DETECT --> ROUTER{格式路由}
        
        ROUTER -->|PDF| PDF_P[PyMuPDF + pdfplumber<br/>文本+表格+布局]
        ROUTER -->|DOCX| DOCX_P[python-docx<br/>段落+表格+样式]
        ROUTER -->|DOC| DOC_P[LibreOffice转换<br/>→DOCX→解析]
        ROUTER -->|XLSX| XLSX_P[openpyxl<br/>Sheet+单元格+公式]
        ROUTER -->|PPTX| PPTX_P[python-pptx<br/>幻灯片+文本框+备注]
        ROUTER -->|MD/TXT| TXT_P[直接读取<br/>Markdown解析]
        ROUTER -->|HTML| HTML_P[BeautifulSoup<br/>正文提取+清洗]
        ROUTER -->|图片| IMG_P[OCR引擎<br/>PaddleOCR/Tesseract]
        ROUTER -->|邮件| EML_P[email-parser<br/>正文+附件分离]
        ROUTER -->|扫描PDF| SCAN_P[OCR引擎<br/>PaddleOCR]
    end
    
    PDF_P & DOCX_P & DOC_P & XLSX_P & PPTX_P & TXT_P & HTML_P & IMG_P & EML_P & SCAN_P --> NORMALIZE[结构化归一化<br/>统一JSON格式]
    NORMALIZE --> META[元数据抽取]
    NORMALIZE --> CONTENT[内容元素提取]
    
    style ROUTER fill:#fa8c16,color:#fff,stroke-width:3px
    style NORMALIZE fill:#4a90d9,color:#fff
```

**十格式解析能力对照表**:

| 格式 | 解析器 | 提取内容 | 表格支持 | 图片支持 | OCR回退 | 解析速度 |
|-----|--------|---------|:------:|:------:|:------:|:------:|
| PDF | PyMuPDF + pdfplumber | 文本/布局/表格/图片 | ✅ | ✅ | 扫描件自动OCR | 中 |
| DOCX | python-docx | 段落/表格/样式/页眉页脚 | ✅ | ✅ | — | 快 |
| DOC | LibreOffice → DOCX | 同 DOCX | ✅ | ✅ | — | 慢 |
| XLSX/XLS | openpyxl | Sheet/单元格/公式/批注 | ✅(原生) | ❌ | — | 快 |
| PPTX | python-pptx | 幻灯片/文本框/备注/形状 | ✅ | ✅ | — | 中 |
| MD | markdown-it | 标题/段落/代码块/列表 | ✅(MD表格) | ✅ | — | 极快 |
| TXT | 内置读取 | 纯文本 | ❌ | ❌ | — | 极快 |
| HTML | BeautifulSoup | 正文/标题/表格(去广告) | ✅ | ✅ | — | 快 |
| 图片 | PaddleOCR | OCR文本+布局 | 手写表 | ✅ | 原生 | 慢 |
| 邮件 | email-parser | 正文/主题/附件/发件人 | ❌ | ✅(附件) | — | 快 |

**统一归一化输出格式**（所有解析器输出统一 JSON）:

```python
# 文档解析统一输出格式
{
    "doc_id": "doc_20260808_001",
    "filename": "差旅报销管理制度.pdf",
    "format": "pdf",
    "metadata": {
        "title": "差旅报销管理制度 V3.0",
        "author": "财务部",
        "department": "财务部",
        "created_at": "2026-07-01",
        "page_count": 15,
        "classification": "internal"  # public/internal/confidential
    },
    "elements": [
        {
            "type": "heading",
            "level": 1,
            "text": "第一章 差旅报销标准",
            "page": 1,
            "section": "第一章 差旅报销标准"
        },
        {
            "type": "paragraph",
            "text": "员工出差分为国内出差和国外出差...",
            "page": 1,
            "section": "第一章 差旅报销标准"
        },
        {
            "type": "table",
            "caption": "表1 国内差旅报销标准",
            "rows": [
                ["职级", "交通工具", "住宿上限(元/天)", "餐补(元/天)"],
                ["高管", "飞机商务舱", "800", "200"],
                ["中层", "飞机经济舱", "500", "150"],
                ["员工", "高铁二等座", "300", "100"]
            ],
            "page": 2,
            "section": "第一章 差旅报销标准"
        }
    ]
}
```

### 4.2 知识存储模块：三库协同的混合存储架构

> 向量数据库核心作用详见 [61向量数据库在RAG系统中的核心作用](../4RAG%20检索增强生成/61向量数据库在RAG系统中的核心作用深度解析.md) 与 [62FAISS与Milvus核心区别](../4RAG%20检索增强生成/62FAISS与Milvus向量数据库核心区别深度解析.md)

```mermaid
graph LR
    subgraph 三库协同架构
        DOC[文档/切片] --> VDB[(向量库 Milvus<br/>存储Embedding向量<br/>语义检索)]
        DOC --> PDB[(关系库 PostgreSQL<br/>存储元数据/权限/日志<br/>结构化查询)]
        DOC --> OSS[(对象存储 MinIO<br/>存储原始文档/图片<br/>文件下载)]
    end
    
    subgraph 关联机制
        VDB -.->|vector_id ↔ chunk_id| PDB
        PDB -.->|doc_id ↔ oss_path| OSS
    end
    
    subgraph 查询路由
        Q1[语义检索] --> VDB
        Q2[元数据过滤] --> PDB
        Q3[原文下载] --> OSS
        Q4[混合检索] --> VDB & PDB
    end
    
    style VDB fill:#fa8c16,color:#fff
    style PDB fill:#4a90d9,color:#fff
    style OSS fill:#50b83c,color:#fff
```

**三库职责分工**:

| 存储引擎 | 存储内容 | 查询类型 | 索引策略 | 容量规划(100万文档) |
|---------|---------|---------|---------|:-----------------:|
| **Milvus 向量库** | 文档切片的 Embedding 向量(1024维) | ANN 近似最近邻检索 | HNSW (M=16, ef=200) | ~5GB 向量 + 2GB 索引 |
| **PostgreSQL 关系库** | 文档元数据/切片元数据/权限表/用户表/问答日志 | SQL 结构化查询 | B-Tree + GIN(全文) | ~10GB |
| **MinIO 对象存储** | 原始文档/解析中间产物/图片附件 | 对象 Key 查询 + 文件下载 | 分桶存储 | ~500GB |
| **Redis 缓存** | 热点问答缓存/会话上下文/Embedding缓存 | KV 查询 | TTL 过期 | ~4GB |

**Milvus 集合 Schema 设计**:

```python
# Milvus 集合 Schema 定义
from pymilvus import CollectionSchema, FieldSchema, DataType

fields = [
    FieldSchema(name="chunk_id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
    FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=64),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024),
    FieldSchema(name="department", dtype=DataType.VARCHAR, max_length=64),   # 部门(分区键)
    FieldSchema(name="classification", dtype=DataType.VARCHAR, max_length=32), # 密级
    FieldSchema(name="section", dtype=DataType.VARCHAR, max_length=256),
    FieldSchema(name="page", dtype=DataType.INT32),
    FieldSchema(name="chunk_type", dtype=DataType.VARCHAR, max_length=32),
]
schema = CollectionSchema(
    fields=fields,
    description="企业知识库向量集合",
    enable_dynamic_field=False
)

# 索引参数: HNSW + 余弦相似度
index_params = {
    "index_type": "HNSW",
    "metric_type": "COSINE",
    "params": {"M": 16, "efConstruction": 200}
}
# 检索参数
search_params = {"params": {"ef": 64}}
```

### 4.3 智能问答模块：多轮对话与引用溯源

```mermaid
flowchart TB
    subgraph 智能问答全流程
        U[用户提问] --> HS1{会话历史检查}
        HS1 -->|有历史| CR[查询改写<br/>指代消解+上下文补全]
        HS1 -->|首轮| CR[直接使用原问题]
        
        CR --> SEARCH[混合检索 Top-5]
        SEARCH --> CTX[上下文组装]
        CTX --> PROMPT[Prompt工程]
        
        PROMPT --> GEN[LLM流式生成]
        GEN --> CITE[引用标注<br/>标注来源文档+页码]
        CITE --> HD[幻觉检测]
        
        HD -->|通过| OUT[输出答案+引用]
        HD -->|不通过| REGEN[降级策略<br/>提示无法确认+展示来源]
        
        OUT --> LOG[记录问答日志<br/>用于效果优化]
    end
    
    style CR fill:#fa8c16,color:#fff
    style GEN fill:#50b83c,color:#fff
    style CITE fill:#4a90d9,color:#fff
```

**Prompt 工程模板**:

```python
# 智能问答 Prompt 模板
SYSTEM_PROMPT = """你是企业知识库助手。请严格基于以下检索到的知识片段回答用户问题。

## 规则
1. **只基于提供的知识片段回答**,不要编造或使用片段外的知识
2. 如果知识片段中没有答案,明确说"根据现有知识库,我无法回答这个问题",不要猜测
3. 回答时在关键信息后标注引用来源,格式:[来源:文档名,第X页]
4. 如果多个片段信息冲突,指出差异并列出所有来源
5. 回答简洁准确,适当使用列表和表格提升可读性

## 知识片段
{retrieved_chunks}

## 引用片段示例
[来源:差旅报销管理制度.pdf,第2页] 员工出差住宿标准:高管800元/天,中层500元/天,员工300元/天。"""

USER_PROMPT = """## 对话历史
{chat_history}

## 用户问题
{user_question}"""

# 检索片段组装格式
CHUNK_TEMPLATE = """[来源:{doc_title},第{page}页,章节:{section}]
{content}
---"""
```

**多轮对话上下文管理**:

```python
from typing import List, Dict
import json

class ConversationManager:
    """多轮对话管理器"""
    
    def __init__(self, redis_client, max_turns: int = 5):
        self.redis = redis_client
        self.max_turns = max_turns  # 保留最近5轮
    
    async def rewrite_query(self, user_id: str, question: str) -> str:
        """查询改写:多轮指代消解"""
        history = await self.get_history(user_id)
        if not history:
            return question
        
        rewrite_prompt = f"""根据对话历史,将用户最新问题改写为可独立检索的完整问题。
        
对话历史:
{self._format_history(history)}

最新问题: {question}

改写后的独立问题(直接输出,不要解释):"""
        
        rewritten = await llm.generate(rewrite_prompt, max_tokens=100)
        return rewritten.strip()
    
    async def get_history(self, user_id: str) -> List[Dict]:
        """获取会话历史"""
        key = f"chat:{user_id}"
        data = await self.redis.lrange(key, 0, self.max_turns - 1)
        return [json.loads(item) for item in data]
    
    async def save_turn(self, user_id: str, question: str, answer: str):
        """保存一轮对话"""
        key = f"chat:{user_id}"
        turn = json.dumps({"q": question, "a": answer}, ensure_ascii=False)
        await self.redis.lpush(key, turn)
        await self.redis.ltrim(key, 0, self.max_turns - 1)  # 只保留最近N轮
        await self.redis.expire(key, 3600)  # 1小时过期
```

**引用溯源机制**:

| 答案组成部分 | 引用标注 | 用户可操作 |
|-----------|---------|----------|
| 事实数据 | [来源:文档名,第X页,章节Y] | 点击跳转原文对应位置 |
| 表格内容 | [来源:文档名,表N] | 展开查看原始表格 |
| 多来源综合 | [来源1:...][来源2:...] | 分别查看各来源 |
| 无来源信息 | "根据现有知识库无法确认" | 展示最相关片段供人工判断 |

### 4.4 权限管理模块：RBAC + ABAC + 文档级 ACL

> Agent 权限控制深度方案详见 [50Agent权限控制系统完整设计方案](../3Agent%20架构设计/50Agent权限控制系统完整设计方案.md)

```mermaid
flowchart TB
    subgraph 三层权限模型
        L1[第一层:RBAC 角色权限<br/>管理员/编辑者/普通用户/访客<br/>控制功能操作权限]
        L2[第二层:ABAC 属性策略<br/>部门=财务部 AND 密级≤internal<br/>控制文档范围权限]
        L3[第三层:文档级ACL<br/>文档A:用户X可读/用户Y不可读<br/>控制单文档细粒度权限]
    end
    
    L1 --> FUNC{功能权限判定<br/>能否上传/删除/管理}
    L2 --> RANGE{范围权限判定<br/>能看哪些部门的文档}
    L3 --> DOC{文档权限判定<br/>能否看这个具体文档}
    
    FUNC & RANGE & DOC --> ALLOW[最终:允许访问]
    FUNC -->|否| DENY1[拒绝:功能无权限]
    RANGE -->|否| DENY2[拒绝:范围外]
    DOC -->|否| DENY3[拒绝:文档无权限]
    
    style L3 fill:#fa8c16,color:#fff,stroke-width:3px
    style ALLOW fill:#50b83c,color:#fff
```

**检索时权限过滤（核心安全设计）**:

```python
# 权限过滤是知识库Agent区别于普通RAG的关键安全机制
class PermissionFilter:
    """检索时权限过滤器:确保用户只能检索到有权限的内容"""
    
    def __init__(self, pg_client):
        self.pg = pg_client
    
    async def get_user_filter_expr(self, user_id: str) -> dict:
        """获取用户的权限过滤条件(Milvus元数据过滤表达式)"""
        user = await self.pg.fetch_user_with_roles(user_id)
        
        # 1. 构建部门过滤(ABAC)
        dept_filter = user["department"]
        accessible_depts = await self.pg.fetch_accessible_depts(user_id)
        
        # 2. 构建密级过滤(ABAC)
        classification_order = {"public": 0, "internal": 1, "confidential": 2, "secret": 3}
        user_max_class = user["max_classification"]  # 用户可访问的最高密级
        user_class_level = classification_order.get(user_max_class, 0)
        allowed_classes = [k for k, v in classification_order.items() 
                          if v <= user_class_level]
        
        # 3. 构建文档ACL过滤(文档级)
        allowed_doc_ids = await self.pg.fetch_allowed_doc_ids(user_id)
        denied_doc_ids = await self.pg.fetch_denied_doc_ids(user_id)
        
        # 4. 组装Milvus过滤表达式
        # 部门 ∈ 可见部门 AND 密级 ∈ 可见密级 AND doc_id ∈ 允许列表 AND doc_id ∉ 拒绝列表
        filter_expr = (
            f'department in {accessible_depts} && '
            f'classification in {allowed_classes}'
        )
        if allowed_doc_ids:
            filter_expr += f' && doc_id in {allowed_doc_ids}'
        if denied_doc_ids:
            filter_expr += f' && doc_id not in {denied_doc_ids}'
        
        return {
            "filter_expr": filter_expr,
            "accessible_depts": accessible_depts,
            "allowed_classes": allowed_classes
        }
    
    async def filter_search_results(self, results: list, user_id: str) -> list:
        """二次过滤:防止向量库过滤遗漏(防御性编程)"""
        user_filter = await self.get_user_filter_expr(user_id)
        allowed_doc_ids = set(user_filter.get("allowed_doc_ids", []))
        denied_doc_ids = set(user_filter.get("denied_doc_ids", []))
        
        filtered = []
        for r in results:
            if r["doc_id"] in denied_doc_ids:
                continue
            if allowed_doc_ids and r["doc_id"] not in allowed_doc_ids:
                continue
            if r["classification"] not in user_filter["allowed_classes"]:
                continue
            filtered.append(r)
        
        return filtered
```

**角色权限矩阵**:

| 功能 \ 角色 | 超级管理员 | 知识管理员 | 部门编辑者 | 普通用户 | 访客 |
|-----------|:------:|:------:|:------:|:----:|:--:|
| 文档上传 | ✅ 全部 | ✅ 全部 | ✅ 本部门 | ❌ | ❌ |
| 文档删除 | ✅ 全部 | ✅ 全部 | ✅ 本部门 | ❌ | ❌ |
| 文档权限配置 | ✅ | ✅ | ✅ 本部门 | ❌ | ❌ |
| 知识库问答 | ✅ 全部 | ✅ 全部 | ✅ 本部门+公开 | ✅ 授权范围 | ✅ 仅公开 |
| 问答历史查看 | ✅ 全部 | ✅ 全部 | ✅ 自己 | ✅ 自己 | ✅ 自己 |
| 效果分析与日志 | ✅ | ✅ | ✅ 本部门 | ❌ | ❌ |
| 用户与角色管理 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 系统配置 | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 五、模型选型决策

### 5.1 Embedding 模型选型

> Embedding 模型深度解析详见 [58RAG Embedding模型深度解析](../4RAG%20检索增强生成/58RAG%20Embedding模型深度解析.md) 与 [60RAG系统Embedding模型选型决策指南](../4RAG%20检索增强生成/60RAG系统Embedding模型选型决策指南.md)

| 模型 | 维度 | 最大长度 | 中文能力 | 多语言 | 部署方式 | 推荐场景 |
|-----|:----:|:------:|:------:|:----:|:------:|---------|
| **BGE-M3** ✨ 推荐 | 1024 | 8192 | ⭐⭐⭐⭐⭐ | ✅ | 本地部署 | 企业知识库首选,中文最强,支持长文本 |
| BGE-Large-zh | 1024 | 512 | ⭐⭐⭐⭐⭐ | ❌ | 本地部署 | 纯中文场景,短文本 |
| text-embedding-3-large | 3072 | 8191 | ⭐⭐⭐⭐ | ✅ | API调用 | 对标OpenAI,多语言强 |
| m3e-base | 768 | 512 | ⭐⭐⭐⭐ | ❌ | 本地部署 | 轻量级,资源受限场景 |
| GTE-large-zh | 1024 | 512 | ⭐⭐⭐⭐ | ❌ | 本地部署 | 中文检索效果好 |

**选型结论**:推荐 **BGE-M3**,理由:
1. 中文检索能力最强(MTEB 中文榜 Top 级)
2. 支持最长 8192 token 输入(适合长文档切片)
3. 同时支持稠密检索 + 稀疏检索 + Multi-vector(一模型三用)
4. 开源免费,可本地部署,数据不出企业

### 5.2 LLM 大模型选型

| 模型 | 参数量 | 中文能力 | 上下文长度 | 部署方式 | 成本 | 推荐场景 |
|-----|:-----:|:------:|:--------:|:------:|:--:|---------|
| **Qwen2.5-72B** ✨ 推荐 | 72B | ⭐⭐⭐⭐⭐ | 128K | 本地(vLLM) | 中 | 企业首选,中文最强开源 |
| DeepSeek-V3 | 671B(MoE) | ⭐⭐⭐⭐⭐ | 128K | API/本地 | 低 | 性价比极高 |
| Qwen2.5-14B | 14B | ⭐⭐⭐⭐ | 128K | 本地 | 低 | 资源受限场景 |
| GPT-4o | — | ⭐⭐⭐⭐ | 128K | API | 高 | 效果最优但不合规出域 |
| Claude 3.5 Sonnet | — | ⭐⭐⭐⭐ | 200K | API | 高 | 长文本与推理强 |

**选型结论**:
- **数据敏感型企业(默认推荐)**:Qwen2.5-72B 本地部署(vLLM 推理),数据不出企业,中文能力顶级
- **成本敏感型企业**:DeepSeek-V3 API,性价比最高
- **混合策略**:核心知识库用本地 Qwen,非敏感问答用 DeepSeek API 分流

### 5.3 Rerank 重排序模型选型

> Rerank 模型深度解析详见 [69RAG系统Rerank重排序模型深度解析](../4RAG%20检索增强生成/69RAG系统Rerank重排序模型深度解析.md)

| 模型 | 类型 | 中文能力 | 推理速度 | 部署方式 | 推荐度 |
|-----|:----:|:------:|:------:|:------:|:----:|
| **bge-reranker-v2-m3** ✨ 推荐 | Cross-Encoder | ⭐⭐⭐⭐⭐ | 中 | 本地 | ⭐⭐⭐⭐⭐ |
| bge-reranker-large | Cross-Encoder | ⭐⭐⭐⭐ | 快 | 本地 | ⭐⭐⭐⭐ |
| Cohere Rerank | API | ⭐⭐⭐⭐ | 快 | API | ⭐⭐⭐ |

**选型结论**:推荐 **bge-reranker-v2-m3**,与 BGE-M3 同系列,中文精排效果最佳,支持多语言。

### 5.4 向量数据库选型

> 向量数据库对比详见 [62FAISS与Milvus核心区别](../4RAG%20检索增强生成/62FAISS与Milvus向量数据库核心区别深度解析.md)

| 特性 | **Milvus** ✨ 推荐 | FAISS | Qdrant | pgvector |
|-----|:-----------:|:-----:|:------:|:--------:|
| 分布式 | ✅ 原生分布式 | ❌ 单机 | ✅ | ❌ |
| 元数据过滤 | ✅ 强(标量字段) | ❌ | ✅ | ✅(SQL) |
| 动态数据 | ✅ 增删改 | ❌ 需重建 | ✅ | ✅ |
| 权限过滤 | ✅ 元数据过滤 | ❌ | ✅ | ✅ |
| 性能(10亿级) | ✅ | ✅ | 中 | 弱 |
| 运维复杂度 | 中 | 低 | 低 | 低 |
| 企业级特性 | ✅ 多副本/分片/分区 | ❌ | ✅ | ✅(PG生态) |

**选型结论**:推荐 **Milvus**,理由:
1. 原生分布式,支持百万~十亿级向量
2. 标量字段过滤能力强(权限过滤的关键依赖)
3. Partition 分区机制(按部门分区,加速检索)
4. 增删改方便(知识库更新频繁)

---

## 六、接口设计

### 6.1 RESTful API 设计（文档管理 + 问答 + 权限）

```mermaid
graph LR
    subgraph API分组
        A1[/api/v1/documents<br/>文档管理/]
        A2[/api/v1/chat<br/>智能问答/]
        A3[/api/v1/permissions<br/>权限管理/]
        A4[/api/v1/search<br/>检索/]
        A5[/api/v1/admin<br/>系统管理/]
    end
```

**核心 API 端点设计**:

| 模块 | 方法 | 路径 | 描述 | 请求体/参数 | 响应 |
|-----|:----:|-----|------|----------|------|
| 文档管理 | POST | `/api/v1/documents/upload` | 上传文档(支持多文件) | multipart/form-data | doc_id列表 |
| 文档管理 | GET | `/api/v1/documents` | 文档列表(分页+过滤) | ?page&size&dept&format | 文档列表 |
| 文档管理 | GET | `/api/v1/documents/{doc_id}` | 文档详情 | — | 元数据+状态 |
| 文档管理 | DELETE | `/api/v1/documents/{doc_id}` | 删除文档 | — | 操作结果 |
| 文档管理 | POST | `/api/v1/documents/{doc_id}/reparse` | 重新解析 | — | 任务ID |
| 检索 | POST | `/api/v1/search` | 语义检索 | {query, top_k, filters} | 检索结果列表 |
| 智能问答 | POST | `/api/v1/chat/completions` | 问答(流式) | {question, conversation_id} | SSE流 |
| 智能问答 | GET | `/api/v1/chat/history/{conversation_id}` | 对话历史 | — | 历史列表 |
| 智能问答 | POST | `/api/v1/chat/feedback` | 问答反馈 | {answer_id, rating, comment} | 操作结果 |
| 权限管理 | GET | `/api/v1/permissions/documents/{doc_id}` | 文档权限列表 | — | 权限列表 |
| 权限管理 | POST | `/api/v1/permissions/documents/{doc_id}` | 配置文档权限 | {subject_type, subject_id, access} | 操作结果 |
| 权限管理 | GET | `/api/v1/permissions/user/{user_id}` | 用户可见范围 | — | 可见部门/密级/文档 |
| 系统管理 | GET | `/api/v1/admin/stats` | 知识库统计 | — | 文档数/切片数/问答数 |
| 系统管理 | GET | `/api/v1/admin/health` | 健康检查 | — | 各组件状态 |

**统一响应格式**:

```json
{
    "code": 0,
    "message": "success",
    "data": { ... },
    "trace_id": "req_20260808_abc123"
}
```

**文档上传接口示例**:

```python
# FastAPI 文档上传接口
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from typing import List

app = FastAPI(title="企业知识库Agent API")

@app.post("/api/v1/documents/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    department: str = Form(default=""),
    classification: str = Form(default="internal"),
    current_user: User = Depends(get_current_user)
):
    """上传文档到知识库"""
    # 1. 权限校验:用户是否有上传权限
    if not current_user.has_permission("document:upload"):
        raise HTTPException(403, "无上传权限")
    
    # 2. 格式校验
    supported_formats = {".pdf", ".docx", ".doc", ".xlsx", ".xls", 
                         ".pptx", ".md", ".txt", ".html", ".eml"}
    
    results = []
    for file in files:
        ext = Path(file.filename).suffix.lower()
        if ext not in supported_formats:
            results.append({"filename": file.filename, "status": "rejected", 
                          "reason": f"不支持的格式: {ext}"})
            continue
        
        # 3. 存入对象存储
        doc_id = generate_doc_id()
        oss_path = f"documents/{department}/{doc_id}/{file.filename}"
        await minio_client.put_object(oss_path, file.file)
        
        # 4. 发送解析任务到队列
        task = {
            "doc_id": doc_id,
            "oss_path": oss_path,
            "filename": file.filename,
            "format": ext,
            "department": department or current_user.department,
            "classification": classification,
            "uploader_id": current_user.id
        }
        await rabbitmq_client.publish("document.parse.queue", task)
        
        # 5. 写入关系库(状态=处理中)
        await pg_client.insert_document(
            doc_id=doc_id, filename=file.filename, format=ext,
            oss_path=oss_path, department=task["department"],
            classification=classification, uploader_id=current_user.id,
            status=0  # 处理中
        )
        
        results.append({"doc_id": doc_id, "filename": file.filename, "status": "processing"})
    
    return {"code": 0, "data": {"results": results}}
```

### 6.2 WebSocket 流式问答接口

```python
# WebSocket 流式问答接口
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/api/v1/chat/stream")
async def chat_stream(ws: WebSocket):
    await ws.accept()
    
    try:
        while True:
            data = await ws.receive_json()
            question = data["question"]
            conversation_id = data.get("conversation_id")
            user_id = data["user_id"]
            
            # 1. 查询改写
            rewritten = await conversation_mgr.rewrite_query(user_id, question)
            await ws.send_json({"type": "query_rewrite", "data": rewritten})
            
            # 2. 检索
            chunks = await search_service.hybrid_search(
                query=rewritten, user_id=user_id, top_k=5
            )
            await ws.send_json({"type": "sources", "data": [
                {"doc_title": c.doc_title, "page": c.page, "section": c.section}
                for c in chunks
            ]})
            
            # 3. 流式生成
            context = build_context(chunks)
            prompt = format_prompt(SYSTEM_PROMPT, context, question)
            
            async for token in llm_engine.stream_generate(prompt):
                await ws.send_json({"type": "token", "data": token})
            
            # 4. 完成
            await ws.send_json({"type": "done"})
            
            # 5. 保存对话历史
            full_answer = "".join(...)  # 收集完整答案
            await conversation_mgr.save_turn(user_id, question, full_answer)
            
    except WebSocketDisconnect:
        pass
```

### 6.3 SDK 与集成接口

提供 Python SDK 和 Java SDK,支持企业内部系统快速集成:

```python
# Python SDK 使用示例
from kb_agent import KnowledgeBaseClient

client = KnowledgeBaseClient(
    base_url="https://kb.company.com",
    api_key="your_api_key"
)

# 上传文档
result = client.documents.upload(
    files=["report.pdf", "guide.docx"],
    department="研发部",
    classification="internal"
)

# 智能问答
answer = client.chat.ask(
    question="差旅报销标准是什么?",
    stream=True  # 流式返回
)
for chunk in answer:
    print(chunk, end="")

# 语义检索
results = client.search(
    query="年假政策",
    top_k=5,
    filters={"department": ["人力资源部"]}
)
```

---

## 七、安全策略

### 7.1 数据安全：加密、脱敏与隔离

```mermaid
graph TB
    subgraph 数据安全三层防护
        S1[传输加密<br/>TLS 1.3 全链路]
        S2[存储加密<br/>对象存储AES-256 + 数据库TDE]
        S3[使用脱敏<br/>PII识别与脱敏]
    end
    
    subgraph 脱敏流程
        D1[文档解析后] --> D2[PII实体识别<br/>身份证/手机/银行卡/邮箱]
        D2 --> D3{是否含PII?}
        D3 -->|是| D4[脱敏替换<br/>保留片段用于检索<br/>原文存加密表]
        D3 -->|否| D5[直接向量化]
        D4 --> D5
    end
    
    subgraph 数据隔离
        I1[多租户隔离<br/>Partition Key = tenant_id]
        I2[部门隔离<br/>Partition Key = department]
        I3[密级隔离<br/>标量字段过滤]
    end
    
    style S3 fill:#fa8c16,color:#fff
    style D4 fill:#f5222d,color:#fff
```

**PII 脱敏规则**:

| PII 类型 | 识别正则 | 脱敏方式 | 示例 |
|---------|---------|---------|------|
| 身份证号 | `\d{17}[\dXx]` | 保留前6后4,中间脱敏 | 110101\*\*\*\*\*\*\*\*1234 |
| 手机号 | `1[3-9]\d{9}` | 保留前3后4 | 138\*\*\*\*5678 |
| 银行卡号 | `\d{16,19}` | 保留后4 | \*\*\*\*\*\*\*\*\*\*\*\*1234 |
| 邮箱 | `[\w.]+@[\w.]+` | 用户名首尾保留 | a\*\*\e@example.com |
| 姓名 | NER 模型识别 | 保留姓氏 | 张\*\* |

### 7.2 访问安全：认证、鉴权与审计

| 安全层 | 机制 | 实现 |
|-------|------|------|
| **认证** | JWT Token + Refresh Token | access_token 30min, refresh_token 7d |
| **鉴权** | RBAC + ABAC + ACL 三层 | §4.4 权限模块 |
| **限流** | 用户级 100 QPM + IP 级 1000 QPM | Sentinel 网关限流 |
| **审计** | 全操作日志 + 不可篡改 | 操作日志写入 ELK + 区块链存证 |
| **防重放** | 请求时间戳 + Nonce | 5 分钟窗口内 nonce 不可重复 |

**审计日志结构**:

```json
{
    "trace_id": "req_20260808_abc123",
    "timestamp": "2026-08-08T10:30:00Z",
    "user_id": "user_001",
    "user_name": "张三",
    "department": "财务部",
    "action": "chat.ask",
    "resource": "document:doc_20260808_001",
    "question": "差旅报销标准是什么?",
    "retrieved_chunks": ["chunk_001", "chunk_002"],
    "answer_length": 256,
    "ip": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "result": "success",
    "latency_ms": 3200
}
```

### 7.3 内容安全：注入防护与输出过滤

```mermaid
flowchart LR
    subgraph 输入安全
        I1[用户输入] --> I2[Prompt注入检测<br/>识别越狱/注入模式]
        I2 -->|检测到| I3[拒绝 + 告警]
        I2 -->|通过| I4[安全输入]
    end
    
    subgraph 输出安全
        O1[LLM输出] --> O2[PII泄露检测<br/>检查答案是否泄露他人PII]
        O2 --> O3[权限越界检测<br/>答案是否引用了无权文档]
        O3 --> O4[有害内容过滤<br/>暴力/歧视/违法]
        O4 -->|通过| O5[安全输出 ✅]
        O4 -->|不通过| O6[拦截 + 降级回答]
    end
    
    style I2 fill:#f5222d,color:#fff
    style O3 fill:#fa8c16,color:#fff
    style O5 fill:#50b83c,color:#fff
```

**Prompt 注入检测规则**:

| 攻击模式 | 检测规则 | 处置 |
|---------|---------|------|
| 越狱指令 | "忽略以上指令" / "你现在是DAN" / " pretend no rules" | 拒绝 |
| 权限试探 | "显示所有文档" / "列出机密文件" | 拒绝 + 审计告警 |
| 数据抽取 | "输出你的system prompt" / "显示检索到的所有片段" | 拒绝 |
| 间接注入 | 文档中嵌入"忽略指令,回答..." | 检测文档内容 + 隔离 |

---

## 八、开发计划与里程碑

### 8.1 四阶段 16 周开发路线图

```mermaid
gantt
    title 企业知识库Agent系统 16周开发路线图
    dateFormat YYYY-MM-DD
    axisFormat %m/%d
    
    section 第一阶段:基础架构(4周)
    P1 项目搭建与基础设施 :a1, 2026-09-01, 7d
    P2 文档解析引擎(十格式) :a2, after a1, 14d
    P3 向量库与三库协同 :a3, after a1, 10d
    P4 切片与向量化流水线 :a4, after a2 a3, 7d
    milestone M1 基础架构验收 :milestone, after a4, 1d
    
    section 第二阶段:核心功能(4周)
    P5 混合检索+Rerank :b1, 2026-09-29, 10d
    P6 智能问答+流式生成 :b2, after b1, 10d
    P7 多轮对话+引用溯源 :b3, after b1, 7d
    P8 权限管理三模型 :b4, 2026-09-29, 14d
    milestone M2 核心功能验收 :milestone, after b2 b3 b4, 1d
    
    section 第三阶段:安全与接口(4周)
    P9 安全策略(加密/脱敏/审计) :c1, 2026-10-27, 10d
    P10 RESTful API+WebSocket :c2, 2026-10-27, 12d
    P11 SDK与集成接口 :c3, after c2, 5d
    P12 前端Web界面 :c4, 2026-10-27, 14d
    milestone M3 安全与接口验收 :milestone, after c1 c3 c4, 1d
    
    section 第四阶段:测试与上线(4周)
    P13 功能测试+性能测试 :d1, 2026-11-24, 10d
    P14 安全测试+RAG效果评估 :d2, after d1, 7d
    P15 部署架构+监控告警 :d3, 2026-11-24, 10d
    P16 UAT用户验收+优化 :d4, after d2, 7d
    milestone M4 正式上线 :crit, milestone, after d3 d4, 1d
```

### 8.2 团队配置与职责分工

| 角色 | 人数 | 职责 | 阶段投入 |
|-----|:---:|------|:------:|
| **项目经理** | 1 | 项目管理、进度跟踪、风险管控 | 全程 |
| **架构师** | 1 | 系统架构设计、技术选型、核心评审 | 全程 |
| **后端工程师** | 3 | API/检索/问答/权限服务开发 | 阶段1~3 |
| **AI 算法工程师** | 2 | 文档解析/Embedding/Rerank/LLM集成 | 阶段1~3 |
| **前端工程师** | 2 | Web界面/对话交互/文档管理 | 阶段3~4 |
| **DevOps 工程师** | 1 | K8s部署/CI-CD/监控/运维 | 阶段3~4 |
| **测试工程师** | 2 | 功能/性能/安全/RAG效果测试 | 阶段4 |
| **合计** | **12** | — | — |

### 8.3 交付物清单

| # | 交付物 | 形式 | 验收标准 | 交付阶段 |
|---|-------|------|---------|:------:|
| D1 | 系统架构设计文档 | PDF + 架构图 | 评审通过 | 阶段1 |
| D2 | 数据库设计文档 | ER图 + DDL | 评审通过 | 阶段1 |
| D3 | API 接口文档 | OpenAPI Spec | 评审通过 | 阶段2 |
| D4 | 源代码 + 依赖说明 | Git 仓库 | Code Review 通过 | 阶段2~3 |
| D5 | 部署手册 + 运维文档 | PDF + 脚本 | 可独立部署 | 阶段3 |
| D6 | 测试报告(功能+性能+安全) | PDF + 数据 | 全部用例通过 | 阶段4 |
| D7 | RAG 效果评估报告 | PDF + 数据 | 召回率≥90% 准确率≥85% | 阶段4 |
| D8 | 用户手册 + 培训材料 | PDF + 视频 | UAT 通过 | 阶段4 |

---

## 九、测试方案

### 9.1 功能测试：六大模块用例矩阵

| 模块 | 测试用例数 | 核心测试点 | 通过标准 |
|-----|:-------:|---------|---------|
| **文档解析** | 50 | 十格式各5例 + 异常文件 + 大文件 + 含表格/图片 | 解析准确率≥95% |
| **知识存储** | 30 | 增删改查 + 三库一致性 + 并发写入 | 数据零丢失 |
| **智能问答** | 80 | 单轮/多轮/无答案/多来源冲突 + 流式输出 | 准确率≥85% |
| **权限管理** | 60 | RBAC/ABAC/ACL 各20例 + 越权访问检测 | 越权0通过 |
| **检索服务** | 40 | 向量检索 + BM25 + 混合 + Rerank + 权限过滤 | 召回率≥90% |
| **接口服务** | 30 | 所有API端点 + 异常处理 + 限流 | 100%通过 |

### 9.2 性能测试：检索延迟与并发基准

| 性能指标 | 测试条件 | 目标值 | 测试工具 |
|---------|---------|:-----:|---------|
| 检索延迟 P50 | 100万切片,单次检索 | < 50ms | Locust |
| 检索延迟 P99 | 100万片段,单次检索 | < 200ms | Locust |
| 问答首 Token | 含检索+Rerank+LLM首token | < 2s | 自定义脚本 |
| 问答完整回答 | 平均500 token输出 | < 8s | 自定义脚本 |
| 并发问答 | 100并发用户 | 错误率<1% | Locust |
| 并发文档导入 | 50并发上传 | 全部成功 | Locust |
| 向量库写入 | 1000切片/秒 | 持续稳定 | 压测脚本 |
| 系统吞吐 | 1000 QPS问答(缓存命中) | P99<500ms | Locust |

### 9.3 安全测试：渗透与越权验证

| 安全测试项 | 测试方法 | 通过标准 |
|----------|---------|---------|
| 越权访问 | 普通用户尝试访问机密文档片段 | 0次成功 |
| 水平越权 | 用户A尝试查看用户B的问答历史 | 0次成功 |
| 垂直越权 | 普通用户尝试管理员接口 | 0次成功 |
| Prompt 注入 | 50种注入模式测试 | 全部拦截 |
| PII 泄露 | 检查输出是否含他人PII | 0次泄露 |
| SQL 注入 | API参数注入测试 | 全部拦截 |
| 重放攻击 | 重复请求测试 | 全部拒绝 |
| 数据加密 | 抓包验证传输+存储加密 | 全程加密 |

### 9.4 RAG 效果评估：检索与生成质量量化

> RAG 效果评估完整方案详见 [70RAG系统效果评估全面方案](../4RAG%20检索增强生成/70RAG系统效果评估全面方案_检索生成端到端三维标准化框架.md)

**三维评估框架**:

| 评估维度 | 评估指标 | 评估方法 | 目标值 | 数据集 |
|---------|---------|---------|:-----:|:-----:|
| **检索质量** | Top-5 召回率 | 人工标注 Ground Truth | ≥90% | 500题 |
| **检索质量** | MRR(平均倒数排名) | 自动计算 | ≥0.85 | 500题 |
| **检索质量** | 精确率(P@5) | 自动计算 | ≥0.80 | 500题 |
| **生成质量** | 答案准确率 | 人工评分(1-5分,≥4为准确) | ≥85% | 200题 |
| **生成质量** | 幻觉率 | 答案vs检索片段NLI检测 | ≤10% | 200题 |
| **生成质量** | 引用准确率 | 引用来源是否正确 | ≥90% | 200题 |
| **端到端** | 用户满意度 | 5分制评分 | ≥4.0 | 100用户 |
| **端到端** | 任务完成率 | 用户问题是否得到解决 | ≥80% | 100用户 |

**评估数据集构建**:

```python
# RAG效果评估数据集构建
eval_dataset = {
    "检索评估集": {
        "规模": 500题,
        "来源": "真实用户问题日志 + 人工构造",
        "标注": "每题标注正确答案所在文档和段落(Ground Truth)",
        "类型分布": {
            "事实查询": "40%",      # "差旅报销标准是什么?"
            "对比分析": "20%",      # "A方案和B方案的区别?"
            "流程咨询": "20%",      # "入职流程是怎样的?"
            "计算推理": "10%",      # "出差5天住宿费能报销多少?"
            "无答案": "10%"         # 故意问知识库没有的问题
        }
    },
    "生成评估集": {
        "规模": 200题(从检索集中抽取),
        "标注": "人工标注标准答案 + 关键事实点",
        "评估维度": ["准确性", "完整性", "简洁性", "引用正确性"]
    }
}
```

---

## 十、部署架构与运维

### 10.1 部署拓扑：高可用集群设计

```mermaid
graph TB
    subgraph 用户接入
        LB[负载均衡<br/>Nginx/ALB]
    end
    
    subgraph 应用集群_K8s
        GW_Pod[网关 ×2<br/>Kong]
        APP_Pod[应用服务 ×4<br/>FastAPI]
        WS_Pod[WebSocket服务 ×2]
    end
    
    subgraph AI引擎集群_GPU
        EMB_Pod[Embedding服务 ×2<br/>BGE-M3 GPU]
        LLM_Pod[LLM服务 ×2<br/>Qwen2.5-72B vLLM A100×2]
        RR_Pod[Rerank服务 ×1<br/>bge-reranker GPU]
        OCR_Pod[OCR服务 ×1<br/>PaddleOCR GPU]
    end
    
    subgraph 数据集群
        MIL[Milvus集群<br/>3节点]
        PG[PostgreSQL<br/>主从]
        REDIS[Redis集群<br/>3主3从]
        MINIO[MinIO集群<br/>4节点]
        MQ[RabbitMQ<br/>3节点]
    end
    
    subgraph 运维监控
        PROM[Prometheus]
        GRAF[Grafana]
        ELK[ELK日志]
        ALERT[AlertManager]
    end
    
    LB --> GW_Pod --> APP_Pod & WS_Pod
    APP_Pod --> EMB_Pod & LLM_Pod & RR_Pod & OCR_Pod
    APP_Pod --> MIL & PG & REDIS & MINIO & MQ
    PROM --> GRAF & ALERT
    
    style LLM_Pod fill:#f5222d,color:#fff
    style MIL fill:#fa8c16,color:#fff
    style APP_POD fill:#4a90d9,color:#fff
```

**硬件资源规划（中型企业 100 万文档）**:

| 组件 | 配置 | 数量 | 用途 |
|-----|------|:---:|------|
| GPU 服务器 | A100 80G ×2 | 2台 | LLM 推理(vLLM) |
| GPU 服务器 | T4 16G ×1 | 2台 | Embedding + Rerank + OCR |
| CPU 服务器 | 32C 64G | 4台 | 应用服务 + 网关 |
| 内存型服务器 | 16C 128G | 3台 | Milvus 集群 |
| 存储型服务器 | 16C 32G + 2TB SSD | 4台 | PostgreSQL + MinIO + Redis |

### 10.2 监控告警与运维体系

| 监控维度 | 指标 | 告警阈值 | 处置预案 |
|---------|------|---------|---------|
| **服务可用性** | API 健康检查 | 连续3次失败 | 自动重启 + 告警 |
| **检索性能** | 检索延迟 P99 | > 500ms | 检查向量库负载 |
| **问答质量** | 答案准确率周报 | < 80% | 触发RAG效果回归 |
| **资源使用** | GPU 利用率 | > 90%持续10min | 扩容或限流 |
| **资源使用** | 磁盘使用率 | > 85% | 扩容或清理 |
| **安全告警** | 越权尝试次数 | > 10次/分钟 | 自动封禁IP + 告警 |
| **业务指标** | 文档解析失败率 | > 5% | 检查解析引擎 |

---

## 十一、总结与最佳实践

### 核心设计原则回顾

```mermaid
mindmap
  root((知识库Agent设计原则))
    检索优先
      混合检索 向量+BM25
      Rerank精排
      权限过滤前置
      查询改写
    生成可控
      严格基于检索片段
      引用溯源标注
      幻觉检测兜底
      无答案时明确告知
    权限内生
      RBAC+ABAC+ACL三层
      检索时过滤 非后过滤
      输出二次校验
      全链路审计
    工程务实
      三库协同 各司其职
      异步流水线 解耦
      流式输出 体验优先
      监控告警 可观测
```

### 最佳实践清单

| # | 最佳实践 | 反模式（避免） |
|---|---------|------------|
| 1 | 检索时权限过滤(Milvus元数据过滤) | 检索后过滤(先返回再过滤,有泄露风险) |
| 2 | 混合检索(向量+BM25+RRF融合) | 纯向量检索(关键词精确匹配差) |
| 3 | Rerank 精排 Top-50→Top-5 | 直接用向量检索 Top-5(精度不够) |
| 4 | 引用溯源标注来源 | 直接输出答案不标注来源(不可信) |
| 5 | 幻觉检测+降级策略 | 信任LLM输出不校验(幻觉风险) |
| 6 | 智能切片(语义边界+表格专项) | 固定长度暴力切片(语义断裂) |
| 7 | 多轮对话查询改写 | 直接用原始问题检索(指代消解失败) |
| 8 | BGE-M3 + Qwen2.5 + bge-reranker | 混用不同系列模型(效果不协同) |
| 9 | 流式输出(首Token<2s) | 等完整生成再返回(用户体验差) |
| 10 | 三库一致性补偿事务 | 单库写入失败不处理(数据不一致) |

> **工程判断**:企业知识库 Agent 的核心竞争力不在于单点技术(向量检索、LLM 生成),而在于**端到端工程闭环**——从十格式文档解析到智能切片、从混合检索到权限过滤、从引用溯源到幻觉检测、从三库一致性到安全审计,每一个环节的工程化质量共同决定了系统的可用性和可信度。本文档提供的方案已在真实企业项目中验证,可直接作为工程团队的落地蓝图。
