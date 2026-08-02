# Vue3 响应式原理深度解析

> 本文档系统阐述 Vue3 响应式系统的核心实现机制，涵盖 Proxy 代理、依赖收集与追踪、变更检测、reactive/ref/computed/watch 的内部工作原理，并与 Vue2 响应式系统进行深度对比。包含代码示例、流程图与核心原理说明，适合深入理解 Vue3 响应式设计。

---

## 目录

- [Vue3 响应式原理深度解析](#vue3-响应式原理深度解析)
  - [目录](#目录)
  - [一、响应式系统概述](#一响应式系统概述)
    - [1.1 什么是响应式](#11-什么是响应式)
    - [1.2 响应式的核心问题](#12-响应式的核心问题)
    - [1.3 Vue3 响应式架构](#13-vue3-响应式架构)
  - [二、Vue2 响应式原理回顾](#二vue2-响应式原理回顾)
    - [2.1 Object.defineProperty 方案](#21-objectdefineproperty-方案)
    - [2.2 Vue2 的局限性](#22-vue2-的局限性)
  - [三、Vue3 核心基础：Proxy](#三vue3-核心基础proxy)
    - [3.1 Proxy 基础](#31-proxy-基础)
    - [3.2 Reflect 的作用](#32-reflect-的作用)
    - [3.3 Proxy vs defineProperty](#33-proxy-vs-defineproperty)
  - [四、依赖收集与触发更新](#四依赖收集与触发更新)
    - [4.1 核心数据结构](#41-核心数据结构)
    - [4.2 track 依赖收集](#42-track-依赖收集)
    - [4.3 trigger 触发更新](#43-trigger-触发更新)
    - [4.4 完整流程图](#44-完整流程图)
  - [五、reactive 实现原理](#五reactive-实现原理)
    - [5.1 reactive 简易实现](#51-reactive-简易实现)
    - [5.2 嵌套对象代理](#52-嵌套对象代理)
    - [5.3 数组处理](#53-数组处理)
    - [5.4 集合类型处理](#54-集合类型处理)
    - [5.5 代理缓存 proxyMap](#55-代理缓存-proxymap)
  - [六、ref 实现原理](#六ref-实现原理)
    - [6.1 ref 简易实现](#61-ref-简易实现)
    - [6.2 ref 与 reactive 的关系](#62-ref-与-reactive-的关系)
    - [6.3 模板自动解包](#63-模板自动解包)

---

## 一、响应式系统概述

### 1.1 什么是响应式

**响应式（Reactivity）** 是指：当数据发生变化时，依赖该数据的逻辑（如视图渲染、计算属性、watch 回调）能够自动更新。

```javascript
// 响应式的直观表现
const count = reactive({ value: 0 })

// 注册一个副作用：依赖 count.value
effect(() => {
  console.log('count 是:', count.value)  // 初始输出：count 是: 0
})

// 修改数据，副作用自动重新执行
count.value = 1  // 自动输出：count 是: 1
```

### 1.2 响应式的核心问题

实现响应式需解决三个核心问题：

| 问题 | 说明 | 解决方案 |
| --- | --- | --- |
| **① 数据劫持** | 如何感知数据被读取/修改？ | Proxy / Object.defineProperty |
| **② 依赖收集** | 如何知道"谁"依赖了"哪个数据"？ | track：读取时记录当前 effect |
| **③ 派发更新** | 数据变化时如何通知依赖重新执行？ | trigger：修改时执行记录的 effect |

### 1.3 Vue3 响应式架构

```
┌──────────────────────────────────────────────────────────┐
│                    Vue3 响应式系统架构                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  应用层 API（用户使用）                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ reactive │  │   ref    │  │ computed │  │  watch   │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
│       │             │             │             │        │
│       └─────┬───────┴─────┬───────┘             │        │
│             │             │                     │        │
│             ▼             ▼                     │        │
│  核心机制层                                          │    │
│  ┌──────────────────────────────┐                 │      │
│  │   代理层 Proxy + Reflect     │                 │      │
│  │  (get → track, set → trigger)│                 │      │
│  └──────────────┬───────────────┘                 │      │
│                 │                                  │      │
│                 ▼                                  ▼      │
│  ┌──────────────────────────┐    ┌────────────────────┐  │
│  │  依赖存储 targetMap      │    │  副作用管理 effect  │  │
│  │  (WeakMap → Map → Set)   │◀──▶│  (ReactiveEffect)  │  │
│  └──────────────────────────┘    └────────────────────┘  │
│                                          │                │
│                                          ▼                │
│                                 ┌──────────────────┐      │
│                                 │  调度器 scheduler │      │
│                                 │  (异步批量执行)   │      │
│                                 └──────────────────┘      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 二、Vue2 响应式原理回顾

### 2.1 Object.defineProperty 方案

Vue2 通过 `Object.defineProperty` 将对象属性转为 getter/setter：

```javascript
// Vue2 响应式核心简化实现
let activeEffect = null

function defineReactive(obj, key, val) {
  const dep = new Dep()  // 每个属性一个 Dep（依赖收集器）
  
  Object.defineProperty(obj, key, {
    enumerable: true,
    configurable: true,
    get() {
      console.log(`读取 ${key}`)
      dep.depend()         // 收集依赖：把 activeEffect 加入 dep
      return val
    },
    set(newVal) {
      if (newVal === val) return
      console.log(`修改 ${key}: ${val} → ${newVal}`)
      val = newVal
      dep.notify()         // 派发更新：通知所有依赖重新执行
    }
  })
}

// Dep：依赖管理器
class Dep {
  constructor() {
    this.subs = []         // 订阅者列表（Watcher 实例）
  }
  depend() {
    if (activeEffect) {
      this.subs.push(activeEffect)
    }
  }
  notify() {
    this.subs.forEach(watcher => watcher.update())
  }
}

// 将对象所有属性转为响应式
function observe(obj) {
  Object.keys(obj).forEach(key => {
    defineReactive(obj, key, obj[key])
  })
}

// 使用
const state = { count: 0, name: '张三' }
observe(state)

activeEffect = () => { console.log('count 变了:', state.count) }
state.count        // 触发 get，收集 activeEffect
state.count = 1    // 触发 set，执行 activeEffect → 输出 "count 变了: 1"
```

**Vue2 响应式流程**：

```
数据初始化
   │
   ▼
observe(obj) 遍历所有属性
   │
   ▼
defineReactive 为每个属性定义 get/set
   │
   ▼
组件渲染时创建 Watcher，设置 activeEffect = watcher
   │
   ▼
渲染读取数据 → 触发 get → dep.depend() 收集 Watcher
   │
   ▼
数据修改 → 触发 set → dep.notify() 通知所有 Watcher
   │
   ▼
Watcher.update() → 异步队列 → 重新渲染
```

### 2.2 Vue2 的局限性

| 局限 | 说明 | 解决方案 |
| --- | --- | --- |
| **无法检测新增/删除属性** | `obj.newKey = 1` 不触发响应式 | `Vue.set()` / `Vue.delete()` |
| **无法监听数组索引与 length** | `arr[0] = x`、`arr.length = 0` 不触发 | 重写 7 个数组方法 + `$set` |
| **深度监听需递归遍历** | 初始化时递归整个对象，性能差 | 初始化慢 |
| **无法监听 Map/Set/WeakMap** | 仅支持普通对象 | 不支持集合类型 |
| **每个属性一个 Dep** | 对象大时 Dep 数量多，内存开销大 | 内存占用高 |
| **无法监听属性的存在性** | 新增属性无 getter/setter | `Vue.set` |

**新增属性问题示例**：

```javascript
// Vue2 新增属性不响应式
const vm = new Vue({
  data: {
    user: { name: '张三' }
  }
})

vm.user.age = 25        // ❌ 视图不更新（age 没有 getter/setter）
Vue.set(vm.user, 'age', 25)  // ✅ 用 Vue.set 才响应式
this.$set(this.user, 'age', 25)  // ✅ 组件内用 $set
```

**数组问题示例**：

```javascript
// Vue2 数组监听问题
const vm = new Vue({
  data: {
    list: [1, 2, 3]
  }
})

vm.list[0] = 99         // ❌ 不响应式（索引赋值）
vm.list.length = 0      // ❌ 不响应式（修改 length）
vm.list.push(4)         // ✅ 响应式（重写了 push）
Vue.set(vm.list, 0, 99) // ✅ 用 $set
```

Vue2 通过**重写数组的 7 个方法**（push/pop/shift/unshift/splice/sort/reverse）来实现数组响应式：

```javascript
// Vue2 数组方法重写（简化）
const arrayProto = Array.prototype
const arrayMethods = Object.create(arrayProto)
;['push', 'pop', 'shift', 'unshift', 'splice', 'sort', 'reverse'].forEach(method => {
  const original = arrayProto[method]
  arrayMethods[method] = function (...args) {
    const result = original.apply(this, args)
    // 通知依赖更新
    const ob = this.__ob__
    ob.dep.notify()
    // 新增的元素也要转为响应式
    const inserted = method === 'push' || method === 'unshift' ? args : 
                     method === 'splice' ? args.slice(2) : []
    if (inserted.length) ob.observeArray(inserted)
    return result
  }
})
```

---

## 三、Vue3 核心基础：Proxy

### 3.1 Proxy 基础

**Proxy** 是 ES6 引入的元编程能力，可以创建一个对象的代理，拦截对其的基本操作（get/set/has/deleteProperty 等）。

```javascript
// Proxy 基础用法
const target = { name: '张三', age: 25 }

const proxy = new Proxy(target, {
  // 拦截读取
  get(obj, key, receiver) {
    console.log(`读取 ${String(key)}`)
    return Reflect.get(obj, key, receiver)
  },
  // 拦截设置
  set(obj, key, value, receiver) {
    console.log(`设置 ${String(key)} = ${value}`)
    return Reflect.set(obj, key, value, receiver)  // 返回布尔值表示成功
  },
  // 拦截 in 操作符
  has(obj, key) {
    console.log(`检查 ${String(key)} 是否存在`)
    return Reflect.has(obj, key)
  },
  // 拦截 delete
  deleteProperty(obj, key) {
    console.log(`删除 ${String(key)}`)
    return Reflect.deleteProperty(obj, key)
  }
})

proxy.name          // 输出 "读取 name"，返回 '张三'
proxy.age = 26      // 输出 "设置 age = 26"
'name' in proxy     // 输出 "检查 name 是否存在"，返回 true
delete proxy.name   // 输出 "删除 name"
```

**Proxy 的关键优势**：

| 优势 | 说明 |
| --- | --- |
| **整体代理** | 代理整个对象，而非每个属性 |
| **支持新增属性** | 新增属性自动被拦截（无需 `Vue.set`） |
| **支持数组** | 索引赋值、length 修改、数组方法均能拦截 |
| **支持集合** | Map/Set/WeakMap/WeakSet 可代理 |
| **13 种拦截器** | get/set/has/deleteProperty/ownKeys/apply 等 |
| **惰性代理** | 访问嵌套属性时才递归代理（性能优） |

### 3.2 Reflect 的作用

**Reflect** 与 Proxy 配套使用，提供与拦截器同名的静态方法，用于执行默认行为。

```javascript
// Reflect 的作用：执行对象的默认操作
const obj = { name: '张三', age: 25 }

// 等价于 obj.name
Reflect.get(obj, 'name')        // '张三'

// 等价于 obj.name = '李四'，返回布尔值表示成功
Reflect.set(obj, 'name', '李四') // true

// 等价于 'name' in obj
Reflect.has(obj, 'name')        // true

// 等价于 delete obj.name，返回布尔值
Reflect.deleteProperty(obj, 'name') // true
```

**为什么 Proxy 必须配合 Reflect？**

```javascript
const obj = { name: '张三' }

const proxy = new Proxy(obj, {
  get(target, key, receiver) {
    // ❌ 错误写法：直接 target[key]
    // return target[key]  // 在某些场景（如继承）会丢失 this 指向
    
    // ✅ 正确写法：用 Reflect 传递 receiver
    return Reflect.get(target, key, receiver)
  }
})

// receiver 的作用：保证 getter 中的 this 指向 proxy
const parent = { get value() { return this._v } }
const child = Object.create(parent)
child._v = 10

const proxyChild = new Proxy(child, {
  get(target, key, receiver) {
    // Reflect.get 传递 receiver，getter 中 this 是 receiver（proxyChild）
    return Reflect.get(target, key, receiver)
  }
})

console.log(proxyChild.value)  // 10（正确，this 指向 proxyChild）
```

### 3.3 Proxy vs defineProperty

| 维度 | Object.defineProperty | Proxy |
| --- | --- | --- |
| **代理范围** | 单个属性 | 整个对象 |
| **新增属性** | ❌ 需 `Vue.set` | ✅ 自动响应 |
| **删除属性** | ❌ 需 `Vue.delete` | ✅ deleteProperty 拦截 |
| **数组监听** | ❌ 索引/length 失效 | ✅ 全部支持 |
| **集合类型** | ❌ 不支持 Map/Set | ✅ 支持 |
| **深度监听** | 初始化递归（慢） | 访问时递归（惰性，快） |
| **性能** | 大对象初始化慢 | 初始化快，访问时按需代理 |
| **兼容性** | IE9+ | ES6（不支持 IE） |
| **拦截器数量** | 仅 get/set | 13 种 |

---

## 四、依赖收集与触发更新

### 4.1 核心数据结构

Vue3 用三层结构存储依赖关系：`targetMap → depsMap → dep`

```
targetMap (WeakMap)
│
├─ target1 (object) → depsMap (Map)
│                       ├─ key1 → dep (Set of effects)
│                       ├─ key2 → dep (Set of effects)
│                       └─ key3 → dep (Set of effects)
│
├─ target2 (object) → depsMap (Map)
│                       ├─ key1 → dep (Set of effects)
│                       └─ ITERATE_KEY → dep (Set of effects)  ← 数组/集合迭代
│
└─ target3 (object) → depsMap (Map)
                        └─ ... 
```

```typescript
// 核心数据结构定义
const targetMap = new WeakMap<object, Map<any, Set<ReactiveEffect>>>()

// targetMap 结构：
// WeakMap {
//   [target对象]: Map {
//     [属性key]: Set { effect1, effect2, ... }
//   }
// }
```

**为什么用 WeakMap？**

```javascript
// WeakMap 的 key 是弱引用，不影响垃圾回收
const targetMap = new WeakMap()

let obj = { name: '张三' }
targetMap.set(obj, new Map())

obj = null  // obj 被回收后，WeakMap 中对应的 entry 也会被自动清理
// 避免 targetMap 持续膨胀导致内存泄漏
```

### 4.2 track 依赖收集

**track**：在 getter 中调用，记录"当前 effect 依赖了 target 的 key"。

```typescript
let activeEffect: ReactiveEffect | null = null

/**
 * 依赖收集
 * @param target 原始对象
 * @param key 属性键
 */
function track(target: object, key: unknown) {
  if (!activeEffect) return  // 没有正在执行的 effect，无需收集
  
  // 第一层：target → depsMap
  let depsMap = targetMap.get(target)
  if (!depsMap) {
    targetMap.set(target, (depsMap = new Map()))
  }
  
  // 第二层：key → dep
  let dep = depsMap.get(key)
  if (!dep) {
    depsMap.set(key, (dep = new Set()))
  }
  
  // 第三层：将当前 effect 加入 dep
  dep.add(activeEffect)
  
  // 同时让 effect 记录它所在的 dep（便于清理）
  activeEffect.deps.push(dep)
}

// 简化的 ReactiveEffect
class ReactiveEffect {
  deps: Set<ReactiveEffect>[] = []  // 此 effect 被哪些 dep 收集
  
  constructor(private fn: () => void) {}
  
  run() {
    activeEffect = this
    try {
      return this.fn()  // 执行时触发 get → track
    } finally {
      activeEffect = null
    }
  }
}
```

### 4.3 trigger 触发更新

**trigger**：在 setter 中调用，找到依赖 target.key 的所有 effect 并执行。

```typescript
/**
 * 触发更新
 * @param target 原始对象
 * @param key 属性键
 * @param type 操作类型（SET/ADD/DELETE）
 */
function trigger(target: object, key: unknown, type: TriggerOpTypes) {
  const depsMap = targetMap.get(target)
  if (!depsMap) return  // 没有被 track 过
  
  // 收集需要执行的 effect
  const effects = new Set<ReactiveEffect>()
  
  // 1. 收集 key 对应的 dep
  const dep = depsMap.get(key)
  if (dep) {
    dep.forEach(effect => effects.add(effect))
  }
  
  // 2. 新增/删除操作，还需触发迭代相关依赖
  if (type === 'ADD' || type === 'DELETE') {
    const iterateEffects = depsMap.get(ITERATE_KEY)
    if (iterateEffects) {
      iterateEffects.forEach(effect => effects.add(effect))
    }
    
    // 数组新增元素，触发 length 依赖
    if (Array.isArray(target) && type === 'ADD') {
      const lengthEffects = depsMap.get('length')
      if (lengthEffects) {
        lengthEffects.forEach(effect => effects.add(effect))
      }
    }
  }
  
  // 3. 执行所有 effect
  effects.forEach(effect => {
    // 有 scheduler 则走调度器（异步批量），否则直接执行
    if (effect.scheduler) {
      effect.scheduler()
    } else {
      effect.run()
    }
  })
}
```

### 4.4 完整流程图

```
                     响应式数据读取与修改流程
                     
┌─────────────────────────────────────────────────────────────────┐
│  effect(() => {                                                  │
│    console.log(state.count)   ← 读取触发 get                     │
│  })                                                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ 1. 设置 activeEffect = 当前 effect
                           ▼
              ┌────────────────────────┐
              │  执行 effect 函数       │
              └────────────┬───────────┘
                           │
                           │ 2. 读取 state.count 触发 Proxy.get
                           ▼
              ┌────────────────────────┐
              │  Proxy.get 拦截        │
              │  调用 track(target,key)│
              └────────────┬───────────┘
                           │
                           │ 3. 依赖收集
                           ▼
              ┌────────────────────────┐
              │  targetMap 结构：       │
              │  WeakMap {              │
              │    [target]: Map {      │
              │      [key]: Set {       │
              │        activeEffect ◀───┼── 加入当前 effect
              │      }                  │
              │    }                    │
              │  }                      │
              └────────────────────────┘

───────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────────┐
│  state.count = 1    ← 修改触发 set                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ 1. Proxy.set 拦截
                           ▼
              ┌────────────────────────┐
              │  调用 trigger(target,   │
              │    key, 'SET')         │
              └────────────┬───────────┘
                           │
                           │ 2. 查找依赖
                           ▼
              ┌────────────────────────┐
              │  targetMap.get(target) │
              │    .get(key)           │
              │  → Set { effect1, ...}│
              └────────────┬───────────┘
                           │
                           │ 3. 遍历执行
                           ▼
              ┌────────────────────────┐
              │  effects.forEach(       │
              │    effect.run()         │
              │  )                      │
              │  → 重新执行 effect      │
              │  → 视图更新             │
              └────────────────────────┘
```

---

## 五、reactive 实现原理

### 5.1 reactive 简易实现

```typescript
import { track, trigger } from './effect'

// 代理缓存：避免重复代理同一对象
const reactiveMap = new WeakMap<object, any>()

/**
 * 创建响应式对象
 * @param target 原始对象
 */
function reactive<T extends object>(target: T): T {
  // 非对象直接返回
  if (typeof target !== 'object' || target === null) {
    return target
  }
  
  // 已存在代理，直接返回（缓存）
  const existingProxy = reactiveMap.get(target)
  if (existingProxy) {
    return existingProxy
  }
  
  // 创建 Proxy
  const proxy = new Proxy(target, {
    get(target: T, key: string | symbol, receiver: unknown) {
      // 特殊属性处理
      if (key === '__isReactive') return true
      
      // 数组特殊处理（后续详述）
      if (Array.isArray(target)) {
        // 重写数组方法...
      }
      
      const result = Reflect.get(target, key, receiver)
      
      // 依赖收集
      track(target, key)
      
      // 嵌套对象惰性代理（性能优化）
      if (typeof result === 'object' && result !== null) {
        return reactive(result)
      }
      
      return result
    },
    
    set(target: T, key: string | symbol, value: unknown, receiver: unknown) {
      const oldValue = (target as any)[key]
      
      // 判断是新增还是修改
      const hadKey = Array.isArray(target) && isIntegerKey(key)
        ? Number(key) < target.length
        : Object.prototype.hasOwnProperty.call(target, key)
      
      const result = Reflect.set(target, key, value, receiver)
      
      // 确保 receiver 是 target 的代理（避免原型链触发）
      if (target === (receiver as any).__raw || receiver === target) {
        if (!hadKey) {
          trigger(target, key, 'ADD')
        } else if (value !== oldValue && (value === value || oldValue === oldValue)) {
          trigger(target, key, 'SET')
        }
      }
      
      return result
    },
    
    deleteProperty(target: T, key: string | symbol) {
      const hadKey = Object.prototype.hasOwnProperty.call(target, key)
      const result = Reflect.deleteProperty(target, key)
      if (result && hadKey) {
        trigger(target, key, 'DELETE')
      }
      return result
    },
    
    has(target: T, key: string | symbol) {
      const result = Reflect.has(target, key)
      track(target, key)
      return result
    },
    
    ownKeys(target: T) {
      track(target, Array.isArray(target) ? 'length' : ITERATE_KEY)
      return Reflect.ownKeys(target)
    }
  })
  
  // 缓存代理
  reactiveMap.set(target, proxy)
  
  return proxy
}

const ITERATE_KEY = Symbol('iterate')
```

### 5.2 嵌套对象代理

Vue3 采用**惰性代理**（lazy）：只有访问到嵌套对象时才递归代理，而非初始化时一次性代理整个对象。

```typescript
// get 中嵌套对象处理
get(target, key, receiver) {
  // ...
  const result = Reflect.get(target, key, receiver)
  track(target, key)
  
  // ✅ 惰性代理：访问到才代理
  if (typeof result === 'object' && result !== null) {
    return reactive(result)
  }
  
  return result
}
```

**Vue2 vs Vue3 深度响应式对比**：

```
Vue2（初始化时递归）：
  observe(state)
    ├─ defineReactive(state, 'user')
    │   └─ observe(state.user)  ← 初始化就递归
    │       ├─ defineReactive(state.user, 'name')
    │       └─ defineReactive(state.user, 'address')
    │           └─ observe(state.user.address)  ← 继续递归
  缺点：大对象初始化慢

Vue3（访问时递归）：
  reactive(state)
    └─ 创建 Proxy（不递归）
  
  state.user          ← 触发 get，返回 reactive(state.user)
    └─ 创建 Proxy
  state.user.address  ← 触发 get，返回 reactive(state.user.address)
      └─ 创建 Proxy
  优点：按需代理，初始化快
```

### 5.3 数组处理

Vue3 的 Proxy 能直接拦截数组操作，但仍需对部分方法特殊处理：

```typescript
// 数组方法分类
const arrayInstrumentations: Record<string, Function> = {}

// 1. 查找类方法（includes/indexOf/lastIndexOf）：避免查找失败
;['includes', 'indexOf', 'lastIndexOf'].forEach(method => {
  arrayInstrumentations[method] = function (...args: any[]) {
    const arr = (this as any).__raw  // 原始数组
    const res = arr[method](...args)
    
    if (res === -1 || res === false) {
      // 在原始数组找不到，再到代理数组找（响应式对象场景）
      return arr[method](...args.map(item => 
        item && item.__raw ? item.__raw : item
      ))
    }
    return res
  }
})

// 2. 变更类方法（push/pop/shift/unshift/splice）：避免 length 触发死循环
;['push', 'pop', 'shift', 'unshift', 'splice'].forEach(method => {
  arrayInstrumentations[method] = function (...args: any[]) {
    pauseTracking()  // 暂停依赖收集
    const res = Array.prototype[method].apply(this, args)
    resetTracking()  // 恢复依赖收集
    return res
  }
})
```

**为什么 push 要暂停依赖收集？**

```javascript
// push 内部会修改 length，触发 trigger
// 若不暂停，effect 中 push 会导致 effect 重复执行（死循环）
effect(() => {
  arr.push(1)  // push 修改 length → trigger → 重新执行 effect → 再 push...
})

// 暂停依赖收集后：push 期间不收集依赖，避免循环
```

### 5.4 集合类型处理

Map/Set/WeakMap/WeakSet 的方法依赖内部插槽（`[[SetData]]`），Proxy 拦截后会失效，需特殊处理：

```typescript
// 集合类型的自定义方法
const collectionMethods = {
  get(key) {
    const target = (this as any).__raw
    const had = target.has(key)
    track(target, key)
    if (had) {
      const result = target.get(key)
      return typeof result === 'object' ? reactive(result) : result
    }
    return result
  },
  set(key, value) {
    const target = (this as any).__raw
    const had = target.has(key)
    const oldValue = target.get(key)
    // value 解包（若是响应式对象，存原始值）
    const rawValue = value && value.__raw ? value.__raw : value
    target.set(key, rawValue)
    if (!had) {
      trigger(target, key, 'ADD')
    } else if (oldValue !== value) {
      trigger(target, key, 'SET')
    }
    return this
  },
  // add/delete/forEach/iterate 类似处理...
}

// 集合类型代理工厂
function collectionReactive(target: Map<any, any> | Set<any>) {
  return new Proxy(target, {
    get(target, key, receiver) {
      // 自定义方法优先
      if (key in collectionMethods) {
        return collectionMethods[key]
      }
      const result = Reflect.get(target, key, receiver)
      return typeof result === 'function' ? result.bind(target) : result
    }
  })
}
```

### 5.5 代理缓存 proxyMap

```typescript
// 三种响应式代理的缓存
const reactiveMap = new WeakMap()       // reactive
const shallowReactiveMap = new WeakMap() // shallowReactive
const readonlyMap = new WeakMap()        // readonly
const shallowReadonlyMap = new WeakMap() // shallowReadonly

function createReactiveObject(target, isReadonly, shallow, handlers) {
  const proxyMap = isReadonly
    ? (shallow ? shallowReadonlyMap : readonlyMap)
    : (shallow ? shallowReactiveMap : reactiveMap)
  
  // 已存在代理直接返回
  const existingProxy = proxyMap.get(target)
  if (existingProxy) return existingProxy
  
  const proxy = new Proxy(target, handlers)
  proxyMap.set(target, proxy)
  return proxy
}
```

**缓存的作用**：
1. **避免重复代理**：同一对象多次 reactive 只创建一次 Proxy
2. **保证一致性**：同一对象始终返回同一个代理
3. **性能优化**：减少 Proxy 创建开销

---

## 六、ref 实现原理

### 6.1 ref 简易实现

`ref` 通过对象访问器（get/set）实现，包装基本类型为对象：

```typescript
import { track, trigger } from './effect'

interface Ref<T> {
  value: T
  __isRef: true
}

/**
 * 创建 ref
 * @param value 初始值
 */
function ref<T>(value: T): Ref<T> {
  // 若已是 ref 直接返回
  if (isRef(value)) return value as Ref<T>
  
  return new RefImpl(value)
}

class RefImpl<T> {
  private _value: T
  private _rawValue: T
  public __isRef = true
  public dep: Set<ReactiveEffect> = new Set()  // ref 自己维护 dep（不进 targetMap）
  
  constructor(value: T) {
    this._rawValue = value
    // 对象类型用 reactive 包裹
    this._value = isObject(value) ? reactive(value) : value
  }
  
  get value(): T {
    // 依赖收集（ref 用自己的 dep，而非 targetMap）
    trackRefValue(this)
    return this._value
  }
  
  set value(newVal: T) {
    if (newVal !== this._rawValue) {
      this._rawValue = newVal
      this._value = isObject(newVal) ? reactive(newVal) : newVal
      // 触发更新
      triggerRefValue(this)
    }
  }
}

function trackRefValue(ref: RefImpl<any>) {
  if (activeEffect) {
    ref.dep.add(activeEffect)
    activeEffect.deps.push(ref.dep)
  }
}

function triggerRefValue(ref: RefImpl<any>) {
  ref.dep.forEach(effect => {
    if (effect.scheduler) {
      effect.scheduler()
    } else {
      effect.run()
    }
  })
}

const isObject = (v: unknown): v is object => 
  typeof v === 'object' && v !== null
```

### 6.2 ref 与 reactive 的关系

```
┌─────────────────────────────────────────────────────┐
│              ref 与 reactive 对比                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ref(0)                                             │
│  ┌─────────────────────┐                            │
│  │ RefImpl {           │                            │
│  │   _value: 0,        │ ← 基本类型直接存           │
│  │   dep: Set[effect]  │ ← 自己维护 dep             │
│  │   get value()       │ → track(dep)              │
│  │   set value(v)      │ → trigger(dep)            │
│  │ }                   │                            │
│  └─────────────────────┘                            │
│                                                     │
│  ref({ name: '张三' })                              │
│  ┌─────────────────────┐                            │
│  │ RefImpl {           │                            │
│  │   _value: Proxy{}   │ ← 对象类型用 reactive 包裹 │
│  │   dep: Set[effect]  │                            │
│  │   get value()       │ → track(dep) + 返回 Proxy │
│  │   set value(v)      │ → trigger(dep)            │
│  │ }                   │                            │
│  └─────────────────────┘                            │
│                                                     │
│  reactive({ name: '张三' })                         │
│  ┌─────────────────────┐                            │
│  │ Proxy {             │                            │
│  │   get → track       │ ← 依赖进 targetMap         │
│  │   set → trigger     │                            │
│  │ }                   │                            │
│  └─────────────────────┘                            │
└─────────────────────────────────────────────────────┘
```

**核心差异**：
- **ref**：通过 `value` 属性的 get/set，依赖存在 ref 自己的 `dep`（Set）
- **reactive**：通过 Proxy 拦截，依赖存在全局 `targetMap`
- **ref 包对象**：内部用 reactive 包裹，但 ref 的 `.value` 替换仍触发 ref 的 dep

### 6.3 模板自动解包

模板中 ref 自动解包（无需 `.value`）：

```typescript
// 编译器自动处理：模板中的 ref 变量自动加 .value
// 源码：
<template>{{ count }}</template>
<script setup>
const count = ref(0)  // RefImpl
</script>

// 编译后：
render(_ctx) {
  return _ctx.count.value  // 自动加 .value
}
// 但模板中直接写 {{ count }} 也行，编译器会自动解包
```

**自动解包的实现**：组件 setup 返回的对象会被 `proxyRefs` 包裹：

```typescript
/**
 * proxyRefs：自动解包 ref
 * setup 返回的对象会经过此处理
 */
function proxyRefs(objectWithRefs) {
  return new Proxy(objectWithRefs, {
    get(target, key, receiver) {
      const result = Reflect.get(target, key, receiver)
      // 如果是 ref，返回 .value
      return isRef(result) ? result.value : result
    },
    set(target, key, value, receiver) {
      const oldValue = target[key]
      if (isRef(oldValue) && !isRef(value)) {
        // 赋值给 ref 属性，自动设置 .value
        oldValue.value = value
        return true
      }
      return Reflect.set(target, key, value, receiver)
    }
  })
}

// 示例
const count = ref(0)
const state = proxyRefs({ count })
console.log(state.count)   // 0（自动解包）
state.count = 1            // 等价于 count.value = 1
```

---

## 七、computed 实现原理

### 7.1 惰性求值与缓存

**computed** 的核心特性是**惰性求值**与**缓存**：
- **惰性求值**：只有访问 `.value` 时才计算，不访问不计算
- **缓存**：依赖不变时返回缓存值，依赖变化才重新计算

```typescript
const count = ref(0)
const double = computed(() => count.value * 2)

// 此时 computed 内部不执行（惰性）
console.log(double.value)  // 0（首次访问，执行计算，缓存结果）
console.log(double.value)  // 0（再次访问，返回缓存，不执行）

count.value = 1            // 依赖变化，标记为脏
console.log(double.value)  // 2（重新计算，缓存）
```

### 7.2 computed 简易实现

computed 本质是一个带缓存的特殊 effect：

```typescript
import { ReactiveEffect } from './effect'

class ComputedRefImpl<T> {
  public dep: Set<ReactiveEffect> = new Set()  // 依赖此 computed 的 effect
  private _value!: T                            // 缓存值
  private _dirty: boolean = true                // 脏标记：true 表示需重新计算
  public effect: ReactiveEffect                  // 内部 effect
  
  public readonly __isRef = true                 // computed 也是 ref
  
  constructor(getter: () => T, private setter: (v: T) => void) {
    // 创建 effect，但配置 scheduler（不立即执行，而是标记脏）
    this.effect = new ReactiveEffect(getter, () => {
      // scheduler：依赖变化时不立即计算，只标记为脏
      if (!this._dirty) {
        this._dirty = true
        // 通知依赖此 computed 的 effect 重新执行
        triggerRefValue(this)
      }
    })
  }
  
  get value(): T {
    // 依赖收集：让依赖此 computed 的 effect 被收集
    trackRefValue(this)
    
    // 脏标记为 true，需重新计算
    if (this._dirty) {
      this._dirty = false
      // 执行 effect.run()，重新计算并更新 _value
      this._value = this.effect.run()
    }
    return this._value
  }
  
  set value(newVal: T) {
    this.setter(newVal)
  }
}

function computed<T>(getter: () => T): ComputedRefImpl<T>
function computed<T>(options: { get: () => T; set: (v: T) => void }): ComputedRefImpl<T>
function computed<T>(getterOrOptions: any): ComputedRefImpl<T> {
  let getter: () => T
  let setter: (v: T) => void
  
  if (typeof getterOrOptions === 'function') {
    getter = getterOrOptions
    setter = () => {
      console.warn('Write operation failed: computed value is readonly')
    }
  } else {
    getter = getterOrOptions.get
    setter = getterOrOptions.set
  }
  
  return new ComputedRefImpl(getter, setter)
}
```

### 7.3 脏标记机制

computed 的核心是"**依赖变化不立即计算，只标记脏；下次访问时若脏才计算**"：

```
                    computed 缓存机制
                    
① 初始化
   ┌─────────────────────┐
   │ computed(() => {     │
   │   return count*2     │ ← getter 未执行
   │ })                   │
   │ _dirty = true        │ ← 初始为脏
   └─────────────────────┘

② 首次访问 .value
   ┌─────────────────────┐
   │ 读取 _value          │
   │ _dirty=true → 执行   │
   │   effect.run()       │ ← 执行 getter，count 被追踪
   │   _value = 0         │ ← 缓存结果
   │   _dirty = false     │ ← 标记干净
   └─────────────────────┘

③ 再次访问 .value
   ┌─────────────────────┐
   │ _dirty=false         │
   │ → 直接返回 _value=0  │ ← 命中缓存，不执行
   └─────────────────────┘

④ count 变化
   ┌─────────────────────┐
   │ count 触发 trigger   │
   │ → computed 的 effect  │
   │   scheduler 执行     │
   │ → _dirty = true      │ ← 仅标记脏，不计算
   │ → 通知依赖它的 effect │
   └─────────────────────┘

⑤ 再次访问 .value
   ┌─────────────────────┐
   │ _dirty=true → 执行   │
   │   effect.run()       │ ← 重新计算
   │   _value = 2         │ ← 更新缓存
   │   _dirty = false     │
   └─────────────────────┘
```

**computed 的 effect 与普通 effect 区别**：
- **普通 effect**：依赖变化立即执行 `run()`
- **computed 的 effect**：依赖变化执行 `scheduler()`（仅标记脏），不立即计算

---

## 八、watch 与 watchEffect 实现原理

### 8.1 effect 与 ReactiveEffect

`ReactiveEffect` 是响应式系统的核心，watch/watchEffect/computed 都基于它：

```typescript
let activeEffect: ReactiveEffect | null = null
const effectStack: ReactiveEffect[] = []  // effect 栈（支持嵌套）

class ReactiveEffect<T = any> {
  active: boolean = true
  deps: Set<ReactiveEffect>[] = []  // 此 effect 被哪些 dep 收集
  scheduler?: () => void            // 调度器（有则用，无则直接 run）
  
  // 记录父级 effect（用于嵌套）
  parent: ReactiveEffect | null = null
  
  constructor(private fn: () => T, scheduler?: () => void) {
    this.scheduler = scheduler
  }
  
  run(): T {
    // 非活跃状态直接执行（不收集依赖）
    if (!this.active) return this.fn()
    
    // 防止重复入栈（已激活则直接返回）
    let parent: ReactiveEffect | null = activeEffect
    try {
      this.parent = parent
      activeEffect = this
      effectStack.push(this)
      
      // 清理旧依赖（避免分支切换导致的无效依赖）
      cleanup(this)
      
      return this.fn()  // 执行时触发 get → track
    } finally {
      effectStack.pop()
      activeEffect = effectStack[effectStack.length - 1] || null
      this.parent = null
    }
  }
  
  stop() {
    if (this.active) {
      cleanup(this)  // 清除所有依赖
      this.active = false
    }
  }
}

// 清理 effect 的所有依赖（分支切换优化）
function cleanup(effect: ReactiveEffect) {
  effect.deps.forEach(dep => dep.delete(effect))
  effect.deps.length = 0
}

// 创建 effect
function effect<T>(fn: () => T, options: { scheduler?: () => void } = {}) {
  const _effect = new ReactiveEffect(fn, options.scheduler)
  _effect.run()  // 立即执行一次
  return _effect
}
```

**分支切换（branching）问题与 cleanup**：

```javascript
// 分支切换：依赖会变化
const state = reactive({ flag: true, a: 1, b: 2 })

effect(() => {
  // flag 为 true 时依赖 flag + a
  // flag 为 false 时依赖 flag + b
  console.log(state.flag ? state.a : state.b)
})

// 初始：effect 依赖 { flag, a }
state.a = 10   // 触发 effect 重新执行

// 修改 flag 后，effect 应该只依赖 { flag, b }
state.flag = false
// 但若不 cleanup，effect 仍依赖 { flag, a, b }
// a 变化仍会触发 effect（无效触发）

// cleanup 解决：每次 run 前清空旧依赖，重新收集
```

### 8.2 watchEffect 实现

```typescript
import { ReactiveEffect } from './effect'
import { scheduler } from './scheduler'

interface WatchEffectOptions {
  flush?: 'pre' | 'post' | 'sync'  // 执行时机
  onTrack?: (e: any) => void       // 追踪调试
  onTrigger?: (e: any) => void     // 触发调试
}

/**
 * watchEffect：自动收集依赖，立即执行
 */
function watchEffect(effect: (onCleanup: (fn: () => void) => void) => void,
                    options: WatchEffectOptions = {}) {
  let cleanupFn: (() => void) | null = null
  
  // 注册清理函数
  const onCleanup = (fn: () => void) => {
    cleanupFn = fn
  }
  
  // 包装的 getter
  const getter = () => {
    // 执行前先清理上次的副作用
    if (cleanupFn) {
      cleanupFn()
      cleanupFn = null
    }
    effect(onCleanup)
  }
  
  // 创建 effect，配置调度器（控制执行时机）
  const _effect = new ReactiveEffect(getter, () => {
    // 调度器：根据 flush 选项决定执行时机
    if (options.flush === 'sync') {
      _effect.run()  // 同步执行
    } else {
      scheduler(_effect)  // 异步批量执行
    }
  })
  
  // 立即执行一次（收集依赖）
  _effect.run()
  
  // 返回停止函数
  return () => _effect.stop()
}
```

### 8.3 watch 实现

```typescript
import { ReactiveEffect } from './effect'

type WatchSource<T> = (() => T) | Ref<T> | { value: T }

interface WatchOptions {
  immediate?: boolean    // 立即执行
  deep?: boolean         // 深度侦听
  flush?: 'pre' | 'post' | 'sync'
  once?: boolean
}

/**
 * watch：侦听特定源，可获取新旧值
 */
function watch<T>(
  source: WatchSource<T> | WatchSource<T>[],
  cb: (newVal: T, oldVal: T, onCleanup: (fn: () => void) => void) => void,
  options: WatchOptions = {}
) {
  const { immediate, deep, flush = 'pre' } = options
  
  // ① 将 source 转为 getter 函数
  let getter: () => any
  if (isRef(source)) {
    getter = () => (source as Ref<T>).value
  } else if (isReactive(source)) {
    getter = () => source
    // reactive 默认深度
    if (!deep) console.warn('reactive source 应配合 deep')
  } else if (typeof source === 'function') {
    getter = source as () => T
  } else if (Array.isArray(source)) {
    // 多源：返回数组
    getter = () => source.map(s => 
      isRef(s) ? s.value : typeof s === 'function' ? s() : s
    )
  } else {
    getter = () => source
  }
  
  // ② 深度侦听：递归遍历收集所有嵌套依赖
  if (deep) {
    const baseGetter = getter
    getter = () => traverse(baseGetter())
  }
  
  // ③ 清理函数管理
  let cleanupFn: (() => void) | null = null
  const onCleanup = (fn: () => void) => {
    cleanupFn = fn
  }
  
  // ④ 旧值存储
  let oldValue: any = undefined
  
  // ⑤ 包装 job（watch 的回调执行）
  const job = () => {
    if (cleanupFn) {
      cleanupFn()
      cleanupFn = null
    }
    const newValue = _effect.run()
    if (deep || newValue !== oldValue || isObject(newValue)) {
      cb(newValue, oldValue, onCleanup)
      oldValue = newValue
    }
  }
  
  // ⑥ 创建 effect（不立即执行，仅配置调度器）
  const _effect = new ReactiveEffect(getter, 
    flush === 'sync' ? job : () => scheduler(job, flush)
  )
  
  // ⑦ 首次执行
  if (immediate) {
    job()  // 立即执行回调
  } else {
    oldValue = _effect.run()  // 仅收集依赖，存储旧值
  }
  
  // ⑧ 返回停止函数
  return () => _effect.stop()
}

// 深度遍历：触发所有嵌套属性的 get，收集深度依赖
function traverse(value: any, seen = new Set()) {
  if (!isObject(value) || seen.has(value)) return value
  seen.add(value)
  if (Array.isArray(value)) {
    for (let i = 0; i < value.length; i++) traverse(value[i], seen)
  } else {
    for (const key in value) traverse(value[key], seen)
  }
  return value
}
```

**watch vs watchEffect 原理对比**：

| 维度 | watch | watchEffect |
| --- | --- | --- |
| **依赖收集** | 通过 getter 显式指定 | 自动收集回调内依赖 |
| **执行时机** | 默认不立即执行（除非 immediate） | 默认立即执行 |
| **旧值** | ✅ 可获取 | ❌ 无法获取 |
| **实现** | getter + scheduler + 手动 job | effect + scheduler |

---

## 九、调度器 Scheduler

调度器负责**异步批量执行** effect，避免同步多次修改导致的重复渲染：

```typescript
// 调度器核心实现
const queue: (() => void)[] = []    // 任务队列
const resolvedPromise = Promise.resolve()
let isFlushing = false              // 是否正在刷新
let isFlushPending = false          // 是否有待处理的刷新

function nextTick<T>(fn?: () => T): Promise<T> {
  const p = resolvedPromise
  return fn ? p.then(fn) : p
}

/**
 * 将 job 加入队列，异步批量执行
 */
function queueJob(job: () => void) {
  // 去重：相同 job 只入队一次
  if (!queue.includes(job)) {
    queue.push(job)
  }
  queueFlush()
}

function queueFlush() {
  // 已有刷新任务在等待，无需重复
  if (!isFlushing && !isFlushPending) {
    isFlushPending = true
    // 微任务：Promise.then
    resolvedPromise.then(flushJobs)
  }
}

/**
 * 执行队列中的所有 job
 */
function flushJobs() {
  isFlushPending = false
  isFlushing = true
  
  // 排序：确保组件更新顺序（父组件先于子组件）
  // queue.sort((a, b) => a.id - b.id)
  
  try {
    for (let i = 0; i < queue.length; i++) {
      queue[i]()  // 执行 job
    }
  } finally {
    // 清空队列
    queue.length = 0
    isFlushing = false
  }
}

/**
 * watch 的调度入口
 */
function scheduler(job: () => void, flush: 'pre' | 'post' | 'sync') {
  if (flush === 'sync') {
    job()  // 同步执行
  } else if (flush === 'pre') {
    // 组件更新前执行（默认）
    queueJob(job)
  } else {
    // 'post'：组件更新后执行
    nextTick(() => job())
  }
}
```

**调度器解决的问题**：

```javascript
// 不用调度器：同步修改会触发多次 effect
const state = reactive({ a: 1, b: 2 })

effect(() => {
  console.log('渲染', state.a, state.b)
})

state.a = 10   // 触发一次 effect
state.b = 20   // 又触发一次 effect
// 输出两次："渲染 10 2" 和 "渲染 10 20"
// 但中间状态 "10 2" 是无效的，浪费一次渲染

// 用调度器：合并到微任务，只渲染最终状态
state.a = 10   // job 入队
state.b = 20   // job 已在队列，不入队
// 微任务执行：只输出一次 "渲染 10 20"
```

```
同步代码阶段：
  state.a = 10  → queueJob(job) → 队列: [job]
  state.b = 20  → queueJob(job) → 队列: [job]（去重）
  console.log('end')
                  │
                  ▼
微任务阶段（同步代码执行完）：
  flushJobs()
  → job() 执行
  → effect 重新运行，读取最新值
  → 只渲染一次（10 20）
```

**flush 时机**：

| flush | 说明 | 应用场景 |
| --- | --- | --- |
| `sync` | 同步执行 | 需要立即看到更新 |
| `pre`（默认） | 组件更新前 | watch 回调中操作数据 |
| `post` | 组件更新后（nextTick 后） | 需要访问更新后的 DOM |

---

## 十、Vue2 vs Vue3 响应式对比

### 10.1 核心机制对比

| 维度 | Vue2 | Vue3 |
| --- | --- | --- |
| **劫持方式** | Object.defineProperty | Proxy |
| **劫持范围** | 单个属性 | 整个对象 |
| **新增属性** | ❌ 需 Vue.set | ✅ 自动响应 |
| **删除属性** | ❌ 需 Vue.delete | ✅ deleteProperty 拦截 |
| **数组监听** | ❌ 重写 7 个方法 | ✅ 原生支持 |
| **集合类型** | ❌ 不支持 | ✅ 支持 Map/Set |
| **深度响应** | 初始化递归（慢） | 访问时惰性（快） |
| **依赖存储** | 每属性一个 Dep | 全局 targetMap |
| **副作用管理** | Watcher 类 | ReactiveEffect + effect 栈 |
| **调度器** | nextTick + 队列 | 微任务 + 队列（类似） |
| **缓存机制** | 无 | computed 脏标记 |
| **TS 支持** | 弱（Options API） | 强（Composition API + 类型推导） |

### 10.2 依赖收集对比

```
Vue2 依赖收集结构：
┌────────────────────────────────────┐
│  Observer（每个对象一个）           │
│  ┌──────────────────────────────┐  │
│  │  Dep（每个属性一个）          │  │
│  │  subs: [Watcher, Watcher]    │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │  Dep                          │  │
│  │  subs: [Watcher]              │  │
│  └──────────────────────────────┘  │
└────────────────────────────────────┘
  - 每个对象有 Observer
  - 每个属性有 Dep
  - Watcher 收集 Dep

Vue3 依赖收集结构：
┌────────────────────────────────────┐
│  targetMap (WeakMap 全局唯一)       │
│  ┌──────────────────────────────┐  │
│  │  [target] → depsMap (Map)    │  │
│  │  ┌────────────────────────┐  │  │
│  │  │  [key] → dep (Set)     │  │  │
│  │  │  { effect, effect }    │  │  │
│  │  └────────────────────────┘  │  │
│  └──────────────────────────────┘  │
└────────────────────────────────────┘
  - 全局一个 targetMap
  - 三层结构：target → key → effect
  - effect 双向记录（deps）
```

### 10.3 性能对比

```
初始化性能（10 万属性的对象）：
┌────────────┬────────────┬──────────────────┐
│   方案     │ 初始化耗时 │ 说明              │
├────────────┼────────────┼──────────────────┤
│  Vue2      │  ~300ms    │ 递归遍历所有属性  │
│  Vue3      │  ~1ms      │ 仅创建 Proxy     │
└────────────┴────────────┴──────────────────┘

访问性能（首次访问嵌套对象）：
┌────────────┬────────────┬──────────────────┐
│   方案     │ 首次访问   │ 说明              │
├────────────┼────────────┼──────────────────┤
│  Vue2      │  快        │ 已全部代理        │
│  Vue3      │  稍慢      │ 惰性创建子 Proxy  │
└────────────┴────────────┴──────────────────┘

内存占用：
┌────────────┬────────────────────────────────┐
│  Vue2      │ 每属性一个 Dep 对象，占用多     │
│  Vue3      │ 共享 targetMap，按需创建 dep   │
└────────────┴────────────────────────────────┘
```

### 10.4 API 对比

| 能力 | Vue2 | Vue3 |
| --- | --- | --- |
| 响应式对象 | `data() { return {} }` | `reactive({})` |
| 响应式基本类型 | `data() { return { x: 1 } }` | `ref(1)` |
| 计算属性 | `computed: { double() {} }` | `computed(() => {})` |
| 侦听器 | `watch: { x() {} }` | `watch(x, () => {})` |
| 自动侦听 | 无 | `watchEffect(() => {})` |
| 只读 | 无 | `readonly(obj)` |
| 浅层 | 无 | `shallowReactive` / `shallowRef` |
| 标记非响应式 | `Object.freeze()` | `markRaw(obj)` |
| 转换 ref | 无 | `toRef` / `toRefs` |
| 自定义 ref | 无 | `customRef` |

---

## 十一、常见问题与最佳实践

### 11.1 为什么 ref 解构会丢失响应性？

```javascript
const { value } = ref(0)
// value 是基本类型，已脱离 ref 对象
value++  // ❌ 不响应式

// 正确：用 .value
const count = ref(0)
count.value++  // ✅ 响应式
```

### 11.2 为什么 reactive 解构会丢失响应性？

```javascript
const state = reactive({ count: 0, name: '张三' })
let { count, name } = state  // count/name 是基本类型值，脱离代理

// 解决：用 toRefs
const { count, name } = toRefs(state)  // 变成 ref，保持响应性
```

### 11.3 为什么 reactive 不能整体替换？

```javascript
const state = reactive({ count: 0 })

// ❌ 错误：替换后 state 不再是原始 Proxy
state = { count: 1 }  // 丢失响应性

// ✅ 正确方案1：用 ref
const stateRef = ref({ count: 0 })
stateRef.value = { count: 1 }  // 替换 value，保持响应性

// ✅ 正确方案2：用 Object.assign
Object.assign(state, { count: 1 })  // 合并属性，不替换对象
```

### 11.4 ref 与 reactive 如何选择？

```
选择决策树：

是基本类型？
  ├─ 是 → ref
  └─ 否 → 是对象
            ├─ 需要整体替换？ → ref
            └─ 仅修改属性？ → reactive

经验法则：
- 简单值（数字/字符串/布尔）→ ref
- 表单、复杂对象 → reactive  
- 需要解构传递 → ref + toRefs
- 数组（频繁增删）→ ref（可整体替换）
```

### 11.5 watch 深度侦听的陷阱

```javascript
const state = reactive({ user: { name: '张三' } })

// reactive 默认深度侦听
watch(() => state.user, (newVal) => {
  console.log('变化', newVal)  // 会触发
})
state.user.name = '李四'  // ✅ 触发

// 但侦听 getter 返回的引用不变，浅层不触发
watch(() => state.user, (newVal) => {
  console.log('变化')  // ❌ 不触发（引用未变）
}, { deep: false })
state.user.name = '李四'

// ref 包对象需 deep
const userRef = ref({ name: '张三' })
watch(userRef, (newVal) => {
  console.log('变化')  // ❌ 不触发（value 引用未变）
}, { deep: false })
userRef.value.name = '李四'

watch(userRef, (newVal) => {
  console.log('变化')  // ✅ 触发（deep）
}, { deep: true })
```

### 11.6 性能优化建议

```typescript
// 1. 大数据用 shallowRef / shallowReactive
const bigList = shallowRef<Item[]>([])  // 仅 .value 变化才响应
const config = shallowReactive({ theme: 'dark' })  // 仅第一层响应

// 2. 不可变数据用 markRaw
const staticData = markRaw(hugeDataset)  // 跳过代理

// 3. 避免不必要的深度侦听
watch(() => state.id, cb)  // ✅ 精确侦听
// watch(state, cb, { deep: true })  // ❌ 不必要的深度

// 4. computed 缓存复杂计算
const filtered = computed(() => 
  largeList.value.filter(item => item.active)  // 依赖不变不重算
)

// 5. 及时停止不再需要的 effect
const stop = watchEffect(() => { /* ... */ })
stop()  // 手动停止

// 6. v-once / v-memo 减少更新
// <div v-memo="[item.id]">...</div>
```

---

## 附录 核心源码索引

Vue3 响应式源码位于 `packages/reactivity/src/`：

| 文件 | 核心内容 |
| --- | --- |
| `reactive.ts` | reactive / readonly / shallowReactive 实现 |
| `ref.ts` | ref / computed / customRef 实现 |
| `effect.ts` | ReactiveEffect / track / trigger / cleanup |
| `baseHandlers.ts` | 普通对象的 Proxy handlers（get/set/has/deleteProperty） |
| `collectionHandlers.ts` | Map/Set 等集合类型的 handlers |
| `dep.ts` | dep 数据结构与依赖管理 |
| `computed.ts` | ComputedRefImpl 实现 |
| `watch.ts` | watch / watchEffect 实现（在 runtime-core） |
| `scheduler.ts` | 调度器与队列管理（在 runtime-core） |

**推荐阅读顺序**：
1. `effect.ts`：理解 ReactiveEffect、track、trigger（核心）
2. `reactive.ts`：理解 Proxy 的创建
3. `baseHandlers.ts`：理解 get/set 拦截细节
4. `ref.ts`：理解 ref 与 computed
5. `collectionHandlers.ts`：理解集合类型处理
6. `watch.ts`：理解 watch/watchEffect

---

## 参考资料

- Vue3 响应式官方文档：https://cn.vuejs.org/guide/extras/reactivity-in-depth.html
- Vue3 响应式 API：https://cn.vuejs.org/api/reactivity-core.html
- Vue3 源码：https://github.com/vuejs/core/tree/main/packages/reactivity
- MDN Proxy：https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Proxy
- MDN Reflect：https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Reflect
- ES6 Proxy 规范：https://tc39.es/ecma262/#sec-proxy-object-internal-methods-and-internal-slots

---

> **文档说明**：本文档共 11 大章节 + 附录 + 参考资料，系统覆盖 Vue3 响应式系统的核心原理：从 Object.defineProperty 的局限到 Proxy 的优势，从 track/trigger 的依赖收集到 computed 的缓存机制，从 ReactiveEffect 到调度器的批量更新。每个原理均配简易实现代码与流程图，并包含 Vue2 vs Vue3 的深度对比。建议结合 Vue3 源码阅读，加深理解。

