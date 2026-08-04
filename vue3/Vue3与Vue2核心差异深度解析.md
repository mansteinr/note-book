# Vue 3 与 Vue 2 核心差异深度解析

> 本文档系统对比 Vue 3 与 Vue 2 在底层实现逻辑上的核心差异，涵盖响应式系统、虚拟 DOM、API 设计、编译优化、模块架构等维度的深度分析，配合代码示例与架构图解，帮助开发团队深入理解 Vue 3 的架构演进与技术优势。

---

## 目录

- [Vue 3 与 Vue 2 核心差异深度解析](#vue-3-与-vue-2-核心差异深度解析)
  - [目录](#目录)
  - [一、概述：Vue 3 的架构演进](#一概述vue-3-的架构演进)
    - [1.1 为什么需要 Vue 3](#11-为什么需要-vue-3)
    - [1.2 Vue 3 核心改进概览](#12-vue-3-核心改进概览)
    - [1.3 架构演进时间线](#13-架构演进时间线)
  - [二、响应式系统：Object.defineProperty vs Proxy](#二响应式系统objectdefineproperty-vs-proxy)
    - [2.1 Vue 2 响应式原理回顾](#21-vue-2-响应式原理回顾)
      - [Object.defineProperty 核心机制](#objectdefineproperty-核心机制)
      - [Vue 2 的局限性](#vue-2-的局限性)
    - [2.2 Vue 3 响应式原理详解](#22-vue-3-响应式原理详解)
      - [Proxy 核心机制](#proxy-核心机制)
      - [Vue 3 响应式架构](#vue-3-响应式架构)
      - [Vue 3 新增/删除属性示例](#vue-3-新增删除属性示例)
    - [2.3 核心差异对比表](#23-核心差异对比表)
  - [三、虚拟 DOM 重写与性能优化](#三虚拟-dom-重写与性能优化)
    - [3.1 Vue 2 的虚拟 DOM 实现](#31-vue-2-的虚拟-dom-实现)
      - [Vue 2 VNode 结构](#vue-2-vnode-结构)
      - [Vue 2 Diff 算法](#vue-2-diff-算法)
    - [3.2 Vue 3 的虚拟 DOM 重写](#32-vue-3-的虚拟-dom-重写)
      - [Vue 3 VNode 结构](#vue-3-vnode-结构)
      - [Patch Flag 机制详解](#patch-flag-机制详解)
      - [Block Tree（块树）机制](#block-tree块树机制)
    - [3.3 Diff 算法优化](#33-diff-算法优化)
  - [四、Composition API vs Options API](#四composition-api-vs-options-api)
    - [4.1 Options API 设计理念](#41-options-api-设计理念)
    - [4.2 Composition API 设计理念](#42-composition-api-设计理念)
    - [4.3 代码组织对比示例](#43-代码组织对比示例)
      - [场景：实现一个搜索功能（带防抖、请求、结果展示）](#场景实现一个搜索功能带防抖请求结果展示)
  - [五、生命周期钩子的变化](#五生命周期钩子的变化)
    - [5.1 Vue 2 生命周期](#51-vue-2-生命周期)
    - [5.2 Vue 3 生命周期](#52-vue-3-生命周期)
      - [生命周期钩子对照](#生命周期钩子对照)
    - [5.3 迁移与注意事项](#53-迁移与注意事项)
  - [六、TypeScript 支持差异](#六typescript-支持差异)
    - [6.1 Vue 2 的 TS 支持](#61-vue-2-的-ts-支持)
    - [6.2 Vue 3 的 TS 支持](#62-vue-3-的-ts-支持)
    - [6.3 类型推导对比](#63-类型推导对比)
  - [七、编译优化策略](#七编译优化策略)
    - [7.1 Vue 2 编译流程](#71-vue-2-编译流程)
    - [7.2 Vue 3 编译优化](#72-vue-3-编译优化)
    - [7.3 Patch Flag 机制](#73-patch-flag-机制)
      - [完整 Patch Flag 列表](#完整-patch-flag-列表)
      - [Patch Flag 在运行时的使用](#patch-flag-在运行时的使用)
    - [7.4 静态提升](#74-静态提升)
      - [可静态提升的内容](#可静态提升的内容)
  - [八、内部模块结构调整](#八内部模块结构调整)
    - [8.1 Vue 2 模块结构](#81-vue-2-模块结构)
    - [8.2 Vue 3 模块结构](#82-vue-3-模块结构)
    - [8.3 Monorepo 架构优势](#83-monorepo-架构优势)
  - [九、性能数据对比](#九性能数据对比)
    - [9.1 综合性能对比](#91-综合性能对比)
    - [9.2 渲染性能对比](#92-渲染性能对比)
  - [十、迁移指南与最佳实践](#十迁移指南与最佳实践)
    - [10.1 迁移策略](#101-迁移策略)
    - [10.2 常见兼容性问题](#102-常见兼容性问题)
    - [10.3 最佳实践建议](#103-最佳实践建议)
      - [组件设计最佳实践](#组件设计最佳实践)
  - [十一、总结与选型建议](#十一总结与选型建议)
    - [11.1 核心差异总结](#111-核心差异总结)
    - [11.2 选型建议](#112-选型建议)
    - [11.3 学习资源推荐](#113-学习资源推荐)
  - [附录：术语表](#附录术语表)

---

## 一、概述：Vue 3 的架构演进

### 1.1 为什么需要 Vue 3

Vue 2 发布于 2016 年，凭借渐进式框架的设计理念迅速成为全球最流行的前端框架之一。但随着项目复杂度的提升和现代 JavaScript 语言的发展，Vue 2 逐渐暴露出一系列架构层面的局限性。

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 2 的核心痛点                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. 响应式系统的局限性                                                  │
│     - Object.defineProperty 无法监听新增/删除属性                       │
│     - 无法监听数组索引直接修改                                           │
│     - 需要 Vue.set / Vue.delete 等 API 补丁                            │
│                                                                         │
│  2. 大规模组件的逻辑复用困难                                           │
│     - Options API 强制按选项类型组织代码                                 │
│     - 相同功能的逻辑分散在 data、methods、computed 等选项中             │
│     - 难以跨组件提取和复用逻辑                                           │
│                                                                         │
│  3. 虚拟 DOM 性能瓶颈                                                  │
│     - 全量 Diff 算法，即使模板完全相同也需重新创建 VNode               │
│     - 缺少编译期优化，运行时开销大                                       │
│                                                                         │
│  4. TypeScript 支持不完善                                               │
│     - 需要额外的声明文件                                                 │
│     - Options API 的类型推导不够智能                                     │
│                                                                         │
│  5. 运行时体积过大                                                      │
│     - 无法按需求裁剪                                                     │
│     - 即使只用核心功能也需加载完整运行时                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Vue 3 核心改进概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 3 核心改进全景                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  响应式系统：Object.defineProperty → Proxy                      │   │
│  │  - 支持监听所有数据变化                                         │   │
│  │  - 支持 Map/Set/Class 等复杂类型                               │   │
│  │  - 惰性响应式（嵌套对象按需代理）                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  虚拟 DOM：全量 Diff → 精细化 Patch                             │   │
│  │  - Patch Flag 标记动态节点类型                                  │   │
│  │  - 静态提升减少 VNode 创建                                      │   │
│  │  - 块级更新（Block Tree）缩小 Diff 范围                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  API 设计：Options API → Composition API + <script setup>       │   │
│  │  - 逻辑关注点聚合                                               │   │
│  │  - 原生 TS 支持                                                │   │
│  │  - 更好的代码组织与复用                                         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  编译优化：引入编译期优化策略                                   │   │
│  │  - 静态提升（Hoisting Static）                                 │   │
│  │  - Patch Flag（动态标记）                                      │   │
│  │  - 块级更新（Block Tree）                                      │   │
│  │  - 事件缓存（Event Caching）                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  架构演进：Monorepo + Tree-shaking                             │   │
│  │  - 独立模块包化 @vue/reactivity、@vue/renderer-core 等         │   │
│  │  - 按需引入，减小打包体积                                       │   │
│  │  - 模块间解耦，便于独立迭代                                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.3 架构演进时间线

```
时间轴：
────────────────────────────────────────────────────────────────────────→

2013  Vue 0.x 发布（原型阶段）
  │
2014  Vue 1.x 发布（MVVM 架构确立）
  │
2016  Vue 2.0 发布（虚拟 DOM、响应式系统成熟）
  │   ├── 引入 Object.defineProperty 响应式
  │   ├── 引入虚拟 DOM + Diff 算法
  │   ├── 支持 SSR
  │   └── 组件化体系完善
  │
2018  Vue 3 设计启动
  │   ├── 评估 Proxy 方案
  │   ├── 规划 Composition API
  │   └── 模块架构重构
  │
2020  Vue 3.0 正式发布
  │   ├── 基于 Proxy 的响应式系统
  │   ├── Composition API
  │   ├── 重写虚拟 DOM 和 Diff 算法
  │   └── Monorepo 架构
  │
2021  Vue 3.2 发布
  │   ├── <script setup> 稳定
  │   └── 响应式 API 完善
  │
2022  Vue 3.3 发布
  │   ├── 宏（Macros）增强
  │   └── Reactivity Transform
  │
2023+ Vue 3.4+ 持续迭代
```

---

## 二、响应式系统：Object.defineProperty vs Proxy

### 2.1 Vue 2 响应式原理回顾

#### Object.defineProperty 核心机制

Vue 2 使用 `Object.defineProperty` 劫持对象属性的 `getter` 和 `setter`，实现数据变更检测。

```javascript
// Vue 2 响应式核心实现
function defineReactive(obj, key, val) {
  Object.defineProperty(obj, key, {
    enumerable: true,
    configurable: true,
    get() {
      // 依赖收集：记录谁访问了这个属性
      dep.depend()
      return val
    },
    set(newVal) {
      if (newVal === val) return
      val = newVal
      // 触发更新：通知所有依赖
      dep.notify()
    }
  })
}

// 递归处理对象
function observe(obj) {
  if (typeof obj !== 'object' || obj === null) return
  Object.keys(obj).forEach(key => {
    defineReactive(obj, key, obj[key])
  })
}
```

#### Vue 2 的局限性

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 2 响应式系统的局限                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  局限 1：无法监听属性新增/删除                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  const vm = new Vue({ data: { count: 0 } })                     │   │
│  │  vm.newProp = 'hello'  // ❌ 无法触发响应式                     │   │
│  │  delete vm.count       // ❌ 无法触发响应式                     │   │
│  │                                                                 │   │
│  │  // 需要使用特定 API                                              │   │
│  │  this.$set(this.data, 'newProp', 'hello')  // ✅ 可以            │   │
│  │  this.$delete(this.data, 'count')          // ✅ 可以            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  局限 2：无法监听数组索引直接修改                                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  const vm = new Vue({ data: { list: [1, 2, 3] } })              │   │
│  │  vm.list[0] = 100   // ❌ 无法触发更新                          │   │
│  │  vm.list.length = 5 // ❌ 无法触发更新                          │   │
│  │                                                                 │   │
│  │  // Vue 2 对数组方法进行了拦截                                     │   │
│  │  // push、pop、shift、unshift、splice、sort、reverse             │   │
│  │  vm.list.splice(0, 1, 100)  // ✅ 可以触发                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  局限 3：初始化时全量递归遍历                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  // Vue 2 在初始化时递归遍历所有嵌套对象                         │   │
│  │  // 即使某些深层属性可能永远不会被访问                            │   │
│  │  const data = {                                                  │   │
│  │    user: {                                                      │   │
│  │      profile: {                                                 │   │
│  │        settings: {                                              │   │
│  │          preferences: { /* 100 层嵌套 */ }                     │   │
│  │        }                                                        │   │
│  │      }                                                          │   │
│  │    }                                                            │   │
│  │  }                                                              │   │
│  │  // 所有嵌套对象在初始化时都被深度代理                             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  局限 4：不支持 Map、Set、Class 等类型                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  const data = {                                                 │   │
│  │    map: new Map(),   // ❌ 无法响应式                           │   │
│  │    set: new Set(),   // ❌ 无法响应式                           │   │
│  │  }                                                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Vue 3 响应式原理详解

#### Proxy 核心机制

Vue 3 使用 ES6 `Proxy` 代理整个对象，可以拦截对象上的所有操作。

```javascript
// Vue 3 响应式核心实现
function createReactiveObject(target, isReadonly) {
  // 使用 Proxy 代理整个对象
  const proxy = new Proxy(target, {
    get(target, key, receiver) {
      // 依赖收集
      track(target, key)
      
      // 递归代理嵌套对象（惰性）
      const res = Reflect.get(target, key, receiver)
      if (isObject(res)) {
        return reactive(res)  // 按需代理
      }
      return res
    },
    
    set(target, key, value, receiver) {
      // 触发更新
      trigger(target, key)
      return Reflect.set(target, key, value, receiver)
    },
    
    // Vue 3 能拦截的操作：
    has(target, key)        // in 操作符
    deleteProperty(target, key)  // delete 操作
    ownKeys(target)         // Object.keys / for...in
    getOwnPropertyDescriptor(target, key)
    // 等等...覆盖几乎所有对象操作
  })
  
  return proxy
}
```

#### Vue 3 响应式架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 3 响应式系统架构                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  核心 API：                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                 │   │
│  │  reactive()         → 对象响应式                                │   │
│  │  ├── 底层使用 Proxy 代理整个对象                                 │   │
│  │  ├── 惰性递归：嵌套对象在访问时才代理                             │   │
│  │  └── 支持 Map/Set/Class 等复杂类型                               │   │
│  │                                                                 │   │
│  │  ref()              → 基本类型响应式                             │   │
│  │  ├── 包装为对象 { value: xxx }                                   │   │
│  │  └── 通过 .value 访问，模板中自动解包                           │   │
│  │                                                                 │   │
│  │  computed()         → 计算属性                                  │   │
│  │  ├── 惰性求值（只有在依赖变化时才重新计算）                       │   │
│  │  └── 自动缓存结果                                               │   │
│  │                                                                 │   │
│  │  watch() / watchEffect() → 侦听器                                │   │
│  │  ├── 自动依赖收集                                               │   │
│  │  └── 支持副作用清理                                             │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  依赖收集流程：                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  1. Effect 执行，设置当前激活的 effect 栈                       │   │
│  │  2. 访问响应式属性 → 触发 Proxy.get → track()                   │   │
│  │  3. track() 将当前 effect 收集到对应属性的依赖集合中             │   │
│  │  4. 属性值变化 → 触发 Proxy.set → trigger()                     │   │
│  │  5. trigger() 执行所有依赖该属性的 effect                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Vue 3 新增/删除属性示例

```javascript
// Vue 3 中直接添加/删除属性即可响应
const state = reactive({ count: 0 })

// 新增属性 - 直接触发响应式
state.newProp = 'hello'  // ✅ 自动触发更新

// 删除属性 - 直接触发响应式
delete state.count  // ✅ 自动触发更新

// 数组索引直接赋值
const list = reactive([1, 2, 3])
list[0] = 100  // ✅ 自动触发更新
list.length = 5  // ✅ 自动触发更新

// Map/Set 支持
const map = reactive(new Map())
map.set('key', 'value')  // ✅ 自动触发更新
map.delete('key')  // ✅ 自动触发更新
```

### 2.3 核心差异对比表

| 对比维度 | Vue 2 (Object.defineProperty) | Vue 3 (Proxy) |
|---------|-------------------------------|---------------|
| **监听范围** | 只能监听已有属性 | 监听所有属性（包括新增/删除） |
| **数组支持** | 仅支持方法调用（push/splice等） | 支持索引、长度、所有操作 |
| **数据类型** | 仅支持 Object | 支持 Object、Array、Map、Set、Class |
| **初始化性能** | 全量递归遍历 | 惰性递归（按需代理） |
| **内存占用** | 每个属性需 getter/setter | 仅 Proxy 包装，更轻量 |
| **兼容性** | 支持 IE9+ | 需 Proxy 支持（IE 不支持） |
| **API 设计** | 需 `Vue.set`/`Vue.delete` | 原生 JS 操作即可 |

---

## 三、虚拟 DOM 重写与性能优化

### 3.1 Vue 2 的虚拟 DOM 实现

#### Vue 2 VNode 结构

```javascript
// Vue 2 VNode 结构
{
  tag: 'div',                    // 标签名
  data: {                        // 属性数据
    class: ['container', 'active'],
    style: { color: 'red' },
    on: { click: handler }
  },
  children: [                    // 子节点
    { tag: 'span', children: 'Hello' }
  ],
  text: undefined,               // 文本节点内容
  elm: null,                     // 对应的真实 DOM 元素
  key: 'id',                     // 唯一标识
  componentInstance: null        // 组件实例
}
```

#### Vue 2 Diff 算法

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 2 Diff 算法流程（全量 Diff）                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. 新旧 VNode 树逐层遍历                                               │
│  2. 对每一层进行同层比较                                                 │
│  3. 如果节点类型不同（tag 不同），直接替换                               │
│  4. 如果节点类型相同，比较属性和子节点                                   │
│  5. 对子节点列表使用双指针进行 Diff                                      │
│                                                                         │
│  问题：                                                                 │
│  - 即使整个模板没有变化，也需要重新 Diff 所有节点                       │
│  - 没有静态标记，无法区分动态和静态内容                                 │
│  - 每次更新都要创建新的 VNode                                           │
│                                                                         │
│  复杂度：O(n³) → 经过优化后为 O(n)（同层比较）                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Vue 3 的虚拟 DOM 重写

#### Vue 3 VNode 结构

```javascript
// Vue 3 VNode 结构（更轻量）
{
  __v_isVNode: true,
  __v_skip: false,              // 是否跳过 Patch
  type: 'div',                  // 标签名（可以是组件对象）
  props: {                      // 属性数据（无 getter/setter）
    class: 'container active',
    style: { color: 'red' }
  },
  children: [                   // 子节点
    { __v_isVNode: true, type: 'span', children: 'Hello' }
  ],
  patchFlag: 1,                 // 补丁标记（核心优化）
  dynamicChildren: null,        // 动态子节点数组
  key: 'id',
  ref: null,
  // ...更精简的结构
}
```

#### Patch Flag 机制详解

Patch Flag 是 Vue 3 编译期为动态节点打上的标记，运行时可据此跳过不必要的 Diff。

```javascript
// Patch Flag 常量定义
export const enum PatchFlags {
  TEXT = 1,             // 动态文本
  CLASS = 2,            // 动态 class
  STYLE = 4,            // 动态 style
  PROPS = 8,            // 动态 props
  FULL_PROPS = 16,      // 有 key 的动态 props
  NEED_HYDRATION = 32,  // 需要 hydration
  STABLE_FRAGMENT = 64, // 稳定的 Fragment
  KEYED_FRAGMENT = 128, // 有 key 的 Fragment
  UNKEYED_FRAGMENT = 256, // 无 key 的 Fragment
  REF = 512,            // 有 ref
  BAIL = 1024,          // 静态标记
}

// 编译时生成的 render 函数示例
function render(ctx) {
  return (openBlock(),
    createElementBlock("div", null, [
      createElementVNode("span", {
        // PatchFlag: TEXT | CLASS
        // 告诉运行时：只有文本和 class 需要更新
        // style、其他 props 无需检查
        class: ctx.isActive,
      }, toDisplayString(ctx.message), 1 /* TEXT | CLASS */)
    ]))
}
```

#### Block Tree（块树）机制

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 3 Block Tree 机制                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  核心思想：将模板分割为多个「块」，每个块只包含动态节点                  │
│                                                                         │
│  编译前：                                                               │
│  <template>                                                             │
│    <div class="static">                                                │
│      <h1>静态标题</h1>       ← 永远不会变                              │
│      <p>{{ message }}</p>    ← 只有这个会变                            │
│      <button @click="save">保存</button>  ← 永远不会变                 │
│    </div>                                                              │
│  </template>                                                           │
│                                                                         │
│  编译后：                                                               │
│  function render(ctx) {                                                │
│    return (openBlock(),                                                │
│      createElementBlock("div", { class: "static" }, [                   │
│        // 静态节点：直接创建，无 PatchFlag                             │
│        createElementVNode("h1", null, "静态标题"),                    │
│        // 动态节点：标记 PatchFlag，仅 Diff 此节点                     │
│        createElementVNode("p", null, toDisplayString(ctx.message),     │
│          1 /* TEXT */),                                                │
│        // 静态节点：直接创建                                           │
│        createElementVNode("button", {                                  │
│          onClick: ctx.save                                             │
│        }, "保存")                                                      │
│      ]))                                                               │
│    )                                                                   │
│  }                                                                     │
│                                                                         │
│  运行时行为：                                                           │
│  - 只有 PatchFlag 标记为 TEXT 的 <p> 节点会被 Diff                      │
│  - <h1> 和 <button> 完全跳过 Diff 检查                                 │
│  - 极大减少 Diff 范围和计算量                                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Diff 算法优化

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 2 vs Vue 3 Diff 算法对比                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Vue 2 Diff：全量同层比较                                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  新 VNode: [A, B, C, D, E]                                      │   │
│  │  旧 VNode: [A, X, C, D, E]                                      │   │
│  │                                                                 │   │
│  │  Diff 过程：                                                    │   │
│  │  比较 A==A ✅  → 跳过                                           │   │
│  │  比较 B==X ❌  → 标记为变化                                     │   │
│  │  比较 C==C ✅  → 跳过                                           │   │
│  │  比较 D==D ✅  → 跳过                                           │   │
│  │  比较 E==E ✅  → 跳过                                           │   │
│  │                                                                 │   │
│  │  问题：即使只有 B 变化，仍需遍历所有节点                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Vue 3 Diff：Patch Flag 精准定位                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  新 VNode: [A, B(PatchFlag:TEXT), C, D, E]                      │   │
│  │  旧 VNode: [A, B(PatchFlag:TEXT), C, D, E]                      │   │
│  │                                                                 │   │
│  │  Diff 过程：                                                    │   │
│  │  A: 检查 PatchFlag → 无标记 → 跳过 ✅                           │   │
│  │  B: 检查 PatchFlag → TEXT 标记 → 比较文本 → 可能更新            │   │
│  │  C: 检查 PatchFlag → 无标记 → 跳过 ✅                           │   │
│  │  D: 检查 PatchFlag → 无标记 → 跳过 ✅                           │   │
│  │  E: 检查 PatchFlag → 无标记 → 跳过 ✅                           │   │
│  │                                                                 │   │
│  │  优化：只检查有 PatchFlag 的节点，其余直接跳过                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  性能对比：                                                             │
│  - Vue 2: 每个 VNode 都要检查是否变化                                   │
│  - Vue 3: 只检查有 PatchFlag 的 VNode，大幅减少检查次数                │
│  - 提升幅度：模板越复杂、静态内容越多，提升越明显                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 四、Composition API vs Options API

### 4.1 Options API 设计理念

Options API 是 Vue 2 经典的组件 API 设计，将组件逻辑按**选项类型**进行分类组织。

```javascript
// Vue 2 Options API
export default {
  // 数据
  data() {
    return {
      count: 0,
      user: null
    }
  },
  // 计算属性
  computed: {
    doubleCount() {
      return this.count * 2
    }
  },
  // 方法
  methods: {
    increment() {
      this.count++
    },
    fetchUser() {
      // 获取用户数据
    }
  },
  // 侦听器
  watch: {
    count(newVal) {
      console.log('count changed:', newVal)
    }
  },
  // 生命周期
  mounted() {
    this.fetchUser()
  }
}
```

**Options API 的问题：**
- 逻辑按类型分散在 `data`、`methods`、`computed`、`watch` 等不同选项中
- 同一功能的逻辑难以聚合
- 跨组件复用逻辑需要使用 Mixins（可能导致命名冲突和来源不清晰）

### 4.2 Composition API 设计理念

Composition API 是 Vue 3 全新的 API 设计，以**逻辑关注点**为组织原则。

```javascript
// Vue 3 Composition API
import { ref, computed, watch, onMounted } from 'vue'

export default {
  setup() {
    // 功能 1：计数器逻辑（所有相关代码聚合在一起）
    const count = ref(0)
    const doubleCount = computed(() => count.value * 2)
    const increment = () => count.value++
    watch(count, (newVal) => {
      console.log('count changed:', newVal)
    })
    
    // 功能 2：用户数据逻辑（独立聚合）
    const user = ref(null)
    const fetchUser = async () => {
      user.value = await api.getUser()
    }
    onMounted(fetchUser)
    
    return { count, doubleCount, increment, user, fetchUser }
  }
}
```

**Composition API 的优势：**
- 同一功能的逻辑聚合在一起，便于阅读和维护
- 逻辑复用更方便（使用组合函数，无需 Mixins）
- 更好的 TypeScript 类型推导
- 更灵活的代码组织

### 4.3 代码组织对比示例

#### 场景：实现一个搜索功能（带防抖、请求、结果展示）

**Vue 2 Options API 实现：**
```javascript
export default {
  data() {
    return {
      // 搜索相关数据
      keyword: '',
      results: [],
      loading: false,
      debounceTimer: null
    }
  },
  computed: {
    // 搜索相关计算
    hasResults() {
      return this.results.length > 0
    }
  },
  watch: {
    // 搜索相关侦听
    keyword() {
      this.debounceSearch()
    }
  },
  methods: {
    // 搜索相关方法
    debounceSearch() {
      clearTimeout(this.debounceTimer)
      this.debounceTimer = setTimeout(() => {
        this.doSearch()
      }, 300)
    },
    async doSearch() {
      this.loading = true
      this.results = await api.search(this.keyword)
      this.loading = false
    },
    clearResults() {
      this.results = []
    }
  }
}
// 问题：搜索相关的代码分散在 data/computed/watch/methods 中
// 在复杂组件中，很难追踪一个功能的所有相关代码
```

**Vue 3 Composition API 实现：**
```javascript
// 可复用的搜索组合函数
function useSearch() {
  const keyword = ref('')
  const results = ref([])
  const loading = ref(false)
  let debounceTimer = null

  const hasResults = computed(() => results.value.length > 0)

  const debounceSearch = () => {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(doSearch, 300)
  }

  const doSearch = async () => {
    loading.value = true
    results.value = await api.search(keyword.value)
    loading.value = false
  }

  const clearResults = () => {
    results.value = []
  }

  watch(keyword, debounceSearch)

  return {
    keyword, results, loading, hasResults,
    clearResults
  }
}

// 组件中使用
export default {
  setup() {
    // 搜索功能的所有代码聚合在一起
    const {
      keyword, results, loading, hasResults, clearResults
    } = useSearch()

    return { keyword, results, loading, hasResults, clearResults }
  }
}
// 优势：搜索逻辑完全聚合，可以在任何组件中复用
```

---

## 五、生命周期钩子的变化

### 5.1 Vue 2 生命周期

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 2 生命周期图                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  初始化阶段：                                                           │
│  beforeCreate → data 初始化 → created → 编译模板 → beforeMount         │
│       ↑                                 ↓                               │
│       │                              mount                             │
│       │                                 ↓                               │
│       │                              mounted                            │
│       │                                 ↓                               │
│       │                              挂载完成                           │
│                                                                         │
│  更新阶段：                                                             │
│  数据变化 → beforeUpdate → Virtual DOM diff → updated                   │
│                                                                         │
│  销毁阶段：                                                             │
│  销毁触发 → beforeDestroy → 销毁完成 → destroyed                         │
│                                                                         │
│  其他钩子：                                                             │
│  - activated: keep-alive 激活                                          │
│  - deactivated: keep-alive 停用                                        │
│  - errorCaptured: 错误捕获                                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Vue 3 生命周期

Vue 3 的生命周期钩子名称大部分保持不变，但提供了新的 `setup` 钩子和 Composition API 版本。

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 3 生命周期图                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  setup() ← 新增，取代 beforeCreate + created                            │
│    │                                                                    │
│    ▼                                                                    │
│  onBeforeMount() ← 对应 beforeMount                                    │
│    │                                                                    │
│    ▼                                                                    │
│  onMounted() ← 对应 mounted                                             │
│    │    - 可以访问 DOM                                                  │
│    │    - 可以获取子组件实例                                            │
│    │                                                                    │
│    ▼                                                                    │
│  onBeforeUpdate() ← 对应 beforeUpdate                                   │
│    │                                                                    │
│    ▼                                                                    │
│  onUpdated() ← 对应 updated                                            │
│    │                                                                    │
│    ▼                                                                    │
│  onBeforeUnmount() ← 对应 beforeDestroy                                 │
│    │                                                                    │
│    ▼                                                                    │
│  onUnmounted() ← 对应 destroyed                                         │
│    │                                                                    │
│    ▼                                                                    │
│  其他：                                                                 │
│  - onActivated / onDeactivated → keep-alive                             │
│  - onErrorCaptured → 错误捕获                                           │
│  - onRenderTracked → 渲染追踪（调试用）                                │
│  - onRenderTriggered → 渲染触发（调试用）                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 生命周期钩子对照

| Vue 2 (Options API) | Vue 3 (Composition API) | 执行时机 |
|---------------------|------------------------|---------|
| `beforeCreate` | `setup()` 之前 | 组件实例创建前 |
| `created` | `setup()` 之内 | 组件实例创建完成 |
| `beforeMount` | `onBeforeMount` | 挂载前 |
| `mounted` | `onMounted` | 挂载后（DOM 就绪） |
| `beforeUpdate` | `onBeforeUpdate` | 更新前 |
| `updated` | `onUpdated` | 更新后 |
| `beforeDestroy` | `onBeforeUnmount` | 卸载前 |
| `destroyed` | `onUnmounted` | 卸载后 |
| `activated` | `onActivated` | keep-alive 激活 |
| `deactivated` | `onDeactivated` | keep-alive 停用 |
| `errorCaptured` | `onErrorCaptured` | 错误捕获 |

### 5.3 迁移与注意事项

```javascript
// Vue 2 写法
export default {
  mounted() {
    this.fetchData()
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
  }
}

// Vue 3 Composition API 写法
import { onMounted, onBeforeUnmount } from 'vue'

export default {
  setup() {
    const handleResize = () => { /* ... */ }
    
    onMounted(() => {
      fetchData()
      window.addEventListener('resize', handleResize)
    })
    
    // 钩子注册在 setup 中，逻辑聚合更自然
    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize)
    })
  }
}

// 注意：
// 1. Vue 3 中钩子可以注册在 setup() 之外的普通函数中
// 2. 但必须在 setup() 同步执行阶段注册（不能在异步回调中）
// 3. <script setup> 中直接使用即可，无需 setup() 包裹
```

---

## 六、TypeScript 支持差异

### 6.1 Vue 2 的 TS 支持

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 2 TypeScript 支持现状                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. 需要额外的类型声明文件                                              │
│     - @types/vue（社区维护）                                             │
│     - 需要手动安装和配置                                                │
│                                                                         │
│  2. Options API 类型推导不够智能                                        │
│     - data 需要显式类型标注                                             │
│     - computed 返回类型需要手动指定                                      │
│     - methods 参数类型需要手动指定                                      │
│                                                                         │
│  3. 典型 Vue 2 TS 代码                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  <script lang="ts">                                              │   │
│  │  import { Component, Vue } from 'vue-property-decorator'         │   │
│  │                                                                 │   │
│  │  @Component({                                                    │   │
│  │    name: 'MyComponent'                                          │   │
│  │  })                                                              │   │
│  │  export default class MyComponent extends Vue {                  │   │
│  │    // 需要显式类型标注                                           │   │
│  │    msg: string = 'Hello'                                        │   │
│  │    count: number = 0                                            │   │
│  │                                                                 │   │
│  │    // computed 需要指定返回类型                                   │   │
│  │    get doubleCount(): number {                                   │   │
│  │      return this.count * 2                                       │   │
│  │    }                                                             │   │
│  │                                                                 │   │
│  │    // methods 参数需要指定类型                                    │   │
│  │    increment(amount: number): void {                             │   │
│  │      this.count += amount                                        │   │
│  │    }                                                             │   │
│  │  }                                                               │   │
│  │  </script>                                                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  问题：                                                                 │
│  - 需要 vue-class-component 和 vue-property-decorator 等额外库        │
│  - 类型推导不够完善，需要大量手动标注                                   │
│  - 代码量增加，开发效率低                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Vue 3 的 TS 支持

Vue 3 从底层就使用 TypeScript 编写，提供了一流的 TS 支持。

```javascript
// Vue 3 Composition API 原生 TS 支持
import { ref, computed, reactive } from 'vue'
import type { Ref } from 'vue'

// 1. ref 自动推导类型
const count = ref(0)           // Ref<number>
const message = ref('hello')   // Ref<string>
const isLoading = ref(false)   // Ref<boolean>

// 2. reactive 自动推导类型
const state = reactive({
  user: 'Alice',
  age: 25
})
// state.user: string
// state.age: number

// 3. computed 自动推导
const doubleCount = computed(() => count.value * 2)
// ComputedRef<number>

// 4. 泛型支持
function useList<T>(items: T[]) {
  const list = ref<T[]>(items)
  const add = (item: T) => list.value.push(item)
  const remove = (item: T) => {
    const index = list.value.indexOf(item)
    if (index > -1) list.value.splice(index, 1)
  }
  return { list, add, remove }
}

// 使用
const { list, add } = useList<string>(['apple', 'banana'])
add('orange')  // 类型安全
// add(123)  // ❌ 类型错误

// 5. defineProps / defineEmits 类型安全
// <script setup lang="ts">
// const props = defineProps<{
//   title: string
//   count?: number
// }>()
// const emit = defineEmits<{
//   (e: 'change', value: string): void
//   (e: 'update:count', value: number): void
// }>()
// </script>
```

### 6.3 类型推导对比

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 2 vs Vue 3 类型推导能力                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  场景 1：ref 类型推导                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  // Vue 2：需要手动标注                                         │   │
│  │  data() {                                                      │   │
│  │    return {                                                    │   │
│  │      count: 0 as number  // 需要 as number                     │   │
│  │    }                                                           │   │
│  │  }                                                             │   │
│  │                                                                 │   │
│  │  // Vue 3：自动推导                                             │   │
│  │  const count = ref(0)  // 自动推导为 Ref<number>                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  场景 2：computed 返回类型                                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  // Vue 2：需要指定返回类型                                     │   │
│  │  computed: {                                                   │   │
│  │    doubleCount(): number {  // 需要 : number                    │   │
│  │      return this.count * 2                                     │   │
│  │    }                                                           │   │
│  │  }                                                             │   │
│  │                                                                 │   │
│  │  // Vue 3：自动推导                                             │   │
│  │  const doubleCount = computed(() => count.value * 2)            │   │
│  │  // 自动推导为 ComputedRef<number>                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  场景 3：模板中的类型支持                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  // Vue 2：模板中无类型检查                                     │   │
│  │  <template>                                                    │   │
│  │    <div>{{ count }}</div>  <!-- 无类型提示 -->                 │   │
│  │  </template>                                                   │   │
│  │                                                                 │   │
│  │  // Vue 3：Volar 提供模板类型检查                               │   │
│  │  <template>                                                    │   │
│  │    <div>{{ count }}</div>  <!-- 有类型提示 -->                 │   │
│  │  </template>                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 七、编译优化策略

### 7.1 Vue 2 编译流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 2 编译流程                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  模板 → 解析 → AST → 代码生成 → Render 函数                             │
│                                                                         │
│  Vue 2 生成的 Render 函数示例：                                         │
│                                                                         │
│  render() {                                                             │
│    return _c('div', {                                                   │
│      class: ['container', { active: this.isActive }]                    │
│    }, [                                                                 │
│      _c('h1', [_v(this.message)]),                                     │
│      _c('button', {                                                     │
│        on: { click: this.handleClick }                                  │
│      }, [_v('提交')])                                                   │
│    ])                                                                   │
│  }                                                                     │
│                                                                         │
│  特点：                                                                 │
│  - 每次渲染都要完整执行 Render 函数                                     │
│  - 创建所有节点的 VNode                                                 │
│  - 运行时进行全量 Diff                                                  │
│  - 没有编译期优化标记                                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Vue 3 编译优化

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 3 编译优化全景                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  优化 1：静态提升（Hoisting Static）                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  编译前：                                                      │   │
│  │  <template>                                                    │   │
│  │    <div class="wrapper">                                       │   │
│  │      <h1>静态标题</h1>                                        │   │
│  │      <p>{{ message }}</p>                                      │   │
│  │    </div>                                                      │   │
│  │  </template>                                                   │   │
│  │                                                                 │   │
│  │  编译后（Vue 2）：                                             │   │
│  │  render() {                                                    │   │
│  │    return _c('div', { class: 'wrapper' }, [                   │   │
│  │      _c('h1', [_v('静态标题')]),                               │   │
│  │      _c('p', [_v(this.message)])                               │   │
│  │    ])                                                          │   │
│  │  }  // 每次渲染都创建 h1 的 VNode                              │   │
│  │                                                                 │   │
│  │  编译后（Vue 3）：                                             │   │
│  │  const _hoisted_1 = /* hoisted */                             │   │
│  │    createElementVNode("h1", null, "静态标题")                  │   │
│  │                                                                 │   │
│  │  render() {                                                    │   │
│  │    return (openBlock(),                                        │   │
│  │      createElementBlock("div", { class: "wrapper" }, [         │   │
│  │        _hoisted_1,  // 复用已创建的 VNode                       │   │
│  │        createElementVNode("p", null,                           │   │
│  │          toDisplayString(ctx.message), 1 /* TEXT */)           │   │
│  │      ]))                                                       │   │
│  │  }  // h1 的 VNode 只创建一次                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  优化 2：Patch Flag 标记                                                │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  为每个动态节点标记更新类型：                                    │   │
│  │  - TEXT (1): 动态文本                                          │   │
│  │  - CLASS (2): 动态 class                                       │   │
│  │  - STYLE (4): 动态 style                                       │   │
│  │  - PROPS (8): 动态 props                                       │   │
│  │                                                                 │   │
│  │  运行时只检查有 PatchFlag 的节点                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  优化 3：事件缓存（Event Caching）                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  // Vue 2：每次渲染创建新的事件处理函数                         │   │
│  │  onClick: function($event) {                                    │   │
│  │    return ctx.handleClick($event)                                │   │
│  │  }                                                              │   │
│  │                                                                 │   │
│  │  // Vue 3：事件缓存                                             │   │
│  │  onClick: _cache[0] || (_cache[0] = ($event) =>                  │   │
│  │    ($event).call(ctx.handleClick($event)))                       │   │
│  │  // 首次创建后缓存，后续渲染复用                                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  优化 4：Block Tree 块级更新                                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  openBlock() + createElementBlock() 包裹动态节点                │   │
│  │  构建时收集动态子节点到 dynamicChildren 数组                      │   │
│  │  更新时只遍历 dynamicChildren，跳过静态节点                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.3 Patch Flag 机制

#### 完整 Patch Flag 列表

```javascript
// Patch Flag 枚举值
export const enum PatchFlags {
  TEXT = 1,              // 动态文本节点
  CLASS = 2,             // 动态 class
  STYLE = 4,             // 动态 style
  PROPS = 8,             // 动态 props（不含 class/style）
  FULL_PROPS = 16,       // 动态 props（含 class/style）
  NEED_HYDRATION = 32,   // 需要 hydration
  STABLE_FRAGMENT = 64,  // 稳定的 Fragment
  KEYED_FRAGMENT = 128,  // 带 key 的 Fragment
  UNKEYED_FRAGMENT = 256,// 不带 key 的 Fragment
  REF = 512,             // 有 ref 引用
  BAIL = 1024            // 静态节点标记
}
```

#### Patch Flag 在运行时的使用

```javascript
// 简化的 Patch 函数示例
function patchElement(n1, n2) {
  const el = (n2.el = n1.el)
  const { patchFlag } = n2
  
  // PatchFlag 为 0：完全跳过
  if (patchFlag === 0) return
  
  // 检查动态文本
  if (patchFlag & PatchFlags.TEXT) {
    if (n1.children !== n2.children) {
      hostSetElementText(el, n2.children)
    }
  }
  
  // 检查动态 class
  if (patchFlag & PatchFlags.CLASS) {
    // 更新 class
  }
  
  // 检查动态 style
  if (patchFlag & PatchFlags.STYLE) {
    // 更新 style
  }
  
  // 检查动态 props
  if (patchFlag & PatchFlags.PROPS) {
    // 更新 props
  }
}
```

### 7.4 静态提升

#### 可静态提升的内容

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    静态提升规则                                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  可静态提升的条件：                                                     │
│  1. 节点没有动态绑定（无 Mustache 表达式）                              │
│  2. 节点没有动态 props（如 :class、:style、v-bind）                    │
│  3. 节点没有动态事件（如 @click、v-on）                                │
│  4. 节点不是 v-if/v-for 等指令的一部分                                  │
│  5. 节点文本内容完全静态                                                │
│                                                                         │
│  提升后的效果：                                                         │
│  - 编译时创建一次 VNode，存入常量                                       │
│  - 运行时直接复用，不再重新创建                                         │
│  - 大幅减少内存分配和 GC 压力                                           │
│                                                                         │
│  示例：                                                                 │
│  编译前模板：                                                           │
│  <div>                                                                   │
│    <h1>静态标题</h1>          ← 可提升                                  │
│    <p>{{ dynamic }}</p>       ← 不可提升（有动态绑定）                   │
│    <footer>页脚</footer>      ← 可提升                                  │
│  </div>                                                                 │
│                                                                         │
│  编译结果：                                                             │
│  // 提升的静态 VNode（模块级变量）                                      │
│  const _hoisted_1 = createElementVNode("h1", null, "静态标题")          │
│  const _hoisted_2 = createElementVNode("footer", null, "页脚")          │
│                                                                         │
│  render() {                                                             │
│    return (openBlock(),                                                 │
│      createElementBlock("div", null, [                                  │
│        _hoisted_1,                    // 复用                          │
│        createElementVNode("p", null,                                    │
│          toDisplayString(ctx.dynamic), 1),  // 动态节点                │
│        _hoisted_2                     // 复用                          │
│      ]))                                                                │
│  }                                                                     │
│                                                                         │
│  注意：Vite/Create Vue App 等脚手架默认启用静态提升                      │
│  可通过 compiler-hoist 选项关闭                                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 八、内部模块结构调整

### 8.1 Vue 2 模块结构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 2 模块结构                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  vue/                                                                   │
│  ├── src/                                                               │
│  │   ├── compiler/         # 模板编译                                   │
│  │   │   ├── parser/       # 模板解析                                  │
│  │   │   ├── codegen/      # 代码生成                                  │
│  │   │   └── directives/   # 指令处理                                  │
│  │   ├── core/             # 核心逻辑                                  │
│  │   │   ├── instance/     # 组件实例                                  │
│  │   │   ├── observer/     # 响应式系统                                │
│  │   │   ├── vdom/         # 虚拟 DOM                                  │
│  │   │   └── lifecycle.js  # 生命周期                                  │
│  │   ├── platforms/       # 平台相关                                   │
│  │   │   └── web/          # Web 平台实现                              │
│  │   ├── server/           # 服务端渲染                                 │
│  │   └── shared/           # 公共工具                                   │
│  └── package.json        # 单一包配置                                  │
│                                                                         │
│  问题：                                                                 │
│  - 所有代码耦合在一个仓库中                                             │
│  - 无法按需引入（Tree-shaking 困难）                                    │
│  - 模块间依赖复杂，难以独立迭代                                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Vue 3 模块结构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 3 模块结构（Monorepo）                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  vue-next/                                                              │
│  ├── packages/                                                          │
│  │   ├── reactivity/      # 响应式系统（独立包）                        │
│  │   │   └── @vue/reactivity                                            │
│  │   ├── runtime-core/    # 运行时核心（独立包）                        │
│  │   │   └── @vue/runtime-core                                          │
│  │   ├── runtime-dom/     # Web 平台运行时（独立包）                    │
│  │   │   └── @vue/runtime-dom                                           │
│  │   ├── runtime-ssr/     # SSR 运行时（独立包）                        │
│  │   │   └── @vue/runtime-ssr                                           │
│  │   ├── compiler-core/   # 编译核心（独立包）                          │
│  │   │   └── @vue/compiler-core                                         │
│  │   ├── compiler-dom/    # Web 编译（独立包）                          │
│  │   │   └── @vue/compiler-dom                                          │
│  │   ├── compiler-sfc/    # SFC 编译（独立包）                          │
│  │   │   └── @vue/compiler-sfc                                          │
│  │   ├── compiler-ssr/    # SSR 编译（独立包）                          │
│  │   │   └── @vue/compiler-ssr                                          │
│  │   ├── server-renderer/ # 服务端渲染器                                │
│  │   │   └── @vue/server-renderer                                       │
│  │   ├── global-bridge/   # 全局桥接                                    │
│  │   │   └── @vue/global-bridge                                         │
│  │   └── vue/             # 完整构建包（整合所有子包）                   │
│  │       └── vue                                                        │
│  ├── scripts/             # 构建脚本                                    │
│  └── package.json        # Monorepo 配置                                │
│                                                                         │
│  架构优势：                                                             │
│  - 每个模块独立，职责单一                                               │
│  - 可以按需引入（Tree-shaking）                                        │
│  - 各模块可以独立发布版本                                               │
│  - 便于维护和测试                                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.3 Monorepo 架构优势

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Monorepo 架构带来的优势                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. Tree-shaking 支持                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  // Vue 2：必须引入整个 vue.js                                  │   │
│  │  import Vue from 'vue'                                          │   │
│  │  // 即使只使用响应式，也加载了模板编译、SSR 等所有功能             │   │
│  │                                                                 │   │
│  │  // Vue 3：按需引入                                               │   │
│  │  import { ref, reactive, computed } from 'vue'                  │   │
│  │  // Vite/Rollup 等打包工具自动 Tree-shake                       │   │
│  │  // 只打包使用的代码，大幅减小体积                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  2. 体积对比                                                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Vue 2 运行时：~30KB（min+gzip）                                │   │
│  │  Vue 3 运行时：~10KB（min+gzip，核心功能）                      │   │
│  │  Vue 3 完整包：~30KB（min+gzip，包含所有功能）                   │   │
│  │                                                                 │   │
│  │  注意：Vue 3 完整包与 Vue 2 体积相当，但核心包只有 ~10KB          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  3. 模块解耦                                                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  可以只使用 @vue/reactivity，配合其他框架：                     │   │
│  │  import { reactive, effect } from '@vue/reactivity'            │   │
│  │  // 不依赖 Vue 的组件系统，独立使用响应式                        │   │
│  │                                                                 │   │
│  │  可以自定义渲染器：                                                │   │
│  │  import { createRenderer } from '@vue/runtime-core'            │   │
│  │  // 可以创建自定义的渲染目标（如 Canvas、WebGL、Terminal）       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  4. 独立迭代                                                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  各模块可以独立发版：                                             │   │
│  │  - @vue/reactivity 1.1.0                                        │   │
│  │  - @vue/runtime-dom 3.2.0                                       │   │
│  │  - @vue/compiler-sfc 3.1.0                                      │   │
│  │  - vue 3.2.0（整合所有子包）                                     │   │
│  │                                                                 │   │
│  │  便于独立修复 bug 和发布新功能                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 九、性能数据对比

### 9.1 综合性能对比

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 2 vs Vue 3 性能对比                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  基准测试结果（来源：Vue 官方 Benchmark）：                              │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  指标                │ Vue 2    │ Vue 3    │ 提升幅度          │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │  首屏渲染时间        │ 基准     │ 快 2x    │ ↓ 50%             │   │
│  │  更新渲染时间        │ 基准     │ 快 1.3~2x │ ↓ 23~50%          │   │
│  │  内存占用            │ 基准     │ 少 54%   │ ↓ 46%             │   │
│  │  运行时体积          │ ~30KB    │ ~10KB    │ ↓ 67%             │   │
│  │  完整包体积          │ ~30KB    │ ~30KB    │ ≈ 相同            │   │
│  │  代码组织效率        │ 一般     │ 高       │ ↑ 显著提升        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  关键性能提升来源：                                                     │
│  1. 响应式系统：Proxy 比 defineProperty 性能更优                       │
│  2. 虚拟 DOM：Patch Flag 减少 Diff 范围                                │
│  3. 编译优化：静态提升减少 VNode 创建                                   │
│  4. Tree-shaking：减小运行时体积                                       │
│  5. Composition API：减少内存分配                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 9.2 渲染性能对比

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    渲染性能对比（基准测试场景）                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  场景 1：10000 个节点的列表渲染                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Vue 2: ~150ms                                                  │   │
│  │  Vue 3: ~80ms                                                   │   │
│  │  提升：~47%                                                     │   │
│  │                                                                 │   │
│  │  原因：                                                          │   │
│  │  - Patch Flag 减少 Diff 范围                                     │   │
│  │  - 静态提升减少 VNode 创建                                       │   │
│  │  - Proxy 响应式性能更优                                          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  场景 2：频繁更新的组件                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Vue 2: ~12ms/帧                                                 │   │
│  │  Vue 3: ~6ms/帧                                                  │   │
│  │  提升：~50%                                                     │   │
│  │                                                                 │   │
│  │  原因：                                                          │   │
│  │  - 事件缓存减少函数创建                                          │   │
│  │  - Block Tree 缩小更新范围                                       │   │
│  │  - 优化的 Diff 算法                                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  场景 3：内存占用对比                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Vue 2: 10000 节点 → ~35MB 内存                                  │   │
│  │  Vue 3: 10000 节点 → ~16MB 内存                                  │   │
│  │  节省：~54%                                                     │   │
│  │                                                                 │   │
│  │  原因：                                                          │   │
│  │  - VNode 结构更精简                                              │   │
│  │  - 惰性响应式减少代理开销                                        │   │
│  │  - 静态节点复用                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 十、迁移指南与最佳实践

### 10.1 迁移策略

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 2 → Vue 3 迁移策略                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  策略 1：渐进式迁移（推荐）                                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  1. 使用 @vue/compat 兼容构建                                   │   │
│  │  2. 逐步将 Options API 组件迁移到 Composition API                │   │
│  │  3. 先迁移新增功能，再重构旧代码                                 │   │
│  │  4. 保持 Vue 2 运行时兼容（大部分代码无需修改）                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  策略 2：全量迁移                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  1. 新建 Vue 3 项目                                             │   │
│  │  2. 使用 Vite 作为构建工具                                      │   │
│  │  3. 逐步迁移组件                                                │   │
│  │  4. 利用迁移构建工具批量修改                                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  迁移工具：                                                             │
│  - @vue/compat: 兼容构建，自动处理大部分不兼容变更                      │
│  - codemod 脚本: 批量转换 Options API → Composition API                 │
│  - Volar: VS Code 插件，提供智能提示                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 10.2 常见兼容性问题

| 问题类型 | Vue 2 行为 | Vue 3 行为 | 解决方案 |
|---------|-----------|-----------|---------|
| `v-model` 自定义 | `value` + `input` 事件 | `modelValue` + `update:modelValue` | 使用 `defineModel` 或手动映射 |
| 生命周期命名 | `beforeDestroy` / `destroyed` | `beforeUnmount` / `unmounted` | 手动重命名 |
| 根元素限制 | 单一根元素 | 支持多根元素（Fragments） | 无需修改 |
| 过滤器 | `filter` 管道符 | 已移除 | 改为方法或计算属性 |
| `$children` | 直接子组件数组 | 已移除 | 使用 `$refs` 或 provide/inject |
| `$listeners` | 父组件事件监听 | 已合并到 `$attrs` | 直接使用 `$attrs` |
| `sync` 修饰符 | `v-model` 替代 | 使用 `v-model` 替代 | 迁移到 `v-model` |

### 10.3 最佳实践建议

#### 组件设计最佳实践

```javascript
// 1. 优先使用 Composition API + <script setup>
// MyComponent.vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const props = defineProps<{
  title: string
  count?: number
}>()

const emit = defineEmits<{
  (e: 'change', value: string): void
}>()

const localCount = ref(props.count ?? 0)
const doubleCount = computed(() => localCount.value * 2)

onMounted(() => {
  console.log('Component mounted')
})
</script>

// 2. 逻辑复用封装为组合函数
// composables/useUser.ts
export function useUser(userId: Ref<string>) {
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<Error | null>(null)

  const fetchUser = async () => {
    loading.value = true
    try {
      user.value = await api.getUser(userId.value)
    } catch (e) {
      error.value = e as Error
    } finally {
      loading.value = false
    }
  }

  watch(userId, fetchUser, { immediate: true })

  return { user, loading, error, fetchUser }
}

// 3. 性能优化要点
// - 使用 shallowRef/shallowReactive 处理深层数据
// - 使用 markRaw 标记不需要响应的对象
// - 使用 computed 缓存计算结果
// - 合理使用 v-memo 缓存模板结果
```

---

## 十一、总结与选型建议

### 11.1 核心差异总结

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 2 vs Vue 3 核心差异总结                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  维度              │ Vue 2                    │ Vue 3                    │
│  ─────────────────────────────────────────────────────────────────      │
│  响应式系统        │ Object.defineProperty   │ Proxy (惰性、全覆盖)       │
│  虚拟 DOM          │ 全量 Diff               │ Patch Flag + Block Tree   │
│  API 设计          │ Options API             │ Composition API           │
│  类型支持          │ 需额外声明文件          │ 原生 TypeScript 支持      │
│  编译优化          │ 无                      │ 静态提升 + 事件缓存       │
│  架构设计          │ 单体仓库               │ Monorepo + Tree-shaking  │
│  运行时体积        │ ~30KB                  │ ~10KB（可裁剪）           │
│  性能              │ 基准                   │ 提升 1.3~2x              │
│  浏览器支持        │ IE9+                   │ 现代浏览器（不支持 IE）   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 11.2 选型建议

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    选型决策树                                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  你的项目处于什么阶段？                                                  │
│  ├── 新项目                                                             │
│  │   └── ✅ 选择 Vue 3                                                  │
│  │       - 使用 Vite + TypeScript + Composition API                     │
│  │       - 享受最新特性和性能优势                                       │
│  │                                                                      │
│  ├── Vue 2 现有项目（可维护）                                           │
│  │   ├── 项目复杂度低、团队熟悉 Vue 2                                   │
│  │   │   └── ⚠️ 可暂不迁移，继续维护                                    │
│  │   ├── 项目需要长期维护、团队愿意学习新技术                            │
│  │   │   └── ✅ 渐进式迁移到 Vue 3                                      │
│  │   └── 项目需要 Vue 3 新特性                                          │
│  │       └── ✅ 迁移到 Vue 3                                            │
│  │                                                                      │
│  ├── 需要 IE 支持                                                       │
│  │   └── ⚠️ 继续使用 Vue 2（Vue 3 不支持 IE）                           │
│  │                                                                      │
│  └── 需要 SSR                                                           │
│      ├── Nuxt 2（基于 Vue 2）                                           │
│      │   └── 适合已有 Nuxt 2 项目                                      │
│      └── Nuxt 3（基于 Vue 3）                                           │
│          └── 适合新项目或愿意迁移的项目                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 11.3 学习资源推荐

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 3 学习资源                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  官方资源：                                                             │
│  - Vue 3 官方文档（https://vuejs.org）                                  │
│  - Vue 3 源码（https://github.com/vuejs/core）                           │
│  - Vue 3 RFC（https://github.com/vuejs/rfcs）                           │
│                                                                         │
│  推荐书籍：                                                             │
│  - 《Vue.js 设计与实现》（霍春阳）                                       │
│  - 《Vue 3 组合式 API 深入剖析》                                        │
│                                                                         │
│  在线教程：                                                             │
│  - Vue Mastery（https://www.vuemastery.com）                            │
│  - Vue School（https://vueschool.io）                                   │
│  - 尤雨溪的 Vue 3 深度分享                                              │
│                                                                         │
│  实战项目：                                                             │
│  - Vue 3 + Vite + TypeScript 脚手架                                     │
│  - Element Plus（基于 Vue 3 的组件库）                                   │
│  - Pinia（推荐的 Vue 3 状态管理）                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 附录：术语表

| 术语 | 英文名 | 说明 |
|------|--------|------|
| 响应式 | Reactivity | 数据变化自动触发视图更新的机制 |
| 代理 | Proxy | ES6 原生对象代理，Vue 3 响应式的基础 |
| 虚拟 DOM | Virtual DOM | 真实 DOM 的 JavaScript 对象表示 |
| 差异算法 | Diff Algorithm | 比较新旧虚拟 DOM 树的算法 |
| 组合式 API | Composition API | Vue 3 新的函数式 API 设计 |
| 选项式 API | Options API | Vue 2 经典的选项式 API 设计 |
| 静态提升 | Hoisting | 将静态节点提升到渲染函数外 |
| 补丁标记 | Patch Flag | 编译期为动态节点添加的标记 |
| 块级更新 | Block Tree | 将模板分割为块，实现精细化更新 |
| 按需加载 | Tree-shaking | 打包时移除未使用的代码 |
| 模块仓库 | Monorepo | 单仓库管理多个包的架构 |
| 生命周期 | Lifecycle | 组件从创建到销毁的全过程 |

---

> **文档版本**：v1.0  
> **适用版本**：Vue 3.x / Vue 2.x  
> **最后更新**：2026-08  
> **参考来源**：Vue 官方文档、Vue 源码、Vue RFCs