# A2A（Agent-to-Agent）协议面试题集详解

> 本文档系统梳理 A2A（Agent2Agent）协议的核心概念、架构设计、使用场景、实现难点与未来趋势，并对比 MCP 协议，难度覆盖基础、中级、高级三个层次，题型含概念题、原理题、分析题、设计题。

---

## 目录

- [A2A（Agent-to-Agent）协议面试题集详解](#a2aagent-to-agent协议面试题集详解)
  - [目录](#目录)
  - [一、A2A 技术概念与原理简介](#一a2a-技术概念与原理简介)
    - [1.1 什么是 A2A](#11-什么是-a2a)
    - [1.2 核心特性](#12-核心特性)
    - [1.3 与传统系统的区别](#13-与传统系统的区别)
  - [二、A2A 架构设计要点](#二a2a-架构设计要点)
    - [2.1 核心角色与组件](#21-核心角色与组件)
    - [2.2 通信机制](#22-通信机制)
      - [2.2.1 协议栈](#221-协议栈)
      - [2.2.2 核心方法](#222-核心方法)
      - [2.2.3 Task 状态机](#223-task-状态机)
    - [2.3 数据交互流程](#23-数据交互流程)
      - [2.3.1 完整协作时序](#231-完整协作时序)
      - [2.3.2 任务请求示例](#232-任务请求示例)
      - [2.3.3 任务响应示例](#233-任务响应示例)
    - [2.4 安全策略](#24-安全策略)
  - [三、A2A 三大基础规范详解](#三a2a-三大基础规范详解)
    - [3.1 Agent Card 规范](#31-agent-card-规范)
      - [3.1.1 定义说明](#311-定义说明)
      - [3.1.2 核心要素](#312-核心要素)
      - [3.1.3 技术要求](#313-技术要求)
      - [3.1.4 实现标准](#314-实现标准)
      - [3.1.5 应用场景](#315-应用场景)
    - [3.2 Tasks 规范](#32-tasks-规范)
      - [3.2.1 定义说明](#321-定义说明)
      - [3.2.2 核心要素](#322-核心要素)
      - [3.2.3 技术要求](#323-技术要求)
      - [3.2.4 实现标准](#324-实现标准)
      - [3.2.5 应用场景](#325-应用场景)
    - [3.3 Transport 规范](#33-transport-规范)
      - [3.3.1 定义说明](#331-定义说明)
      - [3.3.2 核心要素](#332-核心要素)
      - [3.3.3 技术要求](#333-技术要求)
      - [3.3.4 实现标准](#334-实现标准)
      - [3.3.5 应用场景](#335-应用场景)
    - [3.4 三大规范协同关系](#34-三大规范协同关系)
  - [四、A2A 工作流程与四大核心能力实现方案](#四a2a-工作流程与四大核心能力实现方案)
    - [4.1 发行能力模块](#41-发行能力模块)
      - [4.1.1 模块定义与定位](#411-模块定义与定位)
      - [4.1.2 数字资产发行流程](#412-数字资产发行流程)
      - [4.1.3 合规校验机制](#413-合规校验机制)
      - [4.1.4 版本控制策略](#414-版本控制策略)
      - [4.1.5 技术选型建议与安全考量](#415-技术选型建议与安全考量)
      - [4.1.6 与其他模块的交互逻辑](#416-与其他模块的交互逻辑)
    - [4.2 认证授权体系](#42-认证授权体系)
      - [4.2.1 模块定义与定位](#421-模块定义与定位)
      - [4.2.2 身份验证流程](#422-身份验证流程)
      - [4.2.3 权限分级模型](#423-权限分级模型)
      - [4.2.4 访问控制策略](#424-访问控制策略)
      - [4.2.5 技术选型建议与安全考量](#425-技术选型建议与安全考量)
      - [4.2.6 与其他模块的交互逻辑](#426-与其他模块的交互逻辑)
    - [4.3 任务委托机制](#43-任务委托机制)
      - [4.3.1 模块定义与定位](#431-模块定义与定位)
      - [4.3.2 委托流程设计](#432-委托流程设计)
      - [4.3.3 责任划分原则](#433-责任划分原则)
      - [4.3.4 委托关系管理](#434-委托关系管理)
      - [4.3.5 技术选型建议与安全考量](#435-技术选型建议与安全考量)
      - [4.3.6 与其他模块的交互逻辑](#436-与其他模块的交互逻辑)
    - [4.4 可观测性方案](#44-可观测性方案)
      - [4.4.1 模块定义与定位](#441-模块定义与定位)
      - [4.4.2 性能指标监控](#442-性能指标监控)
      - [4.4.3 异常检测机制](#443-异常检测机制)
      - [4.4.4 日志记录规范](#444-日志记录规范)
      - [4.4.5 可视化仪表盘设计](#445-可视化仪表盘设计)
      - [4.4.6 技术选型建议与安全考量](#446-技术选型建议与安全考量)
      - [4.4.7 与其他模块的交互逻辑](#447-与其他模块的交互逻辑)
    - [4.5 四大模块协同工作流](#45-四大模块协同工作流)
  - [五、A2A 典型使用场景分析](#五a2a-典型使用场景分析)
    - [5.1 场景一：跨框架多智能体协作](#51-场景一跨框架多智能体协作)
    - [5.2 场景二：跨企业供应链协同](#52-场景二跨企业供应链协同)
    - [5.3 场景三：复杂任务委派](#53-场景三复杂任务委派)
    - [5.4 场景四：人机混合协作](#54-场景四人机混合协作)
  - [六、A2A 技术实现难点与解决方案](#六a2a-技术实现难点与解决方案)
    - [6.1 难点一：异步通信与长任务处理](#61-难点一异步通信与长任务处理)
    - [6.2 难点二：冲突解决机制](#62-难点二冲突解决机制)
    - [6.3 难点三：性能优化](#63-难点三性能优化)
    - [6.4 难点四：错误处理与容错](#64-难点四错误处理与容错)
    - [6.5 难点五：可观测性与调试](#65-难点五可观测性与调试)
  - [七、A2A 未来发展趋势与挑战](#七a2a-未来发展趋势与挑战)
    - [7.1 发展趋势](#71-发展趋势)
    - [7.2 面临的挑战](#72-面临的挑战)
  - [八、A2A vs MCP 对比](#八a2a-vs-mcp-对比)
    - [8.1 定位对比](#81-定位对比)
    - [8.2 核心差异对比表](#82-核心差异对比表)
    - [8.3 互补关系](#83-互补关系)
    - [8.4 选型建议](#84-选型建议)
  - [九、面试题及详解](#九面试题及详解)
    - [题目 1：A2A 定义与核心特性（概念题·基础）](#题目-1a2a-定义与核心特性概念题基础)
    - [题目 2：A2A vs 传统 API 区别（概念题·基础）](#题目-2a2a-vs-传统-api-区别概念题基础)
    - [题目 3：Agent Card 作用与字段（概念题·基础）](#题目-3agent-card-作用与字段概念题基础)
    - [题目 4：Task 状态机流转（原理题·中级）](#题目-4task-状态机流转原理题中级)
    - [题目 5：通信机制与核心方法（原理题·中级）](#题目-5通信机制与核心方法原理题中级)
    - [题目 6：安全策略分层（原理题·中级）](#题目-6安全策略分层原理题中级)
    - [题目 7：跨框架协作场景分析（分析题·中级）](#题目-7跨框架协作场景分析分析题中级)
    - [题目 8：异步通信与长任务处理（分析题·高级）](#题目-8异步通信与长任务处理分析题高级)
    - [题目 9：冲突解决机制设计（设计题·高级）](#题目-9冲突解决机制设计设计题高级)
    - [题目 10：性能优化方案（设计题·高级）](#题目-10性能优化方案设计题高级)
    - [题目 11：容错与故障转移（设计题·高级）](#题目-11容错与故障转移设计题高级)
    - [题目 12：A2A vs MCP 对比与选型（分析题·高级）](#题目-12a2a-vs-mcp-对比与选型分析题高级)
  - [十、考点速查表](#十考点速查表)

---

## 一、A2A 技术概念与原理简介

### 1.1 什么是 A2A

**A2A（Agent2Agent Protocol）** 是 Google 于 2025 年 4 月联合 50+ 合作伙伴推出的**开放协议**，旨在让不同框架（LangGraph/AutoGen/CrewAI 等）、不同厂商构建的 Agent 能够**跨框架、跨平台互相通信与协作**，打破 Agent 生态孤岛。

**一句话定义**：A2A = Agent 间的 HTTP/JSON-RPC 通信标准，让任意 Agent 都能像调用 API 一样调用其他 Agent。

**协议定位**：

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    subgraph 互联网协议栈演进
        HTTP[HTTP<br/>应用间通信]
        API[REST/gRPC<br/>服务间通信]
        MCP[MCP<br/>模型与工具通信]
        A2A[A2A<br/>Agent 间通信]
    end

    HTTP --> API --> MCP --> A2A

    style A2A fill:#fff3e0,stroke:#e65100,stroke-width:3px
    style MCP fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
```

### 1.2 核心特性

| 特性 | 说明 | 价值 |
|------|------|------|
| **框架无关** | 不绑定任何 Agent 框架，LangGraph/AutoGen/CrewAI 均可接入 | 打破生态孤岛 |
| **基于 Web 标准** | HTTP + JSON-RPC 2.0，复用现有基础设施 | 低门槛接入 |
| **Agent Card 自描述** | Agent 通过 JSON 元数据暴露能力，支持动态发现 | 即插即用 |
| **Task 生命周期管理** | Task 有完整状态机（submitted→working→completed） | 可追踪、可恢复 |
| **多模态支持** | Message 由多个 Part 组成（文本/文件/结构化数据） | 支持复杂业务 |
| **流式响应** | 通过 SSE（Server-Sent Events）支持长任务流式输出 | 用户体验好 |
| **推送通知** | 支持 Webhook 回调，无需轮询长任务状态 | 资源高效 |
| **企业级安全** | 支持 OAuth2/API Key/Bearer Token 等标准认证 | 生产可用 |

### 1.3 与传统系统的区别

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart LR
    subgraph 传统API调用
        A1[应用A] -->|硬编码API| A2[应用B]
        A2 -->|固定响应| A1
    end

    subgraph A2A协作
        B1[Agent A] -->|动态任务| B2[Agent B]
        B2 -->|协商/流式/推送| B1
        B1 -.->|发现Agent Card| B2
    end

    style A2 fill:#ffcdd2,stroke:#c62828
    style B2 fill:#c8e6c9,stroke:#2e7d32
```

| 维度 | 传统 API 调用 | A2A 协作 |
|------|--------------|----------|
| **调用方** | 应用 A 硬编码调用应用 B | Agent A 动态发现并调用 Agent B |
| **接口定义** | OpenAPI/Swagger 固定 Schema | Agent Card 自描述，可动态发现 |
| **交互模式** | 请求-响应，同步为主 | 任务驱动，支持流式/推送/长任务 |
| **响应内容** | 固定 JSON 结构 | 多模态 Message（文本+文件+数据） |
| **状态管理** | 无状态，每次独立 | Task 有完整生命周期状态机 |
| **错误处理** | HTTP 状态码 | Task 状态（failed/canceled）+ 错误对象 |
| **发现机制** | 需提前知道端点 | Agent Card 自动发现能力 |
| **协作深度** | 单次调用 | 多轮协商、子任务委派 |

---

## 二、A2A 架构设计要点

### 2.1 核心角色与组件

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    subgraph A2A核心角色
        CA[Client Agent<br/>发起方Agent]
        RA[Remote Agent<br/>被调用Agent]
    end

    subgraph 核心组件
        AC[Agent Card<br/>能力自描述]
        TK[Task<br/>任务生命周期]
        MSG[Message<br/>多模态消息]
        PT[Part<br/>内容片段]
        AR[Artifact<br/>任务产出]
    end

    CA -->|创建Task| RA
    RA -->|返回Artifact| CA
    RA -.->|暴露| AC
    CA -.->|发现| AC
    TK --> MSG
    MSG --> PT
    TK --> AR

    style CA fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style RA fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style AC fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
```

| 组件 | 定义 | 关键字段 |
|------|------|----------|
| **Agent Card** | Agent 的自描述 JSON，暴露能力与端点 | `name`, `description`, `url`, `skills`, `authentication` |
| **Task** | 协作的基本单位，有生命周期 | `id`, `status`, `messages`, `artifacts` |
| **Message** | Task 中的多模态消息 | `role`(user/agent), `parts[]` |
| **Part** | Message 的内容片段 | `text` / `file` / `data` |
| **Artifact** | Task 的产出物 | `name`, `parts[]` |

**Agent Card 示例**：

```json
{
  "name": "code-review-agent",
  "description": "自动化代码审查 Agent,支持多语言",
  "url": "https://agent.example.com/a2a",
  "version": "1.0.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true
  },
  "skills": [
    {
      "id": "review_python",
      "name": "Python 代码审查",
      "description": "审查 Python 代码质量、规范、安全",
      "tags": ["python", "code-review", "security"]
    },
    {
      "id": "review_java",
      "name": "Java 代码审查",
      "description": "审查 Java 代码规范与潜在 Bug",
      "tags": ["java", "code-review"]
    }
  ],
  "authentication": {
    "schemes": ["Bearer", "OAuth2"]
  },
  "defaultInputModes": ["text", "file"],
  "defaultOutputModes": ["text", "file"]
}
```

### 2.2 通信机制

#### 2.2.1 协议栈

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart LR
    subgraph A2A协议栈
        L5[JSON-RPC 2.0<br/>消息格式]
        L4[HTTP/HTTPS<br/>传输层]
        L3[SSE / Webhook<br/>流式与推送]
        L2[OAuth2/API Key<br/>认证层]
        L1[Agent Card<br/>发现层]
    end

    L1 --> L2 --> L4 --> L5
    L4 --> L3
```

#### 2.2.2 核心方法

| JSON-RPC 方法 | 用途 | 模式 |
|---------------|------|------|
| `tasks/send` | 发送任务（同步返回结果） | 请求-响应 |
| `tasks/sendSubscribe` | 发送任务并订阅流式更新 | SSE 流式 |
| `tasks/get` | 查询任务状态 | 请求-响应 |
| `tasks/cancel` | 取消任务 | 请求-响应 |
| `tasks/pushNotificationSet` | 设置 Webhook 回调地址 | 请求-响应 |
| `tasks/resubscribe` | 重新订阅已断开的流 | SSE 流式 |

#### 2.2.3 Task 状态机

```mermaid
%%{init: {'theme':'neutral'}}%%
stateDiagram-v2
    [*] --> submitted: tasks/send
    submitted --> working: Agent 开始处理
    working --> input_required: 需用户补充信息
    input_required --> working: 用户提供信息
    working --> completed: 成功完成
    working --> failed: 处理失败
    working --> canceled: tasks/cancel
    submitted --> canceled: tasks/cancel
    completed --> [*]
    failed --> [*]
    canceled --> [*]
```

| 状态 | 含义 | Client 动作 |
|------|------|-------------|
| `submitted` | 任务已提交，未开始 | 等待 |
| `working` | Agent 处理中 | 流式接收或轮询 |
| `input_required` | 需用户补充信息 | 收集输入并 `tasks/send` |
| `completed` | 成功完成 | 读取 Artifact |
| `failed` | 处理失败 | 读取错误信息 |
| `canceled` | 已取消 | 终止 |

### 2.3 数据交互流程

#### 2.3.1 完整协作时序

```mermaid
%%{init: {'theme':'neutral'}}%%
sequenceDiagram
    participant CA as Client Agent
    participant RA as Remote Agent
    participant WH as Webhook(可选)

    Note over CA,RA: 1. 发现阶段
    CA->>RA: GET /.well-known/agent.json
    RA-->>CA: Agent Card(能力+端点)

    Note over CA,RA: 2. 认证阶段
    CA->>CA: 获取 OAuth2 Token
    CA->>RA: 请求(带 Bearer Token)

    Note over CA,RA: 3. 任务发起(流式)
    CA->>RA: tasks/sendSubscribe(任务)
    RA-->>CA: SSE: status=working
    RA-->>CA: SSE: 进度更新1
    RA-->>CA: SSE: 进度更新2

    Note over CA,RA: 4. 需要补充输入
    RA-->>CA: SSE: status=input_required
    CA->>RA: tasks/send(补充输入)
    RA-->>CA: SSE: status=working

    Note over CA,RA: 5. 完成
    RA-->>CA: SSE: status=completed + Artifact
    CA->>CA: 处理产出
```

#### 2.3.2 任务请求示例

```json
{
  "jsonrpc": "2.0",
  "method": "tasks/send",
  "id": "req-001",
  "params": {
    "id": "task-12345",
    "message": {
      "role": "user",
      "parts": [
        {"text": "审查这段 Python 代码"},
        {"file": {"mimeType": "text/x-python", "data": "base64..."}}
      ]
    }
  }
}
```

#### 2.3.3 任务响应示例

```json
{
  "jsonrpc": "2.0",
  "id": "req-001",
  "result": {
    "id": "task-12345",
    "status": {"state": "completed"},
    "artifacts": [
      {
        "name": "审查报告",
        "parts": [
          {"text": "发现 3 个问题:1...."},
          {"data": {"issues": 3, "severity": "high", "json": "..."}}
        ]
      }
    ]
  }
}
```

### 2.4 安全策略

| 安全层 | 机制 | 说明 |
|--------|------|------|
| **认证** | OAuth2 / API Key / Bearer Token | Agent Card 声明支持的 schemes |
| **授权** | Scope / Role-Based | 限制 Agent 可访问的资源 |
| **传输** | HTTPS 强制 | 防止中间人攻击 |
| **输入校验** | JSON Schema 校验 Message | 防 Prompt 注入、参数篡改 |
| **速率限制** | Rate Limiting | 防滥用、防 DoS |
| **审计** | 全量 Task 日志 | 满足合规审计 |
| **隔离** | Agent 沙箱执行 | 防恶意代码执行 |

---

## 三、A2A 三大基础规范详解

> A2A 协议的核心由 **Agent Card 规范**、**Tasks 规范**、**Transport 规范** 三大基础规范构成。Agent Card 规范解决"如何发现 Agent 并了解其能力"的问题，Tasks 规范解决"如何发起并管理 Agent 间协作任务"的问题，Transport 规范解决"如何在网络上可靠传输通信内容"的问题。三者相互配合，共同构成 A2A 协议的完整技术底座。本章从**定义说明、核心要素、技术要求、实现标准、应用场景**五个维度逐规范展开。

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    subgraph A2A三大基础规范
        AC[Agent Card 规范<br/>能力发现层]
        TK[Tasks 规范<br/>任务协作层]
        TR[Transport 规范<br/>通信传输层]
    end

    AC -->|发现后建立协作| TK
    TK -->|基于传输通道执行| TR
    TR -->|承载发现与任务通信| AC
    TR -->|承载| TK

    style AC fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    style TK fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style TR fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
```

| 规范 | 解决问题 | 核心抽象 | 层级定位 |
|------|----------|----------|----------|
| **Agent Card 规范** | 如何发现 Agent、了解能力 | Agent Card JSON 元数据 | 能力发现层 |
| **Tasks 规范** | 如何协作、管理任务生命周期 | Task / Message / Artifact | 任务协作层 |
| **Transport 规范** | 如何传输、保证可靠通信 | HTTP + JSON-RPC + SSE + Webhook | 通信传输层 |

### 3.1 Agent Card 规范

#### 3.1.1 定义说明

**Agent Card** 是 A2A 协议中 Agent 的**自描述元数据文件**，采用 JSON 格式，遵循 RFC 8615 的 Well-Known URI 约定，标准托管路径为 `/.well-known/agent.json`。它是 A2A **能力发现机制**的核心载体，使得 Client Agent 无需预先硬编码配置即可动态发现任意 Remote Agent 的身份、能力、端点与认证方式。

Agent Card 的设计理念类比于 Web 世界的 `robots.txt` 与 OpenAPI 的 `swagger.json`：前者约定爬虫访问规则，后者描述 API 接口规范，而 Agent Card 则描述"**Agent 是谁、能做什么、如何调用**"三大问题。通过标准化自描述，A2A 实现了 Agent 的即插即用与跨框架互操作。

```mermaid
%%{init: {'theme':'neutral'}}%%
sequenceDiagram
    participant CA as Client Agent
    participant RA as Remote Agent

    Note over CA,RA: Agent Card 发现流程
    CA->>RA: GET /.well-known/agent.json
    RA-->>CA: 200 OK + Agent Card(JSON)
    Note over CA: 解析能力(skills)<br/>确认端点(url)<br/>选择认证方式
    CA->>CA: 能力匹配决策
    CA->>RA: 按认证方式发起 Task
```

#### 3.1.2 核心要素

Agent Card 由若干结构化字段构成，分为**基础信息、能力声明、技能列表、认证配置、输入输出模式**五大类要素：

| 要素类别 | 字段 | 类型 | 必填 | 说明 |
|----------|------|------|------|------|
| **基础信息** | `name` | string | 是 | Agent 的人类可读名称 |
| **基础信息** | `description` | string | 否 | Agent 功能概述，供 Client 理解用途 |
| **基础信息** | `url` | string | 是 | Agent 的 A2A 服务端点（接收 JSON-RPC 请求） |
| **基础信息** | `version` | string | 否 | Agent 版本号（语义化版本） |
| **基础信息** | `protocolVersion` | string | 是 | 支持的 A2A 协议版本 |
| **能力声明** | `capabilities.streaming` | boolean | 否 | 是否支持 SSE 流式响应 |
| **能力声明** | `capabilities.pushNotifications` | boolean | 否 | 是否支持 Webhook 推送通知 |
| **技能列表** | `skills[]` | array | 是 | Agent 能力清单，每项含 id/name/description/tags |
| **技能列表** | `skills[].id` | string | 是 | 技能唯一标识 |
| **技能列表** | `skills[].tags[]` | array | 否 | 技能标签，便于能力匹配检索 |
| **技能列表** | `skills[].examples[]` | array | 否 | 调用示例，辅助 LLM 理解用法 |
| **认证配置** | `authentication.schemes[]` | array | 否 | 支持的认证方案（Bearer/OAuth2/API Key） |
| **输入输出** | `defaultInputModes` | array | 否 | 默认输入模式（text/file/data） |
| **输入输出** | `defaultOutputModes` | array | 否 | 默认输出模式（text/file/data） |

**技能（Skill）结构详解**：

技能是 Agent Card 中描述 Agent 能力的最小单元，Client Agent 通过匹配技能标签决定是否调用该 Agent。

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart LR
    subgraph Skill结构
        S1[id<br/>唯一标识]
        S2[name<br/>技能名称]
        S3[description<br/>详细描述]
        S4[tags[]<br/>标签集合]
        S5[examples[]<br/>调用示例]
    end

    S1 --> S4
    S4 -->|Client 匹配检索| Match[能力匹配]

    style S1 fill:#e3f2fd,stroke:#1565c0
    style Match fill:#c8e6c9,stroke:#2e7d32
```

#### 3.1.3 技术要求

Agent Card 规范对实现方提出以下技术要求：

| 要求类别 | 具体要求 | 说明 |
|----------|----------|------|
| **托管路径** | 必须托管于 `/.well-known/agent.json` | 遵循 RFC 8615，Client 可固定路径发现 |
| **访问协议** | 必须支持 HTTPS GET 请求 | 跨网络安全访问，禁止仅 HTTP |
| **响应格式** | Content-Type 必须为 `application/json` | 标准 JSON 响应，UTF-8 编码 |
| **无需认证** | Agent Card 的 GET 请求不应要求认证 | 发现阶段尚未建立认证，需公开可读 |
| **字段约束** | `name`、`url`、`protocolVersion` 为必填 | 缺失则 Client 无法正常调用 |
| **版本兼容** | `protocolVersion` 需声明支持的协议大版本 | Client 据此判断兼容性 |
| **技能描述** | `skills` 至少包含一项 | 空 skills 的 Agent 无法被能力匹配 |
| **扩展性** | 允许自定义扩展字段（以 `x-` 前缀） | 满足企业定制需求，不破坏标准 |

#### 3.1.4 实现标准

**完整 Agent Card JSON 示例**：

```json
{
  "name": "code-review-agent",
  "description": "自动化代码审查 Agent，支持多语言代码质量、规范与安全检查",
  "url": "https://agent.example.com/a2a",
  "version": "1.2.0",
  "protocolVersion": "0.3.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true
  },
  "skills": [
    {
      "id": "review_python",
      "name": "Python 代码审查",
      "description": "审查 Python 代码质量、PEP8 规范、安全漏洞",
      "tags": ["python", "code-review", "security", "lint"],
      "examples": ["审查这段 Python 代码的潜在 Bug", "检查代码是否符合 PEP8"]
    },
    {
      "id": "review_java",
      "name": "Java 代码审查",
      "description": "审查 Java 代码规范、空指针风险、并发问题",
      "tags": ["java", "code-review", "concurrency"],
      "examples": ["审查 Java 服务的并发安全性"]
    }
  ],
  "authentication": {
    "schemes": ["Bearer", "OAuth2"]
  },
  "defaultInputModes": ["text", "file"],
  "defaultOutputModes": ["text", "file", "data"]
}
```

**Agent Card 服务端实现示例**：

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

AGENT_CARD = {
    "name": "code-review-agent",
    "description": "自动化代码审查 Agent",
    "url": "https://agent.example.com/a2a",
    "version": "1.2.0",
    "protocolVersion": "0.3.0",
    "capabilities": {"streaming": True, "pushNotifications": True},
    "skills": [
        {"id": "review_python", "name": "Python 代码审查",
         "description": "审查 Python 代码", "tags": ["python", "code-review"]}
    ],
    "authentication": {"schemes": ["Bearer", "OAuth2"]},
    "defaultInputModes": ["text", "file"],
    "defaultOutputModes": ["text", "file", "data"],
}

@app.get("/.well-known/agent.json")
async def get_agent_card():
    """暴露 Agent Card，无需认证"""
    return JSONResponse(
        content=AGENT_CARD,
        media_type="application/json",
        headers={"Cache-Control": "public, max-age=3600"}
    )
```

#### 3.1.5 应用场景

| 应用场景 | 说明 | Agent Card 的作用 |
|----------|------|-------------------|
| **动态能力发现** | Client Agent 运行时发现可用 Agent | 通过 GET `/.well-known/agent.json` 获取能力清单 |
| **能力匹配与路由** | Client 根据任务需求选择最合适的 Agent | 匹配 `skills[].tags` 与任务关键词 |
| **Agent 市场注册** | Agent 上架到 Agent 市场/注册中心 | 提交 Agent Card 作为能力描述与索引依据 |
| **版本协商** | Client 判断 Agent 协议版本是否兼容 | 读取 `protocolVersion` 与 `version` 字段 |
| **认证方式选择** | Client 按声明方式准备认证凭证 | 读取 `authentication.schemes` 选择认证流程 |
| **多 Agent 编排** | 编排器动态组合多个 Agent 完成复杂任务 | 发现各 Agent 的 skills 后构建协作 DAG |

---

### 3.2 Tasks 规范

#### 3.2.1 定义说明

**Tasks 规范** 定义了 A2A 协议中 Agent 间协作的基本单位——**Task（任务）**。一个 Task 代表 Client Agent 向 Remote Agent 发起的一次协作请求，具有**完整的生命周期状态机**、**多轮消息交互**与**结构化产出**能力。

与传统的无状态 API 调用不同，A2A 的 Task 是**有状态、可追踪、可恢复**的：每个 Task 拥有唯一 ID，经历从提交到终止的完整状态流转，支持流式进度更新、补充输入、取消、查询与推送通知。Tasks 规范是 A2A 支持**长任务处理**与**多轮协作**的关键基础。

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    subgraph Task组成结构
        T[Task]
        T --> ID[id<br/>唯一标识]
        T --> SID[sessionId<br/>会话标识]
        T --> ST[status<br/>状态机]
        T --> MSG[messages[]<br/>消息历史]
        T --> ART[artifacts[]<br/>产出物]
    end

    subgraph Message结构
        M[Message]
        M --> ROLE[role<br/>user/agent]
        M --> P[parts[]<br/>内容片段]
    end

    subgraph Part类型
        P --> PT[text<br/>文本]
        P --> PF[file<br/>文件]
        P --> PD[data<br/>结构化数据]
    end

    T -.->|包含| M

    style T fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style M fill:#e3f2fd,stroke:#1565c0
    style P fill:#e8f5e9,stroke:#2e7d32
```

#### 3.2.2 核心要素

Tasks 规范的核心要素包括**任务对象、状态机、消息、内容片段、产出物**五大要素：

| 核心要素 | 定义 | 关键属性 |
|----------|------|----------|
| **Task** | 协作的基本单位 | `id`（唯一）、`sessionId`、`status`、`messages[]`、`artifacts[]` |
| **TaskStatus** | 任务当前状态 | `state`（状态枚举）、`timestamp`、`message`（可选状态说明） |
| **Message** | Task 中的多模态消息 | `role`（user/agent）、`parts[]`（内容片段数组） |
| **Part** | Message 的内容片段 | 三种类型：`text`（文本）、`file`（文件）、`data`（结构化 JSON） |
| **Artifact** | Task 的产出物 | `name`（产出名称）、`parts[]`（产出内容片段） |

**Task 状态机（完整状态流转）**：

```mermaid
%%{init: {'theme':'neutral'}}%%
stateDiagram-v2
    [*] --> submitted: tasks/send 创建任务
    submitted --> working: Agent 接收并开始处理
    submitted --> canceled: tasks/cancel
    working --> input_required: 需用户补充信息
    input_required --> working: 用户提供输入(tasks/send)
    working --> completed: 处理成功
    working --> failed: 处理失败
    working --> canceled: tasks/cancel
    completed --> [*]
    failed --> [*]
    canceled --> [*]
```

| 状态 | 含义 | Client 对应动作 | 是否终态 |
|------|------|------------------|----------|
| `submitted` | 任务已提交，Agent 尚未开始处理 | 等待或轮询 | 否 |
| `working` | Agent 正在处理任务 | 流式接收进度或轮询 | 否 |
| `input_required` | Agent 需要用户补充信息才能继续 | 收集输入并 `tasks/send` 继续 | 否 |
| `completed` | 任务成功完成 | 读取 `artifacts` 产出物 | 是 |
| `failed` | 任务处理失败 | 读取错误信息，决定重试或降级 | 是 |
| `canceled` | 任务被取消 | 终止处理流程 | 是 |

#### 3.2.3 技术要求

| 要求类别 | 具体要求 | 说明 |
|----------|----------|------|
| **唯一标识** | 每个 Task 必须有全局唯一 `id` | 由 Client 生成或 Server 生成，确保跨 Agent 不冲突 |
| **状态机约束** | 状态只能按合法路径流转 | 终态（completed/failed/canceled）后不可再变更 |
| **幂等性** | 相同 `id` 的重复提交应幂等处理 | 防网络重试导致重复执行 |
| **持久化** | Task 状态与消息历史应持久化存储 | 支持断线后 `tasks/get` 查询与恢复 |
| **并发控制** | 同一 Task 的并发更新需版本控制 | 乐观锁防并发写冲突 |
| **多轮支持** | `input_required` 支持多轮消息交互 | 消息历史 `messages[]` 累积保存 |
| **超时处理** | 长时间无进展的 Task 应有超时机制 | 防 Resource 泄漏，支持自动 `failed` |
| **取消安全** | `tasks/cancel` 应能安全终止正在执行的任务 | 释放资源，状态转为 `canceled` |

#### 3.2.4 实现标准

**Tasks 规范定义的 6 个核心 JSON-RPC 方法**：

| 方法 | 用途 | 交互模式 | 请求参数 | 返回结果 |
|------|------|----------|----------|----------|
| `tasks/send` | 发送任务（同步返回结果） | 请求-响应 | `id`, `message`, `sessionId?` | Task 对象（含状态与产出） |
| `tasks/sendSubscribe` | 发送任务并订阅流式更新 | SSE 流式 | `id`, `message`, `sessionId?` | SSE 事件流（进度 + 最终结果） |
| `tasks/get` | 查询任务当前状态 | 请求-响应 | `id`, `historyLength?` | Task 对象（含状态与历史） |
| `tasks/cancel` | 取消任务 | 请求-响应 | `id` | Task 对象（status=canceled） |
| `tasks/pushNotificationSet` | 设置 Webhook 回调地址 | 请求-响应 | `id`, `pushNotificationConfig` | 确认结果 |
| `tasks/resubscribe` | 重新订阅已断开的流 | SSE 流式 | `id` | SSE 事件流（恢复订阅） |

**Task 对象标准结构**：

```json
{
  "id": "task-12345",
  "sessionId": "session-67890",
  "status": {
    "state": "completed",
    "timestamp": "2026-08-01T10:30:00Z",
    "message": null
  },
  "messages": [
    {
      "role": "user",
      "parts": [
        {"text": "审查这段 Python 代码"},
        {"file": {"mimeType": "text/x-python", "data": "base64encoded..."}}
      ]
    },
    {
      "role": "agent",
      "parts": [
        {"text": "已完成审查，发现 3 个问题"}
      ]
    }
  ],
  "artifacts": [
    {
      "name": "审查报告",
      "parts": [
        {"text": "## 代码审查报告\n1. 第12行：未处理异常..."},
        {"data": {"issues": 3, "severity": "high", "details": ["..."]}}
      ]
    }
  ]
}
```

**Task 管理器实现示例**：

```python
import asyncio
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class TaskStatus:
    """任务状态"""
    state: str                          # submitted/working/input_required/completed/failed/canceled
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    message: Optional[dict] = None      # 可选的状态说明消息

@dataclass
class Task:
    """A2A 任务对象"""
    id: str
    session_id: str
    status: TaskStatus
    messages: list = field(default_factory=list)     # 消息历史
    artifacts: list = field(default_factory=list)    # 产出物
    version: int = 1                                 # 乐观锁版本号

# 合法状态流转映射
VALID_TRANSITIONS = {
    "submitted":       {"working", "canceled"},
    "working":         {"input_required", "completed", "failed", "canceled"},
    "input_required":  {"working", "canceled"},
    "completed":       set(),   # 终态
    "failed":          set(),   # 终态
    "canceled":        set(),   # 终态
}

class TaskManager:
    """Task 管理器：状态机 + 乐观并发控制"""

    def __init__(self):
        self._tasks: dict[str, Task] = {}

    async def create_task(self, task_id: str, session_id: str, message: dict) -> Task:
        """创建新任务"""
        if task_id in self._tasks:
            return self._tasks[task_id]  # 幂等：已存在则返回现有
        task = Task(
            id=task_id,
            session_id=session_id,
            status=TaskStatus(state="submitted"),
            messages=[message],
        )
        self._tasks[task_id] = task
        return task

    async def update_state(self, task_id: str, new_state: str,
                            expected_version: int) -> Task:
        """状态流转（带状态机校验 + 乐观锁）"""
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"Task 不存在: {task_id}")

        # 1. 乐观锁校验
        if task.version != expected_version:
            raise ConflictError(
                f"版本冲突: 期望 {expected_version}, 实际 {task.version}"
            )

        # 2. 状态机校验
        current = task.status.state
        if new_state not in VALID_TRANSITIONS.get(current, set()):
            raise InvalidTransitionError(
                f"非法状态流转: {current} → {new_state}"
            )

        # 3. 更新状态
        task.status = TaskStatus(state=new_state)
        task.version += 1
        return task

    async def get_task(self, task_id: str, history_length: int = 0) -> Task:
        """查询任务（可限制消息历史长度）"""
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"Task 不存在: {task_id}")
        if history_length > 0:
            task.messages = task.messages[-history_length:]
        return task

    async def cancel_task(self, task_id: str) -> Task:
        """取消任务"""
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"Task 不存在: {task_id}")
        current = task.status.state
        if current in ("completed", "failed", "canceled"):
            raise InvalidTransitionError(f"终态任务不可取消: {current}")
        task.status = TaskStatus(state="canceled")
        task.version += 1
        return task
```

#### 3.2.5 应用场景

| 应用场景 | Task 规范的作用 | 关键特性 |
|----------|----------------|----------|
| **长任务处理** | 代码审查、数据分析等耗时任务 | 状态机 + SSE 流式 + Webhook 推送 |
| **多轮交互协作** | Agent 处理中需用户补充信息 | `input_required` 状态 + 消息历史累积 |
| **任务委派** | PM Agent 委派子任务给专业 Agent | Task ID 追踪 + Artifact 产出回收 |
| **异步通知** | 任务完成无需轮询 | `tasks/pushNotificationSet` Webhook 回调 |
| **任务恢复** | 网络中断后恢复协作 | `tasks/get` 查询状态 + `tasks/resubscribe` 恢复流 |
| **审计追溯** | 合规审计需完整协作记录 | `messages[]` 全量消息历史持久化 |
| **并发协作** | 多 Client 同时调用同一 Agent | 乐观锁版本控制防冲突 |

---

### 3.3 Transport 规范

#### 3.3.1 定义说明

**Transport 规范** 定义了 A2A 协议的底层通信传输机制，规定 Agent 间如何通过网络可靠地交换 JSON-RPC 消息。A2A 的 Transport 规范基于成熟的 **Web 标准**构建——以 **HTTP/HTTPS** 为传输层、**JSON-RPC 2.0** 为消息格式、**SSE（Server-Sent Events）** 为流式推送机制、**Webhook** 为异步回调机制。

Transport 规范的设计哲学是"**复用而非重建**"：不发明新协议，而是基于 Web 生态已有基础设施，让 A2A 能穿透现有防火墙、负载均衡、API 网关，实现零改造接入企业网络环境。

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    subgraph Transport规范四层
        direction TB
        L1[传输协议层<br/>HTTP/HTTPS]
        L2[消息格式层<br/>JSON-RPC 2.0]
        L3[流式推送层<br/>SSE Server-Sent Events]
        L4[异步回调层<br/>Webhook]
    end

    L1 --> L2
    L1 --> L3
    L1 --> L4

    style L1 fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style L2 fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style L3 fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style L4 fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
```

#### 3.3.2 核心要素

| 核心要素 | 定义 | 关键属性 |
|----------|------|----------|
| **HTTP/HTTPS 传输** | 所有 A2A 通信基于 HTTP 协议 | 强制 HTTPS（生产环境）；支持 HTTP/1.1 与 HTTP/2 |
| **JSON-RPC 2.0 消息** | 请求与响应的标准消息格式 | `jsonrpc`、`method`、`params`、`id`、`result`/`error` |
| **SSE 流式推送** | 长任务的实时进度更新机制 | `text/event-stream`；单向服务器推送；自动重连 |
| **Webhook 回调** | 任务状态变更的异步通知机制 | Client 注册 URL；Server POST 推送状态变更 |
| **内容编码** | 消息体的编码与压缩 | UTF-8 编码；支持 Gzip/Brotli 压缩 |
| **认证传输** | 认证凭证的传递方式 | Authorization Header（Bearer Token / OAuth2） |

**三种传输模式对比**：

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart LR
    subgraph 同步模式
        C1[Client] -->|HTTP POST<br/>tasks/send| S1[Server]
        S1 -->|JSON Response<br/>最终结果| C1
    end

    subgraph 流式模式
        C2[Client] -->|HTTP POST<br/>tasks/sendSubscribe| S2[Server]
        S2 -->|SSE: working 进度1| C2
        S2 -->|SSE: working 进度2| C2
        S2 -->|SSE: completed 结果| C2
    end

    subgraph 异步模式
        C3[Client] -->|HTTP POST<br/>tasks/send + 注册Webhook| S3[Server]
        S3 -->|JSON: submitted| C3
        S3 -.->|Webhook POST<br/>状态变更通知| C3
    end
```

#### 3.3.3 技术要求

| 要求类别 | 具体要求 | 说明 |
|----------|----------|------|
| **传输安全** | 生产环境必须使用 HTTPS | 防中间人攻击，TLS 1.2+ |
| **消息格式** | 请求体必须为 JSON-RPC 2.0 格式 | Content-Type: `application/json` |
| **SSE 编码** | SSE 流必须为 `text/event-stream` | UTF-8 编码，`data:` 前缀分帧 |
| **幂等性** | 相同 `id` 的重复请求应幂等 | 防网络重试导致重复执行 |
| **超时控制** | Server 应设置合理的请求超时 | 同步请求 30-60s；SSE 长连接按需保活 |
| **连接复用** | 鼓励 HTTP Keep-Alive 连接复用 | 减少 TCP 握手开销 |
| **压缩传输** | 鼓励启用 Gzip/Brotli 压缩 | 大 JSON 消息体带宽降低 70% |
| **错误码标准** | 遵循 JSON-RPC 2.0 错误码规范 | 预定义错误码 + 业务扩展错误码 |
| **Webhook 验证** | Webhook 回调需带验证 Token | 防伪造回调，`X-Agent-Token` Header 校验 |

**JSON-RPC 2.0 标准消息结构**：

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart LR
    subgraph 请求消息
        R[Request]
        R --> R1["jsonrpc: '2.0'"]
        R --> R2["method: 'tasks/send'"]
        R --> R3["params: {任务参数}"]
        R --> R4["id: 'req-001'"]
    end

    subgraph 成功响应
        S[Response]
        S --> S1["jsonrpc: '2.0'"]
        S --> S2["result: {任务结果}"]
        S --> S3["id: 'req-001'"]
    end

    subgraph 错误响应
        E[Error Response]
        E --> E1["jsonrpc: '2.0'"]
        E --> E2["error: {code, message, data}"]
        E --> E3["id: 'req-001'"]
    end

    R -.->|处理成功| S
    R -.->|处理失败| E

    style R fill:#e3f2fd,stroke:#1565c0
    style S fill:#e8f5e9,stroke:#2e7d32
    style E fill:#ffcdd2,stroke:#c62828
```

#### 3.3.4 实现标准

**标准 JSON-RPC 请求示例**：

```http
POST /a2a HTTP/1.1
Host: agent.example.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
Accept: application/json, text/event-stream

{
  "jsonrpc": "2.0",
  "method": "tasks/send",
  "id": "req-001",
  "params": {
    "id": "task-12345",
    "sessionId": "session-67890",
    "message": {
      "role": "user",
      "parts": [
        {"text": "审查这段 Python 代码"},
        {"file": {"mimeType": "text/x-python", "data": "aW1wb3J0IG9z..."}}
      ]
    }
  }
}
```

**SSE 流式响应示例**：

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

data: {"id":"task-12345","status":{"state":"working"},"message":{"role":"agent","parts":[{"text":"开始分析代码..."}]}}

data: {"id":"task-12345","status":{"state":"working"},"message":{"role":"agent","parts":[{"text":"发现 2 个潜在问题..."}]}}

data: {"id":"task-12345","status":{"state":"completed"},"artifacts":[{"name":"审查报告","parts":[{"text":"审查完成，共 3 个问题"}]}]}
```

**JSON-RPC 错误码标准**：

| 错误码 | 含义 | 触发场景 | 处理建议 |
|--------|------|----------|----------|
| `-32700` | Parse Error（解析错误） | 请求体非合法 JSON | 检查请求格式 |
| `-32600` | Invalid Request（无效请求） | 不符合 JSON-RPC 2.0 规范 | 检查必填字段 |
| `-32601` | Method Not Found（方法不存在） | method 不在 6 个核心方法内 | 检查方法名拼写 |
| `-32602` | Invalid Params（参数无效） | 参数缺失或类型错误 | 校验参数 Schema |
| `-32603` | Internal Error（内部错误） | Agent 内部处理异常 | 指数退避重试 |
| `-32001` | 认证失败 | Token 无效或过期 | 刷新 Token 重试 |
| `-32002` | 授权不足 | 权限不足访问该技能 | 降级或申请权限 |
| `-32003` | Task Not Found | 查询的 Task ID 不存在 | 检查 ID 或重新创建 |
| `-32004` | Task Not Cancellable | 终态任务不可取消 | 检查任务当前状态 |

**Transport 客户端实现示例**：

```python
import httpx
import json
import uuid
from typing import AsyncIterator

class A2ATransportClient:
    """A2A 传输层客户端：封装同步/流式/Webhook 三种模式"""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "Accept": "application/json, text/event-stream",
        }

    async def send_sync(self, method: str, params: dict) -> dict:
        """同步请求-响应模式"""
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "id": str(uuid.uuid4()),
            "params": params,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                self.base_url, json=request, headers=self.headers
            )
            resp.raise_for_status()
            data = resp.json()
            if "error" in data:
                raise A2AError(data["error"])
            return data["result"]

    async def send_streaming(self, method: str, params: dict) -> AsyncIterator[dict]:
        """SSE 流式订阅模式"""
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "id": str(uuid.uuid4()),
            "params": params,
        }
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST", self.base_url, json=request, headers=self.headers
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        yield json.loads(line[6:])


class A2AError(Exception):
    """A2A 协议错误"""
    def __init__(self, error: dict):
        self.code = error.get("code")
        self.message = error.get("message")
        self.data = error.get("data")
        super().__init__(f"[{self.code}] {self.message}")
```

#### 3.3.5 应用场景

| 应用场景 | 传输模式 | 说明 |
|----------|----------|------|
| **即时查询** | 同步（`tasks/send`） | 库存查询、状态查询等秒级返回的任务 |
| **长任务流式** | SSE（`tasks/sendSubscribe`） | 代码审查、报告生成等需实时展示进度的任务 |
| **超长任务异步** | Webhook（`tasks/pushNotificationSet`） | 模型训练、批处理等小时级任务 |
| **断线恢复** | 重订阅（`tasks/resubscribe`） | 网络中断后恢复 SSE 流，不丢失进度 |
| **跨企业通信** | HTTPS + OAuth2 | 跨组织 Agent 协作，穿透企业防火墙 |
| **高并发场景** | 连接池 + 压缩 | 大量并发 Task 调用，连接复用与带宽优化 |
| **移动端/弱网** | Webhook 异步 | 移动设备不稳定连接，用 Webhook 推送最终结果 |

**三种传输模式选型决策**：

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TD
    Start[任务传输选型] --> Q1{任务耗时?}

    Q1 -->|秒级| Sync[同步模式<br/>tasks/send]
    Q1 -->|分钟级| Q2{需实时进度?}
    Q1 -->|小时级| Webhook[Webhook 模式<br/>pushNotificationSet]

    Q2 -->|是| SSE[SSE 流式<br/>sendSubscribe]
    Q2 -->|否| Q3{Client 长连接稳定?}

    Q3 -->|是| SSE
    Q3 -->|否| Webhook

    style Sync fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style SSE fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style Webhook fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
```

---

### 3.4 三大规范协同关系

三大规范并非孤立存在，而是在一次完整的 A2A 协作中**层层协同**：

```mermaid
%%{init: {'theme':'neutral'}}%%
sequenceDiagram
    participant CA as Client Agent
    participant RA as Remote Agent

    Note over CA,RA: 阶段1：Agent Card 规范（能力发现）
    CA->>RA: GET /.well-known/agent.json
    RA-->>CA: Agent Card(skills + url + auth)

    Note over CA,RA: 阶段2：Transport 规范（建立传输）
    CA->>CA: 按 auth schemes 获取 Token
    CA->>RA: HTTPS + JSON-RPC 请求(带 Bearer Token)

    Note over CA,RA: 阶段3：Tasks 规范（任务协作）
    CA->>RA: tasks/sendSubscribe(Task)
    Note over RA: Task 状态: submitted → working
    RA-->>CA: SSE: status=working + 进度
    RA-->>CA: SSE: status=completed + Artifact
    Note over CA: 读取产出，协作完成
```

| 阶段 | 规范 | 作用 | 产出 |
|------|------|------|------|
| **1. 发现** | Agent Card 规范 | 发现 Agent 能力与端点 | Agent Card JSON |
| **2. 传输** | Transport 规范 | 建立安全通信通道 | HTTPS + JSON-RPC 连接 |
| **3. 协作** | Tasks 规范 | 管理任务生命周期 | Task 状态流转 + Artifact 产出 |

> **总结**：Agent Card 规范让 Agent"可被发现"，Tasks 规范让协作"可追踪可恢复"，Transport 规范让通信"可靠可扩展"。三者共同构成 A2A 协议的坚实底座，支撑跨框架、跨企业的 Agent 互操作生态。

---

## 四、A2A 工作流程与四大核心能力实现方案

> A2A 协议在三大基础规范（Agent Card、Tasks、Transport）之上，构建了支撑 Agent 全生命周期协作的**四大核心能力**：**发行能力**（让 Agent 能力可发布、可发现）、**认证授权**（让协作可信任、可管控）、**任务委托**（让工作可分解、可委派）、**可观测性**（让系统可监控、可追溯）。本章系统阐述各能力模块的实现方案，涵盖具体实现步骤、技术选型建议、安全考量因素及模块间交互逻辑。

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    subgraph A2A四大核心能力
        ISS[发行能力模块<br/>能力发布与版本管理]
        AUTH[认证授权体系<br/>身份验证与访问控制]
        DELEG[任务委托机制<br/>任务分解与责任划分]
        OBS[可观测性方案<br/>监控告警与审计追溯]
    end

    ISS -->|发布能力需认证| AUTH
    AUTH -->|授权后允许委托| DELEG
    DELEG -->|委托过程需监控| OBS
    OBS -.->|监控反馈优化| ISS
    OBS -.->|审计覆盖| AUTH

    style ISS fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    style AUTH fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style DELEG fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style OBS fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

| 能力模块 | 核心职责 | 解决问题 | 关键产出 |
|----------|----------|----------|----------|
| **发行能力模块** | 数字资产（Agent Card/Skill/Task 模板）的发布、校验与版本管理 | 如何让 Agent 能力可发布、可发现、可演进 | 版本化资产注册表 |
| **认证授权体系** | 身份验证、权限分级与访问控制 | 如何确保协作方可信、权限可管控 | 认证凭证 + 权限策略 |
| **任务委托机制** | 任务分解、委派流转与责任划分 | 如何实现复杂任务的层级委派与责任追溯 | 委托链 + 责任矩阵 |
| **可观测性方案** | 指标监控、异常检测、日志审计与可视化 | 如何让系统运行状态可见、问题可定位 | 监控仪表盘 + 审计日志 |

### 4.1 发行能力模块

#### 4.1.1 模块定义与定位

**发行能力模块**负责 A2A 生态中**数字资产的发布、校验、版本管理与发现注册**。数字资产包括 Agent Card（能力描述）、Skill 定义（技能元数据）、Task 模板（任务模板）与 Artifact 规范（产出格式）。该模块是 A2A 能力发现机制的工程化实现，让 Agent 能力从"开发完成"到"可被发现调用"形成完整闭环。

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart LR
    subgraph 数字资产类型
        A1[Agent Card<br/>能力自描述]
        A2[Skill 定义<br/>技能元数据]
        A3[Task 模板<br/>任务模板]
        A4[Artifact 规范<br/>产出格式]
    end

    A1 --> REG[发行注册中心<br/>Registry]
    A2 --> REG
    A3 --> REG
    A4 --> REG

    REG --> DISC[能力发现<br/>Discovery]
    DISC --> CALL[Client 调用]

    style REG fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
```

#### 4.1.2 数字资产发行流程

数字资产发行遵循"**开发 → 校验 → 注册 → 发布 → 发现**"五步流程：

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    A[1.资产开发<br/>编写 Agent Card/Skill] --> B[2.合规校验<br/>Schema + 安全 + 合规]
    B --> C{校验通过?}
    C -->|否| B1[返回修改<br/>输出校验报告]
    C -->|是| D[3.版本分配<br/>语义化版本号]
    D --> E[4.注册发布<br/>写入注册中心]
    E --> F[5.能力发现<br/>Client 可获取]
    F --> G[6.变更通知<br/>推送 list_changed]

    B1 --> A
    style B fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style E fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style F fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

**发行流程实现示例**：

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class DigitalAsset:
    """数字资产基类"""
    asset_id: str                    # 资产唯一 ID
    asset_type: str                  # card / skill / task_template / artifact_spec
    name: str                        # 资产名称
    version: str                     # 语义化版本号
    content: dict                    # 资产内容（JSON）
    publisher: str                   # 发布者 Agent ID
    created_at: str                  # 创建时间
    status: str = "draft"            # draft / verified / published / deprecated


class AssetPublisher:
    """数字资产发行器"""

    def __init__(self, registry, validator):
        self._registry = registry        # 注册中心
        self._validator = validator      # 合规校验器

    async def publish(self, asset: DigitalAsset) -> dict:
        """完整发行流程"""
        # 步骤1：合规校验
        validation = await self._validator.validate(asset)
        if not validation.passed:
            return {"success": False, "errors": validation.errors}

        # 步骤2：版本分配（检查版本唯一性）
        existing = await self._registry.get(asset.asset_id)
        if existing and existing.version == asset.version:
            return {"success": False, "errors": ["版本号已存在，请递增"]}

        # 步骤3：注册发布
        asset.status = "published"
        await self._registry.save(asset)

        # 步骤4：变更通知
        await self._notify_change(asset)

        return {"success": True, "asset_id": asset.asset_id,
                "version": asset.version}

    async def _notify_change(self, asset: DigitalAsset):
        """通知订阅者资产已更新"""
        await self._registry.broadcast_notification(
            method="notifications/assets/list_changed",
            data={"asset_id": asset.asset_id, "version": asset.version}
        )
```

#### 4.1.3 合规校验机制

合规校验是发行流程的"守门人"，确保发布的数字资产符合协议规范与安全要求：

| 校验维度 | 校验内容 | 校验方式 | 失败处理 |
|----------|----------|----------|----------|
| **Schema 校验** | JSON 结构是否符合 Agent Card 规范 | JSON Schema 验证 | 拒绝发布，返回字段错误 |
| **必填字段** | name/url/protocolVersion/skills 是否齐全 | 字段存在性检查 | 拒绝发布，列出缺失字段 |
| **安全校验** | URL 是否 HTTPS、认证方案是否合法 | 安全策略匹配 | 拒绝发布，提示安全风险 |
| **内容审查** | 描述/技能是否含恶意指令、Prompt 注入 | 关键词过滤 + LLM 审查 | 拒绝发布，标记风险内容 |
| **唯一性校验** | asset_id + version 是否已存在 | 注册中心查询 | 拒绝发布，要求版本递增 |
| **兼容性校验** | 新版本是否与旧版本向后兼容 | 语义化版本比对 | 警告但允许发布（标记 breaking） |

**合规校验器实现**：

```python
import jsonschema
from dataclasses import dataclass
from typing import List

@dataclass
class ValidationResult:
    """校验结果"""
    passed: bool
    errors: List[str]

class ComplianceValidator:
    """合规校验器：多维校验数字资产"""

    # Agent Card JSON Schema
    CARD_SCHEMA = {
        "type": "object",
        "required": ["name", "url", "protocolVersion", "skills"],
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "url": {"type": "string", "pattern": "^https://"},
            "protocolVersion": {"type": "string"},
            "skills": {"type": "array", "minItems": 1},
            "version": {"type": "string"},
            "authentication": {"type": "object"},
        }
    }

    # 敏感词/注入模式
    INJECTION_PATTERNS = ["ignore previous", "system prompt", "rm -rf", "eval("]

    async def validate(self, asset: DigitalAsset) -> ValidationResult:
        """执行全部校验"""
        errors = []

        # 1. Schema 校验
        try:
            jsonschema.validate(asset.content, self.CARD_SCHEMA)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema 校验失败: {e.message}")

        # 2. 安全校验：URL 必须 HTTPS
        url = asset.content.get("url", "")
        if not url.startswith("https://"):
            errors.append("安全校验失败: url 必须使用 HTTPS")

        # 3. 内容审查：检测 Prompt 注入
        desc = asset.content.get("description", "")
        for pattern in self.INJECTION_PATTERNS:
            if pattern.lower() in desc.lower():
                errors.append(f"内容审查失败: 检测到可疑指令 '{pattern}'")
                break

        # 4. 唯一性校验
        # （由注册中心在 publish 流程中检查）

        return ValidationResult(passed=len(errors) == 0, errors=errors)
```

#### 4.1.4 版本控制策略

数字资产采用**语义化版本控制**（Semantic Versioning），支持版本演进、兼容管理与灰度发布：

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart LR
    subgraph 版本号结构
        MAJOR[主版本号<br/>不兼容变更]
        MINOR[次版本号<br/>向后兼容新增]
        PATCH[补丁号<br/>Bug 修复]
    end

    MAJOR --> |主版本+1| BREAK[Breaking Change<br/>旧 Client 需升级]
    MINOR --> |次版本+1| COMPAT[兼容新增<br/>旧 Client 正常工作]
    PATCH --> |补丁+1| FIX[修复补丁<br/>无功能变更]

    style BREAK fill:#ffcdd2,stroke:#c62828
    style COMPAT fill:#c8e6c9,stroke:#2e7d32
    style FIX fill:#e3f2fd,stroke:#1565c0
```

| 版本变更类型 | 版本号变化 | 兼容性 | Client 影响 | 发布策略 |
|--------------|-----------|--------|-------------|----------|
| **补丁修复** | PATCH +1 | 完全兼容 | 无感知 | 直接发布 |
| **功能新增** | MINOR +1 | 向后兼容 | 可选使用新功能 | 直接发布 |
| **破坏性变更** | MAJOR +1 | 不兼容 | 必须升级适配 | 灰度发布 + 过渡期 |
| **资产废弃** | 标记 deprecated | 过渡期兼容 | 收到废弃警告 | 过渡期后下线 |

**版本管理与灰度发布实现**：

```python
class VersionManager:
    """版本管理器：支持灰度发布与废弃管理"""

    async def check_compatibility(self, asset_id: str,
                                   old_ver: str, new_ver: str) -> str:
        """检查版本兼容性"""
        old = [int(x) for x in old_ver.split(".")]
        new = [int(x) for x in new_ver.split(".")]
        if new[0] != old[0]:
            return "breaking"      # 主版本变更：不兼容
        elif new[1] > old[1]:
            return "compatible"    # 次版本变更：兼容新增
        else:
            return "patch"         # 补丁变更：完全兼容

    async def deprecate(self, asset_id: str, version: str,
                         successor_id: str, sunset_date: str):
        """标记资产废弃，指定替代者与下线日期"""
        asset = await self._registry.get(asset_id, version)
        asset.status = "deprecated"
        asset.content["deprecated"] = True
        asset.content["successor"] = successor_id
        asset.content["sunset"] = sunset_date  # 过渡期结束日期
        await self._registry.save(asset)
        # 通知 Client 资产即将下线

    async def canary_publish(self, asset: DigitalAsset,
                              rollout_percent: int = 10):
        """灰度发布：仅向部分 Client 暴露新版本"""
        asset.content["x-canary"] = True
        asset.content["x-rollout-percent"] = rollout_percent
        await self._registry.save(asset)
```

#### 4.1.5 技术选型建议与安全考量

**技术选型建议**：

| 技术组件 | 推荐方案 | 选型理由 |
|----------|----------|----------|
| **注册中心** | Redis / etcd / Consul | 高可用 KV 存储，支持版本化与 TTL |
| **Schema 校验** | jsonschema（Python）/ ajv（JS） | 标准化 JSON Schema 验证，性能好 |
| **内容审查** | 关键词过滤 + LLM 审查双保险 | 规则覆盖已知模式，LLM 覆盖变体 |
| **变更通知** | SSE 推送 / Webhook 回调 | 实时通知订阅者刷新能力列表 |
| **版本存储** | Git-like 内容寻址存储 | 完整版本历史，支持回滚 |

**安全考量**：

| 安全风险 | 威胁描述 | 防护措施 |
|----------|----------|----------|
| **恶意资产发布** | 攻击者发布含恶意指令的 Agent Card | 发布需认证 + 内容审查 + 人工审核 |
| **版本回退攻击** | 攻击者用旧版本（含漏洞）替换新版本 | 版本不可变，仅允许新增 |
| **Prompt 注入** | 描述/skills 字段注入恶意 Prompt | 内容审查 + 输入净化 |
| **伪造发布者** | 冒充其他 Agent 发布资产 | 发布需数字签名，验签后才注册 |

#### 4.1.6 与其他模块的交互逻辑

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    ISS[发行能力模块] -->|发布前需认证| AUTH[认证授权体系]
    AUTH -->|返回发布权限| ISS
    ISS -->|发布的 Skill 可被委托| DELEG[任务委托机制]
    DELEG -->|委托执行产生 Task| ISS
    ISS -.->|发布/变更事件| OBS[可观测性方案]
    OBS -.->|审计发行记录| ISS

    style ISS fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
```

| 交互方 | 交互内容 | 触发时机 |
|--------|----------|----------|
| **→ 认证授权** | 发行前校验发布者身份与发布权限 | 资产提交发布时 |
| **→ 任务委托** | 发布的 Skill/Task 模板供委托调用 | 委托方发现能力后 |
| **→ 可观测性** | 发布/废弃/版本变更事件接入审计 | 每次资产变更时 |
| **← 可观测性** | 监控反馈资产调用量与错误率，指导版本迭代 | 定期巡检 |

---

### 4.2 认证授权体系

#### 4.2.1 模块定义与定位

**认证授权体系**是 A2A 协作的安全基石，负责解决"**你是谁**"（认证）与"**你能做什么**"（授权）两大核心问题。在跨框架、跨企业的 Agent 协作场景中，认证授权体系确保只有合法的 Agent 才能参与协作，且其行为被严格限制在授权范围内。

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart LR
    subgraph 认证授权三层模型
        L1[认证层 Authentication<br/>验证身份：你是谁?]
        L2[授权层 Authorization<br/>验证权限：你能做什么?]
        L3[审计层 Audit<br/>记录行为：你做了什么?]
    end

    L1 --> L2 --> L3
    L3 -.->|异常告警| L1

    style L1 fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style L2 fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style L3 fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

#### 4.2.2 身份验证流程

A2A 支持多种认证方案，由 Agent Card 的 `authentication.schemes` 声明，Client 按声明方式获取凭证：

```mermaid
%%{init: {'theme':'neutral'}}%%
sequenceDiagram
    participant CA as Client Agent
    participant AS as Auth Server(IdP)
    participant RA as Remote Agent

    Note over CA,AS: 阶段1：获取认证凭证
    CA->>AS: 1. OAuth2 授权请求(client_id, scope)
    AS->>AS: 2. 校验 Client 身份与授权范围
    AS-->>CA: 3. 返回 Access Token(Bearer)

    Note over CA,RA: 阶段2：携带凭证请求
    CA->>RA: 4. tasks/send(Authorization: Bearer <token>)
    RA->>RA: 5. 验证 Token 有效性
    RA->>RA: 6. 验证权限范围(Scope)
    RA-->>CA: 7. 返回结果(或 401/403 错误)

    Note over RA: 阶段3：审计记录
    RA->>RA: 8. 记录调用日志(agent_id, action, timestamp)
```

**身份验证实现**：

```python
from dataclasses import dataclass
from typing import Optional
import jwt
import time

@dataclass
class AuthCredential:
    """认证凭证"""
    scheme: str              # Bearer / OAuth2 / APIKey
    token: str               # 访问令牌
    expires_at: float        # 过期时间戳
    scopes: list             # 权限范围

class Authenticator:
    """身份验证器：支持多种认证方案"""

    async def authenticate(self, headers: dict,
                            agent_card: dict) -> AuthCredential:
        """根据 Agent Card 声明的认证方案验证身份"""
        schemes = agent_card.get("authentication", {}).get("schemes", [])
        auth_header = headers.get("Authorization", "")

        # 方案1：Bearer Token（JWT）
        if "Bearer" in schemes and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            return await self._verify_jwt(token)

        # 方案2：API Key
        if "APIKey" in schemes:
            api_key = headers.get("X-API-Key")
            return await self._verify_api_key(api_key)

        # 方案3：无认证（仅限低风险场景）
        if not schemes:
            return AuthCredential("none", "", 0, [])

        raise AuthError(f"不支持的认证方案，Agent 要求: {schemes}")

    async def _verify_jwt(self, token: str) -> AuthCredential:
        """验证 JWT Token"""
        try:
            payload = jwt.decode(token, self._public_key,
                                 algorithms=["RS256"])
            if payload["exp"] < time.time():
                raise AuthError("Token 已过期")
            return AuthCredential(
                scheme="Bearer",
                token=token,
                expires_at=payload["exp"],
                scopes=payload.get("scope", "").split()
            )
        except jwt.InvalidTokenError as e:
            raise AuthError(f"Token 无效: {e}")
```

#### 4.2.3 权限分级模型

A2A 采用**三级权限模型**，按操作风险等级划分权限：

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    subgraph 三级权限模型
        L0[L0 免授权<br/>公开数据查询<br/>只读操作]
        L1[L1 需确认<br/>用户弹窗确认<br/>中风险写操作]
        L2[L2 需审批<br/>管理员审批<br/>高风险操作]
    end

    L0 --> |风险递增| L1
    L1 --> |风险递增| L2

    style L0 fill:#e8f5e9,stroke:#2e7d32
    style L1 fill:#fff3e0,stroke:#e65100
    style L2 fill:#ffcdd2,stroke:#c62828
```

| 权限等级 | 风险等级 | 典型操作 | 授权方式 | 示例 |
|----------|----------|----------|----------|------|
| **L0 免授权** | 低 | 只读查询、公开数据访问 | 无需授权 | `get_quote`、`search_docs` |
| **L1 需确认** | 中 | 写操作、用户数据修改 | 用户弹窗确认 | `update_profile`、`create_ticket` |
| **L2 需审批** | 高 | 资金操作、数据删除、系统配置 | 管理员审批 | `transfer_funds`、`delete_record` |

**RBAC + Scope 混合权限模型**：

```python
from dataclasses import dataclass, field
from typing import Set

@dataclass
class Role:
    """角色定义"""
    name: str                          # 角色名
    permissions: Set[str]              # 权限集合
    max_level: int = 0                 # 最高允许的操作等级

@dataclass
class AgentIdentity:
    """Agent 身份"""
    agent_id: str                      # Agent 唯一标识
    roles: list                        # 角色列表
    scopes: Set[str]                   # OAuth2 Scope
    trust_level: int = 0               # 信任等级

class PermissionChecker:
    """权限检查器：RBAC + Scope + 等级控制"""

    # 预定义角色
    ROLES = {
        "viewer":   Role("viewer",   {"read"}, max_level=0),
        "operator": Role("operator", {"read", "write"}, max_level=1),
        "admin":    Role("admin",    {"read", "write", "delete", "config"}, max_level=2),
    }

    async def check(self, identity: AgentIdentity,
                     action: str, required_level: int) -> bool:
        """检查权限"""
        # 1. 等级检查：操作所需等级 ≤ 角色最高等级
        max_level = max(
            self.ROLES[r].max_level for r in identity.roles
        )
        if required_level > max_level:
            return False

        # 2. 权限检查：action 是否在角色权限集合内
        required_perm = self._action_to_permission(action)
        has_perm = any(
            required_perm in self.ROLES[r].permissions
            for r in identity.roles
        )
        if not has_perm:
            return False

        # 3. Scope 检查：操作所需 Scope 是否在凭证范围内
        required_scope = self._action_to_scope(action)
        if required_scope and required_scope not in identity.scopes:
            return False

        return True
```

#### 4.2.4 访问控制策略

| 策略类型 | 机制 | 适用场景 | 实现要点 |
|----------|------|----------|----------|
| **RBAC（角色访问控制）** | 按角色分配权限 | 企业内部 Agent 协作 | 角色绑定权限集合 |
| **ABAC（属性访问控制）** | 按属性动态决策 | 跨组织复杂协作 | 基于时间/位置/数据敏感度 |
| **Scope 限定** | OAuth2 Scope 限制 | 跨企业 API 协作 | Token 声明可访问的资源范围 |
| **速率限制** | 请求频率控制 | 防滥用、防 DoS | 令牌桶/滑动窗口算法 |
| **IP 白名单** | 来源 IP 限制 | 内网 Agent 协作 | 仅允许信任 IP 访问 |
| **时效控制** | Token 过期机制 | 所有场景 | 短期 Token + 刷新机制 |

**访问控制拦截器实现**：

```python
class AccessControlMiddleware:
    """访问控制中间件：认证→授权→限流→审计"""

    async def intercept(self, request: dict,
                         agent_card: dict) -> dict:
        """请求拦截：执行访问控制链"""
        # 1. 认证：验证身份
        credential = await self._authenticator.authenticate(
            request["headers"], agent_card
        )
        if not credential:
            return self._deny(401, "认证失败")

        # 2. 授权：验证权限
        identity = await self._build_identity(credential)
        action = request["method"]  # tasks/send, tasks/cancel 等
        required_level = self._get_required_level(action)

        if not await self._perm_checker.check(identity, action, required_level):
            return self._deny(403, "权限不足")

        # 3. 限流：验证频率
        if not await self._rate_limiter.allow(identity.agent_id):
            return self._deny(429, "请求频率超限")

        # 4. 审计：记录访问
        await self._audit_logger.log(identity, action, request)

        # 5. 放行
        return {"allowed": True, "identity": identity}
```

#### 4.2.5 技术选型建议与安全考量

**技术选型建议**：

| 技术组件 | 推荐方案 | 选型理由 |
|----------|----------|----------|
| **OAuth2 服务器** | Keycloak / Auth0 / 自建 IdP | 标准化 OAuth2/OIDC，支持多租户 |
| **Token 签发** | JWT（RS256 非对称签名） | 无状态验证，公钥可分发 |
| **权限存储** | Redis（热数据） + PostgreSQL（持久化） | 高速缓存 + 持久化审计 |
| **限流算法** | 令牌桶（Token Bucket） | 支持突发流量，平滑限流 |
| **审计日志** | ELK Stack（Elasticsearch + Kibana） | 全文检索 + 可视化分析 |

**安全考量**：

| 安全风险 | 威胁描述 | 防护措施 |
|----------|----------|----------|
| **Token 窃取** | 攻击者截获 Bearer Token 冒充调用 | 强制 HTTPS + 短期 Token + Token 绑定 |
| **权限提升** | 低权限 Agent 尝试越权操作 | 每次请求校验权限等级 + 最小权限原则 |
| **Token 重放** | 攻击者重放已使用的 Token | Token 一次性使用 + Nonce 防重放 |
| **凭证泄露** | API Key 写入代码库泄露 | 密钥管理服务（KMS）+ 环境变量注入 |
| **暴力破解** | 攻击者暴力尝试 API Key | 登录失败锁定 + IP 限流 |

#### 4.2.6 与其他模块的交互逻辑

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    AUTH[认证授权体系] -->|验证发布者权限| ISS[发行能力模块]
    AUTH -->|验证委托方与被委托方权限| DELEG[任务委托机制]
    AUTH -.->|认证/授权事件| OBS[可观测性方案]
    OBS -.->|异常登录/越权告警| AUTH

    style AUTH fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
```

| 交互方 | 交互内容 | 触发时机 |
|--------|----------|----------|
| **→ 发行能力** | 校验资产发布者身份与发布权限 | 资产提交发行时 |
| **→ 任务委托** | 验证委托方与被委托方的权限与信任等级 | 委托发起时 |
| **→ 可观测性** | 认证成功/失败、授权通过/拒绝事件 | 每次请求认证时 |
| **← 可观测性** | 异常登录、越权尝试告警 | 实时监控 |

---

### 4.3 任务委托机制

#### 4.3.1 模块定义与定位

**任务委托机制**是 A2A 实现**复杂任务分解与多 Agent 协作**的核心能力。当单个 Agent 无法独立完成复杂任务时，可将任务分解为子任务，委托给具备相应能力的其他 Agent 执行。委托机制负责任务分解、委派流转、责任划分与委托关系管理，形成可追溯的委托链。

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    subgraph 委托层级
        PM[PM Agent<br/>任务发起者]
        PM -->|委托子任务| Dev[开发 Agent]
        PM -->|委托子任务| QA[测试 Agent]
        PM -->|委托子任务| Doc[文档 Agent]

        Dev -->|二次委托| DevSub[代码生成子 Agent]
        QA -->|二次委托| QASub[测试用例子 Agent]

        Dev -->|返回 Artifact| PM
        QA -->|返回 Artifact| PM
        Doc -->|返回 Artifact| PM
    end

    style PM fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style Dev fill:#e3f2fd,stroke:#1565c0
    style QA fill:#e3f2fd,stroke:#1565c0
    style Doc fill:#e3f2fd,stroke:#1565c0
```

#### 4.3.2 委托流程设计

任务委托遵循"**分解 → 匹配 → 委派 → 追踪 → 汇总**"五步流程：

```mermaid
%%{init: {'theme':'neutral'}}%%
sequenceDiagram
    participant PM as 委托方 Agent
    participant REG as 能力注册中心
    participant RA as 被委托方 Agent

    Note over PM: 1. 任务分解
    PM->>PM: 将复杂任务分解为子任务

    Note over PM,REG: 2. 能力匹配
    PM->>REG: 查询匹配子任务的 Agent(skill tags)
    REG-->>PM: 返回候选 Agent 列表

    Note over PM,RA: 3. 委派执行
    PM->>RA: tasks/send(子任务 + 委托上下文)
    Note over RA: 4. 执行子任务
    RA-->>PM: 返回 Artifact(产出)

    Note over PM: 5. 汇总整合
    PM->>PM: 整合各子任务产出
    PM->>PM: 更新委托关系状态
```

**委托流程实现**：

```python
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class DelegationStatus(Enum):
    """委托状态"""
    PENDING = "pending"          # 待执行
    IN_PROGRESS = "in_progress"  # 执行中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"            # 失败
    CANCELED = "canceled"        # 已取消

@dataclass
class DelegationRecord:
    """委托记录"""
    delegation_id: str               # 委托唯一 ID
    parent_task_id: str              # 父任务 ID
    child_task_id: str               # 子任务 ID
    delegator: str                   # 委托方 Agent ID
    delegatee: str                   # 被委托方 Agent ID
    status: DelegationStatus = DelegationStatus.PENDING
    responsibility: str = ""         # 责任描述
    created_at: str = ""
    completed_at: Optional[str] = None

class DelegationManager:
    """委托管理器"""

    def __init__(self, registry, auth_checker):
        self._registry = registry        # 能力注册中心
        self._auth = auth_checker        # 认证授权
        self._delegations: dict = {}     # 委托记录

    async def delegate(self, parent_task: dict,
                        sub_tasks: List[dict]) -> List[DelegationRecord]:
        """任务委托主流程"""
        records = []

        for sub_task in sub_tasks:
            # 步骤1：能力匹配——找到能处理子任务的 Agent
            candidates = await self._registry.find_agents(
                skills=sub_task["required_skills"],
                tags=sub_task.get("tags", [])
            )
            if not candidates:
                raise DelegationError(
                    f"无可用 Agent 处理子任务: {sub_task['name']}"
                )

            # 步骤2：权限校验——委托方是否有权委派
            delegatee = candidates[0]  # 选最优候选
            await self._auth.check_delegation_permission(
                delegator=parent_task["delegator_id"],
                delegatee=delegatee["agent_id"],
                task=sub_task
            )

            # 步骤3：创建委托记录
            record = DelegationRecord(
                delegation_id=f"dlg-{sub_task['id']}",
                parent_task_id=parent_task["id"],
                child_task_id=sub_task["id"],
                delegator=parent_task["delegator_id"],
                delegatee=delegatee["agent_id"],
                responsibility=sub_task.get("responsibility", ""),
            )
            self._delegations[record.delegation_id] = record

            # 步骤4：发送子任务给被委托方
            await self._send_delegation_task(delegatee, sub_task, record)
            records.append(record)

        return records

    async def collect_results(self, parent_task_id: str) -> dict:
        """汇总子任务结果"""
        child_records = [
            r for r in self._delegations.values()
            if r.parent_task_id == parent_task_id
        ]
        results = {}
        for record in child_records:
            if record.status == DelegationStatus.COMPLETED:
                results[record.child_task_id] = await self._get_artifact(
                    record.child_task_id
                )
        return results
```

#### 4.3.3 责任划分原则

委托机制遵循明确的责任划分原则，确保每个子任务都有清晰的责任主体：

| 原则 | 含义 | 实践要求 |
|------|------|----------|
| **单一责任主体** | 每个子任务有且仅有一个责任 Agent | 委托记录明确 `delegatee`，禁止多头负责 |
| **责任不转移** | 委托方对最终结果负责，被委托方对子任务执行负责 | 委托方需审核子任务产出质量 |
| **最小委托粒度** | 子任务应是最小可独立执行的单元 | 避免粗粒度委托导致责任模糊 |
| **可追溯性** | 委托链完整可追溯 | 每层委托记录 delegator/delegatee/时间 |
| **失败隔离** | 子任务失败不影响其他子任务 | 独立容错，失败可重试或降级 |

**责任矩阵（RACI 模型在委托中的应用）**：

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart LR
    subgraph 责任矩阵
        direction TB
        R[Responsible<br/>执行者：被委托 Agent]
        A[Accountable<br/>负责者：委托 Agent]
        C[Consulted<br/>咨询者：领域专家]
        I[Informed<br/>知情者：最终用户]
    end

    R -->|执行子任务| A
    A -->|审核产出| R
    A -->|汇总结果| I
    C -.->|提供咨询| R

    style A fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style R fill:#e3f2fd,stroke:#1565c0
```

#### 4.3.4 委托关系管理

委托关系管理维护完整的委托链，支持层级委托、循环检测与状态追踪：

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    subgraph 委托关系树
        T0[根任务<br/>PM Agent] --> T1[子任务1<br/>开发 Agent]
        T0 --> T2[子任务2<br/>测试 Agent]
        T0 --> T3[子任务3<br/>文档 Agent]
        T1 --> T1a[孙任务1a<br/>代码生成 Agent]
        T1 --> T1b[孙任务1b<br/>代码审查 Agent]
    end

    T0 -.->|循环检测| CHECK{DAG<br/>无环检测}
    CHECK -->|有环| REJECT[拒绝循环委托]
    CHECK -->|无环| ALLOW[允许委托]

    style T0 fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style CHECK fill:#ffcdd2,stroke:#c62828
```

**委托关系管理实现**：

```python
class DelegationGraph:
    """委托关系图：维护委托链 + 循环检测"""

    def __init__(self):
        self._edges: dict[str, set] = {}  # parent_task -> {child_tasks}
        self._records: dict[str, DelegationRecord] = {}

    async def add_delegation(self, record: DelegationRecord) -> bool:
        """添加委托关系（含循环检测）"""
        # 循环检测：检查 child 是否是 parent 的祖先（会形成环）
        if await self._would_create_cycle(
            record.parent_task_id, record.child_task_id
        ):
            raise DelegationError(
                f"检测到循环委托: {record.parent_task_id} → {record.child_task_id}"
            )

        # 添加边
        if record.parent_task_id not in self._edges:
            self._edges[record.parent_task_id] = set()
        self._edges[record.parent_task_id].add(record.child_task_id)
        self._records[record.delegation_id] = record
        return True

    async def _would_create_cycle(self, parent: str, child: str) -> bool:
        """DFS 检测添加 parent→child 边是否会形成环"""
        if parent == child:
            return True  # 自环
        # 从 child 出发能否到达 parent（如果能，则加边后成环）
        visited = set()
        stack = [child]
        while stack:
            node = stack.pop()
            if node == parent:
                return True
            if node in visited:
                continue
            visited.add(node)
            stack.extend(self._edges.get(node, set()))
        return False

    async def get_delegation_chain(self, task_id: str) -> list:
        """获取任务的完整委托链（从根到当前）"""
        chain = []
        current = task_id
        while current:
            chain.append(current)
            # 找到 current 的父任务
            parent = None
            for p, children in self._edges.items():
                if current in children:
                    parent = p
                    break
            current = parent
        return list(reversed(chain))  # 从根到叶

    async def update_status(self, delegation_id: str,
                             status: DelegationStatus):
        """更新委托状态"""
        record = self._records.get(delegation_id)
        if record:
            record.status = status
```

#### 4.3.5 技术选型建议与安全考量

**技术选型建议**：

| 技术组件 | 推荐方案 | 选型理由 |
|----------|----------|----------|
| **委托图存储** | Neo4j（图数据库）/ Redis 图结构 | 高效 DAG 遍历与循环检测 |
| **任务队列** | Celery / RabbitMQ / Kafka | 异步任务分发与削峰填谷 |
| **状态追踪** | Redis Hash + Sorted Set | 高速状态查询与超时检测 |
| **结果汇总** | MapReduce 模式 / asyncio.gather | 并行收集子任务产出 |

**安全考量**：

| 安全风险 | 威胁描述 | 防护措施 |
|----------|----------|----------|
| **循环委托** | Agent A 委托 B，B 委托 A，死循环 | DAG 循环检测 + 委托深度限制 |
| **越权委托** | 低权限 Agent 委托高权限操作 | 委托权限校验 + 权限不可越级传递 |
| **委托链过长** | 多层嵌套委托导致延迟与资源消耗 | 最大委托深度限制（如 5 层） |
| **恶意委托** | Agent 委托恶意子任务给其他 Agent | 子任务内容审查 + 被委托方有权拒绝 |
| **结果篡改** | 被委托方返回篡改的产出 | 产出数字签名 + 委托方验签 |

#### 4.3.6 与其他模块的交互逻辑

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    DELEG[任务委托机制] -->|委托前需认证授权| AUTH[认证授权体系]
    DELEG -->|委托需匹配已发行能力| ISS[发行能力模块]
    DELEG -.->|委托事件/状态变更| OBS[可观测性方案]
    OBS -.->|委托链异常告警| DELEG

    style DELEG fill:#fff3e0,stroke:#e65100,stroke-width:2px
```

| 交互方 | 交互内容 | 触发时机 |
|--------|----------|----------|
| **→ 认证授权** | 校验委托方与被委托方权限与信任等级 | 委托发起前 |
| **→ 发行能力** | 查询已发行的 Skill/Task 模板匹配被委托方 | 能力匹配阶段 |
| **→ 可观测性** | 委托创建/状态变更/完成/失败事件 | 每次委托状态变化 |
| **← 可观测性** | 委托链异常（循环/超时/失败率告警） | 实时监控 |

---

### 4.4 可观测性方案

#### 4.4.1 模块定义与定位

**可观测性方案**为 A2A 协作系统提供"**可见性、可诊断性、可审计性**"能力。在跨框架、跨企业的多 Agent 协作中，调用链路复杂、故障定位困难，可观测性方案通过**指标监控、异常检测、日志记录与可视化仪表盘**，让系统运行状态全面可见、问题快速定位、行为完整可审计。

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    subgraph 可观测性三大支柱
        M[Metrics 指标<br/>性能与吞吐量化]
        L[Logs 日志<br/>行为与事件记录]
        T[Traces 追踪<br/>调用链路还原]
    end

    M --> DASH[可视化仪表盘]
    L --> DASH
    T --> DASH
    DASH --> ALERT[告警通知]

    style M fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style L fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style T fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style DASH fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
```

#### 4.4.2 性能指标监控

A2A 系统的监控指标分为**可用性、吞吐量、延迟、资源、业务**五大维度：

| 指标维度 | 指标名称 | 计算方式 | 告警阈值 |
|----------|----------|----------|----------|
| **可用性** | Agent 健康状态 | 心跳检测 | unhealthy |
| **可用性** | 服务可用率 | 成功请求/总请求 | < 99.9% |
| **吞吐量** | 每秒任务数（TPS） | 1 秒内 tasks/send 次数 | > 1000 |
| **吞吐量** | 活跃 Task 数 | working 状态 Task 数 | > 500 |
| **延迟** | 平均响应时间 | 所有请求耗时均值 | > 500ms |
| **延迟** | P99 响应时间 | 99 分位延迟 | > 2000ms |
| **资源** | CPU/内存占用 | 系统监控 | > 80% |
| **资源** | 活跃连接数 | HTTP 连接池 | > 100 |
| **业务** | Task 成功率 | completed/(completed+failed) | < 95% |
| **业务** | 委托链深度 | 平均委托层级 | > 5 |

**指标采集实现**：

```python
import time
from dataclasses import dataclass, field
from collections import defaultdict, deque
from statistics import mean

@dataclass
class MetricsCollector:
    """指标采集器"""
    _requests_total: int = 0
    _requests_success: int = 0
    _requests_failed: int = 0
    _response_times: deque = field(
        default_factory=lambda: deque(maxlen=10000)  # 滑动窗口
    )
    _task_states: dict = field(default_factory=lambda: defaultdict(int))
    _start_time: float = field(default_factory=time.time)

    def record_request(self, method: str, duration_ms: float,
                        success: bool, task_state: str = None):
        """记录一次请求"""
        self._requests_total += 1
        if success:
            self._requests_success += 1
        else:
            self._requests_failed += 1
        self._response_times.append(duration_ms)
        if task_state:
            self._task_states[task_state] += 1

    def get_metrics(self) -> dict:
        """获取当前指标快照"""
        total = max(self._requests_total, 1)
        times = list(self._response_times) or [0]
        sorted_times = sorted(times)
        p99_idx = int(len(sorted_times) * 0.99)

        return {
            "uptime_seconds": time.time() - self._start_time,
            "requests_total": self._requests_total,
            "requests_success": self._requests_success,
            "requests_failed": self._requests_failed,
            "error_rate": self._requests_failed / total,
            "success_rate": self._requests_success / total,
            "avg_response_ms": round(mean(times), 2),
            "p99_response_ms": round(sorted_times[p99_idx], 2),
            "task_states": dict(self._task_states),
            "active_tasks": self._task_states.get("working", 0),
        }
```

#### 4.4.3 异常检测机制

异常检测通过**阈值告警、趋势突变、模式异常**三种策略识别系统异常：

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    subgraph 异常检测三层策略
        L1[阈值告警<br/>指标超限即告警]
        L2[趋势突变<br/>短时变化率超限]
        L3[模式异常<br/>偏离正常基线]
    end

    L1 --> A1[错误率 > 5%]
    L1 --> A2[P99 > 2000ms]
    L2 --> A3[QPS 突增 300%]
    L2 --> A4[失败率突增]
    L3 --> A5[调用频率周期异常]
    L3 --> A6[委托链异常模式]

    A1 & A2 & A3 & A4 & A5 & A6 --> NOTIFY[告警通知<br/>邮件/短信/Webhook]

    style L1 fill:#fff3e0,stroke:#e65100
    style L2 fill:#e3f2fd,stroke:#1565c0
    style L3 fill:#f3e5f5,stroke:#6a1b9a
    style NOTIFY fill:#ffcdd2,stroke:#c62828,stroke-width:2px
```

**异常检测实现**：

```python
from dataclasses import dataclass
from enum import Enum

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class AlertRule:
    """告警规则"""
    name: str
    metric: str                # 监控指标名
    condition: str             # gt / lt / change_rate
    threshold: float           # 阈值
    severity: AlertSeverity
    window_seconds: int = 60   # 检测窗口

class AnomalyDetector:
    """异常检测器"""

    RULES = [
        AlertRule("high_error_rate", "error_rate", "gt", 0.05,
                  AlertSeverity.CRITICAL),
        AlertRule("high_latency", "p99_response_ms", "gt", 2000,
                  AlertSeverity.WARNING),
        AlertRule("qps_spike", "requests_per_second", "change_rate", 3.0,
                  AlertSeverity.WARNING, window_seconds=300),
        AlertRule("agent_unhealthy", "health_status", "eq", 0,
                  AlertSeverity.CRITICAL),
    ]

    async def check(self, metrics: dict) -> list:
        """检测异常并生成告警"""
        alerts = []
        for rule in self.RULES:
            value = metrics.get(rule.metric)
            if value is None:
                continue

            triggered = False
            if rule.condition == "gt" and value > rule.threshold:
                triggered = True
            elif rule.condition == "eq" and value == rule.threshold:
                triggered = True
            elif rule.condition == "change_rate":
                # 需要历史基线对比
                baseline = await self._get_baseline(
                    rule.metric, rule.window_seconds
                )
                if baseline > 0 and value / baseline > rule.threshold:
                    triggered = True

            if triggered:
                alerts.append({
                    "rule": rule.name,
                    "severity": rule.severity.value,
                    "metric": rule.metric,
                    "value": value,
                    "threshold": rule.threshold,
                    "timestamp": time.time(),
                })

        # 发送告警
        for alert in alerts:
            await self._notify(alert)
        return alerts
```

#### 4.4.4 日志记录规范

A2A 系统采用**结构化日志**规范，确保日志可检索、可关联、可审计：

| 日志类别 | 记录内容 | 日志级别 | 示例字段 |
|----------|----------|----------|----------|
| **访问日志** | 每次请求的方法、状态、耗时 | INFO | `request_id`, `method`, `status`, `duration_ms` |
| **认证日志** | 认证成功/失败、授权通过/拒绝 | INFO/WARN | `agent_id`, `scheme`, `result`, `scope` |
| **任务日志** | Task 状态流转、委托事件 | INFO | `task_id`, `from_state`, `to_state`, `delegator` |
| **错误日志** | 异常堆栈、错误码 | ERROR | `error_code`, `stack_trace`, `context` |
| **审计日志** | 高风险操作、合规审计 | INFO | `agent_id`, `action`, `resource`, `timestamp` |

**结构化日志规范示例**：

```json
{
  "timestamp": "2026-08-01T10:30:00.123Z",
  "level": "INFO",
  "trace_id": "trace-a1b2c3d4",
  "span_id": "span-e5f6g7h8",
  "agent_id": "client-agent-001",
  "remote_agent": "code-review-agent",
  "event": "task_state_transition",
  "task_id": "task-12345",
  "from_state": "working",
  "to_state": "completed",
  "duration_ms": 15200,
  "method": "tasks/sendSubscribe",
  "metadata": {
    "delegation_id": "dlg-001",
    "artifact_count": 1
  }
}
```

**日志记录器实现**：

```python
import json
import logging
from datetime import datetime, timezone

class StructuredLogger:
    """结构化日志记录器"""

    def __init__(self, name: str):
        self._logger = logging.getLogger(name)
        self._trace_id = None

    def set_trace_id(self, trace_id: str):
        """设置链路追踪 ID（贯穿整个调用链）"""
        self._trace_id = trace_id

    def log(self, level: str, event: str, **fields):
        """记录结构化日志"""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "trace_id": self._trace_id,
            "event": event,
            **fields,
        }
        message = json.dumps(record, ensure_ascii=False)
        getattr(self._logger, level.lower())(message)

    def log_task_event(self, task_id: str, event: str, **fields):
        """记录任务事件日志"""
        self.log("INFO", event, task_id=task_id, **fields)

    def log_auth_event(self, agent_id: str, event: str,
                        result: bool, **fields):
        """记录认证事件日志"""
        level = "INFO" if result else "WARNING"
        self.log(level, event, agent_id=agent_id,
                 result="success" if result else "failed", **fields)
```

#### 4.4.5 可视化仪表盘设计

可视化仪表盘将监控指标、调用链路与告警信息整合呈现，分为**全局概览、调用拓扑、任务追踪、告警面板**四大视图：

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    subgraph 可视化仪表盘
        D1[全局概览视图<br/>健康状态/TPS/错误率/延迟]
        D2[调用拓扑视图<br/>Agent 协作关系图]
        D3[任务追踪视图<br/>Task 状态/委托链]
        D4[告警面板<br/>活跃告警/历史告警]
    end

    D1 --> DETAIL[下钻详情]
    D2 --> DETAIL
    D3 --> DETAIL
    D4 --> DETAIL

    style D1 fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style D2 fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style D3 fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style D4 fill:#ffcdd2,stroke:#c62828,stroke-width:2px
```

| 仪表盘视图 | 展示内容 | 关键组件 | 数据刷新 |
|------------|----------|----------|----------|
| **全局概览** | 系统整体健康度、核心 KPI | 健康指示灯、折线图、数字卡片 | 5 秒 |
| **调用拓扑** | Agent 间协作关系与流量 | 有向图（节点=Agent，边=调用） | 10 秒 |
| **任务追踪** | Task 状态分布与委托链 | 甘特图、状态饼图、委托树 | 实时 |
| **告警面板** | 活跃告警列表与历史趋势 | 告警表格、趋势图、确认按钮 | 实时 |

**全局概览仪表盘核心指标卡片**：

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart LR
    subgraph 核心KPI卡片
        K1[健康状态<br/>🟢 Healthy]
        K2[TPS<br/>156/s]
        K3[错误率<br/>0.3%]
        K4[P99 延迟<br/>850ms]
        K5[活跃 Task<br/>42]
        K6[活跃告警<br/>0]
    end

    style K1 fill:#e8f5e9,stroke:#2e7d32
    style K2 fill:#e3f2fd,stroke:#1565c0
    style K3 fill:#e8f5e9,stroke:#2e7d32
    style K4 fill:#fff3e0,stroke:#e65100
    style K5 fill:#e3f2fd,stroke:#1565c0
    style K6 fill:#e8f5e9,stroke:#2e7d32
```

#### 4.4.6 技术选型建议与安全考量

**技术选型建议**：

| 技术组件 | 推荐方案 | 选型理由 |
|----------|----------|----------|
| **指标存储** | Prometheus + VictoriaMetrics | 时序数据库，高效聚合查询 |
| **日志存储** | Elasticsearch + Kibana（ELK） | 全文检索 + 日志可视化 |
| **链路追踪** | Jaeger / OpenTelemetry | 标准化分布式追踪，跨 Agent 链路 |
| **可视化** | Grafana | 统一仪表盘，支持多数据源 |
| **告警通知** | Alertmanager + PagerDuty | 多级告警路由，值班排班 |

**安全考量**：

| 安全风险 | 威胁描述 | 防护措施 |
|----------|----------|----------|
| **日志泄露敏感数据** | 日志记录 Token/密钥/用户隐私 | 日志脱敏 + 敏感字段掩码 |
| **审计日志篡改** | 攻击者删除审计痕迹 | 日志追加写入 + 区块链/WORM 存储 |
| **监控数据泄露** | 指标接口未授权访问 | 监控端点认证 + 内网隔离 |
| **日志膨胀** | 海量日志消耗存储 | 日志分级保留 + TTL 自动清理 |

#### 4.4.7 与其他模块的交互逻辑

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    OBS[可观测性方案] -.->|采集发行/变更事件| ISS[发行能力模块]
    OBS -.->|采集认证/授权事件| AUTH[认证授权体系]
    OBS -.->|采集委托/状态事件| DELEG[任务委托机制]
    OBS -->|异常告警反馈| ISS
    OBS -->|越权告警反馈| AUTH
    OBS -->|委托异常告警反馈| DELEG

    style OBS fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

| 交互方 | 交互内容 | 触发时机 |
|--------|----------|----------|
| **← 发行能力** | 采集资产发布/废弃/版本变更事件 | 资产变更时 |
| **← 认证授权** | 采集认证成功/失败、授权通过/拒绝事件 | 每次请求 |
| **← 任务委托** | 采集委托创建/状态变更/完成/失败事件 | 委托状态变化时 |
| **→ 全部模块** | 异常告警反馈（越权、委托异常、发行异常） | 检测到异常时 |

---

### 4.5 四大模块协同工作流

四大核心能力在一次完整的 A2A 协作中**协同联动**，形成"发布→认证→委托→监控"的完整闭环：

```mermaid
%%{init: {'theme':'neutral'}}%%
sequenceDiagram
    participant DEV as Agent 开发者
    participant ISS as 发行能力
    participant AUTH as 认证授权
    participant CA as Client Agent
    participant DELEG as 任务委托
    participant RA as Remote Agent
    participant OBS as 可观测性

    Note over DEV,ISS: 1. 能力发行
    DEV->>ISS: 提交 Agent Card 发布
    ISS->>ISS: 合规校验 + 版本分配
    ISS->>AUTH: 校验发布者身份
    AUTH-->>ISS: 发布权限确认
    ISS->>ISS: 注册发布
    ISS->>OBS: 记录发行事件

    Note over CA,AUTH: 2. 认证授权
    CA->>AUTH: 请求访问凭证(OAuth2)
    AUTH->>AUTH: 身份验证 + 权限分级
    AUTH-->>CA: 返回 Bearer Token + Scope
    AUTH->>OBS: 记录认证事件

    Note over CA,DELEG: 3. 任务委托
    CA->>DELEG: 发起复杂任务(需分解)
    DELEG->>ISS: 查询匹配的已发行能力
    ISS-->>DELEG: 返回候选 Agent
    DELEG->>AUTH: 校验委托权限
    AUTH-->>DELEG: 权限确认
    DELEG->>RA: 委派子任务(tasks/send)
    RA-->>DELEG: 返回 Artifact
    DELEG->>OBS: 记录委托事件

    Note over OBS: 4. 全程可观测
    OBS->>OBS: 指标采集 + 异常检测
    OBS->>OBS: 仪表盘展示 + 告警通知
```

| 阶段 | 主导模块 | 协同模块 | 产出 |
|------|----------|----------|------|
| **1. 能力发行** | 发行能力 | 认证授权（校验发布者） | 版本化 Agent Card 注册 |
| **2. 认证授权** | 认证授权 | — | Bearer Token + 权限 Scope |
| **3. 任务委托** | 任务委托 | 发行能力（能力匹配）、认证授权（权限校验） | 子任务委派 + Artifact 产出 |
| **4. 全程监控** | 可观测性 | 全部模块（事件采集） | 监控仪表盘 + 审计日志 + 告警 |

> **总结**：发行能力让 Agent"可发布可发现"，认证授权让协作"可信任可管控"，任务委托让工作"可分解可追溯"，可观测性让系统"可监控可诊断"。四大模块层层协同，共同构成 A2A 协议从能力发布到协作执行再到运维监控的完整工程闭环。

---

## 五、A2A 典型使用场景分析

```mermaid
%%{init: {'theme':'neutral'}}%%
mindmap
  root((A2A 应用场景))
    多智能体协作
      跨框架 Agent 互联
      LangGraph 调 CrewAI
      企业 Agent 生态
    跨系统集成
      企业内部系统互联
      SaaS 服务编排
      供应链协同
    复杂任务委派
      代码审查委派
      报告生成委派
      数据分析委派
    人机混合协作
      Agent 委派给人工
      人工审批 Agent 结果
      长任务异步通知
```

### 5.1 场景一：跨框架多智能体协作

**业务背景**：企业已有 LangGraph 构建的客服 Agent，需调用 CrewAI 构建的数据分析 Agent 完成用户数据查询。

**A2A 解决方案**：

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart LR
    U[用户] --> CA[客服 Agent<br/>LangGraph]
    CA -->|发现Agent Card| DA[数据分析 Agent<br/>CrewAI]
    CA -->|tasks/sendSubscribe| DA
    DA -->|SSE 流式返回| CA
    CA --> U
```

**关键点**：
- 客服 Agent 通过 `GET /.well-known/agent.json` 发现数据分析 Agent 的能力。
- 用 `tasks/sendSubscribe` 发起分析任务，SSE 流式接收进度。
- 数据分析 Agent 返回 Artifact（分析报告），客服 Agent 整合后回复用户。
- **无需改写框架**，LangGraph 与 CrewAI 通过 A2A 标准 HTTP 通信。

### 5.2 场景二：跨企业供应链协同

**业务背景**：采购方 Agent 需协调供应商 Agent 查询库存、下单、跟踪物流。

| 协作步骤 | A2A 调用 | 说明 |
|----------|----------|------|
| 1. 发现供应商能力 | `GET agent.json` | 获取供应商 Agent 的 skills |
| 2. 查询库存 | `tasks/send` | 同步返回库存数据 |
| 3. 下单 | `tasks/sendSubscribe` | 长任务，流式跟踪订单状态 |
| 4. 物流跟踪 | `tasks/pushNotificationSet` | 设置 Webhook，物流更新自动推送 |
| 5. 异常处理 | `input_required` 状态 | 缺货时 Agent 请求采购方决策 |

### 5.3 场景三：复杂任务委派

**业务背景**：项目经理 Agent 需协调多个专业 Agent 完成产品发布。

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    PM[PM Agent] -->|委派| Dev[开发 Agent]
    PM -->|委派| QA[测试 Agent]
    PM -->|委派| Doc[文档 Agent]
    PM -->|委派| Mkt[市场 Agent]

    Dev -->|Artifact: 代码| PM
    QA -->|Artifact: 测试报告| PM
    Doc -->|Artifact: 文档| PM
    Mkt -->|Artifact: 营销方案| PM

    PM -->|汇总| Done[发布完成]
```

**关键点**：
- PM Agent 用 A2A 委派子任务给 4 个专业 Agent。
- 各 Agent 独立工作，通过 Artifact 返回产出。
- PM Agent 用 `tasks/get` 轮询或 Webhook 推送收集结果。
- 任一 Agent 失败（`failed` 状态），PM Agent 决定重试或降级。

### 5.4 场景四：人机混合协作

**业务背景**：金融合规审查 Agent 处理大额交易，需人工审批。

| 步骤 | 状态流转 | 说明 |
|------|----------|------|
| 1. Agent 收到交易 | `submitted` | 合规 Agent 接收任务 |
| 2. Agent 初审 | `working` | 自动检查黑名单、规则 |
| 3. 需人工决策 | `input_required` | 触发人工审批 |
| 4. 人工批准 | `working` → `completed` | 人工输入决策结果 |
| 5. 人工拒绝 | `working` → `canceled` | 取消交易 |
| 6. 长任务通知 | Webhook 推送 | 异步通知审批结果 |

---

## 六、A2A 技术实现难点与解决方案

### 6.1 难点一：异步通信与长任务处理

**问题**：复杂任务（如代码审查、数据分析）可能耗时数分钟到数小时，同步 HTTP 会超时。

**解决方案**：

| 方案 | 机制 | 适用场景 |
|------|------|----------|
| **SSE 流式订阅** | `tasks/sendSubscribe` 长连接，实时推送进度 | 中等耗时（秒-分钟） |
| **Webhook 推送** | `tasks/pushNotificationSet` 注册回调，状态变更推送 | 长耗时（分钟-小时） |
| **轮询** | `tasks/get` 定期查询状态 | 简单场景，不实时 |
| **断线重连** | `tasks/resubscribe` 重新订阅已断开流 | 网络不稳定 |

**Webhook 实现示例**：

```python
# Client 注册 Webhook
await client.send({
    "method": "tasks/pushNotificationSet",
    "params": {
        "id": "task-12345",
        "pushNotificationConfig": {
            "url": "https://client.example.com/webhook",
            "token": "secret-token",  # 验证用
            "events": ["completed", "failed", "input_required"]
        }
    }
})

# Remote Agent 在状态变更时推送
async def notify_client(task_id: str, new_state: str):
    config = get_push_config(task_id)
    async with httpx.AsyncClient() as client:
        await client.post(
            config["url"],
            headers={"X-Agent-Token": config["token"]},
            json={"task_id": task_id, "state": new_state}
        )
```

### 6.2 难点二：冲突解决机制

**问题**：多个 Client Agent 同时调用同一 Remote Agent，可能产生资源冲突或结果冲突。

**冲突类型与解决**：

| 冲突类型 | 表现 | 解决方案 |
|----------|------|----------|
| **并发写冲突** | 多 Agent 同时修改同一 Task | Task 级锁 + 乐观并发控制（版本号） |
| **资源争用** | 多 Agent 争抢 Remote Agent 算力 | 队列排队 + 优先级调度 |
| **结果不一致** | 多 Agent 对同一问题给出不同结果 | Client 侧投票/仲裁/择优 |
| **死锁** | Agent A 等 B，B 等 A | 超时强制取消 + DAG 检测循环 |

**乐观并发控制**：

```python
class TaskManager:
    """带乐观并发的 Task 管理"""

    async def update_task(self, task_id: str, update: dict, expected_version: int):
        """带版本号的更新,防并发冲突"""
        task = await self.get(task_id)
        if task["version"] != expected_version:
            raise ConflictError(
                f"版本冲突:期望 {expected_version},实际 {task['version']}"
            )
        update["version"] = task["version"] + 1
        return await self.save(task_id, update)
```

### 6.3 难点三：性能优化

**优化方案**：

| 优化维度 | 方案 | 效果 |
|----------|------|------|
| **连接复用** | HTTP Keep-Alive / 连接池 | 减少 TCP 握手开销 |
| **流式优先** | SSE 替代轮询 | 实时性提升，资源消耗降低 |
| **批处理** | 多 Task 合并提交 | 吞吐量提升 |
| **Agent Card 缓存** | 客户端缓存发现结果 | 减少发现请求 |
| **结果缓存** | 相同输入 Task 结果缓存 | 重复任务零延迟 |
| **分级路由** | 简单任务路由到轻量 Agent | 成本降低 |
| **压缩传输** | Gzip/Brotli 压缩 JSON | 带宽降低 70% |

### 6.4 难点四：错误处理与容错

**错误分类与处理**：

| 错误类型 | JSON-RPC 错误码 | 处理策略 |
|----------|----------------|----------|
| **认证失败** | -32001 | 刷新 Token 重试 |
| **授权不足** | -32002 | 降级或转人工 |
| **任务不存在** | -32003 | 重新创建任务 |
| **任务已取消** | -32004 | 终止处理 |
| **参数校验失败** | -32602 | 修正参数重试 |
| **Agent 内部错误** | -32603 | 指数退避重试 |
| **超时** | 网络层 | 切换 Webhook 异步模式 |
| **Agent 不可用** | 网络层 | 故障转移到备用 Agent |

**指数退避重试实现**：

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class A2AClient:
    """带容错的 A2A 客户端"""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        retry=retry_if_exception_type((TimeoutError, ConnectionError)),
    )
    async def send_task(self, remote_agent_url: str, task: dict) -> dict:
        """发送任务,带自动重试"""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                remote_agent_url,
                json={
                    "jsonrpc": "2.0",
                    "method": "tasks/send",
                    "id": self._gen_id(),
                    "params": task,
                },
                headers={"Authorization": f"Bearer {self.token}"},
            )
            resp.raise_for_status()
            data = resp.json()
            if "error" in data:
                raise A2AError(data["error"])
            return data["result"]

    async def send_task_with_fallback(
        self, primary: str, backup: str, task: dict
    ) -> dict:
        """带故障转移的任务发送"""
        try:
            return await self.send_task(primary, task)
        except Exception as e:
            print(f"主 Agent 失败,切换备用: {e}")
            return await self.send_task(backup, task)
```

### 6.5 难点五：可观测性与调试

**挑战**：跨 Agent 调用链路复杂，问题难定位。

**解决方案**：

| 方案 | 做法 | 价值 |
|------|------|------|
| **trace_id 透传** | 全链路追踪 ID 贯穿所有 Agent | 跨 Agent 调用链可视化 |
| **Task 日志** | 记录每次状态变更 | 审计与回溯 |
| **SSE 事件流** | 流式更新即日志 | 实时观测进度 |
| **Agent Card 版本** | 记录调用的 Agent 版本 | 问题复现 |
| **LangSmith 集成** | A2A 调用接入追踪平台 | 生产级可观测 |

---

## 七、A2A 未来发展趋势与挑战

### 7.1 发展趋势

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart LR
    T1[标准化<br/>生态统一] --> T2[商业化<br/>Agent 市场]
    T2 --> T3[智能化<br/>自组织协作]
    T3 --> T4[治理化<br/>合规与审计]

    style T1 fill:#e3f2fd,stroke:#1565c0
    style T2 fill:#fff3e0,stroke:#e65100
    style T3 fill:#e8f5e9,stroke:#2e7d32
    style T4 fill:#f3e5f5,stroke:#6a1b9a
```

| 趋势 | 说明 | 影响 |
|------|------|------|
| **Agent 市场兴起** | 类似 App Store 的 Agent 能力市场 | Agent 可变现、可发现 |
| **跨厂商互操作** | OpenAI/Anthropic/Google 统一支持 | 生态融合 |
| **自组织协作** | Agent 自主发现、协商、组队 | 复杂任务自动化 |
| **Agent 身份体系** | Agent 有独立身份与信誉 | 信任机制建立 |
| **实时流式协作** | 多 Agent 实时流式交互 | 协作效率提升 |
| **边缘 Agent** | Agent 部署到边缘节点 | 低延迟场景 |

### 7.2 面临的挑战

| 挑战 | 描述 | 潜在解法 |
|------|------|----------|
| **安全信任** | 跨组织 Agent 调用如何建立信任 | Agent 身份认证 + 信誉系统 |
| **质量保证** | 远程 Agent 返回结果质量参差 | SLA 协议 + 质量评估 |
| **成本计费** | 跨组织调用如何计费结算 | Token 化计量 + 智能合约 |
| **隐私保护** | 敏感数据跨 Agent 流转 | 联邦学习 + 数据脱敏 |
| **协议碎片化** | A2A vs MCP vs 厂商私有协议 | 协议融合或适配层 |
| **调试困难** | 跨 Agent 调用链路复杂 | 标准化追踪协议 |
| **治理合规** | Agent 自主决策的合规边界 | 审计日志 + 人工监督 |

---

## 八、A2A vs MCP 对比

### 8.1 定位对比

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    subgraph 定位差异
        MCP_C[MCP<br/>Agent ↔ 工具<br/>纵向集成]
        A2A_C[A2A<br/>Agent ↔ Agent<br/>横向协作]
    end

    subgraph MCP场景
        MA1[Agent] -->|调用工具| Tool1[数据库]
        MA1 -->|调用工具| Tool2[API]
        MA1 -->|调用工具| Tool3[文件系统]
    end

    subgraph A2A场景
        A2_1[Agent A] <-->|协作| A2_2[Agent B]
        A2_2 <-->|协作| A2_3[Agent C]
        A2_1 <-->|协作| A2_3
    end

    style MCP_C fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style A2A_C fill:#fff3e0,stroke:#e65100,stroke-width:2px
```

### 8.2 核心差异对比表

| 维度 | MCP（Model Context Protocol） | A2A（Agent2Agent Protocol） |
|------|------------------------------|---------------------------|
| **出品方** | Anthropic（2024.11） | Google（2025.4） |
| **定位** | Agent 与工具/资源之间的连接 | Agent 与 Agent 之间的协作 |
| **通信方向** | 纵向：Agent → 工具 | 横向：Agent ↔ Agent |
| **核心抽象** | Tools / Resources / Prompts | Task / Message / Artifact |
| **通信模式** | 请求-响应（主），Sampling 反向 | 请求-响应 + SSE 流式 + Webhook 推送 |
| **状态管理** | 无状态（工具调用） | Task 有完整生命周期状态机 |
| **传输协议** | stdio（本地） + Streamable HTTP | HTTP + JSON-RPC 2.0 |
| **发现机制** | Server 暴露 Tools/Resources | Agent Card 自描述（`.well-known/agent.json`） |
| **长任务支持** | 弱（工具调用即时返回） | 强（Task 状态机 + 流式 + 推送） |
| **多模态** | 弱（文本为主） | 强（Message 含文本/文件/数据 Part） |
| **典型场景** | Agent 调数据库/API/文件 | 跨框架 Agent 协作、跨企业协同 |
| **认证** | 本地 stdio 无需；HTTP 用标准认证 | OAuth2 / API Key / Bearer Token |

### 8.3 互补关系

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TB
    User[用户] --> Agent[Agent]
    Agent -->|MCP| Tools[工具层<br/>数据库/API/文件]
    Agent -->|A2A| OtherAgents[其他 Agent<br/>跨框架/跨企业]

    Agent -->|MCP| Local[本地资源]
    Agent -->|A2A| Remote[远程 Agent]

    style Agent fill:#fff3e0,stroke:#e65100,stroke-width:3px
    style Tools fill:#e3f2fd,stroke:#1565c0
    style OtherAgents fill:#e8f5e9,stroke:#2e7d32
```

| 协作模式 | 说明 | 示例 |
|----------|------|------|
| **MCP 纵向** | Agent 用 MCP 调用工具获取能力 | Agent 通过 MCP 查数据库 |
| **A2A 横向** | Agent 用 A2A 与其他 Agent 协作 | 客服 Agent 委派分析 Agent |
| **MCP + A2A** | Agent 既调工具又协作 | Agent A 用 MCP 查数据，用 A2A 委派 Agent B 处理 |

### 8.4 选型建议

| 场景 | 推荐协议 | 理由 |
|------|----------|------|
| **Agent 访问数据库/API** | MCP | MCP 是工具连接标准，生态丰富 |
| **Agent 读取本地文件** | MCP | stdio 传输，本地高效 |
| **Agent 调用 RAG 检索** | MCP | Resources 原语适配 |
| **跨框架 Agent 协作** | A2A | A2A 是 Agent 间通信标准 |
| **跨企业 Agent 协同** | A2A | HTTP+认证，适合跨组织 |
| **长任务委派（代码审查）** | A2A | Task 状态机 + 流式，支持长任务 |
| **多 Agent 协商辩论** | A2A | 多轮 Task 交互 |
| **Agent 同时需工具+协作** | MCP + A2A | 互补使用，不冲突 |

**一句话总结**：**MCP 让 Agent 拥有工具，A2A 让 Agent 拥有伙伴。**

---

## 九、面试题及详解

### 题目 1：A2A 定义与核心特性（概念题·基础）

**难度**：基础　**类型**：概念题

**问题描述**：
请简述 A2A 协议的定义，列举至少 4 个核心特性，并说明它解决了什么问题。

**参考答案要点**：

**定义**：A2A 是 Google 联合 50+ 合作伙伴推出的开放协议，基于 HTTP + JSON-RPC 2.0，让不同框架、不同厂商构建的 Agent 能够跨框架、跨平台互相通信与协作。

**核心特性**（列举 4+ 即可）：
1. **框架无关**：不绑定 LangGraph/AutoGen/CrewAI 等特定框架。
2. **基于 Web 标准**：HTTP + JSON-RPC，复用现有基础设施。
3. **Agent Card 自描述**：Agent 通过 JSON 元数据暴露能力，支持动态发现。
4. **Task 生命周期管理**：Task 有完整状态机（submitted→working→completed）。
5. **多模态支持**：Message 含文本/文件/数据 Part。
6. **流式响应**：SSE 支持长任务流式输出。
7. **推送通知**：Webhook 回调，无需轮询。

**解决的问题**：打破 Agent 生态孤岛——不同框架的 Agent 之前无法互操作，每个框架都是封闭生态。A2A 提供统一通信标准，让任意 Agent 都能像调用 API 一样调用其他 Agent。

**评分标准**：定义准确 2 分；特性≥4 个 2 分；解决的问题 1 分（满分 5）。

---

### 题目 2：A2A vs 传统 API 区别（概念题·基础）

**难度**：基础　**类型**：概念题

**问题描述**：
请从接口定义、交互模式、状态管理、发现机制四个维度对比 A2A 与传统 API 调用。

**参考答案要点**：

| 维度 | 传统 API | A2A |
|------|----------|-----|
| **接口定义** | OpenAPI/Swagger 固定 Schema | Agent Card 自描述，动态发现 |
| **交互模式** | 请求-响应，同步为主 | 任务驱动，支持流式/推送/长任务 |
| **状态管理** | 无状态，每次独立 | Task 有完整生命周期状态机 |
| **发现机制** | 需提前知道端点 | Agent Card 自动发现能力 |

**关键区别**：传统 API 是"硬编码调用"，A2A 是"动态发现+任务协作"。A2A 的 Task 有状态机，支持长任务流式和 Webhook 推送，而传统 API 通常是单次无状态调用。

**评分标准**：四维度对比各 1 分；关键区别说明 1 分（满分 5）。

---

### 题目 3：Agent Card 作用与字段（概念题·基础）

**难度**：基础　**类型**：概念题

**问题描述**：
Agent Card 是 A2A 的核心组件之一，请说明其作用并列出至少 5 个关键字段。

**参考答案要点**：

**作用**：Agent Card 是 Agent 的自描述 JSON 文件，通常位于 `/.well-known/agent.json`，让 Client Agent 能够：
1. **发现 Agent**：通过 GET 请求获取能力清单。
2. **了解能力**：通过 skills 字段知道 Agent 能做什么。
3. **知道如何调用**：通过 url 字段获取端点。
4. **知道如何认证**：通过 authentication 字段选择认证方式。

**关键字段**（列出 5+ 即可）：
- `name`：Agent 名称
- `description`：Agent 功能描述
- `url`：Agent 的 A2A 端点
- `version`：Agent 版本
- `capabilities`：能力声明（streaming/pushNotifications）
- `skills`：技能列表（id/name/description/tags）
- `authentication`：支持的认证方式（schemes）
- `defaultInputModes` / `defaultOutputModes`：默认输入输出模式

**评分标准**：作用说明 2 分；字段≥5 个 2 分；发现机制说明 1 分（满分 5）。

---

### 题目 4：Task 状态机流转（原理题·中级）

**难度**：中级　**类型**：原理题

**问题描述**：
请画出（或描述）A2A Task 的完整状态机，并说明每个状态的含义与 Client 的对应动作。

**参考答案要点**：

**状态流转**：
```
submitted → working → completed
                ↓        ↑
          input_required
                ↓
             working（用户提供输入后）

working → failed（处理失败）
working → canceled（被取消）
```

**状态说明**：

| 状态 | 含义 | Client 动作 |
|------|------|-------------|
| `submitted` | 任务已提交，未开始 | 等待 |
| `working` | Agent 处理中 | 流式接收或轮询 |
| `input_required` | 需用户补充信息 | 收集输入并 `tasks/send` |
| `completed` | 成功完成 | 读取 Artifact |
| `failed` | 处理失败 | 读取错误信息，决定重试 |
| `canceled` | 已取消 | 终止处理 |

**关键点**：
- `input_required` 是 A2A 的特色，支持多轮交互（Agent 处理中发现需补充信息）。
- `working` 可通过 SSE 流式接收进度，或用 `tasks/get` 轮询。
- 终止状态（completed/failed/canceled）后 Task 不可再变更。

**评分标准**：状态机完整 2 分；状态含义 2 分；Client 动作 1.5 分；关键点 0.5 分（满分 6）。

---

### 题目 5：通信机制与核心方法（原理题·中级）

**难度**：中级　**类型**：原理题

**问题描述**：
请列出 A2A 的 6 个核心 JSON-RPC 方法，说明各自用途与交互模式。

**参考答案要点**：

| 方法 | 用途 | 交互模式 |
|------|------|----------|
| `tasks/send` | 发送任务，同步返回结果 | 请求-响应 |
| `tasks/sendSubscribe` | 发送任务并订阅流式更新 | SSE 流式 |
| `tasks/get` | 查询任务状态 | 请求-响应 |
| `tasks/cancel` | 取消任务 | 请求-响应 |
| `tasks/pushNotificationSet` | 设置 Webhook 回调 | 请求-响应 |
| `tasks/resubscribe` | 重新订阅已断开的流 | SSE 流式 |

**关键点**：
- 同步任务用 `tasks/send`，长任务用 `tasks/sendSubscribe`（SSE）。
- 长任务也可用 `tasks/pushNotificationSet` 注册 Webhook，异步推送状态变更。
- 网络断开时用 `tasks/resubscribe` 恢复流式订阅，避免丢失进度。

**评分标准**：6 个方法各 0.5 分 3 分；交互模式 1.5 分；关键点 1.5 分（满分 6）。

---

### 题目 6：安全策略分层（原理题·中级）

**难度**：中级　**类型**：原理题

**问题描述**：
A2A 作为跨组织 Agent 通信协议，安全至关重要。请从认证、授权、传输、输入校验四层说明安全策略。

**参考答案要点**：

| 安全层 | 机制 | 说明 |
|--------|------|------|
| **认证** | OAuth2 / API Key / Bearer Token | Agent Card 声明支持的 schemes，Client 按声明获取凭证 |
| **授权** | Scope / Role-Based | 限制 Agent 可访问的资源范围 |
| **传输** | HTTPS 强制 | 防止中间人攻击，所有通信加密 |
| **输入校验** | JSON Schema 校验 Message | 防 Prompt 注入、参数篡改 |
| **速率限制** | Rate Limiting | 防滥用、防 DoS |
| **审计** | 全量 Task 日志 | 满足合规审计 |
| **隔离** | Agent 沙箱执行 | 防恶意代码执行 |

**关键点**：
- 认证方式由 Agent Card 的 `authentication.schemes` 声明，Client 必须按声明方式认证。
- 跨组织场景优先用 OAuth2，支持细粒度 Scope 授权。
- 输入校验不仅校验格式，还需检测 Prompt 注入（如恶意指令）。

**评分标准**：四层各 1 分 4 分；关键点 2 分（满分 6）。

---

### 题目 7：跨框架协作场景分析（分析题·中级）

**问题描述**：
企业已有 LangGraph 构建的客服 Agent，需调用 CrewAI 构建的数据分析 Agent。请用 A2A 设计协作方案，说明发现、调用、结果整合流程。

**参考答案要点**：

**协作流程**：

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart LR
    U[用户] --> CA[客服Agent<br/>LangGraph]
    CA -->|1.发现| DA[分析Agent<br/>CrewAI]
    CA -->|2.委派Task| DA
    DA -->|3.SSE流式返回| CA
    CA -->|4.整合回复| U
```

**详细步骤**：
1. **发现**：客服 Agent 通过 `GET https://analytics.example.com/.well-known/agent.json` 获取分析 Agent 的 Agent Card，了解其 skills（数据分析）与端点。
2. **认证**：客服 Agent 用 OAuth2 获取访问 Token。
3. **发起任务**：用 `tasks/sendSubscribe` 发起分析任务，SSE 流式接收进度。
4. **状态处理**：
   - `working`：展示进度给用户
   - `input_required`：收集用户补充信息后 `tasks/send` 继续
   - `completed`：读取 Artifact（分析报告）
5. **结果整合**：客服 Agent 将分析报告整合到对话中回复用户。

**关键点**：
- LangGraph 与 CrewAI 无需互相适配，通过 A2A 标准 HTTP 通信。
- 流式更新让用户实时感知进度，体验好。
- `input_required` 支持多轮交互，Agent 处理中可请求补充信息。

**评分标准**：流程完整 2.5 分；A2A 方法使用正确 2 分；关键点 1.5 分（满分 6）。

---

### 题目 8：异步通信与长任务处理（分析题·高级）

**问题描述**：
代码审查任务可能耗时 10-30 分钟，同步 HTTP 会超时。请用 A2A 设计长任务处理方案，包含 SSE、Webhook、断线重连。

**参考答案要点**：

**方案设计**：

| 阶段 | A2A 方法 | 机制 |
|------|----------|------|
| 1. 发起长任务 | `tasks/sendSubscribe` | SSE 长连接，实时推送进度 |
| 2. 进度更新 | SSE 事件 | status=working + 进度文本 |
| 3. 注册备份通知 | `tasks/pushNotificationSet` | Webhook 作为 SSE 断线兜底 |
| 4. SSE 断线 | `tasks/resubscribe` | 重新订阅，恢复流 |
| 5. 任务完成 | SSE / Webhook | status=completed + Artifact |

**关键设计**：
1. **SSE 优先**：实时性好，用户可看到进度。但 SSE 可能因网络中断断开。
2. **Webhook 兜底**：同时注册 Webhook，SSE 断线时 Webhook 仍能推送最终状态。
3. **断线重连**：用 `tasks/resubscribe` 恢复流，不丢失已处理进度。
4. **超时保护**：Client 设置最大等待时间，超时后用 `tasks/get` 查询最终状态。

```python
# 长任务处理伪代码
async def long_task_with_fallback(agent_url, task):
    # 1. 注册 Webhook 兜底
    await client.call(agent_url, "tasks/pushNotificationSet", {
        "id": task["id"],
        "pushNotificationConfig": {"url": WEBHOOK_URL, "token": SECRET}
    })

    # 2. SSE 流式订阅
    try:
        async for event in client.subscribe(agent_url, "tasks/sendSubscribe", task):
            if event["status"] == "completed":
                return event["artifact"]
    except ConnectionError:
        # 3. 断线重连
        async for event in client.resubscribe(agent_url, task["id"]):
            if event["status"] == "completed":
                return event["artifact"]

    # 4. 兜底:Webhook 会异步推送,Client 可等待或轮询
    return await wait_for_webhook(task["id"], timeout=3600)
```

**评分标准**：方案完整 2.5 分；SSE+Webhook 双保险 1.5 分；断线重连 1 分；代码 1 分（满分 6）。

---

### 题目 9：冲突解决机制设计（设计题·高级）

**问题描述**：
多个 Client Agent 同时调用同一 Remote Agent，可能产生并发写冲突、资源争用、结果不一致。请设计完整的冲突解决机制。

**参考答案要点**：

**冲突类型与解决**：

| 冲突类型 | 解决方案 | 实现 |
|----------|----------|------|
| **并发写冲突** | 乐观并发控制（版本号） | Task 带 version，更新时校验 |
| **资源争用** | 队列排队 + 优先级 | Remote Agent 侧任务队列 |
| **结果不一致** | Client 侧投票/仲裁 | 多 Agent 结果多数表决 |
| **死锁** | 超时强制取消 + DAG 检测 | 循环依赖检测 |

**乐观并发控制实现**：

```python
class TaskManager:
    async def update_task(self, task_id, update, expected_version):
        task = await self.get(task_id)
        if task["version"] != expected_version:
            raise ConflictError(f"版本冲突:期望{expected_version},实际{task['version']}")
        update["version"] = task["version"] + 1
        return await self.save(task_id, update)
```

**死锁检测**：
- Client 维护调用 DAG（有向无环图）。
- 新增调用前检查是否形成环。
- 检测到环则超时取消其中一个 Task，打破死锁。

**评分标准**：四类冲突各 1 分 4 分；乐观并发实现 1 分；死锁检测 1 分（满分 6）。

---

### 题目 10：性能优化方案（设计题·高级）

**问题描述**：
A2A 系统在高并发场景下延迟高、吞吐量低。请从连接、传输、缓存、路由四个维度给出优化方案。

**参考答案要点**：

| 维度 | 优化方案 | 效果 |
|------|----------|------|
| **连接** | HTTP Keep-Alive / 连接池复用 | 减少 TCP 握手开销 |
| **传输** | SSE 替代轮询；Gzip/Brotli 压缩 JSON | 实时性提升，带宽降 70% |
| **缓存** | Agent Card 缓存 + Task 结果缓存 | 减少发现请求，重复任务零延迟 |
| **路由** | 简单任务路由到轻量 Agent（mini 模型） | 成本降低 40% |
| **批处理** | 多 Task 合并提交 | 吞吐量提升 |
| **异步流水线** | Agent 间异步传递，不阻塞等待 | 资源利用率提升 |

**Agent Card 缓存示例**：
```python
from functools import lru_cache

@lru_cache(maxsize=128, ttl=3600)  # 缓存1小时
async def get_agent_card(agent_url: str) -> dict:
    """带缓存的 Agent Card 发现"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{agent_url}/.well-known/agent.json")
        return resp.json()
```

**评分标准**：四维度各 1 分 4 分；量化效果 1 分；代码示例 1 分（满分 6）。

---

### 题目 11：容错与故障转移（设计题·高级）

**问题描述**：
Remote Agent 可能不可用或超时。请设计 A2A 客户端的容错与故障转移方案。

**参考答案要点**：

**容错策略**：

| 错误类型 | 策略 | 实现 |
|----------|------|------|
| **网络超时** | 指数退避重试 | tenacity 重试 3 次 |
| **Agent 不可用** | 故障转移到备用 Agent | 主备 Agent 列表 |
| **认证失败** | 刷新 Token 重试 | OAuth2 token refresh |
| **Task 失败** | 重新创建任务 | 记录上下文，重试 |
| **5xx 错误** | 指数退避重试 | 区分可重试错误 |
| **4xx 错误** | 不重试，修正参数 | 参数校验 |

**故障转移实现**：

```python
class A2AClient:
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=30),
           retry=retry_if_exception_type((TimeoutError, ConnectionError)))
    async def send_task(self, url, task):
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=self._wrap(task),
                                      headers={"Authorization": f"Bearer {self.token}"})
            resp.raise_for_status()
            return resp.json()["result"]

    async def send_with_fallback(self, primary, backup, task):
        try:
            return await self.send_task(primary, task)
        except Exception as e:
            print(f"主Agent失败,切换备用: {e}")
            return await self.send_task(backup, task)
```

**评分标准**：错误分类 2 分；重试策略 2 分；故障转移实现 2 分（满分 6）。

---

### 题目 12：A2A vs MCP 对比与选型（分析题·高级）

**问题描述**：
请对比 A2A 与 MCP 的定位、核心抽象、通信模式、适用场景，并说明二者关系及选型建议。

**参考答案要点**：

**核心对比**：

| 维度 | MCP | A2A |
|------|-----|-----|
| **定位** | Agent ↔ 工具（外部，获取天气 钉钉等内容）（纵向集成） | Agent ↔ Agent（横向协作） |
| **核心抽象** | Tools / Resources / Prompts | Task / Message / Artifact |
| **通信模式** | 请求-响应为主 | 请求-响应 + SSE + Webhook |
| **状态管理** | 无状态 | Task 生命周期状态机 |
| **传输** | stdio + Streamable HTTP | HTTP + JSON-RPC |
| **发现** | Server 暴露 Tools/Resources | Agent Card 自描述 |
| **长任务** | 弱 | 强（流式+推送） |

**关系**：**互补而非竞争**。
- MCP 让 Agent 拥有工具（纵向能力扩展）。
- A2A 让 Agent 拥有伙伴（横向协作扩展）。
- 一个 Agent 可同时用 MCP 调工具 + 用 A2A 协作。

**选型建议**：
- Agent 访问数据库/API/文件 → **MCP**
- 跨框架/跨企业 Agent 协作 → **A2A**
- 长任务委派（代码审查等）→ **A2A**
- Agent 既需工具又需协作 → **MCP + A2A**

**一句话总结**：**MCP 让 Agent 拥有工具，A2A 让 Agent 拥有伙伴。**

**评分标准**：对比维度≥6 项 3 分；互补关系 1.5 分；选型建议 1 分；总结 0.5 分（满分 6）。

---

## 十、考点速查表

| 题号 | 类型 | 难度 | 考点 | 满分 |
|------|------|------|------|------|
| 1 | 概念题 | 基础 | A2A 定义、核心特性 | 5 |
| 2 | 概念题 | 基础 | A2A vs 传统 API 区别 | 5 |
| 3 | 概念题 | 基础 | Agent Card 作用与字段 | 5 |
| 4 | 原理题 | 中级 | Task 状态机流转 | 6 |
| 5 | 原理题 | 中级 | 通信机制（JSON-RPC 方法） | 6 |
| 6 | 原理题 | 中级 | 安全策略分层 | 6 |
| 7 | 分析题 | 中级 | 跨框架协作场景分析 | 6 |
| 8 | 分析题 | 高级 | 异步通信与长任务处理 | 6 |
| 9 | 设计题 | 高级 | 冲突解决机制设计 | 6 |
| 10 | 设计题 | 高级 | 性能优化方案 | 6 |
| 11 | 设计题 | 高级 | 容错与故障转移 | 6 |
| 12 | 分析题 | 高级 | A2A vs MCP 对比与选型 | 6 |

**面试官建议**：
- **初级岗位**：重点考察题 1-3，要求理解 A2A 基本概念与 Agent Card。
- **中级岗位**：增加题 4-7，要求掌握 Task 状态机、通信机制、能分析场景。
- **高级岗位**：重点考察题 8-12，要求能设计容错、优化性能、对比选型 A2A vs MCP。
