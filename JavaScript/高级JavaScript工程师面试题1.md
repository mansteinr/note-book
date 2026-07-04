# 高级JavaScript工程师面试题

## 目录

- [高级JavaScript工程师面试题](#高级javascript工程师面试题)
  - [目录](#目录)
  - [浏览器垃圾清除机制原理](#浏览器垃圾清除机制原理)
    - [选择题](#选择题)
    - [简答题](#简答题)
  - [浏览器渲染流程和原理](#浏览器渲染流程和原理)
    - [选择题](#选择题-1)
    - [简答题](#简答题-1)
  - [Event Loop事件循环](#event-loop事件循环)
    - [选择题](#选择题-2)
    - [简答题](#简答题-2)
  - [闭包与作用域](#闭包与作用域)
    - [选择题](#选择题-3)
    - [简答题](#简答题-3)
  - [原型与原型链](#原型与原型链)
    - [选择题](#选择题-4)
    - [简答题](#简答题-4)
  - [网络协议与HTTP](#网络协议与http)
    - [选择题](#选择题-5)
    - [简答题](#简答题-5)
  - [JavaScript异步编程](#javascript异步编程)
    - [选择题](#选择题-6)
    - [简答题](#简答题-6)
  - [性能优化](#性能优化)
    - [选择题](#选择题-7)
    - [简答题](#简答题-7)
  - [ES6+新特性](#es6新特性)
    - [选择题](#选择题-8)
    - [简答题](#简答题-8)
  - [工程化与架构](#工程化与架构)
    - [选择题](#选择题-9)
    - [简答题](#简答题-9)
  - [总结](#总结)

---

## 浏览器垃圾清除机制原理

### 选择题

**1. JavaScript中，以下哪个不是垃圾回收的方式？**
A. 标记-清除
B. 引用计数
C. 标记-整理
D. 自动删除

**答案：D**

**2. 标记-清除算法的主要缺点是？**
A. 效率低
B. 会产生内存碎片
C. 需要额外空间
D. 实现复杂

**答案：B**

**3. V8引擎使用的垃圾回收算法是？**
A. 引用计数
B. 标记-清除
C. 分代收集
D. 以上都是

**答案：C**

**4. 内存泄漏的原因不包括？**
A. 意外的全局变量
B. 闭包
C. 定时器未清理
D. 局部变量

**答案：D**

---

### 简答题

**1. 请详细解释浏览器的垃圾回收机制原理，包括V8引擎的分代回收策略。**

**答案：**

**垃圾回收的基本概念：**

JavaScript的垃圾回收（Garbage Collection，GC）是自动进行的，通过判断对象是否还需要被引用来决定是否回收其内存。

**常见的垃圾回收算法：**

**1. 引用计数法：**
```javascript
// 思路：跟踪每个对象被引用的次数
let a = { obj: 1 };  // 引用计数：1
let b = a;           // 引用计数：2
a = null;            // 引用计数：1
b = null;            // 引用计数：0 → 可以回收

// 缺点：循环引用无法回收
function cycle() {
  let a = {};
  let b = {};
  a.prop = b;
  b.prop = a;
}  // a和b永远不会被回收
```

**2. 标记-清除法：**
```
从根对象（window/global）开始
→ 标记所有能到达的对象
→ 清除没有被标记的对象
→ 优点：解决了循环引用问题
→ 缺点：产生内存碎片
```

**3. 标记-整理法：**
```
在标记-清除基础上
→ 标记后整理，把存活对象向一端移动
→ 然后清理掉边界外的内存
→ 避免内存碎片
```

**V8引擎的分代回收策略：**

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

**老生代区域（大空间，存活时间长）：**
```javascript
// 使用 Mark-Sweep（标记-清除）和 Mark-Compact（标记-整理）
// Mark-Sweep 先标记，再清除
// Mark-Compact 清除后整理内存

// 对象晋升条件：
// 1. 经历过一次 Scavenge 回收
// 2. To 空间使用超过 25%

// 全停顿（Stop-The-World）优化：
// - 增量标记（Incremental Marking）
// - 并行标记
// - 惰性清理
```

**V8垃圾回收流程可视化：**
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

**如何避免内存泄漏：**

```javascript
// 1. 避免意外的全局变量
function bad() {
  leak = 'this is global';  // 没有var/let/const，变成全局变量
}

// 2. 及时清理定时器和监听器
let timer = setInterval(() => {}, 1000);
// 不用时清理
clearInterval(timer);

// 3. 闭包可能导致内存泄漏
function closureLeak() {
  const bigData = new Array(1000000);
  return function() {
    return bigData;  // bigData被引用，不会回收
  }
}

// 4. 及时清理DOM引用
let dom = document.getElementById('xxx');
// 使用后
dom = null;

// 5. Map/Set的引用
let map = new Map();
map.set(dom, 'info');
// 改用WeakMap
let weakMap = new WeakMap();
weakMap.set(dom, 'info');  // WeakMap不阻止回收
```

---

**2. 常见的内存泄漏场景有哪些？如何检测和预防？**

**答案：**

**常见内存泄漏场景：**

**1. 意外的全局变量：**
```javascript
function foo() {
  bar = 'this is global';  // 没有声明，自动成为全局变量
  this.baz = 'also global'; // this指向window时
}
```

**2. 未清理的定时器和回调函数：**
```javascript
let timer = setInterval(() => {
  let dom = document.getElementById('element');
  if (dom) {
    // do something
  }
}, 1000);
// 组件销毁时忘记清理定时器
```

**3. 脱离DOM的引用：**
```javascript
let elements = {
  button: document.getElementById('button'),
  image: document.getElementById('image')
};
// DOM被删除了，但elements还在引用
document.body.removeChild(elements.button);
// 即使DOM移除了，elements.button还在，无法回收
```

**4. 闭包引起的泄漏：**
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

**5. 未清理的事件监听器：**
```javascript
const element = document.getElementById('my-element');
element.addEventListener('click', onClick);
// 移除元素时忘记移除监听器
element.parentNode.removeChild(element);
```

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
// ESLint规则
// no-undef - 避免未声明变量
// no-global-assign - 避免全局变量赋值

// 3. 使用WeakMap/WeakSet
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

### 选择题

**1. 浏览器渲染页面的正确顺序是？**
A. HTML解析 → 样式计算 → 布局 → 绘制 → 合成
B. 样式计算 → HTML解析 → 布局 → 绘制 → 合成
C. HTML解析 → 布局 → 样式计算 → 绘制 → 合成
D. HTML解析 → 样式计算 → 绘制 → 布局 → 合成

**答案：A**

**2. 会触发reflow的操作是？**
A. 修改元素颜色
B. 修改元素尺寸
C. 修改背景图片
D. 修改transform

**答案：B**

**3. CSS中，以下哪个属性变化只会触发repaint？**
A. width
B. transform
C. color
D. display

**答案：C**

**4. 浏览器分层的好处不包括？**
A. 减少重绘范围
B. 提高性能
C. 节约内存
D. 可以独立控制层级

**答案：C**

---

### 简答题

**1. 请详细描述浏览器的完整渲染流程，从HTML到像素显示在屏幕上。**

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

// 关键路径
// 解析HTML -> 解析CSS -> 执行JS -> 构建DOM -> 布局 -> 绘制
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

**2. 请解释reflow和repaint的区别，以及如何减少它们的发生。**

**答案：**

**重排（Reflow / Layout）：**
```
定义：布局发生变化，需要重新计算几何信息
触发原因：
- 元素尺寸、位置变化
- 元素内容变化
- 页面初始渲染
- 浏览器窗口变化
- 访问offsetWidth/clientWidth等属性

// 会触发重排的属性
element.style.width = '100px';
element.style.height = '100px';
element.style.margin = '10px';
element.style.padding = '10px';
element.style.border = '1px solid';
element.style.display = 'block';
element.style.position = 'absolute';

// 获取布局属性也会触发
const width = element.offsetWidth;
const height = element.offsetHeight;
const top = element.offsetTop;
const left = element.offsetLeft;
```

**重绘（Repaint / Paint）：**
```
定义：样式变化但布局不变，只需重新绘制
触发原因：
- 颜色变化
- 背景图片变化
- 阴影变化
- visibility变化
- 其他不影响布局的样式变化

// 只会触发重绘的属性
element.style.color = 'red';
element.style.background = '#fff';
element.style.boxShadow = '1px 1px 5px rgba(0,0,0,0.5)';
element.style.borderColor = 'blue';
element.style.visibility = 'hidden';
```

**重排和重绘的关系：**
```
重排必然引发重绘
重绘不一定引发重排

性能影响：重排 > 重绘
```

**减少重排重绘的方法：**

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

// 方法3：使用文档片段（DocumentFragment）
const fragment = document.createDocumentFragment();
// 批量添加到fragment，不会触发重排
fragment.appendChild(el1);
fragment.appendChild(el2);
fragment.appendChild(el3);
// 最后一次性插入
container.appendChild(fragment);

// 方法4：使用cloneNode和replaceChild
const clone = element.cloneNode(true);
// 修改clone，不触发重排
clone.style.width = '100px';
clone.style.height = '100px';
// 最后替换，只触发一次重排
element.parentNode.replaceChild(clone, element);

// 方法5：避免频繁读取布局属性
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

// 方法6：使用transform代替top/left/width等
// transform不会触发重排
element.style.transform = 'translateX(100px)';  // 好
element.style.left = '100px';  // 不好，会触发重排

// 方法7：使用requestAnimationFrame优化动画
function animate() {
  // 动画操作
  element.style.transform = `translateX(${x}px)`;
  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);

// 方法8：使用will-change提示浏览器
element.style.willChange = 'transform';  // 提示浏览器transform会变化
```

---

## Event Loop事件循环

### 选择题

**1. JavaScript的执行机制是？**
A. 多线程
B. 单线程
C. 并发
D. 并行

**答案：B**

**2. 以下哪个是微任务？**
A. setTimeout
B. Promise.then
C. setInterval
D. I/O事件

**答案：B**

**3. 一个周期内任务执行顺序正确的是？**
A. 宏任务 → 微任务 → 渲染
B. 微任务 → 宏任务 → 渲染
C. 渲染 → 宏任务 → 微任务
D. 渲染 → 微任务 → 宏任务

**答案：A**

**4. Promise.resolve().then(() => {}) 放入什么队列？**
A. 宏任务队列
B. 微任务队列
C. 同步执行
D. 都不对

**答案：B**

---

### 简答题

**1. 请详细解释Event Loop事件循环的工作原理，包括宏任务、微任务的执行顺序。**

**答案：**

**JavaScript运行机制：**

```
JavaScript是单线程的
→ 同一时间只能执行一个任务
→ 通过Event Loop来调度任务执行
```

**任务队列分类：**

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
│         │            │  │ - setImmediate │ │  │
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

**宏任务（Macro Task）：**
```javascript
// 常见宏任务
setTimeout(() => {
  console.log('setTimeout');
});

setInterval(() => {
  console.log('setInterval');
});

setImmediate(() => {
  console.log('setImmediate');
});

requestAnimationFrame(() => {
  console.log('requestAnimationFrame');
});

// I/O操作
fs.readFile('/path', () => {
  console.log('read file');
});

// DOM事件
element.addEventListener('click', () => {
  console.log('click');
});
```

**微任务（Micro Task）：**
```javascript
// 常见微任务
Promise.resolve().then(() => {
  console.log('Promise then');
});

// async/await
async function foo() {
  await bar();  // await后的代码是微任务
  console.log('after await');
}

// queueMicrotask
queueMicrotask(() => {
  console.log('queueMicrotask');
});

// MutationObserver
const observer = new MutationObserver(() => {
  console.log('DOM changed');
});
```

**Event Loop执行流程：**

```javascript
// 完整循环步骤
1. 执行同步代码（调用栈清空）
2. 执行所有微任务队列中的任务
3. 执行浏览器渲染（如果需要）
4. 取出一个宏任务执行
5. 返回步骤2，循环往复

// 简化示例
console.log(1);  // 同步任务

setTimeout(() => console.log(2), 0);  // 宏任务

Promise.resolve().then(() => console.log(3));  // 微任务

// 执行顺序
// 1 → 3 → 2
```

**经典面试题示例：**

```javascript
// 题目1
console.log('1');

setTimeout(() => {
  console.log('2');
}, 0);

Promise.resolve().then(() => {
  console.log('3');
});

console.log('4');

// 答案：1 4 3 2

// 题目2
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

// 题目3（复杂版）
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

**浏览器环境与Node.js环境的差异：**
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

## 闭包与作用域

### 选择题

**1. 闭包的作用不包括？**
A. 访问函数内部变量
B. 让变量长期保存在内存
C. 提高性能
D. 实现封装

**答案：C**

**2. 关于闭包，以下说法正确的是？**
A. 闭包会导致内存泄漏
B. 闭包会降低性能
C. 闭包是JavaScript特有的
D. 闭包让函数可以记住词法作用域

**答案：D**

**3. 以下代码输出结果是？**
```javascript
for (var i = 0; i < 5; i++) {
  setTimeout(() => console.log(i), 1000);
}
```
A. 0 1 2 3 4
B. 5 5 5 5 5
C. 0 1 2 3 4 5
D. 报错

**答案：B**

---

### 简答题

**1. 请解释闭包的原理及其应用场景。**

**答案：**

**闭包定义：**
```javascript
// 当一个函数能够记住并访问它的词法作用域
// 即使该函数在其词法作用域之外执行时
// 就产生了闭包

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
```javascript
1. 函数嵌套函数
2. 内部函数引用外部函数的变量
3. 内部函数被外部返回或被外部引用
```

**闭包的应用场景：**

**场景1：数据封装/私有变量**
```javascript
function createCounter() {
  let count = 0;  // 私有变量，外部无法直接访问
  
  return {
    increment() {
      count++;
      return count;
    },
    decrement() {
      count--;
      return count;
    },
    getCount() {
      return count;
    }
  };
}

const counter = createCounter();
counter.increment();  // 1
counter.increment();  // 2
counter.decrement();  // 1
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

function sum(a, b, c) {
  return a + b + c;
}

const curriedSum = curry(sum);
curriedSum(1)(2)(3);  // 6
curriedSum(1, 2)(3);  // 6
```

**场景3：事件处理与回调**
```javascript
for (let i = 0; i < 5; i++) {
  document.getElementById('btn-' + i).addEventListener('click', () => {
    console.log('Click button ' + i);  // i被闭包保存
  });
}
```

**场景4：模块模式**
```javascript
const module = (function() {
  let privateData = 'private';
  
  function privateMethod() {
    console.log('This is private');
  }
  
  return {
    publicMethod() {
      privateMethod();  // 可以访问私有
    },
    setPrivateData(newValue) {
      privateData = newValue;
    }
  };
})();

module.publicMethod();
```

**闭包常见问题：**

```javascript
// 问题1：经典for循环面试题
for (var i = 0; i < 5; i++) {
  setTimeout(() => {
    console.log(i);  // 5次都是5
  }, 1000);
}

// 解法1：let块级作用域
for (let i = 0; i < 5; i++) {
  setTimeout(() => {
    console.log(i);  // 0,1,2,3,4
  }, 1000);
}

// 解法2：立即执行函数（IIFE）
for (var i = 0; i < 5; i++) {
  (function(j) {
    setTimeout(() => {
      console.log(j);  // 0,1,2,3,4
    }, 1000);
  })(i);
}

// 解法3：使用bind
for (var i = 0; i < 5; i++) {
  setTimeout(console.log.bind(console, i), 1000);
}

// 问题2：内存泄漏
function leakMemory() {
  let bigData = new Array(1000000);  // 大数组
  return function() {
    return bigData;  // bigData被闭包引用，无法回收
  };
}

// 解决：及时释放引用
function cleanup() {
  bigData = null;  // 释放引用
}
```

---

## 原型与原型链

### 选择题

**1. 以下关于原型的说法正确的是？**
A. 每个函数都有prototype属性
B. 每个对象都有prototype属性
C. 对象的__proto__指向自身
D. 原型链的顶端是undefined

**答案：A**

**2. Object.prototype.__proto__的值是？**
A. Object.prototype
B. null
C. undefined
D. Object

**答案：B**

**3. 以下代码输出结果是？**
```javascript
function Person() {}
Person.prototype.name = 'Person';
const person = new Person();
person.name = 'Tom';
console.log(person.name);
```
A. Person
B. Tom
C. undefined
D. 报错

**答案：B**

---

### 简答题

**1. 请详细解释原型和原型链的工作原理，以及如何通过原型实现继承。**

**答案：**

**原型基本概念：**

```javascript
// 每个函数都有 prototype 属性
function Person() {}
console.log(Person.prototype);  // { constructor: Person }

// 每个对象都有 __proto__ 属性（隐式原型）
const person = new Person();
console.log(person.__proto__ === Person.prototype);  // true

// 关系图
person
  └── __proto__ ───────→ Person.prototype
                            ├── constructor ──→ Person
                            └── __proto__ ─────→ Object.prototype
                                              └── __proto__ ──→ null
```

**原型链图示：**

```javascript
// 原型链结构
person.__proto__ === Person.prototype;
Person.prototype.__proto__ === Object.prototype;
Object.prototype.__proto__ === null;  // 原型链终点

// 完整链
// person -> Person.prototype -> Object.prototype -> null
```

**属性查找规则：**

```javascript
// 当访问对象属性时
// 1. 先在对象自身查找
// 2. 找不到，去__proto__中查找
// 3. 继续往上，直到找到或到null

function Person() {}
Person.prototype.name = 'Prototype Person';

const person1 = new Person();
const person2 = new Person();

person1.name = 'Tom';  // 对象自身属性

console.log(person1.name);  // Tom - 找到自身
console.log(person2.name);  // Prototype Person - 找到原型
```

**原型继承的实现方式：**

**方式1：原型链继承**
```javascript
function Animal(name) {
  this.name = name;
}
Animal.prototype.sayName = function() {
  console.log(this.name);
};

function Dog(name, breed) {
  this.breed = breed;
}
Dog.prototype = new Animal('Dog');  // 原型链继承
Dog.prototype.constructor = Dog;  // 修正构造函数

const dog = new Dog('Fido', 'Golden Retriever');
dog.sayName();  // Dog
// 缺点：1. 无法给父构造函数传参 2. 所有实例共享父属性
```

**方式2：构造函数继承**
```javascript
function Animal(name) {
  this.name = name;
}

function Dog(name, breed) {
  Animal.call(this, name);  // 调用父构造函数
  this.breed = breed;
}

const dog = new Dog('Fido', 'Golden');
console.log(dog.name);  // Fido
// 优点：可以传参，不共享父属性
// 缺点：无法继承父原型方法
```

**方式3：组合继承（原型链 + 构造函数）**
```javascript
function Animal(name) {
  this.name = name;
}
Animal.prototype.sayName = function() {
  console.log(this.name);
};

function Dog(name, breed) {
  Animal.call(this, name);  // 构造函数继承
  this.breed = breed;
}
Dog.prototype = new Animal();  // 原型链继承
Dog.prototype.constructor = Dog;

const dog = new Dog('Fido', 'Golden');
dog.sayName();  // Fido
// 优点：结合两者优点
// 缺点：父构造函数被调用两次
```

**方式4：寄生组合继承（最完美）**
```javascript
function Animal(name) {
  this.name = name;
}
Animal.prototype.sayName = function() {
  console.log(this.name);
};

function Dog(name, breed) {
  Animal.call(this, name);
  this.breed = breed;
}

// 关键步骤：原型式继承
function object(o) {
  function F() {}
  F.prototype = o;
  return new F();
}

Dog.prototype = object(Animal.prototype);
Dog.prototype.constructor = Dog;

const dog = new Dog('Fido', 'Golden');
dog.sayName();  // Fido
// 优点：避免了父构造函数被调用两次
```

**方式5：ES6 class继承（语法糖）**
```javascript
class Animal {
  constructor(name) {
    this.name = name;
  }
  
  sayName() {
    console.log(this.name);
  }
}

class Dog extends Animal {
  constructor(name, breed) {
    super(name);  // 调用父构造函数
    this.breed = breed;
  }
  
  bark() {
    console.log('Woof!');
  }
}

const dog = new Dog('Fido', 'Golden');
dog.sayName();  // Fido
dog.bark();  // Woof!
```

**原型继承的判断方法：**

```javascript
function Animal() {}
function Dog() {}
Dog.prototype = new Animal();
const dog = new Dog();

console.log(dog instanceof Dog);  // true
console.log(dog instanceof Animal);  // true
console.log(dog instanceof Object);  // true

console.log(Dog.prototype.isPrototypeOf(dog));  // true
console.log(Animal.prototype.isPrototypeOf(dog));  // true
```

---

## 网络协议与HTTP

### 选择题

**1. OSI七层模型中，HTTP位于哪一层？**
A. 网络层
B. 传输层
C. 应用层
D. 数据链路层

**答案：C**

**2. TCP三次握手的正确顺序是？**
A. SYN → SYN+ACK → ACK
B. ACK → SYN → SYN+ACK
C. SYN+ACK → SYN → ACK
D. ACK → SYN+ACK → SYN

**答案：A**

**3. HTTP 2.0相比1.1的特点不包括？**
A. 多路复用
B. 二进制分帧
C. 服务器推送
D. 更加安全

**答案：D**

---

### 简答题

**1. 请详细解释TCP的三次握手和四次挥手过程。**

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

// 为什么是三次握手？
// 1. 确认双方发送、接收能力正常
// 2. 同步序列号（seq）
// 3. 防止重复连接
```

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

// 为什么是四次挥手？
// 因为TCP是全双工的，关闭时需要单独关闭两个方向的连接
```

**常见HTTP状态码：**

```javascript
// 1XX 信息
100 Continue  // 继续
101 Switching Protocols  // 切换协议

// 2XX 成功
200 OK  // 请求成功
201 Created  // 创建成功
204 No Content  // 无内容

// 3XX 重定向
301 Moved Permanently  // 永久重定向
302 Found  // 临时重定向
304 Not Modified  // 未修改（缓存相关）

// 4XX 客户端错误
400 Bad Request  // 错误请求
401 Unauthorized  // 未授权
403 Forbidden  // 禁止访问
404 Not Found  // 未找到
405 Method Not Allowed  // 方法不允许
408 Request Timeout  // 请求超时
429 Too Many Requests  // 请求过多

// 5XX 服务端错误
500 Internal Server Error  // 服务器错误
502 Bad Gateway  // 网关错误
503 Service Unavailable  // 服务不可用
504 Gateway Timeout  // 网关超时
```

**HTTP1.1 vs HTTP2 vs HTTP3：**

```javascript
// HTTP1.1
// - 支持持久连接
// - 管线化（Pipelining）支持
// - Host头
// - 缺点：队头阻塞（Head-of-line blocking）

// HTTP2
// - 二进制协议（不再是文本协议）
// - 多路复用（Multiplexing）
// - 头部压缩（HPACK）
// - 服务器推送（Server Push）
// - 流控制

// HTTP3
// - 基于QUIC协议
// - 基于UDP
// - 彻底解决队头阻塞
// - 更快的连接建立
// - 更好的网络切换体验
```

---

## JavaScript异步编程

### 选择题

**1. Promise的状态不包括？**
A. pending
B. fulfilled
C. rejected
D. finished

**答案：D**

**2. 以下关于async/await的说法错误的是？**
A. async函数总是返回Promise
B. await只能在async函数中使用
C. await后面必须接Promise
D. await让代码看起来像同步代码

**答案：C**

**3. Promise.all在什么情况下会被reject？**
A. 任何一个Promise被reject
B. 所有Promise被reject
C. 第一个Promise被reject
D. 不会被reject

**答案：A**

---

### 简答题

**1. 请对比异步编程的几种方案：Callback、Promise、Generator、Async/Await。**

**答案：**

**回调函数Callback（早期方案）：**
```javascript
// 回调地狱
function loadData(url, callback) {
  ajax(url, function(data1) {
    ajax(data1.url, function(data2) {
      ajax(data2.url, function(data3) {
        // 嵌套太深
      });
    });
  });
}

// 错误处理困难
function readFiles(callback) {
  fs.readFile('file1', (err, data1) => {
    if (err) {
      callback(err);
      return;
    }
    fs.readFile('file2', (err, data2) => {
      if (err) {
        callback(err);
        return;
      }
      callback(null, [data1, data2]);
    });
  });
}
```

**Promise方案：**
```javascript
function asyncTask() {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      resolve('success');
      // or reject('error');
    }, 1000);
  });
}

// 链式调用
asyncTask()
  .then(data => processData(data))
  .then(result => saveResult(result))
  .catch(error => handleError(error));

// Promise静态方法
Promise.all([p1, p2, p3]);  // 全部成功才成功，一个失败就失败
Promise.allSettled([p1, p2, p3]);  // 等待所有完成
Promise.race([p1, p2, p3]);  // 竞速，取第一个完成的
Promise.any([p1, p2, p3]);  // 取第一个成功的
Promise.resolve(1);  // 包装为fulfilled的Promise
Promise.reject(new Error());  // 包装为rejected的Promise
```

**Generator方案：**
```javascript
function* gen() {
  const data1 = yield fetch('/api/data1');
  const data2 = yield fetch('/api/data2');
  return { data1, data2 };
}

// Generator + Promise 自动执行
function run(generator) {
  const iterator = generator();
  
  function next(result) {
    const { value, done } = iterator.next(result);
    if (done) {
      return value;
    }
    return Promise.resolve(value).then(next);
  }
  
  return next();
}

// 使用
run(gen).then(result => {
  console.log(result);
});
```

**Async/Await方案（推荐）：**
```javascript
async function getData() {
  try {
    const data1 = await fetch('/api/data1');
    const data2 = await fetch('/api/data2');
    return { data1, data2 };
  } catch (error) {
    console.error(error);
  }
}

// 并发执行
async function concurrent() {
  const [data1, data2] = await Promise.all([
    fetch('/api/data1'),
    fetch('/api/data2')
  ]);
}

// 返回值总是Promise
async function foo() {
  return 123;
}
foo().then(data => console.log(data));  // 123
```

**对比总结：**

| 方案 | 优点 | 缺点 |
|------|------|------|
| Callback | 简单易懂 | 回调地狱，错误处理困难 |
| Promise | 链式调用，好处理错误 | 有一定学习成本 |
| Generator | 可以暂停执行 | 需要手动或自动执行函数 |
| Async/Await | 写法像同步，最佳方案 | 需要ES7支持 |

---

## 性能优化

### 选择题

**1. 图片格式中，哪个支持透明且无损？**
A. JPEG
B. PNG
C. GIF
D. WebP

**答案：B**

**2. 以下哪个方案对减少HTTP请求数最有效？**
A. 图片懒加载
B. 合并CSS/JS文件
C. CDN加速
D. 服务器渲染

**答案：B**

**3. 减少DOM操作的方法不包括？**
A. 使用DocumentFragment
B. 批量修改
C. 使用innerHTML
D. 使用虚拟DOM

**答案：C**

---

### 简答题

**1. Web前端性能优化的方法有哪些？请从加载、渲染、代码层面进行说明。**

**答案：**

**加载优化：**

```javascript
// 1. 资源压缩与合并
// - 压缩JS: Terser, UglifyJS
// - 压缩CSS: PostCSS, cssnano
// - 图片压缩: tinypng, imagemin

// 2. 资源懒加载
// 图片懒加载
<img data-src="image.jpg" loading="lazy">

// 使用Intersection Observer
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.src = entry.target.dataset.src;
      observer.unobserve(entry.target);
    }
  });
});

// 路由懒加载（Vue）
const Home = () => import('./Home.vue');

// 3. 使用CDN
// 将静态资源放在CDN上
<script src="https://cdn.example.com/vue.js"></script>

// 4. 预加载资源
<link rel="preload" href="important.js" as="script">
<link rel="prefetch" href="future.js" as="script">
<link rel="dns-prefetch" href="//api.example.com">

// 5. 使用Service Worker缓存
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
```

**渲染优化：**

```javascript
// 1. 减少DOM操作
const fragment = document.createDocumentFragment();
for (let i = 0; i < 100; i++) {
  const div = document.createElement('div');
  fragment.appendChild(div);
}
document.body.appendChild(fragment);  // 只操作一次DOM

// 2. 使用虚拟DOM
// Vue/React等框架内部实现了虚拟DOM优化

// 3. 防抖和节流
// 防抖（debounce）
function debounce(fn, delay) {
  let timer;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

// 节流（throttle）
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

// 4. 使用requestAnimationFrame
function animate() {
  element.style.transform = `translateX(${x}px)`;
  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);

// 5. 使用transform和opacity
element.style.transform = 'translateX(100px)';  // 只触发合成
element.style.opacity = '0.5';  // 只触发合成
// 避免修改：width, height, top, left等会触发重排的属性
```

**代码层面优化：**

```javascript
// 1. 避免不必要的计算
// 缓存计算结果
function heavyComputation() {
  let result;
  return function() {
    if (result) return result;
    result = /* 昂贵计算 */;
    return result;
  };
}

// 2. 选择正确的事件委托
document.addEventListener('click', (e) => {
  if (e.target.matches('.button')) {
    // 处理所有.button元素的点击
  }
});
// 代替给每个button单独绑定事件

// 3. 循环优化
// 缓存长度
const len = array.length;
for (let i = 0; i < len; i++) {
  // ...
}

// 从后往前遍历
for (let i = array.length; i--; ) {
  // ...
}

// 4. 使用位运算
// ❌
let isEven = n % 2 === 0;

// ✅
let isEven = (n & 1) === 0;

// 5. Web Worker处理耗时任务
const worker = new Worker('worker.js');
worker.postMessage(data);
worker.onmessage = (e) => console.log(e.data);
```

**性能检测工具：**

```javascript
// Lighthouse审计
// Chrome DevTools的Lighthouse可以全面检测性能

// Performance面板
// 录制页面加载，分析各个阶段耗时

// Performance API
const t0 = performance.now();
// 执行操作
const t1 = performance.now();
console.log(`Time taken: ${t1 - t0}ms`);

// 控制台面板
// 查看console.time()输出
console.time('test');
// 代码
console.timeEnd('test');
```

---

## ES6+新特性

### 选择题

**1. 以下哪个不是ES6新增的特性？**
A. let/const
B. Promise
C. class
D. arrow function
E. map/filter/reduce

**答案：E**

**2. 箭头函数和普通函数的区别是？**
A. 没有自己的this
B. 不能作为构造函数
C. 没有arguments对象
D. 以上都是

**答案：D**

**3. 以下代码输出结果是？**
```javascript
const arr = [1, [2, [3, 4]]];
console.log(arr.flat(2));
```
A. [1, 2, [3,4]]
B. [1,2,3,4]
C. [1,[2,[3,4]]]
D. 报错

**答案：B**

---

### 简答题

**1. ES6+的常用新特性有哪些？请列举并说明。**

**答案：**

**let/const块级作用域：**
```javascript
// 块级作用域
{
  let a = 10;
  const b = 20;
}
console.log(a);  // ReferenceError

// const声明常量
const PI = 3.14;
PI = 3.1415;  // TypeError

// 但对象属性可以修改
const obj = { x: 1 };
obj.x = 2;  // OK
```

**箭头函数：**
```javascript
// 简写
const sum = (a, b) => a + b;

// 不绑定this
const obj = {
  init() {
    document.addEventListener('click', () => {
      this.doSomething();  // this指向obj，而不是document
    });
  },
  doSomething() {}
};

// 没有arguments
const fn = () => {
  console.log(arguments);  // ReferenceError
};
```

**解构赋值：**
```javascript
// 数组解构
const [a, b, ...c] = [1, 2, 3, 4, 5];

// 对象解构
const { name, age, ...rest } = {
  name: 'Tom',
  age: 18,
  gender: 'male',
  city: 'beijing'
};

// 默认值
const { x = 10 } = { x: undefined };

// 解构重命名
const { name: username } = user;
```

**展开运算符：**
```javascript
// 数组展开
const arr1 = [1, 2];
const arr2 = [...arr1, 3, 4];  // [1,2,3,4]

// 对象展开
const obj1 = { x: 1 };
const obj2 = { y: 2, ...obj1 };  // {y:2, x:1}

// 函数参数展开
function sum(...nums) {
  return nums.reduce((a, b) => a + b);
}
sum(1, 2, 3);
```

**Promise：**
```javascript
const promise = new Promise((resolve, reject) => {
  setTimeout(() => resolve('done'), 1000);
});

promise.then(result => console.log(result));
```

**Class：**
```javascript
class Person {
  constructor(name) {
    this.name = name;
  }
  
  sayHello() {
    console.log(`Hello, ${this.name}`);
  }
  
  // 静态方法
  static create(name) {
    return new Person(name);
  }
}

class Student extends Person {
  constructor(name, grade) {
    super(name);
    this.grade = grade;
  }
}
```

**Map/Set：**
```javascript
// Map
const map = new Map();
map.set('name', 'Tom');
map.get('name');

// Set
const set = new Set();
set.add(1);
set.add(1);  // 不会重复
set.size;  // 1
```

**ES6+更多特性：**
```javascript
// Symbol - 唯一标识符
const sym = Symbol('id');

// Generator - 可暂停函数
function* gen() {
  yield 1;
  yield 2;
  return 3;
}

// Proxy - 代理对象
const proxy = new Proxy(obj, {
  get(target, prop) {
    console.log(`Getting ${prop}`);
    return target[prop];
  }
});

// async/await - 异步语法糖
async function fetchData() {
  const data = await fetch('/api');
  return data;
}

// 数组新增方法
[1,2,3].includes(2);  // true
[1,2,3].find(x => x > 1);  // 2
[1,2,3].findIndex(x => x > 1);  // 1
[1,[2,3]].flat(2);  // [1,2,3]

// 对象新增方法
Object.assign({}, {a:1}, {b:2});
Object.entries({a:1, b:2});  // [['a',1], ['b',2]]

// 可选链
user?.address?.street;  // 安全访问嵌套属性

// 空值合并
const name = userName ?? 'default';

// 类的私有属性
class Counter {
  #count = 0;
  inc() {
    this.#count++;
  }
}
```

---

## 工程化与架构

### 选择题

**1. Webpack的核心概念不包括？**
A. Entry
B. Output
C. Loader
D. Router

**答案：D**

**2. Babel的作用是？**
A. 打包文件
B. 转译JavaScript语法
C. 处理CSS
D. 压缩图片

**答案：B**

**3. 组件化开发的优点不包括？**
A. 提高复用性
B. 提高可维护性
C. 提高性能
D. 便于团队协作

**答案：C**

---

### 简答题

**1. 现代前端工程化包括哪些内容？请从构建、测试、部署方面说明。**

**答案：**

**构建工具：**

```javascript
// Webpack
module.exports = {
  entry: './src/index.js',
  output: {
    filename: 'bundle.js'
  },
  module: {
    rules: [
      { test: /\.js$/, use: 'babel-loader' },
      { test: /\.css$/, use: ['style-loader', 'css-loader'] }
    ]
  }
};

// Vite - 现代前端构建工具
export default {
  plugins: [vue()],
  build: {
    rollupOptions: {
      // 配置
    }
  }
};

// Rollup - 打包库
export default {
  input: 'src/main.js',
  output: {
    file: 'bundle.js',
    format: 'esm'
  }
};
```

**代码规范与质量检查：**

```javascript
// ESLint
// .eslintrc.js
module.exports = {
  env: {
    browser: true,
    es2021: true
  },
  rules: {
    'no-undef': 'error',
    'no-unused-vars': 'warn'
  }
};

// Prettier - 代码格式化
// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2
}

// TypeScript - 类型检查
interface User {
  name: string;
  age: number;
}
```

**测试：**

```javascript
// Jest - 单元测试
test('1 + 1 should be 2', () => {
  expect(1 + 1).toBe(2);
});

// Vitest
import { describe, it, expect } from 'vitest';
describe('math', () => {
  it('1+1', () => {
    expect(1+1).toBe(2);
  });
});

// 端到端测试
// Cypress / Playwright
describe('Todo List', () => {
  it('adds new todo', () => {
    cy.visit('/');
    cy.get('input').type('Buy milk{enter}');
    cy.contains('Buy milk');
  });
});
```

**CI/CD流程：**

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
// MVC模式
// - Model: 数据模型
// - View: 视图
// - Controller: 控制器

// MVVM模式（Vue, Knockout）
// - Model
// - View
// - ViewModel

// Flux/Redux模式
// - Store: 唯一状态管理
// - Action: 描述事件
// - Reducer: 纯函数更新状态
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
