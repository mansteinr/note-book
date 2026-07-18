# Stylus 常见面试题集

> 本文档系统整理 Stylus CSS 预处理器的高频面试题，涵盖基础语法、核心特性、高级用法、与 SCSS/LESS 的对比及实际应用场景。共 25 道题目，按初级、中级、高级三个难度层次划分，每题附参考答案与考察要点，适合不同层次的前端开发者面试准备。

---

## 目录

- [一、Stylus 简介](#一stylus-简介)
- [二、初级题目（10 道）](#二初级题目10-道)
- [三、中级题目（10 道）](#三中级题目10-道)
- [四、高级题目（5 道）](#四高级题目5-道)
- [附录：考点速查表](#附录考点速查表)

---

## 一、Stylus 简介

Stylus 是由 TJ Holowaychuk（Express.js 作者）于 2010 年创建的 CSS 预处理器，基于 Node.js 平台。它吸取了 SCSS 和 LESS 的设计精华，同时提供了更灵活、更富表现力的语法。

**核心特点：**

| 特性 | 说明 |
|------|------|
| 语法灵活 | 支持标准 CSS 语法、缩进语法（无花括号/分号/冒号）、极简风格 |
| 变量 | 以 `$` 或自定义前缀开头，也可省略前缀直接赋值 |
| 嵌套 | 支持选择器嵌套和属性嵌套 |
| 混合 Mixins | 透明混合（无需特殊关键字），定义和调用极简 |
| 函数 | 支持自定义函数，有 `return` 语句 |
| 条件与循环 | 内置 `if/else`、`for/in`、`for/range` 等控制流 |
| 内置函数 | 丰富的颜色、数学、字符串、图像处理函数 |
| 模块化 | 支持 `@import` 和 `@require` |
| 运算符 | 支持 `[]` 下标访问、`..` 和 `...` 范围运算符 |

**安装与编译：**

```bash
npm install -g stylus

# 编译单个文件
stylus styles.styl -o styles.css

# 监听并编译
stylus -w styles.styl -o styles.css

# 压缩输出
stylus -c styles.styl -o styles.min.css
```

---

## 二、初级题目（10 道）

---

### Q1：Stylus 是什么？它有哪些核心特性？

**难度：** 初级

**考察知识点：** Stylus 基本概念、核心特性 | **能力等级：** 初级

**参考答案：**

Stylus 是由 TJ Holowaychuk 创建的基于 Node.js 的 CSS 预处理器。它在 CSS 基础上扩展了变量、嵌套、混合、函数、条件循环等编程特性。

**核心特性：**

1. **语法自由度极高**：可同时接受标准 CSS 语法（花括号/分号）、缩进语法（省略花括号）和极简风格（省略冒号/分号）
2. **变量系统**：`$` 前缀变量，支持属性查找和 `@` 引用
3. **透明混合**：定义即为普通选择器，调用时直接写名称即可，无需 `@include` 等关键字
4. **内置控制流**：`if/else`、`for/in`、`for/range` 等，表达能力强大
5. **函数支持**：可自定义函数，且有 `return` 语句
6. **丰富的内置函数**：提供颜色运算、数学计算、图像处理等工具函数
7. **属性嵌套**：可将属性名嵌套（如 `font` 下有 `size`、`weight` 等）

**评分标准：**
- 说出 Stylus 的基本定位（30%）
- 列举至少 4 个核心特性（40%）
- 能简要说明语法灵活性（30%）

---

### Q2：Stylus 支持哪几种语法风格？各有什么特点？

**难度：** 初级

**考察知识点：** 语法风格、灵活性 | **能力等级：** 初级

**参考答案：**

Stylus 支持三种语法风格，可在同一文件中混合使用：

**1. 标准 CSS 风格（完全兼容 CSS）**

```stylus
.button {
  color: #fff;
  background: #1890ff;
  border-radius: 4px;
}
```

**2. 缩进风格（省略花括号和分号，类似 Sass）**

```stylus
.button
  color: #fff
  background: #1890ff
  border-radius: 4px
```

**3. 极简风格（省略冒号和分号）**

```stylus
.button
  color #fff
  background #1890ff
  border-radius 4px
```

**特点对比：**

| 风格 | 花括号 | 冒号 | 分号 | 适用场景 |
|------|--------|------|------|----------|
| 标准 CSS | 有 | 有 | 有 | 从 CSS 迁移、团队协作 |
| 缩进风格 | 无 | 有 | 无 | 简洁编码、Sass 用户 |
| 极简风格 | 无 | 无 | 无 | 快速原型、个人项目 |

**注意事项：** 极简风格下，属性名和值之间必须有空格。混合使用不同风格时需保持一致性，避免造成混淆。

**评分标准：**
- 列举三种风格（30%）
- 每种风格写出示例（40%）
- 说明适用场景和注意事项（30%）

---

### Q3：Stylus 中如何定义和使用变量？

**难度：** 初级

**考察知识点：** 变量定义与使用 | **能力等级：** 初级

**参考答案：**

Stylus 变量以 `$` 开头，赋值使用 `=` 或 `:`。变量支持块级作用域。

```stylus
// 变量定义
$primary-color = #1890ff
$font-size-base = 14px
$font-family = -apple-system, BlinkMacSystemFont, sans-serif

// 使用变量
.button
  background $primary-color
  font-size $font-size-base
  font-family $font-family
  padding ($font-size-base / 2) $font-size-base

// 变量可参与运算
$base = 4px
.margin
  margin ($base * 2) ($base * 4)  // 8px 16px
```

**属性查找（Property Lookup）：** 使用 `@` 前缀引用当前选择器或父级选择器的属性值。

```stylus
.box
  color #333
  background @color           // 引用当前选择器的 color 值 → #333
  border-color darken(@color, 20%)
```

**变量作用域：**

```stylus
$color = red

.block
  $color = blue
  color $color           // 输出 blue
  .element
    $color = green
    color $color         // 输出 green
  color $color           // 输出 blue（回到 .block 作用域）
```

**评分标准：**
- 正确写出变量定义和使用语法（40%）
- 解释属性查找 `@` 的用法（30%）
- 理解作用域查找规则（30%）

---

### Q4：Stylus 的嵌套规则有哪些？什么是属性嵌套？

**难度：** 初级

**考察知识点：** 嵌套规则 | **能力等级：** 初级

**参考答案：**

**选择器嵌套：** 与 SCSS/LESS 类似，`&` 代表父选择器。

```stylus
.nav
  background #333
  li
    display inline-block
  a
    color #fff
    &:hover
      color #1890ff
    &.active
      font-weight bold
```

**属性嵌套（Property Nesting）：** Stylus 的独特特性，允许将带相同前缀的属性分组嵌套。

```stylus
.box
  font
    size 14px
    weight bold
    family 'Microsoft YaHei', sans-serif
  // 编译为：
  // font-size: 14px;
  // font-weight: bold;
  // font-family: 'Microsoft YaHei', sans-serif;

  margin
    top 10px
    right 20px
    bottom 10px
    left 20px
  // 编译为：
  // margin-top: 10px;
  // margin-right: 20px;
  // margin-bottom: 10px;
  // margin-left: 20px;

  border
    1px solid #ddd    // 直接写值，编译为 border: 1px solid #ddd;
    radius 4px         // 扩张属性，编译为 border-radius: 4px;
```

**属性嵌套的优势：**
- 减少重复书写属性前缀
- 结构更清晰，符合视觉逻辑
- 是 Stylus 区别于 SCSS/LESS 的显著特性之一

**评分标准：**
- 理解基本选择器嵌套（30%）
- 能写出属性嵌套示例（40%）
- 理解属性嵌套的编译规则（30%）

---

### Q5：Stylus 中 Mixin（混合）如何定义和使用？与 SCSS/LESS 有何不同？

**难度：** 初级

**考察知识点：** Mixin 定义与调用 | **能力等级：** 初级

**参考答案：**

Stylus 的 Mixin 是**透明混合**——定义就是普通选择器，调用时直接写名称即可，无需 `@include`（SCSS）或 `.mixin()`（LESS）等特殊关键字。

```stylus
// 定义 Mixin（与普通选择器写法一致）
border-radius($radius = 4px)
  -webkit-border-radius $radius
  -moz-border-radius $radius
  border-radius $radius

// 调用 Mixin（直接写名称，无需关键字）
.btn
  border-radius(6px)       // 带参数调用
  padding 8px 16px

.avatar
  border-radius()           // 使用默认值
  // 或省略括号：border-radius
```

**多参数混合：**

```stylus
box-shadow($x = 0, $y = 2px, $blur = 4px, $color = rgba(0,0,0,.15))
  box-shadow $x $y $blur $color

.card
  box-shadow(0, 4px, 8px, rgba(0,0,0,.2))
```

**与 SCSS/LESS 的关键区别：**

| 维度 | Stylus | SCSS | LESS |
|------|--------|------|------|
| 定义方式 | 普通选择器 | `@mixin name { }` | `.name() { }` |
| 调用方式 | 直接写名称 | `@include name` | `.name()` |
| 语法噪音 | 最少 | 中等 | 中等 |
| 透明性 | 完全透明（定义即调用） | 需要 `@mixin` 和 `@include` | 需要括号区分 |

**评分标准：**
- 理解透明混合的概念（30%）
- 写出正确的定义与调用示例（40%）
- 与 SCSS/LESS 对比清晰（30%）

---

### Q6：Stylus 中如何使用 `@import` 和 `@require` 进行模块化？

**难度：** 初级

**考察知识点：** 模块化导入 | **能力等级：** 初级

**参考答案：**

Stylus 提供两种导入方式：

**`@import`：** 导入并编译输出。

```stylus
// 导入 .styl 文件（扩展名可省略）
@import 'variables'
@import 'mixins'
@import 'reset'

// 导入 CSS 文件（保留 .css 扩展名，输出为 CSS @import 语句）
@import 'normalize.css'

// 导入多个文件
@import 'variables', 'mixins', 'components/button'
```

**`@require`：** 仅导入一次（类似 Node.js 的 `require`），重复导入会被忽略。

```stylus
@require 'variables'
@require 'mixins'
```

**`@import` 与 `@require` 的区别：**

| 维度 | @import | @require |
|------|---------|----------|
| 重复导入 | 每次都会执行 | 只执行一次，后续忽略 |
| 适用场景 | 需要每次导入都输出 | 全局变量、混合等需幂等 |
| 类比 | CSS 的 @import | Node.js 的 require() |

**推荐的模块化组织结构：**

```
styles/
├── main.styl                # 入口
├── base/
│   ├── variables.styl       # @require
│   ├── mixins.styl          # @require
│   └── reset.styl           # @import
├── components/
│   ├── button.styl
│   ├── form.styl
│   └── modal.styl
└── pages/
    ├── home.styl
    └── about.styl
```

```stylus
// main.styl
@require 'base/variables'
@require 'base/mixins'
@import 'base/reset'
@import 'components/button'
@import 'components/form'
```

**评分标准：**
- 区分 `@import` 和 `@require`（40%）
- 理解各自适用场景（30%）
- 能画出模块化目录结构（30%）

---

### Q7：Stylus 中如何实现 Extend（继承）？

**难度：** 初级

**考察知识点：** 继承语法 | **能力等级：** 初级

**参考答案：**

Stylus 提供 `@extend` 语法实现选择器继承，生成的 CSS 使用选择器分组，避免代码重复。

```stylus
// 基础类
.message
  padding 10px
  border 1px solid #ddd
  border-radius 4px

// 继承
.message-success
  @extend .message
  background #dff0d8
  border-color #d0e9c6
  color #3c763d

.message-error
  @extend .message
  background #f2dede
  border-color #ebccd1
  color #a94442
```

**编译结果：**

```css
.message,
.message-success,
.message-error {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.message-success {
  background: #dff0d8;
  border-color: #d0e9c6;
  color: #3c763d;
}
.message-error {
  background: #f2dede;
  border-color: #ebccd1;
  color: #a94442;
}
```

**占位符选择器：** 使用 `$` 前缀定义仅用于继承的选择器，不会输出到 CSS。

```stylus
$base-style
  color #333
  font-size 14px
  line-height 1.5

.article
  @extend $base-style
  margin 20px

// $base-style 不会输出到 CSS
```

**Extend 与 Mixin 的选择：**

| 场景 | Extend | Mixin |
|------|--------|-------|
| 静态样式继承 | 推荐 | 可用 |
| 需要参数化 | 不支持 | 推荐 |
| 需要动态逻辑 | 不支持 | 推荐 |
| 需要紧凑 CSS 输出 | 推荐 | 样式会重复 |

**评分标准：**
- 写出 `@extend` 用法（40%）
- 理解占位符选择器 `$`（30%）
- 理解 Extend vs Mixin 的选择依据（30%）

---

### Q8：Stylus 中的插值语法如何使用？

**难度：** 初级

**考察知识点：** 插值 | **能力等级：** 初级

**参考答案：**

Stylus 使用 `{}`（花括号）进行插值，比 SCSS 的 `#{}` 和 LESS 的 `@{}` 更简洁。

```stylus
// 选择器插值
$component = 'card'

.{$component}
  padding 20px
  &__title
    font-size 18px
  &--large
    padding 40px

// 编译为：
// .card { padding: 20px; }
// .card__title { font-size: 18px; }
// .card--large { padding: 40px; }
```

```stylus
// 属性名插值
$direction = 'left'
$value = 'margin'

.box
  {$value}-{$direction} 20px
  // 编译为：margin-left: 20px;
```

```stylus
// 选择器中的复杂插值
$prefix = 'col'
for $i in 1..12
  .{$prefix}-{$i}
    width ($i / 12 * 100)%
```

```stylus
// 字符串插值
$base-url = 'https://cdn.example.com'
$version = '2.0'

.logo
  background-image url($base-url + '/logo.png?v=' + $version)
  // 或使用 sprintf 函数
  background-image url(s('https://cdn.example.com/logo.png?v=%s', $version))
```

**评分标准：**
- 写出选择器插值（40%）
- 写出属性名插值（30%）
- 了解字符串拼接方式（30%）

---

### Q9：Stylus 如何进行数值运算？

**难度：** 初级

**考察知识点：** 运算 | **能力等级：** 初级

**参考答案：**

Stylus 支持加（+）、减（-）、乘（*）、除（/）、取模（%）等运算，并自动处理单位转换。

```stylus
$base = 4px

.box
  padding $base * 2            // 8px
  margin ($base * 3) ($base)   // 12px 4px
  width 100% - 20px            // 混合单位运算
  font-size 14px + 2           // 16px（自动添加 px）
  line-height 24px / 2 + 1     // 13px
```

**运算符优先级：** 使用括号控制运算顺序。

```stylus
width (100px + 50px) / 2       // 75px
width 100px + 50px / 2         // 125px（除法优先）
```

**颜色运算：**

```stylus
$color = #4488cc

.light
  background $color + #222    // 通道相加 → #66aacc
.dark
  background $color - #111    // 通道相减 → #3377bb
```

**`calc()` 共存：** Stylus 在 `calc()` 内会自动计算变量值，其余部分保持不变。

```stylus
$sidebar-width = 200px

.main
  width calc(100% - $sidebar-width)  // calc(100% - 200px)
```

**评分标准：**
- 写出基本运算示例（40%）
- 理解单位和运算符优先级（30%）
- 知道 `calc()` 的变量替换行为（30%）

---

### Q10：Stylus 中如何使用内置函数？列举常用的颜色处理函数

**难度：** 初级

**考察知识点：** 内置函数 | **能力等级：** 初级

**参考答案：**

Stylus 内置了丰富的函数，涵盖颜色处理、数学运算、字符串操作、类型判断等。

**常用颜色函数：**

```stylus
$primary = #1890ff

// 颜色调整
lighten($primary, 20%)      // 变亮 20%
darken($primary, 20%)       // 变暗 20%
saturate($primary, 50%)     // 增加饱和度
desaturate($primary, 50%)   // 降低饱和度
fade($primary, 50%)         // 设置透明度（0-100%）
fade-in($primary, 0.1)      // 减少透明度（0-1）
fade-out($primary, 0.1)     // 增加透明度（0-1）
spin($primary, 30deg)       // 色相旋转 30 度
mix($primary, #ff0000, 50%) // 混合两个颜色

// 颜色通道提取
red($primary)               // 红色通道值
green($primary)             // 绿色通道值
blue($primary)              // 蓝色通道值
alpha($primary)             // 透明度
hue($primary)               // 色相
saturation($primary)        // 饱和度
lightness($primary)         // 亮度

// 颜色创建
rgb(24, 144, 255)           // RGB → #1890ff
rgba(24, 144, 255, 0.5)     // RGBA
hsl(210, 100%, 55%)         // HSL
hsla(210, 100%, 55%, 0.5)   // HSLA
```

**实际应用——交互状态色值体系：**

```stylus
$primary = #1890ff

.btn-primary
  background $primary
  &:hover
    background lighten($primary, 8%)
  &:active
    background darken($primary, 8%)
  &:disabled
    background fade($primary, 40%)
    cursor not-allowed
  border-color darken($primary, 10%)
```

**数学函数：**

```stylus
ceil(2.4)       // 3
floor(2.6)      // 2
round(2.5)      // 3
abs(-5px)       // 5px
min(10, 20, 5)  // 5
max(10, 20, 5)  // 20
unit(10px)      // 'px'
unit(10px, '')  // 10（移除单位）
```

**评分标准：**
- 列举至少 5 个颜色函数（40%）
- 写出交互状态色值应用（30%）
- 了解常用的数学函数（30%）

---

## 三、中级题目（10 道）

---

### Q11：Stylus 的条件语句 `if/else` 如何使用？与 SCSS/LESS 有何区别？

**难度：** 中级

**考察知识点：** 条件判断 | **能力等级：** 中级

**参考答案：**

Stylus 内置了 `if/else if/else` 条件语句，语法接近 JavaScript，比 SCSS 的 `@if` 和 LESS 的 `when()` Guard 更直观。

```stylus
// 基础 if/else
$theme = 'dark'

body
  if $theme == 'dark'
    background #222
    color #eee
  else
    background #fff
    color #333
```

```stylus
// 多条件分支
$size = 'large'

.btn
  if $size == 'small'
    padding 4px 8px
    font-size 12px
  else if $size == 'medium'
    padding 6px 12px
    font-size 14px
  else if $size == 'large'
    padding 10px 20px
    font-size 16px
  else
    padding 8px 16px
    font-size 14px
```

```stylus
// 结合颜色函数判断
$bg-color = #f5f5f5

.text
  if lightness($bg-color) > 50%
    color #333           // 浅色背景用深色文字
  else
    color #fff           // 深色背景用浅色文字
```

```stylus
// 条件判断在 Mixin 中的应用
set-text-color($bg)
  if lightness($bg) >= 50%
    color #333
  else
    color #fff

.card
  set-text-color(#f5f5f5)    // 浅色背景 → color: #333
.dark-card
  set-text-color(#333)       // 深色背景 → color: #fff
```

**与 SCSS/LESS 的对比：**

| 维度 | Stylus | SCSS | LESS |
|------|--------|------|------|
| 语法 | `if ... else` | `@if ... @else` | `when()` Guard |
| 可读性 | 与 JS 一致，最直观 | 类似编程语言 | 相对隐晦 |
| 嵌套复杂度 | 支持完全嵌套 | 支持完全嵌套 | 受 Guard 限制 |
| 学习成本 | 最低 | 中等 | 较高 |

**评分标准：**
- 写出 `if/else` 基本语法（30%）
- 写出结合颜色函数的实际应用（40%）
- 与 SCSS/LESS 对比清晰（30%）

---

### Q12：Stylus 的 `for/in` 和 `for/range` 循环如何使用？

**难度：** 中级

**考察知识点：** 循环控制 | **能力等级：** 中级

**参考答案：**

Stylus 提供两种原生循环语法，无需像 LESS 那样用递归模拟。

**`for/range`：数值范围循环**

```stylus
// 生成栅格系统
for $i in 1..12
  .col-{$i}
    width ($i / 12 * 100)%

// 编译为：
// .col-1 { width: 8.333333333333334%; }
// .col-2 { width: 16.666666666666668%; }
// ... .col-12 { width: 100%; }
```

```stylus
// 1..10 与 1...10 的区别
// 1..10  → 包含 10（闭区间）
// 1...10 → 不包含 10（左闭右开）
```

**`for/in`：遍历列表/数组**

```stylus
// 遍历颜色列表
$colors = red green blue orange purple

for $color, $i in $colors
  .text-{$color}
    color $color
  .bg-{$color}
    background $color

// 编译为：
// .text-red { color: red; }
// .bg-red { background: red; }
// .text-green { color: green; }
// .bg-green { background: green; }
// ...
```

```stylus
// 遍历键值对（Hash/Map）
$sizes = {
  sm: 12px,
  md: 14px,
  lg: 16px,
  xl: 20px
}

for $name, $size in $sizes
  .text-{$name}
    font-size $size
```

```stylus
// 实际应用：生成间距工具类
$spacing-values = 0 4 8 12 16 20 24 32 40 48

for $value in $spacing-values
  .m-{$value}
    margin $value * 1px
  .mt-{$value}
    margin-top $value * 1px
  .p-{$value}
    padding $value * 1px
  .pt-{$value}
    padding-top $value * 1px
```

**与 SCSS/LESS 的对比：**

| 维度 | Stylus | SCSS | LESS |
|------|--------|------|------|
| 循环语法 | `for/in`、`for/range` | `@for`、`@each`、`@while` | 递归混合 |
| 表达能力 | 强，原生语法 | 强，三种循环 | 弱，需模拟 |
| 代码可读性 | 高 | 高 | 低 |

**评分标准：**
- 写出 `for/range` 用法（30%）
- 写出 `for/in` 遍历列表和 Hash（40%）
- 理解 `..` 与 `...` 的区别（30%）

---

### Q13：Stylus 中如何定义和使用自定义函数？与 Mixin 有什么区别？

**难度：** 中级

**考察知识点：** 自定义函数 | **能力等级：** 中级

**参考答案：**

Stylus 支持自定义函数，语法类似 JavaScript 函数，有明确的 `return` 语句。

```stylus
// 定义函数
add($a, $b)
  return $a + $b

sum($numbers...)
  $total = 0
  for $num in $numbers
    $total = $total + $num
  return $total

// 调用函数
.width
  width add(100px, 50px)    // 150px
  height sum(10px, 20px, 30px)  // 60px
```

**实际应用：**

```stylus
// 计算对比度并返回合适的文字颜色
contrast-color($bg)
  if lightness($bg) >= 50%
    return #333
  else
    return #fff

// 生成响应式断点
em($px, $base = 16px)
  return ($px / $base) * 1em

// 使用
.card
  background #1890ff
  color contrast-color(#1890ff)   // 自动判断返回 #fff
  max-width em(600px)              // 37.5em
```

**函数与 Mixin 的区别：**

| 维度 | 函数 | Mixin |
|------|------|-------|
| 返回值 | 返回一个值，用于赋值 | 返回一组 CSS 属性 |
| 使用方式 | 作为值使用 | 作为 CSS 规则块 |
| `return` | 有 | 没有 |
| 适用场景 | 计算、转换、判断 | 样式封装、复用 |
| 示例 | `width func(100px)` | 直接 `func(100px)` 输出属性 |

```stylus
// 函数：返回计算值
px-to-rem($px, $base = 16px)
  return ($px / $base) * 1rem

// 混合：输出一组 CSS
center-block($width)
  width $width
  margin-left auto
  margin-right auto

.container
  // 函数用于赋值
  font-size px-to-rem(14px)     // 作为值
  // 混合输出属性
  center-block(960px)            // 输出 CSS 块
```

**评分标准：**
- 写出自定义函数定义与调用（40%）
- 明确区分函数与 Mixin 的差异（40%）
- 有实际应用场景（20%）

---

### Q14：Stylus 中的 `@` 属性查找是如何工作的？有哪些应用场景？

**难度：** 中级

**考察知识点：** 属性查找 | **能力等级：** 中级

**参考答案：**

属性查找（Property Lookup）是 Stylus 的特有机制，使用 `@` 前缀引用当前选择器已定义的属性值。

```stylus
.box
  color #333
  background @color                    // 引用 color → #333
  border-color darken(@color, 20%)     // 基于 color 计算
  text-shadow 1px 1px 0 @background    // 引用 background
```

**向上查找：** `@` 可以查找父级选择器的属性。

```stylus
.block
  color #333
  .element
    color @color         // 查找 .block 的 color → #333
  .child
    background @color    // 同样查找 .block 的 color
```

**多个 `@` 前缀：** 多个 `@` 表示向上多级查找。

```stylus
.grand
  font-size 16px
  .parent
    font-size 14px
    .child
      font-size @@font-size       // 一个 @ 指 .parent 的 14px
      line-height @@@font-size    // 两个 @ 指 .grand 的 16px
```

**实际应用场景：**

```stylus
// 场景 1：基于主色自动生成变体
$primary = #1890ff

.btn
  background $primary
  border-color darken(@background, 10%)
  &:hover
    background lighten(@background, 8%)
  &:active
    background darken(@background, 8%)
  // 所有变体都基于统一的 background 属性计算

// 场景 2：居中对齐辅助
center($width)
  width $width
  margin-left "calc(50% - %s / 2)" % @width
  // 或者：margin-left (50% - @width / 2)
```

**评分标准：**
- 解释属性查找的基本用法（40%）
- 理解多级 `@` 查找（30%）
- 写出实际应用场景（30%）

---

### Q15：Stylus 的 `@keyframes` 和 `@media` 如何在嵌套中工作？

**难度：** 中级

**考察知识点：** 嵌套中的 @规则 | **能力等级：** 中级

**参考答案：**

Stylus 支持在嵌套中书写 `@media` 和 `@keyframes`，编译时会自动提升到顶层（冒泡）。

```stylus
// @media 嵌套
.component
  width 100%

  @media (min-width: 768px)
    width 50%

  @media (min-width: 1024px)
    width 33.33%

// 编译为：
// .component { width: 100%; }
// @media (min-width: 768px) { .component { width: 50%; } }
// @media (min-width: 1024px) { .component { width: 33.33%; } }
```

```stylus
// @keyframes 嵌套
.loading
  animation spin 1s linear infinite

  @keyframes spin
    from
      transform rotate(0deg)
    to
      transform rotate(360deg)

// 编译为：
// .loading { animation: spin 1s linear infinite; }
// @keyframes spin {
//   from { transform: rotate(0deg); }
//   to { transform: rotate(360deg); }
// }
```

```stylus
// 使用变量生成 @keyframes
$animation-name = 'fadeIn'

.element
  animation {$animation-name} .3s ease

  @keyframes {$animation-name}
    from
      opacity 0
      transform translateY(-10px)
    to
      opacity 1
      transform translateY(0)
```

```stylus
// 响应式设计综合示例
.sidebar
  width 300px
  float left

  @media (max-width: 768px)
    width 100%
    float none

  @media (min-width: 769px) and (max-width: 1024px)
    width 250px
```

**评分标准：**
- 理解 `@media` 嵌套的编译行为（40%）
- 理解 `@keyframes` 嵌套（30%）
- 能结合插值动态生成动画（30%）

---

### Q16：Stylus 中如何使用 Hash（映射/字典）数据结构？

**难度：** 中级

**考察知识点：** Hash 数据结构 | **能力等级：** 中级

**参考答案：**

Stylus 支持 Hash（类似 JavaScript 对象）作为数据结构，可用于存储键值对，结合循环遍历实现强大的配置驱动样式。

```stylus
// 定义 Hash
$colors = {
  primary: #1890ff,
  success: #52c41a,
  warning: #faad14,
  danger: #f5222d,
  info: #13c2c2
}

// 遍历 Hash 生成类
for $name, $color in $colors
  .btn-{$name}
    background $color
    &:hover
      background lighten($color, 10%)
    &:active
      background darken($color, 10%)
```

```stylus
// 配置驱动的响应式断点
$breakpoints = {
  sm: 576px,
  md: 768px,
  lg: 992px,
  xl: 1200px,
  xxl: 1400px
}

for $name, $width in $breakpoints
  @media (min-width: $width)
    .container
      max-width $width

// 编译为：
// @media (min-width: 576px) { .container { max-width: 576px; } }
// @media (min-width: 768px) { .container { max-width: 768px; } }
// ...
```

```stylus
// 复杂配置——设计令牌系统
$theme = {
  colors: {
    primary: #1890ff,
    text: #333,
    bg: #fff
  },
  fonts: {
    base: 14px,
    heading: 24px
  },
  spacing: {
    xs: 4px,
    sm: 8px,
    md: 16px,
    lg: 24px
  }
}

// 访问 Hash 值
$primary-color = $theme.colors.primary
$font-base = $theme.fonts.base

// 遍历生成间距工具类
for $name, $value in $theme.spacing
  .m-{$name}
    margin $value
  .p-{$name}
    padding $value
```

**评分标准：**
- 写出 Hash 定义和遍历（40%）
- 展示配置驱动样式的应用（30%）
- 理解嵌套 Hash 的访问方式（30%）

---

### Q17：Stylus 中如何使用内置函数进行图像处理？

**难度：** 中级

**考察知识点：** 图像处理函数 | **能力等级：** 中级

**参考答案：**

Stylus 提供了一组独特的图像处理函数，可在编译时读取图像的尺寸信息，这在 SCSS 和 LESS 中是不具备的。

```stylus
// 获取图像尺寸
.logo
  width image-size('logo.png')[0]    // 图像宽度
  height image-size('logo.png')[1]   // 图像高度
  background url('logo.png')
```

```stylus
// 实际应用：内联图像（转为 Base64）
.small-icon
  background url('data:image/png;base64,' + base64-encode('icon.png'))
  // 或使用 embedurl 函数
  background embedurl('icon.png', 'png')
```

**常用图像函数：**

```stylus
// image-size(path) — 返回 [width, height]
$size = image-size('bg.png')
$bg-width = $size[0]
$bg-height = $size[1]

// base64-encode(path) — 将文件转为 Base64
$encoded = base64-encode('font.woff')

// embedurl(path, [mimeType]) — 内联资源
.icon
  background embedurl('icon.png')    // 自动转 Base64 内联
```

**实际应用场景：**

```stylus
// 场景：精灵图自动化
$sprite-width = image-size('sprite.png')[0]
$sprite-height = image-size('sprite.png')[1]

.sprite
  background url('sprite.png')
  width ($sprite-width / 5)     // 假设 5 列
  height $sprite-height

// 场景：图标按钮自适应
.icon-btn($icon)
  background embedurl($icon) no-repeat center
  background-size contain
  width image-size($icon)[0]
  height image-size($icon)[1]

.btn-search
  .icon-btn('search-icon.png')
```

**注意事项：** 图像处理函数在编译时执行，需要文件系统访问权限，在浏览器端编译模式下不可用。

**评分标准：**
- 了解 `image-size()` 的用法（40%）
- 了解 `embedurl()` 和 Base64 编码（30%）
- 能写出实际应用场景（30%）

---

### Q18：Stylus 中 `@css` 的作用是什么？什么场景下使用？

**难度：** 中级

**考察知识点：** @css 指令 | **能力等级：** 中级

**参考答案：**

`@css` 指令用于在 Stylus 中直接输出纯 CSS 代码，不经过 Stylus 编译器处理。它告诉编译器「这段内容已经是 CSS，直接输出即可」。

```stylus
// 使用 @css 输出特殊 CSS（如 CSS 自定义属性）
@css {
  :root {
    --primary-color: #1890ff;
    --font-size: 14px;
    --spacing: 8px;
  }
}

// 编译为：
// :root {
//   --primary-color: #1890ff;
//   --font-size: 14px;
//   --spacing: 8px;
// }
```

**与 `@block` 的区别：**

- `@css`：完全忽略 Stylus 处理，内容原样输出
- `@block`：内容作为 Stylus 代码块，可在其中使用变量和函数

```stylus
// @css 中变量不会被解析
$color = red

@css {
  .box {
    color: $color;   // 输出原样：color: $color;
  }
}

// 使用字符串拼接实现类似效果
.box
  {color}: $color    // 正确：输出 color: red;
```

**实际应用场景：**

```stylus
// 场景 1：CSS 自定义属性（CSS Variables）
@css {
  :root {
    --header-height: 60px;
    --sidebar-width: 240px;
  }
}

.main
  margin-left var(--sidebar-width)
  padding-top var(--header-height)
```

```stylus
// 场景 2：第三方 CSS 片段直接嵌入
@css {
  @font-face {
    font-family: 'MyFont';
    src: url('myfont.woff2') format('woff2');
    font-display: swap;
  }
}
```

```stylus
// 场景 3：CSS Grid 复杂布局
@css {
  .grid-container {
    display: grid;
    grid-template-areas:
      "header header header"
      "sidebar main main"
      "footer footer footer";
  }
}
```

**评分标准：**
- 解释 `@css` 的作用（40%）
- 与 Stylus 正常语法的区别（30%）
- 列举实际应用场景（30%）

---

### Q19：Stylus 中 `@block` 和 `@extends` 有什么异同？

**难度：** 中级

**考察知识点：** @block 与 @extends | **能力等级：** 中级

**参考答案：**

**`@extend`：** 选择器级别的继承，合并选择器分组。

```stylus
.base
  color #333
  font-size 14px

.derived
  @extend .base
  font-weight bold

// 编译为：
// .base, .derived { color: #333; font-size: 14px; }
// .derived { font-weight: bold; }
```

**`@block`：** 代码块级别的复用，将一组 Stylus 规则作为块引用。

```stylus
// 定义代码块
$base-style = @block {
  color #333
  font-size 14px
  line-height 1.5
}

.article
  {$base-style}
  margin 20px

.comment
  {$base-style}
  border-left 3px solid #ddd

// 编译为（样式会复制到每个选择器）：
// .article { color: #333; font-size: 14px; line-height: 1.5; margin: 20px; }
// .comment { color: #333; font-size: 14px; line-height: 1.5; border-left: 3px solid #ddd; }
```

**对比：**

| 维度 | @extend | @block |
|------|---------|--------|
| CSS 输出 | 选择器分组，样式不重复 | 样式复制到每个使用处 |
| 最终体积 | 更紧凑 | 可能冗余 |
| 参数化 | 不支持 | 不支持（使用 Mixin 替代） |
| 动态逻辑 | 不支持 | 不支持（使用 Mixin 替代） |
| 适用场景 | 静态样式继承 | 跨文件样式块复用 |
| 在何处使用 | 选择器内 | 任意位置 |

```stylus
// 实际选择建议
// 使用 @extend 的情况：
.msg-base
  padding 10px
  border-radius 4px

.msg-error
  @extend .msg-base
  color red

// 使用 @block 的情况：
$clearfix = @block {
  &:after
    content ''
    display table
    clear both
}

.container
  {$clearfix}
  width 100%
```

**评分标准：**
- 解释 `@extend` 和 `@block` 各自的作用（40%）
- 理解 CSS 输出的差异（30%）
- 能给出选择建议（30%）

---

### Q20：Stylus 在 Node.js 中如何通过 API 进行编程式编译？

**难度：** 中级

**考察知识点：** Node.js API | **能力等级：** 中级

**参考答案：**

Stylus 提供 Node.js API，可在构建工具、自动化脚本中编程式调用。

```javascript
const stylus = require('stylus')
const fs = require('fs')

// 基础编译
const stylusStr = `
$color = #1890ff
body
  color $color
`

stylus.render(stylusStr, (err, css) => {
  if (err) throw err
  console.log(css)
  // 输出：body { color: #1890ff; }
})
```

```javascript
// 编译文件
stylus.render(fs.readFileSync('./styles/main.styl', 'utf8'), {
  filename: 'main.styl',     // 设置文件名（用于错误定位）
  compress: true,            // 压缩输出
  paths: ['./styles'],       // @import 搜索路径
  'include css': false       // 是否包含 .css 文件
}, (err, css) => {
  if (err) throw err
  fs.writeFileSync('./dist/main.css', css)
})
```

```javascript
// 使用中间件（插件）系统
const stylus = require('stylus')
const nib = require('nib')    // Stylus 官方扩展库
const rupture = require('rupture')  // 响应式断点库

stylus(str)
  .use(nib())              // 使用 nib 插件
  .use(rupture())          // 使用 rupture 插件
  .import('nib')           // 导入 nib
  .set('compress', true)   // 设置选项
  .define('version', '1.0') // 定义全局变量
  .render((err, css) => {
    console.log(css)
  })
```

```javascript
// 自定义函数
stylus(str)
  .define('add', (a, b) => a.operate('+', b))
  .define('double', (n) => n.operate('*', 2))
  .render((err, css) => {
    console.log(css)
  })
```

```javascript
// 与 Express 集成
const express = require('express')
const stylus = require('stylus')

app.use(stylus.middleware({
  src: __dirname + '/styles',
  dest: __dirname + '/public',
  compile: (str, path) => {
    return stylus(str)
      .set('filename', path)
      .set('compress', true)
      .use(nib())
  }
}))
```

**常用 API 方法：**

| 方法 | 说明 |
|------|------|
| `stylus.render(str, options, callback)` | 编译字符串 |
| `.use(fn)` | 使用中间件/插件 |
| `.set(key, value)` | 设置编译选项 |
| `.define(name, fn)` | 定义全局函数 |
| `.import(path)` | 导入文件 |
| `.include(path)` | 添加搜索路径 |

**评分标准：**
- 写出基础渲染 API（40%）
- 了解中间件系统（30%）
- 了解 Express 集成方式（30%）

---

## 四、高级题目（5 道）

---

### Q21：Stylus、SCSS、LESS 三者之间的核心差异是什么？如何进行技术选型？

**难度：** 高级

**考察知识点：** 预处理器对比选型 | **能力等级：** 高级

**参考答案：**

**核心差异对比：**

| 维度 | Stylus | SCSS | LESS |
|------|--------|------|------|
| 创建时间 | 2010 | 2006 | 2009 |
| 语言平台 | Node.js | Dart / Ruby / C++ | JavaScript |
| 变量符号 | `$` | `$` | `@` |
| 语法灵活性 | 极高（三种风格） | 标准 CSS 超集 | 标准 CSS 超集 |
| 混合定义 | 普通选择器（透明） | `@mixin` | `.mixin()` |
| 混合调用 | 直接写名称 | `@include` | `.mixin()` |
| 条件语句 | `if/else`（原生） | `@if/@else` | `when()` Guard |
| 循环语句 | `for/in`、`for/range` | `@for`、`@each`、`@while` | 递归混合 |
| 函数 | 自定义函数 + `return` | `@function` + `@return` | 混合模拟 |
| 属性嵌套 | 支持 | 不支持 | 不支持 |
| 图像处理 | 支持（编译时读尺寸） | 不支持 | 不支持 |
| 浏览器编译 | 支持 | 不支持 | 支持 |
| 社区生态 | 较小 | 最大 | 中等 |
| 典型用户 | 早期 Express 项目 | Bootstrap、Foundation | Ant Design |
| 学习曲线 | 低（语法自由） | 中等 | 低 |

**技术选型建议：**

```stylus
// 选择 Stylus 的场景：
// - 需要极致简洁的语法
// - 需要属性嵌套
// - 需要编译时图像处理
// - Node.js 技术栈团队
// - 个人项目或快速原型

// 选择 SCSS 的场景：
// - 使用 Bootstrap 等 SCSS 生态的框架
// - 团队习惯 CSS 标准语法
// - 需要最丰富的第三方库支持
// - 大型企业级项目

// 选择 LESS 的场景：
// - 使用 Ant Design 组件库
// - 需要浏览器端实时编译
// - 团队需要最低学习成本
// - 中小型项目
```

**评分标准：**
- 全面对比至少 6 个维度（40%）
- 每种预处理器的适用场景清晰（30%）
- 选型逻辑合理（30%）

---

### Q22：Stylus 的透明混合（Transparent Mixins）有什么优势和潜在问题？

**难度：** 高级

**考察知识点：** 透明混合深入 | **能力等级：** 高级

**参考答案：**

**透明混合的概念：** Stylus 中 Mixin 的定义就是普通选择器，调用时也不需特殊关键字。定义和调用的语法完全一致，编译器根据上下文区分。

```stylus
// 定义 —— 看起来像普通选择器
border-radius($radius)
  -webkit-border-radius $radius
  border-radius $radius

// 作为 Mixin 调用 —— 语法相同
.btn
  border-radius(4px)

// 作为普通选择器输出 —— 语法相同
border-radius(4px)
  display block

// 编译为：
// .btn { -webkit-border-radius: 4px; border-radius: 4px; }
// border-radius(4px) { display: block; }
```

**优势：**

1. **语法噪音最小**：无需 `@mixin`/`@include`（SCSS）或 `.()` 区分（LESS）
2. **学习成本低**：不需要额外记忆 Mixin 关键字
3. **代码简洁**：定义和使用都极简，提升开发效率

```stylus
// Stylus 透明混合
size($w, $h = $w)
  width $w
  height $h

.box
  size(100px, 200px)

// SCSS 对比
@mixin size($w, $h: $w) {
  width: $w;
  height: $h;
}
.box {
  @include size(100px, 200px);
}
```

**潜在问题：**

1. **命名冲突风险**：普通选择器和 Mixin 共用同一命名空间，可能产生意外覆盖

```stylus
// 问题示例
.button
  padding 10px

// 另一个文件中定义了同名 Mixin
.button($color)
  background $color
  border 1px solid darken($color, 10%)

// 调用时可能产生混淆
.btn
  button(#1890ff)  // 是调用 Mixin 还是覆盖选择器？
```

2. **代码可读性**：在大型项目中，无法一眼区分「这是 Mixin 调用」还是「这是一条 CSS 规则」

3. **编辑器支持**：部分编辑器的语法高亮和智能提示不如 SCSS 的 `@include` 明确

**最佳实践：**

```stylus
// 1. 使用明确的命名约定区分 Mixin
// Mixin 用动词前缀
border-radius($r) { ... }
center-block($w) { ... }
set-theme($name) { ... }

// 2. 使用 @block 或独立文件管理 Mixin
// mixins.styl
border-radius($r)
  border-radius $r

// 3. 在大型项目中考虑使用命名空间
#mixins
  .border-radius($r)
    border-radius $r

// 调用
.btn
  #mixins.border-radius(4px)
```

**评分标准：**
- 解释透明混合的概念（30%）
- 分析优势和问题（40%）
- 提出最佳实践（30%）

---

### Q23：如何设计一个基于 Stylus 的高可维护性主题系统？

**难度：** 高级

**考察知识点：** 架构设计 | **能力等级：** 高级

**参考答案：**

```stylus
// ===== 1. 设计令牌层（Design Tokens） =====
// tokens/colors.styl
$colors = {
  blue-5: #40a9ff,
  blue-6: #1890ff,
  blue-7: #096dd9,
  green-5: #73d13d,
  green-6: #52c41a,
  green-7: #389e0d,
  red-5: #ff7875,
  red-6: #f5222d,
  red-7: #cf1322,
  neutral-1: #fff,
  neutral-2: #fafafa,
  neutral-3: #f5f5f5,
  neutral-8: #595959,
  neutral-10: #262626
}

// tokens/semantic.styl
// 语义化令牌（引用基础色板）
$primary-color = $colors.blue-6
$primary-hover = $colors.blue-5
$primary-active = $colors.blue-7

$success-color = $colors.green-6
$error-color = $colors.red-6

$text-color = $colors.neutral-10
$text-secondary = $colors.neutral-8
$bg-color = $colors.neutral-1
$bg-secondary = $colors.neutral-2
$border-color = $colors.neutral-3

$border-radius = 4px
$font-size-base = 14px
$font-size-lg = 16px
$font-size-sm = 12px

// ===== 2. 混合层 =====
// mixins/button.styl
button-base()
  display inline-block
  padding 8px 16px
  border-radius $border-radius
  font-size $font-size-base
  cursor pointer
  transition all .3s
  border 1px solid transparent
  outline none
  line-height 1.5

button-variant($bg, $color, $border = $bg)
  background $bg
  color $color
  border-color $border
  &:hover
    background lighten($bg, 8%)
  &:active
    background darken($bg, 8%)
  &:disabled
    background fade($bg, 40%)
    cursor not-allowed

// mixins/form.styl
form-control()
  display block
  width 100%
  padding 8px 12px
  font-size $font-size-base
  border 1px solid $border-color
  border-radius $border-radius
  transition border-color .3s
  &:focus
    border-color $primary-color
    outline none
    box-shadow 0 0 0 2px fade($primary-color, 20%)

// ===== 3. 组件层 =====
// components/button.styl
.btn
  button-base()
  &-primary
    button-variant($primary-color, #fff)
  &-success
    button-variant($success-color, #fff)
  &-danger
    button-variant($error-color, #fff)
  &-default
    button-variant(#fff, $text-color, $border-color)
    &:hover
      color $primary-color
      border-color $primary-color

// ===== 4. 主题切换 =====
// themes/dark.styl
dark-theme()
  $primary-color = #177ddc
  $text-color = rgba(255, 255, 255, .85)
  $text-secondary = rgba(255, 255, 255, .65)
  $bg-color = #141414
  $bg-secondary = #1f1f1f
  $border-color = #434343

// 使用
body
  background $bg-color
  color $text-color

body.theme-dark
  dark-theme()
  background $bg-color
  color $text-color
```

**设计原则：**

1. **分层架构**：令牌层 → 混合层 → 组件层 → 主题层
2. **语义化命名**：避免直接使用颜色值，使用语义化变量
3. **单一职责**：每个文件只负责一类样式
4. **可覆盖性**：核心变量集中管理，主题切换只需覆盖变量

**文件组织：**

```
styles/
├── main.styl
├── tokens/
│   ├── colors.styl
│   ├── semantic.styl
│   └── typography.styl
├── mixins/
│   ├── layout.styl
│   ├── button.styl
│   └── form.styl
├── base/
│   ├── reset.styl
│   └── typography.styl
├── components/
│   ├── button.styl
│   ├── form.styl
│   └── modal.styl
└── themes/
    ├── dark.styl
    └── compact.styl
```

**评分标准：**
- 分层架构清晰（30%）
- 令牌设计合理（30%）
- 主题切换方案可行（40%）

---

### Q24：Stylus 在实际项目（如 Vue/Nuxt）中如何配置和使用？有哪些常见问题？

**难度：** 高级

**考察知识点：** 工程化配置 | **能力等级：** 高级

**参考答案：**

**Vue CLI 项目配置：**

```javascript
// vue.config.js
module.exports = {
  css: {
    loaderOptions: {
      stylus: {
        // 全局引入变量和混合文件
        import: [
          '~@/styles/tokens/colors.styl',
          '~@/styles/tokens/semantic.styl',
          '~@/styles/mixins/button.styl'
        ],
        // 或使用 use 配置
        use: [
          require('nib')()
        ]
      }
    }
  }
}
```

**在 .vue 文件中使用：**

```vue
<template>
  <div class="container">
    <button :class="btnClass">按钮</button>
  </div>
</template>

<style lang="stylus" scoped>
// 使用全局注入的变量
.container
  padding 20px
  background $bg-secondary

// 使用全局注入的混合
.btn
  button-base()
  button-variant($primary-color, #fff)

// 动态类名（插值）
$component = 'card'
.{$component}
  border-radius $border-radius
  box-shadow 0 2px 8px rgba(0, 0, 0, .1)
</style>
```

**Nuxt 项目配置：**

```javascript
// nuxt.config.js
export default {
  build: {
    loaders: {
      stylus: {
        import: [
          '~assets/styles/tokens.styl',
          '~assets/styles/mixins.styl'
        ]
      }
    }
  },
  styleResources: {
    stylus: [
      '~assets/styles/tokens.styl',
      '~assets/styles/mixins.styl'
    ]
  }
}
```

**Webpack 配置：**

```javascript
// webpack.config.js
module.exports = {
  module: {
    rules: [
      {
        test: /\.styl(us)?$/,
        use: [
          'vue-style-loader',
          'css-loader',
          {
            loader: 'stylus-loader',
            options: {
              import: [
                path.resolve(__dirname, 'src/styles/tokens.styl'),
                path.resolve(__dirname, 'src/styles/mixins.styl')
              ],
              use: [require('nib')()]
            }
          }
        ]
      }
    ]
  }
}
```

**常见问题与解决：**

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 变量未定义 | 未全局引入 | 在 `import` 选项中配置全局文件 |
| 编译报错 `out of memory` | 递归/循环过大 | 限制循环范围，使用 `@require` 替代 `@import` |
| webpack 中 `@import` 路径错误 | 路径解析问题 | 使用 `~` 前缀或配置 `paths` 选项 |
| 与 PostCSS 冲突 | 加载顺序 | 确保 `stylus-loader` 在 `postcss-loader` 之前 |
| 热更新不生效 | 缓存问题 | 检查 `cache-loader` 配置 |

**评分标准：**
- 写出 Vue/Nuxt 配置（40%）
- 理解全局变量注入机制（30%）
- 能解决常见问题（30%）

---

### Q25：Stylus 的编译原理是什么？请描述从 `.styl` 到 `.css` 的完整流程

**难度：** 高级

**考察知识点：** 编译原理 | **能力等级：** 高级

**参考答案：**

Stylus 的编译过程分为以下几个阶段：

```
.styl 文件
    ↓
[1. 词法分析 Lexer] → Token 流
    ↓
[2. 语法分析 Parser] → AST（抽象语法树）
    ↓
[3. 求值计算 Evaluator] → 求值后的 AST
    ↓
[4. 规范化 Normalizer] → 标准化 AST
    ↓
[5. 代码生成 Compiler] → CSS 字符串
    ↓
[6. 输出] → .css 文件
```

**各阶段详解：**

**1. 词法分析（Lexer）**

将源代码字符串转换为 Token 序列。Stylus 的 Lexer 需要处理三种语法风格的兼容。

```javascript
// 源码
$color = #1890ff
body
  color $color

// Token 流（简化表示）
// [IDENT($color), ASSIGN, HASH(#1890ff), NEWLINE,
//  IDENT(body), NEWLINE, INDENT,
//  IDENT(color), IDENT($color), NEWLINE, OUTDENT]
```

**2. 语法分析（Parser）**

将 Token 流转换为 AST。Stylus 的 Parser 需要处理缩进（通过 INDENT/OUTDENT token 推断层级）。

```
// AST（简化）
Root
  └── Assignment
        ├── name: $color
        └── value: #1890ff
  └── Selector: body
        └── Block
              └── Property: color
                    └── Value: $color (引用)
```

**3. 求值计算（Evaluator）**

遍历 AST 执行求值：
- 变量替换：`$color` → `#1890ff`
- 函数调用：`lighten(#1890ff, 10%)` → `#40a9ff`
- 运算：`100px + 50px` → `150px`
- Mixin 展开：将 Mixin 调用替换为具体 CSS 属性
- 循环展开：`for/in` 展开为多个选择器块
- 条件求值：`if/else` 根据条件选择分支

```javascript
// 求值后的 AST
Root
  └── Selector: body
        └── Block
              └── Property: color
                    └── Value: #1890ff  // 已替换
```

**4. 规范化（Normalizer）**

将求值后的 AST 标准化：
- 处理 `@extend`：合并选择器
- 处理属性嵌套：展开为完整的属性名
- 处理 `@media` 冒泡：将嵌套的媒体查询提升到顶层

```
// 属性嵌套展开
font: { size: 14px, weight: bold }
→ font-size: 14px; font-weight: bold
```

**5. 代码生成（Compiler）**

将 AST 转换为 CSS 字符串，处理缩进、空格、换行等格式。

**6. 增量编译与缓存**

```javascript
// Stylus 支持中间件系统，可在编译各阶段插入自定义逻辑
stylus(str)
  .use(function(style) {
    // style 是可操作的 AST 对象
    style.define('add', (a, b) => a.operate('+', b))
  })
  .render(callback)
```

**核心源码结构：**

```
stylus/
├── lib/
│   ├── lexer.js       # 词法分析器
│   ├── parser.js      # 语法分析器
│   ├── evaluator.js   # 求值器
│   ├── normalizer.js  # 规范化器
│   ├── compiler.js    # 代码生成器
│   ├── visitor.js     # AST 遍历器
│   ├── nodes/         # AST 节点定义
│   └── functions/     # 内置函数
└── bin/stylus         # CLI 入口
```

**与 SCSS/LESS 编译的差异：**

| 维度 | Stylus | SCSS | LESS |
|------|--------|------|------|
| 实现语言 | JavaScript | Dart / C++ | JavaScript |
| 运行环境 | Node.js / 浏览器 | Dart VM / Node.js | Node.js / 浏览器 |
| 速度 | 中等 | 快（Dart/C++ 实现） | 中等 |
| 中间件 | 丰富的中间件系统 | 自定义函数 | 插件系统 |

**评分标准：**
- 描述完整的编译流程（40%）
- 理解各阶段的作用（30%）
- 能对比 SCSS/LESS（30%）

---

## 附录：考点速查表

| 知识点 | 核心内容 | 难度范围 | 出现频率 |
|--------|---------|----------|---------|
| 语法风格 | 三种风格（CSS/缩进/极简） | 初级 | 高 |
| 变量 | `$` 变量、`@` 属性查找、作用域 | 初级-中级 | 高 |
| 嵌套 | 选择器嵌套、属性嵌套、`&` | 初级 | 高 |
| 透明混合 | 定义与调用、参数、与 SCSS/LESS 对比 | 初级-高级 | 高 |
| 继承 | `@extend`、占位符 `$`、`@block` | 初级-中级 | 中 |
| 条件与循环 | `if/else`、`for/in`、`for/range` | 中级 | 高 |
| 自定义函数 | `return`、与 Mixin 区别 | 中级 | 中 |
| 插值 | `{}` 语法 | 初级 | 中 |
| 运算 | 数值运算、颜色运算、`calc()` | 初级 | 中 |
| 内置函数 | 颜色、数学、图像处理 | 初级-中级 | 中 |
| 模块化 | `@import`、`@require` | 初级 | 中 |
| Hash | 键值对、配置驱动 | 中级 | 中 |
| 工程化 | Vue/Nuxt/Webpack 配置 | 高级 | 中 |
| 编译原理 | 词法→语法→求值→生成 | 高级 | 低 |
| 对比选型 | Stylus vs SCSS vs LESS | 高级 | 高 |

---

> **参考资源：** [Stylus 官方文档](https://stylus-lang.com/) | [Stylus GitHub](https://github.com/stylus/stylus) | 本文档适用于面试准备与日常开发参考。