# JavaScript 数组操作 API 详解

> 本文档全面覆盖 JavaScript 数组的创建、属性、增删改查、遍历、搜索、排序、转换、ES6+ 新方法及实战工具函数，每个 API 均包含语法、参数、返回值、代码示例与注意事项。

---

## 目录

- [一、数组创建](#一数组创建)
  - [1.1 字面量创建](#11-字面量创建)
  - [1.2 Array 构造函数](#12-array-构造函数)
  - [1.3 Array.of()](#13-arrayof)
  - [1.4 Array.from()](#14-arrayfrom)
  - [1.5 Array.fromAsync()](#15-arrayfromasync)
- [二、数组属性](#二数组属性)
  - [2.1 length](#21-length)
- [三、增删改查方法（会修改原数组）](#三增删改查方法会修改原数组)
  - [3.1 push()](#31-push)
  - [3.2 pop()](#32-pop)
  - [3.3 unshift()](#33-unshift)
  - [3.4 shift()](#34-shift)
  - [3.5 splice()](#35-splice)
  - [3.6 fill()](#36-fill)
  - [3.7 copyWithin()](#37-copywithin)
- [四、拼接与截取](#四拼接与截取)
  - [4.1 concat()](#41-concat)
  - [4.2 slice()](#42-slice)
  - [4.3 flat()](#43-flat)
  - [4.4 flatMap()](#44-flatmap)
- [五、遍历方法](#五遍历方法)
  - [5.1 forEach()](#51-foreach)
  - [5.2 map()](#52-map)
  - [5.3 filter()](#53-filter)
  - [5.4 reduce()](#54-reduce)
  - [5.5 reduceRight()](#55-reduceright)
  - [5.6 entries() / keys() / values()](#56-entries--keys--values)
- [六、搜索方法](#六搜索方法)
  - [6.1 indexOf() / lastIndexOf()](#61-indexof--lastindexof)
  - [6.2 find() / findIndex() / findLast() / findLastIndex()](#62-find--findindex--findlast--findlastindex)
  - [6.3 includes()](#63-includes)
  - [6.4 some() / every()](#64-some--every)
- [七、排序与翻转](#七排序与翻转)
  - [7.1 sort()](#71-sort)
  - [7.2 reverse()](#72-reverse)
  - [7.3 toSorted() / toReversed()](#73-tosorted--toreversed)
- [八、转换方法](#八转换方法)
  - [8.1 join()](#81-join)
  - [8.2 toString()](#82-tostring)
  - [8.3 toLocaleString()](#83-tolocalestring)
- [九、ES6+ 新增方法](#九es6-新增方法)
  - [9.1 Array.isArray()](#91-arrayisarray)
  - [9.2 扩展运算符 ...](#92-扩展运算符-)
  - [9.3 at()](#93-at)
  - [9.4 Array.from() 进阶](#94-arrayfrom-进阶)
  - [9.5 group() / groupToMap()](#95-group--grouptomap)
- [十、实战工具函数](#十实战工具函数)
- [十一、高频面试题](#十一高频面试题)

---

# 一、数组创建

## 1.1 字面量创建

**语法**

```js
const arr = [元素1, 元素2, ...];
```

**说明**

最常用的创建方式，直接用方括号包裹元素，逗号分隔。

**示例**

```js
const fruits = ['apple', 'banana', 'orange'];
const mixed = [1, 'hello', true, null, { name: 'Tom' }, [1, 2, 3]];
const empty = [];
```

**注意**

- 不要在元素列表末尾留多余的逗号，否则在不同浏览器中行为不一致。
- `const arr = [1, 2, 3,]` 在 ES5 中可能创建长度为 4 的数组（trailing comma）。

---

## 1.2 Array 构造函数

**语法**

```js
new Array(元素1, 元素2, ...);
new Array(length);
Array(元素1, 元素2, ...);  // 可省略 new
```

**参数**

| 参数 | 说明 |
|---|---|
| `元素1, 元素2, ...` | 直接指定数组元素 |
| `length` | 只传一个数字时，创建指定长度的空数组 |

**返回值**

新创建的 Array 实例。

**示例**

```js
// 方式 1：直接指定元素
const arr1 = new Array(1, 2, 3);        // [1, 2, 3]
const arr2 = Array('a', 'b', 'c');      // ['a', 'b', 'c']

// 方式 2：指定长度（不常用）
const arr3 = new Array(5);               // [empty × 5]，长度 5 但没有元素
const arr4 = new Array(3).fill(0);       // [0, 0, 0]（配合 fill 初始化）

// ⚠️ 只传一个数字 → 创建长度，不是单元素数组！
const trap = new Array(5);               // [empty × 5]，不是 [5]
```

**注意**

- `new Array(5)` 创建的是长度为 5 的空数组（holes），不是包含 `5` 的数组。
- 避免坑：想要创建单元素数组用 `Array.of(5)`。

---

## 1.3 Array.of()

**语法**

```js
Array.of(元素0, 元素1, ...);
```

**说明**

ES6 新增。与 `Array` 构造函数的区别：**不管传几个参数，都作为数组元素**，不会把单个数字当长度。

**示例**

```js
Array.of(5);              // [5]  ← 区别于 new Array(5) → [empty × 5]
Array.of(1, 2, 3);        // [1, 2, 3]
Array.of('hello');        // ['hello']
Array.of(undefined);      // [undefined]
```

**注意**

- 解决了 `new Array(5)` 的坑，语义更清晰。
- 适合需要把单个值包装成数组的场景。

---

## 1.4 Array.from()

**语法**

```js
Array.from(arrayLike, mapFn?, thisArg?);
```

**参数**

| 参数 | 说明 |
|---|---|
| `arrayLike` | 类数组对象或可迭代对象（String、Set、Map、NodeList、arguments） |
| `mapFn` | 可选，对每个元素执行的映射函数 |
| `thisArg` | 可选，mapFn 中的 this |

**返回值**

新的 Array 实例。

**示例**

```js
// 1. 字符串 → 数组
Array.from('hello');             // ['h', 'e', 'l', 'l', 'o']

// 2. Set → 数组（数组去重）
const set = new Set([1, 2, 2, 3, 3, 3]);
Array.from(set);                  // [1, 2, 3]

// 3. arguments → 数组
function sum() {
  const args = Array.from(arguments);
  return args.reduce((a, b) => a + b, 0);
}
sum(1, 2, 3);                     // 6

// 4. NodeList → 数组
const divs = document.querySelectorAll('div');
Array.from(divs).forEach(d => console.log(d.tagName));

// 5. 带映射函数
Array.from([1, 2, 3], x => x * 2);        // [2, 4, 6]
Array.from({ length: 5 }, (_, i) => i);    // [0, 1, 2, 3, 4]

// 6. 生成序列
Array.from({ length: 10 }, (_, i) => i + 1);  // [1, 2, 3, ..., 10]
```

**注意**

- `Array.from({ length: 5 })` 创建长度 5 的数组，元素是 `undefined`（不是 holes）。
- 与 `new Array(5)` 的区别：`Array.from` 的结果可以被 `map`/`forEach` 遍历。

---

## 1.5 Array.fromAsync()

**语法**

```js
Array.fromAsync(asyncIterable);
```

**说明**

ES2024 新增。将异步可迭代对象转为 Promise，resolve 后得到数组。

**示例**

```js
async function* asyncGen() {
  yield 1;
  yield 2;
  yield 3;
}

const arr = await Array.fromAsync(asyncGen());  // [1, 2, 3]
```

---

# 二、数组属性

## 2.1 length

**语法**

```js
arr.length;          // 读取
arr.length = 新长度;  // 写入
```

**说明**

返回或设置数组的长度（uint32）。设置小于当前长度时，**从末尾截断数组**。

**示例**

```js
const arr = [1, 2, 3, 4, 5];
console.log(arr.length);   // 5

// 截断
arr.length = 3;
console.log(arr);          // [1, 2, 3]

// 清空数组
arr.length = 0;
console.log(arr);          // []

// 扩展（产生 holes）
arr.length = 5;
console.log(arr);          // [empty × 5]
```

**注意**

- 修改 `length` 是直接操作原数组。
- 用 `arr.length = 0` 清空数组比 `arr = []` 更彻底（同一引用的对象都能感知）。
- 扩大 `length` 会产生 holes，不能被 `map` 等遍历到。

---

# 三、增删改查方法（会修改原数组）

## 3.1 push()

**语法**

```js
arr.push(元素1, ..., 元素N);
```

**参数**

要添加到数组末尾的一个或多个元素。

**返回值**

添加后数组的**新长度**。

**示例**

```js
const arr = [1, 2];
const len = arr.push(3, 4);

console.log(len);    // 4（返回新长度）
console.log(arr);    // [1, 2, 3, 4]（修改原数组）

// 合并两个数组（注意：这样会变成嵌套）
arr.push([5, 6]);
console.log(arr);    // [1, 2, 3, 4, [5, 6]]

// 正确合并
arr.push(...[5, 6]); // 用扩展运算符
```

**注意**

- **修改原数组**，不创建新数组。
- 返回值是长度，不是新数组（链式调用要小心）。
- 性能：`push` 是 O(1) 均摊，比 `unshift` 快很多。

---

## 3.2 pop()

**语法**

```js
arr.pop();
```

**返回值**

被移除的最后一个元素；空数组返回 `undefined`。

**示例**

```js
const arr = [1, 2, 3];
const last = arr.pop();

console.log(last);   // 3
console.log(arr);     // [1, 2]

// 空数组
const empty = [];
empty.pop();          // undefined
```

**注意**

- **修改原数组**。
- 空数组 `pop()` 返回 `undefined`，不报错。

---

## 3.3 unshift()

**语法**

```js
arr.unshift(元素1, ..., 元素N);
```

**返回值**

添加后数组的新长度。

**示例**

```js
const arr = [3, 4];
arr.unshift(1, 2);

console.log(arr);   // [1, 2, 3, 4]
```

**注意**

- **修改原数组**。
- 性能：`unshift` 需要把所有现有元素后移，O(n)。
- 多个参数时，按参数顺序插入（不是反序）：
  ```js
  [4].unshift(1, 2, 3);  // [1, 2, 3, 4]，不是 [3, 2, 1, 4]
  ```

---

## 3.4 shift()

**语法**

```js
arr.shift();
```

**返回值**

被移除的第一个元素；空数组返回 `undefined`。

**示例**

```js
const arr = [1, 2, 3];
const first = arr.shift();

console.log(first);  // 1
console.log(arr);     // [2, 3]
```

**注意**

- **修改原数组**。
- 性能：O(n)，所有元素前移。
- 用 `push` + `shift` 可以实现 FIFO 队列。

---

## 3.5 splice()

**语法**

```js
arr.splice(start, deleteCount?, item1?, ..., itemN?);
```

**参数**

| 参数 | 说明 |
|---|---|
| `start` | 开始修改的索引（负数从末尾算，`-1` = 最后一个） |
| `deleteCount` | 可选，要删除的元素数量。省略则删到末尾 |
| `item1, ..., itemN` | 可选，在 `start` 位置插入的元素 |

**返回值**

被删除的元素组成的数组。没有删除则返回空数组 `[]`。

**示例**

```js
const arr = [1, 2, 3, 4, 5];

// 1. 删除：从索引 1 删 2 个
arr.splice(1, 2);             // 返回 [2, 3]，arr 变 [1, 4, 5]

// 2. 插入：在索引 1 插入，deleteCount = 0
arr.splice(1, 0, 'a', 'b');   // 返回 []，arr 变 [1, 'a', 'b', 4, 5]

// 3. 替换：删 1 个同时插 2 个
arr.splice(1, 1, 'x', 'y');   // 返回 ['a']，arr 变 [1, 'x', 'y', 'b', 4, 5]

// 4. 清空：从 0 删到末尾
arr.splice(0);                 // 返回 [1, 'x', 'y', 'b', 4, 5]，arr 变 []

// 5. 负数索引
const arr2 = [1, 2, 3, 4, 5];
arr2.splice(-2);               // 返回 [4, 5]，arr2 变 [1, 2, 3]

// 6. 不传 deleteCount → 删到末尾
[1, 2, 3, 4].splice(2);       // 返回 [3, 4]
```

**注意**

- **修改原数组**。
- 最灵活的数组方法：可以实现增、删、改三种操作。
- `splice` 是 O(n) 操作。

---

## 3.6 fill()

**语法**

```js
arr.fill(value, start?, end?);
```

**参数**

| 参数 | 说明 |
|---|---|
| `value` | 填充值 |
| `start` | 可选，起始索引（默认 0） |
| `end` | 可选，结束索引（不含，默认 `arr.length`） |

**返回值**

修改后的原数组。

**示例**

```js
// 1. 全部填充
[1, 2, 3, 4].fill(0);              // [0, 0, 0, 0]

// 2. 部分填充
[1, 2, 3, 4, 5].fill(0, 1, 3);     // [1, 0, 0, 4, 5]

// 3. 初始化数组
new Array(5).fill(0);               // [0, 0, 0, 0, 0]
new Array(3).fill('').map(() => 'x'); // ['x', 'x', 'x']

// 4. ⚠️ 引用类型坑
const arr = new Array(3).fill({});   // [{}, {}, {}]
arr[0].name = 'Tom';
console.log(arr);                    // [{name:'Tom'}, {name:'Tom'}, {name:'Tom'}]
// 三个元素指向同一个对象！
```

**注意**

- **修改原数组**。
- ⚠️ `fill({})` 填充的是同一个对象引用，修改一个会影响全部。
- 正确初始化对象数组：`Array.from({ length: 3 }, () => ({}))`。

---

## 3.7 copyWithin()

**语法**

```js
arr.copyWithin(target, start?, end?);
```

**参数**

| 参数 | 说明 |
|---|---|
| `target` | 复制到的目标位置 |
| `start` | 可选，复制起始位置（默认 0） |
| `end` | 可选，复制结束位置（不含，默认 `arr.length`） |

**返回值**

修改后的原数组。

**示例**

```js
[1, 2, 3, 4, 5].copyWithin(0, 3);    // [4, 5, 3, 4, 5]
// 把索引 3~末尾 [4,5] 复制到索引 0 位置

[1, 2, 3, 4, 5].copyWithin(1, 3, 5); // [1, 4, 5, 4, 5]
// 把索引 3~5 [4,5] 复制到索引 1 位置
```

**注意**

- **修改原数组**，不改变长度。
- 较少使用，主要在需要高性能内存操作的场景。

---

# 四、拼接与截取

## 4.1 concat()

**语法**

```js
arr.concat(值1, 值2, ..., 值N);
```

**参数**

要拼接的值，可以是数组或普通值。如果是数组，会展开一层。

**返回值**

**新数组**，不修改原数组。

**示例**

```js
const arr1 = [1, 2];
const arr2 = [3, 4];

// 1. 合并数组
const merged = arr1.concat(arr2);    // [1, 2, 3, 4]
console.log(arr1);                    // [1, 2]（原数组不变）

// 2. 合并多个值
arr1.concat(arr2, 5, 6);             // [1, 2, 3, 4, 5, 6]

// 3. 合并嵌套数组（只展开一层）
arr1.concat([3, [4, 5]]);            // [1, 2, 3, [4, 5]]

// 4. 用扩展运算符替代
const merged2 = [...arr1, ...arr2];   // [1, 2, 3, 4]
```

**注意**

- **不修改原数组**，返回新数组。
- 只展平一层嵌套。
- ES6+ 推荐用扩展运算符 `[...arr1, ...arr2]`。

---

## 4.2 slice()

**语法**

```js
arr.slice(start?, end?);
```

**参数**

| 参数 | 说明 |
|---|---|
| `start` | 可选，起始索引（默认 0，负数从末尾算） |
| `end` | 可选，结束索引（不含，默认 `arr.length`） |

**返回值**

**新数组**，包含从 `start` 到 `end`（不含）的元素。

**示例**

```js
const arr = [1, 2, 3, 4, 5];

// 1. 基本截取
arr.slice(1, 3);      // [2, 3]
arr.slice(2);           // [3, 4, 5]（从索引 2 到末尾）

// 2. 负数索引
arr.slice(-2);          // [4, 5]（最后 2 个）
arr.slice(-3, -1);      // [3, 4]

// 3. 浅拷贝
const copy = arr.slice();  // [1, 2, 3, 4, 5]

// 4. 空参数
arr.slice();            // [1, 2, 3, 4, 5]（浅拷贝）
arr.slice(undefined, 2); // [1, 2]
```

**注意**

- **不修改原数组**。
- 是浅拷贝：元素是对象时，拷贝的是引用。
- `slice()` 不传参数 = 浅拷贝数组。

---

## 4.3 flat()

**语法**

```js
arr.flat(depth?);
```

**参数**

| 参数 | 说明 |
|---|---|
| `depth` | 可选，展平深度（默认 1）。传 `Infinity` 全部展平 |

**返回值**

展平后的新数组。

**示例**

```js
// 1. 默认展平 1 层
[1, [2, [3, [4]]]].flat();           // [1, 2, [3, [4]]]

// 2. 指定深度
[1, [2, [3, [4]]]].flat(2);          // [1, 2, 3, [4]]

// 3. 全部展平
[1, [2, [3, [4]]]].flat(Infinity);    // [1, 2, 3, 4]

// 4. 移除空元素（holes）
[1, , 3, , 5].flat();                 // [1, 3, 5]（空位被移除）

// 5. 实战：拍平 JSON 结构
const data = [
  { id: 1, children: [{ id: 2 }, { id: 3 }] },
  { id: 4, children: [{ id: 5 }] }
];
data.flatMap(d => [d, ...d.children]);  // [{id:1}, {id:2}, {id:3}, {id:4}, {id:5}]
```

**注意**

- **不修改原数组**。
- 会移除 holes（空位），但不会移除 `undefined` 元素。
- 深度不确定时用 `Infinity`。

---

## 4.4 flatMap()

**语法**

```js
arr.flatMap(callback, thisArg?);
```

**参数**

| 参数 | 说明 |
|---|---|
| `callback(element, index, array)` | 对每个元素执行的映射函数，返回数组或值 |
| `thisArg` | 可选，callback 中的 this |

**返回值**

先 map 再 flat(1) 后的新数组。

**示例**

```js
// 1. 等价于 map + flat
[1, 2, 3].flatMap(x => [x, x * 2]);
// [1, 2, 2, 4, 3, 6]

// 2. 过滤 + 映射（一步完成）
const arr = [1, -2, 3, -4, 5];
arr.flatMap(n => n > 0 ? [n] : []);   // [1, 3, 5]

// 3. 拆分字符串
['hello world', 'foo bar'].flatMap(s => s.split(' '));
// ['hello', 'world', 'foo', 'bar']

// 4. 提取嵌套属性
const orders = [
  { id: 1, items: ['A', 'B'] },
  { id: 2, items: ['C'] },
  { id: 3, items: [] }
];
orders.flatMap(o => o.items);  // ['A', 'B', 'C']
```

**注意**

- 等价于 `arr.map(fn).flat(1)`，但效率更高（只遍历一次）。
- 只展平一层，不能指定深度。
