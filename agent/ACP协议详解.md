# ACP 智能体通信协议详解

> **文档说明**：本文档系统阐述 ACP（Agent Communication Protocol，智能体通信协议）的核心概念、技术架构、数据传输流程、消息格式规范、安全机制及应用场景。由于 "ACP" 在 Agent 领域存在两个主流流派（AgentUnion ACP 与 IBM/BeeAI ACP），本文以 **AgentUnion ACP**（构建"智能体互联网"的完整协议体系）为主线进行深度解析，并在第十一章对照说明 **IBM/BeeAI ACP**（基于 REST 的轻量级互操作协议，已于 2025 年并入 Linux Foundation 的 A2A 协议）。文档包含版本信息、兼容性说明、关键参数定义、异常处理策略及示例代码、交互流程图，便于开发人员快速掌握协议细节并进行系统集成。

## 目录

- [一、协议概述](#一协议概述)
- [二、ACP 命名歧义与流派说明](#二acp-命名歧义与流派说明)
- [三、核心概念](#三核心概念)
- [四、技术架构](#四技术架构)
- [五、数据传输流程](#五数据传输流程)
- [六、消息格式规范](#六消息格式规范)
- [七、安全机制](#七安全机制)
- [八、数据规范](#八数据规范)
- [九、版本信息与兼容性](#九版本信息与兼容性)
- [十、应用场景](#十应用场景)
- [十一、IBM/BeeAI ACP 对照](#十一ibmbeeai-acp-对照)
- [十二、异常处理策略](#十二异常处理策略)
- [十三、示例代码与集成实践](#十三示例代码与集成实践)
- [十四、与主流协议对比](#十四与主流协议对比)
- [十五、总结与最佳实践](#十五总结与最佳实践)

---

## 一、协议概述

### 1.1 协议定位

**ACP（Agent Communication Protocol，智能体通信协议）** 是一套开放协议，用于解决 Agent 互相通信协作的问题，目标是达到 **Agent 功能复用、效率最优**，使企业和开发者可以用最低成本开发出可用于生产级部署的 Agent 应用。

ACP 定义了一系列 Agent 协议规范，涵盖：

- **身份标识与标准入口**：AID（Agent Identifier）
- **接入智能体互联网的机制**：AP（Access Point）接入点
- **数据规范**：Agent 可使用的数据、存储形式、目录结构
- **通信协议**：基于 HTTPS 的消息通信流程与时序
- **授权体系规范**：Agent 协作的授权与交易流程
- **行为与安全规范**：保证网络相容性与安全性

### 1.2 设计目标

| 目标 | 说明 |
|------|------|
| **开放性** | 任何 Agent 都可接入，不绑定特定厂商或框架 |
| **可靠性** | 基于 PKI 证书体系与双向认证，确保通信可信 |
| **可协作性** | 统一消息格式与流程，让异构 Agent 自由协作 |
| **可发现性** | 面向 Agent 搜索引擎原生友好设计 |
| **可迁移性** | 相同身份多设备部署，实现负载均衡 |
| **可复制性** | 不同身份本地部署，实现 Agent 服务级分享 |

### 1.3 核心定位一句话

> **MCP 让 Agent 能使用工具，ACP 让 Agent 能互相对话。**

ACP 解决的是 Agent 与 Agent 之间的横向通信问题，与 MCP（Agent 与工具/数据源的纵向连接）互补，而非竞争。

---

## 二、ACP 命名歧义与流派说明

"ACP" 在 Agent 领域是一个有歧义的缩写，至少存在两个主流协议流派，理解它们的区别对技术选型至关重要。

### 2.1 两大主流流派对比

| 维度 | AgentUnion ACP | IBM/BeeAI ACP |
|------|---------------|---------------|
| **发起方** | AgentUnion（国内） | IBM Research / BeeAI（国际） |
| **全称** | Agent Communication Protocol | Agent Communication Protocol |
| **定位** | 智能体互联网基础设施协议 | 跨框架智能体互操作协议 |
| **核心理念** | 类似互联网 TCP/IP，构建 Agent Internet | 基于 REST API 的轻量级消息传递 |
| **身份体系** | AID（Agent Identifier），类似域名 | Agent Manifest，能力声明 |
| **传输层** | HTTPS + WSS + SSE | REST API + SSE |
| **发现机制** | AP 接入点 + Agent 搜索引擎 | 在线端点 / well-known URL / 注册表 / 镜像 label |
| **SDK** | Python / TypeScript / C++ / Flutter | Python / TypeScript |
| **治理状态** | 活跃迭代中 | 已并入 Linux Foundation A2A（2025 年） |
| **典型场景** | 智能体互联网、跨厂商开放协作 | 内网气隙环境、本地优先部署 |

### 2.2 其他 ACP 变体（非主流，需注意区分）

| 名称 | 全称 | 说明 |
|------|------|------|
| **Agent Client Protocol** | ACP | Zed 编辑器团队主推，JSON-RPC 2.0 over stdio，用于编辑器接入编程 Agent |
| **Agent Control Protocol** | ACP | WebSocket 协议，让 AI Agent 操作应用 UI |
| **Agent Control Protocol** | ACP | 准入控制协议，B2B 机构环境自治 Agent 治理 |
| **AACP** | Agent Action Compression Protocol | 管道分隔的协调消息压缩格式 |

> **本文档后续章节**：第三至第十章、第十三章以 **AgentUnion ACP** 为主线深度解析；第十一章单独对照 **IBM/BeeAI ACP**。

---

## 三、核心概念

### 3.1 形象类比

> **Agent 如果是电脑，AID 就是它的网卡，而 ACP 是网线，AP 是路由器。**

### 3.2 Agent Internet（智能体互联网）

由 Agent 互联互通后构成的**开放性协作网络**。类似互联网，但节点是 Agent 而非主机。任何遵循 ACP 规范的 Agent 都可接入这个网络，与其他 Agent 进行发现、通信、协作。

### 3.3 Agent（智能体）

Agent 是 **LLM + Tools + ACP** 三要素封装的程序：

- **LLM**：大语言模型作为推理引擎
- **Tools**：可调用的外部工具集
- **ACP**：通信协议，让 Agent 能入网协作

### 3.4 AID（Agent Identifier，智能体身份标识）

每个智能体在网络中有唯一的身份标识 AID，是接入智能体互联网的前提。

#### 3.4.1 AID 格式

```
格式：{agent-name}.{ap-domain}
示例：
  weather_agent.ap1.agentunion.cn
  writing-bot.ap2.agentunion.cn
  research-agent.my-ap.com
```

#### 3.4.2 AID 双重属性

| 属性 | 说明 |
|------|------|
| **网络可寻址标识** | 通过接入点（AP）的泛域名解析实现的二级域名，作为 Agent 在浏览器中的标准入口 |
| **数字身份凭证** | 基于 PKI 的 X.509v3 证书，完成与接入点和其他 Agent 的身份认证 |

#### 3.4.3 AID 核心设计原则

- **唯一性**：采用 `<agent_name>.ap_domain` 的二级域名结构
- **分布式解析**：通过接入点（AP）的泛域名解析实现分布式命名空间管理
- **双因素标识**：同时包含网络可寻址标识（域名）和数字身份凭证（证书）

### 3.5 AP（Access Point，接入点）

Agent 通过 AP 接入智能体互联网，AP 为 Agent 完成身份认证、寻址查找、通信、数据存储等核心服务。

#### 3.5.1 AP 核心服务

| 服务 | 说明 |
|------|------|
| **AID 创建与管理** | 提供 AID 申请、颁发、续期、吊销服务 |
| **身份认证** | 基于 PKI 的双向证书认证 |
| **寻址查找** | 通过 AID 域名解析定位 Agent |
| **状态查询与发现** | 维护 Agent 在线状态，支持搜索引擎增量获取 |
| **公有数据管理** | 存储 Agent 的 AgentProfile 等公有数据 |
| **会话服务** | 提供 Agent 间会话的中继与管理 |
| **契约签名验证** | 为会话中产生的数字契约提供身份认证、签名和验证 |

#### 3.5.2 AP 分布式特性

Agent Internet 中存在大量 AP，Agent 可在**任意一个 AP** 上创建 AID，使用 AID 身份通过 AP 接入网络后与其他 Agent 通信。这种设计避免了单点故障，实现分布式治理。

### 3.6 User（用户）

Agent 能够接受用户的输入，以完成：

- **需求提出**：用户向 Agent 下达任务
- **信息补全**：用户补充 Agent 执行所需的上下文
- **授权与支付**：用户对关键操作或付费服务授权
- **关键选择**：执行流程中的分支决策

User 能够接受 Agent 的输出。

### 3.7 概念关系图

```
┌─────────────────────────────────────────────────────────────────┐
│                  Agent Internet（智能体互联网）                  │
│                                                                 │
│   ┌──────────┐    ACP协议    ┌──────────┐    ACP协议    ┌──────┐│
│   │ Agent A  │◄────────────►│   AP     │◄────────────►│Agent B││
│   │ (AID-A)  │              │ 接入点   │              │(AID-B)││
│   └────┬─────┘              └────┬─────┘              └──────┘││
│        │                         │                             │
│        │                         │   ┌──────────────────┐      │
│        │                         └──►│  AP 核心服务     │      │
│        │                             │  · 身份认证      │      │
│        │                             │  · 寻址查找      │      │
│        │                             │  · 会话管理      │      │
│        │                             │  · 数据存储      │      │
│        │                             │  · 契约签名      │      │
│        │                             └──────────────────┘      │
│        │                                                       │
│        ▼                                                       │
│   ┌──────────┐                                                 │
│   │  User    │  (需求/授权/支付)                               │
│   └──────────┘                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 四、技术架构

### 4.1 分层架构

ACP 采用分层设计，各层职责清晰、互不耦合：

```
┌─────────────────────────────────────────────────────────────────┐
│                     应用层（Application Layer）                  │
│   Agent 业务逻辑、LLM 推理、工具调用                             │
├─────────────────────────────────────────────────────────────────┤
│                     协议层（Protocol Layer）                     │
│   ACP 消息格式、会话时序、行为规范                               │
├─────────────────────────────────────────────────────────────────┤
│                     身份层（Identity Layer）                     │
│   AID 证书、PKI 认证、数字契约签名                              │
├─────────────────────────────────────────────────────────────────┤
│                     传输层（Transport Layer）                    │
│   HTTPS + WSS + SSE                                             │
├─────────────────────────────────────────────────────────────────┤
│                     发现层（Discovery Layer）                    │
│   AP 注册、Agent 搜索引擎、AgentProfile                         │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 各层职责说明

| 层级 | 职责 | 关键组件 |
|------|------|----------|
| **应用层** | Agent 业务执行、LLM 推理、工具编排 | LLM、Tools、业务逻辑 |
| **协议层** | 定义消息格式、会话时序、行为规范 | ACP Message、Session |
| **身份层** | 身份认证、授权、契约签名验证 | AID 证书、PKI、DKR |
| **传输层** | 数据可靠传输、加密通道 | HTTPS、WSS、SSE |
| **发现层** | Agent 注册、能力发现、搜索引擎 | AP、AgentProfile |

### 4.3 Agent 三要素架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Agent 架构                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│   │    LLM      │  │   Tools     │  │    ACP      │            │
│   │  推理引擎   │  │  工具集     │  │  通信协议   │            │
│   ├─────────────┤  ├─────────────┤  ├─────────────┤            │
│   │ • 意图理解  │  │ • API 调用  │  │ • 消息收发  │            │
│   │ • 任务规划  │  │ • 数据查询  │  │ • 会话管理  │            │
│   │ • 决策执行  │  │ • 文件操作  │  │ • 身份认证  │            │
│   │ • 结果生成  │  │ • 外部集成  │  │ • 契约签署  │            │
│   └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│   三要素协同：LLM 决策 → Tools 执行 → ACP 协作                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.4 AP 接入点架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      AP（Access Point）架构                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    接口层                                │   │
│   │   HTTPS API | WSS | SSE | 泛域名解析                    │   │
│   └────────────────────────┬────────────────────────────────┘   │
│                            │                                    │
│   ┌────────────────────────▼────────────────────────────────┐   │
│   │                    服务层                                │   │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│   │  │ AID 管理 │ │ 会话服务 │ │ 数据存储 │ │ 契约服务 │  │   │
│   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│   └────────────────────────┬────────────────────────────────┘   │
│                            │                                    │
│   ┌────────────────────────▼────────────────────────────────┐   │
│   │                    安全层                                │   │
│   │  PKI 认证 | OCSP | CRL | 加密存储 | 审计日志            │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 五、数据传输流程

### 5.1 Agent 接入流程

```
┌─────────────────────────────────────────────────────────────────┐
│                   Agent 接入智能体互联网流程                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 申请 AID                                                    │
│     Agent ──生成密钥对（公钥+私钥）──► 向 AP 提交公钥和身份信息 │
│                                                                 │
│  2. AP 颁发证书                                                  │
│     AP 验证身份 ──► 用 AP 私钥签名 ──► 返回 X.509v3 证书        │
│                                                                 │
│  3. Agent 验证证书                                              │
│     检查 AP 签名（根证书验证）─► 验证有效期/域名/CRL/OCSP       │
│                                                                 │
│  4. 获得 AID                                                    │
│     Agent 妥善保存证书和私钥，获得有效 AID                       │
│                                                                 │
│  5. 接入网络                                                    │
│     Agent 使用 AID 通过 AP 双向认证后接入智能体互联网            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Agent 间会话时序

```
Agent A                    AP                      Agent B
  │                         │                         │
  │  1. 发起会话请求        │                         │
  │  (携带 AID-A 证书)      │                         │
  ├────────────────────────►│                         │
  │                         │  2. 寻址 Agent B        │
  │                         │  (通过 AID-B 解析)      │
  │                         ├────────────────────────►│
  │                         │                         │
  │                         │  3. Agent B 响应        │
  │                         │  (携带 AID-B 证书)      │
  │                        ◄────────────────────────┤
  │                         │                         │
  │  4. 双向认证            │                         │
  │  (AP 协助证书验证)      │                         │
  │◄───────────────────────►│◄───────────────────────►│
  │                         │                         │
  │  5. 建立会话通道        │                         │
  │◄───────────────────────►│◄───────────────────────►│
  │                         │                         │
  │  6. 消息交互（通过 AP 中继）                      │
  ├────────────────────────►│────────────────────────►│
  │                         │                         │
  │  7. 返回结果            │                         │
  │◄────────────────────────┤◄────────────────────────┤
  │                         │                         │
  │  8. 数字契约签署        │                         │
  │◄───────────────────────►│◄───────────────────────►│
  │                         │                         │
  │  9. 会话结束            │                         │
  │◄────────────────────────┤◄────────────────────────┤
  │                         │                         │
```

### 5.3 通信协议层次

ACP 数据传输基于 **HTTPS 协议**，Agent 需要通过接入点及其提供的会话服务完成与其他 Agent 之间的通信：

| 通信类型 | 协议 | 用途 |
|---------|------|------|
| **请求-响应** | HTTPS | 同步消息交互、API 调用 |
| **实时双向** | WSS（WebSocket Secure） | 实时会话、低延迟交互 |
| **流式推送** | SSE（Server-Sent Events） | 长任务进度、流式输出 |
| **事件通知** | WSS | Agent 状态变更、异步事件 |

### 5.4 会话生命周期

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  创建    │───►│  认证    │───►│  通信    │───►│  结束    │
│ Session  │    │ Auth     │    │ Message  │    │ Close    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │
     │               │               │               │
     ▼               ▼               ▼               ▼
 申请会话ID      双向证书认证     消息收发        契约签署
 分配会话资源    建立加密通道     状态维护        资源释放
```

---

## 六、消息格式规范

### 6.1 ACP 消息基础结构

ACP 消息基于 JSON 格式，包含消息头（Header）和消息体（Body）两部分：

```json
{
  "header": {
    "message_id": "msg-uuid-xxxxx",
    "from": "agent-a.ap1.agentunion.cn",
    "to": "agent-b.ap2.agentunion.cn",
    "timestamp": "2026-08-06T10:30:00Z",
    "message_type": "request",
    "session_id": "session-uuid-xxxxx",
    "protocol_version": "1.0",
    "reply_to": "msg-uuid-xxxxx"
  },
  "body": {
    "content": {},
    "metadata": {}
  }
}
```

### 6.2 消息头字段定义

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `message_id` | string | ✅ | 消息唯一标识（UUID） |
| `from` | string | ✅ | 发送方 AID |
| `to` | string | ✅ | 接收方 AID |
| `timestamp` | string | ✅ | ISO 8601 时间戳 |
| `message_type` | string | ✅ | 消息类型（见 6.3） |
| `session_id` | string | ✅ | 会话标识 |
| `protocol_version` | string | ✅ | 协议版本 |
| `reply_to` | string | ❌ | 回复的消息 ID |

### 6.3 消息类型

| 类型 | 说明 | 典型场景 |
|------|------|----------|
| `request` | 请求消息 | 发起任务、调用能力 |
| `response` | 响应消息 | 返回结果、确认接收 |
| `notification` | 通知消息 | 状态更新、事件推送 |
| `error` | 错误消息 | 异常报告、失败通知 |
| `consensus` | 共识消息 | 多 Agent 投票、协商 |
| `action` | 动作消息 | 执行指令、工具调用 |

### 6.4 消息体结构

#### 6.4.1 请求消息示例

```json
{
  "header": {
    "message_id": "req-001",
    "from": "orchestrator.ap1.agentunion.cn",
    "to": "research-agent.ap2.agentunion.cn",
    "timestamp": "2026-08-06T10:30:00Z",
    "message_type": "request",
    "session_id": "sess-001",
    "protocol_version": "1.0"
  },
  "body": {
    "content": {
      "action": "research",
      "query": "分析 2026 年 AI Agent 市场趋势",
      "parameters": {
        "depth": "comprehensive",
        "format": "report",
        "language": "zh-CN"
      }
    },
    "metadata": {
      "priority": "high",
      "timeout": 300,
      "retry_count": 0
    }
  }
}
```

#### 6.4.2 响应消息示例

```json
{
  "header": {
    "message_id": "resp-001",
    "from": "research-agent.ap2.agentunion.cn",
    "to": "orchestrator.ap1.agentunion.cn",
    "timestamp": "2026-08-06T10:35:00Z",
    "message_type": "response",
    "session_id": "sess-001",
    "protocol_version": "1.0",
    "reply_to": "req-001"
  },
  "body": {
    "content": {
      "status": "success",
      "result": {
        "summary": "2026 年 AI Agent 市场呈现爆发式增长...",
        "report_url": "https://...",
        "data": {}
      }
    },
    "metadata": {
      "processing_time": 285,
      "tokens_used": 15000
    }
  }
}
```

#### 6.4.3 错误消息示例

```json
{
  "header": {
    "message_id": "err-001",
    "from": "research-agent.ap2.agentunion.cn",
    "to": "orchestrator.ap1.agentunion.cn",
    "timestamp": "2026-08-06T10:30:05Z",
    "message_type": "error",
    "session_id": "sess-001",
    "protocol_version": "1.0",
    "reply_to": "req-001"
  },
  "body": {
    "content": {
      "error_code": "RATE_LIMIT_EXCEEDED",
      "error_message": "请求频率超过限制",
      "details": {
        "limit": 100,
        "window": "1m",
        "retry_after": 30
      }
    },
    "metadata": {
      "retryable": true
    }
  }
}
```

### 6.5 多部件消息（Multi-Part Message）

ACP 支持多模态消息，一条消息可包含多种 MIME 类型的部件：

```json
{
  "header": { ... },
  "body": {
    "content": {
      "parts": [
        {
          "type": "text/plain",
          "content": "分析结果如下："
        },
        {
          "type": "application/json",
          "content": { "metric": "growth", "value": "150%" }
        },
        {
          "type": "image/png",
          "content": "base64-encoded-image-data",
          "encoding": "base64"
        }
      ]
    }
  }
}
```

---

## 七、安全机制

### 7.1 证书管理体系

ACP 基于 **PKI（公钥基础设施）** 构建完整的证书管理体系，使用 **ECDSA NIST-P 384** 椭圆曲线算法。

### 7.2 AID 身份证书结构

| 字段 | 说明 | 示例 |
|------|------|------|
| `SerialNumber` | 证书序列号（128 位） | 345355563353335335 |
| `Subject.Organization` | 主体组织 | agentunion.cn |
| `Subject.CommonName` | 主体名称（须与 AID 一致） | weather_agent.ap1.net |
| `Subject Public Key Info` | 主体公钥信息/算法 | NIST-P 384 |
| `NotBefore` | 证书有效期起始 | 2025-05-01 00:00:00 |
| `NotAfter` | 证书有效期结束 | 2025-10-31 23:59:59 |
| `KeyUsage` | 证书用途 | - |
| `ExtKeyUsage` | 证书扩展用途 | - |
| `BasicConstraintsValid` | 基本约束 | true |
| `IsCA` | 是否是 CA | false |
| `MaxPathLen` | 非CA只能是 0 | 0 |
| `OCSP` | 证书 OCSP 访问网址 | https://agentunion.cn/ocsp/xxxx |
| `CAIssuers` | 颁发者证书下载地址 | https://agentunion.cn/certs/xxx |

### 7.3 证书生命周期管理

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  申请    │───►│  颁发    │───►│  使用    │───►│  续期/吊销 │
│ Apply    │    │ Issue    │    │ Use      │    │ Renew    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │
     ▼               ▼               ▼               ▼
 生成密钥对      AP 签名颁发      双向认证        自动续期(<7天)
 提交公钥        返回证书        加密通信        OCSP/CRL 吊销
```

### 7.4 双向认证流程

```
Agent A                              Agent B
   │                                    │
   │  1. 交换证书                       │
   ├───────────────────────────────────►│
   │◄───────────────────────────────────┤
   │                                    │
   │  2. A 验证 B 证书                  │
   │     · 验证主体信息                 │
   │     · 验证证书链到根证书           │
   │     · 验证有效期、域名、CRL/OCSP   │
   │                                    │
   │  3. A 发送随机口令给 B             │
   ├───────────────────────────────────►│
   │                                    │
   │  4. B 用私钥签名口令               │
   │◄───────────────────────────────────┤
   │                                    │
   │  5. A 用 B 公钥验证签名            │
   │     确认 B 持有对应私钥            │
   │                                    │
   │  6. B 对 A 重复上述流程            │
   │                                    │
   │  ✅ 双向认证完成                   │
```

### 7.5 DKR（Dual-Key Recovery）双钥恢复机制

为解决 AID 私钥丢失导致的服务不可用问题，ACP 提供 DKR 机制：

#### 7.5.1 核心要求

| 要求 | 说明 |
|------|------|
| **可用性** | 私钥丢失后可通过备份密钥快速恢复身份 |
| **安全性** | 恢复操作需通过加密签名和接入点（AP）验证 |
| **最小权限** | 备份密钥仅具备有限恢复权限，不参与日常通信 |

#### 7.5.2 工作流程

```
┌─────────────────────────────────────────────────────────────────┐
│                  初始注册阶段                                    │
├─────────────────────────────────────────────────────────────────┤
│  1. 用户生成主 AID（A）和备份 AID（B）的密钥对（SK/PK）          │
│  2. A 使用 SK_A 签署授权书，允许 B 在特定条件下发起恢复请求     │
│  3. 将 A 和 B 的公钥及授权书提交至 AP 完成身份绑定              │
│  4. AP 验证授权书有效性后激活 DKR 功能                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  恢复执行阶段                                    │
├─────────────────────────────────────────────────────────────────┤
│  1. SK_A 丢失时，B 向 AP 提交恢复请求：                        │
│     · A 的 AID 标识                                             │
│     · 新生成的密钥对（SK_A'/PK_A'）                             │
│     · B 使用 SK_B 签名的恢复授权书                              │
│  2. AP 执行验证：                                               │
│     · 验证 B 的签名                                             │
│     · 验证授权书有效性                                          │
│     · 检查恢复条件                                              │
│  3. 验证通过后，AP 更新 A 的公钥为 PK_A'                       │
│  4. A 使用新私钥 SK_A' 恢复服务                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.6 数字契约

会话过程中产生的关键操作（如授权、交易、关键决策）通过数字契约固化：

| 特性 | 说明 |
|------|------|
| **不可篡改** | 基于数字签名，确保契约内容完整 |
| **可验证** | 任何第三方都可验证契约真实性 |
| **可追溯** | 完整记录操作链路，支持审计 |
| **法律效力** | 满足电子签名法要求 |

---

## 八、数据规范

### 8.1 Agent 数据目录结构

遵循 ACP 数据规范的 Agent 目录结构如下：

```
my-agent/
├── agentprofile.json       # Agent 档案（公有，用于发现）
├── config.json             # Agent 配置（私有）
├── credentials/            # 证书与密钥
│   ├── aid.crt             # AID 证书
│   ├── aid.key             # AID 私钥
│   └── ca.crt              # 根证书
├── data/                   # Agent 数据
│   ├── public/             # 公有数据（可分享）
│   └── private/            # 私有数据
├── logs/                   # 日志
└── README.md               # 说明文档
```

### 8.2 agentprofile.json 规范

AgentProfile 是 Agent 的公开档案，用于被搜索引擎和其他 Agent 发现：

```json
{
  "aid": "research-agent.ap1.agentunion.cn",
  "name": "研究助手",
  "description": "专业的市场研究与分析 Agent，支持多领域深度调研",
  "version": "1.0.0",
  "provider": {
    "organization": "Example Corp",
    "contact": "contact@example.com"
  },
  "capabilities": [
    "market-research",
    "data-analysis",
    "report-generation"
  ],
  "inputs": {
    "query": {
      "type": "string",
      "required": true,
      "description": "研究查询语句"
    },
    "depth": {
      "type": "string",
      "enum": ["quick", "standard", "comprehensive"],
      "default": "standard"
    }
  },
  "outputs": {
    "report": {
      "type": "object",
      "description": "研究报告"
    }
  },
  "pricing": {
    "model": "per-call",
    "price": 0.5,
    "currency": "USD"
  },
  "discovery": {
    "searchable": true,
    "category": "research"
  }
}
```

### 8.3 config.json 规范

Agent 的私有配置文件：

```json
{
  "aid": "research-agent.ap1.agentunion.cn",
  "ap_endpoint": "https://ap1.agentunion.cn",
  "llm": {
    "provider": "openai",
    "model": "gpt-4",
    "api_key_env": "OPENAI_API_KEY"
  },
  "tools": [
    {
      "name": "web-search",
      "enabled": true
    },
    {
      "name": "database",
      "enabled": true,
      "config": {
        "host": "localhost",
        "port": 5432
      }
    }
  ],
  "security": {
    "require_auth": true,
    "allowed_callers": [],
    "rate_limit": {
      "requests": 100,
      "window": "1m"
    }
  },
  "logging": {
    "level": "info",
    "path": "./logs"
  }
}
```

### 8.4 数据规范的价值

| 价值 | 说明 |
|------|------|
| **可发现性** | 遵循规范的 Agent 更容易被搜索引擎索引 |
| **可迁移性** | 相同身份多设备部署，实现负载均衡 |
| **可复制性** | 不同身份本地部署，实现 Agent 服务级分享 |
| **可分享性** | Agent 输出数据的分享更容易 |

---

## 九、版本信息与兼容性

### 9.1 协议版本

| 版本 | 发布时间 | 状态 | 主要特性 |
|------|----------|------|----------|
| 1.0 | 2025-05 | ✅ 稳定 | 初始版本，AID、AP、基础通信 |
| 1.1 | 2025-10 | ✅ 稳定 | 新增 DKR 双钥恢复机制 |
| 1.2 | 2026-03 | ✅ 稳定 | 增强多模态消息支持 |
| 2.0 | 2026-06（规划） | 🔄 规划中 | 跨组织信任、声誉快照可移植性 |

### 9.2 版本兼容性策略

| 策略 | 说明 |
|------|------|
| **向后兼容** | 新版本必须兼容旧版本消息格式 |
| **版本协商** | 通信前协商共同支持的最高版本 |
| **降级处理** | 不支持的新字段应忽略而非报错 |
| **版本字段** | 每条消息必须包含 `protocol_version` 字段 |

### 9.3 与其他协议的关系

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent 协议生态全景                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────┐       │
│   │  ACP（AgentUnion）                                   │       │
│   │  Agent ◄─────────────────────► Agent                │       │
│   │  智能体互联网基础设施协议                            │       │
│   └─────────────────────────────────────────────────────┘       │
│                          ▲ ▼ 互补                               │
│   ┌─────────────────────────────────────────────────────┐       │
│   │  MCP（Model Context Protocol）                       │       │
│   │  Agent ◄─────────────────────► Tools/Data           │       │
│   │  模型连接外部工具/数据                               │       │
│   └─────────────────────────────────────────────────────┘       │
│                                                                 │
│   ┌─────────────────────────────────────────────────────┐       │
│   │  A2A（Agent to Agent，Google）                        │       │
│   │  Agent ◄─────────────────────► Agent                │       │
│   │  通用交互范式（已吸收 IBM/BeeAI ACP）                │       │
│   └─────────────────────────────────────────────────────┘       │
│                                                                 │
│   ┌─────────────────────────────────────────────────────┐       │
│   │  ANP（Agent Network Protocol）                       │       │
│   │  Agent 组网和路由                                    │       │
│   │  底层网络层                                          │       │
│   └─────────────────────────────────────────────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 9.4 协议分工对比

| 协议 | 全称 | 解决的问题 | 类比 |
|------|------|-----------|------|
| **MCP** | Model Context Protocol | 模型连接外部工具/数据 | 给 Agent 装"手"和"眼" |
| **ACP** | Agent Communication Protocol | Agent 之间互相通信协作 | Agent 之间的"语言" |
| **A2A** | Agent to Agent | Agent 对 Agent 交互模式 | 通用交互范式 |
| **ANP** | Agent Network Protocol | Agent 组网和路由 | 底层网络层 |

---

## 十、应用场景

### 10.1 智能体互联网

**场景描述**：构建类似互联网的 Agent 协作网络，让全球 Agent 自由互通。

**典型应用**：
- 用户通过个人助理 Agent 调用专业研究 Agent 完成深度调研
- 企业 Agent 调用第三方风控 Agent 进行实时风险评估
- 多个 Agent 协作完成复杂工作流（如"分析投诉并生成解决方案"）

### 10.2 跨框架协作

**场景描述**：不同框架（LangChain、CrewAI、AutoGen 等）开发的 Agent 无缝协作。

```
┌─────────────────────────────────────────────────────────────┐
│  Before ACP：N 个 Agent = N×(N-1) 种集成方式 😱             │
│                                                             │
│  LangChain Agent ──(自定义API)──► CrewAI Agent              │
│  AutoGen Agent   ──(gRPC)────────► BeeAI Agent              │
│  Custom Agent    ──(WebSocket)────► OpenAI Agent            │
├─────────────────────────────────────────────────────────────┤
│  After ACP：N 个 Agent = 1 种协议搞定 ✅                    │
│                                                             │
│  LangChain Agent ──┐                                        │
│  CrewAI Agent    ──┤                                        │
│  AutoGen Agent   ──┼──── ACP 统一协议 ────► 自由互通        │
│  BeeAI Agent     ──┤                                        │
│  Custom Agent    ──┘                                        │
└─────────────────────────────────────────────────────────────┘
```

### 10.3 企业级 Agent 服务

**场景描述**：企业部署收费的 Agent 服务，通过 ACP 授权与交易规范快速上线。

**关键能力**：
- Agent 能力声明（AgentProfile）
- 标准化调用接口
- 内置授权与计费流程
- 数字契约保障交易可信

### 10.4 多 Agent 协作编排

**场景描述**：多个专业 Agent 协作完成复杂任务。

```
用户请求："分析客户投诉并生成解决方案"
    │
    ▼
┌─────────────┐
│ Orchestrator│ ── 调用 ──► ┌─────────────┐
│ 编排 Agent  │              │ 客服 Agent  │ ── 提取投诉信息
└─────────────┘              └─────────────┘
    │
    ├── 调用 ──► ┌─────────────┐
    │            │ 风控 Agent  │ ── 评估风险等级
    │            └─────────────┘
    │
    ├── 调用 ──► ┌─────────────┐
    │            │ 数据 Agent  │ ── 查询客户历史
    │            └─────────────┘
    │
    └── 调用 ──► ┌─────────────┐
                 │ 方案 Agent  │ ── 生成解决方案
                 └─────────────┘
                      │
                      ▼
                 返回给用户
```

### 10.5 Agent 搜索引擎

**场景描述**：Agent 搜索引擎增量获取 AP 下所有开放的 Agent 的 AgentProfile，让 Agent 被轻易发现，无需 Agent 额外做任何事情。

**特性**：
- 面向搜索引擎原生友好设计
- Agent 可配置是否开放给搜索引擎
- 增量索引，实时更新

---

## 十一、IBM/BeeAI ACP 对照

### 11.1 协议定位

**IBM/BeeAI ACP** 是 IBM Research 与 BeeAI 社区提出的智能体通信协议，**已于 2025 年并入 Linux Foundation 治理下的 A2A 协议**。它的核心思路是：把每个 Agent 暴露成标准 HTTP 服务，一条 curl 就能调用。

### 11.2 核心特征

#### 11.2.1 彻底 REST 化

每个 Agent 就是一个暴露标准 HTTP 端点的服务，发消息、收结果、路由请求都是普通 HTTP 调用。**不需要专用 SDK**，curl、Postman 就能直接对接，官方 SDK 只是可选的便利层。

#### 11.2.2 多模态消息

一条消息里可以并排放结构化数据、纯文本、图片乃至向量嵌入，靠 MIME 类型标注每一段（part）的格式，适配同时涉及大模型与视觉模型的混合流程。

#### 11.2.3 异步优先交互模型

ACP **默认异步，同时支持同步**：

| 模式 | 适用场景 | 实现方式 |
|------|---------|----------|
| **异步** | 长耗时、多步骤任务 | await/resume 维持会话连续性 |
| **同步** | 交互式、低延迟场景 | 直接 HTTP 调用 |
| **流式** | 进度推送、流式输出 | SSE（Server-Sent Events） |

#### 11.2.4 基于元数据的离线发现

Agent 元数据写在代码声明里（如 `@server.agent(name=..., metadata={...})`），运行起来就成了 Agent Manifest。获取 manifest 的四条路径：

| 方式 | 说明 | 在线要求 |
|------|------|:--------:|
| **在线端点查询** | `GET /agents` 或 `GET /agents/{name}` | ✅ 需在线 |
| **well-known URL** | `GET /.well-known/agent.yml` | ✅ 需可访问 |
| **中心化注册表** | 客户端查注册表找 Agent | ✅ 需联网 |
| **镜像 label** | 元数据嵌进容器镜像 label | ❌ 可离线 |

> **"离线发现"的含义**：只针对"发现"这一步，不针对"调用"。发现是搞清楚"这个 Agent 是谁、会什么、怎么调"，可以离线完成；调用依然走 REST，Agent 必须处于运行态。

### 11.3 两种 ACP 全面对比

| 维度 | AgentUnion ACP | IBM/BeeAI ACP |
|------|---------------|---------------|
| **设计哲学** | 构建智能体互联网（类 TCP/IP） | 轻量级 REST 互操作 |
| **身份体系** | AID（域名+证书双因素） | Agent Manifest（能力声明） |
| **传输协议** | HTTPS + WSS + SSE | REST + SSE |
| **发现机制** | AP 接入点 + 搜索引擎 | 在线端点 / well-known / 注册表 / 镜像 |
| **离线能力** | 弱（依赖 AP） | 强（镜像 label 离线发现） |
| **安全模型** | PKI 证书 + 双向认证 + DKR | Bearer Token + 可选 mTLS + JWS |
| **治理状态** | AgentUnion 独立运营 | 已并入 Linux Foundation A2A |
| **适用环境** | 开放互联网协作 | 内网气隙、本地优先部署 |
| **集成复杂度** | 较高（需 AP 部署） | 低（一条 curl 即可） |

### 11.4 选型建议

| 场景 | 推荐协议 | 理由 |
|------|---------|------|
| 开放互联网 Agent 协作 | AgentUnion ACP | 完整的身份体系与发现机制 |
| 内网气隙环境 | IBM/BeeAI ACP | 支持离线发现，无需公网 |
| 快速原型集成 | IBM/BeeAI ACP | REST 化，集成成本低 |
| 生产级收费 Agent 服务 | AgentUnion ACP | 内置授权与交易规范 |
| 跨组织可信协作 | 两者皆可（或 A2A） | 均支持，A2A 是融合方向 |

---

## 十二、异常处理策略

### 12.1 错误码体系

| 错误码 | 类别 | 说明 | 是否可重试 |
|--------|------|------|:----------:|
| `AUTH_FAILED` | 认证错误 | AID 证书无效或过期 | ❌ |
| `AUTH_EXPIRED` | 认证错误 | 证书已过期，需续期 | ❌ |
| `PERMISSION_DENIED` | 授权错误 | 无权限调用目标 Agent | ❌ |
| `AGENT_NOT_FOUND` | 寻址错误 | 目标 AID 不存在或离线 | ✅ |
| `AGENT_OFFLINE` | 寻址错误 | 目标 Agent 当前不在线 | ✅ |
| `RATE_LIMIT_EXCEEDED` | 限流错误 | 请求频率超过限制 | ✅ |
| `TIMEOUT` | 超时错误 | 请求超时 | ✅ |
| `INVALID_MESSAGE` | 协议错误 | 消息格式不合法 | ❌ |
| `VERSION_MISMATCH` | 协议错误 | 协议版本不兼容 | ❌ |
| `INTERNAL_ERROR` | 系统错误 | Agent 内部异常 | ✅ |
| `SERVICE_UNAVAILABLE` | 系统错误 | 服务暂不可用 | ✅ |

### 12.2 重试策略

```python
# 重试策略示例
RETRY_CONFIG = {
    "max_retries": 3,              # 最大重试次数
    "initial_delay": 1,            # 初始延迟（秒）
    "max_delay": 30,               # 最大延迟（秒）
    "backoff_multiplier": 2,       # 退避倍数
    "retryable_errors": [          # 可重试的错误码
        "AGENT_NOT_FOUND",
        "AGENT_OFFLINE",
        "RATE_LIMIT_EXCEEDED",
        "TIMEOUT",
        "INTERNAL_ERROR",
        "SERVICE_UNAVAILABLE"
    ]
}
```

### 12.3 超时处理

| 超时类型 | 默认值 | 说明 |
|---------|--------|------|
| **连接超时** | 10s | 建立 TCP/TLS 连接超时 |
| **读取超时** | 60s | 等待响应数据超时 |
| **会话超时** | 300s | 整个会话最长时长 |
| **空闲超时** | 60s | 会话无活动超时 |

### 12.4 故障恢复

```
┌─────────────────────────────────────────────────────────────────┐
│                     故障恢复流程                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 检测故障                                                    │
│     · 心跳检测 / 超时检测 / 错误码识别                          │
│                                                                 │
│  2. 故障分类                                                    │
│     · 瞬时故障（网络抖动）→ 直接重试                            │
│     · 持久故障（Agent 下线）→ 切换备用 Agent                    │
│     · 协议故障（版本不兼容）→ 降级处理                          │
│                                                                 │
│  3. 恢复操作                                                    │
│     · 瞬时故障：指数退避重试                                     │
│     · 持久故障：查询 AP 获取备用 Agent                          │
│     · 协议故障：协商兼容版本或降级                              │
│                                                                 │
│  4. 状态同步                                                    │
│     · 恢复后会话状态同步                                         │
│     · 未完成消息的重新投递                                       │
│                                                                 │
│  5. 审计记录                                                    │
│     · 故障详情记录到审计日志                                     │
│     · 触发告警（如需）                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 十三、示例代码与集成实践

### 13.1 Python SDK 基础示例

```python
"""
ACP Python SDK 基础示例
演示 Agent 注册、发现、通信的完整流程
"""
from acp import ACPClient, AID, AgentProfile

# ============================================
# 1. 申请 AID 并接入网络
# ============================================
# 生成密钥对并申请 AID
client = ACPClient(ap_endpoint="https://ap1.agentunion.cn")

# 申请 AID（首次）
aid = client.register_aid(
    agent_name="my-research-agent",
    organization="Example Corp",
    enable_dkr=True  # 启用双钥恢复
)
print(f"AID 申请成功: {aid}")

# ============================================
# 2. 配置 AgentProfile
# ============================================
profile = AgentProfile(
    aid="my-research-agent.ap1.agentunion.cn",
    name="研究助手",
    description="专业的市场研究与分析 Agent",
    version="1.0.0",
    capabilities=["market-research", "data-analysis"],
    inputs={
        "query": {"type": "string", "required": True},
        "depth": {"type": "string", "enum": ["quick", "comprehensive"]}
    },
    outputs={
        "report": {"type": "object"}
    },
    pricing={"model": "per-call", "price": 0.5, "currency": "USD"}
)
client.publish_profile(profile)

# ============================================
# 3. 监听 incoming 消息
# ============================================
@client.on_message("request")
def handle_request(message):
    """处理来自其他 Agent 的请求"""
    print(f"收到请求: {message.header.message_id}")
    print(f"来自: {message.header.from_}")
    print(f"内容: {message.body.content}")
    
    # 执行业务逻辑
    result = perform_research(message.body.content)
    
    # 返回响应
    return client.create_response(
        reply_to=message.header.message_id,
        session_id=message.header.session_id,
        status="success",
        result=result
    )

@client.on_message("error")
def handle_error(message):
    """处理错误消息"""
    print(f"错误: {message.body.content.error_code}")
    print(f"详情: {message.body.content.error_message}")

# ============================================
# 4. 调用其他 Agent
# ============================================
# 发现 Agent
agents = client.discover_agents(capability="writing")
print(f"发现 {len(agents)} 个写作 Agent")

# 发起调用
response = client.send_request(
    to="writing-bot.ap2.agentunion.cn",
    content={
        "action": "write",
        "topic": "AI Agent 市场趋势",
        "format": "article"
    },
    timeout=300
)

if response.header.message_type == "response":
    print(f"收到响应: {response.body.content}")
else:
    print(f"调用失败: {response.body.content.error_message}")

# ============================================
# 5. 启动 Agent
# ============================================
client.serve()  # 阻塞运行，监听消息
```

### 13.2 TypeScript SDK 示例

```typescript
/**
 * ACP TypeScript SDK 基础示例
 */
import { ACPClient, AgentProfile, Message } from 'acp-ts';

// 1. 初始化客户端并申请 AID
const client = new ACPClient({
  apEndpoint: 'https://ap1.agentunion.cn'
});

const aid = await client.registerAID({
  agentName: 'my-research-agent',
  organization: 'Example Corp',
  enableDKR: true
});
console.log(`AID 申请成功: ${aid}`);

// 2. 配置 AgentProfile
const profile: AgentProfile = {
  aid: 'my-research-agent.ap1.agentunion.cn',
  name: '研究助手',
  description: '专业的市场研究与分析 Agent',
  version: '1.0.0',
  capabilities: ['market-research', 'data-analysis'],
  inputs: {
    query: { type: 'string', required: true },
    depth: { type: 'string', enum: ['quick', 'comprehensive'] }
  },
  outputs: {
    report: { type: 'object' }
  },
  pricing: { model: 'per-call', price: 0.5, currency: 'USD' }
};
await client.publishProfile(profile);

// 3. 监听消息
client.onMessage('request', async (message: Message) => {
  console.log(`收到请求: ${message.header.message_id}`);
  console.log(`来自: ${message.header.from}`);
  
  const result = await performResearch(message.body.content);
  
  return client.createResponse({
    replyTo: message.header.message_id,
    sessionId: message.header.session_id,
    status: 'success',
    result
  });
});

// 4. 调用其他 Agent
const response = await client.sendRequest({
  to: 'writing-bot.ap2.agentunion.cn',
  content: {
    action: 'write',
    topic: 'AI Agent 市场趋势',
    format: 'article'
  },
  timeout: 300
});

if (response.header.messageType === 'response') {
  console.log('收到响应:', response.body.content);
} else {
  console.error('调用失败:', response.body.content.errorMessage);
}

// 5. 启动服务
client.serve();
```

### 13.3 完整会话交互流程图

```
┌─────────────────────────────────────────────────────────────────┐
│              ACP 完整会话交互流程                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Agent A (调用方)          AP             Agent B (被调用方)    │
│                                                                 │
│  ┌──────────────┐                        ┌──────────────┐       │
│  │ 1.加载证书   │                        │ 1.加载证书   │       │
│  │ 2.连接AP     │                        │ 2.连接AP     │       │
│  │ 3.双向认证   │                        │ 3.双向认证   │       │
│  └──────┬───────┘                        └──────┬───────┘       │
│         │                                      │               │
│         │  4.发现 Agent B                      │               │
│         ├─────────────────────────────────────►│               │
│         │         (查询 AgentProfile)          │               │
│         │◄─────────────────────────────────────┤               │
│         │                                      │               │
│         │  5.发起会话请求                      │               │
│         ├──────────────► AP ──────────────────►│               │
│         │                                      │               │
│         │              6.B 接受会话            │               │
│         │◄──────────────  AP ◄────────────────┤               │
│         │                                      │               │
│         │  7.建立加密通道                      │               │
│         ├──────────────► AP ──────────────────►│               │
│         │◄──────────────  AP ◄────────────────┤               │
│         │                                      │               │
│         │  8.发送请求消息                      │               │
│         ├──────────────► AP ──────────────────►│               │
│         │                                      │               │
│         │              9.B 处理并返回          │               │
│         │◄──────────────  AP ◄────────────────┤               │
│         │                                      │               │
│         │  10.签署数字契约                     │               │
│         ├──────────────► AP ──────────────────►│               │
│         │◄──────────────  AP ◄────────────────┤               │
│         │                                      │               │
│         │  11.关闭会话                         │               │
│         ├──────────────► AP ──────────────────►│               │
│         │                                      │               │
│  ┌──────┴───────┐                        ┌──────┴───────┐       │
│  │ 会话完成     │                        │ 会话完成     │       │
│  │ 资源释放     │                        │ 资源释放     │       │
│  └──────────────┘                        └──────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 13.4 Docker 部署示例

```dockerfile
# Dockerfile for ACP Agent
FROM python:3.11-slim

WORKDIR /app

# 安装 ACP SDK
RUN pip install acp-sdk

# 复制 Agent 代码
COPY . /app/

# 暴露端口
EXPOSE 8080

# 启动 Agent
CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  my-agent:
    build: .
    ports:
      - "8080:8080"
    environment:
      - AP_ENDPOINT=https://ap1.agentunion.cn
      - AGENT_NAME=my-research-agent
      - LLM_API_KEY=${LLM_API_KEY}
    volumes:
      - ./credentials:/app/credentials
      - ./data:/app/data
    restart: unless-stopped
```

---

## 十四、与主流协议对比

### 14.1 四大协议全景对比

| 维度 | MCP | ACP（AgentUnion） | A2A | ANP |
|------|-----|-------------------|-----|-----|
| **全称** | Model Context Protocol | Agent Communication Protocol | Agent to Agent | Agent Network Protocol |
| **发起方** | Anthropic → Linux Foundation | AgentUnion | Google → Linux Foundation | 社区 |
| **解决问题** | Agent 连接工具/数据 | Agent 间通信协作 | Agent 对 Agent 交互 | Agent 组网和路由 |
| **类比** | Agent 的"USB-C" | Agent 的"语言" | 通用交互范式 | 底层网络层 |
| **传输协议** | JSON-RPC 2.0 | HTTPS + WSS + SSE | JSON-RPC 2.0 | HTTP |
| **身份体系** | 动态凭证 | AID + PKI 证书 | Agent Card | DID |
| **发现机制** | 服务端注册 | AP + 搜索引擎 | Agent Card | DID 注册表 |
| **典型场景** | Agent 调用工具 | 智能体互联网 | 跨组织任务委派 | Agent 组网 |

### 14.2 协议协作关系

```
                    ┌─────────────────────┐
                    │   用户业务需求      │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   编排 Agent        │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
    ┌─────────▼─────────┐ ┌───▼────┐ ┌─────────▼─────────┐
    │ ACP/A2A（横向）   │ │ MCP    │ │ ACP/A2A（横向）   │
    │ Agent ◄─► Agent   │ │（纵向）│ │ Agent ◄─► Agent   │
    └─────────┬─────────┘ │ Agent  │ └─────────┬─────────┘
              │            │◄─►工具 │            │
              │            └────────┘            │
    ┌─────────▼─────────┐               ┌────────▼──────────┐
    │   专业 Agent A    │               │  专业 Agent B     │
    └───────────────────┘               └───────────────────┘
```

- **MCP（纵向）**：Agent 连接工具、数据源
- **ACP/A2A（横向）**：Agent 之间互相通信协作
- 两者互补，通常一起使用

---

## 十五、总结与最佳实践

### 15.1 核心要点

| 要点 | 说明 |
|------|------|
| **ACP 是什么** | 智能体通信协议，解决 Agent 间协作问题 |
| **两大流派** | AgentUnion ACP（智能体互联网）与 IBM/BeeAI ACP（REST 互操作，已并入 A2A） |
| **核心概念** | AID（身份）、AP（接入点）、Agent Internet（网络）、User（用户） |
| **安全机制** | PKI 证书 + 双向认证 + DKR 双钥恢复 + 数字契约 |
| **与 MCP 关系** | 互补而非竞争，MCP 纵向连工具，ACP 横向连 Agent |

### 15.2 选型决策树

```
┌─────────────────────────────────────────────────────────────────┐
│                    ACP 协议选型决策树                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  需要让 Agent 间通信协作吗？                                    │
│  ├── 否 → 考虑 MCP（Agent 连工具）                             │
│  └── 是 ↓                                                       │
│                                                                 │
│  是否需要构建开放互联网协作？                                    │
│  ├── 是 → AgentUnion ACP                                        │
│  │       (完整身份体系、授权交易、搜索引擎)                     │
│  │                                                              │
│  └── 否 ↓                                                       │
│                                                                 │
│  是否为内网/气隙环境？                                          │
│  ├── 是 → IBM/BeeAI ACP（或已融合的 A2A）                      │
│  │       (支持离线发现、REST 轻量)                              │
│  │                                                              │
│  └── 否 → 两者皆可，根据团队技术栈选择                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 15.3 集成最佳实践

1. **身份先行**：优先申请 AID 并妥善保管私钥，启用 DKR 备份
2. **规范 Profile**：完整填写 AgentProfile，确保可被搜索引擎发现
3. **错误处理**：实现完整错误码处理与指数退避重试
4. **安全通信**：强制双向认证，敏感操作必须签署数字契约
5. **版本协商**：通信前协商协议版本，做好向后兼容
6. **监控审计**：记录完整会话日志，支持事后追溯
7. **渐进集成**：先小规模试点，验证后扩大协作范围

### 15.4 常见陷阱

| 陷阱 | 解决方案 |
|------|----------|
| 私钥丢失导致服务不可用 | 启用 DKR 双钥恢复机制 |
| Agent 无法被发现 | 检查 AgentProfile 完整性与搜索引擎配置 |
| 协议版本不兼容 | 实现版本协商与降级处理 |
| 证书过期导致服务中断 | 配置自动续期（剩余 <7 天触发） |
| 消息格式错误 | 使用 SDK 提供的序列化工具，避免手动拼装 |
| 跨框架协作失败 | 严格遵循 ACP 数据规范，避免框架私有字段 |

---

## 参考资料

- [ACP 官方文档（AgentUnion）](https://acp.agentunion.cn/introduction/)
- [AID 智能体身份标识](https://acp.agentunion.cn/introduction/aid.html)
- [ACP 证书管理体系](https://acp.agentunion.cn/introduction/certificate.html)
- [Agent 会话时序](https://acp.agentunion.cn/introduction/session.html)
- [ACP 消息格式](https://acp.agentunion.cn/introduction/protocol/message.html)
- [Agent 行为及安全规范](https://acp.agentunion.cn/introduction/security.html)
- [ACP 与 A2A 技术对照（51CTO）](https://www.51cto.com/article/852070.html)
- [AI Agent 通信协议全景解读](https://blog.csdn.net/zlt501962603/article/details/160594467)
- [ACP 智能体通信协议：从原理到实战](https://blog.csdn.net/m0_59235945/article/details/160049052)
- [A2A Protocol（Google）](https://google.github.io/A2A/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
