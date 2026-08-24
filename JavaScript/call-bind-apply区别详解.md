# JavaScript 中 call、bind 和 apply 区别详解


## 目录

- [JavaScript 中 call、bind 和 apply 区别详解](#javascript-中-callbind-和-apply-区别详解)
  - [目录](#目录)
  - [一、概述：this 指向的问题](#一概述this-指向的问题)
    - [1.1 为什么需要 call、bind、apply](#11-为什么需要-callbindapply)
    - [1.2 核心作用](#12-核心作用)
    - [1.3 方法关系图](#13-方法关系图)
  - [二、call 方法详解](#二call-方法详解)
    - [2.1 基本定义与语法](#21-基本定义与语法)
    - [2.2 核心特性](#22-核心特性)
    - [2.3 代码示例](#23-代码示例)
      - [基础用法：改变 this 指向](#基础用法改变-this-指向)
      - [示例：借用其他对象的方法](#示例借用其他对象的方法)
      - [示例：调用父构造函数实现继承](#示例调用父构造函数实现继承)
      - [示例：使用 null/undefined 作为 this](#示例使用-nullundefined-作为-this)
    - [2.4 常见使用场景](#24-常见使用场景)
      - [场景 1：方法借用](#场景-1方法借用)
      - [场景 2：链式调用](#场景-2链式调用)
  - [三、apply 方法详解](#三apply-方法详解)
    - [3.1 基本定义与语法](#31-基本定义与语法)
    - [3.2 核心特性](#32-核心特性)
    - [3.3 代码示例](#33-代码示例)
      - [基础用法：改变 this 指向](#基础用法改变-this-指向-1)
      - [示例：Math 方法扩展](#示例math-方法扩展)
      - [示例：函数柯里化](#示例函数柯里化)
      - [示例：类数组转数组](#示例类数组转数组)
    - [3.4 常见使用场景](#34-常见使用场景)
      - [场景 1：将数组元素作为函数参数传递](#场景-1将数组元素作为函数参数传递)
      - [场景 2：继承实现](#场景-2继承实现)
      - [场景 3：函数节流与防抖](#场景-3函数节流与防抖)
  - [四、bind 方法详解](#四bind-方法详解)
    - [4.1 基本定义与语法](#41-基本定义与语法)
    - [4.2 核心特性](#42-核心特性)
    - [4.3 代码示例](#43-代码示例)
      - [基础用法：创建绑定函数](#基础用法创建绑定函数)
      - [示例：预设参数（函数柯里化）](#示例预设参数函数柯里化)
      - [示例：事件处理中的 this 绑定](#示例事件处理中的-this-绑定)
      - [示例：setTimeout 中的 this 绑定](#示例settimeout-中的-this-绑定)
      - [示例：bind 与 new 的特殊行为](#示例bind-与-new-的特殊行为)
    - [4.4 常见使用场景](#44-常见使用场景)
      - [场景 1：事件处理](#场景-1事件处理)
      - [场景 2：Partial Application（偏函数应用）](#场景-2partial-application偏函数应用)
      - [场景 3：函数引用传递](#场景-3函数引用传递)
  - [五、三种方法核心差异对比](#五三种方法核心差异对比)
    - [5.1 参数传递方式对比](#51-参数传递方式对比)
    - [5.2 执行时机与返回值对比](#52-执行时机与返回值对比)
    - [5.3 综合对比表](#53-综合对比表)
  - [六、手写实现 call、bind、apply](#六手写实现-callbindapply)
    - [6.1 手写 call](#61-手写-call)
    - [6.2 手写 apply](#62-手写-apply)
    - [6.3 手写 bind](#63-手写-bind)
  - [七、适用场景与最佳实践](#七适用场景与最佳实践)
    - [7.1 何时使用 call](#71-何时使用-call)
    - [7.2 何时使用 apply](#72-何时使用-apply)
    - [7.3 何时使用 bind](#73-何时使用-bind)
    - [7.4 性能考量](#74-性能考量)
    - [7.5 常见错误用法](#75-常见错误用法)
      - [错误 1：忘记绑定 this](#错误-1忘记绑定-this)
      - [错误 2：滥用 bind](#错误-2滥用-bind)
      - [错误 3：对箭头函数使用 call/apply/bind](#错误-3对箭头函数使用-callapplybind)
      - [错误 4：apply 传递非数组参数](#错误-4apply-传递非数组参数)
  - [八、面试题精选](#八面试题精选)
    - [题目 1：call、bind、apply 的区别是什么？](#题目-1callbindapply-的区别是什么)
    - [题目 2：如何实现一个函数的 bind？](#题目-2如何实现一个函数的-bind)
    - [题目 3：bind 后的函数使用 new 调用会发生什么？](#题目-3bind-后的函数使用-new-调用会发生什么)
    - [题目 4：如何用 call/apply 实现继承？](#题目-4如何用-callapply-实现继承)
    - [题目 5：箭头函数可以使用 call/apply/bind 吗？](#题目-5箭头函数可以使用-callapplybind-吗)
  - [九、总结速查表](#九总结速查表)
    - [核心差异速查表](#核心差异速查表)
    - [适用场景速查表](#适用场景速查表)
    - [最佳实践清单](#最佳实践清单)
  - [附录：ES6+ 现代替代方案](#附录es6-现代替代方案)

---

## 一、概述：this 指向的问题

### 1.1 为什么需要 call、bind、apply

在 JavaScript 中，`this` 的指向取决于函数的调用方式：

```javascript
// 1. 作为普通函数调用 —— this 指向全局对象（浏览器中为 window）
function sayHello() {
  console.log(this); // window（非严格模式）或 undefined（严格模式）
}
sayHello();

// 2. 作为对象方法调用 —— this 指向调用该方法的对象
const obj = {
  name: 'Alice',
  sayHello() {
    console.log(this.name);
  }
};
obj.sayHello(); // 'Alice'

// 3. 使用 new 调用 —— this 指向新创建的实例对象
function Person(name) {
  this.name = name;
}
const p = new Person('Bob');
console.log(p.name); // 'Bob'

// 问题场景：当我们需要改变 this 指向时
const obj1 = { name: 'Alice' };
const obj2 = { name: 'Bob' };
function greet(greeting) {
  console.log(`${greeting}, ${this.name}!`);
}

// 如何让 greet 中的 this 指向 obj1 或 obj2？
// 答案：使用 call、bind、apply
```

### 1.2 核心作用

`call`、`bind`、`apply` 三个方法的核心作用都是 **改变函数执行时的 `this` 指向**。

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    核心作用图解                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  原函数：                                                               │
│  function greet(greeting) {                                            │
│    console.log(`${greeting}, ${this.name}!`);                           │
│  }                                                                     │
│                                                                         │
│  目标对象：                                                             │
│  const person = { name: 'Alice' };                                     │
│                                                                         │
│  使用 call：                                                            │
│  greet.call(person, 'Hello');  // Hello, Alice!                        │
│                                                                         │
│  使用 apply：                                                           │
│  greet.apply(person, ['Hello']);  // Hello, Alice!                      │
│                                                                         │
│  使用 bind：                                                            │
│  const boundGreet = greet.bind(person, 'Hello');                       │
│  boundGreet();  // Hello, Alice!                                        │
│                                                                         │
│  共同点：都能将 greet 函数中的 this 指向 person 对象                    │
│  不同点：参数传递方式、执行时机、返回值各不相同                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.3 方法关系图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    call、bind、apply 关系图                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Function.prototype                                                     │
│  ├── call(thisArg, arg1, arg2, ...)     ← 立即执行，参数逐个传递      │
│  ├── apply(thisArg, [arg1, arg2, ...])  ← 立即执行，参数数组传递      │
│  └── bind(thisArg, arg1, arg2, ...)     ← 返回新函数，延迟执行        │
│                                                                         │
│  三者关系：                                                             │
│  bind 基于 call 实现                                                    │
│  call 和 apply 功能相同，仅参数传递方式不同                             │
│                                                                         │
│  call vs apply：                                                        │
│  - call 传参：call(obj, arg1, arg2)     ← 逗号分隔                    │
│  - apply 传参：apply(obj, [arg1, arg2]) ← 数组包裹                    │
│                                                                         │
│  call vs bind：                                                         │
│  - call：立即执行函数，返回函数执行结果                                  │
│  - bind：返回新的绑定了 this 的函数，不立即执行                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 二、call 方法详解

### 2.1 基本定义与语法

`Function.prototype.call()` 方法用于在指定的 `this` 上下文中立即调用函数，并以**参数列表**的形式传递参数。

**语法结构：**

```javascript
function.call(thisArg, arg1, arg2, ...)
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `thisArg` | `Object` | 可选。函数执行时要绑定的 `this` 值。如果为 `null` 或 `undefined`，则 `this` 指向全局对象（浏览器中为 `window`，严格模式下为 `undefined`） |
| `arg1, arg2, ...` | 任意类型 | 可选。传递给函数的参数，以逗号分隔 |

**返回值：** 函数的执行结果（即函数体内的 `return` 值）。

### 2.2 核心特性

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    call 核心特性                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ✅ 立即执行函数                                                         │
│  ✅ 以参数列表形式传参（逗号分隔）                                       │
│  ✅ 返回函数执行结果                                                     │
│  ✅ 可以改变 this 指向                                                   │
│  ✅ 支持传递 null/undefined 作为 this                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.3 代码示例

#### 基础用法：改变 this 指向

```javascript
// 示例 1：基本的 this 指向改变
function sayHello(greeting, punctuation) {
  console.log(`${greeting}, ${this.name}${punctuation}`);
}

const user1 = { name: 'Alice' };
const user2 = { name: 'Bob' };

// 使用 call 改变 this 指向
sayHello.call(user1, 'Hello', '!');  // Hello, Alice!
sayHello.call(user2, 'Hi', '.');    // Hi, Bob.
```

#### 示例：借用其他对象的方法

```javascript
// 示例 2：数组方法借用
const arrayLike = {
  length: 3,
  0: 'a',
  1: 'b',
  2: 'c'
};

// 使用 Array.prototype.push 的 call 方法
Array.prototype.push.call(arrayLike, 'd');
console.log(arrayLike); // {0: 'a', 1: 'b', 2: 'c', 3: 'd', length: 4}

// 使用 Array.prototype.slice 将类数组转为真正数组
const realArray = Array.prototype.slice.call(arrayLike);
console.log(realArray); // ['a', 'b', 'c', 'd']
```

#### 示例：调用父构造函数实现继承

```javascript
// 示例 3：构造函数继承
function Parent(name, age) {
  this.name = name;
  this.age = age;
}

Parent.prototype.sayName = function() {
  console.log(`My name is ${this.name}`);
};

function Child(name, age, grade) {
  // 使用 call 调用父构造函数，实现属性继承
  Parent.call(this, name, age);
  this.grade = grade;
}

const child = new Child('Charlie', 12, '六年级');
console.log(child.name);  // 'Charlie'（从 Parent 继承）
console.log(child.age);   // 12（从 Parent 继承）
console.log(child.grade); // '六年级'（Child 自身属性）
```

#### 示例：使用 null/undefined 作为 this

```javascript
// 示例 4：null/undefined 的特殊行为
function showContext() {
  console.log('this:', this);
}

// 非严格模式
showContext.call(null);      // this: window（浏览器）
showContext.call(undefined); // this: window（浏览器）

// 严格模式
'use strict';
showContext.call(null);      // this: null
showContext.call(undefined); // this: undefined
```

### 2.4 常见使用场景

#### 场景 1：方法借用

```javascript
// 将类数组对象转为数组
function toArray() {
  return Array.prototype.slice.call(arguments);
}

const result = toArray(1, 2, 3, 4);
console.log(result); // [1, 2, 3, 4]

// 将 NodeList 转为数组
const nodes = document.querySelectorAll('.item');
const nodeArray = Array.prototype.slice.call(nodes);
// 或使用 Array.from（ES6+）
const nodeArray2 = Array.from(nodes);
```

#### 场景 2：链式调用

```javascript
// 实现类似 jQuery 的链式调用
function Chain(value) {
  this.value = value;
}

Chain.prototype.add = function(n) {
  this.value += n;
  return this; // 返回 this 实现链式调用
};

Chain.prototype.multiply = function(n) {
  this.value *= n;
  return this;
};

Chain.prototype.get = function() {
  return this.value;
};

// 使用 call 在不同上下文间链式调用
const chain = new Chain(5);
const result = chain.add(3).multiply(2).get();
console.log(result); // 16
```

---

## 三、apply 方法详解

### 3.1 基本定义与语法

`Function.prototype.apply()` 方法用于在指定的 `this` 上下文中立即调用函数，并以**数组**的形式传递参数。

**语法结构：**

```javascript
function.apply(thisArg, [argsArray])
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `thisArg` | `Object` | 可选。函数执行时要绑定的 `this` 值。行为与 `call` 相同 |
| `argsArray` | `Array` | 可选。传递给函数的参数数组。如果为 `null` 或 `undefined`，表示不传递参数 |

**返回值：** 函数的执行结果（即函数体内的 `return` 值）。

### 3.2 核心特性

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    apply 核心特性                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ✅ 立即执行函数                                                         │
│  ✅ 以数组形式传参（参数放在数组中）                                     │
│  ✅ 返回函数执行结果                                                     │
│  ✅ 可以改变 this 指向                                                   │
│  ✅ 适合将数组参数传递给函数                                             │
│                                                                         │
│  与 call 的唯一区别：参数传递方式不同                                    │
│  - call：call(obj, arg1, arg2)        ← 参数逐个列出                    │
│  - apply：apply(obj, [arg1, arg2])    ← 参数打包为数组                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.3 代码示例

#### 基础用法：改变 this 指向

```javascript
// 示例 1：基本用法
function greet(greeting, time) {
  console.log(`${greeting}, ${this.name}! It's ${time}.`);
}

const person = { name: 'Alice' };

// 使用 apply，参数以数组形式传递
greet.apply(person, ['Good morning', '10 AM']);
// Good morning, Alice! It's 10 AM.
```

#### 示例：Math 方法扩展

```javascript
// 示例 2：使用 apply 求数组最大/最小值
const numbers = [5, 3, 8, 1, 9, 2];

// 使用 apply 将数组元素作为参数传递给 Math.max
const max = Math.max.apply(null, numbers);
console.log(max); // 9

const min = Math.min.apply(null, numbers);
console.log(min); // 1

// ES6+ 展开运算符方式
const max2 = Math.max(...numbers);
console.log(max2); // 9
```

#### 示例：函数柯里化

```javascript
// 示例 3：使用 apply 实现函数柯里化
function curry(fn) {
  const args = Array.prototype.slice.call(arguments, 1);
  
  return function curried() {
    const newArgs = args.concat(Array.prototype.slice.call(arguments));
    
    if (newArgs.length >= fn.length) {
      return fn.apply(this, newArgs);
    } else {
      return curry.apply(this, [fn].concat(newArgs));
    }
  };
}

// 使用示例
function sum(a, b, c) {
  return a + b + c;
}

const curriedSum = curry(sum);
console.log(curriedSum(1)(2)(3)); // 6
console.log(curriedSum(1, 2)(3)); // 6
console.log(curriedSum(1)(2, 3)); // 6
```

#### 示例：类数组转数组

```javascript
// 示例 4：将类数组对象（如 arguments、NodeList）转为数组
// 在 ES5 中常用的方式
function convertToArray() {
  // 使用 apply + concat 技巧
  return Array.prototype.concat.apply([], arguments);
}

const result = convertToArray(1, 2, 3);
console.log(result); // [1, 2, 3]

// ES6 中推荐使用 Array.from 或展开运算符
function convertToArray2() {
  return Array.from(arguments);
  // 或 return [...arguments];
}
```

### 3.4 常见使用场景

#### 场景 1：将数组元素作为函数参数传递

```javascript
// 当函数接受多个参数，但数据存储在数组中时
function createUser(name, age, role) {
  return { name, age, role };
}

const userData = ['Alice', 25, 'admin'];

// 使用 apply 直接传递数组
const user = createUser.apply(null, userData);
console.log(user); // { name: 'Alice', age: 25, role: 'admin' }

// 对比 call：需要手动展开参数
const user2 = createUser.call(null, ...userData); // ES6+
```

#### 场景 2：继承实现

```javascript
// 与 call 实现继承相同，只是传参方式不同
function Animal(name, type) {
  this.name = name;
  this.type = type;
}

function Dog(name, breed) {
  // 使用 apply 调用父构造函数
  Animal.apply(this, [name, 'mammal']);
  this.breed = breed;
}

const dog = new Dog('Rex', 'Husky');
console.log(dog.name);   // 'Rex'
console.log(dog.type);   // 'mammal'
console.log(dog.breed);  // 'Husky'
```

#### 场景 3：函数节流与防抖

```javascript
// 示例：节流函数实现
function throttle(fn, wait) {
  let lastTime = 0;
  
  return function throttled() {
    const now = Date.now();
    const args = arguments;
    const context = this;
    
    if (now - lastTime >= wait) {
      fn.apply(context, args);
      lastTime = now;
    }
  };
}

// 使用
const throttledScroll = throttle(() => {
  console.log('scroll event');
}, 100);

window.addEventListener('scroll', throttledScroll);
```

---

## 四、bind 方法详解

### 4.1 基本定义与语法

`Function.prototype.bind()` 方法用于创建一个新的绑定了指定 `this` 值的函数，并可以预设部分参数。与 `call` 和 `apply` 不同，`bind` **不会立即执行函数**，而是返回一个新的函数。

**语法结构：**

```javascript
function.bind(thisArg, arg1, arg2, ...)
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `thisArg` | `Object` | 可选。绑定到新函数的 `this` 值。如果为 `null` 或 `undefined`，`this` 将绑定到全局对象 |
| `arg1, arg2, ...` | 任意类型 | 可选。预设的参数，在调用新函数时会作为前置参数传递 |

**返回值：** 一个绑定了 `this` 和预设参数的**新函数**。

### 4.2 核心特性

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    bind 核心特性                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ✅ 返回新函数，不立即执行                                               │
│  ✅ 以参数列表形式预设参数（柯里化）                                     │
│  ✅ 可以改变 this 指向                                                   │
│  ✅ 支持预设参数 + 调用时传参                                           │
│  ✅ 返回的新函数可以作为构造函数使用（new 时 this 不生效）                 │
│  ✅ 绑定一次后不可再次改变 this                                          │
│                                                                         │
│  与 call/apply 的最大区别：bind 是延迟执行                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.3 代码示例

#### 基础用法：创建绑定函数

```javascript
// 示例 1：基本的 this 绑定
const module = {
  x: 42,
  getX: function() {
    return this.x;
  }
};

const unboundGetX = module.getX;
console.log(unboundGetX()); // undefined（this 指向全局对象，没有 x 属性）

const boundGetX = module.getX.bind(module);
console.log(boundGetX()); // 42（this 绑定到 module 对象）
```

#### 示例：预设参数（函数柯里化）

```javascript
// 示例 2：使用 bind 实现函数柯里化
function multiply(a, b, c) {
  return a * b * c;
}

// 预设第一个参数为 2
const multiplyByTwo = multiply.bind(null, 2);
console.log(multiplyByTwo(3, 4)); // 24（2 * 3 * 4）

// 预设前两个参数
const multiplyByTwoAndThree = multiply.bind(null, 2, 3);
console.log(multiplyByTwoAndThree(4)); // 24（2 * 3 * 4）
```

#### 示例：事件处理中的 this 绑定

```javascript
// 示例 3：事件处理中保持 this 指向
class ButtonController {
  constructor(element) {
    this.element = element;
    this.clickCount = 0;
    
    // 使用 bind 绑定 this
    this.handleClick = this.handleClick.bind(this);
    this.element.addEventListener('click', this.handleClick);
  }
  
  handleClick() {
    this.clickCount++;
    console.log(`Button clicked ${this.clickCount} times`);
    // this 正确指向 ButtonController 实例
  }
  
  destroy() {
    this.element.removeEventListener('click', this.handleClick);
  }
}
```

#### 示例：setTimeout 中的 this 绑定

```javascript
// 示例 4：setTimeout 中保持 this 指向
function User() {
  this.name = 'Alice';
  
  // 问题：setTimeout 中的 this 指向全局对象
  setTimeout(function() {
    console.log(this.name); // undefined（this 指向 window）
  }, 100);
  
  // 解决方案 1：使用 bind
  setTimeout(function() {
    console.log(this.name); // 'Alice'（this 绑定到 user 实例）
  }.bind(this), 100);
  
  // 解决方案 2：使用箭头函数（ES6）
  setTimeout(() => {
    console.log(this.name); // 'Alice'（箭头函数继承外层 this）
  }, 100);
}

const user = new User();
```

#### 示例：bind 与 new 的特殊行为

```javascript
// 示例 5：bind 后的函数使用 new 调用时，bind 的 this 不生效
function Animal(type) {
  this.type = type;
}

const boundAnimal = Animal.bind({ type: 'fish' });

// 使用 new 调用时，bind 的 this 被忽略，this 指向新创建的对象
const animal = new boundAnimal('dog');
console.log(animal.type); // 'dog'（不是 'fish'）

// 原因：当使用 new 调用时，函数内部的 this 会被新创建的对象覆盖
// 这是 JavaScript 的规范行为
```

### 4.4 常见使用场景

#### 场景 1：事件处理

```javascript
// React 中的事件绑定（类组件）
class MyComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = { count: 0 };
    
    // 在构造函数中绑定 this
    this.handleClick = this.handleClick.bind(this);
  }
  
  handleClick() {
    this.setState({ count: this.state.count + 1 });
  }
  
  render() {
    return <button onClick={this.handleClick}>Click me</button>;
  }
}

// 更推荐的做法：使用箭头函数（函数式组件或类字段）
class MyComponent2 extends React.Component {
  // 使用类字段语法，箭头函数自动绑定 this
  handleClick = () => {
    this.setState({ count: this.state.count + 1 });
  };
  
  render() {
    return <button onClick={this.handleClick}>Click me</button>;
  }
}
```

#### 场景 2：Partial Application（偏函数应用）

```javascript
// 示例：创建一个只需要传入剩余参数的函数
function formatDate(date, format, locale) {
  // 日期格式化逻辑
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  
  const year = date.getFullYear();
  const month = months[date.getMonth()];
  const day = date.getDate();
  
  if (format === 'short') {
    return `${month} ${day}, ${year}`;
  } else if (format === 'long') {
    return `${month} ${day}, ${year} (${locale})`;
  }
}

// 创建预设格式和地区的函数
const formatShortDate = formatDate.bind(null, null, 'short', 'en-US');
// 只需传入日期
console.log(formatShortDate(new Date())); // 'Aug 4, 2026'

const formatChineseDate = formatDate.bind(null, null, 'long', 'zh-CN');
console.log(formatChineseDate(new Date())); // 'Aug 4, 2026 (zh-CN)'
```

#### 场景 3：函数引用传递

```javascript
// 示例：将方法作为回调传递
const obj = {
  name: 'Test',
  greet: function(greeting) {
    console.log(`${greeting}, ${this.name}`);
  }
};

// 问题：作为回调传递时 this 会丢失
setTimeout(obj.greet, 100); // 'undefined, undefined'（this 指向全局对象）

// 解决方案：使用 bind 保持 this
setTimeout(obj.greet.bind(obj, 'Hello'), 100); // 'Hello, Test'

// 另一个场景：数组方法作为回调
const numbers = [1, 2, 3];
const obj2 = {
  multiplier: 2,
  multiply: function(n) {
    return n * this.multiplier;
  }
};

// 问题：map 的回调中 this 指向全局对象
// const result = numbers.map(obj2.multiply); // NaN

// 解决方案：使用 bind 绑定 this
const result = numbers.map(obj2.multiply.bind(obj2));
console.log(result); // [2, 4, 6]
```

---

## 五、三种方法核心差异对比

### 5.1 参数传递方式对比

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    参数传递方式对比                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  call：以参数列表形式传递（逗号分隔）                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  function fn(a, b, c) { ... }                                  │   │
│  │  fn.call(context, arg1, arg2, arg3)                            │   │
│  │  调用时直接传入多个参数                                         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  apply：以数组形式传递                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  function fn(a, b, c) { ... }                                  │   │
│  │  fn.apply(context, [arg1, arg2, arg3])                         │   │
│  │  将所有参数打包到数组中传入                                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  bind：以参数列表形式预设（逗号分隔）                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  function fn(a, b, c) { ... }                                  │   │
│  │  const boundFn = fn.bind(context, arg1)                        │   │
│  │  boundFn(arg2, arg3)  // 调用时再传入剩余参数                   │   │
│  │  可以预设部分参数，调用时再传入剩余参数                         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  代码对比示例：                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  function sum(a, b, c) {                                        │   │
│  │    return a + b + c;                                             │   │
│  │  }                                                               │   │
│  │                                                                  │   │
│  │  const context = {};                                             │   │
│  │  const args = [1, 2, 3];                                         │   │
│  │                                                                  │   │
│  │  // call：参数逐个传入                                           │   │
│  │  sum.call(context, 1, 2, 3);  // 6                               │   │
│  │                                                                  │   │
│  │  // apply：参数数组传入                                           │   │
│  │  sum.apply(context, args);  // 6                                │   │
│  │                                                                  │   │
│  │  // bind：预设参数 + 调用时传参                                   │   │
│  │  const boundSum = sum.bind(context, 1);  // 预设第一个参数为 1   │   │
│  │  boundSum(2, 3);  // 6（传入剩余两个参数）                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 执行时机与返回值对比

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    执行时机与返回值对比                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  call：立即执行，返回函数执行结果                                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  const result = fn.call(context, arg1, arg2);                   │   │
│  │  // fn 立即执行，result 是 fn 的返回值                          │   │
│  │                                                                  │   │
│  │  const greet = function(name) {                                 │   │
│  │    return `Hello, ${name}!`;                                    │   │
│  │  };                                                              │   │
│  │                                                                  │   │
│  │  const message = greet.call(null, 'Alice');                     │   │
│  │  console.log(message); // 'Hello, Alice!'                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  apply：立即执行，返回函数执行结果                                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  const result = fn.apply(context, [arg1, arg2]);                │   │
│  │  // fn 立即执行，result 是 fn 的返回值                          │   │
│  │                                                                  │   │
│  │  const message = greet.apply(null, ['Bob']);                    │   │
│  │  console.log(message); // 'Hello, Bob!'                         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  bind：延迟执行，返回新函数                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  const boundFn = fn.bind(context, arg1);                        │   │
│  │  // fn 没有执行，boundFn 是一个新函数                           │   │
│  │                                                                  │   │
│  │  const result = boundFn(arg2);  // 调用时才执行                 │   │
│  │  // result 是 fn 的返回值                                        │   │
│  │                                                                  │   │
│  │  const boundGreet = greet.bind(null);                           │   │
│  │  boundGreet('Charlie'); // 'Hello, Charlie!'                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  关键差异：                                                              │
│  - call/apply：立即执行，得到结果                                        │
│  - bind：返回新函数，需要手动调用才能得到结果                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.3 综合对比表

| 对比维度 | call | apply | bind |
|---------|------|-------|------|
| **执行时机** | 立即执行 | 立即执行 | 延迟执行（返回新函数） |
| **参数传递** | 逗号分隔 `fn(ctx, a, b)` | 数组包裹 `fn(ctx, [a, b])` | 逗号分隔 + 预设 `fn.bind(ctx, a)` |
| **返回值** | 函数执行结果 | 函数执行结果 | 绑定了 this 的新函数 |
| **this 绑定** | 临时绑定（一次性） | 临时绑定（一次性） | 永久绑定（不可更改） |
| **传参方式** | 逐个列出 | 数组传递 | 预设部分 + 调用时补全 |
| **适用场景** | 方法借用、继承 | 数组参数传递、继承 | 事件绑定、柯里化 |

---

## 六、手写实现 call、bind、apply

### 6.1 手写 call

```javascript
/**
 * 手写实现 Function.prototype.call
 * @param {Object} context - 要绑定的 this 值
 * @param {...any} args - 传递给函数的参数
 * @returns {any} 函数执行结果
 */
Function.prototype.myCall = function(context, ...args) {
  // 1. 如果 context 为 null/undefined，使用全局对象
  context = context || window;
  
  // 2. 创建唯一的属性名，避免覆盖原有属性
  const fn = Symbol('fn');
  
  // 3. 将函数挂载到 context 上
  context[fn] = this;
  
  // 4. 执行函数，此时 this 指向 context
  const result = context[fn](...args);
  
  // 5. 清理临时属性
  delete context[fn];
  
  // 6. 返回执行结果
  return result;
};

// 测试
function sayHello(greeting) {
  return `${greeting}, ${this.name}!`;
}

const person = { name: 'Alice' };
console.log(sayHello.myCall(person, 'Hi')); // 'Hi, Alice!'
```

### 6.2 手写 apply

```javascript
/**
 * 手写实现 Function.prototype.apply
 * @param {Object} context - 要绑定的 this 值
 * @param {Array} args - 传递给函数的参数数组
 * @returns {any} 函数执行结果
 */
Function.prototype.myApply = function(context, args) {
  // 1. 如果 context 为 null/undefined，使用全局对象
  context = context || window;
  
  // 2. 处理参数：如果 args 不是数组或为 null，则设为空数组
  args = args || [];
  
  // 3. 创建唯一的属性名
  const fn = Symbol('fn');
  
  // 4. 将函数挂载到 context 上
  context[fn] = this;
  
  // 5. 执行函数
  const result = context[fn](...args);
  
  // 6. 清理临时属性
  delete context[fn];
  
  // 7. 返回执行结果
  return result;
};

// 测试
function sum(a, b, c) {
  return a + b + c;
}

console.log(sum.myApply(null, [1, 2, 3])); // 6
```

### 6.3 手写 bind

```javascript
/**
 * 手写实现 Function.prototype.bind
 * @param {Object} context - 要绑定的 this 值
 * @param {...any} presets - 预设的参数
 * @returns {Function} 绑定了 this 和预设参数的新函数
 */
Function.prototype.myBind = function(context, ...presets) {
  // 保存原函数的引用
  const originalFn = this;
  
  // 返回一个新函数
  function boundFunction(...args) {
    // 如果作为构造函数使用（使用 new 调用）
    if (this instanceof boundFunction) {
      // 使用 new.target 检查是否通过 new 调用
      // 如果是构造函数调用，this 应该指向新创建的对象
      return new originalFn(...presets, ...args);
    }
    
    // 否则，使用 context 作为 this
    // 合并预设参数和调用时的参数
    return originalFn.apply(context, [...presets, ...args]);
  }
  
  // 保持原型链：使 boundFunction 的 prototype 指向原函数的 prototype
  boundFunction.prototype = Object.create(originalFn.prototype);
  boundFunction.prototype.constructor = boundFunction;
  
  return boundFunction;
};

// 测试 1：基本绑定
function greet(greeting, name) {
  return `${greeting}, ${name}! I'm ${this.title}`;
}

const obj = { title: 'Mr.' };
const boundGreet = greet.myBind(obj, 'Hello');
console.log(boundGreet('Alice')); // 'Hello, Alice! I'm Mr.'

// 测试 2：作为构造函数
function Person(name) {
  this.name = name;
}
Person.prototype.sayHi = function() {
  return `Hi, I'm ${this.name}`;
};

const BoundPerson = Person.myBind({ name: 'Bound' });
const person = new BoundPerson('Alice');
console.log(person.name); // 'Alice'（new 时忽略 bind 的 this）
console.log(person.sayHi()); // 'Hi, I'm Alice'
```

---

## 七、适用场景与最佳实践

### 7.1 何时使用 call

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    call 适用场景                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. 方法借用                                                            │
│     - 将类数组转为数组：Array.prototype.slice.call(arguments)            │
│     - 调用其他对象的方法                                                 │
│                                                                         │
│  2. 构造函数继承                                                        │
│     - 在子类构造函数中调用父类构造函数：Parent.call(this, ...args)       │
│                                                                         │
│  3. 需要立即执行且参数个数固定                                          │
│     - 参数数量已知，以逗号分隔传递更清晰                                 │
│                                                                         │
│  不适用场景：                                                            │
│  - 参数已经是数组形式（推荐使用 apply）                                  │
│  - 需要延迟执行或多次调用（推荐使用 bind）                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.2 何时使用 apply

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    apply 适用场景                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. 数组参数传递                                                        │
│     - 将数组元素作为参数传递给函数                                       │
│     - Math.max.apply(null, [1, 2, 3, 4])                                │
│                                                                         │
│  2. 可变参数函数                                                        │
│     - 函数接受的参数数量不确定                                           │
│     - 实现函数柯里化或函数组合                                           │
│                                                                         │
│  3. 继承实现                                                            │
│     - Parent.apply(this, argsArray)                                     │
│                                                                         │
│  现代替代方案：                                                          │
│  - 使用展开运算符：Math.max(...[1, 2, 3, 4])                           │
│  - 使用 Array.from() 处理类数组                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.3 何时使用 bind

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    bind 适用场景                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. 事件处理                                                            │
│     - React 类组件中绑定 this                                            │
│     - setTimeout/setInterval 中保持 this                                 │
│                                                                         │
│  2. 回调函数                                                            │
│     - 将方法作为回调传递时保持 this 指向                                  │
│     - array.map(callback.bind(this))                                    │
│                                                                         │
│  3. 函数柯里化 / 偏函数应用                                             │
│     - 预设部分参数，创建专用函数                                         │
│     - const multiplyByTwo = multiply.bind(null, 2)                      │
│                                                                         │
│  4. 需要重复调用的函数                                                  │
│     - 绑定一次，多次调用                                                │
│     - 性能优于每次调用时使用 call/apply                                  │
│                                                                         │
│  注意：                                                                  │
│  - bind 每次调用都会创建新函数，有一定性能开销                           │
│  - 如果只调用一次，call/apply 更合适                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.4 性能考量

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    性能考量                                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. call vs apply：性能基本相同                                          │
│     - 两者底层实现类似，性能差异可以忽略                                 │
│     - 选择主要基于参数传递方式的可读性                                   │
│                                                                         │
│  2. bind 的性能开销                                                     │
│     - bind 会创建新的函数对象，有内存分配开销                            │
│     - 频繁调用时建议使用 call/apply                                      │
│     - 只绑定一次、多次调用时，bind 更高效                                │
│                                                                         │
│  3. 现代 JavaScript 的替代方案                                           │
│     - 使用箭头函数代替 bind（箭头函数自动绑定 this）                     │
│     - 使用展开运算符代替 apply（更简洁）                                 │
│     - 使用 rest 参数代替 arguments（更现代）                            │
│                                                                         │
│  性能优化建议：                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  ❌ 不推荐：循环中频繁使用 bind                                  │   │
│  │  for (let i = 0; i < 10000; i++) {                              │   │
│  │    const boundFn = fn.bind(this);  // 每次循环创建新函数         │   │
│  │    boundFn();                                                    │   │
│  │  }                                                               │   │
│  │                                                                  │   │
│  │  ✅ 推荐：bind 一次，循环中复用                                  │   │
│  │  const boundFn = fn.bind(this);  // 只绑定一次                   │   │
│  │  for (let i = 0; i < 10000; i++) {                              │   │
│  │    boundFn();  // 复用已绑定的函数                               │   │
│  │  }                                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.5 常见错误用法

#### 错误 1：忘记绑定 this

```javascript
// 错误示例
class Counter {
  constructor() {
    this.count = 0;
    // 错误：没有绑定 this，handleClick 中的 this 不是 Counter 实例
    document.getElementById('btn').addEventListener('click', this.handleClick);
  }
  
  handleClick() {
    this.count++; // this 指向按钮元素，不是 Counter 实例
    console.log(this.count); // NaN
  }
}

// 正确示例
class Counter2 {
  constructor() {
    this.count = 0;
    // 正确：使用 bind 绑定 this
    document.getElementById('btn').addEventListener('click', 
      this.handleClick.bind(this));
  }
  
  handleClick() {
    this.count++;
    console.log(this.count); // 正确
  }
}
```

#### 错误 2：滥用 bind

```javascript
// 错误示例：每次渲染都创建新的绑定函数
class MyComponent extends React.Component {
  render() {
    // 错误：每次 render 都创建新函数，导致子组件不必要的重新渲染
    return (
      <ChildComponent onClick={this.handleClick.bind(this)} />
    );
  }
}

// 正确示例：在构造函数中绑定一次
class MyComponent2 extends React.Component {
  constructor(props) {
    super(props);
    // 正确：只绑定一次
    this.handleClick = this.handleClick.bind(this);
  }
  
  handleClick() {
    // ...
  }
  
  render() {
    return (
      <ChildComponent onClick={this.handleClick} />
    );
  }
}

// 更好的方式：使用箭头函数（类字段语法）
class MyComponent3 extends React.Component {
  // 箭头函数自动绑定 this
  handleClick = () => {
    // ...
  };
  
  render() {
    return (
      <ChildComponent onClick={this.handleClick} />
    );
  }
}
```

#### 错误 3：对箭头函数使用 call/apply/bind

```javascript
// 错误示例：箭头函数的 this 是词法绑定的，无法通过 call/apply/bind 改变
const arrowFn = () => {
  console.log(this.name); // this 始终指向定义时的上下文
};

const obj = { name: 'Test' };
arrowFn.call(obj);    // this 不指向 obj
arrowFn.apply(obj);   // this 不指向 obj
arrowFn.bind(obj)();  // this 不指向 obj

// 原因：箭头函数没有自己的 this，它会捕获定义时的 this
// call/apply/bind 对箭头函数无效
```

#### 错误 4：apply 传递非数组参数

```javascript
// 错误示例
function sum(a, b, c) {
  return a + b + c;
}

// 错误：apply 的第二个参数必须是数组或类数组对象
// sum.apply(null, 1, 2, 3); // TypeError: CreateListFromArrayLike called on non-object

// 正确
sum.apply(null, [1, 2, 3]); // 6
```

---

## 八、面试题精选

### 题目 1：call、bind、apply 的区别是什么？

**答案要点：**

```
1. 执行时机：
   - call 和 apply 立即执行函数
   - bind 返回新函数，延迟执行

2. 参数传递：
   - call：参数以逗号分隔（逐个传递）
   - apply：参数以数组形式传递
   - bind：可以预设部分参数，调用时再传递剩余参数

3. 返回值：
   - call 和 apply 返回函数执行结果
   - bind 返回绑定了 this 的新函数

4. this 绑定：
   - call 和 apply 是一次性绑定
   - bind 是永久绑定，不可更改

5. 使用场景：
   - call：方法借用、继承
   - apply：数组参数传递、可变参数函数
   - bind：事件绑定、函数柯里化
```

### 题目 2：如何实现一个函数的 bind？

**答案要点：**

```javascript
Function.prototype.myBind = function(context, ...presets) {
  const originalFn = this;
  
  function boundFunction(...args) {
    // 如果通过 new 调用，忽略 context
    if (this instanceof boundFunction) {
      return new originalFn(...presets, ...args);
    }
    // 否则使用 context 作为 this
    return originalFn.apply(context, [...presets, ...args]);
  }
  
  // 保持原型链
  boundFunction.prototype = Object.create(originalFn.prototype);
  
  return boundFunction;
};
```

### 题目 3：bind 后的函数使用 new 调用会发生什么？

**答案要点：**

```javascript
function Person(name) {
  this.name = name;
}

const BoundPerson = Person.bind({ name: 'Bound' });

// 使用 new 调用时
const person = new BoundPerson('Alice');

// 结果：person.name === 'Alice'（不是 'Bound'）
// 原因：当使用 new 调用时，JavaScript 会创建一个新对象作为 this
// 这个新对象会覆盖 bind 时绑定的 this

// 这是 JavaScript 规范中明确规定的行为：
// 如果一个绑定函数被用作构造函数（使用 new 调用）
// 那么 bind 时指定的 this 会被忽略
// this 会指向新创建的实例对象
```

### 题目 4：如何用 call/apply 实现继承？

**答案要点：**

```javascript
// 使用 call 实现继承
function Parent(name, age) {
  this.name = name;
  this.age = age;
}

Parent.prototype.sayHello = function() {
  console.log(`Hello, I'm ${this.name}`);
};

function Child(name, age, grade) {
  // 使用 call 调用父构造函数，继承属性
  Parent.call(this, name, age);
  this.grade = grade;
}

// 使用 Object.create 继承原型方法
Child.prototype = Object.create(Parent.prototype);
Child.prototype.constructor = Child;

// 测试
const child = new Child('Alice', 10, '四年级');
child.sayHello(); // 'Hello, I'm Alice'
console.log(child.grade); // '四年级'
```

### 题目 5：箭头函数可以使用 call/apply/bind 吗？

**答案要点：**

```javascript
// 箭头函数的 this 是词法绑定的，无法通过 call/apply/bind 改变
const arrowFn = () => {
  console.log(this); // this 始终指向定义时的上下文
};

const obj = { name: 'Test' };

// call/apply/bind 对箭头函数的 this 无效
arrowFn.call(obj);    // this 不指向 obj
arrowFn.apply(obj);   // this 不指向 obj
arrowFn.bind(obj)();  // this 不指向 obj

// 但是箭头函数仍然可以被调用
// 如果箭头函数没有使用 this，call/apply/bind 不会报错
const arrowFn2 = (a, b) => a + b;
console.log(arrowFn2.call(null, 1, 2)); // 3（可以正常传参）

// 总结：
// - 箭头函数的 this 无法被改变
// - 但仍然可以使用 call/apply/bind 传递参数
// - 如果需要改变 this，必须使用普通函数
```

---

## 九、总结速查表

### 核心差异速查表

| 对比项 | call | apply | bind |
|-------|------|-------|------|
| **执行方式** | 立即执行 | 立即执行 | 返回新函数 |
| **参数格式** | `(ctx, a, b, c)` | `(ctx, [a, b, c])` | `(ctx, a)` + 调用时补全 |
| **返回值** | 函数结果 | 函数结果 | 新函数 |
| **this 绑定** | 一次性 | 一次性 | 永久 |
| **性能** | 与 apply 相当 | 与 call 相当 | 创建新函数，略慢 |

### 适用场景速查表

| 场景 | 推荐方法 | 原因 |
|------|---------|------|
| 已知固定参数数量 | `call` | 传参更直观 |
| 参数是数组形式 | `apply` | 无需展开数组 |
| 需要延迟执行 | `bind` | 返回新函数 |
| 事件处理回调 | `bind` | 保持 this 指向 |
| 函数柯里化 | `bind` | 预设参数 |
| 立即调用一次 | `call` / `apply` | 无需创建新函数 |
| 方法借用 | `call` | 传递参数方便 |
| 数组参数传递 | `apply` | 直接传入数组 |

### 最佳实践清单

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    最佳实践清单                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ✅ 推荐做法：                                                           │
│  □ 优先使用箭头函数（自动绑定 this）                                   │
│  □ 使用展开运算符（...）代替 apply 传递数组参数                        │
│  □ 在构造函数中绑定一次 bind，避免重复创建新函数                       │
│  □ 明确知道何时需要改变 this 指向                                      │
│  □ 使用注释说明 call/apply/bind 的用途                                 │
│                                                                         │
│  ❌ 避免做法：                                                           │
│  □ 对箭头函数使用 call/apply/bind（无效）                               │
│  □ 在循环或频繁调用的地方使用 bind                                      │
│  □ 忘记绑定事件处理函数的 this                                         │
│  □ 混淆 call 和 apply 的参数格式                                       │
│  □ 滥用 this 改变，优先考虑更清晰的代码组织方式                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 附录：ES6+ 现代替代方案

| 传统写法 | ES6+ 替代方案 | 说明 |
|---------|-------------|------|
| `fn.call(ctx, a, b)` | `fn.call(ctx, a, b)` | call 仍然常用 |
| `fn.apply(ctx, [a, b])` | `fn.call(ctx, ...[a, b])` | 展开运算符更简洁 |
| `fn.bind(ctx)` + 调用 | 箭头函数 `() => fn.call(ctx)` | 更现代的写法 |
| `Array.prototype.slice.call(arguments)` | `Array.from(arguments)` | 更语义化 |
| `Math.max.apply(null, arr)` | `Math.max(...arr)` | 更简洁 |
| `fn.apply(this, args)` (继承) | `Reflect.apply(fn, this, args)` | 更安全的 API |

---
