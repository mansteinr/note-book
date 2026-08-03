# Script 标签 defer 与 async 属性详解

> 本文档详细说明 JavaScript 中 `<script>` 标签的 `defer` 属性、`async` 属性以及普通无属性之间的区别，包括执行机制、加载顺序、DOM 阻塞分析和适用场景，帮助开发者优化页面加载性能。

---

## 目录

- [一、script 标签概述](#一script-标签概述)
- [二、三种加载方式对比](#二三种加载方式对比)
- [三、执行机制详解](#三执行机制详解)
- [四、加载与执行顺序差异](#四加载与执行顺序差异)
- [五、DOM 解析阻塞分析](#五dom-解析阻塞分析)
- [六、适用场景说明](#六适用场景说明)
- [七、实际应用示例](#七实际应用示例)
- [八、常见问题与最佳实践](#八常见问题与最佳实践)
- [九、浏览器兼容性](#九浏览器兼容性)

---

## 一、script 标签概述

### 1.1 script 标签的作用

`<script>` 标签用于在 HTML 页面中嵌入或引用 JavaScript 代码，是前端开发中最基础的标签之一。

### 1.2 三种加载方式

```
┌─────────────────────────────────────────────────────────────────┐
│                script 标签的三种加载方式                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 普通无属性：<script src="app.js"></script>                  │
│     - 阻塞 DOM 解析                                             │
│     - 同步执行脚本                                              │
│     - 必须等脚本下载并执行完才继续解析 DOM                      │
│                                                                 │
│  2. defer 属性：<script src="app.js" defer></script>            │
│     - 不阻塞 DOM 解析                                           │
│     - 并行下载脚本                                              │
│     - 在 DOMContentLoaded 之前按顺序执行                        │
│                                                                 │
│  3. async 属性：<script src="app.js" async></script>            │
│     - 不阻塞 DOM 解析                                           │
│     - 并行下载脚本                                              │
│     - 下载完立即执行，不保证顺序                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、三种加载方式对比

### 2.1 核心对比表

| 特性 | 普通（无属性） | defer | async |
|------|---------------|-------|-------|
| **是否阻塞 DOM 解析** | ✅ 阻塞 | ❌ 不阻塞 | ❌ 不阻塞 |
| **下载方式** | 阻塞式下载 | 并行下载 | 并行下载 |
| **执行时机** | 下载完立即执行 | DOMContentLoaded 之前 | 下载完立即执行 |
| **执行顺序** | 按文档顺序 | 按文档顺序 | 不保证顺序 |
| **DOMContentLoaded 影响** | 需等待脚本执行 | 在之前执行 | 可能之前或之后 |
| **DOMContentLoaded 等待** | 等待 | 等待 | 不等待 |
| **适用场景** | 必须立即执行的脚本 | 依赖 DOM 的脚本 | 独立的第三方脚本 |

### 2.2 关键区别总结

| 对比维度 | 普通 | defer | async |
|---------|------|-------|-------|
| **阻塞行为** | 完全阻塞 | 仅执行时短暂阻塞 | 仅执行时短暂阻塞 |
| **脚本依赖** | 保证顺序 | 保证顺序 | 不保证顺序 |
| **DOM 可用性** | 执行时 DOM 未解析完 | 执行时 DOM 已解析完 | 不确定 |
| **性能影响** | 最差 | 较好 | 最好（对主线程） |

---

## 三、执行机制详解

### 3.1 普通 script（无属性）

#### 执行机制

```
HTML 解析流程：
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  解析 HTML → 遇到 <script> → 暂停解析                          │
│       ↓                                                         │
│  发起网络请求 → 下载脚本 → 执行脚本                             │
│       ↓                                                         │
│  继续解析 HTML → 完成渲染                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 特点

- **完全阻塞**：脚本下载和执行期间，HTML 解析完全停止
- **同步执行**：必须等脚本执行完毕才能继续
- **顺序保证**：按文档顺序执行

#### 示例代码

```html
<!DOCTYPE html>
<html>
<head>
    <title>普通 script 示例</title>
    
    <!-- 阻塞 DOM 解析，必须等脚本下载并执行完 -->
    <script src="script1.js"></script>
    <!-- script1.js 执行完后才继续解析下面的内容 -->
    
    <script src="script2.js"></script>
    <!-- script2.js 执行完后才继续 -->
</head>
<body>
    <!-- script1.js 和 script2.js 执行完才解析到这里 -->
    <div id="app">Hello World</div>
    
    <script src="script3.js"></script>
</body>
</html>
```

**执行顺序**：script1.js → script2.js → script3.js（严格按顺序）

### 3.2 defer 属性

#### 执行机制

```
HTML 解析流程：
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  解析 HTML → 遇到 <script defer> → 继续解析                    │
│       ↓                                                         │
│  后台并行下载脚本（不阻塞）                                     │
│       ↓                                                         │
│  解析完成 → DOMContentLoaded 之前                               │
│       ↓                                                         │
│  按文档顺序执行所有 defer 脚本                                  │
│       ↓                                                         │
│  触发 DOMContentLoaded 事件                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 特点

- **不阻塞解析**：下载过程不阻塞 HTML 解析
- **保证顺序**：按文档顺序执行
- **DOM 可用**：执行时 DOM 已解析完成
- **在 DOMContentLoaded 之前**：确保脚本执行完后才触发事件

#### 示例代码

```html
<!DOCTYPE html>
<html>
<head>
    <title>defer 示例</title>
    
    <!-- 不阻塞，并行下载，DOMContentLoaded 前执行 -->
    <script src="utils.js" defer></script>
    
    <!-- 不阻塞，并行下载，DOMContentLoaded 前执行 -->
    <script src="app.js" defer></script>
</head>
<body>
    <!-- 继续解析，不等待脚本 -->
    <div id="app">Hello World</div>
    
    <!-- 脚本下载完但在 DOMContentLoaded 前执行 -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM 已加载完成');
        });
    </script>
</body>
</html>

<!-- 执行顺序：utils.js → app.js → DOMContentLoaded 事件 -->
```

**执行顺序**：utils.js → app.js → DOMContentLoaded（严格按文档顺序）

### 3.3 async 属性

#### 执行机制

```
HTML 解析流程：
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  解析 HTML → 遇到 <script async> → 继续解析                    │
│       ↓                                                         │
│  后台并行下载脚本（不阻塞）                                     │
│       ↓                                                         │
│  下载完成 → 立即暂停解析 → 执行脚本 → 继续解析                  │
│       ↓                                                         │
│  （可能在 DOMContentLoaded 之前或之后）                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 特点

- **不阻塞解析**：下载过程不阻塞 HTML 解析
- **不保证顺序**：下载完就执行，先下载完先执行
- **独立执行**：脚本之间无依赖关系
- **执行时机不确定**：可能在 DOMContentLoaded 之前或之后

#### 示例代码

```html
<!DOCTYPE html>
<html>
<head>
    <title>async 示例</title>
    
    <!-- 并行下载，下载完立即执行，不保证顺序 -->
    <script src="analytics.js" async></script>
    
    <!-- 并行下载，下载完立即执行，不保证顺序 -->
    <script src="advertisement.js" async></script>
</head>
<body>
    <div id="app">Hello World</div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM 已加载完成');
            // async 脚本可能在这之前执行，也可能在这之后
        });
    </script>
</body>
</html>

<!-- 执行顺序：不确定，谁先下载完谁先执行 -->
```

**执行顺序**：不保证（先下载完先执行）

---

## 四、加载与执行顺序差异

### 4.1 时间轴对比图

```
时间轴 →
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  普通 script：                                                          │
│  HTML解析 ████████ 暂停 ████ 下载 ██████ 执行 ████ 继续解析 ████████   │
│                   ↓           ↓          ↓                              │
│               遇到script   等待下载    执行脚本                          │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  defer script：                                                         │
│  HTML解析 ████████████████████████ ████████████                        │
│           ↓                           ↓                                 │
│       遇到script                  解析完成                              │
│           ↓                           ↓                                 │
│       并行下载                 执行defer脚本                            │
│           ██████████████         ████                                   │
│                              DOMContentLoaded                           │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  async script：                                                         │
│  HTML解析 ██████████████████████████████████████                       │
│           ↓                 ↓               ↓                          │
│       遇到script         下载完成        执行脚本                       │
│           并行下载           ████            ████                       │
│                                                                         │
│  （执行时机不确定，可能在解析中途）                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 多脚本执行顺序示例

#### 场景一：多个普通 script

```html
<script src="a.js"></script>
<script src="b.js"></script>
<script src="c.js"></script>

<!-- 执行顺序：a.js → b.js → c.js（严格按顺序，阻塞解析） -->
```

#### 场景二：多个 defer script

```html
<script src="a.js" defer></script>
<script src="b.js" defer></script>
<script src="c.js" defer></script>

<!-- 执行顺序：a.js → b.js → c.js（严格按顺序，不阻塞解析） -->
<!-- 所有脚本在 DOMContentLoaded 之前执行 -->
```

#### 场景三：多个 async script

```html
<script src="a.js" async></script>
<script src="b.js" async></script>
<script src="c.js" async></script>

<!-- 执行顺序：不确定（先下载完先执行） -->
<!-- 可能是：b.js → c.js → a.js（取决于文件大小和网络） -->
```

#### 场景四：混合使用

```html
<script src="a.js"></script>
<script src="b.js" defer></script>
<script src="c.js" async></script>
<script src="d.js" defer></script>

<!-- 执行顺序： -->
<!-- 1. a.js 立即执行（阻塞） -->
<!-- 2. c.js 下载完随时执行（可能在 b.js 和 d.js 之前或之后） -->
<!-- 3. b.js 和 d.js 在 DOMContentLoaded 之前按顺序执行 -->
<!-- 实际顺序：a.js → [不确定c.js何时] → b.js → d.js -->
```

---

## 五、DOM 解析阻塞分析

### 5.1 阻塞行为对比

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DOM 解析阻塞情况                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  普通 script：                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ HTML解析 ████████ 暂停 ████████████████ 恢复 ████████      │   │
│  │              ↓                                    ↓          │   │
│  │          完全阻塞                            继续解析        │   │
│  │                                                               │   │
│  │ 影响：页面白屏时间变长，用户等待时间长                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  defer script：                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ HTML解析 ████████████████████████████████                  │   │
│  │                                                               │   │
│  │ 下载 ████████████ (不阻塞)                                  │   │
│  │                           执行 ████ (短暂阻塞)              │   │
│  │                                                               │   │
│  │ 影响：页面渲染更快，用户体验更好                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  async script：                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ HTML解析 ██████████████████████████████████                │   │
│  │                                                               │   │
│  │ 下载 ████████████ (不阻塞)                                  │   │
│  │                           执行 ████ (短暂阻塞)              │   │
│  │                                                               │   │
│  │ 影响：主线程阻塞时间最短，但脚本执行时机不可控               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 DOMContentLoaded 触发时机

| 情况 | DOMContentLoaded 触发时机 |
|------|--------------------------|
| **普通 script** | 所有普通脚本执行完毕后 |
| **defer script** | 所有 defer 脚本执行完毕后 |
| **async script** | 不等待 async 脚本，可能之前或之后触发 |

### 5.3 阻塞时间计算

```javascript
// 普通 script 阻塞时间
阻塞时间 = 下载时间 + 执行时间

// defer script 阻塞时间
阻塞时间 = 执行时间（下载在后台进行）

// async script 阻塞时间
阻塞时间 = 执行时间（下载在后台进行）
```

**结论**：defer 和 async 都能显著减少页面白屏时间，提升用户体验。

---

## 六、适用场景说明

### 6.1 普通 script（无属性）

#### 适用场景

```javascript
// 1. 必须立即执行的脚本（初始化关键功能）
<script>
    // 立即配置全局变量
    window.appConfig = { version: '1.0.0' };
</script>

// 2. 需要阻塞后续内容的脚本（如 document.write）
<script>
    document.write('<div>动态内容</div>');
</script>

// 3. 必须按顺序执行的依赖脚本
<script src="jquery.js"></script>
<script src="jquery-plugin.js"></script> <!-- 依赖 jquery -->
```

#### 不推荐场景

```javascript
// ❌ 不推荐：放在 <head> 中阻塞渲染
<head>
    <script src="large-library.js"></script> <!-- 阻塞渲染 -->
</head>

// ✅ 推荐：放在 </body> 之前
<body>
    <!-- 页面内容 -->
    <script src="large-library.js"></script>
</body>
```

### 6.2 defer 属性

#### 适用场景

```javascript
// 1. 依赖 DOM 元素的脚本
<script src="app.js" defer></script>
// app.js 内容：
document.getElementById('app').innerHTML = 'Hello';

// 2. 需要按顺序执行的多个脚本
<script src="jquery.js" defer></script>
<script src="jquery-plugin.js" defer></script> <!-- 保证顺序 -->
<script src="app.js" defer></script>

// 3. 页面初始化脚本
<script src="init.js" defer></script>

// 4. 放在 <head> 中提前下载但不阻塞渲染
<head>
    <script src="app.js" defer></script> <!-- 提前下载 -->
</head>
```

#### 最佳实践

```html
<!DOCTYPE html>
<html>
<head>
    <!-- 推荐位置：提前下载，DOMContentLoaded 前执行 -->
    <script src="analytics.js" defer></script>
    <script src="app.js" defer></script>
</head>
<body>
    <div id="app"></div>
    
    <!-- 也可以放在 body 底部 -->
    <script src="utils.js" defer></script>
</body>
</html>
```

### 6.3 async 属性

#### 适用场景

```javascript
// 1. 独立的第三方脚本（无依赖）
<script src="https://www.googletagmanager.com/gtag/js" async></script>
<script src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js" async></script>

// 2. 统计分析脚本
<script src="analytics.js" async></script>

// 3. 广告脚本
<script src="advertisement.js" async></script>

// 4. 社交分享按钮
<script src="social-share.js" async></script>

// 5. 不依赖 DOM 的独立功能
<script src="chat-widget.js" async></script>
```

#### 特点

```javascript
// async 脚本特点：
// ✅ 完全独立，不依赖其他脚本
// ✅ 不依赖 DOM 元素（或 DOM 加载后自动初始化）
// ✅ 执行时机不重要
// ❌ 不能保证执行顺序
// ❌ 可能在 DOMContentLoaded 之前或之后执行
```

---

## 七、实际应用示例

### 7.1 电商网站示例

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>电商平台</title>
    
    <!-- 立即执行：配置全局变量 -->
    <script>
        window.siteConfig = {
            apiBase: 'https://api.example.com',
            version: '2.0.0'
        };
    </script>
    
    <!-- defer: 核心业务逻辑（依赖 DOM） -->
    <script src="js/jquery.min.js" defer></script>
    <script src="js/jquery.cookie.js" defer></script>
    <script src="js/app.js" defer></script>
    
    <!-- async: 独立的第三方脚本 -->
    <script src="https://www.googletagmanager.com/gtag/js" async></script>
    <script async>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'GA_MEASUREMENT_ID');
    </script>
</head>
<body>
    <!-- 页面内容 -->
    <div id="app">
        <header>导航栏</header>
        <main>商品列表</main>
        <footer>页脚</footer>
    </div>
    
    <!-- defer: 可放在 body 底部 -->
    <script src="js/footer.js" defer></script>
    
    <!-- 普通: 必须立即执行的脚本 -->
    <script>
        // 初始化用户状态
        if (document.cookie.indexOf('user_token') !== -1) {
            console.log('用户已登录');
        }
    </script>
</body>
</html>
```

### 7.2 SPA 应用示例

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>单页应用</title>
    
    <!-- defer: Vue/React 框架 -->
    <script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.prod.js" defer></script>
    
    <!-- defer: 应用代码（保证顺序） -->
    <script src="js/router.js" defer></script>
    <script src="js/store.js" defer></script>
    <script src="js/app.js" defer></script>
    
    <!-- async: 统计脚本（独立） -->
    <script src="https://cdn.example.com/analytics.min.js" async></script>
</head>
<body>
    <div id="app"></div>
    
    <!-- 内联 script: 立即执行 -->
    <script>
        // 性能监控
        window.addEventListener('load', function() {
            var timing = performance.timing;
            var loadTime = timing.loadEventEnd - timing.navigationStart;
            console.log('页面加载时间:', loadTime + 'ms');
        });
    </script>
</body>
</html>
```

### 7.3 博客网站示例

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>技术博客</title>
    
    <!-- async: 广告脚本 -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
    
    <!-- defer: 代码高亮 -->
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js" defer></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-javascript.min.js" defer></script>
</head>
<body>
    <article>
        <h1>JavaScript 教程</h1>
        <pre><code class="language-javascript">
const greeting = 'Hello, World!';
console.log(greeting);
        </code></pre>
    </article>
    
    <!-- 普通: 评论系统（必须立即执行） -->
    <script>
        // 评论初始化
        window.commentConfig = {
            articleId: '12345',
            author: '张三'
        };
    </script>
    <script src="js/comments.js"></script>
</body>
</html>
```

### 7.4 动态加载脚本示例

```javascript
// 动态创建 script 标签（默认 async: true）

// 方式一：动态创建（async 行为）
function loadScriptAsync(url) {
    const script = document.createElement('script');
    script.src = url;
    script.async = true;  // 默认值，可省略
    document.head.appendChild(script);
}

// 方式二：动态创建（defer 行为）
function loadScriptDefer(url) {
    const script = document.createElement('script');
    script.src = url;
    script.async = false;  // 设置为 false 才能保证顺序
    document.head.appendChild(script);
}

// 使用示例
loadScriptAsync('https://example.com/analytics.js');
loadScriptDefer('js/dependent-script.js');

// 动态加载多个脚本（保证顺序）
['jquery.js', 'jquery-plugin.js', 'app.js'].forEach(url => {
    loadScriptDefer(url);
});
```

---

## 八、常见问题与最佳实践

### 8.1 常见问题

#### Q1: defer 和 async 可以同时使用吗？

```html
<!-- ❌ 不推荐：同时使用 defer 和 async -->
<script src="app.js" defer async></script>

<!-- 结果：async 优先级更高，defer 被忽略 -->
<!-- 行为等同于只有 async -->
```

**答案**：可以同时使用，但 `async` 优先级更高，`defer` 会被忽略。不推荐同时使用。

#### Q2: 内联 script 可以使用 defer/async 吇？

```html
<!-- ❌ 无效：内联 script 不支持 defer/async -->
<script defer>
    console.log('这段代码会立即执行');
</script>

<!-- ✅ 有效：外部脚本才支持 defer/async -->
<script src="app.js" defer></script>
```

**答案**：内联 `<script>` 标签不支持 `defer` 和 `async` 属性，会被忽略。

#### Q3: 动态创建的 script 默认是 async 还是 defer？

```javascript
// 动态创建的 script 默认是 async: true
const script = document.createElement('script');
script.src = 'app.js';
console.log(script.async);  // true

// 如果需要保证顺序，设置 async: false
script.async = false;
```

**答案**：动态创建的 `<script>` 默认 `async: true`。如需保证顺序，需设置 `async: false`。

#### Q4: 为什么 defer 脚本在 DOMContentLoaded 之前执行？

```html
<script>
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DOM 加载完成');
    });
</script>

<script src="defer-script.js" defer></script>
<!-- defer-script.js 会在 DOMContentLoaded 之前执行 -->
```

**答案**：`defer` 的设计目的是确保脚本能在 DOM 准备好后立即执行，同时保证所有 defer 脚本执行完后才触发 `DOMContentLoaded`。

#### Q5: 混合使用 defer 和 async 会怎样？

```html
<script src="a.js" defer></script>
<script src="b.js" async></script>
<script src="c.js" defer></script>

<!-- 执行顺序： -->
<!-- 1. a.js 和 c.js：DOMContentLoaded 之前按顺序执行 -->
<!-- 2. b.js：下载完随时执行（可能在 a.js/c.js 之前或之后） -->
```

**答案**：`defer` 脚本和 `async` 脚本相互独立，`async` 脚本可能在任何时候执行。

### 8.2 最佳实践

#### 1. 优先使用 defer

```html
<!-- ✅ 推荐：大多数情况使用 defer -->
<head>
    <script src="app.js" defer></script>
</head>

<!-- ❌ 避免：阻塞渲染 -->
<head>
    <script src="app.js"></script>
</head>
```

#### 2. 独立脚本使用 async

```html
<!-- ✅ 推荐：独立的第三方脚本使用 async -->
<script src="https://www.googletagmanager.com/gtag/js" async></script>
<script src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js" async></script>
```

#### 3. 关键脚本放在 head 中使用 defer

```html
<!-- ✅ 推荐：提前下载但不阻塞渲染 -->
<head>
    <script src="critical.js" defer></script>
</head>
```

#### 4. 依赖脚本按顺序使用 defer

```html
<!-- ✅ 推荐：保证顺序 -->
<script src="jquery.js" defer></script>
<script src="jquery-plugin.js" defer></script> <!-- 依赖 jquery.js -->
<script src="app.js" defer></script> <!-- 依赖前两个 -->
```

#### 5. 避免 document.write

```javascript
// ❌ 避免：defer/async 脚本中不要使用 document.write
<script src="app.js" defer>
    document.write('<div>内容</div>'); // 会清除整个页面
</script>
```

#### 6. 检测脚本加载状态

```javascript
// 监听脚本加载完成
const script = document.createElement('script');
script.src = 'app.js';

script.onload = function() {
    console.log('脚本加载成功');
};

script.onerror = function() {
    console.error('脚本加载失败');
};

document.head.appendChild(script);
```

---

## 九、浏览器兼容性

### 9.1 兼容性支持

| 特性 | Chrome | Firefox | Safari | Edge | IE |
|------|--------|---------|--------|------|-----|
| **defer** | 所有版本 | 所有版本 | 所有版本 | 所有版本 | IE10+ |
| **async** | 所有版本 | 所有版本 | 所有版本 | 所有版本 | IE10+ |
| **defer 按顺序执行** | 所有版本 | 所有版本 | 所有版本 | 所有版本 | IE10+ |

### 9.2 IE 浏览器注意事项

```html
<!-- IE9 及以下：defer 可能不按顺序执行 -->
<!--[if IE]>
    <script src="app.js" defer></script>
<![endif]-->

<!-- 推荐：IE 使用 polyfill 或放在 </body> 之前 -->
<!--[if lt IE 10]>
    <script src="app.js"></script>
<![endif]-->
```

### 9.3 兼容性检测

```javascript
// 检测浏览器是否支持 defer/async
function supportsScriptAttributes() {
    const script = document.createElement('script');
    return {
        defer: 'defer' in script,
        async: 'async' in script
    };
}

console.log(supportsScriptAttributes());
// { defer: true, async: true }
```

---

## 十、总结

### 10.1 快速选择指南

```
┌─────────────────────────────────────────────────────────────────────┐
│                     script 属性选择决策树                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  脚本是否依赖 DOM？                                                 │
│  ├── 是 → 脚本之间有依赖吗？                                        │
│  │       ├── 是 → 使用 defer（保证顺序）                            │
│  │       └── 否 → 可以使用 defer 或放在 </body> 之前                │
│  │                                                                 │
│  └── 否 → 脚本必须立即执行吗？                                      │
│          ├── 是 → 使用普通 script（无属性）                         │
│          └── 否 → 使用 async（独立第三方脚本）                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 10.2 核心要点总结

| 要点 | 说明 |
|------|------|
| **普通 script** | 阻塞 DOM 解析，必须下载执行完才继续 |
| **defer** | 不阻塞解析，DOMContentLoaded 前按顺序执行 |
| **async** | 不阻塞解析，下载完立即执行，不保证顺序 |
| **DOMContentLoaded** | defer 在之前执行，async 可能之前或之后 |
| **执行顺序** | defer 保证顺序，async 不保证 |
| **最佳实践** | 优先 defer，第三方用 async，关键用普通 |

### 10.3 性能优化建议

1. **减少普通 script 的使用**：避免阻塞渲染
2. **优先使用 defer**：保证顺序且不阻塞
3. **独立脚本用 async**：最大化性能
4. **关键脚本放 head**：使用 defer 提前下载
5. **避免 document.write**：defer/async 中禁用

---

## 参考资料

- [MDN: script 标签](https://developer.mozilla.org/zh-CN/docs/Web/HTML/Element/script)
- [HTML 规范: Script 标签](https://html.spec.whatwg.org/multipage/scripting.html)
- [Google Developers: 优化 JavaScript 执行](https://developers.google.com/web/fundamentals/performance/optimizing-javascript-execution)

---

> **文档说明**：本文档详细说明了 JavaScript 中 `<script>` 标签的 `defer` 属性、`async` 属性以及普通无属性之间的区别。通过对比表格、执行流程图、代码示例和最佳实践，帮助开发者深入理解不同属性对页面加载性能和脚本执行顺序的影响，从而做出正确的技术选择。