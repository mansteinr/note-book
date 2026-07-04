# 高级JavaScript工程师面试题

## 目录

- [浏览器垃圾回收机制专题](#浏览器垃圾回收机制专题)
- [浏览器渲染原理专题](#浏览器渲染原理专题)
- [JavaScript核心知识点](#javascript核心知识点)
- [前端工程化与性能优化](#前端工程化与性能优化)
- [框架相关知识](#框架相关知识)
- [综合场景设计题](#综合场景设计题)

---

## 浏览器垃圾回收机制专题

### 基础概念题

**题目1：请详细解释JavaScript的垃圾回收机制，包括标记清除算法和引用计数算法的原理及其优缺点。**

**考察知识点：**
- 垃圾回收的基本原理
- 标记清除算法
- 引用计数算法
- 两种算法的优缺点对比

**参考答案要点：**

#### 垃圾回收基本概念

JavaScript是自动垃圾回收的语言，程序运行时不再需要的内存会被自动释放。垃圾回收器的核心任务是找出"死"对象，释放它们占用的内存。

#### 引用计数算法

```javascript
// 引用计数原理
let obj = { a: 1 };  // {a:1} 被obj引用，计数=1
let obj2 = obj;      // 同一个对象被obj2引用，计数=2
obj = null;          // 计数=1
obj2 = null;         // 计数=0 → 可回收
```

**优点：**
- 实现简单
- 立即回收（引用计数为0时即可回收）
- 不需要暂停程序运行太长时间

**缺点：**
- 无法处理循环引用
```javascript
function cycle() {
  let obj1 = {};
  let obj2 = {};
  obj1.ref = obj2;
  obj2.ref = obj1;
  // obj1和obj2互相引用，计数都是1，但实际上已经没有用了
  // 引用计数算法无法回收
}
```
- 需要额外空间存储引用计数
- 每次增减引用都需要操作，性能开销

#### 标记清除算法（主流）

```javascript
// 标记清除两个阶段
// 1. 标记阶段：从根对象开始标记可到达的对象
// 2. 清除阶段：回收未标记的对象
```

**优点：**
- 解决了循环引用问题
- 不需要额外的引用计数空间
- 实现相对简单

**缺点：**
- 会产生内存碎片（清除后内存不连续）
- 全停顿（Stop-The-World）：执行期间需要暂停程序
- 扫描所有对象，时间消耗较大

#### 现代优化方案

- **标记-整理**：标记后整理存活对象到一起，避免碎片
- **分代回收**（V8引擎）
  - 新生代（存活时间短的对象）：使用Scavenge算法（复制算法）
  - 老生代（存活时间长的对象）：使用标记-清除/标记-整理

**评分标准：**
- 能清晰解释两种算法：60分
- 能对比优缺点：80分
- 能提到现代优化方案（如分代回收）：100分

---

**题目2：什么是分代回收？V8引擎是如何实现分代回收的？**

**考察知识点：**
- 分代回收的理论基础
- V8引擎的新生代回收策略
- V8引擎的老生代回收策略
- 晋升条件

**参考答案要点：**

#### 分代回收的理论基础

**弱分代假说（Weak Generational Hypothesis）：**
- 绝大多数对象生命周期很短
- 很少有年老对象引用年轻对象

基于这个假说，V8将堆分成两代：
- **新生代（New Space）**：存放新创建的对象
- **老生代（Old Space）**：存放在新生代存活一定时间的对象

#### 新生代回收（Scavenge算法）

```javascript
// 新生代空间被分成两个相等的区域：
// - From 空间（使用中）
// - To 空间（空闲）

// 回收过程：
// 1. 扫描From空间，标记存活对象
// 2. 复制存活对象到To空间（保证内存连续）
// 3. 清空From空间
// 4. 交换From和To空间
```

**特点：**
- 牺牲空间换时间
- 只复制存活对象（大多数是死对象，效率高）
- 空间利用率50%

#### 对象晋升到老生代的条件

```javascript
// 条件1：经历过一次Scavenge回收
if (age >= 1) {
  // 晋升到老生代
}

// 条件2：To空间使用超过25%
if (toSpaceUsage > 25%) {
  // 直接晋升，避免To空间不足
}
```

#### 老生代回收

**算法：** 标记清除 + 标记整理

```javascript
// 标记阶段（Mark）：从根开始标记存活对象
// 清除阶段（Sweep）：清除未标记对象（产生碎片）
// 整理阶段（Compact）：移动存活对象到一起（避免碎片）

// 优化：增量标记（Incremental Marking）
// - 将标记过程拆分成小步骤
// - 边执行JavaScript边标记
// - 减少单次停顿时间
```

**全停顿优化：**
- 增量标记（Incremental Marking）
- 并行标记（Parallel Marking）
- 惰性清理（Lazy Sweeping）
- 并发标记（Concurrent Marking，V8最新版）

**评分标准：**
- 能解释分代回收的基本概念：60分
- 能详细说明新生代和老生代的回收算法：80分
- 能解释对象晋升条件和优化技术：100分

---

### 实践应用题

**题目3：请列举常见的JavaScript内存泄漏场景，并说明如何检测和预防。**

**考察知识点：**
- 内存泄漏的概念
- 常见内存泄漏场景
- 内存泄漏的检测方法
- 预防内存泄漏的最佳实践

**参考答案要点：**

#### 常见内存泄漏场景

##### 1. 意外的全局变量

```javascript
function bad() {
  // 没有声明，自动变成全局变量
  leak = 'this is global';
  
  // this在非严格模式下指向window
  this.leak2 = 'also global';
}

bad();  // 调用后window.leak和window.leak2都不会回收
```

**解决：** 使用严格模式 `'use strict'`

##### 2. 未清理的定时器和回调

```javascript
// 定时器忘记清理
let timer = setInterval(() => {
  let dom = document.getElementById('element');
  if (dom) {
    // 使用dom
  }
}, 1000);

// 组件销毁时需要
// clearInterval(timer);
```

##### 3. 脱离DOM的引用

```javascript
const elements = {
  button: document.getElementById('button'),
  image: document.getElementById('image')
};

// DOM被删除了，但elements还在引用
document.body.removeChild(elements.button);
// elements.button还在内存中，无法回收
```

##### 4. 闭包引起的泄漏

```javascript
let leakData;
function closure() {
  let bigData = new Array(1000000).fill('*');  // 大数组
  leakData = function() {
    return bigData;  // bigData被闭包引用
  };
}

closure();  // bigData永远不会回收
```

##### 5. 未清理的事件监听器

```javascript
const element = document.getElementById('my-element');
element.addEventListener('click', onClick);

// 移除元素时忘记移除监听器
element.parentNode.removeChild(element);
// 监听器还在，element也不会被回收
```

##### 6. Console.log保留引用

```javascript
const obj = { big: new Array(1000000) };
console.log(obj);  // 浏览器控制台可能保持引用
// 生产环境应该移除console.log
```

##### 7. Map/Set保存对象引用

```javascript
// 使用Map/Set要注意
let map = new Map();
let obj = { data: 'big data' };
map.set(obj, 'info');  // obj被map引用
obj = null;  // 但map还在引用，无法回收

// 解决：使用WeakMap/WeakSet
let weakMap = new WeakMap();
weakMap.set(obj, 'info');  // WeakMap不阻止回收
```

#### 如何检测内存泄漏

**Chrome DevTools Memory面板：**
1. 打开开发者工具 → Memory
2. 选择"Take heap snapshot"
3. 执行操作后再拍快照
4. 对比两次快照，查找异常增长的对象

**Performance面板监控：**
1. 打开Performance
2. 勾选Memory
3. 录制操作过程
4. 观察内存曲线是否持续增长

**Allocation Sampling：**
- 录制一段时间的内存分配
- 查看哪些函数分配了内存

#### 预防内存泄漏的最佳实践

```javascript
// 1. 使用严格模式
'use strict';

// 2. 及时清理资源
function doSomething() {
  let resource = acquireResource();
  try {
    // 使用资源
  } finally {
    resource.release();  // 保证清理
  }
}

// 3. 组件卸载时清理（React/Vue示例）
// React useEffect
useEffect(() => {
  const timer = setInterval(() => {}, 1000);
  return () => clearInterval(timer);  // 清理函数
}, []);

// Vue beforeUnmount
beforeUnmount() {
  clearInterval(this.timer);
  window.removeEventListener('resize', this.handler);
}

// 4. 使用WeakMap/WeakSet管理引用
const cache = new WeakMap();
function setCache(key, value) {
  cache.set(key, value);  // key被回收后自动删除
}

// 5. 使用try-finally确保清理
function withResource(fn) {
  const resource = acquire();
  try {
    return fn(resource);
  } finally {
    resource.release();
  }
}
```

**评分标准：**
- 能列举至少3种常见场景：60分
- 能说明检测方法：80分
- 能给出具体的预防措施：100分

---

## 浏览器渲染原理专题

### 基础概念题

**题目1：请详细描述浏览器从HTML到屏幕显示像素的完整渲染过程。**

**考察知识点：**
- HTML解析与DOM树构建
- CSS解析与CSSOM树构建
- 渲染树（Render Tree）构建
- 布局（Layout/Reflow）
- 绘制（Paint/Repaint）
- 合成（Composite）
- 关键渲染路径（CRP）

**参考答案要点：**

#### 完整渲染流程

```
1. HTML解析 → DOM树
2. CSS解析 → CSSOM树
3. DOM + CSSOM → 渲染树（Render Tree）
4. 布局（Layout）：计算几何位置和尺寸
5. 绘制（Paint）：生成绘制指令
6. 合成（Composite）：将图层合成到屏幕
```

#### 详细步骤说明

##### 1. HTML解析构建DOM树

```javascript
// HTML解析器
// 遇到标签 → 生成DOM节点
// 遇到文本 → 生成文本节点
// 构建树结构

// 示例HTML
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

**注意：**
- HTML解析遇到script会暂停（等待脚本执行）
- 使用async/defer属性可以优化

##### 2. CSS解析构建CSSOM树

```javascript
// CSSOM树包含：
// - 浏览器默认样式（User Agent Stylesheet）
// - 内部样式（<style>标签）
// - 外部样式（<link>标签）
// - 行内样式（style属性）

// 示例CSS
.container { width: 100%; }
h1 { color: red; }
p { font-size: 16px; }
```

##### 3. 合成渲染树

```javascript
// 渲染树只包含需要显示的节点
// - display: none 的节点不在渲染树中
// - visibility: hidden 的节点在渲染树中
// - ::before/::after 伪元素会在渲染树中
```

##### 4. 布局（Layout/Reflow）

```javascript
// 计算每个节点的几何信息
// - 尺寸（width/height）
// - 位置（x/y坐标）
// - 盒模型参数（padding/margin/border）
```

##### 5. 绘制（Paint）

```javascript
// 为每个节点生成绘制指令
// - 绘制背景
// - 绘制边框
// - 绘制文本
// - 绘制阴影
```

##### 6. 分层与合成

```javascript
// 浏览器会创建图层（Layers）提高性能
// - z-index层级会创建独立图层
// - transform/opacity变化会创建独立图层
// - will-change提示浏览器预创建图层
// - video/canvas元素有自己的图层

// 合成阶段
// - GPU加速
// - 图层独立绘制，不影响其他图层
// - transform/opacity只触发合成，不触发布局和绘制
```

#### 关键渲染路径（Critical Rendering Path）

```javascript
// 关键资源：影响首屏渲染的资源
// - HTML（DOM）
// - CSS（CSSOM）
// - JavaScript（可能修改DOM/CSSOM）

// 优化CRP
// - 内联关键CSS
// - 异步非关键CSS
// - 使用media属性区分屏幕CSS
// - 延迟非关键JS加载
```

**评分标准：**
- 能列出主要阶段：60分
- 能详细解释每个阶段做了什么：80分
- 能提到关键渲染路径优化：100分

---

**题目2：请解释重排（Reflow）和重绘（Repaint）的区别，说明哪些操作会触发它们，并列举优化方法。**

**考察知识点：**
- 重排/重绘的定义
- 触发重排/重绘的属性/操作
- 性能影响对比
- 优化方法

**参考答案要点：**

#### 重排（Reflow/Layout）

```javascript
// 定义：元素几何信息变化，需要重新计算布局

// 触发重排的操作
element.style.width = '100px';
element.style.height = '100px';
element.style.margin = '10px';
element.style.padding = '10px';
element.style.border = '1px solid';
element.style.display = 'block';
element.style.position = 'absolute';
element.style.left = '10px';

// 读取布局属性也会触发
const width = element.offsetWidth;
const height = element.offsetHeight;
const top = element.offsetTop;
const left = element.offsetLeft;
const clientWidth = element.clientWidth;
const scrollWidth = element.scrollWidth;
```

#### 重绘（Repaint/Paint）

```javascript
// 定义：样式变化但布局不变，只需要重新绘制

// 触发重绘的属性
element.style.color = 'red';
element.style.background = '#fff';
element.style.boxShadow = '1px 1px 5px rgba(0,0,0,0.5)';
element.style.borderColor = 'blue';
element.style.visibility = 'hidden';
```

#### 两者关系

```javascript
// 重排一定触发重绘
// 重绘不一定触发重排

// 性能影响：重排 > 重绘 > 合成
```

#### 优化方法

##### 1. 批量修改DOM

```javascript
// 不好：多次修改，多次重排
element.style.width = '100px';
element.style.height = '100px';
element.style.margin = '10px';

// 好：一次修改
element.style.cssText = 'width: 100px; height: 100px; margin: 10px;';

// 更好：使用class
element.className = 'box';

// 最好：使用DocumentFragment
const fragment = document.createDocumentFragment();
for (let i = 0; i < 100; i++) {
  const div = document.createElement('div');
  fragment.appendChild(div);
}
document.body.appendChild(fragment);  // 只触发一次重排
```

##### 2. 先隐藏再修改

```javascript
// 先隐藏
element.style.display = 'none';  // 触发一次重排

// 修改
element.style.width = '100px';
element.style.height = '100px';
element.style.color = 'red';

// 恢复显示
element.style.display = 'block';  // 触发一次重排

// 总共只触发2次重排
```

##### 3. 缓存布局属性

```javascript
// 不好：每次读取都会触发重排
for (let i = 0; i < 100; i++) {
  el.style.left = el.offsetWidth + i + 'px';
  el.style.top = el.offsetHeight + i + 'px';
}

// 好：先缓存
const width = el.offsetWidth;
const height = el.offsetHeight;
for (let i = 0; i < 100; i++) {
  el.style.left = width + i + 'px';
  el.style.top = height + i + 'px';
}
```

##### 4. 使用transform代替布局属性

```javascript
// 不好：修改left会触发重排
element.style.left = '100px';

// 好：transform只触发合成
element.style.transform = 'translateX(100px)';

// 同样适用于
element.style.transform = 'scale(1.5)';
element.style.transform = 'rotate(45deg)';
element.style.opacity = '0.5';  // opacity也只触发合成
```

##### 5. 使用CSS动画代替JavaScript动画

```css
/* CSS动画比JS动画性能更好 */
@keyframes slide {
  from { transform: translateX(0); }
  to { transform: translateX(100px); }
}

.box {
  animation: slide 1s ease;
}
```

##### 6. 使用requestAnimationFrame优化动画

```javascript
function animate() {
  // 在浏览器下次重绘前执行
  element.style.transform = `translateX(${x}px)`;
  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);
```

##### 7. 使用will-change提示浏览器

```css
/* 提示浏览器该元素会有transform变化，提前创建图层 */
.box {
  will-change: transform;
}
```

**评分标准：**
- 能区分重排和重绘：60分
- 能列举触发的属性/操作：80分
- 能详细说明多种优化方法：100分

---

## JavaScript核心知识点

### 执行上下文与作用域

**题目1：请详细解释JavaScript的执行上下文和作用域链的工作原理。**

**考察知识点：**
- 执行上下文的概念
- 全局执行上下文
- 函数执行上下文
- 调用栈
- 作用域链
- 变量提升（Hoisting）
- 暂时性死区（TDZ）

**参考答案要点：**

#### 执行上下文

```javascript
// JavaScript引擎执行代码前会创建执行上下文
// 分为：
// 1. 全局执行上下文（Global Execution Context）
// 2. 函数执行上下文（Function Execution Context）
// 3. eval执行上下文（不推荐使用）

// 每个执行上下文包含：
// - 变量对象（VO）：var、function声明
// - 作用域链（Scope Chain）
// - this指向
```

#### 执行上下文创建阶段（Creation Phase）

```javascript
// 1. 创建变量对象
//    - 创建arguments对象（函数执行上下文）
//    - 函数声明提升
//    - 变量声明提升（初始化为undefined）

// 2. 创建作用域链
// 3. 确定this指向

// 变量提升示例
console.log(a);  // undefined（变量提升）
console.log(foo);  // [Function: foo]（函数提升优先）

var a = 10;
function foo() {
  console.log('foo');
}

// 相当于
function foo() {
  console.log('foo');
}
var a;
console.log(a);
console.log(foo);
a = 10;
```

#### 执行上下文执行阶段（Execution Phase）

```javascript
// 1. 变量赋值
// 2. 函数调用
// 3. 执行其他代码
```

#### 调用栈（Call Stack）

```javascript
function first() {
  second();
}

function second() {
  third();
}

function third() {
  console.log('third');
}

first();

// 调用栈变化：
// [global]
// [global, first]
// [global, first, second]
// [global, first, second, third]
// [global, first, second]
// [global, first]
// [global]
```

#### 作用域链

```javascript
let globalVar = 'global';

function outer() {
  let outerVar = 'outer';
  
  function inner() {
    let innerVar = 'inner';
    console.log(globalVar);  // 从作用域链查找
    console.log(outerVar);
    console.log(innerVar);
  }
  
  inner();
}

outer();

// inner的作用域链：
// inner Scope -> outer Scope -> global Scope
```

#### 暂时性死区（TDZ）

```javascript
console.log(x);  // ReferenceError: Cannot access 'x' before initialization
console.log(y);  // undefined
let x = 10;
var y = 20;

// TDZ区域：从块级作用域开始到变量声明
{
  // 这里是x的TDZ
  // console.log(x); // ReferenceError
  let x = 10;
  console.log(x); // 10
}
```

**评分标准：**
- 能解释执行上下文和调用栈：60分
- 能解释作用域链和变量提升：80分
- 能提到暂时性死区和let/const特性：100分

---

### 闭包

**题目2：请解释闭包的原理、形成条件以及实际应用场景。**

**考察知识点：**
- 闭包的定义
- 闭包形成的条件
- 闭包的原理
- 闭包的优缺点
- 闭包的应用场景

**参考答案要点：**

#### 闭包定义

```javascript
// 当一个函数能够记住并访问它的词法作用域
// 即使该函数在其词法作用域之外执行时
// 就产生了闭包

function outer() {
  let count = 0;  // 变量在outer作用域
  return function inner() {
    count++;
    console.log(count);
  };
}

const fn = outer();
fn();  // 1 - outer执行完了，但count仍然存活
fn();  // 2 - 闭包使count保留
fn();  // 3
```

#### 闭包形成条件

```javascript
1. 函数嵌套函数
2. 内部函数引用外部函数的变量
3. 内部函数被外部返回或被外部引用
```

#### 闭包原理

```javascript
// 当inner函数被返回时
// inner函数的作用域链仍然保留对outer作用域的引用
// 所以outer作用域的变量不会被垃圾回收

// 作用域链
// inner -> outer -> global
```

#### 闭包应用场景

##### 1. 数据封装/私有变量

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
console.log(counter.count);  // undefined - 无法直接访问
```

##### 2. 函数柯里化

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

##### 3. 模块模式

```javascript
const Module = (function() {
  let privateVar = 'private';
  
  function privateMethod() {
    console.log('This is private');
  }
  
  return {
    publicMethod() {
      privateMethod();
    },
    setPrivateData(newValue) {
      privateVar = newValue;
    }
  };
})();

Module.publicMethod();
```

##### 4. 事件处理与回调

```javascript
for (let i = 0; i < 5; i++) {
  document.getElementById('btn-' + i).addEventListener('click', () => {
    console.log('Click button ' + i);  // i被闭包保存
  });
}
```

#### 闭包注意事项

##### 内存泄漏

```javascript
function leakMemory() {
  let bigData = new Array(1000000);  // 大数组
  return function() {
    return bigData;  // bigData被闭包引用，无法回收
  };
}

// 解决：及时释放引用
const fn = leakMemory();
// 使用完后
fn = null;  // 释放引用
```

##### 经典for循环面试题

```javascript
// 问题
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

// 解法2：IIFE
for (var i = 0; i < 5; i++) {
  (function(j) {
    setTimeout(() => console.log(j), 1000);
  })(i);
}
```

**评分标准：**
- 能解释闭包定义和形成条件：60分
- 能说明闭包原理：80分
- 能列举多个应用场景并说明注意事项：100分

---

### 原型与原型链

**题目3：请详细解释JavaScript的原型和原型链，以及如何通过原型实现继承。**

**考察知识点：**
- 原型的概念
- `prototype`属性
- `__proto__`属性
- 原型链结构
- 属性查找规则
- 继承的实现方式

**参考答案要点：**

#### 原型基本概念

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

#### 原型链

```javascript
// 原型链结构
person.__proto__ === Person.prototype;
Person.prototype.__proto__ === Object.prototype;
Object.prototype.__proto__ === null;  // 原型链终点

// 完整链
// person -> Person.prototype -> Object.prototype -> null
```

#### 属性查找规则

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

#### 继承的实现方式

##### 方式1：原型链继承

```javascript
function Animal(name) {
  this.name = name;
  this.colors = ['red', 'blue'];
}
Animal.prototype.sayName = function() {
  console.log(this.name);
};

function Dog(breed) {
  this.breed = breed;
}
Dog.prototype = new Animal('Dog');  // 原型链继承
Dog.prototype.constructor = Dog;  // 修正构造函数

const dog1 = new Dog('Golden');
const dog2 = new Dog('Lab');
dog1.colors.push('green');  // 问题：共享引用类型
console.log(dog2.colors);  // ['red', 'blue', 'green'] - 受到影响

// 缺点：
// 1. 无法给父构造函数传参
// 2. 所有实例共享父属性（引用类型）
```

##### 方式2：构造函数继承

```javascript
function Animal(name) {
  this.name = name;
  this.colors = ['red', 'blue'];
}

function Dog(name, breed) {
  Animal.call(this, name);  // 调用父构造函数
  this.breed = breed;
}

const dog1 = new Dog('Fido', 'Golden');
const dog2 = new Dog('Buddy', 'Lab');
dog1.colors.push('green');
console.log(dog2.colors);  // ['red', 'blue'] - 不共享

// 优点：
// 1. 可以传参
// 2. 不共享父属性
// 3. 避免引用类型问题

// 缺点：
// 1. 无法继承父原型方法
// 2. 每个实例都有父构造函数副本
```

##### 方式3：组合继承（原型链 + 构造函数）

```javascript
function Animal(name) {
  this.name = name;
  this.colors = ['red', 'blue'];
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

const dog1 = new Dog('Fido', 'Golden');
const dog2 = new Dog('Buddy', 'Lab');
dog1.colors.push('green');
console.log(dog2.colors);  // ['red', 'blue']
dog1.sayName();  // Fido

// 优点：
// 1. 可以传参
// 2. 不共享父属性
// 3. 继承父原型方法

// 缺点：
// 1. 父构造函数被调用两次
```

##### 方式4：寄生组合继承（最完美）

```javascript
function Animal(name) {
  this.name = name;
  this.colors = ['red', 'blue'];
}
Animal.prototype.sayName = function() {
  console.log(this.name);
};

function Dog(name, breed) {
  Animal.call(this, name);
  this.breed = breed;
}

// 原型式继承
function inheritPrototype(child, parent) {
  function F() {}
  F.prototype = parent.prototype;
  child.prototype = new F();
  child.prototype.constructor = child;
}

inheritPrototype(Dog, Animal);

const dog1 = new Dog('Fido', 'Golden');
const dog2 = new Dog('Buddy', 'Lab');
dog1.colors.push('green');
console.log(dog2.colors);  // ['red', 'blue']
dog1.sayName();  // Fido

// 优点：
// 1. 父构造函数只调用一次
// 2. 不共享父属性
// 3. 继承父原型方法
// 4. 效率最高
```

##### 方式5：ES6 class继承（语法糖）

```javascript
class Animal {
  constructor(name) {
    this.name = name;
    this.colors = ['red', 'blue'];
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

// 注意：
// - 本质还是基于原型的继承
// - 语法更清晰、易懂
```

**评分标准：**
- 能解释原型和原型链的基本概念：60分
- 能说明属性查找规则：80分
- 能详细说明多种继承方式及其优缺点：100分

---

### 异步编程

**题目4：请对比JavaScript异步编程的几种方案：Callback、Promise、Generator、Async/Await，说明它们的原理和优缺点。**

**考察知识点：**
- 回调函数
- Promise原理与API
- Generator函数
- Async/Await语法
- 各方案对比

**参考答案要点：**

#### 回调函数（Callback）

```javascript
// 基本用法
function loadData(url, callback) {
  // 异步操作
  setTimeout(() => {
    callback('data from ' + url);
  }, 1000);
}

loadData('api/data', (data) => {
  console.log(data);
});

// 回调地狱
loadData('url1', (data1) => {
  loadData(data1.url, (data2) => {
    loadData(data2.url, (data3) => {
      loadData(data3.url, (data4) => {
        // 嵌套太深，难以维护
      });
    });
  });
});

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

**优点：**
- 简单易懂
- 兼容性好

**缺点：**
- 回调地狱
- 错误处理困难
- 难以控制执行流程

---

#### Promise

```javascript
// Promise状态：pending → fulfilled/rejected，一旦改变不可逆转

function asyncTask() {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      resolve('success');
      // reject('error');
    }, 1000);
  });
}

// 链式调用
asyncTask()
  .then(data => {
    console.log(data);
    return processData(data);
  })
  .then(result => {
    console.log(result);
    return saveResult(result);
  })
  .catch(error => {
    console.error(error);
  });

// Promise静态方法
Promise.all([p1, p2, p3]);  // 全部成功才成功，一个失败就失败
Promise.allSettled([p1, p2, p3]);  // 等待所有完成
Promise.race([p1, p2, p3]);  // 竞速，取第一个完成的
Promise.any([p1, p2, p3]);  // 取第一个成功的
Promise.resolve(1);  // 包装为fulfilled的Promise
Promise.reject(new Error());  // 包装为rejected的Promise
```

**优点：**
- 链式调用，避免回调地狱
- 统一的错误处理
- 丰富的组合方法

**缺点：**
- 有一定学习成本
- 不能取消
- 代码流程不够直观

---

#### Generator

```javascript
function* gen() {
  const data1 = yield fetch('/api/data1');
  const data2 = yield fetch('/api/data2');
  return { data1, data2 };
}

// 手动执行
const g = gen();
console.log(g.next());  // { value: Promise1, done: false }
console.log(g.next(data1));  // { value: Promise2, done: false }
console.log(g.next(data2));  // { value: {data1, data2}, done: true }

// 自动执行器
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

**优点：**
- 可以暂停执行
- 可以控制执行流程
- 更灵活的异步控制

**缺点：**
- 需要手动或配合自动执行器
- 学习曲线陡峭
- 代码可读性不如async/await

---

#### Async/Await（推荐）

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

// async函数总是返回Promise
async function foo() {
  return 123;
}
foo().then(data => console.log(data));  // 123

// await后面可以不是Promise
async function bar() {
  const result = await 'hello';  // 自动包装为Promise
  console.log(result);  // 'hello'
}
```

**优点：**
- 写法像同步代码，最优雅
- 错误处理简单（try/catch）
- 可读性最好
- 支持try/catch错误处理

**缺点：**
- 需要ES7支持
- await会阻塞后续代码执行（可以用Promise.all并发）

#### 方案对比总结

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| Callback | 简单易懂 | 回调地狱、错误处理困难 | ❌ |
| Promise | 链式调用、好处理错误 | 有学习成本 | ⭐⭐ |
| Generator | 可以暂停执行 | 需要手动执行、复杂 | ⭐ |
| Async/Await | 写法像同步、最佳方案 | 需要ES7支持 | ⭐⭐⭐⭐⭐ |

**评分标准：**
- 能说明各方案基本用法：60分
- 能对比各方案优缺点：80分
- 能详细解释Promise和async/await的原理：100分

---

### 事件循环机制

**题目5：请详细解释JavaScript的事件循环（Event Loop）机制，包括宏任务、微任务，以及它们的执行顺序。**

**考察知识点：**
- JavaScript单线程特性
- 事件循环原理
- 调用栈
- 任务队列
- 宏任务（Macro Task）
- 微任务（Micro Task）
- 执行顺序
- 浏览器渲染时机

**参考答案要点：**

#### 为什么JavaScript是单线程的

```javascript
// JavaScript是单线程的，为什么？
// - 主要用于处理DOM，多线程会有同步问题
// - 单线程简单、容易理解
// - 通过Event Loop实现异步
```

#### 事件循环核心组件

```
┌─────────────────────────────────────────────────┐
│                Event Loop                        │
├─────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────────────┐  │
│  │   Call Stack │    │   Task Queues        │  │
│  │  (调用栈)    │    │                      │  │
│  └──────────────┘    │  ┌────────────────┐ │  │
│         │            │  │  Micro Tasks   │ │  │
│         │            │  │ - Promise.then │ │  │
│         │            │  │ - queueMicrotask│ │  │
│         │            │  └────────────────┘ │  │
│         │            │  ┌────────────────┐ │  │
│         │            │  │  Macro Tasks   │ │  │
│         │            │  │ - setTimeout  │ │  │
│         │            │  │ - setInterval │ │  │
│         │            │  │ - setImmediate│ │  │
│         │            │  │ - I/O         │ │  │
│         │            │  └────────────────┘ │  │
│         ▼            └──────────────────────┘  │
│  ┌────────────────────────────────────────┐   │
│  │         Web APIs                       │   │
│  │ - DOM Events                          │   │
│  │ - timer                               │   │
│  │ - fetch                               │   │
│  │ - AJAX                                │   │
│  └────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

#### 宏任务（Macro Task）

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

#### 微任务（Micro Task）

```javascript
// 常见微任务
Promise.resolve().then(() => {
  console.log('Promise then');
});

// async/await中的await
async function foo() {
  await bar();  // await后面的代码作为微任务
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

// process.nextTick（Node.js）
```

#### 事件循环执行顺序

```javascript
// 完整执行顺序
1. 执行同步代码（调用栈清空）
2. 清空微任务队列（全部执行完）
3. 执行浏览器渲染（如果需要）
4. 从宏任务队列取一个执行
5. 回到步骤2，循环往复

// 注意：
// - 每次宏任务执行完都会清空微任务队列
// - 渲染发生在微任务清空后、宏任务执行前
```

#### 经典面试题示例

##### 题目1

```javascript
console.log(1);

setTimeout(() => console.log(2), 0);

Promise.resolve().then(() => console.log(3));

console.log(4);

// 答案：1, 4, 3, 2

// 解析：
// 1. 同步代码：console.log(1) → 输出1
// 2. setTimeout → 宏任务队列
// 3. Promise.then → 微任务队列
// 4. 同步代码：console.log(4) → 输出4
// 5. 清空微任务：Promise.then → 输出3
// 6. 宏任务：setTimeout → 输出2
```

##### 题目2

```javascript
console.log('script start');

setTimeout(() => {
  console.log('setTimeout');
}, 0);

Promise.resolve()
  .then(() => {
    console.log('promise1');
  })
  .then(() => {
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

##### 题目3（async/await版本）

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

// 答案：
// script start
// async1 start
// async2
// promise1
// script end
// async1 end
// promise2
// setTimeout

// 解析：
// 1. script start（同步）
// 2. setTimeout → 宏任务
// 3. async1() → async1 start（同步）
// 4. await async2() → async2（同步），然后 async1 end 作为微任务
// 5. new Promise → promise1（同步），then 作为微任务
// 6. script end（同步）
// 7. 清空微任务：async1 end, promise2
// 8. 宏任务：setTimeout
```

#### Node.js vs 浏览器的区别

```javascript
// 浏览器
// - 微任务：Promise.then, queueMicrotask, MutationObserver
// - 宏任务：setTimeout, setInterval, requestAnimationFrame, I/O

// Node.js
// - 微任务：Promise.then, queueMicrotask, process.nextTick
// - 宏任务：setTimeout, setInterval, setImmediate, I/O

// Node.js的事件循环有多个阶段：
// 1. Timers（setTimeout/setInterval）
// 2. Pending callbacks
// 3. Idle/Prepare
// 4. Poll（I/O）
// 5. Check（setImmediate）
// 6. Close callbacks
```

**评分标准：**
- 能解释事件循环基本概念：60分
- 能区分宏任务和微任务并说明执行顺序：80分
- 能正确分析复杂的执行顺序问题：100分

---

### 模块化

**题目6：请对比JavaScript的模块化方案：CommonJS、ES Modules（ESM）、AMD、CMD，说明它们的区别和使用场景。**

**考察知识点：**
- CommonJS
- ES Modules
- AMD
- CMD
- 区别对比
- 使用场景

**参考答案要点：**

#### CommonJS

```javascript
// 语法
// 导出
const foo = 'foo';
function bar() {}
module.exports = { foo, bar };

// 或者
exports.foo = 'foo';
exports.bar = function() {};

// 导入
const { foo, bar } = require('./module');
const module = require('./module');

// 特点
// - Node.js默认模块系统
// - 同步加载
// - 运行时加载
// - 导出的是值的拷贝
// - 不能在浏览器直接使用（需要打包）
```

#### ES Modules（ESM）

```javascript
// 语法
// 导出
export const foo = 'foo';
export function bar() {}

// 默认导出
export default function() {}

// 导入
import { foo, bar } from './module.js';
import module from './module.js';
import * as all from './module.js';

// 动态导入
import('./module.js').then(module => {
  console.log(module);
});

// 特点
// - 浏览器原生支持（需要type="module"）
// - Node.js也支持（.mjs或package.json"type": "module"）
// - 静态加载（编译时）
// - 支持Tree Shaking
// - 导入的是值的引用
// - 必须使用完整路径
```

#### AMD（Asynchronous Module Definition）

```javascript
// Require.js是代表实现
// 语法
define(['module1', 'module2'], function(module1, module2) {
  // 依赖前置
  function foo() {
    module1.doSomething();
  }
  return { foo };
});

// 特点
// - 异步加载
// - 依赖前置
// - 浏览器端使用
// - 现在很少使用了
```

#### CMD（Common Module Definition）

```javascript
// Sea.js是代表实现
// 语法
define(function(require, exports, module) {
  // 就近依赖
  const module1 = require('./module1');
  function foo() {
    module1.doSomething();
  }
  module.exports = { foo };
});

// 特点
// - 异步加载
// - 依赖就近（需要时才加载）
// - 浏览器端使用
// - 现在很少使用了
```

#### 方案对比

| 特性 | CommonJS | ES Modules | AMD | CMD |
|------|----------|------------|-----|-----|
| 加载方式 | 同步 | 静态（编译时）+ 动态 | 异步 | 异步 |
| 使用环境 | Node.js | 浏览器+Node.js | 浏览器 | 浏览器 |
| 语法 | require/exports | import/export | define/require | define/require |
| Tree Shaking | 不支持 | 支持 | 不支持 | 不支持 |
| 导出值 | 值拷贝 | 引用 | 值 | 值 |
| 流行度 | 高 | 最高 | 低 | 低 |

#### 使用建议

```javascript
// 新项目推荐：ES Modules
// - 原生支持
// - Tree Shaking友好
// - 统一前后端

// Node.js旧项目：CommonJS
// - 兼容性好
// - 生态成熟

// 浏览器打包工具：ES Modules
// - Webpack/Rollup/Vite都推荐ESM
```

**评分标准：**
- 能说明CommonJS和ES Modules的基本用法：60分
- 能对比CommonJS和ES Modules的区别：80分
- 能了解其他方案并给出使用建议：100分

---

### 函数式编程

**题目7：请解释JavaScript函数式编程的概念、特点，列举常用的函数式编程方法和应用场景。**

**考察知识点：**
- 函数式编程概念
- 纯函数
- 不可变数据
- 函数柯里化
- 函数组合
- 高阶函数
- 应用场景

**参考答案要点：**

#### 函数式编程核心概念

```javascript
// 函数式编程（Functional Programming）是一种编程范式
// 强调用函数来表达计算

// 核心特点：
// 1. 纯函数（Pure Function）
// 2. 不可变数据（Immutability）
// 3. 函数是一等公民（First-class）
// 4. 函数组合（Composition）
// 5. 避免副作用（Side Effects）
// 6. 声明式编程（Declarative）
```

#### 纯函数

```javascript
// 定义：
// 1. 相同的输入总是返回相同的输出
// 2. 没有副作用

// 纯函数示例
function sum(a, b) {
  return a + b;
}

// 不纯的函数示例
let counter = 0;
function increment() {
  counter++;  // 副作用：修改外部变量
  return counter;
}

// 不纯的函数示例
function getDate() {
  return new Date();  // 依赖外部状态
}

// 不纯的函数示例
function push(arr, item) {
  arr.push(item);  // 副作用：修改参数
  return arr;
}
```

#### 不可变数据

```javascript
// 原数组
const arr = [1, 2, 3];

// 不好：修改原数组
arr.push(4);  // arr变为 [1,2,3,4]

// 好：创建新数组
const newArr = [...arr, 4];  // arr不变，newArr是 [1,2,3,4]

// 对象同理
const obj = { a: 1, b: 2 };

// 不好：修改原对象
obj.c = 3;

// 好：创建新对象
const newObj = { ...obj, c: 3 };

// 使用Immer简化
import { produce } from 'immer';

const newState = produce(state, draft => {
  draft.a = 2;  // 直接修改draft，但返回的是新state
});
```

#### 高阶函数

```javascript
// 定义：接收函数作为参数，或返回函数的函数

// 示例1：接收函数作为参数
function map(arr, fn) {
  const result = [];
  for (let i = 0; i < arr.length; i++) {
    result.push(fn(arr[i]));
  }
  return result;
}

const arr = [1, 2, 3];
const doubled = map(arr, x => x * 2);  // [2,4,6]

// 示例2：返回函数
function createMultiplier(factor) {
  return function(x) {
    return x * factor;
  };
}

const double = createMultiplier(2);
const triple = createMultiplier(3);
double(5);  // 10
triple(5);  // 15
```

#### 函数柯里化

```javascript
// 定义：将多参数函数转为一系列单参数函数

// 普通函数
function add(a, b) {
  return a + b;
}

// 柯里化
function curriedAdd(a) {
  return function(b) {
    return a + b;
  };
}

// 使用
curriedAdd(1)(2);  // 3

// 更通用的柯里化函数
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

// 使用
const add = curry((a, b, c) => a + b + c);
add(1)(2)(3);  // 6
add(1, 2)(3);  // 6
add(1)(2, 3);  // 6
add(1, 2, 3);  // 6
```

#### 函数组合

```javascript
// 定义：将多个函数组合成一个新函数

// 普通写法
function toUpper(str) {
  return str.toUpperCase();
}
function trim(str) {
  return str.trim();
}
function reverse(str) {
  return str.split('').reverse().join('');
}

const result = reverse(toUpper(trim('  hello  ')));  // 'OLLEH'

// 组合写法
function compose(...fns) {
  return function(x) {
    return fns.reduceRight((acc, fn) => fn(acc), x);
  };
}

const process = compose(reverse, toUpper, trim);
const result = process('  hello  ');  // 'OLLEH'

// pipe函数（从左到右执行）
function pipe(...fns) {
  return function(x) {
    return fns.reduce((acc, fn) => fn(acc), x);
  };
}

const process = pipe(trim, toUpper, reverse);
```

#### 函数式编程常用方法

```javascript
// map - 转换数组元素
[1, 2, 3].map(x => x * 2);  // [2,4,6]

// filter - 过滤数组
[1, 2, 3, 4, 5].filter(x => x % 2 === 0);  // [2,4]

// reduce - 累积计算
[1, 2, 3, 4, 5].reduce((sum, x) => sum + x, 0);  // 15

// 链式调用
[1, 2, 3, 4, 5]
  .filter(x => x % 2 === 0)
  .map(x => x * 2)
  .reduce((sum, x) => sum + x, 0);  // 12
```

#### 函数式编程的优点

```javascript
// 1. 可预测性（纯函数）
// 2. 可测试性（纯函数容易测试）
// 3. 代码复用性（高阶函数）
// 4. 可维护性（声明式代码更易读）
// 5. 并发友好（不可变数据）
```

**评分标准：**
- 能解释函数式编程基本概念和特点：60分
- 能说明纯函数和不可变数据：80分
- 能列举高阶函数、柯里化、函数组合等方法：100分

---

### TypeScript

**题目8：请介绍TypeScript的核心特性、类型系统的主要概念，以及它与JavaScript的区别。**

**考察知识点：**
- TypeScript基本概念
- 类型注解
- 接口/类型别名
- 泛型
- 类型守卫
- TS与JS区别

**参考答案要点：**

#### TypeScript基本概念

```typescript
// TypeScript是JavaScript的超集
// - 增加了类型系统
// - 最终编译成JavaScript
// - 任何合法的JavaScript都是合法的TypeScript

// 简单示例
function greet(name: string): string {
  return `Hello, ${name}!`;
}

greet('TypeScript');  // 正常
greet(123);  // 编译时错误
```

#### 类型注解

```typescript
// 基本类型
let name: string = 'Alice';
let age: number = 30;
let isStudent: boolean = false;
let nothing: null = null;
let notDefined: undefined = undefined;
let anything: any = 'anything';  // 尽量避免
let unknown: unknown = 'unknown';  // 比any安全

// 数组
let numbers: number[] = [1, 2, 3];
let names: Array<string> = ['a', 'b', 'c'];

// 元组
let tuple: [string, number] = ['hello', 10];

// 函数
function add(a: number, b: number): number {
  return a + b;
}

// 箭头函数
const add = (a: number, b: number): number => a + b;

// 返回void
function log(message: string): void {
  console.log(message);
}
```

#### 接口（Interface）

```typescript
// 定义对象类型
interface User {
  id: number;
  name: string;
  age?: number;  // 可选属性
  readonly email: string;  // 只读属性
}

const user: User = {
  id: 1,
  name: 'Alice',
  email: 'alice@example.com'
};

// 函数接口
interface Add {
  (a: number, b: number): number;
}

const add: Add = (a, b) => a + b;

// 类接口
interface IAnimal {
  name: string;
  makeSound(): void;
}

class Dog implements IAnimal {
  name: string;
  constructor(name: string) {
    this.name = name;
  }
  makeSound() {
    console.log('Woof!');
  }
}
```

#### 类型别名（Type）

```typescript
// 定义类型
type ID = number | string;
type User = {
  id: ID;
  name: string;
};

// 联合类型
type Status = 'pending' | 'approved' | 'rejected';
let status: Status = 'pending';  // 只能是这三个值之一

// 交叉类型
type Person = { name: string; age: number };
type Employee = { id: number; department: string };
type Worker = Person & Employee;

const worker: Worker = {
  name: 'Alice',
  age: 30,
  id: 1,
  department: 'IT'
};
```

#### 泛型

```typescript
// 泛型函数
function identity<T>(arg: T): T {
  return arg;
}

identity<string>('hello');
identity(123);  // 类型推断

// 泛型接口
interface Box<T> {
  value: T;
}

const box: Box<string> = { value: 'hello' };

// 泛型类
class Stack<T> {
  private items: T[] = [];
  push(item: T) {
    this.items.push(item);
  }
  pop(): T | undefined {
    return this.items.pop();
  }
}

// 泛型约束
interface Lengthwise {
  length: number;
}

function logLength<T extends Lengthwise>(arg: T): void {
  console.log(arg.length);
}
```

#### 类型守卫

```typescript
// typeof类型守卫
function processValue(value: string | number) {
  if (typeof value === 'string') {
    // value在这里是string类型
    console.log(value.toUpperCase());
  } else {
    // value在这里是number类型
    console.log(value.toFixed(2));
  }
}

// instanceof类型守卫
class Cat { meow() {} }
class Dog { bark() {} }

function makeSound(animal: Cat | Dog) {
  if (animal instanceof Cat) {
    animal.meow();
  } else {
    animal.bark();
  }
}

// 自定义类型守卫
interface User {
  id: number;
  name: string;
}

interface Product {
  id: number;
  title: string;
}

function isUser(item: User | Product): item is User {
  return 'name' in item;
}

function processItem(item: User | Product) {
  if (isUser(item)) {
    console.log(item.name);
  } else {
    console.log(item.title);
  }
}
```

#### TypeScript vs JavaScript

| 特性 | TypeScript | JavaScript |
|------|------------|------------|
| 类型系统 | 有 | 无 |
| 编译 | 需要编译成JS | 不需要，直接运行 |
| 类型检查 | 编译时 | 运行时 |
| 接口/泛型 | 支持 | 不支持 |
| IDE支持 | 更好的智能提示 | 相对较弱 |
| 学习曲线 | 稍高 | 较低 |
| 生态 | 需要类型定义 | 原生支持所有库 |

**评分标准：**
- 能解释TypeScript基本概念：60分
- 能说明主要类型系统特性：80分
- 能对比TS与JS区别并说明使用场景：100分

---

## 前端工程化与性能优化

### 构建工具

**题目1：请对比Webpack和Vite的工作原理和优缺点，说明它们的适用场景。**

**考察知识点：**
- Webpack工作原理
- Vite工作原理
- 两者对比
- 适用场景

**参考答案要点：**

#### Webpack工作原理

```javascript
// Webpack核心概念
// 1. Entry：入口文件
// 2. Output：输出
// 3. Loader：处理非JS文件
// 4. Plugin：执行更广泛的任务
// 5. Module：模块
// 6. Chunk：代码块
// 7. Bundle：最终输出文件

// 工作流程
// 1. 解析依赖图
// 2. 加载所有模块
// 3. 处理模块（Loader）
// 4. 转换模块
// 5. 生成Chunk
// 6. 输出文件

// 特点
// - 全量打包构建
// - 开发环境需要先打包再运行
// - 热更新需要重新构建变化的模块
// - 生产环境打包优化成熟
```

#### Vite工作原理

```javascript
// Vite开发服务器
// - 基于ES Modules
// - 不需要打包，直接使用浏览器原生模块系统
// - 按需编译（只有请求的模块才编译）
// - 冷启动快

// Vite构建
// - 使用Rollup进行打包
// - 类似Webpack的生产构建

// 核心特点
// 1. 开发服务器快
// 2. HMR极快
// 3. 原生ESM支持
// 4. 开箱即用（TypeScript、CSS预处理等）

// 依赖预构建
// - 将CommonJS/UMD模块转换为ESM
// - 缓存起来，避免重复处理
```

#### Webpack vs Vite对比

| 特性 | Webpack | Vite |
|------|---------|------|
| 开发启动速度 | 较慢（需要全量打包） | 快（按需编译） |
| HMR速度 | 一般 | 快 |
| 构建工具 | Webpack自己 | Rollup |
| 生态 | 非常成熟 | 快速发展 |
| 配置复杂度 | 高 | 低（开箱即用） |
| 浏览器兼容性 | 好 | 需要ES6+支持 |
| 适用项目 | 大型复杂项目 | 新项目/中小型项目 |

#### 适用场景

```javascript
// Webpack更适合：
// - 大型复杂项目
// - 需要精细的打包控制
// - 需要兼容旧浏览器
// - 特殊的构建需求

// Vite更适合：
// - 新项目
// - 中小型项目
// - 追求开发体验
// - Vue/React/Svelte等现代框架
// - 不需要复杂的打包配置
```

**评分标准：**
- 能解释两者基本工作原理：60分
- 能对比优缺点：80分
- 能说明适用场景：100分

---

### 代码分割与懒加载

**题目2：请解释代码分割（Code Splitting）和懒加载（Lazy Loading）的概念，说明如何在项目中实现。**

**考察知识点：**
- 代码分割概念
- 为什么需要代码分割
- 实现方式
- 动态导入
- 路由懒加载
- 组件懒加载

**参考答案要点：**

#### 代码分割概念

```javascript
// 将代码分成多个bundle，按需加载
// 避免加载过大的单个bundle
// 提高首屏加载速度

// 问题：单bundle过大
// - 首屏加载时间长
// - 很多未使用的代码

// 解决：代码分割
// - 首屏只加载必需的代码
// - 其他代码按需加载
```

#### 实现方式

##### 1. 动态导入（Dynamic Import）

```javascript
// Webpack/Vite自动分割
button.addEventListener('click', async () => {
  const module = await import('./heavy-module.js');
