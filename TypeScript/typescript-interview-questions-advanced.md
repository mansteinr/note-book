# TypeScript高级工程师面试题集

## 目录

- [高级类型](#高级类型)
- [类型推断](#类型推断)
- [类型守卫与类型收窄](#类型守卫与类型收窄)
- [装饰器](#装饰器)
- [高级泛型](#高级泛型)
- [模板字面量与映射类型](#模板字面量与映射类型)
- [TypeScript高级应用](#typescript高级应用)
- [类型系统原理与工程实践](#类型系统原理与工程实践)

---

## 高级类型

### 题目1

**题目描述**：请解释以下类型的区别和适用场景：`any` vs `unknown` vs `never`。

**代码示例**：
```typescript
// 请分析这三段代码的区别
let a: any = 100;
let b: unknown = 100;
let c: never;

a.toUpperCase();  // 允许
b.toUpperCase();  // 不允许
// c = 123;       // 不允许
```

**参考答案**：

#### 区别说明

| 类型 | 说明 | 类型检查强度 | 适用场景 |
|------|------|------------|---------|
| `any` | 任意类型，逃避类型检查 | 弱 | 快速迁移JS代码、非类型安全场景 |
| `unknown` | 未知类型，需要类型收窄 | 中 | 不确定类型但需要安全检查 |
| `never` | 永不存在值的类型 | 强 | 表示函数不会正常返回、穷举检查 |

#### 详细分析

```typescript
// 1. any：完全失去类型检查
let a: any = 100;
a.toUpperCase();  // ❌ 编译通过但运行时错误！
// 不推荐，慎用！

// 2. unknown：类型安全的未知类型
let b: unknown = 100;
// b.toUpperCase();  // ✅ 编译报错，安全！

// unknown类型收窄后使用
if (typeof b === 'string') {
  b.toUpperCase();  // ✅ 安全
}

// 3. never：表示不可能的类型
function error(message: string): never {
  throw new Error(message);  // 永远不会正常返回
}
```

#### 评分标准

- 能区分 `any` 和 `unknown`：60分
- 能说明 `never` 的应用：80分
- 完整说明三者的适用场景和区别：100分

---

### 题目2

**题目描述**：请实现一个类型 `DeepReadonly<T>`，可以将对象的所有属性（包括嵌套属性）设置为只读。

**代码示例**：
```typescript
interface Person {
  name: string;
  age: number;
  address: {
    city: string;
  };
}

// 你的实现
type DeepReadonly<T> = /* ??? */;

// 期望效果
type ReadonlyPerson = DeepReadonly<Person>;
// 结果类型：
// {
//   readonly name: string;
//   readonly age: number;
//   readonly address: {
//     readonly city: string;
//   };
// }
```

**参考答案**：

```typescript
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object 
    ? T[K] extends Function 
      ? T[K]
      : DeepReadonly<T[K]>
    : T[K];
};
```

#### 实现解析

1. **映射类型**：`[K in keyof T]` 遍历对象所有键
2. **条件类型**：`T[K] extends object` 判断是否对象类型
3. **递归处理**：对象类型递归应用 `DeepReadonly`
4. **函数特殊处理**：函数类型直接保留，不做只读处理

#### 进阶版本（包含数组）

```typescript
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends (infer U)[]
    ? readonly U[]
    : T[K] extends object
      ? DeepReadonly<T[K]>
      : T[K];
};
```

#### 评分标准

- 能实现简单的只读：60分
- 能处理嵌套对象：80分
- 能正确处理函数和数组：100分

---

### 题目3

**题目描述**：请实现类型 `Merge<F, S>`，合并两个对象类型，S 的属性覆盖 F 的属性。

**代码示例**：
```typescript
type A = { name: string; age: number };
type B = { age: string; gender: 'male' | 'female' };

// 你的实现
type Merge<F, S> = /* ??? */;

// 期望效果
type C = Merge<A, B>;
// 结果：{ name: string; age: string; gender: 'male' | 'female' }
```

**参考答案**：

```typescript
type Merge<F, S> = {
  [K in keyof F | keyof S]: K extends keyof S 
    ? S[K] 
    : K extends keyof F ? F[K] : never;
};
```

#### 实现解析

1. 联合键：`keyof F | keyof S` 包含两个对象的所有键
2. 条件判断：先判断键是否在 S 中，在的话优先用 S 类型
3. 否则用 F 类型

#### 更好的实现方式

```typescript
type Merge<F, S> = Omit<F, keyof S> & S;
```

#### 评分标准

- 能理解类型合并需求：60分
- 能实现正确的合并逻辑：80分
- 能想到更简洁的 Omit 写法：100分

---

## 类型推断

### 题目4

**题目描述**：请解释 TypeScript 的类型推断机制，特别是 `infer` 关键字的作用。

**代码示例**：
```typescript
// 请实现 ReturnType
type ReturnType<T> = /* ??? */;

type Fn = (a: number) => string;
type Result = ReturnType<Fn>;  // 应该是 string
```

**参考答案**：

#### TypeScript 类型推断概述

TypeScript 有多种类型推断机制：
1. 初始值推断
2. 函数返回值推断
3. 上下文类型推断
4. 类型参数推断

#### infer 关键字详解

`infer` 只能在条件类型中使用，用于推断类型参数。

```typescript
// 实现 ReturnType
type ReturnType<T extends (...args: any[]) => any> = 
  T extends (...args: any[]) => infer R
    ? R
    : never;
```

#### 更多 infer 用法示例

```typescript
// 获取数组元素类型
type ElementType<T> = T extends (infer U)[] ? U : never;
type E = ElementType<number[]>;  // number

// 获取 Promise 内部类型
type UnwrapPromise<T> = T extends Promise<infer U> ? U : never;
type U = UnwrapPromise<Promise<string>>;  // string

// 获取函数参数类型
type FirstArg<T> = T extends (arg: infer A) => any ? A : never;
type FA = FirstArg<(x: number) => void>;  // number
```

#### 评分标准

- 能解释 infer 的基本作用：60分
- 能实现 ReturnType：80分
- 能展示多种 infer 应用：100分

---

### 题目5

**题目描述**：请实现类型 `PickByType<T, U>`，从对象类型 T 中挑选出类型为 U 的属性。

**代码示例**：
```typescript
interface Person {
  name: string;
  age: number;
  phone: string;
  isStudent: boolean;
}

// 你的实现
type PickByType<T, U> = /* ??? */;

// 期望效果
type StringKeys = PickByType<Person, string>;
// 结果：{ name: string; phone: string }
```

**参考答案**：

```typescript
type PickByType<T, U> = {
  [K in keyof T as T[K] extends U ? K : never]: T[K]
};
```

#### 实现解析

1. **映射类型 + 键重映射**：`as` 语法在 TypeScript 4.1+ 支持
2. **条件判断**：`T[K] extends U` 判断属性值类型是否匹配
3. **never 过滤**：不匹配的键重映射为 `never`，会自动被过滤

#### 键重映射的其他应用

```typescript
// 去掉 readonly
type Mutable<T> = {
  -readonly [K in keyof T]: T[K]
};

// 去掉可选
type Required<T> = {
  [K in keyof T]-?: T[K]
};
```

#### 评分标准

- 理解类型过滤需求：60分
- 知道键重映射语法：80分
- 完整实现并理解原理：100分

---

## 类型守卫与类型收窄

### 题目6

**题目描述**：请实现一个类型守卫，可以判断一个值是否是有效的 URL 字符串。

**代码示例**：
```typescript
// 你的实现
function isValidUrl(x: unknown): x is string {
  /* ??? */
}

// 使用方式
function processUrl(input: string | number) {
  if (isValidUrl(input)) {
    // 这里 input 应该被正确收窄为 string 类型
    console.log(input.toUpperCase());
  }
}
```

**参考答案**：

```typescript
function isValidUrl(x: unknown): x is string {
  if (typeof x !== 'string') {
    return false;
  }
  try {
    new URL(x);
    return true;
  } catch {
    return false;
  }
}
```

#### 类型守卫的完整实现

```typescript
// 更好的实现，还可以有更多检查
function isValidUrl(x: unknown): x is string {
  // 1. 先确保是 string
  if (typeof x !== 'string') {
    return false;
  }
  
  // 2. 尝试构造 URL
  try {
    const url = new URL(x);
    return url.protocol === 'http:' || url.protocol === 'https:';
  } catch {
    return false;
  }
}
```

#### 更多类型守卫示例

```typescript
// 自定义类型守卫
interface Cat { meow(): void; }
interface Dog { bark(): void; }

function isCat(x: Cat | Dog): x is Cat {
  return 'meow' in x;
}

// is 类型守卫 + 断言函数
function assert(x: unknown): asserts x is string {
  if (typeof x !== 'string') {
    throw new Error('Not a string');
  }
}

// 使用断言函数
function f(x: unknown) {
  assert(x);
  x.toUpperCase();  // ✅ x is string
}
```

#### 评分标准

- 理解类型守卫的作用：60分
- 能实现基本的 URL 检查：80分
- 完整的实现 + 更多类型守卫知识：100分

---

### 题目7

**题目描述**：请解释 TypeScript 类型收窄的各种方式，并说明它们的适用场景。

**参考答案**：

#### TypeScript 类型收窄方式

1. **typeof 类型守卫**
```typescript
function process(x: string | number) {
  if (typeof x === 'string') {
    x.toUpperCase();  // x is string
  }
}
```

2. **instanceof 类型守卫**
```typescript
if (x instanceof Date) {
  x.getFullYear();  // x is Date
}
```

3. **in 运算符**
```typescript
if ('meow' in x) {
  x.meow();  // x has meow property
}
```

4. **等值收窄**
```typescript
function process(x: 'a' | 'b' | number) {
  if (x === 'a') {
    x;  // 'a'
  }
}
```

5. **类型谓词（自定义类型守卫）**
```typescript
function isString(x: unknown): x is string {
  return typeof x === 'string';
}
```

6. **可辨识联合**
```typescript
type Circle = { type: 'circle'; radius: number };
type Square = { type: 'square'; side: number };

function area(shape: Circle | Square) {
  switch (shape.type) {  // 'type' 是可辨识属性
    case 'circle': return Math.PI * shape.radius ** 2;
    case 'square': return shape.side ** 2;
  }
}
```

7. **断言函数**
```typescript
function assertIsDefined<T>(val: T): asserts val is NonNullable<T> {
  if (val == null) {
    throw new Error('Not defined');
  }
}
```

#### 评分标准

- 能说明 3-4 种方式：60分
- 能说明全部方式并举例子：80分
- 能深入解释原理和适用场景：100分

---

## 装饰器

### 题目8

**题目描述**：请实现一个日志装饰器，可以打印函数调用信息。

**代码示例**：
```typescript
// 你的装饰器实现
function log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  /* ??? */
}

// 使用方式
class Calculator {
  @log
  add(a: number, b: number) {
    return a + b;
  }
}

const calc = new Calculator();
calc.add(1, 2);
// 期望输出：Calling add with [1, 2], result: 3
```

**参考答案**：

```typescript
function log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  
  descriptor.value = function(...args: any[]) {
    console.log(`Calling ${propertyKey} with [${args.join(', ')}]`);
    const result = originalMethod.apply(this, args);
    console.log(`Result: ${result}`);
    return result;
  };
}
```

#### 完整的装饰器实现（含 TypeScript 类型）

```typescript
function log() {
  return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value as (...args: any[]) => any;
    
    descriptor.value = function(...args: any[]) {
      console.log(`Calling ${propertyKey} with ${JSON.stringify(args)}`);
      
      try {
        const result = originalMethod.apply(this, args);
        
        if (result instanceof Promise) {
          return result.then(r => {
            console.log(`Async result: ${JSON.stringify(r)}`);
            return r;
          }).catch(err => {
            console.error(`Error: ${err}`);
            throw err;
          });
        } else {
          console.log(`Result: ${JSON.stringify(result)}`);
          return result;
        }
      } catch (err) {
        console.error(`Error: ${err}`);
        throw err;
      }
    };
  };
}

// 使用装饰器工厂
class Calculator {
  @log()
  add(a: number, b: number) {
    return a + b;
  }
  
  @log()
  async asyncAdd(a: number, b: number) {
    await new Promise(r => setTimeout(r, 100));
    return a + b;
  }
}
```

#### 装饰器类型

1. 类装饰器
2. 方法装饰器
3. 访问器装饰器
4. 属性装饰器
5. 参数装饰器

#### 评分标准

- 能实现基本的日志功能：60分
- 能处理 Promise 异步函数：80分
- 完整理解装饰器机制和类型：100分

---

### 题目9

**题目描述**：请实现一个属性验证装饰器，可以验证类属性的取值。

**代码示例**：
```typescript
// 你的实现
function MinLength(min: number) {
  /* ??? */
}

// 使用方式
class User {
  @MinLength(3)
  username: string;
  
  constructor(username: string) {
    this.username = username;
  }
}

new User('al');  // 应该报错：username length must be at least 3
new User('bob'); // 应该正常
```

**参考答案**：

```typescript
function MinLength(min: number) {
  return function(target: any, propertyKey: string) {
    let value: string;
    
    const getter = function() {
      return value;
    };
    
    const setter = function(newVal: string) {
      if (newVal.length < min) {
        throw new Error(`${propertyKey} must be at least ${min} characters long`);
      }
      value = newVal;
    };
    
    Object.defineProperty(target, propertyKey, {
      get: getter,
      set: setter,
      enumerable: true,
      configurable: true
    });
  };
}
```

#### 评分标准

- 理解属性装饰器机制：60分
- 能实现基本的验证逻辑：80分
- 完整的类型和错误处理：100分

---

## 高级泛型

### 题目10

**题目描述**：请解释 TypeScript 中 `extends` 在不同上下文中的作用。

**参考答案**：

#### extends 的多种用法

1. **接口继承**
```typescript
interface A { x: number }
interface B extends A { y: number }
```

2. **泛型约束**
```typescript
function fn<T extends { x: number }>(arg: T) {
  return arg.x;
}
```

3. **条件类型**
```typescript
type IsString<T> = T extends string ? true : false;
```

4. **分布条件类型（分布式）**
```typescript
type ToArray<T> = T extends any ? T[] : never;
// ToArray<string | number> 是 string[] | number[]（分布）
```

#### 深入说明条件类型分布

```typescript
// 条件类型在联合类型上会自动分发
type Distribute<T> = T extends any ? [T] : never;
type Test1 = Distribute<string | number>;
// [string] | [number]

// 不希望分布的话，可以用括号包裹
type NonDistribute<T> = [T] extends [any] ? [T] : never;
type Test2 = NonDistribute<string | number>;
// [string | number]
```

#### 评分标准

- 能说明 2-3 种用法：60分
- 能说明全部 4 种用法：80分
- 深入理解分布条件类型：100分

---

### 题目11

**题目描述**：请实现一个类型 `Awaited<T>`，解析 Promise 类型（类似 TypeScript 内置的 Awaited）。

**代码示例**：
```typescript
// 你的实现
type Awaited<T> = /* ??? */;

// 期望效果
type Result1 = Awaited<Promise<string>>;            // string
type Result2 = Awaited<Promise<Promise<number>>>;   // number (递归解析)
type Result3 = Awaited<string>;                     // string (不是 Promise)
```

**参考答案**：

```typescript
type Awaited<T> =
  T extends PromiseLike<infer U>
    ? Awaited<U>
    : T;
```

#### 实现解析

1. **递归类型**：持续解析直到不是 Promise
2. **PromiseLike**：匹配任何 thenable 对象，不是只有 Promise

#### 更完整的实现

```typescript
type Awaited<T> =
  T extends null | undefined
    ? T
    : T extends PromiseLike<infer U>
      ? Awaited<U>
      : T;
```

#### 评分标准

- 能解析单层 Promise：60分
- 能递归解析嵌套 Promise：80分
- 完整处理 null/undefined：100分

---

## 模板字面量与映射类型

### 题目12

**题目描述**：请利用模板字面量类型，实现一个类型，可以将对象的所有键转换为驼峰命名法。

**代码示例**：
```typescript
interface SnakeCase {
  user_id: number;
  user_name: string;
  created_at: Date;
}

// 你的实现
type CamelCase<S extends string> = /* ??? */;
type CamelizeKeys<T> = {
  [K in keyof T as CamelCase<string & K>]: T[K];
};

// 期望效果
type CamelCaseObj = CamelizeKeys<SnakeCase>;
// {
//   userId: number;
//   userName: string;
//   createdAt: Date;
// }
```

**参考答案**：

```typescript
type CamelCase<S extends string> = 
  S extends `${infer Prefix}_${infer First}${infer Rest}`
    ? `${Prefix}${Uppercase<First>}${CamelCase<Rest>}`
    : S;
```

#### 完整实现

```typescript
// 辅助类型：Capitalize 只大写首字母（TypeScript 内置）
type _CamelCase<S extends string> =
  S extends `${infer First}_${infer Rest}`
    ? `${Lowercase<First>}${_CamelCase<Capitalize<Rest>>}`
    : S;

type CamelCaseKeys<T> = {
  [K in keyof T as _CamelCase<string & K>]: T[K];
};
```

#### 更多模板字面量应用

```typescript
// 1. CSS 属性单位
type CSSProp = `${string}px` | `${string}%`;
const w: CSSProp = '100px';

// 2. 事件名类型
type EventName = `on${Capitalize<string>}`;
const click: EventName = 'onClick';

// 3. URL 路径参数
type PathParam<T> = T extends `:${infer Param}` ? Param : never;
type UserId = PathParam<'/api/users/:id'>;  // 'id'
```

#### 评分标准

- 理解模板字面量的基本语法：60分
- 能实现简单的转换：80分
- 完整实现递归转换：100分

---

### 题目13

**题目描述**：请实现类型 `Flatten<T>`，将嵌套数组扁平化。

**代码示例**：
```typescript
// 你的实现
type Flatten<T> = /* ??? */;

// 期望效果
type Test1 = Flatten<[1, [2, [3]], 4]>;  // [1, 2, 3, 4]
type Test2 = Flatten<[[string], [number]]>; // [string, number]
```

**参考答案**：

```typescript
type Flatten<T extends any[]> = 
  T extends [infer First, ...infer Rest]
    ? First extends any[]
      ? [...Flatten<First>, ...Flatten<Rest>]
      : [First, ...Flatten<Rest>]
    : [];
```

#### 实现解析

1. **infer + 剩余模式**：解构数组第一个元素和剩余元素
2. **递归**：如果第一个元素是数组，递归展开
3. **拼接数组**：用 `[...A, ...B]` 语法

#### 评分标准

- 理解数组模式匹配：60分
- 能实现单层展开：80分
- 完整递归展开：100分

---

## TypeScript高级应用

### 题目14

**题目描述**：请说明 TypeScript 中 `strict` 模式包含哪些选项，它们的作用是什么。

**参考答案**：

#### strict 模式包含的选项

```json
{
  "compilerOptions": {
    "strict": true
  }
}
```

相当于同时启用：

1. **noImplicitAny**：不允许隐式 any
2. **noImplicitThis**：不允许 this 类型隐式为 any
3. **strictNullChecks**：严格 null 检查
4. **strictFunctionTypes**：严格函数类型检查
5. **strictPropertyInitialization**：严格属性初始化
6. **strictBindCallApply**：严格检查 bind/call/apply
7. **useUnknownInCatchVariables**：catch 变量默认为 unknown

#### 每个选项的详细作用

```typescript
// 1. noImplicitAny
function add(a, b) {  // ❌ 参数类型隐式 any
  return a + b;
}

// 2. strictNullChecks
const str: string = null;  // ❌ 严格模式报错

// 3. strictPropertyInitialization
class Person {
  name: string;  // ❌ 没有初始化
}

// 4. strictFunctionTypes
type Callback = (x: string) => void;
const fn: Callback = (x: number) => {};  // ❌ 函数类型不兼容
```

#### 评分标准

- 知道 `strict` 是一组选项：60分
- 能列举 4-5 个选项并说明：80分
- 完整理解所有选项及其作用：100分

---

### 题目15

**题目描述**：请实现一个类型安全的状态管理库的类型定义（类似 Redux 或 Pinia）。

**代码示例**：
```typescript
// 你的类型定义
interface Store<S, A> {
  getState: () => S;
  dispatch: (action: A) => void;
  subscribe: (listener: (state: S) => void) => () => void;
}

function createStore<S, A>(reducer: (state: S, action: A) => S, initialState: S): Store<S, A> {
  /* 实现 */
}

// 使用方式
type State = { count: number };
type Action = { type: 'inc' } | { type: 'dec' };

const store = createStore<State, Action>(
  (state, action) => {
    switch (action.type) {
      case 'inc': return { count: state.count + 1 };
      case 'dec': return { count: state.count - 1 };
      default: return state;
    }
  },
  { count: 0 }
);
```

**参考答案**：

```typescript
interface Listener<S> {
  (state: S): void;
}

interface Store<S, A> {
  getState(): S;
  dispatch(action: A): void;
  subscribe(listener: Listener<S>): () => void;
}

type Reducer<S, A> = (state: S, action: A) => S;

function createStore<S, A>(reducer: Reducer<S, A>, initialState: S): Store<S, A> {
  let state = initialState;
  const listeners = new Set<Listener<S>>();
  
  return {
    getState: () => state,
    
    dispatch: (action) => {
      state = reducer(state, action);
      listeners.forEach(listener => listener(state));
    },
    
    subscribe: (listener) => {
      listeners.add(listener);
      return () => listeners.delete(listener);
    }
  };
}
```

#### 进阶版本（更类型安全）

```typescript
type ActionCreator<Type extends string, Payload = void> =
  Payload extends void
    ? { type: Type }
    : { type: Type; payload: Payload };

type ActionMap = {
  inc: { amount: number };
  dec: { amount: number };
  reset: void;
};

type Action = {
  [Type in keyof ActionMap]: ActionCreator<Type, ActionMap[Type]>;
}[keyof ActionMap];
```

#### 评分标准

- 能定义基本的 Store 类型：60分
- 完整的泛型定义：80分
- 类型安全的 Action 设计：100分

---

### 题目16

**题目描述**：请说明 TypeScript 中 `declare` 关键字的作用，什么时候需要使用它。

**参考答案**：

#### declare 关键字概述

`declare` 用于告诉 TypeScript "某个东西存在"，即使它没有在当前代码中定义。

#### 常见使用场景

1. **全局变量声明**
```typescript
// global.d.ts
declare const $: {
  (selector: string): HTMLElement;
  ajax(settings: any): void;
};

// 使用
$('#app').style.color = 'red';
```

2. **模块声明**
```typescript
declare module '*.png' {
  const value: string;
  export default value;
}

declare module '*.css' {
  const classes: { [key: string]: string };
  export default classes;
}
```

3. **全局函数声明**
```typescript
declare function customFunc(x: number): string;
```

4. **全局类型声明**
```typescript
declare namespace MyLib {
  interface Config {
    url: string;
  }
  function init(config: Config): void;
}

MyLib.init({ url: 'http://api.example.com' });
```

#### 类型声明文件 (.d.ts)

- 通常放在 `@types/` 目录下
- 不需要实现，只需要类型定义
- 使用 `/// <reference path="..." />` 引入

#### 评分标准

- 理解声明文件的基本作用：60分
- 能举例 2-3 个场景：80分
- 完整理解各种声明语法：100分

---

## 类型系统原理与工程实践

### 题目17

**题目描述**：请说明 TypeScript 的结构化类型系统（Structural Typing）和名义类型系统（Nominal Typing）的区别。

**参考答案**：

#### 结构化类型 vs 名义类型

| 特性 | TypeScript（结构化） | Java（名义） |
|------|---------------------|-------------|
| 类型比较 | 比较结构/形状 | 比较类型名字 |
| 兼容性 | 结构相同就兼容 | 必须相同类型或继承 |

#### 示例

```typescript
// TypeScript 结构化类型
class Dog { name: string; }
class Cat { name: string; }

const dog: Dog = new Cat();  // ✅ 结构相同，允许！

// 如果是名义类型语言（如 Java）
// 这会报错，即使结构相同
```

#### 模拟名义类型

```typescript
// 用 branded type 模拟名义类型
type Brand<K, T> = K & { __brand: T };

type USD = Brand<number, 'USD'>;
type EUR = Brand<number, 'EUR'>;

const usd = 100 as USD;
const eur = 200 as EUR;

const a: USD = eur;  // ❌ 类型不同
```

#### 评分标准

- 理解基本区别：60分
- 能举例说明：80分
- 知道如何模拟名义类型：100分

---

### 题目18

**题目描述**：请说明 TypeScript 项目的最佳配置策略，以及如何处理类型和代码的分离。

**参考答案**：

#### tsconfig.json 最佳配置

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    
    "moduleResolution": "NodeNext",
    "resolveJsonModule": true,
    
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

#### 项目结构建议

```
project/
├── src/
│   ├── types/        # 类型定义
│   │   ├── index.ts
│   │   └── user.ts
│   ├── utils/        # 工具函数
│   ├── components/   # 组件
│   └── index.ts
├── tests/
├── types/            # 全局类型声明
│   └── global.d.ts
├── tsconfig.json
└── package.json
```

#### 评分标准

- 知道基本的配置项：60分
- 能说明 strict 相关配置：80分
- 完整的项目架构和配置策略：100分

---

### 题目19

**题目描述**：请实现一个类型安全的事件发射器（Event Emitter）。

**代码示例**：
```typescript
// 你的实现
interface EventMap {
  'click': { x: number; y: number };
  'change': { value: string };
}

class Emitter<E extends Record<string, any>> {
  /* ??? */
}

// 使用方式
const emitter = new Emitter<EventMap>();

emitter.on('click', event => {
  console.log(event.x, event.y);  // event 类型正确
});

emitter.emit('click', { x: 10, y: 20 });  // ✅
emitter.emit('change', { value: 'new' }); // ✅
```

**参考答案**：

```typescript
class Emitter<E extends Record<string, any>> {
  private listeners = new Map<keyof E, Set<(data: any) => void>>();
  
  on<K extends keyof E>(event: K, listener: (data: E[K]) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(listener);
  }
  
  off<K extends keyof E>(event: K, listener: (data: E[K]) => void) {
    this.listeners.get(event)?.delete(listener);
  }
  
  emit<K extends keyof E>(event: K, data: E[K]) {
    this.listeners.get(event)?.forEach(listener => listener(data));
  }
}
```

#### 评分标准

- 能理解类型安全需求：60分
- 基本的泛型实现：80分
- 完整的类型安全实现：100分

---

### 题目20

**题目描述**：请说明 TypeScript 中类型体操的常见模式，并举几个实用例子。

**参考答案**：

#### 常见类型体操模式

1. **递归类型**
```typescript
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};
```

2. **模板字面量递归**
```typescript
type Paths<T> = T extends object
  ? { [K in keyof T]: K extends string ? K | `${K}.${Paths<T[K]>}` : never }[keyof T]
  : never;
```

3. **分布条件类型**
```typescript
type Diff<T, U> = T extends U ? never : T;
```

4. **可变元组**
```typescript
type Push<T extends any[], V> = [...T, V];
type Result = Push<[1, 2], 3>;  // [1, 2, 3]
```

5. **模式匹配**
```typescript
type TupleToUnion<T extends any[]> = T extends [infer First, ...infer Rest]
  ? First | TupleToUnion<Rest>
  : never;
```

#### 实用例子

```typescript
// 1. 获取函数返回类型
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

// 2. 去掉属性名前缀
type Unprefixed<T, P> = {
  [K in keyof T as K extends `${P}${infer Rest}` ? Rest : K]: T[K]
};

// 3. 深度 Partial
type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object ? DeepPartial<T[K]> : T[K]
};
```

#### 评分标准

- 知道 2-3 个模式：60分
- 能实现基本的类型体操：80分
- 完整理解并能设计复杂类型：100分

---

## 总结

这份高级面试题主要考察：
1. **类型系统的深入理解** - 从类型定义到类型系统原理
2. **高级类型的运用** - 条件类型、映射类型、模板字面量
3. **类型安全的设计** - 类型守卫、泛型、装饰器
4. **工程化实践** - 类型声明、配置、最佳实践
5. **类型体操的能力** - 灵活运用 TypeScript 强大的类型系统

**答题建议**：
- 先理解题目意图，不要着急写答案
- 结合代码示例说明会更清晰
- 展示不仅会用，还能理解背后的原理
- 可以从简单到复杂，逐步深入
