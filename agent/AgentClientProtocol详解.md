# Agent Client Protocol 详解

> **文档说明**：本文档系统介绍 **Agent Client Protocol（ACP，Agent 客户端协议）**——由 Zed Industries 于 2025 年 8 月发布的开放标准，用于标准化**代码编辑器/IDE（Client）**与 **AI 编码 Agent（Agent）**之间的通信。文档全面阐述协议的核心概念、设计架构、通信流程、数据格式规范、接口定义、错误处理机制、安全策略及扩展机制，并提供 TypeScript / Python / Rust 多语言示例。ACP 被誉为"Agent 界的 LSP"，与 MCP 互补：MCP 让 Agent 能用工具，ACP 让编辑器能驱动 Agent。
>
> **⚠️ 命名提示**："ACP" 是有歧义的缩写。本文档介绍的是 **Zed 主导的 Agent Client Protocol**（编辑器 ↔ Agent），与同目录下 [ACP协议详解.md](./ACP协议详解.md) 介绍的 **AgentUnion Agent Communication Protocol**（Agent ↔ Agent）是**完全不同的两个协议**，请勿混淆。

## 目录

- [一、协议概述](#一协议概述)
- [二、核心概念](#二核心概念)
- [三、设计架构](#三设计架构)
- [四、通信流程](#四通信流程)
- [五、数据格式规范](#五数据格式规范)
- [六、接口定义](#六接口定义)
- [七、错误处理机制](#七错误处理机制)
- [八、安全策略](#八安全策略)
- [九、扩展机制](#九扩展机制)
- [十、与 MCP 的关系](#十与-mcp-的关系)
- [十一、使用示例](#十一使用示例)
- [十二、生态与采纳](#十二生态与采纳)
- [十三、最佳实践](#十三最佳实践)
- [十四、与其他协议对比](#十四与其他协议对比)
- [十五、总结](#十五总结)

---

## 一、协议概述

### 1.1 协议定位

**Agent Client Protocol（ACP）** 是一个开放标准，标准化**代码编辑器/IDE**与**AI 编码 Agent**之间的通信。在 ACP 之前，每个编辑器需要为每个 Agent 编写定制化集成，导致生态重复造轮子。ACP 用单一接口替代这些一次性集成：**任何兼容 ACP 的 Agent 都能在任何兼容 ACP 的编辑器中运行，无需自定义胶水代码**。

### 1.2 核心定位一句话

> **LSP 标准化了编辑器与语言服务器的通信，ACP 标准化了编辑器与 AI 编码 Agent 的通信。**

### 1.3 设计目标

| 目标 | 说明 |
|------|------|
| **解耦** | 打破编辑器与 Agent 的一对一集成困境 |
| **互操作** | 任意 Agent × 任意编辑器自由组合 |
| **流式友好** | 原生支持流式输出、工具调用状态、diff 展示 |
| **人在回路** | 内置权限请求机制，敏感操作需用户确认 |
| **可扩展** | 通过 `_meta` 字段和下划线前缀方法支持自定义扩展 |
| **会话化** | 支持多轮对话会话，可恢复、可分支 |

### 1.4 协议基本信息

| 属性 | 值 |
|------|-----|
| **发起方** | Zed Industries |
| **首发时间** | 2025 年 8 月 |
| **当前稳定版本** | protocolVersion 1 |
| **传输协议** | JSON-RPC 2.0 over stdio（本地）/ HTTP、WebSocket（远程，WIP） |
| **消息编码** | NDJSON（换行分隔的 JSON），UTF-8 |
| **许可证** | Apache-2.0 |
| **规范语言** | Rust（Cargo workspace） |
| **官方文档** | https://agentclientprotocol.com/ |
| **仓库** | https://github.com/agentclientprotocol/agent-client-protocol |

---

## 二、核心概念

### 2.1 形象类比

> **Agent 如果是员工，Client（编辑器）就是工作台，ACP 是工作台与员工之间的标准操作规程，MCP 是员工手中的工具箱。**

### 2.2 Client（客户端）

Client 是 **代码编辑器/IDE**，提供用户与 Agent 交互的界面。Client 的职责：

- **启动并管理 Agent 进程**（作为子进程）
- **管理环境**：文件系统、终端、工作目录
- **处理用户交互**：接收用户输入、展示 Agent 输出
- **控制资源访问**：通过权限机制决定 Agent 能做什么
- **渲染富内容**：diff 视图、工具调用状态、计划展示

典型 Client：Zed、JetBrains IDEs（IntelliJ、PyCharm、Rider 等）、Neovim、Emacs、VS Code（社区插件）。

### 2.3 Agent（智能体）

Agent 是 **使用生成式 AI 自主修改代码的程序**，通常作为 Client 的子进程运行。Agent 的职责：

- **接收用户 prompt** 并调用 LLM 推理
- **执行工具调用**：读写文件、运行命令、调用外部服务
- **流式返回输出**：文本、diff、工具状态、思考过程
- **请求权限**：敏感操作前向 Client 请求用户授权
- **管理会话状态**：维护多轮对话上下文

典型 Agent：Claude Code、Gemini CLI、Aider、Pydantic AI Agent、ZeroClaw 等。

### 2.4 Session（会话）

Session 是 **一次连续的编辑/对话上下文**，是 Agent 与 Client 交互的核心单元。

| 生命周期阶段 | 说明 |
|-------------|------|
| **创建** | `session/new` 创建新会话，或 `session/load` 恢复历史会话 |
| **Prompt 轮次** | 用户发送 `session/prompt`，Agent 流式返回 `session/update` |
| **取消** | `session/cancel` 中断正在进行的 prompt |
| **恢复** | Agent 通过 `session/update` 回放完整历史 |
| **关闭** | Client 终止子进程或显式关闭会话 |

### 2.5 Capability（能力）

Capability 是 **Client 与 Agent 在初始化时协商的功能声明**，决定后续可用特性。能力协商是 ACP 的核心设计，确保向后兼容。

| 能力类型 | 典型示例 | 声明方 |
|---------|----------|--------|
| **Client 能力** | `fileSystem`、`terminal` | Client |
| **Agent 能力** | `loadSession`、`promptCapabilities`、`mcpCapabilities` | Agent |
| **认证方法** | `authMethods` | Agent |

### 2.6 概念关系图

```
┌─────────────────────────────────────────────────────────────────┐
│                    ACP 协议生态全景                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────┐                                   │
│   │      用户（User）       │                                   │
│   └────────────┬────────────┘                                   │
│                │ 输入 prompt / 确认权限 / 查看输出               │
│                ▼                                                │
│   ┌────────────────────────────────────────────────────────┐    │
│   │              Client（代码编辑器/IDE）                   │    │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │    │
│   │  │ Chat UI  │  │ 文件编辑 │  │  终端    │             │    │
│   │  └──────────┘  └──────────┘  └──────────┘             │    │
│   │  ┌──────────────────────────────────────┐              │    │
│   │  │  ACP Client（JSON-RPC Handler）       │              │    │
│   │  └────────────────┬─────────────────────┘              │    │
│   └───────────────────┼────────────────────────────────────┘    │
│                       │                                         │
│                       │ JSON-RPC 2.0 over stdio                 │
│                       │ (NDJSON)                                │
│                       │                                         │
│   ┌───────────────────▼────────────────────────────────────┐    │
│   │              Agent（AI 编码 Agent 进程）                │    │
│   │  ┌──────────────────────────────────────┐              │    │
│   │  │  ACP Agent（JSON-RPC Processor）      │              │    │
│   │  └────────────────┬─────────────────────┘              │    │
│   │                   │                                      │    │
│   │  ┌─────────┐  ┌───▼──────┐  ┌──────────┐  ┌─────────┐ │    │
│   │  │  LLM    │  │ 工具执行  │  │ MCP 客户 │  │ 会话存储│ │    │
│   │  │ 接口    │  │          │  │ 端(可选) │  │         │ │    │
│   │  └────┬────┘  └──────────┘  └──────────┘  └─────────┘ │    │
│   └───────┼───────────────────────────────────────────────┘    │
│           │                                                      │
│           ▼                                                      │
│   ┌─────────────────┐                                            │
│   │  LLM Provider   │  Claude / GPT / Gemini / ...              │
│   └─────────────────┘                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、设计架构

### 3.1 分层架构

ACP 采用清晰的分层设计：

```
┌─────────────────────────────────────────────────────────────────┐
│                    应用层（Application Layer）                   │
│   编辑器 UI / Agent 业务逻辑 / LLM 推理 / 工具执行               │
├─────────────────────────────────────────────────────────────────┤
│                    协议层（Protocol Layer）                      │
│   ACP 方法 / 通知 / 会话管理 / 能力协商 / 内容类型              │
├─────────────────────────────────────────────────────────────────┤
│                    RPC 层（RPC Layer）                           │
│   JSON-RPC 2.0 请求/响应/通知语义                               │
├─────────────────────────────────────────────────────────────────┤
│                    传输层（Transport Layer）                     │
│   stdio（NDJSON）/ HTTP / WebSocket                            │
├─────────────────────────────────────────────────────────────────┤
│                    进程层（Process Layer）                       │
│   子进程管理 / stdin/stdout 管道 / 生命周期                     │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 进程模型

ACP 采用 **Client 主导的子进程模型**：

```
┌─────────────────────────────────────────────────────────────────┐
│                      进程模型                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────────────────────────────────┐                  │
│   │           Client 进程（父）              │                  │
│   │                                          │                  │
│   │   ┌────────────────────────────────┐    │                  │
│   │   │  spawn(agent_command, args)    │    │                  │
│   │   └────────────┬───────────────────┘    │                  │
│   │                │                        │                  │
│   │      ┌─────────▼─────────┐              │                  │
│   │      │   stdin (写入)    │──────────────┼──────┐           │
│   │      └─────────┬─────────┘              │      │           │
│   │      ┌─────────▼─────────┐              │      ▼           │
│   │      │  stdout (读取)    │◄─────────────┼──────────┐       │
│   │      └─────────┬─────────┘              │      │   │       │
│   │      ┌─────────▼─────────┐              │      │   │       │
│   │      │  stderr (日志)    │              │      │   │       │
│   │      └───────────────────┘              │      │   │       │
│   └──────────────────────────────────────────┘      │   │       │
│                                                     │   │       │
│                       ┌─────────────────────────────┘   │       │
│                       │                                 │       │
│                       ▼                                 │       │
│   ┌──────────────────────────────────────────────────┐ │       │
│   │           Agent 进程（子）                        │ │       │
│   │                                                  │ │       │
│   │   stdin  ◄──── JSON-RPC 请求/通知                │◄┘       │
│   │   stdout ────► JSON-RPC 响应/通知                │         │
│   │   stderr ────► 日志（非 JSON）                   │         │
│   └──────────────────────────────────────────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**关键规则**：
- Client 通过 `spawn` 启动 Agent 子进程，连接其 stdin/stdout
- stdout **只能输出 NDJSON**，任何非 JSON 输出会破坏协议流
- 日志、诊断信息必须输出到 stderr
- Client 在连接断开时应终止子进程（Kill on Drop 模式）

### 3.3 消息流向

ACP 是 **双向通信**协议，初始化后双方都可主动发送消息：

```
┌──────────────────┐                    ┌──────────────────┐
│     Client       │                    │      Agent       │
│                  │  请求（Request）   │                  │
│                  │ ──────────────────►│                  │
│                  │                    │                  │
│                  │  响应（Response）  │                  │
│                  │◄────────────────── │                  │
│                  │                    │                  │
│                  │  通知（Notification）                  │
│                  │◄────────────────── │                  │
│                  │ ──────────────────►│                  │
│                  │                    │                  │
└──────────────────┘                    └──────────────────┘
```

| 消息类型 | 特征 | 发起方 |
|---------|------|--------|
| **Request** | 包含 `id` 字段，期望得到响应 | 双向 |
| **Response** | 包含与请求匹配的 `id`，含 `result` 或 `error` | 双向 |
| **Notification** | 无 `id` 字段，单向通知，无响应 | 双向 |

### 3.4 仓库结构

```
agent-client-protocol/
├── src/                      # Rust schema crate
│   ├── lib.rs                # 模块入口
│   ├── agent.rs              # Agent 侧类型（2500+ 行）
│   ├── client.rs             # Client 侧类型
│   ├── rpc.rs                # JSON-RPC 底层格式
│   ├── content.rs            # 内容类型：Text/Diff/Image
│   ├── tool_call.rs          # 工具调用：kind/status/permissions
│   ├── plan.rs               # Agent Plan 任务规划
│   ├── protocol_level.rs     # 协议版本管理
│   ├── error.rs              # 错误码定义
│   └── ext.rs                # 扩展机制（_meta, 自定义方法）
├── schema/
│   ├── schema.json           # 稳定版 JSON Schema
│   └── schema.unstable.json  # 实验性特性
├── docs/                     # 官方文档（MDX）
└── Cargo.toml                # Rust crate
```

---

## 四、通信流程

### 4.1 完整交互时序图

```
┌─────────────────────────────────────────────────────────────────┐
│                  ACP 完整交互时序                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Client (IDE)                        Agent                      │
│                                                                 │
│  ════════════ 阶段 1：初始化 ════════════                        │
│                                                                 │
│  ┌──────────────────────┐                                       │
│  │ 1. initialize        │                                       │
│  │   protocolVersion    │                                       │
│  │   clientCapabilities │                                       │
│  │   clientInfo         │                                       │
│  └──────────┬───────────┘                                       │
│             │ ─────────────────────────────────────────────►    │
│             │                                                   │
│                                  ┌──────────────────────┐       │
│                                  │ 协商版本             │       │
│                                  │ 检查能力             │       │
│                                  └──────────┬───────────┘       │
│             │◄─────────────────────────────────────────────     │
│  ┌──────────▼───────────┐                                       │
│  │ InitializeResponse   │                                       │
│  │   protocolVersion    │                                       │
│  │   agentCapabilities  │                                       │
│  │   agentInfo          │                                       │
│  │   authMethods        │                                       │
│  └──────────────────────┘                                       │
│                                                                 │
│  ════════════ 阶段 2：认证（可选）════════════                   │
│                                                                 │
│  ┌──────────────────────┐                                       │
│  │ 2. authenticate      │                                       │
│  │   (如需)             │                                       │
│  └──────────┬───────────┘                                       │
│             │ ─────────────────────────────────────────────►    │
│             │◄─────────────────────────────────────────────     │
│  ┌──────────▼───────────┐                                       │
│  │ AuthResponse         │                                       │
│  └──────────────────────┘                                       │
│                                                                 │
│  ════════════ 阶段 3：会话创建 ════════════                      │
│                                                                 │
│  ┌──────────────────────┐                                       │
│  │ 3. session/new       │                                       │
│  │   cwd                │                                       │
│  │   mcpServers         │                                       │
│  │   (可选)             │                                       │
│  └──────────┬───────────┘                                       │
│             │ ─────────────────────────────────────────────►    │
│             │◄─────────────────────────────────────────────     │
│  ┌──────────▼───────────┐                                       │
│  │ NewSessionResponse   │                                       │
│  │   sessionId          │                                       │
│  │   models             │                                       │
│  │   modes              │                                       │
│  └──────────┬───────────┘                                       │
│             │                                                   │
│             │◄─────────────────────────────────────────────     │
│  ┌──────────▼───────────┐                                       │
│  │ Notification:        │                                       │
│  │ session/update       │                                       │
│  │ (available_commands) │                                       │
│  └──────────────────────┘                                       │
│                                                                 │
│  ════════════ 阶段 4：Prompt 轮次 ════════════                   │
│                                                                 │
│  ┌──────────────────────┐                                       │
│  │ 4. session/prompt    │                                       │
│  │   sessionId          │                                       │
│  │   prompt[]           │                                       │
│  └──────────┬───────────┘                                       │
│             │ ─────────────────────────────────────────────►    │
│             │                    ┌──────────────────────┐       │
│             │                    │ 提交 LLM 推理        │       │
│             │                    └──────────┬───────────┘       │
│             │                                                   │
│             │   ┌────────────────────────────────────────┐     │
│             │   │ 循环：流式返回 session/update 通知     │     │
│             │   └────────────────────────────────────────┘     │
│             │◄─────────────────────────────────────────────     │
│  ┌──────────▼───────────┐                                       │
│  │ Notification:        │                                       │
│  │ session/update       │                                       │
│  │ (agent_message_chunk)│                                       │
│  └──────────────────────┘                                       │
│             │◄─────────────────────────────────────────────     │
│  ┌──────────▼───────────┐                                       │
│  │ Notification:        │                                       │
│  │ session/update       │                                       │
│  │ (tool_call: pending) │                                       │
│  └──────────────────────┘                                       │
│                                                                 │
│  ════════════ 阶段 5：权限请求（可选）═══════════               │
│                                                                 │
│             │◄─────────────────────────────────────────────     │
│  ┌──────────▼───────────┐                                       │
│  │ 5. request_permission│                                       │
│  │   toolCall           │                                       │
│  │   options            │                                       │
│  └──────────┬───────────┘                                       │
│             │                                                   │
│             │  用户确认                                         │
│             │ ─────────────────────────────────────────────►    │
│             │◄─────────────────────────────────────────────     │
│  ┌──────────▼───────────┐                                       │
│  │ PermissionResponse   │                                       │
│  │   optionId           │                                       │
│  └──────────────────────┘                                       │
│                                                                 │
│  ════════════ 阶段 6：工具执行与后续更新 ════════════            │
│                                                                 │
│             │◄─────────────────────────────────────────────     │
│  ┌──────────▼───────────┐                                       │
│  │ Notification:        │                                       │
│  │ session/update       │                                       │
│  │ (tool_call:          │                                       │
│  │  in_progress)        │                                       │
│  └──────────────────────┘                                       │
│             │◄─────────────────────────────────────────────     │
│  ┌──────────▼───────────┐                                       │
│  │ Notification:        │                                       │
│  │ session/update       │                                       │
│  │ (tool_call:          │                                       │
│  │  completed)          │                                       │
│  └──────────────────────┘                                       │
│             │◄─────────────────────────────────────────────     │
│  ┌──────────▼───────────┐                                       │
│  │ Notification:        │                                       │
│  │ session/update       │                                       │
│  │ (agent_message_chunk)│                                       │
│  └──────────────────────┘                                       │
│                                                                 │
│  ════════════ 阶段 7：Prompt 完成 ════════════                   │
│                                                                 │
│             │◄─────────────────────────────────────────────     │
│  ┌──────────▼───────────┐                                       │
│  │ PromptResponse       │                                       │
│  │   stopReason         │                                       │
│  └──────────────────────┘                                       │
│                                                                 │
│  ════════════ 阶段 8：取消（可选）═══════════                    │
│                                                                 │
│  ┌──────────────────────┐                                       │
│  │ Notification:        │                                       │
│  │ session/cancel       │                                       │
│  │   sessionId          │                                       │
│  └──────────┬───────────┘                                       │
│             │ ─────────────────────────────────────────────►    │
│             │                                                   │
│             │  (Agent 终止处理，仍返回 PromptResponse)          │
│             │◄─────────────────────────────────────────────     │
│  ┌──────────▼───────────┐                                       │
│  │ PromptResponse       │                                       │
│  │   stopReason:        │                                       │
│  │   "cancelled"        │                                       │
│  └──────────────────────┘                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 消息流程摘要

| 阶段 | Client → Agent | Agent → Client |
|------|---------------|----------------|
| **初始化** | `initialize` → `authenticate`（可选） | `InitializeResponse` → `AuthResponse` |
| **会话创建** | `session/new` 或 `session/load` | `NewSessionResponse` + `session/update`（命令更新） |
| **Prompt 轮次** | `session/prompt` | `session/update` × N（流式）+ `PromptResponse` |
| **权限请求** | `PermissionResponse` | `session/request_permission` |
| **取消** | `session/cancel`（通知） | `PromptResponse`（stopReason: cancelled） |
| **文件操作** | `fs/read_text_file`、`fs/write_text_file` 响应 | `fs/read_text_file`、`fs/write_text_file` 请求 |
| **终端操作** | `terminal/*` 响应 | `terminal/create`、`terminal/output` 等请求 |

### 4.3 关键流程规则

1. **Client 始终是发起方**：Client 启动 Agent 并驱动连接
2. **每个 prompt 恰好得到一个 PromptResponse**：即使被取消也必须返回
3. **`session/cancel` 仅用于正在进行的 prompt**：不是会话终止
4. **能力决定可用功能**：调用前必须检查能力
5. **所有文件路径必须为绝对路径**
6. **行号从 1 开始**

---

## 五、数据格式规范

### 5.1 JSON-RPC 2.0 消息结构

所有 ACP 消息基于 JSON-RPC 2.0，分为三类：

#### 5.1.1 请求（Request）

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "session/prompt",
  "params": {
    "sessionId": "sess_abc123",
    "prompt": [
      { "type": "text", "text": "解释这段代码" }
    ]
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `jsonrpc` | string | ✅ | 固定为 `"2.0"` |
| `id` | number \| string | ✅ | 请求标识，用于匹配响应 |
| `method` | string | ✅ | 方法名 |
| `params` | object \| array | ❌ | 方法参数 |

#### 5.1.2 响应（Response）

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "stopReason": "end_turn"
  }
}
```

错误响应：

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32601,
    "message": "Method not found"
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `jsonrpc` | string | ✅ | 固定为 `"2.0"` |
| `id` | number \| string | ✅ | 与请求匹配的标识 |
| `result` | any | ❌ | 成功结果（与 error 互斥） |
| `error` | object | ❌ | 错误信息（与 result 互斥） |

#### 5.1.3 通知（Notification）

```json
{
  "jsonrpc": "2.0",
  "method": "session/update",
  "params": {
    "sessionId": "sess_abc123",
    "update": {
      "sessionUpdate": "agent_message_chunk",
      "content": { "type": "text", "text": "正在分析..." }
    }
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `jsonrpc` | string | ✅ | 固定为 `"2.0"` |
| `method` | string | ✅ | 方法名 |
| `params` | object \| array | ❌ | 方法参数 |
| **`id`** | **无** | **-** | **通知无 id 字段** |

### 5.2 NDJSON 帧格式

ACP 使用 **NDJSON（Newline-Delimited JSON）** 格式：每条消息为一行 JSON，以换行符 `\n` 分隔。

```
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{...}}\n
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":1,...}}\n
{"jsonrpc":"2.0","method":"session/update","params":{...}}\n
```

**关键规则**：
- 每条消息占一行，**不能包含嵌入式换行符**
- 消息编码为 UTF-8
- stdout **只能输出 NDJSON**，非 JSON 内容会破坏协议
- 日志必须输出到 stderr

### 5.3 内容类型（Content Types）

ACP 定义多种内容块类型用于 prompt 和消息：

#### 5.3.1 文本内容（TextContent）

```json
{
  "type": "text",
  "text": "请帮我重构这个函数"
}
```

#### 5.3.2 资源内容（ResourceContent）

```json
{
  "type": "resource",
  "resource": {
    "uri": "file:///path/to/file.rs",
    "text": "文件内容..."
  }
}
```

#### 5.3.3 图片内容（ImageContent）

```json
{
  "type": "image",
  "source": {
    "type": "base64",
    "mediaType": "image/png",
    "data": "iVBORw0KGgo..."
  }
}
```

#### 5.3.4 Diff 内容（DiffContent）

```json
{
  "type": "diff",
  "path": "/absolute/path/to/file.rs",
  "diff": "--- original\n+++ modified\n@@ -1,3 +1,3 @@\n-old line\n+new line",
  "oldText": "old line",
  "newText": "new text"
}
```

### 5.4 工具调用（Tool Call）

#### 5.4.1 工具调用结构

```json
{
  "sessionUpdate": "tool_call",
  "toolCallId": "tc-1",
  "title": "Edit file",
  "kind": "edit",
  "status": "pending",
  "rawInput": {
    "path": "/absolute/path/to/file.rs",
    "content": "..."
  },
  "locations": [
    {
      "path": "/absolute/path/to/file.rs",
      "line": 10
    }
  ]
}
```

#### 5.4.2 工具调用 kind

| kind | 说明 | 典型操作 |
|------|------|----------|
| `read` | 读取操作 | 读文件、查询 |
| `edit` | 编辑操作 | 修改文件、写入 |
| `shell` | 命令执行 | 运行命令、脚本 |
| `execute` | 通用执行 | 调用外部服务 |

#### 5.4.3 工具调用 status

| status | 说明 |
|--------|------|
| `pending` | 等待执行（可能等待权限） |
| `in_progress` | 正在执行 |
| `completed` | 执行完成 |
| `failed` | 执行失败 |

### 5.5 会话更新（session/update）

`session/update` 通知的 `update` 字段通过 `sessionUpdate` 区分类型：

| `sessionUpdate` 值 | 说明 |
|-------------------|------|
| `agent_message_chunk` | Agent 输出的文本/思考块 |
| `tool_call` | 工具调用状态更新 |
| `plan` | 任务计划更新 |
| `available_commands_update` | 可用命令更新 |
| `current_mode_update` | 当前模式更新 |

---

## 六、接口定义

### 6.1 Agent 侧方法（Client → Agent）

#### 6.1.1 `initialize` - 初始化握手

**功能**：协商协议版本、交换能力声明。这是连接建立后的第一个请求。

**请求参数**：

```json
{
  "protocolVersion": 1,
  "clientCapabilities": {
    "fileSystem": {
      "readTextFile": true,
      "writeTextFile": true
    },
    "terminal": true
  },
  "clientInfo": {
    "name": "zed",
    "version": "0.180.0"
  }
}
```

**响应结果**：

```json
{
  "protocolVersion": 1,
  "agentCapabilities": {
    "loadSession": true,
    "promptCapabilities": {
      "image": true,
      "audio": false,
      "embeddedContext": true
    },
    "mcpCapabilities": {
      "http": true,
      "sse": true
    },
    "sessionCapabilities": {
      "resume": {},
      "close": {}
    }
  },
  "agentInfo": {
    "name": "claude-code",
    "title": "Claude Code",
    "version": "1.0.0"
  },
  "authMethods": []
}
```

**关键参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `protocolVersion` | uint16 (0-65535) | 协议主版本，标识 MAJOR 版本兼容性 |
| `clientCapabilities` | object | Client 能力声明 |
| `agentCapabilities` | object | Agent 能力声明 |
| `agentInfo` | object | Agent 元信息 |
| `authMethods` | array | 支持的认证方法列表 |

#### 6.1.2 `authenticate` - 认证

**功能**：如 Agent 声明了 `authMethods`，Client 必须在会话前认证。

**请求参数**：

```json
{
  "method": "anthropic_api_key",
  "credentials": {
    "apiKey": "sk-ant-..."
  }
}
```

**响应结果**：

```json
{
  "authenticated": true,
  "user": "developer@example.com"
}
```

#### 6.1.3 `session/new` - 创建新会话

**功能**：创建新的会话，指定工作目录和可选的 MCP servers。

**请求参数**：

```json
{
  "cwd": "/absolute/path/to/project",
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
    }
  },
  "agentAlias": "myagent"
}
```

**响应结果**：

```json
{
  "sessionId": "sess_abc123def456",
  "workspaceDir": "/absolute/path/to/project",
  "models": [
    { "id": "claude-sonnet-4", "name": "Claude Sonnet 4" }
  ],
  "modes": [
    { "name": "default", "description": "默认模式" }
  ]
}
```

#### 6.1.4 `session/load` - 加载已有会话

**功能**：恢复历史会话，Agent 通过 `session/update` 回放完整历史。需要 `loadSession` 能力。

**请求参数**：

```json
{
  "sessionId": "sess_abc123def456"
}
```

**响应**：Agent 通过一系列 `session/update` 通知回放历史，最后返回响应。

#### 6.1.5 `session/prompt` - 发送 prompt

**功能**：在会话中发送用户消息，触发 Agent 处理。Agent 通过 `session/update` 流式返回更新，最后返回 `PromptResponse`。

**请求参数**：

```json
{
  "sessionId": "sess_abc123def456",
  "prompt": [
    { "type": "text", "text": "帮我重构 main.rs 中的 process 函数" },
    {
      "type": "resource",
      "resource": {
        "uri": "file:///path/to/main.rs",
        "text": "文件内容..."
      }
    }
  ]
}
```

**响应结果**：

```json
{
  "stopReason": "end_turn"
}
```

| `stopReason` 值 | 说明 |
|----------------|------|
| `end_turn` | Agent 主动结束 |
| `tool_use` | 需要工具调用结果 |
| `max_tokens` | 达到 token 上限 |
| `cancelled` | 被 `session/cancel` 取消 |
| `error` | 发生错误 |

### 6.2 Agent 侧通知

#### 6.2.1 `session/cancel` - 取消

**功能**：取消正在进行的 prompt 处理。通知（无响应），Agent 仍需返回 `PromptResponse`（stopReason 为 `cancelled`）。

```json
{
  "jsonrpc": "2.0",
  "method": "session/cancel",
  "params": {
    "sessionId": "sess_abc123def456"
  }
}
```

### 6.3 Client 侧方法（Agent → Client）

#### 6.3.1 `session/request_permission` - 请求权限

**功能**：Agent 执行敏感工具调用前，请求用户授权。

**请求参数**：

```json
{
  "sessionId": "sess_abc123def456",
  "toolCallId": "tc-1",
  "options": [
    { "id": "allow", "label": "允许", "type": "allow" },
    { "id": "deny", "label": "拒绝", "type": "deny" },
    { "id": "allow_always", "label": "总是允许", "type": "allow" }
  ]
}
```

**响应结果**：

```json
{
  "outcome": {
    "behavior": "allow",
    "optionId": "allow"
  }
}
```

#### 6.3.2 `fs/read_text_file` - 读取文件

**功能**：Agent 请求 Client 读取文件内容。需要 `fs.readTextFile` 能力。

**请求参数**：

```json
{
  "path": "/absolute/path/to/file.rs"
}
```

**响应结果**：

```json
{
  "content": "文件内容..."
}
```

#### 6.3.3 `fs/write_text_file` - 写入文件

**功能**：Agent 请求 Client 写入文件。需要 `fs.writeTextFile` 能力。

**请求参数**：

```json
{
  "path": "/absolute/path/to/file.rs",
  "content": "新内容..."
}
```

#### 6.3.4 终端方法

| 方法 | 功能 | 能力要求 |
|------|------|----------|
| `terminal/create` | 创建新终端 | `terminal` |
| `terminal/output` | 获取终端输出与退出状态 | `terminal` |
| `terminal/release` | 释放终端 | `terminal` |
| `terminal/wait_for_exit` | 等待终端退出 | `terminal` |

**`terminal/create` 请求示例**：

```json
{
  "command": ["npm", "test"],
  "cwd": "/absolute/path/to/project"
}
```

**`terminal/create` 响应示例**：

```json
{
  "terminalId": "term-1"
}
```

### 6.4 可选 Agent 方法

| 方法 | 功能 | 能力要求 |
|------|------|----------|
| `logout` | 结束当前认证状态 | `agentCapabilities.auth.logout` |
| `session/set_mode` | 切换 Agent 操作模式 | unstable |

### 6.5 方法总览表

| 方法 | 方向 | 类型 | 说明 |
|------|:----:|:----:|------|
| `initialize` | Client → Agent | Request | 初始化握手 |
| `authenticate` | Client → Agent | Request | 认证 |
| `session/new` | Client → Agent | Request | 创建会话 |
| `session/load` | Client → Agent | Request | 加载会话 |
| `session/prompt` | Client → Agent | Request | 发送 prompt |
| `session/cancel` | Client → Agent | Notification | 取消 prompt |
| `logout` | Client → Agent | Request | 登出 |
| `session/set_mode` | Client → Agent | Request | 切换模式 |
| `session/request_permission` | Agent → Client | Request | 请求权限 |
| `session/update` | Agent → Client | Notification | 会话更新 |
| `fs/read_text_file` | Agent → Client | Request | 读文件 |
| `fs/write_text_file` | Agent → Client | Request | 写文件 |
| `terminal/create` | Agent → Client | Request | 创建终端 |
| `terminal/output` | Agent → Client | Request | 终端输出 |
| `terminal/release` | Agent → Client | Request | 释放终端 |
| `terminal/wait_for_exit` | Agent → Client | Request | 等待退出 |

---

## 七、错误处理机制

### 7.1 JSON-RPC 标准错误码

| 错误码 | 名称 | 说明 |
|--------|------|------|
| `-32700` | Parse error | JSON 解析错误 |
| `-32600` | Invalid Request | 无效请求 |
| `-32601` | Method not found | 方法不存在 |
| `-32602` | Invalid params | 参数无效 |
| `-32603` | Internal error | 内部错误 |

### 7.2 ACP 特定错误码

| 错误码 | 名称 | 说明 | 处理建议 |
|--------|------|------|----------|
| `-32000` | `SESSION_NOT_FOUND` | 会话不存在 | 检查 sessionId，可能需重新创建 |
| `-32001` | `PROTOCOL_VERSION_MISMATCH` | 协议版本不匹配 | 协商共同支持的版本 |
| `-32002` | `AUTHENTICATION_REQUIRED` | 需要认证 | 先调用 `authenticate` |
| `-32003` | `AUTHENTICATION_FAILED` | 认证失败 | 检查凭据 |
| `-32004` | `CAPABILITY_NOT_SUPPORTED` | 能力不支持 | 检查能力声明 |
| `-32005` | `PERMISSION_DENIED` | 权限被拒 | 用户拒绝了权限请求 |
| `-32006` | `INVALID_SESSION_STATE` | 会话状态无效 | 检查会话生命周期 |

### 7.3 错误响应示例

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "error": {
    "code": -32000,
    "message": "Session not found",
    "data": {
      "sessionId": "sess_abc123"
    }
  }
}
```

### 7.4 错误处理策略

```
┌─────────────────────────────────────────────────────────────────┐
│                    错误处理决策树                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  收到错误响应                                                   │
│       │                                                         │
│       ▼                                                         │
│  是否为协议错误（-327xx）？                                     │
│  ├── 是 → 检查消息格式，记录日志，通常不可重试                  │
│  └── 否 ↓                                                       │
│                                                                 │
│  是否为认证错误（-32002, -32003）？                             │
│  ├── 是 → 重新认证或提示用户                                    │
│  └── 否 ↓                                                       │
│                                                                 │
│  是否为会话错误（-32000, -32006）？                             │
│  ├── 是 → 重新创建会话或加载会话                                │
│  └── 否 ↓                                                       │
│                                                                 │
│  是否为能力错误（-32004）？                                     │
│  ├── 是 → 检查能力声明，降级处理                                │
│  └── 否 ↓                                                       │
│                                                                 │
│  其他错误                                                        │
│  └── 记录日志，提示用户，可选重试                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.5 重试与超时

| 场景 | 默认超时 | 重试策略 |
|------|----------|----------|
| `initialize` | 30s | 不重试，失败即退出 |
| `session/new` | 10s | 不重试 |
| `session/prompt` | 无限制 | 不重试（用 cancel 中断） |
| `fs/read_text_file` | 5s | 最多重试 3 次 |
| `terminal/output` | 30s | 不重试 |

---

## 八、安全策略

### 8.1 威胁模型

ACP 面临的主要安全威胁：

| 威胁 | 说明 | 缓解措施 |
|------|------|----------|
| **未授权文件访问** | Agent 读取敏感文件 | 权限请求机制 + 工作目录限制 |
| **恶意命令执行** | Agent 运行危险命令 | `session/request_permission` + 终端权限 |
| **凭据泄露** | API Key 等敏感信息 | 认证机制 + 环境变量传递 |
| **会话劫持** | 恶意进程冒充 Agent | 子进程模型 + stdin/stdout 隔离 |
| **提示注入** | 恶意内容操纵 Agent | 用户确认 + 输出审查 |

### 8.2 权限模型

ACP 的核心安全机制是 **人在回路（Human-in-the-Loop）权限请求**：

```
┌─────────────────────────────────────────────────────────────────┐
│                    权限请求流程                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Agent 决定执行敏感操作                                        │
│       │                                                         │
│       ▼                                                         │
│   ┌─────────────────────────────┐                              │
│   │ 1. 发送 tool_call (pending) │                              │
│   └────────────┬────────────────┘                              │
│                │                                                │
│                ▼                                                │
│   ┌─────────────────────────────┐                              │
│   │ 2. request_permission       │                              │
│   │    options: [allow, deny]   │                              │
│   └────────────┬────────────────┘                              │
│                │                                                │
│   ┌────────────▼────────────────┐                              │
│   │ 3. Client 展示权限对话框     │                              │
│   │    用户选择                  │                              │
│   └────────────┬────────────────┘                              │
│                │                                                │
│                ▼                                                │
│   ┌─────────────────────────────┐                              │
│   │ 4. 返回 PermissionResponse  │                              │
│   │    optionId: allow/deny     │                              │
│   └────────────┬────────────────┘                              │
│                │                                                │
│                ▼                                                │
│   ┌─────────────────────────────┐                              │
│   │ 5. 根据选择执行或取消        │                              │
│   └─────────────────────────────┘                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 8.3 工作目录隔离

`session/new` 的 `cwd` 参数限制 Agent 的文件访问边界：

```json
{
  "cwd": "/absolute/path/to/project"
}
```

**规则**：
- 所有文件路径必须为绝对路径
- Agent 不应访问 `cwd` 之外的文件（除非显式授权）
- `../` 路径穿越应被规范化拦截

### 8.4 认证机制

ACP 支持多种认证方法，由 Agent 在 `initialize` 响应中声明：

```json
{
  "authMethods": [
    {
      "method": "anthropic_api_key",
      "description": "Anthropic API Key"
    },
    {
      "method": "oauth",
      "description": "OAuth 2.0"
    }
  ]
}
```

### 8.5 安全最佳实践

| 实践 | 说明 |
|------|------|
| **最小权限** | Agent 仅请求必要权限 |
| **显式确认** | 敏感操作必须用户确认 |
| **路径校验** | 所有路径必须为绝对路径，校验穿越 |
| **stderr 日志** | 日志输出到 stderr，不污染 stdout |
| **子进程隔离** | Agent 作为子进程运行，崩溃不影响 Client |
| **Kill on Drop** | 连接断开时终止子进程 |
| **凭据保护** | API Key 通过环境变量传递，不硬编码 |

---

## 九、扩展机制

### 9.1 `_meta` 字段

所有协议类型都包含 `_meta` 字段（`{ [key: string]: unknown }`），用于附加自定义信息：

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "session/prompt",
  "params": {
    "sessionId": "sess_abc123",
    "prompt": [...],
    "_meta": {
      "traceparent": "00-80e1afed08e019fc1110464cfa66635c-7a085853722dc6d2-01",
      "zed.dev/debugMode": true
    }
  }
}
```

**保留键**（用于 W3C Trace Context，与 MCP/OpenTelemetry 互操作）：
- `traceparent`
- `tracestate`
- `baggage`

**规则**：实现**不得**在规范类型的根级别添加任何自定义字段，所有名称都保留给未来协议版本。

### 9.2 扩展方法

以**下划线 `_`** 开头的方法名保留给自定义扩展：

#### 9.2.1 自定义请求

```json
// 请求
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "_zed.dev/workspace/buffers",
  "params": { "language": "rust" }
}

// 响应
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "buffers": [
      { "id": 0, "path": "/home/user/project/src/main.rs" }
    ]
  }
}
```

若接收方不识别自定义方法，应返回标准错误：

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32601,
    "message": "Method not found"
  }
}
```

#### 9.2.2 自定义通知

```json
{
  "jsonrpc": "2.0",
  "method": "_zed.dev/file_opened",
  "params": { "path": "/home/user/project/src/editor.rs" }
}
```

**规则**：实现**应**忽略无法识别的自定义通知。

### 9.3 能力声明

通过能力对象的 `_meta` 字段声明扩展支持：

```json
{
  "agentCapabilities": {
    "loadSession": true,
    "_meta": {
      "zed.dev": {
        "workspace": true,
        "fileNotifications": true
      }
    }
  }
}
```

### 9.4 三类特性

| 类别 | 说明 | 兼容性 |
|------|------|--------|
| **Core ACP（稳定）** | 标准协议特性 | 所有实现保证兼容 |
| **Unstable 特性** | 实验性特性，可能变更 | 需显式 opt-in |
| **实现扩展** | 特定实现的自定义功能 | 不可移植，用 `_meta` 扩展 |

---

## 十、与 MCP 的关系

### 10.1 互补关系

> **MCP 让 Agent 能使用工具，ACP 让编辑器能驱动 Agent。**

- **MCP**：Agent ↔ 工具/数据源（纵向）
- **ACP**：编辑器 ↔ Agent（横向）
- 两者**互补**而非竞争，通常一起使用

### 10.2 对比表

| 维度 | ACP | MCP |
|------|-----|-----|
| **定位** | 编辑器 ↔ AI 编码 Agent | AI 应用 ↔ 工具/资源服务器 |
| **方向** | Client 调用 Agent | LLM 调用工具 |
| **会话模型** | 多轮对话 Session | 无状态工具调用 |
| **传输** | stdio（本地）/ HTTP、WS（远程） | stdio / HTTP / SSE |
| **设计重心** | 代码编辑器 UX（diff 显示、权限确认） | 工具扩展 |
| **复用关系** | 复用 MCP 数据类型，可转发 MCP servers | 独立协议 |

### 10.3 协作模式

ACP 在内部复用 MCP：编辑器把配置好的 MCP servers 传给 Agent，Agent 直接连接 MCP 服务。

```
┌─────────────────────────────────────────────────────────────────┐
│                  ACP 与 MCP 协作架构                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐                                              │
│   │   编辑器     │                                              │
│   └──────┬───────┘                                              │
│          │ ACP（编辑器 ↔ Agent）                                │
│          ▼                                                      │
│   ┌──────────────┐                                              │
│   │    Agent     │                                              │
│   └──────┬───────┘                                              │
│          │ MCP（Agent ↔ 工具）                                  │
│          ├──────────────┬──────────────┬──────────────┐         │
│          ▼              ▼              ▼              ▼         │
│   ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ │
│   │ 文件系统   │ │  数据库    │ │  Git       │ │  外部 API  │ │
│   │ MCP Server │ │ MCP Server │ │ MCP Server │ │ MCP Server │ │
│   └────────────┘ └────────────┘ └────────────┘ └────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 10.4 配置 MCP Servers

`session/new` 时可传入 MCP servers 配置：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "ghp_..." }
    }
  }
}
```

---

## 十一、使用示例

### 11.1 TypeScript 实现最小 Agent

```typescript
/**
 * 最小 ACP Agent 实现（TypeScript）
 * 使用 @agentclientprotocol/sdk
 */
import { Agent } from '@agentclientprotocol/sdk';

class MyAgent extends Agent {
  // 1. 初始化握手
  async initialize(params: any): Promise<any> {
    return {
      protocolVersion: 1,
      agentCapabilities: {
        loadSession: false,
        promptCapabilities: {
          image: false,
          audio: false,
          embeddedContext: false
        }
      },
      agentInfo: {
        name: 'my-agent',
        title: 'My Agent',
        version: '1.0.0'
      },
      authMethods: []
    };
  }

  // 2. 创建新会话
  async newSession(params: any): Promise<any> {
    const sessionId = `sess_${Date.now()}`;
    return {
      sessionId,
      workspaceDir: params.cwd
    };
  }

  // 3. 处理 prompt
  async prompt(params: any): Promise<any> {
    const userText = params.prompt
      .filter((p: any) => p.type === 'text')
      .map((p: any) => p.text)
      .join(' ');

    // 流式返回更新
    this.notify('session/update', {
      sessionId: params.sessionId,
      update: {
        sessionUpdate: 'agent_message_chunk',
        content: { type: 'text', text: '正在处理...' }
      }
    });

    // 调用 LLM 处理
    const response = await callLLM(userText);

    this.notify('session/update', {
      sessionId: params.sessionId,
      update: {
        sessionUpdate: 'agent_message_chunk',
        content: { type: 'text', text: response }
      }
    });

    return { stopReason: 'end_turn' };
  }

  // 4. 设置模式（可选）
  async setMode(params: any): Promise<any> {
    return {};
  }
}

// 启动 Agent
const agent = new MyAgent();
agent.run();
```

### 11.2 Python 实现（使用 Pydantic AI Harness）

```python
"""
ACP Agent 实现（Python）
使用 pydantic-ai-harness 的实验性 ACP 适配器
"""
import warnings
from pydantic_ai import Agent
from pydantic_ai_harness.experimental import HarnessExperimentalWarning
from pydantic_ai_harness.experimental.acp import run_acp_stdio_sync

# 静默实验性警告
warnings.filterwarnings('ignore', category=HarnessExperimentalWarning)

def build_agent() -> Agent[None, str]:
    """构建 Pydantic AI Agent"""
    return Agent(
        'anthropic:claude-sonnet-4-6',
        instructions='你是一个专业的编码助手。'
    )

if __name__ == '__main__':
    # 作为 ACP Agent 运行，编辑器会以子进程方式启动此脚本
    run_acp_stdio_sync(build_agent())
```

**编辑器配置（Zed `settings.json`）**：

```json
{
  "agent_servers": {
    "My Pydantic AI Agent": {
      "command": "python",
      "args": ["/path/to/my_acp_agent.py"]
    }
  }
}
```

### 11.3 Rust 实现最小 Client

```rust
//! 最小 ACP Client 实现（Rust）
use agent_client_protocol::{Client, Request};
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use tokio::process::{Child, Command, ChildStdin, ChildStdout};
use tokio::sync::mpsc;

struct MyClient {
    child: Child,
    stdin: ChildStdin,
    stdout: BufReader<ChildStdout>,
}

impl MyClient {
    async fn spawn(command: &str, args: &[&str]) -> anyhow::Result<Self> {
        let mut child = Command::new(command)
            .args(args)
            .stdin(std::process::Stdio::piped())
            .stdout(std::process::Stdio::piped())
            .stderr(std::process::Stdio::piped())
            .spawn()?;

        let stdin = child.stdin.take().unwrap();
        let stdout = BufReader::new(child.stdout.take().unwrap());

        Ok(Self { child, stdin, stdout })
    }

    async fn send_request(&mut self, id: u64, method: &str, params: serde_json::Value) -> anyhow::Result<()> {
        let request = serde_json::json!({
            "jsonrpc": "2.0",
            "id": id,
            "method": method,
            "params": params
        });
        let mut line = serde_json::to_string(&request)?;
        line.push('\n');
        self.stdin.write_all(line.as_bytes()).await?;
        Ok(())
    }

    async fn initialize(&mut self) -> anyhow::Result<()> {
        self.send_request(1, "initialize", serde_json::json!({
            "protocolVersion": 1,
            "clientCapabilities": {
                "fileSystem": { "readTextFile": true, "writeTextFile": true }
            },
            "clientInfo": { "name": "my-client", "version": "0.1.0" }
        })).await?;

        // 读取响应
        let mut line = String::new();
        self.stdout.read_line(&mut line).await?;
        let response: serde_json::Value = serde_json::from_str(&line)?;
        println!("Agent 能力: {:?}", response["result"]["agentCapabilities"]);
        Ok(())
    }
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let mut client = MyClient::spawn("python", &["my_agent.py"]).await?;
    client.initialize().await?;

    // 保持运行
    client.child.wait().await?;
    Ok(())
}
```

### 11.4 NDJSON 原始交互示例

直接用命令行观察 ACP 交互（以 `claude-code` 为例）：

```bash
# 启动 Agent，通过 stdin 发送 NDJSON
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":1,"clientCapabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | claude-code --acp
```

**`initialize` 交互**：

```
→ {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":1,"clientCapabilities":{"fileSystem":{"readTextFile":true,"writeTextFile":true},"terminal":true},"clientInfo":{"name":"zed","version":"0.180.0"}}}
← {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":1,"agentCapabilities":{"loadSession":true,"promptCapabilities":{"image":false,"audio":false,"embeddedContext":false},"mcpCapabilities":{"http":false,"sse":false},"sessionCapabilities":{"resume":{},"close":{}}},"agentInfo":{"name":"claude-code","title":"Claude Code","version":"1.0.0"},"authMethods":[]}}
```

**`session/new` 交互**：

```
→ {"jsonrpc":"2.0","id":2,"method":"session/new","params":{"cwd":"/path/to/project"}}
← {"jsonrpc":"2.0","id":2,"result":{"sessionId":"sess-ab12cd","workspaceDir":"/path/to/project"}}
```

**`session/prompt` 交互**：

```
→ {"jsonrpc":"2.0","id":3,"method":"session/prompt","params":{"sessionId":"sess-ab12cd","prompt":[{"type":"text","text":"解释 main.rs"}]}}
← {"jsonrpc":"2.0","method":"session/update","params":{"sessionId":"sess-ab12cd","update":{"sessionUpdate":"agent_message_chunk","content":{"type":"text","text":"正在分析..."}}}}
← {"jsonrpc":"2.0","method":"session/update","params":{"sessionId":"sess-ab12cd","update":{"sessionUpdate":"tool_call","toolCallId":"tc-1","title":"Read file","kind":"read","status":"pending","rawInput":{"path":"/path/to/main.rs"}}}}
← {"jsonrpc":"2.0","method":"session/update","params":{"sessionId":"sess-ab12cd","update":{"sessionUpdate":"tool_call","toolCallId":"tc-1","status":"completed"}}}
← {"jsonrpc":"2.0","method":"session/update","params":{"sessionId":"sess-ab12cd","update":{"sessionUpdate":"agent_message_chunk","content":{"type":"text","text":"这个函数的作用是..."}}}}
← {"jsonrpc":"2.0","id":3,"result":{"stopReason":"end_turn"}}
```

---

## 十二、生态与采纳

### 12.1 支持的编辑器（Client）

| 编辑器 | 支持状态 | 说明 |
|--------|---------|------|
| **Zed** | ✅ 官方 | ACP 发起方，原生支持 |
| **JetBrains IDEs** | ✅ 官方 | IntelliJ、PyCharm、Rider 等 |
| **Neovim** | ✅ 社区 | 通过插件支持 |
| **Emacs** | ✅ 社区 | 通过插件支持 |
| **VS Code** | ✅ 社区 | 通过扩展支持 |
| **Obsidian** | ✅ 社区 | 通过插件支持 |
| **marimo** | ✅ 社区 | Python notebook 集成 |

### 12.2 兼容的 Agent

| Agent | 说明 |
|-------|------|
| **Claude Code** | Anthropic 官方 CLI Agent |
| **Gemini CLI** | Google 官方 CLI Agent |
| **Aider** | 开源 AI 编程助手 |
| **Pydantic AI** | 通过 harness 适配器支持 |
| **ZeroClaw** | 内置 ACP 支持 |
| **Autohand** | 内置 ACP 模式 |

### 12.3 SDK 库

| 语言 | 包名 | 安装 |
|------|------|------|
| **TypeScript** | `@agentclientprotocol/sdk` | `npm install @agentclientprotocol/sdk` |
| **Python** | `agent-client-protocol` | `pip install agent-client-protocol` |
| **Rust** | `agent-client-protocol` | `cargo add agent-client-protocol` |
| **Kotlin** | `acp-kotlin` | Maven/Gradle |
| **Java** | 即将发布 | - |
| **Go** | 即将发布 | - |

### 12.4 版本管理

| 版本 | 状态 | 说明 |
|------|------|------|
| **v1** | ✅ 稳定 | 当前推荐版本 |
| **v2** | 🔄 规划中 | 增量特性 |

**版本协商规则**：
- `protocolVersion` 是 `uint16`（0-65535），标识 MAJOR 版本
- 线兼容性由初始化时协商的 `protocolVersion` 决定，而非 SDK 版本号
- Schema artifacts 按版本发布（`schema/v1`、`schema/v2`）
- JSON Schema 文件附加到 GitHub Releases

---

## 十三、最佳实践

### 13.1 Client 实现最佳实践

1. **stdio 隔离**：stdout 只读 NDJSON，日志输出到 stderr
2. **Kill on Drop**：连接断开时终止子进程
3. **100ms 启动检测**：spawn 后延迟 100ms 检测早期退出
4. **能力检查**：调用可选方法前检查能力声明
5. **绝对路径**：所有文件路径使用绝对路径
6. **行号从 1 开始**：遵循编辑器惯例
7. **每个 prompt 一个响应**：即使取消也必须返回 `PromptResponse`
8. **`_meta` 传播**：传播 traceparent 等追踪字段

### 13.2 Agent 实现最佳实践

1. **流式输出**：用 `session/update` 流式返回，避免长时间无响应
2. **分块传输**：文本块保持在 wire 限制内
3. **diff 渲染**：文件修改用 `DiffContent`，便于编辑器渲染
4. **权限请求**：敏感操作前主动请求权限
5. **工具状态**：及时更新工具调用状态（pending → in_progress → completed）
6. **stderr 日志**：所有日志输出到 stderr
7. **会话恢复**：支持 `loadSession` 时完整回放历史
8. **优雅取消**：`session/cancel` 后快速终止并返回响应

### 13.3 常见陷阱

| 陷阱 | 解决方案 |
|------|----------|
| stdout 输出非 JSON | 所有日志输出到 stderr |
| 路径使用相对路径 | 统一使用绝对路径 |
| 行号从 0 开始 | 行号从 1 开始 |
| 未检查能力就调用 | 调用前检查能力声明 |
| prompt 无响应 | 即使取消也必须返回 PromptResponse |
| 自定义字段放根级 | 使用 `_meta` 字段扩展 |
| 嵌入式换行符 | NDJSON 每行一条消息，不能有嵌入换行 |
| 忽略版本协商 | 初始化时协商 protocolVersion |

---

## 十四、与其他协议对比

### 14.1 协议生态全景

| 协议 | 全称 | 解决问题 | 方向 |
|------|------|---------|------|
| **ACP**（本文） | Agent Client Protocol | 编辑器 ↔ Agent | 纵向（Client → Agent） |
| **MCP** | Model Context Protocol | Agent ↔ 工具 | 纵向（Agent → 工具） |
| **A2A** | Agent to Agent | Agent ↔ Agent | 横向 |
| **ACP**（AgentUnion） | Agent Communication Protocol | Agent ↔ Agent | 横向 |

### 14.2 详细对比

| 维度 | ACP（Zed） | MCP | A2A | ACP（AgentUnion） |
|------|-----------|-----|-----|-------------------|
| **发起方** | Zed Industries | Anthropic | Google | AgentUnion |
| **传输** | stdio NDJSON | stdio/HTTP/SSE | JSON-RPC | HTTPS/WSS/SSE |
| **会话模型** | 多轮 Session | 无状态 | 任务委派 | 多轮 Session |
| **身份体系** | 子进程模型 | 动态凭证 | Agent Card | AID + PKI |
| **典型场景** | 编辑器集成 | 工具扩展 | 跨组织协作 | 智能体互联网 |
| **类比** | LSP for agents | USB-C for tools | HTTP for agents | TCP/IP for agents |

### 14.3 协作关系

```
┌─────────────────────────────────────────────────────────────────┐
│                  Agent 协议生态协作                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐                                              │
│   │   编辑器     │                                              │
│   └──────┬───────┘                                              │
│          │ ACP（Zed）：编辑器驱动 Agent                         │
│          ▼                                                      │
│   ┌──────────────┐                                              │
│   │    Agent     │◄───── A2A / ACP（AgentUnion）：Agent 协作    │
│   └──────┬───────┘                                              │
│          │ MCP：Agent 调用工具                                  │
│          ├──────────────┬──────────────┬──────────────┐         │
│          ▼              ▼              ▼              ▼         │
│   ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ │
│   │ 文件系统   │ │  数据库    │ │  Git       │ │  外部 API  │ │
│   └────────────┘ └────────────┘ └────────────┘ └────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 十五、总结

### 15.1 核心要点

| 要点 | 说明 |
|------|------|
| **协议定位** | 编辑器 ↔ AI 编码 Agent 的标准协议，"Agent 界的 LSP" |
| **核心架构** | JSON-RPC 2.0 over stdio（NDJSON），Client 启动 Agent 子进程 |
| **核心概念** | Client（编辑器）、Agent（AI 程序）、Session（会话）、Capability（能力） |
| **关键流程** | initialize → session/new → session/prompt → session/update → PromptResponse |
| **安全机制** | 人在回路权限请求、工作目录隔离、stderr 日志、Kill on Drop |
| **扩展机制** | `_meta` 字段 + 下划线前缀方法 + 能力声明 |
| **与 MCP 关系** | 互补：MCP 连工具，ACP 连编辑器 |

### 15.2 选型决策

```
你需要让编辑器集成 AI Agent 吗？
├── 是 → ACP（Zed）✅
│
└── 否 ↓

你需要让 Agent 调用外部工具吗？
├── 是 → MCP ✅
│
└── 否 ↓

你需要让 Agent 之间互相协作吗？
├── 是 → A2A 或 ACP（AgentUnion）
│
└── 否 → 重新评估需求
```

### 15.3 一句话总结

> **ACP（Agent Client Protocol）是 Zed 主导的开放标准，用 JSON-RPC 2.0 over stdio 标准化编辑器与 AI 编码 Agent 的通信，让任意 Agent × 任意编辑器自由组合，被誉为"Agent 界的 LSP"。**

---

## 参考资料

- [Agent Client Protocol 官方文档](https://agentclientprotocol.com/)
- [Agent Client Protocol GitHub](https://github.com/agentclientprotocol/agent-client-protocol)
- [Zed 外部 Agent 文档](https://zed.dev/docs/ai/external-agents)
- [Zed ACP 页面](https://zed.dev/acp)
- [JetBrains AI Assistant ACP](https://www.jetbrains.com/help/ai-assistant/acp.html)
- [ACP 协议规范 v1](https://agentclientprotocol.com/protocol/v1/overview.md)
- [ACP 扩展机制](https://agentclientprotocol.com/protocol/extensibility)
- [ACP 客户端最佳实践](https://github.com/open-runtime/dart_acp/blob/main/specs/acp-client-best-practices.md)
- [Pydantic AI ACP 集成](https://pydantic.dev/docs/ai/harness/acp/)
- [ACP 生态分析](https://github.com/Oaklight/agentabi/blob/main/research/03_zed_acp_ecosystem.md)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [JSON-RPC 2.0 规范](https://www.jsonrpc.org/specification)
