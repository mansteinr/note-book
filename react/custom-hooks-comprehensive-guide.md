# 自定义 Hook 深度解析：概念、创建与最佳实践

## 目录

1. [什么是自定义 Hook？](#什么是自定义-hook)
2. [自定义 Hook 的核心优势](#自定义-hook-的核心优势)
3. [创建自定义 Hook 的基本原则](#创建自定义-hook-的基本原则)
4. [常用自定义 Hook 模式](#常用自定义-hook-模式)
5. [状态管理自定义 Hook](#状态管理自定义-hook)
6. [副作用管理自定义 Hook](#副作用管理自定义-hook)
7. [表单处理自定义 Hook](#表单处理自定义-hook)
8. [API 请求自定义 Hook](#api-请求自定义-hook)
9. [性能优化自定义 Hook](#性能优化自定义-hook)
10. [测试与调试自定义 Hook](#测试与调试自定义-hook)
11. [最佳实践与常见陷阱](#最佳实践与常见陷阱)
12. [实战案例与完整示例](#实战案例与完整示例)
13. [总结与进阶建议](#总结与进阶建议)

## 一、什么是自定义 Hook？

### 1.1 自定义 Hook 的定义

自定义 Hook 是 **React 开发者自己创建的、用于封装和复用组件逻辑的 JavaScript 函数**。它遵循 React Hook 的规则，可以调用其他 Hook（如 useState、useEffect 等）。

```javascript
// 自定义 Hook 的基本结构
function useCustomHook(initialValue) {
  // 可以调用其他 Hook
  const [state, setState] = useState(initialValue);
  
  // 自定义逻辑
  const customFunction = () => {
    // 处理逻辑
  };
  
  // 返回需要暴露的值和函数
  return { state, customFunction };
}

// 在组件中使用自定义 Hook
function MyComponent() {
  const { state, customFunction } = useCustomHook('初始值');
  
  return <div>{state}</div>;
}
```

### 1.2 自定义 Hook 的核心特征

1. **以 `use` 开头**：这是 React 的约定，方便识别和工具检查
2. **可以调用其他 Hook**：可以在自定义 Hook 中使用任何 React 内置 Hook
3. **逻辑复用**：封装可复用的状态逻辑和副作用
4. **独立状态**：每次调用自定义 Hook 都会获得独立的状态副本

### 1.3 与普通函数的区别

```javascript
// ❌ 普通函数：不能使用 React Hook
function regularFunction() {
  // 这里不能调用 useState、useEffect 等 Hook
  return someValue;
}

// ✅ 自定义 Hook：可以使用 React Hook
function useCustomHook() {
  // 这里可以调用任何 React Hook
  const [state, setState] = useState();
  useEffect(() => { /* ... */ });
  
  return state;
}
```

### 1.4 与高阶组件（HOC）和渲染属性（Render Props）的对比

| 特性 | 自定义 Hook | 高阶组件（HOC） | 渲染属性（Render Props） |
|------|------------|----------------|-------------------------|
| **代码结构** | 函数调用 | 组件包装 | 属性传递 |
| **逻辑复用** | 直接复用逻辑 | 通过组件包装复用 | 通过属性复用 |
| **嵌套问题** | 无嵌套 | 可能产生深层嵌套 | 可能产生深层嵌套 |
| **性能影响** | 较小 | 可能增加组件层级 | 可能增加渲染次数 |
| **学习曲线** | 较低 | 中等 | 中等 |
| **TypeScript** | 类型推断好 | 类型定义复杂 | 类型定义中等 |

## 二、自定义 Hook 的核心优势

### 2.1 逻辑复用

```javascript
// 问题：多个组件需要相同的逻辑
function ComponentA() {
  const [count, setCount] = useState(0);
  
  const increment = () => setCount(prev => prev + 1);
  const decrement = () => setCount(prev => prev - 1);
  const reset = () => setCount(0);
  
  return (
    <div>
      <button onClick={decrement}>-</button>
      <span>{count}</span>
      <button onClick={increment}>+</button>
      <button onClick={reset}>重置</button>
    </div>
  );
}

// 同样的逻辑在 ComponentB 中重复...
function ComponentB() {
  const [count, setCount] = useState(0);
  
  const increment = () => setCount(prev => prev + 1);
  const decrement = () => setCount(prev => prev - 1);
  const reset = () => setCount(0);
  
  return (
    <div>
      <button onClick={decrement}>-</button>
      <span>{count}</span>
      <button onClick={increment}>+</button>
      <button onClick={reset}>重置</button>
    </div>
  );
}

// 解决方案：创建自定义 Hook
function useCounter(initialValue = 0) {
  const [count, setCount] = useState(initialValue);
  
  const increment = () => setCount(prev => prev + 1);
  const decrement = () => setCount(prev => prev - 1);
  const reset = () => setCount(initialValue);
  
  return { count, increment, decrement, reset };
}

// 简化后的组件
function ComponentA() {
  const { count, increment, decrement, reset } = useCounter();
  
  return (
    <div>
      <button onClick={decrement}>-</button>
      <span>{count}</span>
      <button onClick={increment}>+</button>
      <button onClick={reset}>重置</button>
    </div>
  );
}

function ComponentB() {
  const { count, increment, decrement, reset } = useCounter(10);
  
  return (
    <div>
      <button onClick={decrement}>-</button>
      <span>{count}</span>
      <button onClick={increment}>+</button>
      <button onClick={reset}>重置</button>
    </div>
  );
}
```

### 2.2 关注点分离

```javascript
// 问题：组件混合了多个关注点
function ComplexComponent({ userId }) {
  // 关注点1：用户数据管理
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // 关注点2：用户设置管理
  const [settings, setSettings] = useState({});
  const [saving, setSaving] = useState(false);
  
  // 关注点3：用户活动记录
  const [activities, setActivities] = useState([]);
  const [page, setPage] = useState(1);
  
  // 混合的副作用
  useEffect(() => {
    fetchUser(userId);
  }, [userId]);
  
  useEffect(() => {
    fetchSettings(userId);
  }, [userId]);
  
  useEffect(() => {
    fetchActivities(userId, page);
  }, [userId, page]);
  
  // 混合的业务逻辑
  const fetchUser = async (id) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/users/${id}`);
      const data = await response.json();
      setUser(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  // ... 更多混合的逻辑
  
  return (
    <div>
      {/* 混合的 UI 渲染 */}
    </div>
  );
}

// 解决方案：使用自定义 Hook 分离关注点
function useUser(userId) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    fetchUser(userId);
  }, [userId]);
  
  const fetchUser = async (id) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/users/${id}`);
      const data = await response.json();
      setUser(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return { user, loading, error, refetch: () => fetchUser(userId) };
}

function useUserSettings(userId) {
  const [settings, setSettings] = useState({});
  const [saving, setSaving] = useState(false);
  
  // ... 设置相关逻辑
  
  return { settings, saving, updateSettings };
}

function useUserActivities(userId) {
  const [activities, setActivities] = useState([]);
  const [page, setPage] = useState(1);
  
  // ... 活动相关逻辑
  
  return { activities, page, setPage, loadMore };
}

// 简化后的组件
function SimplifiedComponent({ userId }) {
  const { user, loading, error } = useUser(userId);
  const { settings, saving } = useUserSettings(userId);
  const { activities, page, setPage } = useUserActivities(userId);
  
  if (loading) return <div>加载中...</div>;
  if (error) return <div>错误: {error}</div>;
  
  return (
    <div>
      <UserProfile user={user} settings={settings} />
      <ActivitiesList activities={activities} />
      <Pagination page={page} setPage={setPage} />
    </div>
  );
}
```

### 2.3 可测试性

```javascript
// 自定义 Hook 可以独立测试
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

test('useCounter 应该正常工作', () => {
  const { result } = renderHook(() => useCounter(0));
  
  // 测试初始值
  expect(result.current.count).toBe(0);
  
  // 测试 increment
  act(() => {
    result.current.increment();
  });
  expect(result.current.count).toBe(1);
  
  // 测试 decrement
  act(() => {
    result.current.decrement();
  });
  expect(result.current.count).toBe(0);
  
  // 测试 reset
  act(() => {
    result.current.increment();
    result.current.increment();
    result.current.reset();
  });
  expect(result.current.count).toBe(0);
});
```

### 2.4 代码可维护性

1. **单一职责**：每个自定义 Hook 专注于一个特定功能
2. **易于理解**：通过 Hook 名称即可了解其功能
3. **易于修改**：修改逻辑只需在一个地方进行
4. **易于删除**：删除功能只需移除对应的 Hook 调用

## 三、创建自定义 Hook 的基本原则

### 3.1 命名约定

```javascript
// ✅ 正确：以 "use" 开头，使用驼峰命名
function useCounter() { /* ... */ }
function useFetchData() { /* ... */ }
function useLocalStorage() { /* ... */ }

// ❌ 错误：不以 "use" 开头
function counter() { /* ... */ }
function fetchDataHook() { /* ... */ }

// ✅ 正确：描述性名称
function useUserAuthentication() { /* ... */ }
function useFormValidation() { /* ... */ }
function useInfiniteScroll() { /* ... */ }
```

### 3.2 参数设计

```javascript
// ✅ 正确：清晰的参数设计
function useFetch(url, options = {}) {
  const { method = 'GET', headers = {} } = options;
  // ...
}

// ✅ 正确：使用配置对象
function useTimer(config = {}) {
  const {
    initialTime = 0,
    interval = 1000,
    autoStart = false
  } = config;
  // ...
}

// ❌ 错误：参数过多
function useComplexHook(param1, param2, param3, param4, param5) {
  // 难以使用和维护
}

// ✅ 正确：使用对象参数
function useComplexHook(options) {
  const { param1, param2, param3, param4, param5 } = options;
  // 更清晰
}
```

### 3.3 返回值设计

```javascript
// ✅ 正确：返回对象，便于解构
function useCounter(initialValue = 0) {
  const [count, setCount] = useState(initialValue);
  
  const increment = () => setCount(prev => prev + 1);
  const decrement = () => setCount(prev => prev - 1);
  const reset = () => setCount(initialValue);
  
  return {
    count,
    increment,
    decrement,
    reset,
    setCount // 暴露原始 setter 以供灵活使用
  };
}

// ✅ 正确：返回数组，模仿 useState
function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue);
  
  const toggle = () => setValue(prev => !prev);
  
  return [value, toggle, setValue];
}

// 使用示例
const [isOn, toggleIsOn] = useToggle(false);

// ❌ 错误：返回不一致的类型
function useInconsistentHook() {
  const [value, setValue] = useState('');
  const [count, setCount] = useState(0);
  
  // 返回混合类型，难以使用
  return [value, setValue, count, setCount];
}
```

### 3.4 依赖管理

```javascript
// ✅ 正确：正确处理依赖
function useFetch(url, options) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    let isMounted = true;
    
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await fetch(url, options);
        const result = await response.json();
        
        if (isMounted) {
          setData(result);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };
    
    fetchData();
    
    return () => {
      isMounted = false;
    };
  }, [url, options]); // 正确声明依赖
  
  return { data, loading, error };
}

// ❌ 错误：遗漏依赖
function useProblematicFetch(url) {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(setData);
  }, []); // 遗漏了 url 依赖，url 变化时不会重新获取
  
  return data;
}
```

### 3.5 错误处理

```javascript
// ✅ 正确：完善的错误处理
function useSafeFetch(url) {
  const [state, setState] = useState({
    data: null,
    loading: true,
    error: null
  });
  
  useEffect(() => {
    let isMounted = true;
    
    const fetchData = async () => {
      try {
        setState(prev => ({ ...prev, loading: true, error: null }));
        
        const response = await fetch(url);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (isMounted) {
          setState({
            data,
            loading: false,
            error: null
          });
        }
      } catch (error) {
        if (isMounted) {
          setState({
            data: null,
            loading: false,
            error: error.message
          });
        }
      }
    };
    
    fetchData();
    
    return () => {
      isMounted = false;
    };
  }, [url]);
  
  return state;
}
```

## 四、常用自定义 Hook 模式

### 4.1 状态管理 Hook

```javascript
// useToggle：切换布尔值
function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue);
  
  const toggle = useCallback(() => {
    setValue(prev => !prev);
  }, []);
  
  const setOn = useCallback(() => {
    setValue(true);
  }, []);
  
  const setOff = useCallback(() => {
    setValue(false);
  }, []);
  
  return [value, toggle, setOn, setOff];
}

// 使用示例
function ToggleComponent() {
  const [isDarkMode, toggleDarkMode] = useToggle(false);
  
  return (
    <button onClick={toggleDarkMode}>
      {isDarkMode ? '切换到浅色模式' : '切换到深色模式'}
    </button>
  );
}
```

### 4.2 表单处理 Hook

```javascript
// useForm：表单状态管理
function useForm(initialValues = {}, validate) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // 处理字段变化
  const handleChange = useCallback((name, value) => {
    setValues(prev => ({
      ...prev,
      [name]: value
    }));
    
    // 实时验证
    if (validate) {
      const error = validate[name] ? validate[name](value) : null;
      setErrors(prev => ({
        ...prev,
        [name]: error
      }));
    }
  }, [validate]);
  
  // 处理字段失去焦点
  const handleBlur = useCallback((name) => {
    setTouched(prev => ({
      ...prev,
      [name]: true
    }));
  }, []);
  
  // 处理表单提交
  const handleSubmit = useCallback((onSubmit) => async (event) => {
    event.preventDefault();
    
    setIsSubmitting(true);
    
    // 验证所有字段
    if (validate) {
      const newErrors = {};
      Object.keys(values).forEach(key => {
        const validator = validate[key];
        if (validator) {
          const error = validator(values[key]);
          if (error) newErrors[key] = error;
        }
      });
      
      setErrors(newErrors);
      setTouched(
        Object.keys(values).reduce((acc, key) => {
          acc[key] = true;
          return acc;
        }, {})
      );
      
      if (Object.keys(newErrors).length > 0) {
        setIsSubmitting(false);
        return;
      }
    }
    
    try {
      await onSubmit(values);
    } finally {
      setIsSubmitting(false);
    }
  }, [values, validate]);
  
  // 重置表单
  const resetForm = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  }, [initialValues]);
  
  return {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    resetForm,
    setValues
  };
}

// 使用示例
function LoginForm() {
  const { values, errors, touched, handleChange, handleBlur, handleSubmit } = useForm(
    { email: '', password: '' },
    {
      email: (value) => !value ? '邮箱不能为空' : !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) ? '邮箱格式不正确' : null,
      password: (value) => !value ? '密码不能为空' : value.length < 6 ? '密码至少6位' : null
    }
  );
  
  const onSubmit = async (formValues) => {
    console.log('提交:', formValues);
    // 调用 API
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <input
          type="email"
          name="email"
          value={values.email}
          onChange={(e) => handleChange('email', e.target.value)}
          onBlur={() => handleBlur('email')}
          placeholder="邮箱"
        />
        {touched.email && errors.email && <span>{errors.email}</span>}
      </div>
      
      <div>
        <input
          type="password"
          name="password"
          value={values.password}
          onChange={(e) => handleChange('password', e.target.value)}
          onBlur={() => handleBlur('password')}
          placeholder="密码"
        />
        {touched.password && errors.password && <span>{errors.password}</span>}
      </div>
      
      <button type="submit">登录</button>
    </form>
  );
}
```

### 4.3 副作用管理 Hook

```javascript
// useInterval：定时器 Hook
function useInterval(callback, delay) {
  const savedCallback = useRef();
  
  // 保存最新的回调函数
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);
  
  // 设置定时器
  useEffect(() => {
    function tick() {
      savedCallback.current?.();
    }
    
    if (delay !== null) {
      const id = setInterval(tick, delay);
      return () => clearInterval(id);
    }
  }, [delay]);
}

// 使用示例
function Timer() {
  const [count, setCount] = useState(0);
  
  useInterval(() => {
    setCount(count + 1);
  }, 1000);
  
  return <div>计时: {count} 秒</div>;
}

// useDebounce：防抖 Hook
function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    
    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);
  
  return debouncedValue;
}

// 使用示例
function SearchInput() {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 500);
  
  // debouncedQuery 会在用户停止输入 500ms 后更新
  useEffect(() => {
    if (debouncedQuery) {
      // 执行搜索
      search(debouncedQuery);
    }
  }, [debouncedQuery]);
  
  return (
    <input
      type="text"
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="搜索..."
    />
  );
}
```

### 4.4 浏览器 API Hook

```javascript
// useLocalStorage：本地存储 Hook
function useLocalStorage(key, initialValue) {
  // 从 localStorage 读取初始值
  const readValue = useCallback(() => {
    if (typeof window === 'undefined') {
      return initialValue;
    }
    
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`读取 localStorage 键 "${key}" 时出错:`, error);
      return initialValue;
    }
  }, [key, initialValue]);
  
  const [storedValue, setStoredValue] = useState(readValue);
  
  // 设置 localStorage 值
  const setValue = useCallback((value) => {
    try {
      // 允许值是一个函数（像 useState 一样）
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      
      setStoredValue(valueToStore);
      
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.warn(`设置 localStorage 键 "${key}" 时出错:`, error);
    }
  }, [key, storedValue]);
  
  // 监听其他标签页的更改
  useEffect(() => {
    const handleStorageChange = (event) => {
      if (event.key === key && event.storageArea === localStorage) {
        setStoredValue(readValue());
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [key, readValue]);
  
  return [storedValue, setValue];
}

// 使用示例
function ThemeToggle() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');
  
  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };
  
  return (
    <button onClick={toggleTheme}>
      切换到 {theme === 'light' ? '深色' : '浅色'} 主题
    </button>
  );
}

// useMediaQuery：媒体查询 Hook
function useMediaQuery(query) {
  const [matches, setMatches] = useState(false);
  
  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    
    // 初始检查
    setMatches(mediaQuery.matches);
    
    // 监听变化
    const handler = (event) => {
      setMatches(event.matches);
    };
    
    mediaQuery.addEventListener('change', handler);
    
    return () => {
      mediaQuery.removeEventListener('change', handler);
    };
  }, [query]);
  
  return matches;
}

// 使用示例
function ResponsiveComponent() {
  const isMobile = useMediaQuery('(max-width: 768px)');
  const isTablet = useMediaQuery('(min-width: 769px) and (max-width: 1024px)');
  const isDesktop = useMediaQuery('(min-width: 1025px)');
  
  if (isMobile) return <MobileLayout />;
  if (isTablet) return <TabletLayout />;
  return <DesktopLayout />;
}
```

## 五、状态管理自定义 Hook

### 5.1 useReducer 增强 Hook

```javascript
// useReducerWithMiddleware：支持中间件的 useReducer
function useReducerWithMiddleware(reducer, initialState, middlewares = []) {
  const [state, setState] = useState(initialState);
  
  const dispatch = useCallback((action) => {
    // 应用中间件
    const chain = middlewares.map(middleware => middleware({ getState: () => state }));
    
    // 创建增强的 dispatch
    let enhancedDispatch = (action) => {
      const newState = reducer(state, action);
      setState(newState);
      return action;
    };
    
    // 从右到左组合中间件
    for (let i = chain.length - 1; i >= 0; i--) {
      enhancedDispatch = chain[i](enhancedDispatch);
    }
    
    // 执行 action
    return enhancedDispatch(action);
  }, [reducer, state, middlewares]);
  
  return [state, dispatch];
}

// 使用示例
const loggerMiddleware = ({ getState }) => next => action => {
  console.log('即将执行:', action);
  console.log('当前状态:', getState());
  
  const result = next(action);
  
  console.log('执行后状态:', getState());
  return result;
};

const thunkMiddleware = ({ getState }) => next => action => {
  if (typeof action === 'function') {
    return action(next, getState);
  }
  return next(action);
};

function counterReducer(state, action) {
  switch (action.type) {
    case 'INCREMENT':
      return { count: state.count + 1 };
    case 'DECREMENT':
      return { count: state.count - 1 };
    case 'RESET':
      return { count: 0 };
    default:
      return state;
  }
}

function CounterWithMiddleware() {
  const [state, dispatch] = useReducerWithMiddleware(
    counterReducer,
    { count: 0 },
    [loggerMiddleware, thunkMiddleware]
  );
  
  // 可以 dispatch 普通 action
  const increment = () => dispatch({ type: 'INCREMENT' });
  
  // 也可以 dispatch 函数（thunk）
  const incrementAsync = () => dispatch((dispatch, getState) => {
    setTimeout(() => {
      dispatch({ type: 'INCREMENT' });
    }, 1000);
  });
  
  return (
    <div>
      <p>计数: {state.count}</p>
      <button onClick={increment}>增加</button>
      <button onClick={incrementAsync}>异步增加</button>
    </div>
  );
}
```

### 5.2 全局状态管理 Hook

```javascript
// createGlobalState：创建全局状态 Hook
function createGlobalState(initialState) {
  let state = initialState;
  const listeners = new Set();
  
  const setState = (newState) => {
    // 支持函数更新
    if (typeof newState === 'function') {
      state = newState(state);
    } else {
      state = newState;
    }
    
    // 通知所有监听器
    listeners.forEach(listener => listener(state));
  };
  
  const useGlobalState = () => {
    const [localState, setLocalState] = useState(state);
    
    useEffect(() => {
      const listener = (newState) => {
        setLocalState(newState);
      };
      
      listeners.add(listener);
      
      return () => {
        listeners.delete(listener);
      };
    }, []);
    
    return [localState, setState];
  };
  
  return useGlobalState;
}

// 使用示例
const useCounterState = createGlobalState({ count: 0 });

function CounterA() {
  const [state, setState] = useCounterState();
  
  return (
    <div>
      <p>CounterA: {state.count}</p>
      <button onClick={() => setState({ count: state.count + 1 })}>
        增加
      </button>
    </div>
  );
}

function CounterB() {
  const [state] = useCounterState();
  
  return (
    <div>
      <p>CounterB: {state.count}</p>
      {/* 共享同一个状态 */}
    </div>
  );
}

function App() {
  return (
    <div>
      <CounterA />
      <CounterB />
    </div>
  );
}
```

### 5.3 状态持久化 Hook

```javascript
// usePersistedState：持久化状态 Hook
function usePersistedState(key, initialValue, storage = localStorage) {
  const [state, setState] = useState(() => {
    try {
      const item = storage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`读取存储键 "${key}" 时出错:`, error);
      return initialValue;
    }
  });
  
  // 状态变化时保存到存储
  useEffect(() => {
    try {
      storage.setItem(key, JSON.stringify(state));
    } catch (error) {
      console.error(`保存存储键 "${key}" 时出错:`, error);
    }
  }, [key, state, storage]);
  
  // 监听存储变化（其他标签页）
  useEffect(() => {
    const handleStorageChange = (event) => {
      if (event.key === key && event.storageArea === storage) {
        try {
          const newValue = event.newValue ? JSON.parse(event.newValue) : initialValue;
          setState(newValue);
        } catch (error) {
          console.error(`解析存储键 "${key}" 时出错:`, error);
        }
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [key, initialValue, storage]);
  
  return [state, setState];
}

// 使用示例
function UserPreferences() {
  const [theme, setTheme] = usePersistedState('theme', 'light');
  const [language, setLanguage] = usePersistedState('language', 'zh-CN');
  const [notifications, setNotifications] = usePersistedState('notifications', true);
  
  return (
    <div>
      <h2>用户偏好设置</h2>
      
      <div>
        <label>
          主题:
          <select value={theme} onChange={(e) => setTheme(e.target.value)}>
            <option value="light">浅色</option>
            <option value="dark">深色</option>
            <option value="auto">自动</option>
          </select>
        </label>
      </div>
      
      <div>
        <label>
          语言:
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="zh-CN">简体中文</option>
            <option value="en-US">English</option>
            <option value="ja-JP">日本語</option>
          </select>
        </label>
      </div>
      
      <div>
        <label>
          <input
            type="checkbox"
            checked={notifications}
            onChange={(e) => setNotifications(e.target.checked)}
          />
          接收通知
        </label>
      </div>
    </div>
  );
}
```

## 六、副作用管理自定义 Hook

### 6.1 网络请求 Hook

```javascript
// useFetch：增强版网络请求 Hook
function useFetch(url, options = {}) {
  const {
    method = 'GET',
    headers = {},
    body = null,
    immediate = true,
    onSuccess,
    onError
  } = options;
  
  const [state, setState] = useState({
    data: null,
    loading: false,
    error: null,
    status: null
  });
  
  const [trigger, setTrigger] = useState(0);
  
  const execute = useCallback(async (overrides = {}) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const finalUrl = overrides.url || url;
      const finalMethod = overrides.method || method;
      const finalHeaders = { ...headers, ...overrides.headers };
      const finalBody = overrides.body !== undefined ? overrides.body : body;
      
      const response = await fetch(finalUrl, {
        method: finalMethod,
        headers: finalHeaders,
        body: finalBody ? JSON.stringify(finalBody) : null
      });
      
      const data = await response.json();
      
      setState({
        data,
        loading: false,
        error: null,
        status: response.status
      });
      
      if (onSuccess) {
        onSuccess(data, response);
      }
      
      return { data, response };
    } catch (error) {
      setState({
        data: null,
        loading: false,
        error: error.message,
        status: null
      });
      
      if (onError) {
        onError(error);
      }
      
      throw error;
    }
  }, [url, method, headers, body, onSuccess, onError]);
  
  // 手动触发请求
  const refetch = useCallback((overrides = {}) => {
    setTrigger(prev => prev + 1);
    return execute(overrides);
  }, [execute]);
  
  // 自动执行请求
  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate, trigger]);
  
  return {
    ...state,
    execute,
    refetch,
    setData: (data) => setState(prev => ({ ...prev, data }))
  };
}

// 使用示例
function UserProfile({ userId }) {
  const { data: user, loading, error, refetch } = useFetch(
    `/api/users/${userId}`,
    {
      onSuccess: (data) => {
        console.log('用户数据加载成功:', data);
      },
      onError: (error) => {
        console.error('用户数据加载失败:', error);
      }
    }
  );
  
  if (loading) return <div>加载中...</div>;
  if (error) return <div>错误: {error}</div>;
  if (!user) return <div>无用户数据</div>;
  
  return (
    <div>
      <h2>{user.name}</h2>
      <p>邮箱: {user.email}</p>
      <p>角色: {user.role}</p>
      <button onClick={refetch}>刷新数据</button>
    </div>
  );
}
```

### 6.2 WebSocket Hook

```javascript
// useWebSocket：WebSocket 连接 Hook
function useWebSocket(url, options = {}) {
  const {
    reconnect = true,
    reconnectInterval = 3000,
    reconnectAttempts = 5,
    onOpen,
    onMessage,
    onClose,
    onError
  } = options;
  
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [reconnectCount, setReconnectCount] = useState(0);
  
  const connect = useCallback(() => {
    const ws = new WebSocket(url);
    
    ws.onopen = (event) => {
      setIsConnected(true);
      setReconnectCount(0);
      if (onOpen) onOpen(event);
    };
    
    ws.onmessage = (event) => {
      if (onMessage) onMessage(event);
    };
    
    ws.onclose = (event) => {
      setIsConnected(false);
      if (onClose) onClose(event);
      
      // 自动重连
      if (reconnect && reconnectCount < reconnectAttempts) {
        setTimeout(() => {
          setReconnectCount(prev => prev + 1);
          connect();
        }, reconnectInterval);
      }
    };
    
    ws.onerror = (event) => {
      if (onError) onError(event);
    };
    
    setSocket(ws);
    
    return ws;
  }, [url, reconnect, reconnectInterval, reconnectAttempts, onOpen, onMessage, onClose, onError, reconnectCount]);
  
  // 发送消息
  const send = useCallback((data) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(typeof data === 'string' ? data : JSON.stringify(data));
      return true;
    }
    return false;
  }, [socket]);
  
  // 关闭连接
  const disconnect = useCallback(() => {
    if (socket) {
      socket.close();
    }
  }, [socket]);
  
  // 初始连接
  useEffect(() => {
    const ws = connect();
    
    return () => {
      ws.close();
    };
  }, [connect]);
  
  return {
    socket,
    isConnected,
    send,
    disconnect,
    reconnectCount
  };
}

// 使用示例
function ChatRoom({ roomId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  
  const { isConnected, send } = useWebSocket(
    `wss://api.example.com/chat/${roomId}`,
    {
      onMessage: (event) => {
        const message = JSON.parse(event.data);
        setMessages(prev => [...prev, message]);
      },
      onOpen: () => {
        console.log('已连接到聊天室');
      },
      onClose: () => {
        console.log('已断开连接');
      }
    }
  );
  
  const handleSend = () => {
    if (input.trim() && send) {
      send({
        type: 'message',
        content: input,
        timestamp: new Date().toISOString()
      });
      setInput('');
    }
  };
  
  return (
    <div>
      <div>连接状态: {isConnected ? '已连接' : '连接中...'}</div>
      
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className="message">
            <span>{msg.content}</span>
          </div>
        ))}
      </div>
      
      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="输入消息..."
        />
        <button onClick={handleSend} disabled={!isConnected}>
          发送
        </button>
      </div>
    </div>
  );
}
```

### 6.3 定时器与动画 Hook

```javascript
// useAnimationFrame：动画帧 Hook
function useAnimationFrame(callback) {
  const requestRef = useRef();
  const previousTimeRef = useRef();
  
  const animate = useCallback((time) => {
    if (previousTimeRef.current !== undefined) {
      const deltaTime = time - previousTimeRef.current;
      callback(deltaTime);
    }
    
    previousTimeRef.current = time;
    requestRef.current = requestAnimationFrame(animate);
  }, [callback]);
  
  useEffect(() => {
    requestRef.current = requestAnimationFrame(animate);
    
    return () => {
      cancelAnimationFrame(requestRef.current);
    };
  }, [animate]);
}

// 使用示例：平滑滚动动画
function SmoothScroll({ targetY, duration = 500 }) {
  const [position, setPosition] = useState(0);
  
  useAnimationFrame((deltaTime) => {
    const progress = Math.min(1, (Date.now() - startTime) / duration);
    const easedProgress = easeInOutCubic(progress);
    
    const newPosition = startPosition + (targetY - startPosition) * easedProgress;
    setPosition(newPosition);
    
    if (progress >= 1) {
      // 动画完成
    }
  });
  
  return (
    <div style={{ transform: `translateY(${position}px)` }}>
      {/* 内容 */}
    </div>
  );
}

// useCountdown：倒计时 Hook
function useCountdown(initialSeconds, onComplete) {
  const [seconds, setSeconds] = useState(initialSeconds);
  const [isActive, setIsActive] = useState(false);
  
  useEffect(() => {
    let interval = null;
    
    if (isActive && seconds > 0) {
      interval = setInterval(() => {
        setSeconds(prev => {
          if (prev <= 1) {
            setIsActive(false);
            if (onComplete) onComplete();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } else if (!isActive && seconds !== 0) {
      clearInterval(interval);
    }
    
    return () => clearInterval(interval);
  }, [isActive, seconds, onComplete]);
  
  const start = useCallback(() => {
    setIsActive(true);
  }, []);
  
  const pause = useCallback(() => {
    setIsActive(false);
  }, []);
  
  const reset = useCallback(() => {
    setIsActive(false);
    setSeconds(initialSeconds);
  }, [initialSeconds]);
  
  const resume = useCallback(() => {
    setIsActive(true);
  }, []);
  
  return {
    seconds,
    isActive,
    start,
    pause,
    reset,
    resume,
    formatted: `${Math.floor(seconds / 60)}:${(seconds % 60).toString().padStart(2, '0')}`
  };
}

// 使用示例
function CountdownTimer() {
  const { seconds, isActive, start, pause, reset, formatted } = useCountdown(
    300, // 5分钟
    () => {
      console.log('倒计时结束!');
    }
  );
  
  return (
    <div>
      <h2>倒计时: {formatted}</h2>
      
      <div>
        {!isActive ? (
          <button onClick={start}>开始</button>
        ) : (
          <button onClick={pause}>暂停</button>
        )}
        
        <button onClick={reset} disabled={seconds === 300}>
          重置
        </button>
      </div>
    </div>
  );
}
```

## 七、表单处理自定义 Hook

### 7.1 复杂表单验证 Hook

```javascript
// useFormValidation：增强表单验证 Hook
function useFormValidation(initialValues, validationSchema, options = {}) {
  const {
    validateOnChange = true,
    validateOnBlur = true,
    validateOnSubmit = true
  } = options;
  
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitCount, setSubmitCount] = useState(0);
  
  // 验证单个字段
  const validateField = useCallback((name, value) => {
    if (!validationSchema || !validationSchema[name]) {
      return null;
    }
    
    const validator = validationSchema[name];
    
    // 支持同步和异步验证器
    if (typeof validator === 'function') {
      return validator(value, values);
    }
    
    // 支持验证规则对象
    if (typeof validator === 'object') {
      const rules = validator;
      let error = null;
      
      // 必填验证
      if (rules.required && !value) {
        error = rules.requiredMessage || '此字段为必填项';
      }
      
      // 最小长度验证
      if (!error && rules.minLength && value.length < rules.minLength) {
        error = rules.minLengthMessage || `至少需要 ${rules.minLength} 个字符`;
      }
      
      // 最大长度验证
      if (!error && rules.maxLength && value.length > rules.maxLength) {
        error = rules.maxLengthMessage || `不能超过 ${rules.maxLength} 个字符`;
      }
      
      // 正则表达式验证
      if (!error && rules.pattern && !rules.pattern.test(value)) {
        error = rules.patternMessage || '格式不正确';
      }
      
      // 自定义验证函数
      if (!error && rules.validate) {
        const customError = rules.validate(value, values);
        if (customError) error = customError;
      }
      
      return error;
    }
    
    return null;
  }, [validationSchema, values]);
  
  // 验证所有字段
  const validateAll = useCallback(async () => {
    const newErrors = {};
    
    for (const [name, value] of Object.entries(values)) {
      const error = validateField(name, value);
      
      if (error && typeof error.then === 'function') {
        // 异步验证
        try {
          const asyncError = await error;
          if (asyncError) newErrors[name] = asyncError;
        } catch (err) {
          newErrors[name] = err.message;
        }
      } else if (error) {
        // 同步验证
        newErrors[name] = error;
      }
    }
    
    setErrors(newErrors);
    return newErrors;
  }, [values, validateField]);
  
  // 处理字段变化
  const handleChange = useCallback((name, value) => {
    setValues(prev => ({
      ...prev,
      [name]: value
    }));
    
    // 标记为已触摸
    setTouched(prev => ({
      ...prev,
      [name]: true
    }));
    
    // 实时验证
    if (validateOnChange) {
      const error = validateField(name, value);
      setErrors(prev => ({
        ...prev,
        [name]: error
      }));
    }
  }, [validateField, validateOnChange]);
  
  // 处理字段失去焦点
  const handleBlur = useCallback((name) => {
    setTouched(prev => ({
      ...prev,
      [name]: true
    }));
    
    // 失去焦点时验证
    if (validateOnBlur) {
      const error = validateField(name, values[name]);
      setErrors(prev => ({
        ...prev,
        [name]: error
      }));
    }
  }, [validateField, validateOnBlur, values]);
  
  // 处理表单提交
  const handleSubmit = useCallback((onSubmit) => async (event) => {
    if (event) event.preventDefault();
    
    setIsSubmitting(true);
    setSubmitCount(prev => prev + 1);
    
    // 标记所有字段为已触摸
    const allTouched = Object.keys(values).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {});
    setTouched(allTouched);
    
    // 验证所有字段
    let validationErrors = {};
    if (validateOnSubmit) {
      validationErrors = await validateAll();
    }
    
    // 如果有错误，停止提交
    if (Object.keys(validationErrors).length > 0) {
      setIsSubmitting(false);
      return { success: false, errors: validationErrors };
    }
    
    // 执行提交
    try {
      const result = await onSubmit(values);
      setIsSubmitting(false);
      return { success: true, data: result, errors: {} };
    } catch (error) {
      setIsSubmitting(false);
      return { success: false, error: error.message, errors: {} };
    }
  }, [values, validateOnSubmit, validateAll]);
  
  // 重置表单
  const resetForm = useCallback((newValues = initialValues) => {
    setValues(newValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  }, [initialValues]);
  
  // 设置字段值（用于编程式设置）
  const setFieldValue = useCallback((name, value) => {
    handleChange(name, value);
  }, [handleChange]);
  
  // 设置字段错误（用于服务器验证错误）
  const setFieldError = useCallback((name, error) => {
    setErrors(prev => ({
      ...prev,
      [name]: error
    }));
  }, []);
  
  // 检查表单是否有效
  const isValid = Object.keys(errors).length === 0;
  
  // 检查表单是否被修改过
  const isDirty = !deepEqual(values, initialValues);
  
  return {
    // 状态
    values,
    errors,
    touched,
    isSubmitting,
    submitCount,
    
    // 验证状态
    isValid,
    isDirty,
    
    // 操作方法
    handleChange,
    handleBlur,
    handleSubmit,
    resetForm,
    setFieldValue,
    setFieldError,
    validateField,
    validateAll,
    
    // 原始 setter（高级用法）
    setValues,
    setErrors,
    setTouched
  };
}

// 使用示例：注册表单
function RegistrationForm() {
  const {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit
  } = useFormValidation(
    {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      agreeToTerms: false
    },
    {
      username: {
        required: true,
        minLength: 3,
        maxLength: 20,
        pattern: /^[a-zA-Z0-9_]+$/,
        patternMessage: '只能包含字母、数字和下划线'
      },
      email: {
        required: true,
        pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        patternMessage: '请输入有效的邮箱地址'
      },
      password: {
        required: true,
        minLength: 8,
        validate: (value) => {
          if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value)) {
            return '必须包含大小写字母和数字';
          }
          return null;
        }
      },
      confirmPassword: {
        required: true,
        validate: (value, values) => {
          if (value !== values.password) {
            return '两次输入的密码不一致';
          }
          return null;
        }
      },
      agreeToTerms: {
        required: true,
        validate: (value) => {
          if (!value) {
            return '必须同意服务条款';
          }
          return null;
        }
      }
    },
    {
      validateOnChange: true,
      validateOnBlur: true
    }
  );
  
  const onSubmit = async (formValues) => {
    console.log('提交注册:', formValues);
    // 调用注册 API
    const response = await fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formValues)
    });
    
    if (!response.ok) {
      throw new Error('注册失败');
    }
    
    return response.json();
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div className="form-group">
        <label>用户名</label>
        <input
          type="text"
          name="username"
          value={values.username}
          onChange={(e) => handleChange('username', e.target.value)}
          onBlur={() => handleBlur('username')}
          className={touched.username && errors.username ? 'error' : ''}
        />
        {touched.username && errors.username && (
          <div className="error-message">{errors.username}</div>
        )}
      </div>
      
      <div className="form-group">
        <label>邮箱</label>
        <input
          type="email"
          name="email"
          value={values.email}
          onChange={(e) => handleChange('email', e.target.value)}
          onBlur={() => handleBlur('email')}
          className={touched.email && errors.email ? 'error' : ''}
        />
        {touched.email && errors.email && (
          <div className="error-message">{errors.email}</div>
        )}
      </div>
      
      <div className="form-group">
        <label>密码</label>
        <input
          type="password"
          name="password"
          value={values.password}
          onChange={(e) => handleChange('password', e.target.value)}
          onBlur={() => handleBlur('password')}
          className={touched.password && errors.password ? 'error' : ''}
        />
        {touched.password && errors.password && (
          <div className="error-message">{errors.password}</div>
        )}
      </div>
      
      <div className="form-group">
        <label>确认密码</label>
        <input
          type="password"
          name="confirmPassword"
          value={values.confirmPassword}
          onChange={(e) => handleChange('confirmPassword', e.target.value)}
          onBlur={() => handleBlur('confirmPassword')}
          className={touched.confirmPassword && errors.confirmPassword ? 'error' : ''}
        />
        {touched.confirmPassword && errors.confirmPassword && (
          <div className="error-message">{errors.confirmPassword}</div>
        )}
      </div>
      
      <div className="form-group">
        <label>
          <input
            type="checkbox"
            name="agreeToTerms"
            checked={values.agreeToTerms}
            onChange={(e) => handleChange('agreeToTerms', e.target.checked)}
          />
          我同意服务条款
        </label>
        {touched.agreeToTerms && errors.agreeToTerms && (
          <div className="error-message">{errors.agreeToTerms}</div>
        )}
      </div>
      
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? '注册中...' : '注册'}
      </button>
    </form>
  );
}
```

### 7.2 动态表单 Hook

```javascript
// useDynamicForm：动态表单字段管理
function useDynamicForm(initialFields = []) {
  const [fields, setFields] = useState(initialFields);
  const [values, setValues] = useState({});
  const [errors, setErrors] = useState({});
  
  // 初始化值
  useEffect(() => {
    const initialValues = {};
    fields.forEach(field => {
      initialValues[field.name] = field.initialValue || '';
    });
    setValues(initialValues);
  }, [fields]);
  
  // 添加字段
  const addField = useCallback((field) => {
    setFields(prev => [...prev, field]);
    setValues(prev => ({
      ...prev,
      [field.name]: field.initialValue || ''
    }));
  }, []);
  
  // 移除字段
  const removeField = useCallback((fieldName) => {
    setFields(prev => prev.filter(field => field.name !== fieldName));
    setValues(prev => {
      const newValues = { ...prev };
      delete newValues[fieldName];
      return newValues;
    });
    setErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[fieldName];
      return newErrors;
    });
  }, []);
  
  // 更新字段
  const updateField = useCallback((fieldName, updates) => {
    setFields(prev => prev.map(field => 
      field.name === fieldName ? { ...field, ...updates } : field
    ));
  }, []);
  
  // 处理字段值变化
  const handleChange = useCallback((fieldName, value) => {
    setValues(prev => ({
      ...prev,
      [fieldName]: value
    }));
    
    // 清除该字段的错误
    setErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[fieldName];
      return newErrors;
    });
  }, []);
  
  // 验证字段
  const validateField = useCallback((fieldName, value) => {
    const field = fields.find(f => f.name === fieldName);
    if (!field || !field.validate) return null;
    
    const error = field.validate(value, values);
    setErrors(prev => ({
      ...prev,
      [fieldName]: error
    }));
    
    return error;
  }, [fields, values]);
  
  // 验证所有字段
  const validateAll = useCallback(() => {
    const newErrors = {};
    
    fields.forEach(field => {
      if (field.validate) {
        const error = field.validate(values[field.name], values);
        if (error) {
          newErrors[field.name] = error;
        }
      }
    });
    
    setErrors(newErrors);
    return newErrors;
  }, [fields, values]);
  
  // 获取表单数据
  const getFormData = useCallback(() => {
    return values;
  }, [values]);
  
  // 重置表单
  const resetForm = useCallback(() => {
    const initialValues = {};
    fields.forEach(field => {
      initialValues[field.name] = field.initialValue || '';
    });
    setValues(initialValues);
    setErrors({});
  }, [fields]);
  
  return {
    // 状态
    fields,
    values,
    errors,
    
    // 字段操作
    addField,
    removeField,
    updateField,
    
    // 值操作
    handleChange,
    setValues,
    
    // 验证
    validateField,
    validateAll,
    
    // 工具方法
    getFormData,
    resetForm,
    
    // 状态检查
    isValid: Object.keys(errors).length === 0,
    isDirty: !deepEqual(values, fields.reduce((acc, field) => {
      acc[field.name] = field.initialValue || '';
      return acc;
    }, {}))
  };
}

// 使用示例：动态调查问卷
function DynamicSurvey() {
  const questionTypes = [
    { value: 'text', label: '文本输入' },
    { value: 'textarea', label: '多行文本' },
    { value: 'radio', label: '单选' },
    { value: 'checkbox', label: '多选' },
    { value: 'select', label: '下拉选择' }
  ];
  
  const {
    fields,
    values,
    errors,
    addField,
    removeField,
    updateField,
    handleChange,
    validateAll
  } = useDynamicForm([
    {
      name: 'name',
      type: 'text',
      label: '姓名',
      placeholder: '请输入您的姓名',
      required: true,
      validate: (value) => !value ? '姓名不能为空' : null
    },
    {
      name: 'email',
      type: 'text',
      label: '邮箱',
      placeholder: '请输入您的邮箱',
      required: true,
      validate: (value) => {
        if (!value) return '邮箱不能为空';
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return '邮箱格式不正确';
        return null;
      }
    }
  ]);
  
  const addQuestion = () => {
    const questionNumber = fields.filter(f => f.type !== 'text').length + 1;
    
    addField({
      name: `question_${questionNumber}`,
      type: 'text',
      label: `问题 ${questionNumber}`,
      placeholder: '请输入问题内容',
      required: true,
      validate: (value) => !value ? '问题不能为空' : null
    });
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    const errors = validateAll();
    if (Object.keys(errors).length > 0) {
      alert('请检查表单错误');
      return;
    }
    
    console.log('提交调查问卷:', values);
    // 提交逻辑
  };
  
  return (
    <div className="dynamic-survey">
      <h2>调查问卷</h2>
      
      <form onSubmit={handleSubmit}>
        {fields.map((field) => (
          <div key={field.name} className="form-field">
            <label>
              {field.label}
              {field.required && <span className="required">*</span>}
            </label>
            
            {field.type === 'text' && (
              <input
                type="text"
                value={values[field.name] || ''}
                onChange={(e) => handleChange(field.name, e.target.value)}
                placeholder={field.placeholder}
                className={errors[field.name] ? 'error' : ''}
              />
            )}
            
            {field.type === 'textarea' && (
              <textarea
                value={values[field.name] || ''}
                onChange={(e) => handleChange(field.name, e.target.value)}
                placeholder={field.placeholder}
                className={errors[field.name] ? 'error' : ''}
                rows={4}
              />
            )}
            
            {field.type === 'select' && field.options && (
              <select
                value={values[field.name] || ''}
                onChange={(e) => handleChange(field.name, e.target.value)}
                className={errors[field.name] ? 'error' : ''}
              >
                <option value="">请选择</option>
                {field.options.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            )}
            
            {errors[field.name] && (
              <div className="error-message">{errors[field.name]}</div>
            )}
            
            {!field.name.startsWith('question_') && (
              <button
                type="button"
                onClick={() => removeField(field.name)}
                className="remove-btn"
              >
                删除
              </button>
            )}
            
            {field.name.startsWith('question_') && (
              <div className="question-options">
                <select
                  value={field.type}
                  onChange={(e) => updateField(field.name, { type: e.target.value })}
                >
                  {questionTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        ))}
        
        <div className="form-actions">
          <button type="button" onClick={addQuestion}>
            添加问题
          </button>
          
          <button type="submit">
            提交问卷
          </button>
        </div>
      </form>
    </div>
  );
}
```

## 八、API 请求自定义 Hook

### 8.1 数据获取与缓存 Hook

```javascript
// useQuery：数据查询 Hook（类似 React Query）
function useQuery(key, fetcher, options = {}) {
  const {
    enabled = true,
    staleTime = 0,
    cacheTime = 5 * 60 * 1000, // 5分钟
    retry = 3,
    retryDelay = 1000,
    onSuccess,
    onError,
    onSettled
  } = options;
  
  const [state, setState] = useState({
    data: null,
    error: null,
    status: 'idle', // 'idle' | 'loading' | 'success' | 'error'
    isFetching: false,
    isStale: true
  });
  
  const cache = useRef(new Map());
  const retryCount = useRef(0);
  
  const fetchData = useCallback(async () => {
    // 检查缓存
    const cached = cache.current.get(key);
    const now = Date.now();
    
    if (cached && now - cached.timestamp < staleTime) {
      setState({
        data: cached.data,
        error: null,
        status: 'success',
        isFetching: false,
        isStale: false
      });
      return;
    }
    
    // 开始获取
    setState(prev => ({
      ...prev,
      status: 'loading',
      isFetching: true
    }));
    
    try {
      const data = await fetcher();
      
      // 更新缓存
      cache.current.set(key, {
        data,
        timestamp: now
      });
      
      // 设置清理定时器
      setTimeout(() => {
        cache.current.delete(key);
      }, cacheTime);
      
      setState({
        data,
        error: null,
        status: 'success',
        isFetching: false,
        isStale: false
      });
      
      if (onSuccess) onSuccess(data);
      if (onSettled) onSettled(data, null);
      
      retryCount.current = 0;
    } catch (error) {
      // 重试逻辑
      if (retryCount.current < retry) {
        retryCount.current += 1;
        
        setTimeout(() => {
          fetchData();
        }, retryDelay * retryCount.current);
        
        return;
      }
      
      setState({
        data: null,
        error: error.message,
        status: 'error',
        isFetching: false,
        isStale: true
      });
      
      if (onError) onError(error);
      if (onSettled) onSettled(null, error);
    }
  }, [key, fetcher, staleTime, cacheTime, retry, retryDelay, onSuccess, onError, onSettled]);
  
  // 手动重新获取
  const refetch = useCallback(() => {
    fetchData();
  }, [fetchData]);
  
  // 设置数据（乐观更新）
  const setData = useCallback((newData) => {
    setState(prev => ({
      ...prev,
      data: typeof newData === 'function' ? newData(prev.data) : newData
    }));
    
    // 更新缓存
    cache.current.set(key, {
      data: newData,
      timestamp: Date.now()
    });
  }, [key]);
  
  // 自动获取
  useEffect(() => {
    if (enabled) {
      fetchData();
    }
  }, [enabled, fetchData]);
  
  return {
    ...state,
    refetch,
    setData,
    isIdle: state.status === 'idle',
    isLoading: state.status === 'loading',
    isError: state.status === 'error',
    isSuccess: state.status === 'success'
  };
}

// 使用示例
function UserProfile({ userId }) {
  const { data: user, isLoading, error, refetch } = useQuery(
    ['user', userId],
    () => fetch(`/api/users/${userId}`).then(res => res.json()),
    {
      staleTime: 1000 * 60, // 1分钟
      onSuccess: (data) => {
        console.log('用户数据加载成功:', data);
      },
      onError: (error) => {
        console.error('用户数据加载失败:', error);
      }
    }
  );
  
  if (isLoading) return <div>加载中...</div>;
  if (error) return <div>错误: {error}</div>;
  
  return (
    <div>
      <h2>{user.name}</h2>
      <p>邮箱: {user.email}</p>
      <button onClick={refetch}>刷新</button>
    </div>
  );
}
```

### 8.2 数据变更 Hook

```javascript
// useMutation：数据变更 Hook
function useMutation(mutator, options = {}) {
  const {
    onSuccess,
    onError,
    onSettled,
    onMutate
  } = options;
  
  const [state, setState] = useState({
    data: null,
    error: null,
    status: 'idle', // 'idle' | 'loading' | 'success' | 'error'
    isIdle: true,
    isLoading: false,
    isError: false,
    isSuccess: false
  });
  
  const mutate = useCallback(async (variables, context) => {
    setState({
      data: null,
      error: null,
      status: 'loading',
      isIdle: false,
      isLoading: true,
      isError: false,
      isSuccess: false
    });
    
    let optimisticData = null;
    
    // 乐观更新回调
    if (onMutate) {
      optimisticData = onMutate(variables);
    }
    
    try {
      const data = await mutator(variables);
      
      setState({
        data,
        error: null,
        status: 'success',
        isIdle: false,
        isLoading: false,
        isError: false,
        isSuccess: true
      });
      
      if (onSuccess) onSuccess(data, variables, context);
      if (onSettled) onSettled(data, null, variables, context);
      
      return data;
    } catch (error) {
      setState({
        data: null,
        error: error.message,
        status: 'error',
        isIdle: false,
        isLoading: false,
        isError: true,
        isSuccess: false
      });
      
      if (onError) onError(error, variables, context, optimisticData);
      if (onSettled) onSettled(null, error, variables, context);
      
      throw error;
    }
  }, [mutator, onSuccess, onError, onSettled, onMutate]);
  
  const reset = useCallback(() => {
    setState({
      data: null,
      error: null,
      status: 'idle',
      isIdle: true,
      isLoading: false,
      isError: false,
      isSuccess: false
    });
  }, []);
  
  return {
    ...state,
    mutate,
    reset
  };
}

// 使用示例：创建用户
function CreateUserForm() {
  const createUserMutation = useMutation(
    (userData) => fetch('/api/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    }).then(res => res.json()),
    {
      onMutate: (userData) => {
        // 乐观更新：立即在 UI 中显示新用户
        console.log('即将创建用户:', userData);
        return userData;
      },
      onSuccess: (data) => {
        console.log('用户创建成功:', data);
        alert('用户创建成功!');
      },
      onError: (error) => {
        console.error('用户创建失败:', error);
        alert('用户创建失败: ' + error.message);
      }
    }
  );
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const userData = {
      name: formData.get('name'),
      email: formData.get('email'),
      role: formData.get('role')
    };
    
    createUserMutation.mutate(userData);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>姓名:</label>
        <input type="text" name="name" required />
      </div>
      
      <div>
        <label>邮箱:</label>
        <input type="email" name="email" required />
      </div>
      
      <div>
        <label>角色:</label>
        <select name="role">
          <option value="user">普通用户</option>
          <option value="admin">管理员</option>
          <option value="editor">编辑</option>
        </select>
      </div>
      
      <button type="submit" disabled={createUserMutation.isLoading}>
        {createUserMutation.isLoading ? '创建中...' : '创建用户'}
      </button>
      
      {createUserMutation.isError && (
        <div className="error">错误: {createUserMutation.error}</div>
      )}
      
      {createUserMutation.isSuccess && (
        <div className="success">用户创建成功!</div>
      )}
    </form>
  );
}

// 组合使用 useQuery 和 useMutation
function UserManagement() {
  const { data: users, isLoading, refetch } = useQuery(
    'users',
    () => fetch('/api/users').then(res => res.json())
  );
  
  const deleteUserMutation = useMutation(
    (userId) => fetch(`/api/users/${userId}`, { method: 'DELETE' }),
    {
      onSuccess: () => {
        // 用户删除成功后重新获取用户列表
        refetch();
      }
    }
  );
  
  if (isLoading) return <div>加载用户列表...</div>;
  
  return (
    <div>
      <h2>用户管理</h2>
      
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>姓名</th>
            <th>邮箱</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <tr key={user.id}>
              <td>{user.id}</td>
              <td>{user.name}</td>
              <td>{user.email}</td>
              <td>
                <button
                  onClick={() => deleteUserMutation.mutate(user.id)}
                  disabled={deleteUserMutation.isLoading}
                >
                  {deleteUserMutation.isLoading ? '删除中...' : '删除'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

## 九、性能优化自定义 Hook

### 9.1 记忆化 Hook

```javascript
// useMemoizedCallback：记忆化回调函数
function useMemoizedCallback(callback, deps) {
  const callbackRef = useRef(callback);
  const memoizedCallback = useRef();
  
  // 更新回调引用
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);
  
  // 创建记忆化回调
  if (!memoizedCallback.current) {
    memoizedCallback.current = (...args) => {
      return callbackRef.current(...args);
    };
  }
  
  // 依赖变化时重新创建
  useEffect(() => {
    memoizedCallback.current = (...args) => {
      return callbackRef.current(...args);
    };
  }, deps);
  
  return memoizedCallback.current;
}

// 使用示例
function ExpensiveComponent({ data, onUpdate }) {
  const memoizedOnUpdate = useMemoizedCallback(onUpdate, [data]);
  
  return (
    <div>
      <button onClick={() => memoizedOnUpdate(data)}>
        更新数据
      </button>
    </div>
  );
}
```

### 9.2 防抖与节流 Hook

```javascript
// useThrottle：节流 Hook
function useThrottle(value, limit) {
  const [throttledValue, setThrottledValue] = useState(value);
  const lastRan = useRef(Date.now());
  
  useEffect(() => {
    const handler = setTimeout(() => {
      if (Date.now() - lastRan.current >= limit) {
        setThrottledValue(value);
        lastRan.current = Date.now();
      }
    }, limit - (Date.now() - lastRan.current));
    
    return () => {
      clearTimeout(handler);
    };
  }, [value, limit]);
  
  return throttledValue;
}

// useDebounce：防抖 Hook（增强版）
function useDebounce(value, delay, options = {}) {
  const {
    maxWait,
    leading = false,
    trailing = true
  } = options;
  
  const [debouncedValue, setDebouncedValue] = useState(value);
  const timeoutRef = useRef();
  const maxTimeoutRef = useRef();
  const leadingCallRef = useRef(false);
  
  useEffect(() => {
    const shouldCallLeading = leading && !leadingCallRef.current;
    
    if (shouldCallLeading) {
      setDebouncedValue(value);
      leadingCallRef.current = true;
    }
    
    // 清除之前的定时器
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    if (maxWait && !maxTimeoutRef.current) {
      maxTimeoutRef.current = setTimeout(() => {
        if (trailing) {
          setDebouncedValue(value);
        }
        leadingCallRef.current = false;
        maxTimeoutRef.current = null;
      }, maxWait);
    }
    
    timeoutRef.current = setTimeout(() => {
      if (trailing) {
        setDebouncedValue(value);
      }
      leadingCallRef.current = false;
      
      if (maxTimeoutRef.current) {
        clearTimeout(maxTimeoutRef.current);
        maxTimeoutRef.current = null;
      }
    }, delay);
    
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      if (maxTimeoutRef.current) {
        clearTimeout(maxTimeoutRef.current);
      }
    };
  }, [value, delay, maxWait, leading, trailing]);
  
  return debouncedValue;
}

// 使用示例：搜索输入
function SearchInput() {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 500, {
    leading: true,
    maxWait: 2000
  });
  
  useEffect(() => {
    if (debouncedQuery) {
      performSearch(debouncedQuery);
    }
  }, [debouncedQuery]);
  
  return (
    <input
      type="text"
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="搜索..."
    />
  );
}
```

### 9.3 虚拟列表 Hook

```javascript
// useVirtualList：虚拟列表 Hook
function useVirtualList(items, options = {}) {
  const {
    itemHeight = 50,
    overscan = 5,
    containerRef
  } = options;
  
  const [scrollTop, setScrollTop] = useState(0);
  const [containerHeight, setContainerHeight] = useState(0);
  
  // 计算可见项
  const totalHeight = items.length * itemHeight;
  const startIndex = Math.floor(scrollTop / itemHeight);
  const visibleCount = Math.ceil(containerHeight / itemHeight);
  
  const endIndex = Math.min(
    items.length - 1,
    startIndex + visibleCount + overscan
  );
  
  const visibleItems = items.slice(
    Math.max(0, startIndex - overscan),
    endIndex + 1
  );
  
  const offsetY = Math.max(0, (startIndex - overscan) * itemHeight);
  
  // 滚动处理
  const handleScroll = useCallback(() => {
    if (containerRef.current) {
      setScrollTop(containerRef.current.scrollTop);
    }
  }, [containerRef]);
  
  // 容器尺寸变化处理
  const handleResize = useCallback(() => {
    if (containerRef.current) {
      setContainerHeight(containerRef.current.clientHeight);
    }
  }, [containerRef]);
  
  // 初始化和监听
  useEffect(() => {
    if (containerRef.current) {
      handleResize();
      containerRef.current.addEventListener('scroll', handleScroll);
      
      const resizeObserver = new ResizeObserver(handleResize);
      resizeObserver.observe(containerRef.current);
      
      return () => {
        containerRef.current?.removeEventListener('scroll', handleScroll);
        resizeObserver.disconnect();
      };
    }
  }, [containerRef, handleScroll, handleResize]);
  
  return {
    visibleItems,
    totalHeight,
    offsetY,
    startIndex,
    endIndex
  };
}

// 使用示例
function VirtualList({ items }) {
  const containerRef = useRef();
  const { visibleItems, totalHeight, offsetY } = useVirtualList(items, {
    itemHeight: 60,
    overscan: 3,
    containerRef
  });
  
  return (
    <div
      ref={containerRef}
      style={{
        height: '500px',
        overflow: 'auto',
        position: 'relative'
      }}
    >
      <div style={{ height: `${totalHeight}px` }}>
        <div style={{ transform: `translateY(${offsetY}px)` }}>
          {visibleItems.map((item, index) => (
            <div
              key={item.id}
              style={{
                height: '60px',
                borderBottom: '1px solid #eee',
                padding: '10px'
              }}
            >
              {item.content}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

## 十、测试与调试自定义 Hook

### 10.1 测试自定义 Hook

```javascript
// 测试 useCounter Hook
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

describe('useCounter', () => {
  test('应该使用初始值', () => {
    const { result } = renderHook(() => useCounter(10));
    expect(result.current.count).toBe(10);
  });
  
  test('应该增加计数', () => {
    const { result } = renderHook(() => useCounter(0));
    
    act(() => {
      result.current.increment();
    });
    
    expect(result.current.count).toBe(1);
  });
  
  test('应该减少计数', () => {
    const { result } = renderHook(() => useCounter(5));
    
    act(() => {
      result.current.decrement();
    });
    
    expect(result.current.count).toBe(4);
  });
  
  test('应该重置计数', () => {
    const { result } = renderHook(() => useCounter(0));
    
    act(() => {
      result.current.increment();
      result.current.increment();
      result.current.reset();
    });
    
    expect(result.current.count).toBe(0);
  });
});

// 测试异步 Hook
import { waitFor } from '@testing-library/react';
import { useFetch } from './useFetch';

describe('useFetch', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });
  
  test('应该加载数据', async () => {
    const mockData = { id: 1, name: 'Test' };
    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockData)
    });
    
    const { result } = renderHook(() => useFetch('/api/test'));
    
    expect(result.current.loading).toBe(true);
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    expect(result.current.data).toEqual(mockData);
    expect(result.current.error).toBeNull();
  });
  
  test('应该处理错误', async () => {
    global.fetch.mockRejectedValue(new Error('Network error'));
    
    const { result } = renderHook(() => useFetch('/api/test'));
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    expect(result.current.data).toBeNull();
    expect(result.current.error).toBe('Network error');
  });
});
```

### 10.2 调试自定义 Hook

```javascript
// useDebugValue：React 内置调试 Hook
function useComplexState(initialState) {
  const [state, setState] = useState(initialState);
  
  // 在 React DevTools 中显示调试信息
  useDebugValue(state, state => 
    `状态: ${JSON.stringify(state)}`
  );
  
  return [state, setState];
}

// 自定义调试 Hook
function useDebugHook(hook, label) {
  const result = hook();
  
  useEffect(() => {
    console.log(`[${label}] 状态变化:`, result);
  }, [result, label]);
  
  return result;
}

// 使用示例
function MyComponent() {
  const counter = useDebugHook(
    () => useCounter(0),
    'useCounter'
  );
  
  const { count, increment } = counter;
  
  return (
    <div>
      <p>计数: {count}</p>
      <button onClick={increment}>增加</button>
    </div>
  );
}

// 性能调试 Hook
function usePerformanceDebug(label) {
  const renderCount = useRef(0);
  const lastRenderTime = useRef(Date.now());
  
  renderCount.current += 1;
  
  useEffect(() => {
    const now = Date.now();
    const timeSinceLastRender = now - lastRenderTime.current;
    
    console.log(`[${label}] 第 ${renderCount.current} 次渲染`);
    console.log(`[${label}] 距离上次渲染: ${timeSinceLastRender}ms`);
    
    lastRenderTime.current = now;
  });
  
  return {
    renderCount: renderCount.current
  };
}

// 使用示例
function OptimizedComponent() {
  usePerformanceDebug('OptimizedComponent');
  
  // 组件逻辑...
  return <div>优化组件</div>;
}
```

### 10.3 错误边界与错误处理 Hook

```javascript
// useErrorBoundary：错误边界 Hook
function useErrorBoundary() {
  const [error, setError] = useState(null);
  
  const ErrorBoundary = useCallback(({ children, fallback }) => {
    if (error) {
      return fallback ? fallback(error) : (
        <div>
          <h2>出错了!</h2>
          <p>{error.message}</p>
          <button onClick={() => setError(null)}>重试</button>
        </div>
      );
    }
    
    return children;
  }, [error]);
  
  const withErrorBoundary = useCallback((Component, fallback) => {
    return (props) => (
      <ErrorBoundary fallback={fallback}>
        <Component {...props} />
      </ErrorBoundary>
    );
  }, [ErrorBoundary]);
  
  return {
    error,
    setError,
    ErrorBoundary,
    withErrorBoundary,
    clearError: () => setError(null)
  };
}

// 使用示例
function BuggyComponent() {
  const { setError } = useErrorBoundary();
  
  const handleClick = () => {
    try {
      // 可能抛出错误的代码
      throw new Error('测试错误');
    } catch (error) {
      setError(error);
    }
  };
  
  return (
    <button onClick={handleClick}>
      触发错误
    </button>
  );
}

function App() {
  const { ErrorBoundary } = useErrorBoundary();
  
  return (
    <ErrorBoundary fallback={(error) => (
      <div>
        <h2>应用程序错误</h2>
        <p>{error.message}</p>
      </div>
    )}>
      <BuggyComponent />
    </ErrorBoundary>
  );
}
```

## 十一、最佳实践与常见陷阱

### 11.1 最佳实践

1. **单一职责原则**
```javascript
// ✅ 正确：每个 Hook 只做一件事
function useCounter() { /* 只管理计数 */ }
function useTimer() { /* 只管理计时器 */ }
function useForm() { /* 只管理表单 */ }

// ❌ 错误：一个 Hook 做太多事
function useEverything() { /* 管理计数、计时器、表单... */ }
```

2. **清晰的命名**
```javascript
// ✅ 正确：描述性名称
function useUserAuthentication() { /* ... */ }
function useInfiniteScroll() { /* ... */ }
function useLocalStorageState() { /* ... */ }

// ❌ 错误：模糊的命名
function useHook() { /* ... */ }
function useStuff() { /* ... */ }
function useMyLogic() { /* ... */ }
```

3. **适当的抽象层级**
```javascript
// ✅ 正确：适当的抽象
function useFetch(url) { /* 通用数据获取 */ }
function useUser(userId) { /* 用户特定逻辑 */ }

// ❌ 错误：过度抽象或不足
function useFetchUserProfileAndSettingsAndActivities(userId) { /* 太具体 */ }
function useGenericHook(config) { /* 太通用 */ }
```

4. **完善的错误处理**
```javascript
// ✅ 正确：完善的错误处理
function useSafeHook() {
  const [error, setError] = useState(null);
  
  const execute = useCallback(async () => {
    try {
      // 操作...
    } catch (err) {
      setError(err);
      console.error('Hook 执行失败:', err);
    }
  }, []);
  
  return { execute, error };
}
```

5. **性能考虑**
```javascript
// ✅ 正确：性能优化
function useOptimizedHook(deps) {
  const memoizedValue = useMemo(() => {
    // 昂贵的计算
    return computeExpensiveValue(deps);
  }, [deps]);
  
  const memoizedCallback = useCallback(() => {
    // 回调函数
  }, [deps]);
  
  return { memoizedValue, memoizedCallback };
}
```

### 11.2 常见陷阱

1. **无限循环**
```javascript
// ❌ 错误：导致无限循环
function useProblematicHook(value) {
  const [state, setState] = useState(value);
  
  useEffect(() => {
    // 每次渲染都设置状态，导致无限循环
    setState(value);
  }); // 缺少依赖数组
  
  return state;
}

// ✅ 正确：正确处理依赖
function useCorrectHook(value) {
  const [state, setState] = useState(value);
  
  useEffect(() => {
    setState(value);
  }, [value]); // 正确声明依赖
  
  return state;
}
```

2. **过时的闭包**
```javascript
// ❌ 错误：过时的闭包
function useStaleClosure() {
  const [count, setCount] = useState(0);
  
  const increment = useCallback(() => {
    // count 总是初始值 0
    setCount(count + 1);
  }, []); // 缺少 count 依赖
  
  return { count, increment };
}

// ✅ 正确：使用函数更新
function useCorrectClosure() {
  const [count, setCount] = useState(0);
  
  const increment = useCallback(() => {
    setCount(prev => prev + 1); // 使用函数更新
  }, []); // 不需要 count 依赖
  
  return { count, increment };
}
```

3. **条件调用 Hook**
```javascript
// ❌ 错误：条件调用 Hook
function useConditionalHook(shouldUse) {
  if (shouldUse) {
    const [state, setState] = useState(); // 违反规则
  }
  
  return null;
}

// ✅ 正确：无条件调用 Hook
function useUnconditionalHook(shouldUse) {
  const [state, setState] = useState();
  
  // 条件逻辑放在 Hook 调用之后
  const actualState = shouldUse ? state : null;
  
  return actualState;
}
```

4. **循环中调用 Hook**
```javascript
// ❌ 错误：循环中调用 Hook
function useLoopHook(items) {
  const results = [];
  
  for (let item of items) {
    const [state, setState] = useState(item); // 违反规则
    results.push(state);
  }
  
  return results;
}

// ✅ 正确：使用数组管理状态
function useArrayHook(items) {
  const [states, setStates] = useState(items);
  
  // 操作整个数组
  const updateItem = useCallback((index, newValue) => {
    setStates(prev => {
      const newStates = [...prev];
      newStates[index] = newValue;
      return newStates;
    });
  }, []);
  
  return { states, updateItem };
}
```

5. **忘记清理副作用**
```javascript
// ❌ 错误：忘记清理
function useUncleanHook() {
  useEffect(() => {
    const interval = setInterval(() => {
      console.log('tick');
    }, 1000);
    
    // 忘记清理 interval
  }, []);
}

// ✅ 正确：清理副作用
function useCleanHook() {
  useEffect(() => {
    const interval = setInterval(() => {
      console.log('tick');
    }, 1000);
    
    return () => {
      clearInterval(interval); // 清理
    };
  }, []);
}
```

## 十二、实战案例与完整示例

### 12.1 电商购物车 Hook

```javascript
// useShoppingCart：电商购物车 Hook
function useShoppingCart(initialItems = []) {
  const [items, setItems] = useState(initialItems);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // 计算总价
  const totalPrice = useMemo(() => {
    return items.reduce((sum, item) => {
      return sum + (item.price * item.quantity);
    }, 0);
  }, [items]);
  
  // 计算总数量
  const totalQuantity = useMemo(() => {
    return items.reduce((sum, item) => sum + item.quantity, 0);
  }, [items]);
  
  // 添加商品
  const addItem = useCallback(async (product, quantity = 1) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // 模拟 API 调用
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setItems(prev => {
        const existingItemIndex = prev.findIndex(
          item => item.id === product.id
        );
        
        if (existingItemIndex >= 0) {
          // 更新现有商品数量
          const newItems = [...prev];
          newItems[existingItemIndex] = {
            ...newItems[existingItemIndex],
            quantity: newItems[existingItemIndex].quantity + quantity
          };
          return newItems;
        } else {
          // 添加新商品
          return [...prev, {
            ...product,
            quantity,
            addedAt: new Date().toISOString()
          }];
        }
      });
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  // 移除商品
  const removeItem = useCallback((itemId) => {
    setItems(prev => prev.filter(item => item.id !== itemId));
  }, []);
  
  // 更新商品数量
  const updateQuantity = useCallback((itemId, quantity) => {
    if (quantity <= 0) {
      removeItem(itemId);
      return;
    }
    
    setItems(prev => prev.map(item => 
      item.id === itemId ? { ...item, quantity } : item
    ));
  }, [removeItem]);
  
  // 清空购物车
  const clearCart = useCallback(() => {
    setItems([]);
  }, []);
  
  // 保存到本地存储
  const saveToLocalStorage = useCallback(() => {
    try {
      localStorage.setItem('shoppingCart', JSON.stringify(items));
    } catch (err) {
      console.error('保存购物车失败:', err);
    }
  }, [items]);
  
  // 从本地存储加载
  const loadFromLocalStorage = useCallback(() => {
    try {
      const saved = localStorage.getItem('shoppingCart');
      if (saved) {
        setItems(JSON.parse(saved));
      }
    } catch (err) {
      console.error('加载购物车失败:', err);
    }
  }, []);
  
  // 自动保存到本地存储
  useEffect(() => {
    saveToLocalStorage();
  }, [items, saveToLocalStorage]);
  
  return {
    // 状态
    items,
    isLoading,
    error,
    totalPrice,
    totalQuantity,
    
    // 操作方法
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
    loadFromLocalStorage,
    
    // 状态检查
    isEmpty: items.length === 0,
    hasItem: (itemId) => items.some(item => item.id === itemId),
    getItem: (itemId) => items.find(item => item.id === itemId)
  };
}

// 使用示例
function ShoppingCart() {
  const {
    items,
    totalPrice,
    totalQuantity,
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
    isLoading
  } = useShoppingCart();
  
  const products = [
    { id: 1, name: '商品A', price: 100, stock: 10 },
    { id: 2, name: '商品B', price: 200, stock: 5 },
    { id: 3, name: '商品C', price: 300, stock: 3 }
  ];
  
  return (
    <div className="shopping-cart">
      <h2>购物车 ({totalQuantity} 件商品)</h2>
      
      <div className="cart-items">
        {items.length === 0 ? (
          <p>购物车为空</p>
        ) : (
          items.map(item => (
            <div key={item.id} className="cart-item">
              <span className="item-name">{item.name}</span>
              <span className="item-price">¥{item.price}</span>
              
              <div className="quantity-controls">
                <button
                  onClick={() => updateQuantity(item.id, item.quantity - 1)}
                  disabled={item.quantity <= 1}
                >
                  -
                </button>
                <span>{item.quantity}</span>
                <button
                  onClick={() => updateQuantity(item.id, item.quantity + 1)}
                  disabled={item.quantity >= item.stock}
                >
                  +
                </button>
              </div>
              
              <span className="item-total">
                ¥{item.price * item.quantity}
              </span>
              
              <button
                onClick={() => removeItem(item.id)}
                className="remove-btn"
              >
                删除
              </button>
            </div>
          ))
        )}
      </div>
      
      <div className="cart-summary">
        <div className="total">
          总计: <strong>¥{totalPrice.toFixed(2)}</strong>
        </div>
        
        <div className="actions">
          <button
            onClick={clearCart}
            disabled={items.length === 0}
            className="clear-btn"
          >
            清空购物车
          </button>
          
          <button
            disabled={items.length === 0 || isLoading}
            className="checkout-btn"
          >
            {isLoading ? '处理中...' : '去结算'}
          </button>
        </div>
      </div>
      
      <div className="product-list">
        <h3>推荐商品</h3>
        {products.map(product => (
          <div key={product.id} className="product">
            <span>{product.name} - ¥{product.price}</span>
            <button
              onClick={() => addItem(product)}
              disabled={isLoading}
            >
              加入购物车
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 12.2 实时聊天应用 Hook

```javascript
// useChat：实时聊天 Hook
function useChat(roomId, userId) {
  const [messages, setMessages] = useState([]);
  const [users, setUsers] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  
  const socketRef = useRef();
  const typingTimeoutRef = useRef();
  
  // 连接 WebSocket
  const connect = useCallback(() => {
    const socket = new WebSocket(`wss://chat.example.com/ws/${roomId}`);
    
    socket.onopen = () => {
      setIsConnected(true);
      
      // 发送加入消息
      socket.send(JSON.stringify({
        type: 'join',
        userId,
        timestamp: new Date().toISOString()
      }));
    };
    
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'message':
          setMessages(prev => [...prev, data]);
          break;
          
        case 'user_joined':
          setUsers(prev => [...prev, data.user]);
          break;
          
        case 'user_left':
          setUsers(prev => prev.filter(user => user.id !== data.userId));
          break;
          
        case 'typing_start':
          if (data.userId !== userId) {
            setIsTyping(true);
          }
          break;
          
        case 'typing_stop':
          if (data.userId !== userId) {
            setIsTyping(false);
          }
          break;
          
        case 'users_list':
          setUsers(data.users);
          break;
          
        case 'history':
          setMessages(data.messages);
          break;
      }
    };
    
    socket.onclose = () => {
      setIsConnected(false);
      
      // 尝试重连
      setTimeout(() => {
        connect();
      }, 3000);
    };
    
    socket.onerror = (error) => {
      console.error('WebSocket 错误:', error);
    };
    
    socketRef.current = socket;
    
    return socket;
  }, [roomId, userId]);
  
  // 发送消息
  const sendMessage = useCallback((content) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket 未连接');
    }
    
    const message = {
      type: 'message',
      content,
      userId,
      timestamp: new Date().toISOString()
    };
    
    socketRef.current.send(JSON.stringify(message));
    return message;
  }, [userId]);
  
  // 发送输入状态
  const sendTyping = useCallback(() => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      return;
    }
    
    // 清除之前的定时器
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    
    // 发送开始输入
    socketRef.current.send(JSON.stringify({
      type: 'typing_start',
      userId,
      timestamp: new Date().toISOString()
    }));
    
    // 设置停止输入的定时器
    typingTimeoutRef.current = setTimeout(() => {
      socketRef.current.send(JSON.stringify({
        type: 'typing_stop',
        userId,
        timestamp: new Date().toISOString()
      }));
    }, 3000);
  }, [userId]);
  
  // 获取消息历史
  const fetchHistory = useCallback(async (limit = 50) => {
    try {
      const response = await fetch(
        `https://chat.example.com/api/rooms/${roomId}/messages?limit=${limit}`
      );
      const data = await response.json();
      setMessages(data.messages);
    } catch (error) {
      console.error('获取消息历史失败:', error);
    }
  }, [roomId]);
  
  // 断开连接
  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.close();
    }
    
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
  }, []);
  
  // 初始连接
  useEffect(() => {
    const socket = connect();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);
  
  return {
    // 状态
    messages,
    users,
    isConnected,
    isTyping,
    
    // 操作方法
    sendMessage,
    sendTyping,
    fetchHistory,
    disconnect,
    
    // 工具方法
    getUnreadCount: (lastReadId) => {
      const lastReadIndex = messages.findIndex(msg => msg.id === lastReadId);
      return lastReadIndex === -1 ? messages.length : messages.length - lastReadIndex - 1;
    },
    
    getUser: (userId) => users.find(user => user.id === userId)
  };
}

// 使用示例
function ChatRoom({ roomId, userId, userName }) {
  const [input, setInput] = useState('');
  const {
    messages,
    users,
    isConnected,
    isTyping,
    sendMessage,
    sendTyping,
    fetchHistory
  } = useChat(roomId, userId);
  
  const handleSend = () => {
    if (input.trim()) {
      sendMessage(input);
      setInput('');
    }
  };
  
  const handleInputChange = (e) => {
    setInput(e.target.value);
    sendTyping();
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };
  
  return (
    <div className="chat-room">
      <div className="chat-header">
        <h2>聊天室: {roomId}</h2>
        <div className="connection-status">
          状态: {isConnected ? '已连接' : '连接中...'}
        </div>
      </div>
      
      <div className="chat-layout">
        <div className="users-panel">
          <h3>在线用户 ({users.length})</h3>
          <ul>
            {users.map(user => (
              <li key={user.id}>
                {user.name} {user.id === userId && '(你)'}
              </li>
            ))}
          </ul>
        </div>
        
        <div className="chat-main">
          <div className="messages-container">
            {messages.map((message, index) => {
              const isOwn = message.userId === userId;
              const showAvatar = index === 0 || 
                messages[index - 1].userId !== message.userId;
              
              return (
                <div
                  key={message.id || index}
                  className={`message ${isOwn ? 'own' : 'other'} ${showAvatar ? 'show-avatar' : ''}`}
                >
                  {showAvatar && !isOwn && (
                    <div className="avatar">
                      {message.userName?.charAt(0) || 'U'}
                    </div>
                  )}
                  
                  <div className="message-content">
                    {showAvatar && !isOwn && (
                      <div className="sender-name">
                        {message.userName || '未知用户'}
                      </div>
                    )}
                    
                    <div className="message-text">
                      {message.content}
                    </div>
                    
                    <div className="message-time">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              );
            })}
            
            {isTyping && (
              <div className="typing-indicator">
                <span>对方正在输入...</span>
              </div>
            )}
          </div>
          
          <div className="input-area">
            <textarea
              value={input}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder="输入消息..."
              rows={3}
            />
            
            <div className="input-actions">
              <button
                onClick={() => fetchHistory()}
                className="history-btn"
              >
                历史消息
              </button>
              
              <button
                onClick={handleSend}
                disabled={!input.trim() || !isConnected}
                className="send-btn"
              >
                发送
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### 12.3 拖拽排序 Hook

```javascript
// useDragAndDrop：拖拽排序 Hook
function useDragAndDrop(items, onReorder) {
  const [draggingId, setDraggingId] = useState(null);
  const [dragOverId, setDragOverId] = useState(null);
  const [dragPosition, setDragPosition] = useState(null); // 'above' | 'below'
  
  const dragStart = useCallback((id) => {
    setDraggingId(id);
  }, []);
  
  const dragOver = useCallback((id, position) => {
    if (id !== draggingId) {
      setDragOverId(id);
      setDragPosition(position);
    }
  }, [draggingId]);
  
  const dragLeave = useCallback(() => {
    setDragOverId(null);
    setDragPosition(null);
  }, []);
  
  const drop = useCallback(() => {
    if (draggingId && dragOverId && draggingId !== dragOverId) {
      // 计算新顺序
      const oldIndex = items.findIndex(item => item.id === draggingId);
      const newIndex = items.findIndex(item => item.id === dragOverId);
      
      let adjustedNewIndex = newIndex;
      if (dragPosition === 'below') {
        adjustedNewIndex = newIndex + 1;
      }
      
      // 调整索引（如果拖拽到后面，且目标在拖拽项前面）
      if (oldIndex < adjustedNewIndex) {
        adjustedNewIndex -= 1;
      }
      
      // 重新排序
      const newItems = [...items];
      const [draggedItem] = newItems.splice(oldIndex, 1);
      newItems.splice(adjustedNewIndex, 0, draggedItem);
      
      // 调用回调
      onReorder(newItems);
    }
    
    // 重置状态
    setDraggingId(null);
    setDragOverId(null);
    setDragPosition(null);
  }, [draggingId, dragOverId, dragPosition, items, onReorder]);
  
  const dragEnd = useCallback(() => {
    setDraggingId(null);
    setDragOverId(null);
    setDragPosition(null);
  }, []);
  
  return {
    draggingId,
    dragOverId,
    dragPosition,
    dragStart,
    dragOver,
    dragLeave,
    drop,
    dragEnd,
    
    // 工具方法
    isDragging: (id) => id === draggingId,
    isDragOver: (id) => id === dragOverId,
    getDragStyle: (id) => {
      if (id === draggingId) {
        return { opacity: 0.5 };
      }
      
      if (id === dragOverId) {
        return {
          borderTop: dragPosition === 'above' ? '2px solid #007bff' : undefined,
          borderBottom: dragPosition === 'below' ? '2px solid #007bff' : undefined
        };
      }
      
      return {};
    }
  };
}

// 使用示例
function SortableList({ items: initialItems, onSort }) {
  const [items, setItems] = useState(initialItems);
  
  const {
    dragStart,
    dragOver,
    dragLeave,
    drop,
    dragEnd,
    getDragStyle
  } = useDragAndDrop(items, (newItems) => {
    setItems(newItems);
    onSort(newItems);
  });
  
  return (
    <div className="sortable-list">
      {items.map((item, index) => (
        <div
          key={item.id}
          className="sortable-item"
          draggable
          style={getDragStyle(item.id)}
          onDragStart={() => dragStart(item.id)}
          onDragOver={(e) => {
            e.preventDefault();
            
            const rect = e.currentTarget.getBoundingClientRect();
            const mouseY = e.clientY;
            const middleY = rect.top + rect.height / 2;
            
            dragOver(item.id, mouseY < middleY ? 'above' : 'below');
          }}
          onDragLeave={dragLeave}
          onDrop={drop}
          onDragEnd={dragEnd}
        >
          <div className="drag-handle">☰</div>
          <div className="item-content">
            <h4>{item.title}</h4>
            <p>{item.description}</p>
          </div>
          <div className="item-index">{index + 1}</div>
        </div>
      ))}
    </div>
  );
}

// 使用示例：任务管理
function TaskManager() {
  const [tasks, setTasks] = useState([
    { id: 1, title: '设计登录页面', description: '完成UI设计', status: 'todo' },
    { id: 2, title: '开发API接口', description: '用户认证接口', status: 'in-progress' },
    { id: 3, title: '编写测试用例', description: '单元测试和集成测试', status: 'todo' },
    { id: 4, title: '部署到生产', description: '配置服务器和部署', status: 'done' }
  ]);
  
  const handleSort = (sortedTasks) => {
    setTasks(sortedTasks);
    console.log('任务重新排序:', sortedTasks);
  };
  
  return (
    <div className="task-manager">
      <h2>任务管理</h2>
      <SortableList items={tasks} onSort={handleSort} />
    </div>
  );
}
```

## 十三、总结与进阶建议

### 13.1 自定义 Hook 的核心价值

1. **逻辑复用**：将通用逻辑封装成可重用的 Hook
2. **关注点分离**：使组件更专注于渲染，逻辑由 Hook 管理
3. **可测试性**：Hook 可以独立测试，提高代码质量
4. **可维护性**：逻辑集中管理，便于修改和维护
5. **可组合性**：多个 Hook 可以组合使用，构建复杂功能

### 13.2 进阶学习方向

1. **TypeScript 类型安全**
```typescript
// 类型安全的自定义 Hook
interface UseCounterReturn {
  count: number;
  increment: () => void;
  decrement: () => void;
  reset: () => void;
}

function useCounter(initialValue: number = 0): UseCounterReturn {
  const [count, setCount] = useState<number>(initialValue);
  
  const increment = useCallback(() => {
    setCount(prev => prev + 1);
  }, []);
  
  const decrement = useCallback(() => {
    setCount(prev => prev - 1);
  }, []);
  
  const reset = useCallback(() => {
    setCount(initialValue);
  }, [initialValue]);
  
  return { count, increment, decrement, reset };
}
```

2. **性能优化模式**
```javascript
// 使用 React.memo 和 useMemo 优化
const OptimizedComponent = React.memo(function OptimizedComponent({ data }) {
  const processedData = useMemo(() => {
    return expensiveProcessing(data);
  }, [data]);
  
  return <div>{processedData}</div>;
});

// 使用 useCallback 避免不必要的重渲染
function ParentComponent() {
  const handleClick = useCallback(() => {
    console.log('点击');
  }, []);
  
  return <ChildComponent onClick={handleClick} />;
}
```

3. **错误边界与 Suspense**
```javascript
// 结合错误边界
function useErrorBoundary() {
  const [error, setError] = useState(null);
  
  if (error) {
    throw error;
  }
  
  return { setError };
}

// 结合 Suspense
function useSuspenseFetch(url) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(setData)
      .catch(setError);
  }, [url]);
  
  if (error) throw error;
  if (!data) throw new Promise(resolve => setTimeout(resolve, 100));
  
  return data;
}
```

4. **并发特性支持**
```javascript
// 使用 useTransition 处理并发更新
function useOptimisticUpdate(initialState) {
  const [state, setState] = useState(initialState);
  const [isPending, startTransition] = useTransition();
  
  const optimisticUpdate = useCallback((newState) => {
    // 立即更新 UI（乐观更新）
    setState(newState);
    
    // 在后台执行实际更新
    startTransition(async () => {
      try {
        await api.update(newState);
      } catch (error) {
        // 回滚到之前的状态
        setState(initialState);
      }
    });
  }, [initialState, startTransition]);
  
  return { state, optimisticUpdate, isPending };
}
```

### 13.3 最佳实践总结

1. **始终以 `use` 开头命名**：遵循 React 约定
2. **保持 Hook 的纯粹性**：避免副作用，保持可预测性
3. **正确处理依赖**：避免无限循环和过时闭包
4. **提供清晰的 API**：易于理解和使用
5. **考虑性能影响**：使用记忆化优化性能
6. **完善的错误处理**：提供错误恢复机制
7. **编写测试用例**：确保 Hook 的可靠性
8. **文档化**：提供使用示例和 API 文档

### 13.4 资源推荐

1. **官方文档**
   - [React Hooks 官方文档](https://reactjs.org/docs/hooks-intro.html)
   - [自定义 Hook 指南](https://reactjs.org/docs/hooks-custom.html)

2. **优秀开源 Hook 库**
   - [React Use](https://github.com/streamich/react-use)：丰富的自定义 Hook 集合
   - [ahooks](https://github.com/alibaba/hooks)：阿里巴巴的高质量 React Hooks 库
   - [SWR](https://swr.vercel.app/)：数据获取 Hook 库
   - [React Query](https://tanstack.com/query)：强大的异步状态管理

3. **学习资源**
   - [React Hooks 完整指南](https://overreacted.io/zh-hans/a-complete-guide-to-useeffect/)
   - [自定义 Hook 设计模式](https://kentcdodds.com/blog/custom-hooks-patterns)
   - [Hook 测试最佳实践](https://testing-library.com/docs/react-testing-library/example-intro)

### 13.5 未来展望

随着 React 的不断发展，自定义 Hook 将在以下方面继续演进：

1. **React Compiler 集成**：编译器将自动优化 Hook 性能
2. **并发特性支持**：更好地支持并发渲染和 Suspense
3. **服务器组件**：在服务器端使用 Hook 的能力
4. **类型系统增强**：更好的 TypeScript 支持
5. **开发工具改进**：更强大的调试和性能分析工具

### 结语

自定义 Hook 是 React 生态系统中强大的工具，它改变了我们构建 React 应用的方式。通过将逻辑封装成可重用的 Hook，我们可以创建更清晰、更可维护、更可测试的代码。掌握自定义 Hook 的创建和使用，将使你成为更高效的 React 开发者。

记住，好的自定义 Hook 应该是：
- **专注的**：每个 Hook 只做一件事
- **可重用的**：可以在多个组件中复用
- **可测试的**：易于编写测试用例
- **文档化的**：有清晰的 API 和使用示例
- **类型安全的**：提供完整的 TypeScript 类型定义

通过不断实践和探索，你将能够创建出高质量的自定义 Hook，提升你的 React 开发体验和代码质量。

---
*文档创建完成：自定义 Hook 深度解析*
*创建时间：2026-03-30*
*文档版本：1.0.0*
*作者：React 技术专家*

