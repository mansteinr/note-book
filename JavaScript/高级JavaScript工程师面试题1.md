# 高级JavaScript工程师面试题

## 目录

- [高级JavaScript工程师面试题](#高级javascript工程师面试题)
  - [目录](#目录)
  - [浏览器垃圾清除机制原理](#浏览器垃圾清除机制原理)
    - [问答题](#问答题)
  - [浏览器渲染流程和原理](#浏览器渲染流程和原理)
    - [问答题](#问答题-1)
  - [Event Loop事件循环](#event-loop事件循环)
    - [问答题](#问答题-2)
  - [闭包与作用域](#闭包与作用域)
    - [问答题](#问答题-3)
  - [原型与原型链](#原型与原型链)
    - [问答题](#问答题-4)
  - [网络协议与HTTP](#网络协议与http)
    - [问答题](#问答题-5)
  - [JavaScript异步编程](#javascript异步编程)
    - [问答题](#问答题-6)
  - [性能优化](#性能优化)
    - [问答题](#问答题-7)
  - [ES6+新特性](#es6新特性)
    - [问答题](#问答题-8)
  - [工程化与架构](#工程化与架构)
    - [问答题](#问答题-9)
  - [总结](#总结)

---

## 浏览器垃圾清除机制原理

### 问答题

**1. 请列举并解释 JavaScript 中常见的垃圾回收算法，说明各自的工作原理、优缺点及适用场景。**

**答案：**

JavaScript 的垃圾回收（Garbage Collection，GC）是自动进行的，通过判断对象是否还需要被引用来决定是否回收其内存。常见的垃圾回收算法有以下几种：

**（1）引用计数法（Reference Counting）**

```javascript
// 思路：跟踪每个对象被引用的次数
let a = { obj: 1 };  // 引用计数：1
let b = a;           // 引用计数：2
a = null;            // 引用计数：1
b = null;            // 引用计数：0 → 可以回收
```

- **工作原理**：为每个对象维护一个引用计数器，当引用计数降为 0 时，立即回收该对象。
- **优点**：实现简单，可立即回收垃圾，不会造成长时间停顿。
- **缺点**：无法处理循环引用问题，维护计数器有性能开销。
- **致命缺陷**：

```javascript
function cycle() {
  let a = {};
  let b = {};
  a.prop = b;
  b.prop = a;
}  // a和b的引用计数都不为0，永远不会被回收
```

- **适用场景**：早期浏览器（如 IE6/7 的 DOM 对象和 BOM 对象使用引用计数），现已弃用。

**（2）标记-清除法（Mark-Sweep）**

```
从根对象（window/global）开始
→ 标记所有能到达的对象
→ 清除没有被标记的对象
```

- **工作原理**：分两个阶段——标记阶段从根对象出发，递归遍历所有可达对象并标记；清除阶段遍历堆内存，回收未标记的对象。
- **优点**：解决了循环引用问题，是目前主流垃圾回收算法的基础。
- **缺点**：会产生内存碎片（回收后的内存空间不连续），可能导致后续分配大对象时找不到足够连续空间。
- **适用场景**：现代浏览器的基本垃圾回收策略。

**（3）标记-整理法（Mark-Compact）**

```
在标记-清除基础上
→ 标记后整理，把存活对象向一端移动
→ 然后清理掉边界外的内存
```

- **工作原理**：在标记-清除的基础上增加整理阶段，将所有存活对象向内存空间的一端移动，然后清理边界以外的内存。
- **优点**：避免了内存碎片问题，分配大对象时效率更高。
- **缺点**：移动对象需要更新所有引用，性能开销较大。
- **适用场景**：老生代垃圾回收。

**（4）分代收集法（Generational Collection）**

- **工作原理**：将堆内存分为新生代和老生代两个区域，不同区域采用不同的回收策略。新创建的对象放在新生代，经过多次回收仍存活的对象晋升到老生代。
- **优点**：针对不同生命周期的对象采用不同策略，提高整体回收效率。
- **适用场景**：V8 引擎的核心回收策略。

**总结对比：**

| 算法 | 循环引用 | 内存碎片 | 性能 | 复杂度 |
|------|---------|---------|------|--------|
| 引用计数 | ❌ 无法处理 | ✅ 无碎片 | ⚠️ 计数开销 | 低 |
| 标记-清除 | ✅ 可处理 | ❌ 有碎片 | 较好 | 中 |
| 标记-整理 | ✅ 可处理 | ✅ 无碎片 | ⚠️ 移动开销 | 中高 |
| 分代收集 | ✅ 可处理 | ✅ 无碎片 | ✅ 最优 | 高 |

---

**2. 请详细解释 V8 引擎的垃圾回收机制，包括分代回收策略的原理、新生代与老生代的回收算法、对象晋升条件以及全停顿优化方案。**

**答案：**

V8 引擎采用**分代回收策略**，将堆内存分为新生代和老生代两个区域，针对不同生命周期的对象采用不同的回收算法。

**新生代区域（小空间，存活时间短）：**

```javascript
// 使用 Scavenge 算法（复制算法）
// 分为 From 空间和 To 空间
// 分配内存在 From 空间
// GC时把存活对象复制到 To 空间
// 然后清空 From 空间
// 交换 From 和 To 空间
// 存活两次以上的对象晋升到老生代

// 特点：快，但空间利用率只有50%
```

- **Scavenge 算法（复制算法）**：将内存分为大小相等的 From 和 To 两个空间。分配对象在 From 空间，GC 时将存活对象复制到 To 空间，然后清空 From 空间，最后交换 From/To 角色。
- **优点**：速度极快，适合存活率低的新生代。
- **缺点**：空间利用率仅 50%。

**老生代区域（大空间，存活时间长）：**

```javascript
// 使用 Mark-Sweep（标记-清除）和 Mark-Compact（标记-整理）
// Mark-Sweep 先标记，再清除
// Mark-Compact 清除后整理内存
```

- **Mark-Sweep（标记-清除）**：先从根对象遍历标记所有可达对象，再清除未标记对象。
- **Mark-Compact（标记-整理）**：在清除基础上整理内存，消除碎片。当碎片过多时触发。

**对象晋升条件：**

1. 经历过一次 Scavenge 回收仍存活的对象
2. To 空间使用率超过 25%

**V8 垃圾回收流程可视化：**

```
┌─────────────────┐
│   新生成对象     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   From Space    │───┐
└────────┬────────┘   │
         │            │
         ▼ (GC)       │
┌─────────────────┐  │
│    To Space     │  │
└────────┬────────┘   │
         │            │
    (存活2次)         │
         │            │
         ▼            │
┌─────────────────┐  │
│   老生代空间     │◀─┘
│  Mark-Sweep     │
│  Mark-Compact   │
└─────────────────┘
```

**全停顿（Stop-The-World）优化：**

由于 GC 过程中需要暂停 JavaScript 执行（全停顿），大对象回收会导致明显卡顿。V8 的优化方案：

- **增量标记（Incremental Marking）**：将标记过程拆分为多个小步骤，穿插在 JavaScript 执行之间。
- **并行标记（Parallel Marking）**：利用多个辅助线程并行执行标记工作。
- **惰性清理（Lazy Sweeping）**：延迟实际的内存清理，按需进行。

---

**3. 请列举常见的内存泄漏场景，分析其成因，并说明如何检测和预防内存泄漏。**

**答案：**

**常见内存泄漏场景：**

**（1）意外的全局变量：**

```javascript
function foo() {
  bar = 'this is global';  // 没有声明，自动成为全局变量
  this.baz = 'also global'; // this指向window时
}
```

- **成因**：未使用 `var`/`let`/`const` 声明的变量会自动挂载到全局对象上，永远不会被回收。

**（2）未清理的定时器和回调函数：**

```javascript
let timer = setInterval(() => {
  let dom = document.getElementById('element');
  if (dom) {
    // do something
  }
}, 1000);
// 组件销毁时忘记清理定时器
```

- **成因**：定时器回调引用了外部变量或 DOM 元素，只要定时器未被清除，这些引用就不会被释放。

**（3）脱离 DOM 的引用：**

```javascript
let elements = {
  button: document.getElementById('button'),
  image: document.getElementById('image')
};
// DOM被删除了，但elements还在引用
document.body.removeChild(elements.button);
// 即使DOM移除了，elements.button还在，无法回收
```

- **成因**：DOM 节点从文档树移除后，JavaScript 变量仍持有其引用，导致无法回收。

**（4）闭包引起的泄漏：**

```javascript
let leakData;
function closure() {
  let bigData = new Array(1000000).fill('*');
  leakData = function() {
    return bigData;
  };
}
closure();
// bigData 永远不会被回收
```

- **成因**：闭包维持对外部变量的引用，即使不再使用也无法回收。

**（5）未清理的事件监听器：**

```javascript
const element = document.getElementById('my-element');
element.addEventListener('click', onClick);
// 移除元素时忘记移除监听器
element.parentNode.removeChild(element);
```

- **成因**：事件监听器持有对元素和回调函数的引用，不移除会导致泄漏。

**如何检测内存泄漏：**

```javascript
// Chrome DevTools 检测步骤
1. 打开 Memory 标签
2. 选择 "Take heap snapshot"
3. 执行一些操作
4. 再次拍快照
5. 比较两次快照，找出异常增长的对象

// Performance 标签监测
1. 打开 Performance 标签
2. 勾选 Memory
3. 录制操作
4. 观察内存走势图
```

**内存泄漏预防最佳实践：**

```javascript
// 1. 使用严格模式
'use strict';

// 2. 使用工具检测
// ESLint规则: no-undef, no-global-assign

// 3. 使用WeakMap/WeakSet（不阻止垃圾回收）
let weakMap = new WeakMap();
let weakSet = new WeakSet();

// 4. 使用try-finally保证清理
function doSomething() {
  let resource = acquireResource();
  try {
    // 使用资源
  } finally {
    resource.release();  // 保证清理
  }
}

// 5. 组件卸载时清理
// React示例
useEffect(() => {
  const timer = setInterval(() => {}, 1000);
  return () => {
    clearInterval(timer);  // 清理
  };
}, []);
```

---

## 浏览器渲染流程和原理

### 问答题

**1. 请详细描述浏览器渲染页面的完整流程，从 HTML 解析到像素显示在屏幕上的每个阶段，并说明各阶段的作用和关键点。**

**答案：**

**浏览器渲染的完整流程：**

```
1. 解析HTML → 生成DOM树
2. 解析CSS → 生成CSSOM树
3. 合成渲染树 → Render Tree（DOM + CSSOM）
4. 布局 → 计算几何位置和尺寸
5. 分层 → 计算层叠关系
6. 绘制 → 生成绘制指令
7. 分块 → 将图层分块
8. 光栅化 → 将块转换为位图
9. 合成 → 将位图显示到屏幕
```

**详细步骤说明：**

**步骤1：HTML解析构建DOM树**

```javascript
// HTML解析过程
// 遇到标签 → 生成DOM节点
// 遇到文本 → 生成文本节点
// 构建树结构

// HTML
<div class="container">
  <h1>Title</h1>
  <p>Content</p>
</div>

// 生成的DOM树
// Document
//   └── html
//       ├── head
//       └── body
//           └── div.container
//               ├── h1
//               │   └── "Title"
//               └── p
//                   └── "Content"
```

**步骤2：CSS解析构建CSSOM树**

```javascript
// 解析CSS规则
.container { width: 100%; }
h1 { color: red; }
p { font-size: 16px; }

// 生成CSSOM树
// 包含：浏览器默认样式 + 内部样式 + 外部样式 + 行内样式
```

**步骤3：构建渲染树**

```javascript
// 将DOM和CSSOM合成，只包含需要显示的节点
// display: none的元素不会在渲染树中
// content: ''等伪元素会包含在渲染树中
```

**步骤4：Layout布局**

```javascript
// 计算每个元素的几何信息
// - 尺寸
// - 位置
// - 布局树不一定和DOM树一一对应
```

**步骤5：分层Layer**

```javascript
// 为提高渲染效率，浏览器会分层
// 分层依据：
// - z-index
// - transform
// - opacity
// - will-change
// - video/canvas等
```

**步骤6：Paint绘制**

```javascript
// 为每个层生成绘制指令
// 绘制指令包括：
// - 绘制背景
// - 绘制边框
// - 绘制内容
```

**步骤7：合成**

```javascript
// 将各个层合成显示到屏幕
// GPU加速发生在这一阶段
// transform效率高是因为直接在合成阶段处理
```

**资源加载优化关键时间点：**

```javascript
// DOMContentLoaded - DOM解析完成，不等待样式、图片等资源
document.addEventListener('DOMContentLoaded', () => {
  // 可以操作DOM了
});

// load - 所有资源加载完成
window.addEventListener('load', () => {
  // 图片、样式、脚本都加载好了
});
```

**JS阻塞渲染的处理：**

```javascript
// 普通script标签会阻塞解析
<script src="app.js"></script>

// async 异步加载，加载完立即执行
<script src="app.js" async></script>

// defer 延迟执行，DOM解析完成后执行
<script src="app.js" defer></script>
```

---

**2. 请解释什么是重排（Reflow），列举会触发重排的常见操作和属性，并分析其性能影响。**

**答案：**

**重排（Reflow / Layout）定义：**

当元素的布局信息（尺寸、位置等）发生变化时，浏览器需要重新计算几何信息，这个过程称为重排。

**触发重排的常见操作：**

```javascript
// 修改几何属性
element.style.width = '100px';
element.style.height = '100px';
element.style.margin = '10px';
element.style.padding = '10px';
element.style.border = '1px solid';
element.style.display = 'block';
element.style.position = 'absolute';

// 修改DOM结构
document.body.appendChild(newElement);
element.removeChild(child);

// 窗口变化
window.addEventListener('resize', handler);

// 读取布局属性也会触发重排
const width = element.offsetWidth;
const height = element.offsetHeight;
const top = element.offsetTop;
const left = element.offsetLeft;
element.getComputedStyle();
element.getBoundingClientRect();
```

**性能影响：**

- 重排是浏览器渲染流程中最耗性能的操作之一。
- 一次重排可能引发整个页面或大面积区域的重新计算。
- 频繁重排会导致页面卡顿，影响用户体验。
- 重排必然引发重绘。

**减少重排的方法：**

```javascript
// 方法1：批量修改DOM
const fragment = document.createDocumentFragment();
for (let i = 0; i < 100; i++) {
  const div = document.createElement('div');
  fragment.appendChild(div);
}
document.body.appendChild(fragment);  // 只触发一次重排

// 方法2：先display:none，修改后再恢复
element.style.display = 'none';  // 触发一次重排
element.style.width = '100px';
element.style.height = '100px';
element.style.color = 'red';
element.style.display = 'block';  // 触发一次重排
// 总共只2次重排，而不是3次

// 方法3：使用cloneNode和replaceChild
const clone = element.cloneNode(true);
clone.style.width = '100px';
clone.style.height = '100px';
element.parentNode.replaceChild(clone, element);

// 方法4：避免频繁读取布局属性（缓存布局值）
// ❌ 错误写法 - 每次读取都会触发重排
for (let i = 0; i < 100; i++) {
  el.style.left = el.offsetWidth + i + 'px';
  el.style.top = el.offsetHeight + i + 'px';
}

// ✅ 正确写法 - 先缓存
const width = el.offsetWidth;
const height = el.offsetHeight;
for (let i = 0; i < 100; i++) {
  el.style.left = width + i + 'px';
  el.style.top = height + i + 'px';
}

// 方法5：使用transform代替top/left/width等
element.style.transform = 'translateX(100px)';  // 不触发重排
element.style.left = '100px';  // 会触发重排
```

---

**3. 请解释什么是重绘（Repaint），分析哪些 CSS 属性变化只会触发重绘而不会触发重排，并说明重绘与重排的关系。**

**答案：**

**重绘（Repaint / Paint）定义：**

当元素的样式变化但不影响布局（尺寸、位置不变）时，浏览器只需重新绘制元素的外观，这个过程称为重绘。

**只会触发重绘的属性：**

```javascript
element.style.color = 'red';
element.style.background = '#fff';
element.style.backgroundColor = 'blue';
element.style.boxShadow = '1px 1px 5px rgba(0,0,0,0.5)';
element.style.borderColor = 'blue';
element.style.visibility = 'hidden';
element.style.outline = '1px solid red';
element.style.textDecoration = 'underline';
```

这些属性共同特点：只改变元素的外观视觉效果，不改变其几何尺寸和位置。

**重排和重绘的关系：**

```
重排必然引发重绘
重绘不一定引发重排

性能影响：重排 > 重绘
```

**只触发合成（Composite）的属性：**

```javascript
// 以下属性既不触发重排也不触发重绘，只触发合成阶段，性能最优
element.style.transform = 'translateX(100px)';
element.style.opacity = '0.5';
element.style.filter = 'blur(5px)';

// 使用will-change提示浏览器
element.style.willChange = 'transform';  // 提示浏览器transform会变化
```

**优化建议：**

```javascript
// 使用requestAnimationFrame优化动画
function animate() {
  element.style.transform = `translateX(${x}px)`;
  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);
```

---

**4. 请说明浏览器渲染时的分层（Layer）机制，分析分层带来的好处、触发分层的条件及其实现原理。**

**答案：**

**分层机制定义：**

浏览器在渲染过程中，会将页面分成多个图层（Layer），每个图层独立进行绘制和合成。这样做可以让某些变化只在单独的图层上处理，而不影响整个页面。

**触发分层的条件：**

```javascript
// 以下CSS属性会触发元素成为独立图层
element.style.transform = 'translateZ(0)';       // 3D变换
element.style.willChange = 'transform';           // 明确提示
element.style.opacity = '0.5';                     // 透明度
element.style.position = 'fixed';                  // 固定定位
element.style.zIndex = '999';                      // 层叠上下文

// 特殊元素
// <video>, <canvas>, <iframe> 等会自动分层
// CSS filter, mask 等也会触发分层
```

**分层带来的好处：**

- **减少重绘范围**：只重绘发生变化的图层，不影响其他图层。
- **提高动画性能**：使用 transform/opacity 的动画只在合成阶段处理，不触发重排和重绘。
- **独立控制层级**：可以独立控制每个图层的显示、隐藏、变换等。
- **GPU 加速**：独立图层可以利用 GPU 进行硬件加速渲染。

**注意事项：**

- 分层**不节约内存**，反而会增加内存占用（每个图层都需要额外的内存空间存储位图）。
- 过度创建图层会导致内存消耗过大，反而降低性能。
- 不要滥用 `will-change`，应在确实需要时使用，用完及时移除。

```javascript
// ❌ 不推荐：所有元素都设置will-change
* { will-change: transform; }

// ✅ 推荐：仅在需要时设置，用完移除
element.style.willChange = 'transform';
// 动画结束后
element.addEventListener('transitionend', () => {
  element.style.willChange = 'auto';
});
```

---

## Event Loop事件循环

### 问答题

**1. 请解释 JavaScript 的单线程执行模型，分析其设计原因及 Event Loop 机制的作用。**

**答案：**

**JavaScript 的单线程模型：**

JavaScript 是单线程的，同一时间只能执行一个任务。这意味着所有的同步代码在调用栈（Call Stack）中按顺序执行，前一个任务完成后才能执行下一个。

**设计原因：**

- **历史原因**：JavaScript 最初设计用于浏览器中处理简单的用户交互和 DOM 操作，单线程足以满足需求。
- **简化 DOM 操作**：如果多线程同时操作 DOM，需要处理复杂的并发冲突问题（如锁机制），单线程避免了这种复杂性。
- **避免死锁**：单线程不需要处理线程同步、死锁等复杂问题。

**Event Loop 的作用：**

由于单线程的限制，如果所有任务都同步执行，一个耗时任务会阻塞后续所有任务。Event Loop 机制通过任务队列实现了**异步非阻塞**执行：

```
┌─────────────────────────────────────────────────┐
│               Event Loop                          │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐    ┌──────────────────────┐  │
│  │   调用栈     │    │   任务队列            │  │
│  │   Call Stack │    │                      │  │
│  └──────────────┘    │  ┌────────────────┐ │  │
│         │            │  │  微任务队列     │ │  │
│         │            │  │ - Promise      │ │  │
│         │            │  │ - MutationOb   │ │  │
│         │            │  └────────────────┘ │  │
│         │            │  ┌────────────────┐ │  │
│         │            │  │  宏任务队列     │ │  │
│         │            │  │ - setTimeout   │ │  │
│         │            │  │ - setInterval  │ │  │
│         │            │  │ - I/O          │ │  │
│         │            │  └────────────────┘ │  │
│         ▼            └──────────────────────┘  │
│  ┌────────────────────────────────────────┐   │
│  │         Web APIs                       │   │
│  │ - DOM Events                          │   │
│  │ - timer                               │   │
│  │ - fetch                               │   │
│  └────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

通过 Web APIs（如定时器、网络请求、事件监听等），耗时操作可以交给浏览器底层处理，完成后将回调放入任务队列，Event Loop 负责在调用栈空闲时将队列中的任务推入执行栈。

---

**2. 请区分宏任务和微任务，列举常见的宏任务和微任务 API，并说明它们的优先级关系和执行时机。**

**答案：**

**宏任务（Macro Task）：**

```javascript
// 常见宏任务
setTimeout(() => { console.log('setTimeout'); });
setInterval(() => { console.log('setInterval'); });
setImmediate(() => { console.log('setImmediate'); });  // Node.js
requestAnimationFrame(() => { console.log('requestAnimationFrame'); });

// I/O操作
fs.readFile('/path', () => { console.log('read file'); });

// DOM事件
element.addEventListener('click', () => { console.log('click'); });
```

**微任务（Micro Task）：**

```javascript
// 常见微任务
Promise.resolve().then(() => { console.log('Promise then'); });

// async/await
async function foo() {
  await bar();  // await后的代码是微任务
  console.log('after await');
}

// queueMicrotask
queueMicrotask(() => { console.log('queueMicrotask'); });

// MutationObserver
const observer = new MutationObserver(() => { console.log('DOM changed'); });

// Node.js特有
process.nextTick(() => { console.log('nextTick'); });  // 优先级最高
```

**优先级关系：**

```
微任务优先级 > 宏任务优先级

在每个宏任务执行完成后，会清空所有微任务队列，
然后再执行下一个宏任务。
```

**执行时机对比：**

| 任务类型 | 执行时机 | 常见 API |
|---------|---------|---------|
| 宏任务 | 每轮 Event Loop 取一个执行 | setTimeout、setInterval、I/O、UI 事件 |
| 微任务 | 每个宏任务后全部清空 | Promise.then、queueMicrotask、MutationObserver |

---

**3. 请详细描述 Event Loop 在一个周期内的任务执行顺序，并分析微任务和宏任务的调度机制，结合经典代码示例说明执行结果。**

**答案：**

**Event Loop 执行流程：**

```javascript
// 完整循环步骤
1. 执行同步代码（调用栈清空）
2. 执行所有微任务队列中的任务
3. 执行浏览器渲染（如果需要）
4. 取出一个宏任务执行
5. 返回步骤2，循环往复
```

**关键要点：**
- 每个宏任务执行后，会清空**所有**微任务
- 微任务执行期间产生的新微任务也会在当前轮次清空
- 渲染发生在微任务之后、下一个宏任务之前

**经典示例1：**

```javascript
console.log('1');  // 同步任务

setTimeout(() => {
  console.log('2');
}, 0);  // 宏任务

Promise.resolve().then(() => {
  console.log('3');
});  // 微任务

// 执行顺序：1 → 3 → 2
```

**经典示例2：**

```javascript
console.log('script start');

setTimeout(() => {
  console.log('setTimeout');
}, 0);

Promise.resolve().then(() => {
  console.log('promise1');
}).then(() => {
  console.log('promise2');
});

console.log('script end');

// 答案：
// script start
// script end
// promise1
// promise2
// setTimeout
```

**经典示例3（复杂版）：**

```javascript
async function async1() {
  console.log('async1 start');
  await async2();
  console.log('async1 end');
}

async function async2() {
  console.log('async2');
}

console.log('script start');

setTimeout(() => {
  console.log('setTimeout');
}, 0);

async1();

new Promise((resolve) => {
  console.log('promise1');
  resolve();
}).then(() => {
  console.log('promise2');
});

console.log('script end');

// 答案
// script start
// async1 start
// async2
// promise1
// script end
// async1 end
// promise2
// setTimeout
```

**浏览器环境与 Node.js 环境的差异：**

```javascript
// 浏览器：
// 微任务：Promise.then, MutationObserver, queueMicrotask
// 宏任务：setTimeout, setInterval, setImmediate, I/O, requestAnimationFrame

// Node.js：
// 微任务：Promise.then, process.nextTick, queueMicrotask
// 宏任务：setTimeout, setInterval, setImmediate, I/O
// Node.js的Event Loop有多个阶段：timers, pending callbacks, idle, poll, check, close callbacks
```

---

**4. 请说明 `Promise.resolve().then()` 回调属于哪种任务类型，并解释其在 Event Loop 中的执行时机，与 setTimeout 回调的区别。**

**答案：**

`Promise.resolve().then(() => {})` 的回调函数属于**微任务（Micro Task）**，会被放入微任务队列。

**执行时机：**

- 微任务在每个宏任务执行完毕后、下一个宏任务执行前被全部清空。
- 即使 `setTimeout` 的延迟设为 0，也必须在当前所有微任务执行完后才会执行。

**与 setTimeout 的区别：**

```javascript
// 示例对比
setTimeout(() => {
  console.log('setTimeout');  // 宏任务，最后执行
}, 0);

Promise.resolve().then(() => {
  console.log('Promise');  // 微任务，先执行
});

// 输出顺序：Promise → setTimeout
```

**原因分析：**

1. `Promise.then` 回调进入微任务队列，优先级更高。
2. `setTimeout` 回调进入宏任务队列，需要等当前所有微任务清空后才执行。
3. 微任务的设计目的是让异步操作的结果尽快被处理，减少延迟。

**实际应用场景：**

```javascript
// 利用微任务确保代码在当前同步代码后、下一个宏任务前执行
// 常用于：确保DOM更新后立即执行回调（Vue的nextTick原理）
function nextTick(callback) {
  return Promise.resolve().then(callback);
}
```

---

## 闭包与作用域

### 问答题

**1. 请解释闭包的概念、形成条件、主要作用和应用场景，并分析闭包可能带来的问题。**

**答案：**

**闭包定义：**

当一个函数能够记住并访问它的词法作用域，即使该函数在其词法作用域之外执行时，就产生了闭包。

```javascript
function outer() {
  let count = 0;  // 变量在outer作用域
  return function inner() {
    // inner函数记住了outer的词法作用域
    count++;
    console.log(count);
  };
}

const fn = outer();
fn();  // 1 - outer执行完了，但count仍然存活
fn();  // 2 - 闭包使count保留
fn();  // 3
```

**闭包形成的条件：**

1. 函数嵌套函数
2. 内部函数引用外部函数的变量
3. 内部函数被外部返回或被外部引用

**闭包的主要作用：**

- **访问函数内部变量**：从外部读取函数内部的局部变量。
- **让变量长期保存在内存**：闭包引用的变量不会被垃圾回收。
- **实现封装**：创建私有变量和私有方法。
- **实现模块化**：通过 IIFE 创建独立的作用域。

**闭包的应用场景：**

**场景1：数据封装/私有变量**

```javascript
function createCounter() {
  let count = 0;  // 私有变量，外部无法直接访问
  
  return {
    increment() { count++; return count; },
    decrement() { count--; return count; },
    getCount() { return count; }
  };
}

const counter = createCounter();
counter.increment();  // 1
counter.increment();  // 2
console.log(counter.count);  // undefined - 无法直接访问私有变量
```

**场景2：函数柯里化**

```javascript
function curry(fn) {
  return function curried(...args) {
    if (args.length >= fn.length) {
      return fn.apply(this, args);
    } else {
      return function(...moreArgs) {
        return curried.apply(this, args.concat(moreArgs));
      };
    }
  };
}

const curriedSum = curry((a, b, c) => a + b + c);
curriedSum(1)(2)(3);  // 6
```

**场景3：模块模式**

```javascript
const module = (function() {
  let privateData = 'private';
  
  function privateMethod() {
    console.log('This is private');
  }
  
  return {
    publicMethod() { privateMethod(); },
    setPrivateData(newValue) { privateData = newValue; }
  };
})();
```

**场景4：事件处理与回调**

```javascript
for (let i = 0; i < 5; i++) {
  document.getElementById('btn-' + i).addEventListener('click', () => {
    console.log('Click button ' + i);  // i被闭包保存
  });
}
```

**闭包可能带来的问题及解决：**

```javascript
// 问题1：经典for循环面试题
for (var i = 0; i < 5; i++) {
  setTimeout(() => {
    console.log(i);  // 5次都是5
  }, 1000);
}

// 解法1：let块级作用域
for (let i = 0; i < 5; i++) {
  setTimeout(() => { console.log(i); }, 1000);  // 0,1,2,3,4
}

// 解法2：立即执行函数（IIFE）
for (var i = 0; i < 5; i++) {
  (function(j) {
    setTimeout(() => { console.log(j); }, 1000);  // 0,1,2,3,4
  })(i);
}

// 问题2：内存泄漏
function leakMemory() {
  let bigData = new Array(1000000);
  return function() { return bigData; };  // bigData被闭包引用，无法回收
}

// 解决：及时释放引用
function cleanup() { bigData = null; }
```

---

**2. 请从多个维度分析闭包的特性，包括其与词法作用域的关系、对内存的影响、与普通函数的区别等。**

**答案：**

**闭包与词法作用域的关系：**

闭包的核心特性是**让函数可以记住并访问其词法作用域**。JavaScript 采用词法作用域（静态作用域），函数的作用域在定义时就确定了，而非执行时。闭包正是利用这一特性，使内部函数即使在外部函数返回后，仍能访问外部函数的变量。

```javascript
// 词法作用域：函数的作用域在定义时确定
function outer() {
  const x = 10;
  function inner() {
    // inner在定义时就"记住"了x
    console.log(x);
  }
  return inner;
}

const fn = outer();
fn();  // 10 —— 即使outer已执行完毕，inner仍能访问x
```

**闭包对内存的影响：**

- **变量长期存活**：闭包引用的变量不会被垃圾回收，会长期保存在内存中。
- **可能导致内存泄漏**：如果闭包引用了大对象且不及时释放，会造成内存泄漏。
- **不必然导致性能问题**：合理使用闭包不会显著影响性能，现代JS引擎已对闭包做了优化。

**闭包与普通函数的区别：**

| 特性 | 普通函数 | 闭包 |
|------|---------|------|
| 作用域访问 | 只能访问自身作用域和全局 | 还能访问外层函数作用域 |
| 变量生命周期 | 随函数执行结束而销毁 | 被引用的变量会长期存活 |
| 内存占用 | 较少 | 较多（维持对外部变量的引用） |
| 应用场景 | 通用代码组织 | 数据封装、回调、柯里化等 |

**闭包不是 JavaScript 特有的：**

闭包是函数式编程语言的通用特性，Python、Scheme、Haskell 等语言都支持闭包。只是 JavaScript 中闭包使用尤为广泛。

---

**3. 请分析以下代码的输出结果，并解释 `var` 声明在闭包中的行为及解决方案。**

```javascript
for (var i = 0; i < 5; i++) {
  setTimeout(() => console.log(i), 1000);
}
```

**答案：**

**输出结果：** `5 5 5 5 5`（1秒后连续输出5个5）

**原因分析：**

1. `var` 声明的 `i` 是函数级作用域，整个循环中只有一个 `i` 变量。
2. 循环执行时，5个 `setTimeout` 回调被注册到宏任务队列，它们都引用同一个 `i` 变量。
3. 1秒后，循环已结束，`i` 的值为 5（循环退出条件 `i < 5` 失败时的值）。
4. 回调执行时读取到的 `i` 都是 5。

**解决方案：**

```javascript
// 解法1：使用let（推荐）
for (let i = 0; i < 5; i++) {
  setTimeout(() => console.log(i), 1000);  // 0,1,2,3,4
}
// let创建块级作用域，每次循环迭代都会创建一个新的i

// 解法2：使用立即执行函数（IIFE）创建闭包
for (var i = 0; i < 5; i++) {
  (function(j) {
    setTimeout(() => console.log(j), 1000);  // 0,1,2,3,4
  })(i);
}
// 每次迭代将i的值传入IIFE，j保存了当时的i值

// 解法3：使用bind
for (var i = 0; i < 5; i++) {
  setTimeout(console.log.bind(console, i), 1000);  // 0,1,2,3,4
}

// 解法4：使用setTimeout的第三个参数
for (var i = 0; i < 5; i++) {
  setTimeout((j) => console.log(j), 1000, i);  // 0,1,2,3,4
}
```

---

## 原型与原型链

### 问答题

**1. 请解释 prototype 和 \_\_proto\_\_ 的区别，说明函数和对象在原型链中的关系，并描述属性查找规则。**

**答案：**

**prototype 与 \_\_proto\_\_ 的区别：**

```javascript
// 每个函数都有 prototype 属性（显式原型）
function Person() {}
console.log(Person.prototype);  // { constructor: Person }

// 每个对象都有 __proto__ 属性（隐式原型）
const person = new Person();
console.log(person.__proto__ === Person.prototype);  // true
```

| 属性 | 存在于 | 作用 |
|------|--------|------|
| `prototype` | 函数 | 指向函数的原型对象，用于实例继承 |
| `__proto__` | 所有对象 | 指向创建该对象的构造函数的 prototype |

**原型链结构：**

```javascript
person.__proto__ === Person.prototype;
Person.prototype.__proto__ === Object.prototype;
Object.prototype.__proto__ === null;  // 原型链终点

// 完整链
// person -> Person.prototype -> Object.prototype -> null
```

```
关系图：
person
  └── __proto__ ───────→ Person.prototype
                            ├── constructor ──→ Person
                            └── __proto__ ─────→ Object.prototype
                                              └── __proto__ ──→ null
```

**属性查找规则：**

当访问对象属性时：
1. 先在对象自身查找
2. 找不到，去 `__proto__` 中查找
3. 继续往上，直到找到或到达 `null`

```javascript
function Person() {}
Person.prototype.name = 'Prototype Person';

const person1 = new Person();
const person2 = new Person();

person1.name = 'Tom';  // 对象自身属性

console.log(person1.name);  // Tom - 找到自身
console.log(person2.name);  // Prototype Person - 找到原型
```

**属性设置规则：**

```javascript
// 给对象设置属性时，只会在对象自身创建，不会修改原型
person2.name = 'Jerry';
console.log(person2.name);          // Jerry - 自身属性
console.log(Person.prototype.name); // Prototype Person - 原型未改变
```

---

**2. 请说明 `Object.prototype.__proto__` 的值是什么，并解释原型链的终点及判断方法。**

**答案：**

**`Object.prototype.__proto__` 的值是 `null`。**

**原型链的终点：**

所有对象的原型链最终都会到达 `Object.prototype`，而 `Object.prototype.__proto__` 指向 `null`，表示原型链的终点。

```javascript
console.log(Object.prototype.__proto__);  // null

// 任何对象沿着__proto__向上查找，最终都会到达null
const obj = {};
console.log(obj.__proto__.__proto__);  // null

const arr = [];
console.log(arr.__proto__.__proto__.__proto__);  // null
```

**判断原型链终点的方法：**

```javascript
// 方法1：直接检查__proto__是否为null
const obj = {};
let proto = obj;
while (proto !== null) {
  proto = Object.getPrototypeOf(proto);
}
console.log('到达原型链终点');

// 方法2：使用Object.getPrototypeOf
console.log(Object.getPrototypeOf(Object.prototype));  // null

// 方法3：使用isPrototypeOf
console.log(Object.prototype.isPrototypeOf({}));  // true
console.log(Object.prototype.hasOwnProperty('__proto__'));  // false（__proto__是getter/setter）
```

**注意事项：**

- `__proto__` 是非标准属性（虽然被广泛支持），推荐使用 `Object.getPrototypeOf()` 和 `Object.setPrototypeOf()`。
- `null` 作为原型链终点的设计，避免了无限循环查找。

---

**3. 请分析以下代码的输出结果，并解释原型链上的属性查找规则与遮蔽效应。**

```javascript
function Person() {}
Person.prototype.name = 'Person';
const person = new Person();
person.name = 'Tom';
console.log(person.name);
```

**答案：**

**输出结果：** `Tom`

**原因分析：**

1. `Person.prototype.name = 'Person'`：在原型对象上设置 `name` 属性。
2. `const person = new Person()`：创建实例，`person.__proto__` 指向 `Person.prototype`。
3. `person.name = 'Tom'`：在实例**自身**上添加 `name` 属性（不修改原型）。
4. `console.log(person.name)`：按属性查找规则，先在自身找到 `'Tom'`，不再向上查找原型。

**属性遮蔽效应：**

当对象自身和原型上都有同名属性时，自身属性会**遮蔽**原型上的属性：

```javascript
function Person() {}
Person.prototype.name = 'Person';

const person = new Person();
console.log(person.name);  // 'Person' —— 自身没有，查找原型

person.name = 'Tom';  // 在自身添加属性，遮蔽原型
console.log(person.name);  // 'Tom' —— 自身属性优先

delete person.name;  // 删除自身属性
console.log(person.name);  // 'Person' —— 遮蔽解除，查找原型
```

**判断属性位置：**

```javascript
console.log(person.hasOwnProperty('name'));  // false（删除后）
console.log('name' in person);  // true（原型上有）
console.log(Object.getPrototypeOf(person).hasOwnProperty('name'));  // true
```

---

## 网络协议与HTTP

### 问答题

**1. 请说明 HTTP 在 OSI 七层模型和 TCP/IP 四层模型中的位置，并解释其与传输层协议的关系。**

**答案：**

**HTTP 在网络模型中的位置：**

| OSI 七层模型 | TCP/IP 四层模型 | 示例协议 |
|-------------|----------------|---------|
| 应用层 | 应用层 | **HTTP**、HTTPS、FTP、DNS、SMTP |
| 表示层 | 应用层 | （合并到应用层） |
| 会话层 | 应用层 | （合并到应用层） |
| 传输层 | 传输层 | TCP、UDP |
| 网络层 | 网络层 | IP、ICMP |
| 数据链路层 | 网络接口层 | Ethernet、Wi-Fi |
| 物理层 | 网络接口层 | （合并到网络接口层） |

**HTTP 位于应用层**，是最上层的协议。

**HTTP 与传输层的关系：**

- HTTP 基于 **TCP** 协议（可靠传输），HTTP/3 基于 **QUIC**（基于 UDP）。
- HTTP 本身不处理数据传输的可靠性、顺序等问题，这些由 TCP 保证。
- HTTP 通过 TCP 连接发送请求和接收响应。

**TCP 三次握手建立连接后，HTTP 才能开始通信：**

```
客户端                          服务端
  |                               |
  |  TCP三次握手                   |
  |  SYN → SYN+ACK → ACK          |
  | ----------------------------→ |
  |                               |
  |  HTTP请求                      |
  |  GET /index.html HTTP/1.1     |
  | ----------------------------→ |
  |                               |
  |  HTTP响应                      |
  |  HTTP/1.1 200 OK              |
  | ←---------------------------- |
  |                               |
  |  TCP四次挥手                   |
  |  FIN → ACK → FIN → ACK        |
  | ----------------------------→ |
```

---

**2. 请详细描述 TCP 三次握手和四次挥手的过程，分析每一步的作用，并解释为何握手是三次而挥手是四次。**

**答案：**

**TCP三次握手（建立连接）：**

```
客户端                    服务端
   |                       |
   |    1. SYN=1, seq=x    |
   | --------------------> |
   |                       |
   |   2. SYN=1, ACK=x+1, seq=y
   | <-------------------- |
   |                       |
   |    3. ACK=y+1         |
   | --------------------> |
   |                       |
   |      连接建立完成       |
```

**详细说明：**

```javascript
// 第一次握手：客户端发送SYN包
SYN = 1  // 表示要建立连接
seq = x  // 客户端随机生成的序列号
客户端进入 SYN_SEND 状态

// 第二次握手：服务端回复SYN+ACK
SYN = 1  // 同意建立连接
ACK = x + 1  // 确认收到了客户端的seq
seq = y  // 服务端随机生成的序列号
服务端进入 SYN_RECV 状态

// 第三次握手：客户端回复ACK
ACK = y + 1  // 确认收到了服务端的seq
客户端进入 ESTABLISHED 状态
服务端收到ACK后也进入 ESTABLISHED 状态
```

**为什么是三次握手？**

1. 确认双方发送、接收能力均正常
2. 同步序列号（seq）
3. 防止已失效的连接请求到达服务端，造成资源浪费

**TCP四次挥手（关闭连接）：**

```
客户端                    服务端
   |                       |
   |    1. FIN=1, seq=x    |
   | --------------------> |
   |                       |
   |    2. ACK=x+1         |
   | <-------------------- |
   |                       |
   |    3. FIN=1, seq=y    |
   | <-------------------- |
   |                       |
   |    4. ACK=y+1         |
   | --------------------> |
   |                       |
   |      连接关闭完成       |
```

**详细说明：**

```javascript
// 第一次挥手：客户端发送FIN
FIN = 1  // 表示要关闭连接
seq = x
客户端进入 FIN_WAIT_1 状态

// 第二次挥手：服务端回复ACK
ACK = x + 1
服务端进入 CLOSE_WAIT 状态
客户端收到后进入 FIN_WAIT_2 状态

// 第三次挥手：服务端发送FIN
FIN = 1
seq = y
服务端进入 LAST_ACK 状态

// 第四次挥手：客户端回复ACK
ACK = y + 1
客户端进入 TIME_WAIT 状态
// TIME_WAIT 持续 2MSL 后进入 CLOSED
// 保证最后一个ACK能被收到
```

**为什么是四次挥手？**

TCP 是全双工通信，关闭连接时需要单独关闭两个方向：
- 客户端发送 FIN 表示不再发送数据，但仍可接收
- 服务端先回复 ACK，处理完剩余数据后发送 FIN
- 客户端回复 ACK，连接完全关闭

因此需要四次挥手。

**常见HTTP状态码：**

```javascript
// 2XX 成功：200 OK, 201 Created, 204 No Content
// 3XX 重定向：301 永久重定向, 302 临时重定向, 304 未修改
// 4XX 客户端错误：400 错误请求, 401 未授权, 403 禁止访问, 404 未找到
// 5XX 服务端错误：500 服务器错误, 502 网关错误, 503 服务不可用, 504 网关超时
```

---

**3. 请对比 HTTP/1.1、HTTP/2 和 HTTP/3 的主要特性，分析各版本的改进点和局限性。**

**答案：**

| 特性 | HTTP/1.1 | HTTP/2 | HTTP/3 |
|------|---------|--------|--------|
| **传输层** | TCP | TCP | QUIC（基于UDP） |
| **协议格式** | 文本 | 二进制 | 二进制 |
| **多路复用** | ❌ | ✅ | ✅ |
| **队头阻塞** | 有（应用层） | 有（TCP层） | ❌ 彻底解决 |
| **头部压缩** | ❌ | ✅ HPACK | ✅ QPACK |
| **服务器推送** | ❌ | ✅ | ✅ |
| **连接建立** | 需TCP握手 | 需TCP握手+TLS | 更快（合并握手） |

**HTTP/1.1：**

```javascript
// 特点：
// - 支持持久连接（Keep-Alive）
// - 支持管线化（Pipelining）
// - 支持Host头（虚拟主机）
// 缺点：
// - 队头阻塞（Head-of-line blocking）
// - 同一域名并发请求数有限（通常6个）
// - 头部未压缩，重复数据多
```

**HTTP/2：**

```javascript
// 改进：
// - 二进制分帧（Binary Framing）
// - 多路复用：一个TCP连接上并行多个请求
// - 头部压缩（HPACK算法）
// - 服务器推送（Server Push）
// - 流控制
// 局限性：
// - 仍然基于TCP，TCP层存在队头阻塞
// - 非加密版本被多数浏览器放弃支持
// 注：HTTP/2本身不"更加安全"，安全性由TLS保证
```

**HTTP/3：**

```javascript
// 改进：
// - 基于QUIC协议（Google开发）
// - 基于UDP，彻底解决队头阻塞
// - 更快的连接建立（合并TLS握手）
// - 更好的网络切换体验（连接迁移）
// - 内置加密（TLS 1.3）
```

**安全性说明：**

HTTP/2 并不比 HTTP/1.1 "更加安全"——安全性由 HTTPS（TLS）提供，而非 HTTP 协议版本本身。HTTP/3 内置了 TLS 1.3，因此在传输层上更安全。

---

## JavaScript异步编程

### 问答题

**1. 请解释 Promise 的三种状态及其转换规则，分析 Promise 的状态机模型。**

**答案：**

**Promise 的三种状态：**

| 状态 | 说明 | 是否可变 |
|------|------|---------|
| `pending` | 初始状态，进行中 | 可变 |
| `fulfilled` | 已成功（resolved） | 不可变（终态） |
| `rejected` | 已失败（rejected） | 不可变（终态） |

**状态转换规则：**

```
pending ──→ fulfilled（resolve调用）
       └──→ rejected（reject调用或抛出异常）
```

- 状态只能从 `pending` 转换为 `fulfilled` 或 `rejected`
- 一旦变为终态（fulfilled/rejected），**永远不会改变**
- 没有 `finished` 状态——Promise只有上述三种状态

```javascript
const promise = new Promise((resolve, reject) => {
  // 初始状态：pending
  
  resolve('success');  // 状态变为 fulfilled
  
  reject('error');     // 无效，状态已不可变
  resolve('again');    // 无效
});

promise.then(
  data => console.log(data),    // 'success'
  error => console.error(error) // 不会执行
);
```

**状态机的特点：**

1. **单向不可逆**：状态只能从 pending → fulfilled/rejected，不能回退。
2. **一次性**：终态一旦确定，resolve/reject 的后续调用都是静默失败。
3. **异步传播**：状态变化后，通过 then/catch 注册的回调会在微任务中异步执行。

```javascript
// 示例：状态传播
const p1 = new Promise(resolve => setTimeout(() => resolve('done'), 1000));
const p2 = p1.then(data => { throw new Error('fail'); });
// p1: fulfilled
// p2: rejected

// p2的状态取决于回调的返回值：
// - 回调返回普通值 → p2 fulfilled
// - 回调抛出异常 → p2 rejected
// - 回调返回Promise → p2状态跟随该Promise
```

---

**2. 请详细说明 async/await 的语法规则，包括使用限制、返回值特性和错误处理机制。**

**答案：**

**基本语法：**

```javascript
async function fetchData() {
  const data = await fetch('/api');
  return data;
}
```

**核心规则：**

1. **async 函数总是返回 Promise**：

```javascript
async function foo() {
  return 123;  // 返回普通值
}
foo().then(data => console.log(data));  // 123

// 等价于
async function foo() {
  return Promise.resolve(123);
}

// 如果返回的是Promise，则直接返回该Promise
async function bar() {
  return Promise.resolve(456);
}
bar().then(data => console.log(data));  // 456
```

2. **await 只能在 async 函数中使用**（顶层 await 需要 ES2022+）：

```javascript
// ❌ 错误：await不能在普通函数中使用
function normal() {
  await fetch('/api');  // SyntaxError
}

// ✅ 正确：在async函数中使用
async function asyncFunc() {
  await fetch('/api');
}

// ✅ ES2022+ 顶层await
// const data = await fetch('/api');  // 仅在模块顶层
```

3. **await 后面不一定要接 Promise**：

```javascript
// await后面可以接任何值
async function foo() {
  const result = await 123;  // 等价于 await Promise.resolve(123)
  console.log(result);  // 123
  
  const obj = await { name: 'test' };
  console.log(obj.name);  // 'test'
}
// 注：await会把非Promise值包装为Promise.resolve()
// 所以说"await后面必须接Promise"是错误的
```

**错误处理机制：**

```javascript
// 方式1：try-catch
async function getData() {
  try {
    const data = await fetch('/api');
    return data;
  } catch (error) {
    console.error('请求失败:', error);
  }
}

// 方式2：.catch()
async function getData2() {
  const data = await fetch('/api').catch(err => {
    console.error(err);
    return null;
  });
  return data;
}
```

**并发执行：**

```javascript
// 串行执行（慢）
async function serial() {
  const data1 = await fetch('/api/1');  // 等待完成
  const data2 = await fetch('/api/2');  // 再开始
}

// 并发执行（快）
async function concurrent() {
  const [data1, data2] = await Promise.all([
    fetch('/api/1'),
    fetch('/api/2')
  ]);
}
```

---

**3. 请对比 Promise 的静态方法（all、allSettled、race、any），分析各自的使用场景和差异。**

**答案：**

| 方法 | 成功条件 | 失败条件 | 返回值 |
|------|---------|---------|--------|
| `Promise.all` | 所有成功 | **任一失败** | 所有结果的数组 |
| `Promise.allSettled` | 永远不失败 | — | 所有结果（含status）的数组 |
| `Promise.race` | 第一个完成的状态 | 第一个完成的状态 | 第一个完成的结果 |
| `Promise.any` | **任一成功** | 全部失败 | 第一个成功的结果 |

**Promise.all：**

```javascript
// 所有Promise都成功才成功，任一失败就立即失败
Promise.all([p1, p2, p3])
  .then(results => console.log(results))  // [result1, result2, result3]
  .catch(error => console.error(error));   // 第一个失败的错误

// 适用场景：多个请求必须全部成功才能继续
```

**Promise.allSettled：**

```javascript
// 等待所有Promise完成（无论成功或失败），永远不会reject
Promise.allSettled([p1, p2, p3])
  .then(results => {
    results.forEach(result => {
      if (result.status === 'fulfilled') {
        console.log('成功:', result.value);
      } else {
        console.log('失败:', result.reason);
      }
    });
  });

// 适用场景：需要知道所有结果，不论成功失败
```

**Promise.race：**

```javascript
// 返回第一个完成（成功或失败）的Promise
Promise.race([
  fetch('/api'),
  new Promise((_, reject) => 
    setTimeout(() => reject(new Error('timeout')), 5000)
  )
]).then(data => console.log(data))
  .catch(err => console.error(err));

// 适用场景：请求超时控制、竞速
```

**Promise.any：**

```javascript
// 任一Promise成功就成功，全部失败才失败
Promise.any([p1, p2, p3])
  .then(firstSuccess => console.log(firstSuccess))
  .catch(err => console.error('全部失败:', err));  // AggregateError

// 适用场景：多个备用资源，取最快可用的一个
```

**异步方案对比总结：**

| 方案 | 优点 | 缺点 |
|------|------|------|
| Callback | 简单易懂 | 回调地狱，错误处理困难 |
| Promise | 链式调用，好处理错误 | 有一定学习成本 |
| Generator | 可以暂停执行 | 需要手动或自动执行函数 |
| Async/Await | 写法像同步，最佳方案 | 需要ES7支持 |

---

## 性能优化

### 问答题

**1. 请对比常见的图片格式（JPEG、PNG、GIF、WebP、SVG、AVIF），分析各自的特点、优缺点和适用场景。**

**答案：**

| 格式 | 压缩方式 | 透明 | 动画 | 有损/无损 | 适用场景 |
|------|---------|------|------|----------|---------|
| **JPEG** | 有损 | ❌ | ❌ | 有损 | 照片、色彩丰富的图片 |
| **PNG** | 无损 | ✅ | ❌ | 无损 | 图标、需要透明的图片、截图 |
| **GIF** | 无损 | ✅ | ✅ | 无损（256色） | 简单动画 |
| **WebP** | 有损/无损 | ✅ | ✅ | 都支持 | 通用替代（现代浏览器） |
| **SVG** | 矢量 | ✅ | ✅ | 无损 | 图标、Logo、简单图形 |
| **AVIF** | 有损/无损 | ✅ | ✅ | 都支持 | 下一代图片格式（压缩率最高） |

**详细说明：**

- **JPEG**：适合色彩丰富的照片，不支持透明，有损压缩会导致文字边缘模糊。
- **PNG**：支持透明且无损，适合需要精确显示的图标和UI元素，但文件体积较大。
- **GIF**：仅支持256色，适合简单动画，文件体积大。
- **WebP**：Google开发，同时支持有损和无损压缩，支持透明和动画，体积比JPEG/PNG小25-35%，现代浏览器已广泛支持。
- **SVG**：矢量格式，无限缩放不失真，适合图标和简单图形。
- **AVIF**：下一代格式，压缩率比WebP更高，但浏览器兼容性还在完善中。

**选型建议：**

```html
<!-- 使用picture标签提供多种格式回退 -->
<picture>
  <source srcset="image.avif" type="image/avif">
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="fallback">
</picture>
```

---

**2. 请列举减少 HTTP 请求数的优化方案，并分析各自的实现原理和效果。**

**答案：**

**方案1：合并 CSS/JS 文件**

```javascript
// 将多个CSS/JS文件合并为一个
// 构建工具（Webpack、Vite）自动处理
// 原理：减少HTTP请求数量，减少握手和头部开销
// 效果：对减少请求数最有效
```

**方案2：CSS Sprites（雪碧图）**

```css
/* 将多个小图标合并为一张大图，通过background-position定位 */
.icon-home {
  background-image: url('sprite.png');
  background-position: 0 0;
  width: 16px;
  height: 16px;
}
.icon-user {
  background-image: url('sprite.png');
  background-position: -16px 0;
  width: 16px;
  height: 16px;
}
```

**方案3：内联资源（Data URI / Base64）**

```css
/* 小图片转为Base64内联到CSS中 */
.icon {
  background-image: url(data:image/png;base64,iVBORw0KGgo...);
}
/* 原理：小图片直接嵌入，不产生额外请求 */
/* 注意：Base64会比原文件大33%，仅适用于小图片 */
```

**方案4：使用 SVG Sprite**

```html
<svg style="display:none">
  <symbol id="icon-home" viewBox="0 0 24 24">...</symbol>
  <symbol id="icon-user" viewBox="0 0 24 24">...</symbol>
</svg>

<svg><use href="#icon-home"/></svg>
```

**方案5：使用 HTTP/2 多路复用**

```javascript
// HTTP/2下，多个请求可在一个TCP连接上并行
// 合并文件的需求降低
// 但仍需避免过多小文件（头部开销）
```

**方案6：缓存策略**

```javascript
// 强缓存 + 协商缓存减少重复请求
// Cache-Control: max-age=31536000  // 强缓存
// ETag / Last-Modified              // 协商缓存
```

**其他方案对比：**

| 方案 | 效果 | 实现难度 | 适用场景 |
|------|------|---------|---------|
| 合并文件 | ⭐⭐⭐⭐⭐ | 低 | 通用 |
| CSS Sprites | ⭐⭐⭐⭐ | 中 | 图标 |
| Data URI | ⭐⭐⭐ | 低 | 小图片 |
| SVG Sprite | ⭐⭐⭐ | 中 | 矢量图标 |
| HTTP/2 | ⭐⭐⭐⭐ | 高 | 服务器配置 |

---

**3. 请列举减少 DOM 操作的方法，并分析为什么频繁 DOM 操作会影响性能，同时说明哪些方法有效、哪些方法存在误区。**

**答案：**

**为什么频繁 DOM 操作影响性能：**

1. **DOM 操作引发重排和重绘**：每次 DOM 修改可能触发浏览器的布局计算和绘制。
2. **DOM 操作跨线程通信**：JavaScript 引擎和渲染引擎是分离的，DOM 操作需要跨线程通信。
3. **强制同步布局（Layout Thrashing）**：读取布局属性后立即修改样式，会导致浏览器被迫执行同步布局计算。

**有效的 DOM 优化方法：**

```javascript
// 方法1：使用DocumentFragment批量操作
const fragment = document.createDocumentFragment();
for (let i = 0; i < 100; i++) {
  const div = document.createElement('div');
  fragment.appendChild(div);
}
document.body.appendChild(fragment);  // 只触发一次重排

// 方法2：批量修改后一次性插入
element.style.display = 'none';  // 触发一次重排
element.style.width = '100px';
element.style.height = '100px';
element.style.display = 'block';  // 触发一次重排

// 方法3：使用cloneNode和replaceChild
const clone = element.cloneNode(true);
clone.style.width = '100px';
element.parentNode.replaceChild(clone, element);

// 方法4：避免频繁读取布局属性（防止强制同步布局）
const width = el.offsetWidth;  // 先缓存
for (let i = 0; i < 100; i++) {
  el.style.left = width + i + 'px';  // 只写不读
}

// 方法5：使用虚拟DOM（Vue/React框架内部优化）
// 通过diff算法最小化DOM操作

// 方法6：使用requestAnimationFrame
function animate() {
  element.style.transform = `translateX(${x}px)`;
  requestAnimationFrame(animate);
}
```

**使用 innerHTML 的误区：**

```javascript
// 使用innerHTML不是最优的减少DOM操作的方法
// 原因：
// 1. innerHTML需要解析HTML字符串，有解析开销
// 2. 会销毁并重建所有子节点，包括事件监听器
// 3. 存在XSS安全风险
// 相比之下，DocumentFragment和批量操作更安全高效
```

**性能优化综合建议：**

```javascript
// 1. 使用防抖和节流控制高频操作
function debounce(fn, delay) {
  let timer;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

function throttle(fn, delay) {
  let last = 0;
  return function(...args) {
    const now = Date.now();
    if (now - last >= delay) {
      last = now;
      fn.apply(this, args);
    }
  };
}

// 2. 使用transform和opacity做动画（只触发合成）
element.style.transform = 'translateX(100px)';

// 3. 事件委托
document.addEventListener('click', (e) => {
  if (e.target.matches('.button')) {
    // 处理所有.button元素的点击
  }
});
```

---

## ES6+新特性

### 问答题

**1. 请列举 ES6 的主要新特性，说明各特性的设计目的和使用场景，并区分哪些是 ES6 新增的、哪些是更早或更晚版本引入的。**

**答案：**

**ES6（ES2015）新增的核心特性：**

```javascript
// 1. let/const 块级作用域
{
  let a = 10;
  const b = 20;
}
// 设计目的：解决var的变量提升和作用域问题

// 2. 箭头函数
const sum = (a, b) => a + b;
// 设计目的：简化函数写法，解决this绑定问题

// 3. Promise
const p = new Promise((resolve, reject) => {});
// 设计目的：解决回调地狱，提供统一的异步编程接口

// 4. class 类语法
class Person {
  constructor(name) { this.name = name; }
}
// 设计目的：提供更清晰的面向对象语法（语法糖）

// 5. 模板字符串
const greeting = `Hello, ${name}!`;
// 设计目的：简化字符串拼接

// 6. 解构赋值
const { name, age } = user;
const [a, b] = arr;
// 设计目的：简化数据提取

// 7. 展开运算符
const arr2 = [...arr1, 3, 4];
// 设计目的：简化数组和对象的合并

// 8. 默认参数
function foo(a = 1, b = 2) {}
// 设计目的：简化默认值处理

// 9. Symbol
const sym = Symbol('id');
// 设计目的：提供唯一的属性键

// 10. Map/Set
const map = new Map();
const set = new Set();
// 设计目的：提供更完善的数据结构

// 11. Proxy/Reflect
const proxy = new Proxy(obj, {});
// 设计目的：提供对象代理和元编程能力

// 12. 模块化 import/export
import { foo } from './module.js';
export const bar = 123;
// 设计目的：原生模块化支持

// 13. Generator
function* gen() { yield 1; }
// 设计目的：提供可暂停的函数
```

**非 ES6 的常见特性（容易混淆）：**

```javascript
// 以下方法在ES5就已存在，不是ES6新增：
[1, 2, 3].map(x => x * 2);       // ES5
[1, 2, 3].filter(x => x > 1);    // ES5
[1, 2, 3].reduce((a, b) => a + b); // ES5
[1, 2, 3].forEach(x => console.log(x)); // ES5

// ES2016+ 新增：
[1, 2, 3].includes(2);           // ES2016
2 ** 10;                          // ES2016 指数运算符

// ES2017+ 新增：
Object.entries({a: 1});           // ES2017
Object.values({a: 1});            // ES2017
async function foo() {}           // ES2017

// ES2018+ 新增：
const { a, ...rest } = obj;       // ES2018 对象剩余/展开
const re = /(?<year>\d{4})/;      // ES2018 正则命名捕获组

// ES2020+ 新增：
user?.address?.street;            // ES2020 可选链
const name = userName ?? 'default'; // ES2020 空值合并
BigInt(123);                      // ES2020

// ES2022+ 新增：
class Counter { #count = 0; }     // ES2022 私有属性
await fetch();                    // ES2022 顶层await
```

---

**2. 请详细对比箭头函数和普通函数的区别，分析箭头函数的使用限制和适用场景。**

**答案：**

| 区别维度 | 箭头函数 | 普通函数 |
|---------|---------|---------|
| **this 绑定** | 没有自己的 this，继承外层 | 根据调用方式动态绑定 |
| **构造函数** | ❌ 不能作为构造函数 | ✅ 可以用 new 调用 |
| **arguments** | ❌ 没有 arguments 对象 | ✅ 有 arguments 对象 |
| **prototype** | ❌ 没有 prototype 属性 | ✅ 有 prototype 属性 |
| **yield** | ❌ 不能用作 Generator | ✅ 可以用 function* |
| **new.target** | ❌ 没有 | ✅ 有 |

**详细说明：**

```javascript
// 1. this 绑定
const obj = {
  name: 'Alice',
  // 箭头函数：this继承外层（定义时的词法作用域）
  arrow: () => console.log(this.name),  // undefined（this指向window/外层）
  
  // 普通函数：this指向调用者
  normal: function() { console.log(this.name); }  // 'Alice'
};

obj.arrow();   // undefined
obj.normal();  // 'Alice'

// 2. 不能作为构造函数
const Arrow = () => {};
new Arrow();  // TypeError: Arrow is not a constructor

function Normal() {}
new Normal();  // ✅ 正常

// 3. 没有arguments
const arrowFn = () => {
  console.log(arguments);  // ReferenceError
};

const normalFn = function() {
  console.log(arguments);  // Arguments对象
};

// 箭头函数使用剩余参数代替arguments
const arrowFn2 = (...args) => {
  console.log(args);  // 数组
};
```

**适用场景：**

```javascript
// ✅ 推荐：回调函数、需要外层this的场景
class Timer {
  constructor() {
    this.count = 0;
    // 箭头函数自动绑定this
    setInterval(() => {
      this.count++;  // this正确指向Timer实例
    }, 1000);
  }
}

// ✅ 推荐：简单的纯函数
const add = (a, b) => a + b;
const square = x => x * x;

// ❌ 不推荐：对象方法
const obj = {
  name: 'Alice',
  sayHi: () => console.log(this.name),  // this不指向obj！
};
obj.sayHi();  // undefined

// ❌ 不推荐：需要arguments的场景
// ❌ 不推荐：需要作为构造函数
// ❌ 不推荐：需要动态this的场景（如事件监听中需要this指向元素）
```

---

**3. 请分析以下代码的输出结果，并解释 `Array.prototype.flat` 方法的工作原理。**

```javascript
const arr = [1, [2, [3, 4]]];
console.log(arr.flat(2));
```

**答案：**

**输出结果：** `[1, 2, 3, 4]`

**flat 方法说明：**

`Array.prototype.flat()` 是 ES2019 新增的方法，用于将嵌套数组"拉平"。

```javascript
// flat(depth) 参数说明
// depth：指定要提取嵌套数组的深度，默认为1

const arr = [1, [2, [3, 4]]];

arr.flat();    // [1, 2, [3, 4]]   —— 默认深度1，只展开一层
arr.flat(1);   // [1, 2, [3, 4]]   —— 同上
arr.flat(2);   // [1, 2, 3, 4]     —— 深度2，展开两层
arr.flat(Infinity);  // [1, 2, 3, 4]  —— 展开所有层级
```

**工作原理：**

```javascript
// flat的简化实现
Array.prototype.myFlat = function(depth = 1) {
  function flatten(arr, currentDepth) {
    let result = [];
    for (const item of arr) {
      if (Array.isArray(item) && currentDepth < depth) {
        result = result.concat(flatten(item, currentDepth + 1));
      } else {
        result.push(item);
      }
    }
    return result;
  }
  return flatten(this, 0);
};

// flat会移除空位
[1, , 3].flat();  // [1, 3] —— 空位被移除
```

**相关方法 flatMap：**

```javascript
// flatMap = map + flat(1)
[1, 2, 3].flatMap(x => [x, x * 2]);
// [1, 2, 2, 4, 3, 6]  —— 先map再flat一层
```

---

## 工程化与架构

### 问答题

**1. 请说明 Webpack 的核心概念（Entry、Output、Loader、Plugin、Mode 等），并分析其工作流程。**

**答案：**

**Webpack 核心概念：**

| 概念 | 说明 | 作用 |
|------|------|------|
| **Entry** | 入口文件 | 指定Webpack从哪个文件开始构建依赖图 |
| **Output** | 输出配置 | 指定打包后的文件名和输出路径 |
| **Loader** | 模块转换器 | 将非JS文件（CSS、图片等）转换为JS模块 |
| **Plugin** | 插件 | 扩展Webpack功能（压缩、HTML生成等） |
| **Mode** | 模式 | development/production，影响优化行为 |
| **Module** | 模块 | 一切皆模块，Webpack通过依赖关系递归构建 |

**配置示例：**

```javascript
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  mode: 'production',  // 模式
  
  entry: './src/index.js',  // 入口
  
  output: {  // 输出
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.[contenthash].js'
  },
  
  module: {  // Loader配置
    rules: [
      { test: /\.js$/, use: 'babel-loader' },
      { test: /\.css$/, use: ['style-loader', 'css-loader'] },
      { test: /\.(png|jpg)$/, type: 'asset/resource' }
    ]
  },
  
  plugins: [  // 插件
    new HtmlWebpackPlugin({ template: './src/index.html' })
  ]
};
```

**Webpack 工作流程：**

```
1. 读取配置文件
2. 从Entry出发，递归解析依赖关系
3. 用Loader转换匹配的模块文件
4. 将所有模块组合成Chunk
5. 应用Plugin进行优化和处理
6. 输出最终打包文件到Output目录
```

**Loader vs Plugin 的区别：**

- **Loader**：文件级转换器，处理单个文件的内容（如 babel-loader 转译 JS）
- **Plugin**：全局级扩展，在整个构建生命周期中注入自定义逻辑（如 HtmlWebpackPlugin 生成 HTML）

**注意**：Router（路由）不是 Webpack 的核心概念，路由是前端框架（Vue Router、React Router）的概念。

---

**2. 请解释 Babel 的作用和工作原理，说明其在现代前端工程化中的地位。**

**答案：**

**Babel 的作用：**

Babel 是一个 JavaScript 编译器（转译器），主要作用是将新版 JavaScript 代码转换为向后兼容的旧版本代码，使其能在不支持新特性的浏览器或环境中运行。

**核心功能：**

```javascript
// 1. 语法转译
// 源代码（ES6+）
const greet = (name = 'World') => `Hello, ${name}!`;
class Person { ... }

// 转译后（ES5）
var greet = function(name) {
  name = name === undefined ? 'World' : name;
  return 'Hello, ' + name + '!';
};
function Person() { ... }

// 2. Polyfill（API补丁）
// 源代码
Promise.resolve().then(...);
Array.from(...);

// 转译后（注入polyfill）
require('core-js/promise');
require('core-js/array/from');
```

**Babel 工作原理：**

```
源代码
   │
   ▼
┌──────────────┐
│  Parse 解析   │  将代码解析为AST（抽象语法树）
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Transform 转换│  遍历AST，应用插件进行修改
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Generate 生成 │  将修改后的AST重新生成代码
└──────┬───────┘
       │
       ▼
   目标代码
```

**Babel 配置示例：**

```javascript
// .babelrc / babel.config.js
module.exports = {
  presets: [
    '@babel/preset-env',      // 根据目标环境自动转译
    '@babel/preset-react',    // 转译JSX
    '@babel/preset-typescript' // 转译TypeScript
  ],
  plugins: [
    '@babel/plugin-proposal-optional-chaining'
  ]
};
```

**在现代前端工程化中的地位：**

- 与 Webpack/Vite 等构建工具深度集成
- 支持 JSX、TypeScript 等非原生语法
- 是 React/Vue 等框架生态的基础设施
- Babel **只负责转译JavaScript语法**，不处理CSS、不打包文件、不压缩图片

---

**3. 请分析前端组件化开发的优势和局限，说明组件设计的核心原则和最佳实践。**

**答案：**

**组件化开发的优势：**

```javascript
// ✅ 提高复用性：一次编写，多处使用
const Button = { template: '<button>...</button>' };

// ✅ 提高可维护性：每个组件独立管理自己的逻辑和样式
// 修改一个组件不影响其他组件

// ✅ 便于团队协作：不同开发者负责不同组件
// 组件接口清晰，降低沟通成本
```

**组件化开发的局限：**

```javascript
// ❌ 不直接提高性能
// 组件化本身不会让页面更快
// 过度组件化反而可能增加性能开销（组件实例化、状态管理）

// ❌ 增加初始开发成本
// 需要设计组件接口、拆分粒度
// 简单页面可能不需要组件化
```

**组件设计的核心原则：**

```javascript
// 原则1：单一职责（每个组件只做一件事）
// ✅ 好的设计
const UserAvatar = { /* 只负责显示头像 */ };
const UserName = { /* 只负责显示名字 */ };

// ❌ 差的设计
const UserProfile = { /* 既显示头像、又显示名字、还处理编辑 */ };

// 原则2：高内聚低耦合
// 组件内部逻辑紧密相关，组件之间依赖最小化

// 原则3：合理的粒度
// 太细：组件过多，管理复杂
// 太粗：复用性差
// 经验法则：如果一个UI片段在多个地方复用，就拆成组件

// 原则4：清晰的接口（Props/Events）
const Button = {
  props: {
    type: { type: String, default: 'default' },  // 类型
    disabled: { type: Boolean, default: false },  // 是否禁用
    loading: { type: Boolean, default: false }     // 加载状态
  },
  emits: ['click'],  // 明确声明事件
  template: '<button @click="$emit(\'click\')">...</button>'
};

// 原则5：可配置性
// 通过Props提供配置项，slot提供内容扩展
const Card = {
  props: ['title'],
  template: `
    <div class="card">
      <div class="card-header">{{ title }}</div>
      <div class="card-body">
        <slot></slot>  <!-- 内容分发 -->
      </div>
    </div>
  `
};
```

---

**4. 请从构建工具、代码规范、测试、CI/CD 等方面说明现代前端工程化的完整体系。**

**答案：**

**构建工具：**

```javascript
// Webpack - 传统的模块打包工具
module.exports = {
  entry: './src/index.js',
  output: { filename: 'bundle.js' },
  module: {
    rules: [
      { test: /\.js$/, use: 'babel-loader' },
      { test: /\.css$/, use: ['style-loader', 'css-loader'] }
    ]
  }
};

// Vite - 现代前端构建工具（基于ESM，开发时极速启动）
export default {
  plugins: [vue()],
  build: {
    rollupOptions: { /* 配置 */ }
  }
};

// Rollup - 适合打包库
export default {
  input: 'src/main.js',
  output: { file: 'bundle.js', format: 'esm' }
};
```

**代码规范与质量检查：**

```javascript
// ESLint - 代码规范检查
module.exports = {
  env: { browser: true, es2021: true },
  rules: {
    'no-undef': 'error',
    'no-unused-vars': 'warn'
  }
};

// Prettier - 代码格式化
// .prettierrc
{ "semi": true, "singleQuote": true, "tabWidth": 2 }

// TypeScript - 类型检查
interface User { name: string; age: number; }
```

**测试：**

```javascript
// Jest / Vitest - 单元测试
test('1 + 1 should be 2', () => {
  expect(1 + 1).toBe(2);
});

// Cypress / Playwright - 端到端测试
describe('Todo List', () => {
  it('adds new todo', () => {
    cy.visit('/');
    cy.get('input').type('Buy milk{enter}');
    cy.contains('Buy milk');
  });
});
```

**CI/CD 流程：**

```yaml
# GitHub Actions 示例
name: CI/CD
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npm test
      - run: npm run build
```

**架构设计模式：**

```javascript
// MVC模式: Model-View-Controller
// MVVM模式（Vue）: Model-View-ViewModel
// Flux/Redux模式: Store-Action-Reducer
```

---

## 总结

高级JavaScript工程师需要掌握的核心知识：

1. **深入理解JavaScript原理**：
   - 原型与原型链
   - 执行上下文与闭包
   - Event Loop事件循环
   - 垃圾回收机制

2. **浏览器原理**：
   - 渲染流程与优化
   - 重排重绘原理
   - 存储机制
   - 浏览器安全

3. **网络协议**：
   - HTTP/HTTPS
   - TCP/UDP
   - WebSocket
   - 网络安全

4. **性能优化**：
   - 加载优化
   - 渲染优化
   - 代码优化
   - 性能监测

5. **工程化能力**：
   - 构建工具
   - 组件化设计
   - 测试
   - CI/CD

希望这份面试题能帮助您系统梳理和准备！
