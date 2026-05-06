# Sass 使用指南

## 什么是 Sass？

Sass（Syntactically Awesome Style Sheets）是一个 CSS 预处理器，它扩展了 CSS 的功能，提供了变量、嵌套规则、混合（mixins）、函数等高级功能，使 CSS 更易于维护和编写。

## Sass 的两种语法

### 1. SCSS 语法（推荐）
SCSS（Sassy CSS）是 Sass 3 引入的新语法，完全兼容 CSS3 语法，使用 `.scss` 文件扩展名。

```scss
// 变量
$primary-color: #3498db;
$font-stack: Helvetica, sans-serif;

// 嵌套
nav {
  ul {
    margin: 0;
    padding: 0;
    list-style: none;
  }

  li {
    display: inline-block;
  }

  a {
    color: $primary-color;
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }
}
```

### 2. 缩进语法（旧语法）
使用 `.sass` 文件扩展名，基于缩进而非花括号。

```sass
$primary-color: #3498db
$font-stack: Helvetica, sans-serif

nav
  ul
    margin: 0
    padding: 0
    list-style: none

  li
    display: inline-block

  a
    color: $primary-color
    text-decoration: none
    
    &:hover
      text-decoration: underline
```

## 核心特性

### 1. 变量
```scss
// 定义变量
$primary-color: #3498db;
$secondary-color: #2ecc71;
$font-size-base: 16px;
$spacing-unit: 8px;

// 使用变量
.header {
  background-color: $primary-color;
  font-size: $font-size-base;
  padding: $spacing-unit * 2;
}
```

### 2. 嵌套
```scss
// CSS 嵌套
.container {
  width: 100%;
  
  .header {
    background: #333;
    
    .logo {
      width: 100px;
      height: 50px;
    }
  }
  
  .content {
    padding: 20px;
    
    p {
      line-height: 1.6;
    }
  }
}

// 父选择器引用
.button {
  background: blue;
  
  &:hover {
    background: darkblue;
  }
  
  &.active {
    background: green;
  }
  
  &--large {
    padding: 20px;
  }
}
```

### 3. 混合（Mixins）
```scss
// 定义混合
@mixin flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

@mixin border-radius($radius) {
  -webkit-border-radius: $radius;
  -moz-border-radius: $radius;
  border-radius: $radius;
}

@mixin box-shadow($x, $y, $blur, $color) {
  -webkit-box-shadow: $x $y $blur $color;
  -moz-box-shadow: $x $y $blur $color;
  box-shadow: $x $y $blur $color;
}

// 使用混合
.card {
  @include flex-center;
  @include border-radius(10px);
  @include box-shadow(0, 2px, 10px, rgba(0,0,0,0.1));
}
```

### 4. 继承
```scss
// 基础样式
%button-base {
  display: inline-block;
  padding: 10px 20px;
  border: none;
  cursor: pointer;
  font-size: 16px;
  text-align: center;
}

// 继承
.primary-button {
  @extend %button-base;
  background-color: #3498db;
  color: white;
  
  &:hover {
    background-color: #2980b9;
  }
}

.secondary-button {
  @extend %button-base;
  background-color: #95a5a6;
  color: white;
  
  &:hover {
    background-color: #7f8c8d;
  }
}
```

### 5. 函数
```scss
// 内置函数
$primary-color: #3498db;

.darken {
  background-color: darken($primary-color, 20%);
}

.lighten {
  background-color: lighten($primary-color, 20%);
}

.transparent {
  background-color: transparentize($primary-color, 0.5);
}

// 自定义函数
@function calculate-rem($px) {
  @return ($px / 16px) * 1rem;
}

@function spacing($multiplier) {
  @return $multiplier * 8px;
}

// 使用函数
.container {
  font-size: calculate-rem(16px);
  margin: spacing(2);
  padding: spacing(1);
}
```

### 6. 控制指令
```scss
// @if, @else if, @else
@mixin theme-colors($theme) {
  @if $theme == 'light' {
    background-color: white;
    color: black;
  } @else if $theme == 'dark' {
    background-color: black;
    color: white;
  } @else {
    background-color: gray;
    color: white;
  }
}

// @for 循环
@for $i from 1 through 5 {
  .col-#{$i} {
    width: percentage($i / 5);
  }
}

// @each 循环
$colors: red, green, blue, yellow;

@each $color in $colors {
  .text-#{$color} {
    color: $color;
  }
}

// @while 循环
$i: 1;
@while $i <= 3 {
  .item-#{$i} {
    width: 100px * $i;
  }
  $i: $i + 1;
}
```

## 模块化

### 1. Partials 和 @import
```scss
// _variables.scss (partial file)
$primary-color: #3498db;
$secondary-color: #2ecc71;

// _mixins.scss (partial file)
@mixin flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

// main.scss
@import 'variables';
@import 'mixins';

.container {
  background-color: $primary-color;
  @include flex-center;
}
```

### 2. @use 和 @forward（Sass 模块系统）
```scss
// _variables.scss
$primary-color: #3498db !default;
$secondary-color: #2ecc71 !default;

// _mixins.scss
@mixin flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

// _index.scss
@forward 'variables';
@forward 'mixins';

// main.scss
@use 'index' as *;

.container {
  background-color: $primary-color;
  @include flex-center;
}
```

## 安装和使用

### 1. 安装 Sass
```bash
# 使用 npm
npm install -g sass

# 使用 yarn
yarn global add sass

# 检查安装
sass --version
```

### 2. 基本使用
```bash
# 编译单个文件
sass input.scss output.css

# 监听文件变化
sass --watch input.scss:output.css

# 压缩输出
sass input.scss output.css --style compressed

# 编译整个目录
sass --watch src/scss:dist/css
```

### 3. 在项目中配置
```json
// package.json
{
  "scripts": {
    "sass": "sass src/scss:dist/css",
    "sass:watch": "sass --watch src/scss:dist/css",
    "sass:build": "sass src/scss:dist/css --style compressed"
  },
  "devDependencies": {
    "sass": "^1.77.0"
  }
}
```

## 最佳实践

### 1. 文件组织
```
scss/
├── abstracts/
│   ├── _variables.scss
│   ├── _functions.scss
│   ├── _mixins.scss
│   └── _placeholders.scss
├── base/
│   ├── _reset.scss
│   ├── _typography.scss
│   └── _base.scss
├── components/
│   ├── _buttons.scss
│   ├── _cards.scss
│   └── _forms.scss
├── layout/
│   ├── _header.scss
│   ├── _footer.scss
│   └── _grid.scss
├── pages/
│   ├── _home.scss
│   └── _contact.scss
├── themes/
│   └── _dark.scss
└── main.scss
```

### 2. 命名规范
```scss
// BEM 命名法
.block {
  &__element {
    &--modifier {
    }
  }
}

// 示例
.card {
  &__header {
    &--large {
    }
  }
  
  &__body {
  }
  
  &__footer {
  }
}
```

### 3. 响应式设计
```scss
// 断点变量
$breakpoints: (
  'xs': 0,
  'sm': 576px,
  'md': 768px,
  'lg': 992px,
  'xl': 1200px,
  'xxl': 1400px
);

// 响应式混合
@mixin respond-to($breakpoint) {
  @if map-has-key($breakpoints, $breakpoint) {
    @media (min-width: map-get($breakpoints, $breakpoint)) {
      @content;
    }
  } @else {
    @warn "Unknown breakpoint: #{$breakpoint}";
  }
}

// 使用
.container {
  width: 100%;
  
  @include respond-to('md') {
    width: 750px;
  }
  
  @include respond-to('lg') {
    width: 970px;
  }
}
```

## 实际示例

### 1. 按钮组件
```scss
// _buttons.scss
$button-padding: 12px 24px;
$button-border-radius: 4px;
$button-font-size: 16px;

@mixin button-variant($background, $color, $hover-background) {
  background-color: $background;
  color: $color;
  border: 1px solid darken($background, 10%);
  
  &:hover {
    background-color: $hover-background;
    border-color: darken($hover-background, 10%);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.button {
  display: inline-block;
  padding: $button-padding;
  border-radius: $button-border-radius;
  font-size: $button-font-size;
  text-align: center;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &--primary {
    @include button-variant(#3498db, white, #2980b9);
  }
  
  &--secondary {
    @include button-variant(#95a5a6, white, #7f8c8d);
  }
  
  &--success {
    @include button-variant(#2ecc71, white, #27ae60);
  }
  
  &--large {
    padding: 16px 32px;
    font-size: 18px;
  }
  
  &--small {
    padding: 8px 16px;
    font-size: 14px;
  }
}
```

### 2. 卡片组件
```scss
// _cards.scss
$card-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
$card-border-radius: 8px;
$card-padding: 20px;

.card {
  background: white;
  border-radius: $card-border-radius;
  box-shadow: $card-shadow;
  padding: $card-padding;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
  }
  
  &__header {
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
  }
  
  &__title {
    font-size: 20px;
    font-weight: bold;
    margin: 0;
  }
  
  &__body {
    line-height: 1.6;
  }
  
  &__footer {
    margin-top: 15px;
    padding-top: 10px;
    border-top: 1px solid #eee;
    text-align: right;
  }
  
  &--featured {
    border-left: 4px solid #3498db;
  }
}
```

## 常见问题

### 1. 编译错误
```bash
# 查看详细错误信息
sass input.scss output.css --trace

# 启用 Source Maps
sass input.scss output.css --source-map
```

### 2. 性能优化
```scss
// 避免过度嵌套
// ❌ 不好
.container {
  .header {
    .nav {
      ul {
        li {
          a {
            // 太深了！
          }
        }
      }
    }
  }
}

// ✅ 更好
.container {
  .header-nav {
    ul {
      li {
        a {
          // 合理的深度
        }
      }
    }
  }
}
```

### 3. 浏览器兼容性
```scss
// 使用 Autoprefixer 处理前缀
// 不要手动写前缀
@mixin transform($property) {
  transform: $property;
}

.element {
  @include transform(rotate(45deg));
}
```

## 总结

Sass 是一个强大的 CSS 预处理器，通过以下功能提升开发效率：
1. **变量** - 统一管理颜色、尺寸等
2. **嵌套** - 清晰的层级结构
3. **混合** - 可复用的代码块
4. **继承** - 减少重复代码
5. **函数和运算** - 动态计算值
6. **模块化** - 更好的代码组织

建议从 SCSS 语法开始学习，因为它更接近原生 CSS，更容易上手。随着项目规模增大，合理组织文件结构和遵循最佳实践将大大提高代码的可维护性。