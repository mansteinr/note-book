# Vue 组件作用域 CSS 实现原理深度解析

> 本文档系统阐述 Vue 组件作用域 CSS（Scoped CSS）的核心概念、实现机制、编译流程、深度选择器原理及最佳实践，帮助开发者深入理解组件样式隔离的底层逻辑。

---

## 目录

- [一、作用域 CSS 核心概念](#一作用域-css-核心概念)
  - [1.1 什么是作用域 CSS](#11-什么是作用域-css)
  - [1.2 为什么需要作用域 CSS](#12-为什么需要作用域-css)
  - [1.3 作用域 CSS 的基本使用](#13-作用域-css-的基本使用)
- [二、技术机制：属性选择器策略](#二技术机制属性选择器策略)
  - [2.1 核心原理：data-v-hash 属性](#21-核心原理data-v-hash-属性)
  - [2.2 属性选择器实现详解](#22-属性选择器实现详解)
  - [2.3 作用域 CSS 编译过程](#23-作用域-css-编译过程)
- [三、与全局 CSS 的区别与相互作用](#三与全局-css-的区别与相互作用)
  - [3.1 全局 CSS vs 作用域 CSS](#31-全局-css-vs-作用域-css)
  - [3.2 样式优先级与加载顺序](#32-样式优先级与加载顺序)
  - [3.3 混合使用的注意事项](#33-混合使用的注意事项)
- [四、深度选择器（:deep）的使用与原理](#四深度选择器deep的使用与原理)
  - [4.1 深度选择器的必要性](#41-深度选择器的必要性)
  - [4.2 Vue 2 深度选择器语法](#42-vue-2-深度选择器语法)
  - [4.3 Vue 3 深度选择器语法](#43-vue-3-深度选择器语法)
  - [4.4 深度选择器编译原理](#44-深度选择器编译原理)
  - [4.5 :global() 全局穿透](#45-global-全局穿透)
- [五、实际开发中的最佳实践](#五实际开发中的最佳实践)
  - [5.1 样式组织规范](#51-样式组织规范)
  - [5.2 常见问题与解决方案](#52-常见问题与解决方案)
  - [5.3 性能优化建议](#53-性能优化建议)
- [六、高级主题](#六高级主题)
  - [6.1 作用域 CSS 与 CSS Modules 对比](#61-作用域-css-与-css-modules-对比)
  - [6.2 作用域 CSS 与 CSS-in-JS 对比](#62-作用域-css-与-css-in-js-对比)
  - [6.3 自定义作用域策略](#63-自定义作用域策略)
- [七、面试题深度解析](#七面试题深度解析)
- [八、总结与速查表](#八总结与速查表)

---

## 一、作用域 CSS 核心概念

### 1.1 什么是作用域 CSS

**作用域 CSS（Scoped CSS）** 是 Vue.js 提供的一种样式隔离机制，它确保组件内的样式只作用于该组件的元素，而不会泄漏到其他组件或全局样式中。

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    作用域 CSS 概念图解                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  问题场景：                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  父组件样式: .title { color: red }                              │   │
│  │                                                                  │   │
│  │  子组件 A:                                                       │   │
│  │  <div class="title">标题A</div>  ← 被污染为红色                  │   │
│  │                                                                  │   │
│  │  子组件 B:                                                       │   │
│  │  <div class="title">标题B</div>  ← 也被污染为红色                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  作用域 CSS 解决方案：                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  父组件样式: .title[data-v-parent] { color: red }               │   │
│  │                                                                  │   │
│  │  子组件 A (data-v-child-a):                                     │   │
│  │  <div class="title" data-v-child-a>标题A</div>                  │   │
│  │  ↑ 只有父组件通过 :deep() 才能影响                               │   │
│  │                                                                  │   │
│  │  子组件 B (data-v-child-b):                                     │   │
│  │  <div class="title" data-v-child-b>标题B</div>                  │   │
│  │  ↑ 不受影响                                                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 为什么需要作用域 CSS

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    作用域 CSS 解决的核心问题                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  问题 1：样式污染                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  // ComponentA.vue                                              │   │
│  │  <style>                                                        │   │
│  │  .button { background: blue; }  /* 影响所有 .button */          │   │
│  │  </style>                                                       │   │
│  │                                                                  │   │
│  │  // ComponentB.vue（也使用 .button）                             │   │
│  │  <div class="button">点击</div>  /* 被错误地设为蓝色 */          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  问题 2：样式冲突                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  // 两个组件都定义了 .card 样式                                  │   │
│  │  // 后加载的组件会覆盖前者的样式                                  │   │
│  │  // 造成样式不可预测                                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  问题 3：组件复用性差                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  // 如果样式不是组件内部定义的                                   │   │
│  │  // 组件依赖外部样式，无法独立使用                                │   │
│  │  // 降低了组件的可移植性和复用性                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  作用域 CSS 的优势：                                                    │
│  ✅ 样式隔离：组件样式互不干扰                                          │
│  ✅ 即插即用：组件可以独立使用                                          │
│  ✅ 可维护性：样式与组件结构绑定                                        │
│  ✅ 可移植性：组件可以轻松迁移到其他项目                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.3 作用域 CSS 的基本使用

#### Vue 2 基本用法

```html
<!-- Vue 2 Scoped CSS -->
<template>
  <div class="container">
    <h1 class="title">组件标题</h1>
    <p class="content">这是组件内容</p>
  </div>
</template>

<script>
export default {
  name: 'MyComponent'
}
</script>

<!-- 使用 scoped 属性启用作用域 CSS -->
<style scoped>
/* 这些样式只会作用于当前组件 */
.container {
  padding: 20px;
  border: 1px solid #ccc;
}

.title {
  color: #333;
  font-size: 24px;
}

.content {
  line-height: 1.6;
  color: #666;
}
</style>
```

#### Vue 3 基本用法

```html
<!-- Vue 3 Scoped CSS -->
<template>
  <div class="container">
    <h1 class="title">组件标题</h1>
    <p class="content">这是组件内容</p>
  </div>
</template>

<script setup>
// 组件逻辑
</script>

<!-- Vue 3 同样使用 scoped 属性 -->
<style scoped>
.container {
  padding: 20px;
  border: 1px solid #ccc;
}

.title {
  color: #333;
  font-size: 24px;
}

.content {
  line-height: 1.6;
  color: #666;
}
</style>
```

#### 多个 style 块

```html
<template>
  <div class="wrapper">
    <div class="scoped-box">作用域样式</div>
    <div class="global-box">全局样式</div>
  </div>
</template>

<!-- 可以同时存在多个 style 块 -->
<style scoped>
/* 作用域样式：只影响当前组件 */
.scoped-box {
  background: lightblue;
  padding: 10px;
}
</style>

<style>
/* 全局样式：影响所有使用此 class 的元素 */
.global-box {
  background: lightgreen;
  padding: 10px;
}
</style>
```

---

## 二、技术机制：属性选择器策略

### 2.1 核心原理：data-v-hash 属性

Vue 通过给组件的根元素和所有子元素添加唯一的 `data-v-xxxx` 属性来实现样式隔离。

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    data-v-hash 属性机制                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  编译前：                                                               │
│  <template>                                                             │
│    <div class="container">                                              │
│      <h1 class="title">标题</h1>                                        │
│      <p class="content">内容</p>                                       │
│    </div>                                                               │
│  </template>                                                           │
│                                                                         │
│  <style scoped>                                                         │
│  .container { padding: 20px; }                                          │
│  .title { color: red; }                                                │
│  .content { font-size: 14px; }                                          │
│  </style>                                                               │
│                                                                         │
│  编译后：                                                               │
│  HTML 结构：                                                            │
│  <div class="container" data-v-7a3b9c1d>                               │
│    <h1 class="title" data-v-7a3b9c1d>标题</h1>                        │
│    <p class="content" data-v-7a3b9c1d>内容</p>                        │
│  </div>                                                                 │
│                                                                         │
│  CSS 样式：                                                             │
│  .container[data-v-7a3b9c1d] { padding: 20px; }                       │
│  .title[data-v-7a3b9c1d] { color: red; }                               │
│  .content[data-v-7a3b9c1d] { font-size: 14px; }                        │
│                                                                         │
│  关键说明：                                                             │
│  1. 每个组件有唯一的 hash 值（如 7a3b9c1d）                            │
│  2. 所有选择器被添加 [data-v-hash] 属性选择器                           │
│  3. 只有带有该属性的元素才会被样式影响                                  │
│  4. hash 值基于组件内容生成（稳定且唯一）                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 属性选择器实现详解

#### 属性选择器规则

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    属性选择器添加规则                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  规则 1：普通选择器                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  原选择器: .title                                                │   │
│  │  编译结果: .title[data-v-hash]                                  │   │
│  │                                                                  │   │
│  │  原选择器: div.title                                             │   │
│  │  编译结果: div.title[data-v-hash]                               │   │
│  │                                                                  │   │
│  │  原选择器: #app                                                  │   │
│  │  编译结果: #app[data-v-hash]                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  规则 2：后代选择器                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  原选择器: .container .title                                     │   │
│  │  编译结果: .container .title[data-v-hash]                       │   │
│  │                                                                  │   │
│  │  注意：属性选择器只添加到最后一个选择器上                          │   │
│  │  这意味着 .container 不需要有 data-v-hash 属性                  │   │
│  │  只要 .title 有就行                                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  规则 3：伪元素选择器                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  原选择器: .button:hover                                         │   │
│  │  编译结果: .button:hover[data-v-hash]                            │   │
│  │                                                                  │   │
│  │  原选择器: .item::before                                         │   │
│  │  编译结果: .item[data-v-hash]::before                            │   │
│  │                                                                  │   │
│  │  原选择器: .item::after                                          │   │
│  │  编译结果: .item[data-v-hash]::after                             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  规则 4：嵌套选择器（预处理器）                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  原代码 (SCSS):                                                  │   │
│  │  .container {                                                    │   │
│  │    .title { color: red; }                                        │   │
│  │  }                                                               │   │
│  │                                                                  │   │
│  │  编译结果:                                                       │   │
│  │  .container .title[data-v-hash] { color: red; }                 │   │
│  │                                                                  │   │
│  │  注意：嵌套展开后，属性选择器只添加到最后一级                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 实际编译示例

**Vue 2 编译示例：**

```html
<!-- 源码 -->
<template>
  <div class="wrapper">
    <div class="box">
      <span class="label">文本</span>
    </div>
  </div>
</template>

<style scoped>
.wrapper {
  display: flex;
}

.wrapper .box {
  padding: 10px;
}

.wrapper .box .label {
  font-weight: bold;
}

.box:hover {
  background: #eee;
}
</style>
```

```css
/* 编译后的 CSS（Vue 2） */
.wrapper[data-v-1a2b3c] {
  display: flex;
}

.wrapper .box[data-v-1a2b3c] {
  padding: 10px;
}

.wrapper .box .label[data-v-1a2b3c] {
  font-weight: bold;
}

.box:hover[data-v-1a2b3c] {
  background: #eee;
}
```

```html
<!-- 编译后的 HTML -->
<div class="wrapper" data-v-1a2b3c>
  <div class="box" data-v-1a2b3c>
    <span class="label" data-v-1a2b3c>文本</span>
  </div>
</div>
```

**Vue 3 编译示例：**

```html
<!-- 源码 -->
<template>
  <div class="container">
    <div class="card">
      <h3 class="title">标题</h3>
      <p class="desc">描述</p>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 1200px;
}

.container .card {
  border: 1px solid #ddd;
}

.container .card .title {
  font-size: 18px;
}

.container .card .desc {
  color: #666;
}
</style>
```

```css
/* 编译后的 CSS（Vue 3） */
.container[data-v-x9y8z7w] {
  max-width: 1200px;
}

.container .card[data-v-x9y8z7w] {
  border: 1px solid #ddd;
}

.container .card .title[data-v-x9y8z7w] {
  font-size: 18px;
}

.container .card .desc[data-v-x9y8z7w] {
  color: #666;
}
```

### 2.3 作用域 CSS 编译过程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    作用域 CSS 编译流程图                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  步骤 1：SFC 解析                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  .vue 文件 → vue-loader/@vue/compiler-sfc                       │   │
│  │  解析出 <template>、<script>、<style> 三部分                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  步骤 2：Hash 生成                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  根据组件内容生成唯一 hash 值                                    │   │
│  │  示例: 7a3b9c1d                                                 │   │
│  │  用于 data-v-7a3b9c1d 属性名                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  步骤 3：模板处理                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  为模板中的所有元素添加 data-v-hash 属性                         │   │
│  │  生成对应的 render 函数                                         │   │
│  │  render() { return _c('div', { attrs: {'data-v-7a3b9c1d': ''} }) }│   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  步骤 4：CSS 处理                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  使用 PostCSS 处理 style 内容                                    │   │
│  │  postcss-plugin-scoped 添加属性选择器                            │   │
│  │  .title → .title[data-v-7a3b9c1d]                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  步骤 5：代码生成                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  生成 JavaScript 模块代码                                        │   │
│  │  包含：render 函数、样式字符串、组件选项                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  步骤 6：打包输出                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Vite/Webpack 将组件打包到产物中                                  │   │
│  │  CSS 可以被抽离为独立文件或内联                                   │   │
│  │  运行时：通过 JS 动态注入 <style> 标签                           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### PostCSS 处理流程

```javascript
// vue-loader/@vue/compiler-sfc 内部的 PostCSS 处理伪代码
const postcss = require('postcss')
const scopedPlugin = require('postcss-scoped-css')

async function processScopedCSS(css, hash) {
  const result = await postcss([
    // 自定义插件：添加 data-v-hash 属性选择器
    {
      postcssPlugin: 'scope-css',
      Once(root) {
        root.walkRules(rule => {
          // 处理每个规则
          const selector = rule.selector
          const newSelector = addScopeToSelector(selector, hash)
          rule.selector = newSelector
        })
        
        // 处理 @keyframes 等特殊规则
        root.walkAtRules('keyframes', atRule => {
          // keyframes 不需要添加属性选择器
          // 但使用 keyframes 的选择器需要
        })
      }
    }
  ]).process(css)
  
  return result.css
}

function addScopeToSelector(selector, hash) {
  // 处理复合选择器
  return selector.split(',').map(part => {
    // 处理每个选择器部分
    return processSelectorPart(part.trim(), hash)
  }).join(', ')
}

function processSelectorPart(selector, hash) {
  // 处理伪元素/伪类
  const pseudoMatch = selector.match(/^(.+?)(::?[\w-]+)$/)
  
  if (pseudoMatch) {
    // 伪元素/伪类：data-v-hash 在伪元素之前
    return `${pseudoMatch[1]}[data-v-${hash}]${pseudoMatch[2]}`
  }
  
  // 普通选择器
  return `${selector}[data-v-${hash}]`
}
```

---

## 三、与全局 CSS 的区别与相互作用

### 3.1 全局 CSS vs 作用域 CSS

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    全局 CSS vs 作用域 CSS 对比                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  全局 CSS                                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  定义位置：                                                      │   │
│  │  - 项目级 CSS 文件（main.css、global.css）                     │   │
│  │  - 无 scoped 属性的 <style> 标签                                │   │
│  │                                                                  │   │
│  │  作用范围：                                                      │   │
│  │  - 影响所有页面和组件                                            │   │
│  │  - 需要严格管理以避免样式冲突                                    │   │
│  │                                                                  │   │
│  │  典型用途：                                                      │   │
│  │  - Reset/Normalize 样式                                          │   │
│  │  - 全局字体、颜色变量                                            │   │
│  │  - 第三方组件库样式覆盖                                          │   │
│  │  - 公共工具类（.text-center、.hidden）                          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  作用域 CSS                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  定义位置：                                                      │   │
│  │  - .vue 文件中带 scoped 属性的 <style> 标签                     │   │
│  │                                                                  │   │
│  │  作用范围：                                                      │   │
│  │  - 只影响当前组件及其子组件的根元素                               │   │
│  │  - 自动添加 data-v-hash 属性实现隔离                             │   │
│  │                                                                  │   │
│  │  典型用途：                                                      │   │
│  │  - 组件专属样式                                                  │   │
│  │  - 组件内部布局                                                  │   │
│  │  - 组件主题定制                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 样式优先级与加载顺序

#### CSS 优先级规则

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CSS 优先级与加载顺序                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  优先级从高到低：                                                       │
│  1. !important 声明                                                    │
│  2. 内联样式（style 属性）                                             │
│  3. ID 选择器 (#id)                                                    │
│  4. 类/伪类/属性选择器 (.class, :pseudo, [attr])                      │
│  5. 元素/伪元素选择器 (element, ::pseudo)                             │
│                                                                         │
│  同优先级时：后加载的样式生效                                           │
│                                                                         │
│  作用域 CSS 与全局 CSS 的优先级关系：                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  // 全局样式（main.css）                                        │   │
│  .title { color: blue; }                                            │   │
│  // 编译后：.title { color: blue; }                                │   │
│  │                                                                  │   │
│  │  // 组件作用域样式                                               │   │
│  │  .title { color: red; }  /* 写在 <style scoped> */                │   │
│  │  // 编译后：.title[data-v-hash] { color: red; }                 │   │
│  │                                                                  │   │
│  │  由于属性选择器 [data-v-hash] 的优先级与类选择器相同             │   │
│  │  如果作用域 CSS 后加载，则 .title 显示红色                       │   │
│  │  如果全局 CSS 后加载，则 .title 显示蓝色                         │   │
│  │                                                                  │   │
│  │  影响因素：                                                      │   │
│  │  1. CSS 文件的加载顺序                                           │   │
│  │  2. <style> 标签在文档中的位置                                   │   │
│  │  3. 组件的加载时机                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  实际建议：                                                             │
│  - 全局样式尽早加载（在 head 中）                                       │
│  - 组件样式按需加载                                                   │
│  - 使用 :deep() 或 !important 明确穿透                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 样式加载顺序示例

```javascript
// Vue 3 main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// 全局样式最先导入
import './styles/global.css'  // Reset、变量、公共类

// 创建应用
const app = createApp(App)
app.use(router)
app.use(store)
app.mount('#app')
```

```html
<!-- 组件中同时使用全局和作用域样式 -->
<template>
  <div class="page-container">
    <!-- 全局样式生效 -->
    <h1 class="text-center text-primary">页面标题</h1>
    
    <!-- 作用域样式生效 -->
    <div class="custom-section">
      <p class="section-title">自定义区块</p>
    </div>
  </div>
</template>

<!-- 作用域样式 -->
<style scoped>
.custom-section {
  margin: 20px 0;
  padding: 15px;
  background: #f5f5f5;
}

.section-title {
  font-size: 16px;
  color: #333;
}
</style>

<!-- 全局样式（此文件内的全局样式） -->
<style>
/* 这个样式是全局的，会影响所有组件 */
.text-center {
  text-align: center;
}

.text-primary {
  color: #409eff;
}
</style>
```

### 3.3 混合使用的注意事项

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    混合使用全局和作用域 CSS 的注意事项                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  注意 1：选择器冲突                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  问题：                                                          │   │
│  │  /* global.css */                                                │   │
│  .button { background: red; }                                       │   │
│  │                                                                  │   │
│  │  /* MyComponent.vue */                                           │   │
│  │  <style scoped>                                                  │   │
│  │  .button { background: blue; }  /* 可能被全局覆盖 */             │   │
│  │  </style>                                                        │   │
│  │                                                                  │   │
│  │  解决：                                                          │   │
│  │  1. 使用更具体的选择器                                           │   │
│  │  2. 使用 :deep() 显式穿透                                        │   │
│  │  3. 调整加载顺序                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  注意 2：子组件样式穿透                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  问题：父组件的作用域样式无法影响子组件                           │   │
│  │                                                                  │   │
│  │  /* Parent.vue */                                                │   │
│  │  <template>                                                      │   │
│  │    <ChildComponent />                                            │   │
│  │  </template>                                                     │   │
│  │                                                                  │   │
│  │  <style scoped>                                                  │   │
│  │  /* 无法影响 ChildComponent 内部的元素 */                        │   │
│  │  .child-title { color: red; }  /* 不生效 */                      │   │
│  │  </style>                                                        │   │
│  │                                                                  │   │
│  │  解决：                                                          │   │
│  │  1. 使用 :deep() 深度选择器                                      │   │
│  │  2. 在子组件中暴露样式接口（CSS Variables）                      │   │
│  │  3. 使用子组件的 props 控制样式                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  注意 3：CSS 变量的使用                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  CSS 变量可以穿透作用域边界！                                    │   │
│  │                                                                  │   │
│  │  /* 父组件 */                                                    │   │
│  │  <template>                                                      │   │
│  │    <div style="--theme-color: red">                              │   │
│  │      <ChildComponent />                                          │   │
│  │    </div>                                                        │   │
│  │  </template>                                                     │   │
│  │                                                                  │   │
│  │  /* 子组件 */                                                    │   │
│  │  <style scoped>                                                  │   │
│  │  .child-element {                                                │   │
│  │    color: var(--theme-color);  /* 可以获取到父组件的变量 */      │   │
│  │  }                                                               │   │
│  │  </style>                                                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 四、深度选择器（:deep）的使用与原理

### 4.1 深度选择器的必要性

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    深度选择器解决的问题                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  场景：父组件需要修改子组件内部的样式                                     │
│                                                                         │
│  App.vue (父组件):                                                      │
│  <template>                                                             │
│    <div class="app">                                                    │
│      <el-button>按钮</el-button>  ← 第三方组件                        │
│    </div>                                                               │
│  </template>                                                           │
│                                                                         │
│  <style scoped>                                                         │
│  /* 需求：修改 el-button 内部的文字颜色 */                              │
│                                                                         │
│  /* 方式 1：不使用 deep —— 不生效！ */                                  │
│  .el-button span { color: red; }  /* 编译后：                        │
│                                       .el-button span[data-v-hash]   │
│                                       子组件内部的 span 没有 data-v-hash │
│                                       选择器不匹配 */                  │
│                                                                         │
│  /* 方式 2：使用 :deep —— 生效！ */                                     │
│  :deep(.el-button span) { color: red; }  /* 编译后：                │
│                                             .el-button span           │
│                                             (无 data-v-hash 属性选择器) │
│                                             匹配子组件内部的元素 */      │
│  </style>                                                               │
│                                                                         │
│  核心原理：                                                             │
│  普通 scoped 选择器 → 添加 data-v-hash 属性选择器                        │
│  → 只能匹配带有该属性的元素                                             │
│  → 子组件内部的元素没有父组件的 data-v-hash 属性                        │
│  → 所以无法匹配                                                         │
│                                                                         │
│  :deep() 选择器 → 不添加 data-v-hash 属性选择器                         │
│  → 可以匹配子组件内部的元素                                             │
│  → 但仍受父组件作用域约束（只能影响父组件包含的子组件）                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Vue 2 深度选择器语法

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vue 2 深度选择器语法                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  语法 1：>>>  （Sass/Less 支持不佳，不推荐）                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  <style scoped lang="less">                                      │   │
│  │  .wrapper >>> .child-element {                                    │   │
│  │    color: red;                                                    │   │
│  │  }                                                               │   │
│  │  </style>                                                        │   │
│  │                                                                  │   │
│  │  编译结果：.wrapper .child-element { color: red; }               │   │
│  │  注意：>>> 不能在 Sass 中使用                                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  语法 2：/deep/  （推荐，通用）                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  <style scoped lang="scss">                                      │   │
│  │  .wrapper /deep/ .child-element {                                │   │
│  │    color: red;                                                    │   │
│  │  }                                                               │   │
│  │  </style>                                                        │   │
│  │                                                                  │   │
│  │  编译结果：.wrapper .child-element { color: red; }               │   │
│  │  注意：适用于所有预处理器                                          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  语法 3：::v-deep  （推荐，Vue 官方推荐）                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  <style scoped lang="scss">                                      │   │
│  │  .wrapper ::v-deep .child-element {                              │   │
│  │    color: red;                                                    │   │
│  │  }                                                               │   │
│  │  </style>                                                        │   │
│  │                                                                  │   │
│  │  编译结果：.wrapper .child-element { color: red; }               │   │
│  │  注意：适用于所有场景，最稳定                                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  三种语法对比：                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  语法          │ Sass  │ Less │ CSS  │ 推荐度                   │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │  >>>          │ ❌    │ ✅   │ ✅   │ ⭐⭐                      │   │
│  │  /deep/       │ ✅    │ ✅   │ ✅   │ ⭐⭐⭐⭐                   │   │
│  │  ::v-deep     │ ✅    │ ✅   │ ✅   │ ⭐⭐⭐⭐⭐                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Vue 2 深度选择器示例

```html
<!-- 父组件 Parent.vue -->
<template>
  <div class="parent">
    <ChildComponent />
  </div>
</template>

<script>
import ChildComponent from './ChildComponent.vue'

export default {
  components: { ChildComponent }
}
</script>

<!-- Vue 2 深度选择器三种写法 -->
<style scoped lang="scss">
/* 写法 1：/deep/ */
.parent /deep/ .child-title {
  color: red;
}

/* 写法 2：::v-deep */
.parent ::v-deep .child-content {
  font-size: 16px;
}

/* 写法 3：>>> */
.parent >>> .child-button {
  padding: 10px 20px;
}
</style>
```

### 4.3 Vue 3 深度选择器语法

Vue 3 推荐使用 `:deep()` 伪类替代旧的深度选择器语法。

```html
<!-- Vue 3 Parent.vue -->
<template>
  <div class="parent">
    <ChildComponent />
  </div>
</template>

<script setup>
import ChildComponent from './ChildComponent.vue'
</script>

<!-- Vue 3 :deep() 用法 -->
<style scoped>
/* 基本用法 */
.parent :deep(.child-title) {
  color: red;
}

/* 嵌套场景 */
.parent {
  :deep(.child-content) {
    font-size: 16px;
  }
  
  :deep(.child-list) {
    li {
      padding: 10px;
      
      &:hover {
        background: #eee;
      }
    }
  }
}

/* 多个选择器 */
:deep(.child-title),
:deep(.child-content) {
  font-weight: bold;
}

/* 与普通选择器混合 */
.parent :deep(.child-item .child-text) {
  line-height: 1.5;
}
</style>
```

#### Vue 3 旧语法兼容

```html
<!-- Vue 3 也兼容旧语法 -->
<style scoped>
/* 这些语法在 Vue 3 中仍然有效，但推荐迁移到 :deep() */

/* /deep/ 写法 */
.parent /deep/ .child-element {
  color: red;
}

/* ::v-deep 写法 */
.parent ::v-deep .child-element {
  color: red;
}

/* >>> 写法 */
.parent >>> .child-element {
  color: red;
}
</style>
```

### 4.4 深度选择器编译原理

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    深度选择器编译原理详解                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  普通 scoped 样式编译：                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  源代码:                                                         │   │
│  │  .wrapper .child { color: red; }                                 │   │
│  │                                                                  │   │
│  │  编译结果:                                                       │   │
│  │  .wrapper .child[data-v-hash] { color: red; }                   │   │
│  │                                                                  │   │
│  │  说明：最后一个选择器添加 data-v-hash 属性                       │   │
│  │  只能匹配带有 data-v-hash 属性的元素                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  :deep() 编译：                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  源代码:                                                         │   │
│  │  .wrapper :deep(.child) { color: red; }                          │   │
│  │                                                                  │   │
│  │  编译结果:                                                       │   │
│  │  .wrapper .child[data-v-hash] { color: red; }  /* 错误理解 */   │   │
│  │  .wrapper .child { color: red; }  /* 正确理解！无 data-v-hash */ │   │
│  │                                                                  │   │
│  │  说明：:deep() 包裹的部分不会添加 data-v-hash 属性               │   │
│  │  :deep() 之后的选择器不添加属性选择器                            │   │
│  │  可以匹配子组件内部的元素                                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  嵌套 :deep() 编译：                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  源代码:                                                         │   │
│  │  .wrapper {                                                      │   │
│  │    :deep(.child) {                                               │   │
│  │      .inner { color: red; }                                      │   │
│  │    }                                                             │   │
│  │  }                                                               │   │
│  │                                                                  │   │
│  │  编译结果:                                                       │   │
│  │  .wrapper .child[data-v-hash] .inner { color: red; }             │   │
│  │                                                                  │   │
│  │  说明：:deep() 开始，到嵌套结束                                  │   │
│  │  :deep() 内的选择器不添加 data-v-hash                            │   │
│  │  :deep() 外的选择器仍添加 data-v-hash                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  实际例子：                                                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  // 父组件模板                                                   │   │
│  │  <template>                                                      │   │
│  │    <div class="parent" data-v-parent>                            │   │
│  │      <ChildComponent />                                          │   │
│  │    </div>                                                        │   │
│  │  </template>                                                     │   │
│  │                                                                  │   │
│  │  // 子组件模板（编译后）                                         │   │
│  │  <div class="child" data-v-child>                                │   │
│  │    <span class="title" data-v-child>标题</span>                  │   │
│  │  </div>                                                          │   │
│  │                                                                  │   │
│  │  // 父组件使用 :deep()                                           │   │
│  │  .parent :deep(.child .title) { color: red; }                    │   │
│  │                                                                  │   │
│  │  // 编译结果                                                     │   │
│  │  .parent .child .title { color: red; }                           │   │
│  │                                                                  │   │
│  │  // 匹配过程                                                     │   │
│  │  1. .parent → 匹配父组件的 div（有 data-v-parent）                │   │
│  │  2. .child → 匹配子组件的 div（无 data-v-parent，正常匹配）       │   │
│  │  3. .title → 匹配子组件的 span（无 data-v-parent，正常匹配）      │   │
│  │  ✅ 样式生效！                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.5 :global() 全局穿透

Vue 3 还提供了 `:global()` 伪类，用于将部分选择器标记为全局样式。

```html
<!-- Vue 3 :global() 用法 -->
<template>
  <div class="container">
    <div class="scoped-item">作用域元素</div>
    <div class="global-item">全局元素</div>
  </div>
</template>

<style scoped>
/* 普通 scoped 样式 */
.container {
  padding: 20px;
}

.scoped-item {
  background: lightblue;
}

/* 使用 :global() 将 .global-item 标记为全局 */
:global(.global-item) {
  background: lightgreen;
}

/* 与嵌套选择器结合 */
.container {
  /* scoped */
  .scoped-item {
    color: blue;
  }
  
  /* global */
  :global(.global-item) {
    color: green;
  }
}
</style>
```

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    :global() 与 :deep() 对比                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  :deep()                                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  作用：穿透子组件样式作用域                                       │   │
│  │  编译结果：选择器不添加 data-v-hash                               │   │
│  │  示例：:deep(.child) → .child                                    │   │
│  │  适用场景：父组件修改子组件内部样式                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  :global()                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  作用：声明全局样式，不受作用域限制                                 │   │
│  │  编译结果：选择器完全不添加 data-v-hash                            │   │
│  │  示例：:global(.global) → .global                                │   │
│  │  适用场景：定义需要全局生效的样式                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  两者的区别：                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  :deep()：                                                         │   │
│  │  - 只影响 :deep() 后面的选择器                                    │   │
│  │  - 前面的选择器仍添加 data-v-hash                                 │   │
│  │  - 样式仍绑定在当前组件的 DOM 子树中                               │   │
│  │                                                                  │   │
│  │  :global()：                                                      │   │
│  │  - 影响 :global() 包裹的所有选择器                                │   │
│  │  - 完全不添加 data-v-hash                                         │   │
│  │  - 样式真正变为全局生效                                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 五、实际开发中的最佳实践

### 5.1 样式组织规范

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    样式组织最佳实践规范                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  规范 1：样式命名                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  // 推荐使用 BEM 命名规范                                        │   │
│  │  .block__element--modifier                                      │   │
│  │                                                                  │   │
│  │  /* MyComponent.vue */                                           │   │
│  │  <style scoped lang="scss">                                      │   │
│  │  .my-component {                                                  │   │
│  │    &__header {                                                    │   │
│  │      padding: 16px;                                               │   │
│  │    }                                                             │   │
│  │                                                                  │   │
│  │    &__title {                                                     │   │
│  │      font-size: 18px;                                             │   │
│  │                                                                  │   │
│  │      &--large {                                                   │   │
│  │        font-size: 24px;                                           │   │
│  │      }                                                           │   │
│  │    }                                                             │   │
│  │  }                                                               │   │
│  │  </style>                                                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  规范 2：CSS 变量（CSS Custom Properties）                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  /* 定义在父组件或全局 */                                        │   │
│  │  :root {                                                          │   │
│  │    --primary-color: #409eff;                                     │   │
│  │    --font-size-base: 14px;                                       │   │
│  │  }                                                               │   │
│  │                                                                  │   │
│  │  /* 子组件中使用（CSS 变量可以穿透作用域） */                     │   │
│  │  <style scoped>                                                  │   │
│  │  .child-component {                                              │   │
│  │    color: var(--primary-color);  /* 可用 */                      │   │
│  │    font-size: var(--font-size-base);                             │   │
│  │  }                                                               │   │
│  │  </style>                                                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  规范 3：样式分层                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  /* 推荐的样式层级组织 */                                        │   │
│  │  <style scoped lang="scss">                                      │   │
│  │  // 1. 组件根元素样式                                            │   │
│  │  .my-component {                                                 │   │
│  │    display: flex;                                                │   │
│  │    flex-direction: column;                                       │   │
│  │  }                                                               │   │
│  │                                                                  │   │
│  │  // 2. 子元素样式                                                │   │
│  │  .my-component__header { ... }                                    │   │
│  │  .my-component__content { ... }                                  │   │
│  │  .my-component__footer { ... }                                   │   │
│  │                                                                  │   │
│  │  // 3. 状态样式                                                  │   │
│  │  .my-component--active { ... }                                   │   │
│  │  .my-component--disabled { ... }                                 │   │
│  │                                                                  │   │
│  │  // 4. 深度穿透样式（谨慎使用）                                  │   │
│  │  .my-component :deep(.child-element) { ... }                     │   │
│  │  </style>                                                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 常见问题与解决方案

#### 问题 1：样式不生效

```html
<!-- 问题场景 -->
<template>
  <div class="parent">
    <ChildComponent class="child" />
  </div>
</template>

<style scoped>
/* 问题：子组件上的 class 不会生效 */
.child {
  background: red;  /* 不生效！ */
}
</style>

<!-- 原因：scoped 样式编译为 .child[data-v-hash]，但子组件根元素没有父组件的 data-v-hash 属性 -->

<!-- 解决方案 1：使用 :deep() -->
<style scoped>
.parent :deep(.child) {
  background: red;
}
</style>

<!-- 解决方案 2：使用 ::v-deep（Vue 2） -->
<style scoped>
.parent ::v-deep .child {
  background: red;
}
</style>

<!-- 解决方案 3：子组件暴露根元素 class -->
<!-- ChildComponent.vue -->
<template>
  <div class="child" :class="$attrs.class">
    <!-- 子组件内容 -->
  </div>
</template>
```

#### 问题 2：第三方组件样式穿透

```html
<!-- 常见场景：修改 Element Plus 组件样式 -->
<template>
  <div class="page">
    <el-table :data="tableData">
      <el-table-column prop="name" label="名称" />
    </el-table>
  </div>
</template>

<style scoped>
/* 不生效的写法 */
.el-table th {
  background: red;  /* 不生效 */
}

/* 生效的写法 1：使用 :deep() */
.page :deep(.el-table th) {
  background: red;
}

/* 生效的写法 2：使用 ::v-deep（Vue 2） */
.page ::v-deep .el-table th {
  background: red;
}

/* 生效的写法 3：使用 /deep/（Vue 2） */
.page /deep/ .el-table th {
  background: red;
}

/* 生效的写法 4：去掉 scoped（不推荐，会泄漏） */
<style>
.page .el-table th {
  background: red;
}
</style>

/* 最佳实践：只在必要时穿透，避免过度使用 :deep() */
```

#### 问题 3：scoped 样式与 CSS 动画

```html
<!-- 问题：CSS 动画在 scoped 中的表现 -->
<template>
  <div class="animated-box">
    动画元素
  </div>
</template>

<style scoped>
/* @keyframes 规则本身不受 scoped 影响 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 但 animation 属性仍然受 scoped 影响 */
.animated-box {
  animation: fadeIn 1s ease-in;
}
</style>

/* 说明：
   1. @keyframes 规则不会被添加 data-v-hash
   2. 但使用该动画的选择器会被添加 data-v-hash
   3. 所以动画本身是全局的，但只有带有 data-v-hash 的元素能使用 */
```

### 5.3 性能优化建议

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    作用域 CSS 性能优化建议                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  优化 1：避免过度使用 :deep()                                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  ❌ 不推荐：大量使用 :deep() 会降低样式隔离效果                 │   │
│  │  .container :deep(*) {                                          │   │
│  │    margin: 0;                                                    │   │
│  │  }                                                               │   │
│  │                                                                  │   │
│  │  ✅ 推荐：精确选择需要穿透的元素                                 │   │
│  │  .container :deep(.specific-element) {                           │   │
│  │    margin: 0;                                                    │   │
│  │  }                                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  优化 2：选择器性能                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  ❌ 不推荐：过长的选择器链                                       │   │
│  │  .page .container .wrapper .content .box .title { ... }          │   │
│  │                                                                  │   │
│  │  ✅ 推荐：简洁的选择器                                           │   │
│  │  .box-title { ... }                                              │   │
│  │                                                                  │   │
│  │  注意：选择器越长，浏览器解析和匹配的开销越大                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  优化 3：CSS 变量代替 :deep()                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  // 父组件                                                       │   │
│  │  <template>                                                      │   │
│  │    <div :style="{ '--theme-color': 'red' }">                     │   │
│  │      <ChildComponent />                                          │   │
│  │    </div>                                                        │   │
│  │  </template>                                                     │   │
│  │                                                                  │   │
│  │  // 子组件                                                       │   │
│  │  <style scoped>                                                  │   │
│  │  .child-title {                                                  │   │
│  │    color: var(--theme-color);  /* 无需 :deep() */                │   │
│  │  }                                                               │   │
│  │  </style>                                                        │   │
│  │                                                                  │   │
│  │  优势：                                                          │   │
│  │  - 避免使用 :deep() 穿透                                         │   │
│  │  - 性能更好                                                      │   │
│  │  - 更灵活                                                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  优化 4：样式预处理器利用                                                │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  // 利用 SCSS 变量和 mixin 减少重复                               │   │
│  │  <style scoped lang="scss">                                      │   │
│  │  $primary-color: #409eff;                                        │   │
│  │  $spacing: 16px;                                                 │   │
│  │                                                                  │   │
│  │  @mixin flex-center {                                             │   │
│  │    display: flex;                                                │   │
│  │    align-items: center;                                          │   │
│  │    justify-content: center;                                      │   │
│  │  }                                                               │   │
│  │                                                                  │   │
│  │  .container {                                                    │   │
│  │    @include flex-center;                                         │   │
│  │    color: $primary-color;                                        │   │
│  │    padding: $spacing;                                            │   │
│  │  }                                                               │   │
│  │  </style>                                                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 六、高级主题

### 6.1 作用域 CSS 与 CSS Modules 对比

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Scoped CSS vs CSS Modules                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  对比维度        │ Scoped CSS              │ CSS Modules               │
│  ─────────────────────────────────────────────────────────────────      │
│  隔离方式        │ 属性选择器              │ 类名哈希                  │
│  ─────────────────────────────────────────────────────────────────      │
│  编译结果        │ .title[data-v-hash]    │ .title_hash               │
│  ─────────────────────────────────────────────────────────────────      │
│  穿透方式        │ :deep() / ::v-deep     │ :global() / :compose      │
│  ─────────────────────────────────────────────────────────────────      │
│  使用复杂度      │ 简单                    │ 需导出类名引用            │
│  ─────────────────────────────────────────────────────────────────      │
│  动态类名        │ 支持                    │ 支持（需导入）            │
│  ─────────────────────────────────────────────────────────────────      │
│  与 Vue 集成     │ 原生支持                │ 需额外配置                │
│  ─────────────────────────────────────────────────────────────────      │
│  适用场景        │ Vue 项目                │ React/Vue 等              │
│  ─────────────────────────────────────────────────────────────────      │
│  样式泄漏风险    │ 低                      │ 低                        │
│  ─────────────────────────────────────────────────────────────────      │
│                                                                         │
│  Scoped CSS 示例：                                                      │
│  <style scoped>                                                         │
│  .title { color: red; }  /* 直接使用 */                                 │
│  </style>                                                               │
│                                                                         │
│  CSS Modules 示例：                                                     │
│  <style module>                                                         │
│  .title { color: red; }                                                 │
│  </style>                                                               │
│  // JS 中使用                                                           │
│  import styles from './Component.vue'                                   │
│  // 模板中: :class="styles.title"                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.2 作用域 CSS 与 CSS-in-JS 对比

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Scoped CSS vs CSS-in-JS                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  对比维度        │ Scoped CSS              │ CSS-in-JS                 │
│  ─────────────────────────────────────────────────────────────────      │
│  编写方式        │ <style scoped>          │ JS/TS 对象/字符串         │
│  ─────────────────────────────────────────────────────────────────      │
│  运行时开销      │ 编译时处理              │ 运行时处理                │
│  ─────────────────────────────────────────────────────────────────      │
│  动态样式        │ CSS 变量/表达式        │ JS 变量/函数              │
│  ─────────────────────────────────────────────────────────────────      │
│  SSR 支持        │ 原生支持                │ 需额外配置                │
│  ─────────────────────────────────────────────────────────────────      │
│  学习曲线        │ 低                      │ 较高                      │
│  ─────────────────────────────────────────────────────────────────      │
│  调试难度        │ 简单                    │ 需浏览器扩展              │
│  ─────────────────────────────────────────────────────────────────      │
│                                                                         │
│  Scoped CSS 优势：                                                      │
│  ✅ 静态编译，运行时无开销                                              │
│  ✅ 与标准 CSS 语法一致                                                  │
│  ✅ 易于调试和维护                                                       │
│  ✅ 支持所有 CSS 特性（伪类、动画等）                                    │
│                                                                         │
│  CSS-in-JS 优势：                                                       │
│  ✅ 更强的动态能力（基于 JS 变量）                                       │
│  ✅ 更好的类型安全（配合 TypeScript）                                    │
│  ✅ 自动前缀和适配                                                       │
│  ✅ 组件级样式即弃                                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.3 自定义作用域策略

#### 自定义哈希算法

```javascript
// vue.config.js 或 vite.config.js
// Vue CLI 配置
module.exports = {
  css: {
    loaderOptions: {
      css: {
        // 自定义 scoped CSS 行为
      }
    }
  }
}

// Vite 配置
// vite.config.ts
export default {
  css: {
    modules: {
      // CSS Modules 配置
      generateScopedName: '[name]__[local]__[hash:base64:5]'
    }
  }
}
```

#### 使用 CSS Modules 替代 Scoped

```html
<!-- Vue 3 支持 CSS Modules -->
<template>
  <div :class="$style.wrapper">
    <h1 :class="$style.title">标题</h1>
    <p :class="$style.content">内容</p>
  </div>
</template>

<style module>
.wrapper {
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.title {
  font-size: 24px;
  color: #333;
}

.content {
  line-height: 1.6;
  color: #666;
}
</style>

<!-- CSS Modules 配合 scoped 使用 -->
<style scoped>
/* 组件基础样式 */
.container {
  max-width: 1200px;
  margin: 0 auto;
}
</style>

<style module>
/* 组件专属样式，通过 $style 对象访问 */
.header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
```

---

## 七、面试题深度解析

### 7.1 什么是 Vue 的作用域 CSS？它是如何实现的？

**答案要点：**

```
作用域 CSS 是 Vue.js 提供的样式隔离机制，确保组件内的样式只作用于该组件。

实现原理：
1. 每个组件在编译时会生成唯一的 hash 值（如 7a3b9c1d）
2. 为组件模板中的所有元素添加 data-v-hash 属性
3. 为 <style scoped> 中的所有选择器添加 [data-v-hash] 属性选择器
4. 编译前: .title { color: red; }
   编译后: .title[data-v-7a3b9c1d] { color: red; }
5. 只有带有该 data-v 属性的元素才会被样式影响

这样就实现了样式隔离，避免组件间样式污染。
```

### 7.2 Vue 中 :deep()、::v-deep、/deep/ 有什么区别？

**答案要点：**

```
这些都是 Vue 提供的深度选择器，用于穿透子组件的样式作用域。

区别如下：

1. ::v-deep（Vue 2 推荐）
   - 语法: .parent ::v-deep .child
   - 适用: 所有预处理器
   - 编译结果: .parent .child

2. /deep/（Vue 2 可用）
   - 语法: .parent /deep/ .child
   - 适用: 所有预处理器
   - 编译结果: .parent .child

3. >>>（不推荐）
   - 语法: .parent >>> .child
   - 适用: 原生 CSS、Less
   - 不支持 Sass/SCSS

4. :deep()（Vue 3 推荐）
   - 语法: .parent :deep(.child)
   - 适用: 所有预处理器
   - 编译结果: .parent .child

推荐使用:
- Vue 2: ::v-deep 或 /deep/
- Vue 3: :deep()

注意：>>> 在 Sass 中不可用，因为 >>> 会被解析为 Sass 操作符。
```

### 7.3 如何在 Vue 中修改第三方组件的样式？

**答案要点：**

```
有以下几种方式：

方式 1：使用深度选择器（推荐）
<style scoped>
/* Vue 2 */
.container ::v-deep .el-table th {
  background: red;
}

/* Vue 3 */
.container :deep(.el-table th) {
  background: red;
}
</style>

方式 2：去掉 scoped（不推荐，会样式泄漏）
<style>
.container .el-table th {
  background: red;
}
</style>

方式 3：使用 CSS 变量（最佳实践）
/* 父组件设置变量 */
<template>
  <div style="--table-header-bg: red">
    <el-table :data="data" />
  </div>
</template>

/* 如果第三方组件支持 CSS 变量，这种方式最优雅 */

方式 4：使用第三方组件的 props
<el-table :header-cell-style="{ background: 'red' }" />

推荐优先级：
1. 使用组件提供的 props/插槽
2. 使用 CSS 变量穿透
3. 使用 :deep() 深度选择器
4. 去掉 scoped（最后选择）
```

### 7.4 Vue 中作用域 CSS 和全局 CSS 如何配合使用？

**答案要点：**

```
1. 全局 CSS（无 scoped 的 <style> 标签）
   - 影响所有组件
   - 用于：Reset、字体、公共工具类
   - 注意：全局样式加载顺序会影响优先级

2. 作用域 CSS（有 scoped 的 <style> 标签）
   - 只影响当前组件
   - 用于：组件专属样式
   - 自动添加 data-v-hash 属性实现隔离

3. 混合使用示例：
<style scoped>
/* 作用域样式：只影响当前组件 */
.my-component {
  padding: 20px;
}
</style>

<style>
/* 全局样式：影响所有组件 */
.text-center {
  text-align: center;
}
</style>

4. 优先级关系：
   - 同优先级时，后加载的样式生效
   - 作用域 CSS 的属性选择器与类选择器优先级相同
   - 建议全局样式先加载，组件样式后加载

5. 注意事项：
   - CSS 变量可以穿透作用域边界
   - @keyframes 动画规则不受 scoped 影响
   - 组件的 :class 绑定可以使用全局类名
```

### 7.5 为什么使用了 scoped 样式，子组件的根元素样式还是不生效？

**答案要点：**

```
原因：
scoped 样式编译后，选择器会被添加 [data-v-hash] 属性选择器。
但是这个属性只添加到当前组件模板中的元素上，
子组件的根元素上没有父组件的 data-v-hash 属性。

示例：
// 父组件
<template>
  <div class="parent">  <!-- data-v-parent -->
    <ChildComponent />  <!-- 没有 data-v-parent -->
  </div>
</template>

<style scoped>
/* 编译为: .child[data-v-parent] */
/* 但子组件根元素没有 data-v-parent，所以不匹配 */
.child { background: red; }
</style>

解决方案：
1. 使用 :deep() 穿透
.parent :deep(.child) { background: red; }

2. 子组件接收父组件的 class
<!-- ChildComponent.vue -->
<template>
  <div :class="$attrs.class">  <!-- 接收父组件的 class -->
    子组件内容
  </div>
</template>

3. 使用 CSS 变量传递样式
```

---

## 八、总结与速查表

### 8.1 作用域 CSS 核心要点

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    作用域 CSS 核心要点总结                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. 实现原理：                                                          │
│     - 每个组件有唯一 hash 值                                             │
│     - 元素添加 data-v-hash 属性                                         │
│     - 选择器添加 [data-v-hash] 属性选择器                               │
│                                                                         │
│  2. 深度选择器语法：                                                     │
│     - Vue 2: ::v-deep 或 /deep/                                         │
│     - Vue 3: :deep()                                                     │
│                                                                         │
│  3. :global() 用法：                                                     │
│     - 将选择器标记为全局样式                                             │
│     - 不受 scoped 限制                                                   │
│                                                                         │
│  4. CSS 变量特性：                                                       │
│     - 可以穿透作用域边界                                                 │
│     - 是实现父子组件样式传递的最佳方式                                   │
│                                                                         │
│  5. 注意事项：                                                           │
│     - 子组件根元素没有父组件的 data-v 属性                                │
│     - @keyframes 不受 scoped 影响                                       │
│     - 选择器优先级和加载顺序会影响样式生效                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.2 深度选择器速查表

| 语法 | Vue 版本 | 适用预处理器 | 推荐度 |
|------|---------|------------|--------|
| `::v-deep` | Vue 2 | 全部 | ⭐⭐⭐⭐⭐ |
| `/deep/` | Vue 2 | 全部 | ⭐⭐⭐⭐ |
| `>>>` | Vue 2 | CSS/Less | ⭐⭐ |
| `:deep()` | Vue 3 | 全部 | ⭐⭐⭐⭐⭐ |
| `:global()` | Vue 3 | 全部 | 全局穿透 |

### 8.3 常见问题速查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 样式不生效 | 选择器没有匹配到元素 | 检查选择器是否正确 |
| 子组件样式不生效 | 子组件根元素无父组件的 data-v 属性 | 使用 :deep() 或 :global() |
| 第三方组件样式不生效 | 选择器优先级或穿透问题 | 使用 :deep() 或组件 props |
| CSS 动画不生效 | @keyframes 不受 scoped 影响 | 正常使用即可 |
| 全局样式被覆盖 | 加载顺序问题 | 调整 CSS 加载顺序 |

### 8.4 最佳实践清单

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    作用域 CSS 最佳实践清单                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ✅ 推荐做法：                                                           │
│  □ 使用 scoped 属性启用样式隔离                                         │
│  □ 使用 BEM 命名规范命名类名                                            │
│  □ 使用 CSS 变量实现样式传递                                            │
│  □ 使用 :deep() 穿透子组件样式                                         │
│  □ 使用预处理器管理复杂样式                                            │
│  □ 为第三方组件使用 CSS 变量或 props 定制样式                           │
│                                                                         │
│  ❌ 避免做法：                                                           │
│  □ 滥用 :deep() 穿透（降低隔离性）                                     │
│  □ 选择器链过长（影响性能）                                            │
│  □ 使用 !important（破坏优先级规则）                                    │
│  □ 大量使用全局样式（造成污染）                                        │
│  □ 混用多种深度选择器语法（建议统一）                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 附录：术语表

| 术语 | 英文名 | 说明 |
|------|--------|------|
| 作用域 CSS | Scoped CSS | Vue 提供的样式隔离机制 |
| 深度选择器 | Deep Selector | 穿透子组件样式作用域的选择器 |
| 属性选择器 | Attribute Selector | 基于 HTML 属性选择元素的 CSS 选择器 |
| 哈希值 | Hash | 基于组件内容生成的唯一标识 |
| 样式泄漏 | Style Leak | 组件样式影响到其他组件的现象 |
| CSS 变量 | CSS Custom Properties | 原生 CSS 变量，可以穿透作用域 |
| CSS Modules | CSS Modules | 基于类名哈希的样式隔离方案 |
| CSS-in-JS | CSS-in-JS | 在 JavaScript 中编写 CSS 的方案 |
| BEM | Block Element Modifier | 一种 CSS 命名规范 |

---

> **文档版本**：v1.0  
> **适用版本**：Vue 2.x / Vue 3.x  
> **最后更新**：2026-08  
> **参考来源**：Vue 官方文档、Vue Loader 文档、PostCSS 文档
