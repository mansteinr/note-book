# TypeScript中级工程师面试题集

## 目录

- [基础类型](#基础类型)
- [接口与类型别名](#接口与类型别名)
- [泛型](#泛型)
- [类](#类)
- [模块与导入导出](#模块与导入导出)
- [高级类型](#高级类型)
- [类型推断与类型守卫](#类型推断与类型守卫)

---

## 基础类型

### 题目1

**题目描述**：以下关于 TypeScript 基本类型的说法，正确的是？

A. TypeScript 中 `number` 类型只能表示整数，小数需要用 `float` 类型
B. TypeScript 新增了 `boolean` 类型，JavaScript 中没有
C. `null` 和 `undefined` 是所有类型的子类型，可以赋值给任何类型（strictNullChecks 关闭时）
D. `string` 类型可以包含数字，所以 `"123"` 既可以是 `string` 也可以是 `number`

**正确答案**：C

**详细解析**：

- **A错误**：TypeScript 中 `number` 类型同时表示整数和浮点数，没有单独的 `float` 类型
- **B错误**：JavaScript 中本身就有 `boolean` 类型，不是 TypeScript 新增的
- **C正确**：在 `strictNullChecks: false` 配置下，`null` 和 `undefined` 可以赋值给任何类型
- **D错误**：`"123"` 是字符串类型，不是数字类型，虽然内容看起来像数字

---

### 题目2

**题目描述**：以下关于 TypeScript 数组类型的声明方式，错误的是？

A. `const list: number[] = [1, 2, 3]`
B. `const list: Array<number> = [1, 2, 3]`
C. `const list: (number | string)[] = [1, '2', 3]`
D. `const list: Array<number | string> = [1, 2, 3]` （不可以混合类型）

**正确答案**：D

**详细解析**：

- **A和B**：两种数组类型声明方式都是正确的，等价
- **C**：`(number | string)[]` 表示可以是数字或字符串的数组
- **D错误**：`Array<number | string>` 表示可以混合数字和字符串，所以是可以的

---

### 题目3

**题目描述**：以下代码的输出结果是？

```typescript
let x: number | boolean = true;
x = 100;
console.log(x.toFixed(2));
```

A. `"100.00"`
B. `100.00`
C. 编译时错误：`boolean` 类型没有 `toFixed` 方法
D. 运行时错误

**正确答案**：A

**详细解析**：

虽然 x 可能是 `boolean` 类型，但在最后一行时 x 已经赋值为 `100`（number 类型），所以可以调用 `toFixed` 方法，结果是字符串 `"100.00"`。

---

### 题目4

**题目描述**：TypeScript 中，以下哪种类型定义方式可以精确表示一个函数？

A. `let fn: Function`
B. `let fn: (a: number, b: number) => number`
C. `let fn: (number, number) => number`
D. `let fn: (a, b) => number`

**正确答案**：B

**详细解析**：

- **A**：太宽泛，不精确
- **B正确**：完整的函数类型定义，包括参数名、参数类型、返回值类型
- **C**：缺少参数名（虽然在类型声明中可以省略参数名，但在函数类型定义时最好加上）
- **D**：缺少类型注解，会被推断为 `any`

---

## 接口与类型别名

### 题目5

**题目描述**：关于 `interface` 和 `type` 的区别，以下说法错误的是？

A. `interface` 可以自动合并同名声明，`type` 不可以
B. `type` 可以定义基本类型别名，`interface` 只能定义对象类型
C. `interface` 可以被 `implements`，`type` 不可以
D. 它们完全相同，可以互换使用

**正确答案**：D

**详细解析**：

- **A正确**：`interface` 会自动合并同名声明
- **B正确**：`type` 可以定义像 `type MyString = string` 这样的基本类型别名
- **C正确**：类可以 `implements` 接口，但不能 `implements` type
- **D错误**：它们有区别，不是完全相同

---

### 题目6

**题目描述**：以下 TypeScript 接口的定义，错误的是？

A. `interface A { name: string; age: number }`
B. `interface A { [key: string]: any }`
C. `interface A { name: string; [key: number]: any }`
D. `interface A { (): void }`（函数类型不能用接口）

**正确答案**：D

**详细解析**：

接口完全可以定义函数类型：
```typescript
interface Func {
  (): void
}
const fn: Func = () => console.log('hello')
```

所以 D 是错误的，其他都是正确的接口定义方式。

---

### 题目7

**题目描述**：以下代码的运行结果是？

```typescript
interface Config {
  name: string;
  readonly id: number;
  age?: number;
}

const config: Config = {
  name: 'test',
  id: 100
};
config.id = 200;
config.age = 18;
console.log(config);
```

A. `{ name: 'test', id: 200, age: 18 }`
B. `{ name: 'test', id: 100, age: 18 }`
C. 编译时错误
D. 运行时错误

**正确答案**：C

**详细解析**：

`id` 属性被标记为 `readonly`，只读属性在对象创建后不能修改，所以 `config.id = 200` 会报错。

---

### 题目8

**题目描述**：关于接口的继承，以下代码的正确输出结果是？

```typescript
interface Animal {
  name: string;
}

interface Bird extends Animal {
  fly(): void;
}

const sparrow: Bird = {
  name: 'sparrow',
  fly() { console.log('flying'); }
};
console.log('name' in sparrow);
```

A. `true`
B. `false`
C. 编译错误
D. 运行错误

**正确答案**：A

**详细解析**：

接口继承后，子接口会继承父接口的所有属性，所以 `sparrow` 对象包含 `name` 属性，`'name' in sparrow` 返回 `true`。

---

## 泛型

### 题目9

**题目描述**：以下泛型函数调用方式，错误的是？

```typescript
function identity<T>(arg: T): T {
  return arg;
}
```

A. `identity<string>("hello")`
B. `identity(100)` （类型推断）
C. `identity<number>("100")`
D. `identity<boolean>(true)`

**正确答案**：C

**详细解析**：

泛型类型参数 `<number>` 说明函数期望接收 `number` 类型，但传入 `"100"` 是字符串，会报错。

---

### 题目10

**题目描述**：以下关于泛型约束的代码，正确的是？

A.
```typescript
function fn<T>(arg: T): T {
  console.log(arg.length); // 直接用
  return arg;
}
```

B.
```typescript
interface Lengthwise {
  length: number;
}
function fn<T extends Lengthwise>(arg: T): T {
  console.log(arg.length);
  return arg;
}
```

C.
```typescript
function fn<T extends Array>(arg: T): T {
  console.log(arg.length);
  return arg;
}
```

D.
```typescript
function fn<T>(arg: T): T {
  return arg as any; // 类型断言后再访问
}
```

**正确答案**：B

**详细解析**：

使用泛型约束 `<T extends Lengthwise>`，确保 `arg` 有 `length` 属性，这样在函数中访问 `arg.length` 就是安全的。

---

### 题目11

**题目描述**：以下代码的输出结果是？

```typescript
class MyClass<T> {
  value: T;
  constructor(value: T) {
    this.value = value;
  }
  getValue(): T {
    return this.value;
  }
}

const obj = new MyClass<number>(100);
console.log(typeof obj.getValue());
```

A. `"object"`
B. `"number"`
C. `"string"`
D. 编译错误

**正确答案**：B

**详细解析**：

泛型类被实例化为 `MyClass<number>` 类型，`getValue()` 返回值类型是 `number`，所以 `typeof` 结果是 `"number"`。

---

### 题目12

**题目描述**：以下关于泛型的说法，错误的是？

A. 泛型可以提高代码的复用性
B. 泛型可以在使用时才指定类型
C. 泛型只能用于函数和类，不能用于接口
D. 泛型可以有多个类型参数 `<T, U>`

**正确答案**：C

**详细解析**：

泛型完全可以用于接口：
```typescript
interface Container<T> {
  value: T;
  getValue(): T;
}
```

所以 C 是错误的。

---

## 类

### 题目13

**题目描述**：TypeScript 类中，关于访问修饰符的说法，正确的是？

A. `public` 是默认修饰符，可以省略
B. `private` 成员可以在子类中访问
C. `protected` 成员只能在类内部访问
D. TypeScript 没有访问修饰符，这是 Java 有的

**正确答案**：A

**详细解析**：

- **A正确**：`public` 是默认的，可以省略
- **B错误**：`private` 成员只能在类内部访问，子类不能访问
- **C错误**：`protected` 成员可以在类内部和子类中访问
- **D错误**：TypeScript 有访问修饰符

---

### 题目14

**题目描述**：以下代码的输出结果是？

```typescript
class Parent {
  protected name: string = 'parent';
  constructor() {
    console.log('Parent constructor');
  }
}

class Child extends Parent {
  constructor() {
    super();
    console.log('Child constructor');
    console.log(this.name);
  }
}

new Child();
```

A.
```
Child constructor
parent
Parent constructor
```
B.
```
Parent constructor
Child constructor
parent
```
C.
```
Parent constructor
Child constructor
```
然后报错：`name` 不可访问
D. 编译错误

**正确答案**：B

**详细解析**：

- 子类构造函数必须先调用 `super()`
- `protected` 成员可以在子类中访问
- 所以先输出父类构造，再输出子类构造，最后输出 `parent`

---

### 题目15

**题目描述**：关于 TypeScript 类的 `readonly` 修饰符，以下说法正确的是？

A. 只能在声明时赋值，不能在构造函数中赋值
B. 可以在声明时或构造函数中赋值，但之后不能再修改
C. 和 `const` 完全一样
D. 不能修饰属性，只能修饰变量

**正确答案**：B

**详细解析**：

```typescript
class MyClass {
  readonly value: number;  // 可以声明时赋值
  constructor(v: number) {
    this.value = v;       // 也可以构造函数中赋值
  }
  update() {
    // this.value = 100;  // 编译错误：不能修改
  }
}
```

---

### 题目16

**题目描述**：以下关于抽象类的说法，错误的是？

A. 抽象类不能直接实例化
B. 抽象类必须包含抽象方法
C. 抽象类可以包含非抽象方法
D. 子类必须实现抽象类的抽象方法

**正确答案**：B

**详细解析**：

抽象类**可以**包含抽象方法，也可以不包含，所以 B 是错误的。其他选项都是正确的。

---

## 模块与导入导出

### 题目17

**题目描述**：以下模块导入方式，错误的是？

A. `import * as utils from './utils'`
B. `import { add, sub } from './utils'`
C. `import utils from './utils'`
D. `import './utils'` （只执行模块，不导入任何内容）

**正确答案**：D 是正确的导入方式！所有选项都是正确的。

**详细解析**：

题目问的是错误的导入方式，但实际上 A、B、C、D 都是 TypeScript 支持的合法导入方式。

---

### 题目18

**题目描述**：以下模块导出方式，错误的是？

A.
```typescript
// 导出变量
export const value = 100;
// 导出函数
export function fn() { return 100; }
```

B.
```typescript
export default { value: 100 };
```

C.
```typescript
const a = 100;
export = a;
```

D.
```typescript
export { a as default } from './a';
```

**正确答案**：所有选项都是正确的，没有错误的。

**详细解析**：

TypeScript 支持多种导出方式，包括命名导出、默认导出、`export =` 语法等。

---

### 题目19

**题目描述**：关于模块系统的说法，正确的是？

A. TypeScript 默认用 CommonJS 模块系统
B. 在浏览器中只能用 ES Modules
C. Node.js 只支持 CommonJS，不支持 ES Modules
D. 模块系统不能混用

**正确答案**：A

**详细解析**：

- **A正确**：TypeScript 默认配置 `module: "commonjs"`
- **B错误**：浏览器可以打包工具处理 CommonJS 模块
- **C错误**：Node.js 14+ 完全支持 ES Modules
- **D错误**：可以混用

---

## 高级类型

### 题目20

**题目描述**：以下关于联合类型 `|` 和交叉类型 `&` 的说法，正确的是？

A. `A | B` 表示必须同时拥有 A 和 B 的属性
B. `A & B` 表示可以是 A 或者 B
C. `number | string` 表示可以是数字或字符串
D. `number & string` 类型会有很多值

**正确答案**：C

**详细解析**：

- **A错误**：`A | B` 是联合类型，表示可以是 A 或 B
- **B错误**：`A & B` 是交叉类型，表示同时是 A 和 B
- **C正确**：`number | string` 表示数字或字符串
- **D错误**：`number & string` 没有交集，是 `never` 类型

---

### 题目21

**题目描述**：以下关于字面量类型的代码，输出结果是？

```typescript
type Status = 'pending' | 'success' | 'error';

function handleStatus(s: Status) {
  switch (s) {
    case 'pending': return 'loading';
    case 'success': return 'done';
    case 'error': return 'fail';
    default: {
      // 这行在编译时会报错吗？
      const exhaustiveCheck: never = s;
      return exhaustiveCheck;
    }
  }
}

console.log(handleStatus('success'));
```

A. `done`，编译无错误
B. 编译错误：`s` 是 `Status` 类型，不能赋值给 `never`
C. `fail`
D. 运行时错误

**正确答案**：A

**详细解析**：

这是 TypeScript 的穷举检查技巧。由于所有可能的 Status 都被 case 分支覆盖了，default 分支永远不会执行，所以不会报错。代码输出 `done`。

---

### 题目22

**题目描述**：以下关于类型断言的说法，正确的是？

A. 类型断言会改变数据的实际类型
B. 类型断言可以将 `any` 类型断言为任意类型
C. `as` 语法是类型安全的，一定不会有问题
D. 类型断言只能用 `as` 语法，不能用尖括号

**正确答案**：B

**详细解析**：

- **A错误**：类型断言不会改变实际类型，只是告诉编译器"相信我，我知道这是什么类型"
- **B正确**：`any` 可以被断言为任何类型
- **C错误**：类型断言不是绝对安全的
- **D错误**：尖括号语法 `<T>val` 也是支持的

---

### 题目23

**题目描述**：以下代码的输出结果是？

```typescript
type Person = {
  name: string;
  age: number;
};

const user = {
  name: 'Alice',
  age: 25,
  gender: 'female'
};

const p: Person = user;
console.log('gender' in p);
```

A. `true`
B. `false`
C. 编译错误
D. 运行错误

**正确答案**：A

**详细解析**：

虽然 `p` 的类型定义为 `Person`（没有 `gender` 属性），但实际赋值的对象有这个属性，在运行时 `'gender' in p` 返回 `true`。

---

## 类型推断与类型守卫

### 题目24

**题目描述**：以下关于类型推断的说法，错误的是？

A. TypeScript 可以自动推断变量类型
B. 函数参数如果有默认值，可以推断类型
C. 函数返回值类型一定需要显式声明
D. 可以从上下文推断类型（contextual typing）

**正确答案**：C

**详细解析**：

函数返回值类型可以不声明，TypeScript 会自动推断：
```typescript
function add(a: number, b: number) {
  return a + b;  // 自动推断返回值类型为 number
}
```

---

### 题目25

**题目描述**：以下哪段代码是类型守卫（Type Guard）？

A.
```typescript
function isString(x: any): boolean {
  return typeof x === 'string';
}
```

B.
```typescript
function isString(x: any): x is string {
  return typeof x === 'string';
}
```

C.
```typescript
function isString(x: any) {
  return typeof x === 'string';
}
```

D.
```typescript
type IsString<T> = T extends string ? true : false;
```

**正确答案**：B

**详细解析**：

类型守卫函数的返回值类型是 `x is T` 的形式，这样 TypeScript 会在 `if (isString(x))` 分支中正确地将 x 类型收窄为 `string`。

---

### 题目26

**题目描述**：以下代码中，在 `if` 分支内 x 的类型是？

```typescript
type Dog = { bark: () => void };
type Cat = { meow: () => void };

function makeSound(x: Dog | Cat) {
  if ('bark' in x) {
    // 这里 x 是什么类型？
    x.bark();
  }
}
```

A. `Dog`
B. `Cat`
C. `Dog | Cat`
D. `any`

**正确答案**：A

**详细解析**：

使用 `in` 运算符判断属性存在也是类型守卫的一种方式，在分支内 TypeScript 会正确地将类型收窄。

---

### 题目27

**题目描述**：以下关于 `typeof` 和 `instanceof` 的说法，正确的是？

A. 它们都可以作为类型守卫
B. `typeof` 只能检测基本类型，`instanceof` 可以检测任何类型
C. `instanceof` 在 TypeScript 中无效
D. 它们都是 JavaScript 原生操作，TypeScript 不做特殊处理

**正确答案**：A

**详细解析**：

两者都可以在 TypeScript 中作为类型守卫使用：
```typescript
if (typeof x === 'string') { /* x is string */ }
if (x instanceof Date) { /* x is Date */ }
```

---

## 综合题

### 题目28

**题目描述**：以下代码中，变量 `result` 的类型是什么？

```typescript
function process<T>(val: T): T extends string ? number : boolean {
  return (typeof val === 'string' ? 123 : true) as any;
}

const result = process('hello');
```

A. `string | number | boolean`
B. `number`
C. `boolean`
D. `any`

**正确答案**：B

**详细解析**：

条件类型 `T extends string ? number : boolean` 表示如果 `T` 是 `string` 类型，返回值类型是 `number`，否则是 `boolean`。由于传入 `'hello'`（`string`），所以 `result` 类型是 `number`。

---

### 题目29

**题目描述**：以下 TypeScript 工具类型的说明，错误的是？

A. `Partial<T>`：将 T 的所有属性变为可选
B. `Required<T>`：将 T 的所有属性变为必填
C. `Readonly<T>`：将 T 的所有属性变为只读
D. `Exclude<T, U>`：从 T 中移除可以赋值给 U 的类型

**正确答案**：D

**详细解析**：

`Exclude<T, U>` 是从 T 中**不可以**赋值给 U 的类型，或者说从 T 中排除在 U 中的类型。
`Extract<T, U>` 才是从 T 中提取可以赋值给 U 的类型。

---

### 题目30

**题目描述**：以下代码的运行结果是？

```typescript
enum Status {
  Pending = 'pending',
  Success = 'success'
}

const currentStatus = Status.Success;
console.log(typeof currentStatus);
console.log(currentStatus);
```

A.
```
"string"
"success"
```

B.
```
"number"
"success"
```

C.
```
"object"
"Success"
```

D. 编译错误

**正确答案**：A

**详细解析**：

字符串枚举的成员值是字符串类型，所以 `typeof` 是 `"string"`，值是 `"success"`。

---

## 答案速查

| 题号 | 答案 | 分值（建议） |
|-----|------|------------|
| 1 | C | 3分 |
| 2 | D | 3分 |
| 3 | A | 4分 |
| 4 | B | 3分 |
| 5 | D | 4分 |
| 6 | D | 3分 |
| 7 | C | 4分 |
| 8 | A | 3分 |
| 9 | C | 4分 |
| 10 | B | 4分 |
| 11 | B | 4分 |
| 12 | C | 3分 |
| 13 | A | 3分 |
| 14 | B | 4分 |
| 15 | B | 3分 |
| 16 | B | 4分 |
| 17 | (都正确) | 3分 |
| 18 | (都正确) | 3分 |
| 19 | A | 4分 |
| 20 | C | 4分 |
| 21 | A | 4分 |
| 22 | B | 3分 |
| 23 | A | 4分 |
| 24 | C | 3分 |
| 25 | B | 4分 |
| 26 | A | 4分 |
| 27 | A | 3分 |
| 28 | B | 5分 |
| 29 | D | 4分 |
| 30 | A | 3分 |

**满分100分**，得分建议：
- 90-100分：优秀的中级TypeScript开发者
- 70-89分：良好，基础扎实
- 50-69分：及格，需要加强练习
- 50分以下：需要系统学习TypeScript
