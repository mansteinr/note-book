# 四、Presets 预设详解

## 4.1 Preset 概念

**Preset（预设）** 是一组 Plugins 的集合，用于一键启用某个场景下的所有转换。

```js
// 不用 Preset：手动列举每个插件
{
  plugins: [
    '@babel/plugin-transform-arrow-functions',
    '@babel/plugin-transform-classes',
    '@babel/plugin-transform-template-literals',
    '@babel/plugin-transform-destructuring',
    // ... 几十个插件
  ],
}

// 用 Preset：一行搞定
{
  presets: ['@babel/preset-env'],
}
```

### Preset 的本质

```js
// @babel/preset-env 本质上是一个返回插件数组的函数
module.exports = function presetEnv(api, opts) {
  // 1. 读取 browserslist 配置
  const targets = normalizeTargets(opts.targets);

  // 2. 根据 targets 查询 compat-table
  //    决定哪些语法需要转换、哪些 API 需要 polyfill
  const plugins = filterPluginsByTargets(allPlugins, targets);

  // 3. 返回插件数组
  return plugins;
};
```

---

## 4.2 @babel/preset-env

`@babel/preset-env` 是最核心的预设，它**智能地**根据目标环境决定需要启用哪些转换插件和 polyfill。

### 核心特性

| 特性 | 说明 |
|---|---|
| **按需转换** | 根据 `targets` 自动决定哪些语法需要降级 |
| **语法转换** | ES6+ 新语法 → ES5 语法 |
| **Polyfill 注入** | 配合 `useBuiltIns` 自动引入缺失的 API |
| **debug 模式** | 输出转换详情，方便调试 |

### 配置示例

```js
// babel.config.js
module.exports = {
  presets: [
    [
      '@babel/preset-env',
      {
        // 目标环境
        targets: {
          chrome: '60',
          firefox: '60',
          safari: '11',
          ie: '11',
          node: 'current',
        },

        // 或使用 browserslist 字符串
        // targets: '> 0.25%, not dead',

        // 模块转换方式
        modules: 'auto', // 'amd' | 'umd' | 'systemjs' | 'commonjs' | 'cjs' | 'auto' | false

        // polyfill 策略（详见第九章）
        useBuiltIns: 'usage', // false | 'entry' | 'usage'
        corejs: { version: 3, proposals: true },

        // 是否启用 ES5→ES3 降级（IE6-8 兼容）
        loose: false,

        // 输出调试信息
        debug: false,

        // 指定包含/排除的插件
        include: ['transform-classes'],
        exclude: ['transform-typeof-symbol'],

        // 强制所有插件走 ES5 兼容路径
        forceAllTransforms: false,

        // spec 模式（更严格、更慢，用于验证）
        spec: false,
      },
    ],
  ],
};
```

### targets 配置详解

`targets` 决定了"目标环境是什么"，Babel 会只转换目标环境不支持的语法。

```js
// 方式 1：对象形式
targets: {
  chrome: '58',      // Chrome 58+
  ie: '11',           // IE 11
  firefox: '60',
  safari: '11',
  node: '12',
  edge: '17',
}

// 方式 2：browserslist 字符串
targets: '> 0.5%, last 2 versions, not dead, not ie 11'

// 方式 3：不配置 targets
// → Babel 会转换所有 ES6+ 语法（最保守）
```

### browserslist 配置文件

```json
// package.json 中的 browserslist 字段
{
  "browserslist": [
    "> 1%",
    "last 2 versions",
    "not dead",
    "not ie 11"
  ]
}
```

```ini
# 或独立文件 .browserslistrc
> 1%
last 2 versions
not dead
not ie 11
```

**常用查询语法**

| 语法 | 含义 |
|---|---|
| `> 1%` | 全球使用率 > 1% 的浏览器 |
| `last 2 versions` | 每个浏览器的最后 2 个版本 |
| `not dead` | 排除已停止维护的浏览器（如 IE 10） |
| `not ie 11` | 排除 IE 11 |
| `ie >= 11` | IE 11 及以上 |
| `since 2020` | 2020 年之后发布的浏览器 |
| `defaults` | `> 0.5%, last 2 versions, not dead` 的快捷写法 |

### debug 模式输出示例

```js
// babel.config.js
module.exports = {
  presets: [
    ['@babel/preset-env', { debug: true, targets: { ie: 11 } }],
  ],
};
```

```
@babel/preset-env: debug logs:
Using targets:
{
  "ie": "11"
}

Using modules transform: commonjs

Using plugins:
  transform-arrow-functions { ie }
  transform-classes { ie }
  transform-computed-properties { ie }
  transform-destructuring { ie }
  transform-for-of { ie }
  transform-template-literals { ie }
  transform-spread { ie }
  transform-object-super { ie }
  transform-shorthand-properties { ie }
  transform-sticky-regex { ie }
  transform-typeof-symbol { ie }
  transform-exponentiation-operator { ie }
  transform-async-to-generator { ie }
```

---

## 4.3 @babel/preset-react

用于转换 JSX 和 React 相关语法。

```js
// babel.config.js
module.exports = {
  presets: [
    [
      '@babel/preset-react',
      {
        // JSX 运行时模式（React 17+ 新转换）
        runtime: 'automatic', // 'classic'(默认) | 'automatic'

        // 开发模式（添加 __source / __self 调试信息）
        development: false,

        // 是否在字符串前加 /** @jsx */
        throwIfNamespace: true,

        // 自定义 pragma（classic 模式）
        pragma: 'React.createElement',
        pragmaFrag: 'React.Fragment',
      },
    ],
  ],
};
```

### classic vs automatic

```
Classic 模式（React 16 及之前默认）：
  每个文件顶部自动 import React from 'react'
  JSX → React.createElement(...)

Automatic 模式（React 17+ 推荐）：
  自动按需 import { jsx as _jsx } from 'react/jsx-runtime'
  无需手动 import React
  产物更小（不引入整个 React）
```

```jsx
// Classic 输出
import React from 'react';
const el = React.createElement('div', null, 'Hello');

// Automatic 输出
import { jsx as _jsx } from 'react/jsx-runtime';
const el = _jsx('div', { children: 'Hello' });
```

---

## 4.4 @babel/preset-typescript

用于剥离 TypeScript 类型注解，不进行类型检查。

```js
// babel.config.js
module.exports = {
  presets: [
    [
      '@babel/preset-typescript',
      {
        // 是否仅解析不转换（用于类型剥离场景）
        onlyRemoveTypeImports: false,

        // 是否启用 optimizeConstEnums
        optimizeConstEnums: false,

        // 允许的 namespace 模式
        allowNamespaces: true,

        // 是否允许 declare fields
        allowDeclareFields: false,
      },
    ],
  ],
};
```

**Babel vs tsc 处理 TypeScript 的差异**

| 维度 | Babel | tsc |
|---|---|---|
| 类型检查 | **不检查**，仅剥离类型 | 检查 + 剥离 |
| 编译速度 | 快（只做语法转换） | 慢（需类型推断） |
| 类型导入 | 需手动 `import type` | 自动 elide imports |
| const enum | 不支持（会报错或降级） | 支持 |
| namespace 嵌套 | 部分支持 | 完全支持 |
| 适用 | 大型项目（配合 IDE 检查） | 严格类型项目 |

---

## 4.5 Preset 执行顺序

**Presets 的执行顺序是逆序的**（从后往前），这是 Babel 的一个容易混淆的设计。

```js
// 配置
presets: ['@babel/preset-env', '@babel/preset-react', '@babel/preset-typescript']

// 执行顺序：
// 1. @babel/preset-typescript  ← 最后配置，最先执行
// 2. @babel/preset-react
// 3. @babel/preset-env         ← 最先配置，最后执行
```

**为什么是逆序？**

- 先剥离 TypeScript 类型（preset-typescript）。
- 再转换 JSX（preset-react）。
- 最后做语法降级（preset-env）。
- 这个顺序符合"从语法层面 → 语义层面"的处理逻辑。

**Plugin 的执行顺序是正序的**（从前往后）：

```js
plugins: ['pluginA', 'pluginB', 'pluginC']
// 执行顺序：A → B → C
```

---

# 五、Plugins 插件机制

## 5.1 Plugin 概念

**Plugin（插件）** 是 Babel 转换的最小单元，每个插件负责一种特定的语法转换。

```js
// 箭头函数转换插件
const arrowFunctionPlugin = require('@babel/plugin-transform-arrow-functions');

// 箭头函数 → 普通函数
const code = 'const fn = () => 1;';
const result = babel.transformSync(code, {
  plugins: [arrowFunctionPlugin],
});
console.log(result.code);
// var fn = function () { return 1; };
```

### Plugin 的分类

| 分类 | 包名格式 | 说明 |
|---|---|---|
| 已标准语法 | `@babel/plugin-transform-*` | ES6+ 已进入标准，稳定 |
| 提案阶段语法 | `@babel/plugin-proposal-*` | Stage 0-3 提案，可能变动 |
| 仅解析 | `@babel/plugin-syntax-*` | 只让 parser 能解析，不转换 |

---

## 5.2 Plugin 执行顺序

**Plugins 正序执行（从前往后），Presets 逆序执行（从后往前）。**

```
完整执行顺序：
  1. Plugins（正序）
     plugin[0] → plugin[1] → ... → plugin[n]

  2. Presets（逆序）
     preset[n] → preset[n-1] → ... → preset[0]
```

**为什么要先 Plugin 后 Preset？**

- Plugin 是单一转换，应该先执行。
- Preset 是插件集合，通常做整体降级，后执行。

---

## 5.3 Plugin 与 Preset 执行顺序

```
配置文件示例：
  plugins: ['plugin-A', 'plugin-B']
  presets: ['preset-1', 'preset-2']

实际执行顺序：
  ┌────────────────────────────────────────┐
  │ 1. plugin-A 的 visitor 注册（先注册）   │
  │ 2. plugin-B 的 visitor 注册            │
  │ 3. preset-2 展开为插件，逆序注册        │
  │ 4. preset-1 展开为插件，逆序注册        │
  │                                        │
  │ → 遍历 AST 时，按注册顺序依次执行       │
  │   plugin-A → plugin-B → preset-2's plugins → preset-1's plugins
  └────────────────────────────────────────┘
```

---

## 5.4 常用插件清单

### 语法转换插件（高频）

| 插件 | 转换内容 |
|---|---|
| `@babel/plugin-transform-arrow-functions` | 箭头函数 → 普通函数 |
| `@babel/plugin-transform-classes` | class → 构造函数 + 原型链 |
| `@babel/plugin-transform-template-literals` | 模板字符串 → 字符串拼接 |
| `@babel/plugin-transform-destructuring` | 解构赋值 → 临时变量 |
| `@babel/plugin-transform-spread` | 展开运算符 → apply/concat |
| `@babel/plugin-transform-async-to-generator` | async/await → generator |
| `@babel/plugin-transform-block-scoping` | let/const → var |
| `@babel/plugin-transform-computed-properties` | 计算属性 → Object.defineProperty |
| `@babel/plugin-transform-shorthand-properties` | 简写属性 → 完整形式 |
| `@babel/plugin-transform-for-of` | for...of → for + Symbol.iterator |
| `@babel/plugin-transform-object-super` | super → Object.getPrototypeOf |
| `@babel/plugin-transform-parameters` | 默认参数 / 剩余参数 |
| `@babel/plugin-transform-exponentiation-operator` | `**` → Math.pow |
| `@babel/plugin-transform-optional-chaining` | `?.` → 三元判断 |
| `@babel/plugin-transform-nullish-coalescing` | `??` → 三元判断 |
| `@babel/plugin-transform-object-rest-spread` | 对象剩余/展开 |
| `@babel/plugin-proposal-logical-assignment-operators` | `\|\|= &&= ??=` |
| `@babel/plugin-proposal-numeric-separator` | `1_000_000` → `1000000` |

### 实用功能插件

| 插件 | 作用 |
|---|---|
| `@babel/plugin-proposal-class-properties` | 类属性直接赋值 |
| `@babel/plugin-proposal-private-methods` | 私有方法 `#method` |
| `@babel/plugin-proposal-decorators` | 装饰器 `@decorator` |
| `@babel/plugin-syntax-dynamic-import` | `import()` 动态导入 |
| `@babel/plugin-transform-runtime` | 抽取 helper 函数，避免重复注入 |

---

# 六、配置文件体系

## 6.1 babel.config.js vs .babelrc

Babel 7 引入了两种配置文件，用途不同：

| 维度 | `babel.config.js` | `.babelrc` / `.babelrc.json` |
|---|---|---|
| 作用范围 | **整个项目**（Monorepo 友好） | **单个目录及其子目录** |
| 文件类型 | JS / JSON | JSON |
| 推荐场景 | 项目根配置 | 包级别/目录级别配置 |
| node_modules 处理 | 可以配置 | 默认不处理 |
| Monorepo | **推荐**（一个配置覆盖所有子包） | 不推荐 |

### 配置文件优先级

```
Babel 查找配置的顺序（从高到低）：
  1. 代码内联配置（transform 的 options 参数）
  2. babel.config.js / babel.config.json
  3. .babelrc / .babelrc.json / .babelrc.js
  4. package.json 中的 "babel" 字段
  5. babel.config函数返回的配置
```

### Monorepo 配置示例

```
my-monorepo/
├── babel.config.js          ← 全局配置（覆盖所有包）
├── package.json
├── packages/
│   ├── package-a/
│   │   ├── .babelrc.json   ← 包级别配置（覆盖/扩展全局）
│   │   └── src/
│   └── package-b/
│       ├── .babelrc.json
│       └── src/
```

```js
// 根目录 babel.config.js
module.exports = {
  presets: ['@babel/preset-env'],
  plugins: [],
  // 允许 overrides 对不同路径应用不同配置
  overrides: [
    {
      test: ['./packages/react-app'],  // 只对 React 包生效
      presets: ['@babel/preset-react'],
    },
    {
      test: ['./packages/ts-lib'],     // 只对 TS 包生效
      presets: ['@babel/preset-typescript'],
    },
  ],
};
```

---

## 6.2 配置项详解

```js
// babel.config.js 完整配置示例
module.exports = function (api) {
  // 根据 NODE_ENV 切换配置
  const isProduction = api.env('production');
  const isDevelopment = api.env('development');
  const isTest = api.env('test');

  // 缓存配置，提升构建速度
  api.cache.using(() => process.env.NODE_ENV);

  return {
    // 预设
    presets: [
      ['@babel/preset-env', { targets: { node: 'current' } }],
      '@babel/preset-typescript',
      ['@babel/preset-react', { runtime: 'automatic' }],
    ],

    // 插件
    plugins: [
      // 生产环境移除 prop-types
      isProduction && ['transform-react-remove-prop-types', { removeImport: true }],

      // 开发环境启用 React 快速刷新
      isDevelopment && 'react-refresh/babel',

      // 装饰器支持（必须在 class-properties 之前）
      ['@babel/plugin-proposal-decorators', { legacy: true }],
      ['@babel/plugin-proposal-class-properties', { loose: true }],

      // lodash 按需引入
      'lodash',

      // 按需引入组件库
      ['import', {
        libraryName: 'antd',
        libraryDirectory: 'es',
        style: true,
      }],

      // 路径别名
      ['module-resolver', {
        alias: {
          '@': './src',
        },
      }],
    ].filter(Boolean),

    // 仅对特定文件覆盖配置
    overrides: [
      {
        test: /node_modules\/lodash/,
        sourceType: 'script',
      },
    ],

    // 忽略文件
    ignore: [
      /node_modules/,
      /\.test\.js$/,
    ],

    // 仅处理匹配的文件
    only: [
      './src',
      './tests',
    ],

    // SourceMap 生成
    sourceMaps: isDevelopment ? 'inline' : false,

    // 配置文件注释（Babel 7.9+）
    comments: false,

    // 额外传递给插件的配置
    passPerPreset: false,
  };
};
```

### api.env() 环境判断

```js
module.exports = function (api) {
  // api.env() === process.env.BABEL_ENV || process.env.NODE_ENV
  const env = api.env();

  if (env === 'production') {
    return productionConfig;
  } else if (env === 'test') {
    return testConfig;
  } else {
    return developmentConfig;
  }
};
```

### api.cache 缓存

```js
module.exports = function (api) {
  // 方式 1：永久缓存（配置不变就一直用缓存）
  api.cache(true);

  // 方式 2：永不缓存（每次重新计算）
  api.cache(false);

  // 方式 3：根据环境变量缓存
  api.cache.using(() => process.env.NODE_ENV);

  // 方式 4：根据回调值缓存（值变化才更新）
  api.cache.using(() => JSON.stringify({
    env: process.env.NODE_ENV,
    targets: readBrowserslist(),
  }));

  return { /* config */ };
};
```

---

## 6.3 targets 目标环境

`targets` 是 preset-env 的核心配置，决定哪些转换需要启用。

### 配置方式

```js
// 方式 1：对象
targets: {
  chrome: '58',
  ie: '11',
  firefox: '60',
}

// 方式 2：browserslist 字符串
targets: '> 0.25%, not dead'

// 方式 3：从 package.json 或 .browserslistrc 读取
// 不配置 targets，Babel 自动使用 browserslist

// 方式 4：指定 esmodules 支持
targets: { esmodules: true }  // 只支持原生 ESM 的浏览器
```

### targets 与转换的关系

```
targets 配置                          转换内容
──────────────────────────────────────────────────────────────
不配置 targets                        转换所有 ES6+ 语法（最保守）
targets: { ie: 11 }                   转换 IE 11 不支持的所有语法
targets: { chrome: 90 }              几乎不转换（Chrome 90 支持大部分新语法）
targets: { node: 'current' }          几乎不转换（当前 Node 版本）
```

---

# 七、工程配置实战

## 7.1 Webpack 集成

### 基础配置

```js
// webpack.config.js
const path = require('path');

module.exports = {
  module: {
    rules: [
      {
        test: /\.(js|jsx|ts|tsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            // 指向 babel.config.js
            configFile: path.resolve(__dirname, 'babel.config.js'),
            // 开启缓存
            cacheDirectory: true,
            // 缓存压缩
            cacheCompression: isProduction,
          },
        },
      },
    ],
  },
};
```

### babel-loader 性能优化

```js
{
  test: /\.(js|jsx|ts|tsx)$/,
  // 优化 1：只处理 src 目录
  include: path.resolve(__dirname, 'src'),

  use: {
    loader: 'babel-loader',
    options: {
      // 优化 2：开启缓存（二次构建速度提升 90%+）
      cacheDirectory: true,

      // 优化 3：生产环境压缩缓存
      cacheCompression: process.env.NODE_ENV === 'production',

      // 优化 4：并行处理（thread-loader）
      // 配合 thread-loader 使用
    },
  },
},
```

### 配合 thread-loader 并行编译

```js
const os = require('os');

module.exports = {
  module: {
    rules: [
      {
        test: /\.(js|ts)$/,
        include: path.resolve('src'),
        use: [
          {
            loader: 'thread-loader',
            options: {
              workers: os.cpus().length - 1,  // CPU 核数 - 1
              poolTimeout: 2000,
            },
          },
          {
            loader: 'babel-loader',
            options: {
              cacheDirectory: true,
            },
          },
        ],
      },
    ],
  },
};
```

---

## 7.2 Vite 集成

Vite 在开发环境使用 esbuild 做快速转译（不做 polyfill），生产构建用 Rollup + @rollup/plugin-babel 或 vite-plugin-babel。

### 开发环境

Vite 默认用 esbuild 转译 TS/JSX，不经过 Babel。若需要 Babel 插件（如自动国际化），需显式配置：

```js
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [
    react({
      // 使用 Babel 处理 JSX（而非默认的 esbuild）
      babel: {
        // 指定 Babel 配置文件
        configFile: true,
        // 额外插件
        plugins: [
          'babel-plugin-macros',
          // 自定义插件
          './babel-plugins/auto-track.js',
        ],
      },
    }),
  ],
});
```

### 生产环境

```js
// vite.config.js
import { defineConfig } from 'vite';
import babel from '@rollup/plugin-babel';

export default defineConfig({
  build: {
    rollupOptions: {
      plugins: [
        babel({
          babelHelpers: 'bundled',
          exclude: 'node_modules/**',
          extensions: ['.js', '.jsx', '.ts', '.tsx'],
        }),
      ],
    },
    // polyfill
    target: 'es2015', // 或 ['es2015', 'chrome 60']
  },
});
```

---

## 7.3 生产环境配置最佳实践

### React 项目完整配置

```js
// babel.config.js
module.exports = function (api) {
  const isProduction = api.env('production');
  const isDevelopment = api.env('development');
  const isTest = api.env('test');

  api.cache.using(() => process.env.NODE_ENV);

  return {
    presets: [
      [
        '@babel/preset-env',
        {
          // 测试环境用当前 Node，其他环境用 browserslist
          targets: isTest ? { node: 'current' } : undefined,
          modules: isTest ? 'commonjs' : false, // 生产环境保留 ESM 给 Webpack tree shake
          useBuiltIns: 'entry',
          corejs: 3,
        },
      ],
      [
        '@babel/preset-react',
        {
          runtime: 'automatic',    // React 17+ 新 JSX 转换
          development: isDevelopment,
        },
      ],
      '@babel/preset-typescript',
    ],

    plugins: [
      // 装饰器必须在 class properties 之前
      ['@babel/plugin-proposal-decorators', { legacy: true }],
      ['@babel/plugin-proposal-class-properties', { loose: false }],

      // @babel/plugin-transform-runtime 抽取 helper
      ['@babel/plugin-transform-runtime', {
        corejs: 3,
        helpers: true,
        regenerator: true,
        useESModules: !isTest,
      }],

      // 开发环境：React 快速刷新
      isDevelopment && 'react-refresh/babel',

      // 生产环境：移除 PropTypes
      isProduction && [
        'transform-react-remove-prop-types',
        { removeImport: true },
      ],

      // antd 按需引入
      ['import', {
        libraryName: 'antd',
        libraryDirectory: 'es',
        style: true,
      }],

      // lodash 按需引入
      'lodash',

      // 路径别名（也可在 webpack/tsconfig 配置）
      ['module-resolver', {
        root: ['./src'],
        alias: {
          '@': './src',
          '@components': './src/components',
          '@utils': './src/utils',
        },
      }],
    ].filter(Boolean),

    // 忽略测试文件和 mock
    ignore: isProduction ? [/\.test\.(js|ts)$/, /__mocks__/] : [],
  };
};
```

### Vue 3 项目配置

```js
// babel.config.js
module.exports = {
  presets: [
    [
      '@babel/preset-env',
      {
        targets: { node: 'current' }, // SSR 兼容
        modules: false,
      },
    ],
    '@babel/preset-typescript',
  ],
  plugins: [
    ['@babel/plugin-transform-runtime', { corejs: 3 }],
    // Vue JSX 支持
    '@vue/babel-plugin-jsx',
  ],
};
```

---
