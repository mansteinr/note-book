# Vue 3 + Element Plus + Pinia 前端工程化方案

> 本方案面向中大型前端项目，基于 Vue 3 + Element Plus + Pinia 技术栈，系统覆盖项目结构、构建配置、代码规范、开发环境、测试策略、部署流程、性能优化、依赖管理、全局错误统一处理等九大核心领域。方案遵循现代前端工程化最佳实践，确保项目具备可实施性、可维护性与可扩展性。

---

## 目录

- [一、总体设计原则与技术栈选型](#一总体设计原则与技术栈选型)
- [二、项目目录结构设计](#二项目目录结构设计)
- [三、构建流程配置](#三构建流程配置)
- [四、代码规范与质量控制](#四代码规范与质量控制)
- [五、开发环境优化](#五开发环境优化)
- [六、测试策略](#六测试策略)
- [七、部署流程](#七部署流程)
- [八、性能优化措施](#八性能优化措施)
- [九、依赖管理机制](#九依赖管理机制)
- [十、全局错误统一处理机制](#十全局错误统一处理机制)
- [附录 实施路线图与工具速查](#附录-实施路线图与工具速查)

---

## 一、总体设计原则与技术栈选型

### 1.1 设计原则

| 原则 | 说明 |
| --- | --- |
| **可实施性** | 方案落地有具体配置与代码示例，可直接复制使用 |
| **可维护性** | 规范统一、结构清晰、文档完善，新人 1 天上手 |
| **可扩展性** | 模块化设计，新增功能不影响既有代码 |
| **可测试性** | 核心逻辑单测覆盖，关键流程 E2E 保障 |
| **一致性** | 代码风格、目录结构、命名规范全团队统一 |

### 1.2 技术栈选型

| 领域 | 选型 | 版本 | 选型理由 |
| --- | --- | --- | --- |
| **框架** | Vue 3 | ^3.4 | Composition API、性能提升、TypeScript 支持 |
| **构建** | Vite | ^5.0 | 极速冷启动、HMR、Rollup 打包 |
| **语言** | TypeScript | ^5.3 | 类型安全、IDE 支持、重构友好 |
| **UI 库** | Element Plus | ^2.5 | 企业级组件丰富、Vue 3 原生、按需引入 |
| **状态管理** | Pinia | ^2.1 | Vue 3 官方推荐、TS 友好、DevTools 集成 |
| **路由** | Vue Router | ^4.2 | 官方路由、动态路由、导航守卫 |
| **HTTP** | Axios | ^1.6 | 拦截器、取消请求、广泛使用 |
| **CSS** | SCSS + CSS Module | - | 变量、嵌套、样式隔离 |
| **代码规范** | ESLint + Prettier + Stylelint | - | 代码质量、格式统一、样式规范 |
| **Git Hook** | Husky + lint-staged | - | 提交前检查 |
| **提交规范** | Commitizen + commitlint | - | 规范化提交信息 |
| **单元测试** | Vitest | ^1.0 | Vite 原生、Jest 兼容、极速 |
| **E2E 测试** | Playwright | ^1.40 | 跨浏览器、自动等待、录制 |
| **Mock** | MSW | ^2.0 | Service Worker 拦截、开发/测试统一 |

### 1.3 Node 与包管理器

```json
{
  "engines": {
    "node": ">=18.19.0",
    "pnpm": ">=8.15.0"
  }
}
```

- **Node LTS**：18.19+（Vite 5 要求）
- **包管理器**：pnpm（速度快、磁盘节省、严格依赖）

---

## 二、项目目录结构设计

### 2.1 目录结构

```
vue3-admin/
├── .vscode/                    # VS Code 配置
│   ├── extensions.json         # 推荐插件
│   └── settings.json           # 项目设置
├── .husky/                     # Git Hooks
│   ├── pre-commit
│   └── commit-msg
├── .env                        # 环境变量（基础）
├── .env.development            # 开发环境
├── .env.staging                # 预发布环境
├── .env.production             # 生产环境
├── .eslintrc.cjs               # ESLint 配置
├── .prettierrc                 # Prettier 配置
├── .stylelintrc.cjs            # Stylelint 配置
├── .gitignore
├── .editorconfig               # 编辑器统一配置
├── .nvmrc                      # Node 版本
├── package.json
├── pnpm-lock.yaml
├── tsconfig.json               # TS 配置
├── tsconfig.node.json
├── vite.config.ts              # Vite 配置
├── vitest.config.ts            # 测试配置
├── playwright.config.ts        # E2E 配置
├── index.html
├── public/                     # 静态资源（不处理）
│   └── favicon.ico
└── src/
    ├── main.ts                 # 应用入口
    ├── App.vue                 # 根组件
    ├── assets/                 # 静态资源（会处理）
    │   ├── images/
    │   ├── icons/              # SVG 图标（自动注册）
    │   └── styles/             # 全局样式
    │       ├── variables.scss  # SCSS 变量
    │       ├── mixins.scss     # Mixin
    │       ├── reset.scss      # 重置样式
    │       └── index.scss      # 全局入口
    ├── components/             # 全局通用组件
    │   ├── BaseTable/          # 基础表格
    │   │   ├── index.vue
    │   │   └── types.ts
    │   ├── BaseForm/           # 基础表单
    │   ├── BaseDialog/         # 基础弹窗
    │   ├── BaseUpload/         # 基础上传
    │   └── BaseChart/          # 基础图表
    ├── composables/            # 组合式函数
    │   ├── useTable.ts         # 表格逻辑
    │   ├── useForm.ts          # 表单逻辑
    │   ├── useDialog.ts        # 弹窗逻辑
    │   ├── usePermission.ts    # 权限
    │   └── useTheme.ts         # 主题
    ├── directives/             # 自定义指令
    │   ├── permission.ts       # v-permission
    │   ├── debounce.ts         # v-debounce
    │   └── index.ts
    ├── enums/                  # 枚举
    │   └── index.ts
    ├── hooks/                  # 与 composables 区分（业务 hooks）
    │   └── useUser.ts
    ├── layouts/                # 布局组件
    │   ├── default/
    │   │   ├── index.vue
    │   │   ├── Header.vue
    │   │   ├── Sidebar.vue
    │   │   └── Breadcrumb.vue
    │   └── blank/
    │       └── index.vue
    ├── router/                 # 路由
    │   ├── index.ts            # 路由实例
    │   ├── routes.ts           # 静态路由
    │   ├── guards.ts           # 导航守卫
    │   └── modules/            # 路由模块
    │       ├── user.ts
    │       └── order.ts
    ├── stores/                 # Pinia 状态
    │   ├── index.ts            # Pinia 实例
    │   ├── modules/
    │   │   ├── user.ts         # 用户状态
    │   │   ├── app.ts          # 应用状态（侧边栏、主题）
    │   │   ├── permission.ts   # 权限路由
    │   │   └── tagsView.ts     # 标签页
    │   └── types.ts
    ├── api/                    # API 接口
    │   ├── request.ts          # Axios 封装
    │   ├── types/              # 接口类型
    │   │   └── common.ts
    │   └── modules/
    │       ├── user.ts
    │       └── order.ts
    ├── utils/                  # 工具函数
    │   ├── request.ts          # 请求工具
    │   ├── auth.ts             # 鉴权工具
    │   ├── storage.ts          # 本地存储
    │   ├── validate.ts         # 校验工具
    │   ├── format.ts           # 格式化
    │   └── download.ts         # 下载工具
    ├── types/                  # 全局类型
    │   ├── global.d.ts
    │   ├── env.d.ts
    │   └── shims-vue.d.ts
    ├── views/                  # 页面
    │   ├── login/
    │   │   └── index.vue
    │   ├── dashboard/
    │   │   └── index.vue
    │   ├── system/
    │   │   ├── user/
    │   │   │   ├── index.vue
    │   │   │   └── components/
    │   │   └── role/
    │   ├── error/
    │   │   ├── 404.vue
    │   │   └── 403.vue
    │   └── profile/
    ├── constants/              # 常量
    │   └── index.ts
    ├── plugins/                # 插件
    │   ├── elementPlus.ts      # Element Plus
    │   ├── pinia.ts
    │   └── errorHandler.ts
    ├── mocks/                  # Mock 数据
    │   ├── index.ts
    │   └── modules/
    │       └── user.ts
    └── tests/                  # 测试
        ├── unit/
        │   ├── utils/
        │   └── composables/
        └── e2e/
            └── login.spec.ts
```

### 2.2 命名规范

| 类型 | 规范 | 示例 |
| --- | --- | --- |
| **目录** | kebab-case | `user-management/` |
| **组件文件** | PascalCase | `UserList.vue` |
| **页面文件** | index.vue | `views/user/index.vue` |
| **TS 文件** | camelCase | `useTable.ts` |
| **常量** | UPPER_SNAKE | `MAX_RETRY` |
| **类型** | PascalCase | `UserInfo` |
| **CSS 类** | kebab-case + BEM | `.user-list__item--active` |

### 2.3 组件分类规范

```
组件层级：
├── 基础组件（Base*）：components/ 下，纯展示，无业务逻辑
├── 业务组件：views/xxx/components/ 下，含业务逻辑
├── 布局组件：layouts/ 下，页面骨架
└── 页面组件：views/ 下，路由对应页面
```

---

## 三、构建流程配置

### 3.1 Vite 配置

```typescript
// vite.config.ts
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'
import { visualizer } from 'rollup-plugin-visualizer'
import gzipPlugin from 'rollup-plugin-gzip'
import { generateAlias, generateProxy } from './build/vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  const isProd = mode === 'production'

  return {
    base: env.VITE_BASE_URL || '/',
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
        '#': resolve(__dirname, 'src/types'),
      },
    },
    plugins: [
      vue(),
      // 自动导入 Vue/Vue Router/Pinia API
      AutoImport({
        imports: ['vue', 'vue-router', 'pinia'],
        resolvers: [ElementPlusResolver()],
        dts: 'src/types/auto-imports.d.ts',
        eslintrc: { enabled: true },
      }),
      // 自动注册组件
      Components({
        resolvers: [ElementPlusResolver()],
        dts: 'src/types/components.d.ts',
        dirs: ['src/components'],
      }),
      // SVG 图标
      createSvgIconsPlugin({
        iconDirs: [resolve(__dirname, 'src/assets/icons')],
        symbolId: 'icon-[dir]-[name]',
      }),
      // 打包分析（仅生产）
      isProd && visualizer({
        filename: 'dist/stats.html',
        gzipSize: true,
        brotliSize: true,
      }),
      // Gzip 压缩（生产）
      isProd && gzipPlugin({ ext: '.gz' }),
    ],
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `@use "@/assets/styles/variables.scss" as *;`,
        },
      },
    },
    server: {
      host: '0.0.0.0',
      port: 5173,
      open: true,
      proxy: generateProxy(env),
      cors: true,
    },
    build: {
      target: 'es2015',
      outDir: 'dist',
      assetsDir: 'assets',
      sourcemap: !isProd,
      minify: 'esbuild',
      chunkSizeWarningLimit: 2000,
      rollupOptions: {
        output: {
          // 入口文件
          entryFileNames: 'assets/js/[name]-[hash].js',
          // 静态资源
          chunkFileNames: 'assets/js/[name]-[hash].js',
          assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
          // 手动分包
          manualChunks: {
            'vue-vendor': ['vue', 'vue-router', 'pinia'],
            'element-plus': ['element-plus'],
            'echarts': ['echarts'],
            'utils-vendor': ['axios', 'lodash-es', 'dayjs'],
          },
        },
      },
    },
    optimizeDeps: {
      include: [
        'vue',
        'vue-router',
        'pinia',
        'axios',
        'element-plus',
        'lodash-es',
        'dayjs',
      ],
    },
  }
})
```

### 3.2 环境变量配置

```bash
# .env（基础配置）
VITE_APP_TITLE=Vue3 Admin
VITE_APP_BASE_API=/api

# .env.development
VITE_APP_ENV=development
VITE_APP_BASE_API=/api
VITE_APP_MOCK=true
VITE_APP_PROXY_TARGET=http://localhost:3000

# .env.staging
VITE_APP_ENV=staging
VITE_APP_BASE_API=https://staging-api.example.com
VITE_APP_MOCK=false

# .env.production
VITE_APP_ENV=production
VITE_APP_BASE_API=https://api.example.com
VITE_APP_MOCK=false
```

### 3.3 TypeScript 配置

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ESNext",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "jsx": "preserve",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "lib": ["ESNext", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "#/*": ["src/types/*"]
    },
    "types": ["vite/client", "element-plus/global"]
  },
  "include": [
    "src/**/*.ts",
    "src/**/*.d.ts",
    "src/**/*.tsx",
    "src/**/*.vue",
    "tests/**/*.ts"
  ],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 3.4 package.json scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc --noEmit && vite build",
    "build:staging": "vue-tsc --noEmit && vite build --mode staging",
    "preview": "vite preview",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx --fix",
    "lint:style": "stylelint \"src/**/*.{css,scss,vue}\" --fix",
    "format": "prettier --write src/",
    "type-check": "vue-tsc --noEmit",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest run --coverage",
    "test:e2e": "playwright test",
    "prepare": "husky install",
    "commit": "git-cz"
  }
}
```

---

## 四、代码规范与质量控制

### 4.1 ESLint 配置

```javascript
// .eslintrc.cjs
module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
    es2023: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:vue/vue3-recommended',
    '@vue/eslint-config-typescript',
    '@vue/eslint-config-prettier',
    './.eslintrc-auto-import.json',
  ],
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@typescript-eslint/parser',
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  rules: {
    // Vue 规则
    'vue/multi-word-component-names': 'off',
    'vue/define-macros-order': ['error', { order: ['defineProps', 'defineEmits'] }],
    'vue/component-name-in-template-casing': ['error', 'PascalCase'],
    'vue/component-tags-order': ['error', { order: ['script', 'template', 'style'] }],
    'vue/block-order': ['error', { order: ['script', 'template', 'style'] }],
    
    // TypeScript 规则
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/consistent-type-imports': 'error',
    '@typescript-eslint/no-non-null-assertion': 'off',
    
    // 通用规则
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'no-debugger': 'warn',
    'prefer-const': 'error',
    'no-var': 'error',
    'eqeqeq': ['error', 'always'],
  },
}
```

### 4.2 Prettier 配置

```json
// .prettierrc
{
  "semi": false,
  "singleQuote": true,
  "trailingComma": "es5",
  "tabWidth": 2,
  "useTabs": false,
  "printWidth": 100,
  "endOfLine": "lf",
  "arrowParens": "always",
  "vueIndentScriptAndStyle": false,
  "htmlWhitespaceSensitivity": "ignore"
}
```

```javascript
// .prettierignore
dist
node_modules
public
*.md
auto-imports.d.ts
components.d.ts
```

### 4.3 Stylelint 配置

```javascript
// .stylelintrc.cjs
module.exports = {
  extends: [
    'stylelint-config-standard',
    'stylelint-config-standard-scss',
    'stylelint-config-recommended-vue/scss',
  ],
  rules: {
    'selector-class-pattern': null,
    'no-descending-specificity': null,
    'scss/at-rule-no-unknown': true,
    'unit-no-unknown': true,
    'color-no-invalid-hex': true,
    'declaration-block-no-duplicate-properties': true,
    'no-duplicate-selectors': true,
    'max-nesting-depth': [3, { message: '嵌套不超过 3 层' }],
  },
}
```

### 4.4 EditorConfig

```ini
# .editorconfig
root = true

[*]
charset = utf-8
indent_style = space
indent_size = 2
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.md]
trim_trailing_whitespace = false
```

### 4.5 Git Hook 配置

```bash
# 安装 Husky
pnpm add -D husky lint-staged
pnpm exec husky install
pnpm exec husky add .husky/pre-commit
pnpm exec husky add .husky/commit-msg
```

```bash
# .husky/pre-commit
pnpm exec lint-staged
```

```bash
# .husky/commit-msg
pnpm exec commitlint --edit $1
```

```json
// package.json
{
  "lint-staged": {
    "*.{vue,js,jsx,ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{css,scss,vue}": ["stylelint --fix"],
    "*.{md,json,yml}": ["prettier --write"]
  }
}
```

### 4.6 提交规范

```bash
pnpm add -D @commitlint/cli @commitlint/config-conventional commitizen cz-conventional-changelog
```

```javascript
// commitlint.config.cjs
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',     // 新功能
        'fix',      // 修复
        'docs',     // 文档
        'style',    // 格式（不影响功能）
        'refactor', // 重构
        'perf',     // 性能优化
        'test',     // 测试
        'build',    // 构建
        'ci',       // CI 配置
        'chore',    // 杂务
        'revert',   // 回滚
      ],
    ],
    'subject-max-length': [2, 'always', 72],
  },
}
```

```json
// package.json
{
  "config": {
    "commitizen": {
      "path": "cz-conventional-changelog"
    }
  }
}
```

提交示例：

```
feat(user): 添加用户列表分页功能
fix(order): 修复订单金额计算错误
perf(table): 优化大数据表格渲染性能
docs(readme): 更新部署文档
```

### 4.7 代码审查清单

| 审查项 | 说明 |
| --- | --- |
| 功能正确 | 代码是否实现需求 |
| 命名清晰 | 变量/函数/组件命名是否达意 |
| 单一职责 | 函数/组件是否职责单一 |
| 无冗余 | 是否有重复代码可抽取 |
| 类型完整 | TypeScript 类型是否完整 |
| 边界处理 | 空值、异常、边界是否处理 |
| 性能考虑 | 是否有不必要的渲染/计算 |
| 安全性 | XSS、敏感信息是否处理 |

---

## 五、开发环境优化

### 5.1 VS Code 配置

```json
// .vscode/settings.json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit",
    "source.fixAll.stylelint": "explicit"
  },
  "eslint.validate": ["javascript", "typescript", "vue"],
  "stylelint.validate": ["css", "scss", "vue"],
  "[vue]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "files.associations": {
    "*.vue": "vue"
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/dist": true,
    "**/pnpm-lock.yaml": true
  }
}
```

```json
// .vscode/extensions.json
{
  "recommendations": [
    "Vue.volar",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "stylelint.vscode-stylelint",
    "editorconfig.editorconfig",
    "antfu.iconify",
    "lokalise.i18n-ally",
    "eamodio.gitlens"
  ]
}
```

### 5.2 路径别名配置

Vite、TypeScript、ESLint 三处需同步：

```typescript
// vite.config.ts
resolve: {
  alias: {
    '@': resolve(__dirname, 'src'),
    '#': resolve(__dirname, 'src/types'),
  }
}
```

```json
// tsconfig.json
"paths": {
  "@/*": ["src/*"],
  "#/*": ["src/types/*"]
}
```

### 5.3 Mock 数据方案

```bash
pnpm add -D msw
```

```typescript
// src/mocks/index.ts
import { setupWorker } from 'msw/browser'
import { userHandlers } from './modules/user'

export const worker = setupWorker(...userHandlers)

// main.ts
async function enableMocking() {
  if (import.meta.env.VITE_APP_MOCK !== 'true') return
  const { worker } = await import('./mocks')
  return worker.start({
    onUnhandledRequest: 'bypass',
  })
}

enableMocking().then(() => {
  const app = createApp(App)
  app.mount('#app')
})
```

```typescript
// src/mocks/modules/user.ts
import { http, HttpResponse } from 'msw'

export const userHandlers = [
  http.get('/api/users', () => {
    return HttpResponse.json({
      code: 0,
      data: {
        list: [
          { id: 1, name: '张三', email: 'zhangsan@example.com' },
        ],
        total: 1,
      },
    })
  }),
  
  http.post('/api/login', async ({ request }) => {
    const body = await request.json()
    if (body.username === 'admin') {
      return HttpResponse.json({
        code: 0,
        data: { token: 'mock-token-123' },
      })
    }
    return HttpResponse.json({ code: 401, message: '用户名或密码错误' }, { status: 401 })
  }),
]
```

### 5.4 热更新优化

```typescript
// vite.config.ts
server: {
  hmr: {
    overlay: false,  // 关闭错误遮罩（用控制台）
  },
}
```

### 5.5 开发工具集成

**Vue DevTools 7**：

```bash
pnpm add -D vite-plugin-vue-devtools
```

```typescript
// vite.config.ts
import VueDevTools from 'vite-plugin-vue-devtools'

plugins: [
  VueDevTools(),
]
```

---

## 六、测试策略

### 6.1 测试金字塔

```
        ▲
        │   E2E 测试（5%）
        │   关键流程：登录、下单、支付
        │
        │  集成测试（15%）
        │  组件交互：表单提交、列表加载
        │
        │ 单元测试（80%）
        │ 工具函数、composables、纯组件
        ▼
```

### 6.2 Vitest 单元测试

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*.{ts,vue}'],
      exclude: ['src/**/*.d.ts', 'src/types/**'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 70,
        statements: 80,
      },
    },
  },
})
```

**工具函数测试示例**：

```typescript
// src/utils/format.test.ts
import { describe, it, expect } from 'vitest'
import { formatMoney, formatDate } from './format'

describe('formatMoney', () => {
  it('应正确格式化金额', () => {
    expect(formatMoney(1234.56)).toBe('1,234.56')
    expect(formatMoney(0)).toBe('0.00')
    expect(formatMoney(-100)).toBe('-100.00')
  })

  it('应处理空值', () => {
    expect(formatMoney(null)).toBe('--')
    expect(formatMoney(undefined)).toBe('--')
  })
})

describe('formatDate', () => {
  it('应格式化日期', () => {
    const date = new Date('2024-01-15T10:30:00')
    expect(formatDate(date, 'YYYY-MM-DD')).toBe('2024-01-15')
    expect(formatDate(date, 'YYYY-MM-DD HH:mm:ss')).toBe('2024-01-15 10:30:00')
  })
})
```

**Composables 测试示例**：

```typescript
// src/composables/useCounter.test.ts
import { describe, it, expect } from 'vitest'
import { useCounter } from './useCounter'

describe('useCounter', () => {
  it('应初始化为 0', () => {
    const { count } = useCounter()
    expect(count.value).toBe(0)
  })

  it('应递增', () => {
    const { count, increment } = useCounter()
    increment()
    expect(count.value).toBe(1)
  })

  it('不应超过最大值', () => {
    const { count, increment } = useCounter({ max: 5 })
    for (let i = 0; i < 10; i++) increment()
    expect(count.value).toBe(5)
  })
})
```

**组件测试示例**：

```typescript
// src/components/BaseButton.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseButton from './BaseButton.vue'

describe('BaseButton', () => {
  it('应渲染默认插槽', () => {
    const wrapper = mount(BaseButton, {
      slots: { default: '点击我' },
    })
    expect(wrapper.text()).toBe('点击我')
  })

  it('点击应触发 click 事件', async () => {
    const wrapper = mount(BaseButton)
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toHaveLength(1)
  })

  it('disabled 时不应触发 click', async () => {
    const wrapper = mount(BaseButton, { props: { disabled: true } })
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeUndefined()
  })
})
```

### 6.3 Playwright E2E 测试

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  retries: process.env.CI ? 2 : 0,
  use: {
    baseURL: 'http://localhost:5173',
    headless: true,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  webServer: {
    command: 'pnpm preview',
    port: 4173,
    reuseExistingServer: !process.env.CI,
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
    { name: 'firefox', use: { browserName: 'firefox' } },
    { name: 'webkit', use: { browserName: 'webkit' } },
  ],
})
```

```typescript
// tests/e2e/login.spec.ts
import { test, expect } from '@playwright/test'

test.describe('登录流程', () => {
  test('正确账号应登录成功', async ({ page }) => {
    await page.goto('/login')
    await page.fill('[data-testid="username"]', 'admin')
    await page.fill('[data-testid="password"]', '123456')
    await page.click('[data-testid="submit"]')
    
    await expect(page).toHaveURL('/dashboard')
    await expect(page.locator('.welcome')).toContainText('欢迎')
  })

  test('错误账号应提示', async ({ page }) => {
    await page.goto('/login')
    await page.fill('[data-testid="username"]', 'wrong')
    await page.fill('[data-testid="password"]', 'wrong')
    await page.click('[data-testid="submit"]')
    
    await expect(page.locator('.el-message--error')).toBeVisible()
  })
})
```

### 6.4 测试覆盖率目标

| 模块 | 覆盖率目标 |
| --- | --- |
| utils/ | ≥ 90% |
| composables/ | ≥ 85% |
| stores/ | ≥ 80% |
| components/ | ≥ 70% |
| views/ | 关键页面 E2E |

---

## 七、部署流程

### 7.1 CI/CD 流程

```
开发者 → Push → GitHub/GitLab → CI 流水线
                              │
                              ├─ Lint 检查
                              ├─ 类型检查
                              ├─ 单元测试
                              ├─ 构建打包
                              ├─ E2E 测试（可选）
                              └─ 部署（按分支）
                                  ├─ develop → 预发布
                                  ├─ main → 生产
                                  └─ PR → Preview 环境
```

### 7.2 GitHub Actions 配置

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  quality:
    name: 代码质量检查
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: pnpm/action-setup@v2
        with:
          version: 8
      
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
      
      - run: pnpm install --frozen-lockfile
      
      - name: ESLint
        run: pnpm lint
      
      - name: Stylelint
        run: pnpm lint:style
      
      - name: 类型检查
        run: pnpm type-check
      
      - name: 单元测试
        run: pnpm test:coverage
      
      - name: 上传覆盖率
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info

  build:
    name: 构建
    runs-on: ubuntu-latest
    needs: quality
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
        with:
          version: 8
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
      
      - run: pnpm install --frozen-lockfile
      - run: pnpm build
        env:
          VITE_APP_ENV: production
      
      - name: 上传产物
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  deploy-staging:
    name: 部署预发布
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
      
      - name: 部署到 Nginx
        uses: appleboy/scp-action@v0.1.7
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_KEY }}
          source: 'dist/*'
          target: '/var/www/staging'

  deploy-production:
    name: 部署生产
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://app.example.com
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
      
      - name: 部署到 CDN
        run: |
          # 同步到 OSS/CDN
          aliyun oss cp dist/ oss://prod-bucket/ --recursive
```

### 7.3 GitLab CI 配置

```yaml
# .gitlab-ci.yml
stages:
  - quality
  - build
  - deploy

variables:
  NODE_VERSION: '20'

cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .pnpm-store/

quality:
  stage: quality
  image: node:${NODE_VERSION}
  before_script:
    - corepack enable
    - pnpm config set store-dir .pnpm-store
    - pnpm install --frozen-lockfile
  script:
    - pnpm lint
    - pnpm type-check
    - pnpm test:coverage
  coverage: '/All files[^|]*\|[^|]*\s+([\d\.]+)/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

build:
  stage: build
  image: node:${NODE_VERSION}
  needs: [quality]
  script:
    - pnpm build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week

deploy-staging:
  stage: deploy
  needs: [build]
  only:
    - develop
  script:
    - rsync -avz dist/ user@staging:/var/www/staging/

deploy-production:
  stage: deploy
  needs: [build]
  only:
    - main
  when: manual  # 手动触发生产部署
  script:
    - rsync -avz dist/ user@prod:/var/www/production/
```

### 7.4 Nginx 部署配置

```nginx
# nginx.conf
server {
    listen 80;
    server_name app.example.com;
    root /var/www/production;
    index index.html;

    # gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;
    gzip_min_length 1000;

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA 路由回退
    location / {
        try_files $uri $uri/ /index.html;
    }

    # index.html 不缓存
    location = /index.html {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    # API 代理
    location /api/ {
        proxy_pass http://backend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
}
```

### 7.5 Docker 部署

```dockerfile
# Dockerfile（多阶段构建）
FROM node:20-alpine AS builder
WORKDIR /app
RUN corepack enable
COPY pnpm-lock.yaml package.json ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "80:80"
    restart: always
    environment:
      - NODE_ENV=production
```

---

## 八、性能优化措施

### 8.1 构建优化

**① 代码分割**

```typescript
// 路由懒加载
const routes = [
  {
    path: '/dashboard',
    component: () => import('@/views/dashboard/index.vue'),
  },
  {
    path: '/system/user',
    component: () => import('@/views/system/user/index.vue'),
  },
]

// 组件懒加载
const BaseChart = defineAsyncComponent(() => import('@/components/BaseChart/index.vue'))
```

**② 手动分包**

```typescript
// vite.config.ts
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'vue-vendor': ['vue', 'vue-router', 'pinia'],
        'element-plus': ['element-plus'],
        'echarts': ['echarts'],
      },
    },
  },
}
```

**③ Tree Shaking**

```typescript
// 按需引入 Element Plus（unplugin 自动处理）
// 或手动按需
import { ElButton, ElTable } from 'element-plus'
```

**④ 压缩**

```typescript
// vite-plugin-compression（gzip + brotli）
import compression from 'vite-plugin-compression'

plugins: [
  compression({
    algorithm: 'gzip',
    ext: '.gz',
    threshold: 10240,  // >10KB 才压缩
  }),
  compression({
    algorithm: 'brotliCompress',
    ext: '.br',
  }),
]
```

### 8.2 运行时优化

**① 组件缓存**

```vue
<template>
  <router-view v-slot="{ Component }">
    <keep-alive :include="cachedViews">
      <component :is="Component" />
    </keep-alive>
  </router-view>
</template>

<script setup lang="ts">
import { useTagsViewStore } from '@/stores/modules/tagsView'
const tagsViewStore = useTagsViewStore()
const cachedViews = computed(() => tagsViewStore.cachedViews)
</script>
```

**② 虚拟列表（大数据量）**

```vue
<template>
  <el-table-v2
    :data="data"
    :columns="columns"
    :height="500"
    :row-height="50"
    estimated-row-height="50"
  />
</template>
```

**③ 防抖节流**

```typescript
// composables/useDebounce.ts
import { ref, customRef } from 'vue'

export function useDebouncedRef<T>(value: T, delay = 200) {
  let timer: number
  return customRef((track, trigger) => {
    return {
      get() {
        track()
        return value
      },
      set(newValue: T) {
        clearTimeout(timer)
        timer = setTimeout(() => {
          value = newValue
          trigger()
        }, delay)
      },
    }
  })
}
```

**④ 图片懒加载**

```typescript
// directives/lazy.ts
import type { Directive } from 'vue'

export const lazy: Directive<HTMLImageElement> = {
  mounted(el, binding) {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          el.src = binding.value
          observer.unobserve(el)
        }
      },
      { rootMargin: '50px' }
    )
    observer.observe(el)
    el._observer = observer
  },
  unmounted(el) {
    el._observer?.disconnect()
  }
}
```

**⑤ 请求缓存**

```typescript
// composables/useRequest.ts
const cache = new Map<string, any>()

export function useRequest<T>(key: string, fetcher: () => Promise<T>) {
  if (cache.has(key)) {
    return { data: ref(cache.get(key)), loading: ref(false) }
  }
  const data = ref<T>()
  const loading = ref(true)
  fetcher().then(res => {
    data.value = res
    cache.set(key, res)
    loading.value = false
  })
  return { data, loading }
}
```

### 8.3 首屏优化

| 优化项 | 措施 | 效果 |
| --- | --- | --- |
| 路由懒加载 | 按需加载页面 | 首屏 JS 减少 60% |
| 骨架屏 | 加载占位 | 感知性能提升 |
| 预加载关键资源 | `<link rel="preload">` | 加速关键资源 |
| CDN 加速 | 静态资源上 CDN | 传输加速 |
| Gzip/Brotli | 服务端压缩 | 体积减少 70% |
| 图片优化 | WebP + 懒加载 | 图片体积减少 50% |

```html
<!-- index.html 预加载 -->
<link rel="preload" href="/assets/js/vue-vendor.js" as="script">
<link rel="preload" href="/assets/css/index.css" as="style">

<!-- 骨架屏 -->
<div id="app">
  <div class="skeleton">
    <div class="skeleton-header"></div>
    <div class="skeleton-content"></div>
  </div>
</div>
```

### 8.4 Element Plus 按需引入

```typescript
// vite.config.ts（自动按需引入）
plugins: [
  AutoImport({ resolvers: [ElementPlusResolver()] }),
  Components({ resolvers: [ElementPlusResolver()] }),
]
```

```typescript
// 自定义主题（仅引入用到的样式）
import 'element-plus/theme-chalk/src/button.scss'
import 'element-plus/theme-chalk/src/table.scss'
```

---

## 九、依赖管理机制

### 9.1 依赖分类

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "element-plus": "^2.5.0",
    "axios": "^1.6.0",
    "dayjs": "^1.11.0",
    "lodash-es": "^4.17.0",
    "echarts": "^5.4.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0",
    "typescript": "^5.3.0",
    "vue-tsc": "^1.8.0",
    "eslint": "^8.56.0",
    "prettier": "^3.1.0",
    "vitest": "^1.0.0",
    "@playwright/test": "^1.40.0"
  }
}
```

### 9.2 版本管理策略

| 依赖类型 | 版本范围 | 更新策略 |
| --- | --- | --- |
| **核心框架**（Vue/Router/Pinia） | `^x.y.0` | 跟随官方，评估后升级 |
| **UI 库**（Element Plus） | `^x.y.0` | 谨慎升级，测试兼容 |
| **工具库**（lodash/dayjs） | `^x.y.0` | 定期更新 |
| **开发依赖**（ESLint/Vitest） | `^x.y.0` | 可较频繁更新 |

### 9.3 依赖更新检查

```bash
# 检查可更新依赖
pnpm outdated

# 安全漏洞检查
pnpm audit

# 交互式更新
pnpm dlx npm-check-updates -i
```

```yaml
# .github/workflows/dependency-check.yml
name: Dependency Check
on:
  schedule:
    - cron: '0 0 * * 1'  # 每周一
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pnpm audit --audit-level moderate
      - name: 通知
        if: failure()
        uses: slack/slack-notify@v1
```

### 9.4 锁文件管理

- `pnpm-lock.yaml` 必须提交到 Git
- CI 中使用 `pnpm install --frozen-lockfile` 确保一致性
- 禁止手动编辑锁文件

### 9.5 依赖安全

```json
// package.json
{
  "scripts": {
    "audit": "pnpm audit",
    "audit:fix": "pnpm audit --fix"
  }
}
```

定期检查：
- 每周运行 `pnpm audit`
- 修复高危漏洞
- 关注依赖废弃（deprecated）警告

---

## 十、全局错误统一处理机制

> 本章设计一套覆盖前端应用全场景的错误统一处理机制，包括错误捕获、标准化、分级、上报、用户提示、降级处理的完整闭环，确保线上问题可感知、可追踪、可恢复，同时不破坏用户体验。

### 10.1 设计目标与原则

| 原则 | 说明 |
| --- | --- |
| **全场景覆盖** | 捕获 API、JS 运行时、Vue 组件、资源加载、Promise 未处理等所有错误 |
| **统一出口** | 所有错误归集到唯一 ErrorHandler，避免散落在各处 |
| **错误标准化** | 异构错误统一转为 `AppError` 结构，便于处理与上报 |
| **分级处理** | 按严重程度分级，决定是否阻断、是否上报、如何提示 |
| **用户友好** | 技术细节对用户屏蔽，仅展示可理解的提示 |
| **可观测** | 错误上报至监控平台（Sentry/自建），形成闭环 |
| **可扩展** | 通过插件/中间件机制新增错误源与处理策略 |
| **降级可用** | 错误发生时提供降级方案，避免白屏 |

### 10.2 错误分类与捕获策略

```
┌─────────────────────────────────────────────────────────────┐
│                   错误捕获全景图                              │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ API 请求错误 │  │JS 运行时错误 │  │Vue 组件错误  │         │
│  │Axios 拦截器  │  │window.onerror│ │app.config.   │         │
│  │             │  │             │  │errorHandler  │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │资源加载错误  │  │Promise 错误  │  │ 路由错误     │         │
│  │error/capture│  │unhandledrej │  │router.onError│         │
│  │Events       │  │ection       │  │             │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          ▼                                  │
│              ┌───────────────────────┐                      │
│              │  统一 ErrorHandler    │                      │
│              │  (标准化 + 分级 + 上报)│                      │
│              └───────────┬───────────┘                      │
│                          ▼                                  │
│              ┌───────────────────────┐                      │
│              │  用户提示 / 降级 / 上报 │                      │
│              └───────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

**六类错误捕获明细**：

| 错误类型 | 捕获方式 | 触发场景 |
| --- | --- | --- |
| **API 请求错误** | Axios 响应拦截器 | HTTP 4xx/5xx、超时、网络断开 |
| **JS 运行时错误** | `window.addEventListener('error')` | 语法错误、类型错误、引用错误 |
| **Vue 组件错误** | `app.config.errorHandler` | 组件渲染/生命周期/事件处理错误 |
| **资源加载错误** | `window.addEventListener('error', capture)` | 图片/CSS/JS 加载失败 |
| **Promise 未处理** | `window.addEventListener('unhandledrejection')` | Promise reject 未 catch |
| **路由错误** | `router.onError()` | 路由守卫/懒加载失败 |

### 10.3 错误信息标准化

将所有异构错误统一为 `AppError` 结构：

```typescript
// src/types/error.ts
/** 错误级别 */
export enum ErrorLevel {
  FATAL = 'fatal',       // 致命：白屏、应用不可用
  ERROR = 'error',       // 错误：功能异常，影响主流程
  WARNING = 'warning',   // 警告：非主流程异常
  INFO = 'info',         // 信息：可忽略的异常
}

/** 错误来源 */
export enum ErrorSource {
  API = 'api',
  JS = 'javascript',
  VUE = 'vue',
  RESOURCE = 'resource',
  PROMISE = 'promise',
  ROUTE = 'route',
}

/** 错误业务码（HTTP 之外的业务错误码） */
export enum BizCode {
  SUCCESS = 0,
  TOKEN_EXPIRED = 401,
  FORBIDDEN = 403,
  NOT_FOUND = 404,
  SERVER_ERROR = 500,
  NETWORK_ERROR = -1,
  TIMEOUT = -2,
  UNKNOWN = -999,
}

/** 统一错误结构 */
export interface AppError {
  /** 唯一标识（用于去重） */
  id: string
  /** 错误级别 */
  level: ErrorLevel
  /** 错误来源 */
  source: ErrorSource
  /** 错误码（HTTP 状态码或业务码） */
  code: number | BizCode
  /** 错误名称 */
  name: string
  /** 用户可见的消息（友好提示） */
  userMessage: string
  /** 开发调试消息（技术细节） */
  devMessage: string
  /** 原始错误对象（序列化前的引用） */
  raw?: unknown
  /** 堆栈信息 */
  stack?: string
  /** 发生时间 */
  timestamp: number
  /** 发生页面 URL */
  url: string
  /** 用户标识（脱敏） */
  userId?: string
  /** 额外上下文 */
  context?: Record<string, unknown>
}
```

### 10.4 统一 ErrorHandler 核心实现

```typescript
// src/plugins/errorHandler/index.ts
import type { AppError, ErrorLevel, ErrorSource } from '@/types/error'
import { ErrorLevel as Level, ErrorSource as Source, BizCode } from '@/types/error'
import { normalizeError } from './normalizer'
import { reportError } from './reporter'
import { notifyUser } from './notifier'
import { dedupe } from './dedupe'

/**
 * 全局错误处理器
 * 职责：标准化 → 去重 → 分级处理 → 上报 → 提示
 */
class ErrorHandler {
  private isReady = false
  /** 上报队列（批量上报） */
  private queue: AppError[] = []
  /** 上报定时器 */
  private flushTimer: number | null = null
  /** 批量上报间隔 */
  private readonly FLUSH_INTERVAL = 5000
  /** 批量上报阈值 */
  private readonly FLUSH_THRESHOLD = 10

  /** 初始化，注册各类错误监听 */
  install(app: App, options?: ErrorHandlerOptions) {
    this.config = { enableReport: true, enableNotify: true, ...options }
    
    // 1. JS 运行时错误 + 资源加载错误
    window.addEventListener('error', (event) => {
      // 资源加载错误（target 为元素）
      if (event.target && (event.target as HTMLElement).tagName) {
        this.handle({
          source: Source.RESOURCE,
          level: Level.WARNING,
          code: BizCode.UNKNOWN,
          name: 'ResourceLoadError',
          message: `资源加载失败: ${(event.target as HTMLElement).src || (event.target as HTMLElement).href}`,
          raw: event,
        })
      } else {
        // JS 运行时错误
        this.handle({
          source: Source.JS,
          level: Level.ERROR,
          code: BizCode.UNKNOWN,
          name: event.error?.name || 'RuntimeError',
          message: event.message,
          stack: event.error?.stack,
          raw: event.error,
        })
      }
      // 阻止默认控制台输出（可选）
      // event.preventDefault()
    }, true)  // 注意：资源错误需在捕获阶段监听

    // 2. Promise 未处理 rejection
    window.addEventListener('unhandledrejection', (event) => {
      this.handle({
        source: Source.PROMISE,
        level: Level.ERROR,
        code: BizCode.UNKNOWN,
        name: 'UnhandledRejection',
        message: this.extractMessage(event.reason),
        stack: event.reason?.stack,
        raw: event.reason,
      })
    })

    // 3. Vue 组件错误
    app.config.errorHandler = (err, instance, info) => {
      this.handle({
        source: Source.VUE,
        level: Level.ERROR,
        code: BizCode.UNKNOWN,
        name: err?.name || 'VueError',
        message: this.extractMessage(err),
        stack: err?.stack,
        raw: err,
        context: {
          componentName: instance?.$options?.name || 'Anonymous',
          lifecycleHook: info,
        },
      })
    }

    // 4. 路由错误（需在 router 初始化后注册）
    // 见 10.6 集成步骤

    this.isReady = true
    console.info('[ErrorHandler] 已启用全局错误监控')
  }

  /** 核心处理入口 */
  handle(input: ErrorInput): AppError {
    // 标准化
    const error = normalizeError(input)
    
    // 去重（相同错误短时间内不重复上报）
    if (dedupe.isDuplicate(error)) {
      return error
    }

    // 分级处理
    this.handleByLevel(error)

    // 加入上报队列
    if (this.config.enableReport) {
      this.enqueueReport(error)
    }

    return error
  }

  /** 按级别处理 */
  private handleByLevel(error: AppError) {
    switch (error.level) {
      case Level.FATAL:
        // 致命错误：上报 + 提示 + 降级（白屏兜底）
        notifyUser.showFatalPage(error.userMessage)
        break
      case Level.ERROR:
        // 错误：上报 + 提示
        if (this.config.enableNotify) {
          notifyUser.showToast(error.userMessage, 'error')
        }
        break
      case Level.WARNING:
        // 警告：上报 + 轻提示
        if (this.config.enableNotify) {
          notifyUser.showToast(error.userMessage, 'warning')
        }
        break
      case Level.INFO:
        // 信息：仅上报
        break
    }
  }

  /** 入队批量上报 */
  private enqueueReport(error: AppError) {
    this.queue.push(error)
    if (this.queue.length >= this.FLUSH_THRESHOLD) {
      this.flush()
    } else if (!this.flushTimer) {
      this.flushTimer = window.setTimeout(() => this.flush(), this.FLUSH_INTERVAL)
    }
  }

  /** 批量上报 */
  private async flush() {
    if (this.flushTimer) {
      clearTimeout(this.flushTimer)
      this.flushTimer = null
    }
    if (this.queue.length === 0) return

    const batch = this.queue.splice(0)
    try {
      await reportError.send(batch)
    } catch (e) {
      // 上报失败，放回队列重试（最多 3 次）
      console.warn('[ErrorHandler] 上报失败，稍后重试', e)
      this.queue.unshift(...batch.slice(0, 5))  // 仅重试前 5 条，防堆积
    }
  }

  /** 提取错误消息 */
  private extractMessage(err: unknown): string {
    if (typeof err === 'string') return err
    if (err instanceof Error) return err.message
    try {
      return JSON.stringify(err)
    } catch {
      return 'Unknown Error'
    }
  }
}

export const errorHandler = new ErrorHandler()
```

### 10.5 错误标准化器（Normalizer）

将异构错误输入统一为 `AppError`：

```typescript
// src/plugins/errorHandler/normalizer.ts
import type { AppError } from '@/types/error'
import { ErrorLevel, ErrorSource, BizCode } from '@/types/error'

/** 错误输入（捕获时的原始结构） */
export interface ErrorInput {
  source: ErrorSource
  level: ErrorLevel
  code: number | BizCode
  name: string
  message: string
  stack?: string
  raw?: unknown
  context?: Record<string, unknown>
}

let errorCounter = 0

/** 生成唯一 ID */
function generateId(): string {
  errorCounter++
  return `err_${Date.now()}_${errorCounter}`
}

/** 根据错误码推断级别 */
function inferLevel(code: number | BizCode): ErrorLevel {
  if (code === BizCode.NETWORK_ERROR || code >= 500) return ErrorLevel.ERROR
  if (code === BizCode.TOKEN_EXPIRED || code === 403) return ErrorLevel.WARNING
  if (code >= 400 && code < 500) return ErrorLevel.WARNING
  return ErrorLevel.ERROR
}

/** 根据错误码生成用户友好消息 */
function getUserMessage(code: number | BizCode, source: ErrorSource): string {
  // API 错误
  if (source === ErrorSource.API) {
    switch (code) {
      case BizCode.NETWORK_ERROR: return '网络连接失败，请检查网络后重试'
      case BizCode.TIMEOUT: return '请求超时，请稍后重试'
      case BizCode.TOKEN_EXPIRED: return '登录已过期，请重新登录'
      case 403: return '您没有权限执行此操作'
      case 404: return '请求的资源不存在'
      case 500: return '服务器开小差了，请稍后重试'
      default: return '请求失败，请稍后重试'
    }
  }
  // 资源加载错误
  if (source === ErrorSource.RESOURCE) return '资源加载失败，已尝试降级处理'
  // Vue/JS/Promise 默认
  return '应用出现异常，请刷新页面重试'
}

/** 标准化错误 */
export function normalizeError(input: ErrorInput): AppError {
  const level = input.level || inferLevel(input.code)
  
  return {
    id: generateId(),
    level,
    source: input.source,
    code: input.code,
    name: input.name,
    userMessage: getUserMessage(input.code, input.source),
    devMessage: input.message,
    raw: input.raw,
    stack: input.stack,
    timestamp: Date.now(),
    url: window.location.href,
    context: {
      ...input.context,
      userAgent: navigator.userAgent,
    },
  }
}
```

### 10.6 用户提示器（Notifier）

基于 Element Plus 的统一提示展示：

```typescript
// src/plugins/errorHandler/notifier.ts
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import type { ErrorLevel } from '@/types/error'

class Notifier {
  /** 轻量 Toast 提示（非阻断） */
  showToast(message: string, type: 'error' | 'warning' | 'info' = 'error') {
    ElMessage({
      message,
      type,
      duration: 3000,
      grouping: true,  // 相同消息合并
    })
  }

  /** 通知卡片（重要错误） */
  notify(title: string, message: string) {
    ElNotification({
      title,
      message,
      type: 'error',
      duration: 5000,
    })
  }

  /** 弹窗确认（需用户决策） */
  confirm(message: string, title = '操作失败'): Promise<boolean> {
    return ElMessageBox.confirm(message, title, {
      confirmButtonText: '重试',
      cancelButtonText: '取消',
      type: 'error',
    }).then(() => true).catch(() => false)
  }

  /** 致命错误页面（白屏兜底） */
  showFatalPage(message: string) {
    // 避免重复渲染
    if (document.getElementById('fatal-error-page')) return
    
    const app = document.getElementById('app')
    if (app) {
      app.innerHTML = `
        <div id="fatal-error-page" style="
          display:flex;flex-direction:column;align-items:center;justify-content:center;
          height:100vh;background:#f5f7fa;font-family:sans-serif;color:#606266;">
          <h2 style="margin-bottom:16px;color:#f56c6c;">应用出现异常</h2>
          <p style="margin-bottom:24px;color:#909399;">${message}</p>
          <button onclick="location.reload()" style="
            padding:8px 24px;background:#409eff;color:#fff;border:none;
            border-radius:4px;cursor:pointer;font-size:14px;">刷新页面</button>
        </div>
      `
    }
  }
}

export const notifyUser = new Notifier()
```

### 10.7 错误上报器（Reporter）

支持多后端上报，带重试与采样：

```typescript
// src/plugins/errorHandler/reporter.ts
import type { AppError } from '@/types/error'
import axios from 'axios'

interface ReportConfig {
  /** 上报接口 */
  endpoint: string
  /** 采样率（0-1，1 = 全量上报） */
  sampleRate: number
  /** 最大重试次数 */
  maxRetry: number
}

class Reporter {
  private config: ReportConfig = {
    endpoint: '/api/log/error',
    sampleRate: 1,
    maxRetry: 3,
  }

  configure(config: Partial<ReportConfig>) {
    this.config = { ...this.config, ...config }
  }

  /** 采样判断 */
  private shouldReport(): boolean {
    if (this.config.sampleRate >= 1) return true
    return Math.random() < this.config.sampleRate
  }

  /** 发送错误批次（使用 sendBeacon 优先，避免页面卸载丢数据） */
  async send(errors: AppError[]): Promise<void> {
    if (!this.shouldReport()) return

    // 1. 页面卸载场景：用 sendBeacon（异步且不阻塞）
    if (navigator.sendBeacon && errors.length > 0) {
      const blob = new Blob([JSON.stringify({ errors })], { type: 'application/json' })
      const success = navigator.sendBeacon(this.config.endpoint, blob)
      if (success) return
    }

    // 2. 普通场景：用 fetch（keepalive 确保页面跳转不丢）
    await fetch(this.config.endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ errors }),
      keepalive: true,
    }).catch((e) => {
      // fetch 失败再用 axios 兜底
      return axios.post(this.config.endpoint, { errors }).catch(() => {
        throw e  // 最终失败抛出，由 ErrorHandler 处理重试
      })
    })
  }
}

export const reportError = new Reporter()
```

### 10.8 去重器（Dedupe）

避免相同错误短时间内重复上报刷屏：

```typescript
// src/plugins/errorHandler/dedupe.ts
import type { AppError } from '@/types/error'

class Dedupe {
  /** 去重窗口（毫秒） */
  private readonly WINDOW = 10_000
  /** 已上报错误的指纹 → 最近时间 */
  private fingerprints = new Map<string, number>()

  /** 生成错误指纹（基于来源+名称+消息+堆栈首行） */
  private fingerprint(error: AppError): string {
    const stackFirstLine = error.stack?.split('\n')[1] || ''
    return [error.source, error.name, error.devMessage, stackFirstLine].join('|')
  }

  /** 是否为重复错误 */
  isDuplicate(error: AppError): boolean {
    const fp = this.fingerprint(error)
    const now = Date.now()
    const lastTime = this.fingerprints.get(fp)
    
    if (lastTime && now - lastTime < this.WINDOW) {
      return true  // 窗口内重复
    }
    
    this.fingerprints.set(fp, now)
    return false
  }

  /** 清理过期指纹（定时调用） */
  cleanup() {
    const now = Date.now()
    for (const [fp, time] of this.fingerprints) {
      if (now - time > this.WINDOW) {
        this.fingerprints.delete(fp)
      }
    }
  }
}

export const dedupe = new Dedupe()

// 每分钟清理一次过期指纹
setInterval(() => dedupe.cleanup(), 60_000)
```

### 10.9 API 请求错误集成

在 Axios 拦截器中接入 ErrorHandler：

```typescript
// src/api/request.ts
import axios from 'axios'
import { errorHandler } from '@/plugins/errorHandler'
import { ErrorSource, ErrorLevel, BizCode } from '@/types/error'
import { useUserStore } from '@/stores/modules/user'

const service = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API,
  timeout: 15000,
})

// 请求拦截器（附加 token）
service.interceptors.request.use((config) => {
  const userStore = useUserStore()
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
})

// 响应拦截器（统一错误处理）
service.interceptors.response.use(
  (response) => {
    const { code, data, message } = response.data
    // 业务成功
    if (code === 0 || code === 200) return data
    
    // 业务失败（HTTP 200 但业务码非成功）
    errorHandler.handle({
      source: ErrorSource.API,
      level: ErrorLevel.WARNING,
      code,
      name: 'BizError',
      message: message || '业务处理失败',
      context: { url: response.config.url, responseData: response.data },
    })
    return Promise.reject(new Error(message || '业务处理失败'))
  },
  (error) => {
    // HTTP 错误（4xx/5xx/超时/断网）
    let code: number | BizCode
    let level: ErrorLevel
    let name: string

    if (error.response) {
      // 有响应但状态码非 2xx
      code = error.response.status
      level = code >= 500 ? ErrorLevel.ERROR : ErrorLevel.WARNING
      name = 'HttpError'
    } else if (error.code === 'ECONNABORTED') {
      code = BizCode.TIMEOUT
      level = ErrorLevel.WARNING
      name = 'TimeoutError'
    } else if (!window.navigator.onLine) {
      code = BizCode.NETWORK_ERROR
      level = ErrorLevel.ERROR
      name = 'OfflineError'
    } else {
      code = BizCode.NETWORK_ERROR
      level = ErrorLevel.ERROR
      name = 'NetworkError'
    }

    errorHandler.handle({
      source: ErrorSource.API,
      level,
      code,
      name,
      message: error.message,
      stack: error.stack,
      raw: error,
      context: {
        url: error.config?.url,
        method: error.config?.method,
        params: error.config?.params,
      },
    })

    // 401 特殊处理：跳转登录
    if (code === 401 || code === BizCode.TOKEN_EXPIRED) {
      const userStore = useUserStore()
      userStore.logout()
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)

export default service
```

### 10.10 路由错误集成

```typescript
// src/router/index.ts
import { errorHandler } from '@/plugins/errorHandler'
import { ErrorSource, ErrorLevel } from '@/types/error'

router.onError((error) => {
  errorHandler.handle({
    source: ErrorSource.ROUTE,
    level: ErrorLevel.ERROR,
    code: -999,
    name: 'RouteError',
    message: error.message,
    stack: error.stack,
    raw: error,
    context: { currentRoute: router.currentRoute.value.path },
  })
  
  // 懒加载失败：提示刷新（常见于发版后旧 chunk 失效）
  if (error.message.includes('Failed to fetch dynamically imported module')) {
    ElMessage.warning('应用已更新，正在刷新...')
    setTimeout(() => window.location.reload(), 1500)
  }
})
```

### 10.11 集成步骤

**步骤 1：安装插件**

```typescript
// src/main.ts
import { createApp } from 'vue'
import { errorHandler } from '@/plugins/errorHandler'
import { reportError } from '@/plugins/errorHandler/reporter'
import App from './App.vue'

const app = createApp(App)

// 配置错误上报（按环境区分）
reportError.configure({
  endpoint: import.meta.env.VITE_APP_ERROR_REPORT_URL || '/api/log/error',
  sampleRate: import.meta.env.PROD ? 1 : 1,  // 生产全量，开发全量
})

// 安装全局错误处理
errorHandler.install(app, {
  enableReport: import.meta.env.PROD,  // 仅生产上报
  enableNotify: true,
})

app.mount('#app')
```

**步骤 2：环境变量**

```bash
# .env.production
VITE_APP_ERROR_REPORT_URL=https://api.example.com/log/error
```

**步骤 3：业务代码主动上报**

```typescript
// 在业务代码中主动捕获并上报
import { errorHandler } from '@/plugins/errorHandler'
import { ErrorSource, ErrorLevel } from '@/types/error'

try {
  await complexBusinessLogic()
} catch (err) {
  errorHandler.handle({
    source: ErrorSource.JS,
    level: ErrorLevel.ERROR,
    code: -999,
    name: 'OrderCalcError',
    message: '订单金额计算异常',
    raw: err,
    context: { orderId: '123', step: 'discount' },
  })
}
```

**步骤 4：Vue 组件局部错误边界**

```vue
<!-- src/components/ErrorBoundary.vue -->
<template>
  <slot v-if="!hasError" />
  <div v-else class="error-boundary">
    <el-result icon="error" title="组件加载失败" sub-title="请刷新或联系管理员">
      <template #extra>
        <el-button type="primary" @click="reset">重试</el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue'
import { errorHandler } from '@/plugins/errorHandler'
import { ErrorSource, ErrorLevel } from '@/types/error'

const hasError = ref(false)

onErrorCaptured((err, instance, info) => {
  hasError.value = true
  errorHandler.handle({
    source: ErrorSource.VUE,
    level: ErrorLevel.WARNING,  // 组件级错误降级为 WARNING，不阻断整个应用
    code: -999,
    name: 'ComponentError',
    message: err.message,
    stack: err.stack,
    raw: err,
    context: { component: instance?.$options?.name, info },
  })
  return false  // 阻止错误继续向上冒泡
})

const reset = () => {
  hasError.value = false
}
</script>
```

### 10.12 目录结构

```
src/plugins/errorHandler/
├── index.ts          # ErrorHandler 核心类（install + handle）
├── normalizer.ts     # 错误标准化器
├── notifier.ts       # 用户提示器（Element Plus）
├── reporter.ts       # 错误上报器（sendBeacon/fetch）
├── dedupe.ts         # 去重器
└── types.ts          # 处理器内部类型

src/types/
└── error.ts          # AppError/ErrorLevel/ErrorSource/BizCode 全局类型
```

### 10.13 测试方法

**单元测试：标准化器**

```typescript
// tests/unit/plugins/errorHandler/normalizer.test.ts
import { describe, it, expect } from 'vitest'
import { normalizeError } from '@/plugins/errorHandler/normalizer'
import { ErrorSource, ErrorLevel, BizCode } from '@/types/error'

describe('normalizeError', () => {
  it('应正确标准化 API 网络错误', () => {
    const error = normalizeError({
      source: ErrorSource.API,
      level: ErrorLevel.ERROR,
      code: BizCode.NETWORK_ERROR,
      name: 'NetworkError',
      message: 'Network Error',
    })
    expect(error.source).toBe(ErrorSource.API)
    expect(error.userMessage).toBe('网络连接失败，请检查网络后重试')
    expect(error.id).toMatch(/^err_\d+_\d+$/)
    expect(error.url).toBe(window.location.href)
  })

  it('应正确标准化 401 错误', () => {
    const error = normalizeError({
      source: ErrorSource.API,
      level: ErrorLevel.WARNING,
      code: 401,
      name: 'HttpError',
      message: 'Unauthorized',
    })
    expect(error.userMessage).toBe('登录已过期，请重新登录')
  })

  it('应附加上下文信息', () => {
    const error = normalizeError({
      source: ErrorSource.VUE,
      level: ErrorLevel.ERROR,
      code: -999,
      name: 'VueError',
      message: 'test',
      context: { componentName: 'UserList' },
    })
    expect(error.context?.componentName).toBe('UserList')
    expect(error.context?.userAgent).toBe(navigator.userAgent)
  })
})
```

**单元测试：去重器**

```typescript
// tests/unit/plugins/errorHandler/dedupe.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { dedupe } from '@/plugins/errorHandler/dedupe'
import type { AppError } from '@/types/error'

describe('Dedupe', () => {
  beforeEach(() => {
    // 重置内部状态
    vi.useFakeTimers()
  })

  const mockError = (overrides: Partial<AppError> = {}): AppError => ({
    id: 'err_1',
    level: 'error' as any,
    source: 'js' as any,
    code: -999,
    name: 'TestError',
    userMessage: 'test',
    devMessage: 'test message',
    timestamp: Date.now(),
    url: 'http://localhost',
    ...overrides,
  })

  it('相同错误在窗口期内应判定为重复', () => {
    const error = mockError()
    expect(dedupe.isDuplicate(error)).toBe(false)  // 第一次：不重复
    expect(dedupe.isDuplicate(error)).toBe(true)   // 第二次：重复
  })

  it('窗口期外应判定为不重复', () => {
    const error = mockError()
    dedupe.isDuplicate(error)
    vi.advanceTimersByTime(10_001)  // 超过 10 秒窗口
    expect(dedupe.isDuplicate(error)).toBe(false)
  })

  it('不同错误不应判定为重复', () => {
    const error1 = mockError({ name: 'ErrorA', devMessage: 'msg A' })
    const error2 = mockError({ name: 'ErrorB', devMessage: 'msg B' })
    expect(dedupe.isDuplicate(error1)).toBe(false)
    expect(dedupe.isDuplicate(error2)).toBe(false)
  })
})
```

**集成测试：ErrorHandler 流程**

```typescript
// tests/unit/plugins/errorHandler/index.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createApp } from 'vue'
import { errorHandler } from '@/plugins/errorHandler'

describe('ErrorHandler 集成', () => {
  let app: ReturnType<typeof createApp>

  beforeEach(() => {
    app = createApp({})
    vi.spyOn(console, 'info').mockImplementation(() => {})
  })

  it('install 后应注册 window error 监听', () => {
    const spy = vi.spyOn(window, 'addEventListener')
    errorHandler.install(app, { enableReport: false, enableNotify: false })
    expect(spy).toHaveBeenCalledWith('error', expect.any(Function), true)
    expect(spy).toHaveBeenCalledWith('unhandledrejection', expect.any(Function))
  })

  it('handle 应返回标准化的 AppError', () => {
    const result = errorHandler.handle({
      source: 'api' as any,
      level: 'error' as any,
      code: 500,
      name: 'TestError',
      message: 'test',
    })
    expect(result.id).toBeDefined()
    expect(result.userMessage).toBeDefined()
    expect(result.timestamp).toBeGreaterThan(0)
  })
})
```

**E2E 测试：错误场景验证**

```typescript
// tests/e2e/error-handling.spec.ts
import { test, expect } from '@playwright/test'

test.describe('错误处理', () => {
  test('API 500 错误应展示友好提示', async ({ page }) => {
    // 拦截接口返回 500
    await page.route('**/api/users', (route) => {
      route.fulfill({ status: 500, body: 'Internal Server Error' })
    })
    
    await page.goto('/system/user')
    
    // 验证 ElMessage 错误提示出现
    await expect(page.locator('.el-message--error')).toBeVisible()
    await expect(page.locator('.el-message--error')).toContainText('服务器')
  })

  test('资源加载失败应降级展示', async ({ page }) => {
    await page.route('**/logo.png', (route) => {
      route.abort()
    })
    
    await page.goto('/dashboard')
    // 验证降级图片或占位符
    await expect(page.locator('.logo-placeholder')).toBeVisible()
  })

  test('JS 运行时错误不应白屏', async ({ page }) => {
    await page.goto('/dashboard')
    // 注入运行时错误
    await page.evaluate(() => {
      throw new Error('test runtime error')
    })
    // 页面仍可交互
    await expect(page.locator('body')).toBeVisible()
  })
})
```

### 10.14 验收标准

| 验收项 | 标 准 | 验证方式 |
| --- | --- | --- |
| **API 错误捕获** | 所有 4xx/5xx/超时/断网均被捕获并提示 | E2E 模拟各类响应 |
| **JS 运行时错误** | window.error 触发后不白屏，有提示 | E2E 注入错误 |
| **Vue 组件错误** | errorHandler 捕获，组件局部降级 | 单测 + 手动触发 |
| **资源加载错误** | 图片/CSS/JS 失败有占位或降级 | E2E 拦截资源 |
| **Promise 未处理** | unhandledrejection 被捕获 | 单测 + 手动触发 |
| **路由懒加载失败** | 提示刷新，不卡死 | E2E 模拟 chunk 404 |
| **错误标准化** | 所有错误转为 AppError 结构 | 单测验证字段 |
| **去重生效** | 10 秒内相同错误仅上报一次 | 单测验证 |
| **用户提示友好** | 用户不看到技术细节（stack/raw） | 代码审查 + E2E |
| **401 自动登出** | token 过期自动跳转登录 | E2E 模拟 401 |
| **批量上报** | 5 秒或 10 条触发上报 | 单测 mock fetch |
| **页面卸载不丢数据** | sendBeacon 兜底上报 | 手动验证 |
| **白屏兜底** | FATAL 级别显示兜底页 | E2E 模拟致命错误 |
| **可关闭上报** | 开发环境可关闭 | 配置验证 |
| **采样率可控** | 生产按比例上报 | 配置验证 |

### 10.15 进阶优化

**① Source Map 还原**

生产环境代码压缩后，上报的 stack 不可读。部署时上传 Source Map 到监控平台，平台自动还原：

```typescript
// vite.config.ts
build: {
  sourcemap: 'hidden',  // 生成但不暴露给用户
}

// CI/CD 部署后自动上传 Source Map 到 Sentry
// npx sentry-cli sourcemaps upload --release <version> dist/
```

**② 错误聚合看板**

后端按错误指纹聚合，统计：
- 错误 Top N（按频次）
- 错误趋势（按时间）
- 影响用户数
- 首次出现/最近出现

**③ 用户反馈闭环**

错误提示附带"反馈"按钮，用户可补充场景描述：

```typescript
notifyUser.showToast('操作失败，点击反馈详情', 'error')
// 同时展示"反馈"按钮，点击弹出反馈表单
```

**④ 性能监控联动**

将错误与性能指标（FCP/LCP/慢请求）关联，分析错误对性能的影响。

---

## 附录 实施路线图与工具速查

### A.1 实施路线图

```
阶段一：基础搭建（1-2 天）
├─ 初始化项目（Vite + Vue 3 + TS）
├─ 配置目录结构与别名
├─ 集成 Element Plus + Pinia + Vue Router
└─ 配置环境变量

阶段二：规范建设（2-3 天）
├─ ESLint + Prettier + Stylelint
├─ Husky + lint-staged
├─ Commitizen + commitlint
└─ VS Code 配置统一

阶段三：核心能力（3-5 天）
├─ Axios 封装（拦截器、错误处理）
├─ 路由守卫与权限
├─ Pinia 模块化
├─ 通用组件封装（Table/Form/Dialog）
├─ Mock 方案集成
└─ 全局错误统一处理（ErrorHandler + 上报 + 提示）

阶段四：测试与部署（3-5 天）
├─ Vitest 单测配置
├─ Playwright E2E
├─ CI/CD 流水线
└─ Nginx/Docker 部署

阶段五：持续优化（持续）
├─ 性能监控
├─ 依赖更新
├─ 代码审查
└─ 文档维护
```

### A.2 工具速查表

| 类别 | 工具 | 用途 |
| --- | --- | --- |
| **构建** | Vite 5 | 开发服务器 + 打包 |
| **框架** | Vue 3.4 | UI 框架 |
| **语言** | TypeScript 5 | 类型安全 |
| **UI** | Element Plus | 组件库 |
| **状态** | Pinia | 状态管理 |
| **路由** | Vue Router 4 | 路由 |
| **HTTP** | Axios | 请求库 |
| **CSS** | SCSS | 样式预处理 |
| **规范** | ESLint + Prettier + Stylelint | 代码质量 |
| **Hook** | Husky + lint-staged | Git 钩子 |
| **提交** | Commitizen + commitlint | 提交规范 |
| **单测** | Vitest + @vue/test-utils | 单元测试 |
| **E2E** | Playwright | 端到端测试 |
| **Mock** | MSW | 接口模拟 |
| **分析** | rollup-plugin-visualizer | 打包分析 |
| **压缩** | vite-plugin-compression | Gzip/Brotli |
| **自动导入** | unplugin-auto-import | API 自动导入 |
| **组件注册** | unplugin-vue-components | 组件自动注册 |
| **图标** | vite-plugin-svg-icons | SVG 雪碧图 |
| **DevTools** | vite-plugin-vue-devtools | 开发工具 |

### A.3 常用命令速查

```bash
# 开发
pnpm dev                    # 启动开发服务器
pnpm build                  # 生产构建
pnpm build:staging          # 预发布构建
pnpm preview                # 预览构建产物

# 质量检查
pnpm lint                   # ESLint 修复
pnpm lint:style             # Stylelint 修复
pnpm format                 # Prettier 格式化
pnpm type-check             # 类型检查

# 测试
pnpm test                   # 单元测试
pnpm test:coverage          # 覆盖率报告
pnpm test:e2e               # E2E 测试

# Git
pnpm commit                 # 规范化提交

# 依赖
pnpm install                # 安装依赖
pnpm add <pkg>              # 添加依赖
pnpm add -D <pkg>           # 添加开发依赖
pnpm remove <pkg>           # 移除依赖
pnpm outdated               # 检查更新
pnpm audit                  # 安全检查
```

### A.4 关键配置文件清单

```
项目根目录/
├── .editorconfig              # 编辑器配置
├── .env / .env.*              # 环境变量
├── .eslintrc.cjs              # ESLint
├── .prettierrc                # Prettier
├── .stylelintrc.cjs           # Stylelint
├── .nvmrc                     # Node 版本
├── .vscode/                   # VS Code
├── .husky/                    # Git Hooks
├── commitlint.config.cjs      # 提交规范
├── package.json               # 项目配置
├── pnpm-lock.yaml             # 锁文件
├── tsconfig.json              # TypeScript
├── vite.config.ts             # Vite 构建
├── vitest.config.ts           # 单测配置
├── playwright.config.ts       # E2E 配置
├── nginx.conf                 # Nginx 部署
├── Dockerfile                 # Docker
└── .github/workflows/ci.yml   # CI/CD
```

---

## 参考资料

- Vite 官方文档：https://vitejs.dev/
- Vue 3 官方文档：https://vuejs.org/
- Element Plus：https://element-plus.org/
- Pinia：https://pinia.vuejs.org/
- Vitest：https://vitest.dev/
- Playwright：https://playwright.dev/
- MSW：https://mswjs.io/

---

> **文档说明**：本方案共 9 大章节，覆盖 Vue 3 + Element Plus + Pinia 技术栈的完整工程化体系。所有配置均提供具体代码示例，可直接落地使用。建议按附录实施路线图分阶段推进，避免一次性引入过多复杂度。方案可根据团队规模与项目需求裁剪调整，核心原则是"规范统一、自动化、可维护"。
