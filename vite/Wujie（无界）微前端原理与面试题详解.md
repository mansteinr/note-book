# Wujie（无界）微前端原理与面试题详解

> 适合：高级前端工程师 / 前端架构师 / Vue3 前端岗位面试  
> 重点：Wujie 原理、iframe、Web Components、JS/CSS 隔离、路由、通信、保活、性能优化、qiankun 对比

---

# 一、什么是 Wujie

Wujie（无界）是一套微前端框架，用于解决大型前端项目中多个独立应用之间的：

- 独立开发
- 独立部署
- 独立发布
- 技术栈共存
- JS 隔离
- CSS 隔离
- 路由隔离
- 应用通信
- 生命周期管理
- 应用保活

等问题。

例如一个大型企业管理平台：

```text
                         主应用
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
          用户中心       订单中心       数据中心
            Vue3          React          Vue3
```

每一个业务系统都可以作为独立的子应用。

---

# 二、为什么需要微前端

传统大型前端项目通常是一个巨大的单体应用：

```text
                    一个前端项目
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
    用户模块           订单模块           数据模块
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                       Vue
```

随着项目越来越大，会出现：

```text
代码越来越多
      ↓
构建越来越慢
      ↓
发布越来越慢
      ↓
团队之间互相影响
      ↓
升级成本越来越高
      ↓
不同技术栈难以共存
```

微前端的目标就是把：

```text
一个巨型前端
```

拆成：

```text
                  主应用
                    │
       ┌────────────┼────────────┐
       │            │            │
       ▼            ▼            ▼
      A系统        B系统        C系统
       │            │            │
      Vue          React        Vue
```

每个系统可以独立维护。

---

# 三、Wujie 的核心思想

Wujie 最核心的设计可以概括成：

```text
Wujie
  │
  ├── iframe
  │     ↓
  │   JS运行环境隔离
  │
  ├── Web Components
  │     ↓
  │   DOM / CSS隔离
  │
  ├── Proxy / DOM代理
  │     ↓
  │   iframe JS 与真实DOM连接
  │
  ├── 路由处理
  │
  ├── 生命周期
  │
  ├── 应用通信
  │
  └── 保活 / 预加载
```

面试中最值得记住的一句话：

> **Wujie 利用 iframe 提供独立的 JavaScript 运行环境，利用 Web Components 承载子应用 DOM 并实现样式隔离，再通过代理机制把 iframe 中运行的 JavaScript 与子应用 DOM 连接起来。**

---

# 四、Wujie 整体架构

可以把 Wujie 理解成：

```text
                         主应用
                           │
                           ▼
                    Web Component
                           │
                     Shadow DOM
                           │
                   ┌───────┴───────┐
                   │               │
                   ▼               ▼
                子应用 DOM      iframe
                                   │
                                   ▼
                                window
                                   │
                  ┌────────────────┼────────────────┐
                  │                │                │
                  ▼                ▼                ▼
                document        history          location
                  │
                  ▼
              子应用 JS
```

其中：

```text
iframe
    ↓
负责运行环境隔离

Web Components
    ↓
负责 DOM / CSS

Proxy / DOM代理
    ↓
负责连接 iframe 与 DOM
```

---

# 五、为什么 Wujie 使用 iframe

这是 Wujie 最核心的知识点。

假设两个子应用都直接运行在主应用的 window：

```text
主应用 window
      │
      ├── 子应用 A
      │
      └── 子应用 B
```

A：

```javascript
window.user = 'A';
```

B：

```javascript
window.user = 'B';
```

可能造成：

```text
A修改window
      ↓
影响B
```

这就是全局变量污染。

---

# 六、iframe 的隔离能力

iframe 天然拥有独立的：

```text
window
document
history
location
```

因此：

```text
主应用
 │
 ├── iframe A
 │      └── window A
 │
 └── iframe B
        └── window B
```

于是：

```javascript
// A
window.user = 'A';

// B
window.user = 'B';
```

实际上是：

```text
window A
    ≠
window B
```

所以两个子应用拥有相对独立的 JS 运行环境。

---

# 七、为什么不直接使用 iframe

这是面试非常喜欢问的问题。

如果直接使用：

```html
<iframe src="http://user.example.com"></iframe>
```

确实可以实现很强的隔离。

但是问题也比较明显：

```text
1. DOM完全独立
2. 主子应用页面融合困难
3. 页面高度处理麻烦
4. 弹窗处理麻烦
5. DOM操作不方便
6. 页面布局不方便
7. 主子应用交互成本较高
```

所以 Wujie 不是简单的：

```text
Wujie = iframe
```

而是：

```text
Wujie
 =
iframe
+
Web Components
+
DOM Proxy
+
生命周期
+
路由
+
通信
```

---

# 八、Web Components 在 Wujie 中的作用

Web Components 可以提供：

```text
Custom Elements
Shadow DOM
HTML Templates
```

Wujie 利用 Web Components 将子应用集成到主应用页面中。

可以理解为：

```text
主应用
  │
  ├── 主应用 DOM
  │
  └── WebComponent
         │
         └── Shadow DOM
                │
                └── 子应用 DOM
```

这样既能够：

```text
集成到主应用
```

又能够：

```text
保持一定的隔离边界
```

---

# 九、Wujie 的 CSS 隔离

假设：

### 子应用 A

```css
.button {
    color: red;
}
```

### 子应用 B

```css
.button {
    color: blue;
}
```

如果两个子应用 CSS 全部进入主应用：

```text
document
   │
   ├── A CSS
   │
   └── B CSS
```

可能产生：

```text
CSS污染
```

Wujie 利用 Web Components / Shadow DOM：

```text
WebComponent A
      │
      └── Shadow DOM
             │
             └── A CSS

WebComponent B
      │
      └── Shadow DOM
             │
             └── B CSS
```

从而减少 CSS 冲突。

---

# 十、CSS 隔离并不是绝对的

实际项目中仍然要注意：

```text
body
html
:root

Teleport

Modal

Tooltip

Dropdown

第三方组件库

动态插入CSS
```

例如 Vue：

```vue
<Teleport to="body">
    <Dialog />
</Teleport>
```

组件实际可能被挂到：

```text
document.body
```

这样就可能脱离原来的 Shadow DOM 边界。

所以项目中需要统一处理：

```text
弹窗容器
Teleport容器
第三方组件库
全局CSS
z-index
```

---

# 十一、DOM Proxy 是什么

这是 Wujie 比较核心的技术点。

子应用代码：

```javascript
document.querySelector('#app');
```

普通 iframe：

```text
iframe
   │
   └── iframe.document
```

Wujie 需要将：

```text
子应用JS
    ↓
iframe document
    ↓
DOM代理
    ↓
WebComponent
    ↓
真实DOM
```

连接起来。

因此子应用代码仍然可以按照普通前端应用的方式操作：

```javascript
document.querySelector();
document.createElement();
document.body;
document.head;
```

Wujie 在运行时对相关行为进行代理。

---

# 十二、Wujie 的 JavaScript 隔离

Wujie 的 JS 隔离核心依赖 iframe。

例如：

```javascript
window.xxx = 123;
```

这个 `window` 主要属于：

```text
子应用 iframe.window
```

而不是：

```text
主应用 top.window
```

所以：

```text
子应用A
 ↓
iframe A
 ↓
window A

子应用B
 ↓
iframe B
 ↓
window B
```

两个应用之间天然具有较强的隔离能力。

---

# 十三、Wujie 的路由隔离

iframe 本身拥有：

```javascript
window.history
window.location
```

所以：

```text
主应用
  │
  └── 主应用 history

子应用
  │
  └── iframe history
```

例如子应用：

```javascript
history.pushState(
    {},
    '',
    '/user/detail'
);
```

主要操作的是自己的 history 环境。

因此可以实现：

```text
主应用路由
      +
子应用路由
```

之间的隔离与同步。

---

# 十四、Wujie 的生命周期

从架构上可以理解为：

```text
加载
 ↓
初始化
 ↓
mount
 ↓
运行
 ↓
unmount
```

常见生命周期概念：

```text
beforeLoad
afterLoad

beforeMount
afterMount

beforeUnmount
afterUnmount
```

不同版本具体 API 可能有所不同。

实际开发应该以当前版本官方 API 为准。

---

# 十五、Wujie 的保活机制

普通微前端：

```text
进入A
 ↓
创建A

离开A
 ↓
销毁A
```

再次进入：

```text
重新加载A
```

Wujie 可以通过保活：

```text
进入A
 ↓
创建A
 ↓
离开A
 ↓
保留A实例
 ↓
进入B
 ↓
再次进入A
 ↓
恢复A
```

所以：

```text
保活
=
实例不销毁
```

---

# 十六、保活适合什么场景

例如：

```text
订单编辑
在线表单
数据分析
流程设计器
代码编辑器
Canvas编辑器
复杂配置页面
```

例如：

```text
订单页面
 ↓
填写20分钟
 ↓
切换用户中心
 ↓
回来
```

如果不保活：

```text
订单状态丢失
```

如果保活：

```text
继续之前的编辑状态
```

---

# 十七、保活的缺点

保活意味着：

```text
应用实例仍然存在
```

因此下面资源可能继续工作：

```text
WebSocket

setInterval

setTimeout

MutationObserver

ResizeObserver

IntersectionObserver

Worker

EventBus

ECharts

Canvas

Fabric.js
```

例如：

```javascript
setInterval(() => {
    requestData();
}, 1000);
```

用户离开页面：

```text
子应用仍然alive
      ↓
定时器继续执行
```

最终可能导致：

```text
CPU升高
内存增加
WebSocket增加
后台请求增加
```

所以高级项目应该设计：

```text
active
   ↓
正常运行

inactive
   ↓
暂停高频任务

destroy
   ↓
彻底释放资源
```

---

# 十八、Wujie 的应用通信

常见方式：

```text
Props
EventBus
postMessage
window.parent
```

---

## 18.1 Props

适合：

```text
主应用
   ↓
子应用
```

例如：

```javascript
props: {
    userId: 1001,
    token: 'xxx'
}
```

子应用读取：

```javascript
$wujie.props.userId
```

适合：

```text
初始化配置
用户信息
权限信息
业务参数
```

---

# 十九、EventBus

如果多个应用之间需要通信：

```text
                 EventBus
              /     |      \
             /      |       \
          主应用    A        B
```

例如：

```text
用户登录
订单状态变化
权限变化
主题变化
语言变化
```

可以通过事件通知。

但是要注意：

```text
不要让EventBus变成全局垃圾场
```

应该：

```text
事件命名规范
事件生命周期管理
及时取消监听
避免循环依赖
```

---

# 二十、postMessage

如果涉及窗口之间通信，可以使用：

```javascript
window.postMessage();
```

适合：

```text
不同window
iframe
跨域场景
```

但需要注意：

```text
origin校验
消息格式
权限校验
```

不能无脑：

```javascript
window.addEventListener(
    'message',
    handler
);
```

而应该校验：

```javascript
event.origin
```

---

# 二十一、Wujie + WebSocket

实际项目中一个比较典型的问题：

```text
主应用
  │
  ├── 子应用A → WebSocket
  ├── 子应用B → WebSocket
  └── 子应用C → WebSocket
```

可能出现：

```text
一个浏览器
 ↓
多个WebSocket连接
```

如果有几十个子应用：

```text
连接数量
 ↓
明显增加
```

---

# 二十二、推荐的 WebSocket 架构

可以让主应用统一维护：

```text
                      WebSocket
                           │
                           ▼
                        主应用
                           │
                      MessageBus
                 ┌─────────┼─────────┐
                 ▼         ▼         ▼
                 A         B         C
```

主应用负责：

```text
连接
重连
心跳
鉴权
消息解析
异常处理
```

子应用只负责：

```text
订阅自己关心的数据
```

例如：

```text
订单消息
 ↓
Order App

监控消息
 ↓
Monitor App

告警消息
 ↓
Alarm App
```

这样可以减少：

```text
WebSocket连接
重复解析
心跳
服务器连接压力
```

---

# 二十三、Wujie 性能优化

主要从几个方向优化。

## 1. 懒加载

用户进入应用时再加载：

```text
首页
 ↓
用户点击订单
 ↓
加载订单应用
```

---

## 2. preload

用户还没有进入子应用：

```text
首页
 ↓
后台预加载订单资源
```

用户点击：

```text
订单
 ↓
快速展示
```

---

## 3. 代码分包

减少：

```text
单个JS包体积
```

---

## 4. CDN

静态资源：

```text
JS
CSS
图片
字体
```

使用 CDN。

---

## 5. gzip / Brotli

降低网络传输体积。

---

## 6. 应用共享

避免多个子应用重复加载：

```text
Vue
React
组件库
公共SDK
```

但需要注意版本兼容。

---

# 二十四、Wujie 与 qiankun 对比

这是非常高频的面试题。

| 特性 | Wujie | qiankun |
|---|---|---|
| 核心技术 | iframe + Web Components | single-spa + 沙箱 |
| JS隔离 | iframe | Proxy等机制 |
| CSS隔离 | Web Components / Shadow DOM | CSS隔离 |
| 路由 | iframe环境 | 主子应用协调 |
| 保活 | 支持 | 需要结合方案 |
| 多应用同时运行 | 支持 | 支持 |
| 子应用嵌套 | 支持 | 相对复杂 |
| 浏览器原生隔离 | 较强 | 相对较少 |
| 改造成本 | 相对较低 | 视项目而定 |

---

# 二十五、Wujie 的优点

```text
1. JS隔离能力强
2. CSS隔离能力强
3. 路由隔离
4. 子应用技术栈可以不同
5. 支持应用保活
6. 支持多应用同时运行
7. 支持子应用嵌套
8. 支持预加载
9. 浏览器原生隔离能力利用充分
```

---

# 二十六、Wujie 的缺点

```text
1. iframe有初始化成本
2. 多应用会增加内存
3. 保活应用越多内存越高
4. 跨域场景需要额外处理
5. 第三方组件库可能需要适配
6. Teleport / Modal需要特别注意
7. 多层嵌套会增加复杂度
8. 调试比普通单体应用复杂
```

---

# 二十七、Wujie 高频面试题 1

## Q：Wujie 是什么？核心原理是什么？

### 标准回答

> Wujie 是一个微前端框架，核心使用 iframe、Web Components 和 DOM Proxy。
>
> iframe 主要提供独立的 JavaScript 运行环境，每个子应用拥有自己的 window、document、history 和 location，从而实现较强的 JS 隔离。
>
> Web Components 负责承载子应用 DOM，并利用 Shadow DOM 等能力实现 CSS 隔离。
>
> 最后通过 DOM Proxy 等机制，把 iframe 中运行的 JavaScript 和 Web Components 中的 DOM 连接起来。
>
> 所以我一般把 Wujie 总结为：**iframe 负责 JS 隔离，Web Components 负责 DOM/CSS 隔离，Proxy 负责两者连接。**

### 可能追问

> Wujie 是不是简单的 iframe？

回答：

> 不是。iframe 是 Wujie 实现 JS 隔离的重要基础，但 Wujie 还结合了 Web Components、DOM Proxy、生命周期、路由和通信等机制。

---

# 二十八、Wujie 高频面试题 2

## Q：为什么 Wujie 使用 iframe？

### 标准回答

> 因为 iframe 可以天然提供独立的 window、document、history 和 location。
>
> 每个子应用可以运行在独立 iframe 中，因此不同应用之间的全局变量不会直接共享。
>
> 相比完全依赖 Proxy 的 JS 沙箱，iframe 的隔离能力更多来自浏览器原生能力，因此隔离边界比较清晰。

### 追问

> iframe 有什么缺点？

回答：

```text
初始化成本
资源加载成本
DOM集成复杂
弹窗处理复杂
跨域通信复杂
多个iframe增加内存
```

然后补充：

> Wujie 通过 Web Components、预加载、保活等机制改善这些问题。

---

# 二十九、Wujie 高频面试题 3

## Q：既然用了 iframe，为什么还需要 Web Components？

### 标准回答

> iframe 主要解决的是 JS 运行环境隔离，但是 iframe 中的 DOM 属于独立文档，与主应用 DOM 集成不够方便。
>
> Web Components 可以提供独立的 DOM 容器，并结合 Shadow DOM 实现 CSS 隔离。
>
> 因此 Wujie 的两个核心技术职责不同：
>
> ```text
> iframe
> ↓
> JS运行环境
>
> Web Components
> ↓
> DOM / CSS
> ```
>
> 再通过 DOM Proxy 把两者连接起来。

---

# 三十、Wujie 高频面试题 4

## Q：Wujie 如何实现 JS、CSS、DOM 隔离？

### 标准回答

可以分成三个部分：

### JS

```text
iframe
 ↓
独立window
 ↓
JS隔离
```

### CSS

```text
Web Components
 ↓
Shadow DOM
 ↓
CSS隔离
```

### DOM

```text
iframe中的JS
 ↓
DOM Proxy
 ↓
WebComponent
 ↓
真实DOM
```

所以：

```text
JS
 ↓
iframe

CSS
 ↓
Shadow DOM

DOM
 ↓
DOM Proxy
```

---

# 三十一、Wujie 高频面试题 5

## Q：Wujie 如何实现主应用和子应用通信？

### 标准回答

> 我会根据通信场景选择不同方式。
>
> 初始化阶段主应用给子应用传递配置，可以使用 props。
>
> 多个应用运行过程中需要事件通知，可以使用 EventBus。
>
> 如果是窗口之间的通信，可以使用 postMessage。
>
> 实际项目中我会尽量避免子应用直接大量调用 window.parent，因为这样会导致子应用强依赖主应用内部实现，降低微前端的独立性。

架构：

```text
                    主应用
                       │
          ┌────────────┼────────────┐
          │            │            │
        Props       EventBus    postMessage
          │            │            │
          └────────────┼────────────┘
                       │
                    子应用
```

---

# 三十二、Wujie 高频面试题 6

## Q：Wujie 的保活是什么？有什么优缺点？

### 标准回答

> Wujie 的保活核心是切换应用时不真正销毁子应用实例，而是保留 iframe 和应用运行状态，再次进入时恢复之前的实例。
>
> 这样可以很好地解决订单编辑、复杂表单、Canvas 编辑器等页面切换后状态丢失的问题。
>
> 但是保活也会增加内存和 CPU 消耗，因为子应用实例并没有真正销毁。WebSocket、定时器、Observer、Worker 等资源也可能继续运行。
>
> 因此实际项目中应该根据业务场景决定哪些应用保活，并在 inactive 状态暂停高频任务。

---

# 三十三、高级追问：Wujie 子应用白屏怎么办？

可以按照下面流程排查：

```text
                  子应用白屏
                       │
                       ▼
                   Network
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
        HTML          JS           CSS
          │            │            │
          └────────────┼────────────┘
                       ▼
                base / publicPath
                       │
                       ▼
                      CORS
                       │
                       ▼
                  生命周期
                       │
                       ▼
                  mount是否成功
                       │
                       ▼
                     路由
                       │
                       ▼
             第三方组件 / Teleport
```

---

# 三十四、最常见的资源 404 问题

例如：

```text
主应用：

https://example.com/
```

子应用：

```text
https://example.com/user/
```

但是 Vite 配置：

```javascript
export default defineConfig({
    base: '/'
});
```

子应用请求：

```text
/assets/index.js
```

实际正确资源可能是：

```text
/user/assets/index.js
```

于是：

```text
JS 404
 ↓
子应用白屏
```

因此部署微前端时要重点检查：

```text
Vite base
Webpack publicPath
CDN地址
Nginx
静态资源路径
```

---

# 三十五、Wujie + Vite 常见问题

Vue3 + Vite 子应用中重点关注：

```text
vite.config.ts
```

例如：

```javascript
export default defineConfig({
    base: '/user/'
});
```

如果采用不同部署方式，需要根据实际路径调整。

同时注意：

```text
动态import
图片
字体
CSS
Worker
```

这些资源也可能出现路径问题。

---

# 三十六、Wujie + Vue3 常见问题

Vue3 项目：

```text
Vue Router
Pinia
Teleport
Element Plus
ECharts
WebSocket
```

都需要考虑微前端环境。

尤其是：

```text
Teleport
```

例如：

```vue
<Teleport to="body">
    <Dialog />
</Teleport>
```

可能导致：

```text
子应用
 ↓
Shadow DOM
 ↓
Teleport
 ↓
主应用body
```

从而出现：

```text
样式丢失
z-index异常
弹窗位置异常
```

因此建议统一处理弹窗挂载容器。

---

# 三十七、Wujie 内存泄漏问题

重点排查：

```text
WebSocket
setInterval
setTimeout
MutationObserver
ResizeObserver
IntersectionObserver
EventBus
Worker
ECharts
Canvas
Fabric.js
```

例如：

```javascript
onMounted(() => {
    timer = setInterval(loadData, 1000);
});

onUnmounted(() => {
    clearInterval(timer);
});
```

但是如果应用是：

```text
alive
```

那么：

```text
unmount
```

可能并不会按照普通页面销毁逻辑发生。

所以需要设计：

```text
active
inactive
destroy
```

三个状态，而不是只依赖：

```text
mounted
unmounted
```

---

# 三十八、Wujie 项目实战回答模板

面试官：

> 你们项目为什么使用 Wujie？

可以回答：

> 我们项目是一个大型企业级平台，包含多个相对独立的业务系统。为了让不同团队可以独立开发、部署和发布，我们采用了微前端架构。
>
> 在微前端方案上，我们选择 Wujie，主要看重它基于 iframe 和 Web Components 的隔离机制。
>
> 子应用 JavaScript 运行在独立 iframe 中，可以减少不同应用之间的全局变量污染；同时 Web Components 可以提供 DOM 和 CSS 隔离。
>
> 另外项目存在多个子应用同时运行以及页面切换后保留状态的需求，所以 Wujie 的保活和多应用激活能力比较适合我们的业务。
>
> 实际开发过程中，我们重点处理了三个问题。
>
> 第一是子应用资源路径问题，通过 Vite base、静态资源路径和网关配置解决。
>
> 第二是第三方组件库、Teleport 和弹窗样式问题，通过统一弹窗容器和组件规范解决。
>
> 第三是保活产生的资源问题，比如 WebSocket、定时器和 Observer，我们通过应用生命周期管理，在 inactive 状态暂停高频任务，销毁时统一释放资源。
>
> 对于实时数据，我们没有让每个子应用都创建 WebSocket，而是由主应用统一维护连接，然后通过消息总线将数据分发给对应的子应用，这样可以减少连接数量和重复处理。

---

# 三十九、面试官继续追问：为什么不用 qiankun？

推荐回答：

> 我认为不能简单说 Wujie 一定比 qiankun 好。
>
> qiankun 的生态和实践也比较成熟，如果项目已经建立在 qiankun 或 single-spa 体系上，没有必要为了技术选型而迁移。
>
> 我们选择 Wujie 主要是因为项目比较重视 iframe 带来的 JS 隔离、应用保活、多应用同时激活以及子应用之间的隔离边界。
>
> 所以最终还是根据项目需求选择，而不是单纯比较哪个框架更好。

---

# 四十、面试画图

如果面试官要求你画 Wujie 架构，可以画：

```text
                       主应用
                         │
                         ▼
                  Web Components
                         │
                     Shadow DOM
                         │
            ┌────────────┴────────────┐
            │                         │
            ▼                         ▼
        子应用DOM                   iframe
                                      │
                                      ▼
                                   window
                                      │
                          ┌───────────┼───────────┐
                          │           │           │
                          ▼           ▼           ▼
                       document    history     location
                          │
                          ▼
                       子应用JS
                          │
                          ▼
                     DOM Proxy
                          │
                          ▼
                    WebComponent
```

然后用一句话解释：

```text
iframe
→ JS隔离

Web Components
→ DOM/CSS隔离

DOM Proxy
→ JS与DOM连接

生命周期
→ 应用管理

EventBus
→ 应用通信

alive
→ 应用保活
```

---

# 四十一、Wujie 最重要的 6 道面试题

如果时间有限，优先掌握：

| 优先级 | 面试题 |
|---|---|
| ★★★★★ | Wujie 是什么？核心原理是什么？ |
| ★★★★★ | 为什么使用 iframe？ |
| ★★★★★ | 为什么 iframe 后还需要 Web Components？ |
| ★★★★★ | JS、CSS、DOM 如何隔离？ |
| ★★★★☆ | 主子应用如何通信？ |
| ★★★★☆ | 保活怎么实现？有什么问题？ |

---

# 四十二、最终总结

Wujie 最重要的不是 API，而是理解：

```text
                    Wujie
                      │
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
       iframe    WebComponent    Proxy
          │           │           │
          ▼           ▼           ▼
       JS隔离      DOM/CSS      DOM连接
          │           │
          └──────┬────┘
                 ▼
                路由
                 │
                 ▼
              生命周期
                 │
                 ▼
                保活
                 │
                 ▼
                通信
                 │
                 ▼
              性能优化
```

面试时最核心的一句话：

> **Wujie 通过 iframe 获得独立的 JS 运行环境，通过 Web Components 实现 DOM/CSS 隔离，再利用代理机制将子应用运行环境和页面 DOM 连接起来，同时提供路由、生命周期、通信、保活和预加载等微前端能力。**

如果你能进一步结合自己的项目，把 **Vue3 + Wujie + WebSocket + Canvas/Fabric.js + 性能优化**串起来讲，面试时会比单纯背 Wujie API 更容易体现高级前端工程师的项目经验。