# Node.js 基础知识完全指南

> 本文档系统性地介绍 Node.js 的核心概念、基础语法、模块系统、常用 API、异步编程模型等关键内容，适合初学者循序渐进地学习与参考。

---

## 目录

1. [Node.js 概述](#1-nodejs-概述)
2. [安装与环境配置](#2-安装与环境配置)
3. [模块系统](#3-模块系统)
4. [全局对象与变量](#4-全局对象与变量)
5. [Buffer 缓冲区](#5-buffer-缓冲区)
6. [文件系统模块 fs](#6-文件系统模块-fs)
7. [路径模块 path](#7-路径模块-path)
8. [事件模块 events](#8-事件模块-events)
9. [流 Stream](#9-流-stream)
10. [HTTP 模块](#10-http-模块)
11. [异步编程模型](#11-异步编程模型)
12. [事件循环机制](#12-事件循环机制)
13. [错误处理](#13-错误处理)
14. [包管理器 npm](#14-包管理器-npm)
15. [Process 进程对象](#15-process-进程对象)
16. [其他常用核心模块](#16-其他常用核心模块)
17. [实战示例](#17-实战示例)
18. [常见问题与最佳实践](#18-常见问题与最佳实践)

---

## 1. Node.js 概述

### 1.1 什么是 Node.js

Node.js 是一个基于 **Chrome V8 引擎**的 JavaScript 运行时（Runtime），它让 JavaScript 能够脱离浏览器在服务端运行。Node.js 由 Ryan Dahl 于 2009 年发布，使用 C++ 编写底层，封装了 V8 引擎使其能够运行在操作系统上。

```js
// 一个最简单的 Node.js 程序
console.log('Hello, Node.js!');
```

### 1.2 Node.js 的核心特点

| 特点 | 说明 |
| --- | --- |
| **事件驱动** | 通过事件监听与回调处理请求，无需为每个请求创建新线程 |
| **非阻塞 I/O** | I/O 操作不会阻塞主线程，提高并发处理能力 |
| **单线程** | 主线程为单线程，通过事件循环处理并发，避免线程切换开销 |
| **跨平台** | 支持 Windows、Linux、macOS 等主流操作系统 |
| ** npm 生态** | 拥有全球最大的开源包管理系统 |

### 1.3 Node.js 的应用场景

- **Web 服务器**：构建高性能 Web 服务（Express、Koa、NestJS）
- **API 服务**：RESTful API、GraphQL 服务
- **实时应用**：聊天室、在线协作（WebSocket、Socket.io）
- **构建工具**：Webpack、Vite、Rollup 等前端工程化工具
- **命令行工具**：脚手架、自动化脚本
- **微服务**：轻量级微服务架构
- **服务端渲染**：Next.js、Nuxt.js 等 SSR 框架

### 1.4 Node.js 运行原理

```
┌──────────────────────────────────────┐
│            JavaScript 代码            │
├──────────────────────────────────────┤
│         Node.js 核心模块              │
│   (fs / http / path / events ...)    │
├──────────────────────────────────────┤
│   V8 引擎     │     Libuv 库         │
│  (JS 编译执行) │ (事件循环/异步 I/O)  │
├──────────────────────────────────────┤
│          操作系统 (OS)                │
└──────────────────────────────────────┘
```

- **V8 引擎**：负责将 JavaScript 代码编译为机器码执行
- **Libuv**：C 语言编写的跨平台异步 I/O 库，提供事件循环、线程池（默认 4 个线程处理密集型 I/O）、网络与文件 I/O 能力

> ⚠️ 注意：Node.js 的"单线程"指的是 JavaScript 主线程单线程，底层 Libuv 仍会使用线程池处理 I/O，并非真正的"单线程"。

---

## 2. 安装与环境配置

### 2.1 安装 Node.js

推荐使用 **nvm（Node Version Manager）** 进行多版本管理：

```bash
# Windows 下载 nvm-windows
# macOS / Linux
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 安装最新 LTS 版本
nvm install --lts

# 切换版本
nvm use 18.17.0

# 查看已安装版本
nvm ls
```

### 2.2 验证安装

```bash
node -v      # 查看 Node.js 版本
npm -v       # 查看 npm 版本
```

### 2.3 运行 JavaScript 文件

```bash
# 运行文件
node app.js

# 进入 REPL 交互式环境
node

# 执行一行代码
node -e "console.log(process.version)"
```

---

## 3. 模块系统

Node.js 支持两种模块规范：**CommonJS**（默认，CJS）与 **ES Modules**（ESM）。

### 3.1 CommonJS 模块

CommonJS 是 Node.js 默认的模块规范，每个文件就是一个模块，拥有独立的作用域。

#### 3.1.1 导出模块

```js
// math.js

// 方式一：逐个导出
exports.add = function (a, b) {
  return a + b;
};
exports.sub = function (a, b) {
  return a - b;
};

// 方式二：整体导出（推荐）
module.exports = {
  add(a, b) {
    return a + b;
  },
  sub(a, b) {
    return a - b;
  },
  PI: 3.14159,
};

// 方式三：导出构造函数 / 类
module.exports = class Calculator {
  add(a, b) {
    return a + b;
  }
};
```

#### 3.1.2 引入模块

```js
// app.js
const math = require('./math');      // 引入自定义模块（需带路径）
const fs = require('fs');             // 引入核心模块（无需路径）
const express = require('express');   // 引入第三方模块（node_modules 中查找）

console.log(math.add(1, 2));          // 3
```

#### 3.1.3 `exports` 与 `module.exports` 的关系

```js
// Node.js 在每个模块顶部隐式添加：
// const exports = module.exports = {};

// ✅ 正确：给 exports 添加属性
exports.foo = 'bar';        // 等价于 module.exports.foo = 'bar'

// ❌ 错误：直接给 exports 赋值会切断引用
exports = { foo: 'bar' };   // module.exports 仍是 {}，导出失败
```

> 💡 **记忆技巧**：始终使用 `module.exports` 导出，避免出错。

#### 3.1.4 require 的加载机制

1. **缓存优先**：模块首次加载后会被缓存，再次 `require` 返回缓存对象
2. **查找顺序**：核心模块 → 文件模块（按扩展名 `.js` → `.json` → `.node`）→ 目录（`package.json` 的 `main` 字段 → `index.js`）→ `node_modules` 逐级向上查找
3. **同步加载**：`require` 是同步操作

```js
// 演示模块缓存
// counter.js
let count = 0;
module.exports = {
  increment() {
    return ++count;
  },
};

// app.js
const counterA = require('./counter');
const counterB = require('./counter'); // 返回缓存的同一个对象
console.log(counterA.increment()); // 1
console.log(counterB.increment()); // 2（共享状态）
```

### 3.2 ES Modules

ES Modules 是 ECMAScript 官方模块规范，Node.js 从 v12 开始稳定支持。

#### 3.2.1 启用 ESM

- 方式一：文件后缀使用 `.mjs`
- 方式二：在 `package.json` 中设置 `"type": "module"`

```json
{
  "name": "my-app",
  "type": "module"
}
```

#### 3.2.2 基本语法

```js
// math.mjs
export function add(a, b) {
  return a + b;
}
export const PI = 3.14159;

// 默认导出
export default class Calculator {
  static multiply(a, b) {
    return a * b;
  }
}
```

```js
// app.mjs
import Calculator, { add, PI } from './math.mjs';

console.log(add(1, 2));          // 3
console.log(Calculator.multiply(3, 4)); // 12
```

#### 3.2.3 动态导入

```js
// 按需动态加载模块
const moduleName = './math.mjs';
const math = await import(moduleName);
console.log(math.add(1, 2));
```

#### 3.2.4 CJS 与 ESM 差异对照

| 特性 | CommonJS | ES Modules |
| --- | --- | --- |
| 导出 | `module.exports` / `exports` | `export` / `export default` |
| 引入 | `require()` | `import` |
| 加载方式 | 同步、运行时 | 异步、编译时静态分析 |
| 是否支持 Tree-shaking | 否 | 是 |
| `this` 顶层指向 | `module.exports` | `undefined` |
| `__dirname` / `__filename` | 内置可用 | 需自行模拟 |

```js
// ESM 中模拟 __dirname 和 __filename
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
```

### 3.3 核心模块一览

| 模块 | 作用 |
| --- | --- |
| `fs` | 文件系统操作 |
| `path` | 路径处理 |
| `http` / `https` | HTTP 服务与客户端 |
| `url` | URL 解析 |
| `events` | 事件触发器 |
| `stream` | 流式数据处理 |
| `buffer` | 二进制数据 |
| `os` | 操作系统信息 |
| `crypto` | 加密解密 |
| `util` | 工具函数 |
| `process` | 进程对象 |
| `child_process` | 子进程 |
| `net` / `dgram` | TCP / UDP |
| `zlib` | 压缩解压 |

---

## 4. 全局对象与变量

### 4.1 global 对象

`global` 类似浏览器中的 `window`，是全局命名空间。在全局作用域中用 `var` 声明的变量会挂载到 `global` 上（但 `const` / `let` 不会）。

```js
global.myGlobal = 'Hello';
console.log(myGlobal); // 'Hello'（不推荐）

// ESM 中全局对象为 globalThis
globalThis.myGlobal = 'Hello';
```

### 4.2 __dirname 与 __filename

```js
// 假设文件路径为 /home/user/project/app.js
console.log(__dirname);  // /home/user/project（当前文件所在目录）
console.log(__filename); // /home/user/project/app.js（当前文件绝对路径）
```

### 4.3 console 对象

```js
console.log('普通日志');
console.info('信息');
console.warn('警告');
console.error('错误');

// 格式化输出
console.log('%s 是 %d 岁', 'Tom', 18);

// 计时
console.time('loop');
for (let i = 0; i < 1000000; i++) {}
console.timeEnd('loop'); // loop: 2.345ms

// 堆栈追踪
console.trace('追踪信息');

// 表格输出
console.table([
  { name: 'Tom', age: 18 },
  { name: 'Jerry', age: 20 },
]);
```

### 4.4 setTimeout / setInterval / setImmediate

```js
// 延时执行
const timer = setTimeout(() => {
  console.log('2 秒后执行');
}, 2000);
clearTimeout(timer); // 取消

// 定时执行
const interval = setInterval(() => {
  console.log('每秒执行');
}, 1000);
clearInterval(interval);

// 当前事件循环结束后立即执行
setImmediate(() => {
  console.log('immediate');
});

// 最高优先级（微任务）
process.nextTick(() => {
  console.log('nextTick');
});
```

---

## 5. Buffer 缓冲区

Buffer 是 Node.js 专门处理二进制数据的全局对象，类似整数数组，但元素大小固定为 1 字节（0-255），且不占用 V8 堆内存。

### 5.1 创建 Buffer

```js
// 从字符串创建
const buf1 = Buffer.from('Hello', 'utf8');
console.log(buf1); // <Buffer 48 65 6c 6c 6f>

// 从数组创建
const buf2 = Buffer.from([72, 101, 108, 108, 111]);

// 指定长度创建（已弃用 new Buffer，推荐 Buffer.alloc）
const buf3 = Buffer.alloc(10);          // 全部填充 0，安全
const buf4 = Buffer.allocUnsafe(10);    // 不初始化，性能更高但可能含敏感数据
```

### 5.2 Buffer 操作

```js
const buf = Buffer.from('Hello World');

// 读取
console.log(buf.length);           // 11
console.log(buf.toString());       // 'Hello World'
console.log(buf.toString('hex'));  // 十六进制
console.log(buf[0]);               // 72（'H' 的 ASCII）

// 写入
const buf2 = Buffer.alloc(10);
buf2.write('Hi');
console.log(buf2.toString()); // 'Hi'

// 拼接
const buf3 = Buffer.concat([Buffer.from('Hello '), Buffer.from('World')]);
console.log(buf3.toString()); // 'Hello World'

// 截取（返回新 Buffer，共享内存）
const sub = buf.subarray(0, 5);
console.log(sub.toString()); // 'Hello'

// 复制
const copy = Buffer.alloc(5);
buf.copy(copy, 0, 0, 5);
```

### 5.3 Buffer 与编码

```js
const str = '你好';

console.log(Buffer.byteLength(str, 'utf8'));  // 6（每个中文 3 字节）
console.log(Buffer.from(str, 'utf8').toString('base64')); // 5L2g5aW9

// 常见编码：utf8 / base64 / hex / ascii / latin1 / ucs2
```

---

## 6. 文件系统模块 fs

`fs` 模块提供文件读写能力，几乎所有 API 都有**同步**与**异步**两个版本。

### 6.1 异步与同步 API 对照

```js
const fs = require('fs');

// 异步（推荐，不阻塞）
fs.readFile('./test.txt', 'utf8', (err, data) => {
  if (err) throw err;
  console.log(data);
});

// 同步（阻塞，慎用）
try {
  const data = fs.readFileSync('./test.txt', 'utf8');
  console.log(data);
} catch (err) {
  console.error(err);
}
```

### 6.2 Promise API（推荐）

```js
const fs = require('fs').promises;
// 或 const fsp = require('fs/promises');

async function readFile() {
  try {
    const data = await fs.readFile('./test.txt', 'utf8');
    console.log(data);
  } catch (err) {
    console.error(err);
  }
}
```

### 6.3 文件操作

```js
const fs = require('fs').promises;

// 写入文件（覆盖）
await fs.writeFile('./msg.txt', 'Hello World');

// 追加写入
await fs.appendFile('./msg.txt', '\nNew Line');

// 判断是否存在（推荐 access，避免 stat 开销）
try {
  await fs.access('./msg.txt');
  console.log('存在');
} catch {
  console.log('不存在');
}

// 删除文件
await fs.unlink('./msg.txt');

// 复制文件
await fs.copyFile('./src.txt', './dest.txt');

// 重命名 / 移动
await fs.rename('./old.txt', './new.txt');

// 获取文件信息
const stats = await fs.stat('./msg.txt');
console.log(stats.isFile());      // true
console.log(stats.isDirectory()); // false
console.log(stats.size);          // 文件大小（字节）
console.log(stats.mtime);         // 修改时间
```

### 6.4 目录操作

```js
const fs = require('fs').promises;
const path = require('path');

// 创建目录（recursive 递归创建）
await fs.mkdir('./a/b/c', { recursive: true });

// 读取目录
const files = await fs.readdir('./');
console.log(files); // ['a', 'b.txt', ...]

// 递归遍历目录
async function walk(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const result = [];
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      result.push(...(await walk(fullPath)));
    } else {
      result.push(fullPath);
    }
  }
  return result;
}

// 删除目录（递归）
await fs.rm('./a', { recursive: true, force: true });
```

### 6.5 文件监听

```js
const fs = require('fs');

// 监听文件变化
fs.watch('./msg.txt', (eventType, filename) => {
  console.log(`${filename} ${eventType}`);
});

// 监听目录
fs.watch('./', { recursive: true }, (eventType, filename) => {
  console.log(`${filename} changed`);
});
```

---

## 7. 路径模块 path

`path` 模块用于处理和转换文件路径，跨平台兼容（自动处理 Windows 的 `\` 与 POSIX 的 `/`）。

```js
const path = require('path');

// 路径拼接（推荐，避免手动拼接字符串）
const full = path.join('/user', 'local', 'bin');
console.log(full); // /user/local/bin（Windows 下为 \user\local\bin）

// 解析为绝对路径
console.log(path.resolve('foo', 'bar')); // /当前目录/foo/bar
console.log(path.resolve('/a', 'b', 'c')); // /a/b/c

// 解析路径组成
const parsed = path.parse('/home/user/file.txt');
console.log(parsed);
// {
//   root: '/',
//   dir: '/home/user',
//   base: 'file.txt',
//   ext: '.txt',
//   name: 'file'
// }

// 路径组成部分
console.log(path.dirname('/a/b/c.txt')); // /a/b
console.log(path.basename('/a/b/c.txt')); // c.txt
console.log(path.basename('/a/b/c.txt', '.txt')); // c
console.log(path.extname('c.txt')); // .txt

// 拼接路径片段
console.log(path.format({
  dir: '/home/user',
  base: 'file.txt'
})); // /home/user/file.txt

// 相对路径
console.log(path.relative('/a/b/c', '/a/d')); // ../../d

// 规范化路径（处理 .. 和 .）
console.log(path.normalize('/a/b/../c/./d')); // /a/c/d

// 跨平台分隔符
console.log(path.sep);           // Linux: '/'，Windows: '\'
console.log(path.delimiter);     // Linux: ':'，Windows: ';'
console.log(path.posix.sep);     // '/'
console.log(path.win32.sep);     // '\'
```

---

## 8. 事件模块 events

`events` 模块是 Node.js 事件驱动的核心，提供了 `EventEmitter` 类，多数核心模块（如 `http`、`fs`、`stream`）都继承自它。

### 8.1 基本用法

```js
const EventEmitter = require('events');
const emitter = new EventEmitter();

// 注册监听器
emitter.on('greet', (name) => {
  console.log(`Hello, ${name}!`);
});

// 注册一次性监听器（触发后自动移除）
emitter.once('connect', () => {
  console.log('已连接');
});

// 触发事件
emitter.emit('greet', 'Tom');   // Hello, Tom!
emitter.emit('connect');        // 已连接
emitter.emit('connect');        // （无输出，已移除）
```

### 8.2 监听器管理

```js
const emitter = new EventEmitter();

function listener1() { console.log('L1'); }
function listener2() { console.log('L2'); }

emitter.on('data', listener1);
emitter.on('data', listener2);

// 查询监听器数量
console.log(emitter.listenerCount('data')); // 2
console.log(emitter.listeners('data'));     // [ [Function: listener1], [Function: listener2] ]

// 移除监听器
emitter.off('data', listener1); // 等价于 emitter.removeListener
emitter.removeAllListeners('data'); // 移除所有
```

### 8.3 同步执行与错误处理

```js
const emitter = new EventEmitter();

// 监听器按注册顺序同步执行
emitter.on('event', () => console.log('first'));
emitter.on('event', () => console.log('second'));
emitter.emit('event');
// 输出：
// first
// second

// 'error' 事件：若无监听器，触发时会抛出并使进程崩溃
emitter.on('error', (err) => {
  console.error('捕获错误：', err.message);
});
emitter.emit('error', new Error('出错了')); // 会被上面的监听器捕获
```

### 8.4 继承 EventEmitter

```js
const EventEmitter = require('events');

class UserStore extends EventEmitter {
  constructor() {
    super();
    this.users = [];
  }

  add(user) {
    this.users.push(user);
    this.emit('added', user);            // 触发事件
  }
}

const store = new UserStore();
store.on('added', (user) => console.log('用户添加：', user));
store.add({ name: 'Tom' });
```

---

## 9. 流 Stream

Stream 是处理流式数据的抽象接口，适用于**大文件、网络数据**等分块传输场景，能避免一次性将数据全部加载到内存。

### 9.1 四种流类型

| 类型 | 说明 | 示例 |
| --- | --- | --- |
| **Readable** 可读流 | 数据源，可从中读取 | `fs.createReadStream`、HTTP 请求 |
| **Writable** 可写流 | 数据终点，可向其写入 | `fs.createWriteStream`、HTTP 响应 |
| **Duplex** 双工流 | 同时可读可写（独立通道） | TCP Socket |
| **Transform** 转换流 | 读写过程中转换数据 | `zlib.createGzip()` |

### 9.2 可读流

```js
const fs = require('fs');

const rs = fs.createReadStream('./bigfile.txt', {
  encoding: 'utf8',
  highWaterMark: 64 * 1024, // 缓冲区大小（64KB）
});

// 数据事件模式
rs.on('data', (chunk) => {
  console.log('收到数据：', chunk.length);
});

rs.on('end', () => {
  console.log('读取完成');
});

rs.on('error', (err) => {
  console.error('出错：', err);
});

// 暂停 / 恢复
rs.pause();
rs.resume();
```

#### 9.2.1 使用 async迭代 读取（推荐）

```js
const fs = require('fs');

async function readStream() {
  const rs = fs.createReadStream('./bigfile.txt', 'utf8');
  for await (const chunk of rs) {
    console.log('收到：', chunk.length);
  }
  console.log('完成');
}
```

### 9.3 可写流

```js
const fs = require('fs');

const ws = fs.createWriteStream('./output.txt');

ws.write('第一行\n');
ws.write('第二行\n');

ws.end('结束'); // 必须调用 end() 才会真正写入完成

ws.on('finish', () => {
  console.log('写入完成');
});

ws.on('error', (err) => {
  console.error('出错：', err);
});
```

### 9.4 管道 pipe

`pipe` 方法把可读流直接接到可写流，自动处理背压（backpressure）问题。

```js
const fs = require('fs');
const zlib = require('zlib');

// 文件复制
fs.createReadStream('./input.txt')
  .pipe(fs.createWriteStream('./output.txt'))
  .on('finish', () => console.log('复制完成'));

// 文件压缩
fs.createReadStream('./input.txt')
  .pipe(zlib.createGzip())
  .pipe(fs.createWriteStream('./input.txt.gz'))
  .on('finish', () => console.log('压缩完成'));
```

### 9.5 自定义流

```js
const { Transform } = require('stream');

// 自定义转换流：将数据转为大写
const upperCase = new Transform({
  transform(chunk, encoding, callback) {
    this.push(chunk.toString().toUpperCase());
    callback();
  },
});

process.stdin.pipe(upperCase).pipe(process.stdout);
```

---

## 10. HTTP 模块

`http` 模块允许 Node.js 创建 Web 服务器和发起 HTTP 请求。

### 10.1 创建 HTTP 服务器

```js
const http = require('http');

const server = http.createServer((req, res) => {
  // req: IncomingMessage（可读流）
  // res: ServerResponse（可写流）

  // 设置响应头
  res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });

  // 路由分发
  const { method, url } = req;
  if (url === '/' && method === 'GET') {
    res.end(JSON.stringify({ message: '欢迎来到首页' }));
  } else if (url === '/users' && method === 'GET') {
    res.end(JSON.stringify([{ id: 1, name: 'Tom' }]));
  } else {
    res.writeHead(404);
    res.end('Not Found');
  }
});

server.listen(3000, () => {
  console.log('服务器运行于 http://localhost:3000');
});
```

### 10.2 接收 POST 请求体

```js
const server = http.createServer(async (req, res) => {
  if (req.method === 'POST') {
    let body = '';
    for await (const chunk of req) {
      body += chunk;
    }
    console.log('收到：', body);
    res.end('OK');
  }
});
```

### 10.3 发起 HTTP 请求

```js
const http = require('http');

// 方式一：原生 http
http.get('http://localhost:3000/users', (res) => {
  let data = '';
  res.on('data', (chunk) => (data += chunk));
  res.on('end', () => console.log(data));
}).on('error', (err) => console.error(err));

// 方式二：POST 请求
const postData = JSON.stringify({ name: 'Tom' });

const req = http.request(
  {
    hostname: 'localhost',
    port: 3000,
    path: '/users',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(postData),
    },
  },
  (res) => {
    let data = '';
    res.on('data', (c) => (data += c));
    res.on('end', () => console.log(data));
  }
);

req.write(postData);
req.end();
```

> 💡 **实践建议**：生产环境推荐使用 `fetch`（Node 18+ 内置）或第三方库 `axios`，API 更简洁。

```js
// Node 18+ 内置 fetch
const res = await fetch('http://localhost:3000/users');
const data = await res.json();
console.log(data);
```

---

## 11. 异步编程模型

异步编程是 Node.js 的核心，常见方案演进：**回调函数 → Promise → async/await**。

### 11.1 回调函数

```js
const fs = require('fs');

// 回调函数签名约定：第一个参数为错误，后续为结果
fs.readFile('./file.txt', 'utf8', (err, data) => {
  if (err) return console.error(err);
  console.log(data);
});
```

#### 11.1.1 回调地狱

```js
// ❌ 丑陋的回调地狱
getUser(userId, (err, user) => {
  if (err) return handleError(err);
  getOrders(user.id, (err, orders) => {
    if (err) return handleError(err);
    getOrderDetail(orders[0].id, (err, detail) => {
      if (err) return handleError(err);
      console.log(detail);
    });
  });
});
```

### 11.2 Promise

Promise 表示一个异步操作的最终结果，有三种状态：`pending`（进行中）、`fulfilled`（已成功）、`rejected`（已失败）。

```js
// 创建 Promise
function readFile(path) {
  return new Promise((resolve, reject) => {
    fs.readFile(path, 'utf8', (err, data) => {
      if (err) reject(err);
      else resolve(data);
    });
  });
}

// 链式调用解决回调地狱
readFile('./user.txt')
  .then((user) => getOrders(user.id))
  .then((orders) => getOrderDetail(orders[0].id))
  .then((detail) => console.log(detail))
  .catch((err) => console.error(err))
  .finally(() => console.log('完成'));
```

#### 11.2.1 Promise 静态方法

```js
// 全部成功才成功（任一失败即失败）
const [a, b] = await Promise.all([fetchA(), fetchB()]);

// 任一成功即成功（返回最先的结果）
const first = await Promise.any([fetchA(), fetchB()]);

// 全部完成（无论成败），返回状态数组
const results = await Promise.allSettled([fetchA(), fetchB()]);
// [{ status: 'fulfilled', value: ... }, { status: 'rejected', reason: ... }]

// 任一完成即返回（无论成败）
const result = await Promise.race([fetchA(), timeout(5000)]);
```

### 11.3 async / await

`async/await` 是 Promise 的语法糖，让异步代码看起来像同步代码。

```js
async function getOrderDetail(userId) {
  try {
    const user = await getUser(userId);          // await 自动等待 Promise 完成
    const orders = await getOrders(user.id);
    const detail = await getOrderDetail(orders[0].id);
    return detail;
  } catch (err) {
    console.error('出错：', err);
    throw err; // 可重新抛出
  }
}

// 调用
getOrderDetail(1).then(console.log).catch(console.error);
```

#### 11.3.1 并发执行多个 await

```js
// ❌ 串行执行，速度慢
const a = await fetchA();
const b = await fetchB();

// ✅ 并发执行（推荐）
const [a, b] = await Promise.all([fetchA(), fetchB()]);
```

#### 11.3.2 for await of 遍历异步集合

```js
const urls = [url1, url2, url3];

// 串行异步遍历
for await (const url of urls) {
  const data = await fetch(url);
  console.log(data);
}
```

### 11.4 util.promisify

将遵循 `(err, result) => {}` 回调风格的函数转为 Promise 风格。

```js
const util = require('util');
const fs = require('fs');

const readFile = util.promisify(fs.readFile);

(async () => {
  const data = await readFile('./file.txt', 'utf8');
  console.log(data);
})();
```

---

## 12. 事件循环机制

事件循环是 Node.js 异步能力的核心，它负责调度异步任务的执行。

### 12.1 事件循环阶段

```
┌───────────────────────────┐
├─► 1. timers               │  执行 setTimeout / setInterval 回调
│   ┌─────────────────────┐ │
│   │ 2. pending callbacks │ │  执行系统级回调（如 TCP 错误）
│   └─────────────────────┘ │
│   ┌─────────────────────┐ │
│   │ 3. idle, prepare    │ │  内部使用
│   └─────────────────────┘ │
│   ┌─────────────────────┐ │
│   │ 4. poll             │ │  获取新 I/O 事件，执行 I/O 回调
│   └─────────────────────┘ │
│   ┌─────────────────────┐ │
│   │ 5. check            │ │  执行 setImmediate 回调
│   └─────────────────────┘ │
│   ┌─────────────────────┐ │
│   │ 6. close callbacks  │ │  执行 close 事件（socket.on('close')）
│   └─────────────────────┘ │
└───────────────────────────┘
```

### 12.2 微任务与宏任务

Node.js 中的任务分两类：

- **微任务（Microtask）**：`process.nextTick`、`Promise.then`、`queueMicrotask`
- **宏任务（Macrotask）**：`setTimeout`、`setInterval`、`setImmediate`、I/O 回调

> **执行顺序**：每个阶段切换之间，都会清空所有微任务队列，且 `process.nextTick` 优先级高于 `Promise.then`。

### 12.3 经典面试题

```js
console.log('1');

setTimeout(() => console.log('2'), 0);

Promise.resolve().then(() => console.log('3'));

process.nextTick(() => console.log('4'));

setImmediate(() => console.log('5'));

console.log('6');

// 输出顺序：1 6 4 3 2 5
// 解析：
// 1. 同步代码：1, 6
// 2. 微任务（nextTick 优先于 Promise）：4, 3
// 3. 宏任务（timers 阶段先于 check 阶段）：2, 5
```

### 12.4 setTimeout 与 setImmediate 的顺序

```js
// 在主模块中两者顺序不确定（取决于 1ms 计时器是否触发）
setTimeout(() => console.log('timeout'), 0);
setImmediate(() => console.log('immediate'));

// 在 I/O 回调中 setImmediate 一定先于 setTimeout
fs.readFile('./file.txt', () => {
  setTimeout(() => console.log('timeout'), 0);
  setImmediate(() => console.log('immediate')); // 一定先输出
});
```

---

## 13. 错误处理

### 13.1 同步错误

```js
try {
  const data = JSON.parse('invalid json');
} catch (err) {
  console.error('解析失败：', err.message);
}
```

### 13.2 异步错误

#### 13.2.1 回调风格

```js
fs.readFile('./file.txt', (err, data) => {
  if (err) {
    console.error(err);
    return;
  }
  console.log(data);
});
```

#### 13.2.2 Promise + async/await

```js
async function read() {
  try {
    const data = await fs.promises.readFile('./file.txt', 'utf8');
    console.log(data);
  } catch (err) {
    console.error('文件读取失败：', err.message);
  } finally {
    console.log('清理资源');
  }
}
```

### 13.3 事件错误

```js
const emitter = new EventEmitter();

// 必须监听 'error' 事件，否则触发时会抛出使进程崩溃
emitter.on('error', (err) => {
  console.error('捕获错误：', err.message);
});

emitter.emit('error', new Error('自定义错误'));
```

### 13.4 未捕获异常处理

```js
// 捕获未处理的同步异常
process.on('uncaughtException', (err) => {
  console.error('未捕获异常：', err);
  // 建议记录日志后退出，避免应用处于不确定状态
  process.exit(1);
});

// 捕获未处理的 Promise 拒绝
process.on('unhandledRejection', (reason, promise) => {
  console.error('未处理的 Promise 拒绝：', reason);
});
```

### 13.5 自定义错误

```js
class ValidationError extends Error {
  constructor(message, field) {
    super(message);
    this.name = 'ValidationError';
    this.field = field;
  }
}

function validateUser(user) {
  if (!user.name) {
    throw new ValidationError('用户名不能为空', 'name');
  }
}

try {
  validateUser({});
} catch (err) {
  if (err instanceof ValidationError) {
    console.error(`字段 ${err.field} 校验失败：${err.message}`);
  } else {
    throw err;
  }
}
```

---

## 14. 包管理器 npm

### 14.1 初始化项目

```bash
# 交互式创建 package.json
npm init

# 快速创建（使用默认值）
npm init -y
```

### 14.2 package.json 详解

```jsonc
{
  "name": "my-app",                 // 包名（小写、无空格）
  "version": "1.0.0",               // 语义化版本号
  "description": "项目描述",
  "main": "index.js",               // 入口文件（CJS）
  "type": "commonjs",               // 模块类型：commonjs | module
  "scripts": {                      // 自定义脚本
    "start": "node app.js",
    "dev": "nodemon app.js",
    "test": "jest"
  },
  "keywords": ["node", "demo"],
  "author": "Tom <tom@example.com>",
  "license": "MIT",
  "dependencies": {                 // 生产依赖
    "express": "^4.18.2"
  },
  "devDependencies": {              // 开发依赖（不打包进生产）
    "nodemon": "^3.0.0",
    "jest": "^29.0.0"
  },
  "engines": {                      // 运行环境要求
    "node": ">=18.0.0"
  },
  "private": true                   // 防止意外发布到 npm
}
```

### 14.3 常用 npm 命令

```bash
# 安装依赖
npm install                  # 安装 package.json 中所有依赖
npm install express          # 安装 express（写入 dependencies）
npm install express --save   # 同上（npm 5+ 默认 --save）
npm install -D nodemon       # 安装到 devDependencies
npm install -g pm2           # 全局安装

# 卸载
npm uninstall express

# 更新
npm update express

# 查看包信息
npm view express version     # 查看最新版本
npm list                     # 查看已安装依赖树
npm list --depth=0           # 只看顶层依赖
npm outdated                 # 查看过时的包

# 运行脚本
npm run dev                  # 运行 scripts 中的命令
npm start                    # start / test / restart 可省略 run

# 清理缓存
npm cache clean --force

# 审计安全漏洞
npm audit
npm audit fix
```

### 14.4 语义化版本号 semver

格式：`主版本.次版本.修订版本`（`Major.Minor.Patch`）

| 符号 | 含义 | 示例 |
| --- | --- | --- |
| `^` | 允许次版本和修订版本升级（默认） | `^1.2.3` → `>=1.2.3 <2.0.0` |
| `~` | 只允许修订版本升级 | `~1.2.3` → `>=1.2.3 <1.3.0` |
| `*` | 任意版本 | `*` |
| `=` | 精确版本 | `=1.2.3` |
| `>` `>=` `<` `<=` | 范围比较 | `>=1.2.3` |

> - **主版本号（Major）**：不兼容的 API 修改
> - **次版本号（Minor）**：向下兼容的功能新增
> - **修订号（Patch）**：向下兼容的缺陷修复

### 14.5 package-lock.json

`package-lock.json` 记录了依赖树的精确版本和下载地址，确保不同环境安装的依赖完全一致。**应提交到版本控制系统**。

### 14.6 npx 命令

`npx` 用于执行本地或远程包，无需先全局安装。

```bash
# 执行 create-react-app（无需先安装）
npx create-react-app my-app

# 执行本地 node_modules/.bin 中的命令
npx eslint .
```

---

## 15. Process 进程对象

`process` 是全局对象，提供当前 Node.js 进程的信息与控制能力。

### 15.1 进程信息

```js
console.log(process.version);       // Node.js 版本
console.log(process.platform);      // 平台：darwin / linux / win32
console.log(process.arch);          // CPU 架构：x64 / arm64
console.log(process.pid);           // 进程 ID
console.log(process.cwd());         // 当前工作目录
console.log(process.memoryUsage()); // 内存占用
console.log(process.cpuUsage());    // CPU 占用
console.log(process.uptime());      // 进程运行时长（秒）
```

### 15.2 环境变量

```js
// 读取环境变量
console.log(process.env.NODE_ENV);
console.log(process.env.PATH);

// 设置环境变量（跨平台推荐 cross-env 包）
// Linux/macOS: NODE_ENV=production node app.js
// Windows: set NODE_ENV=production && node app.js

// 使用 cross-env
// package.json: "start": "cross-env NODE_ENV=production node app.js"
```

### 15.3 命令行参数

```js
// 执行：node app.js --name Tom --age 18 extra
console.log(process.argv);
// [
//   'C:\\...\\node.exe',       // node 路径
//   'M:\\...\\app.js',         // 脚本路径
//   '--name', 'Tom',
//   '--age', '18',
//   'extra'
// ]

// 推荐使用 minimist / yargs / commander 解析参数
```

### 15.4 标准输入输出

```js
// stdout / stderr 是可写流
process.stdout.write('标准输出\n');
process.stderr.write('错误输出\n');

// stdin 是可读流
process.stdin.on('data', (data) => {
  console.log('收到输入：', data.toString().trim());
});

// 退出进程
process.exit(0);  // 0 表示成功
process.exit(1);  // 非 0 表示失败

// 退出前钩子
process.on('exit', (code) => {
  console.log(`进程退出，退出码：${code}`);
  // 此回调中只能执行同步操作
});
```

### 15.5 信号事件

```js
// Ctrl + C 触发
process.on('SIGINT', () => {
  console.log('收到 SIGINT，准备退出');
  process.exit(0);
});

// kill 命令默认发送
process.on('SIGTERM', () => {
  console.log('收到 SIGTERM，优雅关闭');
  server.close(() => process.exit(0));
});
```

---

## 16. 其他常用核心模块

### 16.1 os 模块

```js
const os = require('os');

console.log(os.platform());     // 平台
console.log(os.arch());         // CPU 架构
console.log(os.cpus());         // CPU 信息数组
console.log(os.hostname());     // 主机名
console.log(os.totalmem());     // 总内存（字节）
console.log(os.freemem());      // 空闲内存
console.log(os.uptime());       // 系统运行时间（秒）
console.log(os.homedir());      // 用户主目录
console.log(os.tmpdir());       // 临时目录
console.log(os.networkInterfaces()); // 网络接口
```

### 16.2 url 模块

```js
// 传统 API（已部分弃用）
const url = require('url');
const parsed = url.parse('https://user:pass@host:8080/path?q=1#hash');
console.log(parsed.pathname); // /path

// WHATWG URL API（推荐）
const myURL = new URL('https://user:pass@host:8080/path?q=1#hash');
console.log(myURL.hostname); // host
console.log(myURL.pathname); // /path
console.log(myURL.searchParams.get('q')); // 1

// 修改 URL
myURL.searchParams.append('page', '2');
console.log(myURL.href);
```

### 16.3 crypto 模块

```js
const crypto = require('crypto');

// 哈希
const hash = crypto.createHash('sha256').update('hello').digest('hex');
console.log(hash);

// HMAC
const hmac = crypto.createHmac('sha256', 'secret').update('hello').digest('hex');

// 随机字节
const bytes = crypto.randomBytes(16);
console.log(bytes.toString('hex'));

// AES 对称加密
const algorithm = 'aes-256-cbc';
const key = crypto.randomBytes(32);
const iv = crypto.randomBytes(16);

const cipher = crypto.createCipheriv(algorithm, key, iv);
let encrypted = cipher.update('hello', 'utf8', 'hex');
encrypted += cipher.final('hex');

const decipher = crypto.createDecipheriv(algorithm, key, iv);
let decrypted = decipher.update(encrypted, 'hex', 'utf8');
decrypted += decipher.final('utf8');
console.log(decrypted); // hello
```

### 16.4 util 模块

```js
const util = require('util');

// promisify：回调风格转 Promise
const readFile = util.promisify(fs.readFile);

// callbackify：Promise 转回调
const cbReadFile = util.callbackify(readFile);

// inspect：格式化对象
console.log(util.inspect({ a: 1 }, { depth: null, colors: true }));

// format：格式化字符串
console.log(util.format('%s:%d', 'port', 3000));

// isDeepStrictEqual：深度严格相等
console.log(util.isDeepStrictEqual({ a: 1 }, { a: 1 })); // true

// types：类型判断
console.log(util.types.isPromise(Promise.resolve())); // true
console.log(util.types.isMap(new Map()));              // true
```

### 16.5 child_process 模块

```js
const { exec, execFile, spawn, fork } = require('child_process');

// exec：执行 shell 命令，缓冲输出
exec('ls -la', (err, stdout, stderr) => {
  if (err) return console.error(err);
  console.log(stdout);
});

// spawn：流式输出，适合大量数据
const ls = spawn('ls', ['-la']);
ls.stdout.on('data', (data) => console.log(data.toString()));
ls.on('close', (code) => console.log(`退出码：${code}`));

// fork：创建 Node 子进程，可与父进程通信
const child = fork('./child.js');
child.send({ msg: 'hello' });
child.on('message', (msg) => console.log('父进程收到：', msg));
```

---

## 17. 实战示例

### 17.1 静态文件服务器

```js
const http = require('http');
const fs = require('fs');
const path = require('path');

const MIME = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'text/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.gif': 'image/gif',
};

const server = http.createServer((req, res) => {
  let filePath = path.join(__dirname, 'public', req.url === '/' ? 'index.html' : req.url);
  const ext = path.extname(filePath);

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('404 Not Found');
      return;
    }
    res.writeHead(200, { 'Content-Type': (MIME[ext] || 'text/plain') + '; charset=utf-8' });
    res.end(data);
  });
});

server.listen(3000, () => console.log('服务器运行于 http://localhost:3000'));
```

### 17.2 使用流的大文件复制

```js
const fs = require('fs');

// 流式复制（内存友好，适合大文件）
function copyFile(src, dest) {
  return new Promise((resolve, reject) => {
    fs.createReadStream(src)
      .pipe(fs.createWriteStream(dest))
      .on('finish', resolve)
      .on('error', reject);
  });
}

copyFile('./bigfile.mp4', './copy.mp4')
  .then(() => console.log('复制完成'))
  .catch(console.error);
```

### 17.3 简单 RESTful API

```js
const http = require('http');
const users = [{ id: 1, name: 'Tom' }];

const server = http.createServer(async (req, res) => {
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  const { method, url } = req;

  // GET /users
  if (url === '/users' && method === 'GET') {
    res.end(JSON.stringify(users));
    return;
  }

  // POST /users
  if (url === '/users' && method === 'POST') {
    let body = '';
    for await (const chunk of req) body += chunk;
    const user = JSON.parse(body);
    user.id = users.length + 1;
    users.push(user);
    res.writeHead(201);
    res.end(JSON.stringify(user));
    return;
  }

  res.writeHead(404);
  res.end(JSON.stringify({ error: 'Not Found' }));
});

server.listen(3000, () => console.log('API 服务运行于 http://localhost:3000'));
```

### 17.4 命令行工具：统计项目代码行数

```js
#!/usr/bin/env node
const fs = require('fs').promises;
const path = require('path');

async function countLines(dir, ext = '.js') {
  let total = 0;
  const entries = await fs.readdir(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory() && !['node_modules', '.git'].includes(entry.name)) {
      total += await countLines(fullPath, ext);
    } else if (entry.isFile() && entry.name.endsWith(ext)) {
      const content = await fs.readFile(fullPath, 'utf8');
      total += content.split('\n').length;
      console.log(`${entry.name}: ${content.split('\n').length} 行`);
    }
  }
  return total;
}

(async () => {
  const total = await countLines(process.cwd());
  console.log(`\n总计：${total} 行`);
})();
```

---

## 18. 常见问题与最佳实践

### 18.1 性能优化

- **使用流处理大文件**：避免 `readFile` 一次性读入内存
- **合理使用缓存**：对重复计算结果进行缓存
- **避免同步 API**：在 Web 服务中禁用 `*Sync` 方法
- **使用 cluster 模块**：充分利用多核 CPU
- **监控内存**：注意内存泄漏，使用 `--max-old-space-size` 调整堆大小

```js
// cluster 多进程示例
const cluster = require('cluster');
const os = require('os');

if (cluster.isPrimary) {
  for (let i = 0; i < os.cpus().length; i++) {
    cluster.fork();
  }
} else {
  // 每个 worker 运行一个 http 服务
  require('./app');
}
```

### 18.2 安全实践

- **校验用户输入**：防止 SQL 注入、XSS、命令注入
- **使用 helmet**：设置安全响应头
- **HTTPS**：生产环境必须使用 HTTPS
- **依赖审计**：定期 `npm audit`
- **限制请求体大小**：防止 DoS 攻击
- **不信任前端**：服务端必须重新校验

### 18.3 项目结构建议

```
my-app/
├── src/
│   ├── controllers/    # 控制器
│   ├── services/       # 业务逻辑
│   ├── models/         # 数据模型
│   ├── routes/         # 路由
│   ├── middlewares/    # 中间件
│   ├── utils/          # 工具函数
│   └── app.js          # 入口
├── tests/              # 测试
├── public/             # 静态资源
├── .env                # 环境变量
├── .gitignore
├── package.json
└── README.md
```

### 18.4 调试技巧

```bash
# 启用 inspector，配合 Chrome DevTools 调试
node --inspect app.js
node --inspect-brk app.js   # 第一行断点

# 使用 VS Code 调试：创建 .vscode/launch.json
```

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "启动程序",
      "program": "${workspaceFolder}/app.js"
    }
  ]
}
```

### 18.5 常见陷阱

| 陷阱 | 说明 | 解决方案 |
| --- | --- | --- |
| 回调未处理错误 | 异步回调中忽略 err 参数 | 始终检查 err |
| Promise 未 catch | Promise 链未捕获 reject | 末尾加 `.catch()` 或 `try/catch` |
| `exports` 赋值 | `exports = {...}` 切断引用 | 使用 `module.exports` |
| 同步阻塞主线程 | 大量计算阻塞事件循环 | 拆分任务、用 Worker |
| 内存泄漏 | 闭包、定时器、事件监听器未清理 | 及时 `clearTimeout`、`removeListener` |
| 路径硬编码 | 拼接字符串导致跨平台问题 | 使用 `path.join` / `path.resolve` |
| 大文件 readFile | 一次性读入内存 OOM | 使用 Stream |

### 18.6 学习路线建议

1. **入门**：JavaScript 基础 → Node.js 安装运行 → 模块系统 → fs/path/http
2. **进阶**：异步编程（Promise/async）→ 事件循环 → Stream → 错误处理
3. **实战**：Express/Koa 框架 → 数据库（MySQL/MongoDB）→ 身份认证 → 部署
4. **深入**：源码阅读（Libuv/V8）→ 性能优化 → 微服务 → NestJS

---

## 附录：常用快捷参考

### A. Node.js 版本与特性

| 版本 | 重要特性 |
| --- | --- |
| v12 | ESM 稳定支持、worker_threads |
| v14 | 顶层 await（ESM）、可选链 |
| v16 | Apple Silicon 支持、Timers Promises API |
| v18 | 内置 fetch、Web Streams API、Test Runner |
| v20 | 单可执行应用（SEA）、权限模型 |
| v22 | 内置 WebSocket 客户端、`require()` 支持 ESM |

### B. 推荐学习资源

- [Node.js 官方文档](https://nodejs.org/zh-cn/docs/)
- [Node.js 最佳实践](https://github.com/goldbergyoni/nodebestpractices)
- [The Art of Node](https://github.com/maxogden/art-of-node)

---

> 📌 **结语**：Node.js 的核心在于理解**事件循环**与**异步编程**。掌握这两点后，配合核心模块的熟练使用，即可应对绝大多数服务端开发场景。建议边学边练，多动手实现小型项目以巩固知识。
