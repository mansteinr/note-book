# Vue 3 `watch` 实现原理与实践指南

> `watch` 用于观察响应式数据变化后执行副作用：请求接口、同步 URL、写入本地缓存、启动或清理外部资源等。它不负责“派生一个值”，那是 `computed` 的职责。

## 目录

- [一、watch 解决什么问题](#一watch-解决什么问题)
- [二、watch 的核心组成](#二watch-的核心组成)
- [三、调度时机 flush](#三调度时机-flush)
- [四、清理过期副作用](#四清理过期副作用)
- [五、简化实现](#五简化实现)
- [六、watch 与 watchEffect](#六watch-与-watcheffect)
- [七、常见用法](#七常见用法)
- [八、常见误区](#八常见误区)
- [九、面试速答](#九面试速答)

---

## 一、watch 解决什么问题

当“某个数据变化后，需要做一件外部事情”时使用 `watch`：

```javascript
const keyword = ref('');
const results = ref([]);

watch(keyword, async (newKeyword) => {
  results.value = await search(newKeyword);
});
```

这里 `results` 不是简单由 `keyword` 同步推导的值，因为它依赖异步网络请求。因此应该用 `watch`，而不是 `computed`。

`watch` 的特点：

- 明确指定依赖源；
- 能获取新值和旧值；
- 仅在值真正变化时执行（深度监听等特殊场景除外）；
- 可控制回调在组件更新前、后或同步执行；
- 可以清理上一次尚未完成的副作用。

## 二、watch 的核心组成

一个 `watch` 可以拆成四部分：

```text
source（监听源） → getter（读取依赖） → ReactiveEffect（追踪变化） → scheduler（调度回调）
```

### 2.1 监听源会被标准化为 getter

`watch` 支持多种 source。Vue 会先把它们转换成统一的 getter：

```javascript
watch(count, callback);                    // ref
watch(() => state.userId, callback);       // getter
watch([count, () => state.userId], callback); // 多个 source
watch(state, callback);                    // reactive 对象：隐式深度监听
```

概念上的转换如下：

```javascript
function normalizeSource(source) {
  if (isRef(source)) return () => source.value;
  if (isReactive(source)) return () => traverse(source);
  if (Array.isArray(source)) return () => source.map(normalizeSourceValue);
  if (typeof source === 'function') return source;
  return () => undefined;
}
```

### 2.2 oldValue 与 newValue

首次执行 getter 后，返回值被保存为 `oldValue`。依赖触发时，Vue 再执行 getter 得到 `newValue`，并判断是否需要执行回调：

```text
oldValue = getter()

依赖变化
  → newValue = getter()
  → 若值变化（或 deep / forceTrigger）
  → callback(newValue, oldValue)
  → oldValue = newValue
```

对 reactive 对象进行深度监听时，新旧值往往是同一个代理对象引用；此时不要依赖 `oldValue !== newValue` 判断内部字段变化。

## 三、调度时机 `flush`

`watch` 默认不是立即同步执行回调，而是加入 Vue 的更新队列。`flush` 决定回调相对组件渲染的执行时机：

| 配置 | 时机 | 适用场景 |
| --- | --- | --- |
| `'pre'`（默认） | 组件更新前、同一轮异步队列中 | 根据状态更新其他状态，默认选择 |
| `'post'` | 组件 DOM 更新后 | 读取或操作更新后的 DOM |
| `'sync'` | 依赖变化时立刻执行 | 极少数必须同步的场景，避免用于高频数据 |

```javascript
watch(selectedId, () => {
  // DOM 已更新，可以安全读取对应节点
  measureSelectedRow();
}, { flush: 'post' });
```

`flush: 'sync'` 会失去批处理能力：连续修改多次响应式数据，回调可能执行多次，容易产生性能问题或递归更新。

## 四、清理过期副作用

异步请求最容易发生竞态：用户快速输入 `v`、`vu`、`vue`，较慢的旧请求可能最后返回并覆盖新结果。

Vue 提供 `onCleanup`（回调第三个参数）注册清理函数；下一次回调执行前或停止监听时，它会被调用。

```javascript
watch(keyword, async (value, _oldValue, onCleanup) => {
  const controller = new AbortController();

  onCleanup(() => controller.abort());

  const response = await fetch(`/api/search?q=${encodeURIComponent(value)}`, {
    signal: controller.signal
  });
  results.value = await response.json();
});
```

Vue 3.5+ 还提供 `onWatcherCleanup()`；它必须在 watcher 回调的同步执行阶段调用，不能放在第一个 `await` 之后。跨版本项目使用回调参数 `onCleanup` 更直观。

## 五、简化实现

以下代码用于理解流程，不是 Vue 源码的逐行复制。

```javascript
function simpleWatch(source, callback, options = {}) {
  const getter = normalizeSource(source, options.deep);
  let cleanup;
  let oldValue;

  const onCleanup = (fn) => {
    cleanup = fn;
  };

  const job = () => {
    const newValue = effect.run();
    const changed = options.deep || hasChanged(newValue, oldValue);

    if (!changed) return;

    cleanup?.();
    callback(newValue, oldValue, onCleanup);
    oldValue = newValue;
  };

  const scheduler = () => {
    if (options.flush === 'sync') {
      job();
    } else if (options.flush === 'post') {
      queuePostRenderEffect(job);
    } else {
      queuePreFlushCb(job);
    }
  };

  const effect = new ReactiveEffect(getter, scheduler);

  if (options.immediate) {
    job();
  } else {
    oldValue = effect.run(); // 首次只收集依赖，不执行回调
  }

  return () => {
    cleanup?.();
    effect.stop();
  };
}
```

实现中的关键点：

1. `effect.run()` 执行 getter 并收集它读到的响应式依赖；
2. 依赖改变后，不直接调用 callback，而是交给 scheduler 调度；
3. 执行 callback 前先清理上一轮副作用；
4. 返回的 stop 函数可手动停止监听并触发清理。

## 六、watch 与 watchEffect

| 特性 | `watch` | `watchEffect` |
| --- | --- | --- |
| 依赖来源 | 显式指定 | 自动收集同步执行期间访问到的依赖 |
| 新旧值 | 可获得 | 不直接提供 |
| 默认执行 | 依赖变化后 | 创建时立即执行一次 |
| 适用场景 | 依赖明确、需比较新旧值 | 依赖较多且只关心“重新执行副作用” |

```javascript
// 适合 watch：只在 userId 改变时请求，且要拿到旧值
watch(() => route.params.userId, (userId, oldUserId) => {
  loadUser(userId);
});

// 适合 watchEffect：同步访问到的依赖会自动收集
watchEffect(() => {
  document.title = `${user.value.name} - ${appName.value}`;
});
```

注意：`watchEffect` 中 `await` 之后访问的响应式数据不会被该次执行自动追踪。异步逻辑依赖明确时，通常使用 `watch` 更清晰。

## 七、常见用法

### 7.1 立即执行

```javascript
watch(
  () => route.params.id,
  (id) => loadDetail(id),
  { immediate: true }
);
```

`immediate: true` 会在创建 watcher 时先执行一次回调；此时 `oldValue` 是 `undefined`。

### 7.2 深度监听与有限深度

```javascript
// 监听对象内部任意层级变化；大对象上要谨慎使用
watch(form, validateForm, { deep: true });

// Vue 3.5+：最多遍历两层，降低深层对象的遍历成本
watch(form, validateForm, { deep: 2 });
```

深度监听不是对对象做深拷贝，而是遍历属性以触发依赖收集。对象很大或变化频繁时，应监听更具体的 getter：

```javascript
watch(() => form.profile.email, validateEmail);
```

### 7.3 一次性监听与手动停止

```javascript
// Vue 3.4+：首次变化后自动停止
watch(hasPermission, openGuide, { once: true });

const stop = watch(connectionState, syncStatus);
// 不再需要监听时
stop();
```

在 `setup()` 中同步创建的 watcher 会随组件卸载自动停止；异步回调中创建的 watcher 可能不绑定当前组件，应保存 `stop` 并主动清理。

## 八、常见误区

| 误区 | 问题 | 建议 |
| --- | --- | --- |
| 用 `watch` 同步派生值 | 多了一份可变状态，易不同步 | 用 `computed` 表达派生状态 |
| 深度监听整个大型 store | 每次遍历与触发范围过大 | 监听具体字段或使用有限深度 |
| 异步请求没有清理 | 旧请求可能覆盖新请求 | 使用 `AbortController` + `onCleanup` |
| 用 `flush: 'sync'` 处理高频事件 | 失去批处理，回调次数暴增 | 保持默认 `'pre'` 或自行节流 |
| 在 `watchEffect` 的 `await` 后读取依赖 | 该依赖不会被自动追踪 | 在 await 前读取，或改用 `watch` |
| 在异步函数中随手创建 watcher | 可能不会随组件自动停止 | 保存 stop 函数并在合适时机调用 |

## 九、面试速答

**Q：Vue 3 `watch` 的实现原理是什么？**

> Vue 会把监听源标准化为 getter，并为 getter 创建 `ReactiveEffect`。初次执行 getter 收集依赖并保存旧值；依赖改变时由 scheduler 根据 `flush` 把任务放入相应队列。任务执行后重新运行 getter，比较新旧值；需要执行时先调用上一轮 cleanup，再调用 watch 回调并更新旧值。

**Q：`watch` 和 `watchEffect` 有什么区别？**

> `watch` 显式声明数据源，能获得新旧值，默认只在数据变化后执行；`watchEffect` 自动收集同步访问的依赖，创建时立即执行，更适合不关心新旧值的简单副作用。

**Q：为什么 watch 回调里要使用 onCleanup？**

> 它用于撤销上一轮副作用，例如取消旧请求、清除计时器或断开订阅。这样可以避免竞态条件、资源泄漏和过期结果覆盖最新状态。
