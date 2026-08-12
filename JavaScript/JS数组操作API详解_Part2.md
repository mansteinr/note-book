# 五、遍历方法

## 5.1 forEach()

**语法**

```js
arr.forEach(callback(element, index, array), thisArg?);
```

**参数**

| 参数 | 说明 |
|---|---|
| `callback` | 每个元素执行的函数 |
| `element` | 当前元素 |
| `index` | 当前索引 |
| `array` | 正在遍历的数组 |
| `thisArg` | 可选，callback 中的 this |

**返回值**

`undefined`。

**示例**

```js
const arr = ['a', 'b', 'c'];

// 1. 基本遍历
arr.forEach((item, index) => {
  console.log(index, item);
});
// 0 'a'
// 1 'b'
// 2 'c'

// 2. 累加
let sum = 0;
[1, 2, 3, 4].forEach(n => sum += n);
console.log(sum);   // 10

// 3. ⚠️ 不能 break / continue
[1, 2, 3, 4, 5].forEach(n => {
  if (n === 3) break;  // ❌ SyntaxError!
});
// 替代：用 for...of + break
for (const n of [1, 2, 3, 4, 5]) {
  if (n === 3) break;
  console.log(n);
}
```

**注意**

- **不返回新数组**，不能链式调用。
- **不能 break / continue / return** 中断。
- **不会跳过 holes**（空位），但不会对 holes 调用 callback。
- 中途不能修改 `arr.length` 来影响遍历次数（遍历开始时已确定）。

---

## 5.2 map()

**语法**

```js
arr.map(callback(element, index, array), thisArg?);
```

**返回值**

**新数组**，每个元素是 callback 的返回值。

**示例**

```js
const arr = [1, 2, 3, 4];

// 1. 映射
arr.map(x => x * 2);              // [2, 4, 6, 8]

// 2. 提取属性
const users = [{ name: 'Tom', age: 20 }, { name: 'Jerry', age: 25 }];
users.map(u => u.name);            // ['Tom', 'Jerry']

// 3. 格式化
[1, 2, 3].map(n => `第${n}名`);    // ['第1名', '第2名', '第3名']

// 4. 返回对象时注意箭头函数语法
[1, 2, 3].map(n => ({ id: n }));  // [{id:1}, {id:2}, {id:3}]（要加括号）
// ❌ [1,2,3].map(n => { id: n })  → 返回 [undefined, undefined, undefined]
// 因为 {} 被解析为函数体块，而不是对象字面量
```

**注意**

- **不修改原数组**（除非 callback 内主动修改）。
- 返回数组长度与原数组相同。
- ⚠️ `map` 会跳过 holes，但保留 holes（不调用 callback）。

---

## 5.3 filter()

**语法**

```js
arr.filter(callback(element, index, array), thisArg?);
```

**返回值**

**新数组**，包含所有使 callback 返回 `true` 的元素。

**示例**

```js
const arr = [1, 2, 3, 4, 5, 6];

// 1. 过滤偶数
arr.filter(n => n % 2 === 0);      // [2, 4, 6]

// 2. 过滤对象
const users = [
  { name: 'Tom', age: 17 },
  { name: 'Jerry', age: 25 },
  { name: 'Spike', age: 15 }
];
users.filter(u => u.age >= 18);    // [{ name: 'Jerry', age: 25 }]

// 3. 去重（配合 indexOf）
const nums = [1, 2, 2, 3, 3, 3, 4];
nums.filter((n, i, arr) => arr.indexOf(n) === i);  // [1, 2, 3, 4]

// 4. 去除 falsy 值
[0, 1, '', 'a', null, undefined, NaN, false, true]
  .filter(Boolean);    // [1, 'a', true]
```

**注意**

- **不修改原数组**。
- 返回数组长度 ≤ 原数组。
- `filter(Boolean)` 是去除 falsy 值的常用技巧。

---

## 5.4 reduce()

**语法**

```js
arr.reduce(callback(accumulator, currentValue, index, array), initialValue?);
```

**参数**

| 参数 | 说明 |
|---|---|
| `accumulator` | 累加器，上一次 callback 的返回值 |
| `currentValue` | 当前元素 |
| `index` | 当前索引 |
| `array` | 正在遍历的数组 |
| `initialValue` | 可选，accumulator 的初始值 |

**返回值**

最终的累加值。

**示例**

```js
const arr = [1, 2, 3, 4, 5];

// 1. 求和
arr.reduce((acc, cur) => acc + cur, 0);           // 15

// 2. 求积
arr.reduce((acc, cur) => acc * cur, 1);           // 120

// 3. 求最大值
arr.reduce((max, cur) => Math.max(max, cur));     // 5

// 4. 数组扁平化（手动实现 flat）
[[1, 2], [3, 4], [5]].reduce((acc, cur) => acc.concat(cur), []);  // [1,2,3,4,5]

// 5. 数组分组
const people = [
  { name: 'Tom', dept: 'eng' },
  { name: 'Jerry', dept: 'sales' },
  { name: 'Spike', dept: 'eng' }
];
people.reduce((groups, p) => {
  (groups[p.dept] = groups[p.dept] || []).push(p);
  return groups;
}, {});
// { eng: [{name:'Tom'...}, {name:'Spike'...}], sales: [{name:'Jerry'...}] }

// 6. 管道函数
const fns = [x => x + 1, x => x * 2, x => x - 3];
const result = fns.reduce((val, fn) => fn(val), 5);   // (5+1)*2-3 = 9

// 7. 计算元素出现次数
['a', 'b', 'a', 'c', 'b', 'a'].reduce((count, char) => {
  count[char] = (count[char] || 0) + 1;
  return count;
}, {});
// { a: 3, b: 2, c: 1 }
```

**注意**

- **不修改原数组**（除非 callback 内修改）。
- ⚠️ **如果不传 `initialValue`**：第一次调用时 `accumulator = arr[0]`，`currentValue = arr[1]`，从索引 1 开始遍历。
- ⚠️ **空数组不传 `initialValue`** 会报 `TypeError: Reduce of empty array with no initial value`。
- 最佳实践：**始终传 `initialValue`**。

---

## 5.5 reduceRight()

**语法**

```js
arr.reduceRight(callback(accumulator, currentValue, index, array), initialValue?);
```

**说明**

与 `reduce` 完全一致，区别是**从右向左**遍历。

**示例**

```js
// 从右到左拼接
['world', 'hello'].reduceRight((acc, cur) => acc + ' ' + cur);
// 'hello world'

// 反转数组（不修改原数组）
[1, 2, 3, 4].reduceRight((acc, cur) => [...acc, cur], []);  // [4, 3, 2, 1]
```

---

## 5.6 entries() / keys() / values()

**语法**

```js
arr.entries();    // 返回 [index, value] 的迭代器
arr.keys();       // 返回 index 的迭代器
arr.values();     // 返回 value 的迭代器
```

**返回值**

Array Iterator 对象。

**示例**

```js
const arr = ['a', 'b', 'c'];

// 1. entries
for (const [index, value] of arr.entries()) {
  console.log(index, value);
}
// 0 'a'
// 1 'b'
// 2 'c'

// 2. keys
for (const index of arr.keys()) {
  console.log(index);
}
// 0
// 1
// 2

// 3. values
for (const value of arr.values()) {
  console.log(value);
}
// a
// b
// c

// 4. 转 Array
const entries = [...arr.entries()];   // [[0,'a'], [1,'b'], [2,'c']]
```

**注意**

- 返回的是 Iterator，不是数组，需要用 `for...of` 或扩展运算符消费。
- `values()` 在 ES2015 规范中曾因兼容性问题被移除，ES2015+ 现代浏览器支持。

---

# 六、搜索方法

## 6.1 indexOf() / lastIndexOf()

**语法**

```js
arr.indexOf(searchElement, fromIndex?);
arr.lastIndexOf(searchElement, fromIndex?);
```

**参数**

| 参数 | 说明 |
|---|---|
| `searchElement` | 要查找的元素 |
| `fromIndex` | 可选，起始索引。`indexOf` 默认 0；`lastIndexOf` 默认 `arr.length - 1` |

**返回值**

找到的索引（从 0 开始）；未找到返回 **-1**。

**示例**

```js
const arr = [1, 2, 3, 2, 1];

arr.indexOf(2);            // 1（第一个 2 的位置）
arr.lastIndexOf(2);        // 3（最后一个 2 的位置）
arr.indexOf(5);            // -1（不存在）

// 从指定位置开始查找
arr.indexOf(2, 2);         // 3（从索引 2 开始找 2）

// 查找对象（⚠️ 严格相等 ===，引用比较）
const obj = { a: 1 };
[{ a: 1 }, obj].indexOf(obj);    // 1（同一引用）
[{ a: 1 }, { a: 1 }].indexOf({ a: 1 });  // -1（不同引用）

// 查找 NaN（⚠️ indexOf 找不到 NaN）
[1, NaN, 3].indexOf(NaN);       // -1（因为 NaN !== NaN）
// 用 includes 可以找到 NaN
[1, NaN, 3].includes(NaN);      // true
```

**注意**

- 使用严格相等 `===`。
- **不能查找 NaN**（因为 `NaN !== NaN`），用 `includes()` 替代。
- `indexOf` 常用于数组去重。

---

## 6.2 find() / findIndex() / findLast() / findLastIndex()

**语法**

```js
arr.find(callback(element, index, array));
arr.findIndex(callback(element, index, array));
arr.findLast(callback(element, index, array));         // ES2023+
arr.findLastIndex(callback(element, index, array));     // ES2023+
```

**返回值**

| 方法 | 返回 |
|---|---|
| `find` | 第一个满足条件的**元素值**；没找到返回 `undefined` |
| `findIndex` | 第一个满足条件的**索引**；没找到返回 `-1` |
| `findLast` | 最后一个满足条件的**元素值** |
| `findLastIndex` | 最后一个满足条件的**索引** |

**示例**

```js
const users = [
  { id: 1, name: 'Tom', age: 20 },
  { id: 2, name: 'Jerry', age: 25 },
  { id: 3, name: 'Spike', age: 20 }
];

// 1. find：找到第一个 age=20 的用户
users.find(u => u.age === 20);       // { id: 1, name: 'Tom', age: 20 }

// 2. findIndex：找到索引
users.findIndex(u => u.name === 'Jerry');  // 1

// 3. findLast：找到最后一个 age=20
users.findLast(u => u.age === 20);   // { id: 3, name: 'Spike', age: 20 }

// 4. findLastIndex
users.findLastIndex(u => u.age === 20);  // 2

// 5. 未找到
users.find(u => u.age > 100);        // undefined
users.findIndex(u => u.age > 100);   // -1
```

**注意**

- **不修改原数组**。
- `find` 适合找对象数组中的元素（`indexOf` 做不到，因为是引用比较）。
- 一旦找到就停止遍历（找到第一个/最后一个后 break）。

---

## 6.3 includes()

**语法**

```js
arr.includes(searchElement, fromIndex?);
```

**返回值**

`true` 或 `false`。

**示例**

```js
[1, 2, 3].includes(2);       // true
[1, 2, 3].includes(4);       // false

// ⭐ 可以找到 NaN（区别于 indexOf）
[1, NaN, 3].includes(NaN);   // true

// 从指定位置
[1, 2, 3, 1].includes(1, 2); // true（从索引 2 开始找到 1）

// 负索引
[1, 2, 3].includes(1, -2);   // false（从倒数第 2 个开始找，只有 [2,3]）
```

**注意**

- **不修改原数组**。
- 使用 SameValueZero 算法（`NaN === NaN`），能正确判断 `NaN`。
- 比 `indexOf() !== -1` 更语义化。

---

## 6.4 some() / every()

**语法**

```js
arr.some(callback(element, index, array));
arr.every(callback(element, index, array));
```

**返回值**

| 方法 | 返回 |
|---|---|
| `some` | 只要有一个元素满足条件就返回 `true`；否则 `false` |
| `every` | 所有元素都满足条件才返回 `true`；否则 `false` |

**示例**

```js
const arr = [1, 2, 3, 4, 5];

// 1. some：是否有偶数
arr.some(n => n % 2 === 0);     // true

// 2. every：是否都是正数
arr.every(n => n > 0);          // true

// 3. 空数组
[].some(fn);                    // false
[].every(fn);                   // true（空数组 every 恒为 true，注意！）

// 4. 实战：表单验证
const form = [
  { field: 'name', value: 'Tom', required: true },
  { field: 'email', value: '', required: true },
  { field: 'phone', value: '13800138000', required: false }
];
const isValid = form.filter(f => f.required).every(f => f.value !== '');
console.log(isValid);   // false（email 为空）
```

**注意**

- **不修改原数组**。
- `some` 遇到第一个 `true` 就停止遍历。
- `every` 遇到第一个 `false` 就停止遍历。
- ⚠️ 空数组 `every` 返回 `true`（逻辑上"所有 0 个元素都满足"为真）。

---

# 七、排序与翻转

## 7.1 sort()

**语法**

```js
arr.sort(compareFn?);
```

**参数**

| 参数 | 说明 |
|---|---|
| `compareFn(a, b)` | 可选，比较函数。返回负数 a 在前；正数 b 在前；0 不变 |

**返回值**

排序后的原数组（引用相同）。

**示例**

```js
// ⚠️ 默认按 Unicode 排序（会出 bug）
[10, 2, 1, 21].sort();          // [1, 10, 2, 21]（字符串比较！）

// ✅ 数字升序
[10, 2, 1, 21].sort((a, b) => a - b);     // [1, 2, 10, 21]

// ✅ 数字降序
[10, 2, 1, 21].sort((a, b) => b - a);     // [21, 10, 2, 1]

// 字符串排序
['banana', 'apple', 'cherry'].sort();     // ['apple', 'banana', 'cherry']

// 字符串不区分大小写
['banana', 'Apple', 'cherry'].sort((a, b) => a.localeCompare(b));
// ['Apple', 'banana', 'cherry']

// 对象数组排序
const users = [
  { name: 'Tom', age: 25 },
  { name: 'Jerry', age: 20 },
  { name: 'Spike', age: 30 }
];
users.sort((a, b) => a.age - b.age);
// [{name:'Jerry',age:20}, {name:'Tom',age:25}, {name:'Spike',age:30}]

// 多条件排序
const data = [
  { dept: 'B', name: 'Tom' },
  { dept: 'A', name: 'Jerry' },
  { dept: 'B', name: 'Anna' },
  { dept: 'A', name: 'Bob' }
];
data.sort((a, b) => {
  if (a.dept !== b.dept) return a.dept.localeCompare(b.dept);
  return a.name.localeCompare(b.name);
});
// 先按 dept 排，dept 相同按 name 排
```

**注意**

- **修改原数组**！
- ⚠️ 默认把元素转为字符串按 Unicode 排序，**数字排序一定要传比较函数**。
- 排序不保证稳定（V8 在 ES2019 后保证稳定）。

---

## 7.2 reverse()

**语法**

```js
arr.reverse();
```

**返回值**

翻转后的原数组。

**示例**

```js
const arr = [1, 2, 3, 4, 5];
arr.reverse();
console.log(arr);   // [5, 4, 3, 2, 1]

// 不修改原数组的翻转
const reversed = [...arr].reverse();
// 或 const reversed = arr.slice().reverse();
```

**注意**

- **修改原数组**。
- 不修改原数组的翻转用 `[...arr].reverse()`。

---

## 7.3 toSorted() / toReversed()

**语法**

```js
arr.toSorted(compareFn?);    // ES2023+
arr.toReversed();              // ES2023+
```

**说明**

ES2023 新增。与 `sort` / `reverse` 功能相同，但**不修改原数组**，返回新数组。

**示例**

```js
const arr = [3, 1, 2];

const sorted = arr.toSorted((a, b) => a - b);
console.log(sorted);   // [1, 2, 3]
console.log(arr);       // [3, 1, 2]（原数组不变）

const reversed = arr.toReversed();
console.log(reversed);  // [2, 1, 3]
console.log(arr);       // [3, 1, 2]（原数组不变）
```

**注意**

- **不修改原数组**（不可变操作，React/函数式编程友好）。
- ES2023 新增，注意浏览器/Node 版本兼容性。

---

# 八、转换方法

## 8.1 join()

**语法**

```js
arr.join(separator?);
```

**参数**

| 参数 | 说明 |
|---|---|
| `separator` | 可选，分隔符（默认逗号 `,`） |

**返回值**

拼接后的字符串。

**示例**

```js
const arr = ['hello', 'world'];

arr.join();           // 'hello,world'
arr.join(' ');        // 'hello world'
arr.join('-');        // 'hello-world'
arr.join('');         // 'helloworld'

// ⚠️ undefined / null 会被转成空字符串
['a', undefined, 'b', null].join('-');   // 'a--b-'

// 实战：CSV 生成
const data = [
  { name: 'Tom', age: 20 },
  { name: 'Jerry', age: 25 }
];
const csv = data.map(r => [r.name, r.age].join(',')).join('\n');
// Tom,20
// Jerry,25

// 实战：重复字符串
const repeat = (str, n) => Array(n).fill(str).join('');
repeat('abc', 3);    // 'abcabcabc'
```

**注意**

- **不修改原数组**。
- `undefined` / `null` 被转为空字符串。
- 空数组 `join` 返回空字符串 `''`。

---

## 8.2 toString()

**语法**

```js
arr.toString();
```

**返回值**

等价于 `arr.join(',')`。

**示例**

```js
[1, 2, 3].toString();       // '1,2,3'
['a', 'b'].toString();      // 'a,b'
[1, [2, [3]]].toString();   // '1,2,3'（递归扁平化后拼接）
```

**注意**

- 等价于 `join(',')`，没有自定义分隔符。

---

## 8.3 toLocaleString()

**语法**

```js
arr.toLocaleString(locales?, options?);
```

**示例**

```js
const arr = [1234567.89, new Date()];
arr.toLocaleString('zh-CN');
// '1,234,567.89,2026/8/12 下午7:30:00'

[1000, 2000].toLocaleString('zh-CN', { style: 'currency', currency: 'CNY' });
// '¥1,000.00,¥2,000.00'
```

---

# 九、ES6+ 新增方法

## 9.1 Array.isArray()

**语法**

```js
Array.isArray(value);
```

**返回值**

`true` 如果 value 是数组；否则 `false`。

**示例**

```js
Array.isArray([1, 2, 3]);     // true
Array.isArray('hello');       // false
Array.isArray({});            // false
Array.isArray(null);          // false
Array.isArray(undefined);     // false
Array.isArray(new Array(3));  // true

// ⚠️ 不能用 instanceof 判断跨 iframe 的数组
// iframe 中创建的数组 instanceof Array → false
// 但 Array.isArray 可以正确判断
```

**注意**

- 最可靠的数组类型判断方法。
- 比 `instanceof Array` 更可靠（跨 iframe / 跨 realm）。

---

## 9.2 扩展运算符 ...

**语法**

```js
[...iterable];
```

**示例**

```js
// 1. 复制数组（浅拷贝）
const arr = [1, 2, 3];
const copy = [...arr];

// 2. 合并数组
const merged = [...arr1, ...arr2];

// 3. Set 转数组（去重）
const unique = [...new Set([1, 2, 2, 3])];

// 4. 字符串转数组
const chars = [...'hello'];   // ['h','e','l','l','o']

// 5. NodeList 转数组
const divs = [...document.querySelectorAll('div')];

// 6. arguments 转数组
function sum() {
  return [...arguments].reduce((a, b) => a + b, 0);
}

// 7. 解构 + 剩余
const [first, ...rest] = [1, 2, 3, 4];  // first=1, rest=[2,3,4]
```

---

## 9.3 at()

**语法**

```js
arr.at(index);
```

**说明**

ES2022 新增。支持负索引访问，等价于 `arr[arr.length + index]`（当 index 为负数时）。

**示例**

```js
const arr = [1, 2, 3, 4, 5];

arr.at(0);     // 1（第一个）
arr.at(-1);    // 5（最后一个）
arr.at(-2);    // 4（倒数第二个）
arr.at(10);    // undefined（越界）

// 对比传统方式
arr[arr.length - 1];  // 5（繁琐）
arr.at(-1);           // 5（简洁）
```

**注意**

- 比 `arr[arr.length - 1]` 更简洁。
- 越界返回 `undefined`，不报错。

---

## 9.4 Array.from() 进阶

```js
// 1. 生成 0~N-1 序列
Array.from({ length: 5 }, (_, i) => i);   // [0, 1, 2, 3, 4]

// 2. 生成 1~N 序列
Array.from({ length: 10 }, (_, i) => i + 1);  // [1, 2, ..., 10]

// 3. 生成随机数数组
Array.from({ length: 5 }, () => Math.random());

// 4. 生成 UUID 前缀
Array.from({ length: 8 }, () => Math.floor(Math.random() * 16).toString(16)).join('');
// 'a3f7b2c1'

// 5. 二维数组初始化（避免引用陷阱）
const grid = Array.from({ length: 3 }, () => Array(3).fill(0));
grid[0][0] = 1;  // 只改第一个子数组
// [[1,0,0], [0,0,0], [0,0,0]]  ✅

// ⚠️ 对比错误写法
const bad = new Array(3).fill(new Array(3).fill(0));
bad[0][0] = 1;
// [[1,0,0], [1,0,0], [1,0,0]]  ❌ 全部被改了
```

---

## 9.5 group() / groupToMap()

**语法**

```js
arr.group(callback(element, index, array));        // 返回对象
arr.groupToMap(callback(element, index, array));   // 返回 Map
```

**说明**

ES2024 新增。按 callback 返回的 key 对元素分组。

**示例**

```js
const inventory = [
  { name: 'apples', quantity: 6 },
  { name: 'bananas', quantity: 2 },
  { name: 'apples', quantity: 3 },
  { name: 'oranges', quantity: 5 }
];

// group：返回普通对象
const grouped = inventory.group(item => item.name);
// {
//   apples: [{ name: 'apples', quantity: 6 }, { name: 'apples', quantity: 3 }],
//   bananas: [{ name: 'bananas', quantity: 2 }],
//   oranges: [{ name: 'oranges', quantity: 5 }]
// }

// groupToMap：返回 Map（key 可以是任意类型）
const map = inventory.groupToMap(item =>
  item.quantity > 3 ? 'sufficient' : 'insufficient'
);
map.get('sufficient');   // [{ name: 'apples', quantity: 6 }, { name: 'oranges', quantity: 5 }]
map.get('insufficient'); // [{ name: 'bananas', quantity: 2 }, { name: 'apples', quantity: 3 }]
```

**注意**

- ES2024 非常新，注意 polyfill。
- 不修改原数组。
- 用 `reduce` 手动实现分组是兼容方案。

---

# 十、实战工具函数

## 10.1 数组去重（5 种方案）

```js
// 1. Set（最简洁，ES6+）
[...new Set([1, 2, 2, 3, 3, 3])];  // [1, 2, 3]

// 2. filter + indexOf
[1, 2, 2, 3, 3].filter((n, i, arr) => arr.indexOf(n) === i);  // [1, 2, 3]

// 3. reduce + includes
[1, 2, 2, 3, 3].reduce((unique, n) =>
  unique.includes(n) ? unique : [...unique, n], []);

// 4. 对象数组去重（按 key）
const users = [
  { id: 1, name: 'Tom' },
  { id: 2, name: 'Jerry' },
  { id: 1, name: 'Tom' }
];
const uniqueUsers = [...new Map(users.map(u => [u.id, u])).values()];
// [{ id: 1, name: 'Tom' }, { id: 2, name: 'Jerry' }]

// 5. 对象数组去重（通用函数）
function uniqueBy(arr, keyFn) {
  const seen = new Set();
  return arr.filter(item => {
    const key = keyFn(item);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}
uniqueBy(users, u => u.id);
```

## 10.2 数组扁平化

```js
// 1. flat(Infinity)
[1, [2, [3, [4]]]].flat(Infinity);  // [1, 2, 3, 4]

// 2. 递归实现
function flatten(arr) {
  return arr.reduce((flat, cur) =>
    Array.isArray(cur) ? flat.concat(flatten(cur)) : flat.concat(cur), []);
}

// 3. 迭代实现（栈）
function flattenIter(arr) {
  const stack = [...arr];
  const result = [];
  while (stack.length) {
    const item = stack.pop();
    if (Array.isArray(item)) {
      stack.push(...item);
    } else {
      result.unshift(item);
    }
  }
  return result;
}

// 4. 指定深度
function flattenDepth(arr, depth = 1) {
  if (depth <= 0) return [...arr];
  return arr.reduce((flat, cur) =>
    Array.isArray(cur) ? flat.concat(flattenDepth(cur, depth - 1)) : flat.concat(cur), []);
}
```

## 10.3 数组交集/并集/差集

```js
const a = [1, 2, 3, 4];
const b = [3, 4, 5, 6];

// 并集
const union = [...new Set([...a, ...b])];           // [1, 2, 3, 4, 5, 6]

// 交集
const intersection = a.filter(x => b.includes(x));     // [3, 4]

// 差集（a 有 b 没有）
const difference = a.filter(x => !b.includes(x));      // [1, 2]

// 对称差集（a 或 b 独有的）
const symDiff = [...a.filter(x => !b.includes(x)), ...b.filter(x => !a.includes(x))];
// [1, 2, 5, 6]
```

## 10.4 数组分块

```js
function chunk(arr, size) {
  return Array.from({ length: Math.ceil(arr.length / size) }, (_, i) =>
    arr.slice(i * size, i * size + size)
  );
}

chunk([1, 2, 3, 4, 5], 2);   // [[1, 2], [3, 4], [5]]
chunk([1, 2, 3, 4, 5], 3);   // [[1, 2, 3], [4, 5]]
```

## 10.5 数组洗牌

```js
function shuffle(arr) {
  const result = [...arr];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

shuffle([1, 2, 3, 4, 5]);   // [3, 1, 5, 2, 4]（随机）
```

## 10.6 深拷贝数组

```js
// 浅拷贝
const shallow = [...arr];

// 深拷贝（简单场景）
const deep = JSON.parse(JSON.stringify(arr));

// 深拷贝（含函数、Date 等）
function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime());
  if (Array.isArray(obj)) return obj.map(deepClone);
  const cloned = {};
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) cloned[key] = deepClone(obj[key]);
  }
  return cloned;
}
```

---

# 十一、高频面试题

## Q1：map 和 forEach 的区别？

| 维度 | forEach | map |
|---|---|---|
| 返回值 | `undefined` | **新数组** |
| 链式调用 | 不能 | 能 |
| 使用场景 | 副作用操作（打印、修改外部变量） | 数据转换 |
| 性能 | 略快（不创建新数组） | 略慢 |

```js
// forEach：适合副作用
arr.forEach(item => console.log(item));

// map：适合转换数据
const doubled = arr.map(x => x * 2);
```

## Q2：如何判断一个变量是否是数组？

```js
// ✅ 最佳：Array.isArray
Array.isArray(value);

// ❌ typeof（返回 'object'）
typeof [];   // 'object'

// ⚠️ instanceof（跨 iframe 失效）
[] instanceof Array;   // true（同 realm）

// ✅ Object.prototype.toString
Object.prototype.toString.call([]);   // '[object Array]'
```

## Q3：sort 默认排序为什么是错的？

```js
[10, 2, 1, 21].sort();   // [1, 10, 2, 21]  ← 字符串排序！

// 原因：默认把元素转成字符串，按 Unicode 码点比较
// '10' < '2' → 因为 '1' < '2'

// 修复：传比较函数
[10, 2, 1, 21].sort((a, b) => a - b);   // [1, 2, 10, 21]
```

## Q4：什么是数组 holes？哪些方法跳过 holes？

```js
const arr = [1, , 3];  // 索引 1 是 hole（空位）

// 跳过 holes（不调用 callback）
arr.forEach(() => {});      // 只执行 2 次
arr.map(x => x * 2);        // [2, empty, 6]（保留 hole）
arr.filter(() => true);     // [1, 3]（移除 hole）

// 不跳过 holes（当作 undefined）
arr.find(() => true);       // 1（但会检查 hole）
arr.includes(undefined);    // false（hole 不是 undefined）
[1, , 3].join('-');         // '1--3'（hole 转空字符串）
```

## Q5：如何实现数组的 map 方法？

```js
Array.prototype.myMap = function(callback, thisArg) {
  if (typeof callback !== 'function') {
    throw new TypeError(callback + ' is not a function');
  }
  const result = [];
  for (let i = 0; i < this.length; i++) {
    if (i in this) {  // 跳过 holes
      result[i] = callback.call(thisArg, this[i], i, this);
    }
  }
  return result;
};
```

## Q6：如何实现数组的 reduce 方法？

```js
Array.prototype.myReduce = function(callback, initialValue) {
  if (typeof callback !== 'function') {
    throw new TypeError(callback + ' is not a function');
  }
  let acc, startIndex;
  if (arguments.length >= 2) {
    acc = initialValue;
    startIndex = 0;
  } else {
    // 没传初始值：找第一个非 hole 元素
    if (this.length === 0) {
      throw new TypeError('Reduce of empty array with no initial value');
    }
    startIndex = 0;
    while (startIndex < this.length && !(startIndex in this)) startIndex++;
    if (startIndex >= this.length) {
      throw new TypeError('Reduce of empty array with no initial value');
    }
    acc = this[startIndex++];
  }
  for (let i = startIndex; i < this.length; i++) {
    if (i in this) {
      acc = callback(acc, this[i], i, this);
    }
  }
  return acc;
};
```

## Q7：push/pop 和 unshift/shift 的性能差异？

```
push/pop：O(1) 均摊
  → 在数组末尾操作，JS 引擎分配空间时有预留，通常不需要移动元素

unshift/shift：O(n)
  → 在数组头部操作，所有元素需要前移/后移

大数组场景：unshift 10000 次比 push 10000 次慢 100 倍以上
```

## Q8：数组方法哪些修改原数组，哪些不修改？

| 修改原数组 | 不修改原数组（返回新数组） |
|---|---|
| push / pop / unshift / shift | concat / slice / flat / flatMap |
| splice / fill / copyWithin | map / filter / reduce / reduceRight |
| sort / reverse | find / findIndex / findLast / findLastIndex |
| | some / every / includes / indexOf |
| | join / toString / toLocaleString |
| | entries / keys / values |
| | toSorted / toReversed（ES2023+） |
| | at / group / groupToMap |

---

> **使用建议**：
> 1. 优先使用 ES6+ 语法（扩展运算符、`Array.from`、`flat`、`find`）
> 2. 注意区分"修改原数组"和"返回新数组"的方法（React 中必须用不可变操作）
> 3. 函数式编程倾向使用 `map` / `filter` / `reduce` 链式调用
> 4. 大数组操作注意性能：`push` > `unshift`，`includes` > `indexOf !== -1`
