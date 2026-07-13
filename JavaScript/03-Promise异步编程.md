# JavaScript Promise 异步编程面试题

## 一、核心概念解析

### 1. Promise 定义

Promise 是 ES6 引入的异步编程解决方案，它代表一个**未来才完成的操作**的结果。Promise 是一个对象，可以获取异步操作的消息。

### 2. 三种状态

```
Pending（进行中） ──→ Fulfilled（已成功）
                 └──→ Rejected（已失败）
```

- 状态一旦改变，**不可逆转**
- 只能从 `Pending` 变为 `Fulfilled` 或 `Rejected`

### 3. 基本用法

```javascript
const promise = new Promise((resolve, reject) => {
  // 异步操作
  setTimeout(() => {
    const success = true;
    if (success) {
      resolve('操作成功');
    } else {
      reject(new Error('操作失败'));
    }
  }, 1000);
});

promise
  .then(value => console.log(value))   // 操作成功
  .catch(error => console.error(error))
  .finally(() => console.log('完成'));
```

### 4. Promise 静态方法

| 方法 | 行为 | 快速失败 |
|------|------|---------|
| `Promise.all` | 全部成功才成功 | 任一失败立即失败 |
| `Promise.allSettled` | 等待所有完成（无论成功/失败） | 从不失败 |
| `Promise.race` | 返回第一个完成的（无论成功/失败） | 取决于第一个完成的状态 |
| `Promise.any` | 返回第一个成功的 | 全部失败才失败 |
| `Promise.resolve` | 包装为 resolved 的 Promise | — |
| `Promise.reject` | 包装为 rejected 的 Promise | — |

---

## 二、面试题

### 题目 1：Promise 执行顺序（基础）

#### 题干

```javascript
console.log('1');

setTimeout(() => console.log('2'), 0);

Promise.resolve().then(() => console.log('3'));

console.log('4');
```

以上代码的输出顺序是什么？为什么？

#### 解题思路

本题考察**微任务（Microtask）与宏任务（Macrotask）** 的执行顺序：

1. 同步代码先执行：`1` → `4`
2. 微任务优先于宏任务：`Promise.then` 是微任务，`setTimeout` 是宏任务
3. 因此 `3` 在 `2` 之前输出

#### 正确代码实现

```javascript
// 输出顺序：
// 1
// 4
// 3
// 2

// 执行顺序分析：
// 1. 执行栈：console.log('1')
// 2. 执行栈：setTimeout 回调进入宏任务队列
// 3. 执行栈：Promise.resolve().then 回调进入微任务队列
// 4. 执行栈：console.log('4')
// 5. 执行栈清空，清空微任务队列：console.log('3')
// 6. 执行宏任务队列：console.log('2')
```

#### 知识点拓展

- **宏任务**：`setTimeout`、`setInterval`、`I/O`、`UI rendering`、`setImmediate`
- **微任务**：`Promise.then/catch/finally`、`MutationObserver`、`queueMicrotask`
- 每次事件循环中，先执行一个宏任务，然后清空所有微任务，再进行渲染

---

### 题目 2：Promise 链式调用与错误处理（基础）

#### 题干

```javascript
Promise.resolve(1)
  .then(val => {
    console.log(val);
    return val + 1;
  })
  .then(val => {
    console.log(val);
    throw new Error('Error!');
  })
  .then(val => {
    console.log(val);
  })
  .catch(err => {
    console.log('Caught:', err.message);
  })
  .then(val => {
    console.log('After catch:', val);
  });
```

以上代码的输出是什么？

#### 解题思路

1. Promise 链式调用中，每个 `.then` 返回一个新的 Promise
2. 如果 `.then` 中抛出异常或返回 rejected Promise，会跳过后续 `.then` 直到找到 `.catch`
3. `.catch` 处理完错误后，可以继续链式调用 `.then`
4. `.catch` 返回的 `undefined` 会作为下一个 `.then` 的参数

#### 正确代码实现

```javascript
// 输出：
// 1
// 2
// Caught: Error!
// After catch: undefined

// 流程分析：
// resolve(1) → then(1) 打印 1，返回 2
// then(2) 打印 2，抛出 Error
// 跳过 then(3)，进入 catch 打印 "Caught: Error!"
// catch 返回 undefined，进入 then(4) 打印 "After catch: undefined"
```

#### 知识点拓展

- `.catch` 实际上是 `.then(null, rejectHandler)` 的语法糖
- 在 `.then` 或 `.catch` 中 return 的值会被 `Promise.resolve()` 包装
- 如果 `.catch` 中再抛出异常，需要后续的 `.catch` 处理

---

### 题目 3：实现 Promise.all（进阶）

#### 题干

实现一个自定义的 `myPromiseAll` 函数，模拟 `Promise.all` 的行为。

#### 解题思路

`Promise.all` 的核心逻辑：
1. 接收一个可迭代对象（通常为数组）
2. 返回一个新的 Promise
3. 所有 Promise 都成功时，按输入顺序返回结果数组
4. 任一 Promise 失败，立即以该错误拒绝

#### 正确代码实现

```javascript
function myPromiseAll(promises) {
  return new Promise((resolve, reject) => {
    if (!Array.isArray(promises)) {
      return reject(new TypeError('Argument must be an array'));
    }

    if (promises.length === 0) {
      return resolve([]);
    }

    const results = [];
    let completed = 0;

    promises.forEach((promise, index) => {
      // 非 Promise 值用 Promise.resolve 包装
      Promise.resolve(promise)
        .then(value => {
          results[index] = value; // 保持输入顺序
          completed++;
          if (completed === promises.length) {
            resolve(results);
          }
        })
        .catch(reject); // 任一失败，立即拒绝
    });
  });
}

// 测试
const p1 = Promise.resolve(1);
const p2 = new Promise(r => setTimeout(() => r(2), 100));
const p3 = 3; // 普通值

myPromiseAll([p1, p2, p3]).then(console.log); // [1, 2, 3]

// 失败测试
const p4 = Promise.reject(new Error('Fail'));
myPromiseAll([p1, p4, p3]).catch(err => console.log(err.message)); // Fail
```

#### 知识点拓展

- `Promise.all` 采用**快速失败**策略：一个失败，整体失败
- `Promise.allSettled` 则等待所有完成，返回每个 Promise 的 `{ status, value/reason }`
- 注意 `Promise.all` 的**空数组**行为：`Promise.all([])` 返回 `[]`（已 resolve）

---

### 题目 4：Promise 并发控制（进阶）

#### 题干

实现一个函数 `asyncPool`，限制异步任务的并发数量。给定任务数组和并发数 `limit`，最多同时执行 `limit` 个任务。

#### 解题思路

1. 使用一个 `running` 计数器跟踪当前执行的任务数
2. 使用一个队列管理待执行的任务
3. 每当一个任务完成，从队列中取出下一个任务执行
4. 返回一个 Promise，在所有任务完成后 resolve

#### 正确代码实现

```javascript
function asyncPool(tasks, limit) {
  return new Promise(resolve => {
    const results = [];
    let running = 0;
    let index = 0;

    function run() {
      if (index === tasks.length && running === 0) {
        resolve(results);
        return;
      }

      while (running < limit && index < tasks.length) {
        const currentIndex = index++;
        const task = tasks[currentIndex];

        running++;
        Promise.resolve(task())
          .then(result => {
            results[currentIndex] = result;
          })
          .catch(error => {
            results[currentIndex] = { error };
          })
          .finally(() => {
            running--;
            run();
          });
      }
    }

    run();
  });
}

// 使用示例
const createTask = (id, delay) => () =>
  new Promise(r => {
    setTimeout(() => {
      console.log(`Task ${id} done`);
      r(id);
    }, delay);
  });

const tasks = [
  createTask(1, 1000),
  createTask(2, 500),
  createTask(3, 800),
  createTask(4, 200),
  createTask(5, 1200)
];

asyncPool(tasks, 2).then(results => {
  console.log('All done:', results);
});
// 同时最多 2 个任务执行
```

#### 知识点拓展

- 并发控制是面试高频考点，也是工程实践（如批量请求接口）中的常见需求
- 可用 `async/await` + `for...of` 实现类似效果
- 实际项目可参考 `p-limit` 库

---

### 题目 5：Promise 超时控制（进阶）

#### 题干

实现一个 `promiseTimeout` 函数，给一个 Promise 添加超时控制。如果 Promise 在指定时间内未完成，则自动超时失败。

#### 解题思路

利用 `Promise.race` 实现：将原始 Promise 与一个超时 Promise 进行竞速。

#### 正确代码实现

```javascript
function promiseTimeout(promise, ms) {
  const timeout = new Promise((_, reject) => {
    setTimeout(() => {
      reject(new Error(`Promise timed out after ${ms}ms`));
    }, ms);
  });

  return Promise.race([promise, timeout]);
}

// 使用示例
const slowPromise = new Promise(r => setTimeout(() => r('Done'), 2000));

promiseTimeout(slowPromise, 1000)
  .then(console.log)
  .catch(err => console.log(err.message)); // Promise timed out after 1000ms

// 改进版：超时后清理定时器
function promiseTimeoutWithCleanup(promise, ms) {
  let timer;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => {
      reject(new Error(`Timed out after ${ms}ms`));
    }, ms);
  });

  return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
}
```

#### 知识点拓展

- `Promise.race` 接收第一个完成的 Promise，无论成功或失败
- 超时后清理定时器是良好的实践，避免内存泄漏
- 超时控制常用于网络请求、数据库查询等场景

---

### 题目 6：实现 Promise.retry（高阶）

#### 题干

实现一个 `promiseRetry` 函数，当 Promise 失败时自动重试，最多重试 `times` 次。每次重试之间有延迟。

#### 解题思路

使用递归或 `async/await` 循环实现：
1. 执行任务
2. 如果成功则返回结果
3. 如果失败且剩余重试次数 > 0，等待延迟后重试
4. 如果所有重试都失败，抛出最后一次错误

#### 正确代码实现

```javascript
function promiseRetry(fn, times, delay = 0) {
  return new Promise((resolve, reject) => {
    const attempt = (remaining) => {
      fn()
        .then(resolve)
        .catch(error => {
          if (remaining <= 1) {
            reject(error);
          } else {
            setTimeout(() => {
              attempt(remaining - 1);
            }, delay);
          }
        });
    };

    attempt(times);
  });
}

// 使用示例
let attempts = 0;
const unstableTask = () => {
  attempts++;
  console.log(`Attempt ${attempts}`);
  if (attempts < 3) {
    return Promise.reject(new Error('Failed'));
  }
  return Promise.resolve('Success');
};

promiseRetry(unstableTask, 5, 500)
  .then(result => console.log(result)) // Success
  .catch(err => console.log(err.message));

// 使用 async/await 实现
async function promiseRetryAsync(fn, times, delay = 0) {
  let lastError;
  for (let i = 0; i < times; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      if (i < times - 1 && delay > 0) {
        await new Promise(r => setTimeout(r, delay));
      }
    }
  }
  throw lastError;
}
```

#### 知识点拓展

- 重试策略：固定延迟、指数退避（Exponential Backoff）、随机延迟 + 抖动（Jitter）
- 指数退避示例：`delay * Math.pow(2, attempt)` + 随机抖动
- 重试应配合**幂等性**保证，避免重复操作产生副作用

---

### 题目 7：实现 Promise 串行执行（高阶）

#### 题干

实现一个函数 `serialPromises`，接收一个返回 Promise 的函数数组，要求**按顺序串行执行**，并将结果按顺序返回。

#### 解题思路

`reduce` 或 `async/await` 循环实现：
1. 使用 `reduce` 累积 Promise 链，每次 `.then` 后执行下一个任务
2. 或使用 `for...of` 循环 `await` 每个任务

#### 正确代码实现

```javascript
// 方法一：reduce 实现
function serialPromises(tasks) {
  return tasks.reduce((prevPromise, task) => {
    return prevPromise.then(results => {
      return task().then(result => {
        results.push(result);
        return results;
      });
    });
  }, Promise.resolve([]));
}

// 方法二：async/await 实现
async function serialPromisesAsync(tasks) {
  const results = [];
  for (const task of tasks) {
    const result = await task();
    results.push(result);
  }
  return results;
}

// 使用示例
const tasks = [
  () => new Promise(r => setTimeout(() => { console.log('Task 1'); r(1); }, 300)),
  () => new Promise(r => setTimeout(() => { console.log('Task 2'); r(2); }, 100)),
  () => new Promise(r => setTimeout(() => { console.log('Task 3'); r(3); }, 200))
];

serialPromises(tasks).then(console.log);
// 输出顺序：Task 1 → Task 2 → Task 3 → [1, 2, 3]
// 即使 Task 2 的延迟更短，也得等 Task 1 完成
```

#### 知识点拓展

- 串行 vs 并行：串行保证顺序但慢，并行快但不保证顺序
- `reduce` 实现串行的本质：将 Promise 链逐步构建
- `async/await` 实现更直观，推荐在生产中使用

---

### 题目 8：微任务队列与 Promise 嵌套（高阶）

#### 题干

```javascript
Promise.resolve()
  .then(() => {
    console.log('A');
    Promise.resolve()
      .then(() => console.log('B'))
      .then(() => console.log('C'));
  })
  .then(() => console.log('D'));

console.log('E');
```

以上代码的输出是什么？为什么？

#### 解题思路

本题考察**微任务队列的嵌套执行顺序**：

1. 同步代码先执行：`E`
2. 第一个 `.then` 注册的回调进入微任务队列
3. 执行第一个 `.then` 回调，输出 `A`，内部注册 `then(B)` 进入微任务队列
4. 第一个 `.then` 回调返回 `undefined`，外部第二个 `.then` 注册 `D` 进入微任务队列
5. **关键**：微任务队列中有 `B` 和 `D`，先入先出，所以先执行 `B`
6. `B` 的 `.then` 注册 `C` 进入微任务队列
7. 执行 `D`，输出 `D`
8. 执行 `C`，输出 `C`

#### 正确代码实现

```javascript
// 输出：
// E
// A
// B
// D
// C

// 详细执行流程：
// 1. 同步：Promise.resolve() 创建已决议的 Promise
// 2. 同步：注册 then(A) → 微任务队列: [A]
// 3. 同步：console.log('E') → 输出 E
// 4. 微任务：执行 A → 输出 A
//    内部：Promise.resolve().then(B) → 微任务队列: [B]
//    外部：A 返回 undefined → 注册 then(D) → 微任务队列: [B, D]
// 5. 微任务：执行 B → 输出 B
//    内部：B 返回 undefined → 注册 then(C) → 微任务队列: [D, C]
// 6. 微任务：执行 D → 输出 D
// 7. 微任务：执行 C → 输出 C
```

#### 知识点拓展

- 微任务队列是**先进先出（FIFO）** 的
- 每次 `.then` 返回后，新注册的 `.then` 会被追加到微任务队列末尾
- 理解这个机制对分析复杂 Promise 执行顺序至关重要

---

## 三、易错点与最佳实践

### 常见易错点

| 易错点 | 错误示例 | 正确做法 |
|--------|---------|---------|
| 忘记 return Promise | `.then(() => { return fetch(url) })` 写成了 `.then(() => { fetch(url) })` | 确保 `.then` 中返回 Promise 或值 |
| 嵌套 Promise 而非链式 | `.then(() => { return p.then(...) })` | 使用链式调用 `.then().then()` |
| 在 `.then` 中直接 `throw` 非 Error | `throw 'error'` | `throw new Error('error')` |
| 忽略 `.catch` | Promise 链末尾没有 `.catch` | 始终添加 `.catch` 处理错误 |
| `new Promise` 中执行同步代码抛出异常 | 未用 `try/catch` 包裹 | 用 `try/catch` 包裹，调用 `reject` |

### 最佳实践

```javascript
// 1. 始终以 .catch 结尾
fetch('/api/data')
  .then(res => res.json())
  .then(data => process(data))
  .catch(err => console.error('Failed:', err));

// 2. async/await + try/catch 替代 Promise 链
async function fetchData() {
  try {
    const res = await fetch('/api/data');
    const data = await res.json();
    return process(data);
  } catch (err) {
    console.error('Failed:', err);
    throw err;
  }
}

// 3. 避免 Promise 嵌套（回调地狱的变体）
// ❌ 不推荐
fetch('/a').then(dataA => {
  fetch('/b').then(dataB => {
    fetch('/c').then(dataC => {});
  });
});

// ✅ 推荐
fetch('/a')
  .then(dataA => fetch('/b'))
  .then(dataB => fetch('/c'))
  .then(dataC => {});

// 4. 使用 Promise.all 并行处理独立请求
const [users, posts] = await Promise.all([
  fetch('/api/users').then(r => r.json()),
  fetch('/api/posts').then(r => r.json())
]);

// 5. 使用 AbortController 取消请求
const controller = new AbortController();
fetch('/api/data', { signal: controller.signal })
  .then(res => res.json())
  .catch(err => {
    if (err.name === 'AbortError') return;
    console.error(err);
  });
// 取消： controller.abort();
```

### Promise 状态变迁图

```
                  ┌──────────────────┐
                  │   new Promise()  │
                  └────────┬─────────┘
                           │
                    ┌──────▼──────┐
                    │   Pending   │
                    └──┬──────┬──┘
                       │      │
               resolve │      │ reject
                       │      │
              ┌────────▼─┐  ┌─▼────────┐
              │ Fulfilled │  │ Rejected │
              └────────┬──┘  └──┬───────┘
                       │        │
              .then()  │  .catch│
                       │        │
              ┌────────▼────────▼───────┐
              │    .finally()           │
              └─────────────────────────┘
```