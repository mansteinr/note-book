# React 应用性能优化指南

## 简介

React 应用的性能优化是提升用户体验的关键。本文将介绍多种实用的性能优化方法。

## 主要优化方法

### 1. 使用 React.memo() 进行组件记忆化

React.memo() 是一个高阶组件，它会对组件的 props 进行浅比较，只有当 props 发生变化时才会重新渲染组件。

```jsx
const MyComponent = React.memo(function MyComponent(props) {
  return <div>{props.value}</div>
})
```

**适用场景：**
- 纯展示型组件
- props 频繁变化但渲染成本高的组件
- 避免父组件更新时子组件不必要的重新渲染

### 2. 使用 useMemo 和 useCallback 钩子

#### useMemo
缓存计算结果，避免在每次渲染时重复执行昂贵的计算。

```jsx
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(a, b)
}, [a, b])
```

#### useCallback
缓存函数引用，避免在每次渲染时创建新的函数实例。

```jsx
const handleClick = useCallback(() => {
  doSomething(a, b)
}, [a, b])
```

**适用场景：**
- 复杂的计算逻辑
- 作为 props 传递给子组件的函数
- 依赖项数组中的值变化时才重新计算

### 3. 代码分割和懒加载

使用 React.lazy() 和 Suspense 实现组件的按需加载，减少初始加载体积。

```jsx
const LazyComponent = React.lazy(() => import('./LazyComponent'))

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LazyComponent />
    </Suspense>
  )
}
```

**适用场景：**
- 路由级别的代码分割
- 大型组件的延迟加载
- 非关键功能的按需加载

### 4. 虚拟化长列表

对于包含大量数据的列表，使用虚拟化技术只渲染可见区域的元素。

```jsx
import { FixedSizeList } from 'react-window'

const Row = ({ index, style }) => (
  <div style={style}>Row {index}</div>
)

const MyList = () => (
  <FixedSizeList
    height={400}
    width={300}
    itemSize={35}
    itemCount={1000}
  >
    {Row}
  </FixedSizeList>
)
```

**适用场景：**
- 渲染大量数据（100+ 项）
- 长列表或表格
- 无限滚动列表

### 5. 优化状态管理

#### 避免不必要的状态更新
```jsx
setCount(prev => prev + 1) // 使用函数式更新
```

#### 合并相关状态
```jsx
const [state, setState] = useState({ name: '', age: 0 })
// 而不是
const [name, setName] = useState('')
const [age, setAge] = useState(0)
```

#### 使用 Context API 的优化
```jsx
const ValueContext = React.createContext()

const Provider = ({ children }) => {
  const [value, setValue] = useState(0)
  
  const memoizedValue = useMemo(() => ({
    value,
    setValue
  }), [value])
  
  return (
    <ValueContext.Provider value={memoizedValue}>
      {children}
    </ValueContext.Provider>
  )
}
```

## 其他优化技巧

### 6. 使用生产环境构建
```bash
npm run build
```

### 7. 图片优化
- 使用适当的图片格式（WebP, AVIF）
- 实现图片懒加载
- 使用响应式图片

### 8. CSS 优化
- 避免内联样式
- 使用 CSS 模块或 styled-components
- 减少 CSS 选择器复杂度

### 9. 使用 Web Workers
将繁重的计算任务移到 Web Worker 中执行，避免阻塞主线程。

### 10. 服务端渲染（SSR）
使用 Next.js 等框架实现服务端渲染，提升首屏加载速度。

## 性能监控工具

- React DevTools Profiler
- Chrome DevTools Performance
- Lighthouse
- WebPageTest

## 最佳实践

1. **测量优先**：在优化前先测量性能瓶颈
2. **渐进式优化**：从影响最大的问题开始
3. **避免过早优化**：只在必要时进行优化
4. **保持代码可读性**：不要为了性能牺牲代码质量
5. **定期审查**：随着应用增长，定期审查性能

## 总结

React 性能优化是一个持续的过程，需要根据具体应用场景选择合适的优化策略。建议从测量开始，识别瓶颈，然后有针对性地应用优化方法。

记住：**过早优化是万恶之源**。在优化之前，确保真正存在性能问题。
