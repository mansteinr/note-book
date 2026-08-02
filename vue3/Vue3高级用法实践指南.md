# Vue3 高级用法实践指南

> 本文档系统讲解 Vue3 核心高级特性的实现与应用，涵盖组合式 API、响应式系统（Reactive/Ref/Computed）、自定义 Hooks、Teleport、Suspense 与异步组件、依赖注入（Provide/Inject）、组合式函数封装、自定义指令等内容。每个特性均提供完整 TypeScript 代码示例、详细注释与实际应用场景演示，并附项目结构规范、ESLint/Prettier 配置与使用指南。

---

## 目录

- [一、项目结构与工程配置](#一项目结构与工程配置)
  - [1.1 推荐项目结构](#11-推荐项目结构)
  - [1.2 TypeScript 配置](#12-typescript-配置)
  - [1.3 ESLint 配置](#13-eslint-配置)
  - [1.4 Prettier 配置](#14-prettier-配置)
- [二、组合式 API（Composition API）](#二组合式-apicomposition-api)
  - [2.1 setup 函数与 `<script setup>`](#21-setup-函数与-script-setup)
  - [2.2 生命周期钩子](#22-生命周期钩子)
  - [2.3 响应式 API 总览](#23-响应式-api-总览)
- [三、响应式系统详解](#三响应式系统详解)
  - [3.1 reactive 与 ref](#31-reactive-与-ref)
  - [3.2 computed 计算属性](#32-computed-计算属性)
  - [3.3 watch 与 watchEffect](#33-watch-与-watcheffect)
  - [3.4 响应式工具函数](#34-响应式工具函数)
- [四、自定义 Hooks（组合式函数封装）](#四自定义-hooks组合式函数封装)
- [五、Teleport 组件](#五teleport-组件)
- [六、Suspense 与异步组件](#六suspense-与异步组件)
- [七、依赖注入（Provide/Inject）](#七依赖注入provideinject)
- [八、自定义指令](#八自定义指令)
- [九、使用指南与最佳实践](#九使用指南与最佳实践)
- [附录 完整示例索引](#附录-完整示例索引)

---

## 一、项目结构与工程配置

### 1.1 推荐项目结构

```
vue3-advanced-practice/
├── .vscode/
│   ├── extensions.json          # 推荐插件
│   └── settings.json            # 项目设置
├── public/
│   └── favicon.ico
├── src/
│   ├── assets/                  # 静态资源
│   │   └── styles/
│   │       └── main.css
│   ├── components/              # 通用组件
│   │   ├── ModalDialog.vue      # Teleport 弹窗
│   │   ├── AsyncChart.vue       # 异步组件
│   │   └── DraggableCard.vue    # 拖拽组件
│   ├── composables/             # 自定义 Hooks（组合式函数）
│   │   ├── useMouse.ts
│   │   ├── useFetch.ts
│   │   ├── useLocalStorage.ts
│   │   ├── useDebounce.ts
│   │   ├── useEventListener.ts
│   │   ├── usePagination.ts
│   │   └── index.ts
│   ├── directives/              # 自定义指令
│   │   ├── index.ts
│   │   ├── permission.ts        # v-permission
│   │   ├── debounce.ts          # v-debounce
│   │   ├── lazy.ts              # v-lazy
│   │   ├── draggable.ts         # v-draggable
│   │   └── copy.ts              # v-copy
│   ├── examples/                # 特性演示页面
│   │   ├── ReactiveDemo.vue
│   │   ├── ComputedDemo.vue
│   │   ├── HooksDemo.vue
│   │   ├── TeleportDemo.vue
│   │   ├── SuspenseDemo.vue
│   │   ├── ProvideInjectDemo.vue
│   │   └── DirectivesDemo.vue
│   ├── router/
│   │   └── index.ts
│   ├── types/                   # 类型定义
│   │   └── index.ts
│   ├── App.vue
│   └── main.ts
├── .eslintrc.cjs
├── .prettierrc
├── .gitignore
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
└── README.md
```

**目录职责说明**：

| 目录 | 职责 | 命名规范 |
| --- | --- | --- |
| `components/` | 全局通用组件，无业务逻辑 | PascalCase |
| `composables/` | 可复用的组合式函数 | camelCase，`use` 前缀 |
| `directives/` | 自定义指令 | camelCase |
| `examples/` | 各特性演示页面 | PascalCase + Demo 后缀 |
| `types/` | 全局类型定义 | kebab-case + `.d.ts` |

### 1.2 TypeScript 配置

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ESNext",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,                          // 严格模式（必开）
    "jsx": "preserve",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "lib": ["ESNext", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "noUnusedLocals": true,                  // 未使用变量报错
    "noUnusedParameters": true,              // 未使用参数报错
    "noFallthroughCasesInSwitch": true,      // switch 穿透报错
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]                       // 路径别名
    },
    "types": ["vite/client"]
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

```json
// tsconfig.node.json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

**类型声明文件**（让 TypeScript 识别 `.vue` 文件）：

```typescript
// src/types/shims-vue.d.ts
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// 环境变量类型
interface ImportMetaEnv {
  readonly VITE_APP_TITLE: string
  readonly VITE_APP_BASE_API: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

### 1.3 ESLint 配置

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
    'plugin:vue/vue3-recommended',           // Vue3 推荐规则
    '@vue/eslint-config-typescript',         // TS 支持
    '@vue/eslint-config-prettier',           // 关闭与 Prettier 冲突的规则
  ],
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@typescript-eslint/parser',
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  rules: {
    // Vue 规则
    'vue/multi-word-component-names': 'off',              // 允许单词组件名
    'vue/component-name-in-template-casing': ['error', 'PascalCase'],
    'vue/component-tags-order': ['error', { order: ['script', 'template', 'style'] }],
    'vue/block-order': ['error', { order: ['script', 'template', 'style'] }],
    
    // TypeScript 规则
    '@typescript-eslint/no-explicit-any': 'warn',         // any 警告
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/consistent-type-imports': 'error', // 统一 type import
    
    // 通用规则
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'no-debugger': 'warn',
    'prefer-const': 'error',
    'no-var': 'error',
    'eqeqeq': ['error', 'always'],                        // 必须用 ===
  },
}
```

### 1.4 Prettier 配置

```json
// .prettierrc
{
  "semi": false,                // 不用分号
  "singleQuote": true,          // 单引号
  "trailingComma": "es5",       // 尾逗号
  "tabWidth": 2,                // 缩进 2 空格
  "useTabs": false,
  "printWidth": 100,            // 每行最大 100 字符
  "endOfLine": "lf",
  "arrowParens": "always"       // 箭头函数参数总是加括号
}
```

**Vite 配置**：

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    open: true,
  },
})
```

**package.json 核心依赖**：

```json
{
  "name": "vue3-advanced-practice",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc --noEmit && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext .vue,.js,.ts --fix",
    "format": "prettier --write src/",
    "type-check": "vue-tsc --noEmit"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vue-tsc": "^1.8.0",
    "eslint": "^8.56.0",
    "eslint-plugin-vue": "^9.20.0",
    "prettier": "^3.1.0"
  }
}
```

---

## 二、组合式 API（Composition API）

### 2.1 setup 函数与 `<script setup>`

**Composition API** 是 Vue3 的核心特性，解决了 Options API 在大型组件中逻辑分散、复用困难的问题。

**Options API 的痛点**（逻辑分散）：

```javascript
// 同一个功能的代码被拆散到 data/methods/computed/ watch 各处
export default {
  data() {
    return { count: 0 }           // ← 计数器数据
  },
  computed: {
    double() {                    // ← 计数器计算
      return this.count * 2
    }
  },
  methods: {
    increment() {                 // ← 计数器方法
      this.count++
    }
  },
  watch: {
    count(val) {                  // ← 计数器监听
      console.log('count:', val)
    }
  }
}
```

**Composition API 的优势**（逻辑聚合）：

```vue
<!-- 使用 <script setup> 语法糖（推荐） -->
<script setup lang="ts">
import { ref, computed, watch } from 'vue'

// ✅ 计数器功能的所有逻辑聚在一起
const count = ref(0)                              // 响应式数据
const double = computed(() => count.value * 2)    // 计算属性
function increment() {                            // 方法
  count.value++
}
watch(count, (val) => {                           // 监听
  console.log('count:', val)
})
</script>

<template>
  <div>
    <p>count: {{ count }} | double: {{ double }}</p>
    <button @click="increment">+1</button>
  </div>
</template>
```

**`<script setup>` 的核心优势**：

| 特性 | 说明 |
| --- | --- |
| **无需 return** | 顶层变量/函数自动暴露给模板 |
| **无需 components 注册** | import 的组件直接使用 |
| **更好的类型推导** | TS 支持更完善 |
| **编译优化** | 编译后性能更好 |
| **更少样板代码** | 代码更简洁 |

**`defineProps` 与 `defineEmits`**（编译宏，无需 import）：

```vue
<script setup lang="ts">
// 定义 Props（带类型）
interface Props {
  title: string
  count?: number              // 可选
  type?: 'primary' | 'danger' | 'default'  // 联合类型
}

// withDefaults 设置默认值
const props = withDefaults(defineProps<Props>(), {
  count: 0,
  type: 'default',
})

// 定义 Emits（带类型校验）
const emit = defineEmits<{
  (e: 'change', value: number): void
  (e: 'submit', data: { id: number; name: string }): void
}>()

function handleClick() {
  emit('change', props.count + 1)
}
</script>

<template>
  <button :class="`btn-${props.type}`" @click="handleClick">
    {{ props.title }} ({{ props.count }})
  </button>
</template>
```

**`defineExpose`**（暴露组件方法给父组件 ref）：

```vue
<!-- Child.vue -->
<script setup lang="ts">
import { ref } from 'vue'

const count = ref(0)

// <script setup> 默认不暴露任何内容
// 父组件 ref 拿不到内部数据，需用 defineExpose 显式暴露
function reset() {
  count.value = 0
}

function increment() {
  count.value++
}

defineExpose({ count, reset, increment })
</script>
```

```vue
<!-- Parent.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Child from './Child.vue'

const childRef = ref<InstanceType<typeof Child>>()

onMounted(() => {
  // 调用子组件暴露的方法
  childRef.value?.increment()
  console.log(childRef.value?.count)  // 1
})
</script>

<template>
  <Child ref="childRef" />
  <button @click="childRef?.reset()">重置子组件</button>
</template>
```

### 2.2 生命周期钩子

Vue3 的生命周期钩子在 Composition API 中以 `on` 前缀函数形式使用：

```vue
<script setup lang="ts">
import {
  onBeforeMount,    // 挂载前
  onMounted,        // 挂载后（常用）
  onBeforeUpdate,   // 更新前
  onUpdated,        // 更新后
  onBeforeUnmount,  // 卸载前（常用，清理定时器/事件）
  onUnmounted,      // 卸载后
  onErrorCaptured,  // 捕获后代组件错误
  onActivated,      // keep-alive 激活
  onDeactivated,    // keep-alive 停用
} from 'vue'

// 挂载后：操作 DOM、发起请求
onMounted(() => {
  console.log('组件已挂载，DOM 可访问')
  window.addEventListener('resize', handleResize)
})

// 卸载前：清理副作用（定时器、事件监听、WebSocket）
onBeforeUnmount(() => {
  console.log('组件即将卸载，清理资源')
  window.removeEventListener('resize', handleResize)
  clearInterval(timer)
})

// 错误捕获（用于错误边界）
onErrorCaptured((err, instance, info) => {
  console.error('子组件错误:', err, info)
  return false  // 返回 false 阻止错误继续向上冒泡
})

const timer = setInterval(() => {}, 1000)
function handleResize() { /* ... */ }
</script>
```

**生命周期对照表**：

| Options API | Composition API | 说明 |
| --- | --- | --- |
| `beforeCreate` | `setup()` 开始 | 初始化响应式数据 |
| `created` | `setup()` 结束 | 可访问响应式数据 |
| `beforeMount` | `onBeforeMount` | DOM 挂载前 |
| `mounted` | `onMounted` | DOM 挂载后 |
| `beforeUpdate` | `onBeforeUpdate` | 数据更新前 |
| `updated` | `onUpdated` | 数据更新后 |
| `beforeUnmount` | `onBeforeUnmount` | 组件卸载前 |
| `unmounted` | `onUnmounted` | 组件卸载后 |
| `errorCaptured` | `onErrorCaptured` | 后代错误捕获 |
| `activated` | `onActivated` | keep-alive 激活 |
| `deactivated` | `onDeactivated` | keep-alive 停用 |

### 2.3 响应式 API 总览

```typescript
import {
  ref,              // 基本类型响应式
  reactive,         // 对象响应式
  readonly,         // 只读代理
  shallowRef,       // 浅层 ref（只对 .value 响应）
  shallowReactive,  // 浅层 reactive（只对第一层响应）
  toRef,            // reactive 属性转 ref
  toRefs,           // reactive 所有属性转 ref
  isRef,            // 判断是否为 ref
  isReactive,       // 判断是否为 reactive
  isProxy,          // 判断是否为 proxy
  unref,            // 获取 ref 的值（ref 则取 .value，否则原样返回）
  computed,         // 计算属性
  watch,            // 侦听器
  watchEffect,      // 自动收集依赖的侦听器
  customRef,        // 自定义 ref（控制依赖追踪与触发）
  markRaw,          // 标记对象永不转为响应式
  effectScope,      // 副作用作用域
} from 'vue'
```

---

## 三、响应式系统详解

### 3.1 reactive 与 ref

**reactive**：用于对象/数组，基于 Proxy 实现深度响应式。

```typescript
import { reactive, isReactive } from 'vue'

// reactive：对象类型响应式（Proxy 代理）
interface User {
  name: string
  age: number
  hobbies: string[]
  address: {
    city: string
    street: string
  }
}

const user = reactive<User>({
  name: '张三',
  age: 25,
  hobbies: ['读书', '游泳'],
  address: { city: '北京', street: '朝阳路' },
})

// 直接访问修改（无需 .value）
console.log(user.name)           // '张三'
user.age = 26                     // ✅ 触发更新
user.hobbies.push('编程')          // ✅ 数组方法也能触发
user.address.city = '上海'         // ✅ 嵌套对象也响应式（深度）

console.log(isReactive(user))             // true
console.log(isReactive(user.address))     // true（嵌套也是 reactive）
```

**ref**：用于基本类型（也可用于对象），通过 `.value` 访问。

```typescript
import { ref, isRef } from 'vue'

// ref：任意类型响应式
const count = ref<number>(0)              // 基本类型
const name = ref<string>('张三')           // 字符串
const user = ref<User>({ name: '李四', age: 30 })  // 对象（内部用 reactive）
const list = ref<string[]>([])             // 数组

// 访问需 .value
console.log(count.value)     // 0
count.value++                 // ✅ 修改需 .value
console.log(name.value)       // '张三'

// ref 包裹对象时，.value 是 reactive 代理
user.value.age = 31           // ✅ 内部自动用 reactive
console.log(isRef(user))      // true
console.log(isRef(count))     // true
```

**reactive 与 ref 的选择**：

| 维度 | ref | reactive |
| --- | --- | --- |
| 适用类型 | 基本类型 + 对象 | 仅对象 |
| 访问方式 | `.value` | 直接访问 |
| 模板中 | 自动解包（无需 .value） | 直接访问 |
| 解构 | 不会失去响应性（用 toRefs） | ❌ 解构失去响应性 |
| 重新赋值 | ✅ `xxx.value = newObj` | ❌ 不能整体替换 |
| 推荐场景 | 简单值、需替换整体 | 表单、复杂对象 |

**reactive 的陷阱**：解构丢失响应性 + 不能整体替换。

```typescript
const state = reactive({ count: 0, name: '张三' })

// ❌ 陷阱1：解构丢失响应性
let { count, name } = state
count++              // 不会触发更新（count 是普通变量）

// ✅ 解决：用 toRefs 解构
const { count, name } = toRefs(state)
count.value++        // ✅ 保持响应性

// ❌ 陷阱2：整体替换会失去响应性
// state = { count: 1, name: '李四' }  // 错误！丢失响应性

// ✅ 解决：用 ref 或 Object.assign
const stateRef = ref({ count: 0, name: '张三' })
stateRef.value = { count: 1, name: '李四' }  // ✅ ref 可替换
Object.assign(state, { count: 1, name: '李四' })  // ✅ 合并属性
```

**实际应用场景：表单状态管理**

```vue
<script setup lang="ts">
import { reactive, ref } from 'vue'

interface FormState {
  username: string
  password: string
  remember: boolean
}

// 表单用 reactive（对象，字段多）
const form = reactive<FormState>({
  username: '',
  password: '',
  remember: false,
})

// 提交状态用 ref（基本类型）
const loading = ref(false)
const errorMsg = ref('')

async function handleSubmit() {
  loading.value = true
  errorMsg.value = ''
  try {
    await login(form)
    // 成功后重置表单
    Object.assign(form, { username: '', password: '', remember: false })
  } catch (e) {
    errorMsg.value = (e as Error).message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <form @submit.prevent="handleSubmit">
    <input v-model="form.username" placeholder="用户名" />
    <input v-model="form.password" type="password" placeholder="密码" />
    <el-checkbox v-model="form.remember">记住我</el-checkbox>
    <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
    <button type="submit" :disabled="loading">
      {{ loading ? '登录中...' : '登录' }}
    </button>
  </form>
</template>
```

### 3.2 computed 计算属性

**computed**：基于响应式依赖缓存计算结果，依赖不变时返回缓存值。

```typescript
import { ref, computed } from 'vue'

const firstName = ref('张')
const lastName = ref('三')

// 只读计算属性
const fullName = computed(() => `${firstName.value}${lastName.value}`)
console.log(fullName.value)  // '张三'

// 依赖不变，多次访问只计算一次（缓存）
fullName.value  // 缓存
fullName.value  // 缓存

firstName.value = '李'  // 依赖变化
fullName.value  // '李三'（重新计算）
```

**可写计算属性**（getter + setter）：

```typescript
const fullName = computed({
  get() {
    return `${firstName.value}${lastName.value}`
  },
  set(newValue: string) {
    // 假设格式为 "姓 名"
    const [first, last] = newValue.split(' ')
    firstName.value = first
    lastName.value = last || ''
  },
})

fullName.value = '王 五'
console.log(firstName.value)  // '王'
console.log(lastName.value)   // '五'
```

**实际应用场景：购物车计算**

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'

interface CartItem {
  id: number
  name: string
  price: number
  quantity: number
}

const cart = ref<CartItem[]>([
  { id: 1, name: 'iPhone', price: 8999, quantity: 1 },
  { id: 2, name: 'iPad', price: 4999, quantity: 2 },
])

// 计算总数量
const totalCount = computed(() =>
  cart.value.reduce((sum, item) => sum + item.quantity, 0)
)

// 计算总价
const totalPrice = computed(() =>
  cart.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
)

// 折扣后价格（依赖其他 computed）
const discount = ref(0.9)  // 9 折
const finalPrice = computed(() => Math.round(totalPrice.value * discount.value))

// 满减判断
const freeShipping = computed(() => totalPrice.value >= 10000)

// 格式化金额
const formattedPrice = computed(() =>
  `¥${finalPrice.value.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}`
)
</script>

<template>
  <div>
    <div v-for="item in cart" :key="item.id">
      {{ item.name }} × {{ item.quantity }} = ¥{{ item.price * item.quantity }}
    </div>
    <hr />
    <p>商品数量：{{ totalCount }}</p>
    <p>原价：¥{{ totalPrice }}</p>
    <p>折后：{{ formattedPrice }}</p>
    <p>运费：{{ freeShipping ? '免运费' : '¥20' }}</p>
  </div>
</template>
```

### 3.3 watch 与 watchEffect

**watch**：显式指定侦听的源，可获取新值与旧值。

```typescript
import { ref, watch } from 'vue'

const count = ref(0)

// 侦听单个 ref
watch(count, (newVal, oldVal) => {
  console.log(`count: ${oldVal} → ${newVal}`)
})

// 侦听多个源
const firstName = ref('张')
const lastName = ref('三')
watch([firstName, lastName], ([newFirst, newLast], [oldFirst, oldLast]) => {
  console.log(`姓名变化: ${oldFirst}${oldLast} → ${newFirst}${newLast}`)
})

// 侦听 reactive 属性（需用 getter 函数）
const state = reactive({ user: { name: '张三', age: 25 } })
watch(
  () => state.user.name,                    // getter 返回要侦听的值
  (newVal, oldVal) => {
    console.log(`name: ${oldVal} → ${newVal}`)
  }
)

// 侦听 reactive 对象（深度默认开启）
watch(state, (newVal) => {
  console.log('state 变化', newVal)
})

// 侦听 ref 对象（需开启 deep 才能侦听内部变化）
const obj = ref({ a: 1 })
watch(obj, (newVal) => {
  console.log('obj 变化', newVal)
}, { deep: true })                            // ✅ 深度侦听
```

**watch 选项**：

```typescript
watch(source, callback, {
  immediate: true,    // 立即执行一次（默认 false）
  deep: true,         // 深度侦听（对象内部变化）
  flush: 'post',      // 回调执行时机：'pre'(默认,DOM更新前) | 'post'(DOM更新后) | 'sync'(同步)
  once: true,         // 只触发一次（Vue 3.4+）
})
```

```typescript
// immediate：立即执行（初始化时也触发）
const userId = ref(1)
watch(userId, (id) => {
  fetchUserDetail(id)  // 侦听 + 初始化都执行
}, { immediate: true })

// once：只触发一次
watch(loading, (val) => {
  if (!val) console.log('首次加载完成')
}, { once: true })
```

**watchEffect**：自动收集依赖，无需指定侦听源。

```typescript
import { ref, watchEffect } from 'vue'

const count = ref(0)
const name = ref('张三')

// 自动追踪回调内使用的响应式依赖
watchEffect(() => {
  console.log(`count=${count.value}, name=${name.value}`)
  // 用到 count 和 name，自动侦听两者
})
// 立即输出：count=0, name=张三

count.value++   // 输出：count=1, name=张三
name.value = '李四'  // 输出：count=1, name=李四

// 清理副作用
watchEffect((onCleanup) => {
  const timer = setTimeout(() => {
    console.log('执行', count.value)
  }, 1000)
  
  // 依赖变化或组件卸载时调用清理
  onCleanup(() => {
    clearTimeout(timer)
  })
})
```

**watch vs watchEffect 对比**：

| 维度 | watch | watchEffect |
| --- | --- | --- |
| 侦听源 | 显式指定 | 自动收集 |
| 旧值 | ✅ 可获取 | ❌ 无法获取 |
| 立即执行 | 需 `immediate: true` | 默认立即执行 |
| 多源侦听 | ✅ 支持 | 自动（用到就侦听） |
| 适用场景 | 需要新旧值对比、精确控制 | 仅执行副作用 |

**实际应用场景：搜索防抖**

```vue
<script setup lang="ts">
import { ref, watch } from 'vue'

const keyword = ref('')
const searchResults = ref<string[]>([])
const loading = ref(false)

// 侦听搜索关键词，防抖请求
watch(keyword, (newVal) => {
  if (!newVal.trim()) {
    searchResults.value = []
    return
  }
  
  loading.value = true
  // 防抖：500ms 内无变化才请求
  const timer = setTimeout(async () => {
    try {
      const data = await fetch(`/api/search?q=${newVal}`).then(r => r.json())
      searchResults.value = data.results
    } finally {
      loading.value = false
    }
  }, 500)
  
  // cleanup：下次触发前清除上次定时器
  return () => clearTimeout(timer)
})
</script>

<template>
  <input v-model="keyword" placeholder="搜索..." />
  <div v-if="loading">搜索中...</div>
  <ul v-else>
    <li v-for="item in searchResults" :key="item">{{ item }}</li>
  </ul>
</template>
```

### 3.4 响应式工具函数

```typescript
import {
  ref, reactive, toRef, toRefs, unref, isRef, isReactive,
  readonly, shallowRef, shallowReactive, customRef, markRaw,
} from 'vue'

// 1. toRef：reactive 属性转 ref（保持引用关联）
const state = reactive({ name: '张三', age: 25 })
const nameRef = toRef(state, 'name')  // ref，与 state.name 关联
nameRef.value = '李四'
console.log(state.name)  // '李四'（同步变化）

// 2. toRefs：reactive 所有属性转 ref（解构用）
const { name, age } = toRefs(state)
name.value = '王五'
console.log(state.name)  // '王五'

// 3. unref：获取值（ref 取 .value，非 ref 原样返回）
const a = ref(1)
const b = 2
console.log(unref(a))  // 1
console.log(unref(b))  // 2

// 4. readonly：只读代理（防止误改）
const original = reactive({ count: 0 })
const copy = readonly(original)
// copy.count = 1  // ❌ 警告：只读不可修改
original.count = 1
console.log(copy.count)  // 1（原对象变化，只读代理同步）

// 5. shallowRef / shallowReactive：浅层响应式（性能优化）
const shallow = shallowRef({ a: { b: 1 } })
shallow.value.a.b = 2      // ❌ 不触发更新（深层不响应）
shallow.value = { a: { b: 2 } }  // ✅ 触发更新（.value 替换）

const shallowObj = shallowReactive({ a: 1, nested: { b: 2 } })
shallowObj.a = 2            // ✅ 第一层响应
shallowObj.nested.b = 3     // ❌ 嵌套不响应

// 6. customRef：自定义 ref（防抖场景）
function debouncedRef<T>(value: T, delay = 200) {
  let timer: number
  return customRef<T>((track, trigger) => {
    return {
      get() {
        track()                    // 追踪依赖
        return value
      },
      set(newValue: T) {
        clearTimeout(timer)
        timer = setTimeout(() => {
          value = newValue
          trigger()                // 触发更新
        }, delay)
      },
    }
  })
}
const keyword = debouncedRef('', 300)

// 7. markRaw：标记对象永不转为响应式（跳过代理）
const config = markRaw({ 
  immutableData: largeDataset  // 大数据集不需要响应式
})
const state2 = reactive({ config })  // config 不会被代理

---

## 四、自定义 Hooks（组合式函数封装）

**自定义 Hook**（Composition Function）是 Vue3 复用逻辑的官方推荐方式，相比 Vue2 的 mixin 更清晰、无命名冲突、类型安全。

**Hook 命名规范**：以 `use` 开头，如 `useMouse`、`useFetch`、`useLocalStorage`。

### 4.1 useEventListener：事件监听 Hook

```typescript
// src/composables/useEventListener.ts
import { onMounted, onUnmounted, type Ref } from 'vue'

/**
 * 事件监听 Hook
 * 自动在组件卸载时移除监听，无需手动清理
 * 
 * @param target  目标元素或 ref
 * @param event   事件名
 * @param callback 回调函数
 * @param options  addEventListener 选项
 * 
 * @example
 * // 监听 window 滚动
 * useEventListener(window, 'scroll', handleScroll)
 * // 监听某个 ref 元素点击
 * const btnRef = ref<HTMLElement>()
 * useEventListener(btnRef, 'click', () => {})
 */
export function useEventListener(
  target: Ref<EventTarget | null> | EventTarget,
  event: string,
  callback: EventListenerOrEventListenerObject,
  options: boolean | AddEventListenerOptions = false
) {
  onMounted(() => {
    const el = 'value' in (target as Ref) ? target.value : target
    el?.addEventListener(event, callback, options)
  })
  
  // 组件卸载时自动移除，避免内存泄漏
  onUnmounted(() => {
    const el = 'value' in (target as Ref) ? target.value : target
    el?.removeEventListener(event, callback, options)
  })
}
```

### 4.2 useMouse：鼠标位置 Hook

```typescript
// src/composables/useMouse.ts
import { ref } from 'vue'
import { useEventListener } from './useEventListener'

/**
 * 鼠标位置 Hook
 * 返回响应式的鼠标坐标，组件卸载自动清理
 * 
 * @returns { x, y } 鼠标坐标
 * 
 * @example
 * const { x, y } = useMouse()
 * // 模板中：{{ x }}, {{ y }}
 */
export function useMouse() {
  const x = ref(0)
  const y = ref(0)
  
  function update(event: MouseEvent) {
    x.value = event.pageX
    y.value = event.pageY
  }
  
  // 复用 useEventListener，自动管理生命周期
  useEventListener(window, 'mousemove', update)
  
  return { x, y }
}
```

**使用示例**：

```vue
<script setup lang="ts">
import { useMouse } from '@/composables/useMouse'

const { x, y } = useMouse()
</script>

<template>
  <div>鼠标位置：{{ x }}, {{ y }}</div>
</template>
```

### 4.3 useFetch：数据请求 Hook

```typescript
// src/composables/useFetch.ts
import { ref, watchEffect, type Ref } from 'vue'

interface UseFetchOptions<T> {
  immediate?: boolean              // 是否立即执行（默认 true）
  initialData?: T                  // 初始数据
  onSuccess?: (data: T) => void    // 成功回调
  onError?: (err: Error) => void   // 失败回调
}

interface UseFetchReturn<T> {
  data: Ref<T | null>
  loading: Ref<boolean>
  error: Ref<Error | null>
  execute: () => Promise<void>     // 手动触发
}

/**
 * 数据请求 Hook
 * 支持 URL 响应式变化自动重新请求
 * 
 * @param url 请求地址（可为 ref）
 * @param options 配置项
 * 
 * @example
 * const userId = ref(1)
 * const { data, loading, error } = useFetch(
 *   () => `/api/users/${userId.value}`
 * )
 */
export function useFetch<T = unknown>(
  url: string | (() => string),
  options: UseFetchOptions<T> = {}
): UseFetchReturn<T> {
  const { immediate = true, initialData, onSuccess, onError } = options
  
  const data = ref<T | null>(initialData ?? null) as Ref<T | null>
  const loading = ref(false)
  const error = ref<Error | null>(null)
  
  async function execute() {
    const urlStr = typeof url === 'function' ? url() : url
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch(urlStr)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      const json = await response.json()
      data.value = json
      onSuccess?.(json)
    } catch (e) {
      error.value = e as Error
      onError?.(e as Error)
    } finally {
      loading.value = false
    }
  }
  
  if (immediate) {
    // watchEffect 自动追踪 url 变化并重新请求
    watchEffect(() => {
      if (typeof url === 'function') {
        url()  // 触发依赖收集
      }
      execute()
    })
  }
  
  return { data, loading, error, execute }
}
```

**使用示例**：

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useFetch } from '@/composables/useFetch'

interface User {
  id: number
  name: string
  email: string
}

const userId = ref(1)

// URL 响应式：userId 变化自动重新请求
const { data: user, loading, error } = useFetch<User>(
  () => `/api/users/${userId.value}`,
  {
    onError: (err) => console.error('请求失败:', err.message),
  }
)

function nextUser() {
  userId.value++
}
</script>

<template>
  <div>
    <button @click="nextUser">下一个用户 ({{ userId }})</button>
    <div v-if="loading">加载中...</div>
    <div v-else-if="error">错误：{{ error.message }}</div>
    <div v-else-if="user">
      {{ user.name }} - {{ user.email }}
    </div>
  </div>
</template>
```

### 4.4 useLocalStorage：本地存储 Hook

```typescript
// src/composables/useLocalStorage.ts
import { ref, watch, type Ref } from 'vue'

/**
 * localStorage 响应式 Hook
 * 数据变化自动同步到 localStorage，刷新不丢失
 * 
 * @param key 存储键
 * @param defaultValue 默认值
 * 
 * @example
 * const theme = useLocalStorage('theme', 'light')
 * theme.value = 'dark'  // 自动同步到 localStorage
 */
export function useLocalStorage<T>(
  key: string,
  defaultValue: T
): Ref<T> {
  // 读取初始值
  const readValue = (): T => {
    try {
      const item = window.localStorage.getItem(key)
      return item ? (JSON.parse(item) as T) : defaultValue
    } catch {
      return defaultValue
    }
  }
  
  const stored = ref<T>(readValue()) as Ref<T>
  
  // 监听变化自动写入
  watch(
    stored,
    (newVal) => {
      try {
        window.localStorage.setItem(key, JSON.stringify(newVal))
      } catch (e) {
        console.error('localStorage 写入失败:', e)
      }
    },
    { deep: true }  // 对象深层变化也监听
  )
  
  return stored
}
```

**使用示例**：

```vue
<script setup lang="ts">
import { useLocalStorage } from '@/composables/useLocalStorage'

// 主题持久化
const theme = useLocalStorage<'light' | 'dark'>('app-theme', 'light')
// 购物车持久化
const cart = useLocalStorage<{ id: number; qty: number }[]>('cart', [])

function toggleTheme() {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
}
</script>

<template>
  <div :class="theme">
    <button @click="toggleTheme">切换主题（当前：{{ theme }}）</button>
  </div>
</template>
```

### 4.5 useDebounce：防抖 Hook

```typescript
// src/composables/useDebounce.ts
import { ref, watch, type Ref, onUnmounted } from 'vue'

/**
 * 防抖 ref Hook
 * 值变化后延迟更新，期间再次变化重新计时
 * 
 * @param source 响应式源
 * @param delay 延迟毫秒
 * 
 * @example
 * const keyword = ref('')
 * const debounced = useDebounce(keyword, 300)
 * // keyword 变化 300ms 后 debounced 才更新
 */
export function useDebounce<T>(source: Ref<T>, delay = 200): Ref<T> {
  const debounced = ref(source.value) as Ref<T>
  let timer: number | null = null
  
  watch(source, (newVal) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      debounced.value = newVal
    }, delay)
  })
  
  onUnmounted(() => {
    if (timer) clearTimeout(timer)
  })
  
  return debounced
}

/**
 * 防抖函数 Hook（用于函数防抖）
 */
export function useDebounceFn<T extends (...args: any[]) => any>(
  fn: T,
  delay = 200
): T {
  let timer: number | null = null
  
  const debounced = ((...args: Parameters<T>) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }) as T
  
  onUnmounted(() => {
    if (timer) clearTimeout(timer)
  })
  
  return debounced
}
```

### 4.6 usePagination：分页 Hook

```typescript
// src/composables/usePagination.ts
import { ref, computed, type Ref } from 'vue'

interface UsePaginationOptions {
  currentPage?: number    // 当前页（默认 1）
  pageSize?: number       // 每页条数（默认 10）
  total?: number          // 总数（默认 0）
}

interface UsePaginationReturn {
  currentPage: Ref<number>
  pageSize: Ref<number>
  total: Ref<number>
  totalPages: Ref<number>          // 总页数（计算属性）
  hasNext: Ref<boolean>            // 是否有下一页
  hasPrev: Ref<boolean>            // 是否有上一页
  nextPage: () => void             // 下一页
  prevPage: () => void             // 上一页
  goToPage: (page: number) => void // 跳转到指定页
  setTotal: (total: number) => void
}

/**
 * 分页 Hook
 * 封装分页逻辑，与表格组件配合使用
 * 
 * @example
 * const { currentPage, pageSize, totalPages, nextPage } = usePagination({
 *   total: 100,
 *   onChange: (page) => fetchData(page)
 * })
 */
export function usePagination(
  options: UsePaginationOptions & {
    onChange?: (page: number, size: number) => void
  } = {}
): UsePaginationReturn {
  const currentPage = ref(options.currentPage ?? 1)
  const pageSize = ref(options.pageSize ?? 10)
  const total = ref(options.total ?? 0)
  
  const totalPages = computed(() =>
    Math.ceil(total.value / pageSize.value)
  )
  
  const hasNext = computed(() => currentPage.value < totalPages.value)
  const hasPrev = computed(() => currentPage.value > 1)
  
  function nextPage() {
    if (hasNext.value) {
      currentPage.value++
      options.onChange?.(currentPage.value, pageSize.value)
    }
  }
  
  function prevPage() {
    if (hasPrev.value) {
      currentPage.value--
      options.onChange?.(currentPage.value, pageSize.value)
    }
  }
  
  function goToPage(page: number) {
    const clamped = Math.max(1, Math.min(page, totalPages.value))
    if (clamped !== currentPage.value) {
      currentPage.value = clamped
      options.onChange?.(currentPage.value, pageSize.value)
    }
  }
  
  function setTotal(t: number) {
    total.value = t
    // 当前页超出范围时回到最后一页
    if (currentPage.value > totalPages.value && totalPages.value > 0) {
      currentPage.value = totalPages.value
    }
  }
  
  return {
    currentPage, pageSize, total, totalPages,
    hasNext, hasPrev, nextPage, prevPage, goToPage, setTotal,
  }
}
```

### 4.7 Hooks 统一导出

```typescript
// src/composables/index.ts
export { useEventListener } from './useEventListener'
export { useMouse } from './useMouse'
export { useFetch } from './useFetch'
export { useLocalStorage } from './useLocalStorage'
export { useDebounce, useDebounceFn } from './useDebounce'
export { usePagination } from './usePagination'
```

### 4.8 Hooks 演示页面

```vue
<!-- src/examples/HooksDemo.vue -->
<script setup lang="ts">
import { ref, watch } from 'vue'
import {
  useMouse, useFetch, useLocalStorage,
  useDebounce, useDebounceFn, usePagination,
} from '@/composables'

// 1. 鼠标位置
const { x, y } = useMouse()

// 2. 防抖搜索
const keyword = ref('')
const debouncedKeyword = useDebounce(keyword, 300)
watch(debouncedKeyword, (val) => {
  if (val) console.log('搜索:', val)
})

// 3. localStorage 持久化
const visitCount = useLocalStorage('visit-count', 0)
visitCount.value++

// 4. 防抖函数（按钮点击防抖）
const handleClick = useDebounceFn(() => {
  console.log('点击触发（防抖 500ms）')
}, 500)

// 5. 分页
const { currentPage, pageSize, totalPages, nextPage, prevPage } = usePagination({
  total: 100,
  onChange: (page) => console.log('请求第', page, '页'),
})
</script>

<template>
  <div class="demo">
    <h3>鼠标位置</h3>
    <p>x: {{ x }}, y: {{ y }}</p>
    
    <h3>防抖搜索</h3>
    <input v-model="keyword" placeholder="输入关键词..." />
    <p>实际搜索：{{ debouncedKeyword }}</p>
    
    <h3>localStorage 持久化</h3>
    <p>访问次数：{{ visitCount }}（刷新不丢失）</p>
    
    <h3>分页</h3>
    <p>第 {{ currentPage }} / {{ totalPages }} 页（每页 {{ pageSize }} 条）</p>
    <button @click="prevPage">上一页</button>
    <button @click="nextPage">下一页</button>
    
    <h3>防抖按钮</h3>
    <button @click="handleClick">快速点击我（500ms 防抖）</button>
  </div>
</template>
```

---

## 五、Teleport 组件

**Teleport** 是 Vue3 内置组件，可将组件内容"传送"到 DOM 树的其他位置（通常是 `body`），解决层级嵌套导致的样式/事件问题。

### 5.1 为什么需要 Teleport

**问题场景**：弹窗/通知在深层组件中，被父级 `overflow: hidden`、`z-index`、`transform` 等影响。

```
<div class="parent" style="overflow: hidden; transform: translateX(0)">
  <div class="child">
    <!-- 弹窗在这里渲染，会被 parent 的 overflow:hidden 裁剪 -->
    <div class="modal">...</div>
  </div>
</div>

<!-- 用 Teleport 传送到 body，脱离父级限制 -->
<Teleport to="body">
  <div class="modal">...</div>  <!-- 渲染在 body 下 -->
</Teleport>
```

### 5.2 基础用法

```vue
<!-- src/components/ModalDialog.vue -->
<script setup lang="ts">
interface Props {
  modelValue: boolean       // 控制显示
  title?: string
  to?: string               // 传送目标（默认 body）
}

const props = withDefaults(defineProps<Props>(), {
  title: '弹窗',
  to: 'body',
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'close'): void
}>()

function close() {
  emit('update:modelValue', false)
  emit('close')
}
</script>

<template>
  <!-- Teleport：将内容传送到 to 指定的元素 -->
  <Teleport :to="to">
    <Transition name="modal">
      <div v-if="modelValue" class="modal-overlay" @click.self="close">
        <div class="modal-container">
          <div class="modal-header">
            <h3>{{ title }}</h3>
            <button class="modal-close" @click="close">×</button>
          </div>
          <div class="modal-body">
            <!-- 插槽：使用方自定义内容 -->
            <slot></slot>
          </div>
          <div class="modal-footer">
            <slot name="footer">
              <button @click="close">关闭</button>
            </slot>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;                          /* top:0; right:0; bottom:0; left:0 */
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;                     /* 高层级，在最顶层 */
}
.modal-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  min-width: 400px;
  max-width: 90%;
}
/* Transition 动画 */
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.3s;
}
.modal-enter-from, .modal-leave-to {
  opacity: 0;
}
</style>
```

### 5.3 Teleport 演示页面

```vue
<!-- src/examples/TeleportDemo.vue -->
<script setup lang="ts">
import { ref } from 'vue'
import ModalDialog from '@/components/ModalDialog.vue'

const visible = ref(false)
const visible2 = ref(false)

function handleConfirm() {
  alert('确认提交')
  visible.value = false
}
</script>

<template>
  <div class="demo" style="overflow: hidden; transform: scale(1); position: relative; z-index: 1;">
    <h3>Teleport 演示</h3>
    <p>当前容器有 overflow: hidden，普通弹窗会被裁剪</p>
    
    <button @click="visible = true">打开弹窗（Teleport 到 body）</button>
    <button @click="visible2 = true">打开自定义底部弹窗</button>
    
    <!-- 弹窗内容会传送到 body，不受父级样式影响 -->
    <ModalDialog v-model="visible" title="用户协议">
      <p>请阅读以下协议内容...</p>
      <template #footer>
        <button @click="visible = false">取消</button>
        <button @click="handleConfirm">确认</button>
      </template>
    </ModalDialog>
    
    <!-- 传送到指定元素 -->
    <Teleport to="#notification-container">
      <div v-if="visible2" class="bottom-modal">
        <h4>底部弹窗</h4>
        <button @click="visible2 = false">关闭</button>
      </div>
    </Teleport>
  </div>
</template>
```

### 5.4 Teleport 的 disabled 属性

```vue
<script setup lang="ts">
import { ref } from 'vue'
const isMobile = ref(false)
</script>

<template>
  <!-- disabled：true 时在原位置渲染，false 时传送到 to -->
  <Teleport to="body" :disabled="isMobile">
    <div class="tooltip">
      <!-- 桌面端传送 body，移动端在原位置 -->
      提示内容
    </div>
  </Teleport>
</template>
```

### 5.5 多个 Teleport 挂载同一目标

```vue
<!-- 多个 Teleport 挂载 body，按渲染顺序堆叠 -->
<Teleport to="body">
  <div class="toast">Toast 1</div>
</Teleport>
<Teleport to="body">
  <div class="toast">Toast 2</div>
</Teleport>
<!-- body 下：Toast1 在前，Toast2 在后 -->
```

---

## 六、Suspense 与异步组件

**Suspense** 是 Vue3 内置组件，用于协调异步依赖（异步组件、async setup），在加载完成前展示 fallback 内容。

### 6.1 异步组件定义

**方式一：`defineAsyncComponent`**（推荐）

```typescript
// src/router/lazy.ts
import { defineAsyncComponent } from 'vue'

// 基础异步组件
const AsyncChart = defineAsyncComponent(() =>
  import('@/components/AsyncChart.vue')
)

// 带配置的异步组件（加载中/失败/超时）
const AsyncChartWithConfig = defineAsyncComponent({
  loader: () => import('@/components/AsyncChart.vue'),
  loadingComponent: LoadingSpinner,        // 加载中显示
  errorComponent: ErrorDisplay,            // 失败显示
  delay: 200,                              // 延迟 200ms 显示 loading（防闪烁）
  timeout: 10000,                          // 10 秒超时显示 error
})

export { AsyncChart, AsyncChartWithConfig }
```

**方式二：路由懒加载**（本质也是异步组件）

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('@/examples/ReactiveDemo.vue'),  // 懒加载
  },
  {
    path: '/chart',
    component: () => import('@/components/AsyncChart.vue'),
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
```

### 6.2 async setup（异步组件 setup）

```vue
<!-- src/components/AsyncChart.vue -->
<script setup lang="ts">
import { ref } from 'vue'

interface ChartData {
  labels: string[]
  values: number[]
}

// async setup：Suspense 会等待此函数 resolve
// 适用于需要预取数据的场景
const chartData = ref<ChartData>(await fetchChartData())

async function fetchChartData(): Promise<ChartData> {
  // 模拟异步请求
  const res = await fetch('/api/chart-data')
  return res.json()
}
</script>

<template>
  <div class="chart">
    <div v-for="(val, i) in chartData.values" :key="i" class="bar">
      <span>{{ chartData.labels[i] }}: {{ val }}</span>
    </div>
  </div>
</template>
```

> **注意**：`async setup` 必须配合 `<Suspense>` 使用，否则会报错。

### 6.3 Suspense 基础用法

```vue
<!-- src/examples/SuspenseDemo.vue -->
<script setup lang="ts">
import { defineAsyncComponent } from 'vue'

const LoadingSpinner = {
  template: '<div class="loading">加载中... ⏳</div>',
}

const ErrorDisplay = {
  template: '<div class="error">组件加载失败 ❌</div>',
}

// 异步加载图表组件
const AsyncChart = defineAsyncComponent({
  loader: () => import('@/components/AsyncChart.vue'),
  loadingComponent: LoadingSpinner,
  errorComponent: ErrorDisplay,
  delay: 200,
  timeout: 10000,
})
</script>

<template>
  <div class="demo">
    <h3>Suspense 演示</h3>
    
    <!-- Suspense 包裹异步组件 -->
    <Suspense>
      <!-- 默认插槽：异步组件 -->
      <template #default>
        <AsyncChart />
      </template>
      
      <!-- fallback 插槽：加载中显示 -->
      <template #fallback>
        <div class="loading">
          <div class="spinner"></div>
          <p>数据加载中，请稍候...</p>
        </div>
      </template>
    </Suspense>
  </div>
</template>

<style scoped>
.loading {
  text-align: center;
  padding: 40px;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
```

### 6.4 嵌套异步依赖

Suspense 会等待**所有嵌套的异步依赖**全部完成后才显示：

```vue
<template>
  <Suspense>
    <template #default>
      <!-- UserProfile 内部也有 async setup -->
      <UserProfile>
        <!-- UserPosts 也是异步组件 -->
        <UserPosts :user-id="userId" />
      </UserProfile>
    </template>
    
    <template #fallback>
      <!-- UserProfile 和 UserPosts 都加载完才消失 -->
      <div>加载用户资料和文章...</div>
    </template>
  </Suspense>
</template>
```

### 6.5 错误处理

```vue
<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue'
import AsyncChart from '@/components/AsyncChart.vue'

const error = ref<Error | null>(null)

// 捕获异步组件的错误
onErrorCaptured((err) => {
  error.value = err as Error
  console.error('异步组件错误:', err)
  return false  // 阻止错误向上传播
})
</script>

<template>
  <div v-if="error" class="error">
    <h3>出错了</h3>
    <p>{{ error.message }}</p>
    <button @click="error = null">重试</button>
  </div>
  
  <Suspense v-else>
    <template #default>
      <AsyncChart />
    </template>
    <template #fallback>
      <div class="loading">加载中...</div>
    </template>
  </Suspense>
</template>
```

### 6.6 Suspense 实际应用场景

| 场景 | 说明 |
| --- | --- |
| **路由页面懒加载** | 配合路由实现按需加载，显示 loading |
| **预取数据** | async setup 中请求接口，加载完再渲染 |
| **大组件延迟加载** | 图表/编辑器等重组件异步加载 |
| **多组件协调** | 等待多个异步组件全部就绪 |

---

## 七、依赖注入（Provide/Inject）

**Provide/Inject** 用于跨层级组件传递数据，避免 "prop 逐层透传"（prop drilling）问题。

### 7.1 prop drilling 问题

```
App（拥有 theme 数据）
  └─ Layout（不需要 theme，但要传给子）
       └─ Header（不需要 theme，但要传给子）
            └─ ThemeButton（需要 theme）

问题：theme 数据要经过 Layout、Header 两层"中转"，中间组件被迫接收并传递不关心的 prop
```

### 7.2 provide / inject 基础用法

```typescript
import { provide, inject, ref, type InjectionKey } from 'vue'

// ① 定义 InjectionKey（带类型）
const themeKey: InjectionKey<Ref<string>> = Symbol('theme')

// ② 祖先组件 provide
function provideTheme() {
  const theme = ref<'light' | 'dark'>('light')
  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
  }
  provide(themeKey, theme)            // 注入响应式数据
  return { theme, toggleTheme }
}

// ③ 后代组件 inject
function useTheme() {
  const theme = inject(themeKey, ref('light'))  // 第二个参数为默认值
  if (!theme) throw new Error('useTheme 必须在 provideTheme 后调用')
  return theme
}
```

```vue
<!-- 祖先组件：App.vue -->
<script setup lang="ts">
import { provide, ref, readonly } from 'vue'

// provide 数据（只读，防止后代误改）
const theme = ref<'light' | 'dark'>('light')

function toggleTheme() {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
}

// readonly：后代只能读不能改（修改必须通过提供的方法）
provide('theme', readonly(theme))
provide('toggleTheme', toggleTheme)
</script>

<template>
  <button @click="toggleTheme">切换主题</button>
  <Layout />
</template>
```

```vue
<!-- 后代组件：ThemeButton.vue（跨多层） -->
<script setup lang="ts">
import { inject, type Ref } from 'vue'

// inject 获取数据（带类型断言与默认值）
const theme = inject<Readonly<Ref<string>>>('theme', readonly(ref('light')))
const toggleTheme = inject<() => void>('toggleTheme', () => {})
</script>

<template>
  <button :class="`btn-${theme}`" @click="toggleTheme">
    当前主题：{{ theme }}
  </button>
</template>
```

### 7.3 类型安全的 Provide/Inject（推荐）

使用 `InjectionKey` 实现完整类型推导：

```typescript
// src/types/inject-keys.ts
import type { InjectionKey, Ref } from 'vue'

// 定义带类型的 key
export const userKey: InjectionKey<Ref<User | null>> = Symbol('user')
export const themeKey: InjectionKey<Ref<'light' | 'dark'>> = Symbol('theme')
export const loadingKey: InjectionKey<Ref<boolean>> = Symbol('loading')

interface User {
  id: number
  name: string
}
```

```typescript
// 祖先组件
import { provide } from 'vue'
import { userKey, themeKey } from '@/types/inject-keys'

const user = ref<User | null>(null)
const theme = ref<'light' | 'dark'>('light')

provide(userKey, user)      // ✅ 类型匹配 Ref<User | null>
provide(themeKey, theme)    // ✅ 类型匹配 Ref<'light' | 'dark'>
```

```typescript
// 后代组件
import { inject } from 'vue'
import { userKey, themeKey } from '@/types/inject-keys'

const user = inject(userKey)        // 自动推导为 Ref<User | null> | undefined
const theme = inject(themeKey, ref('light'))  // 提供默认值

if (user?.value) {
  console.log(user.value.name)      // ✅ 类型安全
}
```

### 7.4 封装为组合式函数

```typescript
// src/composables/useTheme.ts
import { inject, provide, ref, readonly, type Ref } from 'vue'
import { themeKey } from '@/types/inject-keys'

/**
 * 主题 Provider：在祖先组件调用
 * @example
 * // App.vue
 * const { theme, toggleTheme } = provideTheme()
 */
export function provideTheme() {
  const theme = ref<'light' | 'dark'>('light')
  
  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
  }
  
  // 注入只读数据 + 操作方法
  provide(themeKey, readonly(theme))
  provide('toggleTheme', toggleTheme)
  
  return { theme, toggleTheme }
}

/**
 * 主题 Consumer：在后代组件调用
 * @example
 * // DeepChild.vue
 * const { theme, toggleTheme } = useTheme()
 */
export function useTheme() {
  const theme = inject(themeKey, readonly(ref<'light' | 'dark'>('light')))
  const toggleTheme = inject<() => void>('toggleTheme', () => {})
  
  return { theme, toggleTheme }
}
```

### 7.5 Provide/Inject 演示页面

```vue
<!-- src/examples/ProvideInjectDemo.vue -->
<script setup lang="ts">
import { provideTheme } from '@/composables/useTheme'
import ChildLevel1 from './ChildLevel1.vue'

// 祖先组件 provide
const { theme, toggleTheme } = provideTheme()
</script>

<template>
  <div :class="`app ${theme}`">
    <h3>Provide/Inject 演示</h3>
    <p>当前主题：{{ theme }}</p>
    <button @click="toggleTheme">祖先组件切换</button>
    <hr />
    <ChildLevel1 />
  </div>
</template>
```

```vue
<!-- src/examples/ChildLevel1.vue（中间层，不需要 theme） -->
<script setup lang="ts">
import ChildLevel2 from './ChildLevel2.vue'
</script>

<template>
  <div>
    <h4>第一层（不关心 theme，也不传 prop）</h4>
    <ChildLevel2 />
  </div>
</template>
```

```vue
<!-- src/examples/ChildLevel2.vue（深层后代，直接 inject 使用） -->
<script setup lang="ts">
import { useTheme } from '@/composables/useTheme'

// 直接获取祖先的数据，无需 prop 中转
const { theme, toggleTheme } = useTheme()
</script>

<template>
  <div>
    <h4>第二层（直接 inject 获取 theme）</h4>
    <p>主题：{{ theme }}</p>
    <button @click="toggleTheme">后代组件切换</button>
  </div>
</template>
```

### 7.6 Provide/Inject 最佳实践

| 实践 | 说明 |
| --- | --- |
| **用 InjectionKey** | 提供完整类型推导，避免 any |
| **readonly 包裹** | 防止后代误改，修改必须通过方法 |
| **封装为 composable** | provideXxx + useXxx 配对使用 |
| **提供默认值** | inject 第二参数，避免 undefined |
| **响应式数据** | provide ref/reactive，保持响应性 |

---

## 八、自定义指令

**自定义指令**用于封装对底层 DOM 的访问逻辑，在元素上以 `v-xxx` 形式使用。

### 8.1 指令钩子函数

```typescript
import type { Directive, DirectiveBinding } from 'vue'

const myDirective: Directive<HTMLElement, string> = {
  // 元素挂载前
  created(el, binding, vnode) {
    console.log('created', binding.value)
  },
  // 挂载前（DOM 还未插入）
  beforeMount(el, binding) {
    console.log('beforeMount')
  },
  // 挂载后（DOM 已插入）★ 最常用
  mounted(el, binding) {
    console.log('mounted', el, binding.value)
  },
  // 更新前
  beforeUpdate(el, binding) {
    console.log('beforeUpdate')
  },
  // 更新后
  updated(el, binding) {
    console.log('updated')
  },
  // 卸载前
  beforeUnmount(el, binding) {
    console.log('beforeUnmount')
  },
  // 卸载后 ★ 常用于清理
  unmounted(el, binding) {
    console.log('unmounted')
  },
}
```

**钩子参数**：

```typescript
interface DirectiveBinding<T = any> {
  value: T            // 指令绑定值：v-my="1" → 1
  oldValue: T         // 旧值（update 时有）
  arg: string         // 参数：v-my:foo → 'foo'
  modifiers: object   // 修饰符：v-my.bar → { bar: true }
  dir: Directive      // 指令对象本身
  instance: Component // 组件实例
}
```

### 8.2 v-permission：权限控制指令

```typescript
// src/directives/permission.ts
import type { Directive } from 'vue'
import { useUserStore } from '@/stores/user'

/**
 * 权限控制指令
 * 根据用户角色控制元素显示
 * 
 * @example
 * <button v-permission="'admin'">仅管理员可见</button>
 * <div v-permission="['admin', 'editor']">管理员或编辑可见</div>
 */
export const permission: Directive<HTMLElement, string | string[]> = {
  mounted(el, binding) {
    const userStore = useUserStore()
    const requiredRoles = binding.value
    const roles = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles]
    
    // 用户角色不包含所需角色，移除元素
    const hasPermission = roles.some(role => userStore.roles.includes(role))
    if (!hasPermission) {
      el.parentNode?.removeChild(el)
    }
  },
}
```

### 8.3 v-debounce：防抖指令

```typescript
// src/directives/debounce.ts
import type { Directive } from 'vue'

/**
 * 防抖指令
 * 对点击事件防抖，避免重复提交
 * 
 * @example
 * <button v-debounce:500="handleClick">防抖按钮</button>
 * <button v-debounce:1000.immediate="handleClick">立即执行+防抖</button>
 */
export const debounce: Directive<HTMLElement, () => void> = {
  mounted(el, binding) {
    const handler = binding.value
    const delay = Number(binding.arg) || 300                // 参数为延迟毫秒
    const immediate = binding.modifiers.immediate           // 修饰符：是否立即执行
    
    let timer: number | null = null
    
    el.addEventListener('click', () => {
      if (timer) clearTimeout(timer)
      
      if (immediate && !timer) {
        handler()                                            // 立即执行一次
      }
      
      timer = setTimeout(() => {
        if (!immediate) handler()
        timer = null
      }, delay)
    })
  },
  unmounted(el) {
    // 清理：可在此移除事件监听（实际应保存引用）
  },
}
```

### 8.4 v-lazy：图片懒加载指令

```typescript
// src/directives/lazy.ts
import type { Directive } from 'vue'

/**
 * 图片懒加载指令
 * 使用 IntersectionObserver，进入视口才加载
 * 
 * @example
 * <img v-lazy="/path/to/image.jpg" />
 * <img v-lazy="imgUrl" alt="图片" />
 */
export const lazy: Directive<HTMLImageElement, string> = {
  mounted(el, binding) {
    const src = binding.value
    
    // 占位图
    el.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"/>'
    
    // 创建观察器
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            // 进入视口，加载真实图片
            el.src = src
            // 加载完成后停止观察
            observer.unobserve(el)
          }
        })
      },
      { rootMargin: '50px' }  // 提前 50px 加载
    )
    
    observer.observe(el)
    
    // 保存观察器引用，卸载时清理
    ;(el as any)._lazyObserver = observer
  },
  unmounted(el) {
    // 清理观察器，避免内存泄漏
    ;(el as any)._lazyObserver?.disconnect()
  },
}
```

### 8.5 v-draggable：拖拽指令

```typescript
// src/directives/draggable.ts
import type { Directive } from 'vue'

/**
 * 拖拽指令
 * 让元素可拖拽移动
 * 
 * @example
 * <div v-draggable>拖拽我</div>
 */
export const draggable: Directive<HTMLElement> = {
  mounted(el) {
    el.style.cursor = 'move'
    el.style.userSelect = 'none'
    el.style.position = 'absolute'
    
    let isDragging = false
    let startX = 0
    let startY = 0
    let initialLeft = 0
    let initialTop = 0
    
    function handleMouseDown(e: MouseEvent) {
      isDragging = true
      startX = e.clientX
      startY = e.clientY
      const rect = el.getBoundingClientRect()
      initialLeft = rect.left
      initialTop = rect.top
      
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      e.preventDefault()
    }
    
    function handleMouseMove(e: MouseEvent) {
      if (!isDragging) return
      const deltaX = e.clientX - startX
      const deltaY = e.clientY - startY
      el.style.left = `${initialLeft + deltaX}px`
      el.style.top = `${initialTop + deltaY}px`
    }
    
    function handleMouseUp() {
      isDragging = false
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
    
    el.addEventListener('mousedown', handleMouseDown)
    
    // 保存引用便于清理
    ;(el as any)._dragHandler = handleMouseDown
  },
  unmounted(el) {
    el.removeEventListener('mousedown', (el as any)._dragHandler)
  },
}
```

### 8.6 v-copy：复制指令

```typescript
// src/directives/copy.ts
import type { Directive } from 'vue'

/**
 * 复制到剪贴板指令
 * 点击元素复制文本
 * 
 * @example
 * <button v-copy="textToCopy">点击复制</button>
 */
export const copy: Directive<HTMLElement, string> = {
  mounted(el, binding) {
    el.style.cursor = 'pointer'
    
    function handleClick() {
      const text = binding.value
      // 使用 Clipboard API
      navigator.clipboard.writeText(text).then(() => {
        // 复制成功提示（可用 ElMessage）
        console.log('已复制：', text)
        const original = el.textContent
        el.textContent = '✓ 已复制'
        setTimeout(() => {
          el.textContent = original
        }, 1500)
      }).catch(() => {
        // 降级方案
        const textarea = document.createElement('textarea')
        textarea.value = text
        document.body.appendChild(textarea)
        textarea.select()
        document.execCommand('copy')
        document.body.removeChild(textarea)
      })
    }
    
    el.addEventListener('click', handleClick)
    ;(el as any)._copyHandler = handleClick
  },
  updated(el, binding) {
    // 值变化时更新（无需重新绑定事件）
  },
  unmounted(el) {
    el.removeEventListener('click', (el as any)._copyHandler)
  },
}
```

### 8.7 指令统一注册

```typescript
// src/directives/index.ts
import type { App } from 'vue'
import { permission } from './permission'
import { debounce } from './debounce'
import { lazy } from './lazy'
import { draggable } from './draggable'
import { copy } from './copy'

/**
 * 全局注册自定义指令
 */
export function setupDirectives(app: App) {
  app.directive('permission', permission)
  app.directive('debounce', debounce)
  app.directive('lazy', lazy)
  app.directive('draggable', draggable)
  app.directive('copy', copy)
}
```

```typescript
// src/main.ts
import { createApp } from 'vue'
import App from './App.vue'
import { setupDirectives } from './directives'

const app = createApp(App)
setupDirectives(app)          // 注册全局指令
app.mount('#app')
```

### 8.8 自定义指令演示页面

```vue
<!-- src/examples/DirectivesDemo.vue -->
<script setup lang="ts">
import { ref } from 'vue'

const copyText = ref('这是要复制的文本')
const images = ref([
  '/img/1.jpg', '/img/2.jpg', '/img/3.jpg', '/img/4.jpg',
  '/img/5.jpg', '/img/6.jpg', '/img/7.jpg', '/img/8.jpg',
])

function handleClick() {
  console.log('按钮点击（已防抖）')
}
</script>

<template>
  <div class="demo">
    <h3>自定义指令演示</h3>
    
    <!-- v-permission：权限控制 -->
    <h4>v-permission 权限控制</h4>
    <button v-permission="'admin'">仅管理员可见</button>
    <button v-permission="['admin', 'editor']">管理员或编辑可见</button>
    
    <!-- v-debounce：防抖 -->
    <h4>v-debounce 防抖（500ms）</h4>
    <button v-debounce:500="handleClick">防抖按钮（500ms）</button>
    <button v-debounce:1000.immediate="handleClick">立即执行+防抖</button>
    
    <!-- v-lazy：图片懒加载 -->
    <h4>v-lazy 图片懒加载</h4>
    <div class="image-list">
      <img v-for="(src, i) in images" :key="i" v-lazy="src" 
           style="width:200px;height:150px;margin:5px;" />
    </div>
    
    <!-- v-draggable：拖拽 -->
    <h4>v-draggable 拖拽</h4>
    <div v-draggable style="width:100px;height:100px;background:#409eff;color:#fff;
         display:flex;align-items:center;justify-content:center;">
      拖拽我
    </div>
    
    <!-- v-copy：复制 -->
    <h4>v-copy 复制到剪贴板</h4>
    <input v-model="copyText" placeholder="输入要复制的文本" />
    <button v-copy="copyText">点击复制</button>
  </div>
</template>
```

---

## 九、使用指南与最佳实践

### 9.1 项目初始化

```bash
# 1. 创建 Vite + Vue3 + TS 项目
pnpm create vite vue3-advanced-practice --template vue-ts
cd vue3-advanced-practice

# 2. 安装依赖
pnpm install

# 3. 安装 ESLint + Prettier
pnpm add -D eslint eslint-plugin-vue @vue/eslint-config-typescript \
  @vue/eslint-config-prettier prettier

# 4. 安装 Vue Router
pnpm add vue-router

# 5. 启动开发
pnpm dev
```

### 9.2 main.ts 完整配置

```typescript
// src/main.ts
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { setupDirectives } from './directives'

const app = createApp(App)

app.use(router)             // 注册路由
setupDirectives(app)        // 注册自定义指令

// 全局错误处理
app.config.errorHandler = (err, instance, info) => {
  console.error('全局错误:', err, info)
}

app.mount('#app')
```

### 9.3 App.vue 与路由配置

```vue
<!-- src/App.vue -->
<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { provideTheme } from '@/composables/useTheme'

// 提供 theme 给后代组件
const { theme, toggleTheme } = provideTheme()
</script>

<template>
  <div :class="`app ${theme}`">
    <nav>
      <RouterLink to="/">响应式</RouterLink> |
      <RouterLink to="/computed">计算属性</RouterLink> |
      <RouterLink to="/hooks">Hooks</RouterLink> |
      <RouterLink to="/teleport">Teleport</RouterLink> |
      <RouterLink to="/suspense">Suspense</RouterLink> |
      <RouterLink to="/provide">Provide/Inject</RouterLink> |
      <RouterLink to="/directives">自定义指令</RouterLink>
    </nav>
    <button @click="toggleTheme">切换主题</button>
    <RouterView />
  </div>
</template>
```

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/',           component: () => import('@/examples/ReactiveDemo.vue') },
  { path: '/computed',   component: () => import('@/examples/ComputedDemo.vue') },
  { path: '/hooks',      component: () => import('@/examples/HooksDemo.vue') },
  { path: '/teleport',   component: () => import('@/examples/TeleportDemo.vue') },
  { path: '/suspense',   component: () => import('@/examples/SuspenseDemo.vue') },
  { path: '/provide',    component: () => import('@/examples/ProvideInjectDemo.vue') },
  { path: '/directives', component: () => import('@/examples/DirectivesDemo.vue') },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
```

### 9.4 最佳实践总结

| 特性 | 最佳实践 |
| --- | --- |
| **`<script setup>`** | 始终使用，替代 setup 函数 |
| **响应式选择** | 对象用 reactive，基本类型/需替换用 ref |
| **解构 reactive** | 用 toRefs 保持响应性 |
| **computed** | 用于派生状态，避免模板中复杂计算 |
| **watch** | 需要新旧值对比时用 watch，仅副作用用 watchEffect |
| **自定义 Hooks** | `use` 前缀，返回 ref/只读数据，封装生命周期清理 |
| **Teleport** | 弹窗/通知/tooltip 传送到 body，脱离父级样式 |
| **Suspense** | 配合异步组件/async setup，提供 loading 体验 |
| **Provide/Inject** | 用 InjectionKey 类型安全 + readonly 防误改 |
| **自定义指令** | 仅用于 DOM 操作，业务逻辑用组件/Hooks |
| **TypeScript** | interface 定义类型，避免 any，开启 strict |
| **清理副作用** | onUnmounted 中清理定时器/事件/观察器 |

### 9.5 性能优化要点

```typescript
// 1. shallowRef/shallowReactive：大对象只关心第一层变化
const bigList = shallowRef<Item[]>([])  // 替换整体才触发更新

// 2. markRaw：跳过响应式代理（不可变大数据）
const staticData = markRaw(largeDataset)

// 3. v-once：只渲染一次（静态内容）
// <div v-once>{{ computedExpensive }}</div>

// 4. v-memo：依赖不变则跳过更新
// <div v-memo="[item.id, item.selected]">...</div>

// 5. 异步组件懒加载
const HeavyComp = defineAsyncComponent(() => import('./Heavy.vue'))

// 6. keep-alive 缓存组件
// <router-view v-slot="{ Component }">
//   <keep-alive :include="['UserList']">
//     <component :is="Component" />
//   </keep-alive>
// </router-view>
```

### 9.6 调试技巧

```typescript
// 1. Vue Devtools：安装浏览器插件，查看组件树/状态/事件

// 2. 响应式调试：watch 监听某个值的变化
watch(someRef, (newVal, oldVal) => {
  console.trace('变化追踪:', oldVal, '→', newVal)
}, { deep: true })

// 3. 打印当前依赖：getDebugScope（Vue 内部 API）
import { getCurrentScope } from 'vue'
console.log('当前作用域:', getCurrentScope())

// 4. 性能分析
import { performance } from 'perf_hooks'
const start = performance.now()
// ...执行代码
console.log('耗时:', performance.now() - start, 'ms')
```

---

## 附录 完整示例索引

| 章节 | 特性 | 代码示例 |
| --- | --- | --- |
| 二 | `<script setup>` | defineProps/defineEmits/defineExpose |
| 二 | 生命周期 | onMounted/onUnmounted/onErrorCaptured |
| 三 | reactive/ref | 表单状态管理 |
| 三 | computed | 购物车计算（总数/总价/折扣/格式化） |
| 三 | watch/watchEffect | 搜索防抖 |
| 三 | 工具函数 | toRefs/customRef/markRaw |
| 四 | useEventListener | 事件监听自动清理 |
| 四 | useMouse | 鼠标位置追踪 |
| 四 | useFetch | 数据请求 + URL 响应式 |
| 四 | useLocalStorage | 本地存储持久化 |
| 四 | useDebounce | 防抖 ref + 防抖函数 |
| 四 | usePagination | 分页逻辑封装 |
| 五 | Teleport | ModalDialog 弹窗组件 |
| 六 | Suspense | 异步组件 + async setup |
| 七 | Provide/Inject | 主题跨层传递（类型安全） |
| 八 | v-permission | 权限控制 |
| 八 | v-debounce | 防抖指令 |
| 八 | v-lazy | 图片懒加载 |
| 八 | v-draggable | 拖拽指令 |
| 八 | v-copy | 复制到剪贴板 |

---

## 参考资料

- Vue3 官方文档：https://cn.vuejs.org/
- Composition API：https://cn.vuejs.org/guide/extras/composition-api-faq.html
- Vue3 响应式：https://cn.vuejs.org/guide/extras/reactivity-in-depth.html
- Teleport：https://cn.vuejs.org/guide/built-ins/teleport.html
- Suspense：https://cn.vuejs.org/guide/built-ins/suspense.html
- 自定义指令：https://cn.vuejs.org/guide/reusability/custom-directives.html

---

> **文档说明**：本文档共 9 大章节，系统覆盖 Vue3 核心高级特性（组合式 API、响应式系统、自定义 Hooks、Teleport、Suspense、Provide/Inject、自定义指令）。每个特性均提供完整 TypeScript 代码示例、详细注释与应用场景演示，可直接复制到项目中使用。建议按章节顺序学习，配合实际项目实践加深理解。

