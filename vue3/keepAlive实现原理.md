

Vue3 的 KeepAlive 组件是一个内置组件，用于缓存不活动的组件实例，以避免重复渲染和保持状态。它的实现原理主要依赖于 Vue 的渲染器（renderer）和虚拟节点（vnode）的概念。

### 实现原理

1. **缓存机制**：KeepAlive 内部维护一个缓存对象（cache），用于存储被缓存的组件实例。这个缓存对象是一个 Map，键为组件的 key（默认基于组件的类型和 props 生成），值为组件的 vnode。
2. **渲染过程**：
   - 当包裹在 KeepAlive 内的组件切换时（例如通过 v-if 或动态组件），KeepAlive 会检查该组件是否在缓存中存在。
   - 如果存在，则直接使用缓存的 vnode，并将其激活（调用 activated 生命周期钩子，即再次激活：从缓存中取出实例，标记为 **COMPONENT_SHOULD_KEEP_ALIVE**）；如果不存在，则将其添加到缓存中(即首次渲染：缓存组件实例，标记为 **COMPONENT_KEPT_ALIVEZ**)。
   - 当组件被移除时（切换走），KeepAlive 并不会销毁它，而是将其移出当前 DOM 树（但保留在内存中），并调用 deactivated 钩子，也就是将组件移入隐藏容器（storageContainer）而非销毁。
3. **LRU（最近最少使用）算法**：为了防止缓存无限制增长，KeepAlive 默认会使用 LRU 策略来淘汰最久没有被访问的缓存实例。当缓存实例数量超过设置的最大值（通过 `max` 属性设置）时，最久未被访问的实例会被销毁。
4.  **生命周期钩子**：被 KeepAlive 包裹的组件会拥有两个额外的生命周期钩子：`activated` 和 `deactivated`，分别在组件被激活（插入到 DOM 树）和停用（从 DOM 树移除，但保留在内存）时触发。

### 核心代码解析

```javascript
const KeepAliveImpl = {
  __isKeepAlive: true,
  props: {
    include: [String, RegExp, Array], // 匹配到的组件会被缓存
    exclude: [String, RegExp, Array], // 匹配到的组件不会被缓存
    max: [String, Number] // 最大缓存数
  },
  setup(props, { slots }) {
    const cache = new Map() // 缓存 vnode 的 Map
    const keys = new Set() // 用于记录 key 的顺序，实现 LRU
    let pendingCacheKey = null
    // 创建隐藏容器（用于存放缓存的DOM）
    const storageContainer = document.createElement('div')
    const cacheSubtree = () => {
      // 在组件更新前缓存当前子树（即被 KeepAlive 包裹的组件）
      if (pendingCacheKey !== null) {
        cache.set(pendingCacheKey, instance.subTree)
      }
    }
    onMounted(cacheSubtree)
    onUpdated(cacheSubtree)
    return () => {
      // 获取默认插槽的内容
      const children = slots.default()
      if (children.length !== 1) {
        return children[0]
      }
      const vnode = children[0]
      const comp = vnode.type
      const key = vnode.key == null ? comp : vnode.key
      // 检查 include 和 exclude
      const name = comp.name
      if (name && (
        (props.include && !matches(props.include, name)) ||
        (props.exclude && matches(props.exclude, name))
      ) {
        return vnode // 直接渲染（不缓存）
      }
      // 5. 命中缓存
      const cacheKey = key
      pendingCacheKey = cacheKey
      // 如果缓存中存在，则从缓存中取出
      const cachedVNode = cache.get(cacheKey)
      if (cachedVNode) {
        // 更新 keys 的顺序，表示最近访问
        keys.delete(cacheKey)
        keys.add(cacheKey)
        // 标记 vnode 是从缓存中取出的
        vnode.el = cachedVNode.el
        vnode.component = cachedVNode.component
        // 避免挂载
        vnode.shapeFlag |= 512 /* ShapeFlags.COMPONENT_KEPT_ALIVE */
      } else {
        // 首次缓存
        keys.add(cacheKey)
        // 如果超过最大数量，则移除最久未使用的
        if (props.max && keys.size > parseInt(props.max, 10)) {
          pruneCacheEntry(keys.values().next().value)
        }
      }
      // 标记 vnode 是 KeepAlive 的，避免被卸载
      vnode.shapeFlag |= 256 /* ShapeFlags.COMPONENT_SHOULD_KEEP_ALIVE */
      return vnode
    }
  }
}


// 7. 缓存淘汰函数
function pruneCacheEntry(key: string | number) {
  const cached = cache.get(key)!
  // 触发组件卸载生命周期（实际DOM被移动到隐藏容器）
  unmount(cached)
  cache.delete(key)
  keys.delete(key)
}

// 8. 渲染器特殊处理（@vue/runtime-core）
function unmount(vnode) {
  if (vnode.shapeFlag & ShapeFlags.COMPONENT_SHOULD_KEEP_ALIVE) {
    // 将组件DOM移动到隐藏容器（而非删除）
    move(vnode, storageContainer)
    return
  }
  // ...正常卸载
}
```

### 关键点说明

1. **缓存对象**：使用 `Map` 存储 vnode，并通过 `keys`（一个 Set）记录访问顺序。
2. **LRU 策略**：在添加新缓存时，如果超过 `max`，则删除 `keys` 中的第一个元素（即最久未访问的）。
3. **标记 vnode**：通过修改 vnode 的 `shapeFlag` 属性，告诉渲染器这个组件应该被缓存或从缓存中恢复。
4. **挂载/更新时缓存子树**：在 `onMounted` 和 `onUpdated` 钩子中缓存当前组件的子树（即被 KeepAlive 包裹的组件的 vnode）。
5. **include/exclude**：根据组件名称（name）匹配是否需要缓存。



### 辅助函数
- `matches`：用于检查组件名是否匹配 include 或 exclude 的模式。
- `pruneCacheEntry`：用于删除缓存中的条目，并调用组件的卸载生命周期。

### 关键点说明

1、失活的组件被移动到隐藏的 storageContainer 容器，而非销毁 DOM 节点：

```
// 伪代码：移动 DOM 到隐藏容器
storageContainer.appendChild(vnode.component.subTree.el)
```

2、LRU 淘汰逻辑

```
keys: Set(['A', 'B', 'C']) // 访问顺序
// 当访问已缓存的 B 时：
keys.delete('B'); keys.add('B') // 变为 ['A','C','B']
// 淘汰时删除 keys 的第一个值（最久未访问）
```