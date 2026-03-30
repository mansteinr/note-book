# React 19 并发渲染 (Concurrent Rendering) 详解

## 目录

1. [什么是并发渲染？](#什么是并发渲染)
2. [并发渲染解决的问题](#并发渲染解决的问题)
3. [Fiber 架构：并发的基础](#fiber-架构并发的基础)
4. [React 19 中的并发特性](#react-19-中的并发特性)
5. [并发渲染的核心机制](#并发渲染的核心机制)
6. [并发渲染带来的用户体验提升](#并发渲染带来的用户体验提升)
7. [并发 API 使用指南](#并发-api-使用指南)
8. [实际应用场景](#实际应用场景)
9. [总结](#总结)

## 一、什么是并发渲染？

### 1.1 并发渲染的定义

并发渲染 (Concurrent Rendering) 是 React 18 引入并在 React 19 中进一步完善的底层渲染机制。它不是指同时执行多个任务（并行），而是指 **React 能够同时处理多个更新任务，并根据优先级在这些任务之间进行智能切换**。

```text
┌─────────────────────────────────────────────────────────────┐
│                   传统渲染 vs 并发渲染                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  传统渲染：                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ 任务A   │→│ 任务B   │→│ 任务C   │→│ 任务D   │        │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
│                                                             │
│  并发渲染：                                                 │
│  ┌─────────┐  ┌─────────┐                                  │
│  │ 高优先级│←→│ 低优先级│                                  │
│  │ 任务A   │  │ 任务B   │                                  │
│  └─────────┘  └─────────┘                                  │
│        ↓            ↓                                       │
│  ┌─────────┐  ┌─────────┐                                  │
│  │ 用户输入│  │ 数据渲染│                                  │
│  │ 立即响应│  │ 可中断  │                                  │
│  └─────────┘  └─────────┘                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 并发 vs 并行

**并发**：
- 同一时间段内处理多个任务
- 任务之间可以切换和中断
- 适用于单核处理器
- 核心是任务调度和优先级管理

**并行**：
- 同一时刻执行多个任务
- 需要多核处理器支持
- 任务同时进行，互不干扰

React 的并发渲染属于**并发**，它通过智能的任务调度，让高优先级任务（如用户输入）能够打断低优先级任务（如大数据列表渲染）。

## 二、并发渲染解决的问题

### 2.1 传统渲染的瓶颈

在 React 16 之前，渲染过程是**同步且不可中断**的：

```javascript
// 传统同步渲染的问题
function SearchComponent() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  
  // 每次输入都会触发完整渲染
  const handleInput = (e) => {
    const value = e.target.value;
    setQuery(value);
    
    // 假设这是一个耗时的过滤操作
    const filtered = hugeList.filter(item => 
      item.includes(value)
    );
    setResults(filtered); // 阻塞主线程 200ms
  };
  
  return (
    <div>
      <input value={query} onChange={handleInput} />
      <LargeList items={results} /> {/* 渲染耗时 */}
    </div>
  );
}
```

**问题**：
- 用户输入被阻塞
- 页面卡顿、不流畅
- 无法响应其他交互

### 2.2 并发渲染的解决方案

并发渲染将渲染过程拆分为可中断的小任务：

```text
用户输入 "r" → 显示 "r" → 中断列表渲染 → 
用户输入 "e" → 显示 "re" → 继续列表渲染 →
用户输入 "a" → 显示 "rea" → 再次中断...
```

## 三、Fiber 架构：并发的基础

### 3.1 Fiber 节点结构

Fiber 是 React 16 引入的底层架构，为并发渲染提供了基础：

```javascript
// Fiber 节点简化结构
const fiberNode = {
  tag: FunctionComponent,        // 组件类型
  type: ComponentFunction,       // 组件函数
  stateNode: null,               // 组件实例
  return: parentFiber,           // 父 Fiber
  child: firstChildFiber,        // 第一个子 Fiber
  sibling: nextSiblingFiber,     // 兄弟 Fiber
  alternate: previousFiber,      // 上一次渲染的 Fiber
  memoizedProps: props,          // 记忆的 props
  memoizedState: state,          // 记忆的 state
  updateQueue: updates,          // 更新队列
  lanes: LanePriority,           // 优先级车道
  // ... 其他属性
};
```

### 3.2 可中断的渲染过程

Fiber 架构将渲染分为两个阶段：

**第一阶段：渲染阶段 (Render Phase)**
- 可中断、可恢复
- 在内存中计算变更
- 无副作用，可安全中断

**第二阶段：提交阶段 (Commit Phase)**
- 不可中断
- 一次性应用所有变更
- 确保 UI 一致性

```text
┌─────────────────────────────────────────────────────┐
│                Fiber 渲染流程                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  开始渲染 → 处理 Fiber1 → 检查中断 → 处理 Fiber2 → ... │
│        ↑              ↓              ↓              │
│        └────── 用户输入 ──────→ 中断渲染 → 响应输入    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## 四、React 19 中的并发特性

### 4.1 use Hook：并发数据获取

React 19 引入了 `use` Hook，支持在渲染期间读取 Promise：

```javascript
import { use, Suspense } from 'react';

// 异步数据获取
async function fetchUserData(userId) {
  const response = await fetch(`/api/users/${userId}`);
  return response.json();
}

function UserProfile({ userId }) {
  // 在渲染中直接使用 Promise
  const userData = use(fetchUserData(userId));
  
  return (
    <div>
      <h1>{userData.name}</h1>
      <p>{userData.email}</p>
    </div>
  );
}

function App() {
  return (
    <Suspense fallback={<div>Loading user...</div>}>
      <UserProfile userId="123" />
    </Suspense>
  );
}
```

### 4.2 useTransition：标记非紧急更新

```javascript
import { useState, useTransition } from 'react';

function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isPending, startTransition] = useTransition();
  
  const handleSearch = (newQuery) => {
    // 紧急更新：立即显示用户输入
    setQuery(newQuery);
    
    // 非紧急更新：标记为可中断
    startTransition(() => {
      const filtered = filterLargeDataset(newQuery);
      setResults(filtered);
    });
  };
  
  return (
    <div>
      <input 
        value={query} 
        onChange={(e) => handleSearch(e.target.value)}
      />
      {isPending && <div>Searching...</div>}
      <SearchResults results={results} />
    </div>
  );
}
```

### 4.3 useOptimistic：乐观更新

```javascript
import { useOptimistic } from 'react';

function LikeButton({ postId, initialLikes }) {
  const [likes, addLike] = useOptimistic(
    initialLikes,
    (currentLikes, newLike) => currentLikes + 1
  );
  
  const handleClick = async () => {
    // 立即更新 UI（乐观）
    addLike();
    
    try {
      // 发送请求到服务器
      await fetch(`/api/posts/${postId}/like`, {
        method: 'POST'
      });
    } catch (error) {
      // 如果失败，React 会自动回滚
      console.error('Like failed:', error);
    }
  };
  
  return (
    <button onClick={handleClick}>
      👍 {likes}
    </button>
  );
}
```

## 五、并发渲染的核心机制

### 5.1 Lane 模型：优先级管理

React 使用 Lane（车道）模型来管理任务优先级：

```javascript
// 优先级常量（简化版）
const SyncLane = 0b0000000000000000000000000000001;
const InputContinuousLane = 0b0000000000000000000000000000100;
const DefaultLane = 0b0000000000000000000000000010000;
const TransitionLane = 0b0000000000000000000100000000000;
const IdleLane = 0b1000000000000000000000000000000;

// 任务分配
const update = {
  payload: newState,
  lane: isUserInput ? InputContinuousLane : TransitionLane,
  next: null
};
```

### 5.2 时间切片 (Time Slicing)

React 将渲染工作分成 5ms 的时间片：

```javascript
// 伪代码：时间切片调度
function workLoopConcurrent() {
  while (workInProgress !== null && !shouldYield()) {
    performUnitOfWork(workInProgress);
  }
  
  // 检查是否需要让出主线程
  if (workInProgress !== null) {
    // 还有工作，但时间片用完了
    return true; // 需要继续
  }
  
  return false; // 工作完成
}

function shouldYield() {
  // 检查是否超过了 5ms 的时间预算
  return performance.now() - startTime > 5;
}
```

### 5.3 可中断的协调过程

```text
┌─────────────────────────────────────────────────────────┐
│                   可中断协调流程                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  开始协调 → 处理组件A → 检查中断 → 处理组件B → 检查中断 → ... │
│        │          │          │          │          │    │
│        ▼          ▼          ▼          ▼          ▼    │
│      Fiber1    Fiber2    用户输入!  继续Fiber2   Fiber3  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 六、并发渲染带来的用户体验提升

### 6.1 即时响应性

**传统渲染**：
- 用户输入 → 等待渲染完成 → 显示结果
- 有明显的延迟感

**并发渲染**：
- 用户输入 → 立即显示 → 后台渲染
- 感觉即时响应

```javascript
// 并发渲染下的搜索体验
function ConcurrentSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isPending, startTransition] = useTransition();
  
  return (
    <div>
      {/* 输入框始终响应迅速 */}
      <input 
        value={query}
        onChange={(e) => {
          setQuery(e.target.value); // 立即更新
          startTransition(() => {
            // 后台处理，不阻塞输入
            setResults(searchAPI(e.target.value));
          });
        }}
      />
      
      {/* 显示加载状态 */}
      {isPending && <Spinner />}
      
      {/* 结果逐步显示 */}
      <ResultsList items={results} />
    </div>
  );
}
```

### 6.2 流畅的过渡动画

```javascript
function TabContainer() {
  const [activeTab, setActiveTab] = useState('home');
  const [isPending, startTransition] = useTransition();
  
  const handleTabChange = (tab) => {
    startTransition(() => {
      setActiveTab(tab);
    });
  };
  
  return (
    <div>
      <TabBar activeTab={activeTab} onChange={handleTabChange} />
      
      {/* 平滑过渡，无内容闪烁 */}
      <Suspense fallback={<TabSkeleton />}>
        <TabContent tab={activeTab} />
      </Suspense>
    </div>
  );
}
```

### 6.3 减少布局抖动

```javascript
// 资源预加载，避免布局抖动
function ImageWithSuspense({ src, alt }) {
  return (
    <Suspense fallback={
      <div style={{ width: '300px', height: '200px', background: '#eee' }}>
        Loading...
      </div>
    }>
      <img src={src} alt={alt} />
    </Suspense>
  );
}

// 字体加载，避免文本闪烁
function App() {
  return (
    <Suspense fallback={<div>Loading fonts...</div>}>
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Inter"
      />
      <div style={{ fontFamily: 'Inter, sans-serif' }}>
        Content with loaded font
      </div>
    </Suspense>
  );
}
```

### 6.4 智能的后台预加载

```javascript
function ProductPage({ productId }) {
  // 预加载相关数据
  const relatedProductsPromise = useMemo(
    () => fetchRelatedProducts(productId),
    [productId]
  );
  
  return (
    <div>
      <ProductDetails productId={productId} />
      
      {/* 后台预加载，用户滚动时立即显示 */}
      <Suspense fallback={<ProductGridSkeleton />}>
        <RelatedProducts promise={relatedProductsPromise} />
      </Suspense>
    </div>
  );
}
```

## 七、并发 API 使用指南

### 7.1 useTransition 最佳实践

```javascript
// ✅ 正确：用于非紧急更新
function GoodExample() {
  const [isPending, startTransition] = useTransition();
  
  const handleUpdate = (newData) => {
    // 紧急更新
    setImmediateState(newData.immediate);
    
    // 非紧急更新
    startTransition(() => {
      setHeavyState(newData.heavy);
    });
  };
  
  return (
    <div>
      <button onClick={() => handleUpdate(data)}>
        Update
      </button>
      {isPending && <LoadingIndicator />}
    </div>
  );
}

// ❌ 错误：滥用 useTransition
function BadExample() {
  const [isPending, startTransition] = useTransition();
  
  const handleClick = () => {
    // 用户点击应该是紧急的！
    startTransition(() => {
      setClicked(true); // 这会延迟响应
    });
  };
  
  return <button onClick={handleClick}>Click me</button>;
}
```

### 7.2 Suspense 数据获取模式

```javascript
// Render-as-you-fetch 模式
function UserProfileWrapper({ userId }) {
  // 在渲染前开始获取数据
  const userPromise = fetchUser(userId);
  const postsPromise = fetchUserPosts(userId);
  
  return (
    <Suspense fallback={<ProfileSkeleton />}>
      <UserProfile 
        userPromise={userPromise}
        postsPromise={postsPromise}
      />
    </Suspense>
  );
}

function UserProfile({ userPromise, postsPromise }) {
  // 在渲染中读取数据
  const user = use(userPromise);
  const posts = use(postsPromise);
  
  return (
    <div>
      <h1>{user.name}</h1>
      <PostList posts={posts} />
    </div>
  );
}
```

### 7.3 错误边界与并发

```javascript
import { ErrorBoundary } from 'react-error-boundary';

function App() {
  return (
    <ErrorBoundary
      fallback={<ErrorFallback />}
      onReset={() => window.location.reload()}
    >
      <Suspense fallback={<LoadingSpinner />}>
        <ConcurrentComponent />
      </Suspense>
    </ErrorBoundary>
  );
}

function ErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div role="alert">
      <p>Something went wrong:</p>
      <pre>{error.message}</pre>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}
```

## 八、实际应用场景

### 8.1 大型数据表格

```javascript
function DataGrid({ data }) {
  const [sortBy, setSortBy] = useState('id');
  const [filter, setFilter] = useState('');
  const [isPending, startTransition] = useTransition();
  
  const handleSort = (column) => {
    startTransition(() => {
      setSortBy(column); // 排序可能很耗时
    });
  };
  
  const handleFilter = (value) => {
    setFilter(value); // 输入立即响应
    startTransition(() => {
      // 过滤在后台进行
      applyFilter(value);
    });
  };
  
  // 虚拟滚动 + 并发渲染
  const visibleRows = useVirtualRows(data, sortBy, filter);
  
  return (
    <div>
      <SearchInput value={filter} onChange={handleFilter} />
      {isPending && <div>Updating...</div>}
      <VirtualList rows={visibleRows} onSort={handleSort} />
    </div>
  );
}
```

### 8.2 实时聊天应用

```javascript
function ChatApp() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isPending, startTransition] = useTransition();
  
  // 接收新消息（可能很频繁）
  useEffect(() => {
    const socket = new WebSocket('ws://chat.example.com');
    
    socket.onmessage = (event) => {
      const newMessage = JSON.parse(event.data);
      
      startTransition(() => {
        setMessages(prev => [...prev, newMessage]);
      });
    };
    
    return () => socket.close();
  }, []);
  
  const sendMessage = () => {
    const message = { text: input, timestamp: Date.now() };
    
    // 乐观更新
    setMessages(prev => [...prev, { ...message, pending: true }]);
    setInput('');
    
    // 发送到服务器
    sendToServer(message).then(() => {
      // 服务器确认后更新状态
      setMessages(prev => 
        prev.map(msg => 
          msg.timestamp === message.timestamp 
            ? { ...msg, pending: false }
            : msg
        )
      );
    });
  };
  
  return (
    <div>
      <MessageList messages={messages} />
      <MessageInput 
        value={input}
        onChange={setInput}
        onSend={sendMessage}
      />
      {isPending && <div>Receiving new messages...</div>}
    </div>
  );
}
```

### 8.3 仪表盘应用

```javascript
function Dashboard() {
  const [dateRange, setDateRange] = useState('today');
  const [isPending, startTransition] = useTransition();
  
  const handleDateChange = (range) => {
    startTransition(() => {
      setDateRange(range);
    });
  };
  
  return (
    <div>
      <DateRangeSelector value={dateRange} onChange={handleDateChange} />
      
      {isPending ? (
        <DashboardSkeleton />
      ) : (
        <div className="dashboard-grid">
          <Suspense fallback={<MetricCardSkeleton />}>
            <RevenueChart dateRange={dateRange} />
          </Suspense>
          
          <Suspense fallback={<MetricCardSkeleton />}>
            <UserMetrics dateRange={dateRange} />
          </Suspense>
          
          <Suspense fallback={<MetricCardSkeleton />}>
            <ConversionRate dateRange={dateRange} />
          </Suspense>
        </div>
      )}
    </div>
  );
}
```

## 九、总结

### 9.1 并发渲染的核心价值

1. **响应性**：用户交互始终优先，无阻塞感
2. **流畅性**：动画和过渡更加平滑
3. **可预测性**：复杂应用行为更可控
4. **开发体验**：更简单的异步状态管理

### 9.2 适用场景

**推荐使用并发渲染**：
- 大型数据列表/表格
- 实时搜索和过滤
- 复杂仪表盘
- 实时聊天应用
- 需要平滑过渡的应用

**可能不需要并发渲染**：
- 简单的静态页面
- 小规模应用
- 对兼容性要求极高的场景

### 9.3 迁移建议

1. **渐进式迁移**：从关键路径开始，逐步应用并发特性
2. **性能监控**：使用 React DevTools 监控渲染性能
3. **测试覆盖**：确保并发模式下的功能正确性
4. **错误处理**：完善错误边界和降级策略

### 9.4 未来展望

React 19 的并发渲染为下一代 Web 应用奠定了基础：

- **更智能的预加载**：基于用户行为的预测性加载
- **离线优先**：更好的离线体验和同步策略
- **跨平台一致性**：React Native 的并发支持
- **开发者工具**：更强大的调试和分析工具

---

© 2026 React 19 并发渲染详解指南