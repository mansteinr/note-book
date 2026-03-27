
- [React 19 核心特性](#react-19-核心特性)
  - [Actions: 表单交互的革命​](#actions-表单交互的革命)
  - [并发与 use Hook](#并发与-use-hook)
  - [其他新特性](#其他新特性)
- [React Compiler (理念篇)](#react-compiler-理念篇)
  - [手动优化的痛点：useMemo, useCallback 的困境](#手动优化的痛点usememo-usecallback-的困境)
  - [React Compiler (“Forget”)](#react-compiler-forget)
  - [Compiler 如何实现自动记忆化 (Memoization)](#compiler-如何实现自动记忆化-memoization)
- [高级 Hooks 与状态管理​](#高级-hooks-与状态管理)
  - [复杂状态逻辑：useReducer vs useState](#复杂状态逻辑usereducer-vs-usestate)
  - [全局状态管理：useContext 与性能陷阱](#全局状态管理usecontext-与性能陷阱)
  - [手动性能优化：React.memo, useMemo, useCallback 的正确使用场景](#手动性能优化reactmemo-usememo-usecallback-的正确使用场景)
  - [自定义 Hooks：封装逻辑与实现复用 (含 TS 泛型)](#自定义-hooks封装逻辑与实现复用-含-ts-泛型)
- [TypeScript 高级应用](#typescript-高级应用)
  - [泛型组件与泛型 Hooks​](#泛型组件与泛型-hooks)
  - [React 事件对象的精确类型](#react-事件对象的精确类型)
  - [结合 Zod 进行运行时类型校验​](#结合-zod-进行运行时类型校验)
  - [高级类型工具 (Utility Types) 在组件 Props 中的应用](#高级类型工具-utility-types-在组件-props-中的应用)


## React 19 核心特性
### Actions: 表单交互的革命​
​

长久以来，处理 Web 表单一直是一项繁琐的任务。开发者需要手动管理 loading 状态、错误信息、成功反馈，并用 `e.preventDefault()` 来阻止浏览器的默认行为。React 19 引入的 **Actions** 彻底颠覆了这一传统模式，将表单的异步交互与状态管理无缝集成到框架底层。

**使用`<form>` 的 action 属性简化数据提交**

在 React 19 中，我们可以直接将一个函数（即 Action）传递给原生 `<form>` 元素的 `action` 属性。当你提交这个表单时，React 会自动拦截提交事件，处理表单数据的序列化（`FormData`），并调用你提供的 `Action` 函数。​
这意味着，我们可以告别 `onSubmit` 事件处理器和 `preventDefault()` 了。


```

// 传统的表单处理方式​
const OldForm = () => {​
  const handleSubmit = (e) => {​
    e.preventDefault();​
    const formData = new FormData(e.target);​
    // ...手动提交逻辑​
  };​
  return <form onSubmit={handleSubmit}>...</form>;​
};​
​
// React 19 的新方式​
const NewForm = () => {​
  // 定义一个 Action 函数​
  const submitAction = async (formData: FormData) => {​
    const name = formData.get('name');​
    console.log(`Submitting name: ${name}`);​
    // ...异步提交逻辑​
    await api.post('/users', { name });​
  };​
  ​
  return (​
    <form action={submitAction}>​
      <input type="text" name="name" />​
      <button type="submit">Submit</button>​
    </form>​
  );​
};
```

这种方式不仅代码更简洁，语义也更清晰：这个表单的“行为”（action）就是执行 `submitAction` 函数。

**服务端 Actions 与客户端 Actions**

Action 可以是定义在客户端的普通异步函数（**客户端 Action**），也可以是结合了“use server”指令、在服务端执行的函数（**服务端 Action**）。服务端 Actions 是 React Server Components 架构下的一个强大特性（通常在 Next.js 等全栈框架中使用），它允许前后端代码以前所未有的方式集成，实现无缝的 RPC 调用。在本课程中，我们将主要聚焦于客户端 Actions 的应用。​
**使用 useActionState 处理 Pending/Error/Success 状态​**

Actions 的真正威力在于它内置了对异步流程状态的管理能力。useActionState (在早期版本中被称为 useFormState) Hook 是专门为此设计的。它接收一个 Action 函数和初始状态，然后返回一个包含了当前状态、一个可被调用的新 **Action** 以及一个**pending** 状态的数组。


```
import { useActionState } from 'react';​
​
const AddToCartForm = ({ productId }) => {​
  // 定义 Action，它接收前一个状态和 formData​
  const addToCartAction = async (previousState, formData) => {​
    const quantity = formData.get('quantity');​
    const result = await addToCartApi(productId, quantity);​
    if (result.success) {​
      // 返回新的成功状态​
      return { message: 'Item added to cart!' };​
    } else {​
      // 返回新的错误状态​
      return { message: `Error: ${result.error}` };​
    }​
  };​
​
  // 使用 useActionState​
  const [state, submitAction, isPending] = useActionState(addToCartAction, null);​
​
  return (​
    <form action={submitAction}>​
      <input type="number" name="quantity" defaultValue="1" />​
      <button type="submit" disabled={isPending}>​
        {isPending ? 'Adding...' : 'Add to Cart'}​
      </button>​
      {state?.message && <p>{state.message}</p>}​
    </form>​
  );​
};
```


观察上述代码，`useActionState` 极大地简化了状态管理。我们不再需要手动创建 `useState` 来管理 `isLoading`, `error`, `successMessage`。React 已经为我们处理好了一切：​
1.当表单提交时，`isPending` 自动变为 `true`。​
2.`Action` 函数执行完毕后，`isPending` 自动变回 false。​
3.`Action` 函数的返回值会成为 `state` 的新值，从而触发 UI 更新。

**使用 useFormStatus 优化用户体验**


`useActionState` 管理的是整个表单的状态，但有时我们希望表单内的某个子组件（比如提交按钮）能够独立地响应表单的提交状态，而无需通过 props 逐层传递 `isPending`。`useFormStatus` Hook 正是为了解决这个问题而生。​
它只能在 `<form>` 组件的**子组件**中使用，并且会返回其所在表-单的当前状态信息，包括 pending, data, method 等。


```
import { useFormStatus } from 'react-dom';​
​
// 一个独立的、能感知表单状态的按钮组件​
const SubmitButton = () => {​
  // useFormStatus 获取父级 <form> 的状态​
  const { pending } = useFormStatus(); ​
​
  return (​
    <button type="submit" disabled={pending}>​
      {pending ? 'Submitting...' : 'Submit'}​
    </button>​
  );​
};​
​
// 在表单中使用​
const MyForm = () => {​
  const submitAction = async (formData) => { /* ... */ };​
  return (​
    <form action={submitAction}>​
      <input name="field" />​
      <SubmitButton /> ​
    </form>​
  );​
};
```


通过 `useFormStatus`，我们创建了一个高度解耦且可复用的 `SubmitButton` 组件。它能自动响应任何包裹它的 `<form>` 的提交状态，代码组织更加清晰。


### 并发与 use Hook


并发（Concurrency）是 React 近年来最重要的底层升级，它允许 React 在渲染过程中处理多个状态更新，并根据优先级中断和恢复渲染任务。在 React 19 中，并发特性通过一个全新的、极其强大的 use Hook 得到了更直观的体现。

**`use` Hook：在渲染中读取 Promise 和 Context**

`use` Hook 是一个可以在渲染期间“解包”数据源的 Hook。目前它支持两种数据源：**Promise** 和 **Context**。

与其他的 Hooks 不同，`use` 可以在**条件语句**、**循环或普通函数**中调用，这赋予了它前所未有的灵活性。
当 `use` 被用于一个 Promise 时，它会做一件神奇的事情：​
- 如果 Promise 正在 pending，它会“抛出”这个 Promise。​
- 这个“抛出”的行为会被最近的 `<Suspense> `边界捕获，并显示 fallback UI。​
- 当 Promise `resolve` 后，React 会重新尝试渲染该组件，此时 use Hook 会返回 Promise 的结果值。​
- 如果 Promise `reject`，错误则会被最近的 `<ErrorBoundary>` 捕获。

**结合 Suspense 实现优雅的数据加载 UI**

`use` 和 `<Suspense>` 的结合，是 React 官方推荐的、用于在客户端获取数据的方式，它彻底改变了“Fetch-on-render”的模式。

```
import { Suspense, use } from 'react';​
import { ErrorBoundary } from 'react-error-boundary';​
​
// 一个获取数据的函数，它返回一个 Promise​
const fetchMessage = () => {​
  return new Promise(resolve => setTimeout(() => resolve("Hello from the future!"), 2000));​
};​
​
// Message 组件在渲染时“读取”Promise​
const Message = ({ messagePromise }) => {​
  // 在渲染期间直接 use(promise)​
  const message = use(messagePromise);​
  return <p>Message: {message}</p>;​
};​
​
// App 组件管理 Promise 的创建和 Suspense 边界​
const App = () => {​
  // 在渲染开始前就创建 Promise​
  const messagePromise = fetchMessage();​
​
  return (​
    <div>​
      <h1>My App</h1>​
      <ErrorBoundary fallback={<p>Oops, something went wrong.</p>}>​
        <Suspense fallback={<p>⏳ Loading message...</p>}>​
          <Message messagePromise={messagePromise} />​
        </Suspense>​
      </ErrorBoundary>​
    </div>​
  );​
};
```

这种模式被称为“**Render-as-you-fetch**”。我们不再需要在 `useEffect` 中获取数据，也无需手动管理 `loading` 状态。数据获取的请求在渲染开始时就已发出，组件则声明式地等待数据就位。这避免了网络请求的瀑布流问题，并使得数据加载的 UI 逻辑变得异常简洁和健壮。

### 其他新特性

**`useOptimistic`：实现乐观更新，提升交互体验**

在与服务器交互时，为了让应用感觉更“快”，我们常常使用**乐观更新**（`Optimistic Updates`）技术。即在操作的请求还未得到服务器确认时，就先假设它会成功，并立即更新 UI。​
`useOptimistic` Hook 将这种复杂的模式变得非常简单。它接收一个当前状态，并返回一个该状态的“乐观”副本以及一个更新函数。在异步操作期间，你可以调用更新函数来设置一个临时的、乐观的状态值。当异步操作结束后，无论是成功还是失败，React 都会自动将 UI 回滚到原始的、与服务器一致的状态。


**`Asset Loading`：通过 Suspense 管理资源加载​**
在过去，我们常常会遇到样式闪烁（FOUC）或因字体未加载完成而导致的布局抖动。React 19 将样式、字体、脚本等资源的加载也整合进了 Suspense 机制。​
现在，React 能够自动检测到组件渲染所依赖的样式表或字体，并在这些资源加载完成之前，暂停渲染并显示 `<Suspense>` 的 fallback UI。这从根本上保证了用户看到的永远是内容与样式完全匹配的、完整的界面，极大地提升了用户体验的稳定性。



**`ref` 作为 Prop：简化 `forwardRef`​**

`forwardRef` 是 React 中用于将 `ref` 从父组件转发到子组件内部 DOM 节点的 API，但它的写法相对冗长和不直观。在 React 19 中，这个过程被大大简化了。现在，`ref` 可以像普通 prop 一样直接传递给函数式组件，无需再用 `forwardRef` 进行包装。


```

// 旧方式​
const MyInputOld = React.forwardRef((props, ref) => {​
  return <input ref={ref} {...props} />;​
});​
​
// React 19 新方式​
const MyInputNew = (props) => {​
  // 'ref' is now a regular prop​
  return <input ref={props.ref} {...props} />;​
};​
​
// 使用时​
const App = () => {​
  const inputRef = useRef();​
  return <MyInputNew ref={inputRef} />; // 直接传递 ref​
};
```

## React Compiler (理念篇)

在 React 的世界里，性能优化一直是一个重要课题。当应用变得复杂，组件树层级加深时，不必要的重新渲染会成为性能瓶颈。为了解决这个问题，React 提供了 `React.memo`,` useMemo` 和 `useCallback` 等一系列手动优化的工具。然而，这些工具在带来性能提升的同时，也引入了新的复杂性。React Compiler 的诞生，正是为了将开发者从这种手动优化的困境中解放出来。

### 手动优化的痛点：useMemo, useCallback 的困境

在 React 中，当一个父组件的状态或 Props 发生变化时，它会默认重新渲染其所有的子组件，即使传递给某些子组件的 Props 并未发生任何改变。为了避免这种浪费，我们可以使用 `React.memo` 来包裹子组件，使其只有在 Props 真正发生变化时才重新渲染。​
这听起来很美好，但问题随之而来。如果父组件传递给子组件的 Props 是一个对象、数组或函数，那么在每次父组件渲染时，它们都会被重新创建，导致引用地址发生变化。从 React.memo 的角度看，这等同于 Props 发生了变化，从而导致优化失效。​
为了解决这个问题，我们被迫引入了 `useMemo` 来缓存对象或复杂计算的结果，以及 `useCallback` 来缓存函数实例。


```
// 一个需要手动优化的场景​
const ParentComponent = () => {​
  const [count, setCount] = useState(0);​
  const [text, setText] = useState('');​
​
  // 如果不使用 useMemo，每次 ParentComponent 渲染，user 对象都会被重建​
  const user = useMemo(() => ({​
    name: 'Alice',​
    count: count,​
  }), [count]); // 只有 count 变化时才重新创建 user 对象​
​
  // 如果不使用 useCallback，每次 ParentComponent 渲染，handleClick 函数都会被重建​
  const handleClick = useCallback(() => {​
    console.log('Button clicked, count is:', count);​
  }, [count]); // 只有 count 变化时才重新创建 handleClick 函数​
​
  return (​
    <div>​
      <input value={text} onChange={e => setText(e.target.value)} />​
      {/* MemoizedChild 只有在 user 或 handleClick 变化时才重新渲染 */}​
      <MemoizedChild user={user} onClick={handleClick} />​
    </div>​
  );​
};
```

这种手动优化的模式带来了诸多痛点：

- **代码污染与心智负担**：`useMemo` 和 `useCallback` 的大量使用，让组件的业务逻辑变得不再纯粹，代码可读性下降。开发者必须时刻思考“这里是否需要缓存？”，“那个函数是否需要用 `useCallback` 包裹？”。​
- **依赖项数组的陷阱**：管理依赖项数组是极其繁琐且容易出错的。忘记添加依赖项会导致“陈旧闭包”的 bug；添加了不必要的依赖项则可能导致缓存频繁失效，失去优化的意义。​
- **偏离声明式初心**：React 的核心魅力在于其声明式编程。我们本应只关心“UI 该是什么样”，但手动优化却迫使我们不断地向 React 发出命令式的指令：“请记住这个值”，“请不要重新创建这个函数”，这在一定程度上违背了 React 的设计哲学。
  

### React Compiler (“Forget”)


面对手动优化的种种困境，React 团队提出了一个釜底抽薪的解决方案：一个名为 **React Compiler** 的先进编译器，其内部代号为 “**Forget**”。​
“Forget” 这个名字精准地传达了它的设计哲学：**它的目标是让开发者可以“忘记”手动性能优化这件事**。​
React Compiler 的核心理念是，**React 本就应该是默认具备高性能反应能力的（Reactive by default）**。开发者应该能够编写最直白、最简洁的 JavaScript 和 React 代码，而由工具链来自动处理那些复杂的性能优化工作。它旨在将 React 从一个需要开发者手动提示才能实现最优性能的库，转变为一个足够智能、能够自动进行精细化优化的框架。

其主要目标包括：
- **自动化记忆化（Memoization）**：自动分析代码，并智能地包裹那些可以在多次渲染间复用的值、计算和组件，等效于自动插入 `useMemo`, `useCallback` 和 `React.memo`。​
- **提升开发者体验**：将开发者从管理依赖项的苦差事中解放出来，让代码回归业务逻辑本身，使其更易于编写、阅读和维护。​
- **保持 JavaScript 语意**：编译器在进行优化时，会严格遵守 JavaScript 的语言规则，确保编译后的代码行为与源代码完全一致。


### Compiler 如何实现自动记忆化 (Memoization)

React Compiler 并非 React 运行时库的一部分，而是一个**编译时工具**（通常作为 Babel 插件）。它在项目构建打包的过程中，对源代码进行深度分析和重写。


它的工作原理（在一个较高的层次上）可以这样理解：

- **深度静态分析**：编译器会像一个经验丰富的 React 开发者一样“阅读”你的组件代码。但它比任何人都更严谨、更不知疲倦。它能够理解 React 的规则（比如 props 和 state 的不可变性），也能够理解 JavaScript 的语义。​
- **建模与依赖追踪**：它会构建出组件内所有值、对象、函数之间的依赖关系图。它能精确地知道，当某个 state 或 prop 变化时，到底会影响到哪些下游的计算和值。​
- **智能代码重写**：基于分析结果，编译器会识别出那些计算成本较高或作为 props 传递且在多次渲染中可能保持不变的部分。然后，它会自动地、安全地将这些部分用缓存机制（类似于 useMemo）包裹起来。由于它拥有全局的依赖视图，它生成的“依赖项数组”远比手动维护的要精确。

本质上，React Compiler 将性能优化的职责从**开发者**转移到了**工具链**。它通过在编译时进行一次性的、深入的分析，来换取运行时的高效以及开发时的简洁。​


## 高级 Hooks 与状态管理​
​

随着应用功能的日益复杂，简单的` useState `已经不足以应对所有的状态管理需求。组件之间的数据共享、复杂状态的逻辑流转、以及伴随而来的性能问题，都对我们提出了更高的要求。本章将深入探讨 React 提供的更高级的状态管理工具，以及如何封装和复用我们的状态逻辑

### 复杂状态逻辑：useReducer vs useState

我们已经熟练掌握了 `useState`，它非常适合处理简单的、独立的状态，如布尔值、字符串或数字。但当一个状态对象包含多个关联的字段，或者状态的下一个值依赖于前一个值的复杂计算时，`useState` 的更新逻辑就会散落在各个事件处理函数中，变得难以维护。​
为了应对这种场景，React 提供了另一个内置的 Hook：`useReducer`。它借鉴了 `Redux` 的思想，是一种将状态更新逻辑从组件中分离出来并集中管理的模式。

`useReducer` 接收一个 **reducer** 函数 和一个**初始状态**，返回当前的状态和一个 `dispatch` 函数。​
- **Reducer 函数**: 这是一个纯函数，它接收当前的状态（state）和一个动作（action）对象作为参数，然后返回一个全新的状态。所有状态如何变化的逻辑都定义在这里。​
- **Action 对象**: 这是一个普通的 JavaScript 对象，通常包含一个 `type` 字段来描述操作类型，以及一个可选的 payload 字段来传递数据。​
- **Dispatch 函数**: 我们在事件处理函数中调用 `dispatch(action)` 来“派发”一个动作。这会触发 React 调用我们的 reducer 函数，用它返回的新状态来更新 UI。

让我们用一个经典的购物车计数器例子来对比两者：
```
// 使用 useReducer 来管理更复杂的 state​
import { useReducer } from 'react';​
​
// 1. 定义 state 的类型和初始 state​
const initialState = { count: 0, lastAction: null };​
type State = typeof initialState;​
​
// 2. 定义 action 的类型​
type Action = { type: 'increment'; payload: number } | { type: 'decrement'; payload: number } | { type: 'reset' };​
​
// 3. 编写 reducer 函数，集中处理所有状态转换逻辑​
function reducer(state: State, action: Action): State {​
  switch (action.type) {​
    case 'increment':​
      return { count: state.count + action.payload, lastAction: 'increment' };​
    case 'decrement':​
      return { count: state.count - action.payload, lastAction: 'decrement' };​
    case 'reset':​
      return { count: 0, lastAction: 'reset' };​
    default:​
      throw new Error();​
  }​
}​
​
const Counter = () => {​
  // 4. 在组件中使用 useReducer​
  const [state, dispatch] = useReducer(reducer, initialState);​
​
  return (​
    <>​
      <p>Count: {state.count} (Last action: {state.lastAction})</p>​
      {/* 5. 通过 dispatch 派发 action 来触发状态更新 */}​
      <button onClick={() => dispatch({ type: 'increment', payload: 1 })}>+1</button>​
      <button onClick={() => dispatch({ type: 'decrement', payload: 1 })}>-1</button>​
  );​
};
```

**何时选择 useReducer**

- 当状态逻辑非常复杂，涉及多个子值时。​
- 当下一个状态严重依赖于前一个状态时。​
- 当你想将状态变更的逻辑提取出组件，以便于独立测试和维护时。​
- 在多人协作的大型项目中，useReducer 提供了更可预测和严格的状态流。​
- 对于简单场景，useState 依然是更简洁的选择。


### 全局状态管理：useContext 与性能陷阱

当多个散落在组件树不同位置的组件需要共享同一个状态时（例如，当前登录的用户信息、全局的主题设置），逐层通过 props 传递数据会变得非常繁琐和低效，这种现象被称为“**Prop Drilling**”（属性钻探）。​
为了解决这个问题，React 提供了 **Context API**。它允许我们创建一个全局的数据“广播站”，任何在这个“广播站”覆盖范围内的组件，都可以直接“收听”到这份数据，而无需关心它们在组件树中的层级深度。​
使用 Context 主要分为三步：​
- `createContext`: 在应用的上层创建一个 Context 对象。​
- `Provider`: 使用 MyContext.Provider 组件将需要共享的数据通过 value 属性“广播”出去。这个 Provider 会包裹住所有可能需要这份数据的子组件。​
- `useContext`: 在任何一个子组件中，通过 useContext(MyContext) Hook 来“订阅”并获取这份数据。

```
// 1. 创建一个 ThemeContext​
const ThemeContext = createContext('light');​
​
// App.tsx​
const App = () => {​
  const [theme, setTheme] = useState('light');​
  return (​
    // 2. 使用 Provider 提供当前的 theme 值​
    <ThemeContext.Provider value={theme}>​
      <Toolbar />​
      <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>​
        Toggle Theme​
      </button>​
    </ThemeContext.Provider>​
  );​
};​
​
// Toolbar.tsx - 中间组件，无需关心 theme​
const Toolbar = () => <ThemedButton />;​
​
// ThemedButton.tsx - 深度嵌套的子组件​
const ThemedButton = () => {​
  // 3. 直接通过 useContext 获取 theme​
  const theme = useContext(ThemeContext);​
  return <button style={{ background: theme === 'dark' ? '#333' : '#FFF' }}>I am a themed button</button>;​
};
```

性能陷阱​
Context 虽然强大，但它有一个重要的性能特征：当 Provider 的 value 发生变化时，所有消费该 Context 的组件（即调用了 useContext 的组件）都会被强制重新渲染。即使这些组件只关心 `value` 对象中的一小部分数据，只要 value 的引用地址发生变化，它们也会被波及。​
如果 `value` 是一个复杂的对象，并且在父组件的每次渲染中都被重新创建，这可能会导致不必要的性能开销。解决方案通常是结合 `useMemo` 来缓存 `value` 对象，或者将一个大的 Context 拆分成多个更细粒度的 `Context`

### 手动性能优化：React.memo, useMemo, useCallback 的正确使用场景

正如`React Compiler` 的目标是自动化性能优化。但在它完全成熟和普及之前，或者在某些需要精细调优的场景下，理解手动优化的工具仍然是一项必备技能。​
- **React.memo**: 这是一个高阶组件，用于包裹你的函数式组件。它会对传入的 props 进行浅比较，只有在 props 发生变化时，才会重新渲染被包裹的组件。这是防止因父组件渲染而导致的不必要子组件渲染的主要工具。​
- **useMemo**: 这个 Hook 用于“记忆化”一个计算结果。它接收一个函数和一个依赖项数组，只有在依赖项发生变化时，才会重新执行该函数并返回新的值。它主要用于两个场景：​
  &emsp;&emsp;a. 缓存开销巨大的计算结果，避免在每次渲染时都重复计算。​
  &emsp;&emsp;b.当向一个被 React.memo 包裹的子组件传递对象或数组作为 prop 时，使用 useMemo 来保证该 prop 的引用稳定性。​
- **useCallback**: 这个 Hook 用于“记忆化”一个函数实例。它与 useMemo 类似，但专门用于函数。主要使用场景是：当向一个被 React.memo 包裹的子组件传递函数作为 prop 时，使用 useCallback 来保证该函数 prop 的引用稳定性。

>**核心原则：不要过早优化**。这些 API 自身也有成本（内存占用和比较开销）。只在你通过 React DevTools Profiler 等工具确认了某个组件存在性能瓶颈时，才应该考虑使用它们进行优化。

### 自定义 Hooks：封装逻辑与实现复用 (含 TS 泛型)


自定义 Hook 是现代 React 中实现逻辑复用的基石。它是一个以 use 开头的 JavaScript 函数，其内部可以调用其他的 Hooks（如 `useState`, `useEffect` 等）。通过自定义 Hook，我们可以将组件中可复用的**状态逻辑**（而非 UI）提取出来，让组件本身保持简洁，只关注于渲染。​

假设我们有多个组件都需要从本地存储（LocalStorage）中读取和写入数据，我们可以创建一个 `useLocalStorageState` 的自定义 Hook。

```
import { useState, useEffect } from 'react';​
​
// 自定义 Hook - 使用了 TypeScript 泛型 <T>​
function useLocalStorageState<T>(key: string, defaultValue: T): [T, React.Dispatch<React.SetStateAction<T>>] {​
  // 1. 从 localStorage 读取初始值​
  const [state, setState] = useState<T>(() => {​
    const storedValue = localStorage.getItem(key);​
    return storedValue !== null ? JSON.parse(storedValue) : defaultValue;​
  });​
​
  // 2. 每当 state 变化时，将其写入 localStorage​
  useEffect(() => {​
    localStorage.setItem(key, JSON.stringify(state));​
  }, [key, state]);​
​
  return [state, setState];​
}​
​
// 在组件中使用自定义 Hook​
const UserSettings = () => {​
  const [theme, setTheme] = useLocalStorageState<'light' | 'dark'>('theme', 'light');​
  const [fontSize, setFontSize] = useLocalStorageState<number>('fontSize', 16);​
​
  // ... UI to change theme and font size​
};
```

在这个例子中，我们使用了 TypeScript 的**泛型 T**。这使得我们的 `useLocalStorageState` Hook 可以适用于任何可被 JSON 序列化的数据类型，无论是字符串、数字还是对象，同时保持了完整的类型安全。这就是自定义 Hook 结合 TypeScript 的强大之处：创建高度可复用、类型安全且与 UI 无关的逻辑单元

## TypeScript 高级应用


### 泛型组件与泛型 Hooks​
​
我们已经在自定义 Hook 中见识了泛型的威力，同样的能力也可以被应用在**泛型组件**上。泛型组件允许我们在定义组件时不预先写死其处理的数据类型，而是由使用该组件的父组件来指定。​
这在创建可复用的列表、表格、下拉菜单等 UI 模式时非常有用。例如，我们可以创建一个可以渲染任何类型数据数组的 `List` 组件。


```
import React from 'react';​
​
// 定义泛型 Props 类型​
// <T> 是一个类型变量，在使用组件时会被具体类型替换​
type ListProps<T> = {​
  items: T[]; // items 是一个 T 类型的数组​
  renderItem: (item: T) => React.ReactNode; // renderItem 函数接收一个 T 类型的参数​
};​
​
// 定义泛型组件 List<T>​
export function List<T>({ items, renderItem }: ListProps<T>) {​
  return (​
    <ul>​
      {items.map((item, index) => (​
        // 这里 item 的类型被正确推断为 T​
        <li key={index}>{renderItem(item)}</li>​
      ))}​
    </ul>​
  );​
}​
​
// 使用泛型组件​
type User = { id: number; name: string };​
const users: User[] = [{ id: 1, name: 'Alice' }];​
​
type Product = { sku: string; price: number };​
const products: Product[] = [{ sku: 'X123', price: 99.9 }];​
​
const App = () => (​
  <>​
    {/* 此时，T 被指定为 User */}​
    <List<User>​
      items={users}​
  </>​
);
```

通过泛型，我们创建了一个高度抽象且完全类型安全的 `List` 组件，它将“渲染什么”的逻辑（renderItem）交给了调用者，而自己只负责“如何渲染”（列表结构）的逻辑。


### React 事件对象的精确类型

在事件处理函数中，为事件对象 e 提供精确的类型，可以帮助我们安全地访问特定于该事件的属性（如 `e.target.value`），并获得编辑器的智能提示。`@types/react` 包为我们预定义了丰富的事件类型。​
放弃使用宽泛的 `any` 或 `React.SyntheticEvent`，转而使用更具体的类型是一个好习惯：

- **鼠标事件**: `React.MouseEvent<HTMLElement>​`

```
const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {​
  // e.currentTarget 的类型是 HTMLButtonElement​
  console.log(e.currentTarget.tagName); // "BUTTON"​
};
```

- **表单元素变化事件**: `React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>​`

```
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {​
  // e.target.value 的类型被正确推断为 string​
  setValue(e.target.value);​
};
```

- **表单提交事件**: `React.FormEvent<HTMLFormElement>​`

```
const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {​
  e.preventDefault();​
  // e.currentTarget 的类型是 HTMLFormElement​
  console.log('Form submitted');​
};
```

使用精确的事件类型，可以让我们的代码更加健壮，有效防止因访问不存在的属性而导致的运行时错误。


### 结合 Zod 进行运行时类型校验​


TypeScript 的类型系统在**编译时**为我们提供了强大的保护，但这份保护在应用的“边界”处会失效——尤其是当我们从外部 API 接收数据时。API 返回的数据结构可能与我们预期的 TypeScript 类型不符，这可能导致运行时错误。​
为了弥补这一短板，我们引入**运行时类型校验库**，其中 **Zod** 是当前最流行和强大的选择。Zod 允许我们定义一个数据的 schema（模式），然后用它来解析（parse）未知来源的数据。
​

```
import { z } from 'zod';​
​
// 1. 使用 Zod 定义 User 的 schema​
const UserSchema = z.object({​
  id: z.string(),​
  name: z.string(),​
  email: z.string().email(),​
  isAdmin: z.boolean().optional(),​
});​
​
// 2. 从 Zod schema 推断出 TypeScript 类型​
type User = z.infer<typeof UserSchema>;​
​
// 在数据获取函数中使用​
async function fetchUser(userId: string): Promise<User> {​
  const response = await fetch(`/api/users/${userId}`);​
  const data = await response.json();​
​
  try {​
    // 3. 使用 schema.parse 来校验和解析数据​
    // 如果数据结构不符合 schema，这里会抛出一个详细的错误​
    const user = UserSchema.parse(data);​
    return user;​
  } catch (error) {​
    console.error('API data validation failed:', error);​
    throw new Error('Invalid user data received from server.');​
  }​
}
```


“TypeScript + Zod”是一个黄金组合。我们只需维护一份 Zod schema，就可以同时获得运行时的安全校验和编译时的静态类型提示（通过 z.infer），极大地提升了处理外部数据的健壮性。

### 高级类型工具 (Utility Types) 在组件 Props 中的应用

TypeScript 内置了一系列**高级类型工具（Utility Types）**，它们就像是操作类型的函数，可以基于已有类型创建出新的、衍生出的类型。在定义复杂的组件 Props 时，它们非常有用，可以帮助我们避免重复定义，保持类型的一致性。​
一些在 React 中常用的高级类型工具包括：​
- `Partial<Type>`: 将 `Type` 中的所有属性变为可选。​
- `Required<Type>`: 将 `Type` 中的所有属性变为必选。​
- `Pick<Type, Keys>`: 从 `Type` 中挑选出指定的 `Keys` 属性来创建一个新类型。​
- `Omit<Type, Keys>`: 从 `Type` 中排除掉指定的 `Keys` 属性来创建一个新类型。​
结合 React 自带的 `ComponentProps` 类型，我们可以实现非常灵活的 Props 定义。例如，创建一个自定义 `Button` 组件，它继承原生 `<button>` 的所有属性，但我们想自定义 `onClick` 的行为。​
​

```
import React from 'react';​
​
// 使用 Omit 来排除原生的 onClick，因为我们要自定义它​
type ButtonProps = Omit<React.ComponentProps<'button'>, 'onClick'> & {​
  // 自定义我们的 onClick prop​
  onClick: (source: 'custom-button') => void;​
  variant: 'primary' | 'secondary';​
};​
​
export const CustomButton = ({ onClick, variant, ...rest }: ButtonProps) => {​
  const handleClick = () => {​
    onClick('custom-button');​
  };​
​
  return (​
    <button​
      onClick={handleClick}​
      // 其他所有原生 button 属性都通过 ...rest 透传下去​
      // 例如 disabled, type, className 等​
      {...rest} ​
      style={{ backgroundColor: variant === 'primary' ? 'blue' : 'gray' }}​
    />​
  );​
};
```

通过这种方式，我们创建的 `CustomButton` 组件既拥有了强类型的自定义 `props (variant, onClick)`，又继承了原生按钮的所有能力，同时保持了极高的灵活性和类型安全。