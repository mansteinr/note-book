# JavaScript for 循环内存管理最佳实践

---

## 目录

1. [问题背景与内存泄漏风险](#1-问题背景与内存泄漏风险)
2. [变量声明规范](#2-变量声明规范)
3. [块级作用域的正确使用](#3-块级作用域的正确使用)
4. [循环中的闭包陷阱与解决方案](#4-循环中的闭包陷阱与解决方案)
5. [IIFE 在循环中的应用](#5-iife-在循环中的应用)
6. [内存泄漏检测与测试方法](#6-内存泄漏检测与测试方法)
7. [编码规范与质量标准](#7-编码规范与质量标准)
8. [综合案例与最佳实践模板](#8-综合案例与最佳实践模板)

---

## 1. 问题背景与内存泄漏风险

### 1.1 核心问题

在 JavaScript 的 `for` 循环中，不当的变量声明和使用方式会导致以下问题：

| 问题类型 | 具体表现 | 严重程度 |
|----------|----------|----------|
| **全局变量泄漏** | 未声明变量或 `var` 声明提升导致变量挂载到 `window` | 高 |
| **闭包内存泄漏** | 循环中创建闭包，意外持有大对象引用 | 高 |
| **变量污染** | `var` 无块级作用域，循环变量污染外层作用域 | 中 |
| **DOM 引用残留** | 已移除的 DOM 元素仍被 JS 变量引用 | 中 |
| **定时器/事件监听器未清理** | 循环中注册的定时器或事件监听器未被移除 | 高 |

### 1.2 典型内存泄漏场景

```javascript
// ❌ 场景一：意外创建全局变量
function processItems(items) {
    for (i = 0; i < items.length; i++) {  // 未声明 i，泄漏为全局变量！
        result = items[i] * 2;             // result 也泄漏为全局变量！
        console.log(result);
    }
}
processItems([1, 2, 3]);
console.log(window.i);      // 3 — 全局变量 i 泄漏
console.log(window.result); // 6 — 全局变量 result 泄漏

// ❌ 场景二：var 声明导致循环变量提升
function createButtons() {
    for (var i = 0; i < 5; i++) {
        var btn = document.createElement('button');
        btn.addEventListener('click', function() {
            console.log(i); // 永远输出 5，闭包引用的是同一个 i
        });
        document.body.appendChild(btn);
    }
}

// ❌ 场景三：循环中的 DOM 引用泄漏
var elements = [];
function cacheElements() {
    for (var i = 0; i < 1000; i++) {
        elements.push(document.getElementById('item-' + i));
    }
    // 即使 DOM 元素从页面移除，elements 数组仍持有引用，无法 GC
}
```

### 1.3 内存泄漏的后果

```
循环次数少 → 少量内存浪费 → 可能无明显影响
循环次数多 → 内存持续增长 → 页面卡顿
长期运行   → 内存耗尽     → 页面崩溃 / 浏览器假死
```

---

## 2. 变量声明规范

### 2.1 声明关键字选择原则

| 关键字 | 作用域 | 可重复声明 | 提升行为 | 挂载到 window | 推荐使用场景 |
|--------|--------|------------|----------|---------------|-------------|
| `var` | 函数作用域 | 是 | 提升并初始化为 `undefined` | 是（全局作用域） | **不推荐使用** |
| `let` | 块级作用域 | 否 | 提升但进入 TDZ | 否 | 循环变量、可变变量 |
| `const` | 块级作用域 | 否 | 提升但进入 TDZ | 否 | 常量、函数引用、对象引用 |

### 2.2 循环变量声明规范

```javascript
// ✅ 正确：使用 let 声明循环变量
for (let i = 0; i < items.length; i++) {
    // i 是块级作用域，每次迭代创建新的绑定
    const item = items[i];  // 使用 const 声明不变引用
    processItem(item);
}
// 此处无法访问 i — 块级作用域已结束

// ✅ 正确：使用 const 声明循环内的不变引用
for (let i = 0; i < items.length; i++) {
    const element = items[i];       // 每次迭代独立的 const 绑定
    const result = transform(element);
    displayResult(result);
}

// ✅ 正确：for...of 循环中使用 const（每次迭代新绑定）
for (const item of items) {
    processItem(item);
}

// ❌ 错误：使用 var 声明循环变量
for (var i = 0; i < items.length; i++) {
    // i 泄漏到外层作用域
}
console.log(i); // 可访问，但这是意外的副作用

// ❌ 错误：未声明变量（严格模式下会报错，非严格模式泄漏为全局变量）
for (i = 0; i < items.length; i++) {
    // i 成为 window.i
}
```

### 2.3 循环中缓存数组长度的规范

```javascript
// ✅ 推荐：使用 const 缓存数组长度，避免每次迭代读取 length 属性
for (let i = 0; i < items.length; i++) {
    // 每次迭代都访问 items.length
}

// ✅ 更优：缓存长度
for (let i = 0, len = items.length; i < len; i++) {
    // len 是块级作用域内的常量
}

// ✅ 推荐：使用 for...of（最简洁）
for (const item of items) {
    processItem(item);
}

// ❌ 错误：使用 var 缓存长度
for (var i = 0, len = items.length; i < len; i++) {
    // i 和 len 都泄漏到外层作用域
}
```

### 2.4 严格模式强制检查

```javascript
'use strict';

function processLoop() {
    // 严格模式下，未声明变量会抛出 ReferenceError
    for (i = 0; i < 10; i++) {  // ❌ ReferenceError: i is not defined
        console.log(i);
    }
}

// ✅ 推荐：所有 JS 文件或模块默认开启严格模式
// 在文件顶部添加 'use strict';
// 或使用 ES Module（自动严格模式）
```

---

## 3. 块级作用域的正确使用

### 3.1 let/const 的块级作用域机制

```javascript
// 块级作用域示意
{
    let blockVar = 'block scoped';
    const blockConst = 'also block scoped';
    var functionVar = 'function scoped';  // 会穿透块级作用域
}
console.log(functionVar); // 'function scoped' — 可访问
// console.log(blockVar); // ReferenceError — 不可访问

// 在 for 循环中的应用
for (let i = 0; i < 3; i++) {
    // 每次迭代创建一个新的块级作用域
    let iterationValue = i * 2;  // 仅在此次迭代中有效
    console.log(iterationValue);
}
// console.log(iterationValue); // ReferenceError — 完全隔离
```

### 3.2 for 循环的每次迭代独立作用域

```javascript
// let 声明的循环变量：每次迭代创建新的绑定
const callbacks = [];
for (let i = 0; i < 3; i++) {
    callbacks.push(() => i);
}
console.log(callbacks[0]()); // 0
console.log(callbacks[1]()); // 1
console.log(callbacks[2]()); // 2
// 每个回调函数捕获的是各自迭代中的独立 i 绑定

// var 声明的循环变量：所有迭代共享同一个绑定
const varCallbacks = [];
for (var i = 0; i < 3; i++) {
    varCallbacks.push(() => i);
}
console.log(varCallbacks[0]()); // 3
console.log(varCallbacks[1]()); // 3
console.log(varCallbacks[2]()); // 3
// 所有回调函数共享同一个 i，循环结束后 i 为 3
```

### 3.3 在循环中使用块级作用域隔离变量

```javascript
// ✅ 使用块级作用域隔离子循环
for (let i = 0; i < 5; i++) {
    // 外层循环变量
    for (let j = 0; j < 3; j++) {
        // 内层循环变量，与外层完全隔离
        const combined = i * 10 + j;
        processItem(combined);
    }
    // j 在此处不可访问
}
// i 在此处不可访问

// ✅ 使用 {} 创建显式块级作用域
for (let i = 0; i < largeData.length; i++) {
    // 创建独立块，使大对象尽早可被 GC
    {
        const chunk = largeData[i];  // chunk 仅在块内有效
        const processed = heavyProcess(chunk);
        results.push(processed);
    }
    // chunk 和 processed 超出作用域，可被垃圾回收
}

// ❌ 错误：循环变量向外泄漏
for (var i = 0; i < 5; i++) {
    for (var j = 0; j < 3; j++) {
        // i 和 j 共享同一个绑定，且泄漏到外层
    }
}
console.log(i, j); // 5, 3 — 意外泄漏
```

### 3.4 for...in 和 for...of 的作用域特性

```javascript
// for...of：每次迭代创建新的 const 绑定
const arr = [10, 20, 30];
for (const value of arr) {
    // value 是每次迭代独立的 const 绑定
    console.log(value);
    // value = 100; // TypeError: Assignment to constant variable
}

// for...in：同样每次迭代创建新的绑定
const obj = { a: 1, b: 2, c: 3 };
for (const key in obj) {
    // key 是每次迭代独立的 const 绑定
    console.log(key, obj[key]);
}

// 使用解构获取索引和值
for (const [index, value] of arr.entries()) {
    console.log(`${index}: ${value}`);
}
```

---

## 4. 循环中的闭包陷阱与解决方案

### 4.1 经典闭包陷阱

```javascript
// ❌ 陷阱：var + 异步回调 = 所有回调共享同一变量
function createButtonHandlers() {
    const buttons = document.querySelectorAll('button');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].addEventListener('click', function() {
            console.log('Button ' + i + ' clicked'); // 永远输出 "Button 5 clicked"
        });
    }
}

// 原因分析：
// 1. var 声明的 i 是函数作用域，所有迭代共享同一个 i
// 2. 事件回调是异步的，执行时循环已结束，i = buttons.length
// 3. 闭包引用的是 i 的最终值，而非每次迭代时的值
```

### 4.2 解决方案一：使用 let

```javascript
// ✅ 方案一：使用 let（推荐，最简洁）
function createButtonHandlers() {
    const buttons = document.querySelectorAll('button');
    for (let i = 0; i < buttons.length; i++) {
        buttons[i].addEventListener('click', function() {
            console.log('Button ' + i + ' clicked'); // 输出正确的索引
        });
    }
}
// let 在每次迭代创建独立的绑定，闭包捕获各自的值
```

### 4.3 解决方案二：使用 IIFE

```javascript
// ✅ 方案二：使用 IIFE 创建独立作用域
function createButtonHandlers() {
    const buttons = document.querySelectorAll('button');
    for (var i = 0; i < buttons.length; i++) {
        (function(index) {
            buttons[index].addEventListener('click', function() {
                console.log('Button ' + index + ' clicked');
            });
        })(i);
    }
}
// IIFE 立即执行，将当前 i 值作为参数传入，创建独立的作用域
```

### 4.4 解决方案三：使用 forEach

```javascript
// ✅ 方案三：使用 forEach（每次迭代天然独立作用域）
function createButtonHandlers() {
    const buttons = document.querySelectorAll('button');
    buttons.forEach((button, index) => {
        button.addEventListener('click', function() {
            console.log('Button ' + index + ' clicked');
        });
    });
}
```

### 4.5 方案四：使用 bind 绑定参数

```javascript
// ✅ 方案四：使用 bind 固化参数
function createButtonHandlers() {
    function handleClick(index) {
        console.log('Button ' + index + ' clicked');
    }

    const buttons = document.querySelectorAll('button');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].addEventListener('click', handleClick.bind(null, i));
    }
}
```

### 4.6 方案对比

| 方案 | 简洁性 | 兼容性 | 内存开销 | 推荐度 |
|------|--------|--------|----------|--------|
| `let` 声明 | 极简 | ES6+ | 低 | 首选 |
| IIFE | 一般 | 全兼容 | 每次迭代创建新函数 | 兼容旧环境 |
| `forEach` | 简洁 | ES5+ | 低 | 推荐 |
| `bind` | 一般 | ES5+ | 每次创建绑定函数 | 特定场景 |

### 4.7 循环中不必要的闭包优化

```javascript
// ❌ 过度使用闭包：每次迭代创建新函数，且捕获大对象
function processLargeData(dataArray) {
    const results = [];
    for (let i = 0; i < dataArray.length; i++) {
        // 闭包捕获了整个 dataArray，阻止 GC
        const processor = function() {
            return heavyTransform(dataArray[i]);
        };
        results.push(processor());
    }
    return results;
}

// ✅ 优化：避免不必要的闭包，直接调用
function processLargeData(dataArray) {
    const results = [];
    for (let i = 0; i < dataArray.length; i++) {
        results.push(heavyTransform(dataArray[i]));
    }
    return results; // dataArray 可以通过参数传递，函数结束即可 GC
}

// ✅ 优化：分批处理大数组，减少内存峰值
async function processInBatches(dataArray, batchSize = 100) {
    const results = [];
    for (let i = 0; i < dataArray.length; i += batchSize) {
        const batch = dataArray.slice(i, i + batchSize);
        const batchResults = batch.map(item => heavyTransform(item));
        results.push(...batchResults);
        // 每批处理完，batch 变量可被 GC
        await yieldToEventLoop(); // 让出主线程
    }
    return results;
}

function yieldToEventLoop() {
    return new Promise(resolve => setTimeout(resolve, 0));
}
```

---

## 5. IIFE 在循环中的应用

### 5.1 IIFE 基本模式

```javascript
// IIFE 语法形式
(function() {
    // 独立的函数作用域
    // 内部变量不会泄漏到外部
})();

// 带参数的 IIFE
for (var i = 0; i < 5; i++) {
    (function(index) {
        // index 捕获了当前 i 的值
        setTimeout(() => {
            console.log(index); // 输出 0, 1, 2, 3, 4
        }, 100);
    })(i);
}
```

### 5.2 IIFE 用于隔离循环中的异步操作

```javascript
// 场景：批量发起异步请求，需要保留每次请求的上下文
function fetchAllWithContext(urls, baseParams) {
    const results = [];

    for (var i = 0; i < urls.length; i++) {
        (function(url, index) {
            // 独立作用域，隔离 url 和 index
            const requestParams = {
                ...baseParams,
                page: index + 1,
                timestamp: Date.now()
            };

            fetch(url, { body: JSON.stringify(requestParams) })
                .then(response => response.json())
                .then(data => {
                    results[index] = data; // 按顺序存储结果
                    console.log(`第 ${index + 1} 个请求完成`);
                })
                .catch(err => {
                    console.error(`请求 ${url} 失败:`, err);
                });
        })(urls[i], i);
    }

    return results;
}
```

### 5.3 IIFE 用于清理循环中的临时资源

```javascript
// 场景：循环中创建临时 DOM 元素，需要确保及时清理
function renderThumbnails(imageUrls) {
    const container = document.getElementById('thumbnails');

    for (let i = 0; i < imageUrls.length; i++) {
        // IIFE 确保临时变量在块结束后可被 GC
        (function(url, idx) {
            const tempCanvas = document.createElement('canvas');
            const tempCtx = tempCanvas.getContext('2d');
            const tempImage = new Image();

            tempImage.onload = function() {
                tempCanvas.width = 100;
                tempCanvas.height = 100;
                tempCtx.drawImage(tempImage, 0, 0, 100, 100);

                const thumbnail = document.createElement('img');
                thumbnail.src = tempCanvas.toDataURL();
                thumbnail.alt = `Thumbnail ${idx + 1}`;
                container.appendChild(thumbnail);

                // 手动清理临时资源
                tempCanvas.width = 0;
                tempCanvas.height = 0;
                tempImage.src = '';
            };

            tempImage.src = url;
        })(imageUrls[i], i);
    }
}
```

### 5.4 IIFE 与现代替代方案对比

```javascript
// 场景：为每个元素绑定不同的事件处理器
const elements = document.querySelectorAll('.item');

// 方式一：IIFE（ES5 兼容）
for (var i = 0; i < elements.length; i++) {
    (function(elem, index) {
        elem.addEventListener('click', function() {
            handleClick(index);
        });
    })(elements[i], i);
}

// 方式二：let（ES6+，推荐）
for (let i = 0; i < elements.length; i++) {
    elements[i].addEventListener('click', function() {
        handleClick(i);
    });
}

// 方式三：forEach（ES5+）
elements.forEach((elem, index) => {
    elem.addEventListener('click', () => handleClick(index));
});
```

---

## 6. 内存泄漏检测与测试方法

### 6.1 全局变量泄漏检测

```javascript
// 方法一：检测 window 对象上是否存在意外属性
function detectGlobalLeaks(whitelist = []) {
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    document.body.appendChild(iframe);

    // 获取纯净的 window 属性集合
    const cleanWindow = iframe.contentWindow;
    const cleanKeys = Object.keys(cleanWindow);

    document.body.removeChild(iframe);

    // 对比当前 window 与纯净 window
    const leaks = [];
    for (const key of Object.keys(window)) {
        if (!cleanKeys.includes(key) && !whitelist.includes(key)) {
            leaks.push({
                name: key,
                value: window[key],
                type: typeof window[key]
            });
        }
    }

    return leaks;
}

// 使用示例
const leaks = detectGlobalLeaks(['myApp', 'jQuery']);
if (leaks.length > 0) {
    console.error('检测到全局变量泄漏:', leaks);
    leaks.forEach(leak => {
        console.warn(`泄漏变量: ${leak.name}, 类型: ${leak.type}, 值:`, leak.value);
    });
}
```

### 6.2 函数执行前后对比检测

```javascript
// 方法二：对比函数执行前后的全局变量
function testForLeaks(fn, label = 'test') {
    const snapshotBefore = Object.keys(window).filter(k => !k.startsWith('webkit'));

    fn();

    const snapshotAfter = Object.keys(window).filter(k => !k.startsWith('webkit'));
    const newGlobals = snapshotAfter.filter(k => !snapshotBefore.includes(k));

    if (newGlobals.length > 0) {
        console.error(`[${label}] 检测到新增全局变量:`, newGlobals);
        newGlobals.forEach(key => {
            console.error(`  - window.${key} = ${typeof window[key]}: ${JSON.stringify(window[key])}`);
        });
        return false;
    }

    console.log(`[${label}] 未检测到全局变量泄漏`);
    return true;
}

// 使用示例
testForLeaks(() => {
    for (i = 0; i < 5; i++) {  // 故意使用未声明的 i
        temp = i * 2;           // 故意使用未声明的 temp
    }
}, '未声明变量测试');
// 输出: [未声明变量测试] 检测到新增全局变量: ['i', 'temp']
```

### 6.3 闭包泄漏检测

```javascript
// 方法三：检测闭包是否阻止了垃圾回收
function testClosureLeak() {
    // 使用 WeakRef 检测对象是否被 GC（需要浏览器支持）
    if (typeof WeakRef === 'undefined') {
        console.warn('当前环境不支持 WeakRef，无法进行精确的 GC 检测');
        return;
    }

    let ref;
    function createLeak() {
        const largeObject = new Array(1000000).fill('data');
        ref = new WeakRef(largeObject);

        // 场景测试：是否在循环中创建了持有大对象的闭包
        for (let i = 0; i < 10; i++) {
            const closure = () => largeObject[i]; // 闭包持有 largeObject 引用
            closure(); // 使用后 closure 应被释放
        }
        // largeObject 超出作用域
    }

    createLeak();

    // 强制 GC（需要 --expose-gc 标志）
    if (typeof gc === 'function') {
        gc();
    }

    // 等待 GC 完成
    setTimeout(() => {
        const obj = ref.deref();
        if (obj) {
            console.warn('大对象未被回收，可能存在闭包泄漏');
        } else {
            console.log('大对象已被回收，无闭包泄漏');
        }
    }, 1000);
}
```

### 6.4 浏览器 DevTools 内存分析

```javascript
// 方法四：使用 Performance 和 Memory 面板
// 手动步骤（Chrome DevTools）：
// 1. 打开 Performance 面板
// 2. 勾选 "Memory" 选项
// 3. 点击录制按钮
// 4. 执行循环操作
// 5. 停止录制
// 6. 观察 JS Heap 是否持续增长（锯齿状上升趋势 = 内存泄漏）

// 代码辅助：在关键位置插入标记
function memoryTest() {
    performance.mark('loop-start');

    for (let i = 0; i < 10000; i++) {
        // 执行测试代码
        const item = processItem(i);
        results.push(item);
    }

    performance.mark('loop-end');
    performance.measure('loop-duration', 'loop-start', 'loop-end');

    const measure = performance.getEntriesByName('loop-duration')[0];
    console.log(`循环执行耗时: ${measure.duration.toFixed(2)}ms`);

    performance.clearMarks();
    performance.clearMeasures();
}

// 使用 console.memory 查看堆内存（Chrome 专用）
function checkMemoryUsage() {
    if (console.memory) {
        console.log('堆内存使用情况:', {
            usedJSHeapSize: (console.memory.usedJSHeapSize / 1048576).toFixed(2) + ' MB',
            totalJSHeapSize: (console.memory.totalJSHeapSize / 1048576).toFixed(2) + ' MB',
            limit: (console.memory.jsHeapSizeLimit / 1048576).toFixed(2) + ' MB'
        });
    }
}
```

### 6.5 自动化测试套件

```javascript
// 完整的自动化测试框架
class MemoryLeakDetector {
    constructor() {
        this.tests = [];
        this.results = [];
    }

    // 注册测试用例
    addTest(name, fn, expectedLeaks = 0) {
        this.tests.push({ name, fn, expectedLeaks });
        return this;
    }

    // 运行所有测试
    async run() {
        console.log(`开始运行 ${this.tests.length} 个内存泄漏检测测试...\n`);

        for (const test of this.tests) {
            const result = await this.runSingle(test);
            this.results.push(result);
        }

        this.report();
        return this.results;
    }

    async runSingle(test) {
        const snapshotBefore = this.getGlobalSnapshot();

        try {
            await test.fn();
        } catch (err) {
            return {
                name: test.name,
                passed: false,
                error: err.message,
                leaks: []
            };
        }

        // 等待微任务完成
        await new Promise(resolve => setTimeout(resolve, 100));

        const snapshotAfter = this.getGlobalSnapshot();
        const newGlobals = snapshotAfter.filter(k => !snapshotBefore.includes(k));

        const passed = newGlobals.length <= test.expectedLeaks;

        return {
            name: test.name,
            passed,
            leaks: newGlobals.map(k => ({ name: k, type: typeof window[k] })),
            expectedLeaks: test.expectedLeaks
        };
    }

    getGlobalSnapshot() {
        return Object.keys(window).filter(k =>
            !k.startsWith('webkit') &&
            !k.startsWith('on') &&
            k !== 'name' &&
            k !== 'length'
        );
    }

    report() {
        console.log('='.repeat(60));
        console.log('内存泄漏检测报告');
        console.log('='.repeat(60));

        let passed = 0;
        let failed = 0;

        for (const result of this.results) {
            const status = result.passed ? 'PASS' : 'FAIL';
            const icon = result.passed ? '✓' : '✗';
            console.log(`${icon} [${status}] ${result.name}`);

            if (result.leaks.length > 0) {
                console.log(`   泄漏变量: ${result.leaks.map(l => l.name).join(', ')}`);
            }
            if (result.error) {
                console.log(`   错误: ${result.error}`);
            }

            if (result.passed) passed++;
            else failed++;
        }

        console.log('\n' + '='.repeat(60));
        console.log(`总计: ${this.results.length} | 通过: ${passed} | 失败: ${failed}`);
        console.log('='.repeat(60));
    }
}

// 使用示例
const detector = new MemoryLeakDetector();

detector
    .addTest('使用 let 声明循环变量', () => {
        for (let i = 0; i < 10; i++) {
            const temp = i * 2;
        }
    }, 0) // 预期 0 个泄漏

    .addTest('使用 var 声明循环变量', () => {
        for (var i = 0; i < 10; i++) {
            var temp = i * 2;
        }
    }, 2) // 预期 2 个泄漏（i 和 temp，非严格模式下仅在全局作用域时）

    .addTest('未声明变量', () => {
        for (i_test = 0; i_test < 5; i_test++) {
            temp_test = i_test * 2;
        }
    }, 2) // 预期 2 个泄漏

    .addTest('for...of 使用 const', () => {
        for (const item of [1, 2, 3]) {
            const result = item * 2;
        }
    }, 0); // 预期 0 个泄漏

// 运行测试
// detector.run();
```

---

## 7. 编码规范与质量标准

### 7.1 强制规则（ESLint 配置）

```javascript
// .eslintrc.js 推荐配置
module.exports = {
    extends: ['eslint:recommended'],
    parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module'
    },
    rules: {
        // 禁止使用 var
        'no-var': 'error',

        // 优先使用 const
        'prefer-const': 'error',

        // 禁止未声明的变量
        'no-undef': 'error',

        // 禁止未使用的变量
        'no-unused-vars': ['error', {
            vars: 'all',
            args: 'after-used',
            ignoreRestSiblings: true
        }],

        // 禁止在循环中创建函数（防止意外的闭包问题）
        'no-loop-func': 'warn',

        // 强制块级作用域
        'block-scoped-var': 'error',

        // 建议使用 for...of 替代传统 for 循环
        // （如需要，可安装 eslint-plugin-unicorn）
        // 'unicorn/prefer-for-of': 'warn',

        // 禁止对 const 重新赋值
        'no-const-assign': 'error',

        // 要求使用 === 和 !==
        'eqeqeq': ['error', 'always']
    }
};
```

### 7.2 编码规范清单

| 编号 | 规范 | 说明 | 优先级 |
|------|------|------|--------|
| R1 | 使用 `let` 声明循环变量 | 禁止 `var`、禁止未声明变量 | 必须 |
| R2 | 循环内不变引用使用 `const` | 如 `const item = items[i]` | 必须 |
| R3 | 优先使用 `for...of` 遍历数组 | 更简洁，天然块级作用域 | 推荐 |
| R4 | 缓存数组长度 | `for (let i = 0, len = arr.length; i < len; i++)` | 推荐 |
| R5 | 避免在循环中创建闭包 | 除非必要，使用 `let` 或 `forEach` 替代 | 推荐 |
| R6 | 循环中注册的事件监听器必须有对应移除逻辑 | 防止 DOM 引用泄漏 | 必须 |
| R7 | 循环中创建的定时器必须清理 | `clearTimeout` / `clearInterval` | 必须 |
| R8 | 大数组分批处理 | 使用 `slice` 分批，降低内存峰值 | 推荐 |
| R9 | 开启严格模式 | `'use strict'` 或 ES Module | 必须 |
| R10 | 配置 ESLint 规则 | `no-var`、`prefer-const`、`no-undef` | 必须 |

### 7.3 质量标准

```javascript
// 质量标准：满足以下所有条件视为合格

// Q1: 零全局变量泄漏
// 测试方法：运行 testForLeaks() 函数，无新增全局变量

// Q2: 循环变量仅在循环体内可访问
// 测试方法：在循环外尝试访问循环变量应抛出 ReferenceError

// Q3: 所有变量使用 const 或 let 声明
// 测试方法：ESLint no-var 规则通过，无 var 关键字

// Q4: 闭包捕获正确的值
// 测试方法：所有异步回调输出与迭代次数一致的独立值

// Q5: 内存可被正常回收
// 测试方法：Chrome DevTools Memory 面板，JS Heap 无持续增长趋势

// Q6: 事件监听器和定时器在组件销毁时被清理
// 测试方法：移除组件后，Heap Snapshot 中无相关 DOM 引用

// 质量检测函数
function qualityCheck(fn) {
    const checks = {
        noGlobalLeak: false,
        blockScoped: false,
        noVarUsage: false,
        correctClosureValue: false
    };

    // 检测全局泄漏
    const before = Object.keys(window);
    fn();
    const after = Object.keys(window);
    checks.noGlobalLeak = after.length === before.length;

    // 检测闭包正确性
    const callbacks = [];
    for (let i = 0; i < 5; i++) {
        callbacks.push(() => i);
    }
    checks.correctClosureValue = callbacks.every((cb, idx) => cb() === idx);

    // 综合评分
    const score = Object.values(checks).filter(Boolean).length;
    const total = Object.keys(checks).length;

    return {
        passed: score === total,
        score: `${score}/${total}`,
        details: checks
    };
}
```

### 7.4 代码审查检查点

```markdown
## Code Review — for 循环内存管理检查点

### 声明检查
- [ ] 循环变量是否使用 `let` 而非 `var`？
- [ ] 循环内是否有未声明的变量（`i = 0` 而非 `let i = 0`）？
- [ ] 循环内的不变引用是否使用 `const`？

### 作用域检查
- [ ] 循环变量是否在循环外被意外访问？
- [ ] 嵌套循环的内外层变量是否使用不同的变量名？
- [ ] 是否使用了块级作用域 `{}` 隔离大对象？

### 闭包检查
- [ ] 循环中是否创建了闭包？是否必要？
- [ ] 闭包捕获的值是否是每次迭代的独立绑定？
- [ ] 异步回调中使用的循环变量是否正确？

### 资源检查
- [ ] 循环中注册的事件监听器是否有对应的 `removeEventListener`？
- [ ] 循环中创建的定时器是否被清理？
- [ ] 循环中创建的 DOM 引用是否在不需要时置为 `null`？
- [ ] 大数组是否分批处理？

### 性能检查
- [ ] 数组长度是否已缓存？
- [ ] 是否优先使用 `for...of` 遍历？
- [ ] 循环体内是否有不必要的重复计算？
```

---

## 8. 综合案例与最佳实践模板

### 8.1 模板：安全的 for 循环

```javascript
// 标准模板：安全的 for 循环
function safeForLoop(items) {
    'use strict'; // 始终开启严格模式

    const results = [];                  // 使用 const 声明引用不变的数组
    const len = items.length;            // 缓存长度

    for (let i = 0; i < len; i++) {     // let 声明循环变量
        const item = items[i];           // const 声明每次迭代不变的引用
        const processed = processItem(item);
        results.push(processed);
    }

    // 循环结束后，i 和 item 不可访问（块级作用域）
    return results;
}
```

### 8.2 模板：带事件绑定的循环

```javascript
// 标准模板：循环中绑定事件
function bindEventsWithCleanup(container) {
    const elements = container.querySelectorAll('.interactive');
    const cleanups = []; // 收集清理函数

    for (const [index, element] of elements.entries()) {
        // 使用命名函数便于后续移除
        const handler = createHandler(index);

        element.addEventListener('click', handler);

        // 注册清理函数
        cleanups.push(() => {
            element.removeEventListener('click', handler);
        });
    }

    // 返回清理函数，供组件销毁时调用
    return function cleanup() {
        cleanups.forEach(fn => fn());
        cleanups.length = 0; // 释放引用
    };
}

function createHandler(index) {
    return function(event) {
        console.log(`Element ${index} clicked`, event.target);
    };
}
```

### 8.3 模板：异步循环处理

```javascript
// 标准模板：异步循环处理（避免内存峰值）
async function asyncProcessInBatches(items, batchSize = 50) {
    const results = [];

    for (let i = 0; i < items.length; i += batchSize) {
        // 使用块级作用域隔离批次数据
        {
            const batch = items.slice(i, Math.min(i + batchSize, items.length));

            // 并发处理当前批次
            const batchResults = await Promise.all(
                batch.map(item => processItemAsync(item))
            );

            results.push(...batchResults);
        }
        // batch 和 batchResults 超出作用域，可被 GC

        // 让出事件循环，避免长时间阻塞
        await new Promise(resolve => setTimeout(resolve, 0));
    }

    return results;
}
```

### 8.4 模板：DOM 操作中的内存安全

```javascript
// 标准模板：DOM 操作中的内存安全
class ListRenderer {
    constructor(container) {
        this.container = container;
        this.observers = new Set();        // 使用 Set 管理观察者
        this.eventHandlers = new WeakMap(); // 使用 WeakMap 避免内存泄漏
    }

    render(items) {
        // 先清理旧内容
        this.destroy();

        const fragment = document.createDocumentFragment();

        for (let i = 0; i < items.length; i++) {
            const item = items[i];
            const element = this.createItemElement(item, i);

            // 使用 WeakMap 存储事件处理器，DOM 移除后可自动 GC
            const handler = (e) => this.handleClick(item, i, e);
            this.eventHandlers.set(element, handler);
            element.addEventListener('click', handler);

            fragment.appendChild(element);
        }

        this.container.appendChild(fragment);
        // fragment 在 appendChild 后自动清空，其中元素移入容器
    }

    createItemElement(item, index) {
        const div = document.createElement('div');
        div.textContent = item.label;
        div.className = 'list-item';
        return div;
    }

    handleClick(item, index, event) {
        console.log(`Item ${index} clicked:`, item);
    }

    destroy() {
        // 清理所有子元素的事件监听器
        const children = Array.from(this.container.children);
        for (const child of children) {
            const handler = this.eventHandlers.get(child);
            if (handler) {
                child.removeEventListener('click', handler);
                this.eventHandlers.delete(child);
            }
        }

        this.container.innerHTML = ''; // 清空容器
        this.observers.clear();        // 清理观察者
    }
}
```

### 8.5 完整示例：综合应用

```javascript
// 综合示例：包含所有最佳实践的循环处理
'use strict';

class DataProcessor {
    constructor() {
        // 使用 WeakMap 存储 DOM 关联数据，自动 GC
        this.elementData = new WeakMap();
        this.cleanupFns = [];
    }

    /**
     * 批量处理数据并渲染到 DOM
     * 整合了所有内存管理最佳实践
     */
    async processAndRender(dataArray, container) {
        // 1. 参数验证
        if (!Array.isArray(dataArray) || !container) {
            throw new TypeError('参数类型错误');
        }

        // 2. 清理旧数据
        this.cleanup();

        const fragment = document.createDocumentFragment();
        const BATCH_SIZE = 100;
        const totalLen = dataArray.length;

        // 3. 分批处理，控制内存峰值
        for (let batchStart = 0; batchStart < totalLen; batchStart += BATCH_SIZE) {
            const batchEnd = Math.min(batchStart + BATCH_SIZE, totalLen);

            // 4. 使用块级作用域隔离批次
            {
                const batch = dataArray.slice(batchStart, batchEnd);

                // 5. 处理批次中的每个元素
                for (let i = 0; i < batch.length; i++) {
                    const item = batch[i];
                    const globalIndex = batchStart + i;

                    // 6. 使用 const 声明不变引用
                    const element = this.createElement(item, globalIndex);

                    // 7. 使用 WeakMap 存储关联数据
                    this.elementData.set(element, {
                        original: item,
                        index: globalIndex,
                        renderedAt: Date.now()
                    });

                    fragment.appendChild(element);
                }
            }
            // batch 超出作用域，可被 GC

            // 8. 让出主线程，保持 UI 响应
            if (batchStart + BATCH_SIZE < totalLen) {
                await new Promise(resolve => setTimeout(resolve, 0));
            }
        }

        // 9. 一次性插入 DOM，减少回流
        container.appendChild(fragment);
    }

    createElement(item, index) {
        const div = document.createElement('div');
        div.textContent = item.label;
        div.className = 'data-item';

        // 使用命名函数便于清理
        const clickHandler = (e) => {
            const data = this.elementData.get(div);
            if (data) {
                console.log(`Clicked item ${data.index}:`, data.original);
            }
        };

        div.addEventListener('click', clickHandler);

        // 注册清理函数
        this.cleanupFns.push(() => {
            div.removeEventListener('click', clickHandler);
        });

        return div;
    }

    cleanup() {
        // 批量执行清理
        for (const fn of this.cleanupFns) {
            fn();
        }
        this.cleanupFns.length = 0; // 清空数组，释放引用
    }

    destroy() {
        this.cleanup();
        // WeakMap 中的引用在 DOM 元素移除后会自动被 GC
    }
}
```

---

> **参考资料：**
> - MDN Web Docs — [let](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/let)
> - MDN Web Docs — [const](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/const)
> - MDN Web Docs — [Memory Management](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Memory_Management)
> - ECMAScript 规范 — [Block-Level Scoping](https://tc39.es/ecma262/#sec-block)
> - ESLint 规则 — [no-var](https://eslint.org/docs/latest/rules/no-var) | [prefer-const](https://eslint.org/docs/latest/rules/prefer-const)
> - Chrome DevTools — [Memory Problems](https://developer.chrome.com/docs/devtools/memory-problems/)