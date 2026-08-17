# Babel 深度解析

> 本文档从源码级原理、AST 结构、Presets/Plugins 机制、工程配置实战、自定义插件开发、Polyfill 策略到面试高频题，全面覆盖 Babel 的核心知识体系。

---

## 目录

- [一、Babel 概述](#一babel-概述)
  - [1.1 Babel 是什么](#11-babel-是什么)
  - [1.2 Babel 能做什么](#12-babel-能做什么)
  - [1.3 Babel 不能做什么](#13-babel-不能做什么)
  - [1.4 Babel 核心包生态](#14-babel-核心包生态)
- [二、核心架构与工作原理](#二核心架构与工作原理)
  - [2.1 三阶段流水线总览](#21-三阶段流水线总览)
  - [2.2 Parse 解析阶段](#22-parse-解析阶段)
  - [2.3 Transform 转换阶段](#23-transform-转换阶段)
  - [2.4 Generate 生成阶段](#24-generate-生成阶段)
  - [2.5 Babel 核心源码模块分工](#25-babel-核心源码模块分工)
- [三、AST 抽象语法树深度解析](#三ast-抽象语法树深度解析)
  - [3.1 什么是 AST](#31-什么是-ast)
  - [3.2 AST 节点类型](#32-ast-节点类型)
  - [3.3 AST 生成示例](#33-ast-生成示例)
  - [3.4 Visitor 访问者模式](#34-visitor-访问者模式)
  - [3.5 Path 路径对象](#35-path-路径对象)
- [四、Presets 预设详解](#四presets-预设详解)
  - [4.1 Preset 概念](#41-preset-概念)
  - [4.2 @babel/preset-env](#42-babelpreset-env)
  - [4.3 @babel/preset-react](#43-babelpreset-react)
  - [4.4 @babel/preset-typescript](#44-babelpreset-typescript)
  - [4.5 Preset 执行顺序](#45-preset-执行顺序)
- [五、Plugins 插件机制](#五plugins-插件机制)
  - [5.1 Plugin 概念](#51-plugin-概念)
  - [5.2 Plugin 执行顺序](#52-plugin-执行顺序)
  - [5.3 Plugin 与 Preset 执行顺序](#53-plugin-与-preset-执行顺序)
  - [5.4 常用插件清单](#54-常用插件清单)
- [六、配置文件体系](#六配置文件体系)
  - [6.1 babel.config.js vs .babelrc](#61-babelconfigjs-vs-babelrc)
  - [6.2 配置项详解](#62-配置项详解)
  - [6.3 targets 目标环境](#63-targets-目标环境)
- [七、工程配置实战](#七工程配置实战)
  - [7.1 Webpack 集成](#71-webpack-集成)
  - [7.2 Vite 集成](#72-vite-集成)
  - [7.3 生产环境配置最佳实践](#73-生产环境配置最佳实践)
- [八、自定义插件开发](#八自定义插件开发)
  - [8.1 插件基本结构](#81-插件基本结构)
  - [8.2 实战：自动埋点插件](#82-实战自动埋点插件)
  - [8.3 实战：去除 console 插件](#83-实战去除-console-插件)
  - [8.4 实战：国际化提取插件](#84-实战国际化提取插件)
- [九、Polyfill 与按需引入](#九polyfill-与按需引入)
  - [9.1 Polyfill 概念](#91-polyfill-概念)
  - [9.2 @babel/polyfill 的废弃](#92-babelpolyfill-的废弃)
  - [9.3 core-js@3 方案](#93-core-js3-方案)
  - [9.4 useBuiltIns 三种模式](#94-usebuiltins-三种模式)
  - [9.5 @babel/runtime vs @babel/polyfill](#95-babelruntime-vs-babelpolyfill)
- [十、面试高频题](#十面试高频题)
  - [10.1 Babel 原理篇](#101-babel-原理篇)
  - [10.2 配置实战篇](#102-配置实战篇)
  - [10.3 Polyfill 篇](#103-polyfill-篇)
  - [10.4 插件开发篇](#104-插件开发篇)

---

# 一、Babel 概述

## 1.1 Babel 是什么

Babel 是一个 **JavaScript 编译器**（JavaScript Compiler），它的核心作用是将现代版本的 JavaScript 代码（ES6+ / ES Next / TypeScript / JSX）转换为向后兼容的 JavaScript 代码，使其能在低版本浏览器或其他环境中正常运行。

```
输入 (ES6+)                    输出 (ES5)
┌──────────────────────┐      ┌──────────────────────┐
│ const add = (a, b) =>│      │ var add = function(a,│
│   a + b               │ ──→ │   b) { return a + b; }│
│                       │      │                       │
│ class Person {        │      │ function Person() {}  │
│   constructor(name) { │      │ // ...                │
│     this.name = name  │      │                       │
│   }                   │      │                       │
│ }                     │      │                       │
└──────────────────────┘      └──────────────────────┘
```

**核心定位**

| 维度 | 说明 |
|---|---|
| **名称来源** | Babel 取自《圣经》中的巴别塔（Tower of Babel），寓意让不同"语言"（JS 版本）互相沟通 |
| **社区地位** | 前端工程化基石，几乎所有的现代前端项目（React / Vue / Angular）都依赖 Babel |
| **维护方** | 由 Sebastian McKenzie 于 2014 年创建，现为开源社区项目 |
| **最新版本** | Babel 7（2018 年发布），采用 Monorepo 结构 |

---

## 1.2 Babel 能做什么

### 语法转换

将高版本语法转换为低版本语法：

```js
// 输入：ES6 箭头函数
const sum = (a, b) => a + b;

// 输出：ES5 函数表达式
var sum = function sum(a, b) {
  return a + b;
};
```

### JSX 转换

```jsx
// 输入：JSX
const element = <div className="app">Hello</div>;

// 输出：React.createElement
const element = React.createElement(
  "div",
  { className: "app" },
  "Hello"
);
```

### TypeScript 类型剥离

```ts
// 输入：TypeScript
function greet(name: string): string {
  return `Hello, ${name}`;
}

// 输出：JavaScript（类型被剥离）
function greet(name) {
  return "Hello, " + name;
}
```

### Polyfill 兼容

```js
// 输入：使用 Promise（ES6 API）
const p = new Promise((resolve) => resolve(42));

// 输出：注入 core-js 的 Promise polyfill
require("core-js/modules/es.promise.js");
var p = new Promise(function (resolve) { return resolve(42); });
```

### 源码级转换（插件）

- 自动埋点（给每个函数加日志）
- 自动国际化（提取中文字符串）
- 自动 lodash 按需引入
- 删除生产环境 console

---

## 1.3 Babel 不能做什么

| 不支持 | 原因 | 替代方案 |
|---|---|---|
| 模块打包 | Babel 只做转译，不做依赖图 | Webpack / Rollup / Vite |
| CSS 预处理 | Babel 只处理 JS | PostCSS / Sass / Less |
| 代码压缩 | Babel 不做压缩 | Terser / UglifyJS |
| Tree Shaking | 依赖打包器 | Webpack / Rollup |
| 类型检查 | Babel 只剥离类型，不检查 | tsc / TS 编译器 |

---

## 1.4 Babel 核心包生态

Babel 7 采用 **Monorepo** 结构，拆分为多个独立包：

```
@babel/
├── core                    # 核心 API：transform / parse / generate
├── cli                     # 命令行工具：babel 命令
├── node                    # 直接运行 ES6+ 文件
├── parser                  # Babylon → @babel/parser：JS 解析器
├── traverse                # AST 遍历器
├── generator               # AST → 代码生成器
├── types                   # AST 节点类型定义 + 工具函数
├── template                # 代码模板
├── helper                  # 编译时辅助函数
│
├── preset-env              # 智能预设：按目标环境自动决定插件
├── preset-react            # JSX 转换预设
├── preset-typescript       # TypeScript 预设
│
├── plugin-proposal-*       # 提案阶段语法插件
├── plugin-transform-*      # 已进入标准的语法转换插件
├── plugin-syntax-*         # 仅解析不转换（让 parser 支持）
│
├── runtime                 # 运行时辅助函数（@babel/runtime）
├── helpers                 # 编译时注入的 helper 函数
└── polyfill                # 已废弃（7.4.0+），改用 core-js + regenerator-runtime
```

**核心包依赖关系**

```
@babel/cli
    └─ @babel/core
         ├─ @babel/parser      解析 → AST
         ├─ @babel/traverse    遍历 AST
         ├─ @babel/generator   AST → 代码
         ├─ @babel/types       节点类型工具
         ├─ @babel/template    代码模板
         └─ @babel/helpers     辅助函数
```

---

# 二、核心架构与工作原理

## 2.1 三阶段流水线总览

Babel 的核心是 **Parse → Transform → Generate** 三阶段流水线：

```
源代码字符串
    │
    ▼
┌─────────────────────────────────────┐
│  阶段 1：Parse（解析）              │
│  @babel/parser                      │
│  ├── 词法分析(Lexical Analysis)     │
│  │   源代码 → Tokens 流             │
│  └── 语法分析(Syntax Analysis)      │
│      Tokens → AST（抽象语法树）      │
└──────────────┬──────────────────────┘
               │ AST
               ▼
┌─────────────────────────────────────┐
│  阶段 2：Transform（转换）          │
│  @babel/traverse + @babel/types     │
│  ├── 深度优先遍历 AST               │
│  ├── Visitor 模式匹配节点           │
│  └── Plugins/Presets 修改 AST      │
│      （增删改节点）                  │
└──────────────┬──────────────────────┘
               │ 修改后的 AST
               ▼
┌─────────────────────────────────────┐
│  阶段 3：Generate（生成）           │
│  @babel/generator                   │
│  ├── 深度优先遍历 AST               │
│  ├── 拼接代码字符串                 │
│  └── Source Map 生成                │
└──────────────┬──────────────────────┘
               │
               ▼
          目标代码 + SourceMap
```

**核心源码入口**

```js
// @babel/core 的 transformSync 简化版
function transformSync(code, options) {
  // 1. 加载配置（合并 presets/plugins）
  const config = resolveOptions(options);

  // 2. Parse：源代码 → AST
  const ast = parser.parse(code, {
    sourceType: 'module',
    plugins: ['jsx', 'typescript', ...config.parserPlugins],
  });

  // 3. Transform：遍历 AST，应用插件
  traverse(ast, {
    // 将所有插件的 visitor 合并到一起
    ...combinedVisitors(config.plugins, config.presets),
  });

  // 4. Generate：AST → 目标代码
  const output = generator(ast, {
    sourceMaps: true,
  }, code);

  return {
    code: output.code,
    map: output.map,
    ast: ast,
  };
}
```

---

## 2.2 Parse 解析阶段

解析阶段由 `@babel/parser`（原名 Babylon）完成，分为词法分析和语法分析两步。

### 词法分析（Lexical Analysis / Tokenization）

将源代码字符串逐字符扫描，分割为 **Tokens（词法单元）** 流。

```
源代码：const add = (a, b) => a + b;

词法分析 → Tokens：
┌────────┬───────┬───────┬───────┬───────┬───────┬───────┬───────┬───────┬───────┐
│ const  │ add   │ =     │ (     │ a     │ ,     │ b     │ )     │ =>    │ a + b │
│keyword │identif│punctua│punctua│identif │punctua│identif│punctua│punctua│identif│
└────────┴───────┴───────┴───────┴───────┴───────┴───────┴───────┴───────┴───────┘
```

每个 Token 包含：`type`（类型）、`value`（值）、`start`/`end`（位置）。

```js
// Token 结构示例
{
  type: { label: 'const', keyword: 'const' },
  value: 'const',
  start: 0,
  end: 5,
  loc: { start: { line: 1, column: 0 }, end: { line: 1, column: 5 } }
}
```

### 语法分析（Syntax Analysis / Parsing）

将 Tokens 流按 JavaScript 语法规则组织为 **AST（抽象语法树）**。

```
Tokens → Parser → AST

AST 结构（简化）：
Program
└── VariableDeclaration (kind: "const")
    └── VariableDeclarator
        ├── Identifier (name: "add")
        └── ArrowFunctionExpression
            ├── params: [Identifier(a), Identifier(b)]
            └── body: BinaryExpression
                ├── operator: "+"
                ├── left: Identifier(a)
                └── right: Identifier(b)
```

**parser 关键配置**

```js
parser.parse(code, {
  sourceType: 'module',       // 'script' | 'module' | 'unambiguous'
  allowImportExportEverywhere: false,
  allowReturnOutsideFunction: false,
  plugins: [
    'jsx',              // 支持 JSX
    'typescript',       // 支持 TypeScript
    'decorators-legacy',// 支持装饰器
    'classProperties',  // 支持类属性
    'optionalChaining', // 支持 ?.
    'nullishCoalescing',// 支持 ??
    'objectRestSpread', // 支持 ...展开
    'dynamicImport',    // 支持 import()
  ],
  sourceMaps: true,
});
```

---

## 2.3 Transform 转换阶段

转换阶段由 `@babel/traverse` 驱动，使用 **Visitor（访问者）模式** 遍历 AST，并在遍历过程中调用各插件注册的 visitor 方法修改 AST。

### 遍历流程

```
traverse(ast, visitor)

深度优先遍历 AST：
  Program
    ├── enter (进入 Program)
    ├── VariableDeclaration
    │     ├── enter
    │     ├── VariableDeclarator
    │     │     ├── enter
    │     │     ├── Identifier "add"
    │     │     │     ├── enter
    │     │     │     └── exit
    │     │     ├── ArrowFunctionExpression
    │     │     │     ├── enter
    │     │     │     ├── Identifier "a"
    │     │     │     ├── Identifier "b"
    │     │     │     ├── BinaryExpression
    │     │     │     └── exit
    │     │     └── exit
    │     └── exit
    └── exit (离开 Program)
```

### Visitor 模式

每个插件通过 visitor 对象定义对特定节点类型的处理逻辑：

```js
// 箭头函数转换插件（简化版）
const arrowFunctionPlugin = {
  name: 'transform-arrow-functions',
  visitor: {
    // 遇到 ArrowFunctionExpression 节点时触发
    ArrowFunctionExpression(path) {
      const { node } = path;

      // 1. 创建普通函数表达式节点
      const functionExpr = t.functionExpression(
        null,              // 函数名（匿名）
        node.params,       // 参数列表
        node.body,         // 函数体
        false,             // 是否生成器
        node.async         // 是否 async
      );

      // 2. 替换原节点
      path.replaceWith(functionExpr);
    },
  },
};
```

---

## 2.4 Generate 生成阶段

生成阶段由 `@babel/generator` 完成，遍历修改后的 AST，输出代码字符串。

```
修改后的 AST → Generator → 输出代码

输出：
  var add = function(a, b) {
    return a + b;
  };
```

**Generator 关键配置**

```js
generator(ast, {
  retainLines: false,        // 保留源码行号
  compact: 'auto',           // 紧凑模式：false | 'auto' | true
  minified: false,           // 是否压缩
  jsescOption: {             // 字符串转义选项
    minimal: true,
  },
  sourceMaps: true,          // 生成 SourceMap
  sourceFileName: 'input.js',
}, originalCode);
```

---

## 2.5 Babel 核心源码模块分工

| 模块 | npm 包 | 职责 |
|---|---|---|
| **Parser** | `@babel/parser` | 源代码 → AST（词法分析 + 语法分析） |
| **Traverse** | `@babel/traverse` | 深度优先遍历 AST，调用 visitor |
| **Generator** | `@babel/generator` | AST → 目标代码字符串 + SourceMap |
| **Types** | `@babel/types` | AST 节点类型定义 + 创建/判断/修改工具 |
| **Template** | `@babel/template` | 从代码字符串快速创建 AST 节点 |
| **Core** | `@babel/core` | 整合上述模块，提供 transform/parse API |
| **CLI** | `@babel/cli` | 命令行工具 `babel input.js -o output.js` |
| **Helpers** | `@babel/helpers` | 编译时注入的辅助函数（如 `_classCallCheck`） |
| **Runtime** | `@babel/runtime` | 运行时辅助函数库（供业务代码引用） |

**源码调用链示例**

```js
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const generator = require('@babel/generator').default;
const t = require('@babel/types');

// 1. Parse
const ast = parser.parse('const x = 1;');

// 2. Transform
traverse(ast, {
  VariableDeclaration(path) {
    // const → var
    path.node.kind = 'var';
  },
});

// 3. Generate
const output = generator(ast);
console.log(output.code); // "var x = 1;"
```

---

# 三、AST 抽象语法树深度解析

## 3.1 什么是 AST

**AST（Abstract Syntax Tree，抽象语法树）** 是源代码的树状结构表示，每个节点对应代码中的一个语法构造。

```
源代码：
  function add(a, b) {
    return a + b;
  }

AST（简化版树形结构）：
  Program (body: [...])
    └─ FunctionDeclaration
       ├─ id: Identifier (name: "add")
       ├─ params: [
       │    Identifier (name: "a"),
       │    Identifier (name: "b")
       │  ]
       └─ body: BlockStatement
            └─ body: [
                 ReturnStatement
                   └─ BinaryExpression
                        ├─ operator: "+"
                        ├─ left: Identifier (name: "a")
                        └─ right: Identifier (name: "b")
               ]
```

**AST 的本质**

| 维度 | 说明 |
|---|---|
| 数据结构 | 树（Tree），节点为 JSON 对象 |
| 生成方式 | 词法分析 → Tokens → 语法分析 → AST |
| 作用 | 让程序"理解"代码结构，是编译器、lint、格式化、IDE 的基础 |
| 消费方 | Babel、ESLint、Prettier、TypeScript、Webpack、Vite |

---

## 3.2 AST 节点类型

每个 AST 节点都有一个 `type` 字段，标识其语法类别。`@babel/types` 定义了所有节点类型。

### 常见节点类型速查

| 类型 | 说明 | 示例代码 |
|---|---|---|
| `Program` | 整个程序的根节点 | 整个文件 |
| `FunctionDeclaration` | 函数声明 | `function foo() {}` |
| `FunctionExpression` | 函数表达式 | `var f = function() {}` |
| `ArrowFunctionExpression` | 箭头函数 | `(a) => a + 1` |
| `VariableDeclaration` | 变量声明 | `const x = 1` |
| `VariableDeclarator` | 变量声明器 | `x = 1`（在 const/var/let 内） |
| `Identifier` | 标识符 | `x`, `foo`, `bar` |
| `Literal` / `StringLiteral` / `NumericLiteral` | 字面量 | `"hello"`, `42`, `true` |
| `BinaryExpression` | 二元表达式 | `a + b` |
| `AssignmentExpression` | 赋值表达式 | `x = 1` |
| `CallExpression` | 函数调用 | `foo(1, 2)` |
| `MemberExpression` | 成员访问 | `obj.prop` / `arr[0]` |
| `IfStatement` | if 语句 | `if (x) {}` |
| `ForStatement` | for 循环 | `for (let i...) {}` |
| `WhileStatement` | while 循环 | `while (x) {}` |
| `ReturnStatement` | return 语句 | `return x` |
| `BlockStatement` | 代码块 | `{ ... }` |
| `ExpressionStatement` | 表达式语句 | `foo();` |
| `ObjectExpression` | 对象字面量 | `{ a: 1 }` |
| `ArrayExpression` | 数组字面量 | `[1, 2, 3]` |
| `ClassDeclaration` | 类声明 | `class Foo {}` |
| `ClassExpression` | 类表达式 | `var C = class {}` |
| `ImportDeclaration` | import | `import x from 'mod'` |
| `ExportDefaultDeclaration` | export default | `export default x` |
| `JSXElement` | JSX 元素 | `<div />` |
| `TSInterfaceDeclaration` | TS 接口 | `interface Foo {}` |

### 节点公共属性

每个 AST 节点都包含以下公共属性：

```js
{
  type: 'Identifier',          // 节点类型
  start: 0,                    // 源码起始位置
  end: 5,                      // 源码结束位置
  loc: {                       // 位置信息
    start: { line: 1, column: 0 },
    end: { line: 1, column: 5 },
  },
  // ...类型特有属性
  name: 'add',
}
```

---

## 3.3 AST 生成示例

### 示例 1：变量声明 + 箭头函数

```js
// 源代码
const greet = (name) => `Hello, ${name}!`;
```

**对应的 AST**

```json
{
  "type": "Program",
  "body": [
    {
      "type": "VariableDeclaration",
      "kind": "const",
      "declarations": [
        {
          "type": "VariableDeclarator",
          "id": {
            "type": "Identifier",
            "name": "greet"
          },
          "init": {
            "type": "ArrowFunctionExpression",
            "id": null,
            "params": [
              {
                "type": "Identifier",
                "name": "name"
              }
            ],
            "body": {
              "type": "TemplateLiteral",
              "expressions": [
                {
                  "type": "Identifier",
                  "name": "name"
                }
              ],
              "quasis": [
                {
                  "type": "TemplateElement",
                  "value": {
                    "raw": "Hello, ",
                    "cooked": "Hello, "
                  },
                  "tail": false
                },
                {
                  "type": "TemplateElement",
                  "value": {
                    "raw": "!",
                    "cooked": "!"
                  },
                  "tail": true
                }
              ]
            },
            "async": false
          }
        }
      ]
    }
  ],
  "sourceType": "module"
}
```

### 示例 2：使用 @babel/parser 实战

```js
const parser = require('@babel/parser');

const code = `
  class Animal {
    constructor(name) {
      this.name = name;
    }
    speak() {
      return \`\${this.name} makes a sound.\`;
    }
  }
`;

const ast = parser.parse(code, {
  sourceType: 'module',
  plugins: ['classProperties'],
});

// 打印 AST
console.log(JSON.stringify(ast, null, 2));
```

### 在线 AST 查看工具

| 工具 | 地址 |
|---|---|
| AST Explorer | https://astexplorer.net/ |
| Babel REPL | https://babeljs.io/repl |
| TypeScript AST Viewer | https://ts-ast-viewer.com/ |

---

## 3.4 Visitor 访问者模式

**Visitor 模式** 是 Babel Transform 阶段的核心设计模式：为每种 AST 节点类型定义一个处理方法，遍历到该类型节点时自动调用。

### 基本结构

```js
const visitor = {
  // 进入 Identifier 节点时触发
  Identifier(path) {
    console.log('访问 Identifier:', path.node.name);
  },

  // 进入和离开都处理
  FunctionDeclaration: {
    enter(path) {
      console.log('进入函数声明:', path.node.id.name);
    },
    exit(path) {
      console.log('离开函数声明:', path.node.id.name);
    },
  },
};
```

### enter / exit 执行顺序

```
       enter(Identifier)     enter(FunctionDeclaration)
              ↓                        ↓
FunctionDeclaration → Identifier → ... → exit(Identifier) → exit(FunctionDeclaration)
     ↓                ↓                              ↑                    ↑
  enter               enter                         exit                 exit

执行顺序（深度优先）：
  1. enter(FunctionDeclaration)
  2.   enter(Identifier "foo")     ← 函数名
  3.   enter(Identifier "a")       ← 参数
  4.   exit(Identifier "a")
  5.   enter(Identifier "b")
  6.   exit(Identifier "b")
  7.   ... 函数体内部 ...
  8. exit(FunctionDeclaration)
```

### visitor 的合并

多个插件的 visitor 会被 Babel 自动合并为一个，按插件顺序依次执行。

```js
// 插件 A
const pluginA = {
  visitor: {
    Identifier(path) { /* A 的逻辑 */ },
  },
};

// 插件 B
const pluginB = {
  visitor: {
    Identifier(path) { /* B 的逻辑 */ },
  },
};

// 合并后：遍历到 Identifier 时先执行 A 再执行 B
// 等价于：
const merged = {
  visitor: {
    Identifier(path) {
      pluginA.visitor.Identifier(path);
      pluginB.visitor.Identifier(path);
    },
  },
};
```

---

## 3.5 Path 路径对象

在 Babel 中，visitor 回调函数接收的参数不是 AST 节点本身，而是 **Path 对象**。Path 封装了节点及其上下文关系。

### Path 的作用

```
AST 节点 (Node)          Path 对象
┌──────────────┐        ┌──────────────────────────┐
│ type: ...    │        │ node: AST 节点            │
│ ...属性      │  ←──   │ parent: 父节点            │
└──────────────┘        │ parentPath: 父 Path       │
                        │ scope: 作用域             │
                        │ key: 在父节点中的 key      │
                        │ container: 所在容器        │
                        └──────────────────────────┘
```

**为什么需要 Path？**

- AST 节点是纯数据（JSON 对象），无法知道自己的父节点是谁。
- Path 封装了节点之间的关系，支持向上查找、替换、删除等操作。

### Path 常用方法

```js
visitor = {
  Identifier(path) {
    const { node, parent, parentPath, scope } = path;

    // ---- 节点操作 ----
    // 替换当前节点
    path.replaceWith(t.numericLiteral(0));

    // 替换为多个节点
    path.replaceWithMultiple([node1, node2]);

    // 删除当前节点
    path.remove();

    // 在当前节点前插入
    path.insertBefore(t.expressionStatement(...));

    // 在当前节点后插入
    path.insertAfter(t.expressionStatement(...));

    // ---- 上下文查询 ----
    // 获取函数参数（如果当前在函数体内）
    const params = path.getFunctionParent().node.params;

    // 向上查找最近的指定类型节点
    const funcPath = path.findParent(p => p.isFunctionDeclaration());

    // 获取变量绑定
    const binding = path.scope.getBinding('someVar');
    // binding = { kind, constantViolations, path, references, ... }

    // ---- 作用域操作 ----
    // 生成唯一变量名（避免冲突）
    const newName = path.scope.generateUidIdentifier('temp');
    // → "_temp"

    // 重命名变量（会自动更新所有引用）
    path.scope.rename('oldName', 'newName');

    // ---- 类型判断 ----
    if (path.isIdentifier()) { }
    if (path.isMemberExpression()) { }
    if (path.isCallExpression()) { }

    // ---- 停止遍历 ----
    path.skip(); // 跳过当前节点的子节点遍历
    path.stop(); // 停止整个遍历
  },
};
```

### Scope 作用域

Path 中的 `scope` 属性提供作用域信息，用于变量分析和重命名。

```js
visitor = {
  FunctionDeclaration(path) {
    const { scope } = path;

    // 获取所有绑定
    scope.bindings; // { name: Binding, ... }

    // 检查变量是否已定义
    scope.hasBinding('myVar');

    // 检查自己的绑定（不包含父级）
    scope.hasOwnBinding('myVar');

    // 获取绑定信息
    const binding = scope.getBinding('myVar');
    // binding.kind: 'var' | 'let' | 'const' | 'param' | 'hoisted'
    // binding.path: 声明该变量的 Path
    // binding.references: 引用次数
    // binding.referenced: 是否被引用
    // binding.constant: 是否常量（无重新赋值）
    // binding.constantViolations: 重新赋值的 Path 数组
  },
};
```

---
