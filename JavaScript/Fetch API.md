# Fetch API 面试题集

> 本文档系统梳理 Fetch API 的核心知识点与常见面试题，涵盖基础概念、标准用法、错误处理、与传统 AJAX 的对比等方面，适合前端开发岗位面试复习使用。

---

## 目录

- [Fetch API 面试题集](#fetch-api-面试题集)
  - [目录](#目录)
  - [一、Fetch API 简介](#一fetch-api-简介)
  - [二、Fetch API 标准使用方法](#二fetch-api-标准使用方法)
    - [2.1 请求配置（Request Init）](#21-请求配置request-init)
    - [2.2 响应处理（Response）](#22-响应处理response)
    - [2.3 错误处理](#23-错误处理)
  - [三、Fetch API 与 AJAX 对比分析](#三fetch-api-与-ajax-对比分析)
    - [3.1 Fetch API vs XMLHttpRequest](#31-fetch-api-vs-xmlhttprequest)
    - [3.2 Fetch API 的优势](#32-fetch-api-的优势)
    - [3.3 Fetch API 的局限性](#33-fetch-api-的局限性)
    - [3.4 Fetch vs Axios 简单对比](#34-fetch-vs-axios-简单对比)
  - [四、面试题及详解](#四面试题及详解)
    - [题目 1：Fetch API 的基本使用流程](#题目-1fetch-api-的基本使用流程)
    - [题目 2：Response 对象的常用属性和方法](#题目-2response-对象的常用属性和方法)
    - [题目 3：Fetch 的请求配置项](#题目-3fetch-的请求配置项)
    - [题目 4：Fetch 的错误处理机制](#题目-4fetch-的错误处理机制)
    - [题目 5：Fetch 发送 POST 请求及 JSON 数据](#题目-5fetch-发送-post-请求及-json-数据)
    - [题目 6：Fetch 处理文件上传](#题目-6fetch-处理文件上传)
    - [题目 7：Fetch 中断请求（AbortController）](#题目-7fetch-中断请求abortcontroller)
    - [题目 8：Fetch 的跨域请求（CORS）处理](#题目-8fetch-的跨域请求cors处理)
    - [题目 9：Fetch 与 XMLHttpRequest 对比](#题目-9fetch-与-xmlhttprequest-对比)
    - [题目 10：Fetch 的兼容性及 Polyfill 方案](#题目-10fetch-的兼容性及-polyfill-方案)
    - [题目 11：Fetch 中的 Cookie 和凭证处理](#题目-11fetch-中的-cookie-和凭证处理)
    - [题目 12：Fetch 超时处理](#题目-12fetch-超时处理)
    - [题目 13：封装一个健壮的 Fetch 请求库](#题目-13封装一个健壮的-fetch-请求库)
    - [题目 14：Fetch 的 ReadableStream 与流式处理](#题目-14fetch-的-readablestream-与流式处理)
    - [题目 15：Fetch 与 Service Worker 的配合使用](#题目-15fetch-与-service-worker-的配合使用)
  - [附录：考点速查表](#附录考点速查表)

---

## 一、Fetch API 简介

Fetch API 是现代浏览器提供的一个全局 `fetch()` 方法，用于发起网络请求并获取资源。它基于 **Promise** 设计，提供了一种更简洁、更强大的方式来替代传统的 `XMLHttpRequest`。

**核心特性：**

| 特性 | 说明 |
|------|------|
| **Promise 驱动** | 基于 Promise 的异步编程模型，支持 `async/await` |
| **链式调用** | 请求和响应处理可通过 `.then()` 链式编排 |
| **Request / Response 对象** | 提供标准化的请求和响应对象 |
| **Headers 对象** | 便捷的请求头和响应头操作 API |
| **ReadableStream** | 支持流式读取响应体，便于处理大文件 |
| **跨域支持** | 内置 CORS 支持，通过 `mode` 配置控制 |
| **Service Worker 兼容** | 可在 Service Worker 中使用，实现离线缓存 |

**基本用法：**

```javascript
fetch(url)
  .then(response => {
    // 检查响应状态
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json(); // 解析 JSON 数据
  })
  .then(data => {
    console.log(data);
  })
  .catch(error => {
    console.error('请求失败:', error);
  });
```

**重要概念：** `fetch()` 返回的 Promise **仅在网络故障时 reject**（如断网、DNS 解析失败）。HTTP 错误状态码（如 404、500）不会导致 Promise reject，需要手动检查 `response.ok` 或 `response.status`。

---

## 二、Fetch API 标准使用方法

### 2.1 请求配置（Request Init）

`fetch()` 的第二个参数是一个配置对象，包含以下常用选项：

```javascript
fetch(url, {
  method: 'POST',                    // 请求方法：GET、POST、PUT、DELETE 等
  headers: {                         // 请求头
    'Content-Type': 'application/json',
    'Authorization': 'Bearer token123'
  },
  body: JSON.stringify({             // 请求体（GET/HEAD 请求不能有 body）
    name: 'Alice',
    age: 25
  }),
  mode: 'cors',                      // 跨域模式：cors、no-cors、same-origin
  credentials: 'include',            // 凭证：omit、same-origin、include
  cache: 'no-cache',                 // 缓存策略：default、no-store、reload 等
  redirect: 'follow',                // 重定向：follow、error、manual
  referrerPolicy: 'no-referrer',     // Referrer 策略
  signal: abortController.signal     // 用于中断请求的 AbortSignal
});
```

### 2.2 响应处理（Response）

```javascript
// Response 对象常用属性和方法
const response = await fetch(url);

// --- 属性 ---
response.ok          // boolean，状态码 200-299 时为 true
response.status      // number，HTTP 状态码（200、404、500 等）
response.statusText  // string，状态文本（'OK'、'Not Found' 等）
response.headers     // Headers 对象，响应头
response.url         // string，最终请求的 URL（跟随重定向后）
response.type        // string，响应类型：basic、cors、opaque 等
response.redirected  // boolean，是否经过了重定向

// --- 解析响应体的方法（均为异步 Promise） ---
await response.json()       // 解析为 JSON 对象
await response.text()       // 解析为纯文本
await response.blob()       // 解析为 Blob（二进制数据）
await response.arrayBuffer() // 解析为 ArrayBuffer
await response.formData()   // 解析为 FormData

// --- 注意：响应体只能被读取一次 ---
const data1 = await response.json(); // ✅ 成功
const data2 = await response.text(); // ❌ 报错：body already read
```

### 2.3 错误处理

```javascript
async function fetchWithErrorHandling(url, options = {}) {
  try {
    const response = await fetch(url, options);
    
    // 1. 检查 HTTP 状态码
    if (!response.ok) {
      // 尝试获取服务器返回的错误信息
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const errorBody = await response.json();
        errorMessage = errorBody.message || errorMessage;
      } catch (e) {
        // JSON 解析失败，使用默认错误信息
      }
      throw new Error(errorMessage);
    }
    
    return await response.json();
    
  } catch (error) {
    // 2. 区分网络错误和业务错误
    if (error.name === 'TypeError') {
      // 网络故障（断网、DNS 解析失败等）
      throw new Error('网络连接失败，请检查网络');
    }
    if (error.name === 'AbortError') {
      // 请求被中断
      throw new Error('请求已取消');
    }
    throw error; // 其他错误直接抛出
  }
}
```

---

## 三、Fetch API 与 AJAX 对比分析

### 3.1 Fetch API vs XMLHttpRequest

| 对比维度 | XMLHttpRequest | Fetch API |
|---------|---------------|-----------|
| **API 设计** | 事件驱动，回调式 | Promise 驱动，支持 `async/await` |
| **语法简洁性** | 繁琐，需多个事件监听 | 简洁，链式调用 |
| **响应处理** | `xhr.responseText` 字符串 | 内置 json()、blob() 等多种解析方法 |
| **请求/响应对象** | 无标准化对象 | Request / Response 标准对象 |
| **Headers 操作** | `xhr.setRequestHeader()` | `Headers` 对象，API 更丰富 |
| **流式处理** | 不支持 | 支持 ReadableStream |
| **Service Worker** | 不支持 | 完全支持 |
| **请求中断** | `xhr.abort()` | `AbortController.abort()` |
| **上传进度** | 支持 `xhr.upload.onprogress` | **不支持**（需自行实现） |
| **请求超时** | 内置 `xhr.timeout` 属性 | **不支持**（需自行封装） |
| **Cookie 控制** | 默认携带同源 Cookie | 默认不携带（需设置 `credentials`） |
| **错误捕获** | `onerror` 事件 | try/catch 或 `.catch()` |
| **浏览器兼容** | 所有浏览器 | IE 不支持（需 Polyfill） |

### 3.2 Fetch API 的优势

1. **Promise 驱动**：支持 `async/await`，避免回调地狱，代码可读性更高
2. **API 设计现代**：Request / Response / Headers 标准化对象，语义清晰
3. **流式处理**：基于 ReadableStream，支持逐块处理响应数据
4. **Service Worker 集成**：PWA 离线缓存的核心能力
5. **跨域控制**：`mode` 配置项提供更精细的跨域策略
6. **链式调用**：`.then()` 链式编排，数据处理流程清晰

### 3.3 Fetch API 的局限性

1. **不支持上传进度**：无法监听文件上传进度（需用 XMLHttpRequest 或自行实现）
2. **不支持请求超时**：没有内置 timeout 配置，需配合 `AbortController` + `setTimeout` 实现
3. **Cookie 默认不携带**：同源请求默认也不携带 Cookie，需显式设置 `credentials`
4. **不支持 JSONP**：无法用于跨域请求 JSONP 数据
5. **IE 不兼容**：IE 全系列不支持，需 Polyfill
6. **错误处理需手动**：HTTP 错误状态码不会自动 reject，需手动检查
7. **不能取消已发出的请求**：不像 Axios 有 CancelToken，需用 AbortController

### 3.4 Fetch vs Axios 简单对比

| 特性 | Fetch | Axios |
|------|-------|-------|
| 类型 | 浏览器原生 API | 第三方库 |
| 请求/响应拦截器 | 无（需自行封装） | 内置拦截器 |
| 自动 JSON 解析 | 需手动 `.json()` | 自动解析 |
| 请求超时 | 无内置 | 内置 `timeout` 配置 |
| 上传进度 | 不支持 | 支持 |
| 取消请求 | AbortController | CancelToken / AbortController |
| 并发请求 | 需 Promise.all | `axios.all` / `axios.spread` |
| 体积 | 0（浏览器内置） | ~14KB (gzip) |

---

## 四、面试题及详解

### 题目 1：Fetch API 的基本使用流程

**题目描述：** 请写出使用 Fetch API 发送 GET 请求并解析 JSON 响应数据的完整代码。

**考察知识点：** Fetch 基础 | **能力等级：** 初级

**参考答案：**

```javascript
// 方式 1：Promise 链式调用
function fetchUsers() {
  fetch('https://api.example.com/users')
    .then(response => {
      // 检查 HTTP 状态码是否正常
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return response.json(); // 解析 JSON
    })
    .then(data => {
      console.log('获取到的用户数据:', data);
      // 渲染到页面...
    })
    .catch(error => {
      console.error('请求失败:', error.message);
    });
}

// 方式 2：async/await（推荐）
async function fetchUsersAsync() {
  try {
    const response = await fetch('https://api.example.com/users');
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('获取到的用户数据:', data);
    return data;
    
  } catch (error) {
    console.error('请求失败:', error.message);
    throw error; // 向上层传递错误
  }
}
```

**关键点：**
- `fetch()` 返回 Promise，`response.json()` 也返回 Promise
- 必须检查 `response.ok` 判断 HTTP 状态码
- 网络错误才会进入 `catch`，HTTP 错误（404/500）不会

**评分标准：**
- 正确使用 `.then()` 或 `async/await`（4 分）
- 检查 `response.ok` 处理 HTTP 错误（4 分）
- 正确使用 `.catch()` 或 `try/catch`（2 分）

---

### 题目 2：Response 对象的常用属性和方法

**题目描述：** 请介绍 Fetch API 中 Response 对象的常用属性和方法，并说明如何根据响应头的 `Content-Type` 选择不同的解析方式。

**考察知识点：** Response 对象 | **能力等级：** 初级

**参考答案：**

**Response 对象常用属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `response.ok` | boolean | 状态码在 200-299 之间时为 true |
| `response.status` | number | HTTP 状态码 |
| `response.statusText` | string | 状态码对应的文本 |
| `response.headers` | Headers | 响应头对象 |
| `response.url` | string | 最终请求的 URL（含重定向后的地址） |
| `response.type` | string | 响应类型：basic / cors / opaque / opaqueredirect |
| `response.body` | ReadableStream | 响应体的流对象 |
| `response.redirected` | boolean | 是否经过了重定向 |

**根据 Content-Type 选择解析方式：**

```javascript
async function parseResponseByContentType(url) {
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`请求失败: ${response.status}`);
  }
  
  // 获取 Content-Type 响应头
  const contentType = response.headers.get('Content-Type') || '';
  
  if (contentType.includes('application/json')) {
    return await response.json();
  }
  
  if (contentType.includes('text/')) {
    return await response.text();
  }
  
  if (contentType.includes('image/') || contentType.includes('application/octet-stream')) {
    const blob = await response.blob();
    return URL.createObjectURL(blob); // 创建可用的 URL
  }
  
  if (contentType.includes('multipart/form-data')) {
    return await response.formData();
  }
  
  // 默认尝试解析为 JSON，失败则返回文本
  try {
    return await response.json();
  } catch {
    return await response.text();
  }
}
```

**注意：响应体只能被读取一次，重复读取会报错。**

```javascript
// ❌ 错误：重复读取响应体
const data = await response.json();
const text = await response.text(); // TypeError: body already read

// ✅ 正确：需要多次使用，先 clone
const clone = response.clone();
const data = await response.json();
const text = await clone.text();
```

**评分标准：**
- 列举出至少 5 个 Response 属性（4 分）
- 根据 Content-Type 选择合适的解析方法（3 分）
- 说明 clone() 的使用场景（3 分）

---

### 题目 3：Fetch 的请求配置项

**题目描述：** 请详细说明 `fetch()` 第二个参数（init 对象）的常用配置项及其作用，并写一个完整的 POST 请求示例。

**考察知识点：** 请求配置 | **能力等级：** 初级

**参考答案：**

```javascript
// fetch(url, init) 的 init 配置项详解
fetch('https://api.example.com/data', {
  // ---- 请求方法 ----
  method: 'POST',
  // 取值: GET、POST、PUT、DELETE、PATCH、HEAD、OPTIONS

  // ---- 请求头 ----
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJhbGciOi...',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json'
  },
  // 也可以是 Headers 对象:
  // headers: new Headers({ 'Content-Type': 'application/json' })

  // ---- 请求体 ----
  body: JSON.stringify({
    name: 'Alice',
    email: 'alice@example.com',
    age: 25
  }),
  // 注意: GET 和 HEAD 请求不能有 body
  // body 类型: string、FormData、Blob、ArrayBuffer、URLSearchParams、ReadableStream

  // ---- 跨域模式 ----
  mode: 'cors',
  // cors: 允许跨域（默认）
  // no-cors: 限制跨域（只能发送简单请求，响应不可读）
  // same-origin: 禁止跨域
  // navigate: 导航模式

  // ---- 凭证（Cookie） ----
  credentials: 'same-origin',
  // omit: 不发送凭证
  // same-origin: 同源时发送（默认）
  // include: 始终发送（跨域也发送）

  // ---- 缓存策略 ----
  cache: 'default',
  // default: 遵循浏览器默认缓存策略
  // no-store: 不缓存
  // reload: 强制从服务器获取
  // no-cache: 发送条件请求验证缓存
  // force-cache: 强制使用缓存
  // only-if-cached: 仅使用缓存

  // ---- 重定向策略 ----
  redirect: 'follow',
  // follow: 自动跟随重定向（默认）
  // error: 遇到重定向抛错
  // manual: 手动处理重定向

  // ---- Referrer 策略 ----
  referrerPolicy: 'strict-origin-when-cross-origin',

  // ---- 请求中断 ----
  signal: abortController.signal, // 配合 AbortController 使用

  // ---- 完整性校验 ----
  integrity: 'sha256-...' // 子资源完整性校验
});
```

**完整 POST 请求示例：**

```javascript
async function createUser(userData) {
  try {
    const response = await fetch('https://api.example.com/users', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify(userData)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || `创建失败: ${response.status}`);
    }

    // 201 Created 通常返回新创建的资源
    const newUser = await response.json();
    return newUser;

  } catch (error) {
    console.error('创建用户失败:', error);
    throw error;
  }
}

// 调用
createUser({ name: 'Bob', email: 'bob@test.com' })
  .then(user => console.log('创建成功:', user))
  .catch(err => console.error(err));
```

**评分标准：**
- 列举 5 个以上配置项并说明作用（5 分）
- 正确编写 POST 请求示例（3 分）
- 说明 body 的适用类型（2 分）

---

### 题目 4：Fetch 的错误处理机制

**题目描述：** 请说明 Fetch API 的错误处理机制：哪些情况会进入 `.catch()`，哪些不会？如何正确处理 HTTP 错误状态码（如 404、500）？请写出一个健壮的错误处理方案。

**考察知识点：** 错误处理 | **能力等级：** 中级

**参考答案：**

**核心原则：Fetch 的 Promise 仅在网络层面的错误时 reject，HTTP 层面的错误不会 reject。**

```javascript
// 哪些情况会进入 .catch()（网络错误）：
// 1. 网络断开（断网）
// 2. DNS 解析失败（域名不存在）
// 3. 请求被 AbortController 取消
// 4. CORS 策略阻止（跨域请求被浏览器拦截）
// 5. SSL/TLS 证书错误
// 6. 请求超时（自行封装的）

// 哪些情况不会进入 .catch()（HTTP 错误）：
// 1. 404 Not Found
// 2. 500 Internal Server Error
// 3. 403 Forbidden
// 4. 401 Unauthorized
// 5. 任何 HTTP 响应（即使是非 2xx 状态码）
```

**健壮的错误处理方案：**

```javascript
/**
 * 自定义错误类：区分不同的错误类型
 */
class HttpError extends Error {
  constructor(message, status, response) {
    super(message);
    this.name = 'HttpError';
    this.status = status;
    this.response = response;
  }
}

class NetworkError extends Error {
  constructor(message, originalError) {
    super(message);
    this.name = 'NetworkError';
    this.originalError = originalError;
  }
}

class TimeoutError extends Error {
  constructor(message) {
    super(message);
    this.name = 'TimeoutError';
  }
}

/**
 * 健壮的 Fetch 封装
 */
async function robustFetch(url, options = {}) {
  const { timeout = 10000, ...fetchOptions } = options;
  
  // 超时控制
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, {
      ...fetchOptions,
      signal: controller.signal
    });
    
    // 处理 HTTP 错误
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      
      // 尝试解析服务器返回的错误详情
      try {
        const errorBody = await response.json();
        errorMessage = errorBody.message || errorBody.error || errorMessage;
      } catch {
        // 响应体不是 JSON，使用默认错误信息
      }
      
      throw new HttpError(errorMessage, response.status, response);
    }
    
    return response;
    
  } catch (error) {
    // 分类处理错误
    if (error instanceof HttpError) {
      throw error; // 直接抛出 HTTP 错误
    }
    
    if (error.name === 'AbortError') {
      if (controller.signal.aborted && !timeoutId._cleared) {
        throw new TimeoutError(`请求超时 (${timeout}ms)`);
      }
      throw new Error('请求已被取消');
    }
    
    // 网络错误（TypeError: Failed to fetch）
    if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
      throw new NetworkError('网络连接失败，请检查网络设置', error);
    }
    
    throw error;
    
  } finally {
    clearTimeout(timeoutId);
  }
}

// 使用示例
async function getUserData(userId) {
  try {
    const response = await robustFetch(`/api/users/${userId}`, {
      timeout: 5000
    });
    return await response.json();
    
  } catch (error) {
    switch (error.name) {
      case 'HttpError':
        // HTTP 错误：根据状态码处理
        if (error.status === 401) {
          redirectToLogin();
        } else if (error.status === 404) {
          showNotFound();
        } else if (error.status >= 500) {
          showServerError();
        }
        break;
      case 'NetworkError':
        showNetworkError();
        break;
      case 'TimeoutError':
        showTimeoutError();
        break;
      default:
        showUnknownError(error.message);
    }
    throw error;
  }
}
```

**评分标准：**
- 准确区分网络错误和 HTTP 错误（4 分）
- 定义自定义错误类分类处理（3 分）
- 实现超时控制和错误恢复逻辑（3 分）

---

### 题目 5：Fetch 发送 POST 请求及 JSON 数据

**题目描述：** 请使用 Fetch API 实现一个完整的用户登录功能，包括发送 POST 请求、携带 JSON 请求体、处理成功和失败响应，并妥善管理 Token 存储。

**考察知识点：** POST 请求、Token 管理 | **能力等级：** 中级

**参考答案：**

```javascript
// ---- Auth 服务 ----
class AuthService {
  constructor() {
    this.baseURL = 'https://api.example.com';
    this.tokenKey = 'auth_token';
    this.refreshTokenKey = 'refresh_token';
  }
  
  // 获取存储的 Token
  getToken() {
    return localStorage.getItem(this.tokenKey);
  }
  
  getRefreshToken() {
    return localStorage.getItem(this.refreshTokenKey);
  }
  
  // 存储 Token
  setTokens(accessToken, refreshToken) {
    localStorage.setItem(this.tokenKey, accessToken);
    if (refreshToken) {
      localStorage.setItem(this.refreshTokenKey, refreshToken);
    }
  }
  
  // 清除 Token
  clearTokens() {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.refreshTokenKey);
  }
  
  /**
   * 用户登录
   */
  async login(username, password) {
    try {
      const response = await fetch(`${this.baseURL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });
      
      // 解析响应
      const data = await response.json();
      
      if (!response.ok) {
        throw {
          status: response.status,
          message: data.message || '登录失败',
          data: data
        };
      }
      
      // 存储 Token
      this.setTokens(data.access_token, data.refresh_token);
      
      return {
        success: true,
        user: data.user,
        token: data.access_token
      };
      
    } catch (error) {
      if (error.status) {
        // 服务器返回的错误
        switch (error.status) {
          case 401:
            throw new Error('用户名或密码错误');
          case 429:
            throw new Error('登录尝试过于频繁，请稍后再试');
          case 403:
            throw new Error('账号已被禁用');
          default:
            throw new Error(error.message || '登录失败');
        }
      }
      // 网络错误
      throw new Error('网络连接失败，请检查网络');
    }
  }
  
  /**
   * 刷新 Token
   */
  async refreshAccessToken() {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new Error('无刷新令牌');
    }
    
    const response = await fetch(`${this.baseURL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken })
    });
    
    if (!response.ok) {
      this.clearTokens();
      throw new Error('Token 刷新失败，请重新登录');
    }
    
    const data = await response.json();
    this.setTokens(data.access_token, data.refresh_token);
    return data.access_token;
  }
  
  /**
   * 带认证的请求封装
   */
  async authenticatedRequest(endpoint, options = {}) {
    const token = this.getToken();
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    };
    
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers
      }
    });
    
    // Token 过期，尝试刷新
    if (response.status === 401) {
      try {
        const newToken = await this.refreshAccessToken();
        // 重试请求
        return await fetch(`${this.baseURL}${endpoint}`, {
          ...options,
          headers: {
            ...defaultHeaders,
            'Authorization': `Bearer ${newToken}`,
            ...options.headers
          }
        });
      } catch {
        window.location.href = '/login';
        throw new Error('登录已过期，请重新登录');
      }
    }
    
    return response;
  }
  
  /**
   * 退出登录
   */
  logout() {
    this.clearTokens();
    window.location.href = '/login';
  }
}

// ---- 使用示例 ----
const authService = new AuthService();

// 登录
document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  
  try {
    const result = await authService.login(username, password);
    console.log('登录成功:', result.user);
    window.location.href = '/dashboard';
  } catch (error) {
    showErrorToast(error.message);
  }
});
```

**评分标准：**
- 正确发送 POST 请求并设置 JSON 请求体（3 分）
- 处理不同的 HTTP 错误状态码（3 分）
- 实现 Token 管理和自动刷新机制（4 分）

---

### 题目 6：Fetch 处理文件上传

**题目描述：** 请使用 Fetch API 实现文件上传功能，包括单文件上传、多文件上传，并说明如何显示上传进度（提示：Fetch 本身不支持进度监听，需说明替代方案）。

**考察知识点：** 文件上传、FormData | **能力等级：** 中级

**参考答案：**

```javascript
// ---- 单文件上传 ----
async function uploadSingleFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  // 可附加额外字段
  formData.append('category', 'document');
  formData.append('description', '这是一个测试文件');

  try {
    const response = await fetch('https://api.example.com/upload', {
      method: 'POST',
      body: formData
      // 注意：使用 FormData 时不要手动设置 Content-Type！
      // 浏览器会自动设置 Content-Type: multipart/form-data; boundary=...
    });
    
    if (!response.ok) {
      throw new Error(`上传失败: ${response.status}`);
    }
    
    const result = await response.json();
    console.log('上传成功:', result.url);
    return result;
    
  } catch (error) {
    console.error('上传失败:', error);
    throw error;
  }
}

// ---- 多文件上传 ----
async function uploadMultipleFiles(files) {
  const formData = new FormData();
  
  // 方式 1：逐个添加（字段名相同，服务器接收为数组）
  for (const file of files) {
    formData.append('files', file);
  }
  
  // 方式 2：添加额外数据
  formData.append('folder_id', '12345');

  try {
    const response = await fetch('https://api.example.com/upload/multiple', {
      method: 'POST',
      body: formData
    });
    
    return await response.json();
    
  } catch (error) {
    console.error('批量上传失败:', error);
    throw error;
  }
}

// ---- 上传进度实现（Fetch 不支持 xhr.upload.onprogress） ----
// 方案 1：使用 XMLHttpRequest 实现上传进度
function uploadWithProgress(file, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append('file', file);
    
    // 监听上传进度
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        const percent = Math.round((e.loaded / e.total) * 100);
        onProgress(percent);
      }
    });
    
    // 监听完成
    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        reject(new Error(`上传失败: ${xhr.status}`));
      }
    });
    
    xhr.addEventListener('error', () => reject(new Error('网络错误')));
    xhr.addEventListener('abort', () => reject(new Error('上传已取消')));
    
    xhr.open('POST', 'https://api.example.com/upload');
    xhr.send(formData);
  });
}

// 方案 2：使用 ReadableStream 分块上传（大文件场景）
async function uploadWithChunkedStream(file, chunkSize = 1024 * 1024) {
  const totalChunks = Math.ceil(file.size / chunkSize);
  
  for (let i = 0; i < totalChunks; i++) {
    const start = i * chunkSize;
    const end = Math.min(start + chunkSize, file.size);
    const chunk = file.slice(start, end);
    
    const formData = new FormData();
    formData.append('chunk', chunk);
    formData.append('chunkIndex', i);
    formData.append('totalChunks', totalChunks);
    formData.append('fileName', file.name);
    
    const response = await fetch('https://api.example.com/upload/chunk', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`分块 ${i + 1}/${totalChunks} 上传失败`);
    }
    
    // 计算进度
    const progress = Math.round(((i + 1) / totalChunks) * 100);
    console.log(`上传进度: ${progress}%`);
  }
  
  // 通知服务器合并分块
  await fetch('https://api.example.com/upload/merge', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fileName: file.name, totalChunks })
  });
}

// ---- 文件上传前的校验 ----
function validateFile(file) {
  const MAX_SIZE = 10 * 1024 * 1024; // 10MB
  const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'];
  
  if (file.size > MAX_SIZE) {
    throw new Error(`文件大小不能超过 ${MAX_SIZE / 1024 / 1024}MB`);
  }
  
  if (!ALLOWED_TYPES.includes(file.type)) {
    throw new Error(`不支持的文件类型: ${file.type}`);
  }
  
  return true;
}

// ---- 完整使用示例 ----
document.getElementById('uploadBtn').addEventListener('click', async () => {
  const fileInput = document.getElementById('fileInput');
  const file = fileInput.files[0];
  
  if (!file) {
    alert('请选择文件');
    return;
  }
  
  try {
    validateFile(file);
    
    const result = await uploadWithProgress(file, (percent) => {
      document.getElementById('progressBar').style.width = `${percent}%`;
      document.getElementById('progressText').textContent = `${percent}%`;
    });
    
    console.log('上传成功:', result);
  } catch (error) {
    alert(error.message);
  }
});
```

**评分标准：**
- 正确使用 FormData 上传文件（4 分）
- 说明 Fetch 不支持进度监听及替代方案（3 分）
- 实现分块上传和文件校验（3 分）

---

### 题目 7：Fetch 中断请求（AbortController）

**题目描述：** 请说明如何使用 AbortController 中断 Fetch 请求，并实现一个场景：用户输入搜索关键词时，自动取消上一次未完成的请求（防抖搜索）。

**考察知识点：** AbortController、请求取消 | **能力等级：** 中级

**参考答案：**

**AbortController 原理：**

```javascript
// 基本用法
const controller = new AbortController();

fetch('https://api.example.com/data', {
  signal: controller.signal  // 传入 signal
});

// 中断请求
controller.abort(); // 请求会被取消，Promise reject 并抛出 AbortError

// 检查是否已被中断
console.log(controller.signal.aborted); // true
```

**防抖搜索实现：**

```javascript
/**
 * 搜索框防抖 + 自动取消上一次请求
 */
class SearchController {
  constructor() {
    this.abortController = null;  // 当前的 AbortController
    this.debounceTimer = null;    // 防抖计时器
    this.DEBOUNCE_DELAY = 300;    // 防抖延迟（毫秒）
  }
  
  /**
   * 执行搜索
   */
  async search(keyword) {
    // 取消上一次请求
    if (this.abortController) {
      this.abortController.abort();
      console.log('已取消上一次搜索请求');
    }
    
    // 创建新的 AbortController
    this.abortController = new AbortController();
    const currentController = this.abortController;
    
    // 空关键词不搜索
    if (!keyword.trim()) {
      return [];
    }
    
    try {
      const response = await fetch(
        `https://api.example.com/search?q=${encodeURIComponent(keyword)}`,
        { signal: currentController.signal }
      );
      
      if (!response.ok) {
        throw new Error(`搜索失败: ${response.status}`);
      }
      
      const data = await response.json();
      
      // 确保是最新的请求结果（防止竞态条件）
      if (currentController.signal.aborted) {
        return; // 请求已被取消，丢弃结果
      }
      
      return data.results;
      
    } catch (error) {
      // AbortError 说明请求被取消，不需要处理
      if (error.name === 'AbortError') {
        console.log('请求已取消');
        return [];
      }
      throw error;
    }
  }
  
  /**
   * 处理输入事件（防抖 + 取消）
   */
  handleInput(value) {
    // 清除上一次的防抖计时器
    clearTimeout(this.debounceTimer);
    
    // 设置新的防抖计时器
    this.debounceTimer = setTimeout(() => {
      this.search(value);
    }, this.DEBOUNCE_DELAY);
  }
  
  /**
   * 销毁：清理所有资源
   */
  destroy() {
    if (this.abortController) {
      this.abortController.abort();
    }
    clearTimeout(this.debounceTimer);
  }
}

// ---- 使用示例 ----
const searchCtrl = new SearchController();

const searchInput = document.getElementById('searchInput');
const resultsContainer = document.getElementById('results');

// 方式 1：使用防抖包装
searchInput.addEventListener('input', (e) => {
  searchCtrl.handleInput(e.target.value);
});

// 方式 2：使用通用 abortableFetch 封装
function createAbortableFetch() {
  let controller = null;
  
  const abortableFetch = async (url, options = {}) => {
    // 取消上一次请求
    if (controller) {
      controller.abort();
    }
    
    controller = new AbortController();
    
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal
      });
      return response;
    } catch (error) {
      if (error.name === 'AbortError') {
        return null; // 请求被取消，返回 null
      }
      throw error;
    }
  };
  
  abortableFetch.abort = () => {
    if (controller) {
      controller.abort();
    }
  };
  
  return abortableFetch;
}

// 使用通用封装
const fetchSearch = createAbortableFetch();

searchInput.addEventListener('input', async (e) => {
  const keyword = e.target.value.trim();
  if (!keyword) return;
  
  const response = await fetchSearch(
    `https://api.example.com/search?q=${encodeURIComponent(keyword)}`
  );
  
  if (response) {
    const data = await response.json();
    renderResults(data.results);
  }
});
```

**AbortController 的其他用途：**

```javascript
// 1. 同时取消多个请求
const controller = new AbortController();

fetch('/api/a', { signal: controller.signal });
fetch('/api/b', { signal: controller.signal });
fetch('/api/c', { signal: controller.signal });

controller.abort(); // 三个请求同时取消

// 2. 设置超时自动取消
function fetchWithTimeout(url, timeout = 5000) {
  const controller = new AbortController();
  setTimeout(() => controller.abort(), timeout);
  return fetch(url, { signal: controller.signal });
}

// 3. 组件卸载时取消请求（React 示例）
useEffect(() => {
  const controller = new AbortController();
  
  fetch('/api/data', { signal: controller.signal })
    .then(res => res.json())
    .then(data => setData(data))
    .catch(err => {
      if (err.name !== 'AbortError') {
        console.error(err);
      }
    });
  
  return () => controller.abort(); // 组件卸载时取消请求
}, []);
```

**评分标准：**
- 正确使用 AbortController 中断请求（3 分）
- 实现防抖搜索 + 请求取消（4 分）
- 展示 AbortController 的其他实用场景（3 分）

---

### 题目 8：Fetch 的跨域请求（CORS）处理

**题目描述：** 请说明 Fetch API 中跨域请求的 CORS 机制，解释 `mode` 配置项的不同取值，以及 `简单请求` 与 `预检请求` 的区别。同时说明如何解决开发中的跨域问题。

**考察知识点：** CORS、跨域 | **能力等级：** 中级

**参考答案：**

**CORS（Cross-Origin Resource Sharing）核心概念：**

```javascript
// Fetch 的 mode 配置项
fetch(url, {
  mode: 'cors'        // 默认值，允许跨域（遵循 CORS 协议）
  // mode: 'no-cors'  // 限制跨域（只能发送简单请求，响应不可读）
  // mode: 'same-origin' // 禁止跨域，只能同源请求
});
```

**简单请求 vs 预检请求：**

| 条件 | 简单请求 | 预检请求 |
|------|---------|---------|
| **请求方法** | GET、HEAD、POST | PUT、DELETE、PATCH 等 |
| **Content-Type** | `text/plain`、`multipart/form-data`、`application/x-www-form-urlencoded` | `application/json` 等 |
| **自定义头部** | 仅限安全头部 | 含自定义头部（如 Authorization） |
| **请求次数** | 1 次 | 2 次（OPTIONS + 实际请求） |
| **ReadableStream** | 不可用 | 可用 |

```javascript
// 简单请求：直接发送，浏览器自动添加 Origin 头
fetch('https://api.example.com/data', {
  method: 'GET',
  mode: 'cors'
});

// 预检请求：先发送 OPTIONS 请求，服务器允许后才发送实际请求
fetch('https://api.example.com/users', {
  method: 'DELETE',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer token123'
  },
  mode: 'cors'
});
// 浏览器先发送: OPTIONS /users
// 服务器返回: Access-Control-Allow-Methods: DELETE
//            Access-Control-Allow-Headers: Content-Type, Authorization
// 然后发送: DELETE /users
```

**服务端 CORS 配置（Express 示例）：**

```javascript
const express = require('express');
const cors = require('cors');
const app = express();

// 方式 1：使用 cors 中间件
app.use(cors({
  origin: 'https://myapp.com',     // 允许的源
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,                 // 允许携带 Cookie
  maxAge: 86400                      // 预检请求缓存时间（秒）
}));

// 方式 2：手动设置响应头
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', 'https://myapp.com');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  
  // 预检请求直接返回 204
  if (req.method === 'OPTIONS') {
    return res.sendStatus(204);
  }
  next();
});
```

**开发中解决跨域的方法：**

```javascript
// 方案 1：开发环境代理（Vite 配置）
// vite.config.js
export default {
  server: {
    proxy: {
      '/api': {
        target: 'https://api.example.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
};

// 方案 2：Webpack DevServer 代理
// webpack.config.js
module.exports = {
  devServer: {
    proxy: {
      '/api': 'https://api.example.com'
    }
  }
};

// 方案 3：Nginx 反向代理
// nginx.conf
// location /api/ {
//   proxy_pass https://api.example.com/;
// }

// 方案 4：Chrome 插件（临时调试）
// 安装 "Allow CORS" 插件，仅开发调试用
```

**no-cors 模式说明：**

```javascript
// no-cors 模式：只能发送"简单请求"
fetch('https://other-domain.com/data', { mode: 'no-cors' })
  .then(response => {
    console.log(response.type); // 'opaque'
    // response.ok 为 false
    // 无法读取 response.body
    // 无法读取 response.headers
    // 适用场景：发送日志、埋点等不需要读取响应的场景
  });
```

**评分标准：**
- 解释 CORS 机制和 mode 配置项（3 分）
- 区分简单请求和预检请求（3 分）
- 说明至少 3 种跨域解决方案（4 分）

---

### 题目 9：Fetch 与 XMLHttpRequest 对比

**题目描述：** 请从 API 设计、错误处理、请求取消、上传进度、Cookie 处理等方面对比 Fetch API 和 XMLHttpRequest，并说明各自的适用场景。

**考察知识点：** 技术选型、对比分析 | **能力等级：** 中级

**参考答案：**

**核心差异对比：**

```javascript
// ===== 相同功能的不同实现 =====

// 1. 发送 GET 请求
// XMLHttpRequest
const xhr = new XMLHttpRequest();
xhr.open('GET', 'https://api.example.com/data');
xhr.onload = () => {
  if (xhr.status >= 200 && xhr.status < 300) {
    const data = JSON.parse(xhr.responseText);
    console.log(data);
  }
};
xhr.onerror = () => console.error('网络错误');
xhr.send();

// Fetch
fetch('https://api.example.com/data')
  .then(res => {
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  })
  .then(data => console.log(data))
  .catch(err => console.error(err));

// 2. 发送 POST 请求（JSON）
// XMLHttpRequest
const xhr2 = new XMLHttpRequest();
xhr2.open('POST', 'https://api.example.com/users');
xhr2.setRequestHeader('Content-Type', 'application/json');
xhr2.onload = () => console.log(xhr2.responseText);
xhr2.send(JSON.stringify({ name: 'Alice' }));

// Fetch
fetch('https://api.example.com/users', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'Alice' })
})
  .then(res => res.json())
  .then(data => console.log(data));

// 3. 请求中断
// XMLHttpRequest
xhr.abort(); // 直接调用

// Fetch
const controller = new AbortController();
fetch(url, { signal: controller.signal });
controller.abort(); // 通过 AbortController

// 4. 上传进度
// XMLHttpRequest: 支持
xhr.upload.addEventListener('progress', (e) => {
  const percent = (e.loaded / e.total) * 100;
  console.log(`上传进度: ${percent}%`);
});

// Fetch: 不支持（需 XMLHttpRequest 或分块上传实现）

// 5. Cookie / 凭证
// XMLHttpRequest: 默认携带同源 Cookie
xhr.withCredentials = true; // 跨域也携带

// Fetch: 默认不携带
fetch(url, { credentials: 'include' }); // 需要显式设置

// 6. 超时设置
// XMLHttpRequest: 内置
xhr.timeout = 5000;
xhr.ontimeout = () => console.error('请求超时');

// Fetch: 无内置，需自行实现
const ctrl = new AbortController();
setTimeout(() => ctrl.abort(), 5000);
fetch(url, { signal: ctrl.signal });
```

**详细对比表：**

| 特性 | XMLHttpRequest | Fetch API |
|------|---------------|-----------|
| 基础 API 风格 | 事件回调 | Promise |
| 语法简洁性 | 繁琐 | 简洁 |
| async/await 支持 | 需要封装 | 原生支持 |
| 请求/响应对象 | 无标准化 | Request / Response |
| 流式读取 | 不支持 | ReadableStream |
| Service Worker | 不支持 | 支持 |
| 下载进度 | `onprogress` 事件 | `response.body.getReader()` |
| 上传进度 | `upload.onprogress` | **不支持** |
| 请求超时 | `timeout` 属性 | 需 AbortController + setTimeout |
| Cookie 默认策略 | 携带同源 Cookie | 不携带 |
| 跨域控制 | `withCredentials` | `mode` + `credentials` |
| 取消请求 | `abort()` | `AbortController.abort()` |
| 浏览器兼容 | 所有浏览器 | IE 不支持 |
| 错误处理 | `onerror` / `onabort` / `ontimeout` | try/catch（仅网络错误） |

**适用场景选择：**

| 场景 | 推荐技术 | 原因 |
|------|---------|------|
| 现代 Web 应用 | **Fetch** | 简洁、Promise 原生支持 |
| 需要上传进度 | **XMLHttpRequest** | Fetch 不支持 |
| 需要下载进度 | 两者均可 | Fetch 需用 ReadableStream |
| PWA / Service Worker | **Fetch** | 唯一选择 |
| 需要兼容 IE | **XMLHttpRequest** | Fetch 不支持 IE |
| 旧项目维护 | **XMLHttpRequest** | 保持一致性 |
| 简单请求（GET/POST） | **Fetch** | 代码更简洁 |

**评分标准：**
- 从 5 个以上维度对比两种技术（5 分）
- 给出代码示例对比（3 分）
- 说明各自的适用场景（2 分）

---

### 题目 10：Fetch 的兼容性及 Polyfill 方案

**题目描述：** 请说明 Fetch API 的浏览器兼容性情况，以及如何在项目中引入 Polyfill 方案来支持不兼容的浏览器（如 IE）。同时说明使用 Polyfill 后有哪些功能限制。

**考察知识点：** 兼容性、Polyfill | **能力等级：** 中级

**参考答案：**

**浏览器兼容性：**

| 浏览器 | 最低支持版本 | 说明 |
|--------|------------|------|
| Chrome | 42+ | 完全支持 |
| Firefox | 39+ | 完全支持 |
| Safari | 10.1+ | 完全支持 |
| Edge | 14+ | 完全支持 |
| IE | **不支持** | 所有版本均不支持 |
| Opera | 29+ | 完全支持 |
| iOS Safari | 10.3+ | 完全支持 |
| Android Chrome | 所有版本 | 完全支持 |

**Polyfill 方案：**

```javascript
// 方案 1：使用 whatwg-fetch（最常用）
// 安装：npm install whatwg-fetch
import 'whatwg-fetch'; // 在入口文件顶部引入

// 或使用 CDN
// <script src="https://cdn.jsdelivr.net/npm/whatwg-fetch@3.6.20/dist/fetch.umd.min.js"></script>

// 方案 2：使用 unfetch（更轻量，~1KB）
// 安装：npm install unfetch
import fetch from 'unfetch';

// 方案 3：使用 axios（完全替代方案）
// 内置兼容性处理，无需 Polyfill
import axios from 'axios';

// 方案 4：按需加载 Polyfill（条件加载）
// 仅在浏览器不支持时加载
if (!window.fetch) {
  // 动态加载 Polyfill
  const script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/npm/whatwg-fetch/dist/fetch.umd.min.js';
  document.head.appendChild(script);
}

// 或使用更现代的方式
(async () => {
  if (!window.fetch) {
    await import('whatwg-fetch');
  }
  // 正常使用 fetch
})();
```

**Polyfill 后的功能限制：**

```javascript
// 1. ReadableStream 不支持（whatwg-fetch 不支持流式读取）
// 以下代码在 Polyfill 环境下不可用：
const response = await fetch(url);
const reader = response.body.getReader(); // ❌ Polyfill 不支持

// 2. AbortController 不支持（需要额外 Polyfill）
// 安装：npm install abortcontroller-polyfill
import 'abortcontroller-polyfill/dist/abortcontroller-polyfill-only';

// 3. 部分 Headers 方法不支持
// Headers.entries()、Headers.keys()、Headers.values() 在 IE 中不可用

// 4. Response.redirect() 静态方法不支持
// const response = Response.redirect(url, 301); // ❌

// 5. 部分 Request 构造选项不支持
// referrerPolicy、integrity 等在 Polyfill 中可能无效
```

**完整的兼容性检测与 Polyfill 方案：**

```javascript
/**
 * 检测 Fetch API 支持情况
 */
function detectFetchSupport() {
  const features = {
    fetch: typeof window.fetch === 'function',
    headers: typeof window.Headers === 'function',
    request: typeof window.Request === 'function',
    response: typeof window.Response === 'function',
    abortController: typeof window.AbortController === 'function',
    readableStream: typeof window.ReadableStream === 'function'
  };
  
  console.table(features);
  return features;
}

/**
 * 按需加载 Polyfill
 */
async function ensureFetchSupport() {
  const features = detectFetchSupport();
  
  if (!features.fetch) {
    await import('whatwg-fetch');
    console.log('已加载 Fetch Polyfill');
  }
  
  if (!features.abortController) {
    await import('abortcontroller-polyfill/dist/abortcontroller-polyfill-only');
    console.log('已加载 AbortController Polyfill');
  }
  
  // 如果 ReadableStream 不支持，使用降级方案
  if (!features.readableStream) {
    console.warn('ReadableStream 不可用，流式处理将降级为一次性读取');
  }
}

// 应用启动时执行
ensureFetchSupport().then(() => {
  // 安全使用 Fetch API
  fetch('/api/data').then(res => res.json()).then(console.log);
});
```

**Webpack / Vite 配置 Polyfill：**

```javascript
// webpack.config.js
module.exports = {
  entry: [
    'whatwg-fetch',  // 确保在所有代码之前加载
    './src/index.js'
  ]
};

// vite.config.js（使用 @vitejs/plugin-legacy）
import legacy from '@vitejs/plugin-legacy';

export default {
  plugins: [
    legacy({
      targets: ['ie >= 11'],
      polyfills: ['es.promise', 'es.fetch']
    })
  ]
};
```

**评分标准：**
- 说明 Fetch API 的浏览器兼容性（3 分）
- 给出至少 2 种 Polyfill 方案（3 分）
- 说明 Polyfill 后的功能限制（4 分）

---

### 题目 11：Fetch 中的 Cookie 和凭证处理

**题目描述：** 请说明 Fetch API 中 `credentials` 配置项的作用，对比三种取值（omit、same-origin、include）的行为差异，并说明跨域请求携带 Cookie 时前后端分别需要如何配置。

**考察知识点：** Cookie、凭证、跨域 | **能力等级：** 中级

**参考答案：**

**credentials 配置项：**

| 取值 | 同源请求 | 跨域请求 | 说明 |
|------|---------|---------|------|
| `omit` | 不发送 Cookie | 不发送 Cookie | 完全不发送凭证 |
| `same-origin`（默认） | 发送 Cookie | 不发送 Cookie | 仅同源时发送 |
| `include` | 发送 Cookie | 发送 Cookie | 始终发送凭证 |

```javascript
// 三种模式对比
// 1. omit：完全不发送 Cookie
fetch('https://api.example.com/data', {
  credentials: 'omit'
});

// 2. same-origin（默认）：同源时发送
fetch('/api/data'); // 同源，发送 Cookie
fetch('https://api.example.com/data'); // 跨域，不发送 Cookie

// 3. include：始终发送
fetch('https://api.example.com/data', {
  credentials: 'include'
});
```

**跨域请求携带 Cookie 的完整配置：**

**前端代码：**

```javascript
// 跨域请求携带 Cookie
async function fetchWithCredentials(url) {
  try {
    const response = await fetch(url, {
      credentials: 'include',  // 关键：跨域也发送 Cookie
      mode: 'cors'             // 确保是 cors 模式
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
    
  } catch (error) {
    console.error('请求失败:', error);
    throw error;
  }
}

// 登录后保存 Cookie
async function login(username, password) {
  const response = await fetch('https://api.example.com/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
    credentials: 'include' // 接收服务器 Set-Cookie
  });
  
  return await response.json();
}

// 后续请求自动携带 Cookie
async function getProfile() {
  return await fetchWithCredentials('https://api.example.com/user/profile');
}
```

**服务端配置（Express）：**

```javascript
const express = require('express');
const cors = require('cors');
const app = express();

// 关键配置：credentials: true 时，origin 不能为 '*'
app.use(cors({
  origin: 'https://myapp.com',    // 必须指定具体域名，不能是 '*'
  credentials: true,               // 允许携带凭证
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// 设置 Cookie（服务端）
app.post('/api/auth/login', (req, res) => {
  // 设置 Cookie
  res.cookie('session_id', 'abc123', {
    httpOnly: true,      // 防止 JS 访问
    secure: true,        // 仅 HTTPS
    sameSite: 'none',    // 跨域请求需要设为 'none'
    maxAge: 3600000,     // 1 小时
    path: '/'
  });
  
  res.json({ success: true });
});

// 读取 Cookie
app.get('/api/user/profile', (req, res) => {
  const sessionId = req.cookies.session_id;
  // 验证 session...
  res.json({ username: 'Alice' });
});
```

**SameSite Cookie 属性说明：**

| sameSite 值 | 同站请求 | 跨站请求 | 说明 |
|-------------|---------|---------|------|
| `Strict` | 发送 | 不发送 | 最严格，防止 CSRF |
| `Lax`（默认） | 发送 | 仅顶级导航发送 | 平衡安全和体验 |
| `None` | 发送 | 发送 | 必须同时设置 `Secure` |

**注意事项：**

```javascript
// 1. credentials: 'include' + mode: 'cors' 时，服务端必须：
//    - Access-Control-Allow-Origin 不能是 '*'
//    - Access-Control-Allow-Credentials 必须是 'true'

// 2. 不能同时满足的条件
// ❌ 错误：服务端返回了 Access-Control-Allow-Origin: *
fetch('https://api.example.com/data', { credentials: 'include' });
// 浏览器会报错：The value of the 'Access-Control-Allow-Origin' header
// must not be the wildcard '*' when the request's credentials mode is 'include'.

// 3. Cookie 的安全最佳实践
// Set-Cookie: session_id=abc123; HttpOnly; Secure; SameSite=Strict; Path=/
```

**评分标准：**
- 准确说明 credentials 三种取值的行为（4 分）
- 正确配置跨域 Cookie 前后端（4 分）
- 说明 SameSite 属性的作用（2 分）

---

### 题目 12：Fetch 超时处理

**题目描述：** Fetch API 没有内置的 timeout 配置，请设计并实现一个支持超时、重试和退避策略的 Fetch 封装函数。

**考察知识点：** 超时、重试策略 | **能力等级：** 高级

**参考答案：**

```javascript
/**
 * 支持超时、重试和退避策略的 Fetch 封装
 */
class FetchClient {
  constructor(defaultOptions = {}) {
    this.defaultOptions = {
      timeout: 10000,        // 默认超时 10 秒
      retries: 3,            // 默认重试 3 次
      retryDelay: 1000,      // 初始重试延迟 1 秒
      retryBackoff: 2,       // 退避倍数（指数退避）
      retryOn: [408, 429, 500, 502, 503, 504], // 需要重试的状态码
      ...defaultOptions
    };
  }
  
  /**
   * 核心请求方法
   */
  async request(url, options = {}) {
    const config = { ...this.defaultOptions, ...options };
    const { timeout, retries, retryDelay, retryBackoff, retryOn, ...fetchOptions } = config;
    
    let lastError = null;
    
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        // 创建 AbortController 用于超时控制
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        
        const response = await fetch(url, {
          ...fetchOptions,
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        // 检查是否需要重试
        if (!response.ok && attempt < retries && retryOn.includes(response.status)) {
          throw new RetryableError(
            `HTTP ${response.status}: ${response.statusText}`,
            response.status,
            response
          );
        }
        
        // 检查 HTTP 错误
        if (!response.ok) {
          throw new HttpError(
            `HTTP ${response.status}: ${response.statusText}`,
            response.status,
            response
          );
        }
        
        return response;
        
      } catch (error) {
        lastError = error;
        
        // 如果是可重试的错误且还有重试次数
        if (error instanceof RetryableError && attempt < retries) {
          // 计算退避延迟
          const delay = retryDelay * Math.pow(retryBackoff, attempt);
          // 添加随机抖动（Jitter），防止惊群效应
          const jitter = Math.random() * 200;
          const waitTime = delay + jitter;
          
          console.warn(
            `第 ${attempt + 1} 次重试，等待 ${Math.round(waitTime)}ms...`,
            `(${url})`
          );
          
          await this.sleep(waitTime);
          continue;
        }
        
        // 超时错误
        if (error.name === 'AbortError') {
          if (attempt < retries) {
            console.warn(`请求超时，第 ${attempt + 1} 次重试...`);
            await this.sleep(retryDelay * Math.pow(retryBackoff, attempt));
            continue;
          }
          throw new TimeoutError(`请求超时 (${timeout}ms)，已重试 ${retries} 次`);
        }
        
        // 网络错误也可以重试
        if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
          if (attempt < retries) {
            console.warn(`网络错误，第 ${attempt + 1} 次重试...`);
            await this.sleep(retryDelay * Math.pow(retryBackoff, attempt));
            continue;
          }
          throw new NetworkError('网络连接失败，已重试所有次数');
        }
        
        throw error;
      }
    }
    
    throw lastError;
  }
  
  /**
   * 便捷方法
   */
  async get(url, options = {}) {
    return this.request(url, { ...options, method: 'GET' });
  }
  
  async post(url, data, options = {}) {
    return this.request(url, {
      ...options,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      body: JSON.stringify(data)
    });
  }
  
  async put(url, data, options = {}) {
    return this.request(url, {
      ...options,
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      body: JSON.stringify(data)
    });
  }
  
  async delete(url, options = {}) {
    return this.request(url, { ...options, method: 'DELETE' });
  }
  
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// ---- 自定义错误类 ----
class HttpError extends Error {
  constructor(message, status, response) {
    super(message);
    this.name = 'HttpError';
    this.status = status;
    this.response = response;
  }
}

class RetryableError extends HttpError {
  constructor(message, status, response) {
    super(message, status, response);
    this.name = 'RetryableError';
  }
}

class TimeoutError extends Error {
  constructor(message) {
    super(message);
    this.name = 'TimeoutError';
  }
}

class NetworkError extends Error {
  constructor(message) {
    super(message);
    this.name = 'NetworkError';
  }
}

// ---- 使用示例 ----
const client = new FetchClient({
  timeout: 5000,
  retries: 3,
  retryDelay: 1000,
  retryBackoff: 2
});

async function fetchUserData(userId) {
  try {
    const response = await client.get(`/api/users/${userId}`, {
      headers: { 'Authorization': 'Bearer token123' }
    });
    
    return await response.json();
    
  } catch (error) {
    switch (error.name) {
      case 'TimeoutError':
        showError('请求超时，请稍后重试');
        break;
      case 'NetworkError':
        showError('网络连接失败，请检查网络');
        break;
      case 'HttpError':
        if (error.status === 404) {
          showError('用户不存在');
        } else {
          showError(`服务器错误: ${error.status}`);
        }
        break;
      default:
        showError('未知错误');
    }
    throw error;
  }
}

// 使用
fetchUserData(123).then(user => console.log(user));
```

**重试策略对比：**

| 策略 | 延迟计算 | 特点 | 适用场景 |
|------|---------|------|---------|
| 固定延迟 | `delay` | 简单 | 简单场景 |
| 线性退避 | `delay * attempt` | 逐渐增加 | 轻量服务 |
| 指数退避 | `delay * 2^attempt` | 快速增长 | 高负载服务 |
| 指数退避 + 抖动 | `delay * 2^attempt + random` | 避免惊群 | 分布式系统 |

**评分标准：**
- 正确实现 AbortController 超时控制（3 分）
- 实现指数退避 + 抖动重试策略（4 分）
- 合理分类错误类型并处理（3 分）

---

### 题目 13：封装一个健壮的 Fetch 请求库

**题目描述：** 请基于 Fetch API 封装一个功能完整的 HTTP 请求库，要求支持：请求/响应拦截器、请求去重、并发请求控制、自动 JSON 解析、统一的错误处理。实际项目中这类封装很常见，考察候选人的工程化能力。

**考察知识点：** 工程封装、拦截器、并发控制 | **能力等级：** 高级

**参考答案：**

```javascript
/**
 * 基于 Fetch 的 HTTP 请求库
 * 功能：拦截器、请求去重、并发控制、自动解析、统一错误处理
 */
class HttpClient {
  constructor(baseURL = '', defaultOptions = {}) {
    this.baseURL = baseURL;
    this.defaultOptions = {
      headers: { 'Content-Type': 'application/json' },
      timeout: 10000,
      ...defaultOptions
    };
    
    // 拦截器
    this.interceptors = {
      request: [],
      response: [],
      responseError: []
    };
    
    // 请求去重：pendingRequests 存储进行中的请求
    this.pendingRequests = new Map();
    
    // 并发控制
    this.maxConcurrent = 6;          // 最大并发数
    this.currentConcurrent = 0;      // 当前并发数
    this.pendingQueue = [];          // 等待队列
  }
  
  // ---- 拦截器注册 ----
  useRequestInterceptor(onFulfilled, onRejected) {
    this.interceptors.request.push({ onFulfilled, onRejected });
    return this.interceptors.request.length - 1; // 返回拦截器 ID
  }
  
  useResponseInterceptor(onFulfilled, onRejected) {
    this.interceptors.response.push({ onFulfilled, onRejected });
    return this.interceptors.response.length - 1;
  }
  
  ejectInterceptor(type, id) {
    if (this.interceptors[type]) {
      this.interceptors[type][id] = null;
    }
  }
  
  // ---- 运行拦截器链 ----
  async runInterceptors(type, initialValue) {
    const interceptors = this.interceptors[type].filter(Boolean);
    let result = initialValue;
    
    for (const interceptor of interceptors) {
      try {
        result = await interceptor.onFulfilled(result);
      } catch (error) {
        if (interceptor.onRejected) {
          result = await interceptor.onRejected(error);
        } else {
          throw error;
        }
      }
    }
    
    return result;
  }
  
  // ---- 请求去重：生成请求唯一标识 ----
  generateRequestKey(url, options) {
    const { method = 'GET', body } = options;
    return `${method}:${url}:${body || ''}`;
  }
  
  // ---- 并发控制 ----
  async acquireSlot() {
    if (this.currentConcurrent < this.maxConcurrent) {
      this.currentConcurrent++;
      return;
    }
    
    // 等待队列
    return new Promise(resolve => {
      this.pendingQueue.push(resolve);
    });
  }
  
  releaseSlot() {
    this.currentConcurrent--;
    
    // 释放下一个等待的请求
    if (this.pendingQueue.length > 0) {
      const next = this.pendingQueue.shift();
      this.currentConcurrent++;
      next();
    }
  }
  
  // ---- 核心请求方法 ----
  async request(url, options = {}) {
    const fullURL = this.baseURL + url;
    const mergedOptions = {
      ...this.defaultOptions,
      ...options,
      headers: {
        ...this.defaultOptions.headers,
        ...options.headers
      }
    };
    
    // 去重检查
    const requestKey = this.generateRequestKey(fullURL, mergedOptions);
    if (this.pendingRequests.has(requestKey)) {
      console.log('请求去重:', requestKey);
      return this.pendingRequests.get(requestKey);
    }
    
    // 并发控制：获取执行槽位
    await this.acquireSlot();
    
    const requestPromise = this._executeRequest(fullURL, mergedOptions, requestKey);
    
    // 存储进行中的请求
    this.pendingRequests.set(requestKey, requestPromise);
    
    try {
      const result = await requestPromise;
      return result;
    } finally {
      this.pendingRequests.delete(requestKey);
      this.releaseSlot();
    }
  }
  
  async _executeRequest(url, options, requestKey) {
    // 1. 运行请求拦截器
    let requestConfig = { url, options };
    requestConfig = await this.runInterceptors('request', requestConfig);
    
    // 2. 超时控制
    const controller = new AbortController();
    const timeoutId = setTimeout(
      () => controller.abort(),
      requestConfig.options.timeout
    );
    
    try {
      // 3. 发送请求
      const response = await fetch(requestConfig.url, {
        ...requestConfig.options,
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      // 4. 自动解析响应
      let data = null;
      const contentType = response.headers.get('Content-Type') || '';
      
      if (contentType.includes('application/json')) {
        data = await response.json();
      } else if (contentType.includes('text/')) {
        data = await response.text();
      } else {
        data = await response.blob();
      }
      
      // 5. 统一响应格式
      const result = {
        ok: response.ok,
        status: response.status,
        statusText: response.statusText,
        headers: response.headers,
        data: data,
        config: { url, options: requestConfig.options }
      };
      
      // 6. 运行响应拦截器
      let finalResult = await this.runInterceptors('response', result);
      
      // 7. HTTP 错误处理
      if (!response.ok) {
        const error = new HttpError(
          data?.message || `HTTP ${response.status}`,
          response.status,
          finalResult
        );
        // 运行错误拦截器
        try {
          finalResult = await this.runInterceptors('responseError', error);
        } catch {
          throw error;
        }
      }
      
      return finalResult;
      
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError') {
        throw new TimeoutError(`请求超时 (${options.timeout}ms)`);
      }
      
      throw error;
    }
  }
  
  // ---- 便捷方法 ----
  get(url, params, options = {}) {
    if (params) {
      const queryString = new URLSearchParams(params).toString();
      url = `${url}?${queryString}`;
    }
    return this.request(url, { ...options, method: 'GET' });
  }
  
  post(url, data, options = {}) {
    return this.request(url, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data)
    });
  }
  
  put(url, data, options = {}) {
    return this.request(url, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }
  
  delete(url, options = {}) {
    return this.request(url, { ...options, method: 'DELETE' });
  }
  
  patch(url, data, options = {}) {
    return this.request(url, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  }
}

// ---- 错误类 ----
class HttpError extends Error {
  constructor(message, status, response) {
    super(message);
    this.name = 'HttpError';
    this.status = status;
    this.response = response;
  }
}

class TimeoutError extends Error {
  constructor(message) {
    super(message);
    this.name = 'TimeoutError';
  }
}

// ---- 使用示例 ----
const http = new HttpClient('https://api.example.com');

// 注册请求拦截器：添加 Token
http.useRequestInterceptor(async (config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.options.headers = {
      ...config.options.headers,
      'Authorization': `Bearer ${token}`
    };
  }
  console.log(`[请求] ${config.options.method} ${config.url}`);
  return config;
});

// 注册响应拦截器：处理 Token 过期
http.useResponseInterceptor(
  (response) => {
    console.log(`[响应] ${response.status} ${response.config.url}`);
    return response.data; // 直接返回 data，简化调用
  },
  async (error) => {
    if (error.status === 401) {
      // Token 过期，尝试刷新
      const newToken = await refreshToken();
      if (newToken) {
        // 重试原请求
        return http.request(error.response.config.url, error.response.config.options);
      }
      // 跳转登录
      window.location.href = '/login';
    }
    throw error;
  }
);

// 使用
async function getUsers() {
  const users = await http.get('/users', { page: 1, limit: 10 });
  console.log(users);
}

async function createUser(userData) {
  const newUser = await http.post('/users', userData);
  console.log('创建成功:', newUser);
}
```

**评分标准：**
- 实现请求/响应拦截器链（4 分）
- 实现请求去重和并发控制（3 分）
- 统一错误处理和自动解析（3 分）

---

### 题目 14：Fetch 的 ReadableStream 与流式处理

**题目描述：** 请说明 Fetch API 中 ReadableStream 的用途，并演示如何使用 `response.body.getReader()` 实现大文件下载的进度显示和流式处理。

**考察知识点：** ReadableStream、流式处理 | **能力等级：** 高级

**参考答案：**

**ReadableStream 概念：**

```javascript
// response.body 是一个 ReadableStream
// 可以逐块读取响应数据，而不是一次性加载到内存中
// 适用场景：大文件下载、实时数据流、SSE 流式响应

async function streamDownload(url) {
  const response = await fetch(url);
  
  // 获取内容长度（如果服务器提供了 Content-Length 头）
  const contentLength = response.headers.get('Content-Length');
  const total = contentLength ? parseInt(contentLength, 10) : 0;
  
  // 获取可读流
  const reader = response.body.getReader();
  let received = 0;
  let chunks = []; // 存储所有数据块
  
  while (true) {
    // 逐块读取
    const { done, value } = await reader.read();
    
    if (done) {
      break; // 读取完成
    }
    
    // value 是 Uint8Array（二进制数据块）
    chunks.push(value);
    received += value.length;
    
    // 计算进度
    if (total > 0) {
      const progress = ((received / total) * 100).toFixed(1);
      console.log(`下载进度: ${progress}% (${received}/${total} bytes)`);
      updateProgressBar(progress);
    } else {
      console.log(`已接收: ${received} bytes`);
    }
  }
  
  // 合并所有数据块
  const allChunks = new Uint8Array(received);
  let position = 0;
  for (const chunk of chunks) {
    allChunks.set(chunk, position);
    position += chunk.length;
  }
  
  return allChunks;
}
```

**完整的大文件下载器实现：**

```javascript
/**
 * 流式文件下载器：支持进度显示、暂停/恢复、断点续传
 */
class StreamDownloader {
  constructor() {
    this.abortController = null;
    this.downloadedBytes = 0;
    this.isPaused = false;
  }
  
  /**
   * 下载文件并显示进度
   */
  async download(url, onProgress, onComplete) {
    this.abortController = new AbortController();
    this.downloadedBytes = 0;
    this.isPaused = false;
    
    try {
      // 支持断点续传
      const headers = {};
      if (this.downloadedBytes > 0) {
        headers['Range'] = `bytes=${this.downloadedBytes}-`;
      }
      
      const response = await fetch(url, {
        headers,
        signal: this.abortController.signal
      });
      
      if (!response.ok && response.status !== 206) {
        throw new Error(`下载失败: ${response.status}`);
      }
      
      const contentLength = response.headers.get('Content-Length');
      const total = contentLength ? parseInt(contentLength, 10) + this.downloadedBytes : 0;
      
      const reader = response.body.getReader();
      const chunks = [];
      
      while (true) {
        // 暂停检查
        while (this.isPaused) {
          await this.sleep(100);
        }
        
        const { done, value } = await reader.read();
        
        if (done) break;
        
        chunks.push(value);
        this.downloadedBytes += value.length;
        
        // 进度回调
        if (total > 0 && onProgress) {
          onProgress({
            loaded: this.downloadedBytes,
            total: total,
            percentage: ((this.downloadedBytes / total) * 100).toFixed(1)
          });
        }
      }
      
      // 合并数据
      const blob = new Blob(chunks);
      
      if (onComplete) {
        onComplete(blob);
      }
      
      return blob;
      
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('下载已取消');
      }
      throw error;
    }
  }
  
  /**
   * 保存文件到本地
   */
  saveFile(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
  
  /**
   * 暂停下载
   */
  pause() {
    this.isPaused = true;
  }
  
  /**
   * 恢复下载
   */
  resume() {
    this.isPaused = false;
  }
  
  /**
   * 取消下载
   */
  cancel() {
    if (this.abortController) {
      this.abortController.abort();
    }
  }
  
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// ---- 使用示例 ----
const downloader = new StreamDownloader();

// 下载文件
async function startDownload() {
  const url = 'https://example.com/large-file.zip';
  
  await downloader.download(
    url,
    // 进度回调
    (progress) => {
      document.getElementById('progressBar').style.width = `${progress.percentage}%`;
      document.getElementById('progressText').textContent = 
        `${progress.percentage}% (${formatBytes(progress.loaded)} / ${formatBytes(progress.total)})`;
    },
    // 完成回调
    (blob) => {
      console.log('下载完成!');
      downloader.saveFile(blob, 'downloaded-file.zip');
    }
  );
}

// 暂停
document.getElementById('pauseBtn').onclick = () => downloader.pause();
// 恢复
document.getElementById('resumeBtn').onclick = () => downloader.resume();
// 取消
document.getElementById('cancelBtn').onclick = () => downloader.cancel();

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
```

**SSE（Server-Sent Events）流式处理：**

```javascript
/**
 * 使用 Fetch + ReadableStream 处理 SSE 流式响应
 * 场景：ChatGPT 流式对话、实时日志推送
 */
async function streamChatResponse(prompt) {
  const response = await fetch('https://api.example.com/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt })
  });
  
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  
  while (true) {
    const { done, value } = await reader.read();
    
    if (done) break;
    
    // 解码二进制数据为文本
    buffer += decoder.decode(value, { stream: true });
    
    // 按行分割（SSE 格式：data: xxx\n\n）
    const lines = buffer.split('\n');
    buffer = lines.pop() || ''; // 保留不完整的最后一行
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        
        if (data === '[DONE]') {
          console.log('流式响应完成');
          return;
        }
        
        try {
          const parsed = JSON.parse(data);
          // 逐字显示到页面
          appendToChat(parsed.content);
        } catch {
          // 非 JSON 数据，直接显示
          appendToChat(data);
        }
      }
    }
  }
}
```

**评分标准：**
- 解释 ReadableStream 的用途和原理（3 分）
- 实现下载进度显示（4 分）
- 展示 SSE 流式处理场景（3 分）

---

### 题目 15：Fetch 与 Service Worker 的配合使用

**题目描述：** 请说明 Fetch API 在 Service Worker 中的作用，以及如何使用 Service Worker 拦截 Fetch 请求实现离线缓存策略（Cache First、Network First 等）。

**考察知识点：** Service Worker、离线缓存 | **能力等级：** 高级

**参考答案：**

**Service Worker 中的 Fetch 事件：**

```javascript
// service-worker.js

const CACHE_NAME = 'my-app-v1';
const CACHE_URLS = [
  '/',
  '/index.html',
  '/styles/main.css',
  '/scripts/app.js',
  '/images/logo.png'
];

// 安装阶段：预缓存静态资源
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('预缓存静态资源');
      return cache.addAll(CACHE_URLS);
    })
  );
  // 立即激活，不等待旧 SW 关闭
  self.skipWaiting();
});

// 激活阶段：清理旧缓存
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

// 拦截 Fetch 请求
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // 根据请求类型选择不同的缓存策略
  if (request.method !== 'GET') {
    // 非 GET 请求直接走网络
    return;
  }
  
  if (url.pathname.startsWith('/api/')) {
    // API 请求：Network First
    event.respondWith(networkFirst(request));
  } else if (url.pathname.match(/\.(png|jpg|jpeg|gif|svg|woff2)$/)) {
    // 静态资源：Cache First
    event.respondWith(cacheFirst(request));
  } else {
    // 页面请求：Network First（保证最新内容）
    event.respondWith(networkFirst(request));
  }
});

// ===== 缓存策略实现 =====

/**
 * Cache First（缓存优先）
 * 适用：不常变化的静态资源（图片、字体、CSS、JS）
 */
async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    // 缓存成功的响应
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    // 网络不可用且无缓存时，返回离线页面
    return caches.match('/offline.html');
  }
}

/**
 * Network First（网络优先）
 * 适用：需要最新数据的 API 请求、页面
 */
async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    // 更新缓存
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    // 网络失败时使用缓存
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    // 无缓存，返回离线页面
    return caches.match('/offline.html');
  }
}

/**
 * Cache Only（仅缓存）
 * 适用：完全离线可用的应用壳资源
 */
async function cacheOnly(request) {
  return caches.match(request);
}

/**
 * Network Only（仅网络）
 * 适用：必须在线才能使用的功能（如支付）
 */
async function networkOnly(request) {
  return fetch(request);
}

/**
 * Stale While Revalidate（后台更新）
 * 适用：可接受陈旧数据，但下次访问时获取最新
 */
async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE_NAME);
  const cachedResponse = await cache.match(request);
  
  // 后台更新缓存（不阻塞响应）
  const fetchPromise = fetch(request).then((networkResponse) => {
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  }).catch(() => {
    // 静默失败
  });
  
  // 立即返回缓存内容（如果有）
  return cachedResponse || fetchPromise;
}
```

**缓存策略选择指南：**

| 策略 | 响应速度 | 数据新鲜度 | 适用场景 |
|------|---------|-----------|---------|
| **Cache First** | 快 | 低 | 静态资源（图片、字体） |
| **Network First** | 慢 | 高 | API 数据、页面内容 |
| **Cache Only** | 最快 | 最低 | 应用壳资源 |
| **Network Only** | 最慢 | 最高 | 支付、敏感操作 |
| **Stale While Revalidate** | 快 | 中 | 可接受稍旧的数据 |

**注册 Service Worker：**

```javascript
// main.js - 注册 Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', async () => {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js');
      console.log('Service Worker 注册成功:', registration.scope);
      
      // 监听更新
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            console.log('新版本可用，请刷新页面');
            // 提示用户更新
            showUpdateNotification();
          }
        });
      });
    } catch (error) {
      console.error('Service Worker 注册失败:', error);
    }
  });
}
```

**评分标准：**
- 解释 Service Worker 中 Fetch 事件的作用（3 分）
- 实现 Cache First 和 Network First 策略（4 分）
- 说明不同缓存策略的适用场景（3 分）

---

## 附录：考点速查表

| 序号 | 题目 | 核心考点 | 难度 |
|------|------|---------|------|
| 1 | Fetch API 基本使用流程 | Promise、response.json()、错误检查 | 初级 |
| 2 | Response 对象属性和方法 | 响应解析、Content-Type、clone() | 初级 |
| 3 | Fetch 请求配置项 | method、headers、body、mode、credentials | 初级 |
| 4 | Fetch 错误处理机制 | 网络错误 vs HTTP 错误、自定义错误类 | 中级 |
| 5 | POST 请求及 Token 管理 | JSON 请求体、认证、Token 刷新 | 中级 |
| 6 | 文件上传处理 | FormData、上传进度替代方案 | 中级 |
| 7 | AbortController 中断请求 | 请求取消、防抖搜索 | 中级 |
| 8 | 跨域请求 CORS 处理 | mode、预检请求、代理方案 | 中级 |
| 9 | Fetch vs XMLHttpRequest | API 设计、功能对比、适用场景 | 中级 |
| 10 | 兼容性及 Polyfill 方案 | 浏览器兼容、whatwg-fetch、降级 | 中级 |
| 11 | Cookie 和凭证处理 | credentials、SameSite、跨域 Cookie | 中级 |
| 12 | 超时与重试策略 | AbortController、指数退避、抖动 | 高级 |
| 13 | 封装健壮的请求库 | 拦截器、请求去重、并发控制 | 高级 |
| 14 | ReadableStream 流式处理 | 下载进度、SSE 流式响应 | 高级 |
| 15 | Service Worker 配合 | 离线缓存、缓存策略 | 高级 |

**按难度统计：** 初级 3 题 / 中级 9 题 / 高级 3 题

**使用建议：**
- **初级岗位**：重点掌握题目 1-3，了解 Fetch 基本使用和配置
- **中级岗位**：重点掌握题目 4-11，熟悉错误处理、文件上传、跨域、兼容性等实战问题
- **高级岗位**：重点掌握题目 12-15，能封装请求库、处理流式数据和 Service Worker 集成