# Vue 3 `computed` 实现原理与实践指南

> `computed` 的本质是一个**带缓存的派生状态**：依赖未变化时重复读取不重新计算；依赖变化后不会立即求值，而是先标记为“脏”，下次读取时再重新计算。

## 目录

- [一、computed 解决什么问题](#一computed-解决什么问题)
- [二、核心机制](#二核心机制)
- [三、简化实现](#三简化实现)
- [四、只读与可写 computed](#四只读与可写-computed)
- [五、computed、method 与 watch 的区别](#五computedmethod-与-watch-的区别)
- [六、常见误区](#六常见误区)
- [七、面试速答](#七面试速答)

---

## 一、computed 解决什么问题

当一个值可以由其他响应式数据推导出来时，应优先表达为计算属性：

```vue
<script setup>
import { computed, ref } from 'vue';

const price = ref(100);
const count = ref(2);

const total = computed(() => price.value * count.value);
</script>
```

`total` 不保存独立业务状态，它是 `price` 和 `count` 的派生结果。相比在多个地方手动同步 `total`，这种写法更可靠。

### 它与普通函数的关键差异

```javascript
const totalByMethod = () => price.value * count.value;
const totalByComputed = computed(() => price.value * count.value);
```

- 调用 `totalByMethod()` 时，每次都会执行函数；
- 读取 `totalByComputed.value` 时，若依赖没有变化，直接返回上一次的缓存结果。

## 二、核心机制

### 2.1 依赖收集

`computed` 内部会创建一个响应式副作用（effect）。首次读取 `.value` 并执行 getter 时，getter 中访问到的响应式数据会收集这个 effect 作为依赖。

```text
读取 total.value
  → 执行 getter：price.value * count.value
  → price、count 记录“total 的 effect 依赖我”
  → 缓存计算结果
```

### 2.2 缓存与脏标记

计算属性并不是依赖一变化就立即重算，而是采用**惰性求值**：

```text
price 改变
  → 通知 computed 的 effect
  → 将 computed 标记为 dirty（缓存失效）
  → 不立即运行 getter

下次读取 total.value
  → dirty 为 true
  → 执行 getter，更新缓存并清除 dirty 标记
```

这种设计避免了“依赖连续变化，但中间结果从未被读取”时的无效计算。

### 2.3 computed 本身也可以被依赖

```javascript
const subtotal = computed(() => price.value * count.value);
const total = computed(() => subtotal.value * 1.06);
```

当模板或另一个 `computed` 读取 `subtotal.value` 时，会将自身的 effect 订阅到 `subtotal`。因此依赖更新的传播链是：

```text
price / count → subtotal 失效 → total 失效 → 组件重新渲染
```

## 三、简化实现

下面的代码仅用于理解；真实 Vue 还处理了版本、嵌套 effect、调度和异常等边界情况。

```javascript
class SimpleComputedRef {
  constructor(getter, setter = undefined) {
    this.getter = getter;
    this.setter = setter;
    this._value = undefined;
    this._dirty = true;

    this.effect = new ReactiveEffect(getter, () => {
      // 依赖变化：只让缓存失效，并通知使用该 computed 的消费者
      if (!this._dirty) {
        this._dirty = true;
        triggerRefValue(this);
      }
    });
  }

  get value() {
    // 让外层组件 effect / computed effect 订阅当前 computed
    trackRefValue(this);

    if (this._dirty) {
      this._dirty = false;
      this._value = this.effect.run();
    }
    return this._value;
  }

  set value(newValue) {
    if (this.setter) {
      this.setter(newValue);
    } else {
      console.warn('Write operation failed: computed value is readonly');
    }
  }
}

function simpleComputed(getterOrOptions) {
  const getter = typeof getterOrOptions === 'function'
    ? getterOrOptions
    : getterOrOptions.get;
  const setter = typeof getterOrOptions === 'function'
    ? undefined
    : getterOrOptions.set;

  return new SimpleComputedRef(getter, setter);
}
```

核心点只有三个：

1. 第一次读取时执行 getter 并缓存结果；
2. 依赖变化时仅设置 `_dirty = true`；
3. 下一次读取时才重新执行 getter。

## 四、只读与可写 computed

### 4.1 只读 computed

传入 getter 函数时，返回的计算属性是只读的：

```javascript
const fullName = computed(() => `${firstName.value} ${lastName.value}`);

fullName.value = 'Ada Lovelace'; // 开发环境会警告
```

### 4.2 可写 computed

传入 `{ get, set }` 时，可以把赋值转换为对源状态的更新：

```javascript
const fullName = computed({
  get() {
    return `${firstName.value} ${lastName.value}`;
  },
  set(value) {
    const [first = '', last = ''] = value.trim().split(/\s+/, 2);
    firstName.value = first;
    lastName.value = last;
  }
});

fullName.value = 'Ada Lovelace';
```

可写 `computed` 不是让派生值拥有独立状态；`set` 必须把新值转换回可追踪的源状态。

## 五、computed、method 与 watch 的区别

| 场景 | 推荐 | 原因 |
| --- | --- | --- |
| 从已有状态同步推导一个值 | `computed` | 声明式、可缓存、自动追踪依赖 |
| 每次调用都要重新执行，或需要参数 | method / 普通函数 | 不应依赖缓存，函数可接收参数 |
| 数据变化后执行异步请求、写缓存、操作 DOM | `watch` / `watchEffect` | 这是副作用，不应放进 computed getter |

```javascript
// ✅ 纯派生状态
const visibleTodos = computed(() => todos.value.filter(todo => !todo.done));

// ✅ 副作用：查询条件变化后请求接口
watch(keyword, async (value) => {
  results.value = await search(value);
});

// ❌ getter 内部产生副作用
const bad = computed(() => {
  fetch('/api/report');
  return source.value;
});
```

## 六、常见误区

| 误区 | 问题 | 建议 |
| --- | --- | --- |
| 在 getter 中请求接口、修改状态 | getter 可能被多次读取，副作用难以预测 | 使用 `watch` 或事件函数 |
| 返回对象后直接修改它 | 可能绕过源状态，造成状态来源混乱 | 修改源 `ref/reactive`，让 computed 自然更新 |
| 以为计算属性会“主动更新” | 它是惰性的，只有被读取才重新求值 | 用模板、watch 或业务读取触发消费 |
| 用 computed 替代所有函数 | 有参数的计算或一次性操作并不适合缓存 | 按是否是派生状态选择 API |
| 在数组循环里创建大量 computed | 增加 effect 与依赖管理成本 | 先评估是否真的需要细粒度缓存 |

## 七、面试速答

**Q：Vue 3 `computed` 的原理是什么？**

> `computed` 内部维护一个 lazy effect、缓存值和脏标记。首次读取 `.value` 时执行 getter 并收集依赖；依赖变化时调度器只把它标记为脏并通知依赖它的 effect，不立即重新计算；下一次读取 `.value` 时再执行 getter 更新缓存。因此它同时具备依赖追踪、惰性求值和缓存复用。

**Q：为什么 computed 的 getter 必须保持纯粹？**

> getter 的职责是从状态推导值，它可能在渲染或其他计算过程中被多次读取。若在其中发请求、修改状态或操作 DOM，会造成重复副作用、循环更新和难以调试的行为。副作用应放到 `watch`、生命周期钩子或显式事件函数中。

**Q：computed 和 watch 怎么选？**

> 需要一个“由其他状态计算出来的值”时用 computed；需要“数据变化后做某件事”时用 watch。前者用于声明派生状态，后者用于处理副作用。
