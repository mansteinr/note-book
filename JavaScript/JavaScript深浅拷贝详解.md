# JavaScript 深浅拷贝详解

> 本文档系统介绍 JavaScript 中深浅拷贝的概念、核心差异、实现方法及最佳实践，涵盖基础数据类型与引用数据类型的拷贝表现、多种浅拷贝与深拷贝实现方式、特殊数据类型的处理方案，以及性能对比和常见问题解析。

---

## 目录

- [JavaScript 深浅拷贝详解](#javascript-深浅拷贝详解)
  - [目录](#目录)
  - [一、概述：为什么需要深浅拷贝](#一概述为什么需要深浅拷贝)
    - [1.1 问题场景](#11-问题场景)
    - [1.2 深浅拷贝的作用](#12-深浅拷贝的作用)
  - [二、核心概念与差异](#二核心概念与差异)
    - [2.1 基本数据类型 vs 引用数据类型](#21-基本数据类型-vs-引用数据类型)
    - [2.2 内存存储机制](#22-内存存储机制)
      - [基本数据类型：值存储在栈中](#基本数据类型值存储在栈中)
      - [引用数据类型：值存储在堆中，变量存储引用](#引用数据类型值存储在堆中变量存储引用)
    - [2.3 深浅拷贝定义](#23-深浅拷贝定义)
      - [浅拷贝（Shallow Copy）](#浅拷贝shallow-copy)
      - [深拷贝（Deep Copy）](#深拷贝deep-copy)
    - [2.4 核心差异对比](#24-核心差异对比)
  - [三、浅拷贝实现方式](#三浅拷贝实现方式)
    - [3.1 Object.assign()](#31-objectassign)
      - [基本用法](#基本用法)
      - [浅拷贝特性验证](#浅拷贝特性验证)
      - [源码级分析](#源码级分析)
      - [优缺点](#优缺点)
    - [3.2 扩展运算符](#32-扩展运算符)
      - [基本用法](#基本用法-1)
      - [数组浅拷贝](#数组浅拷贝)
      - [源码级分析](#源码级分析-1)
      - [优缺点](#优缺点-1)
    - [3.3 Array.prototype.slice()](#33-arrayprototypeslice)
      - [基本用法](#基本用法-2)
      - [实现原理](#实现原理)
      - [优缺点](#优缺点-2)
    - [3.4 Array.prototype.concat()](#34-arrayprototypeconcat)
      - [基本用法](#基本用法-3)
      - [优缺点](#优缺点-3)
    - [3.5 Object.keys() + forEach](#35-objectkeys--foreach)
      - [基本用法](#基本用法-4)
      - [支持数组](#支持数组)
      - [优缺点](#优缺点-4)
    - [3.6 手写浅拷贝函数](#36-手写浅拷贝函数)
      - [通用浅拷贝实现](#通用浅拷贝实现)
    - [3.7 各方式优缺点对比](#37-各方式优缺点对比)
  - [四、深拷贝实现方式](#四深拷贝实现方式)
    - [4.1 JSON.parse(JSON.stringify())](#41-jsonparsejsonstringify)
      - [基本用法](#基本用法-5)
      - [工作原理](#工作原理)
      - [局限性](#局限性)
      - [循环引用问题](#循环引用问题)
      - [优缺点](#优缺点-5)
    - [4.2 递归拷贝函数](#42-递归拷贝函数)
      - [通用深拷贝实现](#通用深拷贝实现)
      - [使用示例](#使用示例)
    - [4.3 structuredClone()（浏览器原生）](#43-structuredclone浏览器原生)
      - [基本用法](#基本用法-6)
      - [特性与限制](#特性与限制)
      - [与 JSON.parse(JSON.stringify()) 对比](#与-jsonparsejsonstringify-对比)
    - [4.4 第三方库实现（lodash）](#44-第三方库实现lodash)
      - [使用 lodash 的 cloneDeep](#使用-lodash-的-clonedeep)
      - [lodash cloneDeep 特性](#lodash-clonedeep-特性)
    - [4.5 各方式对比与适用场景](#45-各方式对比与适用场景)
      - [选择建议](#选择建议)
  - [五、特殊数据类型的拷贝处理](#五特殊数据类型的拷贝处理)
    - [5.1 Date 对象](#51-date-对象)
      - [问题](#问题)
      - [正确处理方式](#正确处理方式)
    - [5.2 RegExp 对象](#52-regexp-对象)
      - [问题](#问题-1)
      - [正确处理方式](#正确处理方式-1)
    - [5.3 Function 函数](#53-function-函数)
      - [问题](#问题-2)
      - [处理方式](#处理方式)
    - [5.4 Map 和 Set](#54-map-和-set)
      - [问题](#问题-3)
      - [正确处理方式](#正确处理方式-2)
    - [5.5 Symbol 类型](#55-symbol-类型)
      - [问题](#问题-4)
      - [处理方式](#处理方式-1)
    - [5.6 循环引用](#56-循环引用)
      - [问题场景](#问题场景)
      - [解决方案：使用 WeakMap](#解决方案使用-weakmap)
  - [六、性能对比与最佳实践](#六性能对比与最佳实践)
    - [6.1 性能对比](#61-性能对比)
      - [测试环境与数据](#测试环境与数据)
      - [性能测试结果](#性能测试结果)
    - [6.2 选择策略](#62-选择策略)
    - [6.3 常见错误用法](#63-常见错误用法)
      - [错误 1：对大型对象进行不必要的深拷贝](#错误-1对大型对象进行不必要的深拷贝)
      - [错误 2：忽略循环引用导致栈溢出](#错误-2忽略循环引用导致栈溢出)
      - [错误 3：用 JSON 方式拷贝包含特殊类型的对象](#错误-3用-json-方式拷贝包含特殊类型的对象)
      - [错误 4：在 Vue/Pinia 等状态管理中直接修改](#错误-4在-vuepinia-等状态管理中直接修改)
  - [七、面试题精选](#七面试题精选)
    - [题目 1：如何实现一个深拷贝？](#题目-1如何实现一个深拷贝)
    - [题目 2：浅拷贝和深拷贝的区别是什么？](#题目-2浅拷贝和深拷贝的区别是什么)
    - [题目 3：JSON.parse(JSON.stringify()) 有什么缺陷？](#题目-3jsonparsejsonstringify-有什么缺陷)
    - [题目 4：如何处理循环引用的深拷贝？](#题目-4如何处理循环引用的深拷贝)
  - [八、总结与速查表](#八总结与速查表)
    - [核心概念速查表](#核心概念速查表)
    - [浅拷贝方法速查表](#浅拷贝方法速查表)
    - [深拷贝方法速查表](#深拷贝方法速查表)
    - [最佳实践清单](#最佳实践清单)
    - [记忆口诀](#记忆口诀)
  - [附录：完整工具函数](#附录完整工具函数)
    - [通用深拷贝工具库](#通用深拷贝工具库)

---

## 一、概述：为什么需要深浅拷贝

### 1.1 问题场景

```javascript
// 场景 1：数据修改引发的连锁反应
const original = { name: 'Alice', address: { city: 'Beijing' } };
const copy = original; // 直接赋值，不是拷贝

copy.name = 'Bob';
console.log(original.name); // 'Bob' —— original 也被修改了！

// 场景 2：数组操作影响原始数据
const arr1 = [1, 2, [3, 4]];
const arr2 = arr1; // 直接赋值

arr2.push(5);
console.log(arr1); // [1, 2, [3, 4], 5] —— arr1 也被修改了！
```

### 1.2 深浅拷贝的作用

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    深浅拷贝的作用                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. 数据隔离：确保修改副本时不影响原始数据                              │
│  2. 状态管理：在 Vuex/Pinia 等状态管理中避免意外修改                    │
│  3. 缓存优化：避免重复计算，提高性能                                    │
│  4. 数据传递：在函数间传递数据时避免副作用                                │
│                                                                         │
│  核心问题：如何正确地复制一个复杂对象，使其与原对象完全独立？            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 二、核心概念与差异

### 2.1 基本数据类型 vs 引用数据类型

JavaScript 中的数据类型分为两大类，它们在内存中的存储方式完全不同：

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    数据类型分类                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  基本数据类型（原始类型）：                                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  • String（字符串）                                               │   │
│  │  • Number（数字）                                                 │   │
│  │  • Boolean（布尔值）                                              │   │
│  │  • null（空值）                                                   │   │
│  │  • undefined（未定义）                                            │   │
│  │  • Symbol（符号，ES6+）                                           │   │
│  │  • BigInt（大整数，ES10+）                                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  引用数据类型（复杂类型）：                                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  • Object（对象）                                                 │   │
│  │  • Array（数组）                                                  │   │
│  │  • Function（函数）                                               │   │
│  │  • Date（日期对象）                                               │   │
│  │  • RegExp（正则表达式）                                           │   │
│  │  • Map、Set（ES6+ 集合类型）                                     │   │
│  │  • 其他内置对象                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 内存存储机制

#### 基本数据类型：值存储在栈中

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    栈内存（Stack）                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  let a = 10;                                                            │
│  let b = a;  // 复制值                                                  │
│  b = 20;                                                                │
│                                                                         │
│  栈内存：                                                               │
│  ┌─────────────┐    ┌─────────────┐                                    │
│  │ 变量 a      │    │ 变量 b      │                                    │
│  │ ┌─────────┐ │    │ ┌─────────┐ │                                    │
│  │ │   10    │ │    │ │   20    │ │                                    │
│  │ └─────────┘ │    │ └─────────┘ │                                    │
│  └─────────────┘    └─────────────┘                                    │
│       ↑                    ↑                                            │
│       │                    │                                            │
│       └── 独立的两个值，互不影响 ──┘                                    │
│                                                                         │
│  结论：基本数据类型的赋值本身就是拷贝（深拷贝）                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 引用数据类型：值存储在堆中，变量存储引用

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    内存模型                                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  let obj1 = { name: 'Alice' };                                          │
│  let obj2 = obj1;  // 复制引用，不是值                                  │
│                                                                         │
│  栈内存（Stack）：                                                       │
│  ┌─────────────┐    ┌─────────────┐                                    │
│  │ 变量 obj1   │    │ 变量 obj2   │                                    │
│  │ ┌─────────┐ │    │ ┌─────────┐ │                                    │
│  │ │  地址1  │ │    │ │  地址1  │ │  ← 两个变量指向同一地址              │
│  │ └─────────┘ │    │ └─────────┘ │                                    │
│  └─────────────┘    └─────────────┘                                    │
│       │                    │                                            │
│       │                    │                                            │
│       └────────┬───────────┘                                            │
│                │                                                        │
│                ▼                                                        │
│  堆内存（Heap）：                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  { name: 'Alice' }  ← 只有一份实际数据                           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  修改 obj2.name = 'Bob'：                                               │
│  → 实际上是修改堆中的数据                                               │
│  → obj1.name 也会变成 'Bob'                                             │
│                                                                         │
│  结论：引用数据类型的赋值不是拷贝，只是复制了引用                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.3 深浅拷贝定义

#### 浅拷贝（Shallow Copy）

> 创建一个新对象，新对象的基本类型属性会复制值，但引用类型属性只复制引用（共享同一内存地址）。

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    浅拷贝示意图                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  原对象 original：                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  {                                                               │   │
│  │    name: 'Alice',         ← 基本类型                              │   │
│  │    age: 25,               ← 基本类型                              │   │
│  │    address: {             ← 引用类型                              │   │
│  │      city: 'Beijing',                                             │   │
│  │      zip: '100000'                                               │   │
│  │    }                                                             │   │
│  │  }                                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  浅拷贝副本 copy：                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  {                                                               │   │
│  │    name: 'Alice',         ← 复制了值（独立）                       │   │
│  │    age: 25,               ← 复制了值（独立）                       │   │
│  │    address: ────────────────────┐                                │   │
│  │  }                              │                                │   │
│  └─────────────────────────────────│────────────────────────────────┘   │
│                                    │                                    │
│                                    ▼                                    │
│                          指向原对象的 address                            │
│                          { city: 'Beijing', zip: '100000' }              │
│                          ← 共享引用，修改会互相影响                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 深拷贝（Deep Copy）

> 创建一个新对象，新对象的所有属性（包括嵌套的引用类型）都会复制值，形成完全独立的数据副本。

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    深拷贝示意图                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  原对象 original：                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  {                                                               │   │
│  │    name: 'Alice',                                                │   │
│  │    age: 25,                                                      │   │
│  │    address: {                                                    │   │
│  │      city: 'Beijing',                                             │   │
│  │      zip: '100000'                                               │   │
│  │    }                                                             │   │
│  │  }                                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  深拷贝副本 copy：                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  {                                                               │   │
│  │    name: 'Alice',         ← 复制了值（独立）                       │   │
│  │    age: 25,               ← 复制了值（独立）                       │   │
│  │    address: {             ← 也是新对象！（独立）                    │   │
│  │      city: 'Beijing',    ← 复制了值（独立）                       │   │
│  │      zip: '100000'       ← 复制了值（独立）                       │   │
│  │    }                                                             │   │
│  │  }                                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  关键点：                                                                │
│  ✅ 基本类型：复制值                                                    │
│  ✅ 引用类型：递归复制，创建新对象                                      │
│  ✅ 所有层级的数据都是独立的                                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.4 核心差异对比

| 对比维度 | 浅拷贝 | 深拷贝 |
|---------|--------|--------|
| **基本类型属性** | 复制值，独立 | 复制值，独立 |
| **引用类型属性** | 复制引用，共享内存 | 递归复制，独立 |
| **嵌套对象** | 不复制，共享引用 | 递归复制，完全独立 |
| **性能** | 较快 | 较慢（递归遍历） |
| **内存占用** | 较少 | 较多（创建新对象） |
| **实现复杂度** | 简单 | 复杂 |
| **数据隔离** | 部分隔离（顶层隔离） | 完全隔离 |

---

## 三、浅拷贝实现方式

### 3.1 Object.assign()

#### 基本用法

```javascript
const original = { name: 'Alice', age: 25 };
const copy = Object.assign({}, original);

console.log(copy); // { name: 'Alice', age: 25 }
console.log(copy === original); // false —— 不是同一个对象
```

#### 浅拷贝特性验证

```javascript
const original = {
  name: 'Alice',
  address: { city: 'Beijing', zip: '100000' }
};

const copy = Object.assign({}, original);

// 修改顶层属性 —— 不影响原对象
copy.name = 'Bob';
console.log(original.name); // 'Alice' ✅ 互不影响

// 修改嵌套属性 —— 影响原对象！
copy.address.city = 'Shanghai';
console.log(original.address.city); // 'Shanghai' ❌ 影响了原对象
```

#### 源码级分析

```javascript
// Object.assign 内部简化实现
function myAssign(target, ...sources) {
  for (const source of sources) {
    // 只遍历可枚举属性
    for (const key in source) {
      if (Object.prototype.hasOwnProperty.call(source, key)) {
        // 基本类型：复制值
        // 引用类型：复制引用
        target[key] = source[key];
      }
    }
  }
  return target;
}
```

#### 优缺点

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Object.assign() 优缺点                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ✅ 优点：                                                               │
│  □ 原生 API，兼容性好（ES6+）                                          │
│  □ 支持多个源对象合并                                                   │
│  □ 语法简洁，易读                                                       │
│  □ 处理基本类型属性效果好                                               │
│                                                                         │
│  ❌ 缺点：                                                               │
│  □ 只能进行浅拷贝，嵌套对象共享引用                                     │
│  □ 不能处理 getter/setter（直接复制值）                                  │
│  □ 不能处理不可枚举属性                                                 │
│  □ 不支持 Symbol 属性（ES2018+ 才支持）                                │
│                                                                         │
│  适用场景：                                                              │
│  ✓ 简单对象的浅拷贝                                                     │
│  ✓ 多对象属性合并                                                       │
│  ✓ 默认值对象扩展                                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 3.2 扩展运算符

#### 基本用法

```javascript
const original = { name: 'Alice', age: 25 };
const copy = { ...original };

console.log(copy); // { name: 'Alice', age: 25 }
console.log(copy === original); // false
```

#### 数组浅拷贝

```javascript
const arr1 = [1, 2, 3];
const arr2 = [...arr1];

console.log(arr2); // [1, 2, 3]
console.log(arr2 === arr1); // false

// 修改不影响原数组
arr2.push(4);
console.log(arr1); // [1, 2, 3]
console.log(arr2); // [1, 2, 3, 4]
```

#### 源码级分析

```javascript
// 扩展运算符的编译结果（简化）
// { ...original } 等价于：
function spreadCopy(obj) {
  const result = {};
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      result[key] = obj[key]; // 与 Object.assign 相同
    }
  }
  return result;
}
```

#### 优缺点

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    扩展运算符 优缺点                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ✅ 优点：                                                               │
│  □ 语法最简洁，可读性强                                                │
│  □ 同时适用于对象和数组                                                 │
│  □ 支持字符串等可迭代对象                                               │
│  □ 性能略优于 Object.assign                                             │
│                                                                         │
│  ❌ 缺点：                                                               │
│  □ 只能进行浅拷贝                                                       │
│  □ 兼容性需要 ES6+ 环境或转译                                           │
│  □ 不能处理原型链上的属性                                               │
│                                                                         │
│  适用场景：                                                              │
│  ✓ 简单对象/数组的快速浅拷贝                                            │
│  ✓ 函数参数展开                                                         │
│  ✓ 数组合并                                                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 3.3 Array.prototype.slice()

#### 基本用法

```javascript
const arr1 = [1, 2, 3, [4, 5]];
const arr2 = arr1.slice(); // 不传参数，复制整个数组

console.log(arr2); // [1, 2, 3, [4, 5]]
console.log(arr2 === arr1); // false
console.log(arr2[3] === arr1[3]); // true —— 嵌套数组共享引用
```

#### 实现原理

```javascript
// slice 无参调用的内部简化实现
Array.prototype.mySlice = function() {
  const result = [];
  for (let i = 0; i < this.length; i++) {
    result[i] = this[i]; // 复制值或引用
  }
  return result;
};
```

#### 优缺点

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    slice() 优缺点                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ✅ 优点：                                                               │
│  □ 专门用于数组，语义清晰                                               │
│  □ 原生 API，兼容性好                                                   │
│  □ 可选择性复制部分数组                                                 │
│                                                                         │
│  ❌ 缺点：                                                               │
│  □ 仅适用于数组，不适用于对象                                           │
│  □ 浅拷贝，嵌套元素共享引用                                             │
│  □ 对类数组对象无效（需要 Array.from 转换）                             │
│                                                                         │
│  适用场景：                                                              │
│  ✓ 数组浅拷贝                                                           │
│  ✓ 数组切片复制                                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 3.4 Array.prototype.concat()

#### 基本用法

```javascript
const arr1 = [1, 2, 3];
const arr2 = [].concat(arr1); // 创建新数组

console.log(arr2); // [1, 2, 3]
console.log(arr2 === arr1); // false

// 也可以通过 concat 实现
const arr3 = arr1.concat(); // 不传参数
```

#### 优缺点

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    concat() 优缺点                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ✅ 优点：                                                               │
│  □ 原生 API，兼容性好                                                   │
│  □ 同时支持数组合并和拷贝                                               │
│                                                                         │
│  ❌ 缺点：                                                               │
│  □ 仅适用于数组                                                         │
│  □ 浅拷贝，嵌套元素共享引用                                             │
│  □ 语义不如 slice 清晰（用于拷贝有些奇怪）                               │
│                                                                         │
│  适用场景：                                                              │
│  ✓ 数组合并时顺便创建新数组                                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 3.5 Object.keys() + forEach

#### 基本用法

```javascript
const original = { name: 'Alice', age: 25 };
const copy = {};

Object.keys(original).forEach(key => {
  copy[key] = original[key];
});

console.log(copy); // { name: 'Alice', age: 25 }
```

#### 支持数组

```javascript
const arr1 = [1, 2, 3];
const arr2 = [];

Object.keys(arr1).forEach(key => {
  arr2[key] = arr1[key];
});

console.log(arr2); // [1, 2, 3]
```

#### 优缺点

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Object.keys() + forEach 优缺点                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ✅ 优点：                                                               │
│  □ 灵活可控，可以添加额外逻辑                                           │
│  □ 只遍历自身可枚举属性                                                 │
│  □ 可扩展性强（如过滤属性、转换值等）                                   │
│                                                                         │
│  ❌ 缺点：                                                               │
│  □ 代码较冗长                                                           │
│  □ 性能略低于原生 API                                                   │
│                                                                         │
│  适用场景：                                                              │
│  ✓ 需要在拷贝时进行属性处理                                             │
│  ✓ 过滤特定属性                                                         │
│  ✓ 自定义拷贝逻辑                                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 3.6 手写浅拷贝函数

#### 通用浅拷贝实现

```javascript
/**
 * 通用浅拷贝函数
 * @param {Object|Array} source - 源对象
 * @returns {Object|Array} 拷贝后的新对象
 */
function shallowCopy(source) {
  // 基本类型直接返回
  if (typeof source !== 'object' || source === null) {
    return source;
  }
  
  // 判断是数组还是对象
  const target = Array.isArray(source) ? [] : {};
  
  // 遍历自身可枚举属性
  for (const key in source) {
    if (Object.prototype.hasOwnProperty.call(source, key)) {
      target[key] = source[key];
    }
  }
  
  return target;
}

// 使用示例
const obj = { name: 'Alice', hobbies: ['reading', 'coding'] };
const objCopy = shallowCopy(obj);

console.log(objCopy); // { name: 'Alice', hobbies: ['reading', 'coding'] }
console.log(objCopy === obj); // false
console.log(objCopy.hobbies === obj.hobbies); // true —— 浅拷贝，嵌套数组共享引用

const arr = [1, 2, { nested: 'value' }];
const arrCopy = shallowCopy(arr);

console.log(arrCopy); // [1, 2, { nested: 'value' }]
console.log(arrCopy === arr); // false
```

---

### 3.7 各方式优缺点对比

| 方法 | 适用类型 | 语法简洁性 | 性能 | 嵌套支持 | 兼容性 |
|------|---------|-----------|------|---------|--------|
| `Object.assign()` | 对象 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ | ES6+ |
| `{ ...obj }` | 对象/数组 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ | ES6+ |
| `arr.slice()` | 数组 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ | 所有版本 |
| `arr.concat()` | 数组 | ⭐⭐⭐ | ⭐⭐⭐ | ❌ | 所有版本 |
| `Object.keys() + forEach` | 对象/数组 | ⭐⭐ | ⭐⭐⭐ | ❌ | ES5+ |
| `for...in` | 对象/数组 | ⭐⭐ | ⭐⭐⭐ | ❌ | 所有版本 |

---

## 四、深拷贝实现方式

### 4.1 JSON.parse(JSON.stringify())

#### 基本用法

```javascript
const original = {
  name: 'Alice',
  age: 25,
  address: {
    city: 'Beijing',
    zip: '100000'
  },
  hobbies: ['reading', 'coding']
};

// 转换为 JSON 字符串，再解析回对象
const copy = JSON.parse(JSON.stringify(original));

console.log(copy);
// {
//   name: 'Alice',
//   age: 25,
//   address: { city: 'Beijing', zip: '100000' },
//   hobbies: ['reading', 'coding']
// }

// 验证深拷贝
console.log(copy === original); // false
console.log(copy.address === original.address); // false —— 独立对象！

copy.address.city = 'Shanghai';
console.log(original.address.city); // 'Beijing' —— 不影响原对象 ✅
```

#### 工作原理

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    JSON.parse(JSON.stringify()) 工作原理                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  步骤 1：JSON.stringify(obj)                                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  将 JavaScript 对象转换为 JSON 字符串                            │   │
│  │                                                                  │   │
│  │  { name: 'Alice', address: { city: 'Beijing' } }                 │   │
│  │  →                                                              │   │
│  │  '{"name":"Alice","address":{"city":"Beijing"}}'                  │   │
│  │                                                                  │   │
│  │  此过程会：                                                      │   │
│  │  ✅ 递归遍历所有层级的属性                                       │   │
│  │  ✅ 将引用类型转为基本类型表示                                   │   │
│  │  ❌ 丢失不支持的类型（function、Date、undefined 等）              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  步骤 2：JSON.parse(jsonString)                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  将 JSON 字符串解析为新的 JavaScript 对象                        │   │
│  │                                                                  │   │
│  │  '{"name":"Alice","address":{"city":"Beijing"}}'                  │   │
│  │  →                                                              │   │
│  │  { name: 'Alice', address: { city: 'Beijing' } }                 │   │
│  │                                                                  │   │
│  │  此过程会：                                                      │   │
│  │  ✅ 创建全新的对象实例                                           │   │
│  │  ✅ 所有属性都是独立的                                           │   │
│  │  ❌ 无法还原丢失的类型信息                                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 局限性

```javascript
// ❌ 不能处理的类型示例
const obj = {
  string: 'hello',
  number: 123,
  boolean: true,
  null: null,
  undefined: undefined,      // → 丢失！
  symbol: Symbol('test'),    // → 丢失！
  function: () => 'hello',  // → 丢失！
  date: new Date(),          // → 变为字符串！
  regexp: /abc/g,            // → 变为空对象！
  map: new Map([['key', 'value']]), // → 丢失！
  set: new Set([1, 2, 3]),  // → 丢失！
  nan: NaN,                  // → 变为 null！
  infinity: Infinity,       // → 变为 null！
};

const copy = JSON.parse(JSON.stringify(obj));
console.log(copy);
// {
//   string: 'hello',
//   number: 123,
//   boolean: true,
//   null: null,
//   // undefined 丢失
//   // symbol 丢失
//   // function 丢失
//   date: '2024-01-01T00:00:00.000Z', // 变为字符串
//   regexp: {},                       // 变为空对象
//   // map 丢失
//   // set 丢失
//   nan: null,                        // NaN 变为 null
//   infinity: null                    // Infinity 变为 null
// }
```

#### 循环引用问题

```javascript
// ❌ 循环引用会导致报错
const obj = { name: 'test' };
obj.self = obj; // 循环引用

try {
  JSON.parse(JSON.stringify(obj));
} catch (e) {
  console.log(e.message);
  // "Converting circular structure to JSON"
}
```

#### 优缺点

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    JSON.parse(JSON.stringify()) 优缺点                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ✅ 优点：                                                               │
│  □ 实现最简单，一行代码搞定                                             │
│  □ 性能较好（V8 引擎优化）                                              │
│  □ 能处理大多数常见数据结构                                             │
│  □ 原生 API，无第三方依赖                                               │
│                                                                         │
│  ❌ 缺点：                                                               │
│  □ 不能处理函数、undefined、Symbol 等类型                               │
│  □ Date 对象会变为字符串                                                 │
│  □ RegExp 对象会变为空对象                                              │
│  □ NaN、Infinity 会变为 null                                           │
│  □ 循环引用会报错                                                       │
│  □ 忽略不可枚举属性和原型链                                             │
│                                                                         │
│  适用场景：                                                              │
│  ✓ 仅包含基本类型、数组、普通对象的纯数据                               │
│  ✓ API 请求/响应数据的拷贝                                             │
│  ✓ 配置对象的拷贝                                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 4.2 递归拷贝函数

#### 通用深拷贝实现

```javascript
/**
 * 通用深拷贝函数
 * @param {*} source - 源对象
 * @param {WeakMap} [hash=new WeakMap()] - 用于处理循环引用
 * @returns {*} 拷贝后的新对象
 */
function deepClone(source, hash = new WeakMap()) {
  // 1. 处理基本类型
  if (typeof source !== 'object' || source === null) {
    return source;
  }
  
  // 2. 处理循环引用
  if (hash.has(source)) {
    return hash.get(source);
  }
  
  // 3. 创建对应的目标对象
  const target = Array.isArray(source) 
    ? [] 
    : Object.create(Object.getPrototypeOf(source));
  
  // 4. 保存到 hash，处理循环引用
  hash.set(source, target);
  
  // 5. 处理特殊类型
  if (source instanceof Date) {
    return new Date(source.getTime());
  }
  
  if (source instanceof RegExp) {
    return new RegExp(source.source, source.flags);
  }
  
  if (source instanceof Map) {
    const mapCopy = new Map();
    source.forEach((value, key) => {
      mapCopy.set(deepClone(key, hash), deepClone(value, hash));
    });
    return mapCopy;
  }
  
  if (source instanceof Set) {
    const setCopy = new Set();
    source.forEach(value => {
      setCopy.add(deepClone(value, hash));
    });
    return setCopy;
  }
  
  // 6. 处理普通对象和数组
  for (const key in source) {
    if (Object.prototype.hasOwnProperty.call(source, key)) {
      target[key] = deepClone(source[key], hash);
    }
  }
  
  return target;
}
```

#### 使用示例

```javascript
// 基础用法
const original = {
  name: 'Alice',
  age: 25,
  hobbies: ['reading', 'coding'],
  address: {
    city: 'Beijing',
    zip: '100000'
  }
};

const copy = deepClone(original);
console.log(copy === original); // false
console.log(copy.address === original.address); // false
console.log(copy.hobbies === original.hobbies); // false

// 循环引用测试
const obj = { name: 'test' };
obj.self = obj;

const cloned = deepClone(obj);
console.log(cloned.name); // 'test'
console.log(cloned.self === cloned); // true —— 循环引用正确处理

// 特殊类型测试
const complex = {
  date: new Date('2024-01-01'),
  regex: /hello/gi,
  map: new Map([['key', 'value']]),
  set: new Set([1, 2, 3])
};

const complexCopy = deepClone(complex);
console.log(complexCopy.date instanceof Date); // true
console.log(complexCopy.regex instanceof RegExp); // true
console.log(complexCopy.map instanceof Map); // true
console.log(complexCopy.set instanceof Set); // true
```

---

### 4.3 structuredClone()（浏览器原生）

#### 基本用法

```javascript
const original = {
  name: 'Alice',
  age: 25,
  nested: { value: 'deep' },
  date: new Date('2024-01-01'),
  regex: /hello/gi,
  map: new Map([['key', 'value']])
};

// 使用浏览器原生的 structuredClone
const copy = structuredClone(original);

console.log(copy === original); // false
console.log(copy.nested === original.nested); // false
console.log(copy.date instanceof Date); // true
console.log(copy.regex instanceof RegExp); // true
console.log(copy.map instanceof Map); // true
```

#### 特性与限制

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    structuredClone() 特性                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ✅ 支持的类型：                                                         │
│  □ 基本类型（除 Symbol 外）                                             │
│  □ Object、Array                                                        │
│  □ Date、RegExp                                                         │
│  □ Map、Set                                                             │
│  □ Blob、File、FileList                                                 │
│  □ ImageData、ArrayBuffer                                               │
│  □ 循环引用                                                             │
│                                                                         │
│  ❌ 不支持的类型：                                                       │
│  □ Function（会抛出 DataCloneError）                                    │
│  □ Symbol                                                               │
│  □ DOM 节点                                                             │
│  □ 原型链（不保留原型）                                                 │
│  □ 对象的 getter/setter                                                │
│                                                                         │
│  兼容性：                                                                │
│  □ 现代浏览器（Chrome 98+, Firefox 94+, Safari 15.4+）                 │
│  □ Node.js 17+                                                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 与 JSON.parse(JSON.stringify()) 对比

```javascript
const obj = {
  date: new Date('2024-01-01'),
  map: new Map([['key', 'value']]),
  regex: /hello/gi,
  nested: { value: 'test' }
};

// JSON 方式
const jsonCopy = JSON.parse(JSON.stringify(obj));
console.log(jsonCopy.date); // '2024-01-01T00:00:00.000Z'（字符串）
console.log(jsonCopy.map);  // {}（丢失）
console.log(jsonCopy.regex); // {}（丢失）

// structuredClone 方式
const structuredCopy = structuredClone(obj);
console.log(structuredCopy.date instanceof Date); // true ✅
console.log(structuredCopy.map instanceof Map); // true ✅
console.log(structuredCopy.regex instanceof RegExp); // true ✅
```

---

### 4.4 第三方库实现（lodash）

#### 使用 lodash 的 cloneDeep

```javascript
import { cloneDeep } from 'lodash';

const original = {
  name: 'Alice',
  age: 25,
  hobbies: ['reading', 'coding'],
  address: {
    city: 'Beijing',
    zip: '100000'
  },
  date: new Date('2024-01-01'),
  map: new Map([['key', 'value']]),
  // 等等...
};

const copy = cloneDeep(original);

console.log(copy === original); // false
console.log(copy.address === original.address); // false
console.log(copy.date instanceof Date); // true
```

#### lodash cloneDeep 特性

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    lodash cloneDeep 特性                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ✅ 支持的类型：                                                         │
│  □ 基本类型（null、undefined、boolean、number、string）                │
│  □ Object、Array                                                        │
│  □ Date、RegExp                                                         │
│  □ Map、Set                                                             │
│  □ Symbol                                                               │
│  □ Function（返回同一个函数引用，不复制）                                │
│  □ Buffer（Node.js）                                                    │
│  □ TypedArray                                                           │
│  □ 循环引用                                                             │
│  □ 原型链（保留原型）                                                   │
│                                                                         │
│  安装：                                                                  │
│  npm install lodash                                                     │
│                                                                         │
│  或使用按需加载：                                                        │
│  npm install lodash.clonedeep                                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 4.5 各方式对比与适用场景

| 方式 | 实现难度 | 性能 | 类型支持 | 循环引用 | 依赖 |
|------|---------|------|---------|---------|------|
| `JSON.parse(JSON.stringify())` | ⭐ | ⭐⭐⭐⭐ | ❌ 有限 | ❌ | 无 |
| `structuredClone()` | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ | 无（浏览器原生） |
| 递归拷贝函数 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | 无 |
| lodash `cloneDeep` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | lodash |

#### 选择建议

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    选择策略                                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. 如果数据是纯 JSON 格式（无函数、Date、循环引用等）：                 │
│     → JSON.parse(JSON.stringify())                                      │
│                                                                         │
│  2. 如果需要处理 Date、RegExp、Map 等类型：                              │
│     → structuredClone()（现代浏览器）                                    │
│     → lodash cloneDeep（兼容性要求高）                                   │
│                                                                         │
│  3. 如果有特殊需求或想理解原理：                                         │
│     → 手写递归拷贝函数                                                   │
│                                                                         │
│  4. 如果项目已引入 lodash：                                              │
│     → 直接使用 cloneDeep                                                │
│                                                                         │
│  5. 如果是性能敏感场景：                                                 │
│     → 优先使用 structuredClone() 或 lodash cloneDeep                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 五、特殊数据类型的拷贝处理

### 5.1 Date 对象

#### 问题

```javascript
const date = new Date('2024-01-01');
console.log(typeof date); // 'object'
console.log(date instanceof Date); // true

// JSON 方式的问题
const jsonCopy = JSON.parse(JSON.stringify(date));
console.log(jsonCopy); // '2024-01-01T00:00:00.000Z'（变成字符串！）
console.log(jsonCopy instanceof Date); // false
```

#### 正确处理方式

```javascript
// 方式 1：使用 getTime() 或 valueOf()
const dateCopy = new Date(date.getTime());

// 方式 2：使用 structuredClone（推荐）
const structuredCopy = structuredClone(date);

// 方式 3：在递归拷贝中特殊处理
function cloneDate(source) {
  if (source instanceof Date) {
    return new Date(source.getTime());
  }
}
```

### 5.2 RegExp 对象

#### 问题

```javascript
const regex = /hello/gi;
console.log(typeof regex); // 'object'

// JSON 方式的问题
const jsonCopy = JSON.parse(JSON.stringify(regex));
console.log(jsonCopy); // {}（变成空对象！）
console.log(jsonCopy instanceof RegExp); // false
```

#### 正确处理方式

```javascript
// 方式 1：使用 source 和 flags
const regexCopy = new RegExp(regex.source, regex.flags);

// 方式 2：使用 structuredClone（推荐）
const structuredCopy = structuredClone(regex);

// 方式 3：在递归拷贝中特殊处理
function cloneRegExp(source) {
  if (source instanceof RegExp) {
    return new RegExp(source.source, source.flags);
  }
}
```

### 5.3 Function 函数

#### 问题

```javascript
const fn = function(a, b) { return a + b; };

// JSON 方式的问题
const jsonCopy = JSON.parse(JSON.stringify(fn));
console.log(jsonCopy); // undefined（函数被丢弃！）
```

#### 处理方式

```javascript
// 方式 1：使用 eval（不推荐，安全风险）
const fnCopy = eval(fn.toString());

// 方式 2：使用 bind/call（创建新的函数引用）
const fnCopy = fn.bind({});

// 方式 3：lodash cloneDeep（保留函数引用）
import { cloneDeep } from 'lodash';
const fnCopy = cloneDeep(fn);
console.log(fnCopy === fn); // true（lodash 返回同一个引用）

// 方式 4：通常函数不需要深拷贝，直接引用即可
const fnCopy = fn; // 函数通常保持引用即可
```

### 5.4 Map 和 Set

#### 问题

```javascript
const map = new Map([['key1', 'value1'], ['key2', 'value2']]);
const set = new Set([1, 2, 3]);

// JSON 方式的问题
console.log(JSON.parse(JSON.stringify(map))); // {}（丢失！）
console.log(JSON.parse(JSON.stringify(set))); // {}（丢失！）
```

#### 正确处理方式

```javascript
// Map 拷贝
function cloneMap(source) {
  if (source instanceof Map) {
    const mapCopy = new Map();
    source.forEach((value, key) => {
      mapCopy.set(key, value); // 或递归拷贝
    });
    return mapCopy;
  }
}

// Set 拷贝
function cloneSet(source) {
  if (source instanceof Set) {
    const setCopy = new Set();
    source.forEach(value => {
      setCopy.add(value); // 或递归拷贝
    });
    return setCopy;
  }
}

// 使用 structuredClone（推荐）
const mapCopy = structuredClone(map);
const setCopy = structuredClone(set);
```

### 5.5 Symbol 类型

#### 问题

```javascript
const sym = Symbol('test');
const obj = { [sym]: 'value' };

// JSON 方式的问题
console.log(JSON.parse(JSON.stringify(obj))); // {}（Symbol 属性丢失！）
```

#### 处理方式

```javascript
// 在递归拷贝中处理 Symbol
function cloneWithSymbols(source) {
  // 拷贝 Symbol 属性
  const symbolKeys = Object.getOwnPropertySymbols(source);
  symbolKeys.forEach(sym => {
    target[sym] = deepClone(source[sym], hash);
  });
}

// lodash cloneDeep 支持 Symbol
import { cloneDeep } from 'lodash';
const copy = cloneDeep(obj);
```

### 5.6 循环引用

#### 问题场景

```javascript
// 循环引用示例
const obj = { name: 'test' };
obj.self = obj; // obj 引用了自己

const obj2 = { a: {} };
obj2.a.b = obj2; // 间接循环引用

// JSON 方式会报错
try {
  JSON.parse(JSON.stringify(obj));
} catch (e) {
  console.log(e.message); // "Converting circular structure to JSON"
}
```

#### 解决方案：使用 WeakMap

```javascript
/**
 * 支持循环引用的深拷贝
 */
function deepCloneWithCircular(source, hash = new WeakMap()) {
  if (typeof source !== 'object' || source === null) {
    return source;
  }
  
  // 如果已经拷贝过，直接返回
  if (hash.has(source)) {
    return hash.get(source);
  }
  
  const target = Array.isArray(source) ? [] : {};
  
  // 先保存到 hash，处理循环引用
  hash.set(source, target);
  
  // 递归拷贝
  for (const key in source) {
    if (Object.prototype.hasOwnProperty.call(source, key)) {
      target[key] = deepCloneWithCircular(source[key], hash);
    }
  }
  
  return target;
}

// 测试
const obj = { name: 'test' };
obj.self = obj; // 循环引用

const copy = deepCloneWithCircular(obj);
console.log(copy.name); // 'test'
console.log(copy.self === copy); // true ✅ 正确处理循环引用
```

---

## 六、性能对比与最佳实践

### 6.1 性能对比

#### 测试环境与数据

```javascript
// 测试用对象
const testObj = {
  name: 'Test',
  data: Array.from({ length: 1000 }, (_, i) => ({
    id: i,
    value: `item_${i}`,
    nested: { a: i, b: i * 2 }
  })),
  config: {
    timeout: 5000,
    retries: 3,
    options: { debug: true, verbose: false }
  }
};

// 性能测试函数
function benchmark(name, fn, times = 100) {
  console.time(name);
  for (let i = 0; i < times; i++) {
    fn();
  }
  console.timeEnd(name);
}
```

#### 性能测试结果

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    性能对比表（100 次调用）                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  方法                                    │ 耗时           │ 备注       │
│  ───────────────────────────────────────────────────────────────────  │
│  直接赋值（reference）                   │ ~0.01ms        │ 不拷贝     │
│  Object.assign()                         │ ~0.5ms         │ 浅拷贝     │
│  { ...spread }                           │ ~0.4ms         │ 浅拷贝     │
│  JSON.parse(JSON.stringify())            │ ~2ms           │ 深拷贝     │
│  structuredClone()                       │ ~1.5ms         │ 深拷贝     │
│  手写递归深拷贝                           │ ~5ms           │ 深拷贝     │
│  lodash cloneDeep                        │ ~8ms           │ 深拷贝     │
│                                                                         │
│  注意：实际耗时因数据规模、引擎版本而异                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.2 选择策略

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    选择策略决策树                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  开始                                                                    │
│    │                                                                     │
│    ▼                                                                     │
│  需要拷贝吗？                                                            │
│    │                                                                     │
│    ├── 否 → 直接使用引用                                                 │
│    │                                                                     │
│    └── 是                                                                │
│         │                                                                │
│         ▼                                                                │
│       只需要拷贝顶层吗？                                                  │
│         │                                                                │
│         ├── 是                                                           │
│         │    │                                                           │
│         │    ▼                                                           │
│         │  是数组吗？                                                    │
│         │    │                                                           │
│         │    ├── 是 → arr.slice() 或 [...arr]                            │
│         │    │                                                           │
│         │    └── 否 → { ...obj } 或 Object.assign({}, obj)               │
│         │                                                                │
│         └── 否                                                           │
│              │                                                           │
│              ▼                                                           │
│            数据包含特殊类型吗？                                           │
│              │                                                           │
│              ├── 否 → JSON.parse(JSON.stringify())                        │
│              │                                                           │
│              └── 是                                                      │
│                   │                                                      │
│                   ▼                                                      │
│                 浏览器环境吗？                                           │
│                   │                                                      │
│                   ├── 是 → structuredClone()                              │
│                   │                                                      │
│                   └── 否                                                │
│                        │                                                 │
│                        ▼                                                 │
│                      使用 lodash cloneDeep 或手写深拷贝                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.3 常见错误用法

#### 错误 1：对大型对象进行不必要的深拷贝

```javascript
// ❌ 错误：对频繁访问的大型对象进行深拷贝
const hugeData = fetchHugeData(); // 10MB 数据

// 每次渲染都深拷贝
function render() {
  const copy = JSON.parse(JSON.stringify(hugeData)); // 性能问题！
  return processData(copy);
}

// ✅ 正确：只在必要时拷贝，或使用浅拷贝 + 局部更新
function render() {
  // 只拷贝需要修改的部分
  const partialCopy = { ...hugeData, items: [...hugeData.items] };
  return processData(partialCopy);
}
```

#### 错误 2：忽略循环引用导致栈溢出

```javascript
// ❌ 错误：没有处理循环引用
function deepClone(obj) {
  if (typeof obj !== 'object' || obj === null) return obj;
  
  const clone = Array.isArray(obj) ? [] : {};
  for (const key in obj) {
    // 如果有循环引用，会无限递归导致栈溢出
    clone[key] = deepClone(obj[key]); 
  }
  return clone;
}

// ✅ 正确：使用 WeakMap 处理循环引用
function deepCloneSafe(obj, hash = new WeakMap()) {
  if (typeof obj !== 'object' || obj === null) return obj;
  if (hash.has(obj)) return hash.get(obj); // 处理循环引用
  
  const clone = Array.isArray(obj) ? [] : {};
  hash.set(obj, clone);
  
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      clone[key] = deepCloneSafe(obj[key], hash);
    }
  }
  return clone;
}
```

#### 错误 3：用 JSON 方式拷贝包含特殊类型的对象

```javascript
// ❌ 错误：丢失类型信息
const data = {
  createdAt: new Date(),
  config: new Map([['key', 'value']]),
  handler: () => console.log('test')
};

const copy = JSON.parse(JSON.stringify(data));
// copy.createdAt 是字符串，不是 Date！
// copy.config 是 {}，不是 Map！
// copy.handler 丢失了！

// ✅ 正确：使用支持特殊类型的深拷贝
const correctCopy = structuredClone(data);
// correctCopy.createdAt 是 Date ✅
// correctCopy.config 是 Map ✅
// correctCopy.handler 会报错（Function 不支持）
```

#### 错误 4：在 Vue/Pinia 等状态管理中直接修改

```javascript
// ❌ 错误：直接修改 store 中的对象
const store = useStore();
store.user.profile.name = 'New Name'; // 直接修改，绕过响应式

// ✅ 正确：创建副本或使用 action
const newProfile = { ...store.user.profile, name: 'New Name' };
store.updateProfile(newProfile); // 通过 action 修改
```

---

## 七、面试题精选

### 题目 1：如何实现一个深拷贝？

**答案框架：**

```javascript
function deepClone(source, hash = new WeakMap()) {
  // 1. 基本类型直接返回
  if (typeof source !== 'object' || source === null) {
    return source;
  }
  
  // 2. 处理循环引用
  if (hash.has(source)) {
    return hash.get(source);
  }
  
  // 3. 创建目标对象
  const target = Array.isArray(source) ? [] : {};
  hash.set(source, target);
  
  // 4. 处理特殊类型
  if (source instanceof Date) {
    return new Date(source.getTime());
  }
  if (source instanceof RegExp) {
    return new RegExp(source.source, source.flags);
  }
  
  // 5. 递归拷贝
  for (const key in source) {
    if (Object.prototype.hasOwnProperty.call(source, key)) {
      target[key] = deepClone(source[key], hash);
    }
  }
  
  return target;
}
```

**考察要点：**
- 基本类型 vs 引用类型的判断
- 循环引用的处理（WeakMap）
- 特殊类型的处理（Date、RegExp）
- 原型链的处理

### 题目 2：浅拷贝和深拷贝的区别是什么？

**答案要点：**

```
1. 核心区别：引用类型的处理
   - 浅拷贝：只复制第一层，嵌套对象共享引用
   - 深拷贝：递归复制所有层级，完全独立

2. 实现方式：
   - 浅拷贝：Object.assign、扩展运算符、slice 等
   - 深拷贝：JSON.parse(JSON.stringify)、递归函数、第三方库

3. 性能差异：
   - 浅拷贝更快
   - 深拷贝因为递归遍历更慢

4. 使用场景：
   - 浅拷贝：简单结构、临时副本
   - 深拷贝：复杂嵌套、需要完全隔离
```

### 题目 3：JSON.parse(JSON.stringify()) 有什么缺陷？

**答案要点：**

```
1. 不能处理的类型：
   - Function（丢失）
   - undefined（丢失）
   - Symbol（丢失）
   - Date（变为字符串）
   - RegExp（变为空对象）
   - Map、Set（丢失）
   - NaN、Infinity（变为 null）

2. 其他问题：
   - 循环引用报错
   - 忽略不可枚举属性
   - 忽略原型链
   - 性能在大数据量下较差
```

### 题目 4：如何处理循环引用的深拷贝？

**答案要点：**

```javascript
// 使用 WeakMap 存储已拷贝的对象
function deepCloneWithCircular(source, hash = new WeakMap()) {
  if (typeof source !== 'object' || source === null) {
    return source;
  }
  
  // 检查是否已经拷贝过（处理循环引用）
  if (hash.has(source)) {
    return hash.get(source);
  }
  
  const target = Array.isArray(source) ? [] : {};
  
  // 先保存到 hash，再递归
  hash.set(source, target);
  
  for (const key in source) {
    if (Object.prototype.hasOwnProperty.call(source, key)) {
      target[key] = deepCloneWithCircular(source[key], hash);
    }
  }
  
  return target;
}
```

**核心思路：**
- 使用 `WeakMap` 以「原对象 → 拷贝对象」的映射存储
- 在递归之前先保存映射关系，检测到循环引用时直接返回
- `WeakMap` 不会阻止垃圾回收，内存友好

---

## 八、总结与速查表

### 核心概念速查表

| 概念 | 定义 | 性能 | 数据隔离 |
|------|------|------|---------|
| **直接赋值** | 复制引用，不创建新对象 | ⭐⭐⭐⭐⭐ | ❌ 无隔离 |
| **浅拷贝** | 复制基本类型值，引用类型共享引用 | ⭐⭐⭐⭐ | ⭐ 顶层隔离 |
| **深拷贝** | 递归复制所有层级，完全独立 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ 完全隔离 |

### 浅拷贝方法速查表

| 方法 | 适用类型 | 语法 | 备注 |
|------|---------|------|------|
| `Object.assign()` | 对象 | `Object.assign({}, obj)` | 多对象合并 |
| `{ ...obj }` | 对象/数组 | `{ ...obj }` | 最简洁 |
| `arr.slice()` | 数组 | `arr.slice()` | 数组专用 |
| `arr.concat()` | 数组 | `[].concat(arr)` | 合并+拷贝 |

### 深拷贝方法速查表

| 方法 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| `JSON.parse(JSON.stringify())` | 纯 JSON 数据 | 简单快速 | 丢失类型 |
| `structuredClone()` | 现代浏览器 | 原生支持，类型全 | 不支持 Function |
| 手写递归函数 | 自定义需求 | 灵活可控 | 实现复杂 |
| lodash `cloneDeep` | 通用场景 | 功能最完善 | 需要引入依赖 |

### 最佳实践清单

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    最佳实践清单                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ✅ 推荐做法：                                                           │
│  □ 明确需求：先判断是需要浅拷贝还是深拷贝                               │
│  □ 优先使用原生方法：{ ...obj } > Object.assign > slice                 │
│  □ 数据是纯 JSON 时使用 JSON.parse(JSON.stringify())                    │
│  □ 现代浏览器优先使用 structuredClone()                                │
│  □ 复杂场景使用 lodash cloneDeep                                       │
│  □ 处理循环引用时使用 WeakMap                                          │
│  □ 对大型数据进行性能测试                                              │
│                                                                         │
│  ❌ 避免做法：                                                           │
│  □ 不必要的深拷贝（影响性能）                                          │
│  □ 忽略循环引用（导致栈溢出）                                          │
│  □ 用 JSON 方式拷贝含特殊类型的对象                                    │
│  □ 在循环中频繁拷贝大型对象                                            │
│  □ 直接修改引用数据（绕过状态管理）                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 记忆口诀

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    记忆口诀                                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  深浅拷贝看引用：                                                       │
│  • 浅拷贝：基本类型复制值，引用类型复制引用                             │
│  • 深拷贝：所有类型都复制值，完全独立无关联                             │
│                                                                         │
│  选择策略：                                                              │
│  • 简单结构用浅拷贝，{ ...obj } 最常用                                  │
│  • 纯数据用 JSON，一行代码搞定                                          │
│  • 复杂对象用递归，特殊类型要单独处理                                   │
│  • 现代浏览器用 structuredClone，原生支持类型全                         │
│                                                                         │
│  注意事项：                                                              │
│  • 循环引用用 WeakMap，防止死循环和栈溢出                               │
│  • 特殊类型（Date/RegExp）要特殊处理                                    │
│  • 性能敏感场景要测量，避免不必要的深拷贝                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 附录：完整工具函数

### 通用深拷贝工具库

```javascript
/**
 * 通用深拷贝工具函数库
 * 支持：基本类型、Object、Array、Date、RegExp、Map、Set、循环引用
 */
const DeepCloneUtils = {
  /**
   * 深拷贝
   */
  clone(source) {
    return this._deepClone(source, new WeakMap());
  },
  
  /**
   * 内部递归方法
   */
  _deepClone(source, hash) {
    // 基本类型
    if (typeof source !== 'object' || source === null) {
      return source;
    }
    
    // 循环引用
    if (hash.has(source)) {
      return hash.get(source);
    }
    
    // 特殊类型处理
    if (source instanceof Date) {
      return new Date(source.getTime());
    }
    
    if (source instanceof RegExp) {
      return new RegExp(source.source, source.flags);
    }
    
    if (source instanceof Map) {
      const mapCopy = new Map();
      source.forEach((value, key) => {
        mapCopy.set(
          this._deepClone(key, hash),
          this._deepClone(value, hash)
        );
      });
      return mapCopy;
    }
    
    if (source instanceof Set) {
      const setCopy = new Set();
      source.forEach(value => {
        setCopy.add(this._deepClone(value, hash));
      });
      return setCopy;
    }
    
    // 普通对象/数组
    const isArray = Array.isArray(source);
    const target = isArray ? [] : {};
    
    hash.set(source, target);
    
    // 拷贝可枚举属性
    for (const key in source) {
      if (Object.prototype.hasOwnProperty.call(source, key)) {
        target[key] = this._deepClone(source[key], hash);
      }
    }
    
    // 拷贝 Symbol 属性
    const symbolKeys = Object.getOwnPropertySymbols(source);
    symbolKeys.forEach(sym => {
      target[sym] = this._deepClone(source[sym], hash);
    });
    
    return target;
  },
  
  /**
   * 浅拷贝
   */
  shallowClone(source) {
    if (typeof source !== 'object' || source === null) {
      return source;
    }
    
    const target = Array.isArray(source) ? [] : {};
    
    for (const key in source) {
      if (Object.prototype.hasOwnProperty.call(source, key)) {
        target[key] = source[key];
      }
    }
    
    return target;
  }
};

// 使用示例
const original = {
  name: 'Alice',
  birthDate: new Date('1990-01-01'),
  contacts: new Map([['email', 'alice@example.com']]),
  tags: new Set(['developer', 'frontend']),
  hobbies: ['reading', 'coding'],
  profile: {
    city: 'Beijing',
    website: 'https://example.com'
  }
};

// 深拷贝
const deepCopy = DeepCloneUtils.clone(original);
console.log(deepCopy.birthDate instanceof Date); // true
console.log(deepCopy.contacts instanceof Map); // true
console.log(deepCopy.tags instanceof Set); // true
console.log(deepCopy.profile === original.profile); // false ✅

// 浅拷贝
const shallowCopy = DeepCloneUtils.shallowClone(original);
console.log(shallowCopy.profile === original.profile); // true（共享引用）
```

---

> **文档版本**：v1.0  
> **适用版本**：JavaScript（ES6+）  
> **最后更新**：2026-08  
> **参考来源**：MDN Web Docs、lodash 文档