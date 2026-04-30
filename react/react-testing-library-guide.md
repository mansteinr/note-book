# React Testing Library：核心测试哲学与实践指南

## 目录
- [一、React Testing Library 概述](#一react-testing-library-概述)
- [二、核心测试哲学](#二核心测试哲学)
- [三、安装与配置](#三安装与配置)
- [四、核心 API 深度解析](#四核心-api-深度解析)
- [五、实际测试示例](#五实际测试示例)
- [六、高级测试技巧](#六高级测试技巧)
- [七、最佳实践与常见问题](#七最佳实践与常见问题)
- [八、与其他测试工具对比](#八与其他测试工具对比)
- [九、总结与决策指南](#九总结与决策指南)

## 一、React Testing Library 概述

### 1.1 什么是 React Testing Library
React Testing Library 是一套轻量级的测试工具，用于测试 React 组件。它建立在 DOM Testing Library 之上，专门为 React 应用设计，提供了简单而强大的 API 来测试用户交互行为。

### 1.2 核心特性
1. **用户导向**：模拟真实用户行为
2. **易于使用**：简洁直观的 API
3. **可维护性**：测试代码贴近实际使用
4. **无障碍友好**：促进可访问性实践
5. **框架无关**：可与 Jest、Vitest 等测试框架配合

### 1.3 主要组成部分
- **@testing-library/react**：React 组件测试
- **@testing-library/jest-dom**：Jest 匹配器扩展
- **@testing-library/user-event**：模拟用户交互
- **@testing-library/dom**：底层 DOM 操作

### 1.4 发展历史
React Testing Library 源自 Kent C. Dodds 创建的 Testing Library 家族，旨在解决传统测试方法中的问题，如过度关注实现细节、测试脆弱性等。

## 二、核心测试哲学

### 2.1 核心原则
> **"The more your tests resemble the way your software is used, the more confidence they can give you."**
> 
> 测试越接近软件的实际使用方式，就越给人信心。

### 2.2 三大核心原则

#### 2.2.1 原则一：测试用户行为，而非实现细节

**传统测试（不推荐）：**
```javascript
// ❌ 测试实现细节
test('renders correctly', () => {
  const { container } = render(<Button />);
  
  // 测试内部类名 - 实现细节
  expect(container.querySelector('.btn-primary')).toBeInTheDocument();
  
  // 测试内部状态 - 实现细节
  expect(Button.prototype.state).toBe('idle');
  
  // 测试内部方法调用 - 实现细节
  jest.spyOn(Button.prototype, 'handleClick');
});
```

**React Testing Library（推荐）：**
```javascript
// ✅ 测试用户行为
test('clicks when clicked', () => {
  const handleClick = jest.fn();
  render(<Button onClick={handleClick}>点击我</Button>);
  
  // 模拟用户点击
  fireEvent.click(screen.getByText('点击我'));
  
  // 验证用户期望的结果
  expect(handleClick).toHaveBeenCalledTimes(1);
});
```

#### 2.2.2 原则二：像用户一样查询元素

**查询优先级：**
```
1. getByRole()          // 最推荐 - 可访问性
2. getByLabelText()      // 表单元素
3. getByPlaceholderText() // 表单占位符
4. getByText()          // 文本内容
5. getByDisplayValue()   // 表单当前值
6. getByAltText()       // 图片 alt 文本
7. getByTitle()         // title 属性
8. getByTestId()        // 最后选择 - 仅用于无其他选项
```

**示例：**
```javascript
// ✅ 优先使用 role
const button = screen.getByRole('button', { name: '提交' });

// ✅ 表单元素使用 label
const input = screen.getByLabelText('用户名');

// ✅ 文本内容查询
const heading = screen.getByText('欢迎页面');

// ❌ 避免使用 testId（除非必要）
const element = screen.getByTestId('submit-button');
```

#### 2.2.3 原则三：使用可访问性查询

**为什么可访问性重要：**
1. **更好的测试**：确保应用对所有用户可用
2. **更稳定的测试**：可访问性 API 更稳定
3. **法律合规**：满足可访问性法规要求
4. **更好的用户体验**：提升整体用户体验

**可访问性查询示例：**
```javascript
// ✅ 使用 role 查询
const button = screen.getByRole('button');
const navigation = screen.getByRole('navigation');
const dialog = screen.getByRole('dialog');

// ✅ 使用 label 查询表单元素
const emailInput = screen.getByLabelText('邮箱地址');
const passwordInput = screen.getByLabelText('密码');

// ✅ 使用 name 选项精确定位
const submitButton = screen.getByRole('button', { 
  name: /提交/i 
});

// ❌ 避免使用 CSS 选择器
const button = container.querySelector('.btn-submit');
```

### 2.4 测试金字塔

```
        E2E Tests
       /          \
      /            \
     /              \
    /                \
   /                  \
  /  Integration Tests   \
 /                      \
/__________________________\
        Unit Tests
```

**建议比例：**
- **单元测试**：70% - 快速、大量
- **集成测试**：20% - 关键流程
- **E2E 测试**：10% - 核心用户旅程

## 三、安装与配置

### 3.1 安装依赖

```bash
# npm
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event

# yarn
yarn add --dev @testing-library/react @testing-library/jest-dom @testing-library/user-event

# pnpm
pnpm add -D @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

### 3.2 Jest 配置

```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|webp|svg)$': '<rootDir>/__mocks__/fileMock.js',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
    '!src/**/__tests__/**',
  ],
};
```

### 3.3 设置文件

```javascript
// jest.setup.js
import '@testing-library/jest-dom';

// 全局配置
global.IS_REACT_ACT_ENVIRONMENT = true;

// 模拟 matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});
```

### 3.4 TypeScript 配置

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
  },
});
```

## 四、核心 API 深度解析

### 4.1 render 函数

```javascript
import { render, screen } from '@testing-library/react';

// 基本渲染
render(<App />);

// 带选项渲染
render(<App />, {
  container: document.body, // 自定义容器
  baseElement: document.body, // 基础元素
  hydrate: false, // 是否水合
  wrapper: ({ children }) => (
    <ThemeProvider theme={theme}>
      {children}
    </ThemeProvider>
  ),
});

// 返回值解构
const { container, debug, rerender, unmount } = render(<App />);

// container - 组件容器
// debug - 调试函数
// rerender - 重新渲染
// unmount - 卸载组件
```

### 4.2 查询函数

#### 4.2.1 getBy 系列（找不到时抛出错误）
```javascript
// 必须找到元素，否则测试失败
const button = screen.getByRole('button');
const heading = screen.getByText('标题');
const input = screen.getByLabelText('用户名');

// 适合：验证元素存在
```

#### 4.2.2 queryBy 系列（找不到时返回 null）
```javascript
// 可能找不到元素
const button = screen.queryByRole('button');
if (button) {
  // 元素存在时的逻辑
}

// 适合：条件性验证
```

#### 4.2.3 findBy 系列（异步查询）
```javascript
// 等待元素出现
const button = await screen.findByRole('button');
const dialog = await screen.findByRole('dialog');

// 适合：异步加载的元素
```

#### 4.2.4 getAllBy、queryAllBy、findAllBy 系列
```javascript
// 查询多个元素
const buttons = screen.getAllByRole('button');
const items = screen.queryAllByText('项目');

// 适合：验证元素数量
expect(buttons).toHaveLength(3);
```

### 4.3 用户交互模拟

```javascript
import { fireEvent, userEvent } from '@testing-library/user-event';

// 使用 userEvent（推荐）
const user = userEvent.setup();

test('表单提交', async () => {
  render(<LoginForm />);
  
  // 模拟用户输入
  await user.type(
    screen.getByLabelText('用户名'),
    'testuser'
  );
  await user.type(
    screen.getByLabelText('密码'),
    'password123'
  );
  
  // 模拟用户点击
  await user.click(
    screen.getByRole('button', { name: '登录' })
  );
  
  // 验证结果
  expect(screen.getByText('登录成功')).toBeInTheDocument();
});

// 使用 fireEvent（低级）
test('鼠标悬停', () => {
  render(<Tooltip text="提示内容">悬停我</Tooltip>);
  
  const trigger = screen.getByText('悬停我');
  fireEvent.mouseEnter(trigger);
  
  expect(screen.getByText('提示内容')).toBeInTheDocument();
});
```

### 4.4 等待与异步处理

```javascript
import { waitFor, within } from '@testing-library/react';

// waitFor - 等待条件满足
test('异步数据加载', async () => {
  render(<UserProfile userId={1} />);
  
  await waitFor(() => {
    expect(screen.getByText('用户资料')).toBeInTheDocument();
  }, {
    timeout: 3000, // 超时时间
    interval: 100, // 检查间隔
  });
});

// waitForElementToBeRemoved - 等待元素消失
test('加载状态消失', async () => {
  render(<DataLoader />);
  
  const loading = screen.getByText('加载中...');
  await waitForElementToBeRemoved(loading);
  
  expect(screen.getByText('数据加载完成')).toBeInTheDocument();
});
```

### 4.5 调试工具

```javascript
{ debug } = render(<Component />);

// debug() - 打印当前 DOM
debug();

// debug(element) - 打印特定元素
debug(screen.getByRole('button'));

// prettyDOM() - 格式化 DOM
import { prettyDOM } from '@testing-library/dom';
console.log(prettyDOM(container));

// logTestingPlaygroundURL() - 生成调试 URL
import { logTestingPlaygroundURL } from '@testing-library/dom';
logTestingPlaygroundURL(container);
```

## 五、实际测试示例

### 5.1 基础组件测试

```javascript
// Button.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('Button 组件', () => {
  test('渲染按钮文本', () => {
    render(<Button>点击我</Button>);
    expect(screen.getByText('点击我')).toBeInTheDocument();
  });

  test('处理点击事件', async () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>点击我</Button>);
    
    const user = userEvent.setup();
    await user.click(screen.getByRole('button'));
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('禁用状态', () => {
    render(<Button disabled>禁用按钮</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  test('加载状态', () => {
    render(<Button loading>提交中...</Button>);
    
    expect(screen.getByRole('button')).toBeDisabled();
    expect(screen.getByText('提交中...')).toBeInTheDocument();
  });
});
```

### 5.2 表单组件测试

```javascript
// LoginForm.test.js
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('LoginForm 组件', () => {
  test('完整登录流程', async () => {
    const onSubmit = jest.fn();
    render(<LoginForm onSubmit={onSubmit} />);
    
    const user = userEvent.setup();
    
    // 填写表单
    await user.type(screen.getByLabelText('用户名'), 'testuser');
    await user.type(screen.getByLabelText('密码'), 'password123');
    
    // 提交表单
    await user.click(screen.getByRole('button', { name: '登录' }));
    
    // 验证提交数据
    expect(onSubmit).toHaveBeenCalledWith({
      username: 'testuser',
      password: 'password123',
    });
  });

  test('表单验证', async () => {
    render(<LoginForm />);
    
    const user = userEvent.setup();
    
    // 提交空表单
    await user.click(screen.getByRole('button', { name: '登录' }));
    
    // 验证错误消息
    expect(screen.getByText('请输入用户名')).toBeInTheDocument();
    expect(screen.getByText('请输入密码')).toBeInTheDocument();
  });

  test('密码显示切换', async () => {
    render(<LoginForm />);
    
    const user = userEvent.setup();
    const passwordInput = screen.getByLabelText('密码');
    const toggleButton = screen.getByRole('button', { name: /显示密码/i });
    
    // 初始状态：密码隐藏
    expect(passwordInput).toHaveAttribute('type', 'password');
    
    // 点击切换
    await user.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'text');
    
    // 再次切换
    await user.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'password');
  });
});
```

### 5.3 异步组件测试

```javascript
// UserProfile.test.js
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('UserProfile 组件', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('加载用户数据', async () => {
    // 模拟 API 响应
    mockFetchUser.mockResolvedValue({
      id: 1,
      name: '张三',
      email: 'zhangsan@example.com',
    });

    render(<UserProfile userId={1} />);

    // 等待加载完成
    await waitFor(() => {
      expect(screen.getByText('张三')).toBeInTheDocument();
      expect(screen.getByText('zhangsan@example.com')).toBeInTheDocument();
    });
  });

  test('处理加载错误', async () => {
    mockFetchUser.mockRejectedValue(new Error('网络错误'));

    render(<UserProfile userId={1} />);

    await waitFor(() => {
      expect(screen.getByText('加载失败')).toBeInTheDocument();
      expect(screen.getByText('网络错误')).toBeInTheDocument();
    });
  });

  test('显示加载状态', () => {
    mockFetchUser.mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    );

    render(<UserProfile userId={1} />);

    expect(screen.getByText('加载中...')).toBeInTheDocument();
  });
});
```

### 5.4 列表组件测试

```javascript
// TodoList.test.js
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('TodoList 组件', () => {
  const initialTodos = [
    { id: 1, text: '学习 React', completed: false },
    { id: 2, text: '编写测试', completed: true },
  ];

  test('渲染待办事项列表', () => {
    render(<TodoList todos={initialTodos} />);

    expect(screen.getByText('学习 React')).toBeInTheDocument();
    expect(screen.getByText('编写测试')).toBeInTheDocument();
  });

  test('添加新任务', async () => {
    const onAdd = jest.fn();
    render(<TodoList todos={initialTodos} onAdd={onAdd} />);

    const user = userEvent.setup();
    
    await user.type(screen.getByPlaceholderText('添加新任务'), '新任务');
    await user.click(screen.getByRole('button', { name: '添加' }));

    expect(onAdd).toHaveBeenCalledWith('新任务');
  });

  test('切换任务状态', async () => {
    const onToggle = jest.fn();
    render(<TodoList todos={initialTodos} onToggle={onToggle} />);

    const user = userEvent.setup();
    const firstTodo = screen.getByText('学习 React');
    
    await user.click(firstTodo);

    expect(onToggle).toHaveBeenCalledWith(1);
  });

  test('删除任务', async () => {
    const onDelete = jest.fn();
    render(<TodoList todos={initialTodos} onDelete={onDelete} />);

    const user = userEvent.setup();
    const deleteButton = screen.getByRole('button', { name: /删除/i });
    
    await user.click(deleteButton);

    expect(onDelete).toHaveBeenCalledWith(1);
  });
});
```

### 5.5 模态框组件测试

```javascript
// Modal.test.js
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('Modal 组件', () => {
  test('打开模态框', async () => {
    render(
      <>
        <button onClick={openModal}>打开</button>
        <Modal isOpen={isOpen} onClose={closeModal}>
          <h2>模态框标题</h2>
          <p>模态框内容</p>
        </Modal>
      </>
    );

    const user = userEvent.setup();
    
    // 模态框初始关闭
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();

    // 打开模态框
    await user.click(screen.getByText('打开'));
    
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('模态框标题')).toBeInTheDocument();
    });
  });

  test('关闭模态框', async () => {
    render(
      <Modal isOpen={true} onClose={closeModal}>
        <h2>模态框标题</h2>
        <button onClick={closeModal}>关闭</button>
      </Modal>
    );

    const user = userEvent.setup();
    
    // 点击关闭按钮
    await user.click(screen.getByRole('button', { name: '关闭' }));
    
    await waitForElementToBeRemoved(() => 
      screen.queryByRole('dialog')
    );
  });

  test('点击遮罩层关闭', async () => {
    render(
      <Modal isOpen={true} onClose={closeModal}>
        <h2>模态框标题</h2>
      </Modal>
    );

    const user = userEvent.setup();
    
    // 点击遮罩层
    await user.click(screen.getByRole('dialog'));
    
    expect(closeModal).toHaveBeenCalled();
  });

  test('焦点管理', async () => {
    render(
      <>
        <input id="outside" />
        <Modal isOpen={true} onClose={closeModal}>
          <input id="inside" autoFocus />
        </Modal>
      </>
    );

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    // 验证焦点在模态框内
    expect(screen.getByRole('dialog')).toHaveFocus();
  });
});
```

## 六、高级测试技巧

### 6.1 自定义渲染函数

```javascript
// test-utils.js
import { render } from '@testing-library/react';
import { ThemeProvider } from './theme';

const customRender = (ui, options = {}) => {
  const AllTheProviders = ({ children }) => {
    return (
      <ThemeProvider theme={defaultTheme}>
        <AuthProvider>
          <Router>
            {children}
          </Router>
        </AuthProvider>
      </ThemeProvider>
    );
  };

  return render(ui, {
    wrapper: AllTheProviders,
    ...options,
  });
};

export * from '@testing-library/react';
export { customRender as render };
```

### 6.2 测试 Hook

```javascript
// useCounter.test.js
import { renderHook, act } from '@testing-library/react';

describe('useCounter Hook', () => {
  test('初始值为 0', () => {
    const { result } = renderHook(() => useCounter());
    expect(result.current.count).toBe(0);
  });

  test('增加计数', () => {
    const { result } = renderHook(() => useCounter());
    
    act(() => {
      result.current.increment();
    });
    
    expect(result.current.count).toBe(1);
  });

  test('减少计数', () => {
    const { result } = renderHook(() => useCounter());
    
    act(() => {
      result.current.decrement();
    });
    
    expect(result.current.count).toBe(-1);
  });

  test('重置计数', () => {
    const { result } = renderHook(() => useCounter());
    
    act(() => {
      result.current.increment();
      result.current.increment();
      result.current.reset();
    });
    
    expect(result.current.count).toBe(0);
  });
});
```

### 6.3 测试 Context

```javascript
// ThemeContext.test.js
import { render, screen } from '@testing-library/react';

describe('ThemeContext', () => {
  test('提供主题给子组件', () => {
    const customTheme = {
      colors: {
        primary: 'red',
        secondary: 'blue',
      },
    };

    render(
      <ThemeProvider theme={customTheme}>
        <ThemeConsumer />
      </ThemeProvider>
    );

    expect(screen.getByText('Primary: red')).toBeInTheDocument();
    expect(screen.getByText('Secondary: blue')).toBeInTheDocument();
  });

  test('切换主题', async () => {
    const { rerender } = render(
      <ThemeProvider theme={lightTheme}>
        <ThemeConsumer />
      </ThemeProvider>
    );

    expect(screen.getByText('Light Theme')).toBeInTheDocument();

    rerender(
      <ThemeProvider theme={darkTheme}>
        <ThemeConsumer />
      </ThemeProvider>
    );

    expect(screen.getByText('Dark Theme')).toBeInTheDocument();
  });
});
```

### 6.4 测试路由

```javascript
// Router.test.js
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

describe('路由测试', () => {
  test('渲染正确路由', () => {
    render(
      <MemoryRouter initialEntries={['/about']}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('关于我们')).toBeInTheDocument();
  });

  test('路由参数', () => {
    render(
      <MemoryRouter initialEntries={['/users/123']}>
        <Routes>
          <Route path="/users/:id" element={<UserDetail />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('用户 ID: 123')).toBeInTheDocument();
  });

  test('导航测试', async () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );

    const user = userEvent.setup();
    
    await user.click(screen.getByText('关于我们'));
    
    expect(screen.getByText('关于我们')).toBeInTheDocument();
  });
});
```

### 6.5 模拟 API 和外部依赖

```javascript
// api.test.js
import { render, screen, waitFor } from '@testing-library/react';

// 模拟 fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ data: 'test' }),
  })
);

describe('API 测试', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('成功获取数据', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ name: '测试数据' }),
    });

    render(<DataFetcher />);

    await waitFor(() => {
      expect(screen.getByText('测试数据')).toBeInTheDocument();
    });

    expect(fetch).toHaveBeenCalledWith('/api/data');
  });

  test('处理 API 错误', async () => {
    fetch.mockRejectedValueOnce(new Error('网络错误'));

    render(<DataFetcher />);

    await waitFor(() => {
      expect(screen.getByText('加载失败')).toBeInTheDocument();
    });
  });
});
```

## 七、最佳实践与常见问题

### 7.1 最佳实践

#### 7.1.1 测试命名规范
```javascript
// ✅ 好的测试命名
describe('Button 组件', () => {
  test('当点击时调用 onClick 处理函数', () => {});
  test('当禁用时不可点击', () => {});
  test('当加载时显示加载状态', () => {});
});

// ❌ 不好的测试命名
describe('Button', () => {
  test('test1', () => {});
  test('button click', () => {});
  test('disabled', () => {});
});
```

#### 7.1.2 测试组织结构
```javascript
// 按功能组织测试
describe('用户认证', () => {
  describe('登录功能', () => {
    test('成功登录', () => {});
    test('失败登录', () => {});
  });

  describe('注册功能', () => {
    test('成功注册', () => {});
    test('验证错误', () => {});
  });
});
```

#### 7.1.3 测试隔离
```javascript
// 每个测试前重置状态
beforeEach(() => {
  jest.clearAllMocks();
  localStorage.clear();
});

// 测试后清理
afterEach(() => {
  cleanup();
});
```

#### 7.1.4 使用描述性断言
```javascript
// ✅ 描述性断言
expect(button).toBeDisabled();
expect(input).toHaveValue('test');
expect(element).toHaveClass('active');

// ❌ 不够清晰
expect(button.disabled).toBe(true);
expect(input.value).toBe('test');
expect(element.classList.contains('active')).toBe(true);
```

### 7.2 常见问题与解决方案

#### 7.2.1 问题：测试不稳定（Flaky Tests）

**原因：**
- 异步操作未正确等待
- 定时器未清理
- 并发操作冲突

**解决方案：**
```javascript
// 使用 waitFor 等待异步操作
await waitFor(() => {
  expect(screen.getByText('加载完成')).toBeInTheDocument();
});

// 清理定时器
beforeEach(() => {
  jest.useFakeTimers();
});

afterEach(() => {
  jest.runOnlyPendingTimers();
  jest.useRealTimers();
});

// 使用 act 包装状态更新
act(() => {
  component.setState({ value: 'new' });
});
```

#### 7.2.2 问题：找不到元素

**原因：**
- 元素尚未渲染
- 查询方式不正确
- 元素在条件分支中

**解决方案：**
```javascript
// 使用异步查询
const element = await screen.findByRole('button');

// 使用 queryBy 检查元素是否存在
const element = screen.queryByRole('button');
if (element) {
  // 元素存在时的逻辑
}

// 使用更精确的查询
const button = screen.getByRole('button', { 
  name: /提交/i,
  exact: false 
});
```

#### 7.2.3 问题：测试运行缓慢

**优化策略：**
```javascript
// 1. 减少不必要的渲染
beforeEach(() => {
  // 只渲染必要的部分
  render(<ComponentUnderTest />);
});

// 2. 使用浅渲染（谨慎使用）
import { shallow } from 'enzyme';
const wrapper = shallow(<Component />);

// 3. 并行运行测试
// jest.config.js
module.exports = {
  maxWorkers: '50%',
};

// 4. 跳过慢速测试
test.skip('慢速测试', () => {
  // 这个测试会被跳过
});
```

#### 7.2.4 问题：测试覆盖率低

**提高