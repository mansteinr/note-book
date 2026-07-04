# 高级Vue3工程师面试题集

## 目录

1. [Vue3响应式系统](#vue3响应式系统)
2. [Computed实现原理](#computed实现原理)
3. [Watch实现原理](#watch实现原理)
4. [KeepAlive实现原理](#keepalive实现原理)
5. [虚拟DOM与Diff算法](#虚拟dom与diff算法)
6. [组合式API设计](#组合式api设计)
7. [组件通信与生命周期](#组件通信与生命周期)
8. [Vue3性能优化](#vue3性能优化)
9. [编译原理与架构设计](#编译原理与架构设计)
10. [状态管理与工程化](#状态管理与工程化)
11. [实战项目题](#实战项目题)

---

## Vue3响应式系统

### 选择题

**1. Vue3响应式系统的核心底层API是？**
A. Object.defineProperty
B. Proxy + Reflect
C. Object.observe
D. Proxy

**答案：B**

**2. 关于Vue3的Proxy实现响应式，描述正确的是？**
A. Proxy只能代理对象的第一层属性
B. Proxy代理后所有操作都会经过拦截器
C. Proxy不需要配合Reflect使用
D. Proxy无法监听数组变化

**答案：B**

**3. Vue3中reactive和ref的关系描述正确的是？**
A. ref基于Object.defineProperty实现
B. reactive可以处理基本类型
C. ref的value如果是对象，内部会调用reactive处理
D. ref和reactive没有任何关系

**答案：C**

**4. Vue3响应式系统中，effect函数的执行时机是？**
A. 创建时立即执行一次
B. 只在依赖变化时执行
C. 创建时执行，依赖变化时也执行
D. 由开发者手动调用

**答案：C**

---

### 简答题

**题目1：请详细阐述Vue3响应式系统的完整实现，从数据创建到视图更新的全流程。**

**考察重点：**
- Proxy拦截机制
- 依赖收集与track函数
- 触发更新与trigger函数
- effect副作用系统
- 懒代理实现

**参考答案：**

Vue3响应式系统基于 **Proxy + Reflect + Effect系统** 实现，完整流程如下：

#### 1. 响应式数据创建

```javascript
// reactive实现核心
function reactive(target) {
  if (!isObject(target)) return target
  if (target.__v_isReactive) return target  // 已代理过
  
  return new Proxy(target, {
    get(target, key, receiver) {
      if (key === '__v_isReactive') return true
      if (key === '__v_raw') return target
      
      // 依赖收集
      track(target, key)
      
      // 使用Reflect保证this正确
      const result = Reflect.get(target, key, receiver)
      
      // 懒代理（Lazy Proxy）：只有访问时才代理深层对象
      if (isObject(result)) {
        return reactive(result)
      }
      
      return result
    },
    
    set(target, key, value, receiver) {
      const oldValue = target[key]
      const hadKey = hasOwn(target, key)
      const result = Reflect.set(target, key, value, receiver)
      
      // 触发更新
      if (!hadKey) {
        trigger(target, key, 'ADD', value)
      } else if (hasChanged(value, oldValue)) {
        trigger(target, key, 'SET', value, oldValue)
      }
      
      return result
    },
    
    deleteProperty(target, key) {
      const hadKey = hasOwn(target, key)
      const result = Reflect.deleteProperty(target, key)
      if (hadKey) trigger(target, key, 'DELETE')
      return result
    },
    
    has(target, key) {
      track(target, key)
      return Reflect.has(target, key)
    },
    
    ownKeys(target) {
      track(target, Array.isArray(target) ? 'length' : Symbol('iterate'))
      return Reflect.ownKeys(target)
    }
  })
}

// ref实现
function ref(value) {
  if (isRef(value)) return value
  
  const wrappedValue = isObject(value) ? reactive(value) : value
  
  class RefImpl {
    __v_isRef = true
    get value() {
      track(this, 'value')
      return wrappedValue
    }
    set value(newVal) {
      if (hasChanged(newVal, wrappedValue)) {
        wrappedValue = isObject(newVal) ? reactive(newVal) : newVal
        trigger(this, 'value')
      }
    }
  }
  
  return new RefImpl()
}
```

#### 2. 依赖收集（track）

```javascript
// 全局变量
let activeEffect = null
let effectStack = []
const targetMap = new WeakMap()  // 所有依赖关系

function track(target, key) {
  if (!activeEffect) return
  
  // 结构：targetMap <Map> → depsMap <Map> → deps <Set> → effects
  let depsMap = targetMap.get(target)
  if (!depsMap) targetMap.set(target, depsMap = new Map())
  
  let deps = depsMap.get(key)
  if (!deps) depsMap.set(key, deps = new Set())
  
  deps.add(activeEffect)
  activeEffect.deps.push(deps)  // 反向引用用于清理
}
```

#### 3. 触发更新（trigger）

```javascript
function trigger(target, key, type, newValue, oldValue) {
  const depsMap = targetMap.get(target)
  if (!depsMap) return
  
  const effects = new Set()
  
  // 添加直接依赖
  const deps = depsMap.get(key)
  if (deps) deps.forEach(effect => effects.add(effect))
  
  // 数组length变化处理
  if (key === 'length' && Array.isArray(target)) {
    depsMap.forEach((d, k) => {
      if (isIntegerKey(k) && Number(k) >= newValue) {
        d.forEach(effect => effects.add(effect))
      }
    })
  }
  
  // 新增/删除属性时触发迭代相关effects
  if (type === 'ADD' || type === 'DELETE') {
    const iterateDeps = depsMap.get(Symbol('iterate'))
    if (iterateDeps) iterateDeps.forEach(effect => effects.add(effect))
  }
  
  // 执行所有effect
  effects.forEach(effect => {
    if (effect.scheduler) {
      effect.scheduler()  // 有调度器用调度器
    } else {
      effect()
    }
  })
}
```

#### 4. Effect副作用系统

```javascript
function effect(fn, options = {}) {
  const effectFn = function() {
    // 清理旧依赖
    cleanup(effectFn)
    
    // 入栈，设置activeEffect
    activeEffect = effectFn
    effectStack.push(effectFn)
    
    try {
      return fn()
    } finally {
      effectStack.pop()
      activeEffect = effectStack[effectStack.length - 1]
    }
  }
  
  effectFn.deps = []
  effectFn.options = options
  effectFn.scheduler = options.scheduler
  
  if (!options.lazy) effectFn()
  
  return effectFn
}

function cleanup(effectFn) {
  for (let i = 0; i < effectFn.deps.length; i++) {
    effectFn.deps[i].delete(effectFn)
  }
  effectFn.deps.length = 0
}
```

#### 5. 完整更新链路

```
1. 数据变化 → set陷阱触发 → trigger执行
2. trigger查找依赖 → effects执行
3. effect执行render → 访问响应式数据 → track收集
4. 生成新vnode树 → diff算法 → patch DOM
```

**评分标准：**
- 能说明Proxy的基本使用：60分
- 能完整说明track和trigger流程：80分
- 能解释懒代理、WeakMap选择、栈管理等细节：100分

---

**题目2：请详细对比Vue2和Vue3响应式系统的区别。**

**考察重点：**
- Object.defineProperty vs Proxy
- 数组监听实现
- 对象深层监听
- 初始化性能

**参考答案：**

| 对比维度 | Vue2 (defineProperty) | Vue3 (Proxy) |
|---------|----------------------|-------------|
| **拦截方式** | 劫持每个属性的getter/setter | 代理整个对象的所有操作 |
| **新增属性** | 需要 `Vue.$set` | 原生支持，无需额外处理 |
| **删除属性** | 需要 `Vue.$delete` | 原生支持 |
| **数组监听** | 重写 7个数组方法（push/pop等） | 原生支持索引和length变化 |
| **初始化** | 递归遍历所有属性，响应式成本高 | 懒代理，只代理访问到的层级 |
| **内存占用** | 每个属性都需要定义getter/setter | 一个Proxy代理整个对象 |
| **支持类型** | Object/Array有限支持 | Object/Array/Map/Set/WeakMap/WeakSet |
| **Symbol属性** | 不支持 | 支持 |
| **性能** | 大数据初始化慢，更新快 | 大数据初始化快，懒代理优化 |

**具体差异示例：**

```javascript
// Vue2：需要递归响应式化
const data = {
  user: {
    profile: {
      name: 'Vue2'
    }
  }
}
observe(data)  // 立即递归所有层级

// Vue3：懒代理
const data = reactive({
  user: {
    profile: {
      name: 'Vue3'
    }
  }
})
// user.profile.name访问时才会逐层代理
```

---

### 编程题

**题目：请手写一个完整的Vue3响应式系统，包括reactive、ref、effect、track、trigger。**

**参考答案：**

（代码较长，详见前文面试题1的完整实现）

---

## Computed实现原理

### 选择题

**1. Vue3的computed默认执行策略是？**
A. 同步立即计算
B. 延迟计算（第一次访问时计算）
C. 异步计算
D. 定时计算

**答案：B**

**2. computed的缓存失效时机是？**
A. 每次访问时重新计算
B. 依赖的响应式数据变化时标记失效
C. 定时器触发时
D. 组件重新渲染时

**答案：B**

---

### 简答题

**题目1：请详细解释Vue3中computed的实现原理。**

**考察重点：**
- 懒执行机制
- 缓存策略
- 脏值检测
- 嵌套computed

**参考答案：**

Vue3的computed基于effect系统实现，核心特点：**懒执行（Lazy）**、**缓存（Cache）**、**脏值检测（Dirty Checking）**。

```javascript
function computed(getterOrOptions) {
  let getter, setter
  if (typeof getterOrOptions === 'function') {
    getter = getterOrOptions
    setter = () => console.warn('computed is readonly')
  } else {
    getter = getterOrOptions.get
    setter = getterOrOptions.set
  }
  
  let value
  let isDirty = true
  
  const computedEffect = effect(getter, {
    lazy: true,
    scheduler: () => {
      if (!isDirty) {
        isDirty = true
        trigger(computedRef, 'value')
      }
    }
  })
  
  const computedRef = {
    __v_isRef: true,
    __v_isComputed: true,
    
    get value() {
      if (isDirty) {
        value = computedEffect()
        isDirty = false
      }
      track(computedRef, 'value')
      return value
    },
    
    set value(newVal) {
      setter(newVal)
    }
  }
  
  return computedRef
}
```

**核心机制分析：**

1. **懒执行**：创建computed时不执行getter，第一次访问.value时才执行
2. **缓存机制**：isDirty为false时直接返回缓存value
3. **脏值检测**：依赖变化时scheduler标记isDirty=true，不立即重算
4. **嵌套computed**：computed作为另一个computed的依赖，自动触发链式更新

**评分标准：**
- 能说明懒执行和缓存：60分
- 能说明scheduler和脏值检测：80分
- 能完整实现手写computed：100分

---

## Watch实现原理

### 选择题

**1. Vue3中watch和watchEffect的核心区别是？**
A. watch自动收集依赖，watchEffect需要指定数据源
B. watch需要指定数据源且能获取新旧值，watchEffect自动收集依赖
C. watchEffect有缓存机制
D. watch不支持immediate选项

**答案：B**

**2. watch的deep:true内部是如何实现的？**
A. 递归监听对象的所有属性
B. 递归访问对象的所有属性以触发依赖收集
C. 使用Object.observe监听
D. 定时轮询检查变化

**答案：B**

---

### 简答题

**题目1：请详细分析Vue3中watch的实现原理。**

**考察重点：**
- source类型处理
- deep实现
- 竞态处理
- 停止机制

**参考答案：**

```javascript
function watch(source, cb, options = {}) {
  // 1. 标准化getter
  let getter, isMultiSource = false
  
  if (isRef(source)) {
    getter = () => source.value
  } else if (isReactive(source)) {
    getter = () => source
    options.deep = true  // reactive默认deep
  } else if (Array.isArray(source)) {
    isMultiSource = true
    getter = () => source.map(s => {
      if (isRef(s)) return s.value
      if (isReactive(s)) return traverse(s)
      if (isFunction(s)) return s()
      return s
    })
  } else if (isFunction(source)) {
    getter = source
  }
  
  // 2. deep处理：递归访问所有属性收集依赖
  if (options.deep) {
    const baseGetter = getter
    getter = () => traverse(baseGetter())
  }
  
  // 3. 竞态处理
  let cleanup
  const onCleanup = (fn) => {
    cleanup = fn
  }
  
  let oldValue
  
  const job = () => {
    if (cleanup) cleanup()
    const newValue = effectFn()
    cb(newValue, oldValue, onCleanup)
    oldValue = newValue
  }
  
  const effectFn = effect(getter, {
    lazy: true,
    scheduler: job
  })
  
  // 4. 初始化
  if (options.immediate) {
    job()
  } else {
    oldValue = effectFn()
  }
  
  // 5. 返回停止函数
  return () => {
    cleanup = undefined
    effectFn.deps.forEach(dep => dep.delete(effectFn))
  }
}

// 辅助函数：递归遍历收集所有依赖
function traverse(value, seen = new Set()) {
  if (!isObject(value) || seen.has(value)) return value
  seen.add(value)
  if (Array.isArray(value)) {
    value.forEach(item => traverse(item, seen))
  } else {
    Object.values(value).forEach(item => traverse(item, seen))
  }
  return value
}
```

**关键机制：**

1. **deep实现**：traverse递归访问所有属性，触发每个属性的getter进行依赖收集
2. **竞态处理**：onCleanup在前一次执行前清理，避免竞态问题
3. **停止机制**：从所有deps中移除effect，防止继续触发

---

## KeepAlive实现原理

### 选择题

**1. KeepAlive组件的缓存机制使用的数据结构是？**
A. Object
B. Map
C. WeakMap
D. Set

**答案：B**

**2. KeepAlive组件使用的缓存淘汰算法是？**
A. FIFO
B. LRU
C. LFU
D. 随机淘汰

**答案：B**

---

### 简答题

**题目1：请详细解释Vue3中KeepAlive的实现原理。**

**考察重点：**
- 缓存机制
- LRU算法
- 生命周期钩子
- 组件标记

**参考答案：**

```javascript
const KeepAliveImpl = {
  __isKeepAlive: true,
  
  props: {
    include: [String, RegExp, Array],
    exclude: [String, RegExp, Array],
    max: [String, Number]
  },
  
  setup(props, { slots }) {
    const cache = new Map()
    const keys = new Set()
    const storageContainer = document.createElement('div')
    
    // 缓存淘汰
    const pruneCacheEntry = (key) => {
      const cached = cache.get(key)
      if (cached?.component) {
        cached.component.ctx.deactivated()
      }
      cache.delete(key)
      keys.delete(key)
    }
    
    // 监听include/exclude变化
    watch(() => [props.include, props.exclude], ([inc, exc]) => {
      cache.forEach((v, key) => {
        const name = getComponentName(v.type)
        if ((inc && !matches(inc, name)) || (exc && matches(exc, name))) {
          pruneCacheEntry(key)
        }
      })
    })
    
    return () => {
      const children = slots.default()
      if (children.length !== 1) return children[0]
      
      const vnode = children[0]
      const key = vnode.key ?? vnode.type
      const name = getComponentName(vnode.type)
      
      // 检查include/exclude
      if (name && ((props.include && !matches(props.include, name)) 
                  || (props.exclude && matches(props.exclude, name)))) {
        return vnode
      }
      
      // 检查缓存
      const cached = cache.get(key)
      if (cached) {
        // 命中缓存：更新LRU顺序
        keys.delete(key)
        keys.add(key)
        
        vnode.el = cached.el
        vnode.component = cached.component
        vnode.shapeFlag |= 512  // COMPONENT_KEPT_ALIVE
      } else {
        // 加入缓存
        keys.add(key)
        if (props.max && keys.size > Number(props.max)) {
          // LRU淘汰
          pruneCacheEntry(keys.values().next().value)
        }
        cache.set(key, vnode)
      }
      
      vnode.shapeFlag |= 256  // COMPONENT_SHOULD_KEEP_ALIVE
      return vnode
    }
  }
}
```

**关键点说明：**

1. **缓存结构**：Map存储vnode，Set维护LRU顺序
2. **LRU实现**：访问时移到最后，淘汰时删第一个
3. **组件标记**：shapeFlag标记让渲染器知道是缓存组件
4. **DOM处理**：组件切换时DOM移到隐藏容器，而非销毁
5. **生命周期**：activated/deactivated钩子替代mounted/unmounted

---

## 虚拟DOM与Diff算法

### 简答题

**题目1：请详细解释Vue3虚拟DOM的优化策略。**

**考察重点：**
- PatchFlags
- 静态提升
- 事件缓存
- Block树

**参考答案：**

Vue3的虚拟DOM相比Vue2有巨大优化，主要包括：

#### 1. PatchFlags（动态属性标记）

```javascript
// 编译前
<div id="app">
  <h1>{{ title }}</h1>
  <p v-if="show">Content</p>
</div>

// 编译后
import { createVNode as _createVNode, toDisplayString as _toDisplayString, openBlock as _openBlock, createBlock as _createBlock, withCtx as _withCtx } from "vue"

const _hoisted_1 = { id: "app" }
const _hoisted_2 = /*#__PURE__*/_createVNode("h1", null, null, -1 /* HOISTED */)

export function render(_ctx, _cache, $props, $setup, $data, $options) {
  return (_openBlock(), _createBlock("div", _hoisted_1, [
    _createVNode("h1", null, _toDisplayString(_ctx.title), 1 /* TEXT */),
    _cache[0] || (_cache[0] = _withCtx((_openBlock(), _createBlock("p", null, "Content")))),
    _ctx.show ? _cache[0] : null
  ]))
}
```

**PatchFlags枚举：**
```javascript
const PatchFlags = {
  TEXT: 1,               // 动态文本
  CLASS: 1 << 1,         // 动态class
  STYLE: 1 << 2,         // 动态style
  PROPS: 1 << 3,         // 动态props（非class/style）
  FULL_PROPS: 1 << 4,    // 动态key的props
  HYDRATE_EVENTS: 1 << 5, // 水合事件
  STABLE_FRAGMENT: 1 << 6, // 稳定fragment
  KEYED_FRAGMENT: 1 << 7,  // 有key的fragment
  UNKEYED_FRAGMENT: 1 << 8, // 无key的fragment
  NEED_PATCH: 1 << 9,    // 需要额外patch（如ref）
  DYNAMIC_SLOTS: 1 << 10,  // 动态插槽
  HOISTED: -1,           // 静态提升
  BAIL: -2               // 退出优化模式
}
```

#### 2. 静态提升（Hoist Static）

```javascript
// 编译前
<div>
  <span>静态文本</span>
  <span>{{ dynamic }}</span>
</div>

// 编译后
const _hoisted_1 = /*#__PURE__*/_createVNode("span", null, "静态文本", -1 /* HOISTED */)

function render() {
  return _createVNode("div", null, [
    _hoisted_1,           // 引用提升后的静态节点
    _createVNode("span", null, _ctx.dynamic, 1 /* TEXT */)
  ])
}
```

#### 3. 事件处理器缓存

```javascript
// 编译前
<button @click="onClick">按钮</button>

// 编译后
function render(_ctx, _cache) {
  return _createVNode("button", { 
    onClick: _cache[0] || (_cache[0] = (...args) => (_ctx.onClick(...args)))
  }, "按钮")
}
```

#### 4. Block树优化

```javascript
// 将模板按条件/循环拆分为多个Block
<div>
  <header>{{ title }}</header>
  <div v-for="item in list" :key="item.id">{{ item.name }}</div>
  <footer v-if="show">Footer</footer>
</div>

// 编译后拆分为多个Block，只patch动态变化的部分
```

---

## 组合式API设计

### 简答题

**题目1：请对比Options API和Composition API的区别。**

**考察重点：**
- 代码组织
- 逻辑复用
- TypeScript支持
- Tree-shaking

**参考答案：**

| 特性 | Options API | Composition API |
|------|------------|-----------------|
| **代码组织** | 按类型（data/methods/computed）分散 | 按功能逻辑聚合 |
| **逻辑复用** | Mixins（易冲突） | 自定义Hooks（清晰、可组合） |
| **TS支持** | 需要Vue.extend或class | 天然完美支持 |
| **Tree-shaking** | 选项式优化困难 | 函数式天然易优化 |
| **内存占用** | 每个组件创建实例 | 函数调用，开销小 |
| **学习曲线** | 清晰易懂，适合新手 | 理解稍复杂，灵活性高 |
| **调试友好** | Vue DevTools支持好 | DevTools同样支持 |

**代码组织对比：**

```javascript
// Options API：相关逻辑分散在各个选项
export default {
  data() { return { count: 0, name: 'Vue' } },
  computed: { double() { return this.count * 2 } },
  methods: { inc() { this.count++ } },
  watch: { count() { /* ... */ } }
}

// Composition API：相关逻辑聚合
import { ref, computed, watch } from 'vue'
export default {
  setup() {
    // 计数器相关逻辑
    const count = ref(0)
    const double = computed(() => count.value * 2)
    const inc = () => count.value++
    
    // 名字相关逻辑
    const name = ref('Vue')
    watch(name, () => { /* ... */ })
    
    return { count, double, inc, name }
  }
}

// 更好的方式：自定义Hook
function useCounter() {
  const count = ref(0)
  const double = computed(() => count.value * 2)
  const inc = () => count.value++
  return { count, double, inc }
}
```

---

## Vue3性能优化

### 简答题

**题目1：Vue3应用的性能优化策略有哪些？**

**参考答案：**

#### 编译时优化
1. 确保使用生产构建 `createApp(App).mount('#app')`
2. 使用Vite或Rollup进行Tree-shaking
3. 开启Babel插件按需引入（如果是UI库）

#### 运行时优化

```javascript
// 1. 合理使用key
// ❌
<div v-for="(item, i) in list" :key="i">
// ✅
<div v-for="item in list" :key="item.id">

// 2. 避免不必要的响应式
const staticData = markRaw({ /* 不需要响应式的数据 */ })
const shallowState = shallowReactive({ /* 只需要浅层响应式 */ })

// 3. 合理使用computed缓存（不是所有计算都需要缓存）
// ✅ 复杂计算用computed
// ❌ 简单计算直接用方法

// 4. v-once：只渲染一次
<span v-once>{{ staticContent }}</span>

// 5. v-memo：记忆化模板部分
<div v-for="item in list" :key="item.id" v-memo="[item.id, item.name]">
  <!-- 只有item.id或item.name变化时才重新渲染 -->
</div>

// 6. 虚拟列表（大数据量）
import { useVirtualList } from '@vueuse/core'
```

#### 组件优化
```javascript
// 异步组件 + 懒加载
const LazyComponent = defineAsyncComponent({
  loader: () => import('./LazyComponent.vue'),
  loadingComponent: Loading,
  errorComponent: ErrorComponent,
  delay: 200,
  timeout: 10000
})

// 路由懒加载
const routes = [
  { path: '/home', component: () => import('./Home.vue') }
]

// 使用functional组件（无状态）
<template functional>
  <div>{{ props.text }}</div>
</template>
```

#### 状态管理优化
- 使用Pinia替代Vuex（性能更好、API更简洁）
- 合理拆分store，避免单个store过大
- 使用computed缓存派生状态

---

## 实战项目题

**题目1：请设计一个Vue3电商项目的技术架构。**

**参考答案要点：**

```
项目架构：
├── src/
│   ├── components/
│   │   ├── base/ (Button/Input/Dropdown等基础组件)
│   │   ├── business/ (ProductCard/CartItem等业务组件)
│   │   └── layout/ (Header/Footer/Sidebar)
│   ├── views/
│   ├── stores/ (Pinia状态管理)
│   │   ├── useCartStore.ts
│   │   ├── useUserStore.ts
│   │   └── useProductStore.ts
│   ├── composables/ (自定义Hooks)
│   │   ├── useRequest.ts
│   │   ├── usePagination.ts
│   │   └── useDebounce.ts
│   ├── api/ (API请求封装)
│   ├── types/ (TypeScript类型定义)
│   └── router/
```

**关键技术选型：**
- UI库：Element Plus / Ant Design Vue
- 状态管理：Pinia
- 路由：Vue Router 4
- HTTP：Axios
- 构建工具：Vite
- CSS方案：Tailwind CSS / SCSS
- 工具库：VueUse

---

## 高级题

**题目1：Vue3的SSR（服务端渲染）实现原理是什么？**

**参考答案要点：**

```javascript
// Vue3的SSR核心是服务端创建App，生成HTML字符串，客户端hydrate（水合）
// 服务端代码
import { createSSRApp } from 'vue'
import App from './App.vue'
import { renderToString } from '@vue/server-renderer'

async function serverRender() {
  const app = createSSRApp(App)
  const html = await renderToString(app)
  return html
}

// 客户端代码
import { createSSRApp } from 'vue'
import App from './App.vue'
const app = createSSRApp(App)
app.mount('#app', true)  // hydrate模式：不重新创建DOM，只绑定事件
```

---

## 面试建议

### 准备方向
1. **源码阅读**：重点看 reactivity、runtime-core、compiler-core 三个核心包
2. **实战项目**：深入理解 Composition API 的最佳实践
3. **性能优化**：能从编译时、运行时、架构设计等层面说明优化策略
4. **TypeScript**：熟练使用 TS 写 Vue3 组件，理解类型系统
5. **最新动态**：关注 Vue3.4+、VueUse 等生态进展

### 面试技巧
- 先说大方向，再深入细节
- 对比Vue2/Vue3的差异是常考点
- 结合实际项目经验说明理解
- 手写核心API是区分高级/中级的关键
