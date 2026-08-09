# Ajax 技术全面学习资料

---

## 目录

1. [Ajax 概述](#1-ajax-概述)
   - 1.1 [什么是 Ajax](#11-什么是-ajax)
   - 1.2 [Ajax 的工作原理](#12-ajax-的工作原理)
   - 1.3 [Ajax 的优缺点](#13-ajax-的优缺点)
   - 1.4 [与传统 Web 开发模式的区别](#14-与传统-web-开发模式的区别)
2. [核心技术详解](#2-核心技术详解)
   - 2.1 [XMLHttpRequest 对象](#21-xmlhttprequest-对象)
   - 2.2 [状态码详解](#22-状态码详解)
   - 2.3 [跨域解决方案](#23-跨域解决方案)
   - 2.4 [异步编程模式](#24-异步编程模式)
3. [常见面试题及参考答案](#3-常见面试题及参考答案)
   - [基础概念题（Q1-Q5）](#基础概念题)
   - [原理分析题（Q6-Q9）](#原理分析题)
   - [代码实现题（Q10-Q12）](#代码实现题)
   - [实际应用场景题（Q13-Q15）](#实际应用场景题)
   - [进阶面试题（Q16-Q18）](#进阶面试题)
4. [最佳实践与注意事项](#4-最佳实践与注意事项)
   - 4.1 [错误处理](#41-错误处理)
   - 4.2 [性能优化](#42-性能优化)
   - 4.3 [安全考量](#43-安全考量)
   - 4.4 [兼容性处理](#44-兼容性处理)
   - 4.5 [开发调试技巧](#45-开发调试技巧)

---

## 1. Ajax 概述

### 1.1 什么是 Ajax

Ajax（Asynchronous JavaScript And XML）最早产生于 2005 年，由 Jesse James Garrett 在文章《Ajax: A New Approach to Web Applications》中首次提出。它并非一门单一的技术，而是一组技术有机结合形成的交互式 Web 应用开发模式，核心包括：

- **HTML / XHTML**：用于构建页面结构和内容
- **CSS**：用于页面表现与样式
- **DOM**（Document Object Model）：用于动态显示和交互
- **XML / JSON**：用于数据交换格式
- **XMLHttpRequest**：用于异步通信
- **JavaScript**：用于将以上技术绑定在一起

Ajax 的核心思想是：在用户与页面交互的过程中，通过 JavaScript 在后台异步向服务器发送请求并获取数据，然后利用 DOM 操作局部更新页面，**无需重新加载整个页面**，从而带来更流畅的用户体验。

### 1.2 Ajax 的工作原理

```
┌──────────────┐         ┌─────────────────┐         ┌──────────────┐
│   浏览器端    │  HTTP   │  XMLHttpRequest  │  HTTP   │   服务器端    │
│  (JavaScript) │◄───────►│     (Ajax引擎)    │◄───────►│  (Web Server) │
└──────────────┘         └─────────────────┘         └──────────────┘
```

**工作流程：**

1. **触发事件**：用户在页面上的操作（点击按钮、输入文字等）触发 JavaScript 事件
2. **创建 XHR 对象**：JavaScript 创建 `XMLHttpRequest` 对象
3. **配置请求**：设置请求方法（GET/POST）、URL、是否异步等参数
4. **发送请求**：通过 `XMLHttpRequest` 向服务器发送 HTTP 请求
5. **服务器处理**：服务器接收请求并处理，返回响应数据
6. **接收响应**：JavaScript 监听 `onreadystatechange` 事件，获取服务器返回的数据
7. **更新页面**：通过 DOM 操作，将新数据局部更新到页面中

```javascript
// Ajax 基本工作流程示例
function ajaxRequest(url, callback) {
    // 1. 创建 XMLHttpRequest 对象
    const xhr = new XMLHttpRequest();

    // 2. 监听状态变化
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            // 3. 获取响应数据并回调
            callback(xhr.responseText);
        }
    };

    // 4. 配置并发送请求
    xhr.open('GET', url, true);
    xhr.send();
}
```

### 1.3 Ajax 的优缺点

**优点：**

| 优点 | 说明 |
|------|------|
| **无刷新更新** | 局部刷新页面，无需重新加载整个页面，用户体验更流畅 |
| **异步通信** | 不阻塞用户操作，浏览器在等待服务器响应时仍可交互 |
| **按需加载** | 只传输必要数据，减少带宽占用和服务器负载 |
| **前后端分离** | 促进前端与后端的职责分离，接口标准化 |
| **广泛支持** | 所有现代浏览器都原生支持 |

**缺点：**

| 缺点 | 说明 |
|------|------|
| **SEO 不友好** | 搜索引擎爬虫可能无法抓取动态加载的内容 |
| **浏览器历史** | 破坏浏览器前进/后退按钮的正常行为（可通过 History API 解决） |
| **跨域限制** | 受同源策略限制，跨域请求需要额外处理 |
| **调试困难** | 异步流程复杂时，调试难度增加（可借助 DevTools Network 面板） |
| **安全性** | 增加了攻击面，如 XSS、CSRF 等（需配合 CSRF Token、CSP 等防护） |

### 1.4 与传统 Web 开发模式的区别

| 对比维度 | 传统 Web 模式（同步） | Ajax 模式（异步） |
|----------|----------------------|-------------------|
| **请求方式** | 整个页面提交，全量刷新 | 局部请求，增量更新 |
| **用户体验** | 页面刷新时有白屏等待 | 页面无闪烁，操作流畅 |
| **数据传输** | 传输整个 HTML 页面 | 仅传输业务数据（JSON/XML） |
| **服务器负载** | 每次请求返回完整页面，负载高 | 只返回数据，负载低 |
| **带宽消耗** | 重复传输 HTML 模板结构，浪费带宽 | 按需传输数据，节省带宽 |
| **处理模式** | 同步阻塞，请求期间用户无法操作 | 异步非阻塞，用户可继续操作 |

```
传统模式：
┌────────┐  HTTP请求  ┌────────┐
│ 客户端  │ ────────► │ 服务器  │
│        │ ◄──────── │        │
│ (等待)  │  完整页面  │        │
└────────┘           └────────┘

Ajax模式：
┌────────┐  Ajax请求  ┌──────────────┐  HTTP请求  ┌────────┐
│ 客户端  │ ────────► │ Ajax 引擎    │ ────────► │ 服务器  │
│        │ ◄──────── │ (XMLHttpReq) │ ◄──────── │        │
│ (继续)  │  数据响应  └──────────────┘  数据响应  └────────┘
└────────┘
```

---

## 2. 核心技术详解

### 2.1 XMLHttpRequest 对象

#### 2.1.1 创建 XHR 对象

```javascript
// 标准方式（所有现代浏览器）
const xhr = new XMLHttpRequest();

// 兼容 IE5/IE6（仅遗留系统维护需要，IE 已于 2022 年停止支持）
let xhr;
if (window.XMLHttpRequest) {
    xhr = new XMLHttpRequest();
} else {
    xhr = new ActiveXObject('Microsoft.XMLHTTP');
}
```

#### 2.1.2 XHR 核心方法

```javascript
// 1. open() - 初始化请求
xhr.open(method, url, async, user, password);
// method: GET/POST/PUT/DELETE 等
// url: 请求地址
// async: true(异步) / false(同步，不推荐)

// 2. send() - 发送请求
xhr.send(body);
// GET 请求：xhr.send(null) 或 xhr.send()
// POST 请求：xhr.send('key1=value1&key2=value2')

// 3. setRequestHeader() - 设置请求头
xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

// 4. abort() - 取消请求
xhr.abort();

// 5. getResponseHeader() - 获取指定响应头
xhr.getResponseHeader('Content-Type');

// 6. getAllResponseHeaders() - 获取所有响应头
xhr.getAllResponseHeaders();
```

#### 2.1.3 XHR 核心属性

```javascript
// readyState - 请求状态码（详见 2.2 节）
xhr.readyState  // 0~4

// status - HTTP 状态码
xhr.status      // 200, 404, 500 等

// statusText - HTTP 状态文本
xhr.statusText  // "OK", "Not Found" 等

// responseText - 响应文本
xhr.responseText

// responseXML - 响应 XML 数据
xhr.responseXML

// responseType - 设置响应数据类型
xhr.responseType = 'json';  // '' | 'text' | 'json' | 'document' | 'blob' | 'arraybuffer'

// response - 根据 responseType 返回对应类型的数据
xhr.response

// timeout - 设置超时时间（毫秒）
xhr.timeout = 5000;

// withCredentials - 跨域请求是否携带 Cookie
xhr.withCredentials = true;
```

#### 2.1.4 XHR 事件

```javascript
// 传统事件监听
xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
        console.log('请求成功');
    }
};

// 现代事件监听（推荐）
xhr.onload = function() {
    // 请求成功完成时触发
    console.log('响应数据:', xhr.response);
};

xhr.onerror = function() {
    // 请求出错时触发
    console.error('网络错误');
};

xhr.onprogress = function(e) {
    // 下载进度事件
    if (e.lengthComputable) {
        const percent = (e.loaded / e.total) * 100;
        console.log(`下载进度: ${percent}%`);
    }
};

xhr.upload.onprogress = function(e) {
    // 上传进度事件
    if (e.lengthComputable) {
        const percent = (e.loaded / e.total) * 100;
        console.log(`上传进度: ${percent}%`);
    }
};

xhr.ontimeout = function() {
    // 请求超时时触发
    console.error('请求超时');
};

xhr.onabort = function() {
    // 请求被取消时触发
    console.log('请求已取消');
};

xhr.onloadstart = function() {
    // 请求开始时触发
    console.log('请求开始');
};

xhr.onloadend = function() {
    // 请求结束时触发（无论成功或失败）
    console.log('请求结束');
};
```

#### 2.1.5 GET 请求示例

```javascript
function httpGet(url, params) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        // 拼接查询参数
        if (params) {
            const queryString = Object.keys(params)
                .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
                .join('&');
            url += (url.includes('?') ? '&' : '?') + queryString;
        }

        xhr.open('GET', url, true);
        xhr.setRequestHeader('Accept', 'application/json');

        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                resolve(JSON.parse(xhr.responseText));
            } else {
                reject(new Error(`请求失败: ${xhr.status}`));
            }
        };

        xhr.onerror = () => reject(new Error('网络错误'));
        xhr.ontimeout = () => reject(new Error('请求超时'));

        xhr.timeout = 10000; // 10秒超时
        xhr.send();
    });
}
```

#### 2.1.6 POST 请求示例

```javascript
function httpPost(url, data) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        xhr.open('POST', url, true);

        // 发送 JSON 数据
        xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');

        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                resolve(JSON.parse(xhr.responseText));
            } else {
                reject(new Error(`请求失败: ${xhr.status}`));
            }
        };

        xhr.onerror = () => reject(new Error('网络错误'));

        xhr.send(JSON.stringify(data));
    });
}

// 发送表单数据
function httpPostForm(url, formData) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        xhr.open('POST', url, true);
        // 不设置 Content-Type，浏览器会自动设置 multipart/form-data 并包含 boundary

        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                resolve(JSON.parse(xhr.responseText));
            } else {
                reject(new Error(`请求失败: ${xhr.status}`));
            }
        };

        xhr.send(formData);
    });
}
```

### 2.2 状态码详解

#### 2.2.1 readyState（请求状态）

| readyState | 值 | 含义 | 说明 |
|------------|----|------|------|
| UNSENT | 0 | 未初始化 | `open()` 尚未调用 |
| OPENED | 1 | 已打开 | `open()` 已调用，`send()` 尚未调用 |
| HEADERS_RECEIVED | 2 | 已接收响应头 | `send()` 已调用，响应头和状态码已可用 |
| LOADING | 3 | 加载中 | 正在接收响应体数据 |
| DONE | 4 | 完成 | 响应数据接收完毕 |

#### 2.2.2 HTTP Status（HTTP 状态码）

**常见 HTTP 状态码分类：**

| 状态码范围 | 类别 | 含义 |
|------------|------|------|
| 1xx | 信息响应 | 请求已接收，继续处理 |
| 2xx | 成功 | 请求已成功处理 |
| 3xx | 重定向 | 需要进一步操作才能完成请求 |
| 4xx | 客户端错误 | 客户端请求有误 |
| 5xx | 服务器错误 | 服务器处理请求失败 |

**Ajax 开发中常见状态码：**

| 状态码 | 含义 | 说明与处理 |
|--------|------|------------|
| 200 | OK | 请求成功，数据正常返回 |
| 201 | Created | 资源创建成功（常用于 POST 请求） |
| 204 | No Content | 请求成功但无返回内容（常用于 DELETE） |
| 301 | Moved Permanently | 资源永久重定向 |
| 302 | Found | 临时重定向 |
| 304 | Not Modified | 资源未修改，使用缓存（GET 请求优化） |
| 400 | Bad Request | 请求参数错误，前端需校验参数 |
| 401 | Unauthorized | 未认证，需要登录 |
| 403 | Forbidden | 无权限访问 |
| 404 | Not Found | 请求的资源不存在 |
| 405 | Method Not Allowed | 请求方法不被允许 |
| 408 | Request Timeout | 请求超时 |
| 500 | Internal Server Error | 服务器内部错误 |
| 502 | Bad Gateway | 网关错误 |
| 503 | Service Unavailable | 服务暂时不可用 |
| 504 | Gateway Timeout | 网关超时 |

```javascript
// 完整的状态码处理示例
xhr.onload = function() {
    const status = xhr.status;

    if (status >= 200 && status < 300) {
        // 2xx 成功
        handleSuccess(xhr.response);
    } else if (status === 304) {
        // 使用缓存
        handleCache();
    } else if (status === 401) {
        // 未认证，跳转登录
        redirectToLogin();
    } else if (status === 403) {
        // 无权限
        showMessage('无权限访问该资源');
    } else if (status === 404) {
        // 资源不存在
        showMessage('请求的资源不存在');
    } else if (status >= 500) {
        // 服务器错误
        showMessage('服务器繁忙，请稍后重试');
    }
};
```

### 2.3 跨域解决方案

#### 2.3.1 同源策略

同源策略（Same-Origin Policy）是浏览器最核心的安全机制，它限制了一个源（origin）的文档或脚本与另一个源的资源进行交互。

**同源的定义**：协议、域名、端口三者完全相同。

| 对比 | URL | 是否同源 | 原因 |
|------|-----|----------|------|
| 基准 | `http://www.example.com/page` | — | — |
| 比较1 | `http://www.example.com/api` | 同源 | 仅路径不同 |
| 比较2 | `https://www.example.com/page` | 不同源 | 协议不同 |
| 比较3 | `http://api.example.com/page` | 不同源 | 域名不同 |
| 比较4 | `http://www.example.com:8080/page` | 不同源 | 端口不同 |

#### 2.3.2 CORS（跨域资源共享）

CORS（Cross-Origin Resource Sharing）是目前最主流的跨域解决方案，由服务端通过 HTTP 响应头来控制允许跨域的范围。

**简单请求：** 同时满足以下条件：
- 请求方法为 GET、HEAD、POST 之一
- 仅使用 `Accept`、`Accept-Language`、`Content-Language`、`Content-Type`（限 `text/plain`、`multipart/form-data`、`application/x-www-form-urlencoded`）等简单头部

浏览器直接发送请求，服务器在响应头中返回 `Access-Control-Allow-Origin`。

**预检请求（Preflight）：** 不满足简单请求条件时，浏览器会先发送一个 OPTIONS 请求进行预检：

```
客户端                       服务器
  │                            │
  │ ── OPTIONS /api/data ──►  │  (预检请求)
  │    Origin: http://a.com    │
  │                            │
  │ ◄── 200 OK ──────────────  │
  │    Access-Control-Allow-Origin: http://a.com
  │    Access-Control-Allow-Methods: GET, POST, PUT
  │    Access-Control-Allow-Headers: Content-Type
  │                            │
  │ ── POST /api/data ────►   │  (实际请求)
  │                            │
  │ ◄── 200 OK ──────────────  │
  │    Access-Control-Allow-Origin: http://a.com
```

**服务端 CORS 配置示例（Node.js / Express）：**

```javascript
// Express CORS 中间件示例
app.use((req, res, next) => {
    // 允许的源（生产环境应指定具体域名，不可用 *）
    res.setHeader('Access-Control-Allow-Origin', 'https://www.example.com');

    // 允许的请求方法
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');

    // 允许的请求头
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With');

    // 允许携带 Cookie
    res.setHeader('Access-Control-Allow-Credentials', 'true');

    // 预检请求缓存时间（秒）
    res.setHeader('Access-Control-Max-Age', '86400');

    // 预检请求直接返回
    if (req.method === 'OPTIONS') {
        return res.sendStatus(204);
    }

    next();
});
```

**CORS 相关响应头汇总：**

| 响应头 | 说明 |
|--------|------|
| `Access-Control-Allow-Origin` | 允许的源，`*` 表示所有 |
| `Access-Control-Allow-Methods` | 允许的 HTTP 方法 |
| `Access-Control-Allow-Headers` | 允许的请求头 |
| `Access-Control-Allow-Credentials` | 是否允许携带 Cookie |
| `Access-Control-Expose-Headers` | 允许前端访问的响应头 |
| `Access-Control-Max-Age` | 预检请求缓存时间 |

**前端 CORS 请求配置：**

```javascript
// 携带 Cookie 的跨域请求
const xhr = new XMLHttpRequest();
xhr.withCredentials = true; // 关键：允许携带 Cookie
xhr.open('GET', 'https://api.example.com/user', true);
xhr.send();

// 注意：此时服务端 Access-Control-Allow-Origin 不能设为 *，必须指定具体域名
```

**`SameSite` Cookie 属性（关键约束）：**

Chrome 80+ 默认 `SameSite=Lax`，跨域 Ajax 请求**不会携带 Cookie**。若需跨域携带 Cookie，服务端必须显式设置 `SameSite=None; Secure`：

| SameSite 值 | 行为 | 跨域 Ajax 是否携带 |
|-------------|------|:----------------:|
| `Strict` | 仅同源发送 | ❌ |
| `Lax`（默认） | 顶层导航时发送，Ajax 不发送 | ❌ |
| `None` | 跨域发送（需配合 `Secure`） | ✅ |

```http
# 跨域携带 Cookie 必须这样设置：
Set-Cookie: sessionId=abc123; SameSite=None; Secure; HttpOnly
```

#### 2.3.3 JSONP（JSON with Padding）

> **⚠️ 历史方案**：JSONP 在现代开发中已基本淘汰，仅用于维护遗留系统或对接不支持 CORS 的旧 API。新项目应使用 CORS 或代理服务器方案。

JSONP 利用 `<script>` 标签不受同源策略限制的特性，通过动态创建 `<script>` 标签实现跨域数据获取。

**工作原理：**

```
1. 客户端动态创建 <script> 标签，src 指向跨域 API，并附带回调函数名
2. 服务端接收到请求，将数据包装在回调函数中返回
3. 浏览器执行返回的脚本，回调函数被调用，数据被传入
```

**JSONP 实现示例：**

```javascript
// 封装 JSONP 请求
function jsonp(url, callbackName) {
    return new Promise((resolve, reject) => {
        // 生成唯一的回调函数名
        const callback = callbackName || 'jsonp_' + Date.now() + Math.random().toString(36).slice(2);

        // 先创建 script 标签（需在回调中引用，因此提前声明）
        const script = document.createElement('script');

        // 将回调函数挂载到全局
        window[callback] = function(data) {
            resolve(data);
            cleanup();
        };

        // 清理函数：移除 script 标签 + 删除全局回调
        function cleanup() {
            delete window[callback];
            if (script.parentNode) {
                document.head.removeChild(script);
            }
        }

        // 配置 script 标签
        script.src = url + (url.includes('?') ? '&' : '?') + 'callback=' + callback;
        script.onerror = () => {
            reject(new Error('JSONP 请求失败'));
            cleanup();
        };

        // 添加到页面，发起请求
        document.head.appendChild(script);
    });
}

// 使用示例
jsonp('https://api.example.com/data')
    .then(data => console.log('获取数据:', data))
    .catch(err => console.error('请求失败:', err));
```

**JSONP 优缺点：**

| 优点 | 缺点 |
|------|------|
| 兼容性好，支持老旧浏览器 | 只支持 GET 请求，不支持 POST/PUT/DELETE 等 |
| 不依赖 CORS 配置 | 安全性差，容易遭受 XSS 攻击 |
| 实现简单 | 缺乏错误处理机制（难以捕获 HTTP 错误状态码） |
| 无需服务端额外配置（除回调包装） | 服务端需要配合改造，支持回调参数 |

#### 2.3.4 其他跨域方案

**1. 代理服务器（Proxy）**

通过同源的代理服务器转发请求到目标服务器，浏览器只与同源代理交互。这是**开发环境和生产环境最常用的跨域方案**，前端零改动。

**开发环境（Vite / Webpack DevServer）：**

```javascript
// vite.config.ts (Vite) — 推荐方案
export default {
  server: {
    proxy: {
      '/api': {
        target: 'https://api.example.com',
        changeOrigin: true,                    // 修改请求头中的 Origin 为目标地址
        rewrite: (path) => path.replace(/^\/api/, '')  // 去掉 /api 前缀
      }
    }
  }
};

// webpack.config.js (Webpack DevServer)
module.exports = {
    devServer: {
        proxy: {
            '/api': {
                target: 'https://api.example.com',
                changeOrigin: true,
                pathRewrite: { '^/api': '' }
            }
        }
    }
};
```

**生产环境（Nginx 反向代理）：**

```nginx
server {
    listen 80;
    server_name www.example.com;

    location /api/ {
        proxy_pass https://api.example.com/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**2. postMessage**

HTML5 提供的跨文档通信 API，可用于不同窗口（iframe、弹出窗口）之间的跨域通信。

```javascript
// 发送方（http://a.com）
const targetWindow = document.getElementById('iframe').contentWindow;
targetWindow.postMessage('Hello from a.com', 'http://b.com');

// 接收方（http://b.com）
window.addEventListener('message', function(event) {
    // 验证来源
    if (event.origin !== 'http://a.com') return;

    console.log('收到消息:', event.data);

    // 回复消息
    event.source.postMessage('Hello back from b.com', event.origin);
});
```

**3. WebSocket**

WebSocket 协议本身不受同源策略限制，可以实现全双工跨域通信。

```javascript
const ws = new WebSocket('wss://api.example.com/ws');

ws.onopen = function() {
    ws.send(JSON.stringify({ type: 'message', data: 'Hello' }));
};

ws.onmessage = function(event) {
    console.log('收到消息:', JSON.parse(event.data));
};
```

**4. document.domain（已废弃）**

> **⚠️ 已废弃**：`document.domain` 在 **Chrome 109+** 中默认被禁用。现代项目应使用 `postMessage` 替代。仅当维护遗留系统且无法修改代码时，可通过服务端设置 `Origin-Agent-Cluster: ?0` 响应头临时恢复。

当两个页面主域相同而子域不同时，曾可通过设置 `document.domain` 来实现跨域通信。

```javascript
// ❌ 已废弃，不要在新项目中使用
// 仅适用于相同主域的情况（a.example.com 和 b.example.com）
document.domain = 'example.com';
```

**跨域方案对比总结：**

| 方案 | 适用场景 | 请求方法 | 双向通信 | 现代状态 |
|------|----------|----------|----------|----------|
| CORS | 通用跨域方案 | 全部 | 否 | ✅ 标准方案 |
| 代理服务器 | 前后端分离项目 | 全部 | 否 | ✅ 标准方案 |
| postMessage | 窗口间通信 | 不适用 | 是 | ✅ 标准方案 |
| WebSocket | 实时通信 | 全部 | 是 | ✅ 标准方案 |
| JSONP | 老浏览器兼容 | 仅 GET | 否 | ⚠️ 已淘汰 |
| document.domain | 同主域子域间 | 不适用 | 否 | ❌ 已废弃 |

### 2.4 异步编程模式

#### 2.4.1 回调函数模式

最早的异步处理方式，通过回调函数处理异步结果。

```javascript
// 回调模式
function ajaxWithCallback(url, success, error) {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.onload = function() {
        if (xhr.status === 200) {
            success(JSON.parse(xhr.responseText));
        } else {
            error(new Error(`请求失败: ${xhr.status}`));
        }
    };
    xhr.onerror = () => error(new Error('网络错误'));
    xhr.send();
}

// 使用示例 - 回调地狱
ajaxWithCallback('/api/user', function(user) {
    ajaxWithCallback('/api/orders?userId=' + user.id, function(orders) {
        ajaxWithCallback('/api/products?ids=' + orders.map(o => o.productId).join(','), function(products) {
            console.log('最终数据:', products);
        }, function(err) {
            console.error('获取产品失败:', err);
        });
    }, function(err) {
        console.error('获取订单失败:', err);
    });
}, function(err) {
    console.error('获取用户失败:', err);
});
```

**回调地狱问题：**
- 代码嵌套层级深，可读性差
- 错误处理需要在每个回调中单独处理
- 代码逻辑分散，难以维护

#### 2.4.2 Promise 模式

Promise 是 ES6 引入的异步编程解决方案，解决了回调地狱问题。

```javascript
// 封装 Ajax 为 Promise
function ajax(url, options = {}) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        const method = options.method || 'GET';

        xhr.open(method, url, true);

        // 设置请求头
        if (options.headers) {
            Object.keys(options.headers).forEach(key => {
                xhr.setRequestHeader(key, options.headers[key]);
            });
        }

        xhr.timeout = options.timeout || 10000;

        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                let data = xhr.responseText;
                try {
                    data = JSON.parse(data);
                } catch (e) {
                    // 非 JSON 数据保持原样
                }
                resolve(data);
            } else {
                reject(new Error(`请求失败: ${xhr.status} ${xhr.statusText}`));
            }
        };

        xhr.onerror = () => reject(new Error('网络错误'));
        xhr.ontimeout = () => reject(new Error('请求超时'));

        if (options.body) {
            xhr.send(JSON.stringify(options.body));
        } else {
            xhr.send();
        }
    });
}

// 链式调用 - 解决回调地狱
ajax('/api/user')
    .then(user => {
        console.log('用户信息:', user);
        return ajax(`/api/orders?userId=${user.id}`);
    })
    .then(orders => {
        console.log('订单信息:', orders);
        const ids = orders.map(o => o.productId).join(',');
        return ajax(`/api/products?ids=${ids}`);
    })
    .then(products => {
        console.log('产品信息:', products);
    })
    .catch(err => {
        // 统一错误处理
        console.error('请求出错:', err.message);
    });

// Promise 并发控制
Promise.all([
    ajax('/api/user'),
    ajax('/api/config'),
    ajax('/api/menu')
]).then(([user, config, menu]) => {
    console.log('所有请求完成:', { user, config, menu });
}).catch(err => {
    console.error('至少一个请求失败:', err);
});

// Promise.race - 竞速请求
Promise.race([
    ajax('/api/mirror1/data'),
    ajax('/api/mirror2/data')
]).then(data => {
    console.log('最快响应的数据:', data);
});
```

#### 2.4.3 async/await 模式

ES2017 引入的语法糖，使异步代码看起来像同步代码。

```javascript
// async/await 示例
async function loadUserData() {
    try {
        // 顺序执行
        const user = await ajax('/api/user');
        console.log('用户:', user);

        const orders = await ajax(`/api/orders?userId=${user.id}`);
        console.log('订单:', orders);

        const ids = orders.map(o => o.productId).join(',');
        const products = await ajax(`/api/products?ids=${ids}`);
        console.log('产品:', products);

        return { user, orders, products };
    } catch (err) {
        console.error('加载失败:', err.message);
        throw err;
    }
}

// 并发请求
async function loadPageData() {
    try {
        // 并发执行，无依赖关系的请求
        const [user, config, menu] = await Promise.all([
            ajax('/api/user'),
            ajax('/api/config'),
            ajax('/api/menu')
        ]);

        return { user, config, menu };
    } catch (err) {
        console.error('加载失败:', err.message);
        throw err;
    }
}

// Promise.allSettled — 所有请求完成（无论成功或失败），适合批量请求容错
const results = await Promise.allSettled([
    ajax('/api/user'),
    ajax('/api/config'),
    ajax('/api/menu')
]);
// results: [{ status: 'fulfilled', value: ... }, { status: 'rejected', reason: ... }, ...]
const successResults = results
    .filter(r => r.status === 'fulfilled')
    .map(r => r.value);

// Promise.any — 返回第一个成功的请求结果，适合多镜像竞速
const fastestData = await Promise.any([
    ajax('/api/mirror1/data'),
    ajax('/api/mirror2/data')
]);

// 带超时的 async/await 请求（现代写法，使用 AbortSignal.timeout）
async function ajaxWithTimeout(url, timeout = 5000) {
    try {
        const response = await fetch(url, { signal: AbortSignal.timeout(timeout) });
        return await response.json();
    } catch (err) {
        if (err.name === 'TimeoutError') throw new Error('请求超时');
        throw err;
    }
}

// navigator.sendBeacon — 页面卸载时发送数据（不阻塞卸载，适合埋点上报）
window.addEventListener('pagehide', () => {
    navigator.sendBeacon('/api/analytics', JSON.stringify({
        page: location.pathname,
        duration: Date.now() - pageStartTime
    }));
});
```

**三种异步模式对比：**

| 模式 | 可读性 | 错误处理 | 并发控制 | 适用场景 |
|------|--------|----------|----------|----------|
| 回调函数 | 差（嵌套深） | 分散 | 复杂 | 简单异步操作 |
| Promise | 较好（链式） | 统一 | 便捷 | 复杂异步流程 |
| async/await | 优秀（同步风格） | 简洁 | 便捷 | 推荐使用 |

---

## 3. 常见面试题及参考答案

### 基础概念题

#### Q1：什么是 Ajax？它解决了什么问题？

**难度：** 初级 | **知识点：** Ajax 定义、作用

**参考答案：**

Ajax（Asynchronous JavaScript And XML）是一种在无需重新加载整个网页的情况下，与服务器交换数据并更新部分网页的技术。它解决了传统 Web 应用中每次操作都需要完整刷新页面导致用户体验差、服务器负载高、带宽浪费的问题。通过 Ajax，页面可以异步请求数据并局部更新，实现类似桌面应用的流畅交互体验。

**评分要点：**
- 能说出 Ajax 全称及含义（2 分）
- 能解释"无刷新局部更新"的核心价值（2 分）
- 能对比传统模式说明优势（1 分）

---

#### Q2：Ajax 的核心技术组件有哪些？

**难度：** 初级 | **知识点：** Ajax 技术组成

**参考答案：**

Ajax 不是单一技术，而是多种技术的组合：

1. **HTML/XHTML**：页面结构
2. **CSS**：页面样式
3. **DOM**：动态操作页面内容
4. **XML/JSON**：数据交换格式
5. **XMLHttpRequest**：异步通信核心对象
6. **JavaScript**：将以上技术绑定在一起的胶水语言

**评分要点：**
- 列出至少 4 项核心技术（每个 1 分）
- 能简要说明每项技术的作用（加分项）

---

#### Q3：Ajax 的优缺点分别是什么？

**难度：** 初级 | **知识点：** Ajax 优缺点分析

**参考答案：**

**优点：**
- 无刷新更新页面，用户体验好
- 异步通信，不阻塞用户操作
- 按需传输数据，减少带宽和服务器负载
- 促进前后端分离架构

**缺点：**
- SEO 不友好（搜索引擎不易抓取动态内容）
- 破坏浏览器前进/后退机制（需 History API 补救）
- 跨域请求受同源策略限制
- 增加安全风险（XSS、CSRF 等，需配合 CSRF Token、CSP 等防护）

**评分要点：**
- 优缺点各列出至少 3 条（每条 1 分）
- 能给出缺点的解决思路（加分项）

---

#### Q4：XMLHttpRequest 的 readyState 有哪些值？分别代表什么含义？

**难度：** 初级 | **知识点：** readyState 状态码

**参考答案：**

| readyState | 常量名 | 含义 |
|------------|--------|------|
| 0 | UNSENT | 未初始化，`open()` 未调用 |
| 1 | OPENED | 已调用 `open()`，`send()` 未调用 |
| 2 | HEADERS_RECEIVED | 已调用 `send()`，响应头和状态码可用 |
| 3 | LOADING | 正在接收响应体数据 |
| 4 | DONE | 响应数据接收完毕 |

**评分要点：**
- 准确说出 5 个状态值及含义（每个 1 分）

---

#### Q5：GET 和 POST 在 Ajax 中有什么区别？

**难度：** 初级 | **知识点：** HTTP 方法对比

**参考答案：**

| 区别 | GET | POST |
|------|-----|------|
| 参数位置 | URL 查询字符串中 | 请求体（body）中 |
| 数据大小 | 受 URL 长度限制（约 2KB） | 无严格限制 |
| 安全性 | 参数暴露在 URL 中 | 参数在请求体中，相对安全 |
| 缓存 | 可被浏览器缓存 | 不会被缓存（除非手动设置） |
| 幂等性 | 幂等（多次请求结果相同） | 非幂等 |
| 用途 | 获取数据、查询 | 提交数据、创建资源 |
| 后退/刷新 | 无害 | 浏览器会提示重新提交 |

**评分要点：**
- 能对比 4 个以上维度（每个维度 1 分）
- 能结合实际场景说明选择依据（加分项）

---

### 原理分析题

#### Q6：请描述 Ajax 的完整工作流程？

**难度：** 中级 | **知识点：** Ajax 工作原理、请求生命周期

**参考答案：**

Ajax 的完整工作流程如下：

1. **创建 XHR 对象**：`const xhr = new XMLHttpRequest();`
2. **配置请求**：`xhr.open('GET', '/api/data', true);` 设置请求方法、URL、是否异步
3. **设置请求头**（可选）：`xhr.setRequestHeader('Content-Type', 'application/json');`
4. **注册事件监听**：`xhr.onreadystatechange` 或 `xhr.onload` 等
5. **发送请求**：`xhr.send(body);`，GET 请求传 `null` 或不传
6. **服务器处理**：服务器接收请求，执行业务逻辑，返回响应
7. **接收响应**：浏览器触发 `onreadystatechange` 事件，`readyState === 4` 时表示完成
8. **处理数据**：解析 `responseText` 或 `response`，更新 DOM

**关键点：** 整个过程中，JavaScript 不会阻塞，用户可以继续与页面交互。

**评分要点：**
- 完整描述 8 个步骤（8 分）
- 能绘制流程图（加分项）
- 能说明异步非阻塞特性（加分项）

---

#### Q7：什么是同源策略？为什么需要它？

**难度：** 中级 | **知识点：** 浏览器安全策略、同源策略

**参考答案：**

**同源策略**是浏览器最核心的安全机制，它限制了一个源（协议 + 域名 + 端口）的文档或脚本与另一个源的资源交互。

**同源的定义：** 协议、域名、端口三者完全相同才算同源。

**为什么需要同源策略：**
- 防止恶意网站读取其他网站的敏感数据（如 Cookie、localStorage）
- 防止 CSRF（跨站请求伪造）攻击
- 隔离不同网站，保护用户隐私和安全

**示例：** 如果用户在 `http://bank.com` 登录后，又访问了 `http://evil.com`，若无同源策略，`evil.com` 的脚本就可以通过 Ajax 读取用户在 `bank.com` 的账户信息。

**评分要点：**
- 准确解释同源定义（协议、域名、端口）（3 分）
- 能说明安全意义（2 分）
- 能举出实际攻击场景（加分项）

---

#### Q8：CORS 的工作原理是什么？什么是简单请求和预检请求？

**难度：** 中级 | **知识点：** CORS 机制、预检请求

**参考答案：**

**CORS**（Cross-Origin Resource Sharing）通过 HTTP 响应头告诉浏览器允许哪些源的跨域请求。

**简单请求（Simple Request）：**
同时满足以下条件：
- 请求方法为 GET、HEAD、POST 之一
- 仅包含简单头部（`Accept`、`Accept-Language`、`Content-Language`、`Content-Type` 为 `text/plain`、`multipart/form-data`、`application/x-www-form-urlencoded`）
- 无 `ReadableStream` 对象

处理流程：浏览器直接发送请求到服务器，检查响应头 `Access-Control-Allow-Origin` 是否匹配。

**预检请求（Preflight Request）：**
不满足简单请求条件时，浏览器先发送 OPTIONS 请求：
- 携带 `Origin`、`Access-Control-Request-Method`、`Access-Control-Request-Headers`
- 服务器返回 `Access-Control-Allow-Origin`、`Access-Control-Allow-Methods`、`Access-Control-Allow-Headers`
- 预检通过后，浏览器再发送实际请求

**评分要点：**
- 准确解释 CORS 机制（2 分）
- 区分简单请求和预检请求的条件（3 分）
- 能说出 OPTIONS 预检请求携带的关键头部（加分项）

---

#### Q9：JSONP 的实现原理是什么？与 CORS 相比有何优缺点？

**难度：** 中级 | **知识点：** JSONP 原理、跨域方案对比

**参考答案：**

**JSONP 原理：**
利用 `<script>` 标签不受同源策略限制的特性，动态创建 `<script>` 标签，其 `src` 指向需要跨域访问的 API 地址，并附带回调函数名参数。服务器返回一个函数调用，将数据作为参数传入，浏览器执行该脚本，数据即被传入回调函数。

```javascript
// 原理示意
// 1. 客户端定义回调函数
function handleData(data) { console.log(data); }

// 2. 动态创建 script 标签
// <script src="http://api.example.com/data?callback=handleData"></script>

// 3. 服务器返回
// handleData({"name": "张三", "age": 25})
```

**与 CORS 对比：**

| 维度 | JSONP | CORS |
|------|-------|------|
| 请求方法 | 仅 GET | 全部方法 |
| 错误处理 | 难以捕获 HTTP 错误 | 完整的错误处理 |
| 安全性 | 较低（XSS 风险） | 较高（可控的源白名单） |
| 服务端改造 | 需支持回调包装 | 需设置响应头 |
| 浏览器兼容 | 极好（全兼容） | IE10+ |

**评分要点：**
- 准确解释 JSONP 原理（3 分）
- 能写出代码示例（2 分）
- 能对比 CORS 说明优劣（加分项）

---

### 代码实现题

#### Q10：请用原生 JavaScript 封装一个支持 GET/POST 的 Ajax 函数

**难度：** 中级 | **知识点：** XMLHttpRequest 封装、Promise

**参考答案：**

```javascript
function ajax({ url, method = 'GET', data = null, headers = {}, timeout = 10000 }) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        // 处理 GET 请求参数
        if (method.toUpperCase() === 'GET' && data) {
            const params = Object.keys(data)
                .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(data[key])}`)
                .join('&');
            url += (url.includes('?') ? '&' : '?') + params;
        }

        xhr.open(method.toUpperCase(), url, true);

        // 设置请求头
        Object.keys(headers).forEach(key => {
            xhr.setRequestHeader(key, headers[key]);
        });

        // 默认 Content-Type
        if (method.toUpperCase() === 'POST' && !headers['Content-Type']) {
            xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
        }

        xhr.timeout = timeout;

        // 响应处理
        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                let result = xhr.responseText;
                try {
                    result = JSON.parse(result);
                } catch (e) {
                    // 非 JSON 保持原样
                }
                resolve({
                    data: result,
                    status: xhr.status,
                    headers: xhr.getAllResponseHeaders()
                });
            } else {
                reject(new Error(`请求失败: ${xhr.status} ${xhr.statusText}`));
            }
        };

        xhr.onerror = () => reject(new Error('网络错误'));
        xhr.ontimeout = () => reject(new Error('请求超时'));

        // 发送请求
        if (method.toUpperCase() === 'POST' && data) {
            xhr.send(JSON.stringify(data));
        } else {
            xhr.send();
        }
    });
}

// 使用示例
ajax({
    url: '/api/users',
    method: 'GET',
    data: { page: 1, size: 10 }
}).then(res => {
    console.log('数据:', res.data);
}).catch(err => {
    console.error('错误:', err.message);
});
```

**评分要点：**
- 支持 GET/POST 方法切换（2 分）
- GET 请求参数拼接正确（2 分）
- POST 请求 JSON 数据发送（2 分）
- Promise 封装和错误处理（2 分）
- 超时设置（1 分）
- 代码清晰、注释合理（1 分）

---

#### Q11：请实现一个带重试机制的 Ajax 请求函数

**难度：** 高级 | **知识点：** 错误处理、重试策略、Promise

**参考答案：**

```javascript
function ajaxWithRetry(url, options = {}) {
    const {
        method = 'GET',
        data = null,
        headers = {},
        timeout = 10000,
        retries = 3,           // 最大重试次数
        retryDelay = 1000,     // 重试间隔（毫秒）
        retryOn = [500, 502, 503, 504]  // 哪些状态码需要重试
    } = options;

    let attempt = 0;

    function doRequest() {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open(method, url, true);

            Object.keys(headers).forEach(key => {
                xhr.setRequestHeader(key, headers[key]);
            });

            xhr.timeout = timeout;

            xhr.onload = function() {
                if (xhr.status >= 200 && xhr.status < 300) {
                    resolve(xhr.responseText);
                } else if (retryOn.includes(xhr.status)) {
                    // 服务器错误，可以重试
                    reject({ retryable: true, error: new Error(`服务器错误: ${xhr.status}`) });
                } else {
                    // 客户端错误，不重试
                    reject({ retryable: false, error: new Error(`请求失败: ${xhr.status}`) });
                }
            };

            xhr.onerror = function() {
                reject({ retryable: true, error: new Error('网络错误') });
            };

            xhr.ontimeout = function() {
                reject({ retryable: true, error: new Error('请求超时') });
            };

            if (method === 'POST' && data) {
                xhr.send(JSON.stringify(data));
            } else {
                xhr.send();
            }
        }).catch(({ retryable, error }) => {
            attempt++;
            if (retryable && attempt < retries) {
                console.log(`第 ${attempt} 次重试，${retryDelay}ms 后重试...`);
                // 延迟后重试（可加指数退避）
                return new Promise(resolve => {
                    setTimeout(() => {
                        resolve(doRequest());
                    }, retryDelay * attempt); // 指数退避：每次重试间隔递增
                });
            }
            throw error;
        });
    }

    return doRequest();
}

// 使用示例
ajaxWithRetry('/api/data', {
    retries: 3,
    retryDelay: 1000,
    retryOn: [500, 502, 503, 504]
}).then(data => {
    console.log('成功:', data);
}).catch(err => {
    console.error('最终失败:', err.message);
});
```

**评分要点：**
- 实现重试逻辑（3 分）
- 区分可重试和不可重试的错误（2 分）
- 指数退避延迟策略（2 分）
- 重试次数限制（1 分）
- 代码结构清晰，无全局变量污染（2 分）

---

#### Q12：如何实现 Ajax 请求的并发控制（限制同时请求数量）？

**难度：** 高级 | **知识点：** 并发控制、Promise 队列

**参考答案：**

```javascript
class RequestPool {
    constructor(maxConcurrent = 3) {
        this.maxConcurrent = maxConcurrent;
        this.running = 0;       // 当前运行的请求数
        this.queue = [];        // 等待队列
    }

    // 添加请求到池中
    add(requestFn) {
        return new Promise((resolve, reject) => {
            const task = { requestFn, resolve, reject };
            this.queue.push(task);
            this.run();
        });
    }

    // 执行请求
    run() {
        while (this.running < this.maxConcurrent && this.queue.length > 0) {
            const task = this.queue.shift();
            this.running++;

            task.requestFn()
                .then(result => {
                    task.resolve(result);
                })
                .catch(err => {
                    task.reject(err);
                })
                .finally(() => {
                    this.running--;
                    this.run(); // 执行下一个任务
                });
        }
    }
}

// 使用示例
const pool = new RequestPool(3); // 最多同时 3 个请求

const urls = [
    '/api/data1',
    '/api/data2',
    '/api/data3',
    '/api/data4',
    '/api/data5',
    '/api/data6'
];

// 批量请求，自动控制并发
Promise.all(
    urls.map(url => pool.add(() => ajax(url)))
).then(results => {
    console.log('所有请求完成:', results);
}).catch(err => {
    console.error('请求失败:', err);
});
```

**评分要点：**
- 实现并发控制逻辑（4 分）
- 队列管理机制（2 分）
- 完成自动触发下一个任务（2 分）
- 错误处理不影响其他请求（2 分）

---

### 实际应用场景题

#### Q13：如何处理 Ajax 请求中的文件上传并显示进度条？

**难度：** 中级 | **知识点：** FormData、upload 事件、进度监听

**参考答案：**

```javascript
function uploadFile(file, onProgress) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        const formData = new FormData();

        formData.append('file', file);
        // 可附加其他字段
        formData.append('category', 'document');

        xhr.open('POST', '/api/upload', true);

        // 监听上传进度
        xhr.upload.onprogress = function(e) {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                onProgress(percent);
            }
        };

        xhr.onload = function() {
            if (xhr.status === 200) {
                resolve(JSON.parse(xhr.responseText));
            } else {
                reject(new Error(`上传失败: ${xhr.status}`));
            }
        };

        xhr.onerror = () => reject(new Error('网络错误'));
        xhr.ontimeout = () => reject(new Error('上传超时'));

        xhr.send(formData);
    });
}

// 使用示例
const fileInput = document.getElementById('fileInput');
const progressBar = document.getElementById('progressBar');

fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;

    uploadFile(file, (percent) => {
        progressBar.style.width = percent + '%';
        progressBar.textContent = percent + '%';
    }).then(result => {
        console.log('上传成功:', result.url);
    }).catch(err => {
        console.error('上传失败:', err.message);
    });
});
```

**评分要点：**
- 使用 FormData 构建上传数据（2 分）
- 正确监听 `xhr.upload.onprogress` 事件（3 分）
- 计算进度百分比（2 分）
- 错误处理（2 分）
- 能区分上传和下载进度事件（1 分）

---

#### Q14：Ajax 请求如何实现取消功能？

**难度：** 中级 | **知识点：** abort、AbortController

**参考答案：**

**XMLHttpRequest 方式：**

```javascript
// 使用 xhr.abort() 取消请求
function cancellableRequest(url) {
    const xhr = new XMLHttpRequest();
    let isCancelled = false;

    const promise = new Promise((resolve, reject) => {
        xhr.open('GET', url, true);
        xhr.onload = function() {
            if (!isCancelled) {
                resolve(xhr.responseText);
            }
        };
        xhr.onerror = () => reject(new Error('网络错误'));
        xhr.send();
    });

    // 取消方法
    promise.cancel = function() {
        isCancelled = true;
        xhr.abort();
    };

    return promise;
}

// 使用
const request = cancellableRequest('/api/large-data');
request.then(data => console.log(data)).catch(err => console.error(err));

// 5 秒后取消
setTimeout(() => request.cancel(), 5000);
```

**Fetch + AbortController 方式（现代推荐）：**

```javascript
function cancellableFetch(url) {
    const controller = new AbortController();

    const promise = fetch(url, { signal: controller.signal })
        .then(response => response.json());

    promise.cancel = function() {
        controller.abort();
    };

    return promise;
}

// 使用
const request = cancellableFetch('/api/large-data');
request.then(data => console.log(data)).catch(err => {
    if (err.name === 'AbortError') {
        console.log('请求已取消');
    } else {
        console.error('请求失败:', err);
    }
});

// 取消请求
request.cancel();
```

**评分要点：**
- 能正确使用 `xhr.abort()` 或 `AbortController`（3 分）
- 区分取消和错误情况（2 分）
- 清理资源避免内存泄漏（2 分）
- 实际应用场景（防抖搜索、离开页面时取消）（3 分）

---

#### Q15：在一个搜索框中，如何用 Ajax 实现防抖（debounce）和节流（throttle）？

**难度：** 高级 | **知识点：** 防抖、节流、性能优化

**参考答案：**

**防抖（Debounce）：** 一定时间内多次触发只执行最后一次。适用于搜索框输入联想。

**节流（Throttle）：** 一定时间内只执行一次。适用于滚动加载、按钮点击。

```javascript
// 防抖函数
function debounce(fn, delay = 300) {
    let timer = null;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => {
            fn.apply(this, args);
        }, delay);
    };
}

// 节流函数
function throttle(fn, delay = 300) {
    let lastTime = 0;
    return function(...args) {
        const now = Date.now();
        if (now - lastTime >= delay) {
            lastTime = now;
            fn.apply(this, args);
        }
    };
}

// 搜索框应用 - 防抖
const searchInput = document.getElementById('searchInput');
const suggestionBox = document.getElementById('suggestionBox');

// 发送搜索请求
function search(keyword) {
    if (!keyword.trim()) {
        suggestionBox.innerHTML = '';
        return;
    }

    ajax({
        url: '/api/search',
        method: 'GET',
        data: { keyword }
    }).then(res => {
        // 渲染搜索建议
        suggestionBox.innerHTML = res.data
            .map(item => `<div class="suggestion-item">${item.name}</div>`)
            .join('');
    }).catch(err => {
        console.error('搜索失败:', err);
    });
}

// 绑定防抖后的搜索函数
const debouncedSearch = debounce(search, 300);

searchInput.addEventListener('input', function(e) {
    debouncedSearch(e.target.value);
});

// 滚动加载应用 - 节流
const listContainer = document.getElementById('listContainer');
let page = 1;
let isLoading = false;

function loadMore() {
    if (isLoading) return;
    isLoading = true;

    ajax({
        url: '/api/list',
        data: { page, size: 20 }
    }).then(res => {
        // 渲染列表数据
        res.data.forEach(item => {
            const div = document.createElement('div');
            div.textContent = item.title;
            listContainer.appendChild(div);
        });
        page++;
        isLoading = false;
    }).catch(err => {
        console.error('加载失败:', err);
        isLoading = false;
    });
}

const throttledLoad = throttle(loadMore, 500);

listContainer.addEventListener('scroll', function() {
    const { scrollTop, scrollHeight, clientHeight } = listContainer;
    if (scrollTop + clientHeight >= scrollHeight - 50) {
        throttledLoad();
    }
});
```

**评分要点：**
- 正确实现防抖函数（2 分）
- 正确实现节流函数（2 分）
- 结合实际场景正确应用（3 分）
- 处理边界情况（空值、加载状态）（2 分）
- 能区分防抖和节流的使用场景（1 分）

---

### 进阶面试题

#### Q16：Ajax 与 Fetch API 有什么区别？

**难度：** 中级 | **知识点：** Fetch API、Ajax 对比

**参考答案：**

| 对比维度 | Ajax (XMLHttpRequest) | Fetch API |
|----------|----------------------|-----------|
| 规范 | 较老的技术规范 | 现代标准，基于 Promise |
| Promise | 需手动封装 | 原生支持 Promise |
| 语法简洁性 | 较繁琐 | 更简洁、链式调用 |
| Cookie 携带 | 默认携带同源 Cookie | 默认不携带，需设置 `credentials: 'include'` |
| 请求取消 | `xhr.abort()` | `AbortController.abort()` |
| 进度监听 | 原生支持 `onprogress` / `upload.onprogress` | 通过 `response.body`（ReadableStream）支持下载进度；上传进度仍需 XHR |
| 超时设置 | `xhr.timeout`（原生） | `AbortSignal.timeout(ms)`（原生）或 `AbortController + setTimeout` |
| 错误处理 | `onerror` 事件 | 仅网络错误 reject，HTTP 4xx/5xx 不 reject，需手动判断 `response.ok` |
| 响应流 | 不支持 | 支持 `response.body` 流式读取 |
| 浏览器兼容 | 所有浏览器 | 所有现代浏览器（IE 不支持，需 polyfill） |

**代码对比：**

```javascript
// ===== Ajax (XMLHttpRequest) 方式 =====
const xhr = new XMLHttpRequest();
xhr.open('GET', '/api/data');
xhr.timeout = 5000;  // 原生超时设置
xhr.onload = () => console.log(xhr.responseText);
xhr.onerror = () => console.error('网络错误');
xhr.ontimeout = () => console.error('请求超时');
xhr.send();

// ===== Fetch 方式（现代推荐） =====
// 基本用法
fetch('/api/data')
    .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);  // 需手动判断
        return res.json();
    })
    .then(data => console.log(data))
    .catch(err => console.error('Error:', err));

// Fetch + 超时（AbortSignal.timeout，现代浏览器原生支持）
fetch('/api/data', { signal: AbortSignal.timeout(5000) })
    .then(res => res.json())
    .catch(err => {
        if (err.name === 'TimeoutError') console.error('请求超时');
        else if (err.name === 'AbortError') console.error('请求已取消');
        else console.error('请求失败:', err);
    });

// Fetch + 携带 Cookie
fetch('/api/data', { credentials: 'include' })
    .then(res => res.json());
```

**选型建议：**
- 新项目优先使用 **Fetch API**（语法简洁、原生 Promise、支持流式读取）
- 需要**上传进度监听**时仍使用 **XHR**（Fetch 上传进度支持有限）
- 需要**请求/响应拦截器、自动 JSON 转换、超时重试**等高级功能时，使用 **Axios** 库（基于 XHR 封装，功能最完善）

**评分要点：**
- 至少对比 5 个维度（每个 1 分）
- 能写出代码对比示例（2 分）
- 能说明各自的适用场景及选型建议（3 分）

---

#### Q17：如何处理 Ajax 请求中的安全性问题？

**难度：** 高级 | **知识点：** Web 安全、XSS、CSRF、CORS 安全

**参考答案：**

Ajax 开发中需要注意以下安全问题：

**1. XSS（跨站脚本攻击）防护：**
```javascript
// 对用户输入进行转义
function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// 使用 textContent 而非 innerHTML 插入内容
element.textContent = userInput;  // 安全
// element.innerHTML = userInput; // 危险！可能执行恶意脚本
```

**2. CSRF（跨站请求伪造）防护：**
```javascript
// 方案一：请求头携带 CSRF Token
xhr.setRequestHeader('X-CSRF-Token', getCSRFToken());

// 方案二：SameSite Cookie 属性
// Set-Cookie: sessionid=xxx; SameSite=Strict

// 方案三：验证 Referer/Origin 头（服务端）
```

**3. 数据验证：**
```javascript
// 发送前验证数据
function validateAndSend(data) {
    // 验证数据类型和格式
    if (typeof data !== 'object') {
        throw new Error('数据格式错误');
    }
    // 防止原型污染
    if (data.hasOwnProperty('__proto__')) {
        throw new Error('非法数据');
    }
    return JSON.stringify(data);
}
```

**4. HTTPS 传输：** 生产环境必须使用 HTTPS 加密传输，防止中间人攻击。

**5. 敏感信息保护：**
```javascript
// 避免在 URL 中传递敏感信息
// 错误：/api/user?password=123456
// 正确：通过 POST body 传输，并使用 HTTPS

// 不在前端存储敏感信息
// 错误：localStorage.setItem('token', accessToken);
// 正确：使用 HttpOnly Cookie 存储 token
```

**6. CORS 安全配置：**
```javascript
// 服务端不应使用 Access-Control-Allow-Origin: *
// 应指定具体允许的域名
res.setHeader('Access-Control-Allow-Origin', 'https://trusted.example.com');
```

**评分要点：**
- 能识别至少 4 种安全风险（每种 2 分）
- 能给出具体防护方案和代码（2 分）

---

#### Q18：Ajax 请求时如何实现缓存策略？

**难度：** 高级 | **知识点：** HTTP 缓存、缓存策略

**参考答案：**

**1. 利用 HTTP 缓存头：**

```javascript
// 服务端设置缓存头
// 强缓存：
// Cache-Control: max-age=3600  （缓存 1 小时）
// Cache-Control: no-cache      （每次验证）
// Cache-Control: no-store      （不缓存）

// 协商缓存：
// ETag: "abc123"
// Last-Modified: Wed, 21 Oct 2025 07:28:00 GMT
```

**2. 前端缓存实现：**

```javascript
// 前端缓存管理器
class AjaxCache {
    constructor() {
        this.cache = new Map();
    }

    // 生成缓存键
    getKey(url, params) {
        return url + JSON.stringify(params || {});
    }

    // 获取缓存数据
    get(url, params) {
        const key = this.getKey(url, params);
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < cached.ttl) {
            console.log('命中缓存:', key);
            return Promise.resolve(cached.data);
        }
        return null;
    }

    // 设置缓存
    set(url, params, data, ttl = 60000) {
        const key = this.getKey(url, params);
        this.cache.set(key, {
            data,
            timestamp: Date.now(),
            ttl
        });
    }

    // 清除缓存
    clear(url) {
        if (url) {
            for (const key of this.cache.keys()) {
                if (key.startsWith(url)) {
                    this.cache.delete(key);
                }
            }
        } else {
            this.cache.clear();
        }
    }
}

// 带缓存的 Ajax 请求
const cache = new AjaxCache();

function cachedAjax(url, params, options = {}) {
    const { ttl = 60000, forceRefresh = false } = options;

    if (!forceRefresh) {
        const cachedData = cache.get(url, params);
        if (cachedData) return cachedData;
    }

    return ajax({ url, method: 'GET', data: params })
        .then(res => {
            cache.set(url, params, res.data, ttl);
            return res;
        });
}

// 使用示例
cachedAjax('/api/config', null, { ttl: 300000 }) // 缓存 5 分钟
    .then(data => console.log('配置:', data));
```

**3. 防止缓存（确保获取最新数据）：**

```javascript
// 方法一：URL 添加时间戳
xhr.open('GET', `/api/data?_t=${Date.now()}`);

// 方法二：设置请求头
xhr.setRequestHeader('Cache-Control', 'no-cache');
xhr.setRequestHeader('If-Modified-Since', '0');

// 方法三：POST 代替 GET（POST 默认不被缓存）
```

**评分要点：**
- 理解 HTTP 强缓存和协商缓存（2 分）
- 实现前端缓存管理器（3 分）
- 缓存失效策略（2 分）
- 防止缓存的方法（2 分）
- 实际应用场景（1 分）

---

## 4. 最佳实践与注意事项

### 4.1 错误处理

```javascript
// 完善的错误处理封装
async function request(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        timeout: 10000,
        retries: 0,
        retryDelay: 1000,
        showError: true  // 是否显示错误提示
    };

    const config = { ...defaultOptions, ...options };

    try {
        const response = await fetch(url, {
            method: config.method,
            headers: {
                'Content-Type': 'application/json',
                ...config.headers
            },
            body: config.method !== 'GET' ? JSON.stringify(config.data) : undefined,
            signal: AbortSignal.timeout(config.timeout)
        });

        if (!response.ok) {
            // 根据状态码给出不同提示
            const errorMessages = {
                400: '请求参数有误',
                401: '请先登录',
                403: '没有权限访问',
                404: '请求的资源不存在',
                500: '服务器内部错误',
                502: '网关错误',
                503: '服务暂不可用'
            };

            const message = errorMessages[response.status] || `请求失败（${response.status}）`;
            throw new Error(message);
        }

        return await response.json();
    } catch (error) {
        // 网络错误处理
        if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
            error.message = '网络连接失败，请检查网络';
        }

        // 超时处理
        if (error.name === 'TimeoutError' || error.name === 'AbortError') {
            error.message = '请求超时，请稍后重试';
        }

        // 显示错误提示
        if (config.showError && config.retries === 0) {
            showToast(error.message);
        }

        throw error;
    }
}
```

### 4.2 性能优化

```javascript
// 1. 请求合并 - 将多个请求合并为一个
function batchRequest(requests) {
    const grouped = {};
    requests.forEach(req => {
        const key = req.url;
        if (!grouped[key]) grouped[key] = [];
        grouped[key].push(req);
    });

    return Promise.all(
        Object.entries(grouped).map(([url, reqs]) => {
            // 合并参数
            const ids = reqs.map(r => r.params.id).join(',');
            return ajax({ url, method: 'GET', data: { ids } });
        })
    );
}

// 2. 请求去重 - 避免重复请求
const pendingRequests = new Map();

function deduplicatedAjax(url, params) {
    const key = url + JSON.stringify(params);

    if (pendingRequests.has(key)) {
        console.log('请求去重，复用进行中的请求');
        return pendingRequests.get(key);
    }

    const promise = ajax({ url, method: 'GET', data: params })
        .finally(() => {
            pendingRequests.delete(key);
        });

    pendingRequests.set(key, promise);
    return promise;
}

// 3. 预加载 - 提前加载可能需要的数据
function preload(urls) {
    const link = document.createElement('link');
    urls.forEach(url => {
        link.rel = 'prefetch';
        link.href = url;
        document.head.appendChild(link);
    });
}

// 4. 数据压缩 - 请求头告知服务器支持压缩
xhr.setRequestHeader('Accept-Encoding', 'gzip, deflate, br');
```

### 4.3 安全考量

```javascript
// 1. 输入验证与清理
function sanitizeInput(input) {
    if (typeof input === 'string') {
        // 移除危险字符
        return input.replace(/[<>'"&]/g, '');
    }
    return input;
}

// 2. Token 管理
class TokenManager {
    constructor() {
        this.token = null;
        this.refreshPromise = null;
    }

    getToken() {
        return this.token;
    }

    setToken(token) {
        this.token = token;
    }

    // 无感刷新 Token
    async refreshToken() {
        if (this.refreshPromise) {
            return this.refreshPromise;
        }

        this.refreshPromise = ajax({
            url: '/api/auth/refresh',
            method: 'POST'
        }).then(res => {
            this.token = res.data.token;
            return this.token;
        }).finally(() => {
            this.refreshPromise = null;
        });

        return this.refreshPromise;
    }

    clearToken() {
        this.token = null;
    }
}

// 3. 请求拦截器 - 统一添加认证和日志
function createRequestInterceptor() {
    const tokenManager = new TokenManager();

    return async function interceptor(url, options) {
        // 添加 Token
        const token = tokenManager.getToken();
        if (token) {
            options.headers = {
                ...options.headers,
                'Authorization': `Bearer ${token}`
            };
        }

        // 添加防重放攻击的随机数
        options.headers['X-Request-Id'] = generateUUID();

        // 日志记录
        console.log(`[Ajax] ${options.method} ${url}`, {
            timestamp: new Date().toISOString(),
            params: options.data
        });

        try {
            const response = await request(url, options);
            console.log(`[Ajax] 响应 ${url}`, response);
            return response;
        } catch (error) {
            console.error(`[Ajax] 错误 ${url}`, error);
            throw error;
        }
    };
}
```

### 4.4 兼容性处理

> **现代浏览器兼容性说明**：IE 已于 2022 年正式停止支持。所有现代浏览器（Chrome、Firefox、Safari、Edge）均原生支持 `XMLHttpRequest`、`Fetch API`、`AbortController`、`AbortSignal.timeout()` 等全部 Ajax 相关 API。以下兼容代码仅用于维护遗留系统。

```javascript
// 现代环境直接使用，无需兼容处理
const xhr = new XMLHttpRequest();
// 或
const response = await fetch(url, { signal: AbortSignal.timeout(5000) });

// ========== 仅遗留系统维护需要 ==========
// 创建 XHR 的兼容写法（支持 IE6+）
function createXHR() {
    if (typeof XMLHttpRequest !== 'undefined') {
        return new XMLHttpRequest();
    } else if (typeof ActiveXObject !== 'undefined') {
        // IE5/IE6 使用 ActiveXObject
        const versions = ['MSXML2.XMLHttp.6.0', 'MSXML2.XMLHttp.3.0', 'MSXML2.XMLHttp'];
        for (const version of versions) {
            try {
                return new ActiveXObject(version);
            } catch (e) { /* 继续尝试下一个版本 */ }
        }
    }
    throw new Error('浏览器不支持 Ajax');
}

// 跨浏览器事件绑定（支持 IE8+）
function addEvent(element, type, handler) {
    if (element.addEventListener) {
        element.addEventListener(type, handler, false);
    } else if (element.attachEvent) {
        element.attachEvent('on' + type, handler);
    } else {
        element['on' + type] = handler;
    }
}
```

### 4.5 开发调试技巧

```javascript
// 1. 开发环境下的请求日志
if (process.env.NODE_ENV === 'development') {
    const originalOpen = XMLHttpRequest.prototype.open;
    const originalSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function(method, url) {
        this._url = url;
        this._method = method;
        this._startTime = Date.now();
        return originalOpen.apply(this, arguments);
    };

    XMLHttpRequest.prototype.send = function() {
        this.addEventListener('loadend', () => {
            const duration = Date.now() - this._startTime;
            console.log(
                `%c[Ajax] %c${this._method} %c${this._url} %c${this.status} %c${duration}ms`,
                'color: #999',
                'color: #2196F3',
                'color: #333',
                this.status >= 200 && this.status < 300 ? 'color: #4CAF50' : 'color: #F44336',
                'color: #FF9800'
            );
        });
        return originalSend.apply(this, arguments);
    };
}

// 2. 使用浏览器 DevTools Network 面板
// - 筛选 XHR/Fetch 请求
// - 查看请求头、响应头、负载数据
// - 查看请求耗时瀑布图
// - 模拟慢速网络环境
```

---

> **参考资料：**
> - [MDN Web Docs - XMLHttpRequest](https://developer.mozilla.org/zh-CN/docs/Web/API/XMLHttpRequest)
> - [MDN Web Docs - Fetch API](https://developer.mozilla.org/zh-CN/docs/Web/API/Fetch_API)
> - [MDN Web Docs - CORS](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/CORS)
> - [MDN Web Docs - AbortController](https://developer.mozilla.org/zh-CN/docs/Web/API/AbortController)
> - [MDN Web Docs - navigator.sendBeacon](https://developer.mozilla.org/zh-CN/docs/Web/API/Navigator/sendBeacon)
> - [MDN Web Docs - SameSite Cookie](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/Set-Cookie/SameSite)
> - 《JavaScript 高级程序设计》（第 4 版）— Nicholas C. Zakas
> - RFC 6454 - The Web Origin Concept
> - RFC 9110 - HTTP Semantics