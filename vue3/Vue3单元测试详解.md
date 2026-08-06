# Vue 3 单元测试详细技术文档

> **文档说明**：本文档系统介绍 Vue 3 单元测试的核心概念、工具选择、配置方法、最佳实践及常见问题解决方案。覆盖测试环境搭建、组件测试策略、组合式 API（Composition API）测试技巧、异步操作处理、Pinia/Vue Router/Element Plus 等常见依赖的 Mock 策略、测试覆盖率分析及 CI/CD 集成，并提供完整可运行的代码示例。文档基于 Vue 3 + Vite + Vitest + Vue Test Utils 的主流技术栈，可直接指导开发人员从零开始实施 Vue 3 项目的单元测试工作。

## 目录

- [一、单元测试核心概念](#一单元测试核心概念)
- [二、工具链选型](#二工具链选型)
- [三、测试环境搭建](#三测试环境搭建)
- [四、配置文件详解](#四配置文件详解)
- [五、Vue Test Utils 基础用法](#五vue-test-utils-基础用法)
- [六、组件测试策略](#六组件测试策略)
- [七、组合式 API 测试技巧](#七组合式-api-测试技巧)
- [八、异步操作处理方法](#八异步操作处理方法)
- [九、常见依赖的 Mock 策略](#九常见依赖的-mock-策略)
- [十、指令、插槽与 Teleport](#十指令插槽与-teleport)
- [十一、测试覆盖率分析](#十一测试覆盖率分析)
- [十二、最佳实践与规范](#十二最佳实践与规范)
- [十三、常见问题与解决方案](#十三常见问题与解决方案)
- [十四、CI/CD 集成](#十四cicd-集成)
- [十五、实战示例：完整项目单测](#十五实战示例完整项目单测)

---

## 一、单元测试核心概念

### 1.1 什么是单元测试

单元测试（Unit Testing）是对软件中最小的可测试单元进行检查和验证。在 Vue 3 中，一个"单元"通常指：

| 测试单元 | 说明 |
|---------|------|
| **组件** | Vue SFC（`.vue` 文件），验证渲染、交互、状态 |
| **组合式函数** | `useXxx` 钩子函数，验证响应式状态与副作用 |
| **工具函数** | `utils/*.ts` 中的纯函数 |
| **Pinia Store** | 状态管理模块，验证 state/getters/actions |
| **API 封装** | `request.ts` 等服务层模块 |

### 1.2 单元测试的核心价值

| 价值 | 说明 |
|------|------|
| **保证重构安全** | 重构时快速回归，防止引入回归 Bug |
| **驱动设计** | TDD（测试驱动开发）迫使组件解耦、接口清晰 |
| **文档即代码** | 测试用例即活的使用文档，可随时运行验证 |
| **减少调试成本** | 问题定位精确到单个函数/组件，而非整站排查 |
| **提升工程信心** | 覆盖率达标后发版更有底气 |

### 1.3 测试金字塔与 Vue 项目的定位

```
         /        \       ← E2E（端到端）占 10%，跑业务流程
        /----------\      ← 集成测试占 20%，测组件组合
       /   组件单测   \     ← 组件单元测试占 40%
      /----------------\    ← 纯函数/组合函数单测占 30%
     /                    \   ← 总计：单元测试占 70%
```

> Vue 3 项目中：**纯函数和组合式函数单测优先写**，因为它们快、稳定、便宜；组件单测其次，以关键交互为主；E2E 只覆盖核心业务流程。

### 1.4 关键术语

| 术语 | 说明 |
|------|------|
| **Mount** | 把组件挂载到虚拟 DOM 中，返回 `wrapper` 对象 |
| **Shallow Mount** | 浅挂载，不渲染子组件，用于隔离父组件 |
| **Stub** | 用假的组件/模块替换真实依赖 |
| **Mock** | 替换真实实现并可验证调用 |
| **Spy** | 包装真实函数，可记录调用但不替换行为 |
| **Wrapper** | Vue Test Utils 对挂载实例的包装对象，提供 `find`、`trigger` 等 API |
| **`nextTick`** | 等待 Vue DOM 更新队列刷新，是异步断言的关键 |

---

## 二、工具链选型

### 2.1 工具链组合（2026 推荐）

Vue 3 + Vite 项目的标准工具链组合：

| 组件 | 选择 | 说明 |
|------|------|------|
| **测试运行器** | **Vitest** ✅ 推荐 | 与 Vite 原生集成，ESM 零配置、速度快 |
| | Jest（备选） | 老牌，需要处理 ESM 兼容和 transform 链，工程成本高 |
| **DOM 环境** | **jsdom** ✅ 推荐 | 提供浏览器 API 的 Node.js 实现 |
| | happy-dom（备选） | 启动更快，但对部分浏览器 API 支持不完整 |
| **Vue 组件挂载** | **@vue/test-utils** ✅ 官方 | Vue 官方维护，Vue 3 使用 v2.x |
| **断言库** | **Vitest 内置断言 + chai 风格** | Vitest 提供 `expect()`，兼容 Jest 断言 |
| **Mock** | **Vitest 内置 `vi.mock` / `vi.spyOn`** | 原生支持，无需额外引入 sinon |
| **样式 Mock** | Vitest `css.stubModule` 或空 stub | 无需处理 SFC 中 `<style>` 导入 |
| **覆盖率** | **V8 或 istanbul** | Vitest 内置 `--coverage` 即可 |

### 2.2 Vitest vs Jest 对比

| 维度 | Vitest ✅ 推荐（Vite 项目） | Jest |
|------|---------------------------|------|
| **ESM 支持** | 原生支持，无需 transform | 需配置 `transform` / `transformIgnorePatterns` |
| **启动速度** | 冷启动快，Vite 复用配置 | 首次启动慢 |
| **配置** | 可合并到 `vite.config.ts`，一套配置 | 独立 `jest.config.js`，重复配置 |
| **与 Vite 集成** | 无缝，alias/plugin 直接共用 | 需要额外桥接 |
| **HMR/Watch** | 支持 HMR，改后秒跑 | 部分场景重跑耗时 |
| **类型检查** | 原生 TypeScript 友好 | 需要 `ts-jest` 或 `@swc/jest` |
| **CSS/资源** | Vite 内置处理链 | 需要 moduleNameMapper/transform |
| **Vue SFC 支持** | 直接复用 `vite-plugin-vue` | 需要 `@vue/vue3-jest` + 额外配置 |

> **经验教训**：Vite + Vue 3 项目 **首选 Vitest**。反复在 Jest 与 Vitest 之间切换会导致配置冲突和 ESM/CJS 不兼容问题（来源：Experience 209105）。先锁定 Vitest 路线，再补齐用例。

### 2.3 版本对应关系

| 工具 | 推荐版本 | 说明 |
|------|---------|------|
| `vitest` | ≥ 2.0 | Vue 3.4+ 建议 vitest 2.x |
| `@vue/test-utils` | ≥ 2.4 | Vue 3 专用 v2.x（Vue 2 用 v1.x） |
| `@vue/server-test-utils` | 可选 | SSR 测试用 |
| `jsdom` | ≥ 24.x | 模拟浏览器环境 |
| `happy-dom` | 备选 | 轻量替代 |
| `@testing-library/jest-dom` | 可选 | 提供更语义化的 DOM 断言 |
| `pinia-plugin-vitest` | 可选 | Pinia + Vitest 集成简化 |

---

## 三、测试环境搭建

### 3.1 从零创建可测试的 Vue3 + Vite 项目

```bash
# 1. 创建项目
npm create vite@latest my-vue-app -- --template vue-ts
cd my-vue-app

# 2. 安装测试依赖（一行搞定 Vitest 全家桶）
npm install -D vitest @vue/test-utils jsdom

# 3. （可选）断言增强 + 类型定义
npm install -D @testing-library/jest-dom @types/testing-library__jest-dom
```

> ⚠️ **踩坑提示**：Vue 2 项目使用 `vue-test-utils@1.x` + `vue-jest`；Vue 3 必须用 `@vue/test-utils@2.x`，千万不要错装 Vue 2 版（来源：Experience 209105）。

### 3.2 目录结构规范

**方案一：推荐——测试文件紧邻源码**（方便一起打开和移动）

```
src/
├── components/
│   ├── Counter.vue
│   └── Counter.spec.ts          ← 每个组件自带 .spec
├── composables/
│   ├── useUser.ts
│   └── useUser.spec.ts          ← 组合函数也紧邻
├── stores/
│   ├── user.ts
│   └── user.spec.ts
├── utils/
│   ├── format.ts
│   └── format.spec.ts
└── App.vue
```

**方案二：备选——统一 test/ 目录**

```
test/
├── components/
│   └── Counter.spec.ts
├── composables/
│   └── useUser.spec.ts
└── setup.ts                      ← 全局 setup（可选）
```

> **注意**：**不要两套目录并存**（例如同时有 `test/` 和 `src/tests/`），否则容易出现配置匹配冲突和维护成本（来源：Experience 209105）。统一一套，并让 vitest 配置中的 `include` 只匹配一个根。

### 3.3 最小可运行用例

创建第一个用例验证环境是否正常：

```ts
// src/utils/math.spec.ts
import { describe, it, expect } from 'vitest';

describe('基础数学工具', () => {
  it('add 应该正确相加', () => {
    expect(1 + 1).toBe(2);
  });
});
```

```ts
// src/components/HelloWorld.vue
<script setup lang="ts">
defineProps<{ msg: string }>();
</script>
<template>
  <h1>{{ msg }}</h1>
</template>
```

```ts
// src/components/HelloWorld.spec.ts
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import HelloWorld from './HelloWorld.vue';

describe('HelloWorld', () => {
  it('渲染传入的 msg', () => {
    const wrapper = mount(HelloWorld, {
      props: { msg: 'Hello Vitest' }
    });
    expect(wrapper.text()).toContain('Hello Vitest');
  });
});
```

### 3.4 添加运行脚本

```json
// package.json
{
  "scripts": {
    "test": "vitest",                     // 开发模式 watch
    "test:run": "vitest run",             // CI 单次运行
    "test:ui": "vitest --ui",             // 浏览器 UI
    "test:coverage": "vitest run --coverage" // 覆盖率
  }
}
```

---

## 四、配置文件详解

### 4.1 vite.config.ts（合并 Vitest 配置）

Vitest 最爽的一点是**直接复用 Vite 配置**，无需单独维护一份 `jest.config`：

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath } from 'node:url';

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },

  // ⬇️ 直接在 vite.config 中嵌入 vitest
  test: {
    // 启用类似 jest 的全局 API（describe/it/expect），无需每文件 import
    globals: true,

    // 必须：Vue 组件需要 DOM 环境
    environment: 'jsdom',

    // TypeScript 类型：从 vitest/config 继承（在 tsconfig 中配置 types）
    // 测试文件匹配规则
    include: [
      'src/**/*.spec.ts',
      'src/**/*.spec.tsx',
      'src/**/__tests__/**/*.{ts,tsx}'
    ],

    // 单文件超时（默认 5s，复杂组件可适当提高）
    testTimeout: 10_000,

    // 每个文件前自动执行的 setup 脚本
    setupFiles: ['./src/test/setup.ts'],

    // CSS 处理：stub 掉，不参与测试
    css: {
      modules: {
        classNameStrategy: 'non-scoped'
      }
    },

    // coverage 配置
    coverage: {
      provider: 'v8',           // 推荐 v8（V8 原生），备选 istanbul
      reporter: ['text', 'html', 'lcov'],
      include: ['src/**/*.{ts,vue}'],
      exclude: [
        'src/**/*.d.ts',
        'src/**/*.spec.ts',
        'src/main.ts',
        'src/App.vue',
        'src/test/**'
      ],
      // 质量门禁（可选，低于阈值直接失败）
      thresholds: {
        lines: 80,
        branches: 70,
        functions: 80,
        statements: 80
      }
    },

    // 环境变量（测试中通过 import.meta.env 读取）
    env: {
      VITE_APP_TITLE: 'Test App'
    }
  }
});
```

> ⚠️ **关键配置**：Vue 组件单测**必须**设置 `environment: 'jsdom'`，否则会出现 `document is not defined`（来源：Experience 209105）。这个设置应集中在 vitest 配置，不要在每个测试文件里"补救式" `global.document = ...`。

### 4.2 全局 setup 脚本

setup 脚本用于注入**所有测试都需要**的基础设施：

```ts
// src/test/setup.ts
import { beforeAll, afterEach, afterAll } from 'vitest';
import '@testing-library/jest-dom/vitest';  // 启用 toBeInTheDocument 等断言
import { cleanup } from '@vue/test-utils';

// 1. Element Plus 需要的 global 对象补齐（jsdom 缺失时）
if (typeof globalThis.ResizeObserver === 'undefined') {
  globalThis.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as any;
}

// 2. 补充 matchMedia（jsdom 默认缺失）
if (!globalThis.matchMedia) {
  globalThis.matchMedia = (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false
  }) as any;
}

// 3. 每个测试执行完 cleanup，避免 wrapper 互相污染
afterEach(() => {
  cleanup();
});

// 4. 统一模拟 Element Plus 的 ElMessage（示例）
vi.mock('element-plus', async () => {
  const actual = await vi.importActual<any>('element-plus');
  return {
    ...actual,
    ElMessage: {
      success: vi.fn(),
      warning: vi.fn(),
      error: vi.fn(),
      info: vi.fn()
    },
    ElMessageBox: {
      confirm: vi.fn().mockResolvedValue(true)
    }
  };
});
```

### 4.3 tsconfig.json 补充类型

```jsonc
// tsconfig.json / tsconfig.app.json
{
  "compilerOptions": {
    "types": [
      "vite/client",
      "vitest/globals",        // vitest 全局 API 类型
      "@testing-library/jest-dom"  // jest-dom 断言类型（可选）
    ]
  },
  "include": [
    "src/**/*.ts",
    "src/**/*.d.ts",
    "src/**/*.tsx",
    "src/**/*.vue",
    "src/**/*.spec.ts"        // 把 .spec 也纳入类型检查
  ]
}
```

---

## 五、Vue Test Utils 基础用法

### 5.1 `mount` vs `shallowMount`

```ts
import { mount, shallowMount } from '@vue/test-utils';
import Parent from './Parent.vue';

// mount：真实渲染子组件 → 集成测试风格
const wrapperFull = mount(Parent, {
  props: { value: 1 }
});

// shallowMount：子组件用 stub 代替 → 纯单元测试风格，隔离父组件
const wrapperShallow = shallowMount(Parent, {
  props: { value: 1 }
});
```

| 方式 | 适用 | 优点 | 缺点 |
|------|------|------|------|
| `mount` | 验证父子组件交互 | 更接近真实 | 速度慢，子组件问题会影响父组件 |
| `shallowMount` ✅ 组件单测推荐 | 只测当前组件 | 快、隔离 | 不验证集成 |

> **最佳实践**：组件单测优先 `shallowMount`，关键集成场景用 `mount`。

### 5.2 挂载选项总览

```ts
const wrapper = mount(MyComponent, {
  // ⬇️ Props
  props: {
    title: 'Hello',
    modelValue: 0
  },

  // ⬇️ Slots（默认 / 具名 / 作用域）
  slots: {
    default: '默认插槽内容',
    header: '<h1>具名插槽</h1>',
    item: (props: any) => h('span', `作用域：${props.name}`)
  },

  // ⬇️ 全局注入（路由、Pinia、UI 库插件等）
  global: {
    plugins: [createPinia(), router],
    components: { ElButton, ElInput },
    mocks: {
      $message: vi.fn(),
      $t: (key: string) => key           // i18n mock
    },
    directives: {
      'my-dir': vi.fn()
    },
    provide: {
      'global-api': { request: vi.fn() }
    }
  },

  // ⬇️ v-model 支持（Vue Test Utils 2.x）
  attachTo: document.body,              // 挂到真实 body（极少情况需要）
  attrs: { class: 'custom', id: 'app' }
});
```

### 5.3 Wrapper 常用 API

| API | 说明 | 示例 |
|-----|------|------|
| `wrapper.find(selector)` | 查找单个元素 | `wrapper.find('button')` |
| `wrapper.findAll(selector)` | 查找多个元素 | `wrapper.findAll('li')` |
| `wrapper.findComponent(Comp)` | 查找子组件 | `wrapper.findComponent(Child)` |
| `wrapper.get(selector)` | 找不到直接报错（断言用） | `wrapper.get('h1')` |
| `wrapper.text()` | 获取文本 | `expect(wrapper.text()).toContain('Hi')` |
| `wrapper.html()` | 获取 HTML | 用于快照测试 |
| `wrapper.attributes('href')` | 取属性 | `expect(link.attributes('href')).toBe('/a')` |
| `wrapper.classes()` | 取 class 数组 | `expect(btn.classes()).toContain('active')` |
| `wrapper.trigger('click')` | 触发事件 | 异步，需 await |
| `wrapper.setValue(val)` | 设置表单值 | 异步，需 await |
| `wrapper.props('title')` | 取 props | 断言父传子 |
| `wrapper.emitted()` | 取 emitted 事件 | 断言子 emit |
| `wrapper.vm` | 组件实例 | 访问 setup 返回的数据 |

> ⚠️ **选择器稳定性**：避免使用 `:contains("保存")` 这类不稳的文本选择器，更不要依赖 `wrapper.find('button:nth-child(2)')`。推荐使用 **`data-testid`** 属性（来源：Experience 209105）：

```vue
<!-- 模板中 -->
<button data-testid="submit-btn" @click="submit">提交</button>
```

```ts
// 测试中
const btn = wrapper.get('[data-testid="submit-btn"]');
```

### 5.4 `wrapper.vm` 访问响应式数据

```ts
// Counter.vue
<script setup lang="ts">
import { ref } from 'vue';
const count = ref(0);
</script>
<template>
  <button @click="count++">{{ count }}</button>
</template>
```

```ts
// Counter.spec.ts
it('点击后 count 自增', async () => {
  const wrapper = shallowMount(Counter);
  expect(wrapper.vm.count).toBe(0);   // ✅ 直接访问 setup 暴露的变量

  const btn = wrapper.get('button');
  await btn.trigger('click');

  expect(wrapper.vm.count).toBe(1);
  expect(btn.text()).toBe('1');
});
```

> **注意**：仅在 `script setup` 组件中可用（未显式关闭 expose）。如果需要访问组合函数返回的值，这是最直接的方式。

---

## 六、组件测试策略

### 6.1 四类组件的测试重点

| 组件类型 | 测试重点 | 典型示例 |
|---------|---------|----------|
| **展示组件**（Dumb） | Props 渲染正确、Event 正确 emit | Button、Tag、Badge |
| **容器组件**（Smart） | 请求 mock、状态流转、子组件交互 | 列表页、表单页 |
| **Form 组件** | 双向绑定、校验、提交、重置 | Login 表单、搜索框 |
| **高阶组件** | 插槽、透传、Provide/Inject | Table 容器、Tab 容器 |

### 6.2 展示组件：Button

```vue
<!-- components/BaseButton.vue -->
<script setup lang="ts">
interface Props {
  type?: 'primary' | 'default' | 'danger';
  loading?: boolean;
  disabled?: boolean;
}
const props = withDefaults(defineProps<Props>(), {
  type: 'default',
  loading: false,
  disabled: false
});
const emit = defineEmits<{ (e: 'click', payload: number): void }>();
</script>
<template>
  <button
    data-testid="base-btn"
    :class="['btn', `btn-${type}`, { loading, disabled }]"
    :disabled="disabled || loading"
    @click="!disabled && !loading && emit('click', 42)"
  >
    <i v-if="loading" class="spinner" />
    <slot />
  </button>
</template>
```

```ts
// components/BaseButton.spec.ts
import { describe, it, expect, vi } from 'vitest';
import { shallowMount } from '@vue/test-utils';
import BaseButton from './BaseButton.vue';

describe('BaseButton', () => {
  it('渲染默认 type 样式', () => {
    const w = shallowMount(BaseButton, { slots: { default: 'Go' } });
    expect(w.classes()).toContain('btn-default');
    expect(w.get('[data-testid="base-btn"]').text()).toBe('Go');
  });

  it('传入 type=primary 应用对应样式', () => {
    const w = shallowMount(BaseButton, {
      props: { type: 'primary' }
    });
    expect(w.classes()).toContain('btn-primary');
  });

  it('disabled 时点击不触发 click 事件', async () => {
    const w = shallowMount(BaseButton, { props: { disabled: true } });
    await w.trigger('click');
    expect(w.emitted().click).toBeUndefined();
  });

  it('非 disabled 时点击 emit click 并传参 42', async () => {
    const w = shallowMount(BaseButton);
    await w.trigger('click');
    expect(w.emitted('click')?.[0]).toEqual([42]);
  });

  it('loading=true 显示 spinner 并禁用', () => {
    const w = shallowMount(BaseButton, { props: { loading: true } });
    expect(w.find('.spinner').exists()).toBe(true);
    expect(w.attributes('disabled')).toBeDefined();
  });
});
```

### 6.3 Form 组件：登录表单

```vue
<!-- components/LoginForm.vue -->
<script setup lang="ts">
import { reactive } from 'vue';
const form = reactive({ username: '', password: '' });
const emit = defineEmits<{
  (e: 'submit', payload: typeof form): void;
}>();

const rules = {
  username: /^.{3,20}$/,
  password: /^.{6,}$/
};

function submit() {
  if (!rules.username.test(form.username)) return;
  if (!rules.password.test(form.password)) return;
  emit('submit', { ...form });
}
</script>
<template>
  <form @submit.prevent="submit">
    <input data-testid="username" v-model="form.username" />
    <input data-testid="password" type="password" v-model="form.password" />
    <button data-testid="submit" type="submit">登录</button>
  </form>
</template>
```

```ts
// components/LoginForm.spec.ts
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import LoginForm from './LoginForm.vue';

describe('LoginForm', () => {
  it('空表单点击提交不触发 emit', async () => {
    const w = mount(LoginForm);
    await w.get('[data-testid="submit"]').trigger('submit');
    expect(w.emitted('submit')).toBeUndefined();
  });

  it('合法数据点击提交 emit submit', async () => {
    const w = mount(LoginForm);
    await w.get('[data-testid="username"]').setValue('admin');
    await w.get('[data-testid="password"]').setValue('123456');
    await w.get('[data-testid="submit"]').trigger('submit');

    expect(w.emitted('submit')?.[0]?.[0]).toEqual({
      username: 'admin',
      password: '123456'
    });
  });

  it('用户名不足 3 位不触发提交', async () => {
    const w = mount(LoginForm);
    await w.get('[data-testid="username"]').setValue('ab');
    await w.get('[data-testid="password"]').setValue('123456');
    await w.get('[data-testid="submit"]').trigger('submit');
    expect(w.emitted('submit')).toBeUndefined();
  });
});
```

### 6.4 容器组件：UserList（带请求）

```vue
<!-- views/UserList.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { fetchUsers, type User } from '@/api/user';

const list = ref<User[]>([]);
const loading = ref(false);

async function load() {
  loading.value = true;
  list.value = await fetchUsers();
  loading.value = false;
}
onMounted(load);
</script>
<template>
  <div>
    <button data-testid="reload" @click="load">刷新</button>
    <ul v-if="!loading" data-testid="user-list">
      <li v-for="u in list" :key="u.id" class="user-item">
        {{ u.name }}
      </li>
    </ul>
    <p v-else data-testid="loading">加载中...</p>
  </div>
</template>
```

```ts
// views/UserList.spec.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import UserList from './UserList.vue';

// ⚠️ 在顶层 mock 整个模块
const mockFetchUsers = vi.fn();
vi.mock('@/api/user', () => ({
  fetchUsers: () => mockFetchUsers()
}));

beforeEach(() => {
  vi.clearAllMocks();
});

describe('UserList', () => {
  it('mount 时渲染 loading，随后展示用户列表', async () => {
    // 1. 准备 mock 的异步返回（延迟模拟网络）
    let resolve!: (v: any[]) => void;
    mockFetchUsers.mockReturnValue(
      new Promise((r) => (resolve = r))
    );

    const w = mount(UserList);
    expect(w.get('[data-testid="loading"]').text()).toBe('加载中...');

    // 2. 响应返回
    resolve([
      { id: 1, name: 'Alice' },
      { id: 2, name: 'Bob' }
    ]);

    // 3. 关键：等所有 Promise + Vue 更新队列
    await flushPromises();  // 等待 fetchUsers Promise 完成
    await w.vm.$nextTick(); // 等待 DOM 刷新

    expect(w.findAll('.user-item')).toHaveLength(2);
    expect(w.get('[data-testid="user-list"]').text()).toContain('Alice');
    expect(mockFetchUsers).toHaveBeenCalledTimes(1);
  });

  it('点击刷新再次调用 fetchUsers', async () => {
    mockFetchUsers.mockResolvedValue([]);
    const w = mount(UserList);
    await flushPromises();
    await w.vm.$nextTick();

    await w.get('[data-testid="reload"]').trigger('click');
    await flushPromises();

    expect(mockFetchUsers).toHaveBeenCalledTimes(2);
  });
});
```

> **经验教训**：当组件在 `created/onMounted` 中有**嵌套异步链路**时，不要用 `setTimeout(100)` 等固定 sleep；应使用 `flushPromises` + `nextTick` 或条件轮询，稳定性更高（来源：Experience 1152280）。

---

## 七、组合式 API 测试技巧

### 7.1 组合函数可独立测试（推荐）

组合式函数是 Vue 3 单测的黄金地段——**没有 DOM、不依赖组件生命周期、跑得飞快**。优先为它们写足用例：

```ts
// composables/useCounter.ts
import { ref, computed } from 'vue';

export function useCounter(initial = 0) {
  const count = ref(initial);
  const doubled = computed(() => count.value * 2);

  function inc() { count.value++; }
  function dec() { count.value--; }
  function reset() { count.value = initial; }

  return { count, doubled, inc, dec, reset };
}
```

```ts
// composables/useCounter.spec.ts
import { describe, it, expect } from 'vitest';
import { useCounter } from './useCounter';

describe('useCounter', () => {
  it('默认初始值为 0，doubled 计算正确', () => {
    const { count, doubled } = useCounter();
    expect(count.value).toBe(0);
    expect(doubled.value).toBe(0);

    count.value = 5;
    expect(doubled.value).toBe(10);
  });

  it('inc/dec/reset 操作正确', () => {
    const { count, inc, dec, reset } = useCounter(10);
    inc();
    expect(count.value).toBe(11);
    dec();
    expect(count.value).toBe(10);
    reset();
    expect(count.value).toBe(10);
  });
});
```

### 7.2 使用生命周期的组合函数：`vue-composables` 助手 or `mount` 空组件

对于调用了 `onMounted` / `watch` / `onUnmounted` 的组合函数，需在组件上下文中执行：

```ts
// composables/useNow.ts
import { ref, onMounted, onBeforeUnmount } from 'vue';

export function useNow(intervalMs = 1000) {
  const now = ref(Date.now());
  let timer: any;

  onMounted(() => {
    timer = setInterval(() => (now.value = Date.now()), intervalMs);
  });

  onBeforeUnmount(() => clearInterval(timer));
  return { now };
}
```

```ts
// composables/useNow.spec.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { defineComponent } from 'vue';
import { useNow } from './useNow';

beforeEach(() => vi.useFakeTimers());

describe('useNow', () => {
  it('mount 初始化 now，并按 interval 更新', () => {
    const results: number[] = [];
    const wrapper = mount(defineComponent({
      setup() {
        const { now } = useNow(1000);
        return { now };
      },
      template: '<div />'
    }));

    const vm = wrapper.vm as any;
    results.push(vm.now);

    vi.advanceTimersByTime(1000);
    results.push(vm.now);
    expect(results[1] - results[0]).toBeGreaterThanOrEqual(1000);

    vi.advanceTimersByTime(1000);
    expect(vm.now).toBeGreaterThan(results[1]);

    // unmount 后清定时器
    wrapper.unmount();
    vi.advanceTimersByTime(5000);  // 不应报错
  });
});
```

### 7.3 含异步请求的组合函数

```ts
// composables/useFetch.ts
import { ref } from 'vue';

export function useFetch<T>(fn: () => Promise<T>) {
  const data = ref<T | null>(null);
  const loading = ref(false);
  const error = ref<Error | null>(null);

  async function run() {
    loading.value = true;
    error.value = null;
    try {
      data.value = await fn();
    } catch (e) {
      error.value = e as Error;
    } finally {
      loading.value = false;
    }
  }

  return { data, loading, error, run };
}
```

```ts
// composables/useFetch.spec.ts
import { describe, it, expect, vi } from 'vitest';
import { flushPromises } from '@vue/test-utils';
import { useFetch } from './useFetch';

describe('useFetch', () => {
  it('成功流程：loading 切换正确，data 填充', async () => {
    const mockFn = vi.fn().mockResolvedValue({ a: 1 });
    const { data, loading, error, run } = useFetch(mockFn);

    const p = run();
    expect(loading.value).toBe(true);
    expect(data.value).toBeNull();

    await p;
    await flushPromises();

    expect(loading.value).toBe(false);
    expect(error.value).toBeNull();
    expect(data.value).toEqual({ a: 1 });
  });

  it('失败流程：error 被捕获', async () => {
    const err = new Error('boom');
    const mockFn = vi.fn().mockRejectedValue(err);
    const { data, loading, error, run } = useFetch(mockFn);

    await run();
    expect(loading.value).toBe(false);
    expect(data.value).toBeNull();
    expect(error.value).toBe(err);
  });
});
```

### 7.4 Provide/Inject 的组合函数

```ts
// composables/useTheme.ts
import { inject, provide, ref, readonly } from 'vue';

const ThemeKey = Symbol('theme');

export function useProvideTheme() {
  const theme = ref<'light' | 'dark'>('light');
  const toggle = () => (theme.value = theme.value === 'light' ? 'dark' : 'light');
  provide(ThemeKey, { theme: readonly(theme), toggle });
  return { theme, toggle };
}

export function useTheme() {
  const ctx = inject(ThemeKey);
  if (!ctx) throw new Error('useTheme must be used within Provider');
  return ctx;
}
```

```ts
// composables/useTheme.spec.ts
import { describe, it, expect } from 'vitest';
import { defineComponent, h, ref } from 'vue';
import { mount } from '@vue/test-utils';
import { useProvideTheme, useTheme } from './useTheme';

describe('useTheme', () => {
  it('未 provide 时 inject 抛错', () => {
    expect(() => mount(defineComponent({
      setup: () => (useTheme(), () => h('div'))
    }))).toThrow('useTheme must be used');
  });

  it('provide 后可 toggle', () => {
    const child = defineComponent({
      setup() {
        const { theme, toggle } = useTheme();
        return () => h('div', { class: theme.value, onClick: toggle });
      }
    });

    const parent = defineComponent({
      setup() {
        useProvideTheme();
        return () => h(child);
      }
    });

    const w = mount(parent);
    expect(w.classes()).toContain('light');
    w.trigger('click');
    expect(w.classes()).toContain('dark');
  });
});
```

---

## 八、异步操作处理方法

Vue 单测 80% 的问题都是**异步时序问题**。记住：**任何修改 DOM / ref 的操作后，下一行断言前必须 `await` 它。**

### 8.1 核心三板斧

| 工具 | 作用 | 什么时候用 |
|------|------|-----------|
| `await wrapper.trigger('click')` | 触发事件后等待 DOM 更新 | 点击/输入事件之后 |
| `await wrapper.setValue(v)` | 设置表单值后等待 v-model 响应 | 输入框、select 赋值之后 |
| `await flushPromises()` | 等待所有微任务完成 | Promise 链、await/async 函数之后 |
| `await nextTick()` | 等 Vue DOM 更新队列 | 直接修改 `wrapper.vm.x = y` 之后 |

```ts
// 典型错误：没 await 就断言
it('❌ 错误写法', () => {
  w.get('button').trigger('click');  // 没 await
  expect(w.text()).toContain('done');  // 大概率失败
});

it('✅ 正确写法', async () => {
  await w.get('button').trigger('click');
  await flushPromises();
  await nextTick();
  expect(w.text()).toContain('done');
});
```

### 8.2 Fake Timer（模拟 setTimeout / setInterval）

```ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import DebounceInput from './DebounceInput.vue';

beforeEach(() => vi.useFakeTimers());

describe('DebounceInput', () => {
  it('300ms 后才触发搜索', async () => {
    const w = mount(DebounceInput);
    const input = w.get('input');

    await input.setValue('abc');
    await input.setValue('abcd');

    // 200ms 还没触发
    vi.advanceTimersByTime(200);
    expect(w.emitted('search')).toBeUndefined();

    // 再前进 100ms（共 300ms）触发
    vi.advanceTimersByTime(100);
    await flushPromises();
    expect(w.emitted('search')?.pop()?.[0]).toBe('abcd');
  });
});
```

### 8.3 统一 wait 助手（通用技巧）

```ts
// src/test/utils.ts
import { nextTick } from 'vue';

/**
 * 等待"条件成立"，支持嵌套 Promise。
 * 替代 setTimeout(100) 等不稳定等待。
 */
export async function waitFor<T>(
  predicate: () => T | Promise<T>,
  { timeout = 3000, interval = 20 } = {}
): Promise<T> {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    try {
      const result = await predicate();
      if (result) return result;
    } catch { /* 忽略 predicate 抛错 */ }
    await new Promise((r) => setTimeout(r, interval));
    await nextTick();
  }
  throw new Error(`waitFor 超时 ${timeout}ms`);
}

/** 等待一个 tick */
export async function tick(times = 1) {
  for (let i = 0; i < times; i++) await nextTick();
}
```

使用示例：

```ts
it('异步列表出现后断言', async () => {
  const w = mount(UserList);
  await waitFor(() => w.findAll('.user-item').length > 0, { timeout: 2000 });
  expect(w.findAll('.user-item').length).toBeGreaterThan(0);
});
```

### 8.4 `vi.mock` 与异步

```ts
// ✅ 顶层 vi.mock（推荐：与 import 平级）
vi.mock('@/api/user', () => ({
  fetchUsers: vi.fn(() => Promise.resolve([{ id: 1, name: 'A' }]))
}));

// ✅ 在单个用例中改返回值
it('xxx', async () => {
  const mod = await import('@/api/user');
  (mod.fetchUsers as any).mockReturnValueOnce(Promise.resolve([]));
  // ...
});
```

> 经验教训：不要在 `it` 块内部使用 `vi.mock`（会导致提升顺序混乱），统一放在文件顶层或 `describe` 顶层。

---

## 九、常见依赖的 Mock 策略

### 9.1 Pinia Store Mock

```ts
// stores/user.ts
import { defineStore } from 'pinia';
export const useUserStore = defineStore('user', {
  state: () => ({ name: '', age: 0 }),
  getters: {
    adult: (s) => s.age >= 18
  },
  actions: {
    setAge(v: number) { this.age = v; }
  }
});
```

```ts
// stores/user.spec.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useUserStore } from './user';

beforeEach(() => setActivePinia(createPinia()));

describe('UserStore', () => {
  it('adult 根据 age 正确判断', () => {
    const s = useUserStore();
    expect(s.adult).toBe(false);
    s.setAge(20);
    expect(s.adult).toBe(true);
  });
});
```

**在组件测试中使用真实 Pinia（比 stub store 更稳）：**

```ts
// components/UserCard.spec.ts
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import UserCard from './UserCard.vue';
import { useUserStore } from '@/stores/user';

describe('UserCard', () => {
  it('展示 store 中的 name', () => {
    const pinia = createPinia();
    setActivePinia(pinia);             // 可选，全局插件已 set 可省略
    const store = useUserStore();
    store.$patch({ name: 'Alice', age: 20 });

    const w = mount(UserCard, { global: { plugins: [pinia] } });
    expect(w.text()).toContain('Alice');
  });
});
```

### 9.2 Vue Router Mock

```ts
// 方式一：使用真实路由（适合路由集成）
import { createMemoryHistory, createRouter } from 'vue-router';

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: 'home' } },
    { path: '/about', component: { template: 'about' } }
  ]
});

it('跳转到 about', async () => {
  const w = mount(MenuBar, { global: { plugins: [router] } });
  router.push('/');
  await router.isReady();
  await w.get('[data-testid="about-link"]').trigger('click');
  expect(router.currentRoute.value.path).toBe('/about');
});
```

```ts
// 方式二：mock useRouter（轻量推荐）
vi.mock('vue-router', async () => {
  const actual = await vi.importActual<any>('vue-router');
  const push = vi.fn();
  return {
    ...actual,
    useRouter: () => ({ push }),
    useRoute: () => ({ path: '/a', params: { id: '1' } })
  };
});

it('点击按钮调用 router.push(/next)', async () => {
  const { useRouter } = await import('vue-router');
  const w = mount(NextBtn);
  await w.trigger('click');
  expect(useRouter().push).toHaveBeenCalledWith('/next');
});
```

### 9.3 axios / request 层 Mock

```ts
// src/utils/request.ts（封装 axios）
import axios from 'axios';
export const request = axios.create({ baseURL: '/api' });
```

```ts
// src/api/user.ts
import { request } from '@/utils/request';
export interface User { id: number; name: string; }
export const fetchUsers = () =>
  request.get<User[]>('/users').then((r) => r.data);
```

**Mock 策略一：Mock request（拦截 axios 实例）**

```ts
// 测试顶层
vi.mock('@/utils/request', async () => {
  const actual = await vi.importActual<any>('@/utils/request');
  return {
    ...actual,
    request: {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn()
    }
  };
});
```

**Mock 策略二：Mock API 层（更干净）——**直接 mock 所有 `@/api/*` 导出（推荐）：

```ts
vi.mock('@/api/user', () => ({
  fetchUsers: vi.fn().mockResolvedValue([{ id: 1, name: 'A' }]),
  addUser: vi.fn().mockResolvedValue({ id: 2 }),
  updateUser: vi.fn().mockResolvedValue({})
}));
```

### 9.4 Element Plus Mock（全局级）

Element Plus 组件包含大量内部逻辑，测试组件时没必要真实渲染。通常 mock `ElMessage`、`ElMessageBox`、`ElNotification` 即可。真实 UI 组件可按需在 `global.components` 注册或直接 mount 测试。

setup 脚本中已经展示过标准写法，下面补充**在单个用例中验证调用**：

```ts
import { ElMessage, ElMessageBox } from 'element-plus';

it('删除失败时展示 ElMessage.error', async () => {
  (ElMessageBox.confirm as any).mockRejectedValueOnce(new Error('cancel'));
  const w = mount(UserRow);
  await w.get('[data-testid="del"]').trigger('click');
  expect(ElMessage.error).toHaveBeenCalledTimes(1);
});
```

### 9.5 i18n Mock

```ts
// 方式：全局 mocks 中的 $t 直接返回 key
const w = mount(MyI18nComponent, {
  global: {
    mocks: {
      $t: (key: string, opts?: any) =>
        opts ? `${key}:${JSON.stringify(opts)}` : key
    }
  }
});
expect(w.text()).toContain('common.confirm');  // key 即可
```

---

## 十、指令、插槽与 Teleport

### 10.1 自定义指令测试

```ts
// directives/focus.ts
import type { Directive } from 'vue';
export const vFocus: Directive = {
  mounted(el) { el.focus(); }
};
```

```ts
// directives/focus.spec.ts
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import { defineComponent, h } from 'vue';
import { vFocus } from './focus';

describe('vFocus', () => {
  it('mount 后自动 focus', () => {
    const Comp = defineComponent({
      directives: { focus: vFocus },
      template: '<input v-focus data-testid="i" />'
    });
    const w = mount(Comp, { attachTo: document.body });  // 真实 focus 需要挂载
    expect(document.activeElement).toBe(w.get('[data-testid="i"]').element);
    w.unmount();
  });
});
```

### 10.2 插槽测试

```ts
// components/Card.vue
<template>
  <div class="card">
    <header data-testid="head"><slot name="header" /></header>
    <main data-testid="body"><slot /></main>
    <slot name="footer" :author="author" />
  </div>
</template>
<script setup>
const author = 'Vue Team';
</script>
```

```ts
// components/Card.spec.ts
it('渲染默认/具名/作用域插槽', () => {
  const w = mount(Card, {
    slots: {
      header: () => 'Header',
      default: () => 'Body',
      footer: (props: any) => `© ${props.author}`
    }
  });
  expect(w.get('[data-testid="head"]').text()).toBe('Header');
  expect(w.get('[data-testid="body"]').text()).toBe('Body');
  expect(w.html()).toContain('© Vue Team');
});
```

### 10.3 Teleport 测试

```vue
<!-- components/Modal.vue -->
<template>
  <Teleport to="body">
    <div data-testid="modal-body" v-if="visible" class="modal">
      {{ title }}
    </div>
  </Teleport>
</template>
```

```ts
it('Teleport 的内容可以通过 document.body 找到', () => {
  const w = mount(Modal, {
    props: { visible: true, title: 'Hello' },
    attachTo: document.body
  });
  const modalBody = document.querySelector('[data-testid="modal-body"]');
  expect(modalBody?.textContent).toBe('Hello');
  w.unmount(); // 记得清理
  expect(document.querySelector('[data-testid="modal-body"]')).toBeNull();
});
```

---

## 十一、测试覆盖率分析

### 11.1 四个核心覆盖率指标

| 指标 | 含义 | 常见问题 |
|------|------|---------|
| **Lines（行覆盖）** | 每行代码是否至少执行了一次 | 最直观，容易刷高 |
| **Statements（语句覆盖）** | 每条语句是否执行 | 比 Lines 更细（一行多语句） |
| **Branches（分支覆盖）** | `if/else`、三元、`&&` 等分支是否全走到 | 核心指标，代表条件完备性 |
| **Functions（函数覆盖）** | 每个函数是否至少被调用 | 容易遗漏事件回调 |

### 11.2 生成报告

```bash
npm run test:coverage
# 产物默认在 coverage/ 下，打开 coverage/index.html 可交互
```

```
✓ src/utils/math.ts                    100 |        100 |       100 |        100 |
✓ src/composables/useCounter.ts        100 |        100 |       100 |        100 |
✓ src/components/BaseButton.vue     95.65 |      92.30 |        100 |        100 | 12-15
```

### 11.3 质量门禁（CI 中强制）

```ts
// vite.config.ts → test.coverage.thresholds
coverage: {
  thresholds: {
    lines: 80,
    branches: 70,
    functions: 80,
    statements: 80
  }
}
```

低于阈值 → CI 直接失败。

### 11.4 如何提升覆盖率的"质量"

| 做法 | 说明 |
|------|------|
| **先写组合函数 / 工具函数** | 便宜、快、没有副作用 |
| **错误分支必须有测试** | 不要只测"成功路径" |
| **边界条件** | 空、0、负数、超长字符串、跨时区日期 |
| **使用 mutation testing**（如 Stryker） | 检查你的测试是否能抓到 Bug |
| **避免为了覆盖率而写用例** | 没有断言的"走过场"测试毫无价值 |

---

## 十二、最佳实践与规范

### 12.1 AAA 模式（Arrange → Act → Assert）

```ts
it('✅ AAA 清晰三段', async () => {
  // 1. Arrange：准备环境
  const pinia = createPinia();
  const store = useUserStore(pinia);
  store.$patch({ name: 'A' });
  const w = mount(UserCard, { global: { plugins: [pinia] } });

  // 2. Act：做动作
  await w.get('button').trigger('click');

  // 3. Assert：断言结果
  expect(store.name).toBe('B');
  expect(w.text()).toContain('B');
});
```

### 12.2 每条用例一个断言点

```ts
// ❌ 一个 it 什么都测，失败不知道哪坏了
it('一大堆', async () => {
  expect(a).toBe(1);
  expect(b).toBe(2);
  // ...
});

// ✅ 一个 it 一个业务点
it('点击自增按钮 count+1', () => { /* ... */ });
it('点击重置按钮回到初始值', () => { /* ... */ });
it('props.count 变化时展示更新', () => { /* ... */ });
```

### 12.3 数据驱动（参数化测试）

```ts
import { describe, it, expect } from 'vitest';
import { formatDate } from './format';

describe.concurrent('formatDate 边界用例', () => {
  const cases: Array<[string, string]> = [
    ['2024-01-01', '2024年01月01日'],
    ['2024-12-31', '2024年12月31日'],
    ['2024-02-29', '2024年02月29日']
  ];

  it.each(cases)('formatDate(%s) => %s', (input, expected) => {
    expect(formatDate(input)).toBe(expected);
  });
});
```

### 12.4 稳定选择器：优先 `data-testid`

```vue
<template>
  <!-- ❌ 别用 .primary / button:nth-child(2) / :contains 等 -->
  <button data-testid="submit-order" class="primary large">
    提交订单
  </button>
</template>
```

```ts
// ✅ 稳定、不受 UI 文案/样式变化影响
w.get('[data-testid="submit-order"]');
```

### 12.5 避免过度依赖内部实现

```ts
// ❌ 测试内部字段，重构后必坏（setData/直接操作 vm.私有变量）
it('内部 xxx 设为 y', () => {
  (w.vm as any)._privateValue = 1;
});

// ✅ 用 Props / Events / 用户可见 DOM 驱动
it('props 变化后 emit change 且文案更新', async () => {
  await w.setProps({ value: 2 });
  expect(w.emitted('update:modelValue')?.pop()?.[0]).toBe(2);
  expect(w.text()).toContain('2');
});
```

### 12.6 单测隔离：每个用例独立

```ts
let wrapper: VueWrapper;
afterEach(() => {
  wrapper?.unmount();
  vi.clearAllMocks();
  vi.restoreAllMocks();   // 还原 spyOn
});
```

### 12.7 Snapshot 测试用于"防突变"

```ts
it('BaseButton 快照', () => {
  const { html } = mount(
    BaseButton, { props: { type: 'primary' }, slots: { default: 'Ok' } }
  );
  expect(html()).toMatchSnapshot();
});
```

生成 `__snapshots__/BaseButton.spec.ts.snap`，下次修改 SFC 时如果 HTML 变化会失败并提示更新快照（`-u` 更新）。

> **Snapshot 最佳实践**：对稳定的"展示组件"做快照，不要对大容器组件做快照（快照体积大，频繁变更）。

### 12.8 覆盖率 vs 质量

> 80% 的覆盖率是**起点**不是终点。一个没写断言却跑了所有代码的测试，和没写差不多。优先写"断言行为"的测试，然后让覆盖率自然提高。

---

## 十三、常见问题与解决方案

### 13.1 `document is not defined`

**原因**：vitest environment 没设为 `jsdom`。

**修复**：`vite.config.ts` 中 `test.environment = 'jsdom'`。不要在测试里手动写 `global.document = ...` 补丁。

### 13.2 `ResizeObserver is not defined` / `matchMedia is not defined`

**原因**：jsdom 没实现这些浏览器 API。

**修复**：统一在 `setup.ts` 里用空实现 mock（见 4.2 节）。不要每个测试文件写一份。

### 13.3 CSS / Element Plus 样式导入报错

**原因**：Vitest 处理 `.css` / `scss` 失败。

**修复**（Vitest）：
```ts
test: {
  css: {
    modules: { classNameStrategy: 'non-scoped' }
  }
}
```
若某些 CSS 依赖强绑定到运行时，把对应 `import 'xxx.css'` 从源文件中移到入口（`main.ts`），测试用 mount 时通过 `global.mocks` 跳过。

### 13.4 `Cannot find module '@/xxx'`

**原因**：测试环境没有复用 Vite 的 alias。

**修复**：vitest 在 `vite.config.ts` 中直接共用 `resolve.alias`（本文 4.1 节已配）。另需在 `tsconfig.json` 配 `paths` 以便类型解析。

### 13.5 异步组件 / 动态导入的 stub

```ts
// 异步组件：使用 shallowMount 时会自动 stub
import { defineAsyncComponent } from 'vue';
// 如需要手动 stub
const w = mount(Container, {
  global: {
    stubs: {
      'async-child': { template: '<div class="async-child" />' }
    }
  }
});
```

### 13.6 `wrapper.trigger('click')` 不触发回调

**常见原因**：
1. 没 `await trigger` → 改成 `await w.trigger('click')`
2. 按钮被 `disabled` → 检查 `attributes('disabled')`
3. 组件是自定义组件，需要先解包到原生按钮：
   `w.findComponent(MyButton).find('button').trigger('click')`

### 13.7 测试 ESM 依赖 `import.xxx()` 报错

**修复**：Vitest 本身原生 ESM，基本不需要 transform。若必须兼容老 CJS 包，在 `deps.optimizer.web.transformInclude` 中加入：

```ts
test: {
  deps: {
    optimizer: {
      web: {
        transformInclude: [/some-cjs-only-lib/]
      }
    }
  }
}
```

### 13.8 "快照不断变更导致 CI 失败"

**原因**：快照包含随机、时间戳、动态 ID、时间相关数据。

**修复**：

```ts
// 统一 mock 时间
beforeEach(() => {
  vi.setSystemTime(new Date('2026-01-01'));
});
// 或在快照中 strip 动态字段
expect({ ...obj, createdAt: '__ANY__' }).toMatchSnapshot();
```

### 13.9 Pinia 在 `beforeEach` 里 `$reset` 不生效

**修复**：每个用例用新的 Pinia 实例或 `vi.isolateComponents`：

```ts
beforeEach(() => {
  setActivePinia(createPinia());  // 每次 create 新的
});
```

### 13.10 Windows 路径反斜杠 vs 别名

**修复**：统一用 `fileURLToPath(new URL('./src', import.meta.url))` 定义 alias（本文 4.1），不要写硬编码 `./src` + 反斜杠字符串拼接（来源：Experience 209105 Windows PowerShell 适配经验）。

---

## 十四、CI/CD 集成

### 14.1 GitHub Actions 工作流

```yaml
# .github/workflows/test.yml
name: Unit Test & Coverage
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run test:coverage
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage-report
          path: coverage
```

### 14.2 Git Hooks 强制执行（可选）

```bash
# package.json scripts + husky
"scripts": {
  "test:staged": "vitest run --related"
}
```

### 14.3 并行执行

```ts
// vite.config.ts
test: {
  pool: 'threads',        // 线程池（Node 20+ 推荐）
  poolOptions: { threads: { minThreads: 2, maxThreads: 6 } },
  fileParallelism: true
}
```

---

## 十五、实战示例：完整项目单测

### 15.1 一个真实组件的完整测试

```vue
<!-- components/TodoList.vue -->
<script setup lang="ts">
import { computed, reactive } from 'vue';
import { ElMessage } from 'element-plus';

interface Todo { id: number; text: string; done: boolean; }
const props = defineProps<{ initial?: Todo[] }>();
const emit = defineEmits<{ (e: 'save', todos: Todo[]): void }>();

const list = reactive<Todo[]>(props.initial ?? []);
const inputText = reactive({ v: '' });

const left = computed(() => list.filter((t) => !t.done).length);

function add() {
  const t = inputText.v.trim();
  if (!t) return ElMessage.warning('内容不能为空');
  list.push({ id: Date.now(), text: t, done: false });
  inputText.v = '';
}

function toggle(id: number) {
  const item = list.find((i) => i.id === id);
  if (item) item.done = !item.done;
}

function submit() {
  if (list.length === 0) return ElMessage.error('请先添加');
  emit('save', JSON.parse(JSON.stringify(list)));
  ElMessage.success('已保存');
}
</script>
<template>
  <div>
    <input data-testid="input" v-model="inputText.v" @keydown.enter.prevent="add" />
    <button data-testid="add" @click="add">添加</button>
    <ul data-testid="list">
      <li v-for="t in list" :key="t.id" :class="{ done: t.done }">
        <label>
          <input type="checkbox" :checked="t.done" @change="toggle(t.id)" />
          {{ t.text }}
        </label>
      </li>
    </ul>
    <p data-testid="left">剩余：{{ left }}</p>
    <button data-testid="submit" @click="submit">保存</button>
  </div>
</template>
```

```ts
// components/TodoList.spec.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { ElMessage } from 'element-plus';
import TodoList from './TodoList.vue';

beforeEach(() => {
  // 每次用例 reset mock 调用记录（setup.ts 里 vi.mock('element-plus')）
  vi.clearAllMocks();
});

describe('TodoList', () => {
  it('空输入添加时提示并拒绝', async () => {
    const w = mount(TodoList);
    await w.get('[data-testid="add"]').trigger('click');
    expect(ElMessage.warning).toHaveBeenCalledWith('内容不能为空');
    expect(w.findAll('li')).toHaveLength(0);
  });

  it('输入后回车或点击添加都可插入', async () => {
    const w = mount(TodoList);

    await w.get('[data-testid="input"]').setValue('task 1');
    await w.get('[data-testid="input"]').trigger('keydown.enter');
    expect(w.findAll('li')).toHaveLength(1);

    await w.get('[data-testid="input"]').setValue('task 2');
    await w.get('[data-testid="add"]').trigger('click');
    expect(w.findAll('li')).toHaveLength(2);
    expect(w.get('[data-testid="left"]').text()).toContain('2');
  });

  it('点击 checkbox 切换 done 状态并更新剩余', async () => {
    const w = mount(TodoList, {
      props: {
        initial: [
          { id: 1, text: 'A', done: false },
          { id: 2, text: 'B', done: false }
        ]
      }
    });
    expect(w.get('[data-testid="left"]').text()).toContain('2');

    const firstCb = w.findAll('input[type=checkbox]')[0];
    await firstCb.setValue(true);   // 触发 change

    expect(firstCb.element.checked).toBe(true);
    expect(w.get('[data-testid="left"]').text()).toContain('1');
  });

  it('空列表保存给出错误，有数据保存 emit save 且 success', async () => {
    const w1 = mount(TodoList);
    await w1.get('[data-testid="submit"]').trigger('click');
    expect(ElMessage.error).toHaveBeenCalledWith('请先添加');
    expect(w1.emitted('save')).toBeUndefined();

    const w2 = mount(TodoList, {
      props: { initial: [{ id: 1, text: 'A', done: false }] }
    });
    await w2.get('[data-testid="submit"]').trigger('click');
    const save = w2.emitted('save')?.[0]?.[0];
    expect(save).toEqual([{ id: 1, text: 'A', done: false }]);
    expect(ElMessage.success).toHaveBeenCalledWith('已保存');
  });
});
```

### 15.2 完整项目测试目录参考

```
src/
├── components/
│   ├── BaseButton.vue                  展示组件
│   ├── BaseButton.spec.ts              ✅ 渲染、事件、样式、disabled/loading
│   ├── TodoList.vue                    容器组件
│   ├── TodoList.spec.ts                ✅ 交互、v-model、空数据、emit、ElMessage
│   └── LoginForm.vue
├── composables/
│   ├── useCounter.ts / useNow.ts / useFetch.ts / useTheme.ts
│   └── *.spec.ts                       ✅ 优先写，成本低回报高
├── stores/
│   └── user.ts / user.spec.ts          ✅ state/getters/actions 三件套
├── utils/
│   ├── format.ts / math.ts / request.ts
│   └── *.spec.ts                       ✅ 100% 覆盖（含异常分支）
├── api/
│   └── user.ts                         (不单独测，通过组件 + vi.mock 覆盖)
└── test/
    ├── setup.ts                        全局 setup
    └── utils.ts                        waitFor / tick 助手
```

---

## 十六、Vue 2 到 Vue 3 单测迁移速查

| 问题 | Vue 2 (vue-test-utils v1) | Vue 3 (@vue/test-utils v2) |
|------|---------------------------|---------------------------|
| 挂载 | `mount()` / `shallowMount()` | 同名，选项结构统一放 `global.*` |
| 全局配置 | `createLocalVue` + `Vue.use` | `global.plugins`、`global.mocks` |
| 全局变量 | `mocks.$t` / `mocks.$store` | 同左 |
| 设置数据 | `wrapper.setData({ x: 1 })` | `(wrapper.vm as any).x = 1` (不推荐，通过交互驱动) |
| `find` | `wrapper.find('.x')` | 同左，但**没有** `wrapper.find({ name })`，改用 `findComponent` |
| `.vm.$el` | `wrapper.element` | 同左 |
| v-model 监听 | `await wrapper.vm.$emit('update:xxx', v)` | `wrapper.get('[data-testid]').setValue(v)` |
| 生命周期 | `wrapper.destroy()` | 改名 `wrapper.unmount()` |

---

## 参考资料

- [Vue Test Utils 官方文档（Vue 3）](https://test-utils.vuejs.org/)
- [Vitest 官方文档](https://vitest.dev/)
- [Testing Library 断言（vitest-dom）](https://github.com/testing-library/jest-dom)
- [Vitest + Vue 快速开始](https://vitest.dev/guide/#using-vitest-with-vue)
- [Pinia 测试文档](https://pinia.vuejs.org/cookbook/testing.html)
- [Vue Router 测试](https://router.vuejs.org/guide/advanced/testing.html)
- [jsdom 仓库](https://github.com/jsdom/jsdom)
- [JSON-RPC 2.0 规范](https://www.jsonrpc.org/specification)
