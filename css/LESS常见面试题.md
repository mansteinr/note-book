# LESS 常见面试题

> 本文档系统整理 LESS 核心知识点，涵盖变量、混合、嵌套、函数与运算、作用域、导入等核心语法，并结合实际项目场景与高频面试题进行深入解析，适合不同层次的前端开发者学习和面试准备。

---

## 目录

- [一、LESS 简介与核心概念](#一less-简介与核心概念)
- [二、变量定义与使用](#二变量定义与使用)
- [三、混合 Mixins](#三混合-mixins)
- [四、嵌套规则](#四嵌套规则)
- [五、函数与运算](#五函数与运算)
- [六、作用域](#六作用域)
- [七、导入 Import](#七导入-import)
- [八、高级语法特性](#八高级语法特性)
- [九、LESS 与 SCSS 对比](#九less-与-scss-对比)
- [十、面试题集锦](#十面试题集锦)
- [附录：考点速查表](#附录考点速查表)

---

## 一、LESS 简介与核心概念

### 1.1 什么是 LESS？

LESS（Leaner Style Sheets）是一种 CSS 预处理器，由 Alexis Sellier 于 2009 年创建。它在 CSS 语法基础上扩展了**变量、混合、嵌套、函数、运算**等特性，使 CSS 更易维护、更具可复用性。LESS 最终需要编译为标准的 CSS 才能在浏览器中运行。

**核心特点：**

| 特性 | 说明 |
|------|------|
| 向后兼容 CSS | 任何合法的 CSS 代码都是合法的 LESS 代码 |
| 可在浏览器端运行 | 引入 `less.js` 即可在浏览器中实时编译（开发阶段） |
| Node.js 环境编译 | 通过 `lessc` 命令行工具或构建工具（Webpack、Gulp）编译 |
| 变量 | 使用 `@` 符号定义，支持作用域和延迟加载 |
| 混合 Mixins | 将一组 CSS 规则封装复用，可带参数 |
| 嵌套 | 模仿 HTML 结构编写 CSS 层级关系 |
| 运算 | 支持数值、颜色、单位的数学运算 |
| 函数 | 内置丰富的颜色、字符串、数学处理函数 |

### 1.2 LESS 编译方式

```bash
# 使用 npm 安装 LESS
npm install -g less

# 命令行编译
lessc styles.less styles.css

# 压缩输出
lessc styles.less styles.min.css --clean-css

# 监听文件变化自动编译
lessc --watch styles.less styles.css
```

**浏览器端直接使用（仅开发环境）：**

```html
<!-- 先引入 LESS 文件 -->
<link rel="stylesheet/less" type="text/css" href="styles.less" />
<!-- 再引入 less.js -->
<script src="https://cdn.jsdelivr.net/npm/less@4"></script>
```

---

## 二、变量定义与使用

### 2.1 变量基础

LESS 变量以 `@` 开头，使用冒号 `:` 赋值，分号 `;` 结尾。变量支持**延迟加载**（Lazy Loading），即变量可以在声明之前使用，LESS 会以当前作用域内最后一次赋值为准。

```less
// ===== 变量定义 =====
@primary-color: #1890ff;
@link-color: @primary-color;
@font-size-base: 14px;
@border-radius: 4px;
@font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

// 变量支持任何 CSS 属性值
@my-selector: banner;
@my-property: color;
@images: "../images";

// ===== 变量使用 =====
.button {
  background-color: @primary-color;
  font-size: @font-size-base;
  border-radius: @border-radius;
  font-family: @font-family;
}

// 变量用作选择器或属性名（插值语法）
.@{my-selector} {
  @{my-property}: @primary-color;
  background: url("@{images}/bg.png");
}
```

### 2.2 变量插值

变量插值允许将变量嵌入到选择器名、属性名、URL、`@import` 语句中。

```less
// 选择器插值
@component: card;

.@{component} {
  padding: 20px;
  &__title { font-size: 18px; }
  &__body { margin-top: 10px; }
}

// 编译为：
// .card { padding: 20px; }
// .card__title { font-size: 18px; }
// .card__body { margin-top: 10px; }

// 属性名插值
@direction: left;
.box {
  margin-@{direction}: 20px;
  padding-@{direction}: 10px;
}

// URL 插值
@base-url: "https://cdn.example.com";
.logo {
  background-image: url("@{base-url}/logo.png");
}

// @import 插值
@theme: "dark";
@import "@{theme}/variables";  // 导入 dark/variables.less
```

### 2.3 变量作用域与延迟加载

```less
// 延迟加载（Lazy Loading）—— LESS 的核心特性
// 变量在声明之前也可以使用，最终使用当前作用域内最后一次赋值的值

@color: blue;

.box {
  @color: red;
  .inner {
    color: @color;  // 最终取值：green（作用域内最后一次赋值）
    @color: green;
  }
  color: @color;    // 最终取值：red
}

// 编译为：
// .box { color: red; }
// .box .inner { color: green; }
```

### 2.4 变量用作属性值

```less
// 使用 $property 语法，可将变量作为属性值引用
.widget {
  color: #efefef;
  background-color: $color;  // $color 引用当前选择器中 color 属性的值
}

// 编译为：
// .widget {
//   color: #efefef;
//   background-color: #efefef;
// }
```

---

### 面试题速览（变量相关）

| 编号 | 问题 | 难度 |
|------|------|------|
| Q1 | LESS 变量如何定义？有哪些使用场景？ | 初级 |
| Q2 | 什么是 LESS 的延迟加载？举例说明 | 中级 |
| Q3 | `@variable` 和 `@{variable}` 有什么区别？ | 中级 |
| Q4 | `$property` 语法的作用是什么？ | 中级 |

---

## 三、混合 Mixins

### 3.1 基础混合

混合（Mixin）是将一组 CSS 规则封装为一个可复用的代码块，通过选择器调用或函数调用方式引入。

```less
// 定义混合（类选择器方式）
.bordered {
  border: 1px solid #ddd;
  border-radius: 4px;
}

// 调用混合
.panel {
  .bordered();     // 带括号调用
  background: #fff;
}

.card {
  .bordered;       // 不带括号也可以（如果混合不带参数）
  margin: 10px;
}

// 编译为：
// .panel {
//   border: 1px solid #ddd;
//   border-radius: 4px;
//   background: #fff;
// }
// .card {
//   border: 1px solid #ddd;
//   border-radius: 4px;
//   margin: 10px;
// }
```

### 3.2 带参数的混合

```less
// 带默认参数的混合
.border-radius(@radius: 4px) {
  -webkit-border-radius: @radius;
  -moz-border-radius: @radius;
  border-radius: @radius;
}

// 调用
.btn {
  .border-radius(6px);  // 传入参数
}
.avatar {
  .border-radius();     // 使用默认值 4px
}

// 多参数混合
.box-shadow(@x: 0, @y: 2px, @blur: 4px, @color: rgba(0,0,0,.15)) {
  box-shadow: @x @y @blur @color;
}

.card {
  .box-shadow(0, 4px, 8px, rgba(0,0,0,.2));
}
```

### 3.3 @arguments 变量

`@arguments` 代表所有传入参数，用于一次性传递所有参数。

```less
.transition(@property: all, @duration: .3s, @timing: ease) {
  transition: @arguments;  // 等价于 transition: @property @duration @timing;
}

.button {
  .transition(width, .5s, ease-in-out);
}
// 编译为：
// .button { transition: width .5s ease-in-out; }
```

### 3.4 可变参数 @rest

```less
// 使用 ... 接收可变数量的参数
.box-shadow(...) {
  box-shadow: @arguments;
}

// 调用
.shadow-sm { .box-shadow(0 1px 2px rgba(0,0,0,.1)); }
.shadow-lg { .box-shadow(0 4px 8px rgba(0,0,0,.15), 0 2px 4px rgba(0,0,0,.1)); }
```

### 3.5 模式匹配

通过为同名混合添加不同的参数标识（第一个参数作为匹配标识），实现条件分支效果。

```less
// 模式匹配：根据第一个参数决定执行哪个混合
// 参数 @_ 表示匹配所有情况

.triangle(top, @width: 10px, @color: #333) {
  border-width: @width;
  border-color: transparent transparent @color transparent;
  border-style: solid;
}
.triangle(bottom, @width: 10px, @color: #333) {
  border-width: @width;
  border-color: @color transparent transparent transparent;
  border-style: solid;
}
.triangle(left, @width: 10px, @color: #333) {
  border-width: @width;
  border-color: transparent @color transparent transparent;
  border-style: solid;
}
.triangle(right, @width: 10px, @color: #333) {
  border-width: @width;
  border-color: transparent transparent transparent @color;
  border-style: solid;
}
// 公共样式，所有模式匹配都会执行
.triangle(@_, @width: 10px, @color: #333) {
  width: 0;
  height: 0;
}

// 调用
.arrow-up { .triangle(top, 8px, #f00); }
.arrow-down { .triangle(bottom); }
```

### 3.6 混合作为函数

混合可以返回值，类似于函数。

```less
.average(@x, @y) {
  @result: ((@x + @y) / 2);
}

.container {
  .average(16px, 24px);  // 调用混合，此时 @result 变量在当前作用域中可用
  padding: @result;
}

// 编译为：
// .container { padding: 20px; }
```

### 3.7 !important 关键字

在调用混合时使用 `!important`，会将混合内所有属性标记为 `!important`。

```less
.error-text() {
  color: red;
  font-size: 14px;
}

.alert {
  .error-text() !important;
}

// 编译为：
// .alert {
//   color: red !important;
//   font-size: 14px !important;
// }
```

---

### 面试题速览（混合相关）

| 编号 | 问题 | 难度 |
|------|------|------|
| Q5 | 什么是 LESS 混合？如何定义和调用？ | 初级 |
| Q6 | 带参数的混合如何使用？默认参数如何设置？ | 初级 |
| Q7 | `@arguments` 的作用是什么？ | 中级 |
| Q8 | 什么是模式匹配？举一个实际应用场景 | 高级 |
| Q9 | 混合如何作为函数返回值？ | 高级 |
| Q10 | 调用混合时加 `!important` 有什么效果？ | 中级 |

---

## 四、嵌套规则

### 4.1 基础嵌套

嵌套规则允许将 CSS 选择器按照 HTML 层级结构嵌套编写，减少重复书写。

```less
// LESS 嵌套写法
.nav {
  background: #333;
  ul {
    margin: 0;
    padding: 0;
    list-style: none;
  }
  li {
    display: inline-block;
  }
  a {
    display: block;
    padding: 10px 15px;
    color: #fff;
    text-decoration: none;
  }
}

// 编译为：
// .nav { background: #333; }
// .nav ul { margin: 0; padding: 0; list-style: none; }
// .nav li { display: inline-block; }
// .nav a { display: block; padding: 10px 15px; color: #fff; text-decoration: none; }
```

### 4.2 父选择器 & 的使用

`&` 代表当前选择器的父级，在嵌套中非常常用。

```less
// 伪类、伪元素
.btn {
  color: #fff;
  background: #1890ff;

  &:hover { background: #40a9ff; }
  &:active { background: #096dd9; }
  &:focus { outline: 2px solid #69c0ff; }
  &.disabled { opacity: .5; pointer-events: none; }
}

// 编译为：
// .btn { color: #fff; background: #1890ff; }
// .btn:hover { background: #40a9ff; }
// .btn:active { background: #096dd9; }
// .btn:focus { outline: 2px solid #69c0ff; }
// .btn.disabled { opacity: .5; pointer-events: none; }

// BEM 命名法
.block {
  &__element { color: red; }
  &--modifier { color: blue; }
  &__element--modifier { color: green; }
}

// 编译为：
// .block__element { color: red; }
// .block--modifier { color: blue; }
// .block__element--modifier { color: green; }
```

### 4.3 多重 & 嵌套

```less
// & 可多次使用生成复合选择器
.grand {
  .parent {
    & & {
      color: red;  // 匹配 .grand .parent .grand .parent
    }
    && {
      color: blue;  // 匹配 .grand .parent.grand .parent
    }
  }
}
```

### 4.4 @media 嵌套

```less
.component {
  width: 100%;

  @media (min-width: 768px) {
    width: 50%;
  }
  @media (min-width: 1024px) {
    width: 33.33%;
  }
}

// 编译为：
// .component { width: 100%; }
// @media (min-width: 768px) { .component { width: 50%; } }
// @media (min-width: 1024px) { .component { width: 33.33%; } }
```

### 4.5 嵌套中的冒泡

`@media` 和 `@supports` 等指令在嵌套中会发生冒泡，被提升到顶层。

```less
.sidebar {
  width: 300px;
  @media (max-width: 768px) {
    width: 100%;
  }
  @supports (display: grid) {
    grid-area: sidebar;
  }
}

// 编译为：
// .sidebar { width: 300px; }
// @media (max-width: 768px) { .sidebar { width: 100%; } }
// @supports (display: grid) { .sidebar { grid-area: sidebar; } }
```

---

### 面试题速览（嵌套相关）

| 编号 | 问题 | 难度 |
|------|------|------|
| Q11 | LESS 嵌套规则如何工作？& 的作用是什么？ | 初级 |
| Q12 | 嵌套过深会有什么问题？如何避免？ | 中级 |
| Q13 | `@media` 在嵌套中如何编译？ | 中级 |

---

## 五、函数与运算

### 5.1 数值运算

LESS 支持加（+）、减（-）、乘（*）、除（/）四种运算，可对数字、颜色、变量进行运算。

```less
@base: 5%;
@filler: @base * 2;     // 10%
@other: @base + @filler; // 15%

@width: 100px;
@half: @width / 2;       // 50px

// 带单位的运算
@padding: 20px;
.box {
  width: 100% - 20px;          // 混合单位运算
  padding: @padding * 2;       // 40px
  margin: (10px + 20px) / 2;   // 15px（括号改变运算优先级）
  line-height: 24px / 2 + 1;   // 12px + 1 = 13px
}

// 颜色运算
@color1: #224488;
@color2: #112244;
.mix {
  background: @color1 + @color2;  // #3366cc（颜色通道分别相加）
  color: @color1 * 0.5;           // 颜色变暗
}
```

### 5.2 calc() 与 LESS 运算

```less
// calc() 中的表达式不会被 LESS 计算，保持原样输出
@width: 100px;
.box {
  width: calc(100% - @width);  // LESS 先替换 @width，输出 calc(100% - 100px)
  height: calc(~"100% - 50px"); // 使用 ~"" 转义，完全避免 LESS 计算
}
```

### 5.3 内置函数大全

#### 5.3.1 颜色函数

```less
// 颜色定义
@base: #1890ff;

// 颜色通道提取
@hue: hue(@base);           // 色相
@saturation: saturation(@base); // 饱和度
@lightness: lightness(@base);   // 亮度

// 颜色调整
lighten(@base, 10%);     // 变亮
darken(@base, 10%);      // 变暗
saturate(@base, 10%);    // 增加饱和度
desaturate(@base, 10%);  // 降低饱和度
fadein(@base, 10%);      // 降低透明度
fadeout(@base, 10%);     // 增加透明度
fade(@base, 50%);        // 设置透明度 0-100%
spin(@base, 30);         // 色相旋转（角度）

// 颜色混合
mix(@base, #ff0000, 50%);  // 混合两种颜色，权重 50%

// 实际应用
@primary: #1890ff;
@primary-hover: lighten(@primary, 10%);
@primary-active: darken(@primary, 10%);
@primary-disabled: fade(@primary, 40%);
@primary-border: fade(@primary, 20%);

.btn-primary {
  background: @primary;
  &:hover { background: @primary-hover; }
  &:active { background: @primary-active; }
  &:disabled { background: @primary-disabled; }
  border: 1px solid @primary-border;
}
```

#### 5.3.2 数学函数

```less
// 数值处理
ceil(2.4);     // 3  — 向上取整
floor(2.6);    // 2  — 向下取整
round(2.5);    // 3  — 四舍五入
round(2.5, 1); // 2.5 — 保留一位小数
percentage(0.5); // 50%
abs(-5px);     // 5px
min(10px, 20px, 5px); // 5px
max(10px, 20px, 5px); // 20px
mod(11, 3);    // 2  — 取模运算
pow(2, 8);     // 256 — 幂运算
sqrt(25);      // 5  — 平方根
sin(1);        // 正弦（弧度）
cos(1);        // 余弦
pi();          // 圆周率
```

#### 5.3.3 字符串函数

```less
escape('a=1');          // 转义特殊字符为 URL 编码
e('ms:alwaysHasItsOwnSyntax'); // 类似 ~""，转义字符串但不编码
%('Hello %s', 'World');        // 格式化字符串 → "Hello World"
replace('Hello, World', 'World', 'LESS'); // 字符串替换 → "Hello, LESS"
length('hello world');         // 字符串长度
extract('a b c', 2);           // 提取列表第 n 项 → "b"
```

#### 5.3.4 类型判断函数

```less
isnumber(10px);        // true
isstring('text');      // true
iscolor(#fff);         // true
iscolor(red);          // true
iskeyword(keyword);    // true
isurl(url(...));       // true
ispixel(10px);         // true
ispercentage(10%);     // true
isem(10em);            // true
isunit(10px, px);      // true

// 实际应用：确保输出值类型正确
.set-width(@value) when (ispixel(@value)) {
  width: @value;
}
.set-width(@value) when (ispercentage(@value)) {
  width: @value;
}
```

#### 5.3.5 颜色定义函数

```less
// 使用函数创建颜色
rgb(255, 0, 0);        // #ff0000
rgba(255, 0, 0, 0.5);  // rgba(255, 0, 0, 0.5)
hsl(90, 100%, 50%);    // 使用 HSL 色值
hsla(90, 100%, 50%, 0.5);
hsv(90, 100%, 50%);    // 使用 HSV 色值
hsva(90, 100%, 50%, 0.5);
argb(rgba(255, 0, 0, 0.5)); // #80ff0000（ARGB 格式，用于 IE 滤镜）
```

---

### 面试题速览（函数与运算相关）

| 编号 | 问题 | 难度 |
|------|------|------|
| Q14 | LESS 支持哪些运算？有什么注意事项？ | 初级 |
| Q15 | `lighten()` 和 `darken()` 的实现原理是什么？ | 中级 |
| Q16 | 如何在 LESS 中创建主题色变体系统？ | 中级 |
| Q17 | `calc()` 和 LESS 运算如何共存？ | 中级 |

---

## 六、作用域

### 6.1 作用域基础

LESS 中的作用域类似于 JavaScript 的词法作用域，变量和混合先在当前作用域查找，找不到时向上级作用域查找。

```less
@global-color: #333;

.outer {
  @color: blue;
  color: @color;

  .inner {
    @color: red;
    color: @color;  // 先在 .inner 中找，找到 red
    background: @global-color;  // .inner 没有，向上找 .outer，再向上找全局
  }

  .another {
    color: @color;  // 在 .outer 中找，找到 blue
  }
}

// 编译为：
// .outer { color: blue; }
// .outer .inner { color: red; background: #333; }
// .outer .another { color: blue; }
```

### 6.2 延迟加载（Lazy Loading）

这是 LESS 与 SCSS 最重要的区别之一。**变量在声明之前就可以使用**，最终取值为当前作用域内最后一次声明。

```less
// 延迟加载示例
@var: 0;

.class {
  @var: 1;
  .sub {
    @var: 2;
    value: @var;     // 输出 3（取作用域内最后一次赋值）
    @var: 3;
  }
  value: @var;       // 输出 1
  @var: 4;           // 在 .class 作用域中最后赋值为 4，但 .sub 中的 @var 已经被解析为 3
}

// 编译为：
// .class { value: 1; }
// .class .sub { value: 3; }
```

**延迟加载的实际意义：**

```less
// 可以利用延迟加载实现"先使用，后定义"的模式
.theme {
  color: @text-color;
  background: @bg-color;
}

.theme-light {
  @text-color: #333;
  @bg-color: #fff;
  .theme();
}

.theme-dark {
  @text-color: #eee;
  @bg-color: #222;
  .theme();
}
```

---

### 面试题速览（作用域相关）

| 编号 | 问题 | 难度 |
|------|------|------|
| Q18 | 什么是 LESS 的延迟加载？与 SCSS 有什么区别？ | 中级 |
| Q19 | LESS 作用域查找规则是什么？ | 初级 |
| Q20 | 延迟加载在实际项目中有什么应用场景？ | 高级 |

---

## 七、导入 Import

### 7.1 @import 基础

`@import` 用于导入其他 LESS 或 CSS 文件，实现模块化样式管理。

```less
// 导入 LESS 文件（.less 扩展名可省略）
@import "variables";
@import "mixins";
@import "reset";

// 导入 CSS 文件（保留 .css 扩展名，会编译为标准 CSS @import）
@import "normalize.css";

// 导入多个文件
@import "variables", "mixins", "components/button";
```

### 7.2 @import 选项

```less
// reference：导入但不输出到最终 CSS（仅用于引用变量和混合）
@import (reference) "mixins";

// once（默认）：只导入一次，重复导入会被忽略
@import (once) "variables";

// multiple：允许多次导入
@import (multiple) "variables";

// less：将导入文件视为 LESS 文件（无论扩展名）
@import (less) "styles.css";

// css：将导入文件视为 CSS 文件
@import (css) "styles.less";

// inline：内联导入，不处理文件内容直接输出
@import (inline) "external.css";

// optional：文件不存在时不报错
@import (optional) "missing-file";

// 组合使用
@import (optional, reference) "optional-mixins";
```

### 7.3 模块化组织方式

```
styles/
├── main.less              # 入口文件
├── variables/
│   ├── colors.less        # 颜色变量
│   ├── typography.less    # 字体变量
│   └── spacing.less       # 间距变量
├── mixins/
│   ├── layout.less        # 布局混合
│   ├── text.less          # 文字混合
│   └── responsive.less    # 响应式混合
├── base/
│   ├── reset.less         # 重置样式
│   └── typography.less    # 基础排版
├── components/
│   ├── button.less
│   ├── form.less
│   └── modal.less
└── pages/
    ├── home.less
    └── about.less
```

```less
// main.less 入口文件
@import "variables/colors";
@import "variables/typography";
@import "mixins/layout";
@import (reference) "mixins/responsive";
@import "base/reset";
@import "components/button";
@import "components/form";
```

---

### 面试题速览（导入相关）

| 编号 | 问题 | 难度 |
|------|------|------|
| Q21 | `@import` 有哪些选项？`@import (reference)` 的作用是什么？ | 中级 |
| Q22 | LESS 如何实现模块化样式管理？ | 初级 |
| Q23 | 如何避免 `@import` 重复导入？ | 初级 |

---

## 八、高级语法特性

### 8.1 条件判断 Guard

Guard 类似于编程语言中的 `if` 条件判断，用于控制混合是否执行。

```less
// 比较运算符：> >= = =< <
// 当 Guard 条件为 true 时，混合才会执行

.mixin(@a) when (lightness(@a) >= 50%) {
  background: #000;  // 浅色背景用黑色文字
  color: #fff;
}
.mixin(@a) when (lightness(@a) < 50%) {
  background: #fff;  // 深色背景用白色文字
  color: #000;
}
.mixin(@a) {
  border: 1px solid @a;
}

// 调用
.box-light { .mixin(#eee); }
.box-dark { .mixin(#333); }
```

```less
// 逻辑运算符
// and（与）：所有条件都满足
.mixin(@width, @style) when (@width > 100px) and (@style = solid) {
  border: @width @style #000;
}

// ,（或）：满足任一条件即可
.mixin(@color) when (iscolor(@color)), (iskeyword(@color)) {
  color: @color;
}

// not（非）：条件不满足时执行
.mixin(@value) when not (isnumber(@value)) {
  content: @value;
}

// 类型检查函数
.mixin(@value) when (ispixel(@value)) { width: @value; }
.mixin(@value) when (ispercentage(@value)) { width: @value; }
.mixin(@value) when (isem(@value)) { width: @value; }
```

### 8.2 循环 Loops

LESS 本身没有 `for` 或 `while` 循环语法，但可以通过**递归混合 + Guard** 模拟循环。

```less
// 生成栅格系统（类似 Bootstrap）
.generate-columns(@n, @i: 1) when (@i =< @n) {
  .col-@{i} {
    width: (@i * 100% / @n);
  }
  .generate-columns(@n, (@i + 1));  // 递归调用
}

// 生成 12 列栅格
.generate-columns(12);

// 编译为：
// .col-1 { width: 8.33333333%; }
// .col-2 { width: 16.66666667%; }
// ... 
// .col-12 { width: 100%; }
```

```less
// 生成间距工具类
.generate-spacing(@prefix, @property, @n, @step: 4px, @i: 0) when (@i =< @n) {
  .@{prefix}-@{i} {
    @{property}: @i * @step;
  }
  .generate-spacing(@prefix, @property, @n, @step, (@i + 1));
}

// 生成 margin 和 padding 工具类
.generate-spacing(mt, margin-top, 10, 4px);
.generate-spacing(mb, margin-bottom, 10, 4px);
.generate-spacing(pt, padding-top, 10, 4px);
.generate-spacing(pb, padding-bottom, 10, 4px);
```

### 8.3 合并属性 Merge

用于合并多个属性值（如 `box-shadow`、`transform`、`background` 等逗号分隔的属性）。

```less
// 逗号合并（默认 +）
.mixin() {
  box-shadow+: inset 0 0 10px #555;
}
.my-class {
  .mixin();
  box-shadow+: 0 0 20px #000;
}

// 编译为：
// .my-class {
//   box-shadow: inset 0 0 10px #555, 0 0 20px #000;
// }

// 空格合并（+_）
.mixin-space() {
  transform+_: scale(1.2);
}
.another {
  .mixin-space();
  transform+_: rotate(45deg);
}

// 编译为：
// .another {
//   transform: scale(1.2) rotate(45deg);
// }
```

### 8.4 转义 Escaping

```less
// 使用 ~"..." 或 e("...") 转义字符串，保持原样输出
@min768: ~"(min-width: 768px)";

.element {
  @media @min768 {
    width: 50%;
  }
}

// 编译为：
// @media (min-width: 768px) {
//   .element { width: 50%; }
// }

// 转义 CSS 函数或特殊值
.box {
  filter: ~"progid:DXImageTransform.Microsoft.Alpha(opacity=50)";
  width: ~"calc(100% - 30px)";
}
```

### 8.5 命名空间与访问器

```less
// 命名空间：将混合组织在命名空间下，避免全局污染
#theme {
  .colors {
    @primary: #1890ff;
    @success: #52c41a;
    @warning: #faad14;
    @error: #f5222d;
  }

  .button() {
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
  }

  .primary-button() {
    .button();
    background: #theme.colors[@primary];
    color: #fff;
  }
}

// 使用命名空间
.btn {
  #theme > .primary-button();
}

// 访问命名空间中的变量
.title {
  color: #theme.colors[@primary];
}
```

### 8.6 Maps 与变量查找

```less
// LESS 3.5+ 支持类似 Map 的变量结构
#colors() {
  primary: #1890ff;
  success: #52c41a;
  danger: #f5222d;
}

.button {
  color: #colors[primary];
  background: #colors[success];
  border-color: #colors[danger];
}
```

### 8.7 Extend 继承

`&:extend()` 语法用于共享选择器间的公共样式，生成的 CSS 会使用选择器分组。

```less
// Extend 基础用法
.error {
  border: 1px solid #f00;
  background: #fdd;
}

.serious-error {
  &:extend(.error);
  font-weight: bold;
}

// 编译为：
// .error,
// .serious-error {
//   border: 1px solid #f00;
//   background: #fdd;
// }
// .serious-error { font-weight: bold; }

// Extend all：匹配所有包含该选择器的位置
.a { color: red; }
.b { .a {} }
.c {
  &:extend(.a all);  // 匹配所有 .a 出现的地方
}
```

**Extend vs Mixin 对比：**

| 特性 | Mixin | Extend |
|------|-------|--------|
| 输出方式 | 复制样式到每个调用处 | 合并选择器 |
| CSS 体积 | 可能重复 | 更紧凑 |
| 适用场景 | 需要参数化或动态逻辑 | 静态样式继承 |
| 媒体查询 | 可嵌套在 @media 内 | 需匹配同一 @media |

---

### 面试题速览（高级特性相关）

| 编号 | 问题 | 难度 |
|------|------|------|
| Q24 | LESS 中如何实现条件判断？ | 中级 |
| Q25 | LESS 没有循环语法，如何实现循环效果？ | 高级 |
| Q26 | `&:extend()` 和 Mixin 有什么区别？如何选择？ | 高级 |
| Q27 | 合并属性（Merge）有什么作用？ | 中级 |
| Q28 | 命名空间在 LESS 中如何使用？ | 中级 |

---

## 九、LESS 与 SCSS 对比

### 9.1 核心差异对比

| 对比维度 | LESS | SCSS |
|----------|------|------|
| 变量符号 | `@variable` | `$variable` |
| 声明符 | `:` | `:` |
| 变量作用域 | 延迟加载（Lazy Loading） | 即时加载（声明后可用） |
| 混合定义 | `.mixin() { }` | `@mixin name { }` |
| 混合调用 | `.mixin();` 或 `.mixin;` | `@include mixin;` |
| 继承语法 | `&:extend(.class);` | `@extend .class;` |
| 条件语句 | `when()` Guard | `@if @else` |
| 循环 | 递归混合 | `@for`、`@each`、`@while` |
| 内置函数 | 基础函数集 | 更丰富的函数库 |
| 返回语句 | 无 `@return` | `@return` |
| 文件扩展名 | `.less` | `.scss` / `.sass` |
| 编译方式 | Node.js / 浏览器端 | Ruby / Dart / Node.js |
| 使用门槛 | 较低 | 略高 |

### 9.2 语法对比示例

```less
// ===== LESS 写法 =====
@primary: #1890ff;

.button(@bg: @primary) {
  background: @bg;
  &:hover { background: lighten(@bg, 10%); }
}

.btn {
  .button(#52c41a);
}
```

```scss
// ===== SCSS 写法 =====
$primary: #1890ff;

@mixin button($bg: $primary) {
  background: $bg;
  &:hover { background: lighten($bg, 10%); }
}

.btn {
  @include button(#52c41a);
}
```

### 9.3 选择建议

| 场景 | 推荐 |
|------|------|
| 团队有 Ruby 背景 | SCSS |
| 使用 Bootstrap | SCSS |
| 使用 Ant Design | LESS |
| 需要浏览器端实时编译 | LESS |
| 需要复杂编程逻辑 | SCSS |
| 快速上手、学习成本低 | LESS |

---

### 面试题速览（对比相关）

| 编号 | 问题 | 难度 |
|------|------|------|
| Q29 | LESS 和 SCSS 有哪些主要区别？ | 初级 |
| Q30 | 什么场景下选择 LESS？什么场景下选择 SCSS？ | 中级 |

---

## 十、面试题集锦

### 初级题目

#### Q1：LESS 变量如何定义？有哪些使用场景？

**考察知识点：** 变量定义、插值 | **能力等级：** 初级

**参考答案：**

LESS 变量以 `@` 开头，语法为 `@变量名: 值;`。使用场景包括：

1. **统一定义设计规范**：颜色、字体、间距等全局样式常量
2. **主题切换**：通过修改变量值实现主题变换
3. **属性值复用**：避免重复书写相同的颜色/尺寸值
4. **选择器/属性名动态生成**：结合 `@{}` 插值语法
5. **URL 路径管理**：统一管理图片、字体等资源路径

```less
// 设计规范
@primary-color: #1890ff;
@font-size-base: 14px;
@border-radius: 4px;

// 主题切换
@theme: light;
@bg-color: #fff when (@theme = light);
@bg-color: #000 when (@theme = dark);
```

**评分标准：**
- 说出变量定义语法（30%）
- 列举至少 3 种使用场景（40%）
- 能写出插值用法（30%）

---

#### Q2：什么是 LESS 混合？如何定义和调用？

**考察知识点：** Mixin 基础 | **能力等级：** 初级

**参考答案：**

混合（Mixin）是将一组 CSS 属性封装为一个可复用的代码块。定义方式为类选择器形式，调用时使用 `.mixin-name();` 或 `.mixin-name;`。

```less
// 定义
.rounded-corners(@radius: 5px) {
  border-radius: @radius;
}

// 调用
.button { .rounded-corners(8px); }
.card { .rounded-corners(); }
```

核心价值：减少重复代码，提高可维护性，支持参数化定制。

**评分标准：**
- 正确定义语法（30%）
- 正确的调用方式（30%）
- 能说出混合的核心价值（40%）

---

#### Q3：LESS 嵌套规则如何工作？`&` 的作用是什么？

**考察知识点：** 嵌套规则 | **能力等级：** 初级

**参考答案：**

嵌套规则允许按 HTML 层级结构书写 CSS，减少重复选择器。编译后自动展开为后代选择器。

`&` 代表父选择器的引用，常用于：
- 伪类/伪元素：`&:hover`、`&::before`
- 状态修饰符：`&.active`、`&.disabled`
- BEM 命名：`&__element`、`&--modifier`
- 联合选择器：`& + .next`、`& ~ .sibling`

**评分标准：**
- 理解嵌套的编译规则（40%）
- 说出 `&` 的至少 2 种用法（40%）
- 能提到 BEM 命名法应用（20%）

---

#### Q4：`@import` 如何实现 LESS 模块化？

**考察知识点：** 导入与模块化 | **能力等级：** 初级

**参考答案：**

通过 `@import` 将样式拆分为多个文件，按职责组织：

```
styles/
├── variables.less    # 变量定义
├── mixins.less       # 混合定义
├── reset.less        # 基础重置
├── components/       # 组件样式
└── main.less         # 入口汇总
```

编译时所有文件合并为一个 CSS 文件，减少 HTTP 请求。`@import (reference)` 可导入但不输出，仅用于引用变量和混合。

**评分标准：**
- 能说出按职责拆分的方法（40%）
- 知道编译后合并为一个文件（30%）
- 了解 `(reference)` 选项（30%）

---

### 中级题目

#### Q5：什么是 LESS 的延迟加载（Lazy Loading）？与 SCSS 有什么区别？

**考察知识点：** 作用域机制 | **能力等级：** 中级

**参考答案：**

延迟加载是 LESS 的核心特性：**变量可以在声明之前使用**，LESS 采用"先整体扫描，后赋值"的机制，最终取值为当前作用域内的最后一次赋值。

```less
@color: blue;
.box {
  color: @color;  // 输出 red（作用域内最后一次赋值）
  @color: red;
}
```

**与 SCSS 的区别：**
- SCSS 是**即时加载**，变量必须先声明后使用，否则报错
- LESS 允许先使用后声明，更灵活但可能造成误解

**延迟加载的优势：**
- 可以在调用混合后再定义变量，适合主题系统
- 减少变量声明顺序的依赖

**评分标准：**
- 准确解释延迟加载机制（40%）
- 能写出演示代码（30%）
- 与 SCSS 对比清楚（30%）

---

#### Q6：`@arguments` 变量有什么作用？

**考察知识点：** 混合参数处理 | **能力等级：** 中级

**参考答案：**

`@arguments` 代表混合中传入的所有参数，用于一次性引用全部参数值。

```less
.transition(@property: all, @duration: .3s, @timing: ease) {
  transition: @arguments;
}

// 等效于 transition: @property @duration @timing;
```

**常见应用场景：**
- `transition`、`animation` 等多值简写属性
- `box-shadow`、`text-shadow` 等复杂属性
- 将参数透传给另一个混合

**评分标准：**
- 解释 `@arguments` 的含义（40%）
- 写出使用示例（30%）
- 列举适用场景（30%）

---

#### Q7：`lighten()` 和 `darken()` 的实现原理与使用场景？

**考察知识点：** 颜色函数 | **能力等级：** 中级

**参考答案：**

两个函数均基于 **HSL 色彩空间**操作：
- `lighten(@color, @amount)`：将亮度增加指定百分比
- `darken(@color, @amount)`：将亮度减少指定百分比

**实现原理：** 将颜色转为 HSL，调整 L（亮度）通道，再转回 RGB。

**典型应用：**

```less
@primary: #1890ff;

// 交互状态色值体系
.btn-primary {
  background: @primary;
  &:hover { background: lighten(@primary, 8%); }
  &:active { background: darken(@primary, 8%); }
  &:disabled { background: lighten(@primary, 25%); }
}
```

**注意事项：**
- 参数范围 0-100%，超出会被截断
- 对黑白灰（饱和度为 0）的颜色效果有限
- 建议配合 `saturate()`/`desaturate()` 使用以保持视觉一致性

**评分标准：**
- 解释基于 HSL（30%）
- 写出交互状态的应用（40%）
- 提到注意事项（30%）

---

#### Q8：LESS 中如何实现条件判断？

**考察知识点：** Guard 守卫 | **能力等级：** 中级

**参考答案：**

LESS 通过 **Guard（守卫）** 机制实现条件判断，语法为 `when (条件)`。

```less
// 基于颜色亮度判断
.text-color(@bg) when (lightness(@bg) >= 50%) {
  color: #333;  // 浅色背景用深色文字
}
.text-color(@bg) when (lightness(@bg) < 50%) {
  color: #fff;  // 深色背景用浅色文字
}

// 逻辑运算
.mixin(@a) when (@a > 10) and (@a < 100) { ... }
.mixin(@a) when (isnumber(@a)), (ispercentage(@a)) { ... }
.mixin(@a) when not (@a = 0) { ... }
```

**支持的运算符：** `>`、`>=`、`=`、`=<`、`<`、`and`、`,`（或）、`not`

**评分标准：**
- 写出 Guard 语法（40%）
- 展示逻辑运算符用法（30%）
- 有实际应用场景（30%）

---

#### Q9：`@import` 有哪些选项？`@import (reference)` 的作用是什么？

**考察知识点：** 导入选项 | **能力等级：** 中级

**参考答案：**

| 选项 | 作用 |
|------|------|
| `(reference)` | 仅导入变量和混合，不输出 CSS |
| `(once)` | 默认行为，相同文件只导入一次 |
| `(multiple)` | 允许重复导入同一文件 |
| `(less)` | 将 `.css` 文件视为 LESS 处理 |
| `(css)` | 将 `.less` 文件视为 CSS 处理 |
| `(inline)` | 内联导入，不处理直接输出 |
| `(optional)` | 文件不存在时不报错 |

`(reference)` 的核心价值：引入第三方库（如 Bootstrap）的变量和混合，而不产生冗余 CSS。

```less
@import (reference) "bootstrap/mixins";
.my-button {
  .btn();         // 使用 Bootstrap 的 .btn 混合
  .btn-primary(); // 使用 Bootstrap 的 .btn-primary 混合
}
```

**评分标准：**
- 列举至少 4 种选项（40%）
- 解释 `(reference)` 的核心价值（40%）
- 能写出实际应用（20%）

---

#### Q10：合并属性（Merge）有什么作用？如何区分逗号合并和空格合并？

**考察知识点：** Merge 语法 | **能力等级：** 中级

**参考答案：**

合并属性用于将多个值合并到同一个 CSS 属性中，避免后写的值覆盖前面的。

- **逗号合并（`+`）**：值之间用逗号分隔，适用于 `box-shadow`、`background`、`transition` 等
- **空格合并（`+_`）**：值之间用空格分隔，适用于 `transform` 等

```less
// 逗号合并
.shadow() {
  box-shadow+: 0 0 5px rgba(0,0,0,.1);
}
.card {
  .shadow();
  box-shadow+: 0 2px 8px rgba(0,0,0,.2);
}
// 输出：box-shadow: 0 0 5px rgba(0,0,0,.1), 0 2px 8px rgba(0,0,0,.2);

// 空格合并
.transform() {
  transform+_: scale(1.2);
}
.zoom {
  .transform();
  transform+_: rotate(15deg);
}
// 输出：transform: scale(1.2) rotate(15deg);
```

**评分标准：**
- 解释合并属性的作用（30%）
- 区分逗号合并和空格合并（40%）
- 写出正确示例（30%）

---

### 高级题目

#### Q11：什么是模式匹配（Pattern Matching）？举一个实际应用场景

**考察知识点：** 模式匹配 | **能力等级：** 高级

**参考答案：**

模式匹配是 LESS 中通过为同名混合设置不同的"匹配标识"（第一个参数）来实现多态行为。调用时根据第一个参数的值匹配对应的混合。

**实际应用：三角形生成器**

```less
.triangle(top, @w: 10px, @c: #333) {
  border-width: @w;
  border-color: transparent transparent @c transparent;
}
.triangle(bottom, @w: 10px, @c: #333) {
  border-width: @w;
  border-color: @c transparent transparent transparent;
}
.triangle(left, @w: 10px, @c: #333) {
  border-width: @w;
  border-color: transparent @c transparent transparent;
}
.triangle(right, @w: 10px, @c: #333) {
  border-width: @w;
  border-color: transparent transparent transparent @c;
}
// 公共样式——@_ 匹配所有情况
.triangle(@_, @w: 10px, @c: #333) {
  width: 0;
  height: 0;
  border-style: solid;
}

// 使用
.arrow-up { .triangle(top, 8px, #f00); }
.arrow-down { .triangle(bottom, 12px); }
```

**关键点：** `@_` 参数匹配所有模式，将公共代码提取到一处。

**评分标准：**
- 解释模式匹配的概念（30%）
- 写出完整示例（40%）
- 理解 `@_` 的作用（30%）

---

#### Q12：LESS 没有循环语法，如何实现循环效果？举两个实际例子

**考察知识点：** 递归混合 | **能力等级：** 高级

**参考答案：**

LESS 通过**递归混合 + Guard 条件**模拟循环。

**例子 1：栅格系统**

```less
.generate-grid(@n, @i: 1) when (@i =< @n) {
  .col-@{i} {
    width: (@i * 100% / @n);
  }
  .generate-grid(@n, (@i + 1));
}
.generate-grid(12);
```

**例子 2：间距工具类**

```less
.generate-spacing(@prefix, @prop, @n, @step: 4px, @i: 0) when (@i =< @n) {
  .@{prefix}-@{i} {
    @{prop}: @i * @step;
  }
  .generate-spacing(@prefix, @prop, @n, @step, (@i + 1));
}

.generate-spacing(mt, margin-top, 20);
.generate-spacing(pt, padding-top, 20);
```

**注意：** 递归层数过多可能导致编译变慢，建议使用合理的范围。

**评分标准：**
- 写出递归混合的基本结构（40%）
- 至少一个实际应用示例（40%）
- 提到性能注意事项（20%）

---

#### Q13：`&:extend()` 和 Mixin 有什么区别？如何选择？

**考察知识点：** Extend vs Mixin | **能力等级：** 高级

**参考答案：**

| 维度 | `&:extend()` | Mixin |
|------|-------------|-------|
| CSS 输出 | 选择器分组，样式不重复 | 样式复制到每个调用处 |
| 最终体积 | 更紧凑 | 可能冗余 |
| 参数化 | 不支持 | 支持 |
| 动态逻辑 | 不支持 | 支持 Guard 条件 |
| 媒体查询 | 需同层级匹配 | 可嵌套在 @media 内 |
| 适用场景 | 静态样式继承 | 参数化、动态化样式 |

**选择建议：**

```
使用 Extend 的场景：
  - 纯样式继承（如 .error 和 .serious-error）
  - 需要更紧凑的 CSS 输出
  - 样式不需要参数化

使用 Mixin 的场景：
  - 需要参数定制（如颜色、尺寸）
  - 需要条件判断（Guard）
  - 需要动态计算值
  - 需要在 @media 内使用
```

```less
// Extend 示例
.error-base {
  border: 1px solid red;
  color: red;
}
.validation-error {
  &:extend(.error-base);
  font-weight: bold;
}
// 输出：.error-base, .validation-error { border: 1px solid red; color: red; }

// Mixin 示例
.alert-style(@bg, @color) {
  background: @bg;
  color: @color;
  border: 1px solid darken(@bg, 10%);
}
.error-alert { .alert-style(#fdd, red); }
.success-alert { .alert-style(#dfd, green); }
```

**评分标准：**
- 准确对比两者的 CSS 输出差异（40%）
- 能给出选择建议（30%）
- 写出对比示例（30%）

---

#### Q14：延迟加载在实际项目中有什么应用场景？

**考察知识点：** 延迟加载实战 | **能力等级：** 高级

**参考答案：**

**场景 1：主题系统**

```less
// 先定义主题混合，后定义变量值
.theme {
  color: @text-color;
  background: @bg-color;
}

.theme-light {
  @text-color: #333;
  @bg-color: #fff;
  .theme();
}

.theme-dark {
  @text-color: #eee;
  @bg-color: #222;
  .theme();
}
```

**场景 2：工具类生成**

```less
// 基础样式中引用未定义的变量，在具体调用处定义
.generate-button(@name) {
  .btn-@{name} {
    background: @btn-bg;
    color: @btn-color;
    border: 1px solid @btn-border;
    &:hover { background: @btn-hover-bg; }
  }
}

// 使用处定义变量
@btn-bg: #1890ff;
@btn-color: #fff;
@btn-border: darken(@btn-bg, 5%);
@btn-hover-bg: lighten(@btn-bg, 10%);
.generate-button(primary);
```

**场景 3：响应式断点配置**

```less
// 先定义响应式混合，再在不同断点配置中定义变量
.responsive-padding() {
  padding: @padding-mobile;
  @media (min-width: 768px) { padding: @padding-tablet; }
  @media (min-width: 1024px) { padding: @padding-desktop; }
}

@padding-mobile: 12px;
@padding-tablet: 16px;
@padding-desktop: 24px;
.container { .responsive-padding(); }
```

**注意事项：** 延迟加载虽然灵活，但过度使用可能导致代码可读性下降，建议在团队规范中明确使用方式。

**评分标准：**
- 至少 2 个实际应用场景（50%）
- 代码示例完整正确（30%）
- 提到注意事项（20%）

---

#### Q15：如何设计一个基于 LESS 的可扩展主题系统？

**考察知识点：** 综合架构设计 | **能力等级：** 高级

**参考答案：**

```less
// ===== 1. 设计令牌（Design Tokens） =====
// 基础色板
@blue-6: #1890ff;
@blue-5: #40a9ff;
@blue-7: #096dd9;

// 语义化令牌
@primary-color: @blue-6;
@primary-hover: @blue-5;
@primary-active: @blue-7;

@text-color: #333;
@text-color-secondary: #666;
@bg-color: #fff;
@border-color: #d9d9d9;
@border-radius: 4px;

// ===== 2. 组件混合 =====
.button-base() {
  display: inline-block;
  padding: 8px 16px;
  border-radius: @border-radius;
  cursor: pointer;
  transition: all .3s;
  border: 1px solid transparent;
}

.button-variant(@bg, @color, @border) {
  background: @bg;
  color: @color;
  border-color: @border;
  &:hover { background: lighten(@bg, 8%); }
  &:active { background: darken(@bg, 8%); }
}

// ===== 3. 组件样式 =====
.btn {
  .button-base();
  &-primary { .button-variant(@primary-color, #fff, @primary-color); }
  &-default {
    .button-variant(#fff, @text-color, @border-color);
    &:hover { color: @primary-color; border-color: @primary-color; }
  }
}

// ===== 4. 主题切换 =====
// 通过覆盖变量实现主题切换
.theme-dark {
  @primary-color: #177ddc;
  @text-color: #e0e0e0;
  @bg-color: #141414;
  @border-color: #434343;
}
```

**设计原则：**
1. **分层设计**：令牌层 → 混合层 → 组件层
2. **语义化命名**：用语义化变量替代直接颜色值
3. **单一职责**：每个文件只负责一类样式
4. **可覆盖性**：核心变量集中管理，方便主题切换

**评分标准：**
- 分层架构清晰（30%）
- 令牌设计合理（30%）
- 可扩展性论述充分（40%）

---

## 附录：考点速查表

| 知识点 | 核心内容 | 难度范围 | 出现频率 |
|--------|---------|----------|---------|
| 变量 | 定义、插值、延迟加载、`$property` | 初级-中级 | 高 |
| 混合 Mixins | 基础混合、参数、`@arguments`、`@rest`、模式匹配 | 初级-高级 | 高 |
| 嵌套 | 基础嵌套、`&`、`@media` 冒泡 | 初级-中级 | 高 |
| 运算 | 数值运算、颜色运算、`calc()` 共存 | 初级-中级 | 中 |
| 函数 | 颜色函数、数学函数、类型判断 | 初级-中级 | 中 |
| 作用域 | 词法作用域、延迟加载 | 中级 | 高 |
| 导入 | `@import` 选项、模块化 | 初级-中级 | 中 |
| Guard | `when()` 条件、逻辑运算 | 中级 | 中 |
| 循环 | 递归混合 | 高级 | 中 |
| Extend | `&:extend()` 语法、与 Mixin 对比 | 高级 | 中 |
| Merge | 逗号合并、空格合并 | 中级 | 低 |
| 命名空间 | `#namespace > .mixin` | 中级 | 低 |
| 对比 | LESS vs SCSS 差异 | 初级-中级 | 高 |

---

> **参考资源：** [LESS 官方文档](https://lesscss.org/) | 本文档适用于面试准备与日常开发参考。