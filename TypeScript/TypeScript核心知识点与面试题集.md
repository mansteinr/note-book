# TypeScript 核心知识点与面试题集

> 本文档系统整理 TypeScript 核心知识点，涵盖基础类型、高级类型、接口与类型别名、泛型、函数重载、类型守卫、装饰器、模块化、编译配置等关键领域。每个知识点穿插高频面试题与详细解析，适合初中高级前端开发者系统学习与面试准备。

---

## 目录

- [一、TypeScript 基础概念](#一typescript-基础概念)
- [二、基础类型与高级类型](#二基础类型与高级类型)
- [三、接口 Interface 与类型别名 Type](#三接口-interface-与类型别名-type)
- [四、泛型 Generics](#四泛型-generics)
- [五、函数重载](#五函数重载)
- [六、类型守卫与类型收窄](#六类型守卫与类型收窄)
- [七、装饰器 Decorators](#七装饰器-decorators)
- [八、模块化与命名空间](#八模块化与命名空间)
- [九、声明文件与 JS 互操作](#九声明文件与-js-互操作)
- [十、编译配置 tsconfig.json](#十编译配置-tsconfigjson)
- [十一、工具类型 Utility Types](#十一工具类型-utility-types)
- [十二、综合面试题](#十二综合面试题)

---

## 一、TypeScript 基础概念

### 1.1 什么是 TypeScript？

TypeScript 是微软开发的 JavaScript 超集，在 JS 基础上添加了**静态类型系统**。TS 代码最终编译为纯 JS 运行。

**核心特性：**

| 特性 | 说明 |
|------|------|
| 静态类型检查 | 编译时发现类型错误，减少运行时 bug |
| 类型推断 | 自动推断变量类型，减少显式标注 |
| 面向对象增强 | class、interface、泛型、装饰器等 |
| 工具链支持 | 编辑器智能提示、重构、导航 |
| 渐进式迁移 | 与 JS 完全兼容，可逐步迁移 |

### 1.2 安装与编译

```bash
# 全局安装
npm install -g typescript

# 编译单个文件
tsc index.ts

# 初始化 tsconfig.json
tsc --init

# 监听模式
tsc --watch
```

---

### 面试题 1：TypeScript 的类型系统与 JavaScript 有何本质区别？

**参考答案：**

| 维度 | JavaScript | TypeScript |
|------|-----------|------------|
| 类型系统 | 动态类型（运行时确定） | 静态类型（编译时确定） |
| 类型检查 | 运行时 | 编译时 |
| 类型声明 | 无 | 显式标注或推断 |
| 错误发现 | 运行时 | 编译时 |
| 编辑器支持 | 基础 | 强大的智能提示与重构 |

**TypeScript 类型系统的核心原理：** 采用**结构化类型**（Structural Typing，又称"鸭子类型"），即两个类型兼容不是看名称，而是看结构是否匹配。

```typescript
interface Point2D {
  x: number;
  y: number;
}
interface Point3D {
  x: number;
  y: number;
  z: number;
}

// 结构化类型：Point3D 兼容 Point2D（因为它有 x 和 y）
const p2d: Point2D = { x: 1, y: 2 };
const p3d: Point3D = { x: 1, y: 2, z: 3 };
const p: Point2D = p3d; // 合法！结构兼容
```

---

## 二、基础类型与高级类型

### 2.1 基础类型

```typescript
// 原始类型
let isDone: boolean = false;
let count: number = 42;
let name: string = 'TypeScript';

// 数组
let list: number[] = [1, 2, 3];
let list2: Array<number> = [1, 2, 3];

// 元组（Tuple）
let tuple: [string, number] = ['hello', 10];

// 枚举（Enum）
enum Color { Red, Green, Blue }        // 默认 0, 1, 2
enum Status { Active = 1, Inactive = 2 }
enum Direction { Up = 'UP', Down = 'DOWN' } // 字符串枚举

// 特殊类型
let u: undefined = undefined;
let n: null = null;
let obj: object = {};

// void：函数无返回值
function warn(): void {
  console.log('Warning');
}

// never：永不存在的值
function error(msg: string): never {
  throw new Error(msg);
}
function infiniteLoop(): never {
  while (true) {}
}
```

### 2.2 any、unknown、never 对比

| 类型 | 含义 | 类型安全 | 使用场景 |
|------|------|----------|----------|
| `any` | 任意类型，跳过检查 | 无 | 迁移 JS、快速原型 |
| `unknown` | 未知类型，需收窄 | 安全 | 不确定类型但需安全检查 |
| `never` | 永不存在值的类型 | 最严格 | 抛错函数、穷举检查 |

```typescript
// unknown 需要类型收窄后才能使用
let value: unknown = 'hello';
// value.toUpperCase(); // ❌ 报错
if (typeof value === 'string') {
  value.toUpperCase(); // ✅ 安全
}

// never 的穷举检查
type Shape = 'circle' | 'square';
function getArea(shape: Shape) {
  switch (shape) {
    case 'circle': return Math.PI;
    case 'square': return 1;
    default:
      const _exhaustive: never = shape; // 如果遗漏分支，编译报错
      return _exhaustive;
  }
}
```

### 2.3 联合类型与交叉类型

```typescript
// 联合类型（Union）：A 或 B
type ID = string | number;
function printId(id: ID) {
  if (typeof id === 'string') {
    console.log(id.toUpperCase());
  } else {
    console.log(id.toFixed(2));
  }
}

// 交叉类型（Intersection）：A 且 B
interface Nameable { name: string; }
interface Ageable { age: number; }
type Person = Nameable & Ageable;
const p: Person = { name: 'Tom', age: 20 };
```

### 2.4 字面量类型

```typescript
// 字符串字面量类型
type Direction = 'left' | 'right' | 'up' | 'down';
function move(dir: Direction) { }

// 数值字面量类型
type Dice = 1 | 2 | 3 | 4 | 5 | 6;

// 模板字面量类型（TS 4.1+）
type EventName = `on${Capitalize<string>}`;  // 'onClick' | 'onChange' | ...
type Color = 'red' | 'blue';
type Size = 'sm' | 'lg';
type Variant = `${Color}-${Size}`; // 'red-sm' | 'red-lg' | 'blue-sm' | 'blue-lg'
```

---

### 面试题 2：`any`、`unknown`、`never` 有什么区别？各自适用场景是什么？

**参考答案：**

- **`any`**：完全放弃类型检查，可以调用任意方法、赋值给任意类型。适用场景：快速迁移 JS 项目、第三方库无类型定义时。**不推荐在生产代码中滥用。**
- **`unknown`**：安全的"任意类型"，不能直接操作，必须先通过类型守卫收窄。适用场景：API 返回值、JSON.parse 结果等不确定类型。
- **`never`**：表示永远不会发生的类型。适用场景：抛出错误的函数、无限循环、switch 穷举检查。

```typescript
// 实际场景：API 响应处理
async function fetchData(): Promise<unknown> {
  const res = await fetch('/api/data');
  return res.json();
}

const data = await fetchData();
// data 是 unknown，必须先验证
if (typeof data === 'object' && data !== null && 'name' in data) {
  console.log(data.name); // 安全
}
```

---

### 面试题 3：`type` 和 `interface` 有什么区别？什么时候用哪个？

**参考答案：**

| 维度 | `interface` | `type` |
|------|------------|--------|
| 声明合并 | 支持（同名自动合并） | 不支持 |
| 扩展方式 | `extends` | `&`（交叉类型） |
| 实现 | 可被 `class implements` | 可被 `class implements` |
| 原始类型别名 | 不支持 | 支持 `type Name = string` |
| 联合/交叉 | 不支持直接定义 | 支持 `type A = B \| C` |
| 元组 | 可定义但不够灵活 | 更灵活 `type Tuple = [string, number]` |
| 映射类型 | 不支持 | 支持 `type Readonly<T> = ...` |

**选择建议：**

```
使用 interface 的场景：
  - 定义对象的形状（优先使用）
  - 需要声明合并（如扩展第三方库）
  - 定义类的公共 API

使用 type 的场景：
  - 定义联合类型、交叉类型
  - 定义工具类型（映射类型、条件类型）
  - 定义元组、函数签名
  - 原始类型别名
```

```typescript
// interface 声明合并
interface User {
  name: string;
}
interface User {
  age: number;
}
// User 最终为 { name: string; age: number }

// type 不支持合并
type User2 = { name: string };
// type User2 = { age: number }; // ❌ 报错
```

---

## 三、接口 Interface 与类型别名 Type

### 3.1 接口基础

```typescript
// 基本接口
interface Person {
  name: string;
  age: number;
}

// 可选属性
interface Config {
  url: string;
  method?: 'GET' | 'POST';
  timeout?: number;
}

// 只读属性
interface Point {
  readonly x: number;
  readonly y: number;
}
const p: Point = { x: 10, y: 20 };
// p.x = 5; // ❌ 报错

// 索引签名
interface StringMap {
  [key: string]: string;
}
const map: StringMap = { foo: 'bar', baz: 'qux' };

// 函数接口
interface SearchFunc {
  (source: string, subString: string): boolean;
}
const search: SearchFunc = (src, sub) => src.includes(sub);
```

### 3.2 接口继承

```typescript
interface Animal {
  name: string;
}

interface Dog extends Animal {
  breed: string;
  bark(): void;
}

// 多继承
interface Flyable { fly(): void; }
interface Swimmable { swim(): void; }
interface Duck extends Flyable, Swimmable {
  quack(): void;
}
```

### 3.3 `implements` 关键字

```typescript
interface ClockInterface {
  currentTime: Date;
  setTime(d: Date): void;
}

class Clock implements ClockInterface {
  currentTime: Date = new Date();
  setTime(d: Date) {
    this.currentTime = d;
  }
}
```

---

### 面试题 4：什么是索引签名？有哪些使用场景？

**参考答案：**

索引签名（Index Signature）用于描述对象中未知属性名的类型约束。

```typescript
// 字符串索引签名
interface StringDictionary {
  [key: string]: string;
}

// 数字索引签名（通常用于数组）
interface NumberArray {
  [index: number]: number;
}

// 组合使用（注意：数字索引的值类型必须是字符串索引值类型的子类型）
interface Mixed {
  [key: string]: number | string;
  [index: number]: number; // number 是 number | string 的子类型
  name: string;            // 具体属性必须兼容索引签名
}
```

**使用场景：**
- 字典/Map 类型的数据结构
- 动态属性名的对象
- 配置文件类型定义

---

## 四、泛型 Generics

### 4.1 泛型基础

泛型允许在定义函数、接口、类时不指定具体类型，使用时再确定。

```typescript
// 泛型函数
function identity<T>(arg: T): T {
  return arg;
}
identity<string>('hello'); // 显式指定
identity(42);              // 类型推断

// 泛型接口
interface GenericRepository<T> {
  getById(id: number): T;
  getAll(): T[];
  create(item: T): T;
}

// 泛型类
class Stack<T> {
  private items: T[] = [];
  push(item: T) { this.items.push(item); }
  pop(): T | undefined { return this.items.pop(); }
}
```

### 4.2 泛型约束

```typescript
// extends 约束泛型必须具有某些属性
interface Lengthwise {
  length: number;
}

function logLength<T extends Lengthwise>(arg: T): T {
  console.log(arg.length);
  return arg;
}

logLength('hello');     // ✅ string 有 length
logLength([1, 2, 3]);   // ✅ array 有 length
// logLength(123);      // ❌ number 没有 length
```

```typescript
// 使用 keyof 约束泛型参数为对象的键
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
const obj = { name: 'Tom', age: 20 };
getProperty(obj, 'name'); // ✅
// getProperty(obj, 'email'); // ❌ 报错
```

### 4.3 泛型工具类型

| 工具类型 | 作用 | 示例 |
|---------|------|------|
| `Partial<T>` | 所有属性变为可选 | `Partial<{a:1,b:2}>` → `{a?:1,b?:2}` |
| `Required<T>` | 所有属性变为必填 | `Required<{a?:1,b?:2}>` → `{a:1,b:2}` |
| `Readonly<T>` | 所有属性变为只读 | `Readonly<{a:1}>` → `{readonly a:1}` |
| `Pick<T,K>` | 从 T 中选取指定属性 | `Pick<{a,b,c}, 'a'\|'b'>` → `{a,b}` |
| `Omit<T,K>` | 从 T 中排除指定属性 | `Omit<{a,b,c}, 'a'>` → `{b,c}` |
| `Record<K,T>` | 构造键为 K、值为 T 的对象 | `Record<'a'\|'b', number>` → `{a:number,b:number}` |
| `Exclude<T,U>` | 从联合类型 T 中排除 U | `Exclude<'a'\|'b', 'a'>` → `'b'` |
| `Extract<T,U>` | 从联合类型 T 中提取 U | `Extract<'a'\|'b', 'a'>` → `'a'` |
| `NonNullable<T>` | 从 T 中排除 null/undefined | `NonNullable<string\|null>` → `string` |
| `ReturnType<T>` | 获取函数返回值类型 | `ReturnType<()=>string>` → `string` |
| `Parameters<T>` | 获取函数参数类型 | `Parameters<(a:number)=>void>` → `[number]` |
| `Awaited<T>` | 获取 Promise 返回值类型 | `Awaited<Promise<string>>` → `string` |

```typescript
// 实际应用
interface User {
  id: number;
  name: string;
  email: string;
  password: string;
}

// 更新用户时，id 必填，其余可选
type UpdateUser = Pick<User, 'id'> & Partial<Omit<User, 'id'>>;

// 不包含敏感信息的公开用户
type PublicUser = Omit<User, 'password'>;

// API 响应包装
type ApiResponse<T> = {
  code: number;
  data: T;
  message: string;
};
type UserResponse = ApiResponse<User>;
```

---

### 面试题 5：如何实现一个 `DeepPartial<T>` 类型？

**参考答案：**

```typescript
type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object
    ? T[K] extends Function
      ? T[K]
      : DeepPartial<T[K]>
    : T[K];
};

// 使用示例
interface Config {
  server: {
    host: string;
    port: number;
    ssl: {
      enabled: boolean;
      cert: string;
    };
  };
  database: {
    url: string;
  };
}

type PartialConfig = DeepPartial<Config>;
// 所有层级属性都变为可选
```

---

### 面试题 6：`Record<K, T>` 的实现原理是什么？有哪些使用场景？

**参考答案：**

```typescript
// Record 的实现
type Record<K extends keyof any, T> = {
  [P in K]: T;
};
```

**使用场景：**

```typescript
// 1. 字典映射
type PageNames = 'home' | 'about' | 'contact';
type PageInfo = Record<PageNames, { title: string; url: string }>;

// 2. 枚举值映射
type StatusCode = 200 | 404 | 500;
type StatusMessage = Record<StatusCode, string>;

// 3. 创建键值约束
type Cache = Record<string, { data: unknown; timestamp: number }>;
```

---

## 五、函数重载

### 5.1 函数重载基础

TypeScript 的函数重载通过**多个函数签名 + 一个实现签名**实现。

```typescript
// 重载签名（多个）
function add(a: number, b: number): number;
function add(a: string, b: string): string;
function add(a: number, b: string): string;
function add(a: string, b: number): string;

// 实现签名（一个，兼容所有重载）
function add(a: number | string, b: number | string): number | string {
  if (typeof a === 'number' && typeof b === 'number') {
    return a + b;
  }
  return String(a) + String(b);
}

add(1, 2);     // 返回 number
add('a', 'b'); // 返回 string
add(1, 'b');   // 返回 string
```

### 5.2 重载的实际应用

```typescript
// 根据参数类型返回不同的结果
function getData(id: number): User;
function getData(ids: number[]): User[];
function getData(idOrIds: number | number[]): User | User[] {
  if (Array.isArray(idOrIds)) {
    return idOrIds.map(id => db.findById(id));
  }
  return db.findById(idOrIds);
}

// 根据参数数量返回不同结果
function createElement(tag: 'input'): HTMLInputElement;
function createElement(tag: 'img'): HTMLImageElement;
function createElement(tag: string): HTMLElement {
  return document.createElement(tag);
}
```

---

### 面试题 7：函数重载的实现签名为什么不能被外部调用？

**参考答案：**

TypeScript 的函数重载中，**实现签名**对外部是不可见的，只有**重载签名**对外暴露。这是 TypeScript 的设计选择——实现签名被视为"内部实现细节"。

```typescript
// 重载签名
function greet(name: string): string;
function greet(age: number): string;
// 实现签名
function greet(value: string | number): string {
  return `Hello, ${value}`;
}

greet('Tom');  // ✅ 走第一个重载
greet(20);     // ✅ 走第二个重载
// greet(true);  // ❌ 没有匹配的重载，即使实现签名理论上兼容
```

**设计原因：** 实现签名的类型通常比较宽泛（为了兼容所有重载），如果允许外部直接调用，会失去类型检查的精确性。

---

## 六、类型守卫与类型收窄

### 6.1 类型守卫基础

类型守卫（Type Guard）是在运行时检查类型的表达式，帮助 TypeScript 在特定作用域内收窄类型。

```typescript
// 1. typeof 类型守卫
function process(value: string | number) {
  if (typeof value === 'string') {
    return value.toUpperCase(); // value 被收窄为 string
  }
  return value.toFixed(2);      // value 被收窄为 number
}

// 2. instanceof 类型守卫
class Dog { bark() {} }
class Cat { meow() {} }
function handleAnimal(animal: Dog | Cat) {
  if (animal instanceof Dog) {
    animal.bark(); // animal 被收窄为 Dog
  } else {
    animal.meow(); // animal 被收窄为 Cat
  }
}

// 3. in 操作符类型守卫
interface Fish { swim(): void; }
interface Bird { fly(): void; }
function move(animal: Fish | Bird) {
  if ('swim' in animal) {
    animal.swim(); // animal 被收窄为 Fish
  } else {
    animal.fly();  // animal 被收窄为 Bird
  }
}
```

### 6.2 自定义类型守卫

```typescript
// 使用 `参数 is 类型` 语法
interface Cat {
  meow(): void;
  name: string;
}
interface Dog {
  bark(): void;
  breed: string;
}

function isCat(animal: Cat | Dog): animal is Cat {
  return (animal as Cat).meow !== undefined;
}

function handle(animal: Cat | Dog) {
  if (isCat(animal)) {
    animal.meow();  // animal 被收窄为 Cat
  } else {
    animal.bark();  // animal 被收窄为 Dog
  }
}
```

### 6.3 断言函数（TS 3.7+）

```typescript
// asserts 关键字：断言某个条件为真
function assert(condition: unknown, message?: string): asserts condition {
  if (!condition) throw new Error(message);
}

function getValue(key: string): string | undefined {
  return ({} as any)[key];
}

const val = getValue('name');
assert(val !== undefined, 'value must exist');
val.toUpperCase(); // val 被收窄为 string
```

### 6.4 可辨识联合类型（Discriminated Union）

```typescript
// 通过公共字面量属性区分类型
interface Square {
  kind: 'square';
  size: number;
}
interface Circle {
  kind: 'circle';
  radius: number;
}
interface Triangle {
  kind: 'triangle';
  base: number;
  height: number;
}

type Shape = Square | Circle | Triangle;

function getArea(shape: Shape): number {
  switch (shape.kind) {
    case 'square':
      return shape.size * shape.size;    // shape 被收窄为 Square
    case 'circle':
      return Math.PI * shape.radius ** 2; // shape 被收窄为 Circle
    case 'triangle':
      return (shape.base * shape.height) / 2; // shape 被收窄为 Triangle
    default:
      const _exhaustive: never = shape; // 穷举检查
      return _exhaustive;
  }
}
```

---

### 面试题 8：`typeof`、`instanceof`、`in` 三种类型守卫的区别和适用场景？

**参考答案：**

| 类型守卫 | 检查方式 | 适用场景 |
|---------|---------|---------|
| `typeof` | 检查 JS 原始类型 | 区分 `string`、`number`、`boolean`、`symbol`、`undefined`、`object`、`function` |
| `instanceof` | 检查原型链 | 区分不同的类实例 |
| `in` | 检查属性是否存在 | 区分不同形状的接口/对象 |
| 自定义守卫 | 自定义逻辑 + `is` 关键字 | 复杂的类型判断逻辑 |

```typescript
// typeof 的局限性
typeof null === 'object';  // JS 历史遗留问题，不能用 typeof 区分 null
typeof [] === 'object';    // 不能区分数组和对象

// instanceof 的局限性
// 只能用于类，不能用于接口（接口在运行时不存在）

// in 的适用场景
// 适合区分没有公共类/接口关系的对象类型
```

---

## 七、装饰器 Decorators

### 7.1 装饰器基础

装饰器是一种特殊声明，可附加到类、方法、属性、参数上。需要在 `tsconfig.json` 中启用 `experimentalDecorators: true`。

```typescript
// 类装饰器
function sealed(constructor: Function) {
  Object.seal(constructor);
  Object.seal(constructor.prototype);
}

@sealed
class Greeter {
  greeting: string;
  constructor(message: string) {
    this.greeting = message;
  }
}

// 方法装饰器
function log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const original = descriptor.value;
  descriptor.value = function(...args: any[]) {
    console.log(`Calling ${propertyKey} with`, args);
    return original.apply(this, args);
  };
  return descriptor;
}

class Calculator {
  @log
  add(a: number, b: number): number {
    return a + b;
  }
}
```

### 7.2 装饰器工厂

```typescript
// 装饰器工厂：返回装饰器函数的函数
function route(path: string) {
  return function(target: any, propertyKey?: string, descriptor?: PropertyDescriptor) {
    Reflect.defineMetadata('path', path, target, propertyKey);
  };
}

class UserController {
  @route('/users')
  getUsers() {}

  @route('/users/:id')
  getUserById() {}
}
```

### 7.3 属性装饰器与参数装饰器

```typescript
// 属性装饰器
function required(target: any, propertyKey: string) {
  const existing = Reflect.getMetadata('required', target) || [];
  Reflect.defineMetadata('required', [...existing, propertyKey], target);
}

// 参数装饰器
function validate(target: any, propertyKey: string, parameterIndex: number) {
  const existing = Reflect.getMetadata('validate', target, propertyKey) || [];
  Reflect.defineMetadata('validate', [...existing, parameterIndex], target, propertyKey);
}

class User {
  @required
  name: string;

  @required
  email: string;

  save(@validate id: number) {
    // ...
  }
}
```

---

### 面试题 9：装饰器的执行顺序是怎样的？

**参考答案：**

装饰器的执行顺序遵循**从下到上、从内到外**的原则：

1. **参数装饰器** → **方法装饰器** → **属性装饰器** → **类装饰器**
2. 同一类型的装饰器：**从下到上**执行（离被装饰目标越近越先执行）
3. 多个装饰器应用于同一目标时，**表达式从上到下求值，装饰器从下到上执行**

```typescript
function first() {
  console.log('first(): evaluated');
  return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    console.log('first(): called');
  };
}
function second() {
  console.log('second(): evaluated');
  return function(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    console.log('second(): called');
  };
}

class Example {
  @first()
  @second()
  method() {}
}

// 输出：
// first(): evaluated
// second(): evaluated
// second(): called
// first(): called
```

---

## 八、模块化与命名空间

### 8.1 ES Module 与 TypeScript

```typescript
// 导出
export interface User {
  name: string;
  age: number;
}
export function createUser(name: string): User {
  return { name, age: 0 };
}
export default class UserService {
  // ...
}

// 导入
import UserService, { User, createUser } from './user';
import type { User } from './user'; // 仅导入类型（编译后消除）
import * as UserModule from './user';
```

### 8.2 命名空间（Namespace）

命名空间是 TypeScript 早期的模块化方案，适用于将相关代码组织在一起。

```typescript
namespace Validation {
  export interface StringValidator {
    isValid(s: string): boolean;
  }
  export class EmailValidator implements StringValidator {
    isValid(s: string): boolean {
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s);
    }
  }
}

// 使用
const validator = new Validation.EmailValidator();
validator.isValid('test@example.com');

// 嵌套命名空间
namespace App.Models {
  export class User { }
  export class Order { }
}

// 命名空间别名
import UserModel = App.Models.User;
```

---

### 面试题 10：TypeScript 中 `namespace` 和 `module` 有什么区别？现代项目中如何选择？

**参考答案：**

| 维度 | `namespace`（内部模块） | `module`（外部模块） |
|------|------------------------|---------------------|
| 组织方式 | 代码内部分组 | 文件级别模块 |
| 作用域 | 命名空间内 | 文件作用域 |
| 导入导出 | `/// <reference>` 或 `import` | `import`/`export` |
| 编译输出 | 合并到同一文件或 IIFE | 保持模块分离 |
| 使用场景 | 旧项目、声明文件 | **现代项目标准** |

**选择建议：** 现代 TypeScript 项目应使用 **ES Module**（`import`/`export`）。`namespace` 主要用于：
- 声明文件（`.d.ts`）中组织全局类型
- 遗留代码维护
- 需要将多文件编译为单文件输出时

```typescript
// 声明文件中使用 namespace 组织全局类型（推荐用法）
declare namespace MyLib {
  interface Options {
    debug: boolean;
  }
  function init(options: Options): void;
}
```

---

## 九、声明文件与 JS 互操作

### 9.1 声明文件（.d.ts）

声明文件为 JavaScript 库提供类型信息，让 TypeScript 能够理解 JS 代码的类型。

```typescript
// global.d.ts
declare var API_BASE_URL: string;
declare function getConfig(key: string): string | undefined;

// 声明模块
declare module '*.css' {
  const content: Record<string, string>;
  export default content;
}

declare module '*.png' {
  const src: string;
  export default src;
}

// 扩展全局类型
declare global {
  interface Window {
    myCustomProp: string;
  }
}

// 扩展已有模块
declare module 'express' {
  interface Request {
    user?: { id: number; name: string };
  }
}
```

### 9.2 与 JS 互操作

```typescript
// 使用 JSDoc 注释为 JS 文件添加类型（TS 可识别）
/**
 * @param {string} name
 * @param {number} age
 * @returns {{ name: string, age: number }}
 */
function createUser(name, age) {
  return { name, age };
}

// tsconfig 中启用 allowJs 和 checkJs
// { "allowJs": true, "checkJs": true }
```

### 9.3 常用声明文件模板

```typescript
// 为第三方库编写声明文件
// types/my-library/index.d.ts
declare module 'my-library' {
  export interface Options {
    timeout?: number;
    retry?: boolean;
  }
  export function init(options: Options): void;
  export function fetch(url: string): Promise<unknown>;
  export default function main(): void;
}
```

---

### 面试题 11：`declare` 关键字有哪些使用场景？

**参考答案：**

`declare` 关键字用于告诉 TypeScript 编译器「这个变量/函数/类已经存在，不需要再编译输出」。主要用于**声明文件（.d.ts）**中。

**使用场景：**

```typescript
// 1. 声明全局变量
declare var jQuery: (selector: string) => any;

// 2. 声明全局函数
declare function greet(name: string): void;

// 3. 声明全局类
declare class Animal {
  constructor(name: string);
  name: string;
}

// 4. 声明模块
declare module '*.vue' {
  import { DefineComponent } from 'vue';
  const component: DefineComponent;
  export default component;
}

// 5. 声明命名空间
declare namespace MyApp {
  function init(): void;
  interface Config { }
}

// 6. 模块扩展（Module Augmentation）
declare module 'vue' {
  interface ComponentCustomProperties {
    $http: typeof axios;
  }
}
```

---

## 十、编译配置 tsconfig.json

### 10.1 核心配置项

```json
{
  "compilerOptions": {
    /* 编译目标 */
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],

    /* 输出 */
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": true,
    "declarationDir": "./dist/types",
    "sourceMap": true,

    /* 严格模式 */
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,

    /* 模块解析 */
    "moduleResolution": "node",
    "baseUrl": "./",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"]
    },
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,

    /* JS 支持 */
    "allowJs": true,
    "checkJs": false,

    /* 其他 */
    "jsx": "react-jsx",
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### 10.2 关键配置详解

| 配置项 | 说明 | 推荐值 |
|--------|------|--------|
| `strict` | 启用所有严格检查 | `true` |
| `noImplicitAny` | 禁止隐式 any | `true` |
| `strictNullChecks` | 严格 null 检查 | `true` |
| `target` | 编译目标 ES 版本 | `ES2020` 或更高 |
| `module` | 模块系统 | `ESNext` |
| `moduleResolution` | 模块解析策略 | `node`（Node 项目）/ `bundler`（新项目） |
| `esModuleInterop` | 允许默认导入 CommonJS 模块 | `true` |
| `skipLibCheck` | 跳过声明文件类型检查 | `true`（提升编译速度） |
| `paths` | 路径别名 | 配合 `baseUrl` 使用 |
| `declaration` | 生成 `.d.ts` 声明文件 | 库项目设为 `true` |

---

### 面试题 12：`strict` 模式包含哪些子选项？各自的作用是什么？

**参考答案：**

`strict: true` 等价于同时启用以下 8 个选项：

| 选项 | 作用 |
|------|------|
| `noImplicitAny` | 禁止隐式 `any` 类型 |
| `strictNullChecks` | `null` 和 `undefined` 不能赋值给其他类型 |
| `strictFunctionTypes` | 严格检查函数参数的双向协变 |
| `strictBindCallApply` | 严格检查 `bind`/`call`/`apply` 的参数 |
| `strictPropertyInitialization` | 类属性必须在声明或构造函数中初始化 |
| `noImplicitThis` | 禁止 `this` 隐式 `any` |
| `alwaysStrict` | 编译输出添加 `"use strict"` |
| `useUnknownInCatchVariables` | `catch` 变量默认 `unknown` 而非 `any` |

```typescript
// strictNullChecks 的影响
let name: string;
// name = null; // ❌ strictNullChecks 开启时报错
name = 'hello'; // ✅

// strictPropertyInitialization 的影响
class User {
  // name: string; // ❌ 未初始化报错
  name: string = ''; // ✅
  // 或使用确定赋值断言
  name!: string;
}
```

---

## 十一、工具类型 Utility Types

### 11.1 内置工具类型实现原理

```typescript
// Partial<T>：所有属性可选
type MyPartial<T> = {
  [K in keyof T]?: T[K];
};

// Required<T>：所有属性必填
type MyRequired<T> = {
  [K in keyof T]-?: T[K]; // -? 移除可选修饰符
};

// Readonly<T>：所有属性只读
type MyReadonly<T> = {
  readonly [K in keyof T]: T[K];
};

// Pick<T, K>：选取指定属性
type MyPick<T, K extends keyof T> = {
  [P in K]: T[P];
};

// Omit<T, K>：排除指定属性
type MyOmit<T, K extends keyof any> = Pick<T, Exclude<keyof T, K>>;

// Exclude<T, U>：从联合类型中排除
type MyExclude<T, U> = T extends U ? never : T;

// Extract<T, U>：从联合类型中提取
type MyExtract<T, U> = T extends U ? T : never;

// NonNullable<T>：排除 null 和 undefined
type MyNonNullable<T> = T extends null | undefined ? never : T;

// ReturnType<T>：获取函数返回值类型
type MyReturnType<T extends (...args: any[]) => any> = T extends (...args: any[]) => infer R ? R : never;

// Parameters<T>：获取函数参数类型
type MyParameters<T extends (...args: any[]) => any> = T extends (...args: infer P) => any ? P : never;
```

### 11.2 高级工具类型实战

```typescript
// 深度 Readonly
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object
    ? T[K] extends Function
      ? T[K]
      : DeepReadonly<T[K]>
    : T[K];
};

// 使指定属性可选
type PartialByKeys<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
type PartialAll = PartialByKeys<{ a: number; b: string; c: boolean }, 'a' | 'b'>;
// { a?: number; b?: string; c: boolean }

// 提取函数参数中某个位置的类型
type SecondParam<T extends (...args: any[]) => any> = T extends (first: any, second: infer S, ...rest: any[]) => any ? S : never;

// 将联合类型转换为交叉类型
type UnionToIntersection<U> = (U extends any ? (k: U) => void : never) extends (k: infer I) => void ? I : never;
```

---

### 面试题 13：`infer` 关键字的作用是什么？请举例说明

**参考答案：**

`infer` 关键字用于在条件类型中**推断类型变量**，只能在 `extends` 条件类型的 `true` 分支中使用。

```typescript
// 推断函数返回值类型
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

// 推断数组元素类型
type ArrayElement<T> = T extends (infer E)[] ? E : never;
type El = ArrayElement<string[]>; // string

// 推断 Promise 内部类型
type Unwrap<T> = T extends Promise<infer U> ? U : T;
type Result = Unwrap<Promise<number>>; // number

// 推断函数第一个参数类型
type FirstParam<T> = T extends (first: infer F, ...args: any[]) => any ? F : never;

// 递归推断深层 Promise
type DeepUnwrap<T> = T extends Promise<infer U> ? DeepUnwrap<U> : T;
type Deep = DeepUnwrap<Promise<Promise<Promise<string>>>>; // string
```

**核心理解：** `infer` 让 TypeScript 在类型层面具备了"模式匹配"的能力，可以从复杂类型中提取子类型。

---

## 十二、综合面试题

---

### 面试题 14：什么是协变（Covariance）和逆变（Contravariance）？TypeScript 如何处理？

**参考答案：**

- **协变（Covariance）**：子类型可以赋值给父类型。TypeScript 中**返回值类型是协变的**。
- **逆变（Contravariance）**：父类型可以赋值给子类型。TypeScript 中**函数参数类型是逆变的**（开启 `strictFunctionTypes` 时）。
- **双向协变（Bivariance）**：子类型和父类型可以互相赋值。关闭 `strictFunctionTypes` 时的方法参数。

```typescript
class Animal { name = ''; }
class Dog extends Animal { breed = ''; }

// 协变：返回值
type GetAnimal = () => Animal;
type GetDog = () => Dog;
let getAnimal: GetAnimal = () => new Animal();
let getDog: GetDog = () => new Dog();
getAnimal = getDog; // ✅ 协变：Dog 是 Animal 的子类型

// 逆变：参数（strictFunctionTypes 开启时）
type AnimalHandler = (a: Animal) => void;
type DogHandler = (d: Dog) => void;
let handleAnimal: AnimalHandler = (a: Animal) => {};
let handleDog: DogHandler = (d: Dog) => {};
handleDog = handleAnimal; // ✅ 逆变：Animal 参数可以接受 Dog 参数
// handleAnimal = handleDog; // ❌ 不安全
```

---

### 面试题 15：`keyof`、`typeof`、`in` 在类型层面的用法和区别？

**参考答案：**

```typescript
// 1. keyof：获取对象类型的所有键
interface User {
  name: string;
  age: number;
}
type UserKeys = keyof User; // 'name' | 'age'

// 2. typeof（类型层面）：获取值的类型
const config = {
  host: 'localhost',
  port: 3000,
  ssl: true
};
type Config = typeof config; // { host: string; port: number; ssl: boolean }
type ConfigKeys = keyof typeof config; // 'host' | 'port' | 'ssl'

// 3. in（类型层面）：遍历联合类型
type Nullable<T> = {
  [K in keyof T]: T[K] | null;
};
type NullableUser = Nullable<User>; // { name: string | null; age: number | null }

// 三者结合使用
function getValue<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
```

---

### 面试题 16：如何为已有的第三方库扩展类型声明？

**参考答案：**

使用**模块扩展（Module Augmentation）** 技术：

```typescript
// 扩展 Vue 实例属性
// vue-shims.d.ts
import { AxiosInstance } from 'axios';

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $http: AxiosInstance;
    $translate: (key: string) => string;
  }
}

// 扩展 Express Request
declare module 'express' {
  interface Request {
    user?: {
      id: number;
      role: string;
    };
  }
}

// 扩展全局 Window
declare global {
  interface Window {
    __INITIAL_STATE__: Record<string, unknown>;
    analytics: {
      track: (event: string, data?: unknown) => void;
    };
  }
}
```

---

### 面试题 17：`const` 断言（`as const`）的作用和使用场景？

**参考答案：**

`as const` 是 TypeScript 3.4 引入的常量断言，将值标记为**完全不可变**。

```typescript
// 普通声明
const config1 = { host: 'localhost', port: 3000 };
// 类型：{ host: string; port: number }

// as const 断言
const config2 = { host: 'localhost', port: 3000 } as const;
// 类型：{ readonly host: 'localhost'; readonly port: 3000 }

// 使用场景 1：精确的元组类型
const tuple = [1, 'hello'] as const;
// 类型：readonly [1, 'hello']

// 使用场景 2：枚举替代
const Colors = {
  Red: '#FF0000',
  Green: '#00FF00',
  Blue: '#0000FF'
} as const;
type Color = typeof Colors[keyof typeof Colors]; // '#FF0000' | '#00FF00' | '#0000FF'

// 使用场景 3：提取字面量类型
const routes = ['/', '/about', '/contact'] as const;
type Route = typeof routes[number]; // '/' | '/about' | '/contact'
```

---

### 面试题 18：条件类型中的分布式特性是什么？

**参考答案：**

当条件类型 `T extends U ? X : Y` 中的 `T` 是**裸类型参数（naked type parameter）**且为**联合类型**时，条件类型会**分布式地**应用于联合类型的每个成员。

```typescript
// 分布式条件类型
type ToArray<T> = T extends any ? T[] : never;
type Result = ToArray<string | number>; // string[] | number[]

// 等价于：
// (string extends any ? string[] : never) | (number extends any ? number[] : never)
// = string[] | number[]

// 阻止分布式行为：用方括号包裹 T
type ToArrayNonDist<T> = [T] extends [any] ? T[] : never;
type Result2 = ToArrayNonDist<string | number>; // (string | number)[]
```

**实际应用：**

```typescript
// 内置 Exclude 实现依赖于分布式特性
type MyExclude<T, U> = T extends U ? never : T;
type Excluded = MyExclude<'a' | 'b' | 'c', 'a'>; // 'b' | 'c'
// 分布式展开：
// ('a' extends 'a' ? never : 'a') | ('b' extends 'a' ? never : 'b') | ('c' extends 'a' ? never : 'c')
// = never | 'b' | 'c' = 'b' | 'c'
```

---

### 面试题 19：`satisfies` 关键字（TS 4.9+）的作用和使用场景？

**参考答案：**

`satisfies` 用于**验证表达式类型符合某个类型，同时保留其最精确的类型推断**。

```typescript
// 不使用 satisfies
const palette1: Record<string, string | number[]> = {
  red: '#FF0000',
  green: [0, 255, 0],
};
palette1.red.toUpperCase(); // ❌ 报错：类型是 string | number[]

// 使用 satisfies
const palette2 = {
  red: '#FF0000',
  green: [0, 255, 0],
} satisfies Record<string, string | number[]>;
palette2.red.toUpperCase(); // ✅ 类型推断为 string

// 实际场景：既有类型约束，又保留字面量类型
const routes = {
  home: '/',
  about: '/about',
  contact: '/contact',
} satisfies Record<string, string>;
// routes.home 的类型是 '/'（字面量），不是 string
```

**与 `as` 的区别：** `as` 是强制类型断言（可能不安全），`satisfies` 是类型验证（安全，不会丢失精确类型）。

---

### 面试题 20：如何在 TypeScript 中实现一个类型安全的 EventEmitter？

**参考答案：**

```typescript
// 定义事件映射
interface EventMap {
  userLogin: { userId: number; timestamp: number };
  userLogout: { userId: number };
  error: { code: number; message: string };
}

class TypedEventEmitter<T extends Record<string, any>> {
  private handlers = new Map<keyof T, Set<Function>>();

  on<K extends keyof T>(event: K, handler: (payload: T[K]) => void): void {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set());
    }
    this.handlers.get(event)!.add(handler);
  }

  off<K extends keyof T>(event: K, handler: (payload: T[K]) => void): void {
    this.handlers.get(event)?.delete(handler);
  }

  emit<K extends keyof T>(event: K, payload: T[K]): void {
    this.handlers.get(event)?.forEach(handler => handler(payload));
  }
}

// 使用
const emitter = new TypedEventEmitter<EventMap>();
emitter.on('userLogin', (payload) => {
  // payload 的类型自动推断为 { userId: number; timestamp: number }
  console.log(payload.userId, payload.timestamp);
});
emitter.emit('userLogin', { userId: 1, timestamp: Date.now() });
// emitter.emit('userLogin', { userId: 1 }); // ❌ 缺少 timestamp
```

---

### 面试题 21：`enum` 和 `const enum` 的区别？为什么有些团队不推荐使用 `enum`？

**参考答案：**

| 维度 | `enum` | `const enum` |
|------|--------|-------------|
| 编译输出 | 生成 IIFE 对象 | 内联替换（无运行时代码） |
| 运行时开销 | 有 | 无 |
| 反向映射 | 支持（数字枚举） | 不支持 |
| 调试便利性 | 可调试 | 不可调试（值被内联） |
| 跨文件引用 | 正常 | 需 `preserveConstEnums` |

```typescript
// enum 编译输出
enum Color { Red, Green, Blue }
// → var Color; (function(Color) { ... })(Color || (Color = {}));

// const enum 编译输出
const enum Direction { Up, Down, Left, Right }
const dir = Direction.Up;
// → const dir = 0; （直接内联）
```

**不推荐使用 `enum` 的原因：**
- 编译后产生额外的 JavaScript 代码
- 与 TypeScript 的 `isolatedModules` 模式不兼容（如 Babel、esbuild、swc 等单独编译文件时）
- 字符串枚举更推荐使用 `as const` 联合类型替代

```typescript
// 推荐替代方案
const Direction = { Up: 'UP', Down: 'DOWN', Left: 'LEFT', Right: 'RIGHT' } as const;
type Direction = typeof Direction[keyof typeof Direction];
```

---

### 面试题 22：`never` 类型在实际开发中有哪些高级应用？

**参考答案：**

```typescript
// 1. 穷举检查（Exhaustive Check）
type Shape = 'circle' | 'square' | 'triangle';
function getArea(shape: Shape) {
  switch (shape) {
    case 'circle': return Math.PI;
    case 'square': return 1;
    case 'triangle': return 0.5;
    default:
      const _exhaustive: never = shape; // 新增分支时编译报错
      return _exhaustive;
  }
}

// 2. 禁止意外的属性赋值
type OnlyString<T> = {
  [K in keyof T]: T[K] extends string ? K : never;
}[keyof T];

interface User {
  name: string;
  age: number;
  email: string;
}
type StringKeys = OnlyString<User>; // 'name' | 'email'

// 3. 过滤类型
type FilterNever<T> = {
  [K in keyof T as T[K] extends never ? never : K]: T[K];
};

// 4. 阻止某些联合类型成员
type NoNullOrUndefined<T> = T extends null | undefined ? never : T;

// 5. 交叉类型过滤
type NonNullableKeys<T> = {
  [K in keyof T]-?: T[K] extends null | undefined ? never : K;
}[keyof T];
```

---

### 面试题 23：`abstract` 类与 `interface` 的区别？什么时候用抽象类？

**参考答案：**

| 维度 | `abstract class` | `interface` |
|------|-----------------|-------------|
| 编译输出 | 生成 JS 代码 | 完全擦除 |
| 实例化 | 不能直接 `new` | 不能 `new` |
| 实现 | `extends` | `implements` |
| 包含实现 | 可以包含方法实现 | 不能包含实现 |
| 访问修饰符 | 支持 `public`/`protected`/`private` | 不支持 |
| 构造函数 | 有 | 无 |
| 多继承 | 不支持 | 支持（可 extends 多个） |

**使用抽象类的场景：**
- 需要共享部分实现逻辑
- 需要 `protected` 成员
- 需要构造函数逻辑
- 需要在运行时存在（如 `instanceof` 检查）

```typescript
abstract class BaseRepository<T> {
  protected abstract tableName: string;

  async findById(id: number): Promise<T | null> {
    return db.query(`SELECT * FROM ${this.tableName} WHERE id = ?`, [id]);
  }

  abstract validate(data: T): boolean;
}

class UserRepository extends BaseRepository<User> {
  protected tableName = 'users';
  validate(data: User): boolean {
    return data.name.length > 0;
  }
}
```

---

### 面试题 24：`Awaited<T>` 的实现原理是什么？

**参考答案：**

`Awaited<T>` 是 TypeScript 4.5 引入的工具类型，用于递归获取 Promise 的内部类型。

```typescript
// 简化实现
type MyAwaited<T> = T extends null | undefined
  ? T
  : T extends object & { then(onfulfilled: infer F, ...args: any[]): any }
    ? F extends (value: infer V, ...args: any[]) => any
      ? MyAwaited<V>
      : never
    : T;

// 使用
type A = MyAwaited<Promise<string>>;          // string
type B = MyAwaited<Promise<Promise<number>>>; // number
type C = MyAwaited<string>;                   // string
```

**核心思路：** 递归检查 `T` 是否具有 `then` 方法（即是否为 Thenable），如果是则提取 `onfulfilled` 回调的参数类型并递归展开。

---

### 面试题 25：TypeScript 的类型体操（Type Gymnastics）中，`extends` 关键字有哪些不同的用法？

**参考答案：**

`extends` 在 TypeScript 中有 4 种不同用法：

```typescript
// 1. 接口继承
interface Animal { name: string; }
interface Dog extends Animal { breed: string; }

// 2. 类继承
class Animal {}
class Dog extends Animal {}

// 3. 泛型约束
function logLength<T extends { length: number }>(arg: T) {
  return arg.length;
}

// 4. 条件类型
type IsString<T> = T extends string ? true : false;
type A = IsString<'hello'>; // true
type B = IsString<number>;  // false
```

**条件类型中 `extends` 的几个关键特性：**

```typescript
// 分布式条件类型
type Distribute<T> = T extends any ? T[] : never;
type R = Distribute<string | number>; // string[] | number[]

// never 的特殊处理
type IsNever<T> = [T] extends [never] ? true : false; // 需要用 [] 包裹

// 类型推断
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;
```

---

## 附录：考点速查表

| 知识领域 | 核心考点 | 对应题目 |
|---------|---------|----------|
| TypeScript 基础 | 类型系统、结构化类型、编译原理 | Q1 |
| 基础类型 | any/unknown/never、联合类型、交叉类型、字面量类型 | Q2 |
| 接口与类型别名 | interface vs type、声明合并、索引签名、implements | Q3、Q4 |
| 泛型 | 泛型函数/类/接口、约束、工具类型、infer | Q5、Q6、Q13 |
| 函数重载 | 重载签名与实现签名、实际应用 | Q7 |
| 类型守卫 | typeof/instanceof/in、自定义守卫、可辨识联合 | Q8 |
| 装饰器 | 类/方法/属性/参数装饰器、执行顺序 | Q9 |
| 模块化 | namespace vs module、声明文件、模块扩展 | Q10、Q11、Q16 |
| 编译配置 | tsconfig.json、strict 模式、关键配置项 | Q12 |
| 高级类型 | 协变逆变、条件类型、分布式特性、satisfies | Q14、Q15、Q18、Q19 |
| 实战应用 | EventEmitter、enum 替代、抽象类、Awaited | Q17、Q20、Q21、Q22、Q23、Q24 |
| 类型体操 | extends 多重用法、const 断言、never 应用 | Q25 |

---

> **参考资源：** [TypeScript 官方文档](https://www.typescriptlang.org/docs/) | [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/) | [TypeScript Playground](https://www.typescriptlang.org/play)