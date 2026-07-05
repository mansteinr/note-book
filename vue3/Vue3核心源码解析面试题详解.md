# Vue.js 3.0 核心源码解析面试题详解

> 本文档基于 [vuejs/core](https://github.com/vuejs/core) 官方源码编写，系统化考察 Vue 3 源码理解深度。
> 题型包括：选择题（基础概念）、简答题（原理阐述）、分析题（源码分析）、编程题（实战编码）。
> 难度分布：基础 30% / 进阶 40% / 高级 30%。

---

## 目录

- [一、架构设计与核心概念](#一架构设计与核心概念)
- [二、响应式系统源码解析](#二响应式系统源码解析)
- [三、虚拟DOM与Diff算法源码解析](#三虚拟dom与diff算法源码解析)
- [四、组件系统与生命周期源码解析](#四组件系统与生命周期源码解析)
- [五、编译原理与优化源码解析](#五编译原理与优化源码解析)
- [六、调度机制与性能优化源码解析](#六调度机制与性能优化源码解析)

---

## 一、架构设计与核心概念

### 【选择题】

**1.1 Vue 3 核心仓库 `vuejs/core` 采用的代码组织方式是？**

A. 单一仓库（Single Repo）
B. Monorepo + Yarn Workspaces
C. Monorepo + pnpm Workspaces
D. 多仓库（Multi Repo）

**答案：C**

**解析**：Vue 3 核心仓库采用 monorepo 架构，使用 pnpm workspaces 管理多个包。`pnpm` 相比 yarn 有更好的磁盘空间效率和更严格的依赖隔离（避免幽灵依赖）。仓库根目录的 `pnpm-workspace.yaml` 定义了工作空间配置。

---

**1.2 以下 Vue 3 包中，哪一个可以完全独立运行，不依赖其他 Vue 包？**

A. `@vue/runtime-core`
B. `@vue/runtime-dom`
C. `@vue/reactivity`
D. `@vue/compiler-core`

**答案：C**

**解析**：`@vue/reactivity` 是响应式系统包，设计上完全独立，只依赖 `@vue/shared`。它可以在非 Vue 环境（如 React、原生 JS）中单独使用。这也是 Vue 3 架构解耦的重要体现。其他包的依赖关系：`runtime-dom` → `runtime-core` → `reactivity`。

---

**1.3 Vue 3 的 `createApp` 返回的应用实例与 Vue 2 的根实例（`new Vue()`）相比，以下说法正确的是？**

A. Vue 3 的应用实例仍然可以作为响应式数据容器
B. Vue 3 的应用实例是一个轻量级对象，不再承载响应式数据
C. Vue 3 一个应用实例可以挂载到多个 DOM 节点
D. Vue 3 的应用实例自带全局状态管理

**答案：B**

**解析**：Vue 3 的 `createApp` 返回一个轻量级应用实例，主要提供 `use`、`component`、`directive`、`mount`、`unmount` 等方法，不再像 Vue 2 的根实例那样承载 data/computed/methods。一个应用实例只能挂载到一个 DOM 节点（调用多次 mount 会警告）。这种设计避免了全局污染。

```typescript
// Vue 2：根实例承载一切
const app = new Vue({
  data: { count: 0 },
  methods: { inc() { this.count++ } }
})

// Vue 3：应用实例只管注册，状态由组件管理
const app = createApp(App)
app.use(pinia).use(router).mount('#app')
```

---

**1.4 关于 Vue 3 的 `ShapeFlags` 设计，以下描述错误的是？**

A. `ShapeFlags` 使用位运算标记 VNode 类型
B. `ELEMENT = 1`，`COMPONENT = 1 << 2`
C. 一个 VNode 可以同时具有多个 ShapeFlag
D. `ShapeFlags` 主要用于编译阶段优化

**答案：D**

**解析**：`ShapeFlags` 主要用于**运行时**的 patch 阶段，通过位运算快速判断 VNode 类型并选择对应的处理函数（`processElement`/`processComponent`/`processText`）。位运算的优势在于可以用一个数字表示多种类型的组合，判断时用 `&` 操作即可。

```typescript
// packages/runtime-core/src/shapeFlags.ts
export const enum ShapeFlags {
  ELEMENT = 1,
  FUNCTIONAL_COMPONENT = 1 << 1,
  STATEFUL_COMPONENT = 1 << 2,
  TEXT_CHILDREN = 1 << 3,
  ARRAY_CHILDREN = 1 << 4,
  SLOTS_CHILDREN = 1 << 5,
  COMPONENT = ShapeFlags.STATEFUL_COMPONENT | ShapeFlags.FUNCTIONAL_COMPONENT
}
// patch 时：if (shapeFlag & ShapeFlags.ELEMENT) { ... }
```

---

### 【简答题】

**1.5 请阐述 Vue 3 采用 Monorepo 架构的设计优势，以及各核心包之间的依赖关系。**

**参考答案**：

#### Monorepo 架构优势

1. **代码复用**：`@vue/shared` 包提供公共工具函数，避免重复代码
2. **独立发布**：每个包可独立版本发布，用户可按需引入
3. **解耦设计**：`reactivity` 可脱离 Vue 在其他框架使用
4. **统一管理**：共享构建配置、测试配置、CI/CD 流程
5. **依赖清晰**：pnpm workspaces 严格管理包间依赖，避免幽灵依赖

#### 包依赖关系

```
@vue/vue (入口包)
  ├── @vue/runtime-dom
  │     └── @vue/runtime-core
  │           ├── @vue/reactivity
  │           └── @vue/shared
  └── @vue/compiler-dom
        └── @vue/compiler-core
              └── @vue/shared

@vue/compiler-sfc
  ├── @vue/compiler-dom
  ├── @vue/compiler-ssr
  └── @vue/shared
```

#### 设计哲学

- **关注点分离**：编译器、运行时、响应式系统各自独立
- **平台无关**：`runtime-core` 不包含任何 DOM API，通过 `runtime-dom` 注入平台操作
- **按需引入**：用户可以只用 `@vue/reactivity`，不必引入完整 Vue

---

## 二、响应式系统源码解析

### 【选择题】

**2.1 Vue 3 响应式系统中，存储依赖关系的数据结构是？**

A. `Map<target, Map<key, Set<effect>>>`
B. `WeakMap<target, Map<key, Set<effect>>>`
C. `WeakMap<target, WeakMap<key, Set<effect>>>`
D. `Map<target, Set<effect>>`

**答案：B**

**解析**：Vue 3 使用 `WeakMap<target, Map<key, Set<effect>>>` 三层结构：

- **外层 WeakMap**：key 是原始对象，value 是 depsMap。用 WeakMap 是为了让 target 被回收时依赖关系自动清除，避免内存泄漏。
- **中间 Map**：key 是属性名，value 是 dep（Set）。
- **内层 Set**：存储该属性的所有 effect（依赖此属性的副作用函数）。

```typescript
// packages/reactivity/src/effect.ts
type KeyDep = Set<ReactiveEffect>
type DepsMap = Map<any, KeyDep>
type TargetMap = WeakMap<object, DepsMap>

const targetMap: TargetMap = new WeakMap()
```

---

**2.2 关于 Vue 3 的 `reactive` 和 `readonly`，以下说法正确的是？**

A. `reactive` 代理的对象可以被修改，`readonly` 代理的对象完全不可访问
B. 同一个对象同时被 `reactive` 和 `readonly` 包裹会产生两个独立的代理
C. `readonly(reactive(obj))` 会生成一个只读的响应式代理
D. `readonly` 的 get 拦截器中不会进行依赖收集

**答案：C**

**解析**：`readonly(reactive(obj))` 是 Vue 3 常见模式，生成一个**只读的响应式代理**。`readonly` 的 get 拦截器仍然会进行 `track`（依赖收集），但 set 拦截器会发出警告并阻止修改。Vue 3 内部用 `readonlyMap` 和 `reactiveMap` 两个 WeakMap 分别缓存，避免重复代理。

```typescript
// 源码核心逻辑
function createReactiveObject(target, isReadonly, baseHandlers, proxyMap) {
  const existingProxy = proxyMap.get(target)
  if (existingProxy) return existingProxy  // 缓存命中
  
  const proxy = new Proxy(target, baseHandlers)
  proxyMap.set(target, proxy)
  return proxy
}

// readonly 的 get 中仍然 track
function get(target, key, receiver) {
  if (key === ReactiveFlags.IS_READONLY) return true
  track(target, key)  // 依然收集依赖
  return Reflect.get(target, key, receiver)
}
```

---

**2.3 在 Vue 3 的 `effect` 系统中，为什么每次执行 effect 前需要调用 `cleanup` 清除旧依赖？**

A. 为了释放内存
B. 为了避免 effect 遗留在不再访问的属性依赖中，导致无效触发
C. 为了防止循环引用
D. 为了提高执行性能

**答案：B**

**解析**：由于 effect 内部可能存在条件分支，不同执行路径访问的属性可能不同。如果不清理旧依赖，之前访问过但本次不再访问的属性仍然保留对该 effect 的引用，导致属性变化时无效触发 effect。`cleanup` 会从所有依赖该 effect 的 dep（Set）中移除自己，然后重新执行时重新收集。

```typescript
// 问题示例
const state = reactive({ flag: true, a: 1, b: 2 })
effect(() => {
  if (state.flag) {
    console.log(state.a)  // 依赖 flag 和 a
  } else {
    console.log(state.b)  // 依赖 flag 和 b
  }
})

state.flag = false
// 如果不 cleanup：a 变化仍会触发 effect（但实际不需要）
// cleanup 后：只依赖 flag 和 b，a 变化不再触发
```

---

**2.4 `shallowReactive` 和 `reactive` 的核心区别在于？**

A. `shallowReactive` 不进行依赖收集
B. `shallowReactive` 只代理对象的第一层属性，深层属性不转为响应式
C. `shallowReactive` 使用 Object.defineProperty 实现
D. `shallowReactive` 不能触发视图更新

**答案：B**

**解析**：`shallowReactive` 只对对象的第一层属性做响应式处理，深层属性保持原样。其 get 拦截器不会递归调用 `reactive()`：

```typescript
// reactive 的 get：深层代理
get(target, key, receiver) {
  const result = Reflect.get(target, key, receiver)
  if (isObject(result)) {
    return reactive(result)  // 递归代理
  }
  return result
}

// shallowReactive 的 get：不递归
get(target, key, receiver) {
  track(target, key)  // 仍然收集第一层依赖
  return Reflect.get(target, key, receiver)  // 不递归代理深层
}
```

适用场景：只需监听顶层属性变化时，避免深层代理的性能开销。

---

### 【简答题】

**2.5 请阐述 Vue 3 中 `ref` 的实现原理，并解释为什么 `ref` 可以处理基本类型而 `reactive` 不行。**

**参考答案**：

#### `ref` 的核心实现

`ref` 通过**类实例 + 访问器属性**实现响应式，而非 Proxy（因为 Proxy 无法代理基本类型）：

```typescript
// packages/reactivity/src/ref.ts
class RefImpl<T> {
  _value: T
  _rawValue: T
  dep: Dep = new Dep()
  public readonly __v_isRef = true

  constructor(value: T, public readonly __v_isShallow: boolean) {
    this._rawValue = this.__v_isShallow ? value : toRaw(value)
    // 对象类型会转为 reactive
    this._value = this.__v_isShallow ? value : toReactive(value)
  }

  get value() {
    this.dep.track()  // 依赖收集
    return this._value
  }

  set value(newVal) {
    const useDirectValue = this.__v_isShallow || isShallow(newVal) || isReadonly(newVal)
    newVal = useDirectValue ? newVal : toRaw(newVal)
    
    if (hasChanged(newVal, this._rawValue)) {
      this._rawValue = newVal
      this._value = useDirectValue ? newVal : toReactive(newVal)
      this.dep.trigger()  // 触发更新
    }
  }
}
```

#### 为什么 `ref` 能处理基本类型

1. **Proxy 的限制**：Proxy 只能代理对象，`new Proxy(100, handler)` 会抛出 `TypeError`
2. **ref 的解决方案**：用类实例包装基本类型，通过 `get value()` / `set value()` 访问器实现拦截
3. **自动解包**：模板中和 `reactive` 对象中的 `ref` 会自动解包（`.value`）

#### `toReactive` 的作用

```typescript
// packages/reactivity/src/ref.ts
export function toReactive<T>(value: T): T {
  return isObject(value) ? reactive(value) : value
}
```

当 `ref` 的值是对象时，内部会调用 `reactive` 转为响应式代理。所以 `ref({ count: 0 })` 的深层属性也是响应式的。

---

### 【分析题】

**2.6 请阅读以下 Vue 3 源码片段（简化版 `trigger` 函数），分析每个步骤的作用，并解释 `ITERATE_KEY` 的意义。**

```typescript
// 简化版 trigger 源码
export function trigger(target, key, type, newValue, oldValue) {
  const depsMap = targetMap.get(target)
  if (!depsMap) return  // 没有依赖，直接返回

  const effects = new Set<ReactiveEffect>()

  // 步骤1
  const dep = depsMap.get(key)
  if (dep) {
    dep.forEach(e => effects.add(e))
  }

  // 步骤2
  if (type === 'ADD') {
    const iterateEffects = depsMap.get(ITERATE_KEY)
    if (iterateEffects) {
      iterateEffects.forEach(e => effects.add(e))
    }
  }

  // 步骤3
  if (type === 'ADD' && Array.isArray(target)) {
    const lengthEffects = depsMap.get('length')
    if (lengthEffects) {
      lengthEffects.forEach(e => effects.add(e))
    }
  }

  // 步骤4
  triggerEffects(effects)
}
```

**参考答案**：

#### 逐步分析

**步骤1：收集直接依赖**
- 从 `depsMap` 中取出当前 `key` 对应的 `dep`（Set<effect>）
- 这些是直接依赖该属性的 effect，加入到待执行集合
- 场景：`state.count` 变化时，访问了 `state.count` 的 effect 会被触发

**步骤2：处理新增属性 → ITERATE_KEY**
- 当操作类型是 `ADD`（新增属性）时，需要触发对对象**遍历操作**的 effect
- `ITERATE_KEY` 是一个特殊的 Symbol，在 `ownKeys` 拦截器中收集依赖时使用
- 场景：`for...in` 遍历对象时，依赖的是所有 key 的集合。新增属性改变了 key 集合，所以需要重新执行遍历

```typescript
// ownKeys 拦截器（遍历操作触发）
ownKeys(target) {
  track(target, Array.isArray(target) ? 'length' : ITERATE_KEY)
  return Reflect.ownKeys(target)
}
```

**步骤3：处理数组新增元素**
- 数组新增元素时，`length` 会变化
- 直接依赖 `length` 的 effect 需要被触发
- 场景：`arr.push(1)` 导致 `length` 变化，`arr.length` 的依赖需要更新

**步骤4：执行所有 effect**
- 统一执行收集到的所有 effect
- 使用 `Set` 去重，避免同一 effect 被多次触发

#### ITERATE_KEY 的意义

`ITERATE_KEY` 是 Vue 3 内部定义的特殊 key（`Symbol('iterate')`），用于追踪对象的遍历操作（`for...in`、`Object.keys` 等）。当对象新增或删除属性时，遍历结果会变化，因此需要触发依赖 `ITERATE_KEY` 的 effect。这是 Vue 3 解决"新增属性响应式"的核心机制，而 Vue 2 需要 `$set` 才能实现。

---

### 【编程题】

**2.7 请手写一个简化版的 Vue 3 响应式系统，包含 `reactive`、`ref`、`effect`、`track`、`trigger`，并支持嵌套 effect。**

**参考答案**：

```typescript
// ===== 核心数据结构 =====
let activeEffect: ReactiveEffect | null = null
const effectStack: ReactiveEffect[] = []
const targetMap = new WeakMap<object, Map<any, Set<ReactiveEffect>>>()

// ===== ReactiveEffect 类 =====
class ReactiveEffect {
  deps: Set<ReactiveEffect>[] = []
  active = true

  constructor(public fn: () => any, public scheduler?: () => void) {}

  run() {
    if (!this.active) return this.fn()

    // 防止无限嵌套（同一 effect 递归调用）
    let last = activeEffect
    while (last) {
      if (last === this) return
      last = last.deps.length ? undefined : undefined // 简化处理
    }

    try {
      // 清理旧依赖（条件分支变化时避免无效触发）
      cleanup(this)

      // 入栈，设置当前 effect
      effectStack.push(this)
      activeEffect = this

      return this.fn()
    } finally {
      // 出栈，恢复外层 effect
      effectStack.pop()
      activeEffect = effectStack[effectStack.length - 1] || null
    }
  }

  stop() {
    if (this.active) {
      cleanup(this)
      this.active = false
    }
  }
}

// 清理 effect 在所有 dep 中的引用
function cleanup(effect: ReactiveEffect) {
  effect.deps.forEach(dep => dep.delete(effect))
  effect.deps.length = 0
}

// ===== effect 函数 =====
export function effect(fn: () => any, options?: { scheduler?: () => void }) {
  const _effect = new ReactiveEffect(fn, options?.scheduler)
  _effect.run()  // 首次立即执行

  const runner = _effect.run.bind(_effect)
  ;(runner as any).effect = _effect
  return runner
}

// ===== track 依赖收集 =====
export function track(target: object, key: any) {
  if (!activeEffect) return

  let depsMap = targetMap.get(target)
  if (!depsMap) {
    targetMap.set(target, (depsMap = new Map()))
  }

  let dep = depsMap.get(key)
  if (!dep) {
    depsMap.set(key, (dep = new Set()))
  }

  // 双向引用：dep 记住 effect，effect 也记住 dep（用于 cleanup）
  dep.add(activeEffect)
  activeEffect.deps.push(dep)
}

// ===== trigger 触发更新 =====
export function trigger(target: object, key: any) {
  const depsMap = targetMap.get(target)
  if (!depsMap) return

  const dep = depsMap.get(key)
  if (!dep) return

  // 复制一份再遍历，避免 effect 执行时修改 Set 导致无限循环
  const effects = new Set(dep)
  effects.forEach(effect => {
    // 避免无限递归：effect 执行时又修改了同一个属性
    if (effect !== activeEffect) {
      if (effect.scheduler) {
        effect.scheduler()  // 有调度器用调度器（如 computed）
      } else {
        effect.run()
      }
    }
  })
}

// ===== reactive 实现 =====
const reactiveMap = new WeakMap<object, any>()

export function reactive<T extends object>(target: T): T {
  if (!isObject(target)) return target

  // 如果已经是 reactive，直接返回
  const existing = reactiveMap.get(target)
  if (existing) return existing

  const proxy = new Proxy(target, {
    get(target: any, key: string | symbol, receiver: any) {
      // 特殊标记
      if (key === '__v_isReactive') return true
      if (key === '__v_raw') return target

      track(target, key)

      const result = Reflect.get(target, key, receiver)

      // 懒代理：访问时才递归代理子对象
      if (isObject(result)) {
        return reactive(result)
      }
      return result
    },

    set(target: any, key: string | symbol, value: any, receiver: any) {
      const oldValue = target[key]
      const hadKey = isArray(target) && isIntegerKey(key)
        ? Number(key) < target.length
        : Object.prototype.hasOwnProperty.call(target, key)

      const result = Reflect.set(target, key, value, receiver)

      // 确保 receiver 是 target 的代理（避免原型链上的 set 触发）
      if (target === toRaw(receiver)) {
        if (!hadKey) {
          trigger(target, key)  // 新增属性
        } else if (hasChanged(value, oldValue)) {
          trigger(target, key)  // 修改属性
        }
      }

      return result
    },

    deleteProperty(target: any, key: string | symbol) {
      const hadKey = Object.prototype.hasOwnProperty.call(target, key)
      const result = Reflect.deleteProperty(target, key)
      if (hadKey && result) {
        trigger(target, key)
      }
      return result
    },

    has(target: any, key: string | symbol) {
      track(target, key)
      return Reflect.has(target, key)
    },

    ownKeys(target: any) {
      // 遍历操作依赖特殊 key
      track(target, isArray(target) ? 'length' : ITERATE_KEY)
      return Reflect.ownKeys(target)
    }
  })

  reactiveMap.set(target, proxy)
  return proxy
}

// ===== ref 实现 =====
export function ref<T>(value: T) {
  if (isRef(value)) return value

  return new RefImpl(value)
}

class RefImpl<T> {
  _value: T
  dep: Set<ReactiveEffect> = new Set()
  __v_isRef = true

  constructor(value: T) {
    this._value = isObject(value) ? reactive(value as any) : value
  }

  get value() {
    if (activeEffect) {
      // 复用 track 机制
      let depsMap = targetMap.get(this)
      if (!depsMap) {
        targetMap.set(this, (depsMap = new Map()))
      }
      let dep = depsMap.get('value')
      if (!dep) {
        depsMap.set('value', (dep = new Set()))
      }
      dep.add(activeEffect)
      activeEffect.deps.push(dep)
    }
    return this._value
  }

  set value(newVal: T) {
    if (hasChanged(newVal, this._value)) {
      this._value = isObject(newVal) ? reactive(newVal as any) : newVal
      // 触发更新
      let depsMap = targetMap.get(this)
      let dep = depsMap?.get('value')
      if (dep) {
        const effects = new Set(dep)
        effects.forEach(effect => {
          if (effect !== activeEffect) {
            effect.run()
          }
        })
      }
    }
  }
}

// ===== 工具函数 =====
const ITERATE_KEY = Symbol('iterate')

function isObject(val: any): val is object {
  return val !== null && typeof val === 'object'
}
function isArray(val: any): val is any[] {
  return Array.isArray(val)
}
function isIntegerKey(key: any): boolean {
  return typeof key === 'string' && key !== 'NaN' && key[0] !== '-' && '' + parseInt(key, 10) === key
}
function hasChanged(a: any, b: any): boolean {
  return !Object.is(a, b)
}
function toRaw(observed: any): any {
  return (observed && observed.__v_raw) || observed
}
function isRef(r: any): r is RefImpl<any> {
  return !!(r && r.__v_isRef === true)
}

// ===== 测试用例 =====
const state = reactive({ count: 0, nested: { value: 1 } })
effect(() => {
  console.log('count:', state.count)  // 0
  console.log('nested:', state.nested.value)  // 1
})
state.count++        // 触发：count: 1
state.nested.value++ // 触发：nested: 2（懒代理生效）

const num = ref(0)
effect(() => console.log('num:', num.value))  // 0
num.value = 10  // 触发：num: 10

// 嵌套 effect
effect(() => {
  console.log('outer:', state.count)
  effect(() => {
    console.log('inner:', state.count)
  })
})
```

**评分标准**：
- 实现 reactive + effect + track/trigger：60分
- 支持 ref 和懒代理：80分
- 支持 cleanup、嵌套 effect、防递归：100分

---

## 三、虚拟DOM与Diff算法源码解析

### 【选择题】

**3.1 Vue 3 的 VNode 中 `patchFlag` 字段的主要作用是？**

A. 标记 VNode 是否需要被 patch
B. 在编译期标记动态节点的内容类型，运行时按需 patch
C. 记录 VNode 被更新的次数
D. 标记 VNode 的优先级

**答案：B**

**解析**：`patchFlag` 是 Vue 3 编译优化的核心。编译器在编译模板时，会分析出每个节点哪些部分是动态的（会变化），并用位运算标记。运行时 patch 阶段，只需更新被标记的部分，跳过静态内容。

```typescript
// 编译前
<div :class="cls" :id="staticId">{{ msg }}</div>

// 编译后（简化）
createVNode("div", { class: cls, id: staticId }, msg, PatchFlags.TEXT | PatchFlags.CLASS)
// patchFlag = TEXT(1) | CLASS(2) = 3

// 运行时 patch：只比较 class 和 text，跳过 id
if (patchFlag & PatchFlags.CLASS) { /* 更新 class */ }
if (patchFlag & PatchFlags.TEXT) { /* 更新 text */ }
```

---

**3.2 在 Vue 3 的 Diff 算法中，使用"最长递增子序列（LIS）"的目的是？**

A. 找出需要删除的节点
B. 找出需要新增的节点
C. 找出不需要移动的节点，最小化 DOM 移动操作
D. 对节点进行排序

**答案：C**

**解析**：LIS 算法找出新旧子节点中**相对顺序不变的最长节点序列**，这些节点不需要移动。其他不在序列中的节点才需要移动。这样可以最小化 DOM 移动操作次数，提升性能。

```typescript
// 假设旧节点顺序：A B C D E
// 新节点顺序：D A B C E

// newIndexToOldIndexMap（新节点在旧节点中的索引 +1，0表示新增）：
// D=4, A=1, B=2, C=3, E=5  →  [4, 1, 2, 3, 5]

// LIS: [1, 2, 3, 5] → 对应 A, B, C, E（不需要移动）
// 只有 D 需要移动到最前面
```

---

**3.3 Vue 3 中 `Fragment`（片段）的作用是？**

A. 将多个组件打包成一个
B. 允许组件有多个根节点
C. 分割大型模板
D. 实现懒加载

**答案：B**

**解析**：Vue 2 要求组件必须有单个根节点。Vue 3 引入 `Fragment`，允许组件返回多个根节点的 VNode 树。`Fragment` 本身不渲染真实 DOM，只是逻辑容器。

```typescript
// Vue 3 组件可以有多个根节点
const App = {
  template: `
    <header>Title</header>
    <main>Content</main>
    <footer>Footer</footer>
  `
}

// 编译后生成 Fragment VNode
// VNode { type: Fragment, children: [headerVNode, mainVNode, footerVNode] }
```

---

### 【简答题】

**3.4 请简述 Vue 3 Diff 算法的完整流程，包括五个阶段。**

**参考答案**：

Vue 3 的 `patchKeyedChildren` 算法分为五个阶段：

#### 阶段1：从头同步（Sync from start）

```typescript
// 从头部开始，相同类型的节点直接 patch
while (i <= e1 && i <= e2) {
  if (isSameVNodeType(c1[i], c2[i])) {
    patch(c1[i], c2[i], container)
  } else {
    break
  }
  i++
}
```

#### 阶段2：从尾同步（Sync from end）

```typescript
// 从尾部开始，相同类型的节点直接 patch
while (i <= e1 && i <= e2) {
  if (isSameVNodeType(c1[e1], c2[e2])) {
    patch(c1[e1], c2[e2], container)
  } else {
    break
  }
  e1--
  e2--
}
```

#### 阶段3：挂载新节点（Common sequence mount）

```typescript
// 如果旧节点遍历完（i > e1），但新节点还有剩余
if (i > e1) {
  while (i <= e2) {
    patch(null, c2[i], container)  // 挂载新节点
    i++
  }
}
```

#### 阶段4：卸载旧节点（Common sequence unmount）

```typescript
// 如果新节点遍历完（i > e2），但旧节点还有剩余
else if (i > e2) {
  while (i <= e1) {
    unmount(c1[i])  // 卸载多余旧节点
    i++
  }
}
```

#### 阶段5：未知序列处理（Unknown sequence）

这是最复杂的阶段，处理中间部分的节点移动：

1. **构建 key 映射**：新节点的 key → index
2. **遍历旧节点**：通过 key 映射查找新位置，构建 `newIndexToOldIndexMap`
3. **计算 LIS**：找出不需要移动的节点序列
4. **从后向前移动**：不在 LIS 中的节点需要移动，新增节点需要挂载

```typescript
// 5.1 构建 key -> index 映射
const keyToNewIndexMap = new Map()
for (i = s2; i <= e2; i++) {
  keyToNewIndexMap.set(c2[i].key, i)
}

// 5.2 遍历旧节点，填充 newIndexToOldIndexMap
for (i = s1; i <= e1; i++) {
  const newIndex = keyToNewIndexMap.get(c1[i].key)
  if (newIndex === undefined) {
    unmount(c1[i])  // 旧节点不存在于新节点中，卸载
  } else {
    newIndexToOldIndexMap[newIndex - s2] = i + 1  // +1 避免0歧义
    patch(c1[i], c2[newIndex], container)  // 更新
  }
}

// 5.3 计算 LIS
const increasingNewIndexSequence = getSequence(newIndexToOldIndexMap)

// 5.4 从后向前遍历，移动或挂载
let j = increasingNewIndexSequence.length - 1
for (i = toBePatched - 1; i >= 0; i--) {
  const nextIndex = s2 + i
  const nextChild = c2[nextIndex]
  
  if (newIndexToOldIndexMap[i] === 0) {
    // 旧节点中没有，是新增
    patch(null, nextChild, container)
  } else if (j < 0 || i !== increasingNewIndexSequence[j]) {
    // 不在 LIS 中，需要移动
    move(nextChild, container)
  } else {
    // 在 LIS 中，不需要移动
    j--
  }
}
```

---

### 【分析题】

**3.5 请阅读以下 Vue 3 编译器输出（简化版），分析 Patch Flags、静态提升和 Block 收集的工作原理。**

**模板代码**：
```html
<div class="container">
  <h1>Static Title</h1>
  <p :class="dynamicClass">{{ message }}</p>
  <button @click="handleClick">Click</button>
</div>
```

**编译输出**：
```javascript
import { createElementVNode as _createElementVNode, 
         toDisplayString as _toDisplayString, 
         openBlock as _openBlock, 
         createElementBlock as _createElementBlock } from "vue"

const _hoisted_1 = { class: "container" }
const _hoisted_2 = /*#__PURE__*/_createElementVNode("h1", null, "Static Title", -1)
const _hoisted_3 = { class: "dynamicClass" }

export function render(_ctx, _cache) {
  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _hoisted_2,  // 静态提升的 h1
    _createElementVNode("p", { class: _ctx.dynamicClass }, 
      _toDisplayString(_ctx.message), 1 /* TEXT */),
    _createElementVNode("button", { 
      onClick: _cache[0] || (_cache[0] = (...args) => (_ctx.handleClick(...args))) 
    }, "Click")
  ]))
}
```

**参考答案**：

#### 1. 静态提升（Hoist Static）

```javascript
const _hoisted_1 = { class: "container" }
const _hoisted_2 = /*#__PURE__*/_createElementVNode("h1", null, "Static Title", -1)
```

- **原理**：将静态内容提取到 render 函数外部，定义为模块级常量
- **patchFlag = -1**：`HOISTED` 标记，表示该 VNode 是静态提升的，永远不需要 patch
- **优势**：每次渲染都复用同一个 VNode 对象，避免重复创建

#### 2. Patch Flags（补丁标记）

```javascript
_createElementVNode("p", { class: _ctx.dynamicClass }, 
  _toDisplayString(_ctx.message), 1 /* TEXT */)
```

- **patchFlag = 1（TEXT）**：标记该节点只有**文本内容**是动态的
- **运行时优化**：patch 阶段只比较文本内容，跳过 class 的比较（因为 class 是静态的... 等等，这里 class 是动态的）
- **修正**：实际上这里 class 也是动态的，编译器会标记为 `TEXT | CLASS = 1 | 2 = 3`

```javascript
// 更准确的编译输出
_createElementVNode("p", { class: _ctx.dynamicClass }, 
  _toDisplayString(_ctx.message), 3 /* TEXT | CLASS */)
```

- **运行时**：`if (patchFlag & PatchFlags.TEXT)` 更新文本，`if (patchFlag & PatchFlags.CLASS)` 更新 class

#### 3. Block 收集（openBlock + createElementBlock）

```javascript
(_openBlock(), _createElementBlock("div", _hoisted_1, [...]))
```

- **`_openBlock()`**：开始收集动态子节点，创建一个数组 `dynamicChildren`
- **`_createElementBlock()`**：创建 Block VNode，记录所有动态子节点
- **工作原理**：在创建 VNode 的过程中，如果发现子节点有 patchFlag（动态节点），会将其加入 `dynamicChildren` 数组
- **运行时优化**：patch Block 时，**只遍历 `dynamicChildren`**，跳过所有静态节点

```javascript
// 伪代码：Block 的 patch
function patchBlock(n1, n2) {
  // 不遍历所有子节点，只遍历动态子节点
  for (let i = 0; i < n2.dynamicChildren.length; i++) {
    patch(n1.dynamicChildren[i], n2.dynamicChildren[i])
  }
}
```

#### 4. 事件缓存（Cache Event Handlers）

```javascript
onClick: _cache[0] || (_cache[0] = (...args) => (_ctx.handleClick(...args)))
```

- **原理**：将事件处理函数缓存在 `_cache` 数组中
- **优势**：避免每次渲染都创建新的函数，导致子组件不必要更新（props 浅比较）
- **首次渲染**：`_cache[0]` 为空，创建函数并缓存
- **后续渲染**：`_cache[0]` 已存在，直接复用

#### 综合优化效果

| 优化策略 | 作用 | 性能提升 |
|---------|------|---------|
| 静态提升 | 避免重复创建静态 VNode | 减少内存分配 |
| Patch Flags | 按需 patch 动态部分 | 减少 DOM 操作 |
| Block 收集 | 跳过静态子节点遍历 | 减少 VNode 遍历 |
| 事件缓存 | 复用事件处理函数 | 避免不必要更新 |

---

## 四、组件系统与生命周期源码解析

### 【选择题】

**4.1 Vue 3 组件实例（`ComponentInternalInstance`）是在哪个阶段创建的？**

A. `createApp` 时
B. 组件 VNode 被 patch 时
C. 组件挂载到 DOM 时
D. 组件的 setup 函数执行时

**答案：B**

**解析**：在 `patch` → `processComponent` → `mountComponent` 流程中，第一步就是 `createComponentInstance`。随后才执行 `setupComponent`（包含 setup 函数执行）和 `setupRenderEffect`（建立响应式渲染）。

```typescript
// packages/runtime-core/src/renderer.ts
function mountComponent(vnode, container) {
  // 1. 创建组件实例
  const instance = (vnode.component = createComponentInstance(vnode, parentInstance))
  
  // 2. 设置组件（执行 setup、处理 props/slots）
  setupComponent(instance)
  
  // 3. 设置渲染副作用（建立响应式更新）
  setupRenderEffect(instance, container)
}
```

---

**4.2 关于 Vue 3 的 `setup` 函数执行时机，以下说法正确的是？**

A. `setup` 在 `beforeCreate` 之前执行
B. `setup` 在 `beforeCreate` 之后、`created` 之前执行
C. `setup` 和 `created` 同时执行
D. `setup` 在 `mounted` 之后执行

**答案：A**

**解析**：`setup` 函数在组件实例创建后、Options API 初始化之前执行。在 Vue 3 中，`setup` 替代了 `beforeCreate` 和 `created`。此时组件实例已创建，但 data/computed/methods 等尚未初始化，所以 `setup` 中无法通过 `this` 访问这些选项。

```typescript
// packages/runtime-core/src/component.ts
function setupStatefulComponent(instance) {
  // ... 处理 props
  
  // 调用 beforeCreate 钩子
  if (options.beforeCreate) callHook(options.beforeCreate, instance)
  
  // 执行 setup 函数（在 beforeCreate 之后）
  if (setup) {
    const setupResult = setup(instance.props, setupContext)
    handleSetupResult(instance, setupResult)
  }
  
  // 初始化 Options API
  applyOptions(instance, options)  // data/computed/methods/created 等
}
```

---

**4.3 Vue 3 中 `KeepAlive` 组件切换时， deactivated 钩子是在哪个阶段触发的？**

A. 组件 VNode 被 unmount 时
B. 组件 VNode 被移到隐藏容器时
C. 组件 VNode 被创建时
D. 组件 VNode 被 patch 时

**答案：B**

**解析**：`KeepAlive` 缓存的组件在切换时不是被 `unmount`（卸载），而是被**移动到隐藏的 DOM 容器**中。此时触发 `deactivated` 钩子。当切换回来时，组件从隐藏容器移回原位置，触发 `activated` 钩子。这是通过 VNode 的 `shapeFlag` 标记 `COMPONENT_KEPT_ALIVE` 和 `COMPONENT_SHOULD_KEEP_ALIVE` 实现的。

```typescript
// packages/runtime-core/src/components/KeepAlive.ts
function move(container, anchor) {
  // 将组件 DOM 移动到隐藏容器或原位置
  if (shapeFlag & ShapeFlags.COMPONENT_KEPT_ALIVE) {
    // 触发 deactivated
    instance.ctx.deactivate()
    // 移动 DOM 到 storageContainer
    move(vnode, storageContainer, null)
  }
}
```

---

### 【简答题】

**4.4 请阐述 Vue 3 组件的完整挂载流程（从 patch 到 DOM 渲染）。**

**参考答案**：

#### 组件挂载完整流程

```
patch(n1, n2)
  └── processComponent(n1, n2)
        └── mountComponent(n2, container)
              ├── 1. createComponentInstance()    创建组件实例
              ├── 2. setupComponent(instance)      设置组件
              │     ├── initProps()                 初始化 props
              │     ├── initSlots()                 初始化 slots
              │     └── setupStatefulComponent()    执行 setup
              │           ├── callHook(beforeCreate)
              │           ├── 执行 setup(props, ctx)
              │           ├── 处理 setup 返回值
              │           └── applyOptions()        初始化 Options API
              │                 ├── initData()       初始化 data
              │                 ├── initMethods()
              │                 ├── initComputed()
              │                 ├── initWatch()
              │                 └── callHook(created)
              └── 3. setupRenderEffect(instance)   建立渲染副作用
                    ├── callHook(beforeMount)
                    ├── 执行 render 函数生成 subTree
                    ├── patch(null, subTree)         渲染子树
                    ├── callHook(mounted)            挂载完成
                    └── 建立更新机制（响应式触发时重新渲染）
```

#### 关键步骤详解

**1. createComponentInstance**：创建组件实例对象，包含 uid、vnode、props、slots、ctx 等字段

**2. setupComponent**：初始化组件配置，执行 setup 函数

**3. setupRenderEffect**：这是最核心的步骤，用 `effect` 包裹渲染函数，建立响应式更新机制

```typescript
function setupRenderEffect(instance, container) {
  // 用 effect 包裹渲染函数
  const componentUpdateFn = () => {
    if (!instance.isMounted) {
      // 首次挂载
      const subTree = instance.render.call(instance.proxy)
      patch(null, subTree, container)
      instance.isMounted = true
    } else {
      // 更新
      const prevTree = instance.subTree
      const nextTree = instance.render.call(instance.proxy)
      patch(prevTree, nextTree, container)
      instance.subTree = nextTree
    }
  }

  // 创建 effect，调度器使用队列
  const effect = new ReactiveEffect(componentUpdateFn, () => queueJob(update))
  const update = effect.run.bind(effect)
  update()  // 首次执行
}
```

---

### 【分析题】

**4.5 请分析以下 Vue 3 组件更新流程源码，说明为什么组件更新是异步的，以及批量更新的实现机制。**

```typescript
// 调度器实现（简化版）
const queue: SchedulerJob[] = []
let isFlushing = false
let isFlushPending = false
let flushIndex = 0

export function queueJob(job: SchedulerJob) {
  if (!queue.includes(job, flushIndex)) {
    queue.push(job)
  }
  queueFlush()
}

function queueFlush() {
  if (!isFlushing && !isFlushPending) {
    isFlushPending = true
    currentFlushPromise = resolvedPromise.then(flushJobs)
  }
}

function flushJobs() {
  isFlushPending = false
  isFlushing = true

  // 排序：按 id 从小到大（父组件先更新）
  queue.sort(comparator)

  for (flushIndex = 0; flushIndex < queue.length; flushIndex++) {
    const job = queue[flushIndex]
    if (job && job.active) {
      job()
    }
  }

  flushIndex = 0
  queue.length = 0
  isFlushing = false
  currentFlushPromise = null
}
```

**参考答案**：

#### 为什么组件更新是异步的

1. **性能优化**：同步多次修改响应式数据时，只触发一次渲染更新，避免不必要的重复渲染
2. **避免同步无限循环**：如果更新是同步的，render 中再次修改数据会导致无限循环
3. **合并更新**：同一 tick 内的多次数据变更合并为一次更新

```javascript
// 示例：同步修改多次，只渲染一次
state.count = 1
state.count = 2
state.count = 3
// 同步代码执行完后，微任务中只触发一次渲染（count=3）
```

#### 批量更新实现机制

**1. queueJob 入队**
```typescript
export function queueJob(job: SchedulerJob) {
  if (!queue.includes(job, flushIndex)) {
    queue.push(job)  // 去重：同一个 job 不会重复入队
  }
  queueFlush()  // 触发刷新
}
```
- **去重**：用 `includes` 检查是否已存在，避免同一组件多次入队
- **flushIndex 优化**：从当前执行位置开始查找，避免重复检查已执行的任务

**2. queueFlush 触发微任务**
```typescript
function queueFlush() {
  if (!isFlushing && !isFlushPending) {
    isFlushPending = true
    currentFlushPromise = resolvedPromise.then(flushJobs)
  }
}
```
- **微任务**：`resolvedPromise.then` 将 `flushJobs` 放入微任务队列
- **标志位**：`isFlushPending` 防止重复创建 Promise
- **nextTick**：`nextTick` 就是基于 `currentFlushPromise` 实现的

**3. flushJobs 执行**
```typescript
function flushJobs() {
  // 1. 排序
  queue.sort(comparator)
  // 2. 遍历执行
  for (flushIndex = 0; flushIndex < queue.length; flushIndex++) {
    queue[flushIndex]()
  }
  // 3. 重置
  queue.length = 0
  isFlushing = false
}
```

**4. 排序的意义**

```typescript
queue.sort((a, b) => a.id - b.id)
```
- 每个 job 有一个 `id`，按组件创建顺序分配
- **父组件 id < 子组件 id**
- 排序后：父组件先更新，子组件后更新
- 避免子组件先更新后，父组件更新又导致子组件重复更新

#### 完整时序图

```
同步代码执行
  ├── state.count = 1  → trigger → queueJob(componentUpdate) → queueFlush
  ├── state.count = 2  → trigger → queueJob（已存在，跳过）
  ├── state.count = 3  → trigger → queueJob（已存在，跳过）
  └── 同步代码结束
       ↓
微任务队列
  └── flushJobs()
        ├── 排序（父先子后）
        ├── 执行所有 job（componentUpdate）
        │     └── render → patch → DOM 更新（只更新一次）
        └── 重置队列
             ↓
        nextTick 回调执行
```

---

## 五、编译原理与优化源码解析

### 【选择题】

**5.1 Vue 3 编译器的三个核心阶段依次是？**

A. tokenize → parse → generate
B. parse → transform → generate
C. parse → optimize → generate
D. analyze → transform → emit

**答案：B**

**解析**：Vue 3 编译器遵循 `parse → transform → generate` 三阶段架构：

```typescript
// packages/compiler-core/src/compile.ts
export function baseCompile(template, options) {
  const ast = baseParse(template)  // 1. 解析：模板字符串 → AST
  transform(ast, options)          // 2. 转换：AST 转换 + 优化
  return generate(ast, options)    // 3. 生成：AST → 渲染函数代码
}
```

- **parse**：将模板字符串解析为抽象语法树（AST）
- **transform**：遍历 AST，应用转换插件（添加 patchFlag、静态提升、Block 收集等）
- **generate**：将转换后的 AST 生成 JavaScript 代码字符串

---

**5.2 Vue 3 编译器中，`transformElement` 插件的主要作用是？**

A. 将元素节点转换为组件节点
B. 为元素 VNode 生成 patchFlag、props 优化等
C. 删除不必要的元素
D. 改变元素的标签名

**答案：B**

**解析**：`transformElement` 是编译器的核心转换插件，负责：
- 分析元素的动态属性，生成 `patchFlag`
- 将静态属性对象提升（hoist）
- 处理 ref、v-if、v-for 等指令的代码生成
- 生成 `createElementVNode` 调用代码

---

### 【简答题】

**5.3 请阐述 Vue 3 编译器中 AST 的节点类型，以及 `transform` 阶段的遍历策略。**

**参考答案**：

#### AST 节点类型

```typescript
// packages/compiler-core/src/ast.ts
export const enum NodeTypes {
  // 元素/文本
  ELEMENT,          // 元素节点 <div>
  TEXT,             // 文本节点
  COMMENT,          // 注释节点
  SIMPLE_EXPRESSION,// 表达式 {{ msg }}

  // 控制流
  INTERPOLATION,    // 插值 {{ }}
  IF,               // v-if
  FOR,              // v-for

  // 代码生成相关
  COMPOUND_EXPRESSION,  // 复合表达式
  JS_CALL_EXPRESSION,   // 函数调用
  JS_OBJECT_EXPRESSION, // 对象表达式
  JS_ARRAY_EXPRESSION,  // 数组表达式

  // 辅助
  VNODE_CALL,       // createVNode 调用
  JS_FUNCTION_EXPRESSION // 函数表达式
}
```

#### transform 遍历策略

```typescript
// packages/compiler-core/src/transform.ts
export function transform(root, options) {
  const context = createTransformContext(root, options)
  traverseNode(root, context)
}

function traverseNode(node, context) {
  // 1. 进入节点：执行 enter 阶段的转换插件
  context.nodeTransforms.forEach(transform => {
    transform(node, context)  // 可能在 node 上添加 codegenNode
  })

  // 2. 递归遍历子节点
  switch (node.type) {
    case NodeTypes.ELEMENT:
    case NodeTypes.FOR:
    case NodeTypes.IF:
      traverseChildren(node, context)
      break
  }

  // 3. 退出节点：执行 exit 阶段的转换
  // （转换插件可以返回退出函数）
}
```

**关键设计：双阶段转换**
- **进入阶段**：收集信息、处理指令
- **退出阶段**：从子节点开始向上处理，生成 codegenNode
- **原因**：需要先处理子节点，才能确定父节点的 patchFlag 和动态子节点

---

### 【分析题】

**5.4 请分析以下 Vue 3 编译器编译 `v-if` 和 `v-for` 的输出代码，解释实现原理。**

**模板**：
```html
<div v-if="show">
  <span v-for="item in list" :key="item.id">{{ item.name }}</span>
</div>
```

**编译输出**：
```javascript
export function render(_ctx, _cache) {
  return (_ctx.show)
    ? (_openBlock(), _createElementBlock("div", { key: 0 }, 
        _renderList(_ctx.list, (item) => {
          return (_openBlock(true), _createElementBlock("span", { 
            key: item.id 
          }, _toDisplayString(item.name), 1 /* TEXT */))
        }), 128 /* KEYED_FRAGMENT */))
    : _createCommentVNode("v-if", true)
}
```

**参考答案**：

#### v-if 的编译

```javascript
return (_ctx.show)
  ? (_openBlock(), _createElementBlock("div", { key: 0 }, ...))
  : _createCommentVNode("v-if", true)
```

1. **三元表达式**：`v-if` 编译为条件表达式，条件为真时创建节点，否则创建注释节点
2. **key: 0**：`v-if` 节点自动添加 key，用于 diff 时区分不同分支
3. **注释占位**：条件为假时创建注释节点 `<!--v-if-->`，保持 DOM 结构稳定

#### v-for 的编译

```javascript
_renderList(_ctx.list, (item) => {
  return (_openBlock(true), _createElementBlock("span", { key: item.id }, ...))
})
```

1. **`_renderList`**：Vue 内部辅助函数，将列表数据转换为 VNode 数组
2. **`_openBlock(true)`**：参数 `true` 表示这是一个 Fragment Block（v-for 产生的 Fragment）
3. **`128 = KEYED_FRAGMENT`**：patchFlag 标记为带 key 的 Fragment
4. **key: item.id**：v-for 的 key 直接编译到 VNode 的 key 属性

#### `_renderList` 实现

```typescript
// packages/runtime-core/src/helpers/renderList.ts
export function renderList(source, renderItem) {
  let ret
  if (isArray(source) || isString(source)) {
    ret = new Array(source.length)
    for (let i = 0; i < source.length; i++) {
      ret[i] = renderItem(source[i], i)
    }
  } else if (typeof source === 'number') {
    ret = new Array(source)
    for (let i = 0; i < source; i++) {
      ret[i] = renderItem(i + 1, i)
    }
  } else if (isObject(source)) {
    // 对象遍历
    ret = []
    for (const key in source) {
      ret.push(renderItem(source[key], key))
    }
  }
  return ret
}
```

#### 综合分析

- `v-if` 和 `v-for` 在 Vue 3 中通过编译器转换为 JavaScript 原生语法
- 不需要运行时指令解析，性能更高
- `v-if` → 三元表达式，`v-for` → `_renderList` + map
- Fragment 类型标记让 diff 算法选择正确的处理策略

---

## 六、调度机制与性能优化源码解析

### 【选择题】

**6.1 Vue 3 中 `nextTick` 的实现是基于？**

A. `setTimeout`
B. `MutationObserver`
C. `Promise.resolve().then()`
D. `requestAnimationFrame`

**答案：C**

**解析**：Vue 3 的 `nextTick` 基于 `Promise.resolve().then()`（微任务），因为组件更新队列 `flushJobs` 也通过微任务触发。`nextTick` 会等待 `currentFlushPromise`（更新队列的 Promise）完成后执行。

```typescript
// packages/runtime-core/src/scheduler.ts
const resolvedPromise = Promise.resolve() as Promise<any>
let currentFlushPromise: Promise<void> | null = null

export function nextTick(fn?: () => void): Promise<void> {
  const p = currentFlushPromise || resolvedPromise
  return fn ? p.then(this ? fn.bind(this) : fn) : p
}
```

---

**6.2 Vue 3 中 `markRaw` 的作用是？**

A. 标记对象为只读
B. 标记对象不可被转为响应式
C. 标记对象为浅响应式
D. 标记对象为静态常量

**答案：B**

**解析**：`markRaw` 给对象添加 `__v_skip` 属性，`reactive` 函数检查到该属性会直接返回原始对象，不做代理。适用于第三方类实例（如 Map/GLSL 对象）等不应被响应式化的对象。

```typescript
export function markRaw(value) {
  if (Object.isExtensible(value)) {
    def(value, ReactiveFlags.SKIP, true)  // 添加 __v_skip = true
  }
  return value
}

// reactive 中检查
function createReactiveObject(target, ...) {
  if (target[ReactiveFlags.SKIP]) {
    return target  // 跳过，不代理
  }
  // ...
}
```

---

### 【简答题】

**6.3 请列举 Vue 3 相比 Vue 2 在运行时性能方面的主要优化，并简述实现原理。**

**参考答案**：

| 优化策略 | Vue 2 | Vue 3 | 原理 |
|---------|-------|-------|------|
| 响应式 | `Object.defineProperty` 全递归 | `Proxy` 懒代理 | 访问时才代理子属性，减少初始化开销 |
| 编译优化 | 全量 diff | Patch Flags + Block | 只 patch 动态部分，跳过静态内容 |
| 静态提升 | 无 | hoist static | 静态 VNode 提取为常量，避免重复创建 |
| 事件缓存 | 无 | cache handlers | 复用事件函数，避免不必要更新 |
| Diff 算法 | 双端比较 | 双端 + LIS | 最长递增子序列最小化 DOM 移动 |
| 包体积 | 整体打包 | Tree-shaking | 按需引入，未使用 API 不打包 |
| 内存 | 每个属性 getter/setter | Proxy 代理整个对象 | 减少内存占用 |

---

### 【编程题】

**6.4 请实现一个简化版的 Vue 3 调度器（Scheduler），支持：任务去重、微任务批量执行、任务排序、nextTick。**

**参考答案**：

```typescript
// ===== 调度器实现 =====

interface SchedulerJob {
  (): void
  id: number
  active: boolean
}

const queue: SchedulerJob[] = []
let flushIndex = 0
let isFlushing = false
let isFlushPending = false

const resolvedPromise = Promise.resolve() as Promise<void>
let currentFlushPromise: Promise<void> | null = null

// 入队
export function queueJob(job: SchedulerJob) {
  // 去重：从 flushIndex 位置开始查找（已执行的不用查）
  if (queue.indexOf(job, flushIndex) === -1) {
    queue.push(job)
  }
  queueFlush()
}

// 触发刷新
function queueFlush() {
  if (!isFlushing && !isFlushPending) {
    isFlushPending = true
    // 用微任务执行
    currentFlushPromise = resolvedPromise.then(flushJobs)
  }
}

// 刷新队列
function flushJobs() {
  isFlushPending = false
  isFlushing = true

  // 排序：父组件 id 小，先执行
  queue.sort((a, b) => a.id - b.id)

  // 执行前清空 flushIndex
  flushIndex = 0
  for (; flushIndex < queue.length; flushIndex++) {
    const job = queue[flushIndex]
    if (job && job.active) {
      job()
    }
  }

  // 清空队列
  flushIndex = 0
  queue.length = 0

  // 执行后置回调（如 updated 钩子）
  flushPostFlushCbs()

  isFlushing = false
  currentFlushPromise = null

  // 如果在刷新过程中又入队了新任务，继续刷新
  if (queue.length > 0) {
    flushJobs()
  }
}

// 后置回调队列
const pendingPostFlushCbs: SchedulerJob[] = []
let postFlushIndex = 0

export function queuePostFlushCb(cb: SchedulerJob) {
  if (pendingPostFlushCbs.indexOf(cb, postFlushIndex) === -1) {
    pendingPostFlushCbs.push(cb)
  }
}

function flushPostFlushCbs() {
  if (pendingPostFlushCbs.length > 0) {
    pendingPostFlushCbs.sort((a, b) => a.id - b.id)
    for (; postFlushIndex < pendingPostFlushCbs.length; postFlushIndex++) {
      const cb = pendingPostFlushCbs[postFlushIndex]
      if (cb.active) cb()
    }
    pendingPostFlushCbs.length = 0
    postFlushIndex = 0
  }
}

// nextTick
export function nextTick(fn?: () => void): Promise<void> {
  const p = currentFlushPromise || resolvedPromise
  return fn ? p.then(fn) : p
}

// ===== 测试用例 =====

let uid = 0

function createJob(name: string, id: number): SchedulerJob {
  const fn = (() => {
    console.log(`[${name}] executing, id=${id}`)
  }) as any
  fn.id = id
  fn.active = true
  return fn
}

// 模拟组件更新
const parentUpdate = createJob('Parent', 1)
const childUpdate = createJob('Child', 2)
const grandChildUpdate = createJob('GrandChild', 3)

// 同一 tick 内多次入队（去重）
queueJob(parentUpdate)
queueJob(parentUpdate)  // 重复，不会入队
queueJob(childUpdate)
queueJob(grandChildUpdate)

// nextTick 在所有更新后执行
nextTick(() => {
  console.log('All updates done!')
})

// 输出：
// [Parent] executing, id=1
// [Child] executing, id=2
// [GrandChild] executing, id=3
// All updates done!
// （按 id 排序：父→子→孙）
```

**评分标准**：
- 实现基本队列和微任务触发：60分
- 支持去重和排序：80分
- 完整实现后置回调和 nextTick：100分

---

## 总结

### 题型分布

| 题型 | 数量 | 考察重点 |
|------|------|---------|
| 选择题 | 12 | 基础概念、源码细节 |
| 简答题 | 6 | 原理阐述、流程描述 |
| 分析题 | 4 | 源码分析、优化策略 |
| 编程题 | 2 | 核心代码手写 |

### 知识点覆盖

| 模块 | 考察内容 |
|------|---------|
| 架构设计 | monorepo、包依赖、createApp、ShapeFlags |
| 响应式系统 | reactive、ref、effect、track/trigger、cleanup、shallowReactive |
| 虚拟DOM | VNode、PatchFlags、Block、Diff算法（LIS）、Fragment |
| 组件系统 | 组件实例、setup执行、KeepAlive、挂载流程 |
| 编译原理 | parse/transform/generate、AST、v-if/v-for编译 |
| 调度机制 | 异步更新、批量更新、nextTick、markRaw |

### 评分建议

- **基础题（选择题）**：快速筛选，评估知识面
- **进阶题（简答题）**：评估理解和表达能力
- **高级题（分析题）**：评估源码深度和架构理解
- **实战题（编程题）**：评估编码能力和实现能力
