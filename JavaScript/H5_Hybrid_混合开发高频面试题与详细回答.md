# H5 Hybrid 混合开发高频面试题与详细回答

> 适用于前端 / H5 / Hybrid / 移动端 WebView 岗位。  
> 重点覆盖：Hybrid 架构、WebView、刘海屏、安全区域、JSBridge 原理与双向通信、1px 边框、300ms 点击延迟、页面性能、动画流畅度、用户交互、软键盘、网络、缓存、安全、生命周期、白屏、监控和项目实战回答。

---

# 目录

1. Hybrid 基础与架构
2. WebView 原理
3. 刘海屏与 Safe Area
4. 1px 边框问题
5. 300ms 点击延迟
6. JSBridge 原理
7. JSBridge 双向通信
8. JSBridge 常见底层实现
9. 页面首屏优化
10. WebView 性能优化
11. 动画流畅度与 60FPS
12. 渲染、重排与重绘
13. 用户交互优化
14. 滚动性能
15. 软键盘适配
16. 网络与弱网优化
17. 缓存与离线方案
18. Hybrid 生命周期
19. Hybrid 白屏问题
20. 安全问题
21. 错误监控与性能监控
22. 高频面试题与标准回答
23. 项目经验回答模板

---

# 一、什么是 Hybrid 混合开发？

## 1. 什么是 Hybrid？

Hybrid App 是：

> **Native + Web 技术结合开发移动应用的方式。**

典型结构：

```text
                    Native App
                        │
              ┌─────────┴─────────┐
              │                   │
          Native 页面            WebView
                                  │
                            HTML / CSS / JS
                                  │
                              JSBridge
                             ↙       ↘
                        Android      iOS
```

通常：

### H5 负责

- 页面展示
- CSS 样式
- 业务逻辑
- 活动页面
- 商品详情
- 表单页面
- 快速迭代

### Native 负责

- 相机
- 扫码
- 定位
- 蓝牙
- 文件系统
- 系统权限
- 推送
- 支付
- 高性能能力

H5 通过 WebView 运行，并通过 JSBridge 调用 Native。

---

## 2. Hybrid 和纯 H5、Native 有什么区别？

### 纯 H5

```text
浏览器
  ↓
网页
```

优点：

- 开发快
- 发布快
- 跨平台

缺点：

- 系统能力有限
- 性能有限

---

### Native

```text
Android / iOS
  ↓
原生 API
```

优点：

- 性能好
- 系统能力强

缺点：

- Android 和 iOS 需要分别开发
- 发版成本较高

---

### Hybrid

```text
Native App
    ↓
WebView
    ↓
H5
    ↕
JSBridge
    ↕
Native
```

Hybrid 的核心优势：

> **业务迭代速度 + 跨平台 + Native 系统能力。**

---

# 二、WebView 是什么？

## 3. WebView 在 Hybrid 中做什么？

WebView 可以理解成：

> **运行在 App 内部的浏览器环境。**

它可以加载：

```text
HTML
CSS
JavaScript
图片
网络资源
```

例如：

```text
Native App
    │
    └── WebView
           │
           ├── DOM
           ├── CSSOM
           ├── JavaScript
           └── 页面渲染
```

Hybrid 的典型流程：

```text
用户打开 App
       ↓
Native 创建 WebView
       ↓
WebView 加载 URL
       ↓
下载 HTML
       ↓
下载 JS / CSS
       ↓
执行 JavaScript
       ↓
渲染页面
```

---

# 三、H5 如何解决刘海屏？

## 4. 什么是 Safe Area？

全面屏设备可能存在：

```text
刘海
挖孔
圆角
底部 Home Indicator
```

例如：

```text
┌───────────────┐
│    刘海区域     │
├───────────────┤
│               │
│    H5 页面     │
│               │
│               │
├───────────────┤
│ Home Indicator│
└───────────────┘
```

如果没有处理：

```text
按钮被刘海遮挡
底部操作按钮被 Home Indicator 遮挡
```

---

## 5. 如何使用 viewport-fit=cover？

```html
<meta
  name="viewport"
  content="width=device-width,
           initial-scale=1.0,
           viewport-fit=cover"
/>
```

作用：

> 让页面可以扩展到整个屏幕区域。

但是：

```text
使用完整屏幕
    ↓
内容可能进入危险区域
    ↓
需要使用 Safe Area
```

---

## 6. 如何获取安全区域？

使用：

```css
env(safe-area-inset-top)
env(safe-area-inset-right)
env(safe-area-inset-bottom)
env(safe-area-inset-left)
```

例如：

```css
.page {
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
}
```

---

## 7. 顶部导航怎么处理？

```css
.header {
  height: calc(
    44px + env(safe-area-inset-top)
  );

  padding-top: env(safe-area-inset-top);

  box-sizing: border-box;
}
```

---

## 8. 底部固定按钮怎么处理？

```css
.footer {
  padding-bottom: calc(
    16px + env(safe-area-inset-bottom)
  );
}
```

---

## 9. 为什么不能简单给 body 加 padding？

因为可能导致：

```text
fixed 元素异常
背景留白
高度计算错误
全屏页面布局错误
```

更合理：

```text
Header
  ↓
safe-area-inset-top

Footer
  ↓
safe-area-inset-bottom

Content
  ↓
正常布局
```

---

## 面试标准回答

> 在全面屏设备中，顶部可能存在刘海和挖孔，底部存在 Home Indicator。如果 WebView 需要全屏显示，我会在 viewport 中使用 `viewport-fit=cover`，然后通过 CSS 的 `env(safe-area-inset-top)` 和 `env(safe-area-inset-bottom)` 获取安全区域。顶部导航和底部固定操作区域分别增加对应的 padding，避免内容被系统区域遮挡。

---

# 四、移动端 1px 边框问题

## 10. 为什么 1px 看起来很粗？

核心原因：

> **CSS 像素和物理像素不一定是一一对应的。**

例如：

```text
DPR = 1
1 CSS px = 1 physical px
```

高分屏：

```text
DPR = 2
1 CSS px ≈ 2 physical px
```

因此：

```css
border: 1px solid #ddd;
```

可能实际占据多个物理像素。

---

## 11. 什么是 DPR？

```javascript
window.devicePixelRatio
```

例如：

```text
devicePixelRatio = 2
```

代表：

```text
1 个 CSS 像素
=
2 × 2 个物理像素区域
```

---

## 12. 如何解决 1px 问题？

经典方案：

```css
.border {
  position: relative;
}

.border::after {
  content: "";

  position: absolute;

  left: 0;
  right: 0;
  bottom: 0;

  height: 1px;

  background: #ddd;

  transform: scaleY(0.5);
  transform-origin: 0 0;
}
```

核心：

```text
先绘制 1 CSS px
       ↓
transform 缩放
       ↓
视觉上变成 0.5 CSS px
```

---

## 13. 其他方案

可以考虑：

```css
border: 0.5px solid #ddd;
```

但需要考虑：

```text
设备兼容性
浏览器兼容性
WebView 版本
```

因此工程中常见：

```text
伪元素 + transform
```

---

## 面试标准回答

> 1px 问题本质是 CSS 像素和设备物理像素的比例问题。在高 DPR 设备上，1 CSS px 可能对应多个物理像素，因此视觉上边框会显得比较粗。传统方案是通过伪元素绘制 1px，再根据 DPR 使用 transform 缩放，例如 DPR=2 时 scaleY(0.5)，实现接近一个物理像素的细线。

---

# 五、300ms 点击延迟

## 14. 为什么会有 300ms 延迟？

早期移动浏览器支持：

```text
双击屏幕
    ↓
页面缩放
```

因此浏览器收到：

```text
touchstart
    ↓
touchend
```

后不会立即触发 click，而是等待约 300ms 判断：

```text
是不是第二次点击？
```

因此：

```text
touchend
   ↓
等待约 300ms
   ↓
click
```

---

## 15. 现代浏览器还有 300ms 延迟吗？

不一定。

现代浏览器在合理配置：

```html
<meta
  name="viewport"
  content="width=device-width,
           initial-scale=1"
/>
```

以及合适的触摸行为下，传统 300ms 延迟通常已经被消除。

面试不要说：

> 所有移动端都有 300ms 延迟。

正确：

> 300ms 是早期移动浏览器为了支持双击缩放产生的 click 延迟，现代浏览器在合适的 viewport 和触摸行为下通常已经不存在明显的传统延迟，但旧 WebView 和兼容场景仍需要关注。

---

## 16. 如何解决？

### 方案一：正确配置 viewport

```html
<meta
  name="viewport"
  content="width=device-width,
           initial-scale=1"
/>
```

### 方案二：Pointer Events

```javascript
button.addEventListener(
  "pointerup",
  handler
);
```

### 方案三：Touch Event

```javascript
button.addEventListener(
  "touchend",
  handler
);
```

但不建议所有场景都直接使用 touchend，因为可能出现：

```text
滚动误触
事件冲突
重复触发
可访问性问题
```

---

# 六、JSBridge 是什么？

## 17. JSBridge 的作用

JSBridge 是：

> **JavaScript 与 Native 之间的通信桥梁。**

例如：

```javascript
bridge.call(
  "getLocation",
  {},
  result => {
    console.log(result);
  }
);
```

流程：

```text
H5 JavaScript
      ↓
JSBridge
      ↓
WebView 通信机制
      ↓
Native
      ↓
系统定位 API
```

---

# 七、为什么需要 JSBridge？

H5 直接使用 Native 系统能力通常受到限制。

例如：

```text
扫码
相机
定位
支付
分享
蓝牙
文件系统
推送
```

因此：

```text
H5
 ↓
JSBridge
 ↓
Native
 ↓
系统 API
```

JSBridge 本质上是：

> **Web API 和 Native API 之间的适配层。**

---

# 八、JSBridge 双向通信原理

这是 Hybrid 面试最核心的问题。

## 18. 双向通信是什么？

包括两个方向：

```text
JS → Native
```

以及：

```text
Native → JS
```

---

## 19. JS 如何调用 Native？

例如：

```javascript
bridge.call(
  "getUserInfo",
  {},
  callback
);
```

Bridge 将调用转换成统一消息：

```json
{
  "method": "getUserInfo",
  "params": {},
  "callbackId": "cb_10001"
}
```

然后：

```text
JavaScript
     ↓
JSBridge
     ↓
WebView 通道
     ↓
Native
     ↓
执行 getUserInfo
```

---

## 20. 为什么需要 callbackId？

因为可能同时调用：

```text
getUserInfo
getLocation
scanQRCode
getDeviceInfo
```

请求顺序：

```text
A
B
C
```

返回顺序可能是：

```text
C
A
B
```

因此需要：

```text
callbackId
```

例如：

```text
请求 A
callbackId = 1001

请求 B
callbackId = 1002

请求 C
callbackId = 1003
```

Native 返回：

```json
{
  "callbackId": "1002",
  "result": {}
}
```

JS 就可以：

```text
1002
 ↓
找到 callbackMap
 ↓
执行对应回调
```

---

## 21. Native 如何调用 JS？

Native 可以调用 WebView 中的 JavaScript：

```javascript
window.__bridgeCallback__(
  "cb_10001",
  {
    "name": "Tom"
  }
);
```

JS：

```javascript
const callbackMap = new Map();

window.__bridgeCallback__ =
  function(callbackId, result) {

    const callback =
      callbackMap.get(callbackId);

    if (callback) {
      callback(result);

      callbackMap.delete(callbackId);
    }
  };
```

完整流程：

```text
JS 发起请求
     ↓
生成 callbackId
     ↓
callback 存入 Map
     ↓
Native 执行
     ↓
Native 返回 callbackId
     ↓
JS 查找 Map
     ↓
执行对应 callback
```

---

# 九、Promise 版 JSBridge

现代项目通常不会直接暴露大量 callback。

可以封装：

```javascript
function call(method, params) {
  return new Promise(
    (resolve, reject) => {
      const callbackId =
        createCallbackId();

      callbackMap.set(callbackId, {
        resolve,
        reject
      });

      nativeCall({
        method,
        params,
        callbackId
      });
    }
  );
}
```

业务层：

```javascript
const userInfo =
  await bridge.call(
    "getUserInfo",
    {}
  );
```

优势：

```text
业务代码简单
错误处理统一
支持 async/await
```

---

# 十、JSBridge 的事件机制

除了：

```text
Request
   ↓
Response
```

还需要：

```text
Native
   ↓
主动通知
   ↓
H5
```

例如：

```text
App 进入后台
App 回到前台
登录状态变化
网络变化
支付结果
```

设计：

```javascript
bridge.on(
  "appBackground",
  handler
);
```

Native：

```text
emit("appBackground")
```

因此一个完整 Bridge 应支持：

```text
call()
on()
off()
emit()
supports()
```

---

# 十一、JSBridge 常见底层实现

## 22. URL Scheme

例如：

```text
myapp://bridge?
method=getUserInfo&
callbackId=1001
```

Native 拦截：

```text
URL
 ↓
解析 method
 ↓
解析 params
 ↓
调用 Native
```

优点：

- 简单
- 兼容性较好

缺点：

- 参数长度限制
- URL 编码复杂
- 不适合大量数据

---

## 23. iOS WKWebView MessageHandler

JavaScript：

```javascript
window.webkit
  .messageHandlers
  .bridge
  .postMessage({
    method: "getUserInfo",
    params: {}
  });
```

流程：

```text
JS
 ↓
postMessage
 ↓
WKWebView
 ↓
Native
```

---

## 24. Android JavaScript Interface

Native 向 WebView 注入对象：

```text
window.AndroidBridge
```

H5：

```javascript
window.AndroidBridge
  .getUserInfo();
```

需要特别注意：

```text
安全
线程
参数校验
版本兼容
```

---

# 十二、如何设计一个通用 JSBridge？

推荐：

```text
Bridge
├── call
├── on
├── off
├── supports
├── callbackMap
├── timeout
├── errorHandler
├── version
└── logger
```

统一协议：

```json
{
  "method": "getUserInfo",
  "params": {},
  "callbackId": "cb_1001"
}
```

统一响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

---

## 25. Bridge 超时怎么处理？

```javascript
function call(method, params) {
  return new Promise(
    (resolve, reject) => {

      const callbackId =
        createCallbackId();

      const timer =
        setTimeout(() => {
          callbackMap.delete(callbackId);

          reject(
            new Error("Bridge timeout")
          );
        }, 5000);

      callbackMap.set(
        callbackId,
        {
          resolve(result) {
            clearTimeout(timer);
            resolve(result);
          },
          reject
        }
      );

      nativeCall({
        method,
        params,
        callbackId
      });
    }
  );
}
```

---

## 26. Native 不支持某个 API 怎么办？

使用：

```text
能力检测
```

例如：

```javascript
if (
  bridge.supports("scanQRCode")
) {
  bridge.call("scanQRCode");
} else {
  fallback();
}
```

比：

```text
判断 UA
判断 iOS
判断 Android
```

更加可靠。

---

## 面试标准回答：JSBridge 双向通信

> JSBridge 是 H5 与 Native 之间的通信协议层。H5 调用 Native 时，会把 method、params 和 callbackId 封装成消息，通过 WebView 提供的通信机制发送给 Native。Native 根据 method 路由到具体能力，执行完成后携带 callbackId 和结果回传给 H5，H5 再根据 callbackId 找到对应的 Promise 或 callback。
>
> Native 主动调用 H5 时，则通过 evaluateJavascript 或 WebView 提供的 JS 执行机制调用 H5 中预先注册的方法，也可以设计统一事件机制。因此完整的 JSBridge 不只是 JS 调 Native，还包括 Native 回调 JS、Promise 管理、事件、超时、错误处理、版本兼容和安全控制。

---

# 十三、H5 页面首屏优化

## 27. H5 首屏经历哪些阶段？

```text
DNS
 ↓
TCP
 ↓
TLS
 ↓
HTTP Request
 ↓
HTML
 ↓
CSS
 ↓
JavaScript
 ↓
JavaScript 执行
 ↓
Style
 ↓
Layout
 ↓
Paint
 ↓
Composite
```

Hybrid 还包括：

```text
Native
 ↓
创建 WebView
 ↓
WebView 初始化
 ↓
H5 加载
```

---

## 28. 如何优化首屏？

### 减少 JS 体积

```text
Tree Shaking
Code Splitting
压缩
移除无用依赖
```

---

### 路由懒加载

```javascript
{
  path: "/detail",

  component: () =>
    import("./Detail.vue")
}
```

---

### 图片优化

使用：

```text
WebP
AVIF
CDN
缩略图
懒加载
```

---

### 预加载

```html
<link
  rel="preload"
  href="/main.js"
  as="script"
/>
```

注意：

> preload 不能滥用。

---

### preconnect

```html
<link
  rel="preconnect"
  href="https://cdn.example.com"
/>
```

减少：

```text
DNS
TCP
TLS
```

连接成本。

---

# 十四、WebView 预热

## 29. 为什么 WebView 首次启动慢？

因为：

```text
Native 创建 WebView
 ↓
浏览器内核初始化
 ↓
进程
 ↓
缓存
 ↓
JavaScript 环境
```

因此可以：

```text
App 启动
 ↓
提前创建 WebView
 ↓
用户打开页面
 ↓
复用 WebView
```

但是需要考虑：

```text
内存增加
状态污染
生命周期复杂
```

---

# 十五、动画为什么会卡？

## 30. 浏览器渲染流程

```text
JavaScript
   ↓
Style
   ↓
Layout
   ↓
Paint
   ↓
Composite
```

如果动画每一帧都触发：

```text
Layout
 ↓
Paint
```

就容易卡顿。

---

## 31. 为什么推荐 transform？

不推荐频繁修改：

```css
left
top
width
height
```

例如：

```css
.box {
  transform:
    translateX(100px);
}
```

或者：

```css
.box {
  opacity: 0.5;
}
```

通常更容易在合成阶段处理。

注意：

> transform 和 opacity 通常性能更好，但具体情况仍需要使用 Performance 工具验证。

---

# 十六、60 FPS 与 16.67ms

如果目标：

```text
60 FPS
```

则：

```text
1000 / 60
≈ 16.67ms
```

即：

> 一帧最好在约 16.67ms 的预算内完成。

如果：

```text
一帧耗时 40ms
```

就可能掉帧。

---

# 十七、requestAnimationFrame

不推荐：

```javascript
setInterval(() => {
  animate();
}, 16);
```

推荐：

```javascript
function animate() {
  update();

  requestAnimationFrame(
    animate
  );
}

requestAnimationFrame(
  animate
);
```

原因：

> requestAnimationFrame 会配合浏览器绘制节奏执行。

---

# 十八、重排与重绘

## 32. 什么是 Reflow / Layout？

修改布局相关属性：

```text
width
height
top
left
font-size
```

可能导致浏览器重新计算布局。

---

## 33. 什么是 Repaint？

例如修改：

```text
color
background
border-color
```

可能不需要重新计算布局，但需要重新绘制。

---

## 34. 什么是 Layout Thrashing？

错误代码：

```javascript
for (const el of elements) {
  el.style.width = "100px";

  console.log(
    el.offsetWidth
  );
}
```

过程：

```text
写
 ↓
读
 ↓
Layout
 ↓
写
 ↓
读
 ↓
Layout
```

正确思路：

```text
先批量写
再批量读
```

```javascript
for (const el of elements) {
  el.style.width = "100px";
}

for (const el of elements) {
  console.log(
    el.offsetWidth
  );
}
```

---

# 十九、用户交互优化

## 35. 如何防止重复提交？

```javascript
let loading = false;

async function submit() {
  if (loading) {
    return;
  }

  loading = true;

  try {
    await request();
  } finally {
    loading = false;
  }
}
```

---

## 36. 为什么用户点击后需要立即反馈？

错误体验：

```text
点击
 ↓
没有任何反应
 ↓
用户再次点击
```

应该：

```text
点击
 ↓
按钮状态变化
 ↓
Loading
 ↓
请求
 ↓
结果
```

常见：

```text
按钮禁用
Loading
Skeleton
Toast
Optimistic UI
```

---

# 二十、防抖与节流

## 37. 防抖 Debounce

适合：

```text
搜索
输入框
```

```javascript
function debounce(fn, delay) {
  let timer;

  return (...args) => {
    clearTimeout(timer);

    timer = setTimeout(
      () => fn(...args),
      delay
    );
  };
}
```

---

## 38. 节流 Throttle

适合：

```text
scroll
resize
mousemove
```

```javascript
function throttle(fn, delay) {
  let last = 0;

  return (...args) => {
    const now = Date.now();

    if (now - last >= delay) {
      last = now;

      fn(...args);
    }
  };
}
```

---

# 二十一、滚动性能优化

不要在 scroll 中执行大量计算：

```javascript
window.addEventListener(
  "scroll",
  handler
);
```

可以：

```javascript
let ticking = false;

window.addEventListener(
  "scroll",
  () => {

    if (ticking) return;

    ticking = true;

    requestAnimationFrame(() => {
      update();

      ticking = false;
    });
  }
);
```

更推荐：

```text
IntersectionObserver
```

用于：

```text
图片懒加载
曝光统计
无限滚动
元素进入视口
```

---

# 二十二、passive 事件是什么？

```javascript
window.addEventListener(
  "touchmove",
  handler,
  {
    passive: true
  }
);
```

表示：

> 当前监听器不会调用 preventDefault。

浏览器可以更快处理滚动。

但是：

```javascript
event.preventDefault();
```

就不能与 passive: true 一起使用。

---

# 二十三、移动端软键盘问题

## 39. 常见问题

```text
input 获得焦点
 ↓
键盘弹出
 ↓
页面高度变化
 ↓
fixed 元素位置异常
```

不同系统：

```text
iOS
Android
不同 WebView
```

行为可能不同。

---

## 40. 如何解决？

可以使用：

```javascript
window.visualViewport
```

例如：

```javascript
window.visualViewport?.addEventListener(
  "resize",
  () => {
    const height =
      window.visualViewport.height;

    // 根据可视区域重新布局
  }
);
```

如果 Native 可以提供：

```text
键盘高度
键盘显示状态
```

也可以通过 Bridge 通知 H5。

---

# 二十四、长列表如何优化？

不要：

```text
10000 条数据
 ↓
渲染 10000 个 DOM
```

应该：

```text
虚拟列表
```

即：

```text
10000 条数据
       ↓
实际只渲染可视区域
       ↓
几十个 DOM
```

滚动时：

```text
计算可视区域
 ↓
更新数据
 ↓
复用 DOM
```

---

# 二十五、图片优化

策略：

```text
WebP
AVIF
CDN
压缩
缩略图
懒加载
```

例如：

```html
<img
  loading="lazy"
  src="image.webp"
/>
```

列表：

```text
缩略图
 ↓
用户进入详情
 ↓
加载高清图
```

---

# 二十六、H5 弱网优化

移动网络：

```text
Wi-Fi
4G
5G
地铁
电梯
网络切换
断网
```

因此：

```text
请求不一定成功
```

---

## 41. 请求失败需要区分

```text
Network Error
HTTP Error
Business Error
Timeout
Cancel
Permission Error
```

不同错误：

```text
网络错误 → 检查网络
401 → 登录
业务错误 → 业务提示
超时 → 重试
```

---

## 42. 请求取消

页面离开：

```text
Detail
  ↓
请求中
  ↓
用户返回
```

可以：

```javascript
const controller =
  new AbortController();

fetch(url, {
  signal: controller.signal
});

// 页面销毁
controller.abort();
```

---

# 二十七、网络重试

不能无限重试。

可以：

```text
1 秒
 ↓
2 秒
 ↓
4 秒
 ↓
8 秒
```

指数退避：

```text
delay = base × 2^n
```

增加随机抖动：

```text
Jitter
```

避免大量用户同时重试。

---

# 二十八、H5 缓存

常见：

```text
HTTP Cache
Service Worker
Cache Storage
IndexedDB
LocalStorage
SessionStorage
Native Cache
```

建议：

```text
静态资源
→ CDN + HTTP Cache

复杂业务数据
→ IndexedDB

敏感 Token
→ Native 安全存储

大文件
→ 文件缓存
```

---

# 二十九、Hybrid 生命周期

## 43. Native 生命周期与 H5 生命周期不同

Native：

```text
App Start
 ↓
Activity / ViewController
 ↓
WebView
```

H5：

```text
DOMContentLoaded
 ↓
load
 ↓
mounted
```

Native 进入后台：

```text
App Background
```

不一定等价：

```text
H5 unload
```

因此 App 生命周期最好：

```text
Native
 ↓
JSBridge Event
 ↓
H5
```

例如：

```javascript
bridge.on(
  "appBackground",
  pauseTask
);

bridge.on(
  "appForeground",
  resumeTask
);
```

---

# 三十、Hybrid 返回问题

可能存在两套栈：

```text
Native Navigation Stack
```

和：

```text
H5 History Stack
```

例如：

```text
Native
   ↓
WebView A
   ↓
WebView B

H5
   ↓
Page A
   ↓
Page B
```

需要明确：

```text
浏览器返回
还是 Native 返回
```

否则可能：

```text
返回两次
页面跳过
白屏
栈错乱
```

---

# 三十一、Hybrid 白屏问题

## 44. 白屏原因

### 网络

```text
DNS
CDN
超时
断网
```

### 资源

```text
JS 加载失败
CSS 加载失败
Chunk 加载失败
```

### JavaScript

```text
运行时异常
Promise 异常
版本不兼容
```

### WebView

```text
创建失败
内存不足
渲染进程异常
```

### JSBridge

```text
调用 Native 不存在 API
```

---

## 45. 如何解决白屏？

不能只回答：

> 加一个 Loading。

应该建立：

```text
页面加载
 ↓
资源监控
 ↓
JS 监控
 ↓
API 监控
 ↓
Bridge 监控
 ↓
超时
 ↓
降级
 ↓
重试
```

JS：

```javascript
window.addEventListener(
  "error",
  reportError
);

window.addEventListener(
  "unhandledrejection",
  reportPromiseError
);
```

---

# 三十二、Hybrid 安全

## 46. JSBridge 为什么有安全风险？

假设：

```text
恶意 H5
 ↓
调用 JSBridge
 ↓
Native
 ↓
获取敏感能力
```

因此不能：

> 任何 H5 都可以调用任何 Bridge。

---

## 47. 如何保护 JSBridge？

### URL 白名单

```text
https://trusted.example.com
```

才允许使用敏感 Bridge。

### Method 白名单

```text
getDeviceInfo ✓
scanQRCode ✓
pay ✓

executeAnyCode ✗
```

### 参数校验

Native 必须校验：

```text
method
params
origin
```

### 权限校验

```text
用户登录
系统权限
用户确认
```

---

# 三十三、XSS 与 Hybrid

普通 Web：

```text
XSS
 ↓
Cookie / DOM
```

Hybrid：

```text
XSS
 ↓
恶意 JavaScript
 ↓
JSBridge
 ↓
Native API
```

因此风险更高。

需要：

```text
输入过滤
输出编码
CSP
HTTPS
URL 白名单
Bridge 白名单
```

---

# 三十四、H5 如何与 Native 统一登录？

一种思路：

```text
Native 登录
 ↓
安全存储 Token
 ↓
Bridge
 ↓
H5 获取短期凭证
```

不要简单：

```text
所有页面 LocalStorage 保存长期敏感 Token
```

需要考虑：

```text
Token 过期
Token 刷新
退出登录
账号切换
多 WebView
```

---

# 三十五、Bridge 如何传递大数据？

不建议：

```text
Native
 ↓
一次传 50MB JSON
 ↓
JSBridge
```

可能导致：

```text
JSON 序列化
JS 主线程阻塞
内存暴涨
WebView 卡顿
```

建议：

```text
Native
 ↓
文件 / URL / 本地缓存引用
 ↓
H5
```

---

# 三十六、性能监控

建议监控：

```text
WebView 创建耗时
HTML TTFB
资源加载耗时
首屏时间
FCP
LCP
JS Error
Long Task
API 耗时
Bridge 成功率
Bridge 延迟
白屏率
资源加载失败率
```

不要只看平均值。

还应该关注：

```text
P50
P95
P99
```

---

# 三十七、如何定位页面卡顿？

从三个层面：

## JavaScript

检查：

```text
Long Task
大量循环
JSON.parse
复杂计算
内存泄漏
```

## Rendering

检查：

```text
Layout Thrashing
大面积重绘
复杂阴影
滤镜
```

## Network

检查：

```text
接口慢
图片大
JS 大
CDN 慢
```

工具：

```text
Chrome DevTools
Performance
Network
Memory
Lighthouse
Safari Web Inspector
Android WebView Debug
```

---

# 三十八、H5 Hybrid 高频面试题

## 基础

1. 什么是 Hybrid？
2. Hybrid 和 Native 有什么区别？
3. Hybrid 和 React Native 有什么区别？
4. WebView 是什么？
5. Hybrid 最大的问题是什么？

## 移动端

6. 刘海屏如何处理？
7. Safe Area 是什么？
8. viewport-fit=cover 是什么？
9. 1px 边框怎么处理？
10. DPR 是什么？
11. 300ms 延迟是什么？
12. rem、vw、px 如何选择？
13. 移动端软键盘怎么处理？

## JSBridge

14. JSBridge 是什么？
15. JS 如何调用 Native？
16. Native 如何调用 JS？
17. 为什么需要 callbackId？
18. Promise 如何实现？
19. Native 主动通知 H5 怎么做？
20. Bridge 超时怎么办？
21. Bridge 版本不兼容怎么办？
22. Native 不支持 API 怎么办？
23. Bridge 如何保证安全？

## 性能

24. H5 首屏怎么优化？
25. WebView 启动慢怎么优化？
26. 动画如何保证 60FPS？
27. requestAnimationFrame 是什么？
28. 什么是 Layout Thrashing？
29. 为什么 transform 性能更好？
30. 长列表怎么优化？
31. Scroll 怎么优化？
32. 图片怎么优化？

## 网络

33. 弱网怎么办？
34. 请求超时怎么办？
35. 请求取消怎么做？
36. 网络重试怎么设计？
37. 离线缓存怎么做？

## 稳定性

38. Hybrid 为什么白屏？
39. 如何监控白屏？
40. JS 错误怎么监控？
41. Bridge 错误怎么监控？
42. WebView 崩溃怎么办？
43. H5 和 Native 版本不兼容怎么办？

---

# 三十九、项目面试回答模板

> 我们项目采用 Hybrid 架构，业务页面主要使用 H5 开发，通过 Native WebView 承载。H5 负责业务页面和交互，涉及扫码、定位、文件、登录等系统能力时，通过统一的 JSBridge 调用 Native。
>
> JSBridge 在设计上采用 method、params、callbackId 的统一协议。H5 发起调用时生成 callbackId，并将 Promise 的 resolve 和 reject 保存到 callbackMap。Native 收到消息后根据 method 路由到具体能力，执行完成以后携带 callbackId 返回结果，H5 再找到对应 Promise 完成调用。
>
> 除了请求响应模式，我们还支持 Native 主动通知 H5，例如 App 前后台切换、登录状态变化和网络状态变化，通过统一事件机制处理。
>
> 移动端适配方面，我们通过 viewport-fit=cover 和 env(safe-area-inset-*) 处理刘海屏和 Home Indicator；通过 DPR 和伪元素 transform 方案处理 1px 边框；对于传统 300ms 点击延迟，则结合 viewport、现代 Pointer Events 和实际 WebView 兼容情况处理。
>
> 性能方面，我会从 Native 创建 WebView、网络加载、资源体积、JavaScript 执行和浏览器渲染几个阶段优化。例如 WebView 预热、代码分包、路由懒加载、图片压缩、CDN、接口并行、Skeleton、虚拟列表、requestAnimationFrame，并避免 Layout Thrashing。
>
> 稳定性方面，我们监控 JS Error、Promise Error、资源加载错误、接口错误和 Bridge 错误，并结合 WebView 创建耗时、首屏耗时和白屏率定位问题。安全方面对 H5 来源、Bridge 方法和参数做白名单校验，避免恶意页面调用 Native 敏感能力。

---

# 四十、最终知识体系

```text
                     Hybrid
                        │
       ┌────────────────┼────────────────┐
       │                │                │
      H5            JSBridge          Native
       │                │                │
       ├── CSS          ├── call        ├── Camera
       ├── JS           ├── callback    ├── Location
       ├── Vue          ├── Promise     ├── Payment
       ├── Safe Area    ├── event       ├── Push
       ├── 1px          ├── timeout     └── File
       ├── Touch        ├── security
       ├── Animation    └── version
       ├── Performance
       ├── Cache
       ├── Network
       └── Rendering
```

Hybrid 面试最重要的主线是：

> **WebView → H5 → JSBridge → Native → 生命周期 → 性能 → 网络 → 稳定性 → 安全**

如果面试官从任何一个点继续深入，都应该能够顺着这条技术链路继续回答。
