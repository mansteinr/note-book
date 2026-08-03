# 高级Vue3工程师面试题

## 目录

- [高级Vue3工程师面试题](#高级vue3工程师面试题)
  - [目录](#目录)
  - [Vue3响应式原理](#vue3响应式原理)
    - [选择题](#选择题)
    - [简答题](#简答题)
    - [编程题](#编程题)
  - [Computed实现原理](#computed实现原理)
    - [选择题](#选择题-1)
    - [简答题](#简答题-1)
    - [编程题](#编程题-1)
  - [Watch实现原理](#watch实现原理)
    - [选择题](#选择题-2)
    - [简答题](#简答题-2)
    - [编程题](#编程题-2)
  - [KeepAlive实现原理](#keepalive实现原理)
    - [选择题](#选择题-3)
    - [简答题](#简答题-3)
    - [设计题](#设计题)
  - [Vue3架构与优化](#vue3架构与优化)
    - [选择题](#选择题-4)
    - [简答题](#简答题-4)
  - [父子组件生命周期调用顺序](#父子组件生命周期调用顺序)
    - [选择题](#选择题-5)
    - [简答题](#简答题-5)
  - [组合式API深入](#组合式api深入)
    - [选择题](#选择题-6)
    - [简答题](#简答题-6)
  - [Vue3编译原理](#vue3编译原理)
    - [选择题](#选择题-7)
    - [简答题](#简答题-7)
  - [性能优化](#性能优化)
    - [选择题](#选择题-8)
    - [简答题](#简答题-8)
  - [项目实战与最佳实践](#项目实战与最佳实践)
    - [选择题](#选择题-9)
    - [案例分析题](#案例分析题)
  - [源码阅读与设计思想](#源码阅读与设计思想)
    - [简答题](#简答题-9)
  - [总结](#总结)

---

## Vue3响应式原理

### 选择题

**1. Vue3响应式系统使用的是以下哪种API？**
A. Object.defineProperty
B. Proxy
C. Object.defineProperty + Proxy
D. Reflect

**答案：B**

**2. Vue3的ref和reactive的区别描述正确的是？**
A. ref用于基本类型，reactive用于对象
B. ref返回的是值本身，reactive返回代理对象
C. ref底层也是使用reactive实现的
D. reactive可以用于所有类型

**答案：C**

**3. Vue3响应式系统中，effect函数的主要作用是？**
A. 收集依赖
B. 触发更新
C. 副作用管理
D. 数据响应化

**答案：C**

**4. 关于Vue3的响应式系统，以下哪个说法是错误的？**
A. 使用Proxy可以监听对象属性的添加和删除
B. 直接给对象赋值会丢失响应性
C. Vue3的响应式系统支持Map和Set
D. 使用Proxy可以监听数组索引的变化

**答案：B**

---

### 简答题

**1. 请详细解释Vue3响应式系统的核心实现原理，包括Proxy的使用、依赖收集和更新触发的完整流程。**

**答案：**

Vue3的响应式系统基于Proxy实现，核心流程如下：

**响应式数据创建：**
```javascript
// 使用Proxy包装原始对象
const reactive = (target) => {
  return new Proxy(target, {
    get(target, key, receiver) {
      // 收集依赖
      track(target, key)
      const result = Reflect.get(target, key, receiver)
      // 嵌套对象懒代理
      if (isObject(result)) {
        return reactive(result)
      }
      return result
    },
    set(target, key, value, receiver) {
      const oldValue = target[key]
      const result = Reflect.set(target, key, value, receiver)
      if (oldValue !== value) {
        // 触发更新
        trigger(target, key)
      }
      return result
    },
    deleteProperty(target, key) {
      const hadKey = hasOwn(target, key)
      const result = Reflect.deleteProperty(target, key)
      if (hadKey && result) {
        trigger(target, key, 'DELETE')
      }
      return result
    }
  })
}
```

**依赖收集（track）：**
- 维护一个WeakMap，key是目标对象，value是Map
- 内部Map的key是属性名，value是Set（存放effects）
- 在getter中调用track，将当前effect添加到对应Set中

**更新触发（trigger）：**
- 在setter中调用trigger
- 根据操作类型（ADD/DELETE/SET）确定需要执行的effects
- 执行所有相关的副作用函数

**effect函数：**
```javascript
let activeEffect = null
const effect = (fn) => {
  const _effect = () => {
    activeEffect = _effect
    fn()
    activeEffect = null
  }
  _effect()
  return _effect
}
```

**完整工作流程：**
1. 数据通过reactive/ref变成响应式数据
2. 组件渲染会执行setup函数或render函数
3. 访问响应式数据时触发getter，调用track收集依赖
4. 响应式数据变化时触发setter，调用trigger执行effect
5. effect重新执行，组件重新渲染

---

**2. 请解释Vue3中ref和reactive的区别、各自的使用场景以及它们底层的实现原理。**

**答案：**

**区别与使用场景：**
- `ref`：可用于基本类型和对象类型，通过`.value`访问
- `reactive`：仅用于对象类型，直接访问属性，不需要`.value`

**ref实现原理：**
```javascript
const ref = (value) => {
  return {
    __v_isRef: true,
    get value() {
      track(this, 'value')
      return value
    },
    set value(newValue) {
      if (newValue !== value) {
        value = newValue
        trigger(this, 'value')
      }
    }
  }
}
```
- ref内部实际上是一个拥有getter和setter的对象
- ref的值如果是对象，内部也会通过reactive进行代理

**reactive实现原理：**
```javascript
const reactive = (target) => {
  return new Proxy(target, {
    get(target, key) {
      track(target, key)
      const res = target[key]
      // 懒代理，只有访问到的属性才会被代理
      return isObject(res) ? reactive(res) : res
    },
    set(target, key, value) {
      const oldValue = target[key]
      target[key] = value
      if (oldValue !== value) {
        trigger(target, key)
      }
      return true
    }
  })
}
```

**核心区别：**
1. **数据类型限制**：ref支持所有类型，reactive仅支持对象
2. **访问方式**：ref需要.value，reactive直接访问属性
3. **嵌套处理**：reactive深层代理，ref内部对象也会被reactive代理
4. **丢失响应性**：reactive解构或重新赋值会丢失响应性，ref不会

---

### 编程题

**1. 请手写一个简化版的Vue3响应式系统，包括reactive、effect、track、trigger的核心实现。**

**参考答案：**
```javascript
// ==================== 工具函数 ====================
const isObject = (val) => val !== null && typeof val === 'object'
const hasOwn = (target, key) => Object.prototype.hasOwnProperty.call(target, key)

// ==================== 依赖收集 ====================
let activeEffect = null
const targetMap = new WeakMap()

// 收集依赖
const track = (target, key) => {
  if (!activeEffect) return
  
  let depsMap = targetMap.get(target)
  if (!depsMap) {
    depsMap = new Map()
    targetMap.set(target, depsMap)
  }
  
  let deps = depsMap.get(key)
  if (!deps) {
    deps = new Set()
    depsMap.set(key, deps)
  }
  
  deps.add(activeEffect)
}

// 触发更新
const trigger = (target, key, type = 'SET') => {
  const depsMap = targetMap.get(target)
  if (!depsMap) return
  
  const effects = depsMap.get(key)
  if (!effects) return
  
  effects.forEach(effect => effect())
}

// ==================== effect函数 ====================
const effect = (fn) => {
  const effectFn = () => {
    try {
      activeEffect = effectFn
      fn()
    } finally {
      activeEffect = null
    }
  }
  effectFn()
  return effectFn
}

// ==================== reactive ====================
const reactive = (target) => {
  return new Proxy(target, {
    get(target, key, receiver) {
      if (key === '__v_isReactive') return true
      
      track(target, key)
      const res = Reflect.get(target, key, receiver)
      
      return isObject(res) ? reactive(res) : res
    },
    
    set(target, key, value, receiver) {
      const oldValue = target[key]
      const result = Reflect.set(target, key, value, receiver)
      
      const hadKey = hasOwn(target, key)
      
      if (!hadKey) {
        trigger(target, key, 'ADD')
      } else if (oldValue !== value) {
        trigger(target, key, 'SET')
      }
      
      return result
    },
    
    deleteProperty(target, key) {
      const hadKey = hasOwn(target, key)
      const result = Reflect.deleteProperty(target, key)
      
      if (hadKey && result) {
        trigger(target, key, 'DELETE')
      }
      
      return result
    }
  })
}

// ==================== ref ====================
const ref = (value) => {
  const refImpl = {
    __v_isRef: true,
    get value() {
      track(refImpl, 'value')
      return value
    },
    set value(newValue) {
      if (newValue !== value) {
        value = newValue
        trigger(refImpl, 'value')
      }
    }
  }
  return refImpl
}

// ==================== 测试 ====================
const obj = reactive({ count: 0, name: 'Vue3' })
const countRef = ref(100)

effect(() => {
  console.log('obj.count:', obj.count)
})

effect(() => {
  console.log('countRef:', countRef.value)
})

// 测试
obj.count++          // 输出：obj.count: 1
countRef.value = 200 // 输出：countRef: 200
```

---

## Computed实现原理

### 选择题

**1. 关于Vue3的computed，以下描述错误的是？**
A. computed默认是懒执行的
B. computed具有缓存机制
C. computed可以设置getter和setter
D. computed总是会重新计算

**答案：D**

**2. computed的getter函数中访问的响应式数据变化时，会发生什么？**
A. 立即重新计算
B. 标记为dirty，下次访问时重新计算
C. computed值直接更新
D. 什么都不做

**答案：B**

---

### 简答题

**1. 请详细解释Vue3中computed的实现原理，包括懒执行、缓存机制和脏值检测。**

**答案：**

Vue3的computed核心特点是懒执行和缓存机制，实现原理如下：

**computed的核心实现：**
```javascript
const computed = (getter) => {
  let value, isDirty = true
  
  const effectFn = effect(getter, {
    lazy: true,
    scheduler() {
      if (!isDirty) {
        isDirty = true
        trigger(computedObj, 'value')
      }
    }
  })
  
  const computedObj = {
    __v_isRef: true,
    get value() {
      if (isDirty) {
        value = effectFn()
        isDirty = false
      }
      track(computedObj, 'value')
      return value
    }
  }
  
  return computedObj
}
```

**关键机制说明：**

1. **懒执行（lazy）**：
   - 初始化时不立即计算
   - 只有当第一次访问.value时才会执行
   - 通过effect的lazy选项实现

2. **缓存机制**：
   - 使用isDirty标记是否需要重新计算
   - 依赖不变化时，直接返回上次计算的结果
   - 避免不必要的计算开销

3. **脏值检测**：
   - 当依赖变化时，将isDirty设为true
   - 通过自定义的scheduler来实现
   - 不立即重新计算，只标记状态

4. **双向computed（get/set）**：
```javascript
const computed = (options) => {
  let getter = options.get || options
  let setter = options.set
  
  // ...实现逻辑
}
```

**完整工作流程：**
1. 访问computed.value → 检查isDirty → true则执行getter → 收集依赖
2. 依赖数据变化 → 触发scheduler → 设置isDirty为true
3. 再次访问computed.value → 重新计算 → 更新值 → isDirty设为false

---

### 编程题

**1. 请手写一个简化版的computed实现，包含懒执行、缓存机制和脏值检测。**

**参考答案：**
```javascript
// 先有我们之前实现的reactive和effect系统
// 省略track/trigger/reactive的代码...

// ==================== computed实现 ====================
const computed = (getterOrOptions) => {
  let getter, setter
  
  if (typeof getterOrOptions === 'function') {
    getter = getterOrOptions
    setter = () => {
      console.warn('computed value is readonly')
    }
  } else {
    getter = getterOrOptions.get
    setter = getterOrOptions.set
  }
  
  let value
  let isDirty = true
  let activeEffect = null
  
  const effectFn = () => {
    try {
      activeEffect = effectFn
      return getter()
    } finally {
      activeEffect = null
    }
  }
  
  // 自定义scheduler，用于处理依赖变化
  const scheduler = () => {
    if (!isDirty) {
      isDirty = true
      // 触发computed自身的依赖更新
      trigger(computedRef, 'value')
    }
  }
  
  const computedRef = {
    __v_isRef: true,
    __v_isComputed: true,
    
    get value() {
      if (isDirty) {
        value = getter()
        isDirty = false
      }
      
      // 收集computed的依赖
      if (activeEffect) {
        track(computedRef, 'value')
      }
      
      return value
    },
    
    set value(newValue) {
      setter(newValue)
    }
  }
  
  return computedRef
}

// ==================== 测试 ====================
const data = reactive({ count: 0 })
const doubleCount = computed(() => {
  console.log('计算doubleCount')
  return data.count * 2
})

console.log('第一次访问doubleCount:', doubleCount.value) // 计算并输出：2
console.log('第二次访问doubleCount:', doubleCount.value) // 直接返回缓存，不计算

data.count = 1 // 依赖变化，标记dirty
console.log('第三次访问doubleCount:', doubleCount.value) // 重新计算：2
```

---

## Watch实现原理

### 选择题

**1. Vue3中，watch的以下哪个特性是watchEffect不具备的？**
A. 自动收集依赖
B. 可以获取旧值
C. 支持立即执行
D. 可以手动停止

**答案：B**

**2. 关于watch的deep选项，描述正确的是？**
A. deep: true会递归监听对象内部变化
B. deep选项会影响性能，应该尽量避免使用
C. deep选项仅适用于ref类型
D. 使用deep选项后，watch一定会执行多次

**答案：A**

---

### 简答题

**1. 请详细解释Vue3中watch的实现原理，包括watchEffect、watch的区别和各自的工作机制。**

**答案：**

**watch实现原理：**

```javascript
const watch = (source, cb, options = {}) => {
  let getter, oldValue
  
  // 处理不同类型的source
  if (isRef(source)) {
    getter = () => source.value
  } else if (isReactive(source)) {
    getter = () => source
    // 自动deep
    options.deep = true
  } else if (isFunction(source)) {
    getter = source
  } else if (Array.isArray(source)) {
    getter = () => source.map(s => {
      if (isRef(s)) return s.value
      if (isReactive(s)) return traverse(s)
      if (isFunction(s)) return s()
      return s
    })
  }
  
  // 处理deep
  if (options.deep) {
    const originalGetter = getter
    getter = () => traverse(originalGetter())
  }
  
  // 核心effect
  const job = () => {
    const newValue = effectFn()
    cb(newValue, oldValue)
    oldValue = newValue
  }
  
  const effectFn = effect(getter, {
    lazy: true,
    scheduler: job
  })
  
  // 立即执行
  if (options.immediate) {
    job()
  } else {
    oldValue = effectFn()
  }
  
  // 返回停止函数
  return () => {
    stop(effectFn)
  }
}
```

**watchEffect与watch的区别：**

| 特性 | watchEffect | watch |
|------|------------|-------|
| 执行方式 | 立即执行，自动收集依赖 | 懒执行，需要指定数据源 |
| 旧值获取 | 不支持 | 支持获取变化前后的值 |
| 明确数据源 | 不需要 | 需要明确指定 |
| deep选项 | 不需要 | 支持deep选项 |
| 使用场景 | 简单副作用 | 需要精确控制 |

**watchEffect实现原理：**
```javascript
const watchEffect = (effect) => {
  let cleanup
  const onCleanup = (fn) => {
    cleanup = fn
  }
  
  const job = () => {
    if (cleanup) {
      cleanup()
    }
    effect(onCleanup)
  }
  
  const effectFn = effect(job, {
    scheduler: job
  })
  
  return () => {
    stop(effectFn)
    if (cleanup) {
      cleanup()
    }
  }
}
```

**核心工作流程：**
1. **watch工作流程**：定义getter收集依赖 → 依赖变化触发job → 执行回调传入新旧值
2. **watchEffect工作流程**：立即执行回调 → 自动收集依赖 → 依赖变化重新执行
3. **停止机制**：通过stop函数停止watch

---

### 编程题

**1. 请手写一个简化版的watch实现，支持ref、reactive、函数、数组等source类型。**

**参考答案：**
```javascript
// 先有reactive和effect系统

// ==================== 工具函数 ====================
const isRef = (v) => v && v.__v_isRef
const isReactive = (v) => v && v.__v_isReactive
const isFunction = (v) => typeof v === 'function'

// 递归访问对象属性，用于deep watch
const traverse = (value, seen = new Set()) => {
  if (!isObject(value) || seen.has(value)) return
  seen.add(value)
  if (Array.isArray(value)) {
    for (let i = 0; i < value.length; i++) {
      traverse(value[i], seen)
    }
  } else if (typeof value === 'object') {
    for (const key in value) {
      traverse(value[key], seen)
    }
  }
  return value
}

// ==================== watch实现 ====================
const watch = (source, cb, options = {}) => {
  let getter, oldValue
  
  // 1. 标准化getter
  if (isRef(source)) {
    getter = () => source.value
  } else if (isReactive(source)) {
    getter = () => source
    options.deep = true // 自动deep
  } else if (isFunction(source)) {
    getter = source
  } else if (Array.isArray(source)) {
    getter = () => 
      source.map(s => {
        if (isRef(s)) return s.value
        if (isReactive(s)) return traverse(s)
        if (isFunction(s)) return s()
        return s
      })
  }
  
  // 2. 处理deep
  if (options.deep) {
    const originalGetter = getter
    getter = () => traverse(originalGetter())
  }
  
  // 3. 创建job
  const job = () => {
    const newValue = effectFn()
    cb(newValue, oldValue)
    oldValue = newValue
  }
  
  // 4. 创建effect
  const effectFn = effect(getter, {
    lazy: true,
    scheduler: job
  })
  
  // 5. 初始化
  if (options.immediate) {
    job()
  } else {
    oldValue = effectFn()
  }
  
  // 6. 返回停止函数
  return () => {
    stop(effectFn)
  }
}

// ==================== watchEffect实现 ====================
const watchEffect = (effect) => {
  let cleanup
  
  const onCleanup = (fn) => {
    cleanup = fn
  }
  
  const job = () => {
    if (cleanup) {
      cleanup()
    }
    effect(onCleanup)
  }
  
  const effectFn = effect(job, {
    scheduler: job
  })
  
  return () => {
    stop(effectFn)
    if (cleanup) {
      cleanup()
    }
  }
}

// ==================== 测试 ====================
const count = ref(0)
const data = reactive({ name: 'Vue3' })

// 测试watch ref
watch(count, (newVal, oldVal) => {
  console.log('count变化:', oldVal, '→', newVal)
})

// 测试watch reactive
watch(data, (newVal) => {
  console.log('data变化:', newVal)
}, { deep: true })

// 测试watchEffect
watchEffect((onCleanup) => {
  console.log('watchEffect执行:', count.value)
  onCleanup(() => {
    console.log('watchEffect清理')
  })
})

count.value++
data.name = 'Vue3更新'
```

---

## KeepAlive实现原理

### 选择题

**1. KeepAlive组件的缓存机制使用的是哪种数据结构？**
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

**3. 被KeepAlive缓存的组件，切换时会触发哪些生命周期钩子？**
A. created → mounted → unmounted
B. activated → deactivated
C. mounted → unmounted
D. beforeUnmount → unmounted

**答案：B**

---

### 简答题

**1. 请详细解释Vue3中KeepAlive组件的实现原理，包括缓存机制、LRU算法、组件激活/失活流程。**

**答案：**

**KeepAlive实现原理：**

**核心架构：**
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
    let current = null
    
    // 缓存子树
    const cacheSubtree = () => {
      if (current !== null) {
        cache.set(current.key, current)
      }
    }
    
    // 缓存淘汰
    const pruneCacheEntry = (key) => {
      const cached = cache.get(key)
      if (cached && cached.component) {
        cached.component.ctx.deactivated()
      }
      cache.delete(key)
      keys.delete(key)
    }
    
    // 监听include/exclude变化
    watch(() => [props.include, props.exclude], 
      ([include, exclude]) => {
        cache.forEach((v, key) => {
          const name = getComponentName(v.type)
          if (
            (include && !matches(include, name)) ||
            (exclude && matches(exclude, name))
          ) {
            pruneCacheEntry(key)
          }
        })
      }
    )
    
    onDeactivated(cacheSubtree)
    
    return () => {
      const key = vnode.key == null
        ? vnode.type
        : vnode.key
      let cachedVNode = cache.get(key)
      
      // 检查是否匹配
      const name = getComponentName(vnode.type)
      if (
        name &&
        ((props.include && !matches(props.include, name)) ||
        (props.exclude && matches(props.exclude, name)))
      ) {
        return vnode
      }
      
      if (cachedVNode) {
        // 命中缓存
        vnode.component = cachedVNode.component
        vnode.el = cachedVNode.el
        vnode.anchor = cachedVNode.anchor
        keys.delete(key)
        keys.add(key)
        vnode.shapeFlag |= 64 // COMPONENT_KEPT_ALIVE
      } else {
        // 添加到缓存
        keys.add(key)
        if (props.max && keys.size > parseInt(props.max, 10)) {
          pruneCacheEntry(keys.values().next().value)
        }
      }
      
      current = vnode
      vnode.shapeFlag |= 32 // COMPONENT_SHOULD_KEEP_ALIVE
      return vnode
    }
  }
}
```

**关键机制说明：**

1. **缓存结构**：
   - cache: Map，key为缓存key，value为vnode
   - keys: Set，用于LRU算法，记录访问顺序

2. **LRU淘汰策略**：
   ```javascript
   // 访问时：将key移到最后
   keys.delete(key)
   keys.add(key)
   // 淘汰时：删除第一个key（最久未使用）
   if (keys.size > max) {
     pruneCacheEntry(keys.values().next().value)
   }
   ```

3. **组件状态标记**：
   - `COMPONENT_SHOULD_KEEP_ALIVE`: 组件需要被缓存
   - `COMPONENT_KEPT_ALIVE`: 组件从缓存中恢复

4. **生命周期钩子**：
   - `activated`: 组件激活时调用
   - `deactivated`: 组件失活时调用

5. **渲染器配合**：
   - 当组件标记为应该缓存时，卸载会将DOM移动到隐藏容器而非销毁
   - 激活时，从缓存中恢复组件实例和DOM

**完整工作流程：**
1. 组件第一次渲染 → 检查include/exclude → 缓存到Map → 标记为应该缓存
2. 组件切换 → 标记为失活 → 调用deactivated钩子 → DOM移动到隐藏容器
3. 再次访问 → 检查缓存 → 命中缓存 → 调用activated钩子 → 恢复DOM
4. 超过max数量 → LRU算法淘汰最久未使用的组件

---

### 设计题

**1. 请设计一个更高级的KeepAlive组件，支持自定义缓存策略、持久化缓存等特性。**

**参考答案：**
```javascript
const AdvancedKeepAlive = {
  __isKeepAlive: true,
  props: {
    include: [String, RegExp, Array],
    exclude: [String, RegExp, Array],
    max: [String, Number],
    strategy: {
      type: String,
      default: 'LRU',
      validator: (v) => ['LRU', 'LFU', 'FIFO'].includes(v)
    },
    persistent: {
      type: Boolean,
      default: false
    },
    cacheKey: String
  },
  
  setup(props, { slots }) {
    // 数据结构初始化
    const cache = new Map()
    const cacheInfo = new Map() // 存储缓存元信息
    const keys = new Set()
    
    // 策略工厂
    const strategyHandler = {
      LRU: {
        onAccess: (key) => {
          keys.delete(key)
          keys.add(key)
        },
        getEvictionKey: () => keys.values().next().value
      },
      LFU: {
        onAccess: (key) => {
          const info = cacheInfo.get(key)
          info.frequency++
          cacheInfo.set(key, info)
        },
        getEvictionKey: () => {
          let minFreq = Infinity
          let evictKey = null
          cacheInfo.forEach((info, key) => {
            if (info.frequency < minFreq) {
              minFreq = info.frequency
              evictKey = key
            }
          })
          return evictKey
        }
      },
      FIFO: {
        onAccess: () => {},
        getEvictionKey: () => keys.values().next().value
      }
    }
    
    // 持久化逻辑
    const loadCache = () => {
      if (props.persistent && props.cacheKey) {
        try {
          const saved = localStorage.getItem(props.cacheKey)
          if (saved) {
            // 注意：实际中不能直接存储vnode，这里是简化示例
            console.log('加载缓存:', saved)
          }
        } catch (e) {
          console.error('加载缓存失败:', e)
        }
      }
    }
    
    const saveCache = () => {
      if (props.persistent && props.cacheKey) {
        try {
          localStorage.setItem(props.cacheKey, JSON.stringify({
            keys: Array.from(keys),
            timestamp: Date.now()
          }))
        } catch (e) {
          console.error('保存缓存失败:', e)
        }
      }
    }
    
    // 初始化
    onMounted(loadCache)
    onUnmounted(saveCache)
    
    // 缓存淘汰
    const pruneCacheEntry = (key) => {
      const cached = cache.get(key)
      if (cached?.component) {
        cached.component.ctx.deactivated?.()
      }
      cache.delete(key)
      cacheInfo.delete(key)
      keys.delete(key)
    }
    
    return () => {
      const children = slots.default()
      if (children.length !== 1) return children[0]
      
      const vnode = children[0]
      const key = vnode.key ?? vnode.type
      
      // 检查缓存策略
      const strategy = strategyHandler[props.strategy]
      
      // 检查include/exclude
      const name = getComponentName(vnode.type)
      if (
        name &&
        ((props.include && !matches(props.include, name)) ||
        (props.exclude && matches(props.exclude, name)))
      ) {
        return vnode
      }
      
      const cached = cache.get(key)
      
      if (cached) {
        // 命中缓存
        strategy.onAccess(key)
        vnode.component = cached.component
        vnode.el = cached.el
        vnode.shapeFlag |= 64 // COMPONENT_KEPT_ALIVE
      } else {
        // 添加到缓存
        cache.set(key, vnode)
        cacheInfo.set(key, {
          frequency: 1,
          timestamp: Date.now()
        })
        keys.add(key)
        
        // 检查是否需要淘汰
        if (props.max && keys.size > parseInt(props.max, 10)) {
          const evictKey = strategy.getEvictionKey()
          pruneCacheEntry(evictKey)
        }
      }
      
      vnode.shapeFlag |= 32 // COMPONENT_SHOULD_KEEP_ALIVE
      return vnode
    }
  }
}
```

---

## Vue3架构与优化

### 选择题

**1. Vue3相比Vue2，以下哪个不是性能提升的方面？**
A. 更小的打包体积
B. 更快的虚拟DOM
C. 更好的内存管理
D. 直接操作DOM而不是虚拟DOM

**答案：D**

**2. Vue3的Tree-shaking支持是通过什么实现的？**
A. 使用CommonJS
B. 使用ES Modules
C. 使用AMD
D. 代码压缩

**答案：B**

**3. 关于Vue3的Patch Flags，描述错误的是？**
A. 标记节点的动态属性
B. 可以减少比较范围
C. 提高diff效率
D. 只在开发模式使用

**答案：D**

---

### 简答题

**1. 请分析Vue3相比Vue2在架构设计、性能优化、开发体验等方面的改进。**

**答案：**

**架构设计改进：**
1. **Monorepo结构**：将核心拆分为多个独立包
   - `@vue/runtime-core`: 运行时核心
   - `@vue/runtime-dom`: DOM运行时
   - `@vue/compiler-core`: 编译核心
   - `@vue/reactivity`: 响应式系统
   - `@vue/shared`: 共享工具

2. **编译时优化**：
   - PatchFlags标记动态节点
   - 静态提升（hoistStatic）
   - 缓存事件处理器
   - 内联模板

**性能优化：**
1. **更小的体积**：Tree-shaking支持，按需引入
2. **更快的渲染**：虚拟DOM优化，减少比较次数
3. **更好的内存**：更合理的内存使用和回收

**开发体验改进：**
1. **组合式API**：更好的代码组织和复用
2. **TypeScript支持**：更好的类型检查
3. **开发工具**：更好的DevTools支持

**具体改进示例：**
```javascript
// 静态提升
// 编译前
<div>
  <h1>静态标题</h1>
  <p>{{ msg }}</p>
</div>

// 编译后（静态内容被提升到render函数外）
const _hoisted_1 = /*#__PURE__*/_createElementVNode("h1", null, "静态标题", -1)
const _hoisted_2 = /*#__PURE__*/_createTextVNode("静态内容")
```

---

## 父子组件生命周期调用顺序

### 选择题

**1. Vue3中，父子组件生命周期的执行顺序是？**
A. 父beforeCreate → 父created → 子beforeCreate → 子created → 子mounted → 父mounted
B. 父beforeCreate → 子beforeCreate → 子created → 父created → 子mounted → 父mounted
C. 子beforeCreate → 子created → 子mounted → 父beforeCreate → 父created → 父mounted
D. 父beforeCreate → 父created → 父mounted → 子beforeCreate → 子created → 子mounted

**答案：A**

**2. 当父组件更新时，子组件的生命周期执行顺序是？**
A. 父beforeUpdate → 子beforeUpdate → 子updated → 父updated
B. 子beforeUpdate → 子updated → 父beforeUpdate → 父updated
C. 父beforeUpdate → 父updated → 子beforeUpdate → 子updated
D. 只有父组件执行生命周期，子组件不执行

**答案：A**

---

### 简答题

**1. 请详细说明Vue3中父子组件生命周期的完整调用顺序。**

**答案：**

Vue3 中父子组件生命周期的执行遵循"**从外到内，再从内到外**"的原则，具体顺序如下：

**挂载阶段（首次渲染）：**
```
父 beforeCreate → 父 created → 父 beforeMount
  → 子 beforeCreate → 子 created → 子 beforeMount → 子 mounted
→ 父 mounted
```

**更新阶段：**
```
父 beforeUpdate
  → 子 beforeUpdate → 子 updated
→ 父 updated
```

**销毁阶段：**
```
父 beforeUnmount
  → 子 beforeUnmount → 子 unmounted
→ 父 unmounted
```

**核心规律：**
- **挂载**：父组件"前三个"钩子先执行，等待子组件完全挂载后，父组件才执行 mounted
- **更新**：父组件先开始更新，等待子组件更新完成后，父组件才完成更新
- **销毁**：父组件先开始销毁，等待子组件销毁完成后，父组件才完成销毁

**总结：父组件的"开始"钩子先执行，等待子组件完成所有操作后，父组件的"结束"钩子才执行。**

---

## 组合式API深入

### 选择题

**1. 组合式API中的ref和toRef/toRefs有什么区别？**
A. 没有区别
B. ref是响应式，toRef不是
C. toRef用于保持与源对象的响应式连接
D. ref只能用于基本类型

**答案：C**

**2. 关于provide/inject的描述，正确的是？**
A. 只能在setup()中使用
B. provide传递的数据在子组件中修改会影响父组件
C. inject的数据默认是响应式的
D. provide/inject只能传基本类型

**答案：B**

**3. customHook的最佳实践不包括？**
A. 以use开头命名
B. 返回ref对象
C. 包含完整的组件模板
D. 可以组合其他hook

**答案：C**

---

### 简答题

**1. 请谈谈组合式API相比选项式API的优势，以及如何设计可复用的custom hook。**

**答案：**

**组合式API的优势：**

1. **更好的代码组织**：相关逻辑可以放在一起
```javascript
// 选项式API - 相关逻辑分散在各个选项中
export default {
  data() { return { count: 0 } },
  methods: { increment() { this.count++ } },
  computed: { double() { return this.count * 2 } }
}

// 组合式API - 相关逻辑聚合在一起
export default {
  setup() {
    const count = ref(0)
    const double = computed(() => count.value * 2)
    const increment = () => count.value++
    return { count, double, increment }
  }
}
```

2. **更好的逻辑复用**：
```javascript
// 可复用的useCounter
function useCounter() {
  const count = ref(0)
  const increment = () => count.value++
  return { count, increment }
}

// 在多个组件中使用
const { count: c1, increment: i1 } = useCounter()
const { count: c2, increment: i2 } = useCounter()
```

3. **更好的类型推断**：TypeScript支持更好

4. **更少的运行时开销**

**Custom Hook设计原则：**

1. **命名规范**：use开头，语义化
2. **返回值设计**：
   - 返回单个值：`return value`
   - 返回多个值：`return [a, b]`或`return { a, b }`
3. **参数设计**：接受配置，提供默认值
4. **内部状态**：内部状态封装，暴露必要接口
5. **清理函数**：返回stop函数
6. **可测试性**：易于独立测试

**最佳实践示例：**
```javascript
function useFetch(url, options = {}) {
  const data = ref(null)
  const error = ref(null)
  const loading = ref(false)
  
  const execute = async () => {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(url, options)
      data.value = await res.json()
    } catch (e) {
      error.value = e
    } finally {
      loading.value = false
    }
  }
  
  if (options.immediate !== false) {
    execute()
  }
  
  return { data, error, loading, execute }
}
```

---

## Vue3编译原理

### 选择题

**1. Vue3的template编译不包括以下哪个阶段？**
A. parse（解析）
B. transform（转换）
C. generate（生成）
D. execute（执行）

**答案：D**

**2. Vue3的静态提升优化的主要作用是？**
A. 减少内存使用
B. 避免重复创建相同节点
C. 提高渲染性能
D. 减少代码体积

**答案：B**

**3. PatchFlags的作用是？**
A. 标记哪些元素是静态的
B. 标记节点的动态属性，优化diff
C. 提供调试信息
D. 标记组件类型

**答案：B**

---

### 简答题

**1. 请解释Vue3的template编译流程，包括parse、transform、generate三个阶段的具体工作。**

**答案：**

Vue3的编译流程分为三个阶段：

**1. Parse（解析）阶段：**
- 将template字符串解析成抽象语法树（AST）
```javascript
// 输入模板
<div id="app">
  <h1>{{ title }}</h1>
</div>

// 生成AST（简化）
{
  tag: 'div',
  props: [{ name: 'id', value: 'app' }],
  children: [
    {
      tag: 'h1',
      children: [{ type: 2, content: 'title' }]
    }
  ]
}
```

**2. Transform（转换）阶段：**
- 处理AST，进行优化转换
- 静态提升、PatchFlags标记、缓存事件处理等

```javascript
// 优化后的AST
{
  tag: 'div',
  props: [{ name: 'id', value: 'app' }],
  children: [
    {
      tag: 'h1',
      children: [{ type: 2, content: 'title' }],
      patchFlag: 1 // TEXT
    }
  ]
}
```

**3. Generate（生成）阶段：**
- 将优化后的AST生成渲染函数代码

```javascript
// 生成的渲染函数
import { createVNode as _createVNode, toDisplayString as _toDisplayString, openBlock as _openBlock, createBlock as _createBlock } from "vue"

const _hoisted_1 = { id: "app" }

export function render(_ctx, _cache, $props, $setup, $data, $options) {
  return (_openBlock(), _createBlock("div", _hoisted_1, [
    _createVNode("h1", null, _toDisplayString(_ctx.title), 1 /* TEXT */)
  ]))
}
```

**关键优化点：**

1. **PatchFlags**：标记动态部分，减少diff范围
```typescript
const PatchFlags = {
  TEXT: 1,
  CLASS: 1 << 1,
  STYLE: 1 << 2,
  PROPS: 1 << 3,
  FULL_PROPS: 1 << 4,
  HYDRATE_EVENTS: 1 << 5,
  STABLE_FRAGMENT: 1 << 6,
  KEYED_FRAGMENT: 1 << 7,
  UNKEYED_FRAGMENT: 1 << 8,
  NEED_PATCH: 1 << 9,
  DYNAMIC_SLOTS: 1 << 10,
  HOISTED: -1,
  BAIL: -2
}
```

2. **静态提升**：将静态内容提升到render函数外，避免重复创建
3. **事件缓存**：内联事件处理器缓存
4. **v-once**：只渲染一次的标记

---

## 性能优化

### 选择题

**1. 以下哪个不是Vue3的性能优化策略？**
A. 虚拟DOM优化
B. 响应式系统优化
C. 编译时优化
D. 自动删除未使用的代码

**答案：D**

**2. v-for渲染列表时，key的最佳实践是？**
A. 使用索引
B. 使用唯一且稳定的id
C. 使用随机数
D. 不使用key

**答案：B**

**3. 关于Vue3组件更新优化，描述正确的是？**
A. 每次都完整重新渲染
B. 使用PatchFlags只比较动态部分
C. 组件总是重新渲染
D. 只比较props变化

**答案：B**

---

### 简答题

**1. Vue3应用的常见性能优化策略有哪些？请从编译时、运行时、架构设计等层面说明。**

**答案：**

**编译时优化：**
1. **使用生产构建**：去掉警告和调试代码
2. **Tree-shaking**：确保使用ES模块，打包时去掉未使用代码
3. **模板预编译**：在构建时编译，不是在浏览器中

**运行时优化：**
1. **合理使用key**：避免不必要的DOM操作
```javascript
// ❌ 错误
<div v-for="(item, index) in list" :key="index">

// ✅ 正确
<div v-for="item in list" :key="item.id">
```

2. **避免不必要的响应式**：
```javascript
// 不需要响应的数据
const staticData = markRaw({...})
// 浅响应式
const shallow = shallowReactive({...})
```

3. **计算属性缓存**：合理使用computed
4. **函数式组件**：无状态组件使用Functional
5. **v-once**：只渲染一次的内容
```html
<span v-once>{{ someStaticData }}</span>
```

6. **虚拟列表**：大数据量只渲染可见区域
```javascript
import { useVirtualList } from '@vueuse/core'
```

**架构设计优化：**
1. **组件懒加载**：
```javascript
const LazyComponent = defineAsyncComponent(() => 
  import('./LazyComponent.vue')
)
```

2. **路由懒加载**：
```javascript
const Home = () => import('./Home.vue')
const routes = [{ path: '/', component: Home }]
```

3. **合理的组件拆分**：避免过大组件
4. **状态管理优化**：Pinia模块分割
5. **防抖节流**：事件处理优化

**性能调试工具：**
- Vue DevTools性能分析
- Chrome Performance面板
- Lighthouse审计

---

## 项目实战与最佳实践

### 选择题

**1. Vue3项目中，关于TypeScript的使用，最佳实践是？**
A. 尽量不用TypeScript
B. 使用any类型
C. 充分利用类型系统，避免any
D. 只在特殊文件使用TypeScript

**答案：C**

**2. Vue3项目的组件命名最佳实践是？**
A. 全小写
B. 驼峰式
C. PascalCase或kebab-case
D. 随便怎么命名

**答案：C**

**3. 关于Vue3的状态管理，推荐使用？**
A. Vuex
B. Pinia
C. 简单的store
D. 不需要状态管理

**答案：B**

---

### 案例分析题

**1. 请设计一个Vue3电商项目的技术架构和组件划分方案，包括状态管理、API请求封装、组件设计等。**

**参考答案：**

**项目架构设计：**

```
src/
├── components/
│   ├── base/
│   │   ├── Button.vue
│   │   ├── Input.vue
│   │   └── Card.vue
│   ├── business/
│   │   ├── ProductCard.vue
│   │   ├── CartItem.vue
│   │   └── UserAvatar.vue
│   └── layout/
│       ├── Header.vue
│       ├── Footer.vue
│       └── Sidebar.vue
├── views/
│   ├── Home.vue
│   ├── ProductDetail.vue
│   ├── Cart.vue
│   └── User.vue
├── stores/
│   ├── useCartStore.ts
│   ├── useUserStore.ts
│   └── useProductStore.ts
├── composables/
│   ├── useRequest.ts
│   ├── usePagination.ts
│   └── useDebounce.ts
├── api/
│   ├── request.ts
│   ├── product.ts
│   ├── cart.ts
│   └── user.ts
├── types/
│   ├── product.ts
│   ├── user.ts
│   └── cart.ts
├── utils/
│   ├── format.ts
│   ├── validate.ts
│   └── request.ts
├── router/
│   └── index.ts
└── App.vue
```

**状态管理（Pinia）：**

```typescript
// stores/useCartStore.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { CartItem, Product } from '@/types'

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])
  
  const totalPrice = computed(() => 
    items.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
  )
  
  const totalCount = computed(() => 
    items.value.reduce((sum, item) => sum + item.quantity, 0)
  )
  
  const addItem = (product: Product, quantity = 1) => {
    const existing = items.value.find(item => item.id === product.id)
    if (existing) {
      existing.quantity += quantity
    } else {
      items.value.push({ ...product, quantity })
    }
  }
  
  const removeItem = (id: number) => {
    const index = items.value.findIndex(item => item.id === id)
    if (index > -1) {
      items.value.splice(index, 1)
    }
  }
  
  const updateQuantity = (id: number, quantity: number) => {
    const item = items.value.find(item => item.id === id)
    if (item) {
      item.quantity = quantity
    }
  }
  
  const clearCart = () => {
    items.value = []
  }
  
  return {
    items,
    totalPrice,
    totalCount,
    addItem,
    removeItem,
    updateQuantity,
    clearCart
  }
})
```

**API请求封装：**

```typescript
// api/request.ts
import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores'

const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    const { code, data, message } = response.data
    if (code === 200) {
      return data
    } else {
      ElMessage.error(message || '请求失败')
      return Promise.reject(new Error(message))
    }
  },
  (error) => {
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      userStore.logout()
      window.location.href = '/login'
    }
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

export default request
```

**Composable封装：**

```typescript
// composables/useRequest.ts
import { ref, computed } from 'vue'
import type { Ref } from 'vue'

export function useRequest<T>(
  requestFn: () => Promise<T>,
  options = { immediate: true }
) {
  const data = ref<T | null>(null) as Ref<T | null>
  const error = ref<Error | null>(null)
  const loading = ref(false)
  
  const execute = async () => {
    loading.value = true
    error.value = null
    try {
      data.value = await requestFn()
    } catch (e) {
      error.value = e as Error
    } finally {
      loading.value = false
    }
  }
  
  if (options.immediate) {
    execute()
  }
  
  return {
    data,
    error,
    loading,
    execute
  }
}
```

**组件设计原则：**
1. **单一职责**：每个组件只做一件事
2. **Props向下**：通过props传递数据
3. **Events向上**：通过emit向上通信
4. **插槽扩展**：使用slot提供扩展点
5. **可组合**：组件之间可以组合使用
6. **可测试**：易于单元测试

---

## 源码阅读与设计思想

### 简答题

**1. 阅读Vue3源码后，谈谈你对Vue设计思想的理解，哪些设计让你印象深刻？**

**答案：**

**核心设计思想：**

1. **渐进式架构**：
   - 可以只使用核心，也可以使用完整生态
   - 从简单到复杂，逐步升级

2. **响应式优先**：
   - 声明式API让开发者聚焦于业务逻辑
   - 自动依赖追踪，精确更新

3. **组合优于继承**：
   - Composition API体现了这一点
   - 更灵活的代码复用方式

4. **编译时优化**：
   - Template编译时做大量优化
   - 提供更直观的开发体验

**印象深刻的设计：**

**1. Proxy响应式系统：**
- 相比Object.defineProperty更强大
- 支持数组索引、新增删除属性
- 懒代理，性能更好

**2. 渲染器的抽象设计：**
```javascript
// createRenderer可以支持自定义渲染器
createRenderer({
  createElement,
  insert,
  patchProp,
  // ...
})
```
这让Vue可以支持多个平台（Web、Weex、小程序等）

**3. 编译时优化：**
- PatchFlags、静态提升、缓存事件处理器
- 在保持开发体验的同时提升性能

**4. 组件的抽象设计：**
- 组件的设计非常优雅
- props、emit、slots、attrs等概念清晰

**5. 插件系统的设计：**
- 简单的use API
- 可扩展性非常好

---

**2. 请谈谈Vue3源码的整体架构，以及各核心模块的职责。**

**答案：**

**Vue3源码架构：**

```
vue-next/
├── packages/
│   ├── reactivity/        # 响应式系统
│   ├── runtime-core/     # 运行时核心
│   ├── runtime-dom/      # DOM运行时
│   ├── runtime-test/     # 测试工具
│   ├── compiler-core/    # 编译核心
│   ├── compiler-dom/     # DOM编译
│   ├── compiler-sfc/     # SFC编译
│   ├── server-renderer/  # 服务端渲染
│   ├── shared/           # 共享工具
│   └── vue/              # 完整入口
```

**核心模块职责：**

**1. @vue/reactivity：**
- 独立的响应式系统
- 可以在非Vue项目中使用
- 核心是Proxy、effect、track、trigger

**2. @vue/runtime-core：**
- 创建虚拟DOM
- 组件实例化
- Patch逻辑
- 生命周期管理
- 平台无关的核心逻辑

**3. @vue/runtime-dom：**
- 浏览器端实现
- DOM操作封装
- 事件处理
- 样式处理

**4. @vue/compiler-core：**
- 模板解析
- AST转换
- 代码生成
- 优化策略

**5. @vue/compiler-dom：**
- DOM相关编译
- v-model、v-on等转换
- DOM特有的指令处理

**数据流转：**

```
Template
   ↓ (Compiler)
Render Function
   ↓ (Runtime)
Virtual DOM
   ↓ (Patch)
Actual DOM
```

---

## 总结

高级Vue3工程师需要掌握的核心知识：

1. **响应式原理**：Proxy、依赖收集、ref/reactive实现
2. **核心API原理**：computed、watch、keep-alive等
3. **编译原理**：模板编译、优化策略
4. **性能优化**：编译时优化、运行时优化
5. **架构设计**：组件设计、状态管理、项目架构
6. **源码阅读**：核心模块、设计思想
7. **工程实践**：TypeScript、测试、部署
8. **生态系统**：Router、Pinia、UI库、工具库

希望这份面试题能帮助你更好地准备Vue3相关的面试！
