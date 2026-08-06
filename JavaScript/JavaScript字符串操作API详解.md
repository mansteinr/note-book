# JavaScript 字符串操作 API 详解

> **文档说明**：本文档系统整理了 JavaScript 中字符串操作的各类常用 API，涵盖创建转换、拼接分割、查找替换、大小写转换、空白处理、截取提取、比较排序、正则表达式等核心功能。每个方法均提供函数签名、参数说明、返回值类型、功能描述及可运行的使用示例，并在文末提供实用工具函数封装与速查表，便于日常开发查阅。

## 目录

- [一、字符串基础概念](#一字符串基础概念)
- [二、字符串创建与转换](#二字符串创建与转换)
- [三、字符串拼接与分割](#三字符串拼接与分割)
- [四、字符串查找与定位](#四字符串查找与定位)
- [五、字符串替换](#五字符串替换)
- [六、大小写转换](#六大小写转换)
- [七、去除空白字符](#七去除空白字符)
- [八、截取与提取](#八截取与提取)
- [九、字符串比较与排序](#九字符串比较与排序)
- [十、正则表达式相关操作](#十正则表达式相关操作)
- [十一、ES6+ 新增字符串方法](#十一es6-新增字符串方法)
- [十二、字符编码操作](#十二字符编码操作)
- [十三、实用工具函数封装](#十三实用工具函数封装)
- [十四、API 速查表](#十四api-速查表)
- [十五、总结与最佳实践](#十五总结与最佳实践)

---

## 一、字符串基础概念

### 1.1 字符串的不可变性

JavaScript 中字符串是**不可变（Immutable）**的原始类型，所有字符串操作方法都不会修改原字符串，而是返回一个**新字符串**。

```javascript
let str = 'Hello';
str[0] = 'h';  // ❌ 无效操作，严格模式下会报错
console.log(str);  // 'Hello'（原字符串不变）

// 正确方式：通过方法返回新字符串
let newStr = str.toLowerCase();
console.log(str);     // 'Hello'（原字符串不变）
console.log(newStr);  // 'hello'
```

### 1.2 字符串的创建方式

```javascript
// 1. 字符串字面量（推荐）
const str1 = 'Hello';
const str2 = "World";
const str3 = `模板字符串`;  // ES6+

// 2. String 构造函数（返回对象，不推荐）
const str4 = new String('Hello');  // typeof str4 === 'object'
const str5 = String('Hello');      // typeof str5 === 'string'（推荐）

// 3. 转换为字符串
const numStr = (123).toString();         // '123'
const boolStr = String(true);            // 'true'
const nullStr = String(null);            // 'null'
const undefStr = String(undefined);      // 'undefined'
const arrayStr = [1, 2, 3].toString();   // '1,2,3'
```

### 1.3 字符串长度与索引

```javascript
const str = 'JavaScript';

// 长度
console.log(str.length);  // 10

// 索引访问（从 0 开始）
console.log(str[0]);           // 'J'
console.log(str.charAt(0));    // 'J'
console.log(str[str.length - 1]);  // 't'（最后一个字符）

// 遍历字符串
for (const char of str) {
    console.log(char);
}
// 输出: J a v a S c r i p t
```

---

## 二、字符串创建与转换

### 2.1 `String(value)` - 转换为字符串

**函数签名**：`String(value)`

**参数说明**：
- `value`：任意类型的值（`*`）

**返回值**：`string` - 转换后的字符串

**功能描述**：将任意类型的值转换为字符串，是类型转换最安全的方式。

```javascript
// 基本类型转换
console.log(String(123));        // '123'
console.log(String(3.14));       // '3.14'
console.log(String(true));       // 'true'
console.log(String(false));      // 'false'
console.log(String(null));       // 'null'
console.log(String(undefined));  // 'undefined'
console.log(String(NaN));        // 'NaN'

// 对象转换
console.log(String([1, 2, 3]));        // '1,2,3'
console.log(String({}));               // '[object Object]'
console.log(String(new Date()));       // 'Wed Aug 06 2026 ...'
console.log(String(Symbol('id')));     // 'Symbol(id)'
```

### 2.2 `toString()` - 转换为字符串

**函数签名**：`value.toString([radix])`

**参数说明**：
- `radix`（可选）：进制数（2-36），仅数字类型有效（`number`）

**返回值**：`string` - 转换后的字符串

**功能描述**：将值转换为字符串，数字可指定进制。`null` 和 `undefined` 没有 `toString()` 方法。

```javascript
// 数字转字符串
const num = 255;
console.log(num.toString());      // '255'
console.log(num.toString(2));     // '11111111'（二进制）
console.log(num.toString(16));    // 'ff'（十六进制）
console.log(num.toString(8));     // '377'（八进制）

// 数组转字符串
console.log([1, 2, 3].toString());  // '1,2,3'

// 布尔值转字符串
console.log(true.toString());        // 'true'

// ⚠️ null 和 undefined 没有 toString 方法
// console.log(null.toString());     // TypeError
// console.log(undefined.toString()); // TypeError
```

### 2.3 `valueOf()` - 返回字符串原始值

**函数签名**：`str.valueOf()`

**返回值**：`string` - 字符串的原始值

**功能描述**：返回 String 对象的原始字符串值。

```javascript
const strObj = new String('Hello');
console.log(typeof strObj);        // 'object'
console.log(typeof strObj.valueOf());  // 'string'
console.log(strObj.valueOf());     // 'Hello'
```

### 2.4 `String.fromCharCode()` - 从字符编码创建字符串

**函数签名**：`String.fromCharCode(num1[, num2[, ...[, numN]]])`

**参数说明**：
- `num1, num2, ..., numN`：一系列 UTF-16 代码单元（`number`）

**返回值**：`string` - 由指定编码组成的字符串

**功能描述**：使用指定的 UTF-16 代码单元序列创建字符串。

```javascript
console.log(String.fromCharCode(65, 66, 67));    // 'ABC'
console.log(String.fromCharCode(97, 98, 99));    // 'abc'
console.log(String.fromCharCode(0x4e2d, 0x6587)); // '中文'

// 应用：生成随机字母
const randomChar = String.fromCharCode(
    65 + Math.floor(Math.random() * 26)
);
console.log(randomChar);  // 'A' 到 'Z' 中的随机一个
```

### 2.5 `String.fromCodePoint()` - 从码点创建字符串（ES6+）

**函数签名**：`String.fromCodePoint(num1[, num2[, ...[, numN]]])`

**参数说明**：
- `num1, num2, ..., numN`：一系列 Unicode 码点（`number`）

**返回值**：`string` - 由指定码点组成的字符串

**功能描述**：使用指定的 Unicode 码点序列创建字符串，支持辅助平面字符（如 emoji）。

```javascript
console.log(String.fromCodePoint(65, 66, 67));  // 'ABC'
console.log(String.fromCodePoint(0x1F600));      // '😀'（笑脸 emoji）
console.log(String.fromCodePoint(0x1F4A9));      // '💩'

// 对比 fromCharCode（无法正确处理辅助平面字符）
console.log(String.fromCharCode(0x1F600));       // '�'（乱码）
```

---

## 三、字符串拼接与分割

### 3.1 `concat()` - 拼接字符串

**函数签名**：`str.concat(str2[, str3[, ...[, strN]]])`

**参数说明**：
- `str2, str3, ..., strN`：要拼接的字符串（`string`）

**返回值**：`string` - 拼接后的新字符串

**功能描述**：将一个或多个字符串与原字符串拼接，返回新字符串。**推荐使用 `+` 或模板字符串代替**。

```javascript
const str1 = 'Hello';
const str2 = 'World';

// 使用 concat
console.log(str1.concat(' ', str2));        // 'Hello World'
console.log(str1.concat(', ', str2, '!'));  // 'Hello, World!'

// 推荐方式：+ 运算符（性能更好）
console.log(str1 + ' ' + str2);             // 'Hello World'

// 推荐方式：模板字符串（可读性最佳）
console.log(`${str1} ${str2}`);             // 'Hello World'
console.log(`${str1}, ${str2}!`);           // 'Hello, World!'
```

### 3.2 `split()` - 分割字符串为数组

**函数签名**：`str.split([separator[, limit]])`

**参数说明**：
- `separator`（可选）：分隔符，可以是字符串或正则表达式（`string` | `RegExp`）
- `limit`（可选）：返回数组的最大长度（`number`）

**返回值**：`Array<string>` - 分割后的字符串数组

**功能描述**：使用指定分隔符将字符串分割成子字符串数组。

```javascript
const str = 'Hello,World,JavaScript,API';

// 基本分割
console.log(str.split(','));        // ['Hello', 'World', 'JavaScript', 'API']

// 限制返回数量
console.log(str.split(',', 2));     // ['Hello', 'World']

// 按字符分割
console.log('Hello'.split(''));     // ['H', 'e', 'l', 'l', 'o']

// 按正则分割
console.log('a1b2c3d'.split(/\d/)); // ['a', 'b', 'c', 'd']

// 按多个分隔符分割
console.log('Hello,World;JavaScript|API'.split(/[,;|]/));
// ['Hello', 'World', 'JavaScript', 'API']

// 空字符串分割（每个字符一个元素）
console.log('ABC'.split());         // ['ABC']（无分隔符时返回整个字符串）

// 实用：统计单词数
const sentence = 'The quick brown fox';
const wordCount = sentence.split(' ').length;
console.log(wordCount);  // 4

// 实用：反转字符串
const reversed = 'Hello'.split('').reverse().join('');
console.log(reversed);  // 'olleH'
```

### 3.3 `join()` - 数组拼接为字符串（Array 方法）

**函数签名**：`array.join([separator])`

**参数说明**：
- `separator`（可选）：分隔符，默认为逗号 `,`（`string`）

**返回值**：`string` - 拼接后的字符串

**功能描述**：将数组元素连接成一个字符串。常与 `split()` 配合使用。

```javascript
const arr = ['Hello', 'World', 'JavaScript'];

console.log(arr.join());       // 'Hello,World,JavaScript'
console.log(arr.join(''));     // 'HelloWorldJavaScript'
console.log(arr.join(' '));    // 'Hello World JavaScript'
console.log(arr.join('-'));    // 'Hello-World-JavaScript'
console.log(arr.join(', '));   // 'Hello, World, JavaScript'

// 实用：CSV 生成
const data = [
    ['name', 'age', 'city'],
    ['Alice', '25', 'Beijing'],
    ['Bob', '30', 'Shanghai']
];
const csv = data.map(row => row.join(',')).join('\n');
console.log(csv);
// name,age,city
// Alice,25,Beijing
// Bob,30,Shanghai
```

### 3.4 `repeat()` - 重复字符串（ES6+）

**函数签名**：`str.repeat(count)`

**参数说明**：
- `count`：重复次数，0 到 +∞ 之间的整数（`number`）

**返回值**：`string` - 重复后的新字符串

**功能描述**：返回将原字符串重复 `count` 次的新字符串。

```javascript
console.log('abc'.repeat(0));   // ''
console.log('abc'.repeat(1));   // 'abc'
console.log('abc'.repeat(3));   // 'abcabcabc'
console.log('='.repeat(50));    // 50 个等号

// 实用：生成缩进
function indent(text, level) {
    return text.split('\n').map(line => '  '.repeat(level) + line).join('\n');
}
console.log(indent('Hello\nWorld', 2));
//     Hello
//     World

// 实用：生成分隔线
console.log('-'.repeat(40));  // '----------------------------------------'
```

---

## 四、字符串查找与定位

### 4.1 `indexOf()` - 从前查找位置

**函数签名**：`str.indexOf(searchValue[, fromIndex])`

**参数说明**：
- `searchValue`：要查找的子字符串（`string`）
- `fromIndex`（可选）：开始查找的位置，默认 0（`number`）

**返回值**：`number` - 首次出现的索引，未找到返回 -1

**功能描述**：从字符串前向后查找子字符串首次出现的位置。

```javascript
const str = 'Hello World Hello JavaScript';

console.log(str.indexOf('Hello'));       // 0
console.log(str.indexOf('World'));       // 6
console.log(str.indexOf('hello'));       // -1（区分大小写）
console.log(str.indexOf('Hello', 1));    // 12（从索引 1 开始查找）

// 实用：判断子字符串是否存在
function contains(str, sub) {
    return str.indexOf(sub) !== -1;
}
console.log(contains('Hello World', 'World'));  // true

// 实用：统计子字符串出现次数
function countOccurrences(str, sub) {
    let count = 0;
    let pos = str.indexOf(sub);
    while (pos !== -1) {
        count++;
        pos = str.indexOf(sub, pos + sub.length);
    }
    return count;
}
console.log(countOccurrences('Hello Hello Hello', 'Hello'));  // 3
```

### 4.2 `lastIndexOf()` - 从后查找位置

**函数签名**：`str.lastIndexOf(searchValue[, fromIndex])`

**参数说明**：
- `searchValue`：要查找的子字符串（`string`）
- `fromIndex`（可选）：从后向前查找的起始位置，默认 `str.length - 1`（`number`）

**返回值**：`number` - 最后一次出现的索引，未找到返回 -1

**功能描述**：从字符串后向前查找子字符串最后一次出现的位置。

```javascript
const str = 'Hello World Hello JavaScript';

console.log(str.lastIndexOf('Hello'));      // 12
console.log(str.lastIndexOf('o'));          // 17
console.log(str.lastIndexOf('Hello', 5));   // 0（从索引 5 向前查找）

// 实用：获取文件扩展名
function getExtension(filename) {
    const lastDotIndex = filename.lastIndexOf('.');
    return lastDotIndex === -1 ? '' : filename.slice(lastDotIndex + 1);
}
console.log(getExtension('document.pdf'));      // 'pdf'
console.log(getExtension('archive.tar.gz'));    // 'gz'
console.log(getExtension('noextension'));       // ''
```

### 4.3 `includes()` - 是否包含子字符串（ES6+）

**函数签名**：`str.includes(searchString[, position])`

**参数说明**：
- `searchString`：要查找的子字符串（`string`）
- `position`（可选）：开始查找的位置，默认 0（`number`）

**返回值**：`boolean` - 是否包含

**功能描述**：判断字符串是否包含指定的子字符串，返回布尔值。

```javascript
const str = 'Hello World';

console.log(str.includes('World'));       // true
console.log(str.includes('world'));       // false（区分大小写）
console.log(str.includes('Hello', 1));    // false（从索引 1 开始查找）

// 实用：敏感词过滤
const bannedWords = ['spam', 'ads', 'viagra'];
function containsBanned(text) {
    return bannedWords.some(word => 
        text.toLowerCase().includes(word.toLowerCase())
    );
}
console.log(containsBanned('This is SPAM'));  // true
```

### 4.4 `startsWith()` - 是否以指定字符串开头（ES6+）

**函数签名**：`str.startsWith(searchString[, position])`

**参数说明**：
- `searchString`：要查找的开头字符串（`string`）
- `position`（可选）：开始检查的位置，默认 0（`number`）

**返回值**：`boolean` - 是否以指定字符串开头

**功能描述**：判断字符串是否以指定的子字符串开头。

```javascript
const str = 'Hello World';

console.log(str.startsWith('Hello'));      // true
console.log(str.startsWith('hello'));      // false（区分大小写）
console.log(str.startsWith('World', 6));   // true（从索引 6 开始检查）

// 实用：URL 协议判断
const url = 'https://example.com';
if (url.startsWith('https://')) {
    console.log('安全连接');
} else if (url.startsWith('http://')) {
    console.log('非安全连接');
}

// 实用：文件类型判断
function isImageFile(filename) {
    return ['.jpg', '.png', '.gif', '.webp']
        .some(ext => filename.toLowerCase().endsWith(ext));
}
```

### 4.5 `endsWith()` - 是否以指定字符串结尾（ES6+）

**函数签名**：`str.endsWith(searchString[, length])`

**参数说明**：
- `searchString`：要查找的结尾字符串（`string`）
- `length`（可选）：作为原字符串长度的前 `length` 个字符，默认 `str.length`（`number`）

**返回值**：`boolean` - 是否以指定字符串结尾

**功能描述**：判断字符串是否以指定的子字符串结尾。

```javascript
const str = 'Hello World';

console.log(str.endsWith('World'));       // true
console.log(str.endsWith('world'));       // false（区分大小写）
console.log(str.endsWith('Hello', 5));    // true（检查前 5 个字符）

// 实用：文件扩展名判断
const filename = 'photo.jpg';
if (filename.endsWith('.jpg') || filename.endsWith('.png')) {
    console.log('图片文件');
}

// 实用：路径处理
const path = '/usr/local/bin/';
console.log(path.endsWith('/'));  // true（以斜杠结尾）
```

### 4.6 `search()` - 正则搜索位置

**函数签名**：`str.search(regexp)`

**参数说明**：
- `regexp`：正则表达式对象或字面量（`RegExp` | `string`）

**返回值**：`number` - 首次匹配的索引，未找到返回 -1

**功能描述**：使用正则表达式搜索匹配项，返回第一个匹配项的索引。

```javascript
const str = 'Hello World 123';

console.log(str.search(/World/));    // 6
console.log(str.search(/\d/));       // 12（第一个数字的位置）
console.log(str.search(/xyz/));      // -1（未找到）
console.log(str.search(/[A-Z]/));    // 0（第一个大写字母）

// 对比 indexOf：search 支持正则，indexOf 只支持字符串
// 实用：查找第一个数字的位置
const firstDigitIndex = str.search(/\d/);
console.log(firstDigitIndex);  // 12
```

### 4.7 `charAt()` - 获取指定位置字符

**函数签名**：`str.charAt(index)`

**参数说明**：
- `index`：字符位置，0 到 `str.length - 1`（`number`）

**返回值**：`string` - 指定位置的字符（空字符串表示越界）

**功能描述**：返回指定位置的字符。

```javascript
const str = 'Hello';

console.log(str.charAt(0));      // 'H'
console.log(str.charAt(1));      // 'e'
console.log(str.charAt(4));      // 'o'
console.log(str.charAt(10));     // ''（越界返回空字符串）
console.log(str.charAt(-1));     // ''（负数返回空字符串）

// 对比：使用索引访问
console.log(str[0]);             // 'H'
console.log(str[10]);            // undefined（索引越界返回 undefined）

// 实用：遍历字符
for (let i = 0; i < str.length; i++) {
    console.log(str.charAt(i));
}
```

### 4.8 `charCodeAt()` - 获取字符编码

**函数签名**：`str.charCodeAt(index)`

**参数说明**：
- `index`：字符位置（`number`）

**返回值**：`number` - UTF-16 代码单元（0-65535），越界返回 `NaN`

**功能描述**：返回指定位置字符的 UTF-16 代码单元。

```javascript
const str = 'ABC';

console.log(str.charCodeAt(0));  // 65（'A' 的编码）
console.log(str.charCodeAt(1));  // 66（'B' 的编码）
console.log(str.charCodeAt(2));  // 67（'C' 的编码）
console.log(str.charCodeAt(10)); // NaN（越界）

// 实用：判断字符类型
function charType(char) {
    const code = char.charCodeAt(0);
    if (code >= 48 && code <= 57) return 'digit';
    if (code >= 65 && code <= 90) return 'uppercase';
    if (code >= 97 && code <= 122) return 'lowercase';
    return 'other';
}
console.log(charType('5'));  // 'digit'
console.log(charType('A'));  // 'uppercase'
console.log(charType('a'));  // 'lowercase'
```

### 4.9 `codePointAt()` - 获取字符码点（ES6+）

**函数签名**：`str.codePointAt(pos)`

**参数说明**：
- `pos`：字符位置（`number`）

**返回值**：`number` | `undefined` - Unicode 码点，越界返回 `undefined`

**功能描述**：返回指定位置字符的 Unicode 码点，支持辅助平面字符（如 emoji）。

```javascript
console.log('A'.codePointAt(0));      // 65
console.log('中'.codePointAt(0));     // 20013
console.log('😀'.codePointAt(0));     // 128512（正确处理 emoji）
console.log('ABC'.codePointAt(10));   // undefined（越界）
```

---

## 五、字符串替换

### 5.1 `replace()` - 替换匹配项

**函数签名**：`str.replace(pattern, replacement)`

**参数说明**：
- `pattern`：要匹配的模式，字符串或正则表达式（`string` | `RegExp`）
- `replacement`：替换内容，字符串或函数（`string` | `Function`）

**返回值**：`string` - 替换后的新字符串

**功能描述**：替换第一个匹配项（使用 `g` 标志替换所有）。原字符串不变。

```javascript
const str = 'Hello World, Hello JavaScript';

// 字符串替换（仅替换第一个）
console.log(str.replace('Hello', 'Hi'));
// 'Hi World, Hello JavaScript'

// 正则替换第一个
console.log(str.replace(/Hello/, 'Hi'));
// 'Hi World, Hello JavaScript'

// 正则替换所有（g 标志）
console.log(str.replace(/Hello/g, 'Hi'));
// 'Hi World, Hi JavaScript'

// 忽略大小写替换
console.log(str.replace(/hello/gi, 'Hi'));
// 'Hi World, Hi JavaScript'

// 使用特殊变量
console.log('2026-08-06'.replace(/(\d{4})-(\d{2})-(\d{2})/, '$3/$2/$1'));
// '06/08/2026'

// 使用函数作为替换内容
const result = str.replace(/Hello/g, (match, offset, string) => {
    return match.toUpperCase();
});
console.log(result);  // 'HELLO World, HELLO JavaScript'

// 实用：模板替换
function template(str, data) {
    return str.replace(/\{\{(\w+)\}\}/g, (match, key) => {
        return data[key] !== undefined ? data[key] : '';
    });
}
console.log(template('Hello {{name}}, you are {{age}} years old', 
    { name: 'Alice', age: 25 }));
// 'Hello Alice, you are 25 years old'

// 实用：手机号脱敏
function maskPhone(phone) {
    return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
}
console.log(maskPhone('13812345678'));  // '138****5678'
```

### 5.2 `replaceAll()` - 替换所有匹配项（ES2021+）

**函数签名**：`str.replaceAll(pattern, replacement)`

**参数说明**：
- `pattern`：要匹配的模式，字符串或**必须带 `g` 标志的正则表达式**（`string` | `RegExp`）
- `replacement`：替换内容，字符串或函数（`string` | `Function`）

**返回值**：`string` - 替换后的新字符串

**功能描述**：替换所有匹配项。使用正则时必须带 `g` 标志，否则报错。

```javascript
const str = 'Hello World, Hello JavaScript';

// 字符串替换所有
console.log(str.replaceAll('Hello', 'Hi'));
// 'Hi World, Hi JavaScript'

// 正则替换所有（必须带 g 标志）
console.log(str.replaceAll(/Hello/g, 'Hi'));
// 'Hi World, Hi JavaScript'

// ❌ 错误：正则不带 g 标志会报错
// console.log(str.replaceAll(/Hello/, 'Hi'));  // TypeError

// 实用：批量替换空白字符为下划线
const filename = 'my file name.txt'.replaceAll(' ', '_');
console.log(filename);  // 'my_file_name.txt'
```

---

## 六、大小写转换

### 6.1 `toUpperCase()` - 转大写

**函数签名**：`str.toUpperCase()`

**返回值**：`string` - 转换为大写的新字符串

**功能描述**：将字符串中所有字母转换为大写。

```javascript
console.log('hello'.toUpperCase());        // 'HELLO'
console.log('Hello World'.toUpperCase());  // 'HELLO WORLD'
console.log('中文'.toUpperCase());          // '中文'（中文无大小写）

// 实用：标准化用户输入
const userInput = '  Yes  ';
if (userInput.trim().toUpperCase() === 'YES') {
    console.log('用户确认');
}
```

### 6.2 `toLowerCase()` - 转小写

**函数签名**：`str.toLowerCase()`

**返回值**：`string` - 转换为小写的新字符串

**功能描述**：将字符串中所有字母转换为小写。

```javascript
console.log('HELLO'.toLowerCase());        // 'hello'
console.log('Hello World'.toLowerCase());  // 'hello world'

// 实用：不区分大小写的比较
function equalsIgnoreCase(str1, str2) {
    return str1.toLowerCase() === str2.toLowerCase();
}
console.log(equalsIgnoreCase('Hello', 'hello'));  // true

// 实用：邮箱标准化
function normalizeEmail(email) {
    return email.trim().toLowerCase();
}
console.log(normalizeEmail('  Alice@Example.COM  '));  // 'alice@example.com'
```

### 6.3 `toLocaleUpperCase()` / `toLocaleLowerCase()` - 本地化大小写转换

**函数签名**：
- `str.toLocaleUpperCase([locale])`
- `str.toLocaleLowerCase([locale])`

**参数说明**：
- `locale`（可选）：指定语言环境（`string` | `Array<string>`）

**返回值**：`string` - 转换后的字符串

**功能描述**：根据特定语言规则进行大小写转换，处理特殊字符（如土耳其语的 `i`）。

```javascript
// 土耳其语特殊处理
console.log('i'.toUpperCase());              // 'I'
console.log('i'.toLocaleUpperCase('tr-TR')); // 'İ'（土耳其语带点的 I）

// 德语 ß 字符
console.log('ß'.toUpperCase());              // 'SS'
console.log('ß'.toLocaleUpperCase('de-DE')); // 'SS'

// 一般情况下 toUpperCase() 足够，国际化场景才需要 toLocaleUpperCase()
```

---

## 七、去除空白字符

### 7.1 `trim()` - 去除两端空白

**函数签名**：`str.trim()`

**返回值**：`string` - 去除两端空白后的新字符串

**功能描述**：去除字符串两端的空白字符（包括空格、制表符、换行符等）。

```javascript
const str = '   Hello World   ';

console.log(str.trim());      // 'Hello World'
console.log('  \t\nHello\n  '.trim());  // 'Hello'

// 实用：表单输入清理
const username = '  alice123  '.trim();
console.log(username);  // 'alice123'

// 注意：只去除两端，中间的空白保留
console.log('  Hello   World  '.trim());  // 'Hello   World'
```

### 7.2 `trimStart()` / `trimLeft()` - 去除左侧空白（ES2019+）

**函数签名**：`str.trimStart()` 或 `str.trimLeft()`

**返回值**：`string` - 去除左侧空白后的新字符串

**功能描述**：去除字符串开头的空白字符。`trimStart` 是推荐名称，`trimLeft` 是别名。

```javascript
const str = '   Hello World   ';

console.log(str.trimStart());   // 'Hello World   '
console.log(str.trimLeft());    // 'Hello World   '（别名）

// 实用：处理多行文本缩进
const text = `
    line 1
    line 2
    line 3`;
const processed = text.split('\n')
    .map(line => line.trimStart())
    .join('\n');
console.log(processed);
// line 1
// line 2
// line 3
```

### 7.3 `trimEnd()` / `trimRight()` - 去除右侧空白（ES2019+）

**函数签名**：`str.trimEnd()` 或 `str.trimRight()`

**返回值**：`string` - 去除右侧空白后的新字符串

**功能描述**：去除字符串末尾的空白字符。`trimEnd` 是推荐名称，`trimRight` 是别名。

```javascript
const str = '   Hello World   ';

console.log(str.trimEnd());     // '   Hello World'
console.log(str.trimRight());   // '   Hello World'（别名）

// 实用：清理数据导出
const data = ['Alice  ', '  Bob', '  Charlie  '];
const cleaned = data.map(item => item.trim());
console.log(cleaned);  // ['Alice', 'Bob', 'Charlie']
```

---

## 八、截取与提取

### 8.1 `slice()` - 截取子字符串（推荐）

**函数签名**：`str.slice(beginIndex[, endIndex])`

**参数说明**：
- `beginIndex`：开始索引，负数表示从末尾计算（`number`）
- `endIndex`（可选）：结束索引（不包含），负数表示从末尾计算（`number`）

**返回值**：`string` - 截取的子字符串

**功能描述**：提取字符串的一部分，支持负数索引。**不会修改原字符串。**

```javascript
const str = 'Hello World';

// 基本用法
console.log(str.slice(0, 5));    // 'Hello'
console.log(str.slice(6));       // 'World'（省略 endIndex 到末尾）
console.log(str.slice(6, 11));   // 'World'

// 使用负数索引（从末尾计算）
console.log(str.slice(-5));      // 'World'（后 5 个字符）
console.log(str.slice(-5, -1));  // 'Worl'
console.log(str.slice(0, -6));   // 'Hello'

// 实用：获取文件扩展名
function getExt(filename) {
    return filename.slice(filename.lastIndexOf('.') + 1);
}
console.log(getExt('file.txt'));  // 'txt'

// 实用：截断长文本
function truncate(text, maxLen) {
    return text.length > maxLen 
        ? text.slice(0, maxLen) + '...' 
        : text;
}
console.log(truncate('Hello World JavaScript', 10));  // 'Hello Worl...'
```

### 8.2 `substring()` - 截取子字符串

**函数签名**：`str.substring(indexStart[, indexEnd])`

**参数说明**：
- `indexStart`：开始索引（`number`）
- `indexEnd`（可选）：结束索引（不包含）（`number`）

**返回值**：`string` - 截取的子字符串

**功能描述**：提取字符串的一部分。**不支持负数索引**，会自动调整参数顺序（`indexStart > indexEnd` 时会交换）。

```javascript
const str = 'Hello World';

console.log(str.substring(0, 5));    // 'Hello'
console.log(str.substring(6, 11));   // 'World'
console.log(str.substring(6));       // 'World'

// 与 slice 的区别
console.log(str.substring(-5));      // 'Hello World'（负数被当作 0）
console.log(str.slice(-5));          // 'World'（负数从末尾计算）

console.log(str.substring(11, 6));   // 'World'（自动交换参数顺序）
console.log(str.slice(11, 6));       // ''（不交换，返回空字符串）

// 推荐：统一使用 slice()，功能更强大
```

### 8.3 `substr()` - 截取指定长度子字符串（已废弃）

**函数签名**：`str.substr(start[, length])`

**参数说明**：
- `start`：开始索引，负数表示从末尾计算（`number`）
- `length`（可选）：要截取的字符数（`number`）

**返回值**：`string` - 截取的子字符串

**功能描述**：从指定位置开始截取指定长度的子字符串。**⚠️ 已废弃，不推荐使用，请用 `slice()` 代替。**

```javascript
const str = 'Hello World';

console.log(str.substr(0, 5));    // 'Hello'
console.log(str.substr(6, 5));    // 'World'
console.log(str.substr(6));       // 'World'（到末尾）
console.log(str.substr(-5));      // 'World'（负数从末尾计算）

// ⚠️ 已废弃，推荐使用 slice() 代替
// 等价写法：
// str.substr(6, 5)  =>  str.slice(6, 6 + 5)
```

### 8.4 `at()` - 获取指定位置字符（ES2022+）

**函数签名**：`str.at(index)`

**参数说明**：
- `index`：字符位置，支持负数（`number`）

**返回值**：`string` | `undefined` - 指定位置的字符，越界返回 `undefined`

**功能描述**：返回指定位置的字符，支持负数索引（从末尾计算）。

```javascript
const str = 'Hello';

console.log(str.at(0));     // 'H'
console.log(str.at(1));     // 'e'
console.log(str.at(-1));    // 'o'（最后一个字符）
console.log(str.at(-2));    // 'l'
console.log(str.at(10));    // undefined（越界）

// 对比其他方式
console.log(str[str.length - 1]);  // 'o'
console.log(str.charAt(str.length - 1));  // 'o'
console.log(str.slice(-1));  // 'o'

// at() 的优势：简洁地获取最后一个字符
const lastChar = str.at(-1);
```

### 8.5 `substring()` vs `slice()` vs `substr()` 对比

| 特性 | `slice()` | `substring()` | `substr()` |
|------|-----------|---------------|------------|
| **参数** | (start, end) | (start, end) | (start, length) |
| **负数索引** | ✅ 支持（从末尾计算） | ❌ 被当作 0 | ✅ 支持（从末尾计算） |
| **参数顺序** | 不交换 | 自动交换（start > end 时） | - |
| **推荐度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ 已废弃 |
| **使用场景** | 通用推荐 | 简单截取 | 不推荐使用 |

```javascript
const str = 'Hello World';

// 同样截取 'World'
console.log(str.slice(6, 11));        // 'World'
console.log(str.substring(6, 11));    // 'World'
console.log(str.substr(6, 5));        // 'World'

// 从末尾截取 5 个字符
console.log(str.slice(-5));           // 'World' ✅
console.log(str.substring(str.length - 5));  // 'World'（需要手动计算）
```

---

## 九、字符串比较与排序

### 9.1 `localeCompare()` - 本地化比较

**函数签名**：`str.localeCompare(compareString[, locales[, options]])`

**参数说明**：
- `compareString`：要比较的字符串（`string`）
- `locales`（可选）：语言环境（`string` | `Array<string>`）
- `options`（可选）：比较选项对象（`object`）

**返回值**：`number` - 负数（str 在前）、0（相等）、正数（str 在后）

**功能描述**：使用本地化规则比较两个字符串，支持语言特定的排序规则。

```javascript
// 基本比较
console.log('a'.localeCompare('b'));   // -1（a 在 b 前）
console.log('b'.localeCompare('a'));   // 1（b 在 a 后）
console.log('a'.localeCompare('a'));   // 0（相等）

// 实用：数组排序
const fruits = ['banana', 'apple', 'cherry'];
console.log(fruits.sort((a, b) => a.localeCompare(b)));
// ['apple', 'banana', 'cherry']

// 中文排序
const names = ['张三', '李四', '王五', '阿七'];
console.log(names.sort((a, b) => a.localeCompare(b, 'zh-Hans-CN')));
// ['阿七', '李四', '王五', '张三']（按拼音排序）

// 数字排序（使用 numeric 选项）
const versions = ['v10', 'v2', 'v1', 'v20'];
console.log(versions.sort((a, b) => 
    a.localeCompare(b, undefined, { numeric: true })
));
// ['v1', 'v2', 'v10', 'v20']

// 忽略大小写排序
const words = ['Banana', 'apple', 'Cherry'];
console.log(words.sort((a, b) => 
    a.localeCompare(b, undefined, { sensitivity: 'base' })
));
// ['apple', 'Banana', 'Cherry']

// 选项说明
const options = {
    localeMatcher: 'lookup',      // 语言环境匹配算法
    sensitivity: 'base',          // 'base' | 'accent' | 'case' | 'variant'
    ignorePunctuation: true,      // 忽略标点
    numeric: true,                // 数字感知排序
    caseFirst: 'upper'            // 'upper' | 'lower' | 'false'
};
```

### 9.2 基本比较运算符

```javascript
// 使用 < > <= >= 运算符比较（基于 Unicode 编码）
console.log('a' < 'b');      // true
console.log('apple' < 'banana');  // true
console.log('A' < 'a');      // true（大写字母编码小于小写）

// ⚠️ 注意：字典序比较，不是自然数字序
console.log('10' < '9');     // true（'1' < '9' 字符比较）

// 比较长度
function compareByLength(a, b) {
    if (a.length < b.length) return -1;
    if (a.length > b.length) return 1;
    return 0;
}
console.log(['aaa', 'a', 'aa'].sort(compareByLength));
// ['a', 'aa', 'aaa']
```

### 9.3 `localeCompare()` vs 比较运算符

```javascript
// 比较运算符：基于 Unicode 编码，不考虑语言规则
console.log('apple' < 'Banana');   // false（'a'(97) > 'B'(66)）

// localeCompare：考虑语言规则，默认大小写不敏感
console.log('apple'.localeCompare('Banana'));  // -1（apple 在前）

// 中文比较
console.log('张三' < '李四');      // false（基于 Unicode）
console.log('张三'.localeCompare('李四', 'zh-CN'));  // 1（按拼音，李在前）

// 结论：需要本地化排序时使用 localeCompare()
```

---

## 十、正则表达式相关操作

### 10.1 `match()` - 匹配正则表达式

**函数签名**：`str.match(regexp)`

**参数说明**：
- `regexp`：正则表达式对象（`RegExp`）

**返回值**：`Array<string>` | `null` - 匹配结果数组，无匹配返回 `null`

**功能描述**：使用正则表达式匹配字符串，返回匹配结果。

```javascript
const str = 'Hello World 123 JavaScript 456';

// 不带 g 标志：返回第一个匹配及捕获组
console.log(str.match(/\d+/));
// ['123', index: 12, input: 'Hello World 123 JavaScript 456', groups: undefined]

// 带 g 标志：返回所有匹配
console.log(str.match(/\d+/g));  // ['123', '456']

// 带捕获组
console.log(str.match(/(\w+)\s(\w+)/));
// ['Hello World', 'Hello', 'World', index: 0, ...]

// 无匹配返回 null
console.log(str.match(/xyz/));  // null

// 实用：提取所有单词
const words = str.match(/\w+/g);
console.log(words);  // ['Hello', 'World', '123', 'JavaScript', '456']

// 实用：提取 URL 中的查询参数
const url = 'https://example.com?page=1&size=10&sort=desc';
const params = url.match(/(\w+)=(\w+)/g);
console.log(params);  // ['page=1', 'size=10', 'sort=desc']
```

### 10.2 `matchAll()` - 匹配所有结果（ES2020+）

**函数签名**：`str.matchAll(regexp)`

**参数说明**：
- `regexp`：**必须带 `g` 标志的正则表达式**（`RegExp`）

**返回值**：`Iterator` - 匹配结果的迭代器

**功能描述**：返回所有匹配结果的迭代器，每个结果包含捕获组信息。正则必须带 `g` 标志。

```javascript
const str = 'Hello World 123 JavaScript 456';

// 必须带 g 标志
const matches = str.matchAll(/\d+/g);

// 转换为数组使用
const result = [...matches];
console.log(result);
// [
//   ['123', index: 12, input: '...'],
//   ['456', index: 28, input: '...']
// ]

// 实用：提取带捕获组的所有匹配
const text = '2026-08-06 and 2026-12-25';
const dates = [...text.matchAll(/(\d{4})-(\d{2})-(\d{2})/g)];
dates.forEach(match => {
    console.log(`完整日期: ${match[0]}, 年: ${match[1]}, 月: ${match[2]}, 日: ${match[3]}`);
});
// 完整日期: 2026-08-06, 年: 2026, 月: 08, 日: 06
// 完整日期: 2026-12-25, 年: 2026, 月: 12, 日: 25

// 实用：提取 HTML 标签
const html = '<div class="a">content1</div><span class="b">content2</span>';
const tags = [...html.matchAll(/<(\w+)\s+class="(\w+)">([^<]+)<\/\1>/g)];
tags.forEach(match => {
    console.log(`标签: ${match[1]}, 类名: ${match[2]}, 内容: ${match[3]}`);
});
// 标签: div, 类名: a, 内容: content1
// 标签: span, 类名: b, 内容: content2
```

### 10.3 `test()` - 测试是否匹配（RegExp 方法）

**函数签名**：`regexp.test(str)`

**参数说明**：
- `str`：要测试的字符串（`string`）

**返回值**：`boolean` - 是否匹配

**功能描述**：测试字符串是否匹配正则表达式，返回布尔值。

```javascript
const str = 'Hello World 123';

// 测试是否包含数字
console.log(/\d/.test(str));        // true
console.log(/[a-z]/.test(str));     // true
console.log(/xyz/.test(str));       // false

// 实用：表单验证
const validators = {
    email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    phone: /^1[3-9]\d{9}$/,
    url: /^https?:\/\/.+/,
    zipcode: /^\d{6}$/
};

function validate(type, value) {
    const regex = validators[type];
    return regex ? regex.test(value) : false;
}

console.log(validate('email', 'test@example.com'));    // true
console.log(validate('phone', '13812345678'));         // true
console.log(validate('email', 'invalid-email'));       // false
```

### 10.4 `exec()` - 执行匹配（RegExp 方法）

**函数签名**：`regexp.exec(str)`

**参数说明**：
- `str`：要匹配的字符串（`string`）

**返回值**：`Array<string>` | `null` - 匹配结果数组，无匹配返回 `null`

**功能描述**：在指定字符串中执行匹配搜索，返回匹配结果。带 `g` 标志时可循环调用以获取所有匹配。

```javascript
const str = 'Hello World 123 JavaScript 456';

// 单次匹配
console.log(/\d+/.exec(str));
// ['123', index: 12, input: 'Hello World 123 JavaScript 456', groups: undefined]

// 带 g 标志循环匹配
const regex = /\d+/g;
let match;
while ((match = regex.exec(str)) !== null) {
    console.log(`找到: ${match[0]}, 位置: ${match.index}`);
}
// 找到: 123, 位置: 12
// 找到: 456, 位置: 28

// ⚠️ 注意：带 g 标志时 exec 会修改 regex.lastIndex
// 现代 JS 推荐使用 matchAll() 代替
```

---

## 十一、ES6+ 新增字符串方法

### 11.1 模板字符串（Template Literals）

**语法**：`` `string ${expression} string` ``

**功能描述**：支持变量插值、多行字符串、表达式嵌入的字符串字面量。

```javascript
const name = 'Alice';
const age = 25;

// 变量插值
console.log(`Hello, ${name}! You are ${age} years old.`);
// 'Hello, Alice! You are 25 years old.'

// 表达式插值
console.log(`Next year you will be ${age + 1}.`);  // 'Next year you will be 26.'
console.log(`Name length: ${name.length}`);  // 'Name length: 5'

// 多行字符串
const html = `
<div>
    <h1>${name}</h1>
    <p>Age: ${age}</p>
</div>
`;

// 嵌套模板字符串
const items = ['apple', 'banana', 'cherry'];
const list = `
<ul>
    ${items.map(item => `<li>${item}</li>`).join('\n    ')}
</ul>
`;
console.log(list);

// 标签模板字符串
function highlight(strings, ...values) {
    return strings.reduce((result, str, i) => {
        const value = values[i] ? `<b>${values[i]}</b>` : '';
        return result + str + value;
    }, '');
}
console.log(highlight`Hello ${name}, you are ${age} years old`);
// 'Hello <b>Alice</b>, you are <b>25</b> years old'
```

### 11.2 `padStart()` - 前填充字符串（ES2017+）

**函数签名**：`str.padStart(targetLength[, padString])`

**参数说明**：
- `targetLength`：目标长度（`number`）
- `padString`（可选）：填充字符串，默认空格（`string`）

**返回值**：`string` - 填充后的新字符串

**功能描述**：在字符串开头填充指定字符，直到达到目标长度。

```javascript
console.log('5'.padStart(3, '0'));       // '005'
console.log('abc'.padStart(6, 'x'));     // 'xxxabc'
console.log('abc'.padStart(6));          // '   abc'（默认空格）
console.log('abc'.padStart(2, '0'));     // 'abc'（已超过目标长度，不截断）

// 实用：数字补零
function padNumber(num, len) {
    return String(num).padStart(len, '0');
}
console.log(padNumber(5, 3));      // '005'
console.log(padNumber(123, 5));    // '00123'

// 实用：格式化时间
function formatTime(hours, minutes, seconds) {
    return [hours, minutes, seconds]
        .map(n => String(n).padStart(2, '0'))
        .join(':');
}
console.log(formatTime(9, 5, 3));  // '09:05:03'

// 实用：对齐文本
const items = ['apple', 'banana', 'cherry'];
items.forEach(item => {
    console.log(`| ${item.padEnd(10)} |`);
});
// | apple      |
// | banana     |
// | cherry     |
```

### 11.3 `padEnd()` - 后填充字符串（ES2017+）

**函数签名**：`str.padEnd(targetLength[, padString])`

**参数说明**：
- `targetLength`：目标长度（`number`）
- `padString`（可选）：填充字符串，默认空格（`string`）

**返回值**：`string` - 填充后的新字符串

**功能描述**：在字符串末尾填充指定字符，直到达到目标长度。

```javascript
console.log('5'.padEnd(3, '0'));        // '500'
console.log('abc'.padEnd(6, 'x'));      // 'abcxxx'
console.log('abc'.padEnd(6));           // 'abc   '（默认空格）

// 实用：生成等宽分隔线
function divider(title, width = 40) {
    const line = '-'.repeat(width);
    return `${title}`.padEnd(width, '-');
}
console.log(divider('Section 1'));  // 'Section 1-------------------------'

// 实用：表格对齐
const data = [
    { name: 'Alice', score: 95 },
    { name: 'Bob', score: 88 },
    { name: 'Charlie', score: 72 }
];
console.log('Name'.padEnd(10) + 'Score');
console.log('-'.repeat(20));
data.forEach(item => {
    console.log(item.name.padEnd(10) + item.score);
});
// Name      Score
// --------------------
// Alice     95
// Bob       88
// Charlie   72
```

### 11.4 `normalize()` - Unicode 规范化（ES6+）

**函数签名**：`str.normalize([form])`

**参数说明**：
- `form`（可选）：规范化形式，`'NFC'` | `'NFD'` | `'NFKC'` | `'NFKD'`，默认 `'NFC'`（`string`）

**返回值**：`string` - 规范化后的字符串

**功能描述**：将字符串转换为 Unicode 规范化形式，处理组合字符。

```javascript
// NFC：组合形式（默认）
// NFD：分解形式
// NFKC：兼容性组合
// NFKD：兼容性分解

const composed = 'é';        // 一个字符
const decomposed = 'e\u0301'; // e + 组合重音

console.log(composed.length);          // 1
console.log(decomposed.length);        // 2
console.log(composed === decomposed);  // false（视觉相同但编码不同）

// 规范化后比较
console.log(composed === decomposed.normalize('NFC'));  // true

// 实用：统一用户输入比较
function normalizeCompare(a, b) {
    return a.normalize('NFC') === b.normalize('NFC');
}
console.log(normalizeCompare('café', 'cafe\u0301'));  // true
```

### 11.5 `raw()` - 原始字符串（ES6+）

**函数签名**：`String.raw(callSite, ...substitutions)` 或 `` String.raw`template` ``

**参数说明**：
- `callSite`：模板调用对象
- `substitutions`：替换值

**返回值**：`string` - 原始字符串（转义字符不处理）

**功能描述**：获取模板字符串的原始形式，反斜杠不作为转义字符。

```javascript
// 普通模板字符串会处理转义
console.log(`Hello\nWorld`);    // 换行输出
// Hello
// World

// raw 不处理转义
console.log(String.raw`Hello\nWorld`);  // 'Hello\nWorld'（字面量）

// 实用：显示正则表达式模式
const pattern = String.raw`\d+\.\d+`;
console.log(pattern);  // '\d+\.\d+'

// 实用：Windows 文件路径
const path = String.raw`C:\Users\Admin\Documents`;
console.log(path);  // 'C:\Users\Admin\Documents'
```

---

## 十二、字符编码操作

### 12.1 `charCodeAt()` vs `codePointAt()`

```javascript
// 基本字符（BMP 平面）
console.log('A'.charCodeAt(0));     // 65
console.log('A'.codePointAt(0));    // 65（结果相同）

// 辅助平面字符（如 emoji）
const emoji = '😀';
console.log(emoji.charCodeAt(0));   // 55357（代理对的高位）
console.log(emoji.charCodeAt(1));   // 56832（代理对的低位）
console.log(emoji.codePointAt(0));  // 128512（正确的码点）

// 结论：处理 emoji 等辅助平面字符时使用 codePointAt()
```

### 12.2 字符串与字符编码转换

```javascript
// 字符串转 UTF-8 字节数组
function stringToBytes(str) {
    return new TextEncoder().encode(str);
}
console.log(stringToBytes('Hello'));  // Uint8Array [72, 101, 108, 108, 111]
console.log(stringToBytes('中文'));    // Uint8Array [228, 184, 173, 230, 150, 135]

// 字节数组转字符串
function bytesToString(bytes) {
    return new TextDecoder().decode(bytes);
}
console.log(bytesToString(new Uint8Array([72, 101, 108, 108, 111])));  // 'Hello'

// Base64 编码解码（浏览器环境）
function encodeBase64(str) {
    return btoa(unescape(encodeURIComponent(str)));
}
function decodeBase64(base64) {
    return decodeURIComponent(escape(atob(base64)));
}
const encoded = encodeBase64('Hello 世界');
console.log(encoded);  // 'SGVsbG8g5LiW55uM'
console.log(decodeBase64(encoded));  // 'Hello 世界'
```

---

## 十三、实用工具函数封装

### 13.1 字符串验证工具集

```javascript
/**
 * 字符串验证工具集
 * 提供常用的字符串格式验证方法
 */
const StringValidator = {
    /**
     * 验证邮箱格式
     * @param {string} email - 邮箱地址
     * @returns {boolean} 是否合法
     */
    isEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    },

    /**
     * 验证中国大陆手机号
     * @param {string} phone - 手机号
     * @returns {boolean} 是否合法
     */
    isPhone(phone) {
        return /^1[3-9]\d{9}$/.test(phone);
    },

    /**
     * 验证 URL 格式
     * @param {string} url - URL 地址
     * @returns {boolean} 是否合法
     */
    isURL(url) {
        return /^https?:\/\/[^\s]+$/i.test(url);
    },

    /**
     * 验证身份证号（18 位）
     * @param {string} id - 身份证号
     * @returns {boolean} 是否合法
     */
    isIDCard(id) {
        return /^\d{17}[\dXx]$/.test(id);
    },

    /**
     * 验证 IP 地址
     * @param {string} ip - IP 地址
     * @returns {boolean} 是否合法
     */
    isIP(ip) {
        return /^(\d{1,3}\.){3}\d{1,3}$/.test(ip) &&
            ip.split('.').every(n => n >= 0 && n <= 255);
    },

    /**
     * 验证是否为纯数字
     * @param {string} str - 输入字符串
     * @returns {boolean} 是否为纯数字
     */
    isNumeric(str) {
        return /^\d+$/.test(str);
    },

    /**
     * 验证是否为空或仅空白
     * @param {string} str - 输入字符串
     * @returns {boolean} 是否为空
     */
    isEmpty(str) {
        return !str || str.trim().length === 0;
    }
};

// 使用示例
console.log(StringValidator.isEmail('test@example.com'));   // true
console.log(StringValidator.isPhone('13812345678'));        // true
console.log(StringValidator.isURL('https://example.com'));  // true
console.log(StringValidator.isNumeric('12345'));             // true
console.log(StringValidator.isEmpty('   '));                 // true
```

### 13.2 字符串格式化工具集

```javascript
/**
 * 字符串格式化工具集
 * 提供常用的字符串格式化方法
 */
const StringFormatter = {
    /**
     * 模板字符串替换
     * @param {string} template - 模板字符串，使用 {key} 占位
     * @param {Object} data - 替换数据
     * @returns {string} 格式化后的字符串
     */
    format(template, data) {
        return template.replace(/\{(\w+)\}/g, (match, key) => {
            return data[key] !== undefined ? String(data[key]) : match;
        });
    },

    /**
     * 手机号脱敏
     * @param {string} phone - 手机号
     * @returns {string} 脱敏后的手机号
     */
    maskPhone(phone) {
        return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
    },

    /**
     * 邮箱脱敏
     * @param {string} email - 邮箱
     * @returns {string} 脱敏后的邮箱
     */
    maskEmail(email) {
        const [name, domain] = email.split('@');
        const maskedName = name.length > 2 
            ? name[0] + '*'.repeat(name.length - 2) + name[name.length - 1]
            : '*'.repeat(name.length);
        return `${maskedName}@${domain}`;
    },

    /**
     * 身份证脱敏
     * @param {string} id - 身份证号
     * @returns {string} 脱敏后的身份证
     */
    maskIDCard(id) {
        return id.replace(/(\d{4})\d{10}(\d{4})/, '$1**********$2');
    },

    /**
     * 千分位格式化
     * @param {number|string} num - 数字
     * @returns {string} 格式化后的字符串
     */
    thousandSeparator(num) {
        return String(num).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    },

    /**
     * 文本截断
     * @param {string} str - 原字符串
     * @param {number} maxLen - 最大长度
     * @param {string} suffix - 截断后缀，默认 '...'
     * @returns {string} 截断后的字符串
     */
    truncate(str, maxLen, suffix = '...') {
        return str.length > maxLen 
            ? str.slice(0, maxLen - suffix.length) + suffix 
            : str;
    },

    /**
     * 驼峰转下划线
     * @param {string} str - 驼峰字符串
     * @returns {string} 下划线字符串
     */
    camelToSnake(str) {
        return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
    },

    /**
     * 下划线转驼峰
     * @param {string} str - 下划线字符串
     * @returns {string} 驼峰字符串
     */
    snakeToCamel(str) {
        return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
    },

    /**
     * 首字母大写
     * @param {string} str - 原字符串
     * @returns {string} 首字母大写的字符串
     */
    capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
};

// 使用示例
console.log(StringFormatter.format('Hello {name}, age {age}', 
    { name: 'Alice', age: 25 }));  // 'Hello Alice, age 25'
console.log(StringFormatter.maskPhone('13812345678'));       // '138****5678'
console.log(StringFormatter.maskEmail('alice@example.com')); // 'a****e@example.com'
console.log(StringFormatter.thousandSeparator(1234567));     // '1,234,567'
console.log(StringFormatter.truncate('Hello World JavaScript', 10));  // 'Hello W...'
console.log(StringFormatter.camelToSnake('helloWorld'));     // 'hello_world'
console.log(StringFormatter.snakeToCamel('hello_world'));    // 'helloWorld'
console.log(StringFormatter.capitalize('hello'));            // 'Hello'
```

### 13.3 字符串转换工具集

```javascript
/**
 * 字符串转换工具集
 * 提供常用的大小写、编码、类型转换方法
 */
const StringConverter = {
    /**
     * 转换为 kebab-case
     * @param {string} str - 输入字符串
     * @returns {string} kebab-case 字符串
     */
    toKebabCase(str) {
        return str
            .replace(/([a-z])([A-Z])/g, '$1-$2')
            .replace(/[\s_]+/g, '-')
            .toLowerCase();
    },

    /**
     * 转换为 camelCase
     * @param {string} str - 输入字符串
     * @returns {string} camelCase 字符串
     */
    toCamelCase(str) {
        return str
            .replace(/[-_\s]+(.)/g, (_, char) => char.toUpperCase())
            .replace(/^(.)/, char => char.toLowerCase());
    },

    /**
     * 转换为 PascalCase
     * @param {string} str - 输入字符串
     * @returns {string} PascalCase 字符串
     */
    toPascalCase(str) {
        const camel = this.toCamelCase(str);
        return camel.charAt(0).toUpperCase() + camel.slice(1);
    },

    /**
     * 转换为 snake_case
     * @param {string} str - 输入字符串
     * @returns {string} snake_case 字符串
     */
    toSnakeCase(str) {
        return str
            .replace(/([a-z])([A-Z])/g, '$1_$2')
            .replace(/[\s-]+/g, '_')
            .toLowerCase();
    },

    /**
     * 反转字符串
     * @param {string} str - 原字符串
     * @returns {string} 反转后的字符串
     */
    reverse(str) {
        // 使用扩展运算符正确处理 emoji 等辅助平面字符
        return [...str].reverse().join('');
    },

    /**
     * 统计字符数（正确处理 emoji）
     * @param {string} str - 输入字符串
     * @returns {number} 字符数
     */
    charCount(str) {
        return [...str].length;
    },

    /**
     * 去除 HTML 标签
     * @param {string} html - HTML 字符串
     * @returns {string} 纯文本
     */
    stripHTML(html) {
        return html.replace(/<[^>]*>/g, '');
    },

    /**
     * HTML 转义
     * @param {string} str - 原字符串
     * @returns {string} 转义后的字符串
     */
    escapeHTML(str) {
        const escapeMap = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        };
        return str.replace(/[&<>"']/g, char => escapeMap[char]);
    },

    /**
     * HTML 反转义
     * @param {string} str - 转义后的字符串
     * @returns {string} 原字符串
     */
    unescapeHTML(str) {
        const unescapeMap = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'"
        };
        return str.replace(/&(amp|lt|gt|quot|#39);/g, 
            match => unescapeMap[match]);
    }
};

// 使用示例
console.log(StringConverter.toKebabCase('HelloWorld'));    // 'hello-world'
console.log(StringConverter.toCamelCase('hello-world'));   // 'helloWorld'
console.log(StringConverter.toPascalCase('hello world'));  // 'HelloWorld'
console.log(StringConverter.toSnakeCase('HelloWorld'));    // 'hello_world'
console.log(StringConverter.reverse('Hello'));             // 'olleH'
console.log(StringConverter.reverse('😀Hello'));           // 'olleH😀'（正确处理 emoji）
console.log(StringConverter.charCount('😀Hello'));         // 6（正确计数）
console.log(StringConverter.stripHTML('<p>Hello</p>'));    // 'Hello'
console.log(StringConverter.escapeHTML('<script>alert("xss")</script>'));
// '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;'
```

---

## 十四、API 速查表

### 14.1 字符串方法速查表

| 方法 | 功能 | 是否修改原串 | ES 版本 | 返回值 |
|------|------|:----------:|:-------:|--------|
| `String(value)` | 转换为字符串 | - | ES1 | `string` |
| `toString([radix])` | 转换为字符串 | - | ES1 | `string` |
| `charAt(index)` | 获取指定位置字符 | ❌ | ES1 | `string` |
| `charCodeAt(index)` | 获取字符编码 | ❌ | ES1 | `number` |
| `codePointAt(pos)` | 获取字符码点 | ❌ | ES6 | `number` |
| `concat(...strs)` | 拼接字符串 | ❌ | ES1 | `string` |
| `indexOf(sub[, from])` | 从前查找位置 | ❌ | ES1 | `number` |
| `lastIndexOf(sub[, from])` | 从后查找位置 | ❌ | ES1 | `number` |
| `includes(sub[, pos])` | 是否包含 | ❌ | ES6 | `boolean` |
| `startsWith(sub[, pos])` | 是否开头匹配 | ❌ | ES6 | `boolean` |
| `endsWith(sub[, len])` | 是否结尾匹配 | ❌ | ES6 | `boolean` |
| `slice(start[, end])` | 截取子串 | ❌ | ES1 | `string` |
| `substring(start[, end])` | 截取子串 | ❌ | ES1 | `string` |
| `substr(start[, len])` | 截取子串（废弃） | ❌ | ES1 | `string` |
| `at(index)` | 获取位置字符 | ❌ | ES2022 | `string\|undefined` |
| `split([sep[, limit]])` | 分割为数组 | ❌ | ES1 | `Array<string>` |
| `replace(pattern, repl)` | 替换首个 | ❌ | ES1 | `string` |
| `replaceAll(pattern, repl)` | 替换所有 | ❌ | ES2021 | `string` |
| `match(regexp)` | 匹配正则 | ❌ | ES1 | `Array\|null` |
| `matchAll(regexp)` | 匹配所有 | ❌ | ES2020 | `Iterator` |
| `search(regexp)` | 搜索位置 | ❌ | ES1 | `number` |
| `toUpperCase()` | 转大写 | ❌ | ES1 | `string` |
| `toLowerCase()` | 转小写 | ❌ | ES1 | `string` |
| `trim()` | 去两端空白 | ❌ | ES5 | `string` |
| `trimStart()` | 去左侧空白 | ❌ | ES2019 | `string` |
| `trimEnd()` | 去右侧空白 | ❌ | ES2019 | `string` |
| `repeat(count)` | 重复字符串 | ❌ | ES6 | `string` |
| `padStart(len[, str])` | 前填充 | ❌ | ES2017 | `string` |
| `padEnd(len[, str])` | 后填充 | ❌ | ES2017 | `string` |
| `localeCompare(str)` | 本地化比较 | ❌ | ES1 | `number` |
| `normalize([form])` | Unicode 规范化 | ❌ | ES6 | `string` |
| `valueOf()` | 返回原始值 | - | ES1 | `string` |

### 14.2 静态方法速查表

| 方法 | 功能 | ES 版本 | 返回值 |
|------|------|:-------:|--------|
| `String.fromCharCode(...codes)` | 从编码创建字符串 | ES1 | `string` |
| `String.fromCodePoint(...points)` | 从码点创建字符串 | ES6 | `string` |
| `String.raw` | 原始字符串 | ES6 | `string` |

### 14.3 正则相关方法对比

| 方法 | 所属 | 返回值 | 说明 |
|------|------|--------|------|
| `str.match(regexp)` | String | `Array\|null` | 返回匹配结果 |
| `str.matchAll(regexp)` | String | `Iterator` | 返回所有匹配（需 `g` 标志） |
| `str.search(regexp)` | String | `number` | 返回首次匹配索引 |
| `str.replace(regexp, str)` | String | `string` | 替换匹配项 |
| `regexp.test(str)` | RegExp | `boolean` | 测试是否匹配 |
| `regexp.exec(str)` | RegExp | `Array\|null` | 执行匹配搜索 |

---

## 十五、总结与最佳实践

### 15.1 方法选择指南

```
┌─────────────────────────────────────────────────────────────────┐
│                    字符串操作方法选择决策树                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 查找子字符串位置？                                          │
│     ├── 需要正则 → search()                                     │
│     ├── 从前找 → indexOf()                                      │
│     └── 从后找 → lastIndexOf()                                  │
│                                                                 │
│  2. 判断是否包含？                                              │
│     ├── 包含子串 → includes()（ES6+，推荐）                     │
│     ├── 开头匹配 → startsWith()                                 │
│     └── 结尾匹配 → endsWith()                                   │
│                                                                 │
│  3. 截取子字符串？                                              │
│     └── slice()（推荐，支持负数索引）                           │
│                                                                 │
│  4. 替换字符串？                                                │
│     ├── 替换第一个 → replace()                                  │
│     └── 替换所有 → replaceAll()（ES2021+）                      │
│                                                                 │
│  5. 匹配正则？                                                  │
│     ├── 仅判断 → test()                                         │
│     ├── 获取第一个 → match()                                    │
│     └── 获取所有 → matchAll()                                   │
│                                                                 │
│  6. 去除空白？                                                  │
│     ├── 两端 → trim()                                           │
│     ├── 左侧 → trimStart()                                      │
│     └── 右侧 → trimEnd()                                        │
│                                                                 │
│  7. 字符串拼接？                                                │
│     └── 模板字符串（推荐，可读性最佳）                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 15.2 性能最佳实践

```javascript
// 1. 大量拼接使用数组 join（性能优于 + 连续拼接）
const parts = [];
for (let i = 0; i < 1000; i++) {
    parts.push(`item${i}`);
}
const result = parts.join('');  // 比 result += `item${i}` 快

// 2. 避免在循环中使用 replace
// ❌ 慢
let str = 'hello';
for (let i = 0; i < 100; i++) {
    str = str.replace('l', 'L');
}
// ✅ 快：使用正则一次性替换
str = str.replace(/l/g, 'L');

// 3. 查找时优先使用 includes() 而非 indexOf() !== -1
// includes() 语义更清晰，性能相当
if (str.includes('sub')) { ... }

// 4. 截取统一使用 slice()
// 支持负数索引，功能最全
const sub = str.slice(0, 10);
```

### 15.3 常见陷阱与注意事项

```javascript
// 1. 字符串不可变：所有方法返回新字符串
let str = 'Hello';
str.toUpperCase();  // 返回新字符串，str 不变
console.log(str);   // 'Hello'
str = str.toUpperCase();  // 必须重新赋值

// 2. indexOf 返回 -1 而非 falsy 值
// ❌ 错误：indexOf 在位置 0 时返回 0，会被判断为 false
if (str.indexOf('sub')) { ... }
// ✅ 正确
if (str.indexOf('sub') !== -1) { ... }
// ✅ 更好：使用 includes()
if (str.includes('sub')) { ... }

// 3. replace 默认只替换第一个
'aaa'.replace('a', 'b');      // 'baa'（只替换第一个）
'aaa'.replaceAll('a', 'b');   // 'bbb'（替换所有）
'aaa'.replace(/a/g, 'b');     // 'bbb'（正则带 g 标志）

// 4. Unicode 字符处理
// ❌ 错误：split('') 会破坏 emoji
'D😀D'.split('').reverse().join('');  // 乱码
// ✅ 正确：使用扩展运算符
[...'D😀D'].reverse().join('');  // 'D😀D'

// 5. 数字字符串比较不是自然序
'10' < '9';  // true（字典序，'1' < '9'）
// 正确做法：转换为数字比较
Number('10') < Number('9');  // false

// 6. trim() 只去除两端空白
'  Hello   World  '.trim();  // 'Hello   World'（中间空白保留）
```

### 15.4 核心要点总结

| 要点 | 说明 |
|------|------|
| **不可变性** | 所有字符串方法返回新字符串，原字符串不变 |
| **方法选择** | `slice()` 优于 `substring()` 和 `substr()` |
| **查找判断** | `includes()` / `startsWith()` / `endsWith()` 语义清晰 |
| **正则替换** | `replace()` 替换首个，`replaceAll()` 替换所有 |
| **Unicode** | 处理 emoji 使用 `codePointAt()`、`[...str]`、`Array.from()` |
| **本地化** | 排序使用 `localeCompare()`，大小写使用 `toLocaleUpperCase()` |
| **性能** | 大量拼接用数组 `join()`，避免循环中 `replace` |
| **模板字符串** | ES6+ 推荐使用模板字符串拼接，可读性最佳 |

---

## 参考资料

- [MDN: String 对象](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/String)
- [MDN: 正则表达式](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Guide/Regular_Expressions)
- [ECMAScript 规范: String](https://tc39.es/ecma262/#sec-string-objects)
- [MDN: 模板字符串](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Template_literals)
- [MDN: TextEncoder/TextDecoder](https://developer.mozilla.org/zh-CN/docs/Web/API/TextEncoder)
