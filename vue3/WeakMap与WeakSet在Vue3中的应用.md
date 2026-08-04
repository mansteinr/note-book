# WeakMap 与 WeakSet 在 Vue 3 中的应用深度解析

> 本文档详细解析 WeakMap 和 WeakSet 数据结构的基本特性、实现原理，重点分析它们在 Vue 3 响应式系统中的核心应用，结合源码实现说明其内存管理优势及最佳实践。

---

## 目录

- [一、概述](#一概述)
- [二、WeakMap 基本特性](#二weakmap-基本特性)
- [三、WeakSet 基本特性](#三weakset-基本特性)
- [四、与普通 Map/Set 的区别](#四与普通-mapset-的区别)
- [五、Vue 3 响应式系统中的应用](#五vue-3-响应式系统中的应用)
  - [5.1 响应式系统架构概览](#51-响应式系统架构概览)
  - [5.2 targetMap：响应式对象依赖映射](#52-targetmap响应式对象依赖映射)
  - [5.3 effectScope 与依赖清理](#53-effectscope-与依赖清理)
  - [5.4 readonly 与 reactive 的代理映射](#54-readonly-与-reactive-的代理映射)
- [六、Vue 3 源码深度分析](#六vue-3-源码深度分析)
  - [6.1 track 函数源码解析](#61-track-函数源码解析)
  - [6.2 trigger 函数源码解析](#62-trigger-函数源码解析)
  - [6.3 reactive 函数源码解析](#63-reactive-函数源码解析)
- [七、内存管理优势分析](#七内存管理优势分析)
- [八、实际应用场景](#八实际应用场景)
- [九、使用注意事项与最佳实践](#九使用注意事项与最佳实践)
- [十、面试题精选](#十面试题精选)
- [十一、总结速查表](#十一总结速查表)

---

## 一、概述

### 1.1 为什么 Vue 3 大量使用 WeakMap

Vue 3 的响应式系统是基于 `Proxy` 实现的，在追踪依赖关系时需要建立「响应式对象 → 属性 → 副作用函数」的映射关系。如果使用普通的 `Map` 存储这种映射，当响应式对象不再被使用时，`Map` 仍然持有它的引用，导致对象无法被垃圾回收，造成**内存泄漏**。

`WeakMap` 的弱引用特性完美解决了这个问题——当响应式对象本身被销毁时，其在 `WeakMap` 中的依赖记录会自动被 GC 清理。

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 3 响应式系统为什么用 WeakMap                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  问题场景：                                                              │
│  组件 A 创建了响应式对象 state                                          │
│  state 的属性被多个 effect 追踪                                         │
│  组件 A 卸载，state 不再使用                                            │
│  → 如果用 Map 存依赖：Map 仍引用 state → state 无法回收 → 内存泄漏     │
│  → 如果用 WeakMap 存依赖：state 无其他引用时自动回收 → 无内存泄漏      │
│                                                                         │
│  核心价值：                                                              │
│  ✅ 自动清理：响应式对象被销毁时，依赖关系自动释放                       │
│  ✅ 避免内存泄漏：无需手动清理依赖映射                                   │
│  ✅ 性能优化：减少不必要的内存占用                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 二、WeakMap 基本特性

### 2.1 定义

`WeakMap` 是一种键值对集合，其中**键必须是对象**（或非注册符号），值可以是任意类型。键被持有的是**弱引用**，不阻止键对象被垃圾回收。

### 2.2 基本 API

```javascript
// 创建 WeakMap
const wm = new WeakMap();

// 基本操作
const obj = { name: 'Vue' };

wm.set(obj, 'value');        // 设置键值对
wm.get(obj);                 // 'value' —— 获取值
wm.has(obj);                 // true —— 检查键是否存在
wm.delete(obj);              // true —— 删除键值对

// 注意：WeakMap 没有 size 属性，没有 clear()，不可遍历
// wm.size      // undefined
// wm.clear()   // TypeError: wm.clear is not a function
// for (const [k, v] of wm) {}  // TypeError: wm is not iterable
```

### 2.3 弱引用机制

```javascript
// WeakMap 的弱引用特性
let key = { data: 'important' };

const wm = new WeakMap();
wm.set(key, 'metadata');

console.log(wm.get(key));  // 'metadata'

// 解除 key 的外部引用
key = null;  // 或 key 离开作用域

// 此时 { data: 'important' } 对象没有其他强引用
// WeakMap 中的键值对会在某个 GC 时机被自动清理
// 我们无法观察这个时机（因为不可遍历），但内存确实被释放了
```

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WeakMap 弱引用机制示意                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  强引用（Map）：                                                         │
│  ┌──────────┐    强引用     ┌──────────────┐                           │
│  │   Map    │ ──────────→  │  { data: 'x' } │  ← 即使外部无引用也不回收  │
│  └──────────┘              └──────────────┘                           │
│                                                                         │
│  弱引用（WeakMap）：                                                     │
│  ┌──────────┐    弱引用     ┌──────────────┐                           │
│  │ WeakMap  │ ─ ─ ─ ─ ─→  │  { data: 'x' } │  ← 外部无引用时可被回收    │
│  └──────────┘              └──────────────┘                           │
│       ↑                        ↑                                       │
│       │                        │                                       │
│  WeakMap 不阻止               外部强引用消失时                          │
│  键对象被 GC 回收             对象被 GC 回收                             │
│  → 键值对自动消失                                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.4 键类型限制

```javascript
// ✅ 正确：键必须是对象
const wm = new WeakMap();
wm.set({}, 'value');              // 普通对象
wm.set([], 'value');              // 数组对象
wm.set(() => {}, 'value');        // 函数对象
wm.set(class {}, 'value');        // 类
wm.set(Symbol('key'), 'value');   // Symbol（非注册符号）

// ❌ 错误：基本类型不能作为键
wm.set('string', 'value');        // TypeError: Invalid value used as weak map key
wm.set(42, 'value');              // TypeError
wm.set(true, 'value');            // TypeError
wm.set(null, 'value');            // TypeError
wm.set(undefined, 'value');       // TypeError
```

---

## 三、WeakSet 基本特性

### 3.1 定义

`WeakSet` 是一种对象集合，其中每个值**必须是对象**。与 `WeakMap` 类似，集合中持有的是对象的**弱引用**。

### 3.2 基本 API

```javascript
// 创建 WeakSet
const ws = new WeakSet();

// 基本操作
const obj1 = { name: 'A' };
const obj2 = { name: 'B' };

ws.add(obj1);              // 添加对象
ws.add(obj2);
ws.has(obj1);              // true —— 检查是否存在
ws.delete(obj1);           // true —— 删除对象

// 同样没有 size、不可遍历、没有 clear()
```

### 3.3 典型用途

```javascript
// 用途1：标记对象（避免重复处理）
const processed = new WeakSet();

function processOnce(obj) {
  if (processed.has(obj)) {
    return;  // 已处理过，跳过
  }
  processed.add(obj);
  // 执行处理逻辑
  doSomething(obj);
}

// 用途2：对象状态标记
const reactiveObjects = new WeakSet();

function isReactive(obj) {
  return reactiveObjects.has(obj);
}

function makeReactive(obj) {
  const proxy = new Proxy(obj, { /* ... */ });
  reactiveObjects.add(proxy);
  return proxy;
}
```

---

## 四、与普通 Map/Set 的区别

### 4.1 全面对比

| 特性 | Map | WeakMap | Set | WeakSet |
|------|-----|---------|-----|---------|
| **键/值类型** | 任意 | 键必须为对象 | 任意 | 值必须为对象 |
| **引用类型** | 强引用 | 弱引用 | 强引用 | 弱引用 |
| **GC 影响** | 不回收 | 键无引用时回收 | 不回收 | 值无引用时回收 |
| **可遍历** | ✅ | ❌ | ✅ | ❌ |
| **size 属性** | ✅ | ❌ | ✅ | ❌ |
| **clear()** | ✅ | ❌ | ✅ | ❌ |
| **内存泄漏风险** | 有 | 无 | 有 | 无 |
| **适用场景** | 通用映射 | 对象关联数据 | 去重集合 | 对象标记 |

### 4.2 遍历差异

```javascript
// Map 可遍历
const map = new Map();
map.set('a', 1).set('b', 2);
console.log(map.size);  // 2
for (const [key, value] of map) {
  console.log(key, value);  // a 1, b 2
}

// WeakSet 不可遍历
const wm = new WeakMap();
wm.set({}, 1).set({}, 2);
console.log(wm.size);  // undefined
// for (const entry of wm) {}  // TypeError

// 为什么 WeakMap 不可遍历？
// 因为键可能随时被 GC 回收，遍历过程中数量不确定
// 也不存在 keys()、values()、entries() 方法
```

### 4.3 内存行为对比

```javascript
// Map 的内存泄漏问题
const map = new Map();
function testMap() {
  const obj = { data: new Array(1000000).fill('*') };
  map.set(obj, 'metadata');
  // 函数结束后，obj 离开作用域
  // 但 Map 仍强引用 obj → obj 无法被 GC 回收 → 内存泄漏！
}
testMap();
console.log(map.size);  // 1 —— 对象仍在 Map 中

// WeakMap 自动清理
const wm = new WeakMap();
function testWeakMap() {
  const obj = { data: new Array(1000000).fill('*') };
  wm.set(obj, 'metadata');
  // 函数结束后，obj 离开作用域
  // WeakMap 是弱引用 → obj 可被 GC 回收 → 无内存泄漏
}
testWeakMap();
// obj 已被回收，wm 中的条目也会在某次 GC 后消失
// 但我们无法通过 wm.size 查看（因为不可遍历）
```

---

## 五、Vue 3 响应式系统中的应用

### 5.1 响应式系统架构概览

Vue 3 响应式系统的核心是建立「对象 → 属性 → 副作用函数」的依赖关系。这个依赖关系树使用 WeakMap 作为顶层容器。

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 3 响应式依赖关系结构                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  WeakMap (targetMap)                                                    │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Key: target (响应式对象的原始对象)                                │  │
│  │  Value: Map (depsMap)                                             │  │
│  │                                                                   │  │
│  │  ┌─────────────────────────────────────────────────────────────┐ │  │
│  │  │  target1 ──→ Map (depsMap)                                  │ │  │
│  │  │              ┌─────────────────────────────────────────┐    │ │  │
│  │  │              │ Key: key (属性名, 如 'count')            │    │ │  │
│  │  │              │ Value: Set (dep)                         │    │ │  │
│  │  │              │                                          │    │ │  │
│  │  │              │ ┌───────────────────────────────────┐   │    │ │  │
│  │  │              │ │ 'count' ──→ Set(dep)              │   │    │ │  │
│  │  │              │ │             ┌── effect1           │   │    │ │  │
│  │  │              │ │             ├── effect2           │   │    │ │  │
│  │  │              │ │             └── effect3           │   │    │ │  │
│  │  │              │ │ 'name'  ──→ Set(dep)              │   │    │ │  │
│  │  │              │ │             └── effect4           │   │    │ │  │
│  │  │              │ └───────────────────────────────────┘   │    │ │  │
│  │  │              └─────────────────────────────────────────┘    │ │  │
│  │  │                                                              │ │  │
│  │  │  target2 ──→ Map (depsMap)                                  │ │  │
│  │  │              └── ...                                        │ │  │
│  │  └─────────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  为什么用 WeakMap？                                                      │
│  当 target（原始对象）不再被引用时，整个依赖树自动被 GC 清理             │
│  → 组件销毁时，其响应式数据的依赖关系自动释放                            │
│  → 无需手动清理，避免内存泄漏                                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 targetMap：响应式对象依赖映射

`targetMap` 是 Vue 3 响应式系统的全局变量，是一个 `WeakMap`，存储所有响应式对象的依赖关系。

```javascript
// Vue 3 源码简化版（packages/reactivity/src/effect.ts）

// 全局依赖映射：原始对象 → (属性名 → 依赖集合)
const targetMap = new WeakMap();

/**
 * 收集依赖：当 effect 函数中读取响应式属性时调用
 * @param {object} target - 原始对象
 * @param {string} key - 属性名
 */
export function track(target, key) {
  // 当前没有正在执行的 effect，直接返回
  if (!activeEffect) return;
  
  // 第一层：从 targetMap 中获取 target 对应的 depsMap
  let depsMap = targetMap.get(target);
  if (!depsMap) {
    // 第一次访问该 target，创建新的 Map
    depsMap = new Map();
    targetMap.set(target, depsMap);
  }
  
  // 第二层：从 depsMap 中获取 key 对应的 dep（Set）
  let dep = depsMap.get(key);
  if (!dep) {
    // 第一次访问该属性，创建新的 Set
    dep = new Set();
    depsMap.set(key, dep);
  }
  
  // 第三层：将当前 effect 加入 dep 集合
  dep.add(activeEffect);
  
  // 同时记录 effect 的反向依赖（用于清理）
  activeEffect.deps.push(dep);
}

/**
 * 触发更新：当响应式属性被修改时调用
 * @param {object} target - 原始对象
 * @param {string} key - 属性名
 */
export function trigger(target, key) {
  // 从 targetMap 中获取依赖
  const depsMap = targetMap.get(target);
  if (!depsMap) return;  // 没有依赖，直接返回
  
  const dep = depsMap.get(key);
  if (!dep) return;
  
  // 遍历所有依赖该属性的 effect，执行更新
  const effects = new Set(dep);  // 复制一份避免遍历时修改
  effects.forEach(effect => {
    if (effect !== activeEffect) {  // 避免无限递归
      effect.run();  // 执行副作用函数
    }
  });
}
```

**实际使用示例：**

```javascript
import { reactive, effect } from 'vue';

// 创建响应式对象
const state = reactive({ count: 0, name: 'Vue' });

// 注册副作用函数
effect(() => {
  console.log(`count is: ${state.count}`);  // 读取 count，触发 track
});
// 输出：count is: 0

// 修改 count，触发 trigger
state.count++;  // 输出：count is: 1

// 上述操作在 targetMap 中的结构：
// targetMap = WeakMap {
//   { count: 0, name: 'Vue' } (原始对象) → Map {
//     'count' → Set [ effect1 ]
//   }
// }
```

### 5.3 effectScope 与依赖清理

Vue 3 引入了 `effectScope` 来管理一组 effect 的生命周期。当 scope 被销毁时，其内部所有 effect 都会被清理。

```javascript
// Vue 3 源码简化版（packages/reactivity/src/effectScope.ts）

let activeEffectScope;

class EffectScope {
  constructor(detached = false) {
    this.active = true;            // 是否活跃
    this.effects = [];             // 内部管理的 effect 列表
    this.cleanups = [];            // 清理函数列表
    this.scopes = [];              // 子 scope 列表
    this.parent = activeEffectScope;
    
    if (!detached && activeEffectScope) {
      // 挂载到父 scope
      activeEffectScope.scopes.push(this);
    }
  }
  
  /**
   * 在 scope 内运行函数
   */
  run(fn) {
    if (this.active) {
      const prev = activeEffectScope;
      activeEffectScope = this;
      try {
        return fn();
      } finally {
        activeEffectScope = prev;
      }
    }
  }
  
  /**
   * 销毁 scope，清理所有 effect
   */
  stop() {
    if (this.active) {
      // 清理所有 effect
      this.effects.forEach(e => e.stop());
      // 执行清理函数
      this.cleanups.forEach(cleanup => cleanup());
      // 递归清理子 scope
      this.scopes.forEach(s => s.stop());
      this.active = false;
    }
  }
}

function effectScope(detached) {
  return new EffectScope(detached);
}
```

**使用示例：**

```javascript
import { reactive, effect, effectScope } from 'vue';

const scope = effectScope();

scope.run(() => {
  const state = reactive({ count: 0 });
  
  effect(() => {
    console.log('count:', state.count);
  });
  
  effect(() => {
    console.log('doubled:', state.count * 2);
  });
});

state.count++;  // 输出 count: 1, doubled: 2

// 销毁 scope，所有 effect 自动停止
scope.stop();
// 响应式对象 state 如果没有其他引用 → targetMap 中的依赖自动被 GC 清理
state.count++;  // 无输出，effect 已停止
```

### 5.4 readonly 与 reactive 的代理映射

Vue 3 使用 WeakMap 存储原始对象到代理对象的映射，避免重复创建代理。

```javascript
// Vue 3 源码简化版（packages/reactivity/src/reactive.ts）

// 存储原始对象 → reactive 代理的映射
const reactiveMap = new WeakMap();

// 存储原始对象 → readonly 代理的映射
const readonlyMap = new WeakMap();

// 存储代理对象 → 原始对象的映射（用于获取原始对象）
const rawMap = new WeakMap();

/**
 * 创建响应式代理
 */
function reactive(target) {
  // 如果 target 已经是 reactive 代理，直接返回
  if (rawMap.has(target)) {
    return target;
  }
  
  // 检查是否已有对应的 reactive 代理
  const existingProxy = reactiveMap.get(target);
  if (existingProxy) {
    return existingProxy;  // 复用已有代理
  }
  
  // 创建新的 Proxy
  const proxy = new Proxy(target, {
    get(target, key, receiver) {
      // 收集依赖
      track(target, key);
      const result = Reflect.get(target, key, receiver);
      // 深层响应式：如果属性值是对象，递归创建代理
      if (typeof result === 'object' && result !== null) {
        return reactive(result);
      }
      return result;
    },
    set(target, key, value, receiver) {
      const oldValue = target[key];
      const result = Reflect.set(target, key, value, receiver);
      if (oldValue !== value) {
        // 触发更新
        trigger(target, key);
      }
      return result;
    }
  });
  
  // 存储映射
  reactiveMap.set(target, proxy);
  rawMap.set(proxy, target);
  
  return proxy;
}

/**
 * 获取原始对象（从代理对象）
 */
function toRaw(observed) {
  const raw = rawMap.get(observed);
  return raw ? toRaw(raw) : observed;
}
```

**使用示例：**

```javascript
const raw = { count: 0 };
const state1 = reactive(raw);
const state2 = reactive(raw);  // 复用 state1

console.log(state1 === state2);  // true —— 同一个代理

const state = reactive({ nested: { value: 1 } });
console.log(toRaw(state) === raw);           // false（raw 是外层）
console.log(toRaw(state.nested));            // { value: 1 } —— 获取原始嵌套对象
```

---

## 六、Vue 3 源码深度分析

### 6.1 track 函数源码解析

```javascript
// Vue 3 源码（packages/reactivity/src/effect.ts）简化版

// 全局依赖容器 —— WeakMap
const targetMap = new WeakMap();

// 当前活跃的 effect
let activeEffect = null;

// effect 栈（支持嵌套 effect）
const effectStack = [];

class ReactiveEffect {
  constructor(fn, scheduler = null) {
    this.fn = fn;             // 副作用函数
    this.scheduler = scheduler; // 调度器（用于异步更新）
    this.deps = [];           // 反向依赖记录（用于清理）
    this.active = true;       // 是否活跃
  }
  
  run() {
    if (!this.active) {
      return this.fn();
    }
    
    // 避免重复入栈
    if (effectStack.includes(this)) {
      return;
    }
    
    // 清理旧依赖（解决分支切换问题）
    cleanupEffect(this);
    
    try {
      effectStack.push(this);
      activeEffect = this;
      return this.fn();  // 执行函数，触发 track
    } finally {
      effectStack.pop();
      activeEffect = effectStack[effectStack.length - 1] || null;
    }
  }
  
  stop() {
    if (this.active) {
      cleanupEffect(this);
      this.active = false;
    }
  }
}

// 清理 effect 的所有依赖
function cleanupEffect(effect) {
  effect.deps.forEach(dep => {
    dep.delete(effect);  // 从每个 dep 中移除自己
  });
  effect.deps.length = 0;
}

/**
 * 依赖收集
 * 这是 WeakMap 使用的核心
 */
export function track(target, key) {
  if (!activeEffect) return;
  
  // ★ 第一层：WeakMap —— target → depsMap
  let depsMap = targetMap.get(target);
  if (!depsMap) {
    depsMap = new Map();
    targetMap.set(target, depsMap);  // WeakMap.set
  }
  
  // ★ 第二层：Map —— key → dep
  let dep = depsMap.get(key);
  if (!dep) {
    dep = new Set();
    depsMap.set(key, dep);
  }
  
  // ★ 第三层：Set —— dep 包含所有 effect
  if (!dep.has(activeEffect)) {
    dep.add(activeEffect);
    activeEffect.deps.push(dep);  // 反向记录，用于清理
  }
}
```

### 6.2 trigger 函数源码解析

```javascript
// Vue 3 源码简化版

export function trigger(target, key, type) {
  // 从 WeakMap 中获取该 target 的依赖映射
  const depsMap = targetMap.get(target);
  if (!depsMap) {
    // 没有被追踪过
    return;
  }
  
  const effects = new Set();  // 收集需要执行的 effect
  
  // 收集直接依赖该 key 的 effect
  const dep = depsMap.get(key);
  if (dep) {
    dep.forEach(effect => {
      if (effect !== activeEffect) {  // 避免无限递归
        effects.add(effect);
      }
    });
  }
  
  // 处理数组操作的特殊情况
  if (type === 'add' && Array.isArray(target)) {
    // 新增元素时，触发对 length 的依赖
    const lengthDep = depsMap.get('length');
    if (lengthDep) {
      lengthDep.forEach(effect => effects.add(effect));
    }
  }
  
  // 处理对象新增属性的情况（影响 for...in 遍历）
  if (type === 'add' || type === 'delete') {
    const iterateDep = depsMap.get(ITERATE_KEY);
    if (iterateDep) {
      iterateDep.forEach(effect => effects.add(effect));
    }
  }
  
  // 执行所有收集到的 effect
  effects.forEach(effect => {
    if (effect.scheduler) {
      // 有调度器：异步执行（如组件更新）
      effect.scheduler();
    } else {
      // 无调度器：同步执行
      effect.run();
    }
  });
}
```

### 6.3 reactive 函数源码解析

```javascript
// Vue 3 源码简化版（packages/reactivity/src/reactive.ts）

// ★ 核心映射表：原始对象 → 代理对象
const reactiveMap = new WeakMap();
const shallowReactiveMap = new WeakMap();
const readonlyMap = new WeakMap();
const shallowReadonlyMap = new WeakMap();

// 代理标记（特殊 key）
const ReactiveFlags = {
  IS_REACTIVE: '__v_isReactive',
  IS_READONLY: '__v_isReadonly',
  RAW: '__v_raw'
};

function createReactiveObject(target, isReadonly, baseHandlers) {
  // 非对象类型直接返回
  if (typeof target !== 'object' || target === null) {
    return target;
  }
  
  // 已经是代理对象，直接返回（通过 rawMap 检查）
  if (rawMap.has(target)) {
    return target;
  }
  
  // ★ 从 WeakMap 中查找是否已创建过代理
  const proxyMap = isReadonly ? readonlyMap : reactiveMap;
  const existingProxy = proxyMap.get(target);
  if (existingProxy) {
    return existingProxy;  // 复用已有代理，避免重复创建
  }
  
  // 创建新的 Proxy
  const proxy = new Proxy(target, baseHandlers);
  
  // ★ 存储到 WeakMap 中
  proxyMap.set(target, proxy);
  
  return proxy;
}

// 对外暴露的 reactive 函数
function reactive(target) {
  // 如果已经是 readonly，直接返回
  if (isReadonly(target)) {
    return target;
  }
  return createReactiveObject(target, false, mutableHandlers);
}
```

---

## 七、内存管理优势分析

### 7.1 组件销毁场景

```javascript
// 场景：Vue 组件的创建与销毁
import { reactive, effect } from 'vue';

function createComponent() {
  const state = reactive({ count: 0 });
  
  // 注册副作用
  const stop = effect(() => {
    console.log(state.count);
  });
  
  return { state, stop };
}

// 创建组件
let { state, stop } = createComponent();
state.count++;  // 正常触发更新

// 组件销毁
stop();         // 停止 effect
state = null;   // 解除引用

// 此时原始对象没有其他引用
// targetMap (WeakMap) 中的依赖记录会自动被 GC 清理
// 无需手动调用 targetMap.delete()
```

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    组件销毁时内存清理流程                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  组件活跃时：                                                            │
│  ┌──────────────────┐    ┌──────────────────────────────────┐          │
│  │  组件变量 state  │───→│  原始对象 { count: 0 }            │          │
│  │  (强引用)        │    │     ↑                             │          │
│  └──────────────────┘    │     │ 弱引用（WeakMap）            │          │
│                          │  targetMap                       │          │
│                          │  └──→ Map { 'count' → Set[...] } │          │
│                          └──────────────────────────────────┘          │
│                                                                         │
│  组件销毁后（state = null）：                                            │
│  ┌──────────────────┐    ┌──────────────────────────────────┐          │
│  │  组件变量 state  │    │  原始对象 { count: 0 }            │          │
│  │  = null          │    │  无强引用 ← GC 可回收             │          │
│  └──────────────────┘    └──────────────────────────────────┘          │
│                                    ↓                                    │
│                          GC 回收原始对象                                │
│                                    ↓                                    │
│                          targetMap 中对应条目自动消失                   │
│                          （WeakMap 弱引用，不阻止回收）                 │
│                                    ↓                                    │
│                          Map { 'count' → Set[...] } 也被回收           │
│                          整个依赖链自动清理                              │
│                                                                         │
│  如果用普通 Map：                                                        │
│  → Map 强引用原始对象 → 原始对象无法被 GC 回收 → 内存泄漏               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.2 内存占用对比

```javascript
// 模拟大量组件创建销毁的场景

// 使用 WeakMap（Vue 3 的做法）
const weakTargetMap = new WeakMap();

function testWeakMap() {
  for (let i = 0; i < 100000; i++) {
    const obj = { data: new Array(100).fill(i) };
    weakTargetMap.set(obj, new Map([['count', new Set()]]));
    // obj 在循环结束后无外部引用 → 可被 GC 回收
  }
  // WeakMap 中不会有残留
}

// 使用 Map（假设 Vue 用 Map）
const strongTargetMap = new Map();

function testMap() {
  for (let i = 0; i < 100000; i++) {
    const obj = { data: new Array(100).fill(i) };
    strongTargetMap.set(obj, new Map([['count', new Set()]]));
    // Map 强引用 obj → obj 无法被 GC 回收
  }
  console.log(strongTargetMap.size);  // 100000 —— 全部残留！
  // 需要手动 strongTargetMap.clear() 或逐个 delete
}

// 结论：WeakMap 在频繁创建销毁响应式对象的场景下，
// 内存占用远低于 Map
```

---

## 八、实际应用场景

### 8.1 Vue 3 响应式系统（核心应用）

```javascript
// 这是 WeakMap 在 Vue 3 中最重要的应用
import { reactive, watchEffect } from 'vue';

const state = reactive({ todos: [] });

watchEffect(() => {
  console.log('Todos:', state.todos.length);
});

// state.todos 被追踪 → targetMap 中建立依赖
// 当 state 被销毁时 → 依赖自动清理
```

### 8.2 自定义响应式实现

```javascript
// 模拟 Vue 3 实现一个简易响应式系统
const targetMap = new WeakMap();  // ★ 核心使用 WeakMap
let activeEffect = null;

function reactive(target) {
  const handlers = {
    get(obj, key) {
      // 依赖收集
      track(obj, key);
      const result = Reflect.get(obj, key);
      return typeof result === 'object' && result !== null
        ? reactive(result)
        : result;
    },
    set(obj, key, value) {
      const result = Reflect.set(obj, key, value);
      trigger(obj, key);
      return result;
    }
  };
  return new Proxy(target, handlers);
}

function track(target, key) {
  if (!activeEffect) return;
  
  // WeakMap → Map → Set 三层结构
  let depsMap = targetMap.get(target);
  if (!depsMap) {
    depsMap = new Map();
    targetMap.set(target, depsMap);
  }
  
  let dep = depsMap.get(key);
  if (!dep) {
    dep = new Set();
    depsMap.set(key, dep);
  }
  
  dep.add(activeEffect);
}

function trigger(target, key) {
  const depsMap = targetMap.get(target);
  if (!depsMap) return;
  
  const dep = depsMap.get(key);
  if (dep) {
    dep.forEach(effect => effect());
  }
}

function effect(fn) {
  activeEffect = fn;
  fn();
  activeEffect = null;
}

// 使用
const state = reactive({ count: 0 });
effect(() => {
  console.log('Count:', state.count);
});
// 输出：Count: 0

state.count = 10;  // 输出：Count: 10
```

### 8.3 DOM 元素关联数据

```javascript
// 使用 WeakMap 存储与 DOM 元素关联的数据
const elementData = new WeakMap();

function bindData(element, data) {
  elementData.set(element, data);
  // 当 element 从 DOM 中移除且无其他引用时
  // elementData 中的关联数据自动释放
}

function getData(element) {
  return elementData.get(element);
}

// 使用
const div = document.createElement('div');
bindData(div, { id: 1, metadata: 'info' });

// 后续使用
console.log(getData(div));  // { id: 1, metadata: 'info' }

// div 从 DOM 移除后
div.remove();
// 当 div 被GC回收时，关联数据自动清理
```

### 8.4 对象扩展（不污染原对象）

```javascript
// 使用 WeakMap 为对象添加额外属性，不修改原对象
const extensions = new WeakMap();

function extend(obj, props) {
  extensions.set(obj, { ...extensions.get(obj), ...props });
}

function getExtension(obj) {
  return extensions.get(obj) || {};
}

// 使用
const user = { name: 'Alice' };
extend(user, { internalId: 123, flag: true });

console.log(user);  // { name: 'Alice' } —— 原对象未被修改
console.log(getExtension(user));  // { internalId: 123, flag: true }
```

---

## 九、使用注意事项与最佳实践

### 9.1 使用注意事项

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WeakMap/WeakSet 使用注意事项                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ⚠️ 注意1：键必须是对象                                                 │
│  WeakMap 的键和 WeakSet 的值不能是基本类型                              │
│  → 需要基本类型做键时，使用普通 Map                                      │
│                                                                         │
│  ⚠️ 注意2：不可遍历                                                     │
│  没有 size、keys()、values()、entries()、forEach                       │
│  → 需要遍历时，使用普通 Map                                              │
│                                                                         │
│  ⚠️ 注意3：无法主动清理                                                 │
│  没有 clear() 方法                                                      │
│  清理依赖 GC 自动完成，时机不可控                                        │
│                                                                         │
│  ⚠️ 注意4：不适用于需要精确控制的场景                                    │
│  无法知道何时被清理                                                      │
│  无法知道当前有多少条目                                                  │
│                                                                         │
│  ⚠️ 注意5：Symbol 作为键的注意事项                                      │
│  只有非注册符号（Symbol()）可作为键                                      │
│  注册符号（Symbol.for()）不能作为键                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 9.2 最佳实践

```javascript
// ✅ 实践1：Vue 3 响应式系统推荐使用 WeakMap
// 存储对象 → 依赖的映射，避免内存泄漏
const targetMap = new WeakMap();

// ✅ 实践2：DOM 元素关联数据使用 WeakMap
const domCache = new WeakMap();
function cacheDomData(element, data) {
  domCache.set(element, data);
}

// ✅ 实践3：对象标记使用 WeakSet
const processed = new WeakSet();
function processOnce(obj) {
  if (processed.has(obj)) return;
  processed.add(obj);
  // 处理逻辑
}

// ✅ 实践4：缓存计算结果（键为对象时）
const computeCache = new WeakMap();
function expensiveCompute(obj) {
  if (computeCache.has(obj)) {
    return computeCache.get(obj);
  }
  const result = /* ... */ {};
  computeCache.set(obj, result);
  return result;
}

// ❌ 反模式1：需要遍历时使用 WeakMap
// const wm = new WeakMap();
// for (const [k, v] of wm) {}  // 报错

// ❌ 反模式2：基本类型作为键
// wm.set('string', 'value')  // 报错

// ❌ 反模式3：需要知道大小时使用 WeakMap
// console.log(wm.size)  // undefined
```

### 9.3 何时使用 WeakMap vs Map

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    选择决策树                                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  需要存储键值对？                                                        │
│    │                                                                    │
│    ├── 否 → 考虑其他数据结构                                            │
│    │                                                                    │
│    └── 是                                                               │
│         │                                                               │
│         ▼                                                               │
│       键是对象吗？                                                      │
│         │                                                               │
│         ├── 否（基本类型）→ 使用 Map                                     │
│         │                                                               │
│         └── 是（对象）                                                   │
│              │                                                          │
│              ▼                                                          │
│            需要遍历吗？                                                  │
│              │                                                          │
│              ├── 是 → 使用 Map                                          │
│              │                                                          │
│              └── 否                                                     │
│                   │                                                     │
│                   ▼                                                     │
│                 需要知道大小吗？                                         │
│                   │                                                     │
│                   ├── 是 → 使用 Map                                     │
│                   │                                                     │
│                   └── 否                                                │
│                        │                                                │
│                        ▼                                                │
│                      对象销毁后需要自动清理？                            │
│                        │                                                │
│                        ├── 是 → ✅ 使用 WeakMap                          │
│                        │                                                │
│                        └── 否 → 使用 Map                                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 十、面试题精选

### 题目 1：Vue 3 为什么用 WeakMap 存储响应式依赖？

**答案要点：**

1. **避免内存泄漏**：WeakMap 的弱引用特性使得当响应式对象（target）不再被引用时，其在 targetMap 中的依赖记录会被 GC 自动清理。如果用 Map，对象销毁后依赖记录仍存在，导致内存泄漏。

2. **自动清理**：组件频繁创建和销毁时，无需手动清理依赖映射，减少开发负担和出错可能。

3. **性能优化**：WeakMap 不需要维护引用计数，也不需要遍历清理，GC 自动处理。

4. **结构匹配**：Vue 3 的依赖结构是 `target → key → dep`，target 恰好是对象，符合 WeakMap 键必须为对象的要求。

### 题目 2：WeakMap 和 Map 的区别是什么？

**答案要点：**

| 维度 | Map | WeakMap |
|------|-----|---------|
| 键类型 | 任意 | 仅对象 |
| 引用类型 | 强引用 | 弱引用 |
| GC 影响 | 阻止键被回收 | 不阻止键被回收 |
| 可遍历 | ✅ | ❌ |
| size | ✅ | ❌ |
| clear() | ✅ | ❌ |
| 内存泄漏 | 可能 | 不会 |

### 题目 3：WeakMap 不可遍历的原因是什么？

**答案要点：**

1. **GC 时机不确定**：WeakMap 中的键可能随时被 GC 回收，遍历过程中条目数量和内容可能变化。
2. **设计哲学**：WeakMap 的设计目的是「对象关联数据」，而非「可查询的映射表」。
3. **性能考虑**：如果支持遍历，引擎需要维护完整的条目列表，违背弱引用的设计初衷。
4. **安全性**：不可遍历意味着无法通过 WeakMap 获取到键对象，不会意外延长对象生命周期。

### 题目 4：描述 Vue 3 响应式系统中 targetMap 的结构

**答案要点：**

```
targetMap = WeakMap {
  target(原始对象) → Map {
    key(属性名) → Set {
      effect1, effect2, ...
    }
  }
}
```

- **第一层 WeakMap**：target → depsMap，键是原始对象，值是属性依赖映射
- **第二层 Map**：key → dep，键是属性名，值是 effect 集合
- **第三层 Set**：存储所有依赖该属性的 effect 函数

track 时往里添加 effect，trigger 时从里取出 effect 执行。

---

## 十一、总结速查表

### WeakMap/WeakSet 核心特性

| 特性 | WeakMap | WeakSet |
|------|---------|---------|
| 存储内容 | 键值对 | 对象集合 |
| 键/值类型 | 键必须为对象 | 值必须为对象 |
| 弱引用 | 键为弱引用 | 值为弱引用 |
| 可遍历 | ❌ | ❌ |
| size | ❌ | ❌ |
| GC 自动清理 | ✅ | ✅ |

### Vue 3 中的核心应用

| 应用场景 | 使用的数据结构 | 作用 |
|---------|--------------|------|
| **targetMap** | WeakMap | 原始对象 → 属性依赖映射 |
| **reactiveMap** | WeakMap | 原始对象 → reactive 代理 |
| **readonlyMap** | WeakMap | 原始对象 → readonly 代理 |
| **rawMap** | WeakMap | 代理对象 → 原始对象 |
| **shallowReactiveMap** | WeakMap | 原始对象 → 浅层 reactive 代理 |

### 最佳实践清单

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    最佳实践清单                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ✅ 推荐使用 WeakMap 的场景：                                           │
│  □ 对象 → 数据的映射，对象销毁后数据应自动清理                           │
│  □ DOM 元素关联数据                                                     │
│  □ 响应式系统依赖追踪                                                   │
│  □ 对象扩展属性（不污染原对象）                                         │
│  □ 缓存（键为对象时）                                                   │
│                                                                         │
│  ✅ 推荐使用 WeakSet 的场景：                                           │
│  □ 对象标记（如"已处理"、"是响应式"）                                   │
│  □ 避免重复处理同一对象                                                 │
│                                                                         │
│  ❌ 不应使用 WeakMap/WeakSet 的场景：                                   │
│  □ 需要遍历条目                                                         │
│  □ 需要知道大小                                                         │
│  □ 键/值为基本类型                                                      │
│  □ 需要主动控制清理时机                                                 │
│                                                                         │
│  Vue 3 源码中的核心设计：                                               │
│  □ targetMap: WeakMap<target, Map<key, Set<effect>>>                   │
│  □ reactiveMap: WeakMap<target, proxy>                                 │
│  □ 这两个 WeakMap 确保了响应式对象销毁时依赖自动清理                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 记忆口诀

```
WeakMap 弱引用，键为对象不阻止 GC 回收
Vue 3 响应式，targetMap 用它存依赖
组件销毁对象没，依赖记录自动清
不可遍历无 size，这是设计非缺陷
Map 能遍历有 size，但强引用会泄漏
选 Map 还是 WeakMap？看键是否对象、是否需要遍历
```

---

> **文档版本**：v1.0  
> **适用版本**：Vue 3.x、JavaScript ES6+  
> **最后更新**：2026-08  
> **参考来源**：Vue 3 官方源码、MDN Web Docs、ECMAScript 规范
