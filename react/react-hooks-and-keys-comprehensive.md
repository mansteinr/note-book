# React Hooks 与 Key 深度解析：useState、useEffect 与列表渲染

## 目录

1. [useState：状态管理的基础](#usestate状态管理的基础)
2. [useEffect：副作用处理的核心](#useeffect副作用处理的核心)
3. [useEffect 依赖数组的工作原理](#useeffect-依赖数组的工作原理)
4. [React Key 的作用与必要性](#react-key-的作用与必要性)
5. [Hooks 与 Key 的协同应用](#hooks-与-key-的协同应用)
6. [常见问题与解决方案](#常见问题与解决方案)
7. [性能优化最佳实践](#性能优化最佳实践)
8. [总结](#总结)

## 一、useState：状态管理的基础

### 1.1 useState 的基本定义

`useState` 是 React 中最基础、最常用的 Hook，用于在函数组件中添加**局部状态**。它取代了类组件中的 `this.state` 和 `this.setState`。

```jsx
import { useState } from 'react';

function Counter() {
  // useState 返回一个数组：[当前状态值, 更新状态的函数]
  const [count, setCount] = useState(0);
  
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

### 1.2 useState 的核心特性

#### 1.2.1 状态声明与初始化

```jsx
// 基本初始化
const [state, setState] = useState(initialValue);

// 惰性初始化（性能优化）
const [state, setState] = useState(() => {
  // 复杂计算只在初始渲染时执行一次
  return computeExpensiveInitialValue();
});

// 实际示例
function TodoList() {
  const [todos, setTodos] = useState(() => {
    // 从 localStorage 读取初始数据
    const saved = localStorage.getItem('todos');
    return saved ? JSON.parse(saved) : [];
  });
  
  // ... 其他代码
}
```

#### 1.2.2 状态更新机制

```jsx
function Counter() {
  const [count, setCount] = useState(0);
  
  // 直接更新
  const increment = () => {
    setCount(count + 1);
  };
  
  // 函数式更新（基于前一个状态）
  const incrementTwice = () => {
    setCount(prevCount => prevCount + 1);
    setCount(prevCount => prevCount + 1);
  };
  
  // 批量更新（React 18+ 默认行为）
  const updateMultiple = () => {
    setCount(count + 1);
    setCount(count + 1); // 注意：这里使用的是当前的 count 值
    // 实际只增加 1，而不是 2
  };
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>+1</button>
      <button onClick={incrementTwice}>+2（函数式）</button>
    </div>
  );
}
```

#### 1.2.3 状态更新与重新渲染

```javascript
// React 内部的状态更新流程
function updateState(newState) {
  // 1. 更新 Fiber 节点的 memoizedState
  workInProgress.memoizedState = newState;
  
  // 2. 标记组件需要重新渲染
  markUpdateLaneFromFiberToRoot(workInProgress);
  
  // 3. 调度重新渲染
  scheduleUpdateOnFiber(root);
  
  // 4. 在下一次渲染中，useState 返回更新后的值
  return newState;
}
```

### 1.3 useState 的常见模式

#### 1.3.1 对象状态管理

```jsx
function UserForm() {
  // 对象状态
  const [user, setUser] = useState({
    name: '',
    email: '',
    age: 0
  });
  
  // 更新部分属性
  const updateName = (name) => {
    setUser(prev => ({
      ...prev,        // 保留其他属性
      name            // 更新 name 属性
    }));
  };
  
  // 批量更新
  const updateUser = (updates) => {
    setUser(prev => ({
      ...prev,
      ...updates
    }));
  };
  
  return (
    <form>
      <input
        value={user.name}
        onChange={(e) => updateName(e.target.value)}
      />
      <input
        value={user.email}
        onChange={(e) => updateUser({ email: e.target.value })}
      />
    </form>
  );
}
```

#### 1.3.2 数组状态管理

```jsx
function TodoApp() {
  const [todos, setTodos] = useState([]);
  
  // 添加
  const addTodo = (text) => {
    const newTodo = { id: Date.now(), text, completed: false };
    setTodos(prev => [...prev, newTodo]);
  };
  
  // 删除
  const deleteTodo = (id) => {
    setTodos(prev => prev.filter(todo => todo.id !== id));
  };
  
  // 更新
  const toggleTodo = (id) => {
    setTodos(prev => prev.map(todo =>
      todo.id === id 
        ? { ...todo, completed: !todo.completed }
        : todo
    ));
  };
  
  // 排序
  const sortTodos = () => {
    setTodos(prev => [...prev].sort((a, b) => 
      a.text.localeCompare(b.text)
    ));
  };
  
  return (
    // ... 组件内容
  );
}
```

## 二、useEffect：副作用处理的核心

### 2.1 useEffect 的基本定义

`useEffect` 用于在函数组件中执行**副作用操作**，如数据获取、订阅、手动修改 DOM 等。它相当于类组件中的 `componentDidMount`、`componentDidUpdate` 和 `componentWillUnmount` 的组合。

```jsx
import { useState, useEffect } from 'react';

function DataFetcher({ userId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // 副作用函数
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/users/${userId}`);
        const result = await response.json();
        setData(result);
      } catch (error) {
        console.error('Fetch error:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
    
    // 清理函数（可选）
    return () => {
      // 取消请求或清理资源
      console.log('Cleanup for user:', userId);
    };
  }, [userId]); // 依赖数组
  
  if (loading) return <div>Loading...</div>;
  if (!data) return <div>No data</div>;
  
  return <div>{JSON.stringify(data)}</div>;
}
```

### 2.2 useEffect 的执行时机

#### 2.2.1 组件挂载时（Mount）

```jsx
function Component() {
  useEffect(() => {
    console.log('组件挂载时执行');
    // 相当于 componentDidMount
    
    return () => {
      console.log('组件卸载时执行');
      // 相当于 componentWillUnmount
    };
  }, []); // 空依赖数组
  
  return <div>Component</div>;
}
```

#### 2.2.2 组件更新时（Update）

```jsx
function Component({ prop }) {
  useEffect(() => {
    console.log('prop 变化时执行');
    // 相当于 componentDidUpdate（针对特定 prop）
  }, [prop]); // 依赖数组中包含 prop
  
  return <div>Prop: {prop}</div>;
}
```

#### 2.2.3 组件卸载时（Unmount）

```jsx
function Component() {
  useEffect(() => {
    console.log('副作用执行');
    
    // 清理函数在组件卸载时执行
    return () => {
      console.log('清理副作用');
      // 取消订阅、清除定时器、取消请求等
    };
  }, []);
  
  return <div>Component</div>;
}
```

### 2.3 useEffect 的常见用例

#### 2.3.1 数据获取

```jsx
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    let isMounted = true;
    
    const fetchUser = async () => {
      try {
        const response = await fetch(`/api/users/${userId}`);
        if (!response.ok) throw new Error('Failed to fetch');
        const data = await response.json();
        
        if (isMounted) {
          setUser(data);
          setError(null);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
          setUser(null);
        }
      }
    };
    
    fetchUser();
    
    return () => {
      isMounted = false;
      // 可以在这里取消 fetch
    };
  }, [userId]);
  
  // ... 渲染逻辑
}
```

#### 2.3.2 事件监听

```jsx
function WindowSizeTracker() {
  const [windowSize, setWindowSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight
  });
  
  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };
    
    window.addEventListener('resize', handleResize);
    
    // 清理函数：移除事件监听
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []); // 空数组：只在挂载和卸载时执行
  
  return (
    <div>
      Window size: {windowSize.width} x {windowSize.height}
    </div>
  );
}
```

#### 2.3.3 定时器

```jsx
function Timer() {
  const [seconds, setSeconds] = useState(0);
  
  useEffect(() => {
    const intervalId = setInterval(() => {
      setSeconds(prev => prev + 1);
    }, 1000);
    
    // 清理函数：清除定时器
    return () => {
      clearInterval(intervalId);
    };
  }, []); // 空数组：定时器只设置一次
  
  return <div>Seconds: {seconds}</div>;
}
```

#### 2.3.4 文档标题更新

```jsx
function PageTitle({ title }) {
  useEffect(() => {
    // 保存原始标题
    const originalTitle = document.title;
    
    // 更新标题
    document.title = title;
    
    // 清理函数：恢复原始标题
    return () => {
      document.title = originalTitle;
    };
  }, [title]); // 依赖 title
  
  return <div>Current page: {title}</div>;
}
```

## 三、useEffect 依赖数组的工作原理

### 3.1 依赖数组的基本概念

依赖数组是 `useEffect` 的第二个参数，用于控制副作用函数的执行时机。React 使用**浅比较**（Shallow Comparison）来检查依赖项是否发生变化。

```jsx
useEffect(() => {
  // 副作用逻辑
}, [dependency1, dependency2, dependency3]); // 依赖数组
```

### 3.2 依赖数组的三种模式

#### 3.2.1 空依赖数组 `[]`

```jsx
useEffect(() => {
  console.log('只在组件挂载时执行一次');
  // 相当于 componentDidMount
  
  return () => {
    console.log('只在组件卸载时执行');
    // 相当于 componentWillUnmount
  };
}, []); // 空数组：不依赖任何值
```

**执行时机**：
- 组件挂载后执行一次
- 组件卸载前执行清理函数
- 组件更新时**不执行**

#### 3.2.2 有依赖项的数组 `[dep1, dep2]`

```jsx
function Component({ userId, filter }) {
  useEffect(() => {
    console.log('userId 或 filter 变化时执行');
    fetchData(userId, filter);
  }, [userId, filter]); // 依赖 userId 和 filter
  
  return <div>Component</div>;
}
```

**执行时机**：
- 组件挂载后执行
- 当 `userId` 或 `filter` 变化时执行
- 执行前会先执行上一次的清理函数（如果有）

#### 3.2.3 没有依赖数组

```jsx
useEffect(() => {
  console.log('每次渲染后都执行');
  // 相当于 componentDidMount + componentDidUpdate
});
```

**执行时机**：
- 组件挂载后执行
- **每次组件更新后都执行**
- 执行前会先执行上一次的清理函数

### 3.3 React 的依赖比较机制

#### 3.3.1 浅比较（Shallow Comparison）

React 使用 `Object.is` 算法进行浅比较：

```javascript
// React 内部的依赖比较逻辑
function areDependenciesEqual(prevDeps, nextDeps) {
  if (prevDeps === null || nextDeps === null) {
    return false;
  }
  
  if (prevDeps.length !== nextDeps.length) {
    return false;
  }
  
  for (let i = 0; i < prevDeps.length; i++) {
    // 使用 Object.is 进行比较
    if (!Object.is(prevDeps[i], nextDeps[i])) {
      return false;
    }
  }
  
  return true;
}

// Object.is 与 === 的区别
Object.is(NaN, NaN);    // true
NaN === NaN;            // false

Object.is(0, -0);       // false
0 === -0;               // true
```

#### 3.3.2 依赖项变化的检测

```javascript
// 示例：依赖项如何影响 useEffect 的执行
let prevDeps = null;
let effectRunCount = 0;

function checkAndRunEffect(nextDeps) {
  if (!areDependenciesEqual(prevDeps, nextDeps)) {
    console.log(`依赖变化，执行副作用 (#${++effectRunCount})`);
    runSideEffect();
    prevDeps = nextDeps;
  } else {
    console.log('依赖未变化，跳过副作用');
  }
}

// 测试
checkAndRunEffect([1, 2]);     // 执行 (#1)
checkAndRunEffect([1, 2]);     // 跳过（相同）
checkAndRunEffect([1, 3]);     // 执行 (#2)
checkAndRunEffect([2, 3]);     // 执行 (#3)
```

### 3.4 依赖数组的常见陷阱与解决方案

#### 3.4.1 无限循环陷阱

```jsx
// ❌ 错误：导致无限循环
function InfiniteLoop() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    // 每次渲染后都更新 count
    setCount(count + 1); // 触发重新渲染
  }); // 没有依赖数组：每次渲染都执行
  
  return <div>Count: {count}</div>;
}

// ✅ 正确：使用空依赖数组
function FixedLoop() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    // 只在挂载时执行一次
    console.log('Component mounted');
  }, []); // 空数组
  
  return <div>Count: {count}</div>;
}
```

#### 3.4.2 过时的闭包（Stale Closure）

```jsx
// ❌ 错误：过时的闭包
function Timer() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    const intervalId = setInterval(() => {
      // 这里使用的是创建时的 count 值
      setCount(count + 1);
    }, 1000);
    
    return () => clearInterval(intervalId);
  }, []); // 空数组，count 永远不会更新
    
  return <div>Count: {count}</div>; // 永远显示 1
}

// ✅ 正确：使用函数式更新
function FixedTimer() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    const intervalId = setInterval(() => {
      // 使用前一个状态值
      setCount(prev => prev + 1);
    }, 1000);
    
    return () => clearInterval(intervalId);
  }, []); // 不需要依赖 count
    
  return <div>Count: {count}</div>; // 正常计数
}
```

#### 3.4.3 对象/数组作为依赖项

```jsx
// ❌ 错误：每次渲染都创建新对象
function Component() {
  const [user, setUser] = useState({ name: 'John', age: 30 });
  
  useEffect(() => {
    console.log('user 变化');
  }, [user]); // 每次渲染 user 都是新对象，导致副作用频繁执行
  
  return <div>{user.name}</div>;
}

// ✅ 解决方案1：使用 useMemo
function FixedComponent1() {
  const [user, setUser] = useState({ name: 'John', age: 30 });
  
  const stableUser = useMemo(() => user, [user.name, user.age]);
  
  useEffect(() => {
    console.log('user 变化');
  }, [stableUser]); // 只有 name 或 age 变化时才执行
  
  return <div>{user.name}</div>;
}

// ✅ 解决方案2：提取基本类型值
function FixedComponent2() {
  const [user, setUser] = useState({ name: 'John', age: 30 });
  
  useEffect(() => {
    console.log('user 变化');
  }, [user.name, user.age]); // 直接依赖基本类型
  
  return <div>{user.name}</div>;
}
```

#### 3.4.4 函数作为依赖项

```jsx
// ❌ 错误：每次渲染都创建新函数
function Component() {
  const [count, setCount] = useState(0);
  
  const fetchData = () => {
    console.log('Fetching data for count:', count);
  };
  
  useEffect(() => {
    fetchData();
  }, [fetchData]); // fetchData 每次都是新函数
  
  return <button onClick={() => setCount(count + 1)}>Increment</button>;
}

// ✅ 解决方案1：使用 useCallback
function FixedComponent1() {
  const [count, setCount] = useState(0);
  
  const fetchData = useCallback(() => {
    console.log('Fetching data for count:', count);
  }, [count]); // 依赖 count
  
  useEffect(() => {
    fetchData();
  }, [fetchData]); // 只有 count 变化时 fetchData 才变化
  
  return <button onClick={() => setCount(count + 1)}>Increment</button>;
}

// ✅ 解决方案2：将函数移到 useEffect 内部
function FixedComponent2() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    const fetchData = () => {
      console.log('Fetching data for count:', count);
    };
    
    fetchData();
  }, [count]); // 直接依赖 count
  
  return <button onClick={() => setCount(count + 1)}>Increment</button>;
}
```

### 3.5 依赖数组的最佳实践

#### 3.5.1 使用 ESLint 插件

```json
// .eslintrc.json
{
  "plugins": ["react-hooks"],
  "rules": {
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn"
  }
}
```

#### 3.5.2 依赖项管理策略

```javascript
// 策略1：最小化依赖项
function GoodExample({ userId }) {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    // 只依赖必要的值
    fetchData(userId).then(setData);
  }, [userId]); // 只依赖 userId
  
  return <div>{data}</div>;
}

// 策略2：使用 useRef 存储可变值
function RefExample() {
  const [count, setCount] = useState(0);
  const countRef = useRef(count);
  
  useEffect(() => {
    countRef.current = count;
  });
  
  useEffect(() => {
    const intervalId = setInterval(() => {
      console.log('Current count:', countRef.current);
    }, 1000);
    
    return () => clearInterval(intervalId);
  }, []); // 不需要依赖 count
  
  return <div>Count: {count}</div>;
}

// 策略3：使用自定义 Hook 封装逻辑
function useDocumentTitle(title) {
  useEffect(() => {
    document.title = title;
  }, [title]);
}

function MyComponent() {
  useDocumentTitle('My Page');
  return <div>Content</div>;
}
```

## 四、React Key 的作用与必要性

### 4.1 Key 的基本概念

`key` 是 React 的特殊属性，用于在渲染列表时**唯一标识元素**。它帮助 React 追踪哪些元素发生了变化、被添加或被移除。

```jsx
// 基本用法
const items = [
  { id: 1, text: 'Item 1' },
  { id: 2, text: 'Item 2' },
  { id: 3, text: 'Item 3' }
];

function ItemList() {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id}>{item.text}</li>
      ))}
    </ul>
  );
}
```

### 4.2 为什么列表中必须使用 Key？

#### 4.2.1 性能优化：高效的 Diff 算法

Key 是 React Diff 算法的核心依据：

```javascript
// React Diff 算法简化逻辑
function reconcileChildren(oldChildren, newChildren) {
  const oldKeyMap = new Map();
  
  // 构建 key 到旧元素的映射
  oldChildren.forEach((child, index) => {
    const key = child.key || index;
    oldKeyMap.set(key, child);
  });
  
  // 比较新旧元素
  newChildren.forEach((newChild, newIndex) => {
    const key = newChild.key || newIndex;
    const oldChild = oldKeyMap.get(key);
    
    if (oldChild) {
      // 相同 key 的元素：更新
      updateElement(oldChild, newChild);
    } else {
      // 新 key 的元素：创建
      createElement(newChild);
    }
  });
  
  // 删除不再存在的元素
  oldKeyMap.forEach((oldChild, key) => {
    if (!newChildren.some(newChild => 
      (newChild.key || newChildren.indexOf(newChild)) === key
    )) {
      deleteElement(oldChild);
    }
  });
}
```

#### 4.2.2 状态保持：避免组件状态混乱

当列表项包含内部状态时，key 确保状态不会被错误复用：

```jsx
// ❌ 错误：使用索引作为 key
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map((todo, index) => (
        <li key={index}>
          <input type="text" placeholder="备注" />
          {todo.text}
        </li>
      ))}
    </ul>
  );
}

// 问题：删除第一个 todo 时
// 索引 0 原本对应 "学习 React"，现在对应 "学习 Vue"
// 输入框的状态会被错误绑定到新元素！
```

#### 4.2.3 元素识别：准确判断变化类型

Key 帮助 React 准确判断：
- **添加**：新的 key 出现
- **删除**：key 消失  
- **移动**：key 位置变化
- **更新**：相同 key 的内容变化

### 4.3 Key 的选择策略

#### 4.3.1 理想的 Key 类型

| Key 类型 | 优点 | 缺点 | 适用场景 |
|---------|------|------|----------|
| **数据库 ID** | 绝对唯一、稳定 | 需要后端支持 | 大多数场景 |
| **业务唯一标识** | 业务层面唯一 | 可能变化 | 用户、订单等 |
| **索引** | 简单易用 | 动态列表危险 | 静态列表 |
| **随机值** | 保证唯一 | 性能极差 | 不推荐使用 |

#### 4.3.2 Key 选择算法

```javascript
function getOptimalKey(item, index, context) {
  // 优先级 1：数据库 ID
  if (item.id !== undefined) {
    return `id:${item.id}`;
  }
  
  // 优先级 2：业务唯一标识
  if (item.email) {
    return `email:${item.email}`;
  }
  
  // 优先级 3：组合字段
  if (item.name && item.timestamp) {
    return `composite:${item.name}-${item.timestamp}`;
  }
  
  // 最后手段：索引（仅在静态列表中使用）
  if (context.isStaticList) {
    return `index:${index}`;
  }
  
  // 生成稳定哈希
  return `stable:${hashObject(item)}`;
}
```

### 4.4 Key 的常见误区

#### 4.4.1 误区一：索引总是安全的

```jsx
// ❌ 危险：动态列表使用索引
function DynamicList({ items }) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={index}>{item}</li> // 当 items 变化时会有问题
      ))}
    </ul>
  );
}

// ✅ 正确：静态列表可以使用索引
const STATIC_ITEMS = ['选项1', '选项2', '选项3'];
function StaticList() {
  return (
    <ul>
      {STATIC_ITEMS.map((item, index) => (
        <li key={index}>{item}</li> // 安全：列表永远不会变化
      ))}
    </ul>
  );
}
```

#### 4.4.2 误区二：随机值保证唯一性

```jsx
// ❌ 性能灾难：每次渲染都生成新 key
function BadList({ items }) {
  return (
    <ul>
      {items.map(item => (
        <li key={Math.random()}>{item.text}</li> // 每次渲染都重新创建
      ))}
    </ul>
  );
}
```

## 五、Hooks 与 Key 的协同应用

### 5.1 动态列表的状态管理

```jsx
function DynamicTodoList() {
  const [todos, setTodos] = useState([]);
  const [inputValue, setInputValue] = useState('');
  
  // 添加 todo
  const addTodo = () => {
    if (!inputValue.trim()) return;
    
    const newTodo = {
      id: Date.now(), // 使用时间戳作为唯一 key
      text: inputValue,
      completed: false
    };
    
    setTodos(prev => [...prev, newTodo]);
    setInputValue('');
  };
  
  // 删除 todo
  const deleteTodo = (id) => {
    setTodos(prev => prev.filter(todo => todo.id !== id));
  };
  
  // 切换完成状态
  const toggleTodo = (id) => {
    setTodos(prev => prev.map(todo =>
      todo.id === id 
        ? { ...todo, completed: !todo.completed }
        : todo
    ));
  };
  
  // 使用 useEffect 保存到 localStorage
  useEffect(() => {
    localStorage.setItem('todos', JSON.stringify(todos));
  }, [todos]); // 依赖 todos
  
  return (
    <div>
      <input
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && addTodo()}
      />
      <button onClick={addTodo}>Add</button>
      
      <ul>
        {todos.map(todo => (
          <li key={todo.id}>
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => toggleTodo(todo.id)}
            />
            <span style={{
              textDecoration: todo.completed ? 'line-through' : 'none'
            }}>
              {todo.text}
            </span>
            <button onClick={() => deleteTodo(todo.id)}>
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### 5.2 数据获取与列表渲染

```jsx
function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // 获取用户数据
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/users');
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setUsers(data);
        setError(null);
      } catch (err) {
        setError(err.message);
        console.error('Fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchUsers();
    
    // 清理函数
    return () => {
      console.log('Cleanup user fetch');
    };
  }, []); // 空数组：只在挂载时执行
  
  // 过滤用户
  const [filter, setFilter] = useState('');
  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(filter.toLowerCase())
  );
  
  if (loading) return <div>Loading users...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return (
    <div>
      <input
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        placeholder="Filter users..."
      />
      
      <ul>
        {filteredUsers.map(user => (
          <li key={user.id}>
            <strong>{user.name}</strong> - {user.email}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### 5.3 复杂状态与副作用管理

```jsx
function ChatRoom({ roomId }) {
  const [messages, setMessages] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  
  // 连接聊天室
  useEffect(() => {
    let isMounted = true;
    
    const connect = async () => {
      try {
        setConnectionStatus('connecting');
        
        // 模拟连接
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        if (isMounted) {
          setConnectionStatus('connected');
          console.log(`Connected to room: ${roomId}`);
        }
      } catch (error) {
        if (isMounted) {
          setConnectionStatus('error');
          console.error('Connection error:', error);
        }
      }
    };
    
    connect();
    
    // 清理函数：断开连接
    return () => {
      isMounted = false;
      setConnectionStatus('disconnected');
      console.log(`Disconnected from room: ${roomId}`);
    };
  }, [roomId]); // 依赖 roomId
  
  // 发送消息
  const sendMessage = (text) => {
    const newMessage = {
      id: Date.now(),
      text,
      timestamp: new Date(),
      roomId
    };
    
    setMessages(prev => [...prev, newMessage]);
  };
  
  // 自动滚动到底部
  useEffect(() => {
    if (messages.length > 0) {
      const chatContainer = document.getElementById('chat-container');
      if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
      }
    }
  }, [messages]); // 依赖 messages
  
  return (
    <div>
      <h3>Room: {roomId} ({connectionStatus})</h3>
      
      <div id="chat-container" style={{ height: '300px', overflow: 'auto' }}>
        {messages.map(message => (
          <div key={message.id}>
            <strong>{message.timestamp.toLocaleTimeString()}:</strong>
            {message.text}
          </div>
        ))}
      </div>
      
      <MessageInput onSend={sendMessage} />
    </div>
  );
}
```

## 六、常见问题与解决方案

### 6.1 useState 常见问题

#### 6.1.1 问题：状态更新不同步

```jsx
// ❌ 问题：连续调用 setState 可能不会按预期工作
function Counter() {
  const [count, setCount] = useState(0);
  
  const incrementTwice = () => {
    setCount(count + 1);
    setCount(count + 1); // 这里使用的是当前的 count 值
    // 结果：count 只增加 1，而不是 2
  };
  
  return <button onClick={incrementTwice}>+2</button>;
}

// ✅ 解决方案：使用函数式更新
function FixedCounter() {
  const [count, setCount] = useState(0);
  
  const incrementTwice = () => {
    setCount(prev => prev + 1);
    setCount(prev => prev + 1); // 使用前一个状态值
    // 结果：count 增加 2
  };
  
  return <button onClick={incrementTwice}>+2</button>;
}
```

#### 6.1.2 问题：对象状态更新丢失属性

```jsx
// ❌ 问题：直接修改对象会丢失其他属性
function UserForm() {
  const [user, setUser] = useState({ name: '', email: '', age: 0 });
  
  const updateName = (name) => {
    setUser({ name }); // 丢失了 email 和 age！
  };
  
  return <input value={user.name} onChange={(e) => updateName(e.target.value)} />;
}

// ✅ 解决方案：使用扩展运算符
function FixedUserForm() {
  const [user, setUser] = useState({ name: '', email: '', age: 0 });
  
  const updateName = (name) => {
    setUser(prev => ({
      ...prev, // 保留其他属性
      name     // 更新 name
    }));
  };
  
  return <input value={user.name} onChange={(e) => updateName(e.target.value)} />;
}
```

### 6.2 useEffect 常见问题

#### 6.2.1 问题：依赖项遗漏

```jsx
// ❌ 问题：遗漏依赖项导致过时数据
function Component({ userId }) {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetchData(userId).then(setData);
  }, []); // 遗漏了 userId 依赖
  
  return <div>{data}</div>;
}

// ✅ 解决方案：添加所有依赖项
function FixedComponent({ userId }) {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetchData(userId).then(setData);
  }, [userId]); // 正确依赖 userId
  
  return <div>{data}</div>;
}
```

#### 6.2.2 问题：清理函数执行时机

```jsx
// ❌ 问题：不理解清理函数的执行时机
function Component() {
  useEffect(() => {
    console.log('副作用执行');
    
    return () => {
      console.log('清理函数执行');
    };
  }, []);
  
  return <div>Component</div>;
}

// 执行顺序：
// 1. 组件挂载：副作用执行
// 2. 组件更新：清理函数执行 → 副作用执行
// 3. 组件卸载：清理函数执行
```

### 6.3 Key 常见问题

#### 6.3.1 问题：使用索引导致状态混乱

```jsx
// ❌ 问题：动态列表使用索引
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map((todo, index) => (
        <li key={index}>
          <input type="text" />
          {todo.text}
        </li>
      ))}
    </ul>
  );
}

// ✅ 解决方案：使用唯一标识符
function FixedTodoList({ todos }) {
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>
          <input type="text" />
          {todo.text}
        </li>
      ))}
    </ul>
  );
}
```

## 七、性能优化最佳实践

### 7.1 useState 性能优化

#### 7.1.1 惰性初始化

```jsx
// ✅ 优化：复杂初始状态使用函数
function ExpensiveComponent() {
  const [data, setData] = useState(() => {
    // 复杂计算只在初始渲染时执行一次
    return computeExpensiveValue();
  });
  
  return <div>{data}</div>;
}
```

#### 7.1.2 状态合并

```jsx
// ✅ 优化：合并相关状态
function UserProfile() {
  // 合并相关状态，减少重新渲染
  const [user, setUser] = useState({
    name: '',
    email: '',
    age: 0,
    address: ''
  });
  
  // 而不是分开多个状态
  // const [name, setName] = useState('');
  // const [email, setEmail] = useState('');
  // const [age, setAge] = useState(0);
  // const [address, setAddress] = useState('');
  
  return (
    <form>
      <input
        value={user.name}
        onChange={(e) => setUser(prev => ({ ...prev, name: e.target.value }))}
      />
      {/* 其他输入框 */}
    </form>
  );
}
```

### 7.2 useEffect 性能优化

#### 7.2.1 依赖项优化

```jsx
// ✅ 优化：最小化依赖项
function OptimizedComponent({ userId, filters }) {
  const [data, setData] = useState(null);
  
  // 只依赖必要的值
  useEffect(() => {
    fetchData(userId, filters).then(setData);
  }, [userId, filters.status]); // 只依赖 filters.status，而不是整个 filters 对象
  
  return <div>{data}</div>;
}
```

#### 7.2.2 清理函数优化

```jsx
// ✅ 优化：及时清理资源
function TimerComponent() {
  useEffect(() => {
    const intervalId = setInterval(() => {
      console.log('Tick');
    }, 1000);
    
    // 及时清理，避免内存泄漏
    return () => {
      clearInterval(intervalId);
      console.log('Timer cleaned up');
    };
  }, []);
  
  return <div>Timer</div>;
}
```

### 7.3 Key 性能优化

#### 7.3.1 稳定的 Key

```jsx
// ✅ 优化：使用稳定唯一的 Key
function OptimizedList({ items }) {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id}>{item.text}</li> // 稳定唯一
      ))}
    </ul>
  );
}
```

#### 7.3.2 避免不必要的重新渲染

```jsx
// ✅ 优化：使用 React.memo 配合正确的 Key
const MemoizedItem = React.memo(function Item({ item }) {
  console.log('Item rendered:', item.id);
  return <li>{item.text}</li>;
});

function OptimizedMemoList({ items }) {
  return (
    <ul>
      {items.map(item => (
        <MemoizedItem key={item.id} item={item} />
      ))}
    </ul>
  );
}
```

## 八、总结

### 8.1 核心要点回顾

#### 8.1.1 useState
- 用于在函数组件中添加局部状态
- 返回数组：`[state, setState]`
- 支持惰性初始化和函数式更新
- 状态更新会触发组件重新渲染

#### 8.1.2 useEffect
- 用于处理副作用操作
- 执行时机由依赖数组控制
- 三种模式：空数组、有依赖项、无依赖数组
- 必须正确处理依赖项，避免无限循环和过时闭包

#### 8.1.3 Key
- 用于在列表中唯一标识元素
- 帮助 React 优化 Diff 算法
- 必须使用稳定唯一的标识符
- 避免使用索引（除非列表是静态的）

### 8.2 最佳实践总结

1. **useState**：
   - 合并相关状态，减少重新渲染
   - 使用惰性初始化优化性能
   - 使用函数式更新确保状态正确性

2. **useEffect**：
   - 最小化依赖项
   - 及时清理资源
   - 使用 ESLint 插件检查依赖

3. **Key**：
   - 优先使用数据库 ID
   - 避免使用随机值和索引
   - 确保 Key 在兄弟元素中唯一

### 8.3 学习建议

1. **理解原理**：不要仅仅记忆 API，要理解背后的原理
2. **实践练习**：通过实际项目加深理解
3. **代码审查**：在团队中互相审查 Hooks 和 Key 的使用
4. **持续学习**：关注 React 官方文档和社区最佳实践

### 8.4 工具推荐

1. **ESLint**：`eslint-plugin-react-hooks`
2. **React DevTools**：调试 Hooks 和组件状态
3. **性能分析工具**：React Profiler、Chrome DevTools

---

© 2026 React Hooks 与 Key 深度解析指南