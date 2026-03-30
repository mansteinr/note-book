# React + TypeScript Props 类型定义与 React.FC 深度解析

## 目录

1. [TypeScript 在 React 中的重要性](#typescript-在-react-中的重要性)
2. [Props 类型定义的基本方法](#props-类型定义的基本方法)
3. [接口（Interface）与类型别名（Type Alias）的选择](#接口interface与类型别名type-alias的选择)
4. [React.FC 的用法与优缺点](#reactfc-的用法与优缺点)
5. [函数组件 Props 类型定义的最佳实践](#函数组件-props-类型定义的最佳实践)
6. [类组件 Props 类型定义](#类组件-props-类型定义)
7. [高级 Props 类型技巧](#高级-props-类型技巧)
8. [泛型组件与 Props](#泛型组件与-props)
9. [类型推断与类型守卫](#类型推断与类型守卫)
10. [常见问题与解决方案](#常见问题与解决方案)
11. [性能考虑与优化](#性能考虑与优化)
12. [总结与最佳实践](#总结与最佳实践)

## 一、TypeScript 在 React 中的重要性

### 1.1 类型安全的价值

TypeScript 为 React 开发带来了以下核心价值：

1. **编译时类型检查**：在开发阶段捕获类型错误
2. **更好的 IDE 支持**：智能提示、自动补全、重构支持
3. **代码可维护性**：清晰的类型定义使代码更易理解
4. **团队协作**：统一的类型约定减少沟通成本
5. **文档化**：类型定义本身就是代码文档

### 1.2 React + TypeScript 生态

```typescript
// 典型的 React + TypeScript 项目结构
import React, { useState, useEffect, FC } from 'react';
import { User, Product, Order } from './types';

// 类型安全的组件开发
interface UserCardProps {
  user: User;
  onSelect: (userId: string) => void;
  isActive?: boolean;
}

const UserCard: FC<UserCardProps> = ({ user, onSelect, isActive = false }) => {
  // 类型安全的代码
  return (
    <div className={`user-card ${isActive ? 'active' : ''}`}>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
      <button onClick={() => onSelect(user.id)}>
        选择用户
      </button>
    </div>
  );
};
```

## 二、Props 类型定义的基本方法

### 2.1 使用接口（Interface）

```typescript
// 基础 Props 接口定义
interface ButtonProps {
  // 必需属性
  label: string;
  onClick: () => void;
  
  // 可选属性
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  size?: 'small' | 'medium' | 'large';
  variant?: 'primary' | 'secondary' | 'outline';
  
  // 子元素
  children?: React.ReactNode;
  
  // 样式
  className?: string;
  style?: React.CSSProperties;
  
  // 事件处理
  onMouseEnter?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  onMouseLeave?: (event: React.MouseEvent<HTMLButtonElement>) => void;
}

// 使用接口定义组件
function Button({ 
  label, 
  onClick, 
  disabled = false,
  type = 'button',
  size = 'medium',
  variant = 'primary',
  className = '',
  ...rest 
}: ButtonProps) {
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`btn btn-${size} btn-${variant} ${className}`}
      {...rest}
    >
      {label}
    </button>
  );
}
```

### 2.2 使用类型别名（Type Alias）

```typescript
// 使用类型别名定义 Props
type CardProps = {
  title: string;
  description?: string;
  imageUrl?: string;
  footer?: React.ReactNode;
  onClick?: () => void;
  isHighlighted?: boolean;
};

// 或者使用联合类型
type ButtonSize = 'small' | 'medium' | 'large';
type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'danger';

type AdvancedButtonProps = {
  label: string;
  size: ButtonSize;
  variant: ButtonVariant;
  isLoading?: boolean;
  icon?: React.ReactElement;
  iconPosition?: 'left' | 'right';
};

// 组合类型
type BaseButtonProps = {
  onClick: () => void;
  disabled?: boolean;
};

type IconButtonProps = BaseButtonProps & {
  icon: React.ReactElement;
  label?: string;
  ariaLabel: string;
};
```

### 2.3 内联类型定义

```typescript
// 简单的内联类型定义
function Greeting(props: { name: string; age?: number }) {
  return <div>Hello, {props.name}!</div>;
}

// 带默认值的解构
function UserProfile({
  user,
  showDetails = true,
  onEdit,
}: {
  user: {
    id: string;
    name: string;
    email: string;
    avatar?: string;
  };
  showDetails?: boolean;
  onEdit?: (userId: string) => void;
}) {
  return (
    <div className="user-profile">
      {user.avatar && <img src={user.avatar} alt={user.name} />}
      <h3>{user.name}</h3>
      {showDetails && <p>{user.email}</p>}
      {onEdit && <button onClick={() => onEdit(user.id)}>编辑</button>}
    </div>
  );
}
```

## 三、接口（Interface）与类型别名（Type Alias）的选择

### 3.1 主要区别

| 特性 | 接口（Interface） | 类型别名（Type Alias） |
|------|------------------|----------------------|
| **扩展性** | 使用 `extends` 继承 | 使用 `&` 交叉类型 |
| **实现** | 可以被类实现 | 不能直接被类实现 |
| **声明合并** | 支持（同名接口合并） | 不支持 |
| **可读性** | 更适合对象类型 | 更适合联合、元组等复杂类型 |
| **性能** | 在某些情况下更快 | 可能稍慢 |

### 3.2 使用场景建议

```typescript
// ✅ 适合使用接口的场景
// 1. 定义对象形状（特别是组件 Props）
interface User {
  id: string;
  name: string;
  email: string;
  age?: number;
}

interface UserCardProps {
  user: User;
  onSelect: (userId: string) => void;
  isSelected?: boolean;
}

// 2. 需要声明合并
interface ApiResponse {
  data: any;
  status: number;
}

// 后续可以扩展
interface ApiResponse {
  timestamp: string;
  message?: string;
}

// ✅ 适合使用类型别名的场景
// 1. 联合类型
type Status = 'idle' | 'loading' | 'success' | 'error';
type ButtonType = 'button' | 'submit' | 'reset';

// 2. 元组类型
type Point = [number, number];
type UserTuple = [string, number, string?];

// 3. 复杂类型组合
type ApiResponse<T = any> = {
  data: T;
  status: number;
  message?: string;
  timestamp: string;
};

// 4. 从现有类型派生
type PartialUser = Partial<User>;
type ReadonlyUser = Readonly<User>;
type UserIds = User['id']; // 类型查询
```

### 3.3 实际应用建议

```typescript
// 混合使用：接口定义主要结构，类型别名定义辅助类型
interface Product {
  id: string;
  name: string;
  price: number;
  category: ProductCategory;
  inStock: boolean;
}

// 使用类型别名定义枚举-like 类型
type ProductCategory = 'electronics' | 'clothing' | 'books' | 'food';

// 使用接口扩展
interface DiscountedProduct extends Product {
  discount: number;
  originalPrice: number;
}

// 使用类型别名创建实用类型
type ProductList = Product[];
type ProductMap = Record<string, Product>;
type PartialProduct = Partial<Product>;
type ProductPreview = Pick<Product, 'id' | 'name' | 'price'>;
```

## 四、React.FC 的用法与优缺点

### 4.1 React.FC 的基本用法

```typescript
import React, { FC } from 'react';

// 使用 React.FC 定义函数组件
interface UserProfileProps {
  name: string;
  age: number;
  email?: string;
  onUpdate?: (newName: string) => void;
}

const UserProfile: FC<UserProfileProps> = ({ 
  name, 
  age, 
  email, 
  onUpdate,
  children 
}) => {
  return (
    <div className="user-profile">
      <h2>{name}</h2>
      <p>年龄: {age}</p>
      {email && <p>邮箱: {email}</p>}
      {onUpdate && (
        <button onClick={() => onUpdate(`${name} Updated`)}>
          更新名称
        </button>
      )}
      {children}
    </div>
  );
};

// 使用组件
const App = () => {
  return (
    <div>
      <UserProfile name="张三" age={25} email="zhangsan@example.com">
        <p>这是额外的子内容</p>
      </UserProfile>
    </div>
  );
};
```

### 4.2 React.FC 的隐式特性

```typescript
// React.FC 自动包含的隐式属性
interface FC<P = {}> {
  (props: P & { children?: React.ReactNode }): React.ReactElement | null;
  propTypes?: WeakValidationMap<P>;
  contextTypes?: ValidationMap<any>;
  defaultProps?: Partial<P>;
  displayName?: string;
}

// 这意味着使用 React.FC 时：
// 1. 自动包含 children 属性（即使没有在 Props 中声明）
// 2. 支持 defaultProps
// 3. 支持 propTypes（虽然 TypeScript 项目中不常用）
// 4. 返回类型是 React.ReactElement | null

// 示例：隐式 children
interface CardProps {
  title: string;
}

// 即使 CardProps 没有声明 children，也可以使用
const Card: FC<CardProps> = ({ title, children }) => {
  return (
    <div className="card">
      <h3>{title}</h3>
      <div className="card-content">{children}</div>
    </div>
  );
};
```

### 4.3 React.FC 的优点

#### 4.3.1 隐式 children 支持

```typescript
// 不需要显式声明 children 类型
interface ModalProps {
  title: string;
  isOpen: boolean;
  onClose: () => void;
}

// children 自动可用
const Modal: FC<ModalProps> = ({ title, isOpen, onClose, children }) => {
  if (!isOpen) return null;
  
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{title}</h2>
          <button onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          {children} {/* 不需要在 ModalProps 中声明 */}
        </div>
      </div>
    </div>
  );
};
```

#### 4.3.2 更好的默认 Props 支持

```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  onClick: () => void;
  children: React.ReactNode;
}

// 使用 React.FC 配合 defaultProps
const Button: FC<ButtonProps> = ({ 
  variant, 
  size, 
  disabled, 
  onClick, 
  children 
}) => {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
};

// 定义 defaultProps
Button.defaultProps = {
  variant: 'primary',
  size: 'medium',
  disabled: false,
};

// TypeScript 会正确推断默认值
const Example = () => {
  return <Button onClick={() => console.log('clicked')}>点击我</Button>;
};
```

#### 4.3.3 类型安全更严格

```typescript
// React.FC 强制返回 ReactElement | null
// 防止意外返回其他类型

interface GreetingProps {
  name: string;
}

// ✅ 正确：返回 ReactElement
const Greeting1: FC<GreetingProps> = ({ name }) => {
  return <div>Hello, {name}!</div>;
};

// ✅ 正确：返回 null
const Greeting2: FC<GreetingProps> = ({ name }) => {
  if (!name) return null;
  return <div>Hello, {name}!</div>;
};

// ❌ 错误：不能返回 undefined
const Greeting3: FC<GreetingProps> = ({ name }) => {
  if (!name) return; // 类型错误
  return <div>Hello, {name}!</div>;
};

// ❌ 错误：不能返回字符串
const Greeting4: FC<GreetingProps> = ({ name }) => {
  return `Hello, ${name}!`; // 类型错误
};
```

### 4.4 React.FC 的缺点

#### 4.4.1 隐式 children 问题

```typescript
// 问题：即使组件不应该有 children，TypeScript 也不会报错
interface StandaloneComponentProps {
  title: string;
  value: number;
}

// 这个组件设计上不应该接收 children
const StandaloneComponent: FC<StandaloneComponentProps> = ({ 
  title, 
  value 
}) => {
  return (
    <div>
      <h3>{title}</h3>
      <p>值: {value}</p>
      {/* 这里没有使用 children，但 TypeScript 不会警告 */}
    </div>
  );
};

// 使用时的困惑：可以传递 children，但组件不会渲染
const App = () => {
  return (
    <StandaloneComponent title="测试" value={42}>
      <p>这个内容不会被渲染！</p> {/* 没有类型错误，但逻辑错误 */}
    </StandaloneComponent>
  );
};

// 解决方案：明确声明 children 为 never
interface NoChildrenComponentProps {
  title: string;
  children?: never; // 明确表示不接受 children
}

const NoChildrenComponent: FC<NoChildrenComponentProps> = ({ title }) => {
  return <h3>{title}</h3>;
};

// 现在会有类型错误
const App2 = () => {
  return (
    <NoChildrenComponent title="测试">
      <p>类型错误！</p> {/* TypeScript 会报错 */}
    </NoChildrenComponent>
  );
};
```

#### 4.4.2 泛型支持问题

```typescript
// 问题：React.FC 对泛型的支持不够好
interface GenericProps<T> {
  data: T;
  renderItem: (item: T) => React.ReactNode;
}

// ❌ 错误：不能直接使用
// const GenericComponent: FC<GenericProps<T>> = ... // 语法错误

// 解决方案：使用函数声明
function GenericComponent<T>({ data, renderItem }: GenericProps<T>) {
  return <div>{renderItem(data)}</div>;
}

// 或者使用类型断言（不推荐）
const GenericComponent2 = <T,>({ data, renderItem }: GenericProps<T>) => {
  return <div>{renderItem(data)}</div>;
} as <T>(props: GenericProps<T>) => JSX.Element;
```

#### 4.4.3 defaultProps 与解构默认值的冲突

```typescript
interface ComponentProps {
  count?: number;
  text?: string;
}

// 方式1：使用 React.FC + defaultProps
const Component1: FC<ComponentProps> = ({ count, text }) => {
  return (
    <div>
      <p>Count: {count}</p>
      <p>Text: {text}</p>
    </div>
  );
};

Component1.defaultProps = {
  count: 0,
  text: '默认文本',
};

// 方式2：使用解构默认值
const Component2 = ({ count = 0, text = '默认文本' }: ComponentProps) => {
  return (
    <div>
      <p>Count: {count}</p>
      <p>Text: {text}</p>
    </div>
  );
};

// 问题：当同时使用两者时，解构默认值会覆盖 defaultProps
const Component3: FC<ComponentProps> = ({ 
  count = 100, // 解构默认值
  text = '覆盖文本' 
}) => {
  return (
    <div>
      <p>Count: {count}</p> {/* 总是 100，忽略 defaultProps */}
      <p>Text: {text}</p> {/* 总是 '覆盖文本' */}
    </div>
  );
};

Component3.defaultProps = {
  count: 0, // 被忽略
  text: '默认文本', // 被忽略
};
```

#### 4.4.4 性能考虑

```typescript
// React.FC 添加了额外的类型约束，可能影响类型检查性能
// 对于大型项目，简单的函数声明可能更高效

// 轻量级方式
function SimpleComponent(props: { name: string }) {
  return <div>{props.name}</div>;
}

// 带 React.FC 的方式
const FCComponent: FC<{ name: string }> = ({ name }) => {
  return <div>{name}</div>;
};

// 在大型项目中，差异可能变得明显
// 特别是在热重载和类型检查时
```

### 4.5 社区趋势与建议

根据 React 和 TypeScript 社区的当前趋势：

1. **React 官方文档**：不再推荐使用 `React.FC`
2. **TypeScript 团队**：建议使用简单的函数声明
3. **主流开源项目**：逐渐从 `React.FC` 迁移
4. **原因**：
   - 隐式 children 导致类型不准确
   - 泛型支持问题
   - 与函数组件的发展方向不一致

## 五、函数组件 Props 类型定义的最佳实践

### 5.1 推荐的方式：简单函数声明

```typescript
// 最佳实践：使用简单函数声明
interface UserCardProps {
  user: {
    id: string;
    name: string;
    avatar?: string;
  };
  onSelect: (userId: string) => void;
  isSelected?: boolean;
  // 明确声明 children 类型（如果需要）
  children?: React.ReactNode;
}

function UserCard({ 
  user, 
  onSelect, 
  isSelected = false,
  children 
}: UserCardProps) {
  return (
    <div className={`user-card ${isSelected ? 'selected' : ''}`}>
      {user.avatar && (
        <img src={user.avatar} alt={user.name} className="avatar" />
      )}
      <div className="user-info">
        <h3>{user.name}</h3>
        {children}
      </div>
      <button 
        onClick={() => onSelect(user.id)}
        className="select-btn"
      >
        {isSelected ? '已选择' : '选择'}
      </button>
    </div>
  );
}

// 使用解构默认值而不是 defaultProps
function Button({
  label,
  onClick,
  disabled = false,
  type = 'button',
  variant = 'primary',
  size = 'medium',
  className = '',
}: {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'small' | 'medium' | 'large';
  className?: string;
}) {
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`btn btn-${variant} btn-${size} ${className}`}
    >
      {label}
    </button>
  );
}
```

### 5.2 明确 children 类型

```typescript
// 根据组件需求明确声明 children 类型

// 1. 接受任何 React 节点
interface LayoutProps {
  children: React.ReactNode;
  className?: string;
}

function Layout({ children, className = '' }: LayoutProps) {
  return <div className={`layout ${className}`}>{children}</div>;
}

// 2. 只接受特定类型的子元素
interface ListProps {
  // 只接受 ListItem 组件
  children: React.ReactElement<typeof ListItem> | React.ReactElement<typeof ListItem>[];
}

function List({ children }: ListProps) {
  return <ul className="list">{children}</ul>;
}

// 3. 不接受 children
interface IconProps {
  name: string;
  size?: number;
  color?: string;
  // 明确表示不接受 children
  children?: never;
}

function Icon({ name, size = 24, color = 'currentColor' }: IconProps) {
  return (
    <svg width={size} height={size} fill={color}>
      {/* SVG 内容 */}
    </svg>
  );
}

// 4. 接受函数作为 children（render props）
interface DataProviderProps<T> {
  data: T[];
  children: (item: T, index: number) => React.ReactNode;
}

function DataProvider<T>({ data, children }: DataProviderProps<T>) {
  return (
    <div>
      {data.map((item, index) => (
        <div key={index}>{children(item, index)}</div>
      ))}
    </div>
  );
}
```

### 5.3 使用实用类型

```typescript
// 利用 TypeScript 内置实用类型
interface User {
  id: string;
  name: string;
  email: string;
  age: number;
  address?: string;
  phone?: string;
}

// 1. Partial：所有属性变为可选
type PartialUser = Partial<User>;
// 等价于 { id?: string; name?: string; ... }

// 2. Required：所有属性变为必需
type RequiredUser = Required<User>;
// 等价于 { id: string; name: string; ... address: string; phone: string }

// 3. Readonly：所有属性变为只读
type ReadonlyUser = Readonly<User>;

// 4. Pick：选择部分属性
type UserPreview = Pick<User, 'id' | 'name' | 'email'>;

// 5. Omit：排除部分属性
type UserWithoutId = Omit<User, 'id'>;

// 6. Record：创建键值对类型
type UserMap = Record<string, User>;

// 在组件 Props 中的应用
interface BaseProps {
  className?: string;
  style?: React.CSSProperties;
  'data-testid'?: string;
}

// 扩展基础 Props
interface CardProps extends BaseProps {
  title: string;
  content: string;
  onClick?: () => void;
}

// 使用 Partial 创建可选版本
type OptionalCardProps = Partial<CardProps>;

// 使用 Pick 创建简化版本
type SimpleCardProps = Pick<CardProps, 'title' | 'content'>;

// 使用 Omit 创建变体
type CardWithoutClickProps = Omit<CardProps, 'onClick'>;
```

### 5.4 组件 Props 的组织结构

```typescript
// 1. 基础类型定义
type ButtonSize = 'small' | 'medium' | 'large';
type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'danger';
type ButtonType = 'button' | 'submit' | 'reset';

// 2. 基础 Props 接口
interface BaseButtonProps {
  onClick?: () => void;
  disabled?: boolean;
  type?: ButtonType;
  className?: string;
  'aria-label'?: string;
}

// 3. 特定组件的 Props
interface ButtonProps extends BaseButtonProps {
  children: React.ReactNode;
  size?: ButtonSize;
  variant?: ButtonVariant;
  loading?: boolean;
  icon?: React.ReactElement;
  iconPosition?: 'left' | 'right';
}

// 4. 变体组件的 Props
interface IconButtonProps extends BaseButtonProps {
  icon: React.ReactElement;
  'aria-label': string; // 覆盖为必需
  children?: never; // 不允许 children
}

// 5. 使用类型守卫进行 Props 验证
function isIconButtonProps(props: any): props is IconButtonProps {
  return 'icon' in props && 'aria-label' in props;
}

// 6. 组件实现
function Button(props: ButtonProps | IconButtonProps) {
  if (isIconButtonProps(props)) {
    // IconButton 逻辑
    return (
      <button
        type={props.type}
        disabled={props.disabled}
        onClick={props.onClick}
        className={`icon-button ${props.className || ''}`}
        aria-label={props['aria-label']}
      >
        {props.icon}
      </button>
    );
  }
  
  // 普通 Button 逻辑
  return (
    <button
      type={props.type}
      disabled={props.disabled || props.loading}
      onClick={props.onClick}
      className={`btn btn-${props.size} btn-${props.variant} ${props.className || ''}`}
    >
      {props.loading ? (
        <span className="loading">加载中...</span>
      ) : (
        <>
          {props.icon && props.iconPosition === 'left' && props.icon}
          {props.children}
          {props.icon && props.iconPosition === 'right' && props.icon}
        </>
      )}
    </button>
  );
}
```

## 六、类组件 Props 类型定义

### 6.1 类组件的基本 Props 定义

```typescript
import React, { Component } from 'react';

// 定义 Props 接口
interface CounterProps {
  initialCount?: number;
  step?: number;
  onCountChange?: (count: number) => void;
}

// 定义 State 接口
interface CounterState {
  count: number;
  isActive: boolean;
}

// 类组件使用泛型：Component<Props, State>
class Counter extends Component<CounterProps, CounterState> {
  // 默认 Props
  static defaultProps: Partial<CounterProps> = {
    initialCount: 0,
    step: 1,
  };

  constructor(props: CounterProps) {
    super(props);
    
    // 初始化 State
    this.state = {
      count: props.initialCount || 0,
      isActive: false,
    };
  }

  // 类型安全的方法
  increment = () => {
    const { step = 1, onCountChange } = this.props;
    this.setState(
      prevState => ({ count: prevState.count + step }),
      () => {
        // 回调函数中访问最新的 state
        if (onCountChange) {
          onCountChange(this.state.count);
        }
      }
    );
  };

  decrement = () => {
    const { step = 1, onCountChange } = this.props;
    this.setState(
      prevState => ({ count: prevState.count - step }),
      () => {
        if (onCountChange) {
          onCountChange(this.state.count);
        }
      }
    );
  };

  toggleActive = () => {
    this.setState(prevState => ({ isActive: !prevState.isActive }));
  };

  render() {
    const { count, isActive } = this.state;
    
    return (
      <div className={`counter ${isActive ? 'active' : ''}`}>
        <h3>计数器: {count}</h3>
        <div className="controls">
          <button onClick={this.decrement}>-</button>
          <button onClick={this.increment}>+</button>
          <button onClick={this.toggleActive}>
            {isActive ? '停用' : '激活'}
          </button>
        </div>
      </div>
    );
  }
}
```

### 6.2 类组件的生命周期与类型安全

```typescript
interface UserProfileProps {
  userId: string;
  onUserLoaded?: (user: User) => void;
  onError?: (error: Error) => void;
}

interface UserProfileState {
  user: User | null;
  loading: boolean;
  error: string | null;
}

class UserProfile extends Component<UserProfileProps, UserProfileState> {
  private abortController: AbortController | null = null;

  constructor(props: UserProfileProps) {
    super(props);
    this.state = {
      user: null,
      loading: true,
      error: null,
    };
  }

  // 组件挂载时
  componentDidMount() {
    this.fetchUser();
  }

  // Props 更新时
  componentDidUpdate(prevProps: UserProfileProps) {
    if (prevProps.userId !== this.props.userId) {
      this.fetchUser();
    }
  }

  // 组件卸载时
  componentWillUnmount() {
    // 取消未完成的请求
    if (this.abortController) {
      this.abortController.abort();
    }
  }

  // 类型安全的异步方法
  private async fetchUser() {
    const { userId, onUserLoaded, onError } = this.props;
    
    // 取消之前的请求
    if (this.abortController) {
      this.abortController.abort();
    }

    this.abortController = new AbortController();
    
    this.setState({ loading: true, error: null });

    try {
      const response = await fetch(`/api/users/${userId}`, {
        signal: this.abortController.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const user: User = await response.json();
      
      this.setState({ user, loading: false });
      
      if (onUserLoaded) {
        onUserLoaded(user);
      }
    } catch (error) {
      // 类型安全的错误处理
      if (error instanceof Error) {
        // 忽略取消请求的错误
        if (error.name !== 'AbortError') {
          this.setState({ 
            error: error.message, 
            loading: false 
          });
          
          if (onError) {
            onError(error);
          }
        }
      } else {
        this.setState({ 
          error: '未知错误', 
          loading: false 
        });
      }
    }
  }

  render() {
    const { user, loading, error } = this.state;

    if (loading) {
      return <div className="loading">加载中...</div>;
    }

    if (error) {
      return <div className="error">错误: {error}</div>;
    }

    if (!user) {
      return <div className="no-data">未找到用户</div>;
    }

    return (
      <div className="user-profile">
        <h2>{user.name}</h2>
        <p>邮箱: {user.email}</p>
        <p>年龄: {user.age}</p>
        {/* 更多用户信息 */}
      </div>
    );
  }
}
```

### 6.3 类组件的 Ref 转发

```typescript
import React, { Component, createRef } from 'react';

// 定义 Props
interface FocusableInputProps {
  label: string;
  defaultValue?: string;
  onFocus?: () => void;
  onBlur?: () => void;
  onChange?: (value: string) => void;
}

// 定义 Ref 类型
interface FocusableInputHandle {
  focus: () => void;
  blur: () => void;
  getValue: () => string;
  setValue: (value: string) => void;
}

// 使用 forwardRef
const FocusableInput = React.forwardRef<
  FocusableInputHandle, 
  FocusableInputProps
>((props, ref) => {
  const inputRef = createRef<HTMLInputElement>();

  // 暴露方法给父组件
  React.useImperativeHandle(ref, () => ({
    focus: () => {
      inputRef.current?.focus();
      props.onFocus?.();
    },
    blur: () => {
      inputRef.current?.blur();
      props.onBlur?.();
    },
    getValue: () => inputRef.current?.value || '',
    setValue: (value: string) => {
      if (inputRef.current) {
        inputRef.current.value = value;
        props.onChange?.(value);
      }
    },
  }));

  return (
    <div className="input-group">
      <label>{props.label}</label>
      <input
        ref={inputRef}
        defaultValue={props.defaultValue}
        onChange={(e) => props.onChange?.(e.target.value)}
      />
    </div>
  );
});

// 使用示例
class Form extends Component {
  private inputRef = createRef<FocusableInputHandle>();

  handleSubmit = () => {
    if (this.inputRef.current) {
      const value = this.inputRef.current.getValue();
      console.log('输入值:', value);
      
      // 清空输入
      this.inputRef.current.setValue('');
      
      // 重新聚焦
      this.inputRef.current.focus();
    }
  };

  render() {
    return (
      <div className="form">
        <FocusableInput
          ref={this.inputRef}
          label="用户名"
          defaultValue=""
          onChange={(value) => console.log('值变化:', value)}
        />
        <button onClick={this.handleSubmit}>提交</button>
      </div>
    );
  }
}
```

## 七、高级 Props 类型技巧

### 7.1 条件类型与映射类型

```typescript
// 1. 条件类型
type IsString<T> = T extends string ? true : false;

type Test1 = IsString<string>; // true
type Test2 = IsString<number>; // false

// 在 Props 中的应用
type ValueType<T> = T extends string
  ? { value: string; onChange: (value: string) => void }
  : T extends number
  ? { value: number; onChange: (value: number) => void }
  : { value: T; onChange: (value: T) => void };

// 2. 映射类型
type ReadonlyProps<T> = {
  readonly [P in keyof T]: T[P];
};

type OptionalProps<T> = {
  [P in keyof T]?: T[P];
};

type RequiredProps<T> = {
  [P in keyof T]-?: T[P];
};

// 3. 键重映射
type Getters<T> = {
  [P in keyof T as `get${Capitalize<string & P>}`]: () => T[P];
};

interface User {
  name: string;
  age: number;
}

type UserGetters = Getters<User>;
// 等价于 { getName: () => string; getAge: () => number }

// 4. 模板字面量类型
type EventName = `on${Capitalize<'click' | 'change' | 'submit'>}`;
// 等价于 'onClick' | 'onChange' | 'onSubmit'

type ComponentEvents = {
  [K in EventName]?: (event: React.SyntheticEvent) => void;
};

// 5. 复杂示例：表单字段 Props
type FieldType = 'text' | 'number' | 'email' | 'password' | 'date';

type BaseFieldProps = {
  name: string;
  label: string;
  required?: boolean;
  disabled?: boolean;
  placeholder?: string;
};

// 根据类型生成不同的 Props
type FieldProps<T extends FieldType> = BaseFieldProps & 
  (T extends 'number' 
    ? { 
        type: T;
        min?: number;
        max?: number;
        step?: number;
        value?: number;
        onChange?: (value: number) => void;
      }
    : T extends 'date'
    ? {
        type: T;
        minDate?: string;
        maxDate?: string;
        value?: string;
        onChange?: (value: string) => void;
      }
    : {
        type: T;
        value?: string;
        onChange?: (value: string) => void;
      });

// 使用示例
function FormField<T extends FieldType>(props: FieldProps<T>) {
  // 组件实现
  return (
    <div className="form-field">
      <label>{props.label}</label>
      <input
        type={props.type}
        name={props.name}
        required={props.required}
        disabled={props.disabled}
        placeholder={props.placeholder}
        // 其他属性...
      />
    </div>
  );
}

// 类型安全的调用
<FormField<"number">
  type="number"
  name="age"
  label="年龄"
  min={0}
  max={150}
  value={25}
  onChange={(value) => console.log(value)}
/>
```

### 7.2 类型守卫与类型断言

```typescript
// 1. 类型守卫函数
interface User {
  id: string;
  name: string;
  email: string;
}

interface Admin {
  id: string;
  name: string;
  permissions: string[];
}

type Person = User | Admin;

// 类型守卫
function isAdmin(person: Person): person is Admin {
  return 'permissions' in person;
}

function isUser(person: Person): person is User {
  return !isAdmin(person);
}

// 2. 在组件中使用
interface PersonCardProps {
  person: Person;
  onEdit?: (person: Person) => void;
}

function PersonCard({ person, onEdit }: PersonCardProps) {
  // 使用类型守卫
  if (isAdmin(person)) {
    return (
      <div className="admin-card">
        <h3>{person.name} (管理员)</h3>
        <p>权限: {person.permissions.join(', ')}</p>
        {onEdit && <button onClick={() => onEdit(person)}>编辑</button>}
      </div>
    );
  }

  // TypeScript 知道这里 person 是 User
  return (
    <div className="user-card">
      <h3>{person.name}</h3>
      <p>邮箱: {person.email}</p>
      {onEdit && <button onClick={() => onEdit(person)}>编辑</button>}
    </div>
  );
}

// 3. 类型断言（谨慎使用）
interface ApiResponse {
  data: unknown;
  status: number;
}

function processResponse(response: ApiResponse) {
  // 类型断言：明确告诉 TypeScript 数据的类型
  const data = response.data as {
    users: User[];
    total: number;
    page: number;
  };
  
  // 或者使用类型断言函数
  function assertIsUserArray(data: unknown): asserts data is User[] {
    if (!Array.isArray(data)) {
      throw new Error('数据不是数组');
    }
    if (data.length > 0 && !('id' in data[0])) {
      throw new Error('数组元素不是 User 类型');
    }
  }
  
  // 使用断言函数
  assertIsUserArray(response.data);
  // 现在 TypeScript 知道 response.data 是 User[]
  
  return response.data.map(user => user.name);
}

// 4. 非空断言（谨慎使用）
interface ComponentProps {
  data?: {
    items: string[];
    total: number;
  };
  onLoad?: () => void;
}

function Component({ data, onLoad }: ComponentProps) {
  // ❌ 不安全的访问
  // const items = data.items; // 可能为 undefined
  
  // ✅ 安全的访问
  const items = data?.items || [];
  
  // ✅ 使用非空断言（确保 data 不为空）
  const safeItems = data!.items; // 告诉 TypeScript data 一定存在
  
  // 调用可选函数
  onLoad?.(); // 安全调用
  
  return (
    <div>
      <p>项目数: {items.length}</p>
    </div>
  );
}
```

### 7.3 递归类型与复杂结构

```typescript
// 1. 递归类型：树形结构
interface TreeNode<T = any> {
  id: string;
  label: string;
  data: T;
  children?: TreeNode<T>[];
}

// 2. 递归类型：嵌套对象
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

// 3. 递归组件 Props
interface TreeViewProps<T> {
  nodes: TreeNode<T>[];
  onNodeSelect?: (node: TreeNode<T>) => void;
  onNodeExpand?: (node: TreeNode<T>) => void;
  renderNode?: (node: TreeNode<T>) => React.ReactNode;
  depth?: number;
}

function TreeView<T>({
  nodes,
  onNodeSelect,
  onNodeExpand,
  renderNode,
  depth = 0,
}: TreeViewProps<T>) {
  return (
    <div className="tree-view" style={{ marginLeft: depth * 20 }}>
      {nodes.map(node => (
        <div key={node.id} className="tree-node">
          <div
            className="node-content"
            onClick={() => onNodeSelect?.(node)}
          >
            {renderNode ? renderNode(node) : node.label}
            {node.children && (
              <button onClick={() => onNodeExpand?.(node)}>
                {node.children.length > 0 ? '展开' : '无子节点'}
              </button>
            )}
          </div>
          {node.children && node.children.length > 0 && (
            <TreeView
              nodes={node.children}
              onNodeSelect={onNodeSelect}
              onNodeExpand={onNodeExpand}
              renderNode={renderNode}
              depth={depth + 1}
            />
          )}
        </div>
      ))}
    </div>
  );
}

// 4. 复杂表单 Props
type ValidationRule<T> = {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  validate?: (value: T) => string | null;
};

type FormFieldConfig<T> = {
  [K in keyof T]: {
    label: string;
    type: 'text' | 'number' | 'email' | 'select' | 'checkbox';
    options?: { label: string; value: any }[];
    validation?: ValidationRule<T[K]>;
  };
};

interface UserFormData {
  name: string;
  email: string;
  age: number;
  subscribe: boolean;
}

const userFormConfig: FormFieldConfig<UserFormData> = {
  name: {
    label: '姓名',
    type: 'text',
    validation: {
      required: true,
      minLength: 2,
      maxLength: 50,
    },
  },
  email: {
    label: '邮箱',
    type: 'email',
    validation: {
      required: true,
      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    },
  },
  age: {
    label: '年龄',
    type: 'number',
    validation: {
      required: true,
      validate: (value) => value >= 0 ? null : '年龄不能为负数',
    },
  },
  subscribe: {
    label: '订阅通知',
    type: 'checkbox',
  },
};

// 动态表单组件
interface DynamicFormProps<T> {
  config: FormFieldConfig<T>;
  initialData?: Partial<T>;
  onSubmit: (data: T) => void;
  onCancel?: () => void;
}

function DynamicForm<T extends Record<string, any>>({
  config,
  initialData = {},
  onSubmit,
  onCancel,
}: DynamicFormProps<T>) {
  const [formData, setFormData] = useState<Partial<T>>(initialData);
  const [errors, setErrors] = useState<Record<keyof T, string>>({} as any);
  
  // 表单逻辑...
  
  return (
    <form onSubmit={handleSubmit}>
      {Object.entries(config).map(([fieldName, fieldConfig]) => (
        <div key={fieldName} className="form-field">
          <label>{fieldConfig.label}</label>
          {/* 根据类型渲染不同的输入组件 */}
          {renderField(fieldName as keyof T, fieldConfig)}
          {errors[fieldName as keyof T] && (
            <div className="error">{errors[fieldName as keyof T]}</div>
          )}
        </div>
      ))}
      <div className="form-actions">
        <button type="submit">提交</button>
        {onCancel && <button type="button" onClick={onCancel}>取消</button>}
      </div>
    </form>
  );
}
```

## 八、泛型组件与 Props

### 8.1 基础泛型组件

```typescript
// 1. 简单的泛型列表组件
interface ListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  emptyMessage?: string;
  className?: string;
}

function List<T>({
  items,
  renderItem,
  emptyMessage = '暂无数据',
  className = '',
}: ListProps<T>) {
  if (items.length === 0) {
    return <div className={`empty-list ${className}`}>{emptyMessage}</div>;
  }

  return (
    <div className={`list ${className}`}>
      {items.map((item, index) => (
        <div key={index} className="list-item">
          {renderItem(item, index)}
        </div>
      ))}
    </div>
  );
}

// 使用示例
const users: User[] = [
  { id: '1', name: '张三', email: 'zhangsan@example.com' },
  { id: '2', name: '李四', email: 'lisi@example.com' },
];

const products: Product[] = [
  { id: '1', name: '商品A', price: 100 },
  { id: '2', name: '商品B', price: 200 },
];

// 类型安全的使用
<List
  items={users}
  renderItem={(user) => (
    <div>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  )}
/>

<List
  items={products}
  renderItem={(product) => (
    <div>
      <h3>{product.name}</h3>
      <p>价格: ¥{product.price}</p>
    </div>
  )}
/>
```

### 8.2 带约束的泛型组件

```typescript
// 1. 泛型约束：确保类型有特定属性
interface Identifiable {
  id: string | number;
}

interface TableProps<T extends Identifiable> {
  data: T[];
  columns: Array<{
    key: keyof T;
    title: string;
    render?: (value: T[keyof T], row: T) => React.ReactNode;
  }>;
  onRowClick?: (row: T) => void;
  selectedId?: string | number;
}

function Table<T extends Identifiable>({
  data,
  columns,
  onRowClick,
  selectedId,
}: TableProps<T>) {
  return (
    <table className="data-table">
      <thead>
        <tr>
          {columns.map(column => (
            <th key={String(column.key)}>{column.title}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map(row => (
          <tr
            key={row.id}
            onClick={() => onRowClick?.(row)}
            className={row.id === selectedId ? 'selected' : ''}
          >
            {columns.map(column => (
              <td key={String(column.key)}>
                {column.render
                  ? column.render(row[column.key], row)
                  : String(row[column.key])}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// 2. 多个泛型参数
interface Pair<A, B> {
  first: A;
  second: B;
}

interface PairListProps<A, B> {
  pairs: Pair<A, B>[];
  renderFirst: (item: A) => React.ReactNode;
  renderSecond: (item: B) => React.ReactNode;
  separator?: React.ReactNode;
}

function PairList<A, B>({
  pairs,
  renderFirst,
  renderSecond,
  separator = ' : ',
}: PairListProps<A, B>) {
  return (
    <div className="pair-list">
      {pairs.map((pair, index) => (
        <div key={index} className="pair-item">
          <div className="first">{renderFirst(pair.first)}</div>
          <div className="separator">{separator}</div>
          <div className="second">{renderSecond(pair.second)}</div>
        </div>
      ))}
    </div>
  );
}

// 3. 泛型默认值
interface PaginatedListProps<T = any> {
  items: T[];
  pageSize?: number;
  renderItem: (item: T) => React.ReactNode;
  emptyMessage?: string;
}

function PaginatedList<T = any>({
  items,
  pageSize = 10,
  renderItem,
  emptyMessage = '暂无数据',
}: PaginatedListProps<T>) {
  const [currentPage, setCurrentPage] = useState(1);
  
  const totalPages = Math.ceil(items.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const currentItems = items.slice(startIndex, startIndex + pageSize);
  
  if (items.length === 0) {
    return <div className="empty">{emptyMessage}</div>;
  }
  
  return (
    <div className="paginated-list">
      <div className="items">
        {currentItems.map((item, index) => (
          <div key={index} className="item">
            {renderItem(item)}
          </div>
        ))}
      </div>
      <div className="pagination">
        <button
          disabled={currentPage <= 1}
          onClick={() => setCurrentPage(prev => prev - 1)}
        >
          上一页
        </button>
        <span>
          第 {currentPage} 页 / 共 {totalPages} 页
        </span>
        <button
          disabled={currentPage >= totalPages}
          onClick={() => setCurrentPage(prev => prev + 1)}
        >
          下一页
        </button>
      </div>
    </div>
  );
}
```

### 8.3 高阶组件中的泛型

```typescript
// 1. 高阶组件类型定义
type HOC<InjectedProps, OwnProps = {}> = <P extends InjectedProps>(
  Component: React.ComponentType<P>
) => React.ComponentType<Omit<P, keyof InjectedProps> & OwnProps>;

// 2. 带加载状态的高阶组件
interface WithLoadingProps {
  loading: boolean;
  error?: string | null;
}

const withLoading = <P extends object>(
  WrappedComponent: React.ComponentType<P & WithLoadingProps>
): React.ComponentType<Omit<P, keyof WithLoadingProps> & { isLoading: boolean; error?: string }> => {
  return function WithLoadingComponent({ isLoading, error, ...props }) {
    if (isLoading) {
      return <div className="loading">加载中...</div>;
    }
    
    if (error) {
      return <div className="error">错误: {error}</div>;
    }
    
    return <WrappedComponent {...(props as P)} loading={false} />;
  };
};

// 3. 使用示例
interface UserListProps {
  users: User[];
  onSelect: (user: User) => void;
}

const UserList: React.FC<UserListProps & WithLoadingProps> = ({ 
  users, 
  onSelect, 
  loading 
}) => {
  if (loading) {
    return <div>加载用户列表...</div>;
  }
  
  return (
    <div className="user-list">
      {users.map(user => (
        <div key={user.id} onClick={() => onSelect(user)}>
          {user.name}
        </div>
      ))}
    </div>
  );
};

// 应用高阶组件
const UserListWithLoading = withLoading(UserList);

// 4. 更复杂的高阶组件：带数据获取
interface WithDataProps<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

function withData<T, P extends WithDataProps<T>>(
  fetchData: () => Promise<T>,
  options?: { 
    initialData?: T | null;
    onError?: (error: Error) => void;
  }
) {
  return function <C extends React.ComponentType<P>>(
    WrappedComponent: C
  ): React.ComponentType<Omit<P, keyof WithDataProps<T>>> {
    return function WithDataComponent(props: Omit<P, keyof WithDataProps<T>>) {
      const [state, setState] = useState<{
        data: T | null;
        loading: boolean;
        error: string | null;
      }>({
        data: options?.initialData || null,
        loading: false,
        error: null,
      });
      
      const fetchDataWrapper = useCallback(async () => {
        setState(prev => ({ ...prev, loading: true, error: null }));
        
        try {
          const data = await fetchData();
          setState({ data, loading: false, error: null });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : '未知错误';
          setState({ data: null, loading: false, error: errorMessage });
          
          if (options?.onError && error instanceof Error) {
            options.onError(error);
          }
        }
      }, [fetchData]);
      
      useEffect(() => {
        fetchDataWrapper();
      }, [fetchDataWrapper]);
      
      return (
        <WrappedComponent
          {...(props as P)}
          data={state.data}
          loading={state.loading}
          error={state.error}
          refetch={fetchDataWrapper}
        />
      );
    };
  };
}

// 使用示例
interface UserProfileProps extends WithDataProps<User> {
  userId: string;
}

const UserProfileComponent: React.FC<UserProfileProps> = ({ 
  data, 
  loading, 
  error, 
  refetch,
  userId 
}) => {
  // 组件实现...
  return (
    <div>
      {loading && <div>加载中...</div>}
      {error && <div>错误: {error}</div>}
      {data && (
        <div>
          <h2>{data.name}</h2>
          <p>{data.email}</p>
        </div>
      )}
      <button onClick={refetch}>刷新</button>
    </div>
  );
};

// 创建带数据获取的组件
const UserProfileWithData = withData<User, UserProfileProps>(
  () => fetch(`/api/users/123`).then(res => res.json())
)(UserProfileComponent);
```

## 九、类型推断与类型守卫

### 9.1 类型推断的最佳实践

```typescript
// 1. 利用 TypeScript 的类型推断
// 不需要显式声明所有类型

// ✅ 好的实践：让 TypeScript 推断类型
const users = [
  { id: '1', name: '张三', age: 25 },
  { id: '2', name: '李四', age: 30 },
]; // TypeScript 推断为 { id: string; name: string; age: number }[]

// ✅ 好的实践：函数返回类型推断
function createUser(name: string, age: number) {
  return {
    id: Math.random().toString(36).substr(2, 9),
    name,
    age,
    createdAt: new Date(),
  };
  // TypeScript 推断返回类型
}

// ✅ 好的实践：组件 Props 推断
function Greeting({ name, age = 18 }: { name: string; age?: number }) {
  return <div>Hello, {name}! You are {age} years old.</div>;
}

// 2. 需要显式类型的场景
// ✅ 好的实践：复杂对象字面量
const config: AppConfig = {
  apiUrl: 'https://api.example.com',
  timeout: 5000,
  retries: 3,
  // TypeScript 会检查是否满足 AppConfig 类型
};

// ✅ 好的实践：函数参数类型
function processData<T>(data: T, transform: (item: T) => any) {
  // 显式声明泛型参数
  return transform(data);
}

// 3. 组件中的类型推断
interface Product {
  id: string;
  name: string;
  price: number;
  category: string;
}

function ProductList({ products }: { products: Product[] }) {
  // TypeScript 知道 products 是 Product[]
  // 知道每个 product 有 id, name, price, category
  
  return (
    <div>
      {products.map(product => (
        <div key={product.id}>
          <h3>{product.name}</h3>
          <p>价格: ${product.price}</p>
          <p>分类: {product.category}</p>
        </div>
      ))}
    </div>
  );
}

// 4. 使用 as const 进行精确类型推断
const BUTTON_SIZES = ['small', 'medium', 'large'] as const;
type ButtonSize = typeof BUTTON_SIZES[number]; // 'small' | 'medium' | 'large'

const COLORS = {
  primary: '#007acc',
  secondary: '#6c757d',
  success: '#28a745',
  danger: '#dc3545',
} as const;
type ColorKey = keyof typeof COLORS; // 'primary' | 'secondary' | 'success' | 'danger'
type ColorValue = typeof COLORS[ColorKey]; // '#007acc' | '#6c757d' | '#28a745' | '#dc3545'
```

### 9.2 高级类型守卫技巧

```typescript
// 1. 自定义类型守卫
interface ApiSuccessResponse<T> {
  success: true;
  data: T;
  timestamp: string;
}

interface ApiErrorResponse {
  success: false;
  error: string;
  code: number;
  timestamp: string;
}

type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse;

// 类型守卫函数
function isSuccessResponse<T>(
  response: ApiResponse<T>
): response is ApiSuccessResponse<T> {
  return response.success === true;
}

function isErrorResponse<T>(
  response: ApiResponse<T>
): response is ApiErrorResponse {
  return response.success === false;
}

// 在组件中使用
function ApiResult<T>({ response }: { response: ApiResponse<T> }) {
  if (isSuccessResponse(response)) {
    // TypeScript 知道 response 是 ApiSuccessResponse<T>
    return (
      <div className="success">
        <p>数据获取成功: {response.timestamp}</p>
        {/* 可以安全访问 response.data */}
        <pre>{JSON.stringify(response.data, null, 2)}</pre>
      </div>
    );
  }
  
  // TypeScript 知道 response 是 ApiErrorResponse
  return (
    <div className="error">
      <p>错误 ({response.code}): {response.error}</p>
      <p>时间: {response.timestamp}</p>
    </div>
  );
}

// 2. 联合类型的类型守卫
type FormField = 
  | { type: 'text'; value: string; maxLength?: number }
  | { type: 'number'; value: number; min?: number; max?: number }
  | { type: 'checkbox'; value: boolean; label: string }
  | { type: 'select'; value: string; options: string[] };

// 类型守卫函数
function isTextField(field: FormField): field is Extract<FormField, { type: 'text' }> {
  return field.type === 'text';
}

function isNumberField(field: FormField): field is Extract<FormField, { type: 'number' }> {
  return field.type === 'number';
}

// 渲染组件
function FormFieldRenderer({ field }: { field: FormField }) {
  if (isTextField(field)) {
    return (
      <input
        type="text"
        value={field.value}
        maxLength={field.maxLength}
        onChange={(e) => console.log(e.target.value)}
      />
    );
  }
  
  if (isNumberField(field)) {
    return (
      <input
        type="number"
        value={field.value}
        min={field.min}
        max={field.max}
        onChange={(e) => console.log(Number(e.target.value))}
      />
    );
  }
  
  if (field.type === 'checkbox') {
    return (
      <label>
        <input
          type="checkbox"
          checked={field.value}
          onChange={(e) => console.log(e.target.checked)}
        />
        {field.label}
      </label>
    );
  }
  
  // field.type === 'select'
  return (
    <select value={field.value} onChange={(e) => console.log(e.target.value)}>
      {field.options.map(option => (
        <option key={option} value={option}>{option}</option>
      ))}
    </select>
  );
}

// 3. 使用 in 操作符进行类型守卫
interface Cat {
  type: 'cat';
  meow: () => void;
  purr: () => void;
}

interface Dog {
  type: 'dog';
  bark: () => void;
  wagTail: () => void;
}

type Animal = Cat | Dog;

function handleAnimal(animal: Animal) {
  // 使用 in 操作符
  if ('meow' in animal) {
    // TypeScript 知道 animal 是 Cat
    animal.meow();
    animal.purr();
  } else {
    // TypeScript 知道 animal 是 Dog
    animal.bark();
    animal.wagTail();
  }
}

// 4. 使用类型谓词进行复杂验证
function isValidUser(obj: any): obj is User {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    typeof obj.id === 'string' &&
    typeof obj.name === 'string' &&
    typeof obj.email === 'string' &&
    (typeof obj.age === 'undefined' || typeof obj.age === 'number')
  );
}

// 在数据验证中使用
function UserForm({ initialData }: { initialData?: any }) {
  const [user, setUser] = useState<User | null>(
    isValidUser(initialData) ? initialData : null
  );
  
  // ... 表单逻辑
}
```

## 十、常见问题与解决方案

### 10.1 Props 类型扩展问题

```typescript
// 问题：如何正确扩展 HTML 元素属性？

// 1. 扩展按钮属性
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
}

function Button({ 
  variant = 'primary', 
  size = 'medium', 
  loading = false,
  className = '',
  disabled,
  children,
  ...rest 
}: ButtonProps) {
  return (
    <button
      {...rest} // 包含所有原生按钮属性
      disabled={disabled || loading}
      className={`btn btn-${variant} btn-${size} ${loading ? 'loading' : ''} ${className}`}
    >
      {loading ? '加载中...' : children}
    </button>
  );
}

// 2. 扩展输入框属性
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

function Input({ 
  label, 
  error, 
  helperText, 
  className = '',
  ...rest 
}: InputProps) {
  return (
    <div className="input-wrapper">
      {label && <label className="input-label">{label}</label>}
      <input
        {...rest}
        className={`input ${error ? 'error' : ''} ${className}`}
        aria-invalid={!!error}
      />
      {error && <div className="input-error">{error}</div>}
      {helperText && !error && <div className="input-helper">{helperText}</div>}
    </div>
  );
}

// 3. 扩展自定义组件属性
interface BaseProps {
  className?: string;
  style?: React.CSSProperties;
  'data-testid'?: string;
}

interface CardProps extends BaseProps {
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  onClick?: () => void;
}

// 4. 处理 ref 属性
interface InputWithRefProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

const InputWithRef = React.forwardRef<HTMLInputElement, InputWithRefProps>(
  ({ label, error, className = '', ...rest }, ref) => {
    return (
      <div className="input-with-ref">
        <label>{label}</label>
        <input
          ref={ref}
          className={`input ${error ? 'error' : ''} ${className}`}
          {...rest}
        />
        {error && <span className="error-message">{error}</span>}
      </div>
    );
  }
);

// 使用示例
function Form() {
  const inputRef = useRef<HTMLInputElement>(null);
  
  const focusInput = () => {
    inputRef.current?.focus();
  };
  
  return (
    <div>
      <InputWithRef
        ref={inputRef}
        label="用户名"
        placeholder="请输入用户名"
        error={/* 错误信息 */}
      />
      <button onClick={focusInput}>聚焦输入框</button>
    </div>
  );
}
```

### 10.2 可选 Props 与默认值

```typescript
// 问题：如何处理可选 Props 和默认值？

// 1. 使用解构默认值（推荐）
interface UserCardProps {
  user: User;
  showEmail?: boolean;
  showAvatar?: boolean;
  size?: 'small' | 'medium' | 'large';
  onEdit?: (userId: string) => void;
}

function UserCard({
  user,
  showEmail = true, // 解构默认值
  showAvatar = true,
  size = 'medium',
  onEdit,
}: UserCardProps) {
  return (
    <div className={`user-card size-${size}`}>
      {showAvatar && user.avatar && (
        <img src={user.avatar} alt={user.name} className="avatar" />
      )}
      <div className="user-info">
        <h3>{user.name}</h3>
        {showEmail && <p className="email">{user.email}</p>}
      </div>
      {onEdit && (
        <button onClick={() => onEdit(user.id)} className="edit-btn">
          编辑
        </button>
      )}
    </div>
  );
}

// 2. 使用 defaultProps（类组件或 React.FC）
interface AlertProps {
  type: 'success' | 'warning' | 'error' | 'info';
  message: string;
  dismissible?: boolean;
  onDismiss?: () => void;
}

// 使用 React.FC 时
const Alert: React.FC<AlertProps> = ({ 
  type, 
  message, 
  dismissible, 
  onDismiss 
}) => {
  return (
    <div className={`alert alert-${type}`}>
      <span>{message}</span>
      {dismissible && onDismiss && (
        <button onClick={onDismiss} className="alert-dismiss">
          ×
        </button>
      )}
    </div>
  );
};

Alert.defaultProps = {
  dismissible: false,
  type: 'info',
};

// 3. 使用 Partial 和 Required 工具类型
interface Config {
  apiUrl: string;
  timeout: number;
  retries: number;
  debug: boolean;
}

// 组件接受部分配置
function ApiClient({ config }: { config: Partial<Config> }) {
  // 合并默认配置
  const fullConfig: Required<Config> = {
    apiUrl: 'https://api.example.com',
    timeout: 5000,
    retries: 3,
    debug: false,
    ...config,
  };
  
  // 使用完整配置
  return <div>API 客户端配置: {JSON.stringify(fullConfig)}</div>;
}

// 4. 处理复杂的默认值逻辑
interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  visiblePages?: number; // 显示多少页码
  showFirstLast?: boolean; // 显示首尾页
  showPrevNext?: boolean; // 显示上下页
  className?: string;
}

function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  visiblePages = 5,
  showFirstLast = true,
  showPrevNext = true,
  className = '',
}: PaginationProps) {
  // 计算要显示的页码
  const pages = calculateVisiblePages(currentPage, totalPages, visiblePages);
  
  return (
    <nav className={`pagination ${className}`}>
      {showFirstLast && currentPage > 1 && (
        <button onClick={() => onPageChange(1)}>首页</button>
      )}
      
      {showPrevNext && currentPage > 1 && (
        <button onClick={() => onPageChange(currentPage - 1)}>上一页</button>
      )}
      
      {pages.map(page => (
        <button
          key={page}
          onClick={() => onPageChange(page)}
          className={page === currentPage ? 'active' : ''}
        >
          {page}
        </button>
      ))}
      
      {showPrevNext && currentPage < totalPages && (
        <button onClick={() => onPageChange(currentPage + 1)}>下一页</button>
      )}
      
      {showFirstLast && currentPage < totalPages && (
        <button onClick={() => onPageChange(totalPages)}>尾页</button>
      )}
    </nav>
  );
}
```

### 10.3 事件处理与类型

```typescript
// 问题：如何正确定义事件处理函数类型？

// 1. 表单事件
interface LoginFormProps {
  onLogin: (credentials: { email: string; password: string }) => void;
  onCancel?: () => void;
}

function LoginForm({ onLogin, onCancel }: LoginFormProps) {
  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    
    const formData = new FormData(event.currentTarget);
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;
    
    onLogin({ email, password });
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>邮箱:</label>
        <input type="email" name="email" required />
      </div>
      <div>
        <label>密码:</label>
        <input type="password" name="password" required />
      </div>
      <div>
        <button type="submit">登录</button>
        {onCancel && <button type="button" onClick={onCancel}>取消</button>}
      </div>
    </form>
  );
}

// 2. 鼠标和键盘事件
interface InteractiveCardProps {
  title: string;
  content: string;
  onClick?: (event: React.MouseEvent<HTMLDivElement>) => void;
  onDoubleClick?: (event: React.MouseEvent<HTMLDivElement>) => void;
  onMouseEnter?: (event: React.MouseEvent<HTMLDivElement>) => void;
  onMouseLeave?: (event: React.MouseEvent<HTMLDivElement>) => void;
  onKeyDown?: (event: React.KeyboardEvent<HTMLDivElement>) => void;
}

function InteractiveCard({
  title,
  content,
  onClick,
  onDoubleClick,
  onMouseEnter,
  onMouseLeave,
  onKeyDown,
}: InteractiveCardProps) {
  return (
    <div
      className="interactive-card"
      tabIndex={0} // 使元素可聚焦
      onClick={onClick}
      onDoubleClick={onDoubleClick}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      onKeyDown={onKeyDown}
    >
      <h3>{title}</h3>
      <p>{content}</p>
    </div>
  );
}

// 3. 变化事件
interface SearchInputProps {
  value: string;
  onChange: (value: string, event: React.ChangeEvent<HTMLInputElement>) => void;
  onSearch?: (value: string) => void;
  placeholder?: string;
  debounceMs?: number;
}

function SearchInput({
  value,
  onChange,
  onSearch,
  placeholder = '搜索...',
  debounceMs = 300,
}: SearchInputProps) {
  const [internalValue, setInternalValue] = useState(value);
  const timerRef = useRef<NodeJS.Timeout>();
  
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.value;
    setInternalValue(newValue);
    onChange(newValue, event);
    
    // 防抖处理
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }
    
    if (onSearch) {
      timerRef.current = setTimeout(() => {
        onSearch(newValue);
      }, debounceMs);
    }
  };
  
  // 清理定时器
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, []);
  
  return (
    <div className="search-input">
      <input
        type="text"
        value={internalValue}
        onChange={handleChange}
        placeholder={placeholder}
      />
    </div>
  );
}

// 4. 自定义事件
interface CustomEventProps {
  onCustomEvent: (data: { type: string; payload: any }) => void;
}

function CustomEventComponent({ onCustomEvent }: CustomEventProps) {
  const handleClick = () => {
    onCustomEvent({
      type: 'BUTTON_CLICKED',
      payload: { timestamp: Date.now(), userId: '123' },
    });
  };
  
  return (
    <button onClick={handleClick}>
      触发自定义事件
    </button>
  );
}
```

### 10.4 类型断言与类型转换

```typescript
// 问题：何时使用类型断言？如何安全地进行类型转换？

// 1. 安全的类型断言
interface ApiResponse {
  data: unknown;
  status: number;
}

// 使用类型守卫
function isUserResponse(data: unknown): data is { users: User[] } {
  return (
    typeof data === 'object' &&
    data !== null &&
    'users' in data &&
    Array.isArray((data as any).users)
  );
}

// 使用类型断言函数
function assertIsString(value: unknown): asserts value is string {
  if (typeof value !== 'string') {
    throw new Error(`Expected string, got ${typeof value}`);
  }
}

// 在组件中使用
function UserList({ response }: { response: ApiResponse }) {
  if (isUserResponse(response.data)) {
    // TypeScript 知道 response.data.users 是 User[]
    return (
      <div>
        {response.data.users.map(user => (
          <div key={user.id}>{user.name}</div>
        ))}
      </div>
    );
  }
  
  // 尝试类型转换
  try {
    const data = response.data as { items: any[] };
    if (Array.isArray(data.items)) {
      return (
        <div>
          {data.items.map((item, index) => (
            <div key={index}>{JSON.stringify(item)}</div>
          ))}
        </div>
      );
    }
  } catch {
    // 类型转换失败
  }
  
  return <div>无法解析数据</div>;
}

// 2. 使用 as 进行类型断言
function processInput(value: string | number) {
  // 在某些情况下，我们知道值的具体类型
  if (typeof value === 'string') {
    const length = (value as string).length; // 不必要的断言
    const lengthBetter = value.length; // 更好的方式：TypeScript 已经知道是 string
  }
  
  // 必要的类型断言：从父元素获取特定子元素
  const container = document.getElementById('container') as HTMLDivElement;
  const input = container.querySelector('input[type="text"]') as HTMLInputElement;
}

// 3. 非空断言（谨慎使用）
interface UserProfileProps {
  user?: {
    name: string;
    email: string;
  };
  onUpdate?: (user: { name: string; email: string }) => void;
}

function UserProfile({ user, onUpdate }: UserProfileProps) {
  // ❌ 不安全的非空断言
  // const userName = user!.name;
  
  // ✅ 安全的处理
  if (!user) {
    return <div>用户数据加载中...</div>;
  }
  
  // ✅ 使用可选链和空值合并
  const userName = user?.name ?? '未知用户';
  const userEmail = user?.email ?? '无邮箱';
  
  return (
    <div>
      <h3>{userName}</h3>
      <p>{userEmail}</p>
      {onUpdate && (
        <button onClick={() => onUpdate(user)}>更新用户</button>
      )}
    </div>
  );
}

// 4. 双重断言（极少使用）
function handleUnknownValue(value: unknown) {
  // 双重断言：先断言为 any，再断言为目标类型
  const element = value as any as HTMLElement;
  
  // 更好的方式：使用类型守卫
  function isHTMLElement(value: unknown): value is HTMLElement {
    return value instanceof HTMLElement;
  }
  
  if (isHTMLElement(value)) {
    // 安全地使用 value 作为 HTMLElement
    return value.tagName;
  }
  
  return '不是 HTML 元素';
}
```

## 十一、性能考虑与优化

### 11.1 类型定义对性能的影响

```typescript
// 1. 避免过度复杂的类型
// ❌ 过度复杂
type OverlyComplexType = {
  [K in keyof SomeType as `get${Capitalize<string & K>}`]?: 
    SomeType[K] extends (...args: any[]) => any 
      ? ReturnType<SomeType[K]>
      : SomeType[K] extends object
      ? DeepPartial<SomeType[K]>
      : SomeType[K];
};

// ✅ 简化类型
type SimplifiedType = {
  id: string;
  name: string;
  metadata?: Record<string, any>;
};

// 2. 使用接口而不是复杂的类型别名
// ✅ 接口更高效
interface User {
  id: string;
  name: string;
  email: string;
  profile?: {
    avatar?: string;
    bio?: string;
  };
}

// ❌ 复杂的类型别名可能影响性能
type ComplexUser = {
  id: string;
  name: string;
  email: string;
  profile?: {
    avatar?: string;
    bio?: string;
  };
} & {
  [K in `meta_${string}`]?: string;
};

// 3. 避免递归类型深度过大
// ❌ 深度递归
type DeepNested<T, Depth extends number> = 
  Depth extends 0 
    ? T 
    : { data: DeepNested<T, Prev<Depth>> };

// ✅ 限制递归深度
type SafeNested<T> = {
  data?: T;
  children?: SafeNested<T>[];
};

// 4. 使用 const 断言减少类型计算
const BUTTON_VARIANTS = ['primary', 'secondary', 'outline'] as const;
type ButtonVariant = typeof BUTTON_VARIANTS[number]; // 高效的类型推导

const CONFIG = {
  api: {
    baseUrl: 'https://api.example.com',
    timeout: 5000,
  },
  features: {
    darkMode: true,
    analytics: false,
  },
} as const; // 深度只读，类型推导更高效
```

### 11.2 组件 Props 的性能优化

```typescript
// 1. 使用 React.memo 避免不必要的重渲染
interface ExpensiveComponentProps {
  data: LargeDataObject;
  onUpdate: (id: string) => void;
}

// 使用 React.memo 和 useCallback
const ExpensiveComponent = React.memo(function ExpensiveComponent({
  data,
  onUpdate,
}: ExpensiveComponentProps) {
  // 昂贵的渲染逻辑
  return (
    <div>
      {/* 组件内容 */}
    </div>
  );
});

// 在父组件中
function ParentComponent() {
  const [data, setData] = useState<LargeDataObject>(/* ... */);
  
  // 使用 useCallback 记忆化回调
  const handleUpdate = useCallback((id: string) => {
    // 更新逻辑
  }, [/* 依赖 */]);
  
  return <ExpensiveComponent data={data} onUpdate={handleUpdate} />;
}

// 2. 使用 useMemo 记忆化计算
interface DataTableProps<T> {
  data: T[];
  columns: ColumnConfig<T>[];
  sortBy?: keyof T;
  filter?: (item: T) => boolean;
}

function DataTable<T>({ data, columns, sortBy, filter }: DataTableProps<T>) {
  // 使用 useMemo 避免重复计算
  const processedData = useMemo(() => {
    let result = [...data];
    
    if (filter) {
      result = result.filter(filter);
    }
    
    if (sortBy) {
      result.sort((a, b) => {
        const aVal = a[sortBy];
        const bVal = b[sortBy];
        return String(aVal).localeCompare(String(bVal));
      });
    }
    
    return result;
  }, [data, filter, sortBy]);
  
  return (
    <table>
      {/* 使用 processedData */}
    </table>
  );
}

// 3. 分割大型 Props 接口
// ❌ 大型单一接口
interface MonolithicComponentProps {
  // 50+ 个属性...
}

// ✅ 分割为多个接口
interface BaseProps {
  className?: string;
  style?: React.CSSProperties;
}

interface DataProps {
  data: DataType;
  isLoading?: boolean;
  error?: string;
}

interface ActionProps {
  onEdit?: (id: string) => void;
  onDelete?: (id: string) => void;
  onSave?: (data: DataType) => void;
}

interface ComponentProps extends BaseProps, DataProps, ActionProps {
  // 组件特定属性
  variant?: 'compact' | 'detailed';
}

// 4. 使用 Pick 或 Omit 创建轻量级 Props
interface FullUserProps {
  user: User;
  onSelect: (user: User) => void;
  showDetails: boolean;
  showActions: boolean;
  className: string;
  style: React.CSSProperties;
  // ... 更多属性
}

// 创建轻量版 Props
type LightweightUserProps = Pick<FullUserProps, 'user' | 'onSelect'>;

// 或者排除不需要的属性
type MinimalUserProps = Omit<FullUserProps, 'showDetails' | 'showActions' | 'style'>;

function LightweightUserCard({ user, onSelect }: LightweightUserProps) {
  // 轻量级组件
  return (
    <div onClick={() => onSelect(user)}>
      {user.name}
    </div>
  );
}
```

### 11.3 构建时的类型优化

```typescript
// 1. 使用路径别名简化导入
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@components/*": ["src/components/*"],
      "@types/*": ["src/types/*"],
      "@utils/*": ["src/utils/*"]
    }
  }
}

// 在组件中使用
import { User } from '@types/user';
import { Button } from '@components/Button';
import { formatDate } from '@utils/date';

// 2. 使用项目范围的类型定义
// src/types/props.ts
export type CommonProps = {
  className?: string;
  'data-testid'?: string;
  style?: React.CSSProperties;
};

export type ClickableProps = CommonProps & {
  onClick?: () => void;
  disabled?: boolean;
};

export type WithChildren = {
  children: React.ReactNode;
};

// 3. 使用类型导出减少重复
// src/types/index.ts
export * from './props';
export * from './user';
export * from './api';

// 4. 配置 TypeScript 严格模式
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    // 其他配置...
  }
}
```

## 十二、总结与最佳实践

### 12.1 核心要点总结

1. **Props 类型定义是 React + TypeScript 的核心**
   - 提供编译时类型检查
   - 增强代码可读性和可维护性
   - 改善开发体验和团队协作

2. **接口 vs 类型别名**
   - 使用接口定义对象形状（特别是组件 Props）
   - 使用类型别名定义联合类型、元组和复杂类型
   - 接口支持声明合并，类型别名更灵活

3. **React.FC 的现状**
   - 优点：隐式 children、更好的 defaultProps 支持
   - 缺点：隐式 children 问题、泛型支持差、社区趋势已转向简单函数
   - 建议：使用简单函数声明，明确声明 children 类型

4. **最佳实践**
   - 明确声明所有 Props 类型
   - 使用解构默认值而不是 defaultProps
   - 合理使用实用类型（Partial、Pick、Omit 等）
   - 编写类型守卫函数确保类型安全

### 12.2 推荐的工作流程

```typescript
// 1. 定义类型文件
// src/types/user.ts
export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  age?: number;
}

// src/types/props.ts
export interface BaseProps {
  className?: string;
  'data-testid'?: string;
}

// 2. 定义组件 Props
// src/components/UserCard/types.ts
import { User } from '../../types/user';
import { BaseProps } from '../../types/props';

export interface UserCardProps extends BaseProps {
  user: User;
  onSelect: (userId: string) => void;
  isSelected?: boolean;
  showDetails?: boolean;
  children?: React.ReactNode;
}

// 3. 实现组件
// src/components/UserCard/index.tsx
import { UserCardProps } from './types';

export function UserCard({
  user,
  onSelect,
  isSelected = false,
  showDetails = true,
  className = '',
  children,
}: UserCardProps) {
  return (
    <div className={`user-card ${isSelected ? 'selected' : ''} ${className}`}>
      {user.avatar && <img src={user.avatar} alt={user.name} />}
      <h3>{user.name}</h3>
      {showDetails && <p>{user.email}</p>}
      {children}
      <button onClick={() => onSelect(user.id)}>
        {isSelected ? '已选择' : '选择'}
      </button>
    </div>
  );
}

// 4. 使用组件
// src/pages/UserList.tsx
import { UserCard } from '../components/UserCard';
import { User } from '../types/user';

function UserList({ users }: { users: User[] }) {
  const [selectedId, setSelectedId] = useState<string>();
  
  return (
    <div>
      {users.map(user => (
        <UserCard
          key={user.id}
          user={user}
          onSelect={setSelectedId}
          isSelected={user.id === selectedId}
          data-testid={`user-card-${user.id}`}
        >
          <p>额外信息</p>
        </UserCard>
      ))}
    </div>
  );
}
```

### 12.3 常见陷阱与解决方案

| 问题 | 错误示例 | 解决方案 |
|------|----------|----------|
| **隐式 any 类型** | `function Component(props) {}` | 明确声明 Props 类型 |
| **过度使用类型断言** | `const data = value as User;` | 使用类型守卫函数 |
| **忽略可选属性** | 访问未定义的属性 | 使用可选链 `?.` 或空值合并 `??` |
| **复杂的联合类型** | 难以维护的类型定义 | 分割为多个接口，使用类型守卫 |
| **性能问题** | 深度递归类型 | 限制递归深度，使用接口代替复杂类型别名 |

### 12.4 未来发展趋势

1. **React 类型系统演进**
   - 更好的泛型组件支持
   - 改进的 JSX 类型推断
   - 与 React Compiler 更好的集成

2. **TypeScript 新特性**
   - 模板字面量类型增强
   - 更好的条件类型推断
   - 改进的泛型约束

3. **开发工具改进**
   - 更快的类型检查
   - 更好的重构支持
   - 增强的类型提示

### 12.5 学习资源推荐

1. **官方文档**
   - [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
   - [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)

2. **进阶学习**
   - [TypeScript Deep Dive](https://basarat.gitbook.io/typescript/)
   - [React + TypeScript 最佳实践](https://github.com/typescript-cheatsheets/react)

3. **工具与库**
   - [ts-morph](https://github.com/dsherret/ts-morph)：TypeScript AST 操作
   - [type-fest](https://github.com/sindresorhus/type-fest)：实用类型集合
   - [zod](https://github.com/colinhacks/zod)：运行时类型验证

### 结语

React + TypeScript 的组合为现代前端开发提供了强大的类型安全保证。通过合理定义组件 Props 类型，我们可以：

1. **提高代码质量**：编译时捕获类型错误
2. **提升开发效率**：智能提示和自动补全
3. **增强团队协作**：清晰的类型约定
4. **改善维护性**：类型即文档

记住，好的类型定义应该是：
- **明确的**：清晰表达组件契约
- **简洁的**：避免不必要的复杂性
- **可维护的**：易于修改和扩展
- **性能友好的**：不影响构建和开发体验

随着 TypeScript 和 React 生态的不断发展，类型系统将变得更加强大和易用。掌握 Props 类型定义的艺术，将使你成为更高效的 React 开发者。

---
*文档创建完成：React + TypeScript Props 类型定义与 React.FC 深度解析*
*创建时间：2026-03-30*
*文档版本：1.0.0*
*作者：React + TypeScript 技术专家*
