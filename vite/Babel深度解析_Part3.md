# 八、自定义插件开发

自定义插件是 Babel 最强大的能力之一。通过编写插件，我们可以在编译期对代码做任意变换：自动埋点、去除 `console`、国际化文案提取、代码注入、API 转换、安全检查等。

---

## 8.1 插件基本结构

一个 Babel 插件本质上是一个返回 **Visitor 对象** 的函数。

### 最简插件骨架

```js
// babel-plugin-my-plugin.js
module.exports = function myPlugin(babel) {
  // babel 提供 types 工具，用于构造/判断 AST 节点
  const { types: t } = babel;

  return {
    name: 'my-plugin',
    visitor: {
      // 访问 Identifier 节点
      Identifier(path) {
        console.log('Found identifier:', path.node.name);
      },
    },
  };
};
```

### 插件元信息

```js
module.exports = function ({ types: t }) {
  return {
    name: 'babel-plugin-example',
    // pre 在遍历开始前执行
    pre(state) {
      this.counter = 0;
    },
    visitor: {
      FunctionDeclaration(path) {
        this.counter++;
      },
    },
    // post 在遍历结束后执行
    post(state) {
      console.log('Total functions:', this.counter);
    },
  };
};
```

### 插件接收选项

```js
// babel.config.js
module.exports = {
  plugins: [
    ['./babel-plugin-my-plugin', { optionA: true, optionB: 'foo' }],
  ],
};

// babel-plugin-my-plugin.js
module.exports = function ({ types: t }) {
  return {
    visitor: {
      Program(path, state) {
        const opts = state.opts; // { optionA: true, optionB: 'foo' }
        if (opts.optionA) {
          // ...
        }
      },
    },
  };
};
```

---

## 8.2 实战：自动埋点插件

**目标**：自动在函数入口插入埋点函数调用 `__track__('函数名')`。

### 转换效果

```js
// 输入
function handleClick() {
  console.log('clicked');
}
const onSubmit = () => { submit(); };

// 输出
function handleClick() {
  __track__('handleClick');
  console.log('clicked');
}
const onSubmit = () => {
  __track__('onSubmit');
  submit();
};
```

### 完整实现

```js
// babel-plugin-auto-track.js
module.exports = function ({ types: t }) {
  return {
    name: 'auto-track',
    visitor: {
      // 函数声明：function foo() {}
      FunctionDeclaration(path) {
        const name = path.node.id?.name;
        if (!name) return;
        insertTrackCall(path, name);
      },
      // 箭头函数赋值：const foo = () => {}
      VariableDeclarator(path) {
        if (
          t.isArrowFunctionExpression(path.node.init) ||
          t.isFunctionExpression(path.node.init)
        ) {
          const name = path.node.id?.name;
          if (!name) return;
          // 拿到函数 body 所在的 path
          const bodyPath = path.get('init.body');
          insertTrackCall(bodyPath, name);
        }
      },
      // 对象方法：{ foo() {} }
      ObjectMethod(path) {
        const name = path.node.key?.name;
        if (!name) return;
        insertTrackCall(path, name);
      },
    },
  };

  // 插入埋点调用
  function insertTrackCall(path, name) {
    const bodyPath = path.get('body');
    // 只有当 body 是 BlockStatement 时才能插入
    if (!bodyPath.isBlockStatement()) {
      // 箭头函数简写返回：() => foo() → () => { __track__(name); return foo(); }
      bodyPath.replaceWith(
        t.blockStatement([
          createTrackStatement(name),
          t.returnStatement(bodyPath.node),
        ])
      );
      return;
    }
    // 避免重复插入
    const firstStmt = bodyPath.node.body[0];
    if (
      t.isExpressionStatement(firstStmt) &&
      t.isCallExpression(firstStmt.expression) &&
      t.isIdentifier(firstStmt.expression.callee, { name: '__track__' })
    ) {
      return;
    }
    bodyPath.unshiftContainer('body', createTrackStatement(name));
  }

  function createTrackStatement(name) {
    return t.expressionStatement(
      t.callExpression(t.identifier('__track__'), [
        t.stringLiteral(name),
      ])
    );
  }
};
```

### 配置使用

```js
// babel.config.js
module.exports = {
  plugins: [
    ['./babel-plugin-auto-track', { exclude: ['*.test.js'] }],
  ],
};
```

---

## 8.3 实战：去除 console 插件

**目标**：生产环境自动移除 `console.log/info/debug`，但保留 `console.warn/error`。

### 完整实现

```js
// babel-plugin-drop-console.js
module.exports = function ({ types: t }, options = {}) {
  const dropMethods = options.drop || ['log', 'info', 'debug', 'trace'];
  const keepMethods = options.keep || ['warn', 'error'];

  return {
    name: 'drop-console',
    visitor: {
      ExpressionStatement(path) {
        const expr = path.node.expression;
        if (!t.isCallExpression(expr)) return;

        const callee = expr.callee;
        // 匹配 console.xxx(...)
        if (
          t.isMemberExpression(callee) &&
          t.isIdentifier(callee.object, { name: 'console' }) &&
          t.isIdentifier(callee.property)
        ) {
          const methodName = callee.property.name;
          if (dropMethods.includes(methodName)) {
            path.remove();
          }
        }
      },
      // 处理 sequence expression 中的 console：a(), console.log(b), c()
      SequenceExpression(path) {
        const kept = path.node.expressions.filter((expr) => {
          if (
            t.isCallExpression(expr) &&
            t.isMemberExpression(expr.callee) &&
            t.isIdentifier(expr.callee.object, { name: 'console' }) &&
            t.isIdentifier(expr.callee.property) &&
            dropMethods.includes(expr.callee.property.name)
          ) {
            return false;
          }
          return true;
        });
        if (kept.length === 0) {
          path.parentPath.remove();
        } else if (kept.length === 1) {
          path.replaceWith(kept[0]);
        } else {
          path.node.expressions = kept;
        }
      },
    },
  };
};
```

### 测试用例

```js
// 输入
console.log('debug info');
console.warn('warning');
console.error('error');
doSomething(); console.log('x'); doOther();

// 输出
console.warn('warning');
console.error('error');
doSomething(); doOther();
```

---

## 8.4 实战：国际化提取插件

**目标**：将中文字符串自动替换为 `t('key')` 调用，并收集所有 key 到 JSON 文件。

### 转换效果

```js
// 输入
const title = '欢迎使用本系统';
function greet() {
  alert('你好，世界');
}

// 输出
const title = t('welcome_title');
function greet() {
  alert(t('hello_world'));
}
// 同时生成 locale.json：{ "welcome_title": "欢迎使用本系统", "hello_world": "你好，世界" }
```

### 完整实现

```js
// babel-plugin-i18n-extract.js
const fs = require('fs');
const path = require('path');

module.exports = function ({ types: t }, options = {}) {
  const output = options.output || './locale.json';
  const localeMap = new Map();
  const existing = safeReadJSON(output);
  Object.assign(localeMap, existing);

  function makeKey(text) {
    // 简单的 hash 生成 key
    const hash = hashString(text);
    return `k_${hash}`;
  }

  function hashString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = ((hash << 5) - hash) + str.charCodeAt(i);
      hash |= 0;
    }
    return Math.abs(hash).toString(36);
  }

  function replaceChineseString(textPath, text) {
    const key = makeKey(text);
    if (!localeMap[key]) {
      localeMap[key] = text;
    }
    textPath.replaceWith(
      t.callExpression(t.identifier(options.fnName || 't'), [
        t.stringLiteral(key),
      ])
    );
  }

  return {
    name: 'i18n-extract',
    pre() {
      this.hasChinese = (s) => /[\u4e00-\u9fa5]/.test(s);
    },
    visitor: {
      StringLiteral(path) {
        const value = path.node.value;
        if (!this.hasChinese(value)) return;

        // 跳过 import/export 路径
        if (path.parentPath.isImportDeclaration() ||
            path.parentPath.isExportNamedDeclaration() ||
            path.parentPath.isExportAllDeclaration()) return;

        // 跳过 require('xxx')
        if (path.parentPath.isCallExpression() &&
            t.isIdentifier(path.parentPath.node.callee, { name: 'require' })) return;

        replaceChineseString(path, value);
      },
      TemplateLiteral(path) {
        // 跳过带表达式的模板字符串
        if (path.node.expressions.length > 0) return;
        const raw = path.node.quasis[0].value.cooked;
        if (!this.hasChinese(raw)) return;
        // 模板字符串 → 字符串字面量
        const stringNode = t.stringLiteral(raw);
        replaceChineseString(path, raw);
      },
    },
    post() {
      // 写出 locale 文件
      fs.writeFileSync(
        path.resolve(process.cwd(), output),
        JSON.stringify(localeMap, null, 2),
        'utf8'
      );
      console.log(`[i18n] Extracted ${Object.keys(localeMap).length} keys to ${output}`);
    },
  };

  function safeReadJSON(p) {
    try {
      return JSON.parse(fs.readFileSync(path.resolve(process.cwd(), p), 'utf8'));
    } catch {
      return {};
    }
  }
};
```

### 配置

```js
// babel.config.js
module.exports = {
  plugins: [
    ['./babel-plugin-i18n-extract', {
      output: './src/locales/zh-CN.json',
      fnName: 't',
    }],
  ],
};
```

---

## 8.5 插件开发常用 API 速查

| API | 作用 | 示例 |
|-----|------|------|
| `path.node` | 当前 AST 节点 | `path.node.name` |
| `path.parent` | 父节点 | `path.parent` |
| `path.parentPath` | 父 Path 对象 | `path.parentPath.remove()` |
| `path.replaceWith(node)` | 替换当前节点 | `path.replaceWith(t.identifier('foo'))` |
| `path.remove()` | 删除当前节点 | `path.remove()` |
| `path.insertBefore(node)` | 在前面插入 | `path.insertBefore(stmt)` |
| `path.insertAfter(node)` | 在后面插入 | `path.insertAfter(stmt)` |
| `path.get('key')` | 获取子属性 Path | `path.get('body')` |
| `path.scope` | 作用域对象 | `path.scope.generateUidIdentifier('tmp')` |
| `path.scope.hasBinding(name)` | 判断绑定是否存在 | `path.scope.hasBinding('foo')` |
| `path.scope.rename(old, new)` | 重命名变量 | `path.scope.rename('foo', 'bar')` |
| `path.skip()` | 跳过子树遍历 | `path.skip()` |
| `path.stop()` | 停止整个遍历 | `path.stop()` |
| `path.findParent(fn)` | 向上查找父节点 | `path.findParent(p => p.isFunction())` |
| `path.traverse(visitor)` | 在子树上遍历 | `path.traverse({ Identifier() {} })` |
| `t.valueToNode(value)` | JS 值 → AST 节点 | `t.valueToNode({ a: 1 })` |

---

# 九、Polyfill 与按需引入

## 9.1 Polyfill 概念

**Polyfill（垫片/补丁）** 是一段代码，用于在不支持某个 API 的环境中模拟出该 API 的行为。

### 语法 vs API

| 类别 | 示例 | 是否需要 Polyfill |
|------|------|------------------|
| **语法** | 箭头函数、`class`、解构、模板字符串 | 否，Babel 插件直接转换语法 |
| **API** | `Promise`、`Array.includes`、`Object.assign`、`fetch` | 是，需要 Polyfill 才能在旧浏览器运行 |
| **实例方法** | `'abc'.padStart`、`[1,2].flat` | 是 |

### 为什么需要 Polyfill

```js
// Babel 能把箭头函数转换成普通函数
const fn = () => 1;
// ↓ 转换成
var fn = function() { return 1; };

// 但 Babel 不会自动模拟 Promise
const p = new Promise(resolve => resolve(1));
// ↓ IE 中 Promise is not defined → 必须手动引入 polyfill
```

---

## 9.2 @babel/polyfill 的废弃

### 旧方案（已废弃）

```js
// 入口文件顶部引入
import '@babel/polyfill';
```

**问题**：

1. **包体积巨大**：整个 `core-js@2` + `regenerator-runtime` 全量引入，未使用的 API 也会被打包。
2. **污染全局**：直接挂载在 `window` 上，无法隔离。
3. **无法按需加载**：无论用没用到，所有 polyfill 都被引入。
4. **Babel 7.4.0+ 已废弃**，控制台会有警告：
   ```
   WARNING: We are deprecating @babel/polyfill
   ```

### 迁移到新方案

```diff
- import '@babel/polyfill';
+ import 'core-js/stable';
+ import 'regenerator-runtime/runtime';
```

但更推荐使用 `core-js@3` + `useBuiltIns: 'usage'` 自动按需引入。

---

## 9.3 core-js@3 方案

### 安装

```bash
npm install --save core-js@3
# 或
npm install --save core-js regenerator-runtime
```

### 三大能力

| 能力 | 说明 | 引入方式 |
|------|------|----------|
| **标准 polyfill** | 标准 API 实现（如 `Promise`、`Array.includes`） | `core-js/stable` |
| **提案 polyfill** | Stage 1-3 提案 API（如 `Array.prototype.flatten`） | `core-js/proposals` 或 `core-js/features/xxx` |
| **regenerator** | `async/await`、`generator` 的运行时支持 | `regenerator-runtime/runtime` |

### 按特性引入

```js
// 只引入用到的特性
import 'core-js/features/promise';
import 'core-js/features/array/flat';
import 'core-js/features/string/pad-start';
import 'regenerator-runtime/runtime';
```

### 不污染全局的引入

```js
// 不污染全局，从命名空间导入
import Promise from 'core-js-pure/features/promise';
import includes from 'core-js-pure/features/array/virtual/includes';

const arr = [1, 2, 3];
includes.call(arr, 2); // true
```

---

## 9.4 useBuiltIns 三种模式

`@babel/preset-env` 的 `useBuiltIns` 选项控制 polyfill 引入策略。

### 1. `useBuiltIns: false`（默认）

不做任何自动注入，开发者手动 `import 'core-js'`。

```js
{
  presets: [
    ['@babel/preset-env', {
      useBuiltIns: false,
    }],
  ],
}
```

**特点**：完全手动控制，体积大但可控。

### 2. `useBuiltIns: 'entry'`

在入口文件 `import 'core-js'`，Babel 根据 `targets` 自动拆分为按需。

```js
// babel.config.js
{
  presets: [
    ['@babel/preset-env', {
      useBuiltIns: 'entry',
      corejs: 3,
    }],
  ],
}

// 入口文件
import 'core-js';
```

**实际打包**（假设目标是 IE 11）：

```js
// 转换后等价于：
import 'core-js/modules/es.promise';
import 'core-js/modules/es.array.includes';
import 'core-js/modules/es.object.assign';
// ... 但只包含 IE11 不支持的部分
```

**特点**：比 `false` 体积小，但仍包含整个 targets 范围内的所有 polyfill。

### 3. `useBuiltIns: 'usage'`（推荐）

**完全按使用情况注入**，代码里用到什么 API 就引入对应的 polyfill。

```js
{
  presets: [
    ['@babel/preset-env', {
      useBuiltIns: 'usage',
      corejs: 3,
    }],
  ],
}
```

**转换效果**：

```js
// 源码
const arr = [1, 2, 3];
arr.includes(2);
const p = new Promise(r => r(1));

// 编译后（自动注入）
import 'core-js/modules/es.array.includes';
import 'core-js/modules/es.promise';
const arr = [1, 2, 3];
arr.includes(2);
const p = new Promise(r => r(1));
```

**优点**：

- **体积最小**：只注入用到的 API。
- **自动管理**：新增 API 不用改入口。
- **不会遗漏**：不会因为忘记 polyfill 而出 bug。

**配置示例**：

```js
// babel.config.js
module.exports = {
  presets: [
    ['@babel/preset-env', {
      targets: { chrome: '60', ie: '11' },
      useBuiltIns: 'usage',
      corejs: { version: 3, proposals: true },
    }],
  ],
};
```

### 三种模式对比

| 模式 | 注入策略 | 体积 | 全局污染 | 推荐度 |
|------|----------|------|----------|--------|
| `false` | 完全手动 | 最大 | 是 | 低 |
| `'entry'` | 按目标环境 | 中等 | 是 | 中 |
| `'usage'` | 按使用情况 | 最小 | 是 | **高（推荐）** |

---

## 9.5 @babel/runtime vs @babel/polyfill

两者目标不同，常被混淆。

### @babel/polyfill

- **作用**：提供全局 API 垫片（如 `Promise`、`Array.includes`）。
- **污染**：直接挂载到 `window` 上。
- **现状**：已废弃，迁移到 `core-js@3`。

### @babel/runtime

- **作用**：提供 Babel 转换过程中产生的**辅助函数**（helpers），避免重复内联。
- **不污染全局**：以模块方式导入。
- **包含内容**：
  - `_classCallCheck`、`_inherits` 等 class 转换辅助
  - `_typeof`、`_extends` 等 ES6+ 转换辅助
  - `regenerator-runtime`（async/generator）

### 转换示例

**不使用 runtime**：

```js
// 多个文件都会内联同样的辅助函数，体积膨胀
// a.js
function _classCallCheck(...) { ... }
function _inherits(...) { ... }
class A extends B {}

// b.js
function _classCallCheck(...) { ... }   // 重复
function _inherits(...) { ... }          // 重复
class C extends D {}
```

**使用 runtime**：

```js
// a.js
import _classCallCheck from '@babel/runtime/helpers/classCallCheck';
import _inherits from '@babel/runtime/helpers/inherits';
class A extends B {}

// b.js
import _classCallCheck from '@babel/runtime/helpers/classCallCheck';
import _inherits from '@babel/runtime/helpers/inherits';
class C extends D {}
```

### @babel/plugin-transform-runtime

`@babel/plugin-transform-runtime` 是插件，配合 `@babel/runtime` 使用，自动将内联 helper 替换为 import。

```js
// babel.config.js
module.exports = {
  presets: ['@babel/preset-env'],
  plugins: [
    ['@babel/plugin-transform-runtime', {
      corejs: 3,       // 启用 API polyfill 提取
      helpers: true,   // 启用 helper 提取
      regenerator: true, // 启用 async/generator 提取
    }],
  ],
};
```

### 两种方案对比

| 维度 | `useBuiltIns: 'usage'` + `core-js@3` | `@babel/plugin-transform-runtime` + `corejs: 3` |
|------|--------------------------------------|------------------------------------------------|
| **作用范围** | 全局 API（`Promise`、`Array.includes` 等） | 全局 API + Babel helpers |
| **污染全局** | 是 | 否（无污染版本） |
| **包体积** | 应用代码小，但 `core-js` 在主包 | 单库独立打包 |
| **适用场景** | **应用开发**（业务项目） | **库/工具开发**（SDK、组件库） |

### 选择建议

| 场景 | 推荐方案 |
|------|----------|
| **业务应用**（Vue/React/Next 项目） | `useBuiltIns: 'usage'` + `core-js@3` |
| **第三方库**（npm 包、UI 库） | `@babel/plugin-transform-runtime` + `corejs: 3` |
| **同时开发业务 + 组件库** | 业务用 `usage`，组件库单独 `runtime` |

---

# 十、面试高频题

## 10.1 Babel 原理篇

### Q1：Babel 的整体工作流程是什么？

**答**：Babel 采用 **Parse → Transform → Generate** 三阶段流水线：

1. **Parse（解析）**：使用 `@babel/parser` 将源码解析为 AST。分为词法分析（Token 流）和语法分析（AST）。
2. **Transform（转换）**：使用 `@babel/traverse` 遍历 AST，配合 Plugin/Preset 在 Visitor 模式下对节点进行增删改查。
3. **Generate（生成）**：使用 `@babel/generator` 将变换后的 AST 重新生成代码字符串，并生成 sourcemap。

```js
const { parse } = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const generate = require('@babel/generator').default;

const ast = parse(sourceCode);
traverse(ast, visitor);
const output = generate(ast, { sourceMaps: true });
```

---

### Q2：AST 是什么？Babel 中的 AST 节点有哪些常见类型？

**答**：AST（Abstract Syntax Tree，抽象语法树）是源码的树状结构表示，每个节点对应一段代码。

常见节点类型：

| 节点类型 | 说明 | 示例 |
|----------|------|------|
| `Program` | 整个程序的根节点 | 整个文件 |
| `ExpressionStatement` | 表达式语句 | `foo();` |
| `VariableDeclaration` | 变量声明 | `let a = 1;` |
| `FunctionDeclaration` | 函数声明 | `function foo() {}` |
| `ArrowFunctionExpression` | 箭头函数 | `() => {}` |
| `Identifier` | 标识符 | `foo`、`bar` |
| `Literal` / `StringLiteral` / `NumericLiteral` | 字面量 | `'abc'`、`123` |
| `CallExpression` | 函数调用 | `foo(a, b)` |
| `MemberExpression` | 成员访问 | `obj.prop`、`arr[0]` |
| `BinaryExpression` | 二元运算 | `a + b` |
| `AssignmentExpression` | 赋值表达式 | `a = 1` |
| `IfStatement` | if 语句 | `if (x) {}` |
| `BlockStatement` | 块语句 | `{ ... }` |
| `ReturnStatement` | return | `return x;` |
| `ImportDeclaration` | import | `import x from 'y'` |

---

### Q3：Visitor 模式在 Babel 中是如何应用的？

**答**：Babel 借鉴了设计模式中的 Visitor 模式，让开发者**只关心某类节点的处理逻辑**，而无需关心遍历算法本身。

```js
const visitor = {
  // 进入节点时调用
  Identifier: {
    enter(path) {
      console.log('Enter:', path.node.name);
    },
    // 离开节点时调用
    exit(path) {
      console.log('Exit:', path.node.name);
    },
  },
  // 简写：等价于 enter
  FunctionDeclaration(path) {
    path.node.id.name = 'renamed_' + path.node.id.name;
  },
};
```

遍历过程是**深度优先**的，对每个节点先调用 `enter`，递归访问所有子节点后再调用 `exit`。

---

### Q4：Path 对象和 Node 对象有什么区别？

**答**：

| 维度 | Node | Path |
|------|------|------|
| **本质** | AST 节点（纯数据） | 节点 + 上下文信息 |
| **包含内容** | `type`、`name`、`body` 等字段 | `node`、`parent`、`parentPath`、`scope` |
| **可操作性** | 只能读，修改后无法同步到树 | 可增删改查，会自动同步 |
| **访问父子** | 无法直接访问父节点 | `path.parentPath` 直接获取 |
| **作用域** | 无 | `path.scope` 可查询变量绑定 |

```js
// Node：只是数据
const node = path.node;
console.log(node.name);  // 'foo'
// 直接改 node 不会同步到 AST

// Path：包含上下文，操作会同步
path.replaceWith(t.identifier('bar'));
path.remove();
path.parentPath.insertAfter(t.expressionStatement(...));
```

---

### Q5：Babel 如何处理 Plugin 和 Preset 的执行顺序？

**答**：

1. **Plugin 之间**：按**数组顺序**从前到后执行。
2. **Preset 之间**：按**数组顺序倒序**执行（从后往前）。
3. **Plugin vs Preset**：**先 Plugin 后 Preset**。

```js
{
  plugins: ['a', 'b', 'c'],          // 顺序：a → b → c
  presets: ['p1', 'p2', 'p3'],      // 顺序：p3 → p2 → p1
}
// 整体顺序：a → b → c → p3 → p2 → p1
```

**为什么 Preset 要倒序？**
直观上，开发者倾向于把"更具体"的 preset 放后面（如 `preset-typescript` 在 `preset-env` 之后），但实际上后面先执行，相当于"更具体"的转换先做，避免被通用 preset 干扰。

---

## 10.2 配置实战篇

### Q6：babel.config.js 和 .babelrc 有什么区别？

**答**：

| 维度 | `babel.config.js` | `.babelrc` |
|------|--------------------|------------|
| **作用范围** | 整个项目（全局） | 单个目录（及子目录） |
| **配置形式** | JS 函数，可读 `env`、`argv` | JSON 静态对象 |
| **支持 monorepo** | 是 | 否 |
| **node_modules 编译** | 是 | 否（默认跳过） |
| **推荐场景** | 库 + 应用项目 | 单一项目 |
| **加载时机** | 项目根目录 | 当前文件所在目录及向上查找 |

```js
// babel.config.js（推荐）
module.exports = function (api) {
  api.cache.using(() => process.env.NODE_ENV);
  return {
    presets: ['@babel/preset-env'],
    plugins: [],
  };
};

// .babelrc（仅静态）
{
  "presets": ["@babel/preset-env"]
}
```

---

### Q7：如何让 Babel 缓存编译结果加速？

**答**：使用 `api.cache` 显式声明缓存策略。

```js
module.exports = function (api) {
  // 方式 1：基于环境变量
  api.cache.using(() => process.env.NODE_ENV);

  // 方式 2：基于版本
  api.cache.never();  // 不缓存

  // 方式 3：永久缓存（开发期固定）
  api.cache(true);

  return { /* config */ };
};
```

配合 Webpack 的 `cache-loader` 或 `babel-loader?cacheDirectory=true` 可以进一步加速。

```js
// webpack.config.js
module: {
  rules: [
    {
      test: /\.js$/,
      use: {
        loader: 'babel-loader',
        options: {
          cacheDirectory: true,         // 启用缓存
          cacheCompression: false,      // 不压缩，启动更快
        },
      },
    },
  ],
}
```

---

### Q8：Vite 为什么默认不需要 Babel？

**答**：Vite 利用浏览器原生 ES Modules 支持，开发期**直接加载源码**，不做任何转换。生产期使用 **esbuild**（Go 编写）替代 Babel 进行语法转换，速度提升 10-100 倍。

| 场段 | 转换工具 | 说明 |
|------|----------|------|
| 开发期 | 浏览器原生 | 直接 `import` 加载，不编译 |
| 生产期 | esbuild | 语法转换、Tree-shaking、压缩 |

但有些场景仍需要 Babel：

1. 需要兼容老浏览器（IE 11）。
2. 使用 Babel 特定的插件（如自动埋点）。
3. React 项目用 JSX，且需要特定转换。

Vite 中可以手动加入 Babel：

```js
// vite.config.js
import { defineConfig } from 'vite';
import babel from 'vite-plugin-babel';

export default defineConfig({
  plugins: [babel({ babelConfig: { /* ... */ } })],
});
```

---

## 10.3 Polyfill 篇

### Q9：useBuiltIns 三种模式有何区别？

**答**：

| 模式 | 注入策略 | 体积 | 推荐度 |
|------|----------|------|--------|
| `false` | 不注入，手动 `import 'core-js'` | 最大 | 低 |
| `'entry'` | 入口 `import 'core-js'`，按 targets 拆分 | 中等 | 中 |
| `'usage'` | 按代码实际使用情况注入 | 最小 | **高** |

```js
// 'usage' 模式
// 源码
arr.includes(1);
// 编译后
import 'core-js/modules/es.array.includes';
arr.includes(1);
```

---

### Q10：业务项目和第三方库分别该用什么 Polyfill 方案？

**答**：

| 场景 | 推荐方案 | 原因 |
|------|----------|------|
| **业务应用** | `useBuiltIns: 'usage'` + `core-js@3` | 体积最小，全局污染对业务无影响 |
| **第三方库** | `@babel/plugin-transform-runtime` + `corejs: 3` | 不污染全局，依赖隔离 |

业务项目污染全局无影响，但库污染全局会影响使用方：

```js
// 库代码污染了用户的 Array.includes
import 'core-js/modules/es.array.includes';
// 如果用户也定义了 Array.prototype.includes，可能冲突
```

---

### Q11：corejs 配置中 `version` 和 `proposals` 的作用？

**答**：

```js
{
  presets: [
    ['@babel/preset-env', {
      useBuiltIns: 'usage',
      corejs: {
        version: 3,           // 使用 core-js@3（不是 @2）
        proposals: true,       // 提案 API 也按需引入
      },
    }],
  ],
}
```

- `version`：指定 core-js 版本（`2` 或 `3`）。**Babel 7.4+ 默认 `2`，但建议手动指定 `3`**。
- `proposals: true`：是否引入 Stage 1-3 的提案 API（如 `Array.prototype.flatMap`、`Object.fromEntries`）。

---

## 10.4 插件开发篇

### Q12：如何写一个 Babel 插件，在所有函数入口插入 `console.time('xxx')`？

**答**：

```js
module.exports = function ({ types: t }) {
  return {
    name: 'function-timer',
    visitor: {
      'FunctionDeclaration|FunctionExpression|ArrowFunctionExpression'(path) {
        // 获取函数名
        let name = '';
        if (path.isFunctionDeclaration()) {
          name = path.node.id?.name || 'anonymous';
        } else if (path.parentPath.isVariableDeclarator()) {
          name = path.parentPath.node.id.name;
        } else if (path.parentPath.isObjectMethod() ||
                   path.parentPath.isObjectProperty()) {
          name = path.parentPath.node.key.name;
        } else {
          name = 'anonymous';
        }

        const bodyPath = path.get('body');
        if (!bodyPath.isBlockStatement()) {
          // 简写箭头函数 → 转为 block
          bodyPath.replaceWith(
            t.blockStatement([
              createTimerStart(name),
              t.returnStatement(bodyPath.node),
              createTimerEnd(name),
            ])
          );
          return;
        }
        bodyPath.unshiftContainer('body', createTimerStart(name));
        bodyPath.pushContainer('body', createTimerEnd(name));
      },
    },
  };

  function createTimerStart(name) {
    return t.expressionStatement(
      t.callExpression(
        t.memberExpression(t.identifier('console'), t.identifier('time')),
        [t.stringLiteral(name)]
      )
    );
  }
  function createTimerEnd(name) {
    return t.expressionStatement(
      t.callExpression(
        t.memberExpression(t.identifier('console'), t.identifier('timeEnd')),
        [t.stringLiteral(name)]
      )
    );
  }
};
```

---

### Q13：插件开发中如何避免无限循环？

**答**：插件修改节点后，Babel 会重新访问修改后的节点。如果改完还是同类型节点，就会死循环。

**解决方案**：

1. **`path.skip()`**：跳过子树遍历。
2. **`path.requeue()`** + 状态判断：通过 `node.__processed` 标记。
3. **判断节点是否已处理**。

```js
{
  visitor: {
    Identifier(path) {
      if (path.node.__processed) return;
      // 修改节点
      path.replaceWith(t.identifier('newName'));
      path.node.__processed = true;
      path.skip();
    },
  },
}
```

---

### Q14：Babel 插件如何获取当前文件路径、配置选项？

**答**：

```js
module.exports = function ({ types: t }) {
  return {
    visitor: {
      Program(path, state) {
        // 当前文件路径
        const filename = state.filename || this.filename || 'unknown';

        // 用户配置（来自 babel.config.js 的 options）
        const opts = state.opts || {};

        // 当前 babel 配置文件
        const file = state.file;
        const cwd = state.cwd;

        console.log('Processing:', filename, 'opts:', opts);
      },
    },
  };
};
```

---

## 10.5 进阶题

### Q15：Babel 编译 TypeScript 和 tsc 有什么区别？

**答**：

| 维度 | `tsc` | `@babel/preset-typescript` |
|------|-------|------------------------------|
| **类型检查** | 是 | 否（仅剥离类型） |
| **语法转换** | 是 | 是 |
| **Polyfill** | 否 | 是（配合 `preset-env`） |
| **速度** | 慢 | 快 |
| **sourcemap** | 是 | 是 |
| **Decorator** | 完整支持 | 需要额外插件 |

**结论**：业务项目用 Babel，需要严格类型检查用 tsc 或配合 `fork-ts-checker-webpack-plugin`。

---

### Q16：如何排查 Babel 编译后代码无法运行的问题？

**答**：

1. **查看 AST**：用 [AST Explorer](https://astexplorer.net/) 检查源码的 AST。
2. **打印转换前后代码**：在 plugin 中 `console.log(generate(path.node).code)`。
3. **逐步排查插件**：用二分法注释掉部分插件，定位是哪个插件导致的问题。
4. **检查 targets**：错误的 targets 会让 Babel 跳过转换。
5. **检查 polyfill**：缺少 polyfill 是常见原因，使用 `useBuiltIns: 'usage'`。
6. **检查 source map**：用 sourcemap 定位到源码。

```js
// 调试：输出当前文件 AST
module.exports = function ({ types: t }) {
  return {
    visitor: {
      Program: {
        exit(path) {
          console.log(require('@babel/generator').default(path.node).code);
        },
      },
    },
  };
};
```

---

### Q17：Babel 和 SWC、esbuild 的区别？

**答**：

| 维度 | Babel | SWC | esbuild |
|------|-------|-----|---------|
| **语言** | JavaScript | Rust | Go |
| **速度** | 慢 | 快 20-70 倍 | 快 100 倍 |
| **生态** | 最丰富 | 中等 | 较少 |
| **插件** | 支持 | 支持 | 不支持 |
| **TypeScript** | 支持 | 支持 | 支持 |
| **Polyfill** | 支持 | 不支持 | 不支持 |
| **场景** | 库开发、复杂转换 | 替代 Babel | 打包工具 |

**选型建议**：

- 业务项目：esbuild（Vite）+ 必要时 Babel 插件。
- 库开发：Babel（生态完善）或 SWC（速度优先）。
- 复杂 AST 操作：Babel（无可替代）。

---

### Q18：Babel 7 与 Babel 8 的主要变化？

**答**：

Babel 8 的主要改进：

1. **完全废弃 `@babel/polyfill`**：使用 `core-js@3` + `useBuiltIns: 'usage'`。
2. **Node 6/8 不再支持**：最低 Node 14+。
3. **AST 节点结构变化**：更严格，符合 ESTree 规范。
4. **TypeScript 4.x 完整支持**。
5. **更快的 parser**：底层重写。
6. **不再支持 IE 8**：targets 默认值更新。
7. **ECMAScript Modules 原生导出**：`export default` 取代 `module.exports`。

---

## 10.6 综合题

### Q19：手写一个简易的 Babel（实现 Parse + Transform + Generate）

**答**：

```js
// mini-babel.js

// ============== 1. Parser ==============
function tokenize(code) {
  const tokens = [];
  let i = 0;
  while (i < code.length) {
    const char = code[i];
    if (/\s/.test(char)) { i++; continue; }
    if (/[a-zA-Z]/.test(char)) {
      let word = '';
      while (i < code.length && /[a-zA-Z]/.test(code[i])) {
        word += code[i++];
      }
      tokens.push({ type: 'word', value: word });
      continue;
    }
    if (/[0-9]/.test(char)) {
      let num = '';
      while (i < code.length && /[0-9]/.test(code[i])) {
        num += code[i++];
      }
      tokens.push({ type: 'number', value: Number(num) });
      continue;
    }
    tokens.push({ type: 'punct', value: char });
    i++;
  }
  return tokens;
}

function parse(code) {
  const tokens = tokenize(code);
  let pos = 0;
  function walk() {
    const token = tokens[pos];
    if (token.type === 'word') {
      // 简化：只处理 "add(a, b)" 形式
      if (tokens[pos + 1]?.value === '(') {
        pos += 2; // 跳过 name(
        const params = [];
        while (tokens[pos].value !== ')') {
          params.push(walk());
          if (tokens[pos].value === ',') pos++;
        }
        pos++; // 跳过 )
        return {
          type: 'CallExpression',
          callee: { type: 'Identifier', name: token.value },
          arguments: params,
        };
      }
      pos++;
      return { type: 'Identifier', name: token.value };
    }
    if (token.type === 'number') {
      pos++;
      return { type: 'NumericLiteral', value: token.value };
    }
    throw new Error('Unexpected: ' + JSON.stringify(token));
  }
  const ast = { type: 'Program', body: [] };
  while (pos < tokens.length) {
    ast.body.push(walk());
  }
  return ast;
}

// ============== 2. Transformer ==============
function traverse(ast, visitor) {
  function visitNode(node, parent) {
    if (visitor[node.type]?.enter) {
      visitor[node.type].enter(node, parent);
    }
    for (const key in node) {
      if (Array.isArray(node[key])) {
        node[key].forEach((child) => visitNode(child, node));
      } else if (typeof node[key]?.type === 'string') {
        visitNode(node[key], node);
      }
    }
    if (visitor[node.type]?.exit) {
      visitor[node.type].exit(node, parent);
    }
  }
  visitNode(ast, null);
}

function transform(ast) {
  traverse(ast, {
    CallExpression: {
      enter(node) {
        // 重命名 add → sum
        if (node.callee.name === 'add') {
          node.callee.name = 'sum';
        }
      },
    },
  });
  return ast;
}

// ============== 3. Generator ==============
function generate(ast) {
  switch (ast.type) {
    case 'Program':
      return ast.body.map(generate).join('\n');
    case 'CallExpression':
      return generate(ast.callee) + '(' + ast.arguments.map(generate).join(', ') + ')';
    case 'Identifier':
      return ast.name;
    case 'NumericLiteral':
      return String(ast.value);
  }
}

// ============== 4. Pipeline ==============
function compile(code) {
  const ast = parse(code);
  const newAst = transform(ast);
  return generate(newAst);
}

console.log(compile('add(1, 2)'));
// 输出：sum(1, 2)
```

---

### Q20：项目实战 - 如何为一个大型老项目渐进式接入 Babel？

**答**：

**场景**：一个 jQuery + ES5 老项目，需要逐步引入 ES6+ 语法和现代工具链。

**渐进式步骤**：

**阶段 1：引入 Babel 但不改变代码**

```js
// babel.config.js（仅转换语法，不影响行为）
module.exports = {
  presets: [
    ['@babel/preset-env', {
      targets: { ie: '11' },
      useBuiltIns: 'usage',
      corejs: 3,
    }],
  ],
};
```

```js
// webpack.config.js 加上 babel-loader
{
  test: /\.js$/,
  exclude: /node_modules/,
  use: 'babel-loader',
}
```

**阶段 2：替换工具链**

- 用 Webpack 替换 RequireJS / SeaJS。
- 用 npm 替换 Bower / 直接引 script。
- 引入 ESLint 检查现代语法。

**阶段 3：渐进式重写**

- 新功能用 ES6+ 编写。
- 老代码逐模块重写，按需引入 `core-js` polyfill。
- 使用 Babel 插件自动转换（如自动替换 `var` 为 `let/const`）。

**阶段 4：移除 IE 兼容**

- `targets` 更新到现代浏览器。
- 移除多余 polyfill。
- 启用现代构建工具（Vite/esbuild）。

**关键经验**：

1. **小步快跑**：每个 PR 只改一个文件，便于回滚。
2. **自动化测试**：接入前先补齐自动化测试。
3. **灰度发布**：先在小流量验证。
4. **性能监控**：关注 bundle 体积和加载时间。

---

## 10.7 总结与学习路径

### 推荐学习路径

```
入门
├── 理解 JS 编译是什么
├── 安装使用 @babel/cli + @babel/preset-env
└── 写一个 hello world 转换

进阶
├── 阅读 AST Explorer，熟悉节点类型
├── 写第一个插件（替换 console.log）
├── 理解 Visitor 模式和 Path 对象
└── 学习 polyfill 三种模式

高级
├── 深入源码：parse / traverse / generate
├── 实战复杂插件：埋点、i18n、自动 mock
├── 学习 @babel/preset-env 的智能降级机制
└── 对比 SWC / esbuild，理解 Babel 的取舍

专家
├── 参与开源：提交插件到 Babel 生态
├── 实现自定义 DSL（如 styled-components、Emotion）
├── 编写 AST lint 工具
└── 优化大型项目的构建速度
```

### 推荐资源

1. **官方文档**：[babeljs.io](https://babeljs.io/)
2. **AST Explorer**：[astexplorer.net](https://astexplorer.net/)
3. **Babel 源码**：[github.com/babel/babel](https://github.com/babel/babel)
4. **awesome-babel**：插件汇总
5. **《Babel Plugin Handbook》**：插件开发手册

### 常用速查

```bash
# 安装核心包
npm install --save-dev @babel/core @babel/cli @babel/preset-env

# 安装 polyfill
npm install --save core-js@3

# 安装运行时辅助
npm install --save-dev @babel/plugin-transform-runtime
npm install --save @babel/runtime

# 命令行编译
npx babel src --out-dir lib --watch

# 查看 AST
npx babel src/file.js -o out.js --presets=@babel/preset-env
```

---

**至此，Babel 深度解析完整结束。** 从原理 → 工程实战 → 插件开发 → 面试题，覆盖了 Babel 的核心知识体系。希望这份文档能帮助你彻底掌握 Babel，在前端工程化和面试中游刃有余。
