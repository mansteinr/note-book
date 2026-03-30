# React Fiber 架构详解

## 目录

1. [什么是 React Fiber？](#什么是-react-fiber)
2. [为什么需要 Fiber 架构？](#为什么需要-fiber-架构)
3. [Fiber 节点的数据结构](#fiber-节点的数据结构)
4. [Fiber 架构的核心特性](#fiber-架构的核心特性)
5. [Fiber 的协调过程](#fiber-的协调过程)
6. [Fiber 与并发渲染](#fiber-与并发渲染)
7. [Fiber 对开发者的影响](#fiber-对开发者的影响)
8. [Fiber 的性能优化](#fiber-的性能优化)
9. [总结](#总结)

## 一、什么是 React Fiber？

### 1.1 Fiber 的定义

React Fiber 是 React 16 引入的**全新的协调引擎（Reconciliation Engine）**，它彻底重写了 React 的核心渲染算法。Fiber 不是一个新的 API 或功能，而是 React 内部架构的底层重构。

```text
┌─────────────────────────────────────────────────────────┐
│                 React 架构演进                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  React 15 及之前：                                      │
│  ┌─────────────────────────────────────────┐            │
│  │          Stack Reconciler               │            │
│  │  (基于递归调用栈，不可中断)               │            │
│  └─────────────────────────────────────────┘            │
│                                                         │
│  React 16 及之后：                                      │
│  ┌─────────────────────────────────────────┐            │
│  │          Fiber Reconciler               │            │
│  │  (基于链表结构，可中断、可恢复)           │            │
│  └─────────────────────────────────────────┘            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Fiber 的核心概念

**Fiber**（纤维）这个名字来源于其设计理念：将渲染工作分解为**最小的工作单元**，就像纤维一样细密而有序。

每个 Fiber 节点代表：
1. **一个 React 元素**（组件、DOM 节点等）
2. **一个工作单元**（可独立调度和执行）
3. **一个状态容器**（存储组件的状态和副作用）

```javascript
// Fiber 节点的简化表示
class FiberNode {
  constructor(type, props) {
    // 标识信息
    this.tag = type;           // 组件类型（函数组件、类组件、DOM节点等）
    this.type = type;          // 组件函数或DOM标签名
    this.key = props.key;      // 唯一标识符
    
    // 状态信息
    this.stateNode = null;     // 组件实例或DOM节点
    this.memoizedProps = props;// 记忆的props
    this.memoizedState = null; // 记忆的state
    this.updateQueue = null;   // 更新队列
    
    // 链表结构
    this.return = null;        // 父节点
    this.child = null;         // 第一个子节点
    this.sibling = null;       // 兄弟节点
    this.index = 0;            // 在同级中的索引
    
    // 副作用信息
    this.flags = 0;            // 需要执行的副作用类型
    this.subtreeFlags = 0;     // 子树中的副作用
    
    // 工作进度
    this.alternate = null;     // 上一次渲染的Fiber（用于双缓存）
    this.lanes = 0;            // 优先级车道
  }
}
```

## 二、为什么需要 Fiber 架构？

### 2.1 传统 Stack Reconciler 的局限性

在 React 15 及之前，React 使用**基于递归调用栈的协调器**：

```javascript
// 伪代码：传统的递归协调过程
function reconcile(component) {
  // 1. 调用组件的render方法
  const children = component.render();
  
  // 2. 递归处理所有子组件
  children.forEach(child => {
    reconcile(child); // 递归调用，无法中断
  });
  
  // 3. 更新DOM
  updateDOM(component);
}
```

**传统架构的问题**：

1. **不可中断性**：递归调用一旦开始就无法中断
2. **阻塞主线程**：大型组件树渲染时会长时间占用主线程
3. **无法响应高优先级任务**：用户交互会被阻塞
4. **缺乏优先级调度**：所有更新都是同步的

### 2.2 现实场景中的问题

```javascript
// 示例：大型数据列表的渲染阻塞
function LargeList() {
  const [items, setItems] = useState([]);
  
  useEffect(() => {
    // 加载大量数据
    fetch('/api/large-data')
      .then(res => res.json())
      .then(data => {
        setItems(data); // 触发大规模渲染，可能阻塞UI
      });
  }, []);
  
  return (
    <div>
      {/* 用户输入被阻塞 */}
      <SearchInput />
      
      {/* 渲染1000个列表项，耗时200ms+ */}
      {items.map(item => (
        <ListItem key={item.id} data={item} />
      ))}
    </div>
  );
}
```

### 2.3 Fiber 架构的解决方案

Fiber 架构通过以下方式解决传统架构的问题：

1. **将递归改为循环**：使用链表遍历代替递归调用栈
2. **引入工作单元**：将渲染分解为可独立调度的单元
3. **支持中断和恢复**：可以在任意点暂停和继续渲染
4. **优先级调度**：不同任务可以有不同的优先级

```text
┌─────────────────────────────────────────────────────────┐
│           传统递归 vs Fiber 链表遍历                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  传统递归：                                             │
│  reconcile(A)                                          │
│    ↓ reconcile(A.child1)                               │
│        ↓ reconcile(A.child1.child1)                    │
│            ↓ reconcile(A.child1.child1.child1)         │
│                ... (无法中断)                           │
│                                                         │
│  Fiber遍历：                                            │
│  workInProgress = rootFiber                            │
│  while (workInProgress) {                              │
│    performUnitOfWork(workInProgress)                   │
│    if (shouldYield()) { // 检查是否需要中断             │
│      break; // 可以中断！                               │
│    }                                                    │
│    workInProgress = getNextFiber(workInProgress)       │
│  }                                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 三、Fiber 节点的数据结构

### 3.1 完整的 Fiber 节点结构

```javascript
// React 内部实际的 Fiber 节点结构（简化版）
const FiberNode = {
  // === 标识信息 ===
  tag: WorkTag,              // 组件类型（0-24）
  key: null | string,        // 唯一标识
  elementType: any,          // 原始类型
  type: any,                 // 解析后的类型
  
  // === 状态信息 ===
  stateNode: any,            // 实例（组件实例/DOM节点）
  memoizedProps: any,        // 上次渲染的props
  memoizedState: any,        // 上次渲染的state
  dependencies: null | DependenciesLane, // 依赖项
  updateQueue: null | UpdateQueue,      // 更新队列
  
  // === 链表结构 ===
  return: null | FiberNode,  // 父节点
  child: null | FiberNode,   // 第一个子节点
  sibling: null | FiberNode, // 兄弟节点
  index: number,             // 在同级中的位置
  
  // === 副作用信息 ===
  flags: Flags,              // 当前节点的副作用
  subtreeFlags: Flags,       // 子树的副作用
  deletions: null | Array<FiberNode>, // 待删除的节点
  
  // === 工作进度 ===
  lanes: Lanes,              // 优先级车道
  childLanes: Lanes,         // 子节点的优先级
  alternate: null | FiberNode, // 上一次渲染的Fiber
  
  // === 其他 ===
  mode: TypeOfMode,          // 渲染模式（ConcurrentMode等）
  pendingProps: any,         // 新的props（等待处理）
  ref: null | RefObject,     // ref引用
  actualDuration?: number,   // 实际渲染时间（开发模式）
  actualStartTime?: number,  // 实际开始时间（开发模式）
  selfBaseDuration?: number, // 自身基础渲染时间
  treeBaseDuration?: number, // 整棵树的基础渲染时间
};
```

### 3.2 Fiber 节点类型（WorkTag）

React 内部定义了多种 Fiber 节点类型：

```javascript
// ReactWorkTags.js 中的定义（简化）
export const FunctionComponent = 0;     // 函数组件
export const ClassComponent = 1;        // 类组件
export const IndeterminateComponent = 2;// 尚未确定的组件
export const HostRoot = 3;              // 根节点
export const HostPortal = 4;            // Portal
export const HostComponent = 5;         // DOM节点（div、span等）
export const HostText = 6;              // 文本节点
export const Fragment = 7;              // Fragment
export const Mode = 8;                  // StrictMode
export const ContextConsumer = 9;       // Context.Consumer
export const ContextProvider = 10;      // Context.Provider
export const ForwardRef = 11;           // ForwardRef
export const Profiler = 12;             // Profiler
export const SuspenseComponent = 13;    // Suspense
export const MemoComponent = 14;        // React.memo
export const SimpleMemoComponent = 15;  // 简单memo组件
export const LazyComponent = 16;        // React.lazy
export const IncompleteClassComponent = 17; // 未完成的类组件
export const DehydratedFragment = 18;   // 脱水片段（SSR）
export const SuspenseListComponent = 19;// SuspenseList
export const ScopeComponent = 21;       // Scope
export const OffscreenComponent = 22;   // Offscreen
export const LegacyHiddenComponent = 23;// LegacyHidden
export const CacheComponent = 24;       // Cache
```

### 3.3 双缓存机制

Fiber 使用**双缓存（Double Buffering）** 技术来管理当前和上一次的渲染状态：

```javascript
// 双缓存示意图
let current = null;    // 当前显示在屏幕上的Fiber树
let workInProgress = null; // 正在构建的新的Fiber树

function beginWork(current, workInProgress) {
  // 使用alternate指针连接两棵树
  if (workInProgress.alternate === null) {
    // 第一次渲染，创建新的Fiber节点
    workInProgress.alternate = {
      ...workInProgress,
      alternate: workInProgress
    };
  } else {
    // 更新渲染，复用之前的Fiber节点
    workInProgress = workInProgress.alternate;
  }
  
  return workInProgress;
}

function completeWork(current, workInProgress) {
  // 完成工作后，交换两棵树
  const finishedWork = workInProgress;
  
  // 提交阶段后，新的树成为当前树
  current = finishedWork;
  workInProgress = null;
}
```

## 四、Fiber 架构的核心特性

### 4.1 可中断性（Interruptibility）

Fiber 的核心特性是**渲染过程可以被中断**，让高优先级任务（如用户输入）优先执行：

```javascript
// 伪代码：可中断的渲染循环
function workLoopConcurrent() {
  // 检查是否有高优先级任务
  while (workInProgress !== null && !shouldYieldToRenderer()) {
    performUnitOfWork(workInProgress);
  }
  
  // 如果被中断，返回true表示还有工作要做
  if (workInProgress !== null) {
    return true;
  }
  
  return false; // 所有工作完成
}

function shouldYieldToRenderer() {
  // 检查是否需要让出主线程
  // 1. 是否有更高优先级的任务
  // 2. 是否超过了时间片（通常是5ms）
  // 3. 浏览器是否需要重绘
  return (
    hasHigherPriorityWork() ||
    exceededTimeSlice() ||
    browserNeedsRepaint()
  );
}
```

### 4.2 可恢复性（Resumability）

被中断的渲染可以在之后**从断点处恢复**：

```javascript
// 伪代码：恢复渲染
let nextUnitOfWork = null;

function performUnitOfWork(fiber) {
  // 1. 开始处理当前Fiber
  beginWork(fiber);
  
  // 2. 如果有子节点，处理子节点
  if (fiber.child) {
    return fiber.child;
  }
  
  // 3. 处理兄弟节点
  let nextFiber = fiber;
  while (nextFiber) {
    completeWork(nextFiber);
    
    if (nextFiber.sibling) {
      return nextFiber.sibling;
    }
    
    // 4. 回到父节点
    nextFiber = nextFiber.return;
  }
  
  return null;
}

// 中断后恢复
function resumeWork() {
  // 从上次中断的地方继续
  if (nextUnitOfWork) {
    workInProgress = nextUnitOfWork;
    workLoopConcurrent();
  }
}
```

### 4.3 优先级调度（Priority-based Scheduling）

Fiber 引入了**优先级系统**来管理不同任务的执行顺序：

```javascript
// 优先级常量（简化版）
export const NoLane = 0b0000000000000000000000000000000;
export const SyncLane = 0b0000000000000000000000000000001;     // 同步任务
export const InputContinuousLane = 0b0000000000000000000000000000100; // 连续输入
export const DefaultLane = 0b0000000000000000000000000010000;  // 默认更新
export const TransitionLane = 0b0000000000000000000100000000000; // 过渡更新
export const IdleLane = 0b1000000000000000000000000000000;     // 空闲时执行

// 根据事件类型分配优先级
function getEventPriority(domEventName) {
  switch (domEventName) {
    case 'click':
    case 'keydown':
    case 'keyup':
      return DiscreteEventPriority; // 离散事件，高优先级
    
    case 'mousemove':
    case 'scroll':
      return ContinuousEventPriority; // 连续事件，中优先级
    
    default:
      return DefaultEventPriority; // 默认优先级
  }
}
```

### 4.4 增量渲染（Incremental Rendering）

Fiber 支持**增量渲染**，将大型更新分解为多个小批次：

```javascript
// 增量渲染示例
function renderIncrementally(rootFiber) {
  const chunkSize = 10; // 每批处理10个节点
  let processed = 0;
  
  function processChunk() {
    let count = 0;
    while (workInProgress && count < chunkSize) {
      performUnitOfWork(workInProgress);
      count++;
      processed++;
    }
    
    if (workInProgress) {
      // 还有更多工作，安排下一批
      requestIdleCallback(processChunk);
    } else {
      // 所有工作完成，提交更新
      commitRoot();
    }
  }
  
  // 开始第一批处理
  processChunk();
}
```

## 五、Fiber 的协调过程

### 5.1 协调的两个阶段

Fiber 的协调过程分为两个清晰的阶段：

**第一阶段：渲染阶段（Render Phase）**
- 可中断、可恢复
- 在内存中计算变更
- 无副作用，可安全中断

**第二阶段：提交阶段（Commit Phase）**
- 不可中断
- 一次性应用所有变更
- 确保 UI 一致性

```javascript
// Fiber 协调的完整流程
function updateContainer(element, container) {
  // 1. 创建更新任务
  const update = createUpdate();
  update.payload = { element };
  
  // 2. 将更新加入队列
  enqueueUpdate(container.current, update);
  
  // 3. 开始调度
  scheduleUpdateOnFiber(container.current);
}

function scheduleUpdateOnFiber(fiber) {
  // 4. 标记需要更新的节点
  markUpdateLaneFromFiberToRoot(fiber);
  
  // 5. 确保调度器运行
  ensureRootIsScheduled(root);
}

function performConcurrentWorkOnRoot(root) {
  // 6. 渲染阶段（可中断）
  renderRootSync(root);
  
  // 7. 提交阶段（不可中断）
  commitRoot(root);
}
```

### 5.2 渲染阶段详解

渲染阶段负责**计算变更**，但不修改 DOM：

```javascript
function renderRootSync(root) {
  // 准备新的工作树
  prepareFreshStack(root);
  
  // 开始工作循环
  workLoopSync();
  
  // 标记工作完成
  root.finishedWork = root.current.alternate;
}

function workLoopSync() {
  while (workInProgress !== null) {
    performUnitOfWork(workInProgress);
  }
}

function performUnitOfWork(unitOfWork) {
  const current = unitOfWork.alternate;
  
  // 开始处理当前节点
  let next = beginWork(current, unitOfWork);
  
  // 更新 memoizedProps
  unitOfWork.memoizedProps = unitOfWork.pendingProps;
  
  if (next === null) {
    // 没有子节点，完成当前节点
    completeUnitOfWork(unitOfWork);
  } else {
    // 继续处理子节点
    workInProgress = next;
  }
}
```

### 5.3 提交阶段详解

提交阶段负责**应用变更**到 DOM：

```javascript
function commitRoot(root) {
  const finishedWork = root.finishedWork;
  
  if (finishedWork === null) {
    return;
  }
  
  // 提交分为三个子阶段
  commitBeforeMutationEffects();
  commitMutationEffects();
  commitLayoutEffects();
  
  // 交换当前树和工作树
  root.current = finishedWork;
}

function commitMutationEffects() {
  // 实际修改DOM
  commitMutationEffectsOnFiber(finishedWork);
  
  // 处理删除的节点
  commitDeletionEffects();
}

function commitLayoutEffects() {
  // 执行生命周期方法和ref回调
  commitLayoutEffectOnFiber(finishedWork);
  
  // 执行useLayoutEffect
  commitHookEffectListMount();
}
```

## 六、Fiber 与并发渲染

### 6.1 并发模式的基础

Fiber 架构为并发渲染提供了基础：

```javascript
// 启用并发模式
const root = ReactDOM.createRoot(
  document.getElementById('root'),
  {
    // 并发特性配置
    unstable_concurrentUpdatesByDefault: true,
  }
);

root.render(<App />);
```

### 6.2 时间切片（Time Slicing）

Fiber 通过时间切片实现并发：

```javascript
// 时间切片实现
function shouldYield() {
  // 检查是否超过了5ms的时间预算
  const elapsedTime = performance.now() - startTime;
  return elapsedTime > 5; // 5ms时间片
}

function workLoopConcurrent() {
  while (workInProgress !== null && !shouldYield()) {
    performUnitOfWork(workInProgress);
  }
  
  // 如果被中断，返回true
  return workInProgress !== null;
}
```

### 6.3 并发特性 API

基于 Fiber 的并发特性，React 提供了新的 API：

```javascript
import { useState, useTransition, useDeferredValue } from 'react';

function SearchComponent() {
  const [query, setQuery] = useState('');
  const deferredQuery = useDeferredValue(query);
  const [isPending, startTransition] = useTransition();
  
  const handleChange = (e) => {
    const value = e.target.value;
    
    // 紧急更新：立即显示输入
    setQuery(value);
    
    // 非紧急更新：标记为可中断
    startTransition(() => {
      performSearch(value);
    });
  };
  
  return (
    <div>
      <input value={query} onChange={handleChange} />
      {isPending && <Spinner />}
      <SearchResults query={deferredQuery} />
    </div>
  );
}
```

## 七、Fiber 对开发者的影响

### 7.1 生命周期方法的变化

Fiber 引入了新的生命周期方法：

```javascript
class MyComponent extends React.Component {
  // 新的生命周期（Fiber引入）
  static getDerivedStateFromProps(props, state) {
    // 在每次渲染前调用
    return null; // 返回新的state或null
  }
  
  getSnapshotBeforeUpdate(prevProps, prevState) {
    // 在DOM更新前调用
    return snapshot;
  }
  
  // 不推荐使用的生命周期
  componentWillMount() {}    // 使用constructor或componentDidMount
  componentWillReceiveProps() {} // 使用getDerivedStateFromProps
  componentWillUpdate() {}   // 使用getSnapshotBeforeUpdate
}
```

### 7.2 错误边界（Error Boundaries）

Fiber 改进了错误处理机制：

```javascript
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  
  static getDerivedStateFromError(error) {
    // 更新state使下一次渲染显示降级UI
    return { hasError: true };
  }
  
  componentDidCatch(error, errorInfo) {
    // 记录错误信息
    logErrorToService(error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return <h1>Something went wrong.</h1>;
    }
    
    return this.props.children;
  }
}

// 使用
<ErrorBoundary>
  <MyComponent />
</ErrorBoundary>
```

### 7.3 批量更新优化

Fiber 改进了批量更新机制：

```javascript
// React 17及之前：事件处理函数中的setState是批量的
handleClick = () => {
  this.setState({ a: 1 });
  this.setState({ b: 2 });
  // 只触发一次渲染
};

// React 18及之后：所有setState默认都是批量的
setTimeout(() => {
  setState({ a: 1 });
  setState({ b: 2 });
  // 在React 18中也是批量更新
}, 1000);

// 强制同步更新（如果需要）
flushSync(() => {
  setState({ a: 1 });
});
```

## 八、Fiber 的性能优化

### 8.1 开发工具支持

React DevTools 提供了 Fiber 相关的调试功能：

```javascript
// 性能分析API
const onRender = (id, phase, actualDuration, baseDuration, startTime, commitTime) => {
  console.log(`${id} ${phase} took ${actualDuration}ms`);
};

<Profiler id="MyApp" onRender={onRender}>
  <App />
</Profiler>
```

### 8.2 性能监控指标

Fiber 提供了详细的性能数据：

```javascript
// 获取Fiber节点的性能数据
function getFiberPerformanceData(fiber) {
  return {
    actualDuration: fiber.actualDuration,     // 实际渲染时间
    treeBaseDuration: fiber.treeBaseDuration, // 整棵树的基础时间
    selfBaseDuration: fiber.selfBaseDuration, // 自身基础时间
    childCount: getChildCount(fiber),         // 子节点数量
    depth: getDepth(fiber),                   // 深度
  };
}
```

### 8.3 内存优化

Fiber 通过复用节点减少内存分配：

```javascript
// 节点复用策略
function createWorkInProgress(current, pendingProps) {
  let workInProgress = current.alternate;
  
  if (workInProgress === null) {
    // 创建新节点
    workInProgress = createFiber(
      current.tag,
      pendingProps,
      current.key,
      current.mode
    );
    workInProgress.alternate = current;
    current.alternate = workInProgress;
  } else {
    // 复用现有节点
    workInProgress.pendingProps = pendingProps;
    workInProgress.flags = NoFlags;
    workInProgress.nextEffect = null;
    workInProgress.firstEffect = null;
    workInProgress.lastEffect = null;
  }
  
  return workInProgress;
}
```

## 九、总结

### 9.1 Fiber 架构的核心价值

1. **可中断性**：渲染过程可以被高优先级任务中断
2. **可恢复性**：可以从中断点继续渲染
3. **优先级调度**：不同任务有不同的执行优先级
4. **增量渲染**：大型更新可以分解为多个小批次
5. **更好的错误处理**：引入错误边界机制

### 9.2 Fiber 带来的变革

**对 React 内部**：
- 彻底重写了协调算法
- 为并发特性奠定基础
- 改进了性能监控和调试

**对开发者**：
- 更流畅的用户体验
- 更好的错误处理机制
- 新的并发API（useTransition、useDeferredValue等）
- 改进的生命周期方法

**对用户体验**：
- 减少界面卡顿
- 提高响应速度
- 更平滑的动画和过渡

### 9.3 未来发展方向

1. **更智能的调度**：基于用户行为和设备性能的智能调度
2. **离线渲染**：更好的离线体验和同步策略
3. **跨平台统一**：React Native 的深度集成
4. **编译时优化**：React Compiler 的进一步集成

### 9.4 学习建议

1. **理解核心概念**：掌握可中断性、优先级调度等核心概念
2. **实践并发特性**：在实际项目中使用 useTransition、Suspense 等API
3. **性能监控**：使用 React DevTools 监控应用性能
4. **关注更新**：React 团队持续改进 Fiber 架构，关注最新特性

---

© 2026 React Fiber 架构详解指南