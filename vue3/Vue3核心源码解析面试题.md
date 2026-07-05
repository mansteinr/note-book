# Vue.js 3.0 核心源码解析面试题

## 目录

- [整体架构设计](#整体架构设计)
- [响应式系统源码](#响应式系统源码)
- [虚拟DOM与Diff算法源码](#虚拟dom与diff算法源码)
- [组件系统源码](#组件系统源码)
- [编译原理源码](#编译原理源码)
- [生命周期与渲染机制](#生命周期与渲染机制)
- [架构优化与性能](#架构优化与性能)
- [实战源码分析](#实战源码分析)

---

## 整体架构设计

### 题目1

**题目描述**：请介绍 Vue 3 核心仓库的整体架构和模块划分。

**考察重点**：monorepo 架构、各模块职责、模块依赖关系

**参考答案**：

#### Vue3 核心仓库架构（Monorepo）

Vue3 采用 monorepo 架构，主要包含以下模块：

```
vue-next/
├── packages/
│   ├── vue/              # 入口包，整合 runtime-dom + runtime-core + reactivity
│   ├── reactivity/       # 响应式系统（独立可运行）
│   ├── runtime-core/     # 运行时核心，虚拟DOM、组件系统
│   ├── runtime-dom/      # DOM 操作相关
│   ├── compiler-core/    # 编译器核心
│   ├── compiler-dom/     # DOM 编译器
│   ├── compiler-sfc/     # SFC（单文件组件）编译器
│   ├── shared/           # 共享工具函数
│   ├── server-renderer/  # 服务端渲染
│   └── vuex/             # 状态管理（独立仓库）
```

#### 模块依赖关系

```
compiler-dom    compiler-sfc
     |              |
     └──────┬───────┘
            |
    compiler-core    runtime-dom
            |             |
            └──────┬──────┘
                   |
            runtime-core   server-renderer
                   |
            reactivity
                   |
                shared
```

#### 各模块职责

| 模块 | 职责 | 关键文件 |
|------|------|---------|
| `reactivity` | 响应式系统（reactive/ref/effect等） | `ref.ts`, `reactive.ts`, `effect.ts`, `computed.ts` |
| `runtime-core` | 虚拟DOM、组件系统、渲染器 | `renderer.ts`, `component.ts`, `apiCreateApp.ts` |
| `runtime-dom` | DOM 操作、属性处理 | `patchProp.ts`, `nodeOps.ts` |
| `compiler-core` | AST 解析、转换、代码生成 | `transform.ts`, `codegen.ts`, `ast.ts` |
| `compiler-dom` | DOM 特有的编译 | `transformElement.ts` |

#### 评分标准

- 知道是 monorepo 架构：60分
- 能说明主要模块职责：80分
- 能说明模块依赖关系：100分

---

### 题目2

**题目描述**：请说明 Vue 3 的入口源码 `createApp` 的实现流程。

**考察重点**：应用实例创建、插件系统、挂载流程

**参考答案**：

#### `createApp` 核心实现

```typescript
// packages/runtime-core/src/apiCreateApp.ts
export function createAppAPI<HostElement>(
  render: RootRenderFunction,
  hydrate?: RootHydrateFunction
): CreateAppFunction<HostElement> {
  return function createApp(rootComponent, rootProps = null) {
    if (!isFunction(rootComponent)) {
      rootComponent = { ...rootComponent }
    }

    const context = createAppContext()
    let isMounted = false

    const app: App = {
      _uid: uid++,
      _component: rootComponent,
      _props: rootProps,
      _container: null,
      _context: context,
      _instance: null,

      use(plugin, ...options) {
        if (plugin.install) {
          plugin.install(app, ...options)
        } else if (isFunction(plugin)) {
          plugin(app, ...options)
        }
        return app
      },

      mount(rootContainer: HostElement, isHydrate = false): any {
        if (!isMounted) {
          const vnode = createVNode(rootComponent, rootProps)
          vnode.appContext = context
          
          if (isHydrate && hydrate) {
            hydrate(vnode, rootContainer as any)
          } else {
            render(vnode, rootContainer)
          }
          
          isMounted = true
          app._container = rootContainer
          
          return vnode.component?.proxy
        }
      },

      unmount() {
        if (isMounted) {
          render(null, app._container)
          app._instance = null
          isMounted = false
        }
      }
    }
    
    return app
  }
}
```

#### 完整流程

1. 创建应用上下文
2. 创建虚拟根节点
3. 执行挂载（调用 render）
4. 渲染器执行挂载和更新

#### 评分标准

- 理解 createApp 返回 App 实例：60分
- 能说明 mount 的主要流程：80分
- 完整分析源码细节：100分

---

## 响应式系统源码

### 题目3

**题目描述**：请从源码层面分析 `reactive` 的实现细节，包括 Proxy 代理、WeakMap 的作用、懒代理机制。

**考察重点**：源码深度、数据结构、性能考量

**参考答案**：

#### `reactive` 源码实现

```typescript
// packages/reactivity/src/reactive.ts
export function reactive<T extends object>(target: T): UnwrapNestedRefs<T>
export function reactive(target: object) {
  if (target && (target as Target)[ReactiveFlags.RAW]) {
    return target
  }
  
  return createReactiveObject(
    target,
    false,
    mutableHandlers,
    mutableCollectionHandlers,
    reactiveMap
  )
}

function createReactiveObject(
  target: Target,
  isReadonly: boolean,
  baseHandlers: ProxyHandler<any>,
  collectionHandlers: ProxyHandler<any>,
  proxyMap: WeakMap<Target, any>
) {
  if (!isObject(target)) {
    return target
  }
  
  if (target[ReactiveFlags.SKIP] || !Object.isExtensible(target)) {
    return target
  }
  
  const existingProxy = proxyMap.get(target)
  if (existingProxy) {
    return existingProxy
  }
  
  const proxy = new Proxy(target, collectionTypes.has(target.constructor)
    ? collectionHandlers
    : baseHandlers
  )
  
  proxyMap.set(target, proxy)
  return proxy
}
```

#### 关键要点

1. **WeakMap 的作用**：`proxyMap` 存储原始对象到代理对象的映射，避免重复代理，同时配合 GC。
2. **标记位**：`ReactiveFlags` 用于判断对象状态（RAW/SKIP/IS_REACTIVE 等）。
3. **懒代理**：get 拦截器中才递归代理子对象。
4. **集合类型特殊处理**：Map/Set/WeakMap/WeakSet 使用不同的 handlers。

#### 评分标准

- 知道是 Proxy 实现：60分
- 理解 WeakMap 作用和标记位：80分
- 能完整分析源码实现：100分

---

### 题目4

**题目描述**：请分析 `effect` 源码实现，解释 `activeEffect` 和 `effectStack` 的作用机制。

**考察重点**：副作用函数、依赖收集栈、嵌套 effect 处理

**参考答案**：

#### `effect` 源码实现

```typescript
// packages/reactivity/src/effect.ts
let activeEffect: ReactiveEffect | undefined
const effectStack: ReactiveEffect[] = []

export class ReactiveEffect<T = any> {
  active = true
  deps: Dep[] = []
  parent: ReactiveEffect | undefined
  
  constructor(
    public fn: () => T,
    public scheduler: EffectScheduler | null = null,
    scope?: EffectScope
  ) {
    recordEffectScope(this, scope)
  }

  run() {
    if (!this.active) {
      return this.fn()
    }

    let parent: ReactiveEffect | undefined = activeEffect
    let lastShouldTrack = shouldTrack
    
    while (parent) {
      if (parent === this) return
      parent = parent.parent
    }
    
    try {
      this.parent = activeEffect
      activeEffect = this
      shouldTrack = true
      
      trackEffect(this)
      
      return this.fn()
    } finally {
      cleanupEffect(this)
      activeEffect = this.parent
      shouldTrack = lastShouldTrack
      this.parent = undefined
    }
  }
}

export function effect<T = any>(
  fn: () => T,
  options?: ReactiveEffectOptions
): ReactiveEffectRunner<T> {
  const _effect = new ReactiveEffect(fn)
  
  if (options) {
    extend(_effect, options)
  }
  
  if (!options || !options.lazy) {
    _effect.run()
  }
  
  const runner = _effect.run.bind(_effect) as ReactiveEffectRunner<T>
  runner.effect = _effect
  return runner
}
```

#### `track` 源码

```typescript
let targetMap: TargetMap = new WeakMap()

export function track(target: object, type: TrackOpTypes, key: unknown) {
  if (!shouldTrack || activeEffect === undefined) return
  
  let depsMap = targetMap.get(target)
  if (!depsMap) {
    targetMap.set(target, (depsMap = new Map()))
  }
  
  let dep = depsMap.get(key)
  if (!dep) {
    depsMap.set(key, (dep = createDep()))
  }
  
  trackEffects(dep)
}

export function trackEffects(dep: Dep) {
  if (activeEffect) {
    dep.add(activeEffect)
    activeEffect.deps.push(dep)
  }
}
```

#### `effectStack` 的作用

```typescript
// effect 嵌套场景
effect(() => {
  console.log('outer')
  effect(() => {
    console.log('inner')
  })
})

// 栈的作用：恢复外部 effect
// 执行 inner 时 activeEffect 是 inner effect
// inner 执行完后，栈顶弹出，恢复为 outer effect
```

#### 评分标准

- 知道 effectStack 存储副作用：60分
- 理解嵌套 effect 的处理：80分
- 完整分析源码和数据结构：100分

---

### 题目5

**题目描述**：请对比分析 Vue 2 和 Vue 3 响应式系统的架构区别，特别是 Vue 3 的优势。

**考察重点**：设计差异、性能优化、功能增强

**参考答案**：

| 特性 | Vue 2 | Vue 3 |
|------|-------|-------|
| 核心API | Object.defineProperty | Proxy + Reflect |
| 数组支持 | 重写 7 种数组方法，索引不响应 | 原生 Proxy 支持，索引和 length 全响应 |
| 对象支持 | 初始化时递归响应式，新增属性需 $set | 懒代理，新增/删除属性自动响应 |
| 深层监听 | 初始化时一次性递归 | 访问时才代理（Lazy Proxy） |
| 数据结构 | 不支持 Map/Set/WeakMap/WeakSet | 原生支持 |
| 性能开销 | 初始化全递归，大数据慢 | 懒代理，按需递归，更快 |

#### Vue3 的关键优化

1. **懒代理（Lazy Proxy）**
```typescript
// get 中才递归代理
const result = Reflect.get(target, key, receiver)
if (isObject(result)) {
  return reactive(result)  // 访问时才代理
}
```

2. **收集优化**
```typescript
// 只有 activeEffect 才进行依赖收集
if (activeEffect) {
  track(target, key)
}
```

3. **Proxy 的优势**
- 支持完整的对象操作拦截
- 更好的性能（不需要 defineProperty 循环）
- 不污染原对象

#### 评分标准

- 能说明 Proxy vs defineProperty：60分
- 能说明懒代理等优化：80分
- 完整对比设计差异：100分

---

## 虚拟DOM与Diff算法源码

### 题目6

**题目描述**：请分析 Vue 3 的 Patch 函数核心实现，包括 VNode 类型处理、属性更新、子节点更新。

**考察重点**：renderer.ts 源码、VNode 结构

**参考答案**：

#### Patch 核心实现

```typescript
// packages/runtime-core/src/renderer.ts
function patch(
  n1: VNode | null,
  n2: VNode,
  container: RendererNode,
  ...
) {
  if (n1 === n2) return
  
  if (n1 && !isSameVNodeType(n1, n2)) {
    // 类型不同，直接替换
    unmount(n1, null, null, true)
    n1 = null
  }
  
  const { type, shapeFlag } = n2
  
  switch (type) {
    case Text:
      processText(n1, n2, container, anchor)
      break
    case Comment:
      processCommentNode(n1, n2, container, anchor)
      break
    case Static:
      if (n1 == null) {
        mountStaticNode(...)
      }
      break
    case Fragment:
      processFragment(n1, n2, container, ...)
      break
    default:
      if (shapeFlag & ShapeFlags.ELEMENT) {
        processElement(n1, n2, container, ...)
      } else if (shapeFlag & ShapeFlags.COMPONENT) {
        processComponent(n1, n2, container, ...)
      }
  }
}
```

#### processElement 源码

```typescript
function processElement(
  n1: VNode | null,
  n2: VNode,
  container: RendererNode,
  ...
) {
  if (n1 == null) {
    mountElement(n2, container, ...)
  } else {
    patchElement(n1, n2, ...)
  }
}
```

#### 评分标准

- 理解 VNode 类型处理：60分
- 能说明 mount/patch 流程：80分
- 完整分析源码：100分

---

### 题目7

**题目描述**：请从源码层面分析 Vue 3 的 Diff 算法，特别是最长递增子序列（LIS）优化。

**考察重点**：diff 算法原理、LIS 优化、双端比较

**参考答案**：

#### 核心源码 - patchChildren

```typescript
// packages/runtime-core/src/renderer.ts
function patchChildren(
  n1: VNode | null,
  n2: VNode,
  container: RendererNode,
  ...
) {
  const c1 = n1 && n1.children
  const c2 = n2.children
  
  if (patchFlag > 0) {
    if (patchFlag & PatchFlags.KEYED_FRAGMENT) {
      // 带 key 的子节点，做完整 diff
      patchKeyedChildren(...)
      return
    } else if (patchFlag & PatchFlags.UNKEYED_FRAGMENT) {
      // 无 key 的子节点
      patchUnkeyedChildren(...)
      return
    }
  }
  
  // 如果没有 patchFlag，fallback 到完整检查
  if (c1 !== c2) {
    patchUnkeyedChildren(...)
  }
}
```

#### 核心源码 - patchKeyedChildren

```typescript
function patchKeyedChildren(
  c1: VNode[],
  c2: VNode[],
  container: RendererNode,
  ...
) {
  // 1. 双端比较 - 同步前缀
  let i = 0
  const l2 = c2.length
  let e1 = c1.length - 1
  let e2 = l2 - 1

  while (i <= e1 && i <= e2) {
    const n1 = c1[i]
    const n2 = c2[i]
    if (isSameVNodeType(n1, n2)) {
      patch(n1, n2, container)
    } else {
      break
    }
    i++
  }

  while (i <= e1 && i <= e2) {
    const n1 = c1[e1]
    const n2 = c2[e2]
    if (isSameVNodeType(n1, n2)) {
      patch(n1, n2, container)
    } else {
      break
    }
    e1--
    e2--
  }

  // 2. 处理新增
  if (i > e1) {
    if (i <= e2) {
      const nextPos = e2 + 1
      const anchor = nextPos < l2 ? c2[nextPos].el : null
      while (i <= e2) {
        patch(null, c2[i], container, anchor)
        i++
      }
    }
  } 
  // 3. 处理删除
  else if (i > e2) {
    while (i <= e1) {
      unmount(c1[i])
      i++
    }
  } 
  // 4. 处理移动和新增删除
  else {
    const s1 = i
    const s2 = i
    
    // 构建 key -> index 映射
    const keyToNewIndexMap: Map<any, number> = new Map()
    for (i = s2; i <= e2; i++) {
      const nextChild = c2[i]
      keyToNewIndexMap.set(nextChild.key, i)
    }
    
    const toBePatched = e2 - s2 + 1
    let patched = 0
    let maxNewIndexSoFar = 0
    
    const newIndexToOldIndexMap: number[] = new Array(toBePatched).fill(0)
    
    // 遍历旧节点，找出需要 patch 的
    for (i = s1; i <= e1; i++) {
      const prevChild = c1[i]
      const newIndex = keyToNewIndexMap.get(prevChild.key)
      if (newIndex !== undefined) {
        newIndexToOldIndexMap[newIndex - s2] = i + 1
        maxNewIndexSoFar = Math.max(maxNewIndexSoFar, newIndex)
        patch(prevChild, c2[newIndex], container)
        patched++
      } else {
        unmount(prevChild)
      }
    }
    
    // LIS 计算，找出最长递增子序列
    const increasingNewIndexSequence = getSequence(newIndexToOldIndexMap)
    let j = increasingNewIndexSequence.length - 1
    
    // 移动节点，从后往前
    for (i = toBePatched - 1; i >= 0; i--) {
      const nextIndex = s2 + i
      const nextChild = c2[nextIndex]
      const anchor = nextIndex + 1 < l2 ? c2[nextIndex + 1].el : null
      
      if (newIndexToOldIndexMap[i] === 0) {
        patch(null, nextChild, container, anchor)
      } else {
        if (j < 0 || i !== increasingNewIndexSequence[j]) {
          move(nextChild, container, anchor)
        } else {
          j--
        }
      }
    }
  }
}
```

#### LIS 算法源码

```typescript
function getSequence(arr: number[]): number[] {
  const p = arr.slice()
  const result = [0]
  let i, j, u, v, c
  const len = arr.length
  
  for (i = 0; i < len; i++) {
    const arrI = arr[i]
    if (arrI !== 0) {
      j = result[result.length - 1]
      if (arr[j] < arrI) {
        p[i] = j
        result.push(i)
        continue
      }
      u = 0
      v = result.length - 1
      while (u < v) {
        c = ((u + v) / 2) | 0
        if (arr[result[c]] < arrI) {
          u = c + 1
        } else {
          v = c
        }
      }
      if (arrI < arr[result[u]]) {
        if (u > 0) {
          p[i] = result[u - 1]
        }
        result[u] = i
      }
    }
  }
  
  u = result.length
  v = result[u - 1]
  while (u-- > 0) {
    result[u] = v
    v = p[v]
  }
  
  return result
}
```

#### 核心优化点

1. **双端比较**：快速找到相同前后缀
2. **key 映射**：用 Map 快速查找对应关系
3. **最长递增子序列**：最小化 DOM 移动操作
4. **从后往前移动**：避免覆盖问题

#### 评分标准

- 理解双端比较：60分
- 理解 key 映射和 LIS：80分
- 完整分析 diff 算法源码：100分

---

## 组件系统源码

### 题目8

**题目描述**：请从源码层面分析 Vue 3 组件实例的创建和初始化流程。

**考察重点**：createComponentInstance、setupStatefulComponent、生命周期

**参考答案**：

#### 组件实例结构

```typescript
// packages/runtime-core/src/component.ts
export interface ComponentInternalInstance {
  uid: number
  type: ConcreteComponent
  parent: ComponentInternalInstance | null
  appContext: AppContext
  
  vnode: VNode
  next: VNode | null
  
  proxy: ComponentPublicInstance | null
  
  props: Data
  attrs: Data
  slots: InternalSlots
  
  ctx: Data
  setupState: Data
  
  provides: Data
  
  isMounted: boolean
  isUnmounted: boolean
  
  render: InternalRenderFunction | null
}
```

#### 实例创建流程

```typescript
function createComponentInstance(
  vnode: VNode,
  parent: ComponentInternalInstance | null
): ComponentInternalInstance {
  const type = vnode.type as ConcreteComponent
  
  const instance: ComponentInternalInstance = {
    uid: uid++,
    vnode,
    type,
    parent,
    appContext: parent ? parent.appContext : vnode.appContext,
    
    proxy: null,
    proxyCache: null,
    
    ctx: {},
    setupState: {},
    data: {},
    props: {},
    attrs: {},
    slots: {},
    
    provides: parent ? parent.provides : Object.create(null),
    
    isMounted: false,
    isUnmounted: false,
    
    render: null
  }
  
  return instance
}
```

#### setup 执行流程

```typescript
function setupStatefulComponent(
  instance: ComponentInternalInstance,
  isSSR: boolean
) {
  const Component = instance.type as ComponentOptions
  
  const setup = Component.setup
  
  if (setup) {
    const setupContext = createSetupContext(instance)
    
    setCurrentInstance(instance)
    const setupResult = callWithErrorHandling(
      setup,
      instance,
      [instance.props, setupContext]
    )
    unsetCurrentInstance()
    
    if (isFunction(setupResult)) {
      instance.render = setupResult as InternalRenderFunction
    } else if (isObject(setupResult)) {
      instance.setupState = proxyRefs(setupResult)
    }
  }
  
  finishComponentSetup(instance)
}
```

#### 评分标准

- 理解组件实例结构：60分
- 理解 setup 执行流程：80分
- 完整分析源码：100分

---

### 题目9

**题目描述**：请从源码分析 Vue 3 的 Teleport 组件原理。

**考察重点**：虚拟 DOM 移动、目标挂载点、渲染过程

**参考答案**：

#### Teleport 源码

```typescript
// packages/runtime-core/src/components/Teleport.ts
const TeleportImpl = {
  __isTeleport: true,
  process(
    n1: VNode | null,
    n2: VNode,
    container: RendererNode,
    ...
  ) {
    const target = n2.props.to
    const disabled = n2.props.disabled
    
    // 挂载
    if (n1 == null) {
      const mountPoint = findTarget(target)
      mount(n2.children, mountPoint)
      
      // 锚点
      if (!disabled) {
        moveTeleportTarget(n2, container, anchor)
      }
    } else {
      if (disabled !== n1.props.disabled) {
        if (disabled) {
          moveTeleportTarget(n2, container, anchor)
        } else {
          const mountPoint = findTarget(target)
          moveTeleportTarget(n2, mountPoint)
        }
      }
    }
  }
}
```

#### 关键原理

1. **target 查找**：通过 selector 找到目标挂载点
2. **移动逻辑**：disabled 时移回原处，正常时移到目标
3. **锚点处理**：在原位置保留注释节点作为占位

#### 评分标准

- 理解 Teleport 的基本原理：60分
- 理解移动和锚点逻辑：80分
- 完整分析源码：100分

---

## 编译原理源码

### 题目10

**题目描述**：请分析 Vue 3 编译器的主要流程，从 template 到 render 函数。

**考察重点**：parse -> transform -> codegen 三阶段

**参考答案**：

#### 编译流程

```typescript
// packages/compiler-core/src/compile.ts
export function baseCompile(
  template: string | RootNode,
  options: CompilerOptions = {}
): CodegenResult {
  const { ast } = baseParse(template)
  transform(ast)
  return generate(ast)
}
```

#### Parse 阶段 - 生成 AST

```typescript
// packages/compiler-core/src/parse.ts
export function baseParse(content: string) {
  const context = createParserContext(content)
  const ast = parseChildren(context, [])
  return ast
}
```

#### Transform 阶段 - AST 转换和优化

```typescript
// packages/compiler-core/src/transform.ts
export function transform(root: RootNode, options: TransformOptions) {
  const context = createTransformContext(root)
  
  traverseNode(root, context)
  
  return root
}
```

#### Codegen 阶段 - 代码生成

```typescript
// packages/compiler-core/src/codegen.ts
export function generate(ast: RootNode): CodegenResult {
  const context = createCodegenContext()
  
  genFunctionPreamble(ast, context)
  
  genFunctionPreamble(ast, context)
  
  genNode(ast.codegenNode!, context)
  
  return {
    ast,
    code: context.code
  }
}
```

#### 编译优化

1. **Patch Flags**：标记动态内容
2. **静态提升**：hoist 静态内容
3. **Block tree**：构建优化的块树
4. **缓存事件处理**

#### 评分标准

- 理解三阶段流程：60分
- 理解编译优化：80分
- 完整分析源码：100分

---

## 生命周期与渲染机制

### 题目11

**题目描述**：请从源码层面分析 Vue 3 的 nextTick 实现机制。

**考察重点**：微任务队列、Promise 降级、批量更新

**参考答案**：

#### nextTick 源码实现

```typescript
// packages/runtime-core/src/scheduler.ts
export function nextTick<T = void>(this: T, fn?: (this: T) => void): Promise<void> {
  const p = currentFlushPromise || resolvedPromise
  return fn ? p.then(this ? fn.bind(this) : fn) : p
}
```

#### 调度器源码

```typescript
let isFlushing = false
let isFlushPending = false

const queue: SchedulerJob[] = []
let flushIndex = 0

let pendingPostFlushCbs: SchedulerJob[] = []
let postFlushIndex = 0

let currentFlushPromise: Promise<void> | null = null

export function queueJob(job: SchedulerJob) {
  if (!queue.includes(job)) {
    queue.push(job)
    queueFlush()
  }
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
  
  for (flushIndex = 0; flushIndex < queue.length; flushIndex++) {
    queue[flushIndex]()
  }
  
  flushPostFlushCbs()
  
  isFlushing = false
}
```

#### 微任务选择

```typescript
// packages/runtime-dom/src/nodeOps.ts
let resolvePromise: (p: Promise<any>) => void
let rejectPromise: (reason?: any) => void

if (typeof Promise !== 'undefined' && isNative(Promise)) {
  const p = Promise.resolve()
  resolvePromise = (fn) => p.then(fn)
} else if (typeof MutationObserver !== 'undefined') {
  // ... 降级处理
} else {
  // setTimeout 最后降级
}
```

#### 评分标准

- 理解 nextTick 使用微任务：60分
- 理解队列机制和批量更新：80分
- 完整分析调度器源码：100分

---

## 架构优化与性能

### 题目12

**题目描述**：请分析 Vue 3 的渲染器设计，特别是 `createRenderer` 机制和自定义渲染器的实现。

**考察重点**：平台无关性、host config 抽象、渲染器接口

**参考答案**：

#### createRenderer 源码

```typescript
// packages/runtime-core/src/renderer.ts
export function createRenderer<
  HostNode = RendererNode,
  HostElement = RendererElement,
  HostText = RendererText
>(options: RendererOptions<HostNode, HostElement, HostText>) {
  const {
    patchProp,
    insert,
    remove,
    createElement,
    createText,
    createComment,
    setText,
    setElementText,
    nextSibling,
    parentNode
  } = options

  function patch(...) { ... }
  function render(...) { ... }

  return {
    render,
    hydrate,
    createApp: createAppAPI(render, hydrate)
  }
}
```

#### DOM 渲染器实现

```typescript
// packages/runtime-dom/src/index.ts
const { render, createApp } = createRenderer({
  patchProp,
  ...nodeOps
})

export { render, createApp }
```

#### 自定义渲染器示例

```typescript
const { createApp } = createRenderer({
  createElement: (tag) => ({ tag }),
  setText: (el, text) => el.text = text,
  insert: (el, parent) => parent.children.push(el)
})
```

#### 平台无关性设计

1. **Host Config 抽象**：所有平台特定操作都通过配置传入
2. **通用核心逻辑**：patch、diff 等核心逻辑与平台无关
3. **多个平台支持**：DOM、Canvas、Native、自定义渲染

#### 评分标准

- 理解 createRenderer 工厂模式：60分
- 理解 host config 抽象：80分
- 完整分析渲染器架构：100分

---

## 实战源码分析

### 题目13

**题目描述**：请手写一个简化版的 Vue 3 响应式系统，要求包含：reactive、ref、effect、track、trigger。

**考察重点**：对源码的完整理解、核心机制实现

**参考答案**：

```typescript
let activeEffect = null
let effectStack = []
const targetMap = new WeakMap()

class ReactiveEffect {
  deps = []
  
  constructor(public fn) {}
  
  run() {
    let parent = activeEffect
    let lastShouldTrack = shouldTrack
    
    try {
      activeEffect = this
      shouldTrack = true
      return this.fn()
    } finally {
      cleanup(this)
      activeEffect = parent
      shouldTrack = lastShouldTrack
    }
  }
}

function cleanup(effect) {
  for (const dep of effect.deps) {
    dep.delete(effect)
  }
  effect.deps.length = 0
}

function effect(fn) {
  const _effect = new ReactiveEffect(fn)
  _effect.run()
  return _effect.run.bind(_effect)
}

function track(target, key) {
  if (!activeEffect) return
  
  let depsMap = targetMap.get(target)
  if (!depsMap) targetMap.set(target, depsMap = new Map())
  
  let deps = depsMap.get(key)
  if (!deps) depsMap.set(key, deps = new Set())
  
  deps.add(activeEffect)
  activeEffect.deps.push(deps)
}

function trigger(target, key) {
  const depsMap = targetMap.get(target)
  if (!depsMap) return
  
  const deps = depsMap.get(key)
  if (deps) {
    deps.forEach(effect => effect.run())
  }
}

function reactive(target) {
  if (!isObject(target)) return target
  if (target.__v_raw) return target
  
  const proxy = new Proxy(target, {
    get(target, key, receiver) {
      if (key === '__v_raw') return target
      track(target, key)
      const result = Reflect.get(target, key, receiver)
      return isObject(result) ? reactive(result) : result
    },
    
    set(target, key, value, receiver) {
      const oldValue = target[key]
      const result = Reflect.set(target, key, value, receiver)
      if (hasChanged(value, oldValue)) {
        trigger(target, key)
      }
      return result
    }
  })
  
  return proxy
}

function ref(value) {
  const ref = {
    __v_isRef: true,
    _value: isObject(value) ? reactive(value) : value,
    get value() {
      track(this, 'value')
      return this._value
    },
    set value(newVal) {
      if (hasChanged(newVal, this._value)) {
        this._value = isObject(newVal) ? reactive(newVal) : newVal
        trigger(this, 'value')
      }
    }
  }
  return ref
}

function isObject(x) {
  return x !== null && typeof x === 'object'
}

function hasChanged(a, b) {
  return !Object.is(a, b)
}
```

#### 评分标准

- 能实现 reactive/effect 基本功能：60分
- 能理解并实现依赖收集/触发：80分
- 完整实现所有功能：100分

---

## 总结

这份 Vue 3 核心源码解析面试题主要考察：

1. **整体架构**：monorepo、模块划分、职责边界
2. **响应式系统**：Proxy、effect、track/trigger、Lazy Proxy
3. **虚拟DOM**：VNode、Patch、Diff 算法、LIS 优化
4. **组件系统**：组件实例、生命周期、Teleport、Suspense
5. **编译原理**：parse/transform/codegen 三阶段、Patch Flags
6. **调度与更新**：nextTick、微任务队列、批量更新
7. **架构设计**：createRenderer、平台无关、自定义渲染器
8. **实战能力**：手写核心代码

**答题技巧**：
- 先说明设计思想，再逐步深入源码
- 可以从数据结构入手（WeakMap、Set、队列等）
- 关注关键优化（懒代理、Diff 优化等）
- 结合实际项目经验，说明设计的好处
