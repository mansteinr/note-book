# React 函数式组件 vs 类组件：区别与选择指南

## 目录

1. [组件类型概述](#组件类型概述)
2. [语法差异对比](#语法差异对比)
3. [状态管理对比](#状态管理对比)
4. [生命周期对比](#生命周期对比)
5. [性能优化对比](#性能优化对比)
6. [代码组织对比](#代码组织对比)
7. [TypeScript 支持对比](#typescript-支持对比)
8. [测试与调试对比](#测试与调试对比)
9. [迁移策略](#迁移策略)
10. [为什么更倾向于函数式组件](#为什么更倾向于函数式组件)
11. [总结](#总结)

## 一、组件类型概述

### 1.1 类组件（Class Components）

类组件是 React 早期的组件形式，基于 ES6 类语法，继承自 `React.Component` 或 `React.PureComponent`。

```jsx
import React, { Component } from 'react';

class ClassComponent extends Component {
  constructor(props) {
    super(props);
    this.state = { count: 0 };
  }
  
  componentDidMount() {
    console.log('Component mounted');
  }
  
  handleClick = () => {
    this.setState({ count: this.state.count + 1 });
  };
  
  render() {
    return (
      <div>
        <p>Count: {this.state.count}</p>
        <button onClick={this.handleClick}>Increment</button>
      </div>
    );
  }
}
```

### 1.2 函数式组件（Functional Components）

函数式组件是普通的 JavaScript 函数，接收 props 作为参数并返回 JSX。在 React 16.8 引入 Hooks 后，函数式组件具备了完整的功能。

```jsx
import React, { useState, useEffect } from 'react';

function FunctionalComponent() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    console.log('Component mounted');
  }, []);
  
  const handleClick = () => {
    setCount(count + 1);
  };
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={handleClick}>Increment</button>
    </div>
  );
}
```

### 1.3 历史演进

| React 版本 | 类组件 | 函数式组件 |
|------------|--------|------------|
| React 0.14 (2015) | 主要组件形式 | 无状态组件（仅展示） |
| React 16.8 (2019) | 完整功能 | 引入 Hooks，具备完整功能 |
| React 18 (2022) | 仍然支持 | 官方推荐，并发特性支持更好 |
| 未来版本 | 可能逐渐淘汰 | 主要发展方向 |

## 二、语法差异对比

### 2.1 基本语法结构

#### 2.1.1 类组件语法

```jsx
// 类组件基本结构
class ClassComponent extends React.Component {
  // 1. 构造函数（可选）
  constructor(props) {
    super(props); // 必须调用 super(props)
    this.state = { /* 初始状态 */ };
    this.handleClick = this.handleClick.bind(this); // 绑定 this
  }
  
  // 2. 生命周期方法
  componentDidMount() { /* ... */ }
  componentDidUpdate() { /* ... */ }
  componentWillUnmount() { /* ... */ }
  
  // 3. 自定义方法
  handleClick() {
    // 需要处理 this 绑定
    this.setState({ /* ... */ });
  }
  
  // 4. 渲染方法（必须）
  render() {
    return (
      <div>
        {/* JSX 内容 */}
      </div>
    );
  }
}
```

#### 2.1.2 函数式组件语法

```jsx
// 函数式组件基本结构
function FunctionalComponent(props) {
  // 1. 状态声明（使用 Hooks）
  const [state, setState] = useState(initialValue);
  
  // 2. 副作用处理（使用 Hooks）
  useEffect(() => {
    // 相当于 componentDidMount + componentDidUpdate
    return () => {
      // 清理函数，相当于 componentWillUnmount
    };
  }, [dependencies]);
  
  // 3. 事件处理函数
  const handleClick = () => {
    setState(newValue);
  };
  
  // 4. 直接返回 JSX
  return (
    <div>
      {/* JSX 内容 */}
    </div>
  );
}

// 箭头函数形式
const ArrowFunctionalComponent = (props) => {
  // ... 组件逻辑
  return <div>Content</div>;
};
```

### 2.2 Props 访问方式

#### 2.2.1 类组件访问 Props

```jsx
class ClassComponent extends React.Component {
  render() {
    // 通过 this.props 访问
    const { title, content, onClick } = this.props;
    
    return (
      <div>
        <h1>{title}</h1>
        <p>{content}</p>
        <button onClick={onClick}>Click</button>
      </div>
    );
  }
}

// 使用
<ClassComponent 
  title="Hello" 
  content="World" 
  onClick={() => console.log('clicked')}
/>
```

#### 2.2.2 函数式组件访问 Props

```jsx
// 方式1：直接参数解构
function FunctionalComponent({ title, content, onClick }) {
  return (
    <div>
      <h1>{title}</h1>
      <p>{content}</p>
      <button onClick={onClick}>Click</button>
    </div>
  );
}

// 方式2：使用 props 参数
function FunctionalComponent2(props) {
  const { title, content, onClick } = props;
  
  return (
    <div>
      <h1>{title}</h1>
      <p>{content}</p>
      <button onClick={onClick}>Click</button>
    </div>
  );
}

// 使用方式相同
<FunctionalComponent 
  title="Hello" 
  content="World" 
  onClick={() => console.log('clicked')}
/>
```

### 2.3 this 绑定的差异

#### 2.3.1 类组件的 this 绑定问题

```jsx
class ClassComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = { count: 0 };
    
    // 方法1：在构造函数中绑定（推荐）
    this.handleClick = this.handleClick.bind(this);
  }
  
  handleClick() {
    // 如果没有绑定，这里的 this 将是 undefined
    this.setState({ count: this.state.count + 1 });
  }
  
  // 方法2：使用箭头函数（类属性语法）
  handleClick2 = () => {
    this.setState({ count: this.state.count + 1 });
  };
  
  // 方法3：内联箭头函数（每次渲染都创建新函数）
  render() {
    return (
      <div>
        <button onClick={() => this.handleClick()}>
          Click (内联)
        </button>
        <button onClick={this.handleClick}>
          Click (已绑定)
        </button>
        <button onClick={this.handleClick2}>
          Click (箭头函数)
        </button>
      </div>
    );
  }
}
```

#### 2.3.2 函数式组件没有 this 绑定问题

```jsx
function FunctionalComponent() {
  const [count, setCount] = useState(0);
  
  // 直接定义函数，没有 this 绑定问题
  const handleClick = () => {
    setCount(count + 1);
  };
  
  // 如果需要缓存函数，使用 useCallback
  const memoizedHandleClick = useCallback(() => {
    setCount(prev => prev + 1);
  }, []);
  
  return (
    <div>
      <button onClick={handleClick}>
        Click (普通函数)
      </button>
      <button onClick={memoizedHandleClick}>
        Click (记忆化函数)
      </button>
    </div>
  );
}
```

## 三、状态管理对比

### 3.1 类组件的状态管理

#### 3.1.1 状态声明与初始化

```jsx
class ClassComponent extends React.Component {
  constructor(props) {
    super(props);
    
    // 状态声明在构造函数中
    this.state = {
      count: 0,
      user: null,
      items: [],
      loading: false,
      error: null
    };
  }
  
  // 或者使用类属性语法（实验性）
  state = {
    count: 0,
    user: null
  };
}
```

#### 3.1.2 状态更新

```jsx
class ClassComponent extends React.Component {
  state = { count: 0, items: [] };
  
  // 基本更新
  increment = () => {
    this.setState({ count: this.state.count + 1 });
  };
  
  // 函数式更新（基于前一个状态）
  incrementTwice = () => {
    this.setState(prevState => ({ count: prevState.count + 1 }));
    this.setState(prevState => ({ count: prevState.count + 1 }));
  };
  
  // 合并更新
  updateMultiple = () => {
    this.setState({
      loading: true,
      error: null
    });
  };
  
  // 回调函数（更新后执行）
  updateWithCallback = () => {
    this.setState(
      { count: this.state.count + 1 },
      () => {
        console.log('State updated:', this.state.count);
      }
    );
  };
}
```

### 3.2 函数式组件的状态管理

#### 3.2.1 状态声明与初始化

```jsx
function FunctionalComponent() {
  // 多个独立状态
  const [count, setCount] = useState(0);
  const [user, setUser] = useState(null);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // 对象状态（类似类组件）
  const [state, setState] = useState({
    count: 0,
    user: null,
    items: [],
    loading: false,
    error: null
  });
  
  // 惰性初始化（性能优化）
  const [expensiveState, setExpensiveState] = useState(() => {
    const initialValue = computeExpensiveValue();
    return initialValue;
  });
}
```

#### 3.2.2 状态更新

```jsx
function FunctionalComponent() {
  const [count, setCount] = useState(0);
  const [state, setState] = useState({ count: 0, name: '' });
  
  // 基本更新
  const increment = () => {
    setCount(count + 1);
  };
  
  // 函数式更新（推荐）
  const incrementTwice = () => {
    setCount(prev => prev + 1);
    setCount(prev => prev + 1);
  };
  
  // 对象状态更新
  const updateObjectState = () => {
    setState(prev => ({
      ...prev,          // 保留其他属性
      count: prev.count + 1
    }));
  };
  
  // 批量更新（React 18+ 默认行为）
  const batchUpdate = () => {
    setCount(count + 1);
    setCount(count + 1); // 注意：这里使用的是当前的 count 值
    // 实际只增加 1，而不是 2（除非使用函数式更新）
  };
}
```

### 3.3 状态管理对比总结

| 特性 | 类组件 | 函数式组件 |
|------|--------|------------|
| 状态声明 | 在构造函数或类属性中 | 使用 `useState` Hook |
| 状态更新 | `this.setState()` | `setState()` 函数 |
| 状态合并 | 自动合并对象属性 | 需要手动合并（使用扩展运算符） |
| 更新回调 | 支持第二个参数回调 | 使用 `useEffect` 监听状态变化 |
| 批量更新 | React 18+ 默认支持 | React 18+ 默认支持 |
| 性能优化 | `PureComponent` 或 `shouldComponentUpdate` | `React.memo` + `useMemo`/`useCallback` |

## 四、生命周期对比

### 4.1 类组件的生命周期

#### 4.1.1 完整的生命周期方法

```jsx
class LifecycleClassComponent extends React.Component {
  // 1. 挂载阶段
  constructor(props) {
    super(props);
    console.log('1. constructor');
  }
  
  static getDerivedStateFromProps(props, state) {
    console.log('2. getDerivedStateFromProps');
    return null; // 返回新的 state 或 null
  }
  
  componentDidMount() {
    console.log('4. componentDidMount');
    // 数据获取、订阅、DOM 操作
  }
  
  // 2. 更新阶段
  shouldComponentUpdate(nextProps, nextState) {
    console.log('5. shouldComponentUpdate');
    return true; // 返回 false 阻止重新渲染
  }
  
  getSnapshotBeforeUpdate(prevProps, prevState) {
    console.log('6. getSnapshotBeforeUpdate');
    return null; // 返回快照值或 null
  }
  
  componentDidUpdate(prevProps, prevState, snapshot) {
    console.log('7. componentDidUpdate');
    // 基于 props/state 变化执行操作
  }
  
  // 3. 卸载阶段
  componentWillUnmount() {
    console.log('8. componentWillUnmount');
    // 清理工作：取消订阅、清除定时器
  }
  
  // 4. 错误处理
  static getDerivedStateFromError(error) {
    console.log('getDerivedStateFromError');
    return { hasError: true };
  }
  
  componentDidCatch(error, errorInfo) {
    console.log('componentDidCatch');
    // 记录错误信息
  }
  
  render() {
    console.log('3. render');
    return <div>Content</div>;
  }
}
```

#### 4.1.2 生命周期执行顺序

```text
挂载阶段：
1. constructor()
2. static getDerivedStateFromProps()
3. render()
4. componentDidMount()

更新阶段：
1. static getDerivedStateFromProps()
2. shouldComponentUpdate()
3. render()
4. getSnapshotBeforeUpdate()
5. componentDidUpdate()

卸载阶段：
1. componentWillUnmount()

错误处理：
1. static getDerivedStateFromError()
2. componentDidCatch()
```

### 4.2 函数式组件的生命周期替代

#### 4.2.1 使用 useEffect 模拟生命周期

```jsx
function LifecycleFunctionalComponent() {
  const [count, setCount] = useState(0);
  const [data, setData] = useState(null);
  
  // 1. componentDidMount（只执行一次）
  useEffect(() => {
    console.log('componentDidMount 等效');
    
    // 数据获取
    fetchData().then(setData);
    
    // 事件监听
    window.addEventListener('resize', handleResize);
    
    // 清理函数（componentWillUnmount）
    return () => {
      console.log('componentWillUnmount 等效');
      window.removeEventListener('resize', handleResize);
    };
  }, []); // 空依赖数组 = 只运行一次
  
  // 2. componentDidUpdate（监听特定状态）
  useEffect(() => {
    console.log('count 变化:', count);
    // 相当于 componentDidUpdate 中检查 count 变化
  }, [count]); // 依赖 count
  
  // 3. 每次渲染后都执行（不推荐，除非必要）
  useEffect(() => {
    console.log('每次渲染后执行');
  }); // 没有依赖数组
  
  // 4. 基于条件执行
  useEffect(() => {
    if (count > 10) {
      console.log('count 大于 10');
    }
  }, [count]);
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  );
}
```

#### 4.2.2 生命周期映射表

| 类组件生命周期 | 函数式组件替代方案 |
|----------------|-------------------|
| `constructor` | 使用 `useState` 初始化状态 |
| `componentDidMount` | `useEffect(() => {}, [])` |
| `componentDidUpdate` | `useEffect(() => {}, [deps])` |
| `componentWillUnmount` | `useEffect(() => { return cleanup }, [])` |
| `shouldComponentUpdate` | `React.memo` 或 `useMemo` |
| `getDerivedStateFromProps` | 在渲染时计算或使用 `useEffect` |
| `getSnapshotBeforeUpdate` | 暂无直接替代，通常不需要 |
| `getDerivedStateFromError` | 无直接替代，使用错误边界组件 |
| `componentDidCatch` | 无直接替代，使用错误边界组件 |

### 4.3 错误处理对比

#### 4.3.1 类组件的错误边界

```jsx
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  
  componentDidCatch(error, errorInfo) {
    console.error('Error caught:', error, errorInfo);
    // 可以发送错误到监控服务
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

#### 4.3.2 函数式组件的错误处理

```jsx
// 函数式组件本身不能作为错误边界
// 需要使用类组件作为错误边界，或使用第三方库

import { ErrorBoundary } from 'react-error-boundary';

function ErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div role="alert">
      <p>Something went wrong:</p>
      <pre>{error.message}</pre>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onReset={() => window.location.reload()}
    >
      <MyComponent />
    </ErrorBoundary>
  );
}
```

## 五、性能优化对比

### 5.1 类组件的性能优化

#### 5.1.1 PureComponent

```jsx
import React, { PureComponent } from 'react';

class OptimizedClassComponent extends PureComponent {
  state = { count: 0 };
  
  // PureComponent 自动实现 shouldComponentUpdate
  // 进行浅比较（shallow comparison）
  
  handleClick = () => {
    this.setState({ count: this.state.count + 1 });
  };
  
  render() {
    console.log('Class component rendered');
    return (
      <div>
        <p>Count: {this.state.count}</p>
        <button onClick={this.handleClick}>Increment</button>
      </div>
    );
  }
}
```

#### 5.1.2 shouldComponentUpdate

```jsx
class CustomOptimizedClassComponent extends React.Component {
  state = { count: 0, items: [] };
  
  shouldComponentUpdate(nextProps, nextState) {
    // 自定义比较逻辑
    if (this.state.count !== nextState.count) {
      return true;
    }
    
    if (this.props.items !== nextProps.items) {
      return true;
    }
    
    return false; // 其他情况不重新渲染
  }
  
  // 或者使用浅比较辅助函数
  shouldComponentUpdate(nextProps, nextState) {
    return !shallowEqual(this.props, nextProps) ||
           !shallowEqual(this.state, nextState);
  }
}
```

### 5.2 函数式组件的性能优化

#### 5.2.1 React.memo

```jsx
import React, { memo } from 'react';

// 基本用法
const MemoizedComponent = memo(function MyComponent(props) {
  console.log('Memoized component rendered');
  return <div>{props.value}</div>;
});

// 自定义比较函数
const CustomMemoizedComponent = memo(
  function MyComponent(props) {
    return <div>{props.user.name}</div>;
  },
  // 自定义比较函数（类似 shouldComponentUpdate）
  (prevProps, nextProps) => {
    // 返回 true 表示不重新渲染（props 相等）
    // 返回 false 表示需要重新渲染（props 不相等）
    return prevProps.user.id === nextProps.user.id;
  }
);
```

#### 5.2.2 useMemo 和 useCallback

```jsx
function OptimizedFunctionalComponent({ items, filter }) {
  const [count, setCount] = useState(0);
  
  // useMemo：缓存计算结果
  const filteredItems = useMemo(() => {
    console.log('Filtering items...');
    return items.filter(item => 
      item.name.includes(filter)
    );
  }, [items, filter]); // 依赖项变化时才重新计算
  
  // useCallback：缓存函数
  const handleClick = useCallback(() => {
    console.log('Button clicked, count:', count);
    setCount(prev => prev + 1);
  }, []); // 空依赖数组：函数只创建一次
  
  // 依赖 count 的缓存函数
  const handleClickWithCount = useCallback(() => {
    console.log('Current count:', count);
  }, [count]); // 依赖 count，count 变化时重新创建
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={handleClick}>Increment</button>
      <ul>
        {filteredItems.map(item => (
          <li key={item.id}>{item.name}</li>
        ))}
      </ul>
    </div>
  );
}
```

### 5.3 性能优化对比总结

| 优化技术 | 类组件 | 函数式组件 |
|----------|--------|------------|
| 避免不必要渲染 | `PureComponent` 或 `shouldComponentUpdate` | `React.memo` |
| 缓存计算结果 | 在 `render` 方法中手动缓存 | `useMemo` Hook |
| 缓存函数 | 在构造函数中绑定或使用类属性 | `useCallback` Hook |
| 代码分割 | `React.lazy` + `Suspense` | `React.lazy` + `Suspense` |
| 虚拟化长列表 | 第三方库（如 `react-window`） | 第三方库（如 `react-window`） |

## 六、代码组织对比

### 6.1 类组件的代码组织

#### 6.1.1 典型的类组件结构

```jsx
class OrganizedClassComponent extends React.Component {
  // 1. 静态属性
  static defaultProps = {
    initialCount: 0
  };
  
  static propTypes = {
    initialCount: PropTypes.number,
    onCountChange: PropTypes.func
  };
  
  // 2. 构造函数
  constructor(props) {
    super(props);
    this.state = {
      count: props.initialCount,
      isLoading: false,
      data: null
    };
    
    // 方法绑定
    this.increment = this.increment.bind(this);
    this.decrement = this.decrement.bind(this);
  }
  
  // 3. 生命周期方法
  componentDidMount() {
    this.fetchData();
  }
  
  componentDidUpdate(prevProps, prevState) {
    if (prevState.count !== this.state.count) {
      this.props.onCountChange?.(this.state.count);
    }
  }
  
  componentWillUnmount() {
    this.cleanup();
  }
  
  // 4. 业务方法
  async fetchData() {
    this.setState({ isLoading: true });
    
    try {
      const data = await api.fetchData();
      this.setState({ data, isLoading: false });
    } catch (error) {
      this.setState({ isLoading: false, error });
    }
  }
  
  increment() {
    this.setState(prev => ({ count: prev.count + 1 }));
  }
  
  decrement() {
    this.setState(prev => ({ count: prev.count - 1 }));
  }
  
  cleanup() {
    // 清理资源
  }
  
  // 5. 渲染方法
  render() {
    const { count, isLoading, data } = this.state;
    
    if (isLoading) {
      return <div>Loading...</div>;
    }
    
    return (
      <div>
        <h1>Count: {count}</h1>
        <button onClick={this.increment}>+</button>
        <button onClick={this.decrement}>-</button>
        {data && <DataDisplay data={data} />}
      </div>
    );
  }
}
```

#### 6.1.2 类组件的问题

1. **样板代码多**：构造函数、方法绑定、生命周期方法
2. **逻辑分散**：相关逻辑分散在不同的生命周期方法中
3. **this 绑定问题**：容易忘记绑定或绑定错误
4. **难以复用逻辑**：需要使用高阶组件或渲染属性

### 6.2 函数式组件的代码组织

#### 6.2.1 典型的函数式组件结构

```jsx
function OrganizedFunctionalComponent({ 
  initialCount = 0, 
  onCountChange 
}) {
  // 1. 状态声明（顶部）
  const [count, setCount] = useState(initialCount);
  const [isLoading, setIsLoading] = useState(false);
  const [data, setData] = useState(null);
  
  // 2. 副作用（数据获取）
  useEffect(() => {
    fetchData();
    
    return () => {
      // 清理函数
      console.log('Component unmounting');
    };
  }, []); // 空数组：只运行一次
  
  // 3. 业务逻辑（自定义 Hook）
  const { increment, decrement } = useCounter(count, setCount, onCountChange);
  
  // 4. 数据处理（useMemo）
  const processedData = useMemo(() => {
    return data ? processData(data) : null;
  }, [data]);
  
  // 5. 事件处理（useCallback）
  const handleReset = useCallback(() => {
    setCount(initialCount);
  }, [initialCount]);
  
  // 6. 条件渲染
  if (isLoading) {
    return <div>Loading...</div>;
  }
  
  // 7. 返回 JSX
  return (
    <div>
      <h1>Count: {count}</h1>
      <button onClick={increment}>+</button>
      <button onClick={decrement}>-</button>
      <button onClick={handleReset}>Reset</button>
      {processedData && <DataDisplay data={processedData} />}
    </div>
  );
}

// 自定义 Hook：复用逻辑
function useCounter(initialValue, setter, onChange) {
  const increment = useCallback(() => {
    setter(prev => {
      const newValue = prev + 1;
      onChange?.(newValue);
      return newValue;
    });
  }, [setter, onChange]);
  
  const decrement = useCallback(() => {
    setter(prev => {
      const newValue = prev - 1;
      onChange?.(newValue);
      return newValue;
    });
  }, [setter, onChange]);
  
  return { increment, decrement };
}
```

#### 6.2.2 函数式组件的优势

1. **代码简洁**：没有样板代码，逻辑更集中
2. **逻辑复用简单**：自定义 Hook 可以轻松复用逻辑
3. **没有 this 问题**：直接使用变量和函数，无需绑定
4. **更好的可测试性**：纯函数更容易测试
5. **更好的 TypeScript 支持**：类型推断更准确

### 6.3 自定义 Hook 的优势

```jsx
// 自定义 Hook：封装数据获取逻辑
function useFetch(url, options) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(url, options);
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [url, options]);
  
  return { data, loading, error };
}

// 在多个组件中复用
function UserProfile({ userId }) {
  const { data: user, loading, error } = useFetch(`/api/users/${userId}`);
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}

function PostList() {
  const { data: posts, loading, error } = useFetch('/api/posts');
  
  // ... 渲染逻辑
}
```

## 七、TypeScript 支持对比

### 7.1 类组件的 TypeScript 支持

#### 7.1.1 Props 和 State 类型定义

```typescript
import React, { Component } from 'react';

interface Props {
  title: string;
  initialCount?: number;
  onCountChange?: (count: number) => void;
}

interface State {
  count: number;
  isLoading: boolean;
  data: DataType | null;
}

class TypedClassComponent extends Component<Props, State> {
  // 默认 props
  static defaultProps: Partial<Props> = {
    initialCount: 0
  };
  
  constructor(props: Props) {
    super(props);
    
    this.state = {
      count: props.initialCount || 0,
      isLoading: false,
      data: null
    };
  }
  
  // 类型安全的方法
  increment = (): void => {
    this.setState(prevState => ({
      count: prevState.count + 1
    }));
  };
  
  render(): React.ReactNode {
    const { title } = this.props;
    const { count } = this.state;
    
    return (
      <div>
        <h1>{title}</h1>
        <p>Count: {count}</p>
        <button onClick={this.increment}>Increment</button>
      </div>
    );
  }
}
```

#### 7.1.2 泛型类组件

```typescript
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}

class GenericListComponent<T> extends Component<ListProps<T>> {
  render() {
    const { items, renderItem } = this.props;
    
    return (
      <ul>
        {items.map((item, index) => (
          <li key={index}>
            {renderItem(item)}
          </li>
        ))}
      </ul>
    );
  }
}

// 使用
<GenericListComponent
  items={users}
  renderItem={(user) => <span>{user.name}</span>}
/>
```

### 7.2 函数式组件的 TypeScript 支持

#### 7.2.1 Props 类型定义

```typescript
import React, { useState } from 'react';

interface Props {
  title: string;
  initialCount?: number;
  onCountChange?: (count: number) => void;
}

// 方式1：使用 React.FC（有争议）
const TypedFunctionalComponent1: React.FC<Props> = ({
  title,
  initialCount = 0,
  onCountChange
}) => {
  const [count, setCount] = useState(initialCount);
  
  const increment = () => {
    const newCount = count + 1;
    setCount(newCount);
    onCountChange?.(newCount);
  };
  
  return (
    <div>
      <h1>{title}</h1>
      <p>Count: {count}</p>
      <button onClick={increment}>Increment</button>
    </div>
  );
};

// 方式2：直接类型注解（推荐）
function TypedFunctionalComponent2(props: Props) {
  const { title, initialCount = 0, onCountChange } = props;
  const [count, setCount] = useState(initialCount);
  
  // ... 相同逻辑
}

// 方式3：内联类型
const TypedFunctionalComponent3 = (props: {
  title: string;
  initialCount?: number;
}) => {
  // ... 组件逻辑
};
```

#### 7.2.2 泛型函数式组件

```typescript
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}

// 泛型函数式组件
function GenericListComponent<T>({
  items,
  renderItem
}: ListProps<T>) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={index}>
          {renderItem(item)}
        </li>
      ))}
    </ul>
  );
}

// 使用
<GenericListComponent
  items={users}
  renderItem={(user) => <span>{user.name}</span>}
/>
```

### 7.3 TypeScript 支持对比

| 特性 | 类组件 | 函数式组件 |
|------|--------|------------|
| Props 类型 | `Component<Props, State>` | `React.FC<Props>` 或直接注解 |
| State 类型 | 第二个泛型参数 | `useState<Type>` 泛型 |
| 默认 Props | `static defaultProps` | 默认参数值 |
| 子组件类型 | `this.props.children` | `React.ReactNode` 类型 |
| 泛型支持 | 类泛型 `Component<T>` | 函数泛型 `function Component<T>` |
| 类型推断 | 较弱，需要显式注解 | 较强，能更好推断 Hook 类型 |

## 八、测试与调试对比

### 8.1 测试对比

#### 8.1.1 类组件测试

```javascript
// 类组件测试示例
import { render, screen, fireEvent } from '@testing-library/react';
import ClassComponent from './ClassComponent';

describe('ClassComponent', () => {
  it('renders initial count', () => {
    render(<ClassComponent initialCount={5} />);
    expect(screen.getByText('Count: 5')).toBeInTheDocument();
  });
  
  it('increments count on button click', () => {
    render(<ClassComponent />);
    const button = screen.getByText('Increment');
    
    fireEvent.click(button);
    expect(screen.getByText('Count: 1')).toBeInTheDocument();
  });
  
  it('calls onCountChange when count changes', () => {
    const mockOnChange = jest.fn();
    render(<ClassComponent onCountChange={mockOnChange} />);
    
    const button = screen.getByText('Increment');
    fireEvent.click(button);
    
    expect(mockOnChange).toHaveBeenCalledWith(1);
  });
});
```

#### 8.1.2 函数式组件测试

```javascript
// 函数式组件测试示例
import { render, screen, fireEvent } from '@testing-library/react';
import FunctionalComponent from './FunctionalComponent';

describe('FunctionalComponent', () => {
  it('renders initial count', () => {
    render(<FunctionalComponent initialCount={5} />);
    expect(screen.getByText('Count: 5')).toBeInTheDocument();
  });
  
  it('increments count on button click', () => {
    render(<FunctionalComponent />);
    const button = screen.getByText('Increment');
    
    fireEvent.click(button);
    expect(screen.getByText('Count: 1')).toBeInTheDocument();
  });
  
  it('calls onCountChange when count changes', () => {
    const mockOnChange = jest.fn();
    render(<FunctionalComponent onCountChange={mockOnChange} />);
    
    const button = screen.getByText('Increment');
    fireEvent.click(button);
    
    expect(mockOnChange).toHaveBeenCalledWith(1);
  });
  
  it('handles async operations', async () => {
    // 测试异步逻辑
  });
});
```

### 8.2 调试对比

#### 8.2.1 React DevTools 支持

| 调试特性 | 类组件 | 函数式组件 |
|----------|--------|------------|
| 组件树查看 | 支持 | 支持 |
| Props 查看 | 支持 | 支持 |
| State 查看 | 支持（this.state） | 支持（Hook 状态） |
| 钩子查看 | 不支持 | 支持（Hook 调试） |
| 性能分析 | 支持 | 支持（更好的 Hook 分析） |

#### 8.2.2 调试技巧

```jsx
// 类组件调试
class DebugClassComponent extends React.Component {
  componentDidUpdate(prevProps, prevState) {
    // 调试状态变化
    if (prevState.count !== this.state.count) {
      console.log('Count changed:', this.state.count);
    }
  }
  
  render() {
    // 调试渲染
    console.log('Class component rendering');
    return <div>Content</div>;
  }
}

// 函数式组件调试
function DebugFunctionalComponent() {
  const [count, setCount] = useState(0);
  
  // 使用 useEffect 调试
  useEffect(() => {
    console.log('Count changed:', count);
  }, [count]);
  
  // 使用 useDebugValue（自定义 Hook 中）
  useDebugValue(count > 10 ? 'High' : 'Low');
  
  console.log('Functional component rendering');
  return <div>Content</div>;
}
```

## 九、迁移策略

### 9.1 从类组件迁移到函数式组件

#### 9.1.1 逐步迁移策略

```jsx
// 步骤1：识别组件类型
// - 简单展示组件：直接重写为函数式组件
// - 有状态组件：使用 Hooks 重写
// - 复杂组件：分步骤迁移

// 步骤2：迁移无状态组件
// 之前：
class UserInfo extends React.Component {
  render() {
    const { user } = this.props;
    return (
      <div>
        <h2>{user.name}</h2>
        <p>{user.email}</p>
      </div>
    );
  }
}

// 之后：
function UserInfo({ user }) {
  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
}

// 步骤3：迁移有状态组件
// 之前：
class Counter extends React.Component {
  constructor(props) {
    super(props);
    this.state = { count: 0 };
    this.increment = this.increment.bind(this);
  }
  
  increment() {
    this.setState({ count: this.state.count + 1 });
  }
  
  render() {
    return (
      <div>
        <p>Count: {this.state.count}</p>
        <button onClick={this.increment}>Increment</button>
      </div>
    );
  }
}

// 之后：
function Counter() {
  const [count, setCount] = useState(0);
  
  const increment = () => {
    setCount(count + 1);
  };
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>Increment</button>
    </div>
  );
}
```

#### 9.1.2 生命周期方法迁移

```jsx
// 类组件
class DataFetcher extends React.Component {
  state = { data: null, loading: true };
  
  componentDidMount() {
    this.fetchData();
  }
  
  componentDidUpdate(prevProps) {
    if (prevProps.userId !== this.props.userId) {
      this.fetchData();
    }
  }
  
  componentWillUnmount() {
    // 清理工作
  }
  
  async fetchData() {
    try {
      const data = await api.fetchData(this.props.userId);
      this.setState({ data, loading: false });
    } catch (error) {
      this.setState({ loading: false, error });
    }
  }
  
  render() {
    // ... 渲染逻辑
  }
}

// 函数式组件
function DataFetcher({ userId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    let isMounted = true;
    
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await api.fetchData(userId);
        
        if (isMounted) {
          setData(result);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err);
          setLoading(false);
        }
      }
    };
    
    fetchData();
    
    return () => {
      isMounted = false;
      // 清理工作
    };
  }, [userId]); // 依赖 userId，变化时重新获取
  
  // ... 渲染逻辑
}
```

### 9.2 迁移工具和资源

#### 9.2.1 自动化工具

```bash
# 1. 使用 codemod 工具自动迁移
npx react-codemod class-to-function

# 2. 手动迁移辅助工具
# - ESLint 规则：eslint-plugin-react-hooks
# - TypeScript：自动类型推断
# - React DevTools：调试 Hook

# 3. 迁移检查清单
# - [ ] 状态迁移：this.state → useState
# - [ ] 生命周期：componentDidMount → useEffect
# - [ ] 方法绑定：移除 bind，使用 useCallback
# - [ ] 实例方法：转换为函数或自定义 Hook
# - [ ] 引用：this.refs → useRef
# - [ ] 上下文：this.context → useContext
```

## 十、为什么更倾向于函数式组件

### 10.1 技术优势

#### 10.1.1 代码简洁性

```jsx
// 类组件：21行代码
class CounterClass extends React.Component {
  constructor(props) {
    super(props);
    this.state = { count: 0 };
    this.handleClick = this.handleClick.bind(this);
  }
  
  handleClick() {
    this.setState({ count: this.state.count + 1 });
  }
  
  render() {
    return (
      <div>
        <p>Count: {this.state.count}</p>
        <button onClick={this.handleClick}>Increment</button>
      </div>
    );
  }
}

// 函数式组件：11行代码（减少48%）
function CounterFunctional() {
  const [count, setCount] = useState(0);
  
  const handleClick = () => {
    setCount(count + 1);
  };
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={handleClick}>Increment</button>
    </div>
  );
}
```

#### 10.1.2 更好的逻辑复用

```jsx
// 自定义 Hook：一次编写，多处使用
function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : initialValue;
  });
  
  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);
  
  return [value, setValue];
}

// 在多个组件中复用
function ComponentA() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');
  // ...
}

function ComponentB() {
  const [userPrefs, setUserPrefs] = useLocalStorage('prefs', {});
  // ...
}
```

### 10.2 开发体验优势

#### 10.2.1 学习曲线更平缓

```jsx
// 类组件需要理解的概念：
// 1. ES6 类语法
// 2. 继承和 super()
// 3. this 绑定
// 4. 生命周期方法
// 5. 实例属性和方法

// 函数式组件需要理解的概念：
// 1. JavaScript 函数
// 2. Hooks（useState, useEffect 等）
// 3. 闭包和作用域

// 对于新手，函数概念比类概念更基础
```

#### 10.2.2 更好的工具支持

```json
// ESLint 配置
{
  "plugins": ["react-hooks"],
  "rules": {
    "react-hooks/rules-of-hooks": "error",      // 检查 Hook 规则
    "react-hooks/exhaustive-deps": "warn"       // 检查依赖项
  }
}

// TypeScript 更好的类型推断
function Component({ value }: { value: string }) {
  // TypeScript 能准确推断 Hook 类型
  const [count, setCount] = useState(0);          // count: number
  const [name, setName] = useState('');           // name: string
  const [list, setList] = useState<string[]>([]); // list: string[]
  
  // 自动补全和类型检查更好
}
```

### 10.3 性能和维护优势

#### 10.3.1 包体积更小

```javascript
// 函数式组件编译后代码更小
// 类组件：
class MyComponent extends React.Component {
  // 需要包含整个类系统
}

// 函数式组件：
function MyComponent() {
  // 只是普通函数
}

// 实际项目中的包体积差异：
// - 类组件：包含类继承、实例化等开销
// - 函数式组件：更轻量，Tree-shaking 更有效
```

#### 10.3.2 更好的未来兼容性

```jsx
// React 新特性优先支持函数式组件
// 1. 并发特性（Concurrent Features）
function ConcurrentComponent() {
  const [isPending, startTransition] = useTransition();
  
  // 类组件无法直接使用
}

// 2. 服务器组件（Server Components）
// 函数式组件更容易支持服务端渲染优化

// 3. React Forget 编译器
// 针对函数式组件的自动优化编译器

// React 团队官方推荐：
// "在新代码中，我们推荐使用函数式组件和 Hooks"
```

### 10.4 实际项目数据

根据社区调查和实际项目经验：

| 指标 | 类组件 | 函数式组件 |
|------|--------|------------|
| 代码行数 | 通常多 30-50% | 更简洁 |
| 首次渲染时间 | 稍慢（需要实例化） | 稍快 |
| 更新性能 | 依赖优化策略 | 更容易优化 |
| 内存使用 | 稍高（实例对象） | 稍低 |
| 测试覆盖率 | 较难达到高覆盖 | 更容易测试 |
| 团队上手速度 | 较慢（概念多） | 较快 |

### 10.5 何时仍然使用类组件

尽管函数式组件有诸多优势，但在某些情况下类组件仍然是合适的选择：

1. **遗留代码维护**：已有大量类组件代码，迁移成本高
2. **错误边界**：函数式组件不能作为错误边界
3. **特定生命周期需求**：需要 `getSnapshotBeforeUpdate`
4. **第三方库要求**：某些库可能要求类组件
5. **团队技能栈**：团队熟悉类组件，暂时不想迁移

## 十一、总结

### 11.1 核心差异总结

| 方面 | 类组件 | 函数式组件 |
|------|--------|------------|
| 语法 | ES6 类 | JavaScript 函数 |
| 状态 | `this.state` 和 `this.setState()` | `useState` Hook |
| 生命周期 | 生命周期方法 | `useEffect` Hook |
| this 绑定 | 需要处理 | 不需要 |
| 代码量 | 较多（样板代码） | 较少 |
| 逻辑复用 | 高阶组件、渲染属性 | 自定义 Hook |
| 性能优化 | `PureComponent`、`shouldComponentUpdate` | `React.memo`、`useMemo`、`useCallback` |
| TypeScript | 类型注解较复杂 | 类型推断更好 |
| 测试 | 需要实例化 | 纯函数，更容易测试 |
| 未来兼容 | 逐渐淘汰 | 官方推荐，新特性支持 |

### 11.2 选择建议

#### 对于新项目：
- **强烈推荐使用函数式组件**
- 利用 Hooks 和现代 React 特性
- 更好的开发体验和性能

#### 对于现有项目：
- **逐步迁移**到函数式组件
- 新组件使用函数式
- 重构旧组件时考虑迁移

#### 学习路径：
1. 先掌握函数式组件和 Hooks
2. 了解类组件的基本概念（用于维护旧代码）
3. 深入学习自定义 Hook 和高级模式

### 11.3 最佳实践

1. **优先使用函数式组件**：除非有特定需求
2. **合理使用 Hooks**：遵循规则，避免滥用
3. **提取自定义 Hook**：复用逻辑，保持组件简洁
4. **性能优化**：适时使用 `React.memo`、`useMemo`、`useCallback`
5. **类型安全**：使用 TypeScript 增强代码可靠性
6. **测试驱动**：编写可测试的组件

### 11.4 未来展望

React 团队明确表示函数式组件是未来：
- 新特性优先支持函数式组件
- 类组件可能逐渐淡出
- 编译器优化（React Forget）针对函数式组件
- 更好的开发工具和生态系统支持

### 11.5 学习资源

1. **官方文档**：
   - [Hooks API 参考](https://reactjs.org/docs/hooks-reference.html)
   - [Hooks 规则](https://reactjs.org/docs/hooks-rules.html)
   - [自定义 Hook](https://reactjs.org/docs/hooks-custom.html)

2. **社区资源**：
   - [useHooks](https://usehooks.com/) - 常用 Hook 示例
   - [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
   - [Awesome React Hooks](https://github.com/rehooks/awesome-react-hooks)

3. **工具**：
   - ESLint: `eslint-plugin-react-hooks`
   - React DevTools: Hook 调试支持
   - VSCode 扩展: React 相关工具

---

© 2026 React 函数式组件 vs 类组件深度对比指南