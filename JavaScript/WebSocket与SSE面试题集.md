# WebSocket 与 Server-Sent Events (SSE) 面试题集

> 本文档系统梳理 WebSocket 与 Server-Sent Events 两种实时通信技术的核心知识点与常见面试题，涵盖基础概念、原理机制、对比分析、实战应用和常见问题解决方案，适合前端开发岗位面试复习使用。

---

## 目录

- [一、WebSocket 技术基础](#一websocket-技术基础)
- [二、Server-Sent Events (SSE) 技术基础](#二server-sent-events-sse-技术基础)
- [三、WebSocket 与 SSE 对比分析](#三websocket-与-sse-对比分析)
- [四、面试题及详解](#四面试题及详解)
  - [题目 1：WebSocket 的基本概念与握手过程](#题目-1websocket-的基本概念与握手过程)
  - [题目 2：WebSocket 客户端 API 使用](#题目-2websocket-客户端-api-使用)
  - [题目 3：WebSocket 的心跳检测与断线重连](#题目-3websocket-的心跳检测与断线重连)
  - [题目 4：WebSocket 的数据帧格式与二进制传输](#题目-4websocket-的数据帧格式与二进制传输)
  - [题目 5：SSE 的基本概念与使用](#题目-5sse-的基本概念与使用)
  - [题目 6：SSE 的事件类型与自定义事件](#题目-6sse-的事件类型与自定义事件)
  - [题目 7：SSE 的断线重连与 Last-Event-ID](#题目-7sse-的断线重连与-last-event-id)
  - [题目 8：WebSocket 与 SSE 全面对比](#题目-8websocket-与-sse-全面对比)
  - [题目 9：WebSocket 与 HTTP 长轮询对比](#题目-9websocket-与-http-长轮询对比)
  - [题目 10：实时通信技术的适用场景选择](#题目-10实时通信技术的适用场景选择)
  - [题目 11：WebSocket 服务端实现（Node.js）](#题目-11websocket-服务端实现nodejs)
  - [题目 12：SSE 服务端实现（Node.js）](#题目-12sse-服务端实现nodejs)
  - [题目 13：WebSocket 跨域与安全](#题目-13websocket-跨域与安全)
  - [题目 14：WebSocket 的负载均衡与集群方案](#题目-14websocket-的负载均衡与集群方案)
  - [题目 15：SSE 的局限性及突破方案](#题目-15sse-的局限性及突破方案)
- [附录：考点速查表](#附录考点速查表)

---

## 一、WebSocket 技术基础

### 1.1 什么是 WebSocket

WebSocket 是 HTML5 规范定义的一种**全双工通信协议**，它使得客户端和服务器之间可以建立持久连接，双方可以随时互相发送数据。

**核心特性：**

| 特性 | 说明 |
|------|------|
| **全双工通信** | 客户端和服务器可以同时发送数据，互不阻塞 |
| **持久连接** | 一次握手后保持连接，无需反复创建/销毁 |
| **低延迟** | 消息帧头部仅 2-14 字节，开销极小 |
| **二进制支持** | 支持文本和二进制数据的传输 |
| **协议升级** | 基于 HTTP 协议升级而来（HTTP → WebSocket） |
| **跨域支持** | 原生支持跨域，无同源策略限制 |

### 1.2 WebSocket 握手过程

```
客户端                                    服务器
  |                                         |
  |---- HTTP GET (Upgrade 请求) ----------->|
  |     Connection: Upgrade                 |
  |     Upgrade: websocket                  |
  |     Sec-WebSocket-Key: dGhlIH...       |
  |     Sec-WebSocket-Version: 13           |
  |                                         |
  |<---- HTTP 101 Switching Protocols ------|
  |     Connection: Upgrade                 |
  |     Upgrade: websocket                  |
  |     Sec-WebSocket-Accept: s3pPL...     |
  |                                         |
  |<====== WebSocket 全双工通信 ===========>|
```

**握手细节：**

```javascript
// 客户端请求头
GET /chat HTTP/1.1
Host: server.example.com
Connection: Upgrade                    // 要求升级协议
Upgrade: websocket                     // 升级到 WebSocket
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==  // 随机生成的 Base64 密钥
Sec-WebSocket-Version: 13              // WebSocket 协议版本

// 服务端响应头
HTTP/1.1 101 Switching Protocols
Connection: Upgrade
Upgrade: websocket
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=  // 对 Key 的 SHA-1 哈希
```

**Sec-WebSocket-Accept 计算方式：**

```javascript
// 服务端计算 Accept 值
const crypto = require('crypto');

const MAGIC_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11';
const key = 'dGhlIHNhbXBsZSBub25jZQ==';

const accept = crypto
  .createHash('sha1')
  .update(key + MAGIC_STRING)
  .digest('base64');

console.log(accept); // s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

### 1.3 WebSocket 状态（readyState）

| 常量 | 值 | 状态 | 说明 |
|------|---|------|------|
| `WebSocket.CONNECTING` | 0 | 连接中 | 正在建立连接 |
| `WebSocket.OPEN` | 1 | 已连接 | 可以通信 |
| `WebSocket.CLOSING` | 2 | 关闭中 | 正在关闭连接 |
| `WebSocket.CLOSED` | 3 | 已关闭 | 连接已关闭 |

---

## 二、Server-Sent Events (SSE) 技术基础

### 2.1 什么是 SSE

Server-Sent Events（SSE）是一种允许服务器向客户端**单向推送数据**的技术。客户端通过普通的 HTTP 请求建立连接后，服务器可以持续向客户端发送事件流。

**核心特性：**

| 特性 | 说明 |
|------|------|
| **单向通信** | 服务器 → 客户端，客户端无法通过 SSE 发送数据 |
| **基于 HTTP** | 使用标准 HTTP 协议，无需特殊协议升级 |
| **自动重连** | 连接断开后浏览器自动重连 |
| **事件 ID** | 支持 `Last-Event-ID` 机制，断线重连后可从断点继续 |
| **文本格式** | 数据以 `text/event-stream` MIME 类型传输 |
| **原生支持** | 浏览器原生 `EventSource` API，无需额外库 |

### 2.2 SSE 数据格式

```
// SSE 响应数据格式（text/event-stream）

// 基本格式：data: 开头
data: 这是一条消息

// 多行数据
data: 第一行
data: 第二行

// 自定义事件类型（默认是 message）
event: userLogin
data: {"username": "Alice", "time": "2024-01-01"}

// 带 ID 的事件（用于断线重连）
id: 42
data: 带 ID 的消息

// 注释行（以冒号开头，客户端忽略）
: 这是注释

// 事件结束标志：空行
// 每个事件块以两个换行符结束
```

**SSE 数据流示例：**

```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

: ok

event: message
data: {"content": "Hello"}

id: 1
event: update
data: {"status": "processing"}

id: 2
data: {"status": "completed"}
```

### 2.3 EventSource 状态（readyState）

| 常量 | 值 | 状态 | 说明 |
|------|---|------|------|
| `EventSource.CONNECTING` | 0 | 连接中 | 正在建立连接或重连 |
| `EventSource.OPEN` | 1 | 已连接 | 连接正常 |
| `EventSource.CLOSED` | 2 | 已关闭 | 连接已关闭 |

---

## 三、WebSocket 与 SSE 对比分析

### 3.1 核心差异对比

| 对比维度 | WebSocket | SSE |
|---------|-----------|-----|
| **通信方向** | 全双工（双向） | 单向（服务器 → 客户端） |
| **协议** | WebSocket（ws:// / wss://） | HTTP（http:// / https://） |
| **连接建立** | HTTP 升级（101 Switching） | 标准 HTTP 请求 |
| **数据格式** | 文本 + 二进制 | 仅文本（UTF-8） |
| **浏览器 API** | `WebSocket` 构造函数 | `EventSource` 构造函数 |
| **自动重连** | 需手动实现 | 浏览器自动重连 |
| **断点续传** | 需手动实现 | 原生支持 `Last-Event-ID` |
| **消息帧开销** | 2-14 字节 | 文本行开销（较大） |
| **最大并发连接** | 取决于服务器 | 浏览器限制同域 6 个连接（HTTP/1.1） |
| **HTTP/2 优化** | 不受益 | 多路复用，打破 6 连接限制 |
| **防火墙友好** | 可能被拦截 | 与普通 HTTP 流量无异 |
| **Cookie 携带** | 握手时自动携带 | 同源自动携带 Cookie |
| **自定义头部** | 不支持（握手后无法修改） | 不支持（EventSource 无配置） |
| **Node.js 支持** | 需 ws 库或 Socket.IO | 原生 HTTP 模块即可 |
| **IE 兼容** | IE 10+ | **不支持 IE**（Edge 79+） |
| **移动端** | 良好支持 | 部分支持 |

### 3.2 各自优势

**WebSocket 优势：**
- 全双工通信，适合实时互动场景
- 二进制数据传输，可传输文件、音视频等
- 协议开销极小，高频通信性能优越
- 跨域无限制

**SSE 优势：**
- 基于 HTTP，实现简单，无需特殊协议
- 自动重连，无需手动编写重连逻辑
- 支持 `Last-Event-ID` 断点续传
- 浏览器原生 `EventSource` API，使用简单
- HTTP/2 下多路复用，突破单域连接数限制
- 防火墙友好，不会被企业网络拦截

---

## 四、面试题及详解

### 题目 1：WebSocket 的基本概念与握手过程

**题目描述：** 请说明 WebSocket 协议的核心概念、握手过程，以及为什么需要基于 HTTP 进行协议升级。

**考察知识点：** WebSocket 协议原理 | **能力等级：** 初级

**参考答案：**

**WebSocket 协议核心概念：**

WebSocket 是一种在单个 TCP 连接上进行**全双工通信**的网络协议。与 HTTP 的"请求-响应"模式不同，WebSocket 建立连接后，双方可以随时互相发送数据，无需等待对方请求。

**为什么需要基于 HTTP 升级：**

1. **兼容现有网络基础设施**：WebSocket 握手使用 HTTP 的 Upgrade 机制，可以穿透现有的代理服务器和防火墙，无需额外配置
2. **复用 80/443 端口**：wss:// 使用 443 端口，与 HTTPS 共享，不需要开放新端口
3. **安全上下文继承**：可以复用 HTTP 的 Cookie、认证等安全机制

**握手过程详解：**

```javascript
// 客户端发起握手请求
const socket = new WebSocket('wss://example.com/chat');

// 浏览器自动发送的 HTTP 请求：
// GET /chat HTTP/1.1
// Host: example.com
// Connection: Upgrade
// Upgrade: websocket
// Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
// Sec-WebSocket-Version: 13

// 服务端验证并响应：
// HTTP/1.1 101 Switching Protocols
// Connection: Upgrade
// Upgrade: websocket
// Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

**Sec-WebSocket-Key / Sec-WebSocket-Accept 的作用：**

- `Sec-WebSocket-Key` 是客户端随机生成的 16 字节 Base64 编码值
- 服务端将其与固定魔数 `258EAFA5-E914-47DA-95CA-C5AB0DC85B11` 拼接，计算 SHA-1 哈希后 Base64 编码作为 `Sec-WebSocket-Accept`
- 目的：**确认服务端理解 WebSocket 协议**，防止客户端误连非 WebSocket 服务

```javascript
// Node.js 服务端验证示例
const crypto = require('crypto');
const http = require('http');

const server = http.createServer((req, res) => {
  if (req.headers['upgrade']?.toLowerCase() === 'websocket') {
    const key = req.headers['sec-websocket-key'];
    const acceptKey = crypto
      .createHash('sha1')
      .update(key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11')
      .digest('base64');
    
    res.writeHead(101, {
      'Upgrade': 'websocket',
      'Connection': 'Upgrade',
      'Sec-WebSocket-Accept': acceptKey
    });
    // 此后 TCP 连接升级为 WebSocket 协议
  }
});
```

**评分标准：**
- 解释 WebSocket 全双工通信的核心概念（3 分）
- 说明为什么需要基于 HTTP 升级（3 分）
- 正确描述握手流程和 Sec-Key/Accept 的作用（4 分）

---

### 题目 2：WebSocket 客户端 API 使用

**题目描述：** 请写出 WebSocket 客户端 API 的完整使用示例，包括连接建立、消息收发、错误处理、连接关闭，并说明各个事件和方法的用途。

**考察知识点：** WebSocket API | **能力等级：** 初级

**参考答案：**

```javascript
/**
 * WebSocket 客户端完整封装
 */
class WebSocketClient {
  constructor(url, options = {}) {
    this.url = url;
    this.options = {
      reconnectInterval: 3000,    // 重连间隔
      maxReconnectAttempts: 5,    // 最大重连次数
      heartbeatInterval: 30000,   // 心跳间隔
      heartbeatTimeout: 10000,    // 心跳超时
      ...options
    };
    
    this.socket = null;
    this.reconnectAttempts = 0;
    this.heartbeatTimer = null;
    this.heartbeatTimeoutTimer = null;
    this.listeners = {};
    this.isManualClose = false;
  }
  
  /**
   * 建立连接
   */
  connect() {
    this.isManualClose = false;
    
    console.log(`正在连接: ${this.url}`);
    this.socket = new WebSocket(this.url);
    
    // ---- 事件监听 ----
    
    // 1. onopen：连接建立成功
    this.socket.onopen = (event) => {
      console.log('WebSocket 连接已建立');
      this.reconnectAttempts = 0; // 重置重连计数
      this.startHeartbeat();      // 启动心跳
      this.emit('open', event);
    };
    
    // 2. onmessage：接收到消息
    this.socket.onmessage = (event) => {
      // event.data 是服务器发送的数据
      let data = event.data;
      
      // 尝试解析 JSON
      try {
        data = JSON.parse(data);
      } catch (e) {
        // 保持原始字符串
      }
      
      // 处理心跳响应
      if (data === 'pong' || data?.type === 'pong') {
        this.handleHeartbeatResponse();
        return;
      }
      
      this.emit('message', data);
    };
    
    // 3. onerror：发生错误
    this.socket.onerror = (event) => {
      console.error('WebSocket 错误:', event);
      this.emit('error', event);
      // 注意：onerror 后通常会触发 onclose
    };
    
    // 4. onclose：连接关闭
    this.socket.onclose = (event) => {
      console.log(`WebSocket 连接关闭: code=${event.code}, reason=${event.reason}`);
      this.stopHeartbeat();
      this.emit('close', event);
      
      // 非手动关闭，尝试重连
      if (!this.isManualClose) {
        this.tryReconnect();
      }
    };
  }
  
  /**
   * 发送消息
   * @param {*} data - 发送的数据（对象会自动 JSON 序列化）
   */
  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      const payload = typeof data === 'object' ? JSON.stringify(data) : data;
      this.socket.send(payload);
    } else {
      console.warn('WebSocket 未连接，无法发送消息');
    }
  }
  
  /**
   * 手动关闭连接
   */
  close(code = 1000, reason = '') {
    this.isManualClose = true;
    this.stopHeartbeat();
    if (this.socket) {
      this.socket.close(code, reason);
    }
  }
  
  // ---- 心跳机制 ----
  startHeartbeat() {
    this.stopHeartbeat();
    
    this.heartbeatTimer = setInterval(() => {
      if (this.socket?.readyState === WebSocket.OPEN) {
        this.send('ping');
        
        // 设置心跳超时检测
        this.heartbeatTimeoutTimer = setTimeout(() => {
          console.warn('心跳超时，关闭连接');
          this.socket?.close();
        }, this.options.heartbeatTimeout);
      }
    }, this.options.heartbeatInterval);
  }
  
  stopHeartbeat() {
    clearInterval(this.heartbeatTimer);
    clearTimeout(this.heartbeatTimeoutTimer);
  }
  
  handleHeartbeatResponse() {
    clearTimeout(this.heartbeatTimeoutTimer);
  }
  
  // ---- 重连机制 ----
  tryReconnect() {
    if (this.reconnectAttempts >= this.options.maxReconnectAttempts) {
      console.error('已达最大重连次数，停止重连');
      this.emit('reconnectFailed');
      return;
    }
    
    this.reconnectAttempts++;
    const delay = this.options.reconnectInterval * Math.min(this.reconnectAttempts, 5);
    
    console.log(`将在 ${delay}ms 后进行第 ${this.reconnectAttempts} 次重连`);
    
    setTimeout(() => {
      console.log(`正在重连 (${this.reconnectAttempts}/${this.options.maxReconnectAttempts})`);
      this.connect();
    }, delay);
  }
  
  // ---- 事件系统 ----
  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }
  
  off(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
  }
  
  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(cb => cb(data));
    }
  }
}

// ---- 使用示例 ----
const ws = new WebSocketClient('wss://example.com/chat', {
  reconnectInterval: 3000,
  maxReconnectAttempts: 5
});

// 监听事件
ws.on('open', () => {
  console.log('连接成功，发送登录消息');
  ws.send({ type: 'login', token: 'xxx' });
});

ws.on('message', (data) => {
  console.log('收到消息:', data);
  appendMessageToChat(data);
});

ws.on('error', (event) => {
  console.error('连接错误');
});

ws.on('close', (event) => {
  console.log('连接已关闭, code:', event.code);
});

ws.on('reconnectFailed', () => {
  alert('无法连接到服务器，请刷新页面重试');
});

// 建立连接
ws.connect();

// 发送消息
document.getElementById('sendBtn').onclick = () => {
  ws.send({ type: 'message', content: 'Hello!' });
};

// 关闭连接
document.getElementById('disconnectBtn').onclick = () => {
  ws.close(1000, '用户主动断开');
};
```

**WebSocket API 核心事件和方法总结：**

| 事件/方法 | 类型 | 触发时机 |
|----------|------|---------|
| `onopen` | 事件 | 连接建立成功 |
| `onmessage` | 事件 | 收到服务器消息 |
| `onerror` | 事件 | 发生错误（通常后跟 onclose） |
| `onclose` | 事件 | 连接关闭（含关闭码和原因） |
| `send(data)` | 方法 | 发送数据 |
| `close(code, reason)` | 方法 | 关闭连接 |

**关闭码（常用）：**

| 关闭码 | 含义 |
|-------|------|
| 1000 | 正常关闭 |
| 1001 | 端点离开（如页面关闭） |
| 1006 | 异常关闭（连接丢失） |
| 1008 | 协议错误 |
| 1009 | 数据过大 |
| 1011 | 服务器错误 |

**评分标准：**
- 正确使用 WebSocket 构造函数和四个事件（4 分）
- 实现心跳检测和断线重连机制（4 分）
- 处理 JSON 消息解析和事件封装（2 分）

---

### 题目 3：WebSocket 的心跳检测与断线重连

**题目描述：** 请详细阐述 WebSocket 心跳检测的底层机制（TCP Keep-Alive、协议级 Ping/Pong、应用层心跳的区别与联系），并设计一个包含**状态机管理、指数退避、网络状态监听、状态恢复（鉴权+订阅+离线消息补发）**的健壮重连方案。最后说明 TCP 长连接"假死"的原因及解决手段。

**考察知识点：** 心跳分层机制、重连状态机、指数退避 | **能力等级：** 高级

---

#### 一、心跳检测机制深度解析

##### 1. 为什么长连接会“假死”？

TCP 连接虽然可靠，但“可靠”仅限于内核层面的数据包收发。当链路中间节点（NAT、防火墙、负载均衡器）因**空闲超时**主动断开连接时，两端的内核可能并不知道，导致上层应用认为连接仍然存活，但数据实际无法送达。

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   客户端    │    │  中间设备    │    │   服务端    │
│  (Client)   │    │ (NAT/防火墙) │    │  (Server)   │
└──────┬──────┘    └──────┬───────┘    └──────┬──────┘
       │  空闲 30s         │                │
       │─────────────────►│                │
       │                  │                │
       │  空闲 31s...     │                │
       │                  │  空闲超时断开   │
       │                  │  (Connection   │
       │                  │   Timeout)     │
       │                  │◄───────────────│
       │                  │   (连接已失效)  │
       │                  │                │
       │  继续发送数据     │                │
       │─────────────────►│ 丢弃/拒绝      │
       │                  │               ✗│ 收不到数据
       │  (数据丢失，无反馈)│                │
       ▼                  ▼                ▼
  【应用层认为连接正常】  【连接已断开】  【服务端收不到数据】
```

**“假死”场景：**
- **移动网络切换**：WiFi ↔ 4G/5G 切换时 IP 地址变化，原 TCP 连接失效
- **NAT/防火墙超时**：企业网络、运营商网络的 NAT 设备通常有 30s~5min 的空闲超时
- **服务器重启/升级**：服务端进程重启，主动关闭连接但客户端未收到 FIN 包
- **操作系统休眠**：电脑睡眠唤醒后网络状态变化
- **代理/CDN 超时**：某些 CDN/反向代理对 WebSocket 连接有最长保持时间

##### 2. 心跳检测的三个层级

| 层级 | 技术方案 | 说明 | 优缺点 |
| --- | --- | --- | --- |
| **① TCP 层** | `SO_KEEPALIVE` 套接字选项 | 操作系统内核定时发送 TCP Keep-Alive 探测包 | ✅ 无需应用代码<br>❌ 间隔太长（默认 2 小时），且无法穿透所有中间节点 |
| **② WebSocket 协议层** | 协议级 Ping/Pong 帧（opcode 0x9/0xA） | 由浏览器/WS 库底层处理，可配置间隔 | ✅ 自动处理<br>❌ 浏览器原生 WebSocket 不暴露 Ping 接口（仅服务端可发） |
| **③ 应用层** | 自定义 `ping`/`pong` JSON 消息 | 应用层发送心跳业务消息 | ✅ 完全可控，兼容性最好<br>❌ 需手动实现 |

##### 3. 应用层心跳实现（推荐方案）

```typescript
interface HeartbeatOptions {
  interval: number;       // 心跳间隔（毫秒），默认 15s
  timeout: number;        // 心跳超时（毫秒），默认 5s
  maxMissed: number;     // 最大丢失次数，超过则判定连接死亡
}

class HeartbeatManager {
  private pingTimer: number | null = null;
  private missCount: number = 0;
  private options: HeartbeatOptions;
  private ws: WebSocket;
  
  constructor(ws: WebSocket, options: Partial<HeartbeatOptions> = {}) {
    this.ws = ws;
    this.options = {
      interval: 15000,
      timeout: 5000,
      maxMissed: 3,
      ...options
    };
  }
  
  /** 启动心跳 */
  start(): void {
    this.stop();
    this.missCount = 0;
    
    this.pingTimer = window.setInterval(() => {
      // 1. 检查连接状态
      if (this.ws.readyState !== WebSocket.OPEN) {
        this.stop();
        return;
      }
      
      // 2. 发送 ping
      this.ws.send(JSON.stringify({
        type: 'ping',
        timestamp: Date.now()
      }));
      
      // 3. 未收到 pong，累加丢失次数
      this.missCount++;
      console.log(`[Heartbeat] Ping 已发送，丢失次数: ${this.missCount}/${this.options.maxMissed}`);
      
      // 4. 超过最大次数，判定连接死亡
      if (this.missCount >= this.options.maxMissed) {
        console.error('[Heartbeat] 连接已死亡，主动断开');
        this.ws.close(10003, '心跳超时');
        this.stop();
      }
    }, this.options.interval);
  }
  
  /** 停止心跳 */
  stop(): void {
    if (this.pingTimer !== null) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
    this.missCount = 0;
  }
  
  /** 收到 pong 时调用，重置计数 */
  onPong(): void {
    this.missCount = 0;
    console.log('[Heartbeat] Pong 收到，连接正常');
  }
}

// 服务端（Node.js）实现对应的 pong 响应
// wss.on('message', (ws, data) => {
//   const msg = JSON.parse(data);
//   if (msg.type === 'ping') {
//     ws.send(JSON.stringify({ type: 'pong', timestamp: msg.timestamp }));
//   }
// });
```

---

#### 二、断线重连机制深度解析

##### 1. 重连状态机设计

一个健壮的重连系统应该包含清晰的状态机管理：

```
                    ┌──────────────┐
                    │  DISCONNECTED │ ← 初始状态 / 主动关闭
                    └──────┬───────┘
                           │ connect()
                           ▼
                    ┌──────────────┐
              ┌────►│  CONNECTING  │ ← 正在建立连接
              │     └──────┬───────┘
              │            │ onopen
              │            ▼
              │     ┌──────────────┐
              │     │   CONNECTED  │ ← 连接正常
              │     └──────┬───────┘
              │            │ onclose/onerror (非主动)
              │            ▼
              │     ┌──────────────┐
              │     │   RECONNECTING│ ← 尝试重连
              │     └──────┬───────┘
              │            │ 
              │            ├──► 重试次数达上限 ──► RECONNECT_FAILED (终态)
              │            │
              │            └──► 连接成功 ──► CONNECTED
              │
              └── 用户手动 close() ──► DISCONNECTED (终态，不再重连)
```

##### 2. 指数退避算法

指数退避（Exponential Backoff）是重连的核心策略，避免频繁重连冲击服务器：

```typescript
interface ReconnectOptions {
  baseDelay: number;       // 基础延迟 (ms)，默认 1000
  maxDelay: number;        // 最大延迟 (ms)，默认 30000
  maxAttempts: number;     // 最大重连次数，0 表示无限
  multiplier: number;      // 指数倍数，默认 2
  jitter: boolean;         // 是否添加随机抖动
}

class ReconnectManager {
  private attempts: number = 0;
  private timer: number | null = null;
  private options: ReconnectOptions;
  
  constructor(options: Partial<ReconnectOptions> = {}) {
    this.options = {
      baseDelay: 1000,
      maxDelay: 30000,
      maxAttempts: 0, // 0 = 无限重连
      multiplier: 2,
      jitter: true,
      ...options
    };
  }
  
  /** 计算下一次重连延迟 */
  getNextDelay(): number {
    const { baseDelay, maxDelay, multiplier, jitter } = this.options;
    
    // 1. 指数退避：baseDelay * multiplier^attempts
    let delay = baseDelay * Math.pow(multiplier, this.attempts);
    
    // 2. 限制上限
    delay = Math.min(delay, maxDelay);
    
    // 3. 添加随机抖动（0~20%），防止"惊群效应"
    if (jitter) {
      const jitterAmount = delay * 0.2;
      delay += Math.random() * jitterAmount;
    }
    
    return Math.floor(delay);
  }
  
  /** 尝试重连 */
  schedule(connectCallback: () => void): boolean {
    // 检查是否超过最大次数
    if (this.options.maxAttempts > 0 && this.attempts >= this.options.maxAttempts) {
      console.error(`[Reconnect] 已达最大重连次数 ${this.options.maxAttempts}`);
      return false;
    }
    
    this.attempts++;
    const delay = this.getNextDelay();
    
    console.log(`[Reconnect] 第 ${this.attempts} 次重连，等待 ${delay}ms`);
    
    this.timer = window.setTimeout(() => {
      connectCallback();
    }, delay);
    
    return true;
  }
  
  /** 重置重连状态（连接成功后调用） */
  reset(): void {
    this.attempts = 0;
    if (this.timer !== null) {
      clearTimeout(this.timer);
      this.timer = null;
    }
  }
  
  /** 取消重连（用户主动关闭时调用） */
  cancel(): void {
    this.attempts = 0;
    if (this.timer !== null) {
      clearTimeout(this.timer);
      this.timer = null;
    }
  }
}
```

**指数退避延迟计算示例：**

```
第1次重试: 1000ms (1s)
第2次重试: 2000ms (2s)
第3次重试: 4000ms (4s)
第4次重试: 8000ms (8s)
第5次重试: 16000ms (16s)
第6次重试: 30000ms (30s, 达到上限)
第7次及以后: 30000ms + 随机抖动 (30s~36s)
```

**为什么需要抖动（Jitter）？**
当大量客户端同时断线（如服务端重启），如果同时重连会造成**"惊群效应"**（Thundering Herd）。抖动可将重连时间分散开，降低服务端压力。

##### 3. 网络状态监听

利用浏览器 `Network Information API` 和 `online/offline` 事件优化重连策略：

```typescript
class NetworkMonitor {
  private listeners: Set<(online: boolean, type?: string) => void> = new Set();
  private currentOnline: boolean = navigator.onLine;
  
  constructor() {
    // 监听在线/离线事件
    window.addEventListener('online', () => {
      this.currentOnline = true;
      this.notifyListeners(true, this.getConnectionType());
    });
    
    window.addEventListener('offline', () => {
      this.currentOnline = false;
      this.notifyListeners(false);
    });
    
    // 监听网络状态变化（可选）
    const connection = (navigator as any).connection;
    if (connection) {
      connection.addEventListener('change', () => {
        console.log(`网络切换至: ${this.getConnectionType()}`);
      });
    }
  }
  
  /** 获取当前网络类型 */
  getConnectionType(): string {
    const connection = (navigator as any).connection;
    return connection?.effectiveType || 'unknown';
  }
  
  /** 判断是否在线 */
  isOnline(): boolean {
    return this.currentOnline;
  }
  
  /** 订阅状态变化 */
  subscribe(callback: (online: boolean, type?: string) => void): () => void {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }
  
  private notifyListeners(online: boolean, type?: string): void {
    this.listeners.forEach(cb => cb(online, type));
  }
}

// 结合网络状态的重连策略
const networkMonitor = new NetworkMonitor();

// 离线时暂停重连，恢复网络后立即尝试
networkMonitor.subscribe((online, type) => {
  if (online) {
    console.log(`[Network] 网络恢复(${type})，立即尝试重连`);
    ws.reconnectNow(); // 跳过退避，立即重连
  } else {
    console.log('[Network] 网络断开，暂停重连');
    ws.pauseReconnect();
  }
});
```

##### 4. 连接恢复与状态同步

重连成功后需要恢复关键业务状态：

```typescript
interface ConnectionState {
  token: string;           // 认证 Token
  subscriptions: string[]; // 订阅的频道/主题列表
  userInfo: { id: string; name: string };
}

class ResilientWebSocket {
  private state: ConnectionState;
  private heartbeat: HeartbeatManager;
  private reconnectManager: ReconnectManager;
  private networkMonitor: NetworkMonitor;
  
  /** 重连成功后的状态恢复 */
  private async onConnected(): Promise<void> {
    console.log('[WebSocket] 连接成功，恢复状态...');
    
    try {
      // 1. 发送认证信息
      this.ws.send(JSON.stringify({
        type: 'auth',
        token: this.state.token
      }));
      
      // 2. 等待认证结果
      await this.waitForAuthResult();
      
      // 3. 重新订阅频道
      for (const channel of this.state.subscriptions) {
        this.ws.send(JSON.stringify({
          type: 'subscribe',
          channel
        }));
      }
      
      // 4. 恢复成功，重置重连计数
      this.reconnectManager.reset();
      this.heartbeat.start();
      
      // 5. 发送离线积压消息
      this.flushQueue();
      
      console.log('[WebSocket] 状态恢复完成');
      this.emit('reconnected');
    } catch (err) {
      console.error('[WebSocket] 状态恢复失败:', err);
      // 恢复失败，触发下一轮重连
      this.scheduleReconnect();
    }
  }
  
  /** 发送消息（含离线缓存） */
  send(data: any): void {
    const msg = JSON.stringify(data);
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(msg);
    } else {
      this.messageQueue.push(msg);
      console.log(`[WebSocket] 离线缓存消息，队列长度: ${this.messageQueue.length}`);
    }
  }
}
```

---

#### 三、完整实战：生产级 WebSocket 封装

```typescript
type EventCallback = (...args: any[]) => void;

interface WSOptions {
  url: string;
  protocols?: string | string[];
  heartbeat?: Partial<HeartbeatOptions>;
  reconnect?: Partial<ReconnectOptions>;
  token?: string | (() => Promise<string>);
  onMessage?: (data: any) => void;
  onConnected?: () => void;
  onDisconnected?: (code: number, reason: string) => void;
  onError?: (error: Event) => void;
}

class ProductionWebSocket {
  private ws: WebSocket | null = null;
  private url: string;
  private protocols?: string | string[];
  private token?: string | (() => Promise<string>);
  
  private heartbeat: HeartbeatManager | null = null;
  private reconnectManager: ReconnectManager;
  private networkMonitor: NetworkMonitor;
  
  private isManualClose: boolean = false;
  private messageQueue: string[] = [];
  private eventListeners: Map<string, Set<EventCallback>> = new Map();
  
  private readonly DEFAULT_HEARTBEAT = {
    interval: 15000,
    timeout: 5000,
    maxMissed: 3
  };
  
  constructor(options: WSOptions) {
    this.url = options.url;
    this.protocols = options.protocols;
    this.token = options.token;
    
    // 初始化管理器
    this.reconnectManager = new ReconnectManager(options.reconnect);
    this.networkMonitor = new NetworkMonitor();
    
    // 监听网络状态
    this.networkMonitor.subscribe(online => {
      if (online) {
        console.log('[WS] 网络恢复，尝试重连');
        this.connect();
      }
    });
  }
  
  /** 建立连接 */
  async connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('[WS] 已连接，跳过');
      return;
    }
    
    console.log('[WS] 建立新连接...');
    this.isManualClose = false;
    
    try {
      this.ws = this.protocols
        ? new WebSocket(this.url, this.protocols)
        : new WebSocket(this.url);
      
      // 绑定事件
      this.ws.onopen = async () => {
        console.log('[WS] 连接成功');
        this.reconnectManager.reset();
        
        // 启动心跳
        this.heartbeat = new HeartbeatManager(this.ws!, this.options.heartbeat ?? this.DEFAULT_HEARTBEAT);
        this.heartbeat.start();
        
        // 恢复状态
        await this.authenticate();
        
        // 发送积压消息
        this.flushMessageQueue();
        
        this.emit('connected');
      };
      
      this.ws.onmessage = (event) => {
        this.handleMessage(event.data);
      };
      
      this.ws.onclose = (event) => {
        console.log(`[WS] 连接关闭: code=${event.code}`);
        this.heartbeat?.stop();
        this.emit('disconnected', event.code, event.reason);
        
        // 非主动关闭则重连
        if (!this.isManualClose && this.networkMonitor.isOnline()) {
          this.scheduleReconnect();
        }
      };
      
      this.ws.onerror = (event) => {
        this.emit('error', event);
      };
    } catch (err) {
      console.error('[WS] 连接创建失败:', err);
      this.scheduleReconnect();
    }
  }
  
  /** 发送消息 */
  send(data: any): void {
    const msg = typeof data === 'string' ? data : JSON.stringify(data);
    
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(msg);
    } else {
      this.messageQueue.push(msg);
      console.log(`[WS] 离线缓存: ${this.messageQueue.length} 条消息`);
    }
  }
  
  /** 手动关闭连接 */
  close(code: number = 1000, reason: string = ''): void {
    this.isManualClose = true;
    this.heartbeat?.stop();
    this.reconnectManager.cancel();
    this.ws?.close(code, reason);
    console.log('[WS] 主动关闭连接');
  }
  
  /** 订阅事件 */
  on(event: string, callback: EventCallback): () => void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set());
    }
    this.eventListeners.get(event)!.add(callback);
    return () => this.eventListeners.get(event)?.delete(callback);
  }
  
  // ---- 私有方法 ----
  
  private scheduleReconnect(): void {
    const ok = this.reconnectManager.schedule(() => this.connect());
    if (!ok) {
      this.emit('maxReconnectReached');
      console.error('[WS] 已达最大重连次数');
    }
  }
  
  private handleMessage(raw: string): void {
    let data: any;
    try {
      data = JSON.parse(raw);
    } catch {
      data = raw;
    }
    
    // 处理心跳
    if (data?.type === 'pong') {
      this.heartbeat?.onPong();
      return;
    }
    
    // 处理业务消息
    this.emit('message', data);
  }
  
  private async authenticate(): Promise<void> {
    if (!this.token) return;
    
    const token = typeof this.token === 'function' 
      ? await this.token() 
      : this.token;
    
    this.send({ type: 'auth', token });
  }
  
  private flushMessageQueue(): void {
    while (this.messageQueue.length > 0) {
      const msg = this.messageQueue.shift()!;
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(msg);
      } else {
        this.messageQueue.unshift(msg); // 放回队列
        break;
      }
    }
    console.log(`[WS] 离线消息已清空`);
  }
  
  private emit(event: string, ...args: any[]): void {
    this.eventListeners.get(event)?.forEach(cb => cb(...args));
  }
}

// ---- 使用示例 ----
const ws = new ProductionWebSocket({
  url: 'wss://api.example.com/realtime',
  token: () => localStorage.getItem('auth_token')!, // 动态获取 token
  heartbeat: { interval: 15000, timeout: 5000, maxMissed: 3 },
  reconnect: { baseDelay: 1000, maxDelay: 30000, maxAttempts: 10, jitter: true },
  onMessage: (data) => console.log('收到消息:', data),
  onConnected: () => console.log('连接已恢复'),
  onDisconnected: (code) => console.log(`断开: ${code}`),
});

// 订阅业务事件
const offMessage = ws.on('message', data => {
  if (data.type === 'chat') renderChat(data);
  if (data.type === 'notification') showNotification(data);
});

const offReconnected = ws.on('connected', () => {
  console.log('WebSocket 已重新连接');
  refreshUserData();
});

// 建立连接
ws.connect();

// 发送消息
ws.send({ type: 'chat', content: 'Hello!' });

// 页面卸载时清理
window.addEventListener('beforeunload', () => {
  ws.close();
  offMessage();
  offReconnected();
});
```

---

#### 四、重连策略对比总结

| 策略 | 延迟公式 | 适用场景 | 优点 | 缺点 |
| --- | --- | --- | --- | --- |
| 固定延迟 | 恒定值（如 3s） | 简单Demo | 实现简单 | 服务端压力大 |
| 线性退避 | `delay × attempt` | 轻量应用 | 逐步增加 | 增长过快 |
| **指数退避** | `base × 2^attempts` | **生产环境首选** | 增长合理 | 需实现 |
| 指数+抖动 | `base × 2^attempts + rand(0~20%)` | 多客户端场景 | 防止惊群 | 实现略复杂 |
| 智能重连 | 网络状态+指数退避 | 移动端/H5 | 体验最优 | 实现最复杂 |

---

#### 五、考点与评分标准

| 知识点 | 分值 | 说明 |
| --- | --- | --- |
| 解释 TCP 假死原因 | 2 分 | 中间设备超时、网络切换 |
| 心跳三层架构 | 3 分 | TCP 层/协议层/应用层的区别 |
| 应用层心跳实现 | 3 分 | 含超时检测和丢失计数 |
| 重连状态机 | 3 分 | 状态流转设计清晰 |
| 指数退避算法 | 3 分 | 含抖动防止惊群 |
| 网络状态监听 | 2 分 | online/offline + Network API |
| 状态恢复机制 | 3 分 | 鉴权、订阅恢复、离线消息 |
| 生产级封装 | 1 分 | 代码结构清晰、异常处理完善 |

**满分：20 分** | **及格线：12 分** | **优秀标准：17+ 分**

---

### 题目 3（补充）：心跳检测与重连的常见陷阱

**题目描述：** 在实现 WebSocket 心跳与重连时，有哪些常见的"坑"？请列举至少 5 个并给出解决方案。

**考察知识点：** 实战经验、问题排查 | **能力等级：** 高级

**参考答案：**

##### 陷阱 1：重连风暴

**问题：** 服务端重启后，数千客户端同时重连，导致服务端 CPU 飙升甚至雪崩。

**解决方案：**
- 使用**随机抖动**（Jitter）分散重连时间
- 设置**最小/最大重连间隔**限制
- 服务端可返回 **Retry-After** 头提示客户端延迟重连

```typescript
// 客户端尊重服务端的 Retry-After 提示
private async scheduleReconnectFromServer(): Promise<void> {
  try {
    const res = await fetch('/api/ws-retry-info');
    const { retryAfter } = await res.json();
    const jitter = Math.random() * 0.3 * retryAfter; // 30% 抖动
    setTimeout(() => this.connect(), retryAfter + jitter);
  } catch {
    this.scheduleReconnect(); // 降级到本地策略
  }
}
```

##### 陷阱 2：心跳在页面不可见时仍在发送

**问题：** 用户切换到其他标签页，浏览器会 setInterval 降频或暂停，导致心跳紊乱。

**解决方案：**

```typescript
// 监听页面可见性，调整心跳策略
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden') {
    this.heartbeat?.stop();  // 暂停心跳
    console.log('[Heartbeat] 页面隐藏，暂停心跳');
  } else {
    this.heartbeat?.start();  // 恢复心跳
    console.log('[Heartbeat] 页面可见，恢复心跳');
  }
});
```

##### 陷阱 3：onerror 事件的不可靠性

**问题：** 浏览器规范规定 onerror 事件可能不触发，或仅在控制台报错但不触发 onclose。

**解决方案：**
- **不要仅依赖 onerror**，onclose 才是连接关闭的可靠信号
- 结合**心跳超时检测**主动发现连接死亡
- 设置**连接超时定时器**，onopen 未在规定时间内触发则主动重连

```typescript
connectWithTimeout(timeout: number = 10000): Promise<void> {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      this.ws?.close();
      reject(new Error(`连接超时 (${timeout}ms)`));
    }, timeout);
    
    this.ws.onopen = () => {
      clearTimeout(timer);
      resolve();
    };
    
    this.ws.onclose = () => {
      clearTimeout(timer);
      reject(new Error('连接关闭'));
    };
  });
}
```

##### 陷阱 4：重连后旧消息仍在队列中

**问题：** 多次重连失败后，消息队列可能积压大量过时消息。

**解决方案：**
- **消息有效期**：每条消息携带时间戳，重连后丢弃超时消息
- **最大队列长度**：超过阈值时丢弃最旧消息或拒绝新消息
- **消息序号**：服务端可根据序号去重，防止重复消费

```typescript
interface QueueMessage {
  id: string;
  timestamp: number;
  payload: any;
}

const MAX_QUEUE_SIZE = 100;
const MESSAGE_TTL = 30000; // 消息有效期 30s

send(data: any): void {
  const msg: QueueMessage = {
    id: crypto.randomUUID(),
    timestamp: Date.now(),
    payload: data
  };
  
  if (this.ws?.readyState === WebSocket.OPEN) {
    this.ws.send(JSON.stringify(msg));
  } else {
    // 队列满时丢弃最旧消息
    if (this.messageQueue.length >= MAX_QUEUE_SIZE) {
      this.messageQueue.shift();
      console.warn('[WS] 消息队列已满，丢弃最旧消息');
    }
    this.messageQueue.push(msg);
  }
}

flushMessageQueue(): void {
  const now = Date.now();
  this.messageQueue = this.messageQueue.filter(
    msg => now - msg.timestamp < MESSAGE_TTL
  );
  // ... 发送剩余消息
}
```

##### 陷阱 5：多标签页连接风暴

**问题：** 用户打开多个标签页，每个标签页都建立 WebSocket 连接，消耗服务端资源。

**解决方案：**
- 使用 **BroadcastChannel** 在标签页间协调，只保留一个活跃连接
- 实现**连接所有权**机制，非活跃标签页复用主标签页的连接

```typescript
// 主标签页建立连接，其他标签页通过 BroadcastChannel 复用
const channel = new BroadcastChannel('ws-coordination');

let isOwner = false;
let ws: WebSocket | null = null;

async function initializeConnection() {
  // 尝试成为连接所有者
  isOwner = await tryBecomeOwner();
  
  if (isOwner) {
    ws = new WebSocket(url);
    ws.onmessage = (e) => {
      channel.postMessage({ type: 'message', data: e.data });
    };
  } else {
    // 非所有者，监听主标签页的消息
    channel.onmessage = (e) => {
      if (e.data.type === 'message') {
        handleMessage(e.data.data);
      }
    };
  }
}

// 通过 localStorage 锁实现所有权
async function tryBecomeOwner(): Promise<boolean> {
  return new Promise(resolve => {
    const key = 'ws-connection-owner';
    const lock = navigator.locks.request(key, () => {
      resolve(true); // 获取锁成功
      return new Promise(() => {}); // 保持锁
    });
    // 5 秒内未获得锁则放弃
    setTimeout(() => resolve(false), 5000);
  });
}
```

---

#### 六、考点与评分标准

| 陷阱 | 分值 | 解决方案可行性 |
| --- | --- | --- |
| 重连风暴 + 抖动 | 3 分 | ✅ 生产必需 |
| 页面隐藏心跳暂停 | 2 分 | ✅ 移动端适配 |
| onerror 不可靠 | 2 分 | ✅ 健壮性必备 |
| 消息队列管理 | 3 分 | ✅ 数据可靠性 |
| 多标签页协调 | 2 分 | ✅ 用户体验优化 |

**满分：12 分** | **及格线：7 分**

---

### 题目 4：WebSocket 与 HTTP 长轮询对比
| 指数退避 | `delay * factor^attempt` | 推荐方案，避免服务器压力 |
| 随机退避 | `random(min, max)` | 避免惊群效应 |

**评分标准：**
- 解释心跳检测的必要性和 TCP 假死原因（3 分）
- 区分 WebSocket 协议级 Ping/Pong 和应用层心跳（3 分）
- 实现指数退避重连和离线消息缓存（4 分）

---

### 题目 4：WebSocket 的数据帧格式与二进制传输

**题目描述：** 请说明 WebSocket 数据帧的基本结构，以及如何在 WebSocket 中传输二进制数据（如文件、图片）。同时说明 WebSocket 消息分片（Fragmentation）的作用。

**考察知识点：** 数据帧格式、二进制传输 | **能力等级：** 中级

**参考答案：**

**WebSocket 数据帧结构：**

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-------+-+-------------+-------------------------------+
|F|R|R|R| opcode|M| Payload len |    Extended payload length    |
|I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
|N|V|V|V|       |S|             |                               |
+-+-+-+-+-------+-+-------------+-------------------------------+
|     Extended payload length continued, if payload len == 126  |
+-------------------------------+-------------------------------+
|                               | Masking-key, if MASK set to 1 |
+-------------------------------+-------------------------------+
| Masking-key (continued)       |          Payload Data         |
+-------------------------------+-------------------------------+
```

**帧字段说明：**

| 字段 | 位 | 说明 |
|------|----|------|
| **FIN** | 1 bit | 1 表示消息最后一帧，0 表示还有后续帧（分片） |
| **RSV1-3** | 3 bit | 保留位，扩展用（如压缩） |
| **Opcode** | 4 bit | 操作码，标识帧类型 |
| **MASK** | 1 bit | 客户端到服务器的帧必须掩码 |
| **Payload len** | 7 bit | 载荷长度（0-125 直接表示，126 用 2 字节，127 用 8 字节） |
| **Masking-key** | 0/4 bytes | 掩码密钥（仅客户端发送时存在） |
| **Payload** | 变长 | 实际数据 |

**Opcode 操作码：**

| 值 | 含义 | 说明 |
|----|------|------|
| 0x0 | 延续帧 | 分片消息的后续帧 |
| 0x1 | 文本帧 | UTF-8 文本 |
| 0x2 | 二进制帧 | 二进制数据 |
| 0x8 | 关闭帧 | 关闭连接 |
| 0x9 | Ping | 心跳检测 |
| 0xA | Pong | 心跳响应 |

**二进制数据传输：**

```javascript
// 客户端：发送二进制数据
const socket = new WebSocket('wss://example.com');

// 方式 1：发送 ArrayBuffer
const buffer = new ArrayBuffer(16);
const view = new Uint8Array(buffer);
view[0] = 72; // 'H'
socket.send(buffer);

// 方式 2：发送 Blob（文件）
const fileInput = document.getElementById('fileInput');
fileInput.onchange = () => {
  const file = fileInput.files[0];
  socket.send(file); // Blob 自动以二进制帧发送
};

// 方式 3：发送 TypedArray
const uint8Array = new Uint8Array([1, 2, 3, 4, 5]);
socket.send(uint8Array);

// 方式 4：发送 DataView
const dataView = new DataView(new ArrayBuffer(8));
dataView.setInt32(0, 42);
socket.send(dataView);

// 接收二进制数据：设置 binaryType
socket.binaryType = 'arraybuffer'; // 默认是 'blob'
socket.onmessage = (event) => {
  if (event.data instanceof ArrayBuffer) {
    const view = new Uint8Array(event.data);
    console.log('收到二进制数据:', view);
  } else if (event.data instanceof Blob) {
    // 处理 Blob
    const reader = new FileReader();
    reader.onload = () => console.log(reader.result);
    reader.readAsArrayBuffer(event.data);
  }
};
```

**消息分片（Fragmentation）：**

```javascript
// 服务端：发送大消息时分片
// 场景：发送大文件或长文本，分片可降低内存压力

// 第一帧：FIN=0, Opcode=0x1(文本) 或 0x2(二进制)
// 中间帧：FIN=0, Opcode=0x0(延续帧)
// 最后一帧：FIN=1, Opcode=0x0(延续帧)

// 客户端无感知：WebSocket API 会自动在收到所有分片后组装完整消息
// 分片的作用：
// 1. 大消息不需要一次性缓冲区
// 2. 可以边生成边发送（流式传输）
// 3. 多路复用时混合不同消息的分片（需扩展支持）
```

**评分标准：**
- 描述数据帧的基本结构（4 分）
- 说明 Opcode 种类和用途（2 分）
- 演示二进制数据发送和接收（4 分）

---

### 题目 5：SSE 的基本概念与使用

**题目描述：** 请说明 Server-Sent Events (SSE) 的基本概念、工作原理，并写出完整的客户端和服务端代码示例。

**考察知识点：** SSE 基础、EventSource API | **能力等级：** 初级

**参考答案：**

**SSE 工作原理：**

```
客户端                                    服务器
  |                                         |
  |---- GET /events (Accept: text/event-stream) -->|
  |                                         |
  |<---- HTTP 200 (Content-Type: text/event-stream) --|
  |                                         |
  |<---- data: 消息1                         |
  |<---- data: 消息2                         |
  |<---- data: 消息3                         |
  |        ...持续推送...                      |
```

**客户端代码：**

```javascript
/**
 * SSE 客户端封装
 */
class SSEClient {
  constructor(url, options = {}) {
    this.url = url;
    this.options = {
      withCredentials: false,  // 是否携带 Cookie
      ...options
    };
    this.eventSource = null;
    this.listeners = {};
  }
  
  /**
   * 建立连接
   */
  connect() {
    this.eventSource = new EventSource(this.url, {
      withCredentials: this.options.withCredentials
    });
    
    // 1. 连接建立
    this.eventSource.onopen = (event) => {
      console.log('SSE 连接已建立');
      this.emit('open', event);
    };
    
    // 2. 接收默认消息（event: message 或无 event 指定的消息）
    this.eventSource.onmessage = (event) => {
      let data = event.data;
      try {
        data = JSON.parse(data);
      } catch (e) {
        // 保持原始字符串
      }
      this.emit('message', data);
    };
    
    // 3. 接收自定义事件
    // 注意：自定义事件需要通过 addEventListener 注册，不能通过 on + eventName
    this.eventSource.addEventListener('userLogin', (event) => {
      const data = JSON.parse(event.data);
      this.emit('userLogin', data);
    });
    
    this.eventSource.addEventListener('notification', (event) => {
      const data = JSON.parse(event.data);
      this.emit('notification', data);
    });
    
    this.eventSource.addEventListener('progress', (event) => {
      const data = JSON.parse(event.data);
      this.emit('progress', data);
    });
    
    // 4. 连接错误
    this.eventSource.onerror = (event) => {
      console.error('SSE 连接错误:', event);
      
      // EventSource 会自动重连，无需手动处理
      // 可以通过 readyState 判断连接状态
      if (this.eventSource.readyState === EventSource.CLOSED) {
        console.log('连接已永久关闭');
        this.emit('close', event);
      } else {
        console.log('正在重连...');
        this.emit('reconnecting', event);
      }
    };
  }
  
  /**
   * 关闭连接
   */
  close() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }
  
  /**
   * 事件监听
   */
  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }
  
  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(cb => cb(data));
    }
  }
}

// ---- 使用示例 ----
const sse = new SSEClient('/api/events');

sse.on('open', () => {
  console.log('实时数据推送已就绪');
});

sse.on('message', (data) => {
  console.log('收到消息:', data);
  appendMessage(data);
});

sse.on('notification', (data) => {
  console.log('收到通知:', data);
  showNotification(data.title, data.body);
});

sse.on('progress', (data) => {
  updateProgressBar(data.percent);
});

sse.on('reconnecting', () => {
  showStatus('正在重新连接...');
});

sse.on('close', () => {
  showStatus('连接已断开');
});

sse.connect();

// 关闭连接
// sse.close();
```

**服务端代码（Node.js）：**

```javascript
const http = require('http');

const server = http.createServer((req, res) => {
  if (req.url === '/api/events') {
    // 设置 SSE 响应头
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': '*', // 允许跨域
    });
    
    // 发送注释，建立连接
    res.write(': ok\n\n');
    
    let id = 0;
    
    // 每 2 秒发送一条消息
    const intervalId = setInterval(() => {
      id++;
      
      // 发送带 ID 的消息（支持断线重连）
      res.write(`id: ${id}\n`);
      res.write(`data: ${JSON.stringify({
        time: new Date().toISOString(),
        value: Math.random() * 100
      })}\n\n`);
      
      // 发送自定义事件
      if (id % 5 === 0) {
        res.write(`event: notification\n`);
        res.write(`data: ${JSON.stringify({
          title: '提醒',
          body: `这是第 ${id} 条消息`
        })}\n\n`);
      }
    }, 2000);
    
    // 客户端断开连接时清理
    req.on('close', () => {
      console.log('客户端断开连接');
      clearInterval(intervalId);
      res.end();
    });
    
  } else {
    res.writeHead(404);
    res.end();
  }
});

server.listen(3000, () => {
  console.log('SSE 服务运行在 http://localhost:3000');
});
```

**评分标准：**
- 正确使用 EventSource API 建立连接（3 分）
- 区分 onmessage 和自定义事件监听（3 分）
- 编写服务端正确返回 text/event-stream 格式（4 分）

---

### 题目 6：SSE 的事件类型与自定义事件

**题目描述：** 请说明 SSE 服务器端如何定义不同类型的事件，以及客户端如何分别监听。给出一个完整的多事件类型推送示例。

**考察知识点：** SSE 事件类型 | **能力等级：** 中级

**参考答案：**

**SSE 事件格式：**

```
// 默认事件（未指定 event 字段，客户端用 onmessage 接收）
data: 这是一条默认消息

// 自定义事件（指定 event 字段，客户端用 addEventListener 接收）
event: userLogin
data: {"username": "Alice"}

// 多行数据（客户端收到后合并为一行，用 \n 连接）
data: 第一行
data: 第二行
data: 第三行

// 带 ID 和重试时间的事件
id: 42
retry: 5000
event: update
data: {"status": "completed"}
```

**服务端完整示例：**

```javascript
const http = require('http');

const server = http.createServer((req, res) => {
  if (req.url === '/api/events') {
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': '*'
    });
    
    res.write(': ok\n\n');
    
    // 设置重连间隔（毫秒）
    res.write('retry: 3000\n\n');
    
    // 事件 1：系统通知（默认事件）
    setTimeout(() => {
      res.write(`data: ${JSON.stringify({
        type: 'system',
        message: '系统已就绪'
      })}\n\n`);
    }, 1000);
    
    // 事件 2：用户登录事件（自定义事件）
    setTimeout(() => {
      res.write(`event: userLogin\n`);
      res.write(`data: ${JSON.stringify({
        username: 'Alice',
        loginTime: new Date().toISOString()
      })}\n\n`);
    }, 3000);
    
    // 事件 3：订单状态更新（带 ID）
    setTimeout(() => {
      res.write(`id: 1\n`);
      res.write(`event: orderUpdate\n`);
      res.write(`data: ${JSON.stringify({
        orderId: 'ORD-001',
        status: 'processing'
      })}\n\n`);
    }, 5000);
    
    // 事件 4：进度更新（带 ID 的多行数据）
    setTimeout(() => {
      res.write(`id: 2\n`);
      res.write(`event: progress\n`);
      res.write(`data: ${JSON.stringify({ step: '编译中' })}\n`);
      res.write(`data: ${JSON.stringify({ percent: 50 })}\n\n`);
    }, 7000);
    
    // 模拟实时股票推送
    let stockId = 0;
    const stockInterval = setInterval(() => {
      stockId++;
      res.write(`id: ${stockId}\n`);
      res.write(`event: stockPrice\n`);
      res.write(`data: ${JSON.stringify({
        symbol: 'AAPL',
        price: (150 + Math.random() * 10).toFixed(2),
        change: (Math.random() * 4 - 2).toFixed(2),
        timestamp: new Date().toISOString()
      })}\n\n`);
    }, 2000);
    
    req.on('close', () => {
      clearInterval(stockInterval);
      res.end();
    });
  }
});

server.listen(3000);
```

**客户端监听不同事件：**

```javascript
const eventSource = new EventSource('/api/events');

// 1. 监听默认事件（无 event 字段或 event: message）
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('默认消息:', data);
};

// 2. 监听自定义事件：userLogin
eventSource.addEventListener('userLogin', (event) => {
  const data = JSON.parse(event.data);
  console.log(`用户 ${data.username} 已登录`);
  updateUserStatus(data.username, 'online');
});

// 3. 监听自定义事件：orderUpdate
eventSource.addEventListener('orderUpdate', (event) => {
  const data = JSON.parse(event.data);
  // event.lastEventId 可以获取到消息的 id
  console.log(`订单 ${data.orderId} 状态更新: ${data.status} (ID: ${event.lastEventId})`);
  updateOrderUI(data.orderId, data.status);
});

// 4. 监听自定义事件：progress
eventSource.addEventListener('progress', (event) => {
  // 多行 data 会被合并为一行，用 \n 连接
  const lines = event.data.split('\n');
  const stepInfo = JSON.parse(lines[0]);
  const percentInfo = JSON.parse(lines[1]);
  console.log(`${stepInfo.step}: ${percentInfo.percent}%`);
});

// 5. 监听自定义事件：stockPrice
eventSource.addEventListener('stockPrice', (event) => {
  const data = JSON.parse(event.data);
  updateStockChart(data.symbol, data.price);
});

// 6. 移除事件监听
// eventSource.removeEventListener('stockPrice', handler);
```

**事件类型设计最佳实践：**

```javascript
// 推荐：使用事件类型区分不同业务场景
const EVENT_TYPES = {
  // 默认事件：通用消息
  MESSAGE: 'message',
  
  // 业务事件
  USER_LOGIN: 'userLogin',
  USER_LOGOUT: 'userLogout',
  ORDER_UPDATE: 'orderUpdate',
  NOTIFICATION: 'notification',
  
  // 系统事件
  SYSTEM_STATUS: 'systemStatus',
  ERROR: 'error',
  
  // 实时数据
  STOCK_PRICE: 'stockPrice',
  WEATHER_UPDATE: 'weatherUpdate',
  LIVE_CHAT: 'liveChat'
};
```

**评分标准：**
- 正确使用 event 字段定义自定义事件（3 分）
- 客户端分别监听不同事件类型（3 分）
- 实现多事件类型推送的完整示例（4 分）

---

### 题目 7：SSE 的断线重连与 Last-Event-ID

**题目描述：** 请说明 SSE 自动重连机制的工作原理，以及 `Last-Event-ID` 如何实现断点续传。给出服务端和客户端的完整实现。

**考察知识点：** SSE 重连机制、断点续传 | **能力等级：** 中级

**参考答案：**

**SSE 自动重连机制：**

```
客户端                                    服务器
  |                                         |
  |<---- data: 消息1 (id: 1)                |
  |<---- data: 消息2 (id: 2)                |
  |<---- data: 消息3 (id: 3)                |
  |                                         |
  |---- X 连接断开 X --------               |
  |                                         |
  |---- GET /events ----------------------->|
  |     Last-Event-ID: 3                    |  ← 自动携带最后收到的消息 ID
  |                                         |
  |<---- data: 消息4 (id: 4)                |  ← 服务器从 ID 4 开始发送
  |<---- data: 消息5 (id: 5)                |
```

**服务端断点续传实现：**

```javascript
const http = require('http');

// 模拟消息存储
const messageStore = [];
let nextId = 1;

// 预生成一些历史消息
for (let i = 0; i < 10; i++) {
  messageStore.push({
    id: nextId++,
    type: 'message',
    data: { content: `历史消息 ${i + 1}`, time: new Date().toISOString() }
  });
}

const server = http.createServer((req, res) => {
  if (req.url === '/api/events') {
    // 获取客户端上次收到的最后一条消息 ID
    const lastEventId = parseInt(req.headers['last-event-id']) || 0;
    
    console.log(`客户端连接，Last-Event-ID: ${lastEventId}`);
    
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': '*'
    });
    
    res.write(': ok\n\n');
    
    // 1. 发送断点之后的历史消息（补偿丢失的消息）
    const missedMessages = messageStore.filter(msg => msg.id > lastEventId);
    
    for (const msg of missedMessages) {
      res.write(`id: ${msg.id}\n`);
      res.write(`event: ${msg.type}\n`);
      res.write(`data: ${JSON.stringify(msg.data)}\n\n`);
    }
    
    console.log(`已补发 ${missedMessages.length} 条丢失的消息`);
    
    // 2. 发送实时消息
    const intervalId = setInterval(() => {
      const newMsg = {
        id: nextId++,
        type: 'message',
        data: {
          content: `实时消息 ${new Date().toLocaleTimeString()}`,
          time: new Date().toISOString()
        }
      };
      
      // 存储到消息历史
      messageStore.push(newMsg);
      
      // 限制历史消息数量，防止内存溢出
      if (messageStore.length > 1000) {
        messageStore.splice(0, messageStore.length - 1000);
      }
      
      res.write(`id: ${newMsg.id}\n`);
      res.write(`event: ${newMsg.type}\n`);
      res.write(`data: ${JSON.stringify(newMsg.data)}\n\n`);
    }, 2000);
    
    // 设置重连间隔（建议值）
    res.write('retry: 3000\n\n');
    
    req.on('close', () => {
      console.log('客户端断开连接');
      clearInterval(intervalId);
      res.end();
    });
  }
});

server.listen(3000);
```

**客户端完整实现：**

```javascript
class SSEReconnectClient {
  constructor(url) {
    this.url = url;
    this.es = null;
    this.lastEventId = 0;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
  }
  
  connect() {
    // 注意：EventSource 不支持自定义请求头
    // Last-Event-ID 由浏览器自动设置
    this.es = new EventSource(this.url);
    
    this.es.onopen = () => {
      console.log('SSE 连接建立');
      this.reconnectAttempts = 0;
    };
    
    this.es.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // event.lastEventId 是浏览器自动维护的
      this.lastEventId = parseInt(event.lastEventId) || 0;
      console.log(`收到消息 (ID: ${this.lastEventId}):`, data);
      this.handleMessage(data);
    };
    
    this.es.onerror = (event) => {
      console.error('SSE 错误:', event);
      
      // 浏览器自动重连，但我们可以在重连多次失败后手动干预
      if (this.es.readyState === EventSource.CLOSED) {
        this.reconnectAttempts++;
        
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
          console.error('重连次数已达上限，停止重连');
          this.es.close();
          return;
        }
        
        // 手动重连（浏览器可能不会自动重连 CLOSED 状态）
        const delay = Math.min(1000 * this.reconnectAttempts, 30000);
        console.log(`将在 ${delay}ms 后手动重连`);
        setTimeout(() => this.connect(), delay);
      }
    };
  }
  
  handleMessage(data) {
    // 处理业务逻辑
    console.log('处理消息:', data);
  }
  
  close() {
    if (this.es) {
      this.es.close();
    }
  }
}

// 使用
const client = new SSEReconnectClient('/api/events');
client.connect();
```

**retry 字段的作用：**

```javascript
// 服务端可以动态调整重连间隔
// 方式 1：在数据流中发送 retry 指令
res.write('retry: 5000\n\n'); // 告诉客户端 5 秒后重连

// 方式 2：根据服务器负载动态调整
function getReconnectDelay() {
  const cpuUsage = getCPUUsage();
  if (cpuUsage > 80) return 10000; // 高负载，延长重连
  if (cpuUsage > 50) return 5000;
  return 3000; // 正常情况
}
```

**评分标准：**
- 解释 Last-Event-ID 的工作原理（3 分）
- 服务端实现断点续传补发消息（4 分）
- 客户端重连策略和 retry 字段使用（3 分）

---

### 题目 8：WebSocket 与 SSE 全面对比

**题目描述：** 请从通信方向、协议层、性能、浏览器兼容性、使用场景等多个维度全面对比 WebSocket 和 SSE，并给出技术选型建议。

**考察知识点：** 技术对比、选型能力 | **能力等级：** 中级

**参考答案：**

**全面对比表：**

| 对比维度 | WebSocket | SSE |
|---------|-----------|-----|
| **通信方向** | 全双工（双向） | 单向（服务器 → 客户端） |
| **底层协议** | WebSocket 协议（ws:// / wss://） | HTTP 协议（http:// / https://） |
| **连接建立** | HTTP Upgrade → 101 Switching | 标准 HTTP 长连接 |
| **数据格式** | 文本 + 二进制 | 仅文本（UTF-8） |
| **消息帧开销** | 每帧 2-14 字节 | 每消息约 20-50 字节的文本行 |
| **自动重连** | 需手动实现 | 浏览器原生支持 |
| **断点续传** | 需手动实现 | 原生支持 Last-Event-ID |
| **自定义头部** | 握手时可在 HTTP 头中携带 | 不支持（EventSource 无配置项） |
| **Cookie** | 握手时自动携带 | 同源自动携带 |
| **HTTP/2 优化** | 不受益 | 多路复用，突破连接数限制 |
| **浏览器并发限制** | 无限制（取决于服务器） | HTTP/1.1 同域 6 个连接 |
| **防火墙友好度** | 可能被拦截 | 与普通 HTTP 无异 |
| **IE 支持** | IE 10+ | 不支持（Edge 79+） |
| **移动端** | 良好 | 部分支持 |
| **Node.js 实现** | 需 ws 库或 Socket.IO | 原生 HTTP 模块即可 |
| **Nginx 代理** | 需特殊配置 | 标准 HTTP 代理即可 |
| **负载均衡** | 需粘性会话（Sticky Session） | 无需特殊处理 |
| **消息推送** | 支持 | 支持 |
| **客户端上传** | 支持 | 不支持（需额外 HTTP 请求） |
| **流式传输** | 支持 | 支持 |
| **压缩** | 支持 permessage-deflate | 依赖 HTTP 压缩 |

**技术选型决策树：**

```
需要客户端向服务器发送数据？
  ├── 是 → 需要高频双向通信？（如聊天、游戏）
  │         ├── 是 → WebSocket
  │         └── 否 → HTTP 轮询 / HTTP 请求 + SSE
  │
  └── 否 → 需要二进制数据传输？
            ├── 是 → WebSocket
            └── 否 → 需要断点续传？
                      ├── 是 → SSE
                      └── 否 → 两者皆可，优先 SSE（更简单）
```

**具体场景推荐：**

| 场景 | 推荐技术 | 原因 |
|------|---------|------|
| 在线聊天 / IM | **WebSocket** | 需要双向实时通信 |
| 多人协作编辑 | **WebSocket** | 需要双向实时同步 |
| 实时股价推送 | **SSE** | 单向推送，数据量大，断线重连重要 |
| 体育比分直播 | **SSE** | 单向推送，实时性要求高 |
| 通知推送 | **SSE** | 单向推送，简单可靠 |
| 日志实时查看 | **SSE** | 单向推送，流式数据 |
| 文件上传进度 | **WebSocket** | 需要双向通信（上传 + 进度回调） |
| 在线游戏 | **WebSocket** | 极低延迟、双向高频通信 |
| IoT 设备监控 | **WebSocket** | 双向控制 + 数据上报 |
| AI 对话流式输出 | **SSE** | 单向流式推送，HTTP 友好 |
| 视频会议 | **WebRTC** | WebSocket/SSE 都不适合，需要 P2P |
| 实时仪表盘 | **SSE** | 单向数据推送，实现简单 |
| 客服系统 | **WebSocket** | 双向对话 |
| 社交媒体动态流 | **SSE** | 单向推送，HTTP/2 多路复用优势 |

**评分标准：**
- 从 8 个以上维度全面对比（5 分）
- 给出清晰的决策树或选型逻辑（3 分）
- 列举至少 5 个具体场景的技术选型（2 分）

---

### 题目 9：WebSocket 与 HTTP 长轮询对比

**题目描述：** 请对比 WebSocket 和 HTTP 长轮询（Long Polling）的优缺点，说明为什么 WebSocket 是现代实时通信的主流选择。

**考察知识点：** 长轮询、协议对比 | **能力等级：** 中级

**参考答案：**

**HTTP 长轮询原理：**

```
客户端                                    服务器
  |                                         |
  |---- GET /events ----------------------->|
  |                                         | (等待新消息...)
  |                                         | (等待新消息...)
  |<---- 200 OK (有新消息) ------------------|
  |                                         |
  |---- GET /events ----------------------->|  ← 立即发起新请求
  |                                         | (等待新消息...)
  |<---- 200 OK                             |
  |        ... 循环 ...                       |
```

**HTTP 短轮询 vs 长轮询 vs WebSocket：**

| 对比维度 | 短轮询 (Polling) | 长轮询 (Long Polling) | WebSocket |
|---------|-----------------|---------------------|-----------|
| **实现方式** | 定时器 + setInterval | 挂起请求直到有数据 | 持久 TCP 连接 |
| **请求频率** | 固定间隔（如 1s） | 有数据时立即返回 | 事件驱动 |
| **延迟** | 取决于轮询间隔（高） | 较低 | 极低 |
| **服务器资源** | 消耗大（大量无效请求） | 消耗中等 | 消耗小（单连接） |
| **HTTP 开销** | 每请求完整 HTTP 头 | 每请求完整 HTTP 头 | 仅握手时有 HTTP 开销 |
| **并发能力** | 差 | 一般 | 优秀 |
| **实现复杂度** | 简单 | 中等 | 中等 |
| **消息方向** | 半双工 | 半双工 | 全双工 |

**代码对比：**

```javascript
// ===== HTTP 长轮询 =====
// 客户端
async function longPoll() {
  try {
    const response = await fetch('/api/poll', {
      method: 'GET',
      headers: { 'Connection': 'keep-alive' }
    });
    
    const data = await response.json();
    console.log('收到消息:', data);
    
    // 立即发起下一次轮询
    longPoll();
    
  } catch (error) {
    console.error('轮询失败:', error);
    setTimeout(() => longPoll(), 5000); // 错误后延迟重试
  }
}

// 服务端（Node.js）
app.get('/api/poll', (req, res) => {
  // 等待新消息，最多等待 30 秒
  waitForMessage(30000)
    .then(msg => {
      res.json(msg);
    })
    .catch(() => {
      res.status(304).end(); // 超时，无新消息
    });
});

// ===== WebSocket =====
// 客户端
const ws = new WebSocket('wss://example.com/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('收到消息:', data);
};

// 服务端（Node.js + ws）
wss.on('connection', (ws) => {
  ws.on('message', (data) => {
    // 收到客户端消息
  });
  
  // 有新消息直接推送
  onNewMessage((msg) => {
    ws.send(JSON.stringify(msg));
  });
});
```

**WebSocket 取代长轮询的原因：**

1. **资源效率**：WebSocket 仅需一个 TCP 连接，长轮询每次请求都需要建立新连接或复用时有开销
2. **延迟更低**：WebSocket 事件驱动，消息到达立即推送；长轮询在请求间隙可能有延迟
3. **HTTP 头开销**：长轮询每次请求携带完整 HTTP 头（Cookie、User-Agent 等），WebSocket 帧头仅 2-14 字节
4. **全双工**：WebSocket 支持双向同时通信，长轮询只能半双工
5. **服务器压力**：大量客户端时长轮询会占用大量连接和线程资源

**评分标准：**
- 解释长轮询的工作原理（3 分）
- 从多个维度对比三种方案（4 分）
- 分析 WebSocket 取代长轮询的原因（3 分）

---

### 题目 10：实时通信技术的适用场景选择

**题目描述：** 给定以下业务场景，请选择最合适的实时通信技术（WebSocket、SSE、HTTP 轮询），并说明理由。

**考察知识点：** 技术选型、场景分析 | **能力等级：** 中级

**参考答案：**

**场景分析：**

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| **在线客服聊天** | WebSocket | 需要双向对话，客服和用户都能主动发送消息 |
| **股票行情推送** | SSE | 单向推送，数据量大，需要断线重连和断点续传 |
| **AI 对话流式输出** | SSE | 单向流式推送，基于 HTTP 易于部署和扩展 |
| **多人协作文档** | WebSocket | 需要双向实时同步编辑操作 |
| **系统通知推送** | SSE | 单向推送，实现简单，无需维护双向连接 |
| **实时日志查看** | SSE | 单向流式推送，自然文本流 |
| **在线游戏** | WebSocket | 极低延迟要求，双向高频通信 |
| **文件上传进度** | WebSocket | 上传过程需要双向通信 |
| **IoT 设备监控** | WebSocket | 需要双向：设备上报 + 云端下发指令 |
| **实时仪表盘** | SSE | 单向数据推送，HTTP/2 下多路复用优势明显 |
| **体育比分直播** | SSE | 单向推送，实时性要求高，需断线重连 |
| **视频会议** | WebRTC | 都不是最优选，需要 P2P 音视频传输 |
| **社交媒体动态流** | SSE | 单向推送，实现简单，HTTP 基础设施友好 |
| **简单的配置更新通知** | HTTP 轮询 | 场景简单，轮询间隔可接受，无需维护长连接 |

**选型决策框架：**

```
1. 是否需要客户端主动发送数据？
   - 是 → WebSocket
   - 否 → 进入第 2 步

2. 是否需要二进制数据传输？
   - 是 → WebSocket
   - 否 → 进入第 3 步

3. 是否需要断点续传（重连后不丢失消息）？
   - 是 → SSE（原生支持 Last-Event-ID）
   - 否 → 进入第 4 步

4. 是否需要兼容 IE 或特殊网络环境？
   - 是 → WebSocket（兼容性更广）
   - 否 → SSE（更简单）

5. 并发连接数是否非常大（10w+）？
   - 是 → SSE + HTTP/2（多路复用优势）
   - 否 → 两者皆可
```

**混合方案：**

在某些场景下，可以结合使用两种技术：

```javascript
// 混合方案示例：SSE 接收通知 + WebSocket 处理聊天
class HybridCommunication {
  constructor() {
    // SSE 用于系统通知、状态更新
    this.sse = new EventSource('/api/notifications');
    this.sse.addEventListener('notification', this.handleNotification);
    this.sse.addEventListener('statusUpdate', this.handleStatusUpdate);
    
    // WebSocket 用于聊天、实时协作
    this.ws = new WebSocket('wss://example.com/chat');
    this.ws.onmessage = this.handleChatMessage;
  }
  
  handleNotification(event) {
    const data = JSON.parse(event.data);
    showToast(data.title, data.message);
  }
  
  handleChatMessage(event) {
    const data = JSON.parse(event.data);
    appendChatMessage(data);
  }
}
```

**评分标准：**
- 对 8 个以上场景给出正确选型（4 分）
- 给出清晰的决策框架（3 分）
- 说明混合方案的适用性（3 分）

---

### 题目 11：WebSocket 服务端实现（Node.js）

**题目描述：** 请使用 Node.js 实现一个完整的 WebSocket 服务端，包括连接管理、消息广播、房间机制和身份认证。

**考察知识点：** WebSocket 服务端、ws 库 | **能力等级：** 高级

**参考答案：**

```javascript
// server.js
const WebSocket = require('ws');
const http = require('http');
const url = require('url');
const crypto = require('crypto');

const server = http.createServer();
const wss = new WebSocket.Server({ noServer: true });

// ===== 连接管理 =====
const clients = new Map();     // clientId → { ws, userId, rooms, info }
const rooms = new Map();       // roomName → Set<clientId>

// ===== 身份认证（在 HTTP 握手阶段） =====
server.on('upgrade', (req, socket, head) => {
  const { pathname, query } = url.parse(req.url, true);
  
  // 从 URL 参数中获取 Token
  const token = query.token;
  
  // 验证 Token
  authenticateToken(token)
    .then((user) => {
      // 认证通过，升级到 WebSocket
      wss.handleUpgrade(req, socket, head, (ws) => {
        // 将用户信息附加到 WebSocket 实例
        ws.userId = user.id;
        ws.username = user.username;
        
        wss.emit('connection', ws, req);
      });
    })
    .catch(() => {
      // 认证失败，拒绝连接
      socket.write('HTTP/1.1 401 Unauthorized\r\n\r\n');
      socket.destroy();
    });
});

// ===== 连接事件 =====
wss.on('connection', (ws, req) => {
  const clientId = generateClientId();
  const clientInfo = {
    ws,
    userId: ws.userId,
    username: ws.username,
    rooms: new Set(),
    connectedAt: new Date(),
    ip: req.socket.remoteAddress
  };
  
  clients.set(clientId, clientInfo);
  
  console.log(`客户端连接: ${ws.username} (${clientId})`);
  broadcastStats();
  
  // 发送欢迎消息
  sendToClient(ws, {
    type: 'welcome',
    clientId,
    message: `欢迎 ${ws.username}`
  });
  
  // ===== 消息处理 =====
  ws.on('message', (rawData) => {
    let message;
    try {
      message = JSON.parse(rawData.toString());
    } catch (e) {
      sendToClient(ws, { type: 'error', message: '消息格式错误' });
      return;
    }
    
    handleMessage(clientId, message);
  });
  
  // ===== 连接关闭 =====
  ws.on('close', () => {
    // 从所有房间中移除
    clientInfo.rooms.forEach(roomName => {
      leaveRoom(clientId, roomName);
    });
    
    clients.delete(clientId);
    console.log(`客户端断开: ${ws.username} (${clientId})`);
    broadcastStats();
  });
  
  // ===== 心跳检测 =====
  ws.isAlive = true;
  ws.on('pong', () => {
    ws.isAlive = true;
  });
});

// ===== 消息处理 =====
function handleMessage(clientId, message) {
  const client = clients.get(clientId);
  if (!client) return;
  
  const { type, payload } = message;
  
  switch (type) {
    case 'ping':
      // 应用层心跳
      sendToClient(client.ws, { type: 'pong' });
      break;
      
    case 'joinRoom':
      // 加入房间
      joinRoom(clientId, payload.roomName);
      break;
      
    case 'leaveRoom':
      // 离开房间
      leaveRoom(clientId, payload.roomName);
      break;
      
    case 'roomMessage':
      // 发送房间消息
      broadcastToRoom(payload.roomName, {
        type: 'roomMessage',
        from: client.username,
        content: payload.content,
        timestamp: Date.now()
      }, clientId); // 排除发送者
      break;
      
    case 'broadcast':
      // 全局广播
      broadcastToAll({
        type: 'broadcast',
        from: client.username,
        content: payload.content,
        timestamp: Date.now()
      }, clientId);
      break;
      
    case 'privateMessage':
      // 私聊
      sendPrivateMessage(clientId, payload.targetUserId, {
        type: 'privateMessage',
        from: client.username,
        content: payload.content,
        timestamp: Date.now()
      });
      break;
      
    default:
      sendToClient(client.ws, {
        type: 'error',
        message: `不支持的消息类型: ${type}`
      });
  }
}

// ===== 房间管理 =====
function joinRoom(clientId, roomName) {
  const client = clients.get(clientId);
  if (!client) return;
  
  if (!rooms.has(roomName)) {
    rooms.set(roomName, new Set());
  }
  
  rooms.get(roomName).add(clientId);
  client.rooms.add(roomName);
  
  // 通知房间内其他用户
  broadcastToRoom(roomName, {
    type: 'userJoined',
    username: client.username,
    roomName
  }, clientId);
  
  // 发送当前房间成员列表
  const roomClients = getRoomClients(roomName);
  sendToClient(client.ws, {
    type: 'roomInfo',
    roomName,
    users: roomClients.map(c => ({
      id: c.userId,
      username: c.username
    }))
  });
}

function leaveRoom(clientId, roomName) {
  const client = clients.get(clientId);
  if (!client) return;
  
  const room = rooms.get(roomName);
  if (room) {
    room.delete(clientId);
    if (room.size === 0) {
      rooms.delete(roomName);
    }
  }
  
  client.rooms.delete(roomName);
  
  // 通知房间内其他用户
  broadcastToRoom(roomName, {
    type: 'userLeft',
    username: client.username,
    roomName
  });
}

// ===== 消息发送 =====
function sendToClient(ws, message) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(message));
  }
}

function broadcastToRoom(roomName, message, excludeClientId) {
  const room = rooms.get(roomName);
  if (!room) return;
  
  room.forEach(clientId => {
    if (clientId === excludeClientId) return;
    const client = clients.get(clientId);
    if (client) {
      sendToClient(client.ws, message);
    }
  });
}

function broadcastToAll(message, excludeClientId) {
  clients.forEach((client, clientId) => {
    if (clientId === excludeClientId) return;
    sendToClient(client.ws, message);
  });
}

function sendPrivateMessage(fromClientId, toUserId, message) {
  // 根据 userId 查找客户端
  for (const [clientId, client] of clients) {
    if (client.userId === toUserId) {
      sendToClient(client.ws, message);
      return;
    }
  }
  
  // 目标用户不在线
  const fromClient = clients.get(fromClientId);
  if (fromClient) {
    sendToClient(fromClient.ws, {
      type: 'error',
      message: '用户不在线'
    });
  }
}

// ===== 辅助函数 =====
function getRoomClients(roomName) {
  const room = rooms.get(roomName);
  if (!room) return [];
  
  return Array.from(room)
    .map(clientId => clients.get(clientId))
    .filter(Boolean);
}

function broadcastStats() {
  broadcastToAll({
    type: 'stats',
    onlineCount: clients.size,
    roomCount: rooms.size
  });
}

function generateClientId() {
  return crypto.randomUUID();
}

async function authenticateToken(token) {
  // 实际项目中验证 JWT Token
  if (!token) throw new Error('未提供 Token');
  // 模拟验证
  return { id: '123', username: 'Alice' };
}

// ===== 心跳检测定时器 =====
const heartbeatInterval = setInterval(() => {
  wss.clients.forEach((ws) => {
    if (ws.isAlive === false) {
      console.log('心跳超时，断开连接');
      return ws.terminate();
    }
    ws.isAlive = false;
    ws.ping();
  });
}, 30000);

wss.on('close', () => clearInterval(heartbeatInterval));

// 启动服务器
server.listen(8080, () => {
  console.log('WebSocket 服务运行在 ws://localhost:8080');
});
```

**评分标准：**
- 实现连接管理和身份认证（4 分）
- 实现房间机制和消息广播（3 分）
- 实现心跳检测和错误处理（3 分）

---

### 题目 12：SSE 服务端实现（Node.js）

**题目描述：** 请使用 Node.js 实现一个完整的 SSE 服务端，包括多用户连接管理、定时推送、事件分类和优雅关闭。

**考察知识点：** SSE 服务端、连接管理 | **能力等级：** 高级

**参考答案：**

```javascript
const http = require('http');

/**
 * SSE 服务端实现
 */
class SSEServer {
  constructor() {
    // 客户端连接管理：Map<clientId, { id, res, subscribedEvents }>
    this.clients = new Map();
    
    // 事件发布者管理
    this.publishers = new Map();
    
    this.clientIdCounter = 0;
  }
  
  /**
   * 添加客户端连接
   */
  addClient(req, res) {
    const clientId = ++this.clientIdCounter;
    const client = {
      id: clientId,
      req,
      res,
      subscribedEvents: new Set(['message']), // 默认订阅 message 事件
      connectedAt: new Date(),
      lastEventId: 0
    };
    
    this.clients.set(clientId, client);
    
    console.log(`客户端 ${clientId} 连接，当前在线: ${this.clients.size}`);
    
    // 设置 SSE 响应头
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': req.headers.origin || '*',
      'Access-Control-Allow-Credentials': 'true'
    });
    
    // 发送连接确认
    res.write(': ok\n\n');
    
    // 发送客户端 ID
    this.sendEvent(clientId, 'connected', {
      clientId,
      message: '连接成功',
      onlineCount: this.clients.size
    });
    
    // 客户端断开时清理
    req.on('close', () => {
      this.removeClient(clientId);
    });
    
    // 定期发送心跳
    client.heartbeatTimer = setInterval(() => {
      res.write(': heartbeat\n\n');
    }, 15000);
    
    return clientId;
  }
  
  /**
   * 移除客户端连接
   */
  removeClient(clientId) {
    const client = this.clients.get(clientId);
    if (!client) return;
    
    clearInterval(client.heartbeatTimer);
    this.clients.delete(clientId);
    
    console.log(`客户端 ${clientId} 断开，当前在线: ${this.clients.size}`);
    
    // 通知其他客户端在线人数变化
    this.broadcast('status', {
      onlineCount: this.clients.size,
      event: 'userLeft',
      clientId
    });
  }
  
  /**
   * 发送事件给指定客户端
   */
  sendEvent(clientId, eventName, data, eventId = null) {
    const client = this.clients.get(clientId);
    if (!client) return false;
    
    const { res, subscribedEvents } = client;
    
    // 检查是否订阅了该事件
    if (!subscribedEvents.has(eventName) && eventName !== 'connected') {
      return false;
    }
    
    const payload = JSON.stringify(data);
    
    // 发送事件 ID
    if (eventId !== null) {
      res.write(`id: ${eventId}\n`);
      client.lastEventId = eventId;
    } else {
      res.write(`id: ${++client.lastEventId}\n`);
    }
    
    // 发送事件类型
    if (eventName !== 'message') {
      res.write(`event: ${eventName}\n`);
    }
    
    // 发送数据（多行数据用 \n 分割）
    res.write(`data: ${payload}\n\n`);
    
    return true;
  }
  
  /**
   * 广播事件给所有客户端
   */
  broadcast(eventName, data, eventId = null) {
    let sentCount = 0;
    this.clients.forEach((client, clientId) => {
      if (this.sendEvent(clientId, eventName, data, eventId)) {
        sentCount++;
      }
    });
    return sentCount;
  }
  
  /**
   * 广播事件给订阅了特定事件的客户端
   */
  broadcastToSubscribers(eventName, data, eventId = null) {
    let sentCount = 0;
    this.clients.forEach((client, clientId) => {
      if (client.subscribedEvents.has(eventName)) {
        if (this.sendEvent(clientId, eventName, data, eventId)) {
          sentCount++;
        }
      }
    });
    return sentCount;
  }
  
  /**
   * 客户端订阅事件
   */
  subscribe(clientId, eventName) {
    const client = this.clients.get(clientId);
    if (client) {
      client.subscribedEvents.add(eventName);
    }
  }
  
  /**
   * 客户端取消订阅
   */
  unsubscribe(clientId, eventName) {
    const client = this.clients.get(clientId);
    if (client) {
      client.subscribedEvents.delete(eventName);
    }
  }
  
  /**
   * 获取在线统计
   */
  getStats() {
    return {
      onlineCount: this.clients.size,
      clients: Array.from(this.clients.values()).map(c => ({
        id: c.id,
        connectedAt: c.connectedAt,
        subscribedEvents: Array.from(c.subscribedEvents)
      }))
    };
  }
  
  /**
   * 定时发布者
   */
  createPublisher(name, interval, dataGenerator) {
    const timer = setInterval(() => {
      const data = dataGenerator();
      this.broadcastToSubscribers(name, data);
    }, interval);
    
    this.publishers.set(name, timer);
    return timer;
  }
  
  /**
   * 停止定时发布者
   */
  stopPublisher(name) {
    const timer = this.publishers.get(name);
    if (timer) {
      clearInterval(timer);
      this.publishers.delete(name);
    }
  }
  
  /**
   * 优雅关闭
   */
  shutdown() {
    console.log('正在关闭 SSE 服务...');
    
    // 停止所有定时发布者
    this.publishers.forEach((timer, name) => {
      clearInterval(timer);
    });
    this.publishers.clear();
    
    // 通知所有客户端
    this.broadcast('shutdown', {
      message: '服务器即将关闭',
      timestamp: new Date().toISOString()
    });
    
    // 关闭所有连接
    this.clients.forEach((client) => {
      client.res.end();
    });
    this.clients.clear();
    
    console.log('SSE 服务已关闭');
  }
}

// ===== 使用示例 =====
const sseServer = new SSEServer();

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  
  if (url.pathname === '/api/events') {
    // 建立 SSE 连接
    const clientId = sseServer.addClient(req, res);
    
    // 处理客户端订阅请求（通过 URL 参数）
    const events = url.searchParams.get('events');
    if (events) {
      events.split(',').forEach(event => {
        sseServer.subscribe(clientId, event.trim());
      });
    }
    
  } else if (url.pathname === '/api/stats') {
    // 获取在线统计
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(sseServer.getStats()));
    
  } else if (url.pathname === '/api/trigger' && req.method === 'POST') {
    // 手动触发事件（用于测试）
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      const { event, data } = JSON.parse(body);
      const count = sseServer.broadcast(event, data);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ sent: count }));
    });
    
  } else {
    res.writeHead(404);
    res.end();
  }
});

// 创建定时发布者
// 1. 每 2 秒推送系统状态
sseServer.createPublisher('systemStatus', 2000, () => ({
  cpuUsage: (Math.random() * 100).toFixed(1),
  memoryUsage: (Math.random() * 100).toFixed(1),
  onlineCount: sseServer.clients.size,
  timestamp: new Date().toISOString()
}));

// 2. 每 5 秒推送通知
sseServer.createPublisher('notification', 5000, () => ({
  title: '系统通知',
  message: `当前在线 ${sseServer.clients.size} 人`,
  time: new Date().toLocaleTimeString()
}));

server.listen(3000, () => {
  console.log('SSE 服务运行在 http://localhost:3000');
});

// 优雅关闭
process.on('SIGTERM', () => {
  sseServer.shutdown();
  server.close();
});
```

**评分标准：**
- 实现客户端连接管理（3 分）
- 实现事件分类和订阅机制（3 分）
- 实现定时发布者和优雅关闭（4 分）

---

### 题目 13：WebSocket 跨域与安全

**题目描述：** 请说明 WebSocket 的跨域策略和安全风险，以及如何防范常见的 WebSocket 安全攻击（如 CSWSH、DoS、消息注入等）。

**考察知识点：** 跨域安全、攻击防范 | **能力等级：** 高级

**参考答案：**

**WebSocket 跨域策略：**

WebSocket **不受同源策略限制**，任何来源的网页都可以发起 WebSocket 连接。但服务端可以通过检查 `Origin` 请求头来验证请求来源。

```javascript
// 服务端验证 Origin
const http = require('http');
const WebSocket = require('ws');

const ALLOWED_ORIGINS = [
  'https://myapp.com',
  'https://admin.myapp.com'
];

const server = http.createServer();
const wss = new WebSocket.Server({ noServer: true });

server.on('upgrade', (req, socket, head) => {
  const origin = req.headers.origin;
  
  // 验证 Origin
  if (!ALLOWED_ORIGINS.includes(origin)) {
    console.warn(`拒绝来自 ${origin} 的 WebSocket 连接`);
    socket.write('HTTP/1.1 403 Forbidden\r\n\r\n');
    socket.destroy();
    return;
  }
  
  wss.handleUpgrade(req, socket, head, (ws) => {
    wss.emit('connection', ws, req);
  });
});
```

**常见安全攻击及防范：**

**1. CSWSH（Cross-Site WebSocket Hijacking）：**

```javascript
// 攻击原理：恶意网站通过 WebSocket 连接到受害者的服务
// 浏览器会自动携带目标域的 Cookie（如果设置了 credentials）

// 防范措施：
// 方案 1：验证 Origin 头
server.on('upgrade', (req, socket, head) => {
  const origin = req.headers.origin;
  if (!isAllowedOrigin(origin)) {
    socket.destroy();
    return;
  }
  // ...
});

// 方案 2：使用 Token 认证（而非 Cookie）
// 在 URL 参数中传递 Token
const ws = new WebSocket(`wss://example.com/ws?token=${getToken()}`);

// 服务端验证
server.on('upgrade', (req, socket, head) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const token = url.searchParams.get('token');
  
  if (!validateToken(token)) {
    socket.write('HTTP/1.1 401 Unauthorized\r\n\r\n');
    socket.destroy();
    return;
  }
  // ...
});

// 方案 3：使用自定义子协议头
const ws = new WebSocket('wss://example.com/ws', ['authorization_token_xxx']);
```

**2. DoS（拒绝服务）攻击：**

```javascript
// 防范措施：
// 1. 限制最大连接数
const MAX_CONNECTIONS = 10000;
let connectionCount = 0;

wss.on('connection', (ws) => {
  connectionCount++;
  if (connectionCount > MAX_CONNECTIONS) {
    ws.close(1013, '服务器繁忙');
    return;
  }
  
  ws.on('close', () => connectionCount--);
});

// 2. 限制单 IP 连接数
const ipConnections = new Map();
const MAX_CONNECTIONS_PER_IP = 10;

server.on('upgrade', (req, socket, head) => {
  const ip = req.socket.remoteAddress;
  const count = ipConnections.get(ip) || 0;
  
  if (count >= MAX_CONNECTIONS_PER_IP) {
    socket.destroy();
    return;
  }
  
  ipConnections.set(ip, count + 1);
  
  wss.handleUpgrade(req, socket, head, (ws) => {
    ws.on('close', () => {
      const current = ipConnections.get(ip) || 0;
      if (current <= 1) {
        ipConnections.delete(ip);
      } else {
        ipConnections.set(ip, current - 1);
      }
    });
    wss.emit('connection', ws, req);
  });
});

// 3. 限制消息速率
const rateLimitMap = new Map();

wss.on('connection', (ws) => {
  const clientId = generateClientId();
  rateLimitMap.set(clientId, { count: 0, resetTime: Date.now() + 1000 });
  
  ws.on('message', (data) => {
    const limit = rateLimitMap.get(clientId);
    const now = Date.now();
    
    if (now > limit.resetTime) {
      limit.count = 0;
      limit.resetTime = now + 1000;
    }
    
    limit.count++;
    if (limit.count > 50) { // 每秒最多 50 条消息
      ws.close(1008, '消息频率过高');
      return;
    }
    
    // 处理消息...
  });
  
  ws.on('close', () => rateLimitMap.delete(clientId));
});

// 4. 限制消息大小
wss.on('connection', (ws) => {
  const MAX_MESSAGE_SIZE = 1024 * 1024; // 1MB
  ws.on('message', (data) => {
    if (data.length > MAX_MESSAGE_SIZE) {
      ws.close(1009, '消息过大');
      return;
    }
    // 处理消息...
  });
});
```

**3. 消息注入/XSS：**

```javascript
// 防范：对消息内容进行校验和转义
function sanitizeMessage(message) {
  // 验证消息结构
  if (typeof message !== 'object' || !message.type) {
    throw new Error('无效的消息格式');
  }
  
  // 限制消息内容长度
  if (message.content && message.content.length > 10000) {
    throw new Error('消息内容过长');
  }
  
  // 过滤危险字符
  if (message.content) {
    message.content = escapeHtml(message.content);
  }
  
  return message;
}

function escapeHtml(str) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;'
  };
  return str.replace(/[&<>"']/g, char => map[char]);
}
```

**WebSocket 安全最佳实践总结：**

| 安全措施 | 说明 |
|---------|------|
| 验证 Origin | 检查请求来源，防止 CSWSH |
| Token 认证 | 在握手阶段验证身份 |
| WSS 加密 | 生产环境使用 wss:// 协议 |
| 连接数限制 | 防止 DoS 攻击 |
| 消息速率限制 | 防止消息洪水 |
| 消息大小限制 | 防止大消息耗尽内存 |
| 消息内容校验 | 防止 XSS 和注入攻击 |
| 心跳超时断开 | 清理僵死连接 |
| 日志审计 | 记录异常连接和消息 |

**评分标准：**
- 说明 WebSocket 跨域策略和 Origin 验证（3 分）
- 解释 CSWSH 攻击原理和防范（3 分）
- 实现 DoS 防范和消息校验（4 分）

---

### 题目 14：WebSocket 的负载均衡与集群方案

**题目描述：** 请说明 WebSocket 在集群部署时面临的挑战，以及如何通过粘性会话（Sticky Session）、消息中间件（Redis Pub/Sub）等方式实现水平扩展。

**考察知识点：** 集群部署、消息中间件 | **能力等级：** 高级

**参考答案：**

**WebSocket 集群挑战：**

```
客户端 A ----→ 服务器 1（持有 WebSocket 连接 A）
客户端 B ----→ 服务器 2（持有 WebSocket 连接 B）

问题：客户端 A 想给客户端 B 发消息，但它们在不通的服务器上！
```

**方案 1：粘性会话（Sticky Session）：**

```nginx
# Nginx 配置：基于 IP 的粘性会话
upstream websocket_cluster {
    ip_hash;  # 同一 IP 始终路由到同一服务器
    
    server 192.168.1.10:8080;
    server 192.168.1.11:8080;
    server 192.168.1.12:8080;
}

server {
    listen 443 ssl;
    server_name ws.example.com;
    
    location /ws {
        proxy_pass http://websocket_cluster;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 3600s;  # 长连接超时
        proxy_send_timeout 3600s;
    }
}
```

**方案 2：Redis Pub/Sub 消息广播（推荐）：**

```javascript
// server.js
const WebSocket = require('ws');
const Redis = require('ioredis');
const http = require('http');

// Redis 客户端
const pubClient = new Redis();
const subClient = new Redis();

const server = http.createServer();
const wss = new WebSocket.Server({ server });

// 本地客户端连接管理
const localClients = new Map(); // clientId → ws

wss.on('connection', (ws) => {
  const clientId = generateClientId();
  localClients.set(clientId, ws);
  
  console.log(`客户端 ${clientId} 连接到本节点`);
  
  // 1. 客户端发送消息 → 发布到 Redis
  ws.on('message', (rawData) => {
    const message = JSON.parse(rawData.toString());
    
    if (message.type === 'privateMessage') {
      // 通过 Redis 发布私聊消息
      pubClient.publish('chat:private', JSON.stringify({
        fromClientId: clientId,
        targetClientId: message.targetClientId,
        content: message.content,
        nodeId: process.env.NODE_ID
      }));
    } else if (message.type === 'broadcast') {
      // 全局广播
      pubClient.publish('chat:broadcast', JSON.stringify({
        content: message.content,
        nodeId: process.env.NODE_ID
      }));
    }
  });
  
  // 2. 客户端断开 → 通知其他节点
  ws.on('close', () => {
    localClients.delete(clientId);
    pubClient.publish('user:offline', JSON.stringify({
      clientId,
      nodeId: process.env.NODE_ID
    }));
  });
});

// 3. 订阅 Redis 频道，接收其他节点的消息
subClient.subscribe('chat:private', 'chat:broadcast', 'user:offline');

subClient.on('message', (channel, message) => {
  const data = JSON.parse(message);
  
  // 忽略本节点发出的消息
  if (data.nodeId === process.env.NODE_ID) return;
  
  switch (channel) {
    case 'chat:private':
      // 检查目标客户端是否在本节点
      const targetWs = localClients.get(data.targetClientId);
      if (targetWs && targetWs.readyState === WebSocket.OPEN) {
        targetWs.send(JSON.stringify({
          type: 'privateMessage',
          from: data.fromClientId,
          content: data.content
        }));
      }
      break;
      
    case 'chat:broadcast':
      // 广播给本节点所有客户端
      localClients.forEach((ws) => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({
            type: 'broadcast',
            content: data.content
          }));
        }
      });
      break;
      
    case 'user:offline':
      // 通知本节点客户端某用户下线
      localClients.forEach((ws) => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({
            type: 'userOffline',
            clientId: data.clientId
          }));
        }
      });
      break;
  }
});

server.listen(8080);
```

**方案 3：使用 Redis 存储全局状态：**

```javascript
// 全局客户端注册表（Redis）
class GlobalClientRegistry {
  constructor() {
    this.redis = new Redis();
    this.NODE_ID = process.env.NODE_ID;
  }
  
  // 注册客户端
  async register(clientId, userId) {
    // 存储客户端所在节点
    await this.redis.set(
      `client:${clientId}:node`,
      this.NODE_ID,
      'EX', 3600
    );
    // 存储用户的客户端列表
    await this.redis.sadd(
      `user:${userId}:clients`,
      clientId
    );
  }
  
  // 注销客户端
  async unregister(clientId, userId) {
    await this.redis.del(`client:${clientId}:node`);
    await this.redis.srem(`user:${userId}:clients`, clientId);
  }
  
  // 查找客户端所在节点
  async getClientNode(clientId) {
    return this.redis.get(`client:${clientId}:node`);
  }
  
  // 获取用户的所有客户端
  async getUserClients(userId) {
    return this.redis.smembers(`user:${userId}:clients`);
  }
}
```

**方案对比：**

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| **Sticky Session** | 实现简单，无需额外中间件 | 扩展性差，节点故障丢失连接 | 小规模部署 |
| **Redis Pub/Sub** | 实时性好，实现相对简单 | 消息不持久化，丢失后无法恢复 | 中等规模，可接受少量消息丢失 |
| **Redis Stream / Kafka** | 消息持久化，可靠投递 | 实现复杂，延迟略高 | 大规模，消息可靠性要求高 |
| **MQTT Broker** | 专为物联网设计，支持 QoS | 引入额外组件 | IoT 场景 |

**评分标准：**
- 说明 WebSocket 集群的挑战（2 分）
- 实现 Nginx 粘性会话配置（3 分）
- 实现 Redis Pub/Sub 跨节点消息广播（5 分）

---

### 题目 15：SSE 的局限性及突破方案

**题目描述：** 请说明 SSE 的主要局限性（如浏览器连接数限制、仅支持 GET 请求、不支持二进制等），以及针对这些限制的突破方案。

**考察知识点：** SSE 局限性、解决方案 | **能力等级：** 高级

**参考答案：**

**SSE 局限性分析：**

| 局限性 | 说明 | 影响 |
|--------|------|------|
| **浏览器连接数限制** | HTTP/1.1 下同域最多 6 个并发连接 | 多标签页或多 SSE 源时可能阻塞 |
| **仅支持 GET 请求** | EventSource 无法发送 POST 请求 | 无法携带大量请求参数 |
| **不支持自定义请求头** | 无法设置 Authorization 等头 | 认证依赖 Cookie 或 URL 参数 |
| **仅文本数据** | 不支持二进制传输 | 不能传输图片、文件等 |
| **单向通信** | 客户端无法主动发送数据 | 需要双向通信时需额外 HTTP 请求 |
| **IE 不支持** | EventSource 在 IE 中不可用 | 需要 Polyfill 或降级方案 |
| **连接恢复的局限性** | 重连后可能丢失部分消息 | 需要服务端保存历史消息 |

**突破方案：**

**1. 突破浏览器连接数限制：**

```javascript
// 方案 1：使用 HTTP/2（推荐）
// HTTP/2 支持多路复用，同域可建立数百个并发流
// 服务端配置 HTTP/2（Node.js + HTTP/2）
const http2 = require('http2');
const fs = require('fs');

const server = http2.createSecureServer({
  key: fs.readFileSync('key.pem'),
  cert: fs.readFileSync('cert.pem')
});

server.on('stream', (stream, headers) => {
  if (headers[':path'] === '/api/events') {
    stream.respond({
      'content-type': 'text/event-stream',
      'cache-control': 'no-cache',
      ':status': 200
    });
    
    // SSE 数据推送...
    setInterval(() => {
      stream.write(`data: ${JSON.stringify({ time: Date.now() })}\n\n`);
    }, 1000);
  }
});

// 方案 2：使用 SharedWorker 共享 SSE 连接
// share-sse-worker.js（SharedWorker）
const connections = new Map();

self.onconnect = (e) => {
  const port = e.ports[0];
  const tabId = Date.now();
  
  // 如果还没有建立 SSE 连接
  if (connections.size === 0) {
    const es = new EventSource('/api/events');
    
    es.onmessage = (event) => {
      // 广播给所有 Tab
      connections.forEach((p) => {
        p.postMessage({ type: 'sse-message', data: event.data });
      });
    };
    
    es.onerror = () => {
      connections.forEach((p) => {
        p.postMessage({ type: 'sse-error' });
      });
    };
  }
  
  connections.set(tabId, port);
  
  port.onmessage = (e) => {
    // 处理来自 Tab 的消息
  };
  
  port.start();
  
  // Tab 关闭时清理
  port.addEventListener('close', () => {
    connections.delete(tabId);
  });
};
```

**2. 突破仅支持 GET 请求的限制：**

```javascript
// 方案 1：通过 URL 参数传递认证 Token
const es = new EventSource(`/api/events?token=${encodeURIComponent(getToken())}`);

// 方案 2：先 POST 请求获取连接凭证，再建立 SSE
async function connectSSEWithAuth() {
  // 1. 先通过 POST 获取一次性连接 Token
  const response = await fetch('/api/events/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + getToken()
    },
    body: JSON.stringify({ channels: ['chat', 'notification'] })
  });
  
  const { connectionToken } = await response.json();
  
  // 2. 使用 Token 建立 SSE 连接
  const es = new EventSource(`/api/events?connection=${connectionToken}`);
  
  // 服务端验证 Token 后建立连接
  return es;
}

// 方案 3：使用 Fetch + ReadableStream 替代 EventSource（完全控制）
async function fetchSSE(url, options = {}) {
  const response = await fetch(url, {
    method: 'POST',  // 可以使用 POST
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + getToken(),
      ...options.headers
    },
    body: JSON.stringify(options.body),
    signal: options.signal
  });
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  
  const eventSource = {
    listeners: {},
    close() {
      reader.cancel();
      options.signal?.abort?.();
    }
  };
  
  async function readLoop() {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      buffer += decoder.decode(value, { stream: true });
      
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      
      let eventType = 'message';
      let eventData = '';
      let eventId = '';
      
      for (const line of lines) {
        if (line.startsWith('event: ')) {
          eventType = line.slice(7);
        } else if (line.startsWith('data: ')) {
          eventData += (eventData ? '\n' : '') + line.slice(6);
        } else if (line.startsWith('id: ')) {
          eventId = line.slice(4);
        } else if (line === '') {
          // 事件结束
          if (eventData && eventSource.listeners[eventType]) {
            eventSource.listeners[eventType].forEach(cb => cb({
              data: eventData,
              lastEventId: eventId
            }));
          }
          eventType = 'message';
          eventData = '';
          eventId = '';
        }
      }
    }
  }
  
  readLoop().catch(() => {});
  
  return eventSource;
}
```

**3. 突破单向通信限制（SSE + Fetch 混合）：**

```javascript
class HybridSSEClient {
  constructor() {
    this.es = null;
    this.baseURL = '/api';
  }
  
  // 接收服务器推送
  connect() {
    this.es = new EventSource(`${this.baseURL}/events`);
    this.es.onmessage = (e) => console.log('收到:', e.data);
  }
  
  // 向服务器发送数据（通过普通 HTTP 请求）
  async send(data) {
    const response = await fetch(`${this.baseURL}/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  }
}
```

**4. 突破文本限制（Base64 编码二进制）：**

```javascript
// 服务端：将二进制数据 Base64 编码后通过 SSE 发送
const fs = require('fs');

// 读取图片并 Base64 编码
const imageBuffer = fs.readFileSync('image.png');
const base64Image = imageBuffer.toString('base64');

res.write(`event: image\n`);
res.write(`data: ${JSON.stringify({
  filename: 'image.png',
  contentType: 'image/png',
  data: base64Image
})}\n\n`);

// 客户端：解码 Base64 还原二进制
es.addEventListener('image', (event) => {
  const { filename, contentType, data } = JSON.parse(event.data);
  
  // Base64 → Blob
  const byteCharacters = atob(data);
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  const blob = new Blob([byteArray], { type: contentType });
  
  // 显示或下载
  const url = URL.createObjectURL(blob);
  document.getElementById('image').src = url;
});
```

**评分标准：**
- 列举至少 5 个 SSE 局限性（3 分）
- 给出至少 3 个突破方案及代码（4 分）
- 实现 Fetch + ReadableStream 替代方案（3 分）

---

## 附录：考点速查表

| 序号 | 题目 | 核心考点 | 难度 |
|------|------|---------|------|
| 1 | WebSocket 基本概念与握手过程 | 协议原理、HTTP Upgrade、Sec-Key/Accept | 初级 |
| 2 | WebSocket 客户端 API 使用 | 事件处理、心跳、重连封装 | 初级 |
| 3 | WebSocket 心跳检测与断线重连 | Ping/Pong、指数退避、TCP 假死 | 中级 |
| 4 | WebSocket 数据帧格式与二进制传输 | 帧结构、Opcode、二进制数据 | 中级 |
| 5 | SSE 基本概念与使用 | EventSource API、服务端 text/event-stream | 初级 |
| 6 | SSE 事件类型与自定义事件 | event 字段、addEventListener | 中级 |
| 7 | SSE 断线重连与 Last-Event-ID | 自动重连、断点续传、retry 字段 | 中级 |
| 8 | WebSocket 与 SSE 全面对比 | 多维度对比、技术选型决策 | 中级 |
| 9 | WebSocket 与 HTTP 长轮询对比 | 短轮询、长轮询、WebSocket 对比 | 中级 |
| 10 | 实时通信技术适用场景选择 | 场景分析、决策框架、混合方案 | 中级 |
| 11 | WebSocket 服务端实现（Node.js） | ws 库、连接管理、房间机制、认证 | 高级 |
| 12 | SSE 服务端实现（Node.js） | 连接管理、事件订阅、定时发布 | 高级 |
| 13 | WebSocket 跨域与安全 | Origin 验证、CSWSH、DoS 防范 | 高级 |
| 14 | WebSocket 负载均衡与集群 | Sticky Session、Redis Pub/Sub | 高级 |
| 15 | SSE 局限性及突破方案 | HTTP/2、SharedWorker、Fetch 替代 | 高级 |

**按难度统计：** 初级 3 题 / 中级 7 题 / 高级 5 题

**使用建议：**
- **初级岗位**：重点掌握题目 1、2、5，理解两种技术的基本概念和用法
- **中级岗位**：重点掌握题目 3、4、6-10，熟悉对比分析、场景选型和实际应用
- **高级岗位**：重点掌握题目 11-15，能实现完整的服务端、处理安全问题和集群部署