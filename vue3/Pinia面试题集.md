# Pinia 面试题集

> 本文档整理了 Pinia 状态管理库相关的面试题，涵盖基础概念、工作原理、使用方法、与 Vuex 对比、高级特性及最佳实践等方面。题目按难度分为基础、中级、高级三个等级，并按知识点分类组织，便于系统学习和查阅。

## 目录

1. [基础概念](#一基础概念)
   - [什么是 Pinia](#1-什么是-pinia)
   - [核心概念](#2-核心概念)
   - [安装与使用](#3-安装与使用)
2. [Store 定义与使用](#二store-定义与使用)
   - [定义 Store](#1-定义-store)
   - [State 状态管理](#2-state-状态管理)
   - [Getters 计算属性](#3-getters-计算属性)
   - [Actions 方法](#4-actions-方法)
3. [工作原理](#三工作原理)
   - [响应式原理](#1-响应式原理)
   - [Store 注册机制](#2-store-注册机制)
   - [依赖收集与更新](#3-依赖收集与更新)
4. [Pinia 与 Vuex 对比](#四pinia-与-vuex-对比)
   - [核心差异](#1-核心差异)
   - [迁移指南](#2-迁移指南)
5. [高级特性](#五高级特性)
   - [Store 相互调用](#1-store-相互调用)
   - [组合式 Store](#2-组合式-store)
   - [持久化存储](#3-持久化存储)
   - [插件机制](#4-插件机制)
   - [SSR 支持](#5-ssr-支持)
6. [TypeScript 集成](#六typescript-集成)
   - [类型推导](#1-类型推导)
   - [类型标注](#2-类型标注)
7. [测试与调试](#七测试与调试)
   - [单元测试](#1-单元测试)
   - [调试技巧](#2-调试技巧)
8. [最佳实践](#八最佳实践)
   - [项目结构](#1-项目结构)
   - [性能优化](#2-性能优化)
   - [常见陷阱](#3-常见陷阱)
9. [实战场景](#九实战场景)
   - [复杂业务场景](#1-复杂业务场景)
   - [与组合式 API 配合](#2-与组合式-api-配合)

---

## 一、基础概念

### 1. 什么是 Pinia

#### 【基础】题目 1：简述 Pinia 是什么，以及它的主要特点

**答案：**

Pinia 是 Vue.js 的官方状态管理库，由 Vue 核心团队成员 Eduardo San Martin Morote 开发，是 Vuex 的继任者，已成为 Vue3 官方推荐的状态管理方案。

**主要特点：**

- **更简洁的 API**：移除了 Vuex 中的 mutations，直接在 actions 中修改状态
- **完整的 TypeScript 支持**：提供完善的类型推导，无需额外定义类型
- **非常轻量**：压缩后约 1KB
- **模块化设计**：每个 store 独立存在，无需嵌套模块
- **支持组合式 API**：可直接使用 `computed`、`ref` 等 API
- **支持 DevTools**：集成 Vue DevTools，方便调试
- **支持 SSR**：提供服务端渲染支持
- **支持插件扩展**：可自定义插件扩展功能

```javascript
// 基本使用示例
import { createPinia, defineStore } from 'pinia'

const pinia = createPinia()
app.use(pinia)

const useCounterStore = defineStore('counter', {
  state: () => ({ count: 0 }),
  getters: {
    double: (state) => state.count * 2
  },
  actions: {
    increment() {
      this.count++
    }
  }
})
```

---

#### 【基础】题目 2：Pinia 与 Vuex 有什么本质区别？

**答案：**

| 特性 | Vuex | Pinia |
|------|------|-------|
| **mutations** | 必须通过 mutations 修改状态 | 移除 mutations，直接修改 |
| **模块化** | 通过 modules 嵌套 | 每个 store 独立平行 |
| **TypeScript** | 支持较差，需大量类型声明 | 原生支持，类型自动推导 |
| **API 风格** | Options API 为主 | Options 和 Composition 均支持 |
| **体积** | 较大 | 轻量（约 1KB） |
| **嵌套模块** | 支持嵌套 | 不支持嵌套，但可相互调用 |
| **调试工具** | 支持 DevTools | 支持 DevTools，体验更好 |
| **学习成本** | 较高 | 较低 |
| **自动补全** | 较弱 | 完整的自动补全 |

**核心区别示例：**

```javascript
// Vuex 方式
const store = {
  state: { count: 0 },
  mutations: {
    INCREMENT(state) { state.count++ }
  },
  actions: {
    increment({ commit }) { commit('INCREMENT') }
  }
}

// Pinia 方式（更简洁）
const useStore = defineStore('main', {
  state: () => ({ count: 0 }),
  actions: {
    increment() { this.count++ }  // 直接修改，无需 mutations
  }
})
```

---

### 2. 核心概念

#### 【基础】题目 3：Pinia 的核心概念有哪些？

**答案：**

Pinia 有三个核心概念：

**1. State（状态）**
- 存储 应用级别的数据
- 通常是响应式数据
- 通过 `state` 选项定义

**2. Getters（计算属性）**
- 类似组件中的 `computed`
- 基于 state 派生新数据
- 具有缓存特性

**3. Actions（方法）**
- 定义业务逻辑
- 可以是同步或异步
- 通过 `this` 访问和修改 state

```javascript
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  // State：定义状态
  state: () => ({
    users: [],
    currentUser: null
  }),

  // Getters：计算属性
  getters: {
    userCount: (state) => state.users.length,
    isAdmin: (state) => state.currentUser?.role === 'admin'
  },

  // Actions：方法
  actions: {
    async fetchUsers() {
      const response = await fetch('/api/users')
      this.users = await response.json()
    },
    setUser(user) {
      this.currentUser = user
    }
  }
})
```

---

### 3. 安装与使用

#### 【基础】题目 4：如何在 Vue3 项目中安装和使用 Pinia？

**答案：**

**安装：**

```bash
# 使用 npm
npm install pinia

# 使用 yarn
yarn add pinia

# 使用 pnpm
pnpm add pinia
```

**使用步骤：**

```javascript
// main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const app = createApp(App)

// 创建并挂载 Pinia 实例
const pinia = createPinia()
app.use(pinia)

app.mount('#app')
```

**定义和使用 Store：**

```javascript
// stores/counter.js
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', {
  state: () => ({
    count: 0
  }),
  actions: {
    increment() {
      this.count++
    }
  }
})

// 在组件中使用
import { useCounterStore } from '@/stores/counter'

export default {
  setup() {
    const counter = useCounterStore()
    
    return {
      counter,
      increment: counter.increment
    }
  }
}
```

---

## 二、Store 定义与使用

### 1. 定义 Store

#### 【中级】题目 1：Pinia 定义 Store 有哪两种方式？各自的特点是什么？

**答案：**

Pinia 提供两种定义 Store 的方式：Options Store 和 Setup Store。

**1. Options Store（选项式）**

```javascript
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', {
  state: () => ({
    count: 0,
    name: 'Eduardo'
  }),
  getters: {
    doubleCount: (state) => state.count * 2,
    doubleCountPlusOne() {
      return this.doubleCount + 1
    }
  },
  actions: {
    increment() {
      this.count++
    },
    async fetchCount() {
      const res = await fetch('/api/count')
      this.count = await res.json()
    }
  }
})
```

**2. Setup Store（组合式）**

```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCounterStore = defineStore('counter', () => {
  // state - 相当于 state
  const count = ref(0)
  const name = ref('Eduardo')

  // getter - 相当于 getters
  const doubleCount = computed(() => count.value * 2)
  const doubleCountPlusOne = computed(() => doubleCount.value + 1)

  // function - 相当于 actions
  function increment() {
    count.value++
  }

  async function fetchCount() {
    const res = await fetch('/api/count')
    count.value = await res.json()
  }

  return { count, name, doubleCount, doubleCountPlusOne, increment, fetchCount }
})
```

**对比：**

| 特性 | Options Store | Setup Store |
|------|---------------|-------------|
| **API 风格** | Options API | Composition API |
| **状态定义** | `state` 选项 | `ref()` / `reactive()` |
| **计算属性** | `getters` 选项 | `computed()` |
| **方法定义** | `actions` 选项 | 普通函数 |
| **灵活性** | 结构固定 | 更灵活，可使用任何组合式 API |
| **适用场景** | 简单场景 | 复杂场景，需要更多 Vue API |

---

#### 【中级】题目 2：如何重命名 Store 和使用 `$reset` 方法？

**答案：**

**Store 命名：**

Store 的第一个参数是唯一的 ID，用于 DevTools 识别。

```javascript
// 带有 ID 的命名
export const useUserStore = defineStore('user', {
  // ...
})

// 也可以使用 symbol 作为 ID（不推荐，DevTools 中难以识别）
const USER_STORE = Symbol()
export const useUserStore = defineStore(USER_STORE, {
  // ...
})
```

**`$reset` 方法：**

重置 state 到初始状态（仅 Options Store 支持，Setup Store 需手动实现）。

```javascript
const useCounterStore = defineStore('counter', {
  state: () => ({
    count: 0,
    name: 'Eduardo'
  })
})

const counter = useCounterStore()
counter.count = 5
counter.name = 'John'

// 重置到初始状态
counter.$reset()

console.log(counter.count) // 0
console.log(counter.name)  // 'Eduardo'
```

**Setup Store 手动实现 `$reset`：**

```javascript
export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const name = ref('Eduardo')

  function $reset() {
    count.value = 0
    name.value = 'Eduardo'
  }

  return { count, name, $reset }
})
```

---

### 2. State 状态管理

#### 【中级】题目 3：如何修改 Pinia Store 中的 State？有哪些方式？

**答案：**

Pinia 提供多种修改 state 的方式：

**1. 直接修改**

```javascript
const counter = useCounterStore()
counter.count++
counter.count = 10
```

**2. 通过 `$patch` 修改（推荐批量修改）**

```javascript
// 对象方式
counter.$patch({
  count: 10,
  name: 'John'
})

// 函数方式（适合复杂修改）
counter.$patch((state) => {
  state.count = 10
  state.name = 'John'
  state.list.push('new item')
})
```

**3. 通过 action 修改**

```javascript
const counter = useCounterStore()
counter.increment()
counter.$patch({ count: 10 })  // 也可以在 action 内调用
```

**4. 替换整个 state**

```javascript
counter.$state = { count: 10, name: 'John' }
```

**5. 重置 state**

```javascript
counter.$reset()
```

**对比：**

| 方式 | 适用场景 | 性能 | 推荐度 |
|------|----------|------|--------|
| 直接修改 | 简单修改 | 一般 | ⭐⭐⭐ |
| `$patch` | 批量修改 | 较好 | ⭐⭐⭐⭐⭐ |
| action | 业务逻辑 | 一般 | ⭐⭐⭐⭐⭐ |
| `$state` | 整体替换 | 较差 | ⭐⭐ |

---

#### 【中级】题目 4：如何订阅 Pinia Store 的状态变化？

**答案：**

使用 `$subscribe` 方法订阅 state 变化：

```javascript
const counter = useCounterStore()

// 订阅 state 变化
counter.$subscribe((mutation, state) => {
  // mutation.type: 'direct' | 'patch object' | 'patch function'
  // mutation.storeId: store 的 ID
  // state: 新的 state
  
  console.log('mutation type:', mutation.type)
  console.log('store id:', mutation.storeId)
  console.log('new state:', state)
})

// 订阅 getters 变化
counter.$onAction(({ name, store, args, after, onError }) => {
  const startTime = Date.now()
  
  console.log(`Action ${name} started with args:`, args)
  
  after((result) => {
    console.log(`Action ${name} finished in ${Date.now() - startTime}ms`)
    console.log('Result:', result)
  })
  
  onError((error) => {
    console.error(`Action ${name} failed:`, error)
  })
})
```

**组件内自动清理订阅：**

```javascript
import { onUnmounted } from 'vue'
import { useCounterStore } from '@/stores/counter'

export default {
  setup() {
    const counter = useCounterStore()
    
    // 组件卸载时自动清理
    const unsubscribe = counter.$subscribe((mutation, state) => {
      console.log('state changed:', state)
    })
    
    onUnmounted(() => {
      unsubscribe()
    })
  }
}
```

**全局订阅：**

```javascript
// 在 main.js 中全局订阅
import { createPinia } from 'pinia'

const pinia = createPinia()

pinia.use(({ store }) => {
  store.$subscribe((mutation, state) => {
    console.log(`Store ${mutation.storeId} changed:`, state)
  })
})
```

---

### 3. Getters 计算属性

#### 【中级】题目 5：Pinia 的 Getters 如何使用？如何访问其他 Store 的 Getter？

**答案：**

**基本使用：**

```javascript
export const useCounterStore = defineStore('counter', {
  state: () => ({
    count: 0,
    items: [1, 2, 3, 4, 5]
  }),
  getters: {
    // 简单 getter
    doubleCount: (state) => state.count * 2,
    
    // 访问其他 getter
    doubleCountPlusOne() {
      return this.doubleCount + 1
    },
    
    // 带参数的 getter（返回函数）
    getItemByIndex: (state) => {
      return (index) => state.items[index]
    },
    
    // 使用其他 store
    userCount() {
      const userStore = useUserStore()
      return userStore.users.length
    }
  }
})
```

**Setup Store 中的 getter：**

```javascript
export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const items = ref([1, 2, 3, 4, 5])
  
  // 普通 computed
  const doubleCount = computed(() => count.value * 2)
  
  // 带参数的 getter
  const getItemByIndex = (index) => computed(() => items.value[index])
  
  // 访问其他 store
  const userCount = computed(() => {
    const userStore = useUserStore()
    return userStore.users.length
  })
  
  return { count, doubleCount, getItemByIndex, userCount }
})
```

**在组件中使用：**

```vue
<template>
  <div>
    <p>Double: {{ counter.doubleCount }}</p>
    <p>Item: {{ counter.getItemByIndex(2) }}</p>
    <p>User Count: {{ counter.userCount }}</p>
  </div>
</template>

<script setup>
import { useCounterStore } from '@/stores/counter'
const counter = useCounterStore()
</script>
```

---

### 4. Actions 方法

#### 【中级】题目 6：Pinia 的 Actions 如何处理异步操作？如何组合多个 Action？

**答案：**

**异步 Action：**

```javascript
export const useUserStore = defineStore('user', {
  state: () => ({
    users: [],
    loading: false,
    error: null
  }),
  
  actions: {
    async fetchUsers() {
      this.loading = true
      this.error = null
      try {
        const response = await fetch('/api/users')
        if (!response.ok) throw new Error('Failed to fetch')
        this.users = await response.json()
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    
    async getUserById(id) {
      const response = await fetch(`/api/users/${id}`)
      return await response.json()
    }
  }
})
```

**组合多个 Action：**

```javascript
export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [],
    total: 0
  }),
  
  actions: {
    async addToCart(productId, quantity) {
      // 调用其他 store 的 action
      const productStore = useProductStore()
      const userStore = useUserStore()
      
      // 检查库存
      const product = await productStore.getProduct(productId)
      if (product.stock < quantity) {
        throw new Error('Insufficient stock')
      }
      
      // 检查用户权限
      if (!userStore.isLoggedIn) {
        throw new Error('Please login first')
      }
      
      // 添加到购物车
      this.items.push({ product, quantity })
      this.calculateTotal()
    },
    
    calculateTotal() {
      this.total = this.items.reduce((sum, item) => {
        return sum + item.product.price * item.quantity
      }, 0)
    }
  }
})
```

**`$onAction` 订阅：**

```javascript
const cartStore = useCartStore()

// 订阅 action 调用
cartStore.$onAction(({ name, store, args, after, onError }) => {
  console.log(`[${name}] called with args:`, args)
  
  after((result) => {
    console.log(`[${name}] completed with result:`, result)
  })
  
  onError((error) => {
    console.error(`[${name}] failed:`, error)
  })
})
```

---

## 三、工作原理

### 1. 响应式原理

#### 【高级】题目 1：请深入讲解 Pinia 的响应式实现原理

**答案：**

Pinia 的响应式实现基于 Vue3 的响应式系统，核心使用 `reactive`、`ref`、`computed` 等 API。

**1. Options Store 的响应式实现**

```javascript
// 简化版实现原理
function defineStore(id, options) {
  const { state, getters, actions } = options
  
  return function useStore() {
    // 1. 创建响应式 state
    const stateRef = ref()
    function setup() {
      // 使用 reactive 包装 state
      const reactiveState = reactive(state())
      
      // 2. 转换 getters 为 computed
      const computedGetters = {}
      for (const key in getters) {
        computedGetters[key] = computed(() => {
          // 将 this 绑定到包含 state 和 getters 的对象
          const self = { ...reactiveState, ...computedGetters }
          return getters[key].call(self, reactiveState)
        })
      }
      
      // 3. 绑定 actions 的 this
      const boundActions = {}
      for (const key in actions) {
        boundActions[key] = (...args) => {
          const self = { ...reactiveState, ...computedGetters, ...boundActions }
          return actions[key].apply(self, args)
        }
      }
      
      return { ...reactiveState, ...computedGetters, ...boundActions }
    }
    
    return useStore.setup ? useStore.setup() : setup()
  }
}
```

**2. Setup Store 的响应式实现**

```javascript
// Setup Store 更简单，直接使用 Composition API
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCounterStore = defineStore('counter', () => {
  // ref -> state
  const count = ref(0)
  
  // computed -> getters
  const double = computed(() => count.value * 2)
  
  // function -> actions
  const increment = () => count.value++
  
  return { count, double, increment }
})
```

**3. 响应式数据流**

```
组件访问 store.count
       ↓
触发 ref/reactive 的 getter
       ↓
track 收集依赖（当前组件的 render effect）
       ↓
count.value 改变
       ↓
trigger 触发更新
       ↓
组件重新渲染
```

**4. effectScope 的使用**

Pinia 使用 `effectScope` 来管理所有响应式副作用，确保在 store 销毁时正确清理。

```javascript
import { effectScope, ref, computed } from 'vue'

function createSetupStore(id, setup) {
  // 创建独立的 effect scope
  const scope = effectScope(true)
  
  const store = scope.run(() => {
    const state = ref(0)
    const getter = computed(() => state.value * 2)
    
    return { state, getter }
  })
  
  // 提供 $dispose 方法销毁 store
  store.$dispose = () => scope.stop()
  
  return store
}
```

---

### 2. Store 注册机制

#### 【高级】题目 2：Pinia 的 Store 是如何注册和懒加载的？请讲解其内部机制

**答案：**

Pinia 的 Store 采用懒加载机制，只有在第一次调用 `useStore()` 时才会创建。

**1. 注册流程**

```javascript
// main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'

const app = createApp(App)
const pinia = createPinia()

// 将 pinia 实例挂载到 app
app.use(pinia)

app.mount('#app')
```

```javascript
// createPinia 内部简化实现
function createPinia() {
  const scope = effectScope(true)
  
  const state = scope.run(() => ref({}))
  
  const pinia = {
    install(app) {
      // 将 pinia 实例挂载到 app.config.globalProperties
      app.config.globalProperties.$pinia = pinia
      
      // 注入到组件实例
      app.provide(piniaSymbol, pinia)
      
      // 注册到全局
      pinia._a = app
      pinia._e = scope
    },
    
    _s: new Map(),  // 存储所有 store
    _a: null,       // app 实例
    _e: scope,      // 全局 effect scope
    state,          // 全局 state
    
    use(plugin) {
      this._p.push(plugin)
      return this
    }
  }
  
  return pinia
}
```

**2. Store 的懒加载机制**

```javascript
// defineStore 内部简化实现
function defineStore(id, setup) {
  // 返回 useStore 函数
  function useStore(pinia) {
    // 获取当前组件实例注入的 pinia
    const currentInstance = getCurrentInstance()
    if (currentInstance) {
      pinia = inject(piniaSymbol)
    }
    
    // 如果 store 未创建，则创建
    if (!pinia._s.has(id)) {
      if (typeof setup === 'function') {
        // Setup Store
        createSetupStore(id, setup, pinia)
      } else {
        // Options Store
        createOptionsStore(id, setup, pinia)
      }
    }
    
    // 返回已创建的 store
    return pinia._s.get(id)
  }
  
  return useStore
}
```

**3. Store 缓存机制**

```javascript
// Store 创建后会被缓存
const useCounterStore = defineStore('counter', { /* ... */ })

const store1 = useCounterStore()  // 第一次调用，创建 store
const store2 = useCounterStore()  // 第二次调用，返回缓存的 store

console.log(store1 === store2)  // true
```

**4. 整个流程图**

```
app.use(pinia)
    ↓
install() 注入 pinia 到 app
    ↓
组件中调用 useStore()
    ↓
检查 pinia._s 中是否已存在该 store
    ↓
不存在 → 创建 store 并缓存
    ↓
返回 store 实例
```

---

### 3. 依赖收集与更新

#### 【高级】题目 3：Pinia 是如何实现跨组件状态共享和响应式更新的？

**答案：**

Pinia 通过 Vue3 的响应式系统实现跨组件状态共享，核心机制如下：

**1. 单例模式 + 响应式系统**

```javascript
// Pinia 内部维护一个 Map 存储所有 store
const stores = new Map()

// 每次 useStore 返回同一个 store 实例
function useStore() {
  if (!stores.has(id)) {
    stores.set(id, createStore())
  }
  return stores.get(id)
}
```

**2. 依赖收集流程**

```javascript
// 组件 setup 中
const counter = useCounterStore()

// 模板中访问 counter.count
// <div>{{ counter.count }}</div>

// 等同于：
// render 函数执行时，访问 counter.count
// 触发 ref/reactive 的 getter
// track() 收集当前组件的 render effect 作为依赖
```

**3. 更新触发流程**

```javascript
// 在任何地方修改 state
counter.count++

// 触发 trigger()
// 找到依赖该 state 的所有 effects
// 执行这些 effects（重新渲染组件）
```

**4. 完整的响应式更新流程图**

```
组件 A setup:
  const counter = useCounterStore()
  // 获取同一个 store 实例
  // 访问 counter.count → 收集组件 A 为依赖
  ↓
组件 B setup:
  const counter = useCounterStore()
  // 获取同一个 store 实例
  // 访问 counter.count → 收集组件 B 为依赖
  ↓
组件 C (某个事件中):
  counter.count++
  // 触发 trigger
  // 通知所有依赖（组件 A、B）重新渲染
```

**5. 代码示例验证**

```javascript
// stores/counter.js
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', {
  state: () => ({ count: 0 }),
  actions: {
    increment() { this.count++ }
  }
})

// ComponentA.vue
import { useCounterStore } from '@/stores/counter'
const counter = useCounterStore()
// 模板中使用 counter.count

// ComponentB.vue
import { useCounterStore } from '@/stores/counter'
const counter = useCounterStore()
// 任何地方调用 counter.increment() 都会触发 ComponentA 重新渲染
```

---

## 四、Pinia 与 Vuex 对比

### 1. 核心差异

#### 【中级】题目 1：为什么 Vue3 官方推荐使用 Pinia 而不是 Vuex？请详细说明原因

**答案：**

Vue3 官方推荐 Pinia 主要基于以下原因：

**1. 更简洁的 API 设计**

```javascript
// Vuex：需要 mutations
const store = {
  state: { count: 0 },
  mutations: {
    SET_COUNT(state, payload) {
      state.count = payload
    }
  },
  actions: {
    async updateCount({ commit }, payload) {
      commit('SET_COUNT', payload)
    }
  }
}

// Pinia：直接修改
const useStore = defineStore('main', {
  state: () => ({ count: 0 }),
  actions: {
    async updateCount(payload) {
      this.count = payload
    }
  }
})
```

**2. 更好的 TypeScript 支持**

```typescript
// Vuex：需要大量类型声明
import { Module, Store } from 'vuex'

interface State {
  count: number
}

const store: Module<State, RootState> = {
  state: () => ({ count: 0 }),
  mutations: {
    SET_COUNT(state, payload: number) {
      state.count = payload
    }
  },
  actions: {
    async updateCount({ commit }, payload: number) {
      commit('SET_COUNT', payload)
    }
  }
}

// 使用时需要类型断言
this.$store.commit('SET_COUNT', 10) as void
this.$store.dispatch('updateCount', 10) as Promise<void>

// Pinia：完整的类型推导
const useStore = defineStore('main', {
  state: () => ({ count: 0 }),
  actions: {
    updateCount(payload: number) {
      this.count = payload
    }
  }
})

const store = useStore()
store.updateCount(10)  // 完整的类型提示
```

**3. 更好的开发体验**

- 无 mutations，减少样板代码
- 无需嵌套模块，每个 store 独立
- 完整的 DevTools 支持
- 更好的代码补全

**4. 更小的体积**

```javascript
// Vuex 4：~10KB (gzipped)
// Pinia：~1KB (gzipped)
```

**5. 更好的组合式 API 支持**

```javascript
// Pinia 原生支持组合式 API
export const useUserStore = defineStore('user', () => {
  const name = ref('')
  const age = ref(0)
  
  // 可以使用任何组合式 API
  watch(name, (newName) => {
    localStorage.setItem('name', newName)
  })
  
  return { name, age }
})
```

---

## 五、高级特性

### 1. Store 相互调用

#### 【中级】题目 1：在 Pinia 中如何实现 Store 之间的相互调用？

**答案：**

Pinia 中的 Store 可以直接相互调用，无需复杂的模块嵌套。

**1. 在 getter 中调用其他 store**

```javascript
// stores/user.js
import { defineStore } from 'pinia'
import { useCartStore } from './cart'

export const useUserStore = defineStore('user', {
  state: () => ({
    id: 1,
    name: 'John',
    role: 'user'
  }),
  getters: {
    cartItemCount() {
      const cartStore = useCartStore()
      return cartStore.itemCount
    }
  }
})

// stores/cart.js
import { defineStore } from 'pinia'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: []
  }),
  getters: {
    itemCount: state => state.items.length
  }
})
```

**2. 在 action 中调用其他 store**

```javascript
// stores/order.js
import { defineStore } from 'pinia'
import { useUserStore } from './user'
import { useCartStore } from './cart'

export const useOrderStore = defineStore('order', {
  state: () => ({
    orders: []
  }),
  actions: {
    async createOrder() {
      const userStore = useUserStore()
      const cartStore = useCartStore()
      
      // 检查用户是否登录
      if (!userStore.id) {
        throw new Error('Please login first')
      }
      
      // 检查购物车是否为空
      if (cartStore.items.length === 0) {
        throw new Error('Cart is empty')
      }
      
      // 创建订单
      const response = await fetch('/api/orders', {
        method: 'POST',
        body: JSON.stringify({
          userId: userStore.id,
          items: cartStore.items
        })
      })
      
      const order = await response.json()
      this.orders.push(order)
      
      // 清空购物车
      cartStore.clearCart()
      
      return order
    }
  }
})
```

**3. 注意事项**

```javascript
// ❌ 错误：在顶层调用会导致循环依赖问题
import { useUserStore } from './user'
import { useCartStore } from './cart'

const userStore = useUserStore()  // 错误：此时 pinia 可能还未初始化

export const useOrderStore = defineStore('order', {
  actions: {
    createOrder() {
      // ✅ 正确：在 action 内部调用
      const userStore = useUserStore()
      const cartStore = useCartStore()
    }
  }
})
```

---

### 2. 组合式 Store

#### 【高级】题目 2：如何使用组合式 Store 模式复用逻辑？

**答案：**

组合式 Store 模式允许将通用逻辑提取为可复用的函数。

**1. 创建可复用的 Store 函数**

```javascript
// stores/composables/usePagination.js
import { ref, computed } from 'vue'

export function usePagination(fetchData) {
  const currentPage = ref(1)
  const pageSize = ref(10)
  const total = ref(0)
  const data = ref([])
  const loading = ref(false)
  
  const totalPages = computed(() => 
    Math.ceil(total.value / pageSize.value)
  )
  
  const fetchPage = async () => {
    loading.value = true
    try {
      const result = await fetchData({
        page: currentPage.value,
        size: pageSize.value
      })
      data.value = result.list
      total.value = result.total
    } finally {
      loading.value = false
    }
  }
  
  const nextPage = () => {
    if (currentPage.value < totalPages.value) {
      currentPage.value++
      fetchPage()
    }
  }
  
  const prevPage = () => {
    if (currentPage.value > 1) {
      currentPage.value--
      fetchPage()
    }
  }
  
  const goToPage = (page) => {
    currentPage.value = page
    fetchPage()
  }
  
  return {
    currentPage, pageSize, total, data, loading,
    totalPages,
    fetchPage, nextPage, prevPage, goToPage
  }
}
```

**2. 在 Store 中使用组合式函数**

```javascript
// stores/user.js
import { defineStore } from 'pinia'
import { usePagination } from './composables/usePagination'

export const useUserStore = defineStore('user', () => {
  // 使用分页组合式函数
  const pagination = usePagination(async ({ page, size }) => {
    const response = await fetch(`/api/users?page=${page}&size=${size}`)
    return response.json()
  })
  
  const selectedUser = ref(null)
  
  const selectUser = (user) => {
    selectedUser.value = user
  }
  
  return {
    ...pagination,
    selectedUser,
    selectUser
  }
})
```

**3. 多个组合式函数组合**

```javascript
// stores/product.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { usePagination } from './composables/usePagination'
import { useFiltering } from './composables/useFiltering'
import { useSorting } from './composables/useSorting'

export const useProductStore = defineStore('product', () => {
  const filter = ref('')
  
  // 组合多个功能
  const pagination = usePagination(async ({ page, size }) => {
    const response = await fetch(
      `/api/products?filter=${filter.value}&page=${page}&size=${size}`
    )
    return response.json()
  })
  
  const filtering = useFiltering({
    onFilterChange: pagination.fetchPage
  })
  
  const sorting = useSorting({
    onSortChange: pagination.fetchPage
  })
  
  return {
    filter,
    ...pagination,
    ...filtering,
    ...sorting
  }
})
```

---

### 3. 持久化存储

#### 【高级】题目 3：如何实现 Pinia Store 的持久化存储？有哪些方案？

**答案：**

**1. 手动实现持久化**

```javascript
// stores/user.js
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),
  actions: {
    setToken(token) {
      this.token = token
      localStorage.setItem('token', token)
    },
    setUser(user) {
      this.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
```

**2. 使用 `$subscribe` 实现自动持久化**

```javascript
// stores/user.js
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: '',
    user: null,
    preferences: {}
  }),
  actions: {
    init() {
      // 从 localStorage 恢复
      const saved = localStorage.getItem('user-store')
      if (saved) {
        this.$patch(JSON.parse(saved))
      }
      
      // 订阅变化自动保存
      this.$subscribe((mutation, state) => {
        localStorage.setItem('user-store', JSON.stringify(state))
      })
    }
  }
})

// 在组件中使用
const userStore = useUserStore()
userStore.init()
```

**3. 使用 Pinia 持久化插件**

```bash
npm install pinia-plugin-persistedstate
```

```javascript
// main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

const app = createApp(App)
app.use(pinia)
app.mount('#app')
```

```javascript
// stores/user.js
export const useUserStore = defineStore('user', {
  state: () => ({
    token: '',
    user: null,
    preferences: {}
  }),
  persist: {
    key: 'user-store',
    storage: localStorage,
    paths: ['token', 'user']  // 只持久化部分字段
  }
})
```

**4. 自定义持久化插件**

```javascript
// plugins/persist.js
import { toRaw } from 'vue'

export function createPersistPlugin(options = {}) {
  const { key = 'pinia', storage = localStorage } = options
  
  return ({ store }) => {
    // 从存储恢复状态
    const savedState = storage.getItem(`${key}-${store.$id}`)
    if (savedState) {
      store.$patch(JSON.parse(savedState))
    }
    
    // 订阅状态变化
    store.$subscribe((mutation, state) => {
      const stateToSave = toRaw(state)
      storage.setItem(`${key}-${store.$id}`, JSON.stringify(stateToSave))
    })
  }
}

// 使用
import { createPinia } from 'pinia'
import { createPersistPlugin } from './plugins/persist'

const pinia = createPinia()
pinia.use(createPersistPlugin({
  key: 'myapp',
  storage: localStorage
}))
```

---

### 4. 插件机制

#### 【高级】题目 4：如何编写 Pinia 插件？请举例说明常见插件的应用场景

**答案：**

**插件基本结构：**

```javascript
// plugins/myPlugin.js
export function myPiniaPlugin({ store }) {
  // 可以在 store 上添加属性或方法
  store.myMethod = () => {
    console.log('Plugin method called on', store.$id)
  }
  
  // 可以订阅 state 变化
  store.$subscribe((mutation, state) => {
    console.log(`[${store.$id}] State changed:`, mutation.type)
  })
  
  // 可以订阅 action 调用
  store.$onAction(({ name, args, after, onError }) => {
    console.log(`[${store.$id}] Action ${name} started`)
    after(() => {
      console.log(`[${store.$id}] Action ${name} completed`)
    })
  })
}

// 注册插件
const pinia = createPinia()
pinia.use(myPiniaPlugin)
```

**1. 日志插件**

```javascript
// plugins/logger.js
export function loggerPlugin({ store }) {
  store.$subscribe((mutation, state) => {
    console.group(`[${store.$id}] State Update`)
    console.log('Mutation type:', mutation.type)
    console.log('New state:', state)
    console.groupEnd()
  })
  
  store.$onAction(({ name, args, after, onError }) => {
    const startTime = Date.now()
    
    console.group(`[${store.$id}] Action: ${name}`)
    console.log('Args:', args)
    
    after((result) => {
      console.log('Result:', result)
      console.log('Duration:', Date.now() - startTime, 'ms')
      console.groupEnd()
    })
    
    onError((error) => {
      console.error('Error:', error)
      console.groupEnd()
    })
  })
}
```

**2. 数据验证插件**

```javascript
// plugins/validator.js
export function validatorPlugin({ store }) {
  // 添加验证方法
  store.$validate = (rules) => {
    const errors = {}
    for (const field in rules) {
      const rule = rules[field]
      const value = store[field]
      
      if (rule.required && !value) {
        errors[field] = `${field} is required`
      }
      if (rule.min && value < rule.min) {
        errors[field] = `${field} must be at least ${rule.min}`
      }
      if (rule.max && value > rule.max) {
        errors[field] = `${field} must be at most ${rule.max}`
      }
    }
    return errors
  }
}
```

**3. API 请求缓存插件**

```javascript
// plugins/apiCache.js
const cache = new Map()

export function apiCachePlugin({ store }) {
  store.$cachedApi = async (key, apiCall, ttl = 60000) => {
    const cacheKey = `${store.$id}:${key}`
    const cached = cache.get(cacheKey)
    
    if (cached && Date.now() - cached.timestamp < ttl) {
      return cached.data
    }
    
    const data = await apiCall()
    cache.set(cacheKey, {
      data,
      timestamp: Date.now()
    })
    
    return data
  }
  
  store.$clearCache = () => {
    for (const key of cache.keys()) {
      if (key.startsWith(`${store.$id}:`)) {
        cache.delete(key)
      }
    }
  }
}
```

**4. 同步插件（跨标签页同步）**

```javascript
// plugins/sync.js
export function syncPlugin({ store }) {
  // 监听其他标签页的 storage 事件
  window.addEventListener('storage', (event) => {
    if (event.key === `pinia-sync-${store.$id}` && event.newValue) {
      const newState = JSON.parse(event.newValue)
      store.$patch(newState)
    }
  })
  
  // 状态变化时同步到其他标签页
  store.$subscribe((mutation, state) => {
    localStorage.setItem(
      `pinia-sync-${store.$id}`,
      JSON.stringify(state)
    )
  })
}
```

---

### 5. SSR 支持

#### 【高级】题目 5：Pinia 在 SSR 中如何使用？需要注意哪些问题？

**答案：**

**1. 基本配置**

```javascript
// server.js (Node.js 服务端)
import express from 'express'
import { createSSRApp } from 'vue'
import { renderToString } from '@vue/server-renderer'
import { createPinia } from 'pinia'
import App from './App.vue'

const server = express()

server.get('*', async (req, res) => {
  const app = createSSRApp(App)
  const pinia = createPinia()
  app.use(pinia)
  
  // 在服务端预取数据
  const appInstance = app.mount()
  
  // 调用 store 的初始化方法
  await Promise.all([
    useUserStore(pinia).fetchUser(),
    useProductStore(pinia).fetchProducts()
  ])
  
  const html = await renderToString(appInstance)
  
  // 将 state 序列化到客户端
  const state = pinia.state.value
  
  res.send(`
    <!DOCTYPE html>
    <html>
      <head><title>SSR App</title></head>
      <body>
        <div id="app">${html}</div>
        <script>
          window.__PINIA_STATE__ = ${JSON.stringify(state)}
        </script>
        <script src="/client.js"></script>
      </body>
    </html>
  `)
})

server.listen(3000)
```

```javascript
// client.js (客户端入口)
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()

// 从服务端注入的 state 恢复
if (window.__PINIA_STATE__) {
  pinia.state.value = window.__PINIA_STATE__
}

app.use(pinia)
app.mount('#app')
```

**2. 注意事项**

**a. 避免单例状态污染**

```javascript
// ❌ 错误：所有请求共享同一个 pinia 实例
const pinia = createPinia()  // 在模块级别创建

server.get('*', (req, res) => {
  app.use(pinia)  // 所有请求使用同一个 pinia
})

// ✅ 正确：每个请求创建新的 pinia 实例
server.get('*', (req, res) => {
  const pinia = createPinia()  // 每次请求创建新实例
  const app = createApp(App)
  app.use(pinia)
  // ...
})
```

**b. 数据预取**

```javascript
// stores/user.js
export const useUserStore = defineStore('user', {
  state: () => ({
    user: null
  }),
  actions: {
    async fetchUser() {
      const response = await fetch('/api/user')
      this.user = await response.json()
    }
  }
})

// 在组件中使用 onServerPrefetch 预取数据
import { onServerPrefetch } from 'vue'
import { useUserStore } from '@/stores/user'

export default {
  setup() {
    const userStore = useUserStore()
    
    // 服务端预取
    onServerPrefetch(async () => {
      await userStore.fetchUser()
    })
    
    // 客户端如果 state 为空则再次获取
    if (!userStore.user) {
      userStore.fetchUser()
    }
    
    return { userStore }
  }
}
```

**3. 使用 Nuxt 3**

```javascript
// Nuxt 3 自动配置了 Pinia，只需安装模块
// nuxt.config.js
export default defineNuxtConfig({
  modules: ['@pinia/nuxt']
})

// stores/user.js - 自动导入
export const useUserStore = defineStore('user', {
  state: () => ({ user: null }),
  actions: {
    async fetchUser() {
      this.user = await $fetch('/api/user')
    }
  }
})

// 在组件中使用
const userStore = useUserStore()
// Nuxt 会自动处理 SSR 数据预取
```

---

## 六、TypeScript 集成

### 1. 类型推导

#### 【中级】题目 1：Pinia 如何自动推导 TypeScript 类型？

**答案：**

Pinia 提供完整的 TypeScript 支持，可以自动推导 state、getters、actions 的类型。

**1. 自动类型推导**

```typescript
// stores/counter.ts
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', {
  state: () => ({
    count: 0,                    // 自动推导为 number
    name: 'Eduardo',             // 自动推导为 string
    items: [] as string[],       // 显式标注为 string[]
    user: null as User | null    // 显式标注为 User | null
  }),
  
  getters: {
    // 自动推导返回类型
    doubleCount(): number {
      return this.count * 2
    },
    
    // 自动推导参数类型
    doubleCountPlusOne(): number {
      return this.doubleCount + 1
    }
  },
  
  actions: {
    // 参数和返回值自动推导
    increment() {
      this.count++  // this 类型自动推导
    },
    
    async fetchCount(): Promise<void> {
      const response = await fetch('/api/count')
      this.count = await response.json()
    }
  }
})

// 使用时类型自动推导
const counter = useCounterStore()
counter.count         // number
counter.name          // string
counter.doubleCount   // number
counter.increment()   // () => void
```

**2. Setup Store 的类型推导**

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // ref 的类型自动推导
  const name = ref('')               // Ref<string>
  const age = ref(0)                 // Ref<number>
  const user = ref<User | null>(null) // 显式标注
  
  // computed 的类型自动推导
  const displayName = computed(() => name.value.toUpperCase()) // ComputedRef<string>
  
  // 函数参数和返回值自动推导
  function setName(newName: string): void {
    name.value = newName
  }
  
  async function fetchUser(id: number): Promise<void> {
    const response = await fetch(`/api/users/${id}`)
    user.value = await response.json()
  }
  
  return { name, age, user, displayName, setName, fetchUser }
})
```

---

### 2. 类型标注

#### 【高级】题目 2：如何为 Pinia Store 添加完整的类型标注？如何跨文件复用类型？

**答案：**

**1. 定义接口并标注**

```typescript
// types/user.ts
export interface User {
  id: number
  name: string
  email: string
  role: 'admin' | 'user' | 'guest'
}

export interface UserState {
  users: User[]
  currentUser: User | null
  loading: boolean
  error: string | null
}

export interface UserGetters {
  userCount: number
  isAdmin: boolean
  currentUserRole: string
}

export interface UserActions {
  fetchUsers: () => Promise<void>
  login: (credentials: { email: string; password: string }) => Promise<void>
  logout: () => void
  updateUser: (id: number, data: Partial<User>) => Promise<void>
}
```

**2. 在 Store 中使用类型**

```typescript
// stores/user.ts
import { defineStore } from 'pinia'
import type { UserState, UserGetters, UserActions } from '@/types/user'

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    users: [],
    currentUser: null,
    loading: false,
    error: null
  }),
  
  getters: {
    userCount: (state): UserGetters['userCount'] => state.users.length,
    
    isAdmin: (state): UserGetters['isAdmin'] => 
      state.currentUser?.role === 'admin',
    
    currentUserRole: (state): UserGetters['currentUserRole'] => 
      state.currentUser?.role ?? 'guest'
  },
  
  actions: {
    async fetchUsers() {
      this.loading = true
      try {
        const response = await fetch('/api/users')
        this.users = await response.json()
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    
    async login(credentials) {
      const response = await fetch('/api/login', {
        method: 'POST',
        body: JSON.stringify(credentials)
      })
      this.currentUser = await response.json()
    },
    
    logout() {
      this.currentUser = null
    },
    
    async updateUser(id, data) {
      const response = await fetch(`/api/users/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
      })
      const updatedUser = await response.json()
      const index = this.users.findIndex(u => u.id === id)
      if (index !== -1) {
        this.users[index] = updatedUser
      }
    }
  }
})
```

**3. 使用 `StoreDefinition` 类型**

```typescript
import { defineStore, type Store } from 'pinia'

// 定义 store 类型
type UserStore = Store<'user', UserState, UserGetters, UserActions>

// 在组件中使用
import { useUserStore } from '@/stores/user'

export default defineComponent({
  setup() {
    const userStore = useUserStore()  // 类型自动推导为 UserStore
    
    // 完整的类型提示
    userStore.fetchUsers()
    userStore.currentUser?.name
    
    return { userStore }
  }
})
```

**4. 组合式 Store 的类型标注**

```typescript
// stores/composables/usePagination.ts
import { ref, computed, type Ref, type ComputedRef } from 'vue'

interface PaginationOptions<T> {
  fetchData: (params: { page: number; size: number }) => Promise<{
    list: T[]
    total: number
  }>
  initialPageSize?: number
}

interface PaginationReturn<T> {
  currentPage: Ref<number>
  pageSize: Ref<number>
  total: Ref<number>
  data: Ref<T[]>
  loading: Ref<boolean>
  totalPages: ComputedRef<number>
  fetchPage: () => Promise<void>
  nextPage: () => void
  prevPage: () => void
  goToPage: (page: number) => void
}

export function usePagination<T>(
  options: PaginationOptions<T>
): PaginationReturn<T> {
  const currentPage = ref(1)
  const pageSize = ref(options.initialPageSize ?? 10)
  const total = ref(0)
  const data = ref([]) as Ref<T[]>
  const loading = ref(false)
  
  const totalPages = computed(() => 
    Math.ceil(total.value / pageSize.value)
  )
  
  const fetchPage = async () => {
    loading.value = true
    try {
      const result = await options.fetchData({
        page: currentPage.value,
        size: pageSize.value
      })
      data.value = result.list
      total.value = result.total
    } finally {
      loading.value = false
    }
  }
  
  const nextPage = () => {
    if (currentPage.value < totalPages.value) {
      currentPage.value++
      fetchPage()
    }
  }
  
  const prevPage = () => {
    if (currentPage.value > 1) {
      currentPage.value--
      fetchPage()
    }
  }
  
  const goToPage = (page: number) => {
    currentPage.value = page
    fetchPage()
  }
  
  return {
    currentPage, pageSize, total, data, loading,
    totalPages, fetchPage, nextPage, prevPage, goToPage
  }
}
```

---

## 七、测试与调试

### 1. 单元测试

#### 【高级】题目 1：如何为 Pinia Store 编写单元测试？

**答案：**

**1. 基本测试设置**

```javascript
// counter.spec.js
import { setActivePinia, createPinia } from 'pinia'
import { useCounterStore } from '@/stores/counter'

describe('Counter Store', () => {
  beforeEach(() => {
    // 每个测试前创建新的 pinia 实例
    setActivePinia(createPinia())
  })
  
  it('should have initial count of 0', () => {
    const counter = useCounterStore()
    expect(counter.count).toBe(0)
  })
  
  it('should increment count', () => {
    const counter = useCounterStore()
    counter.increment()
    expect(counter.count).toBe(1)
  })
  
  it('should double the count', () => {
    const counter = useCounterStore()
    counter.count = 5
    expect(counter.doubleCount).toBe(10)
  })
  
  it('should reset state', () => {
    const counter = useCounterStore()
    counter.count = 10
    counter.$reset()
    expect(counter.count).toBe(0)
  })
})
```

**2. 测试异步 Action**

```javascript
// user.spec.js
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '@/stores/user'

// Mock fetch
global.fetch = vi.fn()

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    fetch.mockClear()
  })
  
  it('should fetch users', async () => {
    const mockUsers = [
      { id: 1, name: 'John' },
      { id: 2, name: 'Jane' }
    ]
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockUsers)
    })
    
    const userStore = useUserStore()
    await userStore.fetchUsers()
    
    expect(userStore.users).toEqual(mockUsers)
    expect(userStore.loading).toBe(false)
    expect(fetch).toHaveBeenCalledWith('/api/users')
  })
  
  it('should handle fetch error', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'))
    
    const userStore = useUserStore()
    await userStore.fetchUsers()
    
    expect(userStore.users).toEqual([])
    expect(userStore.error).toBe('Network error')
    expect(userStore.loading).toBe(false)
  })
})
```

**3. 测试 Store 交互**

```javascript
// order.spec.js
import { setActivePinia, createPinia } from 'pinia'
import { useOrderStore } from '@/stores/order'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'

describe('Order Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })
  
  it('should create order when user is logged in and cart is not empty', async () => {
    // 设置 user store
    const userStore = useUserStore()
    userStore.setUser({ id: 1, name: 'John' })
    
    // 设置 cart store
    const cartStore = useCartStore()
    cartStore.items = [
      { id: 1, name: 'Product 1', price: 100 }
    ]
    
    // Mock API
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ id: 1, items: cartStore.items })
    })
    
    const orderStore = useOrderStore()
    const order = await orderStore.createOrder()
    
    expect(order.id).toBe(1)
    expect(orderStore.orders).toHaveLength(1)
    expect(cartStore.items).toHaveLength(0)  // 购物车应被清空
  })
  
  it('should throw error when user is not logged in', async () => {
    const userStore = useUserStore()
    userStore.setUser(null)
    
    const cartStore = useCartStore()
    cartStore.items = [{ id: 1 }]
    
    const orderStore = useOrderStore()
    
    await expect(orderStore.createOrder()).rejects.toThrow('Please login first')
  })
})
```

**4. 测试初始状态**

```javascript
// 初始状态测试
it('should have correct initial state', () => {
  const store = useUserStore()
  
  expect(store.$state).toEqual({
    users: [],
    currentUser: null,
    loading: false,
    error: null
  })
})

// 测试 $patch
it('should patch state', () => {
  const store = useUserStore()
  
  store.$patch({
    users: [{ id: 1, name: 'John' }],
    loading: true
  })
  
  expect(store.users).toHaveLength(1)
  expect(store.loading).toBe(true)
})
```

---

### 2. 调试技巧

#### 【中级】题目 2：如何使用 Vue DevTools 调试 Pinia？

**答案：**

**1. 基本调试**

Vue DevTools 自动识别 Pinia，提供专门的面板：

- **State 查看**：实时查看所有 store 的 state
- **Timeline**：记录 state 变化和 action 调用
- **Time Travel**：回退到任意历史状态
- **Custom Inspector**：查看 store 的 getters 和 actions

**2. 启用调试模式**

```javascript
// 开发环境下启用严格模式
const pinia = createPinia()

if (import.meta.env.DEV) {
  // 可以添加开发环境的调试插件
  pinia.use(({ store }) => {
    store.$subscribe((mutation, state) => {
      console.log(`[${store.$id}] State changed:`, mutation.type, state)
    })
    
    store.$onAction(({ name, args, after, onError }) => {
      console.log(`[${store.$id}] Action ${name} called with:`, args)
      
      after((result) => {
        console.log(`[${store.$id}] Action ${name} returned:`, result)
      })
    })
  })
}
```

**3. 使用 `$subscribe` 和 `$onAction` 调试**

```javascript
// 临时调试代码
const counter = useCounterStore()

// 调试 state 变化
const unsubState = counter.$subscribe((mutation, state) => {
  debugger  // 在浏览器中暂停
  console.log('State changed:', mutation, state)
})

// 调试 action 调用
const unsubAction = counter.$onAction(({ name, args, after, onError }) => {
  console.log(`Action ${name} called`)
  
  after((result) => {
    console.log(`Action ${name} completed:`, result)
  })
  
  onError((error) => {
    console.error(`Action ${name} failed:`, error)
  })
})

// 调试完成后取消订阅
// unsubState()
// unsubAction()
```

**4. 在控制台中调试**

```javascript
// 在浏览器控制台中访问 store
// 前提：需要将 store 挂载到 window 对象

// main.js
if (import.meta.env.DEV) {
  import('@/stores').then(stores => {
    window.stores = stores
  })
}

// 控制台中
stores.useCounterStore().count
stores.useUserStore().fetchUsers()
```

---

## 八、最佳实践

### 1. 项目结构

#### 【中级】题目 1：Pinia Store 的推荐项目结构是什么？

**答案：**

**1. 按功能模块组织**

```
src/
├── stores/
│   ├── index.js              # 统一导出
│   ├── user.js               # 用户模块
│   ├── cart.js               # 购物车模块
│   ├── product.js            # 商品模块
│   └── composables/          # 可复用的组合式函数
│       ├── usePagination.js
│       └── useFiltering.js
├── components/
├── views/
└── App.vue
```

```javascript
// stores/index.js
export * from './user'
export * from './cart'
export * from './product'
```

**2. 按业务领域组织（大型项目）**

```
src/
├── modules/
│   ├── user/
│   │   ├── stores/
│   │   │   ├── user.js
│   │   │   └── auth.js
│   │   ├── components/
│   │   └── views/
│   ├── cart/
│   │   ├── stores/
│   │   │   └── cart.js
│   │   ├── components/
│   │   └── views/
│   └── product/
│       ├── stores/
│       │   └── product.js
│       └── views/
└── stores/                  # 全局 store
    ├── app.js               # 应用配置
    └── theme.js             # 主题设置
```

**3. 命名规范**

```javascript
// ✅ 推荐：useXxxStore
export const useUserStore = defineStore('user', { /* ... */ })
export const useCartStore = defineStore('cart', { /* ... */ })

// ❌ 不推荐：缺少 use 前缀或 Store 后缀
export const user = defineStore('user', { /* ... */ })
export const useUser = defineStore('user', { /* ... */ })
```

**4. 统一的 Store 模板**

```javascript
// stores/template.js
import { defineStore } from 'pinia'

/**
 * Xxx Store
 * 负责管理 xxx 相关的状态和逻辑
 */
export const useXxxStore = defineStore('xxx', {
  // 状态
  state: () => ({
    data: [],
    loading: false,
    error: null
  }),
  
  // 计算属性
  getters: {
    dataCount: (state) => state.data.length,
    hasError: (state) => !!state.error
  },
  
  // 方法
  actions: {
    /**
     * 获取数据
     * @param {Object} params - 查询参数
     */
    async fetchData(params = {}) {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/xxx', { params })
        this.data = response.data
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    
    /**
     * 重置状态
     */
    reset() {
      this.$reset()
    }
  }
})
```

---

### 2. 性能优化

#### 【高级】题目 2：Pinia 有哪些性能优化的方法和最佳实践？

**答案：**

**1. 避免不必要的响应式**

```javascript
import { markRaw } from 'vue'

export const useLargeDataStore = defineStore('largeData', {
  state: () => ({
    // 大型静态数据使用 markRaw 避免响应式开销
    config: markRaw(largeConfigObject),
    
    // 不需要响应式的数据
    staticData: markRaw({
      options: [/* ... */],
      mappings: { /* ... */ }
    }),
    
    // 需要响应式的数据
    items: [],
    selectedItem: null
  })
})
```

**2. 使用 `storeToRefs` 解构保持响应性**

```javascript
import { storeToRefs } from 'pinia'
import { useUserStore } from '@/stores/user'

// ✅ 推荐：使用 storeToRefs
const userStore = useUserStore()
const { users, currentUser } = storeToRefs(userStore)

// actions 可以直接解构（函数不需要响应性）
const { fetchUsers, login } = userStore

// ❌ 错误：直接解构会丢失响应性
const { users, currentUser } = userStore  // 不是响应式的
```

**3. 按需订阅**

```javascript
// ❌ 错误：订阅整个 state
store.$subscribe((mutation, state) => {
  // 每次 state 任何变化都会触发
  console.log(state)
})

// ✅ 推荐：使用 watch 精确订阅
import { watch } from 'vue'
import { storeToRefs } from 'pinia'

const { count } = storeToRefs(store)
watch(count, (newCount) => {
  // 只在 count 变化时触发
  console.log('count changed:', newCount)
})
```

**4. 懒加载 Store**

```javascript
// 对于体积较大的 store，可以懒加载
const LazyStore = defineAsyncComponent(() => 
  import('@/stores/largeStore')
)

// 在组件中
export default {
  async setup() {
    // 只在需要时加载
    const { useLargeStore } = await import('@/stores/largeStore')
    const store = useLargeStore()
    
    return { store }
  }
}
```

**5. 合理使用 computed**

```javascript
export const useProductStore = defineStore('product', () => {
  const products = ref([])
  const filterText = ref('')
  
  // ✅ 推荐：使用 computed 缓存结果
  const filteredProducts = computed(() => {
    return products.value.filter(p => 
      p.name.includes(filterText.value)
    )
  })
  
  // ✅ 推荐：复杂的计算使用 computed
  const totalPrice = computed(() => 
    filteredProducts.value.reduce((sum, p) => sum + p.price, 0)
  )
  
  return { products, filterText, filteredProducts, totalPrice }
})
```

**6. 批量更新**

```javascript
// ❌ 错误：多次单独修改
store.count = 1
store.name = 'John'
store.age = 30
// 触发 3 次更新

// ✅ 推荐：使用 $patch 批量更新
store.$patch({
  count: 1,
  name: 'John',
  age: 30
})
// 只触发 1 次更新
```

---

### 3. 常见陷阱

#### 【高级】题目 3：使用 Pinia 时有哪些常见陷阱和注意事项？

**答案：**

**1. 解构丢失响应性**

```javascript
import { useCounterStore } from '@/stores/counter'

// ❌ 错误：直接解构 state 和 getters 会丢失响应性
const { count, doubleCount } = useCounterStore()
// count 和 doubleCount 不是响应式的

// ✅ 正确：使用 storeToRefs
import { storeToRefs } from 'pinia'
const store = useCounterStore()
const { count, doubleCount } = storeToRefs(store)

// actions 可以直接解构
const { increment } = store
```

**2. 在 setup 外部使用 store**

```javascript
// ❌ 错误：在模块顶层使用
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()  // 错误！此时 pinia 还未挂载

export function someHelper() {
  return userStore.user
}

// ✅ 正确：在函数内部使用
import { useUserStore } from '@/stores/user'

export function someHelper() {
  const userStore = useUserStore()
  return userStore.user
}

// ✅ 或者：手动传入 pinia 实例
import { getActivePinia } from 'pinia'

export function someHelper() {
  const pinia = getActivePinia()
  const userStore = useUserStore(pinia)
  return userStore.user
}
```

**3. 循环依赖问题**

```javascript
// ❌ 错误：在 store 顶层相互引用
// storeA.js
import { useBStore } from './storeB'
const bStore = useBStore()  // 错误！storeB 可能还未初始化

export const useAStore = defineStore('a', {
  actions: {
    doSomething() {
      bStore.doOther()
    }
  }
})

// ✅ 正确：在 action 内部引用
export const useAStore = defineStore('a', {
  actions: {
    doSomething() {
      const bStore = useBStore()  // 在这里调用
      bStore.doOther()
    }
  }
})
```

**4. SSR 中的状态污染**

```javascript
// ❌ 错误：在模块级别修改 state
let globalState = {}

export const useStore = defineStore('main', {
  state: () => globalState  // 所有请求共享同一个 state
})

// ✅ 正确：每次返回新的 state
export const useStore = defineStore('main', {
  state: () => ({
    // 每次调用 state() 返回新对象
    data: []
  })
})
```

**5. 忘记处理异步错误**

```javascript
// ❌ 错误：未处理异步错误
export const useUserStore = defineStore('user', {
  actions: {
    async fetchUser() {
      const response = await fetch('/api/user')
      this.user = await response.json()
      // 如果 fetch 失败，错误会向上抛出
    }
  }
})

// ✅ 正确：处理错误
export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    error: null,
    loading: false
  }),
  actions: {
    async fetchUser() {
      this.loading = true
      this.error = null
      try {
        const response = await fetch('/api/user')
        if (!response.ok) throw new Error('Failed to fetch')
        this.user = await response.json()
      } catch (error) {
        this.error = error.message
        console.error('Failed to fetch user:', error)
      } finally {
        this.loading = false
      }
    }
  }
})
```

---

## 九、实战场景

### 1. 复杂业务场景

#### 【高级】题目 1：如何使用 Pinia 实现一个完整的购物车功能？

**答案：**

**1. 定义商品 Store**

```javascript
// stores/product.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useProductStore = defineStore('product', () => {
  const products = ref([])
  const loading = ref(false)
  const filter = ref({
    category: '',
    priceRange: [0, 1000],
    searchText: ''
  })
  
  const filteredProducts = computed(() => {
    return products.value.filter(product => {
      const matchCategory = !filter.value.category || 
        product.category === filter.value.category
      const matchPrice = product.price >= filter.value.priceRange[0] &&
        product.price <= filter.value.priceRange[1]
      const matchSearch = !filter.value.searchText ||
        product.name.includes(filter.value.searchText)
      return matchCategory && matchPrice && matchSearch
    })
  })
  
  async function fetchProducts() {
    loading.value = true
    try {
      const response = await fetch('/api/products')
      products.value = await response.json()
    } finally {
      loading.value = false
    }
  }
  
  function setFilter(newFilter) {
    Object.assign(filter.value, newFilter)
  }
  
  return {
    products, loading, filter, filteredProducts,
    fetchProducts, setFilter
  }
})
```

**2. 定义购物车 Store**

```javascript
// stores/cart.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useProductStore } from './product'

export const useCartStore = defineStore('cart', () => {
  const items = ref([])
  const couponCode = ref('')
  const discount = ref(0)
  
  // 计算属性
  const itemCount = computed(() => 
    items.value.reduce((sum, item) => sum + item.quantity, 0)
  )
  
  const subtotal = computed(() => 
    items.value.reduce((sum, item) => 
      sum + item.product.price * item.quantity, 0
    )
  )
  
  const total = computed(() => 
    Math.max(0, subtotal.value - discount.value)
  )
  
  // 方法
  function addToCart(product, quantity = 1) {
    const existingItem = items.value.find(
      item => item.product.id === product.id
    )
    
    if (existingItem) {
      existingItem.quantity += quantity
    } else {
      items.value.push({ product, quantity })
    }
  }
  
  function removeFromCart(productId) {
    const index = items.value.findIndex(
      item => item.product.id === productId
    )
    if (index !== -1) {
      items.value.splice(index, 1)
    }
  }
  
  function updateQuantity(productId, quantity) {
    const item = items.value.find(
      item => item.product.id === productId
    )
    if (item) {
      if (quantity <= 0) {
        removeFromCart(productId)
      } else {
        item.quantity = quantity
      }
    }
  }
  
  function clearCart() {
    items.value = []
    couponCode.value = ''
    discount.value = 0
  }
  
  async function applyCoupon(code) {
    try {
      const response = await fetch('/api/coupons/validate', {
        method: 'POST',
        body: JSON.stringify({ code, subtotal: subtotal.value })
      })
      const result = await response.json()
      
      if (result.valid) {
        couponCode.value = code
        discount.value = result.discount
      } else {
        throw new Error(result.message)
      }
    } catch (error) {
      console.error('Coupon validation failed:', error)
      throw error
    }
  }
  
  return {
    items, couponCode, discount,
    itemCount, subtotal, total,
    addToCart, removeFromCart, updateQuantity,
    clearCart, applyCoupon
  }
})
```

**3. 定义订单 Store**

```javascript
// stores/order.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useCartStore } from './cart'
import { useUserStore } from './user'

export const useOrderStore = defineStore('order', () => {
  const orders = ref([])
  const currentOrder = ref(null)
  const loading = ref(false)
  
  async function createOrder(shippingAddress) {
    const cartStore = useCartStore()
    const userStore = useUserStore()
    
    if (!userStore.currentUser) {
      throw new Error('Please login first')
    }
    
    if (cartStore.items.length === 0) {
      throw new Error('Cart is empty')
    }
    
    loading.value = true
    try {
      const response = await fetch('/api/orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userStore.token}`
        },
        body: JSON.stringify({
          userId: userStore.currentUser.id,
          items: cartStore.items,
          subtotal: cartStore.subtotal,
          discount: cartStore.discount,
          total: cartStore.total,
          shippingAddress
        })
      })
      
      if (!response.ok) {
        throw new Error('Failed to create order')
      }
      
      const order = await response.json()
      orders.value.unshift(order)
      currentOrder.value = order
      cartStore.clearCart()
      
      return order
    } finally {
      loading.value = false
    }
  }
  
  async function fetchOrders() {
    const userStore = useUserStore()
    loading.value = true
    try {
      const response = await fetch('/api/orders', {
        headers: {
          'Authorization': `Bearer ${userStore.token}`
        }
      })
      orders.value = await response.json()
    } finally {
      loading.value = false
    }
  }
  
  return {
    orders, currentOrder, loading,
    createOrder, fetchOrders
  }
})
```

**4. 在组件中使用**

```vue
<!-- Cart.vue -->
<template>
  <div class="cart">
    <h2>购物车</h2>
    
    <div v-if="cartStore.itemCount === 0" class="empty">
      购物车为空
    </div>
    
    <div v-else>
      <div 
        v-for="item in cartStore.items" 
        :key="item.product.id"
        class="cart-item"
      >
        <span>{{ item.product.name }}</span>
        <span>¥{{ item.product.price }}</span>
        <input
          v-model.number="item.quantity"
          type="number"
          min="0"
          @change="updateQuantity(item.product.id, item.quantity)"
        >
        <span>¥{{ item.product.price * item.quantity }}</span>
        <button @click="cartStore.removeFromCart(item.product.id)">
          删除
        </button>
      </div>
      
      <div class="cart-summary">
        <div>
          <label>优惠券码:</label>
          <input v-model="couponInput" type="text">
          <button @click="applyCoupon">应用</button>
        </div>
        
        <div>商品数量: {{ cartStore.itemCount }}</div>
        <div>小计: ¥{{ cartStore.subtotal }}</div>
        <div>优惠: -¥{{ cartStore.discount }}</div>
        <div>总计: ¥{{ cartStore.total }}</div>
        
        <button @click="checkout" :disabled="orderStore.loading">
          {{ orderStore.loading ? '提交中...' : '结算' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useOrderStore } from '@/stores/order'

const cartStore = useCartStore()
const orderStore = useOrderStore()
const couponInput = ref('')

const updateQuantity = (productId, quantity) => {
  cartStore.updateQuantity(productId, quantity)
}

const applyCoupon = async () => {
  try {
    await cartStore.applyCoupon(couponInput.value)
    alert('优惠券应用成功')
  } catch (error) {
    alert('优惠券无效: ' + error.message)
  }
}

const checkout = async () => {
  try {
    const order = await orderStore.createOrder({
      address: '...',
      // ...
    })
    alert(`订单创建成功: ${order.id}`)
  } catch (error) {
    alert('订单创建失败: ' + error.message)
  }
}
</script>
```

---

### 2. 与组合式 API 配合

#### 【高级】题目 2：如何将 Pinia 与 Vue3 组合式 API 深度结合使用？

**答案：**

**1. 使用 watch 监听 store 变化**

```javascript
import { watch, watchEffect } from 'vue'
import { storeToRefs } from 'pinia'
import { useUserStore } from '@/stores/user'

export default {
  setup() {
    const userStore = useUserStore()
    const { currentUser, token } = storeToRefs(userStore)
    
    // 监听单个属性
    watch(currentUser, (newUser, oldUser) => {
      console.log('User changed:', newUser)
      if (newUser) {
        localStorage.setItem('user', JSON.stringify(newUser))
      } else {
        localStorage.removeItem('user')
      }
    })
    
    // 监听多个属性
    watch([currentUser, token], ([user, token]) => {
      if (user && token) {
        console.log('User logged in with token')
      }
    })
    
    // 使用 watchEffect 自动收集依赖
    watchEffect(() => {
      document.title = currentUser.value 
        ? `${currentUser.value.name} - My App`
        : 'My App'
    })
    
    return { currentUser }
  }
}
```

**2. 在 store 中使用生命周期钩子**

```javascript
import { defineStore } from 'pinia'
import { onMounted, onUnmounted, ref } from 'vue'

export const useWebSocketStore = defineStore('websocket', () => {
  const socket = ref(null)
  const messages = ref([])
  const isConnected = ref(false)
  
  // 注意：这些钩子只在组件 setup 中调用 store 时生效
  onMounted(() => {
    connectWebSocket()
  })
  
  onUnmounted(() => {
    disconnectWebSocket()
  })
  
  function connectWebSocket() {
    socket.value = new WebSocket('ws://localhost:8080')
    
    socket.value.onopen = () => {
      isConnected.value = true
    }
    
    socket.value.onmessage = (event) => {
      messages.value.push(JSON.parse(event.data))
    }
    
    socket.value.onclose = () => {
      isConnected.value = false
    }
  }
  
  function disconnectWebSocket() {
    if (socket.value) {
      socket.value.close()
      socket.value = null
    }
  }
  
  function sendMessage(message) {
    if (socket.value && isConnected.value) {
      socket.value.send(JSON.stringify(message))
    }
  }
  
  return {
    socket, messages, isConnected,
    sendMessage
  }
})
```

**3. 自定义组合式函数与 store 配合**

```javascript
// composables/useAuth.js
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

export function useAuth() {
  const userStore = useUserStore()
  const router = useRouter()
  const { currentUser, token, isLoggedIn } = storeToRefs(userStore)
  
  const requireAuth = (callback) => {
    if (!isLoggedIn.value) {
      router.push('/login')
      return
    }
    callback()
  }
  
  const logout = async () => {
    await userStore.logout()
    router.push('/login')
  }
  
  const hasRole = (role) => {
    return currentUser.value?.role === role
  }
  
  return {
    user: currentUser,
    token,
    isLoggedIn,
    requireAuth,
    logout,
    hasRole
  }
}

// 在组件中使用
export default {
  setup() {
    const { user, isLoggedIn, logout, hasRole } = useAuth()
    
    return { user, isLoggedIn, logout, hasRole }
  }
}
```

**4. 使用 provide/inject 共享 store**

```javascript
// 父组件
import { provide } from 'vue'
import { useUserStore } from '@/stores/user'

export default {
  setup() {
    const userStore = useUserStore()
    
    // 提供给后代组件
    provide('userStore', userStore)
    
    return {}
  }
}

// 子组件
import { inject } from 'vue'

export default {
  setup() {
    const userStore = inject('userStore')
    
    return { userStore }
  }
}
```

**5. 动态 store 创建**

```javascript
import { defineStore } from 'pinia'

// 工厂函数创建动态 store
export function createDynamicStore(id, initialState) {
  return defineStore(id, {
    state: () => ({ ...initialState }),
    actions: {
      updateState(newState) {
        Object.assign(this, newState)
      }
    }
  })()
}

// 使用
const dynamicStore = createDynamicStore('dynamic-1', {
  data: [],
  loading: false
})
```

---

## 总结

### Pinia 知识体系总览

```
Pinia 状态管理
├── 核心概念
│   ├── State（状态）
│   ├── Getters（计算属性）
│   └── Actions（方法）
├── Store 定义方式
│   ├── Options Store（选项式）
│   └── Setup Store（组合式）
├── 核心特性
│   ├── $patch（批量修改）
│   ├── $reset（重置状态）
│   ├── $subscribe（订阅状态）
│   └── $onAction（订阅动作）
├── 高级特性
│   ├── Store 相互调用
│   ├── 组合式 Store
│   ├── 持久化存储
│   ├── 插件机制
│   └── SSR 支持
├── TypeScript 集成
│   ├── 类型自动推导
│   └── 完整类型标注
├── 测试调试
│   ├── 单元测试
│   └── DevTools 调试
└── 最佳实践
    ├── 项目结构组织
    ├── 性能优化
    └── 避免常见陷阱
```

### 难度分布

| 难度 | 题目数量 | 主要内容 |
|------|----------|----------|
| 基础 | 4 | 概念理解、安装使用、核心概念 |
| 中级 | 8 | Store 定义、State 管理、Getters/Actions、TypeScript、调试、项目结构 |
| 高级 | 13 | 工作原理、Vuex 迁移、组合式 Store、插件、SSR、性能优化、实战场景 |

### 学习建议

1. **入门阶段**：先掌握基础概念，理解 State、Getters、Actions 的作用
2. **进阶阶段**：学习两种 Store 定义方式，掌握 TypeScript 集成
3. **高级阶段**：深入理解工作原理，学习插件开发和 SSR 应用
4. **实战阶段**：通过完整项目练习，掌握最佳实践和性能优化

---

> 本文档持续更新中，如有疑问或建议，欢迎交流讨论。
