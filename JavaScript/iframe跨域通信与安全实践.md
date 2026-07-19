# iframe 跨域通信与安全实践

> 本文档系统阐述 iframe 嵌入技术及父子页面间安全通信的完整方案，涵盖 postMessage API、CORS、代理服务器、document.domain 等多种跨域通信方法，深入分析各方法的适用场景、安全性、浏览器兼容性及最佳实践。

---

## 目录

- [一、引言](#一引言)
- [二、iframe 基础知识](#二iframe-基础知识)
- [三、同源场景下的 iframe 通信](#三同源场景下的-iframe-通信)
- [四、postMessage 跨域通信](#四postmessage-跨域通信)
- [五、document.domain 深度分析](#五documentdomain-深度分析)
- [六、CORS 与 iframe 的配合使用](#六cors-与-iframe-的配合使用)
- [七、代理服务器中转方案](#七代理服务器中转方案)
- [八、其他辅助通信方案](#八其他辅助通信方案)
- [九、安全性全面分析](#九安全性全面分析)
- [十、全局方案对比](#十全局方案对比)
- [十一、最佳实践与生产级方案](#十一最佳实践与生产级方案)
- [十二、常见问题解答](#十二常见问题解答)

---

## 一、引言

### 1.1 为什么需要 iframe 跨域通信？

iframe 是前端开发中常见的页面嵌入手段，典型应用场景包括：

| 场景 | 说明 |
|------|------|
| 第三方内容嵌入 | 嵌入支付页面、地图、视频播放器等 |
| 微前端架构 | qiankun、Micro-app 等框架底层依赖 iframe 或类似机制 |
| 跨域数据展示 | 在父页面中嵌入其他域的数据报表或仪表盘 |
| 安全沙箱隔离 | 隔离不可信内容，防止其影响主页面 |
| 多系统集成 | 在同一页面中整合多个独立子系统 |

### 1.2 核心挑战

```
┌─────────────────────────┐      ┌─────────────────────────┐
│  父页面                    │      │  iframe 子页面             │
│  https://parent.com      │      │  https://child.com       │
│                          │      │                          │
│  需要实现：                │      │  需要实现：                │
│  - 向 iframe 发送数据     │ ──── │  - 接收父页面数据          │
│  - 接收 iframe 的回传数据 │ <──── │  - 向父页面回传数据        │
│  - 控制 iframe 行为       │ ──── │  - 通知父页面状态变化      │
│  - 读取 iframe 内部状态   │ ──── │  - 请求父页面执行操作      │
└─────────────────────────┘      └─────────────────────────┘
```

**核心问题：** 浏览器同源策略阻止了父页面与跨域 iframe 之间的直接 DOM 访问和 JavaScript 调用。

---

## 二、iframe 基础知识

### 2.1 基本嵌入方式

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>iframe 嵌入示例</title>
  <style>
    .iframe-container {
      position: relative;
      width: 100%;
      height: 600px;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      overflow: hidden;
    }
    iframe {
      width: 100%;
      height: 100%;
      border: none;
    }
  </style>
</head>
<body>
  <!-- 基础嵌入 -->
  <iframe
    src="https://child.example.com/embed.html"
    width="800"
    height="600"
    title="嵌入内容"
    loading="lazy"
  ></iframe>

  <!-- 安全沙箱嵌入 -->
  <div class="iframe-container">
    <iframe
      id="secureFrame"
      src="https://child.example.com/embed.html"
      sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
      allow="camera; microphone; geolocation"
      referrerpolicy="strict-origin-when-cross-origin"
      loading="lazy"
      title="安全嵌入内容"
    ></iframe>
  </div>
</body>
</html>
```

### 2.2 iframe 核心属性详解

| 属性 | 说明 | 推荐值 |
|------|------|--------|
| `src` | 嵌入页面的 URL | 明确的 URL |
| `sandbox` | 安全沙箱限制 | 最小权限原则（见下文） |
| `allow` | 权限策略（Feature Policy） | 按需开启 |
| `referrerpolicy` | Referrer 发送策略 | `strict-origin-when-cross-origin` |
| `loading` | 延迟加载 | `lazy`（非首屏 iframe） |
| `title` | 无障碍标题 | 必填，描述 iframe 内容 |
| `name` | iframe 名称（用于 `window.open` 的 target） | 语义化命名 |

### 2.3 sandbox 安全沙箱配置

```html
<!-- ⚠️ 最严格的沙箱：禁止一切 -->
<iframe sandbox="" src="..."></iframe>

<!-- ✅ 推荐：最小权限原则 -->
<iframe
  sandbox="allow-scripts allow-same-origin"
  src="...">
</iframe>

<!-- 典型场景配置 -->
<!-- 支付页面：只需要表单和脚本 -->
<iframe sandbox="allow-scripts allow-forms allow-same-origin"></iframe>

<!-- 视频播放器：需要脚本和媒体播放 -->
<iframe sandbox="allow-scripts allow-same-origin"></iframe>

<!-- 安全文档预览：禁止脚本，仅展示内容 -->
<iframe sandbox="allow-same-origin"></iframe>
```

**sandbox 属性值说明：**

| 值 | 效果 |
|----|------|
| `""`（空字符串） | 启用所有限制（最严格） |
| `allow-scripts` | 允许执行 JavaScript |
| `allow-same-origin` | 允许同源访问（与 `allow-scripts` 同时启用时存在安全风险） |
| `allow-forms` | 允许表单提交 |
| `allow-popups` | 允许弹出窗口 |
| `allow-top-navigation` | 允许修改父页面 URL |
| `allow-modals` | 允许模态对话框 |
| `allow-downloads` | 允许下载 |
| `allow-pointer-lock` | 允许指针锁定 |
| `allow-popups-to-escape-sandbox` | 允许弹出窗口不受沙箱限制 |

> **⚠️ 安全警告：** `allow-scripts` 与 `allow-same-origin` 同时启用时，iframe 可以移除自身的 sandbox 属性，导致沙箱失效。应避免同时使用这两个值，除非完全信任 iframe 内容。

### 2.4 iframe 的 DOM 操作

```javascript
// ===== 父页面操作 iframe =====

// 获取 iframe 元素
const iframe = document.getElementById('myFrame');

// 获取 iframe 的 contentWindow（同源可用）
const iframeWindow = iframe.contentWindow;

// 获取 iframe 的 document（同源可用）
const iframeDocument = iframe.contentDocument ||
                       iframe.contentWindow.document;

// 动态创建 iframe
function createIframe(src, options = {}) {
  const iframe = document.createElement('iframe');

  // 设置属性
  iframe.src = src;
  iframe.width = options.width || '100%';
  iframe.height = options.height || '400';
  iframe.sandbox = options.sandbox || 'allow-scripts allow-same-origin';
  iframe.allow = options.allow || '';
  iframe.referrerPolicy = options.referrerPolicy || 'strict-origin-when-cross-origin';
  iframe.loading = options.loading || 'lazy';
  iframe.title = options.title || '嵌入内容';
  iframe.style.border = 'none';

  // 加载完成回调
  iframe.addEventListener('load', () => {
    console.log(`iframe 加载完成: ${src}`);
    if (options.onLoad) options.onLoad(iframe);
  });

  // 加载失败处理
  iframe.addEventListener('error', () => {
    console.error(`iframe 加载失败: ${src}`);
    if (options.onError) options.onError(iframe);
  });

  document.getElementById(options.container || 'app').appendChild(iframe);
  return iframe;
}

// 移除 iframe
function removeIframe(iframe) {
  // 清理事件监听，防止内存泄漏
  iframe.src = 'about:blank';
  iframe.remove();
}

// 检查 iframe 是否加载完成
function isIframeLoaded(iframe) {
  return iframe.contentWindow &&
         iframe.contentDocument &&
         iframe.contentDocument.readyState === 'complete';
}
```

---

## 三、同源场景下的 iframe 通信

同源场景下，父子页面可以直接相互访问 DOM 和 JavaScript 对象，无需任何特殊处理。

### 3.1 父页面访问 iframe

```javascript
// 父页面代码
const iframe = document.getElementById('myFrame');

iframe.addEventListener('load', () => {
  // 直接访问 iframe 的 DOM
  const title = iframe.contentDocument.querySelector('h1').textContent;

  // 直接调用 iframe 中的函数
  iframe.contentWindow.childFunction('Hello from parent');

  // 直接读取 iframe 中的全局变量
  const data = iframe.contentWindow.sharedData;

  // 直接修改 iframe 的样式
  iframe.contentDocument.body.style.background = '#f5f5f5';
});
```

### 3.2 iframe 访问父页面

```javascript
// iframe 内部代码
// 直接访问父页面的 DOM
const parentTitle = window.parent.document.querySelector('h1').textContent;

// 直接调用父页面中的函数
window.parent.parentFunction('Hello from iframe');

// 直接读取父页面的全局变量
const parentData = window.parent.sharedData;

// 访问顶层窗口（处理多层嵌套）
const topData = window.top.sharedData;
```

### 3.3 同源通信的局限性

```
同源场景下可以直接通信，但存在以下问题：

❌ 紧密耦合：iframe 和父页面强依赖对方的 DOM 结构和方法名
❌ 安全风险：iframe 拥有完全访问父页面的能力
❌ 维护困难：任何一方的 DOM 结构调整都可能导致另一方失效
❌ 无法跨域：一旦域名不同，所有直接访问方式全部失效
```

---

## 四、postMessage 跨域通信

### 4.1 技术原理

`postMessage` 是 HTML5 提供的跨文档通信 API，允许不同源（协议、域名、端口不同）的窗口之间安全地传递消息。它是现代 iframe 跨域通信的**首选方案**。

```
┌──────────────────────────────────────────────────────────────────┐
│                      postMessage 通信流程                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  父页面（https://parent.com）          iframe（https://child.com）  │
│  ┌─────────────────────────┐          ┌─────────────────────────┐ │
│  │ targetWindow.postMessage│          │ window.addEventListener │ │
│  │   (data, targetOrigin)  │─────────>│   ('message', handler)  │ │
│  └─────────────────────────┘          └─────────────────────────┘ │
│                                                                    │
│  ┌─────────────────────────┐          ┌─────────────────────────┐ │
│  │ window.addEventListener │          │ parent.postMessage      │ │
│  │   ('message', handler)  │<─────────│   (data, targetOrigin)  │ │
│  └─────────────────────────┘          └─────────────────────────┘ │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

### 4.2 基础实现

**父页面代码：**

```javascript
// ===== 父页面：发送消息给 iframe 并接收回复 =====

const iframe = document.getElementById('myFrame');

// 1. 监听来自 iframe 的消息
window.addEventListener('message', (event) => {
  // 安全校验：验证消息来源
  if (event.origin !== 'https://child.example.com') {
    console.warn(`拒绝来自未授权源的消息: ${event.origin}`);
    return;
  }

  console.log('父页面收到:', event.data);

  switch (event.data.type) {
    case 'ready':
      console.log('iframe 已就绪');
      // iframe 就绪后发送初始化数据
      sendToIframe({ type: 'init', payload: { userId: 123 } });
      break;

    case 'response':
      console.log('收到 iframe 回复:', event.data.payload);
      break;

    case 'error':
      console.error('iframe 报告错误:', event.data.payload);
      break;
  }
});

// 2. 发送消息给 iframe
function sendToIframe(data) {
  iframe.contentWindow.postMessage(
    data,
    'https://child.example.com'  // 精确指定目标源
  );
}

// 3. iframe 加载完成后发送消息
iframe.addEventListener('load', () => {
  sendToIframe({ type: 'parentReady', payload: { timestamp: Date.now() } });
});
```

**iframe 子页面代码：**

```javascript
// ===== iframe 内部：接收父页面消息并回复 =====

// 1. 监听来自父页面的消息
window.addEventListener('message', (event) => {
  // 安全校验：验证消息来源
  if (event.origin !== 'https://parent.example.com') {
    console.warn(`拒绝来自未授权源的消息: ${event.origin}`);
    return;
  }

  console.log('iframe 收到:', event.data);

  switch (event.data.type) {
    case 'parentReady':
      console.log('父页面已就绪');
      break;

    case 'init':
      // 处理初始化数据
      initializeApp(event.data.payload);
      break;

    case 'action':
      // 执行具体操作
      handleAction(event.data.payload);
      // 回复父页面
      window.parent.postMessage(
        { type: 'response', payload: { success: true, result: 'done' } },
        'https://parent.example.com'
      );
      break;
  }
});

// 2. 通知父页面 iframe 已就绪
window.addEventListener('DOMContentLoaded', () => {
  window.parent.postMessage(
    { type: 'ready', payload: { timestamp: Date.now() } },
    'https://parent.example.com'
  );
});

// 3. 发送消息给父页面
function sendToParent(data) {
  window.parent.postMessage(
    data,
    'https://parent.example.com'
  );
}
```

### 4.3 生产级通信封装

下面是一个完整的、生产环境可用的 iframe 双向通信封装：

```javascript
/**
 * iframe 跨域通信管理器
 * 支持：请求-响应模式、事件订阅模式、超时处理、自动重连
 */
class IframeBridge {
  /**
   * @param {object} options
   * @param {HTMLIFrameElement} [options.iframe] - 父页面传入 iframe 元素
   * @param {string} options.targetOrigin - 对端页面的源
   * @param {string} [options.selfOrigin] - 自身源（验证用）
   * @param {number} [options.timeout] - 请求超时时间（毫秒）
   */
  constructor(options) {
    this.targetWindow = options.iframe
      ? options.iframe.contentWindow
      : window.parent;
    this.targetOrigin = options.targetOrigin;
    this.selfOrigin = options.selfOrigin || window.location.origin;
    this.timeout = options.timeout || 10000;

    this._listeners = new Map();
    this._pendingRequests = new Map();
    this._requestId = 0;
    this._ready = false;
    this._readyPromise = null;

    this._handleMessage = this._handleMessage.bind(this);
    window.addEventListener('message', this._handleMessage);
  }

  // ===== 事件监听 =====

  /**
   * 监听指定类型的事件
   * @param {string} type - 事件类型
   * @param {Function} handler - 处理函数
   */
  on(type, handler) {
    if (!this._listeners.has(type)) {
      this._listeners.set(type, new Set());
    }
    this._listeners.get(type).add(handler);
  }

  /**
   * 取消监听
   */
  off(type, handler) {
    const handlers = this._listeners.get(type);
    if (handlers) {
      handlers.delete(handler);
    }
  }

  /**
   * 监听一次性事件
   */
  once(type, handler) {
    const wrapper = (...args) => {
      handler(...args);
      this.off(type, wrapper);
    };
    this.on(type, wrapper);
  }

  // ===== 消息发送 =====

  /**
   * 发送事件（单向，不等待回复）
   * @returns {number} 消息 ID
   */
  emit(type, payload) {
    const id = this._nextId();
    this._send({ type, payload, id, direction: 'event' });
    return id;
  }

  /**
   * 发送请求并等待响应（类似 RPC）
   * @returns {Promise<any>}
   */
  request(type, payload, timeout = this.timeout) {
    return new Promise((resolve, reject) => {
      const id = this._nextId();
      const timer = setTimeout(() => {
        this._pendingRequests.delete(id);
        reject(new Error(`请求 "${type}" 超时 (${timeout}ms)`));
      }, timeout);

      this._pendingRequests.set(id, { resolve, reject, timer });
      this._send({ type, payload, id, direction: 'request' });
    });
  }

  /**
   * 等待对端就绪
   * @returns {Promise<void>}
   */
  waitReady(timeout = 15000) {
    if (this._ready) return Promise.resolve();
    if (this._readyPromise) return this._readyPromise;

    this._readyPromise = new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this._readyPromise = null;
        reject(new Error('等待对端就绪超时'));
      }, timeout);

      this.once('ready', () => {
        clearTimeout(timer);
        this._ready = true;
        this._readyPromise = null;
        resolve();
      });
    });

    return this._readyPromise;
  }

  // ===== 内部方法 =====

  _send(message) {
    this.targetWindow.postMessage(message, this.targetOrigin);
  }

  _nextId() {
    return `${Date.now().toString(36)}_${(++this._requestId).toString(36)}`;
  }

  _handleMessage(event) {
    // 精确的源验证
    if (event.origin !== this.targetOrigin) {
      return;
    }

    const { type, payload, id, direction } = event.data || {};

    if (!type) return;

    // 处理响应（匹配之前的请求）
    if (id && this._pendingRequests.has(id)) {
      const { resolve, reject, timer } = this._pendingRequests.get(id);
      clearTimeout(timer);
      this._pendingRequests.delete(id);

      if (event.data.error) {
        reject(new Error(event.data.error));
      } else {
        resolve(payload);
      }
      return;
    }

    // 处理请求：执行对应处理器并回复
    if (direction === 'request') {
      const handlers = this._listeners.get(type);
      if (handlers && handlers.size > 0) {
        const handler = Array.from(handlers)[0]; // 取第一个处理器
        try {
          const result = handler(payload);
          Promise.resolve(result).then((resolved) => {
            this._send({ type: `${type}:response`, payload: resolved, id });
          }).catch((err) => {
            this._send({ type: `${type}:response`, payload: null, id, error: err.message });
          });
        } catch (err) {
          this._send({ type: `${type}:response`, payload: null, id, error: err.message });
        }
      }
      return;
    }

    // 处理事件：触发所有监听器
    const handlers = this._listeners.get(type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(payload);
        } catch (err) {
          console.error(`事件处理器错误 [${type}]:`, err);
        }
      });
    }
  }

  // ===== 销毁 =====

  destroy() {
    window.removeEventListener('message', this._handleMessage);

    this._pendingRequests.forEach(({ timer, reject }) => {
      clearTimeout(timer);
      reject(new Error('Bridge 已销毁'));
    });
    this._pendingRequests.clear();
    this._listeners.clear();
    this._ready = false;
    this._readyPromise = null;
  }
}
```

**使用示例：**

```javascript
// ===== 父页面使用 =====
const iframe = document.getElementById('myFrame');
const bridge = new IframeBridge({
  iframe: iframe,
  targetOrigin: 'https://child.example.com',
  timeout: 8000
});

// 监听子页面事件
bridge.on('childEvent', (data) => {
  console.log('子页面事件:', data);
});

// 等待子页面就绪
bridge.waitReady().then(() => {
  // 发送请求并等待响应
  return bridge.request('getUserInfo', { userId: 123 });
}).then((userInfo) => {
  console.log('获取到用户信息:', userInfo);
}).catch((err) => {
  console.error('通信失败:', err);
});

// ===== iframe 子页面使用 =====
const bridge = new IframeBridge({
  targetOrigin: 'https://parent.example.com'
});

// 处理父页面的请求
bridge.on('getUserInfo', (params) => {
  const userInfo = fetchUserInfo(params.userId);
  return userInfo; // 自动作为响应返回
});

// 通知父页面就绪
bridge.emit('ready', { timestamp: Date.now() });

// 发送事件给父页面
bridge.emit('childEvent', { action: 'click', target: 'button' });
```

### 4.4 postMessage 安全性

| 安全措施 | 实现方式 | 风险等级 |
|---------|---------|---------|
| 源验证 | 始终检查 `event.origin` | 必须 |
| 目标指定 | `postMessage` 第二个参数精确指定，不用 `*` | 必须 |
| 数据验证 | 验证消息结构和数据类型 | 强烈建议 |
| 频率限制 | 防止消息洪水攻击 | 建议 |
| 加密传输 | 敏感数据 HTTPS + 加密 | 按需 |

```javascript
// 完整的安全验证示例
window.addEventListener('message', (event) => {
  // 1. 源验证
  const ALLOWED_ORIGINS = ['https://trusted.com', 'https://admin.trusted.com'];
  if (!ALLOWED_ORIGINS.includes(event.origin)) {
    console.warn(`拒绝消息: ${event.origin}`);
    return;
  }

  // 2. 数据结构验证
  const { data } = event;
  if (!data || typeof data !== 'object') {
    console.warn('无效的消息格式');
    return;
  }

  // 3. 消息类型验证（白名单）
  const ALLOWED_TYPES = ['init', 'action', 'navigate', 'resize'];
  if (!ALLOWED_TYPES.includes(data.type)) {
    console.warn(`未授权的消息类型: ${data.type}`);
    return;
  }

  // 4. Payload 验证（根据类型做 Schema 校验）
  if (!validatePayload(data.type, data.payload)) {
    console.warn('无效的消息载荷');
    return;
  }

  // 通过所有验证，处理消息
  handleMessage(data);
});

function validatePayload(type, payload) {
  const schemas = {
    init: (p) => p && typeof p.userId === 'number',
    action: (p) => p && typeof p.action === 'string',
    navigate: (p) => p && typeof p.url === 'string' && p.url.startsWith('/'),
    resize: (p) => p && typeof p.height === 'number' && p.height > 0
  };
  const validator = schemas[type];
  return validator ? validator(payload) : false;
}
```

### 4.5 postMessage 浏览器兼容性

| 浏览器 | 支持版本 | 备注 |
|--------|---------|------|
| Chrome | 4+ | 完整支持 |
| Firefox | 3.5+ | 完整支持 |
| Safari | 4+ | 完整支持 |
| Edge | 所有版本 | 完整支持 |
| Internet Explorer | IE8+ | IE8/IE9 仅支持字符串，且仅支持 iframe 通信 |

**IE8/IE9 兼容代码：**

```javascript
/**
 * 兼容 IE8/IE9 的 postMessage 封装
 */
function postMessageCompat(targetWindow, data, targetOrigin) {
  // IE8/IE9 仅支持字符串
  if (typeof data === 'object') {
    data = JSON.stringify(data);
  }
  targetWindow.postMessage(data, targetOrigin);
}

window.addEventListener('message', (event) => {
  let data = event.data;
  // IE8/IE9 返回字符串，现代浏览器返回对象
  if (typeof data === 'string') {
    try {
      data = JSON.parse(data);
    } catch (e) {
      // 保持字符串格式
    }
  }
  // 处理 data...
});
```

---

## 五、document.domain 深度分析

### 5.1 技术原理

`document.domain` 通过将子域页面的域名降级为主域，使同主域不同子域的页面之间可以互相访问 DOM。

```
场景：a.example.com 和 b.example.com 需要通信
原理：双方都设置 document.domain = 'example.com'
结果：浏览器认为它们同源，允许互相访问
```

### 5.2 基础实现

```javascript
// 页面 A：http://a.example.com/pageA.html
document.domain = 'example.com';

// 页面 B：http://b.example.com/pageB.html
document.domain = 'example.com';

// 设置后，A 可以访问 B 的 DOM（B 在 iframe 中）
const iframe = document.getElementById('frameB');
iframe.contentDocument.querySelector('h1').textContent; // 可以访问
```

### 5.3 现代浏览器支持现状

| 浏览器 | 支持状态 | 说明 |
|--------|---------|------|
| Chrome | ⚠️ 已弃用 | Chrome 115+ 通过 Origin-keyed Agent Clusters 默认禁用 |
| Firefox | ⚠️ 已弃用 | 默认禁用，需手动修改配置才能启用 |
| Safari | ⚠️ 已弃用 | 16.4+ 已移除支持 |
| Edge | ⚠️ 已弃用 | 与 Chrome 一致，115+ 已弃用 |

**结论：`document.domain` 在现代浏览器中已不可靠，不应在新项目中使用。**

### 5.4 已知的安全风险

```
风险 1：子域间隔离被打破
─────────────────────────────────────
设置 document.domain = 'example.com' 后，
a.example.com、b.example.com、c.example.com
之间可以互相访问对方的 DOM 和 JavaScript 上下文。
恶意子域（如 evil.example.com）可以窃取其他子域的数据。

风险 2：端口号绕过
─────────────────────────────────────
两个页面设置相同的 document.domain 后，
不同端口号之间的隔离也被打破了。
a.example.com:3000 可以访问 a.example.com:4000 的数据。

风险 3：iframe 沙箱绕过
─────────────────────────────────────
如果 iframe 设置 document.domain 匹配父页面，
即使有 sandbox 属性，某些限制也可能被绕过。

风险 4：XSS 攻击面扩大
─────────────────────────────────────
一个子域的 XSS 漏洞可能影响所有同主域的子域。
```

### 5.5 迁移方案

如果项目中正在使用 `document.domain`，应迁移到 `postMessage`：

```javascript
// ===== 旧方案（使用 document.domain）=====
// 页面 A（a.example.com）
document.domain = 'example.com';
const iframe = document.getElementById('frameB');
iframe.contentWindow.doSomething(data);

// ===== 新方案（使用 postMessage）=====
// 页面 A（a.example.com）
const iframe = document.getElementById('frameB');
iframe.contentWindow.postMessage(
  { type: 'doSomething', payload: data },
  'https://b.example.com'
);

// 页面 B（b.example.com）
window.addEventListener('message', (event) => {
  if (event.origin !== 'https://a.example.com') return;
  if (event.data.type === 'doSomething') {
    handleAction(event.data.payload);
  }
});
```

---

## 六、CORS 与 iframe 的配合使用

### 6.1 应用场景

CORS 通常用于解决 Ajax 跨域请求，但在 iframe 场景中，CORS 主要负责解决 **iframe 内部发起的跨域请求**问题。

```
┌──────────────────────────────────────────────────────────┐
│  父页面（https://parent.com）                             │
│  ┌────────────────────────────────────────────────────┐  │
│  │  iframe（https://child.com）                        │  │
│  │                                                    │  │
│  │  fetch('https://api.example.com/data')  ← 跨域请求  │  │
│  │                                                    │  │
│  │  需要 API 服务端配置 CORS 响应头                      │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### 6.2 实现方案

**iframe 内部代码：**

```javascript
// iframe 内部发起跨域 API 请求
async function fetchData() {
  try {
    const response = await fetch('https://api.example.com/data', {
      method: 'GET',
      credentials: 'include', // 携带 Cookie
      headers: {
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    // 将获取的数据通过 postMessage 传给父页面
    window.parent.postMessage(
      { type: 'apiData', payload: data },
      'https://parent.com'
    );
  } catch (error) {
    window.parent.postMessage(
      { type: 'apiError', payload: { message: error.message } },
      'https://parent.com'
    );
  }
}
```

**API 服务端 CORS 配置：**

```javascript
// Node.js Express
app.use((req, res, next) => {
  const allowedOrigins = ['https://child.com', 'https://parent.com'];
  const origin = req.headers.origin;

  if (allowedOrigins.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  }
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.sendStatus(204);
  }
  next();
});
```

### 6.3 CORS + postMessage 组合方案

```
场景：父页面需要在 iframe 中展示数据，但数据来自第三方 API

┌────────────┐    postMessage     ┌────────────┐    CORS     ┌──────────┐
│  父页面     │<──────────────────>│  iframe    │<───────────>│  API 服务 │
│  parent.com │   (跨域通信)       │  child.com │  (跨域请求)  │ api.com  │
└────────────┘                    └────────────┘             └──────────┘

优点：
- 父页面和 iframe 通过 postMessage 安全通信
- iframe 独立处理 API 请求，通过 CORS 解决跨域
- 职责分离清晰，各自处理自己的跨域问题
```

---

## 七、代理服务器中转方案

### 7.1 技术原理

通过代理服务器将跨域请求转为同源请求，在 iframe 场景中主要有两种应用方式：

**方式一：iframe 内容代理**

```
浏览器请求同源的代理 → 代理服务器转发到真实服务器 → 返回内容
```

**方式二：API 请求代理（iframe 内部使用）**

```
iframe 内 Ajax 请求同源代理 → 代理转发到跨域 API
```

### 7.2 Nginx 反向代理实现

```nginx
server {
    listen 80;
    server_name www.parent.com;

    # 父页面静态资源
    location / {
        root /var/www/parent;
        try_files $uri $uri/ /index.html;
    }

    # 代理 iframe 内容（同源化 iframe）
    location /embed/child/ {
        proxy_pass https://child.example.com/;
        proxy_set_header Host child.example.com;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # 处理 iframe 内的相对路径
        sub_filter 'href="/' 'href="/embed/child/';
        sub_filter 'src="/' 'src="/embed/child/';
        sub_filter 'action="/' 'action="/embed/child/';
        sub_filter_once off;
        sub_filter_types text/html application/javascript;
    }

    # 代理 iframe 内部的 API 请求
    location /embed/api/ {
        proxy_pass https://api.example.com/;
        proxy_set_header Host api.example.com;
    }
}
```

**使用方式：**

```html
<!-- 父页面中嵌入同源化的 iframe -->
<iframe src="/embed/child/app.html"></iframe>

<!-- iframe 内部发起的 API 请求也变为同源 -->
<script>
  // 原来：fetch('https://api.example.com/data')
  // 现在：fetch('/embed/api/data')
  fetch('/embed/api/data')
    .then(res => res.json())
    .then(data => console.log(data));
</script>
```

### 7.3 Node.js 代理中间件

```javascript
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();

// 代理 iframe 内容
app.use('/embed/child', createProxyMiddleware({
  target: 'https://child.example.com',
  changeOrigin: true,
  pathRewrite: { '^/embed/child': '' },
  onProxyRes: (proxyRes, req, res) => {
    // 修改响应头中的 CSP 以允许在 iframe 中展示
    proxyRes.headers['content-security-policy'] =
      "frame-ancestors 'self' https://parent.com";
    proxyRes.headers['x-frame-options'] = 'ALLOW-FROM https://parent.com';
  }
}));

// 代理 API 请求
app.use('/embed/api', createProxyMiddleware({
  target: 'https://api.example.com',
  changeOrigin: true,
  pathRewrite: { '^/embed/api': '' }
}));

app.listen(3000);
```

### 7.4 代理方案的优缺点

| 维度 | 评价 |
|------|------|
| 安全性 | ✅ 高 —— 请求在服务端转发，客户端无感知 |
| 复杂度 | ⚠️ 中 —— 需要额外的服务端配置和维护 |
| 性能 | ⚠️ 中 —— 多一层转发，有轻微延迟 |
| 适用性 | ✅ 广泛 —— 适用于所有跨域场景 |

---

## 八、其他辅助通信方案

### 8.1 URL 参数传递

```javascript
// 父页面通过 URL 参数向 iframe 传递初始数据
const params = new URLSearchParams({
  userId: '123',
  theme: 'dark',
  lang: 'zh-CN'
});
const iframe = document.createElement('iframe');
iframe.src = `https://child.example.com/?${params.toString()}`;
```

```javascript
// iframe 内部读取 URL 参数
const params = new URLSearchParams(window.location.search);
const userId = params.get('userId');
const theme = params.get('theme');
```

**局限性：** 仅适合初始加载时传递少量数据，无法动态通信。

### 8.2 服务端中转（Cookie/Storage 同步）

```javascript
// 父页面：将数据写入服务端
await fetch('/api/session', {
  method: 'POST',
  body: JSON.stringify({ key: 'sharedData', value: data }),
  headers: { 'Content-Type': 'application/json' }
});

// iframe 页面：从服务端读取数据
const response = await fetch('/api/session?key=sharedData');
const data = await response.json();
```

**局限性：** 需要服务端支持，有网络延迟，不适合高频数据交换。

### 8.3 BroadcastChannel API（同源场景）

```javascript
// 仅适用于同源页面之间的通信
const channel = new BroadcastChannel('app_channel');

// 页面 A 发送消息
channel.postMessage({ type: 'update', payload: data });

// 页面 B 接收消息
channel.addEventListener('message', (event) => {
  console.log('收到:', event.data);
});
```

**局限性：** 仅同源可用，不适用于跨域 iframe 通信。

---

## 九、安全性全面分析

### 9.1 各方案安全风险矩阵

| 方案 | XSS 风险 | 数据泄露 | 中间人攻击 | 权限提升 | 总体安全评级 |
|------|---------|---------|-----------|---------|-------------|
| postMessage | ⚠️ 中 | ⚠️ 中 | ⚠️ 中 | ⚠️ 中 | ⭐⭐⭐⭐ |
| document.domain | ❌ 高 | ❌ 高 | ❌ 高 | ❌ 高 | ⭐ |
| CORS | ⚠️ 低 | ⚠️ 低 | ⚠️ 低 | ✅ 无 | ⭐⭐⭐⭐⭐ |
| 代理服务器 | ✅ 无 | ✅ 无 | ⚠️ 低 | ✅ 无 | ⭐⭐⭐⭐⭐ |
| URL 参数 | ❌ 高 | ❌ 高 | ❌ 高 | ✅ 无 | ⭐⭐ |

### 9.2 安全防护清单

```javascript
// ===== iframe 安全防护清单 =====

// 1. 使用 sandbox 限制 iframe 权限
<iframe sandbox="allow-scripts allow-forms" src="..."></iframe>

// 2. 使用 CSP 响应头限制 iframe 行为
// 服务端设置：
// Content-Security-Policy: frame-ancestors 'self' https://trusted-parent.com
// 或 meta 标签：
<meta http-equiv="Content-Security-Policy"
      content="frame-ancestors 'self' https://trusted-parent.com">

// 3. 防止点击劫持（Clickjacking）
// 服务端设置：
// X-Frame-Options: DENY                    // 完全禁止被嵌入
// X-Frame-Options: SAMEORIGIN              // 仅允许同源嵌入
// X-Frame-Options: ALLOW-FROM https://parent.com  // 允许指定源

// 4. 验证 postMessage 来源
window.addEventListener('message', (event) => {
  if (event.origin !== 'https://expected-origin.com') {
    return; // 拒绝
  }
  // 处理消息
});

// 5. 结构化数据验证
function validateMessage(data) {
  const schema = {
    type: 'string',
    payload: 'object',
    id: 'string'
  };
  for (const [key, expectedType] of Object.entries(schema)) {
    if (typeof data[key] !== expectedType) {
      return false;
    }
  }
  return true;
}
```

### 9.3 常见安全攻击与防御

**攻击类型 1：恶意 postMessage 注入**

```javascript
// 攻击者页面
targetWindow.postMessage(
  { type: 'malicious', payload: '<script>stealCookies()</script>' },
  '*'  // 不指定目标源
);

// ✅ 防御：精确验证 origin + 数据清洗
window.addEventListener('message', (event) => {
  if (event.origin !== 'https://trusted.com') return;
  if (typeof event.data.payload !== 'string') return;
  const sanitized = DOMPurify.sanitize(event.data.payload);
  // 处理 sanitized
});
```

**攻击类型 2：iframe 沙箱逃逸**

```javascript
// ✅ 防御：最小权限原则配置 sandbox
// 不要同时使用 allow-scripts 和 allow-same-origin
<iframe sandbox="allow-scripts allow-forms"></iframe>

// 替代方案：使用不同源提供 iframe 内容
// 让 iframe 内容来自独立子域，避免使用 allow-same-origin
```

---

## 十、全局方案对比

### 10.1 方案对比总表

| 方案 | 适用场景 | 通信方向 | 实时性 | 安全性 | 复杂度 | 兼容性 | 推荐度 |
|------|---------|---------|--------|--------|--------|--------|--------|
| **postMessage** | iframe 跨域通信 | 双向 | 实时 | ⭐⭐⭐⭐ | 中 | IE8+ | ⭐⭐⭐⭐⭐ |
| **CORS** | iframe 内 Ajax 跨域 | 单向 | 实时 | ⭐⭐⭐⭐⭐ | 中 | IE10+ | ⭐⭐⭐⭐⭐ |
| **代理服务器** | 同源化 iframe | 双向 | 实时 | ⭐⭐⭐⭐⭐ | 高 | 全部 | ⭐⭐⭐⭐⭐ |
| **document.domain** | 同主域子域 | 双向 | 实时 | ⭐ | 低 | 已弃用 | ⭐ |
| **URL 参数** | 初始数据传递 | 单向 | 非实时 | ⭐⭐ | 低 | 全部 | ⭐⭐ |
| **服务端中转** | 低频数据同步 | 双向 | 非实时 | ⭐⭐⭐⭐ | 中 | 全部 | ⭐⭐⭐ |

### 10.2 方案选择决策树

```
需要 iframe 跨域通信？
│
├── iframe 内容可控（可修改代码）？
│   ├── 是 → postMessage（首选方案）
│   │   └── iframe 内还需调用跨域 API？
│   │       ├── 是 → postMessage + CORS 组合
│   │       └── 否 → 纯 postMessage
│   │
│   └── 否 → 代理服务器（同源化 iframe）
│
├── 仅需传递初始参数？
│   └── 是 → URL 参数传递
│
├── 同主域子域间通信（旧项目）？
│   └── 迁移到 postMessage（不推荐 document.domain）
│
└── 需要最高安全保证？
    └── 代理服务器 + CSP + iframe sandbox
```

---

## 十一、最佳实践与生产级方案

### 11.1 推荐方案：postMessage + 类型安全协议

**定义通信协议：**

```typescript
// ===== 通信协议定义 =====

// 父页面 → iframe 的消息类型
type ParentMessage =
  | { type: 'init'; payload: { userId: number; theme: string; locale: string } }
  | { type: 'navigate'; payload: { path: string } }
  | { type: 'resize'; payload: { width: number; height: number } }
  | { type: 'action'; payload: { action: string; params?: Record<string, unknown> } };

// iframe → 父页面的消息类型
type ChildMessage =
  | { type: 'ready'; payload: { timestamp: number } }
  | { type: 'resize'; payload: { width: number; height: number } }
  | { type: 'navigate'; payload: { path: string } }
  | { type: 'event'; payload: { name: string; data: unknown } }
  | { type: 'error'; payload: { code: string; message: string } };
```

### 11.2 生产级完整示例

**父页面：**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>父页面</title>
  <style>
    .app { display: flex; flex-direction: column; height: 100vh; }
    .toolbar { padding: 16px; background: #f5f5f5; border-bottom: 1px solid #e0e0e0; }
    .toolbar button { margin-right: 8px; padding: 8px 16px; }
    .iframe-wrapper { flex: 1; position: relative; }
    iframe { width: 100%; height: 100%; border: none; }
    .status { padding: 8px 16px; background: #fafafa; font-size: 12px; color: #666; }
  </style>
</head>
<body>
  <div class="app">
    <div class="toolbar">
      <button onclick="navigateChild('/dashboard')">仪表盘</button>
      <button onclick="navigateChild('/settings')">设置</button>
      <button onclick="sendAction('refresh')">刷新</button>
      <button onclick="sendAction('export')">导出</button>
    </div>
    <div class="iframe-wrapper">
      <iframe
        id="appFrame"
        src="https://child.example.com/embed"
        sandbox="allow-scripts allow-forms allow-popups"
        title="子应用"
      ></iframe>
    </div>
    <div class="status" id="status">
      状态：等待加载...
    </div>
  </div>

  <script src="./IframeBridge.js"></script>
  <script>
    const statusEl = document.getElementById('status');
    const iframe = document.getElementById('appFrame');

    // 创建通信桥接
    const bridge = new IframeBridge({
      iframe: iframe,
      targetOrigin: 'https://child.example.com',
      timeout: 10000
    });

    // 监听子页面事件
    bridge.on('ready', () => {
      statusEl.textContent = '状态：已连接';
      // 初始化子页面
      bridge.emit('init', {
        userId: 123,
        theme: 'light',
        locale: 'zh-CN'
      });
    });

    bridge.on('resize', ({ width, height }) => {
      iframe.style.height = height + 'px';
      statusEl.textContent = `状态：已连接（子页面尺寸: ${width}x${height}）`;
    });

    bridge.on('navigate', ({ path }) => {
      statusEl.textContent = `状态：子页面导航到 ${path}`;
    });

    bridge.on('error', ({ code, message }) => {
      statusEl.textContent = `状态：错误 - ${code}: ${message}`;
    });

    // 父页面操作
    function navigateChild(path) {
      bridge.emit('navigate', { path });
    }

    function sendAction(action) {
      bridge.emit('action', { action });
    }

    // 等待连接就绪
    bridge.waitReady().then(() => {
      console.log('与子页面通信已就绪');
    }).catch(() => {
      statusEl.textContent = '状态：连接超时';
    });
  </script>
</body>
</html>
```

**iframe 子页面：**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>子页面</title>
  <style>
    body { font-family: sans-serif; margin: 0; padding: 20px; }
    .page { padding: 20px; }
  </style>
</head>
<body>
  <div class="page" id="content">
    <h2>子页面内容</h2>
    <p id="info">等待初始化...</p>
  </div>

  <script src="./IframeBridge.js"></script>
  <script>
    const bridge = new IframeBridge({
      targetOrigin: 'https://parent.example.com'
    });

    // 处理父页面消息
    bridge.on('init', (config) => {
      document.getElementById('info').textContent =
        `用户ID: ${config.userId}, 主题: ${config.theme}`;
      document.body.className = `theme-${config.theme}`;
    });

    bridge.on('navigate', ({ path }) => {
      document.getElementById('content').innerHTML =
        `<h2>导航到: ${path}</h2>`;
      // 通知父页面导航完成
      bridge.emit('navigate', { path });
    });

    bridge.on('action', ({ action }) => {
      switch (action) {
        case 'refresh':
          location.reload();
          break;
        case 'export':
          handleExport();
          break;
      }
    });

    // 通知父页面就绪
    bridge.emit('ready', { timestamp: Date.now() });

    // 动态调整 iframe 高度
    function updateHeight() {
      const height = document.body.scrollHeight;
      bridge.emit('resize', { width: window.innerWidth, height });
    }

    const observer = new ResizeObserver(updateHeight);
    observer.observe(document.body);

    // 点击事件上报
    document.addEventListener('click', (e) => {
      bridge.emit('event', {
        name: 'click',
        data: { target: e.target.tagName, text: e.target.textContent?.slice(0, 50) }
      });
    });

    async function handleExport() {
      try {
        // 子页面内发起跨域 API 请求（需要 CORS 支持）
        const response = await fetch('https://api.example.com/export', {
          method: 'POST',
          credentials: 'include'
        });
        const data = await response.json();
        bridge.emit('event', { name: 'exportDone', data });
      } catch (err) {
        bridge.emit('error', { code: 'EXPORT_FAIL', message: err.message });
      }
    }
  </script>
</body>
</html>
```

### 11.3 安全最佳实践汇总

```
1. 始终验证 postMessage 的 event.origin
2. postMessage 第二个参数精确指定目标源，不使用 '*'
3. 验证消息结构和数据类型
4. iframe 使用 sandbox 最小权限原则
5. 服务端设置 X-Frame-Options 或 CSP frame-ancestors
6. 敏感数据传输使用 HTTPS
7. 避免同时使用 allow-scripts 和 allow-same-origin
8. 不使用 document.domain（现代浏览器已弃用）
9. 定期审计 iframe 的权限配置
10. 对来自 iframe 的数据进行输入清洗
```

---

## 十二、常见问题解答

### Q1：postMessage 可以传递哪些类型的数据？

支持结构化克隆算法支持的所有类型：基本类型（string、number、boolean）、对象、数组、Date、RegExp、Blob、File、ImageData、ArrayBuffer、Map、Set 等。不支持函数、DOM 节点、Symbol、Error 对象。

### Q2：iframe 加载完成后为什么收不到 postMessage？

可能原因：
1. 父页面在 iframe 的 `message` 监听器注册之前就发送了消息
2. `event.origin` 验证不匹配
3. iframe 的 sandbox 中未包含 `allow-scripts`

**解决方案：** 使用 `waitReady` 模式，iframe 先发送 `ready` 事件，父页面收到后再发送消息。

### Q3：多个 iframe 之间如何通信？

通过父页面中继：iframe A → 父页面 → iframe B。

```javascript
// 父页面中继
window.addEventListener('message', (event) => {
  if (event.origin !== 'https://iframe-a.com') return;
  // 转发给 iframe B
  iframeB.contentWindow.postMessage(event.data, 'https://iframe-b.com');
});
```

### Q4：如何在 iframe 中检测自己是否被嵌入？

```javascript
// 检测是否在 iframe 中
if (window.self !== window.top) {
  console.log('当前页面在 iframe 中');
  // 可选：检查父页面来源
  try {
    const parentOrigin = window.parent.location.origin;
    console.log('父页面来源:', parentOrigin);
  } catch (e) {
    console.log('无法获取父页面来源（跨域）');
  }
}
```

### Q5：postMessage 的消息大小有限制吗？

各浏览器实现不同，通常无硬性限制，但建议单条消息不超过 64KB。大数据传输建议分片或使用 SharedArrayBuffer（同源场景）。

### Q6：document.domain 设置后能否撤销？

不能。一旦设置 `document.domain`，无法恢复到原始值，也无法设置回更具体的子域。这是另一个不应使用它的原因。

---

## 总结

| 要点 | 结论 |
|------|------|
| 首选方案 | **postMessage** —— 浏览器原生支持，双向通信，安全性可控 |
| 辅助方案 | **CORS** —— 解决 iframe 内 Ajax 跨域问题 |
| 生产方案 | **代理服务器** —— 同源化 iframe，零前端改动 |
| 废弃方案 | **document.domain** —— 现代浏览器已弃用，应迁移到 postMessage |
| 安全核心 | 始终验证 origin、精确指定 targetOrigin、sasandbox 最小权限 |
| 最佳实践 | 使用 IframeBridge 封装、定义通信协议、waitReady 模式 |

> **参考资源：**
> - [MDN - postMessage](https://developer.mozilla.org/zh-CN/docs/Web/API/Window/postMessage)
> - [MDN - iframe](https://developer.mozilla.org/zh-CN/docs/Web/HTML/Element/iframe)
> - [MDN - document.domain](https://developer.mozilla.org/zh-CN/docs/Web/API/Document/domain)
> - [Chrome - Origin-keyed Agent Clusters](https://developer.chrome.com/docs/privacy-sandbox/origin-keyed-agent-clusters/)
> - [HTML 规范 - Cross-origin communication](https://html.spec.whatwg.org/multipage/web-messaging.html)