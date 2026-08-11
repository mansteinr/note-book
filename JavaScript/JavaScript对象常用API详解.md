# JavaScript 对象常用 API 详解

---

## 目录

- [1. 对象创建](#1-对象创建)
  - [1.1 Object.create()](#11-objectcreate)
  - [1.2 Object.assign()](#12-objectassign)
  - [1.3 对象字面量](#13-对象字面量)
  - [1.4 new Object()](#14-new-object)
- [2. 属性访问与操作](#2-属性访问与操作)
  - [2.1 点号与方括号访问](#21-点号与方括号访问)
  - [2.2 Object.defineProperty()](#22-objectdefineproperty)
  - [2.3 Object.defineProperties()](#23-objectdefineproperties)
  - [2.4 Object.getOwnPropertyDescriptor()](#24-objectgetownpropertydescriptor)
  - [2.5 Object.getOwnPropertyDescriptors()](#25-objectgetownpropertydescriptors)
- [3. 属性遍历](#3-属性遍历)
  - [3.1 Object.keys()](#31-objectkeys)
  - [3.2 Object.values()](#32-objectvalues)
  - [3.3 Object.entries()](#33-objectentries)
  - [3.4 Object.getOwnPropertyNames()](#34-objectgetownpropertynames)
  - [3.5 Object.getOwnPropertySymbols()](#35-objectgetownpropertysymbols)
  - [3.6 for...in 循环](#36-forin-循环)
- [4. 对象合并与克隆](#4-对象合并与克隆)
  - [4.1 Object.assign() 合并](#41-objectassign-合并)
  - [4.2 展开运算符 ...](#42-展开运算符-)
  - [4.3 浅拷贝 vs 深拷贝](#43-浅拷贝-vs-深拷贝)
- [5. 原型相关](#5-原型相关)
  - [5.1 Object.getPrototypeOf()](#51-objectgetprototypeof)
  - [5.2 Object.setPrototypeOf()](#52-objectsetprototypeof)
  - [5.3 Object.prototype.isPrototypeOf()](#53-objectprototypeisprototypeof)
  - [5.4 instanceof 操作符](#54-instanceof-操作符)
- [6. 对象保护机制](#6-对象保护机制)
  - [6.1 Object.preventExtensions()](#61-objectpreventextensions)
  - [6.2 Object.isExtensible()](#62-objectisextensible)
  - [6.3 Object.seal()](#63-objectseal)
  - [6.4 Object.isSealed()](#64-objectissealed)
  - [6.5 Object.freeze()](#65-objectfreeze)
  - [6.6 Object.isFrozen()](#66-objectisfrozen)
- [7. 其他实用方法](#7-其他实用方法)
  - [7.1 Object.is()](#71-objectis)
  - [7.2 Object.fromEntries()](#72-objectfromentries)
  - [7.3 Object.prototype.hasOwnProperty()](#73-objectprototypehasownproperty)
  - [7.4 Object.prototype.toString()](#74-objectprototypetostring)
  - [7.5 Object.prototype.valueOf()](#75-objectprototypevalueof)
  - [7.6 Object.hasOwn()](#76-objecthasown)
- [8. 属性描述符详解](#8-属性描述符详解)
  - [8.1 数据描述符](#81-数据描述符)
  - [8.2 访问器描述符](#82-访问器描述符)
  - [8.3 描述符共享键](#83-描述符共享键)
- [9. 常见面试题与实战场景](#9-常见面试题与实战场景)
  - [9.1 如何判断一个对象为空？](#91-如何判断一个对象为空)
  - [9.2 深拷贝的实现方式](#92-深拷贝的实现方式)
  - [9.3 如何实现对象的不可变性？](#93-如何实现对象的不可变性)
  - [9.4 遍历对象的多种方式对比](#94-遍历对象的多种方式对比)

---

## 1. 对象创建

### 1.1 Object.create()

**语法**：
```javascript
Object.create(proto, propertiesObject?)
```

**说明**：使用指定的原型对象和可选的属性描述符创建一个新对象。

**参数**：
- `proto`：新对象的原型对象，可以为 `null`
- `propertiesObject`（可选）：属性描述符对象，格式同 `Object.defineProperties()`

**返回值**：一个新对象，其原型为 `proto`，并带有指定的属性

**示例**：
```javascript
// 以 null 为原型创建对象（纯净对象，无任何继承属性）
const pureObj = Object.create(null);
console.log(pureObj.toString); // undefined

// 以指定对象为原型
const person = {
  name: '张三',
  sayHello() {
    console.log(`你好，我是${this.name}`);
  }
};

const student = Object.create(person, {
  grade: {
    value: '三年级',
    writable: true,
    enumerable: true,
    configurable: true
  },
  school: {
    value: '第一小学',
    enumerable: true
  }
});

console.log(student.name);      // 张三（继承自原型）
console.log(student.grade);     // 三年级
student.sayHello();             // 你好，我是张三
console.log(Object.getPrototypeOf(student) === person); // true
```

---

### 1.2 Object.assign()

**语法**：
```javascript
Object.assign(target, ...sources)
```

**说明**：将一个或多个源对象的所有**可枚举自有属性**复制到目标对象，返回目标对象。

**参数**：
- `target`：目标对象，会被修改
- `sources`：一个或多个源对象

**返回值**：修改后的目标对象

**示例**：
```javascript
// 基本合并
const obj1 = { a: 1, b: 2 };
const obj2 = { b: 3, c: 4 };
const result = Object.assign(obj1, obj2);
console.log(result);  // { a: 1, b: 3, c: 4 }
console.log(obj1);    // { a: 1, b: 3, c: 4 }（目标对象被修改）

// 多个源对象
const o1 = { x: 1 };
const o2 = { y: 2 };
const o3 = { z: 3 };
const merged = Object.assign({}, o1, o2, o3);
console.log(merged);  // { x: 1, y: 2, z: 3 }

// 浅拷贝（只拷贝一层）
const original = {
  name: '张三',
  info: { age: 25, city: '北京' }
};
const copy = Object.assign({}, original);
copy.info.age = 30;
console.log(original.info.age); // 30（嵌套对象被修改）
```

**注意事项**：
- 只拷贝可枚举（`enumerable: true`）的自有属性
- 会调用源对象的 getter 和目标对象的 setter
- 属性相同者，后面的源会覆盖前面的
- 无法正确拷贝 Symbol 属性之外的不可枚举属性

---

### 1.3 对象字面量

**说明**：最常用的对象创建方式，简洁直观。

**示例**：
```javascript
// 基础写法
const user = {
  name: '李四',
  age: 28,
  ['job']: '前端工程师',  // 计算属性名（ES6）
  sayHi() {              // 简写方法（ES6）
    console.log('Hi!');
  }
};

// 简写属性名（ES6）：变量名即属性名
const name = '王五';
const age = 30;
const person = { name, age };
console.log(person);  // { name: '王五', age: 30 }
```

---

### 1.4 new Object()

**说明**：构造函数方式创建对象，等同于字面量 `{}`。

**示例**：
```javascript
const obj = new Object();
obj.name = '赵六';
obj.age = 25;
console.log(obj);  // { name: '赵六', age: 25 }

// new Object() 会根据传入参数返回对应类型
console.log(new Object('hello') instanceof String);   // true
console.log(new Object(123) instanceof Number);       // true
console.log(new Object(true) instanceof Boolean);     // true
```

---

## 2. 属性访问与操作

### 2.1 点号与方括号访问

**说明**：两种访问对象属性的方式，各有适用场景。

**示例**：
```javascript
const obj = {
  name: '张三',
  'my-age': 25,
  123: '数字键'
};

// 点号访问：属性名必须是合法标识符
console.log(obj.name);  // 张三

// 方括号访问：可以包含任意字符、变量、表达式
console.log(obj['my-age']);   // 25
console.log(obj[123]);        // 数字键

const key = 'name';
console.log(obj[key]);        // 张三（变量作属性名）
console.log(obj['na' + 'me']);// 张三（表达式作属性名）
```

**安全访问（可选链 `?.`，ES2020）**：
```javascript
const user = { profile: { name: '小明' } };
console.log(user?.profile?.name);    // 小明
console.log(user?.address?.city);    // undefined（不报错）
console.log(user?.sayHello?.());     // undefined（方法调用安全）
```

---

### 2.2 Object.defineProperty()

**语法**：
```javascript
Object.defineProperty(obj, prop, descriptor)
```

**说明**：在对象上定义一个新属性，或修改现有属性，并返回该对象。

**参数**：
- `obj`：目标对象
- `prop`：属性名（字符串或 Symbol）
- `descriptor`：属性描述符对象（详见第8章）

**返回值**：修改后的对象

**示例**：
```javascript
const person = {};

// 定义数据属性
Object.defineProperty(person, 'name', {
  value: '张三',
  writable: true,      // 可修改
  enumerable: true,    // 可枚举
  configurable: true   // 可删除/可修改描述符
});

// 定义只读属性
Object.defineProperty(person, 'id', {
  value: '001',
  writable: false,     // 不可修改
  enumerable: true,
  configurable: false  // 不可删除
});
person.id = '002';       // 静默失败（严格模式报错）
console.log(person.id);  // 001

// 定义访问器属性（getter/setter）
let _age = 0;
Object.defineProperty(person, 'age', {
  get() {
    console.log('获取 age');
    return _age;
  },
  set(val) {
    console.log(`设置 age 为 ${val}`);
    if (val < 0 || val > 150) {
      throw new RangeError('年龄不合法');
    }
    _age = val;
  },
  enumerable: true,
  configurable: true
});

person.age = 25;   // 设置 age 为 25
console.log(person.age); // 获取 age → 25
```

---

### 2.3 Object.defineProperties()

**语法**：
```javascript
Object.defineProperties(obj, props)
```

**说明**：一次性定义或修改对象的多个属性。

**示例**：
```javascript
const obj = {};
Object.defineProperties(obj, {
  name: {
    value: '张三',
    writable: true,
    enumerable: true
  },
  age: {
    value: 25,
    writable: true,
    enumerable: true
  },
  info: {
    get() {
      return `${this.name}，${this.age}岁`;
    },
    enumerable: true
  }
});

console.log(obj.info);  // 张三，25岁
```

---

### 2.4 Object.getOwnPropertyDescriptor()

**语法**：
```javascript
Object.getOwnPropertyDescriptor(obj, prop)
```

**说明**：返回对象指定自有属性的描述符。

**返回值**：属性描述符对象，或 `undefined`（属性不存在时）

**示例**：
```javascript
const obj = { name: '张三' };

const desc = Object.getOwnPropertyDescriptor(obj, 'name');
console.log(desc);
// {
//   value: '张三',
//   writable: true,
//   enumerable: true,
//   configurable: true
// }

const desc2 = Object.getOwnPropertyDescriptor(obj, 'age');
console.log(desc2);  // undefined
```

---

### 2.5 Object.getOwnPropertyDescriptors()

**语法**：
```javascript
Object.getOwnPropertyDescriptors(obj)
```

**说明**：返回对象所有自有属性的描述符对象（ES2017）。

**示例**：
```javascript
const obj = {
  name: '张三',
  get info() { return `${this.name}`; }
};

const descriptors = Object.getOwnPropertyDescriptors(obj);
console.log(descriptors);
// {
//   name: { value: '张三', writable: true, enumerable: true, configurable: true },
//   info: { get: [Function: get info], set: undefined, enumerable: true, configurable: true }
// }

// 应用场景：配合 Object.create() 实现完整克隆（包含 getter/setter）
const clone = Object.create(
  Object.getPrototypeOf(obj),
  Object.getOwnPropertyDescriptors(obj)
);
```

---

## 3. 属性遍历

### 3.1 Object.keys()

**语法**：
```javascript
Object.keys(obj)
```

**说明**：返回对象所有**可枚举自有属性**的键名数组（ES5）。

**返回值**：字符串数组

**示例**：
```javascript
const obj = { a: 1, b: 2, c: 3 };
Object.defineProperty(obj, 'd', {
  value: 4,
  enumerable: false  // 不可枚举
});

console.log(Object.keys(obj));  // ['a', 'b', 'c']（不含 d）

// 常用：遍历对象
Object.keys(obj).forEach(key => {
  console.log(`${key}: ${obj[key]}`);
});
```

---

### 3.2 Object.values()

**语法**：
```javascript
Object.values(obj)
```

**说明**：返回对象所有**可枚举自有属性**的属性值数组（ES2017）。

**示例**：
```javascript
const obj = { name: '张三', age: 25, job: '前端' };
console.log(Object.values(obj));  // ['张三', 25, '前端']

// 求对象数值属性总和
const scores = { math: 90, english: 85, chinese: 92 };
const total = Object.values(scores).reduce((sum, v) => sum + v, 0);
console.log(total);  // 267
```

---

### 3.3 Object.entries()

**语法**：
```javascript
Object.entries(obj)
```

**说明**：返回对象所有**可枚举自有属性**的 `[key, value]` 对数组（ES2017）。

**示例**：
```javascript
const obj = { name: '张三', age: 25 };
console.log(Object.entries(obj));
// [ ['name', '张三'], ['age', 25] ]

// 配合 for...of 遍历
for (const [key, value] of Object.entries(obj)) {
  console.log(`${key}: ${value}`);
}

// 转换为 Map
const map = new Map(Object.entries(obj));
console.log(map.get('name'));  // 张三
```

---

### 3.4 Object.getOwnPropertyNames()

**语法**：
```javascript
Object.getOwnPropertyNames(obj)
```

**说明**：返回对象所有自有属性的键名数组，**包括不可枚举属性**（但不含 Symbol）。

**示例**：
```javascript
const obj = { a: 1, b: 2 };
Object.defineProperty(obj, 'c', {
  value: 3,
  enumerable: false
});

console.log(Object.keys(obj));                // ['a', 'b']
console.log(Object.getOwnPropertyNames(obj)); // ['a', 'b', 'c']（包含不可枚举）
```

---

### 3.5 Object.getOwnPropertySymbols()

**语法**：
```javascript
Object.getOwnPropertySymbols(obj)
```

**说明**：返回对象所有自有 Symbol 属性的数组。

**示例**：
```javascript
const id = Symbol('id');
const secret = Symbol('secret');
const obj = {
  name: '张三',
  [id]: '001'
};
Object.defineProperty(obj, secret, {
  value: '保密数据',
  enumerable: false
});

console.log(Object.keys(obj));                      // ['name']
console.log(Object.getOwnPropertySymbols(obj));     // [ Symbol(id), Symbol(secret) ]
console.log(obj[id]);       // 001
console.log(obj[secret]);   // 保密数据
```

---

### 3.6 for...in 循环

**说明**：遍历对象所有**可枚举属性**，包括**原型链上**的属性。

**示例**：
```javascript
const parent = { inherited: '继承属性' };
const child = Object.create(parent);
child.own = '自有属性';

for (const key in child) {
  console.log(key); // own → inherited（包括继承的）
}

// 排除继承属性：配合 hasOwnProperty
for (const key in child) {
  if (Object.prototype.hasOwnProperty.call(child, key)) {
    console.log(key); // 只输出 own
  }
}
```

---

## 4. 对象合并与克隆

### 4.1 Object.assign() 合并

**说明**：详见 1.2 节。常用作浅拷贝和对象合并。

**示例**：
```javascript
// 设置默认配置
const defaults = { theme: 'light', language: 'zh-CN' };
const userConfig = { theme: 'dark' };
const finalConfig = Object.assign({}, defaults, userConfig);
console.log(finalConfig);  // { theme: 'dark', language: 'zh-CN' }
```

---

### 4.2 展开运算符 ...

**说明**：ES6 提供的对象展开语法，简洁直观，等价于 `Object.assign({}, ...)`。

**示例**：
```javascript
// 合并对象
const a = { x: 1, y: 2 };
const b = { y: 3, z: 4 };
const merged = { ...a, ...b };
console.log(merged);  // { x: 1, y: 3, z: 4 }

// 添加属性的同时覆盖
const user = { name: '张三', age: 25 };
const updated = { ...user, age: 26, job: '前端' };
console.log(updated);  // { name: '张三', age: 26, job: '前端' }

// 条件属性（值为 undefined/false 的表达式会被忽略）
const includeAge = true;
const person = {
  name: '李四',
  ...(includeAge && { age: 30 })
};
console.log(person);  // { name: '李四', age: 30 }
```

---

### 4.3 浅拷贝 vs 深拷贝

**浅拷贝**：只复制对象的第一层，嵌套对象仍共享引用。
```javascript
const original = {
  name: '张三',
  address: { city: '北京' }
};

// 浅拷贝方式一：Object.assign()
const copy1 = Object.assign({}, original);

// 浅拷贝方式二：展开运算符
const copy2 = { ...original };

copy1.address.city = '上海';
console.log(original.address.city);  // 上海（原对象被修改）
```

**深拷贝**：完全复制整个对象结构，嵌套对象不共享引用。

**方式一：JSON 序列化（不支持函数、Symbol、循环引用等）**
```javascript
const original = { name: '张三', info: { age: 25 } };
const deepCopy = JSON.parse(JSON.stringify(original));
deepCopy.info.age = 30;
console.log(original.info.age);  // 25（不受影响）

// 缺点示例
const bad = {
  a: undefined,       // 丢失
  b: function() {},   // 丢失
  c: Symbol('s'),     // 丢失
  d: new Date()       // 转为字符串
};
console.log(JSON.parse(JSON.stringify(bad)));
// { d: '2024-01-01T00:00:00.000Z' }（a、b、c 丢失）
```

**方式二：递归实现**
```javascript
function deepClone(obj, hash = new WeakMap()) {
  // 基本类型直接返回
  if (obj === null || typeof obj !== 'object') return obj;
  // 处理循环引用
  if (hash.has(obj)) return hash.get(obj);
  // 处理 Date、RegExp 等特殊对象
  if (obj instanceof Date) return new Date(obj);
  if (obj instanceof RegExp) return new RegExp(obj);
  if (obj instanceof Map) return new Map(deepClone([...obj], hash));
  if (obj instanceof Set) return new Set(deepClone([...obj], hash));
  // 创建新对象
  const clone = Array.isArray(obj) ? [] : {};
  hash.set(obj, clone);
  // 递归拷贝所有属性（包括 Symbol）
  for (const key of [...Object.keys(obj), ...Object.getOwnPropertySymbols(obj)]) {
    clone[key] = deepClone(obj[key], hash);
  }
  return clone;
}

const original = { a: { b: { c: 1 } } };
const cloned = deepClone(original);
cloned.a.b.c = 999;
console.log(original.a.b.c);  // 1
```

---

## 5. 原型相关

### 5.1 Object.getPrototypeOf()

**语法**：
```javascript
Object.getPrototypeOf(obj)
```

**说明**：返回对象的原型（`[[Prototype]]`）。

**示例**：
```javascript
const arr = [1, 2, 3];
console.log(Object.getPrototypeOf(arr) === Array.prototype);    // true
console.log(Object.getPrototypeOf(arr) === Object.getPrototypeOf([])); // true

const obj = {};
console.log(Object.getPrototypeOf(obj) === Object.prototype);  // true

// Object.prototype 的原型是 null（原型链终点）
console.log(Object.getPrototypeOf(Object.prototype));           // null
```

---

### 5.2 Object.setPrototypeOf()

**语法**：
```javascript
Object.setPrototypeOf(obj, proto)
```

**说明**：设置对象的原型（ES6）。**性能较差，尽量避免使用**，推荐用 `Object.create()` 代替。

**示例**：
```javascript
const animal = { type: '动物' };
const cat = { name: '猫咪' };
Object.setPrototypeOf(cat, animal);
console.log(cat.type);  // 动物

// 不推荐：动态修改原型影响性能
```

---

### 5.3 Object.prototype.isPrototypeOf()

**语法**：
```javascript
protoObj.isPrototypeOf(obj)
```

**说明**：判断 `protoObj` 是否存在于 `obj` 的原型链上。

**示例**：
```javascript
const animal = { type: '动物' };
const cat = Object.create(animal);
const kitten = Object.create(cat);

console.log(animal.isPrototypeOf(kitten));   // true
console.log(cat.isPrototypeOf(kitten));      // true
console.log(Object.prototype.isPrototypeOf(kitten)); // true
```

---

### 5.4 instanceof 操作符

**说明**：判断构造函数的 `prototype` 是否出现在对象的原型链上。

**示例**：
```javascript
const arr = [1, 2, 3];
console.log(arr instanceof Array);     // true
console.log(arr instanceof Object);    // true（Array 继承自 Object）

function Person(name) { this.name = name; }
const p = new Person('张三');
console.log(p instanceof Person);      // true
console.log(p instanceof Object);      // true

// 与 typeof 对比
console.log(typeof null);              // 'object'（历史遗留 bug）
console.log(null instanceof Object);   // false（正确）
```

---

## 6. 对象保护机制

> 三种保护级别：**不可扩展 < 密封 < 冻结**，保护范围逐级增强。

### 6.1 Object.preventExtensions()

**语法**：
```javascript
Object.preventExtensions(obj)
```

**说明**：让对象变得不可扩展，即**不能添加新属性**，但可以修改、删除现有属性。

**示例**：
```javascript
const obj = { a: 1 };
Object.preventExtensions(obj);

obj.b = 2;         // 静默失败（严格模式报错）
console.log(obj.b); // undefined

delete obj.a;      // 可删除
console.log(obj.a); // undefined
```

---

### 6.2 Object.isExtensible()

**说明**：判断对象是否可扩展（能否添加新属性）。

```javascript
const obj = {};
console.log(Object.isExtensible(obj));  // true
Object.preventExtensions(obj);
console.log(Object.isExtensible(obj));  // false
```

---

### 6.3 Object.seal()

**语法**：
```javascript
Object.seal(obj)
```

**说明**：密封对象：
- ❌ 不可添加新属性
- ❌ 不可删除现有属性
- ❌ 不可将现有属性在数据属性/访问器属性间转换
- ✅ 可修改现有属性的值
- 本质：给所有属性设置 `configurable: false`，并阻止扩展

**示例**：
```javascript
const obj = { a: 1, b: 2 };
Object.seal(obj);

obj.c = 3;            // ❌ 添加失败
console.log(obj.c);   // undefined

delete obj.a;         // ❌ 删除失败
console.log(obj.a);   // 1

obj.a = 100;          // ✅ 可修改值
console.log(obj.a);   // 100
```

---

### 6.4 Object.isSealed()

**说明**：判断对象是否被密封。

```javascript
const obj = { a: 1 };
console.log(Object.isSealed(obj));  // false
Object.seal(obj);
console.log(Object.isSealed(obj));  // true
```

---

### 6.5 Object.freeze()

**语法**：
```javascript
Object.freeze(obj)
```

**说明**：冻结对象，**最高级别保护**：
- ❌ 不可添加新属性
- ❌ 不可删除现有属性
- ❌ 不可修改现有属性的值
- ❌ 不可修改属性描述符
- 本质：`seal()` + 所有属性 `writable: false`

**示例**：
```javascript
const obj = { a: 1, nested: { b: 2 } };
Object.freeze(obj);

obj.a = 100;      // ❌ 修改失败
console.log(obj.a);  // 1

obj.c = 3;        // ❌ 添加失败
delete obj.a;     // ❌ 删除失败

// ⚠️ 浅冻结：嵌套对象仍可修改
obj.nested.b = 999;
console.log(obj.nested.b);  // 999
```

**深冻结实现**：
```javascript
function deepFreeze(obj) {
  const keys = Object.getOwnPropertyNames(obj);
  const symbols = Object.getOwnPropertySymbols(obj);
  [...keys, ...symbols].forEach(key => {
    const value = obj[key];
    if (value && typeof value === 'object') {
      deepFreeze(value);
    }
  });
  return Object.freeze(obj);
}
```

---

### 6.6 Object.isFrozen()

**说明**：判断对象是否被冻结。

```javascript
const obj = { a: 1 };
console.log(Object.isFrozen(obj));  // false
Object.freeze(obj);
console.log(Object.isFrozen(obj));  // true
```

---

## 7. 其他实用方法

### 7.1 Object.is()

**语法**：
```javascript
Object.is(value1, value2)
```

**说明**：判断两个值是否为**同一个值**（ES6），行为与 `===` 类似，但更精确：
- `NaN` 与 `NaN` 相等
- `+0` 与 `-0` 不相等

**对比示例**：
```javascript
// 相同点
console.log(Object.is(1, 1));           // true
console.log(Object.is('a', 'a'));       // true
console.log(Object.is({}, {}));         // false（引用不同）

// 不同点
console.log(NaN === NaN);               // false
console.log(Object.is(NaN, NaN));       // true ✅

console.log(+0 === -0);                 // true
console.log(Object.is(+0, -0));         // false ✅
```

---

### 7.2 Object.fromEntries()

**语法**：
```javascript
Object.fromEntries(iterable)
```

**说明**：把键值对列表转换为对象，是 `Object.entries()` 的逆操作（ES2019）。

**参数**：可迭代对象，如 `Array`、`Map` 等，每项是 `[key, value]` 对。

**示例**：
```javascript
// 数组 → 对象
const entries = [['name', '张三'], ['age', 25]];
const obj = Object.fromEntries(entries);
console.log(obj);  // { name: '张三', age: 25 }

// Map → 对象
const map = new Map();
map.set('a', 1);
map.set('b', 2);
console.log(Object.fromEntries(map));  // { a: 1, b: 2 }

// 应用：对象过滤
const user = { name: '张三', age: 25, password: '123456' };
const filtered = Object.fromEntries(
  Object.entries(user).filter(([k]) => k !== 'password')
);
console.log(filtered);  // { name: '张三', age: 25 }

// 应用：对象转换
const prices = { apple: 5, banana: 3 };
const doubled = Object.fromEntries(
  Object.entries(prices).map(([k, v]) => [k, v * 2])
);
console.log(doubled);  // { apple: 10, banana: 6 }
```

---

### 7.3 Object.prototype.hasOwnProperty()

**语法**：
```javascript
obj.hasOwnProperty(prop)
```

**说明**：判断对象是否**自有**指定属性（不查原型链）。

**示例**：
```javascript
const parent = { inherited: '继承属性' };
const child = Object.create(parent);
child.own = '自有属性';

console.log(child.hasOwnProperty('own'));         // true
console.log(child.hasOwnProperty('inherited'));   // false（继承自原型）

// 安全调用（防止对象覆盖 hasOwnProperty）
const obj = { hasOwnProperty: 'hello', a: 1 };
// obj.hasOwnProperty('a') 会报错，因为 hasOwnProperty 被覆盖
console.log(Object.prototype.hasOwnProperty.call(obj, 'a')); // true ✅
```

---

### 7.4 Object.prototype.toString()

**说明**：返回对象的字符串表示，常用来精确判断数据类型。

**示例**：
```javascript
const toString = Object.prototype.toString;

console.log(toString.call({}));           // '[object Object]'
console.log(toString.call([]));           // '[object Array]'
console.log(toString.call(function(){})); // '[object Function]'
console.log(toString.call(new Date()));   // '[object Date]'
console.log(toString.call(/abc/));        // '[object RegExp]'
console.log(toString.call(null));         // '[object Null]'
console.log(toString.call(undefined));    // '[object Undefined]'
console.log(toString.call(Symbol()));     // '[object Symbol]'
console.log(toString.call(new Map()));    // '[object Map]'

// 封装类型判断函数
function getType(val) {
  return toString.call(val).slice(8, -1).toLowerCase();
}
console.log(getType([]));      // 'array'
console.log(getType(null));    // 'null'
```

---

### 7.5 Object.prototype.valueOf()

**说明**：返回对象的原始值表示，在类型转换时会被自动调用。

**示例**：
```javascript
const obj = {
  value: 42,
  valueOf() {
    return this.value;
  }
};

console.log(obj + 8);          // 50（自动调用 valueOf）
console.log(Number(obj));      // 42
```

---

### 7.6 Object.hasOwn()

**语法**：
```javascript
Object.hasOwn(obj, prop)
```

**说明**：ES2022 新增，`hasOwnProperty` 的推荐替代版，更安全。

**示例**：
```javascript
const obj = { a: 1 };
const parent = { b: 2 };
Object.setPrototypeOf(obj, parent);

console.log(Object.hasOwn(obj, 'a'));      // true
console.log(Object.hasOwn(obj, 'b'));      // false（继承的）

// 比 hasOwnProperty 安全
const bad = Object.create(null);
bad.a = 1;
// bad.hasOwnProperty('a') 报错（无原型）
console.log(Object.hasOwn(bad, 'a'));      // true ✅
```

---

## 8. 属性描述符详解

### 8.1 数据描述符

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `value` | 任意 | `undefined` | 属性的值 |
| `writable` | Boolean | `false` | 能否修改 `value` |
| `enumerable` | Boolean | `false` | 能否被枚举（`for...in`、`Object.keys()` 等） |
| `configurable` | Boolean | `false` | 能否删除属性、修改描述符、切换为访问器属性 |

**示例**：
```javascript
const obj = {};
Object.defineProperty(obj, 'data', {
  value: 'hello',
  writable: false,
  enumerable: true,
  configurable: false
});
```

---

### 8.2 访问器描述符

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `get` | Function | `undefined` | getter 函数，读取属性时调用 |
| `set` | Function | `undefined` | setter 函数，写入属性时调用 |
| `enumerable` | Boolean | `false` | 能否被枚举 |
| `configurable` | Boolean | `false` | 能否删除属性、修改描述符、切换为数据属性 |

**注意**：`get/set` 不能与 `value/writable` 同时出现。

---

### 8.3 描述符共享键

```javascript
// ❌ 错误：混用数据和访问器描述符
Object.defineProperty({}, 'x', {
  value: 1,
  get() { return 1; }  // 报错！
});

// ✅ 正确：二选一
// 数据描述符 → value + writable
// 访问器描述符 → get + set
```

---

## 9. 常见面试题与实战场景

### 9.1 如何判断一个对象为空？

```javascript
// 方法一：Object.keys()（推荐，兼容性好）
function isEmpty1(obj) {
  return Object.keys(obj).length === 0 && obj.constructor === Object;
}

// 方法二：JSON.stringify()
function isEmpty2(obj) {
  return JSON.stringify(obj) === '{}';
}

// 方法三：Object.getOwnPropertyNames() + Symbol
function isEmpty3(obj) {
  return (
    Object.getOwnPropertyNames(obj).length === 0 &&
    Object.getOwnPropertySymbols(obj).length === 0
  );
}

// 方法四：for...in + hasOwnProperty
function isEmpty4(obj) {
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) return false;
  }
  return true;
}
```

---

### 9.2 深拷贝的实现方式

| 方式 | 优点 | 缺点 |
|---|---|---|
| `JSON.parse(JSON.stringify())` | 简单易用，性能不错 | 丢失函数、Symbol、undefined；Date 转字符串；不支持循环引用 |
| `structuredClone()`（浏览器） | 原生支持，处理循环引用、Date、Map 等 | 不支持函数、Symbol；较新 |
| 递归实现（4.3 节） | 可定制，支持循环引用 | 需手动处理特殊类型（Date、Map、Set 等） |
| `_.cloneDeep()`（Lodash） | 生产级，覆盖全面 | 需要引入第三方库 |

---

### 9.3 如何实现对象的不可变性？

```javascript
// 方式一：Object.freeze() + 深冻结（见 6.5 节）
deepFreeze(obj);

// 方式二：展开运算符创建新对象（函数式风格）
const state = { count: 0, user: { name: '张三' } };
const newState = {
  ...state,
  count: state.count + 1,
  user: { ...state.user, name: '李四' }
};

// 方式三：使用 Immer 库（推荐）
// import produce from 'immer';
// const nextState = produce(state, draft => {
//   draft.count++;
//   draft.user.name = '李四';
// });
```

---

### 9.4 遍历对象的多种方式对比

| 方式 | 自有属性 | 继承属性 | 不可枚举 | Symbol | 适用场景 |
|---|:---:|:---:|:---:|:---:|---|
| `Object.keys()` | ✅ | ❌ | ❌ | ❌ | 遍历可枚举自有键（最常用） |
| `Object.values()` | ✅ | ❌ | ❌ | ❌ | 遍历可枚举自有值 |
| `Object.entries()` | ✅ | ❌ | ❌ | ❌ | 同时遍历键值对 |
| `for...in` | ✅ | ✅ | ❌ | ❌ | 遍历所有可枚举属性（含继承） |
| `getOwnPropertyNames()` | ✅ | ❌ | ✅ | ❌ | 遍历所有自有键（含不可枚举） |
| `getOwnPropertySymbols()` | ❌ | ❌ | ✅ | ✅ | 遍历所有自有 Symbol |
| `Reflect.ownKeys()` | ✅ | ❌ | ✅ | ✅ | 遍历所有自有键（最全） |

---

> 文档版本：v1.0 | 更新日期：2026-08-11
