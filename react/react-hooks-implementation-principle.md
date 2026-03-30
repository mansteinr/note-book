# React Hooks 实现原理与调用规则

## 目录

1. [Hooks 实现原理概述](#hooks-实现原理概述)
2. [Hook 链表的核心机制](#hook-链表的核心机制)
3. [useState 实现原理](#usestate-实现原理)
4. [useEffect 实现原理](#useeffect-实现原理)
5. [为什么 Hooks 不能在条件语句或循环中调用](#为什么-hooks-不能在条件语句或循环中调用)
6. [常见错误示例与分析](#常见错误示例与分析)
7. [React 的 Hook 调用规则](#react-的-hook-调用规则)
8. [总结](#总结)

## 一、Hooks 实现原理概述

React Hooks 是 React 16.8 引入的特性，允许函数组件拥有状态和生命周期方法。其核心实现依赖于 **Fiber 架构** 和 **Hook 链表**。

### 1.1 Fiber 架构基础

Fiber 是 React 16 引入的新架构，将渲染过程拆分为多个小任务，实现了增量渲染和优先级调度。

```text
┌─────────────────────────────────────────────────────────┐
│                      React 渲染流程                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  组件渲染 → Hook 调用 → Fiber 节点创建 → 差异比较 → DOM 更新 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Hook 系统的核心组件

- **Component Fiber**: 组件对应的 Fiber 节点，包含组件的状态和 Hook 链表
- **Hook 对象**: 存储单个 Hook 的状态、更新函数和依赖项
- **Hook 链表**: 按调用顺序连接所有 Hook 对象的单向链表

## 二、Hook 链表的核心机制

### 2.1 Hook 对象结构

每个 Hook 对应一个对象，包含以下信息：

```javascript
const hook = {
  memoizedState: currentState,    // 当前状态值
  baseState: initialState,        // 初始状态值
  baseQueue: updateQueue,         // 更新队列
  queue: {
    pending: null,                // 等待处理的更新
    dispatch: dispatchAction      // 更新函数
  },
  next: nextHook                  // 下一个 Hook 对象
};
```

### 2.2 Hook 链表的构建过程

组件渲染时，React 会按顺序调用所有 Hook，并构建 Hook 链表：

```text
组件首次渲染：
useState → 创建 Hook1 → useState → 创建 Hook2 → useEffect → 创建 Hook3 → ...
  ↑             ↑           ↑             ↑           ↑             ↑
  └─────────────┘           └─────────────┘           └─────────────┘
    链表头 ←────────────────→ 中间节点 ←────────────────→ 链表尾

组件重新渲染：
useState → 获取 Hook1 → useState → 获取 Hook2 → useEffect → 获取 Hook3 → ...
```

### 2.3 关键全局变量

React 内部使用两个关键全局变量来管理 Hook 链表：

```javascript
let currentlyRenderingFiber = null;  // 当前渲染的 Fiber 节点
let workInProgressHook = null;       // 当前处理的 Hook 对象
```

## 三、useState 实现原理

### 3.1 基本实现

```javascript
function useState(initialState) {
  // 获取当前组件的 Hook 链表
  const hook = getHook();
  
  // 首次渲染时初始化状态
  if (hook.memoizedState === undefined) {
    hook.memoizedState = typeof initialState === 'function' 
      ? initialState() 
      : initialState;
    hook.baseState = hook.memoizedState;
  }
  
  // 创建更新函数
  const dispatch = dispatchAction.bind(null, currentlyRenderingFiber, hook.queue);
  
  // 返回状态和更新函数
  return [hook.memoizedState, dispatch];
}
```

### 3.2 更新流程

```javascript
function dispatchAction(fiber, queue, action) {
  // 创建更新对象
  const update = {
    action,
    next: null
  };
  
  // 将更新添加到队列
  if (queue.pending === null) {
    update.next = update;
  } else {
    update.next = queue.pending.next;
    queue.pending.next = update;
  }
  queue.pending = update;
  
  // 调度重新渲染
  scheduleUpdateOnFiber(fiber);
}
```

## 四、useEffect 实现原理

### 4.1 基本实现

```javascript
function useEffect(create, deps) {
  // 获取当前组件的 Hook 链表
  const hook = getHook();
  
  // 保存依赖项
  const nextDeps = deps === undefined ? null : deps;
  let destroy = undefined;
  
  if (hook.memoizedState !== undefined) {
    // 重新渲染时，检查依赖项是否变化
    const prevState = hook.memoizedState;
    const prevDeps = prevState[1];
    
    // 比较依赖项
    if (nextDeps !== null && prevDeps !== null) {
      if (areHookInputsEqual(nextDeps, prevDeps)) {
        // 依赖项未变化，跳过执行
        return;
      }
    }
    
    // 依赖项变化，获取上一次的清理函数
    destroy = prevState[0];
  }
  
  // 执行副作用函数，获取清理函数
  if (create !== undefined) {
    destroy = create();
  }
  
  // 保存当前副作用和依赖项
  hook.memoizedState = [destroy, nextDeps];
  
  // 将副作用添加到 Fiber 节点的副作用队列
  currentlyRenderingFiber.updateQueue.push({
    hook,
    destroy,
    create
  });
}
```

### 4.2 依赖项比较

```javascript
function areHookInputsEqual(nextDeps, prevDeps) {
  if (prevDeps === null || nextDeps === null) {
    return false;
  }
  
  // 使用 Object.is 比较每个依赖项
  for (let i = 0; i < prevDeps.length && i < nextDeps.length; i++) {
    if (!Object.is(nextDeps[i], prevDeps[i])) {
      return false;
    }
  }
  
  return true;
}
```

## 五、为什么 Hooks 不能在条件语句或循环中调用

### 5.1 核心原因：依赖于调用顺序

React Hooks 依赖于**稳定的调用顺序**来维护 Hook 链表的正确性。每次渲染时，React 都会按相同的顺序遍历 Hook 链表：

```javascript
// 正确：稳定的调用顺序
function Component() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState('');
  
  useEffect(() => {
    // 副作用
  }, [count]);
  
  return <div>...</div>;
}
```

### 5.2 条件调用导致的问题

如果在条件语句或循环中调用 Hook，会破坏调用顺序的稳定性：

```javascript
// 错误：条件调用 Hook
function Component({ show }) {
  const [count, setCount] = useState(0);
  
  if (show) {
    const [name, setName] = useState('');  // 条件调用
  }
  
  const [age, setAge] = useState(0);
  
  return <div>...</div>;
}
```

当 `show` 为 `true` 时，Hook 调用顺序：
```
useState(0) → useState('') → useState(0)
```

当 `show` 为 `false` 时，Hook 调用顺序：
```
useState(0) → useState(0)
```

### 5.3 链表错乱的后果

调用顺序的变化会导致：

1. **状态错乱**：React 会将错误的状态值分配给错误的 Hook
2. **内存泄漏**：清理函数无法正确执行
3. **不可预测的行为**：组件状态变得不可预测
4. **渲染错误**：React 会抛出 "Rendered more hooks than during the previous render" 错误

## 六、常见错误示例与分析

### 6.1 条件语句中的 Hook

```javascript
// 错误示例
function Counter({ show }) {
  const [count, setCount] = useState(0);
  
  if (show) {
    const [doubleCount, setDoubleCount] = useState(count * 2);  // ❌ 条件调用
    
    useEffect(() => {
      setDoubleCount(count * 2);
    }, [count]);
  }
  
  return (
    <div>
      <p>Count: {count}</p>
      {show && <p>Double Count: {doubleCount}</p>}  // ❌ doubleCount 可能未定义
      <button onClick={() => setCount(count + 1)}>增加</button>
    </div>
  );
}
```

**问题分析**：
- 当 `show` 从 `true` 变为 `false` 时，Hook 调用顺序改变
- React 会将 `age` Hook 的状态错误地分配给原本的 `doubleCount` Hook

**解决方案**：将条件逻辑移到 Hook 内部或 JSX 中

```javascript
// 正确示例
function Counter({ show }) {
  const [count, setCount] = useState(0);
  const [doubleCount, setDoubleCount] = useState(count * 2);  // ✅ 始终调用
  
  useEffect(() => {
    if (show) {  // ✅ 条件在 Hook 内部
      setDoubleCount(count * 2);
    }
  }, [count, show]);
  
  return (
    <div>
      <p>Count: {count}</p>
      {show && <p>Double Count: {doubleCount}</p>}  // ✅ 条件渲染
      <button onClick={() => setCount(count + 1)}>增加</button>
    </div>
  );
}
```

### 6.2 循环中的 Hook

```javascript
// 错误示例
function TodoList({ todos }) {
  todos.forEach((todo) => {
    const [isEditing, setIsEditing] = useState(false);  // ❌ 循环中调用
    
    useEffect(() => {
      // 副作用
    }, [todo.id]);
  });
  
  return <div>...</div>;
}
```

**问题分析**：
- Hook 调用次数取决于 `todos` 数组的长度
- 当数组长度变化时，调用顺序和数量都会改变

**解决方案**：将 Hook 逻辑封装到子组件中

```javascript
// 正确示例
function TodoItem({ todo }) {
  const [isEditing, setIsEditing] = useState(false);  // ✅ 子组件中调用
  
  useEffect(() => {
    // 副作用
  }, [todo.id]);
  
  return <div>...</div>;
}

function TodoList({ todos }) {
  return (
    <div>
      {todos.map(todo => (
        <TodoItem key={todo.id} todo={todo} />  // ✅ 循环渲染组件
      ))}
    </div>
  );
}
```

### 6.3 嵌套函数中的 Hook

```javascript
// 错误示例
function Component() {
  const [count, setCount] = useState(0);
  
  function handleClick() {
    const [message, setMessage] = useState('');  // ❌ 嵌套函数中调用
  }
  
  return <button onClick={handleClick}>点击</button>;
}
```

**问题分析**：
- Hook 仅在函数调用时执行，而不是组件渲染时
- React 无法追踪这些 Hook

**解决方案**：将状态提升到组件顶层

```javascript
// 正确示例
function Component() {
  const [count, setCount] = useState(0);
  const [message, setMessage] = useState('');  // ✅ 组件顶层调用
  
  function handleClick() {
    setMessage('点击了按钮');
  }
  
  return (
    <div>
      <button onClick={handleClick}>点击</button>
      {message && <p>{message}</p>}
    </div>
  );
}
```

## 七、React 的 Hook 调用规则

React 官方定义了两条 Hook 调用规则：

### 7.1 只在顶层调用 Hook

✅ **正确**：在组件顶层调用 Hook

```javascript
function Component() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState('');
  
  useEffect(() => {
    // 副作用
  }, [count]);
  
  return <div>...</div>;
}
```

❌ **错误**：在条件语句、循环或嵌套函数中调用 Hook

```javascript
function Component({ show }) {
  if (show) {
    const [name, setName] = useState('');  // ❌ 条件语句中
  }
  
  for (let i = 0; i < 3; i++) {
    const [value, setValue] = useState(i);  // ❌ 循环中
  }
  
  function nested() {
    const [state, setState] = useState(0);  // ❌ 嵌套函数中
  }
  
  return <div>...</div>;
}
```

### 7.2 只在 React 函数组件或自定义 Hook 中调用 Hook

✅ **正确**：在函数组件中调用

```javascript
function MyComponent() {
  const [count, setCount] = useState(0);
  return <div>{count}</div>;
}
```

✅ **正确**：在自定义 Hook 中调用

```javascript
function useCounter(initialValue) {
  const [count, setCount] = useState(initialValue);
  const increment = () => setCount(count + 1);
  return [count, increment];
}
```

❌ **错误**：在普通 JavaScript 函数中调用

```javascript
function regularFunction() {
  const [count, setCount] = useState(0);  // ❌ 普通函数中
}
```

## 八、总结

### 8.1 Hooks 实现原理要点

1. **Fiber 架构**：React 渲染的基础架构，支持增量渲染
2. **Hook 链表**：按调用顺序存储所有 Hook 对象的单向链表
3. **状态管理**：每个 Hook 独立管理自己的状态和更新队列
4. **依赖比较**：使用 Object.is 比较依赖项，决定是否重新执行副作用

### 8.2 不能在条件语句或循环中调用的原因

1. **依赖顺序**：Hooks 依赖稳定的调用顺序来维护链表结构
2. **状态错乱**：条件调用会导致状态与 Hook 不匹配
3. **内存泄漏**：清理函数无法正确执行
4. **不可预测性**：组件行为变得不可预测

### 8.3 最佳实践

1. **始终在组件顶层调用 Hook**
2. **保持 Hook 调用顺序稳定**
3. **将条件逻辑移到 Hook 内部**
4. **使用自定义 Hook 封装复杂逻辑**
5. **使用 ESLint 插件自动检查**（`eslint-plugin-react-hooks`）

---

© 2026 React Hooks 实现原理与调用规则指南