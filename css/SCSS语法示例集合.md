# SCSS 语法示例集合

> 系统整理 SCSS 核心知识点，涵盖常用基础语法及高级特性的实际应用，结合常见面试题进行深入解析。

---

## 目录

- [一、变量定义与使用](#一变量定义与使用)
- [二、嵌套规则](#二嵌套规则)
- [三、混合宏 Mixins](#三混合宏-mixins)
- [四、继承 @extend](#四继承-extend)
- [五、函数 Functions](#五函数-functions)
- [六、条件语句](#六条件语句)
- [七、循环控制](#七循环控制)
- [八、插值语法](#八插值语法)
- [九、模块化系统](#九模块化系统)
- [十、内置函数大全](#十内置函数大全)
- [十一、实战综合案例](#十一实战综合案例)
- [十二、面试题集锦](#十二面试题集锦)

---

## 一、变量定义与使用

### 1.1 基础变量

```scss
// ===== 变量定义 =====
// SCSS 变量以 $ 开头，支持任何 CSS 属性值类型

// 颜色变量
$primary-color: #3498db;
$secondary-color: #2ecc71;
$danger-color: #e74c3c;

// 尺寸变量
$font-size-base: 16px;
$spacing-unit: 8px;
$border-radius: 4px;

// 字符串变量
$font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
$font-family-mono: 'SF Mono', 'Fira Code', monospace;

// 布尔变量
$enable-rounded: true;
$enable-shadows: false;

// 空值变量
$config: null;

// ===== 变量使用 =====
.button {
  background-color: $primary-color;      // 颜色引用
  font-size: $font-size-base;            // 尺寸引用
  padding: $spacing-unit * 2;            // 参与运算
  border-radius: $border-radius;
  font-family: $font-family-sans;        // 字符串引用
}
```

### 1.2 变量作用域

```scss
// 全局作用域
$global-color: red;   // 定义在顶层的变量为全局变量

.content {
  // 局部作用域：在 {} 内部定义，仅在此块内有效
  $local-color: blue;
  color: $local-color;    // ✅ 可用：blue
  background: $global-color;  // ✅ 可用：red
}

.sidebar {
  color: $local-color;    // ❌ 报错！$local-color 在此作用域不存在
  background: $global-color;  // ✅ 可用：red
}

// 在局部作用域中覆盖全局变量
$theme: 'light';

.header {
  $theme: 'dark' !global;  // !global 标志将局部变量提升为全局
  // 此时 $theme 已变为 'dark'
}

.footer {
  color: $theme;  // 输出 'dark'（因为被 !global 覆盖了）
}
```

### 1.3 默认值 `!default`

```scss
// !default 表示"如果变量未被赋值，则使用此默认值"
// 常用于第三方库，允许用户在使用前覆盖变量

// _config.scss（库文件）
$primary-color: #3498db !default;
$font-size: 16px !default;

// 用户自定义（在导入库文件之前定义）
$primary-color: #ff6b35;  // 覆盖了默认值

// @import 'config';  // 由于 $primary-color 已定义，!default 不会生效
// 最终 $primary-color 为 #ff6b35，$font-size 为 16px
```

### 1.4 数据类型

```scss
// SCSS 支持 7 种数据类型
$number: 1.5;                    // 数字（含单位：16px, 2rem, 50%）
$string: 'Hello';                // 字符串（有引号或无引号）
$color: #ff0000;                 // 颜色（十六进制、rgb、hsl、命名颜色）
$bool: true;                     // 布尔值
$null: null;                     // 空值
$list: 1px solid red;            // 列表（空格或逗号分隔）
$map: (key1: value1, key2: 2);   // 映射（键值对）
```

---

## 二、嵌套规则

### 2.1 选择器嵌套

```scss
// 原生 CSS 写法
// .nav { ... }
// .nav ul { ... }
// .nav ul li { ... }
// .nav ul li a { ... }

// ===== SCSS 嵌套写法 =====
.nav {
  background: #333;

  ul {
    margin: 0;
    padding: 0;
    list-style: none;

    li {
      display: inline-block;

      a {
        color: #fff;
        text-decoration: none;
        padding: 10px 15px;
        display: block;
      }
    }
  }
}
```

### 2.2 父选择器 `&`

```scss
// & 代表当前选择器的父级，是 SCSS 嵌套中最常用的特性之一

.button {
  background: $primary-color;
  color: #fff;
  padding: 10px 20px;
  border: none;
  cursor: pointer;

  // ===== 伪类选择器 =====
  &:hover {
    background: darken($primary-color, 10%);
  }
  &:focus {
    outline: 2px solid lighten($primary-color, 20%);
  }
  &:active {
    transform: scale(0.98);
  }

  // ===== 组合选择器（BEM 命名法） =====
  &--large {
    padding: 15px 30px;
    font-size: 18px;
  }
  &--small {
    padding: 5px 10px;
    font-size: 12px;
  }
  &--disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  // ===== 与兄弟/子元素组合 =====
  &.active {
    // .button.active
    background: $secondary-color;
  }

  // 在 & 后面继续拼接（注意：& 必须放在开头）
  // 正确：&__element
  // 错误：element&（会被解析为 element.button）
  &__icon {
    margin-right: 5px;
  }
}

// 编译结果：
// .button { ... }
// .button:hover { ... }
// .button--large { ... }
// .button.active { ... }
// .button__icon { ... }
```

### 2.3 属性嵌套

```scss
// 对具有相同前缀的属性进行嵌套（如 font-, margin-, padding- 等）

.box {
  // ===== font 属性嵌套 =====
  font: {
    family: $font-family-sans;
    size: 16px;
    weight: 700;
    style: italic;
  }

  // ===== margin 属性嵌套 =====
  margin: {
    top: 20px;
    right: 15px;
    bottom: 20px;
    left: 15px;
  }

  // ===== border 属性嵌套 =====
  border: {
    width: 1px;
    style: solid;
    color: #ddd;
    radius: 4px;
  }
}

// 编译结果：
// .box {
//   font-family: ...;
//   font-size: 16px;
//   font-weight: 700;
//   font-style: italic;
//   margin-top: 20px;
//   ...
//   border-width: 1px;
//   ...
// }
```

### 2.4 跳出嵌套 `@at-root`

```scss
// @at-root 使样式跳出当前嵌套层级，直接放在根选择器下

.parent {
  color: #333;
  font-size: 16px;

  // 跳出嵌套，直接编译为 .child
  @at-root .child {
    color: #666;
  }

  // 跳出嵌套但保留父选择器上下文
  @at-root {
    .sibling-1 {
      color: red;
    }
    .sibling-2 {
      color: blue;
    }
  }
}

// 编译结果：
// .parent { color: #333; font-size: 16px; }
// .child { color: #666; }
// .sibling-1 { color: red; }
// .sibling-2 { color: blue; }

// 实战场景：在 BEM 嵌套中创建独立类
.modal {
  &__content {
    padding: 20px;

    @at-root .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.5);
    }
  }
}
```

---

## 三、混合宏 Mixins

### 3.1 基础 Mixin

```scss
// Mixin 是可复用的样式块，通过 @mixin 定义，@include 调用

// ===== 无参数 Mixin =====
@mixin flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

@mixin clearfix {
  &::after {
    content: '';
    display: table;
    clear: both;
  }
}

// 使用
.container {
  @include flex-center;
  @include clearfix;
}
```

### 3.2 带参数 Mixin

```scss
// ===== 必选参数 =====
@mixin box-shadow($x, $y, $blur, $color) {
  box-shadow: $x $y $blur $color;
}

.card {
  @include box-shadow(0, 2px, 10px, rgba(0, 0, 0, 0.1));
}

// ===== 默认参数 =====
@mixin border-radius($radius: 4px) {
  border-radius: $radius;
}

.btn {
  @include border-radius;       // 使用默认值 4px
}
.avatar {
  @include border-radius(50%);  // 覆盖为 50%
}

// ===== 命名参数 =====
@mixin position($top, $right, $bottom, $left) {
  top: $top;
  right: $right;
  bottom: $bottom;
  left: $left;
}

.element {
  @include position($top: 10px, $right: 20px, $bottom: auto, $left: 30px);
  // 命名参数可任意顺序传入，提高可读性
}
```

### 3.3 可变参数

```scss
// 使用 ... 接收任意数量的参数

@mixin transition($properties...) {
  transition: $properties;
}

.box {
  @include transition(color 0.3s, background 0.5s, transform 0.2s);
}

// 向嵌套 Mixin 传递可变参数
@mixin button-variant($bg, $color) {
  background: $bg;
  color: $color;
}

@mixin button($bg, $color) {
  display: inline-block;
  padding: 10px 20px;
  border: none;
  @include button-variant($bg, $color);  // 手动传递
}

// 使用 meta.keywords() 配合可变参数实现配置对象模式
@use 'sass:meta';

@mixin theme($args...) {
  // 将可变参数转为 map
  $config: meta.keywords($args);

  @if map-get($config, 'dark') {
    background: #333;
    color: #fff;
  } @else {
    background: #fff;
    color: #333;
  }
}

.page {
  @include theme($dark: true);  // 命名参数会打包为 map
}
```

### 3.4 `@content` 内容块

```scss
// @content 允许向 Mixin 中注入自定义样式块，是 SCSS 最强大的特性之一

// ===== 响应式断点 Mixin =====
$breakpoints: (
  'sm': 576px,
  'md': 768px,
  'lg': 992px,
  'xl': 1200px
);

@mixin respond-to($breakpoint) {
  $value: map-get($breakpoints, $breakpoint);

  @if $value {
    @media (min-width: $value) {
      @content;  // 将调用处的代码块注入此处
    }
  } @else {
    @error "未知断点: #{$breakpoint}";
  }
}

// 使用
.container {
  width: 100%;

  @include respond-to('md') {
    width: 750px;   // 这个代码块会被注入到 @media 内部
  }

  @include respond-to('lg') {
    width: 970px;
  }
}

// 编译结果：
// .container { width: 100%; }
// @media (min-width: 768px) { .container { width: 750px; } }
// @media (min-width: 992px) { .container { width: 970px; } }
```

### 3.5 高级 Mixin 实战

```scss
// ===== 按钮生成器 =====
@mixin button-generator($colors) {
  // 遍历颜色 map 生成多套按钮样式
  @each $name, $color in $colors {
    .btn--#{$name} {
      background: $color;
      color: #fff;
      border: 1px solid darken($color, 10%);

      &:hover {
        background: darken($color, 10%);
      }
      &:active {
        background: darken($color, 15%);
      }
      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
    }
  }
}

// 定义颜色映射
$button-colors: (
  'primary': #3498db,
  'success': #2ecc71,
  'warning': #f39c12,
  'danger': #e74c3c,
  'info': #9b59b6
);

// 一键生成所有按钮样式
@include button-generator($button-colors);


// ===== 三角形生成器 =====
@mixin triangle($direction, $size, $color) {
  width: 0;
  height: 0;
  border: $size solid transparent;

  @if $direction == 'up' {
    border-bottom-color: $color;
    border-top-width: 0;
  } @else if $direction == 'down' {
    border-top-color: $color;
    border-bottom-width: 0;
  } @else if $direction == 'left' {
    border-right-color: $color;
    border-left-width: 0;
  } @else if $direction == 'right' {
    border-left-color: $color;
    border-right-width: 0;
  }
}

.arrow-up {
  @include triangle('up', 10px, #333);
}
```

---

## 四、继承 @extend

### 4.1 基础继承

```scss
// @extend 使一个选择器继承另一个选择器的所有样式
// 编译后会将多个选择器合并为一组，减少生成的 CSS 大小

// 定义基础样式
.base-button {
  display: inline-block;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-align: center;
  font-size: 16px;
  transition: all 0.3s;
}

.primary-button {
  @extend .base-button;  // 继承 .base-button 的所有样式
  background: #3498db;
  color: #fff;
}

.secondary-button {
  @extend .base-button;  // 同样继承
  background: #95a5a6;
  color: #fff;
}

// 编译结果：
// .base-button, .primary-button, .secondary-button {
//   display: inline-block;
//   padding: 10px 20px;
//   ...
// }
// .primary-button { background: #3498db; color: #fff; }
// .secondary-button { background: #95a5a6; color: #fff; }
```

### 4.2 占位符选择器 `%`

```scss
// % 占位符是"仅用于继承"的选择器，自身不会被编译到 CSS 中
// 推荐使用占位符而不是具体类名来做继承基类

// ===== 占位符定义（不会被编译，除非被继承） =====
%clearfix {
  &::after {
    content: '';
    display: table;
    clear: both;
  }
}

%visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

%ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

// 继承占位符
.container {
  @extend %clearfix;
}

.sr-only {
  @extend %visually-hidden;
}

.title {
  @extend %ellipsis;
  max-width: 200px;
}

// 编译结果：%clearfix 不会单独出现，只会在被继承的地方生效
// .container::after { content: ''; display: table; clear: both; }
// .sr-only { position: absolute; width: 1px; ... }
```

### 4.3 @extend 与 @mixin 对比

```scss
// +---------------------------+----------------------------------+
// | @extend 占位符             | @mixin                           |
// +---------------------------+----------------------------------+
// | 编译后生成选择器分组       | 编译后复制代码到每个调用处        |
// | 生成的 CSS 体积更小        | 生成的 CSS 体积可能更大           |
// | 不能传递参数               | 可以传递参数，更灵活              |
// | 适合静态的关系型样式复用   | 适合需要动态值的样式复用          |
// | 选择器之间不能有后代关系   | 无限制                           |
// +---------------------------+----------------------------------+

// @extend 适用场景：静态、无参数的样式复用
%card-base {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background: #fff;
}

// @mixin 适用场景：需要参数、动态值的样式复用
@mixin card($bg: #fff, $shadow: true) {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background: $bg;

  @if $shadow {
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }
}
```

### 4.4 @extend 链式继承与注意点

```scss
// 链式继承
%base {
  color: #333;
  font-size: 16px;
}

%extended {
  @extend %base;
  font-weight: bold;
}

.special {
  @extend %extended;
  text-decoration: underline;
}

// 注意：@extend 不能在选择器有后代关系的上下文中使用
// ❌ 错误示例
.nav {
  .item {
    @extend %base;  // 可以，但继承关系会变复杂
  }
}

// ✅ 推荐：在顶层使用 @extend
.nav-item {
  @extend %base;
}
```

---

## 五、函数 Functions

### 5.1 自定义函数

```scss
// 使用 @function 定义，@return 返回值
// 函数用于计算和返回值，与 Mixin 不同（Mixin 用于输出样式）

// ===== px 转 rem 函数 =====
@function rem($px, $base: 16px) {
  @if unitless($px) {
    $px: $px * 1px;
  }
  @return ($px / $base) * 1rem;
}

// 使用
body {
  font-size: rem(16);       // 1rem
}
h1 {
  font-size: rem(24);       // 1.5rem
  margin-bottom: rem(8);    // 0.5rem
}

// ===== 间距计算函数 =====
$spacing-base: 8px;

@function spacing($multiplier: 1) {
  @return $multiplier * $spacing-base;
}

.section {
  margin: spacing(2);       // 16px
  padding: spacing(3);      // 24px
}

// ===== 颜色变亮/变暗函数 =====
@function tint($color, $percentage) {
  @return mix(#fff, $color, $percentage);
}

@function shade($color, $percentage) {
  @return mix(#000, $color, $percentage);
}

.element {
  background: tint(#3498db, 80%);  // 混合 80% 白色
  border: 1px solid shade(#3498db, 20%);  // 混合 20% 黑色
}

// ===== 对比度函数（自动选择黑/白文字色） =====
@function contrast-color($bg, $dark: #333, $light: #fff) {
  @return if(lightness($bg) > 50%, $dark, $light);
}

.button {
  $bg: #3498db;
  background: $bg;
  color: contrast-color($bg);  // 自动返回白色文字
}
```

### 5.2 函数中的条件与循环

```scss
// ===== 获取 Map 的深度嵌套值 =====
@function map-deep-get($map, $keys...) {
  $value: $map;

  @each $key in $keys {
    $value: map-get($value, $key);
  }

  @return $value;
}

$theme: (
  'colors': (
    'primary': (
      'base': #3498db,
      'light': #5dade2,
      'dark': #2980b9
    ),
    'secondary': (
      'base': #2ecc71,
      'light': #58d68d,
      'dark': #27ae60
    )
  )
);

.button {
  background: map-deep-get($theme, 'colors', 'primary', 'base');
  // 等同于 map-get(map-get(map-get($theme, 'colors'), 'primary'), 'base')
}


// ===== 字符串替换函数 =====
@function str-replace($string, $search, $replace: '') {
  $index: str-index($string, $search);

  @if $index {
    @return str-slice($string, 1, $index - 1) + $replace +
            str-replace(str-slice($string, $index + str-length($search)), $search, $replace);
  }

  @return $string;
}

// 使用：将 url 中的空格替换为 %20
$path: str-replace('path/to/my file.jpg', ' ', '%20');
```

### 5.3 函数递归

```scss
// ===== 计算阶乘 =====
@function factorial($n) {
  @if $n <= 1 {
    @return 1;
  }
  @return $n * factorial($n - 1);
}

// factorial(5) => 120


// ===== 展平嵌套列表 =====
@function flatten($list) {
  $result: ();

  @each $item in $list {
    @if type-of($item) == 'list' and length($item) > 0 {
      $result: join($result, flatten($item), comma);
    } @else {
      $result: append($result, $item, comma);
    }
  }

  @return $result;
}
```

---

## 六、条件语句

### 6.1 `@if` / `@else if` / `@else`

```scss
// ===== 基础条件判断 =====
@mixin theme($type) {
  @if $type == 'light' {
    background: #fff;
    color: #333;
  } @else if $type == 'dark' {
    background: #333;
    color: #fff;
  } @else if $type == 'blue' {
    background: #3498db;
    color: #fff;
  } @else {
    background: #f5f5f5;
    color: #666;
  }
}

.page {
  @include theme('dark');
}


// ===== 真值判断规则 =====
// SCSS 中以下值被视为 false：
//   - false（布尔值）
//   - null（空值）
// 其他所有值（包括 0、空字符串、空列表）都视为 true

@mixin show-if($condition) {
  @if $condition {
    display: block;
  } @else {
    display: none;
  }
}

.element {
  @include show-if(true);   // display: block;
  // @include show-if(0);      // display: block;（0 不是 false！）
  // @include show-if(null);   // display: none;
}
```

### 6.2 综合条件判断实战

```scss
// ===== 响应式图片 Mixin =====
@mixin responsive-image($device) {
  @if $device == 'mobile' {
    width: 100%;
    height: auto;
  } @else if $device == 'tablet' {
    width: 75%;
    height: auto;
  } @else if $device == 'desktop' {
    max-width: 1200px;
    height: auto;
  } @else {
    @error "未知设备类型: #{$device}。可选值: mobile, tablet, desktop";
  }
}


// ===== 根据数值大小决定样式 =====
@mixin size-variant($size) {
  @if $size < 12 {
    font-size: 12px;
    padding: 4px 8px;
  } @else if $size >= 12 and $size < 16 {
    font-size: 14px;
    padding: 6px 12px;
  } @else if $size >= 16 {
    font-size: 16px;
    padding: 10px 20px;
  }
}

// 使用比较运算符：> < >= <= == !=
.btn-sm {
  @include size-variant(10);
}
.btn-lg {
  @include size-variant(18);
}
```

### 6.3 `@supports` 与条件判断结合

```scss
// 检测浏览器是否支持某 CSS 特性
@mixin grid-layout($columns) {
  display: grid;

  @supports (display: grid) {
    grid-template-columns: repeat($columns, 1fr);
  }

  // 不支持 grid 时的降级方案
  @supports not (display: grid) {
    display: flex;
    flex-wrap: wrap;

    > * {
      flex: 0 0 calc(100% / #{$columns});
    }
  }
}
```

---

## 七、循环控制

### 7.1 `@for` 循环

```scss
// ===== @for $i from <start> through <end>  =====
// through：包含 end 值

@for $i from 1 through 5 {
  .col-#{$i} {
    width: percentage($i / 5);  // 20%, 40%, 60%, 80%, 100%
  }
}

// 编译结果：
// .col-1 { width: 20%; }
// .col-2 { width: 40%; }
// ...
// .col-5 { width: 100%; }


// ===== @for $i from <start> to <end> =====
// to：不包含 end 值

@for $i from 1 to 5 {
  .col-#{$i} {
    width: 20% * $i;
  }
}
// 编译结果：.col-1 ~ .col-4（不含 .col-5）


// ===== 实战：生成栅格系统 =====
@for $i from 1 through 12 {
  .col-#{$i} {
    flex: 0 0 percentage($i / 12);
    max-width: percentage($i / 12);
  }
}

// ===== 实战：生成 z-index 层级 =====
$z-layers: (
  'dropdown': 100,
  'sticky': 200,
  'modal': 300,
  'tooltip': 400
);

@for $i from 1 through 10 {
  .z-index-#{$i} {
    z-index: 100 * $i;
  }
}
```

### 7.2 `@each` 循环

```scss
// ===== 遍历简单列表 =====
$colors: red, green, blue, yellow;

@each $color in $colors {
  .bg-#{$color} {
    background-color: $color;
  }
  .text-#{$color} {
    color: $color;
  }
}

// 编译结果：
// .bg-red { background-color: red; }
// .text-red { color: red; }
// .bg-green { background-color: green; }
// ...


// ===== 遍历 Map（键值对） =====
$theme-colors: (
  'primary': #3498db,
  'success': #2ecc71,
  'warning': #f39c12,
  'danger': #e74c3c
);

@each $name, $color in $theme-colors {
  .btn-#{$name} {
    background: $color;
    border-color: darken($color, 10%);

    &:hover {
      background: darken($color, 15%);
    }
  }

  .text-#{$name} {
    color: $color;
  }
}


// ===== 遍历多维 Map =====
$spacers: (
  0: 0,
  1: 4px,
  2: 8px,
  3: 16px,
  4: 24px,
  5: 48px
);

// 生成 .m-0 ~ .m-5 和 .p-0 ~ .p-5
@each $name, $value in $spacers {
  .m-#{$name} {
    margin: $value;
  }
  .p-#{$name} {
    padding: $value;
  }
  .mt-#{$name} {
    margin-top: $value;
  }
  .mb-#{$name} {
    margin-bottom: $value;
  }
  .ml-#{$name} {
    margin-left: $value;
  }
  .mr-#{$name} {
    margin-right: $value;
  }
}


// ===== 解构多个值 =====
$breakpoint-list: (
  'sm' 576px,
  'md' 768px,
  'lg' 992px,
  'xl' 1200px
);

@each $name, $width in $breakpoint-list {
  .container-#{$name} {
    max-width: $width;
  }
}
```

### 7.3 `@while` 循环

```scss
// @while 循环在条件为 true 时持续执行

// ===== 基础示例 =====
$i: 1;
@while $i <= 5 {
  .item-#{$i} {
    width: 100px * $i;
  }
  $i: $i + 1;  // 必须手动递增，否则会死循环
}

// ===== 实战：生成圆角大小 =====
$radius: 4px;
$max-radius: 24px;

@while $radius <= $max-radius {
  .radius-#{$radius} {
    border-radius: $radius;
  }
  $radius: $radius + 4;
}
// 输出：.radius-4px, .radius-8px, .radius-12px, ..., .radius-24px

// ===== 实战：生成字体大小等比数列 =====
$font-size: 10px;
$scale: 1.2;
$i: 0;

@while $i < 6 {
  .fs-#{$i} {
    font-size: $font-size;
  }
  $font-size: $font-size * $scale;
  $i: $i + 1;
}
```

---

## 八、插值语法

### 8.1 `#{}` 插值

```scss
// #{} 用于在字符串中插入变量值，也可用于选择器和属性名

// ===== 在选择器中使用 =====
$component: 'card';

.#{$component} {
  background: #fff;

  &__#{$component}-header {
    font-size: 20px;
    // 编译为 .card__card-header
  }
}

// ===== 在属性名中使用 =====
$direction: 'top';

.element {
  margin-#{$direction}: 20px;  // margin-top: 20px;
  padding-#{$direction}: 10px;  // padding-top: 10px;
}

// ===== 在字符串中使用 =====
$version: '1.0.0';

// 伪元素 content 属性
.info::after {
  content: '版本: #{$version}';  // content: "版本: 1.0.0";
}

// ===== 在注释中使用 =====
$author: 'Zhang San';
// 作者: #{$author}

// ===== 在 @media 中使用 =====
$breakpoint: 768px;

@media (min-width: #{$breakpoint}) {
  .container {
    max-width: 750px;
  }
}
```

### 8.2 插值与循环结合

```scss
// 插值 + 循环是最常见的组合模式

// 生成图标类
$icons: 'home', 'user', 'settings', 'search', 'mail';

@each $icon in $icons {
  .icon-#{$icon} {
    background-image: url('../images/icons/#{$icon}.svg');
    width: 24px;
    height: 24px;
    display: inline-block;
  }
}

// 生成动画延迟
@for $i from 1 through 5 {
  .delay-#{$i} {
    animation-delay: #{$i * 0.1}s;
  }
}

// 响应式列生成
$breakpoints: (
  'sm': 576px,
  'md': 768px,
  'lg': 992px
);

@each $bp, $width in $breakpoints {
  @media (min-width: #{$width}) {
    @for $i from 1 through 12 {
      .col-#{$bp}-#{$i} {
        width: percentage($i / 12);
      }
    }
  }
}
```

---

## 九、模块化系统

### 9.1 `@import`（传统方式）

```scss
// 文件命名：以下划线开头为 partial 文件，不会被独立编译
// _variables.scss
// _mixins.scss
// _reset.scss

// ===== main.scss =====
// 导入时不需要写下划线 _ 和 .scss 扩展名
@import 'variables';   // 导入 _variables.scss
@import 'mixins';      // 导入 _mixins.scss
@import 'reset';       // 导入 _reset.scss

// 注意：@import 的缺点
// 1. 所有变量、Mixin、函数是全局的，无法知道来源
// 2. 多次导入同一文件会导致重复编译
// 3. 没有命名空间，容易冲突
// Sass 官方推荐使用 @use 和 @forward 替代 @import
```

### 9.2 `@use`（现代模块系统）

```scss
// @use 是 Sass 新推荐的模块加载方式，拥有命名空间

// ===== _variables.scss =====
$primary: #3498db;
$secondary: #2ecc71;
$font-size: 16px;

// ===== _mixins.scss =====
@mixin flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

// ===== main.scss =====

// 默认命名空间为文件名（不含前导下划线）
@use 'variables';
@use 'mixins';

.element {
  color: variables.$primary;  // 使用命名空间访问
  @include mixins.flex-center;
}

// 自定义命名空间
@use 'variables' as var;
@use 'mixins' as mix;

.element {
  color: var.$primary;
  @include mix.flex-center;
}

// 使用 * 去掉命名空间（谨慎使用）
@use 'variables' as *;

.element {
  color: $primary;  // 可以直接使用变量
}
```

### 9.3 `@forward`（模块转发）

```scss
// @forward 用于创建一个"索引文件"，将多个模块组织在一起并统一导出

// ===== 文件结构 =====
// abstracts/
//   _variables.scss
//   _mixins.scss
//   _functions.scss
//   _index.scss        ← 索引文件，统一转发

// ===== abstracts/_index.scss =====
@forward 'variables';
@forward 'mixins';
@forward 'functions';

// 可以添加前缀避免冲突
// @forward 'variables' as var-*;

// 可以有选择地暴露
// @forward 'variables' show $primary, $secondary;
// @forward 'mixins' hide flex-center;


// ===== main.scss =====
// 只需导入索引文件即可
@use 'abstracts' as *;

.element {
  color: $primary;
  @include flex-center;
}
```

### 9.4 模块配置 `!default` + `@use with`

```scss
// 库可以定义可配置的默认值，用户通过 with 覆盖

// ===== library/_config.scss =====
$primary: #3498db !default;
$font-size: 16px !default;
$border-radius: 4px !default;

// ===== user.scss =====
@use 'library/config' with (
  $primary: #ff6b35,
  $font-size: 14px
  // $border-radius 保持默认值 4px
);

.element {
  color: config.$primary;      // #ff6b35
  font-size: config.$font-size;  // 14px
}
```

---

## 十、内置函数大全

### 10.1 颜色函数

```scss
$color: #3498db;

// 调整亮度
.darken  { color: darken($color, 10%);  }   // 减少亮度 10%
.lighten { color: lighten($color, 10%); }    // 增加亮度 10%

// 调整饱和度
.saturate   { color: saturate($color, 20%);   }   // 增加饱和度
.desaturate { color: desaturate($color, 20%); }   // 减少饱和度

// 调整透明度
.opacify        { color: opacify(rgba($color, 0.8), 0.1); }        // 增加不透明度
.transparentize { color: transparentize($color, 0.3); }            // 减少不透明度
.fade-in        { color: fade-in(rgba($color, 0.5), 0.3); }        // 同 opacify
.fade-out       { color: fade-out($color, 0.2); }                   // 同 transparentize

// 颜色混合
.mix { color: mix(#3498db, #e74c3c, 50%); }  // 混合两种颜色，权重 50%

// 颜色调整
.adjust-hue { color: adjust-hue($color, 45deg);  }  // 调整色调
.complement { color: complement($color); }             // 补色
.invert     { color: invert($color); }                 // 反色
.grayscale  { color: grayscale($color); }              // 灰度化

// 获取颜色通道
$hue: hue($color);            // 色调
$sat: saturation($color);     // 饱和度
$light: lightness($color);    // 亮度
$red: red($color);            // 红色通道
$green: green($color);        // 绿色通道
$blue: blue($color);          // 蓝色通道
$alpha: alpha($color);        // 透明度
```

### 10.2 数值函数

```scss
// 数学运算
$result: abs(-10);          // 10（绝对值）
$result: ceil(4.2);         // 5（向上取整）
$result: floor(4.8);        // 4（向下取整）
$result: round(4.5);        // 5（四舍五入）
$result: max(10, 20, 5);    // 20（最大值）
$result: min(10, 20, 5);    // 5（最小值）
$result: random(100);       // 1~100 之间的随机整数
$result: percentage(0.75);  // 75%（转为百分比）

// 单位处理
$is-unitless: unitless(16px);  // false（是否有单位）
$is-unitless: unitless(16);    // true
$unit: unit(16px);             // 'px'（获取单位）
$comparable: comparable(16px, 2rem);  // false（单位是否兼容）
```

### 10.3 字符串函数

```scss
$str: 'Hello, SCSS';

$quote: quote(Hello);          // "Hello"（加引号）
$unquote: unquote('"Hello"');  // Hello（去引号）

$upper: to-upper-case($str);   // "HELLO, SCSS"
$lower: to-lower-case($str);   // "hello, scss"

$length: str-length($str);     // 11（字符串长度）
$index: str-index($str, 'SCSS');  // 8（查找子串位置）
$insert: str-insert($str, ' World', 6);  // "Hello World, SCSS"（插入）
$slice: str-slice($str, 1, 5);  // "Hello"（截取）
$unique: unique-id();          // 生成唯一 ID 字符串
```

### 10.4 列表函数

```scss
$list: 10px 20px 30px 40px;

$length: length($list);                     // 4（列表长度）
$nth: nth($list, 2);                        // 20px（第 n 个元素）
$set-nth: set-nth($list, 2, 50px);          // 替换第 n 个元素
$join: join($list, (50px, 60px));           // 合并列表
$append: append($list, 50px);               // 追加元素
$index: index($list, 20px);                 // 2（查找元素位置）
$separator: list-separator($list);          // space（分隔符类型）
$is-bracketed: is-bracketed([10px, 20px]);  // true（是否有方括号）
```

### 10.5 Map 函数

```scss
$map: (
  'primary': #3498db,
  'secondary': #2ecc71,
  'danger': #e74c3c
);

$get: map-get($map, 'primary');                    // 获取值 #3498db
$merge: map-merge($map, ('warning': #f39c12));     // 合并 Map
$remove: map-remove($map, 'danger');               // 移除键
$keys: map-keys($map);                             // ('primary', 'secondary', 'danger')
$values: map-values($map);                         // (#3498db, #2ecc71, #e74c3c)
$has-key: map-has-key($map, 'primary');            // true
$deep-merge: map-deep-merge($map, (colors: ()));   // 深度合并（需 sass:map 模块）
```

### 10.6 自省函数（类型判断）

```scss
// 这些函数在 Mixin 和 Function 中做参数校验非常有用
@use 'sass:meta';

$var1: 16px;
$var2: #ff0000;
$var3: 'hello';
$var4: (1, 2, 3);
$var5: (key: value);

$t1: meta.type-of($var1);   // number
$t2: meta.type-of($var2);   // color
$t3: meta.type-of($var3);   // string
$t4: meta.type-of($var4);   // list
$t5: meta.type-of($var5);   // map

// 结合 @if 做参数校验
@mixin set-color($color) {
  @if meta.type-of($color) != 'color' {
    @error "参数必须是颜色值，传入的是 #{meta.type-of($color)}";
  }
  color: $color;
}
```

---

## 十一、实战综合案例

### 11.1 主题系统

```scss
// ===== 多主题切换系统 =====

// 定义主题 Map
$themes: (
  'light': (
    'bg': #ffffff,
    'text': #333333,
    'primary': #3498db,
    'border': #e0e0e0,
    'card-bg': #f8f9fa,
    'shadow': 0 2px 10px rgba(0, 0, 0, 0.08)
  ),
  'dark': (
    'bg': #1a1a2e,
    'text': #e0e0e0,
    'primary': #5dade2,
    'border': #2c2c44,
    'card-bg': #16213e,
    'shadow': 0 2px 10px rgba(0, 0, 0, 0.3)
  )
);

// 主题 Mixin：遍历主题生成 CSS 变量
@mixin generate-themes {
  @each $theme-name, $theme-map in $themes {
    [data-theme='#{$theme-name}'] {
      @each $key, $value in $theme-map {
        --#{$key}: #{$value};
      }
    }
  }
}

// 生成主题 CSS 变量
:root {
  @include generate-themes;
}

// 使用 CSS 变量，自动适配主题
body {
  background: var(--bg);
  color: var(--text);
}

.card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
}

.button {
  background: var(--primary);
  color: #fff;
}
```

### 11.2 响应式栅格系统

```scss
// ===== 完整的 12 列栅格系统 =====

$grid-columns: 12;
$grid-gutter: 30px;
$breakpoints: (
  'sm': 576px,
  'md': 768px,
  'lg': 992px,
  'xl': 1200px
);

// 容器
.container {
  width: 100%;
  padding-right: $grid-gutter / 2;
  padding-left: $grid-gutter / 2;
  margin-right: auto;
  margin-left: auto;
}

// 响应式容器宽度
@each $bp, $width in $breakpoints {
  @media (min-width: #{$width}) {
    .container {
      max-width: $width;
    }
  }
}

// 行
.row {
  display: flex;
  flex-wrap: wrap;
  margin-right: -$grid-gutter / 2;
  margin-left: -$grid-gutter / 2;
}

// 列
.col {
  flex: 1 0 0%;
  padding: 0 $grid-gutter / 2;
}

// 生成 .col-1 ~ .col-12
@for $i from 1 through $grid-columns {
  .col-#{$i} {
    flex: 0 0 auto;
    width: percentage($i / $grid-columns);
    padding: 0 $grid-gutter / 2;
  }
}

// 生成响应式列 .col-sm-1 ~ .col-xl-12
@each $bp, $width in $breakpoints {
  @media (min-width: #{$width}) {
    @for $i from 1 through $grid-columns {
      .col-#{$bp}-#{$i} {
        flex: 0 0 auto;
        width: percentage($i / $grid-columns);
        padding: 0 $grid-gutter / 2;
      }
    }
  }
}
```

### 11.3 组件库快速构建

```scss
// ===== 使用 SCSS 快速构建按钮组件库 =====

// 按钮尺寸配置
$btn-sizes: (
  'xs': (padding: 4px 8px, font-size: 12px, border-radius: 2px),
  'sm': (padding: 6px 12px, font-size: 14px, border-radius: 3px),
  'md': (padding: 10px 20px, font-size: 16px, border-radius: 4px),
  'lg': (padding: 14px 28px, font-size: 18px, border-radius: 6px),
  'xl': (padding: 18px 36px, font-size: 20px, border-radius: 8px)
);

// 按钮颜色配置
$btn-colors: (
  'primary':   (#3498db, #2980b9, #fff),
  'secondary': (#95a5a6, #7f8c8d, #fff),
  'success':   (#2ecc71, #27ae60, #fff),
  'danger':    (#e74c3c, #c0392b, #fff),
  'warning':   (#f39c12, #e67e22, #fff),
  'info':      (#9b59b6, #8e44ad, #fff),
  'light':     (#ecf0f1, #bdc3c7, #333),
  'dark':      (#2c3e50, #1a252f, #fff)
);

// 基础按钮样式
%btn-base {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 1px solid transparent;
  font-weight: 500;
  text-align: center;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
  white-space: nowrap;

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    pointer-events: none;
  }
}

// 按钮基类
.btn {
  @extend %btn-base;
}

// 生成颜色变体
@each $name, $config in $btn-colors {
  $bg: nth($config, 1);
  $hover-bg: nth($config, 2);
  $text: nth($config, 3);

  .btn--#{$name} {
    background: $bg;
    color: $text;
    border-color: $bg;

    &:hover:not(:disabled) {
      background: $hover-bg;
      border-color: $hover-bg;
    }
  }

  // 轮廓按钮变体
  .btn--outline-#{$name} {
    background: transparent;
    color: $bg;
    border-color: $bg;

    &:hover:not(:disabled) {
      background: $bg;
      color: $text;
    }
  }
}

// 生成尺寸变体
@each $size, $styles in $btn-sizes {
  .btn--#{$size} {
    padding: map-get($styles, padding);
    font-size: map-get($styles, font-size);
    border-radius: map-get($styles, border-radius);
  }
}

// 块级按钮
.btn--block {
  display: flex;
  width: 100%;
}

// 圆角按钮
.btn--rounded {
  border-radius: 50px;
}

// 使用示例：
// <button class="btn btn--primary btn--lg">主要按钮</button>
// <button class="btn btn--outline-danger btn--sm">危险按钮</button>
```

### 11.4 Flex 与 Grid 工具类生成

```scss
// ===== Flex 工具类 =====
$flex-alignments: (
  'start': flex-start,
  'end': flex-end,
  'center': center,
  'between': space-between,
  'around': space-around,
  'evenly': space-evenly
);

// 生成 .flex { display: flex; }
.flex {
  display: flex;
}

// 生成 .flex-row, .flex-column
.flex-row {
  flex-direction: row;
}
.flex-column {
  flex-direction: column;
}

// 生成对齐类
@each $name, $value in $flex-alignments {
  .justify-#{$name} {
    justify-content: $value;
  }
  .items-#{$name} {
    align-items: $value;
  }
}

// 生成 .flex-wrap, .flex-nowrap
.flex-wrap {
  flex-wrap: wrap;
}
.flex-nowrap {
  flex-wrap: nowrap;
}

// 生成 .flex-1 ~ .flex-5
@for $i from 1 through 5 {
  .flex-#{$i} {
    flex: $i;
  }
}


// ===== Grid 工具类 =====
.grid {
  display: grid;
}

// 生成 .grid-cols-1 ~ .grid-cols-12
@for $i from 1 through 12 {
  .grid-cols-#{$i} {
    grid-template-columns: repeat($i, 1fr);
  }
}

// 生成间距
$gaps: (
  '0': 0,
  '1': 4px,
  '2': 8px,
  '3': 16px,
  '4': 24px,
  '5': 48px
);

@each $name, $value in $gaps {
  .gap-#{$name} {
    gap: $value;
  }
}
```

---

## 十二、面试题集锦

### 面试题 1：SCSS 变量和 CSS 变量的区别？

**知识点**：变量机制、编译时 vs 运行时

**参考答案**：

| 对比维度 | SCSS 变量 | CSS 自定义属性 |
|---------|----------|--------------|
| 定义方式 | `$var: value;` | `--var: value;` |
| 使用方式 | `$var` | `var(--var)` |
| 作用域 | 块级作用域 | 继承（DOM 层级） |
| 运行时 | 编译后消失 | 运行时存在，可被 JS 修改 |
| 动态性 | 静态，编译时确定 | 动态，可响应媒体查询等 |
| 适用场景 | 主题配置、全局常量 | 动态主题、组件级变量 |

```scss
// SCSS 变量：编译时确定
$primary: #3498db;
.element {
  background: $primary;  // 编译后直接替换为 #3498db
}

// CSS 变量：运行时生效
:root {
  --primary: #3498db;
}
.element {
  background: var(--primary);  // 运行时从 DOM 树继承
  // JavaScript 可修改：element.style.setProperty('--primary', '#ff0000')
}
```

---

### 面试题 2：@mixin 和 @extend 的区别及使用场景？

**知识点**：代码复用、编译输出、选择器合并

**参考答案**：

| 维度 | @mixin | @extend |
|------|--------|---------|
| 参数 | 支持参数 | 不支持参数 |
| 编译方式 | 代码复制到每个调用处 | 选择器合并为一组 |
| CSS 体积 | 可能较大（重复代码） | 更小（选择器分组） |
| 灵活性 | 高（可传参、动态值） | 低（静态继承） |
| @content | 支持 | 不支持 |
| 媒体查询内 | 可正常使用 | 有限制 |

**使用建议**：
- 需要参数或动态值 → `@mixin`
- 静态样式复用（如 clearfix）→ `%placeholder` + `@extend`
- 组件变体生成 → `@mixin`
- 不要滥用 `@extend`，可能导致选择器顺序混乱

---

### 面试题 3：`@use` 和 `@import` 的区别？

**知识点**：模块系统、命名空间、Sass 演进

**参考答案**：

```scss
// @import（旧方式，即将废弃）
// 缺点：
// 1. 全局作用域，所有变量/Mixin 全局可见，不知道来源
// 2. 多次 @import 同一文件会重复编译
// 3. 没有命名空间，容易命名冲突

// @use（新方式）
// 优点：
// 1. 命名空间隔离，明确来源
// 2. 同一文件只会编译一次
// 3. 通过 @forward 控制导出
// 4. 支持 with 配置

// 迁移示例
// 旧：@import 'variables';
//     color: $primary;  // 不知道 $primary 来自哪里

// 新：@use 'variables';
//     color: variables.$primary;  // 明确来源
```

---

### 面试题 4：SCSS 中 `&` 的作用是什么？有哪些常见用法？

**知识点**：父选择器引用、BEM 命名

**参考答案**：

`&` 代表当前选择器的父级引用，常见用法包括：

```scss
// 1. 伪类/伪元素
.button {
  &:hover { ... }    // .button:hover
  &:focus { ... }    // .button:focus
  &::before { ... }  // .button::before
}

// 2. BEM 命名
.block {
  &__element { ... }     // .block__element
  &--modifier { ... }    // .block--modifier
}

// 3. 组合选择器
.component {
  &.active { ... }       // .component.active
  .parent & { ... }      // .parent .component（& 放在后面）
}

// 4. 复合选择器
.link {
  &-primary { ... }      // .link-primary
  &-secondary { ... }    // .link-secondary
}
```

---

### 面试题 5：`@content` 的作用和使用场景？

**知识点**：内容块注入、高阶 Mixin

**参考答案**：

`@content` 允许向 Mixin 中注入自定义代码块，常用于响应式设计和布局模式。

```scss
// 经典场景：响应式断点
@mixin respond-to($breakpoint) {
  @media (min-width: $breakpoint) {
    @content;
  }
}

// 使用
.container {
  width: 100%;

  @include respond-to(768px) {
    width: 750px;   // 被注入到 @media 内部
  }

  @include respond-to(1200px) {
    width: 1170px;
  }
}

// 其他场景：
// - 布局模式封装（flex/grid 容器）
// - 条件渲染（如仅在特定条件下应用样式）
// - 动画状态管理
```

---

### 面试题 6：`@for`、`@each`、`@while` 的区别和使用场景？

**知识点**：循环控制、列表遍历

**参考答案**：

| 指令 | 适用场景 | 特点 |
|------|---------|------|
| `@for` | 固定次数循环 | 用于生成序列（如栅格列 col-1 ~ col-12） |
| `@each` | 遍历列表/Map | 最适合遍历预定义集合（如颜色、断点） |
| `@while` | 条件循环 | 灵活但需手动控制，较少使用 |

```scss
// @for：生成栅格（固定次数）
@for $i from 1 through 12 {
  .col-#{$i} { width: percentage($i / 12); }
}

// @each：遍历颜色 Map（预定义集合）
$colors: (primary: blue, danger: red);
@each $name, $color in $colors {
  .btn-#{$name} { background: $color; }
}

// @while：生成等比数列（条件未知）
$size: 10px;
@while $size <= 40px {
  .fs-#{$size} { font-size: $size; }
  $size: $size + 10px;
}
```

---

### 面试题 7：SCSS 中 `!default` 和 `!global` 的区别？

**知识点**：变量作用域、默认值

**参考答案**：

```scss
// !default：如果变量未被赋值，则使用此默认值
// 场景：库/框架定义可覆盖的默认变量
$primary-color: blue !default;  // 若已定义 $primary-color，此行被忽略

// !global：将局部变量提升为全局作用域
// 场景：在嵌套块中修改全局变量
.header {
  $theme: 'dark' !global;  // 将 $theme 提升为全局变量
}
```

---

### 面试题 8：如何用 SCSS 实现一个响应式栅格系统？

**知识点**：循环、Map、插值、@media 综合应用

**参考答案**：参见 [第十一章 11.2 响应式栅格系统](#112-响应式栅格系统)。

核心思路：
1. 定义断点 Map
2. `@each` 遍历断点生成 `@media` 查询
3. `@for` 循环生成列宽（`percentage($i / 12)`）
4. 插值 `#{}` 拼接类名如 `.col-md-6`

---

### 面试题 9：SCSS 中 `@warn`、`@error`、`@debug` 的区别？

**知识点**：调试、错误处理

**参考答案**：

| 指令 | 作用 | 是否中断编译 |
|------|------|------------|
| `@debug` | 输出调试信息到控制台 | 否 |
| `@warn` | 输出警告信息 | 否 |
| `@error` | 抛出错误并中断编译 | 是 |

```scss
@mixin respond-to($breakpoint) {
  @if not map-has-key($breakpoints, $breakpoint) {
    @error "断点 '#{$breakpoint}' 不存在！可用断点: #{map-keys($breakpoints)}";
  }
  @media (min-width: map-get($breakpoints, $breakpoint)) {
    @content;
  }
}

@function get-color($name) {
  @if not map-has-key($colors, $name) {
    @warn "颜色 '#{$name}' 未找到，使用默认颜色";
    @return #333;
  }
  @return map-get($colors, $name);
}
```

---

### 面试题 10：SCSS 中如何处理浏览器兼容性前缀？

**知识点**：Mixin 封装、CSS 兼容性

**参考答案**：

```scss
// 通过 Mixin 封装浏览器前缀，集中管理兼容性
@mixin prefix($property, $value, $prefixes: ()) {
  @each $prefix in $prefixes {
    -#{$prefix}-#{$property}: $value;
  }
  #{$property}: $value;
}

// 使用
.element {
  @include prefix(transform, rotate(45deg), webkit ms);
  @include prefix(border-radius, 10px, webkit moz);
  @include prefix(box-shadow, 0 2px 5px rgba(0,0,0,0.2), webkit moz);
}

// 编译结果：
// .element {
//   -webkit-transform: rotate(45deg);
//   -ms-transform: rotate(45deg);
//   transform: rotate(45deg);
//   -webkit-border-radius: 10px;
//   -moz-border-radius: 10px;
//   border-radius: 10px;
// }

// 注意：现代项目推荐使用 Autoprefixer（PostCSS 插件）
// 自动处理前缀，无需手动编写 Mixin
```

---

### 面试题 11：SCSS 中 `@function` 和 `@mixin` 的核心区别？

**知识点**：函数 vs 混合宏

**参考答案**：

| 维度 | @function | @mixin |
|------|-----------|--------|
| 返回值 | 通过 `@return` 返回值 | 输出样式块 |
| 调用方式 | 直接调用 `function()` | `@include mixin()` |
| 使用位置 | 可出现在任何值的位置 | 只能出现在样式规则位置 |
| 包含样式 | 不可以 | 可以 |

```scss
// @function：计算值，用在属性值中
@function rem($px) {
  @return ($px / 16px) * 1rem;
}

.element {
  font-size: rem(24);  // 返回 1.5rem，作为属性值
}

// @mixin：输出样式块
@mixin flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

.element {
  @include flex-center;  // 输出一组样式规则
}
```

---

### 面试题 12：SCSS 中 `@at-root` 的使用场景和注意事项？

**知识点**：跳出嵌套

**参考答案**：

```scss
// 场景 1：在 BEM 嵌套中避免过深的选择器
.card {
  padding: 20px;

  &__header {
    font-size: 20px;

    // 跳出嵌套，防止 .card__header .card__title
    @at-root .card__title {
      font-weight: bold;
    }
  }
}

// 编译为：
// .card { padding: 20px; }
// .card__header { font-size: 20px; }
// .card__title { font-weight: bold; }

// 场景 2：配合 (without: ...) 或 (with: ...) 精确控制
.parent {
  color: red;

  @at-root (without: all) {
    // 跳出所有嵌套层级
    .child { color: blue; }
  }
}
```

---

> **学习建议**：建议按顺序阅读各章节，先掌握变量、嵌套、Mixin 等基础语法，再深入学习循环、条件、模块化等高级特性。每节的代码示例均可直接复制到 `.scss` 文件中编译验证。